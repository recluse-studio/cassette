# test_s26_machine_gate.py — S26 successful machine integration and PHASE LIVE deferral (Q36); depends on broker.py, compiler.py, pager.py, store.py, tests/test_s21_trainer.py, tests/test_s23_failure_rows.py, tests/test_s24_interoperability.py, tools/resource_frontier.py.
"""Prove fixture-scale machine closure while withholding every live-model and hardware claim."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
import platform
import shutil

import pytest

from broker import CanonicalBroker
from compiler import (
    compilation_specification,
    plan_export,
    prepare_recovered_revision,
    recompile_revision,
    verify_bundle_structure,
)
from pager import admit_schedule
from store import (
    canonical_bytes,
    commit_generation,
    digest_bytes,
    import_export,
    load_root,
    pin_generation,
    read_tensor,
    release_capacity,
)
from test_s21_trainer import (
    RECOVERY_BATCH,
    SFT_BATCHES,
    _compiled_parent,
    _quantized_parent,
    _train,
)
from test_s23_failure_rows import MATRIX
from test_s24_interoperability import (
    _capacity,
    _machine_replay,
    _s24_artifact,
)
from tools.resource_frontier import machine_fixture_frontier


pytestmark = pytest.mark.skipif(
    platform.system() != "Darwin" or platform.machine() != "arm64",
    reason="S26 requires arm64 macOS, the pinned MLX runtime, and F_FULLFSYNC",
)

REPO = Path(__file__).resolve().parent.parent
MATRIX_PATH = REPO / "research" / "ACCEPTANCE_MATRIX.yaml"
GATE_PATH = REPO / "tests" / "fixtures" / "s26_machine_gate.json"
LIVE_ROWS_PATH = REPO / "tests" / "fixtures" / "s26_deferred_live_rows.json"
CURVES_PATH = REPO / "tools" / "generated" / "s25_resource_curves.json"
EXPECTED_RECOVERY_INPUTS = (
    "condition_metric", "atom", "observation", "description", "residual_estimator", "precision",
)
RECOVERY_BINDINGS = (
    ("condition", "condition_metric"),
    ("atom", "atom"),
    ("description", "description"),
    ("estimator", "residual_estimator"),
    ("observation", "observation"),
    ("precision", "precision"),
)
EXPECTED_RECOVERY_INVALIDATION = (
    "protected_trace_corpus", "page_layout", "semantic_manifest", "observation_contract",
    "condition_metrics", "compatibility_witnesses", "atom_cover", "description_distortion",
    "residual_metadata", "estimator_calibration", "precision_calibration", "composition_proof",
    "kernel_plan", "physical_schedule", "quality_proof", "protocol_capabilities", "cache_key",
)


def _compiler_capacity(label: str) -> dict:
    """Supply one simulated device to the compiler's exact candidate reservation."""

    return {
        "operation_id": f"s26-{label}",
        "device_bytes": 100 * 1024**3,
        "allocatable_verified_free": 100 * 1024**3,
        "reserve_extent": lambda _length: True,
        "release_extent": lambda _length: True,
    }


def _export(
    broker: CanonicalBroker,
    cartridge: Path,
    root_digest: str,
    target_schema: str,
    label: str,
) -> dict:
    """Run one capacity-admitted broker export and return its verified result."""

    request = {
        "protocol_version": "1",
        "operation": "export",
        "idempotency_key": f"s26-{label}",
        "target": root_digest,
        "arguments": {"target_schema": target_schema},
    }
    plan = plan_export(cartridge, root_digest, target_schema)
    reservation = _capacity(
        broker.operation_id(request), plan["reservation_bytes"]
    )
    try:
        operation = asyncio.run(
            broker.export_revision(request, cartridge, reservation)
        )
    finally:
        release_capacity(reservation)
    assert operation["state"] == "SUCCEEDED"
    return operation["result"]


def _portable_reimport(
    source: Path,
    result: dict,
    destination: Path,
    *,
    base_root: str | None = None,
) -> str:
    """Copy only the derivative package, then reconstruct it through store authority."""

    portable = destination.parent / f"{destination.name}-package"
    shutil.copytree(source / "exports", portable / "exports")
    return import_export(
        portable,
        result["export_id"],
        destination,
        base_root=base_root,
    )


def test_q36_phase_machine_integrates_success_path_and_records_only_live_deferrals(
    tmp_path,
    monkeypatch,
):
    """Q36 promotion readiness: close F0-F3 machine evidence and retain every F4/F5 row as NOT_RUN."""

    payload, material, _ = _s24_artifact()
    acquisition_directory = tmp_path / "acquisition"
    acquisition_directory.mkdir()
    acquired, cartridge, acquisition_broker = _machine_replay(
        acquisition_directory, monkeypatch, "huggingface", payload, material
    )
    assert acquired["state"] == "SUCCEEDED"
    compiled_root = acquired["result"]["root_digest"]
    compiled = load_root(cartridge, compiled_root)
    compiled_bundle = compiled["plans"][0]
    compiled_schedule = admit_schedule(
        compiled_bundle["execution_plan"],
        compiled_bundle["certificate"],
        compiled_bundle["evidence"],
        compiled_bundle["profile"],
    )

    compiled_export = _export(
        acquisition_broker,
        cartridge,
        compiled_root,
        "safetensors-v1",
        "compiled-export",
    )
    compiled_import = tmp_path / "compiled-reimport"
    reimported_root = _portable_reimport(
        cartridge, compiled_export, compiled_import
    )
    assert read_tensor(compiled_import, reimported_root, "weight") == read_tensor(
        cartridge, compiled_root, "weight"
    )
    assert load_root(compiled_import, reimported_root)["semantic_assets"] == compiled[
        "semantic_assets"
    ]
    acquisition_broker.close()

    tier_a, tier_a_base, tier_a_parameters = _quantized_parent(
        tmp_path / "tier-a"
    )
    tier_a_reimport = tmp_path / "tier-a-reimport"
    shutil.copytree(tier_a, tier_a_reimport)
    _, tier_a_artifact = _train(
        tier_a,
        tier_a_base,
        tier_a_parameters,
        "ADAPTER_SFT",
        (SFT_BATCHES[0],),
        "s26-tier-a",
    )
    tier_a_child = pin_generation(tier_a).root_digest
    tier_a_root = load_root(tier_a, tier_a_child)
    assert tier_a_artifact["tier"] == "A"
    assert tier_a_root["deltas"][-1]["kind"] == "adapter"
    adapter_broker = CanonicalBroker(tmp_path / "tier-a-export-log")
    adapter_export = _export(
        adapter_broker,
        tier_a,
        tier_a_child,
        "adapter-safetensors-v1",
        "adapter-export",
    )
    rebuilt_child = _portable_reimport(
        tier_a,
        adapter_export,
        tier_a_reimport,
        base_root=tier_a_base,
    )
    adapter_broker.close()
    assert rebuilt_child == tier_a_child
    assert load_root(tier_a_reimport, rebuilt_child)["deltas"] == tier_a_root["deltas"]

    tier_b, compiled_v1, tier_b_parameters = _compiled_parent(
        tmp_path / "tier-b"
    )
    compiled_v2 = recompile_revision(
        tier_b,
        compilation_specification(tier_b, compiled_v1),
        compiled_v1,
        **_compiler_capacity("tier-b-parent"),
    )
    commit_generation(
        tier_b,
        "s26-tier-b-parent",
        compiled_v2.candidate_root,
        expected_parent_root=compiled_v1,
    )
    certified_parent = load_root(tier_b, compiled_v2.candidate_root)
    input_digests = certified_parent["plans"][0]["derivation"]["input_digests"]
    calibrations = tuple(
        {
            "kind": kind,
            "input_digest": digest_bytes(f"s26-stale-{kind}".encode()),
            "output_digest": input_digests[axis],
            "sample_count": 32768,
            "loss": f"0.0{index + 1}",
        }
        for index, (kind, axis) in enumerate(RECOVERY_BINDINGS)
    )
    _, tier_b_artifact = _train(
        tier_b,
        compiled_v2.candidate_root,
        tier_b_parameters,
        "COMPILED_RECOVERY",
        (RECOVERY_BATCH,),
        "s26-tier-b",
        calibrations=calibrations,
    )
    training_root = pin_generation(tier_b).root_digest
    recovered = prepare_recovered_revision(
        tier_b,
        training_root,
        compiled_v2.candidate_root,
        **_compiler_capacity("tier-b-recovery"),
    )
    assert tier_b_artifact["tier"] == "B"
    assert recovered.changed_inputs == EXPECTED_RECOVERY_INPUTS
    assert recovered.invalidated_artifacts == EXPECTED_RECOVERY_INVALIDATION
    assert recovered.recomputed_artifacts == EXPECTED_RECOVERY_INVALIDATION
    assert recovered.reused_artifacts == ("page_stats",)
    plan, certificate, evidence, profile, _ = verify_bundle_structure(
        tier_b,
        recovered.candidate_root,
        recovered.source_identity,
        recovered.plan_digest,
    )
    recovered_schedule = admit_schedule(plan, certificate, evidence, profile)
    recovered_pin = commit_generation(
        tier_b,
        "s26-tier-b-recovered",
        recovered.candidate_root,
        expected_parent_root=training_root,
    )
    assert recovered_pin.root_digest == recovered.candidate_root

    frontier = machine_fixture_frontier()
    assert CURVES_PATH.read_bytes() == canonical_bytes(frontier) + b"\n"
    assert len(frontier["points"]) == 18
    assert {row["evidence_kind"] for row in frontier["profiles"]} == {
        "SIMULATED_RECORDED_CLASS"
    }
    assert frontier["claim"] == "PREDICTION_ONLY_NO_F4_F5_OR_PHYSICAL_QUALIFICATION"

    deferred = json.loads(LIVE_ROWS_PATH.read_bytes())
    assert canonical_bytes(deferred) + b"\n" == LIVE_ROWS_PATH.read_bytes()
    assert deferred["acceptance_matrix_digest"] == digest_bytes(MATRIX_PATH.read_bytes())
    assert deferred["matrix_id"] == "cassette-first-complete-release"
    assert deferred["claim"] == "DEFERRED_TO_PHASE_LIVE_NOT_RUN"
    assert deferred["phase_machine_outcome"] == "READY_FOR_LIVE_FALSIFICATION_ONLY"
    assert set(deferred["phases"]) == {"L01", "L02", "L03", "L04", "L05"}
    assert deferred["prohibited_evidence"] == [
        "F4_PASS", "F5_PASS", "frontier_capability", "hosted_comparison",
        "physical_drive_performance",
    ]
    matrix_text = MATRIX_PATH.read_text(encoding="utf-8")
    named_values = []
    for phase in deferred["phases"].values():
        for value in phase.values():
            if isinstance(value, str):
                named_values.append(value)
            elif isinstance(value, list):
                named_values.extend(
                    item["id"] if isinstance(item, dict) else item for item in value
                )
    exempt = {
        "Q41", "Q42", "Q43", "Q44", "Q80", "PASS_AND_LIVE_PROVEN",
        "3-8B dense, permissive license", "20-120B sparse",
        "actual_read_only_external_remount", "bus_reset_on_physical_transport",
        "copied_replacement_on_actual_media", "host_sleep_with_active_external_io",
        "live_source_revision_drift", "physical_usb_c_detach_and_reattach",
        "port_migration_on_physical_transport", "real_drive_exhaustion",
    }
    assert all(value in matrix_text for value in named_values if value not in exempt)

    outcome = {
        "version": 1,
        "claim": "PHASE_MACHINE_PASS_READY_FOR_LIVE_FALSIFICATION_ONLY",
        "acceptance_matrix_digest": digest_bytes(MATRIX_PATH.read_bytes()),
        "deferred_live_manifest_digest": digest_bytes(LIVE_ROWS_PATH.read_bytes()),
        "evidence": {
            "acquisition_compilation": {
                "state": acquired["state"],
                "compiled_root": compiled_root,
                "certificate_id": compiled_schedule.certificate_id,
                "plan_id": compiled_schedule.plan_id,
            },
            "failure_matrix": {
                "assertion_count": len(MATRIX.assertions),
                "coordinate_count": len(MATRIX.operations) * len(MATRIX.injections),
                "injection_count": len(MATRIX.injections),
                "operation_count": len(MATRIX.operations),
            },
            "portable_export_reimport": {
                "export_id": compiled_export["export_id"],
                "reimported_root": reimported_root,
                "tensor_digest": digest_bytes(
                    read_tensor(compiled_import, reimported_root, "weight")
                ),
            },
            "tier_a_delta": {
                "base_root": tier_a_base,
                "child_root": tier_a_child,
                "delta_id": tier_a_root["deltas"][-1]["delta_id"],
                "export_id": adapter_export["export_id"],
                "rebuilt_child": rebuilt_child,
            },
            "tier_b_recovery": {
                "training_root": training_root,
                "recovered_root": recovered.candidate_root,
                "certificate_id": recovered_schedule.certificate_id,
                "plan_id": recovered_schedule.plan_id,
                "changed_inputs": list(recovered.changed_inputs),
                "invalidated_artifacts": list(recovered.invalidated_artifacts),
            },
            "simulated_resources": {
                "frontier_digest": digest_bytes(canonical_bytes(frontier)),
                "point_count": len(frontier["points"]),
                "profile_count": len(frontier["profiles"]),
            },
        },
        "live_evidence": "NOT_RUN",
    }
    recorded = json.loads(GATE_PATH.read_bytes())
    assert canonical_bytes(recorded) + b"\n" == GATE_PATH.read_bytes()
    assert outcome == recorded
