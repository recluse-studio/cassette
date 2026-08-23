# test_s25_invalidation.py — S25 Q19/Q27/Q37/Q61/Q70/Q73/Q75 compilation, recovery, replay, and frontier fixture; depends on compiler.py, pager.py, schema/tables.py, store.py, tests/compiler_fixture.py, tests/test_s05_store.py, tests/test_s14_pager.py, tests/test_s21_trainer.py, tools/resource_frontier.py.
"""Prove exact dependency closure, clean equivalence, recovery publication, and bounded curves."""

from __future__ import annotations

import asyncio
from copy import deepcopy
import json
import os
from pathlib import Path
import platform
import shutil
import struct

import pytest

from compiler import (
    compilation_specification,
    plan_revision,
    prepare_recovered_revision,
    prepare_revision,
    recompile_revision,
    verify_bundle_structure,
)
from compiler_fixture import artifact as compiler_artifact
from errors import CassetteError
import pager
from schema.tables import DISPATCH_ROWS
from store import (
    IdentityTuple,
    canonical_bytes,
    commit_generation,
    digest_bytes,
    import_safetensors,
    load_root,
    model_identity,
    pin_generation,
)
from test_s05_store import _identity, _write_safetensors
from test_s14_pager import _selection, _stochastic_fixture
from test_s21_trainer import (
    RECOVERY_BATCH,
    SFT_BATCHES,
    _compiled_parent,
    _quantized_parent,
    _train,
)
from tools.resource_frontier import machine_fixture_frontier


pytestmark = pytest.mark.skipif(
    platform.system() != "Darwin" or platform.machine() != "arm64",
    reason="S25 requires arm64 macOS, pinned MLX Metal, and F_FULLFSYNC",
)

REPO = Path(__file__).resolve().parent.parent
TRACE = json.loads((REPO / "tests" / "fixtures" / "s24_teacher_trace.json").read_bytes())
CURVES = REPO / "tools" / "generated" / "s25_resource_curves.json"
AXES = (
    "weights", "condition_metric", "atom", "cover", "observation", "description",
    "residual_estimator", "composition", "precision", "tokenizer", "template",
    "context", "operator",
)
ARTIFACTS = (
    "protected_trace_corpus", "page_stats", "page_layout", "semantic_manifest",
    "observation_contract", "condition_metrics", "compatibility_witnesses",
    "atom_cover", "description_distortion", "residual_metadata",
    "estimator_calibration", "precision_calibration", "composition_proof",
    "kernel_plan", "physical_schedule", "quality_proof", "protocol_capabilities",
    "cache_key",
)
EXPECTED = {
    "weights": "page_stats page_layout condition_metrics compatibility_witnesses atom_cover description_distortion residual_metadata estimator_calibration precision_calibration composition_proof kernel_plan physical_schedule quality_proof protocol_capabilities cache_key".split(),
    "condition_metric": "condition_metrics compatibility_witnesses atom_cover description_distortion residual_metadata estimator_calibration precision_calibration composition_proof kernel_plan physical_schedule quality_proof protocol_capabilities cache_key".split(),
    "atom": "compatibility_witnesses atom_cover description_distortion residual_metadata estimator_calibration precision_calibration composition_proof kernel_plan physical_schedule quality_proof protocol_capabilities cache_key".split(),
    "cover": "observation_contract atom_cover composition_proof kernel_plan physical_schedule quality_proof protocol_capabilities cache_key".split(),
    "observation": "protected_trace_corpus observation_contract condition_metrics compatibility_witnesses atom_cover description_distortion residual_metadata estimator_calibration precision_calibration composition_proof kernel_plan physical_schedule quality_proof protocol_capabilities cache_key".split(),
    "description": "description_distortion residual_metadata estimator_calibration precision_calibration composition_proof kernel_plan physical_schedule quality_proof protocol_capabilities cache_key".split(),
    "residual_estimator": "residual_metadata estimator_calibration precision_calibration composition_proof kernel_plan physical_schedule quality_proof protocol_capabilities cache_key".split(),
    "composition": "protected_trace_corpus observation_contract condition_metrics compatibility_witnesses atom_cover description_distortion residual_metadata estimator_calibration precision_calibration composition_proof kernel_plan physical_schedule quality_proof protocol_capabilities cache_key".split(),
    "precision": "page_layout semantic_manifest description_distortion residual_metadata estimator_calibration precision_calibration composition_proof kernel_plan physical_schedule quality_proof protocol_capabilities cache_key".split(),
    "tokenizer": "protected_trace_corpus semantic_manifest observation_contract condition_metrics compatibility_witnesses atom_cover description_distortion residual_metadata estimator_calibration precision_calibration composition_proof kernel_plan physical_schedule quality_proof protocol_capabilities cache_key".split(),
    "template": "protected_trace_corpus semantic_manifest observation_contract condition_metrics compatibility_witnesses atom_cover description_distortion residual_metadata estimator_calibration precision_calibration composition_proof kernel_plan physical_schedule quality_proof protocol_capabilities cache_key".split(),
    "context": "protected_trace_corpus semantic_manifest observation_contract condition_metrics compatibility_witnesses atom_cover description_distortion residual_metadata estimator_calibration precision_calibration composition_proof kernel_plan physical_schedule quality_proof protocol_capabilities cache_key".split(),
    "operator": "protected_trace_corpus semantic_manifest observation_contract condition_metrics compatibility_witnesses atom_cover description_distortion residual_metadata estimator_calibration precision_calibration composition_proof kernel_plan physical_schedule quality_proof protocol_capabilities cache_key".split(),
}


def _artifact(weights=(1.0, 0.0, 0.0, 1.0)):
    corpus = TRACE

    def apply(document):
        inputs = corpus["certificate_inputs"]
        document["model"].update(
            architecture="S25Dense",
            config={"fixture": "s25", "hidden_size": 2},
        )
        document["evidence"] = deepcopy(inputs["evidence"])
        document["eta_rep"] = 1
        document["rank_budget"] = inputs["rank_budget"]
        document["operation_bounds"] = deepcopy(inputs["operation_bounds"])
        document["operator_inventory"] = [deepcopy(corpus["operator_case"])]

    return compiler_artifact(
        "huggingface",
        "fixture/s25-dense",
        "git-sha1:" + "5" * 40,
        digest_bytes(b"S25 fixture license"),
        "model.safetensors",
        label="s25-generated-dense",
        mutate_manifest=apply,
        tensor=("F32", (2, 2), struct.pack("<4f", *weights)),
    )


def _source(material: IdentityTuple) -> dict:
    return {
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


def _compile(cartridge: Path, payload: bytes, material: IdentityTuple, name: str):
    incoming = cartridge / "incoming"
    incoming.mkdir(parents=True, exist_ok=True)
    physical = incoming / name
    physical.write_bytes(payload)
    descriptor = os.open(physical, os.O_RDONLY)
    try:
        source = _source(material)
        extents = {
            material.artifacts[0].path: {
                "fd": descriptor,
                "offset": 0,
                "length": len(payload),
                "operation_id": f"s25-{name}",
            }
        }
        plan = plan_revision(source, extents, cartridge)
        return prepare_revision(source, extents, cartridge, plan)
    finally:
        os.close(descriptor)


def _base(tmp_path: Path):
    cartridge = tmp_path / "cartridge"
    payload, material, _ = _artifact()
    legacy = _compile(cartridge, payload, material, "base.safetensors")
    commit_generation(
        cartridge,
        "s25-source-compile",
        legacy.candidate_root,
        expected_parent_root=None,
    )
    prepared = recompile_revision(
        cartridge,
        compilation_specification(cartridge, legacy.candidate_root),
        legacy.candidate_root,
    )
    commit_generation(
        cartridge,
        "s25-certified-compile",
        prepared.candidate_root,
        expected_parent_root=legacy.candidate_root,
    )
    return cartridge, prepared


def _mutate(axis: str, specification: dict) -> None:
    evidence = specification["evidence"]
    if axis == "condition_metric":
        metric = evidence["conditions"][0]["metric"]
        evidence["conditions"][0]["metric"] = [
            [2 if row == column else value for column, value in enumerate(values)]
            for row, values in enumerate(metric)
        ]
    elif axis == "atom":
        evidence["atoms"][0]["service_face_id"] = "face.s25-mutated"
    elif axis == "cover":
        evidence["observation_contract"]["selector"].reverse()
    elif axis == "observation":
        evidence["observation_contract"]["sample_count"] += 1
    elif axis == "description":
        evidence["atoms"][0]["description"]["description_bytes"] += 1
    elif axis == "residual_estimator":
        evidence["atoms"][0]["description"]["estimator"] = {
            "kind": "S25_RECORDED_FIXTURE_ESTIMATOR"
        }
    elif axis == "composition":
        evidence["trace_contract"]["protected_trace_family"] = {
            "name": "s25-composition-mutation"
        }
    elif axis == "precision":
        specification["precision_scheme"] = "f32;s25-plane=base"
    elif axis == "tokenizer":
        specification["tokenizer_digest"] = digest_bytes(b"S25 changed tokenizer")
    elif axis == "template":
        specification["template_digest"] = digest_bytes(b"S25 changed template")
    elif axis == "context":
        specification["profile"]["context_bytes"] += 1
    elif axis == "operator":
        case = {
            name: deepcopy(DISPATCH_ROWS[0][name])
            for name in specification["operator_inventory"][0]
        }
        specification["operator_inventory"] = [case]
        evidence["execution_contract"]["operations"][0]["operator_case_id"] = case["case_id"]
    elif axis != "weights":
        raise AssertionError(axis)


def _complete_input_mutations():
    return (
        ("condition_metric", lambda row: row["evidence"]["conditions"][0]["provenance"].update(source="s25")),
        ("observation", lambda row: row["evidence"]["excluded_conditions"][0]["evidence"].update(reason="still outside protected support")),
        ("description", lambda row: row["evidence"]["description_contract"]["description_family"].update(version="s25")),
        ("residual_estimator", lambda row: row["evidence"]["execution_contract"]["sampling_laws"][0].update(work_unit="ROWS")),
        ("composition", lambda row: row["operation_bounds"][0].update(epsilon_exec=0.25)),
        ("precision", lambda row: row.update(format_versions=[["safetensors", "2"]])),
        ("context", lambda row: row.update(architecture="S25DenseRecompiled")),
        ("context", lambda row: row.update(config_digest=digest_bytes(b"S25 changed config"))),
        ("context", lambda row: row.update(processor_digest=digest_bytes(b"S25 changed processor"))),
        ("context", lambda row: row["evidence"]["physical_conversion"]["conversion_rows"][0].update(latency_ns_peak=1)),
        ("context", lambda row: row["prior_mode_failures"][0].update(q38_record_digest=digest_bytes(b"S25 changed prior failure"))),
    )


def test_q19_q27_q61_q75_each_input_has_one_exact_incremental_closure_and_clean_root(tmp_path):
    """Q19/Q27/Q61/Q75: each changed digest regenerates only its transitive consumers and equals a clean compile."""

    cartridge, prepared = _base(tmp_path)
    root = load_root(cartridge, prepared.candidate_root)
    certificate = root["plans"][0]["certificate"]
    assert certificate["compatibility"]["cover"] == [
        {"atom_id": "atom", "condition_id": "common"},
        {"atom_id": "atom", "condition_id": "rare"},
    ]
    assert certificate["compatibility"]["excluded_conditions"] == [{
        "condition_id": "off-support",
        "cause": "OFF_SUPPORT",
        "evidence_digest": digest_bytes(canonical_bytes({
            "decision": "REJECT", "reason": "no immutable teacher trace"
        })),
    }]
    specification = compilation_specification(cartridge, prepared.candidate_root)
    parent_records = {
        row["artifact"]: row
        for row in root["plans"][0]["derivation"]["artifacts"]
    }
    weight_payload, weight_material, _ = _artifact((1.25, 0.0, 0.0, 1.0))
    weight_root = _compile(
        cartridge, weight_payload, weight_material, "weight-mutation.safetensors"
    )
    weight_source = load_root(cartridge, weight_root.candidate_root)["plans"][0]["source_root"]

    for axis in AXES:
        candidate_specification = deepcopy(specification)
        if axis == "weights":
            candidate_specification["source_root"] = weight_source
        else:
            _mutate(axis, candidate_specification)
        incremental = recompile_revision(
            cartridge, candidate_specification, prepared.candidate_root
        )
        clean = recompile_revision(cartridge, candidate_specification)
        expected = tuple(EXPECTED[axis])
        assert incremental.changed_inputs == (axis,)
        assert incremental.invalidated_artifacts == expected
        assert incremental.recomputed_artifacts == expected
        assert incremental.reused_artifacts == tuple(
            name for name in ARTIFACTS if name not in set(expected)
        )
        assert incremental.candidate_root == clean.candidate_root
        assert incremental.plan_digest == clean.plan_digest
        assert incremental.derivation_digest == clean.derivation_digest
        candidate_records = {
            row["artifact"]: row
            for row in load_root(cartridge, incremental.candidate_root)["plans"][0]["derivation"]["artifacts"]
        }
        assert all(
            candidate_records[name] != parent_records[name]
            for name in expected
        )
        assert all(
            candidate_records[name] == parent_records[name]
            for name in incremental.reused_artifacts
        )
        verify_bundle_structure(
            cartridge,
            incremental.candidate_root,
            incremental.source_identity,
            incremental.plan_digest,
        )
        assert pin_generation(cartridge).root_digest == prepared.candidate_root
        assert load_root(cartridge, prepared.candidate_root) == root

    for axis, mutate in _complete_input_mutations():
        candidate_specification = deepcopy(specification)
        mutate(candidate_specification)
        incremental = recompile_revision(
            cartridge, candidate_specification, prepared.candidate_root
        )
        assert incremental.changed_inputs == (axis,)
        assert incremental.invalidated_artifacts == tuple(EXPECTED[axis])
        assert incremental.candidate_root == recompile_revision(
            cartridge, candidate_specification
        ).candidate_root
        assert pin_generation(cartridge).root_digest == prepared.candidate_root

    malformed = deepcopy(specification)
    del malformed["profile"]
    with pytest.raises(CassetteError) as missing:
        recompile_revision(cartridge, malformed, prepared.candidate_root)
    assert missing.value.code == "INVALID_REQUEST"


def test_q19_q20_q37_q64_exact_and_fresh_replay_emit_only_simulated_machine_curves(tmp_path):
    """Q19/Q20/Q37/Q64: exact and seeded-fresh paths replay, and Q37 curves retain every separate resource."""

    cartridge, prepared = _base(tmp_path / "exact")
    root = load_root(cartridge, prepared.candidate_root)
    certificate = root["plans"][0]["certificate"]
    weights = struct.unpack("<4f", next(
        (cartridge / "incoming").glob("base.safetensors")
    ).read_bytes()[-16:])
    mx, _ = pager._mlx_runtime()
    exact_outputs = [
        pager.dispatch(
            "mlx.matmul.f32.3x2_2x2",
            (
                mx.array(TRACE["teacher_traces"][0]["inputs"], dtype=mx.float32),
                mx.array((weights[:2], weights[2:]), dtype=mx.float32),
            ),
        ).tolist()
        for _ in range(2)
    ]
    assert exact_outputs[0] == exact_outputs[1] == TRACE["teacher_traces"][0]["teacher_logits"]
    assert certificate["resources"]["eta_rep"] == 1.0
    assert certificate["resources"]["fresh_traffic_total"] == 0

    fresh_cartridge = tmp_path / "fresh" / "cartridge"
    sources = {}
    for name, payload in {
        "description": b"S25 description",
        "residual.zero": b"S25 residual zero",
        "residual.one": b"S25 residual one",
    }.items():
        path = tmp_path / "fresh" / f"{name}.safetensors"
        path.parent.mkdir(parents=True, exist_ok=True)
        _write_safetensors(path, ((name, "U8", (len(payload),), payload),))
        sources[path.name] = path
    fresh_root = import_safetensors(
        sources, fresh_cartridge, _identity(*sources.values())
    )
    pages = {
        row["semantic_tensor_id"]: row["spans"][0]["page_digest"]
        for row in load_root(fresh_cartridge, fresh_root)["tensor_maps"]
    }
    plan, fresh_certificate, evidence, profile, page_map = _stochastic_fixture(
        fresh_root, pages
    )

    async def replay():
        runs = []
        for _ in range(2):
            executor = pager.CertifiedPager(
                fresh_cartridge, plan, fresh_certificate, evidence, profile, page_map
            )
            outputs = []
            for step in range(3):
                result = await executor.execute(
                    _selection(fresh_certificate, evidence, step, seed=7)
                )
                outputs.append(result.output_digest)
            runs.append(tuple(outputs))
        return runs

    fresh_outputs = asyncio.run(replay())
    assert fresh_outputs[0] == fresh_outputs[1]
    assert fresh_certificate["resources"]["fresh_samples_total"] == 48
    assert fresh_certificate["resources"]["fresh_traffic_total"] == 144

    frontier = machine_fixture_frontier()
    assert CURVES.read_bytes() == canonical_bytes(frontier) + b"\n"
    assert frontier["claim"] == "PREDICTION_ONLY_NO_F4_F5_OR_PHYSICAL_QUALIFICATION"
    assert len(frontier["points"]) == 18
    assert {row["evidence_kind"] for row in frontier["profiles"]} == {
        "SIMULATED_RECORDED_CLASS"
    }
    exact = next(
        row for row in frontier["points"]
        if row["resource_vector"] == "f2-exact"
        and row["scale"] == "fixture"
        and row["storage_profile"] == "simulated-usbc-flash"
    )
    assert exact["page_count"] == 1
    assert exact["metadata_bytes_total"] == 332
    assert exact["predicted_loaded_bytes"] == 348
    assert exact["predicted_physical_service_ns"] == 2677
    assert exact["predicted_working_set_bytes"] == 4444


def test_q70_q73_q75_tier_a_and_tier_b_recovery_publish_only_clean_certified_children(tmp_path):
    """Q70/Q73/Q75: Tier A completes; Tier B consumes six committed records and publishes one clean Q19 child."""

    tier_a_cartridge, tier_a_parent, tier_a_parameters = _quantized_parent(
        tmp_path / "tier-a"
    )
    _, tier_a = _train(
        tier_a_cartridge,
        tier_a_parent,
        tier_a_parameters,
        "ADAPTER_SFT",
        SFT_BATCHES,
        "s25-tier-a",
    )
    tier_a_root = pin_generation(tier_a_cartridge).root_digest
    assert tier_a["tier"] == "A" and tier_a["operation"] == "ADAPTER_SFT"
    assert load_root(tier_a_cartridge, tier_a_root)["parents"] == [
        load_root(tier_a_cartridge, tier_a_parent)["identity"]
    ]

    cartridge, compiled_v1, parameters = _compiled_parent(tmp_path / "tier-b")
    specification = compilation_specification(cartridge, compiled_v1)
    compiled_v2 = recompile_revision(cartridge, specification, compiled_v1)
    commit_generation(
        cartridge,
        "s25-certified-parent",
        compiled_v2.candidate_root,
        expected_parent_root=compiled_v1,
    )
    parent_root = load_root(cartridge, compiled_v2.candidate_root)
    parent_derivation = parent_root["plans"][0]["derivation"]
    input_digests = parent_derivation["input_digests"]
    kinds = ("condition", "atom", "description", "estimator", "observation", "precision")
    axes = ("condition_metric", "atom", "description", "residual_estimator", "observation", "precision")
    calibrations = tuple(
        {
            "kind": kind,
            "input_digest": digest_bytes(f"s25-stale-{kind}".encode()),
            "output_digest": input_digests[axis],
            "sample_count": 32768,
            "loss": f"0.0{index + 1}",
        }
        for index, (kind, axis) in enumerate(zip(kinds, axes, strict=True))
    )
    hostile = tmp_path / "tier-b-hostile"
    shutil.copytree(cartridge, hostile)
    hostile_calibrations = list(deepcopy(calibrations))
    hostile_calibrations[0]["output_digest"] = digest_bytes(b"wrong recovered condition")
    _, _ = _train(
        hostile,
        compiled_v2.candidate_root,
        parameters,
        "COMPILED_RECOVERY",
        (RECOVERY_BATCH,),
        "s25-hostile-recovery",
        calibrations=tuple(hostile_calibrations),
    )
    hostile_training_root = pin_generation(hostile).root_digest
    with pytest.raises(CassetteError) as detached:
        prepare_recovered_revision(
            hostile, hostile_training_root, compiled_v2.candidate_root
        )
    assert detached.value.code == "CAPABILITY_MISMATCH"

    _, artifact = _train(
        cartridge,
        compiled_v2.candidate_root,
        parameters,
        "COMPILED_RECOVERY",
        (RECOVERY_BATCH,),
        "s25-tier-b-recovery",
        calibrations=calibrations,
    )
    training_root = pin_generation(cartridge).root_digest
    assert artifact["tier"] == "B" and artifact["operation"] == "COMPILED_RECOVERY"
    recovered = prepare_recovered_revision(
        cartridge, training_root, compiled_v2.candidate_root
    )
    expected_changes = tuple(name for name in AXES if name in set(axes))
    expected_invalidated = tuple(
        name for name in ARTIFACTS
        if any(name in EXPECTED[axis] for axis in axes)
    )
    assert recovered.changed_inputs == expected_changes
    assert recovered.invalidated_artifacts == expected_invalidated
    assert recovered.recomputed_artifacts == expected_invalidated
    assert recovered.reused_artifacts == ("page_stats",)
    assert pin_generation(cartridge).root_digest == training_root
    assert load_root(cartridge, compiled_v2.candidate_root) == parent_root
    plan, certificate, _, _, _ = verify_bundle_structure(
        cartridge,
        recovered.candidate_root,
        recovered.source_identity,
        recovered.plan_digest,
    )
    assert plan["invalidation_graph_digest"] == recovered.derivation_digest
    assert certificate == parent_root["plans"][0]["certificate"]
    child = load_root(cartridge, recovered.candidate_root)
    child_records = {
        row["artifact"]: row for row in child["plans"][0]["derivation"]["artifacts"]
    }
    parent_records = {
        row["artifact"]: row for row in parent_derivation["artifacts"]
    }
    assert all(
        child_records[name]["artifact_digest"] != parent_records[name]["artifact_digest"]
        for name in expected_invalidated
    )
    assert child_records["page_stats"] == parent_records["page_stats"]
    pin = commit_generation(
        cartridge,
        "s25-publish-recovered",
        recovered.candidate_root,
        expected_parent_root=training_root,
    )
    assert pin.root_digest == recovered.candidate_root
    assert load_root(cartridge, training_root)["identity"] == recovered.source_identity
