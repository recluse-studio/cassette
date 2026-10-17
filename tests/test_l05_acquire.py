# test_l05_acquire.py — acquisition-only Q5 transfer proof (Q5/Q6/Q51/Q53); depends on broker.py, errors.py, sources.py, store.py, schema/validator.py, tests/fixture_server.py, tests/test_l05_drive.py.
"""Exercise the acquisition-only terminal path against a scratch store and loopback source."""

import asyncio
import copy
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import threading
import subprocess

import pytest

from broker import AcquisitionContext, CanonicalBroker, _MAX_RECORD_BYTES, _partial_record, _source_from, _transfer_extent_id, _verify_partials
from errors import CassetteError
from fixture_server import _FIXTURES, _SECRET, source_fixture_server
from test_l05_drive import _attached_apfs_image
from schema.validator import validate
from sources import PartialState, SourceAdapter, transfer_state_bytes
from store import CapacityCoordinator, campaign_head, canonical_bytes, digest_bytes, grant_transfer_extent, list_external_apfs_volumes, select_external_apfs_volume, verify_campaign_artifact, write_campaign_artifact, compare_campaign_head, storage_profile


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


def test_q5_q51_q53_acquire_stops_at_verified_source_and_reuses_transfer_progress(tmp_path, monkeypatch):
    """Q5/Q6/Q42/Q43/Q51/Q53/Q60: acquisition, composition and raw capture preserve their exact evidence boundaries."""
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
            original_record = (log / (operation_id + '.json')).read_bytes()
            recipe = {'source_record_digest': digest_bytes(canonical_bytes(revision.record())), 'artifacts': [
                {'path': 'empty', 'segments': [{'literal_hex': ''}]},
                {'path': 'packed', 'segments': [{'literal_hex': '00ff'},
                    {'path': artifact_one[0], 'offset': 7, 'length': 4194304 + 17}, {'literal_hex': '0a00'}]},
            ]}
            composition = {'protocol_version': '1', 'operation': 'source.compose',
                'idempotency_key': 'l05-compose-resume', 'target': operation_id,
                'arguments': {'composition': {'acquisition_operation_id': operation_id, 'recipe': recipe}}}
            assert validate('request', composition) == []
            composition_id = broker.issue(composition)['operation_id']
            key = 'source-compose-' + composition_id.removeprefix('op-')
            owner = CapacityCoordinator(cartridge)
            native_statvfs = os.statvfs
            with monkeypatch.context() as hardware:
                def no_capacity(path):
                    observed = native_statvfs(path)
                    return os.statvfs_result((*observed[:4], 0, *observed[5:])) if Path(path) == cartridge else observed
                hardware.setattr(os, 'statvfs', no_capacity)
                waiting = asyncio.run(broker.compose_source(composition, owner))
            assert waiting['state'] == 'PAUSED'
            assert broker.events(composition_id)[-1]['payload']['error']['code'] == 'CAPACITY_EXCEEDED'
            assert campaign_head(cartridge, key) is None
            assert not (cartridge / 'transfers' / composition_id).exists()
            broker.resume(composition_id)
            broker.request_hold(composition_id, 'composition-checkpoint')
            async def pause_composition():
                task = asyncio.create_task(broker.compose_source(composition, owner))
                try:
                    for _ in range(3000):
                        if any(event['payload'].get('hold') == 'ACKNOWLEDGED' for event in broker.events(composition_id)):
                            break
                        assert not task.done(), task.result()
                        await asyncio.sleep(.01)
                    else:
                        raise AssertionError('composition did not reach its durable checkpoint')
                    assert campaign_head(cartridge, key) is not None
                    assert campaign_head(cartridge, key + '-complete') is None
                    broker.pause(composition_id)
                    assert (await task)['state'] == 'PAUSED'
                finally:
                    if not task.done():
                        task.cancel()
                        await asyncio.gather(task, return_exceptions=True)
            asyncio.run(pause_composition())
            broker.close()
            broker = CanonicalBroker(log)
            broker.resume(composition_id)
            broker.release_hold(composition_id, 'composition-checkpoint')
            composed = asyncio.run(broker.compose_source(composition, CapacityCoordinator(cartridge)))
            assert composed['state'] == 'SUCCEEDED' and validate('operation', composed) == []
            head = campaign_head(cartridge, key)
            final = campaign_head(cartridge, key + '-complete')
            assert final['previous'] is None and head['previous'] is None
            io_plan = head['value']['io_plan']
            assert head['value']['binding']['io_plan_digest'] == digest_bytes(canonical_bytes(io_plan))
            assert io_plan['recipe_digest'] == final['value']['recipe_digest']
            assert io_plan['prepass']['range_concurrency'] == 1
            assert io_plan['write']['range_concurrency'] == 2
            assert io_plan['prepass']['source_data_read_bytes'] == io_plan['write']['source_data_read_bytes']
            assert io_plan['prepass']['logical_source_bytes'] == 4194304 + 17
            assert composed['result']['composition_head'] == final['digest']
            assert composed['result']['ownership_digest'] == head['digest']
            assert composed['result']['output_count'] == 2
            expected_composed = b'\x00\xff' + artifact_one[1][7:7 + 4194304 + 17] + b'\x0a\x00'
            assert head['value']['outputs'] == [
                {'path': 'empty', 'size': 0, 'digest': 'sha256:' + hashlib.sha256(b'').hexdigest()},
                {'path': 'packed', 'size': len(expected_composed), 'digest': 'sha256:' + hashlib.sha256(expected_composed).hexdigest()},
            ]
            data = grant_transfer_extent(cartridge, composition_id, _transfer_extent_id(composition_id, 'packed', 'data'),
                len(expected_composed), capacity_controller=owner, require_existing=True)
            try:
                assert os.pread(data.fd, data.length, data.offset) == expected_composed
            finally:
                os.close(data.fd)
            assert 'source_lock' not in composed['result'] and 'immutable_revision' not in composed['result']
            assert asyncio.run(broker.compose_source(composition, owner)) == composed
            assert campaign_head(cartridge, key + '-complete') == final
            assert len([event for event in broker.events(composition_id) if event['type'] == 'completed']) == 1
            assert (log / (operation_id + '.json')).read_bytes() == original_record
            output_records = [campaign_head(cartridge, path.name) for path in (cartridge / 'campaign/heads').iterdir()
                              if path.name.startswith('source-compose-output-')]
            assert {item['value']['output']['path'] for item in output_records} == {'empty', 'packed'}
            assert digest_bytes(canonical_bytes([item['digest'] for item in sorted(output_records,
                key=lambda item: item['value']['output']['path'])])) == composed['result']['completion_records_digest']
            assert all(item['previous'] is None and item['value']['ownership_digest'] == head['digest']
                       for item in output_records)

            async def cancel_at_io(request, entered, release):
                task = asyncio.create_task(broker.compose_source(request, owner))
                try:
                    for _ in range(3000):
                        if entered.is_set():
                            break
                        assert not task.done(), task.result()
                        await asyncio.sleep(.01)
                    else:
                        raise AssertionError('owned composition did not reach the bounded I/O boundary')
                    broker.cancel(broker.operation_id(request))
                    release.set()
                    assert (await task)['state'] == 'CANCELLED'
                finally:
                    release.set()
                    if not task.done():
                        task.cancel()
                        await asyncio.gather(task, return_exceptions=True)

            # Q6/Q60: cancel during a bounded prepass read before any ownership publication.
            prepass = copy.deepcopy(composition)
            prepass['idempotency_key'] = 'l05-compose-prepass-cancel'
            prepass_id = broker.operation_id(prepass)
            source_data = grant_transfer_extent(cartridge, operation_id,
                _transfer_extent_id(operation_id, artifact_one[0], 'data'), len(artifact_one[1]),
                capacity_controller=owner, require_existing=True)
            source_inode = os.fstat(source_data.fd).st_ino
            os.close(source_data.fd)
            entered, release, prepass_fds = threading.Event(), threading.Event(), []
            native_pread = os.pread
            with monkeypatch.context() as hardware:
                def hold_source_read(descriptor, count, offset):
                    result = native_pread(descriptor, count, offset)
                    if os.fstat(descriptor).st_ino == source_inode and not entered.is_set():
                        prepass_fds.append(descriptor)
                        entered.set()
                        assert release.wait(10)
                    return result
                hardware.setattr(os, 'pread', hold_source_read)
                asyncio.run(cancel_at_io(prepass, entered, release))
            assert len(prepass_fds) == 1
            with pytest.raises(OSError):
                os.fstat(prepass_fds[0])
            assert campaign_head(cartridge, 'source-compose-' + prepass_id.removeprefix('op-')) is None
            assert not (cartridge / 'transfers' / prepass_id).exists()

            # Q6/Q53: a grant that completes during cancellation still closes its new descriptor.
            allocation = copy.deepcopy(composition)
            allocation['idempotency_key'] = 'l05-compose-allocation-cancel'
            allocation_id = broker.operation_id(allocation)
            filename = _transfer_extent_id(allocation_id, 'empty', 'data') + '.extent'
            entered, release, allocated_fds = threading.Event(), threading.Event(), []
            native_open = os.open
            with monkeypatch.context() as hardware:
                def hold_grant(path, *args, **kwargs):
                    descriptor = native_open(path, *args, **kwargs)
                    if path == filename and not entered.is_set():
                        allocated_fds.append(descriptor)
                        entered.set()
                        assert release.wait(10)
                    return descriptor
                hardware.setattr(os, 'open', hold_grant)
                asyncio.run(cancel_at_io(allocation, entered, release))
            assert len(allocated_fds) == 1
            with pytest.raises(OSError):
                os.fstat(allocated_fds[0])
            assert campaign_head(cartridge, 'source-compose-' + allocation_id.removeprefix('op-') + '-complete') is None

            # Q6/Q60: restart after the final store record and before canonical success.
            final_request = copy.deepcopy(composition)
            final_request['idempotency_key'] = 'l05-compose-final-boundary'
            final_id = broker.issue(final_request)['operation_id']
            final_key = 'source-compose-' + final_id.removeprefix('op-') + '-complete'
            broker.request_hold(final_id, 'result')
            async def stop_before_success():
                task = asyncio.create_task(broker.compose_source(final_request, owner))
                try:
                    for _ in range(3000):
                        if any(event['payload'].get('hold') == 'ACKNOWLEDGED' for event in broker.events(final_id)):
                            break
                        assert not task.done(), task.result()
                        await asyncio.sleep(.01)
                    else:
                        raise AssertionError('composition did not reach final record before canonical success')
                    assert broker.status(final_id)['state'] == 'RUNNING'
                    assert 'result' not in broker.status(final_id)
                    assert campaign_head(cartridge, final_key) is not None
                    task.cancel()
                    await asyncio.gather(task, return_exceptions=True)
                finally:
                    if not task.done():
                        task.cancel()
                        await asyncio.gather(task, return_exceptions=True)
            asyncio.run(stop_before_success())
            saved_final = campaign_head(cartridge, final_key)
            broker.close()
            broker = CanonicalBroker(log)
            broker.release_hold(final_id, 'result')
            repeated_final = asyncio.run(broker.compose_source(final_request, owner))
            assert repeated_final['state'] == 'SUCCEEDED'
            assert repeated_final['result']['composition_head'] == saved_final['digest']
            assert campaign_head(cartridge, final_key) == saved_final
            assert len([event for event in broker.events(final_id) if event['type'] == 'completed']) == 1
            assert (log / (operation_id + '.json')).read_bytes() == original_record
            with pytest.raises(CassetteError) as not_callable:
                broker.callable_revision(composition_id, cartridge)
            assert not_callable.value.code == 'OPERATION_NOT_FOUND'
            unknown = copy.deepcopy(composition)
            unknown['arguments']['composition']['input_manifests'] = {}
            assert validate('request', unknown)
            unfinished_request = _request('l05-unfinished-source')
            unfinished_id = broker.issue(unfinished_request)['operation_id']
            refused = copy.deepcopy(composition)
            refused.update(idempotency_key='l05-compose-unfinished-source', target=unfinished_id)
            refused['arguments']['composition']['acquisition_operation_id'] = unfinished_id
            rejected = asyncio.run(broker.compose_source(refused, owner))
            assert rejected['state'] == 'FAILED' and rejected['error']['code'] == 'INVALID_REQUEST'
            assert campaign_head(cartridge, 'source-compose-' + rejected['operation_id'].removeprefix('op-')) is None
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

            # Q42/Q43/Q60: a native window observes the actual prepass/owner/writer,
            # including concurrent ranges and repeated input verification. It is no
            # physical qualification, source access or cold-cache pass.
            capture_area = tmp_path / 'capture-fixture'
            capture_area.mkdir()
            _, mount = _attached_apfs_image(capture_area)
            capture_broker = CanonicalBroker(capture_area / 'operations')
            try:
                capture_cartridge = mount / 'CassetteCapture'
                capture_cartridge.mkdir()
                volume = next(item for item in list_external_apfs_volumes() if item.mount_path == str(mount))
                selection = select_external_apfs_volume(volume.volume_uuid)
                acquired_request = _request('l05-capture-input')
                acquired = asyncio.run(capture_broker.run_acquisition(acquired_request,
                    _context(capture_cartridge, server.base_url)))
                assert acquired['state'] == 'SUCCEEDED'
                acquired_id = acquired['operation_id']
                original_capture_input = (capture_area / 'operations' / (acquired_id + '.json')).read_bytes()
                capture_revision = _source_from(capture_broker._load(acquired_id)['checkpoint']['source_lock'], acquired_id)
                capture_recipe = copy.deepcopy(recipe)
                capture_recipe['source_record_digest'] = digest_bytes(canonical_bytes(capture_revision.record()))
                capture_recipe['artifacts'].insert(1, {'path': 'literal', 'segments': [{'literal_hex': '00ff'}]})
                capture_recipe['artifacts'][2]['segments'].extend([
                    {'path': artifact_one[0], 'offset': 0, 'length': 1} for _ in range(512)])
                capture_request = {'protocol_version': '1', 'operation': 'source.compose',
                    'idempotency_key': 'l05-capture-fresh', 'target': acquired_id,
                    'arguments': {'composition': {'acquisition_operation_id': acquired_id, 'recipe': capture_recipe}}}
                capture_owner = CapacityCoordinator(capture_cartridge)
                retained_captures = capture_area / 'retained-captures'
                retained_captures.mkdir()
                def retain_capture(capture, artifact_cartridge=None):
                    area = retained_captures / capture['capture_key']
                    area.mkdir()
                    (area / 'capture.json').write_bytes(canonical_bytes(capture))
                    recorded_cartridge = artifact_cartridge or capture_cartridge
                    owner_key = 'source-compose-' + capture['context']['operation_id'][3:]
                    for name, key in (('owner-head', owner_key), ('final-head', owner_key + '-complete')):
                        (area / (name + '.json')).write_bytes(canonical_bytes(campaign_head(recorded_cartridge, key)))
                    for reference in capture['traces']:
                        proof = verify_campaign_artifact(artifact_cartridge or capture_cartridge, reference['attempt'], reference['name'],
                            reference['digest'], reference['bytes'], maximum_bytes=2097152, include_rows=True)
                        payload = b''.join(canonical_bytes(row) + b'\n' for row in proof['rows'])
                        assert len(payload) == reference['bytes'] and digest_bytes(payload) == reference['digest']
                        (area / reference['name']).write_bytes(payload)
                fresh_id = capture_broker.issue(capture_request)['operation_id']
                capture_broker.request_hold(fresh_id, 'result')
                async def capture_result_hold():
                    task = asyncio.create_task(capture_broker._capture_composition_profile(capture_request,
                        capture_owner, selection, capture_key='l05-composition-fresh'))
                    try:
                        for _ in range(3000):
                            if any(event['payload'].get('hold') == 'ACKNOWLEDGED' for event in capture_broker.events(fresh_id)):
                                break
                            assert not task.done(), task.result()
                            await asyncio.sleep(.01)
                        else:
                            raise AssertionError('generation did not reach its canonical result hold')
                        await asyncio.sleep(.05)
                        capture_broker.release_hold(fresh_id, 'result')
                        return await task
                    finally:
                        if not task.done():
                            task.cancel()
                            await asyncio.gather(task, return_exceptions=True)
                captured = asyncio.run(capture_result_hold())
                retain_capture(captured)
                assert captured['status'] == 'CAPTURED' and captured['operation_state'] == 'SUCCEEDED'
                assert captured['execution_mode'] == 'FRESH'
                assert captured['context']['scope'] == 'RAW_COMPONENT_CAPTURE; QUALIFICATION_NOT_RUN'
                assert captured['cache_state'] == 'UNCONTROLLED; NOT_COLD_PROOF'
                assert captured['timing_evidence'] == 'RAW_WALL_WINDOW; HOLD_MARKERS_REQUIRE_SEGMENTATION'
                assert captured['native_window']['before']['path'] == captured['native_window']['after']['path']
                assert len(captured['traces']) >= 2
                rows = []
                for reference in captured['traces']:
                    assert reference['bytes'] <= 2097152
                    rows.extend(verify_campaign_artifact(capture_cartridge, reference['attempt'], reference['name'],
                        reference['digest'], reference['bytes'], maximum_bytes=2097152, include_rows=True)['rows'])
                assert rows[0]['kind'] == 'WINDOW_OPEN'
                assert [row['kind'] for row in rows if row.get('boundary') == 'result'] == ['HOLD_OPEN', 'HOLD_CLOSE']
                close_index = next(index for index, row in enumerate(rows) if row['kind'] == 'WINDOW_CLOSE')
                assert all(row['kind'] in {'CLAIM_ACCOUNTING_BOUNDARY', 'CAPACITY_CLAIM'} for row in rows[close_index + 1:])
                assert all(row['time_ns'] >= rows[close_index]['ended_ns'] for row in rows[close_index + 1:])
                assert any(row['kind'] == 'CAPACITY_CLAIM' for row in rows)
                assert all(row['role'].startswith(('source_', 'output_')) for row in rows if row['kind'] == 'EXTENT_BOUND')
                cap_id = captured['context']['operation_id']
                saved_owner = campaign_head(capture_cartridge, 'source-compose-' + cap_id.removeprefix('op-'))
                (retained_captures / 'fresh-owner.json').write_bytes(canonical_bytes(saved_owner))
                assert captured['owner_binding'] == saved_owner['value']['binding']
                assert captured['ownership_digest'] == saved_owner['digest']
                cap_plan = saved_owner['value']['io_plan']
                for phase_name, plan_name in [('PREPASS', 'prepass'), ('COMPOSE_WRITE', 'write')]:
                    selected_rows = [row for row in rows if row.get('phase') == phase_name]
                    for role, name in [('source_data', 'source_data_read_bytes'), ('source_state', 'source_state_read_bytes')]:
                        assert sum(row['returned_bytes'] for row in selected_rows if row.get('role') == role and row['kind'] == 'read') == cap_plan[plan_name][name]
                    opens = {(row['output'], row['range_offset'], row['range_started_ns']) for row in selected_rows if row['kind'] == 'RANGE_OPEN'}
                    closes = {(row['output'], row['range_offset'], row['range_started_ns']) for row in selected_rows if row['kind'] == 'RANGE_CLOSE' and row['success']}
                    assert opens == closes and len(opens) == cap_plan[plan_name]['range_calls']
                    assert all((row['output'], row['range_offset'], row['range_started_ns']) in opens
                               for row in selected_rows if row.get('role', '').startswith('source_'))
                assert sum(row['returned_bytes'] for row in rows if row.get('role') == 'output_data' and row['kind'] == 'write') == cap_plan['write']['output_data_write_bytes']
                assert any(row['kind'] == 'F_FULLFSYNC' and row.get('role') == 'output_state' for row in rows)
                statistics = asyncio.run(capture_broker._composition_statistics(capture_request,
                    capture_owner, capture_key='l05-composition-fresh'))
                assert statistics['status'] == 'RECOMPUTED_RAW'
                assert statistics['scope'] == 'FRESH_OBSERVATIONS_ONLY; QUALIFICATION_NOT_RUN'
                assert statistics['ownership_digest'] == captured['ownership_digest']
                assert statistics['phases']['PREPASS']['range_calls'] == cap_plan['prepass']['range_calls']
                # Q42: no-work ranges retain their count but do not measure byte throughput.
                assert statistics['phases']['PREPASS']['range_bytes_per_active_second']['samples'] == cap_plan['prepass']['range_calls'] - 1
                assert statistics['phases']['PREPASS']['range_bytes_per_active_second']['minimum'] > 0
                assert statistics['phases']['COMPOSE_WRITE']['range_calls'] == cap_plan['write']['range_calls']
                assert statistics['phases']['COMPOSE_WRITE']['peak_open_ranges'] == 2
                assert statistics['phases']['PREPASS']['io_bytes']['source_data.read'] == cap_plan['prepass']['source_data_read_bytes']
                assert statistics['phases']['COMPOSE_WRITE']['io_bytes']['output_data.write'] == cap_plan['write']['output_data_write_bytes']
                assert statistics['phases']['COMPOSE_WRITE']['source_to_durable_bytes_per_active_second']['samples'] == 3
                assert statistics['phases']['COMPOSE_WRITE']['source_to_durable_bytes_per_active_second']['empirical_percentiles'] == {}
                assert statistics['counter_scope'] == 'PROCESS_AND_SHARED_DEVICE; NOT_PER_RANGE_OR_PATH'
                assert statistics['hold_seconds'] >= .05
                assert statistics['active_seconds'] == pytest.approx(statistics['wall_seconds'] - statistics['hold_seconds'])
                assert statistics['issued_claim_count'] == sum(row['kind'] == 'CAPACITY_CLAIM' for row in rows)
                (retained_captures / 'fresh-statistics.json').write_bytes(canonical_bytes(statistics))
                # Q42: totals do not prove mapping, closeout or durability order.
                # Store-owned contradiction artifacts reach each deciding grammar guard.
                control_cartridge = capture_area / 'trace-controls'
                control_cartridge.mkdir()
                control_owner = CapacityCoordinator(control_cartridge)
                control_results = {}
                def check_trace(name, changed_rows, capture_value=captured, stats_request=capture_request, capture_patch=None):
                    key = 'l05-composition-contradiction-' + name
                    owner_key = 'source-compose-' + capture_value['context']['operation_id'][3:]
                    for original_key in (owner_key, owner_key + '-complete'):
                        saved = campaign_head(capture_cartridge, original_key)
                        copied = campaign_head(control_cartridge, original_key)
                        if saved is None:
                            assert copied is None
                            continue
                        if copied is None:
                            copied = compare_campaign_head(control_owner, original_key, None, saved['value'])
                        assert copied['digest'] == saved['digest']
                    payload = b''.join(canonical_bytes(row) + b'\n' for row in changed_rows)
                    write_campaign_artifact(control_owner, key, 'contradiction.jsonl', payload)
                    value = {**campaign_head(capture_cartridge, capture_value['capture_key'])['value'],
                        **(capture_patch or {}),
                        'traces': [{'attempt': key, 'name': 'contradiction.jsonl',
                                    'digest': digest_bytes(payload), 'bytes': len(payload)}]}
                    saved = compare_campaign_head(control_owner, key, None, value)
                    retain_capture({**value, 'capture_key': key, 'capture_digest': saved['digest']}, control_cartridge)
                    try:
                        result = asyncio.run(capture_broker._composition_statistics(stats_request,
                            control_owner, capture_key=key))
                        control_results[name] = {'accepted': True, 'status': result['status'], 'statistics': result}
                    except CassetteError as error:
                        control_results[name] = {'accepted': False, 'code': error.code, 'detail': error.detail}
                def short_calls():
                    changed = copy.deepcopy(rows)
                    for kind in ('write', 'read'):
                        index = next(i for i, row in enumerate(changed) if row['kind'] == kind
                            and row.get('role') == 'output_data' and row['path'] == 'packed' and row['offset'] == 0)
                        row = changed[index]
                        half, duration = row['returned_bytes'] // 2, row['duration_ns'] // 2
                        changed[index:index + 1] = [
                            {**row, 'returned_bytes': half, 'duration_ns': duration},
                            {**row, 'offset': half, 'requested_bytes': row['returned_bytes'] - half,
                             'returned_bytes': row['returned_bytes'] - half,
                             'started_ns': row['started_ns'] + duration, 'duration_ns': row['duration_ns'] - duration}]
                    return changed
                check_trace('short-calls', short_calls())
                expected_errors = {}
                for contradiction in ('span', 'range-close', 'checkpoint-sync', 'window', 'boundary-time', 'boundary-outside-window',
                                      'stale-data-sync', 'checkpoint-before-data', 'readback-before-write',
                                      'read-before-range', 'range-after-reads', 'output-before-range',
                                      'checkpoint-first', 'checkpoint-refence', 'checkpoint-after-boundary', 'initial-state-unfenced',
                                      'header-before-data', 'empty-after-complete', 'complete-phase-time', 'output-commit-phase-time'):
                    changed_rows = short_calls() if contradiction in {
                        'stale-data-sync', 'checkpoint-before-data', 'readback-before-write', 'checkpoint-refence'} else copy.deepcopy(rows)
                    if contradiction == 'span':
                        altered = next(row for row in changed_rows if row.get('role') == 'source_data' and row['kind'] == 'read')
                        altered['source_offset'] += 1
                        expected_error = 'source span differs'
                    elif contradiction == 'range-close':
                        removed = next(row for row in changed_rows if row['kind'] == 'RANGE_CLOSE')
                        changed_rows.remove(removed)
                        expected_error = 'ranges exceed their declared concurrency'
                    elif contradiction == 'checkpoint-sync':
                        removed = next(row for row in changed_rows if row.get('role') == 'output_state'
                            and row['kind'] == 'F_FULLFSYNC' and row['phase'] == 'COMPOSE_WRITE'
                            and any(prior['kind'] == 'write' and prior.get('role') == 'output_data'
                                    for prior in changed_rows[:changed_rows.index(row)]))
                        changed_rows.remove(removed)
                        expected_error = 'synchronized range'
                    elif contradiction == 'boundary-time':
                        altered = next(row for row in changed_rows if row['kind'] == 'OUTPUT_BOUNDARY' and row['output'] == 'packed')
                        opened = next(row for row in changed_rows if row['kind'] == 'RANGE_OPEN'
                            and row['phase'] == 'COMPOSE_WRITE' and row['output'] == 'packed' and row['range_offset'] == 0)
                        altered['time_ns'] = opened['range_started_ns'] + 1
                        expected_error = 'checkpoint precedes its observed I/O'
                    elif contradiction == 'boundary-outside-window':
                        altered = next(row for row in changed_rows if row['kind'] == 'OUTPUT_BOUNDARY' and row['output'] == 'packed')
                        closed = next(row for row in changed_rows if row['kind'] == 'WINDOW_CLOSE')
                        altered['time_ns'] = closed['ended_ns'] + 1000000000
                        expected_error = 'native window ends before its observed execution'
                    elif contradiction in {'stale-data-sync', 'checkpoint-before-data', 'readback-before-write'}:
                        second = [row for row in changed_rows if row.get('role') == 'output_data' and row.get('path') == 'packed'
                                  and row['kind'] in {'write', 'read'} and row['offset'] == 2097152]
                        assert len(second) == 2
                        if contradiction == 'readback-before-write':
                            later_write = next(row for row in second if row['kind'] == 'write')
                            changed_rows.remove(later_write)
                            later_read = next(row for row in second if row['kind'] == 'read')
                            changed_rows.insert(changed_rows.index(later_read) + 1, later_write)
                            expected_error = 'readback lacks its observed write'
                        else:
                            for row in second:
                                changed_rows.remove(row)
                            role = 'output_data' if contradiction == 'stale-data-sync' else 'output_state'
                            fence = next(row for row in changed_rows if row['kind'] == 'F_FULLFSYNC'
                                and row.get('role') == role and row.get('path') == 'packed'
                                and any(prior['kind'] == 'write' and prior.get('role') == 'output_data'
                                        and prior.get('path') == 'packed' for prior in changed_rows[:changed_rows.index(row)]))
                            index = changed_rows.index(fence) + 1
                            changed_rows[index:index] = second
                            expected_error = ('checkpoint write precedes its synchronized output data'
                                              if contradiction == 'stale-data-sync' else 'synchronized range')
                    elif contradiction == 'checkpoint-first':
                        first_write = next(row for row in changed_rows if row['kind'] == 'write' and row.get('role') == 'output_data'
                            and row.get('path') == 'packed')
                        boundary = next(row for row in changed_rows if row['kind'] == 'OUTPUT_BOUNDARY' and row.get('output') == 'packed')
                        state_rows = [row for row in changed_rows[changed_rows.index(first_write):changed_rows.index(boundary)]
                            if row.get('role') == 'output_state' and row['kind'] in {'write', 'read'}]
                        assert len(state_rows) == 4
                        for row in state_rows:
                            changed_rows.remove(row)
                        index = changed_rows.index(first_write)
                        changed_rows[index:index] = state_rows
                        expected_error = 'initializing header or synchronized output range'
                    elif contradiction == 'checkpoint-refence':
                        later = [row for row in changed_rows if row.get('role') == 'output_data' and row.get('path') == 'packed'
                            and row['kind'] in {'write', 'read'} and row['offset'] == 2097152]
                        assert len(later) == 2
                        for row in later:
                            changed_rows.remove(row)
                        state_fence = next(row for row in changed_rows if row['kind'] == 'F_FULLFSYNC'
                            and row.get('role') == 'output_state' and row.get('path') == 'packed'
                            and any(prior['kind'] == 'write' and prior.get('role') == 'output_data'
                                and prior.get('path') == 'packed' for prior in changed_rows[:changed_rows.index(row)]))
                        data_fence = next(row for row in changed_rows if row['kind'] == 'F_FULLFSYNC'
                            and row.get('role') == 'output_data' and row.get('path') == 'packed')
                        index = changed_rows.index(state_fence) + 1
                        changed_rows[index:index] = [*later, copy.deepcopy(data_fence), copy.deepcopy(state_fence)]
                        expected_error = 'later checkpoint write'
                    elif contradiction == 'checkpoint-after-boundary':
                        boundary = next(row for row in reversed(changed_rows) if row['kind'] == 'OUTPUT_BOUNDARY' and row.get('output') == 'packed')
                        last_write = next(row for row in reversed(changed_rows[:changed_rows.index(boundary)])
                            if row['kind'] == 'write' and row.get('role') == 'output_data' and row.get('path') == 'packed')
                        state_rows = [row for row in changed_rows[changed_rows.index(last_write):changed_rows.index(boundary)]
                            if row.get('role') == 'output_state' and row['kind'] in {'write', 'read'}][-2:]
                        assert len(state_rows) == 2
                        for row in state_rows:
                            changed_rows.remove(row)
                        index = changed_rows.index(boundary) + 1
                        changed_rows[index:index] = state_rows
                        expected_error = 'checkpoint sync lacks data durability or a later checkpoint write'
                    elif contradiction == 'initial-state-unfenced':
                        removed = next(row for row in changed_rows if row['kind'] == 'F_FULLFSYNC'
                            and row.get('role') == 'output_state' and row.get('path') == 'empty')
                        changed_rows.remove(removed)
                        expected_error = 'output commit differs from its exact durable frontier'
                    elif contradiction == 'header-before-data':
                        first_write = next(row for row in changed_rows if row['kind'] == 'write'
                            and row.get('role') == 'output_data' and row.get('path') == 'packed')
                        header_write = next(row for row in changed_rows[changed_rows.index(first_write):]
                            if row['kind'] == 'write' and row.get('role') == 'output_state' and row.get('path') == 'packed'
                            and 0 < row['offset'] < transfer_state_bytes(0))
                        header_read = next(row for row in changed_rows[changed_rows.index(header_write):]
                            if row['kind'] == 'read' and row.get('role') == 'output_state' and row.get('path') == 'packed'
                            and row['offset'] == header_write['offset'])
                        for index, row in enumerate((header_write, header_read)):
                            changed_rows.remove(row)
                            row.update(started_ns=first_write['started_ns'] - 3 + index, duration_ns=1)
                        changed_rows[changed_rows.index(first_write):changed_rows.index(first_write)] = [header_write, header_read]
                        expected_error = 'initializing header or synchronized output range'
                    elif contradiction == 'empty-after-complete':
                        complete_row = next(row for row in changed_rows if row['kind'] == 'PHASE' and row.get('phase') == 'COMPLETE')
                        empty_write = next(row for row in changed_rows if row['kind'] == 'write'
                            and row.get('role') == 'output_state' and row.get('path') == 'empty')
                        copied = [copy.deepcopy(row) for row in changed_rows[changed_rows.index(empty_write):] if row.get('role') == 'output_state'
                            and row.get('path') == 'empty' and row['kind'] in {'write', 'read', 'F_FULLFSYNC'}]
                        assert len(copied) == 3
                        for index, row in enumerate(copied):
                            row.update(started_ns=complete_row['time_ns'] + index * 2 + 1, duration_ns=1)
                        index = changed_rows.index(complete_row) + 1
                        changed_rows[index:index] = copied
                        expected_error = 'output I/O follows its committed output'
                    elif contradiction in {'complete-phase-time', 'output-commit-phase-time'}:
                        phase = 'COMPLETE' if contradiction == 'complete-phase-time' else 'OUTPUT_COMMIT'
                        altered = next(row for row in changed_rows if row['kind'] == 'PHASE' and row.get('phase') == phase)
                        closed = next(row for row in changed_rows if row['kind'] == 'WINDOW_CLOSE')
                        altered['time_ns'] = closed['ended_ns'] + 1000000000
                        expected_error = 'native window ends before its observed execution'
                    elif contradiction in {'read-before-range', 'range-after-reads', 'output-before-range'}:
                        phase = 'COMPOSE_WRITE' if contradiction == 'output-before-range' else 'PREPASS'
                        opened = next(row for row in changed_rows if row['kind'] == 'RANGE_OPEN'
                            and row['phase'] == phase and row['output'] == 'packed' and row['range_offset'] == 0)
                        if contradiction == 'range-after-reads':
                            old_start = opened['range_started_ns']
                            members = [row for row in changed_rows if row.get('phase') == phase and row.get('output') == 'packed'
                                and row.get('range_offset') == 0 and row.get('range_started_ns') == old_start]
                            new_start = min(row['started_ns'] for row in members if row['kind'] == 'read') + 1
                            for row in members:
                                row['range_started_ns'] = new_start
                        else:
                            altered = next(row for row in changed_rows if row['kind'] == ('write' if contradiction == 'output-before-range' else 'read')
                                and row.get('role') == ('output_data' if contradiction == 'output-before-range' else 'source_state')
                                and row.get('path', row.get('output')) == 'packed' and row['phase'] == phase)
                            end = altered['started_ns'] + altered['duration_ns']
                            altered['started_ns'] = opened['range_started_ns'] - 1
                            altered['duration_ns'] = end - altered['started_ns']
                        expected_error = ('output I/O starts before its fetched range' if contradiction == 'output-before-range'
                                          else 'source I/O starts before its observed range')
                    else:
                        altered = next(row for row in changed_rows if row['kind'] == 'WINDOW_CLOSE')
                        altered['ended_ns'] = rows[0]['started_ns']
                        expected_error = 'positive monotonic duration'
                    check_trace(contradiction, changed_rows)
                    expected_errors[contradiction] = expected_error
                (retained_captures / 'trace-controls.json').write_bytes(canonical_bytes(control_results))
                assert control_results['short-calls']['accepted'] is True
                assert {name: result for name, result in control_results.items()
                        if name != 'short-calls' and result['accepted']} == {}
                for name, expected_error in expected_errors.items():
                    assert control_results[name]['code'] == 'ROOT_INVALID'
                    assert expected_error in control_results[name]['detail']
                canonical_completed = capture_broker._load(cap_id)
                assert asyncio.run(capture_broker._capture_composition_profile(capture_request,
                    capture_owner, selection, capture_key='l05-composition-fresh')) == captured
                assert capture_broker._load(cap_id) == canonical_completed
                with pytest.raises(CassetteError) as terminal_capture:
                    asyncio.run(capture_broker._capture_composition_profile(capture_request,
                        capture_owner, selection, capture_key='l05-composition-terminal'))
                assert terminal_capture.value.code == 'INVALID_REQUEST'
                assert campaign_head(capture_cartridge, 'l05-composition-terminal') is None
                with pytest.raises(CassetteError) as wrong_device:
                    asyncio.run(capture_broker._capture_composition_profile(capture_request,
                        capture_owner, replace(selection, volume=replace(selection.volume, mount_path=str(tmp_path))),
                        capture_key='l05-composition-wrong-device'))
                assert wrong_device.value.code == 'INVALID_REQUEST'
                paused_request = copy.deepcopy(capture_request)
                paused_request['idempotency_key'] = 'l05-capture-paused'
                paused_request['arguments']['composition']['recipe'] = copy.deepcopy(recipe)
                paused_request['arguments']['composition']['recipe']['source_record_digest'] = capture_recipe['source_record_digest']
                paused_request['arguments']['composition']['recipe']['artifacts'].append(
                    {'path': 'tail', 'segments': [{'literal_hex': '1234'}]})
                paused_id = capture_broker.issue(paused_request)['operation_id']
                capture_broker.request_hold(paused_id, 'composition-checkpoint')
                async def pause_capture():
                    task = asyncio.create_task(capture_broker._capture_composition_profile(paused_request,
                        CapacityCoordinator(capture_cartridge), selection, capture_key='l05-composition-paused'))
                    try:
                        for _ in range(3000):
                            if any(event['payload'].get('hold') == 'ACKNOWLEDGED' for event in capture_broker.events(paused_id)):
                                break
                            assert not task.done(), task.result()
                            await asyncio.sleep(.01)
                        else:
                            raise AssertionError('captured composition did not reach its durable hold')
                        capture_broker.pause(paused_id)
                        return await task
                    finally:
                        if not task.done():
                            task.cancel()
                            await asyncio.gather(task, return_exceptions=True)
                incomplete = asyncio.run(pause_capture())
                retain_capture(incomplete)
                assert incomplete['status'] == 'INCOMPLETE' and incomplete['operation_state'] == 'PAUSED'
                with pytest.raises(CassetteError) as rejected_attempt:
                    asyncio.run(capture_broker._capture_composition_profile(paused_request,
                        CapacityCoordinator(capture_cartridge), selection, capture_key='l05-composition-paused'))
                assert rejected_attempt.value.code == 'SOURCE_UNAVAILABLE'
                capture_broker.resume(paused_id)
                capture_broker.release_hold(paused_id, 'composition-checkpoint')
                recovered = asyncio.run(capture_broker._capture_composition_profile(paused_request,
                    CapacityCoordinator(capture_cartridge), selection, capture_key='l05-composition-recovered'))
                retain_capture(recovered)
                assert recovered['status'] == 'CAPTURED' and recovered['execution_mode'] == 'RESUME'
                assert campaign_head(capture_cartridge, 'l05-composition-paused')['digest'] == incomplete['capture_digest']
                recovery_statistics = asyncio.run(capture_broker._composition_statistics(paused_request,
                    CapacityCoordinator(capture_cartridge), capture_key='l05-composition-recovered'))
                assert recovery_statistics['status'] == 'RECOMPUTED_RAW'
                assert recovery_statistics['scope'] == 'RESUMED_OBSERVATIONS_ONLY; QUALIFICATION_NOT_RUN'
                assert recovery_statistics['phases']['PREPASS']['range_calls'] == 0
                assert recovery_statistics['phases']['COMPOSE_WRITE']['range_calls'] == 2
                assert recovery_statistics['phases']['COMPOSE_WRITE']['io_bytes']['output_data.write'] == 23
                assert recovery_statistics['phases']['COMPOSE_WRITE']['source_to_durable_bytes_per_active_second']['samples'] == 2
                assert recovery_statistics['retained_output']['verified_bytes'] == 4194304
                assert recovery_statistics['retained_output']['checkpoint_read_bytes'] == transfer_state_bytes(0) + transfer_state_bytes(4194304)
                assert recovery_statistics['retained_output']['output_frontiers'] == {'empty': 0, 'packed': 4194304}
                (retained_captures / 'recovery-statistics.json').write_bytes(canonical_bytes(recovery_statistics))
                recovery_rows = [json.loads(line) for reference in recovered['traces']
                    for line in (retained_captures / 'l05-composition-recovered' / reference['name']).read_text().splitlines()]
                for contradiction, expected_error in (
                        ('missing-prefix', 'exact verified prefix and checkpoint'),
                        ('prefix-length', 'exact preceding chunk read'),
                        ('checkpoint-read', 'checkpoint prefix is discontinuous'),
                        ('prefix-time', 'precedes its observed prefix verification'),
                        ('source-state-size', 'admitted byte geometry'),
                        ('record-after-data', 'exact verified prefix and checkpoint'),
                        ('record-after-prefix', 'exact verified prefix and checkpoint'),
                        ('probe-as-retained', 'exact verified prefix and checkpoint'),
                        ('new-probe-as-retained', 'exact verified prefix and checkpoint')):
                    changed_rows = copy.deepcopy(recovery_rows)
                    if contradiction in {'missing-prefix', 'prefix-length'}:
                        altered = next(row for row in changed_rows if row['kind'] == 'VERIFIED_PREFIX' and row.get('role') == 'output_data')
                        if contradiction == 'missing-prefix':
                            changed_rows.remove(altered)
                        else:
                            altered['length'] -= 1
                    elif contradiction == 'checkpoint-read':
                        altered = next(row for row in changed_rows if row['kind'] == 'read' and row.get('role') == 'output_state'
                            and row.get('path') == 'packed')
                        altered['offset'] += 1
                    elif contradiction == 'prefix-time':
                        altered = next(row for row in changed_rows if row['kind'] == 'OUTPUT_BOUNDARY' and row.get('output') == 'packed')
                        prefix = next(row for row in changed_rows if row['kind'] == 'VERIFIED_PREFIX' and row.get('role') == 'output_data')
                        altered['time_ns'] = prefix['time_ns'] - 1
                    elif contradiction in {'record-after-data', 'record-after-prefix'}:
                        altered = next(row for row in changed_rows if row['kind'] == 'read' and row.get('role') == 'output_state'
                            and row.get('path') == 'packed' and row['offset'] >= transfer_state_bytes(0))
                        changed_rows.remove(altered)
                        if contradiction == 'record-after-data':
                            target = next(row for row in changed_rows if row['kind'] == 'read' and row.get('role') == 'output_data'
                                and row.get('path') == 'packed')
                            ended = target['started_ns'] + target['duration_ns']
                        else:
                            target = next(row for row in changed_rows if row['kind'] == 'VERIFIED_PREFIX' and row.get('role') == 'output_data')
                            ended = target['time_ns']
                        altered.update(started_ns=ended + 1, duration_ns=1)
                        changed_rows.insert(changed_rows.index(target) + 1, altered)
                    elif contradiction in {'probe-as-retained', 'new-probe-as-retained'}:
                        if contradiction == 'probe-as-retained':
                            initial = next(row for row in changed_rows if row['kind'] == 'write'
                                and row.get('role') == 'output_state' and row.get('path') == 'tail')
                            fence = next(row for row in reversed(changed_rows[:changed_rows.index(initial)])
                                if row['kind'] == 'read' and row.get('role') == 'output_state' and row.get('path') == 'tail')
                            start = changed_rows.index(initial)
                            stop = next(index for index in range(start, len(changed_rows))
                                if changed_rows[index]['kind'] == 'F_FULLFSYNC'
                                and changed_rows[index].get('role') == 'output_state' and changed_rows[index].get('path') == 'tail')
                            assert [row['kind'] for row in changed_rows[start:stop + 1]] == ['write', 'read', 'fsync', 'F_FULLFSYNC']
                            del changed_rows[start:stop + 1]
                        else:
                            fence = next(row for row in changed_rows if row['kind'] == 'F_FULLFSYNC'
                                and row.get('role') == 'output_state' and row.get('path') == 'tail')
                        empty_boundary = next(row for row in changed_rows if row['kind'] == 'OUTPUT_BOUNDARY' and row.get('output') == 'empty')
                        fake = {**empty_boundary, 'output': 'tail', 'time_ns': fence['started_ns'] + fence['duration_ns'] + 1}
                        changed_rows.insert(changed_rows.index(fence) + 1, fake)
                    else:
                        altered = next(row for row in changed_rows if row['kind'] == 'EXTENT_BOUND' and row.get('role') == 'source_state')
                        altered['length'] += 1
                    name = 'resume-' + contradiction
                    check_trace(name, changed_rows, recovered, paused_request)
                    assert control_results[name]['accepted'] is False
                    assert control_results[name]['code'] == 'ROOT_INVALID'
                    assert expected_error in control_results[name]['detail']
                (retained_captures / 'trace-controls.json').write_bytes(canonical_bytes(control_results))
                paused_statistics = asyncio.run(capture_broker._composition_statistics(paused_request,
                    CapacityCoordinator(capture_cartridge), capture_key='l05-composition-paused'))
                assert paused_statistics['status'] == 'RECOMPUTED_INCOMPLETE_RAW'
                assert paused_statistics['capture_status'] == 'INCOMPLETE'
                assert paused_statistics['scope'] == 'INCOMPLETE_OBSERVATIONS_ONLY; QUALIFICATION_NOT_RUN'
                assert paused_statistics['completion_record_observed'] is False
                assert paused_statistics['frontiers']['durable_output'] == {'packed': 4194304}
                assert paused_statistics['frontiers']['fetched_ranges'] == 1
                assert paused_statistics['global_counter_deltas']['device_read_bytes'] is not None
                assert paused_statistics['issued_claim_count'] > 0
                (retained_captures / 'paused-statistics.json').write_bytes(canonical_bytes(paused_statistics))
                # Q60: final publication can survive a caller lost before canonical success.
                fully_written = copy.deepcopy(paused_request)
                fully_written['idempotency_key'] = 'l05-capture-all-prefix'
                fully_written_id = capture_broker.issue(fully_written)['operation_id']
                capture_broker.request_hold(fully_written_id, 'result')
                async def stop_full_capture():
                    task = asyncio.create_task(capture_broker._capture_composition_profile(fully_written,
                        CapacityCoordinator(capture_cartridge), selection, capture_key='l05-all-prefix-interrupted'))
                    try:
                        for _ in range(3000):
                            if any(event['payload'].get('hold') == 'ACKNOWLEDGED' for event in capture_broker.events(fully_written_id)):
                                break
                            assert not task.done(), task.result()
                            await asyncio.sleep(.01)
                        else:
                            raise AssertionError('fully written capture did not reach its canonical result hold')
                        assert campaign_head(capture_cartridge, 'source-compose-' + fully_written_id[3:] + '-complete') is not None
                        task.cancel()
                        with pytest.raises(asyncio.CancelledError):
                            await task
                    finally:
                        if not task.done():
                            task.cancel()
                            await asyncio.gather(task, return_exceptions=True)
                asyncio.run(stop_full_capture())
                failed_full = campaign_head(capture_cartridge, 'l05-all-prefix-interrupted')
                retain_capture({**failed_full['value'], 'capture_key': failed_full['key'], 'capture_digest': failed_full['digest']})
                capture_broker.close()
                capture_broker = CanonicalBroker(capture_area / 'operations')
                capture_broker.release_hold(fully_written_id, 'result')
                all_prefix = asyncio.run(capture_broker._capture_composition_profile(fully_written,
                    CapacityCoordinator(capture_cartridge), selection, capture_key='l05-all-prefix-recovered'))
                retain_capture(all_prefix)
                all_prefix_statistics = asyncio.run(capture_broker._composition_statistics(fully_written,
                    CapacityCoordinator(capture_cartridge), capture_key='l05-all-prefix-recovered'))
                assert all_prefix_statistics['scope'] == 'RESUMED_OBSERVATIONS_ONLY; QUALIFICATION_NOT_RUN'
                assert all_prefix_statistics['phases']['PREPASS']['range_calls'] == 0
                assert all_prefix_statistics['phases']['COMPOSE_WRITE']['range_calls'] == 0
                assert all_prefix_statistics['phases']['COMPOSE_WRITE']['io_bytes'].get('output_data.write', 0) == 0
                assert all_prefix_statistics['phases']['COMPOSE_WRITE']['source_to_durable_bytes_per_active_second']['samples'] == 0
                assert all_prefix_statistics['retained_output']['verified_bytes'] == 4194327
                assert all_prefix_statistics['retained_output']['output_frontiers'] == {'empty': 0, 'packed': 4194325, 'tail': 2}
                (retained_captures / 'all-prefix-statistics.json').write_bytes(canonical_bytes(all_prefix_statistics))
                full_interruption_statistics = asyncio.run(capture_broker._composition_statistics(fully_written,
                    CapacityCoordinator(capture_cartridge), capture_key='l05-all-prefix-interrupted'))
                assert full_interruption_statistics['status'] == 'RECOMPUTED_INCOMPLETE_RAW'
                assert full_interruption_statistics['canonical_operation_state'] == 'SUCCEEDED'
                assert full_interruption_statistics['completion_record_observed'] is True
                assert full_interruption_statistics['frontiers']['durable_output'] == {'packed': 4194325, 'tail': 2}
                assert set(full_interruption_statistics['global_counter_deltas'].values()) == {None}
                assert full_interruption_statistics['issued_claim_count'] is None
                (retained_captures / 'full-interruption-statistics.json').write_bytes(canonical_bytes(full_interruption_statistics))
                cancelled_request = copy.deepcopy(paused_request)
                cancelled_request['idempotency_key'] = 'l05-capture-coroutine-cancelled'
                cancelled_id = capture_broker.issue(cancelled_request)['operation_id']
                capture_broker.request_hold(cancelled_id, 'composition-checkpoint')
                async def cancel_capture():
                    task = asyncio.create_task(capture_broker._capture_composition_profile(cancelled_request,
                        CapacityCoordinator(capture_cartridge), selection, capture_key='l05-composition-cancelled'))
                    try:
                        for _ in range(3000):
                            if any(event['payload'].get('hold') == 'ACKNOWLEDGED' for event in capture_broker.events(cancelled_id)):
                                break
                            assert not task.done(), task.result()
                            await asyncio.sleep(.01)
                        else:
                            raise AssertionError('cancelled capture did not reach its committed hold')
                        task.cancel()
                        with pytest.raises(asyncio.CancelledError):
                            await task
                    finally:
                        if not task.done():
                            task.cancel()
                            await asyncio.gather(task, return_exceptions=True)
                asyncio.run(cancel_capture())
                interrupted = campaign_head(capture_cartridge, 'l05-composition-cancelled')
                assert interrupted['value']['status'] == 'INCOMPLETE'
                assert interrupted['value']['error']['type'] == 'CancelledError'
                interrupted_capture = {**interrupted['value'], 'capture_key': 'l05-composition-cancelled',
                                       'capture_digest': interrupted['digest']}
                retain_capture(interrupted_capture)
                assert capture_broker.cancel(cancelled_id)['state'] == 'CANCELLED'
                cancelled_statistics = asyncio.run(capture_broker._composition_statistics(cancelled_request,
                    CapacityCoordinator(capture_cartridge), capture_key='l05-composition-cancelled'))
                assert cancelled_statistics['status'] == 'RECOMPUTED_INCOMPLETE_RAW'
                assert cancelled_statistics['canonical_operation_state'] == 'CANCELLED'
                assert cancelled_statistics['completion_record_observed'] is False
                assert cancelled_statistics['frontiers']['durable_output'] == {'packed': 4194304}
                assert cancelled_statistics['frontiers']['fetched_ranges'] == 1
                assert set(cancelled_statistics['global_counter_deltas'].values()) == {None}
                assert cancelled_statistics['issued_claim_count'] is None
                (retained_captures / 'cancelled-statistics.json').write_bytes(canonical_bytes(cancelled_statistics))
                interrupted_rows = [json.loads(line) for reference in interrupted_capture['traces']
                    for line in (retained_captures / 'l05-composition-cancelled' / reference['name']).read_text().splitlines()]
                for name, expected_error in (('end-before-io', 'before its observed execution'),
                                              ('invented-owner', 'owner marker differs'),
                                              ('invented-row-endpoint', 'invents unavailable'),
                                              ('invented-endpoint', 'invents unavailable')):
                    changed = copy.deepcopy(interrupted_rows)
                    patch = None
                    if name == 'end-before-io':
                        changed[-1]['ended_ns'] = changed[0]['started_ns'] + 1
                    elif name == 'invented-owner':
                        next(row for row in changed if row['kind'] == 'OWNERSHIP')['digest'] = 'blake3:' + '0' * 64
                    elif name == 'invented-row-endpoint':
                        changed[-1].update(device=interrupted_rows[0]['device'], host=interrupted_rows[0]['host'])
                    else:
                        patch = {'duration_seconds': 0}
                    check_trace('incomplete-' + name, changed, interrupted_capture, cancelled_request, patch)
                    control = control_results['incomplete-' + name]
                    assert control['accepted'] is False and expected_error in control['detail']
                hold_index = next(i for i, row in enumerate(interrupted_rows) if row['kind'] == 'HOLD_OPEN')
                open_hold_rows = interrupted_rows[:hold_index + 1] + [interrupted_rows[-1]]
                check_trace('incomplete-open-hold', open_hold_rows, interrupted_capture, cancelled_request)
                open_hold_statistics = control_results['incomplete-open-hold']['statistics']
                assert open_hold_statistics['active_seconds'] is None
                assert open_hold_statistics['open_hold']['boundary'] == 'composition-checkpoint'
                assert open_hold_statistics['phases']['COMPOSE_WRITE']['range_bytes_per_active_second'] is None
                call = next(row for row in interrupted_rows if row.get('role') == 'source_state' and row['kind'] == 'read')
                range_index = next(i for i, row in enumerate(interrupted_rows) if row['kind'] == 'RANGE_OPEN'
                    and all(row[field] == call[field] for field in ('phase', 'output', 'range_offset', 'range_started_ns')))
                failure = {'type': 'OSError', 'code': None, 'detail': 'synthetic failed-call observation'}
                failed_rows = interrupted_rows[:range_index + 1] + [
                    {**call, 'returned_bytes': 0, 'success': False, 'error_type': 'OSError'},
                    {**interrupted_rows[range_index], 'kind': 'RANGE_CLOSE', 'success': False, 'error_type': 'OSError',
                     'ended_ns': call['started_ns'] + call['duration_ns'] + 1},
                    {**interrupted_rows[-1], 'error': failure}]
                check_trace('incomplete-failed-call', failed_rows, interrupted_capture, cancelled_request, {'error': failure})
                failed_statistics = control_results['incomplete-failed-call']['statistics']
                assert failed_statistics['phases']['PREPASS']['range_calls'] == sum(
                    row['kind'] == 'RANGE_CLOSE' and row.get('success') is True for row in interrupted_rows[:range_index])
                assert failed_statistics['phases']['PREPASS']['failed_ranges'] == 1
                assert failed_statistics['phases']['PREPASS']['failed_calls']['source_state.read:OSError']['samples'] == 1
                assert failed_statistics['ownership_digest'] is None
                open_range = {**interrupted_rows[range_index], 'range_started_ns': interrupted_rows[-1]['ended_ns'] + 1}
                changed = interrupted_rows[:range_index] + [open_range, interrupted_rows[-1]]
                check_trace('incomplete-open-range-after-window', changed, interrupted_capture, cancelled_request)
                control = control_results['incomplete-open-range-after-window']
                assert control['accepted'] is False and 'before its observed execution' in control['detail']
                # Q60: observed close endpoints survive a later interruption; a partial claim tail stays partial.
                close_index = next(index for index, row in enumerate(rows) if row['kind'] == 'WINDOW_CLOSE')
                tail = rows[close_index + 1:]
                claim_total = tail[0]['claim_count']
                assert claim_total > 1 and len(tail) == claim_total + 1
                incomplete_patch = {field: None for field in ('operation_state', 'operation_error',
                    'operation_result_digest', 'owner_binding', 'ownership_digest', 'execution_mode',
                    'composition_head', 'duration_seconds', 'native_window', 'host_window', 'claim_scope')}
                incomplete_patch.update(status='INCOMPLETE', error={'type': 'CancelledError', 'code': None, 'detail': ''})
                for name, claim_tail, accepted in (('absent', [], True), ('partial', tail[:2], True),
                        ('complete', tail, True), ('excess', [*tail, copy.deepcopy(tail[-1])], False)):
                    changed = copy.deepcopy(rows[:close_index + 1] + claim_tail)
                    changed.append({'kind': 'WINDOW_INTERRUPTED',
                        'ended_ns': max(row.get('time_ns', row.get('ended_ns', 0)) for row in changed) + 1,
                        'error': incomplete_patch['error']})
                    if name == 'complete':
                        complete_post_close_rows = changed
                    check_trace('post-close-' + name, changed, captured, capture_request, incomplete_patch)
                    result = control_results['post-close-' + name]
                    assert result['accepted'] is accepted
                    if accepted:
                        post_close = result['statistics']
                        assert post_close['status'] == 'RECOMPUTED_INCOMPLETE_RAW'
                        assert post_close['canonical_operation_state'] == 'SUCCEEDED'
                        assert post_close['global_counter_deltas'] == statistics['global_counter_deltas']
                        assert post_close['issued_claim_count'] == (claim_total if name == 'complete' else None)
                        assert post_close['claim_accounting'] == {'declared_count': claim_total if claim_tail else None,
                            'recorded_count': max(0, len(claim_tail) - 1), 'complete': name == 'complete'}
                    else:
                        assert 'incomplete composition metadata differs' in result['detail']
                check_trace('post-close-invented-metadata', complete_post_close_rows, captured,
                    capture_request, {**incomplete_patch, 'duration_seconds': 0})
                assert 'native or host window differs' in control_results['post-close-invented-metadata']['detail']
                (retained_captures / 'trace-controls.json').write_bytes(canonical_bytes(control_results))
                # Q60: two retained chunks must not fill the next-range admission window.
                two_prefix_request = copy.deepcopy(paused_request)
                two_prefix_request['idempotency_key'] = 'l05-capture-two-prefix-suffix'
                packed = next(item for item in two_prefix_request['arguments']['composition']['recipe']['artifacts']
                              if item['path'] == 'packed')
                packed['segments'] = [{'path': artifact_one[0], 'offset': 0, 'length': 8388608},
                                      {'path': artifact_one[0], 'offset': 7, 'length': 4194325}]
                def stop_after_two_chunks(row):
                    if row['kind'] == 'OUTPUT_BOUNDARY' and row.get('output') == 'packed' and row['offset'] == 8388608:
                        raise CassetteError('SOURCE_UNAVAILABLE', 'packed', 'Q60: retained prefix before suffix',
                            'retryable', 'fixture observer stops after the second committed chunk')
                stopped = asyncio.run(capture_broker.compose_source(two_prefix_request,
                    CapacityCoordinator(capture_cartridge), _capture=stop_after_two_chunks))
                assert stopped['state'] == 'PAUSED'
                assert capture_broker.events(stopped['operation_id'])[-1]['payload']['error']['code'] == 'SOURCE_UNAVAILABLE'
                capture_broker.resume(stopped['operation_id'])
                two_prefix = asyncio.run(capture_broker._capture_composition_profile(two_prefix_request,
                    CapacityCoordinator(capture_cartridge), selection, capture_key='l05-two-prefix-recovered'))
                retain_capture(two_prefix)
                two_prefix_statistics = asyncio.run(capture_broker._composition_statistics(two_prefix_request,
                    CapacityCoordinator(capture_cartridge), capture_key='l05-two-prefix-recovered'))
                assert two_prefix_statistics['scope'] == 'RESUMED_OBSERVATIONS_ONLY; QUALIFICATION_NOT_RUN'
                assert two_prefix_statistics['retained_output']['verified_bytes'] == 8388608
                assert two_prefix_statistics['retained_output']['output_frontiers'] == {'empty': 0, 'packed': 8388608}
                assert two_prefix_statistics['phases']['PREPASS']['range_calls'] == 0
                assert two_prefix_statistics['phases']['COMPOSE_WRITE']['range_calls'] == 3
                assert two_prefix_statistics['phases']['COMPOSE_WRITE']['io_bytes']['output_data.write'] == 4194327
                (retained_captures / 'two-prefix-statistics.json').write_bytes(canonical_bytes(two_prefix_statistics))
                # Q42/Q43: an uncached source request is observed without claiming cold qualification.
                uncached_request = copy.deepcopy(paused_request)
                uncached_request['idempotency_key'] = 'l05-capture-uncached-source'
                uncached_capture = asyncio.run(capture_broker._capture_composition_profile(uncached_request,
                    CapacityCoordinator(capture_cartridge), selection, capture_key='l05-uncached-source',
                    uncached_source=True))
                retain_capture(uncached_capture)
                assert uncached_capture['context']['source_data_cache_policy'] == 'UNCACHED_REQUESTED'
                uncached_rows = [json.loads(line) for reference in uncached_capture['traces']
                    for line in (retained_captures / 'l05-uncached-source' / reference['name']).read_text().splitlines()]
                source_descriptors = [row for row in uncached_rows
                    if row['kind'] == 'EXTENT_BOUND' and row.get('role') == 'source_data']
                assert source_descriptors and all(row['uncached_request'] is True
                    and row['cache_flags_before'] != row['cache_flags_after'] for row in source_descriptors)
                added_flags = {row['cache_flags_after'] ^ row['cache_flags_before'] for row in source_descriptors}
                assert len(added_flags) == 1
                flag = next(iter(added_flags))
                assert flag > 0 and flag & (flag - 1) == 0
                assert all(row['cache_flags_after'] & row['cache_flags_before'] == row['cache_flags_before']
                    and row['cache_flags_after'] & flag for row in source_descriptors)
                assert all(not {'uncached_request', 'cache_flags_before', 'cache_flags_after'}.intersection(row)
                    for row in uncached_rows if row['kind'] == 'EXTENT_BOUND' and row.get('role') != 'source_data')
                uncached_statistics = asyncio.run(capture_broker._composition_statistics(uncached_request,
                    CapacityCoordinator(capture_cartridge), capture_key='l05-uncached-source'))
                assert uncached_statistics['scope'] == 'FRESH_OBSERVATIONS_ONLY; QUALIFICATION_NOT_RUN'
                assert uncached_statistics['cache_classification'] == 'UNCONTROLLED; NOT_COLD_PROOF'
                assert uncached_statistics['phases']['COMPOSE_WRITE']['io_bytes']['output_data.write'] == 4194327
                (retained_captures / 'uncached-statistics.json').write_bytes(canonical_bytes(uncached_statistics))
                # Q42/Q43: the existing qualifier binds the actual composition, not transfer-shaped labels.
                composition_profile = asyncio.run(capture_broker._composition_profile(uncached_request,
                    CapacityCoordinator(capture_cartridge), capture_key='l05-uncached-source'))
                assert composition_profile['status'] == 'PASS'
                assert set(composition_profile['source_phases']) == {'PREPASS', 'COMPOSE_WRITE'}
                assert composition_profile['cache']['source_bytes'] == 8388608
                assert composition_profile['cache']['classification'] == 'WITHIN_HOST_MEMORY'
                assert composition_profile['binding']['plan']['composition'] == uncached_capture['owner_binding']
                assert composition_profile['capture_digest'] == uncached_capture['capture_digest']
                assert composition_profile['source_phases']['PREPASS']['operation_bounds']['throughput_p05_lower_bound_bytes_per_second'] > 0
                assert asyncio.run(capture_broker._composition_profile(uncached_request,
                    CapacityCoordinator(capture_cartridge), capture_key='l05-uncached-source')) == composition_profile
                (retained_captures / 'composition-profile.json').write_bytes(canonical_bytes(composition_profile))
                profile_controls = {}
                for name in ('incomplete', 'resumed', 'path', 'proof', 'memory', 'uncached-request', 'unchanged-flags', 'malformed-inputs'):
                    changed = copy.deepcopy(uncached_statistics)
                    if name == 'incomplete':
                        changed['status'] = 'RECOMPUTED_INCOMPLETE_RAW'
                    elif name == 'resumed':
                        changed['execution_mode'] = 'RESUME'
                    elif name == 'path':
                        changed['profile_inputs']['context']['path']['volume_uuid'] = 'different-volume'
                    elif name == 'proof':
                        changed['profile_inputs']['composition']['source_proof_digest'] = 'blake3:' + '0' * 64
                    elif name == 'memory':
                        changed['profile_inputs']['host_memory_bytes'] = 1
                    elif name == 'malformed-inputs':
                        changed['profile_inputs'] = None
                    else:
                        descriptor = next(iter(changed['profile_inputs']['source_extents'].values()))
                        if name == 'uncached-request':
                            descriptor['uncached_request'] = False
                        else:
                            descriptor['cache_flags_after'] = descriptor['cache_flags_before']
                    with pytest.raises(CassetteError) as error:
                        storage_profile(composition_profile['binding'], [composition_profile['binding']['plan']['io_plan']],
                            [changed], expected_binding=composition_profile['binding'])
                    assert error.value.code == 'PROVENANCE_VIOLATION'
                    profile_controls[name] = error.value.payload()
                # Q42: controlled hardware/counter inputs exercise applicability, not new native measurements.
                for name in ('cache-crossing', 'missing-physical-io', 'insufficient-physical-io', 'insufficient-allocation'):
                    changed = copy.deepcopy(uncached_statistics)
                    bound = copy.deepcopy(composition_profile['binding'])
                    memory = bound['plan']['host_memory_bytes'] = changed['profile_inputs']['host_memory_bytes'] = 4194304
                    minimum = 8388608 - memory
                    changed['global_counter_deltas'].update(process_diskio_read_bytes=minimum, device_read_bytes=minimum)
                    if name == 'missing-physical-io':
                        changed['global_counter_deltas']['device_read_bytes'] = None
                    elif name == 'insufficient-physical-io':
                        changed['global_counter_deltas']['device_read_bytes'] -= 1
                    elif name == 'insufficient-allocation':
                        next(iter(changed['profile_inputs']['source_extents'].values()))['allocated_bytes'] = 8388607
                    if name == 'cache-crossing':
                        assessed = storage_profile(bound, [bound['plan']['io_plan']], [changed], expected_binding=bound)
                        assert assessed['cache']['classification'] == 'MIXED_CACHE_SOURCE_WINDOW_WITH_PHYSICAL_IO'
                        assert assessed['cache']['minimum_bytes_beyond_host_memory'] == minimum
                        profile_controls[name] = assessed['cache']
                    else:
                        with pytest.raises(CassetteError) as error:
                            storage_profile(bound, [bound['plan']['io_plan']], [changed], expected_binding=bound)
                        assert error.value.code == 'PROVENANCE_VIOLATION'
                        profile_controls[name] = error.value.payload()
                (retained_captures / 'composition-profile-controls.json').write_bytes(canonical_bytes({
                    'scope': 'QUALIFIER_INPUT_CONTRADICTIONS; CACHE_CROSSING_CASES_USE_CONTROLLED_HARDWARE_COUNTER_INPUTS_NOT_NATIVE_OBSERVATIONS',
                    'cases': profile_controls}))
                # Q42: an actual empty-only operation has latency and durable state, not byte throughput.
                empty_request = copy.deepcopy(uncached_request)
                empty_request['idempotency_key'] = 'l05-capture-empty-only'
                empty_request['arguments']['composition']['recipe']['artifacts'] = [{'path': 'empty', 'segments': [{'literal_hex': ''}]}]
                empty_capture = asyncio.run(capture_broker._capture_composition_profile(empty_request,
                    CapacityCoordinator(capture_cartridge), selection, capture_key='l05-empty-only'))
                retain_capture(empty_capture)
                empty_profile = asyncio.run(capture_broker._composition_profile(empty_request,
                    CapacityCoordinator(capture_cartridge), capture_key='l05-empty-only'))
                assert empty_profile['status'] == 'PASS' and empty_profile['cache']['source_bytes'] == 0
                assert empty_profile['source_phases']['PREPASS']['observations']['range_calls'] == 1
                for values in empty_profile['source_phases'].values():
                    assert values['observations']['range_bytes_per_active_second']['samples'] == 0
                    assert values['operation_bounds']['throughput_p05_lower_bound_bytes_per_second'] is None
                assert empty_profile['source_phases']['COMPOSE_WRITE']['io_calls'] > 0
                (retained_captures / 'empty-composition-profile.json').write_bytes(canonical_bytes(empty_profile))
                # Q60: cancel against the actual MEASURING head before any owner exists.
                early_request = copy.deepcopy(capture_request)
                early_request['idempotency_key'] = 'l05-capture-before-owner'
                early_id = capture_broker.issue(early_request)['operation_id']
                async def cancel_before_owner():
                    task = asyncio.create_task(capture_broker._capture_composition_profile(early_request,
                        CapacityCoordinator(capture_cartridge), selection, capture_key='l05-before-owner-interrupted'))
                    try:
                        for _ in range(3000):
                            measuring = campaign_head(capture_cartridge, 'l05-before-owner-interrupted')
                            if measuring is not None:
                                assert measuring['value']['status'] == 'MEASURING'
                                assert campaign_head(capture_cartridge, 'source-compose-' + early_id[3:]) is None
                                task.cancel()
                                with pytest.raises(asyncio.CancelledError):
                                    await task
                                return
                            assert not task.done(), task.result()
                            await asyncio.sleep(.001)
                        raise AssertionError('early capture did not publish its measuring head')
                    finally:
                        if not task.done():
                            task.cancel()
                            await asyncio.gather(task, return_exceptions=True)
                asyncio.run(cancel_before_owner())
                early = campaign_head(capture_cartridge, 'l05-before-owner-interrupted')
                assert early['value']['status'] == 'INCOMPLETE'
                retain_capture({**early['value'], 'capture_key': early['key'], 'capture_digest': early['digest']})
                early_statistics = asyncio.run(capture_broker._composition_statistics(early_request,
                    CapacityCoordinator(capture_cartridge), capture_key='l05-before-owner-interrupted'))
                assert early_statistics['status'] == 'RECOMPUTED_INCOMPLETE_RAW'
                assert early_statistics['ownership_digest'] is None
                assert early_statistics['completion_record_observed'] is False
                assert early_statistics['frontiers']['durable_output'] == {}
                assert set(early_statistics['global_counter_deltas'].values()) == {None}
                assert early_statistics['issued_claim_count'] is None
                (retained_captures / 'early-statistics.json').write_bytes(canonical_bytes(early_statistics))
                assert capture_broker.cancel(early_id)['state'] == 'CANCELLED'
                assert (capture_area / 'operations' / (acquired_id + '.json')).read_bytes() == original_capture_input
            finally:
                capture_broker.close()
                subprocess.run(['/usr/bin/hdiutil', 'detach', str(mount), '-quiet'], check=True, capture_output=True)
        finally:
            broker.close()
