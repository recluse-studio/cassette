# test_s26_machine_gate.py — S26 successful machine integration and PHASE LIVE deferral (Q36); depends on broker.py, compiler.py, pager.py, store.py, tests/test_s21_trainer.py, tests/test_s23_failure_rows.py, tests/test_s24_interoperability.py, tools/resource_frontier.py.
"""Prove fixture-scale machine closure while withholding every live-model and hardware claim."""

from __future__ import annotations

import asyncio
from copy import deepcopy
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


def _matrix_block(name: str) -> tuple[str, ...]:
    """Return one top-level matrix block without interpreting unrelated YAML."""

    lines = MATRIX_PATH.read_text(encoding="utf-8").splitlines()
    start = lines.index(f"{name}:") + 1
    end = next(
        (index for index in range(start, len(lines)) if lines[index] and not lines[index].startswith(" ")),
        len(lines),
    )
    return tuple(lines[start:end])


def _direct_fields(name: str) -> dict[str, object]:
    """Parse direct scalar and scalar-list fields from one bounded matrix block."""

    fields: dict[str, object] = {}
    current: str | None = None
    for line in _matrix_block(name):
        if not line.strip():
            continue
        if line.startswith("  ") and not line.startswith("    ") and ":" in line:
            current, raw = line.strip().split(":", 1)
            if raw.strip():
                value = raw.strip()
                fields[current] = value == "true" if value in {"true", "false"} else value
                current = None
            else:
                fields[current] = []
            continue
        if line.startswith("    - ") and current is not None:
            values = fields[current]
            assert isinstance(values, list)
            values.append(line.removeprefix("    - "))
            continue
        current = None
    return fields


def _mapping_records(name: str) -> dict[str, dict[str, str]]:
    """Parse direct records from a top-level keyed matrix mapping."""

    records: dict[str, dict[str, str]] = {}
    current: str | None = None
    for line in _matrix_block(name):
        if line.startswith("  ") and not line.startswith("    ") and line.endswith(":"):
            current = line.strip()[:-1]
            records[current] = {}
        elif current is not None and line.startswith("    ") and not line.startswith("      ") and ":" in line:
            field, value = line.strip().split(":", 1)
            records[current][field] = value.strip()
    return records


def _list_records(name: str) -> tuple[dict[str, str], ...]:
    """Parse direct scalar fields from a top-level matrix list of records."""

    records: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in _matrix_block(name):
        if line.startswith("  - id: "):
            current = {"id": line.removeprefix("  - id: ")}
            records.append(current)
        elif current is not None and line.startswith("    ") and not line.startswith("      ") and ":" in line:
            field, value = line.strip().split(":", 1)
            current[field] = value.strip()
    return tuple(records)


def _validate_deferred_manifest(deferred: dict) -> None:
    """Resolve every deferred field through its exact matrix section."""

    top = {
        line.split(":", 1)[0]: line.split(":", 1)[1].strip()
        for line in MATRIX_PATH.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith(" ") and ": " in line
    }
    completion = _direct_fields("completion_rule")
    boundary = _direct_fields("phase_machine_deferral")
    models = _mapping_records("immutable_models")
    gates = _list_records("fixture_gate_rows")
    assert set(deferred) == {
        "acceptance_matrix_digest", "claim", "matrix_id", "matrix_schema_version",
        "live_evidence", "phase_machine_outcome", "phases", "prohibited_evidence",
        "version",
    }
    assert deferred["acceptance_matrix_digest"] == digest_bytes(MATRIX_PATH.read_bytes())
    assert deferred["matrix_id"] == top["matrix_id"]
    assert deferred["matrix_schema_version"] == int(top["schema_version"])
    assert deferred["claim"] == "DEFERRED_TO_PHASE_LIVE_NOT_RUN"
    assert deferred["live_evidence"] == boundary["live_evidence"]
    assert deferred["phase_machine_outcome"] == boundary["outcome"]
    assert deferred["prohibited_evidence"] == boundary["prohibited_evidence"]
    assert list(deferred["phases"]) == boundary["phases"]

    l01 = deferred["phases"]["L01"]
    storage = _mapping_records("storage_classes")
    assert l01 == {
        "apple_classes": list(_mapping_records("apple_classes")),
        "qualification": sorted({record["profile_contract"] for record in storage.values()}),
        "storage_classes": list(storage),
    }
    assert deferred["phases"]["L02"] == {
        "immutable_models": [
            {"id": model_id, "revision": record["revision"]}
            for model_id, record in models.items()
        ],
        "source_rows": [record["id"] for record in _list_records("source_rows")],
    }
    assert deferred["phases"]["L03"] == {
        "fixture_gates": [
            {"id": record["id"], "model_class": record["model_class"]}
            for record in gates
        ],
    }
    assert deferred["phases"]["L04"] == {
        "execution_rows": [record["id"] for record in _list_records("execution_rows")],
        "offline_rows": [record["id"] for record in _list_records("offline_and_privacy_rows")],
        "protocol_cross_product": _direct_fields("protocol_cross_product")["id"],
        "remaining_failure_injections": list(MATRIX.phase_live_injections),
        "training_rows": [record["id"] for record in _list_records("training_rows")],
        "workload_suites": [record["id"] for record in _list_records("workload_suites")],
    }
    assert deferred["phases"]["L05"] == {
        "completion_contract": completion["contract"],
        "require_live_evidence": completion["require_live_evidence"],
        "required_status": completion["required_status"],
    }


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
    _validate_deferred_manifest(deferred)
    for replacement in ("physical_usb_c_detach_and_reattach", "cancellation"):
        unsupported = deepcopy(deferred)
        unsupported["phases"]["L04"]["remaining_failure_injections"][0] = replacement
        with pytest.raises(AssertionError):
            _validate_deferred_manifest(unsupported)
    wrong_revision = deepcopy(deferred)
    wrong_revision["phases"]["L02"]["immutable_models"][0]["revision"] = "0" * 40
    with pytest.raises(AssertionError):
        _validate_deferred_manifest(wrong_revision)

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
