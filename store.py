# store.py — identity, content pages, transactions, and generations (Q1/Q25/Q32/Q57/Q60/Q73); depends on errors.py, schema.
"""Own model identity, content, transaction recovery, and callable generations.

Source adapters may accept mutable aliases, but they must return a canonical locator and a typed
immutable revision digest. Requested aliases remain provenance; they never enter the identity.
Cassette-owned identities and canonical content use BLAKE3 through this module alone. SafeTensors
payloads enter bounded pages and segments; tensor maps retain their semantic byte ranges while a
separate fixed-record index owns physical placement.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import tempfile

from blake3 import blake3
import rfc8785

from errors import CassetteError
from schema.validator import validate

_DIGEST_HEX_LENGTHS = {"blake3": 64, "sha256": 64, "git-sha1": 40}
_HEX = frozenset("0123456789abcdef")
_REVISION_KINDS = frozenset({"source", "executable", "tuned", "exported"})
_MAX_JSON_INTEGER = 2**53 - 1
PAGE_BYTES = 4 * 1024 * 1024
SEGMENT_BYTES = 1024 * 1024 * 1024
_SAFETENSORS_HEADER_BYTES = 100_000_000
_SAFETENSORS_DTYPE_BITS = {
    "F4": 4, "F6_E2M3": 6, "F6_E3M2": 6,
    "BOOL": 8, "U8": 8, "I8": 8, "F8_E5M2": 8, "F8_E4M3": 8, "F8_E8M0": 8,
    "I16": 16, "U16": 16, "F16": 16, "BF16": 16,
    "I32": 32, "U32": 32, "F32": 32,
    "I64": 64, "U64": 64, "F64": 64,
}
_INDEX_RECORD = struct.Struct(">32s32sQI")
_IDENTITY_RECORD_FIELDS = frozenset({
    "source_kind", "locator", "immutable_revision", "artifacts", "format_versions",
    "tensor_index_digest", "config_digest", "architecture", "operator_set",
    "tokenizer_digest", "processor_digest", "template_digest", "precision_scheme",
    "license_digest", "parent_ids", "transform_manifest_digest",
})
_ROOT_FIELDS = frozenset({
    "identity", "parents", "provenance", "semantic_assets", "tensor_maps", "operators",
    "plans", "deltas", "integrity_root",
})
_TRANSACTION_STATES = (
    "PREPARE",
    "WRITE_TEMP",
    "READBACK_HASH",
    "JOURNAL_PAGE",
    "WRITE_CANDIDATE_ROOT",
    "FULLFSYNC",
    "SWAP_GENERATION_POINTER",
    "FULLFSYNC",
    "COMMITTED",
)
_DEPENDENCY_ORDER = ("payloads", "indexes", "child_root", "verification", "generation_pointer")
_TRANSACTION_FIELDS = frozenset({
    "transaction_id", "step", "state", "candidate_generation", "candidate_root",
    "candidate_id", "expected_parent_generation", "expected_parent_id", "expected_parent_root",
    "generation_record_digest", "dependency_order", "dependency_cursor", "pointer_cursor",
    "resume",
})
_RESUME_FIELDS = frozenset({
    "operation_version", "input_digests", "random_seed", "statistics_digest",
    "page_results", "optimizer_step", "rng_state_digest", "data_cursor", "loss_scale",
})
_TRAINING_MANIFEST_FIELDS = _RESUME_FIELDS - {"page_results"}
_GENERATION_FIELDS = frozenset({
    "generation", "child_id", "root_digest", "parent_generation", "parent_id",
    "parent_root", "training_manifest", "transaction_id",
})
_TRANSACTION_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")
_GENERATION_NAME = re.compile(r"([0-9]{20})\.json")


@dataclass(frozen=True)
class ArtifactIdentity:
    """One Q1 artifact: canonical source path, exact byte count, and authoritative digest."""

    path: str
    size: int
    digest: str


@dataclass(frozen=True)
class IdentityTuple:
    """Q1 identity material plus non-identity alias and revision-kind evidence."""

    revision_kind: str
    source_kind: str
    source_alias: str
    canonical_locator: str
    requested_revision: str | None
    immutable_revision: str | None
    artifacts: tuple[ArtifactIdentity, ...]
    format_versions: tuple[tuple[str, str], ...]
    tensor_index_digest: str
    config_digest: str
    architecture: str
    operator_set: tuple[str, ...]
    tokenizer_digest: str
    processor_digest: str
    template_digest: str
    precision_scheme: str
    license_digest: str
    parent_ids: tuple[str, ...]
    transform_manifest_digest: str | None


@dataclass(frozen=True)
class TensorSpan:
    """One Q57 tensor interval inside one content page."""

    page_digest: str
    offset: int
    length: int
    tensor_offset: int

    def record(self) -> dict:
        return {
            "page_digest": self.page_digest,
            "offset": self.offset,
            "length": self.length,
            "tensor_offset": self.tensor_offset,
        }


@dataclass(frozen=True)
class TensorMap:
    """One semantic tensor reconstructed from representation-independent page spans."""

    semantic_tensor_id: str
    shape: tuple[int, ...]
    dtype: str
    spans: tuple[TensorSpan, ...]

    def record(self) -> dict:
        return {
            "semantic_tensor_id": self.semantic_tensor_id,
            "shape": list(self.shape),
            "dtype": self.dtype,
            "codec": "raw-little-endian",
            "plane": None,
            "spans": [span.record() for span in self.spans],
        }


@dataclass(frozen=True)
class PageLocation:
    """One fixed-schema physical index record; it never enters the logical root."""

    page_digest: str
    segment_id: str
    offset: int
    length: int


@dataclass(frozen=True)
class GenerationPin:
    """One Q73 reader pin; immutable roots keep its bytes stable across later commits."""

    generation: int
    child_id: str
    root_digest: str


@dataclass(frozen=True)
class TransactionState:
    """The last durable Q25 transition for one resumable generation transaction."""

    transaction_id: str
    state: str
    step: int
    candidate_generation: int
    candidate_root: str
    dependency_cursor: int
    pointer_cursor: int


@dataclass(frozen=True)
class TransactionContext:
    """Bounded Q25/Q60 restart material retained by digest and exact cartridge bytes."""

    operation_version: str
    input_digests: tuple[str, ...]
    random_seed: int | None = None
    statistics: bytes | None = None
    optimizer_step: int | None = None
    rng_state: bytes | None = None
    data_cursor: int | None = None
    loss_scale: str | None = None


def _reject(field: str, reason: str, object_id: str = "model:unidentified") -> None:
    raise CassetteError(
        code="IDENTITY_MISMATCH",
        object_id=object_id,
        failed_invariant="Q1: complete immutable identity required",
        retryability="terminal",
        detail=f"{field}: {reason}",
    )


def _text(field: str, value: object, object_id: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        _reject(field, "nonempty text without surrounding whitespace required", object_id)
    return value


def _digest(field: str, value: object, object_id: str) -> str:
    normalized = _text(field, value, object_id).lower()
    algorithm, separator, hexadecimal = normalized.partition(":")
    if (separator != ":" or len(hexadecimal) != _DIGEST_HEX_LENGTHS.get(algorithm)
            or not set(hexadecimal) <= _HEX):
        _reject(
            field,
            f"expected one of {sorted(_DIGEST_HEX_LENGTHS)} with its exact hexadecimal length",
            object_id,
        )
    return f"{algorithm}:{hexadecimal}"


def _digests(field: str, values: object, object_id: str, *, empty: bool) -> tuple[str, ...]:
    if not isinstance(values, (list, tuple, set, frozenset)):
        _reject(field, "a digest collection is required", object_id)
    result = tuple(_digest(f"{field}[]", value, object_id) for value in values)
    if not empty and not result:
        _reject(field, "at least one digest is required", object_id)
    if len(set(result)) != len(result):
        _reject(field, "duplicate digests are forbidden", object_id)
    if any(not value.startswith("blake3:") for value in result):
        _reject(field, "Cassette revision identities must use BLAKE3", object_id)
    return tuple(sorted(result))


def digest_bytes(payload: bytes | bytearray | memoryview) -> str:
    """Return the sole Cassette-owned content digest used by Q1/Q51/Q57/Q62."""

    if not isinstance(payload, (bytes, bytearray, memoryview)):
        _reject("payload", "bytes, bytearray, or memoryview required", "content:unidentified")
    return f"blake3:{blake3(payload).hexdigest()}"


def canonical_bytes(value: object) -> bytes:
    """Return the sole RFC 8785 representation used for identity and manifests."""

    try:
        return rfc8785.dumps(value)
    except rfc8785.CanonicalizationError as error:
        _reject("canonical_value", str(error))


def _identity_record(material: IdentityTuple) -> dict:
    """Validate Q1 material and return the exact JSON-native identity preimage."""

    if not isinstance(material, IdentityTuple):
        _reject("identity_tuple", "IdentityTuple required")
    object_id = "model:unidentified"
    revision_kind = _text("revision_kind", material.revision_kind, object_id)
    if revision_kind not in _REVISION_KINDS:
        _reject("revision_kind", f"expected one of {sorted(_REVISION_KINDS)}", object_id)
    source_kind = _text("source_kind", material.source_kind, object_id)
    source_alias = _text("source_alias", material.source_alias, object_id)
    object_id = f"source:{source_kind}:{source_alias}"
    locator = _text("canonical_locator", material.canonical_locator, object_id)
    if material.requested_revision is not None:
        _text("requested_revision", material.requested_revision, object_id)
    if material.immutable_revision is None:
        _reject("immutable_revision", "mutable source reference has no immutable resolution", object_id)
    immutable_revision = _digest("immutable_revision", material.immutable_revision, object_id)

    if not isinstance(material.artifacts, (list, tuple)) or not material.artifacts:
        _reject("artifacts", "at least one resolved artifact is required", object_id)
    artifacts = []
    for artifact in material.artifacts:
        if not isinstance(artifact, ArtifactIdentity):
            _reject("artifacts[]", "ArtifactIdentity required", object_id)
        path = _text("artifacts[].path", artifact.path, object_id)
        if type(artifact.size) is not int or not 0 <= artifact.size <= _MAX_JSON_INTEGER:
            _reject("artifacts[].size", "an RFC 8785-safe nonnegative byte count is required", object_id)
        artifacts.append({"path": path, "size": artifact.size,
                          "digest": _digest("artifacts[].digest", artifact.digest, object_id)})
    if len({artifact["path"] for artifact in artifacts}) != len(artifacts):
        _reject("artifacts[].path", "paths must be unique", object_id)

    if not isinstance(material.format_versions, (list, tuple)) or not material.format_versions:
        _reject("format_versions", "at least one name and version pair is required", object_id)
    formats = []
    for item in material.format_versions:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            _reject("format_versions[]", "a name and version pair is required", object_id)
        formats.append((_text("format_versions[].name", item[0], object_id),
                        _text("format_versions[].version", item[1], object_id)))
    if len({name for name, _ in formats}) != len(formats):
        _reject("format_versions[].name", "names must be unique", object_id)

    if not isinstance(material.operator_set, (list, tuple, set, frozenset)):
        _reject("operator_set", "an operator collection is required", object_id)
    operators = tuple(_text("operator_set[]", value, object_id) for value in material.operator_set)
    if not operators or len(set(operators)) != len(operators):
        _reject("operator_set", "a nonempty set without duplicates is required", object_id)
    parents = _digests("parent_ids", material.parent_ids, object_id, empty=True)
    transform = None if material.transform_manifest_digest is None else _digest(
        "transform_manifest_digest", material.transform_manifest_digest, object_id
    )
    if transform is not None and not transform.startswith("blake3:"):
        _reject("transform_manifest_digest", "Cassette transform digests must use BLAKE3", object_id)
    if revision_kind == "source" and (parents or transform is not None):
        _reject("revision_binding", "source revisions cannot have parents or transforms", object_id)
    if revision_kind != "source" and (not parents or transform is None):
        _reject("revision_binding", "derived revisions require a parent and transform digest", object_id)

    canonical = {
        "source_kind": source_kind,
        "locator": locator,
        "immutable_revision": immutable_revision,
        "artifacts": sorted(artifacts, key=lambda artifact: artifact["path"]),
        "format_versions": [list(item) for item in sorted(formats)],
        "tensor_index_digest": _digest("tensor_index_digest", material.tensor_index_digest, object_id),
        "config_digest": _digest("config_digest", material.config_digest, object_id),
        "architecture": _text("architecture", material.architecture, object_id),
        "operator_set": sorted(operators),
        "tokenizer_digest": _digest("tokenizer_digest", material.tokenizer_digest, object_id),
        "processor_digest": _digest("processor_digest", material.processor_digest, object_id),
        "template_digest": _digest("template_digest", material.template_digest, object_id),
        "precision_scheme": _text("precision_scheme", material.precision_scheme, object_id),
        "license_digest": _digest("license_digest", material.license_digest, object_id),
        "parent_ids": list(parents),
        "transform_manifest_digest": transform,
    }
    return canonical


def model_identity(material: IdentityTuple) -> str:
    """Return I only when P(I) is complete, immutable, and correctly bound to its revision kind."""

    return digest_bytes(canonical_bytes(_identity_record(material)))


def _q57_reject(object_id: str, detail: str, code: str = "ROOT_INVALID") -> None:
    raise CassetteError(
        code=code,
        object_id=object_id,
        failed_invariant="Q57: canonical cartridge representation",
        retryability="retryable" if code in {"PAGE_CORRUPT", "SOURCE_UNAVAILABLE"} else "terminal",
        detail=detail,
    )


def _content_hex(value: object, object_id: str) -> str:
    if (not isinstance(value, str) or not value.startswith("blake3:") or len(value) != 71
            or not set(value[7:]) <= _HEX):
        _q57_reject(str(object_id), "a lowercase BLAKE3 digest is required")
    return value[7:]


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def _read_exact(handle, length: int, object_id: str, description: str) -> bytes:
    payload = bytearray()
    while len(payload) < length:
        chunk = handle.read(length - len(payload))
        if not chunk:
            _q57_reject(object_id, f"{description} ended after {len(payload)} of {length} bytes")
        payload.extend(chunk)
    return bytes(payload)


def _artifact_hasher(expected_digest: str, object_id: str):
    algorithm = expected_digest.partition(":")[0]
    if algorithm == "blake3":
        return blake3()
    if algorithm == "sha256":
        return hashlib.sha256()
    _reject(
        "artifacts[].digest",
        "SafeTensors byte verification requires a BLAKE3 or SHA-256 artifact digest",
        object_id,
    )


def _safetensors_header(
    handle, source: Path, object_id: str, artifact_hasher
) -> tuple[int, int, dict, tuple[tuple, ...]]:
    prefix = _read_exact(handle, 8, object_id, "SafeTensors header length")
    artifact_hasher.update(prefix)
    header_length = int.from_bytes(prefix, "little")
    file_size = source.stat().st_size
    if not 0 < header_length <= _SAFETENSORS_HEADER_BYTES or 8 + header_length > file_size:
        _q57_reject(object_id, "SafeTensors header length is outside its file or 100 MB limit")
    encoded = _read_exact(handle, header_length, object_id, "SafeTensors header")
    artifact_hasher.update(encoded)
    if encoded[:1] != b"{":
        _q57_reject(object_id, "SafeTensors header must be complete UTF-8 JSON beginning with '{'")
    try:
        header = json.loads(encoded, object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        _q57_reject(object_id, f"invalid SafeTensors header: {error}")
    if not isinstance(header, dict):
        _q57_reject(object_id, "SafeTensors header must be an object")
    metadata = header.pop("__metadata__", {})
    if (not isinstance(metadata, dict)
            or any(not isinstance(key, str) or not isinstance(value, str)
                   for key, value in metadata.items())):
        _q57_reject(object_id, "SafeTensors metadata must map strings to strings")

    data_size = file_size - 8 - header_length
    tensors = []
    for name, spec in header.items():
        if (not isinstance(name, str) or not name or not isinstance(spec, dict)
                or set(spec) != {"dtype", "shape", "data_offsets"}):
            _q57_reject(object_id, f"tensor {name!r} lacks the exact SafeTensors fields")
        dtype, shape, offsets = spec["dtype"], spec["shape"], spec["data_offsets"]
        if dtype not in _SAFETENSORS_DTYPE_BITS:
            _q57_reject(object_id, f"tensor {name!r} has an unknown SafeTensors dtype")
        if (not isinstance(shape, list)
                or any(type(dimension) is not int or dimension < 0 for dimension in shape)):
            _q57_reject(object_id, f"tensor {name!r} has an invalid shape")
        if (not isinstance(offsets, list) or len(offsets) != 2
                or any(type(offset) is not int for offset in offsets)):
            _q57_reject(object_id, f"tensor {name!r} has invalid data offsets")
        start, end = offsets
        if not 0 <= start <= end <= data_size:
            _q57_reject(object_id, f"tensor {name!r} points outside the SafeTensors byte buffer")
        elements = 1
        for dimension in shape:
            elements *= dimension
        bit_length = elements * _SAFETENSORS_DTYPE_BITS[dtype]
        if bit_length % 8 or end - start != bit_length // 8:
            _q57_reject(object_id, f"tensor {name!r} shape, dtype, and byte range disagree")
        tensors.append((name, dtype, tuple(shape), start, end))
    if not tensors:
        _q57_reject(object_id, "SafeTensors header contains no tensors")

    cursor = 0
    for name, _, _, start, end in sorted(tensors, key=lambda tensor: (tensor[3], tensor[4], tensor[0])):
        if start != cursor:
            relation = "overlaps another tensor" if start < cursor else "leaves a hole"
            _q57_reject(object_id, f"tensor {name!r} {relation} in the indexed byte buffer")
        cursor = end
    if cursor != data_size:
        _q57_reject(object_id, "SafeTensors byte buffer is not entirely indexed")
    return 8 + header_length, data_size, metadata, tuple(sorted(tensors))


def _tensor_maps(tensors: tuple[tuple, ...], page_digests: list[str]) -> tuple[TensorMap, ...]:
    maps = []
    for name, dtype, shape, start, end in tensors:
        spans = []
        cursor = start
        while cursor < end:
            page_number, offset = divmod(cursor, PAGE_BYTES)
            length = min(end - cursor, PAGE_BYTES - offset)
            spans.append(TensorSpan(page_digests[page_number], offset, length, cursor - start))
            cursor += length
        maps.append(TensorMap(name, shape, dtype, tuple(spans)))
    return tuple(maps)


def _file_digest(path: Path) -> str:
    digest = blake3()
    with path.open("rb") as handle:
        while payload := handle.read(PAGE_BYTES):
            digest.update(payload)
    return f"blake3:{digest.hexdigest()}"


def _write_segments(cartridge: Path, pages) -> tuple[PageLocation, ...]:
    directory = cartridge / "segments"
    directory.mkdir(parents=True, exist_ok=True)
    locations = []
    temporary = None
    pending = []
    segment_digest = None
    segment_length = 0

    def finish() -> None:
        nonlocal temporary, pending, segment_digest, segment_length
        if temporary is None:
            return
        temporary.flush()
        temporary.close()
        segment_id = f"blake3:{segment_digest.hexdigest()}"
        destination = directory / _content_hex(segment_id, segment_id)
        temporary_path = Path(temporary.name)
        if destination.exists():
            if _file_digest(destination) != segment_id:
                _q57_reject(segment_id, "existing segment bytes do not match their name", "PAGE_CORRUPT")
            temporary_path.unlink()
        else:
            temporary_path.replace(destination)
        locations.extend(
            PageLocation(page_digest, segment_id, offset, length)
            for page_digest, offset, length in pending
        )
        temporary = None
        pending = []
        segment_digest = None
        segment_length = 0

    try:
        for page_digest, payload in pages:
            if not isinstance(payload, bytes) or not 0 < len(payload) <= PAGE_BYTES:
                _q57_reject(str(page_digest), "content pages must contain at most 4 MiB")
            if digest_bytes(payload) != page_digest:
                _q57_reject(str(page_digest), "content page digest does not match its payload", "PAGE_CORRUPT")
            if segment_length and segment_length + len(payload) > SEGMENT_BYTES:
                finish()
            if temporary is None:
                temporary = tempfile.NamedTemporaryFile(
                    mode="w+b", dir=directory, prefix=".pending-", delete=False
                )
                segment_digest = blake3()
            offset = segment_length
            temporary.write(payload)
            segment_digest.update(payload)
            pending.append((page_digest, offset, len(payload)))
            segment_length += len(payload)
        finish()
    finally:
        if temporary is not None:
            name = Path(temporary.name)
            temporary.close()
            name.unlink(missing_ok=True)
    return tuple(locations)


def _index_path(cartridge: Path, root_digest: str) -> Path:
    return cartridge / "indexes" / _content_hex(root_digest, root_digest)


def _write_index(cartridge: Path, root_digest: str, locations: tuple[PageLocation, ...]) -> None:
    by_page = {location.page_digest: location for location in locations}
    if len(by_page) != len(locations):
        _q57_reject(root_digest, "physical page index contains duplicate page identities")
    payload = b"".join(
        _INDEX_RECORD.pack(
            bytes.fromhex(_content_hex(location.page_digest, location.page_digest)),
            bytes.fromhex(_content_hex(location.segment_id, location.segment_id)),
            location.offset,
            location.length,
        )
        for location in sorted(locations, key=lambda item: item.page_digest)
    )
    path = _index_path(cartridge, root_digest)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def _read_index(cartridge: Path, root_digest: str) -> dict[str, PageLocation]:
    path = _index_path(cartridge, root_digest)
    try:
        payload = path.read_bytes()
    except OSError as error:
        _q57_reject(root_digest, f"physical page index is unavailable: {error}")
    if len(payload) % _INDEX_RECORD.size:
        _q57_reject(root_digest, "physical page index has a partial fixed-schema record")
    locations = {}
    for position in range(0, len(payload), _INDEX_RECORD.size):
        page, segment, offset, length = _INDEX_RECORD.unpack_from(payload, position)
        location = PageLocation(f"blake3:{page.hex()}", f"blake3:{segment.hex()}", offset, length)
        if location.page_digest in locations or not 0 < length <= PAGE_BYTES:
            _q57_reject(root_digest, "physical page index has a duplicate or invalid page record")
        locations[location.page_digest] = location
    return locations


def _read_page(cartridge: Path, location: PageLocation) -> bytes:
    path = cartridge / "segments" / _content_hex(location.segment_id, location.segment_id)
    try:
        with path.open("rb") as handle:
            handle.seek(location.offset)
            payload = handle.read(location.length)
    except OSError as error:
        _q57_reject(location.page_digest, f"segment read failed: {error}", "PAGE_CORRUPT")
    if len(payload) != location.length or digest_bytes(payload) != location.page_digest:
        _q57_reject(location.page_digest, "resolved page bytes do not match their identity", "PAGE_CORRUPT")
    return payload


def _material_from_provenance(provenance: object, root_digest: str) -> tuple[IdentityTuple, dict]:
    fields = {"revision_kind", "source_alias", "requested_revision", "identity_material", "containers"}
    if not isinstance(provenance, dict) or set(provenance) != fields:
        _q57_reject(root_digest, "root provenance lacks the exact Q1 evidence fields")
    record = provenance["identity_material"]
    artifacts = record.get("artifacts") if isinstance(record, dict) else None
    if (not isinstance(record, dict) or set(record) != _IDENTITY_RECORD_FIELDS
            or not isinstance(artifacts, list)
            or any(not isinstance(item, dict) or set(item) != {"path", "size", "digest"}
                   for item in artifacts)):
        _q57_reject(root_digest, "root provenance contains malformed Q1 identity material")
    try:
        material = IdentityTuple(
            revision_kind=provenance["revision_kind"],
            source_kind=record["source_kind"],
            source_alias=provenance["source_alias"],
            canonical_locator=record["locator"],
            requested_revision=provenance["requested_revision"],
            immutable_revision=record["immutable_revision"],
            artifacts=tuple(ArtifactIdentity(**item) for item in artifacts),
            format_versions=record["format_versions"],
            tensor_index_digest=record["tensor_index_digest"],
            config_digest=record["config_digest"],
            architecture=record["architecture"],
            operator_set=record["operator_set"],
            tokenizer_digest=record["tokenizer_digest"],
            processor_digest=record["processor_digest"],
            template_digest=record["template_digest"],
            precision_scheme=record["precision_scheme"],
            license_digest=record["license_digest"],
            parent_ids=record["parent_ids"],
            transform_manifest_digest=record["transform_manifest_digest"],
        )
        normalized = _identity_record(material)
    except (CassetteError, TypeError, ValueError) as error:
        _q57_reject(root_digest, f"root Q1 identity evidence is invalid: {error}")
    if normalized != record:
        _q57_reject(root_digest, "root Q1 identity evidence is not in canonical form")

    containers = provenance["containers"]
    if (not isinstance(containers, list)
            or any(not isinstance(item, dict) or set(item) != {"path", "format", "metadata"}
                   or item["format"] != "safetensors"
                   or not isinstance(item["metadata"], dict)
                   or any(not isinstance(key, str) or not isinstance(value, str)
                          for key, value in item["metadata"].items())
                   for item in containers)
            or [item["path"] for item in containers] != [item["path"] for item in artifacts]):
        _q57_reject(root_digest, "root container provenance does not match its Q1 artifacts")
    return material, record


def _merkle_root(leaves: list[dict]) -> str:
    encoded = sorted(canonical_bytes(leaf) for leaf in leaves)
    layer = [blake3(b"\x00" + leaf).digest() for leaf in encoded]
    while len(layer) > 1:
        if len(layer) % 2:
            layer.append(layer[-1])
        layer = [
            blake3(b"\x01" + layer[index] + layer[index + 1]).digest()
            for index in range(0, len(layer), 2)
        ]
    return f"blake3:{layer[0].hex()}"


def _root_integrity(root: dict, locations: tuple[PageLocation, ...]) -> str:
    manifest = {
        field: root[field]
        for field in sorted(_ROOT_FIELDS - {"integrity_root", "semantic_assets"})
    }
    leaves = [{"kind": "manifest", "name": "root", "value": manifest}]
    leaves.extend(
        {"kind": "page", "digest": location.page_digest, "length": location.length}
        for location in locations
    )
    leaves.extend(
        {"kind": "semantic_asset", "name": name, "value": value}
        for name, value in root["semantic_assets"].items()
    )
    return _merkle_root(leaves)


def _verify_root(root: object, root_digest: str, locations: dict[str, PageLocation]) -> None:
    defects = validate("root", root)
    if defects or not isinstance(root, dict) or set(root) != _ROOT_FIELDS:
        detail = "; ".join(defects[:3]) if defects else "root has an incorrect field set"
        _q57_reject(root_digest, f"root schema validation failed: {detail}")
    material, record = _material_from_provenance(root["provenance"], root_digest)
    if model_identity(material) != root["identity"]:
        _q57_reject(root_digest, "root Q1 identity does not match its recorded identity material")
    semantic_assets = {
        "processor": record["processor_digest"],
        "template": record["template_digest"],
        "tokenizer": record["tokenizer_digest"],
    }
    if (root["parents"] != record["parent_ids"]
            or root["operators"] != record["operator_set"]
            or root["semantic_assets"] != semantic_assets):
        _q57_reject(root_digest, "root bindings disagree with their Q1 identity material")
    required = {
        span["page_digest"]
        for tensor_map in root["tensor_maps"]
        for span in tensor_map["spans"]
    }
    if set(locations) != required:
        _q57_reject(root_digest, "physical page index does not match the logical root")
    ordered_locations = tuple(sorted(locations.values(), key=lambda item: item.page_digest))
    if root["integrity_root"] != _root_integrity(root, ordered_locations):
        _q57_reject(root_digest, "root integrity aggregate does not cover its pages and manifests")


def load_root(cartridge: str | Path, root_digest: str) -> dict:
    """Load one immutable root only when its bytes, Q1 evidence, index, and aggregate agree."""

    cartridge = Path(cartridge)
    path = cartridge / "roots" / _content_hex(root_digest, root_digest)
    try:
        payload = path.read_bytes()
        root = json.loads(payload, object_pairs_hook=_unique_object)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        _q57_reject(root_digest, f"root manifest is unavailable or malformed: {error}")
    if digest_bytes(payload) != root_digest or canonical_bytes(root) != payload:
        _q57_reject(root_digest, "root manifest is not the requested canonical object")
    _verify_root(root, root_digest, _read_index(cartridge, root_digest))
    return root


def import_safetensors(
    source: Mapping[str, str | Path], cartridge: str | Path, material: IdentityTuple
) -> str:
    """Import SafeTensors only when their bytes prove the supplied complete Q1 material."""

    identity_record = _identity_record(material)
    identity = digest_bytes(canonical_bytes(identity_record))
    expected_artifacts = {item["path"]: item for item in identity_record["artifacts"]}
    if not isinstance(source, Mapping) or not source:
        _q57_reject(identity, "canonical artifact paths must map to local SafeTensors files")
    sources = []
    for artifact_path, local_path in source.items():
        if not isinstance(artifact_path, str) or not artifact_path or artifact_path != artifact_path.strip():
            _q57_reject(identity, "every SafeTensors source requires one canonical artifact path")
        try:
            sources.append((artifact_path, Path(local_path)))
        except TypeError:
            _q57_reject(identity, f"artifact {artifact_path!r} has no local filesystem path")
    sources = tuple(sorted(sources))
    if {artifact_path for artifact_path, _ in sources} != set(expected_artifacts):
        _reject(
            "artifacts",
            "SafeTensors source paths differ from the complete Q1 artifact set",
            identity,
        )
    cartridge = Path(cartridge)
    artifacts = []
    tensor_names = set()
    for artifact_path, path in sources:
        object_id = f"source:{artifact_path}"
        expected_digest = expected_artifacts[artifact_path]["digest"]
        artifact_hasher = _artifact_hasher(expected_digest, object_id)
        try:
            with path.open("rb") as handle:
                data_start, data_size, metadata, tensors = _safetensors_header(
                    handle, path, object_id, artifact_hasher
                )
        except OSError as error:
            _q57_reject(object_id, f"SafeTensors source is unavailable: {error}", "SOURCE_UNAVAILABLE")
        names = {tensor[0] for tensor in tensors}
        if tensor_names & names:
            _q57_reject(object_id, "SafeTensors artifacts contain duplicate tensor names")
        tensor_names |= names
        artifacts.append((
            artifact_path, path, data_start, data_size, metadata, tensors,
            expected_digest.partition(":")[0], artifact_hasher,
        ))

    seen_pages = set()
    tensor_maps = []

    def unique_pages():
        for artifact_path, path, data_start, data_size, _, tensors, _, artifact_hasher in artifacts:
            object_id = f"source:{artifact_path}"
            try:
                handle = path.open("rb")
            except OSError as error:
                _q57_reject(object_id, f"SafeTensors source is unavailable: {error}", "SOURCE_UNAVAILABLE")
            with handle:
                handle.seek(data_start)
                remaining = data_size
                page_digests = []
                while remaining:
                    payload = _read_exact(
                        handle, min(PAGE_BYTES, remaining), object_id, "SafeTensors payload"
                    )
                    remaining -= len(payload)
                    artifact_hasher.update(payload)
                    page_digest = digest_bytes(payload)
                    page_digests.append(page_digest)
                    if page_digest not in seen_pages:
                        seen_pages.add(page_digest)
                        yield page_digest, payload
                tensor_maps.extend(_tensor_maps(tensors, page_digests))

    locations = _write_segments(cartridge, unique_pages())
    observed_artifacts = [
        {
            "path": artifact_path,
            "size": data_start + data_size,
            "digest": f"{algorithm}:{artifact_hasher.hexdigest()}",
        }
        for artifact_path, _, data_start, data_size, _, _, algorithm, artifact_hasher in artifacts
    ]
    if observed_artifacts != identity_record["artifacts"]:
        _reject(
            "artifacts",
            "SafeTensors path, size, or digest differs from the supplied Q1 evidence",
            identity,
        )
    root = {
        "identity": identity,
        "parents": identity_record["parent_ids"],
        "provenance": {
            "revision_kind": material.revision_kind,
            "source_alias": material.source_alias,
            "requested_revision": material.requested_revision,
            "identity_material": identity_record,
            "containers": [
                {"path": artifact_path, "format": "safetensors", "metadata": metadata}
                for artifact_path, _, _, _, metadata, _, _, _ in artifacts
            ],
        },
        "semantic_assets": {
            "processor": identity_record["processor_digest"],
            "template": identity_record["template_digest"],
            "tokenizer": identity_record["tokenizer_digest"],
        },
        "tensor_maps": [tensor_map.record() for tensor_map in sorted(
            tensor_maps, key=lambda tensor_map: tensor_map.semantic_tensor_id
        )],
        "operators": identity_record["operator_set"],
        "plans": [],
        "deltas": [],
    }
    root["integrity_root"] = _root_integrity(
        root, tuple(sorted(locations, key=lambda item: item.page_digest))
    )
    root_payload = canonical_bytes(root)
    root_digest = digest_bytes(root_payload)
    _write_index(cartridge, root_digest, locations)
    root_path = cartridge / "roots" / _content_hex(root_digest, root_digest)
    root_path.parent.mkdir(parents=True, exist_ok=True)
    if root_path.exists():
        if root_path.read_bytes() != root_payload:
            _q57_reject(root_digest, "existing root bytes do not match their name")
    else:
        root_path.write_bytes(root_payload)
    load_root(cartridge, root_digest)
    return root_digest


def page_locations(cartridge: str | Path, root_digest: str) -> tuple[PageLocation, ...]:
    """Return the sorted physical layout for one verified logical root."""

    load_root(cartridge, root_digest)
    return tuple(_read_index(Path(cartridge), root_digest).values())


def repack_segments(
    cartridge: str | Path, root_digest: str, ordered_page_digests: tuple[str, ...]
) -> str:
    """Rewrite every required page in a new physical order without changing the logical root."""

    cartridge = Path(cartridge)
    root = load_root(cartridge, root_digest)
    current = _read_index(cartridge, root_digest)
    required = {
        span["page_digest"]
        for tensor_map in root["tensor_maps"]
        for span in tensor_map["spans"]
    }
    order = tuple(ordered_page_digests)
    if len(order) != len(set(order)) or set(order) != required or set(current) != required:
        _q57_reject(root_digest, "repack order must contain every required page exactly once", "INVALID_REQUEST")
    locations = _write_segments(
        cartridge, ((page_digest, _read_page(cartridge, current[page_digest])) for page_digest in order)
    )
    _write_index(cartridge, root_digest, locations)
    return root_digest


def read_tensor(cartridge: str | Path, root_digest: str, semantic_tensor_id: str) -> bytes:
    """Resolve every Q57 span for one semantic tensor and return its exact source bytes."""

    cartridge = Path(cartridge)
    root = load_root(cartridge, root_digest)
    matches = [
        tensor_map for tensor_map in root["tensor_maps"]
        if tensor_map["semantic_tensor_id"] == semantic_tensor_id
    ]
    if len(matches) != 1:
        _q57_reject(root_digest, f"semantic tensor {semantic_tensor_id!r} is absent or duplicated")
    locations = _read_index(cartridge, root_digest)
    output = bytearray()
    for span in matches[0]["spans"]:
        if span["tensor_offset"] != len(output) or span["page_digest"] not in locations:
            _q57_reject(root_digest, f"semantic tensor {semantic_tensor_id!r} has a discontinuous span map")
        page = _read_page(cartridge, locations[span["page_digest"]])
        end = span["offset"] + span["length"]
        if end > len(page):
            _q57_reject(root_digest, f"semantic tensor {semantic_tensor_id!r} exceeds its content page")
        output.extend(page[span["offset"]:end])
    return bytes(output)


def _transaction_reject(object_id: str, detail: str, code: str = "ROOT_INVALID") -> None:
    raise CassetteError(
        code=code,
        object_id=object_id,
        failed_invariant="Q25/Q60/Q73: durable generation transaction",
        retryability="retryable" if code == "SOURCE_UNAVAILABLE" else "terminal",
        detail=detail,
    )


def _transaction_id(value: object) -> str:
    if not isinstance(value, str) or _TRANSACTION_ID.fullmatch(value) is None:
        _transaction_reject(
            "transaction:unidentified",
            "transaction_id must contain 1-128 letters, digits, periods, underscores, or hyphens",
            "INVALID_REQUEST",
        )
    return value


def _transaction_digest(value: object, object_id: str) -> str:
    if (not isinstance(value, str) or not value.startswith("blake3:") or len(value) != 71
            or not set(value[7:]) <= _HEX):
        _transaction_reject(object_id, "a lowercase BLAKE3 digest is required")
    return value


def _envelope(record: dict) -> tuple[str, bytes]:
    record_digest = digest_bytes(canonical_bytes(record))
    return record_digest, canonical_bytes({"digest": record_digest, "record": record})


def _read_envelope(path: Path, object_id: str, error_code: str) -> dict:
    try:
        payload = path.read_bytes()
        value = json.loads(payload, object_pairs_hook=_unique_object)
        if canonical_bytes(value) != payload:
            raise ValueError("record is not canonical RFC 8785 JSON")
        if not isinstance(value, dict) or set(value) != {"digest", "record"}:
            raise ValueError("envelope must contain exactly digest and record")
        record = value["record"]
        if not isinstance(record, dict):
            raise ValueError("record must be an object")
        if value["digest"] != digest_bytes(canonical_bytes(record)):
            raise ValueError("record digest does not match its canonical bytes")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError, CassetteError) as error:
        _transaction_reject(object_id, f"durable record is unavailable or invalid: {error}", error_code)
    return record


def _fullsync_file(path: Path, object_id: str) -> None:
    command = getattr(fcntl, "F_FULLFSYNC", None)
    if command is None:
        _transaction_reject(object_id, "macOS F_FULLFSYNC is unavailable", "DURABILITY_UNSUPPORTED")
    try:
        with path.open("rb") as handle:
            os.fsync(handle.fileno())
            fcntl.fcntl(handle.fileno(), command)
    except OSError as error:
        _transaction_reject(object_id, f"F_FULLFSYNC failed for {path.name!r}: {error}", "DURABILITY_UNSUPPORTED")


def _sync_directory(path: Path, object_id: str) -> None:
    try:
        descriptor = os.open(path, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    except OSError as error:
        _transaction_reject(object_id, f"directory sync failed for {path.name!r}: {error}", "DURABILITY_UNSUPPORTED")


def _durable_replace(path: Path, payload: bytes, object_id: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _sync_directory(path.parent.parent, object_id)
    temporary = path.with_name(f".{path.name}.pending")
    try:
        temporary.write_bytes(payload)
        if temporary.read_bytes() != payload:
            _transaction_reject(object_id, f"readback changed {temporary.name!r}")
        _fullsync_file(temporary, object_id)
        os.replace(temporary, path)
    except OSError as error:
        _transaction_reject(object_id, f"atomic record replacement failed: {error}", "DURABILITY_UNSUPPORTED")
    _sync_directory(path.parent, object_id)


def _transactions_path(cartridge: Path) -> Path:
    return cartridge / "transactions"


def _journal_path(cartridge: Path, transaction_id: str) -> Path:
    return _transactions_path(cartridge) / f"{transaction_id}.json"


def _candidate_path(cartridge: Path, transaction_id: str) -> Path:
    return _transactions_path(cartridge) / f"{transaction_id}.generation-candidate"


def _restart_material_path(cartridge: Path, digest: str) -> Path:
    return _transactions_path(cartridge) / "material" / _content_hex(digest, digest)


def _generation_path(cartridge: Path, generation: int) -> Path:
    return cartridge / "generations" / f"{generation:020d}.json"


def _training_manifest(resume: dict) -> dict:
    return {field: resume[field] for field in sorted(_TRAINING_MANIFEST_FIELDS)}


def _generation_body(record: dict) -> dict:
    return {
        "generation": record["candidate_generation"],
        "child_id": record["candidate_id"],
        "root_digest": record["candidate_root"],
        "parent_generation": record["expected_parent_generation"],
        "parent_id": record["expected_parent_id"],
        "parent_root": record["expected_parent_root"],
        "training_manifest": _training_manifest(record["resume"]),
        "transaction_id": record["transaction_id"],
    }


def _validate_generation(record: object, object_id: str) -> dict:
    if not isinstance(record, dict) or set(record) != _GENERATION_FIELDS:
        _transaction_reject(object_id, "generation record has an incorrect field set")
    generation = record["generation"]
    parent_generation = record["parent_generation"]
    parent_id = record["parent_id"]
    parent_root = record["parent_root"]
    if type(generation) is not int or not 1 <= generation <= _MAX_JSON_INTEGER:
        _transaction_reject(object_id, "generation must be a positive RFC 8785-safe integer")
    if (len({parent_generation is None, parent_id is None, parent_root is None}) != 1
            or (parent_generation is not None
                and (type(parent_generation) is not int or not 1 <= parent_generation < generation))):
        _transaction_reject(
            object_id, "parent generation, identity, and root must form one earlier generation"
        )
    _transaction_digest(record["child_id"], object_id)
    _transaction_digest(record["root_digest"], object_id)
    if parent_root is not None:
        _transaction_digest(parent_id, object_id)
        _transaction_digest(parent_root, object_id)
    _validate_training_manifest(record["training_manifest"], object_id, "ROOT_INVALID")
    _transaction_id(record["transaction_id"])
    return record


def _counter(field: str, value: object, object_id: str) -> int | None:
    if value is not None and (type(value) is not int or not 0 <= value <= _MAX_JSON_INTEGER):
        _transaction_reject(object_id, f"resume {field} must be null or a nonnegative safe integer")
    return value


def _validate_training_manifest(manifest: object, object_id: str, error_code: str) -> dict:
    def reject(detail: str) -> None:
        _transaction_reject(object_id, detail, error_code)

    if not isinstance(manifest, dict) or set(manifest) != _TRAINING_MANIFEST_FIELDS:
        reject("training manifest has an incorrect field set")
    version = manifest["operation_version"]
    if not isinstance(version, str) or not version or version != version.strip():
        reject("resume operation_version must be exact nonempty text")
    inputs = manifest["input_digests"]
    if not isinstance(inputs, list) or not inputs or len(inputs) != len(set(inputs)):
        reject("resume input_digests must be a nonempty unique list")
    for digest in inputs:
        try:
            _transaction_digest(digest, object_id)
        except CassetteError:
            reject("resume input_digests contain a malformed digest")
    for field in ("random_seed", "optimizer_step", "data_cursor"):
        try:
            _counter(field, manifest[field], object_id)
        except CassetteError:
            reject(f"resume {field} is malformed")
    for field in ("statistics_digest", "rng_state_digest"):
        if manifest[field] is not None:
            try:
                _transaction_digest(manifest[field], object_id)
            except CassetteError:
                reject(f"resume {field} is malformed")
    loss_scale = manifest["loss_scale"]
    if loss_scale is not None and (not isinstance(loss_scale, str) or not loss_scale):
        reject("resume loss_scale must be null or exact numeric text")
    return manifest


def _validate_resume(resume: object, object_id: str, error_code: str) -> dict:
    def reject(detail: str) -> None:
        _transaction_reject(object_id, detail, error_code)

    if not isinstance(resume, dict) or set(resume) != _RESUME_FIELDS:
        reject("journal resume material has an incorrect field set")
    _validate_training_manifest(_training_manifest(resume), object_id, error_code)
    pages = resume["page_results"]
    if (not isinstance(pages, list) or not pages
            or any(not isinstance(page, dict) or set(page) != {"page_digest", "length"}
                   or type(page["length"]) is not int or not 0 < page["length"] <= PAGE_BYTES
                   for page in pages)
            or pages != sorted(pages, key=lambda page: page["page_digest"])
            or len({page["page_digest"] for page in pages}) != len(pages)):
        reject("resume page_results must be one sorted record per candidate page")
    for page in pages:
        try:
            _transaction_digest(page["page_digest"], object_id)
        except CassetteError:
            reject("resume page_results contain a malformed digest")
    return resume


def _restart_material_digest(payload: object, field: str, object_id: str) -> str | None:
    if payload is None:
        return None
    if not isinstance(payload, bytes):
        _transaction_reject(object_id, f"TransactionContext {field} must be bytes", "INVALID_REQUEST")
    return digest_bytes(payload)


def _write_restart_material(cartridge: Path, payload: bytes, digest: str, object_id: str) -> None:
    path = _restart_material_path(cartridge, digest)
    if path.exists():
        try:
            observed = path.read_bytes()
        except OSError as error:
            _transaction_reject(object_id, f"restart material is unavailable: {error}", "SOURCE_UNAVAILABLE")
        if digest_bytes(observed) != digest:
            _transaction_reject(object_id, "restart material does not match its identity", "SOURCE_UNAVAILABLE")
        return
    _durable_replace(path, payload, object_id)


def _read_restart_material(
    cartridge: Path, digest: str | None, field: str, object_id: str
) -> bytes | None:
    if digest is None:
        return None
    path = _restart_material_path(cartridge, digest)
    try:
        payload = path.read_bytes()
    except OSError as error:
        _transaction_reject(object_id, f"resume {field} bytes are unavailable: {error}", "SOURCE_UNAVAILABLE")
    if digest_bytes(payload) != digest:
        _transaction_reject(object_id, f"resume {field} bytes do not match their digest", "SOURCE_UNAVAILABLE")
    return payload


def _resume_record(
    cartridge: Path,
    candidate_root: str,
    context: TransactionContext | None,
    object_id: str,
    *,
    persist_material: bool,
) -> dict:
    if context is not None and not isinstance(context, TransactionContext):
        _transaction_reject(object_id, "TransactionContext required", "INVALID_REQUEST")
    context = context or TransactionContext("store-generation-v1", (candidate_root,))
    if not isinstance(context.input_digests, tuple):
        _transaction_reject(object_id, "TransactionContext input_digests must be a tuple", "INVALID_REQUEST")
    statistics_digest = _restart_material_digest(context.statistics, "statistics", object_id)
    rng_state_digest = _restart_material_digest(context.rng_state, "rng_state", object_id)
    if persist_material:
        if statistics_digest is not None:
            _write_restart_material(cartridge, context.statistics, statistics_digest, object_id)
        if rng_state_digest is not None:
            _write_restart_material(cartridge, context.rng_state, rng_state_digest, object_id)
    resume = {
        "operation_version": context.operation_version,
        "input_digests": list(context.input_digests),
        "random_seed": context.random_seed,
        "statistics_digest": statistics_digest,
        "page_results": [
            {"page_digest": location.page_digest, "length": location.length}
            for location in sorted(
                _read_index(cartridge, candidate_root).values(), key=lambda item: item.page_digest
            )
        ],
        "optimizer_step": context.optimizer_step,
        "rng_state_digest": rng_state_digest,
        "data_cursor": context.data_cursor,
        "loss_scale": context.loss_scale,
    }
    return _validate_resume(resume, object_id, "INVALID_REQUEST")


def _validate_transaction(record: object, object_id: str) -> dict:
    if not isinstance(record, dict) or set(record) != _TRANSACTION_FIELDS:
        _transaction_reject(object_id, "journal record has an incorrect field set", "SOURCE_UNAVAILABLE")
    step = record["step"]
    if (type(step) is not int or not 0 <= step < len(_TRANSACTION_STATES)
            or record["state"] != _TRANSACTION_STATES[step]):
        _transaction_reject(object_id, "journal step and Q25 state disagree", "SOURCE_UNAVAILABLE")
    dependency_cursor = record["dependency_cursor"]
    pointer_cursor = record["pointer_cursor"]
    if (type(dependency_cursor) is not int
            or not 0 <= dependency_cursor <= _MAX_JSON_INTEGER
            or (step < 5 and dependency_cursor != 0)):
        _transaction_reject(object_id, "journal dependency cursor is invalid", "SOURCE_UNAVAILABLE")
    if (type(pointer_cursor) is not int or pointer_cursor < 0
            or (step < 7 and pointer_cursor != 0)
            or (step == 7 and pointer_cursor not in {1, 2, 3})
            or (step == 8 and pointer_cursor != 3)):
        _transaction_reject(object_id, "journal pointer cursor is invalid", "SOURCE_UNAVAILABLE")
    _transaction_id(record["transaction_id"])
    if record["dependency_order"] != list(_DEPENDENCY_ORDER):
        _transaction_reject(object_id, "journal dependency order is not Q73's order", "SOURCE_UNAVAILABLE")
    _validate_resume(record["resume"], object_id, "SOURCE_UNAVAILABLE")
    generation = _validate_generation(_generation_body(record), object_id)
    expected_digest = digest_bytes(canonical_bytes(generation))
    if record["generation_record_digest"] != expected_digest:
        _transaction_reject(object_id, "journal does not bind its candidate generation", "SOURCE_UNAVAILABLE")
    return record


def _load_transaction(cartridge: Path, transaction_id: str) -> dict:
    object_id = f"transaction:{_transaction_id(transaction_id)}"
    record = _validate_transaction(
        _read_envelope(_journal_path(cartridge, transaction_id), object_id, "SOURCE_UNAVAILABLE"),
        object_id,
    )
    _read_restart_material(
        cartridge, record["resume"]["statistics_digest"], "statistics", object_id
    )
    _read_restart_material(
        cartridge, record["resume"]["rng_state_digest"], "rng_state", object_id
    )
    return record


def _write_transaction(cartridge: Path, record: dict) -> None:
    transaction_id = record["transaction_id"]
    object_id = f"transaction:{transaction_id}"
    _validate_transaction(record, object_id)
    _read_restart_material(
        cartridge, record["resume"]["statistics_digest"], "statistics", object_id
    )
    _read_restart_material(
        cartridge, record["resume"]["rng_state_digest"], "rng_state", object_id
    )
    _, payload = _envelope(record)
    _durable_replace(_journal_path(cartridge, transaction_id), payload, object_id)


def _public_transaction(record: dict) -> TransactionState:
    return TransactionState(
        record["transaction_id"], record["state"], record["step"],
        record["candidate_generation"], record["candidate_root"],
        record["dependency_cursor"], record["pointer_cursor"],
    )


def _load_generation(path: Path) -> dict:
    match = _GENERATION_NAME.fullmatch(path.name)
    object_id = f"generation:{path.name}"
    if match is None:
        _transaction_reject(object_id, "generation filename is not a fixed-width integer")
    record = _validate_generation(_read_envelope(path, object_id, "ROOT_INVALID"), object_id)
    if record["generation"] != int(match.group(1)):
        _transaction_reject(object_id, "generation filename and record disagree")
    return record


def _generation_files(cartridge: Path) -> tuple[Path, ...]:
    directory = cartridge / "generations"
    if not directory.exists():
        return ()
    files = []
    for path in directory.iterdir():
        if path.name.startswith("."):
            continue
        if not path.is_file() or _GENERATION_NAME.fullmatch(path.name) is None:
            _transaction_reject(f"generation:{path.name}", "generation directory contains an unknown object")
        files.append(path)
    return tuple(sorted(files, reverse=True))


def _verify_dependency_paths(cartridge: Path, root_digest: str) -> tuple[dict, tuple[Path, ...]]:
    root = load_root(cartridge, root_digest)
    locations = _read_index(cartridge, root_digest)
    segment_ids = sorted({location.segment_id for location in locations.values()})
    segment_paths = tuple(
        cartridge / "segments" / _content_hex(segment_id, segment_id)
        for segment_id in segment_ids
    )
    for segment_id, path in zip(segment_ids, segment_paths, strict=True):
        try:
            observed = _file_digest(path)
        except OSError as error:
            _q57_reject(segment_id, f"segment is unavailable: {error}", "PAGE_CORRUPT")
        if observed != segment_id:
            _q57_reject(segment_id, "segment bytes do not match their identity", "PAGE_CORRUPT")
    for location in sorted(locations.values(), key=lambda item: item.page_digest):
        _read_page(cartridge, location)
    return root, (*segment_paths, _index_path(cartridge, root_digest),
                  cartridge / "roots" / _content_hex(root_digest, root_digest))


def _semantic_manifest(root: dict) -> dict:
    return {
        "root_identity": root["identity"],
        "parents": root["parents"],
        "semantic_assets": root["semantic_assets"],
        "tensor_maps": root["tensor_maps"],
        "operators": root["operators"],
        "deltas": root["deltas"],
    }


def _generation_identity(
    root: dict,
    parent_id: str | None,
    training_manifest: dict,
    ordered_page_digests: list[str],
) -> str:
    return digest_bytes(canonical_bytes({
        "parent_id": parent_id,
        "training_manifest": training_manifest,
        "ordered_page_or_delta_digests": ordered_page_digests,
        "semantic_manifest": _semantic_manifest(root),
    }))


def _verify_generation_binding(cartridge: Path, record: dict, root: dict) -> None:
    object_id = f"generation:{record['generation']}"
    if record["parent_generation"] is not None:
        parent = _load_generation(_generation_path(cartridge, record["parent_generation"]))
        if (parent["child_id"] != record["parent_id"]
                or parent["root_digest"] != record["parent_root"]):
            _transaction_reject(object_id, "generation parent binding is inconsistent")
    pages = sorted(_read_index(cartridge, record["root_digest"]), key=str)
    expected = _generation_identity(
        root, record["parent_id"], record["training_manifest"], pages
    )
    if expected != record["child_id"]:
        _transaction_reject(object_id, "child identity does not match the Q73 preimage")


def _valid_generations(cartridge: Path, verify_dependencies: bool) -> tuple[GenerationPin, ...]:
    pins = []
    failures = []
    for path in _generation_files(cartridge):
        try:
            record = _load_generation(path)
            root = (_verify_dependency_paths(cartridge, record["root_digest"])[0]
                    if verify_dependencies else load_root(cartridge, record["root_digest"]))
            _verify_generation_binding(cartridge, record, root)
            pins.append(GenerationPin(record["generation"], record["child_id"], record["root_digest"]))
        except CassetteError as error:
            failures.append(error)
    if not pins and failures:
        raise failures[0]
    return tuple(pins)


def pin_generation(cartridge: str | Path) -> GenerationPin | None:
    """Pin the highest callable generation without allowing a later commit to change this reader."""

    generations = _valid_generations(Path(cartridge), False)
    return generations[0] if generations else None


def recover_generation(cartridge: str | Path) -> GenerationPin | None:
    """Rehash every dependency and select the highest valid generation after mount or process death."""

    generations = _valid_generations(Path(cartridge), True)
    return generations[0] if generations else None


def _next_generation(cartridge: Path) -> int:
    files = _generation_files(cartridge)
    return int(files[0].stem) + 1 if files else 1


def begin_generation(
    cartridge: str | Path,
    transaction_id: str,
    candidate_root: str,
    *,
    expected_parent_root: str | None,
    context: TransactionContext | None = None,
) -> TransactionState:
    """Durably prepare one idempotent Q25/Q60 transaction against an exact parent generation."""

    cartridge = Path(cartridge)
    transaction_id = _transaction_id(transaction_id)
    object_id = f"transaction:{transaction_id}"
    candidate_root = _transaction_digest(candidate_root, object_id)
    candidate = load_root(cartridge, candidate_root)
    journal = _journal_path(cartridge, transaction_id)
    if journal.exists():
        record = _load_transaction(cartridge, transaction_id)
        requested_resume = (
            _resume_record(
                cartridge, candidate_root, context, object_id, persist_material=False
            )
            if context is not None else None
        )
        if (record["candidate_root"] != candidate_root
                or record["expected_parent_root"] != expected_parent_root
                or (requested_resume is not None and record["resume"] != requested_resume)):
            _transaction_reject(
                object_id,
                "idempotency key names different candidate, parent, or restart material",
                "IDEMPOTENCY_CONFLICT",
            )
        return _public_transaction(record)

    active = recover_generation(cartridge)
    active_root = active.root_digest if active else None
    if expected_parent_root != active_root:
        _transaction_reject(
            f"transaction:{transaction_id}",
            f"expected parent {expected_parent_root!r}, found {active_root!r}",
            "IDEMPOTENCY_CONFLICT",
        )
    resume = _resume_record(
        cartridge, candidate_root, context, object_id, persist_material=True
    )
    generation = _next_generation(cartridge)
    parent_id = active.child_id if active else None
    candidate_id = _generation_identity(
        candidate,
        parent_id,
        _training_manifest(resume),
        [page["page_digest"] for page in resume["page_results"]],
    )
    record = {
        "transaction_id": transaction_id,
        "step": 0,
        "state": _TRANSACTION_STATES[0],
        "candidate_generation": generation,
        "candidate_root": candidate_root,
        "candidate_id": candidate_id,
        "expected_parent_generation": active.generation if active else None,
        "expected_parent_id": parent_id,
        "expected_parent_root": active_root,
        "generation_record_digest": "",
        "dependency_order": list(_DEPENDENCY_ORDER),
        "dependency_cursor": 0,
        "pointer_cursor": 0,
        "resume": resume,
    }
    record["generation_record_digest"] = digest_bytes(canonical_bytes(_generation_body(record)))
    _write_transaction(cartridge, record)
    return _public_transaction(record)


def transaction_state(cartridge: str | Path, transaction_id: str) -> TransactionState:
    """Read one journal only after its canonical bytes and bound candidate verify."""

    return _public_transaction(_load_transaction(Path(cartridge), transaction_id))


def load_transaction_context(
    cartridge: str | Path, transaction_id: str
) -> TransactionContext:
    """Reconstruct exact Q25/Q60 restart state only from verified cartridge objects."""

    cartridge = Path(cartridge)
    record = _load_transaction(cartridge, transaction_id)
    resume = record["resume"]
    object_id = f"transaction:{record['transaction_id']}"
    return TransactionContext(
        resume["operation_version"],
        tuple(resume["input_digests"]),
        random_seed=resume["random_seed"],
        statistics=_read_restart_material(
            cartridge, resume["statistics_digest"], "statistics", object_id
        ),
        optimizer_step=resume["optimizer_step"],
        rng_state=_read_restart_material(
            cartridge, resume["rng_state_digest"], "rng_state", object_id
        ),
        data_cursor=resume["data_cursor"],
        loss_scale=resume["loss_scale"],
    )


def _candidate_payload(record: dict) -> bytes:
    record_digest, payload = _envelope(_generation_body(record))
    if record_digest != record["generation_record_digest"]:
        _transaction_reject(f"transaction:{record['transaction_id']}", "candidate digest changed")
    return payload


def _write_candidate(cartridge: Path, record: dict) -> Path:
    path = _candidate_path(cartridge, record["transaction_id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_bytes(_candidate_payload(record))
    except OSError as error:
        _transaction_reject(f"transaction:{record['transaction_id']}", f"candidate write failed: {error}")
    return path


def _ensure_candidate(cartridge: Path, record: dict) -> Path:
    path = _candidate_path(cartridge, record["transaction_id"])
    expected = _candidate_payload(record)
    try:
        observed = path.read_bytes()
    except OSError:
        observed = None
    if observed != expected:
        path = _write_candidate(cartridge, record)
        try:
            observed = path.read_bytes()
        except OSError as error:
            _transaction_reject(f"transaction:{record['transaction_id']}", f"candidate readback failed: {error}")
    if observed != expected:
        _transaction_reject(f"transaction:{record['transaction_id']}", "candidate readback digest changed")
    return path


def _publish_candidate(cartridge: Path, record: dict, repair: bool = False) -> Path:
    destination = _generation_path(cartridge, record["candidate_generation"])
    expected = _candidate_payload(record)
    if destination.exists():
        if destination.read_bytes() != expected:
            _transaction_reject(f"generation:{record['candidate_generation']}", "generation collision")
        return destination
    candidate = _candidate_path(cartridge, record["transaction_id"])
    if repair:
        candidate = _ensure_candidate(cartridge, record)
        _fullsync_file(candidate, f"transaction:{record['transaction_id']}")
    else:
        try:
            observed = candidate.read_bytes()
        except OSError as error:
            _transaction_reject(
                f"transaction:{record['transaction_id']}", f"candidate is unavailable: {error}"
            )
        if observed != expected:
            _transaction_reject(
                f"transaction:{record['transaction_id']}", "candidate changed after its durable hash"
            )
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.rename(candidate, destination)
    except OSError as error:
        _transaction_reject(
            f"transaction:{record['transaction_id']}",
            f"atomic generation publication failed: {error}",
            "DURABILITY_UNSUPPORTED",
        )
    return destination


def advance_generation(cartridge: str | Path, transaction_id: str) -> TransactionState:
    """Execute one idempotent Q25 transition; a fresh process may execute the next transition."""

    cartridge = Path(cartridge)
    record = _load_transaction(cartridge, transaction_id)
    step = record["step"]
    object_id = f"transaction:{record['transaction_id']}"
    if step == len(_TRANSACTION_STATES) - 1:
        generation = _load_generation(
            _generation_path(cartridge, record["candidate_generation"])
        )
        root, _ = _verify_dependency_paths(cartridge, generation["root_digest"])
        _verify_generation_binding(cartridge, generation, root)
        return _public_transaction(record)
    if step == 0:
        _write_candidate(cartridge, record)
    elif step == 1:
        _ensure_candidate(cartridge, record)
    elif step == 2:
        _fullsync_file(_ensure_candidate(cartridge, record), object_id)
    elif step == 3:
        _verify_dependency_paths(cartridge, record["candidate_root"])
    elif step == 4:
        record = {**record, "step": 5, "state": _TRANSACTION_STATES[5]}
        _write_transaction(cartridge, record)
        return _public_transaction(record)
    elif step == 5:
        _, paths = _verify_dependency_paths(cartridge, record["candidate_root"])
        directories = tuple(dict.fromkeys(path.parent for path in paths))
        boundaries = (*(("file", path) for path in paths),
                      *(("directory", path) for path in directories))
        cursor = record["dependency_cursor"]
        if cursor < len(boundaries):
            kind, path = boundaries[cursor]
            (_fullsync_file if kind == "file" else _sync_directory)(path, object_id)
            record = {**record, "dependency_cursor": cursor + 1}
        elif cursor == len(boundaries):
            _verify_dependency_paths(cartridge, record["candidate_root"])
            record = {**record, "dependency_cursor": cursor + 1}
        elif cursor == len(boundaries) + 1:
            active = pin_generation(cartridge)
            if ((active.root_digest if active else None) != record["expected_parent_root"]
                    and (active is None or active.generation != record["candidate_generation"])):
                _transaction_reject(object_id, "callable parent changed before generation publication")
            _publish_candidate(cartridge, record)
            record = {**record, "step": 6, "state": _TRANSACTION_STATES[6]}
        else:
            _transaction_reject(object_id, "journal dependency cursor exceeds its verified frontier")
        _write_transaction(cartridge, record)
        return _public_transaction(record)
    elif step == 6:
        destination = _publish_candidate(cartridge, record, repair=True)
        _fullsync_file(destination, object_id)
        record = {**record, "step": 7, "state": _TRANSACTION_STATES[7], "pointer_cursor": 1}
        _write_transaction(cartridge, record)
        return _public_transaction(record)
    elif step == 7:
        destination = _generation_path(cartridge, record["candidate_generation"])
        if record["pointer_cursor"] == 1:
            _sync_directory(destination.parent, object_id)
            record = {**record, "pointer_cursor": 2}
        elif record["pointer_cursor"] == 2:
            _sync_directory(destination.parent.parent, object_id)
            record = {**record, "pointer_cursor": 3}
        else:
            generation = _load_generation(destination)
            root, _ = _verify_dependency_paths(cartridge, generation["root_digest"])
            _verify_generation_binding(cartridge, generation, root)
            record = {**record, "step": 8, "state": _TRANSACTION_STATES[8]}
        _write_transaction(cartridge, record)
        return _public_transaction(record)
    record = {**record, "step": step + 1, "state": _TRANSACTION_STATES[step + 1]}
    _write_transaction(cartridge, record)
    return _public_transaction(record)


def commit_generation(
    cartridge: str | Path,
    transaction_id: str,
    candidate_root: str,
    *,
    expected_parent_root: str | None,
    context: TransactionContext | None = None,
) -> GenerationPin:
    """Resume until the exact candidate is a fully synced immutable callable generation."""

    state = begin_generation(
        cartridge,
        transaction_id,
        candidate_root,
        expected_parent_root=expected_parent_root,
        context=context,
    )
    while state.state != "COMMITTED":
        state = advance_generation(cartridge, transaction_id)
    advance_generation(cartridge, transaction_id)
    record = _load_transaction(Path(cartridge), transaction_id)
    return GenerationPin(record["candidate_generation"], record["candidate_id"], candidate_root)


def rollback_generation(cartridge: str | Path, transaction_id: str) -> GenerationPin:
    """Publish the prior valid root as a new generation while retaining both immutable revisions."""

    cartridge = Path(cartridge)
    generations = _valid_generations(cartridge, True)
    if len(generations) < 2:
        _transaction_reject(
            f"transaction:{transaction_id}", "rollback requires a current and prior valid generation",
            "INVALID_REQUEST",
        )
    current, prior = generations[:2]
    return commit_generation(
        cartridge, transaction_id, prior.root_digest, expected_parent_root=current.root_digest
    )


def collect_garbage(cartridge: str | Path) -> tuple[str, ...]:
    """Remove only unreachable transaction temporaries; retained generations and reader pins survive."""

    cartridge = Path(cartridge)
    if recover_generation(cartridge) is None:
        return ()
    directory = _transactions_path(cartridge)
    if not directory.exists():
        return ()
    records = [_load_transaction(cartridge, path.stem) for path in sorted(directory.glob("*.json"))]
    live = {
        _candidate_path(cartridge, record["transaction_id"])
        for record in records
        if record["step"] < 6
    }
    removed = []
    for path in sorted(item for item in directory.rglob("*") if item.is_file()):
        is_atomic_temporary = path.name.startswith(".") and path.name.endswith(".pending")
        is_candidate = path.parent == directory and path.name.endswith(".generation-candidate")
        if path not in live and (is_atomic_temporary or is_candidate):
            try:
                path.unlink()
            except OSError as error:
                _transaction_reject(f"transaction:{path.name}", f"temporary reclamation failed: {error}")
            removed.append(path.name)
    if removed:
        _sync_directory(directory, "transactions:garbage-collection")
    return tuple(removed)
