# test_s15_pager.py — F3 certified causal-decoder execution, nonlinear risk, trace, and KV rollback (Q19/Q36/Q63); depends on errors.py, pager.py, schema/tables.py, store.py, tests/test_s05_store.py, tests/test_s14_pager.py.
"""S15 proves one exact and one fresh-residual tiny decoder from cartridge pages."""

from __future__ import annotations

import asyncio
import copy
from fractions import Fraction
import math
from pathlib import Path
import platform
import struct

import pytest

import pager
from errors import CassetteError
from schema.tables import OPERATOR_DISPATCH, Q40_MODES
from store import canonical_bytes, digest_bytes, import_safetensors, load_root, page_locations
from tests.test_s05_store import _identity, _write_safetensors
from tests.test_s14_pager import _corrupt_pages, _restore_pages


pytestmark = pytest.mark.skipif(
    platform.system() != "Darwin" or platform.machine() != "arm64",
    reason="S15 requires arm64 macOS with the pinned MLX Metal decoder runtime",
)

GIB = 1024**3
MATMUL_CASE = "mlx.matmul.f32.2x4_4x4"
ADD_CASE = "mlx.add.f32.2x4"
SILU_CASE = "mlx.silu.f32.2x4"
NORM_CASE = "mlx.rms_norm.f32.2x4"
ROPE_CASES = (
    "mlx.rope.traditional.f32.1x1x2x4",
    "mlx.rope.traditional.f32.1x1x2x4.offset1",
)
ATTENTION_CASE = "mlx.attention.causal.f32.1x1x2x4"
EMBEDDING_CASE = "mlx.embedding.f32_u32.4x4_2"
PARAMETER_ROLES = (
    "embedding",
    "norm_attention",
    "query",
    "key",
    "value",
    "attention_output",
    "norm_ffn",
    "ffn_up_base",
    "ffn_down",
    "norm_final",
    "unembedding",
)
EMBEDDING = (
    (0.3, -0.2, 0.1, 0.5),
    (-0.4, 0.6, 0.2, -0.1),
    (0.7, 0.1, -0.3, 0.2),
    (-0.2, -0.5, 0.8, 0.4),
)
NORM_ATTENTION = (1.0, 0.9, 1.1, 0.8)
NORM_FFN = (0.95, 1.05, 0.85, 1.15)
NORM_FINAL = (1.1, 0.8, 1.0, 0.9)
QUERY = (
    (0.5, -0.1, 0.2, 0.0),
    (0.1, 0.4, -0.2, 0.3),
    (-0.3, 0.2, 0.6, -0.1),
    (0.2, 0.0, 0.1, 0.5),
)
KEY = (
    (0.4, 0.2, -0.1, 0.3),
    (-0.2, 0.5, 0.3, 0.0),
    (0.1, -0.3, 0.4, 0.2),
    (0.3, 0.1, -0.2, 0.6),
)
VALUE = (
    (0.6, -0.2, 0.1, 0.2),
    (0.1, 0.5, -0.3, 0.1),
    (-0.2, 0.2, 0.7, -0.1),
    (0.3, 0.0, 0.2, 0.4),
)
ATTENTION_OUTPUT = (
    (0.5, 0.1, -0.2, 0.2),
    (-0.1, 0.6, 0.2, 0.0),
    (0.2, -0.2, 0.5, 0.1),
    (0.0, 0.3, -0.1, 0.4),
)
FFN_DOWN = (
    (0.4, -0.1, 0.2, 0.1),
    (0.2, 0.5, -0.2, 0.0),
    (-0.1, 0.3, 0.4, 0.2),
    (0.1, -0.2, 0.1, 0.6),
)
UNEMBEDDING = (
    (0.7, -0.2, 0.1, 0.3),
    (-0.1, 0.6, 0.2, -0.2),
    (0.2, 0.1, 0.5, 0.4),
    (-0.3, 0.2, -0.1, 0.8),
)
TARGET = (
    (Fraction(1, 4), Fraction(1, 4), Fraction(1, 4), Fraction(1, 16)),
    (Fraction(1, 4), Fraction(-1, 4), Fraction(1, 4), Fraction(-1, 16)),
    (Fraction(1, 4), Fraction(1, 4), Fraction(-1, 4), Fraction(-1, 16)),
    (Fraction(1, 4), Fraction(-1, 4), Fraction(-1, 4), Fraction(1, 16)),
)
ZERO = tuple(tuple(Fraction(0) for _ in range(4)) for _ in range(4))
PROBABILITIES = {
    0: Fraction(16, 49),
    1: Fraction(16, 49),
    2: Fraction(16, 49),
    3: Fraction(1, 49),
}
PREFILL_TOKENS = (0, 1)
DECODE_TOKENS = (1, 2)


def _digest(value: object) -> str:
    return digest_bytes(canonical_bytes(value))


def _seal(document: dict, identity_field: str) -> None:
    document[identity_field] = _digest(
        {name: value for name, value in document.items() if name != identity_field}
    )


def _normal_scalar(value: object) -> list[str]:
    return [str(Fraction(value)), "0"]


def _normal_matrix(matrix) -> list[list[list[str]]]:
    return [[_normal_scalar(value) for value in row] for row in matrix]


def _flat(values):
    if isinstance(values, (list, tuple)):
        return tuple(scalar for value in values for scalar in _flat(value))
    return (values,)


def _payload(values) -> bytes:
    flattened = _flat(values)
    return struct.pack(f"<{len(flattened)}f", *(float(value) for value in flattened))


def _shape(values) -> tuple[int, ...]:
    if not isinstance(values[0], (list, tuple)):
        return (len(values),)
    return (len(values), len(values[0]))


def _transpose(matrix):
    return tuple(tuple(row[column] for row in matrix) for column in range(len(matrix[0])))


def _correction(unit: int):
    matrix = [[Fraction(0) for _ in range(4)] for _ in range(4)]
    for row in range(4):
        matrix[row][unit] = TARGET[row][unit] / PROBABILITIES[unit]
    return tuple(tuple(row) for row in matrix)


def _operator_cases(step: int) -> tuple[str, ...]:
    rope = ROPE_CASES[step]
    return (
        EMBEDDING_CASE,
        NORM_CASE,
        MATMUL_CASE,
        MATMUL_CASE,
        MATMUL_CASE,
        rope,
        rope,
        ATTENTION_CASE,
        MATMUL_CASE,
        ADD_CASE,
        NORM_CASE,
        MATMUL_CASE,
        MATMUL_CASE,
        ADD_CASE,
        SILU_CASE,
        MATMUL_CASE,
        ADD_CASE,
        NORM_CASE,
        MATMUL_CASE,
    )


def _metadata(
    atom_id: str,
    operation_id: str,
    kind: str,
    law_id: str,
    units: tuple[tuple[int, str], ...],
) -> bytes:
    return canonical_bytes({
        "atom_id": atom_id,
        "operation_id": operation_id,
        "sampling_kind": kind,
        "sampling_law_id": law_id,
        "sample_units": [
            {"probability": probability, "unit": unit}
            for unit, probability in units
        ],
    })


def _fixture(
    root_digest: str,
    pages: dict[str, str],
    *,
    runtime_buffer_bytes: int = 0,
) -> tuple[dict, dict, dict, dict, dict]:
    condition_ids = ("condition.exact", "condition.fresh")
    face_id = "face.all"
    cover = [
        {"condition_id": "condition.exact", "atom_id": "atom.exact"},
        {"condition_id": "condition.fresh", "atom_id": "atom.fresh"},
    ]
    exact_law_id = "sampling.exact"
    fresh_law_id = "sampling.fresh-columns"
    exact_operation = "operation.ffn-up.exact"
    fresh_operation = "operation.ffn-up.fresh"
    fresh_units = tuple(
        (unit, str(probability))
        for unit, probability in PROBABILITIES.items()
    )
    exact_metadata = _metadata(
        "atom.exact", exact_operation, "EXACT", exact_law_id, ()
    )
    fresh_metadata = _metadata(
        "atom.fresh",
        fresh_operation,
        "FRESH_RANDOM",
        fresh_law_id,
        fresh_units,
    )
    target_values = [str(value) for row in TARGET for value in row]
    target_evidence = {
        "field": "REAL",
        "source_shape": [4, 4],
        "source_values": target_values,
        "shape": [4, 4],
        "flattening_order": list(range(16)),
    }
    target_record = {
        "field": "REAL",
        "shape": [4, 4],
        "values": _normal_matrix(TARGET),
    }
    flattening_record = {
        "source_shape": [4, 4],
        "target_shape": [4, 4],
        "order": list(range(16)),
    }
    identity_metric = [
        ["1" if row == column else "0" for column in range(16)]
        for row in range(16)
    ]
    positive_minors = [_normal_scalar(1) for _ in range(16)]
    conditions = [
        {
            "condition_id": condition_id,
            "metric": copy.deepcopy(identity_metric),
            "provenance": {"fixture": "S15", "condition_id": condition_id},
        }
        for condition_id in condition_ids
    ]
    condition_claims = [
        {
            "condition_id": row["condition_id"],
            "provenance_digest": _digest(row["provenance"]),
            "metric_digest": _digest(_normal_matrix(tuple(
                tuple(int(value) for value in metric_row)
                for metric_row in row["metric"]
            ))),
            "positive_definite_witness_digest": _digest(positive_minors),
        }
        for row in conditions
    ]
    exact_description_bytes = 624
    fresh_description_bytes = 560
    estimator_none = {"kind": "NONE"}
    estimator_fresh = {"kind": "FRESH_RESIDUAL_COLUMN_AVERAGE"}
    atom_norm = Fraction(49, 64)
    atom_evidence = [
        {
            "atom_id": "atom.exact",
            "matrix": [[str(value) for value in row] for row in TARGET],
            "service_face_id": face_id,
            "description": {
                "class": "EXACT",
                "description_bytes": exact_description_bytes,
                "metadata_bytes": len(exact_metadata),
                "reconstruction": [[str(value) for value in row] for row in TARGET],
                "estimator": estimator_none,
                "estimator_calibration": {
                    "distortion": "0",
                    "atom_norm_squared": str(atom_norm),
                },
                "sampling_law_id": exact_law_id,
            },
        },
        {
            "atom_id": "atom.fresh",
            "matrix": [[str(value) for value in row] for row in TARGET],
            "service_face_id": face_id,
            "description": {
                "class": "BLOCK",
                "description_bytes": fresh_description_bytes,
                "metadata_bytes": len(fresh_metadata),
                "reconstruction": [[str(value) for value in row] for row in ZERO],
                "estimator": estimator_fresh,
                "estimator_calibration": {
                    "distortion": str(atom_norm),
                    "atom_norm_squared": str(atom_norm),
                },
                "sampling_law_id": fresh_law_id,
            },
        },
    ]
    atom_claims = []
    for row in atom_evidence:
        reconstruction = tuple(
            tuple(Fraction(value) for value in item)
            for item in row["description"]["reconstruction"]
        )
        residual = tuple(
            tuple(
                value - rebuilt
                for value, rebuilt in zip(target_row, rebuilt_row, strict=True)
            )
            for target_row, rebuilt_row in zip(TARGET, reconstruction, strict=True)
        )
        atom_claims.append({
            "atom_id": row["atom_id"],
            "witness_digest": _digest(_normal_matrix(TARGET)),
            "rank": 4,
            "service_face_id": face_id,
            "witness_losses": [
                {"condition_id": condition_id, "loss": 0.0}
                for condition_id in condition_ids
            ],
            "description": {
                "class": row["description"]["class"],
                "reconstruction_digest": _digest(_normal_matrix(reconstruction)),
                "residual_relation_digest": _digest(_normal_matrix(residual)),
                "distortion_bound": float(Fraction(
                    row["description"]["estimator_calibration"]["distortion"]
                )),
                "estimator_digest": _digest(row["description"]["estimator"]),
                "estimator_calibration_digest": _digest(
                    row["description"]["estimator_calibration"]
                ),
                "sampling_law_id": row["description"]["sampling_law_id"],
            },
        })
    exact_law = {
        "sampling_law_id": exact_law_id,
        "kind": "EXACT",
        "law": {"family": "NO_RESIDUAL", "atom_ids": ["atom.exact"]},
        "work_unit": "COLUMNS",
        "seed_policy": "NONE",
    }
    fresh_law = {
        "sampling_law_id": fresh_law_id,
        "kind": "FRESH_RANDOM",
        "law": {
            "family": "FROBENIUS_RESIDUAL_COLUMNS",
            "adversary": "FIXED_QUERY_BEFORE_PRIVATE_COINS",
            "coins": "FRESH_INDEPENDENT",
            "atom_distributions": [{
                "atom_id": "atom.fresh",
                "columns": [
                    {"column": unit, "probability": str(probability)}
                    for unit, probability in PROBABILITIES.items()
                ],
            }],
        },
        "work_unit": "COLUMNS",
        "seed_policy": "RECORDED_COUNTER_KEY",
    }
    exact_loss = {"coefficient": "1", "remainder_bound": "0"}
    fresh_loss = {"coefficient": "7/40", "remainder_bound": "0"}
    rank_accounting = {"kind": "ATOM_BOUND", "maximum_rank": 4}
    operations = [
        {
            "operation_id": exact_operation,
            "operator_case_id": MATMUL_CASE,
            "rank_accounting": rank_accounting,
            "loss_propagation": exact_loss,
            "sampling_law_id": exact_law_id,
        },
        {
            "operation_id": fresh_operation,
            "operator_case_id": MATMUL_CASE,
            "rank_accounting": rank_accounting,
            "loss_propagation": fresh_loss,
            "sampling_law_id": fresh_law_id,
        },
    ]
    operation_claims = [
        {
            "operation_id": exact_operation,
            "operator_case_id": MATMUL_CASE,
            "rank_accounting_digest": _digest(rank_accounting),
            "loss_propagation_digest": _digest(exact_loss),
            "remainder_bound": 0.0,
            "epsilon_exec": 0.0,
            "delta_exec": 0.0,
            "sampling_law_id": exact_law_id,
        },
        {
            "operation_id": fresh_operation,
            "operator_case_id": MATMUL_CASE,
            "rank_accounting_digest": _digest(rank_accounting),
            "loss_propagation_digest": _digest(fresh_loss),
            "remainder_bound": 0.0,
            "epsilon_exec": 1.5,
            "delta_exec": 0.5,
            "sampling_law_id": fresh_law_id,
        },
    ]
    risk = {"kind": "UNION_BOUND", "proof": {"rule": "Boole"}}
    trace_steps = [
        {
            "step": 0,
            "operation_id": exact_operation,
            "atom_id": "atom.exact",
            "fresh_samples": 0,
            "fresh_traffic": 0,
        },
        {
            "step": 1,
            "operation_id": fresh_operation,
            "atom_id": "atom.fresh",
            "fresh_samples": 1,
            "fresh_traffic": 4,
        },
    ]
    trace_rows = [
        {
            **trace_steps[0],
            "description_bytes_resident": exact_description_bytes,
            "metadata_bytes_resident": len(exact_metadata),
            "epsilon_exec": 0.0,
            "delta_exec": 0.0,
        },
        {
            **trace_steps[1],
            "description_bytes_resident": fresh_description_bytes,
            "metadata_bytes_resident": len(fresh_metadata),
            "epsilon_exec": 1.5,
            "delta_exec": 0.5,
        },
    ]
    schedule_rows = [
        {
            **{
                name: value
                for name, value in row.items()
                if name not in {"epsilon_exec", "delta_exec"}
            },
            "epsilon_exec": "0" if row["step"] == 0 else "3/2",
            "delta_exec": "0" if row["step"] == 0 else "1/2",
        }
        for row in trace_rows
    ]
    physical_rows = [
        {
            "operation_id": exact_operation,
            "probe_unit": "COLUMNS",
            "probes": 0,
            "page_reads": 12,
            "bytes": 624,
            "memory_bytes_peak": 1248 + len(exact_metadata),
            "latency_ns_peak": 1000,
        },
        {
            "operation_id": fresh_operation,
            "probe_unit": "COLUMNS",
            "probes": 1,
            "page_reads": 12,
            "bytes": 624,
            "memory_bytes_peak": 1248 + len(fresh_metadata),
            "latency_ns_peak": 1000,
        },
    ]
    metadata_peak = max(len(exact_metadata), len(fresh_metadata))
    resources = {
        "eta_rep": 0.0,
        "epsilon_exec": 0.2625,
        "delta_exec_total": 0.5,
        "atom_count": 2,
        "max_atom_rank": 4,
        "description_bytes_peak": exact_description_bytes,
        "description_bytes_total": exact_description_bytes + fresh_description_bytes,
        "metadata_bytes_peak": metadata_peak,
        "metadata_bytes_total": len(exact_metadata) + len(fresh_metadata),
        "fresh_samples_max": 1,
        "fresh_samples_total": 1,
        "fresh_traffic_max": 4,
        "fresh_traffic_total": 4,
        "fresh_traffic_unit": "SCALARS",
        "horizon": 2,
    }
    description_contract = {
        "description_family": {"kind": "DECLARED_RECONSTRUCTION"},
        "distortion_metric": {"kind": "FROBENIUS_SQUARED"},
        "estimator_family": {"kind": "RESIDUAL_COLUMN_OR_EXACT"},
        "residual_family": {"relation": "ATOM_MINUS_RECONSTRUCTION"},
    }
    observation = {
        "kind": "PROTECTED_TEST_LAW",
        "experiment": {"name": "S15 exact and fresh nonlinear decoder"},
        "support": list(condition_ids),
        "selector": copy.deepcopy(cover),
        "loss_family": {"kind": "decoder-logit-l2"},
        "sample_count": 4,
        "confidence": 1.0,
        "off_support": "REJECT",
    }
    graph_steps = []
    for step, base_page in enumerate((pages["exact.base"], pages["fresh.base"])):
        role_pages = {
            "embedding": pages["embedding"],
            "norm_attention": pages["norm_attention"],
            "query": pages["query"],
            "key": pages["key"],
            "value": pages["value"],
            "attention_output": pages["attention_output"],
            "norm_ffn": pages["norm_ffn"],
            "ffn_up_base": base_page,
            "ffn_down": pages["ffn_down"],
            "norm_final": pages["norm_final"],
            "unembedding": pages["unembedding"],
        }
        graph_steps.append({
            "step": step,
            "position_offset": step,
            "operator_cases": list(_operator_cases(step)),
            "parameters": [
                {"role": role, "page_digest": role_pages[role]}
                for role in PARAMETER_ROLES
            ],
        })
    protected_graph = {
        "name": "S15 two-step tiny decoder",
        "architecture": "PRENORM_CAUSAL_DECODER",
        "hidden_size": 4,
        "vocabulary_size": 4,
        "token_count": 2,
        "horizon": 2,
        "steps": graph_steps,
    }
    trace = {
        "protected_trace_family": protected_graph,
        "prefix_policy": "COHERENT_RESTRICTION",
        "fresh_traffic_unit": "SCALARS",
        "steps": copy.deepcopy(trace_steps),
    }
    certificate = {
        "certificate_version": "q19-v1",
        "certificate_id": _digest("unsealed-certificate"),
        "target": {
            "target_digest": _digest(target_record),
            "flattening_digest": _digest(flattening_record),
            "shape": [4, 4],
            "field": "REAL",
        },
        "condition_metrics": condition_claims,
        "compatibility": {
            "eta_rep": 0.0,
            "rank_budget": 4,
            "service_faces": [
                {"face_id": face_id, "condition_ids": list(condition_ids)}
            ],
            "minimal_nonfaces": [],
            "cover": copy.deepcopy(cover),
            "excluded_conditions": [],
        },
        "atoms": atom_claims,
        "description_contract": {
            "description_family_digest": _digest(
                description_contract["description_family"]
            ),
            "distortion_metric_digest": _digest(
                description_contract["distortion_metric"]
            ),
            "residual_family_digest": _digest(
                description_contract["residual_family"]
            ),
            "estimator_family_digest": _digest(
                description_contract["estimator_family"]
            ),
        },
        "observation_contract": {
            "kind": observation["kind"],
            "experiment_digest": _digest(observation["experiment"]),
            "support_digest": _digest(observation["support"]),
            "selector_digest": _digest(observation["selector"]),
            "loss_family_digest": _digest(observation["loss_family"]),
            "sample_count": observation["sample_count"],
            "confidence": observation["confidence"],
            "off_support": observation["off_support"],
        },
        "execution_contract": {
            "sampling_laws": [
                {
                    "sampling_law_id": law["sampling_law_id"],
                    "kind": law["kind"],
                    "law_digest": _digest(law["law"]),
                    "work_unit": law["work_unit"],
                    "seed_policy": law["seed_policy"],
                }
                for law in (exact_law, fresh_law)
            ],
            "operations": operation_claims,
            "risk_composition_kind": risk["kind"],
            "risk_composition_digest": _digest(risk),
        },
        "trace_contract": {
            "protected_trace_family_digest": _digest(protected_graph),
            "schedule_digest": _digest({
                "prefix_policy": trace["prefix_policy"],
                "steps": schedule_rows,
            }),
            "prefix_policy": trace["prefix_policy"],
            "horizon": 2,
        },
        "resources": resources,
        "resource_tables": {
            "per_atom": [
                {
                    "atom_id": "atom.exact",
                    "description_bytes": exact_description_bytes,
                    "metadata_bytes": len(exact_metadata),
                    "fresh_samples_max": 0,
                    "fresh_samples_total": 0,
                    "fresh_traffic_max": 0,
                    "fresh_traffic_total": 0,
                    "epsilon_exec": 0.0,
                    "delta_exec": 0.0,
                },
                {
                    "atom_id": "atom.fresh",
                    "description_bytes": fresh_description_bytes,
                    "metadata_bytes": len(fresh_metadata),
                    "fresh_samples_max": 1,
                    "fresh_samples_total": 1,
                    "fresh_traffic_max": 4,
                    "fresh_traffic_total": 4,
                    "epsilon_exec": 1.5,
                    "delta_exec": 0.5,
                },
            ],
            "per_operation": [
                {
                    "operation_id": exact_operation,
                    "description_bytes_peak": exact_description_bytes,
                    "description_bytes_total": exact_description_bytes,
                    "metadata_bytes_peak": len(exact_metadata),
                    "metadata_bytes_total": len(exact_metadata),
                    "fresh_samples_max": 0,
                    "fresh_samples_total": 0,
                    "fresh_traffic_max": 0,
                    "fresh_traffic_total": 0,
                    "epsilon_exec": 0.0,
                    "delta_exec": 0.0,
                },
                {
                    "operation_id": fresh_operation,
                    "description_bytes_peak": fresh_description_bytes,
                    "description_bytes_total": fresh_description_bytes,
                    "metadata_bytes_peak": len(fresh_metadata),
                    "metadata_bytes_total": len(fresh_metadata),
                    "fresh_samples_max": 1,
                    "fresh_samples_total": 1,
                    "fresh_traffic_max": 4,
                    "fresh_traffic_total": 4,
                    "epsilon_exec": 1.5,
                    "delta_exec": 0.5,
                },
            ],
            "per_trace_step": trace_rows,
        },
        "physical_conversion": {
            "conversion_rows": copy.deepcopy(physical_rows),
            "conversion_digest": _digest(physical_rows),
        },
    }
    _seal(certificate, "certificate_id")
    evidence = {
        "target": target_evidence,
        "conditions": conditions,
        "atoms": atom_evidence,
        "description_contract": description_contract,
        "observation_contract": observation,
        "execution_contract": {
            "sampling_laws": [exact_law, fresh_law],
            "operations": operations,
            "risk_composition": risk,
        },
        "trace_contract": trace,
        "physical_conversion": {"conversion_rows": copy.deepcopy(physical_rows)},
        "minimal_nonface_proofs": [],
        "excluded_conditions": [],
    }
    profile = {
        "activation_bytes": 680,
        "cache_bytes": 0,
        "context_bytes": 64,
        "execution_bytes": GIB,
        "other_observed_bytes": GIB,
        "physical_bytes": 16 * GIB,
        "recommended_max_working_set_bytes": 16 * GIB,
        "runtime_buffer_bytes": runtime_buffer_bytes,
        "training_window_bytes": 0,
    }
    plan = {
        "plan_version": "compiled-plan-v1",
        "plan_id": _digest("unsealed-plan"),
        "selected_mode": "COMPILED_CERTIFIED",
        "prior_mode_failures": [
            {
                "ordinal": index + 1,
                "mode": mode,
                "q38_record_digest": _digest({"failed_mode": mode}),
            }
            for index, mode in enumerate(Q40_MODES[:-1])
        ],
        "target_digest": certificate["target"]["target_digest"],
        "profile_digest": _digest(profile),
        "certificate_id": certificate["certificate_id"],
        "tensor_graph_digest": _digest(protected_graph),
        "page_map_digest": _digest("unsealed page map"),
        "layout_digest": _digest("S15 layout"),
        "precision_planes_digest": _digest("S15 float32"),
        "semantic_manifest_digest": _digest("S15 semantics"),
        "invalidation_graph_digest": _digest("S15 invalidation"),
        "dispatch": copy.deepcopy(OPERATOR_DISPATCH),
        "resource_limits": copy.deepcopy(resources),
        "artifact_refs": [certificate["target"]["target_digest"]],
        "weight_payload_bytes": 0,
    }
    common_pages = [
        pages["embedding"],
        pages["norm_attention"],
        pages["query"],
        pages["key"],
        pages["value"],
        pages["attention_output"],
        pages["norm_ffn"],
    ]
    tail_pages = [
        pages["ffn_down"],
        pages["norm_final"],
        pages["unembedding"],
    ]
    page_map = {
        "root_digest": root_digest,
        "steps": [
            {
                "step": 0,
                "operation_id": exact_operation,
                "atom_id": "atom.exact",
                "description_digest": _digest(atom_claims[0]["description"]),
                "exact_pages": [
                    *common_pages,
                    pages["exact.base"],
                    *tail_pages,
                    pages["exact.correction"],
                ],
                "sample_units": [],
            },
            {
                "step": 1,
                "operation_id": fresh_operation,
                "atom_id": "atom.fresh",
                "description_digest": _digest(atom_claims[1]["description"]),
                "exact_pages": [
                    *common_pages,
                    pages["fresh.base"],
                    *tail_pages,
                ],
                "sample_units": [
                    {
                        "unit": unit,
                        "page_digests": [pages[f"fresh.unit{unit}"]],
                    }
                    for unit in PROBABILITIES
                ],
            },
        ],
    }
    plan["page_map_digest"] = _digest(page_map)
    _seal(plan, "plan_id")
    return plan, certificate, evidence, profile, page_map


def _rebind(
    plan: dict,
    certificate: dict,
    evidence: dict,
    profile: dict,
    page_map: dict,
) -> None:
    certificate["trace_contract"]["protected_trace_family_digest"] = _digest(
        evidence["trace_contract"]["protected_trace_family"]
    )
    certificate["physical_conversion"]["conversion_digest"] = _digest(
        certificate["physical_conversion"]["conversion_rows"]
    )
    _seal(certificate, "certificate_id")
    plan["certificate_id"] = certificate["certificate_id"]
    plan["target_digest"] = certificate["target"]["target_digest"]
    plan["profile_digest"] = _digest(profile)
    plan["page_map_digest"] = _digest(page_map)
    plan["tensor_graph_digest"] = _digest(
        evidence["trace_contract"]["protected_trace_family"]
    )
    plan["resource_limits"] = copy.deepcopy(certificate["resources"])
    _seal(plan, "plan_id")


def _selection(
    certificate: dict,
    evidence: dict,
    step: int,
    seed: int = 7,
) -> pager.CompiledSelection:
    trace = evidence["trace_contract"]["steps"][step]
    atom_id = trace["atom_id"]
    condition = next(
        row["condition_id"]
        for row in certificate["compatibility"]["cover"]
        if row["atom_id"] == atom_id
    )
    atom = next(row for row in certificate["atoms"] if row["atom_id"] == atom_id)
    face = certificate["compatibility"]["service_faces"][0]
    conversion = next(
        row
        for row in certificate["physical_conversion"]["conversion_rows"]
        if row["operation_id"] == trace["operation_id"]
    )
    return pager.CompiledSelection(
        observed_condition=condition,
        atom_id=atom_id,
        service_face=tuple(face["condition_ids"]),
        certificate_digest=certificate["certificate_id"],
        description_digest=_digest(atom["description"]),
        execution_seed_or_exact_schedule=(
            certificate["trace_contract"]["schedule_digest"] if step == 0 else seed
        ),
        bytes=conversion["bytes"],
    )


def _multiply(left, right):
    return tuple(
        tuple(
            sum(
                left[row][inner] * right[inner][column]
                for inner in range(len(right))
            )
            for column in range(len(right[0]))
        )
        for row in range(len(left))
    )


def _add(left, right):
    return tuple(
        tuple(a + b for a, b in zip(left_row, right_row, strict=True))
        for left_row, right_row in zip(left, right, strict=True)
    )


def _rms_norm(values, weights):
    return tuple(
        tuple(
            value * weight
            / math.sqrt(
                sum(scalar * scalar for scalar in row) / len(row) + 1e-5
            )
            for value, weight in zip(row, weights, strict=True)
        )
        for row in values
    )


def _rope(values, offset):
    result = []
    for position, row in enumerate(values, start=offset):
        rotated = []
        for left, right, frequency in (
            (row[0], row[1], 1.0),
            (row[2], row[3], 0.01),
        ):
            angle = position * frequency
            rotated.extend((
                left * math.cos(angle) - right * math.sin(angle),
                left * math.sin(angle) + right * math.cos(angle),
            ))
        result.append(tuple(rotated))
    return tuple(result)


def _attention(query, key, value):
    result = []
    for query_index, query_row in enumerate(query):
        scores = [
            sum(
                left * right
                for left, right in zip(query_row, key_row, strict=True)
            ) * 0.5
            for key_row in key[: query_index + 1]
        ]
        largest = max(scores)
        exponentials = [math.exp(score - largest) for score in scores]
        total = sum(exponentials)
        probabilities = [item / total for item in exponentials]
        result.append(tuple(
            sum(
                probability * value_row[column]
                for probability, value_row in zip(
                    probabilities,
                    value[: query_index + 1],
                    strict=True,
                )
            )
            for column in range(4)
        ))
    return tuple(result)


def _decoder_oracle(
    up_map,
    tokens: tuple[int, int],
    *,
    position_offset: int,
    prior: tuple[tuple[float, ...], tuple[float, ...]] | None = None,
):
    hidden = tuple(EMBEDDING[token] for token in tokens)
    attention_input = _rms_norm(hidden, NORM_ATTENTION)
    query = _rope(_multiply(attention_input, QUERY), position_offset)
    current_key = _rope(_multiply(attention_input, KEY), position_offset)
    current_value = _multiply(attention_input, VALUE)
    effective_key = current_key
    effective_value = current_value
    if prior is not None:
        effective_key = (prior[0], current_key[1])
        effective_value = (prior[1], current_value[1])
    attention = _attention(query, effective_key, effective_value)
    attention_output = _multiply(attention, ATTENTION_OUTPUT)
    residual_attention = _add(hidden, attention_output)
    feed_forward_input = _rms_norm(residual_attention, NORM_FFN)
    up = _multiply(feed_forward_input, _transpose(up_map))
    activated = tuple(
        tuple(value / (1.0 + math.exp(-value)) for value in row)
        for row in up
    )
    feed_forward_down = _multiply(activated, FFN_DOWN)
    residual_output = _add(residual_attention, feed_forward_down)
    final_hidden = _rms_norm(residual_output, NORM_FINAL)
    full_logits = _multiply(final_hidden, UNEMBEDDING)
    return (
        full_logits[-1],
        (current_key[-1], current_value[-1]),
        feed_forward_input,
        up,
    )


def _seed_for_unit(certificate_id: str, unit: int) -> int:
    weights = tuple(
        probability.numerator * (49 // probability.denominator)
        for probability in PROBABILITIES.values()
    )
    ceiling = 1 << 256
    accepted = ceiling - ceiling % sum(weights)
    for seed in range(100_000):
        attempt = 0
        while True:
            block = digest_bytes(canonical_bytes({
                "certificate_id": certificate_id,
                "step": 1,
                "seed": seed,
                "draw": 0,
                "attempt": attempt,
            }))
            value = int(block[7:], 16)
            attempt += 1
            if value < accepted:
                target = value % sum(weights)
                break
        cursor = 0
        for candidate, weight in zip(PROBABILITIES, weights, strict=True):
            cursor += weight
            if target < cursor:
                if candidate == unit:
                    return seed
                break
    raise AssertionError(f"no deterministic seed found for unit {unit}")


def _norm(values) -> float:
    return math.sqrt(sum(value * value for value in _flat(values)))


def _assert_execution_contract(
    outcomes: dict[int, tuple[float, float]],
    input_norm: float,
    *,
    coefficient: float,
) -> tuple[float, float]:
    atom_norm = math.sqrt(49 / 64)
    epsilon = 1.5
    delta = 0.5
    expected_local_squared = sum(
        float(PROBABILITIES[unit]) * local_error**2
        for unit, (local_error, _) in outcomes.items()
    )
    assert expected_local_squared <= (49 / 64) * input_norm**2 + 1e-9
    local_threshold = epsilon * atom_norm * input_norm
    local_risk = sum(
        PROBABILITIES[unit]
        for unit, (local_error, _) in outcomes.items()
        if local_error > local_threshold
    )
    assert local_risk <= delta
    for local_error, final_error in outcomes.values():
        assert final_error <= coefficient * local_error + 1e-6
    final_threshold = coefficient * epsilon * atom_norm * input_norm
    final_risk = sum(
        PROBABILITIES[unit]
        for unit, (_, final_error) in outcomes.items()
        if final_error > final_threshold
    )
    assert final_risk <= delta
    return float(local_risk), float(final_risk)


def test_q19_q36_q63_f3_decoder_trace_nonlinear_risk_and_kv_rollback(tmp_path):
    """Q19/Q36/Q63 acceptance: a certified causal decoder executes exact and fresh nonlinear paths, proves risk, and rolls KV back."""

    cartridge = tmp_path / "cartridge"
    values = {
        "embedding": EMBEDDING,
        "norm_attention": NORM_ATTENTION,
        "query": QUERY,
        "key": KEY,
        "value": VALUE,
        "attention_output": ATTENTION_OUTPUT,
        "norm_ffn": NORM_FFN,
        "exact.base": _transpose(TARGET),
        "fresh.base": _transpose(ZERO),
        "ffn_down": FFN_DOWN,
        "norm_final": NORM_FINAL,
        "unembedding": UNEMBEDDING,
        "exact.correction": _transpose(ZERO),
        **{
            f"fresh.unit{unit}": _transpose(_correction(unit))
            for unit in PROBABILITIES
        },
    }
    sources = {}
    for name, tensor in values.items():
        path = tmp_path / f"{name}.safetensors"
        _write_safetensors(
            path,
            ((name, "F32", _shape(tensor), _payload(tensor)),),
        )
        sources[path.name] = path
    root_digest = import_safetensors(
        sources,
        cartridge,
        _identity(*sources.values()),
    )
    root = load_root(cartridge, root_digest)
    pages = {
        row["semantic_tensor_id"]: row["spans"][0]["page_digest"]
        for row in root["tensor_maps"]
    }
    locations = {
        location.page_digest: location
        for location in page_locations(cartridge, root_digest)
    }
    plan, certificate, evidence, profile, page_map = _fixture(root_digest, pages)

    assert any(value < 0 for value in _flat(TARGET))
    assert any(value.denominator > 1 for value in _flat(TARGET))
    assert pages["fresh.base"] == pages["exact.correction"]

    malformed_map = copy.deepcopy(page_map)
    malformed_map["steps"][0]["exact_pages"][2] = pages["fresh.unit0"]
    malformed_plan = copy.deepcopy(plan)
    malformed_plan["page_map_digest"] = _digest(malformed_map)
    _seal(malformed_plan, "plan_id")
    assert isinstance(
        pager.CertifiedPager(
            cartridge,
            malformed_plan,
            certificate,
            evidence,
            profile,
            malformed_map,
        ),
        pager.CertifiedPager,
    )
    with pytest.raises(CassetteError) as graph_page:
        pager.CertifiedTransformer(
            cartridge,
            malformed_plan,
            certificate,
            evidence,
            profile,
            malformed_map,
        )
    assert graph_page.value.failed_invariant == (
        "Q36: exact F3 decoder description"
    )

    malformed_base = copy.deepcopy(page_map)
    malformed_base["steps"][0]["exact_pages"][7] = pages["fresh.unit0"]
    malformed_base_plan = copy.deepcopy(plan)
    malformed_base_plan["page_map_digest"] = _digest(malformed_base)
    _seal(malformed_base_plan, "plan_id")
    with pytest.raises(CassetteError) as base_page:
        pager.CertifiedTransformer(
            cartridge,
            malformed_base_plan,
            certificate,
            evidence,
            profile,
            malformed_base,
        )
    assert base_page.value.failed_invariant == (
        "Q36: exact F3 decoder description"
    )

    malformed_correction = copy.deepcopy(page_map)
    malformed_correction["steps"][1]["sample_units"][0]["page_digests"] = [
        pages["fresh.unit1"]
    ]
    malformed_correction_plan = copy.deepcopy(plan)
    malformed_correction_plan["page_map_digest"] = _digest(malformed_correction)
    _seal(malformed_correction_plan, "plan_id")
    with pytest.raises(CassetteError) as correction_page:
        pager.CertifiedTransformer(
            cartridge,
            malformed_correction_plan,
            certificate,
            evidence,
            profile,
            malformed_correction,
        )
    assert correction_page.value.failed_invariant == (
        "Q19/Q36: physical correction equals certified estimator"
    )

    malformed_graph_plan = copy.deepcopy(plan)
    malformed_graph_certificate = copy.deepcopy(certificate)
    malformed_graph_evidence = copy.deepcopy(evidence)
    malformed_graph_profile = copy.deepcopy(profile)
    malformed_graph_map = copy.deepcopy(page_map)
    malformed_graph_evidence["trace_contract"]["protected_trace_family"]["steps"][0][
        "operator_cases"
    ][14] = ADD_CASE
    _rebind(
        malformed_graph_plan,
        malformed_graph_certificate,
        malformed_graph_evidence,
        malformed_graph_profile,
        malformed_graph_map,
    )
    assert isinstance(
        pager.admit_schedule(
            malformed_graph_plan,
            malformed_graph_certificate,
            malformed_graph_evidence,
            malformed_graph_profile,
        ),
        pager.CertifiedSchedule,
    )
    with pytest.raises(CassetteError) as graph_operator:
        pager.CertifiedTransformer(
            cartridge,
            malformed_graph_plan,
            malformed_graph_certificate,
            malformed_graph_evidence,
            malformed_graph_profile,
            malformed_graph_map,
        )
    assert graph_operator.value.failed_invariant == (
        "Q30/Q36: generated F3 decoder graph"
    )

    stale_graph_plan = copy.deepcopy(plan)
    stale_graph_plan["tensor_graph_digest"] = _digest("another graph")
    _seal(stale_graph_plan, "plan_id")
    assert isinstance(
        pager.CertifiedPager(
            cartridge,
            stale_graph_plan,
            certificate,
            evidence,
            profile,
            page_map,
        ),
        pager.CertifiedPager,
    )
    with pytest.raises(CassetteError) as stale_graph:
        pager.CertifiedTransformer(
            cartridge,
            stale_graph_plan,
            certificate,
            evidence,
            profile,
            page_map,
        )
    assert stale_graph.value.failed_invariant == (
        "Q19/Q36: immutable protected decoder graph"
    )

    for field, value in (("hidden_size", 4.0), ("horizon", 2.0)):
        scalar_plan = copy.deepcopy(plan)
        scalar_certificate = copy.deepcopy(certificate)
        scalar_evidence = copy.deepcopy(evidence)
        scalar_profile = copy.deepcopy(profile)
        scalar_map = copy.deepcopy(page_map)
        scalar_evidence["trace_contract"]["protected_trace_family"][field] = value
        _rebind(
            scalar_plan,
            scalar_certificate,
            scalar_evidence,
            scalar_profile,
            scalar_map,
        )
        assert isinstance(
            pager.admit_schedule(
                scalar_plan,
                scalar_certificate,
                scalar_evidence,
                scalar_profile,
            ),
            pager.CertifiedSchedule,
        )
        with pytest.raises(CassetteError) as scalar_graph:
            pager.CertifiedTransformer(
                cartridge,
                scalar_plan,
                scalar_certificate,
                scalar_evidence,
                scalar_profile,
                scalar_map,
            )
        assert scalar_graph.value.failed_invariant == (
            "Q19/Q36: protected decoder graph"
        )

    for field in ("bytes", "memory_bytes_peak"):
        altered_plan = copy.deepcopy(plan)
        altered_certificate = copy.deepcopy(certificate)
        altered_evidence = copy.deepcopy(evidence)
        altered_profile = copy.deepcopy(profile)
        altered_map = copy.deepcopy(page_map)
        for owner in (
            altered_certificate["physical_conversion"]["conversion_rows"],
            altered_evidence["physical_conversion"]["conversion_rows"],
        ):
            owner[0][field] += 1
        _rebind(
            altered_plan,
            altered_certificate,
            altered_evidence,
            altered_profile,
            altered_map,
        )
        with pytest.raises(CassetteError) as hidden_resource:
            pager.CertifiedTransformer(
                cartridge,
                altered_plan,
                altered_certificate,
                altered_evidence,
                altered_profile,
                altered_map,
            )
        assert hidden_resource.value.failed_invariant == (
            "Q63: transformer trace equals certified schedule"
        )

    low_loss_plan = copy.deepcopy(plan)
    low_loss_certificate = copy.deepcopy(certificate)
    low_loss_evidence = copy.deepcopy(evidence)
    low_loss_profile = copy.deepcopy(profile)
    low_loss_map = copy.deepcopy(page_map)
    low_loss = {"coefficient": "1/20", "remainder_bound": "0"}
    low_loss_evidence["execution_contract"]["operations"][1][
        "loss_propagation"
    ] = low_loss
    low_loss_certificate["execution_contract"]["operations"][1][
        "loss_propagation_digest"
    ] = _digest(low_loss)
    low_loss_certificate["resources"]["epsilon_exec"] = 0.075
    _rebind(
        low_loss_plan,
        low_loss_certificate,
        low_loss_evidence,
        low_loss_profile,
        low_loss_map,
    )
    assert isinstance(
        pager.admit_schedule(
            low_loss_plan,
            low_loss_certificate,
            low_loss_evidence,
            low_loss_profile,
        ),
        pager.CertifiedSchedule,
    )

    async def run_pair(seed: int, prefill_tokens=PREFILL_TOKENS, decode_tokens=DECODE_TOKENS):
        transformer = pager.CertifiedTransformer(
            cartridge, plan, certificate, evidence, profile, page_map
        )
        prefill = await transformer.execute_token(
            _selection(certificate, evidence, 0), prefill_tokens
        )
        decode = await transformer.execute_token(
            _selection(certificate, evidence, 1, seed), decode_tokens
        )
        return transformer, prefill, decode

    async def exercise():
        malformed_tokens = pager.CertifiedTransformer(
            cartridge, plan, certificate, evidence, profile, page_map
        )
        with pytest.raises(CassetteError) as token_error:
            await malformed_tokens.execute_token(
                _selection(certificate, evidence, 0),
                (False, 1),
            )
        assert token_error.value.code == "INVALID_REQUEST"
        assert token_error.value.failed_invariant == (
            "Q36: bounded transformer activation"
        )
        assert malformed_tokens.last_attempt_transitions == ()
        assert malformed_tokens.kv_snapshot == b""

        continuity = pager.CertifiedTransformer(
            cartridge, plan, certificate, evidence, profile, page_map
        )
        await continuity.execute_token(
            _selection(certificate, evidence, 0), PREFILL_TOKENS
        )
        checkpoint = continuity.kv_snapshot
        with pytest.raises(CassetteError) as history_error:
            await continuity.execute_token(
                _selection(certificate, evidence, 1, 7),
                (3, 2),
            )
        assert history_error.value.failed_invariant == (
            "Q36: coherent recurrent token history"
        )
        assert continuity.kv_snapshot == checkpoint
        assert continuity.next_step == 1
        assert continuity.last_attempt_transitions == ()

        prefill_expected, prior, _, _ = _decoder_oracle(
            TARGET,
            PREFILL_TOKENS,
            position_offset=0,
        )
        exact_decode, _, decoder_input, exact_up = _decoder_oracle(
            TARGET,
            DECODE_TOKENS,
            position_offset=1,
            prior=prior,
        )
        executions = {}
        outcomes = {}
        for unit in PROBABILITIES:
            seed = _seed_for_unit(certificate["certificate_id"], unit)
            transformer, prefill, decode = await run_pair(seed)
            sampled_logits, _, sampled_input, sampled_up = _decoder_oracle(
                _correction(unit),
                DECODE_TOKENS,
                position_offset=1,
                prior=prior,
            )
            assert decode.page_execution.sample_units == (unit,)
            assert prefill.logits == pytest.approx(prefill_expected, abs=2e-5)
            assert decode.logits == pytest.approx(sampled_logits, abs=2e-5)
            assert _flat(sampled_input) == pytest.approx(
                _flat(decoder_input), abs=1e-12
            )
            local_error = _norm(tuple(
                sampled - exact
                for sampled, exact in zip(
                    _flat(sampled_up), _flat(exact_up), strict=True
                )
            ))
            final_error = _norm(tuple(
                sampled - exact
                for sampled, exact in zip(
                    decode.logits, exact_decode, strict=True
                )
            ))
            outcomes[unit] = (local_error, final_error)
            executions[unit] = (transformer, prefill, decode, seed)

        local_risk, final_risk = _assert_execution_contract(
            outcomes,
            _norm(decoder_input),
            coefficient=7 / 40,
        )
        assert local_risk == pytest.approx(1 / 49)
        assert final_risk == pytest.approx(1 / 49)
        low_loss_transformer = pager.CertifiedTransformer(
            cartridge,
            low_loss_plan,
            low_loss_certificate,
            low_loss_evidence,
            low_loss_profile,
            low_loss_map,
        )
        await low_loss_transformer.execute_token(
            _selection(low_loss_certificate, low_loss_evidence, 0),
            PREFILL_TOKENS,
        )
        low_loss_decode = await low_loss_transformer.execute_token(
            _selection(
                low_loss_certificate,
                low_loss_evidence,
                1,
                _seed_for_unit(low_loss_certificate["certificate_id"], 0),
            ),
            DECODE_TOKENS,
        )
        assert low_loss_decode.trace.loss_coefficient == pytest.approx(1 / 20)
        with pytest.raises(AssertionError):
            _assert_execution_contract(
                outcomes,
                _norm(decoder_input),
                coefficient=low_loss_decode.trace.loss_coefficient,
            )

        weighted_logits = tuple(
            sum(
                float(PROBABILITIES[unit])
                * executions[unit][2].logits[index]
                for unit in PROBABILITIES
            )
            for index in range(4)
        )
        assert weighted_logits != pytest.approx(exact_decode, abs=1e-5)

        replay_unit = 0
        replay_transformer, prefill_a, decode_a, replay_seed = executions[replay_unit]
        replay_b, prefill_b, decode_b = await run_pair(replay_seed)
        assert prefill_a.logits_digest == prefill_b.logits_digest
        assert decode_a.logits_digest == decode_b.logits_digest
        assert decode_a.kv_digest == decode_b.kv_digest
        assert replay_transformer.kv_snapshot == replay_b.kv_snapshot
        assert prefill_a.trace.phase == "PREFILL"
        assert prefill_a.trace.position_offset == 0
        assert decode_a.trace.phase == "DECODE"
        assert decode_a.trace.position_offset == 1
        for execution in (prefill_a, decode_a):
            assert execution.trace.logits_shape == (4,)
            assert len(execution.logits) == 4
            assert execution.trace.operator_cases == _operator_cases(
                execution.trace.schedule.step
            )
            assert execution.trace.page_reads == 12
            assert execution.trace.load_bytes == 624
            assert execution.trace.model_tensor_bytes == 624
            assert execution.trace.activation_bytes == 680
            assert execution.trace.kv_reserved_bytes == 64
            assert (
                execution.trace.model_memory_bytes
                == execution.trace.schedule.live_memory_bytes
            )
            assert all(
                [
                    target
                    for page, _, target in execution.page_execution.transitions
                    if page == page_digest
                ]
                == [
                    "ACQUIRING",
                    "HASHED",
                    "RESIDENT",
                    "GPU_SUBMITTED",
                    "RECLAIMABLE",
                ]
                for page_digest in execution.page_execution.planned_pages
            )
        assert prefill_a.trace.epsilon_exec == 0.0
        assert decode_a.trace.epsilon_exec == 1.5
        assert decode_a.trace.delta_exec == 0.5
        assert decode_a.trace.loss_coefficient == pytest.approx(7 / 40)
        assert decode_a.trace.remainder_bound == 0.0
        assert prefill_a.kv_bytes == 32
        assert decode_a.kv_bytes == 64

        changed_transformer, _, changed_history = await run_pair(
            replay_seed,
            (0, 3),
            (3, 2),
        )
        assert changed_history.logits_digest != decode_a.logits_digest
        assert changed_history.kv_digest != decode_a.kv_digest
        assert changed_transformer.kv_snapshot != replay_transformer.kv_snapshot

        selected_unit = decode_a.page_execution.sample_units[0]
        unselected_unit = next(
            unit for unit in PROBABILITIES if unit != selected_unit
        )
        unselected_original = _corrupt_pages(
            cartridge,
            locations,
            (pages[f"fresh.unit{unselected_unit}"],),
        )
        untouched, _, untouched_decode = await run_pair(replay_seed)
        assert untouched_decode.logits_digest == decode_a.logits_digest
        assert (
            pages[f"fresh.unit{unselected_unit}"]
            not in untouched_decode.page_execution.planned_pages
        )
        assert untouched.kv_snapshot == replay_transformer.kv_snapshot
        _restore_pages(unselected_original)

        exact_original = _corrupt_pages(
            cartridge,
            locations,
            (pages["exact.base"],),
        )
        exact_failure = pager.CertifiedTransformer(
            cartridge, plan, certificate, evidence, profile, page_map
        )
        with pytest.raises(CassetteError) as corrupt_exact:
            await exact_failure.execute_token(
                _selection(certificate, evidence, 0), PREFILL_TOKENS
            )
        assert corrupt_exact.value.code == "PAGE_CORRUPT"
        assert exact_failure.next_step == 0
        assert exact_failure.kv_snapshot == b""
        assert exact_failure.last_transformer is None
        assert not any(
            target == "GPU_SUBMITTED"
            for _, _, target in exact_failure.last_attempt_transitions
        )
        _restore_pages(exact_original)

        rollback = pager.CertifiedTransformer(
            cartridge, plan, certificate, evidence, profile, page_map
        )
        rollback_prefill = await rollback.execute_token(
            _selection(certificate, evidence, 0), PREFILL_TOKENS
        )
        checkpoint = rollback.kv_snapshot
        sampled_original = _corrupt_pages(
            cartridge,
            locations,
            (pages[f"fresh.unit{selected_unit}"],),
        )
        retry_selection = _selection(
            certificate,
            evidence,
            1,
            replay_seed,
        )
        with pytest.raises(CassetteError) as corrupt_sample:
            await rollback.execute_token(retry_selection, DECODE_TOKENS)
        assert corrupt_sample.value.code == "PAGE_CORRUPT"
        assert rollback.next_step == 1
        assert rollback.kv_snapshot == checkpoint
        assert rollback.last_transformer == rollback_prefill
        assert rollback.replay_selection == retry_selection
        assert not any(
            target == "GPU_SUBMITTED"
            for _, _, target in rollback.last_attempt_transitions
        )
        _restore_pages(sampled_original)
        retried = await rollback.execute_token(
            retry_selection, DECODE_TOKENS
        )
        assert retried.logits_digest == decode_a.logits_digest
        assert retried.kv_digest == decode_a.kv_digest

        committed_snapshot = rollback.kv_snapshot
        with pytest.raises(CassetteError) as horizon:
            await rollback.execute_token(
                _selection(certificate, evidence, 0), PREFILL_TOKENS
            )
        assert horizon.value.failed_invariant == (
            "Q64: certified execution horizon"
        )
        assert rollback.kv_snapshot == committed_snapshot
        assert rollback.last_transformer == retried

        wrong_runtime_plan = copy.deepcopy(plan)
        wrong_runtime_certificate = copy.deepcopy(certificate)
        wrong_runtime_evidence = copy.deepcopy(evidence)
        wrong_runtime_profile = copy.deepcopy(profile)
        wrong_runtime_map = copy.deepcopy(page_map)
        wrong_runtime_profile["runtime_buffer_bytes"] += 1
        _rebind(
            wrong_runtime_plan,
            wrong_runtime_certificate,
            wrong_runtime_evidence,
            wrong_runtime_profile,
            wrong_runtime_map,
        )
        wrong_runtime = pager.CertifiedTransformer(
            cartridge,
            wrong_runtime_plan,
            wrong_runtime_certificate,
            wrong_runtime_evidence,
            wrong_runtime_profile,
            wrong_runtime_map,
        )
        with pytest.raises(CassetteError) as hidden_allocation:
            await wrong_runtime.execute_token(
                _selection(
                    wrong_runtime_certificate,
                    wrong_runtime_evidence,
                    0,
                ),
                PREFILL_TOKENS,
            )
        assert hidden_allocation.value.failed_invariant == (
            "Q63: no hidden transformer allocation"
        )
        assert wrong_runtime.next_step == 0
        assert wrong_runtime.kv_snapshot == b""

    asyncio.run(exercise())
