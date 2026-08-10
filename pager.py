# pager.py — certificate recomputation, page readiness, certified transformer execution, and pinned MLX dispatch (Q19/Q20/Q30/Q33/Q36/Q40/Q47/Q63/Q64); depends on errors.py, schema, store.py.
"""Admit certified schedules, validate their pages before use, and dispatch through MLX."""

from __future__ import annotations

import asyncio
import importlib.metadata
import math
import platform
import struct
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from errors import CassetteError
from schema.tables import DISPATCH_ROWS, MLX_RUNTIME, OPERATOR_DISPATCH, Q40_MODES
from schema.validator import validate
from store import _read_page, canonical_bytes, digest_bytes, page_locations

_CASES = {row["case_id"]: row for row in DISPATCH_ROWS}
_GIB = 1024**3
_MAX_ITEMS = 1_048_576
_MAX_U64 = 2**64 - 1
_MAX_BINARY64_INTEGER = int(sys.float_info.max)
# Admit the complete finite binary64 span, then stop exact-scalar growth at that boundary.
_MAX_EXACT_BITS = sys.float_info.max_exp + sys.float_info.mant_dig
_ZERO = (Fraction(0), Fraction(0))
_MLX = None


def _error(
    code: str,
    object_id: str,
    invariant: str,
    detail: str,
    *,
    retryability: str = "terminal",
) -> CassetteError:
    return CassetteError(code, object_id, invariant, retryability, detail)


def validate_plan(plan: object, certificate: object) -> None:
    """Q33/Q40: reject malformed, collapsed, stale, or executable plan data before MLX use."""
    plan_defects = validate("execution_plan", plan)
    certificate_defects = validate("mathematical_certificate", certificate)
    if plan_defects or certificate_defects:
        defects = [*plan_defects, *certificate_defects]
        object_id = plan.get("plan_id", "execution-plan") if isinstance(plan, dict) else "execution-plan"
        raise _error(
            "INVALID_REQUEST",
            object_id,
            "Q33: bounded mathematical certificate and plan schema",
            "; ".join(defects[:8]),
        )
    assert isinstance(plan, dict) and isinstance(certificate, dict)
    prior_modes = [item["mode"] for item in plan["prior_mode_failures"]]
    prior_ordinals = [item["ordinal"] for item in plan["prior_mode_failures"]]
    if prior_modes != Q40_MODES[:-1] or prior_ordinals != [1, 2, 3, 4]:
        raise _error(
            "INVALID_REQUEST",
            plan["plan_id"],
            "Q40: least-invasive mode order",
            "compiled mode requires one ordered Q38 failure for each prior mode",
        )
    if plan["certificate_id"] != certificate["certificate_id"]:
        raise _error(
            "CAPABILITY_MISMATCH",
            plan["plan_id"],
            "Q19: immutable certificate identity",
            "plan and certificate identities differ",
        )
    if plan["target_digest"] != certificate["target"]["target_digest"]:
        raise _error(
            "CAPABILITY_MISMATCH",
            plan["plan_id"],
            "Q19: immutable target identity",
            "plan and certificate targets differ",
        )
    if plan["dispatch"] != OPERATOR_DISPATCH:
        raise _error(
            "CAPABILITY_MISMATCH",
            plan["plan_id"],
            "Q30: generated dispatch identity",
            "plan dispatch differs from the pinned generated table",
        )
    declared_cases = set(plan["dispatch"]["case_ids"])
    foreign_cases = sorted(
        {
            operation["operator_case_id"]
            for operation in certificate["execution_contract"]["operations"]
        }
        - declared_cases
    )
    if foreign_cases:
        raise _error(
            "UNSUPPORTED_OPERATOR",
            foreign_cases[0],
            "Q30/Q33: certificate operator confinement",
            "certificate names an operator absent from the generated dispatch table",
        )


@dataclass(frozen=True)
class ResidencyStep:
    """Q63 time-indexed certified residency and transfer demand."""

    step: int
    operation_id: str
    atom_id: str
    description_bytes: int
    metadata_bytes: int
    fresh_samples: int
    fresh_traffic: int
    page_reads: int
    load_bytes: int
    dynamic_memory_bytes: int
    live_memory_bytes: int


@dataclass(frozen=True)
class CertifiedSchedule:
    """Q47/Q63 admission result bound to one certificate, plan, and measured profile."""

    plan_id: str
    certificate_id: str
    profile_digest: str
    reserve_bytes: int
    memory_ceiling_bytes: int
    available_bytes: int
    peak_live_bytes: int
    steps: tuple[ResidencyStep, ...]


@dataclass(frozen=True)
class NativePrefetch:
    """Q64 prediction metadata that may order reads but never alter the source route."""

    page_candidates: tuple[str, ...]
    confidence: float
    bytes: int


@dataclass(frozen=True)
class CompiledSelection:
    """Q64 selection record presented before one compiled schedule step may acquire pages."""

    observed_condition: str
    atom_id: str
    service_face: tuple[str, ...]
    certificate_digest: str
    description_digest: str
    execution_seed_or_exact_schedule: int | str
    bytes: int


@dataclass(frozen=True)
class PageExecution:
    """Q20 committed page-use record; failures publish no instance of this object."""

    mode: str
    step: int | None
    certificate_digest: str | None
    planned_pages: tuple[str, ...]
    sample_units: tuple[int, ...]
    execution_seed: int | None
    output_digest: str
    transitions: tuple[tuple[str, str, str], ...]


@dataclass(frozen=True)
class TransformerTrace:
    """Q63 observed F3 residency, traffic, and MLX allocation for one schedule instant."""

    phase: str
    schedule: ResidencyStep
    planned_pages: tuple[str, ...]
    operator_cases: tuple[str, ...]
    page_reads: int
    load_bytes: int
    model_tensor_bytes: int
    activation_bytes: int
    kv_reserved_bytes: int
    runtime_buffer_bytes: int
    model_memory_bytes: int
    metal_peak_bytes: int


@dataclass(frozen=True)
class TransformerExecution:
    """Q36 committed F3 logits and recurrent state; failures publish no instance."""

    page_execution: PageExecution
    logits: tuple[float, ...]
    logits_digest: str
    kv_digest: str
    kv_bytes: int
    trace: TransformerTrace


def _reject_evidence(object_id: str, label: str, detail: str) -> None:
    raise _error("INVALID_REQUEST", object_id, f"Q19: canonical {label}", detail)


def _record(value: object, fields: set[str], object_id: str, label: str) -> dict:
    if not isinstance(value, dict) or set(value) != fields:
        observed = sorted(value) if isinstance(value, dict) else type(value).__name__
        _reject_evidence(object_id, label, f"requires exactly {sorted(fields)}; received {observed}")
    return value


def _items(value: object, object_id: str, label: str, *, empty: bool = False) -> list:
    if (
        not isinstance(value, list)
        or len(value) > _MAX_ITEMS
        or (not empty and not value)
    ):
        _reject_evidence(object_id, label, "requires a bounded nonempty list")
    return value


def _u64(value: object, object_id: str, label: str) -> int:
    if type(value) is not int or not 0 <= value <= _MAX_U64:
        _reject_evidence(object_id, label, "requires an unsigned 64-bit integer")
    return value


def _fraction(value: object, object_id: str, label: str) -> Fraction:
    candidate = None
    if type(value) is int and value.bit_length() <= _MAX_EXACT_BITS:
        candidate = Fraction(value)
    elif type(value) is float and math.isfinite(value):
        candidate = Fraction(str(value))
    elif isinstance(value, str) and 0 < len(value) <= 128:
        try:
            exponent = value.lower().rpartition("e")
            if exponent[1] and abs(int(exponent[2])) > _MAX_EXACT_BITS:
                raise ValueError
            candidate = Fraction(value)
        except (OverflowError, ValueError, ZeroDivisionError):
            candidate = None
    if candidate is not None and max(
        candidate.numerator.bit_length(), candidate.denominator.bit_length()
    ) <= _MAX_EXACT_BITS:
        return candidate
    _reject_evidence(
        object_id,
        label,
        "requires a finite integer, number, or rational string within the bounded exact-scalar domain",
    )


def _identifier(value: object, object_id: str, label: str) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= 256:
        _reject_evidence(object_id, label, "requires a nonempty identifier of at most 256 characters")
    return value


def _scalar(value: object, field: str, object_id: str, label: str) -> tuple[Fraction, Fraction]:
    if field == "REAL":
        return (_fraction(value, object_id, label), Fraction(0))
    parts = value if isinstance(value, list) else None
    if parts is None or len(parts) != 2:
        _reject_evidence(object_id, label, "a COMPLEX scalar requires [real, imaginary]")
    return (_fraction(parts[0], object_id, label), _fraction(parts[1], object_id, label))


def _normal_scalar(value: tuple[Fraction, Fraction]) -> list[str]:
    return [str(value[0]), str(value[1])]


def _matrix(
    value: object,
    shape: tuple[int, int],
    field: str,
    object_id: str,
    label: str,
) -> tuple[tuple[tuple[Fraction, Fraction], ...], ...]:
    rows = _items(value, object_id, label)
    if len(rows) != shape[0] or any(not isinstance(row, list) or len(row) != shape[1] for row in rows):
        _reject_evidence(object_id, label, f"requires exact matrix shape {list(shape)}")
    return tuple(
        tuple(_scalar(item, field, object_id, f"{label}[{row_index}][{column_index}]")
              for column_index, item in enumerate(row))
        for row_index, row in enumerate(rows)
    )


def _normal_matrix(matrix: tuple[tuple[tuple[Fraction, Fraction], ...], ...]) -> list:
    return [[_normal_scalar(value) for value in row] for row in matrix]


def _normal_exact(value: object) -> object:
    """Replace exact rationals with canonical strings before hashing."""

    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {name: _normal_exact(item) for name, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normal_exact(item) for item in value]
    return value


def _add(left, right):
    return (left[0] + right[0], left[1] + right[1])


def _subtract(left, right):
    return (left[0] - right[0], left[1] - right[1])


def _multiply(left, right):
    return (left[0] * right[0] - left[1] * right[1], left[0] * right[1] + left[1] * right[0])


def _divide(left, right):
    denominator = right[0] * right[0] + right[1] * right[1]
    if denominator == 0:
        raise ZeroDivisionError
    return (
        (left[0] * right[0] + left[1] * right[1]) / denominator,
        (left[1] * right[0] - left[0] * right[1]) / denominator,
    )


def _conjugate(value):
    return (value[0], -value[1])


def _absolute_squared(value) -> Fraction:
    return value[0] * value[0] + value[1] * value[1]


def _sum_complex(values) -> tuple[Fraction, Fraction]:
    total = _ZERO
    for value in values:
        total = _add(total, value)
    return total


def _flatten(matrix):
    return tuple(value for row in matrix for value in row)


def _rank(matrix) -> int:
    rows = [list(row) for row in matrix]
    pivot_row = 0
    for column in range(len(rows[0])):
        pivot = next((index for index in range(pivot_row, len(rows)) if rows[index][column] != _ZERO), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        pivot_value = rows[pivot_row][column]
        rows[pivot_row] = [_divide(value, pivot_value) for value in rows[pivot_row]]
        for index in range(len(rows)):
            if index == pivot_row or rows[index][column] == _ZERO:
                continue
            factor = rows[index][column]
            rows[index] = [
                _subtract(value, _multiply(factor, pivot_value))
                for value, pivot_value in zip(rows[index], rows[pivot_row], strict=True)
            ]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return pivot_row


def _determinant(matrix) -> tuple[Fraction, Fraction]:
    rows = [list(row) for row in matrix]
    result = (Fraction(1), Fraction(0))
    sign = 1
    for column in range(len(rows)):
        pivot = next((index for index in range(column, len(rows)) if rows[index][column] != _ZERO), None)
        if pivot is None:
            return _ZERO
        if pivot != column:
            rows[column], rows[pivot] = rows[pivot], rows[column]
            sign *= -1
        pivot_value = rows[column][column]
        result = _multiply(result, pivot_value)
        for index in range(column + 1, len(rows)):
            if rows[index][column] == _ZERO:
                continue
            factor = _divide(rows[index][column], pivot_value)
            rows[index] = [
                _subtract(value, _multiply(factor, reference))
                for value, reference in zip(rows[index], rows[column], strict=True)
            ]
    return (-result[0], -result[1]) if sign < 0 else result


def _inner(left, metric, right) -> tuple[Fraction, Fraction]:
    applied = []
    for row in metric:
        total = _ZERO
        for coefficient, value in zip(row, right, strict=True):
            total = _add(total, _multiply(coefficient, value))
        applied.append(total)
    result = _ZERO
    for value, product in zip(left, applied, strict=True):
        result = _add(result, _multiply(_conjugate(value), product))
    return result


def _witness_loss(target, atom, metric, object_id: str) -> Fraction:
    target_norm = _inner(target, metric, target)
    atom_norm = _inner(atom, metric, atom)
    cross = _inner(atom, metric, target)
    if target_norm[1] != 0 or atom_norm[1] != 0 or atom_norm[0] <= 0:
        _reject_evidence(object_id, "condition metric", "quadratic forms must be positive real values")
    return target_norm[0] - _absolute_squared(cross) / atom_norm[0]


def _digest(value: object) -> str:
    return digest_bytes(canonical_bytes(value))


def _document_digest(value: dict, identity_field: str) -> str:
    return _digest({name: item for name, item in value.items() if name != identity_field})


def _expect_number(value: object, expected: Fraction, object_id: str, label: str) -> None:
    observed = _fraction(value, object_id, label)
    try:
        observed_number = float(observed)
        expected_number = float(expected)
    except OverflowError:
        observed_number = expected_number = math.inf
    if (
        not math.isfinite(observed_number)
        or not math.isfinite(expected_number)
        or (observed_number == 0.0 and observed != 0)
        or (expected_number == 0.0 and expected != 0)
    ):
        raise _error(
            "CAPABILITY_MISMATCH",
            object_id,
            f"Q19: {label}",
            "the certificate claim or canonical recomputation lies outside the finite certificate-number domain",
        )
    if observed_number != expected_number:
        raise _error(
            "CAPABILITY_MISMATCH",
            object_id,
            f"Q19: {label}",
            f"certificate reports {value}; canonical evidence recomputes {expected}",
        )


def _expect_exact(value: object, expected: Fraction, object_id: str, label: str) -> None:
    observed = _fraction(value, object_id, label)
    if observed != expected:
        raise _error(
            "CAPABILITY_MISMATCH",
            object_id,
            f"Q19: {label}",
            f"canonical evidence reports {value}; exact recomputation yields {expected}",
        )


def _expect(value: object, expected: object, object_id: str, label: str) -> None:
    if value != expected:
        raise _error(
            "CAPABILITY_MISMATCH",
            object_id,
            f"Q19: {label}",
            f"certificate reports {value!r}; canonical evidence recomputes {expected!r}",
        )


def _minimal_nonfaces(universe: frozenset[str], faces: set[frozenset[str]]) -> set[frozenset[str]]:
    maximal = {face for face in faces if not any(face < other for other in faces)}
    complements = [universe - face for face in maximal]
    candidates = {frozenset()}
    for edge in complements:
        if not edge:
            return set()
        expanded = set()
        for candidate in candidates:
            if candidate & edge:
                expanded.add(candidate)
            else:
                expanded.update(candidate | {condition} for condition in edge)
        candidates = {
            candidate
            for candidate in expanded
            if not any(other < candidate for other in expanded)
        }
    return candidates


def _coordinate(value: object, shape: tuple[int, int], object_id: str, label: str) -> tuple[int, int]:
    parts = _items(value, object_id, label)
    if len(parts) != 2:
        _reject_evidence(object_id, label, "requires one [row, column] coordinate")
    row = _u64(parts[0], object_id, f"{label} row")
    column = _u64(parts[1], object_id, f"{label} column")
    if row >= shape[0] or column >= shape[1]:
        _reject_evidence(object_id, label, "coordinate lies outside the target shape")
    return row, column


def _verify_cycle_nonface(
    proof: dict,
    target,
    metrics: dict[str, object],
    eta: Fraction,
    rank_budget: int,
    shape: tuple[int, int],
    field: str,
    object_id: str,
) -> frozenset[str]:
    """Verify one exact robust rank-one cycle obstruction without trusting the atom catalog."""

    row = _record(
        proof,
        {"ambient_delta", "condition_ids", "cycle", "kind", "nonface_id"},
        object_id,
        "minimal-nonface proof",
    )
    nonface_id = _identifier(row["nonface_id"], object_id, "minimal-nonface proof ID")
    if row["kind"] != "UNBALANCED_RANK_ONE_CYCLE" or rank_budget != 1:
        raise _error(
            "CAPABILITY_MISMATCH",
            nonface_id,
            "Q19: independently checkable minimal nonface",
            "S13 admits this proof only for a declared rank-one unbalanced cycle",
        )
    condition_ids = [
        _identifier(value, object_id, "nonface condition ID")
        for value in _items(row["condition_ids"], object_id, "nonface conditions")
    ]
    cycle = _items(row["cycle"], object_id, "nonface cycle")
    if (
        len(condition_ids) < 2
        or len(cycle) != len(condition_ids)
        or len(set(condition_ids)) != len(condition_ids)
    ):
        _reject_evidence(object_id, "minimal-nonface proof", "cycle conditions must be unique and aligned")
    delta = _fraction(row["ambient_delta"], object_id, "cycle ambient delta")
    if delta <= 0 or not 0 <= eta < 2:
        raise _error(
            "CAPABILITY_MISMATCH",
            nonface_id,
            "Q19: robust cycle threshold",
            "cycle proof requires positive ambient delta and representation tolerance below two",
        )

    edges = []
    for expected_condition, raw_edge in zip(condition_ids, cycle, strict=True):
        edge = _record(
            raw_edge,
            {"condition_id", "diagonal", "gain", "successor"},
            object_id,
            "cycle edge",
        )
        _expect(edge["condition_id"], expected_condition, object_id, "cycle condition order")
        diagonal = _coordinate(edge["diagonal"], shape, object_id, "cycle diagonal")
        successor = _coordinate(edge["successor"], shape, object_id, "cycle successor")
        if diagonal[1] != successor[1]:
            _reject_evidence(object_id, "cycle edge", "rank-one ratio coordinates must share one column")
        gain = _scalar(edge["gain"], field, object_id, "cycle gain")
        if _absolute_squared(gain) != 1:
            _reject_evidence(object_id, "cycle gain", "requires exact unit modulus")
        if target[diagonal[0]][diagonal[1]] != (Fraction(1), Fraction(0)) or target[successor[0]][successor[1]] != gain:
            raise _error(
                "CAPABILITY_MISMATCH",
                nonface_id,
                "Q19: cycle target witness",
                "canonical target coordinates do not realize the declared cycle gain",
            )
        metric = metrics.get(expected_condition)
        if metric is None:
            _reject_evidence(object_id, "cycle condition", "condition is absent from canonical metrics")
        selected = {
            diagonal[0] * shape[1] + diagonal[1],
            successor[0] * shape[1] + successor[1],
        }
        for left in range(len(metric)):
            for right in range(len(metric)):
                expected = (
                    (delta + (1 if left in selected else 0), Fraction(0))
                    if left == right
                    else _ZERO
                )
                if metric[left][right] != expected:
                    raise _error(
                        "CAPABILITY_MISMATCH",
                        nonface_id,
                        "Q19: cycle condition metric",
                        "condition metric is not the declared coordinate projector plus ambient delta",
                    )
        edges.append((diagonal, successor, gain))

    rows = [edge[0][0] for edge in edges]
    if len(set(rows)) != len(rows) or any(
        edges[index][1][0] != edges[(index + 1) % len(edges)][0][0]
        for index in range(len(edges))
    ):
        _reject_evidence(object_id, "minimal-nonface proof", "edge coordinates do not form one row cycle")
    row_index = {row_number: index for index, row_number in enumerate(rows)}
    linear = []
    cycle_gain = (Fraction(1), Fraction(0))
    for diagonal, successor, gain in edges:
        coefficients = [_ZERO for _ in rows]
        coefficients[row_index[diagonal[0]]] = (-gain[0], -gain[1])
        coefficients[row_index[successor[0]]] = (Fraction(1), Fraction(0))
        linear.append(coefficients)
        cycle_gain = _multiply(cycle_gain, gain)
    if cycle_gain == (Fraction(1), Fraction(0)):
        raise _error(
            "CAPABILITY_MISMATCH",
            nonface_id,
            "Q19: unbalanced cycle gain",
            "cycle gains multiply to one and provide no incompatibility witness",
        )
    gram = tuple(
        tuple(
            _sum_complex(
                _multiply(_conjugate(linear[k][left]), linear[k][right])
                for k in range(len(linear))
            )
            for right in range(len(rows))
        )
        for left in range(len(rows))
    )
    lower_bound = tuple(
        tuple(
            _subtract(value, (2 * eta, Fraction(0))) if left == right else value
            for right, value in enumerate(gram[left])
        )
        for left in range(len(rows))
    )
    for size in range(1, len(rows) + 1):
        determinant = _determinant(
            tuple(tuple(lower_bound[left][right] for right in range(size)) for left in range(size))
        )
        if determinant[1] != 0 or determinant[0] <= 0:
            raise _error(
                "CAPABILITY_MISMATCH",
                nonface_id,
                "Q19: robust cycle lower bound",
                "cycle Gram bound does not prove incompatibility at the declared tolerance",
            )
    return frozenset(condition_ids)


def _indexed(rows: list[dict], key: str, object_id: str, label: str) -> dict[str, dict]:
    result = {}
    for row in rows:
        identity = row.get(key) if isinstance(row, dict) else None
        if not isinstance(identity, str) or not 1 <= len(identity) <= 256 or identity in result:
            _reject_evidence(object_id, label, f"requires unique nonempty {key} values")
        result[identity] = row
    return result


def _compare_row(observed: dict, expected: dict, object_id: str, label: str) -> None:
    _expect(set(observed), set(expected), object_id, f"{label} fields")
    for name, value in expected.items():
        if isinstance(value, Fraction):
            _expect_number(observed[name], value, object_id, f"{label}.{name}")
        else:
            _expect(observed[name], value, object_id, f"{label}.{name}")


def _checked_sum(values: Sequence[int], object_id: str, label: str) -> int:
    total = sum(values)
    if total > _MAX_U64:
        _reject_evidence(object_id, label, "unsigned 64-bit byte arithmetic overflowed")
    return total


def admit_schedule(
    plan: object,
    certificate: object,
    evidence: object,
    profile: object,
) -> CertifiedSchedule:
    """Q19/Q47/Q63: recompute certificate truth, then admit one residency schedule."""

    validate_plan(plan, certificate)
    assert isinstance(plan, dict) and isinstance(certificate, dict)
    object_id = certificate["certificate_id"]
    source = _record(
        evidence,
        {
            "atoms",
            "conditions",
            "description_contract",
            "excluded_conditions",
            "execution_contract",
            "minimal_nonface_proofs",
            "observation_contract",
            "physical_conversion",
            "target",
            "trace_contract",
        },
        object_id,
        "certificate evidence",
    )
    if _document_digest(certificate, "certificate_id") != object_id:
        raise _error("CAPABILITY_MISMATCH", object_id, "Q19: immutable certificate identity", "certificate digest does not identify its canonical claims")
    if _document_digest(plan, "plan_id") != plan["plan_id"]:
        raise _error("CAPABILITY_MISMATCH", plan["plan_id"], "Q19: immutable plan identity", "plan digest does not identify its canonical claims")
    profile_record = _record(
        profile,
        {"activation_bytes", "cache_bytes", "context_bytes", "execution_bytes", "other_observed_bytes", "physical_bytes", "recommended_max_working_set_bytes", "runtime_buffer_bytes", "training_window_bytes"},
        plan["plan_id"],
        "memory profile",
    )
    memory = {
        name: _u64(value, plan["plan_id"], f"profile {name}")
        for name, value in profile_record.items()
    }
    _expect(plan["profile_digest"], _digest(profile_record), plan["plan_id"], "memory-profile digest")

    target_source = _record(
        source["target"],
        {"field", "flattening_order", "shape", "source_shape", "source_values"},
        object_id,
        "target evidence",
    )
    field = target_source["field"]
    if field not in {"REAL", "COMPLEX"}:
        _reject_evidence(object_id, "target field", "requires REAL or COMPLEX")
    source_shape = tuple(_u64(value, object_id, "source shape") for value in _items(target_source["source_shape"], object_id, "source shape"))
    if any(value == 0 for value in source_shape):
        _reject_evidence(object_id, "source shape", "dimensions must be positive")
    source_count = math.prod(source_shape)
    source_values = _items(target_source["source_values"], object_id, "source values")
    if source_count != len(source_values):
        _reject_evidence(object_id, "source values", "source shape does not match value count")
    target_shape_values = _items(target_source["shape"], object_id, "target shape")
    if len(target_shape_values) != 2:
        _reject_evidence(object_id, "target shape", "flattening requires two dimensions")
    target_shape = tuple(_u64(value, object_id, "target shape") for value in target_shape_values)
    if 0 in target_shape or math.prod(target_shape) != source_count:
        _reject_evidence(object_id, "target shape", "flattening must preserve every source scalar")
    order = _items(target_source["flattening_order"], object_id, "flattening order")
    if any(type(value) is not int for value in order) or sorted(order) != list(range(source_count)):
        _reject_evidence(object_id, "flattening order", "requires one exact permutation of source coordinates")
    flat_target = [_scalar(source_values[index], field, object_id, "source scalar") for index in order]
    target_matrix = tuple(
        tuple(flat_target[row * target_shape[1] : (row + 1) * target_shape[1]])
        for row in range(target_shape[0])
    )
    target_record = {
        "field": field,
        "shape": list(target_shape),
        "values": _normal_matrix(target_matrix),
    }
    flattening_record = {
        "source_shape": list(source_shape),
        "target_shape": list(target_shape),
        "order": order,
    }
    _expect(certificate["target"]["field"], field, object_id, "target field")
    _expect(certificate["target"]["shape"], list(target_shape), object_id, "target shape")
    _expect(certificate["target"]["target_digest"], _digest(target_record), object_id, "target digest")
    _expect(certificate["target"]["flattening_digest"], _digest(flattening_record), object_id, "flattening digest")

    vector_target = _flatten(target_matrix)
    dimension = len(vector_target)
    certificate_conditions = _indexed(certificate["condition_metrics"], "condition_id", object_id, "condition metrics")
    conditions = {}
    for raw in _items(source["conditions"], object_id, "condition evidence"):
        row = _record(raw, {"condition_id", "metric", "provenance"}, object_id, "condition evidence row")
        condition_id = _identifier(row["condition_id"], object_id, "condition ID")
        if condition_id in conditions:
            _reject_evidence(object_id, "condition evidence", "condition IDs must be unique nonempty strings")
        metric = _matrix(row["metric"], (dimension, dimension), field, object_id, f"metric {condition_id}")
        for left in range(dimension):
            for right in range(dimension):
                if metric[left][right] != _conjugate(metric[right][left]):
                    _reject_evidence(object_id, "condition metric", f"{condition_id} is not Hermitian")
        minors = []
        for size in range(1, dimension + 1):
            determinant = _determinant(tuple(tuple(metric[row][column] for column in range(size)) for row in range(size)))
            if determinant[1] != 0 or determinant[0] <= 0:
                _reject_evidence(object_id, "condition metric", f"{condition_id} is not positive definite")
            minors.append(_normal_scalar(determinant))
        claim = certificate_conditions.get(condition_id)
        if claim is None:
            _reject_evidence(object_id, "condition evidence", f"{condition_id} is absent from the certificate")
        _expect(claim["provenance_digest"], _digest(row["provenance"]), object_id, f"{condition_id} provenance digest")
        _expect(claim["metric_digest"], _digest(_normal_matrix(metric)), object_id, f"{condition_id} metric digest")
        _expect(claim["positive_definite_witness_digest"], _digest(minors), object_id, f"{condition_id} positive-definite witness")
        conditions[condition_id] = metric
    _expect(set(certificate_conditions), set(conditions), object_id, "condition catalog")
    universe = frozenset(conditions)
    eta = _fraction(certificate["compatibility"]["eta_rep"], object_id, "compatibility eta")
    rank_budget = certificate["compatibility"]["rank_budget"]

    certificate_atoms = _indexed(certificate["atoms"], "atom_id", object_id, "atom catalog")
    atoms = {}
    for raw in _items(source["atoms"], object_id, "atom evidence"):
        row = _record(raw, {"atom_id", "description", "matrix", "service_face_id"}, object_id, "atom evidence row")
        atom_id = _identifier(row["atom_id"], object_id, "atom ID")
        if atom_id in atoms:
            _reject_evidence(object_id, "atom evidence", "atom IDs must be unique nonempty strings")
        claim = certificate_atoms.get(atom_id)
        if claim is None:
            _reject_evidence(object_id, "atom evidence", f"{atom_id} is absent from the certificate")
        matrix = _matrix(row["matrix"], target_shape, field, object_id, f"atom {atom_id}")
        rank = _rank(matrix)
        if rank == 0 or rank > rank_budget:
            raise _error("CAPABILITY_MISMATCH", atom_id, "Q19: atom rank budget", f"recomputed rank {rank} exceeds declared budget {rank_budget}")
        _expect(claim["rank"], rank, atom_id, "atom rank")
        _expect(claim["witness_digest"], _digest(_normal_matrix(matrix)), atom_id, "atom witness digest")
        losses = {condition_id: _witness_loss(vector_target, _flatten(matrix), metric, atom_id) for condition_id, metric in conditions.items()}
        claimed_losses = _indexed(claim["witness_losses"], "condition_id", atom_id, "witness losses")
        _expect(set(claimed_losses), set(losses), atom_id, "witness-loss conditions")
        for condition_id, loss in losses.items():
            _expect_number(claimed_losses[condition_id]["loss"], loss, atom_id, f"witness loss {condition_id}")
        face = frozenset(condition_id for condition_id, loss in losses.items() if loss <= eta)
        if not face:
            raise _error("CAPABILITY_MISMATCH", atom_id, "Q19: atom service face", "recomputed atom serves no declared condition")
        _expect(claim["service_face_id"], row["service_face_id"], atom_id, "service-face identity")

        description = _record(
            row["description"],
            {"class", "description_bytes", "estimator", "estimator_calibration", "metadata_bytes", "reconstruction", "sampling_law_id"},
            atom_id,
            "description evidence",
        )
        reconstruction = _matrix(description["reconstruction"], target_shape, field, atom_id, "description reconstruction")
        residual = tuple(
            tuple(_subtract(value, reconstructed) for value, reconstructed in zip(atom_row, reconstruction_row, strict=True))
            for atom_row, reconstruction_row in zip(matrix, reconstruction, strict=True)
        )
        distortion = sum((_absolute_squared(value) for value in _flatten(residual)), Fraction(0))
        atom_norm_squared = sum(
            (_absolute_squared(value) for value in _flatten(matrix)), Fraction(0)
        )
        declared_description = claim["description"]
        _expect(declared_description["class"], description["class"], atom_id, "description class")
        _expect_number(declared_description["distortion_bound"], distortion, atom_id, "description distortion")
        _expect(declared_description["reconstruction_digest"], _digest(_normal_matrix(reconstruction)), atom_id, "reconstruction digest")
        _expect(declared_description["residual_relation_digest"], _digest(_normal_matrix(residual)), atom_id, "residual relation digest")
        _expect(declared_description["estimator_digest"], _digest(description["estimator"]), atom_id, "estimator digest")
        _expect(declared_description["estimator_calibration_digest"], _digest(description["estimator_calibration"]), atom_id, "estimator calibration digest")
        _expect(declared_description["sampling_law_id"], description["sampling_law_id"], atom_id, "description sampling law")
        if description["class"] == "EXACT" and distortion != 0:
            raise _error("CAPABILITY_MISMATCH", atom_id, "Q19: exact description", "EXACT reconstruction has a nonzero residual")
        estimator = _record(description["estimator"], {"kind"}, atom_id, "residual estimator")
        calibration = _record(
            description["estimator_calibration"],
            {"atom_norm_squared", "distortion"},
            atom_id,
            "estimator calibration",
        )
        expected_estimator = "NONE" if distortion == 0 else "FRESH_RESIDUAL_COLUMN_AVERAGE"
        _expect(estimator["kind"], expected_estimator, atom_id, "residual estimator kind")
        _expect_exact(calibration["distortion"], distortion, atom_id, "calibrated distortion")
        _expect_exact(
            calibration["atom_norm_squared"],
            atom_norm_squared,
            atom_id,
            "calibrated atom norm",
        )
        atoms[atom_id] = {
            "description_bytes": _u64(description["description_bytes"], atom_id, "description bytes"),
            "distortion": distortion,
            "face": face,
            "face_id": row["service_face_id"],
            "matrix": matrix,
            "metadata_bytes": _u64(description["metadata_bytes"], atom_id, "metadata bytes"),
            "norm_squared": atom_norm_squared,
            "rank": rank,
            "residual_column_norms": tuple(
                sum(
                    (_absolute_squared(residual[row][column]) for row in range(target_shape[0])),
                    Fraction(0),
                )
                for column in range(target_shape[1])
            ),
            "sampling_law_id": description["sampling_law_id"],
        }
    _expect(set(certificate_atoms), set(atoms), object_id, "atom catalog")

    service_faces = _indexed(certificate["compatibility"]["service_faces"], "face_id", object_id, "service faces")
    _expect(set(service_faces), {atom["face_id"] for atom in atoms.values()}, object_id, "service-face catalog")
    for atom_id, atom in atoms.items():
        claimed = service_faces[atom["face_id"]]["condition_ids"]
        if len(claimed) != len(set(claimed)):
            _reject_evidence(object_id, "service face", f"{atom['face_id']} repeats a condition")
        _expect(frozenset(claimed), atom["face"], atom_id, "recomputed service face")

    faces = {atom["face"] for atom in atoms.values()}
    expected_nonfaces = _minimal_nonfaces(universe, faces)
    declared_nonfaces = certificate["compatibility"]["minimal_nonfaces"]
    observed_nonfaces = {}
    nonface_claims = {}
    for row in declared_nonfaces:
        conditions_in_row = row["condition_ids"]
        key = frozenset(conditions_in_row)
        if len(key) != len(conditions_in_row) or key in observed_nonfaces:
            _reject_evidence(object_id, "minimal nonfaces", "condition sets must be unique and duplicate-free")
        observed_nonfaces[key] = row["nonface_id"]
        nonface_claims[key] = row
    _expect(set(observed_nonfaces), expected_nonfaces, object_id, "complete minimal-nonface family")
    proof_rows = _items(
        source["minimal_nonface_proofs"],
        object_id,
        "minimal-nonface proofs",
        empty=True,
    )
    proved_nonfaces = {}
    for proof in proof_rows:
        key = _verify_cycle_nonface(
            proof,
            target_matrix,
            conditions,
            eta,
            rank_budget,
            target_shape,
            field,
            object_id,
        )
        if key in proved_nonfaces:
            _reject_evidence(object_id, "minimal-nonface proofs", "one condition set has duplicate proofs")
        claim = nonface_claims.get(key)
        if claim is None or claim["nonface_id"] != proof["nonface_id"]:
            raise _error(
                "CAPABILITY_MISMATCH",
                proof["nonface_id"],
                "Q19: minimal-nonface proof identity",
                "proof does not identify one declared minimal nonface",
            )
        _expect(
            claim["witness_digest"],
            _digest(proof),
            object_id,
            f"minimal nonface {claim['nonface_id']} witness",
        )
        proved_nonfaces[key] = proof["nonface_id"]
    _expect(set(proved_nonfaces), expected_nonfaces, object_id, "proved minimal-nonface family")

    cover = certificate["compatibility"]["cover"]
    if len(cover) != len(universe) or len({row["condition_id"] for row in cover}) != len(cover):
        raise _error("CAPABILITY_MISMATCH", object_id, "Q19: atom cover", "cover must assign every condition exactly once")
    for row in cover:
        atom = atoms.get(row["atom_id"])
        if row["condition_id"] not in universe or atom is None or row["condition_id"] not in atom["face"]:
            raise _error("CAPABILITY_MISMATCH", object_id, "Q19: atom cover", f"invalid cover entry {row!r}")

    excluded_claims = certificate["compatibility"]["excluded_conditions"]
    excluded_evidence = _items(source["excluded_conditions"], object_id, "excluded-condition evidence", empty=True)
    expected_exclusions = []
    for raw in excluded_evidence:
        row = _record(raw, {"cause", "condition_id", "evidence"}, object_id, "excluded-condition row")
        if row["condition_id"] in universe:
            _reject_evidence(object_id, "excluded conditions", "a covered condition cannot also be excluded")
        expected_exclusions.append({"condition_id": row["condition_id"], "cause": row["cause"], "evidence_digest": _digest(row["evidence"])})
    _expect(excluded_claims, expected_exclusions, object_id, "causal exclusions")

    description_contract = _record(
        source["description_contract"],
        {"description_family", "distortion_metric", "estimator_family", "residual_family"},
        object_id,
        "description contract",
    )
    expected_description_contract = {
        "description_family": {"kind": "DECLARED_RECONSTRUCTION"},
        "distortion_metric": {"kind": "FROBENIUS_SQUARED"},
        "estimator_family": {"kind": "RESIDUAL_COLUMN_OR_EXACT"},
        "residual_family": {"relation": "ATOM_MINUS_RECONSTRUCTION"},
    }
    _expect(
        description_contract,
        expected_description_contract,
        object_id,
        "description and residual contract",
    )
    for claim_name, evidence_name in (
        ("description_family_digest", "description_family"),
        ("distortion_metric_digest", "distortion_metric"),
        ("estimator_family_digest", "estimator_family"),
        ("residual_family_digest", "residual_family"),
    ):
        _expect(certificate["description_contract"][claim_name], _digest(description_contract[evidence_name]), object_id, claim_name)

    observation = _record(
        source["observation_contract"],
        {"confidence", "experiment", "kind", "loss_family", "off_support", "sample_count", "selector", "support"},
        object_id,
        "observation contract",
    )
    support = _items(observation["support"], object_id, "observation support")
    if any(not isinstance(condition_id, str) for condition_id in support) or len(support) != len(set(support)):
        _reject_evidence(object_id, "observation support", "condition IDs must be strings and may not repeat")
    _expect(frozenset(support), universe, object_id, "observation protected support")
    _expect(observation["selector"], cover, object_id, "observation selector and atom cover")
    observation_claim = certificate["observation_contract"]
    for name in ("kind", "off_support", "sample_count"):
        _expect(observation_claim[name], observation[name], object_id, f"observation {name}")
    _expect_number(observation_claim["confidence"], _fraction(observation["confidence"], object_id, "observation confidence"), object_id, "observation confidence")
    for claim_name, evidence_name in (
        ("experiment_digest", "experiment"),
        ("support_digest", "support"),
        ("selector_digest", "selector"),
        ("loss_family_digest", "loss_family"),
    ):
        _expect(observation_claim[claim_name], _digest(observation[evidence_name]), object_id, claim_name)
    if observation["off_support"] != "REJECT" or (observation["kind"] == "PROTECTED_TEST_LAW" and observation["sample_count"] == 0):
        raise _error("CAPABILITY_MISMATCH", object_id, "Q19: observation adequacy", "protected test laws require samples and every off-support observation must reject")

    execution = _record(
        source["execution_contract"],
        {"operations", "risk_composition", "sampling_laws"},
        object_id,
        "execution contract",
    )
    sampling_claims = _indexed(certificate["execution_contract"]["sampling_laws"], "sampling_law_id", object_id, "sampling laws")
    sampling_laws = {}
    for raw in _items(execution["sampling_laws"], object_id, "sampling-law evidence"):
        row = _record(raw, {"kind", "law", "sampling_law_id", "seed_policy", "work_unit"}, object_id, "sampling-law row")
        law_id = _identifier(row["sampling_law_id"], object_id, "sampling-law ID")
        claim = sampling_claims.get(law_id)
        if claim is None or law_id in sampling_laws:
            _reject_evidence(object_id, "sampling laws", "sampling-law IDs must match uniquely")
        for name in ("kind", "seed_policy", "work_unit"):
            _expect(claim[name], row[name], object_id, f"sampling law {law_id} {name}")
        _expect(claim["law_digest"], _digest(row["law"]), object_id, f"sampling law {law_id} digest")
        if (row["kind"] == "EXACT") != (row["seed_policy"] == "NONE"):
            raise _error("CAPABILITY_MISMATCH", law_id, "Q19: sampling coin contract", "EXACT requires NONE; FRESH_RANDOM requires RECORDED_COUNTER_KEY")
        assigned_atoms = [
            atom_id for atom_id, atom in atoms.items() if atom["sampling_law_id"] == law_id
        ]
        if not assigned_atoms:
            _reject_evidence(law_id, "sampling law", "every law must serve at least one atom")
        if row["kind"] == "EXACT":
            expected_law = {"family": "NO_RESIDUAL", "atom_ids": assigned_atoms}
            if any(atoms[atom_id]["distortion"] for atom_id in assigned_atoms):
                raise _error("CAPABILITY_MISMATCH", law_id, "Q19: exact sampling law", "NO_RESIDUAL law names an atom with nonzero distortion")
        else:
            if row["work_unit"] != "COLUMNS":
                raise _error("CAPABILITY_MISMATCH", law_id, "Q19: fresh residual work unit", "residual sampling requires COLUMNS")
            distributions = []
            for atom_id in assigned_atoms:
                distortion = atoms[atom_id]["distortion"]
                if distortion <= 0:
                    raise _error("CAPABILITY_MISMATCH", law_id, "Q19: fresh residual sampling law", "fresh sampling names an atom without a residual")
                distributions.append({
                    "atom_id": atom_id,
                    "columns": [
                        {"column": column, "probability": str(column_norm / distortion)}
                        for column, column_norm in enumerate(atoms[atom_id]["residual_column_norms"])
                        if column_norm > 0
                    ],
                })
            expected_law = {
                "family": "FROBENIUS_RESIDUAL_COLUMNS",
                "adversary": "FIXED_QUERY_BEFORE_PRIVATE_COINS",
                "coins": "FRESH_INDEPENDENT",
                "atom_distributions": distributions,
            }
        _expect(row["law"], expected_law, law_id, "recomputed sampling law")
        sampling_laws[law_id] = row
    _expect(set(sampling_claims), set(sampling_laws), object_id, "sampling-law catalog")

    operation_claims = _indexed(certificate["execution_contract"]["operations"], "operation_id", object_id, "operations")
    operations = {}
    for raw in _items(execution["operations"], object_id, "operation evidence"):
        row = _record(raw, {"loss_propagation", "operation_id", "operator_case_id", "rank_accounting", "sampling_law_id"}, object_id, "operation row")
        operation_id = _identifier(row["operation_id"], object_id, "operation ID")
        claim = operation_claims.get(operation_id)
        if claim is None or operation_id in operations:
            _reject_evidence(object_id, "operations", "operation IDs must match uniquely")
        _expect(claim["operator_case_id"], row["operator_case_id"], operation_id, "operator case")
        _expect(claim["sampling_law_id"], row["sampling_law_id"], operation_id, "operation sampling law")
        _expect(claim["rank_accounting_digest"], _digest(row["rank_accounting"]), operation_id, "rank-accounting map")
        _expect(claim["loss_propagation_digest"], _digest(row["loss_propagation"]), operation_id, "loss-propagation map")
        rank_map = _record(row["rank_accounting"], {"kind", "maximum_rank"}, operation_id, "rank-accounting map")
        if rank_map["kind"] != "ATOM_BOUND":
            _reject_evidence(operation_id, "rank-accounting map", "S13 supports the declared ATOM_BOUND proof")
        maximum_rank = _u64(rank_map["maximum_rank"], operation_id, "operation rank bound")
        loss_map = _record(row["loss_propagation"], {"coefficient", "remainder_bound"}, operation_id, "loss-propagation map")
        coefficient = _fraction(loss_map["coefficient"], operation_id, "loss coefficient")
        remainder = _fraction(loss_map["remainder_bound"], operation_id, "remainder bound")
        if coefficient < 0 or remainder < 0:
            _reject_evidence(operation_id, "loss-propagation map", "coefficient and remainder must be nonnegative")
        _expect_number(claim["remainder_bound"], remainder, operation_id, "operation remainder bound")
        operations[operation_id] = {
            "coefficient": coefficient,
            "delta": _fraction(claim["delta_exec"], operation_id, "operation delta"),
            "epsilon": _fraction(claim["epsilon_exec"], operation_id, "operation epsilon"),
            "maximum_rank": maximum_rank,
            "remainder": remainder,
            "sampling_law_id": row["sampling_law_id"],
        }
    _expect(set(operation_claims), set(operations), object_id, "operation catalog")
    risk = _record(execution["risk_composition"], {"kind", "proof"}, object_id, "risk composition")
    _expect(certificate["execution_contract"]["risk_composition_kind"], risk["kind"], object_id, "risk composition kind")
    _expect(certificate["execution_contract"]["risk_composition_digest"], _digest(risk), object_id, "risk composition digest")

    trace = _record(
        source["trace_contract"],
        {"fresh_traffic_unit", "prefix_policy", "protected_trace_family", "steps"},
        object_id,
        "trace contract",
    )
    raw_steps = _items(trace["steps"], object_id, "trace steps")
    expected_trace = []
    for index, raw in enumerate(raw_steps):
        row = _record(raw, {"atom_id", "fresh_samples", "fresh_traffic", "operation_id", "step"}, object_id, "trace step")
        if row["step"] != index:
            _reject_evidence(object_id, "trace step", "steps must be contiguous from zero")
        operation_id = _identifier(row["operation_id"], object_id, "trace operation ID")
        atom_id = _identifier(row["atom_id"], object_id, "trace atom ID")
        operation = operations.get(operation_id)
        atom = atoms.get(atom_id)
        if operation is None or atom is None:
            _reject_evidence(object_id, "trace step", "operation and atom must exist in the canonical catalogs")
        if operation["sampling_law_id"] != atom["sampling_law_id"] or atom["sampling_law_id"] not in sampling_laws:
            raise _error("CAPABILITY_MISMATCH", object_id, "Q19: trace sampling relation", "trace atom, operation, and sampling law disagree")
        if atom["rank"] > operation["maximum_rank"]:
            raise _error("CAPABILITY_MISMATCH", row["operation_id"], "Q19: operation rank-accounting map", "trace atom exceeds the operation rank bound")
        samples = _u64(row["fresh_samples"], object_id, "fresh samples")
        traffic = _u64(row["fresh_traffic"], object_id, "fresh traffic")
        law = sampling_laws[atom["sampling_law_id"]]
        epsilon = operation["epsilon"]
        delta = operation["delta"]
        if law["kind"] == "EXACT":
            if samples or traffic or atom["distortion"] or epsilon or delta:
                raise _error("CAPABILITY_MISMATCH", row["atom_id"], "Q19: exact execution bound", "EXACT execution requires zero residual, samples, traffic, error, and risk")
        else:
            if samples == 0 or epsilon <= 0 or not 0 < delta < 1:
                raise _error("CAPABILITY_MISMATCH", row["atom_id"], "Q19: fresh residual execution bound", "fresh execution requires positive samples/error and risk strictly between zero and one")
            expected_traffic = target_shape[0] * samples
            if expected_traffic > _MAX_U64:
                _reject_evidence(object_id, "fresh residual traffic", "unsigned 64-bit traffic arithmetic overflowed")
            if trace["fresh_traffic_unit"] != "SCALARS" or traffic != expected_traffic:
                raise _error(
                    "CAPABILITY_MISMATCH",
                    row["atom_id"],
                    "Q19: fresh residual traffic",
                    f"{samples} column samples require exactly {expected_traffic} scalar reads",
                )
            mean_bound = epsilon * epsilon * atom["norm_squared"] * samples
            risk_bound = delta * mean_bound
            if atom["distortion"] > mean_bound or atom["distortion"] > risk_bound:
                raise _error("CAPABILITY_MISMATCH", row["atom_id"], "Q19: fresh residual execution bound", "declared samples, epsilon, and delta do not satisfy the recomputed sufficient bound")
        expected_trace.append({
            "step": index,
            "operation_id": operation_id,
            "atom_id": atom_id,
            "description_bytes_resident": atom["description_bytes"],
            "metadata_bytes_resident": atom["metadata_bytes"],
            "fresh_samples": samples,
            "fresh_traffic": traffic,
            "epsilon_exec": epsilon,
            "delta_exec": delta,
        })

    trace_claim = certificate["trace_contract"]
    _expect(trace_claim["prefix_policy"], trace["prefix_policy"], object_id, "trace prefix policy")
    _expect(trace_claim["protected_trace_family_digest"], _digest(trace["protected_trace_family"]), object_id, "protected trace family")
    schedule_record = _normal_exact(
        {"prefix_policy": trace["prefix_policy"], "steps": expected_trace}
    )
    _expect(trace_claim["schedule_digest"], _digest(schedule_record), object_id, "certified schedule digest")
    _expect(trace_claim["horizon"], len(expected_trace), object_id, "trace horizon")

    trace_rows = certificate["resource_tables"]["per_trace_step"]
    _expect(len(trace_rows), len(expected_trace), object_id, "per-trace-step table length")
    for observed, expected in zip(trace_rows, expected_trace, strict=True):
        _compare_row(observed, expected, object_id, f"trace step {expected['step']}")

    expected_atom_rows = []
    for atom_id, atom in atoms.items():
        selected = [row for row in expected_trace if row["atom_id"] == atom_id]
        if not selected:
            raise _error("CAPABILITY_MISMATCH", atom_id, "Q19: protected trace coverage", "every certified atom requires one protected trace use")
        expected_atom_rows.append({
            "atom_id": atom_id,
            "description_bytes": atom["description_bytes"],
            "metadata_bytes": atom["metadata_bytes"],
            "fresh_samples_max": max(row["fresh_samples"] for row in selected),
            "fresh_samples_total": sum(row["fresh_samples"] for row in selected),
            "fresh_traffic_max": max(row["fresh_traffic"] for row in selected),
            "fresh_traffic_total": sum(row["fresh_traffic"] for row in selected),
            "epsilon_exec": max(row["epsilon_exec"] for row in selected),
            "delta_exec": max(row["delta_exec"] for row in selected),
        })
    atom_rows = _indexed(certificate["resource_tables"]["per_atom"], "atom_id", object_id, "per-atom resources")
    _expect(set(atom_rows), set(atoms), object_id, "per-atom resource catalog")
    for expected in expected_atom_rows:
        _compare_row(atom_rows[expected["atom_id"]], expected, object_id, f"atom resource {expected['atom_id']}")

    expected_operation_rows = []
    for operation_id, operation in operations.items():
        selected = [row for row in expected_trace if row["operation_id"] == operation_id]
        if not selected:
            raise _error("CAPABILITY_MISMATCH", operation_id, "Q19: protected trace coverage", "every certified operation requires one protected trace use")
        selected_atoms = {row["atom_id"] for row in selected}
        expected_operation_rows.append({
            "operation_id": operation_id,
            "description_bytes_peak": max(atoms[atom_id]["description_bytes"] for atom_id in selected_atoms),
            "description_bytes_total": sum(atoms[atom_id]["description_bytes"] for atom_id in selected_atoms),
            "metadata_bytes_peak": max(atoms[atom_id]["metadata_bytes"] for atom_id in selected_atoms),
            "metadata_bytes_total": sum(atoms[atom_id]["metadata_bytes"] for atom_id in selected_atoms),
            "fresh_samples_max": max(row["fresh_samples"] for row in selected),
            "fresh_samples_total": sum(row["fresh_samples"] for row in selected),
            "fresh_traffic_max": max(row["fresh_traffic"] for row in selected),
            "fresh_traffic_total": sum(row["fresh_traffic"] for row in selected),
            "epsilon_exec": operation["epsilon"],
            "delta_exec": operation["delta"],
        })
    operation_rows = _indexed(certificate["resource_tables"]["per_operation"], "operation_id", object_id, "per-operation resources")
    _expect(set(operation_rows), set(operations), object_id, "per-operation resource catalog")
    for expected in expected_operation_rows:
        _compare_row(operation_rows[expected["operation_id"]], expected, object_id, f"operation resource {expected['operation_id']}")

    trace_deltas = [row["delta_exec"] for row in expected_trace]
    if risk["kind"] == "DETERMINISTIC":
        if any(trace_deltas):
            raise _error("CAPABILITY_MISMATCH", object_id, "Q19: deterministic risk composition", "deterministic composition contains nonzero step risk")
        total_delta = Fraction(0)
    elif risk["kind"] == "UNION_BOUND":
        total_delta = sum(trace_deltas, Fraction(0))
    elif risk["kind"] == "INDEPENDENT_PRODUCT":
        survival = Fraction(1)
        for delta in trace_deltas:
            survival *= 1 - delta
        total_delta = 1 - survival
    elif risk["kind"] == "DECLARED_DEPENDENCE":
        proof = _record(risk["proof"], {"total_bound"}, object_id, "declared-dependence proof")
        total_delta = _fraction(proof["total_bound"], object_id, "declared-dependence total")
        if total_delta < max(trace_deltas) or total_delta > sum(trace_deltas, Fraction(0)):
            raise _error("CAPABILITY_MISMATCH", object_id, "Q19: declared-dependence risk composition", "declared bound must lie between the largest event and the union bound")
    else:
        _reject_evidence(object_id, "risk composition", "unknown generated risk-composition kind")
    if total_delta > 1:
        raise _error("CAPABILITY_MISMATCH", object_id, "Q19: composed execution risk", "composed risk exceeds one")
    total_epsilon = sum(
        operations[row["operation_id"]]["coefficient"] * row["epsilon_exec"]
        + operations[row["operation_id"]]["remainder"]
        for row in expected_trace
    )
    expected_resources = {
        "eta_rep": eta,
        "epsilon_exec": total_epsilon,
        "delta_exec_total": total_delta,
        "atom_count": len(atoms),
        "max_atom_rank": max(atom["rank"] for atom in atoms.values()),
        "description_bytes_peak": max(row["description_bytes_resident"] for row in expected_trace),
        "description_bytes_total": _checked_sum([atom["description_bytes"] for atom in atoms.values()], object_id, "description total"),
        "metadata_bytes_peak": max(row["metadata_bytes_resident"] for row in expected_trace),
        "metadata_bytes_total": _checked_sum([atom["metadata_bytes"] for atom in atoms.values()], object_id, "metadata total"),
        "fresh_samples_max": max(row["fresh_samples"] for row in expected_trace),
        "fresh_samples_total": _checked_sum([row["fresh_samples"] for row in expected_trace], object_id, "fresh sample total"),
        "fresh_traffic_max": max(row["fresh_traffic"] for row in expected_trace),
        "fresh_traffic_total": _checked_sum([row["fresh_traffic"] for row in expected_trace], object_id, "fresh traffic total"),
        "fresh_traffic_unit": trace["fresh_traffic_unit"],
        "horizon": len(expected_trace),
    }
    _compare_row(certificate["resources"], expected_resources, object_id, "aggregate resources")
    for name, expected in expected_resources.items():
        limit = plan["resource_limits"][name]
        if name == "fresh_traffic_unit":
            _expect(limit, expected, plan["plan_id"], "plan fresh-traffic unit")
        elif isinstance(expected, Fraction):
            if _fraction(limit, plan["plan_id"], f"plan limit {name}") < expected:
                raise _error("CAPABILITY_MISMATCH", plan["plan_id"], "Q19/Q47: plan resource limit", f"{name} limit is beneath certified demand")
        elif limit < expected:
            raise _error("CAPABILITY_MISMATCH", plan["plan_id"], "Q19/Q47: plan resource limit", f"{name} limit is beneath certified demand")

    physical = _record(source["physical_conversion"], {"conversion_rows"}, object_id, "physical conversion")
    conversion_rows = _items(physical["conversion_rows"], object_id, "physical conversion rows")
    _expect(certificate["physical_conversion"]["conversion_rows"], conversion_rows, object_id, "physical conversion rows")
    _expect(certificate["physical_conversion"]["conversion_digest"], _digest(conversion_rows), object_id, "physical conversion digest")
    conversions = _indexed(conversion_rows, "operation_id", object_id, "physical conversion rows")
    _expect(set(conversions), set(operations), object_id, "physical conversion operation catalog")
    for expected in expected_operation_rows:
        conversion = conversions[expected["operation_id"]]
        operation = operations[expected["operation_id"]]
        sampling_law = sampling_laws[operation["sampling_law_id"]]
        minimum_memory = expected["description_bytes_peak"] + expected["metadata_bytes_peak"]
        if (
            conversion["probe_unit"] != sampling_law["work_unit"]
            or conversion["probes"] != expected["fresh_samples_max"]
        ):
            raise _error(
                "CAPABILITY_MISMATCH",
                expected["operation_id"],
                "Q19: physical probe conversion",
                "physical probe unit and count must equal the certified sampling demand",
            )
        if conversion["memory_bytes_peak"] < minimum_memory or conversion["bytes"] < expected["fresh_traffic_max"]:
            raise _error("CAPABILITY_MISMATCH", expected["operation_id"], "Q19: physical resource conversion", "physical row understates certified memory or fresh traffic")
        if conversion["probes"] and not all(
            conversion[name] > 0 for name in ("bytes", "latency_ns_peak", "page_reads")
        ):
            raise _error(
                "CAPABILITY_MISMATCH",
                expected["operation_id"],
                "Q19: physical resource conversion",
                "a nonzero probe demand requires nonzero bytes, page reads, and latency",
            )

    if memory["recommended_max_working_set_bytes"] > memory["physical_bytes"]:
        _reject_evidence(plan["plan_id"], "memory profile", "recommended working set cannot exceed physical memory")
    reserve = max(4 * _GIB, (memory["physical_bytes"] + 3) // 4)
    physical_ceiling = memory["physical_bytes"] - reserve if memory["physical_bytes"] >= reserve else 0
    recommended_ceiling = 9 * memory["recommended_max_working_set_bytes"] // 10
    ceiling = min(physical_ceiling, recommended_ceiling)
    unavailable = _checked_sum([memory["execution_bytes"], memory["other_observed_bytes"]], plan["plan_id"], "unavailable memory")
    available = ceiling - unavailable if ceiling >= unavailable else 0
    fixed = _checked_sum(
        [
            memory["cache_bytes"],
            memory["context_bytes"],
            memory["activation_bytes"],
            memory["runtime_buffer_bytes"],
            memory["training_window_bytes"],
        ],
        plan["plan_id"],
        "fixed live memory",
    )
    schedule_steps = []
    for row in expected_trace:
        conversion = conversions[row["operation_id"]]
        dynamic = conversion["memory_bytes_peak"]
        live = _checked_sum([fixed, dynamic], plan["plan_id"], f"step {row['step']} live memory")
        schedule_steps.append(ResidencyStep(
            step=row["step"],
            operation_id=row["operation_id"],
            atom_id=row["atom_id"],
            description_bytes=row["description_bytes_resident"],
            metadata_bytes=row["metadata_bytes_resident"],
            fresh_samples=row["fresh_samples"],
            fresh_traffic=row["fresh_traffic"],
            page_reads=conversion["page_reads"],
            load_bytes=conversion["bytes"],
            dynamic_memory_bytes=dynamic,
            live_memory_bytes=live,
        ))
    peak_live = max(step.live_memory_bytes for step in schedule_steps)
    if peak_live > available:
        raise _error(
            "MEMORY_BUDGET_EXCEEDED",
            plan["plan_id"],
            "Q47: conservative unified-memory admission",
            f"certified peak {peak_live} exceeds available budget {available}",
        )
    return CertifiedSchedule(
        plan_id=plan["plan_id"],
        certificate_id=object_id,
        profile_digest=plan["profile_digest"],
        reserve_bytes=reserve,
        memory_ceiling_bytes=ceiling,
        available_bytes=available,
        peak_live_bytes=peak_live,
        steps=tuple(schedule_steps),
    )


def _mlx_runtime():
    """Import the Apple-only runtime only when a generated numerical case executes."""

    global _MLX
    if _MLX is None:
        import mlx.core as mx
        import mlx.optimizers as optim

        _MLX = (mx, optim)
    return _MLX


def _require_runtime(case_id: str, mx) -> None:
    required = MLX_RUNTIME["package"].split("==", 1)[1]
    observed = importlib.metadata.version("mlx")
    if observed != required:
        raise _error(
            "CAPABILITY_MISMATCH",
            case_id,
            "Q30: pinned MLX release",
            f"requires MLX {required}; found {observed}",
        )
    if platform.system() != "Darwin" or platform.machine() != "arm64" or not mx.metal.is_available():
        raise _error(
            "CAPABILITY_MISMATCH",
            case_id,
            "Q30: Apple Silicon Metal feature set",
            "dispatch requires arm64 macOS with MLX Metal available",
        )


def _matmul(values: Sequence[object], _: dict) -> object:
    mx, _ = _mlx_runtime()
    return mx.matmul(values[0], values[1])


def _quantized_matmul(values: Sequence[object], parameters: dict) -> object:
    mx, _ = _mlx_runtime()
    return mx.quantized_matmul(values[0], values[1], values[2], values[3], **parameters)


def _norm(values: Sequence[object], parameters: dict) -> object:
    mx, _ = _mlx_runtime()
    return mx.fast.rms_norm(values[0], values[1], parameters["eps"])


def _rope(values: Sequence[object], parameters: dict) -> object:
    mx, _ = _mlx_runtime()
    return mx.fast.rope(values[0], **parameters)


def _attention(values: Sequence[object], parameters: dict) -> object:
    mx, _ = _mlx_runtime()
    return mx.fast.scaled_dot_product_attention(values[0], values[1], values[2], **parameters)


def _convolution(values: Sequence[object], parameters: dict) -> object:
    mx, _ = _mlx_runtime()
    return mx.conv1d(values[0], values[1], **parameters)


def _embedding(values: Sequence[object], parameters: dict) -> object:
    mx, _ = _mlx_runtime()
    return mx.take(values[0], values[1], **parameters)


def _sampling(values: Sequence[object], parameters: dict) -> object:
    mx, _ = _mlx_runtime()
    return mx.random.categorical(values[0], key=values[1], **parameters)


def _autograd(values: Sequence[object], _: dict) -> object:
    mx, _ = _mlx_runtime()
    return mx.grad(mx.sum)(values[0])


def _optimizer(values: Sequence[object], parameters: dict) -> object:
    _, optim = _mlx_runtime()
    optimizer = optim.SGD(**parameters)
    gradients = {"parameter": values[1]}
    model_parameters = {"parameter": values[0]}
    return optimizer.apply_gradients(gradients, model_parameters)["parameter"]


_EXECUTORS = {
    "attention": _attention,
    "autograd": _autograd,
    "convolution": _convolution,
    "embedding": _embedding,
    "matmul": _matmul,
    "norm": _norm,
    "optimizer": _optimizer,
    "quantized_matmul": _quantized_matmul,
    "rope": _rope,
    "sampling": _sampling,
}


def dispatch(case_id: str, inputs: Sequence[object]) -> object:
    """Q30: execute one exact generated dtype, shape, operator, and parameter tuple."""
    row = _CASES.get(case_id)
    if row is None:
        raise _error(
            "UNSUPPORTED_OPERATOR",
            case_id or "operator-case",
            "Q30: generated operator dispatch",
            "case is absent from the pinned dispatch table",
        )
    mx, _ = _mlx_runtime()
    _require_runtime(case_id, mx)
    values = tuple(inputs)
    observed_shapes = [list(value.shape) for value in values if isinstance(value, mx.array)]
    observed_dtypes = [str(value.dtype).rsplit(".", 1)[-1] for value in values if isinstance(value, mx.array)]
    if len(values) != len(row["input_shapes"]) or len(observed_shapes) != len(values):
        raise _error(
            "INVALID_REQUEST",
            case_id,
            "Q30: generated operator signature",
            f"requires {len(row['input_shapes'])} MLX arrays; received {len(values)} values",
        )
    if observed_shapes != row["input_shapes"] or observed_dtypes != row["input_dtypes"]:
        raise _error(
            "INVALID_REQUEST",
            case_id,
            "Q30: generated dtype and shape tuple",
            f"requires {row['input_dtypes']} {row['input_shapes']}; received {observed_dtypes} {observed_shapes}",
        )
    executor = _EXECUTORS.get(row["operator"])
    if executor is None:
        raise _error(
            "UNSUPPORTED_OPERATOR",
            case_id,
            "Q30: declared runtime operator",
            f"no MLX executor exists for {row['operator']}",
        )
    try:
        result = executor(values, row["parameters"])
        mx.eval(result)
    except Exception as exc:
        raise _error(
            "CAPABILITY_MISMATCH",
            case_id,
            "Q30: pinned MLX operator execution",
            f"{type(exc).__name__}: {exc}",
        ) from exc
    output_shape = list(result.shape)
    output_dtype = str(result.dtype).rsplit(".", 1)[-1]
    if output_shape != row["output_shape"] or output_dtype != row["output_dtype"]:
        raise _error(
            "CAPABILITY_MISMATCH",
            case_id,
            "Q30: declared operator result",
            f"declared {row['output_dtype']} {row['output_shape']}; received {output_dtype} {output_shape}",
        )
    return result


_PAGE_STATES = {
    "ABSENT": frozenset({"ACQUIRING"}),
    "ACQUIRING": frozenset({"HASHED", "FAILED"}),
    "HASHED": frozenset({"RESIDENT"}),
    "RESIDENT": frozenset({"GPU_SUBMITTED"}),
    "GPU_SUBMITTED": frozenset({"RECLAIMABLE"}),
    "RECLAIMABLE": frozenset(),
    "FAILED": frozenset(),
}
_HEX = frozenset("0123456789abcdef")


@dataclass(frozen=True)
class _CompiledRuntimeStep:
    schedule: ResidencyStep
    operator_case_id: str
    service_face: tuple[str, ...]
    description_digest: str
    exact_pages: tuple[str, ...]
    sample_units: tuple[tuple[int, tuple[str, ...]], ...]
    probabilities: tuple[Fraction, ...]
    sampling_kind: str
    exact_schedule: str


def _runtime_error(
    code: str,
    object_id: str,
    invariant: str,
    detail: str,
    *,
    retryability: str = "terminal",
) -> CassetteError:
    return _error(
        code,
        object_id,
        invariant,
        detail,
        retryability=retryability,
    )


def _runtime_record(
    value: object,
    fields: set[str],
    object_id: str,
    label: str,
) -> dict:
    if not isinstance(value, dict) or set(value) != fields:
        raise _runtime_error(
            "CAPABILITY_MISMATCH",
            object_id,
            f"Q20: immutable {label}",
            f"requires exactly {sorted(fields)}",
        )
    return value


def _runtime_items(
    value: object,
    object_id: str,
    label: str,
    *,
    code: str = "CAPABILITY_MISMATCH",
    invariant: str | None = None,
) -> tuple:
    if not isinstance(value, (list, tuple)):
        raise _runtime_error(
            code,
            object_id,
            invariant or f"Q20: immutable {label}",
            "requires an ordered collection",
        )
    return tuple(value)


def _runtime_identifier(
    value: object,
    object_id: str,
    invariant: str,
    label: str,
    *,
    code: str = "CAPABILITY_MISMATCH",
) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= 256:
        raise _runtime_error(
            code,
            object_id,
            invariant,
            f"{label} requires a nonempty identifier of at most 256 characters",
        )
    return value


def _runtime_u64(
    value: object,
    object_id: str,
    invariant: str,
    label: str,
) -> int:
    if type(value) is not int or not 0 <= value <= _MAX_U64:
        raise _runtime_error(
            "CAPABILITY_MISMATCH",
            object_id,
            invariant,
            f"{label} requires an unsigned 64-bit integer",
        )
    return value


def _digest_identity(
    value: object,
    object_id: str,
    invariant: str,
    label: str,
    *,
    code: str = "CAPABILITY_MISMATCH",
) -> str:
    if (
        not isinstance(value, str)
        or not value.startswith("blake3:")
        or len(value) != 71
        or not set(value[7:]) <= _HEX
    ):
        raise _runtime_error(
            code,
            object_id,
            invariant,
            f"{label} requires one canonical BLAKE3 identity",
        )
    return value


def _runtime_document_digest(
    value: object,
    object_id: str,
    invariant: str,
    label: str,
) -> str:
    try:
        return _digest(value)
    except CassetteError as exc:
        raise _runtime_error(
            "CAPABILITY_MISMATCH",
            object_id,
            invariant,
            f"{label} requires canonical JSON data: {exc.detail}",
        ) from exc


def _ordered_unique(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def _move_page(
    states: dict[str, str],
    transitions: list[tuple[str, str, str]],
    page_digest: str,
    target: str,
) -> None:
    source = states[page_digest]
    if target not in _PAGE_STATES[source]:
        raise _runtime_error(
            "CAPABILITY_MISMATCH",
            page_digest,
            "Q20: page-readiness state machine",
            f"illegal transition {source} -> {target}",
        )
    states[page_digest] = target
    transitions.append((page_digest, source, target))


def _deadline(value: object, object_id: str) -> float | None:
    if value is None:
        return None
    if type(value) is int:
        valid = 0 <= value <= _MAX_BINARY64_INTEGER
    else:
        valid = type(value) is float and math.isfinite(value) and value >= 0
    if not valid:
        raise _runtime_error(
            "INVALID_REQUEST",
            object_id,
            "Q20: bounded page-readiness deadline",
            "timeout_seconds must be a finite nonnegative binary64-representable number or None",
        )
    return float(value)


def _cancelled(cancel_event: asyncio.Event | None, object_id: str) -> None:
    if cancel_event is not None and not isinstance(cancel_event, asyncio.Event):
        raise _runtime_error(
            "INVALID_REQUEST",
            object_id,
            "Q20: cancellation control",
            "cancel_event must be an asyncio.Event or None",
        )
    if cancel_event is not None and cancel_event.is_set():
        raise _runtime_error(
            "OPERATION_CANCELLED",
            object_id,
            "Q20: cancellation before page consumption",
            "the operation was cancelled before command submission",
            retryability="retryable",
        )


async def _acquire_pages(
    cartridge: Path,
    locations: dict[str, object],
    ordered_pages: tuple[str, ...],
    timeout_seconds: float | None,
    cancel_event: asyncio.Event | None,
    object_id: str,
    transitions: list[tuple[str, str, str]],
) -> dict[str, bytes]:
    states = {page_digest: "ABSENT" for page_digest in ordered_pages}
    payloads: dict[str, bytes] = {}
    try:
        async with asyncio.timeout(timeout_seconds):
            for page_digest in ordered_pages:
                _cancelled(cancel_event, object_id)
                _move_page(states, transitions, page_digest, "ACQUIRING")
                location = locations.get(page_digest)
                if location is None:
                    _move_page(states, transitions, page_digest, "FAILED")
                    raise _runtime_error(
                        "PAGE_CORRUPT",
                        page_digest,
                        "Q20: every planned page exists before consumption",
                        "the selected root has no physical record for this planned page",
                    )
                try:
                    payload = await asyncio.to_thread(_read_page, cartridge, location)
                except CassetteError:
                    _move_page(states, transitions, page_digest, "FAILED")
                    raise
                if cancel_event is not None and cancel_event.is_set():
                    _move_page(states, transitions, page_digest, "FAILED")
                    _cancelled(cancel_event, object_id)
                _move_page(states, transitions, page_digest, "HASHED")
                _move_page(states, transitions, page_digest, "RESIDENT")
                payloads[page_digest] = payload
    except TimeoutError as exc:
        for page_digest, state in tuple(states.items()):
            if state == "ACQUIRING":
                _move_page(states, transitions, page_digest, "FAILED")
        raise _runtime_error(
            "WORKING_SET_TIMEOUT",
            object_id,
            "Q20: page readiness before command submission",
            "the declared page-readiness deadline expired",
            retryability="retryable",
        ) from exc
    except asyncio.CancelledError as exc:
        for page_digest, state in tuple(states.items()):
            if state == "ACQUIRING":
                _move_page(states, transitions, page_digest, "FAILED")
        raise _runtime_error(
            "OPERATION_CANCELLED",
            object_id,
            "Q20: cancellation before page consumption",
            "the execution task was cancelled before command completion",
            retryability="retryable",
        ) from exc
    return payloads


def _submit_resident_pages(
    payloads: dict[str, bytes],
    ordered_pages: tuple[str, ...],
    transitions: list[tuple[str, str, str]],
    object_id: str,
) -> None:
    """Fence one real MLX command on pages whose content identities were just verified."""

    states = {page_digest: "RESIDENT" for page_digest in ordered_pages}
    try:
        mx, _ = _mlx_runtime()
        _require_runtime(object_id, mx)
        arrays = tuple(
            mx.array(bytearray(payloads[page_digest]), dtype=mx.uint8)
            for page_digest in ordered_pages
        )
        for page_digest in ordered_pages:
            _move_page(states, transitions, page_digest, "GPU_SUBMITTED")
        mx.eval(*arrays)
    except CassetteError:
        raise
    except Exception as exc:
        raise _runtime_error(
            "CAPABILITY_MISMATCH",
            object_id,
            "Q20: resident pages submitted through pinned MLX",
            f"{type(exc).__name__}: {exc}",
        ) from exc
    for page_digest in ordered_pages:
        _move_page(states, transitions, page_digest, "RECLAIMABLE")


def _execution_digest(
    mode: str,
    route: tuple[str, ...],
    payloads: dict[str, bytes],
    *,
    atom_id: str | None = None,
    sample_units: tuple[int, ...] = (),
) -> str:
    return _digest({
        "mode": mode,
        "atom_id": atom_id,
        "route": [
            {"page_digest": page_digest, "payload_digest": digest_bytes(payloads[page_digest])}
            for page_digest in route
        ],
        "sample_units": list(sample_units),
    })


class NativePager:
    """Q20/Q64 exact source-route execution; prediction may change read order only."""

    def __init__(self, cartridge: str | Path, root_digest: str):
        self._cartridge = Path(cartridge)
        self._root_digest = root_digest
        self._locations = {
            location.page_digest: location
            for location in page_locations(self._cartridge, root_digest)
        }
        self.last_attempt_transitions: tuple[tuple[str, str, str], ...] = ()

    async def execute(
        self,
        source_route: Sequence[str],
        prefetch: NativePrefetch,
        *,
        timeout_seconds: float | None = None,
        cancel_event: asyncio.Event | None = None,
    ) -> PageExecution:
        route = tuple(
            _digest_identity(
                page_digest,
                self._root_digest,
                "Q20: source-native planned page identity",
                "source-route page identity",
            )
            for page_digest in _runtime_items(
                source_route,
                self._root_digest,
                "source-native planned pages",
                code="INVALID_REQUEST",
                invariant="Q20: source-native planned pages",
            )
        )
        if not route or len(route) != len(set(route)):
            raise _runtime_error(
                "INVALID_REQUEST",
                self._root_digest,
                "Q20: source-native planned pages",
                "the source route must name at least one distinct page",
            )
        if not isinstance(prefetch, NativePrefetch):
            raise _runtime_error(
                "INVALID_REQUEST",
                self._root_digest,
                "Q64: non-semantic native prefetch",
                "NativePrefetch is required",
            )
        candidates = tuple(
            _digest_identity(
                page_digest,
                self._root_digest,
                "Q64: native prefetch page identity",
                "prefetch page identity",
            )
            for page_digest in _runtime_items(
                prefetch.page_candidates,
                self._root_digest,
                "native prefetch page candidates",
                code="INVALID_REQUEST",
                invariant="Q64: native prefetch page candidates",
            )
        )
        if len(candidates) != len(set(candidates)):
            raise _runtime_error(
                "INVALID_REQUEST",
                self._root_digest,
                "Q64: non-semantic native prefetch",
                "prefetch candidates may not repeat",
            )
        if (
            type(prefetch.confidence) not in (int, float)
            or not 0 <= prefetch.confidence <= 1
            or type(prefetch.bytes) is not int
            or not 0 <= prefetch.bytes <= _MAX_U64
        ):
            raise _runtime_error(
                "INVALID_REQUEST",
                self._root_digest,
                "Q64: bounded native prefetch record",
                "confidence must be in [0,1] and bytes must be unsigned 64-bit",
            )
        deadline = _deadline(timeout_seconds, self._root_digest)
        route_set = set(route)
        acquisition_order = _ordered_unique(
            (*[page for page in candidates if page in route_set], *route)
        )
        transitions: list[tuple[str, str, str]] = []
        try:
            payloads = await _acquire_pages(
                self._cartridge,
                self._locations,
                acquisition_order,
                deadline,
                cancel_event,
                self._root_digest,
                transitions,
            )
            _cancelled(cancel_event, self._root_digest)
            _submit_resident_pages(
                payloads,
                acquisition_order,
                transitions,
                self._root_digest,
            )
        finally:
            self.last_attempt_transitions = tuple(transitions)
        return PageExecution(
            mode="NATIVE_EXACT",
            step=None,
            certificate_digest=None,
            planned_pages=route,
            sample_units=(),
            execution_seed=None,
            output_digest=_execution_digest("NATIVE_EXACT", route, payloads),
            transitions=tuple(transitions),
        )


def _bind_runtime_steps(
    plan: dict,
    certificate: dict,
    evidence: dict,
    schedule: CertifiedSchedule,
    page_map: dict,
    locations: dict[str, object],
) -> tuple[_CompiledRuntimeStep, ...]:
    rows = _runtime_items(page_map["steps"], plan["plan_id"], "page-map steps")
    if len(rows) != len(schedule.steps):
        raise _runtime_error(
            "CAPABILITY_MISMATCH",
            plan["plan_id"],
            "Q20: complete certified page map",
            "one page-map row is required for every certified schedule step",
        )

    atom_claims = {row["atom_id"]: row for row in certificate["atoms"]}
    atom_evidence = {row["atom_id"]: row for row in evidence["atoms"]}
    service_faces = {
        row["face_id"]: tuple(row["condition_ids"])
        for row in certificate["compatibility"]["service_faces"]
    }
    operation_rows = {
        row["operation_id"]: row
        for row in evidence["execution_contract"]["operations"]
    }
    sampling_laws = {
        row["sampling_law_id"]: row
        for row in evidence["execution_contract"]["sampling_laws"]
    }
    runtime_steps = []
    for expected, raw in zip(schedule.steps, rows, strict=True):
        row = _runtime_record(
            raw,
            {
                "atom_id",
                "description_digest",
                "exact_pages",
                "operation_id",
                "sample_units",
                "step",
            },
            plan["plan_id"],
            "page-map step",
        )
        row_step = _runtime_u64(
            row["step"],
            plan["plan_id"],
            "Q20: certified schedule page relation",
            "page-map step",
        )
        row_operation_id = _runtime_identifier(
            row["operation_id"],
            plan["plan_id"],
            "Q20: certified schedule page relation",
            "page-map operation_id",
        )
        row_atom_id = _runtime_identifier(
            row["atom_id"],
            plan["plan_id"],
            "Q20: certified schedule page relation",
            "page-map atom_id",
        )
        if (
            row_step != expected.step
            or row_operation_id != expected.operation_id
            or row_atom_id != expected.atom_id
        ):
            raise _runtime_error(
                "CAPABILITY_MISMATCH",
                plan["plan_id"],
                "Q20: certified schedule page relation",
                "page-map step, operation, and atom must equal the certified schedule",
            )
        atom_claim = atom_claims[expected.atom_id]
        description_digest = _digest(atom_claim["description"])
        row_description_digest = _digest_identity(
            row["description_digest"],
            expected.atom_id,
            "Q20: immutable compiled description",
            "page-map description identity",
        )
        if row_description_digest != description_digest:
            raise _runtime_error(
                "CAPABILITY_MISMATCH",
                expected.atom_id,
                "Q20: immutable compiled description",
                "page-map description identity differs from the certificate",
            )
        exact_pages = tuple(
            _digest_identity(
                page_digest,
                expected.atom_id,
                "Q20: exact description page identity",
                "exact description page identity",
            )
            for page_digest in _runtime_items(
                row["exact_pages"], expected.atom_id, "exact description pages"
            )
        )
        if not exact_pages or len(exact_pages) != len(set(exact_pages)):
            raise _runtime_error(
                "CAPABILITY_MISMATCH",
                expected.atom_id,
                "Q20: exact description pages",
                "each compiled step requires distinct exact description pages",
            )
        operation = operation_rows[expected.operation_id]
        law = sampling_laws[operation["sampling_law_id"]]
        distributions = {
            item["atom_id"]: item["columns"]
            for item in law["law"].get("atom_distributions", [])
        }
        expected_distribution = distributions.get(expected.atom_id, [])
        expected_units = tuple(item["column"] for item in expected_distribution)
        probabilities = tuple(
            Fraction(item["probability"]) for item in expected_distribution
        )
        sample_rows = _runtime_items(
            row["sample_units"], expected.atom_id, "sample page units"
        )
        sample_units = []
        for sample_row in sample_rows:
            sample = _runtime_record(
                sample_row,
                {"page_digests", "unit"},
                expected.atom_id,
                "sample page unit",
            )
            pages = tuple(
                _digest_identity(
                    page_digest,
                    expected.atom_id,
                    "Q20: sampled correction page identity",
                    "sampled correction page identity",
                )
                for page_digest in _runtime_items(
                    sample["page_digests"], expected.atom_id, "sampled correction pages"
                )
            )
            if not pages or len(pages) != len(set(pages)):
                raise _runtime_error(
                    "CAPABILITY_MISMATCH",
                    expected.atom_id,
                    "Q20: sampled correction pages",
                    "every sample unit requires distinct pages",
                )
            sample_units.append((
                _runtime_u64(
                    sample["unit"],
                    expected.atom_id,
                    "Q20: certified sampling page catalog",
                    "sample unit",
                ),
                pages,
            ))
        if tuple(unit for unit, _ in sample_units) != expected_units:
            raise _runtime_error(
                "CAPABILITY_MISMATCH",
                expected.atom_id,
                "Q20: certified sampling page catalog",
                "sample units must equal the recomputed sampling-law support",
            )
        if (law["kind"] == "EXACT") != (not sample_units and not probabilities):
            raise _runtime_error(
                "CAPABILITY_MISMATCH",
                expected.atom_id,
                "Q20: declared exact or stochastic page plan",
                "EXACT forbids sample pages; FRESH_RANDOM requires them",
            )
        possible_routes = [exact_pages]
        if sample_units:
            if expected.fresh_samples == 1:
                possible_routes.extend(
                    _ordered_unique((*exact_pages, *pages))
                    for _, pages in sample_units
                )
            else:
                possible_routes.append(_ordered_unique((
                    *exact_pages,
                    *(page for _, pages in sample_units for page in pages),
                )))
        if max(len(route) for route in possible_routes) > expected.page_reads:
            raise _runtime_error(
                "CAPABILITY_MISMATCH",
                expected.operation_id,
                "Q20: certified page-read count",
                "one possible correction route exceeds the certified page-read count",
            )
        for route in possible_routes:
            known_bytes = sum(
                locations[page_digest].length
                for page_digest in route
                if page_digest in locations
            )
            if known_bytes > expected.load_bytes:
                raise _runtime_error(
                    "CAPABILITY_MISMATCH",
                    expected.operation_id,
                    "Q20: certified page byte count",
                    "known pages exceed the certified load-byte bound",
                )
        runtime_steps.append(_CompiledRuntimeStep(
            schedule=expected,
            operator_case_id=operation["operator_case_id"],
            service_face=service_faces[atom_claim["service_face_id"]],
            description_digest=description_digest,
            exact_pages=exact_pages,
            sample_units=tuple(sample_units),
            probabilities=probabilities,
            sampling_kind=law["kind"],
            exact_schedule=certificate["trace_contract"]["schedule_digest"],
        ))
        if atom_evidence[expected.atom_id]["description"]["sampling_law_id"] != law["sampling_law_id"]:
            raise _runtime_error(
                "CAPABILITY_MISMATCH",
                expected.atom_id,
                "Q20: admitted sampling-law relation",
                "atom description and operation name different sampling laws",
            )
    return tuple(runtime_steps)


def _draw_units(
    step: _CompiledRuntimeStep,
    certificate_id: str,
    seed_or_schedule: int | str,
) -> tuple[tuple[int, ...], int | None]:
    if step.sampling_kind == "EXACT":
        if seed_or_schedule != step.exact_schedule:
            raise _runtime_error(
                "CAPABILITY_MISMATCH",
                certificate_id,
                "Q20: exact certified execution schedule",
                "EXACT execution requires the immutable schedule identity",
            )
        return (), None
    if (
        isinstance(seed_or_schedule, bool)
        or not isinstance(seed_or_schedule, int)
        or not 0 <= seed_or_schedule <= _MAX_U64
    ):
        raise _runtime_error(
            "CAPABILITY_MISMATCH",
            certificate_id,
            "Q20: certified fresh-random seed contract",
            "FRESH_RANDOM requires one recorded unsigned 64-bit counter key",
        )
    denominators = [probability.denominator for probability in step.probabilities]
    denominator = math.lcm(*denominators)
    weights = [
        probability.numerator * (denominator // probability.denominator)
        for probability in step.probabilities
    ]
    total = sum(weights)
    ceiling = 1 << 256
    accepted = ceiling - ceiling % total
    unit_ids = tuple(unit for unit, _ in step.sample_units)
    draws = []
    for draw in range(step.schedule.fresh_samples):
        attempt = 0
        while True:
            block = digest_bytes(canonical_bytes({
                "certificate_id": certificate_id,
                "step": step.schedule.step,
                "seed": seed_or_schedule,
                "draw": draw,
                "attempt": attempt,
            }))
            value = int(block[7:], 16)
            attempt += 1
            if value < accepted:
                target = value % total
                break
        cursor = 0
        for unit, weight in zip(unit_ids, weights, strict=True):
            cursor += weight
            if target < cursor:
                draws.append(unit)
                break
    return tuple(draws), seed_or_schedule


class CertifiedPager:
    """Q20/Q64 compiled execution bound to one recomputed certificate and page map."""

    def __init__(
        self,
        cartridge: str | Path,
        plan: object,
        certificate: object,
        evidence: object,
        profile: object,
        page_map: object,
    ):
        schedule = admit_schedule(plan, certificate, evidence, profile)
        assert isinstance(plan, dict) and isinstance(certificate, dict) and isinstance(evidence, dict)
        map_record = _runtime_record(
            page_map,
            {"root_digest", "steps"},
            plan["plan_id"],
            "page map",
        )
        root_digest = _digest_identity(
            map_record["root_digest"],
            plan["plan_id"],
            "Q20: page-map root identity",
            "page-map root identity",
        )
        if _runtime_document_digest(
            map_record,
            plan["plan_id"],
            "Q20: immutable page-map identity",
            "page map",
        ) != plan["page_map_digest"]:
            raise _runtime_error(
                "CAPABILITY_MISMATCH",
                plan["plan_id"],
                "Q20: immutable page-map identity",
                "the canonical page map does not match the compiled plan",
            )
        self._cartridge = Path(cartridge)
        locations = {
            location.page_digest: location
            for location in page_locations(self._cartridge, root_digest)
        }
        self._steps = _bind_runtime_steps(
            plan,
            certificate,
            evidence,
            schedule,
            map_record,
            locations,
        )
        self._locations = locations
        self._schedule = schedule
        self._profile = dict(profile)
        self._certificate_id = schedule.certificate_id
        self._support = frozenset(evidence["observation_contract"]["support"])
        self._cover = {
            row["condition_id"]: row["atom_id"]
            for row in certificate["compatibility"]["cover"]
        }
        self._next_step = 0
        self.last_attempt_transitions: tuple[tuple[str, str, str], ...] = ()
        self.last_committed: PageExecution | None = None
        self.replay_selection: CompiledSelection | None = None

    @property
    def next_step(self) -> int:
        return self._next_step

    def _validate_selection(
        self,
        selection: object,
    ) -> tuple[_CompiledRuntimeStep, tuple[int, ...], int | None]:
        if self._next_step >= len(self._steps):
            raise _runtime_error(
                "CAPABILITY_MISMATCH",
                self._certificate_id,
                "Q64: certified execution horizon",
                "the immutable certificate has no further schedule step",
            )
        if not isinstance(selection, CompiledSelection):
            raise _runtime_error(
                "INVALID_REQUEST",
                self._certificate_id,
                "Q64: compiled selection record",
                "CompiledSelection is required",
            )
        step = self._steps[self._next_step]
        certificate_digest = _digest_identity(
            selection.certificate_digest,
            self._certificate_id,
            "Q64: compiled selection record",
            "selection certificate_digest",
            code="INVALID_REQUEST",
        )
        observed_condition = _runtime_identifier(
            selection.observed_condition,
            self._certificate_id,
            "Q64: compiled selection record",
            "selection observed_condition",
            code="INVALID_REQUEST",
        )
        atom_id = _runtime_identifier(
            selection.atom_id,
            self._certificate_id,
            "Q64: compiled selection record",
            "selection atom_id",
            code="INVALID_REQUEST",
        )
        if not isinstance(selection.service_face, tuple):
            raise _runtime_error(
                "INVALID_REQUEST",
                self._certificate_id,
                "Q64: compiled selection record",
                "selection service_face requires an ordered tuple",
            )
        service_face = tuple(
            _runtime_identifier(
                condition,
                self._certificate_id,
                "Q64: compiled selection record",
                "selection service-face condition",
                code="INVALID_REQUEST",
            )
            for condition in selection.service_face
        )
        description_digest = _digest_identity(
            selection.description_digest,
            self._certificate_id,
            "Q64: compiled selection record",
            "selection description_digest",
            code="INVALID_REQUEST",
        )
        if certificate_digest != self._certificate_id:
            raise _runtime_error(
                "CAPABILITY_MISMATCH",
                certificate_digest,
                "Q64: immutable compiled certificate",
                "selection certificate differs from the admitted revision",
            )
        if observed_condition not in self._support:
            raise _runtime_error(
                "CAPABILITY_MISMATCH",
                observed_condition,
                "Q64: certified observation support",
                "compiled selection rejects every off-support observation",
            )
        if (
            self._cover.get(observed_condition) != atom_id
            or atom_id != step.schedule.atom_id
        ):
            raise _runtime_error(
                "CAPABILITY_MISMATCH",
                atom_id,
                "Q64: certified atom cover",
                "the selected atom does not cover this condition at this schedule step",
            )
        if service_face != step.service_face:
            raise _runtime_error(
                "CAPABILITY_MISMATCH",
                atom_id,
                "Q64: certified service face",
                "the selection presents a forged or incomplete service face",
            )
        if description_digest != step.description_digest:
            raise _runtime_error(
                "CAPABILITY_MISMATCH",
                atom_id,
                "Q20: immutable compiled description",
                "selection description differs from the admitted certificate",
            )
        if (
            isinstance(selection.bytes, bool)
            or not isinstance(selection.bytes, int)
            or selection.bytes != step.schedule.load_bytes
        ):
            raise _runtime_error(
                "CAPABILITY_MISMATCH",
                step.schedule.operation_id,
                "Q20: certified selection byte count",
                f"selection must declare exactly {step.schedule.load_bytes} bytes",
            )
        draws, seed = _draw_units(
            step,
            self._certificate_id,
            selection.execution_seed_or_exact_schedule,
        )
        return step, draws, seed

    async def _prepare_execution(
        self,
        selection: CompiledSelection,
        timeout_seconds: float | None,
        cancel_event: asyncio.Event | None,
        transitions: list[tuple[str, str, str]],
    ) -> tuple[
        _CompiledRuntimeStep,
        tuple[int, ...],
        int | None,
        tuple[str, ...],
        dict[str, bytes],
    ]:
        step, sample_units, seed = self._validate_selection(selection)
        deadline = _deadline(timeout_seconds, self._certificate_id)
        sample_pages = dict(step.sample_units)
        planned_pages = _ordered_unique((
            *step.exact_pages,
            *(page for unit in sample_units for page in sample_pages[unit]),
        ))
        self.replay_selection = selection
        payloads = await _acquire_pages(
            self._cartridge,
            self._locations,
            planned_pages,
            deadline,
            cancel_event,
            self._certificate_id,
            transitions,
        )
        _cancelled(cancel_event, self._certificate_id)
        return step, sample_units, seed, planned_pages, payloads

    async def execute(
        self,
        selection: CompiledSelection,
        *,
        timeout_seconds: float | None = None,
        cancel_event: asyncio.Event | None = None,
    ) -> PageExecution:
        transitions: list[tuple[str, str, str]] = []
        try:
            step, sample_units, seed, planned_pages, payloads = (
                await self._prepare_execution(
                    selection,
                    timeout_seconds,
                    cancel_event,
                    transitions,
                )
            )
            _submit_resident_pages(
                payloads,
                planned_pages,
                transitions,
                self._certificate_id,
            )
            committed = PageExecution(
                mode="COMPILED_CERTIFIED",
                step=step.schedule.step,
                certificate_digest=self._certificate_id,
                planned_pages=planned_pages,
                sample_units=sample_units,
                execution_seed=seed,
                output_digest=_execution_digest(
                    "COMPILED_CERTIFIED",
                    planned_pages,
                    payloads,
                    atom_id=step.schedule.atom_id,
                    sample_units=sample_units,
                ),
                transitions=tuple(transitions),
            )
            self.last_committed = committed
            self._next_step += 1
            self.replay_selection = None
            return committed
        finally:
            self.last_attempt_transitions = tuple(transitions)


@dataclass(frozen=True)
class _TransformerRuntimeStep:
    embedding_case_id: str
    projection_case_id: str
    attention_case_id: str
    embedding_shape: tuple[int, ...]
    projection_shape: tuple[int, ...]
    attention_shape: tuple[int, ...]
    token_count: int
    vocabulary_size: int
    metadata: bytes
    embedding_page: str
    query_page: str
    key_page: str
    exact_value_page: str
    sampled_value_pages: tuple[tuple[int, str], ...]
    model_tensor_bytes: int
    activation_bytes: int


def _real_matrix(
    value: object,
    shape: tuple[int, int],
    object_id: str,
    label: str,
) -> tuple[tuple[Fraction, ...], ...]:
    matrix = _matrix(value, shape, "REAL", object_id, label)
    if any(scalar[1] for row in matrix for scalar in row):
        raise _runtime_error(
            "CAPABILITY_MISMATCH",
            object_id,
            "Q36: real F3 attention representation",
            f"{label} contains an imaginary component",
        )
    return tuple(tuple(scalar[0] for scalar in row) for row in matrix)


def _float32_payload(
    matrix: tuple[tuple[Fraction, ...], ...],
    object_id: str,
    label: str,
) -> bytes:
    try:
        return struct.pack(
            f"<{sum(len(row) for row in matrix)}f",
            *(float(value) for row in matrix for value in row),
        )
    except (OverflowError, struct.error) as exc:
        raise _runtime_error(
            "CAPABILITY_MISMATCH",
            object_id,
            "Q36: finite float32 transformer representation",
            f"{label} cannot be represented as finite float32: {exc}",
        ) from exc


def _transpose_matrix(
    matrix: tuple[tuple[Fraction, ...], ...],
) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(tuple(row[column] for row in matrix) for column in range(len(matrix[0])))


def _transformer_metadata(
    step: _CompiledRuntimeStep,
    sampling_law_id: str,
) -> bytes:
    return canonical_bytes({
        "atom_id": step.schedule.atom_id,
        "operation_id": step.schedule.operation_id,
        "sampling_kind": step.sampling_kind,
        "sampling_law_id": sampling_law_id,
        "sample_units": [
            {"probability": str(probability), "unit": unit}
            for (unit, _), probability in zip(
                step.sample_units,
                step.probabilities,
                strict=True,
            )
        ],
    })


def _bind_transformer_steps(
    runtime_steps: tuple[_CompiledRuntimeStep, ...],
    evidence: dict,
    locations: dict[str, object],
    profile: dict,
    object_id: str,
) -> tuple[tuple[_TransformerRuntimeStep, ...], int]:
    target = evidence["target"]
    if target["field"] != "REAL" or len(target["shape"]) != 2:
        raise _runtime_error(
            "UNSUPPORTED_OPERATOR",
            object_id,
            "Q36: F3 transformer target representation",
            "certified F3 attention requires one real matrix target",
        )
    target_shape = tuple(target["shape"])
    embedding_cases = [row for row in DISPATCH_ROWS if row["operator"] == "embedding"]
    projection_cases = [row for row in DISPATCH_ROWS if row["operator"] == "matmul"]
    if len(embedding_cases) != 1 or len(projection_cases) != 1:
        raise _runtime_error(
            "UNSUPPORTED_OPERATOR",
            object_id,
            "Q36: generated F3 transformer graph",
            "the generated table must identify one embedding and one projection tuple",
        )
    embedding_case = embedding_cases[0]
    projection_case = projection_cases[0]
    atom_rows = {row["atom_id"]: row for row in evidence["atoms"]}
    bound_steps = []
    kv_capacity = 0
    activation_peak = 0
    for step in runtime_steps:
        case = _CASES.get(step.operator_case_id)
        if (
            case is None
            or case["operator"] != "attention"
            or case["input_dtypes"] != ["float32", "float32", "float32"]
            or case["output_dtype"] != "float32"
        ):
            raise _runtime_error(
                "UNSUPPORTED_OPERATOR",
                step.operator_case_id,
                "Q36: generated F3 attention tuple",
                "the F3 transformer requires one generated float32 attention case",
            )
        attention_shape = tuple(case["input_shapes"][2])
        if (
            tuple(reversed(projection_case["input_shapes"][1])) != target_shape
            or embedding_case["output_shape"] != projection_case["input_shapes"][0]
            or math.prod(projection_case["output_shape"]) != math.prod(attention_shape)
            or len(attention_shape) < 2
            or math.prod(attention_shape[:-2]) != 1
            or case["input_shapes"][0] != case["input_shapes"][1]
            or case["input_shapes"][0] != case["input_shapes"][2]
            or case["output_shape"] != case["input_shapes"][2]
        ):
            raise _runtime_error(
                "UNSUPPORTED_OPERATOR",
                step.operator_case_id,
                "Q36: generated F3 attention tuple",
                "query, key, value, output, and certified matrix shapes must agree",
            )
        atom = atom_rows[step.schedule.atom_id]
        matrix = _real_matrix(
            atom["matrix"], target_shape, step.schedule.atom_id, "atom matrix"
        )
        reconstruction = _real_matrix(
            atom["description"]["reconstruction"],
            target_shape,
            step.schedule.atom_id,
            "description reconstruction",
        )
        description_payload = _float32_payload(
            _transpose_matrix(reconstruction),
            step.schedule.atom_id,
            "transposed description reconstruction",
        )
        embedding_bytes = math.prod(embedding_case["input_shapes"][0]) * 4
        projection_bytes = math.prod(projection_case["input_shapes"][1]) * 4
        exact_lengths = (embedding_bytes, projection_bytes, projection_bytes, projection_bytes)
        if len(step.exact_pages) != 4 or any(
            page not in locations or locations[page].length != length
            for page, length in zip(step.exact_pages, exact_lengths, strict=True)
        ) or (
            step.exact_pages[3] != digest_bytes(description_payload)
            or len(description_payload) != projection_bytes
        ):
            raise _runtime_error(
                "CAPABILITY_MISMATCH",
                step.schedule.atom_id,
                "Q19/Q36: physical description equals certified reconstruction",
                "the ordered embedding, Q, K, and V pages do not encode the certified F3 description",
            )
        sampled_value_pages = []
        for (unit, pages), probability in zip(
            step.sample_units,
            step.probabilities,
            strict=True,
        ):
            if len(pages) != 1 or probability <= 0 or unit >= target_shape[1]:
                raise _runtime_error(
                    "CAPABILITY_MISMATCH",
                    step.schedule.atom_id,
                    "Q36: executable fresh residual page",
                    "each residual column requires one positive-probability value page",
                )
            estimator = [list(row) for row in reconstruction]
            for row in range(target_shape[0]):
                estimator[row][unit] += (
                    matrix[row][unit] - reconstruction[row][unit]
                ) / probability
            estimator_payload = _float32_payload(
                _transpose_matrix(tuple(tuple(row) for row in estimator)),
                step.schedule.atom_id,
                f"transposed sample unit {unit} estimator",
            )
            if (
                pages[0] != digest_bytes(estimator_payload)
                or pages[0] not in locations
                or locations[pages[0]].length != len(estimator_payload)
            ):
                raise _runtime_error(
                    "CAPABILITY_MISMATCH",
                    step.schedule.atom_id,
                    "Q19/Q36: physical correction equals certified estimator",
                    f"sample unit {unit} does not encode its certified float32 estimator",
                )
            sampled_value_pages.append((unit, pages[0]))
        if step.sampling_kind == "EXACT":
            if sampled_value_pages or step.schedule.fresh_samples:
                raise _runtime_error(
                    "CAPABILITY_MISMATCH",
                    step.schedule.atom_id,
                    "Q36: exact F3 description",
                    "exact execution cannot name correction pages or samples",
                )
        elif step.sampling_kind == "FRESH_RANDOM":
            if step.schedule.fresh_samples != 1 or not sampled_value_pages:
                raise _runtime_error(
                    "CAPABILITY_MISMATCH",
                    step.schedule.atom_id,
                    "Q36: fresh F3 residual estimator",
                    "the F3 attention path requires exactly one fresh certified sample",
                )
        else:
            raise _runtime_error(
                "CAPABILITY_MISMATCH",
                step.schedule.atom_id,
                "Q36: exact or fresh F3 description",
                f"unsupported sampling kind {step.sampling_kind!r}",
            )
        metadata = _transformer_metadata(
            step, atom["description"]["sampling_law_id"]
        )
        token_bytes = math.prod(embedding_case["input_shapes"][1]) * 4
        hidden_bytes = math.prod(embedding_case["output_shape"]) * 4
        projection_output_bytes = math.prod(projection_case["output_shape"]) * 4
        output_bytes = math.prod(case["output_shape"]) * 4
        activation_bytes = (
            token_bytes
            + hidden_bytes
            + 5 * projection_output_bytes
            + output_bytes
        )
        model_tensor_bytes = embedding_bytes + 3 * projection_bytes
        maximum_route = 4 + (1 if sampled_value_pages else 0)
        maximum_load = sum(exact_lengths) + (
            projection_bytes if sampled_value_pages else 0
        )
        dynamic_memory = maximum_load + model_tensor_bytes + len(metadata)
        if (
            step.schedule.description_bytes != sum(exact_lengths)
            or step.schedule.metadata_bytes != len(metadata)
            or step.schedule.page_reads != maximum_route
            or step.schedule.load_bytes != maximum_load
            or step.schedule.dynamic_memory_bytes != dynamic_memory
        ):
            raise _runtime_error(
                "CAPABILITY_MISMATCH",
                step.schedule.operation_id,
                "Q63: transformer trace equals certified schedule",
                "description, metadata, page, traffic, or dynamic-memory demand differs from the executable route",
            )
        bound_steps.append(_TransformerRuntimeStep(
            embedding_case_id=embedding_case["case_id"],
            projection_case_id=projection_case["case_id"],
            attention_case_id=case["case_id"],
            embedding_shape=tuple(embedding_case["input_shapes"][0]),
            projection_shape=tuple(projection_case["input_shapes"][1]),
            attention_shape=attention_shape,
            token_count=math.prod(embedding_case["input_shapes"][1]),
            vocabulary_size=embedding_case["input_shapes"][0][0],
            metadata=metadata,
            embedding_page=step.exact_pages[0],
            query_page=step.exact_pages[1],
            key_page=step.exact_pages[2],
            exact_value_page=step.exact_pages[3],
            sampled_value_pages=tuple(sampled_value_pages),
            model_tensor_bytes=model_tensor_bytes,
            activation_bytes=activation_bytes,
        ))
        kv_capacity += 2 * projection_output_bytes
        activation_peak = max(activation_peak, activation_bytes)
    if (
        profile["context_bytes"] != kv_capacity
        or profile["activation_bytes"] != activation_peak
        or profile["cache_bytes"] != 0
        or profile["training_window_bytes"] != 0
    ):
        raise _runtime_error(
            "CAPABILITY_MISMATCH",
            object_id,
            "Q63: F3 recurrent and activation placement",
            "the profile must reserve exactly the F3 KV horizon and activation peak without cache or training state",
        )
    fixed_memory = sum(
        profile[name]
        for name in (
            "activation_bytes",
            "cache_bytes",
            "context_bytes",
            "runtime_buffer_bytes",
            "training_window_bytes",
        )
    )
    if any(
        runtime.schedule.live_memory_bytes
        != fixed_memory + runtime.schedule.dynamic_memory_bytes
        for runtime in runtime_steps
    ):
        raise _runtime_error(
            "CAPABILITY_MISMATCH",
            object_id,
            "Q63: transformer live-memory schedule",
            "one trace step differs from the admitted fixed plus dynamic memory equation",
        )
    return tuple(bound_steps), kv_capacity


def _runtime_tokens(
    value: object,
    count: int,
    vocabulary_size: int,
    object_id: str,
) -> tuple[int, ...]:
    if not isinstance(value, (list, tuple)) or len(value) != count:
        raise _runtime_error(
            "INVALID_REQUEST",
            object_id,
            "Q36: bounded transformer activation",
            f"tokens require exactly {count} unsigned indices",
        )
    tokens = []
    for item in value:
        if type(item) is not int or not 0 <= item < vocabulary_size:
            raise _runtime_error(
                "INVALID_REQUEST",
                object_id,
                "Q36: bounded transformer activation",
                f"every token must be an integer in [0,{vocabulary_size})",
            )
        tokens.append(item)
    return tuple(tokens)


def _flatten_runtime_values(value: object) -> tuple[float, ...]:
    if isinstance(value, list):
        return tuple(
            scalar
            for item in value
            for scalar in _flatten_runtime_values(item)
        )
    return (float(value),)


class CertifiedTransformer(CertifiedPager):
    """Q36 F3 attention execution with certificate-bound pages, logits, and KV commit."""

    def __init__(
        self,
        cartridge: str | Path,
        plan: object,
        certificate: object,
        evidence: object,
        profile: object,
        page_map: object,
    ):
        super().__init__(cartridge, plan, certificate, evidence, profile, page_map)
        assert isinstance(evidence, dict) and isinstance(profile, dict)
        self._transformer_steps, kv_capacity = _bind_transformer_steps(
            self._steps,
            evidence,
            self._locations,
            self._profile,
            self._certificate_id,
        )
        self._kv = bytearray(kv_capacity)
        self._kv_length = 0
        self.last_transformer: TransformerExecution | None = None

    @property
    def kv_snapshot(self) -> bytes:
        return bytes(self._kv[: self._kv_length])

    async def execute_token(
        self,
        selection: CompiledSelection,
        tokens: object,
        *,
        timeout_seconds: float | None = None,
        cancel_event: asyncio.Event | None = None,
    ) -> TransformerExecution:
        transitions: list[tuple[str, str, str]] = []
        try:
            preview, _, _ = self._validate_selection(selection)
            transformer_step = self._transformer_steps[preview.schedule.step]
            token_values = _runtime_tokens(
                tokens,
                transformer_step.token_count,
                transformer_step.vocabulary_size,
                self._certificate_id,
            )
            step, sample_units, seed, planned_pages, payloads = (
                await self._prepare_execution(
                    selection,
                    timeout_seconds,
                    cancel_event,
                    transitions,
                )
            )
            value_page = (
                transformer_step.exact_value_page
                if step.sampling_kind == "EXACT"
                else dict(transformer_step.sampled_value_pages)[sample_units[0]]
            )
            observed_reads = len(payloads)
            observed_load = sum(len(payload) for payload in payloads.values())
            if (
                observed_reads != step.schedule.page_reads
                or observed_load != step.schedule.load_bytes
            ):
                raise _runtime_error(
                    "CAPABILITY_MISMATCH",
                    step.schedule.operation_id,
                    "Q63: no hidden transformer traffic",
                    "observed page reads or loaded bytes differ from the certified schedule",
                )
            mx, _ = _mlx_runtime()
            _require_runtime(transformer_step.attention_case_id, mx)
            mx.synchronize()
            mx.clear_cache()
            baseline = mx.get_active_memory()
            mx.reset_peak_memory()
            states = {page_digest: "RESIDENT" for page_digest in planned_pages}
            for page_digest in planned_pages:
                _move_page(states, transitions, page_digest, "GPU_SUBMITTED")
            embedding_array = mx.array(
                struct.unpack(
                    f"<{len(payloads[transformer_step.embedding_page]) // 4}f",
                    payloads[transformer_step.embedding_page],
                ),
                dtype=mx.float32,
            ).reshape(transformer_step.embedding_shape)
            query_weight = mx.array(
                struct.unpack(
                    f"<{len(payloads[transformer_step.query_page]) // 4}f",
                    payloads[transformer_step.query_page],
                ),
                dtype=mx.float32,
            ).reshape(transformer_step.projection_shape)
            key_weight = mx.array(
                struct.unpack(
                    f"<{len(payloads[transformer_step.key_page]) // 4}f",
                    payloads[transformer_step.key_page],
                ),
                dtype=mx.float32,
            ).reshape(transformer_step.projection_shape)
            value_weight = mx.array(
                struct.unpack(
                    f"<{len(payloads[value_page]) // 4}f",
                    payloads[value_page],
                ),
                dtype=mx.float32,
            ).reshape(transformer_step.projection_shape)
            token_array = mx.array(token_values, dtype=mx.uint32)
            hidden = dispatch(
                transformer_step.embedding_case_id,
                (embedding_array, token_array),
            )
            query_array = dispatch(
                transformer_step.projection_case_id,
                (hidden, query_weight),
            )
            key_array = dispatch(
                transformer_step.projection_case_id,
                (hidden, key_weight),
            )
            value_array = dispatch(
                transformer_step.projection_case_id,
                (hidden, value_weight),
            )
            key_values = _flatten_runtime_values(key_array.tolist())
            value_values = _flatten_runtime_values(value_array.tolist())
            if self._kv_length:
                prior = self.kv_snapshot[-2 * len(key_values) * 4 :]
                prior_key = struct.unpack(
                    f"<{len(key_values)}f", prior[: len(key_values) * 4]
                )
                prior_value = struct.unpack(
                    f"<{len(value_values)}f", prior[len(key_values) * 4 :]
                )
                row_width = transformer_step.attention_shape[-1]
                key_values = (*prior_key[:row_width], *key_values[row_width:])
                value_values = (*prior_value[:row_width], *value_values[row_width:])
            effective_key = mx.array(key_values, dtype=mx.float32).reshape(
                transformer_step.attention_shape
            )
            effective_value = mx.array(value_values, dtype=mx.float32).reshape(
                transformer_step.attention_shape
            )
            logits_array = dispatch(
                transformer_step.attention_case_id,
                (
                    query_array.reshape(transformer_step.attention_shape),
                    effective_key,
                    effective_value,
                ),
            )
            key_payload = struct.pack(
                f"<{len(key_values)}f",
                *key_values,
            )
            value_payload = struct.pack(
                f"<{len(value_values)}f",
                *value_values,
            )
            logits = _flatten_runtime_values(logits_array.tolist())
            logits_payload = struct.pack(f"<{len(logits)}f", *logits)
            metal_peak = mx.get_peak_memory() - baseline
            runtime_bytes = metal_peak - (
                transformer_step.activation_bytes + transformer_step.model_tensor_bytes
            )
            if runtime_bytes != self._profile["runtime_buffer_bytes"]:
                raise _runtime_error(
                    "MEMORY_BUDGET_EXCEEDED",
                    step.schedule.operation_id,
                    "Q63: no hidden transformer allocation",
                    f"MLX used {runtime_bytes} runtime bytes; the certified trace declares {self._profile['runtime_buffer_bytes']}",
                )
            observed_memory = sum((
                self._profile["cache_bytes"],
                len(self._kv),
                observed_load,
                transformer_step.model_tensor_bytes,
                len(transformer_step.metadata),
                transformer_step.activation_bytes,
                runtime_bytes,
                self._profile["training_window_bytes"],
            ))
            if observed_memory != step.schedule.live_memory_bytes:
                raise _runtime_error(
                    "MEMORY_BUDGET_EXCEEDED",
                    step.schedule.operation_id,
                    "Q63: transformer trace equals certified schedule",
                    f"observed {observed_memory} model bytes; schedule declares {step.schedule.live_memory_bytes}",
                )
            kv_end = self._kv_length + len(key_payload) + len(value_payload)
            if kv_end > len(self._kv):
                raise _runtime_error(
                    "MEMORY_BUDGET_EXCEEDED",
                    self._certificate_id,
                    "Q36/Q63: KV horizon reservation",
                    "the next recurrent commit exceeds the admitted KV extent",
                )
            for page_digest in planned_pages:
                _move_page(states, transitions, page_digest, "RECLAIMABLE")
            page_execution = PageExecution(
                mode="COMPILED_CERTIFIED_TRANSFORMER",
                step=step.schedule.step,
                certificate_digest=self._certificate_id,
                planned_pages=planned_pages,
                sample_units=sample_units,
                execution_seed=seed,
                output_digest=_execution_digest(
                    "COMPILED_CERTIFIED_TRANSFORMER",
                    planned_pages,
                    payloads,
                    atom_id=step.schedule.atom_id,
                    sample_units=sample_units,
                ),
                transitions=tuple(transitions),
            )
            self._kv[self._kv_length:kv_end] = key_payload + value_payload
            self._kv_length = kv_end
            trace = TransformerTrace(
                phase="PREFILL" if step.schedule.step == 0 else "DECODE",
                schedule=step.schedule,
                planned_pages=planned_pages,
                operator_cases=(
                    transformer_step.embedding_case_id,
                    transformer_step.projection_case_id,
                    transformer_step.projection_case_id,
                    transformer_step.projection_case_id,
                    transformer_step.attention_case_id,
                ),
                page_reads=observed_reads,
                load_bytes=observed_load,
                model_tensor_bytes=transformer_step.model_tensor_bytes,
                activation_bytes=transformer_step.activation_bytes,
                kv_reserved_bytes=len(self._kv),
                runtime_buffer_bytes=runtime_bytes,
                model_memory_bytes=observed_memory,
                metal_peak_bytes=metal_peak,
            )
            committed = TransformerExecution(
                page_execution=page_execution,
                logits=logits,
                logits_digest=digest_bytes(logits_payload),
                kv_digest=digest_bytes(self.kv_snapshot),
                kv_bytes=self._kv_length,
                trace=trace,
            )
            self.last_committed = page_execution
            self.last_transformer = committed
            self._next_step += 1
            self.replay_selection = None
            return committed
        finally:
            self.last_attempt_transitions = tuple(transitions)
