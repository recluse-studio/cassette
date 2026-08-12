# trainer.py — paged immutable delta training and compiled recovery artifacts (Q21-Q25/Q70-Q73); depends on errors.py, schema, store.py.
"""Train bounded BF16 or FP32 adapters or certificate-recovery tensors and publish one child."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import importlib.metadata
import json
import math
import platform
import struct

from errors import CassetteError
from schema.tables import DISPATCH_ROWS, MLX_RUNTIME
from store import (
    PAGE_BYTES,
    PageLocation,
    TransactionContext,
    append_staged_training_delta,
    canonical_bytes,
    commit_generation,
    digest_bytes,
    load_root,
    page_locations,
    pin_generation,
    read_training_page,
    stage_training_pages,
)

_VERSION = "cassette-training-v1"
_TENSOR_VERSION = "cassette-training-tensor-v1"
_TRACE_VERSION = "cassette-training-trace-v1"
_TIER_A = (
    "ADAPTER_SFT",
    "ADAPTER_CONTINUED_PRETRAINING",
    "OFFLINE_ADAPTER_DPO",
)
_TIER_B = "COMPILED_RECOVERY"
_OBJECTIVE_SPECS = {
    "ADAPTER_SFT": ("instruction_response", 10, (5, 2), "mean_squared_error"),
    "ADAPTER_CONTINUED_PRETRAINING": ("causal_continuation", 10, (5, 2), "mean_squared_error"),
    "OFFLINE_ADAPTER_DPO": ("preference_pair", 7, (7, 1), "pairwise_logistic"),
    "COMPILED_RECOVERY": ("certificate_recovery", 10, (5, 2), "calibration_mean_squared_error"),
}
_CALIBRATION_KINDS = (
    "condition",
    "atom",
    "description",
    "estimator",
    "observation",
    "precision",
)
_MSE_CASE = "mlx.autograd_lora_mse.f32.rank1.2x3_3x2"
_DPO_CASE = "mlx.autograd_lora_dpo.f32.rank1.2x3_3x2"
_RECOVERY_CASE = "mlx.autograd_calibration_mse.f32.1_2x3_3x2_2x2_1"
_OPTIMIZER_CASE = "mlx.sgd.f32.3"
_RECOVERY_OPTIMIZER_CASE = "mlx.sgd.f32.1"
_TRAINING_CASES = {
    "ADAPTER_SFT": (_MSE_CASE, _OPTIMIZER_CASE),
    "ADAPTER_CONTINUED_PRETRAINING": (_MSE_CASE, _OPTIMIZER_CASE),
    "OFFLINE_ADAPTER_DPO": (_DPO_CASE, _OPTIMIZER_CASE),
    "COMPILED_RECOVERY": (_RECOVERY_CASE, _RECOVERY_OPTIMIZER_CASE),
}
_CASES = {row["case_id"]: row for row in DISPATCH_ROWS}
_FLOATS = struct.Struct("<6f")
_BASE_VALUES = struct.Struct("<6b")
_INITIAL_ADAPTER = (0.25, -0.5, 0.75, 0.0, 0.0, 0.0)
_DELTA_PRECISIONS = frozenset({"BF16", "FP32"})
_HEX = frozenset("0123456789abcdef")
_MAX_PARAMETERS = 256
_MAX_STEPS = 4096
_MAX_UPDATES = 32768
_MAX_SAFE_INTEGER = 2**53 - 1
_MANIFEST_FIELDS = frozenset({
    "format", "job_id", "tier", "operation", "parent_root", "parent_identity",
    "parent_certificate_digest", "base_precision", "delta_precision", "operator_cases",
    "adapter_rank", "adapter_scale",
    "step", "total_steps", "optimizer_step", "data_cursor", "random_seed", "rng_counter",
    "window_limit_bytes", "declared_peak_bytes", "base_pages", "delta_pages",
    "objective_pages", "calibration_pages", "state_pages", "trace_pages", "master_pages",
})
_MLX = None


@dataclass(frozen=True, slots=True)
class TrainingCheckpoint:
    """One durable non-callable work root and its exact restart coordinates."""

    job_id: str
    parent_root: str
    work_root: str
    manifest_digest: str
    step: int
    total_steps: int


@dataclass(frozen=True, slots=True)
class TrainingResult:
    """One Q73 child and the committed training artifact that produced it."""

    generation: int
    child_id: str
    root_digest: str
    delta_id: str
    artifact_digest: str
    operation: str

    @property
    def committed_boundary(self) -> str:
        return self.child_id

    def record(self) -> dict:
        """Return the exact broker-safe committed result."""

        return {
            "generation": self.generation,
            "child_id": self.child_id,
            "root_digest": self.root_digest,
            "delta_id": self.delta_id,
            "artifact_digest": self.artifact_digest,
            "operation": self.operation,
            "committed_boundary": self.committed_boundary,
        }


def _reject(code: str, object_id: str, detail: str, invariant: str = "Q21-Q25/Q70-Q73: paged immutable training") -> None:
    raise CassetteError(code, str(object_id), invariant, "terminal", detail)


def _record(value: object, fields: frozenset[str] | set[str], object_id: str, label: str) -> dict:
    if not isinstance(value, dict) or set(value) != fields:
        observed = sorted(value) if isinstance(value, dict) else type(value).__name__
        _reject("ROOT_INVALID", object_id, f"{label} requires exactly {sorted(fields)}; received {observed}")
    return value


def _text(value: object, object_id: str, label: str, maximum: int = 256) -> str:
    if (
        not isinstance(value, str)
        or not 0 < len(value) <= maximum
        or value != value.strip()
        or any(ord(character) < 32 or ord(character) == 127 for character in value)
    ):
        _reject("ROOT_INVALID", object_id, f"{label} must be exact bounded text")
    return value


def _digest(value: object, object_id: str, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 71
        or not value.startswith("blake3:")
        or not set(value[7:]) <= _HEX
    ):
        _reject("ROOT_INVALID", object_id, f"{label} must be one lowercase BLAKE3 digest")
    return value


def _counter(value: object, object_id: str, label: str, *, positive: bool = False) -> int:
    floor = 1 if positive else 0
    if type(value) is not int or not floor <= value <= _MAX_SAFE_INTEGER:
        _reject("ROOT_INVALID", object_id, f"{label} must be an exact bounded integer")
    return value


def _base_codec(precision: object, object_id: str) -> dict:
    """Parse the explicit F1 base codec from the immutable precision identity."""

    value = _text(precision, object_id, "base precision")
    parts = value.split(";")
    if not parts or parts[0] != "i8-symmetric" or len(parts) != 3:
        _reject(
            "TRAINING_UNSUPPORTED",
            object_id,
            "S21 requires an explicit i8-symmetric scale and zero-point codec",
        )
    fields = {}
    for part in parts[1:]:
        name, separator, item = part.partition("=")
        if not separator or name in fields or name not in {"scale", "zero_point"}:
            _reject("TRAINING_UNSUPPORTED", object_id, "base quantization codec fields are malformed")
        fields[name] = item
    try:
        scale = Decimal(fields.get("scale", ""))
        zero_point = int(fields.get("zero_point", ""))
    except (InvalidOperation, TypeError, ValueError):
        _reject("TRAINING_UNSUPPORTED", object_id, "base quantization codec values are malformed")
    if (
        not scale.is_finite()
        or scale <= 0
        or not math.isfinite(float(scale))
        or str(zero_point) != fields["zero_point"]
        or not -128 <= zero_point <= 127
    ):
        _reject("TRAINING_UNSUPPORTED", object_id, "base quantization codec values are unsupported")
    return {"name": "i8-symmetric", "scale": fields["scale"], "zero_point": zero_point}


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def _decode(payload: bytes, object_id: str, label: str) -> dict:
    try:
        value = json.loads(payload, object_pairs_hook=_unique_object)
        if canonical_bytes(value) != payload:
            raise ValueError("record is not canonical RFC 8785 JSON")
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, CassetteError) as error:
        _reject("ROOT_INVALID", object_id, f"{label} is malformed: {error}")
    if not isinstance(value, dict):
        _reject("ROOT_INVALID", object_id, f"{label} must be one object")
    return value


def _f32(values: object, count: int, object_id: str, label: str) -> bytes:
    if (
        not isinstance(values, tuple)
        or len(values) != count
        or any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in values)
        or any(not math.isfinite(float(value)) for value in values)
    ):
        _reject("INVALID_REQUEST", object_id, f"{label} requires {count} finite numeric values")
    codec = struct.Struct(f"<{count}f")
    try:
        payload = codec.pack(*(float(value) for value in values))
    except (OverflowError, struct.error) as error:
        _reject("INVALID_REQUEST", object_id, f"{label} is outside FP32: {error}")
    if any(not math.isfinite(value) for value in codec.unpack(payload)):
        _reject("GRADIENT_INVALID", object_id, f"{label} becomes non-finite in FP32")
    return payload


def _bf16(values: tuple[float, ...]) -> bytes:
    encoded = []
    for value in values:
        bits = struct.unpack("<I", struct.pack("<f", value))[0]
        encoded.append((bits + 0x7FFF + ((bits >> 16) & 1)) >> 16)
    return struct.pack(f"<{len(encoded)}H", *encoded)


def _numeric_payload(values: tuple[float, ...], precision: str) -> bytes:
    return struct.pack(f"<{len(values)}f", *values) if precision == "FP32" else _bf16(values)


def _tensor_page(
    role: str,
    tensor_id: str,
    shape: tuple[int, ...],
    payload: bytes,
    dtype: str = "float32",
) -> bytes:
    return canonical_bytes({
        "format": _TENSOR_VERSION,
        "role": role,
        "tensor_id": tensor_id,
        "dtype": dtype,
        "shape": list(shape),
        "payload_hex": payload.hex(),
    })


def _tensor_values(
    payload: bytes,
    object_id: str,
    role: str,
    tensor_id: str,
    shape: tuple[int, ...],
    precision: str = "FP32",
) -> tuple[float, ...]:
    page = _record(
        _decode(payload, object_id, f"{role} tensor page"),
        {"format", "role", "tensor_id", "dtype", "shape", "payload_hex"},
        object_id,
        f"{role} tensor page",
    )
    encoded = page["payload_hex"]
    count = math.prod(shape)
    expected_dtype = "float32" if precision == "FP32" else "bfloat16"
    expected_bytes = count * (4 if precision == "FP32" else 2)
    if (
        page["format"] != _TENSOR_VERSION
        or page["role"] != role
        or page["tensor_id"] != tensor_id
        or page["dtype"] != expected_dtype
        or page["shape"] != list(shape)
        or not isinstance(encoded, str)
        or len(encoded) != 2 * expected_bytes
        or not set(encoded) <= _HEX
    ):
        _reject("ROOT_INVALID", object_id, f"{role} tensor page disagrees with its declared tuple")
    raw = bytes.fromhex(encoded)
    if precision == "FP32":
        values = struct.unpack(f"<{count}f", raw)
    else:
        values = tuple(
            struct.unpack("<f", struct.pack("<I", value << 16))[0]
            for value in struct.unpack(f"<{count}H", raw)
        )
    if any(not math.isfinite(value) for value in values):
        _reject("GRADIENT_INVALID", object_id, f"{role} tensor contains NaN or infinity")
    if role == "adapter" and (len(values) != 6 or values[5] != 0.0):
        _reject("GRADIENT_INVALID", object_id, "rank-one adapter padding must remain exact zero")
    return values


def _objective_page(operation: str, step: int, values: object, object_id: str) -> bytes:
    role, count, shape, _ = _OBJECTIVE_SPECS[operation]
    return _tensor_page(role, f"batch:{step}", shape, _f32(values, count, object_id, f"batch {step}"))


def _objective_values(payload: bytes, operation: str, step: int, object_id: str) -> tuple[float, ...]:
    role, _, shape, _ = _OBJECTIVE_SPECS[operation]
    return _tensor_values(payload, object_id, role, f"batch:{step}", shape)


def _calibrations(records: object, object_id: str, tier: str) -> tuple[dict, ...]:
    if not isinstance(records, tuple) or len(records) > len(_CALIBRATION_KINDS):
        _reject("INVALID_REQUEST", object_id, "calibration records must be one bounded tuple")
    normalized = []
    for item in records:
        row = _record(
            item,
            {"kind", "input_digest", "output_digest", "sample_count", "loss"},
            object_id,
            "calibration record",
        )
        kind = _text(row["kind"], object_id, "calibration kind")
        _digest(row["input_digest"], object_id, f"{kind} input digest")
        _digest(row["output_digest"], object_id, f"{kind} output digest")
        _counter(row["sample_count"], object_id, f"{kind} sample count", positive=True)
        if not isinstance(row["loss"], str) or not 0 < len(row["loss"]) <= 64:
            _reject("INVALID_REQUEST", object_id, f"{kind} loss must be bounded decimal text")
        try:
            loss = Decimal(row["loss"])
        except (InvalidOperation, TypeError, ValueError):
            _reject("INVALID_REQUEST", object_id, f"{kind} loss must be finite nonnegative decimal text")
        if not loss.is_finite() or loss < 0:
            _reject("INVALID_REQUEST", object_id, f"{kind} loss must be finite nonnegative decimal text")
        normalized.append(dict(row))
    normalized.sort(key=lambda row: _CALIBRATION_KINDS.index(row["kind"]) if row["kind"] in _CALIBRATION_KINDS else len(_CALIBRATION_KINDS))
    kinds = tuple(row["kind"] for row in normalized)
    expected = _CALIBRATION_KINDS if tier == "B" else ()
    if kinds != expected:
        _reject(
            "TRAINING_UNSUPPORTED",
            object_id,
            f"Tier {tier} requires calibration kinds {list(expected)}; received {list(kinds)}",
        )
    return tuple(normalized)


def _compiled_certificate(parent: dict, object_id: str) -> str:
    plans = parent["plans"]
    if not isinstance(plans, list) or not plans or not isinstance(plans[0], dict):
        _reject("TRAINING_UNSUPPORTED", object_id, "Tier B requires one compiled preparation bundle")
    certificate = plans[0].get("certificate")
    if not isinstance(certificate, dict) or "certificate_id" not in certificate:
        _reject("TRAINING_UNSUPPORTED", object_id, "Tier B parent lacks a Q19 certificate")
    return _digest(certificate["certificate_id"], object_id, "parent Q19 certificate")


def _runtime():
    global _MLX
    if _MLX is None:
        import mlx.core as mx
        import mlx.optimizers as optim

        required = MLX_RUNTIME["package"].split("==", 1)[1]
        observed = importlib.metadata.version("mlx")
        if observed != required:
            _reject("CAPABILITY_MISMATCH", "trainer:mlx", f"requires MLX {required}; found {observed}")
        if platform.system() != "Darwin" or platform.machine() != "arm64" or not mx.metal.is_available():
            _reject("CAPABILITY_MISMATCH", "trainer:mlx", "training requires arm64 macOS with MLX Metal")
        _MLX = mx, optim
    return _MLX


def _case(case_id: str, operator: str, inputs: list[list[int]], output: list[int]) -> dict:
    row = _CASES.get(case_id)
    if (
        row is None
        or row["operator"] != operator
        or row["input_dtypes"] != ["float32"] * len(inputs)
        or row["input_shapes"] != inputs
        or row["output_dtype"] != "float32"
        or row["output_shape"] != output
    ):
        _reject("UNSUPPORTED_OPERATOR", case_id, "generated Q30 training case is absent or changed")
    return row


def _update_delta(
    parameter_values: tuple[float, ...],
    base_payload: bytes,
    base_codec: dict,
    objective_values: tuple[float, ...],
    calibration_loss: float | None,
    operation: str,
    precision: str,
    object_id: str,
) -> tuple[bytes, dict]:
    loss_case, optimizer_case = _TRAINING_CASES[operation]
    expected_loss = _OBJECTIVE_SPECS[operation][3]
    if operation == _TIER_B:
        loss_inputs = [[1], [2, 3], [3, 2], [2, 2], [1]]
        output_shape = [1]
        expected_parameters = {"loss": expected_loss}
        optimizer_shape = [[1], [1]]
    else:
        loss_inputs = (
            [[2, 3], [2, 3], [3, 2], [1]]
            if loss_case == _DPO_CASE
            else [[2, 3], [2, 3], [3, 2], [2, 2]]
        )
        output_shape = [2, 3]
        expected_parameters = {
            "adapter_rank": 1,
            "adapter_scale": 1.0,
            "loss": expected_loss,
        }
        optimizer_shape = [[3], [3]]
    loss_row = _case(loss_case, "autograd", loss_inputs, output_shape)
    if loss_row["parameters"] != expected_parameters:
        _reject("UNSUPPORTED_OPERATOR", loss_case, "generated autograd parameters changed")
    optimizer_row = _case(optimizer_case, "optimizer", optimizer_shape, optimizer_shape[0])
    if optimizer_row["parameters"] != {"learning_rate": 0.25}:
        _reject("UNSUPPORTED_OPERATOR", optimizer_case, "generated optimizer parameters changed")
    if len(base_payload) != _BASE_VALUES.size:
        _reject("ROOT_INVALID", object_id, "frozen base page is not one I8 2x3 parameter window")
    base_values = _BASE_VALUES.unpack(base_payload)
    expected_objective = _OBJECTIVE_SPECS[operation][1]
    if len(objective_values) != expected_objective:
        _reject("ROOT_INVALID", object_id, "operation batch has the wrong numerical arity")
    if operation == _TIER_B and (
        calibration_loss is None or not math.isfinite(calibration_loss) or calibration_loss < 0
    ):
        _reject("ROOT_INVALID", object_id, "compiled recovery lacks one finite calibration target")
    if operation != _TIER_B and calibration_loss is not None:
        _reject("ROOT_INVALID", object_id, "Tier A cannot consume compiled calibration evidence")
    mx, optim = _runtime()
    try:
        mx.synchronize()
        mx.clear_cache()
        active_before = mx.get_active_memory()
        mx.reset_peak_memory()
        parameter_shape = (1,) if operation == _TIER_B else (2, 3)
        parameter = mx.array(parameter_values, dtype=mx.float32).reshape(parameter_shape)
        quantized = mx.array(base_values, dtype=mx.int8).reshape((2, 3))
        base = mx.multiply(
            mx.subtract(
                quantized.astype(mx.float32),
                mx.array(base_codec["zero_point"], dtype=mx.float32),
            ),
            mx.array(float(Decimal(base_codec["scale"])), dtype=mx.float32),
        )
        inputs = mx.array(objective_values[:6], dtype=mx.float32).reshape((3, 2))

        if operation == _TIER_B:
            target_values = mx.array(objective_values[6:], dtype=mx.float32).reshape((2, 2))
            calibration_value = mx.array([calibration_loss], dtype=mx.float32)

            def loss(value):
                prediction = mx.add(mx.mean(mx.matmul(base, inputs)), value[0])
                expected = mx.add(mx.mean(target_values), calibration_value[0])
                residual = mx.subtract(prediction, expected)
                return mx.multiply(residual, residual)
        else:
            def effective(value):
                factor_a = value[0:1, :]
                factor_b = value[1, :2].reshape((2, 1))
                return mx.add(
                    base,
                    mx.multiply(
                        loss_row["parameters"]["adapter_scale"], mx.matmul(factor_b, factor_a)
                    ),
                )

        if operation == "OFFLINE_ADAPTER_DPO":
            target_values = mx.array([objective_values[6]], dtype=mx.float32)

            def loss(value):
                scores = mx.matmul(effective(value), inputs)
                margin = mx.subtract(
                    mx.subtract(mx.sum(scores[:, 0]), mx.sum(scores[:, 1])), target_values[0]
                )
                return mx.logaddexp(
                    mx.array(0.0, dtype=mx.float32), mx.negative(margin)
                )
        elif operation != _TIER_B:
            target_values = mx.array(objective_values[6:], dtype=mx.float32).reshape((2, 2))

            def loss(value):
                residual = mx.subtract(mx.matmul(effective(value), inputs), target_values)
                return mx.mean(mx.multiply(residual, residual))

        loss_value, gradient = mx.value_and_grad(loss)(parameter)
        optimizer = optim.SGD(**optimizer_row["parameters"])
        if operation == _TIER_B:
            updated = optimizer.apply_gradients(
                {"parameter": gradient}, {"parameter": parameter}
            )["parameter"]
            mx.eval(loss_value, gradient, updated)
            values = tuple(float(value) for value in updated.tolist())
            rows = ()
        else:
            rows = tuple(
                optimizer.apply_gradients(
                    {"parameter": gradient[index]}, {"parameter": parameter[index]}
                )["parameter"]
                for index in range(2)
            )
            mx.eval(loss_value, gradient, *rows)
            values = tuple(float(value) for row in rows for value in row.tolist())
            updated = None
        loss_hex = struct.pack("<f", float(loss_value.item())).hex()
        peak_delta = mx.get_peak_memory() - active_before
        parameter = quantized = base = inputs = target_values = gradient = None
        loss_value = optimizer = rows = updated = loss = None
        if operation == _TIER_B:
            calibration_value = None
        else:
            effective = None
        mx.synchronize()
        mx.clear_cache()
        active_after = mx.get_active_memory()
    except CassetteError:
        raise
    except Exception as error:
        _reject("GRADIENT_INVALID", object_id, f"pinned MLX update failed: {type(error).__name__}: {error}")
    if (
        any(not math.isfinite(value) for value in values)
        or len(values) != (1 if operation == _TIER_B else 6)
        or (operation != _TIER_B and values[5] != 0.0)
    ):
        _reject("GRADIENT_INVALID", object_id, "pinned MLX update produced a non-finite or malformed delta")
    role = "certificate_recovery" if operation == _TIER_B else "adapter"
    shape = (1,) if operation == _TIER_B else (2, 3)
    stored_values = _tensor_values(
        _tensor_page(
            role,
            object_id,
            shape,
            _numeric_payload(values, precision),
            "float32" if precision == "FP32" else "bfloat16",
        ),
        object_id,
        role,
        object_id,
        shape,
        precision,
    )
    return _numeric_payload(stored_values, precision), {
        "parameter_id": object_id,
        "active_before_bytes": active_before,
        "peak_delta_bytes": peak_delta,
        "active_after_bytes": active_after,
        "loss_hex": loss_hex,
    }


def _state_pages(
    job_id: str,
    step: int,
    delta_pages: list[dict],
    optimizer_case: str,
) -> tuple[bytes, bytes, bytes]:
    optimizer = canonical_bytes({
        "format": _VERSION,
        "role": "optimizer",
        "case_id": optimizer_case,
        "learning_rate": "0.25",
        "step": step,
    })
    rng = canonical_bytes({
        "format": _VERSION,
        "role": "rng",
        "algorithm": "counter-v1",
        "job_id": job_id,
        "counter": step,
    })
    journal = canonical_bytes({
        "format": _VERSION,
        "role": "journal",
        "job_id": job_id,
        "step": step,
        "status": "PREPARED" if step == 0 else "STEP_COMPLETE",
        "ordered_delta_pages": [row["page_digest"] for row in delta_pages],
    })
    return optimizer, rng, journal


def _rows(value: object, fields: set[str], maximum: int, object_id: str, label: str) -> list[dict]:
    if not isinstance(value, list) or not 0 < len(value) <= maximum:
        _reject("ROOT_INVALID", object_id, f"{label} must be one bounded nonempty list")
    return [_record(item, fields, object_id, label) for item in value]


def _manifest_shape(manifest: object, object_id: str) -> dict:
    value = _record(manifest, _MANIFEST_FIELDS, object_id, "training manifest")
    if value["format"] != _VERSION:
        _reject("ROOT_INVALID", object_id, "training manifest version is unsupported")
    for field in ("job_id", "parent_root", "parent_identity"):
        _digest(value[field], object_id, field)
    operation = _text(value["operation"], object_id, "operation")
    tier = value["tier"]
    expected_tier = "A" if operation in _TIER_A else "B" if operation == _TIER_B else None
    if expected_tier is None or tier != expected_tier:
        _reject("ROOT_INVALID", object_id, "operation and training tier disagree")
    certificate = value["parent_certificate_digest"]
    if (tier == "B") != (certificate is not None):
        _reject("ROOT_INVALID", object_id, "Tier B alone requires a parent certificate digest")
    if certificate is not None:
        _digest(certificate, object_id, "parent certificate digest")
    base_codec = _base_codec(value["base_precision"], object_id)
    if (
        value["delta_precision"] not in _DELTA_PRECISIONS
        or value["operator_cases"] != list(_TRAINING_CASES[operation])
    ):
        _reject("ROOT_INVALID", object_id, "delta precision or generated operator cases changed")
    expected_adapter = (1, "1") if tier == "A" else (None, None)
    if (value["adapter_rank"], value["adapter_scale"]) != expected_adapter:
        _reject("ROOT_INVALID", object_id, "adapter geometry and training tier disagree")
    step = _counter(value["step"], object_id, "step")
    total = _counter(value["total_steps"], object_id, "total steps", positive=True)
    if total > _MAX_STEPS or step > total:
        _reject("ROOT_INVALID", object_id, "training step lies outside its bounded horizon")
    if value["optimizer_step"] != step or value["data_cursor"] != step or value["rng_counter"] != step:
        _reject("ROOT_INVALID", object_id, "optimizer, data, RNG, and checkpoint cursors disagree")
    _counter(value["random_seed"], object_id, "random seed")
    limit = _counter(value["window_limit_bytes"], object_id, "window limit", positive=True)
    peak = _counter(value["declared_peak_bytes"], object_id, "declared peak")
    if peak > limit:
        _reject("MEMORY_BUDGET_EXCEEDED", object_id, "declared tensor peak exceeds the admitted window")
    base = _rows(
        value["base_pages"],
        {
            "parameter_id", "tensor_id", "page_digest", "tensor_digest",
            "dtype", "shape", "offset", "length", "codec",
        },
        _MAX_PARAMETERS,
        object_id,
        "base page",
    )
    delta = _rows(value["delta_pages"], {"parameter_id", "page_digest"}, _MAX_PARAMETERS, object_id, "delta page")
    base_ids = [_text(row["parameter_id"], object_id, "base parameter id") for row in base]
    delta_ids = [_text(row["parameter_id"], object_id, "parameter id") for row in delta]
    expected_delta_ids = (
        base_ids if tier == "A" else [f"recovery.{kind}" for kind in _CALIBRATION_KINDS]
    )
    if (
        base_ids != sorted(set(base_ids))
        or delta_ids != expected_delta_ids
        or (tier == "B" and len(base) != 1)
    ):
        _reject("ROOT_INVALID", object_id, "base and trainable parameter catalogs disagree with the tier")
    for row in (*base, *delta):
        _digest(row["page_digest"], object_id, "parameter page digest")
    for row in base:
        _text(row["tensor_id"], object_id, "base tensor id")
        _digest(row["tensor_digest"], object_id, "base tensor digest")
        if (
            row["dtype"] != "I8"
            or row["shape"] != [2, 3]
            or row["codec"] != base_codec
        ):
            _reject("TRAINING_UNSUPPORTED", object_id, "frozen base window must be one declared I8 2x3 tensor")
        _counter(row["offset"], object_id, "base tensor page offset")
        if row["length"] != _BASE_VALUES.size:
            _reject("TRAINING_UNSUPPORTED", object_id, "frozen base tensor length must be six bytes")
    if len({row["page_digest"] for row in base}) != len(base):
        _reject("ROOT_INVALID", object_id, "one frozen base page may enter the update order only once")
    objectives = _rows(value["objective_pages"], {"step", "page_digest"}, _MAX_STEPS, object_id, "objective page")
    if [row["step"] for row in objectives] != list(range(total)):
        _reject("ROOT_INVALID", object_id, "objective page order must cover every step exactly once")
    for row in objectives:
        _digest(row["page_digest"], object_id, "objective page digest")
    calibrations = value["calibration_pages"]
    if not isinstance(calibrations, list) or len(calibrations) > len(_CALIBRATION_KINDS):
        _reject("ROOT_INVALID", object_id, "calibration page list is unbounded")
    calibration_rows = [
        _record(row, {"kind", "page_digest"}, object_id, "calibration page")
        for row in calibrations
    ]
    expected_kinds = list(_CALIBRATION_KINDS) if tier == "B" else []
    if [row["kind"] for row in calibration_rows] != expected_kinds:
        _reject("ROOT_INVALID", object_id, "calibration page kinds do not match the training tier")
    for row in calibration_rows:
        _digest(row["page_digest"], object_id, "calibration page digest")
    states = _record(value["state_pages"], {"optimizer", "rng", "journal"}, object_id, "state pages")
    for digest in states.values():
        _digest(digest, object_id, "state page digest")
    traces = value["trace_pages"]
    if not isinstance(traces, list) or len(traces) != step or len(traces) > _MAX_STEPS:
        _reject("ROOT_INVALID", object_id, "trace pages must cover each completed step exactly once")
    for digest in traces:
        _digest(digest, object_id, "trace page digest")
    if value["master_pages"] != [] or len(delta) * total > _MAX_UPDATES:
        _reject("TRAINING_UNSUPPORTED", object_id, "hidden masters or an unbounded update schedule are forbidden")
    return value


def _base_payload(cartridge, parent_root: str, row: dict) -> bytes:
    root = load_root(cartridge, parent_root)
    matches = [
        tensor
        for tensor in root["tensor_maps"]
        if tensor["semantic_tensor_id"] == row["tensor_id"]
    ]
    expected_span = {
        "page_digest": row["page_digest"],
        "offset": row["offset"],
        "length": row["length"],
        "tensor_offset": 0,
    }
    if (
        len(matches) != 1
        or matches[0]["dtype"] != row["dtype"]
        or matches[0]["shape"] != row["shape"]
        or matches[0]["spans"] != [expected_span]
    ):
        _reject("ROOT_INVALID", row["parameter_id"], "base parameter tuple disagrees with the parent tensor map")
    page = read_training_page(cartridge, parent_root, row["page_digest"])
    payload = page[row["offset"]:row["offset"] + row["length"]]
    if len(payload) != _BASE_VALUES.size or digest_bytes(payload) != row["tensor_digest"]:
        _reject("PAGE_CORRUPT", row["parameter_id"], "frozen quantized tensor bytes changed")
    return payload


def _ordered_pages(manifest: dict, manifest_digest: str) -> list[str]:
    ordered = [manifest_digest]
    ordered.extend(row["page_digest"] for row in manifest["delta_pages"])
    ordered.extend(row["page_digest"] for row in manifest["objective_pages"])
    ordered.extend(row["page_digest"] for row in manifest["calibration_pages"])
    ordered.extend(manifest["state_pages"][name] for name in ("optimizer", "rng", "journal"))
    ordered.extend(manifest["trace_pages"])
    return ordered


def _checkpoint(manifest: dict, work_root: str, manifest_digest: str) -> TrainingCheckpoint:
    return TrainingCheckpoint(
        manifest["job_id"],
        manifest["parent_root"],
        work_root,
        manifest_digest,
        manifest["step"],
        manifest["total_steps"],
    )


def _validate_state(cartridge, work_root: str, manifest: dict) -> None:
    job_id = manifest["job_id"]
    step = manifest["step"]
    optimizer, rng, journal = _state_pages(
        job_id,
        step,
        manifest["delta_pages"],
        manifest["operator_cases"][1],
    )
    expected = {"optimizer": optimizer, "rng": rng, "journal": journal}
    for name, payload in expected.items():
        observed = read_training_page(cartridge, work_root, manifest["state_pages"][name])
        if observed != payload:
            _reject("ROOT_INVALID", job_id, f"{name} state page disagrees with the checkpoint")


def _validate_trace(payload: bytes, manifest: dict, ordinal: int) -> int:
    object_id = manifest["job_id"]
    trace = _record(
        _decode(payload, object_id, "tensor lifetime trace"),
        {
            "format", "role", "job_id", "step", "parameter_order", "events",
            "logical_peak_bytes", "mlx_windows", "peak_um_bytes",
        },
        object_id,
        "tensor lifetime trace",
    )
    parameter_order = [row["parameter_id"] for row in manifest["delta_pages"]]
    if (
        trace["format"] != _TRACE_VERSION
        or trace["role"] != "tensor_lifetime"
        or trace["job_id"] != object_id
        or trace["step"] != ordinal
        or trace["parameter_order"] != parameter_order
        or not isinstance(trace["events"], list)
        or not trace["events"]
    ):
        _reject("ROOT_INVALID", object_id, "tensor lifetime trace binding is malformed")
    live = {}
    peak = 0
    persisted = []
    for sequence, raw in enumerate(trace["events"]):
        event = _record(
            raw,
            {"sequence", "action", "tensor_id", "location", "bytes", "page_digest"},
            object_id,
            "tensor lifetime event",
        )
        tensor_id = _text(event["tensor_id"], object_id, "trace tensor id")
        size = _counter(event["bytes"], object_id, "trace bytes", positive=True)
        action = event["action"]
        if event["sequence"] != sequence or event["location"] not in {"D", "UM"}:
            _reject("ROOT_INVALID", object_id, "tensor lifetime event order or location is invalid")
        if event["page_digest"] is not None:
            _digest(event["page_digest"], object_id, "trace page digest")
        if action in {"LOAD", "PRODUCE"}:
            if event["location"] != "UM" or tensor_id in live:
                _reject("ROOT_INVALID", object_id, "tensor entered unified memory twice or at the wrong location")
            live[tensor_id] = size
            peak = max(peak, sum(live.values()))
        elif action == "PERSIST":
            if event["location"] != "D" or tensor_id not in live or event["page_digest"] is None:
                _reject("ROOT_INVALID", object_id, "only a live tensor may persist to a named drive page")
            persisted.append(tensor_id)
        elif action == "RETIRE":
            if event["location"] != "UM" or live.pop(tensor_id, None) is None:
                _reject("ROOT_INVALID", object_id, "tensor retirement lies outside its live interval")
        else:
            _reject("ROOT_INVALID", object_id, "tensor lifetime action is unknown")
    expected = [f"child:{parameter_id}" for parameter_id in parameter_order]
    windows = trace["mlx_windows"]
    if (
        not isinstance(windows, list)
        or [window.get("parameter_id") for window in windows if isinstance(window, dict)]
        != parameter_order
    ):
        _reject("ROOT_INVALID", object_id, "MLX allocation windows do not cover canonical parameter order")
    runtime_peak = 0
    for window in windows:
        row = _record(
            window,
            {
                "parameter_id", "active_before_bytes", "peak_delta_bytes",
                "active_after_bytes", "loss_hex",
            },
            object_id,
            "MLX allocation window",
        )
        _text(row["parameter_id"], object_id, "MLX parameter id")
        for field in ("active_before_bytes", "peak_delta_bytes", "active_after_bytes"):
            _counter(row[field], object_id, f"MLX {field}")
        if (
            not isinstance(row["loss_hex"], str)
            or len(row["loss_hex"]) != 8
            or not set(row["loss_hex"]) <= _HEX
            or not math.isfinite(struct.unpack("<f", bytes.fromhex(row["loss_hex"]))[0])
        ):
            _reject("GRADIENT_INVALID", object_id, "MLX loss must be one finite FP32 value")
        if row["active_after_bytes"] > row["active_before_bytes"]:
            _reject("MEMORY_BUDGET_EXCEEDED", object_id, "MLX retained an undeclared training allocation")
        runtime_peak = max(runtime_peak, row["peak_delta_bytes"])
    if (
        live
        or persisted != expected
        or trace["logical_peak_bytes"] != peak
        or trace["peak_um_bytes"] != peak + runtime_peak
    ):
        _reject("ROOT_INVALID", object_id, "trace peak, retirement, or canonical update order disagrees")
    return trace["peak_um_bytes"]


def _load_manifest(
    cartridge,
    work_root: str,
    manifest_digest: str,
    *,
    expected_checkpoint: TrainingCheckpoint | None = None,
    deep: bool = False,
) -> dict:
    _digest(work_root, "training:checkpoint", "work root")
    _digest(manifest_digest, work_root, "training manifest digest")
    root = load_root(cartridge, work_root)
    if not root["deltas"]:
        _reject("ROOT_INVALID", work_root, "training root has no ordered delta")
    delta = root["deltas"][-1]
    if delta["manifest_digest"] != manifest_digest:
        _reject("ROOT_INVALID", work_root, "training root names another manifest")
    payload = read_training_page(cartridge, work_root, manifest_digest)
    if digest_bytes(payload) != manifest_digest:
        _reject("PAGE_CORRUPT", manifest_digest, "training manifest bytes changed")
    manifest = _manifest_shape(_decode(payload, manifest_digest, "training manifest"), manifest_digest)
    parent = load_root(cartridge, manifest["parent_root"])
    expected_kind = "adapter" if manifest["tier"] == "A" else "certificate_recovery"
    ordered = _ordered_pages(manifest, manifest_digest)
    if (
        root["parents"] != [parent["identity"]]
        or manifest["parent_identity"] != parent["identity"]
        or delta["base_identity"] != parent["identity"]
        or delta["kind"] != expected_kind
        or delta["ordered_page_digests"] != ordered
        or len(ordered) != len(set(ordered))
    ):
        _reject("ROOT_INVALID", work_root, "training root, parent, kind, or ordered pages disagree")
    if manifest["tier"] == "B" and _compiled_certificate(parent, work_root) != manifest["parent_certificate_digest"]:
        _reject("ROOT_INVALID", work_root, "Tier B artifact names another compiled certificate")
    _validate_state(cartridge, work_root, manifest)
    checkpoint = _checkpoint(manifest, work_root, manifest_digest)
    if expected_checkpoint is not None and (
        not isinstance(expected_checkpoint, TrainingCheckpoint) or expected_checkpoint != checkpoint
    ):
        _reject("INVALID_REQUEST", work_root, "checkpoint coordinates do not match durable cartridge state")
    if deep:
        for row in manifest["base_pages"]:
            _base_payload(cartridge, manifest["parent_root"], row)
        delta_role = "adapter" if manifest["tier"] == "A" else "certificate_recovery"
        delta_shape = (2, 3) if manifest["tier"] == "A" else (1,)
        for row in manifest["delta_pages"]:
            _tensor_values(
                read_training_page(cartridge, work_root, row["page_digest"]),
                row["page_digest"],
                delta_role,
                row["parameter_id"],
                delta_shape,
                manifest["delta_precision"],
            )
        for row in manifest["objective_pages"]:
            _objective_values(
                read_training_page(cartridge, work_root, row["page_digest"]),
                manifest["operation"],
                row["step"],
                row["page_digest"],
            )
        calibration_records = []
        for row in manifest["calibration_pages"]:
            page = _decode(
                read_training_page(cartridge, work_root, row["page_digest"]),
                row["page_digest"],
                "calibration page",
            )
            envelope = _record(page, {"format", "role", "record"}, row["page_digest"], "calibration page")
            if envelope["format"] != _VERSION or envelope["role"] != "calibration":
                _reject("ROOT_INVALID", row["page_digest"], "calibration page role is malformed")
            calibration_records.append(envelope["record"])
        _calibrations(tuple(calibration_records), manifest["job_id"], manifest["tier"])
        peaks = [
            _validate_trace(
                read_training_page(cartridge, work_root, page_digest), manifest, ordinal
            )
            for ordinal, page_digest in enumerate(manifest["trace_pages"], 1)
        ]
        if manifest["declared_peak_bytes"] != max(peaks, default=0):
            _reject("ROOT_INVALID", work_root, "manifest peak does not match its lifetime traces")
    return manifest


def _write_checkpoint(
    cartridge,
    manifest: dict,
    available_locations: tuple[PageLocation, ...],
) -> TrainingCheckpoint:
    payload = canonical_bytes(manifest)
    if len(payload) > PAGE_BYTES:
        _reject("CAPACITY_EXCEEDED", manifest["job_id"], "training manifest exceeds one content page")
    manifest_digest = digest_bytes(payload)
    manifest_location = stage_training_pages(cartridge, (payload,))[0]
    by_digest = {location.page_digest: location for location in (*available_locations, manifest_location)}
    ordered = _ordered_pages(manifest, manifest_digest)
    if len(ordered) != len(set(ordered)) or any(page_digest not in by_digest for page_digest in ordered):
        _reject("ROOT_INVALID", manifest["job_id"], "checkpoint page catalog is incomplete or duplicated")
    root_digest = append_staged_training_delta(
        cartridge,
        manifest["parent_root"],
        "adapter" if manifest["tier"] == "A" else "certificate_recovery",
        tuple(by_digest[page_digest] for page_digest in ordered),
        manifest_digest,
    )
    checkpoint = _checkpoint(manifest, root_digest, manifest_digest)
    _load_manifest(cartridge, root_digest, manifest_digest, expected_checkpoint=checkpoint)
    return checkpoint


def prepare_training(
    cartridge,
    parent_root: str,
    operation: str,
    parameters: tuple[tuple[str, str], ...],
    objectives: tuple[tuple[float, ...], ...],
    *,
    random_seed: int,
    window_limit_bytes: int,
    calibration_records: tuple[dict, ...] = (),
    delta_precision: str = "FP32",
) -> TrainingCheckpoint:
    """Create one durable non-callable work branch over a frozen callable parent."""

    object_id = f"training:{operation}"
    if not isinstance(operation, str) or operation not in {*_TIER_A, _TIER_B}:
        _reject("TRAINING_UNSUPPORTED", object_id, "operation is outside the declared Tier A/B set")
    tier = "A" if operation in _TIER_A else "B"
    _digest(parent_root, object_id, "parent root")
    pin = pin_generation(cartridge)
    if pin is None or pin.root_digest != parent_root:
        _reject("IDEMPOTENCY_CONFLICT", object_id, "training parent is not the current callable generation")
    parent = load_root(cartridge, parent_root)
    if not isinstance(parameters, tuple) or not 0 < len(parameters) <= _MAX_PARAMETERS:
        _reject("INVALID_REQUEST", object_id, "parameters require one bounded nonempty tuple")
    if delta_precision not in _DELTA_PRECISIONS:
        _reject("TRAINING_UNSUPPORTED", object_id, "delta precision must be BF16 or FP32")
    base_precision = parent["provenance"]["identity_material"]["precision_scheme"]
    codec = _base_codec(base_precision, object_id)
    normalized_parameters = []
    for item in parameters:
        if not isinstance(item, tuple) or len(item) != 2:
            _reject("INVALID_REQUEST", object_id, "each parameter requires an id and frozen base page")
        parameter_id = _text(item[0], object_id, "parameter id")
        base_digest = _digest(item[1], object_id, "base page digest")
        matches = [
            tensor
            for tensor in parent["tensor_maps"]
            if tensor["dtype"] == "I8"
            and tensor["shape"] == [2, 3]
            and len(tensor["spans"]) == 1
            and tensor["spans"][0]["page_digest"] == base_digest
            and tensor["spans"][0]["length"] == _BASE_VALUES.size
            and tensor["spans"][0]["tensor_offset"] == 0
        ]
        if len(matches) != 1:
            _reject(
                "TRAINING_UNSUPPORTED",
                parameter_id,
                "each S21 base parameter must name one exact I8 2x3 tensor page",
            )
        page_payload = read_training_page(cartridge, parent_root, base_digest)
        span = matches[0]["spans"][0]
        base_payload = page_payload[span["offset"]:span["offset"] + span["length"]]
        if len(base_payload) != _BASE_VALUES.size:
            _reject("TRAINING_UNSUPPORTED", parameter_id, "quantized base tensor span must contain six bytes")
        normalized_parameters.append({
            "parameter_id": parameter_id,
            "tensor_id": matches[0]["semantic_tensor_id"],
            "page_digest": base_digest,
            "tensor_digest": digest_bytes(base_payload),
            "dtype": "I8",
            "shape": [2, 3],
            "offset": span["offset"],
            "length": span["length"],
            "codec": codec,
        })
    normalized_parameters.sort(key=lambda row: row["parameter_id"])
    if (
        len({item["parameter_id"] for item in normalized_parameters}) != len(normalized_parameters)
        or len({item["page_digest"] for item in normalized_parameters}) != len(normalized_parameters)
    ):
        _reject("INVALID_REQUEST", object_id, "parameter ids and frozen base pages must be unique")
    parent_pages = {location.page_digest for location in page_locations(cartridge, parent_root)}
    if any(item["page_digest"] not in parent_pages for item in normalized_parameters):
        _reject("PAGE_CORRUPT", object_id, "a frozen base page is absent from the callable parent")
    if tier == "B" and len(normalized_parameters) != 1:
        _reject("TRAINING_UNSUPPORTED", object_id, "F1 compiled recovery requires one frozen base window")
    if not isinstance(objectives, tuple) or not 0 < len(objectives) <= _MAX_STEPS:
        _reject("INVALID_REQUEST", object_id, "objectives require one bounded nonempty tuple")
    seed = _counter(random_seed, object_id, "random seed")
    limit = _counter(window_limit_bytes, object_id, "window limit", positive=True)
    calibrations = _calibrations(calibration_records, object_id, tier)
    trainable_count = len(normalized_parameters) if tier == "A" else len(calibrations)
    if trainable_count * len(objectives) > _MAX_UPDATES:
        _reject("TRAINING_UNSUPPORTED", object_id, "training schedule exceeds the bounded update catalog")
    certificate_digest = _compiled_certificate(parent, object_id) if tier == "B" else None
    objective_payloads = tuple(
        _objective_page(operation, step, values, object_id)
        for step, values in enumerate(objectives)
    )
    calibration_payloads = tuple(
        canonical_bytes({"format": _VERSION, "role": "calibration", "record": row})
        for row in calibrations
    )
    durable_inputs = stage_training_pages(cartridge, (*objective_payloads, *calibration_payloads))
    input_locations = {location.page_digest: location for location in durable_inputs}
    objective_rows = [
        {"step": step, "page_digest": digest_bytes(payload)}
        for step, payload in enumerate(objective_payloads)
    ]
    calibration_rows = [
        {"kind": row["kind"], "page_digest": digest_bytes(payload)}
        for row, payload in zip(calibrations, calibration_payloads, strict=True)
    ]
    job_id = digest_bytes(canonical_bytes({
        "version": _VERSION,
        "operation": operation,
        "parent_root": parent_root,
        "parameters": normalized_parameters,
        "objectives": objective_rows,
        "calibrations": calibration_rows,
        "delta_precision": delta_precision,
        "random_seed": seed,
        "window_limit_bytes": limit,
    }))
    if tier == "A":
        delta_ids = [parameter["parameter_id"] for parameter in normalized_parameters]
        delta_role = "adapter"
        delta_shape = (2, 3)
        initial_values = _INITIAL_ADAPTER
    else:
        delta_ids = [f"recovery.{row['kind']}" for row in calibrations]
        delta_role = "certificate_recovery"
        delta_shape = (1,)
        initial_values = (0.0,)
    delta_payloads = tuple(
        _tensor_page(
            delta_role,
            parameter_id,
            delta_shape,
            _numeric_payload(initial_values, delta_precision),
            "float32" if delta_precision == "FP32" else "bfloat16",
        )
        for parameter_id in delta_ids
    )
    delta_rows = [
        {"parameter_id": parameter_id, "page_digest": digest_bytes(payload)}
        for parameter_id, payload in zip(delta_ids, delta_payloads, strict=True)
    ]
    state_payloads = _state_pages(job_id, 0, delta_rows, _TRAINING_CASES[operation][1])
    generated = stage_training_pages(cartridge, (*delta_payloads, *state_payloads))
    generated_locations = {location.page_digest: location for location in generated}
    state_rows = {
        name: digest_bytes(payload)
        for name, payload in zip(("optimizer", "rng", "journal"), state_payloads, strict=True)
    }
    manifest = {
        "format": _VERSION,
        "job_id": job_id,
        "tier": tier,
        "operation": operation,
        "parent_root": parent_root,
        "parent_identity": parent["identity"],
        "parent_certificate_digest": certificate_digest,
        "base_precision": base_precision,
        "delta_precision": delta_precision,
        "operator_cases": list(_TRAINING_CASES[operation]),
        "adapter_rank": 1 if tier == "A" else None,
        "adapter_scale": "1" if tier == "A" else None,
        "step": 0,
        "total_steps": len(objectives),
        "optimizer_step": 0,
        "data_cursor": 0,
        "random_seed": seed,
        "rng_counter": 0,
        "window_limit_bytes": limit,
        "declared_peak_bytes": 0,
        "base_pages": normalized_parameters,
        "delta_pages": delta_rows,
        "objective_pages": objective_rows,
        "calibration_pages": calibration_rows,
        "state_pages": state_rows,
        "trace_pages": [],
        "master_pages": [],
    }
    _manifest_shape(manifest, job_id)
    return _write_checkpoint(
        cartridge,
        manifest,
        tuple({**input_locations, **generated_locations}.values()),
    )


def advance_training(cartridge, checkpoint: TrainingCheckpoint) -> TrainingCheckpoint:
    """Execute one deterministic global step and durably retire every live tensor window."""

    if not isinstance(checkpoint, TrainingCheckpoint):
        _reject("INVALID_REQUEST", "training:checkpoint", "TrainingCheckpoint is required")
    manifest = _load_manifest(
        cartridge,
        checkpoint.work_root,
        checkpoint.manifest_digest,
        expected_checkpoint=checkpoint,
    )
    if manifest["step"] == manifest["total_steps"]:
        _reject("INVALID_REQUEST", manifest["job_id"], "training is complete; commit the child")
    active = pin_generation(cartridge)
    if active is None or active.root_digest != manifest["parent_root"]:
        _reject("IDEMPOTENCY_CONFLICT", manifest["job_id"], "callable parent changed during training")
    location_map = {
        location.page_digest: location
        for location in page_locations(cartridge, checkpoint.work_root)
    }
    parent_locations = {
        location.page_digest: location
        for location in page_locations(cartridge, manifest["parent_root"])
    }
    objective_row = manifest["objective_pages"][manifest["step"]]
    objective_payload = read_training_page(
        cartridge, checkpoint.work_root, objective_row["page_digest"]
    )
    objective_values = _objective_values(
        objective_payload,
        manifest["operation"],
        manifest["step"],
        objective_row["page_digest"],
    )
    calibration_payloads = []
    calibration_records = []
    for row in manifest["calibration_pages"]:
        payload = read_training_page(cartridge, checkpoint.work_root, row["page_digest"])
        page = _record(
            _decode(payload, row["page_digest"], "calibration page"),
            {"format", "role", "record"},
            row["page_digest"],
            "calibration page",
        )
        if page["format"] != _VERSION or page["role"] != "calibration":
            _reject("ROOT_INVALID", row["page_digest"], "calibration page role is malformed")
        calibration_payloads.append((row, payload))
        calibration_records.append(page["record"])
    calibrations = _calibrations(tuple(calibration_records), manifest["job_id"], manifest["tier"])
    calibration_losses = {
        row["kind"]: float(Decimal(row["loss"])) for row in calibrations
    }
    delta_role = "adapter" if manifest["tier"] == "A" else "certificate_recovery"
    delta_shape = (2, 3) if manifest["tier"] == "A" else (1,)
    value_count = math.prod(delta_shape)
    stored_bytes = value_count * (4 if manifest["delta_precision"] == "FP32" else 2)
    gradient_bytes = value_count * 4
    if manifest["tier"] == "A":
        update_rows = [
            (base, delta, None)
            for base, delta in zip(manifest["base_pages"], manifest["delta_pages"], strict=True)
        ]
    else:
        base = manifest["base_pages"][0]
        update_rows = [
            (base, delta, calibration_losses[delta["parameter_id"].removeprefix("recovery.")])
            for delta in manifest["delta_pages"]
        ]
    fixed_live_bytes = len(objective_payload) + sum(len(payload) for _, payload in calibration_payloads)
    required_peak = max(
        fixed_live_bytes
        + parent_locations[base["page_digest"]].length
        + location_map[delta["page_digest"]].length
        + gradient_bytes
        + len(_tensor_page(
            delta_role,
            delta["parameter_id"],
            delta_shape,
            b"\0" * stored_bytes,
            "float32" if manifest["delta_precision"] == "FP32" else "bfloat16",
        ))
        for base, delta, _ in update_rows
    )
    if required_peak > manifest["window_limit_bytes"]:
        _reject(
            "MEMORY_BUDGET_EXCEEDED",
            manifest["job_id"],
            f"one page update requires {required_peak} bytes; admitted {manifest['window_limit_bytes']}",
        )
    events = []
    live = {}
    peak = 0
    output_rows = []
    mlx_windows = []

    def event(action: str, tensor_id: str, size: int, location: str, page_digest: str | None) -> None:
        nonlocal peak
        events.append({
            "sequence": len(events),
            "action": action,
            "tensor_id": tensor_id,
            "location": location,
            "bytes": size,
            "page_digest": page_digest,
        })
        if action in {"LOAD", "PRODUCE"}:
            if tensor_id in live:
                _reject("ROOT_INVALID", manifest["job_id"], "tensor entered unified memory twice")
            live[tensor_id] = size
            peak = max(peak, sum(live.values()))
        elif action == "RETIRE":
            if live.pop(tensor_id, None) is None:
                _reject("ROOT_INVALID", manifest["job_id"], "tensor retired outside its live interval")
        elif action == "PERSIST":
            if tensor_id not in live:
                _reject("ROOT_INVALID", manifest["job_id"], "non-live tensor cannot persist")
            peak = max(peak, sum(live.values()))

    event("LOAD", f"batch:{manifest['step']}", len(objective_payload), "UM", objective_row["page_digest"])
    for row, payload in calibration_payloads:
        event("LOAD", f"calibration:{row['kind']}", len(payload), "UM", row["page_digest"])

    def outputs():
        for base, delta, calibration_loss in update_rows:
            parameter_id = delta["parameter_id"]
            base_payload = _base_payload(cartridge, manifest["parent_root"], base)
            base_page_bytes = parent_locations[base["page_digest"]].length
            base_tensor_id = (
                f"base:{parameter_id}"
                if manifest["tier"] == "A"
                else f"base:{base['parameter_id']}:{parameter_id}"
            )
            event("LOAD", base_tensor_id, base_page_bytes, "UM", base["page_digest"])
            delta_payload = read_training_page(
                cartridge, checkpoint.work_root, delta["page_digest"]
            )
            parameter_values = _tensor_values(
                delta_payload,
                delta["page_digest"],
                delta_role,
                parameter_id,
                delta_shape,
                manifest["delta_precision"],
            )
            event("LOAD", f"delta:{parameter_id}", len(delta_payload), "UM", delta["page_digest"])
            event("PRODUCE", f"gradient:{parameter_id}", gradient_bytes, "UM", None)
            updated_values, mlx_window = _update_delta(
                parameter_values,
                base_payload,
                base["codec"],
                objective_values,
                calibration_loss,
                manifest["operation"],
                manifest["delta_precision"],
                parameter_id,
            )
            mlx_windows.append(mlx_window)
            output_payload = _tensor_page(
                delta_role,
                parameter_id,
                delta_shape,
                updated_values,
                "float32" if manifest["delta_precision"] == "FP32" else "bfloat16",
            )
            output_digest = digest_bytes(output_payload)
            event("PRODUCE", f"child:{parameter_id}", len(output_payload), "UM", output_digest)
            output_rows.append({"parameter_id": parameter_id, "page_digest": output_digest})
            yield output_payload
            event("PERSIST", f"child:{parameter_id}", len(output_payload), "D", output_digest)
            event("RETIRE", f"gradient:{parameter_id}", gradient_bytes, "UM", None)
            event("RETIRE", f"child:{parameter_id}", len(output_payload), "UM", output_digest)
            event("RETIRE", f"delta:{parameter_id}", len(delta_payload), "UM", delta["page_digest"])
            event("RETIRE", base_tensor_id, base_page_bytes, "UM", base["page_digest"])

    output_locations = stage_training_pages(cartridge, outputs())
    for row, payload in reversed(calibration_payloads):
        event("RETIRE", f"calibration:{row['kind']}", len(payload), "UM", row["page_digest"])
    event("RETIRE", f"batch:{manifest['step']}", len(objective_payload), "UM", objective_row["page_digest"])
    runtime_peak = max(window["peak_delta_bytes"] for window in mlx_windows)
    observed_peak = peak + runtime_peak
    if live or peak != required_peak:
        _reject("ROOT_INVALID", manifest["job_id"], "live tensor retirement or admitted peak disagrees")
    if observed_peak > manifest["window_limit_bytes"]:
        _reject(
            "MEMORY_BUDGET_EXCEEDED",
            manifest["job_id"],
            f"logical and MLX tensor peak {observed_peak} exceeds admitted {manifest['window_limit_bytes']}",
        )
    next_step = manifest["step"] + 1
    trace_payload = canonical_bytes({
        "format": _TRACE_VERSION,
        "role": "tensor_lifetime",
        "job_id": manifest["job_id"],
        "step": next_step,
        "parameter_order": [row["parameter_id"] for row in output_rows],
        "events": events,
        "logical_peak_bytes": peak,
        "mlx_windows": mlx_windows,
        "peak_um_bytes": observed_peak,
    })
    state_payloads = _state_pages(
        manifest["job_id"],
        next_step,
        output_rows,
        manifest["operator_cases"][1],
    )
    support_locations = stage_training_pages(cartridge, (trace_payload, *state_payloads))
    trace_digest = digest_bytes(trace_payload)
    state_rows = {
        name: digest_bytes(payload)
        for name, payload in zip(("optimizer", "rng", "journal"), state_payloads, strict=True)
    }
    next_manifest = {
        **manifest,
        "step": next_step,
        "optimizer_step": next_step,
        "data_cursor": next_step,
        "rng_counter": next_step,
        "declared_peak_bytes": max(manifest["declared_peak_bytes"], observed_peak),
        "delta_pages": output_rows,
        "state_pages": state_rows,
        "trace_pages": [*manifest["trace_pages"], trace_digest],
    }
    _manifest_shape(next_manifest, manifest["job_id"])
    retained = [
        *[row["page_digest"] for row in next_manifest["objective_pages"]],
        *[row["page_digest"] for row in next_manifest["calibration_pages"]],
        *manifest["trace_pages"],
    ]
    new_locations = {
        location.page_digest: location
        for location in (*output_locations, *support_locations)
    }
    available = tuple(
        location_map[page_digest] for page_digest in retained
    ) + tuple(new_locations.values())
    return _write_checkpoint(cartridge, next_manifest, available)


def commit_training(
    cartridge,
    checkpoint: TrainingCheckpoint,
    transaction_id: str,
) -> TrainingResult:
    """Commit one completed training artifact through the sole Q73 generation authority."""

    if not isinstance(checkpoint, TrainingCheckpoint):
        _reject("INVALID_REQUEST", "training:checkpoint", "TrainingCheckpoint is required")
    manifest = _load_manifest(
        cartridge,
        checkpoint.work_root,
        checkpoint.manifest_digest,
        expected_checkpoint=checkpoint,
        deep=True,
    )
    if manifest["step"] != manifest["total_steps"]:
        _reject("INVALID_REQUEST", manifest["job_id"], "incomplete training cannot become callable")
    rng_state = read_training_page(
        cartridge, checkpoint.work_root, manifest["state_pages"]["rng"]
    )
    inputs = [
        manifest["parent_root"],
        manifest["job_id"],
        checkpoint.manifest_digest,
        *[row["page_digest"] for row in manifest["objective_pages"]],
        *[row["page_digest"] for row in manifest["calibration_pages"]],
    ]
    context = TransactionContext(
        operation_version=_VERSION,
        input_digests=tuple(dict.fromkeys(inputs)),
        random_seed=manifest["random_seed"],
        statistics=canonical_bytes({
            "job_id": manifest["job_id"],
            "declared_peak_bytes": manifest["declared_peak_bytes"],
            "trace_pages": manifest["trace_pages"],
        }),
        optimizer_step=manifest["optimizer_step"],
        rng_state=rng_state,
        data_cursor=manifest["data_cursor"],
        loss_scale="1.0",
    )
    pin = commit_generation(
        cartridge,
        transaction_id,
        checkpoint.work_root,
        expected_parent_root=manifest["parent_root"],
        context=context,
    )
    root = load_root(cartridge, pin.root_digest)
    delta = root["deltas"][-1]
    if delta["manifest_digest"] != checkpoint.manifest_digest:
        _reject("ROOT_INVALID", pin.root_digest, "committed child names another training artifact")
    return TrainingResult(
        pin.generation,
        pin.child_id,
        pin.root_digest,
        delta["delta_id"],
        checkpoint.manifest_digest,
        manifest["operation"],
    )


def load_training_artifact(cartridge, root_digest: str) -> dict:
    """Load one final Tier A/B artifact without deriving or claiming a Q19 certificate."""

    _digest(root_digest, "training:artifact", "training root")
    root = load_root(cartridge, root_digest)
    if not root["deltas"]:
        _reject("ROOT_INVALID", root_digest, "revision has no training artifact")
    manifest_digest = root["deltas"][-1]["manifest_digest"]
    manifest = _load_manifest(cartridge, root_digest, manifest_digest, deep=True)
    if manifest["step"] != manifest["total_steps"]:
        _reject("ROOT_INVALID", root_digest, "training artifact is not complete")
    return _decode(canonical_bytes(manifest), manifest_digest, "training artifact")
