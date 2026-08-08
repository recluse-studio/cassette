# fixture_server.py — deterministic Hugging Face, Ollama, and Tinker HTTP boundary for S09-S11; depends on (none).
"""Serve distinct source wires while retaining only sanitized request evidence."""

from contextlib import contextmanager
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
from urllib.parse import parse_qs, quote, unquote, urlparse

_SECRET = "s09-fixture-secret-never-serialize"
_SOURCE_FIELDS = (
    "identity", "total_bytes", "artifact_count", "artifact_digests", "format",
    "architecture", "total_parameters", "active_parameters", "dtype_quantization",
    "context", "modalities", "operators", "custom_code", "tokenizer", "processor",
    "template", "license", "gating", "revision_ancestry", "training_precision",
    "source_validators",
)


def _sha(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


_FIXTURES = {
    "huggingface": {
        "locator": "fixture/huggingface-model", "alias": "main", "revision": "git-sha1:" + "1" * 40,
        "identity": "blake3:" + "a" * 64, "auth_scope": "hf:read", "license": _sha(b"hf-license"),
        "format": "safetensors", "artifact": ("model.safetensors", b"huggingface-parameter-bytes", '"hf-v1"'),
        "asset": ("config.json", b'{"model_type":"hf-fixture"}', '"hf-config-v1"'),
    },
    "ollama": {
        "locator": "library/ollama-model", "alias": "latest", "revision": "sha256:" + "2" * 64,
        "identity": "blake3:" + "b" * 64, "auth_scope": "ollama:pull", "license": _sha(b"ollama-license"),
        "format": "gguf", "artifact": ("model.gguf", b"ollama-parameter-bytes", '"ollama-v1"'),
        "asset": ("template.txt", b"{{ .Prompt }}", '"ollama-template-v1"'),
    },
    "tinker": {
        "locator": "training/tinker-export", "alias": "checkpoint-7", "revision": "sha256:" + "3" * 64,
        "identity": "blake3:" + "c" * 64, "auth_scope": "tinker:weights:read", "license": _sha(b"tinker-license"),
        "format": "safetensors", "artifact": ("weights.safetensors", b"tinker-parameter-bytes", '"tinker-v1"'),
        "asset": ("training.json", b'{"step":7}', '"tinker-training-v1"'),
    },
}


def _artifact(kind: str, item: tuple[str, bytes, str]) -> dict:
    name, payload, validator = item
    uri = f"/bytes/{quote(kind, safe='')}/{quote(name, safe='')}"
    digest = _sha(payload)
    if kind == "huggingface":
        return {"rfilename": name, "size": len(payload), "lfs": {"sha256": digest[7:]}, "download_url": uri, "etag": validator}
    if kind == "ollama":
        return {"name": name, "size": len(payload), "digest": digest, "url": uri, "etag": validator}
    return {"key": name, "size_bytes": len(payload), "sha256": digest[7:], "download_url": uri, "validator": validator}


def _manifest(kind: str) -> dict:
    fixture = _FIXTURES[kind]
    artifact = _artifact(kind, fixture["artifact"])
    asset = _artifact(kind, fixture["asset"])
    if kind == "huggingface":
        return {"sha": fixture["revision"][9:], "cassette_identity": fixture["identity"], "siblings": [artifact], "metadata_siblings": [asset], "auth": {"scope": fixture["auth_scope"]}, "license": {"digest": fixture["license"]}}
    if kind == "ollama":
        return {"digest": fixture["revision"], "cassette": {"identity": fixture["identity"]}, "layers": [artifact], "assets": [asset], "scope": fixture["auth_scope"], "license_digest": fixture["license"]}
    return {"immutable_id": fixture["revision"], "provenance": {"identity": fixture["identity"]}, "files": [artifact], "metadata_files": [asset], "authorization": {"scope": fixture["auth_scope"]}, "license": {"sha256": fixture["license"]}}


def _replace_artifact_uri(kind: str, manifest: dict, uri: str) -> None:
    if kind == "huggingface":
        manifest["siblings"][0]["download_url"] = uri
    elif kind == "ollama":
        manifest["layers"][0]["url"] = uri
    else:
        manifest["files"][0]["download_url"] = uri


def _replace_revision(kind: str, manifest: dict, revision: str) -> None:
    if kind == "huggingface":
        manifest["sha"] = revision.removeprefix("git-sha1:")
    elif kind == "ollama":
        manifest["digest"] = revision
    else:
        manifest["immutable_id"] = revision


def _metadata(kind: str) -> dict:
    fixture = _FIXTURES[kind]
    artifact = fixture["artifact"]
    absent = {"trust": "ABSENT", "authority": f"fixture:{kind}:absent"}
    result = {field: dict(absent) for field in _SOURCE_FIELDS}
    result.update({
        "identity": {"value": fixture["identity"], "trust": "EVIDENCE_DIGESTED", "authority": f"fixture:{kind}:manifest"},
        "total_bytes": {"value": len(artifact[1]), "trust": "EVIDENCE_DIGESTED", "authority": f"fixture:{kind}:manifest"},
        "artifact_count": {"value": 1, "trust": "EVIDENCE_DIGESTED", "authority": f"fixture:{kind}:manifest"},
        "artifact_digests": {"value": [_sha(artifact[1])], "trust": "EVIDENCE_DIGESTED", "authority": f"fixture:{kind}:manifest"},
        "format": {"value": fixture["format"], "trust": "PARSED", "authority": f"fixture:{kind}:header"},
        "source_validators": {"value": {"etag": artifact[2]}, "trust": "EVIDENCE_DIGESTED", "authority": f"fixture:{kind}:response"},
        "conflicts": [],
    })
    wrapper = {"huggingface": "remote_metadata", "ollama": "model_info", "tinker": "evidence"}[kind]
    return {wrapper: result}


def _requirements(kind: str) -> dict:
    fixture = _FIXTURES[kind]
    if kind == "huggingface":
        return {"auth": {"scope": fixture["auth_scope"], "required": True}, "license": {"digest": fixture["license"], "acceptance_required": True}}
    if kind == "ollama":
        return {"scope": fixture["auth_scope"], "credential_required": True, "license_digest": fixture["license"], "license_acceptance_required": False}
    return {"authorization": {"scope": fixture["auth_scope"], "required": True}, "license": {"sha256": fixture["license"], "acceptance_required": True}}


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, _format, *_args):
        return

    def _send(self, status: int, payload: bytes, headers: dict[str, str] | None = None):
        self.send_response(status)
        self.send_header("Content-Length", str(len(payload)))
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(payload)

    def _json(self, payload: dict):
        self._send(200, json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(), {"Content-Type": "application/json"})

    def do_GET(self):
        parsed = urlparse(self.path)
        parts = parsed.path.strip("/").split("/")
        authorized = self.headers.get("Authorization") == f"Bearer {_SECRET}"
        self.server.requests.append({
            "path": parsed.path,
            "query": parse_qs(parsed.query),
            "range": self.headers.get("Range"),
            "if_match": self.headers.get("If-Match"),
            "authorized": authorized,
            "license_ref_present": self.headers.get("X-Cassette-License-Acceptance") is not None,
        })
        if not authorized:
            self._send(401, b"")
            return
        if len(parts) == 3 and parts[0] == "source" and parts[1] in _FIXTURES:
            kind, operation = parts[1], parts[2]
            query = parse_qs(parsed.query)
            fixture = _FIXTURES[kind]
            if query.get("locator") != [fixture["locator"]] or operation not in {"resolve", "artifacts", "metadata", "requirements"}:
                self._send(404, b"")
                return
            revision = query.get("revision", [""])[0]
            if operation == "resolve" and revision not in {"", fixture["alias"]}:
                self._send(409, b"")
                return
            if operation != "resolve" and revision != fixture["revision"]:
                self._send(409, b"")
                return
            response = _manifest(kind) if operation in {"resolve", "artifacts"} else _metadata(kind) if operation == "metadata" else _requirements(kind)
            if operation == "resolve" and self.server.range_override is not None:
                _replace_artifact_uri(kind, response, self.server.range_override)
            if operation == "artifacts" and self.server.revision_override is not None:
                _replace_revision(kind, response, self.server.revision_override)
            self._json(response)
            return
        if len(parts) == 3 and parts[0] == "bytes" and parts[1] in _FIXTURES:
            kind, name = parts[1], unquote(parts[2])
            fixture = _FIXTURES[kind]
            matches = [item for item in (fixture["artifact"], fixture["asset"]) if item[0] == name]
            if not matches:
                self._send(404, b"")
                return
            _, payload, validator = matches[0]
            if self.headers.get("If-Match") != validator:
                self._send(412, b"")
                return
            try:
                start, end = (int(value) for value in self.headers["Range"].removeprefix("bytes=").split("-", 1))
            except (KeyError, TypeError, ValueError):
                self._send(400, b"")
                return
            if start < 0 or end < start or end >= len(payload):
                self._send(416, b"")
                return
            self._send(206, payload[start:end + 1], {"Content-Range": f"bytes {start}-{end}/{len(payload)}", "ETag": validator})
            return
        self._send(404, b"")


@contextmanager
def source_fixture_server():
    """Run one deterministic local server and remove its thread at the context boundary."""
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    server.requests = []
    server.base_url = f"http://127.0.0.1:{server.server_port}"
    server.range_override = None
    server.revision_override = None
    thread = threading.Thread(target=server.serve_forever, name="s09-source-fixture", daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()
