# sources.py — stateless source resolution, metadata, range reads, and auth translation (Q9/Q52); depends on errors.py, schema.
"""Normalize source wires without owning acquisition, cartridge, or operation state."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import json
import re
from typing import Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urljoin, urlparse
from urllib.request import Request, urlopen

from errors import CassetteError
from schema.validator import validate

_CONTROL_BYTES = 8 * 1024 * 1024
_DIGEST = re.compile(r"(?P<algorithm>blake3|sha256|git-sha1):(?P<hex>[0-9a-f]+)")
_DIGEST_LENGTH = {"blake3": 64, "sha256": 64, "git-sha1": 40}


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
        if origin is None or origin.scheme not in {"http", "https"} or not origin.netloc or origin.username or origin.password or origin.query or origin.fragment:
            _fail("INVALID_REQUEST", self.kind, "Q52: adapter endpoint must be HTTP(S)", "base_url is invalid")

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
        )
        expected_range = f"bytes {offset}-{offset + length - 1}/{artifact.size}"
        if status != 206 or response_headers.get("Content-Range") != expected_range or response_headers.get("ETag") != validator or len(payload) != length:
            _fail("SOURCE_REVISION_CHANGED", artifact.path, "Q52: range response must retain validator, extent, and length", "source returned different range evidence")
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
            base_origin = urlparse(self.base_url)
            range_origin = urlparse(range_uri)
            if (range_origin.scheme, range_origin.netloc) != (base_origin.scheme, base_origin.netloc) or range_origin.username or range_origin.password or range_origin.query or range_origin.fragment:
                _fail("SOURCE_UNAVAILABLE", object_id, "Q9: credential-bearing range authority must remain on the selected source origin", path)
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
        return await asyncio.to_thread(self._blocking_request, url, request_headers, maximum, object_id)

    def _blocking_request(
        self,
        url: str,
        headers: dict[str, str],
        maximum: int,
        object_id: str,
    ) -> tuple[int, bytes, Mapping[str, str]]:
        try:
            with urlopen(Request(url, headers=headers), timeout=30) as response:
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
        except (URLError, OSError, TimeoutError) as error:
            _fail("SOURCE_UNAVAILABLE", object_id, "Q52: source endpoint must be reachable", type(error).__name__, "retryable")
