# test_s09_sources.py — S09 Q9/Q52 source-boundary fixtures; depends on errors.py, sources.py, tests/fixture_server.py.
"""Prove one five-operation acquisition surface over three distinct deterministic source wires."""

import ast
import asyncio
from dataclasses import fields, replace
import hashlib
import json
from pathlib import Path

import pytest

from errors import CassetteError
from fixture_server import credential_sink_server, source_fixture_server
from sources import SourceAdapter

REPO = Path(__file__).resolve().parent.parent
SECRET = "s09-fixture-secret-never-serialize"
CASES = {
    "huggingface": {
        "locator": "fixture/huggingface-model", "revision": "main",
        "immutable": "git-sha1:" + "1" * 40, "identity": "blake3:" + "a" * 64,
        "artifact": "model.safetensors", "payload": b"huggingface-parameter-bytes",
        "asset": "config.json", "asset_payload": b'{"model_type":"hf-fixture"}',
        "scope": "hf:read", "license": b"hf-license", "license_acceptance": True,
    },
    "ollama": {
        "locator": "library/ollama-model", "revision": "latest",
        "immutable": "sha256:" + "2" * 64, "identity": "blake3:" + "b" * 64,
        "artifact": "model.gguf", "payload": b"ollama-parameter-bytes",
        "asset": "template.txt", "asset_payload": b"{{ .Prompt }}",
        "scope": "ollama:pull", "license": b"ollama-license", "license_acceptance": False,
    },
    "tinker": {
        "locator": "training/tinker-export", "revision": "checkpoint-7",
        "immutable": "sha256:" + "3" * 64, "identity": "blake3:" + "c" * 64,
        "artifact": "weights.safetensors", "payload": b"tinker-parameter-bytes",
        "asset": "training.json", "asset_payload": b'{"step":7}',
        "scope": "tinker:weights:read", "license": b"tinker-license", "license_acceptance": True,
    },
}


async def _acquire_boundary(kind, case, server, vault):
    """One kind-blind caller drives all five Q52 operations in one fixed order."""
    credential_ref = f"keychain:s09/{kind}"
    descriptor = {
        "kind": kind,
        "locator": case["locator"],
        "revision": case["revision"],
        "credential_ref": credential_ref,
        "license_acceptance_ref": f"license:s09/{kind}",
        "expected_identity": case["identity"],
    }
    adapter = SourceAdapter(kind, server.base_url, vault.get)
    before = tuple(getattr(adapter, field.name) for field in fields(adapter))
    resolved = await adapter.resolve(descriptor)
    artifacts = await adapter.enumerate(resolved)
    metadata = await adapter.read_metadata(resolved, ((artifacts[0].path, 0, 8),))
    payload = await adapter.open_range(resolved, artifacts[0], 1, len(case["payload"]) - 2, artifacts[0].validator)
    requirements = await adapter.license_and_auth(resolved)
    after = tuple(getattr(adapter, field.name) for field in fields(adapter))
    return descriptor, adapter, resolved, artifacts, metadata, payload, requirements, before, after


def test_q52_five_operations_run_unchanged_against_each_source_fixture():
    """Q52 acceptance: substitute three deterministic sources without a lifecycle fork."""
    public_operations = {
        name for name, value in vars(SourceAdapter).items()
        if callable(value) and not name.startswith("_")
    }
    assert public_operations == {"resolve", "enumerate", "read_metadata", "open_range", "license_and_auth"}

    with source_fixture_server() as server:
        vault = {f"keychain:s09/{kind}": SECRET for kind in CASES}
        results = [asyncio.run(_acquire_boundary(kind, case, server, vault)) for kind, case in CASES.items()]
        for (kind, case), result in zip(CASES.items(), results, strict=True):
            _, _, resolved, artifacts, metadata, payload, requirements, before, after = result
            assert resolved.source_kind == kind
            assert resolved.immutable_revision == case["immutable"]
            assert resolved.identity == case["identity"]
            assert artifacts == resolved.artifacts
            assert [artifact.path for artifact in artifacts] == [case["artifact"]]
            assert artifacts[0].size == len(case["payload"])
            assert artifacts[0].digest == "sha256:" + hashlib.sha256(case["payload"]).hexdigest()
            assert artifacts[0].range_uri == f"{server.base_url}/bytes/{kind}/{case['artifact']}"
            assert [asset.path for asset in resolved.metadata_assets] == [case["asset"]]
            assert resolved.metadata_assets[0].size == len(case["asset_payload"])
            assert resolved.metadata_assets[0].digest == "sha256:" + hashlib.sha256(case["asset_payload"]).hexdigest()
            assert payload == case["payload"][1:-1]
            assert metadata["identity"] == {
                "value": case["identity"],
                "trust": "EVIDENCE_DIGESTED",
                "authority": f"fixture:{kind}:manifest",
            }
            assert requirements.auth_scope == case["scope"]
            assert requirements.credential_required is True
            assert requirements.license_acceptance_required is case["license_acceptance"]
            expected_license = "sha256:" + hashlib.sha256(case["license"]).hexdigest()
            assert requirements.license_digest == resolved.license_digest == expected_license
            assert set(resolved.record()) == {"immutable_revision", "artifacts", "metadata_assets", "auth_scope", "license_digest"}
            assert set(resolved.record()["artifacts"][0]) == {"path", "size", "digest", "range_uri"}
            assert set(requirements.record()) == {"auth_scope", "credential_required", "license_digest", "license_acceptance_required"}
            assert before == after

        for kind in CASES:
            operations = [request["path"].split("/")[-1] if request["path"].startswith("/source/") else "range" for request in server.requests if f"/{kind}/" in request["path"]]
            assert operations == ["resolve", "artifacts", "metadata", "range", "requirements"]
            assert all(request["authorized"] for request in server.requests if f"/{kind}/" in request["path"])
            assert all(request["license_ref_present"] for request in server.requests if f"/{kind}/" in request["path"])
            metadata_request = next(request for request in server.requests if request["path"] == f"/source/{kind}/metadata")
            assert metadata_request["query"]["range"] == [f"{CASES[kind]['artifact']}:0:8"]

        resolved = results[0][2]
        artifact = resolved.artifacts[0]
        with pytest.raises(CassetteError) as changed:
            asyncio.run(results[0][1].open_range(resolved, artifact, 0, 1, '"wrong-validator"'))
        assert changed.value.code == "SOURCE_REVISION_CHANGED"
        assert changed.value.object_id == artifact.path
        server.revision_override = "git-sha1:" + "9" * 40
        with pytest.raises(CassetteError) as changed_manifest:
            asyncio.run(results[0][1].enumerate(resolved))
        assert changed_manifest.value.code == "SOURCE_REVISION_CHANGED"
        assert changed_manifest.value.object_id == resolved.locator
        server.revision_override = None
        server.artifact_size_override = artifact.size + 1
        with pytest.raises(CassetteError) as changed_artifact:
            asyncio.run(results[0][1].enumerate(resolved))
        assert changed_artifact.value.code == "SOURCE_REVISION_CHANGED"
        assert changed_artifact.value.object_id == resolved.locator
        server.artifact_size_override = None


def test_q9_descriptor_and_records_remain_secret_free_after_expiry_and_move(tmp_path):
    """Q9 acceptance: immutable fixtures resolve while credentials remain opaque and source code stays confined."""
    with source_fixture_server() as server:
        vault = {f"keychain:s09/{kind}": SECRET for kind in CASES}
        results = [asyncio.run(_acquire_boundary(kind, case, server, vault)) for kind, case in CASES.items()]
        cartridge = tmp_path / "cartridge-a"
        cartridge.mkdir()
        for (kind, _), result in zip(CASES.items(), results, strict=True):
            descriptor, _, resolved, _, _, _, requirements, _, _ = result
            record = json.dumps({"descriptor": descriptor, "resolved": resolved.record(), "requirements": requirements.record()}, sort_keys=True)
            assert SECRET not in record
            assert descriptor["credential_ref"] in record
            (cartridge / f"{kind}.json").write_text(record, encoding="utf-8")
        moved = tmp_path / "cartridge-b"
        cartridge.rename(moved)
        assert all(SECRET not in path.read_text(encoding="utf-8") for path in moved.iterdir())
        assert all(SECRET not in json.dumps(request, sort_keys=True) for request in server.requests)

        before_expiry = len(server.requests)
        vault.clear()
        for (_, _), result in zip(CASES.items(), results, strict=True):
            descriptor, adapter, *_ = result
            with pytest.raises(CassetteError) as expired:
                asyncio.run(adapter.resolve(descriptor))
            assert expired.value.code == "AUTH_REQUIRED"
        assert len(server.requests) == before_expiry

        descriptor, adapter, *_ = results[0]
        with pytest.raises(CassetteError) as embedded:
            asyncio.run(adapter.resolve({**descriptor, "token": SECRET}))
        assert embedded.value.code == "INVALID_REQUEST"
        assert SECRET not in embedded.value.detail
        requests_before_wrong_adapter = len(server.requests)
        with pytest.raises(CassetteError) as wrong_adapter:
            asyncio.run(adapter.resolve({**descriptor, "kind": "ollama"}))
        assert wrong_adapter.value.code == "INVALID_REQUEST"
        assert len(server.requests) == requests_before_wrong_adapter
        requests_before_raw_ref = len(server.requests)
        raw_ref = {**descriptor, "credential_ref": SECRET}
        with pytest.raises(CassetteError) as not_opaque:
            asyncio.run(SourceAdapter("huggingface", server.base_url, lambda ref: ref).resolve(raw_ref))
        assert not_opaque.value.code == "INVALID_REQUEST"
        assert SECRET not in not_opaque.value.detail
        assert len(server.requests) == requests_before_raw_ref
        vault[descriptor["credential_ref"]] = SECRET
        with pytest.raises(CassetteError) as mismatch:
            asyncio.run(adapter.resolve({**descriptor, "expected_identity": "blake3:" + "0" * 64}))
        assert mismatch.value.code == "IDENTITY_MISMATCH"
        server.range_override = "https://attacker.invalid/model.safetensors"
        with pytest.raises(CassetteError) as foreign_range:
            asyncio.run(adapter.resolve(descriptor))
        assert foreign_range.value.code == "SOURCE_UNAVAILABLE"
        server.range_override = None

        resolved = results[0][2]
        artifact = resolved.artifacts[0]
        with credential_sink_server(CASES["huggingface"]["payload"], artifact.validator) as sink:
            server.range_override = f"{server.base_url}/redirect"
            server.range_redirect_target = f"{sink.base_url}/range"
            redirected = asyncio.run(adapter.resolve(descriptor))
            redirected_payload = asyncio.run(adapter.open_range(
                redirected,
                redirected.artifacts[0],
                0,
                redirected.artifacts[0].size,
                redirected.artifacts[0].validator,
            ))
            assert redirected_payload == CASES["huggingface"]["payload"]
            assert sink.requests == [{"authorization": None, "license_ref": None, "path": "/range"}]
            server.range_override = None
            server.range_redirect_target = None

            forged_artifact = replace(artifact, range_uri=f"{sink.base_url}/forged")
            forged_revision = replace(resolved, artifacts=(forged_artifact,))
            requests_before_forgery = len(sink.requests)
            with pytest.raises(CassetteError) as forged:
                asyncio.run(adapter.open_range(forged_revision, forged_artifact, 0, 1, forged_artifact.validator))
            assert forged.value.code == "SOURCE_UNAVAILABLE"
            assert len(sink.requests) == requests_before_forgery

            server.control_redirect_target = f"{sink.base_url}/control"
            with pytest.raises(CassetteError) as control_redirect:
                asyncio.run(adapter.resolve(descriptor))
            assert control_redirect.value.code == "SOURCE_UNAVAILABLE"
            assert len(sink.requests) == requests_before_forgery
            server.control_redirect_target = None

        with pytest.raises(CassetteError) as cleartext_remote:
            SourceAdapter("huggingface", "http://source.invalid", vault.get)
        assert cleartext_remote.value.code == "INVALID_REQUEST"

        requests_before_provider_failure = len(server.requests)
        def failed_provider(_credential_ref):
            raise RuntimeError(SECRET)
        with pytest.raises(CassetteError) as provider_failure:
            asyncio.run(SourceAdapter("huggingface", server.base_url, failed_provider).resolve(descriptor))
        assert provider_failure.value.code == "AUTH_REQUIRED"
        assert SECRET not in provider_failure.value.detail
        assert len(server.requests) == requests_before_provider_failure

    source_kinds = set(CASES)
    for path in (path for path in REPO.glob("*.py") if path.name != "sources.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.Match)):
                literals = {item.value for item in ast.walk(node) if isinstance(item, ast.Constant) and isinstance(item.value, str)}
                assert source_kinds.isdisjoint(literals), f"source-specific branch escaped sources.py: {path.name}"
