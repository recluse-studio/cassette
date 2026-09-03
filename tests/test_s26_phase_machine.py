# test_s26_phase_machine.py — S26 concrete-operation failure gate (Q49); depends on broker.py, compiler.py, errors.py, pager.py, sources.py, store.py, trainer.py, tests/fixture_server.py, tests/test_s07_integrity_capacity.py, tests/test_s15_pager.py, tests/test_s21_trainer.py, tests/test_s23_failure_rows.py, tests/test_s24_interoperability.py.
"""Execute every generated failure coordinate through one concrete product entrypoint."""

from __future__ import annotations

import asyncio
from contextlib import ExitStack
from copy import deepcopy
from dataclasses import dataclass
import os
from pathlib import Path
import platform
import shutil
import stat
import sys

import pytest

from broker import AcquisitionContext, CanonicalBroker
from compiler import compilation_specification, recompile_revision
from errors import CassetteError
import fixture_server
import pager
from sources import SourceAdapter, grant_transfer_extent, transfer_state_bytes
from store import (
    CapacityCoordinator,
    CartridgeLifecycle,
    commit_generation,
    create_repair_set,
    digest_bytes,
    import_safetensors,
    initialize_cartridge,
    load_root,
    model_identity,
    page_locations,
    pin_generation,
    repair_revision,
    revision_reachability,
)
import store as store_module
import trainer
from test_s05_store import _identity as _fixture_identity, _write_safetensors
from test_s07_integrity_capacity import _identity as _storage_identity
from test_s07_integrity_capacity import _write_safetensors as _write_storage_source
from test_s15_pager import (
    ATTENTION_OUTPUT,
    DECODE_TOKENS,
    EMBEDDING,
    FFN_DOWN,
    KEY,
    NORM_ATTENTION,
    NORM_FFN,
    NORM_FINAL,
    PREFILL_TOKENS,
    QUERY,
    TARGET,
    UNEMBEDDING,
    VALUE,
    ZERO,
    _correction,
    _fixture as _transformer_contract,
    _payload,
    _selection as _transformer_selection,
    _shape,
    _transpose,
)
from test_s21_trainer import (
    SFT_BATCHES,
    _quantized_parent,
    _training_profile,
    advance_training as _advance_training,
)
from test_s23_failure_rows import (
    EXPECTED_ASSERTIONS,
    EXPECTED_INJECTIONS,
    EXPECTED_OPERATIONS,
    GENERATED_ROWS,
    MATRIX,
    _Cartridge as _S23Cartridge,
    _process_death_outcome,
)
from test_s24_interoperability import _machine_replay, _s24_artifact


pytestmark = pytest.mark.skipif(
    platform.system() != "Darwin" or platform.machine() != "arm64",
    reason="S26 requires arm64 macOS, the pinned MLX runtime, and F_FULLFSYNC",
)

CARTRIDGE_UUID = "26000000-0000-4000-8000-000000000026"
FILESYSTEM_UUID = "26000000-0000-4000-8000-000000000027"
WRONG_FILESYSTEM_UUID = "26000000-0000-4000-8000-000000000028"
WRITE_OPERATIONS = frozenset({
    "acquisition", "compilation", "training", "export", "repair", "removal",
})
LIFECYCLE_INJECTIONS = frozenset({
    "cartridge_disconnect", "reconnect_same_identity", "reconnect_wrong_identity",
    "sleep_wake", "bus_reset", "port_migration", "readonly_remount",
})
RECEIPT_FIELDS = {
    "acquisition": "phase",
    "compilation": "candidate_root",
    "inference_prefill": "trace_phase",
    "inference_decode": "trace_phase",
    "training": "work_root",
    "export": "export_id",
    "repair": "root_digest",
    "removal": "removed_root",
}


@dataclass(frozen=True)
class _Call:
    entrypoint: str
    entrypoint_hit: bool
    error: str | None
    receipt: dict
    delivered: tuple[str, ...] = ()
    committed: tuple[str, ...] = ()


@dataclass
class _Route:
    operation: str
    cartridge: Path
    parent_root: str
    write: bool
    invoke: object
    close: object
    arm: object = lambda _path: None
    corrupt_page: str | None = None
    source_files: tuple[Path, ...] = ()


def _capacity_coordinator(cartridge: Path, injection: str, monkeypatch) -> CapacityCoordinator:
    """Use store-owned coordination while making only Q53 free-space observations deterministic."""

    coordinator = CapacityCoordinator(cartridge)
    if injection not in {
        "insufficient_capacity_before_start",
        "insufficient_capacity_during_candidate_write",
    }:
        return coordinator
    observed = store_module.os.statvfs
    reads = 0

    def measured(path):
        nonlocal reads
        snapshot = observed(path)
        reads += 1
        if injection == "insufficient_capacity_before_start" or reads > 1:
            values = list(snapshot)
            values[4] = 0
            return os.statvfs_result(values)
        return snapshot

    monkeypatch.setattr(store_module.os, "statvfs", measured)
    return coordinator


@dataclass(frozen=True)
class _Outcome:
    operation: str
    injection: str
    call: _Call
    expected_error: str | None
    cartridge: Path
    parent_root: str
    final_root: str
    allowed_roots: tuple[str, ...]
    stale_attempted: bool
    stale_refused: bool
    auxiliary_errors: tuple[str, ...]
    source_files: tuple[Path, ...]


def _probe(entrypoint, invocation):
    """Observe one exact public function code object without patching repository behavior."""

    hit = False
    prior = sys.getprofile()

    def profile(frame, event, _argument):
        nonlocal hit
        if event == "call" and frame.f_code is entrypoint.__code__:
            hit = True

    sys.setprofile(profile)
    try:
        try:
            result = invocation()
        except BaseException as error:
            return hit, None, error
        return hit, result, None
    finally:
        sys.setprofile(prior)


def _capture(entrypoint, invocation, receipt):
    hit, result, raised = _probe(entrypoint, invocation)
    if raised is not None:
        if isinstance(raised, CassetteError):
            return _Call(
                f"{entrypoint.__module__}.{entrypoint.__qualname__}", hit, raised.code, {}
            )
        raise raised
    if isinstance(result, dict) and result.get("state") in {"FAILED", "CANCELLED"}:
        return _Call(
            f"{entrypoint.__module__}.{entrypoint.__qualname__}",
            hit,
            result["error"]["code"],
            {},
        )
    if isinstance(result, dict) and result.get("state") == "PAUSED":
        return _Call(
            f"{entrypoint.__module__}.{entrypoint.__qualname__}",
            hit,
            "CAPACITY_EXCEEDED",
            {},
        )
    return _Call(
        f"{entrypoint.__module__}.{entrypoint.__qualname__}",
        hit,
        None,
        receipt(result),
    )


def _extent(
    cartridge: Path,
    operation_id: str,
    extent_id: str,
    length: int,
    capacity_coordinator: CapacityCoordinator,
):
    extent = grant_transfer_extent(
        cartridge,
        operation_id,
        extent_id,
        length,
        capacity_controller=capacity_coordinator,
    )
    return extent.fd, extent


def _initialize(cartridge: Path) -> None:
    initialize_cartridge(cartridge, CARTRIDGE_UUID)


def _delete_sources(directory: Path) -> tuple[Path, ...]:
    sources = tuple(directory.glob("*.safetensors"))
    for source in sources:
        source.unlink()
    return sources


def _store_snapshot(cartridge: Path) -> dict[str, str]:
    """Bind every immutable or callable store object before a failure injection."""

    authorities = {"generations", "indexes", "roots", "segments"}
    return {
        str(path.relative_to(cartridge)): digest_bytes(path.read_bytes())
        for path in cartridge.rglob("*")
        if path.is_file() and path.relative_to(cartridge).parts[0] in authorities
    }


def _storage_base(directory: Path):
    cartridge, root, parameters = _quantized_parent(directory)
    sources = _delete_sources(directory)
    _initialize(cartridge)
    return cartridge, root, parameters, sources


def _transformer_base(directory: Path):
    cartridge = directory / "cartridge"
    values = {
        "embedding": EMBEDDING,
        "norm_attention": NORM_ATTENTION,
        "query": QUERY,
        "key": KEY,
        "value": VALUE,
        "attention_output": ATTENTION_OUTPUT,
        "norm_ffn": NORM_FFN,
        "exact.base": _transpose(TARGET),
        "fresh.base": _transpose(ZERO),
        "ffn_down": FFN_DOWN,
        "norm_final": NORM_FINAL,
        "unembedding": UNEMBEDDING,
        "exact.correction": _transpose(ZERO),
        **{
            f"fresh.unit{unit}": _transpose(_correction(unit))
            for unit in range(4)
        },
    }
    sources = {}
    directory.mkdir(parents=True, exist_ok=True)
    for name, tensor in values.items():
        source = directory / f"{name}.safetensors"
        _write_safetensors(
            source,
            ((name, "F32", _shape(tensor), _payload(tensor)),),
        )
        sources[source.name] = source
    root = import_safetensors(sources, cartridge, _fixture_identity(*sources.values()))
    commit_generation(cartridge, "s26-transformer-root", root, expected_parent_root=None)
    _initialize(cartridge)
    root_record = load_root(cartridge, root)
    pages = {
        row["semantic_tensor_id"]: row["spans"][0]["page_digest"]
        for row in root_record["tensor_maps"]
    }
    contract = _transformer_contract(root, pages)
    source_paths = tuple(sources.values())
    for source in source_paths:
        source.unlink()
    return cartridge, root, contract, pages["exact.base"], source_paths


def _acquisition_route(directory: Path, monkeypatch) -> _Route:
    cartridge, parent, _, sources = _storage_base(directory / "base")
    payload, material, _ = _s24_artifact()
    fixture = fixture_server._FIXTURES["huggingface"]
    source_identity = model_identity(material)
    monkeypatch.setitem(fixture, "identity", source_identity)
    stack = ExitStack()
    server = stack.enter_context(source_fixture_server_with_material(material, payload))
    counter = 0

    def invoke(pathlike, injection, _armed=None):
        nonlocal counter
        counter += 1
        log = directory / f"acquisition-log-{counter}"
        broker = CanonicalBroker(log)
        request = {
            "protocol_version": "1",
            "operation": "prepare",
            "idempotency_key": f"s26-acquisition-{counter}-{injection}",
            "target": "cartridge:s26:acquisition",
            "arguments": {"source": {
                "kind": "huggingface",
                "locator": fixture["locator"],
                "revision": fixture["alias"],
                "credential_ref": "keychain:s26/acquisition",
                "license_acceptance_ref": "license:s26/acquisition",
                "expected_identity": source_identity,
            }},
        }
        operation_id = broker.operation_id(request)
        try:
            extent_cartridge = Path(pathlike)
        except CassetteError:
            extent_cartridge = cartridge
        grant_coordinator = CapacityCoordinator(extent_cartridge)
        data_fd, data_extent = _extent(
            extent_cartridge,
            operation_id,
            f"s26-acquisition-{counter}-data",
            len(payload),
            grant_coordinator,
        )
        state_length = transfer_state_bytes(len(payload))
        state_fd, state_extent = _extent(
            extent_cartridge,
            operation_id,
            f"s26-acquisition-{counter}-state",
            state_length,
            grant_coordinator,
        )
        capacity = _capacity_coordinator(extent_cartridge, injection, monkeypatch)
        if injection == "source_revision_change_during_transfer":
            server.range_validator_overrides[("huggingface", material.artifacts[0].path, 0)] = '"s26-v2"'
        if injection == "cancellation":
            broker.issue(request)
            broker.cancel(operation_id)
        context = AcquisitionContext(
            SourceAdapter(
                "huggingface",
                server.base_url,
                {"keychain:s26/acquisition": fixture_server._SECRET}.get,
            ),
            capacity,
            {material.artifacts[0].path: (data_extent, state_extent)},
            pathlike,
        )
        try:
            return _capture(
                CanonicalBroker.run_acquisition,
                lambda: asyncio.run(broker.run_acquisition(request, context)),
                lambda result: {
                    "phase": "ACTIVE",
                    "root_digest": broker.callable_revision(
                        operation_id, pathlike
                    ).root_digest,
                },
            )
        finally:
            os.close(data_fd)
            os.close(state_fd)
            broker.close()
            assert capacity.active_claims() == ()

    return _Route(
        "acquisition", cartridge, parent, True, invoke, stack.close,
        source_files=sources,
    )


def source_fixture_server_with_material(material, payload):
    return fixture_server.source_fixture_server(
        artifact_overrides={
            "huggingface": ((material.artifacts[0].path, payload, '"s26-v1"'),)
        }
    )


def _compilation_route(directory: Path, monkeypatch) -> _Route:
    directory.mkdir(parents=True)
    payload, material, _ = _s24_artifact()
    acquired, cartridge, broker = _machine_replay(
        directory, monkeypatch, "huggingface", payload, material
    )
    assert acquired["state"] == "SUCCEEDED", acquired
    _initialize(cartridge)
    compiled_root = acquired["result"]["root_digest"]
    specification = compilation_specification(cartridge, compiled_root)
    counter = 0

    def invoke(pathlike, injection, _armed=None):
        nonlocal counter
        counter += 1
        before = _store_snapshot(cartridge)
        candidate = deepcopy(specification)
        if injection == "source_revision_change_during_transfer":
            candidate["source_root"] = digest_bytes(b"s26-foreign-source-root")
        if injection in {
            "insufficient_capacity_before_start",
            "insufficient_capacity_during_candidate_write",
        }:
            candidate["profile"]["other_observed_bytes"] += 1
        capacity = _capacity_coordinator(cartridge, injection, monkeypatch)

        call = _capture(
            recompile_revision,
            lambda: recompile_revision(
                pathlike,
                candidate,
                compiled_root,
                operation_id=f"s26-compilation-{counter}",
                capacity_coordinator=capacity,
            ),
            lambda result: {"candidate_root": result.candidate_root},
        )
        if injection == "insufficient_capacity_before_start":
            assert capacity.active_claims() == ()
            assert _store_snapshot(cartridge) == before
        elif injection == "insufficient_capacity_during_candidate_write":
            assert capacity.active_claims() == ()
            assert _store_snapshot(cartridge) == before
        else:
            assert capacity.active_claims() == ()
        return _cancel_after_concrete(directory, call, injection, "compilation")

    return _Route(
        "compilation", cartridge, compiled_root, True, invoke, broker.close
    )


def _transformer_route(directory: Path, operation: str) -> _Route:
    cartridge, root, contract, corrupt_page, sources = _transformer_base(directory)
    plan, certificate, evidence, profile, page_map = contract

    def arm(pathlike):
        return pager.CertifiedTransformer(
            pathlike, plan, certificate, evidence, profile, page_map
        )

    def invoke(pathlike, injection, armed=None):
        executor = armed
        if executor is None:
            hit, executor, raised = _probe(
                pager.CertifiedTransformer.__init__, lambda: arm(pathlike)
            )
            if raised is not None:
                if isinstance(raised, CassetteError):
                    return _Call(
                        "pager.CertifiedTransformer.__init__", hit, raised.code, {}
                    )
                raise raised
        if injection in {
            "insufficient_capacity_before_start",
            "insufficient_capacity_during_candidate_write",
        }:
            executor._profile["runtime_buffer_bytes"] += 1
        cancel = asyncio.Event()
        if injection == "cancellation":
            cancel.set()

        async def execute():
            if operation == "inference_prefill":
                return await executor.execute_token(
                    _transformer_selection(certificate, evidence, 0),
                    PREFILL_TOKENS,
                    cancel_event=cancel,
                )
            prefill = await executor.execute_token(
                _transformer_selection(certificate, evidence, 0), PREFILL_TOKENS
            )
            try:
                result = await executor.execute_token(
                    _transformer_selection(certificate, evidence, 1, 7),
                    DECODE_TOKENS,
                    cancel_event=cancel,
                )
            except CassetteError:
                executor._s26_prefill = prefill
                raise
            return result

        try:
            hit, result, raised = _probe(
                pager.CertifiedTransformer.execute_token,
                lambda: asyncio.run(execute()),
            )
        except CassetteError as error:
            committed = ()
            if operation == "inference_prefill" and executor.last_transformer is not None:
                committed = (executor.last_transformer.logits_digest,)
            return _Call(
                "pager.CertifiedTransformer.execute_token", True, error.code, {}, (), committed
            )
        if raised is not None:
            if not isinstance(raised, CassetteError):
                raise raised
            committed = ()
            if operation == "inference_prefill" and executor.last_transformer is not None:
                committed = (executor.last_transformer.logits_digest,)
            return _Call(
                "pager.CertifiedTransformer.execute_token",
                hit,
                raised.code,
                {},
                (),
                committed,
            )
        digest = result.logits_digest
        delivered = () if injection == "process_death_at_every_durable_boundary" else (digest,)
        return _Call(
            "pager.CertifiedTransformer.execute_token",
            hit,
            None,
            {"trace_phase": result.trace.phase, "logits_digest": digest},
            delivered,
            (executor.last_transformer.logits_digest,),
        )

    return _Route(
        operation,
        cartridge,
        root,
        False,
        invoke,
        lambda: None,
        arm,
        corrupt_page,
        sources,
    )


def _training_route(directory: Path, monkeypatch) -> _Route:
    cartridge, parent, parameters, sources = _storage_base(directory)
    options = {
        "random_seed": 17,
        "window_limit_bytes": 32 * 1024,
        "calibration_records": (),
        "delta_precision": "FP32",
    }
    def training_admission(objectives, injection: str):
        workload = trainer.training_workload(
            cartridge, parent, "ADAPTER_SFT", parameters, objectives, **options
        )
        capacity = _capacity_coordinator(cartridge, injection, monkeypatch)
        return trainer.admit_training(
            workload,
            _training_profile(workload.request_digest),
            capacity_coordinator=capacity,
        ), capacity

    admission, admitted_capacity = training_admission((SFT_BATCHES[0],), "training")

    def invoke(pathlike, injection, _armed=None):
        if injection in {
            "insufficient_capacity_before_start",
            "insufficient_capacity_during_candidate_write",
        }:
            hostile_admission, capacity = training_admission((SFT_BATCHES[0],), injection)
            call = _capture(
                trainer.prepare_training,
                lambda: trainer.prepare_training(
                    pathlike,
                    parent,
                    "ADAPTER_SFT",
                    parameters,
                    (SFT_BATCHES[0],),
                    admission=hostile_admission,
                    **options,
                ),
                lambda _result: {"work_root": "unexpected"},
            )
            assert capacity.active_claims() == ()
            return call
        objectives = (SFT_BATCHES[0],)
        if injection == "invalid_gradient_nan_inf":
            objectives = ((3.0e38,) * 10,)
            hostile_admission, hostile_capacity = training_admission(objectives, injection)
            checkpoint = trainer.prepare_training(
                pathlike,
                parent,
                "ADAPTER_SFT",
                parameters,
                objectives,
                admission=hostile_admission,
                **options,
            )
            call = _capture(
                trainer.advance_training,
                lambda: _advance_training(pathlike, checkpoint),
                lambda result: {"work_root": result.work_root},
            )
            assert hostile_capacity.active_claims() == ()
        else:
            call = _capture(
                trainer.prepare_training,
                lambda: trainer.prepare_training(
                    pathlike,
                    parent,
                    "ADAPTER_SFT",
                    parameters,
                    objectives,
                    admission=admission,
                    **options,
                ),
                lambda result: {"work_root": result.work_root},
            )
        assert admitted_capacity.active_claims() == ()
        return _cancel_after_concrete(directory, call, injection, "training")

    def close():
        return None

    return _Route(
        "training", cartridge, parent, True, invoke, close,
        source_files=sources,
    )


def _export_route(directory: Path, monkeypatch) -> _Route:
    cartridge, root, _, sources = _storage_base(directory)
    counter = 0

    def invoke(pathlike, injection, _armed=None):
        nonlocal counter
        counter += 1
        broker = CanonicalBroker(directory / f"export-log-{counter}")
        request = {
            "protocol_version": "1",
            "operation": "export",
            "idempotency_key": f"s26-export-{counter}",
            "target": root,
            "arguments": {"target_schema": "safetensors-v1"},
        }
        operation_id = broker.operation_id(request)
        capacity = _capacity_coordinator(cartridge, injection, monkeypatch)
        if injection == "cancellation":
            broker.issue(request)
            broker.cancel(operation_id)
        try:
            return _capture(
                CanonicalBroker.export_revision,
                lambda: asyncio.run(broker.export_revision(request, pathlike, capacity)),
                lambda result: {
                    "export_id": result["result"]["export_id"],
                    "artifact_digest": result["result"]["artifact_digest"],
                },
            )
        finally:
            broker.close()
            assert capacity.active_claims() == ()

    return _Route(
        "export", cartridge, root, True, invoke, lambda: None,
        source_files=sources,
    )


def _repair_route(directory: Path, monkeypatch) -> _Route:
    cartridge, root, _, sources = _storage_base(directory)
    setup_capacity = _capacity_coordinator(cartridge, "setup", monkeypatch)
    repair_set = create_repair_set(cartridge, root, setup_capacity)
    assert setup_capacity.active_claims() == ()

    def invoke(pathlike, injection, _armed=None):
        capacity = _capacity_coordinator(cartridge, injection, monkeypatch)
        if injection in {
            "insufficient_capacity_before_start",
            "insufficient_capacity_during_candidate_write",
        }:
            parity = repair_set.parity_digests[0]
            (cartridge / "repair" / "objects" / parity[7:]).unlink()
        try:
            call = _capture(
                repair_revision,
                lambda: repair_revision(pathlike, root, capacity),
                lambda result: {"root_digest": result.root_digest, "available": result.available},
            )
            return _cancel_after_concrete(directory, call, injection, "repair")
        finally:
            assert capacity.active_claims() == ()

    return _Route(
        "repair", cartridge, root, True, invoke, lambda: None,
        source_files=sources,
    )


def _removal_route(directory: Path, monkeypatch) -> _Route:
    cartridge, root, _, sources = _storage_base(directory / "base")
    orphan_source = directory / "orphan.safetensors"
    _write_storage_source(orphan_source, "orphan", b"s26-unreachable-revision")
    orphan = import_safetensors(
        {orphan_source.name: orphan_source}, cartridge, _storage_identity(orphan_source)
    )
    orphan_source.unlink()
    sources = (*sources, orphan_source)
    proof = revision_reachability(cartridge, orphan)
    counter = 0

    def invoke(pathlike, injection, _armed=None):
        nonlocal counter
        counter += 1
        broker = CanonicalBroker(directory / f"removal-log-{counter}")
        request = {
            "protocol_version": "1",
            "operation": "remove_revision",
            "idempotency_key": f"s26-remove-{counter}",
            "target": orphan,
            "arguments": {"reachability_digest": proof["reachability_digest"]},
        }
        operation_id = broker.operation_id(request)
        capacity = _capacity_coordinator(cartridge, injection, monkeypatch)
        if injection == "cancellation":
            broker.issue(request)
            broker.cancel(operation_id)
        try:
            return _capture(
                CanonicalBroker.remove_revision,
                lambda: asyncio.run(
                    broker.remove_revision(request, pathlike, proof, capacity)
                ),
                lambda result: {"removed_root": result["result"]["removed_root"]},
            )
        finally:
            broker.close()
            assert capacity.active_claims() == ()

    return _Route(
        "removal", cartridge, root, True, invoke, lambda: None,
        source_files=sources,
    )


ROUTES = {
    "acquisition": _acquisition_route,
    "compilation": _compilation_route,
    "inference_prefill": lambda path, patch: _transformer_route(path, "inference_prefill"),
    "inference_decode": lambda path, patch: _transformer_route(path, "inference_decode"),
    "training": _training_route,
    "export": _export_route,
    "repair": _repair_route,
    "removal": _removal_route,
}


def _cancel_after_concrete(directory: Path, call: _Call, injection: str, operation: str) -> _Call:
    if injection != "cancellation" or call.error is not None:
        return call
    broker = CanonicalBroker(directory / f"{operation}-cancel-log")
    request = {
        "protocol_version": "1",
        "operation": operation,
        "idempotency_key": f"s26-{operation}-cancel",
        "arguments": {},
    }
    operation_id = broker.operation_id(request)
    try:
        broker.issue(request)
        broker.cancel(operation_id)
        result = asyncio.run(broker.execute(request, lambda: {"forbidden": True}))
        return _Call(
            call.entrypoint,
            call.entrypoint_hit,
            result["error"]["code"],
            call.receipt,
            call.delivered,
            call.committed,
        )
    finally:
        broker.close()


def _corrupt(route: _Route, injection: str):
    if injection not in {"corrupt_page", "corrupt_index", "corrupt_root"}:
        return lambda: None
    if injection == "corrupt_page":
        page_digest = route.corrupt_page or page_locations(route.cartridge, route.parent_root)[0].page_digest
        location = next(
            row for row in page_locations(route.cartridge, route.parent_root)
            if row.page_digest == page_digest
        )
        path = route.cartridge / "segments" / location.segment_id[7:]
        offset = location.offset
    elif injection == "corrupt_index":
        path = route.cartridge / "indexes" / route.parent_root[7:]
        offset = 0
    else:
        path = route.cartridge / "roots" / route.parent_root[7:]
        offset = 0
    original = path.read_bytes()
    original_mode = path.stat().st_mode
    path.chmod(original_mode | stat.S_IWUSR)
    changed = bytearray(original)
    changed[offset] ^= 0xFF
    path.write_bytes(changed)

    def restore():
        if not path.exists() or path.read_bytes() != original:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                path.chmod(path.stat().st_mode | stat.S_IWUSR)
            path.write_bytes(original)
        path.chmod(original_mode)

    return restore


def _expected_error(operation: str, injection: str) -> str | None:
    if injection in {
        "cartridge_disconnect", "reconnect_same_identity", "reconnect_wrong_identity",
        "sleep_wake", "bus_reset", "port_migration",
    }:
        return "CARTRIDGE_DISCONNECTED"
    if injection == "readonly_remount":
        return "CARTRIDGE_READ_ONLY" if operation in WRITE_OPERATIONS else None
    if injection in {
        "insufficient_capacity_before_start",
        "insufficient_capacity_during_candidate_write",
    }:
        if operation in {"inference_prefill", "inference_decode"}:
            return "MEMORY_BUDGET_EXCEEDED"
        return "CAPACITY_EXCEEDED"
    if injection == "corrupt_page":
        return None if operation == "repair" else "PAGE_CORRUPT"
    if injection in {"corrupt_index", "corrupt_root"}:
        return None if operation == "repair" else "ROOT_INVALID"
    if injection == "source_revision_change_during_transfer":
        if operation == "acquisition":
            return "SOURCE_REVISION_CHANGED"
        if operation == "compilation":
            return "ROOT_INVALID"
        return None
    if injection == "invalid_gradient_nan_inf":
        return "GRADIENT_INVALID" if operation == "training" else None
    if injection == "cancellation":
        return "OPERATION_CANCELLED"
    if injection == "process_death_at_every_durable_boundary":
        return None
    raise AssertionError(f"unowned S26 injection {injection}")


def _read_only(monkeypatch):
    real = os.statvfs

    def readonly(path):
        values = list(real(path))
        values[8] |= os.ST_RDONLY
        return os.statvfs_result(values)

    monkeypatch.setattr(store_module.os, "statvfs", readonly)


def _lifecycle_coordinate(route: _Route, injection: str, monkeypatch):
    lifecycle = CartridgeLifecycle(CARTRIDGE_UUID)
    if injection == "readonly_remount":
        _read_only(monkeypatch)
    lifecycle.mount(route.cartridge, FILESYSTEM_UUID)
    access = lifecycle.begin(
        f"s26-{route.operation}-{injection}",
        write=False if injection == "readonly_remount" else route.write,
    )
    bound = lifecycle.bind(access, write=route.write)
    armed = route.arm(bound)
    auxiliary = []
    stale_attempted = injection != "readonly_remount"
    if injection == "sleep_wake":
        lifecycle.event("sleep")
    elif injection in {"bus_reset", "port_migration"}:
        lifecycle.event(injection)
    elif injection != "readonly_remount":
        lifecycle.event("disconnect")
    call = route.invoke(bound, injection, armed)
    stale_refused = not stale_attempted or call.error == "CARTRIDGE_DISCONNECTED"
    if injection == "readonly_remount":
        lifecycle.finish(access)
        lifecycle.unmount()
        return call, stale_attempted, stale_refused, tuple(auxiliary), None
    if injection == "sleep_wake":
        lifecycle.event("wake")
    if injection == "reconnect_wrong_identity":
        try:
            lifecycle.mount(route.cartridge, WRONG_FILESYSTEM_UUID)
        except CassetteError as error:
            auxiliary.append(error.code)
        return call, stale_attempted, stale_refused, tuple(auxiliary), None
    replacement = None
    if injection == "reconnect_same_identity":
        replacement = route.cartridge.parent / "copied-replacement"
        shutil.copytree(route.cartridge, replacement)
        try:
            lifecycle.mount(replacement, WRONG_FILESYSTEM_UUID)
        except CassetteError as error:
            auxiliary.append(error.code)
        lifecycle.mount(replacement, WRONG_FILESYSTEM_UUID, replacement=True)
    else:
        lifecycle.mount(route.cartridge, FILESYSTEM_UUID)
    resumed = lifecycle.begin(
        f"s26-{route.operation}-{injection}-resumed", write=route.write
    )
    resumed_bound = lifecycle.bind(resumed, write=route.write)
    resumed_call = route.invoke(resumed_bound, "resumed", route.arm(resumed_bound))
    assert resumed_call.entrypoint_hit
    assert resumed_call.error is None
    assert RECEIPT_FIELDS[route.operation] in resumed_call.receipt
    auxiliary.append(resumed_call.error or "RESUMED")
    exact_child = (
        resumed_call.receipt.get("root_digest")
        if route.operation == "acquisition"
        else None
    )
    lifecycle.finish(resumed)
    lifecycle.unmount()
    if replacement is not None:
        shutil.rmtree(replacement)
    return call, stale_attempted, stale_refused, tuple(auxiliary), exact_child


def _run_coordinate(operation: str, injection: str, tmp_path: Path, monkeypatch) -> _Outcome:
    route = ROUTES[operation](tmp_path / operation, monkeypatch)
    sources = route.source_files
    restore = lambda: None
    try:
        parent = pin_generation(route.cartridge).root_digest
        if injection in LIFECYCLE_INJECTIONS:
            call, attempted, refused, auxiliary, exact_child = _lifecycle_coordinate(
                route, injection, monkeypatch
            )
        else:
            restore = _corrupt(route, injection)
            call = route.invoke(route.cartridge, injection)
            attempted = refused = False
            auxiliary = ()
            exact_child = (
                call.receipt.get("root_digest")
                if operation == "acquisition"
                else None
            )
            if injection == "process_death_at_every_durable_boundary":
                boundary_outcome = _process_death_outcome(
                    operation,
                    injection,
                    _S23Cartridge(
                        route.cartridge.parent,
                        route.cartridge,
                        "s26-process-boundary",
                        parent,
                        load_root(route.cartridge, parent),
                        {},
                    ),
                )
                assert boundary_outcome.observed_error == boundary_outcome.expected_error
                assert boundary_outcome.visible_events == boundary_outcome.committed_events
        restore()
        pin = pin_generation(route.cartridge)
        final = parent if pin is None else pin.root_digest
        allowed = (parent,) if exact_child is None else (parent, exact_child)
        return _Outcome(
            operation,
            injection,
            call,
            _expected_error(operation, injection),
            route.cartridge,
            parent,
            final,
            allowed,
            attempted,
            refused,
            auxiliary,
            sources,
        )
    finally:
        restore()
        route.close()


def _assert_no_partial(outcome: _Outcome) -> None:
    assert outcome.final_root in outcome.allowed_roots
    assert not tuple((Path(path) for path in outcome.source_files if path.exists()))
    assert not tuple(outcome.call.receipt.get("partial_roots", ()))
    assert not tuple(outcome.cartridge.rglob("*.generation-candidate"))
    assert not tuple(outcome.cartridge.rglob("*.pending"))


def _assert_typed(outcome: _Outcome) -> None:
    assert outcome.call.error == outcome.expected_error
    assert outcome.call.entrypoint_hit
    if outcome.injection == "reconnect_wrong_identity":
        assert outcome.auxiliary_errors == ("CARTRIDGE_IDENTITY_MISMATCH",)


def _assert_recovery(outcome: _Outcome) -> None:
    assert outcome.final_root in outcome.allowed_roots
    load_root(outcome.cartridge, outcome.final_root)
    if outcome.injection in {
        "cartridge_disconnect", "reconnect_same_identity", "sleep_wake",
        "bus_reset", "port_migration",
    }:
        assert outcome.auxiliary_errors[-1] == "RESUMED"


def _assert_stale(outcome: _Outcome) -> None:
    assert not outcome.stale_attempted or outcome.stale_refused


def _assert_tokens(outcome: _Outcome) -> None:
    if outcome.operation.startswith("inference_"):
        assert outcome.call.delivered == outcome.call.committed[: len(outcome.call.delivered)]
    else:
        assert outcome.call.delivered == outcome.call.committed == ()


def _assert_no_internal_model(outcome: _Outcome) -> None:
    assert all(not path.exists() for path in outcome.source_files)


ASSERTIONS = {
    "no_partial_callable_revision": _assert_no_partial,
    "exact_typed_error": _assert_typed,
    "parent_or_exact_child_recovery": _assert_recovery,
    "no_stale_handle_use": _assert_stale,
    "no_uncommitted_token": _assert_tokens,
    "no_internal_model_file": _assert_no_internal_model,
}


@pytest.mark.parametrize(("operation", "injection"), GENERATED_ROWS, ids=lambda value: value)
def test_q49_failure_rows_reach_every_concrete_operation_and_six_assertions(
    operation, injection, tmp_path, monkeypatch
):
    """Q49/failure_rows: every generated coordinate reaches one concrete product entrypoint."""

    assert MATRIX.required
    assert MATRIX.operations == EXPECTED_OPERATIONS
    assert MATRIX.injections == EXPECTED_INJECTIONS
    assert MATRIX.assertions == EXPECTED_ASSERTIONS
    assert len(GENERATED_ROWS) == len(set(GENERATED_ROWS)) == 128
    assert set(ROUTES) == set(MATRIX.operations)
    assert set(ASSERTIONS) == set(MATRIX.assertions)
    outcome = _run_coordinate(operation, injection, tmp_path, monkeypatch)
    for assertion in MATRIX.assertions:
        ASSERTIONS[assertion](outcome)
    if outcome.call.error is None:
        assert RECEIPT_FIELDS[operation] in outcome.call.receipt
    if operation == "inference_decode" and injection == "process_death_at_every_durable_boundary":
        rogue = tmp_path / "forbidden-internal-model.safetensors"
        rogue.write_bytes(b"forbidden")
        hostile_call = _Call(
            outcome.call.entrypoint,
            outcome.call.entrypoint_hit,
            outcome.call.error,
            outcome.call.receipt,
            (digest_bytes(b"uncommitted-decode"),),
            outcome.call.committed,
        )
        attacks = {
            "no_partial_callable_revision": {"allowed_roots": ()},
            "exact_typed_error": {"expected_error": "FORGED_ERROR"},
            "parent_or_exact_child_recovery": {"allowed_roots": ()},
            "no_stale_handle_use": {"stale_attempted": True, "stale_refused": False},
            "no_uncommitted_token": {"call": hostile_call},
            "no_internal_model_file": {"source_files": (*outcome.source_files, rogue)},
        }
        try:
            for assertion, mutation in attacks.items():
                hostile = _Outcome(**{**outcome.__dict__, **mutation})
                with pytest.raises(AssertionError):
                    ASSERTIONS[assertion](hostile)
        finally:
            rogue.unlink()
