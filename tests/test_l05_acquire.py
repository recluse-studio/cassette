# test_l05_acquire.py — acquisition-only Q5 transfer proof (Q5/Q51/Q53); depends on broker.py, errors.py, sources.py, store.py, tests/fixture_server.py.
"""Exercise the acquisition-only terminal path against a scratch store and loopback source."""

import asyncio
from pathlib import Path

import pytest

from broker import AcquisitionContext, CanonicalBroker
from errors import CassetteError
from fixture_server import _FIXTURES, _SECRET, source_fixture_server
from sources import SourceAdapter
from store import CapacityCoordinator


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
    """Q5/Q51/Q53 acceptance: acquire verifies every source object, pauses safely, and never becomes callable."""
    artifact_one = ("model-00001.safetensors", b"first model shard" * 4096, '"l05-model-one"')
    artifact_two = ("model-00002.safetensors", b"second model shard" * 4096, '"l05-model-two"')
    tokenizer = ("tokenizer.json", b'{"version":"l05"}', '"l05-tokenizer"')
    config = ("config.json", b'{"hidden_size":2}', '"l05-config"')
    with source_fixture_server(
        artifact_overrides={"tinker": (artifact_one, artifact_two)},
        semantic_overrides={"tinker": (tokenizer, config)},
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
            completed = asyncio.run(broker.run_acquisition(request, _context(cartridge, server.base_url)))
            assert completed["state"] == "SUCCEEDED"
            assert completed["kind"] == "acquire"
            assert completed["result"]["immutable_revision"] == "sha256:" + "3" * 64
            expected_paths = {artifact_one[0], artifact_two[0], tokenizer[0], config[0]}
            verified = completed["result"]["verified_artifacts"]
            assert {item["path"] for item in verified} == expected_paths
            assert completed["result"]["verified_bytes"] == sum(item["size"] for item in verified)
            assert {item["digest"] for item in verified}
            with pytest.raises(CassetteError) as not_callable:
                broker.callable_revision(operation_id, cartridge)
            assert not_callable.value.code == "OPERATION_NOT_FOUND"

            ranges_before_replay = len([item for item in server.requests if item["range"]])
            assert asyncio.run(broker.run_acquisition(request, _context(cartridge, server.base_url))) == completed
            assert len([item for item in server.requests if item["range"]]) == ranges_before_replay
            assert len(list((cartridge / "transfers" / operation_id).glob("*.extent"))) == 2 * len(expected_paths)
        finally:
            broker.close()
