# test_l05_entry.py — L05 product CLI source and drive entry proof (Q5/Q9/Q44/Q49/Q52); depends on broker.py, cli.py, errors.py, store.py, tests/test_l05_drive.py.
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
from errors import CassetteError
from store import CapacityCoordinator, canonical_bytes, compare_inventory, digest_bytes, source_profile_trace, write_campaign_artifact
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
    """Q49: exact OS-owned top-level exclusions preserve nested and ordinary user inventory guards."""
    image, mount = _attached_apfs_image(tmp_path)
    locked = []
    try:
        (mount / 'user.txt').write_bytes(b'keep this user file')
        user = mount / 'UserFolder'
        user.mkdir()
        (user / 'a.bin').write_bytes(bytes(1000))
        (user / '.TemporaryItems').mkdir()
        (user / '.TemporaryItems' / 'x').write_bytes(bytes(10))
        for name, size in (('.DocumentRevisions-V100', 5), ('.TemporaryItems', 7)):
            path = mount / name
            path.mkdir()
            (path / 'owned-fixture').write_bytes(bytes(size))
            path.chmod(0)
            locked.append(path)
        def launch(*arguments, expected_code=0):
            result = subprocess.run([sys.executable, '-B', '-m', 'cli', '--state',
                str(tmp_path / 'state'), *arguments], cwd=Path(__file__).resolve().parents[1],
                capture_output=True, text=True, timeout=30)
            assert result.returncode == expected_code, result.stderr + result.stdout
            return json.loads(result.stdout)
        drives = launch('drives')
        volume = next(item for item in drives['result']['volumes'] if item['mount_path'] == str(mount))
        def select(key, expected_code=0):
            return launch('select-drive', '--volume', volume['volume_uuid'], '--folder', 'Cassette',
                          '--key', key, expected_code=expected_code)
        selection = select('selected-drive')
        assert selection['state'] == 'SUCCEEDED'
        assert selection['result']['selection']['volume']['volume_uuid'] == volume['volume_uuid']
        before = selection['result']['protected_inventory']
        assert before == {'user.txt': {'type': 'file', 'logical_bytes': 19},
                          'UserFolder': {'type': 'directory', 'logical_bytes': 1010}}
        assert selection['result']['folder'] == 'Cassette'
        assert not (mount / 'Cassette').exists()
        assert select('selected-drive') == selection
        for path in (mount / 'LockedUser', user / '.DocumentRevisions-V100'):
            path.mkdir()
            path.chmod(0)
            locked.append(path)
            failure = select('denied-' + path.parent.name + '-' + path.name, expected_code=1)
            assert failure['state'] == 'FAILED' and failure.get('result') is None
            assert failure['error']['code'] == 'CAPABILITY_MISMATCH'
            assert 'PermissionError' in failure['error']['detail']
            path.chmod(0o755)
            path.rmdir()
            locked.remove(path)
        (user / 'a.bin').write_bytes(bytes(1001))
        after = select('changed-user')['result']['protected_inventory']
        assert after['UserFolder']['logical_bytes'] == 1011
        try:
            compare_inventory(before, after)
        except CassetteError as error:
            assert error.code == 'PROVENANCE_VIOLATION'
        else:
            raise AssertionError('protected byte change was not detected')
        temporary = mount / '.TemporaryItems'
        temporary.chmod(0o755)
        (temporary / 'new-owned-fixture').write_bytes(bytes(100))
        temporary.chmod(0)
        assert select('changed-excluded')['result']['protected_inventory'] == after
    finally:
        for path in locked:
            path.chmod(0o755)
        subprocess.run(['/usr/bin/hdiutil', 'detach', str(mount), '-quiet'], check=True, capture_output=True)
        image.unlink()


def test_q5_q9_cli_selection_pins_source_without_downloading_weights(tmp_path):
    """Q5/Q6/Q9/Q42/Q43/Q44/Q49/Q50/Q51/Q60: exact header plans precede complete acquisition.

    The CLI crosses the provider boundary, survives a new process and retains its selection
    after a mutable tag changes. Payload follows reconnect proof and operation-bound measurement.
    """
    tensor_bytes = b'fixture weights must remain at the provider during selection' * 72000
    header_bytes = json.dumps({'weight': {'dtype': 'U8', 'shape': [len(tensor_bytes)],
                              'data_offsets': [0, len(tensor_bytes)]}}, separators=(',', ':')).encode()
    weights = len(header_bytes).to_bytes(8, 'little') + header_bytes + tensor_bytes
    tiny_header = json.dumps({'weight': {'dtype': 'U8', 'shape': [1], 'data_offsets': [0, 1]}}).encode()
    dataset_files = {'empty.json': b'', 'inputs.jsonl': b'{"text":"selected Git dataset"}\n',
                     'samples.parquet': b'PAR1' + b'opaque dataset transport fixture' * 700,
                     'tiny.safetensors': len(tiny_header).to_bytes(8, 'little') + tiny_header + b'x',
                     'unused.jsonl': b'not selected; do not read'}
    license_bytes = b'---\nlicense: apache-2.0\n---\nFixture model card.\n'
    requests = []
    header_ranges = []
    revision = ['a' * 40]
    interrupt = [True]

    class Provider(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_HEAD(self):
            requests.append(('HEAD', self.path))
            name = urlparse(self.path).path.rsplit('/', 1)[-1]
            payload = dataset_files[name] if '/datasets/' in self.path else weights
            digest = (hashlib.sha1(f'blob {len(payload)}\0'.encode() + payload).hexdigest()
                      if '/datasets/' in self.path and not name.endswith('.parquet') else hashlib.sha256(payload).hexdigest())
            self.send_response(200)
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('ETag', '"' + digest + '"')
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
            elif route.startswith('/api/datasets/fixture/data/revision/'):
                siblings = [{'rfilename': name, 'size': len(content),
                             **({'lfs': {'size': len(content), 'sha256': hashlib.sha256(content).hexdigest()}}
                                if name.endswith('.parquet') else
                                {'blobId': hashlib.sha1(f'blob {len(content)}\0'.encode() + content).hexdigest()})}
                            for name, content in {**dataset_files, 'README.md': license_bytes}.items()]
                payload = json.dumps({'id': 'fixture/data', 'sha': 'c' * 40, 'private': False,
                    'gated': False, 'cardData': {'license': 'apache-2.0'}, 'siblings': siblings}).encode()
            elif route.endswith('/README.md'):
                payload = license_bytes
                headers['ETag'] = '"' + hashlib.sha1(f'blob {len(payload)}\0'.encode() + payload).hexdigest() + '"'
            elif route.endswith('/model.safetensors'):
                start, end = map(int, self.headers['Range'].removeprefix('bytes=').split('-'))
                header_ranges.append((start, end))
                payload = weights[start:end+1]
                headers['ETag'] = '"' + hashlib.sha256(weights).hexdigest() + '"'
                headers['Content-Range'] = f'bytes {start}-{end}/{len(weights)}'
            elif route.startswith('/datasets/fixture/data/resolve/'):
                name = route.rsplit('/', 1)[-1]
                whole = dataset_files[name]
                if name == 'inputs.jsonl':
                    time.sleep(.3)
                start, end = map(int, self.headers['Range'].removeprefix('bytes=').split('-'))
                payload = whole[start:end+1]
                digest = (hashlib.sha1(f'blob {len(whole)}\0'.encode() + whole).hexdigest()
                          if not name.endswith('.parquet') else hashlib.sha256(whole).hexdigest())
                headers['ETag'] = '"' + digest + '"'
                headers['Content-Range'] = f'bytes {start}-{end}/{len(whole)}'
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
            if route.endswith('/model.safetensors') and start == 0 and len(payload) > 17 and interrupt[0]:
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
            if arguments[0] == 'go' and 'dataset-go' in arguments:
                progress_lines = [line for line in result.stderr.splitlines() if ': received ' in line]
                assert len(progress_lines) == len(set(progress_lines)), result.stderr
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
            # Q25/Q44/Q60/Q80: kill the real CLI at its first committed profile boundary,
            # then restore the exact measured prefix before permitting another source read.
            control = CanonicalBroker(tmp_path / 'state/operations')
            control.resume(ready['operation_id'])
            control.request_hold(ready['operation_id'], 'profile-checkpoint')
            control.close()
            qualify_command = [sys.executable, '-B', '-m', 'cli', '--state', str(tmp_path / 'state'),
                'qualify', '--model-selection', selected['operation_id'], '--drive-selection',
                drive['operation_id'], '--key', 'go-fixture']
            qualifier = subprocess.Popen(qualify_command, cwd=Path(__file__).resolve().parents[1],
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                deadline = time.monotonic() + 30
                while time.monotonic() < deadline:
                    held = json.loads(record_path.read_bytes())['record']
                    holds = [event['payload'] for event in held['events'] if 'hold' in event['payload']]
                    if holds[-1] == {'hold': 'ACKNOWLEDGED', 'boundary': 'profile-checkpoint'}:
                        break
                    assert qualifier.poll() is None, qualifier.communicate()
                    time.sleep(.02)
                else:
                    raise AssertionError('source profile did not durably acknowledge its first boundary')
                object_dir = mount / 'drewwiberg-lacie/Cassette/campaign/objects'
                checkpoint_path = next(path for path in object_dir.iterdir()
                    if json.loads(path.read_bytes())['value'].get('status') == 'CHECKPOINTED')
                checkpoint = json.loads(checkpoint_path.read_bytes())
                assert checkpoint['value']['checkpoint']['totals']['write_bytes'] >= checkpoint['value']['artifact']['size'] > 0
                for trace in checkpoint['value']['traces']:
                    raw = (mount / 'drewwiberg-lacie/Cassette/captures' / trace['attempt'] / trace['name']).read_bytes()
                    assert len(raw) == trace['bytes'] and digest_bytes(raw) == trace['digest']
                profile_files = list((mount / 'drewwiberg-lacie/Cassette/transfers' /
                    checkpoint['value']['extent_operation']).glob('*.extent'))
                held_files = {path: (path.stat().st_ino, path.read_bytes()) for path in profile_files}
                assert held_files
                qualifier.kill()
                qualifier.communicate(timeout=5)
                assert qualifier.returncode < 0
                qualifier = subprocess.Popen(qualify_command, cwd=Path(__file__).resolve().parents[1],
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                deadline = time.monotonic() + 30
                while time.monotonic() < deadline:
                    resumed_record = json.loads(record_path.read_bytes())['record']
                    resumes = [event['payload']['source_profile_resume'] for event in resumed_record['events']
                               if 'source_profile_resume' in event['payload']]
                    if resumes:
                        assert resumes[-1]['capture_key'] == checkpoint['key']
                        assert resumes[-1]['checkpoint_digest'] == 'blake3:' + checkpoint_path.name
                        break
                    assert qualifier.poll() is None, qualifier.communicate()
                    time.sleep(.02)
                else:
                    raise AssertionError('source profile did not restore its durable observation boundary')
                assert all((path.stat().st_ino, path.read_bytes()) == saved for path, saved in held_files.items())
                # The CLI owns the single broker lock. Stop this still-held recovery process
                # before the controller records release, then enter the same job again.
                qualifier.kill()
                qualifier.communicate(timeout=5)
                control = CanonicalBroker(tmp_path / 'state/operations')
                control.release_hold(ready['operation_id'], 'profile-checkpoint')
                control.close()
                qualifier = subprocess.Popen(qualify_command, cwd=Path(__file__).resolve().parents[1],
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                output, error = qualifier.communicate(timeout=30)
                assert qualifier.returncode == 2 and 'Drive check passed. Download remains paused.' in error, error + output
                qualified = json.loads(output)
            finally:
                if qualifier.poll() is None:
                    qualifier.kill()
                    qualifier.communicate(timeout=5)
            assert qualified['state'] == 'PAUSED'
            assert qualified['operation_id'] == ready['operation_id']
            assert sum(method == 'GET' and path.endswith('/model.safetensors')
                       for method, path in requests) == payload_before_qualification
            qualified_record = json.loads(record_path.read_bytes())['record']
            assert qualified_record['phase'] == 'EMPTY'
            assert qualified_record['events'][-2]['payload']['source_qualification']['status'] == 'PASS'
            qualified_profiles = {p.name: p.read_bytes() for p in
                                  (mount / 'drewwiberg-lacie/Cassette/campaign/objects').iterdir()}
            for declarations in ([], ['wrong.safetensors=10'], ['model.safetensors=0'],
                                 ['model.safetensors=999999999999999999999'],
                                 ['model.safetensors=１２'], ['model.safetensors=-1'],
                                 [f'model.safetensors={len(header_bytes)}'] * 2):
                flags = [value for entry in declarations for value in ('--header-json-bytes', entry)]
                refused = launch('qualify', '--headers', '--model-selection', selected['operation_id'],
                                 '--drive-selection', drive['operation_id'], '--key', 'go-fixture',
                                 *flags, expected_code=1)
                assert refused['error']['code'] == 'INVALID_REQUEST'
                assert not header_ranges
            wrong = launch('headers', '--header-json-bytes', f'model.safetensors={len(header_bytes)+1}',
                           '--model-selection', selected['operation_id'], '--drive-selection',
                           drive['operation_id'], '--key', 'go-fixture', expected_code=2,
                           expected_message='Go remains available with the same selections and key.')
            assert wrong['operation_id'] == ready['operation_id']
            assert header_ranges == [(0, 7)]
            wrong_record = json.loads(record_path.read_bytes())['record']
            assert wrong_record['events'][-1]['payload']['error']['code'] == 'METADATA_INSUFFICIENT'
            header_qualified = launch('qualify', '--headers', '--model-selection', selected['operation_id'],
                                      '--header-json-bytes', f'model.safetensors={len(header_bytes)}',
                                      '--drive-selection', drive['operation_id'], '--key', 'go-fixture',
                                      expected_code=2, expected_message='Drive check passed. Download remains paused.')
            assert header_qualified['operation_id'] == ready['operation_id']
            assert header_ranges == [(0, 7)]
            headers = launch('headers', '--model-selection', selected['operation_id'],
                             '--header-json-bytes', f'model.safetensors={len(header_bytes)}',
                             '--drive-selection', drive['operation_id'], '--key', 'go-fixture', expected_code=2,
                             expected_message='Headers saved. Full download verification is separate.')
            assert headers['operation_id'] == ready['operation_id']
            assert header_ranges == [(0, 7), (0, 7), (8, 7 + len(header_bytes))]
            header_record = json.loads(record_path.read_bytes())['record']
            inspection = next(event['payload']['source_headers'] for event in reversed(header_record['events'])
                              if 'source_headers' in event['payload'])
            assert inspection['status'] == 'PARSED' and inspection['payload_verification'] == 'NOT_RUN'
            assert inspection['artifacts'][0]['header_bytes'] == 8 + len(header_bytes)
            assert inspection['artifacts'][0]['tensor_count'] == 1
            inventory_object = mount / 'drewwiberg-lacie/Cassette/campaign/objects' / inspection['artifacts'][0]['header_record_digest'].split(':')[1]
            parsed = json.loads(inventory_object.read_bytes())['value']['parsed']
            assert parsed['inventory']['tensors'] == [{'semantic_tensor_id': 'weight', 'dtype': 'U8',
                'shape': [len(tensor_bytes)], 'offset': 0, 'length': len(tensor_bytes)}]
            header_extents = list((mount / 'drewwiberg-lacie/Cassette/transfers' / ready['operation_id']).glob('*.extent'))
            assert len(header_extents) == 1 and header_extents[0].stat().st_size == len(weights)
            with header_extents[0].open('rb') as handle:
                handle.seek(8 + len(header_bytes))
                assert handle.read(32) == bytes(32)
            assert launch('headers', '--model-selection', selected['operation_id'],
                          '--header-json-bytes', f'model.safetensors={len(header_bytes)}',
                          '--drive-selection', drive['operation_id'], '--key', 'go-fixture', expected_code=2) == headers
            assert header_ranges == [(0, 7), (0, 7), (8, 7 + len(header_bytes))]
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
            # Q42/Q44/Q51/Q53/Q60: qualification executes the retained source path,
            # records bounded traces, then seals and reclaims only its synthetic extents.
            object_dir = mount / 'drewwiberg-lacie/Cassette/campaign/objects'
            profile_records = []
            for path in object_dir.iterdir():
                item = json.loads(path.read_bytes())
                item['_digest'] = 'blake3:' + path.name
                profile_records.append(item)
            assert all(len(item['value'].get('observations', [])) <= 1
                       for item in profile_records if isinstance(item.get('value'), dict))
            profiles = [item for item in profile_records if item['key'].startswith('download-profile-')]
            plans = [item for item in profiles if 'pattern_count' in item['value']]
            fresh_atoms = [item for item in profiles
                           if 'pattern' in item['value'] and 'measurement' in item['value']]
            resume_atoms = [item for item in profiles
                            if 'artifact' in item['value'] and 'measurement' in item['value']
                            and 'profile_digest' in item['value'] and 'pattern' not in item['value']]
            assert len(plans) == 3
            assert all(plan['value']['binding']['profiler_version'] == '6-retained-read-recovery'
                       for plan in plans)
            assert len(fresh_atoms) == len(resume_atoms) == sum(plan['value']['pattern_count'] for plan in plans)
            assert all(item['previous'] is None for item in (*fresh_atoms, *resume_atoms))
            assert all(item['value']['measurement']['host_write_bytes'] == 0 for item in resume_atoms)
            assert all('binding' not in item['value'] and 'patterns' not in item['value']
                       for item in (*fresh_atoms, *resume_atoms))

            plan_by_digest = {item['_digest']: item for item in plans}
            capture_root = mount / 'drewwiberg-lacie/Cassette/captures'

            def trace_events(measurement):
                events = []
                assert measurement['traces']
                for capture in measurement['traces']:
                    raw_path = capture_root / capture['attempt'] / capture['name']
                    raw = raw_path.read_bytes()
                    assert len(raw) == capture['bytes']
                    assert digest_bytes(raw) == capture['digest']
                    events.extend(json.loads(line) for line in raw.splitlines())
                return events

            def chunks(size):
                return [min(4 * 1024 * 1024, size - offset)
                        for offset in range(0, size, 4 * 1024 * 1024)]

            raw_coverage_checked = False
            for atom in fresh_atoms:
                measurement = atom['value']['measurement']
                events = trace_events(measurement)
                plan = plan_by_digest[atom['value']['profile_digest']]['value']['binding']['plan']
                pattern = atom['value']['pattern']
                statistics = measurement['trace_statistics']
                assert statistics['data_write_bytes'] == pattern['write_bytes']
                assert statistics['io_calls'] == len([event for event in events if 'success' in event])
                assert all(window['ended_ns'] > window['started_ns'] for window in statistics['windows'])
                assert sum(window['active_seconds'] for window in statistics['windows']) == statistics['active_seconds']
                for phase in statistics['phases'].values():
                    for rates in (phase['durable_chunk_bytes_per_second'], phase['verified_range_bytes_per_second']):
                        if rates['samples'] < 20:
                            assert rates['empirical_percentiles'] == {}
                if not plan.get('header_only') and not raw_coverage_checked and pattern['write_bytes'] > 4 * 1024 * 1024:
                    # Q42/Q44/Q51: a valid digest cannot conceal an omitted actual write row.
                    owner = CapacityCoordinator(mount / 'drewwiberg-lacie/Cassette')
                    proof_binding = plan_by_digest[atom['value']['profile_digest']]['value']['binding']
                    rows = list(events)
                    omitted = next(index for index, event in enumerate(rows)
                                   if event.get('role') == 'data' and event.get('kind') == 'write')
                    del rows[omitted]
                    payload = b''.join(canonical_bytes(event) + b'\n' for event in rows)
                    assert len(payload) <= 2097152
                    write_campaign_artifact(owner, 'raw-coverage-control', 'missing-write.jsonl', payload)
                    reference = {'attempt': 'raw-coverage-control', 'name': 'missing-write.jsonl',
                                 'bytes': len(payload), 'digest': digest_bytes(payload)}
                    try:
                        source_profile_trace(owner.cartridge, [reference], expected_data_writes=pattern['write_bytes'],
                            expected_data_reads=pattern['read_bytes'], revalidation=False, has_state=True,
                            record_base=plan['checkpoint_record_base'], expected_path=proof_binding['path'])
                    except CassetteError as error:
                        assert error.code == 'ROOT_INVALID'
                        assert ('unobserved data writes' in str(error) or 'coverage is discontinuous' in str(error))
                    else:
                        raise AssertionError('raw source verifier accepted an omitted data write')
                    raw_coverage_checked = True
                if plan.get('header_only'):
                    header_size = pattern['write_bytes'] - 8
                    data_writes = [event for event in events
                                   if event.get('role') == 'data' and event.get('kind') == 'write']
                    data_reads = [event for event in events
                                  if event.get('role') == 'data' and event.get('kind') == 'read']
                    assert [event['requested_bytes'] for event in data_writes] == [8, header_size]
                    assert [event['returned_bytes'] for event in data_writes] == [8, header_size]
                    assert [event['requested_bytes'] for event in data_reads] == [8, header_size]
                    assert [event['returned_bytes'] for event in data_reads] == [8, header_size]
                    parser_reads = [event for event in events if event.get('kind') == 'PARSER_READ']
                    assert [event['requested_bytes'] for event in parser_reads] == [8, header_size]
                    assert [event['returned_bytes'] for event in parser_reads] == [8, header_size]
                    assert measurement['header']['payload_verification'] == 'NOT_RUN'
                else:
                    size = pattern['write_bytes']
                    expected = chunks(size)
                    data_writes = [event for event in events
                                   if event.get('role') == 'data' and event.get('kind') == 'write']
                    data_reads = [event for event in events
                                  if event.get('role') == 'data' and event.get('kind') == 'read']
                    assert [event['requested_bytes'] for event in data_writes] == expected
                    assert [event['returned_bytes'] for event in data_writes] == expected
                    expected_reads = ([expected[0]] if len(measurement['measurement_windows']) > 1 else []) + expected
                    assert [event['requested_bytes'] for event in data_reads] == expected_reads
                    assert [event['returned_bytes'] for event in data_reads] == expected_reads
                    state_writes = [event for event in events
                                    if event.get('role') == 'state' and event.get('kind') == 'write']
                    record_writes = [event for event in state_writes if event['requested_bytes'] == 33]
                    assert [event['requested_bytes'] for event in record_writes] == [33] * len(expected)
                    assert [event['offset'] for event in record_writes] == [
                        131072 + index * 33 for index in range(len(expected))]
                    envelope_writes = [event for event in state_writes if event['requested_bytes'] != 33]
                    assert [event['offset'] % 131072 for event in envelope_writes] == [
                        0 if index % 2 == 0 else 65536 for index in range(len(expected) + 1)]
                assert all(event['success'] is True for event in events if 'success' in event)

            for atom in resume_atoms:
                events = trace_events(atom['value']['measurement'])
                assert not any(event.get('kind') == 'write' for event in events)
                if atom['value']['measurement']['header'] is not None:
                    parser_reads = [event for event in events if event.get('kind') == 'PARSER_READ']
                    header_size = plan_by_digest[atom['value']['profile_digest']]['value']['binding']['plan'][
                        'header_json_bytes'][atom['value']['artifact']]
                    assert [event['requested_bytes'] for event in parser_reads] == [8, header_size]
            assert raw_coverage_checked

            lifecycle_states = {'PREPARED', 'RETAINED', 'SEALED', 'RECLAIMING', 'RECLAIMED'}
            lifecycle_records = [item for item in profiles
                                 if item['value'].get('status') in lifecycle_states]
            by_digest = {item['_digest']: item for item in lifecycle_records}
            grouped = {}
            for item in lifecycle_records:
                grouped.setdefault(item['key'], []).append(item)
            for records in grouped.values():
                final = [item for item in records if item['value']['status'] == 'RECLAIMED']
                assert len(final) == 1
                current = final[0]
                statuses = []
                while current is not None:
                    statuses.append(current['value']['status'])
                    predecessor = current['previous']
                    current = None if predecessor is None else by_digest[predecessor]
                assert statuses == ['RECLAIMED', 'RECLAIMING', 'SEALED', 'RETAINED', 'PREPARED']
            assert lifecycle_records and all(item['value']['status'] == 'RECLAIMED'
                                             for item in lifecycle_records
                                             if item['previous'] is not None and
                                             item['value']['status'] == 'RECLAIMED')
            assert not list((mount / 'drewwiberg-lacie/Cassette').rglob('profile.bin'))
            seals = [item for item in profiles if 'atoms_digest' in item['value']]
            assert len(seals) == 3 and sum(seal['value']['atom_count'] for seal in seals) == len(fresh_atoms) + len(resume_atoms)
            for event in record['events']:
                proof = event['payload'].get('source_qualification', {})
                if proof.get('status') == 'PASS':
                    # Q42/Q53: the bounded operation log references the store's complete profile.
                    assert set(proof) == {'status', 'profile_digest', 'profile_key', 'path'}
                    assert any(seal['key'] == proof['profile_key'] and seal['_digest'] == proof['profile_digest']
                               for seal in seals)
            qualification = next(event['payload']['source_qualification'] for event in record['events']
                                 if event['payload'].get('source_qualification', {}).get('status') == 'PASS')
            assert qualification['profile_digest'] != fresh_atoms[0]['value']['profile_digest']
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
            dataset_before = len([item for item in requests if item[0] == 'GET'
                                  and item[1].startswith('/datasets/') and not item[1].endswith('/README.md')])
            data_selected = launch('select-dataset', '--connection', connection['operation_id'],
                                   '--dataset', 'fixture/data', '--revision', 'c' * 40,
                                   '--file', 'empty.json', '--file', 'inputs.jsonl', '--file', 'samples.parquet', '--key', 'dataset-selection')
            assert [item['path'] for item in data_selected['result']['source_lock']['artifacts']] == [
                'empty.json', 'inputs.jsonl', 'samples.parquet']
            assert data_selected['result']['source_lock']['artifacts'][0]['digest'].startswith('git-sha1:')
            assert data_selected['result']['descriptor']['artifact_selector'] == {
                'dataset_paths': ['empty.json', 'inputs.jsonl', 'samples.parquet']}
            data_prepared = launch('qualify', '--model-selection', data_selected['operation_id'],
                                   '--drive-selection', fresh_drive['operation_id'], '--key', 'dataset-go', expected_code=2)
            assert len([item for item in requests if item[0] == 'GET' and item[1].startswith('/datasets/')
                        and not item[1].endswith('/README.md')]) == dataset_before
            refusal = launch('headers', '--source-selection', data_selected['operation_id'],
                             '--drive-selection', fresh_drive['operation_id'], '--key', 'dataset-go', expected_code=1)
            assert refusal['error']['code'] == 'MODEL_UNSUPPORTED'
            assert launch('status', data_prepared['operation_id'], expected_code=2) == data_prepared
            data_done = launch('go', '--source-selection', data_selected['operation_id'],
                               '--drive-selection', fresh_drive['operation_id'], '--key', 'dataset-go')
            assert data_done['operation_id'] == data_prepared['operation_id'] and data_done['state'] == 'SUCCEEDED'
            assert data_done['result']['verified_bytes'] == sum(len(dataset_files[name]) for name in (
                'inputs.jsonl', 'samples.parquet')) + len(license_bytes)
            completed_requests = list(requests)
            assert launch('go', '--model-selection', data_selected['operation_id'],
                          '--drive-selection', fresh_drive['operation_id'], '--key', 'dataset-go') == data_done
            assert requests == completed_requests
            assert not any('/datasets/' in path and 'unused.jsonl' in path for _, path in requests)
            tiny_selected = launch('select-dataset', '--connection', connection['operation_id'],
                                   '--dataset', 'fixture/data', '--revision', 'c' * 40,
                                   '--file', 'tiny.safetensors', '--key', 'tiny-header-selection')
            assert tiny_selected['result']['source_lock']['artifacts'][0]['digest'].startswith('git-sha1:')
            tiny = launch('headers', '--source-selection', tiny_selected['operation_id'],
                          '--header-json-bytes', f'tiny.safetensors={len(tiny_header)}',
                          '--drive-selection', fresh_drive['operation_id'], '--key', 'tiny-header', expected_code=2)
            tiny_record = json.loads((tmp_path / 'state/operations' / (tiny['operation_id'] + '.json')).read_bytes())['record']
            assert tiny_record['events'][-2]['payload']['source_headers']['artifacts'][0]['tensor_count'] == 1
            for corruption in ('missing', 'zero-prefix', 'changed-byte'):
                key = 'saved-header-' + corruption
                saved = launch('headers', '--source-selection', selected['operation_id'],
                               '--header-json-bytes', f'model.safetensors={len(header_bytes)}',
                               '--drive-selection', fresh_drive['operation_id'], '--key', key, expected_code=2)
                extents = list((mount / 'drewwiberg-lacie/Cassette/transfers' / saved['operation_id']).glob('*.extent'))
                assert len(extents) == 1
                if corruption == 'missing':
                    extents[0].unlink()
                else:
                    with extents[0].open('r+b') as handle:
                        handle.write(bytes(8) if corruption == 'zero-prefix' else b'!')
                range_count = len(header_ranges)
                refused = launch('headers', '--source-selection', selected['operation_id'],
                                 '--header-json-bytes', f'model.safetensors={len(header_bytes)}',
                                 '--drive-selection', fresh_drive['operation_id'], '--key', key, expected_code=2,
                                 expected_message='Go remains available with the same selections and key.')
                saved_record = json.loads((tmp_path / 'state/operations' / (saved['operation_id'] + '.json')).read_bytes())['record']
                assert refused['state'] == 'PAUSED'
                assert saved_record['events'][-1]['payload']['error']['code'] == 'IDENTITY_MISMATCH'
                assert len(header_ranges) == range_count
                if corruption == 'missing':
                    assert not extents[0].exists()
                assert launch('go', '--source-selection', selected['operation_id'],
                              '--drive-selection', fresh_drive['operation_id'], '--key', key)['state'] == 'SUCCEEDED'
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
