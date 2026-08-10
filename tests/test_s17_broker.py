# test_s17_broker.py — S17 Q47/Q65/Q77 scheduler, lease, cache, and negotiation fixture; depends on broker.py, errors.py, pager.py, schema/tables.py, schema/validator.py, store.py.
"""Attack pre-admission identity, fair dispatch, exclusion, switching, and cache reuse."""

import asyncio
from dataclasses import replace
import json
from pathlib import Path

import pytest

from broker import CanonicalBroker, ScheduledLease
from errors import CassetteError
from pager import CertifiedSchedule
from schema.tables import Q77_FIELDS
from schema.validator import validate
from store import (
    PAGE_BYTES,
    ArtifactIdentity,
    IdentityTuple,
    digest_bytes,
    import_safetensors,
    page_locations,
)


def _digest(label: str) -> str:
    return digest_bytes(label.encode())


def _profile(label: str, *, precision: str = "q4", semantic_state: str | None = None) -> dict:
    profile = {
        "cassette_protocol": "1",
        "adapter_version": "custom-v1",
        "model_revision": _digest(f"{label}:revision"),
        "source_parent": _digest(f"{label}:source"),
        "execution_mode": "COMPILED_CERTIFIED",
        "plan_id": _digest(f"{label}:plan"),
        "performance_tier": "FRONTIER_CLASS",
        "training_tier": "B",
        "modalities": ["text", "vision"],
        "input_limits": {"images": 2, "input_bytes": 4096},
        "context_limit": 8192,
        "reasoning_fields": ["effort", "history"],
        "reasoning_history_policy": "preserve",
        "tool_schema": _digest(f"{label}:tools"),
        "structured_output": True,
        "sampling": ["seed", "temperature"],
        "streaming": True,
        "cancellation": True,
        "conversation_state_contract": "immutable-context-v1",
        "precision": precision,
        "semantic_state": _digest(semantic_state or f"{label}:semantic"),
    }
    profile["field_provenance"] = {
        field: {"status": "EXACT", "evidence": _digest(f"{label}:evidence:{field}")}
        for field in (*Q77_FIELDS, "precision", "semantic_state")
    }
    return profile


def _request(negotiation: dict, key: str, context_id: str, operation: str = "run") -> dict:
    return {
        "protocol_version": "1",
        "operation": operation,
        "idempotency_key": key,
        "target": negotiation["model_revision"],
        "arguments": {
            "context_ref": context_id,
            "negotiation_id": negotiation["negotiation_id"],
        },
    }


def _write_safetensors(path: Path, payload: bytes) -> None:
    header = {
        "fixture.weight": {
            "dtype": "U8",
            "shape": [len(payload)],
            "data_offsets": [0, len(payload)],
        }
    }
    encoded = json.dumps(header, separators=(",", ":")).encode()
    encoded += b" " * (-len(encoded) % 8)
    path.write_bytes(len(encoded).to_bytes(8, "little") + encoded + payload)


def _cartridge(tmp_path: Path) -> tuple[Path, str, tuple]:
    source = tmp_path / "s17-model.safetensors"
    payload = b"".join(bytes([index]) * PAGE_BYTES for index in range(1, 7)) + b"tail-page"
    _write_safetensors(source, payload)
    artifact = ArtifactIdentity(source.name, source.stat().st_size, digest_bytes(source.read_bytes()))
    material = IdentityTuple(
        revision_kind="executable",
        source_kind="huggingface",
        source_alias="fixture/s17@main",
        canonical_locator="fixture/s17",
        requested_revision="main",
        immutable_revision="git-sha1:0123456789abcdef0123456789abcdef01234567",
        artifacts=(artifact,),
        format_versions=(("safetensors", "0.6.2"),),
        tensor_index_digest=_digest("s17-index"),
        config_digest=_digest("s17-config"),
        architecture="S17BoundaryTransformer",
        operator_set=("matmul",),
        tokenizer_digest=_digest("s17-tokenizer"),
        processor_digest=_digest("s17-processor"),
        template_digest=_digest("s17-template"),
        precision_scheme="u8-fixture",
        license_digest=_digest("s17-license"),
        parent_ids=(_digest("s17-parent"),),
        transform_manifest_digest=_digest("s17-transform"),
    )
    cartridge = tmp_path / "cartridge"
    root_digest = import_safetensors({source.name: source}, cartridge, material)
    return cartridge, root_digest, page_locations(cartridge, root_digest)


def _schedule(profile: dict, cache_budget_bytes: int) -> CertifiedSchedule:
    return CertifiedSchedule(
        plan_id=profile["plan_id"],
        certificate_id=_digest(f"{profile['plan_id']}:certificate"),
        profile_digest=_digest(f"{profile['plan_id']}:hardware"),
        reserve_bytes=0,
        memory_ceiling_bytes=cache_budget_bytes,
        available_bytes=cache_budget_bytes,
        cache_budget_bytes=cache_budget_bytes,
        peak_live_bytes=cache_budget_bytes,
        steps=(),
    )


async def _idle(broker: CanonicalBroker) -> None:
    for _ in range(200):
        state = broker.scheduler_status()
        if not state["draining"] and not state["queues"] and not state["leases"]:
            return
        await asyncio.sleep(0)
    raise AssertionError("scheduler did not become idle")


async def _reached(event: asyncio.Event) -> None:
    await asyncio.wait_for(event.wait(), 3)


def test_q47_q65_q77_exact_negotiation_fair_leases_switches_and_cache_identity(tmp_path):
    """Q47/Q65/Q77 acceptance: reject before admission, dispatch fairly, and bound cache bytes."""

    async def scenario():
        cartridge, root_digest, locations = _cartridge(tmp_path)
        full_pages = tuple(sorted(
            location.page_digest for location in locations if location.length == PAGE_BYTES
        ))
        tail_pages = tuple(sorted(
            location.page_digest for location in locations if location.length < PAGE_BYTES
        ))
        assert len(full_pages) == 6
        assert [location.length for location in locations if location.page_digest in tail_pages] == [9]
        cache_budget_bytes = 4 * PAGE_BYTES
        log = tmp_path / "operations"
        broker = CanonicalBroker(log)
        activations = []

        def activator(label: str):
            async def activate(lease: ScheduledLease, capability: dict):
                state = broker.scheduler_status()
                assert lease.kind == "SWITCH"
                assert state["leases"] == [{
                    "lease_id": lease.lease_id,
                    "lease_epoch": lease.lease_epoch,
                    "operation_id": lease.operation_id,
                    "kind": "SWITCH",
                    "client_id": lease.client_id,
                    "context_id": lease.context_id,
                    "negotiation_id": lease.negotiation_id,
                    "model_revision": lease.model_revision,
                    "plan_id": lease.plan_id,
                    "cache_key": list(lease.cache_key),
                }]
                assert capability["model_revision"] == lease.model_revision
                activations.append((label, lease.operation_id, lease.cache_key))
                await asyncio.sleep(0)

            return activate

        profile_a = _profile("a")
        profile_b = _profile("b", precision="q3", semantic_state="b:semantic-v2")
        limited = _profile("limited")
        limited.update(
            modalities=["text"],
            reasoning_fields=[],
            tool_schema=None,
            structured_output=False,
            sampling=["seed"],
            streaming=False,
            cancellation=False,
        )
        best_effort = _profile("best-effort")
        best_effort["field_provenance"]["structured_output"]["status"] = "BEST_EFFORT"
        assert validate("callable_capability", profile_a) == []
        malformed_profile = {**profile_a, "field_provenance": dict(profile_a["field_provenance"])}
        del malformed_profile["field_provenance"]["plan_id"]
        assert validate("callable_capability", malformed_profile)
        activate_a = activator("a")
        activate_b = activator("b")
        activate_limited = activator("limited")
        activate_best_effort = activator("best-effort")

        def register(
            model_ref: str,
            profile: dict,
            activate,
            *,
            cache_bytes: int = cache_budget_bytes,
            target: CanonicalBroker = broker,
        ) -> str:
            return target.register_capability(
                model_ref,
                profile,
                activate,
                schedule=_schedule(profile, cache_bytes),
                cartridge=cartridge,
                root_digest=root_digest,
            )

        profile_a_id = register("model/current", profile_a, activate_a)
        assert register("model/a", profile_a, activate_a) == profile_a_id
        profile_b_id = register("model/b", profile_b, activate_b)
        limited_id = register("model/limited", limited, activate_limited)
        best_effort_id = register("model/best-effort", best_effort, activate_best_effort)
        assert register(profile_a["model_revision"], profile_a, activate_a) == profile_a_id
        invalid_profile = {
            **profile_a,
            "field_provenance": {
                field: dict(record) for field, record in profile_a["field_provenance"].items()
            },
        }
        invalid_profile["field_provenance"]["streaming"]["status"] = "FABRICATED"
        with pytest.raises(CassetteError) as caught:
            register("model/invalid-profile", invalid_profile, activate_a)
        assert caught.value.code == "INVALID_REQUEST"
        with pytest.raises(CassetteError) as caught:
            register("model/foreign-activator", profile_a, activate_b)
        assert caught.value.code == "IDEMPOTENCY_CONFLICT"
        with pytest.raises(CassetteError) as caught:
            register(profile_a["model_revision"], profile_b, activate_b)
        assert caught.value.code == "IDENTITY_MISMATCH"
        assert broker.negotiate({"model_ref": profile_a["model_revision"]})[
            "model_revision"
        ] == profile_a["model_revision"]
        discovered = broker.capabilities()
        assert {row["profile_id"] for row in discovered} == {
            profile_a_id, profile_b_id, limited_id, best_effort_id,
        }
        a_discovery = next(row for row in discovered if row["profile_id"] == profile_a_id)
        assert a_discovery["model_refs"] == sorted({
            "model/a", "model/current", profile_a["model_revision"],
        })
        assert a_discovery["capability"] == profile_a

        requested = {"model_ref": "model/current"}
        requested.update({field: profile_a[field] for field in Q77_FIELDS})
        requested.update(
            modalities=["text"],
            input_limits={"images": 1, "input_bytes": 1024},
            context_limit=4096,
            reasoning_fields=["effort"],
            tool_schema=None,
            structured_output=False,
            sampling=["seed"],
            streaming=False,
            cancellation=False,
        )
        negotiated = broker.negotiate(requested)
        assert validate("negotiated_capability", negotiated) == []
        assert set(negotiated) == {*Q77_FIELDS, "field_provenance", "negotiation_id"}
        assert negotiated["model_revision"] == profile_a["model_revision"]
        assert negotiated["modalities"] == ["text"]
        assert negotiated["input_limits"] == {"images": 1, "input_bytes": 1024}
        assert negotiated["context_limit"] == 4096
        assert negotiated["reasoning_fields"] == ["effort"]
        assert negotiated["tool_schema"] is None
        assert not negotiated["structured_output"]
        assert not negotiated["streaming"]
        assert not negotiated["cancellation"]
        assert set(negotiated["field_provenance"]) == set(Q77_FIELDS)

        before_rejections = broker.scheduler_status()
        bad_digest = _digest("unsupported")
        unsupported = {
            "cassette_protocol": "2",
            "adapter_version": "foreign-v1",
            "model_revision": bad_digest,
            "source_parent": bad_digest,
            "execution_mode": "UNCERTIFIED",
            "plan_id": bad_digest,
            "performance_tier": "FICTIONAL",
            "training_tier": "C",
            "modalities": ["audio"],
            "input_limits": {"input_bytes": 4097},
            "context_limit": 8193,
            "reasoning_fields": ["private_chain"],
            "reasoning_history_policy": "discard",
            "tool_schema": bad_digest,
            "sampling": ["top_p"],
            "conversation_state_contract": "mutable-context",
        }
        for field, value in unsupported.items():
            with pytest.raises(CassetteError) as caught:
                broker.negotiate({"model_ref": "model/current", field: value})
            assert caught.value.code == "CAPABILITY_MISMATCH"
            assert broker.scheduler_status() == before_rejections
        for field in ("structured_output", "streaming", "cancellation"):
            with pytest.raises(CassetteError) as caught:
                broker.negotiate({"model_ref": "model/limited", field: True})
            assert caught.value.code == "CAPABILITY_MISMATCH"
        with pytest.raises(CassetteError) as caught:
            broker.negotiate({"model_ref": "model/best-effort", "structured_output": True})
        assert caught.value.code == "CAPABILITY_MISMATCH"
        for field, value in {
            "modalities": ["vision"],
            "reasoning_fields": ["effort"],
            "tool_schema": bad_digest,
            "sampling": ["temperature"],
        }.items():
            with pytest.raises(CassetteError) as caught:
                broker.negotiate({"model_ref": "model/limited", field: value})
            assert caught.value.code == "CAPABILITY_MISMATCH"
        with pytest.raises(CassetteError) as caught:
            broker.negotiate({"model_ref": "model/absent"})
        assert caught.value.code == "CAPABILITY_MISMATCH"
        with pytest.raises(CassetteError) as caught:
            broker.negotiate({"model_ref": "model/current", "foreign": True})
        assert caught.value.code == "INVALID_REQUEST"
        with pytest.raises(CassetteError) as caught:
            broker.negotiate({"model_ref": "model/current", "context_limit": True})
        assert caught.value.code == "INVALID_REQUEST"
        assert not tuple(log.glob("*.json"))

        forged = broker.negotiate({"model_ref": "model/a"})
        forged = {**forged, "model_revision": bad_digest}
        forged_request = _request(forged, "s17-forged-negotiation", "ctx-forged")
        forged_id = broker.operation_id(forged_request)
        with pytest.raises(CassetteError) as caught:
            await broker.dispatch(
                "forger", "ctx-forged", forged_request, forged, "EXEC",
                lambda lease: {"unreachable": lease.lease_id},
            )
        assert caught.value.code == "CAPABILITY_MISMATCH"
        assert not (log / f"{forged_id}.json").exists()
        forged_limit = broker.negotiate({"model_ref": "model/a"})
        forged_limit = {**forged_limit, "context_limit": forged_limit["context_limit"] - 1}
        forged_limit_request = _request(
            forged_limit, "s17-forged-negotiation-limit", "ctx-forged-limit",
        )
        forged_limit_id = broker.operation_id(forged_limit_request)
        with pytest.raises(CassetteError) as caught:
            await broker.dispatch(
                "forger", "ctx-forged-limit", forged_limit_request, forged_limit, "EXEC",
                lambda lease: {"unreachable": lease.lease_id},
            )
        assert caught.value.code == "CAPABILITY_MISMATCH"
        assert not (log / f"{forged_limit_id}.json").exists()

        one_use = broker.negotiate({"model_ref": "model/a"})
        one_use_request = _request(one_use, "s17-one-use", "ctx-one-use")
        one_use_result = await broker.dispatch(
            "one-use", "ctx-one-use", one_use_request, one_use, "EXEC",
            lambda lease: {"lease": lease.lease_id},
        )
        assert one_use_result["state"] == "SUCCEEDED"
        await _idle(broker)
        reused_request = _request(one_use, "s17-one-use-reused", "ctx-one-use-reused")
        reused_id = broker.operation_id(reused_request)
        with pytest.raises(CassetteError) as caught:
            await broker.dispatch(
                "one-use", "ctx-one-use-reused", reused_request, one_use, "EXEC",
                lambda lease: {"unreachable": lease.lease_id},
            )
        assert caught.value.code == "CAPABILITY_MISMATCH"
        assert not (log / f"{reused_id}.json").exists()

        run_order = []
        saved_leases = []
        first_started = asyncio.Event()
        first_release = asyncio.Event()
        a_pages = full_pages[:2]

        async def first_worker(lease: ScheduledLease):
            run_order.append("first")
            saved_leases.append(lease)
            assert lease.kind == "EXEC"
            assert lease.cache_key == (
                profile_a["model_revision"], profile_a["plan_id"], profile_a["precision"],
                profile_a["semantic_state"],
            )
            assert broker.scheduler_status()["cache_bytes"] == 2 * PAGE_BYTES
            assert broker.scheduler_status()["cache_budget_bytes"] == 4 * PAGE_BYTES
            assert all(broker.cache_contains(lease, page) for page in a_pages)
            forged_lease = replace(lease, context_id="ctx-foreign")
            with pytest.raises(CassetteError) as caught:
                broker.cache_contains(forged_lease, a_pages[0])
            assert caught.value.code == "INVALID_REQUEST"
            first_started.set()
            await first_release.wait()
            return {"label": "first"}

        first_request = _request(negotiated, "s17-first", "ctx-first")
        first_task = asyncio.create_task(broker.dispatch(
            "primary", "ctx-first", first_request, negotiated, "EXEC", first_worker,
            pages=a_pages,
        ))
        await _reached(first_started)
        concurrent_reuse_request = _request(
            negotiated, "s17-first-reused-live", "ctx-first-reused-live",
        )
        concurrent_reuse_id = broker.operation_id(concurrent_reuse_request)
        with pytest.raises(CassetteError) as caught:
            await asyncio.wait_for(broker.dispatch(
                "primary", "ctx-first-reused-live", concurrent_reuse_request, negotiated,
                "EXEC", lambda lease: {"unreachable": lease.lease_id},
            ), 3)
        assert caught.value.code == "CAPABILITY_MISMATCH"
        assert not (log / f"{concurrent_reuse_id}.json").exists()

        fair_tasks = []
        fair_requests = []
        for label, client in (("a1", "alpha"), ("a2", "alpha"), ("b1", "beta"), ("b2", "beta")):
            capability = broker.negotiate({"model_ref": "model/a"})
            request = _request(capability, f"s17-fair-{label}", f"ctx-{label}")

            async def fair_worker(lease: ScheduledLease, item=label):
                assert broker.scheduler_status()["leases"][0]["kind"] == "EXEC"
                run_order.append(item)
                return {"label": item, "context": lease.context_id}

            fair_tasks.append(asyncio.create_task(broker.dispatch(
                client, f"ctx-{label}", request, capability, "EXEC", fair_worker,
            )))
            fair_requests.append(request)
            await asyncio.sleep(0)
        first_release.set()
        first_result, *fair_results = await asyncio.gather(first_task, *fair_tasks)
        assert run_order[:5] == ["first", "a1", "b1", "a2", "b2"]
        assert first_result["result"]["context_id"] == "ctx-first"
        for request, result in zip(fair_requests, fair_results, strict=True):
            context = request["arguments"]["context_ref"]
            assert result["result"]["context_id"] == context
            assert result["result"]["value"]["context"] == context
            operation_id = broker.operation_id(request)
            events = broker.events(operation_id)
            assert [event["sequence"] for event in events] == list(range(len(events)))
            assert events[-1]["type"] == "completed"
        await _idle(broker)

        age_order = []
        age_hold = asyncio.Event()
        age_started = asyncio.Event()
        hold_capability = broker.negotiate({"model_ref": "model/a"})
        hold_request = _request(hold_capability, "s17-age-hold", "ctx-age-hold")

        async def age_holder(lease: ScheduledLease):
            age_started.set()
            await age_hold.wait()
            return {"held": lease.lease_id}

        hold_task = asyncio.create_task(broker.dispatch(
            "age-holder", "ctx-age-hold", hold_request, hold_capability, "EXEC", age_holder,
        ))
        await _reached(age_started)
        heavy_capability = broker.negotiate({"model_ref": "model/a"})
        heavy_request = _request(heavy_capability, "s17-age-heavy", "ctx-heavy")

        async def heavy_worker(lease: ScheduledLease):
            age_order.append("heavy")
            return {"lease": lease.lease_id}

        heavy_task = asyncio.create_task(broker.dispatch(
            "heavy", "ctx-heavy", heavy_request, heavy_capability, "EXEC", heavy_worker, cost=16,
        ))
        await asyncio.sleep(0)
        cheap_tasks = []
        for index in range(6):
            label = f"cheap-{index}"
            capability = broker.negotiate({"model_ref": "model/a"})
            request = _request(capability, f"s17-{label}", f"ctx-{label}")

            async def cheap_worker(lease: ScheduledLease, item=label):
                age_order.append(item)
                return {"lease": lease.lease_id}

            cheap_tasks.append(asyncio.create_task(broker.dispatch(
                "cheap", f"ctx-{label}", request, capability, "EXEC", cheap_worker,
            )))
            await asyncio.sleep(0)
        age_hold.set()
        await asyncio.gather(hold_task, heavy_task, *cheap_tasks)
        assert age_order[:5] == ["cheap-0", "cheap-1", "cheap-2", "cheap-3", "heavy"]
        assert broker.scheduler_status()["age_promotions"] == 1
        await _idle(broker)

        alias_started = asyncio.Event()
        alias_release = asyncio.Event()
        alias_lease = []
        active_negotiation = broker.negotiate({"model_ref": "model/current"})
        queued_old = broker.negotiate({"model_ref": "model/current"})
        stale_unadmitted = broker.negotiate({"model_ref": "model/current"})
        active_request = _request(active_negotiation, "s17-alias-active", "ctx-alias-active")

        async def alias_active_worker(lease: ScheduledLease):
            alias_lease.append(lease)
            alias_started.set()
            await alias_release.wait()
            return {"revision": lease.model_revision}

        active_task = asyncio.create_task(broker.dispatch(
            "alias-active", "ctx-alias-active", active_request, active_negotiation, "EXEC",
            alias_active_worker, pages=a_pages,
        ))
        await _reached(alias_started)
        queued_old_request = _request(queued_old, "s17-alias-queued-old", "ctx-alias-old")

        async def queued_old_worker(lease: ScheduledLease):
            assert lease.model_revision == profile_a["model_revision"]
            return {"revision": lease.model_revision}

        queued_old_task = asyncio.create_task(broker.dispatch(
            "alias-old", "ctx-alias-old", queued_old_request, queued_old, "EXEC", queued_old_worker,
        ))
        await asyncio.sleep(0)
        assert register("model/current", profile_b, activate_b) == profile_b_id
        stale_request = _request(stale_unadmitted, "s17-alias-stale", "ctx-alias-stale")
        stale_id = broker.operation_id(stale_request)
        with pytest.raises(CassetteError) as caught:
            await asyncio.wait_for(broker.dispatch(
                "alias-stale", "ctx-alias-stale", stale_request, stale_unadmitted, "EXEC",
                lambda lease: {"unreachable": lease.lease_id},
            ), 3)
        assert caught.value.code == "CAPABILITY_MISMATCH"
        assert not (log / f"{stale_id}.json").exists()

        b_pages = full_pages[2:]
        new_capability = broker.negotiate({"model_ref": "model/current"})
        assert new_capability["model_revision"] == profile_b["model_revision"]
        new_request = _request(new_capability, "s17-alias-new", "ctx-alias-new")

        async def new_worker(lease: ScheduledLease):
            assert lease.cache_key == (
                profile_b["model_revision"], profile_b["plan_id"], profile_b["precision"],
                profile_b["semantic_state"],
            )
            assert all(broker.cache_contains(lease, page) for page in b_pages)
            assert not broker.cache_contains(lease, a_pages[0])
            return {"revision": lease.model_revision}

        churn_before = broker.scheduler_status()["page_churn"]
        new_task = asyncio.create_task(broker.dispatch(
            "alias-new", "ctx-alias-new", new_request, new_capability, "EXEC", new_worker,
            pages=b_pages,
        ))
        await asyncio.sleep(0)
        prefetched = broker.scheduler_status()
        assert prefetched["cache_bytes"] == 4 * PAGE_BYTES
        assert prefetched["cache_budget_bytes"] == 4 * PAGE_BYTES
        assert all(
            any(row["page"] == page and row["pinned"] for row in prefetched["cache"])
            for page in a_pages
        )
        assert sum(row["page"] in b_pages for row in prefetched["cache"]) == 2
        alias_release.set()
        active_result, old_result, new_result = await asyncio.gather(
            active_task, queued_old_task, new_task,
        )
        assert active_result["result"]["negotiated_capability"]["model_revision"] == profile_a["model_revision"]
        assert old_result["result"]["value"]["revision"] == profile_a["model_revision"]
        assert new_result["result"]["value"]["revision"] == profile_b["model_revision"]
        switched = broker.scheduler_status()
        assert switched["active_cache_key"] == [
            profile_b["model_revision"], profile_b["plan_id"], profile_b["precision"],
            profile_b["semantic_state"],
        ]
        assert switched["page_churn"] - churn_before == 2
        assert switched["cache_bytes"] == 4 * PAGE_BYTES
        assert [item[0] for item in activations] == ["a", "b"]
        with pytest.raises(CassetteError) as caught:
            broker.cache_contains(alias_lease[0], a_pages[0])
        assert caught.value.code == "INVALID_REQUEST"
        await _idle(broker)

        register("model/race", profile_a, activate_a)
        race_capability = broker.negotiate({"model_ref": "model/race"})
        race_request = _request(race_capability, "s17-alias-race", "ctx-alias-race")
        race_id = broker.operation_id(race_request)
        await broker._scheduler_lock.acquire()
        try:
            race_task = asyncio.create_task(broker.dispatch(
                "alias-race", "ctx-alias-race", race_request, race_capability, "EXEC",
                lambda lease: {"unreachable": lease.lease_id},
            ))
            await asyncio.sleep(0)
            await asyncio.sleep(0)
            register("model/race", profile_b, activate_b)
        finally:
            broker._scheduler_lock.release()
        with pytest.raises(CassetteError) as caught:
            await race_task
        assert caught.value.code == "CAPABILITY_MISMATCH"
        assert not (log / f"{race_id}.json").exists()

        write_started = asyncio.Event()
        write_release = asyncio.Event()
        exec_started = asyncio.Event()
        write_capability = broker.negotiate({"model_ref": "model/b"})
        write_request = _request(write_capability, "s17-write", "ctx-write", operation="train")

        async def write_worker(lease: ScheduledLease):
            assert lease.kind == "WRITE"
            assert [row["kind"] for row in broker.scheduler_status()["leases"]] == ["WRITE"]
            write_started.set()
            await write_release.wait()
            return {"committed_boundary": _digest("training-step-1"), "step": 1}

        write_task = asyncio.create_task(broker.dispatch(
            "trainer", "ctx-write", write_request, write_capability, "WRITE", write_worker,
        ))
        await _reached(write_started)
        exec_capability = broker.negotiate({"model_ref": "model/b"})
        exec_request = _request(exec_capability, "s17-after-write", "ctx-after-write")

        async def after_write_worker(lease: ScheduledLease):
            assert lease.kind == "EXEC"
            exec_started.set()
            return {"after": "committed-boundary"}

        exec_task = asyncio.create_task(broker.dispatch(
            "inference", "ctx-after-write", exec_request, exec_capability, "EXEC", after_write_worker,
        ))
        await asyncio.sleep(0)
        assert not exec_started.is_set()
        assert [row["kind"] for row in broker.scheduler_status()["leases"]] == ["WRITE"]
        write_release.set()
        write_result, exec_result = await asyncio.gather(write_task, exec_task)
        assert write_result["result"]["value"]["committed_boundary"] == _digest("training-step-1")
        assert exec_result["state"] == "SUCCEEDED"
        assert exec_started.is_set()
        await _idle(broker)

        invalid_write_capability = broker.negotiate({"model_ref": "model/b"})
        invalid_write_request = _request(
            invalid_write_capability, "s17-write-without-boundary", "ctx-write-without-boundary",
            operation="train",
        )
        invalid_write = await broker.dispatch(
            "trainer", "ctx-write-without-boundary", invalid_write_request,
            invalid_write_capability, "WRITE", lambda lease: {"step": lease.lease_epoch},
        )
        assert invalid_write["state"] == "FAILED"
        assert invalid_write["error"]["code"] == "CAPABILITY_MISMATCH"
        assert not broker.scheduler_status()["leases"]
        await _idle(broker)

        cancel_started = asyncio.Event()
        fence_finished = asyncio.Event()
        cancel_lease = []
        cancel_capability = broker.negotiate({"model_ref": "model/b"})
        cancel_request = _request(cancel_capability, "s17-cancel", "ctx-cancel")
        cancel_id = broker.operation_id(cancel_request)

        async def cancellable_worker(lease: ScheduledLease):
            cancel_lease.append(lease)
            cancel_started.set()
            try:
                await asyncio.Event().wait()
            finally:
                assert broker.scheduler_status()["leases"][0]["lease_id"] == lease.lease_id
                fence_finished.set()

        cancel_task = asyncio.create_task(broker.dispatch(
            "cancel-client", "ctx-cancel", cancel_request, cancel_capability, "EXEC",
            cancellable_worker, pages=(b_pages[0],),
        ))
        await _reached(cancel_started)
        assert broker.cancel(cancel_id)["state"] == "RUNNING"
        cancelled = await cancel_task
        assert cancelled["state"] == "CANCELLED"
        assert fence_finished.is_set()
        assert not broker.scheduler_status()["leases"]
        with pytest.raises(CassetteError) as caught:
            broker.cache_contains(cancel_lease[0], b_pages[0])
        assert caught.value.code == "INVALID_REQUEST"
        terminal = [
            event for event in broker.events(cancel_id)
            if event["type"] in {"completed", "cancelled", "failed"}
        ]
        assert [event["type"] for event in terminal] == ["cancelled"]
        await _idle(broker)

        pause_started = asyncio.Event()
        resumed_started = asyncio.Event()
        resumed_release = asyncio.Event()
        pause_leases = []
        pause_capability = broker.negotiate({"model_ref": "model/b"})
        pause_request = _request(pause_capability, "s17-pause-replay", "ctx-pause")
        pause_id = broker.operation_id(pause_request)

        async def pausing_worker(lease: ScheduledLease):
            pause_leases.append(lease)
            pause_started.set()
            await asyncio.Event().wait()

        pause_task = asyncio.create_task(broker.dispatch(
            "pause-client", "ctx-pause", pause_request, pause_capability, "EXEC",
            pausing_worker, pages=(b_pages[0],),
        ))
        await _reached(pause_started)
        assert broker.pause(pause_id)["state"] == "RUNNING"
        paused = await pause_task
        assert paused["state"] == "PAUSED"
        await _idle(broker)
        assert broker.resume(pause_id)["state"] == "PENDING"

        async def resumed_worker(lease: ScheduledLease):
            pause_leases.append(lease)
            resumed_started.set()
            with pytest.raises(CassetteError) as caught:
                broker.cache_contains(pause_leases[0], b_pages[0])
            assert caught.value.code == "INVALID_REQUEST"
            await resumed_release.wait()
            return {"resumed": True}

        resumed_task = asyncio.create_task(broker.dispatch(
            "pause-client", "ctx-pause", pause_request, pause_capability, "EXEC",
            resumed_worker, pages=(b_pages[0],),
        ))
        await _reached(resumed_started)
        assert pause_leases[0].lease_epoch != pause_leases[1].lease_epoch
        assert pause_leases[0].lease_id != pause_leases[1].lease_id
        resumed_release.set()
        resumed = await resumed_task
        assert resumed["state"] == "SUCCEEDED"
        await _idle(broker)

        queue_started = asyncio.Event()
        queue_release = asyncio.Event()
        queue_capability = broker.negotiate({"model_ref": "model/b"})
        queue_request = _request(queue_capability, "s17-queue-hold", "ctx-queue-hold")

        async def queue_holder(lease: ScheduledLease):
            queue_started.set()
            await queue_release.wait()
            return {"lease": lease.lease_id}

        queue_hold_task = asyncio.create_task(broker.dispatch(
            "queue-holder", "ctx-queue-hold", queue_request, queue_capability, "EXEC", queue_holder,
        ))
        await _reached(queue_started)
        queued = []
        for index in range(8):
            capability = broker.negotiate({"model_ref": "model/b"})
            request = _request(capability, f"s17-client-bound-{index}", f"ctx-client-bound-{index}")
            queued.append(asyncio.create_task(broker.dispatch(
                "bounded-client", f"ctx-client-bound-{index}", request, capability, "EXEC",
                lambda lease, item=index: {"item": item, "lease": lease.lease_id},
            )))
            await asyncio.sleep(0)
        overflow_capability = broker.negotiate({"model_ref": "model/b"})
        overflow_request = _request(overflow_capability, "s17-client-overflow", "ctx-client-overflow")
        overflow_id = broker.operation_id(overflow_request)
        with pytest.raises(CassetteError) as caught:
            await asyncio.wait_for(broker.dispatch(
                "bounded-client", "ctx-client-overflow", overflow_request, overflow_capability,
                "EXEC", lambda lease: {"unreachable": lease.lease_id},
            ), 3)
        assert caught.value.code == "OVERLOADED"
        assert not (log / f"{overflow_id}.json").exists()
        queue_release.set()
        await asyncio.gather(queue_hold_task, *queued)
        await _idle(broker)

        global_started = asyncio.Event()
        global_release = asyncio.Event()
        global_capability = broker.negotiate({"model_ref": "model/b"})
        global_request = _request(global_capability, "s17-global-hold", "ctx-global-hold")

        async def global_holder(lease: ScheduledLease):
            global_started.set()
            await global_release.wait()
            return {"lease": lease.lease_id}

        global_hold_task = asyncio.create_task(broker.dispatch(
            "global-holder", "ctx-global-hold", global_request, global_capability, "EXEC",
            global_holder,
        ))
        await _reached(global_started)
        global_tasks = []
        for client in range(8):
            for item in range(8):
                capability = broker.negotiate({"model_ref": "model/b"})
                context = f"ctx-global-{client}-{item}"
                request = _request(capability, f"s17-global-{client}-{item}", context)
                global_tasks.append(asyncio.create_task(broker.dispatch(
                    f"global-{client}", context, request, capability, "EXEC",
                    lambda lease, c=client, i=item: {"client": c, "item": i, "lease": lease.lease_id},
                )))
                await asyncio.sleep(0)
        assert sum(broker.scheduler_status()["queues"].values()) == 64
        global_overflow = broker.negotiate({"model_ref": "model/b"})
        global_overflow_request = _request(
            global_overflow, "s17-global-overflow", "ctx-global-overflow",
        )
        global_overflow_id = broker.operation_id(global_overflow_request)
        with pytest.raises(CassetteError) as caught:
            await asyncio.wait_for(broker.dispatch(
                "global-overflow", "ctx-global-overflow", global_overflow_request,
                global_overflow, "EXEC", lambda lease: {"unreachable": lease.lease_id},
            ), 3)
        assert caught.value.code == "OVERLOADED"
        assert not (log / f"{global_overflow_id}.json").exists()
        global_release.set()
        await asyncio.gather(global_hold_task, *global_tasks)
        await _idle(broker)

        assert broker.scheduler_status()["switches"] == 2
        assert all(item[2][0] == profile_a["model_revision"] for item in activations[:1])
        assert activations[-1][2] == (
            profile_b["model_revision"], profile_b["plan_id"], profile_b["precision"],
            profile_b["semantic_state"],
        )
        broker.close()

        bounded_log = tmp_path / "bounded-negotiations"
        bounded = CanonicalBroker(bounded_log)
        bounded_profile = _profile("bounded")

        def bounded_activate(lease: ScheduledLease, capability: dict):
            raise AssertionError((lease, capability))

        register("model/bounded", bounded_profile, bounded_activate, target=bounded)
        for _ in range(1024):
            bounded.negotiate({"model_ref": "model/bounded"})
        with pytest.raises(CassetteError) as caught:
            bounded.negotiate({"model_ref": "model/bounded"})
        assert caught.value.code == "OVERLOADED"
        assert not tuple(bounded_log.glob("*.json"))
        bounded.close()

        boundary_log = tmp_path / "byte-boundary-operations"
        boundary = CanonicalBroker(boundary_log)

        def boundary_activate(lease: ScheduledLease, capability: dict):
            assert lease.kind == "SWITCH"
            assert capability["plan_id"] == lease.plan_id

        tail_profile = _profile("tail-boundary")
        full_profile = _profile("full-boundary")
        short_profile = _profile("short-boundary")
        wide_profile = _profile("wide-boundary")
        register(
            "model/tail-boundary",
            tail_profile,
            boundary_activate,
            cache_bytes=9,
            target=boundary,
        )
        register(
            "model/full-boundary",
            full_profile,
            boundary_activate,
            cache_bytes=PAGE_BYTES,
            target=boundary,
        )
        register(
            "model/short-boundary",
            short_profile,
            boundary_activate,
            cache_bytes=PAGE_BYTES - 1,
            target=boundary,
        )
        register(
            "model/wide-boundary",
            wide_profile,
            boundary_activate,
            cache_bytes=PAGE_BYTES + 9,
            target=boundary,
        )

        tail_capability = boundary.negotiate({"model_ref": "model/tail-boundary"})
        tail_request = _request(tail_capability, "s17-tail-equality", "ctx-tail-equality")
        tail_result = await boundary.dispatch(
            "boundary",
            "ctx-tail-equality",
            tail_request,
            tail_capability,
            "EXEC",
            lambda lease: {"lease": lease.lease_id},
            pages=tail_pages,
        )
        assert tail_result["state"] == "SUCCEEDED"
        tail_status = boundary.scheduler_status()
        assert tail_status["cache_bytes"] == 9
        assert tail_status["cache_budget_bytes"] == 9
        assert tail_status["cache"][0]["length"] == 9

        count_capability = boundary.negotiate({"model_ref": "model/tail-boundary"})
        count_request = _request(count_capability, "s17-count-is-not-bytes", "ctx-count-is-not-bytes")
        count_id = boundary.operation_id(count_request)
        with pytest.raises(CassetteError) as caught:
            await boundary.dispatch(
                "boundary",
                "ctx-count-is-not-bytes",
                count_request,
                count_capability,
                "EXEC",
                lambda lease: {"unreachable": lease.lease_id},
                pages=(full_pages[0],),
            )
        assert caught.value.code == "MEMORY_BUDGET_EXCEEDED"
        assert not (boundary_log / f"{count_id}.json").exists()

        pinned_started = asyncio.Event()
        pinned_release = asyncio.Event()

        async def pinned_worker(lease: ScheduledLease):
            assert boundary.cache_contains(lease, tail_pages[0])
            pinned_started.set()
            await pinned_release.wait()
            return {"lease": lease.lease_id}

        pinned_capability = boundary.negotiate({"model_ref": "model/tail-boundary"})
        pinned_request = _request(pinned_capability, "s17-pinned-tail", "ctx-pinned-tail")
        pinned_task = asyncio.create_task(boundary.dispatch(
            "boundary",
            "ctx-pinned-tail",
            pinned_request,
            pinned_capability,
            "EXEC",
            pinned_worker,
            pages=tail_pages,
        ))
        await _reached(pinned_started)
        wide_capability = boundary.negotiate({"model_ref": "model/wide-boundary"})
        wide_request = _request(wide_capability, "s17-wide-prefetch", "ctx-wide-prefetch")
        wide_task = asyncio.create_task(boundary.dispatch(
            "boundary",
            "ctx-wide-prefetch",
            wide_request,
            wide_capability,
            "EXEC",
            lambda lease: {"resident": boundary.cache_contains(lease, full_pages[0])},
            pages=(full_pages[0],),
        ))
        await asyncio.sleep(0)
        prefetch_status = boundary.scheduler_status()
        assert prefetch_status["cache_bytes"] == 9
        assert prefetch_status["cache_budget_bytes"] == 9
        assert all(row["page"] != full_pages[0] for row in prefetch_status["cache"])
        pinned_release.set()
        pinned_result, wide_result = await asyncio.gather(pinned_task, wide_task)
        assert pinned_result["state"] == "SUCCEEDED"
        assert wide_result["result"]["value"]["resident"]
        assert boundary.scheduler_status()["cache_bytes"] == PAGE_BYTES + 9
        assert boundary.scheduler_status()["cache_budget_bytes"] == PAGE_BYTES + 9

        full_capability = boundary.negotiate({"model_ref": "model/full-boundary"})
        full_request = _request(full_capability, "s17-full-equality", "ctx-full-equality")
        full_result = await boundary.dispatch(
            "boundary",
            "ctx-full-equality",
            full_request,
            full_capability,
            "EXEC",
            lambda lease: {"lease": lease.lease_id},
            pages=(full_pages[0],),
        )
        assert full_result["state"] == "SUCCEEDED"
        full_status = boundary.scheduler_status()
        assert full_status["cache_bytes"] == PAGE_BYTES
        assert full_status["cache_budget_bytes"] == PAGE_BYTES
        assert [row["length"] for row in full_status["cache"]] == [PAGE_BYTES]

        short_capability = boundary.negotiate({"model_ref": "model/short-boundary"})
        short_request = _request(short_capability, "s17-full-minus-one", "ctx-full-minus-one")
        short_id = boundary.operation_id(short_request)
        with pytest.raises(CassetteError) as caught:
            await boundary.dispatch(
                "boundary",
                "ctx-full-minus-one",
                short_request,
                short_capability,
                "EXEC",
                lambda lease: {"unreachable": lease.lease_id},
                pages=(full_pages[0],),
            )
        assert caught.value.code == "MEMORY_BUDGET_EXCEEDED"
        assert not (boundary_log / f"{short_id}.json").exists()

        unknown_capability = boundary.negotiate({"model_ref": "model/full-boundary"})
        unknown_request = _request(unknown_capability, "s17-unknown-page", "ctx-unknown-page")
        unknown_id = boundary.operation_id(unknown_request)
        with pytest.raises(CassetteError) as caught:
            await boundary.dispatch(
                "boundary",
                "ctx-unknown-page",
                unknown_request,
                unknown_capability,
                "EXEC",
                lambda lease: {"unreachable": lease.lease_id},
                pages=(_digest("not-in-the-root"),),
            )
        assert caught.value.code == "PAGE_CORRUPT"
        assert not (boundary_log / f"{unknown_id}.json").exists()
        boundary.close()

    asyncio.run(scenario())
