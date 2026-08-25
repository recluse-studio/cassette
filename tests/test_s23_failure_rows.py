# test_s23_failure_rows.py — Q49 failure-row generation and shared-authority preflight; depends on broker.py, errors.py, sources.py, store.py, trainer.py, tests/fixture_server.py.
"""Generate every matrix coordinate and test the shared authorities available before S26."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import errno
import itertools
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys

import pytest

from broker import CanonicalBroker
from errors import CassetteError
from fixture_server import _FIXTURES, _SECRET, source_fixture_server
from sources import SourceAdapter, TransferExtent, transfer_artifact, transfer_state_bytes
import sources as sources_module
from store import (
    ArtifactIdentity,
    CapacityPhase,
    CartridgeLifecycle,
    IdentityTuple,
    canonical_bytes,
    commit_generation,
    digest_bytes,
    import_safetensors,
    initialize_cartridge,
    load_root,
    page_locations,
    pin_generation,
    read_tensor,
    release_capacity,
    reserve_capacity,
)
import store as store_module
import trainer as trainer_module


REPO = Path(__file__).resolve().parent.parent
MATRIX_PATH = REPO / "research" / "ACCEPTANCE_MATRIX.yaml"
CARTRIDGE_UUID = "23000000-0000-4000-8000-000000000023"
FILESYSTEM_UUID = "23000000-0000-4000-8000-000000000024"
WRONG_FILESYSTEM_UUID = "23000000-0000-4000-8000-000000000025"
MODEL_PAYLOAD = b"cassette-s23-generated-model-payload"
GIB = 1024**3

EXPECTED_OPERATIONS = (
    "acquisition",
    "compilation",
    "inference_prefill",
    "inference_decode",
    "training",
    "export",
    "repair",
    "removal",
)
EXPECTED_INJECTIONS = (
    "process_death_at_every_durable_boundary",
    "cartridge_disconnect",
    "reconnect_same_identity",
    "reconnect_wrong_identity",
    "sleep_wake",
    "bus_reset",
    "port_migration",
    "readonly_remount",
    "insufficient_capacity_before_start",
    "insufficient_capacity_during_candidate_write",
    "corrupt_page",
    "corrupt_index",
    "corrupt_root",
    "source_revision_change_during_transfer",
    "invalid_gradient_nan_inf",
    "cancellation",
)
EXPECTED_PHASE_LIVE_INJECTIONS = (
    "cartridge_disconnect",
    "reconnect_same_identity",
    "reconnect_wrong_identity",
    "sleep_wake",
    "bus_reset",
    "port_migration",
    "readonly_remount",
    "insufficient_capacity_before_start",
    "insufficient_capacity_during_candidate_write",
    "source_revision_change_during_transfer",
)
EXPECTED_ASSERTIONS = (
    "no_partial_callable_revision",
    "exact_typed_error",
    "parent_or_exact_child_recovery",
    "no_stale_handle_use",
    "no_uncommitted_token",
    "no_internal_model_file",
)
WRITE_OPERATIONS = frozenset(
    {"acquisition", "compilation", "training", "export", "repair", "removal"}
)


@dataclass(frozen=True)
class _Matrix:
    required: bool
    operations: tuple[str, ...]
    injections: tuple[str, ...]
    phase_live_injections: tuple[str, ...]
    assertions: tuple[str, ...]


@dataclass(frozen=True)
class _Cartridge:
    workspace: Path
    path: Path
    generation: str
    root_digest: str
    root_record: dict
    file_digests: dict[str, str]


@dataclass(frozen=True)
class _Outcome:
    expected_error: str | None
    observed_error: str | None
    stale_attempted: bool = False
    stale_refused: bool = False
    visible_events: tuple[dict, ...] = ()
    committed_events: tuple[dict, ...] = ()


def _failure_matrix() -> _Matrix:
    """Read the bounded failure_rows lists without admitting another YAML dependency."""

    rows: dict[str, object] = {}
    current: str | None = None
    inside = False
    for line in MATRIX_PATH.read_text(encoding="utf-8").splitlines():
        if line == "failure_rows:":
            inside = True
            continue
        if inside and line and not line.startswith(" "):
            break
        if not inside or not line.strip():
            continue
        if line.startswith("  ") and not line.startswith("    ") and ":" in line:
            name, value = line.strip().split(":", 1)
            current = name
            if value.strip():
                rows[name] = value.strip() == "true"
            else:
                rows[name] = []
            continue
        if line.startswith("    - ") and current is not None:
            value = rows.get(current)
            if not isinstance(value, list):
                raise AssertionError(f"failure_rows.{current} mixes scalar and list values")
            value.append(line.removeprefix("    - "))
            continue
        raise AssertionError(f"failure_rows contains unsupported syntax: {line!r}")
    if set(rows) != {
        "required", "expand_over_operations", "injections", "phase_live_injections",
        "assertions",
    }:
        raise AssertionError(f"failure_rows has an incorrect field set: {sorted(rows)}")
    return _Matrix(
        required=rows["required"] is True,
        operations=tuple(rows["expand_over_operations"]),
        injections=tuple(rows["injections"]),
        phase_live_injections=tuple(rows["phase_live_injections"]),
        assertions=tuple(rows["assertions"]),
    )


MATRIX = _failure_matrix()
GENERATED_ROWS = tuple(itertools.product(MATRIX.operations, MATRIX.injections)) or (
    ("missing-operation", "missing-injection"),
)


def _write_safetensors(path: Path, payload: bytes) -> None:
    header = {
        "weight": {
            "dtype": "U8",
            "shape": [len(payload)],
            "data_offsets": [0, len(payload)],
        }
    }
    encoded = json.dumps(header, separators=(",", ":")).encode()
    encoded += b" " * (-len(encoded) % 8)
    path.write_bytes(len(encoded).to_bytes(8, "little") + encoded + payload)


def _identity(source: Path) -> IdentityTuple:
    return IdentityTuple(
        revision_kind="source",
        source_kind="huggingface",
        source_alias="fixture/s23@main",
        canonical_locator="fixture/s23",
        requested_revision="main",
        immutable_revision="git-sha1:" + "2" * 40,
        artifacts=(
            ArtifactIdentity(source.name, source.stat().st_size, digest_bytes(source.read_bytes())),
        ),
        format_versions=(("safetensors", "0.6.2"),),
        tensor_index_digest=digest_bytes(b"S23 tensor index"),
        config_digest=digest_bytes(b"S23 config"),
        architecture="S23GeneratedFailureFixture",
        operator_set=("matmul",),
        tokenizer_digest=digest_bytes(b"S23 tokenizer"),
        processor_digest=digest_bytes(b"S23 processor"),
        template_digest=digest_bytes(b"S23 template"),
        precision_scheme="u8-fixture",
        license_digest=digest_bytes(b"S23 license"),
        parent_ids=(),
        transform_manifest_digest=None,
    )


def _model_file_digests(cartridge: Path) -> dict[str, str]:
    governed = {"cartridge.json", "indexes", "roots", "segments"}
    return {
        str(path.relative_to(cartridge)): digest_bytes(path.read_bytes())
        for path in cartridge.rglob("*")
        if path.is_file() and path.relative_to(cartridge).parts[0] in governed
    }


@pytest.fixture(scope="module")
def cartridge(tmp_path_factory) -> _Cartridge:
    workspace = tmp_path_factory.mktemp("s23-failure-rows")
    source = workspace / "model.safetensors"
    _write_safetensors(source, MODEL_PAYLOAD)
    path = workspace / "cartridge"
    root_digest = import_safetensors({source.name: source}, path, _identity(source))
    generation = commit_generation(
        path,
        "s23-parent-generation",
        root_digest,
        expected_parent_root=None,
    ).generation
    initialize_cartridge(path, CARTRIDGE_UUID)
    source.unlink()
    return _Cartridge(
        workspace,
        path,
        generation,
        root_digest,
        load_root(path, root_digest),
        _model_file_digests(path),
    )


def _request(operation: str, injection: str) -> dict:
    return {
        "protocol_version": "1",
        "operation": operation,
        "idempotency_key": f"s23-{operation}-{injection}",
        "arguments": {},
    }


def _captured(callable_) -> str:
    try:
        callable_()
    except CassetteError as error:
        return error.code
    raise AssertionError("failure injection returned without one typed CassetteError")


def _stale_code(lifecycle: CartridgeLifecycle, access) -> str:
    return _captured(lambda: lifecycle.resolve(access))


def _durable_events(operation_log: Path, operation_id: str) -> tuple[dict, ...]:
    """Read one committed event frontier without using the broker's read path."""

    payload = (operation_log / f"{operation_id}.json").read_bytes()
    envelope = json.loads(payload)
    assert set(envelope) == {"digest", "record"}
    assert canonical_bytes(envelope) == payload
    record = envelope["record"]
    assert envelope["digest"] == digest_bytes(canonical_bytes(record))
    return tuple(record["events"])


def _finish_revalidated(
    lifecycle: CartridgeLifecycle,
    operation: str,
    cartridge: _Cartridge,
    *,
    expected_path: Path | None = None,
) -> None:
    access = lifecycle.begin(f"s23-{operation}-revalidated", write=operation in WRITE_OPERATIONS)
    assert lifecycle.resolve(access) == (expected_path or cartridge.path)
    lifecycle.finish(access)


def _lifecycle_outcome(operation: str, injection: str, cartridge: _Cartridge, monkeypatch) -> _Outcome:
    lifecycle = CartridgeLifecycle(CARTRIDGE_UUID)
    lifecycle.mount(cartridge.path, FILESYSTEM_UUID)
    access = lifecycle.begin(f"s23-{operation}-{injection}", write=operation in WRITE_OPERATIONS)
    assert lifecycle.resolve(access) == cartridge.path

    if injection == "readonly_remount":
        lifecycle.finish(access)
        lifecycle.unmount()
        real_statvfs = os.statvfs

        def readonly_statvfs(path):
            values = list(real_statvfs(path))
            values[8] |= os.ST_RDONLY
            return os.statvfs_result(values)

        monkeypatch.setattr(store_module.os, "statvfs", readonly_statvfs)
        lifecycle.mount(cartridge.path, FILESYSTEM_UUID)
        stale = _stale_code(lifecycle, access) == "CARTRIDGE_DISCONNECTED"
        if operation in WRITE_OPERATIONS:
            code = _captured(
                lambda: lifecycle.begin(f"s23-{operation}-readonly", write=True)
            )
            lifecycle.unmount()
            return _Outcome("CARTRIDGE_READ_ONLY", code, True, stale)
        readonly_access = lifecycle.begin(f"s23-{operation}-readonly", write=False)
        assert lifecycle.resolve(readonly_access) == cartridge.path
        lifecycle.finish(readonly_access)
        lifecycle.unmount()
        return _Outcome(None, None, True, stale)

    if injection == "sleep_wake":
        lifecycle.event("sleep")
        stale = _stale_code(lifecycle, access) == "CARTRIDGE_DISCONNECTED"
        lifecycle.event("wake")
        lifecycle.mount(cartridge.path, FILESYSTEM_UUID)
        _finish_revalidated(lifecycle, operation, cartridge)
        lifecycle.unmount()
        return _Outcome(None, None, True, stale)

    if injection in {"bus_reset", "port_migration"}:
        lifecycle.event(injection)
        stale = _stale_code(lifecycle, access) == "CARTRIDGE_DISCONNECTED"
        lifecycle.mount(cartridge.path, FILESYSTEM_UUID)
        _finish_revalidated(lifecycle, operation, cartridge)
        lifecycle.unmount()
        return _Outcome(None, None, True, stale)

    lifecycle.event("disconnect")
    stale = _stale_code(lifecycle, access) == "CARTRIDGE_DISCONNECTED"
    if injection == "reconnect_same_identity":
        replacement = cartridge.workspace / f"replacement-{operation}"
        shutil.copytree(cartridge.path, replacement)
        try:
            assert _captured(
                lambda: lifecycle.mount(replacement, WRONG_FILESYSTEM_UUID)
            ) == "CARTRIDGE_IDENTITY_MISMATCH"
            identity = lifecycle.mount(
                replacement,
                WRONG_FILESYSTEM_UUID,
                replacement=True,
            )
            assert identity.cartridge_uuid == CARTRIDGE_UUID
            assert identity.filesystem_uuid == WRONG_FILESYSTEM_UUID
            assert (identity.root_generation, identity.root_digest) == (
                cartridge.generation,
                cartridge.root_digest,
            )
            _finish_revalidated(
                lifecycle,
                operation,
                cartridge,
                expected_path=replacement,
            )
            lifecycle.unmount()
        finally:
            shutil.rmtree(replacement, ignore_errors=True)
        return _Outcome(None, None, True, stale)
    if injection == "reconnect_wrong_identity":
        code = _captured(lambda: lifecycle.mount(cartridge.path, WRONG_FILESYSTEM_UUID))
        lifecycle.unmount()
        return _Outcome("CARTRIDGE_IDENTITY_MISMATCH", code, True, stale)

    lifecycle.mount(cartridge.path, FILESYSTEM_UUID)
    _finish_revalidated(lifecycle, operation, cartridge)
    lifecycle.unmount()
    if injection == "cartridge_disconnect":
        return _Outcome("CARTRIDGE_DISCONNECTED", "CARTRIDGE_DISCONNECTED", True, stale)
    return _Outcome(None, None, True, stale)


def _process_death_outcome(operation: str, injection: str, cartridge: _Cartridge) -> _Outcome:
    script = """
import asyncio
import json
import os
import sys
from broker import CanonicalBroker

broker = CanonicalBroker(sys.argv[1])
request = json.loads(sys.argv[2])
boundary = sys.argv[3]
if boundary == "issued":
    broker.issue(request)
    os._exit(73)

async def worker():
    if boundary == "running":
        os._exit(74)
    return {"boundary": "terminal"}

result = asyncio.run(broker.execute(request, worker))
if result["state"] != "SUCCEEDED":
    os._exit(76)
os._exit(75)
"""
    environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    all_visible_events = []
    all_committed_events = []
    observed = None
    for boundary, returncode, state in (
        ("issued", 73, "PENDING"),
        ("running", 74, "RUNNING"),
        ("terminal", 75, "SUCCEEDED"),
    ):
        log = cartridge.workspace / "operation-logs" / f"{operation}-{injection}-{boundary}"
        request = _request(operation, f"{injection}-{boundary}")
        died = subprocess.run(
            [
                sys.executable,
                "-c",
                script,
                str(log),
                json.dumps(request, separators=(",", ":")),
                boundary,
            ],
            cwd=REPO,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        assert died.returncode == returncode and not died.stdout and not died.stderr
        broker = CanonicalBroker(log)
        try:
            operation_id = broker.operation_id(request)
            recovered = broker.status(operation_id)
            assert recovered["state"] == state
            events = broker.events(operation_id)
            if boundary == "issued":
                assert events == ({
                    "run_id": operation_id,
                    "sequence": 0,
                    "type": "started",
                    "payload": {"kind": operation, "phase": "EMPTY"},
                },)
            elif boundary == "running":
                assert [event["type"] for event in events] == ["started", "output_delta"]
            else:
                assert recovered["result"] == {"boundary": "terminal"}
                assert [event["type"] for event in events] == [
                    "started", "output_delta", "completed",
                ]
            if state != "SUCCEEDED":
                cancelled = broker.cancel(operation_id)
                assert cancelled["state"] == "CANCELLED"
                observed = cancelled["error"]["code"]
                events = broker.events(operation_id)
            all_visible_events.extend(events)
            all_committed_events.extend(_durable_events(log, operation_id))
        finally:
            broker.close()
    return _Outcome(
        "OPERATION_CANCELLED",
        observed,
        visible_events=tuple(all_visible_events),
        committed_events=tuple(all_committed_events),
    )


def _capacity_before_outcome(operation: str, injection: str) -> _Outcome:
    allocator_calls = []
    code = _captured(lambda: reserve_capacity(
        f"s23-{operation}-capacity-before",
        device_bytes=100 * GIB,
        allocatable_verified_free=8 * GIB,
        phases=(CapacityPhase(candidate=1),),
        reserve_extent=lambda length: allocator_calls.append(length) is None,
        release_extent=lambda _: True,
    ))
    assert allocator_calls == []
    return _Outcome("CAPACITY_EXCEEDED", code)


def _capacity_during_outcome(operation: str, injection: str, cartridge: _Cartridge, monkeypatch) -> _Outcome:
    partials = cartridge.workspace / "partials"
    partials.mkdir(exist_ok=True)
    path = partials / f"{operation}-{injection}"
    descriptor = os.open(path, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
    os.ftruncate(descriptor, 4)
    extent = TransferExtent(descriptor, 0, 4, f"s23-{operation}-capacity-during")
    real_pwrite = os.pwrite
    writes = 0

    def exhausted_pwrite(fd, payload, offset):
        nonlocal writes
        writes += 1
        if writes == 1:
            return real_pwrite(fd, payload[:1], offset)
        raise OSError(errno.ENOSPC, "fixture extent exhausted")

    monkeypatch.setattr(sources_module.os, "pwrite", exhausted_pwrite)
    try:
        code = _captured(
            lambda: sources_module._pwrite_all(extent, 0, b"four", extent.operation_id)
        )
        assert writes == 2
    finally:
        os.close(descriptor)
        path.unlink(missing_ok=True)
    return _Outcome("CAPACITY_EXCEEDED", code)


def _corruption_outcome(operation: str, injection: str, cartridge: _Cartridge) -> _Outcome:
    location = page_locations(cartridge.path, cartridge.root_digest)[0]
    if injection == "corrupt_page":
        path = cartridge.path / "segments" / location.segment_id.removeprefix("blake3:")
        offset = location.offset
        expected = "PAGE_CORRUPT"
        use = lambda: read_tensor(cartridge.path, cartridge.root_digest, "weight")
    elif injection == "corrupt_index":
        path = cartridge.path / "indexes" / cartridge.root_digest.removeprefix("blake3:")
        offset = 0
        expected = "ROOT_INVALID"
        use = lambda: load_root(cartridge.path, cartridge.root_digest)
    else:
        path = cartridge.path / "roots" / cartridge.root_digest.removeprefix("blake3:")
        offset = 0
        expected = "ROOT_INVALID"
        use = lambda: load_root(cartridge.path, cartridge.root_digest)
    original = path.read_bytes()
    changed = bytearray(original)
    changed[offset] ^= 0xFF
    path.write_bytes(changed)
    try:
        code = _captured(use)
    finally:
        path.write_bytes(original)
    return _Outcome(expected, code)


def _source_revision_outcome(
    operation: str,
    injection: str,
    cartridge: _Cartridge,
) -> _Outcome:
    fixture = _FIXTURES["huggingface"]
    descriptor = {
        "kind": "huggingface",
        "locator": fixture["locator"],
        "revision": fixture["alias"],
        "credential_ref": f"keychain:s23/{operation}",
        "license_acceptance_ref": f"license:s23/{operation}",
        "expected_identity": fixture["identity"],
    }
    with source_fixture_server() as server:
        adapter = SourceAdapter(
            "huggingface", server.base_url, {descriptor["credential_ref"]: _SECRET}.get
        )
        revision = asyncio.run(adapter.resolve(descriptor))
        artifact = revision.artifacts[0]
        operation_id = f"s23-{operation}-source-change"
        partials = cartridge.workspace / "partials"
        partials.mkdir(exist_ok=True)
        data_path = partials / f"{operation}-{injection}.partial"
        state_path = partials / f"{operation}-{injection}.transfer"
        data_fd = os.open(data_path, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
        state_fd = os.open(state_path, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
        state_bytes = transfer_state_bytes(artifact.size)
        os.ftruncate(data_fd, artifact.size)
        os.ftruncate(state_fd, state_bytes)
        data_extent = TransferExtent(data_fd, 0, artifact.size, operation_id)
        state_extent = TransferExtent(state_fd, 0, state_bytes, operation_id)
        transfer_bytes = artifact.size + state_bytes
        reservation = reserve_capacity(
            operation_id,
            device_bytes=100 * GIB,
            allocatable_verified_free=8 * GIB + transfer_bytes,
            phases=(CapacityPhase(inflight=transfer_bytes),),
            reserve_extent=lambda length: length == 8 * GIB + transfer_bytes,
            release_extent=lambda _: True,
        )
        server.range_validator_overrides[("huggingface", artifact.path, 0)] = '"s23-v2"'
        try:
            code = _captured(lambda: asyncio.run(transfer_artifact(
                adapter,
                revision,
                artifact,
                data_extent,
                state_extent,
                reservation,
            )))
            assert os.pread(data_fd, artifact.size, 0) == bytes(artifact.size)
        finally:
            release_capacity(reservation)
            os.close(data_fd)
            os.close(state_fd)
            data_path.unlink(missing_ok=True)
            state_path.unlink(missing_ok=True)
    return _Outcome("SOURCE_REVISION_CHANGED", code)


def _gradient_outcome(operation: str, injection: str) -> _Outcome:
    payload = trainer_module._tensor_page(
        "gradient",
        f"s23-{operation}",
        (1,),
        struct.pack("<f", float("nan")),
    )
    code = _captured(lambda: trainer_module._tensor_values(
        payload,
        f"s23-{operation}-gradient",
        "gradient",
        f"s23-{operation}",
        (1,),
    ))
    return _Outcome("GRADIENT_INVALID", code)


def _cancellation_outcome(operation: str, injection: str, cartridge: _Cartridge) -> _Outcome:
    log = cartridge.workspace / "operation-logs" / f"{operation}-{injection}"
    broker = CanonicalBroker(log)
    request = _request(operation, injection)

    async def run():
        started = asyncio.Event()

        async def worker():
            started.set()
            await asyncio.Event().wait()

        task = asyncio.create_task(broker.execute(request, worker))
        await asyncio.wait_for(started.wait(), timeout=5)
        operation_id = broker.operation_id(request)
        assert broker.cancel(operation_id)["state"] == "RUNNING"
        result = await asyncio.wait_for(task, timeout=5)
        return result, broker.events(operation_id)

    try:
        result, events = asyncio.run(run())
        assert result["state"] == "CANCELLED"
        operation_id = broker.operation_id(request)
        return _Outcome(
            "OPERATION_CANCELLED",
            result["error"]["code"],
            visible_events=events,
            committed_events=_durable_events(log, operation_id),
        )
    finally:
        broker.close()


def _inject(operation: str, injection: str, cartridge: _Cartridge, monkeypatch) -> _Outcome:
    if injection == "process_death_at_every_durable_boundary":
        return _process_death_outcome(operation, injection, cartridge)
    if injection in {
        "cartridge_disconnect",
        "reconnect_same_identity",
        "reconnect_wrong_identity",
        "sleep_wake",
        "bus_reset",
        "port_migration",
        "readonly_remount",
    }:
        return _lifecycle_outcome(operation, injection, cartridge, monkeypatch)
    if injection == "insufficient_capacity_before_start":
        return _capacity_before_outcome(operation, injection)
    if injection == "insufficient_capacity_during_candidate_write":
        return _capacity_during_outcome(operation, injection, cartridge, monkeypatch)
    if injection in {"corrupt_page", "corrupt_index", "corrupt_root"}:
        return _corruption_outcome(operation, injection, cartridge)
    if injection == "source_revision_change_during_transfer":
        return _source_revision_outcome(operation, injection, cartridge)
    if injection == "invalid_gradient_nan_inf":
        return _gradient_outcome(operation, injection)
    if injection == "cancellation":
        return _cancellation_outcome(operation, injection, cartridge)
    raise AssertionError(f"matrix injection {injection!r} has no machine executor")


def _no_partial_callable_revision(cartridge: _Cartridge, _outcome: _Outcome) -> None:
    pin = pin_generation(cartridge.path)
    assert pin is not None
    assert (pin.generation, pin.root_digest) == (
        cartridge.generation,
        cartridge.root_digest,
    )
    assert not tuple(cartridge.path.rglob("*.generation-candidate"))
    assert not tuple(cartridge.path.rglob("*.pending"))


def _exact_typed_error(_cartridge: _Cartridge, outcome: _Outcome) -> None:
    assert outcome.observed_error == outcome.expected_error


def _parent_or_exact_child_recovery(cartridge: _Cartridge, _outcome: _Outcome) -> None:
    assert _model_file_digests(cartridge.path) == cartridge.file_digests
    assert load_root(cartridge.path, cartridge.root_digest) == cartridge.root_record


def _no_stale_handle_use(_cartridge: _Cartridge, outcome: _Outcome) -> None:
    assert not outcome.stale_attempted or outcome.stale_refused


def _no_uncommitted_token(_cartridge: _Cartridge, outcome: _Outcome) -> None:
    assert outcome.visible_events == outcome.committed_events


def _no_internal_model_file(cartridge: _Cartridge, _outcome: _Outcome) -> None:
    carriers = []
    for path in cartridge.workspace.rglob("*"):
        if not path.is_file():
            continue
        try:
            contains_model = MODEL_PAYLOAD in path.read_bytes()
        except OSError:
            contains_model = False
        if contains_model:
            carriers.append(path)
    assert carriers
    assert all(path.is_relative_to(cartridge.path / "segments") for path in carriers)


ASSERTION_EXECUTORS = {
    "no_partial_callable_revision": _no_partial_callable_revision,
    "exact_typed_error": _exact_typed_error,
    "parent_or_exact_child_recovery": _parent_or_exact_child_recovery,
    "no_stale_handle_use": _no_stale_handle_use,
    "no_uncommitted_token": _no_uncommitted_token,
    "no_internal_model_file": _no_internal_model_file,
}


@pytest.mark.parametrize(
    ("operation", "injection"),
    GENERATED_ROWS,
    ids=lambda value: value,
)
def test_q49_failure_rows_generate_complete_matrix_and_execute_shared_authorities(
    operation,
    injection,
    cartridge,
    monkeypatch,
):
    """Q49/failure_rows: generate every coordinate and execute its shared-authority preflight."""

    assert MATRIX == _Matrix(
        True,
        EXPECTED_OPERATIONS,
        EXPECTED_INJECTIONS,
        EXPECTED_PHASE_LIVE_INJECTIONS,
        EXPECTED_ASSERTIONS,
    )
    assert len(GENERATED_ROWS) == 128
    assert set(WRITE_OPERATIONS) <= set(MATRIX.operations)
    assert set(ASSERTION_EXECUTORS) == set(MATRIX.assertions)
    outcome = _inject(operation, injection, cartridge, monkeypatch)
    for assertion in MATRIX.assertions:
        ASSERTION_EXECUTORS[assertion](cartridge, outcome)
    if operation == "acquisition" and injection == "process_death_at_every_durable_boundary":
        hostile_events = list(outcome.visible_events)
        output_index = next(
            index for index, event in enumerate(hostile_events)
            if event["type"] == "output_delta"
        )
        output_event = hostile_events[output_index]
        hostile_events[output_index] = {
            **output_event,
            "payload": {**output_event["payload"], "output": "uncommitted-token"},
        }
        hostile = _Outcome(
            outcome.expected_error,
            outcome.observed_error,
            outcome.stale_attempted,
            outcome.stale_refused,
            tuple(hostile_events),
            outcome.committed_events,
        )
        with pytest.raises(AssertionError):
            _no_uncommitted_token(cartridge, hostile)
