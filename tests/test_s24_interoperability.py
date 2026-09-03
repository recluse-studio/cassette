# test_s24_interoperability.py — S24 protected traces, machine interoperability, delta, export, and removal fixture; depends on adapters, broker.py, compiler.py, errors.py, pager.py, schema, sources.py, store.py, tests/compiler_fixture.py, tests/fixture_server.py, tests/test_s17_broker.py, tests/test_s21_trainer.py, tools/capture_fixture.py, trainer.py.
"""Execute S24 through generated evidence, scratch cartridges, and loopback sources only."""

from __future__ import annotations

import asyncio
import ast
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import struct

import pytest

from adapters import NamedAdapter
from broker import AcquisitionContext, CanonicalBroker, ScheduledLease
from compiler import plan_export, plan_revision, prepare_revision
from compiler_fixture import artifact as compiler_artifact
from errors import CassetteError
import fixture_server
from fixture_server import source_fixture_server
import pager
import store as store_module
from schema.tables import ADAPTER_PROTOCOLS, DISPATCH_ROWS
from sources import SourceAdapter, TransferExtent, transfer_state_bytes
from store import (
    ArtifactIdentity,
    CapacityCoordinator,
    IdentityTuple,
    apply_revision_delta,
    canonical_bytes,
    create_revision_delta,
    create_repair_set,
    derive_root,
    digest_bytes,
    export_semantic_manifest,
    export_shape,
    import_export,
    import_safetensors,
    load_root,
    model_identity,
    page_locations,
    pin_generation,
    read_tensor,
    read_training_page,
    repair_set_shape,
    remove_revision,
    revision_delta_shape,
    revision_reachability,
    revision_removal_shape,
    rollback_generation,
)
from test_s17_broker import _profile, _request, _schedule
from test_s21_trainer import (
    RECOVERY_BATCH,
    SFT_BATCHES,
    _calibration_records,
    _compiled_parent,
    _quantized_parent,
    _train,
)
from tools.capture_fixture import capture
from trainer import adapter_merge_material, load_training_artifact


pytestmark = pytest.mark.skipif(
    platform.system() != "Darwin" or platform.machine() != "arm64",
    reason="S24 requires arm64 macOS, pinned MLX Metal, and F_FULLFSYNC",
)

REPO = Path(__file__).resolve().parent.parent
TRACE_PATH = REPO / "tests" / "fixtures" / "s24_teacher_trace.json"
_EXPORT_PLAN_BODY_FIELDS = (
    "version", "source_root", "source_identity", "target_schema", "mode",
    "semantic_binding", "delta_id", "adapter_rank", "adapter_scale",
)


def _trace() -> dict:
    return json.loads(TRACE_PATH.read_bytes())


def _s24_artifact(kind: str = "huggingface", mutate=None):
    corpus = _trace()

    def apply(document):
        inputs = corpus["certificate_inputs"]
        document["model"].update(
            architecture="S24Dense",
            config={"fixture": "s24", "hidden_size": 2},
        )
        document["evidence"] = deepcopy(inputs["evidence"])
        document["eta_rep"] = inputs["eta_rep"]
        document["rank_budget"] = inputs["rank_budget"]
        document["operation_bounds"] = deepcopy(inputs["operation_bounds"])
        document["operator_inventory"] = [deepcopy(corpus["operator_case"])]
        if mutate is not None:
            mutate(document)

    fixture = fixture_server._FIXTURES[kind]
    payload, material, document = compiler_artifact(
        kind,
        fixture["locator"],
        fixture["revision"],
        fixture["license"],
        fixture["artifact"][0],
        label=f"s24-generated-dense-{kind}",
        mutate_manifest=apply,
    )
    if kind == "ollama":
        material = replace(material, format_versions=(("gguf", "3"),))
    return payload, material, document


def _compiler_inputs(path: Path, material: IdentityTuple, operation_id: str) -> tuple[dict, dict]:
    descriptor = os.open(path, os.O_RDONLY)
    source = {
        "source_kind": material.source_kind,
        "source_alias": material.source_alias,
        "locator": material.canonical_locator,
        "requested_revision": material.requested_revision,
        "immutable_revision": material.immutable_revision,
        "identity": model_identity(material),
        "artifacts": [
            {"path": row.path, "size": row.size, "digest": row.digest}
            for row in material.artifacts
        ],
        "license_digest": material.license_digest,
    }
    return source, {
        material.artifacts[0].path: {
            "fd": descriptor,
            "offset": 0,
            "length": material.artifacts[0].size,
            "operation_id": operation_id,
        }
    }


def _extent(path: Path, length: int, operation_id: str) -> tuple[int, TransferExtent]:
    descriptor = os.open(path, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
    os.ftruncate(descriptor, length)
    return descriptor, TransferExtent(descriptor, 0, length, operation_id)


def _limit_available_bytes(monkeypatch, cartridge: Path, available_bytes: int) -> None:
    """Force the real coordinator's next statvfs measurement to one exact low-space value."""

    original = store_module.os.statvfs
    snapshot = original(cartridge)
    fragments = snapshot.f_frsize
    values = list(snapshot)
    values[3] = values[4] = available_bytes // fragments

    def limited(path):
        if Path(path).resolve() == cartridge.resolve():
            return os.statvfs_result(values)
        return original(path)

    monkeypatch.setattr(store_module.os, "statvfs", limited)


def _operation_id(label: str) -> str:
    return "op-" + digest_bytes(label.encode()).partition(":")[2]


def _f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def _expected_merged_tensors(
    cartridge: Path,
    base_root: str,
    child_root: str,
    artifact: dict,
) -> dict[str, bytes]:
    assert artifact["delta_precision"] == "FP32"
    merged = {}
    for base, delta in zip(artifact["base_pages"], artifact["delta_pages"], strict=True):
        envelope = json.loads(
            read_training_page(cartridge, child_root, delta["page_digest"])
        )
        adapter = struct.unpack("<6f", bytes.fromhex(envelope["payload_hex"]))
        quantized = struct.unpack("<6b", read_tensor(cartridge, base_root, base["tensor_id"]))
        values = []
        for row in range(2):
            for column in range(3):
                correction = _f32(adapter[3 + row] * adapter[column])
                values.append(_f32(float(quantized[row * 3 + column]) + correction))
        merged[base["tensor_id"]] = struct.pack("<6f", *values)
    return merged


def _machine_replay(
    tmp_path: Path,
    monkeypatch,
    kind: str,
    payload: bytes,
    material: IdentityTuple,
) -> tuple[dict, Path, CanonicalBroker]:
    fixture = fixture_server._FIXTURES[kind]
    monkeypatch.setitem(fixture, "identity", model_identity(material))
    cartridge = tmp_path / f"s24-{kind}-cartridge"
    cartridge.mkdir()
    incoming = cartridge / "incoming"
    incoming.mkdir()
    broker = CanonicalBroker(tmp_path / f"s24-{kind}-acquisition-log")
    request = {
        "protocol_version": "1",
        "operation": "prepare",
        "idempotency_key": f"s24-complete-machine-replay-{kind}",
        "target": f"cartridge:s24:{kind}",
        "arguments": {"source": {
            "kind": kind,
            "locator": fixture["locator"],
            "revision": fixture["alias"],
            "credential_ref": f"keychain:s24/{kind}",
            "license_acceptance_ref": f"license:s24/{kind}",
            "expected_identity": model_identity(material),
        }},
    }
    operation_id = broker.operation_id(request)
    artifact_path = incoming / material.artifacts[0].path
    state_path = incoming / f"{material.artifacts[0].path}.transfer"
    data_fd, data_extent = _extent(artifact_path, len(payload), operation_id)
    state_length = transfer_state_bytes(len(payload))
    state_fd, state_extent = _extent(state_path, state_length, operation_id)
    try:
        with source_fixture_server(
            artifact_overrides={kind: ((material.artifacts[0].path, payload, '"s24-v1"'),)}
        ) as server:
            context = AcquisitionContext(
                SourceAdapter(
                    kind,
                    server.base_url,
                    {f"keychain:s24/{kind}": fixture_server._SECRET}.get,
                ),
                CapacityCoordinator(cartridge),
                {material.artifacts[0].path: (data_extent, state_extent)},
                cartridge,
            )
            operation = asyncio.run(broker.run_acquisition(request, context))
    finally:
        os.close(data_fd)
        os.close(state_fd)
    return operation, cartridge, broker


def _store_snapshot(cartridge: Path) -> dict[str, str]:
    return {
        str(path.relative_to(cartridge)): digest_bytes(path.read_bytes())
        for path in cartridge.rglob("*")
        if path.is_file()
    }


def _reseal_export_manifest(manifest: dict, *, bind_source_history: bool = True) -> str:
    """Recompute an attacked portable package without borrowing store.py's manifest builder."""

    semantic = manifest["semantic_manifest"]
    source = manifest["source_revision"]["identity_material"]
    if bind_source_history and manifest["source_revision"]["revision_kind"] == "tuned":
        source["transform_manifest_digest"] = digest_bytes(
            canonical_bytes(semantic["ordered_deltas"])
        )
    source_identity = digest_bytes(canonical_bytes(source))
    semantic["source_identity"] = source_identity
    artifact_semantics = manifest["artifact_semantics"]
    if artifact_semantics is not None:
        artifact_semantics["source_identity"] = source_identity

    plan = manifest["plan"]
    plan["source_identity"] = source_identity
    plan["semantic_binding"] = digest_bytes(canonical_bytes(semantic))
    plan["plan_id"] = digest_bytes(canonical_bytes({
        name: plan[name] for name in _EXPORT_PLAN_BODY_FIELDS
    }))

    exported = manifest["exported_revision"]
    exported["source_alias"] = f"export:{source_identity}"
    exported["requested_revision"] = plan["source_root"]
    exported_record = exported["identity_material"]
    exported_record["locator"] = f"cassette-export:{plan['plan_id']}"
    exported_record["immutable_revision"] = manifest["artifact"]["digest"]
    exported_record["artifacts"] = [manifest["artifact"]]
    exported_record["tensor_index_digest"] = digest_bytes(canonical_bytes(
        artifact_semantics["tensor_contracts"]
        if artifact_semantics is not None
        else semantic["ordered_deltas"][-1]
    ))
    exported_record["architecture"] = semantic["graph"]["architecture"]
    exported_record["operator_set"] = semantic["graph"]["operators"]
    exported_record["tokenizer_digest"] = semantic["semantic_assets"]["tokenizer"]
    exported_record["processor_digest"] = semantic["semantic_assets"]["processor"]
    exported_record["template_digest"] = semantic["semantic_assets"]["template"]
    exported_record["precision_scheme"] = (
        artifact_semantics["precision"]
        if artifact_semantics is not None
        else source["precision_scheme"]
    )
    exported_record["parent_ids"] = [source_identity]
    exported_record["transform_manifest_digest"] = plan["plan_id"]

    export_id = digest_bytes(canonical_bytes({
        "revision": plan["source_root"],
        "target_schema": plan["target_schema"],
        "export_transform": plan["plan_id"],
        "artifact_digests": [manifest["artifact"]],
    }))
    manifest["export_id"] = export_id
    return export_id


def _write_attacked_export(
    package: Path, manifest: dict, *, bind_source_history: bool = True
) -> str:
    export_id = _reseal_export_manifest(
        manifest, bind_source_history=bind_source_history
    )
    path = package / "exports" / "manifests" / export_id.partition(":")[2]
    path.write_bytes(canonical_bytes(manifest))
    return export_id


def _material(root: dict) -> IdentityTuple:
    provenance = root["provenance"]
    record = provenance["identity_material"]
    return IdentityTuple(
        revision_kind=provenance["revision_kind"],
        source_kind=record["source_kind"],
        source_alias=provenance["source_alias"],
        canonical_locator=record["locator"],
        requested_revision=provenance["requested_revision"],
        immutable_revision=record["immutable_revision"],
        artifacts=tuple(ArtifactIdentity(**row) for row in record["artifacts"]),
        format_versions=tuple(tuple(row) for row in record["format_versions"]),
        tensor_index_digest=record["tensor_index_digest"],
        config_digest=record["config_digest"],
        architecture=record["architecture"],
        operator_set=tuple(record["operator_set"]),
        tokenizer_digest=record["tokenizer_digest"],
        processor_digest=record["processor_digest"],
        template_digest=record["template_digest"],
        precision_scheme=record["precision_scheme"],
        license_digest=record["license_digest"],
        parent_ids=tuple(record["parent_ids"]),
        transform_manifest_digest=record["transform_manifest_digest"],
    )


def _run_request(name: str, model_ref: str) -> dict:
    request = {
        "idempotency_key": f"s24-{name}-run",
        "model_ref": model_ref,
        "input": [{"role": "user", "content": "exercise the exact tuned child"}],
        "context_ref": f"s24-{name}-context",
        "generation": {},
    }
    if name == "ollama":
        request.pop("context_ref")
    return request


def test_q18_q19_q30_q40_protected_teacher_trace_is_immutable_and_executable(tmp_path):
    """Q18/Q19/Q30/Q40 acceptance: common, rare, ablated, and off-support evidence binds compilation."""

    corpus = _trace()
    body = {name: corpus[name] for name in corpus if name != "corpus_digest"}
    assert corpus["corpus_digest"] == digest_bytes(canonical_bytes(body))
    assert capture() == corpus
    traces = {row["condition_id"]: row for row in corpus["teacher_traces"]}
    assert traces["common"]["ablation_changed"] is False
    assert traces["rare"]["ablation_changed"] is True
    assert corpus["certificate_inputs"]["evidence"]["excluded_conditions"] == [{
        "condition_id": "off-support",
        "cause": "OFF_SUPPORT",
        "evidence": {"decision": "REJECT", "reason": "no immutable teacher trace"},
    }]
    rows = [row for row in DISPATCH_ROWS if row["case_id"] == corpus["operator_case"]["case_id"]]
    assert len(rows) == 1
    assert {
        name: rows[0][name] for name in corpus["operator_case"]
    } == corpus["operator_case"]
    trainer_tree = ast.parse((REPO / "trainer.py").read_text(encoding="utf-8"))
    material_function = next(
        node
        for node in trainer_tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "adapter_merge_material"
    )
    assert not any(
        isinstance(node, ast.Call)
        and (
            isinstance(node.func, ast.Name) and node.func.id == "_runtime"
            or isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "mx"
        )
        for node in ast.walk(material_function)
    )
    pager_tree = ast.parse((REPO / "pager.py").read_text(encoding="utf-8"))
    merge_function = next(
        node
        for node in pager_tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "merge_adapter_material"
    )
    assert any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "dispatch"
        for node in ast.walk(merge_function)
    )

    hostile = (
        lambda document: document["evidence"]["observation_contract"].update(off_support="ALLOW"),
        lambda document: document["evidence"]["observation_contract"]["selector"].pop(),
    )
    for ordinal, mutate in enumerate(hostile):
        payload, material, _ = _s24_artifact(mutate=mutate)
        cartridge = tmp_path / f"hostile-cartridge-{ordinal}"
        cartridge.mkdir()
        source_path = cartridge / material.artifacts[0].path
        source_path.write_bytes(payload)
        source, extents = _compiler_inputs(source_path, material, f"s24-hostile-{ordinal}")
        descriptor = next(iter(extents.values()))["fd"]
        try:
            plan = plan_revision(source, extents, cartridge)
            with pytest.raises(CassetteError) as refused:
                prepare_revision(
                    source,
                    extents,
                    cartridge,
                    plan,
                    capacity_coordinator=CapacityCoordinator(cartridge),
                    operation_id=f"s24-hostile-{ordinal}",
                )
            assert refused.value.code in {"CAPABILITY_MISMATCH", "INVALID_REQUEST"}
            assert pin_generation(cartridge) is None
        finally:
            os.close(descriptor)


def test_q5_q6_q26_q51_q54_q57_q58_machine_interoperability_update_and_removal(
    tmp_path,
    monkeypatch,
):
    """Q5/Q6/Q26/Q51-Q58 acceptance: replay, export, update, tuned calls, and exact removal."""

    payload, material, _ = _s24_artifact()
    acquired, cartridge, broker = _machine_replay(
        tmp_path, monkeypatch, "huggingface", payload, material
    )
    assert acquired["state"] == "SUCCEEDED", json.dumps(acquired, indent=2)
    compiled_root = acquired["result"]["root_digest"]
    compiled = load_root(cartridge, compiled_root)
    assert {row["condition_id"] for row in compiled["plans"][0]["certificate"]["condition_metrics"]} == {
        "common", "rare",
    }
    assert compiled["plans"][0]["certificate"]["compatibility"]["excluded_conditions"][0]["condition_id"] == "off-support"

    tinker_payload, tinker_material, _ = _s24_artifact("tinker")
    tinker_operation, tinker_cartridge, tinker_broker = _machine_replay(
        tmp_path, monkeypatch, "tinker", tinker_payload, tinker_material
    )
    assert tinker_operation["state"] == "SUCCEEDED", tinker_operation
    tinker_root = load_root(
        tinker_cartridge, tinker_operation["result"]["root_digest"]
    )
    assert tinker_root["provenance"]["identity_material"]["source_kind"] == "tinker"
    tinker_broker.close()

    ollama_payload, ollama_material, _ = _s24_artifact("ollama")
    ollama_operation, _, ollama_broker = _machine_replay(
        tmp_path, monkeypatch, "ollama", ollama_payload, ollama_material
    )
    assert ollama_operation["state"] == "FAILED"
    assert ollama_operation["error"]["code"] == "MODEL_UNSUPPORTED"
    ollama_broker.close()

    exported = {}
    portable_exports = {}
    for target_schema in ("safetensors-v1", "gguf-v3"):
        export_request = {
            "protocol_version": "1",
            "operation": "export",
            "idempotency_key": f"s24-export-{target_schema}",
            "target": compiled_root,
            "arguments": {"target_schema": target_schema},
        }
        plan = plan_export(cartridge, compiled_root, target_schema)
        if target_schema == "safetensors-v1":
            short_request = {
                **export_request,
                "idempotency_key": "s24-export-short-claim",
            }
            short_plan = plan_export(cartridge, compiled_root, target_schema)
            short_claim = CapacityCoordinator(cartridge)
            before_export = _store_snapshot(cartridge)
            with monkeypatch.context() as capacity_patch:
                _limit_available_bytes(
                    capacity_patch, cartridge, short_plan["artifact_size"] - 1
                )
                short_export = asyncio.run(broker.export_revision(
                    short_request, cartridge, short_claim
                ))
            assert short_export["state"] == "FAILED"
            assert short_export["error"]["code"] == "CAPACITY_EXCEEDED"
            assert _store_snapshot(cartridge) == before_export
        export_claim = CapacityCoordinator(cartridge)
        operation = asyncio.run(broker.export_revision(
            export_request, cartridge, export_claim
        ))
        assert operation["state"] == "SUCCEEDED", operation
        exported[target_schema] = operation["result"]
        portable_export = tmp_path / f"portable-{target_schema}"
        shutil.copytree(cartridge / "exports", portable_export / "exports")
        portable_exports[target_schema] = portable_export
        reimported_cartridge = tmp_path / f"reimport-{target_schema}"
        reimported_root = import_export(
            portable_export,
            operation["result"]["export_id"],
            reimported_cartridge,
        )
        reimported = load_root(reimported_cartridge, reimported_root)
        assert reimported["semantic_assets"] == compiled["semantic_assets"]
        assert reimported["operators"] == compiled["operators"]
        assert reimported["provenance"]["identity_material"]["architecture"] == compiled["provenance"]["identity_material"]["architecture"]
        assert reimported["provenance"]["identity_material"]["precision_scheme"] == compiled["provenance"]["identity_material"]["precision_scheme"]
        source_weight = read_tensor(cartridge, compiled_root, "weight")
        imported_weight = read_tensor(reimported_cartridge, reimported_root, "weight")
        assert imported_weight == source_weight
        manifest = json.loads(
            (cartridge / operation["result"]["manifest_path"]).read_bytes()
        )
        semantics = manifest["semantic_manifest"]
        assert semantics == export_semantic_manifest(cartridge, compiled_root)
        assert manifest["artifact_semantics"]["graph"]["plans"] == []
        assert semantics["graph"] == {
            "architecture": compiled["provenance"]["identity_material"]["architecture"],
            "operators": compiled["operators"],
            "plans": compiled["plans"],
        }
        assert semantics["ordered_deltas"] == compiled["deltas"]
        weights = struct.unpack("<4f", imported_weight)
        mx, _ = pager._mlx_runtime()
        output = pager.dispatch(
            "mlx.matmul.f32.3x2_2x2",
            (
                mx.array(_trace()["teacher_traces"][0]["inputs"], dtype=mx.float32),
                mx.array((weights[:2], weights[2:]), dtype=mx.float32),
            ),
        )
        assert output.tolist() == _trace()["teacher_traces"][0]["teacher_logits"]
    assert exported["safetensors-v1"]["artifact_digest"] != exported["gguf-v3"]["artifact_digest"]
    semantic_losses = (
        ("tokenizer", ("semantic_assets", "tokenizer"), None),
        ("operator", ("graph", "operators"), None),
        ("precision", ("precision",), None),
        ("graph-plan", ("graph", "plans"), []),
    )
    for label, field_path, replacement in semantic_losses:
        hostile_export = tmp_path / f"portable-hostile-{label}"
        shutil.copytree(portable_exports["safetensors-v1"], hostile_export)
        hostile_manifest = (
            hostile_export
            / exported["safetensors-v1"]["manifest_path"]
        )
        hostile_record = json.loads(hostile_manifest.read_bytes())
        container = hostile_record["semantic_manifest"]
        for field in field_path[:-1]:
            container = container[field]
        if replacement is None:
            container.pop(field_path[-1])
        else:
            container[field_path[-1]] = replacement
        hostile_manifest.write_bytes(canonical_bytes(hostile_record))
        with pytest.raises(CassetteError) as detached_semantics:
            import_export(
                hostile_export,
                exported["safetensors-v1"]["export_id"],
                tmp_path / f"hostile-{label}-reimport",
            )
        assert detached_semantics.value.code == "ROOT_INVALID"

    forged = plan_export(cartridge, compiled_root, "safetensors-v1")
    forged["semantic_binding"] = digest_bytes(b"dropped tokenizer operator and precision")
    with pytest.raises(CassetteError) as semantic_loss:
        export_shape(cartridge, {
            name: forged[name]
            for name in (
                "version", "source_root", "source_identity", "target_schema", "mode",
                "semantic_binding", "delta_id", "adapter_rank", "adapter_scale",
            )
        })
    assert semantic_loss.value.code == "IDENTITY_MISMATCH"

    update_cartridge, base_root, _ = _quantized_parent(tmp_path / "s24-update")
    base_locations = {row.page_digest: row for row in page_locations(update_cartridge, base_root)}
    changed_digest = sorted(base_locations)[0]
    unchanged_digest = sorted(base_locations)[1]
    changed = bytearray(read_training_page(update_cartridge, base_root, changed_digest))
    changed[0] ^= 1
    delta = create_revision_delta(
        update_cartridge,
        base_root,
        "git-sha1:" + "9" * 40,
        {changed_digest: bytes(changed)},
    )
    payloads = {delta["replacements"][0]["new_page_digest"]: bytes(changed)}
    before = pin_generation(update_cartridge)
    direct_cartridge = tmp_path / "s24-update-direct"
    shutil.copytree(update_cartridge, direct_cartridge)
    direct_operation = _operation_id("s24-direct-delta")
    direct_shape = revision_delta_shape(
        direct_cartridge, direct_operation, base_root, delta, payloads
    )
    short_operation = _operation_id("s24-short-delta")
    short_shape = revision_delta_shape(
        direct_cartridge, short_operation, base_root, delta, payloads
    )
    short_claim = CapacityCoordinator(direct_cartridge)
    pre_admission = _store_snapshot(direct_cartridge)
    with monkeypatch.context() as capacity_patch:
        _limit_available_bytes(
            capacity_patch, direct_cartridge, len(next(iter(payloads.values()))) - 1
        )
        with pytest.raises(CassetteError) as short_delta:
            apply_revision_delta(
                direct_cartridge,
                short_operation,
                base_root,
                delta,
                payloads,
                short_claim,
            )
    assert short_delta.value.code == "CAPACITY_EXCEEDED"
    assert _store_snapshot(direct_cartridge) == pre_admission
    delta_contract_attacks = (
        (
            "base_identity",
            digest_bytes(b"foreign-q54-base-identity"),
            True,
            "DELTA_BASE_MISMATCH",
            "revision delta names another base identity",
        ),
        (
            "delta_digest",
            digest_bytes(b"foreign-q54-declared-digest"),
            False,
            "PAGE_CORRUPT",
            "declared revision-delta digest does not match its content",
        ),
        (
            "target_identity",
            digest_bytes(b"foreign-q54-target-identity"),
            True,
            "IDENTITY_MISMATCH",
            "revision delta does not reconstruct its declared target",
        ),
    )
    for field, value, reseal, code, detail in delta_contract_attacks:
        attacked_delta = deepcopy(delta)
        attacked_delta[field] = value
        if reseal:
            attacked_delta["delta_digest"] = digest_bytes(canonical_bytes({
                name: attacked_delta[name]
                for name in attacked_delta
                if name != "delta_digest"
            }))
        guard_snapshot = _store_snapshot(direct_cartridge)
        attack_claim = CapacityCoordinator(direct_cartridge)
        with pytest.raises(CassetteError) as refused_delta:
            apply_revision_delta(
                direct_cartridge,
                direct_operation,
                base_root,
                attacked_delta,
                payloads,
                attack_claim,
            )
        assert refused_delta.value.code == code
        assert refused_delta.value.detail == detail
        assert _store_snapshot(direct_cartridge) == guard_snapshot
    wrong_base_claim = CapacityCoordinator(direct_cartridge)
    with pytest.raises(CassetteError) as wrong_base:
        apply_revision_delta(
            direct_cartridge,
            direct_operation,
            digest_bytes(b"foreign-base"),
            delta,
            payloads,
            wrong_base_claim,
        )
    assert wrong_base.value.code == "DELTA_BASE_MISMATCH"
    corrupt_claim = CapacityCoordinator(direct_cartridge)
    with pytest.raises(CassetteError) as corrupt:
        apply_revision_delta(
            direct_cartridge,
            direct_operation,
            base_root,
            delta,
            {next(iter(payloads)): b"x" * len(changed)},
            corrupt_claim,
        )
    assert corrupt.value.code == "PAGE_CORRUPT"
    interrupted_claim = CapacityCoordinator(direct_cartridge)
    with pytest.raises(CassetteError) as interrupted:
        apply_revision_delta(
            direct_cartridge, direct_operation, base_root, delta, {}, interrupted_claim
        )
    assert interrupted.value.code == "SOURCE_UNAVAILABLE"
    direct_claim = CapacityCoordinator(direct_cartridge)
    candidate = apply_revision_delta(
        direct_cartridge,
        direct_operation,
        base_root,
        delta,
        payloads,
        direct_claim,
    )
    assert pin_generation(direct_cartridge) == before
    target_locations = {
        row.page_digest: row for row in page_locations(direct_cartridge, candidate)
    }
    assert target_locations[unchanged_digest] == base_locations[unchanged_digest]
    fork = create_revision_delta(
        update_cartridge,
        base_root,
        "git-sha1:" + "8" * 40,
        {changed_digest: bytes(reversed(changed))},
    )
    update_broker = CanonicalBroker(tmp_path / "s24-update-log")
    apply_request = {
        "protocol_version": "1",
        "operation": "apply_delta",
        "idempotency_key": "s24-apply-valid-delta",
        "target": base_root,
        "arguments": {"delta_digest": delta["delta_digest"]},
    }
    apply_operation = update_broker.operation_id(apply_request)
    apply_shape = revision_delta_shape(
        update_cartridge, apply_operation, base_root, delta, payloads
    )
    apply_claim = CapacityCoordinator(update_cartridge)
    applied = asyncio.run(update_broker.apply_delta(
        apply_request,
        update_cartridge,
        delta,
        payloads,
        apply_claim,
        CapacityCoordinator(update_cartridge),
    ))
    assert applied["state"] == "SUCCEEDED", applied
    assert applied["result"]["root_digest"] == candidate
    fork_request = {
        "protocol_version": "1",
        "operation": "apply_delta",
        "idempotency_key": "s24-apply-ancestry-fork",
        "target": base_root,
        "arguments": {"delta_digest": fork["delta_digest"]},
    }
    fork_operation = update_broker.operation_id(fork_request)
    fork_claim = CapacityCoordinator(update_cartridge)
    forked = asyncio.run(update_broker.apply_delta(
        fork_request,
        update_cartridge,
        fork,
        {fork["replacements"][0]["new_page_digest"]: bytes(reversed(changed))},
        fork_claim,
        CapacityCoordinator(update_cartridge),
    ))
    assert forked["state"] == "FAILED"
    assert forked["error"]["code"] == "DELTA_BASE_MISMATCH"
    rolled_back = rollback_generation(update_cartridge, "s24-update-rollback")
    assert rolled_back.root_digest == base_root

    current_proof = revision_reachability(update_cartridge, base_root)
    refusal_snapshot = _store_snapshot(update_cartridge)
    removal_refusal_operation = _operation_id("s24-removal-refusals")
    current_refusal_claim = CapacityCoordinator(update_cartridge)
    with pytest.raises(CassetteError) as current_refusal:
        remove_revision(
            update_cartridge,
            removal_refusal_operation,
            base_root,
            current_proof,
            current_refusal_claim,
        )
    assert current_refusal.value.code == "INVALID_REQUEST"
    assert _store_snapshot(update_cartridge) == refusal_snapshot
    target_proof = revision_reachability(update_cartridge, candidate)
    reachable_refusal_claim = CapacityCoordinator(update_cartridge)
    with pytest.raises(CassetteError) as reachable_refusal:
        remove_revision(
            update_cartridge,
            removal_refusal_operation,
            candidate,
            target_proof,
            reachable_refusal_claim,
        )
    assert reachable_refusal.value.code == "INVALID_REQUEST"
    assert _store_snapshot(update_cartridge) == refusal_snapshot
    with pytest.raises(CassetteError):
        revision_reachability(update_cartridge, "malformed")
    assert _store_snapshot(update_cartridge) == refusal_snapshot

    orphan_source = tmp_path / "orphan.safetensors"
    orphan_payload = b"unreachable-s24-revision"
    header = {
        "orphan": {"dtype": "U8", "shape": [len(orphan_payload)], "data_offsets": [0, len(orphan_payload)]}
    }
    encoded = json.dumps(header, separators=(",", ":")).encode()
    encoded += b" " * (-len(encoded) % 8)
    orphan_source.write_bytes(len(encoded).to_bytes(8, "little") + encoded + orphan_payload)
    orphan_material = IdentityTuple(
        revision_kind="source",
        source_kind="huggingface",
        source_alias="fixture/s24-orphan",
        canonical_locator="fixture/s24-orphan",
        requested_revision=None,
        immutable_revision="git-sha1:" + "7" * 40,
        artifacts=(ArtifactIdentity(
            orphan_source.name,
            orphan_source.stat().st_size,
            digest_bytes(orphan_source.read_bytes()),
        ),),
        format_versions=(("safetensors", "1"),),
        tensor_index_digest=digest_bytes(b"s24-orphan-index"),
        config_digest=digest_bytes(b"s24-orphan-config"),
        architecture="S24Orphan",
        operator_set=("matmul",),
        tokenizer_digest=digest_bytes(b"s24-orphan-tokenizer"),
        processor_digest=digest_bytes(b"s24-orphan-processor"),
        template_digest=digest_bytes(b"s24-orphan-template"),
        precision_scheme="u8",
        license_digest=digest_bytes(b"s24-orphan-license"),
        parent_ids=(),
        transform_manifest_digest=None,
    )
    orphan_root = import_safetensors(
        {orphan_source.name: orphan_source}, update_cartridge, orphan_material
    )
    assert plan_export(update_cartridge, orphan_root, "safetensors-v1")[
        "target_schema"
    ] == "safetensors-v1"
    with pytest.raises(CassetteError) as unrepresentable_precision:
        plan_export(update_cartridge, orphan_root, "gguf-v3")
    assert unrepresentable_precision.value.code == "MODEL_UNSUPPORTED"
    assert (
        unrepresentable_precision.value.detail
        == "GGUF target cannot represent one or more dtypes"
    )

    operator_cartridge = tmp_path / "q26-operator-cartridge"
    operator_cartridge.mkdir()
    operator_material = replace(
        orphan_material,
        source_alias="fixture/s24-foreign-operator",
        canonical_locator="fixture/s24-foreign-operator",
        immutable_revision="git-sha1:" + "8" * 40,
        operator_set=("s24_foreign_operator",),
    )
    operator_root = import_safetensors(
        {orphan_source.name: orphan_source}, operator_cartridge, operator_material
    )
    assert plan_export(operator_cartridge, operator_root, "safetensors-v1")[
        "target_schema"
    ] == "safetensors-v1"
    with pytest.raises(CassetteError) as unrepresentable_operator:
        plan_export(operator_cartridge, operator_root, "gguf-v3")
    assert unrepresentable_operator.value.code == "MODEL_UNSUPPORTED"
    assert (
        unrepresentable_operator.value.detail
        == "GGUF target cannot represent one or more required operators"
    )

    repair_shape = repair_set_shape(update_cartridge, orphan_root)
    repair_claim = CapacityCoordinator(update_cartridge)
    repair_set = create_repair_set(
        update_cartridge, orphan_root, repair_claim
    )
    orphan_proof = revision_reachability(update_cartridge, orphan_root)
    forged_proof = deepcopy(orphan_proof)
    forged_proof["catalog_digest"] = digest_bytes(b"forged-reachability-catalog")
    forged_body = {
        name: forged_proof[name]
        for name in forged_proof
        if name != "reachability_digest"
    }
    forged_proof["reachability_digest"] = digest_bytes(canonical_bytes(forged_body))
    forged_operation = _operation_id("s24-forged-reachability")
    forged_claim = CapacityCoordinator(update_cartridge)
    before_forged_removal = _store_snapshot(update_cartridge)
    with pytest.raises(CassetteError) as forged_reachability:
        remove_revision(
            update_cartridge,
            forged_operation,
            orphan_root,
            forged_proof,
            forged_claim,
        )
    assert forged_reachability.value.code == "INVALID_REQUEST"
    assert _store_snapshot(update_cartridge) == before_forged_removal
    expected_repair_paths = {
        f"repair/{orphan_root[7:]}.json",
        f"repair/manifests/{orphan_root[7:]}",
        f"repair/objects/{repair_set.root_digest[7:]}",
        f"repair/objects/{repair_set.index_digest[7:]}",
        *[
            f"repair/objects/{digest[7:]}"
            for digest in repair_set.parity_digests
        ],
    }
    assert expected_repair_paths <= set(orphan_proof["removable_paths"])
    remove_request = {
        "protocol_version": "1",
        "operation": "remove_revision",
        "idempotency_key": "s24-remove-orphan",
        "target": orphan_root,
        "arguments": {"reachability_digest": orphan_proof["reachability_digest"]},
    }
    remove_operation = update_broker.operation_id(remove_request)
    remove_shape = revision_removal_shape(update_cartridge, orphan_root, orphan_proof)
    short_remove_operation = _operation_id("s24-short-removal")
    short_remove_claim = CapacityCoordinator(update_cartridge)
    pre_remove_admission = _store_snapshot(update_cartridge)
    with monkeypatch.context() as capacity_patch:
        _limit_available_bytes(
            capacity_patch, update_cartridge, remove_shape["journal_bytes"] - 1
        )
        with pytest.raises(CassetteError) as short_removal:
            remove_revision(
                update_cartridge,
                short_remove_operation,
                orphan_root,
                orphan_proof,
                short_remove_claim,
            )
    assert short_removal.value.code == "CAPACITY_EXCEEDED"
    assert _store_snapshot(update_cartridge) == pre_remove_admission
    remove_claim = CapacityCoordinator(update_cartridge)
    removed = asyncio.run(update_broker.remove_revision(
        remove_request, update_cartridge, orphan_proof, remove_claim
    ))
    assert removed["state"] == "SUCCEEDED", removed
    assert removed["result"]["removed_root"] == orphan_root
    repeated_removal = asyncio.run(update_broker.remove_revision(
        remove_request, update_cartridge, orphan_proof, remove_claim
    ))
    assert repeated_removal == removed
    with pytest.raises(CassetteError):
        load_root(update_cartridge, orphan_root)
    assert not any((update_cartridge / path).exists() for path in expected_repair_paths)
    assert pin_generation(update_cartridge).root_digest == base_root
    update_broker.close()

    compiled_variant = derive_root(
        cartridge,
        compiled_root,
        _material(compiled),
        tuple([*compiled["plans"], {"fixture_variant": "s24-ambiguity"}]),
    )
    assert compiled_variant != compiled_root
    with pytest.raises(CassetteError) as ambiguous:
        revision_reachability(cartridge, compiled["identity"])
    assert ambiguous.value.code == "INVALID_REQUEST"

    tier_a, tier_a_base, tier_a_parameters = _quantized_parent(tmp_path / "s24-tier-a")
    tier_a_reimport = tmp_path / "s24-tier-a-reimport"
    shutil.copytree(tier_a, tier_a_reimport)
    _, tier_a_artifact = _train(
        tier_a,
        tier_a_base,
        tier_a_parameters,
        "ADAPTER_SFT",
        (SFT_BATCHES[0],),
        "s24-tier-a-child",
    )
    tier_a_child = pin_generation(tier_a).root_digest
    tier_b, tier_b_base, tier_b_parameters = _compiled_parent(tmp_path / "s24-tier-b")
    _, tier_b_artifact = _train(
        tier_b,
        tier_b_base,
        tier_b_parameters,
        "COMPILED_RECOVERY",
        (RECOVERY_BATCH,),
        "s24-tier-b-child",
        calibrations=_calibration_records("s24"),
    )
    tier_b_child = pin_generation(tier_b).root_digest

    adapter_broker = CanonicalBroker(tmp_path / "s24-adapter-export-log")
    adapter_request = {
        "protocol_version": "1",
        "operation": "export",
        "idempotency_key": "s24-export-adapter",
        "target": tier_a_child,
        "arguments": {"target_schema": "adapter-safetensors-v1"},
    }
    adapter_plan = plan_export(tier_a, tier_a_child, "adapter-safetensors-v1")
    detached_plan = {
        name: adapter_plan[name] for name in _EXPORT_PLAN_BODY_FIELDS
    }
    detached_plan["delta_id"] = digest_bytes(b"foreign-q26-adapter-delta")
    with pytest.raises(CassetteError) as detached_delta:
        export_shape(tier_a, detached_plan)
    assert detached_delta.value.code == "IDENTITY_MISMATCH"
    assert detached_delta.value.detail == (
        "adapter export or merge is detached from its ordered delta"
    )
    adapter_claim = CapacityCoordinator(tier_a)
    adapter_export = asyncio.run(adapter_broker.export_revision(
        adapter_request, tier_a, adapter_claim
    ))
    assert adapter_export["state"] == "SUCCEEDED", adapter_export
    portable_adapter = tmp_path / "portable-adapter"
    shutil.copytree(tier_a / "exports", portable_adapter / "exports")
    rebuilt_child = import_export(
        portable_adapter,
        adapter_export["result"]["export_id"],
        tier_a_reimport,
        base_root=tier_a_base,
    )
    assert rebuilt_child == tier_a_child
    assert load_root(tier_a_reimport, rebuilt_child)["deltas"] == load_root(tier_a, tier_a_child)["deltas"]
    adapter_manifest = json.loads(
        (portable_adapter / adapter_export["result"]["manifest_path"]).read_bytes()
    )
    export_contract_attacks = (
        (
            "tuned-binding",
            "tuned export does not bind its parent and ordered deltas",
        ),
        (
            "mode-history",
            "export mode cannot represent its ordered delta history",
        ),
        (
            "duplicate-delta",
            "adapter export names an absent ordered delta",
        ),
    )
    for label, detail in export_contract_attacks:
        hostile_package = tmp_path / f"portable-hostile-{label}"
        shutil.copytree(portable_adapter, hostile_package)
        hostile_manifest = deepcopy(adapter_manifest)
        bind_source_history = True
        if label == "tuned-binding":
            hostile_manifest["source_revision"]["identity_material"][
                "transform_manifest_digest"
            ] = digest_bytes(b"foreign-q26-ordered-history")
            bind_source_history = False
        elif label == "mode-history":
            hostile_manifest["semantic_manifest"]["ordered_deltas"][-1][
                "delta_id"
            ] = digest_bytes(b"foreign-q26-mode-delta")
        else:
            hostile_manifest["semantic_manifest"]["ordered_deltas"].append(
                deepcopy(
                    hostile_manifest["semantic_manifest"]["ordered_deltas"][-1]
                )
            )
        hostile_export_id = _write_attacked_export(
            hostile_package,
            hostile_manifest,
            bind_source_history=bind_source_history,
        )
        hostile_target = tmp_path / f"hostile-{label}-target"
        shutil.copytree(tier_a_reimport, hostile_target)
        hostile_snapshot = _store_snapshot(hostile_target)
        with pytest.raises(CassetteError) as refused_export:
            import_export(
                hostile_package,
                hostile_export_id,
                hostile_target,
                base_root=tier_a_base,
            )
        assert refused_export.value.code == "ROOT_INVALID"
        assert refused_export.value.detail == detail
        assert _store_snapshot(hostile_target) == hostile_snapshot

    corrupt_page_package = tmp_path / "portable-hostile-adapter-page"
    shutil.copytree(portable_adapter, corrupt_page_package)
    corrupt_page_manifest = deepcopy(adapter_manifest)
    corrupt_page_path = (
        corrupt_page_package / adapter_export["result"]["artifact_path"]
    )
    corrupt_page_bytes = bytearray(corrupt_page_path.read_bytes())
    corrupt_page_bytes[-1] ^= 1
    corrupt_page_path.write_bytes(corrupt_page_bytes)
    corrupt_page_manifest["artifact"]["digest"] = (
        f"sha256:{hashlib.sha256(corrupt_page_bytes).hexdigest()}"
    )
    corrupt_page_export_id = _write_attacked_export(
        corrupt_page_package, corrupt_page_manifest
    )
    corrupt_page_target = tmp_path / "hostile-adapter-page-target"
    shutil.copytree(tier_a_reimport, corrupt_page_target)
    corrupt_page_snapshot = _store_snapshot(corrupt_page_target)
    with pytest.raises(CassetteError) as refused_page:
        import_export(
            corrupt_page_package,
            corrupt_page_export_id,
            corrupt_page_target,
            base_root=tier_a_base,
        )
    assert refused_page.value.code == "PAGE_CORRUPT"
    assert refused_page.value.detail == (
        "adapter pages differ from their ordered delta identities"
    )
    assert _store_snapshot(corrupt_page_target) == corrupt_page_snapshot
    expected_merged = _expected_merged_tensors(
        tier_a, tier_a_base, tier_a_child, tier_a_artifact
    )
    merged_exports = {}
    for target_schema in ("gguf-v3", "safetensors-v1"):
        merged_request = {
            "protocol_version": "1",
            "operation": "export",
            "idempotency_key": f"s24-export-merged-{target_schema}",
            "target": tier_a_child,
            "arguments": {"target_schema": target_schema},
        }
        merged_plan = plan_export(tier_a, tier_a_child, target_schema)
        assert merged_plan["mode"] == "merged"
        assert (
            merged_plan["delta_id"],
            merged_plan["adapter_rank"],
            merged_plan["adapter_scale"],
        ) == (
            load_root(tier_a, tier_a_child)["deltas"][-1]["delta_id"],
            1,
            "1",
        )
        merged_claim = CapacityCoordinator(tier_a)
        merged_export = asyncio.run(adapter_broker.export_revision(
            merged_request, tier_a, merged_claim
        ))
        assert merged_export["state"] == "SUCCEEDED", merged_export
        portable_merged = tmp_path / f"portable-merged-{target_schema}"
        shutil.copytree(tier_a / "exports", portable_merged / "exports")
        merged_exports[target_schema] = (portable_merged, merged_export["result"])
        merged_cartridge = tmp_path / f"reimport-merged-{target_schema}"
        merged_root = import_export(
            portable_merged,
            merged_export["result"]["export_id"],
            merged_cartridge,
        )
        merged_root_record = load_root(merged_cartridge, merged_root)
        assert merged_root_record["deltas"] == []
        assert (
            merged_root_record["provenance"]["identity_material"]["precision_scheme"]
            == "float32-merged-adapter-v1"
        )
        for tensor_id, expected in expected_merged.items():
            assert read_tensor(merged_cartridge, merged_root, tensor_id) == expected
        merged_manifest = json.loads(
            (tier_a / merged_export["result"]["manifest_path"]).read_bytes()
        )
        assert merged_manifest["semantic_manifest"]["ordered_deltas"] == load_root(
            tier_a, tier_a_child
        )["deltas"]
        assert merged_manifest["artifact_semantics"]["ordered_deltas"] == []
        assert merged_manifest["artifact_semantics"]["precision"] == "float32-merged-adapter-v1"
        imported_semantics = export_semantic_manifest(merged_cartridge, merged_root)
        assert imported_semantics == merged_manifest["artifact_semantics"] | {
            "version": "q10-export-semantics-v1",
            "source_identity": imported_semantics["source_identity"],
        }

    portable_merged, merged_result = merged_exports["safetensors-v1"]
    hostile_delta_export = tmp_path / "portable-hostile-ordered-delta"
    shutil.copytree(portable_merged, hostile_delta_export)
    hostile_delta_manifest = hostile_delta_export / merged_result["manifest_path"]
    hostile_delta_record = json.loads(hostile_delta_manifest.read_bytes())
    hostile_delta_record["semantic_manifest"]["ordered_deltas"] = []
    hostile_delta_manifest.write_bytes(canonical_bytes(hostile_delta_record))
    with pytest.raises(CassetteError) as ordered_delta_loss:
        import_export(
            hostile_delta_export,
            merged_result["export_id"],
            tmp_path / "hostile-ordered-delta-reimport",
        )
    assert ordered_delta_loss.value.code == "ROOT_INVALID"

    first_base = tier_a_artifact["base_pages"][0]
    first_delta = tier_a_artifact["delta_pages"][0]
    first_envelope = json.loads(
        read_training_page(tier_a, tier_a_child, first_delta["page_digest"])
    )
    mx, _ = pager._mlx_runtime()
    dispatched_merge = pager.dispatch(
        "mlx.adapter_merge.i8_f32.rank1.2x3",
        (
            mx.array(
                struct.unpack("<6b", read_tensor(tier_a, tier_a_base, first_base["tensor_id"])),
                dtype=mx.int8,
            ).reshape((2, 3)),
            mx.array(
                struct.unpack("<6f", bytes.fromhex(first_envelope["payload_hex"])),
                dtype=mx.float32,
            ).reshape((2, 3)),
            mx.array([1.0], dtype=mx.float32),
            mx.array([0], dtype=mx.int8),
        ),
    )
    assert struct.pack(
        "<6f", *(value for row in dispatched_merge.tolist() for value in row)
    ) == expected_merged[first_base["tensor_id"]]
    for target_schema in ("adapter-safetensors-v1", "gguf-v3", "safetensors-v1"):
        with pytest.raises(CassetteError) as recovery_loss:
            plan_export(tier_b, tier_b_child, target_schema)
        assert recovery_loss.value.code == "MODEL_UNSUPPORTED"
    assert tier_a_artifact["adapter_rank"] == 1
    assert tier_a_artifact["adapter_scale"] == "1"
    assert tier_b_artifact["parent_certificate_digest"] is not None

    async def call_children():
        call_broker = CanonicalBroker(tmp_path / "s24-call-log")
        for tier, child_cartridge, child_root in (
            ("A", tier_a, tier_a_child),
            ("B", tier_b, tier_b_child),
        ):
            root = load_root(child_cartridge, child_root)
            profile = _profile(f"s24-tier-{tier}")
            profile.update(
                model_revision=root["identity"],
                source_parent=root["parents"][0],
                plan_id=(
                    root["plans"][0]["execution_plan"]["plan_id"]
                    if root["plans"] else digest_bytes(f"s24-tier-{tier}-plan".encode())
                ),
                training_tier=tier,
                precision=root["provenance"]["identity_material"]["precision_scheme"],
                semantic_state=digest_bytes(canonical_bytes({
                    "semantic_assets": root["semantic_assets"], "deltas": root["deltas"],
                })),
            )

            async def activate(lease: ScheduledLease, _capability: dict) -> None:
                assert lease.model_revision == root["identity"]
                load_root(child_cartridge, child_root)

            call_broker.register_capability(
                root["identity"],
                profile,
                activate,
                schedule=_schedule(profile, 0),
                cartridge=child_cartridge,
                root_digest=child_root,
            )
            for name in sorted(ADAPTER_PROTOCOLS):
                adapter = NamedAdapter(
                    name,
                    model_aliases={root["identity"]: f"s24/{tier.lower()}"},
                    server_contract=name == "hermes",
                )
                canonical = _run_request(name, root["identity"])
                wire = adapter.to_wire_request(canonical)
                assert adapter.from_wire_request(wire) == canonical
                negotiation = call_broker.negotiate({"model_ref": root["identity"]})
                context_id = f"s24-{tier}-{name}"
                control = _request(
                    negotiation,
                    f"s24-{tier}-{name}-dispatch",
                    context_id,
                )

                async def worker(lease: ScheduledLease) -> dict:
                    assert lease.model_revision == root["identity"]
                    if tier == "A":
                        tensors = pager.merge_adapter_material(
                            adapter_merge_material(child_cartridge, child_root)
                        )
                        tensor_id = sorted(tensors)[0]
                        weight_values = struct.unpack("<6f", tensors[tensor_id])
                    else:
                        artifact = load_training_artifact(child_cartridge, child_root)
                        tensor_id = artifact["base_pages"][0]["tensor_id"]
                        weight_values = tuple(
                            float(value)
                            for value in struct.unpack(
                                "<6b", read_tensor(child_cartridge, child_root, tensor_id)
                            )
                        )
                    mx, _ = pager._mlx_runtime()
                    logits = pager.dispatch(
                        "mlx.matmul.f32.2x3_3x2",
                        (
                            mx.array(weight_values, dtype=mx.float32).reshape((2, 3)),
                            mx.array([[1, 0], [0, 1], [1, -1]], dtype=mx.float32),
                        ),
                    ).tolist()
                    return {
                        "child_root": child_root,
                        "artifact_digest": digest_bytes(canonical_bytes(
                            load_root(child_cartridge, child_root)["deltas"][-1]
                        )),
                        "tensor_id": tensor_id,
                        "logits": logits,
                    }

                operation = await call_broker.dispatch(
                    name, context_id, control, negotiation, "EXEC", worker
                )
                assert operation["state"] == "SUCCEEDED", operation
                assert operation["result"]["value"]["child_root"] == child_root
                assert len(operation["result"]["value"]["logits"]) == 2
        call_broker.close()

    asyncio.run(call_children())
    adapter_broker.close()
    broker.close()
