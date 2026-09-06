# capture_fixture.py — deterministic protected teacher-trace corpus generation (Q18/Q19/Q30/Q40); depends on pager.py, schema, store.py.
"""Capture one generated dense fixture through the pinned MLX dispatch authority."""

from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pager
from schema.tables import DISPATCH_ROWS
from store import canonical_bytes, digest_bytes


CASE_ID = "mlx.matmul.f32.3x2_2x2"


def _identity(size: int) -> list[list[int]]:
    return [[1 if row == column else 0 for column in range(size)] for row in range(size)]


def capture() -> dict:
    """Return one immutable common, rare, ablation, and off-support evidence corpus."""

    row = next(item for item in DISPATCH_ROWS if item["case_id"] == CASE_ID)
    weights = _identity(2)
    ablated = [list(values) for values in weights]
    ablated[1] = [0, 0]
    conditions = (
        ("common", [[1, 0], [2, 0], [-1, 0]]),
        ("rare", [[0, 1], [0, 2], [0, -1]]),
    )
    traces = []
    for condition_id, inputs in conditions:
        full = pager.dispatch_float32(CASE_ID, (inputs, weights))
        removed = pager.dispatch_float32(CASE_ID, (inputs, ablated))
        traces.append({
            "condition_id": condition_id,
            "inputs": inputs,
            "teacher_logits": full,
            "ablated_logits": removed,
            "ablation_changed": full != removed,
        })
    metric = _identity(4)
    evidence = {
        "target": {
            "field": "REAL",
            "source_shape": [2, 2],
            "shape": [2, 2],
            "flattening_order": list(range(4)),
        },
        "conditions": [
            {
                "condition_id": condition_id,
                "metric": metric,
                "provenance": {
                    "trace": digest_bytes(canonical_bytes(trace)),
                },
            }
            for (condition_id, _), trace in zip(conditions, traces, strict=True)
        ],
        "atoms": [{
            "atom_id": "atom",
            "matrix": weights,
            "service_face_id": "face",
            "description": {
                "class": "EXACT",
                "description_bytes": 16,
                "metadata_bytes": 256,
                "reconstruction": weights,
                "estimator": {"kind": "NONE"},
                "estimator_calibration": {"distortion": "0", "atom_norm_squared": "2"},
                "sampling_law_id": "exact",
            },
        }],
        "description_contract": {
            "description_family": {"kind": "DECLARED_RECONSTRUCTION"},
            "distortion_metric": {"kind": "FROBENIUS_SQUARED"},
            "estimator_family": {"kind": "RESIDUAL_COLUMN_OR_EXACT"},
            "residual_family": {"relation": "ATOM_MINUS_RECONSTRUCTION"},
        },
        "observation_contract": {
            "kind": "PROTECTED_TEST_LAW",
            "experiment": {"name": "s24"},
            "support": [condition_id for condition_id, _ in conditions],
            "selector": [
                {"condition_id": condition_id, "atom_id": "atom"}
                for condition_id, _ in conditions
            ],
            "loss_family": {"kind": "condition-quadratic-loss"},
            "sample_count": len(traces),
            "confidence": 0.99,
            "off_support": "REJECT",
        },
        "execution_contract": {
            "sampling_laws": [{
                "sampling_law_id": "exact",
                "kind": "EXACT",
                "law": {"family": "NO_RESIDUAL", "atom_ids": ["atom"]},
                "work_unit": "COLUMNS",
                "seed_policy": "NONE",
            }],
            "operations": [{
                "operation_id": "matmul",
                "operator_case_id": CASE_ID,
                "rank_accounting": {"kind": "ATOM_BOUND", "maximum_rank": 2},
                "loss_propagation": {"coefficient": "1", "remainder_bound": "0"},
                "sampling_law_id": "exact",
            }],
            "risk_composition": {"kind": "DETERMINISTIC", "proof": {"rule": "exact"}},
        },
        "trace_contract": {
            "protected_trace_family": {"name": "s24"},
            "prefix_policy": "COHERENT_RESTRICTION",
            "fresh_traffic_unit": "SCALARS",
            "steps": [
                {
                    "step": step,
                    "operation_id": "matmul",
                    "atom_id": "atom",
                    "fresh_samples": 0,
                    "fresh_traffic": 0,
                }
                for step in range(len(traces))
            ],
        },
        "physical_conversion": {
            "conversion_rows": [{
                "operation_id": "matmul",
                "probe_unit": "COLUMNS",
                "probes": 0,
                "page_reads": 1,
                "bytes": 16,
                "memory_bytes_peak": 272,
                "latency_ns_peak": 0,
            }],
        },
        "minimal_nonface_proofs": [],
        "excluded_conditions": [{
            "condition_id": "off-support",
            "cause": "OFF_SUPPORT",
            "evidence": {"decision": "REJECT", "reason": "no immutable teacher trace"},
        }],
    }
    body = {
        "version": "s24-protected-trace-v1",
        "fixture_id": "s24-generated-dense",
        "operator_case": {
            name: row[name]
            for name in (
                "case_id", "operator", "input_dtypes", "input_shapes", "output_dtype",
                "output_shape", "parameters",
            )
        },
        "teacher_traces": traces,
        "certificate_inputs": {
            "evidence": evidence,
            "eta_rep": 0.0,
            "rank_budget": 2,
            "operation_bounds": [{
                "operation_id": "matmul",
                "epsilon_exec": 0.0,
                "delta_exec": 0.0,
            }],
        },
    }
    return {**body, "corpus_digest": digest_bytes(canonical_bytes(body))}


def capture_native(cartridge, root_digest: str, profile: dict, workload: dict) -> dict:
    """Q18/Q40: capture through the single numerical observation authority."""
    return pager.capture_native(cartridge, root_digest, profile, workload)


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: capture_fixture.py OUTPUT.json")
    path = Path(sys.argv[1])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(capture()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
