# sources.py — source resolution and resumable verified transfer (Q9/Q51/Q52); depends on errors.py, schema, store.py.
"""Normalize source wires and copy verified bytes into store-granted cartridge extents."""

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
    CapacityReservation,
    artifact_hash_state,
    canonical_bytes,
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
        return metadata

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
