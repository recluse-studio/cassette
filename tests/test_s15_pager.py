# test_s15_pager.py — F3 certified tiny-transformer execution, trace, and KV rollback (Q19/Q36/Q63); depends on errors.py, pager.py, schema/tables.py, store.py, tests/test_s05_store.py, tests/test_s14_pager.py.
"""S15 proves one exact and one fresh-residual attention step from cartridge pages."""

from __future__ import annotations

import asyncio
import copy
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
    reason="S15 requires arm64 macOS with the pinned MLX Metal attention runtime",
)

GIB = 1024**3
ATTENTION_CASE = "mlx.attention.f32.1x1x2x2"
EMBEDDING = ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1))
QUERY_WEIGHT = ((1, 0), (0, 1), (0, 0))
KEY_WEIGHT = ((0, 1), (1, 0), (1, 1))
FRESH_EMBEDDING = ((1, -0.0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1))
FRESH_QUERY_WEIGHT = ((1, -0.0), (0, 1), (0, 0))
FRESH_KEY_WEIGHT = ((-0.0, 1), (1, 0), (1, 1))
TARGET = ((1, 0, 1), (0, 1, 1))
ZERO = ((0, 0, 0), (0, 0, 0))
ESTIMATORS = {
    0: ((4, 0, 0), (0, 0, 0)),
    1: ((0, 0, 0), (0, 4, 0)),
    2: ((0, 0, 2), (0, 0, 2)),
}
PREFILL_TOKENS = (0, 1)
DECODE_TOKENS = (2, 3)


def _digest(value: object) -> str:
    return digest_bytes(canonical_bytes(value))


def _seal(document: dict, identity_field: str) -> None:
    document[identity_field] = _digest(
        {name: value for name, value in document.items() if name != identity_field}
    )


def _normal_scalar(value: int) -> list[str]:
    return [str(value), "0"]


def _normal_matrix(matrix: tuple[tuple[int, ...], ...]) -> list[list[list[str]]]:
    return [[_normal_scalar(value) for value in row] for row in matrix]


def _payload(matrix: tuple[tuple[int | float, ...], ...]) -> bytes:
    values = tuple(value for row in matrix for value in row)
    return struct.pack(f"<{len(values)}f", *values)


def _transpose(matrix: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(row[column] for row in matrix) for column in range(len(matrix[0])))


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
) -> tuple[dict, dict, dict, dict, dict]:
    condition_ids = ("condition.exact", "condition.fresh")
    face_id = "face.all"
    cover = [
        {"condition_id": "condition.exact", "atom_id": "atom.exact"},
        {"condition_id": "condition.fresh", "atom_id": "atom.fresh"},
    ]
    exact_law_id = "sampling.exact"
    fresh_law_id = "sampling.fresh-columns"
    exact_operation = "operation.attention.exact"
    fresh_operation = "operation.attention.fresh"
    exact_metadata = _metadata(
        "atom.exact", exact_operation, "EXACT", exact_law_id, ()
    )
    fresh_metadata = _metadata(
        "atom.fresh",
        fresh_operation,
        "FRESH_RANDOM",
        fresh_law_id,
        ((0, "1/4"), (1, "1/4"), (2, "1/2")),
    )
    target_values = [value for row in TARGET for value in row]
    target_evidence = {
        "field": "REAL",
        "source_shape": [2, 3],
        "source_values": target_values,
        "shape": [2, 3],
        "flattening_order": [0, 1, 2, 3, 4, 5],
    }
    target_record = {
        "field": "REAL",
        "shape": [2, 3],
        "values": _normal_matrix(TARGET),
    }
    flattening_record = {
        "source_shape": [2, 3],
        "target_shape": [2, 3],
        "order": [0, 1, 2, 3, 4, 5],
    }
    identity_metric = [
        ["1" if row == column else "0" for column in range(6)]
        for row in range(6)
    ]
    positive_minors = [_normal_scalar(1) for _ in range(6)]
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
    estimator_none = {"kind": "NONE"}
    estimator_fresh = {"kind": "FRESH_RESIDUAL_COLUMN_AVERAGE"}
    exact_calibration = {"distortion": "0", "atom_norm_squared": "4"}
    fresh_calibration = {"distortion": "4", "atom_norm_squared": "4"}
    atom_evidence = [
        {
            "atom_id": "atom.exact",
            "matrix": [list(row) for row in TARGET],
            "service_face_id": face_id,
            "description": {
                "class": "EXACT",
                "description_bytes": 120,
                "metadata_bytes": len(exact_metadata),
                "reconstruction": [list(row) for row in TARGET],
                "estimator": estimator_none,
                "estimator_calibration": exact_calibration,
                "sampling_law_id": exact_law_id,
            },
        },
        {
            "atom_id": "atom.fresh",
            "matrix": [list(row) for row in TARGET],
            "service_face_id": face_id,
            "description": {
                "class": "BLOCK",
                "description_bytes": 120,
                "metadata_bytes": len(fresh_metadata),
                "reconstruction": [list(row) for row in ZERO],
                "estimator": estimator_fresh,
                "estimator_calibration": fresh_calibration,
                "sampling_law_id": fresh_law_id,
            },
        },
    ]
    atom_claims = []
    for row in atom_evidence:
        reconstruction = tuple(tuple(value for value in item) for item in row["description"]["reconstruction"])
        residual = tuple(
            tuple(value - rebuilt for value, rebuilt in zip(target_row, rebuilt_row, strict=True))
            for target_row, rebuilt_row in zip(TARGET, reconstruction, strict=True)
        )
        atom_claims.append({
            "atom_id": row["atom_id"],
            "witness_digest": _digest(_normal_matrix(TARGET)),
            "rank": 2,
            "service_face_id": face_id,
            "witness_losses": [
                {"condition_id": condition_id, "loss": 0.0}
                for condition_id in condition_ids
            ],
            "description": {
                "class": row["description"]["class"],
                "reconstruction_digest": _digest(_normal_matrix(reconstruction)),
                "residual_relation_digest": _digest(_normal_matrix(residual)),
                "distortion_bound": float(row["description"]["estimator_calibration"]["distortion"]),
                "estimator_digest": _digest(row["description"]["estimator"]),
                "estimator_calibration_digest": _digest(row["description"]["estimator_calibration"]),
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
                    {"column": 0, "probability": "1/4"},
                    {"column": 1, "probability": "1/4"},
                    {"column": 2, "probability": "1/2"},
                ],
            }],
        },
        "work_unit": "COLUMNS",
        "seed_policy": "RECORDED_COUNTER_KEY",
    }
    rank_accounting = {"kind": "ATOM_BOUND", "maximum_rank": 2}
    loss_propagation = {"coefficient": "2", "remainder_bound": "0"}
    operations = [
        {
            "operation_id": exact_operation,
            "operator_case_id": ATTENTION_CASE,
            "rank_accounting": rank_accounting,
            "loss_propagation": loss_propagation,
            "sampling_law_id": exact_law_id,
        },
        {
            "operation_id": fresh_operation,
            "operator_case_id": ATTENTION_CASE,
            "rank_accounting": rank_accounting,
            "loss_propagation": loss_propagation,
            "sampling_law_id": fresh_law_id,
        },
    ]
    operation_claims = [
        {
            "operation_id": exact_operation,
            "operator_case_id": ATTENTION_CASE,
            "rank_accounting_digest": _digest(rank_accounting),
            "loss_propagation_digest": _digest(loss_propagation),
            "remainder_bound": 0.0,
            "epsilon_exec": 0.0,
            "delta_exec": 0.0,
            "sampling_law_id": exact_law_id,
        },
        {
            "operation_id": fresh_operation,
            "operator_case_id": ATTENTION_CASE,
            "rank_accounting_digest": _digest(rank_accounting),
            "loss_propagation_digest": _digest(loss_propagation),
            "remainder_bound": 0.0,
            "epsilon_exec": 2.0,
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
            "fresh_traffic": 2,
        },
    ]
    trace_rows = [
        {
            **trace_steps[0],
            "description_bytes_resident": 120,
            "metadata_bytes_resident": len(exact_metadata),
            "epsilon_exec": 0.0,
            "delta_exec": 0.0,
        },
        {
            **trace_steps[1],
            "description_bytes_resident": 120,
            "metadata_bytes_resident": len(fresh_metadata),
            "epsilon_exec": 2.0,
            "delta_exec": 0.5,
        },
    ]
    schedule_rows = [
        {
            **{name: value for name, value in row.items() if name not in {"epsilon_exec", "delta_exec"}},
            "epsilon_exec": "0" if row["step"] == 0 else "2",
            "delta_exec": "0" if row["step"] == 0 else "1/2",
        }
        for row in trace_rows
    ]
    physical_rows = [
        {
            "operation_id": exact_operation,
            "probe_unit": "COLUMNS",
            "probes": 0,
            "page_reads": 4,
            "bytes": 120,
            "memory_bytes_peak": 240 + len(exact_metadata),
            "latency_ns_peak": 1000,
        },
        {
            "operation_id": fresh_operation,
            "probe_unit": "COLUMNS",
            "probes": 1,
            "page_reads": 5,
            "bytes": 144,
            "memory_bytes_peak": 264 + len(fresh_metadata),
            "latency_ns_peak": 1000,
        },
    ]
    metadata_peak = max(len(exact_metadata), len(fresh_metadata))
    metadata_total = len(exact_metadata) + len(fresh_metadata)
    resources = {
        "eta_rep": 0.0,
        "epsilon_exec": 4.0,
        "delta_exec_total": 0.5,
        "atom_count": 2,
        "max_atom_rank": 2,
        "description_bytes_peak": 120,
        "description_bytes_total": 240,
        "metadata_bytes_peak": metadata_peak,
        "metadata_bytes_total": metadata_total,
        "fresh_samples_max": 1,
        "fresh_samples_total": 1,
        "fresh_traffic_max": 2,
        "fresh_traffic_total": 2,
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
        "experiment": {"name": "S15 exact-and-fresh attention"},
        "support": list(condition_ids),
        "selector": copy.deepcopy(cover),
        "loss_family": {"kind": "identity-quadratic-loss"},
        "sample_count": 2,
        "confidence": 0.99,
        "off_support": "REJECT",
    }
    trace = {
        "protected_trace_family": {"name": "S15 prefill-then-decode"},
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
            "shape": [2, 3],
            "field": "REAL",
        },
        "condition_metrics": condition_claims,
        "compatibility": {
            "eta_rep": 0.0,
            "rank_budget": 2,
            "service_faces": [{"face_id": face_id, "condition_ids": list(condition_ids)}],
            "minimal_nonfaces": [],
            "cover": copy.deepcopy(cover),
            "excluded_conditions": [],
        },
        "atoms": atom_claims,
        "description_contract": {
            "description_family_digest": _digest(description_contract["description_family"]),
            "distortion_metric_digest": _digest(description_contract["distortion_metric"]),
            "residual_family_digest": _digest(description_contract["residual_family"]),
            "estimator_family_digest": _digest(description_contract["estimator_family"]),
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
            "protected_trace_family_digest": _digest(trace["protected_trace_family"]),
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
                    "description_bytes": 120,
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
                    "description_bytes": 120,
                    "metadata_bytes": len(fresh_metadata),
                    "fresh_samples_max": 1,
                    "fresh_samples_total": 1,
                    "fresh_traffic_max": 2,
                    "fresh_traffic_total": 2,
                    "epsilon_exec": 2.0,
                    "delta_exec": 0.5,
                },
            ],
            "per_operation": [
                {
                    "operation_id": exact_operation,
                    "description_bytes_peak": 120,
                    "description_bytes_total": 120,
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
                    "description_bytes_peak": 120,
                    "description_bytes_total": 120,
                    "metadata_bytes_peak": len(fresh_metadata),
                    "metadata_bytes_total": len(fresh_metadata),
                    "fresh_samples_max": 1,
                    "fresh_samples_total": 1,
                    "fresh_traffic_max": 2,
                    "fresh_traffic_total": 2,
                    "epsilon_exec": 2.0,
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
        "activation_bytes": 128,
        "cache_bytes": 0,
        "context_bytes": 64,
        "execution_bytes": GIB,
        "other_observed_bytes": GIB,
        "physical_bytes": 16 * GIB,
        "recommended_max_working_set_bytes": 16 * GIB,
        "runtime_buffer_bytes": 36,
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
        "tensor_graph_digest": _digest("S15 tensor graph"),
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
    page_map = {
        "root_digest": root_digest,
        "steps": [
            {
                "step": 0,
                "operation_id": exact_operation,
                "atom_id": "atom.exact",
                "description_digest": _digest(atom_claims[0]["description"]),
                "exact_pages": [
                    pages["exact.embedding"],
                    pages["exact.query"],
                    pages["exact.key"],
                    pages["exact.value"],
                ],
                "sample_units": [],
            },
            {
                "step": 1,
                "operation_id": fresh_operation,
                "atom_id": "atom.fresh",
                "description_digest": _digest(atom_claims[1]["description"]),
                "exact_pages": [
                    pages["fresh.embedding"],
                    pages["fresh.query"],
                    pages["fresh.key"],
                    pages["fresh.base"],
                ],
                "sample_units": [
                    {"unit": 0, "page_digests": [pages["fresh.unit0"]]},
                    {"unit": 1, "page_digests": [pages["fresh.unit1"]]},
                    {"unit": 2, "page_digests": [pages["fresh.unit2"]]},
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
    certificate["physical_conversion"]["conversion_digest"] = _digest(
        certificate["physical_conversion"]["conversion_rows"]
    )
    _seal(certificate, "certificate_id")
    plan["certificate_id"] = certificate["certificate_id"]
    plan["target_digest"] = certificate["target"]["target_digest"]
    plan["profile_digest"] = _digest(profile)
    plan["page_map_digest"] = _digest(page_map)
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


def _transformer_oracle(
    value: tuple[tuple[int, ...], ...],
    tokens: tuple[int, int],
    prior: tuple[tuple[tuple[float, ...], ...], tuple[tuple[float, ...], ...]] | None = None,
) -> tuple[
    tuple[float, ...],
    tuple[tuple[tuple[float, ...], ...], tuple[tuple[float, ...], ...]],
]:
    hidden = tuple(EMBEDDING[token] for token in tokens)

    def multiply(left, right):
        return tuple(
            tuple(
                sum(left[row][inner] * right[inner][column] for inner in range(len(right)))
                for column in range(len(right[0]))
            )
            for row in range(len(left))
        )

    query = multiply(hidden, QUERY_WEIGHT)
    key = multiply(hidden, KEY_WEIGHT)
    projected_value = multiply(hidden, _transpose(value))
    if prior is not None:
        key = (prior[0][0], key[1])
        projected_value = (prior[1][0], projected_value[1])
    probabilities = []
    for query_row in query:
        scores = [
            sum(left * right for left, right in zip(query_row, key_row, strict=True))
            / math.sqrt(2)
            for key_row in key
        ]
        largest = max(scores)
        exponentials = [math.exp(score - largest) for score in scores]
        total = sum(exponentials)
        probabilities.append(tuple(item / total for item in exponentials))
    logits = tuple(
        sum(probabilities[row][inner] * projected_value[inner][column] for inner in range(2))
        for row in range(2)
        for column in range(2)
    )
    return logits, (key, projected_value)


def test_q19_q36_q63_f3_transformer_trace_seed_and_kv_rollback(tmp_path):
    """Q19/Q36/Q63 acceptance: exact and fresh attention obey one certified trace, and failures roll KV back."""

    cartridge = tmp_path / "cartridge"
    sources = {}
    matrices = {
        "exact.embedding": EMBEDDING,
        "exact.query": QUERY_WEIGHT,
        "exact.key": KEY_WEIGHT,
        "exact.value": _transpose(TARGET),
        "fresh.embedding": FRESH_EMBEDDING,
        "fresh.query": FRESH_QUERY_WEIGHT,
        "fresh.key": FRESH_KEY_WEIGHT,
        "fresh.base": _transpose(ZERO),
        "fresh.unit0": _transpose(ESTIMATORS[0]),
        "fresh.unit1": _transpose(ESTIMATORS[1]),
        "fresh.unit2": _transpose(ESTIMATORS[2]),
    }
    for name, matrix in matrices.items():
        path = tmp_path / f"{name}.safetensors"
        _write_safetensors(
            path,
            ((name, "F32", (len(matrix), len(matrix[0])), _payload(matrix)),),
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

    malformed_map = copy.deepcopy(page_map)
    malformed_map["steps"][0]["exact_pages"][-1] = pages["fresh.base"]
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
    with pytest.raises(CassetteError) as semantic_page:
        pager.CertifiedTransformer(
            cartridge,
            malformed_plan,
            certificate,
            evidence,
            profile,
            malformed_map,
        )
    assert semantic_page.value.failed_invariant == (
        "Q19/Q36: physical description equals certified reconstruction"
    )

    malformed_correction_map = copy.deepcopy(page_map)
    malformed_correction_map["steps"][1]["sample_units"][0]["page_digests"] = [
        pages["fresh.unit1"]
    ]
    malformed_correction_plan = copy.deepcopy(plan)
    malformed_correction_plan["page_map_digest"] = _digest(malformed_correction_map)
    _seal(malformed_correction_plan, "plan_id")
    assert isinstance(
        pager.CertifiedPager(
            cartridge,
            malformed_correction_plan,
            certificate,
            evidence,
            profile,
            malformed_correction_map,
        ),
        pager.CertifiedPager,
    )
    with pytest.raises(CassetteError) as semantic_correction:
        pager.CertifiedTransformer(
            cartridge,
            malformed_correction_plan,
            certificate,
            evidence,
            profile,
            malformed_correction_map,
        )
    assert semantic_correction.value.failed_invariant == (
        "Q19/Q36: physical correction equals certified estimator"
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

    async def run_pair(seed: int, prefill_tokens=PREFILL_TOKENS):
        transformer = pager.CertifiedTransformer(
            cartridge, plan, certificate, evidence, profile, page_map
        )
        prefill = await transformer.execute_token(
            _selection(certificate, evidence, 0), prefill_tokens
        )
        decode = await transformer.execute_token(
            _selection(certificate, evidence, 1, seed), DECODE_TOKENS
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
        assert token_error.value.failed_invariant == "Q36: bounded transformer activation"
        assert malformed_tokens.last_attempt_transitions == ()
        assert malformed_tokens.kv_snapshot == b""

        replay_a, prefill_a, decode_a = await run_pair(7)
        replay_b, prefill_b, decode_b = await run_pair(7)
        prefill_expected, prior = _transformer_oracle(TARGET, PREFILL_TOKENS)
        decode_expected, _ = _transformer_oracle(
            ESTIMATORS[decode_a.page_execution.sample_units[0]],
            DECODE_TOKENS,
            prior,
        )
        exact_decode, _ = _transformer_oracle(TARGET, DECODE_TOKENS, prior)
        sampled_decodes = {
            unit: _transformer_oracle(estimator, DECODE_TOKENS, prior)[0]
            for unit, estimator in ESTIMATORS.items()
        }
        probabilities = {0: 0.25, 1: 0.25, 2: 0.5}
        assert tuple(
            sum(probabilities[unit] * sampled_decodes[unit][index] for unit in ESTIMATORS)
            for index in range(4)
        ) == pytest.approx(exact_decode, abs=1e-12)
        assert prefill_a.logits == pytest.approx(prefill_expected, abs=1e-6)
        assert decode_a.logits == pytest.approx(
            decode_expected,
            abs=1e-6,
        )
        assert prefill_a.page_execution.sample_units == ()
        assert prefill_a.page_execution.execution_seed is None
        assert prefill_a.trace.phase == "PREFILL"
        assert decode_a.trace.phase == "DECODE"
        assert prefill_a.trace.page_reads == prefill_a.trace.schedule.page_reads == 4
        assert prefill_a.trace.load_bytes == prefill_a.trace.schedule.load_bytes == 120
        assert decode_a.trace.page_reads == decode_a.trace.schedule.page_reads == 5
        assert decode_a.trace.load_bytes == decode_a.trace.schedule.load_bytes == 144
        for execution in (prefill_a, decode_a):
            assert execution.trace.model_memory_bytes == execution.trace.schedule.live_memory_bytes
            assert execution.trace.operator_cases == (
                "mlx.embedding.f32_u32.4x3_2",
                "mlx.matmul.f32.2x3_3x2",
                "mlx.matmul.f32.2x3_3x2",
                "mlx.matmul.f32.2x3_3x2",
                ATTENTION_CASE,
            )
            assert execution.trace.model_tensor_bytes == 120
            assert execution.trace.activation_bytes == 128
            assert execution.trace.kv_reserved_bytes == 64
            assert execution.trace.runtime_buffer_bytes == 36
            assert execution.trace.metal_peak_bytes == 284
            assert all(
                [target for page, _, target in execution.page_execution.transitions if page == page_digest]
                == ["ACQUIRING", "HASHED", "RESIDENT", "GPU_SUBMITTED", "RECLAIMABLE"]
                for page_digest in execution.page_execution.planned_pages
            )
        assert prefill_a.kv_bytes == 32
        assert decode_a.kv_bytes == 64
        assert prefill_a.logits_digest == prefill_b.logits_digest
        assert decode_a.logits_digest == decode_b.logits_digest
        assert decode_a.page_execution.sample_units == decode_b.page_execution.sample_units
        assert decode_a.kv_digest == decode_b.kv_digest
        assert replay_a.kv_snapshot == replay_b.kv_snapshot
        _, _, changed_history = await run_pair(7, (3, 1))
        assert changed_history.logits_digest != decode_a.logits_digest
        assert changed_history.kv_digest != decode_a.kv_digest

        alternate_seed = None
        alternate = None
        for seed in range(8, 64):
            _, _, candidate = await run_pair(seed)
            if candidate.page_execution.sample_units != decode_a.page_execution.sample_units:
                alternate_seed = seed
                alternate = candidate
                break
        assert alternate_seed is not None and alternate is not None
        assert alternate.logits_digest != decode_a.logits_digest
        assert alternate.kv_digest != decode_a.kv_digest

        selected_unit = decode_a.page_execution.sample_units[0]
        unselected_unit = next(unit for unit in ESTIMATORS if unit != selected_unit)
        unselected_original = _corrupt_pages(
            cartridge, locations, (pages[f"fresh.unit{unselected_unit}"],)
        )
        untouched, _, untouched_decode = await run_pair(7)
        assert untouched_decode.logits_digest == decode_a.logits_digest
        assert pages[f"fresh.unit{unselected_unit}"] not in untouched_decode.page_execution.planned_pages
        assert untouched.kv_snapshot == replay_a.kv_snapshot
        _restore_pages(unselected_original)

        exact_original = _corrupt_pages(
            cartridge, locations, (pages["exact.value"],)
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
        retry_selection = _selection(certificate, evidence, 1, 7)
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
        retried = await rollback.execute_token(retry_selection, DECODE_TOKENS)
        assert retried.logits_digest == decode_a.logits_digest
        assert retried.kv_digest == decode_a.kv_digest

        committed_snapshot = rollback.kv_snapshot
        with pytest.raises(CassetteError) as horizon:
            await rollback.execute_token(
                _selection(certificate, evidence, 0), PREFILL_TOKENS
            )
        assert horizon.value.failed_invariant == "Q64: certified execution horizon"
        assert rollback.kv_snapshot == committed_snapshot
        assert rollback.last_transformer == retried

        wrong_runtime_plan = copy.deepcopy(plan)
        wrong_runtime_certificate = copy.deepcopy(certificate)
        wrong_runtime_evidence = copy.deepcopy(evidence)
        wrong_runtime_profile = copy.deepcopy(profile)
        wrong_runtime_map = copy.deepcopy(page_map)
        wrong_runtime_profile["runtime_buffer_bytes"] = 37
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
                _selection(wrong_runtime_certificate, wrong_runtime_evidence, 0),
                PREFILL_TOKENS,
            )
        assert hidden_allocation.value.failed_invariant == (
            "Q63: no hidden transformer allocation"
        )
        assert wrong_runtime.next_step == 0
        assert wrong_runtime.kv_snapshot == b""

    asyncio.run(exercise())
