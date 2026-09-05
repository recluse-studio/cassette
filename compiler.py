# compiler.py — contained compilation, invalidation, export, Q19 certificates, and hardware plans (Q4/Q11/Q19/Q26/Q27/Q30/Q33/Q37/Q40/Q51/Q55/Q58/Q59/Q60/Q61/Q62/Q70/Q73/Q75); depends on errors.py, schema, store.py.
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
from schema.tables import (
    DISPATCH_ROWS,
    EXPORT_TARGETS,
    HARDWARE_PLAN_CATALOG_VERSION,
    HARDWARE_PLAN_VERSION,
    OPERATOR_DISPATCH,
    Q40_MODES,
)
from schema.validator import validate
from store import (
    ArtifactIdentity,
    CapacityCoordinator,
    IdentityTuple,
    PAGE_BYTES,
    adapter_export_fields,
    adopt_safetensors,
    canonical_bytes,
    derive_root,
    derived_root_shape,
    digest_bytes,
    export_semantic_binding,
    export_shape,
    extent_footprint,
    inspect_safetensors,
    load_root,
    model_identity,
    page_index_byte_count,
    page_locations,
    read_training_page,
    read_tensor,
)

_MANIFEST_KEY = "cassette.compiler.v1"
_VERSION = "s19-compiler-v1"
_RECOMPILE_VERSION = "s25-compiler-v1"
_DERIVATION_VERSION = "q27-q75-v1"
_RECOVERY_KINDS = (
    "condition", "atom", "description", "estimator", "observation", "precision",
)
_RECOVERY_INPUTS = {
    "condition": "condition_metric",
    "atom": "atom",
    "description": "description",
    "estimator": "residual_estimator",
    "observation": "observation",
    "precision": "precision",
}
_INVALIDATION_INPUTS = (
    "weights", "condition_metric", "atom", "cover", "observation", "description",
    "residual_estimator", "composition", "precision", "tokenizer", "template",
    "context", "operator",
)
_DERIVATION_ORDER = (
    "protected_trace_corpus", "page_stats", "page_layout", "semantic_manifest",
    "observation_contract", "condition_metrics", "compatibility_witnesses",
    "atom_cover", "description_distortion", "residual_metadata",
    "estimator_calibration", "precision_calibration", "composition_proof",
    "kernel_plan", "physical_schedule", "quality_proof", "protocol_capabilities",
    "cache_key",
)
_DERIVATION_DEPENDENCIES = {
    "protected_trace_corpus": (
        "input:observation", "input:composition", "input:tokenizer", "input:template",
        "input:context", "input:operator",
    ),
    "page_stats": ("input:weights",),
    "page_layout": ("input:weights", "input:precision"),
    "semantic_manifest": (
        "input:precision", "input:tokenizer", "input:template", "input:context",
        "input:operator",
    ),
    "observation_contract": (
        "input:cover", "input:observation", "input:tokenizer", "input:template",
        "input:context", "input:operator", "artifact:protected_trace_corpus",
    ),
    "condition_metrics": (
        "input:weights", "input:condition_metric", "input:tokenizer", "input:template",
        "input:context", "input:operator", "artifact:protected_trace_corpus",
    ),
    "compatibility_witnesses": (
        "input:weights", "input:atom", "input:tokenizer", "input:template",
        "input:context", "input:operator", "artifact:condition_metrics",
    ),
    "atom_cover": (
        "input:weights", "input:atom", "input:cover", "input:observation",
        "input:tokenizer", "input:template", "input:context", "input:operator",
        "artifact:compatibility_witnesses", "artifact:observation_contract",
    ),
    "description_distortion": (
        "input:weights", "input:atom", "input:description", "input:precision",
        "artifact:compatibility_witnesses",
    ),
    "residual_metadata": (
        "input:weights", "input:atom", "input:description",
        "input:residual_estimator", "input:precision",
        "artifact:description_distortion",
    ),
    "estimator_calibration": (
        "input:weights", "input:atom", "input:residual_estimator",
        "input:observation", "artifact:protected_trace_corpus",
        "artifact:residual_metadata",
    ),
    "precision_calibration": (
        "input:weights", "input:description", "input:residual_estimator",
        "input:precision", "artifact:page_layout", "artifact:residual_metadata",
    ),
    "composition_proof": (
        "input:composition", "input:observation", "input:operator",
        "artifact:atom_cover", "artifact:description_distortion",
        "artifact:estimator_calibration", "artifact:protected_trace_corpus",
    ),
    "kernel_plan": (
        "input:weights", "input:precision", "input:operator", "artifact:page_layout",
        "artifact:atom_cover", "artifact:description_distortion",
        "artifact:estimator_calibration", "artifact:composition_proof",
    ),
    "physical_schedule": (
        "input:weights", "input:context", "input:precision", "input:operator",
        "artifact:page_stats", "artifact:page_layout", "artifact:kernel_plan",
        "artifact:composition_proof",
    ),
    "quality_proof": (
        "artifact:condition_metrics", "artifact:compatibility_witnesses",
        "artifact:atom_cover", "artifact:description_distortion",
        "artifact:estimator_calibration", "artifact:precision_calibration",
        "artifact:composition_proof", "artifact:physical_schedule",
    ),
    "protocol_capabilities": (
        "input:tokenizer", "input:template", "input:context", "input:operator",
        "artifact:semantic_manifest", "artifact:observation_contract",
        "artifact:kernel_plan", "artifact:quality_proof",
    ),
    "cache_key": tuple(
        [f"input:{name}" for name in _INVALIDATION_INPUTS]
        + [f"artifact:{name}" for name in _DERIVATION_ORDER[:-1]]
    ),
}
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
_RECOMPILE_BUNDLE_FIELDS = _BUNDLE_FIELDS | {"derivation", "recovery"}
_SPECIFICATION_FIELDS = frozenset({
    "source_root", "target_tensor", "evidence", "profile", "eta_rep", "rank_budget",
    "operation_bounds", "operator_inventory", "tensor_inventory", "prior_mode_failures", "architecture",
    "config_digest", "format_versions", "precision_scheme", "processor_digest",
    "template_digest", "tokenizer_digest",
})
_TRAINING_MANIFEST_FIELDS = frozenset({
    "format", "job_id", "tier", "operation", "parent_root", "parent_identity",
    "parent_certificate_digest", "base_precision", "delta_precision", "operator_cases",
    "adapter_rank", "adapter_scale", "step", "total_steps", "optimizer_step",
    "data_cursor", "random_seed", "rng_counter", "window_limit_bytes",
    "declared_peak_bytes", "base_pages", "delta_pages", "objective_pages",
    "calibration_pages", "state_pages", "trace_pages", "master_pages", "admission",
    "meter",
})
_HARDWARE_CATALOG_FIELDS = frozenset({
    "version", "catalog_id", "q19_certificate_digest", "base_execution_plan_id", "plans",
})
_HARDWARE_PLAN_FIELDS = frozenset({
    "plan_version", "plan_id", "plan_name", "profile_predicate",
    "q19_certificate_digest", "condition_selector", "atom_refs", "description_budget",
    "metadata_budget", "fresh_sample_or_exact_read_budget", "error_risk_horizon",
    "page_order", "read_groups", "precision_budget", "kernel_dispatch", "concurrency",
    "prefetch_policy", "memory_schedule", "expected_metrics", "weight_payload_bytes",
})
_HARDWARE_SPEC_FIELDS = frozenset({
    "plan_name", "profile_predicate", "page_order", "read_groups", "io_queue_depth",
    "prefetch_policy",
})
_PROFILE_SPEC_FIELDS = frozenset({
    "apple_class", "request_class", "minimum_unified_memory_bytes",
    "minimum_recommended_working_set_bytes", "minimum_sustained_read_bytes_per_second",
    "maximum_p99_read_latency_ns", "requires_writable_storage",
    "operation_plan_profile_digest",
})
_PROFILE_PREDICATE_FIELDS = _PROFILE_SPEC_FIELDS | {
    "required_operator_case_ids", "required_apple_features",
}
_MEASURED_PROFILE_FIELDS = frozenset({
    "apple_class", "request_class", "operation_plan_profile_digest", "unified_memory_bytes",
    "recommended_max_working_set_bytes", "sustained_read_bytes_per_second",
    "p99_read_latency_ns", "operator_case_ids", "apple_features",
    "writable_storage",
})
_MEASURED_PROFILE_DESCRIPTIVE_FIELDS = frozenset({
    "media", "connector", "brand", "advertised_speed", "nominal_capacity_bytes",
})
_READ_GROUP_FIELDS = frozenset({"ordinal", "page_digests", "bytes"})
_PREFETCH_FIELDS = frozenset({"kind", "lookahead_pages"})
_HARDWARE_INVARIANT = "Q11/Q33/Q59: certified metadata-only hardware plans over one executable revision"
_MAX_READ_GROUP_BYTES = 32 * 1024 * 1024
_MAX_PLAN_METADATA_BYTES = 4 * 1024**3
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
_EXPORT_TARGETS = frozenset(EXPORT_TARGETS)


@dataclass(frozen=True, slots=True)
class PreparedRevision:
    """Compiler-owned present-byte proof and immutable candidate-root claim."""

    source_identity: str
    verified_artifacts: tuple[ArtifactIdentity, ...]
    plan_digest: str
    candidate_root: str


@dataclass(frozen=True, slots=True)
class HardwarePlanSelection:
    """One measured-profile selection from a verified metadata-only plan catalog."""

    root_digest: str
    plan_id: str
    certificate_id: str
    measured_profile_digest: str
    predicted_total_latency_ns: int
    plan: dict


@dataclass(frozen=True, slots=True)
class RecompiledRevision:
    """One unpublished deterministic child plus the exact Q27 reuse decision that built it."""

    source_identity: str
    plan_digest: str
    candidate_root: str
    derivation_digest: str
    changed_inputs: tuple[str, ...]
    invalidated_artifacts: tuple[str, ...]
    recomputed_artifacts: tuple[str, ...]
    reused_artifacts: tuple[str, ...]


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


def _number(value: Fraction, object_id: str, label: str) -> float | str:
    try:
        result = float(value)
    except OverflowError:
        result = math.inf
    if not math.isfinite(result) or value < 0 or value > Fraction("1e300"):
        _reject("CAPABILITY_MISMATCH", object_id, f"{label} is outside the certificate number domain")
    if Fraction(str(result)) == value:
        return result
    exact = f"{value.numerator}/{value.denominator}"
    if len(exact) > 128:
        _reject("CAPABILITY_MISMATCH", object_id, f"{label} exceeds the exact certificate scalar bound")
    return exact


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
    if any(lowered.endswith(suffix) for suffix in _UNSAFE_SUFFIXES):
        _reject("CONTAINMENT_REJECTED", object_id, "first-release compilation accepts data-only SafeTensors artifacts")
    if lowered.endswith(".gguf"):
        _reject(
            "MODEL_UNSUPPORTED",
            object_id,
            "GGUF import is available, but the first compiled-preparation path requires SafeTensors",
        )
    if not lowered.endswith(".safetensors"):
        _reject("CONTAINMENT_REJECTED", object_id, "artifact type is outside the data-only compiler allowlist")
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
        if not min(Fraction(1), sum(deltas, Fraction(0))) <= total_delta <= 1:
            _reject("CAPABILITY_MISMATCH", object_id, "a declared total alone cannot justify risk below the union bound")
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
            "confidence": _number(_fraction(observation["confidence"], object_id, "observation confidence"), object_id, "observation confidence"),
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


def _canonical_copy(value: object) -> object:
    """Copy one bounded JSON value through the repository's canonical representation."""

    payload = canonical_bytes(value)
    if len(payload) > _MAX_RECORD_BYTES:
        raise ValueError("canonical compiler record exceeds four megabytes")
    return json.loads(payload, object_pairs_hook=_unique_object)


def _axis_materials(
    source_root: dict,
    target_tensor: str,
    evidence: dict,
    profile: dict,
    inventory: list[dict],
    semantics: dict,
    controls: dict,
    recovery: dict[str, dict],
) -> dict[str, object]:
    atoms = _items(evidence["atoms"], "invalidation:inputs", "atom evidence")
    observation = _record(
        evidence["observation_contract"],
        {"confidence", "experiment", "kind", "loss_family", "off_support", "sample_count", "selector", "support"},
        "invalidation:inputs",
        "observation contract",
    )
    descriptions = []
    estimators = []
    atom_values = []
    for value in atoms:
        atom = _record(
            value,
            {"atom_id", "description", "matrix", "service_face_id"},
            "invalidation:inputs",
            "atom evidence",
        )
        description = _record(
            atom["description"],
            {"class", "description_bytes", "estimator", "estimator_calibration", "metadata_bytes", "reconstruction", "sampling_law_id"},
            "invalidation:inputs",
            "description evidence",
        )
        atom_values.append({
            "atom_id": atom["atom_id"],
            "matrix": atom["matrix"],
            "service_face_id": atom["service_face_id"],
        })
        descriptions.append({
            "atom_id": atom["atom_id"],
            "class": description["class"],
            "description_bytes": description["description_bytes"],
            "metadata_bytes": description["metadata_bytes"],
            "reconstruction": description["reconstruction"],
            "sampling_law_id": description["sampling_law_id"],
        })
        estimators.append({
            "atom_id": atom["atom_id"],
            "estimator": description["estimator"],
            "estimator_calibration": description["estimator_calibration"],
        })
    target_maps = [
        row for row in source_root["tensor_maps"] if row["semantic_tensor_id"] == target_tensor
    ]
    if len(target_maps) != 1:
        _reject("CAPABILITY_MISMATCH", target_tensor, "invalidation input requires one exact target tensor map")
    execution = _record(
        evidence["execution_contract"],
        {"operations", "risk_composition", "sampling_laws"},
        "invalidation:inputs",
        "execution contract",
    )
    raw = {
        "weights": {
            "target_tensor": target_tensor,
            "target": evidence["target"],
            "target_tensor_map": target_maps[0],
            "tensor_maps": source_root["tensor_maps"],
            "artifacts": source_root["provenance"]["identity_material"]["artifacts"],
            "tensor_index_digest": source_root["provenance"]["identity_material"]["tensor_index_digest"],
        },
        "condition_metric": {
            "conditions": evidence["conditions"],
            "eta_rep": controls["eta_rep"],
        },
        "atom": {
            "atoms": atom_values,
            "minimal_nonface_proofs": evidence["minimal_nonface_proofs"],
            "rank_budget": controls["rank_budget"],
        },
        "cover": observation["selector"],
        "observation": {
            "contract": {
                name: value for name, value in observation.items() if name != "selector"
            },
            "excluded_conditions": evidence["excluded_conditions"],
        },
        "description": {
            "contract": evidence["description_contract"],
            "atoms": descriptions,
        },
        "residual_estimator": {
            "atoms": estimators,
            "sampling_laws": execution["sampling_laws"],
        },
        "composition": {
            "operations": [
                {
                    name: value for name, value in row.items()
                    if name != "operator_case_id"
                }
                for row in execution["operations"]
            ],
            "operation_bounds": controls["operation_bounds"],
            "risk_composition": execution["risk_composition"],
            "trace_contract": evidence["trace_contract"],
        },
        "precision": {
            "precision_scheme": semantics["precision_scheme"],
            "format_versions": semantics["format_versions"],
            "tensor_dtypes": [
                {"semantic_tensor_id": row["semantic_tensor_id"], "dtype": row["dtype"]}
                for row in source_root["tensor_maps"]
            ],
        },
        "tokenizer": semantics["tokenizer_digest"],
        "template": semantics["template_digest"],
        "context": {
            "profile": profile,
            "physical_conversion": evidence["physical_conversion"],
            "architecture": semantics["architecture"],
            "config_digest": semantics["config_digest"],
            "processor_digest": semantics["processor_digest"],
            "prior_mode_failures": controls["prior_mode_failures"],
            "license_digest": source_root["provenance"]["identity_material"]["license_digest"],
        },
        "operator": {
            "operator_inventory": inventory,
            "operator_set": semantics["operator_set"],
            "operation_cases": [
                {
                    "operation_id": row["operation_id"],
                    "operator_case_id": row["operator_case_id"],
                }
                for row in execution["operations"]
            ],
        },
    }
    return {
        name: {
            "value": raw[name],
            "recovery": recovery.get(name),
        }
        for name in _INVALIDATION_INPUTS
    }


def _derivation_products(
    source_root: dict,
    target_tensor: str,
    evidence: dict,
    certificate: dict,
    profile: dict,
    inventory: list[dict],
    tensor_inventory: list[dict],
    semantics: dict,
) -> dict[str, object]:
    atom_descriptions = [
        {
            "atom_id": row["atom_id"],
            "description": {
                name: value for name, value in row["description"].items()
                if name not in {"estimator_digest", "estimator_calibration_digest"}
            },
        }
        for row in certificate["atoms"]
    ]
    estimator_claims = [
        {
            "atom_id": row["atom_id"],
            "estimator_digest": row["description"]["estimator_digest"],
            "estimator_calibration_digest": row["description"]["estimator_calibration_digest"],
        }
        for row in certificate["atoms"]
    ]
    witness_claims = [
        {
            "atom_id": row["atom_id"],
            "witness_digest": row["witness_digest"],
            "rank": row["rank"],
            "service_face_id": row["service_face_id"],
            "witness_losses": row["witness_losses"],
        }
        for row in certificate["atoms"]
    ]
    page_layout = [
        {
            "semantic_tensor_id": row["semantic_tensor_id"],
            "dtype": row["dtype"],
            "shape": row["shape"],
            "spans": row["spans"],
        }
        for row in source_root["tensor_maps"]
    ]
    products = {
        "protected_trace_corpus": {
            "excluded_conditions": evidence["excluded_conditions"],
            "trace_contract": evidence["trace_contract"],
        },
        "page_stats": {
            "tensor_inventory": tensor_inventory,
            "tensor_count": len(tensor_inventory),
            "tensor_bytes": sum(row["length"] for row in tensor_inventory),
        },
        "page_layout": page_layout,
        "semantic_manifest": {
            "precision_scheme": semantics["precision_scheme"],
            "processor_digest": semantics["processor_digest"],
            "template_digest": semantics["template_digest"],
            "tokenizer_digest": semantics["tokenizer_digest"],
            "operator_set": semantics["operator_set"],
            "context_digest": _digest(profile),
        },
        "observation_contract": certificate["observation_contract"],
        "condition_metrics": certificate["condition_metrics"],
        "compatibility_witnesses": {
            "atoms": witness_claims,
            "service_faces": certificate["compatibility"]["service_faces"],
            "minimal_nonfaces": certificate["compatibility"]["minimal_nonfaces"],
        },
        "atom_cover": {
            "cover": certificate["compatibility"]["cover"],
            "excluded_conditions": certificate["compatibility"]["excluded_conditions"],
        },
        "description_distortion": {
            "contract": certificate["description_contract"],
            "atoms": atom_descriptions,
        },
        "residual_metadata": {
            "residuals": [
                {
                    "atom_id": row["atom_id"],
                    "residual_relation_digest": row["description"]["residual_relation_digest"],
                    "sampling_law_id": row["description"]["sampling_law_id"],
                }
                for row in certificate["atoms"]
            ],
            "sampling_laws": certificate["execution_contract"]["sampling_laws"],
        },
        "estimator_calibration": {
            "claims": estimator_claims,
            "per_atom_resources": certificate["resource_tables"]["per_atom"],
        },
        "precision_calibration": {
            "precision_scheme": semantics["precision_scheme"],
            "tensor_dtypes": [row["dtype"] for row in source_root["tensor_maps"]],
            "target_tensor": target_tensor,
        },
        "composition_proof": {
            "execution_contract": certificate["execution_contract"],
            "trace_contract": certificate["trace_contract"],
            "resource_tables": certificate["resource_tables"],
        },
        "kernel_plan": {
            "case_ids": [row["case_id"] for row in inventory],
            "dispatch_digest": OPERATOR_DISPATCH["dispatch_digest"],
            "resource_limits": certificate["resources"],
        },
        "physical_schedule": {
            "page_layout": page_layout,
            "profile": profile,
            "physical_conversion": certificate["physical_conversion"],
        },
        "quality_proof": certificate,
        "protocol_capabilities": {
            "certificate_id": certificate["certificate_id"],
            "operator_inventory": inventory,
            "semantic_manifest": {
                "tokenizer_digest": semantics["tokenizer_digest"],
                "template_digest": semantics["template_digest"],
                "operator_set": semantics["operator_set"],
            },
        },
    }
    products["cache_key"] = {
        "input_names": list(_INVALIDATION_INPUTS),
        "artifact_outputs": {
            name: _digest(products[name]) for name in _DERIVATION_ORDER[:-1]
        },
    }
    return products


def _derivation_document(
    inputs: dict[str, object],
    products: dict[str, object],
    previous: dict | None = None,
) -> tuple[dict, tuple[str, ...], tuple[str, ...]]:
    input_digests = {name: _digest(inputs[name]) for name in _INVALIDATION_INPUTS}
    previous_rows = (
        {row["artifact"]: row for row in previous["artifacts"]}
        if previous is not None
        else {}
    )
    records = {}
    rows = []
    authored = []
    carried = []
    for name in _DERIVATION_ORDER:
        dependencies = _DERIVATION_DEPENDENCIES[name]
        vector = []
        for dependency in dependencies:
            kind, dependency_name = dependency.split(":", 1)
            dependency_digest = (
                input_digests[dependency_name]
                if kind == "input"
                else records[dependency_name]["artifact_digest"]
            )
            vector.append({"dependency": dependency, "digest": dependency_digest})
        prior = previous_rows.get(name)
        if prior is not None and prior["dependencies"] == vector:
            row = prior
            carried.append(name)
        else:
            row = {
                "artifact": name,
                "dependencies": vector,
                "complete_input_digest": _digest(vector),
                "output_digest": _digest(products[name]),
            }
            row["artifact_digest"] = _digest(row)
            authored.append(name)
        records[name] = row
        rows.append(row)
    edges = [
        {"artifact": name, "dependencies": list(_DERIVATION_DEPENDENCIES[name])}
        for name in _DERIVATION_ORDER
    ]
    document = {
        "version": _DERIVATION_VERSION,
        "derivation_id": _digest("unsealed-derivation"),
        "input_digests": input_digests,
        "edges": edges,
        "artifacts": rows,
    }
    document["derivation_id"] = _digest({
        name: value for name, value in document.items() if name != "derivation_id"
    })
    return document, tuple(authored), tuple(carried)


def _invalidation_audit(
    previous: dict | None,
    current: dict,
    authored: tuple[str, ...],
    carried: tuple[str, ...],
) -> tuple[tuple[str, ...], ...]:
    if previous is None:
        expected = tuple(_DERIVATION_ORDER)
        if authored != expected or carried:
            _reject(
                "CAPABILITY_MISMATCH",
                current["derivation_id"],
                "a clean derivation did not author every artifact exactly once",
                "Q27/Q61/Q75: exact transitive invalidation and unchanged-input reuse",
            )
        return tuple(_INVALIDATION_INPUTS), expected, authored, carried
    changed = tuple(
        name for name in _INVALIDATION_INPUTS
        if previous["input_digests"][name] != current["input_digests"][name]
    )
    invalidated = []
    changed_set = set(changed)
    invalidated_set = set()
    for name in _DERIVATION_ORDER:
        dependencies = _DERIVATION_DEPENDENCIES[name]
        if any(
            (dependency.startswith("input:") and dependency[6:] in changed_set)
            or (dependency.startswith("artifact:") and dependency[9:] in invalidated_set)
            for dependency in dependencies
        ):
            invalidated.append(name)
            invalidated_set.add(name)
    previous_rows = {row["artifact"]: row for row in previous["artifacts"]}
    current_rows = {row["artifact"]: row for row in current["artifacts"]}
    reused = tuple(name for name in _DERIVATION_ORDER if name not in invalidated_set)
    if authored != tuple(invalidated) or carried != reused:
        _reject(
            "CAPABILITY_MISMATCH",
            current["derivation_id"],
            "artifact authorship differs from the exact Q27 dependency closure",
            "Q27/Q61/Q75: exact transitive invalidation and unchanged-input reuse",
        )
    for name in reused:
        if previous_rows[name] != current_rows[name]:
            _reject(
                "CAPABILITY_MISMATCH",
                name,
                "an artifact changed outside its declared Q27 dependency closure",
                "Q27/Q61/Q75: exact transitive invalidation and unchanged-input reuse",
            )
    return changed, tuple(invalidated), authored, carried


def _execution_plan(
    source_root: dict,
    source_root_digest: str,
    certificate: dict,
    profile: dict,
    contribution: dict,
    inventory: list[dict],
    prior_failures: list[dict],
    cartridge: str | Path,
    invalidation_graph_digest: str | None = None,
) -> dict:
    if invalidation_graph_digest is not None:
        _exact_digest(
            invalidation_graph_digest,
            source_root_digest,
            "persisted invalidation derivation digest",
        )
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
        "invalidation_graph_digest": invalidation_graph_digest or _digest({
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


def _hardware_reject(code: str, object_id: str, detail: str) -> None:
    raise CassetteError(code, object_id, _HARDWARE_INVARIANT, "terminal", detail)


def _hardware_record(
    value: object, fields: frozenset[str] | set[str], object_id: str, label: str
) -> dict:
    if not isinstance(value, dict) or set(value) != fields:
        observed = sorted(value) if isinstance(value, dict) else type(value).__name__
        _hardware_reject(
            "INVALID_REQUEST",
            object_id,
            f"{label} requires exactly {sorted(fields)}; received {observed}",
        )
    return value


def _hardware_record_with_descriptions(
    value: object,
    required_fields: frozenset[str],
    object_id: str,
    label: str,
) -> dict:
    """Accept required measured facts plus optional descriptive evidence facts."""

    allowed_fields = required_fields | _MEASURED_PROFILE_DESCRIPTIVE_FIELDS
    if (
        not isinstance(value, dict)
        or not required_fields <= set(value)
        or not set(value) <= allowed_fields
    ):
        observed = sorted(value) if isinstance(value, dict) else type(value).__name__
        _hardware_reject(
            "INVALID_REQUEST",
            object_id,
            f"{label} requires {sorted(required_fields)} and permits only "
            f"{sorted(_MEASURED_PROFILE_DESCRIPTIVE_FIELDS)} as descriptions; received {observed}",
        )
    return value


def _hardware_items(
    value: object, object_id: str, label: str, *, empty: bool = False
) -> list:
    if not isinstance(value, list) or len(value) > _MAX_ITEMS or (not empty and not value):
        _hardware_reject(
            "INVALID_REQUEST",
            object_id,
            f"{label} requires a bounded {'possibly empty' if empty else 'nonempty'} list",
        )
    return value


def _hardware_identifier(value: object, object_id: str, label: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
        _hardware_reject("INVALID_REQUEST", object_id, f"{label} is not a canonical identifier")
    return value


def _hardware_description(value: object, object_id: str, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > 256:
        _hardware_reject("INVALID_REQUEST", object_id, f"{label} is not bounded descriptive text")
    return value


def _hardware_digest(value: object, object_id: str, label: str) -> str:
    if not isinstance(value, str) or _DIGEST.fullmatch(value) is None:
        _hardware_reject("INVALID_REQUEST", object_id, f"{label} is not one canonical digest")
    return value


def _hardware_u64(value: object, object_id: str, label: str) -> int:
    if type(value) is not int or not 0 <= value <= _MAX_U64:
        _hardware_reject("INVALID_REQUEST", object_id, f"{label} is not an unsigned 64-bit integer")
    return value


def _hardware_identifiers(value: object, object_id: str, label: str) -> list[str]:
    result = [
        _hardware_identifier(item, object_id, label)
        for item in _hardware_items(value, object_id, label, empty=True)
    ]
    if result != sorted(set(result)):
        _hardware_reject("INVALID_REQUEST", object_id, f"{label} must be unique and sorted")
    return result


def _hardware_sum(values, object_id: str, label: str) -> int:
    total = sum(values)
    if total > _MAX_U64:
        _hardware_reject("CAPABILITY_MISMATCH", object_id, f"{label} exceeds unsigned 64-bit accounting")
    return total


def _hardware_io_latency(
    byte_count: int,
    read_count: int,
    bandwidth: int,
    latency_ns: int,
    queue_depth: int,
    object_id: str,
) -> int:
    if bandwidth == 0 or queue_depth == 0:
        _hardware_reject("CAPABILITY_MISMATCH", object_id, "hardware plan requires positive bandwidth and queue depth")
    transfer_ns = (byte_count * 1_000_000_000 + bandwidth - 1) // bandwidth
    latency_waves = (read_count + queue_depth - 1) // queue_depth
    return _hardware_sum(
        (transfer_ns, latency_waves * latency_ns), object_id, "predicted I/O latency"
    )


def _hardware_pages(locations, base_plan: dict, object_id: str) -> tuple[list[dict], int]:
    pages = sorted(
        [
            {
                "page_digest": _hardware_digest(
                    location.page_digest, object_id, "page digest"
                ),
                "length": _hardware_u64(location.length, object_id, "page length"),
            }
            for location in locations
        ],
        key=lambda row: row["page_digest"],
    )
    if not pages or any(row["length"] == 0 for row in pages):
        _hardware_reject("ROOT_INVALID", object_id, "hardware plans require nonempty canonical pages")
    if len({row["page_digest"] for row in pages}) != len(pages):
        _hardware_reject("ROOT_INVALID", object_id, "hardware page catalog repeats a page identity")
    if _digest(pages) != base_plan["page_map_digest"]:
        _hardware_reject("CAPABILITY_MISMATCH", object_id, "hardware pages differ from the compiled page map")
    return pages, _hardware_sum(
        (row["length"] for row in pages), object_id, "executable page bytes"
    )


def _profile_predicate(
    value: object,
    object_id: str,
    required_case_ids: list[str],
    required_apple_features: list[str],
) -> dict:
    source = _hardware_record(value, _PROFILE_SPEC_FIELDS, object_id, "profile predicate")
    result = {
        "apple_class": _hardware_identifier(source["apple_class"], object_id, "Apple class"),
        "request_class": _hardware_identifier(source["request_class"], object_id, "request class"),
        "operation_plan_profile_digest": _hardware_digest(
            source["operation_plan_profile_digest"], object_id, "operation-plan profile digest"
        ),
        **{
            name: _hardware_u64(source[name], object_id, name)
            for name in (
                "minimum_unified_memory_bytes",
                "minimum_recommended_working_set_bytes",
                "minimum_sustained_read_bytes_per_second",
                "maximum_p99_read_latency_ns",
            )
        },
        "required_operator_case_ids": required_case_ids,
        "required_apple_features": required_apple_features,
        "requires_writable_storage": source["requires_writable_storage"],
    }
    if type(result["requires_writable_storage"]) is not bool:
        _hardware_reject("INVALID_REQUEST", object_id, "requires_writable_storage must be boolean")
    if result["minimum_sustained_read_bytes_per_second"] == 0:
        _hardware_reject("INVALID_REQUEST", object_id, "minimum sustained read bandwidth must be positive")
    if result["minimum_recommended_working_set_bytes"] > result["minimum_unified_memory_bytes"]:
        _hardware_reject("CAPABILITY_MISMATCH", object_id, "recommended working set exceeds unified memory")
    return result


def _fresh_read_budget(certificate: dict, object_id: str) -> tuple[dict, int]:
    resources = certificate["resources"]
    conversions = {
        row["operation_id"]: row
        for row in certificate["physical_conversion"]["conversion_rows"]
    }
    trace = certificate["resource_tables"]["per_trace_step"]
    try:
        used = [conversions[row["operation_id"]] for row in trace]
    except KeyError:
        _hardware_reject("CAPABILITY_MISMATCH", object_id, "trace names an operation without a physical conversion")
    physical_bytes = _hardware_sum(
        (row["bytes"] for row in used), object_id, "fresh physical bytes"
    )
    page_reads = _hardware_sum(
        (row["page_reads"] for row in used), object_id, "fresh physical page reads"
    )
    certified_latency = _hardware_sum(
        (row["latency_ns_peak"] for row in used), object_id, "fresh certified latency"
    )
    return {
        "mode": "EXACT" if resources["fresh_samples_total"] == 0 else "FRESH",
        "samples_peak": resources["fresh_samples_max"],
        "samples_total": resources["fresh_samples_total"],
        "traffic_peak": resources["fresh_traffic_max"],
        "traffic_total": resources["fresh_traffic_total"],
        "traffic_unit": resources["fresh_traffic_unit"],
        "physical_bytes_peak": max(row["bytes"] for row in used),
        "physical_bytes_total": physical_bytes,
        "physical_page_reads_peak": max(row["page_reads"] for row in used),
        "physical_page_reads_total": page_reads,
        "certified_latency_ns_total": certified_latency,
    }, max(row["memory_bytes_peak"] for row in used)


def _hardware_plan(
    value: object,
    base_plan: dict,
    certificate: dict,
    locations,
    index_bytes: int,
) -> tuple[dict, int]:
    spec = _hardware_record(value, _HARDWARE_SPEC_FIELDS, certificate["certificate_id"], "hardware plan specification")
    name = _hardware_identifier(spec["plan_name"], certificate["certificate_id"], "hardware plan name")
    used_case_ids = sorted({
        row["operator_case_id"] for row in certificate["execution_contract"]["operations"]
    })
    apple_features = sorted(base_plan["dispatch"]["apple_features"])
    predicate = _profile_predicate(spec["profile_predicate"], name, used_case_ids, apple_features)
    pages, executable_bytes = _hardware_pages(locations, base_plan, name)
    by_digest = {row["page_digest"]: row["length"] for row in pages}
    physical = {location.page_digest: location for location in locations}
    page_order = [
        _hardware_digest(item, name, "ordered page digest")
        for item in _hardware_items(spec["page_order"], name, "page order")
    ]
    if len(page_order) != len(set(page_order)) or set(page_order) != set(by_digest):
        _hardware_reject("CAPABILITY_MISMATCH", name, "page order must reference every compiled page exactly once")
    group_values = _hardware_items(spec["read_groups"], name, "read groups")
    groups = []
    for ordinal, group_value in enumerate(group_values):
        page_digests = [
            _hardware_digest(item, name, "read-group page digest")
            for item in _hardware_items(group_value, name, "read-group pages")
        ]
        try:
            group_bytes = _hardware_sum(
                (by_digest[page_digest] for page_digest in page_digests), name, "read-group bytes"
            )
            group_locations = [physical[page_digest] for page_digest in page_digests]
        except KeyError:
            _hardware_reject("CAPABILITY_MISMATCH", name, "read group names a foreign page")
        if any(
            current.segment_id != following.segment_id
            or current.offset + current.length != following.offset
            for current, following in zip(group_locations, group_locations[1:])
        ):
            _hardware_reject("CAPABILITY_MISMATCH", name, "read group is not one contiguous physical range")
        if group_bytes > _MAX_READ_GROUP_BYTES:
            _hardware_reject("CAPABILITY_MISMATCH", name, "read group exceeds the 32 MiB coalescing bound")
        groups.append({"ordinal": ordinal, "page_digests": page_digests, "bytes": group_bytes})
    if [page for group in groups for page in group["page_digests"]] != page_order:
        _hardware_reject("CAPABILITY_MISMATCH", name, "read groups must partition the declared page order")
    queue_depth = _hardware_u64(spec["io_queue_depth"], name, "I/O queue depth")
    if not 1 <= queue_depth <= 64:
        _hardware_reject("INVALID_REQUEST", name, "I/O queue depth must lie between 1 and 64")
    prefetch = _hardware_record(spec["prefetch_policy"], _PREFETCH_FIELDS, name, "prefetch policy")
    prefetch = {
        "kind": _hardware_identifier(prefetch["kind"], name, "prefetch kind"),
        "lookahead_pages": _hardware_u64(prefetch["lookahead_pages"], name, "prefetch lookahead"),
    }
    if (
        prefetch["kind"] not in {"NONE", "ORDERED"}
        or (prefetch["kind"] == "NONE") != (prefetch["lookahead_pages"] == 0)
        or prefetch["lookahead_pages"] > len(page_order)
    ):
        _hardware_reject("INVALID_REQUEST", name, "prefetch policy and lookahead disagree")
    resources = certificate["resources"]
    fresh, fresh_memory_peak = _fresh_read_budget(certificate, name)
    description = {
        "peak_bytes": resources["description_bytes_peak"],
        "total_bytes": resources["description_bytes_total"],
    }
    metadata = {
        "peak_bytes": resources["metadata_bytes_peak"],
        "total_bytes": resources["metadata_bytes_total"],
    }
    prefetch_bytes_peak = max(
        (
            _hardware_sum(
                (by_digest[page] for page in page_order[index:index + prefetch["lookahead_pages"]]),
                name,
                "prefetch bytes",
            )
            for index in range(len(page_order))
        ),
        default=0,
    ) if prefetch["lookahead_pages"] else 0
    group_memory = _hardware_sum(
        (
            max(group["bytes"] for group in groups),
            prefetch_bytes_peak,
            description["peak_bytes"],
            metadata["peak_bytes"],
            index_bytes,
        ),
        name,
        "resident group, prefetch, index, description, and metadata bytes",
    )
    working_set = max(group_memory, fresh_memory_peak)
    if predicate["minimum_recommended_working_set_bytes"] < working_set:
        _hardware_reject("CAPABILITY_MISMATCH", name, "profile predicate cannot hold the certified working set")
    setup_latency = _hardware_io_latency(
        executable_bytes,
        len(groups),
        predicate["minimum_sustained_read_bytes_per_second"],
        predicate["maximum_p99_read_latency_ns"],
        queue_depth,
        name,
    )
    fresh_io_latency = _hardware_io_latency(
        fresh["physical_bytes_total"],
        fresh["physical_page_reads_total"],
        predicate["minimum_sustained_read_bytes_per_second"],
        predicate["maximum_p99_read_latency_ns"],
        queue_depth,
        name,
    )
    fresh_latency = max(fresh_io_latency, fresh["certified_latency_ns_total"])
    plan = {
        "plan_version": HARDWARE_PLAN_VERSION,
        "plan_id": _digest("unsealed-hardware-plan"),
        "plan_name": name,
        "profile_predicate": predicate,
        "q19_certificate_digest": certificate["certificate_id"],
        "condition_selector": certificate["compatibility"]["cover"],
        "atom_refs": [
            {"atom_id": atom["atom_id"], "description_digest": _digest(atom["description"])}
            for atom in certificate["atoms"]
        ],
        "description_budget": description,
        "metadata_budget": metadata,
        "fresh_sample_or_exact_read_budget": fresh,
        "error_risk_horizon": {
            "eta_rep": resources["eta_rep"],
            "epsilon_exec": resources["epsilon_exec"],
            "delta_exec_total": resources["delta_exec_total"],
            "horizon": resources["horizon"],
        },
        "page_order": page_order,
        "read_groups": groups,
        "precision_budget": {
            "precision_planes_digest": base_plan["precision_planes_digest"],
            "page_payload_bytes": executable_bytes,
        },
        "kernel_dispatch": {
            "dispatch_digest": base_plan["dispatch"]["dispatch_digest"],
            "case_ids": used_case_ids,
            "apple_features": apple_features,
        },
        "concurrency": {"io_queue_depth": queue_depth},
        "prefetch_policy": prefetch,
        "memory_schedule": {
            "page_group_bytes_peak": max(group["bytes"] for group in groups),
            "prefetch_bytes_peak": prefetch_bytes_peak,
            "index_bytes": index_bytes,
            "description_bytes_peak": description["peak_bytes"],
            "metadata_bytes_peak": metadata["peak_bytes"],
            "fresh_bytes_peak": fresh["physical_bytes_peak"],
            "working_set_bytes_peak": working_set,
        },
        "expected_metrics": {
            "page_read_bytes": executable_bytes,
            "index_bytes": _hardware_u64(index_bytes, name, "page-index bytes"),
            "read_group_count": len(groups),
            "fresh_read_bytes_total": fresh["physical_bytes_total"],
            "fresh_page_reads_total": fresh["physical_page_reads_total"],
            "predicted_setup_latency_ns": setup_latency,
            "predicted_fresh_latency_ns": fresh_latency,
            "predicted_total_latency_ns": _hardware_sum(
                (setup_latency, fresh_latency), name, "predicted total latency"
            ),
        },
        "weight_payload_bytes": 0,
    }
    plan["plan_id"] = _digest({field: plan[field] for field in plan if field != "plan_id"})
    defects = validate("hardware_plan", plan)
    if defects:
        _hardware_reject("INVALID_REQUEST", name, "; ".join(defects[:8]))
    return plan, executable_bytes


def _hardware_spec_from_plan(value: object, object_id: str) -> dict:
    plan = _hardware_record(value, _HARDWARE_PLAN_FIELDS, object_id, "hardware plan")
    predicate = _hardware_record(
        plan["profile_predicate"], _PROFILE_PREDICATE_FIELDS, object_id, "stored profile predicate"
    )
    groups = [
        _hardware_record(group, _READ_GROUP_FIELDS, object_id, "stored read group")["page_digests"]
        for group in _hardware_items(plan["read_groups"], object_id, "stored read groups")
    ]
    concurrency = _hardware_record(
        plan["concurrency"], {"io_queue_depth"}, object_id, "stored concurrency"
    )
    return {
        "plan_name": plan["plan_name"],
        "profile_predicate": {name: predicate[name] for name in _PROFILE_SPEC_FIELDS},
        "page_order": plan["page_order"],
        "read_groups": groups,
        "io_queue_depth": concurrency["io_queue_depth"],
        "prefetch_policy": plan["prefetch_policy"],
    }


def _hardware_catalog(
    base_bundle: dict,
    locations,
    index_bytes: int,
    specifications: object,
) -> dict:
    certificate = base_bundle["certificate"]
    base_plan = base_bundle["execution_plan"]
    plans_and_sizes = [
        _hardware_plan(spec, base_plan, certificate, locations, index_bytes)
        for spec in _hardware_items(specifications, certificate["certificate_id"], "hardware plans")
    ]
    plans = sorted((item[0] for item in plans_and_sizes), key=lambda plan: plan["plan_name"])
    if len({plan["plan_name"] for plan in plans}) != len(plans):
        _hardware_reject("INVALID_REQUEST", certificate["certificate_id"], "hardware plan names must be unique")
    executable_bytes = plans_and_sizes[0][1]
    if any(size != executable_bytes for _, size in plans_and_sizes):
        _hardware_reject("CAPABILITY_MISMATCH", certificate["certificate_id"], "hardware plans disagree on executable capacity")
    catalog = {
        "version": HARDWARE_PLAN_CATALOG_VERSION,
        "catalog_id": _digest("unsealed-hardware-catalog"),
        "q19_certificate_digest": certificate["certificate_id"],
        "base_execution_plan_id": base_plan["plan_id"],
        "plans": plans,
    }
    catalog["catalog_id"] = _digest({field: catalog[field] for field in catalog if field != "catalog_id"})
    defects = validate("hardware_plan_catalog", catalog)
    if defects:
        _hardware_reject(
            "INVALID_REQUEST", certificate["certificate_id"], "; ".join(defects[:8])
        )
    cap = min(executable_bytes // 100, _MAX_PLAN_METADATA_BYTES)
    plan_metadata_bytes = _hardware_sum(
        (len(canonical_bytes(plan)) for plan in plans),
        certificate["certificate_id"],
        "hardware plan metadata bytes",
    )
    plans_and_index_bytes = _hardware_sum(
        (len(canonical_bytes([base_bundle, catalog])), index_bytes),
        certificate["certificate_id"],
        "plans and index bytes",
    )
    if plan_metadata_bytes > cap or plans_and_index_bytes > cap:
        _hardware_reject(
            "CAPACITY_EXCEEDED",
            certificate["certificate_id"],
            f"plan metadata or plans-plus-index exceed the {cap}-byte executable-revision allowance",
        )
    return catalog


def _verified_hardware_catalog(
    value: object,
    base_bundle: dict,
    locations,
    index_bytes: int,
    object_id: str,
) -> dict:
    defects = validate("hardware_plan_catalog", value)
    if defects:
        _hardware_reject("ROOT_INVALID", object_id, "; ".join(defects[:8]))
    catalog = _hardware_record(value, _HARDWARE_CATALOG_FIELDS, object_id, "hardware plan catalog")
    plans = _hardware_items(catalog["plans"], object_id, "stored hardware plans")
    expected = _hardware_catalog(
        base_bundle,
        locations,
        index_bytes,
        [_hardware_spec_from_plan(plan, object_id) for plan in plans],
    )
    if catalog != expected:
        _hardware_reject(
            "CAPABILITY_MISMATCH",
            object_id,
            "hardware plan catalog is detached from its certificate, pages, or exact budgets",
        )
    return catalog


def _measured_hardware_profile(value: object) -> dict:
    profile = _hardware_record_with_descriptions(
        value, _MEASURED_PROFILE_FIELDS, "hardware:select", "measured hardware profile"
    )
    result = {
        "apple_class": _hardware_identifier(profile["apple_class"], "hardware:select", "Apple class"),
        "request_class": _hardware_identifier(profile["request_class"], "hardware:select", "request class"),
        "operation_plan_profile_digest": _hardware_digest(
            profile["operation_plan_profile_digest"], "hardware:select", "operation-plan profile digest"
        ),
        **{
            name: _hardware_u64(profile[name], "hardware:select", name)
            for name in (
                "unified_memory_bytes",
                "recommended_max_working_set_bytes",
                "sustained_read_bytes_per_second",
                "p99_read_latency_ns",
            )
        },
        "operator_case_ids": _hardware_identifiers(
            profile["operator_case_ids"], "hardware:select", "operator case IDs"
        ),
        "apple_features": _hardware_identifiers(
            profile["apple_features"], "hardware:select", "Apple features"
        ),
        "writable_storage": profile["writable_storage"],
    }
    if type(result["writable_storage"]) is not bool:
        _hardware_reject("INVALID_REQUEST", "hardware:select", "writable_storage must be boolean")
    if result["sustained_read_bytes_per_second"] == 0:
        _hardware_reject("INVALID_REQUEST", "hardware:select", "measured read bandwidth must be positive")
    if result["recommended_max_working_set_bytes"] > result["unified_memory_bytes"]:
        _hardware_reject("INVALID_REQUEST", "hardware:select", "recommended working set exceeds unified memory")
    for name in sorted(_MEASURED_PROFILE_DESCRIPTIVE_FIELDS & set(profile)):
        result[name] = (
            _hardware_u64(profile[name], "hardware:select", name)
            if name == "nominal_capacity_bytes"
            else _hardware_description(profile[name], "hardware:select", name)
        )
    return result


def _profile_matches(plan: dict, profile: dict) -> bool:
    predicate = plan["profile_predicate"]
    return (
        profile["apple_class"] == predicate["apple_class"]
        and profile["request_class"] == predicate["request_class"]
        and profile["operation_plan_profile_digest"] == predicate["operation_plan_profile_digest"]
        and profile["unified_memory_bytes"] >= predicate["minimum_unified_memory_bytes"]
        and profile["recommended_max_working_set_bytes"] >= predicate["minimum_recommended_working_set_bytes"]
        and profile["sustained_read_bytes_per_second"] >= predicate["minimum_sustained_read_bytes_per_second"]
        and profile["p99_read_latency_ns"] <= predicate["maximum_p99_read_latency_ns"]
        and set(profile["operator_case_ids"]) >= set(predicate["required_operator_case_ids"])
        and set(profile["apple_features"]) >= set(predicate["required_apple_features"])
        and (not predicate["requires_writable_storage"] or profile["writable_storage"])
    )


def _measured_plan_latency(plan: dict, profile: dict) -> int:
    metrics = plan["expected_metrics"]
    queue_depth = plan["concurrency"]["io_queue_depth"]
    setup = _hardware_io_latency(
        metrics["page_read_bytes"],
        metrics["read_group_count"],
        profile["sustained_read_bytes_per_second"],
        profile["p99_read_latency_ns"],
        queue_depth,
        plan["plan_id"],
    )
    fresh = plan["fresh_sample_or_exact_read_budget"]
    fresh_io = _hardware_io_latency(
        fresh["physical_bytes_total"],
        fresh["physical_page_reads_total"],
        profile["sustained_read_bytes_per_second"],
        profile["p99_read_latency_ns"],
        queue_depth,
        plan["plan_id"],
    )
    return _hardware_sum(
        (setup, max(fresh_io, fresh["certified_latency_ns_total"])),
        plan["plan_id"],
        "measured-profile predicted total latency",
    )


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


def _bundle_record(root: dict, object_id: str) -> dict:
    plans = root.get("plans")
    if not isinstance(plans, list) or len(plans) not in {1, 2} or not isinstance(plans[0], dict):
        _reject("ROOT_INVALID", object_id, "compiled root requires one preparation bundle and at most one hardware catalog")
    version = plans[0].get("version")
    fields = _BUNDLE_FIELDS if version == _VERSION else _RECOMPILE_BUNDLE_FIELDS
    if version not in {_VERSION, _RECOMPILE_VERSION}:
        _reject("ROOT_INVALID", object_id, "compiled preparation bundle version is unsupported")
    return _record(plans[0], fields, object_id, "preparation bundle")


def _semantic_record(value: object, object_id: str) -> dict:
    record = _record(
        value,
        {
            "architecture", "config_digest", "format_versions", "precision_scheme",
            "processor_digest", "template_digest", "tokenizer_digest", "operator_set",
        },
        object_id,
        "compiled semantic record",
    )
    _identifier(record["architecture"], object_id, "architecture")
    if not isinstance(record["precision_scheme"], str) or not 0 < len(record["precision_scheme"]) <= 256:
        _reject("INVALID_REQUEST", object_id, "precision scheme must be bounded text")
    for name in ("config_digest", "processor_digest", "template_digest", "tokenizer_digest"):
        _exact_digest(record[name], object_id, name)
    formats = _items(record["format_versions"], object_id, "format versions")
    normalized_formats = []
    for row in formats:
        if not isinstance(row, list) or len(row) != 2 or any(
            not isinstance(part, str) or not part or len(part) > 256 for part in row
        ):
            _reject("INVALID_REQUEST", object_id, "format versions require bounded [name, version] pairs")
        normalized_formats.append(row)
    operators = _items(record["operator_set"], object_id, "operator set")
    for operator in operators:
        _identifier(operator, object_id, "operator")
    if normalized_formats != sorted(normalized_formats) or operators != sorted(set(operators)):
        _reject("INVALID_REQUEST", object_id, "format versions and operator set must be canonical unique lists")
    return record


def _specification_record(value: object, object_id: str) -> dict:
    specification = _record(value, _SPECIFICATION_FIELDS, object_id, "recompile specification")
    _exact_digest(specification["source_root"], object_id, "source root")
    _identifier(specification["target_tensor"], object_id, "target tensor")
    for name in ("config_digest", "processor_digest", "template_digest", "tokenizer_digest"):
        _exact_digest(specification[name], object_id, name)
    _identifier(specification["architecture"], object_id, "architecture")
    if not isinstance(specification["precision_scheme"], str) or not 0 < len(specification["precision_scheme"]) <= 256:
        _reject("INVALID_REQUEST", object_id, "precision scheme must be bounded text")
    specification["operator_inventory"] = _inventory(
        specification["operator_inventory"], object_id
    )
    if not isinstance(specification["profile"], dict):
        _reject("INVALID_REQUEST", object_id, "profile must be one bounded record")
    evidence = _record(
        specification["evidence"],
        {
            "atoms", "conditions", "description_contract", "excluded_conditions",
            "execution_contract", "minimal_nonface_proofs", "observation_contract",
            "physical_conversion", "target", "trace_contract",
        },
        object_id,
        "recompile evidence",
    )
    target = _record(
        evidence["target"],
        {"field", "flattening_order", "shape", "source_shape"},
        object_id,
        "recompile target evidence",
    )
    if "source_values" in target:
        _reject("INVALID_REQUEST", object_id, "recompile target values must come only from verified tensor bytes")
    formats = _items(specification["format_versions"], object_id, "format versions")
    if any(
        not isinstance(row, list)
        or len(row) != 2
        or any(not isinstance(part, str) or not part or len(part) > 256 for part in row)
        for row in formats
    ) or formats != sorted(formats) or len(formats) != len({tuple(row) for row in formats}):
        _reject("INVALID_REQUEST", object_id, "format versions must be sorted unique bounded pairs")
    if not isinstance(specification["prior_mode_failures"], list):
        _reject("INVALID_REQUEST", object_id, "prior mode failures must be one bounded list")
    return specification


def _operation_bounds(certificate: dict) -> list[dict]:
    return [
        {
            "operation_id": row["operation_id"],
            "epsilon_exec": row["epsilon_exec"],
            "delta_exec": row["delta_exec"],
        }
        for row in certificate["execution_contract"]["operations"]
    ]


def _specification_from_bundle(cartridge: str | Path, root_digest: str, root: dict, bundle: dict) -> dict:
    source_root = load_root(cartridge, bundle["source_root"])
    material = root["provenance"]["identity_material"]
    evidence = _canonical_copy(bundle["evidence"])
    evidence["target"].pop("source_values", None)
    formats = [
        list(row) for row in material["format_versions"] if row[0] != "cassette"
    ]
    specification = {
        "source_root": bundle["source_root"],
        "target_tensor": bundle["contribution_map"]["target_tensor"],
        "evidence": evidence,
        "profile": _canonical_copy(bundle["profile"]),
        "eta_rep": bundle["certificate"]["compatibility"]["eta_rep"],
        "rank_budget": bundle["certificate"]["compatibility"]["rank_budget"],
        "operation_bounds": _operation_bounds(bundle["certificate"]),
        "operator_inventory": _canonical_copy(bundle["operator_inventory"]),
        "tensor_inventory": _canonical_copy(bundle["tensor_inventory"]),
        "prior_mode_failures": _canonical_copy(bundle["execution_plan"]["prior_mode_failures"]),
        "architecture": material["architecture"],
        "config_digest": material["config_digest"],
        "format_versions": sorted(formats),
        "precision_scheme": material["precision_scheme"],
        "processor_digest": material["processor_digest"],
        "template_digest": material["template_digest"],
        "tokenizer_digest": material["tokenizer_digest"],
    }
    if source_root["identity"] != bundle["source_identity"]:
        _reject("IDENTITY_MISMATCH", root_digest, "compiled source identity differs from its verified source root")
    return _specification_record(specification, root_digest)


def _recovery_bindings(cartridge: str | Path, root_digest: str) -> tuple[dict[str, dict], dict]:
    root = load_root(cartridge, root_digest)
    if not root["deltas"] or root["deltas"][-1]["kind"] != "certificate_recovery":
        return {}, {"kind": "NONE"}
    delta = root["deltas"][-1]
    manifest_digest = _exact_digest(
        delta["manifest_digest"], root_digest, "recovery manifest digest"
    )
    manifest_payload = read_training_page(cartridge, root_digest, manifest_digest)
    try:
        manifest = json.loads(manifest_payload, object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        _reject("ROOT_INVALID", manifest_digest, f"recovery manifest is malformed: {error}")
    if canonical_bytes(manifest) != manifest_payload:
        _reject("ROOT_INVALID", manifest_digest, "recovery manifest is not canonical JSON")
    manifest = _record(
        manifest, _TRAINING_MANIFEST_FIELDS, manifest_digest, "recovery manifest"
    )
    if (
        manifest["format"] != "cassette-training-v1"
        or manifest["tier"] != "B"
        or manifest["operation"] != "COMPILED_RECOVERY"
        or manifest["operator_cases"] != [
            "mlx.autograd_calibration_mse.f32.1_2x3_3x2_2x2_1",
            "mlx.sgd.f32.1",
        ]
        or manifest["delta_precision"] not in {"BF16", "FP32"}
        or type(manifest["step"]) is not int
        or type(manifest["total_steps"]) is not int
        or not 0 < manifest["step"] <= manifest["total_steps"] <= 4096
        or manifest["step"] != manifest["total_steps"]
        or manifest["optimizer_step"] != manifest["step"]
        or manifest["data_cursor"] != manifest["step"]
        or manifest["rng_counter"] != manifest["step"]
        or manifest["adapter_rank"] is not None
        or manifest["adapter_scale"] is not None
        or manifest["master_pages"] != []
        or not isinstance(manifest["base_pages"], list)
        or len(manifest["base_pages"]) != 1
    ):
        _reject("ROOT_INVALID", manifest_digest, "recovery manifest is incomplete or names another training tier")
    parent_root_digest = _exact_digest(
        manifest["parent_root"], manifest_digest, "recovery parent root"
    )
    parent = load_root(cartridge, parent_root_digest)
    parent_bundle = _bundle_record(parent, parent_root_digest)
    if (
        root["parents"] != [parent["identity"]]
        or manifest["parent_identity"] != parent["identity"]
        or delta["base_identity"] != parent["identity"]
        or root["plans"] != parent["plans"]
        or root["tensor_maps"] != parent["tensor_maps"]
        or root["deltas"] != [*parent["deltas"], delta]
        or manifest["parent_certificate_digest"]
        != parent_bundle["certificate"]["certificate_id"]
    ):
        _reject("IDENTITY_MISMATCH", manifest_digest, "recovery artifact is detached from its compiled parent")
    calibration_rows = manifest["calibration_pages"]
    delta_rows = manifest["delta_pages"]
    if (
        not isinstance(calibration_rows, list)
        or not isinstance(delta_rows, list)
        or [row.get("kind") for row in calibration_rows if isinstance(row, dict)]
        != list(_RECOVERY_KINDS)
        or [row.get("parameter_id") for row in delta_rows if isinstance(row, dict)]
        != [f"recovery.{kind}" for kind in _RECOVERY_KINDS]
        or any(set(row) != {"kind", "page_digest"} for row in calibration_rows)
        or any(set(row) != {"parameter_id", "page_digest"} for row in delta_rows)
    ):
        _reject("ROOT_INVALID", manifest_digest, "recovery page catalogs do not cover the six canonical kinds")
    states = _record(
        manifest["state_pages"], {"optimizer", "rng", "journal"}, manifest_digest, "training state pages"
    )
    objectives = manifest["objective_pages"]
    traces = manifest["trace_pages"]
    if (
        not isinstance(objectives, list)
        or len(objectives) != manifest["total_steps"]
        or any(
            not isinstance(row, dict)
            or set(row) != {"step", "page_digest"}
            or row["step"] != index
            for index, row in enumerate(objectives)
        )
        or not isinstance(traces, list)
        or len(traces) != manifest["step"]
    ):
        _reject("ROOT_INVALID", manifest_digest, "recovery objective or trace catalog is malformed")
    ordered = [
        manifest_digest,
        *[row["page_digest"] for row in delta_rows],
        *[row.get("page_digest") for row in objectives if isinstance(row, dict)],
        *[row["page_digest"] for row in calibration_rows],
        *[states[name] for name in ("optimizer", "rng", "journal")],
        *traces,
    ]
    if (
        any(not isinstance(value, str) for value in ordered)
        or ordered != delta["ordered_page_digests"]
        or len(ordered) != len(set(ordered))
    ):
        _reject("ROOT_INVALID", manifest_digest, "recovery root does not bind the complete ordered training artifact")
    bindings = {}
    expected_dtype = "float32" if manifest["delta_precision"] == "FP32" else "bfloat16"
    expected_bytes = 4 if expected_dtype == "float32" else 2
    for kind, calibration_row, delta_row in zip(
        _RECOVERY_KINDS, calibration_rows, delta_rows, strict=True
    ):
        calibration_digest = _exact_digest(
            calibration_row["page_digest"], manifest_digest, f"{kind} calibration page"
        )
        calibration_payload = read_training_page(cartridge, root_digest, calibration_digest)
        try:
            calibration_page = json.loads(calibration_payload, object_pairs_hook=_unique_object)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            _reject("ROOT_INVALID", calibration_digest, f"calibration page is malformed: {error}")
        if canonical_bytes(calibration_page) != calibration_payload:
            _reject("ROOT_INVALID", calibration_digest, "calibration page is not canonical JSON")
        envelope = _record(
            calibration_page, {"format", "role", "record"}, calibration_digest, "calibration page"
        )
        record = _record(
            envelope["record"],
            {"kind", "input_digest", "output_digest", "sample_count", "loss"},
            calibration_digest,
            "calibration record",
        )
        if (
            envelope["format"] != "cassette-training-v1"
            or envelope["role"] != "calibration"
            or record["kind"] != kind
            or type(record["sample_count"]) is not int
            or record["sample_count"] < 32768
            or record["input_digest"] == record["output_digest"]
            or not isinstance(record["loss"], str)
            or not 0 < len(record["loss"]) <= 64
        ):
            _reject("ROOT_INVALID", calibration_digest, "calibration record is incomplete, undersampled, or unchanged")
        try:
            loss = Fraction(record["loss"])
        except (TypeError, ValueError, ZeroDivisionError):
            _reject("ROOT_INVALID", calibration_digest, "calibration loss is not finite nonnegative decimal text")
        if loss < 0:
            _reject("ROOT_INVALID", calibration_digest, "calibration loss is not finite nonnegative decimal text")
        _exact_digest(record["input_digest"], calibration_digest, "calibration input digest")
        _exact_digest(record["output_digest"], calibration_digest, "calibration output digest")
        delta_digest = _exact_digest(
            delta_row["page_digest"], manifest_digest, f"{kind} recovery delta"
        )
        delta_payload = read_training_page(cartridge, root_digest, delta_digest)
        try:
            delta_page = json.loads(delta_payload, object_pairs_hook=_unique_object)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            _reject("ROOT_INVALID", delta_digest, f"recovery delta page is malformed: {error}")
        if canonical_bytes(delta_page) != delta_payload:
            _reject("ROOT_INVALID", delta_digest, "recovery delta page is not canonical JSON")
        delta_page = _record(
            delta_page,
            {"format", "role", "tensor_id", "dtype", "shape", "payload_hex"},
            delta_digest,
            "recovery delta page",
        )
        payload_hex = delta_page["payload_hex"]
        if (
            not isinstance(payload_hex, str)
            or len(payload_hex) != expected_bytes * 2
            or any(character not in "0123456789abcdef" for character in payload_hex)
        ):
            _reject("ROOT_INVALID", delta_digest, "recovery delta payload is not canonical hexadecimal")
        try:
            numeric = bytes.fromhex(payload_hex)
        except ValueError:
            _reject("ROOT_INVALID", delta_digest, "recovery delta payload is not canonical hexadecimal")
        if (
            delta_page["format"] != "cassette-training-tensor-v1"
            or delta_page["role"] != "certificate_recovery"
            or delta_page["tensor_id"] != f"recovery.{kind}"
            or delta_page["dtype"] != expected_dtype
            or delta_page["shape"] != [1]
            or len(numeric) != expected_bytes
        ):
            _reject("ROOT_INVALID", delta_digest, "recovery delta page changed role, precision, shape, or parameter")
        value = (
            struct.unpack("<f", numeric)[0]
            if expected_dtype == "float32"
            else struct.unpack("<f", struct.pack("<I", struct.unpack("<H", numeric)[0] << 16))[0]
        )
        if not math.isfinite(value):
            _reject("GRADIENT_INVALID", delta_digest, "recovery delta is not finite")
        axis = _RECOVERY_INPUTS[kind]
        bindings[axis] = {
            "kind": kind,
            "calibration_page_digest": calibration_digest,
            "delta_page_digest": delta_digest,
            "record": record,
        }
    summary = {
        "kind": "COMPILED_RECOVERY",
        "manifest_digest": manifest_digest,
        "parent_root": parent_root_digest,
        "parent_certificate_digest": manifest["parent_certificate_digest"],
        "bindings": [bindings[_RECOVERY_INPUTS[kind]] for kind in _RECOVERY_KINDS],
    }
    return bindings, summary


def _semantic_from_specification(specification: dict) -> dict:
    return _semantic_record({
        "architecture": specification["architecture"],
        "config_digest": specification["config_digest"],
        "format_versions": specification["format_versions"],
        "precision_scheme": specification["precision_scheme"],
        "processor_digest": specification["processor_digest"],
        "template_digest": specification["template_digest"],
        "tokenizer_digest": specification["tokenizer_digest"],
        "operator_set": sorted({row["operator"] for row in specification["operator_inventory"]}),
    }, specification["source_root"])


def _proof_from_specification(
    cartridge: str | Path,
    specification: dict,
    previous_derivation: dict | None = None,
) -> tuple[
    dict, dict, dict, list[dict], dict, dict, dict, dict,
    tuple[str, ...], tuple[str, ...],
]:
    source_root_digest = specification["source_root"]
    source_root = load_root(cartridge, source_root_digest)
    values, shape = _decode_tensor(
        source_root, cartridge, source_root_digest, specification["target_tensor"]
    )
    evidence = _canonical_copy(specification["evidence"])
    if evidence["target"]["source_shape"] != shape:
        _reject("CAPABILITY_MISMATCH", specification["target_tensor"], "recompile target shape differs from verified tensor bytes")
    evidence["target"]["source_values"] = values
    certificate = _certificate(
        evidence,
        specification["eta_rep"],
        specification["rank_budget"],
        specification["operation_bounds"],
    )
    inventory = specification["operator_inventory"]
    tensor_inventory = _tensor_inventory(
        specification["tensor_inventory"], source_root, source_root_digest
    )
    contribution = _contribution_map(
        source_root,
        source_root_digest,
        certificate,
        specification["target_tensor"],
        inventory,
        tensor_inventory,
    )
    semantics = _semantic_from_specification(specification)
    recovery_bindings, recovery = _recovery_bindings(cartridge, source_root_digest)
    plain_inputs = _axis_materials(
        source_root,
        specification["target_tensor"],
        evidence,
        specification["profile"],
        inventory,
        semantics,
        specification,
        {},
    )
    for axis, binding in recovery_bindings.items():
        if binding["record"]["output_digest"] != _digest(plain_inputs[axis]):
            _reject(
                "CAPABILITY_MISMATCH",
                binding["calibration_page_digest"],
                f"{binding['kind']} calibration output does not name the recovered Q19 input",
                "Q70/Q75: committed recovery evidence regenerates its exact invalidated witness",
            )
    inputs = _axis_materials(
        source_root,
        specification["target_tensor"],
        evidence,
        specification["profile"],
        inventory,
        semantics,
        specification,
        recovery_bindings,
    )
    products = _derivation_products(
        source_root,
        specification["target_tensor"],
        evidence,
        certificate,
        specification["profile"],
        inventory,
        tensor_inventory,
        semantics,
    )
    derivation, authored, carried = _derivation_document(
        inputs, products, previous_derivation
    )
    return (
        source_root,
        evidence,
        certificate,
        tensor_inventory,
        contribution,
        semantics,
        derivation,
        recovery,
        authored,
        carried,
    )


def _derivation_from_bundle(
    cartridge: str | Path, root_digest: str, root: dict, bundle: dict
) -> tuple[dict, dict]:
    specification = _specification_from_bundle(
        cartridge, root_digest, root, bundle
    )
    (
        _, _, _, _, _, _, derivation, recovery, _, _,
    ) = _proof_from_specification(cartridge, specification)
    if bundle["version"] == _RECOMPILE_VERSION:
        if bundle["derivation"] != derivation or bundle["recovery"] != recovery:
            _reject(
                "CAPABILITY_MISMATCH",
                root_digest,
                "persisted derivation or recovery binding differs from clean recomputation",
                "Q27/Q61/Q70/Q75: clean derivation equals the persisted incremental result",
            )
    return derivation, specification


def _verified_compiled_bundle(
    cartridge: str | Path, root_digest: str
) -> tuple[dict, dict]:
    root = load_root(cartridge, root_digest)
    bundle = _bundle_record(root, root_digest)
    _verify_bundle_structure(
        cartridge,
        root_digest,
        bundle["source_identity"],
        bundle["preparation_plan_digest"],
    )
    return root, bundle


def _recompiled_material(source_root: dict, specification: dict, transform_digest: str) -> IdentityTuple:
    provenance = source_root["provenance"]
    source = provenance["identity_material"]
    formats = tuple(
        tuple(row) for row in specification["format_versions"] if row[0] != "cassette"
    ) + (("cassette", _RECOMPILE_VERSION),)
    return IdentityTuple(
        revision_kind="executable",
        source_kind=source["source_kind"],
        source_alias=provenance["source_alias"],
        canonical_locator=source["locator"],
        requested_revision=provenance["requested_revision"],
        immutable_revision=source["immutable_revision"],
        artifacts=tuple(ArtifactIdentity(**row) for row in source["artifacts"]),
        format_versions=formats,
        tensor_index_digest=source["tensor_index_digest"],
        config_digest=specification["config_digest"],
        architecture=specification["architecture"],
        operator_set=tuple(sorted({row["operator"] for row in specification["operator_inventory"]})),
        tokenizer_digest=specification["tokenizer_digest"],
        processor_digest=specification["processor_digest"],
        template_digest=specification["template_digest"],
        precision_scheme=specification["precision_scheme"],
        license_digest=source["license_digest"],
        parent_ids=(source_root["identity"],),
        transform_manifest_digest=transform_digest,
    )


def _recompile_revision(
    cartridge: str | Path,
    specification_value: object,
    previous_root_digest: str | None,
    require_recovery: bool,
    operation_id: str,
    capacity_coordinator: CapacityCoordinator,
) -> RecompiledRevision:
    specification = _specification_record(
        _canonical_copy(specification_value), "compiler:recompile"
    )
    previous_derivation = None
    if previous_root_digest is not None:
        _exact_digest(previous_root_digest, "compiler:recompile", "previous compiled root")
        previous_root, previous_bundle = _verified_compiled_bundle(
            cartridge, previous_root_digest
        )
        previous_derivation, _ = _derivation_from_bundle(
            cartridge, previous_root_digest, previous_root, previous_bundle
        )
    (
        source_root,
        evidence,
        certificate,
        tensor_inventory,
        contribution,
        _,
        derivation,
        recovery,
        authored,
        carried,
    ) = _proof_from_specification(cartridge, specification, previous_derivation)
    if require_recovery and recovery["kind"] != "COMPILED_RECOVERY":
        _reject(
            "TRAINING_UNSUPPORTED",
            specification["source_root"],
            "certificate recovery requires one complete committed Tier-B artifact",
            "Q70/Q75: committed Tier-B recovery precedes certificate regeneration",
        )
    if not require_recovery and recovery["kind"] != "NONE":
        _reject(
            "INVALID_REQUEST",
            specification["source_root"],
            "a certificate-recovery source must use the recovery recompile operation",
        )
    changed, invalidated, recomputed, reused = _invalidation_audit(
        previous_derivation, derivation, authored, carried
    )
    if require_recovery and previous_derivation is not None:
        expected_changes = tuple(
            name for name in _INVALIDATION_INPUTS
            if name in set(_RECOVERY_INPUTS.values())
        )
        if changed != expected_changes:
            _reject(
                "CAPABILITY_MISMATCH",
                specification["source_root"],
                f"Tier-B recovery changed {list(changed)} instead of {list(expected_changes)}",
                "Q70/Q75: recovery changes only its six committed certificate inputs",
            )
    plan = _execution_plan(
        source_root,
        specification["source_root"],
        certificate,
        specification["profile"],
        contribution,
        specification["operator_inventory"],
        specification["prior_mode_failures"],
        cartridge,
        derivation["derivation_id"],
    )
    plan_digest = _digest({
        "version": _RECOMPILE_VERSION,
        "specification": specification,
    })
    proof = {
        "operator_inventory": specification["operator_inventory"],
        "tensor_inventory": tensor_inventory,
        "evidence": evidence,
        "certificate": certificate,
        "profile": specification["profile"],
        "contribution_map": contribution,
        "execution_plan": plan,
    }
    bundle = {
        "version": _RECOMPILE_VERSION,
        "source_identity": source_root["identity"],
        "source_root": specification["source_root"],
        "preparation_plan_digest": plan_digest,
        **proof,
        "extent_metrics": _extent_metrics(
            source_root,
            proof,
            sum(
                location.length
                for location in page_locations(cartridge, specification["source_root"])
            ),
        ),
        "derivation": derivation,
        "recovery": recovery,
    }
    if len(canonical_bytes(bundle)) > _MAX_RECORD_BYTES:
        _reject(
            "CONTAINMENT_REJECTED",
            specification["source_root"],
            "recompiled proof bundle exceeds the bounded four-megabyte authority",
        )
    material = _recompiled_material(source_root, specification, _digest(bundle))
    shape = derived_root_shape(
        cartridge, specification["source_root"], material, (bundle,)
    )
    candidate = derive_root(
        cartridge,
        specification["source_root"],
        material,
        (bundle,),
        capacity_controller=capacity_coordinator,
        operation_id=operation_id,
    )
    if candidate != shape["root_digest"]:
        _reject(
            "CAPABILITY_MISMATCH",
            candidate,
            "derived candidate differs from its pre-admission root and index shape",
            "Q53/Q60: exact candidate shape remains stable through durable publication",
        )
    _verify_bundle_structure(
        cartridge, candidate, source_root["identity"], plan_digest
    )
    return RecompiledRevision(
        source_root["identity"],
        plan_digest,
        candidate,
        derivation["derivation_id"],
        changed,
        invalidated,
        recomputed,
        reused,
    )


def _plan_revision(source: object, extents: object, cartridge: str | Path) -> str:
    source_record, _, manifest, tensors, _ = _preparation_inputs(source, extents, cartridge)
    return _digest(_compile_inputs(source_record, manifest, tensors))


def _prepare_revision(
    source: object,
    extents: object,
    cartridge: str | Path,
    expected_plan_digest: str,
    capacity_coordinator: CapacityCoordinator,
    operation_id: str,
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
        source_root_digest = adopt_safetensors(
            descriptors,
            cartridge,
            source_material,
            capacity_controller=capacity_coordinator,
            operation_id=operation_id,
        )
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
    candidate = derive_root(
        cartridge,
        source_root_digest,
        compiled_material,
        (bundle,),
        capacity_controller=capacity_coordinator,
        operation_id=operation_id,
    )
    _verify_bundle_structure(
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


def _verify_bundle_structure(
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
    bundle = _bundle_record(root, root_digest)
    if len(canonical_bytes(bundle)) > _MAX_RECORD_BYTES:
        _reject("ROOT_INVALID", root_digest, "compiled proof bundle exceeds its bounded authority")
    if (
        bundle["source_identity"] != source_identity
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
    graph_digest = None
    if bundle["version"] == _VERSION:
        provenance = source_root["provenance"]
        material = provenance["identity_material"]
        texts = [
            container["metadata"][_MANIFEST_KEY]
            for container in provenance["containers"]
            if _MANIFEST_KEY in container["metadata"]
        ]
        if not texts or any(text != texts[0] for text in texts):
            _reject("CAPABILITY_MISMATCH", root_digest, "source compiler manifests are absent or disagree")
        manifest = json.loads(texts[0], object_pairs_hook=_unique_object)
        source = {
            "identity": source_identity,
            "source_alias": provenance["source_alias"],
            "requested_revision": provenance["requested_revision"],
            "artifacts": material["artifacts"],
        }
        values, shape = _decode_tensor(
            source_root, cartridge, bundle["source_root"], manifest["target_tensor"]
        )
        expected_evidence = _canonical_copy(manifest["evidence"])
        expected_evidence["target"]["source_values"] = values
        if (
            _digest(_compile_inputs(source, manifest, tensor_inventory)) != plan_digest
            or expected_evidence["target"]["source_shape"] != shape
            or bundle["evidence"] != expected_evidence
            or certificate != _certificate(
                expected_evidence, manifest["eta_rep"], manifest["rank_budget"], manifest["operation_bounds"]
            )
            or inventory != manifest["operator_inventory"]
            or bundle["profile"] != manifest["profile"]
            or bundle["contribution_map"]["target_tensor"] != manifest["target_tensor"]
            or plan["prior_mode_failures"] != manifest["prior_mode_failures"]
        ):
            _reject("CAPABILITY_MISMATCH", root_digest, "compiled proof differs from its immutable source and preparation inputs")
    elif bundle["version"] == _RECOMPILE_VERSION:
        specification = _specification_from_bundle(
            cartridge, root_digest, root, bundle
        )
        expected_plan_digest = _digest({
            "version": _RECOMPILE_VERSION,
            "specification": specification,
        })
        (
            _,
            expected_evidence,
            expected_certificate,
            expected_tensor_inventory,
            expected_contribution,
            _,
            expected_derivation,
            expected_recovery,
            _,
            _,
        ) = _proof_from_specification(cartridge, specification)
        if (
            plan_digest != expected_plan_digest
            or bundle["evidence"] != expected_evidence
            or certificate != expected_certificate
            or tensor_inventory != expected_tensor_inventory
            or bundle["contribution_map"] != expected_contribution
            or bundle["derivation"] != expected_derivation
            or bundle["recovery"] != expected_recovery
            or root["deltas"] != source_root["deltas"]
        ):
            _reject(
                "CAPABILITY_MISMATCH",
                root_digest,
                "recompiled root differs from its clean source, certificate, dependency, or recovery derivation",
                "Q27/Q61/Q70/Q75: clean derivation equals the persisted incremental result",
            )
        graph_digest = expected_derivation["derivation_id"]
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
        graph_digest,
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
    if len(root["plans"]) == 2:
        _verified_hardware_catalog(
            root["plans"][1],
            bundle,
            page_locations(cartridge, root_digest),
            page_index_byte_count(cartridge, root_digest),
            root_digest,
        )
    return plan, certificate, bundle["evidence"], bundle["profile"], root["identity"]


def _compiled_identity_material(root: dict) -> IdentityTuple:
    provenance = root["provenance"]
    record = provenance["identity_material"]
    return IdentityTuple(
        revision_kind=provenance["revision_kind"],
        source_kind=record["source_kind"],
        source_alias=provenance["source_alias"],
        canonical_locator=record["locator"],
        requested_revision=provenance["requested_revision"],
        immutable_revision=record["immutable_revision"],
        artifacts=tuple(ArtifactIdentity(**artifact) for artifact in record["artifacts"]),
        format_versions=tuple(tuple(item) for item in record["format_versions"]),
        tensor_index_digest=record["tensor_index_digest"],
        config_digest=record["config_digest"],
        architecture=record["architecture"],
        operator_set=tuple(record["operator_set"]),
        tokenizer_digest=record["tokenizer_digest"],
        processor_digest=record["processor_digest"],
        template_digest=record["template_digest"],
        precision_scheme=record["precision_scheme"],
        license_digest=record["license_digest"],
        parent_ids=tuple(record["parent_ids"]),
        transform_manifest_digest=record["transform_manifest_digest"],
    )


def _prepare_hardware_plans(
    cartridge: str | Path,
    compiled_root_digest: str,
    source_identity: str,
    preparation_plan_digest: str,
    specifications: object,
    capacity_coordinator: CapacityCoordinator,
    operation_id: str,
) -> str:
    _verify_bundle_structure(
        cartridge, compiled_root_digest, source_identity, preparation_plan_digest
    )
    root = load_root(cartridge, compiled_root_digest)
    bundle = root["plans"][0]
    locations = page_locations(cartridge, compiled_root_digest)
    catalog = _hardware_catalog(
        bundle,
        locations,
        page_index_byte_count(cartridge, compiled_root_digest),
        specifications,
    )
    candidate = derive_root(
        cartridge,
        compiled_root_digest,
        _compiled_identity_material(root),
        (bundle, catalog),
        capacity_controller=capacity_coordinator,
        operation_id=operation_id,
    )
    _verify_bundle_structure(
        cartridge, candidate, source_identity, preparation_plan_digest
    )
    return candidate


def _verify_hardware_plans(
    cartridge: str | Path,
    root_digest: str,
    source_identity: str,
    preparation_plan_digest: str,
) -> tuple[dict, ...]:
    _verify_bundle_structure(
        cartridge, root_digest, source_identity, preparation_plan_digest
    )
    root = load_root(cartridge, root_digest)
    if len(root["plans"]) != 2:
        _hardware_reject("CAPABILITY_MISMATCH", root_digest, "compiled root has no certified hardware plans")
    return tuple(root["plans"][1]["plans"])


def _select_hardware_plan(
    cartridge: str | Path,
    root_digest: str,
    source_identity: str,
    preparation_plan_digest: str,
    measured_profile: object,
) -> HardwarePlanSelection:
    plans = _verify_hardware_plans(
        cartridge, root_digest, source_identity, preparation_plan_digest
    )
    profile = _measured_hardware_profile(measured_profile)
    candidates = [
        (_measured_plan_latency(plan, profile), plan["plan_id"], plan)
        for plan in plans
        if _profile_matches(plan, profile)
    ]
    if not candidates:
        _hardware_reject(
            "CAPABILITY_MISMATCH",
            root_digest,
            "no certified plan satisfies the measured class; recompile for this hardware envelope",
        )
    predicted, _, selected = min(candidates, key=lambda item: (item[0], item[1]))
    return HardwarePlanSelection(
        root_digest=root_digest,
        plan_id=selected["plan_id"],
        certificate_id=selected["q19_certificate_digest"],
        measured_profile_digest=_digest(profile),
        predicted_total_latency_ns=predicted,
        plan=selected,
    )


def _plan_export(cartridge: str | Path, root_digest: str, target_schema: str) -> dict:
    """Admit one target only when its artifact plus bound sidecar retains every root semantic."""

    _exact_digest(root_digest, "export:plan", "source root digest")
    if target_schema not in _EXPORT_TARGETS:
        _reject("MODEL_UNSUPPORTED", root_digest, f"export target {target_schema!r} is unsupported")
    root = load_root(cartridge, root_digest)
    mode = "adapter" if target_schema == "adapter-safetensors-v1" else "full"
    delta_id = adapter_rank = adapter_scale = None
    if root["deltas"]:
        delta_id, adapter_rank, adapter_scale = adapter_export_fields(cartridge, root_digest)
        if mode == "full":
            mode = "merged"
    if target_schema == "gguf-v3" and not set(root["operators"]) <= set(
        EXPORT_TARGETS[target_schema]["operators"]
    ):
        _reject(
            "MODEL_UNSUPPORTED",
            root_digest,
            "GGUF target cannot represent one or more required operators",
        )
    semantic_binding = export_semantic_binding(cartridge, root_digest)
    body = {
        "version": "q26-export-v1",
        "source_root": root_digest,
        "source_identity": root["identity"],
        "target_schema": target_schema,
        "mode": mode,
        "semantic_binding": semantic_binding,
        "delta_id": delta_id,
        "adapter_rank": adapter_rank,
        "adapter_scale": adapter_scale,
    }
    return export_shape(cartridge, body)


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


def plan_export(cartridge: str | Path, root_digest: str, target_schema: str) -> dict:
    """Return one exact byte-sized export plan after semantic representability passes."""

    return _boundary(
        "export-plan",
        {"identity": root_digest},
        _plan_export,
        cartridge,
        root_digest,
        target_schema,
    )


def prepare_revision(
    source: object,
    extents: object,
    cartridge: str | Path,
    expected_plan_digest: str,
    *,
    capacity_coordinator: CapacityCoordinator,
    operation_id: str,
) -> PreparedRevision:
    """Consume verified bytes once, derive every proof object, and return one unpublished candidate."""

    if not isinstance(capacity_coordinator, CapacityCoordinator):
        _reject(
            "INVALID_REQUEST",
            "compiler:prepare",
            "the concrete store-owned CapacityCoordinator is required",
        )
    if not capacity_coordinator.owns(cartridge):
        _reject(
            "INVALID_REQUEST",
            "compiler:prepare",
            "capacity coordinator does not own the target cartridge filesystem",
        )
    return _boundary(
        "prepare",
        source,
        _prepare_revision,
        source,
        extents,
        cartridge,
        expected_plan_digest,
        capacity_coordinator,
        operation_id,
    )


def compilation_specification(
    cartridge: str | Path, compiled_root_digest: str
) -> dict:
    """Return the complete editable Q75 input record for one verified compiled revision."""

    def inspect() -> dict:
        root, bundle = _verified_compiled_bundle(cartridge, compiled_root_digest)
        return _specification_from_bundle(
            cartridge, compiled_root_digest, root, bundle
        )

    return _boundary(
        "recompile-specification",
        {"identity": compiled_root_digest},
        inspect,
    )


def recompile_revision(
    cartridge: str | Path,
    specification: object,
    previous_root_digest: str | None = None,
    *,
    operation_id: str,
    capacity_coordinator: CapacityCoordinator,
) -> RecompiledRevision:
    """Build one deterministic unpublished child and report exact Q27 reuse against its predecessor."""

    if not isinstance(capacity_coordinator, CapacityCoordinator):
        _reject(
            "INVALID_REQUEST",
            operation_id,
            "the concrete store-owned CapacityCoordinator is required",
        )
    if not capacity_coordinator.owns(cartridge):
        _reject(
            "INVALID_REQUEST",
            operation_id,
            "capacity coordinator does not own the target cartridge filesystem",
        )

    def recompile() -> RecompiledRevision:
        incremental = _recompile_revision(
            cartridge, specification, previous_root_digest, False, operation_id, capacity_coordinator
        )
        if previous_root_digest is None:
            return incremental
        clean = _recompile_revision(
            cartridge, specification, None, False, operation_id, capacity_coordinator
        )
        if (
            incremental.candidate_root != clean.candidate_root
            or incremental.plan_digest != clean.plan_digest
            or incremental.derivation_digest != clean.derivation_digest
        ):
            _reject(
                "CAPABILITY_MISMATCH",
                previous_root_digest,
                "incremental recompile differs from its clean full derivation",
                "Q27/Q61/Q75: incremental and clean compilation produce one exact child",
            )
        return incremental

    return _boundary(
        "recompile",
        {"identity": previous_root_digest or "compiler:clean-recompile"},
        recompile,
    )


def prepare_recovered_revision(
    cartridge: str | Path,
    training_root_digest: str,
    compiled_parent_root_digest: str,
    *,
    operation_id: str,
    capacity_coordinator: CapacityCoordinator,
) -> RecompiledRevision:
    """Consume one committed Tier-B artifact and return its independently regenerated Q19 child."""

    if not isinstance(capacity_coordinator, CapacityCoordinator):
        _reject(
            "INVALID_REQUEST",
            operation_id,
            "the concrete store-owned CapacityCoordinator is required",
        )
    if not capacity_coordinator.owns(cartridge):
        _reject(
            "INVALID_REQUEST",
            operation_id,
            "capacity coordinator does not own the target cartridge filesystem",
        )

    def recover() -> RecompiledRevision:
        _exact_digest(training_root_digest, "compiler:recover", "training root")
        _exact_digest(compiled_parent_root_digest, "compiler:recover", "compiled parent root")
        _, recovery = _recovery_bindings(cartridge, training_root_digest)
        if (
            recovery["kind"] != "COMPILED_RECOVERY"
            or recovery["parent_root"] != compiled_parent_root_digest
        ):
            _reject(
                "IDENTITY_MISMATCH",
                training_root_digest,
                "Tier-B recovery artifact names another compiled parent",
                "Q70/Q75: recovery consumes its exact callable compiled parent",
            )
        specification = compilation_specification(
            cartridge, compiled_parent_root_digest
        )
        specification["source_root"] = training_root_digest
        incremental = _recompile_revision(
            cartridge,
            specification,
            compiled_parent_root_digest,
            True,
            operation_id,
            capacity_coordinator,
        )
        clean = _recompile_revision(
            cartridge,
            specification,
            None,
            True,
            operation_id,
            capacity_coordinator,
        )
        if (
            incremental.candidate_root != clean.candidate_root
            or incremental.plan_digest != clean.plan_digest
            or incremental.derivation_digest != clean.derivation_digest
        ):
            _reject(
                "CAPABILITY_MISMATCH",
                training_root_digest,
                "incremental Tier-B recovery differs from its clean full certificate derivation",
                "Q70/Q75: incremental and clean recovery produce one exact child",
            )
        return incremental

    return _boundary(
        "recover",
        {"identity": training_root_digest},
        recover,
    )


def verify_bundle_structure(
    cartridge: str | Path,
    root_digest: str,
    source_identity: str,
    plan_digest: str,
    source_descriptors: Mapping[str, int] | None = None,
) -> tuple[dict, dict, dict, dict, str]:
    """Reject structurally detached maps, plans, source parents, and extent claims before publication."""

    return _boundary(
        "verify",
        {"identity": source_identity},
        _verify_bundle_structure,
        cartridge,
        root_digest,
        source_identity,
        plan_digest,
        source_descriptors,
    )


def prepare_hardware_plans(
    cartridge: str | Path,
    compiled_root_digest: str,
    source_identity: str,
    preparation_plan_digest: str,
    specifications: object,
    *,
    capacity_coordinator: CapacityCoordinator,
    operation_id: str,
) -> str:
    """Attach replaceable hardware metadata without changing executable identity or page capacity."""

    if not isinstance(capacity_coordinator, CapacityCoordinator):
        _reject(
            "INVALID_REQUEST",
            "compiler:hardware-plan-prepare",
            "the concrete store-owned CapacityCoordinator is required",
        )
    if not capacity_coordinator.owns(cartridge):
        _reject(
            "INVALID_REQUEST",
            "compiler:hardware-plan-prepare",
            "capacity coordinator does not own the target cartridge filesystem",
        )
    return _boundary(
        "hardware-plan-prepare",
        {"identity": source_identity},
        _prepare_hardware_plans,
        cartridge,
        compiled_root_digest,
        source_identity,
        preparation_plan_digest,
        specifications,
        capacity_coordinator,
        operation_id,
    )


def verify_hardware_plans(
    cartridge: str | Path,
    root_digest: str,
    source_identity: str,
    preparation_plan_digest: str,
) -> tuple[dict, ...]:
    """Return hardware plans only after recomputing their page, certificate, and budget bindings."""

    return _boundary(
        "hardware-plan-verify",
        {"identity": source_identity},
        _verify_hardware_plans,
        cartridge,
        root_digest,
        source_identity,
        preparation_plan_digest,
    )


def select_hardware_plan(
    cartridge: str | Path,
    root_digest: str,
    source_identity: str,
    preparation_plan_digest: str,
    measured_profile: object,
) -> HardwarePlanSelection:
    """Choose the lowest predicted-latency certified plan that contains the measured profile."""

    return _boundary(
        "hardware-plan-select",
        {"identity": source_identity},
        _select_hardware_plan,
        cartridge,
        root_digest,
        source_identity,
        preparation_plan_digest,
        measured_profile,
    )
