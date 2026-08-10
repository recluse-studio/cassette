# test_s12_pager.py — F2 fixtures for Q30/Q33/Q40 plans and MLX operators; depends on errors.py, pager.py, schema/tables.py, schema/validator.py, tools/ledger.py.
"""S12 proves bounded mathematical data, exact generated dispatch, and MLX-only numerics."""

from __future__ import annotations

import ast
import copy
import importlib.metadata
import json
import math
import platform
import shutil
import subprocess
from pathlib import Path

import pytest

if platform.system() != "Darwin" or platform.machine() != "arm64":
    pytest.skip(
        "S12 requires arm64 macOS with MLX Metal; skip before importing the runtime",
        allow_module_level=True,
    )

import mlx.core as mx

import pager
from errors import CassetteError
from schema.tables import CERTIFICATE_DIMENSIONS, DISPATCH_ROWS
from schema.validator import validate
from tools.ledger import run as run_ledger

REPO = Path(__file__).resolve().parent.parent
RUNTIME_COMMIT = "365d6f29b47686a9f5401f6a9ec5825fee162d69"
DISPATCH_DIGEST = "sha256:fba00edac946e57c7f1195e4e840b2cfba7552ea9811848318fb56ba58090457"
CASE_IDS = [
    "mlx.matmul.f32.2x3_3x2",
    "mlx.matmul.f32.2x4_4x4",
    "mlx.add.f32.2x4",
    "mlx.silu.f32.2x4",
    "mlx.quantized_matmul.affine4.f32.1x32_2x32",
    "mlx.rms_norm.f32.2x4",
    "mlx.rope.traditional.f32.1x1x2x4",
    "mlx.rope.traditional.f32.1x1x2x4.offset1",
    "mlx.attention.f32.1x1x2x2",
    "mlx.attention.causal.f32.1x1x2x4",
    "mlx.conv1d.f32.1x4x1_1x2x1",
    "mlx.embedding.f32_u32.4x3_2",
    "mlx.embedding.f32_u32.4x4_2",
    "mlx.categorical.f32_u32.2x3_2",
    "mlx.autograd_sum.f32.2x3",
    "mlx.sgd.f32.3",
]
MODES = [
    "BYTE_IDENTICAL_LAYOUT",
    "EXACT_NATIVE_SPARSITY",
    "EXACT_QUANTIZED_LAYOUT",
    "NATIVE_PREDICTIVE_PREFETCH",
    "COMPILED_CERTIFIED",
]


def digest(digit: str) -> str:
    return f"blake3:{digit * 64}"


def resources() -> dict:
    return {
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


def dispatch_record() -> dict:
    return {
        "dispatch_version": "q30-v1",
        "runtime_name": "mlx",
        "runtime_version": "0.31.0",
        "runtime_commit": RUNTIME_COMMIT,
        "dispatch_digest": DISPATCH_DIGEST,
        "case_ids": list(CASE_IDS),
        "apple_features": ["apple_silicon", "metal"],
    }


def otool_dependencies(binary: Path) -> list[str]:
    """Return Mach-O load entries; the first otool heading is not a dependency."""
    lines = subprocess.run(
        ["otool", "-L", str(binary)], check=True, capture_output=True, text=True
    ).stdout.splitlines()
    assert lines and lines[0].rstrip().endswith(":"), "unexpected otool -L structure"
    return [line.strip().split(" (", 1)[0] for line in lines[1:] if line.strip()]


def otool_rpaths(binary: Path) -> list[str]:
    """Return LC_RPATH values used to resolve @rpath dependency entries."""
    lines = subprocess.run(
        ["otool", "-l", str(binary)], check=True, capture_output=True, text=True
    ).stdout.splitlines()
    paths = []
    for index, line in enumerate(lines):
        if line.strip() != "cmd LC_RPATH":
            continue
        for candidate in lines[index + 1 : index + 8]:
            value = candidate.strip()
            if value.startswith("path "):
                paths.append(value[5:].split(" (offset ", 1)[0])
                break
    return paths


def repository_owned_dependencies(binary: Path, repository: Path) -> list[str]:
    """Map actual Mach-O load entries to files owned by the supplied Git repository."""
    repository = repository.resolve()
    tracked = set(
        subprocess.run(
            ["git", "-C", str(repository), "ls-files", "-z"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.split("\0")
    )

    def anchored(value: str) -> Path | None:
        if value.startswith("@loader_path/") or value.startswith("@executable_path/"):
            return binary.parent / value.split("/", 1)[1]
        return Path(value) if value.startswith("/") else None

    candidates: list[Path] = []
    rpaths = [anchored(value) for value in otool_rpaths(binary)]
    for dependency in otool_dependencies(binary):
        if dependency.startswith("@rpath/"):
            suffix = dependency.split("/", 1)[1]
            candidates.extend(path / suffix for path in rpaths if path is not None)
            continue
        candidate = anchored(dependency)
        if candidate is not None:
            candidates.append(candidate)

    owned = []
    for candidate in candidates:
        try:
            relative = candidate.resolve().relative_to(repository).as_posix()
        except ValueError:
            continue
        if relative in tracked:
            owned.append(relative)
    return sorted(set(owned))


def certificate(target_digit: str = "1") -> dict:
    return {
        "certificate_version": "q19-v1",
        "certificate_id": digest("0"),
        "target": {
            "target_digest": digest(target_digit),
            "flattening_digest": digest("2"),
            "shape": [2, 2],
            "field": "REAL",
        },
        "condition_metrics": [
            {
                "condition_id": "condition.a",
                "provenance_digest": digest("3"),
                "metric_digest": digest("4"),
                "positive_definite_witness_digest": digest("5"),
            },
            {
                "condition_id": "condition.b",
                "provenance_digest": digest("6"),
                "metric_digest": digest("7"),
                "positive_definite_witness_digest": digest("8"),
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
                "witness_digest": digest("9"),
                "rank": 1,
                "service_face_id": "face.ab",
                "witness_losses": [
                    {"condition_id": "condition.a", "loss": 0.1},
                    {"condition_id": "condition.b", "loss": 0.125},
                ],
                "description": {
                    "class": "EXACT",
                    "reconstruction_digest": digest("a"),
                    "residual_relation_digest": digest("b"),
                    "distortion_bound": 0.01,
                    "estimator_digest": digest("c"),
                    "estimator_calibration_digest": digest("d"),
                    "sampling_law_id": "sampling.exact",
                },
            }
        ],
        "description_contract": {
            "description_family_digest": digest("a"),
            "distortion_metric_digest": digest("b"),
            "residual_family_digest": digest("c"),
            "estimator_family_digest": digest("d"),
        },
        "observation_contract": {
            "kind": "PROTECTED_TEST_LAW",
            "experiment_digest": digest("c"),
            "support_digest": digest("d"),
            "selector_digest": digest("e"),
            "loss_family_digest": digest("f"),
            "sample_count": 256,
            "confidence": 0.99,
            "off_support": "REJECT",
        },
        "execution_contract": {
            "sampling_laws": [
                {
                    "sampling_law_id": "sampling.exact",
                    "kind": "EXACT",
                    "law_digest": digest("b"),
                    "work_unit": "PAGES",
                    "seed_policy": "NONE",
                }
            ],
            "operations": [
                {
                    "operation_id": "operation.matmul",
                    "operator_case_id": CASE_IDS[0],
                    "rank_accounting_digest": digest("2"),
                    "loss_propagation_digest": digest("4"),
                    "remainder_bound": 0.0,
                    "epsilon_exec": 0.01,
                    "delta_exec": 0.001,
                    "sampling_law_id": "sampling.exact",
                }
            ],
            "risk_composition_kind": "UNION_BOUND",
            "risk_composition_digest": digest("5"),
        },
        "trace_contract": {
            "protected_trace_family_digest": digest("6"),
            "schedule_digest": digest("7"),
            "prefix_policy": "COHERENT_RESTRICTION",
            "horizon": 1,
        },
        "resources": resources(),
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
            "conversion_digest": digest("8"),
        },
    }


def plan(target_digit: str = "1") -> dict:
    return {
        "plan_version": "compiled-plan-v1",
        "plan_id": digest("9"),
        "selected_mode": "COMPILED_CERTIFIED",
        "prior_mode_failures": [
            {"ordinal": index + 1, "mode": mode, "q38_record_digest": digest(str(index + 1))}
            for index, mode in enumerate(MODES[:-1])
        ],
        "target_digest": digest(target_digit),
        "profile_digest": digest("2"),
        "certificate_id": digest("0"),
        "tensor_graph_digest": digest("3"),
        "page_map_digest": digest("4"),
        "layout_digest": digest("5"),
        "precision_planes_digest": digest("6"),
        "semantic_manifest_digest": digest("7"),
        "invalidation_graph_digest": digest("8"),
        "dispatch": dispatch_record(),
        "resource_limits": resources(),
        "artifact_refs": [digest(target_digit)],
        "weight_payload_bytes": 0,
    }


def walk_schema(node: object):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from walk_schema(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk_schema(value)


def flatten(value: object) -> list[float | int]:
    if isinstance(value, list):
        return [item for nested in value for item in flatten(nested)]
    assert isinstance(value, (int, float))
    return [value]


def assert_values(row: dict, observed: mx.array, expected: object) -> None:
    actual_values = flatten(observed.tolist())
    expected_values = flatten(expected)
    assert len(actual_values) == len(expected_values)
    for actual, reference in zip(actual_values, expected_values, strict=True):
        assert math.isclose(
            actual,
            reference,
            rel_tol=row["relative_tolerance"],
            abs_tol=row["absolute_tolerance"],
        )


def golden_cases() -> dict[str, tuple[list[mx.array], object]]:
    xq = mx.array([list(range(1, 33))], dtype=mx.float32)
    weights = mx.array(
        [list(range(32)), list(range(31, -1, -1))], dtype=mx.float32
    )
    packed, scales, biases = mx.quantize(weights, group_size=32, bits=4, mode="affine")
    quantized_reference = []
    for packed_row, scale_row, bias_row in zip(
        packed.tolist(), scales.tolist(), biases.tolist(), strict=True
    ):
        quantized = [
            (word >> shift) & 15 for word in packed_row for shift in range(0, 32, 4)
        ]
        dequantized = [value * scale_row[0] + bias_row[0] for value in quantized]
        quantized_reference.append(
            sum(left * right for left, right in zip(xq.tolist()[0], dequantized, strict=True))
        )

    norm_input = [[1.0, 2.0, 3.0, 4.0], [-1.0, -2.0, -3.0, -4.0]]
    norm_weight = [1.0, 0.5, 2.0, 1.5]
    norm_reference = []
    for row in norm_input:
        denominator = math.sqrt(sum(value * value for value in row) / len(row) + 1e-5)
        norm_reference.append(
            [value * weight / denominator for value, weight in zip(row, norm_weight, strict=True)]
        )

    rope_input = [[[[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]]]]

    def rope_reference(offset: int) -> list:
        reference = [[[[] for _ in range(2)]]]
        for position, row in enumerate(rope_input[0][0], start=offset):
            for left, right, frequency in (
                (row[0], row[1], 1.0),
                (row[2], row[3], 0.01),
            ):
                angle = position * frequency
                reference[0][0][position - offset].extend((
                    left * math.cos(angle) - right * math.sin(angle),
                    left * math.sin(angle) + right * math.cos(angle),
                ))
        return reference

    attention_scale = 2**-0.5
    attention_reference = []
    for scores in ([attention_scale, 0.0], [0.0, attention_scale]):
        weights_row = [math.exp(value) for value in scores]
        total = sum(weights_row)
        first, second = [value / total for value in weights_row]
        attention_reference.append([first + 3.0 * second, 2.0 * first + 4.0 * second])

    causal_weight = math.exp(0.5) / (1.0 + math.exp(0.5))
    causal_attention_reference = [[[[1.0, 2.0, 3.0, 4.0], [
        (1.0 - causal_weight) * 1.0 + causal_weight * 4.0,
        (1.0 - causal_weight) * 2.0 + causal_weight * 3.0,
        (1.0 - causal_weight) * 3.0 + causal_weight * 2.0,
        (1.0 - causal_weight) * 4.0 + causal_weight * 1.0,
    ]]]]
    silu_input = [[-1.0, -0.5, 0.0, 0.5], [1.0, 2.0, -2.0, 3.0]]
    silu_reference = [
        [value / (1.0 + math.exp(-value)) for value in row]
        for row in silu_input
    ]

    return {
        CASE_IDS[0]: (
            [
                mx.array([[1, 2, 3], [4, 5, 6]], dtype=mx.float32),
                mx.array([[1, 2], [3, 4], [5, 6]], dtype=mx.float32),
            ],
            [[22.0, 28.0], [49.0, 64.0]],
        ),
        CASE_IDS[1]: (
            [
                mx.array([[1, 2, 3, 4], [-1, 0.5, 2, -0.5]], dtype=mx.float32),
                mx.array([
                    [0.5, -0.25, 0.75, 0.0],
                    [0.25, 0.5, -0.5, 1.0],
                    [-0.75, 0.25, 0.5, -0.25],
                    [1.0, -0.5, 0.25, 0.5],
                ], dtype=mx.float32),
            ],
            [[2.75, -0.5, 2.25, 3.25], [-2.375, 1.25, -0.125, -0.25]],
        ),
        CASE_IDS[2]: (
            [
                mx.array([[1, 2, 3, 4], [-1, -2, -3, -4]], dtype=mx.float32),
                mx.array([[0.5, -0.5, 1.5, -1.5], [2, -2, 0.25, -0.25]], dtype=mx.float32),
            ],
            [[1.5, 1.5, 4.5, 2.5], [1.0, -4.0, -2.75, -4.25]],
        ),
        CASE_IDS[3]: ([mx.array(silu_input, dtype=mx.float32)], silu_reference),
        CASE_IDS[4]: ([xq, packed, scales, biases], [quantized_reference]),
        CASE_IDS[5]: (
            [mx.array(norm_input, dtype=mx.float32), mx.array(norm_weight, dtype=mx.float32)],
            norm_reference,
        ),
        CASE_IDS[6]: ([mx.array(rope_input, dtype=mx.float32)], rope_reference(0)),
        CASE_IDS[7]: ([mx.array(rope_input, dtype=mx.float32)], rope_reference(1)),
        CASE_IDS[8]: (
            [
                mx.array([[[[1, 0], [0, 1]]]], dtype=mx.float32),
                mx.array([[[[1, 0], [0, 1]]]], dtype=mx.float32),
                mx.array([[[[1, 2], [3, 4]]]], dtype=mx.float32),
            ],
            [[attention_reference]],
        ),
        CASE_IDS[9]: (
            [
                mx.array([[[[1, 0, 0, 0], [0, 1, 0, 0]]]], dtype=mx.float32),
                mx.array([[[[1, 0, 0, 0], [0, 1, 0, 0]]]], dtype=mx.float32),
                mx.array([[[[1, 2, 3, 4], [4, 3, 2, 1]]]], dtype=mx.float32),
            ],
            causal_attention_reference,
        ),
        CASE_IDS[10]: (
            [
                mx.array([[[1], [2], [3], [4]]], dtype=mx.float32),
                mx.array([[[2], [1]]], dtype=mx.float32),
            ],
            [[[4.0], [7.0], [10.0]]],
        ),
        CASE_IDS[11]: (
            [
                mx.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]], dtype=mx.float32),
                mx.array([3, 1], dtype=mx.uint32),
            ],
            [[10.0, 11.0, 12.0], [4.0, 5.0, 6.0]],
        ),
        CASE_IDS[12]: (
            [
                mx.array([
                    [1, 2, 3, 4],
                    [5, 6, 7, 8],
                    [9, 10, 11, 12],
                    [13, 14, 15, 16],
                ], dtype=mx.float32),
                mx.array([2, 0], dtype=mx.uint32),
            ],
            [[9.0, 10.0, 11.0, 12.0], [1.0, 2.0, 3.0, 4.0]],
        ),
        CASE_IDS[13]: (
            [
                mx.array([[0, 1, 2], [2, 1, 0]], dtype=mx.float32),
                mx.array([0, 17], dtype=mx.uint32),
            ],
            [1, 0],
        ),
        CASE_IDS[14]: (
            [mx.array([[1, 2, 3], [4, 5, 6]], dtype=mx.float32)],
            [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0]],
        ),
        CASE_IDS[15]: (
            [
                mx.array([1.0, 2.0, 3.0], dtype=mx.float32),
                mx.array([0.5, -0.5, 0.25], dtype=mx.float32),
            ],
            [0.875, 2.125, 2.9375],
        ),
    }


def test_q33_q40_f2_certificate_dimensions_are_bounded_data_and_fail_before_execution():
    """Q33/Q40 acceptance: F2 represents every separate MATHS field and rejects executable or collapsed data."""
    expected_dimensions = {
        "mathematics": [
            "target",
            "condition_metrics",
            "compatibility",
            "atoms",
            "description_contract",
            "observation_contract",
            "execution_contract",
            "trace_contract",
        ],
        "resources": [
            "eta_rep",
            "epsilon_exec",
            "delta_exec_total",
            "atom_count",
            "max_atom_rank",
            "description_bytes_peak",
            "description_bytes_total",
            "metadata_bytes_peak",
            "metadata_bytes_total",
            "fresh_samples_max",
            "fresh_samples_total",
            "fresh_traffic_max",
            "fresh_traffic_total",
            "fresh_traffic_unit",
            "horizon",
        ],
        "tables": ["per_atom", "per_operation", "per_trace_step"],
        "physical": ["conversion_rows", "conversion_digest"],
    }
    assert CERTIFICATE_DIMENSIONS == expected_dimensions
    for kind in ("execution_plan", "mathematical_certificate", "operator_dispatch"):
        schema = json.loads((REPO / "schema" / f"{kind}.json").read_text(encoding="utf-8"))
        for node in walk_schema(schema):
            if node.get("type") == "object":
                assert node.get("additionalProperties") is False
            if node.get("type") == "array":
                assert "maxItems" in node
            if node.get("type") == "string":
                assert "maxLength" in node

    for target_digit in ("1", "a"):
        pager.validate_plan(plan(target_digit), certificate(target_digit))

    malformed = []
    for field in expected_dimensions["mathematics"]:
        candidate = certificate()
        del candidate[field]
        malformed.append((plan(), candidate))
    collapsed = certificate()
    collapsed["resources"] = {"quality_error": 0.1}
    malformed.append((plan(), collapsed))
    for forbidden in ("code", "command", "model_family", "path", "url", "weight_payload"):
        candidate_plan = plan()
        candidate_plan[forbidden] = "forbidden"
        malformed.append((candidate_plan, certificate()))
    excessive = plan()
    excessive["prior_mode_failures"].append(copy.deepcopy(excessive["prior_mode_failures"][-1]))
    assert any("permits at most 4" in defect for defect in validate("execution_plan", excessive))
    malformed.append((excessive, certificate()))
    infinite = certificate()
    infinite["resources"]["epsilon_exec"] = math.inf
    assert any("number must be finite" in defect for defect in validate("mathematical_certificate", infinite))
    malformed.append((plan(), infinite))

    mx.metal.reset_peak_memory()
    peak_before_validation = mx.metal.get_peak_memory()
    for candidate_plan, candidate_certificate in malformed:
        with pytest.raises(CassetteError) as caught:
            pager.validate_plan(candidate_plan, candidate_certificate)
        assert caught.value.code == "INVALID_REQUEST"
    assert mx.metal.get_peak_memory() == peak_before_validation

    wrong_order = plan()
    wrong_order["prior_mode_failures"].reverse()
    with pytest.raises(CassetteError, match="Q40: least-invasive mode order"):
        pager.validate_plan(wrong_order, certificate())
    wrong_dispatch = plan()
    wrong_dispatch["dispatch"]["case_ids"] = [CASE_IDS[0]]
    with pytest.raises(CassetteError, match="Q30: generated dispatch identity"):
        pager.validate_plan(wrong_dispatch, certificate())
    foreign_operator = certificate()
    foreign_operator["execution_contract"]["operations"][0]["operator_case_id"] = (
        "mlx.custom.kernel"
    )
    with pytest.raises(CassetteError) as unsupported:
        pager.validate_plan(plan(), foreign_operator)
    assert unsupported.value.code == "UNSUPPORTED_OPERATOR"
    assert unsupported.value.object_id == "mlx.custom.kernel"
    with pytest.raises(CassetteError, match="Q19: immutable target identity"):
        pager.validate_plan(plan("1"), certificate("a"))

    pager_tree = ast.parse((REPO / "pager.py").read_text(encoding="utf-8"))
    forbidden_names = {"kimi", "k3", "llama", "ollama", "qwen", "tinker", "huggingface"}
    assert not any(
        isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and any(name in node.value.lower() for name in forbidden_names)
        for node in ast.walk(pager_tree)
    )


def test_q30_f2_every_generated_operator_dtype_and_shape_matches_an_independent_golden_reference(
    tmp_path,
):
    """Q30 acceptance: F2 executes every generated MLX tuple against literal or scalar reference arithmetic."""
    assert importlib.metadata.version("mlx") == "0.31.0"
    rows = {row["case_id"]: row for row in DISPATCH_ROWS}
    cases = golden_cases()
    assert list(rows) == CASE_IDS
    assert set(cases) == set(rows)
    assert {row["operator"] for row in rows.values()} == {
        "activation",
        "add",
        "attention",
        "autograd",
        "convolution",
        "embedding",
        "matmul",
        "norm",
        "optimizer",
        "quantized_matmul",
        "rope",
        "sampling",
    }
    for case_id, row in rows.items():
        inputs, reference = cases[case_id]
        assert_values(row, pager.dispatch(case_id, inputs), reference)

    wrong_shape = [mx.array([[1.0]], dtype=mx.float32), mx.array([[2.0]], dtype=mx.float32)]
    with pytest.raises(CassetteError, match="Q30: generated dtype and shape tuple"):
        pager.dispatch(CASE_IDS[0], wrong_shape)
    with pytest.raises(CassetteError) as absent:
        pager.dispatch("mlx.custom.kernel", [])
    assert absent.value.code == "UNSUPPORTED_OPERATOR"

    native_sources = {".c", ".cc", ".cpp", ".m", ".metal", ".mm", ".swift"}
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=REPO, check=True, capture_output=True, text=True
    ).stdout.splitlines()
    assert not [path for path in tracked if Path(path).suffix in native_sources]
    assert repository_owned_dependencies(Path(mx.__file__), REPO) == []

    native_repo = tmp_path / "native-repository"
    native_repo.mkdir()
    subprocess.run(["git", "-C", str(native_repo), "init", "--quiet"], check=True)
    consumer = native_repo / "consumer.so"
    owned_library = native_repo / "libcassette.dylib"
    shutil.copy2(mx.__file__, consumer)
    shutil.copy2(mx.__file__, owned_library)
    original_dependency = otool_dependencies(consumer)[0]
    subprocess.run(
        [
            "install_name_tool",
            "-change",
            original_dependency,
            str(owned_library.resolve()),
            str(consumer),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "-C", str(native_repo), "add", "consumer.so", "libcassette.dylib"],
        check=True,
    )
    assert repository_owned_dependencies(consumer, native_repo) == ["libcassette.dylib"]
    pager_tree = ast.parse((REPO / "pager.py").read_text(encoding="utf-8"))
    executor_names = {
        pager._EXECUTORS[row["operator"]].__name__ for row in rows.values()
    }
    executor_functions = [
        node
        for node in pager_tree.body
        if isinstance(node, ast.FunctionDef) and node.name in executor_names
    ]
    assert {node.name for node in executor_functions} == executor_names
    authored_arithmetic = (ast.BinOp, ast.BoolOp, ast.Compare, ast.UnaryOp)
    assert not [
        node
        for function in executor_functions
        for node in ast.walk(function)
        if isinstance(node, authored_arithmetic)
    ]


def test_q30_ledger_confines_mlx_to_pager_and_trainer(tmp_path):
    """Q30 acceptance: the ledger accepts pager.py and rejects an MLX import in another product authority."""
    current = run_ledger(REPO)
    assert not [violation for violation in current["violations"] if "mlx import outside" in violation]

    (tmp_path / "research").mkdir()
    (tmp_path / "research" / "RESEARCH.md").write_text("question_id: Q30\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "fixture"\nrequires-python = "==3.13.*"\n'
        'dependencies = ["mlx==0.31.0"]\n',
        encoding="utf-8",
    )
    (tmp_path / "compiler.py").write_text(
        "# compiler.py — hostile confinement fixture; depends on (none).\nimport mlx.core\n",
        encoding="utf-8",
    )
    report = run_ledger(tmp_path)
    assert any("compiler.py: mlx import outside" in violation for violation in report["violations"])
