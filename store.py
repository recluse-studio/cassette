# store.py — canonical model-revision identity authority (Q1; Q32); depends on errors.py.
"""Name one complete immutable model revision from Q1's exact semantic tuple.

Source adapters resolve aliases to a canonical source kind, locator, and immutable revision before
calling this module. Alias spelling is therefore never identity material. Artifact order, format
order, operator order, and parent order are canonicalized because their order has no semantic force.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from errors import CassetteError


@dataclass(frozen=True)
class ArtifactIdentity:
    """One Q1 artifact: canonical source path, exact byte count, and authoritative digest."""

    path: str
    size: int
    digest: str


@dataclass(frozen=True)
class IdentityTuple:
    """The complete Q1 material for one source, executable, tuned, or exported revision."""

    source_kind: str
    locator: str
    immutable_revision: str
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
    transform_manifest_digest: str


def _reject(field: str, reason: str) -> None:
    raise CassetteError(
        code="PROVENANCE_VIOLATION",
        object_id="model:unidentified",
        failed_invariant="Q1: complete immutable identity tuple required",
        retryability="terminal",
        detail=f"{field}: {reason}",
    )


def _text(field: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        _reject(field, "nonempty text required")
    return value


def _texts(field: str, values: object, *, empty: bool = False) -> tuple[str, ...]:
    if not isinstance(values, (list, tuple, set, frozenset)):
        _reject(field, "a collection of text values is required")
    result = tuple(sorted({_text(f"{field}[]", value) for value in values}))
    if not empty and not result:
        _reject(field, "at least one value is required")
    return result


def model_identity(material: IdentityTuple) -> str:
    """Return the stable Q1 identity or reject incomplete or mutable-only material."""

    if not isinstance(material, IdentityTuple):
        _reject("identity_tuple", "IdentityTuple required")
    if not isinstance(material.immutable_revision, str) or not material.immutable_revision.strip():
        _reject("immutable_revision", "absent; a mutable locator cannot identify a model revision")

    scalar_names = (
        "source_kind", "locator", "tensor_index_digest", "config_digest", "architecture",
        "tokenizer_digest", "processor_digest", "template_digest", "precision_scheme",
        "license_digest", "transform_manifest_digest",
    )
    scalars = {name: _text(name, getattr(material, name)) for name in scalar_names}

    if not isinstance(material.artifacts, (list, tuple)) or not material.artifacts:
        _reject("artifacts", "at least one artifact is required")
    artifacts = []
    for artifact in material.artifacts:
        if not isinstance(artifact, ArtifactIdentity):
            _reject("artifacts[]", "ArtifactIdentity required")
        if type(artifact.size) is not int or not 0 <= artifact.size < 2**64:
            _reject("artifacts[].size", "an unsigned 64-bit byte count is required")
        artifacts.append((_text("artifacts[].path", artifact.path), artifact.size,
                          _text("artifacts[].digest", artifact.digest)))
    if len({path for path, _, _ in artifacts}) != len(artifacts):
        _reject("artifacts[].path", "paths must be unique")

    if not isinstance(material.format_versions, (list, tuple)) or not material.format_versions:
        _reject("format_versions", "at least one name and version pair is required")
    formats = []
    for item in material.format_versions:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            _reject("format_versions[]", "a name and version pair is required")
        formats.append((_text("format_versions[].name", item[0]),
                        _text("format_versions[].version", item[1])))
    if len({name for name, _ in formats}) != len(formats):
        _reject("format_versions[].name", "names must be unique")

    canonical = (
        "cassette-model-identity-v1", scalars["source_kind"], scalars["locator"],
        material.immutable_revision, sorted(artifacts), sorted(formats),
        scalars["tensor_index_digest"], scalars["config_digest"], scalars["architecture"],
        _texts("operator_set", material.operator_set), scalars["tokenizer_digest"],
        scalars["processor_digest"], scalars["template_digest"],
        scalars["precision_scheme"], scalars["license_digest"],
        _texts("parent_ids", material.parent_ids, empty=True),
        scalars["transform_manifest_digest"],
    )
    encoded = json.dumps(canonical, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"
