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
from store import CapacityPhase, release_capacity, reserve_capacity, resume_artifact_hasher

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


def _extent(path: Path, length: int) -> tuple[int, TransferExtent]:
    descriptor = os.open(path, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
    os.ftruncate(descriptor, length)
    return descriptor, TransferExtent(descriptor, 0, length, "s10-multi-shard")


def _run(adapter, revision, artifact, extents, reservation, chunk_digests=None):
    return asyncio.run(transfer_artifact(
        adapter,
        revision,
        artifact,
        extents[artifact.path][0],
        extents[artifact.path][1],
        reservation,
        authoritative_chunk_digests=chunk_digests,
    ))


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
    descriptors = []
    extents = {}
    for name, payload, _ in shards:
        data_fd, data_extent = _extent(cartridge / f"{name}.partial", len(payload))
        state_fd, state_extent = _extent(cartridge / f"{name}.transfer", expected_state_bytes[name])
        descriptors.extend((data_fd, state_fd))
        extents[name] = (data_extent, state_extent)
    transfer_bytes = sum(len(payload) + expected_state_bytes[name] for name, payload, _ in shards)
    safety = 20 * 1024**3
    reserved = []
    released = []
    reservation = reserve_capacity(
        "s10-multi-shard",
        device_bytes=400 * 1024**3,
        allocatable_verified_free=transfer_bytes + safety,
        phases=(CapacityPhase(inflight=transfer_bytes),),
        reserve_extent=lambda length: reserved.append(length) is None,
        release_extent=lambda length: released.append(length) is None,
    )
    assert reserved == [transfer_bytes + safety]

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
                    _run(adapter, revision, first, extents, reservation)
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
                    _run(adapter, revision, first, extents, reservation)
            assert record_readback_fault.value.code == "DURABILITY_UNSUPPORTED"

            first_tail = 2 * CHUNK
            server.corrupt_ranges[("huggingface", first.path, first_tail)] = rng.randrange(len(first_payload) - first_tail)
            with pytest.raises(CassetteError) as corrupt_without_chunk_manifest:
                _run(adapter, revision, first, extents, reservation)
            assert corrupt_without_chunk_manifest.value.code == "IDENTITY_MISMATCH"
            assert "whole source digest" in corrupt_without_chunk_manifest.value.detail
            server.corrupt_ranges.clear()

            interruption_cut = rng.randrange(1, len(first_payload) - first_tail)
            request_start = len(server.requests)
            server.interrupt_ranges[("huggingface", first.path, first_tail)] = interruption_cut
            with pytest.raises(CassetteError) as interrupted:
                _run(adapter, revision, first, extents, reservation)
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
                first_result = _run(adapter, revision, first, extents, reservation)
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
                repeated = _run(adapter, revision, first, extents, reservation)
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
                    _run(adapter, revision, first, extents, reservation)
            assert corrupt_checkpoint_record.value.code == "IDENTITY_MISMATCH"
            assert "chunk records" in corrupt_checkpoint_record.value.detail
            assert data_reads == []

            second_digests = _chunk_digests(second_payload)
            second_data = extents[second.path][0]
            server.corrupt_ranges[("huggingface", second.path, 0)] = rng.randrange(CHUNK)
            with pytest.raises(CassetteError) as corrupt_with_chunk_manifest:
                _run(adapter, revision, second, extents, reservation, second_digests)
            assert corrupt_with_chunk_manifest.value.code == "IDENTITY_MISMATCH"
            assert "source chunk 0" in corrupt_with_chunk_manifest.value.detail
            assert os.pread(second_data.fd, CHUNK, second_data.offset) == bytes(CHUNK)
            server.corrupt_ranges.clear()

            def seed_second_partial():
                server.interrupt_ranges[("huggingface", second.path, 2 * CHUNK)] = rng.randrange(1, len(second_payload) - 2 * CHUNK)
                with pytest.raises(CassetteError) as stopped:
                    _run(adapter, revision, second, extents, reservation, second_digests)
                assert stopped.value.code == "SOURCE_UNAVAILABLE"
                assert os.pread(second_data.fd, 2 * CHUNK, second_data.offset) == second_payload[:2 * CHUNK]

            seed_second_partial()
            changed_offset = rng.randrange(2 * CHUNK)
            os.pwrite(second_data.fd, bytes([second_payload[changed_offset] ^ 1]), second_data.offset + changed_offset)
            os.fsync(second_data.fd)
            requests_before_local_check = len(server.requests)
            with pytest.raises(CassetteError) as corrupt_local:
                _run(adapter, revision, second, extents, reservation, second_digests)
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
                    _run(adapter, changed_revision, changed_artifact, extents, reservation, second_digests)
                assert changed_checkpoint.value.code == "SOURCE_REVISION_CHANGED"
                assert "checkpoint identity" in changed_checkpoint.value.detail

            seed_second_partial()
            changed_manifest = list(second_digests)
            changed_manifest[0] = "blake3:" + "0" * 64
            with pytest.raises(CassetteError) as changed_chunk_manifest:
                _run(adapter, revision, second, extents, reservation, tuple(changed_manifest))
            assert changed_chunk_manifest.value.code == "SOURCE_REVISION_CHANGED"
            assert "checkpoint identity" in changed_chunk_manifest.value.detail

            seed_second_partial()
            server.validator_overrides[("huggingface", second.path)] = '"s10-second-v2"'
            with pytest.raises(CassetteError) as changed_live_validator:
                _run(adapter, revision, second, extents, reservation, second_digests)
            assert changed_live_validator.value.code == "SOURCE_REVISION_CHANGED"
            revised = asyncio.run(adapter.resolve(descriptor))
            revised_second = next(item for item in revised.artifacts if item.path == second.path)
            second_result = _run(adapter, revised, revised_second, extents, reservation, second_digests)
            assert second_result.completed_interval_set == ((0, len(second_payload)),)
            assert second_result.validator == '"s10-second-v2"'
            assert os.pread(second_data.fd, len(second_payload), second_data.offset) == second_payload
            assert server.max_active_ranges == 2

            server.validator_overrides[("huggingface", second.path)] = '"s10-second-v3"'
            third_revision = asyncio.run(adapter.resolve(descriptor))
            third_second = next(item for item in third_revision.artifacts if item.path == second.path)
            with pytest.raises(CassetteError) as completed_identity_change:
                _run(adapter, third_revision, third_second, extents, reservation, second_digests)
            assert completed_identity_change.value.code == "SOURCE_REVISION_CHANGED"

            server.interrupt_ranges[("huggingface", second.path, 2 * CHUNK)] = rng.randrange(1, CHUNK)
            server.range_validator_overrides[("huggingface", second.path, 3 * CHUNK)] = '"s10-second-v4"'
            with pytest.raises(CassetteError) as concurrent_revision_change:
                _run(adapter, third_revision, third_second, extents, reservation, second_digests)
            assert concurrent_revision_change.value.code == "SOURCE_REVISION_CHANGED"
            server.range_validator_overrides.clear()
            requests_before_concurrent_resume = len(server.requests)
            _run(adapter, third_revision, third_second, extents, reservation, second_digests)
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

            assert all(path.parent == cartridge for path in cartridge.iterdir())
            assert not any(SECRET.encode() in path.read_bytes() for path in cartridge.iterdir())

            release_capacity(reservation)
            requests_before_release_check = len(server.requests)
            state_before_release_check = os.pread(
                extents[second.path][1].fd,
                expected_state_bytes[second.path],
                extents[second.path][1].offset,
            )
            with pytest.raises(CassetteError) as released_reservation:
                _run(adapter, revised, revised_second, extents, reservation, second_digests)
            assert released_reservation.value.code == "CAPACITY_EXCEEDED"
            assert len(server.requests) == requests_before_release_check
            assert os.pread(
                extents[second.path][1].fd,
                expected_state_bytes[second.path],
                extents[second.path][1].offset,
            ) == state_before_release_check
    finally:
        release_capacity(reservation)
        for descriptor_fd in descriptors:
            os.close(descriptor_fd)
    assert released == [transfer_bytes + safety]
