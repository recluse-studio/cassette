# test_l05_ollama.py — L05 Ollama registry source proof (Q9/Q52); depends on errors.py, sources.py.
"""Exercise Ollama's documented catalogue and registry wire without downloading a model."""

import asyncio
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading

import pytest

from errors import CassetteError
from sources import SourceAdapter


def test_q9_q52_ollama_catalogue_and_registry_resolution_are_separate_real_wires():
    """Q9/Q52: catalogue entries resolve through a digest-pinned registry manifest and blobs."""
    config = b'{"family":"fixture"}'
    model = b"ollama-model-bytes"
    license_bytes = b"fixture-license"
    config_digest = "sha256:" + hashlib.sha256(config).hexdigest()
    model_digest = "sha256:" + hashlib.sha256(model).hexdigest()
    license_digest = "sha256:" + hashlib.sha256(license_bytes).hexdigest()
    manifest = json.dumps({
        "schemaVersion": 2,
        "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
        "config": {"mediaType": "application/vnd.docker.container.image.v1+json",
                   "digest": config_digest, "size": len(config)},
        "layers": [
            {"mediaType": "application/vnd.ollama.image.model", "digest": model_digest,
             "size": len(model)},
            {"mediaType": "application/vnd.ollama.image.license", "digest": license_digest,
             "size": len(license_bytes)},
        ],
    }, sort_keys=True, separators=(",", ":")).encode()
    manifest_digest = "sha256:" + hashlib.sha256(manifest).hexdigest()
    blobs = {config_digest: config, model_digest: model, license_digest: license_bytes}
    requests = []

    class Registry(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            return

        def do_GET(self):
            requests.append((self.path, self.headers.get("Authorization"), self.headers.get("Range")))
            if self.path == "/api/tags":
                self._json({"models": [
                    {"name": "fixture-model:latest", "model": "fixture-model:latest",
                     "digest": manifest_digest[7:19], "size": len(model)},
                    {"name": "unrelated:latest", "model": "unrelated:latest",
                     "digest": "0" * 12, "size": 1},
                ]})
                return
            if self.path in {
                "/v2/library/fixture-model/manifests/latest",
                "/v2/library/fixture-model/manifests/" + manifest_digest,
            }:
                self._send(200, manifest, {"Content-Type": "application/vnd.docker.distribution.manifest.v2+json"})
                return
            prefix = "/v2/library/fixture-model/blobs/"
            if self.path.startswith(prefix):
                digest = self.path[len(prefix):]
                payload = blobs.get(digest)
                if payload is None:
                    self._send(404, b"")
                    return
                start, end = (int(value) for value in self.headers["Range"].removeprefix("bytes=").split("-", 1))
                self._send(206, payload[start:end + 1], {
                    "Content-Range": f"bytes {start}-{end}/{len(payload)}",
                })
                return
            self._send(404, b"")

        def _json(self, payload):
            self._send(200, json.dumps(payload, sort_keys=True).encode(), {"Content-Type": "application/json"})

        def _send(self, status, payload, headers=None):
            self.send_response(status)
            self.send_header("Content-Length", str(len(payload)))
            for name, value in (headers or {}).items():
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(payload)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Registry)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        adapter = SourceAdapter("ollama", f"http://127.0.0.1:{server.server_port}")
        catalogue = asyncio.run(adapter.discover("fixture", limit=1))
        assert catalogue == {
            "candidates": [{"kind": "ollama", "locator": "fixture-model:latest",
                            "revision": None, "private": None, "gated": None,
                            "downloadability": "NOT_VERIFIED"}],
            "next_cursor": None,
        }
        resolved = asyncio.run(adapter.resolve({"kind": "ollama", "locator": "fixture-model:latest"}))
        assert resolved.immutable_revision == manifest_digest
        assert resolved.identity is None
        assert [item.digest for item in resolved.artifacts] == [model_digest]
        assert [item.digest for item in resolved.metadata_assets] == [config_digest, license_digest]
        assert resolved.license_digest == license_digest
        assert asyncio.run(adapter.enumerate(resolved)) == resolved.artifacts
        model_artifact = next(item for item in resolved.artifacts if item.digest == model_digest)
        metadata = asyncio.run(adapter.read_metadata(resolved, ((model_artifact.path, 0, 6),)))
        assert metadata["total_bytes"]["value"] == len(model)
        assert asyncio.run(adapter.open_range(resolved, model_artifact, 0, 6,
                                               model_artifact.validator)) == model[:6]
        requirements = asyncio.run(adapter.license_and_auth(resolved))
        assert requirements.credential_required is False
        assert requirements.license_acceptance_required is False
        assert "/api/tags" in [path for path, _, _ in requests]
        assert "/v2/library/fixture-model/manifests/latest" in [path for path, _, _ in requests]
        assert "/v2/library/fixture-model/manifests/" + manifest_digest in [path for path, _, _ in requests]
        assert all(path != "/api/tags" or authorization is None for path, authorization, _ in requests)

        with pytest.raises(CassetteError) as opaque_private:
            asyncio.run(adapter._validate_credential("keychain:ollama/private"))
        assert opaque_private.value.code == "CAPABILITY_MISMATCH"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_q9_huggingface_credential_validation_rejects_a_missing_or_bad_whoami_record():
    """Q9: Hugging Face credential validation uses the provider's whoami endpoint and retains no secret."""
    class Provider(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            return

        def do_GET(self):
            if self.path != "/api/whoami-v2":
                self.send_error(404)
                return
            if self.headers.get("Authorization") != "Bearer hf-test-secret":
                self.send_response(401)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            payload = b'{"name":"fixture-user"}'
            self.send_response(200)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Provider)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        adapter = SourceAdapter("huggingface", f"http://127.0.0.1:{server.server_port}",
                                {"keychain:hf": "hf-test-secret"}.get)
        assert asyncio.run(adapter._validate_credential("keychain:hf")) == {
            "provider": "huggingface", "authenticated": True, "scope": "NOT_VERIFIED",
        }
        with pytest.raises(CassetteError) as rejected:
            asyncio.run(adapter._validate_credential("keychain:missing"))
        assert rejected.value.code == "AUTH_REQUIRED"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_q9_huggingface_resolution_refuses_non_lfs_model_content_before_any_payload_read():
    """Q9/Q50: a Git-tracked model file stops resolution before a model-bearing GET."""
    requests = []

    class Provider(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            return

        def do_GET(self):
            requests.append(self.path)
            if self.path.startswith("/api/models/fixture/model/revision/main"):
                payload = json.dumps({
                    "id": "fixture/model", "sha": "a" * 40, "private": False, "gated": False,
                    "siblings": [{"rfilename": "model.gguf", "size": 12, "blobId": "b" * 40}],
                }).encode()
                self.send_response(200)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            self.send_error(500)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Provider)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        adapter = SourceAdapter("huggingface", f"http://127.0.0.1:{server.server_port}")
        with pytest.raises(CassetteError) as rejected:
            asyncio.run(adapter.resolve({"kind": "huggingface", "locator": "fixture/model", "revision": "main"}))
        assert rejected.value.code == "METADATA_INSUFFICIENT"
        assert requests == ["/api/models/fixture/model/revision/main?blobs=true"]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
