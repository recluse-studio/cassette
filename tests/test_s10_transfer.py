# test_s10_transfer.py — S10 Q51 resumable-transfer fixture; depends on errors.py, sources.py, store.py, tests/fixture_server.py.
"""Disprove unsafe transfer completion through interruption, corruption, and identity drift."""

import asyncio
from collections import Counter
from dataclasses import replace
import hashlib
import os
from pathlib import Path
import random
from urllib.parse import urlparse

from blake3 import blake3
import pytest

from errors import CassetteError
from fixture_server import source_fixture_server
import sources as sources_module
from sources import (
    SourceAdapter,
    TransferExtent,
    source_profile_boundary,
    transfer_artifact,
    transfer_header,
    transfer_state_bytes,
)
from store import CapacityCoordinator, artifact_hash_state, grant_transfer_extent, resumable_artifact_hasher, resume_artifact_hasher

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


def test_q51_q53_chunk_claims_use_the_store_owned_coordinator(tmp_path, monkeypatch):
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
    data_observations = []
    state_observations = []
    data_extent = replace(data_extent, observer=data_observations.append)
    state_extent = replace(state_extent, observer=state_observations.append)
    extents = {artifact_name: (data_extent, state_extent)}
    profile_data_fd = profile_state_fd = header_fd = None

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
            profile_data_fd, profile_data_extent = _extent(
                cartridge, capacity_coordinator, f"{artifact_name}.profile.data", len(payload)
            )
            profile_state_fd, profile_state_extent = _extent(
                cartridge, capacity_coordinator, f"{artifact_name}.profile.state", transfer_state_bytes(len(payload))
            )
            header_fd, header_extent = _extent(
                cartridge, capacity_coordinator, f"{artifact_name}.header", len(payload)
            )
            completed = _run(adapter, revision, artifact, extents, capacity_coordinator)
            assert completed.completed_interval_set == ((0, len(payload)),)
            assert completed.chunk_digests == _chunk_digests(payload)
            assert os.pread(data_fd, len(payload), 0) == payload

            data_writes = [event for event in data_observations if event["kind"] == "write"]
            data_reads = [event for event in data_observations if event["kind"] == "read"]
            assert [event["requested_bytes"] for event in data_writes] == [CHUNK, CHUNK, 17]
            assert [event["returned_bytes"] for event in data_writes] == [CHUNK, CHUNK, 17]
            assert [event["requested_bytes"] for event in data_reads] == [CHUNK, CHUNK, 17]
            assert [event["returned_bytes"] for event in data_reads] == [CHUNK, CHUNK, 17]
            assert all(event["success"] is True and isinstance(event["duration_ns"], int)
                       for event in (*data_writes, *data_reads))

            state_writes = [event for event in state_observations if event["kind"] == "write"]
            record_writes = [event for event in state_writes if event["requested_bytes"] == RECORD_BYTES]
            assert [event["offset"] for event in record_writes] == [
                state_extent.offset + HEADER_BYTES + index * RECORD_BYTES
                for index in range(3)
            ]
            envelope_writes = [event for event in state_writes if event["requested_bytes"] != RECORD_BYTES]
            assert [event["offset"] for event in envelope_writes] == [
                state_extent.offset,
                state_extent.offset + HEADER_BYTES // 2,
                state_extent.offset,
                state_extent.offset + HEADER_BYTES // 2,
            ]
            flush_kinds = {event["kind"] for event in state_observations}
            assert "fsync" in flush_kinds
            if hasattr(sources_module.fcntl, "F_FULLFSYNC"):
                assert "F_FULLFSYNC" in flush_kinds
            assert all(event["success"] is True and isinstance(event["duration_ns"], int)
                       for event in state_observations)

            baseline_claim_ids = {id(claim) for claim in capacity_coordinator.claims()}
            profile_data_observations = []
            profile_state_observations = []
            header_observations = []
            profile_data_extent = replace(profile_data_extent, observer=profile_data_observations.append)
            profile_state_extent = replace(profile_state_extent, observer=profile_state_observations.append)
            header_extent = replace(header_extent, observer=header_observations.append)

            async def exercise_profile_boundary():
                async with source_profile_boundary(revision, (artifact,)) as (profile_adapter, profile_revision):
                    profile_artifact = profile_revision.artifacts[0]
                    first_port = urlparse(profile_artifact.range_uri).port
                    prefix = await profile_adapter.open_range(
                        profile_revision, profile_artifact, 0, 32, profile_artifact.validator
                    )
                    profile_state = await transfer_artifact(
                        profile_adapter,
                        profile_revision,
                        profile_artifact,
                        profile_data_extent,
                        profile_state_extent,
                        capacity_coordinator,
                    )
                    async with source_profile_boundary(revision, (artifact,)) as (
                        reopened_adapter, reopened_revision
                    ):
                        reopened_artifact = reopened_revision.artifacts[0]
                        second_port = urlparse(reopened_artifact.range_uri).port
                        assert await reopened_adapter.open_range(
                            reopened_revision, reopened_artifact, 0, 1, reopened_artifact.validator
                        )
                    return profile_revision, profile_artifact, profile_state, prefix, first_port, second_port

            (profile_revision, profile_artifact, profile_state, profile_prefix,
             first_port, second_port) = asyncio.run(exercise_profile_boundary())
            assert first_port != second_port
            assert profile_revision.identity is None
            assert profile_revision.credential_ref is None
            assert profile_revision.license_acceptance_ref is None
            assert profile_revision.artifact_selector is None
            assert profile_revision.immutable_revision.startswith(revision.immutable_revision.split(":", 1)[0] + ":")
            assert len(profile_revision.immutable_revision) == len(revision.immutable_revision)
            assert profile_artifact.path == artifact.path
            assert profile_artifact.size == artifact.size
            assert profile_artifact.validator == artifact.validator
            assert profile_artifact.digest != artifact.digest
            assert profile_artifact.digest.split(":", 1)[0] == artifact.digest.split(":", 1)[0]
            assert len(profile_artifact.digest) == len(artifact.digest)
            expected_prefix = random.Random(int(artifact.digest.partition(":")[2][:16], 16)).randbytes(32)
            assert profile_prefix == expected_prefix
            profile_payload = os.pread(profile_data_fd, len(payload), profile_data_extent.offset)
            assert profile_payload[:32] == expected_prefix
            assert profile_payload != payload
            assert profile_state.source_revision == profile_revision.immutable_revision
            assert profile_state.object_size == artifact.size
            assert profile_state.validator == artifact.validator
            assert profile_state.completed_interval_set == ((0, len(payload)),)
            assert profile_state.chunk_digests == _chunk_digests(profile_payload)
            assert any(event["kind"] == "write" for event in profile_data_observations)

            async def exercise_header_boundary():
                async with source_profile_boundary(
                    revision, (artifact,), header_lengths={artifact.path: 128}
                ) as (header_adapter, header_revision):
                    return await transfer_header(
                        header_adapter,
                        header_revision,
                        header_revision.artifacts[0],
                        header_extent,
                        capacity_coordinator,
                        expected_header_json_bytes=128,
                    )

            header_result = asyncio.run(exercise_header_boundary())
            assert header_result["header_bytes"] == 136
            assert header_result["payload_verification"] == "NOT_RUN"
            assert len(header_result["inventory"]["tensors"]) == 1
            parser_reads = [event for event in header_observations if event["kind"] == "PARSER_READ"]
            assert [event["requested_bytes"] for event in parser_reads] == [8, 128]
            assert [event["offset"] for event in parser_reads] == [0, 8]
            sync_events = [event for event in header_observations if event["kind"] == "fsync"]
            assert len(sync_events) == 2
            if hasattr(sources_module.fcntl, "F_FULLFSYNC"):
                assert len([event for event in header_observations if event["kind"] == "F_FULLFSYNC"]) == 2

            real_pread = sources_module.os.pread
            short_observations = []
            shortened = [False]

            def short_return(fd, length, offset):
                result = real_pread(fd, length, offset)
                if fd == data_fd and length > 1 and not shortened[0]:
                    shortened[0] = True
                    return result[:1]
                return result

            resumed_extents = {
                artifact_name: (
                    replace(data_extent, observer=short_observations.append),
                    state_extent,
                )
            }
            with monkeypatch.context() as patcher:
                patcher.setattr(sources_module.os, "pread", short_return)
                resumed = _run(adapter, revision, artifact, resumed_extents, capacity_coordinator)
            assert resumed == completed
            assert any(event["requested_bytes"] > event["returned_bytes"]
                       for event in short_observations if event["kind"] == "read")

            transfer_claims = tuple(
                claim for claim in capacity_coordinator.claims()
                if (id(claim) in baseline_claim_ids
                    and ("checkpoint-initial" in claim.transition.boundary_id
                    or ":chunk-" in claim.transition.boundary_id)
                )
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
        for descriptor in (data_fd, state_fd, profile_data_fd, profile_state_fd, header_fd):
            if descriptor is not None:
                os.close(descriptor)
    assert capacity_coordinator.active_claims() == ()


def test_q51_random_interruption_corruption_validator_resume_without_final_reread(tmp_path, monkeypatch):
    """Q51/Q60: resume verifies stored chunks; initial completion needs no redundant final reread."""

    git_payload = b'{"text":"qualified dataset bytes"}\n'
    git_prefix = f'blob {len(git_payload)}\0'.encode()
    git_digest = 'git-sha1:' + hashlib.sha1(git_prefix + git_payload).hexdigest()
    tail_hash = resumable_artifact_hasher(git_digest, 'dataset-tail', object_size=len(git_payload))
    empty_state = artifact_hash_state(tail_hash, git_digest, 0, 'dataset-tail')
    tail_hash = resume_artifact_hasher(empty_state, git_digest, 0, 'dataset-tail', object_size=len(git_payload))
    assert tail_hash.hexdigest() == hashlib.sha1(git_prefix).hexdigest()
    completed_hash = tail_hash.copy()
    completed_hash.update(git_payload)
    assert completed_hash.hexdigest() == git_digest[9:]
    completed_state = artifact_hash_state(completed_hash, git_digest, len(git_payload), 'dataset-tail')
    assert len(completed_state) < 256 and git_payload.decode().strip() not in completed_state
    assert resume_artifact_hasher(completed_state, git_digest, len(git_payload), 'dataset-tail',
                                 object_size=len(git_payload)).hexdigest() == git_digest[9:]

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
            requests_before_completed_check = len(server.requests)
            with monkeypatch.context() as patcher:
                patcher.setattr(sources_module.os, "pread", tracked_pread)
                repeated = _run(adapter, revision, first, extents, capacity_coordinator)
            assert repeated == first_result
            assert data_reads == [(0, CHUNK), (CHUNK, CHUNK), (2 * CHUNK, len(first_payload) - 2 * CHUNK)]
            assert len(server.requests) == requests_before_completed_check

            first_data = extents[first.path][0]
            changed_offset = len(first_payload) - 1
            os.pwrite(first_data.fd, bytes([first_payload[changed_offset] ^ 1]), first_data.offset + changed_offset)
            os.fsync(first_data.fd)
            with pytest.raises(CassetteError) as changed_completed_bytes:
                _run(adapter, revision, first, extents, capacity_coordinator)
            assert changed_completed_bytes.value.code == "IDENTITY_MISMATCH"
            assert "local transfer chunk 2" in changed_completed_bytes.value.detail
            assert len(server.requests) == requests_before_completed_check
            repaired = _run(adapter, revision, first, extents, capacity_coordinator)
            assert repaired.checkpoint_generation > first_result.checkpoint_generation
            assert replace(repaired, checkpoint_generation=first_result.checkpoint_generation) == first_result
            assert os.pread(first_data.fd, len(first_payload), first_data.offset) == first_payload

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
