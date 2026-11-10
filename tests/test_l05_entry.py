# test_l05_entry.py — L05 product CLI source and drive entry proof (Q5/Q9/Q44/Q49/Q52); depends on broker.py, cli.py, errors.py, store.py, tests/test_l05_drive.py.
"""Exercise the installed-module launch against an external HTTP boundary fixture."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import asyncio
import hashlib
import json
import os
from pathlib import Path
import plistlib
import shutil
import signal
import socket
import stat
import subprocess
import sys
import threading
import time
from urllib.parse import parse_qs, urlparse

import cli
from broker import CanonicalBroker, _source_from
from errors import CassetteError
from store import CapacityCoordinator, campaign_head, canonical_bytes, compare_campaign_head, compare_inventory, digest_bytes, drive_path_observation, select_external_apfs_volume, source_profile_trace, write_campaign_artifact
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
            # Keep the disposable excluded name stable during native volume discovery.
            os.chflags(path, stat.UF_IMMUTABLE)
            try:
                path.rename(path.with_name(name + '-bad-1'))
            except PermissionError:
                pass
            else:
                raise AssertionError('excluded fixture directory could be renamed')
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
        os.chflags(temporary, 0)
        temporary.chmod(0o755)
        (temporary / 'new-owned-fixture').write_bytes(bytes(100))
        temporary.chmod(0)
        assert select('changed-excluded')['result']['protected_inventory'] == after
    finally:
        try:
            for path in locked:
                if path.exists():
                    os.chflags(path, 0)
                    path.chmod(0o755)
        finally:
            subprocess.run(['/usr/bin/hdiutil', 'detach', str(mount), '-quiet'], check=True, capture_output=True)
            image.unlink()


def test_q5_q9_cli_selection_pins_source_without_downloading_weights(tmp_path, monkeypatch):
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
    generated_model = [weights[:32]]
    generated_assets = {'config.json': b'{"family":"owned-source-fixture"}',
                        'license.txt': b'generated-fixture-license'}

    def generated_manifest():
        def entry(name, payload, media):
            return {'mediaType': media, 'digest': 'sha256:' + hashlib.sha256(payload).hexdigest(),
                    'size': len(payload), 'annotations': {'org.opencontainers.image.title': name}}
        return canonical_bytes({'schemaVersion': 2,
            'config': entry('config.json', generated_assets['config.json'], 'application/vnd.docker.container.image.v1+json'),
            'layers': [entry('prepared.bin', generated_model[0], 'application/vnd.ollama.image.model'),
                       entry('license.txt', generated_assets['license.txt'], 'application/vnd.ollama.image.license')]})

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
            if route == '/api/tags':
                payload = canonical_bytes({'models': [{'name': 'fixture/generated:latest',
                    'model': 'fixture/generated:latest', 'size': len(generated_model[0])}]})
            elif route.startswith('/v2/fixture/generated/manifests/'):
                payload = generated_manifest()
            elif route.startswith('/v2/fixture/generated/blobs/'):
                objects = {**generated_assets, 'prepared.bin': generated_model[0]}
                payload = next(content for content in objects.values()
                               if 'sha256:' + hashlib.sha256(content).hexdigest() == route.rsplit('/', 1)[1])
                if 'Range' in self.headers:
                    start, end = map(int, self.headers['Range'].removeprefix('bytes=').split('-'))
                    headers['Content-Range'] = f'bytes {start}-{end}/{len(payload)}'
                    payload = payload[start:end+1]
            elif route == '/api/models':
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
        startup = tmp_path / 'diagnostic-startup'
        startup.mkdir()
        original_startup = str(Path(sys.modules['sitecustomize'].__file__).resolve())
        (startup / 'sitecustomize.py').write_text(
            '# sitecustomize.py — bounded fixture stack capture; depends on no repository files.\n'
            'import runpy\n'
            f'runpy.run_path({original_startup!r}, run_name="sitecustomize")\n'
            'import faulthandler\n'
            'faulthandler.dump_traceback_later(25)\n'
            'import fcntl, json, os, sys, threading, time\nif any(command in sys.argv for command in ("qualify", "qualify-composition", "headers", "go")):\n    directory = os.path.join(os.path.dirname(__file__), "sync-timings")\n    os.makedirs(directory, exist_ok=True)\n    descriptor = os.open(os.path.join(directory, str(os.getpid()) + ".jsonl"), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)\n    pending = {}\n    def observe_sync(frame, event, function):\n        if event == "call" and frame.f_code.co_name == "hold_boundary" and frame.f_locals.get("boundary") == "profile-checkpoint":\n            row = {"event": "source_profile_prepared", "pid": os.getpid(), "parent_pid": os.getppid(), "operation_id": frame.f_locals["operation_id"], "boundary": frame.f_locals["boundary"], "wall_ns": str(time.time_ns()), "monotonic_ns": str(time.monotonic_ns())}\n            os.write(descriptor, (json.dumps(row) + "\\n").encode())\n        if event == "call" and frame.f_code.co_name == "complete_capacity_claim":\n            parent = frame.f_back\n            claim = frame.f_locals.get("claim")\n            if (parent is not None and parent.f_code.co_name == "_checkpointed_transfer"\n                    and claim is not None and claim.transition.boundary_id.endswith(":checkpoint-initial")):\n                state = parent.f_locals["state_extent"]\n                row = {"event": "initial_checkpoint_durable", "pid": os.getpid(),\n                       "parent_pid": os.getppid(), "operation_id": state.operation_id,\n                       "path": parent.f_locals["artifact"].path, "generation": 0,\n                       "wall_ns": str(time.time_ns()), "monotonic_ns": str(time.monotonic_ns())}\n                os.write(descriptor, (json.dumps(row) + "\\n").encode())\n        if frame.f_code.co_name != "_fullsync_descriptor" or function not in (os.fsync, fcntl.fcntl):\n            return\n        thread = threading.get_ident()\n        if event == "c_call":\n            handle = frame.f_locals["descriptor"]\n            status = os.fstat(handle)\n            row = {"event": "start", "pid": os.getpid(), "parent_pid": os.getppid(), "thread": str(thread),\n                   "function": function.__name__, "path": str(frame.f_back.f_locals.get("path", frame.f_locals["name"])),\n                   "object_id": frame.f_locals["object_id"], "device": str(status.st_dev), "inode": str(status.st_ino),\n                   "wall_ns": str(time.time_ns())}\n            os.write(descriptor, (json.dumps(row) + "\\n").encode())\n            pending[thread] = (time.monotonic_ns(), row)\n        elif event in ("c_return", "c_exception") and thread in pending:\n            started, row = pending.pop(thread)\n            row = {**row, "event": event, "elapsed_ns": str(time.monotonic_ns() - started), "wall_ns": str(time.time_ns())}\n            os.write(descriptor, (json.dumps(row) + "\\n").encode())\n    threading.setprofile(observe_sync)\n    sys.setprofile(observe_sync)\n')
        child_environment = {**os.environ, 'PYTHONPATH': os.pathsep.join(
            filter(None, (str(startup), os.environ.get('PYTHONPATH'))))}
        def physical_watchdog(full_flushes):
            # Observed fixture fullsyncs reached 16.623s; allow 16.7s per counted flush.
            # This finite setup estimate preserves the separate ACK and product deadlines.
            return 50 * ((full_flushes * 167 + 100 + 499) // 500)

        def launch(*arguments, expected_code=0, expected_message=None):
            command = [sys.executable, '-B', '-m', 'cli', '--state', str(tmp_path / 'state'), *arguments]
            watchdog_seconds = 30
            if ((arguments[0] in {'qualify', 'headers'} and expected_code == 2)
                    or (arguments[0] == 'go' and (expected_code == 0
                        or (expected_code == 2 and (expected_message ==
                            'Go paused at the physical drive qualification boundary.' or
                            ('--key' in arguments and arguments[arguments.index('--key') + 1] == 'go-reported')))))):
                if '--operation-plan' in arguments:
                    plan_path = Path(arguments[arguments.index('--operation-plan') + 1])
                    plan = json.loads(plan_path.read_bytes())
                    artifacts = plan['artifacts']
                    retained_source = plan.get('source_storage') == 'CARTRIDGE_RETAINED'
                else:
                    option = '--model-selection' if '--model-selection' in arguments else '--source-selection'
                    selected_id = arguments[arguments.index(option) + 1]
                    selected_path = tmp_path / 'state/operations' / (selected_id + '.json')
                    source_lock = json.loads(selected_path.read_bytes())['record']['result']['source_lock']
                    artifacts = [*source_lock['artifacts'], *source_lock.get('metadata_assets', [])]
                    retained_source = False
                # Q42/Q44: count the base publications and extra retained-source lifecycles.
                # This finite completion watchdog does not impose a product service deadline.
                full_flushes = (60 if retained_source else 35) * len(artifacts) + 6
                watchdog_seconds = physical_watchdog(full_flushes)
                if ((arguments[0] == 'qualify' and '--operation-plan' in arguments) or
                        (arguments[0] == 'go' and '--key' in arguments and
                         arguments[arguments.index('--key') + 1] in {'go-reported', 'go-reuse'})):
                    # Attempt31 observed a 16.623s fullsync; this is a harness estimate.
                    watchdog_seconds = 50 * ((full_flushes * 167 + 100 + 499) // 500)
                with (tmp_path / 'qualification-watchdogs.jsonl').open('a') as log:
                    log.write(json.dumps({'arguments': list(arguments), 'artifacts': len(artifacts),
                        'estimated_full_flushes': full_flushes, 'retained_source': retained_source,
                        'watchdog_seconds': watchdog_seconds}) + '\n')
            elif arguments[0] == 'qualify-composition' and expected_code == 0:
                recipe = json.loads(Path(arguments[arguments.index('--recipe') + 1]).read_bytes())
                outputs = recipe['artifacts']
                # Q42/Q44/Q60: three barriers per output publication, two extent grants,
                # an initial checkpoint per output, two flushes per chunk, five global publications and one trace flush.
                chunks = sum(max(1, (sum(len(segment['literal_hex']) // 2 if 'literal_hex' in segment
                    else segment['length'] for segment in item['segments']) + 4 * 1024 * 1024 - 1)
                    // (4 * 1024 * 1024)) for item in outputs)
                full_flushes = 6 * len(outputs) + 2 * chunks + 16
                # Attempt35 observed slow fullsyncs; this remains a fixture estimate.
                watchdog_seconds = 50 * ((full_flushes * 167 + 100 + 499) // 500)
                with (tmp_path / 'qualification-watchdogs.jsonl').open('a') as log:
                    log.write(json.dumps({'arguments': list(arguments), 'artifacts': len(outputs),
                        'estimated_full_flushes': full_flushes, 'output_chunks': chunks,
                        'watchdog_seconds': watchdog_seconds}) + '\n')
            started_ns = time.time_ns()
            with subprocess.Popen(command, cwd=Path(__file__).resolve().parents[1], env=child_environment,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as child:
                try:
                    stdout, stderr = child.communicate(timeout=watchdog_seconds)
                except subprocess.TimeoutExpired as error:
                    child.kill()
                    stdout, stderr = child.communicate()
                    evidence = tmp_path / 'failed-cli'
                    evidence.mkdir(exist_ok=True)
                    states = {}
                    for path in (tmp_path / 'state/operations').glob('op-*.json'):
                        if path.stat().st_mtime_ns >= started_ns:
                            raw = path.read_bytes()
                            states[path.name] = {'raw_hex': raw.hex(), 'sha256': hashlib.sha256(raw).hexdigest()}
                    partial = {name: (value.encode() if isinstance(value, str) else value or b'').hex()
                               for name, value in (('stdout', error.output), ('stderr', error.stderr))}
                    (evidence / (str(len(list(evidence.iterdir()))) + '.json')).write_bytes(canonical_bytes({
                        'command': command, 'cwd': str(Path(__file__).resolve().parents[1]),
                        'pid': child.pid, 'parent_pid': os.getpid(), 'started_ns': str(started_ns),
                        'finished_ns': str(time.time_ns()), 'timeout_seconds': error.timeout, 'exit_code': child.returncode,
                        'partial_hex': partial, 'stdout': stdout, 'stderr': stderr, 'operation_states': states}))
                    raise
                result = subprocess.CompletedProcess(command, child.returncode, stdout, stderr)
            if arguments[0] == 'qualify-composition':
                evidence = tmp_path / 'composition-cli'
                evidence.mkdir(exist_ok=True)
                (evidence / (str(len(list(evidence.iterdir()))) + '.json')).write_bytes(canonical_bytes({
                    'arguments': list(arguments), 'exit_code': result.returncode,
                    'stdout': result.stdout, 'stderr': result.stderr}))
            if '--preparation' in arguments or any(value.startswith('generated-') for value in arguments):
                evidence = tmp_path / 'generated-cli'
                evidence.mkdir(exist_ok=True)
                (evidence / (str(len(list(evidence.iterdir()))) + '.json')).write_bytes(canonical_bytes({
                    'arguments': list(arguments), 'exit_code': result.returncode,
                    'stdout': result.stdout, 'stderr': result.stderr}))
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
        image, mount = _attached_apfs_image(tmp_path, size="128m")
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
            added_path = mount / 'added\tentry'
            added_path.write_bytes(b'top-level addition')
            confirmed = launch('watch-remount', reported['operation_id'], '--reconnected', '--key', 'reported-remount')
            assert confirmed['result']['go_operation_id'] == reported['operation_id']
            assert launch('watch-remount', reported['operation_id'], '--reconnected', '--key', 'reported-remount') == confirmed
            reported_record = json.loads((tmp_path / 'state/operations' / (reported['operation_id'] + '.json')).read_bytes())['record']
            assert any(event['payload'].get('physical_reconnect_reported') == 'OPERATOR'
                       for event in reported_record['events'])
            assert not any('drive_disconnected' in event['payload'] for event in reported_record['events'])
            assert any('drive_remounted' in event['payload'] for event in reported_record['events'])
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
            qualifier = subprocess.Popen(qualify_command, cwd=Path(__file__).resolve().parents[1], env=child_environment,
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                # Wait for the exact owned profile setup before starting the original ACK clock.
                preparation_deadline = time.monotonic() + 50 * ((76 * 167 + 100 + 499) // 500)
                timing_path = startup / 'sync-timings' / (str(qualifier.pid) + '.jsonl')
                while time.monotonic() < preparation_deadline:
                    if timing_path.exists():
                        lines = timing_path.read_text().splitlines()
                        prepared = [json.loads(line) for line in lines if line.endswith('}') and
                                    '"source_profile_prepared"' in line]
                        if any(row['pid'] == qualifier.pid and row['parent_pid'] == os.getpid() and
                               row['operation_id'] == ready['operation_id'] for row in prepared):
                            break
                    if qualifier.poll() is not None:
                        raise RuntimeError('source profile qualifier exited during preparation')
                    time.sleep(.02)
                else:
                    raise TimeoutError('source profile preparation did not reach its owned capture')
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
                qualifier = subprocess.Popen(qualify_command, cwd=Path(__file__).resolve().parents[1], env=child_environment,
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
                qualifier = subprocess.Popen(qualify_command, cwd=Path(__file__).resolve().parents[1], env=child_environment,
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                # Q42/Q44: this is the two-artifact completion watchdog, not a service deadline.
                # Diagnostic estimate: 68 full flushes * 1.60s + 6s = 114.8s, rounded to 120s.
                output, error = qualifier.communicate(timeout=120)
                assert qualifier.returncode == 2 and 'Drive check passed. Download remains paused.' in error, error + output
                qualified = json.loads(output)
            finally:
                failure = sys.exc_info()[1]
                if qualifier.poll() is None:
                    qualifier.kill()
                    qualifier_output, qualifier_error = qualifier.communicate(timeout=5)
                if isinstance(failure, (subprocess.TimeoutExpired, AssertionError, TimeoutError, RuntimeError)):
                    qualifier_output, qualifier_error = qualifier.communicate(timeout=5)
                    evidence = tmp_path / 'failed-cli'
                    evidence.mkdir(exist_ok=True)
                    (evidence / ('qualifier-' + str(qualifier.pid) + '.json')).write_bytes(canonical_bytes({
                        'command': qualify_command, 'pid': qualifier.pid, 'parent_pid': os.getpid(),
                        'finished_ns': str(time.time_ns()), 'timeout_seconds': getattr(failure, 'timeout', None),
                        'exit_code': qualifier.returncode, 'stdout': qualifier_output, 'stderr': qualifier_error,
                        'partial_hex': {name: (value.encode() if isinstance(value, str) else value or b'').hex()
                            for name, value in (('stdout', getattr(failure, 'output', None)), ('stderr', getattr(failure, 'stderr', None)))}}))
            assert qualified['state'] == 'PAUSED'
            assert qualified['operation_id'] == ready['operation_id']
            assert sum(method == 'GET' and path.endswith('/model.safetensors')
                       for method, path in requests) == payload_before_qualification
            qualified_record = json.loads(record_path.read_bytes())['record']
            assert qualified_record['phase'] == 'EMPTY'
            assert qualified_record['events'][-2]['payload']['source_qualification']['status'] == 'PASS'
            # Q41/Q80: another writer may change protected content while Cassette qualifies.
            observed = {'added\tentry': {'type': 'file', 'logical_bytes': len(b'top-level addition')},
                        'drewwiberg-lacie': {'type': 'directory', 'logical_bytes': len(b'changed outside the cartridge')}}
            comparison = {'selected': [{'name': 'drewwiberg-lacie', 'type': 'directory', 'logical_bytes': 9}],
                          'observed': [{'name': name, **entry} for name, entry in sorted(observed.items())],
                          'selected_digest': drive['result']['inventory_digest'],
                          'observed_digest': digest_bytes(canonical_bytes(observed))}
            comparisons = [event['payload']['protected_inventory_comparison'] for event in qualified_record['events']
                           if 'protected_inventory_comparison' in event['payload']]
            assert comparisons and all(value == comparison for value in comparisons)
            assert user_path.read_bytes() == b'changed outside the cartridge'
            assert added_path.read_bytes() == b'top-level addition'
            added_path.unlink()
            user_path.write_bytes(b'protected')
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
            # Q42/Q43/Q60: the product measures composition on its original acquired cartridge.
            original_acquisition = record_path.read_bytes()
            recipe_path = tmp_path / 'composition.json'
            source_record = _source_from(record['checkpoint']['source_lock'], completed['operation_id']).record()
            recipe = {'source_record_digest': digest_bytes(canonical_bytes(source_record)), 'artifacts': [
                {'path': 'prepared.bin', 'segments': [{'literal_hex': '00ff'},
                    {'path': 'model.safetensors', 'offset': 0, 'length': len(weights)}]}]}
            recipe_path.write_bytes(canonical_bytes(recipe))
            composition_args = ['qualify-composition', '--acquisition', completed['operation_id'],
                                '--recipe', str(recipe_path), '--key', 'composition-qualification']
            qualification = launch(*composition_args, expected_message='Composition drive check passed.')
            assert qualification['operation']['kind'] == 'source.compose'
            assert qualification['operation']['state'] == 'SUCCEEDED'
            measured = qualification['source_qualification']
            assert measured['status'] == 'PASS'
            cartridge = mount / 'drewwiberg-lacie/Cassette'
            profile = campaign_head(cartridge, measured['profile_key'])
            capture = campaign_head(cartridge, measured['capture_key'])
            assert profile['digest'] == measured['profile_digest']
            assert profile['value']['capture_digest'] == capture['digest']
            assert profile['value']['binding']['operation'] == qualification['operation']['operation_id']
            assert profile['value']['binding']['plan']['composition']['acquisition_operation_id'] == completed['operation_id']
            assert profile['value']['binding']['drive'] == volume['volume_uuid']
            assert profile['value']['binding']['profiler_version'].endswith('/source-byte-composition-v2')
            assert profile['value']['cache']['classification'] == 'WITHIN_HOST_MEMORY'
            assert launch(*composition_args) == qualification
            assert record_path.read_bytes() == original_acquisition
            assert len([item for item in requests if item[0] == 'GET' and 'model.safetensors' in item[1]]) == payload_requests
            assert 'source_lock' not in qualification['operation']['result']
            recipe['artifacts'][0]['segments'][0]['literal_hex'] = '00fe'
            recipe_path.write_bytes(canonical_bytes(recipe))
            conflict = launch(*composition_args, expected_code=1)
            assert conflict['error']['code'] == 'IDEMPOTENCY_CONFLICT'
            assert campaign_head(cartridge, measured['profile_key']) == profile
            assert record_path.read_bytes() == original_acquisition
            recipe['artifacts'][0]['segments'][0]['literal_hex'] = '00ff'
            recipe_path.write_bytes(canonical_bytes(recipe))
            invalid = launch('qualify-composition', '--acquisition', selected['operation_id'],
                '--recipe', str(recipe_path), '--key', 'composition-invalid-acquisition', expected_code=1)
            assert invalid['error']['code'] == 'INVALID_REQUEST'
            # Q5/Q60: a killed owner continues the same operation under a new, retained capture.
            def interrupt_composition(stop_signal, key):
                interrupted_request = {'protocol_version': '1', 'operation': 'source.compose',
                    'idempotency_key': key,
                    'target': completed['operation_id'], 'arguments': {'composition': {
                        'acquisition_operation_id': completed['operation_id'], 'recipe': recipe}}}
                control = CanonicalBroker(tmp_path / 'state/operations')
                try:
                    interrupted_id = control.issue(interrupted_request)['operation_id']
                    control.request_hold(interrupted_id, 'composition-checkpoint')
                finally:
                    control.close()
                interrupted_args = [*composition_args[:-1], interrupted_request['idempotency_key']]
                command = [sys.executable, '-B', '-m', 'cli', '--state', str(tmp_path / 'state'), *interrupted_args]
                started_ns = time.time_ns()
                child = subprocess.Popen(command, cwd=Path(__file__).resolve().parents[1],
                    env=child_environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                interrupted_path = tmp_path / 'state/operations' / (interrupted_id + '.json')
                stdout, stderr, failure = '', '', None
                setup = {'operation_id': interrupted_id, 'pid': child.pid, 'phase': 'initial-output-checkpoint',
                    'estimated_full_flushes': 9, 'seconds_per_flush': '6.10', 'watchdog_seconds': 100,
                    'basis': 'attempt27 observed maximum6.014525625seconds; estimate, not a product deadline'}
                try:
                    first_output = next(item['path'] for item in recipe['artifacts'] if sum(
                        len(segment['literal_hex']) // 2 if 'literal_hex' in segment else segment['length']
                        for segment in item['segments']) > 0)
                    timing_path = startup / 'sync-timings' / (str(child.pid) + '.jsonl')
                    deadline = time.monotonic() + setup['watchdog_seconds']
                    while time.monotonic() < deadline:
                        rows = [] if not timing_path.exists() else [json.loads(line) for line in
                            timing_path.read_bytes().split(b'\n')[:-1] if line]
                        ready = next((row for row in rows if row.get('event') == 'initial_checkpoint_durable'
                            and row.get('operation_id') == interrupted_id and row.get('path') == first_output), None)
                        if ready is not None:
                            setup['preparation_receipt'] = ready
                            break
                        if child.poll() is not None:
                            stdout, stderr = child.communicate()
                            raise AssertionError('composition CLI exited during initial checkpoint preparation')
                        time.sleep(.01)
                    else:
                        raise AssertionError('composition CLI did not finish initial checkpoint preparation')
                    setup['ack_observer_started_ns'] = str(time.monotonic_ns())
                    for _ in range(3000):
                        live = json.loads(interrupted_path.read_bytes())['record']
                        if any(event['payload'].get('hold') == 'ACKNOWLEDGED' for event in live['events']):
                            break
                        assert child.poll() is None, child.communicate()
                        time.sleep(.01)
                    else:
                        raise AssertionError('composition CLI did not acknowledge its checkpoint hold')
                    child.send_signal(stop_signal)
                    stdout, stderr = child.communicate(timeout=30)
                    assert child.returncode == -stop_signal
                except BaseException as error:
                    failure = repr(error)
                    raise
                finally:
                    if child.poll() is None:
                        child.kill()
                    if failure is not None:
                        stdout, stderr = child.communicate(timeout=30)
                        raw = interrupted_path.read_bytes()
                        packet = tmp_path / 'failed-cli' / ('composition-' + str(child.pid) + '.json')
                        packet.parent.mkdir(exist_ok=True)
                        packet.write_bytes(canonical_bytes({'command': command, 'pid': child.pid,
                            'parent_pid': os.getpid(), 'started_ns': str(started_ns),
                            'finished_ns': str(time.time_ns()), 'exit_code': child.returncode,
                            'stdout': stdout, 'stderr': stderr, 'failure': failure, 'setup': setup,
                            'raw_operation_hex': raw.hex(), 'raw_operation_sha256': hashlib.sha256(raw).hexdigest()}))
                    with (tmp_path / 'composition-checkpoint-preparation.jsonl').open('a') as log:
                        log.write(json.dumps({**setup, 'failure': failure}) + '\n')
                cli_evidence = tmp_path / 'composition-cli'
                (cli_evidence / (str(len(list(cli_evidence.iterdir()))) + '.json')).write_bytes(canonical_bytes({
                    'arguments': interrupted_args, 'signal': stop_signal.name, 'exit_code': child.returncode,
                    'stdout': stdout, 'stderr': stderr}))
                old_key = 'composition-capture-' + interrupted_id.removeprefix('op-')
                incomplete = campaign_head(cartridge, old_key)
                assert incomplete['value']['status'] in {'MEASURING', 'INCOMPLETE'}
                control = CanonicalBroker(tmp_path / 'state/operations')
                try:
                    control.release_hold(interrupted_id, 'composition-checkpoint')
                finally:
                    control.close()
                return interrupted_request, interrupted_id, interrupted_args, interrupted_path, old_key, incomplete

            for stop_signal in (signal.SIGKILL, signal.SIGINT):
                interrupted_request, interrupted_id, interrupted_args, interrupted_path, old_key, incomplete = interrupt_composition(
                    stop_signal, 'composition-interrupted-' + stop_signal.name)
                recovered = launch(*interrupted_args, expected_code=1)
                assert recovered['operation']['operation_id'] == interrupted_id
                assert recovered['operation']['state'] == 'SUCCEEDED'
                assert recovered['source_qualification']['status'] == 'FAIL'
                assert 'complete fresh canonical composition' in recovered['source_qualification']['error']['detail']
                successful_record = interrupted_path.read_bytes()
                attempts = [event['payload']['composition_capture']
                    for event in json.loads(successful_record)['record']['events']
                    if 'composition_capture' in event['payload']]
                assert len(attempts) == 1 and attempts[0] != old_key
                assert campaign_head(cartridge, attempts[0])['value']['status'] == 'CAPTURED'
                assert campaign_head(cartridge, old_key) == incomplete
                assert launch(*interrupted_args, expected_code=1) == recovered
                assert interrupted_path.read_bytes() == successful_record
                assert campaign_head(cartridge, old_key) == incomplete
                assert record_path.read_bytes() == original_acquisition
            # Q5: the retry policy never clears an operator's deliberate pause.
            manual_request = {**interrupted_request, 'idempotency_key': 'composition-manual-pause'}
            control = CanonicalBroker(tmp_path / 'state/operations')
            try:
                manual = control.issue(manual_request)
                manual = control.pause(manual['operation_id'])
            finally:
                control.close()
            manual_args = [*composition_args[:-1], manual_request['idempotency_key']]
            paused = launch(*manual_args, expected_code=2)
            assert paused['operation'] == manual
            assert paused['source_qualification']['status'] == 'NOT_RUN'
            assert campaign_head(cartridge, 'composition-capture-' + manual['operation_id'].removeprefix('op-')) is None
            # Q49: a missing selected root pauses before creating another cartridge or source extent.
            held = cartridge.with_name('Cassette-held-fixture')
            cartridge.rename(held)
            missing_args = [*composition_args[:-1], 'composition-missing-root']
            try:
                missing = launch(*missing_args, expected_code=2)
                assert missing['operation']['state'] == 'PAUSED'
                assert missing['source_qualification']['status'] == 'FAIL'
                assert missing['source_qualification']['error']['code'] == 'CARTRIDGE_DISCONNECTED'
                assert not cartridge.exists()
            finally:
                if not cartridge.exists():
                    held.rename(cartridge)
            resumed = launch(*missing_args)
            assert resumed['operation']['operation_id'] == missing['operation']['operation_id']
            assert resumed['operation']['state'] == 'SUCCEEDED'
            assert resumed['source_qualification']['status'] == 'PASS'
            assert launch(*missing_args) == resumed
            assert record_path.read_bytes() == original_acquisition
            # Retain exact control metadata and raw rows before the owned profile contradiction.
            evidence = tmp_path / 'composition-fixture'
            shutil.copytree(cartridge / 'campaign', evidence / 'cartridge/campaign')
            shutil.copytree(cartridge / 'captures', evidence / 'cartridge/captures')
            (evidence / 'request.json').write_bytes(canonical_bytes({'protocol_version': '1',
                'operation': 'source.compose', 'idempotency_key': 'composition-qualification',
                'target': completed['operation_id'], 'arguments': {'composition': {
                    'acquisition_operation_id': completed['operation_id'], 'recipe': recipe}}}))
            (evidence / 'qualification.json').write_bytes(canonical_bytes(qualification))
            # Q6/Q42/Q60: a failed later profile cannot rewrite a completed byte-preparation result.
            compose_record = tmp_path / 'state/operations' / (qualification['operation']['operation_id'] + '.json')
            complete_bytes = compose_record.read_bytes()
            bad_profile = compare_campaign_head(CapacityCoordinator(cartridge), measured['profile_key'],
                profile['digest'], {**profile['value'], 'wall_seconds': profile['value']['wall_seconds'] + 1})
            refused = launch(*composition_args, expected_code=1)
            assert refused['operation'] == qualification['operation']
            assert refused['source_qualification']['status'] == 'FAIL'
            assert refused['source_qualification']['error']['code'] == 'ROOT_INVALID'
            assert compose_record.read_bytes() == complete_bytes
            compare_campaign_head(CapacityCoordinator(cartridge), measured['profile_key'], bad_profile['digest'], profile['value'])
            assert record_path.read_bytes() == original_acquisition
            # Q9/Q42/Q60: actual provider metadata joins the complete prepared artifact closure.
            generated_recipe = {'source_record_digest': digest_bytes(canonical_bytes(source_record)), 'artifacts': [
                {'path': name, 'segments': [{'literal_hex': content.hex()}]}
                for name, content in sorted(generated_assets.items())] + [
                {'path': 'prepared.bin', 'segments': [{'path': 'model.safetensors', 'offset': 0, 'length': 32}]}]}
            generated_recipe_path = tmp_path / 'generated-recipe.json'
            generated_recipe_path.write_bytes(canonical_bytes(generated_recipe))
            generated_composition_request = {'protocol_version': '1', 'operation': 'source.compose',
                'idempotency_key': 'generated-composition', 'target': completed['operation_id'],
                'arguments': {'composition': {'acquisition_operation_id': completed['operation_id'], 'recipe': generated_recipe}}}
            generated_composition = launch('qualify-composition', '--acquisition', completed['operation_id'],
                '--recipe', str(generated_recipe_path), '--key', 'generated-composition')
            generated_geometry = {'source_lock': None, 'source_kind': 'ollama', 'revision_algorithm': 'sha256',
                'provenance': {'recipe_digest': digest_bytes(canonical_bytes(generated_recipe))},
                'artifacts': [{'path': name, 'size': len(content), 'digest_algorithm': 'sha256',
                               'validator_template': 'sha256:{digest}'}
                              for name, content in sorted({**generated_assets, 'prepared.bin': generated_model[0]}.items())]}
            generated_geometry_path = tmp_path / 'generated-geometry.json'
            generated_geometry_path.write_bytes(canonical_bytes(generated_geometry))
            generated_geometry_request = {'protocol_version': '1', 'operation': 'acquire',
                'idempotency_key': 'generated-geometry', 'target': drive['operation_id'],
                'arguments': {'acquisition': {'drive_selection_id': drive['operation_id'],
                                            'operation_geometry': generated_geometry}}}
            generated_measurement = launch('qualify', '--operation-plan', str(generated_geometry_path),
                '--drive-selection', drive['operation_id'], '--key', 'generated-geometry', expected_code=2)
            generated_measurement_record = json.loads((tmp_path / 'state/operations'
                / (generated_measurement['operation_id'] + '.json')).read_bytes())['record']
            assert generated_measurement['state'] == 'PAUSED' and generated_measurement_record['phase'] == 'EMPTY'
            generated_connection = launch('connect', '--source', 'ollama', '--endpoint',
                f'http://127.0.0.1:{server.server_port}', '--public', '--key', 'generated-connection')
            preparation = {'composition_request': generated_composition_request, 'geometry_request': generated_geometry_request}
            preparation_path = tmp_path / 'generated-preparation.json'
            preparation_path.write_bytes(canonical_bytes(preparation))
            prior_records = {path: path.read_bytes() for path in (tmp_path / 'state/operations').glob('op-*.json')}
            def cartridge_snapshot():
                return {str(path.relative_to(cartridge)): hashlib.sha256(path.read_bytes()).hexdigest()
                        for path in cartridge.rglob('*') if path.is_file()}
            before_join = cartridge_snapshot()
            generated_args = ['select-model', '--connection', generated_connection['operation_id'],
                '--model', 'fixture/generated:latest', '--preparation', str(preparation_path)]
            joined = launch(*generated_args, '--key', 'generated-selected')
            assert joined['state'] == 'SUCCEEDED'
            result = joined['result']
            assert result['source_lock']['identity'] is None
            assert result['source_lock']['immutable_revision'] == 'sha256:' + hashlib.sha256(generated_manifest()).hexdigest()
            assert result['downloaded_bytes'] == 0 and result['execution_compatibility'] == 'NOT_VERIFIED'
            assert result['preparation']['composition_head'] == generated_composition['operation']['result']['composition_head']
            assert result['preparation']['geometry_operation_id'] == generated_measurement['operation_id']
            assert result['preparation']['geometry_digest'] == digest_bytes(canonical_bytes(generated_geometry))
            assert result['preparation']['source_lock_digest'] == digest_bytes(canonical_bytes(result['source_lock']))
            after_requests = list(requests)
            assert launch(*generated_args, '--key', 'generated-selected') == joined
            assert requests == after_requests
            assert cartridge_snapshot() == before_join
            assert all(path.read_bytes() == payload for path, payload in prior_records.items())
            generated_model[0] = b'z' * 32
            wrong_source = launch(*generated_args, '--key', 'generated-wrong-source', expected_code=1)
            assert wrong_source['error']['code'] == 'SOURCE_REVISION_CHANGED'
            assert 'committed preparation outputs' in wrong_source['error']['detail']
            generated_model[0] = weights[:32]
            preparation['composition_request']['arguments']['composition']['recipe'] = recipe
            preparation_path.write_bytes(canonical_bytes(preparation))
            wrong_request = launch(*generated_args, '--key', 'generated-wrong-request', expected_code=1)
            assert wrong_request['error']['code'] == 'INVALID_REQUEST'
            preparation['composition_request']['arguments']['composition']['recipe'] = generated_recipe
            missing_geometry_request = json.loads(canonical_bytes(generated_geometry_request))
            missing_geometry_request['idempotency_key'] = 'generated-geometry-unmeasured'
            control = CanonicalBroker(tmp_path / 'state/operations')
            missing_geometry = control.issue(missing_geometry_request)
            control.pause(missing_geometry['operation_id'])
            control.close()
            missing_record = tmp_path / 'state/operations' / (missing_geometry['operation_id'] + '.json')
            missing_bytes = missing_record.read_bytes()
            preparation['geometry_request'] = missing_geometry_request
            preparation_path.write_bytes(canonical_bytes(preparation))
            missing_profile = launch(*generated_args, '--key', 'generated-missing-profile', expected_code=1)
            assert missing_profile['error']['code'] == 'SOURCE_UNAVAILABLE'
            assert 'already published geometry profile' in missing_profile['error']['detail']
            assert missing_record.read_bytes() == missing_bytes
            assert cartridge_snapshot() == before_join
            assert all(path.read_bytes() == payload for path, payload in prior_records.items())
            assert not any('/blobs/' in path for method, path in requests)
            preparation['geometry_request'] = generated_geometry_request
            preparation_path.write_bytes(canonical_bytes(preparation))
            (evidence / 'generated-join.json').write_bytes(canonical_bytes({
                'request_reference': preparation, 'selection': joined, 'wrong_source': wrong_source,
                'wrong_request': wrong_request, 'missing_profile': missing_profile,
                'cartridge_before': before_join, 'cartridge_after': cartridge_snapshot()}))
            generated_evidence = evidence / 'generated-proof'
            shutil.copytree(cartridge / 'campaign', generated_evidence / 'cartridge/campaign')
            shutil.copytree(cartridge / 'captures', generated_evidence / 'cartridge/captures')
            shutil.copytree(tmp_path / 'state/operations', generated_evidence / 'operations')
            (generated_evidence / 'provider-manifest.json').write_bytes(generated_manifest())
            (generated_evidence / 'provider-requests.json').write_bytes(canonical_bytes(requests))
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
            assert len(plans) == 4
            assert sum(plan['value']['binding']['operation'] == generated_measurement['operation_id']
                       for plan in plans) == 1
            assert all(plan['value']['binding']['profiler_version'] == '7-retained-source-transfer'
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
            assert len(seals) == len(plans) and sum(seal['value']['atom_count'] for seal in seals) == len(fresh_atoms) + len(resume_atoms)
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
            # Q42/Q43: unresolved operation geometry executes the same retained profiler,
            # without source resolution, access claims or a payload-capable operation.
            geometry = {'source_lock': None, 'source_kind': 'ollama', 'revision_algorithm': 'sha256',
                'provenance': {'recipe_commit': 'f' * 40, 'upstream_revision': 'git-sha1:' + 'e' * 40},
                'artifacts': [{'path': 'empty.bin', 'size': 0, 'digest_algorithm': 'sha256',
                               'validator_template': 'sha256:{digest}'},
                              {'path': 'weight.safetensors', 'size': 65553, 'digest_algorithm': 'sha256',
                               'validator_template': 'sha256:{digest}'}]}
            geometry_file = tmp_path / 'operation-geometry.json'
            geometry_file.write_bytes(canonical_bytes(geometry))
            measured = launch('qualify', '--operation-plan', str(geometry_file),
                '--drive-selection', fresh_drive['operation_id'], '--key', 'geometry-profile', expected_code=2,
                expected_message='Drive check passed. Download remains paused.')
            geometry_record = json.loads((tmp_path / 'state/operations' / (measured['operation_id'] + '.json')).read_bytes())['record']
            proof = [event['payload']['source_qualification'] for event in geometry_record['events']
                     if event['payload'].get('source_qualification', {}).get('status') == 'PASS'][-1]
            geometry_complete = campaign_head(mount / 'drewwiberg-lacie/Cassette', proof['profile_key'])
            saved_plan = geometry_complete['value']['measurements']['binding']['plan']
            assert saved_plan['source_lock'] is None and saved_plan['source_identity_verification'] == 'NOT_RUN'
            assert saved_plan['operation_geometry'] == geometry
            assert saved_plan['operation_geometry_digest'] == digest_bytes(canonical_bytes(geometry))
            assert geometry_record['phase'] == 'EMPTY' and geometry_record['checkpoint'] == {}
            assert geometry_record['result'] is None and measured['state'] == 'PAUSED'
            assert requests == completed_requests
            assert launch('qualify', '--operation-plan', str(geometry_file),
                '--drive-selection', fresh_drive['operation_id'], '--key', 'geometry-profile', expected_code=2) == measured

            # Q42/Q44/Q51: measure retained source reads and separate destination writes.
            retained_geometry = json.loads(canonical_bytes(geometry))
            retained_geometry['source_storage'] = 'CARTRIDGE_RETAINED'
            retained_geometry['artifacts'][1]['size'] = 4 * 1024 * 1024 + 17
            retained_geometry['artifacts'].reverse()
            retained_geometry['artifacts'][1]['path'] = 'z-empty.bin'
            geometry_file.write_bytes(canonical_bytes(retained_geometry))
            control = CanonicalBroker(tmp_path / 'state/operations')
            retained_request = {'protocol_version': '1', 'operation': 'acquire',
                'idempotency_key': 'geometry-retained-profile', 'target': fresh_drive['operation_id'],
                'arguments': {'acquisition': {'operation_geometry': retained_geometry,
                    'drive_selection_id': fresh_drive['operation_id']}}}
            retained_id = control.issue(retained_request)['operation_id']
            control.request_hold(retained_id, 'retained-source-checkpoint')
            control.close()
            retained_record_path = tmp_path / 'state/operations' / (retained_id + '.json')
            copy_command = [sys.executable, '-B', '-m', 'cli', '--state', str(tmp_path / 'state'),
                'qualify', '--operation-plan', str(geometry_file), '--drive-selection', fresh_drive['operation_id'],
                '--key', 'geometry-retained-profile']
            copier_started_ns = time.time_ns()
            copier = subprocess.Popen(copy_command, cwd=Path(__file__).resolve().parents[1], env=child_environment,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                # Fresh retained bytes must exist before a retained-copy checkpoint can ACK.
                preparation_budget = physical_watchdog(16 * len(retained_geometry['artifacts']) + 12)
                preparation_deadline = time.monotonic() + preparation_budget
                profile_key = None
                cartridge_path = mount / 'drewwiberg-lacie/Cassette'
                while time.monotonic() < preparation_deadline:
                    if profile_key is None:
                        for pointer in (cartridge_path / 'campaign/heads').glob('download-profile-*'):
                            if (len(pointer.name) != len('download-profile-') + 64
                                    or pointer.stat().st_mtime_ns < copier_started_ns):
                                continue
                            candidate = campaign_head(cartridge_path, pointer.name)
                            if candidate is not None and candidate['value'].get('binding', {}).get('operation') == retained_id:
                                profile_key = pointer.name
                                break
                    copy_phase = (campaign_head(cartridge_path, profile_key + '-0-copy-extents')
                                  if profile_key is not None else None)
                    if copy_phase is not None and copy_phase['value']['binding'].get('source_extent_manifest'):
                        (tmp_path / 'retained-source-preparation.json').write_bytes(canonical_bytes({
                            'operation_id': retained_id, 'profile_key': profile_key,
                            'copy_extent_digest': copy_phase['digest'], 'preparation_watchdog_seconds': preparation_budget,
                            'ack_watchdog_seconds': 30, 'copy_phase_observed_ns': str(time.time_ns())}))
                        break
                    assert copier.poll() is None, copier.communicate()
                    time.sleep(.1)
                else:
                    raise AssertionError('retained source preparation did not reach the copy phase within its fixture watchdog')
                deadline = time.monotonic() + 30
                while time.monotonic() < deadline:
                    retained_events = json.loads(retained_record_path.read_bytes())['record']['events']
                    holds = [event['payload'] for event in retained_events if 'hold' in event['payload']]
                    if holds[-1] == {'hold': 'ACKNOWLEDGED', 'boundary': 'retained-source-checkpoint'}:
                        break
                    assert copier.poll() is None, copier.communicate()
                    time.sleep(.02)
                else:
                    raise AssertionError('retained source copy did not acknowledge its durable boundary')
                copier.kill()
                copier.communicate(timeout=5)
                copier_started_ns = time.time_ns()
                copier = subprocess.Popen(copy_command, cwd=Path(__file__).resolve().parents[1], env=child_environment,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                deadline = time.monotonic() + 30
                while time.monotonic() < deadline:
                    retained_events = json.loads(retained_record_path.read_bytes())['record']['events']
                    if any('source_profile_resume' in event['payload'] for event in retained_events):
                        break
                    assert copier.poll() is None, copier.communicate()
                    time.sleep(.02)
                else:
                    raise AssertionError('retained source copy did not restore its measured boundary')
                copier.kill()
                copier.communicate(timeout=5)
            finally:
                failure = sys.exc_info()[1]
                if copier.poll() is None:
                    copier.kill()
                    copy_output, copy_error = copier.communicate(timeout=5)
                elif failure is not None:
                    copy_output, copy_error = copier.communicate(timeout=5)
                if failure is not None:
                    evidence = tmp_path / 'failed-cli'
                    evidence.mkdir(exist_ok=True)
                    (evidence / ('copier-' + str(copier.pid) + '.json')).write_bytes(canonical_bytes({
                        'command': copy_command, 'pid': copier.pid, 'parent_pid': os.getpid(),
                        'started_ns': str(copier_started_ns), 'finished_ns': str(time.time_ns()),
                        'exit_code': copier.returncode, 'failure': repr(failure),
                        'stdout': copy_output, 'stderr': copy_error,
                        'operation_raw_hex': retained_record_path.read_bytes().hex()}))
            control = CanonicalBroker(tmp_path / 'state/operations')
            control.release_hold(retained_id, 'retained-source-checkpoint')
            control.close()
            retained_measured = launch('qualify', '--operation-plan', str(geometry_file),
                '--drive-selection', fresh_drive['operation_id'], '--key', 'geometry-retained-profile', expected_code=2)
            retained_record = json.loads((tmp_path / 'state/operations' /
                (retained_measured['operation_id'] + '.json')).read_bytes())['record']
            retained_proof = [event['payload']['source_qualification'] for event in retained_record['events']
                             if event['payload'].get('source_qualification', {}).get('status') == 'PASS'][-1]
            cartridge = mount / 'drewwiberg-lacie/Cassette'
            retained_complete = campaign_head(cartridge, retained_proof['profile_key'])['value']
            retained_plan = retained_complete['measurements']['binding']['plan']
            assert retained_plan['source_lock'] is None
            assert retained_plan['source_storage'] == 'CARTRIDGE_RETAINED'
            assert retained_plan['working_set_bytes'] == retained_plan['retained_extent_logical_bytes']
            assert retained_complete['atom_count'] == 6
            assert len(retained_complete['retained_manifests']) == 4
            for reference in retained_complete['retained_manifests']:
                assert campaign_head(cartridge, reference['key'])['value']['status'] == 'RECLAIMED'
            source_size = retained_geometry['artifacts'][0]['size']
            assert retained_complete['measurements']['retained_source']['observed_source_read_bytes'] >= source_size
            profile_key = retained_proof['profile_key'].removesuffix('-complete')
            copy_atom = campaign_head(cartridge, profile_key + '-0-copy')['value']
            copy_measurement = copy_atom['measurement']
            copy_rows = trace_events(copy_measurement)
            source_rows = [row for row in copy_rows if row.get('role') == 'source_data' and row.get('kind') == 'read']
            assert {(row['offset'], row['returned_bytes']) for row in source_rows} == {
                (0, 4 * 1024 * 1024), (4 * 1024 * 1024, 17)}
            assert copy_measurement['trace_statistics']['interrupted_windows'] == 1
            assert not any(row.get('kind') == 'write' and row.get('role', '').startswith('source_') for row in copy_rows)
            assert copy_measurement['trace_statistics']['phases']['FRESH_WRITE_READBACK'][
                'source_to_durable_chunk_bytes_per_second']['samples'] == 2
            for role in ('source_data', 'source_state'):
                payload = b''.join(canonical_bytes(row) + b'\n' for row in copy_rows if row.get('role') != role)
                name = 'missing-' + role + '.jsonl'
                write_campaign_artifact(CapacityCoordinator(cartridge), 'retained-source-control', name, payload)
                reference = {'attempt': 'retained-source-control', 'name': name,
                             'bytes': len(payload), 'digest': digest_bytes(payload)}
                try:
                    source_profile_trace(cartridge, [reference], expected_data_writes=source_size,
                        expected_data_reads=source_size, revalidation=False,
                        expected_source_reads=source_size,
                        source_state_bytes=copy_atom['pattern']['source_state_bytes_per_range'],
                        record_base=2 * 64 * 1024)
                except CassetteError as refused:
                    assert refused.code == 'ROOT_INVALID'
                else:
                    raise AssertionError('raw source verifier accepted omitted retained-source reads')
            assert requests == completed_requests
            assert launch('qualify', '--operation-plan', str(geometry_file),
                '--drive-selection', fresh_drive['operation_id'], '--key', 'geometry-retained-profile', expected_code=2) == retained_measured
            # Q42/Q51: an in-process hold discards pending prefetched source ranges.
            control = CanonicalBroker(tmp_path / 'state/operations')
            live_request = {**retained_request, 'idempotency_key': 'retained-inprocess-hold'}
            live_id = control.issue(live_request)['operation_id']
            control.request_hold(live_id, 'retained-source-checkpoint')

            async def await_retained_copy(task, operation_id, label):
                budget = physical_watchdog(16 * len(retained_geometry['artifacts']) + 12)
                deadline = time.monotonic() + budget
                profile_key = None
                while time.monotonic() < deadline and not task.done():
                    if profile_key is None:
                        for pointer in (cartridge / 'campaign/heads').glob('download-profile-*'):
                            if len(pointer.name) != len('download-profile-') + 64:
                                continue
                            candidate = campaign_head(cartridge, pointer.name)
                            if candidate is not None and candidate['value'].get('binding', {}).get('operation') == operation_id:
                                profile_key = pointer.name
                                break
                    head = campaign_head(cartridge, profile_key + '-0-copy-extents') if profile_key else None
                    if head is not None and head['value']['binding'].get('source_extent_manifest'):
                        (tmp_path / (label + '-preparation.json')).write_bytes(canonical_bytes({
                            'operation_id': operation_id, 'profile_key': profile_key,
                            'copy_extent_digest': head['digest'], 'preparation_watchdog_seconds': budget,
                            'observed_ns': str(time.time_ns())}))
                        return
                    await asyncio.sleep(.02)
                if task.done():
                    await task
                raise AssertionError(label + ' did not reach its retained-copy phase within the preparation watchdog')

            async def release_live_copy():
                task = asyncio.create_task(control.start_download(live_request, qualification_only=True))
                try:
                    await await_retained_copy(task, live_id, 'inprocess-hold')
                    deadline = time.monotonic() + 30
                    while time.monotonic() < deadline and not task.done():
                        holds = [event['payload'] for event in control.events(live_id) if 'hold' in event['payload']]
                        if holds[-1] == {'hold': 'ACKNOWLEDGED', 'boundary': 'retained-source-checkpoint'}:
                            control.release_hold(live_id, 'retained-source-checkpoint')
                            break
                        await asyncio.sleep(.02)
                    else:
                        raise AssertionError('in-process retained copy did not acknowledge its durable boundary')
                    completion_budget = physical_watchdog(60 * len(retained_geometry['artifacts']) + 6)
                    return await asyncio.wait_for(task, timeout=completion_budget)
                finally:
                    if not task.done():
                        task.cancel()
                    await asyncio.gather(task, return_exceptions=True)

            try:
                live_result = asyncio.run(release_live_copy())
                assert live_result['state'] == 'PAUSED'
                live_proof = [event['payload']['source_qualification'] for event in control.events(live_id)
                              if event['payload'].get('source_qualification', {}).get('status') == 'PASS'][-1]
                live_key = live_proof['profile_key'].removesuffix('-complete')
                live_copy = campaign_head(cartridge, live_key + '-0-copy')['value']['measurement']
                assert live_copy['observed_source_read_bytes'] == source_size + 17
                assert live_copy['trace_statistics']['interrupted_windows'] == 1
            finally:
                control.close()
            # Q42/Q44/Q51: a timed-out client cannot close a handler's source descriptor.
            control = CanonicalBroker(tmp_path / 'state/operations')
            late_request = {**retained_request, 'idempotency_key': 'retained-source-timeout'}
            late_id = control.issue(late_request)['operation_id']
            gate, reading = threading.Event(), threading.Event()
            target = {}
            real_read, real_connect = os.pread, socket.socket.connect
            timeout_events = tmp_path / 'source-timeout-events.jsonl'
            event_lock = threading.Lock()

            def observe_timeout(event, **fields):
                row = {'event': event, 'wall_ns': str(time.time_ns()),
                    'monotonic_ns': str(time.monotonic_ns()), 'thread': str(threading.get_ident()), **fields}
                with event_lock, timeout_events.open('a') as log:
                    log.write(json.dumps(row) + '\n')

            def source_handle_state():
                if 'fd' not in target:
                    return {'handler_read_started': reading.is_set()}
                try:
                    metadata = os.fstat(target['fd'])
                    return {'handler_read_started': reading.is_set(), 'fd': target['fd'],
                        'inode': str(metadata.st_ino), 'expected_inode': str(target['inode']),
                        'same_inode': metadata.st_ino == target['inode']}
                except OSError as error:
                    return {'handler_read_started': reading.is_set(), 'fd': target['fd'], 'error': repr(error)}

            def copy_source_inode():
                if 'profile' not in target:
                    for path in (cartridge / 'campaign/heads').iterdir():
                        head = campaign_head(cartridge, path.name)['value']
                        if head.get('binding', {}).get('operation') == late_id:
                            target['profile'] = path.name
                            break
                key = target.get('profile')
                if key and campaign_head(cartridge, key + '-0-copy-extents'):
                    return campaign_head(cartridge, key + '-0-extents')['value']['identities']['state']['inode']

            def slow_read(fd, count, offset):
                inode = copy_source_inode()
                if inode and os.fstat(fd).st_ino == inode and not reading.is_set():
                    target.update(fd=fd, inode=inode, handler_enter_ns=time.monotonic_ns())
                    observe_timeout('handler_gate_enter', fd=fd, inode=str(inode),
                        requested_bytes=count, offset=offset, gate_seconds=5)
                    reading.set()
                    released = gate.wait(5)
                    observe_timeout('handler_gate_return', released=released, **source_handle_state())
                    if not released:
                        raise TimeoutError('owned fixture source gate was not released')
                return real_read(fd, count, offset)

            def short_connect(handle, address):
                observe_timeout('socket_connect_start', host=address[0], port=address[1])
                result = real_connect(handle, address)
                inode = copy_source_inode() if address[0] == '127.0.0.1' else None
                if inode:
                    handle.settimeout(1.0)
                observe_timeout('socket_connect_return', host=address[0], port=address[1],
                    retained_source_inode=str(inode) if inode else None, timeout_seconds=handle.gettimeout())
                return result

            async def time_out_source():
                task = asyncio.create_task(control.start_download(late_request, qualification_only=True))
                try:
                    await await_retained_copy(task, late_id, 'source-timeout')
                    setup_budget = physical_watchdog(6)
                    observe_timeout('copy_phase_observed', handler_setup_seconds=setup_budget,
                        observation_seconds=10, **source_handle_state())
                    setup_deadline = time.monotonic() + setup_budget
                    while not reading.is_set() and not task.done() and time.monotonic() < setup_deadline:
                        await asyncio.sleep(.02)
                    if not reading.is_set():
                        raise AssertionError('source-timeout handler did not enter its gated read within the setup watchdog')
                    # The ten-second observation measures the gated read, not earlier durable setup.
                    deadline = target['handler_enter_ns'] / 1e9 + 10
                    observe_timeout('handler_observation_started', handler_enter_ns=str(target['handler_enter_ns']),
                        observation_seconds=10, **source_handle_state())
                    observed_read = False
                    while time.monotonic() < deadline and not task.done():
                        if reading.is_set():
                            if not observed_read:
                                observe_timeout('handler_read_seen_by_observer', **source_handle_state())
                                observed_read = True
                            failed = [campaign_head(cartridge, path.name)['value']
                                      for path in (cartridge / 'campaign/heads').iterdir()
                                      if path.name.endswith('-capture')]
                            if any(value.get('operation_id') == late_id and value.get('status') == 'INCOMPLETE'
                                   and value.get('error', {}).get('code') == 'SOURCE_UNAVAILABLE' for value in failed):
                                observe_timeout('incomplete_capture_observed', **source_handle_state())
                                assert os.fstat(target['fd']).st_ino == target['inode']
                                break
                        await asyncio.sleep(.02)
                    else:
                        observe_timeout('observation_failed', task_done=task.done(), **source_handle_state())
                        raise AssertionError('source timeout did not reach its still-open handler boundary')
                except BaseException as error:
                    observe_timeout('fixture_exception', error=repr(error), **source_handle_state())
                    raise
                finally:
                    observe_timeout('gate_release', **source_handle_state())
                    gate.set()
                    completion_budget = physical_watchdog(60 * len(retained_geometry['artifacts']) + 6)
                    try:
                        result = await asyncio.wait_for(task, timeout=completion_budget)
                    finally:
                        record_path = tmp_path / 'state/operations' / (late_id + '.json')
                        raw = record_path.read_bytes()
                        observe_timeout('task_drained', task_done=task.done(),
                            record_sha256=hashlib.sha256(raw).hexdigest(), **source_handle_state())
                        (tmp_path / 'source-timeout-observation.json').write_bytes(canonical_bytes({
                            'operation_id': late_id, 'task_done': task.done(), 'raw_record_hex': raw.hex(),
                            'event_log_sha256': hashlib.sha256(timeout_events.read_bytes()).hexdigest(),
                            'final_source_handle': source_handle_state()}))
                return result

            try:
                with monkeypatch.context() as io:
                    io.setattr(os, 'pread', slow_read)
                    io.setattr(socket.socket, 'connect', short_connect)
                    late_result = asyncio.run(time_out_source())
                assert late_result['state'] == 'PAUSED'
                assert control.events(late_id)[-1]['payload']['error']['code'] == 'SOURCE_UNAVAILABLE'
            finally:
                gate.set()
                control.close()
            geometry_file.write_bytes(canonical_bytes(geometry))
            control = CanonicalBroker(tmp_path / 'state/operations')
            geometry_request = {'protocol_version': '1', 'operation': 'acquire', 'idempotency_key': 'geometry-no-payload',
                'target': fresh_drive['operation_id'], 'arguments': {'acquisition': {
                    'operation_geometry': geometry, 'drive_selection_id': fresh_drive['operation_id']}}}
            try:
                for limits in ({}, {'qualification_only': True, 'header_only': True},
                               {'qualification_only': True, 'header_json_bytes': []}):
                    try:
                        asyncio.run(control.start_download(geometry_request, **limits))
                    except CassetteError as error:
                        assert error.code == 'INVALID_REQUEST'
                    else:
                        raise AssertionError('unresolved geometry entered a payload/header path')
            finally:
                control.close()
            assert not (tmp_path / 'state/operations' / (CanonicalBroker.operation_id(geometry_request) + '.json')).exists()
            for change in ('source-lock', 'duplicate', 'unsafe', 'unknown-variable', 'empty-provenance', 'bad-size',
                           'unsupported-digest', 'large-git', 'unicode-validator', 'whitespace-validator'):
                invalid = json.loads(canonical_bytes(geometry))
                if change == 'source-lock':
                    invalid['source_lock'] = selected['result']['source_lock']
                elif change == 'duplicate':
                    invalid['artifacts'].append(invalid['artifacts'][0])
                elif change == 'unsafe':
                    invalid['artifacts'][0]['path'] = '../outside'
                elif change == 'unknown-variable':
                    invalid['artifacts'][0]['validator_template'] = '{source-secret}'
                elif change == 'empty-provenance':
                    invalid['provenance'] = {}
                elif change == 'unsupported-digest':
                    invalid['artifacts'][0]['digest_algorithm'] = 'blake3'
                elif change == 'large-git':
                    invalid['artifacts'][0].update(digest_algorithm='git-sha1', size=4 * 1024 * 1024 + 1)
                elif change == 'unicode-validator':
                    invalid['artifacts'][0]['validator_template'] = 'sha256:{digest}\u2713'
                elif change == 'whitespace-validator':
                    invalid['artifacts'][0]['validator_template'] = 'sha256:{digest} '
                else:
                    invalid['artifacts'][0]['size'] = True
                geometry_file.write_bytes(canonical_bytes(invalid))
                assert launch('qualify', '--operation-plan', str(geometry_file),
                    '--drive-selection', fresh_drive['operation_id'], '--key', 'invalid-geometry-' + change,
                    expected_code=1)['error']['code'] == 'INVALID_REQUEST'
            geometry_file.write_bytes(canonical_bytes({**geometry, 'provenance': {'recipe_commit': 'a' * 40}}))
            assert launch('qualify', '--operation-plan', str(geometry_file),
                '--drive-selection', fresh_drive['operation_id'], '--key', 'geometry-profile',
                expected_code=1)['error']['code'] == 'IDEMPOTENCY_CONFLICT'
            for label, payload in (('deep-json', b'[' * 1200 + b'0' + b']' * 1200),
                                   ('oversized-control', b' ' * (4 * 1024 * 1024 + 1))):
                geometry_file.write_bytes(payload)
                refused = launch('qualify', '--operation-plan', str(geometry_file),
                    '--drive-selection', fresh_drive['operation_id'], '--key', label, expected_code=1)
                assert refused['error']['code'] == 'INVALID_REQUEST'
                assert ('acquisition' in refused['error']['detail'] if label == 'deep-json'
                        else 'control bytes' in refused['error']['detail'])
            assert requests == completed_requests
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
            # Q43/Q60: reconnect invalidates the old measurement, while the same preparation resumes.
            before_composition_requests = list(requests)
            reconnect_request, reconnect_id, reconnect_args, reconnect_path, stale_key, stale = interrupt_composition(
                signal.SIGKILL, 'composition-reconnect')
            subprocess.run(['/usr/bin/hdiutil', 'detach', str(mount), '-quiet'], check=True, capture_output=True)
            attached = False
            remounted = subprocess.run(['/usr/bin/hdiutil', 'attach', '-nobrowse', '-plist', str(image)],
                                       check=True, capture_output=True)
            mount = next(Path(item['mount-point']) for item in plistlib.loads(remounted.stdout)['system-entities']
                         if 'mount-point' in item)
            attached = True
            cartridge = mount / 'drewwiberg-lacie/Cassette'
            # Q6: a relative owner spelling cannot escape through Path.relative_to as ValueError.
            control = CanonicalBroker(tmp_path / 'state/operations')
            relative_owner = CapacityCoordinator(Path(os.path.relpath(cartridge, Path.cwd())))
            before_relative = reconnect_path.read_bytes()
            try:
                try:
                    asyncio.run(control._capture_composition_profile(reconnect_request, relative_owner,
                        select_external_apfs_volume(volume['volume_uuid']), capture_key=stale_key, uncached_source=True))
                except CassetteError as error:
                    assert error.code == 'ROOT_INVALID'
                    assert error.detail == 'generation capture differs from its exact request or path'
                else:
                    raise AssertionError('relative capture owner unexpectedly reused the stale context')
            finally:
                control.close()
            assert reconnect_path.read_bytes() == before_relative
            assert campaign_head(cartridge, stale_key) == stale
            recovered = launch(*reconnect_args, expected_code=1)
            assert recovered['operation']['operation_id'] == reconnect_id
            assert recovered['operation']['state'] == 'SUCCEEDED'
            assert recovered['source_qualification']['status'] == 'FAIL'
            assert 'complete fresh canonical composition' in recovered['source_qualification']['error']['detail']
            succeeded_bytes = reconnect_path.read_bytes()
            attempts = [event['payload']['composition_capture']
                        for event in json.loads(succeeded_bytes)['record']['events']
                        if 'composition_capture' in event['payload']]
            assert len(attempts) == 1 and attempts[0] != stale_key
            continued = campaign_head(cartridge, attempts[0])
            assert continued['value']['status'] == 'CAPTURED'
            assert continued['value']['execution_mode'] == 'RESUME'
            assert stale['value']['context']['path'] != continued['value']['context']['path']
            assert stale['value']['context']['path']['volume_uuid'] == continued['value']['context']['path']['volume_uuid']
            assert campaign_head(cartridge, stale_key) == stale
            assert launch(*reconnect_args, expected_code=1) == recovered
            assert reconnect_path.read_bytes() == succeeded_bytes
            assert record_path.read_bytes() == original_acquisition
            # A fresh operation is a legal measurement on the current native path.
            fresh_args = [*composition_args[:-1], 'composition-reconnect-fresh']
            fresh = launch(*fresh_args)
            assert fresh['source_qualification']['status'] == 'PASS'
            assert requests == before_composition_requests
            evidence = tmp_path / 'composition-remount-fixture'
            shutil.copytree(cartridge / 'campaign', evidence / 'cartridge/campaign')
            shutil.copytree(cartridge / 'captures', evidence / 'cartridge/captures')
            (evidence / 'request.json').write_bytes(canonical_bytes(reconnect_request))
            (evidence / 'qualification.json').write_bytes(canonical_bytes(recovered))
            (evidence / 'fresh-qualification.json').write_bytes(canonical_bytes(fresh))
            # Q6/Q60: this labelled capture-metadata injection represents success before capture seal.
            terminal_path = tmp_path / 'state/operations' / (fresh['operation']['operation_id'] + '.json')
            terminal_bytes = terminal_path.read_bytes()
            terminal_key = fresh['source_qualification']['capture_key']
            sealed = campaign_head(cartridge, terminal_key)
            compare_campaign_head(CapacityCoordinator(cartridge), terminal_key, sealed['digest'],
                                  {'context': sealed['value']['context'], 'status': 'MEASURING'})
            unavailable = launch(*fresh_args, expected_code=1)
            assert unavailable['operation'] == fresh['operation']
            assert unavailable['source_qualification']['status'] == 'FAIL'
            error = unavailable['source_qualification']['error']
            assert error['code'] == 'SOURCE_UNAVAILABLE' and error['retryability'] == 'terminal'
            assert 'fresh composition request key' in error['detail']
            assert terminal_path.read_bytes() == terminal_bytes
            assert launch(*fresh_args, expected_code=1) == unavailable
            assert terminal_path.read_bytes() == terminal_bytes
            # Q6/Q43/Q60: the same terminal capture still needs a new request after reconnect.
            incomplete = campaign_head(cartridge, terminal_key)
            subprocess.run(['/usr/bin/hdiutil', 'detach', str(mount), '-quiet'], check=True, capture_output=True)
            attached = False
            remounted = subprocess.run(['/usr/bin/hdiutil', 'attach', '-nobrowse', '-plist', str(image)],
                                       check=True, capture_output=True)
            mount = next(Path(item['mount-point']) for item in plistlib.loads(remounted.stdout)['system-entities']
                         if 'mount-point' in item)
            attached = True
            cartridge = mount / 'drewwiberg-lacie/Cassette'
            current_path = drive_path_observation(select_external_apfs_volume(volume['volume_uuid']))['path']
            assert current_path != incomplete['value']['context']['path']
            assert current_path['volume_uuid'] == incomplete['value']['context']['path']['volume_uuid']
            unavailable_after_reconnect = launch(*fresh_args, expected_code=1)
            assert unavailable_after_reconnect == unavailable
            assert terminal_path.read_bytes() == terminal_bytes
            assert campaign_head(cartridge, terminal_key) == incomplete
            assert launch(*fresh_args, expected_code=1) == unavailable_after_reconnect
            assert terminal_path.read_bytes() == terminal_bytes
            assert campaign_head(cartridge, terminal_key) == incomplete
            # Exact request binding still decides before terminal guidance on a changed path.
            changed = {**incomplete['value'], 'context': {
                **incomplete['value']['context'], 'request_digest': 'blake3:' + 'f' * 64}}
            contradicted = compare_campaign_head(CapacityCoordinator(cartridge), terminal_key,
                                                incomplete['digest'], changed)
            wrong_request = launch(*fresh_args, expected_code=1)
            assert wrong_request['operation'] == fresh['operation']
            assert wrong_request['source_qualification']['error']['code'] == 'ROOT_INVALID'
            assert terminal_path.read_bytes() == terminal_bytes
            assert campaign_head(cartridge, terminal_key) == contradicted
            (evidence / 'terminal-capture-control.json').write_bytes(canonical_bytes({
                'scope': 'Store capture-metadata injection, not an actual post-success crash',
                'capture_key': terminal_key, 'sealed_digest': sealed['digest'], 'receipt': unavailable,
                'incomplete_head': incomplete, 'after_real_reconnect': unavailable_after_reconnect,
                'path_after_reconnect': current_path,
                'wrong_request_head': contradicted, 'wrong_request': wrong_request}))
        finally:
            if watcher is not None and watcher.poll() is None:
                watcher.terminate()
                watcher.communicate(timeout=10)
            if attached:
                mount.chmod(root_mode)
                subprocess.run(['/usr/bin/hdiutil', 'detach', str(mount), '-quiet'], check=True, capture_output=True)
            if sys.exc_info()[0] is None:
                image.unlink()
        assert all(weights not in path.read_bytes() for path in (tmp_path / 'state').rglob('*') if path.is_file())
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
