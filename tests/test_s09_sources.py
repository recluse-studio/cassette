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
from fixture_server import _FIXTURES, credential_sink_server, source_fixture_server
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
        "immutable": _FIXTURES["ollama"]["revision"], "identity": None,
        "artifact": "model.gguf", "payload": b"ollama-parameter-bytes",
        "asset": "template.txt", "asset_payload": b"{{ .Prompt }}",
        "scope": "ollama:registry:pull", "license": b"ollama-license", "license_acceptance": False,
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
    }
    if case["identity"] is not None:
        descriptor["expected_identity"] = case["identity"]
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
    """Q50/Q52: substitute three deterministic sources without a lifecycle fork or unbounded metadata read."""
    public_operations = {
        name for name, value in vars(SourceAdapter).items()
        if callable(value) and not name.startswith("_")
    }
    # Q52 now admits discovery; these five artifact operations retain their existing semantics.
    assert public_operations == {"discover", "resolve", "enumerate", "read_metadata", "open_range", "license_and_auth"}

    with source_fixture_server() as server:
        vault = {f"keychain:s09/{kind}": SECRET for kind in CASES}
        results = [asyncio.run(_acquire_boundary(kind, case, server, vault)) for kind, case in CASES.items()]
        for (kind, case), result in zip(CASES.items(), results, strict=True):
            _, _, resolved, artifacts, metadata, payload, requirements, before, after = result
            assert resolved.source_kind == kind
            assert resolved.immutable_revision == case["immutable"]
            assert resolved.identity == (None if kind in {"huggingface", "ollama"} else case["identity"])
            assert artifacts == resolved.artifacts
            assert [artifact.path for artifact in artifacts] == [case["artifact"]]
            assert artifacts[0].size == len(case["payload"])
            assert artifacts[0].digest == "sha256:" + hashlib.sha256(case["payload"]).hexdigest()
            expected_uri = (f"{server.base_url}/{case['locator']}/resolve/{case['immutable'][9:]}/{case['artifact']}"
                            if kind == "huggingface" else f"{server.base_url}/v2/{case['locator']}/blobs/{artifacts[0].digest}"
                            if kind == "ollama" else f"{server.base_url}/bytes/{kind}/{case['artifact']}")
            assert artifacts[0].range_uri == expected_uri
            expected_assets = (["LICENSE", case["asset"]] if kind == "huggingface" else
                               ["config.json", "layer-000001", "layer-000002"] if kind == "ollama" else [case["asset"]])
            assert [asset.path for asset in resolved.metadata_assets] == expected_assets
            asset = next(asset for asset in resolved.metadata_assets if asset.digest == "sha256:" + hashlib.sha256(case["asset_payload"]).hexdigest())
            assert asset.size == len(case["asset_payload"])
            assert asset.digest == "sha256:" + hashlib.sha256(case["asset_payload"]).hexdigest()
            assert payload == case["payload"][1:-1]
            if kind == "huggingface":
                assert metadata["identity"]["trust"] == "ABSENT"
                assert "value" not in metadata["identity"]
                assert metadata["format"]["trust"] == "ABSENT"
            elif kind == "tinker":
                assert metadata["identity"] == {
                    "value": case["identity"],
                    "trust": "DECLARED",
                    "authority": (
                        f"source:{kind}:claim:EVIDENCE_DIGESTED:fixture:{kind}:manifest"
                    ),
                }
                assert metadata["format"]["trust"] == "DECLARED"
                assert metadata["format"]["authority"].startswith(
                    f"source:{kind}:claim:PARSED:"
                )
            assert requirements.auth_scope == case["scope"]
            assert requirements.credential_required is (kind != "ollama")
            assert requirements.license_acceptance_required is case["license_acceptance"]
            expected_license = "sha256:" + hashlib.sha256(case["license"]).hexdigest()
            assert requirements.license_digest == resolved.license_digest == expected_license
            assert set(resolved.record()) == {"immutable_revision", "artifacts", "metadata_assets", "auth_scope", "license_digest"}
            assert set(resolved.record()["artifacts"][0]) == {"path", "size", "digest", "range_uri"}
            assert set(requirements.record()) == {"auth_scope", "credential_required", "license_digest", "license_acceptance_required"}
            assert before == after

        hub_requests = [row for row in server.requests if "huggingface-model" in row["path"]]
        assert len([row for row in hub_requests if row["path"].startswith("/api/models/")]) == 4
        assert [row["range"] for row in hub_requests if row["range"]] == ["bytes=0-7", f"bytes=1-{len(CASES['huggingface']['payload']) - 2}"]
        assert all(row["authorized"] and row["license_ref_present"] for row in hub_requests)
        ollama_requests = [request for request in server.requests if "/v2/library/ollama-model/" in request["path"]]
        assert [request["path"].split("/")[-2] for request in ollama_requests] == ["manifests", "manifests", "manifests", "blobs", "blobs", "manifests"]
        assert all(request["authorized"] and request["license_ref_present"] for request in ollama_requests)
        for kind in ("tinker",):
            operations = [request["path"].split("/")[-1] if request["path"].startswith("/source/") else "range" for request in server.requests if f"/{kind}/" in request["path"]]
            assert operations == ["resolve", "artifacts", "metadata", "range", "requirements"]
            assert all(request["authorized"] for request in server.requests if f"/{kind}/" in request["path"])
            assert all(request["license_ref_present"] for request in server.requests if f"/{kind}/" in request["path"])
            metadata_request = next(request for request in server.requests if request["path"] == f"/source/{kind}/metadata")
            assert metadata_request["query"]["range"] == [f"{CASES[kind]['artifact']}:0:8"]

        resolved = results[0][2]
        artifact = resolved.artifacts[0]
        requests_before_oversize = len(server.requests)
        with pytest.raises(CassetteError) as oversized:
            asyncio.run(results[0][1].read_metadata(resolved, ((artifact.path, 0, 8 * 1024 * 1024 + 1),)))
        assert oversized.value.code == "INVALID_REQUEST"
        assert len(server.requests) == requests_before_oversize
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
        assert changed_artifact.value.object_id == artifact.path
        server.artifact_size_override = None
        server.corrupt_ranges[("huggingface", "config.json", 0)] = 0
        with pytest.raises(CassetteError) as changed_git_blob:
            asyncio.run(results[0][1].resolve(results[0][0]))
        assert changed_git_blob.value.code == "SOURCE_REVISION_CHANGED"
        assert changed_git_blob.value.object_id == "config.json"
        assert "Git blob" in changed_git_blob.value.detail
        server.corrupt_ranges.clear()


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
        deferred = asyncio.run(adapter.resolve({**descriptor, "expected_identity": "blake3:" + "0" * 64}))
        assert deferred.identity is None
        other_descriptor, other_adapter, *_ = results[1]
        vault[other_descriptor["credential_ref"]] = SECRET
        with pytest.raises(CassetteError) as mismatch:
            asyncio.run(other_adapter.resolve({**other_descriptor, "expected_identity": "sha256:" + "0" * 64}))
        assert mismatch.value.code == "IDENTITY_MISMATCH"

        resolved = results[0][2]
        artifact = resolved.artifacts[0]
        with credential_sink_server(CASES["huggingface"]["payload"], '"transport-object-etag"') as sink:
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
            server.linked_validator_override = '"changed-source-etag"'
            with pytest.raises(CassetteError) as changed_redirect:
                asyncio.run(adapter.open_range(redirected, redirected.artifacts[0], 0,
                    redirected.artifacts[0].size, redirected.artifacts[0].validator))
            assert changed_redirect.value.code == "SOURCE_REVISION_CHANGED"
            assert len(sink.requests) == 1
            server.linked_validator_override = None
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
    for path in (path for path in REPO.glob("*.py") if path.name not in {"sources.py", "cli.py"}):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.Match)):
                literals = {item.value for item in ast.walk(node) if isinstance(item, ast.Constant) and isinstance(item.value, str)}
                assert source_kinds.isdisjoint(literals), f"source-specific branch escaped sources.py: {path.name}"
