# broker.py — durable source-to-callable operations and canonical Q6 events (Q5/Q6/Q52); depends on errors.py, schema, sources.py, store.py.
"""Own the one operation log and drive preparation without reading cartridge extents."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Mapping
from contextlib import suppress
from dataclasses import dataclass
import fcntl
import inspect
import json
import os
from pathlib import Path
import re

from errors import CassetteError
from schema.validator import validate
from sources import Artifact, PartialState, ResolvedSource, SourceAdapter, TransferExtent, transfer_artifact
from store import (
    ArtifactIdentity,
    CapacityReservation,
    GenerationPin,
    canonical_bytes,
    commit_generation,
    digest_bytes,
    load_root,
    page_locations,
    recover_generation,
)

PROTOCOL_VERSION = "1"
PREPARE_OPERATION = "prepare"
PHASES = (
    "EMPTY",
    "RESOLVED",
    "RESERVED",
    "ACQUIRING",
    "SOURCE_VERIFIED",
    "PLANNED",
    "PREPARING",
    "EXEC_VERIFIED",
    "PUBLISHED",
    "ACTIVE",
)
_MUTABLE_PHASES = frozenset(PHASES[:8])
_TERMINAL_STATES = frozenset({"SUCCEEDED", "CANCELLED", "FAILED"})
_TERMINAL_EVENTS = frozenset({"completed", "cancelled", "failed"})
_OPERATION_ID = re.compile(r"op-[0-9a-f]{64}")
_DIGEST = re.compile(r"blake3:[0-9a-f]{64}")
_SOURCE_DIGEST = re.compile(r"(?:blake3|sha256):[0-9a-f]{64}|git-sha1:[0-9a-f]{40}")
_MAX_RECORD_BYTES = 4 * 1024 * 1024
_RECORD_FIELDS = frozenset({
    "version", "operation_id", "request_digest", "kind", "target", "phase", "state",
    "progress", "checkpoint", "result", "error", "cancel_requested", "pause_requested",
    "events",
})
_CHECKPOINT_FIELDS = {
    "EMPTY": frozenset(),
    "RESOLVED": frozenset({
        "source_lock", "parent_root", "metadata_digest", "requirements_digest",
    }),
    "RESERVED": frozenset({
        "source_lock", "parent_root", "metadata_digest", "requirements_digest", "capacity",
    }),
    "ACQUIRING": frozenset({
        "source_lock", "parent_root", "metadata_digest", "requirements_digest", "capacity",
    }),
    "SOURCE_VERIFIED": frozenset({
        "source_lock", "parent_root", "metadata_digest", "requirements_digest", "capacity",
        "partials",
    }),
    "PLANNED": frozenset({
        "source_lock", "parent_root", "metadata_digest", "requirements_digest", "capacity",
        "partials", "plan_digest",
    }),
    "PREPARING": frozenset({
        "source_lock", "parent_root", "metadata_digest", "requirements_digest", "capacity",
        "partials", "plan_digest",
    }),
    "EXEC_VERIFIED": frozenset({
        "source_lock", "parent_root", "metadata_digest", "requirements_digest", "capacity",
        "partials", "plan_digest", "source_verification", "candidate_root", "page_digests",
    }),
    "PUBLISHED": frozenset({
        "source_lock", "parent_root", "metadata_digest", "requirements_digest", "capacity",
        "partials", "plan_digest", "source_verification", "candidate_root", "page_digests",
        "generation",
    }),
    "ACTIVE": frozenset({
        "source_lock", "parent_root", "metadata_digest", "requirements_digest", "capacity",
        "partials", "plan_digest", "source_verification", "candidate_root", "page_digests",
        "generation",
    }),
}


@dataclass(frozen=True, slots=True)
class PreparedRevision:
    """The preparation owner's present-byte proof and verified canonical-root claim."""

    source_identity: str
    verified_artifacts: tuple[ArtifactIdentity, ...]
    plan_digest: str
    candidate_root: str


@dataclass(frozen=True, slots=True)
class AcquisitionContext:
    """Live authorities required to resume one Q5 preparation from its durable checkpoint."""

    adapter: SourceAdapter
    reservation: CapacityReservation
    transfers: Mapping[str, tuple[TransferExtent, TransferExtent]]
    cartridge: str | Path
    plan: Callable[[ResolvedSource, tuple[PartialState, ...]], object]
    prepare: Callable[[ResolvedSource, tuple[PartialState, ...], str], object]


class _ControlStop(Exception):
    def __init__(self, action: str):
        self.action = action


def _reject(
    code: str,
    object_id: str,
    detail: str,
    *,
    invariant: str = "Q5/Q6: one durable idempotent broker operation",
    retryability: str = "terminal",
) -> None:
    raise CassetteError(code, object_id, invariant, retryability, detail)


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError(f"duplicate JSON field {name!r}")
        result[name] = value
    return result


def _exact_digest(value: object, object_id: str, field: str) -> str:
    if not isinstance(value, str) or _DIGEST.fullmatch(value) is None:
        _reject("ROOT_INVALID", object_id, f"{field} must be one lowercase BLAKE3 digest")
    return value


def _json_digest(value: object, object_id: str, field: str) -> str:
    try:
        payload = canonical_bytes(value)
    except (TypeError, ValueError, OverflowError) as error:
        _reject("INVALID_REQUEST", object_id, f"{field} is not canonical JSON: {type(error).__name__}")
    if len(payload) > _MAX_RECORD_BYTES:
        _reject("INVALID_REQUEST", object_id, f"{field} exceeds {_MAX_RECORD_BYTES} canonical bytes")
    return digest_bytes(payload)


def _source_record(revision: ResolvedSource) -> dict:
    def artifact_record(artifact: Artifact) -> dict:
        return {
            "path": artifact.path,
            "size": artifact.size,
            "digest": artifact.digest,
            "range_uri": artifact.range_uri,
            "validator": artifact.validator,
        }

    return {
        "source_kind": revision.source_kind,
        "locator": revision.locator,
        "immutable_revision": revision.immutable_revision,
        "identity": revision.identity,
        "artifacts": [artifact_record(item) for item in revision.artifacts],
        "metadata_assets": [artifact_record(item) for item in revision.metadata_assets],
        "auth_scope": revision.auth_scope,
        "license_digest": revision.license_digest,
        "credential_ref": revision.credential_ref,
        "license_acceptance_ref": revision.license_acceptance_ref,
    }


def _source_from(record: object, object_id: str) -> ResolvedSource:
    fields = {
        "source_kind", "locator", "immutable_revision", "identity", "artifacts",
        "metadata_assets", "auth_scope", "license_digest", "credential_ref",
        "license_acceptance_ref",
    }
    if not isinstance(record, dict) or set(record) != fields:
        _reject("ROOT_INVALID", object_id, "source lock has an incorrect field set")

    def artifacts(value: object, field: str) -> tuple[Artifact, ...]:
        if not isinstance(value, list) or not value:
            _reject("ROOT_INVALID", object_id, f"source lock {field} must be a nonempty array")
        result = []
        for item in value:
            if not isinstance(item, dict) or set(item) != {
                "path", "size", "digest", "range_uri", "validator",
            }:
                _reject("ROOT_INVALID", object_id, f"source lock {field} contains a malformed artifact")
            if (
                not isinstance(item["path"], str)
                or type(item["size"]) is not int
                or item["size"] < 0
                or not isinstance(item["digest"], str)
                or _SOURCE_DIGEST.fullmatch(item["digest"]) is None
                or not isinstance(item["range_uri"], str)
                or not isinstance(item["validator"], str)
            ):
                _reject("ROOT_INVALID", object_id, f"source lock {field} contains an invalid artifact")
            result.append(Artifact(
                item["path"], item["size"], item["digest"], item["range_uri"], item["validator"]
            ))
        if tuple(item.path for item in result) != tuple(sorted(item.path for item in result)):
            _reject("ROOT_INVALID", object_id, f"source lock {field} is not canonically ordered")
        if len({item.path for item in result}) != len(result):
            _reject("ROOT_INVALID", object_id, f"source lock {field} contains duplicate paths")
        return tuple(result)

    text_fields = (
        "source_kind", "locator", "immutable_revision", "identity", "auth_scope", "license_digest",
    )
    if any(not isinstance(record[field], str) or not record[field] for field in text_fields):
        _reject("ROOT_INVALID", object_id, "source lock contains empty or non-text identity material")
    for field in ("immutable_revision", "identity", "license_digest"):
        if _SOURCE_DIGEST.fullmatch(record[field]) is None:
            _reject("ROOT_INVALID", object_id, f"source lock {field} is not a canonical digest")
    for field in ("credential_ref", "license_acceptance_ref"):
        if record[field] is not None and (not isinstance(record[field], str) or not record[field]):
            _reject("ROOT_INVALID", object_id, f"source lock {field} must be null or nonempty text")
    revision = ResolvedSource(
        record["source_kind"],
        record["locator"],
        record["immutable_revision"],
        record["identity"],
        artifacts(record["artifacts"], "artifacts"),
        artifacts(record["metadata_assets"], "metadata_assets"),
        record["auth_scope"],
        record["license_digest"],
        record["credential_ref"],
        record["license_acceptance_ref"],
    )
    if _source_record(revision) != record:
        _reject("ROOT_INVALID", object_id, "source lock does not round-trip exactly")
    return revision


def _partial_record(path: str, partial: PartialState) -> dict:
    return {
        "path": path,
        "source_revision": partial.source_revision,
        "object_size": partial.object_size,
        "validator": partial.validator,
        "completed_interval_set": [list(interval) for interval in partial.completed_interval_set],
        "chunk_digests": list(partial.chunk_digests),
        "contiguous_source_hash_offset": partial.contiguous_source_hash_offset,
        "serialized_hash_state": partial.serialized_hash_state,
    }


def _partials_from(records: object, revision: ResolvedSource, object_id: str) -> tuple[PartialState, ...]:
    if not isinstance(records, list) or len(records) != len(revision.artifacts):
        _reject("ROOT_INVALID", object_id, "source verification must contain one record per artifact")
    by_path = {artifact.path: artifact for artifact in revision.artifacts}
    result = []
    for record in records:
        if not isinstance(record, dict) or set(record) != {
            "path", "source_revision", "object_size", "validator", "completed_interval_set",
            "chunk_digests", "contiguous_source_hash_offset", "serialized_hash_state",
        }:
            _reject("ROOT_INVALID", object_id, "source verification record has an incorrect field set")
        artifact = by_path.get(record["path"])
        intervals = record["completed_interval_set"]
        chunks = record["chunk_digests"]
        if (
            artifact is None
            or record["source_revision"] != revision.immutable_revision
            or record["object_size"] != artifact.size
            or record["validator"] != artifact.validator
            or intervals != [[0, artifact.size]]
            or type(record["contiguous_source_hash_offset"]) is not int
            or record["contiguous_source_hash_offset"] != artifact.size
            or not isinstance(chunks, list)
            or not chunks
            or any(not isinstance(item, str) or _DIGEST.fullmatch(item) is None for item in chunks)
            or not isinstance(record["serialized_hash_state"], str)
        ):
            _reject("ROOT_INVALID", object_id, f"source verification for {record.get('path')!r} is incomplete")
        result.append(PartialState(
            record["source_revision"],
            record["object_size"],
            record["validator"],
            tuple(tuple(interval) for interval in intervals),
            tuple(chunks),
            record["contiguous_source_hash_offset"],
            record["serialized_hash_state"],
        ))
    if [record["path"] for record in records] != sorted(by_path):
        _reject("ROOT_INVALID", object_id, "source verification records are not canonically ordered")
    return tuple(result)


class CanonicalBroker:
    """Persist Q6 operations and execute each Q5 transition from its last durable phase."""

    def __init__(self, operation_log: str | Path):
        self.operation_log = Path(operation_log)
        try:
            self.operation_log.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            _reject("DURABILITY_UNSUPPORTED", "broker:operation-log", f"operation-log creation failed: {error}")
        self._execution_locks: dict[str, asyncio.Lock] = {}
        self._control_signals: dict[str, asyncio.Event] = {}
        self._active: dict[str, bool] = {}

    @staticmethod
    def operation_id(request: dict) -> str:
        """Derive one stable operation ID from the exact Q6 idempotency-key scope."""

        defects = validate("request", request)
        if defects:
            _reject("INVALID_REQUEST", "request:unidentified", "; ".join(defects))
        if request["protocol_version"] != PROTOCOL_VERSION:
            _reject("INVALID_REQUEST", request["idempotency_key"], "unsupported protocol_version")
        _json_digest(request, request["idempotency_key"], "request")
        identity = digest_bytes(canonical_bytes({"idempotency_key": request["idempotency_key"]}))
        return "op-" + identity[7:]

    def issue(self, request: dict) -> dict:
        """Create one operation or return the exact operation already bound to its key."""

        operation_id = self.operation_id(request)
        request_digest = _json_digest(request, operation_id, "request")
        path = self._path(operation_id)
        if path.exists():
            record = self._load(operation_id)
            if record["request_digest"] != request_digest:
                _reject(
                    "IDEMPOTENCY_CONFLICT",
                    operation_id,
                    "idempotency key is already bound to another canonical request",
                )
            return self._operation(record)
        event = self._event(operation_id, 0, "started", {
            "kind": request["operation"], "phase": "EMPTY",
        })
        record = {
            "version": PROTOCOL_VERSION,
            "operation_id": operation_id,
            "request_digest": request_digest,
            "kind": request["operation"],
            "target": request.get("target"),
            "phase": "EMPTY",
            "state": "PENDING",
            "progress": 0.0,
            "checkpoint": {},
            "result": None,
            "error": None,
            "cancel_requested": False,
            "pause_requested": False,
            "events": [event],
        }
        self._write(record)
        return self._operation(record)

    def status(self, operation_id: str) -> dict:
        """Return one schema-valid operation from its verified durable record."""

        return self._operation(self._load(operation_id))

    def events(self, operation_id: str, after: int = -1) -> tuple[dict, ...]:
        """Return the complete contiguous event suffix after one caller-owned sequence."""

        if type(after) is not int or after < -1:
            _reject("INVALID_REQUEST", operation_id, "after must be an integer at least -1")
        return tuple(event for event in self._load(operation_id)["events"] if event["sequence"] > after)

    def cancel(self, operation_id: str) -> dict:
        """Request cooperative cancellation, or terminate immediately when no phase is running."""

        record = self._load(operation_id)
        if record["state"] in _TERMINAL_STATES:
            return self._operation(record)
        if record["phase"] not in _MUTABLE_PHASES:
            _reject("INVALID_REQUEST", operation_id, f"phase {record['phase']} is no longer cancellable")
        if operation_id in self._active and not self._active[operation_id]:
            _reject("INVALID_REQUEST", operation_id, "the durable publication boundary is not cancellable")
        record = {**record, "cancel_requested": True, "pause_requested": False}
        self._write(record)
        self._signal(operation_id).set()
        if operation_id in self._active:
            return self._operation(record)
        return self._terminal(record, self._cancel_error(record), "CANCELLED", "cancelled")

    def pause(self, operation_id: str) -> dict:
        """Pause before another mutable side effect and retain the last completed Q5 phase."""

        record = self._load(operation_id)
        if record["state"] in _TERMINAL_STATES:
            return self._operation(record)
        if record["phase"] not in _MUTABLE_PHASES:
            _reject("INVALID_REQUEST", operation_id, f"phase {record['phase']} is no longer pausable")
        record = {**record, "pause_requested": True, "cancel_requested": False}
        self._write(record)
        self._signal(operation_id).set()
        if operation_id in self._active:
            return self._operation(record)
        return self._paused(record)

    def resume(self, operation_id: str) -> dict:
        """Clear one durable pause request without changing its last completed phase."""

        record = self._load(operation_id)
        if record["state"] in _TERMINAL_STATES:
            return self._operation(record)
        if record["state"] != "PAUSED" and not record["pause_requested"]:
            return self._operation(record)
        state = "PENDING" if record["phase"] == "EMPTY" else "RUNNING"
        record = self._append(record, "output_delta", {
            "phase": record["phase"], "state": state,
        }, state=state, pause_requested=False)
        self._signal(operation_id).clear()
        return self._operation(record)

    async def execute(self, request: dict, worker: Callable[[], object]) -> dict:
        """Run one non-preparation Q6 operation through the same error, event, and cancellation log."""

        operation = self.issue(request)
        operation_id = operation["operation_id"]
        if request["operation"] == PREPARE_OPERATION:
            _reject("INVALID_REQUEST", operation_id, "prepare must use the Q5 acquisition state machine")
        async with self._lock(operation_id):
            record = self._load(operation_id)
            if record["state"] in _TERMINAL_STATES or record["state"] == "PAUSED":
                return self._operation(record)
            record = self._append(record, "output_delta", {
                "phase": "EMPTY", "state": "RUNNING",
            }, state="RUNNING")
            try:
                result = await self._controlled(operation_id, worker, cancellable=True)
                if not isinstance(result, dict):
                    _reject("INVALID_REQUEST", operation_id, "operation worker must return one result object")
                _json_digest(result, operation_id, "operation result")
                return self._operation(self._success(self._load(operation_id), result))
            except _ControlStop as stopped:
                return self._operation(self._stop(self._load(operation_id), stopped.action))
            except asyncio.CancelledError:
                raise
            except CassetteError as error:
                return self._operation(self._failed(self._load(operation_id), error))

    async def advance_acquisition(self, request: dict, context: AcquisitionContext) -> dict:
        """Execute exactly one Q5 transition; a new broker process may execute the next one."""

        operation = self.issue(request)
        operation_id = operation["operation_id"]
        if request["operation"] != PREPARE_OPERATION:
            _reject("INVALID_REQUEST", operation_id, "acquisition requires operation='prepare'")
        async with self._lock(operation_id):
            record = self._load(operation_id)
            if record["state"] in _TERMINAL_STATES or record["state"] == "PAUSED":
                return self._operation(record)
            try:
                if record["cancel_requested"]:
                    raise _ControlStop("cancel")
                if record["pause_requested"]:
                    raise _ControlStop("pause")
                return self._operation(await self._advance(record, request, context))
            except _ControlStop as stopped:
                return self._operation(self._stop(self._load(operation_id), stopped.action))
            except asyncio.CancelledError:
                raise
            except CassetteError as error:
                return self._operation(self._failed(self._load(operation_id), error))

    async def run_acquisition(self, request: dict, context: AcquisitionContext) -> dict:
        """Resume Q5 until ACTIVE or one typed terminal result, never past the last durable phase."""

        for _ in range(len(PHASES) + 1):
            operation = await self.advance_acquisition(request, context)
            if operation["state"] in _TERMINAL_STATES or operation["state"] == "PAUSED":
                return operation
        _reject("CAPABILITY_MISMATCH", operation["operation_id"], "Q5 state machine exceeded its exact phase count")

    def callable_revision(self, operation_id: str, cartridge: str | Path) -> GenerationPin:
        """Return only a store-verified generation whose broker phase reached PUBLISHED."""

        record = self._load(operation_id)
        if record["phase"] not in {"PUBLISHED", "ACTIVE"}:
            _reject(
                "OPERATION_NOT_FOUND",
                operation_id,
                f"phase {record['phase']} has no callable revision",
                invariant="Q5: only a verified PUBLISHED revision is callable",
            )
        generation = record["checkpoint"]["generation"]
        pin = recover_generation(cartridge)
        if pin is None or pin.root_digest != generation["root_digest"] or pin.child_id != generation["child_id"]:
            _reject("ROOT_INVALID", operation_id, "published generation no longer verifies against the store")
        return pin

    async def _advance(self, record: dict, request: dict, context: AcquisitionContext) -> dict:
        operation_id = record["operation_id"]
        if not isinstance(context, AcquisitionContext):
            _reject("INVALID_REQUEST", operation_id, "AcquisitionContext is required")
        descriptor = request["arguments"].get("source") if isinstance(request["arguments"], dict) else None
        defects = validate("source_descriptor", descriptor)
        if defects:
            _reject("INVALID_REQUEST", operation_id, "; ".join(defects))
        phase = record["phase"]
        checkpoint = dict(record["checkpoint"])
        if phase == "EMPTY":
            async def resolve():
                revision = await context.adapter.resolve(descriptor)
                if await context.adapter.enumerate(revision) != revision.artifacts:
                    _reject("SOURCE_REVISION_CHANGED", revision.locator, "enumeration changed after resolution")
                metadata = await context.adapter.read_metadata(revision)
                requirements = await context.adapter.license_and_auth(revision)
                parent = await asyncio.to_thread(recover_generation, context.cartridge)
                return {
                    "source_lock": _source_record(revision),
                    "parent_root": None if parent is None else parent.root_digest,
                    "metadata_digest": _json_digest(metadata, operation_id, "source metadata"),
                    "requirements_digest": _json_digest(
                        requirements.record(), operation_id, "source requirements"
                    ),
                }

            checkpoint.update(await self._controlled(operation_id, resolve, cancellable=True))
            return self._phase(record, "RESOLVED", checkpoint)
        revision = _source_from(checkpoint["source_lock"], operation_id)
        if context.adapter.kind != revision.source_kind:
            _reject("INVALID_REQUEST", operation_id, "adapter differs from the durable source lock")
        if phase != "RESOLVED":
            observed_capacity = self._capacity(context.reservation, operation_id)
            if observed_capacity != checkpoint["capacity"]:
                _reject(
                    "IDEMPOTENCY_CONFLICT",
                    operation_id,
                    "live reservation differs from the durable capacity commitment",
                )
        if phase == "RESOLVED":
            checkpoint["capacity"] = self._capacity(context.reservation, operation_id)
            return self._phase(record, "RESERVED", checkpoint)
        if phase == "RESERVED":
            return self._phase(record, "ACQUIRING", checkpoint)
        if phase == "ACQUIRING":
            async def acquire():
                if not isinstance(context.transfers, Mapping) or set(context.transfers) != {
                    artifact.path for artifact in revision.artifacts
                }:
                    _reject("INVALID_REQUEST", operation_id, "transfers must name every source artifact exactly once")
                partials = []
                for artifact in revision.artifacts:
                    extents = context.transfers[artifact.path]
                    if not isinstance(extents, tuple) or len(extents) != 2:
                        _reject("INVALID_REQUEST", operation_id, f"{artifact.path} requires data and state extents")
                    partials.append(await transfer_artifact(
                        context.adapter,
                        revision,
                        artifact,
                        extents[0],
                        extents[1],
                        context.reservation,
                    ))
                return [
                    _partial_record(artifact.path, partial)
                    for artifact, partial in zip(revision.artifacts, partials, strict=True)
                ]

            checkpoint["partials"] = await self._controlled(operation_id, acquire, cancellable=True)
            _partials_from(checkpoint["partials"], revision, operation_id)
            return self._phase(record, "SOURCE_VERIFIED", checkpoint)
        partials = _partials_from(checkpoint["partials"], revision, operation_id)
        if phase == "SOURCE_VERIFIED":
            plan_digest = await self._controlled(
                operation_id,
                lambda: context.plan(revision, partials),
                cancellable=True,
            )
            checkpoint["plan_digest"] = _exact_digest(plan_digest, operation_id, "plan digest")
            return self._phase(record, "PLANNED", checkpoint)
        if phase == "PLANNED":
            return self._phase(record, "PREPARING", checkpoint)
        if phase == "PREPARING":
            prepared = await self._controlled(
                operation_id,
                lambda: context.prepare(revision, partials, checkpoint["plan_digest"]),
                cancellable=True,
            )
            checkpoint.update(await asyncio.to_thread(
                self._verify_prepared,
                operation_id,
                context.cartridge,
                revision,
                checkpoint["plan_digest"],
                prepared,
            ))
            return self._phase(record, "EXEC_VERIFIED", checkpoint)
        if phase == "EXEC_VERIFIED":
            pin = await self._controlled(
                operation_id,
                lambda: commit_generation(
                    context.cartridge,
                    operation_id,
                    checkpoint["candidate_root"],
                    expected_parent_root=checkpoint["parent_root"],
                ),
                cancellable=False,
            )
            checkpoint["generation"] = {
                "generation": pin.generation,
                "child_id": pin.child_id,
                "root_digest": pin.root_digest,
            }
            return self._phase(record, "PUBLISHED", checkpoint)
        if phase == "PUBLISHED":
            pin = await self._controlled(
                operation_id,
                lambda: recover_generation(context.cartridge),
                cancellable=False,
            )
            generation = checkpoint["generation"]
            if (
                pin is None
                or pin.generation != generation["generation"]
                or pin.child_id != generation["child_id"]
                or pin.root_digest != generation["root_digest"]
            ):
                _reject("ROOT_INVALID", operation_id, "published generation failed activation verification")
            result = {
                "model_identity": revision.identity,
                "generation": pin.generation,
                "revision_id": pin.child_id,
                "root_digest": pin.root_digest,
            }
            return self._success(
                record,
                result,
                phase="ACTIVE",
                checkpoint=checkpoint,
                event_payload={"phase": "ACTIVE", "result": result},
            )
        return record

    @staticmethod
    def _verify_prepared(
        operation_id: str,
        cartridge: str | Path,
        revision: ResolvedSource,
        plan_digest: str,
        prepared: object,
    ) -> dict:
        if not isinstance(prepared, PreparedRevision):
            _reject(
                "CAPABILITY_MISMATCH",
                operation_id,
                "preparation must return present-byte verification and a canonical root; PartialState is insufficient",
            )
        if prepared.source_identity != revision.identity or prepared.plan_digest != plan_digest:
            _reject("IDENTITY_MISMATCH", operation_id, "preparation result differs from the source lock or plan")
        expected = tuple(
            ArtifactIdentity(artifact.path, artifact.size, artifact.digest)
            for artifact in revision.artifacts
        )
        if prepared.verified_artifacts != expected:
            _reject("IDENTITY_MISMATCH", operation_id, "present-byte verification differs from resolved artifacts")
        root_digest = _exact_digest(prepared.candidate_root, operation_id, "candidate root")
        root = load_root(cartridge, root_digest)
        identity_material = root.get("provenance", {}).get("identity_material", {})
        if (
            root.get("identity") != revision.identity
            or identity_material.get("source_kind") != revision.source_kind
            or identity_material.get("locator") != revision.locator
            or identity_material.get("immutable_revision") != revision.immutable_revision
            or identity_material.get("artifacts") != [
                {"path": item.path, "size": item.size, "digest": item.digest} for item in expected
            ]
        ):
            _reject("IDENTITY_MISMATCH", operation_id, "candidate root is not bound to the durable source lock")
        pages = [location.page_digest for location in page_locations(cartridge, root_digest)]
        return {
            "source_verification": [
                {"path": item.path, "size": item.size, "digest": item.digest} for item in expected
            ],
            "candidate_root": root_digest,
            "page_digests": pages,
        }

    async def _controlled(
        self, operation_id: str, worker: Callable[[], object], *, cancellable: bool
    ) -> object:
        if not callable(worker):
            _reject("INVALID_REQUEST", operation_id, "operation worker must be callable")

        async def invoke():
            if inspect.iscoroutinefunction(worker):
                return await worker()
            value = worker()
            return await value if inspect.isawaitable(value) else value

        signal = self._signal(operation_id)
        signal.clear()
        self._active[operation_id] = cancellable
        task = asyncio.create_task(invoke())
        waiter = asyncio.create_task(signal.wait()) if cancellable else None
        try:
            if waiter is None:
                return await task
            done, _ = await asyncio.wait((task, waiter), return_when=asyncio.FIRST_COMPLETED)
            record = self._load(operation_id)
            if waiter in done or record["cancel_requested"] or record["pause_requested"]:
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task
                raise _ControlStop("cancel" if record["cancel_requested"] else "pause")
            return await task
        except asyncio.CancelledError:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
            raise
        except CassetteError:
            raise
        except _ControlStop:
            raise
        except Exception as error:
            _reject(
                "CAPABILITY_MISMATCH",
                operation_id,
                f"operation worker raised {type(error).__name__}",
            )
        finally:
            if waiter is not None:
                waiter.cancel()
            self._active.pop(operation_id, None)

    def _verify_record(self, record: object, object_id: str) -> dict:
        if not isinstance(record, dict) or set(record) != _RECORD_FIELDS:
            _reject("ROOT_INVALID", object_id, "operation record has an incorrect field set")
        if (
            record["version"] != PROTOCOL_VERSION
            or record["operation_id"] != object_id
            or _OPERATION_ID.fullmatch(object_id) is None
            or _DIGEST.fullmatch(record["request_digest"]) is None
            or not isinstance(record["kind"], str)
            or not record["kind"]
            or (record["target"] is not None and (not isinstance(record["target"], str) or not record["target"]))
            or record["phase"] not in PHASES
            or record["state"] not in {"PENDING", "RUNNING", "PAUSED", *_TERMINAL_STATES}
            or not isinstance(record["cancel_requested"], bool)
            or not isinstance(record["pause_requested"], bool)
            or not isinstance(record["checkpoint"], dict)
        ):
            _reject("ROOT_INVALID", object_id, "operation record contains malformed identity or state")
        operation = self._operation(record, validate_record=False)
        defects = validate("operation", operation)
        if defects or not 0.0 <= operation["progress"] <= 1.0:
            _reject("ROOT_INVALID", object_id, "; ".join(defects) or "operation progress is outside [0,1]")
        if record["result"] is not None:
            _json_digest(record["result"], object_id, "durable result")
        if record["error"] is not None and validate("error", record["error"]):
            _reject("ROOT_INVALID", object_id, "durable error does not conform to Q6")
        events = record["events"]
        if not isinstance(events, list) or not events:
            _reject("ROOT_INVALID", object_id, "operation event log is empty")
        for sequence, event in enumerate(events):
            defects = validate("run_event", event)
            if defects or event.get("run_id") != object_id or event.get("sequence") != sequence:
                _reject("ROOT_INVALID", object_id, "; ".join(defects) or "operation event sequence is not contiguous")
        if events[0] != self._event(object_id, 0, "started", {
            "kind": record["kind"], "phase": "EMPTY",
        }):
            _reject("ROOT_INVALID", object_id, "operation event log does not begin with its exact start")
        terminals = [event for event in events if event["type"] in _TERMINAL_EVENTS]
        if (record["state"] in _TERMINAL_STATES) != (len(terminals) == 1 and terminals[-1] is events[-1]):
            _reject("ROOT_INVALID", object_id, "terminal state and terminal event disagree")
        if record["state"] in _TERMINAL_STATES and terminals[0]["type"] != {
            "SUCCEEDED": "completed", "CANCELLED": "cancelled", "FAILED": "failed",
        }[record["state"]]:
            _reject("ROOT_INVALID", object_id, "terminal event type disagrees with operation state")
        if record["state"] == "SUCCEEDED":
            expected_payload = (
                {"phase": "ACTIVE", "result": record["result"]}
                if record["kind"] == PREPARE_OPERATION
                else record["result"]
            )
            if events[-1]["payload"] != expected_payload:
                _reject("ROOT_INVALID", object_id, "completed event differs from the durable result")
        if record["state"] in {"FAILED", "CANCELLED"} and events[-1]["payload"] != {
            "error": record["error"],
        }:
            _reject("ROOT_INVALID", object_id, "terminal event differs from the durable error")
        if record["state"] not in _TERMINAL_STATES and terminals:
            _reject("ROOT_INVALID", object_id, "nonterminal operation contains a terminal event")
        if record["state"] in {"SUCCEEDED", "FAILED", "CANCELLED"} and (
            record["cancel_requested"] or record["pause_requested"]
        ):
            _reject("ROOT_INVALID", object_id, "terminal operation retains a control request")
        if record["state"] == "SUCCEEDED" and (record["result"] is None or record["error"] is not None):
            _reject("ROOT_INVALID", object_id, "successful operation requires only a result")
        if record["state"] in {"FAILED", "CANCELLED"} and (
            record["error"] is None or record["result"] is not None
        ):
            _reject("ROOT_INVALID", object_id, "failed or cancelled operation requires only an error")
        if record["state"] not in _TERMINAL_STATES and (
            record["result"] is not None or record["error"] is not None
        ):
            _reject("ROOT_INVALID", object_id, "nonterminal operation carries a terminal payload")
        if record["kind"] == PREPARE_OPERATION:
            if set(record["checkpoint"]) != _CHECKPOINT_FIELDS[record["phase"]]:
                _reject("ROOT_INVALID", object_id, f"checkpoint does not match phase {record['phase']}")
            transitions = [
                event["payload"]["phase"]
                for event in events
                if "phase" in event["payload"] and "state" not in event["payload"]
            ]
            if transitions != list(PHASES[:PHASES.index(record["phase"]) + 1]):
                _reject("ROOT_INVALID", object_id, "event phases do not form the exact Q5 prefix")
            if record["phase"] == "EMPTY" and record["state"] not in {
                "PENDING", "PAUSED", "CANCELLED", "FAILED",
            }:
                _reject("ROOT_INVALID", object_id, "EMPTY preparation has an impossible operation state")
            if record["phase"] in PHASES[1:-1] and record["state"] not in {
                "RUNNING", "PAUSED", "CANCELLED", "FAILED",
            }:
                _reject("ROOT_INVALID", object_id, "preparation phase has an impossible operation state")
            if record["phase"] == "ACTIVE" and record["state"] != "SUCCEEDED":
                _reject("ROOT_INVALID", object_id, "ACTIVE preparation must be successful")
            self._verify_checkpoint(record, object_id)
        return record

    def _verify_checkpoint(self, record: dict, object_id: str) -> None:
        phase = PHASES.index(record["phase"])
        checkpoint = record["checkpoint"]
        if phase == 0:
            return
        revision = _source_from(checkpoint["source_lock"], object_id)
        if checkpoint["parent_root"] is not None:
            _exact_digest(checkpoint["parent_root"], object_id, "parent root")
        _exact_digest(checkpoint["metadata_digest"], object_id, "metadata digest")
        _exact_digest(checkpoint["requirements_digest"], object_id, "requirements digest")
        if phase >= PHASES.index("RESERVED"):
            capacity = checkpoint["capacity"]
            if not isinstance(capacity, dict) or set(capacity) != {
                "device_bytes", "safety_bytes", "phase_totals", "repair_bytes", "required_bytes",
            }:
                _reject("ROOT_INVALID", object_id, "capacity checkpoint has an incorrect field set")
            values = [
                capacity["device_bytes"], capacity["safety_bytes"], capacity["repair_bytes"],
                capacity["required_bytes"],
            ]
            if (
                any(type(value) is not int or value < 0 for value in values)
                or not isinstance(capacity["phase_totals"], list)
                or not capacity["phase_totals"]
                or any(type(value) is not int or value < 0 for value in capacity["phase_totals"])
            ):
                _reject("ROOT_INVALID", object_id, "capacity checkpoint contains invalid byte counts")
        if phase >= PHASES.index("SOURCE_VERIFIED"):
            _partials_from(checkpoint["partials"], revision, object_id)
        if phase >= PHASES.index("PLANNED"):
            _exact_digest(checkpoint["plan_digest"], object_id, "plan digest")
        if phase >= PHASES.index("EXEC_VERIFIED"):
            verification = checkpoint["source_verification"]
            expected = [
                {"path": item.path, "size": item.size, "digest": item.digest}
                for item in revision.artifacts
            ]
            if verification != expected:
                _reject("ROOT_INVALID", object_id, "present-byte verification differs from the source lock")
            _exact_digest(checkpoint["candidate_root"], object_id, "candidate root")
            pages = checkpoint["page_digests"]
            if (
                not isinstance(pages, list)
                or not pages
                or pages != sorted(set(pages))
                or any(not isinstance(page, str) or _DIGEST.fullmatch(page) is None for page in pages)
            ):
                _reject("ROOT_INVALID", object_id, "page digest checkpoint is not exact and canonical")
        if phase >= PHASES.index("PUBLISHED"):
            generation = checkpoint["generation"]
            if (
                not isinstance(generation, dict)
                or set(generation) != {"generation", "child_id", "root_digest"}
                or type(generation["generation"]) is not int
                or generation["generation"] < 1
                or generation["root_digest"] != checkpoint["candidate_root"]
            ):
                _reject("ROOT_INVALID", object_id, "published generation checkpoint is malformed")
            _exact_digest(generation["child_id"], object_id, "published revision identity")
            _exact_digest(generation["root_digest"], object_id, "published root")

    @staticmethod
    def _capacity(reservation: object, operation_id: str) -> dict:
        if (
            not isinstance(reservation, CapacityReservation)
            or not reservation.active
            or reservation.operation_id != operation_id
        ):
            _reject("CAPACITY_EXCEEDED", operation_id, "active reservation is not bound to this operation")
        return {
            "device_bytes": reservation.device_bytes,
            "safety_bytes": reservation.safety_bytes,
            "phase_totals": list(reservation.phase_totals),
            "repair_bytes": reservation.repair_bytes,
            "required_bytes": reservation.required_bytes,
        }

    def _operation(self, record: dict, *, validate_record: bool = True) -> dict:
        if validate_record:
            self._verify_record(record, record.get("operation_id", "operation:unidentified"))
        result = {
            "operation_id": record["operation_id"],
            "kind": record["kind"],
            "state": record["state"],
            "progress": record["progress"],
        }
        if record["result"] is not None:
            result["result"] = record["result"]
        if record["error"] is not None:
            result["error"] = record["error"]
        return result

    def _phase(self, record: dict, phase: str, checkpoint: dict) -> dict:
        if PHASES.index(phase) != PHASES.index(record["phase"]) + 1:
            _reject("ROOT_INVALID", record["operation_id"], f"illegal Q5 transition {record['phase']} -> {phase}")
        return self._append(
            record,
            "output_delta",
            {"phase": phase},
            phase=phase,
            state="RUNNING",
            progress=PHASES.index(phase) / (len(PHASES) - 1),
            checkpoint=checkpoint,
        )

    def _success(
        self,
        record: dict,
        result: dict,
        *,
        phase: str | None = None,
        checkpoint: dict | None = None,
        event_payload: dict | None = None,
    ) -> dict:
        changes = {}
        if phase is not None:
            if PHASES.index(phase) != PHASES.index(record["phase"]) + 1:
                _reject(
                    "ROOT_INVALID",
                    record["operation_id"],
                    f"illegal Q5 transition {record['phase']} -> {phase}",
                )
            changes.update(phase=phase, checkpoint=checkpoint)
        return self._append(
            record,
            "completed",
            result if event_payload is None else event_payload,
            state="SUCCEEDED",
            progress=1.0,
            result=result,
            error=None,
            cancel_requested=False,
            pause_requested=False,
            **changes,
        )

    def _failed(self, record: dict, error: CassetteError) -> dict:
        state = "CANCELLED" if error.code == "OPERATION_CANCELLED" else "FAILED"
        event = "cancelled" if state == "CANCELLED" else "failed"
        return self._terminal(record, error, state, event)

    def _terminal(self, record: dict, error: CassetteError, state: str, event: str) -> dict:
        if record["state"] in _TERMINAL_STATES:
            return record
        payload = error.payload()
        return self._append(
            record,
            event,
            {"error": payload},
            state=state,
            result=None,
            error=payload,
            cancel_requested=False,
            pause_requested=False,
        )

    def _paused(self, record: dict) -> dict:
        return self._append(
            record,
            "output_delta",
            {"phase": record["phase"], "state": "PAUSED"},
            state="PAUSED",
            pause_requested=False,
        )

    def _stop(self, record: dict, action: str) -> dict:
        if action == "pause":
            return self._paused(record)
        return self._terminal(record, self._cancel_error(record), "CANCELLED", "cancelled")

    @staticmethod
    def _cancel_error(record: dict) -> CassetteError:
        return CassetteError(
            "OPERATION_CANCELLED",
            record["operation_id"],
            "Q5/Q6: cooperative cancellation retains the last hashed commit",
            "terminal",
            f"cancelled at {record['phase']}",
        )

    def _append(self, record: dict, event_type: str, payload: dict, **changes) -> dict:
        event = self._event(record["operation_id"], len(record["events"]), event_type, payload)
        updated = {**record, **changes, "events": [*record["events"], event]}
        self._write(updated)
        return updated

    @staticmethod
    def _event(operation_id: str, sequence: int, event_type: str, payload: dict) -> dict:
        event = {
            "run_id": operation_id,
            "sequence": sequence,
            "type": event_type,
            "payload": payload,
        }
        defects = validate("run_event", event)
        if defects:
            _reject("INVALID_REQUEST", operation_id, "; ".join(defects))
        return event

    def _path(self, operation_id: str) -> Path:
        if not isinstance(operation_id, str) or _OPERATION_ID.fullmatch(operation_id) is None:
            _reject("OPERATION_NOT_FOUND", "operation:unidentified", "operation_id is malformed")
        return self.operation_log / f"{operation_id}.json"

    def _load(self, operation_id: str) -> dict:
        path = self._path(operation_id)
        try:
            payload = path.read_bytes()
        except FileNotFoundError:
            _reject("OPERATION_NOT_FOUND", operation_id, "operation record does not exist")
        except OSError as error:
            _reject("DURABILITY_UNSUPPORTED", operation_id, f"operation record read failed: {error}")
        if len(payload) > _MAX_RECORD_BYTES:
            _reject("ROOT_INVALID", operation_id, "operation record exceeds its fixed byte bound")
        try:
            envelope = json.loads(payload, object_pairs_hook=_unique_object)
            if canonical_bytes(envelope) != payload or set(envelope) != {"digest", "record"}:
                raise ValueError("operation envelope is not exact canonical content")
            record = envelope["record"]
            if envelope["digest"] != digest_bytes(canonical_bytes(record)):
                raise ValueError("operation envelope digest disagrees with its record")
        except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as error:
            _reject("ROOT_INVALID", operation_id, f"operation record is unavailable or malformed: {error}")
        return self._verify_record(record, operation_id)

    def _write(self, record: dict) -> None:
        operation_id = record["operation_id"]
        self._verify_record(record, operation_id)
        body = canonical_bytes(record)
        payload = canonical_bytes({"digest": digest_bytes(body), "record": record})
        if len(payload) > _MAX_RECORD_BYTES:
            _reject("OVERLOADED", operation_id, "operation record exceeds its fixed byte bound")
        path = self._path(operation_id)
        temporary = path.with_name(f".{path.name}.pending")
        try:
            with temporary.open("wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
                command = getattr(fcntl, "F_FULLFSYNC", None)
                if command is not None:
                    fcntl.fcntl(handle.fileno(), command)
            if temporary.read_bytes() != payload:
                _reject("DURABILITY_UNSUPPORTED", operation_id, "operation-log readback changed")
            os.replace(temporary, path)
            descriptor = os.open(self.operation_log, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        except CassetteError:
            raise
        except OSError as error:
            _reject("DURABILITY_UNSUPPORTED", operation_id, f"operation-log commit failed: {error}")

    def _lock(self, operation_id: str) -> asyncio.Lock:
        return self._execution_locks.setdefault(operation_id, asyncio.Lock())

    def _signal(self, operation_id: str) -> asyncio.Event:
        return self._control_signals.setdefault(operation_id, asyncio.Event())
