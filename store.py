# store.py — identity, content, lifecycle, capacity, integrity, repair, transactions, and generations (Q1/Q25/Q32/Q49/Q53/Q57/Q60/Q62/Q73); depends on errors.py, schema.
"""Own model identity, content, cartridge lifecycle, repair, and callable generations.

Source adapters may accept mutable aliases, but they must return a canonical locator and a typed
immutable revision digest. Requested aliases remain provenance; they never enter the identity.
Cassette-owned identities and canonical content use BLAKE3 through this module alone. SafeTensors
and GGUF payloads enter bounded pages and segments; tensor maps retain their semantic byte ranges
while a separate fixed-record index owns physical placement.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
import ctypes
from dataclasses import dataclass, field, replace
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import struct
import tempfile
import uuid

from blake3 import blake3
import rfc8785
import resumablesha256

from errors import CassetteError
from schema.validator import validate

_DIGEST_HEX_LENGTHS = {"blake3": 64, "sha256": 64, "git-sha1": 40}
_HEX = frozenset("0123456789abcdef")
_REVISION_KINDS = frozenset({"source", "executable", "tuned", "exported"})
_MAX_JSON_INTEGER = 2**53 - 1
_MAX_UNSIGNED_BYTES = 2**64 - 1
_CAPACITY_FIELDS = (
    "committed", "inflight", "candidate", "rollback", "optimizer", "master",
    "dataset", "precision", "journal", "repair",
)
_INTEGRITY_STATES = frozenset({
    "VALID", "SUSPECT", "VERIFYING", "CORRUPT", "REPAIRING", "UNAVAILABLE",
})
_INTEGRITY_TRANSITIONS = {
    "VALID": frozenset({"SUSPECT"}),
    "SUSPECT": frozenset({"VERIFYING"}),
    "VERIFYING": frozenset({"VALID", "CORRUPT"}),
    "CORRUPT": frozenset({"REPAIRING"}),
    "REPAIRING": frozenset({"VALID", "UNAVAILABLE"}),
    "UNAVAILABLE": frozenset(),
}
_CARTRIDGE_TRANSITIONS = {
    "UNMOUNTED": frozenset({"MOUNTED_UNVERIFIED"}),
    "MOUNTED_UNVERIFIED": frozenset({"MOUNTED_VERIFIED", "READ_ONLY", "DISCONNECTED", "FAILED"}),
    "MOUNTED_VERIFIED": frozenset({"ACTIVE", "UNMOUNTED", "DISCONNECTED", "SLEEPING", "REVALIDATING", "FAILED"}),
    "ACTIVE": frozenset({"QUIESCING", "DISCONNECTED", "SLEEPING", "REVALIDATING", "FAILED"}),
    "QUIESCING": frozenset({"MOUNTED_VERIFIED", "READ_ONLY", "DISCONNECTED", "SLEEPING", "REVALIDATING", "FAILED"}),
    "DISCONNECTED": frozenset({"REVALIDATING"}),
    "SLEEPING": frozenset({"REVALIDATING"}),
    "REVALIDATING": frozenset({"MOUNTED_VERIFIED", "READ_ONLY", "DISCONNECTED", "SLEEPING", "FAILED"}),
    "READ_ONLY": frozenset({"UNMOUNTED", "DISCONNECTED", "SLEEPING", "REVALIDATING", "FAILED"}),
    "FAILED": frozenset({"UNMOUNTED", "DISCONNECTED", "REVALIDATING"}),
}
_CARTRIDGE_EVENTS = {
    "disconnect": "DISCONNECTED", "sleep": "SLEEPING", "wake": "REVALIDATING",
    "bus_reset": "REVALIDATING", "port_migration": "REVALIDATING",
}
_CARTRIDGE_IDENTITY_NAME = "cartridge.json"
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
_GGUF_HEADER_BYTES = 100_000_000
_GGUF_MAX_ITEMS = 1_048_576
_GGUF_SCALARS = {
    0: "<B", 1: "<b", 2: "<H", 3: "<h", 4: "<I", 5: "<i", 6: "<f",
    7: "<?", 10: "<Q", 11: "<q", 12: "<d",
}
_GGUF_TENSOR_TYPES = {
    0: ("F32", 1, 4),
    1: ("F16", 1, 2),
    2: ("Q4_0", 32, 18),
    3: ("Q4_1", 32, 20),
    6: ("Q5_0", 32, 22),
    7: ("Q5_1", 32, 24),
    8: ("Q8_0", 32, 34),
    9: ("Q8_1", 32, 40),
    10: ("Q2_K", 256, 84),
    11: ("Q3_K", 256, 110),
    12: ("Q4_K", 256, 144),
    13: ("Q5_K", 256, 176),
    14: ("Q6_K", 256, 210),
    15: ("Q8_K", 256, 292),
    24: ("I8", 1, 1),
    25: ("I16", 1, 2),
    26: ("I32", 1, 4),
    27: ("I64", 1, 8),
    28: ("F64", 1, 8),
    30: ("BF16", 1, 2),
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
_LOG2PHYS = struct.Struct("=Iqq")
_F_LOG2PHYS_EXT = 65
_LIBC = ctypes.CDLL(None, use_errno=True)
_FCLONEFILEAT = getattr(_LIBC, "fclonefileat", None)
if _FCLONEFILEAT is not None:
    _FCLONEFILEAT.argtypes = (ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32)
    _FCLONEFILEAT.restype = ctypes.c_int


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
class CartridgeIdentity:
    """The exact Q49 logical, physical, and callable identity verified at one mount epoch."""

    cartridge_uuid: str
    filesystem_uuid: str
    root_generation: int | None
    root_digest: str | None


@dataclass(frozen=True)
class CartridgeAccess:
    """One epoch-bound Q49 operation authority; invalidation makes it unusable before I/O."""

    operation_id: str
    epoch: int
    write: bool


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


@dataclass(frozen=True)
class CapacityPhase:
    """One Q53 lifecycle phase, stated in exact unsigned bytes by storage owner."""

    committed: int = 0
    inflight: int = 0
    candidate: int = 0
    rollback: int = 0
    optimizer: int = 0
    master: int = 0
    dataset: int = 0
    precision: int = 0
    journal: int = 0
    repair: int = 0

    def __post_init__(self) -> None:
        for field in _CAPACITY_FIELDS:
            _capacity_value(field, getattr(self, field), "capacity:phase")

    @property
    def total(self) -> int:
        """Return this phase's checked Q53 sum."""

        return _capacity_sum(
            (getattr(self, field) for field in _CAPACITY_FIELDS), "capacity:phase"
        )


@dataclass(frozen=True)
class CapacityRequirement:
    """The one Q53 phase maximum and safety calculation, before physical reservation."""

    device_bytes: int
    safety_bytes: int
    phase_totals: tuple[int, ...]
    repair_bytes: int
    required_bytes: int


@dataclass(frozen=True)
class CapacityReservation:
    """A Q53 extent owned by one operation until its terminal cleanup releases it."""

    operation_id: str
    device_bytes: int
    safety_bytes: int
    phase_totals: tuple[int, ...]
    repair_bytes: int
    required_bytes: int
    _release_extent: Callable[[int], bool] = field(repr=False, compare=False)
    active: bool = field(default=True, init=False)


@dataclass(frozen=True)
class RepairSet:
    """The verified replica and parity identities declared for one immutable root."""

    root_digest: str
    manifest_digest: str
    index_digest: str
    parity_digests: tuple[str, ...]
    required_bytes: int


@dataclass(frozen=True)
class IntegrityReport:
    """One Q62 verification or repair result with every legal state transition retained."""

    root_digest: str
    states: tuple[tuple[str, str], ...]
    transitions: tuple[tuple[str, str, str], ...]
    unavailable_pages: tuple[str, ...]

    @property
    def available(self) -> bool:
        """Whether a new run may address every page in this revision."""

        return not self.unavailable_pages


class CartridgeLifecycle:
    """Own the exact Q49 state machine and issue no reusable filesystem handle."""

    def __init__(self, cartridge_uuid: str):
        self._cartridge_uuid = _normalize_uuid(cartridge_uuid, "cartridge_uuid")
        self._state = "UNMOUNTED"
        self._identity: CartridgeIdentity | None = None
        self._path: Path | None = None
        self._epoch = 0
        self._access: CartridgeAccess | None = None
        self._transitions: list[tuple[str, str]] = []

    @property
    def state(self) -> str:
        return self._state

    @property
    def identity(self) -> CartridgeIdentity | None:
        return self._identity

    @property
    def transitions(self) -> tuple[tuple[str, str], ...]:
        return tuple(self._transitions)

    def _move(self, state: str) -> None:
        if state not in _CARTRIDGE_TRANSITIONS[self._state]:
            _lifecycle_reject(
                self._cartridge_uuid,
                f"illegal cartridge lifecycle transition {self._state} -> {state}",
                "INVALID_REQUEST",
            )
        prior = self._state
        self._state = state
        self._transitions.append((prior, state))

    def _invalidate(self) -> None:
        self._epoch += 1
        self._path = None
        self._access = None

    def mount(
        self,
        cartridge: str | Path,
        filesystem_uuid: str,
        *,
        replacement: bool = False,
    ) -> CartridgeIdentity:
        """Verify one mounted volume completely before publishing its path to an operation."""

        filesystem_uuid = _normalize_uuid(filesystem_uuid, "filesystem_uuid")
        if self._state == "UNMOUNTED":
            self._invalidate()
            self._move("MOUNTED_UNVERIFIED")
        elif self._state in {"DISCONNECTED", "FAILED"}:
            self._invalidate()
            self._move("REVALIDATING")
        elif self._state != "REVALIDATING":
            _lifecycle_reject(
                self._cartridge_uuid,
                f"mount requires UNMOUNTED, DISCONNECTED, FAILED, or REVALIDATING; found {self._state}",
                "INVALID_REQUEST",
            )
        path = Path(cartridge)
        try:
            observed_uuid = _read_cartridge_uuid(path)
            if observed_uuid != self._cartridge_uuid:
                _lifecycle_reject(
                    self._cartridge_uuid,
                    f"mounted cartridge UUID is {observed_uuid}",
                    "CARTRIDGE_IDENTITY_MISMATCH",
                )
            identity, read_only = _cartridge_snapshot(path, observed_uuid, filesystem_uuid)
            prior_filesystem = self._identity.filesystem_uuid if self._identity is not None else None
            if prior_filesystem is not None and filesystem_uuid != prior_filesystem:
                prior_root = (self._identity.root_generation, self._identity.root_digest)
                replacement_root = (identity.root_generation, identity.root_digest)
                if not replacement or identity.root_digest is None or replacement_root != prior_root:
                    _lifecycle_reject(
                        self._cartridge_uuid,
                        f"filesystem UUID changed from {prior_filesystem} to {filesystem_uuid} "
                        f"with root {replacement_root!r}; expected {prior_root!r}",
                        "CARTRIDGE_IDENTITY_MISMATCH",
                    )
        except CassetteError:
            self._path = None
            self._access = None
            if self._state != "FAILED":
                self._move("FAILED")
            raise
        except OSError as error:
            self._path = None
            self._access = None
            self._move("DISCONNECTED")
            _lifecycle_reject(
                self._cartridge_uuid, f"mounted cartridge is unavailable: {error}",
                "CARTRIDGE_DISCONNECTED",
            )
        self._identity = identity
        self._path = path
        self._move("READ_ONLY" if read_only else "MOUNTED_VERIFIED")
        return identity

    def begin(self, operation_id: str, *, write: bool) -> CartridgeAccess:
        """Start one serialized operation only from a verified mount epoch."""

        if not isinstance(operation_id, str) or _TRANSACTION_ID.fullmatch(operation_id) is None:
            _lifecycle_reject(
                self._cartridge_uuid, "operation_id does not satisfy the durable identifier grammar",
                "INVALID_REQUEST",
            )
        if type(write) is not bool:
            _lifecycle_reject(self._cartridge_uuid, "write must be bool", "INVALID_REQUEST")
        if self._access is not None:
            _lifecycle_reject(
                self._cartridge_uuid, f"operation {self._access.operation_id!r} already owns access",
                "INVALID_REQUEST",
            )
        if self._state == "READ_ONLY" and write:
            _lifecycle_reject(
                self._cartridge_uuid, "mounted cartridge is read-only", "CARTRIDGE_READ_ONLY"
            )
        if self._state not in {"MOUNTED_VERIFIED", "READ_ONLY"} or self._path is None:
            _lifecycle_reject(
                self._cartridge_uuid, f"cartridge state {self._state} has no verified access",
                "CARTRIDGE_DISCONNECTED",
            )
        access = CartridgeAccess(operation_id, self._epoch, write)
        self._access = access
        if self._state == "MOUNTED_VERIFIED":
            self._move("ACTIVE")
        return access

    def resolve(self, access: CartridgeAccess) -> Path:
        """Return the current path only while this exact access remains active and verified."""

        if (not isinstance(access, CartridgeAccess) or access is not self._access
                or access.epoch != self._epoch or self._path is None
                or self._state not in {"ACTIVE", "READ_ONLY"}):
            _lifecycle_reject(
                self._cartridge_uuid, "operation access was invalidated before filesystem use",
                "CARTRIDGE_DISCONNECTED",
            )
        return self._path

    def finish(self, access: CartridgeAccess) -> CartridgeIdentity:
        """Quiesce one operation and refresh the verified root before another operation starts."""

        path = self.resolve(access)
        if self._state == "READ_ONLY":
            self._access = None
            return self._identity
        self._move("QUIESCING")
        try:
            identity, read_only = _cartridge_snapshot(
                path, self._cartridge_uuid, self._identity.filesystem_uuid
            )
        except CassetteError:
            self._access = None
            self._path = None
            self._move("FAILED")
            raise
        except OSError as error:
            self._access = None
            self._path = None
            self._move("DISCONNECTED")
            _lifecycle_reject(
                self._cartridge_uuid, f"cartridge disappeared while quiescing: {error}",
                "CARTRIDGE_DISCONNECTED",
            )
        self._identity = identity
        self._access = None
        self._move("READ_ONLY" if read_only else "MOUNTED_VERIFIED")
        return identity

    def unmount(self) -> None:
        """Invalidate access before an intentional detach from a quiescent verified state."""

        if self._access is not None or self._state not in {
            "MOUNTED_VERIFIED", "READ_ONLY", "FAILED",
        }:
            _lifecycle_reject(
                self._cartridge_uuid, f"unmount requires a quiescent verified state; found {self._state}",
                "INVALID_REQUEST",
            )
        self._invalidate()
        self._move("UNMOUNTED")

    def event(self, event: str) -> None:
        """Invalidate access and enter the exact Q49 state caused by one volume event."""

        target = _CARTRIDGE_EVENTS.get(event)
        if target is None or (event == "wake" and self._state != "SLEEPING"):
            _lifecycle_reject(
                self._cartridge_uuid, f"event {event!r} is undefined from {self._state}",
                "INVALID_REQUEST",
            )
        if self._state == target:
            return
        if target not in _CARTRIDGE_TRANSITIONS[self._state]:
            _lifecycle_reject(
                self._cartridge_uuid, f"event {event!r} is undefined from {self._state}",
                "INVALID_REQUEST",
            )
        self._invalidate()
        self._move(target)


def _lifecycle_reject(cartridge_uuid: str, detail: str, code: str) -> None:
    retryable = code in {
        "CARTRIDGE_DISCONNECTED", "CARTRIDGE_READ_ONLY", "CARTRIDGE_IDENTITY_MISMATCH",
    }
    raise CassetteError(
        code=code,
        object_id=f"cartridge:{cartridge_uuid}",
        failed_invariant="Q49: removable-volume identity and verified mount epoch",
        retryability="retryable" if retryable else "terminal",
        detail=detail,
    )


def _normalize_uuid(value: object, field: str) -> str:
    object_id = value if isinstance(value, str) and value else "unidentified"
    if not isinstance(value, str) or not value or value != value.strip():
        _lifecycle_reject(str(object_id), f"{field} must be exact nonempty UUID text", "INVALID_REQUEST")
    try:
        return str(uuid.UUID(value))
    except (ValueError, AttributeError):
        _lifecycle_reject(str(object_id), f"{field} is not a UUID", "INVALID_REQUEST")


def _capacity_reject(operation_id: str, detail: str, code: str = "CAPACITY_EXCEEDED") -> None:
    raise CassetteError(
        code=code,
        object_id=f"operation:{operation_id}",
        failed_invariant="Q53: exact extent reservation before transfer or mutation",
        retryability="terminal",
        detail=detail,
    )


def _capacity_value(field: str, value: object, operation_id: str) -> int:
    if type(value) is not int or not 0 <= value <= _MAX_UNSIGNED_BYTES:
        _capacity_reject(
            operation_id, f"{field} must be an unsigned 64-bit byte count", "INVALID_REQUEST"
        )
    return value


def _capacity_sum(values, operation_id: str) -> int:
    total = 0
    for value in values:
        value = _capacity_value("phase byte field", value, operation_id)
        if value > _MAX_UNSIGNED_BYTES - total:
            _capacity_reject(operation_id, "capacity arithmetic exceeds unsigned 64-bit bytes")
        total += value
    return total


def capacity_requirement(
    operation_id: str,
    *,
    device_bytes: int,
    phases: tuple[CapacityPhase, ...],
) -> CapacityRequirement:
    """Compute Q53 once for preflight and the later physical reservation."""

    if not isinstance(operation_id, str) or _TRANSACTION_ID.fullmatch(operation_id) is None:
        _capacity_reject(
            "unidentified", "operation_id must satisfy the durable identifier grammar", "INVALID_REQUEST"
        )
    device_bytes = _capacity_value("device_bytes", device_bytes, operation_id)
    if (not isinstance(phases, tuple) or not phases
            or any(not isinstance(phase, CapacityPhase) for phase in phases)):
        _capacity_reject(operation_id, "one or more CapacityPhase values are required", "INVALID_REQUEST")
    totals = tuple(phase.total for phase in phases)
    five_percent = device_bytes // 20 + bool(device_bytes % 20)
    safety = max(8 * 1024**3, five_percent)
    return CapacityRequirement(
        device_bytes,
        safety,
        totals,
        max(phase.repair for phase in phases),
        _capacity_sum((max(totals), safety), operation_id),
    )


def reserve_capacity(
    operation_id: str,
    *,
    device_bytes: int,
    allocatable_verified_free: int,
    phases: tuple[CapacityPhase, ...],
    reserve_extent: Callable[[int], bool],
    release_extent: Callable[[int], bool],
) -> CapacityReservation:
    """Admit Q53 only after one atomic preallocator reserves the exact phase maximum plus safety."""

    requirement = capacity_requirement(
        operation_id, device_bytes=device_bytes, phases=phases
    )
    free = _capacity_value("allocatable_verified_free", allocatable_verified_free, operation_id)
    if free > requirement.device_bytes:
        _capacity_reject(
            operation_id, "allocatable verified free bytes exceed device bytes", "INVALID_REQUEST"
        )
    if not callable(reserve_extent) or not callable(release_extent):
        _capacity_reject(
            operation_id,
            "reserve_extent and release_extent must be callable",
            "INVALID_REQUEST",
        )
    if free < requirement.required_bytes:
        _capacity_reject(
            operation_id,
            f"required {requirement.required_bytes} bytes; verified allocatable free is {free}",
        )
    try:
        reserved = reserve_extent(requirement.required_bytes)
    except OSError as error:
        _capacity_reject(
            operation_id,
            f"preallocate failed for {requirement.required_bytes} bytes: {error}",
        )
    if reserved is not True:
        _capacity_reject(
            operation_id,
            f"preallocate refused one exact {requirement.required_bytes}-byte extent despite {free} reported free bytes",
        )
    return CapacityReservation(
        operation_id,
        requirement.device_bytes,
        requirement.safety_bytes,
        requirement.phase_totals,
        requirement.repair_bytes,
        requirement.required_bytes,
        release_extent,
    )


def _active_reservation(
    reservation: CapacityReservation, operation_id: str
) -> CapacityReservation:
    if not isinstance(reservation, CapacityReservation) or not reservation.active:
        _capacity_reject(
            operation_id,
            "an active completed CapacityReservation is required",
            "INVALID_REQUEST",
        )
    return reservation


def release_capacity(reservation: CapacityReservation) -> None:
    """Release one Q53 extent exactly once during terminal operation cleanup."""

    if not isinstance(reservation, CapacityReservation):
        _capacity_reject(
            "release", "a completed CapacityReservation is required", "INVALID_REQUEST"
        )
    if not reservation.active:
        return
    try:
        released = reservation._release_extent(reservation.required_bytes)
    except OSError as error:
        _capacity_reject(
            reservation.operation_id,
            f"release failed for {reservation.required_bytes} bytes: {error}",
        )
    if released is not True:
        _capacity_reject(
            reservation.operation_id,
            f"release refused the owned {reservation.required_bytes}-byte extent",
        )
    object.__setattr__(reservation, "active", False)


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


_RESUMABLE_SHA256_STATE = struct.Struct("@64sIQ8I")


def artifact_hasher(expected_digest: str, object_id: str):
    """Return the sole whole-artifact hasher for Q1/Q51/Q57 byte verification."""

    algorithm = expected_digest.partition(":")[0]
    if algorithm == "blake3":
        return blake3()
    if algorithm == "sha256":
        return hashlib.sha256()
    _reject(
        "artifacts[].digest",
        "artifact byte verification requires a BLAKE3 or SHA-256 digest",
        object_id,
    )


def resumable_artifact_hasher(expected_digest: str, object_id: str):
    """Return Q51's pinned SHA-256 hasher whose continuation state is durable."""

    if expected_digest.partition(":")[0] != "sha256":
        _reject(
            "artifacts[].digest",
            "resumable transfer requires an authoritative SHA-256 artifact digest",
            object_id,
        )
    return resumablesha256.sha256()


def artifact_hash_state(hasher, expected_digest: str, offset: int, object_id: str) -> str:
    """Serialize and structurally verify one SHA-256 continuation at an exact byte offset."""

    try:
        payload = hasher.__getstate__()
    except (AttributeError, TypeError, ValueError) as error:
        _reject("serialized_hash_state", f"hasher state is unavailable: {error}", object_id)
    _validate_artifact_hash_state(payload, expected_digest, offset, object_id)
    return "sha256-state-v1:" + payload.hex()


def resume_artifact_hasher(state: str, expected_digest: str, offset: int, object_id: str):
    """Restore one validated Q51 SHA-256 continuation without evaluating serialized code."""

    if not isinstance(state, str) or not state.startswith("sha256-state-v1:"):
        _reject("serialized_hash_state", "a sha256-state-v1 value is required", object_id)
    encoded = state[16:]
    if len(encoded) != 2 * _RESUMABLE_SHA256_STATE.size or not set(encoded) <= _HEX:
        _reject("serialized_hash_state", "state payload is not lowercase hexadecimal", object_id)
    payload = bytes.fromhex(encoded)
    _validate_artifact_hash_state(payload, expected_digest, offset, object_id)
    hasher = resumable_artifact_hasher(expected_digest, object_id)
    try:
        hasher.__setstate__(payload)
    except (TypeError, ValueError) as error:
        _reject("serialized_hash_state", f"state restoration failed: {error}", object_id)
    return hasher


def _validate_artifact_hash_state(
    payload: object, expected_digest: str, offset: int, object_id: str
) -> None:
    if (not isinstance(payload, bytes) or len(payload) != _RESUMABLE_SHA256_STATE.size
            or type(offset) is not int or offset < 0):
        _reject("serialized_hash_state", "state size and byte offset must be exact", object_id)
    if expected_digest.partition(":")[0] != "sha256":
        _reject("artifacts[].digest", "serialized state requires SHA-256", object_id)
    _, buffered, processed_bits, *_ = _RESUMABLE_SHA256_STATE.unpack(payload)
    if buffered != offset % 64 or processed_bits != (offset - buffered) * 8:
        _reject("serialized_hash_state", "state counters do not match the contiguous byte offset", object_id)


def _safetensors_header(
    handle, object_id: str, artifact_hasher
) -> tuple[int, int, dict, tuple[tuple, ...]]:
    prefix = _read_exact(handle, 8, object_id, "SafeTensors header length")
    artifact_hasher.update(prefix)
    header_length = int.from_bytes(prefix, "little")
    file_size = os.fstat(handle.fileno()).st_size
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
    if (not isinstance(metadata, dict) or len(metadata) > 1024
            or any(not isinstance(key, str) or not isinstance(value, str)
                   or not 0 < len(key) <= 256 or len(value) > 4096
                   or any(ord(character) < 32 or ord(character) == 127 for character in key)
                   for key, value in metadata.items())):
        _q57_reject(object_id, "SafeTensors metadata exceeds its bounded string map")

    data_size = file_size - 8 - header_length
    tensors = []
    for name, spec in header.items():
        if (not isinstance(name, str) or not 0 < len(name) <= 4096
                or any(ord(character) < 32 or ord(character) == 127 for character in name)
                or not isinstance(spec, dict)
                or set(spec) != {"dtype", "shape", "data_offsets"}):
            _q57_reject(object_id, f"tensor {name!r} lacks the exact SafeTensors fields")
        dtype, shape, offsets = spec["dtype"], spec["shape"], spec["data_offsets"]
        if dtype not in _SAFETENSORS_DTYPE_BITS:
            _q57_reject(object_id, f"tensor {name!r} has an unknown SafeTensors dtype")
        if (not isinstance(shape, list) or len(shape) > 64
                or any(type(dimension) is not int or not 0 <= dimension <= _MAX_UNSIGNED_BYTES
                       for dimension in shape)):
            _q57_reject(object_id, f"tensor {name!r} has an invalid shape")
        if (not isinstance(offsets, list) or len(offsets) != 2
                or any(type(offset) is not int for offset in offsets)):
            _q57_reject(object_id, f"tensor {name!r} has invalid data offsets")
        start, end = offsets
        if not 0 <= start <= end <= data_size:
            _q57_reject(object_id, f"tensor {name!r} points outside the SafeTensors byte buffer")
        elements = 1
        for dimension in shape:
            if dimension > _MAX_UNSIGNED_BYTES // max(elements, 1):
                _q57_reject(object_id, f"tensor {name!r} element count overflows")
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


def _gguf_header(
    handle, object_id: str, artifact_hasher
) -> tuple[int, int, dict, tuple[tuple, ...]]:
    """Parse one bounded GGUF v2/v3 header and return exact tensor byte intervals."""

    file_size = os.fstat(handle.fileno()).st_size
    header_start = handle.tell()

    def take(length: int, description: str) -> bytes:
        if length < 0 or handle.tell() - header_start + length > _GGUF_HEADER_BYTES:
            _q57_reject(object_id, "GGUF header exceeds its 100 MB allocation bound")
        payload = _read_exact(handle, length, object_id, description)
        artifact_hasher.update(payload)
        return payload

    def scalar(format_code: str, description: str):
        return struct.unpack(format_code, take(struct.calcsize(format_code), description))[0]

    def string(
        description: str, *, empty: bool = False, allow_controls: bool = False
    ) -> str:
        length = scalar("<Q", f"{description} length")
        if length > _GGUF_HEADER_BYTES:
            _q57_reject(object_id, f"{description} exceeds the GGUF header bound")
        try:
            value = take(length, description).decode("utf-8")
        except UnicodeDecodeError as error:
            _q57_reject(object_id, f"{description} is not UTF-8: {error}")
        if (not value and not empty) or (not allow_controls and any(
            ord(character) < 32 or ord(character) == 127 for character in value
        )):
            _q57_reject(object_id, f"{description} contains empty or control-bearing text")
        return value

    def metadata_value(value_type: int, description: str, *, array_item: bool = False):
        if value_type in _GGUF_SCALARS:
            value = scalar(_GGUF_SCALARS[value_type], description)
            if isinstance(value, float) and not math.isfinite(value):
                _q57_reject(object_id, f"{description} is not finite")
            return value
        if value_type == 8:
            return string(description, empty=True, allow_controls=True)
        if value_type == 9 and not array_item:
            item_type = scalar("<I", f"{description} array type")
            count = scalar("<Q", f"{description} array count")
            if count > _GGUF_MAX_ITEMS or item_type == 9:
                _q57_reject(object_id, f"{description} has an unsupported or unbounded array")
            return [
                metadata_value(item_type, f"{description}[{index}]", array_item=True)
                for index in range(count)
            ]
        _q57_reject(object_id, f"{description} has unknown GGUF metadata type {value_type}")

    if take(4, "GGUF magic") != b"GGUF":
        _q57_reject(object_id, "GGUF magic is absent")
    version = scalar("<I", "GGUF version")
    if version not in {2, 3}:
        _q57_reject(object_id, f"GGUF version {version} is unsupported")
    tensor_count = scalar("<Q", "GGUF tensor count")
    metadata_count = scalar("<Q", "GGUF metadata count")
    if not 0 < tensor_count <= _GGUF_MAX_ITEMS or metadata_count > _GGUF_MAX_ITEMS:
        _q57_reject(object_id, "GGUF tensor or metadata count exceeds its bound")

    metadata = {}
    for index in range(metadata_count):
        key = string(f"GGUF metadata key {index}")
        if key in metadata:
            _q57_reject(object_id, f"GGUF metadata key {key!r} is duplicated")
        value_type = scalar("<I", f"GGUF metadata {key!r} type")
        metadata[key] = metadata_value(value_type, f"GGUF metadata {key!r}")

    tensor_rows = []
    names = set()
    for index in range(tensor_count):
        name = string(f"GGUF tensor name {index}")
        if name in names:
            _q57_reject(object_id, f"GGUF tensor name {name!r} is duplicated")
        names.add(name)
        dimensions = scalar("<I", f"GGUF tensor {name!r} rank")
        if dimensions > 64:
            _q57_reject(object_id, f"GGUF tensor {name!r} exceeds the rank bound")
        shape = tuple(
            scalar("<Q", f"GGUF tensor {name!r} dimension {dimension}")
            for dimension in range(dimensions)
        )
        tensor_type = scalar("<I", f"GGUF tensor {name!r} type")
        if tensor_type not in _GGUF_TENSOR_TYPES:
            _q57_reject(object_id, f"GGUF tensor {name!r} uses unsupported type {tensor_type}")
        offset = scalar("<Q", f"GGUF tensor {name!r} offset")
        dtype, block_elements, block_bytes = _GGUF_TENSOR_TYPES[tensor_type]
        elements = 1
        for dimension in shape:
            if dimension > _MAX_UNSIGNED_BYTES // max(elements, 1):
                _q57_reject(object_id, f"GGUF tensor {name!r} element count overflows")
            elements *= dimension
        if elements and (not shape or shape[0] % block_elements or elements % block_elements):
            _q57_reject(object_id, f"GGUF tensor {name!r} shape does not align to its block type")
        length = elements // block_elements * block_bytes if elements else 0
        tensor_rows.append((name, dtype, shape, offset, offset + length))

    alignment = metadata.get("general.alignment", 32)
    if (
        type(alignment) is not int
        or not 1 <= alignment <= PAGE_BYTES
        or alignment & (alignment - 1)
    ):
        _q57_reject(object_id, "GGUF general.alignment must be a power of two within one page")
    padding = (-handle.tell()) % alignment
    if padding and any(take(padding, "GGUF data alignment padding")):
        _q57_reject(object_id, "GGUF data alignment padding must be zero")
    data_start = handle.tell()
    data_size = file_size - data_start
    if data_size < 0:
        _q57_reject(object_id, "GGUF header extends beyond the source file")

    cursor = 0
    for name, _, _, start, end in sorted(tensor_rows, key=lambda row: (row[3], row[4], row[0])):
        if start % alignment or not 0 <= start <= end <= data_size or start < cursor:
            _q57_reject(object_id, f"GGUF tensor {name!r} has an overlapping, unaligned, or external range")
        cursor = end
    summary = {
        "alignment": str(alignment),
        "metadata_digest": digest_bytes(canonical_bytes(metadata)),
        "version": str(version),
    }
    return data_start, data_size, summary, tuple(sorted(tensor_rows))


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


def _clone_extent(source_fd: int, destination: Path, object_id: str) -> None:
    """Create one APFS copy-on-write inode; failure forbids a full-copy fallback under Q4."""

    if _FCLONEFILEAT is None:
        _q57_reject(
            object_id,
            "copy-on-write extent adoption requires the macOS fclonefileat primitive",
            "DURABILITY_UNSUPPORTED",
        )
    directory_fd = None
    try:
        directory_fd = os.open(destination.parent, os.O_RDONLY)
        result = _FCLONEFILEAT(source_fd, directory_fd, os.fsencode(destination.name), 0)
    except OSError as error:
        _q57_reject(
            object_id,
            f"copy-on-write extent adoption failed before clone completion: {error}",
            "DURABILITY_UNSUPPORTED",
        )
    finally:
        if directory_fd is not None:
            os.close(directory_fd)
    if result != 0:
        error = OSError(ctypes.get_errno(), os.strerror(ctypes.get_errno()))
        _q57_reject(
            object_id,
            f"copy-on-write extent adoption is unavailable and a full parameter copy is forbidden: {error}",
            "DURABILITY_UNSUPPORTED",
        )


def stage_conversion_extent(
    source_fd: int,
    cartridge: str | Path,
    target_size: int,
    target_digest: str,
    object_id: str,
    growth_chunks=(),
) -> Path:
    """Resume one COW identity, shrink, or page-bounded grow transform into immutable storage."""

    if (
        type(source_fd) is not int
        or type(target_size) is not int
        or not 0 < target_size <= SEGMENT_BYTES
        or not isinstance(target_digest, str)
        or not isinstance(object_id, str)
        or not object_id
    ):
        _q57_reject(str(object_id), "conversion extent arguments are malformed", "INVALID_REQUEST")
    target_name = _content_hex(target_digest, object_id)
    try:
        source_stat = os.fstat(source_fd)
    except OSError as error:
        _q57_reject(object_id, f"conversion source descriptor is unavailable: {error}", "SOURCE_UNAVAILABLE")
    if not stat.S_ISREG(source_stat.st_mode):
        _q57_reject(object_id, "conversion source descriptor is not a regular file", "INVALID_REQUEST")
    source_size = source_stat.st_size
    directory = Path(cartridge) / "segments"
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / target_name
    pending = destination.with_name(f".{target_name}.pending")

    def exact(path: Path) -> bool:
        try:
            return path.stat().st_size == target_size and _file_digest(path) == target_digest
        except OSError:
            return False

    if destination.exists():
        if not exact(destination):
            _q57_reject(target_digest, "existing conversion segment is corrupt", "PAGE_CORRUPT")
        try:
            destination.chmod(0o400)
        except OSError as error:
            _q57_reject(
                target_digest,
                f"existing conversion segment cannot be made read-only: {error}",
                "DURABILITY_UNSUPPORTED",
            )
        return destination
    if pending.exists() and exact(pending):
        _fullsync_file(pending, object_id)
        try:
            pending.chmod(0o400)
            os.replace(pending, destination)
        except OSError as error:
            _q57_reject(object_id, f"resumed conversion extent cannot commit: {error}", "DURABILITY_UNSUPPORTED")
        _sync_directory(directory, object_id)
        return destination
    try:
        pending.unlink(missing_ok=True)
        _clone_extent(source_fd, pending, object_id)
        pending.chmod(0o600)
        empty = object()
        if target_size < source_size:
            try:
                if next(iter(growth_chunks), empty) is not empty:
                    _q57_reject(object_id, "identity and shrink transforms cannot carry growth chunks")
            except TypeError:
                _q57_reject(object_id, "growth chunks must be iterable", "INVALID_REQUEST")
            os.truncate(pending, target_size)
        elif target_size > source_size:
            cursor = source_size
            try:
                chunks = iter(growth_chunks)
            except TypeError:
                _q57_reject(object_id, "growth chunks must be iterable", "INVALID_REQUEST")
            with pending.open("r+b", buffering=0) as handle:
                for chunk in chunks:
                    if not isinstance(chunk, bytes) or not 0 < len(chunk) <= PAGE_BYTES:
                        _q57_reject(
                            object_id,
                            "growth chunks must be nonempty bytes bounded by one canonical page",
                            "INVALID_REQUEST",
                        )
                    if cursor + len(chunk) > target_size:
                        _q57_reject(object_id, "growth chunks exceed the declared target extent")
                    handle.seek(cursor)
                    handle.write(chunk)
                    cursor += len(chunk)
            if cursor != target_size:
                _q57_reject(object_id, "growth chunks do not fill the declared target extent")
        else:
            try:
                if next(iter(growth_chunks), empty) is not empty:
                    _q57_reject(object_id, "identity and shrink transforms cannot carry growth chunks")
            except TypeError:
                _q57_reject(object_id, "growth chunks must be iterable", "INVALID_REQUEST")
        if not exact(pending):
            _q57_reject(
                object_id,
                "conversion readback differs from the declared target digest",
                "SOURCE_REVISION_CHANGED",
            )
        _fullsync_file(pending, object_id)
        pending.chmod(0o400)
        os.replace(pending, destination)
        _sync_directory(directory, object_id)
    except CassetteError:
        raise
    except OSError as error:
        _q57_reject(object_id, f"conversion extent cannot commit: {error}", "DURABILITY_UNSUPPORTED")
    return destination


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


def _write_index(
    cartridge: Path,
    root_digest: str,
    locations: tuple[PageLocation, ...],
    *,
    durable: bool = False,
) -> None:
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
    if durable:
        _durable_replace(path, payload, f"index:{root_digest}")
    else:
        path.write_bytes(payload)


def _decode_index(payload: bytes, root_digest: str) -> dict[str, PageLocation]:
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


def _read_index(cartridge: Path, root_digest: str) -> dict[str, PageLocation]:
    path = _index_path(cartridge, root_digest)
    try:
        payload = path.read_bytes()
    except OSError as error:
        _q57_reject(root_digest, f"physical page index is unavailable: {error}")
    return _decode_index(payload, root_digest)


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
                   or item["format"] not in {"gguf", "safetensors"}
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


def _root_page_digests(root: dict) -> set[str]:
    """Return every base-tensor and ordered-delta page governed by one logical root."""
    return {
        span["page_digest"]
        for tensor_map in root["tensor_maps"]
        for span in tensor_map["spans"]
    } | {
        page_digest
        for delta in root["deltas"]
        for page_digest in delta["ordered_page_digests"]
    }


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
    delta_ids = []
    for delta in root["deltas"]:
        body = {name: delta[name] for name in delta if name != "delta_id"}
        if delta["delta_id"] != digest_bytes(canonical_bytes(body)):
            _q57_reject(root_digest, "training delta identity does not match its ordered record")
        delta_ids.append(delta["delta_id"])
    if len(delta_ids) != len(set(delta_ids)):
        _q57_reject(root_digest, "root contains duplicate training delta identities")
    if material.revision_kind == "tuned" and root["deltas"] and (
        len(root["parents"]) != 1
        or root["deltas"][-1]["base_identity"] != root["parents"][0]
        or record["transform_manifest_digest"]
        != digest_bytes(canonical_bytes(root["deltas"]))
    ):
        _q57_reject(
            root_digest,
            "tuned root does not bind its immediate parent and complete ordered delta record",
        )
    required = _root_page_digests(root)
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


def inspect_safetensors(source: str | Path | int, expected_digest: str) -> dict:
    """Parse one bounded SafeTensors header without loading or executing repository material."""

    descriptor = None
    original_offset = None
    if type(source) is int:
        object_id = f"source:descriptor:{source}"
        try:
            source_stat = os.fstat(source)
            if not stat.S_ISREG(source_stat.st_mode):
                _q57_reject(object_id, "SafeTensors inspection requires one regular-file descriptor")
            original_offset = os.lseek(source, 0, os.SEEK_CUR)
            descriptor = os.dup(source)
            os.lseek(descriptor, 0, os.SEEK_SET)
            handle = os.fdopen(descriptor, "rb", closefd=True)
            descriptor = None
        except OSError as error:
            _q57_reject(object_id, f"SafeTensors descriptor is unavailable: {error}", "SOURCE_UNAVAILABLE")
    else:
        try:
            path = Path(source)
        except TypeError:
            _q57_reject("source:unidentified", "SafeTensors inspection requires one local path or descriptor")
        object_id = f"source:{path.name}"
        try:
            handle = path.open("rb")
        except OSError as error:
            _q57_reject(object_id, f"SafeTensors source is unavailable: {error}", "SOURCE_UNAVAILABLE")
    hasher = artifact_hasher(expected_digest, object_id)
    try:
        with handle:
            data_start, data_size, metadata, tensors = _safetensors_header(
                handle, object_id, hasher
            )
    except OSError as error:
        _q57_reject(object_id, f"SafeTensors source is unavailable: {error}", "SOURCE_UNAVAILABLE")
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if original_offset is not None:
            try:
                os.lseek(source, original_offset, os.SEEK_SET)
            except OSError:
                pass
    return {
        "data_start": data_start,
        "data_size": data_size,
        "metadata": metadata,
        "tensors": [
            {
                "semantic_tensor_id": name,
                "dtype": dtype,
                "shape": list(shape),
                "offset": start,
                "length": end - start,
            }
            for name, dtype, shape, start, end in tensors
        ],
    }


def _write_cartridge_root(
    cartridge: Path,
    material: IdentityTuple,
    identity_record: dict,
    containers: list[dict],
    tensor_maps: list[dict],
    locations: tuple[PageLocation, ...],
    plans: list[dict] | None = None,
    deltas: list[dict] | None = None,
    *,
    durable: bool = False,
) -> str:
    root = {
        "identity": model_identity(material),
        "parents": identity_record["parent_ids"],
        "provenance": {
            "revision_kind": material.revision_kind,
            "source_alias": material.source_alias,
            "requested_revision": material.requested_revision,
            "identity_material": identity_record,
            "containers": containers,
        },
        "semantic_assets": {
            "processor": identity_record["processor_digest"],
            "template": identity_record["template_digest"],
            "tokenizer": identity_record["tokenizer_digest"],
        },
        "tensor_maps": tensor_maps,
        "operators": identity_record["operator_set"],
        "plans": [] if plans is None else plans,
        "deltas": [] if deltas is None else deltas,
    }
    root["integrity_root"] = _root_integrity(
        root, tuple(sorted(locations, key=lambda item: item.page_digest))
    )
    payload = canonical_bytes(root)
    root_digest = digest_bytes(payload)
    _write_index(cartridge, root_digest, locations, durable=durable)
    path = cartridge / "roots" / _content_hex(root_digest, root_digest)
    path.parent.mkdir(parents=True, exist_ok=True)
    if durable:
        if not path.exists() or path.read_bytes() != payload:
            _durable_replace(path, payload, f"root:{root_digest}")
        else:
            path.with_name(f".{path.name}.pending").unlink(missing_ok=True)
    elif path.exists():
        if path.read_bytes() != payload:
            _q57_reject(root_digest, "existing root bytes do not match their name")
    else:
        path.write_bytes(payload)
    load_root(cartridge, root_digest)
    return root_digest


def _import_tensor_containers(
    source: Mapping[str, str | Path],
    cartridge: str | Path,
    material: IdentityTuple,
    *,
    container_format: str,
    parser,
    codec: str,
) -> str:
    """Import one bounded tensor-container family through the single Q57 page authority."""
    identity_record = _identity_record(material)
    identity = digest_bytes(canonical_bytes(identity_record))
    expected_artifacts = {item["path"]: item for item in identity_record["artifacts"]}
    if not isinstance(source, Mapping) or not source:
        _q57_reject(identity, f"canonical artifact paths must map to local {container_format} files")
    sources = []
    for artifact_path, local_path in source.items():
        if not isinstance(artifact_path, str) or not artifact_path or artifact_path != artifact_path.strip():
            _q57_reject(identity, f"every {container_format} source requires one canonical artifact path")
        try:
            sources.append((artifact_path, Path(local_path)))
        except TypeError:
            _q57_reject(identity, f"artifact {artifact_path!r} has no local filesystem path")
    sources = tuple(sorted(sources))
    if {artifact_path for artifact_path, _ in sources} != set(expected_artifacts):
        _reject(
            "artifacts",
            f"{container_format} source paths differ from the complete Q1 artifact set",
            identity,
        )
    cartridge = Path(cartridge)
    artifacts = []
    tensor_names = set()
    for artifact_path, path in sources:
        object_id = f"source:{artifact_path}"
        expected_digest = expected_artifacts[artifact_path]["digest"]
        source_hasher = artifact_hasher(expected_digest, object_id)
        try:
            with path.open("rb") as handle:
                data_start, data_size, metadata, tensors = parser(handle, object_id, source_hasher)
        except OSError as error:
            _q57_reject(
                object_id,
                f"{container_format} source is unavailable: {error}",
                "SOURCE_UNAVAILABLE",
            )
        names = {tensor[0] for tensor in tensors}
        if tensor_names & names:
            _q57_reject(object_id, f"{container_format} artifacts contain duplicate tensor names")
        tensor_names |= names
        artifacts.append((
            artifact_path, path, data_start, data_size, metadata, tensors,
            expected_digest.partition(":")[0], source_hasher,
        ))

    seen_pages = set()
    tensor_maps = []

    def unique_pages():
        for artifact_path, path, data_start, data_size, _, tensors, _, source_hasher in artifacts:
            object_id = f"source:{artifact_path}"
            try:
                handle = path.open("rb")
            except OSError as error:
                _q57_reject(
                    object_id,
                    f"{container_format} source is unavailable: {error}",
                    "SOURCE_UNAVAILABLE",
                )
            with handle:
                handle.seek(data_start)
                remaining = data_size
                page_digests = []
                while remaining:
                    payload = _read_exact(
                        handle,
                        min(PAGE_BYTES, remaining),
                        object_id,
                        f"{container_format} payload",
                    )
                    remaining -= len(payload)
                    source_hasher.update(payload)
                    page_digest = digest_bytes(payload)
                    page_digests.append(page_digest)
                    if page_digest not in seen_pages:
                        seen_pages.add(page_digest)
                        yield page_digest, payload
                for tensor_map in _tensor_maps(tensors, page_digests):
                    record = tensor_map.record()
                    record["codec"] = codec
                    tensor_maps.append(record)

    locations = _write_segments(cartridge, unique_pages())
    observed_artifacts = [
        {
            "path": artifact_path,
            "size": data_start + data_size,
            "digest": f"{algorithm}:{source_hasher.hexdigest()}",
        }
        for artifact_path, _, data_start, data_size, _, _, algorithm, source_hasher in artifacts
    ]
    if observed_artifacts != identity_record["artifacts"]:
        _reject(
            "artifacts",
            f"{container_format} path, size, or digest differs from the supplied Q1 evidence",
            identity,
        )
    return _write_cartridge_root(
        cartridge,
        material,
        identity_record,
        [
            {"path": artifact_path, "format": container_format, "metadata": metadata}
            for artifact_path, _, _, _, metadata, _, _, _ in artifacts
        ],
        sorted(tensor_maps, key=lambda tensor_map: tensor_map["semantic_tensor_id"]),
        locations,
    )


def import_safetensors(
    source: Mapping[str, str | Path], cartridge: str | Path, material: IdentityTuple
) -> str:
    """Import SafeTensors only when their bytes prove the supplied complete Q1 material."""

    return _import_tensor_containers(
        source,
        cartridge,
        material,
        container_format="safetensors",
        parser=_safetensors_header,
        codec="raw-little-endian",
    )


def import_gguf(
    source: Mapping[str, str | Path], cartridge: str | Path, material: IdentityTuple
) -> str:
    """Import GGUF v2/v3 only when bounded metadata and every tensor range prove Q1."""

    return _import_tensor_containers(
        source,
        cartridge,
        material,
        container_format="gguf",
        parser=_gguf_header,
        codec="gguf-block",
    )


def adopt_safetensors(
    source: Mapping[str, int], cartridge: str | Path, material: IdentityTuple
) -> str:
    """Adopt verified SafeTensors extents as immutable pages without a second parameter copy."""

    identity_record = _identity_record(material)
    identity = model_identity(material)
    expected = {item["path"]: item for item in identity_record["artifacts"]}
    if not isinstance(source, Mapping) or set(source) != set(expected):
        _q57_reject(identity, "adoption requires every canonical SafeTensors artifact exactly once")
    cartridge = Path(cartridge)
    segment_directory = cartridge / "segments"
    segment_directory.mkdir(parents=True, exist_ok=True)
    tensor_names = set()
    tensor_maps = []
    containers = []
    locations = {}
    observed = []

    class ContainerHasher:
        def __init__(self, expected_digest: str, object_id: str):
            self.source = artifact_hasher(expected_digest, object_id)
            self.segment = blake3()
            self.buffer = bytearray()
            self.pages = []
            self.offset = 0

        def update(self, payload: bytes) -> None:
            self.source.update(payload)
            self.segment.update(payload)
            self.buffer.extend(payload)
            while len(self.buffer) >= PAGE_BYTES:
                page = bytes(self.buffer[:PAGE_BYTES])
                del self.buffer[:PAGE_BYTES]
                self.pages.append((digest_bytes(page), self.offset, len(page)))
                self.offset += len(page)

        def finish(self) -> tuple[tuple[str, int, int], ...]:
            if self.buffer:
                page = bytes(self.buffer)
                self.pages.append((digest_bytes(page), self.offset, len(page)))
                self.offset += len(page)
                self.buffer.clear()
            return tuple(self.pages)

    for artifact_path, descriptor in sorted(source.items()):
        if not isinstance(artifact_path, str) or type(descriptor) is not int:
            _q57_reject(identity, "adopted artifacts require canonical paths and open descriptors")
        object_id = f"source:{artifact_path}"
        expected_digest = expected[artifact_path]["digest"]
        hashes = ContainerHasher(expected_digest, object_id)
        original_offset = None
        duplicate = None
        try:
            descriptor_stat = os.fstat(descriptor)
            size = descriptor_stat.st_size
            if not stat.S_ISREG(descriptor_stat.st_mode):
                _q57_reject(object_id, "adopted source descriptor is not a regular file")
            if size > SEGMENT_BYTES:
                _q57_reject(
                    object_id,
                    "zero-copy adoption requires each first-release SafeTensors shard to fit one 1 GiB segment",
                    "MODEL_UNSUPPORTED",
                )
            original_offset = os.lseek(descriptor, 0, os.SEEK_CUR)
            duplicate = os.dup(descriptor)
            os.lseek(duplicate, 0, os.SEEK_SET)
            with os.fdopen(duplicate, "rb", closefd=True) as handle:
                duplicate = None
                data_start, data_size, metadata, tensors = _safetensors_header(
                    handle, object_id, hashes
                )
                remaining = data_size
                while remaining:
                    payload = _read_exact(
                        handle, min(PAGE_BYTES, remaining), object_id, "SafeTensors payload"
                    )
                    hashes.update(payload)
                    remaining -= len(payload)
        except OSError as error:
            _q57_reject(object_id, f"SafeTensors source is unavailable: {error}", "SOURCE_UNAVAILABLE")
        finally:
            if duplicate is not None:
                os.close(duplicate)
            if original_offset is not None:
                try:
                    os.lseek(descriptor, original_offset, os.SEEK_SET)
                except OSError:
                    pass
        page_rows = hashes.finish()
        source_digest = f"{expected_digest.partition(':')[0]}:{hashes.source.hexdigest()}"
        observed.append({"path": artifact_path, "size": size, "digest": source_digest})
        if observed[-1] != expected[artifact_path]:
            _reject(
                "artifacts",
                "adopted SafeTensors bytes differ from the supplied Q1 evidence",
                identity,
            )
        names = {tensor[0] for tensor in tensors}
        if tensor_names & names:
            _q57_reject(object_id, "SafeTensors artifacts contain duplicate tensor names")
        tensor_names |= names
        segment_id = f"blake3:{hashes.segment.hexdigest()}"
        stage_conversion_extent(
            descriptor,
            cartridge,
            size,
            segment_id,
            object_id,
        )
        page_digests = [page_digest for page_digest, _, _ in page_rows]
        for page_digest, offset, length in page_rows:
            locations.setdefault(
                page_digest, PageLocation(page_digest, segment_id, offset, length)
            )
        for name, dtype, shape, start, end in tensors:
            spans = []
            cursor = data_start + start
            absolute_end = data_start + end
            while cursor < absolute_end:
                page_number, page_offset = divmod(cursor, PAGE_BYTES)
                length = min(absolute_end - cursor, page_rows[page_number][2] - page_offset)
                spans.append(TensorSpan(
                    page_digests[page_number], page_offset, length, cursor - data_start - start
                ))
                cursor += length
            tensor_maps.append(TensorMap(name, shape, dtype, tuple(spans)).record())
        containers.append({
            "path": artifact_path,
            "format": "safetensors",
            "metadata": metadata,
        })
    if observed != identity_record["artifacts"]:
        _reject("artifacts", "adopted artifact order differs from Q1 evidence", identity)
    return _write_cartridge_root(
        cartridge,
        material,
        identity_record,
        containers,
        sorted(tensor_maps, key=lambda item: item["semantic_tensor_id"]),
        tuple(sorted(locations.values(), key=lambda item: item.page_digest)),
        durable=True,
    )


def derive_root(
    cartridge: str | Path,
    parent_root_digest: str,
    material: IdentityTuple,
    plans: tuple[dict, ...],
) -> str:
    """Publish one child revision or same-identity plan manifest over verified existing pages."""

    cartridge = Path(cartridge)
    parent = load_root(cartridge, parent_root_digest)
    identity_record = _identity_record(material)
    same_identity_plan = (
        material.revision_kind == parent["provenance"]["revision_kind"]
        and material.source_alias == parent["provenance"]["source_alias"]
        and material.requested_revision == parent["provenance"]["requested_revision"]
        and identity_record == parent["provenance"]["identity_material"]
        and model_identity(material) == parent["identity"]
    )
    child_revision = (
        identity_record["parent_ids"] == [parent["identity"]]
        and identity_record["artifacts"]
        == parent["provenance"]["identity_material"]["artifacts"]
    )
    if (
        material.revision_kind == "source"
        or not (same_identity_plan or child_revision)
    ):
        _q57_reject(
            parent_root_digest,
            "derived root must preserve one exact identity or name one exact artifact-preserving parent",
            "IDENTITY_MISMATCH",
        )
    if not isinstance(plans, tuple) or not plans or any(not isinstance(plan, dict) for plan in plans):
        _q57_reject(parent_root_digest, "derived root requires one or more canonical plan objects")
    try:
        canonical_plans = json.loads(canonical_bytes(list(plans)), object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        _q57_reject(parent_root_digest, f"derived plans are not canonical JSON: {error}")
    return _write_cartridge_root(
        cartridge,
        material,
        identity_record,
        parent["provenance"]["containers"],
        parent["tensor_maps"],
        tuple(sorted(
            _read_index(cartridge, parent_root_digest).values(),
            key=lambda item: item.page_digest,
        )),
        canonical_plans,
        parent["deltas"],
        durable=True,
    )


def _training_delta_records(
    parent: dict,
    parent_root_digest: str,
    kind: str,
    ordered_page_digests: list[str],
    manifest_digest: str,
) -> tuple[dict, list[dict], str]:
    if kind not in {"adapter", "certificate_recovery", "precision_correction", "replacement_pages"}:
        _q57_reject(parent_root_digest, "training delta kind is malformed", "INVALID_REQUEST")
    if not ordered_page_digests or len(ordered_page_digests) != len(set(ordered_page_digests)):
        _q57_reject(
            parent_root_digest,
            "one training delta requires unique ordered page identities",
            "INVALID_REQUEST",
        )
    for page_digest in ordered_page_digests:
        _content_hex(page_digest, parent_root_digest)
    _content_hex(manifest_digest, parent_root_digest)
    body = {
        "kind": kind,
        "base_identity": parent["identity"],
        "ordered_page_digests": ordered_page_digests,
        "manifest_digest": manifest_digest,
    }
    delta = {"delta_id": digest_bytes(canonical_bytes(body)), **body}
    deltas = [*parent["deltas"], delta]
    expected_transform = digest_bytes(canonical_bytes(deltas))
    return delta, deltas, expected_transform


def _write_training_delta_root(
    cartridge: Path,
    parent_root_digest: str,
    parent: dict,
    material: IdentityTuple,
    additions: tuple[PageLocation, ...],
    deltas: list[dict],
    expected_transform: str,
    *,
    durable: bool,
) -> str:
    identity_record = _identity_record(material)
    if (
        material.revision_kind != "tuned"
        or identity_record["parent_ids"] != [parent["identity"]]
        or identity_record["artifacts"]
        != parent["provenance"]["identity_material"]["artifacts"]
        or identity_record["transform_manifest_digest"] != expected_transform
    ):
        _q57_reject(
            parent_root_digest,
            "training delta child identity does not bind its parent, source bytes, and ordered deltas",
            "IDENTITY_MISMATCH",
        )
    current = _read_index(cartridge, parent_root_digest)
    if (
        not isinstance(additions, tuple)
        or not additions
        or any(not isinstance(location, PageLocation) for location in additions)
        or len({location.page_digest for location in additions}) != len(additions)
    ):
        _q57_reject(parent_root_digest, "staged training page locations are malformed", "INVALID_REQUEST")
    for location in additions:
        _read_page(cartridge, location)
    locations = {**current, **{location.page_digest: location for location in additions}}
    return _write_cartridge_root(
        cartridge,
        material,
        identity_record,
        parent["provenance"]["containers"],
        parent["tensor_maps"],
        tuple(sorted(locations.values(), key=lambda location: location.page_digest)),
        parent["plans"],
        deltas,
        durable=durable,
    )


def append_training_delta(
    cartridge: str | Path,
    parent_root_digest: str,
    material: IdentityTuple,
    kind: str,
    pages: tuple[bytes, ...],
    manifest_digest: str,
) -> str:
    """Append ordered immutable delta pages and publish one derived logical root."""

    cartridge = Path(cartridge)
    parent = load_root(cartridge, parent_root_digest)
    if (
        not isinstance(pages, tuple)
        or not pages
        or any(not isinstance(page, bytes) or not 0 < len(page) <= PAGE_BYTES for page in pages)
    ):
        _q57_reject(parent_root_digest, "training delta pages are malformed", "INVALID_REQUEST")
    ordered_page_digests = [digest_bytes(page) for page in pages]
    _, deltas, expected_transform = _training_delta_records(
        parent, parent_root_digest, kind, ordered_page_digests, manifest_digest
    )
    additions = _write_segments(
        cartridge,
        zip(ordered_page_digests, pages, strict=True),
    )
    return _write_training_delta_root(
        cartridge,
        parent_root_digest,
        parent,
        material,
        additions,
        deltas,
        expected_transform,
        durable=False,
    )


def append_staged_training_delta(
    cartridge: str | Path,
    parent_root_digest: str,
    kind: str,
    pages: tuple[PageLocation, ...],
    manifest_digest: str,
) -> str:
    """Bind durable staged pages into one non-callable direct child of the frozen parent."""

    cartridge = Path(cartridge)
    parent = load_root(cartridge, parent_root_digest)
    if (
        not isinstance(pages, tuple)
        or not pages
        or any(not isinstance(location, PageLocation) for location in pages)
    ):
        _q57_reject(
            parent_root_digest,
            "staged training pages require one nonempty PageLocation tuple",
            "INVALID_REQUEST",
        )
    ordered_page_digests = [location.page_digest for location in pages]
    _, deltas, expected_transform = _training_delta_records(
        parent, parent_root_digest, kind, ordered_page_digests, manifest_digest
    )
    material, _ = _material_from_provenance(parent["provenance"], parent_root_digest)
    child_material = replace(
        material,
        revision_kind="tuned",
        parent_ids=(parent["identity"],),
        transform_manifest_digest=expected_transform,
    )
    return _write_training_delta_root(
        cartridge,
        parent_root_digest,
        parent,
        child_material,
        pages,
        deltas,
        expected_transform,
        durable=True,
    )


def read_training_delta(
    cartridge: str | Path, root_digest: str, delta_id: str
) -> tuple[bytes, ...]:
    """Resolve one ordered Q57 training delta from its verified immutable page identities."""

    cartridge = Path(cartridge)
    root = load_root(cartridge, root_digest)
    matches = [delta for delta in root["deltas"] if delta["delta_id"] == delta_id]
    if len(matches) != 1:
        _q57_reject(root_digest, f"training delta {delta_id!r} is absent or duplicated")
    locations = _read_index(cartridge, root_digest)
    return tuple(_read_page(cartridge, locations[page]) for page in matches[0]["ordered_page_digests"])


def _physical_ranges(descriptor: int, size: int, object_id: str) -> list[tuple[int, int]]:
    """Return Darwin device extents, excluding sparse holes, for exact Q4 accounting."""

    ranges = []
    offset = 0
    while offset < size:
        try:
            reply = fcntl.fcntl(
                descriptor,
                _F_LOG2PHYS_EXT,
                _LOG2PHYS.pack(0, size - offset, offset),
            )
            _, contiguous, device_offset = _LOG2PHYS.unpack(reply)
        except (OSError, struct.error) as error:
            _q57_reject(
                object_id,
                f"physical extent instrumentation is unavailable: {error}",
                "DURABILITY_UNSUPPORTED",
            )
        length = min(contiguous, size - offset)
        if length <= 0:
            _q57_reject(
                object_id,
                "physical extent instrumentation returned no forward progress",
                "DURABILITY_UNSUPPORTED",
            )
        if device_offset >= 0:
            ranges.append((device_offset, device_offset + length))
        offset += length
    return ranges


def _range_union_bytes(ranges: list[tuple[int, int]]) -> int:
    total = 0
    end = -1
    for start, stop in sorted(ranges):
        if start >= end:
            total += stop - start
        elif stop > end:
            total += stop - end
        end = max(end, stop)
    return total


def measure_extent_footprint(
    source_descriptors: tuple[int, ...],
    target_descriptors: tuple[int, ...],
    object_id: str,
) -> dict:
    """Measure exact logical and Darwin physical extents for one Q4 conversion instant."""

    if (
        not isinstance(source_descriptors, tuple)
        or not source_descriptors
        or not isinstance(target_descriptors, tuple)
        or not target_descriptors
        or any(type(descriptor) is not int for descriptor in (*source_descriptors, *target_descriptors))
    ):
        _q57_reject(object_id, "Q4 measurement requires nonempty descriptor tuples", "INVALID_REQUEST")
    groups = []
    device = None
    for label, descriptors in (
        ("source", source_descriptors),
        ("target", target_descriptors),
    ):
        logical_bytes = 0
        ranges = []
        for descriptor in descriptors:
            try:
                observed = os.fstat(descriptor)
            except OSError as error:
                _q57_reject(
                    object_id,
                    f"Q4 {label} descriptor is unavailable: {error}",
                    "SOURCE_UNAVAILABLE" if label == "source" else "PAGE_CORRUPT",
                )
            if (
                not stat.S_ISREG(observed.st_mode)
                or (device is not None and observed.st_dev != device)
            ):
                _q57_reject(object_id, f"Q4 {label} extent is not one regular same-device file")
            device = observed.st_dev
            logical_bytes += observed.st_size
            ranges.extend(_physical_ranges(descriptor, observed.st_size, object_id))
        groups.append((logical_bytes, ranges))
    source_bytes, source_ranges = groups[0]
    target_bytes, target_ranges = groups[1]
    source_allocated = _range_union_bytes(source_ranges)
    target_allocated = _range_union_bytes(target_ranges)
    peak_allocated = _range_union_bytes([*source_ranges, *target_ranges])
    return {
        "source_extent_bytes": source_bytes,
        "target_extent_bytes": target_bytes,
        "source_allocated_bytes": source_allocated,
        "target_allocated_bytes": target_allocated,
        "shared_allocated_bytes": source_allocated + target_allocated - peak_allocated,
        "allocated_peak_bytes": peak_allocated,
    }


def extent_footprint(
    cartridge: str | Path,
    root_digest: str,
    source_descriptors: Mapping[str, int],
) -> dict:
    """Measure source, target, shared, and peak physical parameter extents for Q4."""

    cartridge = Path(cartridge)
    root = load_root(cartridge, root_digest)
    artifacts = root["provenance"]["identity_material"]["artifacts"]
    if not isinstance(source_descriptors, Mapping) or set(source_descriptors) != {
        artifact["path"] for artifact in artifacts
    }:
        _q57_reject(root_digest, "Q4 instrumentation requires every source descriptor exactly once")
    source_fds = []
    for artifact in artifacts:
        descriptor = source_descriptors[artifact["path"]]
        if type(descriptor) is not int:
            _q57_reject(root_digest, "Q4 source descriptors must be open integers")
        try:
            observed = os.fstat(descriptor)
        except OSError as error:
            _q57_reject(
                artifact["path"], f"Q4 source descriptor is unavailable: {error}", "SOURCE_UNAVAILABLE"
            )
        if (
            not stat.S_ISREG(observed.st_mode)
            or observed.st_size != artifact["size"]
        ):
            _q57_reject(artifact["path"], "Q4 source extent shape changed")
        source_fds.append(descriptor)

    target_fds = []
    segment_ids = sorted({
        location.segment_id for location in _read_index(cartridge, root_digest).values()
    })
    try:
        for segment_id in segment_ids:
            path = cartridge / "segments" / _content_hex(segment_id, segment_id)
            target_fds.append(os.open(path, os.O_RDONLY))
        return measure_extent_footprint(tuple(source_fds), tuple(target_fds), root_digest)
    except OSError as error:
        _q57_reject(root_digest, f"Q4 target segment is unavailable: {error}", "PAGE_CORRUPT")
    finally:
        for descriptor in target_fds:
            os.close(descriptor)


def page_locations(cartridge: str | Path, root_digest: str) -> tuple[PageLocation, ...]:
    """Return the sorted physical layout for one verified logical root."""

    load_root(cartridge, root_digest)
    return tuple(_read_index(Path(cartridge), root_digest).values())


def stage_training_pages(cartridge: str | Path, pages) -> tuple[PageLocation, ...]:
    """Durably stage unique Q23 training pages without making them callable."""

    if isinstance(pages, (bytes, bytearray, memoryview)):
        _q57_reject("training-pages", "training pages require an iterable of byte pages", "INVALID_REQUEST")
    try:
        iterator = iter(pages)
    except TypeError:
        _q57_reject("training-pages", "training pages require an iterable", "INVALID_REQUEST")
    seen = set()

    def unique_pages():
        for payload in iterator:
            if not isinstance(payload, bytes) or not 0 < len(payload) <= PAGE_BYTES:
                _q57_reject(
                    "training-pages",
                    "each staged training page must contain at most 4 MiB",
                    "INVALID_REQUEST",
                )
            page_digest = digest_bytes(payload)
            if page_digest not in seen:
                seen.add(page_digest)
                yield page_digest, payload

    cartridge = Path(cartridge)
    locations = _write_segments(cartridge, unique_pages())
    if not locations:
        _q57_reject("training-pages", "at least one training page is required", "INVALID_REQUEST")
    segments = cartridge / "segments"
    for segment_id in sorted({location.segment_id for location in locations}):
        _fullsync_file(segments / _content_hex(segment_id, segment_id), f"training-page:{segment_id}")
    _sync_directory(segments, "training-pages")
    for location in locations:
        _read_page(cartridge, location)
    return locations


def read_training_page(
    cartridge: str | Path, root_digest: str, page_digest: str
) -> bytes:
    """Read one Q23 training page only through a verified root and physical index."""

    cartridge = Path(cartridge)
    _content_hex(page_digest, root_digest)
    load_root(cartridge, root_digest)
    locations = _read_index(cartridge, root_digest)
    if page_digest not in locations:
        _q57_reject(
            page_digest,
            "training page is absent from the verified root",
            "PAGE_CORRUPT",
        )
    return _read_page(cartridge, locations[page_digest])


def page_index_byte_count(cartridge: str | Path, root_digest: str) -> int:
    """Return the verified fixed-record index length without exposing its private encoding."""

    load_root(cartridge, root_digest)
    return len(_read_index(Path(cartridge), root_digest)) * _INDEX_RECORD.size


def repack_segments(
    cartridge: str | Path, root_digest: str, ordered_page_digests: tuple[str, ...]
) -> str:
    """Rewrite every required page in a new physical order without changing the logical root."""

    cartridge = Path(cartridge)
    root = load_root(cartridge, root_digest)
    current = _read_index(cartridge, root_digest)
    required = _root_page_digests(root)
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


def verify_root_content(cartridge: str | Path, root_digest: str) -> dict:
    """Verify every candidate segment, page, index, and root before generation publication."""

    return _verify_dependency_paths(Path(cartridge), root_digest)[0]


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


def _cartridge_identity_path(cartridge: Path) -> Path:
    return cartridge / _CARTRIDGE_IDENTITY_NAME


def _read_cartridge_uuid(cartridge: Path) -> str:
    path = _cartridge_identity_path(cartridge)
    try:
        payload = path.read_bytes()
        record = json.loads(payload, object_pairs_hook=_unique_object)
        if (not isinstance(record, dict) or set(record) != {"cartridge_uuid"}
                or canonical_bytes(record) != payload):
            raise ValueError("identity marker is not exact canonical content")
        return _normalize_uuid(record["cartridge_uuid"], "cartridge_uuid")
    except FileNotFoundError as error:
        if not cartridge.is_dir():
            raise
        _lifecycle_reject(
            "unidentified", f"cartridge identity marker is absent: {error}",
            "CARTRIDGE_IDENTITY_MISMATCH",
        )
    except CassetteError as error:
        _lifecycle_reject(
            "unidentified", f"cartridge identity marker is invalid: {error.detail}",
            "CARTRIDGE_IDENTITY_MISMATCH",
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        _lifecycle_reject(
            "unidentified", f"cartridge identity marker is unavailable or invalid: {error}",
            "CARTRIDGE_IDENTITY_MISMATCH",
        )


def initialize_cartridge(cartridge: str | Path, cartridge_uuid: str | None = None) -> str:
    """Create one immutable logical cartridge UUID with durable readback on a writable volume."""

    cartridge = Path(cartridge)
    path = _cartridge_identity_path(cartridge)
    if path.exists():
        observed = _read_cartridge_uuid(cartridge)
        if cartridge_uuid is not None and observed != _normalize_uuid(
            cartridge_uuid, "cartridge_uuid"
        ):
            _lifecycle_reject(
                observed, "the immutable cartridge UUID cannot be replaced",
                "CARTRIDGE_IDENTITY_MISMATCH",
            )
        return observed
    if not cartridge.is_dir():
        _lifecycle_reject(
            "unidentified", "cartridge directory is unavailable", "CARTRIDGE_DISCONNECTED"
        )
    if os.statvfs(cartridge).f_flag & os.ST_RDONLY:
        _lifecycle_reject(
            "unidentified", "cannot initialize a cartridge on a read-only volume",
            "CARTRIDGE_READ_ONLY",
        )
    logical_uuid = (
        str(uuid.uuid4()) if cartridge_uuid is None
        else _normalize_uuid(cartridge_uuid, "cartridge_uuid")
    )
    payload = canonical_bytes({"cartridge_uuid": logical_uuid})
    _durable_replace(path, payload, f"cartridge:{logical_uuid}")
    if _read_cartridge_uuid(cartridge) != logical_uuid:
        _lifecycle_reject(
            logical_uuid, "cartridge UUID changed during durable readback",
            "CARTRIDGE_IDENTITY_MISMATCH",
        )
    return logical_uuid


def _cartridge_snapshot(
    cartridge: Path, cartridge_uuid: str, filesystem_uuid: str
) -> tuple[CartridgeIdentity, bool]:
    if _read_cartridge_uuid(cartridge) != cartridge_uuid:
        _lifecycle_reject(
            cartridge_uuid, "mounted volume contains another logical cartridge",
            "CARTRIDGE_IDENTITY_MISMATCH",
        )
    pin = recover_generation(cartridge)
    read_only = bool(os.statvfs(cartridge).f_flag & os.ST_RDONLY)
    return (
        CartridgeIdentity(
            cartridge_uuid,
            filesystem_uuid,
            pin.generation if pin is not None else None,
            pin.root_digest if pin is not None else None,
        ),
        read_only,
    )


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


def _integrity_reject(object_id: str, detail: str, code: str = "ROOT_INVALID") -> None:
    raise CassetteError(
        code=code,
        object_id=object_id,
        failed_invariant="Q62: verify before use and restore the original content identity",
        retryability="retryable" if code in {"PAGE_CORRUPT", "SOURCE_UNAVAILABLE"} else "terminal",
        detail=detail,
    )


def _repair_manifest_path(cartridge: Path, root_digest: str) -> Path:
    return cartridge / "repair" / f"{_content_hex(root_digest, root_digest)}.json"


def _repair_manifest_replica_path(cartridge: Path, root_digest: str) -> Path:
    return cartridge / "repair" / "manifests" / _content_hex(root_digest, root_digest)


def _repair_object_path(cartridge: Path, digest: str) -> Path:
    return cartridge / "repair" / "objects" / _content_hex(digest, digest)


def _portable_directory_sync(path: Path, object_id: str) -> None:
    try:
        descriptor = os.open(path, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    except OSError as error:
        _integrity_reject(object_id, f"repair directory sync failed for {path.name!r}: {error}")


def _quarantine(path: Path, object_id: str) -> None:
    if not path.exists():
        return
    try:
        payload = path.read_bytes()
        observed = digest_bytes(payload)[7:]
        directory = path.parents[1] / "quarantine"
        directory.mkdir(parents=True, exist_ok=True)
        os.replace(path, directory / f"{path.parent.name}-{path.name}-{observed}")
        _portable_directory_sync(directory, object_id)
    except OSError as error:
        _integrity_reject(object_id, f"corrupt object quarantine failed: {error}")


def _replace_exact(path: Path, payload: bytes, expected_digest: str, object_id: str) -> None:
    if digest_bytes(payload) != expected_digest:
        _integrity_reject(object_id, "repair candidate does not match the original digest")
    try:
        if path.exists() and path.read_bytes() == payload:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.NamedTemporaryFile(
            mode="w+b", dir=path.parent, prefix=f".{path.name}.repair-", delete=False
        )
        temporary_path = Path(temporary.name)
        try:
            temporary.write(payload)
            temporary.flush()
            os.fsync(temporary.fileno())
            command = getattr(fcntl, "F_FULLFSYNC", None)
            if command is not None:
                fcntl.fcntl(temporary.fileno(), command)
        finally:
            temporary.close()
        if temporary_path.read_bytes() != payload:
            _integrity_reject(object_id, "repair candidate changed during readback")
        _quarantine(path, object_id)
        os.replace(temporary_path, path)
        _portable_directory_sync(path.parent, object_id)
    except OSError as error:
        _integrity_reject(object_id, f"exact repair replacement failed: {error}")
    finally:
        if "temporary_path" in locals():
            temporary_path.unlink(missing_ok=True)


def _xor_payloads(payloads: tuple[bytes, ...], length: int) -> bytes:
    output = bytearray()
    for offset in range(0, length, 64 * 1024):
        width = min(64 * 1024, length - offset)
        value = 0
        for payload in payloads:
            value ^= int.from_bytes(payload[offset:offset + width], "little")
        output.extend(value.to_bytes(width, "little"))
    return bytes(output)


def _decode_root_copy(payload: bytes, root_digest: str, locations: dict[str, PageLocation]) -> dict:
    try:
        root = json.loads(payload, object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        _integrity_reject(f"root:{root_digest}", f"repair root copy is malformed: {error}")
    if digest_bytes(payload) != root_digest or canonical_bytes(root) != payload:
        _integrity_reject(f"root:{root_digest}", "repair root copy does not match its identity")
    _verify_root(root, root_digest, locations)
    return root


def _read_repair_object(cartridge: Path, digest: str, description: str) -> bytes:
    path = _repair_object_path(cartridge, digest)
    try:
        payload = path.read_bytes()
    except OSError as error:
        _integrity_reject(description, f"verified repair object is unavailable: {error}", "SOURCE_UNAVAILABLE")
    if digest_bytes(payload) != digest:
        _integrity_reject(description, "verified repair object does not match its identity", "PAGE_CORRUPT")
    return payload


def _decode_repair_manifest(payload: bytes) -> dict:
    envelope = json.loads(payload, object_pairs_hook=_unique_object)
    if (not isinstance(envelope, dict) or set(envelope) != {"digest", "record"}
            or canonical_bytes(envelope) != payload
            or not isinstance(envelope["record"], dict)
            or envelope["digest"] != digest_bytes(canonical_bytes(envelope["record"]))):
        raise ValueError("repair manifest envelope is not exact canonical content")
    return envelope["record"]


def _repair_record(
    cartridge: Path, root_digest: str
) -> tuple[dict, bytes, bytes, dict[str, PageLocation], bytes, str, bool]:
    object_id = f"repair:{root_digest}"
    try:
        manifest_payload = _repair_manifest_replica_path(cartridge, root_digest).read_bytes()
        record = _decode_repair_manifest(manifest_payload)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        _integrity_reject(object_id, f"verified repair manifest copy is unavailable or malformed: {error}")
    try:
        primary_payload = _repair_manifest_path(cartridge, root_digest).read_bytes()
        primary_valid = primary_payload == manifest_payload
    except OSError:
        primary_valid = False
    manifest_digest = digest_bytes(manifest_payload)
    if set(record) != {"root_digest", "index_digest", "pages", "stripes"}:
        _integrity_reject(object_id, "repair manifest has an incorrect field set")
    if record["root_digest"] != root_digest:
        _integrity_reject(object_id, "repair manifest names another root")
    root_copy = _read_repair_object(cartridge, root_digest, f"root-copy:{root_digest}")
    index_digest = record["index_digest"]
    _content_hex(index_digest, object_id)
    index_copy = _read_repair_object(cartridge, index_digest, f"index-copy:{root_digest}")
    locations = _decode_index(index_copy, root_digest)
    root = _decode_root_copy(root_copy, root_digest, locations)
    expected_pages = [
        {
            "page_digest": location.page_digest,
            "segment_id": location.segment_id,
            "offset": location.offset,
            "length": location.length,
            "parity_digest": next(
                (stripe["parity_digest"] for stripe in record["stripes"]
                 if location.page_digest in stripe.get("page_digests", [])),
                None,
            ),
        }
        for location in sorted(locations.values(), key=lambda item: item.page_digest)
    ]
    if record["pages"] != expected_pages or any(page["parity_digest"] is None for page in expected_pages):
        _integrity_reject(object_id, "repair page map does not match the immutable root and index")
    grouped = {}
    for location in locations.values():
        grouped.setdefault(location.segment_id, []).append(location)
    expected_stripes = []
    for segment_id, members in sorted(grouped.items()):
        members.sort(key=lambda item: item.offset)
        matching = [
            stripe for stripe in record["stripes"] if stripe.get("segment_id") == segment_id
        ]
        if len(matching) != 1:
            _integrity_reject(object_id, "repair manifest requires one parity stripe per segment")
        stripe = matching[0]
        if set(stripe) != {"segment_id", "page_digests", "lengths", "parity_digest", "length"}:
            _integrity_reject(object_id, "parity stripe has an incorrect field set")
        expected = {
            "segment_id": segment_id,
            "page_digests": [member.page_digest for member in members],
            "lengths": [member.length for member in members],
            "parity_digest": stripe["parity_digest"],
            "length": max(member.length for member in members),
        }
        _content_hex(stripe["parity_digest"], object_id)
        expected_stripes.append(expected)
    if record["stripes"] != expected_stripes:
        _integrity_reject(object_id, "repair parity map does not match physical segment membership")
    return (
        record,
        root_copy,
        index_copy,
        locations,
        manifest_payload,
        manifest_digest,
        primary_valid,
    )


def create_repair_set(
    cartridge: str | Path, root_digest: str, reservation: CapacityReservation
) -> RepairSet:
    """Create Q62 root/index replicas and one XOR parity stripe per segment after Q53 admission."""

    if not isinstance(reservation, CapacityReservation):
        _capacity_reject("repair-set", "a completed CapacityReservation is required", "INVALID_REQUEST")
    _active_reservation(reservation, reservation.operation_id)
    cartridge = Path(cartridge)
    _verify_dependency_paths(cartridge, root_digest)
    locations = _read_index(cartridge, root_digest)
    root_payload = (cartridge / "roots" / _content_hex(root_digest, root_digest)).read_bytes()
    index_payload = _index_path(cartridge, root_digest).read_bytes()
    index_digest = digest_bytes(index_payload)
    grouped = {}
    for location in locations.values():
        grouped.setdefault(location.segment_id, []).append(location)
    stripes = []
    parity_payloads = {}
    page_to_parity = {}
    for segment_id, members in sorted(grouped.items()):
        members.sort(key=lambda item: item.offset)
        payloads = tuple(_read_page(cartridge, member) for member in members)
        length = max(member.length for member in members)
        parity = _xor_payloads(payloads, length)
        parity_digest = digest_bytes(parity)
        parity_payloads[parity_digest] = parity
        for member in members:
            page_to_parity[member.page_digest] = parity_digest
        stripes.append({
            "segment_id": segment_id,
            "page_digests": [member.page_digest for member in members],
            "lengths": [member.length for member in members],
            "parity_digest": parity_digest,
            "length": length,
        })
    pages = [
        {
            "page_digest": location.page_digest,
            "segment_id": location.segment_id,
            "offset": location.offset,
            "length": location.length,
            "parity_digest": page_to_parity[location.page_digest],
        }
        for location in sorted(locations.values(), key=lambda item: item.page_digest)
    ]
    record = {
        "root_digest": root_digest,
        "index_digest": index_digest,
        "pages": pages,
        "stripes": stripes,
    }
    _, manifest_payload = _envelope(record)
    manifest_digest = digest_bytes(manifest_payload)
    objects = {root_digest: root_payload, index_digest: index_payload, **parity_payloads}
    required = _capacity_sum(
        (*[len(payload) for payload in objects.values()], 2 * len(manifest_payload)),
        reservation.operation_id,
    )
    if reservation.repair_bytes < required:
        _capacity_reject(
            reservation.operation_id,
            f"repair phase reserves {reservation.repair_bytes} bytes; exact repair set needs {required}",
        )
    for digest, payload in objects.items():
        _replace_exact(_repair_object_path(cartridge, digest), payload, digest, f"repair-object:{digest}")
    _replace_exact(
        _repair_manifest_replica_path(cartridge, root_digest),
        manifest_payload,
        manifest_digest,
        f"manifest-copy:{root_digest}",
    )
    _replace_exact(
        _repair_manifest_path(cartridge, root_digest),
        manifest_payload,
        manifest_digest,
        f"repair:{root_digest}",
    )
    _repair_record(cartridge, root_digest)
    return RepairSet(
        root_digest,
        manifest_digest,
        index_digest,
        tuple(stripe["parity_digest"] for stripe in stripes),
        required,
    )


def _transition(
    states: dict[str, str], transitions: list[tuple[str, str, str]], object_id: str, state: str
) -> None:
    prior = states.setdefault(object_id, "VALID")
    if state not in _INTEGRITY_STATES or state not in _INTEGRITY_TRANSITIONS[prior]:
        _integrity_reject(object_id, f"illegal integrity transition {prior} -> {state}")
    states[object_id] = state
    transitions.append((object_id, prior, state))


def _mark_corrupt(
    states: dict[str, str], transitions: list[tuple[str, str, str]], object_id: str
) -> None:
    for state in ("SUSPECT", "VERIFYING", "CORRUPT"):
        _transition(states, transitions, object_id, state)


def _normalize_source_pages(source_pages: Mapping[str, bytes] | None) -> dict[str, bytes]:
    if source_pages is None:
        return {}
    if not isinstance(source_pages, Mapping):
        _integrity_reject("repair:source", "source_pages must map page digests to bytes", "INVALID_REQUEST")
    normalized = {}
    for digest, payload in source_pages.items():
        if (not isinstance(digest, str) or not isinstance(payload, bytes)
                or digest_bytes(payload) != digest):
            _integrity_reject("repair:source", "source page does not match its declared digest", "INVALID_REQUEST")
        normalized[digest] = payload
    return normalized


def _integrity_operation(
    cartridge: Path,
    root_digest: str,
    *,
    repair: bool,
    reservation: CapacityReservation | None,
    source_pages: Mapping[str, bytes] | None,
) -> IntegrityReport:
    (
        record,
        root_copy,
        index_copy,
        locations,
        manifest_payload,
        manifest_digest,
        manifest_valid,
    ) = _repair_record(cartridge, root_digest)
    if repair:
        if not isinstance(reservation, CapacityReservation):
            _capacity_reject("repair", "repair requires a completed CapacityReservation", "INVALID_REQUEST")
        _active_reservation(reservation, reservation.operation_id)
        repair_extent = max(
            len(root_copy),
            len(index_copy),
            len(manifest_payload),
            *(sum(location.length for location in locations.values()
                  if location.segment_id == segment_id)
              for segment_id in {location.segment_id for location in locations.values()}),
            *(stripe["length"] for stripe in record["stripes"]),
        )
        if reservation.repair_bytes < repair_extent:
            _capacity_reject(
                reservation.operation_id,
                f"repair phase reserves {reservation.repair_bytes} bytes; one replacement extent needs {repair_extent}",
            )
    sources = _normalize_source_pages(source_pages)
    states = {}
    transitions = []
    required_pages = tuple(sorted(locations))
    manifest_id = f"manifest:{root_digest}"
    root_id = f"root:{root_digest}"
    index_id = f"index:{root_digest}"
    states[manifest_id] = states[root_id] = states[index_id] = "VALID"
    for digest in required_pages:
        states[f"page:{digest}"] = "VALID"
    for stripe in record["stripes"]:
        states[f"parity:{stripe['parity_digest']}"] = "VALID"

    if not manifest_valid:
        _mark_corrupt(states, transitions, manifest_id)
        if repair:
            _transition(states, transitions, manifest_id, "REPAIRING")
            _replace_exact(
                _repair_manifest_path(cartridge, root_digest),
                manifest_payload,
                manifest_digest,
                manifest_id,
            )
            _transition(states, transitions, manifest_id, "VALID")

    root_path = cartridge / "roots" / _content_hex(root_digest, root_digest)
    index_path = _index_path(cartridge, root_digest)
    for object_id, path, payload, digest in (
        (root_id, root_path, root_copy, root_digest),
        (index_id, index_path, index_copy, record["index_digest"]),
    ):
        try:
            valid = path.read_bytes() == payload
        except OSError:
            valid = False
        if not valid:
            _mark_corrupt(states, transitions, object_id)
            if repair:
                _transition(states, transitions, object_id, "REPAIRING")
                _replace_exact(path, payload, digest, object_id)
                _transition(states, transitions, object_id, "VALID")

    parity_payloads = {}
    for stripe in record["stripes"]:
        digest = stripe["parity_digest"]
        object_id = f"parity:{digest}"
        try:
            payload = _repair_object_path(cartridge, digest).read_bytes()
            valid = digest_bytes(payload) == digest and len(payload) == stripe["length"]
        except OSError:
            payload, valid = b"", False
        if valid:
            parity_payloads[digest] = payload
        else:
            _mark_corrupt(states, transitions, object_id)

    page_payloads = {}
    corrupt_pages = set()
    segment_corrupt = set()
    for segment_id in sorted({location.segment_id for location in locations.values()}):
        path = cartridge / "segments" / _content_hex(segment_id, segment_id)
        try:
            segment = path.read_bytes()
        except OSError:
            segment = b""
        members = sorted(
            (location for location in locations.values() if location.segment_id == segment_id),
            key=lambda item: item.offset,
        )
        if digest_bytes(segment) != segment_id:
            segment_id_state = f"segment:{segment_id}"
            states[segment_id_state] = "VALID"
            _mark_corrupt(states, transitions, segment_id_state)
            segment_corrupt.add(segment_id)
        for location in members:
            payload = segment[location.offset:location.offset + location.length]
            if len(payload) == location.length and digest_bytes(payload) == location.page_digest:
                page_payloads[location.page_digest] = payload
            else:
                object_id = f"page:{location.page_digest}"
                _mark_corrupt(states, transitions, object_id)
                corrupt_pages.add(location.page_digest)

    page_records = {page["page_digest"]: page for page in record["pages"]}
    stripe_records = {stripe["parity_digest"]: stripe for stripe in record["stripes"]}
    if repair:
        for digest in sorted(corrupt_pages):
            object_id = f"page:{digest}"
            _transition(states, transitions, object_id, "REPAIRING")
            page = page_records[digest]
            candidate = None
            local_path = _repair_object_path(cartridge, digest)
            try:
                local = local_path.read_bytes()
                if len(local) == page["length"] and digest_bytes(local) == digest:
                    candidate = local
            except OSError:
                pass
            source = sources.get(digest)
            if candidate is None and source is not None and len(source) == page["length"]:
                candidate = source
            parity_digest = page["parity_digest"]
            stripe = stripe_records[parity_digest]
            peers = [item for item in stripe["page_digests"] if item != digest]
            if (candidate is None and parity_digest in parity_payloads
                    and all(peer in page_payloads for peer in peers)):
                candidate = _xor_payloads(
                    (parity_payloads[parity_digest], *[page_payloads[peer] for peer in peers]),
                    stripe["length"],
                )[:page["length"]]
            if candidate is not None and digest_bytes(candidate) == digest:
                page_payloads[digest] = candidate
            else:
                _transition(states, transitions, object_id, "UNAVAILABLE")

        for segment_id in sorted(segment_corrupt):
            members = sorted(
                (location for location in locations.values() if location.segment_id == segment_id),
                key=lambda item: item.offset,
            )
            if all(member.page_digest in page_payloads for member in members):
                cursor = 0
                payload = bytearray()
                for member in members:
                    if member.offset != cursor:
                        _integrity_reject(f"segment:{segment_id}", "segment page intervals are discontinuous")
                    payload.extend(page_payloads[member.page_digest])
                    cursor += member.length
                _transition(states, transitions, f"segment:{segment_id}", "REPAIRING")
                _replace_exact(
                    cartridge / "segments" / _content_hex(segment_id, segment_id),
                    bytes(payload),
                    segment_id,
                    f"segment:{segment_id}",
                )
                _transition(states, transitions, f"segment:{segment_id}", "VALID")
                for member in members:
                    object_id = f"page:{member.page_digest}"
                    if states[object_id] == "REPAIRING":
                        _transition(states, transitions, object_id, "VALID")

        for stripe in record["stripes"]:
            digest = stripe["parity_digest"]
            object_id = f"parity:{digest}"
            if states[object_id] != "CORRUPT":
                continue
            _transition(states, transitions, object_id, "REPAIRING")
            if all(page in page_payloads for page in stripe["page_digests"]):
                payload = _xor_payloads(
                    tuple(page_payloads[page] for page in stripe["page_digests"]),
                    stripe["length"],
                )
                if digest_bytes(payload) == digest:
                    _replace_exact(_repair_object_path(cartridge, digest), payload, digest, object_id)
                    parity_payloads[digest] = payload
                    _transition(states, transitions, object_id, "VALID")
                    continue
            _transition(states, transitions, object_id, "UNAVAILABLE")

    unavailable = {
        digest for digest in required_pages
        if states[f"page:{digest}"] in {"CORRUPT", "UNAVAILABLE"}
    }
    if any(states[object_id] != "VALID" for object_id in (manifest_id, root_id, index_id)):
        unavailable.update(required_pages)
    if repair and not unavailable:
        load_root(cartridge, root_digest)
        for location in locations.values():
            _read_page(cartridge, location)
    return IntegrityReport(
        root_digest,
        tuple(sorted(states.items())),
        tuple(transitions),
        tuple(sorted(unavailable)),
    )


def verify_revision(cartridge: str | Path, root_digest: str) -> IntegrityReport:
    """Run Q62 verification without changing a corrupt object."""

    return _integrity_operation(
        Path(cartridge), root_digest, repair=False, reservation=None, source_pages=None
    )


def repair_revision(
    cartridge: str | Path,
    root_digest: str,
    reservation: CapacityReservation,
    *,
    source_pages: Mapping[str, bytes] | None = None,
) -> IntegrityReport:
    """Repair exact Q62 identities from local copies, verified source pages, then declared parity."""

    return _integrity_operation(
        Path(cartridge), root_digest, repair=True, reservation=reservation,
        source_pages=source_pages,
    )


def require_revision(cartridge: str | Path, root_digest: str) -> IntegrityReport:
    """Reject a new run unless every potentially addressable page is presently valid."""

    report = verify_revision(cartridge, root_digest)
    if report.unavailable_pages:
        joined = ",".join(report.unavailable_pages)
        object_id = (
            f"page:{report.unavailable_pages[0]}"
            if len(report.unavailable_pages) == 1 else f"pages:{joined}"
        )
        _integrity_reject(
            object_id, f"unavailable potentially addressable pages: {joined}", "PAGE_CORRUPT"
        )
    return report
