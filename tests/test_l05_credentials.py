# test_l05_credentials.py — source credential lifecycle proof (Q9/Q52); depends on broker.py, errors.py.
"""Exercise disposable source credentials through macOS and loopback provider boundaries."""

import errno
import base64
import hashlib
import fcntl
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import pty
import select
import subprocess
import shutil
import sys
import termios
import threading
import time
import uuid
from urllib.parse import parse_qs, urlparse

import pytest

from broker import MacOSSourceCredentialProvider
from errors import CassetteError


def test_q9_q52_cli_existing_ollama_login_signs_account_and_pull_grants_across_processes(tmp_path):
    """Q9/Q52 acquisition entry: existing account, bound key, revocation and same-origin pull authorization."""
    home = tmp_path / 'home'
    key = home / '.ollama/id_ed25519'
    key.parent.mkdir(parents=True)
    subprocess.run(['ssh-keygen', '-q', '-t', 'ed25519', '-N', '', '-f', str(key)], check=True)
    original_key = key.read_bytes()
    public = base64.b64decode(key.with_suffix('.pub').read_text().split()[1])
    public_der = tmp_path / 'public.der'
    public_der.write_bytes(bytes.fromhex('302a300506032b6570032100') + public[-32:])
    openssl = shutil.which('openssl')
    assert openssl is not None, 'the source-boundary fixture requires the installed OpenSSL verifier'
    state = tmp_path / 'state'
    controls = {'revoked': False, 'challenge': 'valid', 'name_field': 'Name'}
    requests = []
    grants = []
    token = 'fixture-ephemeral-registry-grant'
    config = b'{}'
    config_digest = 'sha256:' + hashlib.sha256(config).hexdigest()
    manifest = json.dumps({'schemaVersion': 2, 'config': {
        'mediaType': 'application/vnd.docker.container.image.v1+json', 'digest': config_digest, 'size': len(config)},
        'layers': [{'mediaType': 'application/vnd.ollama.image.model',
                    'digest': 'sha256:' + 'a' * 64, 'size': 16},
                   {'mediaType': 'application/vnd.ollama.image.license',
                    'digest': 'sha256:' + 'b' * 64, 'size': 7}]}).encode()

    def signature_matches(header, challenge):
        if not isinstance(header, str) or ':' not in header:
            return False
        encoded_public, encoded_signature = header.split(':', 1)
        try:
            if base64.b64decode(encoded_public, validate=True) != public:
                return False
            signature = base64.b64decode(encoded_signature, validate=True)
        except ValueError:
            return False
        message_file, signature_file = tmp_path / 'message', tmp_path / 'signature'
        message_file.write_bytes(challenge)
        signature_file.write_bytes(signature)
        checked = subprocess.run([openssl, 'pkeyutl', '-verify', '-pubin', '-keyform', 'DER',
            '-inkey', str(public_der), '-rawin', '-in', str(message_file), '-sigfile', str(signature_file)],
            capture_output=True)
        return checked.returncode == 0

    class Provider(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            return

        def _send(self, status, record, headers=None):
            payload = record if isinstance(record, bytes) else json.dumps(record).encode()
            self.send_response(status)
            self.send_header('Content-Length', str(len(payload)))
            for name, value in (headers or {}).items():
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(payload)

        def do_POST(self):
            requests.append(self.path)
            parsed = urlparse(self.path)
            valid = (parsed.path == '/api/me' and set(parse_qs(parsed.query)) == {'ts'}
                and signature_matches(self.headers.get('Authorization'), ('POST,' + self.path).encode()))
            self._send(200 if valid and not controls['revoked'] else 401,
                       {controls['name_field']: 'fixture-user'})

        def do_GET(self):
            requests.append(self.path)
            parsed = urlparse(self.path)
            if parsed.path == '/api/tags':
                self._send(200, {'models': [{'name': 'fixture:latest'}]})
            elif parsed.path == '/token':
                query = parse_qs(parsed.query)
                expected = b'GET,' + (endpoint + self.path).encode() + b',' + base64.b64encode(hashlib.sha256(b'').hexdigest().encode())
                valid = (set(query) == {'service', 'scope', 'ts', 'nonce'}
                    and query['scope'] == ['repository:library/fixture:pull']
                    and len(base64.urlsafe_b64decode(query['nonce'][0] + '==')) == 16
                    and signature_matches(self.headers.get('Authorization'), expected))
                grants.append(valid)
                self._send(200 if valid and not controls['revoked'] else 401, {'token': token})
            elif parsed.path.startswith('/v2/library/fixture/manifests/'):
                if self.headers.get('Authorization') == 'Bearer ' + token:
                    self._send(200, manifest)
                    return
                realm = 'http://127.0.0.1:1/token' if controls['challenge'] == 'other-origin' else endpoint + '/token'
                scope = 'repository:library/fixture:push' if controls['challenge'] == 'push' else 'repository:library/fixture:pull'
                challenge = f'Bearer realm="{realm}",service="fixture-registry",scope="{scope}"'
                if controls['challenge'] == 'malformed':
                    challenge = 'Bearer realm'
                self._send(401, {}, {'WWW-Authenticate': challenge})
            else:
                self._send(404, {})

    server = ThreadingHTTPServer(('127.0.0.1', 0), Provider)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    endpoint = f'http://127.0.0.1:{server.server_port}'
    environment = {**os.environ, 'HOME': str(home), 'PYTHONDONTWRITEBYTECODE': '1'}

    def cli(*arguments):
        result = subprocess.run([sys.executable, '-B', '-m', 'cli', '--state', str(state), *arguments],
            cwd=Path(__file__).resolve().parents[1], env=environment, capture_output=True, text=True, timeout=30)
        assert '-----BEGIN OPENSSH' not in result.stdout + result.stderr
        assert token not in result.stdout + result.stderr
        return result.returncode, json.loads(result.stdout)

    try:
        code, connection = cli('connect', '--source', 'ollama', '--endpoint', endpoint,
                               '--existing-login', '--key', 'account')
        assert code == 0
        assert connection['result']['authentication'] == {
            'account': 'fixture-user', 'authenticated': True, 'provider': 'ollama', 'scope': 'NOT_VERIFIED'}
        reference = connection['result']['credential_ref']
        assert reference.startswith('ollama-key:v1:blake3:')
        assert len(requests) == 1
        code, unsupported = cli('connect', '--source', 'huggingface', '--endpoint', endpoint,
                                '--existing-login', '--key', 'unsupported-existing-login')
        assert code == 1 and unsupported['error']['code'] == 'CAPABILITY_MISMATCH'
        assert len(requests) == 1
        assert cli('connect', '--source', 'ollama', '--endpoint', endpoint,
                   '--existing-login', '--key', 'account') == (0, connection)
        assert len(requests) == 1  # Replay returns the canonical receipt without another sign-in.
        account = connection['operation_id']
        controls['name_field'] = 'name'
        assert cli('models', '--connection', account, '--key', 'catalogue')[0] == 0
        code, selection = cli('select-model', '--connection', account, '--model', 'fixture:latest', '--key', 'selection')
        assert code == 0
        assert selection['result']['descriptor']['credential_ref'] == reference
        assert grants and all(grants)
        assert not any('/blobs/' in path for path in requests)
        for case in ('other-origin', 'push', 'malformed'):
            controls['challenge'] = case
            grants_before = len(grants)
            code, failed = cli('select-model', '--connection', account, '--model', 'fixture:latest', '--key', case)
            assert code == 1 and failed['error']['code'] == 'AUTH_REQUIRED'
            assert len(grants) == grants_before
        controls['challenge'] = 'valid'
        controls['revoked'] = True
        requests_before = len(requests)
        code, failed = cli('models', '--connection', account, '--key', 'revoked')
        assert code == 1 and failed['error']['code'] == 'AUTH_REQUIRED'
        assert len(requests) == requests_before + 1
        controls['revoked'] = False
        for label, contents in [('missing', None), ('invalid', b'invalid-key'), ('restored', original_key)]:
            if contents is None:
                key.unlink()
            else:
                key.write_bytes(contents)
                key.chmod(0o600)
            requests_before = len(requests)
            code, record = cli('models', '--connection', account, '--key', label)
            if label == 'restored':
                assert code == 0
            else:
                assert code == 1 and record['error']['code'] == 'AUTH_REQUIRED'
                assert len(requests) == requests_before
        key.unlink()
        key.with_suffix('.pub').unlink()
        subprocess.run(['ssh-keygen', '-q', '-t', 'ed25519', '-N', '', '-f', str(key)], check=True)
        requests_before = len(requests)
        code, failed = cli('models', '--connection', account, '--key', 'replaced')
        assert code == 1 and failed['error']['code'] == 'AUTH_REQUIRED'
        assert len(requests) == requests_before
        for secret in (original_key, key.read_bytes(), token.encode(), base64.b64encode(public)):
            assert all(secret not in path.read_bytes() for path in state.rglob('*') if path.is_file())
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _token_cli(state: Path, endpoint: str, token: str) -> tuple[int, str]:
    """Run the installed CLI with a controlling terminal so getpass can mask one input."""
    master, slave = pty.openpty()

    def attach_terminal() -> None:
        os.setsid()
        fcntl.ioctl(slave, termios.TIOCSCTTY, 0)

    process = subprocess.Popen(
        [sys.executable, "-B", "-m", "cli", "--state", str(state), "connect", "--source",
         "huggingface", "--endpoint", endpoint, "--token"],
        cwd=Path(__file__).resolve().parents[1], stdin=slave, stdout=slave, stderr=slave,
        close_fds=True, preexec_fn=attach_terminal,
    )
    os.close(slave)
    output = bytearray()
    sent = False
    deadline = time.monotonic() + 30
    try:
        while process.poll() is None or select.select([master], [], [], 0)[0]:
            if time.monotonic() >= deadline:
                process.kill()
                raise TimeoutError("interactive credential command exceeded 30 seconds")
            ready, _, _ = select.select([master], [], [], 0.1)
            if not ready:
                continue
            try:
                chunk = os.read(master, 65_536)
            except OSError as error:
                if error.errno == errno.EIO:
                    break
                raise
            if not chunk:
                break
            output.extend(chunk)
            if not sent and b"Read token" in output:
                os.write(master, token.encode("utf-8") + b"\n")
                sent = True
    finally:
        os.close(master)
    if not sent:
        raise AssertionError("CLI did not request a masked token")
    return process.wait(timeout=5), output.decode("utf-8")


def _json_from_terminal(output: str) -> dict:
    """Extract the one CLI JSON result after the getpass prompt."""
    return json.loads(output[output.index("{"):])


def _files_do_not_contain(root: Path, secret: str) -> None:
    """Assert that a source token did not enter the broker's durable state."""
    assert all(secret.encode("utf-8") not in path.read_bytes()
               for path in root.rglob("*") if path.is_file())


def test_q9_acquisition_entry_keychain_reference_is_bound_opaque_and_revocable():
    """Q9 acceptance: source tokens stay in Keychain while broker paths receive only opaque references."""
    provider = MacOSSourceCredentialProvider()
    source = "huggingface"
    endpoint = "https://huggingface.co"
    token = "test-" + uuid.uuid4().hex
    reference = provider.save(source, endpoint, token)
    try:
        assert reference.startswith("keychain:v1:")
        assert token not in reference
        assert provider.lookup_callback(source, endpoint)(reference) == token
        with pytest.raises(CassetteError) as mismatched:
            provider.lookup_callback(source, "https://other.example")(reference)
        assert mismatched.value.code == "CAPABILITY_MISMATCH"
        assert token not in str(mismatched.value)
        provider.revoke(reference, source, endpoint)
        with pytest.raises(CassetteError) as absent:
            provider.lookup_callback(source, endpoint)(reference)
        assert absent.value.code == "AUTH_REQUIRED"
        assert "absent or revoked" in absent.value.detail
        assert token not in str(absent.value)
    finally:
        try:
            provider.revoke(reference, source, endpoint)
        except CassetteError as error:
            assert error.code == "AUTH_REQUIRED"


def test_q9_q52_cli_token_connection_uses_keychain_across_processes_and_revocation(tmp_path):
    """Q9/Q52 acceptance: CLI token input is validated, Keychain-held, and rechecked at the provider."""
    token = "test-" + uuid.uuid4().hex
    invalid_token = "invalid-" + uuid.uuid4().hex
    provider_access = {"enabled": True}
    requests = []

    class Provider(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            authorized = self.headers.get("Authorization") == f"Bearer {token}"
            requests.append((self.path, authorized, provider_access["enabled"]))
            if not authorized or not provider_access["enabled"]:
                self.send_response(401)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            if self.path == "/api/whoami-v2":
                payload = {"name": "fixture-user"}
            elif self.path.startswith("/api/models?"):
                payload = [{"id": "fixture/private-model", "sha": "a" * 40,
                            "private": True, "gated": False}]
            else:
                self.send_response(404)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            body = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Provider)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    state = tmp_path / "state"
    endpoint = f"http://127.0.0.1:{server.server_port}"
    reference = None
    try:
        invalid_status, invalid_output = _token_cli(state, endpoint, invalid_token)
        invalid = _json_from_terminal(invalid_output)
        assert invalid_status == 1
        assert invalid["state"] == "FAILED"
        assert invalid["error"]["code"] == "AUTH_REQUIRED"
        assert invalid_token not in invalid_output
        _files_do_not_contain(state, invalid_token)

        status, output = _token_cli(state, endpoint, token)
        connection = _json_from_terminal(output)
        assert status == 0
        assert connection["state"] == "SUCCEEDED"
        assert connection["result"]["authentication"] == {
            "provider": "huggingface", "authenticated": True, "scope": "NOT_VERIFIED",
        }
        reference = connection["result"]["credential_ref"]
        assert reference.startswith("keychain:v1:")
        assert token not in output
        _files_do_not_contain(state, token)
        assert requests[-1] == ("/api/whoami-v2", True, True)

        catalogue = subprocess.run(
            [sys.executable, "-B", "-m", "cli", "--state", str(state), "models", "--connection",
             connection["operation_id"], "--query", "private", "--limit", "1"],
            cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=30,
        )
        assert catalogue.returncode == 0, catalogue.stderr + catalogue.stdout
        listed = json.loads(catalogue.stdout)
        assert listed["result"]["candidates"][0]["locator"] == "fixture/private-model"
        assert token not in catalogue.stdout + catalogue.stderr
        assert requests[-1][0].startswith("/api/models?") and requests[-1][1:] == (True, True)
        _files_do_not_contain(state, token)

        provider_access["enabled"] = False
        revoked_provider = subprocess.run(
            [sys.executable, "-B", "-m", "cli", "--state", str(state), "models", "--connection",
             connection["operation_id"], "--query", "private", "--limit", "1"],
            cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=30,
        )
        provider_failure = json.loads(revoked_provider.stdout)
        assert revoked_provider.returncode == 1
        assert provider_failure["error"]["code"] == "AUTH_REQUIRED"
        assert requests[-1][0].startswith("/api/models?") and requests[-1][1:] == (True, False)
        assert token not in revoked_provider.stdout + revoked_provider.stderr
        _files_do_not_contain(state, token)

        MacOSSourceCredentialProvider().revoke(reference, "huggingface", endpoint)
        reference = None
        requests_before = len(requests)
        missing_keychain = subprocess.run(
            [sys.executable, "-B", "-m", "cli", "--state", str(state), "models", "--connection",
             connection["operation_id"], "--query", "private", "--limit", "1"],
            cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=30,
        )
        missing_failure = json.loads(missing_keychain.stdout)
        assert missing_keychain.returncode == 1
        assert missing_failure["error"]["code"] == "AUTH_REQUIRED"
        assert len(requests) == requests_before
        assert token not in missing_keychain.stdout + missing_keychain.stderr
        _files_do_not_contain(state, token)
    finally:
        if reference is not None:
            try:
                MacOSSourceCredentialProvider().revoke(reference, "huggingface", endpoint)
            except CassetteError as error:
                assert error.code == "AUTH_REQUIRED"
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
