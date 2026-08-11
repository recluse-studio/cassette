# compiler.py — contained source inspection, zero-copy compilation, total contribution maps, and Q19 certificates (Q4/Q19/Q30/Q40/Q51/Q55/Q58/Q60/Q62); depends on errors.py, schema, store.py.
"""Compile verified SafeTensors material into one independently checkable executable revision."""

from __future__ import annotations

from dataclasses import dataclass
import fcntl
from fractions import Fraction
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
import struct
from typing import Mapping

from errors import CassetteError
from schema.tables import DISPATCH_ROWS, OPERATOR_DISPATCH, Q40_MODES
from schema.validator import validate
from store import (
    ArtifactIdentity,
    IdentityTuple,
    PAGE_BYTES,
    adopt_safetensors,
    canonical_bytes,
    derive_root,
    digest_bytes,
    extent_footprint,
    inspect_safetensors,
    load_root,
    model_identity,
    page_locations,
    read_tensor,
)

_MANIFEST_KEY = "cassette.compiler.v1"
_VERSION = "s19-compiler-v1"
_MAX_ITEMS = 1_048_576
_MAX_RECORD_BYTES = 4 * 1024 * 1024
_MAX_U64 = 2**64 - 1
_DIGEST = re.compile(r"(?:blake3|sha256):[0-9a-f]{64}|git-sha1:[0-9a-f]{40}")
_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,255}")
_UNSAFE_SUFFIXES = frozenset({
    ".bin", ".dll", ".dylib", ".exe", ".jar", ".js", ".pkl", ".pickle",
    ".pt", ".py", ".safetensors.py", ".sh", ".so",
})
_UNSAFE_KEYS = frozenset({
    "auto_map", "custom_code", "custom_operator", "custom_operators", "dynamic_library",
    "exec", "executable", "jit_source", "native_library", "network", "pickle",
    "shell", "template_source", "trust_remote_code",
})
_SOURCE_FIELDS = frozenset({
    "source_kind", "source_alias", "locator", "requested_revision", "immutable_revision",
    "identity", "artifacts", "license_digest",
})
_ARTIFACT_FIELDS = frozenset({"path", "size", "digest"})
_EXTENT_FIELDS = frozenset({"fd", "offset", "length", "operation_id"})
_MANIFEST_FIELDS = frozenset({
    "version", "model", "target_tensor", "evidence", "profile", "eta_rep",
    "rank_budget", "operation_bounds", "operator_inventory", "prior_mode_failures",
})
_MODEL_FIELDS = frozenset({
    "architecture", "config", "format_versions", "precision_scheme", "processor_digest",
    "template_digest", "tokenizer_digest",
})
_BUNDLE_FIELDS = frozenset({
    "version", "source_identity", "source_root", "preparation_plan_digest",
    "operator_inventory", "tensor_inventory", "evidence", "certificate", "profile",
    "contribution_map", "execution_plan", "extent_metrics",
})
_CASES = {
    row["case_id"]: {
        name: row[name]
        for name in (
            "case_id", "operator", "input_dtypes", "input_shapes", "output_dtype",
            "output_shape", "parameters",
        )
    }
    for row in DISPATCH_ROWS
}
_ZERO = (Fraction(0), Fraction(0))


@dataclass(frozen=True, slots=True)
class PreparedRevision:
    """Compiler-owned present-byte proof and immutable candidate-root claim."""

    source_identity: str
    verified_artifacts: tuple[ArtifactIdentity, ...]
    plan_digest: str
    candidate_root: str


def _reject(
    code: str,
    object_id: str,
    detail: str,
    invariant: str = "Q19/Q55/Q58: contained compilation from canonical evidence",
) -> None:
    raise CassetteError(code, object_id, invariant, "terminal", detail)


def _record(value: object, fields: frozenset[str] | set[str], object_id: str, label: str) -> dict:
    if not isinstance(value, dict) or set(value) != fields:
        observed = sorted(value) if isinstance(value, dict) else type(value).__name__
        _reject("INVALID_REQUEST", object_id, f"{label} requires exactly {sorted(fields)}; received {observed}")
    return value


def _items(value: object, object_id: str, label: str, *, empty: bool = False) -> list:
    if not isinstance(value, list) or len(value) > _MAX_ITEMS or (not empty and not value):
        _reject("INVALID_REQUEST", object_id, f"{label} requires a bounded {'possibly empty' if empty else 'nonempty'} list")
    return value


def _identifier(value: object, object_id: str, label: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
        _reject("INVALID_REQUEST", object_id, f"{label} is not a bounded canonical identifier")
    return value


def _digest(value: object) -> str:
    return digest_bytes(canonical_bytes(value))


def _exact_digest(value: object, object_id: str, label: str) -> str:
    if not isinstance(value, str) or _DIGEST.fullmatch(value) is None:
        _reject("INVALID_REQUEST", object_id, f"{label} is not one canonical digest")
    return value


def _u64(value: object, object_id: str, label: str) -> int:
    if type(value) is not int or not 0 <= value <= _MAX_U64:
        _reject("INVALID_REQUEST", object_id, f"{label} is not an unsigned 64-bit integer")
    return value


def _fraction(value: object, object_id: str, label: str) -> Fraction:
    try:
        if type(value) is int:
            candidate = Fraction(value)
        elif type(value) is float and math.isfinite(value):
            candidate = Fraction(str(value))
        elif isinstance(value, str) and 0 < len(value) <= 128:
            candidate = Fraction(value)
        else:
            raise ValueError
    except (OverflowError, ValueError, ZeroDivisionError):
        _reject("INVALID_REQUEST", object_id, f"{label} is not a bounded exact scalar")
    if max(candidate.numerator.bit_length(), candidate.denominator.bit_length()) > 1077:
        _reject("INVALID_REQUEST", object_id, f"{label} exceeds the exact scalar bound")
    return candidate


def _number(value: Fraction, object_id: str, label: str) -> float:
    try:
        result = float(value)
    except OverflowError:
        result = math.inf
    if not math.isfinite(result) or result < 0 or result > 1e300:
        _reject("CAPABILITY_MISMATCH", object_id, f"{label} is outside the certificate number domain")
    return result


def _scalar(value: object, field: str, object_id: str, label: str) -> tuple[Fraction, Fraction]:
    if field == "REAL":
        return (_fraction(value, object_id, label), Fraction(0))
    if not isinstance(value, list) or len(value) != 2:
        _reject("INVALID_REQUEST", object_id, f"{label} requires [real, imaginary]")
    return (_fraction(value[0], object_id, label), _fraction(value[1], object_id, label))


def _matrix(value: object, shape: tuple[int, int], field: str, object_id: str, label: str):
    rows = _items(value, object_id, label)
    if len(rows) != shape[0] or any(not isinstance(row, list) or len(row) != shape[1] for row in rows):
        _reject("INVALID_REQUEST", object_id, f"{label} requires exact shape {list(shape)}")
    return tuple(
        tuple(_scalar(item, field, object_id, label) for item in row)
        for row in rows
    )


def _normal_scalar(value) -> list[str]:
    return [str(value[0]), str(value[1])]


def _normal_matrix(matrix) -> list:
    return [[_normal_scalar(value) for value in row] for row in matrix]


def _normal_exact(value: object) -> object:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {name: _normal_exact(item) for name, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normal_exact(item) for item in value]
    return value


def _add(left, right):
    return (left[0] + right[0], left[1] + right[1])


def _subtract(left, right):
    return (left[0] - right[0], left[1] - right[1])


def _multiply(left, right):
    return (left[0] * right[0] - left[1] * right[1], left[0] * right[1] + left[1] * right[0])


def _divide(left, right):
    denominator = right[0] * right[0] + right[1] * right[1]
    if denominator == 0:
        _reject("CAPABILITY_MISMATCH", "certificate:matrix", "matrix elimination reached a zero divisor")
    return (
        (left[0] * right[0] + left[1] * right[1]) / denominator,
        (left[1] * right[0] - left[0] * right[1]) / denominator,
    )


def _conjugate(value):
    return (value[0], -value[1])


def _absolute_squared(value) -> Fraction:
    return value[0] * value[0] + value[1] * value[1]


def _flatten(matrix):
    return tuple(value for row in matrix for value in row)


def _rank(matrix) -> int:
    rows = [list(row) for row in matrix]
    pivot_row = 0
    for column in range(len(rows[0])):
        pivot = next((index for index in range(pivot_row, len(rows)) if rows[index][column] != _ZERO), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        divisor = rows[pivot_row][column]
        rows[pivot_row] = [_divide(value, divisor) for value in rows[pivot_row]]
        for index in range(len(rows)):
            if index == pivot_row or rows[index][column] == _ZERO:
                continue
            factor = rows[index][column]
            rows[index] = [
                _subtract(value, _multiply(factor, reference))
                for value, reference in zip(rows[index], rows[pivot_row], strict=True)
            ]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return pivot_row


def _determinant(matrix):
    rows = [list(row) for row in matrix]
    result = (Fraction(1), Fraction(0))
    sign = 1
    for column in range(len(rows)):
        pivot = next((index for index in range(column, len(rows)) if rows[index][column] != _ZERO), None)
        if pivot is None:
            return _ZERO
        if pivot != column:
            rows[column], rows[pivot] = rows[pivot], rows[column]
            sign *= -1
        divisor = rows[column][column]
        result = _multiply(result, divisor)
        for index in range(column + 1, len(rows)):
            if rows[index][column] == _ZERO:
                continue
            factor = _divide(rows[index][column], divisor)
            rows[index] = [
                _subtract(value, _multiply(factor, reference))
                for value, reference in zip(rows[index], rows[column], strict=True)
            ]
    return (-result[0], -result[1]) if sign < 0 else result


def _inner(left, metric, right):
    applied = []
    for row in metric:
        total = _ZERO
        for coefficient, value in zip(row, right, strict=True):
            total = _add(total, _multiply(coefficient, value))
        applied.append(total)
    result = _ZERO
    for value, product in zip(left, applied, strict=True):
        result = _add(result, _multiply(_conjugate(value), product))
    return result


def _witness_loss(target, atom, metric, object_id: str) -> Fraction:
    target_norm = _inner(target, metric, target)
    atom_norm = _inner(atom, metric, atom)
    cross = _inner(atom, metric, target)
    if target_norm[1] or atom_norm[1] or atom_norm[0] <= 0:
        _reject("CAPABILITY_MISMATCH", object_id, "condition quadratic forms are not positive real values")
    loss = target_norm[0] - _absolute_squared(cross) / atom_norm[0]
    if loss < 0:
        _reject("CAPABILITY_MISMATCH", object_id, "condition witness loss is negative")
    return loss


def _minimal_nonfaces(universe: frozenset[str], faces: set[frozenset[str]]) -> set[frozenset[str]]:
    maximal = {face for face in faces if not any(face < other for other in faces)}
    candidates = {frozenset()}
    for edge in (universe - face for face in maximal):
        if not edge:
            return set()
        expanded = set()
        for candidate in candidates:
            if candidate & edge:
                expanded.add(candidate)
            else:
                expanded.update(candidate | {condition} for condition in edge)
        candidates = {
            candidate for candidate in expanded
            if not any(other < candidate for other in expanded)
        }
    return candidates


def _safe_artifact_path(value: object, object_id: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "\\" in value
        or any(ord(character) < 32 or ord(character) == 127 for character in value)
    ):
        _reject("CONTAINMENT_REJECTED", object_id, "artifact path contains control, escape, or ambiguous characters")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or path.as_posix() != value
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        _reject("CONTAINMENT_REJECTED", object_id, "artifact path escapes its canonical source namespace")
    lowered = value.lower()
    if any(lowered.endswith(suffix) for suffix in _UNSAFE_SUFFIXES) or not lowered.endswith(".safetensors"):
        _reject("CONTAINMENT_REJECTED", object_id, "first-release compilation accepts data-only SafeTensors artifacts")
    return value


def _scan_containment(value: object, object_id: str, label: str = "manifest") -> None:
    if isinstance(value, dict):
        for name, item in value.items():
            if not isinstance(name, str) or name.lower().replace("-", "_") in _UNSAFE_KEYS:
                _reject("CONTAINMENT_REJECTED", object_id, f"{label} declares executable capability {name!r}")
            _scan_containment(item, object_id, f"{label}.{name}")
    elif isinstance(value, list):
        if len(value) > _MAX_ITEMS:
            _reject("CONTAINMENT_REJECTED", object_id, f"{label} exceeds the bounded item count")
        for index, item in enumerate(value):
            _scan_containment(item, object_id, f"{label}[{index}]")
    elif isinstance(value, str):
        lowered = value.lower()
        if len(value) > _MAX_RECORD_BYTES or "\x00" in value or "../" in value or "..\\" in value:
            _reject("CONTAINMENT_REJECTED", object_id, f"{label} contains an unbounded or escaping string")
        if lowered.startswith(("http://", "https://", "file://")) or any(
            lowered.endswith(suffix) for suffix in _UNSAFE_SUFFIXES
        ):
            _reject("CONTAINMENT_REJECTED", object_id, f"{label} requests code, network, or filesystem execution")


def _source(value: object) -> dict:
    source = _record(value, _SOURCE_FIELDS, "source:compile", "source lock")
    for field in ("source_kind", "source_alias", "locator"):
        if not isinstance(source[field], str) or not source[field]:
            _reject("INVALID_REQUEST", "source:compile", f"{field} must be nonempty text")
    if source["requested_revision"] is not None and (
        not isinstance(source["requested_revision"], str) or not source["requested_revision"]
    ):
        _reject("INVALID_REQUEST", "source:compile", "requested_revision must be null or nonempty text")
    for field in ("immutable_revision", "identity", "license_digest"):
        _exact_digest(source[field], "source:compile", field)
    artifacts = _items(source["artifacts"], source["identity"], "source artifacts")
    normalized = []
    for item in artifacts:
        row = _record(item, _ARTIFACT_FIELDS, source["identity"], "source artifact")
        normalized.append({
            "path": _safe_artifact_path(row["path"], source["identity"]),
            "size": _u64(row["size"], source["identity"], "artifact size"),
            "digest": _exact_digest(row["digest"], source["identity"], "artifact digest"),
        })
    if normalized != sorted(normalized, key=lambda item: item["path"]) or len({item["path"] for item in normalized}) != len(normalized):
        _reject("INVALID_REQUEST", source["identity"], "source artifacts must be unique and canonically ordered")
    return {**source, "artifacts": normalized}


def _extent_descriptors(source: dict, extents: object, cartridge: str | Path) -> dict[str, int]:
    if not isinstance(extents, Mapping) or set(extents) != {item["path"] for item in source["artifacts"]}:
        _reject("INVALID_REQUEST", source["identity"], "compiler extents must name every source artifact exactly once")
    cartridge_path = Path(cartridge).resolve(strict=True)
    descriptors = {}
    for artifact in source["artifacts"]:
        row = _record(extents[artifact["path"]], _EXTENT_FIELDS, source["identity"], "compiler extent")
        descriptor = row["fd"]
        if (
            type(descriptor) is not int
            or row["offset"] != 0
            or row["length"] != artifact["size"]
            or not isinstance(row["operation_id"], str)
            or not row["operation_id"]
        ):
            _reject("INVALID_REQUEST", source["identity"], f"extent for {artifact['path']!r} is not exact")
        try:
            descriptor_stat = os.fstat(descriptor)
            matches = []
            incoming = cartridge_path / "incoming"
            if incoming.is_dir():
                for candidate in incoming.rglob("*"):
                    if candidate.is_file() and not candidate.is_symlink():
                        candidate_stat = candidate.stat()
                        if (candidate_stat.st_dev, candidate_stat.st_ino) == (
                            descriptor_stat.st_dev, descriptor_stat.st_ino
                        ):
                            matches.append(candidate)
            if len(matches) == 1:
                path = matches[0].resolve(strict=True)
            else:
                encoded = fcntl.fcntl(descriptor, 50, b"\0" * 1024)
                path = Path(encoded.split(b"\0", 1)[0].decode()).resolve(strict=True)
            path_stat = path.stat()
        except (OSError, UnicodeDecodeError, ValueError) as error:
            _reject("SOURCE_UNAVAILABLE", artifact["path"], f"extent path resolution failed: {error}")
        if (
            not stat.S_ISREG(descriptor_stat.st_mode)
            or descriptor_stat.st_size != artifact["size"]
            or (descriptor_stat.st_dev, descriptor_stat.st_ino) != (path_stat.st_dev, path_stat.st_ino)
            or path == cartridge_path
            or cartridge_path not in path.parents
        ):
            _reject("CONTAINMENT_REJECTED", artifact["path"], "extent is not one exact regular file inside the cartridge")
        descriptors[artifact["path"]] = descriptor
    return descriptors


def _inventory(value: object, object_id: str) -> list[dict]:
    rows = _items(value, object_id, "operator inventory")
    normalized = []
    for item in rows:
        if not isinstance(item, dict) or set(item) != set(next(iter(_CASES.values()))):
            _reject("INVALID_REQUEST", object_id, "operator inventory row has an incorrect field set")
        case_id = _identifier(item["case_id"], object_id, "operator case ID")
        expected = _CASES.get(case_id)
        if expected is None and item.get("operator") not in {
            row["operator"] for row in _CASES.values()
        }:
            _reject(
                "CONTAINMENT_REJECTED",
                case_id,
                "source declares a custom operator outside the pinned trusted runtime",
            )
        if expected is None or item != expected:
            _reject("UNSUPPORTED_OPERATOR", case_id, "source operator tuple is absent from the pinned generated dispatch")
        normalized.append(item)
    if normalized != sorted(normalized, key=lambda item: item["case_id"]) or len({item["case_id"] for item in normalized}) != len(normalized):
        _reject("INVALID_REQUEST", object_id, "operator inventory must be unique and sorted by case ID")
    return normalized


def _manifest(source: dict, descriptors: dict[str, int]) -> tuple[dict, list[dict]]:
    texts = []
    tensors = []
    names = set()
    for artifact in source["artifacts"]:
        inspected = inspect_safetensors(descriptors[artifact["path"]], artifact["digest"])
        _scan_containment(
            {
                name: value
                for name, value in inspected["metadata"].items()
                if name != _MANIFEST_KEY
            },
            source["identity"],
            "SafeTensors metadata",
        )
        if inspected["data_start"] >= PAGE_BYTES:
            _reject(
                "MODEL_UNSUPPORTED",
                artifact["path"],
                "first-release zero-copy adoption requires each SafeTensors header within one page",
            )
        text = inspected["metadata"].get(_MANIFEST_KEY)
        if text is not None:
            texts.append(text)
        for tensor in inspected["tensors"]:
            tensor_id = _identifier(
                tensor["semantic_tensor_id"], source["identity"], "semantic tensor ID"
            )
            if tensor_id in names:
                _reject("INVALID_REQUEST", source["identity"], "SafeTensors shards repeat a semantic tensor ID")
            names.add(tensor_id)
            tensors.append({"artifact_path": artifact["path"], **tensor})
    if not texts or any(text != texts[0] for text in texts):
        _reject("METADATA_INSUFFICIENT", source["identity"], f"all compiler manifests must agree under {_MANIFEST_KEY!r}")
    try:
        manifest = json.loads(texts[0], object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        _reject("INVALID_REQUEST", source["identity"], f"compiler manifest is malformed JSON: {error}")
    if len(texts[0].encode()) > _MAX_RECORD_BYTES or canonical_bytes(manifest).decode() != texts[0]:
        _reject("INVALID_REQUEST", source["identity"], "compiler manifest must be bounded canonical JSON")
    _scan_containment(manifest, source["identity"])
    manifest = _record(manifest, _MANIFEST_FIELDS, source["identity"], "compiler manifest")
    if manifest["version"] != _VERSION:
        _reject("MODEL_UNSUPPORTED", source["identity"], f"compiler manifest version must be {_VERSION}")
    _record(manifest["model"], _MODEL_FIELDS, source["identity"], "model identity manifest")
    _identifier(manifest["target_tensor"], source["identity"], "target tensor ID")
    manifest["operator_inventory"] = _inventory(manifest["operator_inventory"], source["identity"])
    tensors.sort(key=lambda item: item["semantic_tensor_id"])
    return manifest, tensors


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError(f"duplicate JSON field {name!r}")
        result[name] = value
    return result


def _source_material(source: dict, manifest: dict, tensors: list[dict]) -> IdentityTuple:
    model = manifest["model"]
    formats = _items(model["format_versions"], source["identity"], "format versions")
    pairs = []
    for item in formats:
        if not isinstance(item, list) or len(item) != 2 or any(not isinstance(part, str) or not part for part in item):
            _reject("INVALID_REQUEST", source["identity"], "format versions require [name, version] pairs")
        pairs.append(tuple(item))
    material = IdentityTuple(
        revision_kind="source",
        source_kind=source["source_kind"],
        source_alias=source["source_alias"],
        canonical_locator=source["locator"],
        requested_revision=source["requested_revision"],
        immutable_revision=source["immutable_revision"],
        artifacts=tuple(ArtifactIdentity(**item) for item in source["artifacts"]),
        format_versions=tuple(pairs),
        tensor_index_digest=_digest(tensors),
        config_digest=_digest(model["config"]),
        architecture=model["architecture"],
        operator_set=tuple(sorted({row["operator"] for row in manifest["operator_inventory"]})),
        tokenizer_digest=model["tokenizer_digest"],
        processor_digest=model["processor_digest"],
        template_digest=model["template_digest"],
        precision_scheme=model["precision_scheme"],
        license_digest=source["license_digest"],
        parent_ids=(),
        transform_manifest_digest=None,
    )
    if model_identity(material) != source["identity"]:
        _reject("IDENTITY_MISMATCH", source["identity"], "parsed source identity differs from the durable source lock")
    return material


def _compile_inputs(source: dict, manifest: dict, tensors: list[dict]) -> dict:
    return {
        "version": _VERSION,
        "source_identity": source["identity"],
        "source_alias": source["source_alias"],
        "requested_revision": source["requested_revision"],
        "artifacts": source["artifacts"],
        "manifest_digest": _digest(manifest),
        "tensor_index_digest": _digest(tensors),
        "operator_inventory": manifest["operator_inventory"],
    }


def _decode_tensor(root: dict, cartridge: str | Path, root_digest: str, tensor_id: str) -> tuple[list, list[int]]:
    matches = [row for row in root["tensor_maps"] if row["semantic_tensor_id"] == tensor_id]
    if len(matches) != 1:
        _reject("INVALID_REQUEST", root_digest, f"target tensor {tensor_id!r} is absent or duplicated")
    tensor = matches[0]
    payload = read_tensor(cartridge, root_digest, tensor_id)
    dtype = tensor["dtype"]
    formats = {
        "BOOL": "?", "U8": "B", "I8": "b", "U16": "H", "I16": "h",
        "U32": "I", "I32": "i", "U64": "Q", "I64": "q", "F16": "e",
        "F32": "f", "F64": "d",
    }
    if dtype == "BF16":
        values = [
            struct.unpack("<f", struct.pack("<I", value << 16))[0]
            for (value,) in struct.iter_unpack("<H", payload)
        ]
    elif dtype in formats:
        values = [item[0] for item in struct.iter_unpack("<" + formats[dtype], payload)]
    else:
        _reject("MODEL_UNSUPPORTED", tensor_id, f"Q19 target decoding has no exact rule for {dtype}")
    expected = math.prod(tensor["shape"])
    if len(values) != expected or any(isinstance(value, float) and not math.isfinite(value) for value in values):
        _reject("CAPABILITY_MISMATCH", tensor_id, "decoded target values do not match the tensor map")
    return values, tensor["shape"]


def _certificate(evidence: dict, eta_value: object, rank_value: object, bounds_value: object) -> dict:
    object_id = "certificate:unsealed"
    source = _record(
        evidence,
        {
            "atoms", "conditions", "description_contract", "excluded_conditions",
            "execution_contract", "minimal_nonface_proofs", "observation_contract",
            "physical_conversion", "target", "trace_contract",
        },
        object_id,
        "certificate evidence",
    )
    target = _record(
        source["target"],
        {"field", "flattening_order", "shape", "source_shape", "source_values"},
        object_id,
        "target evidence",
    )
    field = target["field"]
    if field not in {"REAL", "COMPLEX"}:
        _reject("INVALID_REQUEST", object_id, "target field must be REAL or COMPLEX")
    source_shape = tuple(_u64(value, object_id, "source shape") for value in _items(target["source_shape"], object_id, "source shape"))
    target_shape_values = _items(target["shape"], object_id, "target shape")
    if len(target_shape_values) != 2:
        _reject("INVALID_REQUEST", object_id, "target shape must have two dimensions")
    target_shape = tuple(_u64(value, object_id, "target shape") for value in target_shape_values)
    count = math.prod(source_shape)
    values = _items(target["source_values"], object_id, "source values")
    order = _items(target["flattening_order"], object_id, "flattening order")
    if count != len(values) or math.prod(target_shape) != count or sorted(order) != list(range(count)):
        _reject("INVALID_REQUEST", object_id, "target shape, values, and flattening permutation disagree")
    flat = [_scalar(values[index], field, object_id, "target scalar") for index in order]
    target_matrix = tuple(
        tuple(flat[row * target_shape[1]:(row + 1) * target_shape[1]])
        for row in range(target_shape[0])
    )
    target_record = {"field": field, "shape": list(target_shape), "values": _normal_matrix(target_matrix)}
    flattening = {"source_shape": list(source_shape), "target_shape": list(target_shape), "order": order}
    vector_target = _flatten(target_matrix)
    dimension = len(vector_target)

    conditions = {}
    condition_claims = []
    for raw in _items(source["conditions"], object_id, "condition evidence"):
        row = _record(raw, {"condition_id", "metric", "provenance"}, object_id, "condition evidence")
        condition_id = _identifier(row["condition_id"], object_id, "condition ID")
        if condition_id in conditions:
            _reject("INVALID_REQUEST", object_id, "condition IDs must be unique")
        metric = _matrix(row["metric"], (dimension, dimension), field, condition_id, "condition metric")
        minors = []
        for left in range(dimension):
            for right in range(dimension):
                if metric[left][right] != _conjugate(metric[right][left]):
                    _reject("CAPABILITY_MISMATCH", condition_id, "condition metric is not Hermitian")
        for size in range(1, dimension + 1):
            determinant = _determinant(tuple(tuple(metric[row][column] for column in range(size)) for row in range(size)))
            if determinant[1] or determinant[0] <= 0:
                _reject("CAPABILITY_MISMATCH", condition_id, "condition metric is not positive definite")
            minors.append(_normal_scalar(determinant))
        conditions[condition_id] = metric
        condition_claims.append({
            "condition_id": condition_id,
            "provenance_digest": _digest(row["provenance"]),
            "metric_digest": _digest(_normal_matrix(metric)),
            "positive_definite_witness_digest": _digest(minors),
        })
    if [row["condition_id"] for row in condition_claims] != sorted(conditions):
        _reject("INVALID_REQUEST", object_id, "condition evidence must be sorted by condition ID")
    eta = _fraction(eta_value, object_id, "eta_rep")
    rank_budget = _u64(rank_value, object_id, "rank budget")

    atoms = {}
    atom_claims = []
    for raw in _items(source["atoms"], object_id, "atom evidence"):
        row = _record(raw, {"atom_id", "description", "matrix", "service_face_id"}, object_id, "atom evidence")
        atom_id = _identifier(row["atom_id"], object_id, "atom ID")
        if atom_id in atoms:
            _reject("INVALID_REQUEST", object_id, "atom IDs must be unique")
        matrix = _matrix(row["matrix"], target_shape, field, atom_id, "atom matrix")
        rank = _rank(matrix)
        if rank == 0 or rank > rank_budget:
            _reject("CAPABILITY_MISMATCH", atom_id, f"atom rank {rank} exceeds budget {rank_budget}")
        losses = {
            condition_id: _witness_loss(vector_target, _flatten(matrix), metric, atom_id)
            for condition_id, metric in conditions.items()
        }
        face = frozenset(condition_id for condition_id, loss in losses.items() if loss <= eta)
        if not face:
            _reject("CAPABILITY_MISMATCH", atom_id, "atom serves no protected condition")
        description = _record(
            row["description"],
            {"class", "description_bytes", "estimator", "estimator_calibration", "metadata_bytes", "reconstruction", "sampling_law_id"},
            atom_id,
            "description evidence",
        )
        reconstruction = _matrix(description["reconstruction"], target_shape, field, atom_id, "description reconstruction")
        residual = tuple(
            tuple(_subtract(value, rebuilt) for value, rebuilt in zip(atom_row, rebuilt_row, strict=True))
            for atom_row, rebuilt_row in zip(matrix, reconstruction, strict=True)
        )
        distortion = sum((_absolute_squared(value) for value in _flatten(residual)), Fraction(0))
        norm = sum((_absolute_squared(value) for value in _flatten(matrix)), Fraction(0))
        atoms[atom_id] = {
            "description_bytes": _u64(description["description_bytes"], atom_id, "description bytes"),
            "metadata_bytes": _u64(description["metadata_bytes"], atom_id, "metadata bytes"),
            "distortion": distortion,
            "norm": norm,
            "rank": rank,
            "face": face,
            "face_id": _identifier(row["service_face_id"], atom_id, "service face ID"),
            "sampling_law_id": _identifier(description["sampling_law_id"], atom_id, "sampling law ID"),
        }
        atom_claims.append({
            "atom_id": atom_id,
            "witness_digest": _digest(_normal_matrix(matrix)),
            "rank": rank,
            "service_face_id": row["service_face_id"],
            "witness_losses": [
                {"condition_id": condition_id, "loss": _number(loss, atom_id, "witness loss")}
                for condition_id, loss in losses.items()
            ],
            "description": {
                "class": description["class"],
                "reconstruction_digest": _digest(_normal_matrix(reconstruction)),
                "residual_relation_digest": _digest(_normal_matrix(residual)),
                "distortion_bound": _number(distortion, atom_id, "description distortion"),
                "estimator_digest": _digest(description["estimator"]),
                "estimator_calibration_digest": _digest(description["estimator_calibration"]),
                "sampling_law_id": description["sampling_law_id"],
            },
        })
    if [row["atom_id"] for row in atom_claims] != sorted(atoms):
        _reject("INVALID_REQUEST", object_id, "atom evidence must be sorted by atom ID")
    faces = {}
    for atom in atoms.values():
        previous = faces.setdefault(atom["face_id"], atom["face"])
        if previous != atom["face"]:
            _reject("CAPABILITY_MISMATCH", atom["face_id"], "one service-face ID names different condition sets")
    service_faces = [
        {"face_id": face_id, "condition_ids": sorted(face)}
        for face_id, face in sorted(faces.items())
    ]
    nonface_sets = _minimal_nonfaces(frozenset(conditions), set(faces.values()))
    proofs = {}
    for proof in _items(source["minimal_nonface_proofs"], object_id, "minimal nonface proofs", empty=True):
        if not isinstance(proof, dict) or not isinstance(proof.get("condition_ids"), list):
            _reject("INVALID_REQUEST", object_id, "minimal nonface proof is malformed")
        key = frozenset(proof["condition_ids"])
        if key in proofs:
            _reject("INVALID_REQUEST", object_id, "minimal nonface proof condition sets repeat")
        proofs[key] = proof
    if set(proofs) != nonface_sets:
        _reject("CAPABILITY_MISMATCH", object_id, "minimal nonface proofs are not complete for the derived service faces")
    minimal_nonfaces = [
        {
            "nonface_id": _identifier(proofs[key].get("nonface_id"), object_id, "minimal nonface ID"),
            "condition_ids": sorted(key),
            "witness_digest": _digest(proofs[key]),
        }
        for key in sorted(nonface_sets, key=lambda item: tuple(sorted(item)))
    ]
    observation = _record(
        source["observation_contract"],
        {"confidence", "experiment", "kind", "loss_family", "off_support", "sample_count", "selector", "support"},
        object_id,
        "observation contract",
    )
    cover = observation["selector"]
    if (
        not isinstance(cover, list)
        or len(cover) != len(conditions)
        or {row.get("condition_id") for row in cover if isinstance(row, dict)} != set(conditions)
        or any(
            not isinstance(row, dict)
            or set(row) != {"condition_id", "atom_id"}
            or row["atom_id"] not in atoms
            or row["condition_id"] not in atoms[row["atom_id"]]["face"]
            for row in cover
        )
    ):
        _reject("CAPABILITY_MISMATCH", object_id, "observation selector is not a total derived atom cover")
    exclusions = []
    for raw in _items(source["excluded_conditions"], object_id, "excluded conditions", empty=True):
        row = _record(raw, {"cause", "condition_id", "evidence"}, object_id, "excluded condition")
        if row["condition_id"] in conditions:
            _reject("CAPABILITY_MISMATCH", object_id, "covered condition is also excluded")
        exclusions.append({"condition_id": row["condition_id"], "cause": row["cause"], "evidence_digest": _digest(row["evidence"])})
    description = _record(
        source["description_contract"],
        {"description_family", "distortion_metric", "estimator_family", "residual_family"},
        object_id,
        "description contract",
    )
    execution = _record(source["execution_contract"], {"operations", "risk_composition", "sampling_laws"}, object_id, "execution contract")
    sampling_claims = [
        {
            "sampling_law_id": row["sampling_law_id"],
            "kind": row["kind"],
            "law_digest": _digest(row["law"]),
            "work_unit": row["work_unit"],
            "seed_policy": row["seed_policy"],
        }
        for row in _items(execution["sampling_laws"], object_id, "sampling laws")
    ]
    bounds = {}
    for raw in _items(bounds_value, object_id, "operation bounds"):
        row = _record(raw, {"operation_id", "epsilon_exec", "delta_exec"}, object_id, "operation bound")
        operation_id = _identifier(row["operation_id"], object_id, "operation bound ID")
        if operation_id in bounds:
            _reject("INVALID_REQUEST", object_id, "operation bounds repeat an ID")
        bounds[operation_id] = (
            _fraction(row["epsilon_exec"], operation_id, "epsilon_exec"),
            _fraction(row["delta_exec"], operation_id, "delta_exec"),
        )
    operations = {}
    operation_claims = []
    for raw in _items(execution["operations"], object_id, "operations"):
        row = _record(raw, {"loss_propagation", "operation_id", "operator_case_id", "rank_accounting", "sampling_law_id"}, object_id, "operation")
        operation_id = _identifier(row["operation_id"], object_id, "operation ID")
        if operation_id in operations or operation_id not in bounds:
            _reject("INVALID_REQUEST", object_id, "each operation requires one unique execution bound")
        rank_map = _record(row["rank_accounting"], {"kind", "maximum_rank"}, operation_id, "rank accounting")
        loss_map = _record(row["loss_propagation"], {"coefficient", "remainder_bound"}, operation_id, "loss propagation")
        epsilon, delta = bounds[operation_id]
        operations[operation_id] = {
            "epsilon": epsilon,
            "delta": delta,
            "coefficient": _fraction(loss_map["coefficient"], operation_id, "loss coefficient"),
            "remainder": _fraction(loss_map["remainder_bound"], operation_id, "remainder bound"),
        }
        operation_claims.append({
            "operation_id": operation_id,
            "operator_case_id": row["operator_case_id"],
            "rank_accounting_digest": _digest(rank_map),
            "loss_propagation_digest": _digest(loss_map),
            "remainder_bound": _number(operations[operation_id]["remainder"], operation_id, "remainder bound"),
            "epsilon_exec": _number(epsilon, operation_id, "epsilon_exec"),
            "delta_exec": _number(delta, operation_id, "delta_exec"),
            "sampling_law_id": row["sampling_law_id"],
        })
    if set(bounds) != set(operations):
        _reject("INVALID_REQUEST", object_id, "operation bounds and operations differ")
    risk = _record(execution["risk_composition"], {"kind", "proof"}, object_id, "risk composition")
    trace = _record(source["trace_contract"], {"fresh_traffic_unit", "prefix_policy", "protected_trace_family", "steps"}, object_id, "trace contract")
    trace_rows = []
    for index, raw in enumerate(_items(trace["steps"], object_id, "trace steps")):
        row = _record(raw, {"atom_id", "fresh_samples", "fresh_traffic", "operation_id", "step"}, object_id, "trace step")
        if row["step"] != index or row["atom_id"] not in atoms or row["operation_id"] not in operations:
            _reject("CAPABILITY_MISMATCH", object_id, "trace is not contiguous over known atoms and operations")
        operation = operations[row["operation_id"]]
        trace_rows.append({
            **row,
            "description_bytes_resident": atoms[row["atom_id"]]["description_bytes"],
            "metadata_bytes_resident": atoms[row["atom_id"]]["metadata_bytes"],
            "epsilon_exec": operation["epsilon"],
            "delta_exec": operation["delta"],
        })
    atom_resources = []
    for atom_id, atom in atoms.items():
        selected = [row for row in trace_rows if row["atom_id"] == atom_id]
        if not selected:
            _reject("CAPABILITY_MISMATCH", atom_id, "protected trace omits a certified atom")
        atom_resources.append({
            "atom_id": atom_id,
            "description_bytes": atom["description_bytes"],
            "metadata_bytes": atom["metadata_bytes"],
            "fresh_samples_max": max(row["fresh_samples"] for row in selected),
            "fresh_samples_total": sum(row["fresh_samples"] for row in selected),
            "fresh_traffic_max": max(row["fresh_traffic"] for row in selected),
            "fresh_traffic_total": sum(row["fresh_traffic"] for row in selected),
            "epsilon_exec": _number(max(row["epsilon_exec"] for row in selected), atom_id, "atom epsilon"),
            "delta_exec": _number(max(row["delta_exec"] for row in selected), atom_id, "atom delta"),
        })
    operation_resources = []
    for operation_id, operation in operations.items():
        selected = [row for row in trace_rows if row["operation_id"] == operation_id]
        if not selected:
            _reject("CAPABILITY_MISMATCH", operation_id, "protected trace omits a certified operation")
        selected_atoms = {row["atom_id"] for row in selected}
        operation_resources.append({
            "operation_id": operation_id,
            "description_bytes_peak": max(atoms[atom_id]["description_bytes"] for atom_id in selected_atoms),
            "description_bytes_total": sum(atoms[atom_id]["description_bytes"] for atom_id in selected_atoms),
            "metadata_bytes_peak": max(atoms[atom_id]["metadata_bytes"] for atom_id in selected_atoms),
            "metadata_bytes_total": sum(atoms[atom_id]["metadata_bytes"] for atom_id in selected_atoms),
            "fresh_samples_max": max(row["fresh_samples"] for row in selected),
            "fresh_samples_total": sum(row["fresh_samples"] for row in selected),
            "fresh_traffic_max": max(row["fresh_traffic"] for row in selected),
            "fresh_traffic_total": sum(row["fresh_traffic"] for row in selected),
            "epsilon_exec": _number(operation["epsilon"], operation_id, "operation epsilon"),
            "delta_exec": _number(operation["delta"], operation_id, "operation delta"),
        })
    deltas = [row["delta_exec"] for row in trace_rows]
    if risk["kind"] == "DETERMINISTIC":
        total_delta = Fraction(0)
    elif risk["kind"] == "UNION_BOUND":
        total_delta = sum(deltas, Fraction(0))
    elif risk["kind"] == "INDEPENDENT_PRODUCT":
        survival = Fraction(1)
        for delta in deltas:
            survival *= 1 - delta
        total_delta = 1 - survival
    elif risk["kind"] == "DECLARED_DEPENDENCE":
        total_delta = _fraction(risk["proof"].get("total_bound") if isinstance(risk["proof"], dict) else None, object_id, "declared risk bound")
    else:
        _reject("INVALID_REQUEST", object_id, "risk composition kind is unsupported")
    total_epsilon = sum(
        operations[row["operation_id"]]["coefficient"] * row["epsilon_exec"]
        + operations[row["operation_id"]]["remainder"]
        for row in trace_rows
    )
    resources = {
        "eta_rep": _number(eta, object_id, "eta_rep"),
        "epsilon_exec": _number(total_epsilon, object_id, "total epsilon"),
        "delta_exec_total": _number(total_delta, object_id, "total delta"),
        "atom_count": len(atoms),
        "max_atom_rank": max(atom["rank"] for atom in atoms.values()),
        "description_bytes_peak": max(row["description_bytes_resident"] for row in trace_rows),
        "description_bytes_total": sum(atom["description_bytes"] for atom in atoms.values()),
        "metadata_bytes_peak": max(row["metadata_bytes_resident"] for row in trace_rows),
        "metadata_bytes_total": sum(atom["metadata_bytes"] for atom in atoms.values()),
        "fresh_samples_max": max(row["fresh_samples"] for row in trace_rows),
        "fresh_samples_total": sum(row["fresh_samples"] for row in trace_rows),
        "fresh_traffic_max": max(row["fresh_traffic"] for row in trace_rows),
        "fresh_traffic_total": sum(row["fresh_traffic"] for row in trace_rows),
        "fresh_traffic_unit": trace["fresh_traffic_unit"],
        "horizon": len(trace_rows),
    }
    conversion_rows = source["physical_conversion"].get("conversion_rows") if isinstance(source["physical_conversion"], dict) else None
    certificate = {
        "certificate_version": "q19-v1",
        "certificate_id": _digest("unsealed-certificate"),
        "target": {
            "target_digest": _digest(target_record),
            "flattening_digest": _digest(flattening),
            "shape": list(target_shape),
            "field": field,
        },
        "condition_metrics": condition_claims,
        "compatibility": {
            "eta_rep": resources["eta_rep"],
            "rank_budget": rank_budget,
            "service_faces": service_faces,
            "minimal_nonfaces": minimal_nonfaces,
            "cover": cover,
            "excluded_conditions": exclusions,
        },
        "atoms": atom_claims,
        "description_contract": {
            "description_family_digest": _digest(description["description_family"]),
            "distortion_metric_digest": _digest(description["distortion_metric"]),
            "residual_family_digest": _digest(description["residual_family"]),
            "estimator_family_digest": _digest(description["estimator_family"]),
        },
        "observation_contract": {
            "kind": observation["kind"],
            "experiment_digest": _digest(observation["experiment"]),
            "support_digest": _digest(observation["support"]),
            "selector_digest": _digest(observation["selector"]),
            "loss_family_digest": _digest(observation["loss_family"]),
            "sample_count": observation["sample_count"],
            "confidence": observation["confidence"],
            "off_support": observation["off_support"],
        },
        "execution_contract": {
            "sampling_laws": sampling_claims,
            "operations": operation_claims,
            "risk_composition_kind": risk["kind"],
            "risk_composition_digest": _digest(risk),
        },
        "trace_contract": {
            "protected_trace_family_digest": _digest(trace["protected_trace_family"]),
            "schedule_digest": _digest(_normal_exact({"prefix_policy": trace["prefix_policy"], "steps": trace_rows})),
            "prefix_policy": trace["prefix_policy"],
            "horizon": len(trace_rows),
        },
        "resources": resources,
        "resource_tables": {
            "per_atom": atom_resources,
            "per_operation": operation_resources,
            "per_trace_step": [
                {**row, "epsilon_exec": _number(row["epsilon_exec"], object_id, "trace epsilon"), "delta_exec": _number(row["delta_exec"], object_id, "trace delta")}
                for row in trace_rows
            ],
        },
        "physical_conversion": {
            "conversion_rows": conversion_rows,
            "conversion_digest": _digest(conversion_rows),
        },
    }
    certificate["certificate_id"] = _digest({name: value for name, value in certificate.items() if name != "certificate_id"})
    defects = validate("mathematical_certificate", certificate)
    if defects:
        _reject("INVALID_REQUEST", certificate["certificate_id"], "; ".join(defects[:8]))
    return certificate


def _tensor_inventory(value: object, source_root: dict, object_id: str) -> list[dict]:
    rows = _items(value, object_id, "tensor inventory")
    root_tensors = {row["semantic_tensor_id"]: row for row in source_root["tensor_maps"]}
    artifact_paths = {
        row["path"] for row in source_root["provenance"]["identity_material"]["artifacts"]
    }
    normalized = []
    for item in rows:
        row = _record(
            item,
            {"artifact_path", "semantic_tensor_id", "dtype", "shape", "offset", "length"},
            object_id,
            "tensor inventory row",
        )
        tensor_id = _identifier(row["semantic_tensor_id"], object_id, "tensor inventory ID")
        tensor = root_tensors.get(tensor_id)
        if (
            row["artifact_path"] not in artifact_paths
            or tensor is None
            or row["dtype"] != tensor["dtype"]
            or row["shape"] != tensor["shape"]
            or row["length"] != sum(span["length"] for span in tensor["spans"])
            or type(row["offset"]) is not int
            or row["offset"] < 0
        ):
            _reject("CAPABILITY_MISMATCH", tensor_id, "tensor inventory is detached from source artifacts or maps")
        normalized.append(row)
    if (
        normalized != sorted(normalized, key=lambda row: row["semantic_tensor_id"])
        or len(normalized) != len(root_tensors)
        or {row["semantic_tensor_id"] for row in normalized} != set(root_tensors)
        or _digest(normalized)
        != source_root["provenance"]["identity_material"]["tensor_index_digest"]
    ):
        _reject(
            "CAPABILITY_MISMATCH",
            object_id,
            "tensor inventory is not the total unique artifact-bound Q1 source catalog",
        )
    return normalized


def _contribution_map(
    source_root: dict,
    source_root_digest: str,
    certificate: dict,
    target_tensor: str,
    inventory: list[dict],
    tensor_inventory: list[dict],
) -> dict:
    observation_digest = _digest(certificate["observation_contract"])
    composition_digest = _digest(certificate["execution_contract"])
    atom_relations = [
        {
            "atom_id": atom["atom_id"],
            "service_face_id": atom["service_face_id"],
            "description_digest": _digest(atom["description"]),
            "residual_relation_digest": atom["description"]["residual_relation_digest"],
        }
        for atom in certificate["atoms"]
    ]
    inventory_by_tensor = {row["semantic_tensor_id"]: row for row in tensor_inventory}
    tensors = []
    for tensor in source_root["tensor_maps"]:
        elements = math.prod(tensor["shape"])
        byte_count = sum(span["length"] for span in tensor["spans"])
        tensors.append({
            "source_tensor": tensor["semantic_tensor_id"],
            "source_artifact": inventory_by_tensor[tensor["semantic_tensor_id"]]["artifact_path"],
            "executable_tensor": tensor["semantic_tensor_id"],
            "dtype": tensor["dtype"],
            "shape": tensor["shape"],
            "elements": elements,
            "bytes": byte_count,
            "classification": "atom_conditioned" if tensor["semantic_tensor_id"] == target_tensor else "represented",
            "transform_relation": "Q19_ATOM_DESCRIPTION" if tensor["semantic_tensor_id"] == target_tensor else "IDENTITY",
            "error_bound": certificate["resources"]["epsilon_exec"] if tensor["semantic_tensor_id"] == target_tensor else 0.0,
            "span_digest": _digest(tensor["spans"]),
            "certificate_id": certificate["certificate_id"],
            "observation_contract_digest": observation_digest,
            "composition_digest": composition_digest,
            "atom_relations": atom_relations if tensor["semantic_tensor_id"] == target_tensor else [],
        })
    semantic_assets = [
        {"name": name, "source_digest": value, "executable_digest": value, "relation": "IDENTITY"}
        for name, value in sorted(source_root["semantic_assets"].items())
    ]
    operators = [
        {
            "operator": operator,
            "case_ids": [row["case_id"] for row in inventory if row["operator"] == operator],
            "relation": "PINNED_RUNTIME_EQUIVALENT",
        }
        for operator in source_root["operators"]
    ]
    artifacts = []
    source_artifacts = source_root["provenance"]["identity_material"]["artifacts"]
    for artifact in source_artifacts:
        members = [row for row in tensor_inventory if row["artifact_path"] == artifact["path"]]
        tensor_bytes = sum(row["length"] for row in members)
        if tensor_bytes > artifact["size"]:
            _reject("CAPABILITY_MISMATCH", artifact["path"], "tensor bytes exceed their source container")
        artifacts.append({
            **artifact,
            "tensor_ids": [row["semantic_tensor_id"] for row in members],
            "tensor_bytes": tensor_bytes,
            "container_overhead_bytes": artifact["size"] - tensor_bytes,
        })
    return {
        "version": "q58-v1",
        "source_root": source_root_digest,
        "certificate_id": certificate["certificate_id"],
        "observation_contract_digest": observation_digest,
        "composition_digest": composition_digest,
        "target_tensor": target_tensor,
        "artifacts": artifacts,
        "tensors": tensors,
        "semantic_assets": semantic_assets,
        "operators": operators,
        "totals": {
            "tensor_count": len(tensors),
            "element_count": sum(row["elements"] for row in tensors),
            "byte_count": sum(row["bytes"] for row in tensors),
            "source_artifact_bytes": sum(row["size"] for row in artifacts),
            "container_overhead_bytes": sum(row["container_overhead_bytes"] for row in artifacts),
            "semantic_asset_count": len(semantic_assets),
            "operator_count": len(operators),
        },
    }


def _execution_plan(
    source_root: dict,
    source_root_digest: str,
    certificate: dict,
    profile: dict,
    contribution: dict,
    inventory: list[dict],
    prior_failures: list[dict],
    cartridge: str | Path,
) -> dict:
    locations = sorted(page_locations(cartridge, source_root_digest), key=lambda item: item.page_digest)
    plan = {
        "plan_version": "compiled-plan-v1",
        "plan_id": _digest("unsealed-plan"),
        "selected_mode": "COMPILED_CERTIFIED",
        "prior_mode_failures": prior_failures,
        "target_digest": certificate["target"]["target_digest"],
        "profile_digest": _digest(profile),
        "certificate_id": certificate["certificate_id"],
        "tensor_graph_digest": _digest(source_root["tensor_maps"]),
        "page_map_digest": _digest([
            {"page_digest": item.page_digest, "length": item.length} for item in locations
        ]),
        "layout_digest": _digest([
            {"page_digest": item.page_digest, "segment_id": item.segment_id, "offset": item.offset, "length": item.length}
            for item in locations
        ]),
        "precision_planes_digest": _digest([
            {"semantic_tensor_id": item["semantic_tensor_id"], "dtype": item["dtype"], "plane": item["plane"]}
            for item in source_root["tensor_maps"]
        ]),
        "semantic_manifest_digest": _digest(contribution),
        "invalidation_graph_digest": _digest({
            "source_root": source_root_digest,
            "certificate_id": certificate["certificate_id"],
            "contribution_map_digest": _digest(contribution),
        }),
        "dispatch": OPERATOR_DISPATCH,
        "resource_limits": certificate["resources"],
        "artifact_refs": sorted({
            certificate["target"]["target_digest"],
            *(item["digest"] for item in source_root["provenance"]["identity_material"]["artifacts"]),
        }),
        "weight_payload_bytes": 0,
    }
    plan["plan_id"] = _digest({name: value for name, value in plan.items() if name != "plan_id"})
    defects = validate("execution_plan", plan)
    if defects:
        _reject("INVALID_REQUEST", plan["plan_id"], "; ".join(defects[:8]))
    if {row["case_id"] for row in inventory} != {
        operation["operator_case_id"] for operation in certificate["execution_contract"]["operations"]
    }:
        _reject("UNSUPPORTED_OPERATOR", plan["plan_id"], "source tuple inventory and certificate operations differ")
    return plan


def _extent_metrics(source_root: dict, proof: dict, target_extent_bytes: int) -> dict:
    source_bytes = sum(
        item["size"]
        for item in source_root["provenance"]["identity_material"]["artifacts"]
    )
    _u64(target_extent_bytes, source_root["identity"], "target extent bytes")
    target_parameter_bytes = sum(item["length"] for item in proof["tensor_inventory"])
    integrity_bytes = len(canonical_bytes(proof))
    declared = max(source_bytes, target_extent_bytes) + PAGE_BYTES + integrity_bytes
    return {
        "source_extent_bytes": source_bytes,
        "target_extent_bytes": target_extent_bytes,
        "target_parameter_bytes": target_parameter_bytes,
        "window_bytes": PAGE_BYTES,
        "journal_bytes": 0,
        "integrity_bytes": integrity_bytes,
        "rollback_delta_bytes": 0,
        "precision_bytes": 0,
        "reserve_bytes": 0,
        "declared_peak_bytes": declared,
        "physical_measurement": "DARWIN_F_LOG2PHYS_EXT",
        "observed_within_declared_peak": True,
        "parameter_storage": "FCLONEFILEAT_VERIFIED_EXTENTS",
    }


def _preparation_inputs(source_value: object, extents: object, cartridge: str | Path):
    source = _source(source_value)
    descriptors = _extent_descriptors(source, extents, cartridge)
    manifest, tensors = _manifest(source, descriptors)
    material = _source_material(source, manifest, tensors)
    return source, descriptors, manifest, tensors, material


def _plan_revision(source: object, extents: object, cartridge: str | Path) -> str:
    source_record, _, manifest, tensors, _ = _preparation_inputs(source, extents, cartridge)
    return _digest(_compile_inputs(source_record, manifest, tensors))


def _prepare_revision(
    source: object,
    extents: object,
    cartridge: str | Path,
    expected_plan_digest: str,
) -> PreparedRevision:
    expected_plan_digest = _exact_digest(
        expected_plan_digest, "compiler:prepare", "expected preparation plan digest"
    )
    source_record, descriptors, manifest, tensors, source_material = _preparation_inputs(
        source, extents, cartridge
    )
    observed_plan_digest = _digest(_compile_inputs(source_record, manifest, tensors))
    if observed_plan_digest != expected_plan_digest:
        _reject("SOURCE_REVISION_CHANGED", source_record["identity"], "compiler inputs changed after durable planning")
    try:
        source_root_digest = adopt_safetensors(descriptors, cartridge, source_material)
    except CassetteError as error:
        if error.code == "IDENTITY_MISMATCH":
            _reject(
                "SOURCE_REVISION_CHANGED",
                source_record["identity"],
                "completed source extent changed before same-read compilation could publish a candidate",
                "Q51/Q60: immutable completed extents before candidate publication",
            )
        raise
    source_root = load_root(cartridge, source_root_digest)
    values, shape = _decode_tensor(
        source_root, cartridge, source_root_digest, manifest["target_tensor"]
    )
    evidence = json.loads(canonical_bytes(manifest["evidence"]), object_pairs_hook=_unique_object)
    target = evidence.get("target") if isinstance(evidence, dict) else None
    if not isinstance(target, dict) or set(target) != {"field", "flattening_order", "shape", "source_shape"}:
        _reject("INVALID_REQUEST", source_record["identity"], "manifest target evidence must omit source values and name exact shapes")
    if target["source_shape"] != shape:
        _reject("CAPABILITY_MISMATCH", manifest["target_tensor"], "manifest source shape differs from the verified tensor")
    evidence["target"] = {**target, "source_values": values}
    certificate = _certificate(
        evidence, manifest["eta_rep"], manifest["rank_budget"], manifest["operation_bounds"]
    )
    tensor_inventory = _tensor_inventory(tensors, source_root, source_root_digest)
    contribution = _contribution_map(
        source_root,
        source_root_digest,
        certificate,
        manifest["target_tensor"],
        manifest["operator_inventory"],
        tensor_inventory,
    )
    profile = manifest["profile"]
    plan = _execution_plan(
        source_root,
        source_root_digest,
        certificate,
        profile,
        contribution,
        manifest["operator_inventory"],
        manifest["prior_mode_failures"],
        cartridge,
    )
    proof = {
        "operator_inventory": manifest["operator_inventory"],
        "tensor_inventory": tensor_inventory,
        "evidence": evidence,
        "certificate": certificate,
        "profile": profile,
        "contribution_map": contribution,
        "execution_plan": plan,
    }
    bundle = {
        "version": _VERSION,
        "source_identity": source_record["identity"],
        "source_root": source_root_digest,
        "preparation_plan_digest": expected_plan_digest,
        **proof,
        "extent_metrics": _extent_metrics(
            source_root,
            proof,
            sum(location.length for location in page_locations(cartridge, source_root_digest)),
        ),
    }
    footprint = extent_footprint(cartridge, source_root_digest, descriptors)
    if (
        footprint["allocated_peak_bytes"] + bundle["extent_metrics"]["integrity_bytes"]
        > bundle["extent_metrics"]["declared_peak_bytes"]
    ):
        _reject(
            "CAPACITY_EXCEEDED",
            source_record["identity"],
            "measured source and target physical extents exceed the Q4 declaration",
        )
    if len(canonical_bytes(bundle)) > _MAX_RECORD_BYTES:
        _reject(
            "CONTAINMENT_REJECTED",
            source_record["identity"],
            "compiled proof bundle exceeds the bounded four-megabyte manifest authority",
        )
    transform_digest = _digest(bundle)
    source_identity = source_root["provenance"]["identity_material"]
    compiled_material = IdentityTuple(
        revision_kind="executable",
        source_kind=source_material.source_kind,
        source_alias=source_material.source_alias,
        canonical_locator=source_material.canonical_locator,
        requested_revision=source_material.requested_revision,
        immutable_revision=source_material.immutable_revision,
        artifacts=source_material.artifacts,
        format_versions=tuple((*source_material.format_versions, ("cassette", _VERSION))),
        tensor_index_digest=source_identity["tensor_index_digest"],
        config_digest=source_identity["config_digest"],
        architecture=source_identity["architecture"],
        operator_set=tuple(source_identity["operator_set"]),
        tokenizer_digest=source_identity["tokenizer_digest"],
        processor_digest=source_identity["processor_digest"],
        template_digest=source_identity["template_digest"],
        precision_scheme=source_identity["precision_scheme"],
        license_digest=source_identity["license_digest"],
        parent_ids=(source_record["identity"],),
        transform_manifest_digest=transform_digest,
    )
    candidate = derive_root(cartridge, source_root_digest, compiled_material, (bundle,))
    _verify_bundle(
        cartridge,
        candidate,
        source_record["identity"],
        expected_plan_digest,
        descriptors,
    )
    return PreparedRevision(
        source_record["identity"],
        source_material.artifacts,
        expected_plan_digest,
        candidate,
    )


def _verify_bundle(
    cartridge: str | Path,
    root_digest: str,
    source_identity: str,
    plan_digest: str,
    source_descriptors: Mapping[str, int] | None = None,
) -> tuple[dict, dict, dict, dict, str]:
    _exact_digest(root_digest, "compiler:verify", "candidate root digest")
    _exact_digest(source_identity, root_digest, "source identity")
    _exact_digest(plan_digest, root_digest, "preparation plan digest")
    root = load_root(cartridge, root_digest)
    if len(root["plans"]) != 1:
        _reject("ROOT_INVALID", root_digest, "compiled root requires exactly one preparation bundle")
    bundle = _record(root["plans"][0], _BUNDLE_FIELDS, root_digest, "preparation bundle")
    if len(canonical_bytes(bundle)) > _MAX_RECORD_BYTES:
        _reject("ROOT_INVALID", root_digest, "compiled proof bundle exceeds its bounded authority")
    if (
        bundle["version"] != _VERSION
        or bundle["source_identity"] != source_identity
        or bundle["preparation_plan_digest"] != plan_digest
        or root["parents"] != [source_identity]
    ):
        _reject("IDENTITY_MISMATCH", root_digest, "compiled root is detached from its source or durable plan")
    source_root = load_root(cartridge, bundle["source_root"])
    if source_root["identity"] != source_identity:
        _reject("IDENTITY_MISMATCH", root_digest, "preparation bundle names a foreign source root")
    inventory = _inventory(bundle["operator_inventory"], root_digest)
    tensor_inventory = _tensor_inventory(bundle["tensor_inventory"], source_root, root_digest)
    certificate = bundle["certificate"]
    plan = bundle["execution_plan"]
    if validate("mathematical_certificate", certificate) or validate("execution_plan", plan):
        _reject("ROOT_INVALID", root_digest, "compiled certificate or execution plan is structurally invalid")
    expected_contribution = _contribution_map(
        source_root,
        bundle["source_root"],
        certificate,
        bundle["contribution_map"].get("target_tensor") if isinstance(bundle["contribution_map"], dict) else "",
        inventory,
        tensor_inventory,
    )
    if bundle["contribution_map"] != expected_contribution:
        _reject("CAPABILITY_MISMATCH", root_digest, "source contribution map is incomplete, duplicated, or detached")
    expected_plan = _execution_plan(
        source_root,
        bundle["source_root"],
        certificate,
        bundle["profile"],
        expected_contribution,
        inventory,
        plan.get("prior_mode_failures") if isinstance(plan, dict) else [],
        cartridge,
    )
    if plan != expected_plan:
        _reject("CAPABILITY_MISMATCH", root_digest, "execution plan is detached from canonical pages or proof objects")
    proof = {
        "operator_inventory": inventory,
        "tensor_inventory": tensor_inventory,
        "evidence": bundle["evidence"],
        "certificate": certificate,
        "profile": bundle["profile"],
        "contribution_map": expected_contribution,
        "execution_plan": expected_plan,
    }
    metrics = bundle["extent_metrics"]
    if not isinstance(metrics, dict):
        _reject("ROOT_INVALID", root_digest, "compiled root lacks its exact Q4 extent footprint")
    expected_metrics = _extent_metrics(
        source_root,
        proof,
        sum(location.length for location in page_locations(cartridge, bundle["source_root"])),
    )
    if metrics != expected_metrics:
        _reject("CAPABILITY_MISMATCH", root_digest, "peak-extent declaration does not match the compiled objects")
    if source_descriptors is not None:
        observed_footprint = extent_footprint(
            cartridge, bundle["source_root"], source_descriptors
        )
        if (
            observed_footprint["allocated_peak_bytes"] + metrics["integrity_bytes"]
            > metrics["declared_peak_bytes"]
        ):
            _reject(
                "CAPACITY_EXCEEDED",
                root_digest,
                "remeasured source and target physical extents exceed the Q4 declaration",
            )
    material = root["provenance"]["identity_material"]
    if material["transform_manifest_digest"] != _digest(bundle):
        _reject("IDENTITY_MISMATCH", root_digest, "compiled identity does not bind the complete preparation bundle")
    return plan, certificate, bundle["evidence"], bundle["profile"], root["identity"]


def _boundary(label: str, source: object, function, *arguments):
    try:
        return function(*arguments)
    except CassetteError:
        raise
    except OSError as error:
        object_id = source.get("identity", f"compiler:{label}") if isinstance(source, dict) else f"compiler:{label}"
        _reject(
            "SOURCE_UNAVAILABLE",
            str(object_id),
            f"{label} could not retain its verified local extent: {error}",
        )
    except (
        AttributeError,
        IndexError,
        KeyError,
        OverflowError,
        RecursionError,
        TypeError,
        ValueError,
        struct.error,
    ) as error:
        object_id = (
            source.get("identity", f"compiler:{label}")
            if isinstance(source, dict)
            else f"compiler:{label}"
        )
        _reject(
            "INVALID_REQUEST",
            str(object_id),
            f"{label} input failed bounded structural interpretation: {type(error).__name__}",
        )


def plan_revision(source: object, extents: object, cartridge: str | Path) -> str:
    """Return the immutable compiler-input digest after contained source-driven inventory."""

    return _boundary("plan", source, _plan_revision, source, extents, cartridge)


def prepare_revision(
    source: object,
    extents: object,
    cartridge: str | Path,
    expected_plan_digest: str,
) -> PreparedRevision:
    """Consume verified bytes once, derive every proof object, and return one unpublished candidate."""

    return _boundary(
        "prepare",
        source,
        _prepare_revision,
        source,
        extents,
        cartridge,
        expected_plan_digest,
    )


def verify_bundle(
    cartridge: str | Path,
    root_digest: str,
    source_identity: str,
    plan_digest: str,
    source_descriptors: Mapping[str, int] | None = None,
) -> tuple[dict, dict, dict, dict, str]:
    """Reject any detached map, certificate, plan, source parent, or extent claim before publication."""

    return _boundary(
        "verify",
        {"identity": source_identity},
        _verify_bundle,
        cartridge,
        root_digest,
        source_identity,
        plan_digest,
        source_descriptors,
    )
