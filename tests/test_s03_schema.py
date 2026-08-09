# test_s03_schema.py — F0 fixtures for the S03 Q6/Q9/Q31/Q50/Q57 contracts; depends on tools/genschema.py, schema/validator.py, tools/ledger.py.
"""S03 proves the generated contracts, serialization round-trip, and hand-edit rejection."""

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

from schema.validator import validate
from tools.genschema import emit
from tools.ledger import check_generated_integrity

REPO = Path(__file__).resolve().parent.parent
EXPECTED_KINDS = {
    "capability_profile",
    "error",
    "execution_plan",
    "mathematical_certificate",
    "operation",
    "operator_dispatch",
    "remote_metadata",
    "remote_metadata_field",
    "request",
    "root",
    "run_event",
    "run_request",
    "source_descriptor",
    "tensor_map",
    "tensor_span",
}
REMOTE_FIELDS = {
    "identity",
    "total_bytes",
    "artifact_count",
    "artifact_digests",
    "format",
    "architecture",
    "total_parameters",
    "active_parameters",
    "dtype_quantization",
    "context",
    "modalities",
    "operators",
    "custom_code",
    "tokenizer",
    "processor",
    "template",
    "license",
    "gating",
    "revision_ancestry",
    "training_precision",
    "source_validators",
}
EXPECTED_FIELDS = {
    "error": {"code", "object_id", "failed_invariant", "retryability", "detail"},
    "request": {"protocol_version", "operation", "idempotency_key", "target", "arguments"},
    "operation": {"operation_id", "kind", "state", "progress", "result", "error"},
    "capability_profile": {
        "protocol_version", "model_refs", "modalities", "context", "reasoning", "tools",
        "structured_output", "streaming", "cancellation", "training", "source",
        "performance_tiers",
    },
    "run_request": {
        "idempotency_key", "model_ref", "input", "context_ref", "generation", "reasoning",
        "output_schema", "tools",
    },
    "run_event": {"run_id", "sequence", "type", "payload"},
    "source_descriptor": {
        "kind", "locator", "revision", "artifact_selector", "credential_ref",
        "license_acceptance_ref", "expected_identity",
    },
    "remote_metadata_field": {"value", "trust", "authority"},
    "remote_metadata": REMOTE_FIELDS | {"conflicts"},
    "tensor_span": {"page_digest", "offset", "length", "tensor_offset"},
    "tensor_map": {"semantic_tensor_id", "shape", "dtype", "codec", "plane", "spans"},
    "root": {
        "identity", "parents", "provenance", "semantic_assets", "tensor_maps", "operators",
        "plans", "deltas", "integrity_root",
    },
    "mathematical_certificate": {
        "certificate_version", "certificate_id", "target", "condition_metrics",
        "compatibility", "atoms", "description_contract", "observation_contract", "execution_contract",
        "trace_contract", "resources", "resource_tables", "physical_conversion",
    },
    "operator_dispatch": {
        "dispatch_version", "runtime_name", "runtime_version", "runtime_commit",
        "dispatch_digest", "case_ids", "apple_features",
    },
    "execution_plan": {
        "plan_version", "plan_id", "selected_mode", "prior_mode_failures", "target_digest",
        "profile_digest", "certificate_id", "tensor_graph_digest", "page_map_digest",
        "layout_digest", "precision_planes_digest", "semantic_manifest_digest",
        "invalidation_graph_digest", "dispatch", "resource_limits", "artifact_refs",
        "weight_payload_bytes",
    },
}
EXPECTED_OPTIONAL = {
    "request": {"target"},
    "operation": {"result", "error"},
    "run_request": {"context_ref", "reasoning", "output_schema", "tools"},
    "source_descriptor": {
        "revision", "artifact_selector", "credential_ref", "license_acceptance_ref",
        "expected_identity",
    },
    "remote_metadata_field": {"value"},
}


def metadata(value=None, trust="ABSENT", authority="fixture:no-evidence"):
    item = {"trust": trust, "authority": authority}
    if trust != "ABSENT":
        item["value"] = value
    return item


REMOTE_GOLDEN = {name: metadata() for name in REMOTE_FIELDS}
REMOTE_GOLDEN.update(
    {
        "identity": metadata("I-abc", "EVIDENCE_DIGESTED", "manifest:sha256:01"),
        "total_bytes": metadata(1_560_936_091_448, "EVIDENCE_DIGESTED", "manifest:sha256:01"),
        "artifact_count": metadata(96, "EVIDENCE_DIGESTED", "manifest:sha256:01"),
        "format": metadata("safetensors", "PARSED", "header:sha256:02"),
        "architecture": metadata("fixture-architecture", "PARSED", "config:sha256:03"),
        "total_parameters": metadata(1_000_000_000_000, "PARSED", "index:sha256:04"),
        "dtype_quantization": metadata("bf16", "PARSED", "header:sha256:02"),
        "context": metadata(262_144, "DECLARED", "config:sha256:03"),
        "modalities": metadata(["text", "vision"], "DECLARED", "config:sha256:03"),
        "custom_code": metadata(False, "PARSED", "config:sha256:03"),
        "tokenizer": metadata("sha256:05", "EVIDENCE_DIGESTED", "manifest:sha256:01"),
        "processor": metadata("sha256:06", "EVIDENCE_DIGESTED", "manifest:sha256:01"),
        "template": metadata("sha256:07", "EVIDENCE_DIGESTED", "manifest:sha256:01"),
        "license": metadata("modified-mit", "DECLARED", "card:sha256:08"),
        "gating": metadata(False, "DECLARED", "source-api:sha256:09"),
        "revision_ancestry": metadata(["rev-parent"], "EVIDENCE_DIGESTED", "manifest:sha256:01"),
        "source_validators": metadata(
            {"etag": "fixture-etag"}, "EVIDENCE_DIGESTED", "source-api:sha256:09"
        ),
        "conflicts": [
            {
                "field": "architecture",
                "candidates": [
                    metadata("card-claim", "DECLARED", "card:sha256:08"),
                    metadata("fixture-architecture", "PARSED", "config:sha256:03"),
                ],
            }
        ],
    }
)

SPAN = {"page_digest": "blake3:00ff", "offset": 0, "length": 4096, "tensor_offset": 0}
TENSOR_MAP = {
    "semantic_tensor_id": "model.layers.0.weight",
    "shape": [32, 32],
    "dtype": "bf16",
    "codec": "raw",
    "plane": 0,
    "spans": [SPAN],
}
DIGESTS = [f"blake3:{digit * 64}" for digit in "0123456789abcdef"]
RESOURCES = {
    "eta_rep": 0.125,
    "epsilon_exec": 0.01,
    "delta_exec_total": 0.001,
    "atom_count": 1,
    "max_atom_rank": 1,
    "description_bytes_peak": 4096,
    "description_bytes_total": 4096,
    "metadata_bytes_peak": 1024,
    "metadata_bytes_total": 1024,
    "fresh_samples_max": 0,
    "fresh_samples_total": 0,
    "fresh_traffic_max": 0,
    "fresh_traffic_total": 0,
    "fresh_traffic_unit": "BYTES",
    "horizon": 1,
}
OPERATOR_DISPATCH = {
    "dispatch_version": "q30-v1",
    "runtime_name": "mlx",
    "runtime_version": "0.31.0",
    "runtime_commit": "365d6f29b47686a9f5401f6a9ec5825fee162d69",
    "dispatch_digest": "sha256:db0c5bae5819952f448174049b5acbb1dcc95ccd49437da45c881eed7250b32f",
    "case_ids": [
        "mlx.matmul.f32.2x3_3x2",
        "mlx.quantized_matmul.affine4.f32.1x32_2x32",
        "mlx.rms_norm.f32.2x4",
        "mlx.rope.traditional.f32.1x1x2x4",
        "mlx.attention.f32.1x1x2x2",
        "mlx.conv1d.f32.1x4x1_1x2x1",
        "mlx.embedding.f32_u32.4x3_2",
        "mlx.categorical.f32_u32.2x3_2",
        "mlx.autograd_sum.f32.2x3",
        "mlx.sgd.f32.3",
    ],
    "apple_features": ["apple_silicon", "metal"],
}
MATHEMATICAL_CERTIFICATE = {
    "certificate_version": "q19-v1",
    "certificate_id": DIGESTS[0],
    "target": {
        "target_digest": DIGESTS[1],
        "flattening_digest": DIGESTS[2],
        "shape": [2, 2],
        "field": "REAL",
    },
    "condition_metrics": [
        {
            "condition_id": "condition.a",
            "provenance_digest": DIGESTS[3],
            "metric_digest": DIGESTS[4],
            "positive_definite_witness_digest": DIGESTS[5],
        },
        {
            "condition_id": "condition.b",
            "provenance_digest": DIGESTS[6],
            "metric_digest": DIGESTS[7],
            "positive_definite_witness_digest": DIGESTS[8],
        },
    ],
    "compatibility": {
        "eta_rep": 0.125,
        "rank_budget": 1,
        "service_faces": [
            {"face_id": "face.ab", "condition_ids": ["condition.a", "condition.b"]}
        ],
        "minimal_nonfaces": [],
        "cover": [
            {"condition_id": "condition.a", "atom_id": "atom.ab"},
            {"condition_id": "condition.b", "atom_id": "atom.ab"},
        ],
        "excluded_conditions": [],
    },
    "atoms": [
        {
            "atom_id": "atom.ab",
            "witness_digest": DIGESTS[9],
            "rank": 1,
            "service_face_id": "face.ab",
            "witness_losses": [
                {"condition_id": "condition.a", "loss": 0.1},
                {"condition_id": "condition.b", "loss": 0.125},
            ],
            "description": {
                "class": "EXACT",
                "reconstruction_digest": DIGESTS[10],
                "residual_relation_digest": DIGESTS[11],
                "distortion_bound": 0.01,
                "estimator_digest": DIGESTS[12],
                "estimator_calibration_digest": DIGESTS[13],
                "sampling_law_id": "sampling.exact",
            },
        }
    ],
    "description_contract": {
        "description_family_digest": DIGESTS[10],
        "distortion_metric_digest": DIGESTS[11],
        "residual_family_digest": DIGESTS[12],
        "estimator_family_digest": DIGESTS[13],
    },
    "observation_contract": {
        "kind": "PROTECTED_TEST_LAW",
        "experiment_digest": DIGESTS[12],
        "support_digest": DIGESTS[13],
        "selector_digest": DIGESTS[14],
        "loss_family_digest": DIGESTS[15],
        "sample_count": 256,
        "confidence": 0.99,
        "off_support": "REJECT",
    },
    "execution_contract": {
        "sampling_laws": [
            {
                "sampling_law_id": "sampling.exact",
                "kind": "EXACT",
                "law_digest": DIGESTS[11],
                "work_unit": "PAGES",
                "seed_policy": "NONE",
            }
        ],
        "operations": [
            {
                "operation_id": "operation.matmul",
                "operator_case_id": "mlx.matmul.f32.2x3_3x2",
                "rank_accounting_digest": DIGESTS[2],
                "loss_propagation_digest": DIGESTS[4],
                "remainder_bound": 0.0,
                "epsilon_exec": 0.01,
                "delta_exec": 0.001,
                "sampling_law_id": "sampling.exact",
            }
        ],
        "risk_composition_kind": "UNION_BOUND",
        "risk_composition_digest": DIGESTS[5],
    },
    "trace_contract": {
        "protected_trace_family_digest": DIGESTS[6],
        "schedule_digest": DIGESTS[7],
        "prefix_policy": "COHERENT_RESTRICTION",
        "horizon": 1,
    },
    "resources": RESOURCES,
    "resource_tables": {
        "per_atom": [
            {
                "atom_id": "atom.ab",
                "description_bytes": 4096,
                "metadata_bytes": 1024,
                "fresh_samples_max": 0,
                "fresh_samples_total": 0,
                "fresh_traffic_max": 0,
                "fresh_traffic_total": 0,
                "epsilon_exec": 0.01,
                "delta_exec": 0.001,
            }
        ],
        "per_operation": [
            {
                "operation_id": "operation.matmul",
                "description_bytes_peak": 4096,
                "description_bytes_total": 4096,
                "metadata_bytes_peak": 1024,
                "metadata_bytes_total": 1024,
                "fresh_samples_max": 0,
                "fresh_samples_total": 0,
                "fresh_traffic_max": 0,
                "fresh_traffic_total": 0,
                "epsilon_exec": 0.01,
                "delta_exec": 0.001,
            }
        ],
        "per_trace_step": [
            {
                "step": 0,
                "operation_id": "operation.matmul",
                "atom_id": "atom.ab",
                "description_bytes_resident": 4096,
                "metadata_bytes_resident": 1024,
                "fresh_samples": 0,
                "fresh_traffic": 0,
                "epsilon_exec": 0.01,
                "delta_exec": 0.001,
            }
        ],
    },
    "physical_conversion": {
        "conversion_rows": [
            {
                "operation_id": "operation.matmul",
                "probe_unit": "BLOCKS",
                "probes": 1,
                "page_reads": 1,
                "bytes": 4096,
                "memory_bytes_peak": 5120,
                "latency_ns_peak": 1000,
            }
        ],
        "conversion_digest": DIGESTS[8],
    },
}
EXECUTION_PLAN = {
    "plan_version": "compiled-plan-v1",
    "plan_id": DIGESTS[9],
    "selected_mode": "COMPILED_CERTIFIED",
    "prior_mode_failures": [
        {"ordinal": index + 1, "mode": mode, "q38_record_digest": DIGESTS[index + 10]}
        for index, mode in enumerate(
            [
                "BYTE_IDENTICAL_LAYOUT",
                "EXACT_NATIVE_SPARSITY",
                "EXACT_QUANTIZED_LAYOUT",
                "NATIVE_PREDICTIVE_PREFETCH",
            ]
        )
    ],
    "target_digest": DIGESTS[1],
    "profile_digest": DIGESTS[2],
    "certificate_id": DIGESTS[0],
    "tensor_graph_digest": DIGESTS[3],
    "page_map_digest": DIGESTS[4],
    "layout_digest": DIGESTS[5],
    "precision_planes_digest": DIGESTS[6],
    "semantic_manifest_digest": DIGESTS[7],
    "invalidation_graph_digest": DIGESTS[8],
    "dispatch": OPERATOR_DISPATCH,
    "resource_limits": RESOURCES,
    "artifact_refs": [DIGESTS[1]],
    "weight_payload_bytes": 0,
}
GOLDEN = {
    "error": {
        "code": "PAGE_CORRUPT",
        "object_id": "page:blake3:00ff",
        "failed_invariant": "Q62: digest must match before residency",
        "retryability": "terminal",
        "detail": "",
    },
    "request": {
        "protocol_version": "1",
        "operation": "run",
        "idempotency_key": "request-1",
        "arguments": {},
    },
    "operation": {
        "operation_id": "operation-1",
        "kind": "acquire",
        "state": "RUNNING",
        "progress": 0.5,
    },
    "capability_profile": {
        "protocol_version": "1",
        "model_refs": ["revision:I-abc"],
        "modalities": ["text", "vision"],
        "context": {"maximum_tokens": 262_144},
        "reasoning": {"supported": True},
        "tools": {"supported": True},
        "structured_output": {"supported": True},
        "streaming": True,
        "cancellation": True,
        "training": {"tiers": ["adapter"]},
        "source": {"kinds": ["huggingface"]},
        "performance_tiers": [{"id": "frontier-class"}],
    },
    "run_request": {
        "idempotency_key": "run-request-1",
        "model_ref": "revision:I-abc",
        "input": [{"role": "user", "content": "hello"}],
        "generation": {"max_output_tokens": 64},
        "reasoning": {"effort": "high"},
        "output_schema": {"type": "object"},
        "tools": [{"name": "fixture"}],
    },
    "run_event": {
        "run_id": "run-1",
        "sequence": 3,
        "type": "output_delta",
        "payload": {"text": "x"},
    },
    "source_descriptor": {
        "kind": "huggingface",
        "locator": "org/model",
        "revision": "immutable-revision",
        "credential_ref": "keychain:item-1",
    },
    "remote_metadata_field": metadata(
        1_560_936_091_448, "EVIDENCE_DIGESTED", "manifest:sha256:01"
    ),
    "remote_metadata": REMOTE_GOLDEN,
    "tensor_span": SPAN,
    "tensor_map": TENSOR_MAP,
    "mathematical_certificate": MATHEMATICAL_CERTIFICATE,
    "operator_dispatch": OPERATOR_DISPATCH,
    "execution_plan": EXECUTION_PLAN,
    "root": {
        "identity": "I-abc",
        "parents": ["I-parent"],
        "provenance": {"source": "huggingface"},
        "semantic_assets": {"tokenizer": "sha256:05"},
        "tensor_maps": [TENSOR_MAP],
        "operators": ["matmul"],
        "plans": ["plan:c1"],
        "deltas": [],
        "integrity_root": "merkle:abc",
    },
}


def install_generator(root: Path) -> None:
    """Give a scratch generated tree the same source authority used by the repository."""
    (root / "tools").mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO / "tools" / "genschema.py", root / "tools" / "genschema.py")
    shutil.copy2(REPO / "errors.py", root / "errors.py")
    shutil.copy2(REPO / "MATHS.md", root / "MATHS.md")


def run_generator(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(root / "tools" / "genschema.py")],
        cwd=root,
        capture_output=True,
        text=True,
    )


def test_exact_contract_set_is_json_schema_and_round_trips():
    """Q6/Q9/Q31/Q50/Q57: every specified record is generated, exact, and JSON-round-trippable."""
    assert set(GOLDEN) == EXPECTED_KINDS
    assert {path.stem for path in (REPO / "schema").glob("*.json") if path.name != "MANIFEST.json"} == EXPECTED_KINDS
    for kind, obj in GOLDEN.items():
        schema = json.loads((REPO / "schema" / f"{kind}.json").read_text(encoding="utf-8"))
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert schema["$id"] == f"https://recluse.studio/cassette/schema/v1/{kind}.json"
        assert schema["type"] == "object" and schema["additionalProperties"] is False
        assert validate(kind, obj) == [], f"{kind} golden rejected"
        decoded = json.loads(json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True))
        assert decoded == obj
        assert validate(kind, decoded) == [], f"{kind} round-trip rejected"


def test_q31_q50_q57_shapes_are_complete():
    """Q6/Q9/Q31/Q50/Q57: every formal record has its complete exact field boundary."""
    assert set(EXPECTED_FIELDS) == EXPECTED_KINDS
    for kind, fields in EXPECTED_FIELDS.items():
        schema = json.loads((REPO / "schema" / f"{kind}.json").read_text(encoding="utf-8"))
        assert set(schema["properties"]) == fields
        assert set(schema["required"]) == fields - EXPECTED_OPTIONAL.get(kind, set())
    root = json.loads((REPO / "schema" / "root.json").read_text())
    assert root["x-cassette-canonicalization"] == "RFC8785"


def test_malformed_f0_instances_are_rejected():
    """Q6/Q9/Q31/Q50/Q57: F0 rejects omissions, type errors, unknowns, bad bounds, and bad refs."""
    missing = dict(GOLDEN["error"])
    del missing["code"]
    assert any("required field missing" in defect for defect in validate("error", missing))
    assert any(
        "bool is not" in defect
        for defect in validate("run_event", {**GOLDEN["run_event"], "sequence": True})
    )
    assert any(
        "unknown field" in defect
        for defect in validate("source_descriptor", {**GOLDEN["source_descriptor"], "secret": "x"})
    )
    assert any(
        "expected number" in defect
        for defect in validate("operation", {**GOLDEN["operation"], "progress": "half"})
    )
    incomplete_remote = dict(GOLDEN["remote_metadata"])
    del incomplete_remote["format"]
    assert any("remote_metadata.format: required" in defect for defect in validate("remote_metadata", incomplete_remote))
    bad_trust = {
        **GOLDEN["remote_metadata"],
        "format": {**GOLDEN["remote_metadata"]["format"], "trust": "GUESSED"},
    }
    assert any("not in enum" in defect for defect in validate("remote_metadata", bad_trust))
    bad_conflict = {
        **GOLDEN["remote_metadata"],
        "conflicts": [{"field": "architecture", "candidates": [metadata()]}],
    }
    assert any("requires at least 2" in defect for defect in validate("remote_metadata", bad_conflict))
    bad_span = {**GOLDEN["tensor_map"], "spans": [{**SPAN, "length": 0}]}
    assert any("below 1" in defect for defect in validate("tensor_map", bad_span))
    bad_error = {**GOLDEN["operation"], "error": {"code": "PAGE_CORRUPT"}}
    assert any("required field missing" in defect for defect in validate("operation", bad_error))
    assert validate("no_such_kind", {}) == ["unknown contract kind 'no_such_kind'"]


def test_generator_is_deterministic_and_ledger_rejects_coordinated_hand_edits(tmp_path):
    """Q33/Q57/q78_exact_accounting: MATHS authority and regeneration fail closed."""
    first, second = tmp_path / "first", tmp_path / "second"
    install_generator(first)
    install_generator(second)
    manifest1 = emit(first / "schema")
    manifest2 = emit(second / "schema")
    assert manifest1 == manifest2
    assert {
        path.name: path.read_bytes()
        for path in (first / "schema").iterdir()
        if path.is_file()
    } == {
        path.name: path.read_bytes()
        for path in (second / "schema").iterdir()
        if path.is_file()
    }

    committed = {
        path.relative_to(REPO / "schema").as_posix(): path.read_bytes()
        for path in sorted((REPO / "schema").rglob("*"))
        if path.is_file() and path.name != "MANIFEST.json" and "__pycache__" not in path.parts
    }
    fresh = {name: (first / "schema" / name).read_bytes() for name in manifest1}
    assert committed == fresh, "committed schema/ differs from fresh generator output"
    assert check_generated_integrity(first) == ("ran", [])

    begin = "<!-- CASSETTE_CERTIFICATE_DIMENSIONS_BEGIN -->"
    end = "<!-- CASSETTE_CERTIFICATE_DIMENSIONS_END -->"
    authority_mutations = {
        "missing": lambda text: text.replace(begin, "", 1).replace(end, "", 1),
        "multiple": lambda text: text.replace(begin, begin + "\n" + begin, 1),
        "malformed": lambda text: text.replace('"eta_rep",', '"eta_rep",,', 1),
        "duplicate": lambda text: text.replace('"epsilon_exec"', '"eta_rep"', 1),
        "added": lambda text: text.replace('"eta_rep",', '"eta_rep",\n    "new_dimension",', 1),
        "removed": lambda text: text.replace('    "eta_rep",\n', "", 1),
        "renamed": lambda text: text.replace('"eta_rep"', '"eta_represented"', 1),
    }
    for name, mutate in authority_mutations.items():
        mutant = tmp_path / f"authority-{name}"
        shutil.copytree(second, mutant)
        maths = mutant / "MATHS.md"
        maths.write_text(mutate(maths.read_text(encoding="utf-8")), encoding="utf-8")
        result = run_generator(mutant)
        assert result.returncode != 0, f"{name} authority mutation regenerated successfully"

    stale = tmp_path / "stale-maths"
    shutil.copytree(second, stale)
    maths = stale / "MATHS.md"
    source = maths.read_text(encoding="utf-8")
    source = source.replace(
        '    "eta_rep",\n    "epsilon_exec",',
        '    "epsilon_exec",\n    "eta_rep",',
        1,
    )
    maths.write_text(source, encoding="utf-8")
    status, violations = check_generated_integrity(stale)
    assert status == "ran"
    assert any("tools/genschema.py" in violation for violation in violations)
    regenerated = run_generator(stale)
    assert regenerated.returncode == 0, regenerated.stderr
    tables = (stale / "schema" / "tables.py").read_text(encoding="utf-8")
    assert tables.index("'epsilon_exec'") < tables.index("'eta_rep'")
    assert check_generated_integrity(stale) == ("ran", [])

    changed = first / "schema" / "error.json"
    changed.write_text(changed.read_text(encoding="utf-8") + " ", encoding="utf-8")
    manifest_path = first / "schema" / "MANIFEST.json"
    recorded = json.loads(manifest_path.read_text(encoding="utf-8"))
    recorded["error.json"] = hashlib.sha256(changed.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(recorded, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    status, violations = check_generated_integrity(first)
    assert status == "ran"
    assert any("tools/genschema.py" in violation for violation in violations)

    without_manifest = tmp_path / "without-manifest"
    shutil.copytree(second, without_manifest)
    (without_manifest / "schema" / "MANIFEST.json").unlink()
    status, violations = check_generated_integrity(without_manifest)
    assert status == "failed" and any("without MANIFEST.json" in violation for violation in violations)

    digest_only = tmp_path / "digest-only"
    emit(digest_only / "schema")
    status, violations = check_generated_integrity(digest_only)
    assert status == "failed" and any("without tools/genschema.py" in violation for violation in violations)
