# store.py — identity, content, export, update, removal, lifecycle, and durable generations (Q1/Q6/Q25/Q26/Q32/Q49/Q53/Q54/Q57/Q60/Q62/Q73); depends on errors.py, schema.
"""Own model identity, content, cartridge lifecycle, repair, and callable generations.

Source adapters may accept mutable aliases, but they must return a canonical locator and a typed
immutable revision digest. Requested aliases remain provenance; they never enter the identity.
Cassette-owned identities and canonical content use BLAKE3 through this module alone. SafeTensors
and GGUF payloads enter bounded pages and segments; tensor maps retain their semantic byte ranges
while a separate fixed-record index owns physical placement.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
import copy
import ctypes
from dataclasses import dataclass, field, replace
import errno
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import stat
import struct
import sys
import tempfile
import threading
import uuid

from blake3 import blake3
import rfc8785
import resumablesha256

from errors import CassetteError
from schema.tables import EXPORT_TARGETS
from schema.validator import validate

_DIGEST_HEX_LENGTHS = {"blake3": 64, "sha256": 64, "git-sha1": 40}
_HEX = frozenset("0123456789abcdef")
_REVISION_KINDS = frozenset({"source", "executable", "tuned", "updated", "exported"})
_MAX_JSON_INTEGER = 2**53 - 1
_MAX_UNSIGNED_BYTES = 2**64 - 1
_TRANSITION_BYTE_FIELDS = (
    "payload_bytes", "journal_bytes", "index_bytes", "root_bytes", "pointer_bytes",
    "recovery_bytes",
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
_DARWIN_MNT_LOCAL = 0x00001000
_DARWIN_ATTR_VOL_UUID = 0x00040000
_DRIVE_ROOT_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")
PAGE_BYTES = 4 * 1024 * 1024
SEGMENT_BYTES = 1024 * 1024 * 1024
_SAFETENSORS_HEADER_BYTES = 100_000_000
_EXPORT_MANIFEST_BYTES = 100_000_000
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
class DriveVolume:
    """One locally mounted APFS candidate identified without writing to it."""

    name: str
    volume_uuid: str
    mount_path: str
    filesystem: str
    available_bytes: int
    device: int
    mount_source: str
    read_only: bool
    observed_access: str


@dataclass(frozen=True)
class WriterContext:
    """The exact process context that will attempt the store-owned write."""

    executable: str
    pid: int
    uid: int
    gid: int
    groups: tuple[int, ...]
    launch_host: str


@dataclass(frozen=True)
class DriveSelection:
    """A volume identity and writer context retained until the next revalidation."""

    volume: DriveVolume
    writer: WriterContext


class _DarwinAttrList(ctypes.Structure):
    """The SDK-defined attrlist layout used only for ATTR_VOL_UUID."""

    _fields_ = [
        ("bitmapcount", ctypes.c_ushort),
        ("reserved", ctypes.c_uint16),
        ("commonattr", ctypes.c_uint32),
        ("volattr", ctypes.c_uint32),
        ("dirattr", ctypes.c_uint32),
        ("fileattr", ctypes.c_uint32),
        ("forkattr", ctypes.c_uint32),
    ]


class _DarwinFsid(ctypes.Structure):
    """The SDK-defined fsid_t field embedded in Darwin's statfs structure."""

    _fields_ = [("values", ctypes.c_int32 * 2)]


class _DarwinStatfs(ctypes.Structure):
    """The arm64 macOS SDK statfs layout used for mounted-volume facts."""

    _fields_ = [
        ("block_size", ctypes.c_uint32),
        ("io_size", ctypes.c_int32),
        ("blocks", ctypes.c_uint64),
        ("free_blocks", ctypes.c_uint64),
        ("available_blocks", ctypes.c_uint64),
        ("files", ctypes.c_uint64),
        ("free_files", ctypes.c_uint64),
        ("filesystem_id", _DarwinFsid),
        ("owner", ctypes.c_uint32),
        ("filesystem_type", ctypes.c_uint32),
        ("mount_flags", ctypes.c_uint32),
        ("filesystem_subtype", ctypes.c_uint32),
        ("filesystem_name", ctypes.c_char * 16),
        ("mount_path", ctypes.c_char * 1024),
        ("mount_source", ctypes.c_char * 1024),
        ("extended_mount_flags", ctypes.c_uint32),
        ("reserved", ctypes.c_uint32 * 7),
    ]


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
class CapacityTransition:
    """One exact Q53 transition from a committed boundary to its next durable boundary."""

    operation_id: str
    boundary_id: str
    payload_bytes: int = 0
    journal_bytes: int = 0
    index_bytes: int = 0
    root_bytes: int = 0
    pointer_bytes: int = 0
    recovery_bytes: int = 0
    declared_writes: int = 1
    write_bytes: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if (not isinstance(self.operation_id, str)
                or _TRANSACTION_ID.fullmatch(self.operation_id) is None):
            _capacity_reject(
                "unidentified", "operation_id must satisfy the durable identifier grammar",
                "INVALID_REQUEST",
            )
        if not isinstance(self.boundary_id, str) or not self.boundary_id.strip():
            _capacity_reject(self.operation_id, "boundary_id must be nonempty text", "INVALID_REQUEST")
        for name in _TRANSITION_BYTE_FIELDS:
            _capacity_value(name, getattr(self, name), self.operation_id)
        if type(self.declared_writes) is not int or self.declared_writes < 1:
            _capacity_reject(
                self.operation_id, "declared_writes must be a positive integer", "INVALID_REQUEST"
            )
        if not isinstance(self.write_bytes, tuple):
            _capacity_reject(
                self.operation_id, "write_bytes must be a tuple", "INVALID_REQUEST"
            )
        if self.write_bytes:
            if (
                len(self.write_bytes) != self.declared_writes
                or any(type(value) is not int or value < 0 for value in self.write_bytes)
                or _capacity_sum(self.write_bytes, self.operation_id) != self.total_bytes
            ):
                _capacity_reject(
                    self.operation_id,
                    "write_bytes must assign every claimed byte to each declared write",
                    "INVALID_REQUEST",
                )
        elif self.declared_writes == 1:
            object.__setattr__(self, "write_bytes", (self.total_bytes,))
        else:
            _capacity_reject(
                self.operation_id,
                "multiple declared writes require an exact per-write byte assignment",
                "INVALID_REQUEST",
            )

    @property
    def total_bytes(self) -> int:
        """Return the checked byte claim for this transition alone."""

        return _capacity_sum(
            (getattr(self, name) for name in _TRANSITION_BYTE_FIELDS), self.operation_id
        )


@dataclass(frozen=True, slots=True)
class TransferExtent:
    """One store-created sparse extent whose writes remain confined to its open handle."""

    fd: int
    offset: int
    length: int
    operation_id: str


@dataclass(frozen=True)
class CapacityClaim:
    """One active or paused Q53 coordination claim for exactly one transition."""

    transition: CapacityTransition
    coordinator: CapacityCoordinator = field(repr=False, compare=False)
    state: str = field(default="PLANNED", init=False)
    history: tuple[str, ...] = field(default=(), init=False)
    observations: tuple[int, ...] = field(default=(), init=False)
    writes_started: int = field(default=0, init=False)
    recovery_parent: GenerationPin | None = field(default=None, init=False)
    recovery_parent_callable: bool = field(default=False, init=False)

    @property
    def active(self) -> bool:
        """Whether this transition still owns Cassette coordination bytes."""

        return self.state == "ACTIVE"


@dataclass
class _CapacityPool:
    """One process-local Q53 claim ledger shared by every path on one filesystem."""

    lock: threading.RLock = field(default_factory=threading.RLock)
    active: dict[tuple[str, str], int] = field(default_factory=dict)


_CAPACITY_POOLS_LOCK = threading.Lock()
_CAPACITY_POOLS: dict[int, _CapacityPool] = {}


class CapacityCoordinator:
    """Measure one cartridge filesystem and coordinate its exact next-transition claims."""

    __slots__ = ("_cartridge", "_device", "_issued", "_measurement_root", "_pool")

    def __init__(self, cartridge: str | Path):
        path = Path(cartridge)
        measurement_root = path
        while not measurement_root.exists() and measurement_root != measurement_root.parent:
            measurement_root = measurement_root.parent
        try:
            device = os.stat(measurement_root).st_dev
        except OSError as error:
            _capacity_reject(
                "coordinator",
                f"cartridge path is unavailable for capacity coordination: {error}",
                "CARTRIDGE_DISCONNECTED",
                "retryable",
            )
        with _CAPACITY_POOLS_LOCK:
            pool = _CAPACITY_POOLS.setdefault(device, _CapacityPool())
        self._cartridge = path
        self._device = device
        self._issued: list[CapacityClaim] = []
        self._measurement_root = measurement_root
        self._pool = pool

    @property
    def cartridge(self) -> Path:
        """Return the exact cartridge path whose filesystem this coordinator measures."""

        return self._cartridge

    def __call__(self, transition: CapacityTransition) -> CapacityClaim:
        """Claim one exact transition through this concrete store-owned coordinator."""

        return claim_next_transition(transition, coordinator=self)

    def claims(self) -> tuple[CapacityClaim, ...]:
        """Return this coordinator's ordered claim and observation record."""

        with self._pool.lock:
            return tuple(self._issued)

    def _raw_free(self, operation_id: str) -> int:
        measurement_path = (
            self._cartridge if self._cartridge.exists() else self._measurement_root
        )
        try:
            if os.stat(measurement_path).st_dev != self._device:
                _capacity_reject(
                    operation_id,
                    "cartridge filesystem identity changed during capacity coordination",
                    "CARTRIDGE_DISCONNECTED",
                    "retryable",
                )
            snapshot = os.statvfs(measurement_path)
        except CassetteError:
            raise
        except OSError as error:
            _capacity_reject(
                operation_id,
                f"capacity measurement failed: {error}",
                "CARTRIDGE_DISCONNECTED",
                "retryable",
            )
        fragment = _capacity_value("filesystem fragment bytes", snapshot.f_frsize, operation_id)
        available_fragments = _capacity_value(
            "filesystem available fragments", snapshot.f_bavail, operation_id
        )
        if fragment == 0:
            _capacity_reject(
                operation_id,
                "filesystem capacity measurement reported a zero fragment size",
                "DURABILITY_UNSUPPORTED",
            )
        if available_fragments > _MAX_UNSIGNED_BYTES // fragment:
            _capacity_reject(operation_id, "filesystem free-byte measurement overflowed")
        return available_fragments * fragment

    def _available(self, claim: CapacityClaim | None, operation_id: str) -> int:
        """Return raw free bytes minus every other live Cassette claim."""

        with self._pool.lock:
            raw_free = self._raw_free(operation_id)
            current_key = None if claim is None else _capacity_claim_key(claim.transition)
            other_claimed = _capacity_sum(
                (
                    amount
                    for key, amount in self._pool.active.items()
                    if key != current_key
                ),
                operation_id,
            )
            return max(raw_free - other_claimed, 0)

    def _activate(self, claim: CapacityClaim) -> bool:
        """Atomically admit and record this transition against all other Cassette writers."""

        transition = claim.transition
        key = _capacity_claim_key(transition)
        with self._pool.lock:
            parent, callable_parent = _capacity_boundary_marker(self._cartridge)
            object.__setattr__(claim, "recovery_parent", parent)
            object.__setattr__(claim, "recovery_parent_callable", callable_parent)
            self._issued.append(claim)
            if key in self._pool.active:
                _capacity_reject(
                    transition.operation_id,
                    f"transition {transition.boundary_id!r} already has an active claim",
                    "INVALID_REQUEST",
                )
            raw_free = self._raw_free(transition.operation_id)
            already_claimed = _capacity_sum(
                self._pool.active.values(), transition.operation_id
            )
            available = max(raw_free - already_claimed, 0)
            _record_capacity_observation(claim, available, "MEASURE")
            object.__setattr__(claim, "history", (*claim.history, "PLAN_NEXT"))
            if available < transition.total_bytes:
                object.__setattr__(claim, "state", "PAUSED_RECOVERABLE")
                object.__setattr__(claim, "history", (*claim.history, "PAUSED_RECOVERABLE"))
                return False
            self._pool.active[key] = transition.total_bytes
            object.__setattr__(claim, "state", "ACTIVE")
            object.__setattr__(claim, "history", (*claim.history, "CLAIM_NEXT"))
            return True

    def _release(self, claim: CapacityClaim) -> None:
        """Release exactly the active ledger entry owned by this claim."""

        key = _capacity_claim_key(claim.transition)
        with self._pool.lock:
            observed = self._pool.active.get(key)
            if key not in self._pool.active or observed != claim.transition.total_bytes:
                _capacity_reject(
                    claim.transition.operation_id,
                    "active claim ledger differs from the transition being released",
                    "INVALID_REQUEST",
                )
            del self._pool.active[key]

    def _recover(self, claim: CapacityClaim) -> bool:
        """Select the valid parent or committed child through store-owned recovery."""

        return _recover_capacity_boundary(self._cartridge, claim)

    def active_claims(self) -> tuple[tuple[str, str, int], ...]:
        """Return a stable inspection record of live claims on this filesystem."""

        with self._pool.lock:
            return tuple(
                (operation_id, boundary_id, amount)
                for (operation_id, boundary_id), amount in sorted(self._pool.active.items())
            )

    def owns(self, cartridge: str | Path) -> bool:
        """Return whether a path still resolves to this coordinator's filesystem."""

        path = Path(cartridge)
        while not path.exists() and path != path.parent:
            path = path.parent
        try:
            return os.stat(path).st_dev == self._device
        except OSError:
            return False

    def owns_descriptor(self, descriptor: int) -> bool:
        """Return whether an open extent belongs to this coordinated filesystem."""

        try:
            return os.fstat(descriptor).st_dev == self._device
        except OSError:
            return False


CapacityTransitionController = CapacityCoordinator


def _capacity_coordinator(
    cartridge: str | Path,
    controller: CapacityCoordinator | None,
    operation_id: str,
) -> CapacityCoordinator:
    """Bind every storage mutation to the concrete coordinator for its filesystem."""

    if controller is None:
        return CapacityCoordinator(cartridge)
    if not isinstance(controller, CapacityCoordinator) or not controller.owns(cartridge):
        _capacity_reject(
            operation_id,
            "capacity coordinator does not own this cartridge filesystem",
            "INVALID_REQUEST",
        )
    return controller


@dataclass(frozen=True)
class ReclaimableObject:
    """The complete Q53 reclaim decision record for one Cassette object."""

    object_id: str
    cassette_owned: bool
    pinned: bool
    reachable_from_retained_root: bool
    rollback_retained: bool
    retention_class: str
    active_claim_reference: bool
    active_transaction_reference: bool
    active_journal_reference: bool

    def __post_init__(self) -> None:
        if not isinstance(self.object_id, str) or not self.object_id:
            _capacity_reject("reclaim", "object_id must be nonempty text", "INVALID_REQUEST")
        for name in (
            "cassette_owned", "pinned", "reachable_from_retained_root", "rollback_retained",
            "active_claim_reference", "active_transaction_reference", "active_journal_reference",
        ):
            if type(getattr(self, name)) is not bool:
                _capacity_reject("reclaim", f"{name} must be bool", "INVALID_REQUEST")
        if self.retention_class not in {"TEMPORARY", "REPRODUCIBLE", "DURABLE", "USER_OWNED"}:
            _capacity_reject(
                "reclaim", "retention_class must be TEMPORARY, REPRODUCIBLE, DURABLE, or USER_OWNED", "INVALID_REQUEST"
            )


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

    def bind(
        self,
        access: CartridgeAccess,
        *,
        write: bool | None = None,
    ) -> BoundCartridge:
        """Bind one path-like value to this exact verified access and mount epoch."""

        self.resolve(access)
        if write is not None and type(write) is not bool:
            _lifecycle_reject(
                self._cartridge_uuid, "bound access mode must be bool or None", "INVALID_REQUEST"
            )
        return BoundCartridge(self, access, access.write if write is None else write)

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


@dataclass(frozen=True, slots=True)
class BoundCartridge(os.PathLike):
    """Resolve one cartridge path only while its Q49 access token remains current."""

    lifecycle: CartridgeLifecycle
    access: CartridgeAccess
    write: bool

    def __fspath__(self) -> str:
        if self.write and not self.access.write:
            _lifecycle_reject(
                self.lifecycle._cartridge_uuid,
                "read-only access cannot resolve a write operation",
                "CARTRIDGE_READ_ONLY",
            )
        return os.fspath(self.lifecycle.resolve(self.access))


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


def _drive_reject(volume_uuid: str, detail: str, code: str = "CAPABILITY_MISMATCH") -> None:
    retryable = code in {"CARTRIDGE_DISCONNECTED", "CARTRIDGE_READ_ONLY"}
    raise CassetteError(
        code=code,
        object_id=f"volume:{volume_uuid}",
        failed_invariant="Q44/Q49: mounted APFS identity and writer-context revalidation",
        retryability="retryable" if retryable else "terminal",
        detail=detail,
    )


def _darwin_statfs(mount: Path) -> _DarwinStatfs:
    if platform.system() != "Darwin":
        _drive_reject(str(mount), "mounted APFS discovery requires macOS")
    result = _DarwinStatfs()
    libc = ctypes.CDLL(None, use_errno=True)
    statfs = libc.statfs
    statfs.argtypes = (ctypes.c_char_p, ctypes.POINTER(_DarwinStatfs))
    statfs.restype = ctypes.c_int
    if statfs(os.fsencode(mount), ctypes.byref(result)) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error), mount)
    return result


def _darwin_volume_uuid(mount: Path) -> str:
    attributes = _DarwinAttrList(bitmapcount=5, volattr=_DARWIN_ATTR_VOL_UUID)
    result = (ctypes.c_ubyte * 20)()
    libc = ctypes.CDLL(None, use_errno=True)
    getattrlist = libc.getattrlist
    getattrlist.argtypes = (
        ctypes.c_char_p,
        ctypes.POINTER(_DarwinAttrList),
        ctypes.c_void_p,
        ctypes.c_size_t,
        ctypes.c_ulong,
    )
    getattrlist.restype = ctypes.c_int
    if getattrlist(os.fsencode(mount), ctypes.byref(attributes), result, len(result), 0) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error), mount)
    return str(uuid.UUID(bytes=bytes(result[4:])))


def _cstring(value: ctypes.Array) -> str:
    return bytes(value).split(b"\0", 1)[0].decode("utf-8", "strict")


def _observed_posix_access(mount: Path, read_only: bool) -> str:
    if read_only:
        return "READ_ONLY_VOLUME"
    metadata = mount.stat()
    uid = os.geteuid()
    groups = frozenset((os.getegid(), *os.getgroups()))
    if uid == 0:
        return "POSIX_MODE_ALLOWED"
    if uid == metadata.st_uid:
        allowed = bool(metadata.st_mode & stat.S_IWUSR)
    elif metadata.st_gid in groups:
        allowed = bool(metadata.st_mode & stat.S_IWGRP)
    else:
        allowed = bool(metadata.st_mode & stat.S_IWOTH)
    return "POSIX_MODE_ALLOWED" if allowed else "POSIX_MODE_DENIED"


def writer_process_context() -> WriterContext:
    """Report the exact Python process that would issue a subsequent store write."""

    return WriterContext(
        executable=os.path.realpath(sys.executable),
        pid=os.getpid(),
        uid=os.geteuid(),
        gid=os.getegid(),
        groups=tuple(sorted(set(os.getgroups()))),
        launch_host=platform.node(),
    )


def list_external_apfs_volumes() -> tuple[DriveVolume, ...]:
    """Read locally mounted APFS volumes below /Volumes without testing or changing write access."""

    if platform.system() != "Darwin":
        _drive_reject("unavailable", "mounted APFS discovery requires macOS")
    volumes = []
    try:
        mounts = sorted(Path("/Volumes").iterdir(), key=lambda path: path.name.casefold())
    except OSError as error:
        _drive_reject("unavailable", f"could not read /Volumes: {error}")
    for mount in mounts:
        try:
            if mount.is_symlink() or not mount.is_dir():
                continue
            filesystem = _darwin_statfs(mount)
            if not filesystem.mount_flags & _DARWIN_MNT_LOCAL:
                continue
            if _cstring(filesystem.filesystem_name).casefold() != "apfs":
                continue
            snapshot = os.statvfs(mount)
            if snapshot.f_frsize <= 0 or snapshot.f_bavail < 0:
                continue
            available_bytes = snapshot.f_frsize * snapshot.f_bavail
            volume_uuid = _darwin_volume_uuid(mount)
            read_only = bool(snapshot.f_flag & os.ST_RDONLY)
            volumes.append(
                DriveVolume(
                    name=mount.name,
                    volume_uuid=volume_uuid,
                    mount_path=str(mount),
                    filesystem="apfs",
                    available_bytes=available_bytes,
                    device=mount.stat().st_dev,
                    mount_source=_cstring(filesystem.mount_source),
                    read_only=read_only,
                    observed_access=_observed_posix_access(mount, read_only),
                )
            )
        except (OSError, UnicodeError, ValueError):
            continue
    return tuple(volumes)


def select_external_apfs_volume(volume_uuid: str) -> DriveSelection:
    """Select one exact discovered volume while retaining its current writer context."""

    normalized = _normalize_uuid(volume_uuid, "volume_uuid")
    matches = tuple(
        volume for volume in list_external_apfs_volumes() if volume.volume_uuid == normalized
    )
    if len(matches) != 1:
        _drive_reject(normalized, "selected APFS volume is unavailable or ambiguous", "CARTRIDGE_DISCONNECTED")
    return DriveSelection(volume=matches[0], writer=writer_process_context())


def revalidate_external_apfs_volume(selection: DriveSelection) -> DriveSelection:
    """Require the selected mount's stable identity before the store opens or creates a root."""

    if not isinstance(selection, DriveSelection):
        _drive_reject("unidentified", "drive selection has the wrong record shape", "INVALID_REQUEST")
    current = select_external_apfs_volume(selection.volume.volume_uuid)
    expected = selection.volume
    observed = current.volume
    if (
        observed.mount_path != expected.mount_path
        or observed.device != expected.device
        or observed.mount_source != expected.mount_source
        or observed.filesystem != expected.filesystem
    ):
        _drive_reject(
            expected.volume_uuid,
            "selected APFS volume identity changed after selection; retry with the current mount",
            "CARTRIDGE_DISCONNECTED",
        )
    return current


def _inventory_reject(object_id: object, detail: str) -> None:
    raise CassetteError(
        "PROVENANCE_VIOLATION",
        str(object_id),
        "Q80: exact campaign evidence",
        "terminal",
        detail,
    )


def inventory_step(root, *, excluded=(), checkpoint=None, limit=1000):
    """Q41/Q79: resumable logical-byte inventory; the result exposes only top-level names."""

    root = Path(root).resolve(strict=True)
    excluded = tuple(excluded)
    if (
        type(limit) is not int
        or limit <= 0
        or any(
            not isinstance(name, str)
            or not name
            or name.startswith("/")
            or any(part in {"", ".", ".."} for part in name.split("/"))
            for name in excluded
        )
    ):
        _inventory_reject(root, "inventory bound or volatile-entry declaration is invalid")
    top = {p.name: "directory" if p.is_dir() and not p.is_symlink() else
           "file" if p.is_file() and not p.is_symlink() else "link" if p.is_symlink() else "special"
           for p in sorted(root.iterdir()) if p.name not in excluded}
    if checkpoint is None:
        state = {"root": str(root), "device": str(root.stat().st_dev), "excluded": sorted(excluded),
                 "top": top, "pending": [[name, name] for name in reversed(top)],
                 "bytes": dict.fromkeys(top, 0), "visited": 0}
    else:
        state = copy.deepcopy(checkpoint)
        if (state["root"] != str(root) or state["device"] != str(root.stat().st_dev)
                or state["excluded"] != sorted(excluded) or state["top"] != top):
            _inventory_reject(root, "inventory identity or top-level entries changed during traversal")
    for _ in range(limit):
        if not state["pending"]:
            break
        relative, owner = state["pending"].pop()
        path = root / relative
        if Path(relative).is_absolute() or '..' in Path(relative).parts:
            _inventory_reject(root, "inventory checkpoint escapes its root")
        if any(relative == name or relative.startswith(name + "/") for name in excluded):
            continue
        metadata = path.lstat()
        if stat.S_ISDIR(metadata.st_mode):
            state["pending"].extend([[p.relative_to(root).as_posix(), owner]
                                     for p in sorted(path.iterdir(), reverse=True)])
        elif stat.S_ISREG(metadata.st_mode):
            state["bytes"][owner] += metadata.st_size
        state["visited"] += 1
    result = None if state["pending"] else {name: {"type": kind, "logical_bytes": state["bytes"][name]}
                                           for name, kind in top.items()}
    return {"checkpoint": state, "inventory": result, "status": "NOT_RUN" if result is None else "PASS"}


def compare_inventory(before, after):
    """Reject an inventory change outside the declared Cassette root."""

    if before != after:
        _inventory_reject("protected-inventory", "protected top-level names, types or logical byte totals changed")


def _capacity_reject(
    operation_id: str,
    detail: str,
    code: str = "CAPACITY_EXCEEDED",
    retryability: str = "terminal",
) -> None:
    raise CassetteError(
        code=code,
        object_id=f"operation:{operation_id}",
        failed_invariant="Q53: exact next-transition claim before transfer or mutation",
        retryability=retryability,
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
        value = _capacity_value("transition byte field", value, operation_id)
        if value > _MAX_UNSIGNED_BYTES - total:
            _capacity_reject(operation_id, "capacity arithmetic exceeds unsigned 64-bit bytes")
        total += value
    return total


def _capacity_claim_key(transition: CapacityTransition) -> tuple[str, str]:
    """Return the single ledger key for one operation boundary."""

    return transition.operation_id, transition.boundary_id


def _record_capacity_observation(
    claim: CapacityClaim, available: int, state: str
) -> int:
    """Append one checked available-byte observation to a claim."""

    available = _capacity_value(
        "allocatable bytes", available, claim.transition.operation_id
    )
    object.__setattr__(claim, "observations", (*claim.observations, available))
    object.__setattr__(claim, "history", (*claim.history, state))
    return available


def _observe_capacity(claim: CapacityClaim, state: str) -> int:
    """Measure physical free bytes; claims coordinate Cassette writers but do not reserve the filesystem."""

    if not isinstance(claim.coordinator, CapacityCoordinator):
        _capacity_reject(
            claim.transition.operation_id,
            "claim lacks the concrete store-owned capacity coordinator",
            "INVALID_REQUEST",
        )
    return _record_capacity_observation(
        claim,
        claim.coordinator._available(claim, claim.transition.operation_id),
        state,
    )


def _release_claim_bytes(claim: CapacityClaim) -> None:
    """Release only this transition's Cassette coordination claim."""

    claim.coordinator._release(claim)


def _pause_claim(claim: CapacityClaim, reason: str) -> CapacityClaim:
    """Recover exactly the prior or committed-child boundary, then pause this transition."""

    if claim.state == "PAUSED_RECOVERABLE":
        return claim
    if claim.state != "ACTIVE":
        _capacity_reject(
            claim.transition.operation_id, "only an active claim can pause", "INVALID_REQUEST"
        )
    recovered = claim.coordinator._recover(claim)
    if recovered is not True:
        _capacity_reject(
            claim.transition.operation_id, "boundary recovery did not select parent or committed child", "ROOT_INVALID"
        )
    _release_claim_bytes(claim)
    object.__setattr__(claim, "state", "PAUSED_RECOVERABLE")
    object.__setattr__(claim, "history", (*claim.history, "PAUSED_RECOVERABLE"))
    return claim


def claim_next_transition(
    transition: CapacityTransition,
    *,
    coordinator: CapacityCoordinator,
) -> CapacityClaim:
    """Measure, atomically coordinate, and remeasure one exact next Q53 transition."""

    if not isinstance(transition, CapacityTransition):
        _capacity_reject("unidentified", "transition must be CapacityTransition", "INVALID_REQUEST")
    if not isinstance(coordinator, CapacityCoordinator):
        _capacity_reject(
            transition.operation_id,
            "the concrete store-owned CapacityCoordinator is required",
            "INVALID_REQUEST",
        )
    claim = CapacityClaim(transition, coordinator)
    if not coordinator._activate(claim):
        return claim
    if _observe_capacity(claim, "MEASURE") < transition.total_bytes:
        return _pause_claim(claim, "post-claim capacity loss")
    return claim


def observe_claim_before_write(claim: CapacityClaim) -> CapacityClaim:
    """Remeasure immediately before one declared write or pause at its committed boundary."""

    active = _active_claim(claim, claim.transition.operation_id)
    if active.writes_started >= active.transition.declared_writes:
        _capacity_reject(
            active.transition.operation_id, "write exceeds the declared next transition", "INVALID_REQUEST"
        )
    remaining_bytes = _capacity_sum(
        active.transition.write_bytes[active.writes_started:],
        active.transition.operation_id,
    )
    if _observe_capacity(active, "MEASURE") < remaining_bytes:
        _pause_claim(active, "pre-write capacity loss")
        _capacity_reject(
            active.transition.operation_id,
            f"capacity fell below the remaining {remaining_bytes}-byte transition before write",
            retryability="retryable",
        )
    object.__setattr__(active, "writes_started", active.writes_started + 1)
    object.__setattr__(active, "history", (*active.history, "EXECUTE"))
    return active


def execute_claimed_write(claim: CapacityClaim, write: Callable[[], object]) -> object:
    """Execute one observed write and turn ENOSPC into a recoverable same-boundary pause."""

    if not callable(write):
        _capacity_reject(claim.transition.operation_id, "write must be callable", "INVALID_REQUEST")
    observe_claim_before_write(claim)
    try:
        return write()
    except OSError as error:
        if error.errno != errno.ENOSPC:
            raise
        _pause_claim(claim, "ENOSPC during declared write")
        _capacity_reject(
            claim.transition.operation_id, "ENOSPC during declared write", retryability="retryable"
        )


def _run_claimed_transition(claim: CapacityClaim, mutation: Callable[[], object]) -> object:
    """Execute one store mutation under its claim and close it only after its durable boundary."""

    if isinstance(claim, CapacityClaim) and claim.state == "PAUSED_RECOVERABLE":
        _capacity_reject(
            claim.transition.operation_id,
            f"next transition {claim.transition.boundary_id!r} has no active capacity claim",
            retryability="retryable",
        )
    try:
        result = execute_claimed_write(claim, mutation)
    except Exception:
        if isinstance(claim, CapacityClaim) and claim.active:
            _pause_claim(claim, "store mutation did not reach its durable boundary")
        raise
    complete_capacity_claim(claim)
    return result


def _run_claimed_writes(
    controller: CapacityCoordinator,
    transition: CapacityTransition,
    mutation: Callable[[CapacityClaim], object],
) -> object:
    """Run each declared physical write, then release only at the durable boundary."""

    claim = controller(transition)
    if not claim.active:
        _capacity_reject(
            transition.operation_id,
            f"next transition {transition.boundary_id!r} needs {transition.total_bytes} available bytes",
            retryability="retryable",
        )
    try:
        result = mutation(claim)
    except Exception as error:
        if claim.active:
            _pause_claim(claim, "store mutation did not reach its durable boundary")
        if isinstance(error, OSError) and error.errno == errno.ENOSPC:
            _capacity_reject(
                transition.operation_id,
                "ENOSPC before the declared durable boundary",
                retryability="retryable",
            )
        raise
    complete_capacity_claim(claim)
    return result


def _claimed_store_write(
    controller: CapacityTransitionController,
    operation_id: str,
    boundary_id: str,
    *,
    payload_bytes: int = 0,
    journal_bytes: int = 0,
    index_bytes: int = 0,
    root_bytes: int = 0,
    pointer_bytes: int = 0,
    recovery_bytes: int = 0,
    write: Callable[[], object],
) -> object:
    """Claim and complete one store-owned durable write boundary."""

    if not isinstance(controller, CapacityCoordinator):
        _capacity_reject(
            operation_id,
            "the concrete store-owned CapacityCoordinator is required",
            "INVALID_REQUEST",
        )
    transition = CapacityTransition(
        operation_id=operation_id,
        boundary_id=boundary_id,
        payload_bytes=payload_bytes,
        journal_bytes=journal_bytes,
        index_bytes=index_bytes,
        root_bytes=root_bytes,
        pointer_bytes=pointer_bytes,
        recovery_bytes=recovery_bytes,
    )
    return _run_claimed_writes(
        controller,
        transition,
        lambda claim: execute_claimed_write(claim, write),
    )


def _claimed_directories(
    controller: CapacityCoordinator,
    operation_id: str,
    boundary_id: str,
    path: Path,
    object_id: str,
) -> None:
    """Create each missing directory as its own observed zero-payload mutation."""

    missing = _missing_directories(path)
    if not missing:
        return
    transition = CapacityTransition(
        operation_id,
        boundary_id,
        declared_writes=len(missing),
        write_bytes=(0,) * len(missing),
    )

    def create(claim: CapacityClaim) -> None:
        for directory in missing:
            execute_claimed_write(claim, directory.mkdir)
            _sync_directory(directory.parent, object_id)

    _run_claimed_writes(controller, transition, create)


def complete_capacity_claim(claim: CapacityClaim) -> CapacityClaim:
    """Observe after the durable boundary, then release exactly this coordination claim."""

    active = _active_claim(claim, claim.transition.operation_id)
    if active.writes_started != active.transition.declared_writes:
        _capacity_reject(
            active.transition.operation_id, "durable boundary has undeclared writes remaining", "INVALID_REQUEST"
        )
    object.__setattr__(active, "history", (*active.history, "DURABLE_BOUNDARY"))
    try:
        _observe_capacity(active, "OBSERVE")
    finally:
        _release_claim_bytes(active)
        object.__setattr__(active, "state", "COMPLETED")
    return active


def pause_capacity_claim(claim: CapacityClaim, reason: str) -> CapacityClaim:
    """Pause an active transition only after exact same-boundary recovery."""

    if not isinstance(reason, str) or not reason:
        _capacity_reject(claim.transition.operation_id, "pause reason must be nonempty text", "INVALID_REQUEST")
    return _pause_claim(_active_claim(claim, claim.transition.operation_id), reason)


def resume_capacity_claim(
    paused_claim: CapacityClaim,
) -> CapacityClaim:
    """Retry only the paused operation's exact same transition and boundary."""

    if not isinstance(paused_claim, CapacityClaim) or paused_claim.state != "PAUSED_RECOVERABLE":
        _capacity_reject("resume", "a paused CapacityClaim is required", "INVALID_REQUEST")
    resumed = claim_next_transition(
        paused_claim.transition,
        coordinator=paused_claim.coordinator,
    )
    object.__setattr__(resumed, "history", (*paused_claim.history, "RESUME", *resumed.history))
    return resumed


def grant_transfer_extent(
    cartridge: str | Path,
    operation_id: str,
    extent_id: str,
    length: int,
    *,
    capacity_controller: CapacityCoordinator | None = None,
) -> TransferExtent:
    """Create one sparse transfer extent without treating its logical size as reserved space."""

    if (
        not isinstance(operation_id, str)
        or _TRANSACTION_ID.fullmatch(operation_id) is None
        or not isinstance(extent_id, str)
        or _TRANSACTION_ID.fullmatch(extent_id) is None
        or type(length) is not int
        or not 0 <= length <= 2**63 - 1
    ):
        _capacity_reject(
            str(operation_id),
            "transfer extent requires valid operation and extent IDs plus a signed 64-bit length",
            "INVALID_REQUEST",
        )
    cartridge = Path(cartridge)
    capacity_controller = _capacity_coordinator(
        cartridge, capacity_controller, operation_id
    )
    directories = []
    descriptor = None
    try:
        directories.append(os.open(cartridge, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW))
        for name in ("transfers", operation_id):
            parent_fd = directories[-1]
            try:
                directory_fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)
            except FileNotFoundError:
                def create_directory(claim: CapacityClaim) -> None:
                    execute_claimed_write(claim, lambda: os.mkdir(name, mode=0o700, dir_fd=parent_fd))
                    os.fsync(parent_fd)

                _run_claimed_writes(capacity_controller, CapacityTransition(
                    operation_id, f"transfer-directory:{name}", declared_writes=1, write_bytes=(0,),
                ), create_directory)
                directory_fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)
            directories.append(directory_fd)
        directory_fd = directories[-1]
        filename = f"{extent_id}.extent"
        flags = os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK
        try:
            descriptor = os.open(filename, flags, dir_fd=directory_fd)
        except FileNotFoundError:
            def create(claim: CapacityClaim) -> int:
                created = execute_claimed_write(claim, lambda: os.open(
                    filename, flags | os.O_CREAT | os.O_EXCL, 0o600, dir_fd=directory_fd,
                ))
                try:
                    def size_and_sync() -> None:
                        os.ftruncate(created, length)
                        os.fsync(created)
                        command = getattr(fcntl, "F_FULLFSYNC", None)
                        if command is not None:
                            fcntl.fcntl(created, command)

                    execute_claimed_write(claim, size_and_sync)
                    os.fsync(directory_fd)
                    return created
                except Exception:
                    os.close(created)
                    os.unlink(filename, dir_fd=directory_fd)
                    raise

            descriptor = _run_claimed_writes(capacity_controller, CapacityTransition(
                operation_id, f"transfer-extent:{extent_id}", declared_writes=2, write_bytes=(0, 0),
            ), create)
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            _capacity_reject(operation_id, "transfer extent must be one owned regular file", "CONTAINMENT_REJECTED")
        if metadata.st_size != length:
            _capacity_reject(operation_id, f"existing transfer extent {extent_id!r} has another shape", "INVALID_REQUEST")
        extent = TransferExtent(descriptor, 0, length, operation_id)
        descriptor = None
        return extent
    except OSError as error:
        _capacity_reject(
            operation_id,
            f"transfer extent {extent_id!r} could not be opened within its cartridge: {error}",
            "CONTAINMENT_REJECTED" if error.errno in {errno.ELOOP, errno.ENOTDIR} else "CARTRIDGE_DISCONNECTED",
        )
    finally:
        if descriptor is not None:
            os.close(descriptor)
        for directory_fd in reversed(directories):
            os.close(directory_fd)


def _active_claim(claim: CapacityClaim, operation_id: str) -> CapacityClaim:
    if (not isinstance(claim, CapacityClaim) or not claim.active
            or claim.transition.operation_id != operation_id):
        _capacity_reject(operation_id, "an active claim for this operation is required", "INVALID_REQUEST")
    return claim


def is_reclaimable_object(candidate: ReclaimableObject) -> bool:
    """Return true only for the narrow Q53 deletion set."""

    if not isinstance(candidate, ReclaimableObject):
        _capacity_reject("reclaim", "candidate must be ReclaimableObject", "INVALID_REQUEST")
    return (
        candidate.cassette_owned
        and not candidate.pinned
        and not candidate.reachable_from_retained_root
        and not candidate.rollback_retained
        and candidate.retention_class in {"TEMPORARY", "REPRODUCIBLE"}
        and not candidate.active_claim_reference
        and not candidate.active_transaction_reference
        and not candidate.active_journal_reference
    )


def select_reclaimable_objects(candidates: tuple[ReclaimableObject, ...]) -> tuple[ReclaimableObject, ...]:
    """Select only Q53-eligible objects; this function performs no deletion."""

    if not isinstance(candidates, tuple):
        _capacity_reject("reclaim", "candidates must be a tuple", "INVALID_REQUEST")
    return tuple(candidate for candidate in candidates if is_reclaimable_object(candidate))


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


def git_blob_sha256(payload: bytes, expected_blob: str, object_id: str) -> str:
    """Q9/Q51: verify a Git blob before deriving its resumable transfer digest."""
    header = f"blob {len(payload)}\0".encode("ascii")
    if hashlib.sha1(header + payload).hexdigest() != expected_blob:
        raise CassetteError("SOURCE_REVISION_CHANGED", object_id,
                            "Q9: Git metadata bytes must match their immutable blob", "terminal",
                            "source bytes differ from the pinned Git blob")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


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
        wire_shape = tuple(
            scalar("<Q", f"GGUF tensor {name!r} dimension {dimension}")
            for dimension in range(dimensions)
        )
        tensor_type = scalar("<I", f"GGUF tensor {name!r} type")
        if tensor_type not in _GGUF_TENSOR_TYPES:
            _q57_reject(object_id, f"GGUF tensor {name!r} uses unsupported type {tensor_type}")
        offset = scalar("<Q", f"GGUF tensor {name!r} offset")
        dtype, block_elements, block_bytes = _GGUF_TENSOR_TYPES[tensor_type]
        elements = 1
        for dimension in wire_shape:
            if dimension > _MAX_UNSIGNED_BYTES // max(elements, 1):
                _q57_reject(object_id, f"GGUF tensor {name!r} element count overflows")
            elements *= dimension
        if elements and (
            not wire_shape
            or wire_shape[0] % block_elements
            or elements % block_elements
        ):
            _q57_reject(object_id, f"GGUF tensor {name!r} shape does not align to its block type")
        length = elements // block_elements * block_bytes if elements else 0
        tensor_rows.append((name, dtype, tuple(reversed(wire_shape)), offset, offset + length))

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
    export_sidecar = metadata.get("cassette.export.v1")
    if isinstance(export_sidecar, str):
        summary["cassette.export.v1"] = export_sidecar
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
        if error.errno == errno.ENOSPC:
            raise
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
        if error.errno == errno.ENOSPC:
            raise error
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
    *,
    capacity_controller: CapacityCoordinator | None = None,
    operation_id: str | None = None,
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
    cartridge = Path(cartridge)
    operation_id = operation_id or f"conversion-{target_name}"
    capacity_controller = _capacity_coordinator(
        cartridge, capacity_controller, operation_id
    )
    try:
        chunks = tuple(growth_chunks)
    except TypeError:
        _q57_reject(object_id, "growth chunks must be iterable", "INVALID_REQUEST")
    if target_size <= source_size and chunks:
        _q57_reject(object_id, "identity and shrink transforms cannot carry growth chunks")
    if target_size > source_size:
        if any(
            not isinstance(chunk, bytes) or not 0 < len(chunk) <= PAGE_BYTES
            for chunk in chunks
        ):
            _q57_reject(
                object_id,
                "growth chunks must be nonempty bytes bounded by one canonical page",
                "INVALID_REQUEST",
            )
        if sum(map(len, chunks)) != target_size - source_size:
            _q57_reject(object_id, "growth chunks do not fill the declared target extent")
    directory = cartridge / "segments"
    if not directory.exists():
        _claimed_directories(
            capacity_controller,
            operation_id,
            f"conversion:{target_name}:directory",
            directory,
            object_id,
        )
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
        if destination.stat().st_mode & 0o222:
            try:
                _claimed_store_write(
                    capacity_controller,
                    operation_id,
                    f"conversion:{target_name}:seal-existing",
                    write=lambda: destination.chmod(0o400),
                )
            except OSError as error:
                _q57_reject(
                    target_digest,
                    f"existing conversion segment cannot be made read-only: {error}",
                    "DURABILITY_UNSUPPORTED",
                )
        return destination
    if pending.exists() and exact(pending):
        transition = CapacityTransition(
            operation_id,
            f"conversion:{target_name}:resume-publication",
            declared_writes=2,
            write_bytes=(0, 0),
        )

        def publish_resumed(claim: CapacityClaim) -> Path:
            _fullsync_file(pending, object_id)
            execute_claimed_write(claim, lambda: pending.chmod(0o400))
            execute_claimed_write(claim, lambda: os.replace(pending, destination))
            _sync_directory(directory, object_id)
            return destination

        return _run_claimed_writes(capacity_controller, transition, publish_resumed)

    pending.unlink(missing_ok=True)
    write_bytes = [0, 0]
    if target_size < source_size:
        write_bytes.append(0)
    elif target_size > source_size:
        write_bytes.extend(len(chunk) for chunk in chunks)
    write_bytes.extend((0, 0))
    transition = CapacityTransition(
        operation_id,
        f"conversion:{target_name}:materialize",
        payload_bytes=sum(map(len, chunks)),
        declared_writes=len(write_bytes),
        write_bytes=tuple(write_bytes),
    )

    def materialize(claim: CapacityClaim) -> Path:
        execute_claimed_write(claim, lambda: _clone_extent(source_fd, pending, object_id))
        execute_claimed_write(claim, lambda: pending.chmod(0o600))
        if target_size < source_size:
            execute_claimed_write(claim, lambda: os.truncate(pending, target_size))
        elif target_size > source_size:
            cursor = source_size
            with pending.open("r+b", buffering=0) as handle:
                for chunk in chunks:
                    handle.seek(cursor)

                    def append(chunk=chunk) -> None:
                        if handle.write(chunk) != len(chunk):
                            raise OSError(errno.ENOSPC, "conversion growth write was incomplete")

                    execute_claimed_write(claim, append)
                    cursor += len(chunk)
        if not exact(pending):
            _q57_reject(
                object_id,
                "conversion readback differs from the declared target digest",
                "SOURCE_REVISION_CHANGED",
            )
        _fullsync_file(pending, object_id)
        execute_claimed_write(claim, lambda: pending.chmod(0o400))
        execute_claimed_write(claim, lambda: os.replace(pending, destination))
        _sync_directory(directory, object_id)
        return destination

    try:
        return _run_claimed_writes(capacity_controller, transition, materialize)
    except CassetteError:
        raise
    except OSError as error:
        _q57_reject(
            object_id,
            f"conversion extent cannot commit: {error}",
            "DURABILITY_UNSUPPORTED",
        )


def _write_segments(
    cartridge: Path,
    pages,
    *,
    capacity_controller: CapacityCoordinator | None = None,
    operation_id: str | None = None,
    boundary_id: str = "segments",
) -> tuple[PageLocation, ...]:
    """Write each content segment through one exact multi-write durable transition."""

    operation_id = operation_id or f"segments-{uuid.uuid4().hex}"
    capacity_controller = _capacity_coordinator(
        cartridge, capacity_controller, operation_id
    )
    directory = cartridge / "segments"
    if not directory.exists():
        _claimed_directories(
            capacity_controller,
            operation_id,
            f"{boundary_id}:directory",
            directory,
            boundary_id,
        )
    locations: list[PageLocation] = []
    pending: list[tuple[str, bytes, int]] = []
    segment_length = 0

    def finish() -> None:
        nonlocal pending, segment_length
        if not pending:
            return
        segment_hasher = blake3()
        for _, payload, _ in pending:
            segment_hasher.update(payload)
        segment_id = f"blake3:{segment_hasher.hexdigest()}"
        destination = directory / _content_hex(segment_id, segment_id)
        if destination.exists():
            if _file_digest(destination) != segment_id:
                _q57_reject(segment_id, "existing segment bytes do not match their name", "PAGE_CORRUPT")
        else:
            transition = CapacityTransition(
                operation_id=operation_id,
                boundary_id=f"{boundary_id}:{_content_hex(segment_id, segment_id)}",
                payload_bytes=segment_length,
                declared_writes=len(pending) + 2,
                write_bytes=(0, *tuple(len(payload) for _, payload, _ in pending), 0),
            )

            def write_segment(claim: CapacityClaim) -> None:
                temporary = None
                temporary_path = None
                try:
                    def create_temporary() -> None:
                        nonlocal temporary, temporary_path
                        temporary = tempfile.NamedTemporaryFile(
                            mode="w+b",
                            buffering=0,
                            dir=directory,
                            prefix=".pending-",
                            delete=False,
                        )
                        temporary_path = Path(temporary.name)

                    execute_claimed_write(claim, create_temporary)
                    for _, payload, _ in pending:
                        def append(payload=payload) -> None:
                            if temporary.write(payload) != len(payload):
                                raise OSError(errno.ENOSPC, "segment write was incomplete")

                        execute_claimed_write(claim, append)
                    temporary.close()
                    temporary = None
                    _fullsync_file(temporary_path, f"segment:{segment_id}")
                    execute_claimed_write(
                        claim, lambda: os.replace(temporary_path, destination)
                    )
                    temporary_path = None
                    _sync_directory(directory, f"segment:{segment_id}")
                finally:
                    if temporary is not None:
                        temporary.close()
                    if temporary_path is not None:
                        temporary_path.unlink(missing_ok=True)

            _run_claimed_writes(capacity_controller, transition, write_segment)
        locations.extend(
            PageLocation(page_digest, segment_id, offset, len(payload))
            for page_digest, payload, offset in pending
        )
        pending = []
        segment_length = 0

    for page_digest, payload in pages:
        if not isinstance(payload, bytes) or not 0 < len(payload) <= PAGE_BYTES:
            _q57_reject(str(page_digest), "content pages must contain at most 4 MiB")
        if digest_bytes(payload) != page_digest:
            _q57_reject(str(page_digest), "content page digest does not match its payload", "PAGE_CORRUPT")
        if segment_length and segment_length + len(payload) > SEGMENT_BYTES:
            finish()
        pending.append((page_digest, payload, segment_length))
        segment_length += len(payload)
    finish()
    return tuple(locations)


def _index_path(cartridge: Path, root_digest: str) -> Path:
    return cartridge / "indexes" / _content_hex(root_digest, root_digest)


def _write_index(
    cartridge: Path,
    root_digest: str,
    locations: tuple[PageLocation, ...],
    *,
    capacity_controller: CapacityCoordinator,
    operation_id: str,
    boundary_id: str,
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
    _claimed_durable_replace(
        capacity_controller,
        operation_id,
        boundary_id,
        path,
        payload,
        f"index:{root_digest}",
        "index_bytes",
    )


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
                   or item["format"] not in {"gguf", "safetensors", "json"}
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


def _cartridge_root_payload(
    material: IdentityTuple,
    identity_record: dict,
    containers: list[dict],
    tensor_maps: list[dict],
    locations: tuple[PageLocation, ...],
    plans: list[dict] | None = None,
    deltas: list[dict] | None = None,
) -> tuple[bytes, str]:
    """Return the one canonical root payload and its content identity without writing."""

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
    return payload, digest_bytes(payload)


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
    capacity_controller: CapacityTransitionController | None = None,
    operation_id: str | None = None,
    boundary_id: str | None = None,
) -> str:
    payload, root_digest = _cartridge_root_payload(
        material,
        identity_record,
        containers,
        tensor_maps,
        locations,
        plans,
        deltas,
    )
    operation_id = operation_id or f"root-{_content_hex(root_digest, root_digest)}"
    capacity_controller = _capacity_coordinator(
        cartridge, capacity_controller, operation_id
    )
    boundary = boundary_id or f"root:{root_digest}"
    indexed_locations = {location.page_digest: location for location in locations}
    index_path = _index_path(cartridge, root_digest)

    if index_path.exists() and _read_index(cartridge, root_digest) != indexed_locations:
        _q57_reject(root_digest, "existing physical page index does not match its root")
    index_write_required = not index_path.exists()

    if index_write_required:
        _write_index(
            cartridge,
            root_digest,
            locations,
            capacity_controller=capacity_controller,
            operation_id=operation_id,
            boundary_id=f"{boundary}:index",
        )
    path = cartridge / "roots" / _content_hex(root_digest, root_digest)
    if path.exists() and path.read_bytes() != payload:
        _q57_reject(root_digest, "existing root bytes do not match their name")
    root_write_required = not path.exists()

    if root_write_required:
        _claimed_durable_replace(
            capacity_controller,
            operation_id,
            f"{boundary}:root",
            path,
            payload,
            f"root:{root_digest}",
            "root_bytes",
        )
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
    capacity_controller: CapacityCoordinator | None = None,
    operation_id: str | None = None,
) -> str:
    """Import one bounded tensor-container family through the single Q57 page authority."""
    identity_record = _identity_record(material)
    identity = digest_bytes(canonical_bytes(identity_record))
    operation_id = operation_id or f"import-{_content_hex(identity, identity)}"
    capacity_controller = _capacity_coordinator(
        cartridge, capacity_controller, operation_id
    )
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

    locations = _write_segments(
        cartridge,
        unique_pages(),
        capacity_controller=capacity_controller,
        operation_id=operation_id,
        boundary_id=f"{container_format}:segments",
    )
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
        capacity_controller=capacity_controller,
        operation_id=operation_id,
        boundary_id=f"{container_format}:root",
    )


def import_safetensors(
    source: Mapping[str, str | Path],
    cartridge: str | Path,
    material: IdentityTuple,
    *,
    capacity_controller: CapacityCoordinator | None = None,
    operation_id: str | None = None,
) -> str:
    """Import SafeTensors only when their bytes prove the supplied complete Q1 material."""

    return _import_tensor_containers(
        source,
        cartridge,
        material,
        container_format="safetensors",
        parser=_safetensors_header,
        codec="raw-little-endian",
        capacity_controller=capacity_controller,
        operation_id=operation_id,
    )


def import_gguf(
    source: Mapping[str, str | Path],
    cartridge: str | Path,
    material: IdentityTuple,
    *,
    capacity_controller: CapacityCoordinator | None = None,
    operation_id: str | None = None,
) -> str:
    """Import GGUF v2/v3 only when bounded metadata and every tensor range prove Q1."""

    return _import_tensor_containers(
        source,
        cartridge,
        material,
        container_format="gguf",
        parser=_gguf_header,
        codec="gguf-block",
        capacity_controller=capacity_controller,
        operation_id=operation_id,
    )


def adopt_safetensors(
    source: Mapping[str, int],
    cartridge: str | Path,
    material: IdentityTuple,
    *,
    capacity_controller: CapacityCoordinator | None = None,
    operation_id: str | None = None,
) -> str:
    """Adopt verified SafeTensors extents as immutable pages without a second parameter copy."""

    identity_record = _identity_record(material)
    identity = model_identity(material)
    expected = {item["path"]: item for item in identity_record["artifacts"]}
    if not isinstance(source, Mapping) or set(source) != set(expected):
        _q57_reject(identity, "adoption requires every canonical SafeTensors artifact exactly once")
    cartridge = Path(cartridge)
    operation_id = operation_id or f"adopt-{_content_hex(identity, identity)}"
    capacity_controller = _capacity_coordinator(
        cartridge, capacity_controller, operation_id
    )
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
                if artifact_path.endswith(".json"):
                    data_start, data_size, metadata = 0, size, {}
                    tensors = (("asset." + artifact_path, "U8", (size,), 0, size),)
                else:
                    data_start, data_size, metadata, tensors = _safetensors_header(
                        handle, object_id, hashes
                    )
                    if any(name.startswith(("asset.", "state.")) for name, *_ in tensors):
                        _q57_reject(object_id, "source tensor uses a reserved semantic-asset or runtime-state name")
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
            capacity_controller=capacity_controller,
            operation_id=operation_id,
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
            "format": "json" if artifact_path.endswith(".json") else "safetensors",
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
        capacity_controller=capacity_controller,
        operation_id=operation_id,
        boundary_id="adopt:root",
    )


def _derived_root_inputs(
    cartridge: str | Path,
    parent_root_digest: str,
    material: IdentityTuple,
    plans: tuple[dict, ...],
) -> tuple[Path, dict, dict, list[dict], tuple[PageLocation, ...]]:
    """Validate and normalize one derived-root request without writing a cartridge byte."""

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
    locations = tuple(sorted(
        _read_index(cartridge, parent_root_digest).values(),
        key=lambda item: item.page_digest,
    ))
    return cartridge, parent, identity_record, canonical_plans, locations


def derived_root_shape(
    cartridge: str | Path,
    parent_root_digest: str,
    material: IdentityTuple,
    plans: tuple[dict, ...],
) -> dict:
    """Return the exact root-and-index bytes required before one derived candidate write."""

    _, parent, identity_record, canonical_plans, locations = _derived_root_inputs(
        cartridge, parent_root_digest, material, plans
    )
    payload, root_digest = _cartridge_root_payload(
        material,
        identity_record,
        parent["provenance"]["containers"],
        parent["tensor_maps"],
        locations,
        canonical_plans,
        parent["deltas"],
    )
    return {
        "candidate_bytes": _capacity_sum(
            (len(payload), len(locations) * _INDEX_RECORD.size), root_digest
        ),
        "root_digest": root_digest,
    }


def derive_root(
    cartridge: str | Path,
    parent_root_digest: str,
    material: IdentityTuple,
    plans: tuple[dict, ...],
    *,
    capacity_controller: CapacityTransitionController | None = None,
    operation_id: str | None = None,
    additional_pages: tuple[PageLocation, ...] = (),
) -> str:
    """Publish one child revision or same-identity plan manifest over verified existing pages."""

    cartridge, parent, identity_record, canonical_plans, locations = _derived_root_inputs(
        cartridge, parent_root_digest, material, plans
    )
    if not isinstance(additional_pages, tuple) or any(not isinstance(page, PageLocation) for page in additional_pages):
        _q57_reject(parent_root_digest, "derived content pages require exact store locations", "INVALID_REQUEST")
    for page in additional_pages:
        _read_page(cartridge, page)
    maps = {row["semantic_tensor_id"]: row for row in parent["tensor_maps"]}
    existing = {page.page_digest for page in locations}
    for page in additional_pages:
        if page.page_digest not in existing:
            name = "state.compiled." + page.page_digest.split(":")[1]
            maps[name] = TensorMap(name, (page.length,), "U8", (TensorSpan(page.page_digest, 0, page.length, 0),)).record()
    locations = tuple(sorted({page.page_digest: page for page in (*locations, *additional_pages)}.values(), key=lambda page: page.page_digest))
    return _write_cartridge_root(
        cartridge,
        material,
        identity_record,
        parent["provenance"]["containers"],
        sorted(maps.values(), key=lambda row: row["semantic_tensor_id"]),
        locations,
        canonical_plans,
        parent["deltas"],
        durable=True,
        capacity_controller=capacity_controller,
        operation_id=operation_id,
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
    capacity_controller: CapacityTransitionController | None = None,
    operation_id: str | None = None,
    boundary_id: str | None = None,
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
        capacity_controller=capacity_controller,
        operation_id=operation_id,
        boundary_id=boundary_id,
    )


def append_training_delta(
    cartridge: str | Path,
    parent_root_digest: str,
    material: IdentityTuple,
    kind: str,
    pages: tuple[bytes, ...],
    manifest_digest: str,
    *,
    capacity_controller: CapacityCoordinator | None = None,
    operation_id: str | None = None,
) -> str:
    """Append ordered immutable delta pages and publish one derived logical root."""

    cartridge = Path(cartridge)
    operation_id = operation_id or f"training-delta-{uuid.uuid4().hex}"
    capacity_controller = _capacity_coordinator(
        cartridge, capacity_controller, operation_id
    )
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
        capacity_controller=capacity_controller,
        operation_id=operation_id,
        boundary_id="training-delta:segments",
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
        capacity_controller=capacity_controller,
        operation_id=operation_id,
        boundary_id="training-delta:root",
    )


def append_staged_training_delta(
    cartridge: str | Path,
    parent_root_digest: str,
    kind: str,
    pages: tuple[PageLocation, ...],
    manifest_digest: str,
    *,
    capacity_controller: CapacityTransitionController | None = None,
    operation_id: str | None = None,
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
        capacity_controller=capacity_controller,
        operation_id=operation_id,
    )


def training_delta_shape(
    cartridge: str | Path,
    parent_root_digest: str,
    kind: str,
    pages: tuple[PageLocation, ...],
    manifest_digest: str,
) -> dict[str, int | str]:
    """Return exact root-and-index bytes before binding already staged training pages."""

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
    current = _read_index(cartridge, parent_root_digest)
    for location in pages:
        _read_page(cartridge, location)
    locations = tuple(sorted(
        {**current, **{location.page_digest: location for location in pages}}.values(),
        key=lambda location: location.page_digest,
    ))
    payload, root_digest = _cartridge_root_payload(
        child_material,
        _identity_record(child_material),
        parent["provenance"]["containers"],
        parent["tensor_maps"],
        locations,
        parent["plans"],
        deltas,
    )
    return {
        "root_bytes": len(payload),
        "index_bytes": len(locations) * _INDEX_RECORD.size,
        "root_digest": root_digest,
    }


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


def stage_training_pages(
    cartridge: str | Path,
    pages,
    *,
    capacity_controller: CapacityCoordinator | None = None,
    operation_id: str | None = None,
    boundary_id: str = "training-pages",
) -> tuple[PageLocation, ...]:
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
    operation_id = operation_id or f"training-pages-{uuid.uuid4().hex}"
    capacity_controller = _capacity_coordinator(
        cartridge, capacity_controller, operation_id
    )
    locations = _write_segments(
        cartridge,
        unique_pages(),
        capacity_controller=capacity_controller,
        operation_id=operation_id,
        boundary_id=boundary_id,
    )
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
    cartridge: str | Path,
    root_digest: str,
    ordered_page_digests: tuple[str, ...],
    *,
    capacity_controller: CapacityCoordinator | None = None,
    operation_id: str | None = None,
) -> str:
    """Rewrite every required page in a new physical order without changing the logical root."""

    cartridge = Path(cartridge)
    operation_id = operation_id or f"repack-{_content_hex(root_digest, root_digest)}"
    capacity_controller = _capacity_coordinator(
        cartridge, capacity_controller, operation_id
    )
    root = load_root(cartridge, root_digest)
    current = _read_index(cartridge, root_digest)
    required = _root_page_digests(root)
    order = tuple(ordered_page_digests)
    if len(order) != len(set(order)) or set(order) != required or set(current) != required:
        _q57_reject(root_digest, "repack order must contain every required page exactly once", "INVALID_REQUEST")
    locations = _write_segments(
        cartridge,
        ((page_digest, _read_page(cartridge, current[page_digest])) for page_digest in order),
        capacity_controller=capacity_controller,
        operation_id=operation_id,
        boundary_id="repack:segments",
    )
    _write_index(
        cartridge,
        root_digest,
        locations,
        capacity_controller=capacity_controller,
        operation_id=operation_id,
        boundary_id=f"repack:{_content_hex(root_digest, root_digest)}:index",
    )
    return root_digest


def read_tensor(cartridge: str | Path, root_digest: str, semantic_tensor_id: str,
                *, offset: int = 0, length: int | None = None) -> bytes:
    """Resolve verified Q57 spans for one tensor or one bounded byte interval."""
    cartridge = Path(cartridge)
    root = load_root(cartridge, root_digest)
    matches = [row for row in root["tensor_maps"] if row["semantic_tensor_id"] == semantic_tensor_id]
    if len(matches) != 1:
        _q57_reject(root_digest, f"semantic tensor {semantic_tensor_id!r} is absent or duplicated")
    spans = matches[0]["spans"]
    size = sum(span["length"] for span in spans)
    length = size-offset if length is None else length
    if type(offset) is not int or type(length) is not int or offset < 0 or length < 0 or offset+length > size:
        _q57_reject(root_digest, "tensor byte interval is outside its verified span map", "INVALID_REQUEST")
    locations = _read_index(cartridge, root_digest)
    output = bytearray()
    for span in spans:
        start = max(offset, span["tensor_offset"])
        end = min(offset+length, span["tensor_offset"]+span["length"])
        if end <= start:
            continue
        if start != offset+len(output) or span["page_digest"] not in locations:
            _q57_reject(root_digest, "tensor interval has a discontinuous or absent span")
        page = _read_page(cartridge, locations[span["page_digest"]])
        source = span["offset"] + start-span["tensor_offset"]
        if source+end-start > len(page):
            _q57_reject(root_digest, "tensor interval exceeds its verified content page")
        output.extend(page[source:source+end-start])
    if len(output) != length:
        _q57_reject(root_digest, "tensor interval has incomplete source coverage")
    return bytes(output)


_EXPORT_PLAN_FIELDS = frozenset({
    "version", "source_root", "source_identity", "target_schema", "mode",
    "semantic_binding", "delta_id", "adapter_rank", "adapter_scale",
})
_MANIFEST_EXPORT_PLAN_FIELDS = _EXPORT_PLAN_FIELDS | {"plan_id", "artifact_size"}
_SEALED_EXPORT_PLAN_FIELDS = _MANIFEST_EXPORT_PLAN_FIELDS | {"transition_bytes"}
_EXPORT_TARGETS = frozenset(EXPORT_TARGETS)
_EXPORT_MANIFEST_FIELDS = frozenset({
    "export_id", "plan", "artifact", "artifact_role", "parameter_authority",
    "semantic_manifest", "artifact_semantics", "exported_revision", "source_revision",
})
_EXPORT_SEMANTIC_FIELDS = frozenset({
    "version", "source_identity", "graph", "semantic_assets", "precision",
    "tensor_contracts", "ordered_deltas",
})
_EXPORT_ARTIFACT_SEMANTIC_FIELDS = frozenset({
    "version", "source_identity", "graph", "semantic_assets", "precision",
    "tensor_contracts", "ordered_deltas",
})
_GGUF_EXPORT_TYPES = {
    dtype: type_id for type_id, (dtype, _, _) in _GGUF_TENSOR_TYPES.items()
}
_MERGED_EXPORT_PRECISION = "float32-merged-adapter-v1"


def _export_semantic_manifest(
    cartridge: Path, root_digest: str, root: dict
) -> dict:
    """Bind logical tensor values without exposing physical page placement."""

    material = root["provenance"]["identity_material"]
    return {
        "version": "q10-export-semantics-v1",
        "source_identity": root["identity"],
        "graph": {
            "architecture": material["architecture"],
            "operators": root["operators"],
            "plans": root["plans"],
        },
        "semantic_assets": root["semantic_assets"],
        "precision": material["precision_scheme"],
        "tensor_contracts": [
            {
                "semantic_tensor_id": tensor["semantic_tensor_id"],
                "dtype": tensor["dtype"],
                "shape": tensor["shape"],
                "value_digest": _tensor_value_digest(cartridge, root_digest, tensor),
            }
            for tensor in root["tensor_maps"]
        ],
        "ordered_deltas": root["deltas"],
    }


def _tensor_value_digest(cartridge: Path, root_digest: str, tensor: dict) -> str:
    """Digest one logical tensor through page-bounded reads."""

    hasher = blake3()
    for payload in _tensor_chunks(cartridge, root_digest, tensor):
        hasher.update(payload)
    return f"blake3:{hasher.hexdigest()}"


def export_semantic_manifest(
    cartridge: str | Path, root_digest: str
) -> dict:
    """Return the portable Q10/Q26 sidecar only from one verified immutable root."""

    cartridge = Path(cartridge)
    return _export_semantic_manifest(
        cartridge, root_digest, load_root(cartridge, root_digest)
    )


def export_semantic_binding(cartridge: str | Path, root_digest: str) -> str:
    """Digest every graph, semantic asset, precision, tensor, and ordered-delta input."""

    cartridge = Path(cartridge)
    return digest_bytes(canonical_bytes(
        export_semantic_manifest(cartridge, root_digest)
    ))


def _adapter_export_material(
    cartridge: str | Path, root_digest: str
) -> tuple[dict, dict, dict]:
    """Load the protected adapter fields shared by portable and merged export."""

    cartridge = Path(cartridge)
    root = load_root(cartridge, root_digest)
    if not root["deltas"] or root["deltas"][-1]["kind"] != "adapter":
        _q57_reject(root_digest, "adapter export requires one terminal adapter delta", "MODEL_UNSUPPORTED")
    delta = root["deltas"][-1]
    try:
        payload = read_training_page(cartridge, root_digest, delta["manifest_digest"])
        manifest = json.loads(payload, object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        _q57_reject(root_digest, f"adapter manifest is malformed: {error}")
    if canonical_bytes(manifest) != payload or not isinstance(manifest, dict):
        _q57_reject(root_digest, "adapter manifest is not exact canonical content")
    rank = manifest.get("adapter_rank")
    scale = manifest.get("adapter_scale")
    base_rows = manifest.get("base_pages")
    delta_rows = manifest.get("delta_pages")
    if (
        manifest.get("format") != "cassette-training-v1"
        or manifest.get("tier") != "A"
        or manifest.get("parent_root") is None
        or manifest.get("parent_identity") != delta["base_identity"]
        or type(rank) is not int
        or rank <= 0
        or not isinstance(scale, str)
        or not isinstance(base_rows, list)
        or not isinstance(delta_rows, list)
        or not base_rows
        or len(base_rows) != len(delta_rows)
        or len(base_rows) > 256
    ):
        _q57_reject(root_digest, "adapter export cannot preserve an absent rank or scale", "MODEL_UNSUPPORTED")
    parent = load_root(cartridge, manifest["parent_root"])
    if (
        root["parents"] != [parent["identity"]]
        or parent["identity"] != delta["base_identity"]
        or delta["manifest_digest"] not in delta["ordered_page_digests"]
        or any(
            not isinstance(row, dict)
            or set(row) != {"parameter_id", "page_digest"}
            or row["page_digest"] not in delta["ordered_page_digests"]
            for row in delta_rows
        )
    ):
        _q57_reject(root_digest, "adapter export is detached from its direct parent or ordered pages")
    return root, delta, manifest


def adapter_export_fields(cartridge: str | Path, root_digest: str) -> tuple[str, int, str]:
    """Return the verified ordered adapter identity, rank, and scale required by Q26."""

    _, delta, manifest = _adapter_export_material(cartridge, root_digest)
    rank = manifest["adapter_rank"]
    scale = manifest["adapter_scale"]
    return delta["delta_id"], rank, scale


def _merged_tensor_specs(cartridge: Path, root_digest: str, root: dict) -> dict[str, dict]:
    """Describe the exact bounded tensors eligible for generated adapter merging."""

    observed_root, _, manifest = _adapter_export_material(cartridge, root_digest)
    parent = load_root(cartridge, manifest["parent_root"])
    if (
        observed_root != root
        or len(root["deltas"]) != 1
        or parent["deltas"]
        or manifest["adapter_rank"] != 1
        or manifest["adapter_scale"] != "1"
        or manifest.get("delta_precision") not in {"BF16", "FP32"}
    ):
        _q57_reject(
            root_digest,
            "merged export requires one direct rank-one adapter over an undeltaed parent",
            "MODEL_UNSUPPORTED",
        )
    tensor_maps = {
        tensor["semantic_tensor_id"]: tensor for tensor in root["tensor_maps"]
    }
    specs = {}
    for base, delta in zip(manifest["base_pages"], manifest["delta_pages"], strict=True):
        if (
            not isinstance(base, dict)
            or set(base) != {
                "parameter_id", "tensor_id", "page_digest", "tensor_digest", "dtype",
                "shape", "offset", "length", "codec",
            }
            or base["parameter_id"] != delta["parameter_id"]
            or base["dtype"] != "I8"
            or base["shape"] != [2, 3]
            or base["length"] != 6
            or base["tensor_id"] in specs
        ):
            _q57_reject(root_digest, "adapter merge tuple is malformed or duplicated")
        tensor = tensor_maps.get(base["tensor_id"])
        if (
            tensor is None
            or tensor["dtype"] != "I8"
            or tensor["shape"] != [2, 3]
            or tensor["spans"] != [{
                "page_digest": base["page_digest"],
                "offset": base["offset"],
                "length": 6,
                "tensor_offset": 0,
            }]
        ):
            _q57_reject(root_digest, "adapter merge tuple differs from its source tensor")
        specs[base["tensor_id"]] = {
            "semantic_tensor_id": base["tensor_id"],
            "dtype": "F32",
            "shape": [2, 3],
            "length": 24,
        }
    return specs


def _tensor_chunks(cartridge: Path, root_digest: str, tensor: dict):
    """Yield one tensor through verified canonical page spans without assembling it."""

    locations = _read_index(cartridge, root_digest)
    cursor = 0
    for span in tensor["spans"]:
        if span["tensor_offset"] != cursor or span["page_digest"] not in locations:
            _q57_reject(root_digest, f"tensor {tensor['semantic_tensor_id']!r} has a discontinuous span map")
        page = _read_page(cartridge, locations[span["page_digest"]])
        end = span["offset"] + span["length"]
        if end > len(page):
            _q57_reject(root_digest, f"tensor {tensor['semantic_tensor_id']!r} exceeds its content page")
        payload = page[span["offset"]:end]
        cursor += len(payload)
        yield payload


def _export_sidecar(plan: dict) -> str:
    return canonical_bytes({
        "plan_id": plan["plan_id"],
        "semantic_binding": plan["semantic_binding"],
        "source_identity": plan["source_identity"],
        "target_schema": plan["target_schema"],
    }).decode()


def _full_export_rows(cartridge: Path, root: dict, plan: dict) -> list[tuple]:
    merged = (
        _merged_tensor_specs(cartridge, plan["source_root"], root)
        if plan["mode"] == "merged"
        else {}
    )
    rows = []
    for tensor in sorted(root["tensor_maps"], key=lambda row: row["semantic_tensor_id"]):
        tensor_id = tensor["semantic_tensor_id"]
        if tensor_id in merged:
            spec = merged[tensor_id]
            rows.append(("merged", tensor_id, spec["dtype"], spec["shape"], spec["length"]))
        else:
            rows.append((
                "tensor",
                tensor,
                tensor["dtype"],
                tensor["shape"],
                sum(span["length"] for span in tensor["spans"]),
            ))
    if set(merged) != {
        value if kind == "merged" else value["semantic_tensor_id"]
        for kind, value, _, _, _ in rows
        if kind == "merged"
    }:
        _q57_reject(plan["source_root"], "merged export omitted one trained tensor")
    return rows


def _artifact_contract_template(cartridge: Path, root: dict, plan: dict) -> list[dict]:
    source = {
        row["semantic_tensor_id"]: row
        for row in _export_semantic_manifest(cartridge, plan["source_root"], root)["tensor_contracts"]
    }
    contracts = []
    for kind, value, dtype, shape, _ in _full_export_rows(cartridge, root, plan):
        tensor_id = value if kind == "merged" else value["semantic_tensor_id"]
        contracts.append({
            "semantic_tensor_id": tensor_id,
            "dtype": dtype,
            "shape": shape,
            "value_digest": (
                "blake3:" + "0" * 64
                if kind == "merged"
                else source[tensor_id]["value_digest"]
            ),
        })
    return contracts


def _artifact_semantics(root: dict, plan: dict, tensor_contracts: list[dict]) -> dict | None:
    if plan["mode"] == "adapter":
        return None
    source_record = root["provenance"]["identity_material"]
    return {
        "version": "q10-export-artifact-semantics-v1",
        "source_identity": root["identity"],
        "graph": {
            "architecture": source_record["architecture"],
            "operators": root["operators"],
            "plans": [],
        },
        "semantic_assets": root["semantic_assets"],
        "precision": (
            _MERGED_EXPORT_PRECISION
            if plan["mode"] == "merged"
            else source_record["precision_scheme"]
        ),
        "tensor_contracts": tensor_contracts,
        "ordered_deltas": [],
    }


def _safetensors_export_layout(
    cartridge: Path,
    root: dict,
    plan: dict,
    locations: dict[str, PageLocation],
) -> dict:
    metadata = {
        "cassette.export.v1": _export_sidecar(plan),
    }
    header: dict[str, object] = {"__metadata__": metadata}
    rows = []
    cursor = 0
    if plan["mode"] in {"full", "merged"}:
        for kind, value, dtype, shape, length in _full_export_rows(cartridge, root, plan):
            tensor_id = value if kind == "merged" else value["semantic_tensor_id"]
            header[tensor_id] = {
                "dtype": dtype,
                "shape": shape,
                "data_offsets": [cursor, cursor + length],
            }
            rows.append((kind, value, cursor, length))
            cursor += length
    else:
        delta = root["deltas"][-1]
        for ordinal, page_digest in enumerate(delta["ordered_page_digests"]):
            location = locations[page_digest]
            name = f"delta.{ordinal:08d}"
            header[name] = {
                "dtype": "U8",
                "shape": [location.length],
                "data_offsets": [cursor, cursor + location.length],
            }
            rows.append(("page", page_digest, cursor, location.length))
            cursor += location.length
    encoded = canonical_bytes(header)
    encoded += b" " * (-len(encoded) % 8)
    prefix = len(encoded).to_bytes(8, "little") + encoded
    return {"prefix": prefix, "rows": rows, "artifact_size": len(prefix) + cursor}


def _gguf_string(value: str) -> bytes:
    payload = value.encode("utf-8")
    return struct.pack("<Q", len(payload)) + payload


def _gguf_export_layout(cartridge: Path, root: dict, plan: dict) -> dict:
    tensors = _full_export_rows(cartridge, root, plan)
    metadata = (
        ("cassette.export.v1", 8, _gguf_string(_export_sidecar(plan))),
        ("general.alignment", 4, struct.pack("<I", 32)),
    )
    offsets = []
    cursor = 0
    for kind, value, dtype, shape, length in tensors:
        cursor += (-cursor) % 32
        offsets.append((kind, value, dtype, shape, cursor, length))
        cursor += length
    header = bytearray(b"GGUF" + struct.pack("<IQQ", 3, len(tensors), len(metadata)))
    for key, kind, value in metadata:
        header.extend(_gguf_string(key))
        header.extend(struct.pack("<I", kind))
        header.extend(value)
    for kind, value, dtype, shape, offset, _ in offsets:
        tensor_id = value if kind == "merged" else value["semantic_tensor_id"]
        header.extend(_gguf_string(tensor_id))
        header.extend(struct.pack("<I", len(shape)))
        for dimension in reversed(shape):
            header.extend(struct.pack("<Q", dimension))
        header.extend(struct.pack("<IQ", _GGUF_EXPORT_TYPES[dtype], offset))
    header.extend(b"\0" * (-len(header) % 32))
    return {
        "prefix": bytes(header),
        "rows": [
            (kind, value, offset, length)
            for kind, value, _, _, offset, length in offsets
        ],
        "artifact_size": len(header) + cursor,
    }


def export_shape(cartridge: str | Path, plan_body: Mapping[str, object]) -> dict:
    """Seal one export plan and report its largest exact next transition, not its total."""

    if not isinstance(plan_body, Mapping) or set(plan_body) != _EXPORT_PLAN_FIELDS:
        _q57_reject("export:plan", "export plan has an incorrect field set", "INVALID_REQUEST")
    try:
        body = json.loads(
            canonical_bytes(dict(plan_body)), object_pairs_hook=_unique_object
        )
    except (OverflowError, TypeError, ValueError) as error:
        _q57_reject(
            "export:plan", f"export plan is not bounded canonical JSON: {error}", "INVALID_REQUEST"
        )
    if body["version"] != "q26-export-v1" or body["target_schema"] not in _EXPORT_TARGETS:
        _q57_reject("export:plan", "export plan version or target schema is unsupported", "INVALID_REQUEST")
    root = load_root(cartridge, body["source_root"])
    if body["source_identity"] != root["identity"]:
        _q57_reject(body["source_root"], "export plan names another source identity", "IDENTITY_MISMATCH")
    if body["semantic_binding"] != export_semantic_binding(cartridge, body["source_root"]):
        _q57_reject(body["source_root"], "export plan drops or changes a bound model semantic", "IDENTITY_MISMATCH")
    full = body["mode"] in {"full", "merged"}
    adapter = body["mode"] == "adapter"
    if not (full or adapter) or adapter != (body["target_schema"] == "adapter-safetensors-v1"):
        _q57_reject(body["source_root"], "export mode disagrees with its target schema", "INVALID_REQUEST")
    if body["mode"] == "full" and (
        body["delta_id"] is not None
        or body["adapter_rank"] is not None
        or body["adapter_scale"] is not None
    ):
        _q57_reject(body["source_root"], "full export carries adapter-only fields", "INVALID_REQUEST")
    if body["mode"] in {"adapter", "merged"} and (
        (body["delta_id"], body["adapter_rank"], body["adapter_scale"])
        != adapter_export_fields(cartridge, body["source_root"])
    ):
        _q57_reject(body["source_root"], "adapter export or merge is detached from its ordered delta", "IDENTITY_MISMATCH")
    tensor_rows = _full_export_rows(Path(cartridge), root, body) if full else []
    if body["target_schema"] == "safetensors-v1" and any(
        dtype not in _SAFETENSORS_DTYPE_BITS for _, _, dtype, _, _ in tensor_rows
    ):
        _q57_reject(body["source_root"], "SafeTensors target cannot represent one or more dtypes", "MODEL_UNSUPPORTED")
    if body["target_schema"] == "gguf-v3" and any(
        dtype not in _GGUF_EXPORT_TYPES for _, _, dtype, _, _ in tensor_rows
    ):
        _q57_reject(body["source_root"], "GGUF target cannot represent one or more dtypes", "MODEL_UNSUPPORTED")
    if body["target_schema"] == "gguf-v3":
        for kind, value, dtype, shape, length in tensor_rows:
            tensor_id = value if kind == "merged" else value["semantic_tensor_id"]
            _, block_elements, block_bytes = _GGUF_TENSOR_TYPES[
                _GGUF_EXPORT_TYPES[dtype]
            ]
            elements = math.prod(shape)
            if (
                not shape
                or shape[-1] % block_elements
                or elements % block_elements
                or elements // block_elements * block_bytes != length
            ):
                _q57_reject(
                    body["source_root"],
                    f"GGUF target cannot encode tensor {tensor_id!r} exactly",
                    "MODEL_UNSUPPORTED",
                )
    plan = {**body, "plan_id": digest_bytes(canonical_bytes(body))}
    locations = _read_index(Path(cartridge), body["source_root"])
    layout = (
        _gguf_export_layout(Path(cartridge), root, plan)
        if body["target_schema"] == "gguf-v3"
        else _safetensors_export_layout(Path(cartridge), root, plan, locations)
    )
    sealed = {**plan, "artifact_size": layout["artifact_size"]}
    suffix = ".gguf" if body["target_schema"] == "gguf-v3" else ".safetensors"
    placeholder = {
        "path": "0" * 64 + suffix,
        "size": layout["artifact_size"],
        "digest": "sha256:" + "0" * 64,
    }
    provisional = {**sealed, "transition_bytes": 0}
    provisional_semantics = _artifact_semantics(
        root,
        provisional,
        _artifact_contract_template(Path(cartridge), root, provisional)
        if provisional["mode"] != "adapter"
        else [],
    )
    manifest_bytes = len(canonical_bytes(
        _export_manifest(
            Path(cartridge), root, provisional, placeholder, provisional_semantics
        )
    ))
    if manifest_bytes > _EXPORT_MANIFEST_BYTES:
        _q57_reject(
            body["source_root"],
            "portable export manifest exceeds its 100 MB interpretation bound",
            "MODEL_UNSUPPORTED",
        )
    return {
        **sealed,
        "transition_bytes": max(
            min(layout["artifact_size"], PAGE_BYTES), manifest_bytes
        ),
    }


def _export_plan(cartridge: Path, value: object) -> tuple[dict, dict, dict]:
    if not isinstance(value, dict) or set(value) != _SEALED_EXPORT_PLAN_FIELDS:
        _q57_reject("export:plan", "sealed export plan has an incorrect field set", "INVALID_REQUEST")
    expected = export_shape(cartridge, {name: value[name] for name in _EXPORT_PLAN_FIELDS})
    if value != expected:
        _q57_reject(value.get("plan_id", "export:plan"), "sealed export plan changed after admission", "IDENTITY_MISMATCH")
    root = load_root(cartridge, value["source_root"])
    locations = _read_index(cartridge, value["source_root"])
    layout = (
        _gguf_export_layout(cartridge, root, value)
        if value["target_schema"] == "gguf-v3"
        else _safetensors_export_layout(cartridge, root, value, locations)
    )
    return value, root, layout


def _export_chunks(
    cartridge: Path,
    root_digest: str,
    layout: dict,
    merged_tensors: Mapping[str, bytes] | None,
):
    expected_merged = {
        value for kind, value, _, _ in layout["rows"] if kind == "merged"
    }
    if (
        (not expected_merged and merged_tensors is not None)
        or (expected_merged and (
            not isinstance(merged_tensors, Mapping)
            or set(merged_tensors) != expected_merged
        ))
    ):
        _q57_reject(root_digest, "merged export tensor set differs from its sealed layout", "INVALID_REQUEST")
    for start in range(0, len(layout["prefix"]), PAGE_BYTES):
        yield layout["prefix"][start:start + PAGE_BYTES]
    cursor = 0
    locations = _read_index(cartridge, root_digest)
    for kind, value, offset, length in layout["rows"]:
        gap = offset - cursor
        while gap:
            part = min(gap, PAGE_BYTES)
            yield b"\0" * part
            gap -= part
        if kind == "tensor":
            chunks = _tensor_chunks(cartridge, root_digest, value)
        elif kind == "merged":
            payload = merged_tensors[value]
            if not isinstance(payload, bytes):
                _q57_reject(root_digest, "merged export tensor is not immutable bytes", "INVALID_REQUEST")
            chunks = (payload,)
        else:
            chunks = (_read_page(cartridge, locations[value]),)
        observed = 0
        for payload in chunks:
            observed += len(payload)
            for start in range(0, len(payload), PAGE_BYTES):
                yield payload[start:start + PAGE_BYTES]
        if observed != length:
            _q57_reject(root_digest, "exported row length changed during streaming", "PAGE_CORRUPT")
        cursor = offset + length


def _sha256_path(path: Path, object_id: str) -> tuple[int, str]:
    """Hash one artifact through bounded reads and return its exact byte count."""

    size = 0
    hasher = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            while payload := handle.read(PAGE_BYTES):
                size += len(payload)
                hasher.update(payload)
    except (OSError, ValueError) as error:
        _q57_reject(object_id, f"artifact read failed: {error}", "SOURCE_UNAVAILABLE")
    return size, f"sha256:{hasher.hexdigest()}"


def _export_artifact_contracts(
    path: Path, artifact_digest: str, target_schema: str, object_id: str
) -> list[dict]:
    """Read back every exported tensor and bind its logical value independently of layout."""

    parser = _gguf_header if target_schema == "gguf-v3" else _safetensors_header
    source_hasher = artifact_hasher(artifact_digest, object_id)
    try:
        with path.open("rb") as handle:
            data_start, _, _, tensors = parser(handle, object_id, source_hasher)
            contracts = []
            for name, dtype, shape, start, end in sorted(tensors):
                handle.seek(data_start + start)
                remaining = end - start
                value_hasher = blake3()
                while remaining:
                    payload = _read_exact(
                        handle,
                        min(PAGE_BYTES, remaining),
                        object_id,
                        f"exported tensor {name}",
                    )
                    value_hasher.update(payload)
                    remaining -= len(payload)
                contracts.append({
                    "semantic_tensor_id": name,
                    "dtype": dtype,
                    "shape": list(shape),
                    "value_digest": f"blake3:{value_hasher.hexdigest()}",
                })
    except OSError as error:
        _q57_reject(object_id, f"export artifact readback failed: {error}", "SOURCE_UNAVAILABLE")
    return contracts


def _verify_export_artifact_contracts(
    cartridge: Path,
    root: dict,
    plan: dict,
    contracts: list[dict],
) -> None:
    expected = _artifact_contract_template(cartridge, root, plan)
    merged_ids = {
        value
        for kind, value, _, _, _ in _full_export_rows(cartridge, root, plan)
        if kind == "merged"
    }
    if len(contracts) != len(expected):
        _q57_reject(plan["source_root"], "export artifact changed the tensor catalog")
    for observed, declared in zip(contracts, expected, strict=True):
        if (
            {name: observed[name] for name in ("semantic_tensor_id", "dtype", "shape")}
            != {name: declared[name] for name in ("semantic_tensor_id", "dtype", "shape")}
            or (
                observed["semantic_tensor_id"] not in merged_ids
                and observed["value_digest"] != declared["value_digest"]
            )
        ):
            _q57_reject(plan["source_root"], "export artifact changed one declared tensor semantic")


def _stream_export_file(
    cartridge: Path,
    operation_id: str,
    root_digest: str,
    plan: dict,
    layout: dict,
    merged_tensors: Mapping[str, bytes] | None,
    capacity_controller: CapacityTransitionController,
) -> tuple[Path, int, str]:
    directory = cartridge / "exports" / "artifacts"
    if not isinstance(capacity_controller, CapacityCoordinator):
        _capacity_reject(
            operation_id, "export requires the concrete capacity coordinator", "INVALID_REQUEST"
        )
    if not directory.exists():
        _claimed_directories(
            capacity_controller,
            operation_id,
            f"export:{plan['plan_id']}:artifact-directory",
            directory,
            operation_id,
        )
    pending = directory / f".{operation_id}.pending"
    hasher = hashlib.sha256()
    size = 0

    def discard_pending() -> None:
        try:
            pending.unlink(missing_ok=True)
        except OSError as error:
            _q57_reject(
                operation_id,
                f"failed export cannot discard its pending extent: {error}",
                "DURABILITY_UNSUPPORTED",
            )

    try:
        _claimed_store_write(
            capacity_controller,
            operation_id,
            f"export:{plan['plan_id']}:artifact-start",
            write=lambda: pending.open("wb").close(),
        )
        for chunk_index, payload in enumerate(
            _export_chunks(cartridge, root_digest, layout, merged_tensors)
        ):
            if not payload:
                continue

            def append(payload=payload) -> None:
                with pending.open("ab", buffering=0) as handle:
                    if handle.write(payload) != len(payload):
                        raise OSError(errno.ENOSPC, "export chunk write was incomplete")
                    os.fsync(handle.fileno())
                    command = getattr(fcntl, "F_FULLFSYNC", None)
                    if command is not None:
                        fcntl.fcntl(handle.fileno(), command)

            _claimed_store_write(
                capacity_controller,
                operation_id,
                f"export:{plan['plan_id']}:artifact-chunk-{chunk_index}",
                payload_bytes=len(payload),
                write=append,
            )
            hasher.update(payload)
            size += len(payload)
    except CassetteError:
        discard_pending()
        raise
    except OSError as error:
        discard_pending()
        if error.errno == errno.ENOSPC:
            raise
        _q57_reject(operation_id, f"export stream failed: {error}", "DURABILITY_UNSUPPORTED")
    if size != plan["artifact_size"]:
        discard_pending()
        _q57_reject(operation_id, "export stream did not fill its admitted extent")
    digest = f"sha256:{hasher.hexdigest()}"
    readback = hashlib.sha256()
    try:
        with pending.open("rb") as handle:
            while payload := handle.read(PAGE_BYTES):
                readback.update(payload)
    except OSError as error:
        discard_pending()
        _q57_reject(operation_id, f"export readback failed: {error}", "DURABILITY_UNSUPPORTED")
    if f"sha256:{readback.hexdigest()}" != digest:
        discard_pending()
        _q57_reject(operation_id, "export readback digest changed", "SOURCE_REVISION_CHANGED")
    suffix = ".gguf" if plan["target_schema"] == "gguf-v3" else ".safetensors"
    destination = directory / f"{digest.partition(':')[2]}{suffix}"
    if destination.exists():
        existing_size, existing_digest = _sha256_path(destination, digest)
        if existing_size != size or existing_digest != digest:
            discard_pending()
            _q57_reject(digest, "existing export artifact bytes changed", "SOURCE_REVISION_CHANGED")
        discard_pending()
    else:
        def publish() -> None:
            try:
                os.replace(pending, destination)
            except OSError as error:
                if error.errno == errno.ENOSPC:
                    raise
                _q57_reject(
                    operation_id,
                    f"export artifact publication failed: {error}",
                    "DURABILITY_UNSUPPORTED",
                )
            _sync_directory(directory, operation_id)

        _claimed_store_write(
            capacity_controller,
            operation_id,
            f"export:{plan['plan_id']}:artifact-publication",
            write=publish,
        )
    return destination, size, digest


def _tuple_from_record(provenance: Mapping[str, object]) -> IdentityTuple:
    record = provenance["identity_material"]
    return IdentityTuple(
        revision_kind=provenance["revision_kind"],
        source_kind=record["source_kind"],
        source_alias=provenance["source_alias"],
        canonical_locator=record["locator"],
        requested_revision=provenance["requested_revision"],
        immutable_revision=record["immutable_revision"],
        artifacts=tuple(ArtifactIdentity(**artifact) for artifact in record["artifacts"]),
        format_versions=tuple(tuple(item) for item in record["format_versions"]),
        tensor_index_digest=record["tensor_index_digest"],
        config_digest=record["config_digest"],
        architecture=record["architecture"],
        operator_set=tuple(record["operator_set"]),
        tokenizer_digest=record["tokenizer_digest"],
        processor_digest=record["processor_digest"],
        template_digest=record["template_digest"],
        precision_scheme=record["precision_scheme"],
        license_digest=record["license_digest"],
        parent_ids=tuple(record["parent_ids"]),
        transform_manifest_digest=record["transform_manifest_digest"],
    )


def _export_manifest(
    cartridge: Path,
    root: dict,
    plan: dict,
    artifact_record: dict,
    artifact_semantics: dict | None,
) -> dict:
    """Build one self-contained derivative manifest from fixed-width artifact evidence."""

    source_material, source_record = _material_from_provenance(
        root["provenance"], plan["source_root"]
    )
    semantic_manifest = _export_semantic_manifest(
        cartridge, plan["source_root"], root
    )
    if digest_bytes(canonical_bytes(semantic_manifest)) != plan["semantic_binding"]:
        _q57_reject(plan["source_root"], "export semantic sidecar changed after admission")
    format_name, format_version = (
        ("gguf", "3") if plan["target_schema"] == "gguf-v3" else ("safetensors", "1")
    )
    exported_material = IdentityTuple(
        revision_kind="exported",
        source_kind="cassette",
        source_alias=f"export:{root['identity']}",
        canonical_locator=f"cassette-export:{plan['plan_id']}",
        requested_revision=plan["source_root"],
        immutable_revision=artifact_record["digest"],
        artifacts=(ArtifactIdentity(**artifact_record),),
        format_versions=((format_name, format_version),),
        tensor_index_digest=digest_bytes(canonical_bytes(
            artifact_semantics["tensor_contracts"]
            if artifact_semantics is not None
            else root["deltas"][-1]
        )),
        config_digest=source_record["config_digest"],
        architecture=source_record["architecture"],
        operator_set=tuple(root["operators"]),
        tokenizer_digest=root["semantic_assets"]["tokenizer"],
        processor_digest=root["semantic_assets"]["processor"],
        template_digest=root["semantic_assets"]["template"],
        precision_scheme=(
            artifact_semantics["precision"]
            if artifact_semantics is not None
            else source_record["precision_scheme"]
        ),
        license_digest=source_record["license_digest"],
        parent_ids=(root["identity"],),
        transform_manifest_digest=plan["plan_id"],
    )
    manifest_plan = {name: plan[name] for name in _MANIFEST_EXPORT_PLAN_FIELDS}
    export_id = digest_bytes(canonical_bytes({
        "revision": plan["source_root"],
        "target_schema": plan["target_schema"],
        "export_transform": plan["plan_id"],
        "artifact_digests": [artifact_record],
    }))
    return {
        "export_id": export_id,
        "plan": manifest_plan,
        "artifact": artifact_record,
        "artifact_role": "DERIVATIVE_NOT_PARAMETER_AUTHORITY",
        "parameter_authority": {
            "kind": "cartridge_root", "root_digest": plan["source_root"]
        },
        "semantic_manifest": semantic_manifest,
        "artifact_semantics": artifact_semantics,
        "exported_revision": {
            "revision_kind": exported_material.revision_kind,
            "source_alias": exported_material.source_alias,
            "requested_revision": exported_material.requested_revision,
            "identity_material": _identity_record(exported_material),
        },
        "source_revision": {
            "revision_kind": source_material.revision_kind,
            "source_alias": source_material.source_alias,
            "requested_revision": source_material.requested_revision,
            "identity_material": source_record,
        },
    }


def _export_revision(
    cartridge: str | Path,
    operation_id: str,
    plan: dict,
    capacity_controller: CapacityTransitionController,
    merged_tensors: Mapping[str, bytes] | None = None,
) -> dict:
    """Stream one derivative artifact on the cartridge while retaining one root authority."""

    cartridge = Path(cartridge)
    plan, root, layout = _export_plan(cartridge, plan)
    artifact, size, artifact_digest = _stream_export_file(
        cartridge,
        operation_id,
        plan["source_root"],
        plan,
        layout,
        merged_tensors,
        capacity_controller,
    )
    artifact_record = {"path": artifact.name, "size": size, "digest": artifact_digest}
    contracts = (
        _export_artifact_contracts(
            artifact, artifact_digest, plan["target_schema"], operation_id
        )
        if plan["mode"] != "adapter"
        else []
    )
    if plan["mode"] != "adapter":
        _verify_export_artifact_contracts(cartridge, root, plan, contracts)
    manifest = _export_manifest(
        cartridge,
        root,
        plan,
        artifact_record,
        _artifact_semantics(root, plan, contracts),
    )
    export_id = manifest["export_id"]
    manifest_payload = canonical_bytes(manifest)
    if max(min(size, PAGE_BYTES), len(manifest_payload)) != plan["transition_bytes"]:
        _q57_reject(operation_id, "export transition size changed after plan sealing")
    manifests = cartridge / "exports" / "manifests"
    path = manifests / _content_hex(export_id, export_id)
    if path.exists() and path.read_bytes() != manifest_payload:
        _q57_reject(export_id, "existing export manifest bytes do not match their identity")
    if not path.exists():
        _claimed_durable_replace(
            capacity_controller,
            operation_id,
            f"export:{export_id}:manifest",
            path,
            manifest_payload,
            f"export:{export_id}",
            "payload_bytes",
        )
    return {
        "export_id": export_id,
        "artifact_digest": artifact_digest,
        "artifact_size": size,
        "manifest_size": len(manifest_payload),
        "target_schema": plan["target_schema"],
        "manifest_path": str(path.relative_to(cartridge)),
        "artifact_path": str(artifact.relative_to(cartridge)),
    }


def export_revision(
    cartridge: str | Path,
    operation_id: str,
    plan: dict,
    capacity_controller: CapacityTransitionController,
    merged_tensors: Mapping[str, bytes] | None = None,
) -> dict:
    """Export one derivative through store-owned exact durable transitions."""

    if not isinstance(capacity_controller, CapacityCoordinator):
        _capacity_reject(operation_id, "export requires a next-transition controller", "INVALID_REQUEST")
    return _export_revision(cartridge, operation_id, plan, capacity_controller, merged_tensors)


def _load_export(cartridge: Path, export_id: str) -> dict:
    path = cartridge / "exports" / "manifests" / _content_hex(export_id, export_id)
    try:
        with path.open("rb") as handle:
            payload = handle.read(_EXPORT_MANIFEST_BYTES + 1)
        if len(payload) > _EXPORT_MANIFEST_BYTES:
            _q57_reject(export_id, "export manifest exceeds its 100 MB bound")
        manifest = json.loads(payload, object_pairs_hook=_unique_object)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        _q57_reject(export_id, f"export manifest is unavailable or malformed: {error}")
    if (
        canonical_bytes(manifest) != payload
        or not isinstance(manifest, dict)
        or set(manifest) != _EXPORT_MANIFEST_FIELDS
        or manifest.get("export_id") != export_id
    ):
        _q57_reject(export_id, "export manifest is not exact canonical content")
    plan = manifest["plan"]
    if (
        not isinstance(plan, dict)
        or set(plan) != _MANIFEST_EXPORT_PLAN_FIELDS
        or type(plan["artifact_size"]) is not int
        or not 0 < plan["artifact_size"] <= _MAX_UNSIGNED_BYTES
        or any(
            not isinstance(plan[field], str)
            for field in (
                "version", "source_root", "source_identity", "target_schema", "mode",
                "semantic_binding", "plan_id",
            )
        )
    ):
        _q57_reject(export_id, "export manifest carries a malformed sealed plan")
    plan_body = {name: plan[name] for name in _EXPORT_PLAN_FIELDS}
    if (
        plan["version"] != "q26-export-v1"
        or plan["target_schema"] not in _EXPORT_TARGETS
        or plan["mode"] not in {"adapter", "full", "merged"}
        or (plan["mode"] == "adapter")
        != (plan["target_schema"] == "adapter-safetensors-v1")
        or any(
            re.fullmatch(r"blake3:[0-9a-f]{64}", plan[field]) is None
            for field in ("source_root", "source_identity", "semantic_binding", "plan_id")
        )
        or (
            plan["delta_id"] is not None
            and (
                not isinstance(plan["delta_id"], str)
                or re.fullmatch(r"blake3:[0-9a-f]{64}", plan["delta_id"]) is None
            )
        )
        or (
            plan["adapter_rank"] is not None
            and (type(plan["adapter_rank"]) is not int or plan["adapter_rank"] <= 0)
        )
        or (
            plan["adapter_scale"] is not None
            and not isinstance(plan["adapter_scale"], str)
        )
        or (
            plan["mode"] == "full"
            and any(
                plan[field] is not None
                for field in ("delta_id", "adapter_rank", "adapter_scale")
            )
        )
        or (
            plan["mode"] in {"adapter", "merged"}
            and any(
                plan[field] is None
                for field in ("delta_id", "adapter_rank", "adapter_scale")
            )
        )
        or plan["plan_id"] != digest_bytes(canonical_bytes(plan_body))
    ):
        _q57_reject(export_id, "export manifest carries a foreign or altered plan")
    semantic = manifest["semantic_manifest"]
    if (
        not isinstance(semantic, dict)
        or set(semantic) != _EXPORT_SEMANTIC_FIELDS
        or semantic["version"] != "q10-export-semantics-v1"
        or not isinstance(semantic["graph"], dict)
        or set(semantic["graph"]) != {"architecture", "operators", "plans"}
        or not isinstance(semantic["semantic_assets"], dict)
        or not isinstance(semantic["tensor_contracts"], list)
        or not isinstance(semantic["ordered_deltas"], list)
    ):
        _q57_reject(export_id, "export semantic sidecar is malformed or detached")
    try:
        semantic_digest = digest_bytes(canonical_bytes(semantic))
    except (OverflowError, TypeError, ValueError) as error:
        _q57_reject(export_id, f"export semantic sidecar is not bounded canonical JSON: {error}")
    if semantic_digest != plan["semantic_binding"]:
        _q57_reject(export_id, "export semantic sidecar is malformed or detached")
    artifact_semantics = manifest["artifact_semantics"]
    if plan["mode"] == "adapter":
        if artifact_semantics is not None:
            _q57_reject(export_id, "adapter export cannot claim standalone tensor semantics")
    elif (
        not isinstance(artifact_semantics, dict)
        or set(artifact_semantics) != _EXPORT_ARTIFACT_SEMANTIC_FIELDS
        or artifact_semantics["version"] != "q10-export-artifact-semantics-v1"
        or artifact_semantics["source_identity"] != plan["source_identity"]
        or not isinstance(artifact_semantics["graph"], dict)
        or set(artifact_semantics["graph"]) != {"architecture", "operators", "plans"}
        or not isinstance(artifact_semantics["semantic_assets"], dict)
        or not isinstance(artifact_semantics["precision"], str)
        or not artifact_semantics["precision"]
        or not isinstance(artifact_semantics["tensor_contracts"], list)
        or artifact_semantics["ordered_deltas"] != []
    ):
        _q57_reject(export_id, "full artifact semantic sidecar is malformed or detached")
    if artifact_semantics is None:
        if not semantic["ordered_deltas"] or not isinstance(semantic["ordered_deltas"][-1], dict):
            _q57_reject(export_id, "adapter export lacks one ordered delta semantic")
        exported_tensor_material = semantic["ordered_deltas"][-1]
    else:
        exported_tensor_material = artifact_semantics["tensor_contracts"]
        expected_artifact_precision = (
            _MERGED_EXPORT_PRECISION
            if plan["mode"] == "merged"
            else semantic["precision"]
        )
        if (
            artifact_semantics["graph"] != {
                "architecture": semantic["graph"]["architecture"],
                "operators": semantic["graph"]["operators"],
                "plans": [],
            }
            or artifact_semantics["semantic_assets"] != semantic["semantic_assets"]
            or artifact_semantics["precision"] != expected_artifact_precision
            or (
                plan["mode"] == "full"
                and artifact_semantics["tensor_contracts"] != semantic["tensor_contracts"]
            )
        ):
            _q57_reject(export_id, "artifact semantics change a bound graph, asset, or precision")
    artifact = manifest["artifact"]
    expected_suffix = ".gguf" if plan["target_schema"] == "gguf-v3" else ".safetensors"
    if (
        not isinstance(artifact, dict)
        or set(artifact) != {"path", "size", "digest"}
        or not isinstance(artifact["path"], str)
        or Path(artifact["path"]).name != artifact["path"]
        or not artifact["path"].endswith(expected_suffix)
        or any(ord(character) < 32 or ord(character) == 127 for character in artifact["path"])
        or type(artifact["size"]) is not int
        or artifact["size"] != plan["artifact_size"]
        or not isinstance(artifact["digest"], str)
        or re.fullmatch(r"sha256:[0-9a-f]{64}", artifact["digest"]) is None
    ):
        _q57_reject(export_id, "export artifact record is malformed or detached")
    if (
        manifest["artifact_role"] != "DERIVATIVE_NOT_PARAMETER_AUTHORITY"
        or manifest["parameter_authority"]
        != {"kind": "cartridge_root", "root_digest": plan["source_root"]}
    ):
        _q57_reject(export_id, "export manifest declares a second parameter authority")
    try:
        source_material = _tuple_from_record(manifest["source_revision"])
        exported_material = _tuple_from_record(manifest["exported_revision"])
    except (KeyError, TypeError, ValueError, CassetteError) as error:
        _q57_reject(export_id, f"export revision evidence is malformed: {error}")
    source_record = _identity_record(source_material)
    exported_record = _identity_record(exported_material)
    expected_format = (
        [["gguf", "3"]]
        if plan["target_schema"] == "gguf-v3"
        else [["safetensors", "1"]]
    )
    if (
        model_identity(source_material) != plan["source_identity"]
        or semantic["source_identity"] != plan["source_identity"]
        or semantic["graph"].get("architecture") != source_record["architecture"]
        or semantic["graph"].get("operators") != source_record["operator_set"]
        or semantic["semantic_assets"] != {
            "processor": source_record["processor_digest"],
            "template": source_record["template_digest"],
            "tokenizer": source_record["tokenizer_digest"],
        }
        or semantic["precision"] != source_record["precision_scheme"]
        or exported_record["artifacts"] != [artifact]
        or exported_material.revision_kind != "exported"
        or exported_record["source_kind"] != "cassette"
        or exported_record["locator"] != f"cassette-export:{plan['plan_id']}"
        or exported_record["immutable_revision"] != artifact["digest"]
        or exported_record["format_versions"] != expected_format
        or exported_record["tensor_index_digest"]
        != digest_bytes(canonical_bytes(exported_tensor_material))
        or exported_record["precision_scheme"] != (
            artifact_semantics["precision"]
            if artifact_semantics is not None
            else source_record["precision_scheme"]
        )
        or exported_record["parent_ids"] != [plan["source_identity"]]
        or exported_record["transform_manifest_digest"] != plan["plan_id"]
    ):
        _q57_reject(export_id, "export semantic or identity evidence contradicts its plan")
    if source_material.revision_kind == "tuned" and (
        len(source_record["parent_ids"]) != 1
        or not semantic["ordered_deltas"]
        or not isinstance(semantic["ordered_deltas"][-1], dict)
        or semantic["ordered_deltas"][-1].get("base_identity")
        != source_record["parent_ids"][0]
        or source_record["transform_manifest_digest"]
        != digest_bytes(canonical_bytes(semantic["ordered_deltas"]))
    ):
        _q57_reject(export_id, "tuned export does not bind its parent and ordered deltas")
    if (
        (plan["mode"] == "full" and semantic["ordered_deltas"])
        or (
            plan["mode"] in {"adapter", "merged"}
            and (
                source_material.revision_kind != "tuned"
                or not semantic["ordered_deltas"]
                or not isinstance(semantic["ordered_deltas"][-1], dict)
                or semantic["ordered_deltas"][-1].get("delta_id") != plan["delta_id"]
            )
        )
    ):
        _q57_reject(export_id, "export mode cannot represent its ordered delta history")
    expected = digest_bytes(canonical_bytes({
        "revision": plan["source_root"],
        "target_schema": plan["target_schema"],
        "export_transform": plan["plan_id"],
        "artifact_digests": [artifact],
    }))
    if expected != export_id:
        _q57_reject(export_id, "export identity does not bind its revision, transform, and artifact")
    return manifest


def import_export(
    source_cartridge: str | Path,
    export_id: str,
    target_cartridge: str | Path,
    *,
    base_root: str | None = None,
) -> str:
    """Re-import one verified derivative and recover its represented semantic revision."""

    source_cartridge = Path(source_cartridge)
    manifest = _load_export(source_cartridge, export_id)
    artifact_record = manifest["artifact"]
    artifact = source_cartridge / "exports" / "artifacts" / artifact_record["path"]
    observed_size, observed_digest = _sha256_path(artifact, export_id)
    if observed_size != artifact_record["size"] or observed_digest != artifact_record["digest"]:
        _q57_reject(export_id, "export artifact differs from its manifest", "SOURCE_REVISION_CHANGED")
    plan = manifest["plan"]
    if plan["mode"] in {"full", "merged"}:
        revision = manifest["exported_revision"]
        material = _tuple_from_record(revision)
        source = {artifact.name: artifact}
        imported = (
            import_gguf(source, target_cartridge, material)
            if plan["target_schema"] == "gguf-v3"
            else import_safetensors(source, target_cartridge, material)
        )
        imported_root = load_root(target_cartridge, imported)
        containers = imported_root["provenance"]["containers"]
        if (
            len(containers) != 1
            or containers[0]["metadata"].get("cassette.export.v1")
            != _export_sidecar(plan)
        ):
            _q57_reject(export_id, "full artifact is detached from its export plan")
        semantic = manifest["artifact_semantics"]
        observed_semantics = _export_semantic_manifest(
            Path(target_cartridge), imported, imported_root
        )
        if (
            observed_semantics["graph"] != semantic["graph"]
            or observed_semantics["semantic_assets"] != semantic["semantic_assets"]
            or observed_semantics["precision"] != semantic["precision"]
            or observed_semantics["tensor_contracts"] != semantic["tensor_contracts"]
            or observed_semantics["ordered_deltas"] != semantic["ordered_deltas"]
        ):
            _q57_reject(export_id, "re-imported full model lost a bound Q10/Q17 semantic")
        return imported
    if base_root is None:
        _q57_reject(export_id, "adapter import requires its exact base root", "DELTA_BASE_MISMATCH")
    base = load_root(target_cartridge, base_root)
    source_revision = manifest["source_revision"]
    child_material = _tuple_from_record(source_revision)
    if len(child_material.parent_ids) != 1 or base["identity"] != child_material.parent_ids[0]:
        _q57_reject(export_id, "adapter base identity differs from its export", "DELTA_BASE_MISMATCH")
    delta = manifest["plan"]["delta_id"]
    matches = [
        row for row in manifest["semantic_manifest"]["ordered_deltas"]
        if isinstance(row, dict) and row.get("delta_id") == delta
    ]
    if len(matches) != 1:
        _q57_reject(export_id, "adapter export names an absent ordered delta")
    delta_record = matches[0]
    semantic = manifest["semantic_manifest"]
    base_semantics = export_semantic_manifest(target_cartridge, base_root)
    if (
        base["deltas"] + [delta_record] != semantic["ordered_deltas"]
        or any(
            base_semantics[field] != semantic[field]
            for field in ("graph", "semantic_assets", "precision", "tensor_contracts")
        )
    ):
        _q57_reject(export_id, "adapter base cannot reconstruct the exported child")
    inspected = inspect_safetensors(artifact, artifact_record["digest"])
    sidecar = inspected["metadata"].get("cassette.export.v1")
    if sidecar != _export_sidecar(plan):
        _q57_reject(export_id, "adapter artifact detached from its export plan")
    data_start = inspected["data_start"]
    ordered = []
    with artifact.open("rb") as handle:
        for ordinal, tensor in enumerate(inspected["tensors"]):
            if tensor["semantic_tensor_id"] != f"delta.{ordinal:08d}":
                _q57_reject(export_id, "adapter tensors do not preserve delta order")
            handle.seek(data_start + tensor["offset"])
            ordered.append(_read_exact(handle, tensor["length"], export_id, "adapter page"))
    if [digest_bytes(payload) for payload in ordered] != delta_record["ordered_page_digests"]:
        _q57_reject(export_id, "adapter pages differ from their ordered delta identities", "PAGE_CORRUPT")
    child = append_training_delta(
        target_cartridge,
        base_root,
        child_material,
        delta_record["kind"],
        tuple(ordered),
        delta_record["manifest_digest"],
    )
    if child != plan["source_root"]:
        _q57_reject(export_id, "adapter re-import did not reconstruct the exact child root")
    if export_semantic_manifest(
        target_cartridge, child
    ) != manifest["semantic_manifest"]:
        _q57_reject(export_id, "adapter re-import lost a bound Q10/Q17 semantic")
    return child


_REVISION_DELTA_FIELDS = frozenset({
    "version", "base_root", "base_identity", "target_revision", "target_artifact",
    "replacements", "tensor_index_digest", "semantic_assets", "operators",
    "update_manifest_digest", "target_revision_record", "target_identity", "target_root",
})


def _replace_tensor_pages(tensor_maps: list[dict], replacements: Mapping[str, str]) -> list[dict]:
    return [
        {
            **tensor,
            "spans": [
                {**span, "page_digest": replacements.get(span["page_digest"], span["page_digest"])}
                for span in tensor["spans"]
            ],
        }
        for tensor in tensor_maps
    ]


def _canonical_safetensors_identity(
    cartridge: Path,
    base_root: str,
    tensor_maps: list[dict],
    replacement_payloads: Mapping[str, bytes],
) -> tuple[int, str]:
    header = {}
    cursor = 0
    for tensor in sorted(tensor_maps, key=lambda row: row["semantic_tensor_id"]):
        length = sum(span["length"] for span in tensor["spans"])
        header[tensor["semantic_tensor_id"]] = {
            "dtype": tensor["dtype"],
            "shape": tensor["shape"],
            "data_offsets": [cursor, cursor + length],
        }
        cursor += length
    encoded = canonical_bytes(header)
    encoded += b" " * (-len(encoded) % 8)
    prefix = len(encoded).to_bytes(8, "little") + encoded
    hasher = hashlib.sha256(prefix)
    locations = _read_index(cartridge, base_root)
    total = len(prefix)
    for tensor in sorted(tensor_maps, key=lambda row: row["semantic_tensor_id"]):
        tensor_offset = 0
        for span in tensor["spans"]:
            if span["tensor_offset"] != tensor_offset:
                _q57_reject(base_root, "updated tensor spans are discontinuous")
            page = replacement_payloads.get(span["page_digest"])
            if page is None:
                location = locations.get(span["page_digest"])
                if location is None:
                    _q57_reject(base_root, "updated tensor names an unavailable page", "PAGE_CORRUPT")
                page = _read_page(cartridge, location)
            end = span["offset"] + span["length"]
            if end > len(page):
                _q57_reject(base_root, "updated tensor span exceeds its page", "PAGE_CORRUPT")
            payload = page[span["offset"]:end]
            hasher.update(payload)
            tensor_offset += len(payload)
            total += len(payload)
    return total, "sha256:" + hasher.hexdigest()


def _updated_root_record(
    material: IdentityTuple,
    tensor_maps: list[dict],
    locations: tuple[PageLocation, ...],
) -> dict:
    identity_record = _identity_record(material)
    root = {
        "identity": model_identity(material),
        "parents": identity_record["parent_ids"],
        "provenance": {
            "revision_kind": material.revision_kind,
            "source_alias": material.source_alias,
            "requested_revision": material.requested_revision,
            "identity_material": identity_record,
            "containers": [{
                "path": identity_record["artifacts"][0]["path"],
                "format": "safetensors",
                "metadata": {},
            }],
        },
        "semantic_assets": {
            "processor": identity_record["processor_digest"],
            "template": identity_record["template_digest"],
            "tokenizer": identity_record["tokenizer_digest"],
        },
        "tensor_maps": tensor_maps,
        "operators": identity_record["operator_set"],
        "plans": [],
        "deltas": [],
    }
    root["integrity_root"] = _root_integrity(
        root, tuple(sorted(locations, key=lambda item: item.page_digest))
    )
    return root


def create_revision_delta(
    cartridge: str | Path,
    base_root: str,
    target_revision: str,
    replacements: Mapping[str, bytes],
) -> dict:
    """Describe one exact same-shape page update without publishing or staging any byte."""

    cartridge = Path(cartridge)
    base = load_root(cartridge, base_root)
    _digest("target_revision", target_revision, base_root)
    if not isinstance(replacements, Mapping) or not replacements:
        _q57_reject(base_root, "revision delta requires one or more replacement pages", "INVALID_REQUEST")
    index = _read_index(cartridge, base_root)
    normalized: dict[str, bytes] = {}
    rows = []
    for old_digest, payload in sorted(replacements.items()):
        _content_hex(old_digest, base_root)
        if old_digest not in index:
            _q57_reject(base_root, f"replacement base page {old_digest} is absent", "DELTA_BASE_MISMATCH")
        if not isinstance(payload, bytes) or not payload or len(payload) != index[old_digest].length:
            _q57_reject(base_root, "replacement payload must preserve one exact page length", "INVALID_REQUEST")
        new_digest = digest_bytes(payload)
        if new_digest == old_digest:
            _q57_reject(base_root, "revision delta cannot claim an unchanged replacement", "INVALID_REQUEST")
        normalized[new_digest] = payload
        rows.append({
            "old_page_digest": old_digest,
            "new_page_digest": new_digest,
            "length": len(payload),
        })
    if len(normalized) != len(rows):
        _q57_reject(base_root, "revision delta replacement pages must remain one-to-one", "INVALID_REQUEST")
    mapping = {row["old_page_digest"]: row["new_page_digest"] for row in rows}
    tensor_maps = _replace_tensor_pages(base["tensor_maps"], mapping)
    size, artifact_digest = _canonical_safetensors_identity(
        cartridge, base_root, tensor_maps, normalized
    )
    artifact = {"path": "model.safetensors", "size": size, "digest": artifact_digest}
    transform = {
        "version": "q54-page-delta-v1",
        "base_root": base_root,
        "base_identity": base["identity"],
        "target_revision": target_revision,
        "target_artifact": artifact,
        "replacements": rows,
        "tensor_index_digest": digest_bytes(canonical_bytes(tensor_maps)),
        "semantic_assets": base["semantic_assets"],
        "operators": base["operators"],
    }
    transform_digest = digest_bytes(canonical_bytes(transform))
    base_material, base_record = _material_from_provenance(base["provenance"], base_root)
    material = replace(
        base_material,
        revision_kind="updated",
        requested_revision=target_revision,
        immutable_revision=target_revision,
        artifacts=(ArtifactIdentity(**artifact),),
        format_versions=(("safetensors", "1"),),
        tensor_index_digest=transform["tensor_index_digest"],
        parent_ids=(base["identity"],),
        transform_manifest_digest=transform_digest,
    )
    lengths = {
        page_digest: location.length for page_digest, location in index.items()
    }
    lengths.update({digest: len(payload) for digest, payload in normalized.items()})
    required = {
        span["page_digest"] for tensor in tensor_maps for span in tensor["spans"]
    }
    abstract_locations = tuple(
        PageLocation(page_digest, page_digest, 0, lengths[page_digest])
        for page_digest in sorted(required)
    )
    root = _updated_root_record(material, tensor_maps, abstract_locations)
    target_root = digest_bytes(canonical_bytes(root))
    target_revision_record = {
        "revision_kind": material.revision_kind,
        "source_alias": material.source_alias,
        "requested_revision": material.requested_revision,
        "identity_material": _identity_record(material),
    }
    body = {
        **transform,
        "update_manifest_digest": transform_digest,
        "target_revision_record": target_revision_record,
        "target_identity": model_identity(material),
        "target_root": target_root,
    }
    return {"delta_digest": digest_bytes(canonical_bytes(body)), **body}


def _revision_delta_candidate(
    cartridge: str | Path,
    base_root: str,
    delta: object,
    payloads: Mapping[str, bytes],
) -> dict:
    """Recompute one Q54 candidate and its exact pre-mutation storage demand."""

    cartridge = Path(cartridge)
    if not isinstance(delta, dict) or set(delta) != _REVISION_DELTA_FIELDS | {"delta_digest"}:
        _q57_reject(base_root, "revision delta has an incorrect field set", "INVALID_REQUEST")
    body = {name: delta[name] for name in delta if name != "delta_digest"}
    if delta["delta_digest"] != digest_bytes(canonical_bytes(body)):
        _q57_reject(base_root, "declared revision-delta digest does not match its content", "PAGE_CORRUPT")
    if base_root != delta["base_root"]:
        _q57_reject(base_root, "revision delta names another base root", "DELTA_BASE_MISMATCH")
    base = load_root(cartridge, base_root)
    if base["identity"] != delta["base_identity"]:
        _q57_reject(base_root, "revision delta names another base identity", "DELTA_BASE_MISMATCH")
    if not isinstance(payloads, Mapping):
        _q57_reject(base_root, "revision delta payloads must be a digest map", "INVALID_REQUEST")
    expected = {row["new_page_digest"] for row in delta["replacements"]}
    if set(payloads) != expected:
        _q57_reject(base_root, "revision delta payload set is incomplete", "SOURCE_UNAVAILABLE")
    old_to_payload = {}
    for row in delta["replacements"]:
        payload = payloads[row["new_page_digest"]]
        if (
            not isinstance(payload, bytes)
            or len(payload) != row["length"]
            or digest_bytes(payload) != row["new_page_digest"]
        ):
            _q57_reject(row["new_page_digest"], "revision delta payload is corrupt", "PAGE_CORRUPT")
        old_to_payload[row["old_page_digest"]] = payload
    rebuilt = create_revision_delta(
        cartridge, base_root, delta["target_revision"], old_to_payload
    )
    if rebuilt != delta:
        _q57_reject(base_root, "revision delta does not reconstruct its declared target", "IDENTITY_MISMATCH")
    index = _read_index(cartridge, base_root)
    additions = []
    for digest in sorted(expected):
        if digest in index:
            _read_page(cartridge, index[digest])
        else:
            additions.append((digest, payloads[digest]))
    mapping = {
        row["old_page_digest"]: row["new_page_digest"] for row in delta["replacements"]
    }
    tensor_maps = _replace_tensor_pages(base["tensor_maps"], mapping)
    required = {
        span["page_digest"] for tensor in tensor_maps for span in tensor["spans"]
    }
    material = _tuple_from_record(delta["target_revision_record"])
    planned = {}
    segment_payload = bytearray()
    segment_rows = []

    def finish_segment() -> None:
        if not segment_rows:
            return
        segment_id = digest_bytes(bytes(segment_payload))
        planned.update({
            digest: PageLocation(digest, segment_id, offset, length)
            for digest, offset, length in segment_rows
        })
        segment_payload.clear()
        segment_rows.clear()

    for digest, payload in additions:
        if segment_payload and len(segment_payload) + len(payload) > SEGMENT_BYTES:
            finish_segment()
        segment_rows.append((digest, len(segment_payload), len(payload)))
        segment_payload.extend(payload)
    finish_segment()
    abstract = {**index, **planned}
    candidate_root = _updated_root_record(
        material,
        tensor_maps,
        tuple(sorted((abstract[digest] for digest in required), key=lambda row: row.page_digest)),
    )
    if (
        digest_bytes(canonical_bytes(candidate_root)) != delta["target_root"]
        or candidate_root["identity"] != delta["target_identity"]
    ):
        _q57_reject(base_root, "revision delta produced another target", "IDENTITY_MISMATCH")
    stage_bytes = _capacity_sum((
        sum(len(payload) for _, payload in additions),
        len(required) * _INDEX_RECORD.size,
        len(canonical_bytes(candidate_root)),
    ), base_root)
    return {
        "additions": tuple(additions),
        "base_index": index,
        "material": material,
        "locations": tuple(sorted(
            (abstract[digest] for digest in required), key=lambda row: row.page_digest
        )),
        "root": candidate_root,
        "required": required,
        "stage_bytes": stage_bytes,
        "tensor_maps": tensor_maps,
    }


def _revision_delta_demand(
    cartridge: Path,
    operation_id: str,
    base_root: str,
    target_root: str,
    candidate: dict,
) -> dict:
    publication_bytes = _generation_publication_bytes(
        cartridge,
        operation_id,
        target_root,
        candidate["root"],
        candidate["locations"],
        base_root,
    )
    return {
        "candidate_bytes": candidate["stage_bytes"],
        "publication_bytes": publication_bytes,
    }


def revision_delta_shape(
    cartridge: str | Path,
    operation_id: str,
    base_root: str,
    delta: object,
    payloads: Mapping[str, bytes],
) -> dict:
    """Return two exact consecutive Q53 transitions without claiming either one."""

    cartridge = Path(cartridge)
    candidate = _revision_delta_candidate(cartridge, base_root, delta, payloads)
    return _revision_delta_demand(
        cartridge, operation_id, base_root, delta["target_root"], candidate
    )


def _apply_revision_delta(
    cartridge: str | Path,
    operation_id: str,
    base_root: str,
    delta: object,
    payloads: Mapping[str, bytes],
    capacity_controller: CapacityTransitionController,
) -> str:
    """Verify, admit, stage, and return one exact unpublished Q54 target revision."""

    cartridge = Path(cartridge)
    candidate = _revision_delta_candidate(cartridge, base_root, delta, payloads)
    new_locations = _write_segments(
        cartridge,
        candidate["additions"],
        capacity_controller=capacity_controller,
        operation_id=operation_id,
        boundary_id=f"revision-delta:{delta['target_root']}:segments",
    )
    available = {
        **candidate["base_index"],
        **{row.page_digest: row for row in new_locations},
    }
    root_digest = _write_cartridge_root(
        cartridge,
        candidate["material"],
        _identity_record(candidate["material"]),
        [{"path": delta["target_artifact"]["path"], "format": "safetensors", "metadata": {}}],
        candidate["tensor_maps"],
        tuple(sorted(
            (available[digest] for digest in candidate["required"]),
            key=lambda row: row.page_digest,
        )),
        durable=True,
        capacity_controller=capacity_controller,
        operation_id=operation_id,
        boundary_id=f"revision-delta:{delta['target_root']}",
    )
    if root_digest != delta["target_root"] or load_root(cartridge, root_digest)["identity"] != delta["target_identity"]:
        _q57_reject(base_root, "revision delta produced another target", "IDENTITY_MISMATCH")
    return root_digest


def apply_revision_delta(
    cartridge: str | Path,
    operation_id: str,
    base_root: str,
    delta: object,
    payloads: Mapping[str, bytes],
    capacity_controller: CapacityTransitionController,
) -> str:
    """Apply one revision delta through store-owned exact durable transitions."""

    if not isinstance(capacity_controller, CapacityCoordinator):
        _capacity_reject(operation_id, "revision delta requires a next-transition controller", "INVALID_REQUEST")
    return _apply_revision_delta(
        cartridge, operation_id, base_root, delta, payloads, capacity_controller
    )


def _root_catalog(cartridge: Path) -> dict[str, dict]:
    directory = cartridge / "roots"
    if not directory.exists():
        return {}
    catalog = {}
    for path in sorted(directory.iterdir()):
        if path.name.startswith("."):
            continue
        if not path.is_file() or len(path.name) != 64 or any(character not in _HEX for character in path.name):
            _q57_reject(f"root:{path.name}", "root directory contains an unknown object")
        root_digest = f"blake3:{path.name}"
        catalog[root_digest] = load_root(cartridge, root_digest)
    return catalog


def revision_reachability(cartridge: str | Path, target: str) -> dict:
    """Recompute the exact immutable-root reachability proof required before Q6 removal."""

    cartridge = Path(cartridge)
    _content_hex(target, "revision:remove")
    catalog = _root_catalog(cartridge)
    if target in catalog:
        target_root = target
    else:
        matches = sorted(digest for digest, root in catalog.items() if root["identity"] == target)
        if len(matches) != 1:
            detail = "revision identity is ambiguous" if matches else "revision is absent"
            _q57_reject(target, detail, "INVALID_REQUEST")
        target_root = matches[0]
    identities: dict[str, list[str]] = {}
    for root_digest, root in catalog.items():
        identities.setdefault(root["identity"], []).append(root_digest)
    generation_roots = sorted({pin.root_digest for pin in _valid_generations(cartridge, True)})
    reachable = set(generation_roots)
    frontier = list(generation_roots)
    while frontier:
        root_digest = frontier.pop()
        for parent_identity in catalog[root_digest]["parents"]:
            for parent_root in identities.get(parent_identity, ()):
                if parent_root not in reachable:
                    reachable.add(parent_root)
                    frontier.append(parent_root)
    target_index = _read_index(cartridge, target_root)
    other_segments = {
        location.segment_id
        for root_digest in catalog
        if root_digest != target_root
        for location in _read_index(cartridge, root_digest).values()
    }
    unique_segments = sorted({
        location.segment_id for location in target_index.values()
    } - other_segments)
    paths = [
        f"roots/{_content_hex(target_root, target_root)}",
        f"indexes/{_content_hex(target_root, target_root)}",
        *[f"segments/{_content_hex(segment, segment)}" for segment in unique_segments],
    ]
    target_repair_replica = _repair_manifest_replica_path(cartridge, target_root)
    target_repair_primary = _repair_manifest_path(cartridge, target_root)
    if target_repair_replica.exists() or target_repair_primary.exists():
        target_repair, *_ = _repair_record(cartridge, target_root)
        target_objects = {
            target_root,
            target_repair["index_digest"],
            *[stripe["parity_digest"] for stripe in target_repair["stripes"]],
        }
        shared_objects = set()
        for other_root in catalog:
            if other_root == target_root:
                continue
            replica = _repair_manifest_replica_path(cartridge, other_root)
            primary = _repair_manifest_path(cartridge, other_root)
            if not replica.exists() and not primary.exists():
                continue
            other_repair, *_ = _repair_record(cartridge, other_root)
            shared_objects.update({
                other_root,
                other_repair["index_digest"],
                *[stripe["parity_digest"] for stripe in other_repair["stripes"]],
            })
        paths.extend((
            str(target_repair_primary.relative_to(cartridge)),
            str(target_repair_replica.relative_to(cartridge)),
            *[
                str(_repair_object_path(cartridge, digest).relative_to(cartridge))
                for digest in sorted(target_objects - shared_objects)
            ],
        ))
    catalog_record = [
        {"root_digest": digest, "identity": root["identity"], "parents": root["parents"]}
        for digest, root in sorted(catalog.items())
    ]
    body = {
        "version": "q6-reachability-v1",
        "target_root": target_root,
        "target_identity": catalog[target_root]["identity"],
        "current_root": None if not generation_roots else max(
            _valid_generations(cartridge, True), key=lambda pin: pin.generation
        ).root_digest,
        "generation_roots": generation_roots,
        "reachable_roots": sorted(reachable),
        "catalog_digest": digest_bytes(canonical_bytes(catalog_record)),
        "removable_paths": paths,
    }
    return {**body, "reachability_digest": digest_bytes(canonical_bytes(body))}


def _finish_revision_removal(cartridge: Path, tombstone: Path, record: dict) -> dict:
    root_path = f"roots/{_content_hex(record['target_root'], record['target_root'])}"
    paths = record["removable_paths"]
    if not isinstance(paths, list) or not paths or paths[0] != root_path or len(paths) != len(set(paths)):
        _q57_reject(record["target_root"], "revision-removal tombstone is malformed")
    removed = []
    for relative in paths:
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts:
            _q57_reject(record["target_root"], "revision-removal path escapes the cartridge")
        destination = cartridge / path
        try:
            if destination.exists():
                destination.unlink()
                _sync_directory(destination.parent, f"remove:{record['target_root']}")
            removed.append(relative)
        except OSError as error:
            _q57_reject(record["target_root"], f"revision removal failed: {error}", "DURABILITY_UNSUPPORTED")
    try:
        tombstone.unlink(missing_ok=True)
        _sync_directory(tombstone.parent, f"remove:{record['target_root']}")
    except OSError as error:
        _q57_reject(record["target_root"], f"removal tombstone cleanup failed: {error}", "DURABILITY_UNSUPPORTED")
    return {"removed_root": record["target_root"], "removed_paths": removed}


def _revision_removal_record(cartridge: Path, target: str, reachability: object) -> dict:
    """Recompute one admissible removal record without changing cartridge bytes."""

    observed = revision_reachability(cartridge, target)
    if reachability != observed:
        _q57_reject(target, "reachability proof is stale, foreign, or malformed", "INVALID_REQUEST")
    target_root = observed["target_root"]
    if target_root == observed["current_root"]:
        _q57_reject(target_root, "current revision cannot be removed", "INVALID_REQUEST")
    if target_root in observed["reachable_roots"]:
        _q57_reject(target_root, "reachable revision cannot be removed", "INVALID_REQUEST")
    return {
        "target_root": target_root,
        "target_identity": observed["target_identity"],
        "reachability": observed,
        "removable_paths": observed["removable_paths"],
    }


def revision_removal_shape(
    cartridge: str | Path, target: str, reachability: object
) -> dict:
    """Return the exact Q53 tombstone demand after all removal refusals pass."""

    cartridge = Path(cartridge)
    _content_hex(target, "revision:remove")
    tombstone = cartridge / "removals" / f"{_content_hex(target, target)}.json"
    if tombstone.exists():
        record = _read_envelope(tombstone, f"remove:{target}", "ROOT_INVALID")
        if record.get("reachability") != reachability:
            _q57_reject(
                target,
                "removal retry carries another reachability proof",
                "IDEMPOTENCY_CONFLICT",
            )
    else:
        record = _revision_removal_record(cartridge, target, reachability)
    _, payload = _envelope(record)
    return {"journal_bytes": len(payload)}


def _remove_revision(
    cartridge: str | Path,
    operation_id: str,
    target: str,
    reachability: object,
    capacity_controller: CapacityTransitionController,
) -> dict:
    """Admit and remove one exact unreachable revision through a resumable tombstone."""

    cartridge = Path(cartridge)
    _content_hex(target, "revision:remove")
    tombstone = cartridge / "removals" / f"{_content_hex(target, target)}.json"
    if tombstone.exists():
        record = _read_envelope(tombstone, f"remove:{target}", "ROOT_INVALID")
        if record.get("reachability") != reachability:
            _q57_reject(
                target,
                "removal retry carries another reachability proof",
                "IDEMPOTENCY_CONFLICT",
            )
    else:
        record = _revision_removal_record(cartridge, target, reachability)
    _, payload = _envelope(record)
    if tombstone.exists():
        return _finish_revision_removal(cartridge, tombstone, record)
    digest = digest_bytes(payload)
    if not digest:
        _q57_reject(record["target_root"], "revision-removal tombstone lacks an identity")
    _claimed_durable_replace(
        capacity_controller,
        operation_id,
        f"removal:{record['target_root']}:tombstone",
        tombstone,
        payload,
        f"remove:{record['target_root']}",
        "journal_bytes",
    )
    return _finish_revision_removal(cartridge, tombstone, record)


def remove_revision(
    cartridge: str | Path,
    operation_id: str,
    target: str,
    reachability: object,
    capacity_controller: CapacityTransitionController,
) -> dict:
    """Remove one revision through its store-owned tombstone transition."""

    if not isinstance(capacity_controller, CapacityCoordinator):
        _capacity_reject(operation_id, "revision removal requires a next-transition controller", "INVALID_REQUEST")
    return _remove_revision(
        cartridge, operation_id, target, reachability, capacity_controller
    )


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
        if error.errno == errno.ENOSPC:
            raise
        _transaction_reject(object_id, f"F_FULLFSYNC failed for {path.name!r}: {error}", "DURABILITY_UNSUPPORTED")


def _sync_directory(path: Path, object_id: str) -> None:
    try:
        descriptor = os.open(path, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    except OSError as error:
        if error.errno == errno.ENOSPC:
            raise
        _transaction_reject(object_id, f"directory sync failed for {path.name!r}: {error}", "DURABILITY_UNSUPPORTED")


def _missing_directories(path: Path) -> tuple[Path, ...]:
    """Return each absent directory from its existing parent to the requested path."""

    missing = []
    cursor = path
    while not cursor.exists():
        if cursor == cursor.parent:
            _transaction_reject(str(path), "durable record has no existing filesystem parent")
        missing.append(cursor)
        cursor = cursor.parent
    return tuple(reversed(missing))


def _claimed_durable_replace(
    capacity_controller: CapacityCoordinator,
    operation_id: str,
    boundary_id: str,
    path: Path,
    payload: bytes,
    object_id: str,
    byte_field: str,
) -> None:
    """Create parents, write, verify, and publish one record with every mutation observed."""

    if byte_field not in _TRANSITION_BYTE_FIELDS:
        _capacity_reject(operation_id, f"unknown durable byte field {byte_field!r}", "INVALID_REQUEST")
    missing = _missing_directories(path.parent)
    temporary = path.with_name(f".{path.name}.pending")
    temporary.unlink(missing_ok=True)
    write_bytes = (*((0,) * len(missing)), len(payload), 0)
    transition = CapacityTransition(
        operation_id,
        boundary_id,
        **{byte_field: len(payload)},
        declared_writes=len(write_bytes),
        write_bytes=write_bytes,
    )

    def commit(claim: CapacityClaim) -> None:
        try:
            for directory in missing:
                execute_claimed_write(claim, directory.mkdir)
                _sync_directory(directory.parent, object_id)

            def write_temporary() -> None:
                if temporary.write_bytes(payload) != len(payload):
                    raise OSError(errno.ENOSPC, "durable record write was incomplete")

            execute_claimed_write(claim, write_temporary)
            if temporary.read_bytes() != payload:
                _transaction_reject(object_id, f"readback changed {temporary.name!r}")
            _fullsync_file(temporary, object_id)
            execute_claimed_write(claim, lambda: os.replace(temporary, path))
            _sync_directory(path.parent, object_id)
        except CassetteError:
            temporary.unlink(missing_ok=True)
            raise
        except OSError as error:
            temporary.unlink(missing_ok=True)
            if error.errno == errno.ENOSPC:
                raise
            _transaction_reject(
                object_id,
                f"atomic record replacement failed: {error}",
                "DURABILITY_UNSUPPORTED",
            )

    _run_claimed_writes(capacity_controller, transition, commit)


def _transactions_path(cartridge: Path) -> Path:
    return cartridge / "transactions"


def campaign_head(cartridge: str | Path, key: str) -> dict | None:
    """Q44/Q60/Q80: read a verified campaign head and its immutable predecessor chain."""
    if not isinstance(key, str) or re.fullmatch(r"[A-Za-z0-9_-]{1,160}", key) is None:
        _transaction_reject(str(key), "campaign key must be a bounded path-free identifier", "INVALID_REQUEST")
    directory = Path(cartridge) / "campaign"
    for path in (Path(cartridge), directory, directory / "objects", directory / "heads"):
        if path.is_symlink() or (path.exists() and not path.is_dir()):
            _transaction_reject(key, "campaign directory is not an ordinary directory")
    head = directory / "heads" / key
    if not head.exists() and not head.is_symlink():
        return None

    def read(path: Path) -> bytes:
        try:
            descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
            with os.fdopen(descriptor, "rb") as handle:
                metadata = os.fstat(handle.fileno())
                if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
                    _transaction_reject(key, "campaign object is linked or nonregular")
                return handle.read()
        except OSError as error:
            _transaction_reject(key, f"campaign object is unavailable: {error}")

    try:
        digest = read(head).decode("ascii")
        first, seen = None, set()
        while digest is not None:
            _digest("campaign digest", digest, key)
            if digest in seen:
                _transaction_reject(key, "campaign predecessor chain contains a cycle")
            seen.add(digest)
            payload = read(directory / "objects" / digest.split(":", 1)[1])
            record = json.loads(payload)
            if digest_bytes(payload) != digest or canonical_bytes(record) != payload or record["key"] != key:
                _transaction_reject(key, "campaign record identity or content changed")
            if first is None:
                first = {"digest": digest, **record}
            digest = record["previous"]
        return first
    except (ValueError, KeyError, UnicodeError) as error:
        _transaction_reject(key, f"campaign head is malformed: {error}")


def compare_campaign_head(
    capacity_controller: CapacityCoordinator, key: str, expected: str | None, value: dict,
) -> dict:
    """Q44/Q53/Q80: publish one immutable record under a process-exclusive head CAS."""
    cartridge = Path(capacity_controller.cartridge)
    descriptor = os.open(cartridge, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        current = campaign_head(cartridge, key)
        if (current["digest"] if current else None) != expected:
            _transaction_reject(key, "campaign head differs from the expected predecessor", "IDEMPOTENCY_CONFLICT")
        record = {"key": key, "previous": expected, "value": value}
        payload = canonical_bytes(record)
        digest = digest_bytes(payload)
        directory = cartridge / "campaign"
        object_path = directory / "objects" / digest.split(":", 1)[1]
        if object_path.exists() or object_path.is_symlink():
            if object_path.is_symlink() or object_path.stat().st_nlink != 1 or object_path.read_bytes() != payload:
                _transaction_reject(key, "existing immutable campaign object differs")
        else:
            _claimed_durable_replace(capacity_controller, key, "campaign-object", object_path,
                                     payload, digest, "journal_bytes")
        _claimed_durable_replace(capacity_controller, key, "campaign-head", directory / "heads" / key,
                                 digest.encode("ascii"), key, "pointer_bytes")
        _fullsync_file(directory / "heads" / key, key)
        return campaign_head(cartridge, key)
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def write_campaign_artifact(owner: CapacityCoordinator, attempt: str, name: str, payload: bytes) -> Path:
    """Q44/Q53: grant and publish one immutable off-drive campaign capture extent."""
    for value in (attempt, name):
        if not isinstance(value, str) or re.fullmatch(r"[A-Za-z0-9_.-]{1,160}", value) is None or value in {'.', '..'}:
            _transaction_reject(str(value), "capture name is not a bounded literal filename", "INVALID_REQUEST")
    path = owner.cartridge / "captures" / attempt / name
    if path.exists() or path.is_symlink():
        _transaction_reject(attempt, "immutable capture file already exists", "IDEMPOTENCY_CONFLICT")
    _claimed_durable_replace(owner, attempt, "capture-artifact", path, payload, name, "payload_bytes")
    return path


def verify_campaign_artifact(
    cartridge: str | Path,
    attempt: str,
    name: str,
    expected_digest: str,
    expected_bytes: int,
) -> dict:
    """Q44: read one bounded campaign probe through unlinked descriptors and verify its Cassette digest."""

    for value in (attempt, name):
        if (
            not isinstance(value, str)
            or re.fullmatch(r"[A-Za-z0-9_.-]{1,160}", value) is None
            or value in {".", ".."}
        ):
            _transaction_reject(str(value), "capture name is not a bounded literal filename", "INVALID_REQUEST")
    expected_digest = _transaction_digest(expected_digest, attempt)
    if type(expected_bytes) is not int or not 0 <= expected_bytes <= 4096:
        _transaction_reject(attempt, "integrity probe size must be an unsigned 4096-byte bound", "INVALID_REQUEST")
    descriptors = []
    try:
        descriptor = os.open(cartridge, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_NONBLOCK)
        descriptors.append(descriptor)
        for component in ("captures", attempt):
            descriptor = os.open(
                component,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_NONBLOCK,
                dir_fd=descriptors[-1],
            )
            descriptors.append(descriptor)
            if not stat.S_ISDIR(os.fstat(descriptor).st_mode):
                _transaction_reject(attempt, "campaign artifact path component is not a directory")
        descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=descriptors[-1])
        descriptors.append(descriptor)
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            _transaction_reject(attempt, "campaign artifact is linked or nonregular")
        if metadata.st_size != expected_bytes:
            _transaction_reject(attempt, "campaign artifact byte count differs from the integrity probe")
        payload = bytearray()
        while len(payload) < expected_bytes:
            chunk = os.read(descriptor, expected_bytes - len(payload))
            if not chunk:
                _transaction_reject(attempt, "campaign artifact ended before its exact probe bound")
            payload.extend(chunk)
        observed_digest = digest_bytes(payload)
        if observed_digest != expected_digest:
            _transaction_reject(attempt, "campaign artifact digest differs from the integrity probe")
        return {
            "attempt": attempt,
            "name": name,
            "digest": observed_digest,
            "bytes": expected_bytes,
        }
    except OSError as error:
        _transaction_reject(attempt, f"campaign artifact is absent or unavailable: {error}")
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def campaign_profile_io(owner: CapacityCoordinator, operation_id: str, pattern: dict) -> dict:
    """Q42/Q44/Q53: perform one measured scratch write, readback and full-sync boundary."""
    import time
    if set(pattern) != {"write_bytes", "read_bytes", "payload_digest"}:
        _transaction_reject(operation_id, "profile pattern requires exact write/read bytes and payload digest")
    write_bytes, read_bytes = pattern["write_bytes"], pattern["read_bytes"]
    if type(write_bytes) is not int or type(read_bytes) is not int or not 0 < read_bytes <= write_bytes <= 16 * 1024 * 1024:
        _transaction_reject(operation_id, "profile atom exceeds its bounded positive extent", "INVALID_REQUEST")
    payload = bytes(write_bytes)
    if digest_bytes(payload) != pattern["payload_digest"]:
        _transaction_reject(operation_id, "profile payload digest differs from its planned atom")
    started = time.monotonic_ns()
    path = write_campaign_artifact(owner, operation_id, "profile.bin", payload)
    written = time.monotonic_ns()
    with path.open("rb") as handle:
        observed = handle.read(read_bytes)
    read_done = time.monotonic_ns()
    _fullsync_file(path, operation_id)
    finished = time.monotonic_ns()
    if observed != payload[:read_bytes]:
        _transaction_reject(operation_id, "profile readback differs from written bytes")
    return {"duration_seconds": (finished-started)/1e9, "write_seconds": (written-started)/1e9,
            "read_seconds": (read_done-written)/1e9, "flush_seconds": (finished-read_done)/1e9,
            "readback_ok": True, "flush_ok": True, "errors": 0, "host_write_bytes": write_bytes,
            "physical_write_bytes": None, "path": str(path)}


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


def _generation_publication_bytes(
    cartridge: Path,
    transaction_id: str,
    candidate_root_digest: str,
    candidate_root: dict,
    locations: tuple[PageLocation, ...],
    expected_parent_root: str | None,
    context: TransactionContext | None = None,
) -> int:
    """Compute the exact additional Q53 bytes at the generation-publication peak."""

    transaction_id = _transaction_id(transaction_id)
    active = recover_generation(cartridge)
    active_root = active.root_digest if active else None
    if active_root != expected_parent_root:
        _transaction_reject(
            f"transaction:{transaction_id}",
            f"expected parent {expected_parent_root!r}, found {active_root!r}",
            "IDEMPOTENCY_CONFLICT",
        )
    object_id = f"transaction:{transaction_id}"
    resume = _resume_record(
        cartridge,
        candidate_root_digest,
        context,
        object_id,
        persist_material=False,
        locations=locations,
    )
    expected_pages = [
        {"page_digest": row.page_digest, "length": row.length}
        for row in sorted(locations, key=lambda item: item.page_digest)
    ]
    if resume["page_results"] != expected_pages:
        _transaction_reject(object_id, "generation shape locations differ from the candidate index")
    generation = _next_generation(cartridge)
    parent_id = active.child_id if active else None
    candidate_id = _generation_identity(
        candidate_root,
        parent_id,
        _training_manifest(resume),
        [row["page_digest"] for row in resume["page_results"]],
    )
    record = {
        "transaction_id": transaction_id,
        "step": 0,
        "state": _TRANSACTION_STATES[0],
        "candidate_generation": generation,
        "candidate_root": candidate_root_digest,
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
    record["generation_record_digest"] = digest_bytes(
        canonical_bytes(_generation_body(record))
    )
    segment_count = len({row.segment_id for row in locations})
    boundary_count = segment_count + 5
    variants = [record]
    variants.extend(
        {**record, "step": step, "state": _TRANSACTION_STATES[step]}
        for step in range(1, 5)
    )
    variants.extend(
        {
            **record,
            "step": 5,
            "state": _TRANSACTION_STATES[5],
            "dependency_cursor": cursor,
        }
        for cursor in range(boundary_count + 2)
    )
    variants.append({
        **record,
        "step": 6,
        "state": _TRANSACTION_STATES[6],
        "dependency_cursor": boundary_count + 1,
    })
    variants.extend(
        {
            **record,
            "step": 7,
            "state": _TRANSACTION_STATES[7],
            "dependency_cursor": boundary_count + 1,
            "pointer_cursor": pointer,
        }
        for pointer in (1, 2, 3)
    )
    variants.append({
        **record,
        "step": 8,
        "state": _TRANSACTION_STATES[8],
        "dependency_cursor": boundary_count + 1,
        "pointer_cursor": 3,
    })
    journal_sizes = []
    for variant in variants:
        _validate_transaction(
            variant, f"transaction:{transaction_id}"
        )
        journal_sizes.append(len(_envelope(variant)[1]))
    journal_peak = max(
        journal_sizes[0],
        *(left + right for left, right in zip(journal_sizes, journal_sizes[1:])),
    )
    generation_bytes = len(_envelope(_generation_body(record))[1])
    material_bytes = 0
    material_digests = set()
    for payload, digest in (
        (context.statistics if context is not None else None, resume["statistics_digest"]),
        (context.rng_state if context is not None else None, resume["rng_state_digest"]),
    ):
        if payload is None or digest in material_digests:
            continue
        material_digests.add(digest)
        path = _restart_material_path(cartridge, digest)
        if path.exists():
            try:
                observed = path.read_bytes()
            except OSError as error:
                _transaction_reject(object_id, f"restart material is unavailable: {error}")
            if digest_bytes(observed) != digest:
                _transaction_reject(object_id, "restart material does not match its identity")
        else:
            material_bytes = _capacity_sum((material_bytes, len(payload)), transaction_id)
    return _capacity_sum((material_bytes, journal_peak, generation_bytes), transaction_id)


def generation_publication_shape(
    cartridge: str | Path,
    transaction_id: str,
    candidate_root: str,
    *,
    expected_parent_root: str | None,
    context: TransactionContext | None = None,
) -> dict[str, int]:
    """Return exact bytes for the next parent-to-callable generation transition."""

    path = Path(cartridge)
    root = load_root(path, candidate_root)
    locations = tuple(_read_index(path, candidate_root).values())
    return {
        "publication_bytes": _generation_publication_bytes(
            path,
            transaction_id,
            candidate_root,
            root,
            locations,
            expected_parent_root,
            context,
        )
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


def _write_restart_material(
    cartridge: Path,
    payload: bytes,
    digest: str,
    object_id: str,
    *,
    capacity_controller: CapacityTransitionController | None = None,
    operation_id: str | None = None,
    boundary_id: str | None = None,
) -> None:
    path = _restart_material_path(cartridge, digest)
    if path.exists():
        try:
            observed = path.read_bytes()
        except OSError as error:
            _transaction_reject(object_id, f"restart material is unavailable: {error}", "SOURCE_UNAVAILABLE")
        if digest_bytes(observed) != digest:
            _transaction_reject(object_id, "restart material does not match its identity", "SOURCE_UNAVAILABLE")
        return
    operation_id = operation_id or f"restart-{_content_hex(digest, digest)}"
    capacity_controller = _capacity_coordinator(
        cartridge, capacity_controller, operation_id
    )
    _claimed_durable_replace(
        capacity_controller,
        operation_id,
        boundary_id or f"{object_id}:restart:{digest}",
        path,
        payload,
        object_id,
        "payload_bytes",
    )


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
    locations: tuple[PageLocation, ...] | None = None,
    capacity_controller: CapacityTransitionController | None = None,
    operation_id: str | None = None,
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
            _write_restart_material(
                cartridge,
                context.statistics,
                statistics_digest,
                object_id,
                capacity_controller=capacity_controller,
                operation_id=operation_id,
                boundary_id=f"{object_id}:restart:statistics",
            )
        if rng_state_digest is not None:
            _write_restart_material(
                cartridge,
                context.rng_state,
                rng_state_digest,
                object_id,
                capacity_controller=capacity_controller,
                operation_id=operation_id,
                boundary_id=f"{object_id}:restart:rng-state",
            )
    candidate_locations = (
        tuple(_read_index(cartridge, candidate_root).values())
        if locations is None else locations
    )
    resume = {
        "operation_version": context.operation_version,
        "input_digests": list(context.input_digests),
        "random_seed": context.random_seed,
        "statistics_digest": statistics_digest,
        "page_results": [
            {"page_digest": location.page_digest, "length": location.length}
            for location in sorted(
                candidate_locations, key=lambda item: item.page_digest
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


def _write_transaction(
    cartridge: Path,
    record: dict,
    *,
    capacity_controller: CapacityTransitionController | None = None,
    operation_id: str | None = None,
    boundary_id: str | None = None,
) -> None:
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
    operation_id = operation_id or f"generation-{transaction_id}"
    capacity_controller = _capacity_coordinator(
        cartridge, capacity_controller, operation_id
    )
    _claimed_durable_replace(
        capacity_controller,
        operation_id,
        boundary_id or f"{object_id}:journal:{record['step']}",
        _journal_path(cartridge, transaction_id),
        payload,
        object_id,
        "journal_bytes",
    )


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


def _valid_generations(cartridge: Path, verify_dependencies: bool, *, highest_only: bool = False) -> tuple[GenerationPin, ...]:
    pins = []
    failures = []
    for path in _generation_files(cartridge):
        try:
            record = _load_generation(path)
            root = (_verify_dependency_paths(cartridge, record["root_digest"])[0]
                    if verify_dependencies else load_root(cartridge, record["root_digest"]))
            _verify_generation_binding(cartridge, record, root)
            pins.append(GenerationPin(record["generation"], record["child_id"], record["root_digest"]))
            if highest_only:
                break
        except CassetteError as error:
            failures.append(error)
    if not pins and failures:
        raise failures[0]
    return tuple(pins)


def pin_generation(cartridge: str | Path) -> GenerationPin | None:
    """Pin the highest callable generation without allowing a later commit to change this reader."""

    generations = _valid_generations(Path(cartridge), False, highest_only=True)
    return generations[0] if generations else None


def recover_generation(cartridge: str | Path) -> GenerationPin | None:
    """Rehash every dependency and select the highest valid generation after mount or process death."""

    generations = _valid_generations(Path(cartridge), True, highest_only=True)
    return generations[0] if generations else None


def _capacity_boundary_marker(cartridge: Path) -> tuple[GenerationPin | None, bool]:
    """Capture the latest exact generation pointer and whether its full revision is callable."""

    paths = _generation_files(cartridge)
    if not paths:
        return None, True
    record = _load_generation(paths[0])
    marker = GenerationPin(record["generation"], record["child_id"], record["root_digest"])
    try:
        callable_generation = recover_generation(cartridge)
    except CassetteError:
        callable_generation = None
    return marker, callable_generation == marker


def _recover_capacity_boundary(cartridge: Path, claim: CapacityClaim) -> bool:
    """Prove this failed transition retained its parent or published its own exact child."""

    try:
        observed, callable_observed = _capacity_boundary_marker(cartridge)
    except CassetteError:
        return False
    parent = claim.recovery_parent
    if observed == parent:
        return not claim.recovery_parent_callable or callable_observed
    if observed is None:
        return False
    if parent is None:
        expected_generation = 0
        expected_parent = (None, None, None)
    else:
        expected_generation = parent.generation + 1
        expected_parent = (parent.generation, parent.child_id, parent.root_digest)
    if observed.generation != expected_generation or not callable_observed:
        return False
    try:
        record = _load_generation(_generation_path(cartridge, observed.generation))
    except CassetteError:
        return False
    return (
        record["transaction_id"] == claim.transition.operation_id
        and (
            record["parent_generation"],
            record["parent_id"],
            record["parent_root"],
        ) == expected_parent
    )


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


def initialize_cartridge(
    cartridge: str | Path,
    cartridge_uuid: str | None = None,
    *,
    capacity_controller: CapacityCoordinator | None = None,
    operation_id: str = "initialize-cartridge",
) -> str:
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
    capacity_controller = _capacity_coordinator(
        cartridge, capacity_controller, operation_id
    )
    _claimed_durable_replace(
        capacity_controller,
        operation_id,
        "cartridge:identity",
        path,
        payload,
        f"cartridge:{logical_uuid}",
        "payload_bytes",
    )
    if _read_cartridge_uuid(cartridge) != logical_uuid:
        _lifecycle_reject(
            logical_uuid, "cartridge UUID changed during durable readback",
            "CARTRIDGE_IDENTITY_MISMATCH",
        )
    return logical_uuid


def create_selected_root(
    selection: DriveSelection,
    destination_path: str,
    *,
    operation_id: str,
    cartridge_uuid: str | None = None,
) -> tuple[Path, str]:
    """Create or reopen one relative Cassette root below an existing selected-volume directory."""

    if (
        not isinstance(destination_path, str)
        or not destination_path
        or destination_path.startswith("/")
        or any(_DRIVE_ROOT_NAME.fullmatch(part) is None for part in destination_path.split("/"))
        or not isinstance(operation_id, str)
        or not operation_id
    ):
        _drive_reject("unidentified", "relative destination path or operation ID is invalid", "INVALID_REQUEST")
    selection = revalidate_external_apfs_volume(selection)
    if selection.volume.read_only:
        _drive_reject(
            selection.volume.volume_uuid,
            "selected APFS volume is read-only",
            "CARTRIDGE_READ_ONLY",
        )
    volume_root = Path(selection.volume.mount_path)
    volume_device = volume_root.stat().st_dev
    cartridge = volume_root.joinpath(*destination_path.split("/"))
    parent = volume_root
    for segment in destination_path.split("/")[:-1]:
        parent = parent / segment
        try:
            metadata = parent.lstat()
        except OSError as error:
            _drive_reject(
                selection.volume.volume_uuid,
                f"relative destination parent {segment!r} is unavailable: {error}",
                "CONTAINMENT_REJECTED",
            )
        if (
            stat.S_ISLNK(metadata.st_mode)
            or not stat.S_ISDIR(metadata.st_mode)
            or metadata.st_dev != volume_device
        ):
            _drive_reject(
                selection.volume.volume_uuid,
                f"relative destination parent {segment!r} is not an ordinary directory on the selected volume",
                "CONTAINMENT_REJECTED",
            )
    marker = _cartridge_identity_path(cartridge)
    try:
        cartridge_metadata = cartridge.lstat()
    except FileNotFoundError:
        cartridge_exists = False
    except OSError as error:
        _drive_reject(
            selection.volume.volume_uuid,
            f"relative destination path is unavailable: {error}",
            "CONTAINMENT_REJECTED",
        )
    else:
        cartridge_exists = True
        if (
            stat.S_ISLNK(cartridge_metadata.st_mode)
            or not stat.S_ISDIR(cartridge_metadata.st_mode)
            or cartridge_metadata.st_dev != volume_device
        ):
            _drive_reject(
                selection.volume.volume_uuid,
                "selected root is not an ordinary directory on the selected volume",
                "CONTAINMENT_REJECTED",
            )
    if cartridge_exists and not marker.exists():
        _drive_reject(
            selection.volume.volume_uuid,
            "selected root already exists without a Cassette identity marker",
            "CONTAINMENT_REJECTED",
        )
    coordinator = CapacityCoordinator(cartridge)
    if not cartridge_exists:
        try:
            _claimed_directories(
                coordinator,
                operation_id,
                "drive:selected-root",
                cartridge,
                f"volume:{selection.volume.volume_uuid}",
            )
        except OSError as error:
            _drive_reject(
                selection.volume.volume_uuid,
                f"actual writer mkdir failed with {error.__class__.__name__} errno {error.errno}; no cause is inferred",
            )
    try:
        cartridge_id = initialize_cartridge(
            cartridge,
            cartridge_uuid,
            capacity_controller=coordinator,
            operation_id=operation_id,
        )
    except OSError as error:
        _drive_reject(
            selection.volume.volume_uuid,
            f"actual writer initialization failed with {error.__class__.__name__} errno {error.errno}; no cause is inferred",
        )
    revalidate_external_apfs_volume(selection)
    return cartridge, cartridge_id


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
    capacity_controller: CapacityTransitionController | None = None,
    operation_id: str | None = None,
) -> TransactionState:
    """Durably prepare one idempotent Q25/Q60 transaction against an exact parent generation."""

    cartridge = Path(cartridge)
    transaction_id = _transaction_id(transaction_id)
    object_id = f"transaction:{transaction_id}"
    operation_id = operation_id or f"generation-{transaction_id}"
    capacity_controller = _capacity_coordinator(
        cartridge, capacity_controller, operation_id
    )
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
        cartridge,
        candidate_root,
        context,
        object_id,
        persist_material=True,
        capacity_controller=capacity_controller,
        operation_id=operation_id,
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
    _write_transaction(
        cartridge,
        record,
        capacity_controller=capacity_controller,
        operation_id=operation_id,
        boundary_id=f"{object_id}:journal:begin",
    )
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


def _write_candidate(
    cartridge: Path,
    record: dict,
    *,
    capacity_controller: CapacityTransitionController | None = None,
    operation_id: str | None = None,
    boundary_id: str | None = None,
) -> Path:
    path = _candidate_path(cartridge, record["transaction_id"])
    payload = _candidate_payload(record)
    operation_id = operation_id or f"generation-{record['transaction_id']}"
    capacity_controller = _capacity_coordinator(
        cartridge, capacity_controller, operation_id
    )

    _claimed_durable_replace(
        capacity_controller,
        operation_id,
        boundary_id or f"transaction:{record['transaction_id']}:candidate",
        path,
        payload,
        f"transaction:{record['transaction_id']}",
        "payload_bytes",
    )
    return path


def _ensure_candidate(
    cartridge: Path,
    record: dict,
    *,
    capacity_controller: CapacityTransitionController | None = None,
    operation_id: str | None = None,
) -> Path:
    path = _candidate_path(cartridge, record["transaction_id"])
    expected = _candidate_payload(record)
    try:
        observed = path.read_bytes()
    except OSError:
        observed = None
    if observed != expected:
        path = _write_candidate(
            cartridge,
            record,
            capacity_controller=capacity_controller,
            operation_id=operation_id,
            boundary_id=f"transaction:{record['transaction_id']}:candidate-repair",
        )
        try:
            observed = path.read_bytes()
        except OSError as error:
            _transaction_reject(f"transaction:{record['transaction_id']}", f"candidate readback failed: {error}")
    if observed != expected:
        _transaction_reject(f"transaction:{record['transaction_id']}", "candidate readback digest changed")
    return path


def _publish_candidate(
    cartridge: Path,
    record: dict,
    repair: bool = False,
    *,
    capacity_controller: CapacityTransitionController | None = None,
    operation_id: str | None = None,
) -> Path:
    operation_id = operation_id or f"generation-{record['transaction_id']}"
    capacity_controller = _capacity_coordinator(
        cartridge, capacity_controller, operation_id
    )
    destination = _generation_path(cartridge, record["candidate_generation"])
    expected = _candidate_payload(record)
    if destination.exists():
        if destination.read_bytes() != expected:
            _transaction_reject(f"generation:{record['candidate_generation']}", "generation collision")
        return destination
    candidate = _candidate_path(cartridge, record["transaction_id"])
    if repair:
        candidate = _ensure_candidate(
            cartridge,
            record,
            capacity_controller=capacity_controller,
            operation_id=operation_id,
        )
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
    missing = _missing_directories(destination.parent)
    transition = CapacityTransition(
        operation_id,
        f"transaction:{record['transaction_id']}:generation-publication",
        declared_writes=len(missing) + 1,
        write_bytes=(*((0,) * len(missing)), 0),
    )

    def publish(claim: CapacityClaim) -> Path:
        for directory in missing:
            execute_claimed_write(claim, directory.mkdir)
            _sync_directory(directory.parent, f"transaction:{record['transaction_id']}")
        try:
            execute_claimed_write(claim, lambda: os.rename(candidate, destination))
        except OSError as error:
            if error.errno == errno.ENOSPC:
                raise
            _transaction_reject(
                f"transaction:{record['transaction_id']}",
                f"atomic generation publication failed: {error}",
                "DURABILITY_UNSUPPORTED",
            )
        _sync_directory(destination.parent, f"transaction:{record['transaction_id']}")
        return destination

    return _run_claimed_writes(capacity_controller, transition, publish)


def advance_generation(
    cartridge: str | Path,
    transaction_id: str,
    *,
    capacity_controller: CapacityTransitionController | None = None,
    operation_id: str | None = None,
) -> TransactionState:
    """Execute one idempotent Q25 transition; a fresh process may execute the next transition."""

    cartridge = Path(cartridge)
    record = _load_transaction(cartridge, transaction_id)
    operation_id = operation_id or f"generation-{record['transaction_id']}"
    capacity_controller = _capacity_coordinator(
        cartridge, capacity_controller, operation_id
    )
    step = record["step"]
    object_id = f"transaction:{record['transaction_id']}"

    def write_journal(next_record: dict) -> None:
        _write_transaction(
            cartridge,
            next_record,
            capacity_controller=capacity_controller,
            operation_id=operation_id,
            boundary_id=f"{object_id}:journal:{next_record['step']}",
        )

    if step == len(_TRANSACTION_STATES) - 1:
        generation = _load_generation(
            _generation_path(cartridge, record["candidate_generation"])
        )
        root, _ = _verify_dependency_paths(cartridge, generation["root_digest"])
        _verify_generation_binding(cartridge, generation, root)
        return _public_transaction(record)
    if step == 0:
        _write_candidate(
            cartridge,
            record,
            capacity_controller=capacity_controller,
            operation_id=operation_id,
            boundary_id=f"{object_id}:candidate",
        )
    elif step == 1:
        _ensure_candidate(
            cartridge,
            record,
            capacity_controller=capacity_controller,
            operation_id=operation_id,
        )
    elif step == 2:
        _fullsync_file(_ensure_candidate(cartridge, record), object_id)
    elif step == 3:
        _verify_dependency_paths(cartridge, record["candidate_root"])
    elif step == 4:
        record = {**record, "step": 5, "state": _TRANSACTION_STATES[5]}
        write_journal(record)
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
            _publish_candidate(
                cartridge,
                record,
                capacity_controller=capacity_controller,
                operation_id=operation_id,
            )
            record = {**record, "step": 6, "state": _TRANSACTION_STATES[6]}
        else:
            _transaction_reject(object_id, "journal dependency cursor exceeds its verified frontier")
        write_journal(record)
        return _public_transaction(record)
    elif step == 6:
        destination = _publish_candidate(
            cartridge,
            record,
            repair=True,
            capacity_controller=capacity_controller,
            operation_id=operation_id,
        )
        _fullsync_file(destination, object_id)
        record = {**record, "step": 7, "state": _TRANSACTION_STATES[7], "pointer_cursor": 1}
        write_journal(record)
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
        write_journal(record)
        return _public_transaction(record)
    record = {**record, "step": step + 1, "state": _TRANSACTION_STATES[step + 1]}
    write_journal(record)
    return _public_transaction(record)


def commit_generation(
    cartridge: str | Path,
    transaction_id: str,
    candidate_root: str,
    *,
    expected_parent_root: str | None,
    context: TransactionContext | None = None,
    capacity_controller: CapacityTransitionController | None = None,
    operation_id: str | None = None,
) -> GenerationPin:
    """Resume until the exact candidate is a fully synced immutable callable generation."""

    operation_id = operation_id or f"generation-{_transaction_id(transaction_id)}"
    capacity_controller = _capacity_coordinator(
        cartridge, capacity_controller, operation_id
    )
    state = begin_generation(
        cartridge,
        transaction_id,
        candidate_root,
        expected_parent_root=expected_parent_root,
        context=context,
        capacity_controller=capacity_controller,
        operation_id=operation_id,
    )
    while state.state != "COMMITTED":
        state = advance_generation(
            cartridge,
            transaction_id,
            capacity_controller=capacity_controller,
            operation_id=operation_id,
        )
    advance_generation(
        cartridge,
        transaction_id,
        capacity_controller=capacity_controller,
        operation_id=operation_id,
    )
    record = _load_transaction(Path(cartridge), transaction_id)
    return GenerationPin(record["candidate_generation"], record["candidate_id"], candidate_root)


def rollback_generation(
    cartridge: str | Path,
    transaction_id: str,
    *,
    capacity_controller: CapacityCoordinator | None = None,
    operation_id: str | None = None,
) -> GenerationPin:
    """Publish the prior valid root as a new generation while retaining both immutable revisions."""

    cartridge = Path(cartridge)
    generations = _valid_generations(cartridge, True)
    if len(generations) < 2:
        _transaction_reject(
            f"transaction:{transaction_id}", "rollback requires a current and prior valid generation",
            "INVALID_REQUEST",
        )
    current, prior = generations[:2]
    operation_id = operation_id or f"rollback-{_transaction_id(transaction_id)}"
    capacity_controller = _capacity_coordinator(
        cartridge, capacity_controller, operation_id
    )
    return commit_generation(
        cartridge,
        transaction_id,
        prior.root_digest,
        expected_parent_root=current.root_digest,
        capacity_controller=capacity_controller,
        operation_id=operation_id,
    )


def reclaim_capacity(
    cartridge: str | Path,
    capacity_controller: CapacityCoordinator | None = None,
) -> tuple[str, ...]:
    """Inventory and remove only transaction objects that satisfy every Q53 reclaim guard."""

    cartridge = Path(cartridge)
    capacity_controller = _capacity_coordinator(
        cartridge, capacity_controller, "capacity-reclamation"
    )
    recover_generation(cartridge)
    directory = _transactions_path(cartridge)
    if not directory.exists():
        return ()
    records = [_load_transaction(cartridge, path.stem) for path in sorted(directory.glob("*.json"))]
    records_by_id = {record["transaction_id"]: record for record in records}
    referenced_material = {
        _restart_material_path(cartridge, digest)
        for record in records
        for digest in (
            record["resume"]["statistics_digest"],
            record["resume"]["rng_state_digest"],
        )
        if digest is not None
    }
    any_active_claim = bool(capacity_controller.active_claims())
    candidates: list[tuple[Path, ReclaimableObject]] = []
    for path in sorted(item for item in directory.rglob("*") if item.is_file()):
        is_atomic_temporary = path.name.startswith(".") and path.name.endswith(".pending")
        is_candidate = path.parent == directory and path.name.endswith(".generation-candidate")
        if not (is_atomic_temporary or is_candidate):
            continue
        transaction_id = None
        if is_candidate:
            transaction_id = path.name.removesuffix(".generation-candidate")
        elif path.parent == directory:
            inner = path.name.removeprefix(".").removesuffix(".pending")
            if inner.endswith(".json"):
                transaction_id = inner.removesuffix(".json")
        record = records_by_id.get(transaction_id)
        active_transaction = record is not None and record["step"] < 8
        journal_reference = (
            record is not None
            or any(
                path == material.with_name(f".{material.name}.pending")
                for material in referenced_material
            )
        )
        candidate = ReclaimableObject(
            object_id=str(path.relative_to(cartridge)),
            cassette_owned=True,
            pinned=False,
            reachable_from_retained_root=False,
            rollback_retained=False,
            retention_class="REPRODUCIBLE" if is_candidate else "TEMPORARY",
            active_claim_reference=any_active_claim,
            active_transaction_reference=active_transaction,
            active_journal_reference=journal_reference,
        )
        candidates.append((path, candidate))
    selected = {
        candidate.object_id
        for candidate in select_reclaimable_objects(
            tuple(candidate for _, candidate in candidates)
        )
    }
    removed = []
    for path, candidate in candidates:
        if candidate.object_id not in selected:
            continue
        try:
            path.unlink()
        except OSError as error:
            _transaction_reject(f"transaction:{path.name}", f"temporary reclamation failed: {error}")
        removed.append(path.name)
    if removed:
        _sync_directory(directory, "transactions:garbage-collection")
    return tuple(removed)


def collect_garbage(
    cartridge: str | Path,
    capacity_controller: CapacityCoordinator | None = None,
) -> tuple[str, ...]:
    """Run the Q53 reclaim inventory without considering caller-authored eligibility flags."""

    return reclaim_capacity(cartridge, capacity_controller)


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
        if error.errno == errno.ENOSPC:
            raise
        _integrity_reject(object_id, f"repair directory sync failed for {path.name!r}: {error}")


def _quarantine_target(path: Path, object_id: str) -> Path | None:
    """Return the immutable quarantine name for an existing corrupt object."""

    if not path.exists():
        return None
    try:
        payload = path.read_bytes()
        observed = digest_bytes(payload)[7:]
        directory = path.parents[1] / "quarantine"
        return directory / f"{path.parent.name}-{path.name}-{observed}"
    except OSError as error:
        _integrity_reject(object_id, f"corrupt object quarantine failed: {error}")


def _replace_exact(
    path: Path,
    payload: bytes,
    expected_digest: str,
    object_id: str,
    *,
    capacity_controller: CapacityCoordinator,
    operation_id: str,
) -> None:
    if digest_bytes(payload) != expected_digest:
        _integrity_reject(object_id, "repair candidate does not match the original digest")
    if not isinstance(capacity_controller, CapacityCoordinator):
        _capacity_reject(operation_id, "repair requires the concrete capacity coordinator", "INVALID_REQUEST")
    if path.exists() and path.read_bytes() == payload:
        return
    temporary = path.with_name(f".{path.name}.repair-pending")
    try:
        if not temporary.exists() or temporary.read_bytes() != payload:
            temporary.unlink(missing_ok=True)
            _claimed_durable_replace(
                capacity_controller,
                operation_id,
                f"{object_id}:repair-material",
                temporary,
                payload,
                object_id,
                "payload_bytes",
            )
        if temporary.read_bytes() != payload:
            _integrity_reject(object_id, "repair candidate changed during readback")

        quarantine = _quarantine_target(path, object_id)
        missing = () if quarantine is None else _missing_directories(quarantine.parent)
        link_required = quarantine is not None and not quarantine.exists()
        write_bytes = (*((0,) * len(missing)), *((0,) if link_required else ()), 0)
        transition = CapacityTransition(
            operation_id,
            f"{object_id}:repair-publication",
            declared_writes=len(write_bytes),
            write_bytes=write_bytes,
        )

        def publish(claim: CapacityClaim) -> None:
            for directory in missing:
                execute_claimed_write(claim, directory.mkdir)
                _portable_directory_sync(directory.parent, object_id)
            if link_required:
                execute_claimed_write(claim, lambda: os.link(path, quarantine))
                _portable_directory_sync(quarantine.parent, object_id)
            execute_claimed_write(claim, lambda: os.replace(temporary, path))
            _portable_directory_sync(path.parent, object_id)

        _run_claimed_writes(capacity_controller, transition, publish)
    except CassetteError:
        raise
    except OSError as error:
        if error.errno == errno.ENOSPC:
            raise
        _integrity_reject(object_id, f"exact repair replacement failed: {error}")


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


def _repair_set_candidate(
    cartridge: Path, root_digest: str
) -> tuple[dict[str, bytes], bytes, str, str, tuple[dict, ...]]:
    """Build the exact immutable Q62 repair transition before a claim permits its writes."""

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
    return objects, manifest_payload, manifest_digest, index_digest, tuple(stripes)


def repair_set_shape(cartridge: str | Path, root_digest: str) -> dict[str, int]:
    """Return the exact next-transition bytes for Q62 repair material without writing it."""

    objects, manifest_payload, _, _, _ = _repair_set_candidate(Path(cartridge), root_digest)
    return {
        "payload_bytes": _capacity_sum(
            (*[len(payload) for payload in objects.values()], 2 * len(manifest_payload)), root_digest
        )
    }


def create_repair_set(
    cartridge: str | Path,
    root_digest: str,
    capacity_controller: CapacityTransitionController,
) -> RepairSet:
    """Create Q62 replicas through separate store-owned durable transitions."""

    if not isinstance(capacity_controller, CapacityCoordinator):
        _capacity_reject("repair-set", "repair set requires a next-transition controller", "INVALID_REQUEST")
    cartridge = Path(cartridge)
    objects, manifest_payload, manifest_digest, index_digest, stripes = _repair_set_candidate(
        cartridge, root_digest
    )
    operation_id = f"repair-set-{root_digest[7:]}"

    def replace(path: Path, payload: bytes, digest: str, object_id: str) -> None:
        if path.exists() and path.read_bytes() == payload:
            return
        _replace_exact(
            path,
            payload,
            digest,
            object_id,
            capacity_controller=capacity_controller,
            operation_id=operation_id,
        )

    for digest, payload in objects.items():
        replace(_repair_object_path(cartridge, digest), payload, digest, f"repair-object:{digest}")
    replace(
        _repair_manifest_replica_path(cartridge, root_digest),
        manifest_payload,
        manifest_digest,
        f"manifest-copy:{root_digest}",
    )
    replace(
        _repair_manifest_path(cartridge, root_digest),
        manifest_payload,
        manifest_digest,
        f"repair:{root_digest}",
    )
    _repair_record(cartridge, root_digest)
    required = _capacity_sum(
        (*[len(payload) for payload in objects.values()], 2 * len(manifest_payload)), root_digest
    )
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


def repair_replacement_shape(cartridge: str | Path, root_digest: str) -> dict[str, int]:
    """Return the exact next Q62 replacement transition without changing repair state."""

    _, root_copy, index_copy, locations, manifest_payload, _, _ = _repair_record(
        Path(cartridge), root_digest
    )
    extent = max(
        len(root_copy),
        len(index_copy),
        len(manifest_payload),
        *(sum(location.length for location in locations.values() if location.segment_id == segment_id)
          for segment_id in {location.segment_id for location in locations.values()}),
    )
    return {"payload_bytes": extent}


def _integrity_operation(
    cartridge: Path,
    root_digest: str,
    *,
    repair: bool,
    capacity_controller: CapacityTransitionController | None,
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
        if not isinstance(capacity_controller, CapacityCoordinator):
            _capacity_reject("repair", "repair requires a next-transition controller", "INVALID_REQUEST")

    def replace(path: Path, payload: bytes, digest: str, object_id: str) -> None:
        if path.exists() and path.read_bytes() == payload:
            return
        if capacity_controller is None:
            _integrity_reject(object_id, "repair controller is absent", "INVALID_REQUEST")
        _replace_exact(
            path,
            payload,
            digest,
            object_id,
            capacity_controller=capacity_controller,
            operation_id=f"repair-{root_digest[7:]}",
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
            replace(
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
                replace(path, payload, digest, object_id)
                _transition(states, transitions, object_id, "VALID")

    # Q47/Q62: verification retains no model pages; repair retains only its current stripe.
    for stripe in record["stripes"]:
        parity_digest = stripe["parity_digest"]
        parity_id = f"parity:{parity_digest}"
        parity_path = _repair_object_path(cartridge, parity_digest)
        try:
            parity_valid = parity_path.stat().st_size == stripe["length"] and _file_digest(parity_path) == parity_digest
        except OSError:
            parity_valid = False
        if not parity_valid:
            _mark_corrupt(states, transitions, parity_id)
        segment_id = stripe["segment_id"]
        segment_path = cartridge / "segments" / _content_hex(segment_id, segment_id)
        segment_state = f"segment:{segment_id}"
        try:
            segment_valid = _file_digest(segment_path) == segment_id
        except OSError:
            segment_valid = False
        if not segment_valid:
            states[segment_state] = "VALID"
            _mark_corrupt(states, transitions, segment_state)
        members = [locations[digest] for digest in stripe["page_digests"]]
        page_payloads = {}
        corrupt_pages = []
        for location in members:
            try:
                payload = _read_page(cartridge, location)
                if repair:
                    page_payloads[location.page_digest] = payload
                del payload
            except CassetteError:
                _mark_corrupt(states, transitions, f"page:{location.page_digest}")
                corrupt_pages.append(location.page_digest)
        if not repair:
            continue
        for digest in sorted(corrupt_pages):
            object_id = f"page:{digest}"
            _transition(states, transitions, object_id, "REPAIRING")
            length = locations[digest].length
            candidate = None
            try:
                local = _repair_object_path(cartridge, digest).read_bytes()
                if len(local) == length and digest_bytes(local) == digest:
                    candidate = local
                del local
            except OSError:
                pass
            source = sources.get(digest)
            if candidate is None and source is not None and len(source) == length:
                candidate = source
            peers = [item for item in stripe["page_digests"] if item != digest]
            if candidate is None and parity_valid and all(peer in page_payloads for peer in peers):
                candidate = _xor_payloads(
                    (parity_path.read_bytes(), *[page_payloads[peer] for peer in peers]),
                    stripe["length"],
                )[:length]
            if candidate is not None and digest_bytes(candidate) == digest:
                page_payloads[digest] = candidate
            else:
                _transition(states, transitions, object_id, "UNAVAILABLE")
            del candidate
        if not segment_valid and all(member.page_digest in page_payloads for member in members):
            cursor = 0
            payload = bytearray()
            for member in members:
                if member.offset != cursor:
                    _integrity_reject(segment_state, "segment page intervals are discontinuous")
                payload.extend(page_payloads[member.page_digest])
                cursor += member.length
            _transition(states, transitions, segment_state, "REPAIRING")
            replace(segment_path, bytes(payload), segment_id, segment_state)
            del payload
            _transition(states, transitions, segment_state, "VALID")
            for member in members:
                object_id = f"page:{member.page_digest}"
                if states[object_id] == "REPAIRING":
                    _transition(states, transitions, object_id, "VALID")
        if not parity_valid:
            _transition(states, transitions, parity_id, "REPAIRING")
            if all(page in page_payloads for page in stripe["page_digests"]):
                payload = _xor_payloads(tuple(page_payloads.values()), stripe["length"])
                if digest_bytes(payload) == parity_digest:
                    replace(parity_path, payload, parity_digest, parity_id)
                    _transition(states, transitions, parity_id, "VALID")
                else:
                    _transition(states, transitions, parity_id, "UNAVAILABLE")
                del payload
            else:
                _transition(states, transitions, parity_id, "UNAVAILABLE")
        page_payloads.clear()

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
        Path(cartridge), root_digest, repair=False, capacity_controller=None, source_pages=None
    )


def repair_revision(
    cartridge: str | Path,
    root_digest: str,
    capacity_controller: CapacityTransitionController,
    *,
    source_pages: Mapping[str, bytes] | None = None,
) -> IntegrityReport:
    """Repair exact Q62 identities through store-owned durable transitions."""

    if not isinstance(capacity_controller, CapacityCoordinator):
        _capacity_reject("repair", "repair requires a next-transition controller", "INVALID_REQUEST")
    return _integrity_operation(
        Path(cartridge),
        root_digest,
        repair=True,
        capacity_controller=capacity_controller,
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


def commit_runtime_state(
    cartridge: str | Path,
    parent_root_digest: str,
    session_id: str,
    payload: bytes,
    *,
    capacity_controller: CapacityCoordinator,
) -> GenerationPin:
    """Q20/Q63: publish one native context through the existing page/root/generation transaction."""
    cartridge = Path(cartridge)
    _transaction_id(session_id)
    if not isinstance(payload, bytes) or not payload:
        _q57_reject(session_id, "runtime context must contain nonempty bytes", "INVALID_REQUEST")
    parent = load_root(cartridge, parent_root_digest)
    if not parent["plans"] or parent["plans"][0].get("version") != "native-v1":
        _q57_reject(session_id, "runtime context requires an ordinary-source native plan", "CAPABILITY_MISMATCH")
    material, identity_record = _material_from_provenance(parent["provenance"], parent_root_digest)
    transaction_id = "native-" + digest_bytes(canonical_bytes({
        "parent": parent_root_digest, "session": session_id, "payload": digest_bytes(payload),
    })).split(":")[1]
    pages = tuple(payload[offset:offset + PAGE_BYTES] for offset in range(0, len(payload), PAGE_BYTES))
    additions = stage_training_pages(
        cartridge, pages, capacity_controller=capacity_controller,
        operation_id=session_id, boundary_id=transaction_id,
    )
    locations = _read_index(cartridge, parent_root_digest)
    locations.update({item.page_digest: item for item in additions})
    name = "state." + session_id
    maps = [item for item in parent["tensor_maps"] if item["semantic_tensor_id"] != name]
    spans = tuple(TensorSpan(digest_bytes(page), 0, len(page), offset * PAGE_BYTES)
                  for offset, page in enumerate(pages))
    maps.append(TensorMap(name, (len(payload),), "U8", spans).record())
    required = {span["page_digest"] for item in maps for span in item["spans"]}
    required.update(page for delta in parent["deltas"] for page in delta["ordered_page_digests"])
    candidate = _write_cartridge_root(
        cartridge, material, identity_record, parent["provenance"]["containers"],
        sorted(maps, key=lambda item: item["semantic_tensor_id"]),
        tuple(locations[key] for key in sorted(required)), parent["plans"], parent["deltas"],
        durable=True, capacity_controller=capacity_controller, operation_id=session_id,
        boundary_id=transaction_id,
    )
    return commit_generation(
        cartridge, transaction_id, candidate, expected_parent_root=parent_root_digest,
        capacity_controller=capacity_controller, operation_id=session_id,
    )
