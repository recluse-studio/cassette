# store.py — canonical digest, model identity, and provenance authority (Q1/Q32/Q57); depends on errors.py.
"""Mint one identity only from a complete, immutable, RFC 8785-canonical Q1 record.

Source adapters may accept mutable aliases, but they must return a canonical locator and a typed
immutable revision digest. Requested aliases remain provenance; they never enter the identity.
Cassette-owned identities and canonical content use BLAKE3 through this module alone.
"""

from __future__ import annotations

from dataclasses import dataclass

from blake3 import blake3
import rfc8785

from errors import CassetteError

_DIGEST_HEX_LENGTHS = {"blake3": 64, "sha256": 64, "git-sha1": 40}
_HEX = frozenset("0123456789abcdef")
_REVISION_KINDS = frozenset({"source", "executable", "tuned", "exported"})
_MAX_JSON_INTEGER = 2**53 - 1


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


def model_identity(material: IdentityTuple) -> str:
    """Return I only when P(I) is complete, immutable, and correctly bound to its revision kind."""

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
        "format_versions": sorted(formats),
        "tensor_index_digest": _digest("tensor_index_digest", material.tensor_index_digest, object_id),
        "config_digest": _digest("config_digest", material.config_digest, object_id),
        "architecture": _text("architecture", material.architecture, object_id),
        "operator_set": sorted(operators),
        "tokenizer_digest": _digest("tokenizer_digest", material.tokenizer_digest, object_id),
        "processor_digest": _digest("processor_digest", material.processor_digest, object_id),
        "template_digest": _digest("template_digest", material.template_digest, object_id),
        "precision_scheme": _text("precision_scheme", material.precision_scheme, object_id),
        "license_digest": _digest("license_digest", material.license_digest, object_id),
        "parent_ids": parents,
        "transform_manifest_digest": transform,
    }
    return digest_bytes(canonical_bytes(canonical))
