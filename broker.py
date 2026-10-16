# broker.py — canonical operations, compilation, export, update, removal, scheduling, and leases (Q5/Q6/Q26/Q52/Q54/Q57/Q65/Q77); depends on compiler.py, errors.py, pager.py, schema, sources.py, store.py, trainer.py.
"""Own the operation log and the single broker admission and dispatch authority."""

from __future__ import annotations

import asyncio
import base64
from collections import deque
from collections.abc import Callable, Mapping
from contextlib import suppress
import ctypes
from dataclasses import asdict, dataclass, replace
import fcntl
import inspect
import math
import json
import os
from pathlib import Path
import re
import _ssl
import sys
import time
import threading
from types import MappingProxyType
import uuid

from compiler import (
    PreparedRevision,
    inspect_source_identity,
    prepare_native_training_child,
    prepare_native_compiled,
    prepare_native_effective_source,
    decode_native_tokens,
    render_native_input,
    verify_native_bundle,
    plan_export,
    plan_revision,
    prepare_revision,
    verify_bundle_structure,
)
from errors import CassetteError
from pager import CertifiedSchedule, NativeTransformer, admit_schedule, capture_native, merge_adapter_material
from schema.tables import Q77_FIELDS
from schema.validator import validate
from sources import Artifact, PartialState, ResolvedSource, SourceAdapter, TransferExtent, header_ranges, source_header_lengths, source_profile_boundary, transfer_artifact, transfer_chunk_count, transfer_header, transfer_state_bytes
from store import (
    ArtifactIdentity,
    CapacityClaim,
    CapacityCoordinator,
    CapacityTransition,
    CartridgeLifecycle,
    DriveSelection,
    DriveVolume,
    WriterContext,
    GenerationPin,
    STORAGE_PROFILER_VERSION,
    apply_revision_delta as apply_store_delta,
    canonical_bytes,
    campaign_head,
    await_extent_io,
    grant_profile_extents,
    seal_profile_extents,
    reclaim_profile_extents,
    drive_path_observation,
    storage_host_observation,
    storage_profile,
    source_profile_trace,
    compare_campaign_head,
    verify_campaign_artifact,
    write_campaign_artifact,
    commit_generation,
    commit_runtime_state,
    complete_capacity_claim,
    digest_bytes,
    create_selected_root,
    inventory_step,
    compare_inventory,
    list_external_apfs_volumes,
    revalidate_external_apfs_volume,
    select_external_apfs_volume,
    execute_claimed_write,
    export_revision as export_store_revision,
    grant_transfer_extent,
    load_root,
    model_identity,
    page_locations,
    recover_generation,
    remove_revision as remove_store_revision,
    pause_capacity_claim,
    verify_root_content,
)
from trainer import (adapter_merge_material, advance_native_training, native_training_inputs, native_training_state, native_training_context)

PROTOCOL_VERSION = "1"
PREPARE_OPERATION = "prepare"
ACQUIRE_OPERATION = "acquire"
PHASES = (
    "EMPTY",
    "RESOLVED",
    "ACQUIRING",
    "SOURCE_VERIFIED",
    "PLANNED",
    "PREPARING",
    "EXEC_VERIFIED",
    "PUBLISHED",
    "ACTIVE",
)
_MUTABLE_PHASES = frozenset(PHASES[:PHASES.index("PUBLISHED")])
_TERMINAL_STATES = frozenset({"SUCCEEDED", "CANCELLED", "FAILED"})
_TERMINAL_EVENTS = frozenset({"completed", "cancelled", "failed"})
_OPERATION_ID = re.compile(r"op-[0-9a-f]{64}")
_DIGEST = re.compile(r"blake3:[0-9a-f]{64}")
_SOURCE_DIGEST = re.compile(r"(?:blake3|sha256):[0-9a-f]{64}|git-sha1:[0-9a-f]{40}")
_MAX_RECORD_BYTES = 4 * 1024 * 1024
_MAX_TEXT = 512
_MAX_CAPABILITY_ITEMS = 64
_MAX_NEGOTIATIONS = 1024
_MAX_CLIENT_QUEUE = 8
_MAX_QUEUE = 64
_MAX_COST = 16
_AGE_PROMOTION = 4
_SEQUENCE_FIELDS = frozenset({"modalities", "reasoning_fields", "sampling"})
_BOOLEAN_FIELDS = frozenset({"structured_output", "streaming", "cancellation"})
_FOUNDATIONAL_FIELDS = frozenset({
    "cassette_protocol", "adapter_version", "model_revision", "source_parent",
    "execution_mode", "plan_id", "performance_tier", "training_tier", "precision",
    "semantic_state",
})
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
    "ACQUIRING": frozenset({
        "source_lock", "parent_root", "metadata_digest", "requirements_digest",
    }),
    "SOURCE_VERIFIED": frozenset({
        "source_lock", "parent_root", "metadata_digest", "requirements_digest",
        "partials",
    }),
    "PLANNED": frozenset({
        "source_lock", "parent_root", "metadata_digest", "requirements_digest",
        "partials", "plan_digest",
    }),
    "PREPARING": frozenset({
        "source_lock", "parent_root", "metadata_digest", "requirements_digest",
        "partials", "plan_digest",
    }),
    "EXEC_VERIFIED": frozenset({
        "source_lock", "parent_root", "metadata_digest", "requirements_digest",
        "partials", "plan_digest", "source_verification", "candidate_root", "page_digests",
    }),
    "PUBLISHED": frozenset({
        "source_lock", "parent_root", "metadata_digest", "requirements_digest",
        "partials", "plan_digest", "source_verification", "candidate_root", "page_digests",
        "generation",
    }),
    "ACTIVE": frozenset({
        "source_lock", "parent_root", "metadata_digest", "requirements_digest",
        "partials", "plan_digest", "source_verification", "candidate_root", "page_digests",
        "generation",
    }),
}


@dataclass(frozen=True, slots=True)
class AcquisitionContext:
    """Live authorities required to resume one Q5 preparation from its durable checkpoint."""

    adapter: SourceAdapter
    capacity_controller: CapacityCoordinator
    transfers: Mapping[str, tuple[TransferExtent, TransferExtent]] | None
    cartridge: str | Path

    def __post_init__(self) -> None:
        """Require the concrete authority without resolving operation-bound paths yet."""

        if not isinstance(self.capacity_controller, CapacityCoordinator):
            _reject(
                "INVALID_REQUEST",
                "acquisition:context",
                "a concrete CapacityCoordinator is required",
            )


@dataclass(frozen=True, slots=True)
class ScheduledLease:
    """One broker-issued lease; equality with the live table is its authority."""

    lease_id: str
    lease_epoch: int
    operation_id: str
    kind: str
    client_id: str
    context_id: str
    negotiation_id: str
    model_revision: str
    plan_id: str
    cache_key: tuple[str, str, str, str]


@dataclass(slots=True)
class _QueuedRun:
    operation_id: str
    client_id: str
    context_id: str
    request: dict
    lease_kind: str
    cost: int
    negotiation: dict
    profile_id: str
    cache_key: tuple[str, str, str, str]
    pages: tuple[str, ...]
    worker: Callable[[ScheduledLease], object]
    future: asyncio.Future
    enqueued_turn: int


@dataclass(frozen=True, slots=True)
class _CacheAuthority:
    """One pager-admitted byte budget bound to one verified store page catalog."""

    root_digest: str
    cache_budget_bytes: int
    page_lengths: Mapping[str, int]


class _ControlStop(Exception):
    def __init__(self, action: str):
        self.action = action


async def _await_completion(value):
    """Acknowledge cancellation only after an executor-backed awaitable releases its work."""
    pending = asyncio.ensure_future(value)
    cancelled = False
    while True:
        try:
            result = await asyncio.shield(pending)
            break
        except asyncio.CancelledError:
            if pending.cancelled():
                raise
            cancelled = True
    if cancelled:
        raise asyncio.CancelledError
    return result


def _json_copy(value: object, object_id: str, field: str) -> object:
    """Return a detached canonical JSON value after enforcing the broker byte bound."""

    _json_digest(value, object_id, field)
    return json.loads(canonical_bytes(value), object_pairs_hook=_unique_object)


def _text(value: object, object_id: str, field: str) -> str:
    if not isinstance(value, str) or not value or len(value) > _MAX_TEXT:
        _reject("INVALID_REQUEST", object_id, f"{field} must be 1..{_MAX_TEXT} characters")
    return value


def _strings(value: object, object_id: str, field: str) -> list[str]:
    if (
        not isinstance(value, list)
        or len(value) > _MAX_CAPABILITY_ITEMS
        or any(not isinstance(item, str) or not item or len(item) > _MAX_TEXT for item in value)
        or value != sorted(set(value))
    ):
        _reject("INVALID_REQUEST", object_id, f"{field} must be a sorted unique bounded string array")
    return value


def _limits(value: object, object_id: str, field: str) -> dict[str, int]:
    if (
        not isinstance(value, dict)
        or not value
        or len(value) > _MAX_CAPABILITY_ITEMS
        or list(value) != sorted(value)
        or any(not isinstance(name, str) or not name or len(name) > _MAX_TEXT for name in value)
        or any(type(limit) is not int or not 0 <= limit < 2**64 for limit in value.values())
    ):
        _reject("INVALID_REQUEST", object_id, f"{field} must be a sorted bounded unsigned-integer object")
    return value


def _profile(value: object, object_id: str) -> dict:
    """Validate one immutable callable profile and its field-level authority."""

    defects = validate("callable_capability", value)
    if defects:
        _reject("INVALID_REQUEST", object_id, "; ".join(defects), invariant="Q77: generated callable profile")
    for field in _SEQUENCE_FIELDS:
        _strings(value[field], object_id, field)
    _limits(value["input_limits"], object_id, "input_limits")
    provenance = value["field_provenance"]
    if any(provenance[field]["status"] != "EXACT" for field in _FOUNDATIONAL_FIELDS):
        _reject("CAPABILITY_MISMATCH", object_id, "callable identity and execution fields must be EXACT")
    return _json_copy(value, object_id, "capability profile")


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

    result = {
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
    if revision.artifact_selector is not None:
        result['artifact_selector'] = json.loads(revision.artifact_selector)
    return result


def _source_from(record: object, object_id: str) -> ResolvedSource:
    fields = {
        "source_kind", "locator", "immutable_revision", "identity", "artifacts",
        "metadata_assets", "auth_scope", "license_digest", "credential_ref",
        "license_acceptance_ref",
    }
    if not isinstance(record, dict) or set(record) not in (fields, fields | {'artifact_selector'}):
        _reject("ROOT_INVALID", object_id, "source lock has an incorrect field set")
    if 'artifact_selector' in record and not isinstance(record['artifact_selector'], dict):
        _reject('ROOT_INVALID', object_id, 'source lock artifact selector must be an object')

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
        "source_kind", "locator", "immutable_revision", "auth_scope", "license_digest",
    )
    if any(not isinstance(record[field], str) or not record[field] for field in text_fields):
        _reject("ROOT_INVALID", object_id, "source lock contains empty or non-text identity material")
    for field in ("immutable_revision", "identity", "license_digest"):
        if field == "identity" and record[field] is None:
            continue
        if not isinstance(record[field], str) or _SOURCE_DIGEST.fullmatch(record[field]) is None:
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
        canonical_bytes(record['artifact_selector']) if 'artifact_selector' in record else None,
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
        "chunk_digests": {"count": len(partial.chunk_digests),
                          "digest": digest_bytes(canonical_bytes(list(partial.chunk_digests)))},
        "contiguous_source_hash_offset": partial.contiguous_source_hash_offset,
        "serialized_hash_state": partial.serialized_hash_state,
    }


def _compiler_artifacts(revision: ResolvedSource) -> tuple[Artifact, ...]:
    """Include the source tokenizer's admitted semantic files in the same verified transfer."""
    objects = _acquisition_artifacts(revision)
    if any(item.path == "tokenizer.json" for item in objects):
        return tuple(sorted((*revision.artifacts, *(item for item in revision.metadata_assets
                                                    if item.path.endswith(".json"))), key=lambda item: item.path))
    return revision.artifacts


def _acquisition_artifacts(revision: ResolvedSource) -> tuple[Artifact, ...]:
    """Return every immutable model and metadata object in one canonical transfer order."""

    objects = (*revision.artifacts, *revision.metadata_assets)
    if len({item.path for item in objects}) != len(objects):
        _reject("SOURCE_REVISION_CHANGED", revision.locator, "model and metadata paths overlap")
    return tuple(sorted(objects, key=lambda item: item.path))


def _transfer_extent_id(operation_id: str, path: str, role: str) -> str:
    """Derive one restart-stable store extent name for a verified source object."""

    return "acquire-" + digest_bytes(canonical_bytes({
        "operation_id": operation_id,
        "path": path,
        "role": role,
    })).removeprefix("blake3:")


def _verify_partials(
    records: object,
    revision: ResolvedSource,
    object_id: str,
    artifacts: tuple[Artifact, ...] | None = None,
) -> None:
    """Validate broker certificates; sources retains every full Q51 checkpoint and chunk digest."""
    artifacts = _compiler_artifacts(revision) if artifacts is None else artifacts
    if not isinstance(records, list) or len(records) != len(artifacts):
        _reject("ROOT_INVALID", object_id, "source verification must contain one record per artifact")
    by_path = {artifact.path: artifact for artifact in artifacts}
    for record in records:
        if not isinstance(record, dict) or set(record) != {
            "path", "source_revision", "object_size", "validator", "completed_interval_set",
            "chunk_digests", "contiguous_source_hash_offset", "serialized_hash_state",
        }:
            _reject("ROOT_INVALID", object_id, "source verification record has an incorrect field set")
        artifact = by_path.get(record["path"])
        intervals = record["completed_interval_set"]
        chunks = record["chunk_digests"]
        chunks_valid = (
            isinstance(chunks, list) and bool(chunks) == bool(artifact and artifact.size)
            and all(isinstance(item, str) and _DIGEST.fullmatch(item) is not None for item in chunks)
        ) or (
            isinstance(chunks, dict) and set(chunks) == {"count", "digest"}
            and type(chunks["count"]) is int and artifact is not None
            and chunks["count"] == transfer_chunk_count(artifact.size)
            and isinstance(chunks["digest"], str) and _DIGEST.fullmatch(chunks["digest"]) is not None
        )
        if (
            artifact is None
            or record["source_revision"] != revision.immutable_revision
            or record["object_size"] != artifact.size
            or record["validator"] != artifact.validator
            or intervals != ([[0, artifact.size]] if artifact.size else [])
            or type(record["contiguous_source_hash_offset"]) is not int
            or record["contiguous_source_hash_offset"] != artifact.size
            or not chunks_valid
            or not isinstance(record["serialized_hash_state"], str)
        ):
            _reject("ROOT_INVALID", object_id, f"source verification for {record.get('path')!r} is incomplete")
    if [record["path"] for record in records] != sorted(by_path):
        _reject("ROOT_INVALID", object_id, "source verification records are not canonically ordered")


def _compiler_source(revision: ResolvedSource, descriptor: Mapping[str, object]) -> dict:
    """Strip network locations and credential references before compiler dispatch."""

    requested_revision = descriptor.get("revision")
    if not isinstance(requested_revision, str) or not requested_revision:
        _reject("INVALID_REQUEST", revision.identity, "source descriptor revision must be nonempty text")
    return {
        "source_kind": revision.source_kind,
        "source_alias": f"{revision.locator}@{requested_revision}",
        "locator": revision.locator,
        "requested_revision": requested_revision,
        "immutable_revision": revision.immutable_revision,
        "identity": revision.identity,
        "artifacts": [
            {"path": item.path, "size": item.size, "digest": item.digest}
            for item in _compiler_artifacts(revision)
        ],
        "license_digest": revision.license_digest,
    }


def _compiler_extents(
    revision: ResolvedSource,
    transfers: Mapping[str, tuple[TransferExtent, TransferExtent]],
    operation_id: str,
) -> dict:
    """Expose only pre-opened data extents; transfer checkpoints remain source-owned evidence."""

    if not isinstance(transfers, Mapping) or set(transfers) != {
        artifact.path for artifact in _compiler_artifacts(revision)
    }:
        _reject("INVALID_REQUEST", operation_id, "transfers must name every source artifact exactly once")
    result = {}
    for artifact in _compiler_artifacts(revision):
        pair = transfers[artifact.path]
        if not isinstance(pair, tuple) or len(pair) != 2 or not isinstance(pair[0], TransferExtent):
            _reject("INVALID_REQUEST", operation_id, f"{artifact.path} requires one compiler data extent")
        extent = pair[0]
        result[artifact.path] = {
            "fd": extent.fd,
            "offset": extent.offset,
            "length": extent.length,
            "operation_id": extent.operation_id,
        }
    return result


class CanonicalBroker:
    """Persist Q6 operations and execute each Q5 transition from its last durable phase."""

    def __init__(self, operation_log: str | Path):
        self.operation_log = Path(operation_log)
        self._owner_fd: int | None = None
        self._capacity_coordinator = CapacityCoordinator(self.operation_log)
        try:
            missing = []
            directory = self.operation_log
            while not directory.exists():
                if directory == directory.parent:
                    _reject(
                        "DURABILITY_UNSUPPORTED",
                        "broker:operation-log",
                        "operation log has no existing filesystem parent",
                    )
                missing.append(directory)
                directory = directory.parent
            for directory in reversed(missing):
                transition = CapacityTransition(
                    "broker-operation-log",
                    f"operation-log-directory:{directory.name}",
                    pointer_bytes=0,
                    declared_writes=1,
                    write_bytes=(0,),
                )
                claim = self._claim_log_transition(transition)
                try:
                    execute_claimed_write(
                        claim, lambda directory=directory: directory.mkdir(exist_ok=True)
                    )
                    descriptor = os.open(directory.parent, os.O_RDONLY)
                    try:
                        os.fsync(descriptor)
                    finally:
                        os.close(descriptor)
                    complete_capacity_claim(claim)
                except Exception:
                    if claim.active:
                        pause_capacity_claim(claim, "operation-log directory did not reach its durable boundary")
                    raise
        except OSError as error:
            _reject("DURABILITY_UNSUPPORTED", "broker:operation-log", f"operation-log creation failed: {error}")
        self.operation_log = self.operation_log.resolve()
        descriptor = -1
        try:
            descriptor = os.open(self.operation_log, os.O_RDONLY)
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            with suppress(OSError):
                os.close(descriptor)
            _reject(
                "OVERLOADED",
                f"broker:{self.operation_log}",
                "operation log already has one live broker owner",
                retryability="retryable",
            )
        except OSError as error:
            if descriptor >= 0:
                with suppress(OSError):
                    os.close(descriptor)
            _reject(
                "DURABILITY_UNSUPPORTED",
                f"broker:{self.operation_log}",
                f"operation-log ownership failed: {error}",
            )
        self._owner_fd = descriptor
        self._execution_locks: dict[str, asyncio.Lock] = {}
        self._control_signals: dict[str, asyncio.Event] = {}
        self._event_signals: dict[str, asyncio.Event] = {}
        self._active: dict[str, bool] = {}
        # Observations of source-owned durable prefixes, never input to resume or verification.
        self._transfer_progress: dict[str, dict] = {}
        self._profiles: dict[str, dict] = {}
        self._profile_activators: dict[str, Callable[[ScheduledLease, dict], object]] = {}
        self._revision_profiles: dict[str, list[str]] = {}
        self._aliases: dict[str, str] = {}
        self._negotiation_sequence = 0
        self._negotiations: dict[str, dict] = {}
        self._queues: dict[str, deque[_QueuedRun]] = {}
        self._scheduler_lock = asyncio.Lock()
        self._model_execution_lock = asyncio.Lock()
        self._client_order: list[str] = []
        self._deficits: dict[str, int] = {}
        self._queue_cursor = 0
        self._scheduler_turn = 0
        self._scheduler_task: asyncio.Task | None = None
        self._scheduled: dict[str, asyncio.Future] = {}
        self._leases: dict[str, ScheduledLease] = {}
        self._lease_epoch = 0
        self._active_cache_key: tuple[str, str, str, str] | None = None
        self._cache_authorities: dict[tuple[str, str, str, str], _CacheAuthority] = {}
        self._cache: dict[tuple[tuple[str, str, str, str], str], int] = {}
        self._cache_pins: dict[tuple[tuple[str, str, str, str], str], set[str]] = {}
        self._cache_bytes = 0
        self._cache_budget_bytes = 0
        self._cache_clock = 0
        self._page_churn = 0
        self._switches = 0
        self._age_promotions = 0

    def close(self) -> None:
        """Release this process's sole authority over the canonical operation log."""

        descriptor = self._owner_fd
        if descriptor is None:
            return
        if self._active or self._scheduler_task is not None or self._leases or any(self._queues.values()):
            _reject(
                "OVERLOADED",
                f"broker:{self.operation_log}",
                "broker cannot close while an operation, scheduled work, or a lease remains live",
                invariant="Q65: leases end before broker ownership",
                retryability="retryable",
            )
        self._owner_fd = None
        try:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
            os.close(descriptor)
        except OSError as error:
            with suppress(OSError):
                os.close(descriptor)
            _reject(
                "DURABILITY_UNSUPPORTED",
                f"broker:{self.operation_log}",
                f"operation-log ownership release failed: {error}",
            )

    def __del__(self):
        descriptor = getattr(self, "_owner_fd", None)
        if descriptor is not None:
            self._owner_fd = None
            with suppress(OSError):
                os.close(descriptor)

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

    def register_capability(
        self,
        model_ref: str,
        profile: dict,
        activate: Callable[[ScheduledLease, dict], object],
        *,
        schedule: CertifiedSchedule,
        cartridge: str | Path,
        root_digest: str,
    ) -> str:
        """Bind one callable profile to pager admission and a verified store page catalog."""

        model_ref = _text(model_ref, "capability:registration", "model_ref")
        if not callable(activate):
            _reject("INVALID_REQUEST", model_ref, "activate must be callable", invariant="Q65: SWITCH lease")
        profile = _profile(profile, model_ref)
        if (
            not isinstance(schedule, CertifiedSchedule)
            or schedule.plan_id != profile["plan_id"]
            or type(schedule.cache_budget_bytes) is not int
            or not 0 <= schedule.cache_budget_bytes < 2**64
        ):
            _reject(
                "CAPABILITY_MISMATCH",
                model_ref,
                "callable profile must carry its exact pager-admitted Q47 cache budget",
                invariant="Q47/Q65: one cache-byte authority",
            )
        root_digest = _exact_digest(root_digest, model_ref, "cache root_digest")
        locations = page_locations(cartridge, root_digest)
        page_lengths = MappingProxyType({location.page_digest: location.length for location in locations})
        cache_key = (
            profile["model_revision"], profile["plan_id"], profile["precision"],
            profile["semantic_state"],
        )
        authority = _CacheAuthority(root_digest, schedule.cache_budget_bytes, page_lengths)
        existing_authority = self._cache_authorities.get(cache_key)
        if existing_authority is not None and (
            existing_authority.root_digest != authority.root_digest
            or existing_authority.cache_budget_bytes != authority.cache_budget_bytes
            or existing_authority.page_lengths != authority.page_lengths
        ):
            _reject(
                "IDEMPOTENCY_CONFLICT",
                model_ref,
                "one cache identity cannot change its root, page lengths, or Q47 byte budget",
                invariant="Q47/Q65: immutable cache authority",
            )
        exact_revision_ref = _DIGEST.fullmatch(model_ref) is not None
        if exact_revision_ref and model_ref != profile["model_revision"]:
            _reject(
                "IDENTITY_MISMATCH",
                model_ref,
                "an immutable revision reference cannot alias another revision",
                invariant="Q77: exact model revision discovery",
            )
        profile_id = digest_bytes(canonical_bytes(profile))
        existing = self._profiles.get(profile_id)
        if existing is None:
            self._profiles[profile_id] = profile
            self._profile_activators[profile_id] = activate
            self._revision_profiles.setdefault(profile["model_revision"], []).append(profile_id)
            self._revision_profiles[profile["model_revision"]].sort()
        elif existing != profile or self._profile_activators[profile_id] is not activate:
            _reject(
                "IDEMPOTENCY_CONFLICT",
                profile_id,
                "an immutable capability profile cannot change its activation authority",
                invariant="Q77: immutable callable profile",
            )
        self._cache_authorities.setdefault(cache_key, authority)
        current = self._aliases.get(model_ref)
        if not exact_revision_ref and current != profile_id:
            self._aliases[model_ref] = profile_id
            self._negotiations = {
                identity: entry for identity, entry in self._negotiations.items()
                if entry["model_ref"] != model_ref or entry["operation_id"] is not None
            }
        return profile_id

    def capabilities(self) -> tuple[dict, ...]:
        """Expose bounded machine-readable profiles with their current model references."""

        aliases = {}
        for model_ref, profile_id in self._aliases.items():
            aliases.setdefault(profile_id, []).append(model_ref)
        records = []
        for profile_id in sorted(self._profiles):
            profile = self._profiles[profile_id]
            records.append({
                "profile_id": profile_id,
                "model_refs": sorted({profile["model_revision"], *aliases.get(profile_id, [])}),
                "capability": _json_copy(profile, profile_id, "capability profile"),
            })
        return tuple(records)

    def negotiate(self, requested: dict) -> dict:
        """Return one immutable exact subset, or reject before queue or lease admission."""

        object_id = "negotiation:unidentified"
        if not isinstance(requested, dict) or "model_ref" not in requested:
            _reject("INVALID_REQUEST", object_id, "negotiation requires model_ref")
        model_ref = _text(requested["model_ref"], object_id, "model_ref")
        object_id = f"negotiation:{model_ref}"
        allowed = frozenset({"model_ref", *Q77_FIELDS})
        if not set(requested) <= allowed:
            _reject("INVALID_REQUEST", object_id, "negotiation contains an unknown field")
        _json_digest(requested, object_id, "requested capability")
        self._validate_requested(requested, object_id)
        profile_ids = self._resolve_profiles(model_ref, object_id)
        matches = [
            profile_id for profile_id in profile_ids
            if self._supports(self._profiles[profile_id], requested)
        ]
        if len(matches) != 1:
            detail = "requested capability is unsupported" if not matches else "requested capability is ambiguous"
            _reject("CAPABILITY_MISMATCH", object_id, detail, invariant="Q77: exact pre-admission negotiation")
        if len(self._negotiations) >= _MAX_NEGOTIATIONS:
            _reject(
                "OVERLOADED",
                object_id,
                "pending negotiation table is full",
                invariant="Q77: bounded pre-admission state",
                retryability="retryable",
            )
        profile_id = matches[0]
        profile = self._profiles[profile_id]
        capability = self._selected_capability(profile, requested)
        self._negotiation_sequence += 1
        material = {
            "profile_id": profile_id,
            "model_ref": model_ref,
            "sequence": self._negotiation_sequence,
            "requested_digest": digest_bytes(canonical_bytes(requested)),
            "capability": capability,
        }
        negotiation_id = digest_bytes(canonical_bytes(material))
        record = {**capability, "negotiation_id": negotiation_id}
        defects = validate("negotiated_capability", record)
        if defects:
            _reject(
                "CAPABILITY_MISMATCH",
                object_id,
                "; ".join(defects),
                invariant="Q77: generated negotiated capability",
            )
        self._negotiations.setdefault(negotiation_id, {
            **material,
            "record": record,
            "cache_key": (
                profile["model_revision"], profile["plan_id"], profile["precision"],
                profile["semantic_state"],
            ),
            "operation_id": None,
        })
        return _json_copy(record, negotiation_id, "negotiated capability")

    async def dispatch(
        self,
        client_id: str,
        context_id: str,
        request: dict,
        negotiation: dict,
        lease_kind: str,
        worker: Callable[[ScheduledLease], object],
        *,
        cost: int = 1,
        pages: tuple[str, ...] = (),
    ) -> dict:
        """Admit one negotiated operation to the sole bounded Q65 scheduler."""

        client_id = _text(client_id, "scheduler:client", "client_id")
        context_id = _text(context_id, f"scheduler:{client_id}", "context_id")
        if lease_kind not in {"EXEC", "WRITE"}:
            _reject("INVALID_REQUEST", client_id, "lease_kind must be EXEC or WRITE")
        if type(cost) is not int or not 1 <= cost <= _MAX_COST:
            _reject("INVALID_REQUEST", client_id, f"cost must be an integer in 1..{_MAX_COST}")
        if not callable(worker):
            _reject("INVALID_REQUEST", client_id, "worker must be callable")
        pages = self._page_ids(pages, client_id)
        operation_id = self.operation_id(request)
        path_exists = self._path(operation_id).exists()
        if path_exists:
            operation = self.issue(request)
            if operation["state"] in _TERMINAL_STATES or operation["state"] == "PAUSED":
                return operation
        entry = self._negotiation(negotiation, operation_id)
        capability = entry["record"]
        arguments = request.get("arguments")
        if (
            request.get("target") != capability["model_revision"]
            or not isinstance(arguments, dict)
            or arguments.get("negotiation_id") != capability["negotiation_id"]
            or arguments.get("context_ref") != context_id
        ):
            _reject(
                "CAPABILITY_MISMATCH",
                operation_id,
                "request target, negotiation, or context differs from pre-admission",
                invariant="Q77: stable run identity",
            )
        self._page_bytes(entry["cache_key"], pages, operation_id)
        duplicate = None
        async with self._scheduler_lock:
            entry = self._negotiation(negotiation, operation_id)
            duplicate = self._scheduled.get(operation_id)
            if duplicate is not None:
                self.issue(request)
            else:
                bound = entry["operation_id"]
                if bound is not None and bound != operation_id:
                    _reject(
                        "CAPABILITY_MISMATCH",
                        operation_id,
                        "one negotiation cannot admit two operations",
                        invariant="Q77: one immutable negotiation per run",
                    )
                queue = self._queues.get(client_id)
                if (
                    self._queued_count() >= _MAX_QUEUE
                    or (queue is not None and len(queue) >= _MAX_CLIENT_QUEUE)
                ):
                    _reject(
                        "OVERLOADED",
                        operation_id,
                        "scheduler queue bound was reached before operation admission",
                        invariant="Q65: bounded client queues",
                        retryability="retryable",
                    )
                if not path_exists:
                    self.issue(request)
                entry["operation_id"] = operation_id
                loop = asyncio.get_running_loop()
                duplicate = loop.create_future()
                work = _QueuedRun(
                    operation_id, client_id, context_id,
                    _json_copy(request, operation_id, "scheduled request"), lease_kind, cost,
                    _json_copy(capability, operation_id, "negotiated capability"),
                    entry["profile_id"], entry["cache_key"], pages, worker, duplicate,
                    self._scheduler_turn,
                )
                if client_id not in self._queues:
                    self._queues[client_id] = deque()
                    self._client_order.append(client_id)
                    self._deficits[client_id] = 0
                self._queues[client_id].append(work)
                self._scheduled[operation_id] = duplicate
                self._prefetch(entry["cache_key"], pages)
                if self._scheduler_task is None:
                    self._scheduler_task = asyncio.create_task(self._drain())
        return await asyncio.shield(duplicate)

    def scheduler_status(self) -> dict:
        """Return the bounded live scheduler, lease, activation, and cache state."""

        return {
            "draining": self._scheduler_task is not None,
            "queues": {client: len(queue) for client, queue in sorted(self._queues.items()) if queue},
            "leases": [self._lease_record(lease) for lease in self._leases.values()],
            "active_cache_key": None if self._active_cache_key is None else list(self._active_cache_key),
            "cache_bytes": self._cache_bytes,
            "cache_budget_bytes": self._cache_budget_bytes,
            "cache": [
                {
                    "cache_key": list(cache_key),
                    "page": page,
                    "length": self._cache_authorities[cache_key].page_lengths[page],
                    "pinned": bool(self._cache_pins.get((cache_key, page))),
                }
                for cache_key, page in sorted(self._cache)
            ],
            "page_churn": self._page_churn,
            "switches": self._switches,
            "age_promotions": self._age_promotions,
        }

    def cache_contains(self, lease: ScheduledLease, page_digest: str) -> bool:
        """Resolve a page only through the exact live revision-plan-precision-semantic key."""

        lease = self._live_lease(lease)
        _exact_digest(page_digest, lease.operation_id, "page digest")
        key = (lease.cache_key, page_digest)
        return key in self._cache and lease.lease_id in self._cache_pins.get(key, set())

    @staticmethod
    def _validate_requested(requested: dict, object_id: str) -> None:
        defects = validate("capability_request", requested)
        if defects:
            _reject("INVALID_REQUEST", object_id, "; ".join(defects), invariant="Q77: generated capability request")
        for field in sorted(_SEQUENCE_FIELDS & requested.keys()):
            _strings(requested[field], object_id, field)
        if "input_limits" in requested:
            _limits(requested["input_limits"], object_id, "input_limits")

    def _resolve_profiles(self, model_ref: str, object_id: str) -> list[str]:
        alias = self._aliases.get(model_ref)
        if alias is not None:
            return [alias]
        profiles = self._revision_profiles.get(model_ref)
        if profiles:
            return list(profiles)
        _reject("CAPABILITY_MISMATCH", object_id, "model_ref does not resolve to a callable profile")

    @staticmethod
    def _supports(profile: dict, requested: dict) -> bool:
        for field, desired in requested.items():
            if field == "model_ref":
                continue
            if profile["field_provenance"][field]["status"] != "EXACT":
                return False
            available = profile[field]
            if field in _SEQUENCE_FIELDS:
                if not set(desired) <= set(available):
                    return False
            elif field in _BOOLEAN_FIELDS:
                if desired and not available:
                    return False
            elif field == "tool_schema":
                if desired is not None and desired != available:
                    return False
            elif field == "input_limits":
                if any(name not in available or limit > available[name] for name, limit in desired.items()):
                    return False
            elif field == "context_limit":
                if desired > available:
                    return False
            elif desired != available:
                return False
        return True

    @staticmethod
    def _selected_capability(profile: dict, requested: dict) -> dict:
        selected = {field: profile[field] for field in Q77_FIELDS}
        for field in (*_SEQUENCE_FIELDS, *_BOOLEAN_FIELDS, "tool_schema", "input_limits", "context_limit"):
            if field in requested:
                selected[field] = requested[field]
        selected["field_provenance"] = {
            field: profile["field_provenance"][field] for field in Q77_FIELDS
        }
        return _json_copy(selected, profile["model_revision"], "selected capability")

    def _negotiation(self, value: object, operation_id: str) -> dict:
        defects = validate("negotiated_capability", value)
        if defects:
            _reject("CAPABILITY_MISMATCH", operation_id, "; ".join(defects), invariant="Q77: generated negotiation")
        negotiation_id = value.get("negotiation_id")
        if not isinstance(negotiation_id, str) or _DIGEST.fullmatch(negotiation_id) is None:
            _reject("CAPABILITY_MISMATCH", operation_id, "negotiation identity is malformed")
        entry = self._negotiations.get(negotiation_id)
        if entry is None or entry["record"] != value:
            _reject(
                "CAPABILITY_MISMATCH",
                operation_id,
                "negotiation was not issued by this broker or its bytes changed",
                invariant="Q77: broker-issued immutable negotiation",
            )
        return entry

    def _page_ids(self, pages: object, object_id: str) -> tuple[str, ...]:
        if (
            not isinstance(pages, tuple)
            or list(pages) != sorted(set(pages))
            or any(not isinstance(page, str) or _DIGEST.fullmatch(page) is None for page in pages)
        ):
            _reject(
                "MEMORY_BUDGET_EXCEEDED",
                object_id,
                "scheduled pages must be a sorted unique tuple of canonical page identities",
                invariant="Q65: bounded page churn",
            )
        return pages

    def _page_bytes(
        self,
        cache_key: tuple[str, str, str, str],
        pages: tuple[str, ...],
        object_id: str,
    ) -> int:
        authority = self._cache_authorities.get(cache_key)
        if authority is None:
            _reject("ROOT_INVALID", object_id, "cache identity has no verified page authority")
        missing = [page for page in pages if page not in authority.page_lengths]
        if missing:
            _reject(
                "PAGE_CORRUPT",
                missing[0],
                "scheduled page is absent from the verified root index",
                invariant="Q62/Q65: verified page identity before cache admission",
            )
        required = sum(authority.page_lengths[page] for page in pages)
        if required > authority.cache_budget_bytes:
            _reject(
                "MEMORY_BUDGET_EXCEEDED",
                object_id,
                f"required cache pages need {required} bytes; Q47 admitted {authority.cache_budget_bytes}",
                invariant="Q47/Q65: cache admission is denominated in bytes",
            )
        return required

    def _queued_count(self) -> int:
        return sum(len(queue) for queue in self._queues.values())

    async def _drain(self) -> None:
        while True:
            async with self._scheduler_lock:
                if self._queued_count() == 0:
                    self._reset_scheduler()
                    return
                work = self._select()
            try:
                async with self._model_execution_lock:
                    result = await self._run_scheduled(work)
            except asyncio.CancelledError:
                if not work.future.done():
                    work.future.cancel()
                raise
            except CassetteError as error:
                record = self._load(work.operation_id)
                result = self._operation(record) if record["state"] in _TERMINAL_STATES else self._operation(
                    self._failed(record, error)
                )
            except Exception as error:
                failure = CassetteError(
                    "CAPABILITY_MISMATCH",
                    work.operation_id,
                    "Q65/Q77: scheduled work remains one typed operation",
                    "terminal",
                    f"scheduler raised {type(error).__name__}",
                )
                result = self._operation(self._failed(self._load(work.operation_id), failure))
            async with self._scheduler_lock:
                self._scheduled.pop(work.operation_id, None)
                if result["state"] in _TERMINAL_STATES:
                    self._negotiations.pop(work.negotiation["negotiation_id"], None)
                if not work.future.done():
                    work.future.set_result(result)
                if self._queued_count() == 0:
                    self._reset_scheduler()
                    return

    def _reset_scheduler(self) -> None:
        self._queues.clear()
        self._client_order.clear()
        self._deficits.clear()
        self._queue_cursor = 0
        self._scheduler_task = None

    def _select(self) -> _QueuedRun:
        while True:
            client_count = len(self._client_order)
            for _ in range(client_count):
                client = self._client_order[self._queue_cursor % client_count]
                self._queue_cursor = (self._queue_cursor + 1) % client_count
                queue = self._queues[client]
                if not queue:
                    continue
                self._deficits[client] += 1
                work = queue[0]
                promoted = self._scheduler_turn - work.enqueued_turn >= _AGE_PROMOTION
                if work.cost <= self._deficits[client] or promoted:
                    queue.popleft()
                    if promoted and work.cost > self._deficits[client]:
                        self._age_promotions += 1
                        self._deficits[client] = 0
                    else:
                        self._deficits[client] -= work.cost
                    self._scheduler_turn += 1
                    return work
            self._scheduler_turn += 1

    async def _run_scheduled(self, work: _QueuedRun) -> dict:
        operation = self.status(work.operation_id)
        if operation["state"] in _TERMINAL_STATES or operation["state"] == "PAUSED":
            return operation
        stopped = await self._activate(work)
        if stopped is not None:
            return stopped
        operation = self.status(work.operation_id)
        if operation["state"] in _TERMINAL_STATES or operation["state"] == "PAUSED":
            return operation
        self._prefetch(work.cache_key, work.pages)
        if any((work.cache_key, page) not in self._cache for page in work.pages):
            _reject(
                "MEMORY_BUDGET_EXCEEDED",
                work.operation_id,
                "required pages do not fit after the prior lease quiesced",
                invariant="Q65: pinned pages are not evicted",
            )
        lease = self._grant(work, work.lease_kind)
        self._pin(lease, work.pages)

        async def execute_worker():
            value = work.worker(lease)
            value = await value if inspect.isawaitable(value) else value
            if not isinstance(value, dict):
                _reject("INVALID_REQUEST", work.operation_id, "scheduled worker must return one result object")
            if work.lease_kind == "WRITE":
                boundary = value.get("committed_boundary")
                if not isinstance(boundary, str) or _DIGEST.fullmatch(boundary) is None:
                    _reject(
                        "CAPABILITY_MISMATCH",
                        work.operation_id,
                        "WRITE work must end at one immutable committed_boundary",
                        invariant="Q65: training yields only at a committed step boundary",
                    )
            return {
                "client_id": work.client_id,
                "context_id": work.context_id,
                "negotiated_capability": work.negotiation,
                "value": value,
            }

        try:
            return await self.execute(work.request, execute_worker)
        finally:
            self._unpin(lease, work.pages)
            self._release(lease)

    async def _activate(self, work: _QueuedRun) -> dict | None:
        if self._active_cache_key == work.cache_key:
            return None
        lease = self._grant(work, "SWITCH")
        try:
            activator = self._profile_activators[work.profile_id]
            try:
                await self._controlled(
                    work.operation_id,
                    lambda: activator(lease, work.negotiation),
                    cancellable=True,
                )
            except _ControlStop as stopped:
                return self._operation(self._stop(self._load(work.operation_id), stopped.action))
            self._active_cache_key = work.cache_key
            self._switches += 1
            return None
        finally:
            self._release(lease)

    def _grant(self, work: _QueuedRun, kind: str) -> ScheduledLease:
        lease_id = digest_bytes(canonical_bytes({
            "operation_id": work.operation_id,
            "kind": kind,
            "negotiation_id": work.negotiation["negotiation_id"],
            "lease_epoch": self._lease_epoch + 1,
        }))
        self._lease_epoch += 1
        lease = ScheduledLease(
            lease_id, self._lease_epoch, work.operation_id, kind, work.client_id, work.context_id,
            work.negotiation["negotiation_id"], work.negotiation["model_revision"],
            work.negotiation["plan_id"], work.cache_key,
        )
        self._leases[lease_id] = lease
        return lease

    def _release(self, lease: ScheduledLease) -> None:
        lease = self._live_lease(lease)
        if any(lease.lease_id in pins for pins in self._cache_pins.values()):
            _reject(
                "ROOT_INVALID",
                lease.operation_id,
                "lease cannot release while one cache page remains pinned",
                invariant="Q65: pinned cache lifetime equals lease lifetime",
            )
        del self._leases[lease.lease_id]

    def _live_lease(self, lease: object) -> ScheduledLease:
        if not isinstance(lease, ScheduledLease) or self._leases.get(lease.lease_id) != lease:
            _reject(
                "INVALID_REQUEST",
                getattr(lease, "operation_id", "lease:unidentified"),
                "lease is absent, stale, or forged",
                invariant="Q65: one live lease table",
            )
        return lease

    @staticmethod
    def _lease_record(lease: ScheduledLease) -> dict:
        return {
            "lease_id": lease.lease_id,
            "lease_epoch": lease.lease_epoch,
            "operation_id": lease.operation_id,
            "kind": lease.kind,
            "client_id": lease.client_id,
            "context_id": lease.context_id,
            "negotiation_id": lease.negotiation_id,
            "model_revision": lease.model_revision,
            "plan_id": lease.plan_id,
            "cache_key": list(lease.cache_key),
        }

    def _prefetch(self, cache_key: tuple[str, str, str, str], pages: tuple[str, ...]) -> None:
        budget_key = self._active_cache_key or cache_key
        budget = self._cache_authorities[budget_key].cache_budget_bytes
        self._cache_budget_bytes = budget
        admitted = set()
        for page in pages:
            key = (cache_key, page)
            self._cache_clock += 1
            if key in self._cache:
                self._cache[key] = self._cache_clock
                admitted.add(key)
                continue
            length = self._cache_authorities[cache_key].page_lengths[page]
            if not self._make_cache_room(length, budget, admitted):
                continue
            self._cache[key] = self._cache_clock
            self._cache_bytes += length
            admitted.add(key)
        self._make_cache_room(0, budget, admitted)

    def _make_cache_room(
        self,
        needed_bytes: int,
        budget_bytes: int,
        protected: set[tuple[tuple[str, str, str, str], str]],
    ) -> bool:
        while self._cache_bytes + needed_bytes > budget_bytes:
            candidates = [
                (age, candidate) for candidate, age in self._cache.items()
                if not self._cache_pins.get(candidate) and candidate not in protected
            ]
            if not candidates:
                return False
            _, victim = min(candidates)
            victim_key, victim_page = victim
            self._cache_bytes -= self._cache_authorities[victim_key].page_lengths[victim_page]
            self._cache.pop(victim)
            self._cache_pins.pop(victim, None)
            self._page_churn += 1
        return True

    def _pin(self, lease: ScheduledLease, pages: tuple[str, ...]) -> None:
        lease = self._live_lease(lease)
        for page in pages:
            key = (lease.cache_key, page)
            if key not in self._cache:
                _reject("PAGE_CORRUPT", page, "scheduled page lacks cache admission", invariant="Q65: cache pin")
            self._cache_pins.setdefault(key, set()).add(lease.lease_id)

    def _unpin(self, lease: ScheduledLease, pages: tuple[str, ...]) -> None:
        lease = self._live_lease(lease)
        for page in pages:
            key = (lease.cache_key, page)
            pins = self._cache_pins.get(key)
            if pins is None or lease.lease_id not in pins:
                _reject("ROOT_INVALID", page, "lease does not own the declared cache pin")
            pins.remove(lease.lease_id)
            if not pins:
                self._cache_pins.pop(key)

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
        return self._operation(self._terminal(
            record, self._cancel_error(record), "CANCELLED", "cancelled"
        ))

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
        return self._operation(self._paused(record))

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

    def request_hold(self, operation_id: str, boundary: str) -> dict:
        """Q5/Q25: arm one durable hold before the named operation boundary."""
        record = self._load(operation_id)
        holds = [event['payload'] for event in record['events'] if 'hold' in event['payload']]
        if record["state"] in _TERMINAL_STATES or not boundary or (holds and holds[-1]['hold'] != 'RELEASED'):
            _reject("INVALID_REQUEST", operation_id, "hold requires a nonterminal operation with no unreleased hold")
        self._append(record, "output_delta", {"hold": "REQUESTED", "boundary": boundary})
        return self.status(operation_id)

    def release_hold(self, operation_id: str, boundary: str) -> dict:
        """Release only the exact acknowledged boundary; the event survives process restart."""
        record = self._load(operation_id)
        holds = [event["payload"] for event in record["events"] if "hold" in event["payload"]]
        if not holds or holds[-1] != {"hold": "ACKNOWLEDGED", "boundary": boundary}:
            _reject("INVALID_REQUEST", operation_id, "release requires the exact acknowledged hold")
        self._append(record, "output_delta", {"hold": "RELEASED", "boundary": boundary})
        return self.status(operation_id)

    async def hold_boundary(self, operation_id: str, boundary: str) -> None:
        """Remain at a committed boundary until its durable release is observed."""
        while True:
            record = self._load(operation_id)
            holds = [event["payload"] for event in record["events"] if "hold" in event["payload"]]
            if not holds or holds[-1]["hold"] == "RELEASED":
                return
            hold = holds[-1]
            if hold["boundary"] != boundary:
                if hold["hold"] == "ACKNOWLEDGED":
                    _reject("ROOT_INVALID", operation_id, "operation moved beyond its unreleased hold")
                return
            if hold["hold"] == "REQUESTED":
                self._append(record, "output_delta", {"hold": "ACKNOWLEDGED", "boundary": boundary})
            await asyncio.sleep(0.02)

    async def execute(
        self,
        request: dict,
        worker: Callable[[], object],
        *,
        cancellable: bool = True,
    ) -> dict:
        """Run one non-preparation Q6 operation through the canonical operation log.

        Coroutine workers own their cancellation cleanup. Awaitables returned by synchronous
        factories finish before the broker acknowledges cancellation or pause.
        """

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
                result = await self._controlled(
                    operation_id, worker, cancellable=cancellable
                )
                if not isinstance(result, dict):
                    _reject("INVALID_REQUEST", operation_id, "operation worker must return one result object")
                _json_digest(result, operation_id, "operation result")
                await self.hold_boundary(operation_id, "result")
                return self._operation(self._success(self._load(operation_id), result))
            except _ControlStop as stopped:
                return self._operation(self._stop(self._load(operation_id), stopped.action))
            except asyncio.CancelledError:
                raise
            except CassetteError as error:
                return self._operation(self._failed(self._load(operation_id), error))

    async def discover_models(self, request: dict) -> dict:
        """Q9/Q52: own discovery admission and record the source adapter's result."""
        if request.get('operation') != 'source.discover':
            _reject('INVALID_REQUEST', 'source.discover', 'discovery requires its named operation')
        self.operation_id(request)
        if set(request['arguments']) != {'discovery'}:
            _reject('INVALID_REQUEST', 'source.discover', 'discovery requires only its generated argument record')
        args = request['arguments']['discovery']
        credential_ref = None
        if args.get('connection_id'):
            connection = self._entry_result(args['connection_id'], 'source.connect')
            if (args['source'], args['endpoint']) != (connection['source'], connection['endpoint']):
                _reject('INVALID_REQUEST', 'source.discover', 'catalogue endpoint differs from its connection')
            credential_ref = connection['credential_ref']
        adapter = SourceAdapter(args['source'], args['endpoint'],
            credential_lookup=MacOSSourceCredentialProvider().lookup_callback(args['source'], args['endpoint']))
        async def discover():
            return await adapter.discover(args['query'], limit=args['limit'], cursor=args['cursor'],
                                          credential_ref=credential_ref)
        return await self.execute(request, discover)

    def _entry_result(self, operation_id: str, kind: str) -> dict:
        record = self._load(operation_id)
        if record['kind'] != kind or record['state'] != 'SUCCEEDED':
            _reject('INVALID_REQUEST', operation_id, f'{kind} requires a successful recorded operation')
        return _json_copy(record['result'], operation_id, 'entry result')

    async def connect_source(self, request: dict, *, token: str | None = None) -> dict:
        """Q9/Q52: validate source access and record only an opaque credential reference."""
        self.operation_id(request)
        if request['operation'] != 'source.connect' or set(request['arguments']) != {'connection'}:
            _reject('INVALID_REQUEST', 'source.connect', 'connection requires its generated argument record')
        args = request['arguments']['connection']
        if args['mode'] != 'token' and (token is not None or args['credential_ref'] is not None):
            _reject('INVALID_REQUEST', 'source.connect', 'public and existing-login connections accept no supplied credential')
        adapter = SourceAdapter(args['source'], args['endpoint'])
        async def connect():
            if args['mode'] == 'public':
                await adapter.discover('', limit=1)
                credential_ref = None
                authentication = {'authenticated': False, 'scope': 'public'}
            elif args['mode'] == 'existing':
                adapter._require_existing_login()
                vault = MacOSSourceCredentialProvider()
                credential_ref = await asyncio.to_thread(vault.existing_login, args['source'], args['endpoint'])
                authenticated_adapter = SourceAdapter(args['source'], args['endpoint'],
                    credential_lookup=vault.lookup_callback(args['source'], args['endpoint']))
                authentication = await authenticated_adapter._validate_credential(credential_ref)
            else:
                vault = MacOSSourceCredentialProvider()
                credential_ref = args['credential_ref']
                if token is None or credential_ref is not None:
                    _reject('INVALID_REQUEST', 'source.connect', 'token connection requires masked input and no caller-supplied reference')
                authenticated_adapter = SourceAdapter(args['source'], args['endpoint'], credential_lookup=lambda _: token)
                authentication = await authenticated_adapter._validate_credential('session:connect')
                credential_ref = await asyncio.to_thread(vault.save, args['source'], args['endpoint'], token)
            return {'source': args['source'], 'endpoint': args['endpoint'],
                    'credential_ref': credential_ref, 'authentication': authentication}
        return await self.execute(request, connect)

    async def select_source(self, request: dict) -> dict:
        """Q5/Q9: freeze immutable source evidence without acquiring its payload."""
        self.operation_id(request)
        if request['operation'] != 'source.select' or set(request['arguments']) != {'selection'}:
            _reject('INVALID_REQUEST', 'source.select', 'selection requires its generated argument record')
        args = request['arguments']['selection']
        connection = self._entry_result(args['connection_id'], 'source.connect')
        adapter = SourceAdapter(connection['source'], connection['endpoint'],
            credential_lookup=MacOSSourceCredentialProvider().lookup_callback(connection['source'], connection['endpoint']))
        async def select():
            descriptor = {'kind': connection['source'], 'locator': args['locator']}
            for field, value in (('revision', args['revision']),
                                 ('artifact_selector', args.get('artifact_selector')),
                                 ('credential_ref', connection['credential_ref']),
                                 ('license_acceptance_ref', args['license_acceptance_ref'])):
                if value is not None:
                    descriptor[field] = value
            revision = await adapter.resolve(descriptor)
            if await adapter.enumerate(revision) != revision.artifacts:
                _reject('SOURCE_REVISION_CHANGED', revision.locator, 'model artifacts changed during selection')
            requirements = await adapter.license_and_auth(revision)
            descriptor['locator'] = revision.locator
            descriptor['revision'] = revision.immutable_revision
            return {'connection_id': args['connection_id'], 'endpoint': connection['endpoint'],
                    'descriptor': descriptor, 'source_lock': _source_record(revision),
                    'requirements': requirements.record(), 'downloaded_bytes': 0,
                    'execution_compatibility': 'NOT_VERIFIED'}
        return await self.execute(request, select)

    async def discover_drives(self, request: dict) -> dict:
        """Q49: expose native mounted-volume observations through the canonical broker."""
        self.operation_id(request)
        if request['operation'] != 'drive.discover' or request['arguments']:
            _reject('INVALID_REQUEST', 'drive.discover', 'drive discovery takes no arguments')
        async def discover():
            return {'volumes': [asdict(volume) for volume in await asyncio.to_thread(list_external_apfs_volumes)]}
        return await self.execute(request, discover)

    async def _protected_inventory(self, selection: DriveSelection, folder: str) -> dict:
        checkpoint = None
        while True:
            revalidate_external_apfs_volume(selection)
            result = await asyncio.to_thread(inventory_step, selection.volume.mount_path,
                excluded=('.Spotlight-V100', '.Trashes', '.fseventsd', folder), checkpoint=checkpoint)
            if result['inventory'] is not None:
                return result['inventory']
            checkpoint = result['checkpoint']

    async def select_drive(self, request: dict) -> dict:
        """Q44/Q49: retain destination intent and a protected inventory before any drive write."""
        self.operation_id(request)
        if request['operation'] != 'drive.select' or set(request['arguments']) != {'drive'}:
            _reject('INVALID_REQUEST', 'drive.select', 'drive selection requires its generated argument record')
        args = request['arguments']['drive']
        if (len(args['folder']) > 512 or any(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}', part) is None
                                             for part in args['folder'].split('/'))):
            _reject('INVALID_REQUEST', 'drive.select', 'destination must be a relative folder path without traversal')
        async def select():
            selection = await asyncio.to_thread(select_external_apfs_volume, args['volume_uuid'])
            inventory = await self._protected_inventory(selection, args['folder'])
            return {'selection': _json_copy(asdict(selection), args['volume_uuid'], 'drive selection'), 'folder': args['folder'],
                    'cartridge_uuid': args['cartridge_uuid'] or str(uuid.uuid4()),
                    'protected_inventory': inventory,
                    'inventory_digest': digest_bytes(canonical_bytes(inventory)), 'drive_write_proof': 'NOT_RUN'}
        return await self.execute(request, select)

    async def start_download(self, request: dict, *, qualification_only: bool = False,
                             header_only: bool = False, header_json_bytes: list[str] | None = None) -> dict:
        """Q5/Q42/Q44/Q49-Q51: qualify the requested path, then pause, inspect headers or acquire."""
        if any(type(value) is not bool for value in (qualification_only, header_only)):
            _reject('INVALID_REQUEST', 'acquire', 'qualification_only and header_only must be boolean execution limits')
        self.operation_id(request)
        if request['operation'] != 'acquire' or set(request['arguments']) != {'acquisition'}:
            _reject('INVALID_REQUEST', 'acquire', 'Go requires its two recorded selections')
        args = request['arguments']['acquisition']
        source_selection = self._entry_result(args['model_selection_id'], 'source.select')
        destination = self._entry_result(args['drive_selection_id'], 'drive.select')
        header_lengths = None
        if header_only:
            selected = _source_from(source_selection['source_lock'], args['model_selection_id'])
            header_lengths = source_header_lengths(selected, header_json_bytes)
        elif header_json_bytes is not None:
            _reject('INVALID_REQUEST', 'acquire', 'header declarations require header-only execution')
        descriptor = source_selection['descriptor']
        request = {**request, 'arguments': {**request['arguments'], 'source': descriptor}}
        operation = self.issue(request)
        operation_id = operation['operation_id']
        if operation['state'] in _TERMINAL_STATES:
            return operation
        if operation['state'] == 'PAUSED':
            pause_error = self.events(operation_id)[-1]['payload'].get('error', {})
            released = any('drive_remounted' in event['payload'] or 'drive_revalidated' in event['payload']
                           for event in self.events(operation_id))
            holds = [event['payload'] for event in self.events(operation_id) if 'hold' in event['payload']]
            if pause_error.get('retryability') != 'retryable' and not (
                    released and (not holds or holds[-1].get('hold') == 'RELEASED')):
                return operation
            self.resume(operation_id)
        try:
            remounts = [event['payload'][field] for event in self.events(operation_id)
                       for field in ('drive_remounted', 'drive_revalidated') if field in event['payload']]
            selected = remounts[-1]['selection'] if remounts else destination['selection']
            selection = DriveSelection(DriveVolume(**selected['volume']), WriterContext(**selected['writer']))
            selection = await asyncio.to_thread(select_external_apfs_volume, selection.volume.volume_uuid) if remounts else await asyncio.to_thread(revalidate_external_apfs_volume, selection)
            adapter = SourceAdapter(descriptor['kind'], source_selection['endpoint'],
                credential_lookup=MacOSSourceCredentialProvider().lookup_callback(descriptor['kind'], source_selection['endpoint']))
            revision = await adapter.resolve(descriptor)
            if _source_record(revision) != source_selection['source_lock']:
                _reject('SOURCE_REVISION_CHANGED', operation_id, 'Go source evidence differs from the selected immutable input')
            await adapter.license_and_auth(revision)
            observed_inventory = destination['protected_inventory']
            if digest_bytes(canonical_bytes(observed_inventory)) != destination['inventory_digest']:
                _reject('ROOT_INVALID', operation_id, 'selected protected inventory digest does not verify')
            cartridge, cartridge_uuid = await asyncio.to_thread(create_selected_root, selection,
                destination['folder'], operation_id=operation_id, cartridge_uuid=destination['cartridge_uuid'])
            owner = CapacityCoordinator(cartridge)
            key = 'go-durability-' + operation_id.removeprefix('op-')
            binding = {'operation_id': operation_id, 'source_revision': revision.immutable_revision,
                'model_selection_id': args['model_selection_id'], 'drive_selection_id': args['drive_selection_id'],
                'volume_uuid': selection.volume.volume_uuid, 'cartridge_uuid': cartridge_uuid,
                'folder': destination['folder'], 'inventory_digest': destination['inventory_digest']}
            head = await asyncio.to_thread(campaign_head, cartridge, key)
            if head is None:
                probe_id = str(uuid.uuid4())
                await asyncio.to_thread(write_campaign_artifact, owner, probe_id, 'integrity.bin', bytes(4096))
                probe = await asyncio.to_thread(verify_campaign_artifact, cartridge, probe_id,
                                               'integrity.bin', digest_bytes(bytes(4096)), 4096)
                head = await asyncio.to_thread(compare_campaign_head, owner, key, None, {**binding, 'probe': probe})
            if {field: value for field, value in head['value'].items() if field != 'probe'} != binding:
                _reject('ROOT_INVALID', operation_id, 'durability pointer belongs to another Go binding')
            binding = head['value']
            probe = binding['probe']
            await asyncio.to_thread(verify_campaign_artifact, cartridge, probe['attempt'], probe['name'],
                                   probe['digest'], probe['bytes'])
            compare_inventory(observed_inventory, await self._protected_inventory(selection, destination['folder']))
            record = self._load(operation_id)
            if not any('drive_prepared' in event['payload'] for event in record['events']):
                self._append(record, 'output_delta', {'drive_prepared': {
                    'root': str(cartridge), 'cartridge_uuid': cartridge_uuid, 'campaign_key': key,
                    'campaign_digest': head['digest'], 'binding': binding,
                    'selection': _json_copy(asdict(selection), operation_id, 'writer selection'),
                    'protected_inventory': observed_inventory,
                    'source_qualification': 'NOT_RUN', 'model_bytes_downloaded': 0}})
            if not remounts:
                prior = await self._revalidate_durability(cartridge, binding)
                holds = [event['payload'] for event in self.events(operation_id) if 'hold' in event['payload']]
                if prior is None:
                    if not holds:
                        self.request_hold(operation_id, 'CARTRIDGE-DURABILITY')
                    elif holds[-1] not in ({'hold': 'REQUESTED', 'boundary': 'CARTRIDGE-DURABILITY'},
                                           {'hold': 'ACKNOWLEDGED', 'boundary': 'CARTRIDGE-DURABILITY'}):
                        _reject('ROOT_INVALID', operation_id, 'durability preparation conflicts with its saved hold')
                    if not holds or holds[-1]['hold'] == 'REQUESTED':
                        self._append(self._load(operation_id), 'output_delta',
                                     {'hold': 'ACKNOWLEDGED', 'boundary': 'CARTRIDGE-DURABILITY'})
                    return self._operation(self._paused(self._load(operation_id)))
                if holds and holds[-1] == {'hold': 'REQUESTED', 'boundary': 'CARTRIDGE-DURABILITY'}:
                    self._append(self._load(operation_id), 'output_delta',
                                 {'hold': 'ACKNOWLEDGED', 'boundary': 'CARTRIDGE-DURABILITY'})
                    holds[-1] = {'hold': 'ACKNOWLEDGED', 'boundary': 'CARTRIDGE-DURABILITY'}
                if holds and holds[-1] == {'hold': 'ACKNOWLEDGED', 'boundary': 'CARTRIDGE-DURABILITY'}:
                    self.release_hold(operation_id, 'CARTRIDGE-DURABILITY')
                self._append(self._load(operation_id), 'output_delta', {'drive_revalidated': {
                    'proof_operation_id': prior, 'selection': _json_copy(asdict(selection), operation_id, 'writer selection')}})
            qualification = await self._qualify_download(operation_id, owner, selection, revision,
                                                          header_lengths=header_lengths)
            if qualification_only:
                return self.pause(operation_id)
            if header_only:
                try:
                    await self._inspect_headers(operation_id, adapter, owner, revision,
                                                qualification['profile_digest'], header_lengths)
                except CassetteError as error:
                    return self._operation(self._paused(self._load(operation_id), error))
                return self.pause(operation_id)
            return await self.run_acquisition(request, AcquisitionContext(adapter, owner, None, cartridge))
        except CassetteError as error:
            if error.retryability == 'retryable':
                return self._operation(self._paused(self._load(operation_id), error))
            return self._operation(self._failed(self._load(operation_id), error))

    async def _revalidate_durability(self, cartridge, binding):
        """Q44/Q49: reread a completed operation's exact durable proof on the same cartridge."""
        for path in sorted(self.operation_log.glob('op-*.json')):
            record = self._load(path.stem)
            if record['kind'] != 'acquire' or record['state'] != 'SUCCEEDED':
                continue
            if not any('drive_remounted' in event['payload'] for event in record['events']):
                continue
            prepared = next((event['payload']['drive_prepared'] for event in record['events']
                             if 'drive_prepared' in event['payload']), None)
            if prepared is None or any(prepared['binding'][field] != binding[field]
                                       for field in ('volume_uuid', 'cartridge_uuid', 'folder')):
                continue
            head = await asyncio.to_thread(campaign_head, cartridge, prepared['campaign_key'])
            if head is None or head['digest'] != prepared['campaign_digest'] or head['value'] != prepared['binding']:
                _reject('ROOT_INVALID', path.stem, 'prior cartridge durability pointer no longer verifies')
            probe = head['value']['probe']
            await asyncio.to_thread(verify_campaign_artifact, cartridge, probe['attempt'], probe['name'],
                                   probe['digest'], probe['bytes'])
            return path.stem
        return None

    async def _capture_source_profile(self, operation_id, owner, selection, baseline, adapter,
                                      revision, artifact, extents, *, header_bytes=None, saved_header=None,
                                      revalidation=False, capture_key):
        """Q42/Q44/Q51: capture actual source I/O; immutable trace batches bound memory use."""
        trace, captures = bytearray(), []
        host_samples = {'count': 0, 'max_gap_ns': 0, 'states': set(), 'first': None, 'last': None}
        capture_lock = threading.Lock()
        timings = {kind: [] for kind in ('read', 'write', 'fsync', 'F_FULLFSYNC', 'PARSER_READ')}
        totals = dict(read_bytes=0, data_read_bytes=0, write_bytes=0, data_write_bytes=0, errors=0, io_calls=0,
                      process_data_read_bytes=0, data_reads_with_process_io=0, data_reads_without_process_io=0)
        attempt = capture_key
        # The localhost listener changes on restart; its port is transport, not source identity.
        source_lock = _source_record(revision)
        source_lock['artifacts'] = [{key: value for key, value in item.items() if key != 'range_uri'}
                                    for item in source_lock['artifacts']]
        context = {'operation_id': operation_id, 'source_lock': source_lock,
                   'artifact': {key: value for key, value in artifact.record().items() if key != 'range_uri'},
                   'extent_operation': extents['data'].operation_id,
                   'revalidation': revalidation, 'header_json_bytes': header_bytes, 'path': baseline['path']}
        capture_head = await asyncio.to_thread(campaign_head, owner.cartridge, attempt)
        windows, restored_boundary, recovery_history = [], None, []
        fresh_read_window = False
        if capture_head is not None and revalidation:
            saved = capture_head['value']
            if (isinstance(saved, dict) and saved.get('status') in {'MEASURING', 'INCOMPLETE'}
                    and not isinstance(saved.get('checkpoint'), dict)):
                if any(saved.get(key) != value for key, value in context.items()):
                    _reject('ROOT_INVALID', attempt, 'retained read restart differs from its bound source or extent')
                recovery_history = json.loads(canonical_bytes(saved.get('recovery_history', [])))
                if not isinstance(recovery_history, list):
                    _reject('ROOT_INVALID', attempt, 'retained read recovery history must be an ordered list')
                recovery_history.append({'capture_digest': capture_head['digest'], 'error': saved.get('error'),
                                         'status': saved['status']})
                capture_head = await asyncio.to_thread(compare_campaign_head, owner, attempt, capture_head['digest'],
                    {**context, 'status': 'MEASURING', 'superseded_capture': capture_head['digest'],
                     'recovery_history': recovery_history})
                fresh_read_window = True
        if capture_head is None:
            capture_head = await asyncio.to_thread(compare_campaign_head, owner, attempt, None,
                                                   {**context, 'status': 'MEASURING'})
        elif not fresh_read_window:
            saved = capture_head['value']
            if (not isinstance(saved, dict) or any(saved.get(key) != value for key, value in context.items())
                    or saved.get('status') not in {'MEASURING', 'INCOMPLETE', 'CHECKPOINTED', 'CAPTURED'}):
                _reject('ROOT_INVALID', attempt, 'source profile capture differs from its exact source and extent')
            recovery_history = json.loads(canonical_bytes(saved.get('recovery_history', [])))
            if not isinstance(recovery_history, list):
                _reject('ROOT_INVALID', attempt, 'profile recovery history must be an ordered list')
            if saved.get('error') is not None:
                recovery_history.append({'capture_digest': capture_head['digest'], 'error': saved['error']})
            if saved['status'] in {'MEASURING', 'INCOMPLETE'} and not isinstance(saved.get('checkpoint'), dict):
                _reject('SOURCE_UNAVAILABLE', attempt, 'source profile requires a fresh measured extent generation', retryability='retryable')
            checkpoint = json.loads(canonical_bytes(saved.get('checkpoint')))
            if saved['status'] != 'CAPTURED' and not isinstance(checkpoint, dict):
                _reject('ROOT_INVALID', attempt, 'source profile checkpoint must be an observation object')
            captures = saved.get('traces') if saved['status'] == 'CAPTURED' else checkpoint.get('traces')
            captures = json.loads(canonical_bytes(captures))
            if not isinstance(captures, list) or not captures:
                _reject('ROOT_INVALID', attempt, 'source profile capture has no durable trace coverage')
            for trace_ref in captures:
                if not isinstance(trace_ref, dict) or set(trace_ref) != {'attempt', 'name', 'bytes', 'digest'}:
                    _reject('ROOT_INVALID', attempt, 'source profile trace reference is malformed')
                await asyncio.to_thread(verify_campaign_artifact, owner.cartridge, trace_ref['attempt'],
                    trace_ref['name'], trace_ref['digest'], trace_ref['bytes'], maximum_bytes=2097152)
            if saved['status'] == 'CAPTURED':
                if not isinstance(saved.get('measurement'), dict) or saved['measurement'].get('traces') != captures:
                    _reject('ROOT_INVALID', attempt, 'completed capture lost its measured result')
                return {**saved['measurement'], 'capture_record_key': attempt, 'capture_record_digest': capture_head['digest']}
            if (not isinstance(checkpoint, dict) or set(checkpoint) != {'totals', 'timings', 'host_samples', 'windows', 'traces', 'source_boundary'}
                    or not isinstance(checkpoint['totals'], dict) or set(checkpoint['totals']) != set(totals)
                    or any(type(value) is not int or value < 0 for value in checkpoint['totals'].values())
                    or not isinstance(checkpoint['timings'], dict) or set(checkpoint['timings']) != set(timings)
                    or any(not isinstance(values, list) or any(type(value) is not int or value < 0 for value in values)
                           for values in checkpoint['timings'].values())
                    or not isinstance(checkpoint['host_samples'], dict)
                    or set(checkpoint['host_samples']) != set(host_samples)
                    or not isinstance(checkpoint['host_samples']['states'], list)
                    or any(type(value) is not int or not 0 <= value <= 3 for value in checkpoint['host_samples']['states'])
                    or any(type(checkpoint['host_samples'][name]) is not int or checkpoint['host_samples'][name] < 0
                           for name in ('count', 'max_gap_ns'))
                    or any(not isinstance(checkpoint['host_samples'][name], dict)
                           or type(checkpoint['host_samples'][name].get('time_ns')) is not int
                           for name in ('first', 'last'))
                    or not isinstance(checkpoint['windows'], list) or not checkpoint['windows']
                    or any(not isinstance(window, dict)
                           or type(window.get('duration_seconds')) not in (int, float)
                           or not math.isfinite(window['duration_seconds']) or window['duration_seconds'] <= 0
                           or any(type(window.get(name)) is not int or window[name] < 0 for name in
                                  ('device_write_bytes', 'process_diskio_read_bytes', 'process_diskio_written_bytes'))
                           or (window.get('device_read_bytes') is not None
                               and (type(window['device_read_bytes']) is not int or window['device_read_bytes'] < 0))
                           for window in checkpoint['windows'])):
                _reject('ROOT_INVALID', attempt, 'source profile observation checkpoint is malformed')
            restored_boundary = checkpoint['source_boundary']
            if (not isinstance(restored_boundary, dict)
                    or (set(restored_boundary) != {'header_digest'} if header_bytes is not None
                        else set(restored_boundary) != {'offset', 'hash_state_digest', 'generation'})
                    or _DIGEST.fullmatch(str(restored_boundary.get('header_digest' if header_bytes is not None else 'hash_state_digest'))) is None
                    or (header_bytes is None and (type(restored_boundary.get('offset')) is not int
                        or not 0 <= restored_boundary['offset'] <= artifact.size
                        or type(restored_boundary.get('generation')) is not int or restored_boundary['generation'] < 0))):
                _reject('ROOT_INVALID', attempt, 'profile checkpoint lost its exact source boundary')
            if header_bytes is not None:
                if saved_header is not None and saved_header != restored_boundary['header_digest']:
                    _reject('ROOT_INVALID', attempt, 'profile header boundary differs from its expected digest')
                saved_header = restored_boundary['header_digest']
            totals, timings, host_samples, windows = (checkpoint[key] for key in
                                                     ('totals', 'timings', 'host_samples', 'windows'))
            host_samples['states'] = set(host_samples['states'])
            # The source executor's binary checkpoint remains the recovery authority. This
            # receipt restores observations only; the held job performs no new source I/O yet.
            self._append(self._load(operation_id), 'output_delta', {'source_profile_resume': {
                'capture_key': attempt, 'checkpoint_digest': capture_head['digest'],
                'extent_operation': extents['data'].operation_id}})
            await self.hold_boundary(operation_id, 'profile-checkpoint')
        def flush_locked():
            if trace:
                payload = bytes(trace)
                name = str(len(captures)) + '-' + uuid.uuid4().hex + '.jsonl'
                write_campaign_artifact(owner, attempt, name, payload)
                captures.append({'attempt': attempt, 'name': name, 'bytes': len(payload),
                                 'digest': digest_bytes(payload)})
                trace.clear()
        def record(row):
            with capture_lock:
                trace.extend(canonical_bytes(row) + b'\n')
                if len(trace) >= 1048576:
                    flush_locked()
        def flush():
            with capture_lock:
                flush_locked()
        def observe(role, event):
            phase = ('RETAINED_REVALIDATION' if revalidation else
                     'RESUME_VERIFY' if restored_boundary is not None else 'FRESH_WRITE_READBACK')
            record({'role': role, 'phase': phase, **event})
            if event['kind'] == 'VERIFIED_PREFIX':
                return
            totals['io_calls'] += 1
            totals['errors'] += not event['success']
            timings[event['kind']].append(event['duration_ns'])
            if event['kind'] in ('read', 'PARSER_READ'):
                totals['read_bytes'] += event['returned_bytes']
                if role == 'data':
                    totals['data_read_bytes'] += event['returned_bytes']
            elif event['kind'] == 'write':
                totals['write_bytes'] += event['returned_bytes']
                if role == 'data':
                    if event['offset'] != extents['data'].offset + totals['data_write_bytes']:
                        _reject('SOURCE_UNAVAILABLE', attempt, 'source profile write coverage is discontinuous', retryability='retryable')
                    totals['data_write_bytes'] += event['returned_bytes']
            if role == 'data' and event['kind'] in ('read', 'PARSER_READ') and revalidation:
                disk_bytes = event['process_diskio_read_bytes']
                totals['process_data_read_bytes'] += disk_bytes
                totals['data_reads_with_process_io' if disk_bytes else 'data_reads_without_process_io'] += 1
        measuring, held = True, False
        try:
            observed_extents = {role: replace(extent, observer=lambda event, role=role: observe(role, event),
                                             observe_process_reads=revalidation and role == 'data')
                                for role, extent in extents.items()}
            if revalidation:
                # A descriptor request does not evict existing cache pages. The samples below decide
                # whether this retained working-set window actually produced process-accounted I/O.
                command = getattr(fcntl, 'F_NOCACHE', None)
                if command is not None:
                    try:
                        fcntl.fcntl(observed_extents['data'].fd, command, 1)
                    except OSError as error:
                        _reject('CAPABILITY_MISMATCH', artifact.path, f'uncached descriptor request failed: {error}')
            async def checkpoint(partial):
                nonlocal capture_head, before, started, measuring, window_host, restored_boundary, held
                boundary = ({'header_digest': partial['header_digest']} if header_bytes is not None else {
                    'offset': partial.contiguous_source_hash_offset,
                    'generation': partial.checkpoint_generation,
                    'hash_state_digest': digest_bytes(partial.serialized_hash_state.encode())})
                if restored_boundary is not None:
                    if boundary != restored_boundary:
                        _reject('SOURCE_UNAVAILABLE', attempt, 'source checkpoint advanced beyond its durable measured boundary', retryability='retryable')
                record({'kind': 'SOURCE_BOUNDARY', 'time_ns': time.monotonic_ns(), 'source_boundary': boundary})
                if restored_boundary is not None:
                    restored_boundary = None
                holds = [event['payload'] for event in self._load(operation_id)['events'] if 'hold' in event['payload']]
                if not holds or holds[-1] != {'hold': 'REQUESTED', 'boundary': 'profile-checkpoint'}:
                    return
                measuring = False
                await close_window()
                snapshot = json.loads(canonical_bytes({'totals': totals, 'timings': timings,
                    'host_samples': {**host_samples, 'states': sorted(host_samples['states'])}, 'windows': windows,
                    'traces': captures, 'source_boundary': boundary}))
                capture_head = await asyncio.to_thread(compare_campaign_head, owner, attempt, capture_head['digest'],
                    {**context, 'status': 'CHECKPOINTED', 'traces': captures,
                     'checkpoint': snapshot, 'recovery_history': recovery_history})
                held = True
                await self.hold_boundary(operation_id, 'profile-checkpoint')
                held = False
                before = await asyncio.to_thread(drive_path_observation, selection)
                sample_host()
                window_host = host_samples['last']
                started = time.monotonic_ns()
                record({'kind': 'WINDOW_OPEN', 'started_ns': started, 'observer_pid': window_host['pid'],
                        'device': before, 'host': window_host})
                measuring = True
            def sample_host():
                sample = storage_host_observation()
                if host_samples['last'] is not None:
                    host_samples['max_gap_ns'] = max(host_samples['max_gap_ns'],
                        sample['time_ns'] - host_samples['last']['time_ns'])
                else:
                    host_samples['first'] = sample
                host_samples['last'] = sample
                host_samples['count'] += 1
                host_samples['states'].add(sample['thermal_state'])
                record({'kind': 'HOST_SAMPLE', **sample})
            async def sample_interval():
                while True:
                    await asyncio.sleep(.5)
                    if measuring:
                        sample_host()
            async def close_window():
                nonlocal measuring
                after = await asyncio.to_thread(drive_path_observation, selection)
                sample_host()
                finished = time.monotonic_ns()
                if before['path'] != baseline['path'] or after['path'] != baseline['path']:
                    _reject('CARTRIDGE_DISCONNECTED', operation_id, 'drive path changed during source-executor measurement')
                writes = (before['device_write_bytes'], after['device_write_bytes'])
                reads = (before.get('device_read_bytes'), after.get('device_read_bytes'))
                if None in writes or writes[1] < writes[0] or (None not in reads and reads[1] < reads[0]):
                    _reject('CAPABILITY_MISMATCH', operation_id, 'physical source telemetry is unavailable or regressed')
                windows.append({'started_ns': started, 'ended_ns': finished,
                    'duration_seconds': (finished - started) / 1e9,
                    'device_write_bytes': writes[1] - writes[0],
                    'device_read_bytes': None if None in reads else reads[1] - reads[0],
                    'observer_pid': window_host['pid'],
                    'process_diskio_read_bytes': host_samples['last']['process_diskio_read_bytes'] - window_host['process_diskio_read_bytes'],
                    'process_diskio_written_bytes': host_samples['last']['process_diskio_written_bytes'] - window_host['process_diskio_written_bytes'],
                    'counter_candidates': {'before': before.get('counter_candidates'), 'after': after.get('counter_candidates')},
                    'device_counters': {'before': {name: before.get(name) for name in
                        ('device_read_bytes', 'device_write_bytes', 'device_read_operations')},
                        'after': {name: after.get(name) for name in
                        ('device_read_bytes', 'device_write_bytes', 'device_read_operations')}}})
                record({'kind': 'WINDOW_CLOSE', 'ended_ns': finished, 'observer_pid': window_host['pid'],
                        'device': after, 'host': host_samples['last']})
                measuring = False
                await await_extent_io(flush)
            before = await asyncio.to_thread(drive_path_observation, selection)
            sample_host()
            window_host = host_samples['last']
            sampler = asyncio.create_task(sample_interval())
            started = time.monotonic_ns()
            record({'kind': 'WINDOW_OPEN', 'started_ns': started, 'observer_pid': window_host['pid'],
                    'device': before, 'host': window_host})
            try:
                if header_bytes is None:
                    partial = await transfer_artifact(adapter, revision, artifact,
                        observed_extents['data'], observed_extents['state'], owner,
                        checkpoint_committed=checkpoint)
                    if partial.contiguous_source_hash_offset != artifact.size:
                        _reject('ROOT_INVALID', artifact.path, 'profile source executor did not complete its artifact')
                    parsed = None
                else:
                    parsed = await transfer_header(adapter, revision, artifact, observed_extents['data'], owner,
                        expected_header_json_bytes=header_bytes, expected_header_digest=saved_header)
                    await checkpoint(parsed)
                await close_window()
            finally:
                sampler.cancel()
                try:
                    await sampler
                except asyncio.CancelledError:
                    pass
                finally:
                    await await_extent_io(flush)
            expected_writes = 0 if revalidation else artifact.size if header_bytes is None else header_bytes + 8
            if totals['data_write_bytes'] != expected_writes:
                _reject('SOURCE_UNAVAILABLE', attempt, 'source profile does not cover its exact data writes', retryability='retryable')
            statistics = await asyncio.to_thread(source_profile_trace, owner.cartridge, captures,
                expected_data_writes=expected_writes,
                expected_data_reads=artifact.size if header_bytes is None else header_bytes + 8, revalidation=revalidation,
                data_offset=extents['data'].offset, has_state='state' in extents,
                record_base=transfer_state_bytes(0), expected_path=baseline['path'])
            if (statistics['data_write_bytes'] != totals['data_write_bytes'] or statistics['io_calls'] != totals['io_calls']
                    or statistics['host_write_bytes'] != totals['write_bytes']
                    or statistics['data_read_bytes'] != totals['data_read_bytes']
                    or statistics['process_data_read_bytes'] != totals['process_data_read_bytes']):
                _reject('SOURCE_UNAVAILABLE', attempt, 'raw source trace differs from its live byte or call count', retryability='retryable')
            elapsed = sum(window['duration_seconds'] for window in windows)
            measurement = {'duration_seconds': elapsed, 'write_seconds': sum(timings['write']) / 1e9,
                    'read_seconds': (sum(timings['read']) + sum(timings['PARSER_READ'])) / 1e9,
                    'flush_seconds': (sum(timings['fsync']) + sum(timings['F_FULLFSYNC'])) / 1e9,
                    'readback_ok': True, 'flush_ok': True, 'errors': totals['errors'],
                    'host_write_bytes': totals['write_bytes'], 'observed_read_bytes': totals['read_bytes'],
                    'observed_data_write_bytes': totals['data_write_bytes'],
                    'observed_data_read_bytes': totals['data_read_bytes'],
                    'device_write_bytes': sum(window['device_write_bytes'] for window in windows),
                    'device_read_bytes': (None if any(window['device_read_bytes'] is None for window in windows)
                                          else sum(window['device_read_bytes'] for window in windows)),
                    'device_counter_authority': 'nearest IOBlockStorageDriver in bound native path; shared device interval',
                    'measurement_windows': windows, 'timing_evidence': 'SUM_OF_ACTIVE_WINDOWS; INTERRUPTIONS_EXCLUDED',
                    'trace_statistics': statistics,
                    'recovery_history': recovery_history,
                    'process_data_read_bytes': totals['process_data_read_bytes'],
                    'data_reads_with_process_io': totals['data_reads_with_process_io'],
                    'data_reads_without_process_io': totals['data_reads_without_process_io'],
                    'read_counter_scope': 'PROCESS_AND_SHARED_DEVICE_NOT_PER_PATH_OR_MEDIA',
                    'uncached_request': revalidation and getattr(fcntl, 'F_NOCACHE', None) is not None,
                    'data_allocated_bytes': os.fstat(extents['data'].fd).st_blocks * 512,
                    'io_calls': totals['io_calls'], 'iops': totals['io_calls'] / elapsed,
                    'io_latency_seconds': statistics['diagnostic_call_union']['empirical_percentiles'],
                    'flush_latency_seconds': statistics['diagnostic_flush_union']['empirical_percentiles'],
                    'legacy_latency_scope': 'DIAGNOSTIC_CALL_UNION_ONLY; QUALIFICATION_USES_SEPARATE_PHASES',
                    'host_telemetry': {'evidence': 'SAMPLED_STATE', 'samples': host_samples['count'],
                        'max_gap_seconds': statistics['max_in_window_sampling_gap_seconds'],
                        'scope': 'ACTIVE_WINDOWS_ONLY; DOWNTIME_REPORTED_SEPARATELY',
                        'thermal_states': sorted(host_samples['states']),
                        'process_diskio_read_bytes': sum(window['process_diskio_read_bytes'] for window in windows),
                        'process_diskio_written_bytes': sum(window['process_diskio_written_bytes'] for window in windows)},
                    'traces': captures, 'header': parsed, 'scratch_retention': 'NAMED_UNTIL_SEALED'}
            captured = await asyncio.to_thread(compare_campaign_head, owner, attempt, capture_head['digest'],
                {**context, 'status': 'CAPTURED', 'traces': captures, 'measurement': measurement,
                 'recovery_history': recovery_history})
            return {**measurement, 'capture_record_key': attempt, 'capture_record_digest': captured['digest']}
        except BaseException as error:
            failure = {'type': type(error).__name__, 'code': error.code if isinstance(error, CassetteError) else None,
                       'detail': str(error)}
            try:
                if measuring:
                    record({'kind': 'WINDOW_INTERRUPTED', 'ended_ns': time.monotonic_ns(), 'error': failure})
                await await_extent_io(flush)
            except BaseException as trace_error:
                failure['trace_flush_error'] = type(trace_error).__name__ + ': ' + str(trace_error)
            try:
                await await_extent_io(compare_campaign_head, owner, attempt, capture_head['digest'],
                    {**capture_head['value'], 'status': ('CHECKPOINTED' if capture_head['value'].get('status') == 'CHECKPOINTED'
                        and held else 'INCOMPLETE'), 'traces': captures, 'recovery_history': recovery_history,
                     'pending_trace_bytes': len(trace), 'error': failure})
            except BaseException as receipt_error:
                raise error from receipt_error
            raise

    async def _abandon_profile_extents(self, operation_id, owner, keys, error, capture_keys=()):
        """Q44/Q53/Q60: preserve failed evidence before reclaiming only its pinned synthetic files."""
        retained, sealed = [], []
        for key in keys:
            manifest = await asyncio.to_thread(campaign_head, owner.cartridge, key)
            if manifest is None or not isinstance(manifest['value'], dict):
                continue
            value = manifest['value']
            if value.get('status') == 'RETAINED':
                retained.append({'key': key, 'retained_digest': manifest['digest']})
            elif value.get('status') in {'SEALED', 'RECLAIMING'}:
                evidence = await asyncio.to_thread(campaign_head, owner.cartridge, value['evidence_key'])
                if (evidence is None or evidence['digest'] != value['evidence_digest']
                        or not isinstance(evidence['value'], dict) or evidence['value'].get('disposition') != 'ABANDONED'):
                    _reject('ROOT_INVALID', key, 'failed profile cleanup reached a completed measurement seal')
                sealed.append((key, manifest['digest'] if value['status'] == 'SEALED' else value['seal_digest']))
        if retained:
            captures = []
            for key in capture_keys:
                capture = await asyncio.to_thread(campaign_head, owner.cartridge, key)
                if capture is not None:
                    captures.append({'key': key, 'digest': capture['digest']})
            evidence_key = 'profile-abandoned-' + uuid.uuid4().hex
            evidence = await asyncio.to_thread(compare_campaign_head, owner, evidence_key, None, {
                'status': 'INCOMPLETE', 'disposition': 'ABANDONED', 'operation_id': operation_id,
                'error': error.payload(), 'captures': captures, 'retained_manifests': retained})
            for item in retained:
                manifest = await asyncio.to_thread(seal_profile_extents, owner, item['key'], item['retained_digest'],
                    evidence_key, evidence['digest'])
                sealed.append((item['key'], manifest['digest']))
        for key, digest in sealed:
            await asyncio.to_thread(reclaim_profile_extents, owner, key, digest)

    async def _qualify_download(self, operation_id, owner, selection, revision, *, header_lengths=None):
        """Q42/Q53/Q60: measure the source executor and retain its whole operation working set."""
        observed = await asyncio.to_thread(drive_path_observation, selection)
        host = await asyncio.to_thread(storage_host_observation)
        artifacts = revision.artifacts if header_lengths is not None else _acquisition_artifacts(revision)
        patterns = [{'artifact': artifact.path,
                     'write_bytes': artifact.size if header_lengths is None else header_lengths[artifact.path] + 8,
                     'read_bytes': artifact.size if header_lengths is None else header_lengths[artifact.path] + 8}
                    for artifact in artifacts]
        lengths = [{'data': artifact.size, **({'state': transfer_state_bytes(artifact.size)}
                                             if header_lengths is None else {})} for artifact in artifacts]
        binding = {'drive': selection.volume.volume_uuid, 'host': observed['path']['host'],
                   'path': observed['path'], 'operation': operation_id,
                   'profiler_version': STORAGE_PROFILER_VERSION,
                   'plan': {'source_lock': _source_record(revision), 'patterns_digest': digest_bytes(canonical_bytes(patterns)),
                            'queue_depth': 1, 'network_range_concurrency': 2,
                            'cache_state': 'FRESH_READBACK_AND_RETAINED_REVALIDATION',
                            'working_set_bytes': (sum(sum(item.values()) for item in lengths) if header_lengths is None
                                                  else sum(header_lengths[artifact.path] + 8 for artifact in artifacts)),
                            'retained_extent_logical_bytes': sum(sum(item.values()) for item in lengths),
                            'host_memory_bytes': host['host_memory_bytes'],
                            'artifact_bytes': sum(artifact.size for artifact in artifacts),
                            'checkpoint_pattern': 'SOURCE_EXECUTOR_ALTERNATING_SLOTS_AND_RECORDS',
                            'checkpoint_record_base': transfer_state_bytes(0),
                            'service_deadline_seconds': None, 'training_endurance': 'NOT_APPLICABLE',
                            'unavailable_telemetry': ['cable_capability', 'media_health'],
                            'thermal_evidence': 'SAMPLED_STATE_WITH_RETAINED_GAPS',
                            'uncached_read_request_available': getattr(fcntl, 'F_NOCACHE', None) is not None,
                            'cache_crossing_required': sum(pattern['read_bytes'] for pattern in patterns) > host['host_memory_bytes'],
                            'cold_read_verification': 'RETAINED_SOURCE_WINDOW; FLAG_ALONE_IS_NOT_PROOF'}}
        if header_lengths is not None:
            binding['plan'].update(header_only=True, header_json_bytes=header_lengths,
                artifact_ranges={artifact.path: [list(pair) for pair in header_ranges(artifact, header_lengths[artifact.path])]
                                 for artifact in artifacts}, checkpoint_pattern='SOURCE_EXECUTOR_HEADER_AND_COMPLETE_PARSER')
        key = 'download-profile-' + digest_bytes(canonical_bytes(binding)).split(':')[1]
        plan = {'binding': binding, 'pattern_count': len(patterns)}
        head = await asyncio.to_thread(campaign_head, owner.cartridge, key)
        if head is None:
            head = await asyncio.to_thread(compare_campaign_head, owner, key, None, plan)
        if head['value'] != plan:
            _reject('ROOT_INVALID', operation_id, 'saved acquisition profile differs from its source or path')
        complete = await asyncio.to_thread(campaign_head, owner.cartridge, key + '-complete')
        try:
            if complete is None:
                observations, revalidations, atom_digests, retained = [], [], [], []
                self._append(self._load(operation_id), 'output_delta', {'source_qualification': {'status': 'MEASURING'}})
                async with source_profile_boundary(revision, artifacts, header_lengths=header_lengths) as (adapter, synthetic):
                    for index, (artifact, pattern, shape) in enumerate(zip(synthetic.artifacts, patterns, lengths, strict=True)):
                        atom_key = key + '-' + str(index)
                        extent_key = atom_key + '-extents'
                        extent_binding = {'profile_digest': head['digest'], 'artifact': artifacts[index].record()}
                        manifest, extents = await asyncio.to_thread(grant_profile_extents, owner, extent_key, extent_binding, shape)
                        capture_key = 'source-' + manifest['digest'].split(':', 1)[1] + '-capture'
                        restart_error = None
                        try:
                            atom = await asyncio.to_thread(campaign_head, owner.cartridge, atom_key)
                            if atom is None:
                                measurement = await self._capture_source_profile(operation_id, owner, selection, observed,
                                    adapter, synthetic, artifact, extents,
                                    header_bytes=None if header_lengths is None else header_lengths[artifact.path],
                                    capture_key=capture_key)
                                if measurement['observed_data_write_bytes'] != pattern['write_bytes']:
                                    _reject('SOURCE_UNAVAILABLE', capture_key, 'profile does not cover its exact data writes', retryability='retryable')
                                atom = await asyncio.to_thread(compare_campaign_head, owner, atom_key, None,
                                    {'profile_digest': head['digest'], 'pattern': pattern, 'measurement': measurement})
                            if (not isinstance(atom['value'], dict)
                                    or set(atom['value']) != {'profile_digest', 'pattern', 'measurement'}
                                    or atom['value'].get('profile_digest') != head['digest']
                                    or atom['value'].get('pattern') != pattern
                                    or not isinstance(atom['value'].get('measurement'), dict)):
                                _reject('ROOT_INVALID', artifact.path, 'saved source profile atom differs from its exact plan')
                            parsed = atom['value']['measurement'].get('header')
                            if header_lengths is not None and (not isinstance(parsed, dict)
                                    or not isinstance(parsed.get('header_digest'), str)
                                    or _DIGEST.fullmatch(parsed['header_digest']) is None
                                    or parsed.get('header_bytes') != header_lengths[artifact.path] + 8):
                                _reject('ROOT_INVALID', artifact.path, 'saved profile header differs from its complete declared bytes')
                            observations.append({**atom['value']['measurement'], 'binding': binding, 'pattern': pattern})
                            atom_digests.append(atom['digest'])
                            retained.append((extent_key, manifest['digest']))
                        except CassetteError as error:
                            if error.code != 'SOURCE_UNAVAILABLE' or error.object_id != capture_key or error.retryability != 'retryable':
                                raise
                            restart_error = error
                        finally:
                            for extent in extents.values():
                                os.close(extent.fd)
                        if restart_error is not None:
                            await self._abandon_profile_extents(operation_id, owner, [extent_key], restart_error, [capture_key])
                            raise restart_error
                    # Reopen the complete retained working set; the source executor verifies every committed byte.
                    for index, artifact in enumerate(synthetic.artifacts):
                        extent_key, _ = retained[index]
                        manifest, extents = await asyncio.to_thread(grant_profile_extents, owner, extent_key,
                            {'profile_digest': head['digest'], 'artifact': artifacts[index].record()}, lengths[index])
                        try:
                            measurement = await self._capture_source_profile(operation_id, owner, selection, observed,
                                adapter, synthetic, artifact, extents,
                                header_bytes=None if header_lengths is None else header_lengths[artifact.path],
                                saved_header=None if header_lengths is None else observations[index]['header']['header_digest'],
                                revalidation=True, capture_key='source-' + manifest['digest'].split(':', 1)[1] + '-resume-capture')
                            if measurement['host_write_bytes'] or measurement['observed_read_bytes'] < patterns[index]['read_bytes']:
                                _reject('ROOT_INVALID', artifact.path, 'retained profile did not revalidate its complete bytes without writing')
                            proof_key = key + '-' + str(index) + '-resume'
                            proof = await asyncio.to_thread(campaign_head, owner.cartridge, proof_key)
                            if proof is None:
                                proof = await asyncio.to_thread(compare_campaign_head, owner, proof_key, None,
                                    {'profile_digest': head['digest'], 'artifact': artifact.path, 'measurement': measurement})
                            if (not isinstance(proof['value'], dict)
                                    or set(proof['value']) != {'profile_digest', 'artifact', 'measurement'}
                                    or proof['value'].get('profile_digest') != head['digest']
                                    or proof['value'].get('artifact') != artifact.path
                                    or not isinstance(proof['value'].get('measurement'), dict)):
                                _reject('ROOT_INVALID', artifact.path, 'saved retained read differs from its source profile')
                            atom_digests.append(proof['digest'])
                            revalidations.append({**proof['value']['measurement'], 'binding': binding, 'pattern': patterns[index]})
                        finally:
                            for extent in extents.values():
                                os.close(extent.fd)
                result = storage_profile(binding, patterns, observations, expected_binding=binding,
                                         revalidations=revalidations)
                seal = {'profile_digest': head['digest'], 'atom_count': len(atom_digests),
                        'atoms_digest': digest_bytes(canonical_bytes(atom_digests)), 'measurements': result,
                        'retained_manifests': [{'key': extent_key, 'retained_digest': manifest_digest}
                                               for extent_key, manifest_digest in retained]}
                complete = await asyncio.to_thread(compare_campaign_head, owner, key + '-complete', None, seal)
            value = complete['value']
            if (not isinstance(value, dict) or value.get('profile_digest') != head['digest']
                    or not isinstance(value.get('measurements'), dict)
                    or value['measurements'].get('binding') != binding
                    or not isinstance(value.get('retained_manifests'), list)
                    or any(not isinstance(item, dict) or set(item) != {'key', 'retained_digest'}
                           or not isinstance(item['retained_digest'], str)
                           or _DIGEST.fullmatch(item['retained_digest']) is None
                           for item in value['retained_manifests'])
                    or [item.get('key') if isinstance(item, dict) else None for item in value['retained_manifests']]
                        != [key + '-' + str(index) + '-extents' for index in range(len(artifacts))]):
                _reject('ROOT_INVALID', operation_id, 'completed source profile differs from its bound operation or extents')
            checked, digests = [[], []], []
            for phase, suffix in enumerate(('', '-resume')):
                for index, pattern in enumerate(patterns):
                    atom = await asyncio.to_thread(campaign_head, owner.cartridge, key + '-' + str(index) + suffix)
                    if (atom is None or not isinstance(atom['value'], dict)
                            or atom['value'].get('profile_digest') != head['digest']
                            or not isinstance(atom['value'].get('measurement'), dict)
                            or (atom['value'].get('pattern') != pattern if phase == 0
                                else atom['value'].get('artifact') != artifacts[index].path)):
                        _reject('ROOT_INVALID', operation_id, 'completed profile measurement is missing or differs')
                    measurement = atom['value']['measurement']
                    capture = await asyncio.to_thread(campaign_head, owner.cartridge, measurement.get('capture_record_key'))
                    if (capture is None or capture['digest'] != measurement.get('capture_record_digest')
                            or not isinstance(capture['value'], dict) or capture['value'].get('status') != 'CAPTURED'
                            or capture['value'].get('operation_id') != operation_id
                            or capture['value'].get('traces') != measurement.get('traces')
                            or capture['value'].get('measurement') != {name: value for name, value in measurement.items()
                                if name not in {'capture_record_key', 'capture_record_digest'}}
                            or not isinstance(measurement.get('traces'), list) or not measurement['traces']):
                        _reject('ROOT_INVALID', operation_id, 'source I/O capture is missing or differs from its measurement')
                    recomputed = await asyncio.to_thread(source_profile_trace, owner.cartridge, measurement['traces'],
                        expected_data_writes=0 if phase else pattern['write_bytes'], expected_data_reads=pattern['read_bytes'],
                        revalidation=bool(phase),
                        has_state=header_lengths is None, record_base=transfer_state_bytes(0), expected_path=binding['path'])
                    if (recomputed != measurement.get('trace_statistics')
                            or recomputed['data_write_bytes'] != measurement.get('observed_data_write_bytes')
                            or recomputed['host_write_bytes'] != measurement.get('host_write_bytes')
                            or recomputed['data_read_bytes'] != measurement.get('observed_data_read_bytes')
                            or recomputed['process_data_read_bytes'] != measurement.get('process_data_read_bytes')
                            or recomputed['io_calls'] != measurement.get('io_calls')):
                        _reject('ROOT_INVALID', operation_id, 'raw source rows differ from their claimed measurement statistics')
                    checked[phase].append({**measurement, 'binding': binding, 'pattern': pattern})
                    digests.append(atom['digest'])
            if (value.get('atom_count') != len(digests)
                    or value.get('atoms_digest') != digest_bytes(canonical_bytes(digests))
                    or storage_profile(binding, patterns, checked[0], expected_binding=binding,
                                       revalidations=checked[1]) != value['measurements']):
                _reject('ROOT_INVALID', operation_id, 'completed profile differs from its verified measurement and trace objects')
            # Reconcile after every entry, including a crash between global seal and individual reclamation.
            for retained in value['retained_manifests']:
                extent_key = retained['key']
                manifest = await asyncio.to_thread(campaign_head, owner.cartridge, extent_key)
                if manifest is None or not isinstance(manifest['value'], dict):
                    _reject('ROOT_INVALID', extent_key, 'completed profile extent manifest is missing or malformed')
                if manifest['value'].get('status') == 'RETAINED':
                    manifest = await asyncio.to_thread(seal_profile_extents, owner, extent_key,
                        retained['retained_digest'], key + '-complete', complete['digest'])
                if (manifest['value'].get('evidence_key') != key + '-complete'
                        or manifest['value'].get('evidence_digest') != complete['digest']):
                    _reject('ROOT_INVALID', extent_key, 'profile extent seal references another measurement')
                seal_digest = (manifest['digest'] if manifest['value'].get('status') == 'SEALED'
                               else manifest['value'].get('seal_digest'))
                await asyncio.to_thread(reclaim_profile_extents, owner, extent_key, seal_digest)
            result = complete['value']['measurements']
            receipt = {'status': result['status'], 'profile_digest': complete['digest'],
                       'profile_key': key + '-complete', 'path': str(owner.cartridge)}
            self._append(self._load(operation_id), 'output_delta', {'source_qualification': receipt})
            if result['status'] != 'PASS':
                _reject('CAPABILITY_MISMATCH', operation_id, 'source executor storage qualification is incomplete')
            return receipt
        except CassetteError as error:
            if complete is None and error.retryability == 'terminal':
                keys = [key + '-' + str(index) + '-extents' for index in range(len(artifacts))]
                capture_keys = []
                for index, extent_key in enumerate(keys):
                    manifest = await asyncio.to_thread(campaign_head, owner.cartridge, extent_key)
                    if manifest is not None and isinstance(manifest['value'], dict):
                        namespace = 'source-' + manifest['digest'].split(':', 1)[1]
                        capture_keys.extend((namespace + '-capture', namespace + '-resume-capture'))
                await self._abandon_profile_extents(operation_id, owner, keys, error, capture_keys)
            raise

    async def _inspect_headers(self, operation_id, adapter, owner, revision, profile_digest, header_lengths):
        """Q44/Q50: publish parsed headers separately from full-source and execution proof."""
        metadata = await adapter.read_metadata(revision)
        summaries = []
        source_digest = digest_bytes(canonical_bytes(_source_record(revision)))
        for artifact in revision.artifacts:
            binding = {'operation_id': operation_id, 'source_lock_digest': source_digest,
                       'artifact': artifact.record(), 'validator': artifact.validator,
                       'header_json_bytes': header_lengths[artifact.path],
                       'physical_profile_digest': profile_digest}
            key = 'source-header-' + digest_bytes(canonical_bytes(binding)).split(':')[1]
            head = await asyncio.to_thread(campaign_head, owner.cartridge, key)
            if head is not None and (not isinstance(head['value'], dict)
                    or set(head['value']) != {'binding', 'parsed'} or head['value']['binding'] != binding
                    or not isinstance(head['value']['parsed'], dict)
                    or set(head['value']['parsed']) != {'header_digest', 'header_bytes', 'inventory', 'payload_verification'}
                    or not isinstance(head['value']['parsed']['header_digest'], str)
                    or _DIGEST.fullmatch(head['value']['parsed']['header_digest']) is None):
                _reject('ROOT_INVALID', operation_id, 'saved header inventory differs from its source or profile')
            extent = await asyncio.to_thread(grant_transfer_extent, owner.cartridge, operation_id,
                _transfer_extent_id(operation_id, artifact.path, 'header'), artifact.size,
                capacity_controller=owner, require_existing=head is not None)
            try:
                parsed = await transfer_header(adapter, revision, artifact, extent, owner,
                    expected_header_json_bytes=header_lengths[artifact.path],
                    expected_header_digest=None if head is None else head['value']['parsed']['header_digest'])
            finally:
                os.close(extent.fd)
            if head is None:
                head = await asyncio.to_thread(compare_campaign_head, owner, key, None,
                                               {'binding': binding, 'parsed': parsed})
            elif head['value']['parsed'] != parsed:
                _reject('ROOT_INVALID', operation_id, 'saved header inventory differs from its verified header bytes')
            summaries.append({'path': artifact.path, 'header_bytes': parsed['header_bytes'],
                'header_digest': parsed['header_digest'], 'header_record_key': key,
                'header_record_digest': head['digest'], 'tensor_count': len(parsed['inventory']['tensors'])})
        summary_binding = {'operation_id': operation_id, 'source_lock_digest': source_digest,
                           'physical_profile_digest': profile_digest}
        key = 'source-headers-' + digest_bytes(canonical_bytes(summary_binding)).split(':')[1]
        value = {**summary_binding,
                 'metadata': metadata, 'artifacts': summaries, 'payload_verification': 'NOT_RUN'}
        head = await asyncio.to_thread(campaign_head, owner.cartridge, key)
        if head is None:
            head = await asyncio.to_thread(compare_campaign_head, owner, key, None, value)
        if head['value'] != value:
            _reject('ROOT_INVALID', operation_id, 'completed header inventory differs from its source evidence')
        self._append(self._load(operation_id), 'output_delta', {'source_headers': {
            'status': 'PARSED', 'artifacts': summaries, 'metadata_record_digest': head['digest'],
            'metadata_record_key': key, 'payload_verification': 'NOT_RUN'}})

    async def watch_drive_remount(self, request: dict) -> dict:
        """Q44/Q49: verify saved bytes after an observed or operator-reported physical reconnect."""
        self.operation_id(request)
        arguments = request['arguments']
        if (request['operation'] != 'drive.remount'
                or set(arguments) not in ({'context_ref'}, {'context_ref', 'reconnect_confirmed'})
                or ('reconnect_confirmed' in arguments and arguments['reconnect_confirmed'] is not True)):
            _reject('INVALID_REQUEST', 'drive.remount', 'remount requires the held Go operation')
        watcher_id = self.operation_id(request)
        if self._path(watcher_id).exists():
            recorded = self.issue(request)
            if recorded['state'] in _TERMINAL_STATES:
                return recorded
        operation_id = request['arguments']['context_ref']
        record = self._load(operation_id)
        prepared = [event['payload']['drive_prepared'] for event in record['events'] if 'drive_prepared' in event['payload']]
        holds = [event['payload'] for event in record['events'] if 'hold' in event['payload']]
        if record['kind'] != 'acquire' or not prepared or not holds or holds[-1] != {
                'hold': 'ACKNOWLEDGED', 'boundary': 'CARTRIDGE-DURABILITY'}:
            _reject('INVALID_REQUEST', operation_id, 'Go has no acknowledged physical durability hold')
        proof = prepared[-1]
        binding = proof['binding']
        async def verify():
            disconnected = any('drive_disconnected' in event['payload'] for event in self.events(operation_id))
            reported = arguments.get('reconnect_confirmed') is True
            if reported:
                self._append(self._load(operation_id), 'output_delta', {'physical_reconnect_reported': 'OPERATOR'})
            while not reported:
                volumes = await asyncio.to_thread(list_external_apfs_volumes)
                matches = [volume for volume in volumes if volume.volume_uuid == binding['volume_uuid']]
                if not matches and not disconnected:
                    self._append(self._load(operation_id), 'output_delta', {'drive_disconnected': binding['volume_uuid']})
                    disconnected = True
                elif disconnected and len(matches) == 1:
                    break
                await asyncio.sleep(0.25)
            selection = await asyncio.to_thread(select_external_apfs_volume, binding['volume_uuid'])
            cartridge = Path(selection.volume.mount_path) / binding['folder']
            lifecycle = CartridgeLifecycle(binding['cartridge_uuid'])
            await asyncio.to_thread(lifecycle.mount, cartridge, binding['volume_uuid'])
            head = await asyncio.to_thread(campaign_head, cartridge, proof['campaign_key'])
            if head is None or head['digest'] != proof['campaign_digest'] or head['value'] != binding:
                _reject('ROOT_INVALID', operation_id, 'campaign object or pointer changed across remount')
            probe = binding['probe']
            await asyncio.to_thread(verify_campaign_artifact, cartridge, probe['attempt'], probe['name'],
                                   probe['digest'], probe['bytes'])
            result = {'go_operation_id': operation_id, 'campaign_digest': head['digest'],
                      'selection': _json_copy(asdict(selection), operation_id, 'remounted selection'),
                      'source_qualification': 'NOT_RUN', 'model_bytes_downloaded': 0}
            self._append(self._load(operation_id), 'output_delta', {'drive_remounted': result})
            self.release_hold(operation_id, 'CARTRIDGE-DURABILITY')
            return result
        return await self.execute(request, verify)

    async def generate_native(
        self, request: dict, cartridge: str | Path, profile: dict,
        capacity_controller: CapacityCoordinator,
    ) -> dict:
        """Q5/Q10/Q20/Q63: own native generation and expose tokens only after the store commit."""
        if request.get("operation") != "run" or not capacity_controller.owns(cartridge):
            _reject("INVALID_REQUEST", "native-run", "native generation requires a run request and the cartridge capacity owner")
        operation_id = self.operation_id(request)
        arguments = request["arguments"]
        required = {"messages", "tools", "seed", "temperature", "max_tokens"}
        if not isinstance(arguments, dict) or not required <= set(arguments) or set(arguments) - required - {"pixels"}:
            _reject("INVALID_REQUEST", operation_id, "native request must name conversation, tools and exact sampler fields")
        maximum = arguments["max_tokens"]
        if type(maximum) is not int or not 0 < maximum <= 1_048_576:
            _reject("INVALID_REQUEST", operation_id, "max_tokens must be a bounded positive integer")
        request_digest = _json_digest(request, operation_id, "native request")

        def expose(tokens: list[int], root_digest: str) -> None:
            record = self._load(operation_id)
            emitted = [event["payload"]["token"] for event in record["events"]
                       if event["type"] == "output_delta" and "token_index" in event["payload"]]
            if emitted != tokens[:len(emitted)]:
                _reject("ROOT_INVALID", operation_id, "broker token events differ from the committed context")
            for index in range(len(emitted), len(tokens)):
                previous_text = decode_native_tokens(cartridge, root_digest, tokens[:index])
                current_text = decode_native_tokens(cartridge, root_digest, tokens[:index + 1])
                if not current_text.startswith(previous_text):
                    _reject("CAPABILITY_MISMATCH", operation_id, "source tokenizer cannot emit a stable append-only text delta")
                record = self._append(record, "output_delta", {
                    "token_index": index, "token": tokens[index], "committed_root": root_digest,
                    "text": current_text[len(previous_text):],
                })

        async def generate():
            pin = recover_generation(cartridge)
            if pin is None or load_root(cartridge, pin.root_digest)["identity"] != request.get("target"):
                _reject("IDENTITY_MISMATCH", operation_id, "native target is not the currently published model identity")
            graph = verify_native_bundle(cartridge, pin.root_digest)
            rendered = render_native_input(cartridge, pin.root_digest, arguments["messages"], arguments["tools"])
            if maximum + len(rendered["token_ids"]) > graph["context_limit"]:
                _reject("CAPABILITY_MISMATCH", operation_id, "prompt and requested generation exceed the source horizon")
            while True:
                runtime = NativeTransformer(cartridge, pin.root_digest, profile, operation_id, request_digest)
                tokens = runtime.state["generated_tokens"]
                expose(tokens, pin.root_digest)
                if tokens:
                    await self.hold_boundary(operation_id, "runtime-commit")
                if len(tokens) >= maximum:
                    return {"tokens": tokens, "text": decode_native_tokens(cartridge, pin.root_digest, tokens),
                            "root_digest": pin.root_digest, "position": runtime.state["position"],
                            "execution_mode": "COMPILED_CERTIFIED" if runtime.compiled else "NATIVE"}
                candidate = await runtime.execute_step(rendered["token_ids"], seed=arguments["seed"],
                                         temperature=arguments["temperature"], pixels=arguments.get("pixels"))
                pin = await _await_completion(asyncio.to_thread(
                    commit_runtime_state, cartridge, pin.root_digest, operation_id, candidate["payload"],
                    capacity_controller=capacity_controller,
                ))
                expose(candidate["state"]["generated_tokens"], pin.root_digest)
                await asyncio.sleep(0)

        async with self._model_execution_lock:
            return await self.execute(request, generate)

    async def train_native(self, request: dict, cartridge, profile: dict,
                           capacity_controller: CapacityCoordinator) -> dict:
        """Q5/Q21/Q25/Q73: own objective evaluation, durable windows and child publication."""
        arguments = request.get("arguments", {})
        if (request.get("operation") != "train" or set(arguments) != {"checkpoint_root", "manifest_digest"}
                or not capacity_controller.owns(cartridge)):
            _reject("INVALID_REQUEST", "native-training", "training requires a prepared checkpoint and its capacity owner")
        operation_id = self.operation_id(request)
        async def train():
            checkpoint, manifest = arguments["checkpoint_root"], arguments["manifest_digest"]
            record = self._load(operation_id)
            if record["checkpoint"]:
                checkpoint, manifest = record["checkpoint"]["checkpoint_root"], record["checkpoint"]["manifest_digest"]
            state = native_training_state(cartridge, checkpoint, manifest)
            if record["checkpoint"]:
                await self.hold_boundary(operation_id, "training-checkpoint")
            parent = load_root(cartridge, state["parent_root"])
            if request.get("target") != parent["identity"]:
                _reject("IDENTITY_MISMATCH", operation_id, "training target differs from the frozen parent")
            verify_native_bundle(cartridge, state["parent_root"], exact_source=True)
            runtime = NativeTransformer(cartridge, state["parent_root"], profile, operation_id, state["job_id"], purpose="EXACT_SOURCE_TRAINING")
            reference = None
            if state["reference_root"]:
                verify_native_bundle(cartridge, state["reference_root"], exact_source=True)
                reference = NativeTransformer(cartridge, state["reference_root"], profile, operation_id, state["job_id"], purpose="EXACT_SOURCE_TRAINING")
            while not state["complete"]:
                state, batch, adapters = native_training_inputs(cartridge, checkpoint, manifest)
                result = runtime.objective(state["operation"], batch, adapters,
                    differentiate=state["adapters"][state["window"]]["tensor_id"], reference=reference, beta=state["beta"],
                    training_context=native_training_context(state, manifest))
                checkpoint, manifest = await _await_completion(asyncio.to_thread(
                    advance_native_training, cartridge, checkpoint, manifest, result, capacity_controller=capacity_controller))
                self._write({**self._load(operation_id), "checkpoint": {
                    "checkpoint_root": checkpoint, "manifest_digest": manifest}})
                state = native_training_state(cartridge, checkpoint, manifest)
                await self.hold_boundary(operation_id, "training-checkpoint")
                await asyncio.sleep(0)
            compiled_parent = parent["plans"][0].get("compiled")
            if compiled_parent:
                teacher = NativeTransformer(cartridge, checkpoint, profile, operation_id, state["job_id"], purpose="EXACT_SOURCE_OBSERVATION")
                tensor_id = teacher.graph["nodes"][-1]["weights"][0]
                source, target = prepare_native_effective_source(cartridge, checkpoint, tensor_id, teacher.effective_tensor(tensor_id),
                    capacity_controller=capacity_controller, operation_id=operation_id)
                workload = json.loads(canonical_bytes(compiled_parent["observations"]["workload"]))
                workload["baseline"]["root_digest"] = source
                observations = capture_native(cartridge, source, profile, workload)
                child = prepare_native_compiled(cartridge, source, observations, compiled_parent["horizon"],
                    compiled_parent["profile"], compiled_parent["prior_failures"], capacity_controller=capacity_controller,
                    operation_id=operation_id, effective_target=target, rank_budget=compiled_parent["rank_budget"],
                    read_deadline_ns=compiled_parent["read_deadline_ns"])
            else:
                child = prepare_native_training_child(cartridge, state["parent_root"], checkpoint, manifest,
                    capacity_controller=capacity_controller, operation_id=operation_id)
            pin = await _await_completion(asyncio.to_thread(commit_generation, cartridge, operation_id, child,
                expected_parent_root=state["parent_root"], capacity_controller=capacity_controller, operation_id=operation_id))
            return {"root_digest": pin.root_digest, "identity": pin.child_id, "manifest_digest": manifest}
        async with self._model_execution_lock:
            return await self.execute(request, train)

    def native_capability(self, cartridge) -> dict:
        """Q31/Q77: describe only the currently published graph and implemented client behavior."""
        pin = recover_generation(cartridge)
        if pin is None:
            _reject("IDENTITY_MISMATCH", "capabilities", "cartridge has no published model")
        root = load_root(cartridge, pin.root_digest)
        graph = verify_native_bundle(cartridge, pin.root_digest)
        result = {"protocol_version": "1", "model_refs": [root["identity"]], "modalities": ["text"],
                  "context": {"maximum_tokens": graph["context_limit"], "history": "EXPLICIT_MESSAGES"},
                  "reasoning": False, "tools": {"prompt_definitions": True, "generated_calls": False},
                  "structured_output": {"supported": False}, "streaming": True, "cancellation": True,
                  "training": {"operations": ["ADAPTER_SFT", "ADAPTER_CONTINUED_PRETRAINING", "OFFLINE_ADAPTER_DPO"],
                               "preparation": "IMMUTABLE_CHECKPOINT", "compiled_recovery": "compiled" in root["plans"][0],
                               "sequence_inputs": ["tokens", "mask"] + (["pixels"] if any(node["operator"] == "image" for node in graph["nodes"]) else [])},
                  "source": {"identity": root["identity"], "root_digest": pin.root_digest,
                             "execution_mode": "COMPILED_CERTIFIED" if "compiled" in root["plans"][0] else "NATIVE"},
                  "performance_tiers": []}
        defects = validate("capability_profile", result)
        if defects:
            _reject("ROOT_INVALID", root["identity"], "; ".join(defects[:8]))
        return result

    def client_request(self, request: dict) -> dict:
        """Q31/Q76: route a canonical client request through actual committed model execution."""
        defects = validate("run_request", request)
        if defects:
            _reject("INVALID_REQUEST", "client-run", "; ".join(defects[:8]))
        if any(name in request for name in ("reasoning", "output_schema", "context_ref", "extensions")):
            _reject("CAPABILITY_MISMATCH", request["idempotency_key"], "runtime cannot silently consume an unimplemented reasoning, schema, context or extension contract")
        messages = request["input"]
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        generation = request.get("generation", {})
        options = generation.get("options", {})
        allowed = {"max_output_tokens", "max_completion_tokens", "temperature", "seed", "stream", "options"}
        if set(generation) - allowed or not isinstance(options, dict) or set(options) - {"temperature", "seed", "num_predict"}:
            _reject("CAPABILITY_MISMATCH", request["idempotency_key"], "client generation settings have no exact implemented runtime meaning")
        for names, values in ((('seed',), [generation.get('seed'), options.get('seed')]),
                              (('temperature',), [generation.get('temperature'), options.get('temperature')]),
                              (('maximum output tokens',), [generation.get('max_output_tokens'), generation.get('max_completion_tokens'), options.get('num_predict')])):
            present = [value for value in values if value is not None]
            if present and any(value != present[0] for value in present):
                _reject("CAPABILITY_MISMATCH", request["idempotency_key"], f"conflicting client values for {names[0]}")
        if generation.get("stream", True) is not True:
            _reject("CAPABILITY_MISMATCH", request["idempotency_key"], "listener currently requires streaming output")
        arguments = {"messages": messages, "tools": request.get("tools", []),
            "seed": generation.get("seed", options.get("seed", 0)),
            "temperature": generation.get("temperature", options.get("temperature", 0.0)),
            "max_tokens": generation.get("max_output_tokens", generation.get("max_completion_tokens", options.get("num_predict", 1)))}
        canonical = {"protocol_version": "1", "operation": "run", "idempotency_key": request["idempotency_key"],
                     "target": request["model_ref"], "arguments": arguments}
        return canonical

    async def run_client(self, request: dict, cartridge, profile: dict,
                         capacity_controller: CapacityCoordinator) -> tuple[dict, list[dict]]:
        canonical = self.client_request(request)
        result = await self.generate_native(canonical, cartridge, profile, capacity_controller)
        return result, list(self.events(self.operation_id(canonical)))

    async def stream_client(self, request: dict, cartridge, profile: dict,
                            capacity_controller: CapacityCoordinator):
        """Q5/Q31: stream each committed event while the owned generation is still running."""
        canonical = self.client_request(request)
        operation_id = self.operation_id(canonical)
        signal = self._event_signals.setdefault(operation_id, asyncio.Event())
        self.issue(canonical)
        task = asyncio.create_task(self.generate_native(canonical, cartridge, profile, capacity_controller))
        cursor = -1
        try:
            while True:
                signal.clear()
                for event in self.events(operation_id, after=cursor):
                    cursor = event["sequence"]
                    yield event
                if task.done():
                    await task
                    for event in self.events(operation_id, after=cursor):
                        yield event
                    break
                waiter = asyncio.create_task(signal.wait())
                try:
                    await asyncio.wait((waiter, task), return_when=asyncio.FIRST_COMPLETED)
                finally:
                    waiter.cancel()
                    with suppress(asyncio.CancelledError):
                        await waiter
        finally:
            if not task.done():
                task.cancel()
            with suppress(asyncio.CancelledError):
                await task
            self._event_signals.pop(operation_id, None)

    async def listen(self, handler, *, port: int = 0):
        """Q5/Q76: stream bounded HTTP or JSONL requests on this process's loopback socket."""
        async def connection(reader, writer):
            jsonl, started = False, False
            responses = None
            try:
                first = await asyncio.wait_for(reader.readline(), 10)
                if len(first) > 65536:
                    _reject("INVALID_REQUEST", "loopback", "request line exceeds 64 KiB")
                jsonl = first.startswith(b"{")
                if jsonl:
                    wire = {"encoding": "jsonl", "record": json.loads(first)}
                else:
                    method, path, version = first.decode('ascii').strip().split(' ')
                    if version != "HTTP/1.1" or method not in {"POST", "GET"}:
                        _reject("INVALID_REQUEST", "loopback", "listener requires a declared HTTP/1.1 GET or POST surface")
                    headers, total = {}, len(first)
                    while True:
                        line = await asyncio.wait_for(reader.readline(), 10)
                        total += len(line)
                        if total > 65536 or not line:
                            _reject("INVALID_REQUEST", "loopback", "headers exceed their bound or ended before the body")
                        if line == b"\r\n":
                            break
                        name, value = line.decode('ascii').split(':', 1)
                        if name.lower() in {item.lower() for item in headers}:
                            _reject("INVALID_REQUEST", "loopback", "duplicate request header")
                        headers[name] = value.strip()
                    lower = {name.lower(): value for name, value in headers.items()}
                    length = int(lower.get("content-length", "0"))
                    if "transfer-encoding" in lower or not 0 <= length <= 1048576 or (method == "POST" and not length):
                        _reject("INVALID_REQUEST", "loopback", "body requires one bounded explicit content length")
                    body = json.loads(await asyncio.wait_for(reader.readexactly(length), 10)) if length else {}
                    translated = {name: value for name, value in headers.items() if name.lower() not in {"host", "content-length", "connection"}}
                    wire = {"method": method, "path": path, "headers": translated, "body": body}
                responses = handler(wire)
                async for response in responses:
                    encoding = response["encoding"]
                    if not started and not jsonl:
                        content_type = {"sse": "text/event-stream", "json": "application/json"}.get(encoding, "application/x-ndjson")
                        writer.write(f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nTransfer-Encoding: chunked\r\nConnection: close\r\n\r\n".encode())
                    started = True
                    for frame in response.get("frames", response.get("records", [])):
                        payload = (b"data: " + canonical_bytes(frame) + b"\n\n") if encoding == "sse" else canonical_bytes(frame) + b"\n"
                        writer.write(payload if jsonl else f"{len(payload):x}\r\n".encode() + payload + b"\r\n")
                        await writer.drain()
                if not jsonl:
                    writer.write(b"0\r\n\r\n")
                    await writer.drain()
            except (CassetteError, ValueError, UnicodeError, asyncio.IncompleteReadError, TimeoutError) as error:
                failure = error if isinstance(error, CassetteError) else CassetteError("INVALID_REQUEST", "loopback", "Q6: bounded request parsing", "terminal", str(error))
                payload = canonical_bytes({"error": failure.payload()}) + b"\n"
                if not started:
                    writer.write(payload if jsonl else f"HTTP/1.1 400 Bad Request\r\nContent-Length: {len(payload)}\r\nConnection: close\r\n\r\n".encode() + payload)
                    await writer.drain()
            except (ConnectionError, BrokenPipeError):
                pass
            finally:
                if responses is not None:
                    await responses.aclose()
                writer.close()
                with suppress(ConnectionError, BrokenPipeError):
                    await writer.wait_closed()
        return await asyncio.start_server(connection, "127.0.0.1", port, limit=65537)

    async def export_revision(
        self,
        request: dict,
        cartridge: str | Path,
        capacity_controller: CapacityCoordinator,
    ) -> dict:
        """Execute one Q26 export whose request binds the exact root and target schema."""

        operation_id = self.operation_id(request)

        def export() -> dict:
            arguments = request.get("arguments")
            if (
                request.get("operation") != "export"
                or not isinstance(arguments, dict)
                or set(arguments) != {"target_schema"}
            ):
                _reject("INVALID_REQUEST", operation_id, "export requires one canonical export request")
            target_schema = arguments.get("target_schema")
            root_digest = request.get("target")
            plan = plan_export(cartridge, root_digest, target_schema)
            merged = (
                merge_adapter_material(adapter_merge_material(cartridge, root_digest))
                if plan["mode"] == "merged"
                else None
            )
            return export_store_revision(
                cartridge, operation_id, plan, capacity_controller, merged
            )

        return await self.execute(
            request, lambda: asyncio.to_thread(export), cancellable=False
        )

    async def apply_delta(
        self,
        request: dict,
        cartridge: str | Path,
        delta: dict,
        payloads: Mapping[str, bytes],
        capacity_controller: CapacityCoordinator,
        publication_controller: CapacityCoordinator,
    ) -> dict:
        """Publish only the exact Q54 target whose request binds its base and delta digest."""

        operation_id = self.operation_id(request)

        def apply() -> dict:
            arguments = request.get("arguments")
            base_root = request.get("target")
            if (
                request.get("operation") != "apply_delta"
                or not isinstance(arguments, dict)
                or set(arguments) != {"delta_digest"}
                or not isinstance(delta, dict)
                or arguments.get("delta_digest") != delta.get("delta_digest")
            ):
                _reject("INVALID_REQUEST", operation_id, "delta request is detached from its declared digest")
            current = recover_generation(cartridge)
            if current is None or current.root_digest != base_root:
                _reject(
                    "DELTA_BASE_MISMATCH",
                    operation_id,
                    "delta base is not the current callable revision",
                    invariant="Q54: exact callable base before delta publication",
                )
            candidate = apply_store_delta(
                cartridge, operation_id, base_root, delta, payloads, capacity_controller
            )
            pin = commit_generation(
                cartridge,
                operation_id,
                candidate,
                expected_parent_root=base_root,
                capacity_controller=publication_controller,
                operation_id=operation_id,
            )
            return {
                "generation": pin.generation,
                "revision_id": pin.child_id,
                "root_digest": pin.root_digest,
                "model_identity": load_root(cartridge, pin.root_digest)["identity"],
            }

        return await self.execute(
            request, lambda: asyncio.to_thread(apply), cancellable=False
        )

    async def remove_revision(
        self,
        request: dict,
        cartridge: str | Path,
        reachability: dict,
        capacity_controller: CapacityCoordinator,
    ) -> dict:
        """Execute exact revision removal only through its request-bound reachability proof."""

        operation_id = self.operation_id(request)

        def remove() -> dict:
            arguments = request.get("arguments")
            if (
                request.get("operation") != "remove_revision"
                or not isinstance(arguments, dict)
                or set(arguments) != {"reachability_digest"}
                or not isinstance(reachability, dict)
                or arguments.get("reachability_digest") != reachability.get("reachability_digest")
            ):
                _reject("INVALID_REQUEST", operation_id, "removal request is detached from its reachability proof")
            result = remove_store_revision(
                cartridge,
                operation_id,
                request.get("target"),
                reachability,
                capacity_controller,
            )
            return result

        return await self.execute(
            request, lambda: asyncio.to_thread(remove), cancellable=False
        )

    async def advance_acquisition(self, request: dict, context: AcquisitionContext) -> dict:
        """Execute exactly one Q5 transition; a new broker process may execute the next one."""

        operation = self.issue(request)
        operation_id = operation["operation_id"]
        if request["operation"] not in {PREPARE_OPERATION, ACQUIRE_OPERATION}:
            _reject("INVALID_REQUEST", operation_id, "acquisition requires operation='prepare' or operation='acquire'")
        async with self._lock(operation_id):
            record = self._load(operation_id)
            if record["state"] in _TERMINAL_STATES or record["state"] == "PAUSED":
                return self._operation(record)
            try:
                if record["cancel_requested"]:
                    raise _ControlStop("cancel")
                if record["pause_requested"]:
                    raise _ControlStop("pause")
                await self.hold_boundary(operation_id, record["phase"])
                record = self._load(operation_id)
                advanced = await self._advance(record, request, context)
                if advanced["state"] not in _TERMINAL_STATES:
                    await self.hold_boundary(operation_id, advanced["phase"])
                return self.status(operation_id)
            except _ControlStop as stopped:
                return self._operation(self._stop(self._load(operation_id), stopped.action))
            except asyncio.CancelledError:
                raise
            except CassetteError as error:
                if error.retryability == "retryable":
                    return self._operation(self._paused(self._load(operation_id), error))
                return self._operation(self._failed(self._load(operation_id), error))

    async def run_acquisition(self, request: dict, context: AcquisitionContext) -> dict:
        """Resume Q5 until its operation-specific terminal phase or one typed terminal result."""

        for _ in range(len(PHASES) + 1):
            operation = await self.advance_acquisition(request, context)
            if operation["state"] in _TERMINAL_STATES or operation["state"] == "PAUSED":
                return operation
        _reject("CAPABILITY_MISMATCH", operation["operation_id"], "Q5 state machine exceeded its exact phase count")

    def callable_revision(self, operation_id: str, cartridge: str | Path) -> GenerationPin:
        """Return only a store-verified generation whose broker phase reached PUBLISHED."""

        record = self._load(operation_id)
        if record["kind"] == "train" and record["state"] == "SUCCEEDED":
            pin = recover_generation(cartridge)
            if pin is None or pin.root_digest != record["result"]["root_digest"] or pin.child_id != record["result"]["identity"]:
                _reject("ROOT_INVALID", operation_id, "training result differs from its published generation")
            verify_native_bundle(cartridge, pin.root_digest)
            return pin
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
        if not context.capacity_controller.owns(context.cartridge):
            _reject(
                "INVALID_REQUEST",
                operation_id,
                "capacity coordinator does not own the acquisition cartridge filesystem",
            )
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
                parent = await _await_completion(asyncio.to_thread(recover_generation, context.cartridge))
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
        if phase == "RESOLVED":
            return self._phase(record, "ACQUIRING", checkpoint)
        if phase == "ACQUIRING":
            async def acquire():
                artifacts = (
                    _acquisition_artifacts(revision)
                    if request["operation"] == ACQUIRE_OPERATION
                    else _compiler_artifacts(revision)
                )
                if context.transfers is None and request["operation"] != ACQUIRE_OPERATION:
                    _reject(
                        "INVALID_REQUEST",
                        operation_id,
                        "prepare requires caller-granted source transfer extents",
                    )
                if context.transfers is not None and (
                        not isinstance(context.transfers, Mapping)
                        or set(context.transfers) != {artifact.path for artifact in artifacts}):
                    _reject("INVALID_REQUEST", operation_id, "transfers must name every required source artifact exactly once")
                partials = []
                for artifact in artifacts:
                    async def checkpoint_committed(partial):
                        self._transfer_progress[operation_id] = {
                            'artifact': artifact.path, 'received_bytes': partial.contiguous_source_hash_offset,
                            'verified_bytes': partial.contiguous_source_hash_offset,
                            'verification': 'CHUNK_READBACK', 'checkpoint': 'DURABLE'}
                        await self.hold_boundary(operation_id, 'source-checkpoint')
                    owned_extents = context.transfers is None
                    if owned_extents:
                        data_extent = await asyncio.to_thread(
                            grant_transfer_extent,
                            context.cartridge,
                            operation_id,
                            _transfer_extent_id(operation_id, artifact.path, "data"),
                            artifact.size,
                            capacity_controller=context.capacity_controller,
                        )
                        try:
                            state_extent = await asyncio.to_thread(
                                grant_transfer_extent,
                                context.cartridge,
                                operation_id,
                                _transfer_extent_id(operation_id, artifact.path, "state"),
                                transfer_state_bytes(artifact.size),
                                capacity_controller=context.capacity_controller,
                            )
                        except Exception:
                            os.close(data_extent.fd)
                            raise
                    else:
                        extents = context.transfers[artifact.path]
                        if (not isinstance(extents, tuple) or len(extents) != 2
                                or not all(isinstance(extent, TransferExtent) for extent in extents)):
                            _reject("INVALID_REQUEST", operation_id, f"{artifact.path} requires data and state extents")
                        data_extent, state_extent = extents
                    try:
                        partials.append(await transfer_artifact(
                            context.adapter,
                            revision,
                            artifact,
                            data_extent,
                            state_extent,
                            context.capacity_controller,
                            checkpoint_committed=checkpoint_committed,
                        ))
                    finally:
                        if owned_extents:
                            os.close(state_extent.fd)
                            os.close(data_extent.fd)
                    progress = {'artifact': artifact.path, 'received_bytes': artifact.size,
                                'verified_bytes': artifact.size, 'verification': 'SOURCE_DIGEST', 'checkpoint': 'DURABLE'}
                    current = self._load(operation_id)
                    if not any(event['payload'] == progress for event in current['events']):
                        self._append(current, 'output_delta', progress)
                return [
                    _partial_record(artifact.path, partial)
                    for artifact, partial in zip(artifacts, partials, strict=True)
                ]

            checkpoint["partials"] = await self._controlled(operation_id, acquire, cancellable=True)
            record = self._load(operation_id)
            artifacts = (
                _acquisition_artifacts(revision)
                if request["operation"] == ACQUIRE_OPERATION
                else _compiler_artifacts(revision)
            )
            _verify_partials(checkpoint["partials"], revision, operation_id, artifacts)
            if request["operation"] == ACQUIRE_OPERATION:
                result = {
                    "immutable_revision": revision.immutable_revision,
                    "verified_artifacts": [
                        {"path": artifact.path, "size": artifact.size, "digest": artifact.digest}
                        for artifact in artifacts
                    ],
                    "verified_bytes": sum(artifact.size for artifact in artifacts),
                }
                return self._success(
                    record,
                    result,
                    phase="SOURCE_VERIFIED",
                    checkpoint=checkpoint,
                    event_payload={"phase": "SOURCE_VERIFIED", "result": result},
                )
            return self._phase(record, "SOURCE_VERIFIED", checkpoint)
        _verify_partials(checkpoint["partials"], revision, operation_id)
        if phase == "SOURCE_VERIFIED":
            material = await self._controlled(operation_id,
                lambda: asyncio.to_thread(inspect_source_identity,
                    _compiler_source(revision, descriptor),
                    _compiler_extents(revision, context.transfers, operation_id), context.cartridge),
                cancellable=True)
            identity = model_identity(material)
            if any(expected is not None and expected != identity
                   for expected in (revision.identity, descriptor.get("expected_identity"))):
                _reject("IDENTITY_MISMATCH", operation_id, "verified source bytes differ from the expected full-model identity")
            revision = replace(revision, identity=identity)
            checkpoint["source_lock"] = _source_record(revision)
            plan_digest = await self._controlled(
                operation_id,
                lambda: asyncio.to_thread(
                    plan_revision,
                    _compiler_source(revision, descriptor),
                    _compiler_extents(revision, context.transfers, operation_id),
                    context.cartridge,
                ),
                cancellable=True,
            )
            checkpoint["plan_digest"] = _exact_digest(plan_digest, operation_id, "plan digest")
            return self._phase(record, "PLANNED", checkpoint)
        if phase == "PLANNED":
            return self._phase(record, "PREPARING", checkpoint)
        if phase == "PREPARING":
            prepared = await self._controlled(
                operation_id,
                lambda: asyncio.to_thread(
                    prepare_revision,
                    _compiler_source(revision, descriptor),
                    _compiler_extents(revision, context.transfers, operation_id),
                    context.cartridge,
                    checkpoint["plan_digest"],
                    capacity_coordinator=context.capacity_controller,
                    operation_id=operation_id,
                ),
                cancellable=True,
            )
            checkpoint.update(await self._controlled(
                operation_id,
                lambda: asyncio.to_thread(
                    self._verify_prepared,
                    operation_id,
                    context.cartridge,
                    revision,
                    checkpoint["plan_digest"],
                    prepared,
                    _compiler_extents(revision, context.transfers, operation_id),
                ),
                cancellable=True,
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
                    capacity_controller=context.capacity_controller,
                    operation_id=operation_id,
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
                "model_identity": load_root(context.cartridge, pin.root_digest)["identity"],
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
        source_descriptors: Mapping[str, dict],
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
            for artifact in _compiler_artifacts(revision)
        )
        if prepared.verified_artifacts != expected:
            _reject("IDENTITY_MISMATCH", operation_id, "present-byte verification differs from resolved artifacts")
        root_digest = _exact_digest(prepared.candidate_root, operation_id, "candidate root")
        root = load_root(cartridge, root_digest)
        identity_material = root.get("provenance", {}).get("identity_material", {})
        if (
            root.get("parents") != [revision.identity]
            or identity_material.get("source_kind") != revision.source_kind
            or identity_material.get("locator") != revision.locator
            or identity_material.get("immutable_revision") != revision.immutable_revision
            or identity_material.get("artifacts") != [
                {"path": item.path, "size": item.size, "digest": item.digest} for item in expected
            ]
        ):
            _reject("IDENTITY_MISMATCH", operation_id, "candidate root is not bound to the durable source lock")
        if root["plans"][0].get("version") == "native-v1":
            verify_native_bundle(cartridge, root_digest, revision.identity, plan_digest)
        else:
            plan, certificate, evidence, profile, compiled_identity = verify_bundle_structure(
                cartridge,
                root_digest,
                revision.identity,
                plan_digest,
                {name: record["fd"] for name, record in source_descriptors.items()},
            )
            if root["identity"] != compiled_identity:
                _reject("IDENTITY_MISMATCH", operation_id, "verified bundle and candidate identity disagree")
            admit_schedule(plan, certificate, evidence, profile)
        verify_root_content(cartridge, root_digest)
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
            if not inspect.isawaitable(value):
                return value
            return await _await_completion(value)

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
            self._control_signals.pop(operation_id, None)

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
                else {"phase": "SOURCE_VERIFIED", "result": record["result"]}
                if record["kind"] == ACQUIRE_OPERATION
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
        if record["kind"] in {PREPARE_OPERATION, ACQUIRE_OPERATION}:
            if set(record["checkpoint"]) != _CHECKPOINT_FIELDS[record["phase"]]:
                _reject("ROOT_INVALID", object_id, f"checkpoint does not match phase {record['phase']}")
            transitions = [
                event["payload"]["phase"]
                for event in events
                if "phase" in event["payload"] and "state" not in event["payload"]
            ]
            if transitions != list(PHASES[:PHASES.index(record["phase"]) + 1]):
                _reject("ROOT_INVALID", object_id, "event phases do not form the exact Q5 prefix")
            maximum_phase = "SOURCE_VERIFIED" if record["kind"] == ACQUIRE_OPERATION else "ACTIVE"
            if PHASES.index(record["phase"]) > PHASES.index(maximum_phase):
                _reject("ROOT_INVALID", object_id, "acquisition-only operation advanced past SOURCE_VERIFIED")
            if record["phase"] == "EMPTY" and record["state"] not in {
                "PENDING", "PAUSED", "CANCELLED", "FAILED",
            }:
                _reject("ROOT_INVALID", object_id, "EMPTY preparation has an impossible operation state")
            if record["phase"] in PHASES[1:PHASES.index(maximum_phase)] and record["state"] not in {
                "RUNNING", "PAUSED", "CANCELLED", "FAILED",
            }:
                _reject("ROOT_INVALID", object_id, "preparation phase has an impossible operation state")
            if record["phase"] == maximum_phase and record["state"] != "SUCCEEDED":
                _reject("ROOT_INVALID", object_id, f"{maximum_phase} acquisition terminal must be successful")
            self._verify_checkpoint(record, object_id)
        elif record["kind"] == "train" and record["checkpoint"]:
            if record["phase"] != "EMPTY" or set(record["checkpoint"]) != {"checkpoint_root", "manifest_digest"}:
                _reject("ROOT_INVALID", object_id, "training checkpoint fields or phase differ")
            for field, value in record["checkpoint"].items():
                _exact_digest(value, object_id, field)
        elif record["phase"] != "EMPTY" or record["checkpoint"]:
            _reject("ROOT_INVALID", object_id, "operation has an unowned checkpoint")
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
        artifacts = (
            _acquisition_artifacts(revision)
            if record["kind"] == ACQUIRE_OPERATION
            else _compiler_artifacts(revision)
        )
        if phase >= PHASES.index("SOURCE_VERIFIED"):
            _verify_partials(checkpoint["partials"], revision, object_id, artifacts)
        if record["kind"] == ACQUIRE_OPERATION:
            return
        if phase >= PHASES.index("PLANNED"):
            _exact_digest(revision.identity, object_id, "parsed source identity")
            _exact_digest(checkpoint["plan_digest"], object_id, "plan digest")
        if phase >= PHASES.index("EXEC_VERIFIED"):
            verification = checkpoint["source_verification"]
            expected = [
                {"path": item.path, "size": item.size, "digest": item.digest}
                for item in _compiler_artifacts(revision)
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

    def _claim_log_transition(self, transition: CapacityTransition) -> CapacityClaim:
        """Claim one exact broker-log transition through its own filesystem coordinator."""

        if (
            not isinstance(self._capacity_coordinator, CapacityCoordinator)
            or not self._capacity_coordinator.owns(self.operation_log)
        ):
            _reject(
                "INVALID_REQUEST",
                transition.operation_id,
                "operation-log capacity coordinator does not own the log filesystem",
            )
        claim = self._capacity_coordinator(transition)
        if not claim.active:
            _reject(
                "CAPACITY_EXCEEDED",
                transition.operation_id,
                "operation-log next transition is paused for recoverable capacity",
                retryability="retryable",
            )
        return claim

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
        if (record["state"] not in _TERMINAL_STATES and record["phase"] == "ACQUIRING"
                and record["operation_id"] in self._transfer_progress):
            result["result"] = {"transfer_progress": dict(self._transfer_progress[record["operation_id"]])}
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
        holds = [event["payload"] for event in record["events"] if "hold" in event["payload"]]
        if holds and holds[-1]["hold"] != "RELEASED":
            _reject("INVALID_REQUEST", record["operation_id"], "operation cannot finish before its requested hold and release")
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

    def _paused(self, record: dict, error: CassetteError | None = None) -> dict:
        payload = {"phase": record["phase"], "state": "PAUSED"}
        if error is not None:
            payload["error"] = error.payload()
        return self._append(
            record,
            "output_delta",
            payload,
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
        if updated["state"] in _TERMINAL_STATES or updated["phase"] != "ACQUIRING":
            self._transfer_progress.pop(record["operation_id"], None)
        signal = self._event_signals.get(record["operation_id"])
        if signal is not None:
            signal.set()
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
        if self._owner_fd is None:
            _reject(
                "OVERLOADED",
                f"broker:{self.operation_log}",
                "operation-log owner is closed",
                retryability="retryable",
            )
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
        transition = CapacityTransition(
            operation_id,
            f"operation-log:{operation_id}",
            journal_bytes=len(payload),
            declared_writes=2,
            write_bytes=(len(payload), 0),
        )
        claim = self._claim_log_transition(transition)
        try:
            def write_temporary() -> None:
                with temporary.open("wb") as handle:
                    if handle.write(payload) != len(payload):
                        raise OSError("operation-log temporary write was incomplete")
                    handle.flush()
                    os.fsync(handle.fileno())
                    command = getattr(fcntl, "F_FULLFSYNC", None)
                    if command is not None:
                        fcntl.fcntl(handle.fileno(), command)

            execute_claimed_write(claim, write_temporary)
            if temporary.read_bytes() != payload:
                _reject("DURABILITY_UNSUPPORTED", operation_id, "operation-log readback changed")

            execute_claimed_write(claim, lambda: os.replace(temporary, path))
            descriptor = os.open(self.operation_log, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
            complete_capacity_claim(claim)
        except CassetteError:
            if claim.active:
                pause_capacity_claim(claim, "operation-log record did not reach its durable boundary")
            raise
        except OSError as error:
            if claim.active:
                pause_capacity_claim(claim, "operation-log record did not reach its durable boundary")
            _reject("DURABILITY_UNSUPPORTED", operation_id, f"operation-log commit failed: {error}")

    def _lock(self, operation_id: str) -> asyncio.Lock:
        return self._execution_locks.setdefault(operation_id, asyncio.Lock())

    def _signal(self, operation_id: str) -> asyncio.Event:
        return self._control_signals.setdefault(operation_id, asyncio.Event())


_KEYCHAIN_SERVICE = "org.cassette.source-credential.v1"
_KEYCHAIN_REF_PREFIX = "keychain:v1:"
_ERR_SEC_AUTH_FAILED = -25293
_ERR_SEC_ITEM_NOT_FOUND = -25300
_ERR_SEC_INTERACTION_NOT_ALLOWED = -25308
_ERR_SEC_INTERACTION_REQUIRED = -25315
_ERR_SEC_USER_CANCELED = -128


class _CFDictionaryCallbacks(ctypes.Structure):
    """Match CoreFoundation's six-field CFDictionary callback records."""

    _fields_ = (
        ("version", ctypes.c_long),
        ("retain", ctypes.c_void_p),
        ("release", ctypes.c_void_p),
        ("copy_description", ctypes.c_void_p),
        ("equal", ctypes.c_void_p),
        ("hash", ctypes.c_void_p),
    )


class MacOSSourceCredentialProvider:
    """Resolve endpoint-bound Keychain tokens and the existing Ollama signing key."""

    def __init__(self) -> None:
        if sys.platform != "darwin":
            _reject("CAPABILITY_MISMATCH", "keychain", "macOS Keychain is unavailable on this platform")
        try:
            self._core_foundation = ctypes.CDLL(
                "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation"
            )
            self._security = ctypes.CDLL("/System/Library/Frameworks/Security.framework/Security")
            self._configure()
            self._keys = _CFDictionaryCallbacks.in_dll(
                self._core_foundation, "kCFTypeDictionaryKeyCallBacks"
            )
            self._values = _CFDictionaryCallbacks.in_dll(
                self._core_foundation, "kCFTypeDictionaryValueCallBacks"
            )
        except (AttributeError, OSError, ValueError):
            _reject("CAPABILITY_MISMATCH", "keychain", "macOS Keychain is unavailable in this process")

    def save(self, provider: str, endpoint: str, token: str) -> str:
        """Save one nonempty token and return its opaque credential reference."""
        binding = self._binding(provider, endpoint)
        if not isinstance(token, str) or not token:
            _reject("INVALID_REQUEST", "keychain", "credential token must be a nonempty string")
        reference = _KEYCHAIN_REF_PREFIX + uuid.uuid4().hex
        attributes = self._dictionary((
            (self._constant("kSecClass"), self._constant("kSecClassGenericPassword")),
            (self._constant("kSecAttrService"), self._text(_KEYCHAIN_SERVICE)),
            (self._constant("kSecAttrAccount"), self._text(reference)),
            (self._constant("kSecAttrGeneric"), self._data(binding)),
            (self._constant("kSecValueData"), self._data(token.encode("utf-8"))),
            (self._constant("kSecUseAuthenticationUI"), self._constant("kSecUseAuthenticationUIFail")),
        ))
        try:
            self._require(self._security.SecItemAdd(attributes, None), reference)
            return reference
        finally:
            self._release(attributes)

    def lookup_callback(self, provider: str, endpoint: str) -> Callable[[str], str | Callable[[bytes], str] | None]:
        """Return the one-argument credential lookup callback SourceAdapter accepts."""
        self._binding(provider, endpoint)
        return lambda reference: self.load(reference, provider, endpoint)

    def existing_login(self, provider: str, endpoint: str) -> str:
        """Bind an existing provider-owned key without copying or changing that key."""
        _, public = self._ollama_key()
        return 'ollama-key:v1:' + digest_bytes(self._binding(provider, endpoint) + public)

    @staticmethod
    def _ollama_key() -> tuple[bytes, bytes]:
        """Read Ollama's unencrypted OpenSSH Ed25519 key; reject other encodings."""
        try:
            with (Path.home() / '.ollama/id_ed25519').open('rb') as stream:
                if os.fstat(stream.fileno()).st_mode & 0o077:
                    raise ValueError('key permissions')
                encoded = stream.read(4097)
            lines = encoded.strip().splitlines()
            if (len(encoded) > 4096 or lines[0] != b'-----BEGIN OPENSSH PRIVATE KEY-----'
                    or lines[-1] != b'-----END OPENSSH PRIVATE KEY-----'):
                raise ValueError('key envelope')
            block = base64.b64decode(b''.join(lines[1:-1]), validate=True)
            if not block.startswith(b'openssh-key-v1\0'):
                raise ValueError('key format')
            cursor = 15

            def word() -> int:
                nonlocal cursor
                if cursor + 4 > len(block):
                    raise ValueError('truncated key')
                value = int.from_bytes(block[cursor:cursor + 4], 'big')
                cursor += 4
                return value

            def field() -> bytes:
                nonlocal cursor
                length = word()
                if cursor + length > len(block):
                    raise ValueError('truncated key field')
                value = block[cursor:cursor + length]
                cursor += length
                return value

            if field() != b'none' or field() != b'none' or field() != b'' or word() != 1:
                raise ValueError('encrypted or multiple keys')
            public = field()
            private = field()
            if cursor != len(block) or len(private) % 8:
                raise ValueError('key extent')
            block, cursor = private, 0
            if word() != word() or field() != b'ssh-ed25519':
                raise ValueError('key check or type')
            raw_public, raw_private = field(), field()
            field()  # OpenSSH comment does not participate in authentication.
            padding = block[cursor:]
            if (len(raw_public) != 32 or len(raw_private) != 64
                    or raw_private[32:] != raw_public
                    or public != b'\0\0\0\x0bssh-ed25519\0\0\0\x20' + raw_public
                    or not padding or padding != bytes(range(1, len(padding) + 1))):
                raise ValueError('key identity or padding')
            return raw_private[:32], public
        except (OSError, ValueError, IndexError):
            _reject('AUTH_REQUIRED', 'ollama', 'existing Ollama login key is missing, unreadable or invalid', retryability='retryable')

    def _sign_ollama(self, reference: str, provider: str, endpoint: str, challenge: bytes) -> str:
        """Use CPython's linked OpenSSL Ed25519 primitive; author no signing algorithm."""
        seed, public = self._ollama_key()
        if reference != 'ollama-key:v1:' + digest_bytes(self._binding(provider, endpoint) + public):
            _reject('AUTH_REQUIRED', reference, 'Ollama login key or endpoint binding changed', retryability='retryable')
        try:
            crypto = ctypes.CDLL(_ssl.__file__)
            function_types = {
                'OBJ_txt2nid': (ctypes.c_int, [ctypes.c_char_p]),
                'EVP_PKEY_new_raw_private_key': (ctypes.c_void_p, [ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]),
                'EVP_PKEY_get_raw_public_key': (ctypes.c_int, [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t)]),
                'EVP_MD_CTX_new': (ctypes.c_void_p, []),
                'EVP_DigestSignInit': (ctypes.c_int, [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]),
                'EVP_DigestSign': (ctypes.c_int, [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t), ctypes.c_char_p, ctypes.c_size_t]),
                'EVP_PKEY_free': (None, [ctypes.c_void_p]),
                'EVP_MD_CTX_free': (None, [ctypes.c_void_p]),
            }
            for name, (result, arguments) in function_types.items():
                function = getattr(crypto, name)
                function.restype, function.argtypes = result, arguments
        except (AttributeError, OSError):
            _reject('CAPABILITY_MISMATCH', 'ollama', 'this Python SSL runtime lacks the required OpenSSL Ed25519 symbols')
        key = crypto.EVP_PKEY_new_raw_private_key(crypto.OBJ_txt2nid(b'ED25519'), None, seed, len(seed))
        context = crypto.EVP_MD_CTX_new()
        try:
            derived_public, public_size = ctypes.create_string_buffer(32), ctypes.c_size_t(32)
            if (not key or not context or crypto.EVP_PKEY_get_raw_public_key(key, derived_public, ctypes.byref(public_size)) != 1
                    or public_size.value != 32 or derived_public.raw != public[-32:]):
                _reject('AUTH_REQUIRED', reference, 'Ollama private key does not match its public identity', retryability='retryable')
            signature, size = ctypes.create_string_buffer(64), ctypes.c_size_t(64)
            if (crypto.EVP_DigestSignInit(context, None, None, None, key) != 1
                    or crypto.EVP_DigestSign(context, signature, ctypes.byref(size), challenge, len(challenge)) != 1
                    or size.value != 64):
                _reject('CAPABILITY_MISMATCH', reference, 'OpenSSL could not sign the Ollama authorization challenge')
            return base64.b64encode(public).decode('ascii') + ':' + base64.b64encode(signature.raw).decode('ascii')
        finally:
            crypto.EVP_MD_CTX_free(context)
            crypto.EVP_PKEY_free(key)

    def load(self, reference: str, provider: str, endpoint: str) -> str | Callable[[bytes], str] | None:
        """Resolve one reference only when its stored provider and endpoint binding matches."""
        binding = self._binding(provider, endpoint)
        if isinstance(reference, str) and reference.startswith('ollama-key:v1:'):
            if reference != self.existing_login(provider, endpoint):
                _reject('AUTH_REQUIRED', reference, 'Ollama login key or endpoint binding changed', retryability='retryable')
            return lambda challenge: self._sign_ollama(reference, provider, endpoint, challenge)
        self._reference(reference)
        query = self._query(reference, binding, return_data=True)
        result = ctypes.c_void_p()
        try:
            status = self._security.SecItemCopyMatching(query, ctypes.byref(result))
        finally:
            self._release(query)
        if status == _ERR_SEC_ITEM_NOT_FOUND:
            if self._exists(reference):
                _reject("CAPABILITY_MISMATCH", reference, "credential reference belongs to a different provider endpoint")
            _reject("AUTH_REQUIRED", reference, "credential reference is absent or revoked", retryability="retryable")
        self._require(status, reference)
        try:
            length = self._core_foundation.CFDataGetLength(result)
            pointer = self._core_foundation.CFDataGetBytePtr(result)
            token = ctypes.string_at(pointer, length).decode("utf-8")
        except UnicodeDecodeError:
            _reject("AUTH_REQUIRED", reference, "credential token cannot be read", retryability="retryable")
        finally:
            self._release(result)
        return token or None

    def revoke(self, reference: str, provider: str, endpoint: str) -> None:
        """Delete one matching Cassette credential without enumerating Keychain items."""
        binding = self._binding(provider, endpoint)
        self._reference(reference)
        query = self._query(reference, binding, return_data=False)
        try:
            status = self._security.SecItemDelete(query)
        finally:
            self._release(query)
        if status == _ERR_SEC_ITEM_NOT_FOUND:
            if self._exists(reference):
                _reject("CAPABILITY_MISMATCH", reference, "credential reference belongs to a different provider endpoint")
            _reject("AUTH_REQUIRED", reference, "credential reference is absent or revoked", retryability="retryable")
        self._require(status, reference)

    def _configure(self) -> None:
        self._core_foundation.CFStringCreateWithCString.argtypes = (
            ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32
        )
        self._core_foundation.CFStringCreateWithCString.restype = ctypes.c_void_p
        self._core_foundation.CFDataCreate.argtypes = (
            ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_long
        )
        self._core_foundation.CFDataCreate.restype = ctypes.c_void_p
        self._core_foundation.CFDictionaryCreate.argtypes = (
            ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_long, ctypes.POINTER(_CFDictionaryCallbacks), ctypes.POINTER(_CFDictionaryCallbacks),
        )
        self._core_foundation.CFDictionaryCreate.restype = ctypes.c_void_p
        self._core_foundation.CFDataGetLength.argtypes = (ctypes.c_void_p,)
        self._core_foundation.CFDataGetLength.restype = ctypes.c_long
        self._core_foundation.CFDataGetBytePtr.argtypes = (ctypes.c_void_p,)
        self._core_foundation.CFDataGetBytePtr.restype = ctypes.POINTER(ctypes.c_ubyte)
        self._core_foundation.CFRelease.argtypes = (ctypes.c_void_p,)
        self._security.SecItemAdd.argtypes = (ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))
        self._security.SecItemAdd.restype = ctypes.c_int32
        self._security.SecItemCopyMatching.argtypes = (ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))
        self._security.SecItemCopyMatching.restype = ctypes.c_int32
        self._security.SecItemDelete.argtypes = (ctypes.c_void_p,)
        self._security.SecItemDelete.restype = ctypes.c_int32

    @staticmethod
    def _binding(provider: str, endpoint: str) -> bytes:
        if (not isinstance(provider, str) or not provider or not isinstance(endpoint, str)
                or not endpoint):
            _reject("INVALID_REQUEST", "keychain", "provider and endpoint must be nonempty strings")
        return canonical_bytes({"endpoint": endpoint, "provider": provider})

    @staticmethod
    def _reference(reference: str) -> None:
        if (not isinstance(reference, str) or not reference.startswith(_KEYCHAIN_REF_PREFIX)
                or len(reference) != len(_KEYCHAIN_REF_PREFIX) + 32):
            _reject("INVALID_REQUEST", "keychain", "credential reference is not a Cassette Keychain reference")
        try:
            uuid.UUID(hex=reference[len(_KEYCHAIN_REF_PREFIX):])
        except ValueError:
            _reject("INVALID_REQUEST", "keychain", "credential reference is not a Cassette Keychain reference")

    def _query(self, reference: str, binding: bytes | None, *, return_data: bool) -> ctypes.c_void_p:
        pairs = [
            (self._constant("kSecClass"), self._constant("kSecClassGenericPassword")),
            (self._constant("kSecAttrService"), self._text(_KEYCHAIN_SERVICE)),
            (self._constant("kSecAttrAccount"), self._text(reference)),
            (self._constant("kSecUseAuthenticationUI"), self._constant("kSecUseAuthenticationUIFail")),
        ]
        if binding is not None:
            pairs.append((self._constant("kSecAttrGeneric"), self._data(binding)))
        if return_data:
            pairs.append((self._constant("kSecReturnData"), self._boolean("kCFBooleanTrue")))
        return self._dictionary(tuple(pairs))

    def _exists(self, reference: str) -> bool:
        query = self._query(reference, None, return_data=False)
        try:
            status = self._security.SecItemCopyMatching(query, None)
        finally:
            self._release(query)
        if status == _ERR_SEC_ITEM_NOT_FOUND:
            return False
        self._require(status, reference)
        return True

    def _constant(self, name: str) -> int:
        return ctypes.c_void_p.in_dll(self._security, name).value

    def _boolean(self, name: str) -> int:
        return ctypes.c_void_p.in_dll(self._core_foundation, name).value

    def _text(self, value: str) -> int:
        return self._core_foundation.CFStringCreateWithCString(None, value.encode("utf-8"), 0x08000100)

    def _data(self, value: bytes) -> int:
        raw = (ctypes.c_ubyte * len(value)).from_buffer_copy(value)
        return self._core_foundation.CFDataCreate(None, raw, len(value))

    def _dictionary(self, pairs: tuple[tuple[int, int], ...]) -> ctypes.c_void_p:
        keys = (ctypes.c_void_p * len(pairs))(*(key for key, _ in pairs))
        values = (ctypes.c_void_p * len(pairs))(*(value for _, value in pairs))
        result = self._core_foundation.CFDictionaryCreate(
            None, keys, values, len(pairs), ctypes.byref(self._keys), ctypes.byref(self._values)
        )
        for _, value in pairs:
            if value not in {
                self._constant("kSecClassGenericPassword"),
                self._constant("kSecUseAuthenticationUIFail"),
                self._boolean("kCFBooleanTrue"),
            }:
                self._release(value)
        return result

    def _release(self, value: ctypes.c_void_p | int | None) -> None:
        if value:
            self._core_foundation.CFRelease(value)

    @staticmethod
    def _require(status: int, reference: str) -> None:
        if status == 0:
            return
        if status in {_ERR_SEC_AUTH_FAILED, _ERR_SEC_INTERACTION_NOT_ALLOWED,
                      _ERR_SEC_INTERACTION_REQUIRED, _ERR_SEC_USER_CANCELED}:
            _reject("AUTH_REQUIRED", reference, "macOS Keychain access was denied", retryability="retryable")
        _reject("CAPABILITY_MISMATCH", reference, "macOS Keychain cannot complete this credential operation")
