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
    """Q42/Q51/Q53: exact recipe I/O and each transfer transition use the store-owned extents."""

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
    composed_fds = []

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

            # Q51/Q42: serving a retained source verifies complete checkpoints and touched
            # chunks without repairing or clearing either granted source extent.
            retained = {"data": data_extent, "state": state_extent}
            assert sources_module._retained_source_range(
                revision, artifact, retained, CHUNK - 7, 31
            ) == payload[CHUNK - 7:CHUNK + 24]
            # Q9/Q33/Q51/Q52: byte-only source recipes freeze the exact input record,
            # preserve literal serializer bytes and read discontiguous verified ranges.
            prefix = b'{"weight":{"dtype":"BF16","shape":[2],"data_offsets":[0,4]}}   '
            prefix = len(prefix).to_bytes(8, 'little') + prefix
            recipe_record = {
                'source_record_digest': sources_module.digest_bytes(sources_module.canonical_bytes(revision.record())),
                'artifacts': [
                    {'path': 'empty', 'segments': [{'literal_hex': ''}]},
                    {'path': 'literal', 'segments': [{'literal_hex': prefix.hex()}]},
                    {'path': 'packed', 'segments': [
                        {'literal_hex': prefix.hex()},
                        {'path': artifact.path, 'offset': 13, 'length': CHUNK + 5},
                        {'literal_hex': b'\x00end\xff'.hex()},
                        {'path': artifact.path, 'offset': 2 * CHUNK - 7, 'length': 24},
                    ]},
                ],
            }
            manifests = {artifact.path: sources_module.digest_bytes(
                sources_module.canonical_bytes(list(completed.chunk_digests)))}
            recipe = sources_module.SourceByteRecipe(recipe_record, revision, manifests)
            manifests[artifact.path] = 'blake3:' + '0' * 64
            assert dict(recipe.input_manifests)[artifact.path] != manifests[artifact.path]
            manifests = dict(recipe.input_manifests)
            expected = {'empty': b'', 'literal': prefix,
                        'packed': prefix + payload[13:CHUNK + 18] + b'\x00end\xff' + payload[-24:]}
            inputs = {artifact.path: retained}
            before_reads = len(data_observations), len(state_observations)
            io_plan = asyncio.run(recipe.fresh_io_plan())
            assert before_reads == (len(data_observations), len(state_observations))
            async def cancel_plan():
                task = asyncio.create_task(recipe.fresh_io_plan())
                await asyncio.sleep(0)
                assert not task.done()
                task.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await task
            asyncio.run(cancel_plan())
            assert before_reads == (len(data_observations), len(state_observations))
            assert io_plan['recipe_digest'] == sources_module.digest_bytes(recipe.encoded)
            assert io_plan['prepass']['range_concurrency'] == 1 and io_plan['write']['range_concurrency'] == 2
            assert io_plan['prepass']['range_calls'] == 4 and io_plan['write']['range_calls'] == 3
            assert io_plan['input_extent_logical_bytes'] == artifact.size + transfer_state_bytes(artifact.size)
            assert io_plan['output_extent_logical_bytes'] == sum(
                len(value) + transfer_state_bytes(len(value)) for value in expected.values())
            assert asyncio.run(recipe.artifact_digests(inputs)) == tuple(
                {'path': path, 'size': len(value), 'digest': 'sha256:' + hashlib.sha256(value).hexdigest()}
                for path, value in expected.items())
            for events, begin, name in zip((data_observations, state_observations), before_reads,
                    ('source_data_read_bytes', 'source_state_read_bytes'), strict=True):
                assert sum(event['returned_bytes'] for event in events[begin:] if event['kind'] == 'read') == io_plan['prepass'][name]
                assert io_plan['write'][name] == io_plan['prepass'][name]
            assert sum(event['kind'] == 'VERIFIED_PREFIX' for event in data_observations[before_reads[0]:]) == io_plan['prepass']['source_verified_chunks']
            assert sum(event['kind'] == 'read' and event['offset'] == state_extent.offset
                       for event in state_observations[before_reads[1]:]) == io_plan['prepass']['source_ranges']
            assert io_plan['write']['output_data_write_bytes'] == sum(map(len, expected.values()))
            assert io_plan['write']['output_data_readback_bytes'] == sum(map(len, expected.values()))
            assert io_plan['source_working_set'] == {
                'scope': 'DISTINCT_TOUCHED_SOURCE_BYTES; CACHE_AND_PHYSICAL_IO_NOT_PROVED',
                'data_bytes': artifact.size, 'state_bytes': transfer_state_bytes(artifact.size)}
            # Q42: tiny repeated spans still reverify complete chunks. Neither literal
            # bytes nor an empty output may conceal those actual source and state reads.
            amplified = sources_module.SourceByteRecipe({
                'source_record_digest': recipe_record['source_record_digest'],
                'artifacts': [{'path': 'tiny', 'segments': [
                    {'path': artifact.path, 'offset': 0, 'length': 1} for _ in range(64)]}]}, revision, manifests)
            amplified_plan = asyncio.run(amplified.fresh_io_plan())
            assert amplified_plan['prepass']['logical_source_bytes'] == 64
            assert amplified_plan['prepass']['source_ranges'] == 64
            assert amplified_plan['prepass']['source_data_read_bytes'] == 64 * CHUNK
            assert amplified_plan['prepass']['source_state_read_bytes'] == 64 * transfer_state_bytes(artifact.size)
            assert amplified_plan['source_working_set']['data_bytes'] == CHUNK
            assert amplified_plan['source_working_set']['state_bytes'] == transfer_state_bytes(artifact.size)
            assert amplified_plan['source_working_set']['data_bytes'] < amplified_plan['input_extent_logical_bytes']
            literal_plan = asyncio.run(sources_module.SourceByteRecipe({
                'source_record_digest': recipe_record['source_record_digest'],
                'artifacts': [{'path': 'literal', 'segments': [{'literal_hex': prefix.hex()}]}]},
                revision, {}).fresh_io_plan())
            assert literal_plan['source_working_set']['data_bytes'] == 0
            assert literal_plan['source_working_set']['state_bytes'] == 0
            before_amplified = len(data_observations), len(state_observations)
            assert asyncio.run(amplified.artifact_digests(inputs))[0]['digest'] == 'sha256:' + hashlib.sha256(payload[:1] * 64).hexdigest()
            for events, begin, name in zip((data_observations, state_observations), before_amplified,
                    ('source_data_read_bytes', 'source_state_read_bytes'), strict=True):
                assert sum(event['returned_bytes'] for event in events[begin:] if event['kind'] == 'read') == amplified_plan['prepass'][name]
            for name, value in expected.items():
                for offset, length in ((0, min(31, len(value))), (len(value), 0)):
                    assert recipe.read_range(name, offset, length, inputs) == value[offset:offset + length]
            assert recipe.read_range('packed', CHUNK - 9, 61, inputs) == expected['packed'][CHUNK - 9:CHUNK + 52]
            assert not any(event['kind'] == 'write' for events, begin in zip(
                (data_observations, state_observations), before_reads, strict=True) for event in events[begin:])
            recipe_record['artifacts'][2]['segments'][0]['literal_hex'] = '00'
            assert recipe.record()['artifacts'][2]['segments'][0]['literal_hex'] == prefix.hex()
            for change in ('source', 'path', 'literal', 'odd', 'missing', 'end', 'boolean', 'negative', 'order', 'json-integer'):
                bad = recipe.record()
                segment = bad['artifacts'][2]['segments'][1]
                if change == 'source':
                    bad['source_record_digest'] = 'blake3:' + '0' * 64
                elif change == 'path':
                    bad['artifacts'][2]['path'] = '../escape'
                elif change in {'literal', 'odd'}:
                    bad['artifacts'][2]['segments'][0]['literal_hex'] = 'gg' if change == 'literal' else '0'
                elif change == 'missing':
                    segment['path'] = 'unknown-input'
                elif change == 'end':
                    segment['offset'] = artifact.size
                elif change in {'boolean', 'negative'}:
                    segment['length'] = True if change == 'boolean' else -1
                elif change == 'json-integer':
                    segment['offset'] = 2**53
                else:
                    bad['artifacts'].reverse()
                with pytest.raises(CassetteError) as invalid_recipe:
                    sources_module.SourceByteRecipe(bad, revision, manifests)
                assert invalid_recipe.value.code == ('SOURCE_REVISION_CHANGED' if change == 'source' else 'INVALID_REQUEST')
            for proof in (None, {}, {**manifests, 'extra': manifests[artifact.path]},
                          {artifact.path: 'sha256:' + '0' * 64}, {artifact.path: 1}):
                with pytest.raises(CassetteError) as invalid_manifest:
                    sources_module.SourceByteRecipe(recipe.record(), revision, proof)
                assert invalid_manifest.value.code == 'INVALID_REQUEST'
            for name, offset, length, handles in (
                    ('', 0, 0, inputs),
                    ('missing', 0, 1, inputs), ('packed', True, 1, inputs), ('packed', 0, CHUNK + 1, inputs),
                    ('packed', len(expected['packed']), 1, inputs), ('empty', 1, 0, inputs),
                    ('packed', 0, 1, {}), ('packed', 0, 1, {artifact.path: {'data': data_extent}})):
                with pytest.raises(CassetteError) as invalid_range:
                    recipe.read_range(name, offset, length, handles)
                assert invalid_range.value.code == 'INVALID_REQUEST'
            large = replace(artifact, size=2**53 - 1)
            large_source = replace(revision, artifacts=(large,))
            with pytest.raises(CassetteError) as overflow:
                sources_module.SourceByteRecipe({
                    'source_record_digest': sources_module.digest_bytes(sources_module.canonical_bytes(large_source.record())),
                    'artifacts': [{'path': 'overflow', 'segments': [
                        {'path': large.path, 'offset': 0, 'length': large.size} for _ in range(1025)]}],
                }, large_source, manifests)
            assert overflow.value.code == 'INVALID_REQUEST' and 'signed 64-bit' in overflow.value.detail
            original_state = os.pread(state_fd, state_extent.length, 0)
            for corruption in ("envelopes", "record", "payload"):
                descriptor = data_fd if corruption == "payload" else state_fd
                original = payload if corruption == "payload" else original_state
                damaged = bytearray(original)
                if corruption == "envelopes":
                    damaged[:HEADER_BYTES] = bytes(HEADER_BYTES)
                else:
                    damaged[0 if corruption == "payload" else HEADER_BYTES + 1] ^= 1
                os.pwrite(descriptor, damaged, 0)
                before_data = os.pread(data_fd, data_extent.length, 0)
                before_state = os.pread(state_fd, state_extent.length, 0)
                with pytest.raises(CassetteError):
                    sources_module._retained_source_range(revision, artifact, retained, 0, 31)
                with pytest.raises(CassetteError):
                    asyncio.run(recipe.artifact_digests(inputs))
                assert os.pread(data_fd, data_extent.length, 0) == before_data
                assert os.pread(state_fd, state_extent.length, 0) == before_state
                os.pwrite(descriptor, original, 0)

            # Q51: a consistent replacement of data and its checkpoint must not replace
            # the original acquisition proof admitted before this read.
            header, chunks = sources_module._load_state(state_extent, artifact.path, None, 'fixture-proof', read_only=True)
            forged_payload = bytes([payload[0] ^ 1]) + payload[1:]
            forged_chunks = _chunk_digests(forged_payload)
            records = b''.join(b'\x01' + bytes.fromhex(value[7:]) for value in forged_chunks)
            forged_header = {**header, 'chunk_records_digest': 'sha256:' + hashlib.sha256(records).hexdigest()}
            os.pwrite(data_fd, forged_payload, 0)
            os.pwrite(state_fd, records, HEADER_BYTES)
            os.pwrite(state_fd, sources_module._state_envelope(forged_header, artifact.path),
                      header['generation'] % 2 * (HEADER_BYTES // 2))
            forged_state = os.pread(state_fd, state_extent.length, 0)
            for read in (
                    lambda: recipe.read_range('packed', 0, len(prefix) + 1, inputs),
                    lambda: asyncio.run(recipe.artifact_digests(inputs))):
                with pytest.raises(CassetteError) as forged_source:
                    read()
                assert forged_source.value.code == 'IDENTITY_MISMATCH'
                assert 'committed acquisition proof' in forged_source.value.detail
            assert os.pread(data_fd, data_extent.length, 0) == forged_payload
            assert os.pread(state_fd, state_extent.length, 0) == forged_state
            assert chunks == completed.chunk_digests
            requests_before_resume = len(server.requests)
            with pytest.raises(CassetteError) as forged_resume:
                _run(adapter, revision, artifact, extents, capacity_coordinator)
            assert forged_resume.value.code == 'IDENTITY_MISMATCH'
            assert 'stored source hash state' in forged_resume.value.detail
            assert len(server.requests) == requests_before_resume
            reset_header, reset_chunks = sources_module._load_state(
                state_extent, artifact.path, None, 'fixture-proof', read_only=True)
            assert reset_header['completed_count'] == 0 and reset_chunks == ()
            assert os.pread(data_fd, data_extent.length, 0) == forged_payload
            os.pwrite(data_fd, payload, 0)
            os.pwrite(state_fd, original_state, 0)

            # Q44/Q51/Q53/Q60: compose with the same durable writer, then resume its
            # committed prefix without overwriting original source extents.
            planned = next(item for item in asyncio.run(recipe.artifact_digests(inputs)) if item['path'] == 'packed')
            generated_data = grant_transfer_extent(cartridge, 's10-compose', 'data', planned['size'],
                capacity_controller=capacity_coordinator)
            composed_fds.append(generated_data.fd)
            generated_state = grant_transfer_extent(cartridge, 's10-compose', 'state',
                transfer_state_bytes(planned['size']), capacity_controller=capacity_coordinator)
            composed_fds.append(generated_state.fd)
            generated_events, generated_state_events = [], []
            generated_data = replace(generated_data, observer=generated_events.append)
            generated_state = replace(generated_state, observer=generated_state_events.append)
            async def interrupt_composition(partial):
                if partial.contiguous_source_hash_offset == CHUNK:
                    raise asyncio.CancelledError
            def compose(digest=planned['digest'], data=generated_data, state=generated_state, callback=None):
                return asyncio.run(sources_module.compose_artifact(recipe, inputs, 'packed', digest,
                    data, state, capacity_coordinator, checkpoint_committed=callback))
            before_fresh = len(data_observations), len(state_observations)
            with pytest.raises(asyncio.CancelledError):
                compose(callback=interrupt_composition)
            packed_pattern = next(item for item in io_plan['outputs'] if item['path'] == 'packed')
            # The writer fetches both bounded ranges before the first checkpoint hold.
            for events, begin, name in zip((data_observations, state_observations), before_fresh,
                    ('source_data_read_bytes', 'source_state_read_bytes'), strict=True):
                assert sum(event['returned_bytes'] for event in events[begin:] if event['kind'] == 'read') == packed_pattern[name]
            prefix_header, _ = sources_module._load_state(
                generated_state, 'packed', None, 'fixture-compose', read_only=True)
            assert prefix_header['completed_count'] == 1
            os.pwrite(data_fd, bytes([payload[-1] ^ 1]), len(payload) - 1)
            with pytest.raises(CassetteError) as changed_input:
                compose()
            assert changed_input.value.code == 'IDENTITY_MISMATCH'
            assert sources_module._load_state(generated_state, 'packed', None, 'fixture-compose',
                read_only=True)[0]['completed_count'] == 1
            os.pwrite(data_fd, payload[-1:], len(payload) - 1)
            composed = compose()
            assert composed.source_revision == sources_module.digest_bytes(recipe.encoded)
            assert composed.contiguous_source_hash_offset == planned['size']
            assert composed.chunk_digests == _chunk_digests(expected['packed'])
            assert os.pread(generated_data.fd, planned['size'], 0) == expected['packed']
            writes_before = tuple(sum(event['kind'] == 'write' for event in events)
                                  for events in (generated_events, generated_state_events))
            assert compose() == composed
            assert tuple(sum(event['kind'] == 'write' for event in events)
                         for events in (generated_events, generated_state_events)) == writes_before
            assert any(event['kind'] == 'F_FULLFSYNC' for event in generated_events)
            os.pwrite(generated_data.fd, b'X', 0)
            with pytest.raises(CassetteError) as changed_output:
                compose()
            assert changed_output.value.code == 'IDENTITY_MISMATCH'
            assert sources_module._load_state(generated_state, 'packed', None, 'fixture-compose',
                read_only=True)[0]['completed_count'] == 0
            assert compose().contiguous_source_hash_offset == planned['size']
            os.pwrite(generated_state.fd, bytes(generated_state.length), 0)
            with pytest.raises(CassetteError) as wrong_expected_digest:
                compose(digest='sha256:' + '0' * 64)
            assert wrong_expected_digest.value.code == 'IDENTITY_MISMATCH'
            assert 'whole source digest' in wrong_expected_digest.value.detail
            original_inputs = os.pread(data_fd, data_extent.length, 0), os.pread(state_fd, state_extent.length, 0)
            for alias_data, alias_state in (
                    (replace(data_extent, operation_id='s10-compose'), generated_state),
                    (generated_data, replace(state_extent, operation_id='s10-compose'))):
                with pytest.raises(CassetteError) as alias:
                    compose(data=alias_data, state=alias_state)
                assert alias.value.code == 'INVALID_REQUEST' and 'overlaps a retained input' in alias.value.detail
            assert original_inputs == (os.pread(data_fd, data_extent.length, 0),
                                       os.pread(state_fd, state_extent.length, 0))

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
                    and claim.transition.operation_id == data_extent.operation_id
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
        for descriptor in (data_fd, state_fd, profile_data_fd, profile_state_fd, header_fd, *composed_fds):
            if descriptor is not None:
                os.close(descriptor)
    assert capacity_coordinator.active_claims() == ()


def test_q51_random_interruption_corruption_validator_resume_without_final_reread(tmp_path, monkeypatch):
    """Q44/Q51/Q60: recover the last durable prefix; completion verifies every stored chunk."""

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

            # A power loss can persist the next header without its last chunk record.
            # The other header still commits the previous two-chunk prefix.
            saved_checkpoint = os.pread(first_state.fd, expected_state_bytes[first.path], first_state.offset)
            tail_record_offset = first_state.offset + HEADER_BYTES + 2 * RECORD_BYTES
            for lost_record in (bytes(RECORD_BYTES), b"\x01" + bytes(RECORD_BYTES - 1)):
                os.pwrite(first_state.fd, saved_checkpoint, first_state.offset)
                os.pwrite(first_state.fd, lost_record, tail_record_offset)
                os.fsync(first_state.fd)
                requests_before_recovery = len(server.requests)
                recovered = _run(adapter, revision, first, extents, capacity_coordinator)
                assert recovered == first_result
                recovery_ranges = [request["range"] for request in server.requests[requests_before_recovery:]
                                   if request["path"].endswith(first.path)]
                assert recovery_ranges == [f"bytes={first_tail}-{len(first_payload) - 1}"]
                assert os.pread(data_extent.fd, len(first_payload), data_extent.offset) == first_payload
            requests_before_completed_check = len(server.requests)

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
