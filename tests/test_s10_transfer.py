# test_s10_transfer.py — S10 Q51 resumable-transfer fixture; depends on errors.py, sources.py, store.py, tests/fixture_server.py.
"""Disprove unsafe transfer completion through interruption, corruption, and identity drift."""

import asyncio
from collections import Counter
from dataclasses import replace
import hashlib
import os
from pathlib import Path
import random

from blake3 import blake3
import pytest

from errors import CassetteError
from fixture_server import source_fixture_server
import sources as sources_module
from sources import SourceAdapter, TransferExtent, transfer_artifact, transfer_state_bytes
from store import CapacityCoordinator, grant_transfer_extent, resume_artifact_hasher

CHUNK = 4 * 1024 * 1024
HEADER_BYTES = 2 * 64 * 1024
RECORD_BYTES = 33
SECRET = "s09-fixture-secret-never-serialize"


def _payload(label: bytes, size: int) -> bytes:
    return (label * (size // len(label) + 1))[:size]


def _chunk_digests(payload: bytes) -> tuple[str, ...]:
    return tuple(
        "blake3:" + blake3(payload[offset:offset + CHUNK]).hexdigest()
        for offset in range(0, len(payload), CHUNK)
    )


def _extent(
    cartridge: Path,
    capacity_coordinator: CapacityCoordinator,
    extent_id: str,
    length: int,
) -> tuple[int, TransferExtent]:
    extent = grant_transfer_extent(
        cartridge,
        "s10-multi-shard",
        extent_id,
        length,
        capacity_controller=capacity_coordinator,
    )
    return extent.fd, extent


def _run(adapter, revision, artifact, extents, capacity_coordinator, chunk_digests=None):
    return asyncio.run(transfer_artifact(
        adapter,
        revision,
        artifact,
        extents[artifact.path][0],
        extents[artifact.path][1],
        capacity_coordinator,
        authoritative_chunk_digests=chunk_digests,
    ))


def test_q51_q53_chunk_claims_use_the_store_owned_coordinator(tmp_path):
    """Q51/Q53: each transfer transition uses the cartridge's concrete coordinator."""

    # Q51/Q55: grants retain cartridge ownership at every directory and file boundary.
    outside = tmp_path / "outside"
    outside.mkdir()
    original = outside / "part.extent"
    original.write_bytes(b"original")
    for component in ("extent", "operation", "transfers", "hardlink"):
        owned = tmp_path / component
        owned.mkdir()
        if component == "transfers":
            (owned / "transfers").symlink_to(outside, target_is_directory=True)
        else:
            (owned / "transfers").mkdir()
            if component == "operation":
                (owned / "transfers" / "operation").symlink_to(outside, target_is_directory=True)
            else:
                directory = owned / "transfers" / "operation"
                directory.mkdir()
                if component == "hardlink":
                    os.link(original, directory / "part.extent")
                else:
                    (directory / "part.extent").symlink_to(original)
        with pytest.raises(CassetteError) as redirected:
            grant_transfer_extent(owned, "operation", "part", 8)
        assert redirected.value.code == "CONTAINMENT_REJECTED"
        assert original.read_bytes() == b"original"
        assert sorted(item.name for item in outside.iterdir()) == ["part.extent"]

    resumed_cart = tmp_path / "resumed"
    resumed_cart.mkdir()
    extent = grant_transfer_extent(resumed_cart, "operation", "part", 8)
    os.pwrite(extent.fd, b"retained", 0)
    os.close(extent.fd)
    resumed = grant_transfer_extent(resumed_cart, "operation", "part", 8)
    try:
        assert os.pread(resumed.fd, 8, 0) == b"retained"
    finally:
        os.close(resumed.fd)

    payload = _payload(b"cassette-s10-capacity/", 2 * CHUNK + 17)
    artifact_name = "model.safetensors"
    cartridge = tmp_path / "scratch-cartridge"
    cartridge.mkdir()
    capacity_coordinator = CapacityCoordinator(cartridge)
    data_fd, data_extent = _extent(
        cartridge, capacity_coordinator, f"{artifact_name}.data", len(payload)
    )
    state_fd, state_extent = _extent(
        cartridge,
        capacity_coordinator,
        f"{artifact_name}.state",
        transfer_state_bytes(len(payload)),
    )
    extents = {artifact_name: (data_extent, state_extent)}

    descriptor = {
        "kind": "huggingface",
        "locator": "fixture/huggingface-model",
        "revision": "main",
        "credential_ref": "keychain:s10/capacity",
        "license_acceptance_ref": "license:s10/capacity",
        "expected_identity": "blake3:" + "a" * 64,
    }
    try:
        with source_fixture_server(
            artifact_overrides={"huggingface": ((artifact_name, payload, '"s10-capacity-v1"'),)}
        ) as server:
            adapter = SourceAdapter(
                "huggingface", server.base_url, {descriptor["credential_ref"]: SECRET}.get
            )
            revision = asyncio.run(adapter.resolve(descriptor))
            artifact = revision.artifacts[0]
            completed = _run(adapter, revision, artifact, extents, capacity_coordinator)
            assert completed.completed_interval_set == ((0, len(payload)),)
            assert completed.chunk_digests == _chunk_digests(payload)
            assert os.pread(data_fd, len(payload), 0) == payload

            transfer_claims = tuple(
                claim for claim in capacity_coordinator.claims()
                if ("checkpoint-initial" in claim.transition.boundary_id
                    or ":chunk-" in claim.transition.boundary_id)
            )
            assert [(claim.transition.declared_writes, claim.writes_started) for claim in transfer_claims] == [
                (2, 2),
                (5, 5),
                (5, 5),
                (5, 5),
            ]
            assert all(claim.state == "COMPLETED" for claim in transfer_claims)

            changed_revision = replace(
                revision,
                immutable_revision="git-sha1:" + "2" * 40,
            )
            claims_before_reset = len(capacity_coordinator.claims())
            with pytest.raises(CassetteError) as reset:
                _run(adapter, changed_revision, artifact, extents, capacity_coordinator)
            assert reset.value.code == "SOURCE_REVISION_CHANGED"
            reset_claim = capacity_coordinator.claims()[claims_before_reset]
            assert "checkpoint-reset-" in reset_claim.transition.boundary_id
            assert (reset_claim.transition.declared_writes, reset_claim.writes_started) == (2, 2)
            assert reset_claim.state == "COMPLETED"

            for slot in range(2):
                os.pwrite(state_fd, b"\xff" * 4, state_extent.offset + slot * HEADER_BYTES)
            os.fsync(state_fd)
            claims_before_clear = len(capacity_coordinator.claims())
            with pytest.raises(CassetteError) as clear:
                _run(adapter, revision, artifact, extents, capacity_coordinator)
            assert clear.value.code == "IDENTITY_MISMATCH"
            clear_claim = capacity_coordinator.claims()[claims_before_clear]
            assert ":checkpoint-clear:" in clear_claim.transition.boundary_id
            assert clear_claim.transition.write_bytes == (HEADER_BYTES, 0)
            assert (clear_claim.transition.declared_writes, clear_claim.writes_started) == (2, 2)
            assert clear_claim.state == "COMPLETED"
    finally:
        os.close(data_fd)
        os.close(state_fd)
    assert capacity_coordinator.active_claims() == ()


def test_q51_random_interruption_corruption_validator_resume_without_final_reread(tmp_path, monkeypatch):
    """Q51 acceptance: multi-shard resume rejects every mismatch and needs no post-completion artifact reread."""

    rng = random.Random(51)
    first_payload = _payload(b"cassette-s10-first-shard/", 2 * CHUNK + 317)
    second_payload = _payload(b"cassette-s10-second-shard/", 3 * CHUNK + 911)
    shards = (
        ("model-00001-of-00002.safetensors", first_payload, '"s10-first-v1"'),
        ("model-00002-of-00002.safetensors", second_payload, '"s10-second-v1"'),
    )
    expected_state_bytes = {
        name: HEADER_BYTES + ((len(payload) + CHUNK - 1) // CHUNK) * RECORD_BYTES
        for name, payload, _ in shards
    }
    assert all(transfer_state_bytes(len(payload)) == expected_state_bytes[name] for name, payload, _ in shards)

    cartridge = tmp_path / "scratch-cartridge"
    cartridge.mkdir()
    capacity_coordinator = CapacityCoordinator(cartridge)
    descriptors = []
    extents = {}
    for name, payload, _ in shards:
        data_fd, data_extent = _extent(
            cartridge, capacity_coordinator, f"{name}.data", len(payload)
        )
        state_fd, state_extent = _extent(
            cartridge, capacity_coordinator, f"{name}.state", expected_state_bytes[name]
        )
        descriptors.extend((data_fd, state_fd))
        extents[name] = (data_extent, state_extent)

    descriptor = {
        "kind": "huggingface",
        "locator": "fixture/huggingface-model",
        "revision": "main",
        "credential_ref": "keychain:s10/huggingface",
        "license_acceptance_ref": "license:s10/huggingface",
        "expected_identity": "blake3:" + "a" * 64,
    }
    try:
        with source_fixture_server(artifact_overrides={"huggingface": shards}) as server:
            server.range_delay = 0.01
            adapter = SourceAdapter("huggingface", server.base_url, {descriptor["credential_ref"]: SECRET}.get)
            revision = asyncio.run(adapter.resolve(descriptor))
            artifacts = {artifact.path: artifact for artifact in revision.artifacts}
            first = artifacts[shards[0][0]]
            second = artifacts[shards[1][0]]
            real_pread = os.pread
            first_state = extents[first.path][1]

            def changed_checkpoint_read(fd, length, offset):
                payload = real_pread(fd, length, offset)
                if fd == first_state.fd and RECORD_BYTES < length < 64 * 1024 and payload:
                    return bytes([payload[0] ^ 1]) + payload[1:]
                return payload

            requests_before_header_fault = len(server.requests)
            with monkeypatch.context() as patcher:
                patcher.setattr(sources_module.os, "pread", changed_checkpoint_read)
                with pytest.raises(CassetteError) as header_readback_fault:
                    _run(adapter, revision, first, extents, capacity_coordinator)
            assert header_readback_fault.value.code == "DURABILITY_UNSUPPORTED"
            assert len(server.requests) == requests_before_header_fault

            def changed_record_read(fd, length, offset):
                payload = real_pread(fd, length, offset)
                if fd == first_state.fd and length == RECORD_BYTES and payload:
                    return payload[:1] + bytes([payload[1] ^ 1]) + payload[2:]
                return payload

            with monkeypatch.context() as patcher:
                patcher.setattr(sources_module.os, "pread", changed_record_read)
                with pytest.raises(CassetteError) as record_readback_fault:
                    _run(adapter, revision, first, extents, capacity_coordinator)
            assert record_readback_fault.value.code == "DURABILITY_UNSUPPORTED"

            first_tail = 2 * CHUNK
            server.corrupt_ranges[("huggingface", first.path, first_tail)] = rng.randrange(len(first_payload) - first_tail)
            with pytest.raises(CassetteError) as corrupt_without_chunk_manifest:
                _run(adapter, revision, first, extents, capacity_coordinator)
            assert corrupt_without_chunk_manifest.value.code == "IDENTITY_MISMATCH"
            assert "whole source digest" in corrupt_without_chunk_manifest.value.detail
            server.corrupt_ranges.clear()

            interruption_cut = rng.randrange(1, len(first_payload) - first_tail)
            request_start = len(server.requests)
            server.interrupt_ranges[("huggingface", first.path, first_tail)] = interruption_cut
            with pytest.raises(CassetteError) as interrupted:
                _run(adapter, revision, first, extents, capacity_coordinator)
            assert interrupted.value.code == "SOURCE_UNAVAILABLE"
            assert interrupted.value.retryability == "retryable"
            data_extent = extents[first.path][0]
            assert os.pread(data_extent.fd, 2 * CHUNK, data_extent.offset) == first_payload[:2 * CHUNK]

            data_reads = []
            restored_offsets = []

            def tracked_pread(fd, length, offset):
                if fd == data_extent.fd:
                    data_reads.append((offset - data_extent.offset, length))
                return real_pread(fd, length, offset)

            real_resume = sources_module.resume_artifact_hasher

            def tracked_resume(state, digest, offset, object_id):
                restored_offsets.append(offset)
                return real_resume(state, digest, offset, object_id)

            with monkeypatch.context() as patcher:
                patcher.setattr(sources_module.os, "pread", tracked_pread)
                patcher.setattr(sources_module, "resume_artifact_hasher", tracked_resume)
                first_result = _run(adapter, revision, first, extents, capacity_coordinator)
            assert data_reads == [(0, CHUNK), (CHUNK, CHUNK), (2 * CHUNK, len(first_payload) - 2 * CHUNK)]
            assert restored_offsets == [2 * CHUNK]
            assert first_result.completed_interval_set == ((0, len(first_payload)),)
            assert first_result.chunk_digests == _chunk_digests(first_payload)
            assert first_result.serialized_hash_state.startswith("sha256-state-v1:")
            resumed_hash = resume_artifact_hasher(
                first_result.serialized_hash_state,
                first.digest,
                first_result.contiguous_source_hash_offset,
                first.path,
            )
            assert resumed_hash.hexdigest() == hashlib.sha256(first_payload).hexdigest()
            changed_state = bytearray.fromhex(first_result.serialized_hash_state.removeprefix("sha256-state-v1:"))
            changed_state[64:68] = b"\xff" * 4
            with pytest.raises(CassetteError) as impossible_hash_offset:
                resume_artifact_hasher(
                    "sha256-state-v1:" + changed_state.hex(),
                    first.digest,
                    first_result.contiguous_source_hash_offset,
                    first.path,
                )
            assert "state counters" in impossible_hash_offset.value.detail
            attempt_ranges = [
                request["range"] for request in server.requests[request_start:]
                if request["path"].endswith(first.path)
            ]
            assert Counter(attempt_ranges) == Counter({
                f"bytes=0-{CHUNK - 1}": 1,
                f"bytes={CHUNK}-{2 * CHUNK - 1}": 1,
                f"bytes={first_tail}-{len(first_payload) - 1}": 2,
            })

            data_reads.clear()
            with monkeypatch.context() as patcher:
                patcher.setattr(sources_module.os, "pread", tracked_pread)
                repeated = _run(adapter, revision, first, extents, capacity_coordinator)
            assert repeated == first_result
            assert data_reads == []

            first_record_offset = first_state.offset + HEADER_BYTES
            original_record = os.pread(first_state.fd, RECORD_BYTES, first_record_offset)
            changed_record = original_record[:1] + bytes([original_record[1] ^ 1]) + original_record[2:]
            os.pwrite(first_state.fd, changed_record, first_record_offset)
            os.fsync(first_state.fd)
            data_reads.clear()
            with monkeypatch.context() as patcher:
                patcher.setattr(sources_module.os, "pread", tracked_pread)
                with pytest.raises(CassetteError) as corrupt_checkpoint_record:
                    _run(adapter, revision, first, extents, capacity_coordinator)
            assert corrupt_checkpoint_record.value.code == "IDENTITY_MISMATCH"
            assert "chunk records" in corrupt_checkpoint_record.value.detail
            assert data_reads == []

            second_digests = _chunk_digests(second_payload)
            second_data = extents[second.path][0]
            server.corrupt_ranges[("huggingface", second.path, 0)] = rng.randrange(CHUNK)
            with pytest.raises(CassetteError) as corrupt_with_chunk_manifest:
                _run(adapter, revision, second, extents, capacity_coordinator, second_digests)
            assert corrupt_with_chunk_manifest.value.code == "IDENTITY_MISMATCH"
            assert "source chunk 0" in corrupt_with_chunk_manifest.value.detail
            assert os.pread(second_data.fd, CHUNK, second_data.offset) == bytes(CHUNK)
            server.corrupt_ranges.clear()

            def seed_second_partial():
                server.interrupt_ranges[("huggingface", second.path, 2 * CHUNK)] = rng.randrange(1, len(second_payload) - 2 * CHUNK)
                with pytest.raises(CassetteError) as stopped:
                    _run(adapter, revision, second, extents, capacity_coordinator, second_digests)
                assert stopped.value.code == "SOURCE_UNAVAILABLE"
                assert os.pread(second_data.fd, 2 * CHUNK, second_data.offset) == second_payload[:2 * CHUNK]

            seed_second_partial()
            changed_offset = rng.randrange(2 * CHUNK)
            os.pwrite(second_data.fd, bytes([second_payload[changed_offset] ^ 1]), second_data.offset + changed_offset)
            os.fsync(second_data.fd)
            requests_before_local_check = len(server.requests)
            with pytest.raises(CassetteError) as corrupt_local:
                _run(adapter, revision, second, extents, capacity_coordinator, second_digests)
            assert corrupt_local.value.code == "IDENTITY_MISMATCH"
            assert "local transfer chunk" in corrupt_local.value.detail
            assert len(server.requests) == requests_before_local_check

            identity_mutations = (
                replace(revision, immutable_revision="git-sha1:" + "9" * 40),
                replace(revision, artifacts=tuple(
                    replace(item, size=item.size - 1) if item.path == second.path else item
                    for item in revision.artifacts
                )),
                replace(revision, artifacts=tuple(
                    replace(item, digest="sha256:" + "0" * 64) if item.path == second.path else item
                    for item in revision.artifacts
                )),
                replace(revision, artifacts=tuple(
                    replace(item, validator='"s10-second-forged"') if item.path == second.path else item
                    for item in revision.artifacts
                )),
            )
            for changed_revision in identity_mutations:
                seed_second_partial()
                changed_artifact = next(item for item in changed_revision.artifacts if item.path == second.path)
                with pytest.raises(CassetteError) as changed_checkpoint:
                    _run(adapter, changed_revision, changed_artifact, extents, capacity_coordinator, second_digests)
                assert changed_checkpoint.value.code == "SOURCE_REVISION_CHANGED"
                assert "checkpoint identity" in changed_checkpoint.value.detail

            seed_second_partial()
            changed_manifest = list(second_digests)
            changed_manifest[0] = "blake3:" + "0" * 64
            with pytest.raises(CassetteError) as changed_chunk_manifest:
                _run(adapter, revision, second, extents, capacity_coordinator, tuple(changed_manifest))
            assert changed_chunk_manifest.value.code == "SOURCE_REVISION_CHANGED"
            assert "checkpoint identity" in changed_chunk_manifest.value.detail

            seed_second_partial()
            server.validator_overrides[("huggingface", second.path)] = '"s10-second-v2"'
            with pytest.raises(CassetteError) as changed_live_validator:
                _run(adapter, revision, second, extents, capacity_coordinator, second_digests)
            assert changed_live_validator.value.code == "SOURCE_REVISION_CHANGED"
            revised = asyncio.run(adapter.resolve(descriptor))
            revised_second = next(item for item in revised.artifacts if item.path == second.path)
            second_result = _run(adapter, revised, revised_second, extents, capacity_coordinator, second_digests)
            assert second_result.completed_interval_set == ((0, len(second_payload)),)
            assert second_result.validator == '"s10-second-v2"'
            assert os.pread(second_data.fd, len(second_payload), second_data.offset) == second_payload
            assert server.max_active_ranges == 2

            server.validator_overrides[("huggingface", second.path)] = '"s10-second-v3"'
            third_revision = asyncio.run(adapter.resolve(descriptor))
            third_second = next(item for item in third_revision.artifacts if item.path == second.path)
            with pytest.raises(CassetteError) as completed_identity_change:
                _run(adapter, third_revision, third_second, extents, capacity_coordinator, second_digests)
            assert completed_identity_change.value.code == "SOURCE_REVISION_CHANGED"

            server.interrupt_ranges[("huggingface", second.path, 2 * CHUNK)] = rng.randrange(1, CHUNK)
            server.range_validator_overrides[("huggingface", second.path, 3 * CHUNK)] = '"s10-second-v4"'
            with pytest.raises(CassetteError) as concurrent_revision_change:
                _run(adapter, third_revision, third_second, extents, capacity_coordinator, second_digests)
            assert concurrent_revision_change.value.code == "SOURCE_REVISION_CHANGED"
            server.range_validator_overrides.clear()
            requests_before_concurrent_resume = len(server.requests)
            _run(adapter, third_revision, third_second, extents, capacity_coordinator, second_digests)
            resumed_ranges = [
                request["range"] for request in server.requests[requests_before_concurrent_resume:]
                if request["path"].endswith(second.path)
            ]
            assert Counter(resumed_ranges) == Counter([
                f"bytes=0-{CHUNK - 1}",
                f"bytes={CHUNK}-{2 * CHUNK - 1}",
                f"bytes={2 * CHUNK}-{3 * CHUNK - 1}",
                f"bytes={3 * CHUNK}-{len(second_payload) - 1}",
            ])

            assert (cartridge / "transfers" / "s10-multi-shard").is_dir()
            assert not any(
                SECRET.encode() in path.read_bytes()
                for path in cartridge.rglob("*")
                if path.is_file()
            )

    finally:
        for descriptor_fd in descriptors:
            os.close(descriptor_fd)
    assert capacity_coordinator.active_claims() == ()
