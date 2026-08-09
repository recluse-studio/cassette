# test_s13_pager.py — F2 fixture for Q19 certificate truth, Q47 memory admission, and Q63 schedules; depends on errors.py, pager.py, schema/tables.py, schema/validator.py, store.py.
"""S13 proves exact certificate recomputation before any residency schedule is admitted."""

from __future__ import annotations

import copy
import math
from fractions import Fraction

import pytest

import pager
from errors import CassetteError
from schema.tables import OPERATOR_DISPATCH, Q40_MODES
from schema.validator import validate
from store import canonical_bytes, digest_bytes

GIB = 1024**3
TARGET = [
    [1, 0, -1],
    [1, 1, 0],
    [0, 1, 1],
]
ATOMS = {
    "atom.ab": [[1, 1, 0], [1, 1, 0], [1, 1, 0]],
    "atom.ac": [[1, 0, -1], [1, 0, -1], [-1, 0, 1]],
    "atom.bc": [[0, -1, -1], [0, 1, 1], [0, 1, 1]],
}
CONDITION_COORDINATES = {
    "condition.a": {0, 3},
    "condition.b": {4, 7},
    "condition.c": {2, 8},
}
SERVICE_FACES = {
    "atom.ab": ("face.ab", ["condition.a", "condition.b"]),
    "atom.ac": ("face.ac", ["condition.a", "condition.c"]),
    "atom.bc": ("face.bc", ["condition.b", "condition.c"]),
}
SERVED_LOSS = Fraction(401, 100_300)
UNSERVED_LOSS = Fraction(601, 300)


def _digest(value: object) -> str:
    return digest_bytes(canonical_bytes(value))


def _seal(document: dict, identity_field: str) -> None:
    document[identity_field] = _digest(
        {name: value for name, value in document.items() if name != identity_field}
    )


def _normal_scalar(value: Fraction | int) -> list[str]:
    exact = Fraction(value)
    return [str(exact), "0"]


def _normal_matrix(matrix: list[list[int | str]]) -> list[list[list[int]]]:
    return [[_normal_scalar(Fraction(value)) for value in row] for row in matrix]


def _metric(condition_id: str) -> tuple[list[list[str]], list[list[int]]]:
    diagonal = [Fraction(1, 1000) for _ in range(9)]
    for coordinate in CONDITION_COORDINATES[condition_id]:
        diagonal[coordinate] += 1
    matrix = [
        [str(diagonal[row]) if row == column else "0" for column in range(9)]
        for row in range(9)
    ]
    product = Fraction(1)
    leading_minors = []
    for value in diagonal:
        product *= value
        leading_minors.append(_normal_scalar(product))
    return matrix, leading_minors


def _reconstruction(atom: list[list[int]]) -> list[list[int]]:
    result = copy.deepcopy(atom)
    result[0][0] -= 1
    return result


def _resources() -> dict:
    return {
        "eta_rep": 0.01,
        "epsilon_exec": 0.5,
        "delta_exec_total": 0.75,
        "atom_count": 3,
        "max_atom_rank": 1,
        "description_bytes_peak": 1024,
        "description_bytes_total": 3072,
        "metadata_bytes_peak": 256,
        "metadata_bytes_total": 768,
        "fresh_samples_max": 3,
        "fresh_samples_total": 9,
        "fresh_traffic_max": 9,
        "fresh_traffic_total": 27,
        "fresh_traffic_unit": "SCALARS",
        "horizon": 3,
    }


def _profile(boundary_field: str = "context_bytes") -> dict:
    profile = {
        "activation_bytes": 0,
        "cache_bytes": 0,
        "context_bytes": 0,
        "execution_bytes": GIB,
        "other_observed_bytes": GIB,
        "physical_bytes": 16 * GIB,
        "recommended_max_working_set_bytes": 16 * GIB,
        "runtime_buffer_bytes": 0,
        "training_window_bytes": 0,
    }
    profile[boundary_field] = 10 * GIB - 4096
    return profile


def _fixture() -> tuple[dict, dict, dict, dict]:
    target_values = [value for row in TARGET for value in row]
    target_evidence = {
        "field": "REAL",
        "source_shape": [3, 3],
        "source_values": target_values,
        "shape": [3, 3],
        "flattening_order": list(range(9)),
    }
    target_record = {
        "field": "REAL",
        "shape": [3, 3],
        "values": _normal_matrix(TARGET),
    }
    flattening_record = {
        "source_shape": [3, 3],
        "target_shape": [3, 3],
        "order": list(range(9)),
    }

    conditions = []
    condition_claims = []
    for condition_id in CONDITION_COORDINATES:
        metric, minors = _metric(condition_id)
        provenance = {"generator": "three-cycle", "condition_id": condition_id}
        conditions.append(
            {"condition_id": condition_id, "metric": metric, "provenance": provenance}
        )
        condition_claims.append(
            {
                "condition_id": condition_id,
                "provenance_digest": _digest(provenance),
                "metric_digest": _digest(_normal_matrix(metric)),
                "positive_definite_witness_digest": _digest(minors),
            }
        )

    sampling_law = {
        "sampling_law_id": "sampling.fresh-columns",
        "kind": "FRESH_RANDOM",
        "law": {
            "family": "FROBENIUS_RESIDUAL_COLUMNS",
            "adversary": "FIXED_QUERY_BEFORE_PRIVATE_COINS",
            "coins": "FRESH_INDEPENDENT",
            "atom_distributions": [
                {
                    "atom_id": atom_id,
                    "columns": [{"column": 0, "probability": "1"}],
                }
                for atom_id in ATOMS
            ],
        },
        "work_unit": "COLUMNS",
        "seed_policy": "RECORDED_COUNTER_KEY",
    }
    atom_evidence = []
    atom_claims = []
    for atom_id, matrix in ATOMS.items():
        face_id, face_conditions = SERVICE_FACES[atom_id]
        reconstruction = _reconstruction(matrix)
        residual = [
            [value - rebuilt for value, rebuilt in zip(row, rebuilt_row, strict=True)]
            for row, rebuilt_row in zip(matrix, reconstruction, strict=True)
        ]
        estimator = {"kind": "FRESH_RESIDUAL_COLUMN_AVERAGE"}
        calibration = {"distortion": "1", "atom_norm_squared": "6"}
        description = {
            "class": "BLOCK",
            "description_bytes": 1024,
            "metadata_bytes": 256,
            "reconstruction": reconstruction,
            "estimator": estimator,
            "estimator_calibration": calibration,
            "sampling_law_id": sampling_law["sampling_law_id"],
        }
        atom_evidence.append(
            {
                "atom_id": atom_id,
                "matrix": matrix,
                "service_face_id": face_id,
                "description": description,
            }
        )
        atom_claims.append(
            {
                "atom_id": atom_id,
                "witness_digest": _digest(_normal_matrix(matrix)),
                "rank": 1,
                "service_face_id": face_id,
                "witness_losses": [
                    {
                        "condition_id": condition_id,
                        "loss": float(
                            SERVED_LOSS
                            if condition_id in face_conditions
                            else UNSERVED_LOSS
                        ),
                    }
                    for condition_id in CONDITION_COORDINATES
                ],
                "description": {
                    "class": "BLOCK",
                    "reconstruction_digest": _digest(_normal_matrix(reconstruction)),
                    "residual_relation_digest": _digest(_normal_matrix(residual)),
                    "distortion_bound": 1.0,
                    "estimator_digest": _digest(estimator),
                    "estimator_calibration_digest": _digest(calibration),
                    "sampling_law_id": sampling_law["sampling_law_id"],
                },
            }
        )

    cover = [
        {"condition_id": "condition.a", "atom_id": "atom.ab"},
        {"condition_id": "condition.b", "atom_id": "atom.bc"},
        {"condition_id": "condition.c", "atom_id": "atom.ac"},
    ]
    nonface_proof = {
        "nonface_id": "nonface.abc",
        "condition_ids": list(CONDITION_COORDINATES),
        "kind": "UNBALANCED_RANK_ONE_CYCLE",
        "ambient_delta": "1/1000",
        "cycle": [
            {
                "condition_id": "condition.a",
                "diagonal": [0, 0],
                "successor": [1, 0],
                "gain": 1,
            },
            {
                "condition_id": "condition.b",
                "diagonal": [1, 1],
                "successor": [2, 1],
                "gain": 1,
            },
            {
                "condition_id": "condition.c",
                "diagonal": [2, 2],
                "successor": [0, 2],
                "gain": -1,
            },
        ],
    }
    description_contract = {
        "description_family": {"kind": "DECLARED_RECONSTRUCTION"},
        "distortion_metric": {"kind": "FROBENIUS_SQUARED"},
        "estimator_family": {"kind": "RESIDUAL_COLUMN_OR_EXACT"},
        "residual_family": {"relation": "ATOM_MINUS_RECONSTRUCTION"},
    }
    observation = {
        "kind": "PROTECTED_TEST_LAW",
        "experiment": {"name": "three-condition-cycle"},
        "support": list(CONDITION_COORDINATES),
        "selector": copy.deepcopy(cover),
        "loss_family": {"kind": "condition-quadratic-loss"},
        "sample_count": 300,
        "confidence": 0.99,
        "off_support": "REJECT",
    }
    rank_accounting = {"kind": "ATOM_BOUND", "maximum_rank": 1}
    loss_propagation = {"coefficient": "1/3", "remainder_bound": "0"}
    operation = {
        "operation_id": "operation.matmul",
        "operator_case_id": OPERATOR_DISPATCH["case_ids"][0],
        "rank_accounting": rank_accounting,
        "loss_propagation": loss_propagation,
        "sampling_law_id": sampling_law["sampling_law_id"],
    }
    risk = {"kind": "UNION_BOUND", "proof": {"rule": "Boole"}}
    execution = {
        "sampling_laws": [sampling_law],
        "operations": [operation],
        "risk_composition": risk,
    }
    trace_steps = [
        {
            "step": index,
            "operation_id": operation["operation_id"],
            "atom_id": atom_id,
            "fresh_samples": 3,
            "fresh_traffic": 9,
        }
        for index, atom_id in enumerate(ATOMS)
    ]
    trace = {
        "protected_trace_family": {"name": "one-use-per-certified-atom"},
        "prefix_policy": "COHERENT_RESTRICTION",
        "fresh_traffic_unit": "SCALARS",
        "steps": trace_steps,
    }
    trace_rows = [
        {
            **row,
            "description_bytes_resident": 1024,
            "metadata_bytes_resident": 256,
            "epsilon_exec": 0.5,
            "delta_exec": 0.25,
        }
        for row in trace_steps
    ]
    schedule_rows = [
        {
            **{name: value for name, value in row.items() if name not in {"epsilon_exec", "delta_exec"}},
            "epsilon_exec": "1/2",
            "delta_exec": "1/4",
        }
        for row in trace_rows
    ]
    physical_rows = [
        {
            "operation_id": operation["operation_id"],
            "probe_unit": "COLUMNS",
            "probes": 3,
            "page_reads": 1,
            "bytes": 4096,
            "memory_bytes_peak": 4096,
            "latency_ns_peak": 1000,
        }
    ]
    resources = _resources()
    certificate = {
        "certificate_version": "q19-v1",
        "certificate_id": _digest("unsealed-certificate"),
        "target": {
            "target_digest": _digest(target_record),
            "flattening_digest": _digest(flattening_record),
            "shape": [3, 3],
            "field": "REAL",
        },
        "condition_metrics": condition_claims,
        "compatibility": {
            "eta_rep": 0.01,
            "rank_budget": 1,
            "service_faces": [
                {"face_id": face_id, "condition_ids": list(condition_ids)}
                for face_id, condition_ids in SERVICE_FACES.values()
            ],
            "minimal_nonfaces": [
                {
                    "nonface_id": "nonface.abc",
                    "condition_ids": list(CONDITION_COORDINATES),
                    "witness_digest": _digest(nonface_proof),
                }
            ],
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
                    "sampling_law_id": sampling_law["sampling_law_id"],
                    "kind": sampling_law["kind"],
                    "law_digest": _digest(sampling_law["law"]),
                    "work_unit": sampling_law["work_unit"],
                    "seed_policy": sampling_law["seed_policy"],
                }
            ],
            "operations": [
                {
                    "operation_id": operation["operation_id"],
                    "operator_case_id": operation["operator_case_id"],
                    "rank_accounting_digest": _digest(rank_accounting),
                    "loss_propagation_digest": _digest(loss_propagation),
                    "remainder_bound": 0.0,
                    "epsilon_exec": 0.5,
                    "delta_exec": 0.25,
                    "sampling_law_id": sampling_law["sampling_law_id"],
                }
            ],
            "risk_composition_kind": risk["kind"],
            "risk_composition_digest": _digest(risk),
        },
        "trace_contract": {
            "protected_trace_family_digest": _digest(trace["protected_trace_family"]),
            "schedule_digest": _digest(
                {"prefix_policy": trace["prefix_policy"], "steps": schedule_rows}
            ),
            "prefix_policy": trace["prefix_policy"],
            "horizon": 3,
        },
        "resources": resources,
        "resource_tables": {
            "per_atom": [
                {
                    "atom_id": atom_id,
                    "description_bytes": 1024,
                    "metadata_bytes": 256,
                    "fresh_samples_max": 3,
                    "fresh_samples_total": 3,
                    "fresh_traffic_max": 9,
                    "fresh_traffic_total": 9,
                    "epsilon_exec": 0.5,
                    "delta_exec": 0.25,
                }
                for atom_id in ATOMS
            ],
            "per_operation": [
                {
                    "operation_id": operation["operation_id"],
                    "description_bytes_peak": 1024,
                    "description_bytes_total": 3072,
                    "metadata_bytes_peak": 256,
                    "metadata_bytes_total": 768,
                    "fresh_samples_max": 3,
                    "fresh_samples_total": 9,
                    "fresh_traffic_max": 9,
                    "fresh_traffic_total": 27,
                    "epsilon_exec": 0.5,
                    "delta_exec": 0.25,
                }
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
        "execution_contract": execution,
        "trace_contract": trace,
        "physical_conversion": {"conversion_rows": copy.deepcopy(physical_rows)},
        "minimal_nonface_proofs": [nonface_proof],
        "excluded_conditions": [],
    }
    profile = _profile()
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
        "tensor_graph_digest": _digest("tensor-graph"),
        "page_map_digest": _digest("page-map"),
        "layout_digest": _digest("layout"),
        "precision_planes_digest": _digest("precision-planes"),
        "semantic_manifest_digest": _digest("semantic-manifest"),
        "invalidation_graph_digest": _digest("invalidation-graph"),
        "dispatch": copy.deepcopy(OPERATOR_DISPATCH),
        "resource_limits": copy.deepcopy(resources),
        "artifact_refs": [certificate["target"]["target_digest"]],
        "weight_payload_bytes": 0,
    }
    _seal(plan, "plan_id")
    return plan, certificate, evidence, profile


def _bind(plan: dict, certificate: dict, profile: dict) -> None:
    _seal(certificate, "certificate_id")
    plan["certificate_id"] = certificate["certificate_id"]
    plan["target_digest"] = certificate["target"]["target_digest"]
    plan["profile_digest"] = _digest(profile)
    _seal(plan, "plan_id")


def _assert_refused(plan: dict, certificate: dict, evidence: dict, profile: dict) -> None:
    with pytest.raises(CassetteError) as caught:
        pager.admit_schedule(plan, certificate, evidence, profile)
    assert caught.value.code in {"CAPABILITY_MISMATCH", "INVALID_REQUEST"}


def _mutable_ids(value: object) -> set[int]:
    found = set()
    if isinstance(value, dict):
        found.add(id(value))
        for item in value.values():
            found.update(_mutable_ids(item))
    elif isinstance(value, list):
        found.add(id(value))
        for item in value:
            found.update(_mutable_ids(item))
    return found


def test_q19_q47_q63_f2_exact_certificate_recomputation_precedes_bounded_schedule_admission():
    """Q19/Q47/Q63 acceptance: exact evidence alone earns a time-indexed schedule within every memory boundary."""
    plan, certificate, evidence, profile = _fixture()
    boundaries = [_mutable_ids(value) for value in (plan, certificate, evidence, profile)]
    assert not any(
        left & right
        for index, left in enumerate(boundaries)
        for right in boundaries[index + 1 :]
    )
    assert validate("mathematical_certificate", certificate) == []
    assert validate("execution_plan", plan) == []

    schedule = pager.admit_schedule(plan, certificate, evidence, profile)
    assert schedule.reserve_bytes == 4 * GIB
    assert schedule.memory_ceiling_bytes == 12 * GIB
    assert schedule.available_bytes == 10 * GIB
    assert schedule.peak_live_bytes == 10 * GIB
    assert [step.step for step in schedule.steps] == [0, 1, 2]
    assert [step.atom_id for step in schedule.steps] == list(ATOMS)
    assert all(
        (step.description_bytes, step.metadata_bytes, step.fresh_samples, step.fresh_traffic)
        == (1024, 256, 3, 9)
        for step in schedule.steps
    )

    # The metric is positive definite but not product-form: entrywise whitening raises this
    # rank-one witness to rank two, so the fixture cannot be reduced to whiten-and-truncate.
    high = math.sqrt(1001 / 1000)
    low = math.sqrt(1 / 1000)
    assert high * low - low * low > 0

    for field in (
        "activation_bytes",
        "cache_bytes",
        "context_bytes",
        "runtime_buffer_bytes",
        "training_window_bytes",
    ):
        candidate_plan, candidate_certificate, candidate_evidence, candidate_profile = _fixture()
        candidate_profile = _profile(field)
        _bind(candidate_plan, candidate_certificate, candidate_profile)
        assert pager.admit_schedule(
            candidate_plan, candidate_certificate, candidate_evidence, candidate_profile
        ).peak_live_bytes == 10 * GIB
        candidate_profile[field] += 1
        _bind(candidate_plan, candidate_certificate, candidate_profile)
        with pytest.raises(CassetteError) as exceeded:
            pager.admit_schedule(
                candidate_plan, candidate_certificate, candidate_evidence, candidate_profile
            )
        assert exceeded.value.code == "MEMORY_BUDGET_EXCEEDED"

    competing_plan, competing_certificate, competing_evidence, competing_profile = _fixture()
    competing_profile.update(
        context_bytes=0,
        other_observed_bytes=11 * GIB - 4096,
    )
    _bind(competing_plan, competing_certificate, competing_profile)
    assert pager.admit_schedule(
        competing_plan, competing_certificate, competing_evidence, competing_profile
    ).peak_live_bytes == 4096
    competing_profile["other_observed_bytes"] += 1
    _bind(competing_plan, competing_certificate, competing_profile)
    with pytest.raises(CassetteError) as competing_exceeded:
        pager.admit_schedule(
            competing_plan, competing_certificate, competing_evidence, competing_profile
        )
    assert competing_exceeded.value.code == "MEMORY_BUDGET_EXCEEDED"

    rounded_plan, rounded_certificate, rounded_evidence, rounded_profile = _fixture()
    rounded_profile.update(
        physical_bytes=16 * GIB + 1,
        recommended_max_working_set_bytes=16 * GIB + 1,
        execution_bytes=0,
        other_observed_bytes=0,
        context_bytes=12 * GIB - 4096,
    )
    _bind(rounded_plan, rounded_certificate, rounded_profile)
    rounded = pager.admit_schedule(
        rounded_plan, rounded_certificate, rounded_evidence, rounded_profile
    )
    assert rounded.reserve_bytes == 4 * GIB + 1
    assert rounded.memory_ceiling_bytes == 12 * GIB

    recommended_plan, recommended_certificate, recommended_evidence, recommended_profile = _fixture()
    recommended_profile.update(
        physical_bytes=32 * GIB,
        recommended_max_working_set_bytes=10 * GIB,
        execution_bytes=0,
        other_observed_bytes=0,
        context_bytes=9 * GIB - 4096,
    )
    _bind(recommended_plan, recommended_certificate, recommended_profile)
    recommended = pager.admit_schedule(
        recommended_plan,
        recommended_certificate,
        recommended_evidence,
        recommended_profile,
    )
    assert recommended.memory_ceiling_bytes == 9 * GIB
    assert recommended.peak_live_bytes == 9 * GIB

    contradictions = []
    for mutation in (
        lambda cert, _: cert["resources"].__setitem__("description_bytes_total", 3073),
        lambda cert, _: cert["resources"].__setitem__("atom_count", 4),
        lambda cert, _: cert["resources"].__setitem__("horizon", 2),
        lambda cert, _: cert["resources"].__setitem__("epsilon_exec", 0.6),
        lambda cert, _: cert["resource_tables"]["per_operation"][0].update(
            description_bytes_peak=3073
        ),
        lambda cert, _: cert["resources"].__setitem__("eta_rep", 0.02),
        lambda cert, _: cert["atoms"][0].__setitem__("rank", 2),
    ):
        candidate_plan, candidate_certificate, candidate_evidence, candidate_profile = _fixture()
        mutation(candidate_certificate, candidate_plan)
        _bind(candidate_plan, candidate_certificate, candidate_profile)
        contradictions.append(
            (candidate_plan, candidate_certificate, candidate_evidence, candidate_profile)
        )
    limit_plan, limit_certificate, limit_evidence, limit_profile = _fixture()
    limit_plan["resource_limits"]["description_bytes_total"] = 3071
    _seal(limit_plan, "plan_id")
    contradictions.append((limit_plan, limit_certificate, limit_evidence, limit_profile))
    for candidate in contradictions:
        _assert_refused(*candidate)

    semantic_mutations = [
        lambda cert, ev: ev["target"]["flattening_order"].reverse(),
        lambda cert, ev: cert["atoms"][0]["witness_losses"][0].__setitem__(
            "loss", 0.5
        ),
        lambda cert, ev: cert["atoms"][0]["witness_losses"][0].__setitem__(
            "loss",
            math.nextafter(
                cert["atoms"][0]["witness_losses"][0]["loss"], math.inf
            ),
        ),
        lambda cert, ev: cert["compatibility"]["service_faces"][0].__setitem__(
            "condition_ids", list(CONDITION_COORDINATES)
        ),
        lambda cert, ev: cert["compatibility"].__setitem__("minimal_nonfaces", []),
        lambda cert, ev: cert["compatibility"]["cover"][2].__setitem__(
            "atom_id", "atom.ab"
        ),
        lambda cert, ev: ev["observation_contract"].__setitem__(
            "off_support", "ALLOW"
        ),
        lambda cert, ev: cert["atoms"][0]["description"].__setitem__(
            "distortion_bound", 2.0
        ),
        lambda cert, ev: cert["execution_contract"]["operations"][0].__setitem__(
            "epsilon_exec", 0.4
        ),
        lambda cert, ev: ev["execution_contract"]["operations"][0][
            "loss_propagation"
        ].__setitem__("coefficient", "1/2"),
        lambda cert, ev: cert["trace_contract"].__setitem__("horizon", 2),
    ]
    for mutation in semantic_mutations:
        candidate_plan, candidate_certificate, candidate_evidence, candidate_profile = _fixture()
        mutation(candidate_certificate, candidate_evidence)
        _bind(candidate_plan, candidate_certificate, candidate_profile)
        _assert_refused(
            candidate_plan, candidate_certificate, candidate_evidence, candidate_profile
        )

    for hostile_scalar in ("1e1000000000", "1e1000", 10**400):
        scalar_plan, scalar_certificate, scalar_evidence, scalar_profile = _fixture()
        scalar_evidence["target"]["source_values"][0] = hostile_scalar
        with pytest.raises(CassetteError) as scalar_refused:
            pager.admit_schedule(
                scalar_plan,
                scalar_certificate,
                scalar_evidence,
                scalar_profile,
            )
        assert scalar_refused.value.code == "INVALID_REQUEST"
        assert scalar_refused.value.failed_invariant == "Q19: canonical source scalar"

    range_plan, range_certificate, range_evidence, range_profile = _fixture()
    range_evidence["target"]["source_values"][0] = "1e200"
    range_target = copy.deepcopy(TARGET)
    range_target[0][0] = "1e200"
    range_certificate["target"]["target_digest"] = _digest(
        {"field": "REAL", "shape": [3, 3], "values": _normal_matrix(range_target)}
    )
    _bind(range_plan, range_certificate, range_profile)
    with pytest.raises(CassetteError) as range_refused:
        pager.admit_schedule(
            range_plan,
            range_certificate,
            range_evidence,
            range_profile,
        )
    assert range_refused.value.code == "CAPABILITY_MISMATCH"
    assert range_refused.value.failed_invariant == "Q19: witness loss condition.a"

    law_plan, law_certificate, law_evidence, law_profile = _fixture()
    law = law_evidence["execution_contract"]["sampling_laws"][0]["law"]
    law["atom_distributions"][0]["columns"] = [
        {"column": 1, "probability": "1"}
    ]
    law_certificate["execution_contract"]["sampling_laws"][0]["law_digest"] = _digest(
        law
    )
    _bind(law_plan, law_certificate, law_profile)
    _assert_refused(law_plan, law_certificate, law_evidence, law_profile)

    traffic_plan, traffic_certificate, traffic_evidence, traffic_profile = _fixture()
    for row in traffic_evidence["trace_contract"]["steps"]:
        row["fresh_traffic"] = 8
    for row in traffic_certificate["resource_tables"]["per_trace_step"]:
        row["fresh_traffic"] = 8
    for row in traffic_certificate["resource_tables"]["per_atom"]:
        row["fresh_traffic_max"] = 8
        row["fresh_traffic_total"] = 8
    operation_resources = traffic_certificate["resource_tables"]["per_operation"][0]
    operation_resources["fresh_traffic_max"] = 8
    operation_resources["fresh_traffic_total"] = 24
    traffic_certificate["resources"]["fresh_traffic_max"] = 8
    traffic_certificate["resources"]["fresh_traffic_total"] = 24
    traffic_plan["resource_limits"]["fresh_traffic_max"] = 8
    traffic_plan["resource_limits"]["fresh_traffic_total"] = 24
    traffic_schedule_rows = []
    for resource_row in traffic_certificate["resource_tables"]["per_trace_step"]:
        schedule_row = {
            name: value
            for name, value in resource_row.items()
            if name not in {"epsilon_exec", "delta_exec"}
        }
        schedule_row.update(epsilon_exec="1/2", delta_exec="1/4")
        traffic_schedule_rows.append(schedule_row)
    traffic_certificate["trace_contract"]["schedule_digest"] = _digest(
        {
            "prefix_policy": traffic_evidence["trace_contract"]["prefix_policy"],
            "steps": traffic_schedule_rows,
        }
    )
    _bind(traffic_plan, traffic_certificate, traffic_profile)
    _assert_refused(
        traffic_plan,
        traffic_certificate,
        traffic_evidence,
        traffic_profile,
    )

    probe_plan, probe_certificate, probe_evidence, probe_profile = _fixture()
    probe_evidence["physical_conversion"]["conversion_rows"][0]["probes"] = 2
    probe_certificate["physical_conversion"]["conversion_rows"][0]["probes"] = 2
    probe_certificate["physical_conversion"]["conversion_digest"] = _digest(
        probe_certificate["physical_conversion"]["conversion_rows"]
    )
    _bind(probe_plan, probe_certificate, probe_profile)
    _assert_refused(
        probe_plan,
        probe_certificate,
        probe_evidence,
        probe_profile,
    )

    estimator_plan, estimator_certificate, estimator_evidence, estimator_profile = _fixture()
    estimator = estimator_evidence["atoms"][0]["description"]["estimator"]
    estimator["kind"] = "BIASED_REUSE"
    estimator_certificate["atoms"][0]["description"]["estimator_digest"] = _digest(
        estimator
    )
    _bind(estimator_plan, estimator_certificate, estimator_profile)
    _assert_refused(
        estimator_plan,
        estimator_certificate,
        estimator_evidence,
        estimator_profile,
    )

    proof_plan, proof_certificate, proof_evidence, proof_profile = _fixture()
    proof_evidence["minimal_nonface_proofs"] = []
    _assert_refused(proof_plan, proof_certificate, proof_evidence, proof_profile)

    false_proof_plan, false_proof_certificate, false_proof_evidence, false_proof_profile = _fixture()
    false_proof = false_proof_evidence["minimal_nonface_proofs"][0]
    false_proof["cycle"][2]["gain"] = 1
    false_proof_certificate["compatibility"]["minimal_nonfaces"][0][
        "witness_digest"
    ] = _digest(false_proof)
    _bind(false_proof_plan, false_proof_certificate, false_proof_profile)
    _assert_refused(
        false_proof_plan,
        false_proof_certificate,
        false_proof_evidence,
        false_proof_profile,
    )

    rank_plan, rank_certificate, rank_evidence, rank_profile = _fixture()
    rank_matrix = [[1, 1, 0], [1, 1, 0], [1, 1, 1]]
    rank_reconstruction = _reconstruction(rank_matrix)
    rank_residual = [
        [value - rebuilt for value, rebuilt in zip(row, rebuilt_row, strict=True)]
        for row, rebuilt_row in zip(rank_matrix, rank_reconstruction, strict=True)
    ]
    rank_evidence["atoms"][0]["matrix"] = rank_matrix
    rank_evidence["atoms"][0]["description"]["reconstruction"] = rank_reconstruction
    rank_evidence["atoms"][0]["description"]["estimator_calibration"][
        "atom_norm_squared"
    ] = "7"
    rank_claim = rank_certificate["atoms"][0]
    rank_claim["rank"] = 2
    rank_claim["witness_digest"] = _digest(_normal_matrix(rank_matrix))
    rank_claim["witness_losses"] = [
        {"condition_id": "condition.a", "loss": float(Fraction(6017, 2_007_000))},
        {"condition_id": "condition.b", "loss": float(Fraction(6017, 2_007_000))},
        {"condition_id": "condition.c", "loss": float(Fraction(1_010_017, 1_007_000))},
    ]
    rank_claim["description"].update(
        reconstruction_digest=_digest(_normal_matrix(rank_reconstruction)),
        residual_relation_digest=_digest(_normal_matrix(rank_residual)),
        estimator_calibration_digest=_digest(
            rank_evidence["atoms"][0]["description"]["estimator_calibration"]
        ),
    )
    rank_map = rank_evidence["execution_contract"]["operations"][0][
        "rank_accounting"
    ]
    rank_map["maximum_rank"] = 2
    rank_certificate["execution_contract"]["operations"][0][
        "rank_accounting_digest"
    ] = _digest(rank_map)
    rank_certificate["resources"]["max_atom_rank"] = 2
    rank_plan["resource_limits"]["max_atom_rank"] = 2
    _bind(rank_plan, rank_certificate, rank_profile)
    _assert_refused(rank_plan, rank_certificate, rank_evidence, rank_profile)

    stale_plan, stale_certificate, stale_evidence, stale_profile = _fixture()
    stale_certificate["certificate_id"] = _digest("forged-certificate-identity")
    stale_plan["certificate_id"] = stale_certificate["certificate_id"]
    _seal(stale_plan, "plan_id")
    _assert_refused(stale_plan, stale_certificate, stale_evidence, stale_profile)

    stale_plan, stale_certificate, stale_evidence, stale_profile = _fixture()
    stale_plan["tensor_graph_digest"] = _digest("forged-tensor-graph")
    _assert_refused(stale_plan, stale_certificate, stale_evidence, stale_profile)

    uncovered_plan, uncovered_certificate, uncovered_evidence, uncovered_profile = _fixture()
    uncovered_certificate["compatibility"]["cover"].pop()
    uncovered_evidence["observation_contract"]["selector"].pop()
    _bind(uncovered_plan, uncovered_certificate, uncovered_profile)
    _assert_refused(
        uncovered_plan, uncovered_certificate, uncovered_evidence, uncovered_profile
    )

    off_support_plan, off_support_certificate, off_support_evidence, off_support_profile = _fixture()
    off_support_evidence["observation_contract"]["support"].append("condition.off-support")
    _assert_refused(
        off_support_plan,
        off_support_certificate,
        off_support_evidence,
        off_support_profile,
    )
