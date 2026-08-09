# sources.py — source resolution, preflight, and verified transfer (Q8/Q9/Q50-Q52/Q56); depends on errors.py, schema, store.py.
"""Normalize source evidence, decide compatibility, and copy bytes into cartridge extents."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import fcntl
from http.client import IncompleteRead
from ipaddress import ip_address
import json
import os
import re
import stat
from typing import Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from errors import CassetteError
from schema.validator import validate
from store import (
    CapacityPhase,
    CapacityReservation,
    artifact_hasher,
    artifact_hash_state,
    canonical_bytes,
    capacity_requirement,
    digest_bytes,
    resumable_artifact_hasher,
    resume_artifact_hasher,
)

_CONTROL_BYTES = 8 * 1024 * 1024
_DIGEST = re.compile(r"(?P<algorithm>blake3|sha256|git-sha1):(?P<hex>[0-9a-f]+)")
_DIGEST_LENGTH = {"blake3": 64, "sha256": 64, "git-sha1": 40}
_SENSITIVE_HEADERS = frozenset({"authorization", "x-cassette-license-acceptance"})
_TRANSFER_CHUNK_BYTES = 4 * 1024 * 1024
_TRANSFER_PARALLEL_RANGES = 2
_TRANSFER_SLOT_BYTES = 64 * 1024
_TRANSFER_RECORD_BYTES = 33
_TRANSFER_RECORDS_OFFSET = 2 * _TRANSFER_SLOT_BYTES
_MAX_FILE_OFFSET = (1 << 63) - 1
_TRANSFER_HEADER_FIELDS = frozenset({
    "version", "generation", "artifact_id", "source_revision", "object_size",
    "validator", "expected_digest", "chunk_bytes", "chunk_count",
    "chunk_manifest_digest", "completed_count", "contiguous_source_hash_offset",
    "serialized_hash_state", "contiguous_source_hash_digest", "chunk_records_digest",
})
_TRANSFER_IDENTITY_FIELDS = frozenset({
    "version", "artifact_id", "source_revision", "object_size", "validator",
    "expected_digest", "chunk_bytes", "chunk_count", "chunk_manifest_digest",
})
_METADATA_TRUST = {"ABSENT": 0, "DECLARED": 1, "PARSED": 2, "EVIDENCE_DIGESTED": 2}
_PREFLIGHT_CLASSES = frozenset({
    "SUPPORTED", "SUPPORTED_AFTER_PREPARATION", "METADATA_INSUFFICIENT", "UNSUPPORTED",
})
_PREFLIGHT_REQUIRED = frozenset({
    "identity", "total_bytes", "artifact_count", "artifact_digests", "format",
    "architecture", "total_parameters", "active_parameters", "dtype_quantization",
    "context", "modalities", "operators", "custom_code", "tokenizer", "template",
    "license", "gating", "source_validators",
})
_PREFLIGHT_STRONG = frozenset({
    "format", "architecture", "total_parameters", "active_parameters",
    "dtype_quantization", "context", "modalities", "operators", "custom_code", "tokenizer",
    "processor", "template",
})


@dataclass(frozen=True, slots=True)
class Artifact:
    """One immutable source object with the exact range-read authority required by Q9."""

    path: str
    size: int
    digest: str
    range_uri: str
    validator: str

    def record(self) -> dict:
        return {
            "path": self.path,
            "size": self.size,
            "digest": self.digest,
            "range_uri": self.range_uri,
        }


@dataclass(frozen=True, slots=True)
class ResolvedSource:
    """The normalized immutable result; credential_ref is an opaque lookup key, never a secret."""

    source_kind: str
    locator: str
    immutable_revision: str
    identity: str
    artifacts: tuple[Artifact, ...]
    metadata_assets: tuple[Artifact, ...]
    auth_scope: str
    license_digest: str
    credential_ref: str | None
    license_acceptance_ref: str | None

    def record(self) -> dict:
        """Return the exact durable Q9 result without authentication material."""
        return {
            "immutable_revision": self.immutable_revision,
            "artifacts": [artifact.record() for artifact in self.artifacts],
            "metadata_assets": [artifact.record() for artifact in self.metadata_assets],
            "auth_scope": self.auth_scope,
            "license_digest": self.license_digest,
        }


@dataclass(frozen=True, slots=True)
class Requirements:
    """Source requirements translated without retaining the resolved credential."""

    auth_scope: str
    credential_required: bool
    license_digest: str
    license_acceptance_required: bool

    def record(self) -> dict:
        return {
            "auth_scope": self.auth_scope,
            "credential_required": self.credential_required,
            "license_digest": self.license_digest,
            "license_acceptance_required": self.license_acceptance_required,
        }


@dataclass(frozen=True, slots=True)
class MetadataProbe:
    """One bounded source range that can decide named absent Q50 fields."""

    fields: tuple[str, ...]
    artifact_path: str
    offset: int
    length: int

    def record(self) -> dict:
        return {
            "kind": "METADATA_RANGE",
            "fields": list(self.fields),
            "artifact_path": self.artifact_path,
            "offset": self.offset,
            "length": self.length,
        }


@dataclass(frozen=True, slots=True)
class CompatibilityProfile:
    """General class bounds supplied to Q56; no current-device inspection occurs here."""

    device_bytes: int
    allocatable_verified_free: int
    memory_bytes: int
    supported_operators: frozenset[str]
    supported_modalities: frozenset[str]
    native_formats: frozenset[str]
    preparation_formats: frozenset[str]
    training_tiers: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PreflightDecision:
    """The complete Q8/Q56 decision with unknowns retained as None, never defaults."""

    classification: str
    source_identity: str | None
    trust: str
    total_bytes: int | None
    peak_bytes: int | None
    architecture: str | None
    operators: tuple[str, ...] | None
    precision: object | None
    total_parameters: int | None
    active_parameters: int | None
    context: object | None
    assets: tuple[dict, ...]
    license: str | None
    training_tiers: tuple[str, ...]
    mode_candidates: tuple[str, ...]
    reasons: tuple[str, ...]
    required_bytes: int | None
    memory_bound: int | None
    storage_bound: int
    deferred_checks: tuple[dict, ...]
    evidence: dict

    def record(self) -> dict:
        """Return the machine Q8/Q56 record without retaining caller-owned containers."""
        record = {
            "class": self.classification,
            "source_identity": self.source_identity,
            "trust": self.trust,
            "total_bytes": self.total_bytes,
            "peak_bytes": self.peak_bytes,
            "architecture": self.architecture,
            "operators": None if self.operators is None else list(self.operators),
            "precision": self.precision,
            "total_parameters": self.total_parameters,
            "active_parameters": self.active_parameters,
            "context": self.context,
            "assets": list(self.assets),
            "license": self.license,
            "training_tiers": list(self.training_tiers),
            "mode_candidates": list(self.mode_candidates),
            "reasons": list(self.reasons),
            "required_bytes": self.required_bytes,
            "memory_bound": self.memory_bound,
            "storage_bound": self.storage_bound,
            "deferred_checks": list(self.deferred_checks),
            "evidence": self.evidence,
        }
        return json.loads(canonical_bytes(record))


@dataclass(frozen=True, slots=True)
class TransferExtent:
    """One pre-opened cartridge extent; the store owns its path and allocation."""

    fd: int
    offset: int
    length: int
    operation_id: str


@dataclass(frozen=True, slots=True)
class TransferChunk:
    """One Q51 fixed chunk after source and local verification."""

    artifact_id: str
    offset: int
    length: int
    blake3_digest: str
    state: str = "VERIFIED"


@dataclass(frozen=True, slots=True)
class PartialState:
    """The durable Q51 resume proof reconstructed from its active header and chunk records."""

    source_revision: str
    object_size: int
    validator: str
    completed_interval_set: tuple[tuple[int, int], ...]
    chunk_digests: tuple[str, ...]
    contiguous_source_hash_offset: int
    serialized_hash_state: str


@dataclass(frozen=True, slots=True)
class _Wire:
    revision: tuple[str, ...]
    revision_prefix: str
    identity: tuple[str, ...]
    artifacts: tuple[str, ...]
    metadata_assets: tuple[str, ...]
    artifact_path: tuple[str, ...]
    artifact_size: tuple[str, ...]
    artifact_digest: tuple[str, ...]
    artifact_digest_prefix: str
    artifact_uri: tuple[str, ...]
    artifact_validator: tuple[str, ...]
    auth_scope: tuple[str, ...]
    license_digest: tuple[str, ...]
    metadata: tuple[str, ...]
    requirement_auth_scope: tuple[str, ...]
    credential_required: tuple[str, ...]
    requirement_license_digest: tuple[str, ...]
    license_acceptance_required: tuple[str, ...]


_WIRES = {
    "huggingface": _Wire(
        ("sha",), "git-sha1:", ("cassette_identity",), ("siblings",),
        ("metadata_siblings",), ("rfilename",), ("size",), ("lfs", "sha256"),
        "sha256:", ("download_url",), ("etag",), ("auth", "scope"),
        ("license", "digest"), ("remote_metadata",), ("auth", "scope"),
        ("auth", "required"), ("license", "digest"), ("license", "acceptance_required"),
    ),
    "ollama": _Wire(
        ("digest",), "", ("cassette", "identity"), ("layers",), ("assets",),
        ("name",), ("size",), ("digest",), "", ("url",), ("etag",),
        ("scope",), ("license_digest",), ("model_info",), ("scope",),
        ("credential_required",), ("license_digest",), ("license_acceptance_required",),
    ),
    "tinker": _Wire(
        ("immutable_id",), "", ("provenance", "identity"), ("files",),
        ("metadata_files",), ("key",), ("size_bytes",), ("sha256",), "sha256:",
        ("download_url",), ("validator",), ("authorization", "scope"),
        ("license", "sha256"), ("evidence",), ("authorization", "scope"),
        ("authorization", "required"), ("license", "sha256"),
        ("license", "acceptance_required"),
    ),
}

CredentialLookup = Callable[[str], str | None]


def _fail(code: str, object_id: str, invariant: str, detail: str, retryability: str = "terminal"):
    raise CassetteError(code, object_id, invariant, retryability, detail)


def _origin(url: str) -> tuple[str, str, int] | None:
    try:
        parsed = urlparse(url)
        port = parsed.port or {"http": 80, "https": 443}.get(parsed.scheme.lower())
        host = parsed.hostname
    except (TypeError, ValueError):
        return None
    if parsed.scheme.lower() not in {"http", "https"} or host is None or port is None or parsed.username or parsed.password:
        return None
    return parsed.scheme.lower(), host.lower(), port


def _loopback_http(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme.lower() != "http":
        return True
    host = parsed.hostname
    if host == "localhost":
        return True
    try:
        return host is not None and ip_address(host).is_loopback
    except ValueError:
        return False


class _CredentialSafeRedirect(HTTPRedirectHandler):
    """Keep control authority local and remove credentials before a range crosses origins."""

    def __init__(self, object_id: str, allow_cross_origin: bool):
        super().__init__()
        self.object_id = object_id
        self.allow_cross_origin = allow_cross_origin

    def redirect_request(self, request, response, code, message, headers, target):
        redirected = super().redirect_request(request, response, code, message, headers, target)
        if redirected is None:
            return None
        source_origin = _origin(request.full_url)
        target_origin = _origin(redirected.full_url)
        if target_origin is None:
            _fail("SOURCE_UNAVAILABLE", self.object_id, "Q9: redirects require an HTTP(S) authority", "source returned an invalid redirect target")
        if source_origin != target_origin:
            if not self.allow_cross_origin:
                _fail("SOURCE_UNAVAILABLE", self.object_id, "Q9: control redirects must retain source authority", "cross-origin control redirect refused")
            for collection in (redirected.headers, redirected.unredirected_hdrs):
                for name in tuple(collection):
                    if name.lower() in _SENSITIVE_HEADERS:
                        del collection[name]
        return redirected


def _require_source_range(base_url: str, range_uri: str, object_id: str, path: str) -> None:
    parsed = urlparse(range_uri)
    if _origin(range_uri) != _origin(base_url) or parsed.query or parsed.fragment:
        _fail("SOURCE_UNAVAILABLE", object_id, "Q9: credential-bearing range authority must remain on the selected source origin", path)


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError(f"duplicate JSON field {name!r}")
        result[name] = value
    return result


def _at(record: object, path: tuple[str, ...], object_id: str) -> object:
    value = record
    for field in path:
        if not isinstance(value, Mapping) or field not in value:
            _fail("SOURCE_UNAVAILABLE", object_id, "Q52: source response must satisfy its pinned wire", f"missing field {'.'.join(path)}")
        value = value[field]
    return value


def _text(value: object, field: str, object_id: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        _fail("SOURCE_UNAVAILABLE", object_id, "Q52: source response fields are exact", f"{field} must be a nonempty canonical string")
    return value


def _digest(value: object, prefix: str, field: str, object_id: str) -> str:
    result = _text(value, field, object_id)
    if ":" not in result:
        result = prefix + result
    match = _DIGEST.fullmatch(result)
    if match is None or len(match.group("hex")) != _DIGEST_LENGTH.get(match.group("algorithm")):
        _fail("SOURCE_UNAVAILABLE", object_id, "Q1/Q52: immutable evidence requires a canonical digest", f"{field} is not a supported digest")
    return result


@dataclass(frozen=True, slots=True)
class SourceAdapter:
    """Q52's five operations; the instance owns configuration, not lifecycle state."""

    kind: str
    base_url: str
    credential_lookup: CredentialLookup | None = None

    def __post_init__(self) -> None:
        if self.kind not in _WIRES:
            _fail("MODEL_UNSUPPORTED", self.kind or "source", "Q52: source kind must have a declared adapter wire", "no source wire is registered")
        origin = urlparse(self.base_url) if isinstance(self.base_url, str) else None
        if origin is None or _origin(self.base_url) is None or origin.query or origin.fragment:
            _fail("INVALID_REQUEST", self.kind, "Q52: adapter endpoint must be HTTP(S)", "base_url is invalid")
        if not _loopback_http(self.base_url):
            _fail("INVALID_REQUEST", self.kind, "Q9: credential-bearing remote endpoints require HTTPS", "non-loopback HTTP base_url refused")

    async def resolve(self, descriptor: dict) -> ResolvedSource:
        """Resolve a Q9 descriptor to immutable source evidence."""
        defects = validate("source_descriptor", descriptor)
        if defects:
            _fail("INVALID_REQUEST", self.kind, "Q9: SourceDescriptor must conform before I/O", "; ".join(defects))
        if descriptor["kind"] != self.kind:
            _fail("INVALID_REQUEST", self.kind, "Q52: selected adapter must match descriptor kind", f"received {descriptor['kind']!r}")
        payload = await self._json("resolve", descriptor["locator"], descriptor.get("revision", ""), descriptor.get("credential_ref"), descriptor.get("license_acceptance_ref"), descriptor.get("artifact_selector"))
        resolved = self._resolved(payload, descriptor)
        expected = descriptor.get("expected_identity")
        if expected is not None and expected != resolved.identity:
            _fail("IDENTITY_MISMATCH", resolved.locator, "Q9: expected source identity must match resolved immutable evidence", "resolved identity differs from expected_identity")
        return resolved

    async def enumerate(self, revision: ResolvedSource) -> tuple[Artifact, ...]:
        """Enumerate every immutable model artifact without changing operation semantics."""
        self._revision(revision)
        payload = await self._json("artifacts", revision.locator, revision.immutable_revision, revision.credential_ref, revision.license_acceptance_ref)
        actual_revision = self._revision_digest(payload, revision.locator)
        artifacts = self._artifacts(payload, self._wire.artifacts, revision.locator)
        if actual_revision != revision.immutable_revision or artifacts != revision.artifacts:
            _fail("SOURCE_REVISION_CHANGED", revision.locator, "Q9/Q52: enumeration must remain bound to the resolved revision", "artifact manifest changed after resolve")
        return artifacts

    async def read_metadata(self, revision: ResolvedSource, ranges: tuple[tuple[str, int, int], ...] = ()) -> dict:
        """Read Q50-shaped evidence; optional ranges name bounded metadata inspection requests."""
        self._revision(revision)
        encoded = []
        for path, offset, length in ranges:
            if not isinstance(path, str) or not path or isinstance(offset, bool) or isinstance(length, bool) or not isinstance(offset, int) or not isinstance(length, int) or offset < 0 or length <= 0:
                _fail("INVALID_REQUEST", revision.locator, "Q52: metadata ranges require path, nonnegative offset, and positive length", "invalid metadata range")
            encoded.append(f"{path}:{offset}:{length}")
        payload = await self._json("metadata", revision.locator, revision.immutable_revision, revision.credential_ref, revision.license_acceptance_ref, ranges=tuple(encoded))
        metadata = _at(payload, self._wire.metadata, revision.locator)
        defects = validate("remote_metadata", metadata)
        if defects:
            _fail("SOURCE_UNAVAILABLE", revision.locator, "Q50/Q52: metadata evidence must conform before use", "; ".join(defects))
        identity = metadata["identity"]
        if identity.get("trust") != "ABSENT" and identity.get("value") != revision.identity:
            _fail("SOURCE_REVISION_CHANGED", revision.locator, "Q9/Q50: metadata identity must match resolve", "metadata names another source identity")
        return _source_metadata_record(metadata, self.kind, revision.locator)

    async def open_range(self, revision: ResolvedSource, artifact: Artifact, offset: int, length: int, validator: str) -> bytes:
        """Return one exact validator-bound byte range; S10 owns transfer scheduling and state."""
        self._revision(revision)
        if artifact not in (*revision.artifacts, *revision.metadata_assets):
            _fail("INVALID_REQUEST", revision.locator, "Q52: range artifact must belong to the resolved revision", artifact.path)
        _require_source_range(self.base_url, artifact.range_uri, revision.locator, artifact.path)
        if isinstance(offset, bool) or isinstance(length, bool) or not isinstance(offset, int) or not isinstance(length, int) or offset < 0 or length <= 0 or offset + length > artifact.size:
            _fail("INVALID_REQUEST", artifact.path, "Q52: range must fit the immutable artifact", f"offset={offset}, length={length}, size={artifact.size}")
        headers = {"Range": f"bytes={offset}-{offset + length - 1}", "If-Match": validator}
        status, payload, response_headers = await self._request(
            artifact.range_uri,
            revision.credential_ref,
            revision.license_acceptance_ref,
            headers,
            length,
            artifact.path,
            allow_cross_origin_redirect=True,
        )
        expected_range = f"bytes {offset}-{offset + length - 1}/{artifact.size}"
        if status != 206 or response_headers.get("Content-Range") != expected_range or response_headers.get("ETag") != validator:
            _fail("SOURCE_REVISION_CHANGED", artifact.path, "Q52: range response must retain validator, extent, and length", "source returned different range evidence")
        if len(payload) != length:
            _fail("SOURCE_UNAVAILABLE", artifact.path, "Q51/Q52: an interrupted range is incomplete", f"received {len(payload)} of {length} bytes", "retryable")
        return payload

    async def license_and_auth(self, revision: ResolvedSource) -> Requirements:
        """Translate source requirements while keeping credential bytes outside every result."""
        self._revision(revision)
        payload = await self._json("requirements", revision.locator, revision.immutable_revision, revision.credential_ref, revision.license_acceptance_ref)
        wire = self._wire
        requirements = Requirements(
            _text(_at(payload, wire.requirement_auth_scope, revision.locator), "auth_scope", revision.locator),
            self._boolean(_at(payload, wire.credential_required, revision.locator), "credential_required", revision.locator),
            _digest(_at(payload, wire.requirement_license_digest, revision.locator), "", "license_digest", revision.locator),
            self._boolean(_at(payload, wire.license_acceptance_required, revision.locator), "license_acceptance_required", revision.locator),
        )
        if requirements.auth_scope != revision.auth_scope or requirements.license_digest != revision.license_digest:
            _fail("SOURCE_REVISION_CHANGED", revision.locator, "Q9/Q52: requirements must remain bound to resolve", "auth or license evidence changed")
        return requirements

    @property
    def _wire(self) -> _Wire:
        return _WIRES[self.kind]

    def _revision(self, revision: ResolvedSource) -> None:
        if not isinstance(revision, ResolvedSource) or revision.source_kind != self.kind:
            _fail("INVALID_REQUEST", self.kind, "Q52: revision must belong to the selected adapter", "source kind mismatch")

    def _revision_digest(self, payload: object, object_id: str) -> str:
        return _digest(_at(payload, self._wire.revision, object_id), self._wire.revision_prefix, "immutable_revision", object_id)

    def _artifacts(self, payload: object, collection_path: tuple[str, ...], object_id: str) -> tuple[Artifact, ...]:
        items = _at(payload, collection_path, object_id)
        if not isinstance(items, list):
            _fail("SOURCE_UNAVAILABLE", object_id, "Q9/Q52: artifacts must be an ordered source list", "artifact collection is not an array")
        artifacts = []
        paths = set()
        for item in items:
            path = _text(_at(item, self._wire.artifact_path, object_id), "artifact.path", object_id)
            size = _at(item, self._wire.artifact_size, object_id)
            if isinstance(size, bool) or not isinstance(size, int) or size < 0 or path in paths:
                _fail("SOURCE_UNAVAILABLE", object_id, "Q9: artifact paths and sizes must be exact and unique", path)
            paths.add(path)
            range_uri = urljoin(self.base_url.rstrip("/") + "/", _text(_at(item, self._wire.artifact_uri, object_id), "artifact.range_uri", object_id))
            _require_source_range(self.base_url, range_uri, object_id, path)
            artifacts.append(Artifact(
                path,
                size,
                _digest(_at(item, self._wire.artifact_digest, object_id), self._wire.artifact_digest_prefix, "artifact.digest", object_id),
                range_uri,
                _text(_at(item, self._wire.artifact_validator, object_id), "artifact.validator", object_id),
            ))
        if not artifacts:
            _fail("SOURCE_UNAVAILABLE", object_id, "Q9: a resolved model requires at least one artifact", "artifact collection is empty")
        return tuple(sorted(artifacts, key=lambda artifact: artifact.path))

    def _resolved(self, payload: object, descriptor: dict) -> ResolvedSource:
        wire = self._wire
        locator = descriptor["locator"]
        return ResolvedSource(
            self.kind,
            locator,
            self._revision_digest(payload, locator),
            _digest(_at(payload, wire.identity, locator), "", "identity", locator),
            self._artifacts(payload, wire.artifacts, locator),
            self._artifacts(payload, wire.metadata_assets, locator),
            _text(_at(payload, wire.auth_scope, locator), "auth_scope", locator),
            _digest(_at(payload, wire.license_digest, locator), "", "license_digest", locator),
            descriptor.get("credential_ref"),
            descriptor.get("license_acceptance_ref"),
        )

    @staticmethod
    def _boolean(value: object, field: str, object_id: str) -> bool:
        if not isinstance(value, bool):
            _fail("SOURCE_UNAVAILABLE", object_id, "Q52: requirement fields have exact types", f"{field} must be boolean")
        return value

    async def _json(self, operation: str, locator: str, revision: str, credential_ref: str | None, license_ref: str | None, selector: object = None, *, ranges: tuple[str, ...] = ()) -> object:
        query = [("locator", locator), ("revision", revision)]
        if selector is not None:
            query.append(("selector", json.dumps(selector, sort_keys=True, separators=(",", ":"))))
        query.extend(("range", item) for item in ranges)
        path = f"source/{quote(self.kind, safe='')}/{operation}?{urlencode(query)}"
        _, payload, _ = await self._request(
            urljoin(self.base_url.rstrip("/") + "/", path),
            credential_ref,
            license_ref,
            {},
            _CONTROL_BYTES,
            locator,
        )
        try:
            return json.loads(payload, object_pairs_hook=_unique_object)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
            _fail("SOURCE_UNAVAILABLE", locator, "Q52: control responses must be UTF-8 JSON", f"{operation} returned malformed JSON")

    async def _request(
        self,
        url: str,
        credential_ref: str | None,
        license_ref: str | None,
        headers: dict[str, str],
        maximum: int,
        object_id: str,
        *,
        allow_cross_origin_redirect: bool = False,
    ) -> tuple[int, bytes, Mapping[str, str]]:
        request_headers = dict(headers)
        if credential_ref is not None:
            try:
                secret = self.credential_lookup(credential_ref) if self.credential_lookup is not None else None
            except Exception as error:
                _fail("AUTH_REQUIRED", object_id, "Q9: credential_ref must resolve at operation time", f"credential provider failed with {type(error).__name__}", "retryable")
            if not isinstance(secret, str) or not secret:
                _fail("AUTH_REQUIRED", object_id, "Q9: credential_ref must resolve at operation time", "credential reference is unavailable", "retryable")
            if secret == credential_ref:
                _fail("INVALID_REQUEST", object_id, "Q9: credential_ref must be opaque", "credential_ref must not contain credential material")
            request_headers["Authorization"] = f"Bearer {secret}"
        if license_ref is not None:
            request_headers["X-Cassette-License-Acceptance"] = license_ref
        return await asyncio.to_thread(self._blocking_request, url, request_headers, maximum, object_id, allow_cross_origin_redirect)

    def _blocking_request(
        self,
        url: str,
        headers: dict[str, str],
        maximum: int,
        object_id: str,
        allow_cross_origin_redirect: bool,
    ) -> tuple[int, bytes, Mapping[str, str]]:
        try:
            opener = build_opener(_CredentialSafeRedirect(object_id, allow_cross_origin_redirect))
            with opener.open(Request(url, headers=headers), timeout=30) as response:
                payload = response.read(maximum + 1)
                if len(payload) > maximum:
                    _fail("SOURCE_UNAVAILABLE", object_id, "Q52: source response must stay within the requested bound", f"response exceeds {maximum} bytes")
                return response.status, payload, response.headers
        except HTTPError as error:
            if error.code in {401, 403}:
                _fail("AUTH_REQUIRED", object_id, "Q9: source rejected the credential reference", f"source returned HTTP {error.code}", "retryable")
            if error.code in {409, 412}:
                _fail("SOURCE_REVISION_CHANGED", object_id, "Q9/Q52: source validator changed", f"source returned HTTP {error.code}")
            _fail("SOURCE_UNAVAILABLE", object_id, "Q52: source operation must complete", f"source returned HTTP {error.code}", "retryable")
        except (IncompleteRead, URLError, OSError, TimeoutError) as error:
            _fail("SOURCE_UNAVAILABLE", object_id, "Q52: source endpoint must be reachable", type(error).__name__, "retryable")


def _preflight_fail(object_id: str, detail: str) -> None:
    _fail(
        "INVALID_REQUEST",
        object_id,
        "Q8/Q50/Q56: preflight inputs must be bounded canonical evidence",
        detail,
    )


def _json_copy(value: object, object_id: str) -> object:
    try:
        return json.loads(canonical_bytes(value))
    except (CassetteError, UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
        _preflight_fail(object_id, "metadata values must be canonical JSON")


def _metadata_candidate(candidate: object, object_id: str) -> dict:
    defects = validate("remote_metadata_field", candidate)
    if defects:
        _preflight_fail(object_id, "; ".join(defects))
    result = _json_copy(candidate, object_id)
    if (result["trust"] == "ABSENT") != ("value" not in result):
        _preflight_fail(object_id, "ABSENT metadata has no value; every other trust state requires one")
    return result


def _source_metadata_candidate(candidate: object, source_kind: str, object_id: str) -> dict:
    """Retain a source claim while deriving its trust from the source boundary."""

    result = _metadata_candidate(candidate, object_id)
    marker = f"source:{source_kind}:claim:"
    if not result["authority"].startswith(marker):
        result["authority"] = f"{marker}{result['trust']}:{result['authority']}"
    if result["trust"] != "ABSENT":
        result["trust"] = "DECLARED"
    return result


def _source_metadata_record(record: object, source_kind: str, object_id: str) -> dict:
    """Remove self-asserted trust from one remote Q50 record without losing its claims."""

    defects = validate("remote_metadata", record)
    if defects:
        _preflight_fail(object_id, "; ".join(defects))
    copied = _json_copy(record, object_id)
    result = {
        field: _source_metadata_candidate(copied[field], source_kind, object_id)
        for field in copied if field != "conflicts"
    }
    result["conflicts"] = [{
        "field": conflict["field"],
        "candidates": [
            _source_metadata_candidate(candidate, source_kind, object_id)
            for candidate in conflict["candidates"]
        ],
    } for conflict in copied["conflicts"]]
    return result


def _verified_metadata_candidates(
    revision: ResolvedSource,
    assets: tuple[tuple[str, bytes], ...],
    fields: frozenset[str],
    object_id: str,
) -> dict[str, list[tuple[dict, int]]]:
    """Derive strong Q50 candidates only from complete digest-matched metadata assets."""

    if not isinstance(assets, tuple):
        _preflight_fail(object_id, "verified metadata assets must be a tuple")
    available = {artifact.path: artifact for artifact in revision.metadata_assets}
    candidates: dict[str, list[tuple[dict, int]]] = {}
    seen = set()
    for item in assets:
        if (not isinstance(item, tuple) or len(item) != 2
                or not isinstance(item[0], str) or type(item[1]) is not bytes
                or item[0] in seen or item[0] not in available):
            _preflight_fail(object_id, "each verified metadata asset must name one resolved path once")
        path, payload = item
        seen.add(path)
        artifact = available[path]
        if len(payload) != artifact.size or len(payload) > _CONTROL_BYTES:
            _preflight_fail(path, "verified metadata bytes must match one bounded resolved asset")
        hasher = artifact_hasher(artifact.digest, path)
        hasher.update(payload)
        actual = f"{artifact.digest.partition(':')[0]}:{hasher.hexdigest()}"
        if actual != artifact.digest:
            _fail(
                "IDENTITY_MISMATCH",
                path,
                "Q50: strong metadata must come from resolved immutable bytes",
                f"expected {artifact.digest}; observed {actual}",
            )
        try:
            values = json.loads(payload, object_pairs_hook=_unique_object)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
            _preflight_fail(path, "verified metadata asset must be UTF-8 JSON without duplicate fields")
        if (not isinstance(values, dict) or not values
                or any(field not in fields for field in values)):
            _preflight_fail(path, "verified metadata asset must contain only generated Q50 fields")
        authority = f"cassette:metadata-asset:{path}:{artifact.digest}"
        for field, value in values.items():
            candidate = _metadata_candidate({
                "value": value,
                "trust": "EVIDENCE_DIGESTED",
                "authority": authority,
            }, object_id)
            candidates.setdefault(field, []).append((candidate, 3))
    return candidates


def _resolved_metadata_candidates(revision: ResolvedSource, object_id: str) -> dict[str, dict]:
    objects = (*revision.artifacts, *revision.metadata_assets)
    if not revision.artifacts or any(not isinstance(artifact, Artifact) for artifact in objects):
        _preflight_fail(object_id, "resolved source artifacts are missing or malformed")
    paths = [artifact.path for artifact in objects]
    if (len(set(paths)) != len(paths)
            or tuple(artifact.path for artifact in revision.artifacts) != tuple(sorted(
                artifact.path for artifact in revision.artifacts
            ))
            or tuple(artifact.path for artifact in revision.metadata_assets) != tuple(sorted(
                artifact.path for artifact in revision.metadata_assets
            ))
            or any(
                _canonical_text(artifact.path) is None
                or type(artifact.size) is not int or not 0 <= artifact.size <= 2**64 - 1
                or _canonical_digest(artifact.digest) is None
                or _canonical_text(artifact.range_uri) is None
                or _canonical_text(artifact.validator) is None
                for artifact in objects
            )):
        _preflight_fail(object_id, "resolved artifacts require unique sorted paths and exact immutable fields")
    authority = f"cassette:resolved:{revision.source_kind}:manifest"
    values = {
        "identity": revision.identity,
        "total_bytes": sum(artifact.size for artifact in revision.artifacts),
        "artifact_count": len(revision.artifacts),
        "artifact_digests": [artifact.digest for artifact in revision.artifacts],
        "license": revision.license_digest,
        "source_validators": {artifact.path: artifact.validator for artifact in objects},
    }
    return {
        field: {"value": value, "trust": "EVIDENCE_DIGESTED", "authority": authority}
        for field, value in values.items()
    }


def normalize_remote_metadata(
    revision: ResolvedSource,
    records: tuple[dict, ...],
    *,
    verified_assets: tuple[tuple[str, bytes], ...] = (),
) -> dict:
    """Merge Q50 evidence, prefer immutable source facts, and retain every contradiction."""

    object_id = revision.locator if isinstance(revision, ResolvedSource) else "source:unidentified"
    if not isinstance(revision, ResolvedSource):
        _preflight_fail(object_id, "ResolvedSource is required")
    if not isinstance(records, tuple) or not records:
        _preflight_fail(object_id, "one or more remote_metadata records are required")
    fields: tuple[str, ...] | None = None
    candidates: dict[str, list[tuple[dict, int]]] = {}
    for record in records:
        record = _source_metadata_record(record, revision.source_kind, object_id)
        record_fields = tuple(sorted(set(record) - {"conflicts"}))
        if fields is None:
            fields = record_fields
            candidates = {field: [] for field in fields}
        elif record_fields != fields:
            _preflight_fail(object_id, "remote_metadata records must expose one generated field set")
        for field in fields:
            candidate = _metadata_candidate(record[field], object_id)
            candidates[field].append((candidate, _METADATA_TRUST[candidate["trust"]]))
        for conflict in record["conflicts"]:
            field = conflict["field"]
            if field not in candidates:
                _preflight_fail(object_id, f"conflict names unknown field {field!r}")
            for raw in conflict["candidates"]:
                candidate = _metadata_candidate(raw, object_id)
                candidates[field].append((candidate, _METADATA_TRUST[candidate["trust"]]))

    for field, verified in _verified_metadata_candidates(
        revision, verified_assets, frozenset(fields or ()), object_id
    ).items():
        candidates[field].extend(verified)

    resolved = _resolved_metadata_candidates(revision, object_id)
    for field, candidate in resolved.items():
        if field not in candidates:
            _preflight_fail(object_id, f"generated metadata schema omits resolved field {field!r}")
        candidates[field].append((_metadata_candidate(candidate, object_id), 4))

    normalized = {}
    conflicts = []
    for field in fields or ():
        unique = {}
        for candidate, priority in candidates[field]:
            encoded = canonical_bytes(candidate)
            retained = unique.get(encoded)
            if retained is None or priority > retained[1]:
                unique[encoded] = (candidate, priority)
        ordered = sorted(
            unique.values(),
            key=lambda item: (-item[1], item[0]["authority"], canonical_bytes(item[0])),
        )
        present = tuple(item for item in ordered if item[0]["trust"] != "ABSENT")
        if not present:
            normalized[field] = ordered[0][0]
            continue
        top_priority = present[0][1]
        top = tuple(item for item in present if item[1] == top_priority)
        top_values = {canonical_bytes(item[0]["value"]) for item in top}
        normalized[field] = (
            top[0][0]
            if len(top_values) == 1
            else {"trust": "ABSENT", "authority": f"cassette:conflict:{field}"}
        )
        distinct_values = {canonical_bytes(item[0]["value"]) for item in present}
        if len(distinct_values) > 1:
            conflicts.append({"field": field, "candidates": [item[0] for item in present]})
    normalized["conflicts"] = sorted(conflicts, key=lambda conflict: conflict["field"])
    defects = validate("remote_metadata", normalized)
    if defects:
        _preflight_fail(object_id, "; ".join(defects))
    return normalized


def _preflight_profile(profile: CompatibilityProfile, object_id: str) -> None:
    if not isinstance(profile, CompatibilityProfile):
        _preflight_fail(object_id, "CompatibilityProfile is required")
    integers = (profile.device_bytes, profile.allocatable_verified_free, profile.memory_bytes)
    if (any(type(value) is not int or not 0 <= value <= 2**64 - 1 for value in integers)
            or profile.device_bytes == 0 or profile.memory_bytes == 0
            or profile.allocatable_verified_free > profile.device_bytes):
        _preflight_fail(object_id, "profile byte bounds must be exact and internally consistent")
    for name, values in (
        ("supported_operators", profile.supported_operators),
        ("supported_modalities", profile.supported_modalities),
        ("native_formats", profile.native_formats),
        ("preparation_formats", profile.preparation_formats),
    ):
        if (not isinstance(values, frozenset) or any(
                not isinstance(value, str) or not value or value != value.strip()
                for value in values
        )):
            _preflight_fail(object_id, f"{name} must be a frozenset of canonical names")
    if any(value != value.casefold() for value in (*profile.native_formats, *profile.preparation_formats)):
        _preflight_fail(object_id, "format names in a compatibility profile must be lowercase")
    if (not isinstance(profile.training_tiers, tuple)
            or len(set(profile.training_tiers)) != len(profile.training_tiers)
            or any(not isinstance(value, str) or not value or value != value.strip()
                   for value in profile.training_tiers)):
        _preflight_fail(object_id, "training_tiers must be unique canonical names")


def _metadata_probes(
    probes: tuple[MetadataProbe, ...],
    revision: ResolvedSource,
    fields: frozenset[str],
) -> tuple[MetadataProbe, ...]:
    if not isinstance(probes, tuple):
        _preflight_fail(revision.locator, "metadata probes must be a tuple")
    artifacts = {artifact.path: artifact for artifact in (*revision.artifacts, *revision.metadata_assets)}
    checked = []
    for probe in probes:
        artifact = artifacts.get(probe.artifact_path) if isinstance(probe, MetadataProbe) else None
        if (artifact is None or not isinstance(probe.fields, tuple) or not probe.fields
                or len(set(probe.fields)) != len(probe.fields)
                or any(field not in fields for field in probe.fields)
                or type(probe.offset) is not int or type(probe.length) is not int
                or probe.offset < 0 or probe.length <= 0
                or probe.offset + probe.length > artifact.size):
            _preflight_fail(revision.locator, "each metadata probe must be bounded by one resolved artifact")
        checked.append(probe)
    return tuple(sorted(checked, key=lambda probe: (probe.artifact_path, probe.offset, probe.fields)))


def _metadata_probe_record(probe: MetadataProbe, revision: ResolvedSource) -> dict:
    artifact = next(
        artifact for artifact in (*revision.artifacts, *revision.metadata_assets)
        if artifact.path == probe.artifact_path
    )
    return {
        **probe.record(),
        "artifact_digest": artifact.digest,
        "validator": artifact.validator,
    }


def _metadata_value(metadata: dict, field: str):
    record = metadata[field]
    return None if record["trust"] == "ABSENT" else record["value"]


def _canonical_text(value: object) -> str | None:
    return value if isinstance(value, str) and value and value == value.strip() else None


def _canonical_names(value: object) -> tuple[str, ...] | None:
    if (not isinstance(value, list) or not value
            or any(_canonical_text(item) is None for item in value)
            or len(set(value)) != len(value)):
        return None
    return tuple(value)


def _context_bound(value: object) -> tuple[dict, int] | None:
    if (not isinstance(value, dict) or set(value) != {"tokens", "state_bytes"}
            or type(value["tokens"]) is not int or value["tokens"] <= 0
            or type(value["state_bytes"]) is not int
            or not 0 <= value["state_bytes"] <= 2**64 - 1):
        return None
    return value, value["state_bytes"]


def _canonical_digest(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    match = _DIGEST.fullmatch(value)
    if match is None or len(match.group("hex")) != _DIGEST_LENGTH.get(match.group("algorithm")):
        return None
    return value


def preflight(
    revision: ResolvedSource,
    metadata_records: tuple[dict, ...],
    requirements: Requirements,
    profile: CompatibilityProfile,
    *,
    verified_assets: tuple[tuple[str, bytes], ...] = (),
    probes: tuple[MetadataProbe, ...] = (),
) -> PreflightDecision:
    """Return one Q8/Q50/Q56 decision without inspecting or allocating on the current machine."""

    object_id = revision.locator if isinstance(revision, ResolvedSource) else "source:unidentified"
    if not isinstance(revision, ResolvedSource):
        _preflight_fail(object_id, "ResolvedSource is required")
    if not isinstance(requirements, Requirements):
        _preflight_fail(object_id, "Requirements is required")
    if (not isinstance(requirements.auth_scope, str) or not requirements.auth_scope
            or not isinstance(requirements.credential_required, bool)
            or _canonical_digest(requirements.license_digest) is None
            or not isinstance(requirements.license_acceptance_required, bool)):
        _preflight_fail(object_id, "Requirements fields must retain their exact Q9 types")
    _preflight_profile(profile, object_id)
    metadata = normalize_remote_metadata(
        revision, metadata_records, verified_assets=verified_assets
    )
    fields = frozenset(metadata) - {"conflicts"}
    checked_probes = _metadata_probes(probes, revision, fields)

    values = {field: _metadata_value(metadata, field) for field in fields}
    unresolved = {
        field for field in _PREFLIGHT_REQUIRED
        if values.get(field) is None
    }
    unresolved.update(
        field for field in _PREFLIGHT_STRONG
        if values.get(field) is not None
        and metadata[field]["trust"] not in {"EVIDENCE_DIGESTED", "PARSED"}
    )
    decisive = []
    invalid = []

    if (revision.source_kind not in _WIRES or _canonical_text(revision.locator) is None
            or _canonical_text(revision.auth_scope) is None
            or _canonical_digest(revision.license_digest) is None
            or _canonical_digest(revision.immutable_revision) is None
            or _canonical_digest(revision.identity) is None
            or not revision.identity.startswith("blake3:")):
        decisive.append("MUTABLE_OR_UNVERIFIED_SOURCE_IDENTITY")
    source_identity = values.get("identity")
    if _canonical_digest(source_identity) is None or source_identity != revision.identity:
        invalid.append("identity")

    total_bytes = values.get("total_bytes")
    artifact_count = values.get("artifact_count")
    artifact_digests = values.get("artifact_digests")
    if type(total_bytes) is not int or not 0 < total_bytes <= 2**64 - 1:
        invalid.append("total_bytes")
        total_bytes = None
    if type(artifact_count) is not int or artifact_count <= 0:
        invalid.append("artifact_count")
    if (not isinstance(artifact_digests, list) or len(artifact_digests) != artifact_count
            or any(_canonical_digest(value) is None for value in artifact_digests)):
        invalid.append("artifact_digests")

    model_format = _canonical_text(values.get("format"))
    architecture = _canonical_text(values.get("architecture"))
    if values.get("format") is not None and model_format is None:
        invalid.append("format")
    if values.get("architecture") is not None and architecture is None:
        invalid.append("architecture")
    total_parameters = values.get("total_parameters")
    active_parameters = values.get("active_parameters")
    if (values.get("total_parameters") is not None
            and (type(total_parameters) is not int or total_parameters <= 0)):
        invalid.append("total_parameters")
        total_parameters = None
    if (values.get("active_parameters") is not None
            and (type(active_parameters) is not int or active_parameters <= 0)):
        invalid.append("active_parameters")
        active_parameters = None
    if (total_parameters is not None and active_parameters is not None
            and active_parameters > total_parameters):
        invalid.append("active_parameters")

    precision = values.get("dtype_quantization")
    precision_active_bytes = None
    if precision is not None:
        if _canonical_text(precision) is None and not isinstance(precision, dict):
            invalid.append("dtype_quantization")
        elif isinstance(precision, dict):
            if _canonical_text(precision.get("name")) is None:
                invalid.append("dtype_quantization")
            if "active_bytes" in precision:
                precision_active_bytes = precision["active_bytes"]
                if (type(precision_active_bytes) is not int or precision_active_bytes <= 0
                        or (total_bytes is not None and precision_active_bytes > total_bytes)):
                    invalid.append("dtype_quantization")
                    precision_active_bytes = None

    context_result = _context_bound(values.get("context"))
    context = context_result[0] if context_result is not None else None
    context_state_bytes = context_result[1] if context_result is not None else None
    if values.get("context") is not None and context_result is None:
        invalid.append("context")
    modalities = _canonical_names(values.get("modalities"))
    operators = _canonical_names(values.get("operators"))
    if values.get("modalities") is not None and modalities is None:
        invalid.append("modalities")
    if values.get("operators") is not None and operators is None:
        invalid.append("operators")
    custom_code = values.get("custom_code")
    gating = values.get("gating")
    if custom_code is not None and not isinstance(custom_code, bool):
        invalid.append("custom_code")
    if gating is not None and not isinstance(gating, bool):
        invalid.append("gating")

    for field in ("tokenizer", "template", "license"):
        if values.get(field) is not None and _canonical_digest(values[field]) is None:
            invalid.append(field)
    if modalities is not None and any(modality != "text" for modality in modalities):
        if values.get("processor") is None:
            unresolved.add("processor")
        elif metadata["processor"]["trust"] not in {"EVIDENCE_DIGESTED", "PARSED"}:
            unresolved.add("processor")
        elif _canonical_digest(values["processor"]) is None:
            invalid.append("processor")
    source_validators = values.get("source_validators")
    if (source_validators is not None
            and (not isinstance(source_validators, dict) or not source_validators
                 or any(_canonical_text(name) is None or _canonical_text(value) is None
                        for name, value in source_validators.items()))):
        invalid.append("source_validators")

    if requirements.auth_scope != revision.auth_scope or requirements.license_digest != revision.license_digest:
        decisive.append("SOURCE_REQUIREMENTS_CHANGED")
    if requirements.credential_required and revision.credential_ref is None:
        decisive.append("CREDENTIAL_REQUIRED")
    if requirements.license_acceptance_required and revision.license_acceptance_ref is None:
        decisive.append("LICENSE_ACCEPTANCE_REQUIRED")
    if gating is True and not (
            requirements.credential_required or requirements.license_acceptance_required
    ):
        decisive.append("GATING_REQUIREMENTS_CONFLICT")
    if custom_code is True:
        decisive.append("CUSTOM_CODE_REQUIRES_CONTAINMENT")
    decisive.extend(f"INVALID_METADATA:{field}" for field in sorted(set(invalid)))

    required_bytes = None
    objects = (*revision.artifacts, *revision.metadata_assets)
    if any(artifact.size > _MAX_FILE_OFFSET for artifact in objects):
        decisive.append("SOURCE_ARTIFACT_EXCEEDS_TRANSFER_LIMIT")
    else:
        try:
            payload_bytes = sum(artifact.size for artifact in objects)
            state_bytes = sum(transfer_state_bytes(artifact.size) for artifact in objects)
            requirement = capacity_requirement(
                "preflight",
                device_bytes=profile.device_bytes,
                phases=(CapacityPhase(inflight=payload_bytes, journal=state_bytes),),
            )
            required_bytes = requirement.required_bytes
            if required_bytes > profile.allocatable_verified_free:
                decisive.append("CAPACITY_EXCEEDED")
        except CassetteError as error:
            if error.code != "CAPACITY_EXCEEDED":
                raise
            decisive.append("CAPACITY_EXCEEDED")

    format_name = model_format.casefold() if model_format is not None else None
    unsupported_operators = (
        tuple(sorted(set(operators) - profile.supported_operators))
        if operators is not None else ()
    )
    unsupported_modalities = (
        tuple(sorted(set(modalities) - profile.supported_modalities))
        if modalities is not None else ()
    )
    decisive.extend(f"UNSUPPORTED_OPERATOR:{operator}" for operator in unsupported_operators)
    decisive.extend(f"UNSUPPORTED_MODALITY:{modality}" for modality in unsupported_modalities)
    native_candidate = format_name in profile.native_formats if format_name is not None else False
    preparation_candidate = (
        format_name in profile.preparation_formats if format_name is not None else False
    )
    if format_name is not None and not native_candidate and not preparation_candidate:
        decisive.append(f"UNSUPPORTED_FORMAT:{format_name}")

    native_peak_bytes = None
    if total_bytes is not None and total_parameters is not None and active_parameters is not None:
        weight_bytes = None
        if active_parameters == total_parameters:
            weight_bytes = total_bytes
        elif precision_active_bytes is not None:
            weight_bytes = precision_active_bytes
        elif native_candidate and total_bytes > profile.memory_bytes:
            unresolved.add("dtype_quantization")
        else:
            weight_bytes = total_bytes
        if weight_bytes is not None and context_state_bytes is not None:
            native_peak_bytes = weight_bytes + context_state_bytes
            if native_peak_bytes > 2**64 - 1:
                decisive.append("MEMORY_BOUND_EXCEEDS_PROFILE")
                native_peak_bytes = None
    if context_state_bytes is not None and context_state_bytes >= profile.memory_bytes:
        decisive.append("MEMORY_BOUND_EXCEEDS_PROFILE")

    probes_by_field = {
        field: tuple(probe for probe in checked_probes if field in probe.fields)
        for field in unresolved
    }
    undecidable = tuple(sorted(field for field, matches in probes_by_field.items() if not matches))
    range_checks = tuple(
        _metadata_probe_record(probe, revision) for probe in checked_probes
        if any(field in unresolved for field in probe.fields)
    )
    reasons = list(dict.fromkeys(decisive))
    selected_modes: tuple[str, ...] = ()
    deferred_checks: tuple[dict, ...] = range_checks
    training_tiers: tuple[str, ...] = ()

    peak_bytes = native_peak_bytes
    if reasons:
        reasons.extend(f"METADATA_REQUIRED:{field}" for field in sorted(unresolved))
        reasons.extend(f"UNDECIDABLE_METADATA:{field}" for field in undecidable)
        classification = "UNSUPPORTED"
    elif unresolved:
        reasons.extend(f"METADATA_REQUIRED:{field}" for field in sorted(unresolved))
        if undecidable:
            reasons.extend(f"UNDECIDABLE_METADATA:{field}" for field in undecidable)
            classification = "UNSUPPORTED"
        else:
            classification = "METADATA_INSUFFICIENT"
    elif native_candidate and native_peak_bytes is not None and native_peak_bytes <= profile.memory_bytes:
        classification = "SUPPORTED"
        reasons.append("NATIVE_STATIC_PREDICATES_PASS")
        selected_modes = ("NATIVE",)
    elif preparation_candidate and context_state_bytes is not None:
        classification = "SUPPORTED_AFTER_PREPARATION"
        reasons.append("PREPARATION_AND_Q17_Q19_EVIDENCE_REQUIRED")
        selected_modes = ("COMPILED",)
        peak_bytes = profile.memory_bytes
        deferred_checks += ({
            "kind": "PREPARATION_VALIDATION",
            "invariants": ["Q17", "Q18", "Q19"],
        },)
    else:
        classification = "UNSUPPORTED"
        reasons.append("MEMORY_BOUND_EXCEEDS_PROFILE")

    training_precision = values.get("training_precision")
    if (training_precision is not None
            and _canonical_text(training_precision) is None
            and not isinstance(training_precision, dict)):
        training_precision = None
    if (classification in {"SUPPORTED", "SUPPORTED_AFTER_PREPARATION"}
            and training_precision is not None
            and metadata["training_precision"]["trust"] in {"EVIDENCE_DIGESTED", "PARSED"}):
        training_tiers = profile.training_tiers
    if classification not in _PREFLIGHT_CLASSES:
        _preflight_fail(object_id, "preflight produced an undeclared classification")
    assets = tuple(
        {"role": role, **artifact.record()}
        for role, collection in (
            ("model", revision.artifacts), ("metadata", revision.metadata_assets)
        )
        for artifact in collection
    )
    return PreflightDecision(
        classification,
        source_identity if isinstance(source_identity, str) else None,
        metadata["identity"]["trust"],
        total_bytes,
        peak_bytes,
        architecture,
        operators,
        precision,
        total_parameters,
        active_parameters,
        context,
        assets,
        values.get("license") if isinstance(values.get("license"), str) else None,
        training_tiers,
        selected_modes,
        tuple(reasons),
        required_bytes,
        peak_bytes,
        profile.allocatable_verified_free,
        deferred_checks,
        metadata,
    )


def transfer_state_bytes(object_size: int) -> int:
    """Return the exact fixed checkpoint extent required for one Q51 artifact."""

    if type(object_size) is not int or not 0 <= object_size <= _MAX_FILE_OFFSET:
        _transfer_fail("INVALID_REQUEST", "transfer:unidentified", "object_size must fit a signed 64-bit file offset")
    chunks = (object_size + _TRANSFER_CHUNK_BYTES - 1) // _TRANSFER_CHUNK_BYTES
    return _TRANSFER_RECORDS_OFFSET + chunks * _TRANSFER_RECORD_BYTES


def _transfer_fail(code: str, object_id: str, detail: str, retryability: str = "terminal") -> None:
    raise CassetteError(code, object_id, "Q51: resumable verified transfer", retryability, detail)


def _extent(extent: TransferExtent, required: int, object_id: str, name: str):
    if (not isinstance(extent, TransferExtent) or type(extent.fd) is not int
            or type(extent.offset) is not int or type(extent.length) is not int
            or extent.fd < 0 or extent.offset < 0 or extent.length < required
            or extent.offset > _MAX_FILE_OFFSET - extent.length
            or not isinstance(extent.operation_id, str) or not extent.operation_id):
        _transfer_fail("INVALID_REQUEST", object_id, f"{name} is not a sufficient pre-opened extent")
    try:
        metadata = os.fstat(extent.fd)
        flags = fcntl.fcntl(extent.fd, fcntl.F_GETFL)
    except OSError as error:
        _transfer_fail("CARTRIDGE_DISCONNECTED", object_id, f"{name} handle is unavailable: {error}", "retryable")
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_size < extent.offset + extent.length:
        _transfer_fail("CAPACITY_EXCEEDED", object_id, f"{name} was not preallocated to {extent.length} bytes")
    if flags & os.O_ACCMODE == os.O_RDONLY:
        _transfer_fail("CARTRIDGE_READ_ONLY", object_id, f"{name} is read-only")
    return metadata


def _pread_exact(extent: TransferExtent, offset: int, length: int, object_id: str) -> bytes:
    if (type(offset) is not int or type(length) is not int or offset < 0 or length < 0
            or offset > extent.length - length):
        _transfer_fail("INVALID_REQUEST", object_id, "cartridge read exceeds its granted extent")
    payload = bytearray()
    while len(payload) < length:
        try:
            part = os.pread(extent.fd, length - len(payload), extent.offset + offset + len(payload))
        except OSError as error:
            _transfer_fail("CARTRIDGE_DISCONNECTED", object_id, f"cartridge read failed: {error}", "retryable")
        if not part:
            _transfer_fail("IDENTITY_MISMATCH", object_id, f"local extent ended after {len(payload)} of {length} bytes")
        payload.extend(part)
    return bytes(payload)


def _pwrite_all(extent: TransferExtent, offset: int, payload: bytes, object_id: str) -> None:
    if (type(offset) is not int or not isinstance(payload, bytes) or offset < 0
            or offset > extent.length - len(payload)):
        _transfer_fail("INVALID_REQUEST", object_id, "cartridge write exceeds its granted extent")
    written = 0
    while written < len(payload):
        try:
            count = os.pwrite(extent.fd, payload[written:], extent.offset + offset + written)
        except OSError as error:
            _transfer_fail("CARTRIDGE_DISCONNECTED", object_id, f"cartridge write failed: {error}", "retryable")
        if count <= 0:
            _transfer_fail("DURABILITY_UNSUPPORTED", object_id, "cartridge write made no progress")
        written += count


def _pwrite_verified(
    extent: TransferExtent, offset: int, payload: bytes, object_id: str, description: str
) -> None:
    _pwrite_all(extent, offset, payload, object_id)
    if digest_bytes(_pread_exact(extent, offset, len(payload), object_id)) != digest_bytes(payload):
        _transfer_fail("DURABILITY_UNSUPPORTED", object_id, f"{description} changed during readback")


def _sync_fd(fd: int, object_id: str) -> None:
    try:
        os.fsync(fd)
        command = getattr(fcntl, "F_FULLFSYNC", None)
        if command is not None:
            fcntl.fcntl(fd, command)
    except OSError as error:
        _transfer_fail("DURABILITY_UNSUPPORTED", object_id, f"durable extent synchronization failed: {error}")


def _state_envelope(record: dict, object_id: str) -> bytes:
    envelope = canonical_bytes({"digest": digest_bytes(canonical_bytes(record)), "record": record})
    if len(envelope) > _TRANSFER_SLOT_BYTES - 4:
        _transfer_fail("INVALID_REQUEST", object_id, "transfer identity exceeds the fixed checkpoint header")
    return len(envelope).to_bytes(4, "big") + envelope


def _decode_state_slot(payload: bytes, slot: int) -> dict | None:
    length = int.from_bytes(payload[:4], "big")
    if length == 0:
        return None
    if length > _TRANSFER_SLOT_BYTES - 4:
        return None
    encoded = payload[4:4 + length]
    try:
        envelope = json.loads(encoded, object_pairs_hook=_unique_object)
        if (not isinstance(envelope, dict) or set(envelope) != {"digest", "record"}
                or canonical_bytes(envelope) != encoded or not isinstance(envelope["record"], dict)
                or envelope["digest"] != digest_bytes(canonical_bytes(envelope["record"]))):
            return None
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, CassetteError):
        return None
    record = envelope["record"]
    if set(record) != _TRANSFER_HEADER_FIELDS:
        return None
    integers = ("version", "generation", "object_size", "chunk_bytes", "chunk_count", "completed_count", "contiguous_source_hash_offset")
    texts = (
        "artifact_id", "source_revision", "validator", "expected_digest",
        "serialized_hash_state", "contiguous_source_hash_digest", "chunk_records_digest",
    )
    if (any(type(record[name]) is not int or record[name] < 0 for name in integers)
            or any(not isinstance(record[name], str) or not record[name] for name in texts)
            or record["version"] != 1 or record["generation"] % 2 != slot
            or record["chunk_bytes"] != _TRANSFER_CHUNK_BYTES
            or record["object_size"] > _MAX_FILE_OFFSET
            or record["chunk_count"] != (
                record["object_size"] + _TRANSFER_CHUNK_BYTES - 1
            ) // _TRANSFER_CHUNK_BYTES
            or record["completed_count"] > record["chunk_count"]
            or (record["chunk_manifest_digest"] is not None
                and (not isinstance(record["chunk_manifest_digest"], str)
                     or not re.fullmatch(r"blake3:[0-9a-f]{64}", record["chunk_manifest_digest"])))):
        return None
    expected_offset = min(record["completed_count"] * _TRANSFER_CHUNK_BYTES, record["object_size"])
    if record["contiguous_source_hash_offset"] != expected_offset:
        return None
    return record


def _load_state(extent: TransferExtent, object_id: str) -> tuple[dict, tuple[str, ...]] | None:
    slots = tuple(
        _pread_exact(extent, slot * _TRANSFER_SLOT_BYTES, _TRANSFER_SLOT_BYTES, object_id)
        for slot in range(2)
    )
    candidates = tuple(
        record for slot, payload in enumerate(slots)
        if (record := _decode_state_slot(payload, slot)) is not None
    )
    if not candidates:
        if any(any(payload) for payload in slots):
            _clear_state(extent, object_id)
            _transfer_fail("IDENTITY_MISMATCH", object_id, "no valid transfer checkpoint header remains")
        return None
    record = max(candidates, key=lambda candidate: candidate["generation"])
    record_bytes = record["completed_count"] * _TRANSFER_RECORD_BYTES
    if record_bytes > extent.length - _TRANSFER_RECORDS_OFFSET:
        _clear_state(extent, object_id)
        _transfer_fail("IDENTITY_MISMATCH", object_id, "transfer chunk records exceed their checkpoint extent")
    encoded_records = _pread_exact(
        extent,
        _TRANSFER_RECORDS_OFFSET,
        record_bytes,
        object_id,
    )
    digests = []
    for index in range(record["completed_count"]):
        start = index * _TRANSFER_RECORD_BYTES
        raw = encoded_records[start:start + _TRANSFER_RECORD_BYTES]
        if raw[0] != 1:
            _clear_state(extent, object_id)
            _transfer_fail("IDENTITY_MISMATCH", object_id, f"transfer chunk record {index} is incomplete")
        digests.append("blake3:" + raw[1:].hex())
    return record, tuple(digests)


def _write_state(extent: TransferExtent, record: dict, object_id: str) -> None:
    slot = record["generation"] % 2
    _pwrite_verified(
        extent,
        slot * _TRANSFER_SLOT_BYTES,
        _state_envelope(record, object_id),
        object_id,
        "transfer checkpoint header",
    )
    _sync_fd(extent.fd, object_id)


def _clear_state(extent: TransferExtent, object_id: str) -> None:
    _pwrite_verified(
        extent,
        0,
        bytes(_TRANSFER_RECORDS_OFFSET),
        object_id,
        "discarded transfer checkpoint",
    )
    _sync_fd(extent.fd, object_id)


def _reset_state(extent: TransferExtent, material: dict, generation: int, object_id: str) -> dict:
    identity = {name: material[name] for name in _TRANSFER_IDENTITY_FIELDS}
    source = resumable_artifact_hasher(identity["expected_digest"], object_id)
    records = resumable_artifact_hasher("sha256:" + "0" * 64, object_id)
    record = {
        **identity,
        "generation": generation + 1,
        "completed_count": 0,
        "contiguous_source_hash_offset": 0,
        "serialized_hash_state": artifact_hash_state(source, identity["expected_digest"], 0, object_id),
        "contiguous_source_hash_digest": _source_hash_state(source, identity["expected_digest"]),
        "chunk_records_digest": _source_hash_state(records, "sha256:"),
    }
    _write_state(extent, record, object_id)
    return record


def _chunk_count(size: int) -> int:
    return (size + _TRANSFER_CHUNK_BYTES - 1) // _TRANSFER_CHUNK_BYTES


def _source_hash_state(hasher, expected_digest: str) -> str:
    return expected_digest.partition(":")[0] + ":" + hasher.hexdigest()


def _partial(record: dict, chunk_digests: tuple[str, ...]) -> PartialState:
    offset = record["contiguous_source_hash_offset"]
    return PartialState(
        record["source_revision"],
        record["object_size"],
        record["validator"],
        () if offset == 0 else ((0, offset),),
        chunk_digests,
        offset,
        record["serialized_hash_state"],
    )


def _transfer_identity(
    revision: ResolvedSource,
    artifact: Artifact,
    authoritative_chunk_digests: tuple[str, ...] | None,
) -> dict:
    if type(artifact.size) is not int or not 0 <= artifact.size <= _MAX_FILE_OFFSET:
        _transfer_fail("INVALID_REQUEST", artifact.path, "artifact size must fit a signed 64-bit file offset")
    count = _chunk_count(artifact.size)
    if authoritative_chunk_digests is not None:
        if (not isinstance(authoritative_chunk_digests, tuple)
                or len(authoritative_chunk_digests) != count
                or any(not isinstance(value, str)
                       or re.fullmatch(r"blake3:[0-9a-f]{64}", value) is None
                       for value in authoritative_chunk_digests)):
            _transfer_fail("INVALID_REQUEST", artifact.path, "authoritative chunk digests must cover every chunk with BLAKE3")
        manifest_digest = digest_bytes(canonical_bytes(list(authoritative_chunk_digests)))
    else:
        manifest_digest = None
    if (not isinstance(artifact.digest, str)
            or re.fullmatch(r"sha256:[0-9a-f]{64}", artifact.digest) is None
            or not isinstance(artifact.validator, str) or not artifact.validator):
        _transfer_fail("SOURCE_UNAVAILABLE", artifact.path, "an authoritative SHA-256 digest and stable validator are required")
    artifact_id = digest_bytes(canonical_bytes({
        "source_revision": revision.immutable_revision,
        "path": artifact.path,
        "size": artifact.size,
        "digest": artifact.digest,
        "validator": artifact.validator,
    }))
    return {
        "version": 1,
        "artifact_id": artifact_id,
        "source_revision": revision.immutable_revision,
        "object_size": artifact.size,
        "validator": artifact.validator,
        "expected_digest": artifact.digest,
        "chunk_bytes": _TRANSFER_CHUNK_BYTES,
        "chunk_count": count,
        "chunk_manifest_digest": manifest_digest,
    }


async def transfer_artifact(
    adapter: SourceAdapter,
    revision: ResolvedSource,
    artifact: Artifact,
    data_extent: TransferExtent,
    state_extent: TransferExtent,
    reservation: CapacityReservation,
    *,
    authoritative_chunk_digests: tuple[str, ...] | None = None,
) -> PartialState:
    """Resume one Q51 artifact and return only after its durable final proof is complete."""

    if not isinstance(adapter, SourceAdapter):
        _transfer_fail("INVALID_REQUEST", "transfer:unidentified", "SourceAdapter is required")
    adapter._revision(revision)
    if not isinstance(artifact, Artifact) or artifact not in revision.artifacts:
        _transfer_fail("INVALID_REQUEST", revision.locator, "artifact must belong to the resolved source revision")
    identity = _transfer_identity(revision, artifact, authoritative_chunk_digests)
    state_required = transfer_state_bytes(artifact.size)
    data_metadata = _extent(data_extent, artifact.size, artifact.path, "data extent")
    state_metadata = _extent(state_extent, state_required, artifact.path, "checkpoint extent")
    if ((data_metadata.st_dev, data_metadata.st_ino) == (state_metadata.st_dev, state_metadata.st_ino)
            and max(data_extent.offset, state_extent.offset)
            < min(data_extent.offset + artifact.size, state_extent.offset + state_required)):
        _transfer_fail("INVALID_REQUEST", artifact.path, "data and checkpoint extents overlap")
    if (not isinstance(reservation, CapacityReservation) or not reservation.active
            or data_extent.operation_id != reservation.operation_id
            or state_extent.operation_id != reservation.operation_id
            or max(reservation.phase_totals, default=0) < artifact.size + state_required):
        _transfer_fail("CAPACITY_EXCEEDED", artifact.path, "an active reservation must contain data and checkpoint extents")

    loaded = _load_state(state_extent, artifact.path)
    if loaded is None:
        hasher = resumable_artifact_hasher(artifact.digest, artifact.path)
        header = {
            **identity,
            "generation": 0,
            "completed_count": 0,
            "contiguous_source_hash_offset": 0,
            "serialized_hash_state": artifact_hash_state(hasher, artifact.digest, 0, artifact.path),
            "contiguous_source_hash_digest": _source_hash_state(hasher, artifact.digest),
            "chunk_records_digest": "sha256:" + "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        }
        chunk_digests: tuple[str, ...] = ()
        _write_state(state_extent, header, artifact.path)
        records_hasher = resumable_artifact_hasher("sha256:" + "0" * 64, artifact.path)
    else:
        header, chunk_digests = loaded
        if any(header[name] != value for name, value in identity.items()):
            retained_progress = header["completed_count"] > 0
            header = _reset_state(state_extent, identity, header["generation"], artifact.path)
            chunk_digests = ()
            if retained_progress:
                _transfer_fail("SOURCE_REVISION_CHANGED", artifact.path, "checkpoint identity differs from the selected source object")
        records_hasher = resumable_artifact_hasher("sha256:" + "0" * 64, artifact.path)
        for digest in chunk_digests:
            records_hasher.update(b"\x01" + bytes.fromhex(digest[7:]))
        if _source_hash_state(records_hasher, "sha256:") != header["chunk_records_digest"]:
            _reset_state(state_extent, header, header["generation"], artifact.path)
            _transfer_fail("IDENTITY_MISMATCH", artifact.path, "transfer chunk records changed after checkpoint")
        try:
            hasher = resume_artifact_hasher(
                header["serialized_hash_state"],
                artifact.digest,
                header["contiguous_source_hash_offset"],
                artifact.path,
            )
        except CassetteError:
            _reset_state(state_extent, header, header["generation"], artifact.path)
            _transfer_fail("IDENTITY_MISMATCH", artifact.path, "serialized source hash state is invalid")
        if _source_hash_state(hasher, artifact.digest) != header["contiguous_source_hash_digest"]:
            _reset_state(state_extent, header, header["generation"], artifact.path)
            _transfer_fail("IDENTITY_MISMATCH", artifact.path, "serialized source hash state changed after checkpoint")
        if header["completed_count"] == header["chunk_count"]:
            if header["contiguous_source_hash_digest"] != artifact.digest:
                _reset_state(state_extent, header, header["generation"], artifact.path)
                _transfer_fail("IDENTITY_MISMATCH", artifact.path, "completed checkpoint does not carry the expected whole-object digest")
            return _partial(header, chunk_digests)
        for index, expected in enumerate(chunk_digests):
            offset = index * _TRANSFER_CHUNK_BYTES
            length = min(_TRANSFER_CHUNK_BYTES, artifact.size - offset)
            payload = _pread_exact(data_extent, offset, length, artifact.path)
            if digest_bytes(payload) != expected:
                _reset_state(state_extent, header, header["generation"], artifact.path)
                _transfer_fail("IDENTITY_MISMATCH", artifact.path, f"local transfer chunk {index} changed before resume")

    completed = header["completed_count"]
    while completed < header["chunk_count"]:
        indices = tuple(range(completed, min(completed + _TRANSFER_PARALLEL_RANGES, header["chunk_count"])))
        results = await asyncio.gather(*(
            adapter.open_range(
                revision,
                artifact,
                index * _TRANSFER_CHUNK_BYTES,
                min(_TRANSFER_CHUNK_BYTES, artifact.size - index * _TRANSFER_CHUNK_BYTES),
                artifact.validator,
            )
            for index in indices
        ), return_exceptions=True)
        revision_failure = next((
            result for result in results
            if isinstance(result, CassetteError) and result.code == "SOURCE_REVISION_CHANGED"
        ), None)
        failure = revision_failure or next(
            (result for result in results if isinstance(result, BaseException)), None
        )
        if failure is not None:
            if revision_failure is not None:
                header = _reset_state(state_extent, header, header["generation"], artifact.path)
            if isinstance(failure, asyncio.CancelledError):
                raise failure
            if isinstance(failure, CassetteError):
                raise failure
            _transfer_fail("SOURCE_UNAVAILABLE", artifact.path, f"range worker failed with {type(failure).__name__}", "retryable")
        for index, payload in zip(indices, results, strict=True):
            offset = index * _TRANSFER_CHUNK_BYTES
            length = min(_TRANSFER_CHUNK_BYTES, artifact.size - offset)
            network_digest = digest_bytes(payload)
            if (authoritative_chunk_digests is not None
                    and network_digest != authoritative_chunk_digests[index]):
                _reset_state(state_extent, header, header["generation"], artifact.path)
                _transfer_fail("IDENTITY_MISMATCH", artifact.path, f"source chunk {index} differs from its authoritative digest")
            _pwrite_all(data_extent, offset, payload, artifact.path)
            readback = _pread_exact(data_extent, offset, length, artifact.path)
            if digest_bytes(readback) != network_digest:
                _reset_state(state_extent, header, header["generation"], artifact.path)
                _transfer_fail("IDENTITY_MISMATCH", artifact.path, f"local write changed transfer chunk {index}")
            _sync_fd(data_extent.fd, artifact.path)
            hasher.update(payload)
            chunk = TransferChunk(identity["artifact_id"], offset, length, network_digest)
            chunk_record = b"\x01" + bytes.fromhex(chunk.blake3_digest[7:])
            _pwrite_verified(
                state_extent,
                _TRANSFER_RECORDS_OFFSET + index * _TRANSFER_RECORD_BYTES,
                chunk_record,
                artifact.path,
                f"transfer chunk record {index}",
            )
            records_hasher.update(chunk_record)
            completed += 1
            chunk_digests += (chunk.blake3_digest,)
            header = {
                **header,
                "generation": header["generation"] + 1,
                "completed_count": completed,
                "contiguous_source_hash_offset": min(completed * _TRANSFER_CHUNK_BYTES, artifact.size),
                "serialized_hash_state": artifact_hash_state(
                    hasher,
                    artifact.digest,
                    min(completed * _TRANSFER_CHUNK_BYTES, artifact.size),
                    artifact.path,
                ),
                "contiguous_source_hash_digest": _source_hash_state(hasher, artifact.digest),
                "chunk_records_digest": _source_hash_state(records_hasher, "sha256:"),
            }
            _write_state(state_extent, header, artifact.path)

    if header["contiguous_source_hash_digest"] != artifact.digest:
        _reset_state(state_extent, header, header["generation"], artifact.path)
        _transfer_fail("IDENTITY_MISMATCH", artifact.path, "whole source digest differs after all ranges completed")
    return _partial(header, chunk_digests)
