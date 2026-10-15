# test_l05_entry.py — L05 product CLI source and drive entry proof (Q5/Q9/Q44/Q49/Q52); depends on broker.py, cli.py, tests/test_l05_drive.py.
"""Exercise the installed-module launch against an external HTTP boundary fixture."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import asyncio
import hashlib
import json
from pathlib import Path
import plistlib
import stat
import subprocess
import sys
import threading
import time
from urllib.parse import parse_qs, urlparse

import cli
from broker import CanonicalBroker
from test_l05_drive import _attached_apfs_image


def test_q9_q52_cli_catalogue_uses_broker_and_bounded_provider_pages(tmp_path):
    """Q52 acceptance: product CLI discovery uses the source adapter and canonical errors.

    This proves the catalogue portion of the matrix source-row assertion
    product_cli_connection_catalogue_selection_and_go_reach_verified_external_download.
    It does not prove the later selection, access, transfer or live-provider boundaries.
    """
    requests = []

    class Provider(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)
            requests.append((parsed.path, query))
            term = query.get('search', [''])[0]
            if term == 'denied':
                self.send_response(401)
                self.send_header('Content-Length', '0')
                self.end_headers()
                return
            payload = [{'id': 'fixture/' + ('second' if 'cursor' in query else 'first'),
                        'sha': 'a' * 40, 'private': False, 'gated': False}]
            if term == 'malformed':
                payload = [{'id': '../invalid'}]
            body = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            if 'cursor' not in query:
                origin = ('https://unrelated.invalid' if term == 'wrong-origin'
                          else f'http://127.0.0.1:{self.server.server_port}')
                self.send_header('Link', f'<{origin}/api/models?cursor=next-page&limit=1>; rel="next"')
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer(('127.0.0.1', 0), Provider)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        def launch(query, *extra):
            result = subprocess.run(
                [sys.executable, '-B', str(Path(cli.__file__).resolve()), '--state', str(tmp_path / 'state'),
                 'models', '--source', 'huggingface', '--endpoint',
                 f'http://127.0.0.1:{server.server_port}', '--query', query, '--limit', '1', *extra],
                cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=30)
            assert result.stdout, result.stderr
            return result, json.loads(result.stdout)

        result, first = launch('dense')
        assert result.returncode == 0, result.stderr
        assert first['state'] == 'SUCCEEDED'
        assert first['result']['candidates'][0]['locator'] == 'fixture/first'
        assert first['result']['candidates'][0]['downloadability'] == 'NOT_VERIFIED'
        assert first['result']['next_cursor'] == 'next-page'
        assert requests[-1][0] == '/api/models'
        assert requests[-1][1]['limit'] == ['1']
        result, second = launch('dense', '--cursor', first['result']['next_cursor'])
        assert result.returncode == 0
        assert second['result']['candidates'][0]['locator'] == 'fixture/second'
        assert second['result']['next_cursor'] is None
        assert second['operation_id'] != first['operation_id']
        for query, code in [('denied', 'AUTH_REQUIRED'), ('malformed', 'SOURCE_UNAVAILABLE'),
                            ('wrong-origin', 'SOURCE_UNAVAILABLE')]:
            result, failure = launch(query)
            assert result.returncode == 1
            assert failure['state'] == 'FAILED'
            assert failure['error']['code'] == code
        result, failure = launch('dense', '--endpoint', 'http://user:fixture-password@127.0.0.1')
        assert result.returncode == 1 and failure['error']['code'] == 'INVALID_REQUEST'
        assert 'fixture-password' not in result.stdout + result.stderr
        assert all(b'fixture-password' not in path.read_bytes()
                   for path in (tmp_path / 'state').rglob('*') if path.is_file())
        assert not (tmp_path / 'Cassette').exists()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_q49_cli_drive_selection_preserves_inventory_and_scoped_intent(tmp_path):
    """Q49 acceptance: CLI selection binds its volume and inventory without creating the destination."""
    image, mount = _attached_apfs_image(tmp_path)
    try:
        (mount / 'user.txt').write_bytes(b'keep this user file')
        def launch(*arguments, expected_code=0):
            result = subprocess.run([sys.executable, '-B', '-m', 'cli', '--state',
                str(tmp_path / 'state'), *arguments], cwd=Path(__file__).resolve().parents[1],
                capture_output=True, text=True, timeout=30)
            assert result.returncode == expected_code, result.stderr + result.stdout
            return json.loads(result.stdout)
        drives = launch('drives')
        volume = next(item for item in drives['result']['volumes'] if item['mount_path'] == str(mount))
        selection = launch('select-drive', '--volume', volume['volume_uuid'], '--folder', 'Cassette',
                           '--key', 'selected-drive')
        assert selection['result']['selection']['volume']['volume_uuid'] == volume['volume_uuid']
        assert selection['result']['protected_inventory']['user.txt'] == {'type': 'file', 'logical_bytes': 19}
        assert selection['result']['folder'] == 'Cassette'
        assert not (mount / 'Cassette').exists()
        assert launch('select-drive', '--volume', volume['volume_uuid'], '--folder', 'Cassette',
                      '--key', 'selected-drive') == selection
    finally:
        subprocess.run(['/usr/bin/hdiutil', 'detach', str(mount), '-quiet'], check=True, capture_output=True)
        image.unlink()


def test_q5_q9_cli_selection_pins_source_without_downloading_weights(tmp_path):
    """Q5/Q6/Q9/Q42/Q44/Q49/Q51: selection defers payload; qualified Go completes and replays.

    The CLI crosses the provider boundary, survives a new process and retains its selection
    after a mutable tag changes. Payload follows reconnect proof and operation-bound measurement.
    """
    weights = b'fixture weights must remain at the provider during selection' * 72000
    license_bytes = b'---\nlicense: apache-2.0\n---\nFixture model card.\n'
    requests = []
    revision = ['a' * 40]
    interrupt = [True]

    class Provider(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_HEAD(self):
            requests.append(('HEAD', self.path))
            self.send_response(200)
            self.send_header('Content-Length', str(len(weights)))
            self.send_header('ETag', '"' + hashlib.sha256(weights).hexdigest() + '"')
            self.end_headers()

        def do_GET(self):
            requests.append(('GET', self.path))
            route = urlparse(self.path).path
            headers = {}
            if route == '/api/models':
                payload = json.dumps([{'id': 'fixture/model', 'sha': revision[0],
                                       'private': False, 'gated': False}]).encode()
            elif route.startswith('/api/models/fixture/model/revision/'):
                requested = route.rsplit('/', 1)[1]
                resolved = revision[0] if requested == 'main' else requested
                payload = json.dumps({'id': 'fixture/model', 'sha': resolved,
                    'private': False, 'gated': False, 'cardData': {'license': 'apache-2.0'}, 'siblings': [
                        {'rfilename': 'model.safetensors', 'size': len(weights),
                         'lfs': {'size': len(weights), 'sha256': hashlib.sha256(weights).hexdigest()}},
                        {'rfilename': 'README.md', 'size': len(license_bytes),
                         'blobId': hashlib.sha1(f'blob {len(license_bytes)}\0'.encode() + license_bytes).hexdigest()}
                    ]}).encode()
            elif route.endswith('/README.md'):
                payload = license_bytes
                headers['ETag'] = '"' + hashlib.sha1(f'blob {len(payload)}\0'.encode() + payload).hexdigest() + '"'
            elif route.endswith('/model.safetensors'):
                start, end = map(int, self.headers['Range'].removeprefix('bytes=').split('-'))
                payload = weights[start:end+1]
                headers['ETag'] = '"' + hashlib.sha256(weights).hexdigest() + '"'
                headers['Content-Range'] = f'bytes {start}-{end}/{len(weights)}'
            else:
                self.send_response(404)
                self.send_header('Content-Length', '0')
                self.end_headers()
                return
            self.send_response(206 if 'Range' in self.headers else 200)
            if 'Range' in self.headers and route.endswith('/README.md'):
                start, end = map(int, self.headers['Range'].removeprefix('bytes=').split('-'))
                headers['Content-Range'] = f'bytes {start}-{end}/{len(payload)}'
                payload = payload[start:end+1]
            self.send_header('Content-Length', str(len(payload)))
            for name, value in headers.items():
                self.send_header(name, value)
            self.end_headers()
            if route.endswith('/model.safetensors') and start == 0 and interrupt[0]:
                interrupt[0] = False
                self.wfile.write(payload[:17])
                self.close_connection = True
            else:
                self.wfile.write(payload)

    server = ThreadingHTTPServer(('127.0.0.1', 0), Provider)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        def launch(*arguments, expected_code=0, expected_message=None):
            result = subprocess.run([sys.executable, '-B', '-m', 'cli', '--state',
                str(tmp_path / 'state'), *arguments], cwd=Path(__file__).resolve().parents[1],
                capture_output=True, text=True, timeout=30)
            assert result.returncode == expected_code, result.stderr + result.stdout
            if expected_message is not None:
                assert expected_message in result.stderr
            return json.loads(result.stdout)

        connection = launch('connect', '--source', 'huggingface', '--endpoint',
                            f'http://127.0.0.1:{server.server_port}', '--public')
        assert connection['state'] == 'SUCCEEDED'
        assert connection['result']['credential_ref'] is None
        selected = launch('select-model', '--connection', connection['operation_id'],
                          '--model', 'fixture/model', '--revision', 'main', '--key', 'selected-model')
        assert selected['state'] == 'SUCCEEDED'
        assert selected['result']['source_lock']['immutable_revision'] == 'git-sha1:' + 'a' * 40
        assert selected['result']['source_lock']['identity'] is None
        revision[0] = 'b' * 40
        repeated = launch('select-model', '--connection', connection['operation_id'],
                          '--model', 'fixture/model', '--revision', 'main', '--key', 'selected-model')
        assert repeated == selected
        inspected = launch('status', selected['operation_id'])
        assert inspected == selected
        image, mount = _attached_apfs_image(tmp_path)
        watcher = None
        attached = True
        try:
            parent = mount / 'drewwiberg-lacie'
            parent.mkdir()
            (parent / 'user.txt').write_bytes(b'protected')
            root_mode = stat.S_IMODE(mount.stat().st_mode)
            mount.chmod(0o555)
            drives = launch('drives')
            volume = next(item for item in drives['result']['volumes'] if item['mount_path'] == str(mount))
            drive = launch('select-drive', '--volume', volume['volume_uuid'], '--folder', 'drewwiberg-lacie/Cassette')
            subprocess.run(['/usr/bin/hdiutil', 'detach', str(mount), '-quiet'], check=True, capture_output=True)
            attached = False
            disconnected = launch('go', '--model-selection', selected['operation_id'], '--drive-selection',
                                  drive['operation_id'], '--key', 'go-fixture', expected_code=2,
                                  expected_message='Go paused: CARTRIDGE_DISCONNECTED:')
            assert disconnected['state'] == 'PAUSED'
            assert launch('qualify', '--model-selection', selected['operation_id'], '--drive-selection',
                          drive['operation_id'], '--key', 'go-fixture', expected_code=2,
                          expected_message='Retry qualify with the same key.') == disconnected
            assert launch('go', '--model-selection', selected['operation_id'], '--drive-selection',
                          drive['operation_id'], '--key', 'go-fixture', expected_code=2) == disconnected
            record_path = tmp_path / 'state/operations' / (disconnected['operation_id'] + '.json')
            record = json.loads(record_path.read_bytes())['record']
            assert record['events'][-1]['payload']['error']['code'] == 'CARTRIDGE_DISCONNECTED'
            assert record['events'][-1]['payload']['error']['retryability'] == 'retryable'
            assert all(event['type'] not in {'failed', 'completed', 'cancelled'} for event in record['events'])
            remounted = subprocess.run(['/usr/bin/hdiutil', 'attach', '-nobrowse', '-plist', str(image)],
                                       check=True, capture_output=True)
            mount = next(Path(item['mount-point']) for item in plistlib.loads(remounted.stdout)['system-entities'] if 'mount-point' in item)
            parent = mount / 'drewwiberg-lacie'
            attached = True
            control = CanonicalBroker(tmp_path / 'state/operations')
            control.resume(disconnected['operation_id'])
            control.request_hold(disconnected['operation_id'], 'CARTRIDGE-DURABILITY')
            control.close()
            ready = launch('go', '--model-selection', selected['operation_id'], '--drive-selection',
                           drive['operation_id'], '--key', 'go-fixture', expected_code=2,
                           expected_message='Go paused at the physical drive qualification boundary.')
            assert ready['state'] == 'PAUSED'
            assert ready['operation_id'] == disconnected['operation_id']
            assert (parent / 'Cassette/cartridge.json').is_file()
            assert (parent / 'user.txt').read_bytes() == b'protected'
            held_record = record_path.read_bytes()
            assert launch('go', '--model-selection', selected['operation_id'], '--drive-selection',
                          drive['operation_id'], '--key', 'go-fixture', expected_code=2) == ready
            assert record_path.read_bytes() == held_record

            weights += b'changed source'
            failed = launch('go', '--model-selection', selected['operation_id'], '--drive-selection',
                            drive['operation_id'], '--key', 'go-terminal', expected_code=1)
            assert failed['state'] == 'FAILED'
            assert failed['error']['code'] == 'SOURCE_REVISION_CHANGED'
            assert launch('go', '--model-selection', selected['operation_id'], '--drive-selection',
                          drive['operation_id'], '--key', 'go-terminal', expected_code=1) == failed
            weights = weights.removesuffix(b'changed source')
            mount.chmod(root_mode)
            subprocess.run(['/usr/bin/hdiutil', 'detach', str(mount), '-quiet'], check=True, capture_output=True)
            attached = False
            watcher = subprocess.Popen([sys.executable, '-B', '-m', 'cli', '--state', str(tmp_path / 'state'),
                'watch-remount', ready['operation_id']], cwd=Path(__file__).resolve().parents[1],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            record_path = tmp_path / 'state/operations' / (ready['operation_id'] + '.json')
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                record = json.loads(record_path.read_bytes())['record']
                if any('drive_disconnected' in event['payload'] for event in record['events']):
                    break
                assert watcher.poll() is None, watcher.communicate()
                time.sleep(.02)
            else:
                raise AssertionError('CLI did not record the detached volume')
            remounted = subprocess.run(['/usr/bin/hdiutil', 'attach', '-nobrowse', '-plist', str(image)],
                                       check=True, capture_output=True)
            mount = next(Path(item['mount-point']) for item in plistlib.loads(remounted.stdout)['system-entities'] if 'mount-point' in item)
            attached = True
            output, error = watcher.communicate(timeout=30)
            assert watcher.returncode == 0, error + output
            recovered = json.loads(output)
            assert recovered['result']['selection']['volume']['volume_uuid'] == volume['volume_uuid']
            assert recovered['result']['source_qualification'] == 'NOT_RUN'
            assert (mount / 'drewwiberg-lacie/user.txt').read_bytes() == b'protected'
            reported = launch('go', '--model-selection', selected['operation_id'], '--drive-selection',
                              drive['operation_id'], '--key', 'go-reported', expected_code=2)
            subprocess.run(['/usr/bin/hdiutil', 'detach', str(mount), '-quiet'], check=True, capture_output=True)
            attached = False
            remounted = subprocess.run(['/usr/bin/hdiutil', 'attach', '-nobrowse', '-plist', str(image)],
                                       check=True, capture_output=True)
            mount = next(Path(item['mount-point']) for item in plistlib.loads(remounted.stdout)['system-entities'] if 'mount-point' in item)
            attached = True
            reported_path = tmp_path / 'state/operations' / (reported['operation_id'] + '.json')
            reported_record = json.loads(reported_path.read_bytes())['record']
            preparation = next(event['payload']['drive_prepared'] for event in reported_record['events']
                               if 'drive_prepared' in event['payload'])
            probe = preparation['binding']['probe']
            probe_path = mount / 'drewwiberg-lacie/Cassette/captures' / probe['attempt'] / probe['name']
            saved_probe = probe_path.read_bytes()
            probe_path.write_bytes(b'x' * len(saved_probe))
            rejected = launch('watch-remount', reported['operation_id'], '--reconnected',
                              '--key', 'reported-remount-corrupt', expected_code=1)
            assert rejected['error']['code'] == 'ROOT_INVALID'
            reported_record = json.loads(reported_path.read_bytes())['record']
            assert reported_record['state'] == 'PAUSED'
            assert not any('drive_remounted' in event['payload'] for event in reported_record['events'])
            probe_path.write_bytes(saved_probe)
            user_path = mount / 'drewwiberg-lacie/user.txt'
            user_path.write_bytes(b'changed outside the cartridge')
            confirmed = launch('watch-remount', reported['operation_id'], '--reconnected', '--key', 'reported-remount')
            assert confirmed['result']['go_operation_id'] == reported['operation_id']
            assert launch('watch-remount', reported['operation_id'], '--reconnected', '--key', 'reported-remount') == confirmed
            reported_record = json.loads((tmp_path / 'state/operations' / (reported['operation_id'] + '.json')).read_bytes())['record']
            assert any(event['payload'].get('physical_reconnect_reported') == 'OPERATOR'
                       for event in reported_record['events'])
            assert not any('drive_disconnected' in event['payload'] for event in reported_record['events'])
            assert any('drive_remounted' in event['payload'] for event in reported_record['events'])
            payload_count = sum(method == 'GET' and path.endswith('/model.safetensors') for method, path in requests)
            refused = launch('go', '--model-selection', selected['operation_id'], '--drive-selection',
                             drive['operation_id'], '--key', 'go-reported', expected_code=1)
            assert refused['error']['code'] == 'PROVENANCE_VIOLATION'
            assert sum(method == 'GET' and path.endswith('/model.safetensors') for method, path in requests) == payload_count
            user_path.write_bytes(b'protected')
            payload_before_qualification = sum(method == 'GET' and path.endswith('/model.safetensors')
                                               for method, path in requests)
            qualified = launch('qualify', '--model-selection', selected['operation_id'], '--drive-selection',
                               drive['operation_id'], '--key', 'go-fixture', expected_code=2,
                               expected_message='Drive check passed. Download remains paused.')
            assert qualified['state'] == 'PAUSED'
            assert qualified['operation_id'] == ready['operation_id']
            assert sum(method == 'GET' and path.endswith('/model.safetensors')
                       for method, path in requests) == payload_before_qualification
            qualified_record = json.loads(record_path.read_bytes())['record']
            assert qualified_record['phase'] == 'EMPTY'
            assert qualified_record['events'][-2]['payload']['source_qualification']['status'] == 'PASS'
            qualified_profiles = {p.name: p.read_bytes() for p in
                                  (mount / 'drewwiberg-lacie/Cassette/campaign/objects').iterdir()}
            interrupted = launch('go', '--model-selection', selected['operation_id'], '--drive-selection',
                                 drive['operation_id'], '--key', 'go-fixture', expected_code=2,
                                 expected_message='Go paused: SOURCE_UNAVAILABLE:')
            assert interrupted['operation_id'] == ready['operation_id']
            interrupted_record = json.loads(record_path.read_bytes())['record']
            payload_after_interrupt = sum(method == 'GET' and path.endswith('/model.safetensors')
                                          for method, path in requests)
            assert launch('qualify', '--model-selection', selected['operation_id'], '--drive-selection',
                          drive['operation_id'], '--key', 'go-fixture', expected_code=2,
                          expected_message='Drive check passed. Download remains paused.')['operation_id'] == ready['operation_id']
            prepared_record = json.loads(record_path.read_bytes())['record']
            assert prepared_record['phase'] == interrupted_record['phase'] == 'ACQUIRING'
            assert prepared_record['checkpoint'] == interrupted_record['checkpoint']
            assert sum(method == 'GET' and path.endswith('/model.safetensors')
                       for method, path in requests) == payload_after_interrupt
            completed = launch('go', '--model-selection', selected['operation_id'], '--drive-selection',
                               drive['operation_id'], '--key', 'go-fixture')
            assert completed['state'] == 'SUCCEEDED'
            assert completed['operation_id'] == ready['operation_id']
            assert completed['result']['verified_bytes'] == len(weights) + len(license_bytes)
            assert all((mount / 'drewwiberg-lacie/Cassette/campaign/objects' / name).read_bytes() == content
                       for name, content in qualified_profiles.items())
            payload_requests = len([item for item in requests if item[0] == 'GET' and 'model.safetensors' in item[1]])
            assert payload_requests >= 3
            assert launch('go', '--model-selection', selected['operation_id'], '--drive-selection',
                          drive['operation_id'], '--key', 'go-fixture') == completed
            assert len([item for item in requests if item[0] == 'GET' and 'model.safetensors' in item[1]]) == payload_requests
            record = json.loads(record_path.read_bytes())['record']
            assert any(event['payload'].get('source_qualification', {}).get('status') == 'PASS' for event in record['events'])
            # Q42/Q53: immutable measurement controls grow once per atom, not once per history prefix.
            profile_records = [json.loads(path.read_bytes()) for path in
                               (mount / 'drewwiberg-lacie/Cassette/campaign/objects').iterdir()]
            assert all(len(item['value'].get('observations', [])) <= 1 for item in profile_records)
            profiles = [item for item in profile_records if item['key'].startswith('download-profile-')]
            plans = [item for item in profiles if 'pattern_count' in item['value']]
            atoms = [item for item in profiles if 'measurement' in item['value']]
            assert len(plans) == 1
            assert len(atoms) == plans[0]['value']['pattern_count']
            assert all(item['previous'] is None for item in profiles)
            assert all('binding' not in item['value'] and 'patterns' not in item['value'] for item in atoms)
            assert not list((mount / 'drewwiberg-lacie/Cassette').rglob('profile.bin'))
            seals = [item for item in profiles if 'atoms_digest' in item['value']]
            assert len(seals) == 1 and seals[0]['value']['atom_count'] == len(atoms)
            qualification = next(event['payload']['source_qualification'] for event in record['events']
                                 if event['payload'].get('source_qualification', {}).get('status') == 'PASS')
            assert qualification['profile_digest'] != atoms[0]['value']['profile_digest']
            assert any(event['payload'].get('received_bytes') == len(weights) for event in record['events'])
            fresh_drive = launch('select-drive', '--volume', volume['volume_uuid'],
                                 '--folder', 'drewwiberg-lacie/Cassette', '--cartridge-uuid',
                                 drive['result']['cartridge_uuid'], '--key', 'reuse-drive')
            payload_before_reuse = sum(method == 'GET' and path.endswith('/model.safetensors')
                                       for method, path in requests)
            prepared_reuse = launch('qualify', '--model-selection', selected['operation_id'], '--drive-selection',
                                    fresh_drive['operation_id'], '--key', 'go-reuse', expected_code=2,
                                    expected_message='Drive check passed. Download remains paused.')
            assert sum(method == 'GET' and path.endswith('/model.safetensors')
                       for method, path in requests) == payload_before_reuse
            reused = launch('go', '--model-selection', selected['operation_id'], '--drive-selection',
                            fresh_drive['operation_id'], '--key', 'go-reuse')
            assert reused['state'] == 'SUCCEEDED'
            assert reused['operation_id'] == prepared_reuse['operation_id']
            reused_record = json.loads((tmp_path / 'state/operations' / (reused['operation_id'] + '.json')).read_bytes())['record']
            reused_proof = next(event['payload']['drive_revalidated'] for event in reused_record['events']
                                if 'drive_revalidated' in event['payload'])
            assert reused_proof['proof_operation_id'] == ready['operation_id']
            assert not any('physical_reconnect_reported' in event['payload'] or
                           'drive_remounted' in event['payload'] for event in reused_record['events'])
            held_request = {'protocol_version': '1', 'operation': 'acquire',
                'idempotency_key': 'go-reuse-requested-hold', 'target': fresh_drive['operation_id'],
                'arguments': {'acquisition': {'model_selection_id': selected['operation_id'],
                                             'drive_selection_id': fresh_drive['operation_id']}}}
            control = CanonicalBroker(tmp_path / 'state/operations')
            held_operation = control.issue({**held_request, 'arguments': {
                **held_request['arguments'], 'source': selected['result']['descriptor']}})
            control.request_hold(held_operation['operation_id'], 'CARTRIDGE-DURABILITY')
            control.close()
            control = CanonicalBroker(tmp_path / 'state/operations')
            try:
                assert asyncio.run(control.start_download(held_request))['state'] == 'SUCCEEDED'
                held_events = control.events(held_operation['operation_id'])
                assert [event['payload']['hold'] for event in held_events if 'hold' in event['payload']] == [
                    'REQUESTED', 'ACKNOWLEDGED', 'RELEASED']
            finally:
                control.close()
            paused_request = {'protocol_version': '1', 'operation': 'acquire',
                'idempotency_key': 'go-reuse-paused', 'target': fresh_drive['operation_id'],
                'arguments': {'acquisition': {'model_selection_id': selected['operation_id'],
                                             'drive_selection_id': fresh_drive['operation_id']}}}
            control = CanonicalBroker(tmp_path / 'state/operations')
            paused_operation = control.issue({**paused_request, 'arguments': {
                **paused_request['arguments'], 'source': selected['result']['descriptor']}})
            control._append(control._load(paused_operation['operation_id']), 'output_delta',
                            {'drive_revalidated': reused_proof})
            assert control.pause(paused_operation['operation_id'])['state'] == 'PAUSED'
            control.close()
            control = CanonicalBroker(tmp_path / 'state/operations')
            try:
                assert asyncio.run(control.start_download(paused_request))['state'] == 'SUCCEEDED'
            finally:
                control.close()
            prior_preparation = next(event['payload']['drive_prepared'] for event in record['events']
                                     if 'drive_prepared' in event['payload'])
            prior_probe = prior_preparation['binding']['probe']
            prior_probe_path = mount / 'drewwiberg-lacie/Cassette/captures' / prior_probe['attempt'] / prior_probe['name']
            prior_probe_bytes = prior_probe_path.read_bytes()
            prior_probe_path.write_bytes(b'x' * len(prior_probe_bytes))
            payload_requests = sum(method == 'GET' and path.endswith('/model.safetensors') for method, path in requests)
            corrupt_reuse = launch('go', '--model-selection', selected['operation_id'], '--drive-selection',
                                   fresh_drive['operation_id'], '--key', 'go-reuse-corrupt', expected_code=1)
            assert corrupt_reuse['error']['code'] == 'ROOT_INVALID'
            assert sum(method == 'GET' and path.endswith('/model.safetensors') for method, path in requests) == payload_requests
            prior_probe_path.write_bytes(prior_probe_bytes)
        finally:
            if watcher is not None and watcher.poll() is None:
                watcher.terminate()
                watcher.communicate(timeout=10)
            if attached:
                mount.chmod(root_mode)
                subprocess.run(['/usr/bin/hdiutil', 'detach', str(mount), '-quiet'], check=True, capture_output=True)
            image.unlink()
        assert all(weights not in path.read_bytes() for path in (tmp_path / 'state').rglob('*') if path.is_file())
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
