# test_l05_acquire.py — acquisition-only Q5 transfer proof (Q5/Q6/Q51/Q53); depends on broker.py, errors.py, sources.py, store.py, schema/validator.py, tests/fixture_server.py.
"""Exercise the acquisition-only terminal path against a scratch store and loopback source."""

import asyncio
import copy
from dataclasses import replace
import json
from pathlib import Path

import pytest

from broker import AcquisitionContext, CanonicalBroker, _MAX_RECORD_BYTES, _partial_record, _source_from, _verify_partials
from errors import CassetteError
from fixture_server import _FIXTURES, _SECRET, source_fixture_server
from schema.validator import validate
from sources import PartialState, SourceAdapter
from store import CapacityCoordinator, canonical_bytes, digest_bytes


def _request(key: str) -> dict:
    fixture = _FIXTURES["tinker"]
    return {
        "protocol_version": "1",
        "operation": "acquire",
        "idempotency_key": key,
        "target": "cartridge:l05:acquire",
        "arguments": {"source": {
            "kind": "tinker",
            "locator": fixture["locator"],
            "revision": fixture["alias"],
            "credential_ref": "keychain:l05/acquire",
            "license_acceptance_ref": "license:l05/acquire",
        }},
    }


def _context(cartridge: Path, endpoint: str) -> AcquisitionContext:
    return AcquisitionContext(
        SourceAdapter("tinker", endpoint, lambda _: _SECRET),
        CapacityCoordinator(cartridge),
        None,
        cartridge,
    )


def test_q5_q51_q53_acquire_stops_at_verified_source_and_reuses_transfer_progress(tmp_path):
    """Q5/Q6/Q51/Q53 acceptance: acquire verifies every source object, pauses safely, and never becomes callable."""
    artifact_one = ("000-model-00001.safetensors", b"a" * (2 * 4194304 + 33), '"l05-model-one"')
    artifact_two = ("model-00002.safetensors", b"second model shard" * 4096, '"l05-model-two"')
    tokenizer = ("tokenizer.json", b'{"version":"l05"}', '"l05-tokenizer"')
    config = ("config.json", b'{"hidden_size":2}', '"l05-config"')
    empty_asset = ("empty.json", b"", '"l05-empty"')
    with source_fixture_server(
        artifact_overrides={"tinker": (artifact_one, artifact_two)},
        semantic_overrides={"tinker": (tokenizer, config, empty_asset)},
    ) as server:
        log = tmp_path / "operations"
        cartridge = tmp_path / "cartridge"
        cartridge.mkdir()
        request = _request("l05-acquire-resume")
        broker = CanonicalBroker(log)
        operation_id = broker.issue(request)["operation_id"]
        try:
            assert asyncio.run(broker.advance_acquisition(request, _context(cartridge, server.base_url)))["state"] == "RUNNING"
            assert asyncio.run(broker.advance_acquisition(request, _context(cartridge, server.base_url)))["state"] == "RUNNING"

            server.interrupt_ranges[("tinker", artifact_one[0], 0)] = 17
            paused = asyncio.run(broker.advance_acquisition(request, _context(cartridge, server.base_url)))
            assert paused["state"] == "PAUSED"
            assert broker.events(operation_id)[-1]["payload"]["error"]["code"] == "SOURCE_UNAVAILABLE"
            server.interrupt_ranges.clear()
            broker.close()

            broker = CanonicalBroker(log)
            assert broker.resume(operation_id)["state"] == "RUNNING"
            broker.request_hold(operation_id, "source-checkpoint")
            async def pause_after_chunk():
                task = asyncio.create_task(broker.run_acquisition(request, _context(cartridge, server.base_url)))
                try:
                    for _ in range(3000):
                        if any(event["payload"].get("hold") == "ACKNOWLEDGED" for event in broker.events(operation_id)):
                            break
                        assert not task.done(), task.result()
                        await asyncio.sleep(.01)
                    else:
                        raise AssertionError("first source checkpoint did not reach its hold")
                    status = broker.status(operation_id)
                    assert validate("operation", status) == []
                    observed = status["result"]["transfer_progress"]
                    assert observed == {"artifact": artifact_one[0], "received_bytes": 4194304,
                                        "verified_bytes": 4194304, "verification": "CHUNK_READBACK", "checkpoint": "DURABLE"}
                    observed["received_bytes"] = 0
                    assert broker.status(operation_id)["result"]["transfer_progress"]["received_bytes"] == 4194304
                    assert not any("received_bytes" in event["payload"] for event in broker.events(operation_id))
                    broker.pause(operation_id)
                    assert (await task)["state"] == "PAUSED"
                finally:
                    if not task.done():
                        task.cancel()
                        await asyncio.gather(task, return_exceptions=True)
            asyncio.run(pause_after_chunk())
            prefix_requests = sum(item["path"].endswith("/" + artifact_one[0]) and item["range"] == "bytes=0-4194303"
                                  for item in server.requests)
            assert prefix_requests == 2
            broker.close()
            broker = CanonicalBroker(log)
            assert "result" not in broker.status(operation_id)
            broker.resume(operation_id)
            broker.release_hold(operation_id, "source-checkpoint")
            completed = asyncio.run(broker.run_acquisition(request, _context(cartridge, server.base_url)))
            assert sum(item["path"].endswith("/" + artifact_one[0]) and item["range"] == "bytes=0-4194303"
                       for item in server.requests) == prefix_requests
            assert completed["state"] == "SUCCEEDED"
            assert validate("operation", completed) == []
            assert completed["kind"] == "acquire"
            assert completed["result"]["immutable_revision"] == "sha256:" + "3" * 64
            expected_paths = {artifact_one[0], artifact_two[0], tokenizer[0], config[0], empty_asset[0]}
            verified = completed["result"]["verified_artifacts"]
            assert {item["path"] for item in verified} == expected_paths
            assert completed["result"]["verified_bytes"] == sum(item["size"] for item in verified)
            assert {item["digest"] for item in verified}
            empty_verified = next(item for item in verified if item["path"] == empty_asset[0])
            assert empty_verified["size"] == 0
            assert empty_verified["digest"] == "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            with pytest.raises(CassetteError) as not_callable:
                broker.callable_revision(operation_id, cartridge)
            assert not_callable.value.code == "OPERATION_NOT_FOUND"

            ranges_before_replay = len([item for item in server.requests if item["range"]])
            assert asyncio.run(broker.run_acquisition(request, _context(cartridge, server.base_url))) == completed
            assert len([item for item in server.requests if item["range"]]) == ranges_before_replay
            assert len(list((cartridge / "transfers" / operation_id).glob("*.extent"))) == 2 * len(expected_paths)
            record = json.loads((log / (operation_id + ".json")).read_bytes())["record"]
            events = record["events"]
            assert [event["sequence"] for event in events] == list(range(len(events)))
            assert sum(event["type"] == "completed" for event in events) == 1
            assert len([event for event in events if "received_bytes" in event["payload"]]) == len(expected_paths)
            assert operation_id not in broker._transfer_progress
            assert len(canonical_bytes(record)) < _MAX_RECORD_BYTES
            revision = _source_from(record["checkpoint"]["source_lock"], operation_id)
            artifact = revision.artifacts[0]
            count = 60000
            large = replace(artifact, size=count * 4194304)
            partial = PartialState(revision.immutable_revision, large.size, large.validator,
                                   ((0, large.size),), ("blake3:" + "1" * 64,) * count,
                                   large.size, "synthetic-size-proof-only")
            compact = _partial_record(large.path, partial)
            assert len(canonical_bytes(compact)) < 1024
            assert compact["chunk_digests"] == {"count": count,
                "digest": digest_bytes(canonical_bytes(list(partial.chunk_digests)))}
            _verify_partials([compact], revision, operation_id, (large,))
            legacy = {**compact, "chunk_digests": list(partial.chunk_digests)}
            assert len(canonical_bytes(legacy)) > _MAX_RECORD_BYTES
            _verify_partials([legacy], revision, operation_id, (large,))
            for certificate in ({"count": count - 1, "digest": compact["chunk_digests"]["digest"]},
                                {"count": True, "digest": compact["chunk_digests"]["digest"]},
                                {"count": count, "digest": "sha256:" + "1" * 64},
                                {**compact["chunk_digests"], "extra": 0}):
                with pytest.raises(CassetteError) as invalid:
                    _verify_partials([{**compact, "chunk_digests": certificate}], revision, operation_id, (large,))
                assert invalid.value.code == "ROOT_INVALID"
            for field, value in (("source_revision", "changed"), ("validator", "changed"),
                                 ("completed_interval_set", [[0, large.size - 1]])):
                changed = copy.deepcopy(compact); changed[field] = value
                with pytest.raises(CassetteError) as invalid:
                    _verify_partials([changed], revision, operation_id, (large,))
                assert invalid.value.code == "ROOT_INVALID"
        finally:
            broker.close()
