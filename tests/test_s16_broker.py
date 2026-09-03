# test_s16_broker.py — S16 Q5/Q6/Q52 durable broker fixture; depends on broker.py, errors.py, sources.py, store.py, tests/compiler_fixture.py, tests/fixture_server.py.
"""Attack replay, transition, cancellation, error, event, and source-substitution boundaries."""

import ast
import asyncio
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from broker import AcquisitionContext, CanonicalBroker, PHASES
from compiler_fixture import artifact as compiler_artifact
from errors import CODES, CassetteError
import fixture_server as source_fixture
import sources as source_module
import store as store_module
from fixture_server import source_fixture_server
from sources import SourceAdapter, TransferExtent, transfer_state_bytes
from store import (
    CapacityCoordinator,
    canonical_bytes,
    digest_bytes,
    grant_transfer_extent,
    model_identity,
)

SECRET = "s09-fixture-secret-never-serialize"
EXPECTED_PHASES = (
    "EMPTY", "RESOLVED", "ACQUIRING", "SOURCE_VERIFIED",
    "PLANNED", "PREPARING", "EXEC_VERIFIED", "PUBLISHED", "ACTIVE",
)


def _request(kind: str, identity: str, key: str) -> dict:
    fixture = source_fixture._FIXTURES[kind]
    return {
        "protocol_version": "1",
        "operation": "prepare",
        "idempotency_key": key,
        "target": f"cartridge:s16:{kind}",
        "arguments": {
            "source": {
                "kind": kind,
                "locator": fixture["locator"],
                "revision": fixture["alias"],
                "credential_ref": f"keychain:s16/{kind}",
                "license_acceptance_ref": f"license:s16/{kind}",
                "expected_identity": identity,
            }
        },
    }


def _extent(
    cartridge: Path,
    extent_id: str,
    length: int,
    operation_id: str,
    coordinator: CapacityCoordinator,
) -> tuple[int, TransferExtent]:
    """Obtain one store-owned transfer extent for the current cartridge path."""

    extent = grant_transfer_extent(
        cartridge,
        operation_id,
        extent_id,
        length,
        capacity_controller=coordinator,
    )
    return extent.fd, extent


def test_q5_q53_broker_log_claims_directory_and_record_subwrites(tmp_path):
    """Q5/Q53: broker-log creation and record publication use completed exact claims."""

    log = tmp_path / "logs" / "nested" / "broker-log"
    broker = CanonicalBroker(log)
    try:
        directory_claims = broker._capacity_coordinator.claims()
        assert tuple(claim.transition.boundary_id for claim in directory_claims) == (
            "operation-log-directory:logs",
            "operation-log-directory:nested",
            "operation-log-directory:broker-log",
        )
        for directory_claim in directory_claims:
            assert directory_claim.transition.operation_id == "broker-operation-log"
            assert directory_claim.transition.write_bytes == (0,)
            assert directory_claim.history == (
                "MEASURE", "PLAN_NEXT", "CLAIM_NEXT", "MEASURE", "MEASURE", "EXECUTE",
                "DURABLE_BOUNDARY", "OBSERVE",
            )
            assert not directory_claim.active

        request = _request("huggingface", digest_bytes(b"s16-broker-log"), "s16-broker-log")
        issued = broker.issue(request)
        record_path = log / f"{issued['operation_id']}.json"
        record_bytes = record_path.read_bytes()
        record_claim = broker._capacity_coordinator.claims()[-1]

        assert record_claim.transition.operation_id == issued["operation_id"]
        assert record_claim.transition.boundary_id == f"operation-log:{issued['operation_id']}"
        assert record_claim.transition.journal_bytes == len(record_bytes)
        assert record_claim.transition.write_bytes == (len(record_bytes), 0)
        assert record_claim.history == (
            "MEASURE", "PLAN_NEXT", "CLAIM_NEXT", "MEASURE", "MEASURE", "EXECUTE", "MEASURE",
            "EXECUTE", "DURABLE_BOUNDARY", "OBSERVE",
        )
        assert not record_claim.active
    finally:
        broker.close()


def _terminal_events(events: tuple[dict, ...]) -> list[dict]:
    return [event for event in events if event["type"] in {"completed", "cancelled", "failed"}]


def test_q5_q6_q52_durable_idempotent_broker_is_source_blind_and_terminal_exact(tmp_path, monkeypatch):
    """Q5/Q6/Q52 acceptance: every phase replays, every failure terminates once, and adapters share one path."""

    assert PHASES == EXPECTED_PHASES
    names = {kind: f"{kind}-model.safetensors" for kind in source_fixture._FIXTURES}
    built = {
        kind: compiler_artifact(
            kind,
            fixture["locator"],
            fixture["revision"],
            fixture["license"],
            names[kind],
        )
        for kind, fixture in source_fixture._FIXTURES.items()
    }
    payloads = {kind: item[0] for kind, item in built.items()}
    materials = {kind: item[1] for kind, item in built.items()}
    identities = {kind: model_identity(material) for kind, material in materials.items()}
    for kind, identity in identities.items():
        monkeypatch.setitem(source_fixture._FIXTURES[kind], "identity", identity)
    overrides = {
        kind: ((names[kind], payloads[kind], f'"s16-{kind}-v1"'),)
        for kind in payloads
    }
    phase_traces = {}
    request_traces = {}

    with source_fixture_server(artifact_overrides=overrides) as server:
        for kind in payloads:
            log = tmp_path / f"log-{kind}"
            cartridge = tmp_path / f"cartridge-{kind}-a"
            cartridge.mkdir()
            incoming = cartridge / "incoming"
            incoming.mkdir()
            broker = CanonicalBroker(log)
            request = _request(kind, identities[kind], f"s16-{kind}-complete")
            issued = broker.issue(request)
            assert broker.issue(request) == issued
            operation_id = issued["operation_id"]
            coordinator = CapacityCoordinator(cartridge)
            data_fd, data_extent = _extent(
                cartridge, "data", len(payloads[kind]), operation_id, coordinator
            )
            state_bytes = transfer_state_bytes(len(payloads[kind]))
            state_fd, state_extent = _extent(
                cartridge, "state", state_bytes, operation_id, coordinator
            )
            location = {"cartridge": cartridge}

            def context():
                return AcquisitionContext(
                    SourceAdapter(kind, server.base_url, {f"keychain:s16/{kind}": SECRET}.get),
                    CapacityCoordinator(location["cartridge"]),
                    {names[kind]: (data_extent, state_extent)},
                    location["cartridge"],
                )

            snapshots = {}

            def retain(phase):
                destination = tmp_path / f"cancel-{kind}-{phase.lower()}"
                destination.mkdir()
                shutil.copyfile(log / f"{operation_id}.json", destination / f"{operation_id}.json")
                snapshots[phase] = destination

            def clone(phase, purpose):
                destination = tmp_path / f"{purpose}-{kind}-{phase.lower()}"
                destination.mkdir()
                shutil.copyfile(
                    snapshots[phase] / f"{operation_id}.json",
                    destination / f"{operation_id}.json",
                )
                return destination

            retain("EMPTY")
            observed_phases = ["EMPTY"]
            toggle = "b"
            published_root = None
            try:
                while broker.status(operation_id)["state"] not in {"SUCCEEDED", "FAILED", "CANCELLED"}:
                    if observed_phases[-1] == "PUBLISHED":
                        assert broker.callable_revision(
                            operation_id, location["cartridge"]
                        ).root_digest == published_root
                    else:
                        with pytest.raises(CassetteError) as premature:
                            broker.callable_revision(operation_id, location["cartridge"])
                        assert premature.value.code == "OPERATION_NOT_FOUND"
                    operation = asyncio.run(broker.advance_acquisition(request, context()))
                    assert operation["state"] != "FAILED", operation.get("error")
                    events = broker.events(operation_id)
                    latest = events[-1]
                    phase = latest["payload"].get("phase", observed_phases[-1])
                    observed_phases.append(phase)
                    if phase in EXPECTED_PHASES[:-2]:
                        retain(phase)
                    if phase == "PUBLISHED":
                        published_root = broker.callable_revision(
                            operation_id, location["cartridge"]
                        ).root_digest
                    if operation["state"] not in {"SUCCEEDED", "FAILED", "CANCELLED"}:
                        moved = tmp_path / f"cartridge-{kind}-{toggle}"
                        location["cartridge"].rename(moved)
                        location["cartridge"] = moved
                        toggle = "a" if toggle == "b" else "b"
                        broker.close()
                        broker = CanonicalBroker(log)
                        assert broker.issue(request)["operation_id"] == operation_id
                assert operation["state"] == "SUCCEEDED", operation
                assert published_root == operation["result"]["root_digest"]
                assert broker.callable_revision(operation_id, location["cartridge"]).root_digest == operation["result"]["root_digest"]
                replay_requests = len(server.requests)
                assert asyncio.run(broker.run_acquisition(request, context())) == operation
                assert len(server.requests) == replay_requests
                with pytest.raises(CassetteError) as conflict:
                    broker.issue({**request, "target": request["target"] + ":other"})
                assert conflict.value.code == "IDEMPOTENCY_CONFLICT"

                events = broker.events(operation_id)
                assert [event["sequence"] for event in events] == list(range(len(events)))
                assert len(_terminal_events(events)) == 1
                assert _terminal_events(events)[0]["type"] == "completed"
                phase_traces[kind] = [
                    event["payload"]["phase"]
                    for event in events
                    if "phase" in event["payload"]
                ]
                assert phase_traces[kind] == list(EXPECTED_PHASES)

                for phase in EXPECTED_PHASES[:EXPECTED_PHASES.index("PUBLISHED")]:
                    cancelled = CanonicalBroker(clone(phase, "cancelled"))
                    result = cancelled.cancel(operation_id)
                    assert result["state"] == "CANCELLED"
                    assert result["error"]["code"] == "OPERATION_CANCELLED"
                    assert set(result) == {"operation_id", "kind", "state", "progress", "error"}
                    cancel_events = cancelled.events(operation_id)
                    assert [event["sequence"] for event in cancel_events] == list(range(len(cancel_events)))
                    assert len(_terminal_events(cancel_events)) == 1
                    cancelled.close()

                for phase in EXPECTED_PHASES[:EXPECTED_PHASES.index("PUBLISHED")]:
                    paused_log = clone(phase, "paused")
                    paused = CanonicalBroker(paused_log)
                    paused_operation = paused.pause(operation_id)
                    assert paused_operation["state"] == "PAUSED"
                    assert set(paused_operation) == {"operation_id", "kind", "state", "progress"}
                    pause_events = paused.events(operation_id)
                    assert [event["sequence"] for event in pause_events] == list(range(len(pause_events)))
                    assert not _terminal_events(pause_events)
                    assert pause_events[-1]["payload"] == {"phase": phase, "state": "PAUSED"}
                    paused_path = paused.operation_log / f"{operation_id}.json"
                    paused_bytes = paused_path.read_bytes()
                    paused_checkpoint = json.loads(paused_bytes)["record"]["checkpoint"]
                    assert asyncio.run(paused.advance_acquisition(request, context())) == paused_operation
                    assert paused_path.read_bytes() == paused_bytes
                    paused.close()

                    paused = CanonicalBroker(paused_log)
                    assert paused.status(operation_id) == paused_operation
                    assert asyncio.run(paused.advance_acquisition(request, context())) == paused_operation
                    assert paused_path.read_bytes() == paused_bytes
                    resumed = paused.resume(operation_id)
                    resumed_state = "PENDING" if phase == "EMPTY" else "RUNNING"
                    assert resumed["state"] == resumed_state
                    resumed_events = paused.events(operation_id)
                    assert [event["sequence"] for event in resumed_events] == list(range(len(resumed_events)))
                    assert not _terminal_events(resumed_events)
                    assert resumed_events[-1]["payload"] == {"phase": phase, "state": resumed_state}
                    resumed_record = json.loads(paused_path.read_bytes())["record"]
                    assert resumed_record["phase"] == phase
                    assert resumed_record["checkpoint"] == paused_checkpoint
                    paused.close()

                assert tuple(AcquisitionContext.__dataclass_fields__) == (
                    "adapter", "capacity_controller", "transfers", "cartridge",
                )
                with pytest.raises(TypeError):
                    AcquisitionContext(
                        context().adapter,
                        context().capacity_controller,
                        context().transfers,
                        location["cartridge"],
                        lambda: "caller-authored preparation",
                    )

                assert not any(
                    SECRET.encode() in path.read_bytes() for path in log.iterdir() if path.is_file()
                )
            finally:
                broker.close()
                os.close(data_fd)
                os.close(state_fd)
            request_traces[kind] = [
                request_record["path"].split("/")[-1]
                if request_record["path"].startswith(f"/source/{kind}/")
                else "range"
                for request_record in server.requests
                if f"/{kind}/" in request_record["path"]
            ]

    assert len({tuple(trace) for trace in phase_traces.values()}) == 1
    assert all(trace == ["resolve", "artifacts", "metadata", "requirements", "range"] for trace in request_traces.values())


def test_q5_capacity_pause_resumes_from_the_exact_transfer_boundary(tmp_path, monkeypatch):
    """Q5/Q53: a feasible first transition need not fit the whole transfer and resumes exactly."""

    kind = "huggingface"
    fixture = source_fixture._FIXTURES[kind]
    name = f"{kind}-resume.safetensors"
    payload, material, _ = compiler_artifact(
        kind, fixture["locator"], fixture["revision"], fixture["license"], name
    )
    identity = model_identity(material)
    monkeypatch.setitem(source_fixture._FIXTURES[kind], "identity", identity)
    monkeypatch.setattr(source_module, "_TRANSFER_CHUNK_BYTES", max(1, len(payload) // 3))

    with source_fixture_server(
        artifact_overrides={kind: ((name, payload, '"s16-resume-v1"'),)}
    ) as server:
        log = tmp_path / "resume-log"
        cartridge = tmp_path / "resume-cartridge"
        cartridge.mkdir()
        incoming = cartridge / "incoming"
        incoming.mkdir()
        broker = CanonicalBroker(log)
        request = _request(kind, identity, "s16-capacity-resume")
        operation_id = broker.issue(request)["operation_id"]
        coordinator = CapacityCoordinator(cartridge)
        data_fd, data_extent = _extent(cartridge, "data", len(payload), operation_id, coordinator)
        state_bytes = transfer_state_bytes(len(payload))
        state_fd, state_extent = _extent(cartridge, "state", state_bytes, operation_id, coordinator)
        context = AcquisitionContext(
            SourceAdapter(kind, server.base_url, {f"keychain:s16/{kind}": SECRET}.get),
            CapacityCoordinator(cartridge),
            {name: (data_extent, state_extent)},
            cartridge,
        )
        try:
            async def exercise_capacity_pause():
                assert (await broker.advance_acquisition(request, context))["state"] == "RUNNING"
                assert broker.events(operation_id)[-1]["payload"]["phase"] == "RESOLVED"
                assert (await broker.advance_acquisition(request, context))["state"] == "RUNNING"
                assert broker.events(operation_id)[-1]["payload"]["phase"] == "ACQUIRING"
                original_statvfs = store_module.os.statvfs

                def no_free(path):
                    snapshot = original_statvfs(path)
                    values = list(snapshot)
                    if Path(path).resolve().is_relative_to(cartridge.resolve()):
                        values[4] = 0
                    return os.statvfs_result(values)

                monkeypatch.setattr(store_module.os, "statvfs", no_free)
                paused_operation = await broker.advance_acquisition(request, context)
                monkeypatch.setattr(store_module.os, "statvfs", original_statvfs)
                assert paused_operation["state"] == "PAUSED"
                assert broker.resume(operation_id)["state"] == "RUNNING"
                completed_operation = await broker.run_acquisition(request, context)
                return paused_operation, completed_operation

            paused, completed = asyncio.run(exercise_capacity_pause())
            assert paused["state"] == "PAUSED"
            assert completed["state"] == "SUCCEEDED"
        finally:
            broker.close()
            os.close(data_fd)
            os.close(state_fd)

    ownership_log = tmp_path / "ownership-log"
    owner = CanonicalBroker(ownership_log)
    ownership_request = {
        "protocol_version": "1",
        "operation": "run",
        "idempotency_key": "s16-canonical-owner",
        "arguments": {},
    }
    owned_operation = owner.issue(ownership_request)
    with pytest.raises(CassetteError) as competing_instance:
        CanonicalBroker(ownership_log)
    assert competing_instance.value.code == "OVERLOADED"
    owner.close()
    with pytest.raises(CassetteError) as closed_owner:
        owner.status(owned_operation["operation_id"])
    assert closed_owner.value.code == "OVERLOADED"

    child_code = (
        "from broker import CanonicalBroker; import sys; "
        "broker = CanonicalBroker(sys.argv[1]); print('owned', flush=True); "
        "sys.stdin.read()"
    )
    child_environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    child = subprocess.Popen(
        [sys.executable, "-c", child_code, str(ownership_log)],
        cwd=Path(__file__).resolve().parent.parent,
        env=child_environment,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert child.stdout is not None
    try:
        assert child.stdout.readline() == "owned\n"
        with pytest.raises(CassetteError) as competing_process:
            CanonicalBroker(ownership_log)
        assert competing_process.value.code == "OVERLOADED"
    finally:
        child.terminate()
        _, child_error = child.communicate(timeout=10)
    assert not child_error
    replacement = CanonicalBroker(ownership_log)
    assert replacement.issue(ownership_request) == owned_operation
    replacement.close()

    generic_log = tmp_path / "generic-log"
    generic = CanonicalBroker(generic_log)
    issued_operations = (
        "capabilities", "source.resolve", "source.acquire", "model.activate", "run",
        "operation.status", "training", "recovery", "revision.remove",
    )
    for name in issued_operations:
        request = {
            "protocol_version": "1",
            "operation": name,
            "idempotency_key": f"s16-double-{name}",
            "arguments": {},
        }
        assert generic.issue(request) == generic.issue(request)

    for code in sorted(CODES):
        request = {
            "protocol_version": "1",
            "operation": f"failure.{code.lower()}",
            "idempotency_key": f"s16-failure-{code.lower()}",
            "arguments": {},
        }

        async def fail(code=code):
            raise CassetteError(code, f"failure:{code}", "Q6: generated typed failure", "terminal", code)

        assert generic.issue(request) == generic.issue(request)
        result = asyncio.run(generic.execute(request, fail))
        assert result["state"] == ("CANCELLED" if code == "OPERATION_CANCELLED" else "FAILED")
        assert result["error"]["code"] == code
        events = generic.events(result["operation_id"])
        assert [event["sequence"] for event in events] == list(range(len(events)))
        assert len(_terminal_events(events)) == 1
        assert generic.issue(request) == result

    async def execute_duplicate_once():
        request = {
            "protocol_version": "1",
            "operation": "run",
            "idempotency_key": "s16-concurrent-double-issue",
            "arguments": {},
        }
        started = asyncio.Event()
        release = asyncio.Event()
        calls = 0

        async def worker():
            nonlocal calls
            calls += 1
            started.set()
            await release.wait()
            return {"result": "one execution"}

        first = asyncio.create_task(generic.execute(request, worker))
        await started.wait()
        second = asyncio.create_task(generic.execute(request, worker))
        await asyncio.sleep(0)
        release.set()
        results = await asyncio.gather(first, second)
        assert calls == 1
        assert results[0] == results[1]
        assert len(_terminal_events(generic.events(results[0]["operation_id"]))) == 1

    asyncio.run(execute_duplicate_once())

    async def pause_running_worker():
        request = {
            "protocol_version": "1",
            "operation": "run",
            "idempotency_key": "s16-cooperative-pause",
            "arguments": {},
        }
        started = asyncio.Event()
        worker_stopped = asyncio.Event()
        calls = 0

        async def worker():
            nonlocal calls
            calls += 1
            started.set()
            try:
                await asyncio.Event().wait()
            finally:
                worker_stopped.set()

        task = asyncio.create_task(generic.execute(request, worker))
        await started.wait()
        operation_id = CanonicalBroker.operation_id(request)
        assert generic.pause(operation_id)["state"] == "RUNNING"
        paused_operation = await task
        assert paused_operation["state"] == "PAUSED"
        assert worker_stopped.is_set()
        pause_events = generic.events(operation_id)
        assert [event["sequence"] for event in pause_events] == list(range(len(pause_events)))
        assert not _terminal_events(pause_events)
        assert pause_events[-1]["payload"] == {"phase": "EMPTY", "state": "PAUSED"}

        async def forbidden_worker():
            nonlocal calls
            calls += 1
            return {"forbidden": "paused work executed"}

        assert await generic.execute(request, forbidden_worker) == paused_operation
        assert calls == 1
        return request, paused_operation

    paused_request, paused_operation = asyncio.run(pause_running_worker())
    generic.close()
    generic = CanonicalBroker(generic_log)
    assert generic.status(paused_operation["operation_id"]) == paused_operation
    assert generic.resume(paused_operation["operation_id"])["state"] == "PENDING"
    resumed_operation = asyncio.run(generic.execute(
        paused_request, lambda: {"result": "resumed from the durable EMPTY checkpoint"}
    ))
    assert resumed_operation["state"] == "SUCCEEDED"
    assert resumed_operation["result"] == {"result": "resumed from the durable EMPTY checkpoint"}
    assert len(_terminal_events(generic.events(resumed_operation["operation_id"]))) == 1

    async def cancel_running_worker():
        request = {
            "protocol_version": "1",
            "operation": "run",
            "idempotency_key": "s16-cooperative-cancel",
            "arguments": {},
        }
        started = asyncio.Event()
        release = asyncio.Event()

        async def worker():
            started.set()
            await release.wait()
            return {"forbidden": "completion after cancellation"}

        task = asyncio.create_task(generic.execute(request, worker))
        await started.wait()
        operation_id = CanonicalBroker.operation_id(request)
        assert generic.cancel(operation_id)["state"] == "RUNNING"
        result = await task
        assert result["state"] == "CANCELLED"
        assert len(_terminal_events(generic.events(operation_id))) == 1

    asyncio.run(cancel_running_worker())

    for label, field, value in (
        ("phase", "phase", "ACTIVE"),
        ("checkpoint", "checkpoint", {"foreign": "authority"}),
    ):
        grammar_request = {
            "protocol_version": "1",
            "operation": "run",
            "idempotency_key": f"s16-forged-generic-{label}",
            "arguments": {},
        }
        grammar_operation = generic.issue(grammar_request)
        grammar_path = generic.operation_log / f"{grammar_operation['operation_id']}.json"
        grammar_envelope = json.loads(grammar_path.read_bytes())
        grammar_envelope["record"][field] = value
        grammar_envelope["digest"] = digest_bytes(canonical_bytes(grammar_envelope["record"]))
        grammar_path.write_bytes(canonical_bytes(grammar_envelope))
        with pytest.raises(CassetteError) as forged_grammar:
            generic.status(grammar_operation["operation_id"])
        assert forged_grammar.value.code == "ROOT_INVALID"

    valid_request = {
        "protocol_version": "1",
        "operation": "run",
        "idempotency_key": "s16-forged-log",
        "arguments": {},
    }
    operation_id = generic.issue(valid_request)["operation_id"]
    path = generic.operation_log / f"{operation_id}.json"
    envelope = json.loads(path.read_bytes())
    envelope["record"]["events"][0]["sequence"] = 9
    envelope["digest"] = digest_bytes(canonical_bytes(envelope["record"]))
    path.write_bytes(canonical_bytes(envelope))
    with pytest.raises(CassetteError) as forged:
        generic.status(operation_id)
    assert forged.value.code == "ROOT_INVALID"

    terminal_request = {
        "protocol_version": "1",
        "operation": "run",
        "idempotency_key": "s16-forged-terminal",
        "arguments": {},
    }
    terminal = asyncio.run(generic.execute(terminal_request, lambda: {"result": "verified"}))
    terminal_path = generic.operation_log / f"{terminal['operation_id']}.json"
    terminal_envelope = json.loads(terminal_path.read_bytes())
    terminal_envelope["record"]["events"][-1]["type"] = "failed"
    terminal_envelope["digest"] = digest_bytes(canonical_bytes(terminal_envelope["record"]))
    terminal_path.write_bytes(canonical_bytes(terminal_envelope))
    with pytest.raises(CassetteError) as forged_terminal:
        generic.status(terminal["operation_id"])
    assert forged_terminal.value.code == "ROOT_INVALID"

    orphan_request = {
        "protocol_version": "1",
        "operation": "run",
        "idempotency_key": "s16-terminal-without-event",
        "arguments": {},
    }
    orphan = asyncio.run(generic.execute(orphan_request, lambda: {"result": "verified"}))
    orphan_path = generic.operation_log / f"{orphan['operation_id']}.json"
    orphan_envelope = json.loads(orphan_path.read_bytes())
    orphan_envelope["record"]["events"].pop()
    orphan_envelope["digest"] = digest_bytes(canonical_bytes(orphan_envelope["record"]))
    orphan_path.write_bytes(canonical_bytes(orphan_envelope))
    with pytest.raises(CassetteError) as orphan_terminal:
        generic.status(orphan["operation_id"])
    assert orphan_terminal.value.code == "ROOT_INVALID"

    tree = ast.parse((Path(__file__).resolve().parent.parent / "broker.py").read_text(encoding="utf-8"))
    source_kinds = set(source_fixture._FIXTURES)
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.Match)):
            literals = {
                item.value
                for item in ast.walk(node)
                if isinstance(item, ast.Constant) and isinstance(item.value, str)
            }
            assert source_kinds.isdisjoint(literals)
    generic.close()
