# pager.py — bounded mathematical-plan validation and pinned MLX dispatch (Q30/Q33/Q40); depends on errors.py, schema.
"""Validate compiled-plan data before allocation and execute only generated MLX dispatch cases."""

from __future__ import annotations

import importlib.metadata
import platform
from collections.abc import Sequence

import mlx.core as mx
import mlx.optimizers as optim

from errors import CassetteError
from schema.tables import DISPATCH_ROWS, MLX_RUNTIME, OPERATOR_DISPATCH, Q40_MODES
from schema.validator import validate

_CASES = {row["case_id"]: row for row in DISPATCH_ROWS}


def _error(code: str, object_id: str, invariant: str, detail: str) -> CassetteError:
    return CassetteError(code, object_id, invariant, "terminal", detail)


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


def _require_runtime(case_id: str) -> None:
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


def _matmul(values: Sequence[mx.array], _: dict) -> mx.array:
    return mx.matmul(values[0], values[1])


def _quantized_matmul(values: Sequence[mx.array], parameters: dict) -> mx.array:
    return mx.quantized_matmul(values[0], values[1], values[2], values[3], **parameters)


def _norm(values: Sequence[mx.array], parameters: dict) -> mx.array:
    return mx.fast.rms_norm(values[0], values[1], parameters["eps"])


def _rope(values: Sequence[mx.array], parameters: dict) -> mx.array:
    return mx.fast.rope(values[0], **parameters)


def _attention(values: Sequence[mx.array], parameters: dict) -> mx.array:
    return mx.fast.scaled_dot_product_attention(values[0], values[1], values[2], **parameters)


def _convolution(values: Sequence[mx.array], parameters: dict) -> mx.array:
    return mx.conv1d(values[0], values[1], **parameters)


def _embedding(values: Sequence[mx.array], parameters: dict) -> mx.array:
    return mx.take(values[0], values[1], **parameters)


def _sampling(values: Sequence[mx.array], parameters: dict) -> mx.array:
    return mx.random.categorical(values[0], key=values[1], **parameters)


def _autograd(values: Sequence[mx.array], _: dict) -> mx.array:
    return mx.grad(mx.sum)(values[0])


def _optimizer(values: Sequence[mx.array], parameters: dict) -> mx.array:
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


def dispatch(case_id: str, inputs: Sequence[mx.array]) -> mx.array:
    """Q30: execute one exact generated dtype, shape, operator, and parameter tuple."""
    row = _CASES.get(case_id)
    if row is None:
        raise _error(
            "UNSUPPORTED_OPERATOR",
            case_id or "operator-case",
            "Q30: generated operator dispatch",
            "case is absent from the pinned dispatch table",
        )
    _require_runtime(case_id)
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
