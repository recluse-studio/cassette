# store.py — canonical identity, content pages, segments, and tensor maps (Q1/Q32/Q57); depends on errors.py, schema.
"""Own model identity and the representation-independent Q57 cartridge store.

Source adapters may accept mutable aliases, but they must return a canonical locator and a typed
immutable revision digest. Requested aliases remain provenance; they never enter the identity.
Cassette-owned identities and canonical content use BLAKE3 through this module alone. SafeTensors
payloads enter bounded pages and segments; tensor maps retain their semantic byte ranges while a
separate fixed-record index owns physical placement.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
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
