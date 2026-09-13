# test_l05_credentials.py — macOS Keychain credential lifecycle proof (Q9/Q52); depends on broker.py, errors.py.
"""Exercise disposable Keychain credentials through macOS and a loopback source boundary."""

import errno
import fcntl
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import pty
import select
import subprocess
import sys
import termios
import threading
import time
import uuid

import pytest

from broker import MacOSKeychainCredentialProvider
from errors import CassetteError


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
    provider = MacOSKeychainCredentialProvider()
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

        MacOSKeychainCredentialProvider().revoke(reference, "huggingface", endpoint)
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
                MacOSKeychainCredentialProvider().revoke(reference, "huggingface", endpoint)
            except CassetteError as error:
                assert error.code == "AUTH_REQUIRED"
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
