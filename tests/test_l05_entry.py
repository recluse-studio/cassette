# test_l05_entry.py — L05 product CLI source and drive entry proof (Q5/Q9/Q44/Q49/Q52); depends on cli.py, tests/test_l05_drive.py.
"""Exercise the installed-module launch against an external HTTP boundary fixture."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
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
    """Q5/Q9/Q44 acceptance: selection and Go preserve source identity before the physical hold.

    The CLI crosses the provider boundary, survives a new process and retains its selection
    after a mutable tag changes. Model payload belongs to the later qualified Go operation.
    """
    weights = b'fixture weights must remain at the provider during selection'
    license_bytes = b'fixture license'
    requests = []
    revision = ['a' * 40]

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
                    'private': False, 'gated': False, 'siblings': [
                        {'rfilename': 'model.safetensors', 'size': len(weights),
                         'lfs': {'size': len(weights), 'sha256': hashlib.sha256(weights).hexdigest()}},
                        {'rfilename': 'LICENSE', 'size': len(license_bytes),
                         'blobId': hashlib.sha1(f'blob {len(license_bytes)}\0'.encode() + license_bytes).hexdigest()}
                    ]}).encode()
            elif route.endswith('/LICENSE'):
                payload = license_bytes
                headers['ETag'] = '"' + hashlib.sha1(f'blob {len(payload)}\0'.encode() + payload).hexdigest() + '"'
            else:
                self.send_response(404)
                self.send_header('Content-Length', '0')
                self.end_headers()
                return
            self.send_response(200)
            self.send_header('Content-Length', str(len(payload)))
            for name, value in headers.items():
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(payload)

    server = ThreadingHTTPServer(('127.0.0.1', 0), Provider)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        def launch(*arguments, expected_code=0):
            result = subprocess.run([sys.executable, '-B', '-m', 'cli', '--state',
                str(tmp_path / 'state'), *arguments], cwd=Path(__file__).resolve().parents[1],
                capture_output=True, text=True, timeout=30)
            assert result.returncode == expected_code, result.stderr + result.stdout
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
            ready = launch('go', '--model-selection', selected['operation_id'], '--drive-selection',
                           drive['operation_id'], '--key', 'go-fixture', expected_code=2)
            assert ready['state'] == 'PAUSED'
            assert (parent / 'Cassette/cartridge.json').is_file()
            assert (parent / 'user.txt').read_bytes() == b'protected'
            assert launch('go', '--model-selection', selected['operation_id'], '--drive-selection',
                          drive['operation_id'], '--key', 'go-fixture', expected_code=2) == ready
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
        finally:
            if watcher is not None and watcher.poll() is None:
                watcher.terminate()
                watcher.communicate(timeout=10)
            if attached:
                mount.chmod(root_mode)
                subprocess.run(['/usr/bin/hdiutil', 'detach', str(mount), '-quiet'], check=True, capture_output=True)
            image.unlink()
        assert all(not (method == 'GET' and 'model.safetensors' in route) for method, route in requests)
        assert all(weights not in path.read_bytes() for path in (tmp_path / 'state').rglob('*') if path.is_file())
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
