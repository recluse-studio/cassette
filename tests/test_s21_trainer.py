# test_s21_trainer.py — S21 immutable paged Tier A/B training, restart, trace, equivalence, and commit fixture; depends on broker.py, compiler.py, errors.py, pager.py, store.py, trainer.py, tests/compiler_fixture.py, tests/test_s17_broker.py.
"""Attack every boundary between frozen pages, live tensors, durable work, and callability."""

from __future__ import annotations

import asyncio
import ast
from dataclasses import asdict, replace
import json
import math
import os
from pathlib import Path
import platform
import shutil
import signal
import struct
import subprocess
import sys

import pytest

from broker import CanonicalBroker, ScheduledLease
from compiler import plan_revision, prepare_revision, verify_bundle_structure
from compiler_fixture import artifact as compiler_artifact
from errors import CassetteError
from store import (
    ArtifactIdentity,
    IdentityTuple,
    append_staged_training_delta,
    canonical_bytes,
    commit_generation,
    digest_bytes,
    import_safetensors,
    load_root,
    load_transaction_context,
    model_identity,
    page_locations,
    pin_generation,
    read_training_page,
    rollback_generation,
    stage_training_pages,
)
from test_s17_broker import _profile, _request, _schedule
import trainer as trainer_module
from trainer import (
    TrainingCheckpoint,
    advance_training,
    commit_training,
    load_training_artifact,
    prepare_training,
)


pytestmark = pytest.mark.skipif(
    platform.system() != "Darwin" or platform.machine() != "arm64",
    reason="S21 requires arm64 macOS, MLX Metal, and F_FULLFSYNC",
)

FLOATS = struct.Struct("<6f")
BASE_VALUES = struct.Struct("<6b")
INITIAL_ADAPTER = (0.25, -0.5, 0.75, 0.0, 0.0, 0.0)
SFT_BATCHES = (
    (1.0, 0.0, 0.0, 1.0, 1.0, -1.0, 0.5, -0.25, 1.0, 0.0),
    (0.0, 1.0, 1.0, 0.0, -1.0, 1.0, 0.0, 0.75, -0.5, 1.25),
)
CONTINUATION_BATCH = (
    1.0, 1.0, 0.0, 1.0, 1.0, 0.0, -0.25, 0.5, 0.75, -1.0,
)
PREFERENCE_BATCH = (1.0, -1.0, 0.5, 0.25, -0.5, 1.0, 0.2)
RECOVERY_BATCH = (1.0, 0.5, -0.5, 1.0, 0.25, -1.0, 0.0, 0.5, -0.25, 1.0)


def _write_safetensors(path: Path, tensor_id: str, payload: bytes) -> None:
    header = {
        tensor_id: {
            "dtype": "I8",
            "shape": [2, 3],
            "data_offsets": [0, len(payload)],
        }
    }
    encoded = json.dumps(header, separators=(",", ":")).encode()
    encoded += b" " * (-len(encoded) % 8)
    path.write_bytes(len(encoded).to_bytes(8, "little") + encoded + payload)


def _quantized_parent(
    tmp_path: Path,
    base_values: tuple[tuple[int, ...], tuple[int, ...]] = (
        (-2, -1, 0, 1, 2, 3),
        (3, 1, -1, -3, 2, 0),
    ),
    precision: str = "i8-symmetric;scale=1;zero_point=0",
) -> tuple[Path, str, tuple[tuple[str, str], ...]]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    sources = (tmp_path / "base-a.safetensors", tmp_path / "base-b.safetensors")
    _write_safetensors(sources[0], "layer.0", BASE_VALUES.pack(*base_values[0]))
    _write_safetensors(sources[1], "layer.1", BASE_VALUES.pack(*base_values[1]))
    artifacts = tuple(
        ArtifactIdentity(path.name, path.stat().st_size, digest_bytes(path.read_bytes()))
        for path in sources
    )
    material = IdentityTuple(
        revision_kind="source",
        source_kind="huggingface",
        source_alias="fixture/s21-quantized",
        canonical_locator="fixture/s21-quantized",
        requested_revision=None,
        immutable_revision="git-sha1:" + "2" * 40,
        artifacts=artifacts,
        format_versions=(("safetensors", "0.6.2"),),
        tensor_index_digest=digest_bytes(b"S21 quantized tensor index"),
        config_digest=digest_bytes(b"S21 quantized config"),
        architecture="S21PagedFixture",
        operator_set=("matmul",),
        tokenizer_digest=digest_bytes(b"S21 tokenizer"),
        processor_digest=digest_bytes(b"S21 processor"),
        template_digest=digest_bytes(b"S21 template"),
        precision_scheme=precision,
        license_digest=digest_bytes(b"S21 license"),
        parent_ids=(),
        transform_manifest_digest=None,
    )
    cartridge = tmp_path / "quantized-cartridge"
    root = import_safetensors(
        {path.name: path for path in sources}, cartridge, material
    )
    commit_generation(cartridge, "s21-quantized-parent", root, expected_parent_root=None)
    locations = sorted(page_locations(cartridge, root), key=lambda location: location.page_digest)
    assert len(locations) == 2
    parameters = tuple(
        (f"adapter.layer.{index}", location.page_digest)
        for index, location in enumerate(locations)
    )
    return cartridge, root, parameters


def _source(material: IdentityTuple) -> dict:
    return {
        "source_kind": material.source_kind,
        "source_alias": material.source_alias,
        "locator": material.canonical_locator,
        "requested_revision": material.requested_revision,
        "immutable_revision": material.immutable_revision,
        "identity": model_identity(material),
        "artifacts": [
            {"path": item.path, "size": item.size, "digest": item.digest}
            for item in material.artifacts
        ],
        "license_digest": material.license_digest,
    }


def _compiled_parent(tmp_path: Path) -> tuple[Path, str, tuple[tuple[str, str], ...]]:
    cartridge = tmp_path / "compiled-cartridge"
    incoming = cartridge / "incoming"
    incoming.mkdir(parents=True)
    artifact_path = "model.safetensors"
    def quantized_manifest(document: dict) -> None:
        values = [["-2", "-1", "0"], ["1", "2", "3"]]
        evidence = document["evidence"]
        document["model"]["precision_scheme"] = "i8-symmetric;scale=1;zero_point=0"
        evidence["target"].update(
            source_shape=[2, 3], shape=[2, 3], flattening_order=list(range(6))
        )
        evidence["conditions"][0]["metric"] = [
            ["1" if row == column else "0" for column in range(6)]
            for row in range(6)
        ]
        evidence["atoms"][0]["matrix"] = values
        evidence["atoms"][0]["description"]["reconstruction"] = values
        evidence["atoms"][0]["description"]["estimator_calibration"]["atom_norm_squared"] = "19"

    payload, material, _ = compiler_artifact(
        "huggingface",
        "fixture/s21-compiled",
        "git-sha1:" + "3" * 40,
        digest_bytes(b"S21 compiled license"),
        artifact_path,
        label="s21-compiled",
        mutate_manifest=quantized_manifest,
        tensor=("I8", (2, 3), BASE_VALUES.pack(-2, -1, 0, 1, 2, 3)),
    )
    physical = incoming / "physical.safetensors"
    physical.write_bytes(payload)
    descriptor = os.open(physical, os.O_RDWR)
    source = _source(material)
    extents = {
        artifact_path: {
            "fd": descriptor,
            "offset": 0,
            "length": len(payload),
            "operation_id": "s21-compiled-source",
        }
    }
    try:
        plan_digest = plan_revision(source, extents, cartridge)
        prepared = prepare_revision(source, extents, cartridge, plan_digest)
        verify_bundle_structure(
            cartridge,
            prepared.candidate_root,
            prepared.source_identity,
            prepared.plan_digest,
            {artifact_path: descriptor},
        )
    finally:
        os.close(descriptor)
    commit_generation(
        cartridge,
        "s21-compiled-parent",
        prepared.candidate_root,
        expected_parent_root=None,
    )
    locations = sorted(
        page_locations(cartridge, prepared.candidate_root),
        key=lambda location: location.page_digest,
    )
    parameters = (("recovery.atom.0", locations[0].page_digest),)
    return cartridge, prepared.candidate_root, parameters


def _run(checkpoint: TrainingCheckpoint, cartridge: Path) -> TrainingCheckpoint:
    while checkpoint.step < checkpoint.total_steps:
        checkpoint = advance_training(cartridge, checkpoint)
    return checkpoint


def _kill_before_checkpoint_root(cartridge: Path, checkpoint: TrainingCheckpoint) -> None:
    environment = os.environ.copy()
    repository = str(Path(__file__).resolve().parent.parent)
    environment["PYTHONPATH"] = repository + os.pathsep + environment.get("PYTHONPATH", "")
    process = subprocess.Popen(
        [
            sys.executable,
            "-B",
            str(Path(__file__).resolve()),
            "_s21_kill",
            str(cartridge),
            json.dumps(asdict(checkpoint), separators=(",", ":")),
        ],
        cwd=repository,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        assert process.stdout.readline().strip() == "BOUNDARY:CHECKPOINT_ROOT"
        process.kill()
        assert process.wait(timeout=10) == -signal.SIGKILL
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=10)
    assert not process.stderr.read().strip()


def _f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def _bf16(value: float) -> float:
    bits = struct.unpack("<I", struct.pack("<f", value))[0]
    rounded = (bits + 0x7FFF + ((bits >> 16) & 1)) >> 16
    return struct.unpack("<f", struct.pack("<I", rounded << 16))[0]


def _expected_adapter(
    base_values: tuple[float, ...],
    objectives: tuple[tuple[float, ...], ...],
    operation: str,
    calibration_losses: tuple[float, ...] = (),
    precision: str = "FP32",
) -> tuple[float, ...]:
    state = list(INITIAL_ADAPTER)
    for objective in objectives:
        factor_a = state[:3]
        factor_b = state[3:5]
        effective = [
            _f32(base_values[row * 3 + column] + _f32(factor_b[row] * factor_a[column]))
            for row in range(2)
            for column in range(3)
        ]
        if operation == "OFFLINE_ADAPTER_DPO":
            difference = [objective[row * 2] - objective[row * 2 + 1] for row in range(3)]
            margin = _f32(sum(
                _f32(effective[row * 3 + column] * difference[column])
                for row in range(2)
                for column in range(3)
            ) - objective[6])
            coefficient = _f32(-1.0 / (1.0 + math.exp(margin)))
            weight_gradient = [
                _f32(coefficient * difference[column])
                for _row in range(2)
                for column in range(3)
            ]
        else:
            correction = sum(calibration_losses) / len(calibration_losses) if calibration_losses else 0.0
            targets = [_f32(value + correction) for value in objective[6:]]
            predictions = [
                _f32(sum(
                    _f32(effective[row * 3 + inner] * objective[inner * 2 + column])
                    for inner in range(3)
                ))
                for row in range(2)
                for column in range(2)
            ]
            errors = [_f32(value - target) for value, target in zip(predictions, targets, strict=True)]
            weight_gradient = [
                _f32(0.5 * sum(
                    _f32(errors[row * 2 + column] * objective[inner * 2 + column])
                    for column in range(2)
                ))
                for row in range(2)
                for inner in range(3)
            ]
        gradient_a = [
            _f32(sum(
                _f32(factor_b[row] * weight_gradient[row * 3 + column])
                for row in range(2)
            ))
            for column in range(3)
        ]
        gradient_b = [
            _f32(sum(
                _f32(weight_gradient[row * 3 + column] * factor_a[column])
                for column in range(3)
            ))
            for row in range(2)
        ]
        state = [
            _f32(value - _f32(0.25 * gradient))
            for value, gradient in zip(state, (*gradient_a, *gradient_b, 0.0), strict=True)
        ]
        if precision == "BF16":
            state = [_bf16(value) for value in state]
    return tuple(state)


def _delta_payloads(cartridge: Path, root_digest: str, artifact: dict) -> dict[str, tuple[float, ...]]:
    output = {}
    role = "adapter" if artifact["tier"] == "A" else "certificate_recovery"
    count = 6 if artifact["tier"] == "A" else 1
    for row in artifact["delta_pages"]:
        payload = read_training_page(cartridge, root_digest, row["page_digest"])
        page = json.loads(payload)
        assert set(page) == {"format", "role", "tensor_id", "dtype", "shape", "payload_hex"}
        assert page["role"] == role and page["tensor_id"] == row["parameter_id"]
        encoded = bytes.fromhex(page["payload_hex"])
        if page["dtype"] == "float32":
            values = struct.unpack(f"<{count}f", encoded)
        else:
            words = struct.unpack(f"<{count}H", encoded)
            values = tuple(
                struct.unpack("<f", struct.pack("<I", word << 16))[0]
                for word in words
            )
        output[row["parameter_id"]] = values
    return output


def _base_values(cartridge: Path, artifact: dict, row: dict) -> tuple[float, ...]:
    quantized = BASE_VALUES.unpack(
        read_training_page(cartridge, artifact["parent_root"], row["page_digest"])[
            row["offset"]:row["offset"] + row["length"]
        ]
    )
    codec = row["codec"]
    scale = float(codec["scale"])
    return tuple((value - codec["zero_point"]) * scale for value in quantized)


def _expected_recovery(
    base_values: tuple[float, ...],
    objectives: tuple[tuple[float, ...], ...],
    calibration_loss: float,
    precision: str,
) -> tuple[float, ...]:
    state = 0.0
    for objective in objectives:
        predictions = [
            _f32(sum(
                _f32(base_values[row * 3 + inner] * objective[inner * 2 + column])
                for inner in range(3)
            ))
            for row in range(2)
            for column in range(2)
        ]
        prediction = _f32(_f32(sum(predictions) / 4.0) + state)
        target = _f32(_f32(sum(objective[6:]) / 4.0) + calibration_loss)
        gradient = _f32(2.0 * _f32(prediction - target))
        state = _f32(state - _f32(0.25 * gradient))
        if precision == "BF16":
            state = _bf16(state)
    return (state,)


def _expected_payloads(
    cartridge: Path,
    artifact: dict,
    objectives: tuple[tuple[float, ...], ...],
    calibration_losses: tuple[float, ...] = (),
) -> dict[str, tuple[float, ...]]:
    if artifact["tier"] == "B":
        base_values = _base_values(cartridge, artifact, artifact["base_pages"][0])
        return {
            f"recovery.{kind}": _expected_recovery(
                base_values,
                objectives,
                loss,
                artifact["delta_precision"],
            )
            for kind, loss in zip(
                ("condition", "atom", "description", "estimator", "observation", "precision"),
                calibration_losses,
                strict=True,
            )
        }
    return {
        row["parameter_id"]: _expected_adapter(
            _base_values(cartridge, artifact, row),
            objectives,
            artifact["operation"],
            calibration_losses,
            artifact["delta_precision"],
        )
        for row in artifact["base_pages"]
    }


def _replay_traces(cartridge: Path, root_digest: str, artifact: dict) -> None:
    expected_parameters = [row["parameter_id"] for row in artifact["delta_pages"]]
    observed_peaks = []
    for ordinal, page_digest in enumerate(artifact["trace_pages"], 1):
        trace = json.loads(read_training_page(cartridge, root_digest, page_digest))
        assert trace["step"] == ordinal
        assert trace["parameter_order"] == expected_parameters
        live = {}
        peak = 0
        persisted = []
        for sequence, event in enumerate(trace["events"]):
            assert event["sequence"] == sequence
            if event["action"] in {"LOAD", "PRODUCE"}:
                assert event["location"] == "UM" and event["tensor_id"] not in live
                live[event["tensor_id"]] = event["bytes"]
                peak = max(peak, sum(live.values()))
            elif event["action"] == "PERSIST":
                assert event["location"] == "D" and event["tensor_id"] in live
                assert event["page_digest"].startswith("blake3:")
                persisted.append(event["tensor_id"])
            else:
                assert event["action"] == "RETIRE" and event["location"] == "UM"
                assert live.pop(event["tensor_id"]) > 0
        assert not live
        assert persisted == [f"child:{parameter_id}" for parameter_id in expected_parameters]
        assert trace["logical_peak_bytes"] == peak
        assert [row["parameter_id"] for row in trace["mlx_windows"]] == expected_parameters
        runtime_peak = 0
        for window in trace["mlx_windows"]:
            assert window["active_after_bytes"] <= window["active_before_bytes"]
            assert window["peak_delta_bytes"] >= 0
            assert math.isfinite(struct.unpack("<f", bytes.fromhex(window["loss_hex"]))[0])
            runtime_peak = max(runtime_peak, window["peak_delta_bytes"])
        assert trace["peak_um_bytes"] == peak + runtime_peak <= artifact["window_limit_bytes"]
        observed_peaks.append(trace["peak_um_bytes"])
    assert artifact["declared_peak_bytes"] == max(observed_peaks, default=0)


def _calibration_records(label: str) -> tuple[dict, ...]:
    return tuple(
        {
            "kind": kind,
            "input_digest": digest_bytes(f"{label}:{kind}:input".encode()),
            "output_digest": digest_bytes(f"{label}:{kind}:output".encode()),
            "sample_count": 32768,
            "loss": f"0.0{index + 1}",
        }
        for index, kind in enumerate(
            ("condition", "atom", "description", "estimator", "observation", "precision")
        )
    )


def _contains_certificate(value: object) -> bool:
    if isinstance(value, dict):
        return "certificate" in value or any(_contains_certificate(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_certificate(item) for item in value)
    return False


def _manifest(cartridge: Path, checkpoint: TrainingCheckpoint) -> dict:
    return json.loads(read_training_page(
        cartridge, checkpoint.work_root, checkpoint.manifest_digest
    ))


def _ordered_pages(manifest: dict, manifest_digest: str) -> list[str]:
    return [
        manifest_digest,
        *[row["page_digest"] for row in manifest["delta_pages"]],
        *[row["page_digest"] for row in manifest["objective_pages"]],
        *[row["page_digest"] for row in manifest["calibration_pages"]],
        *[manifest["state_pages"][name] for name in ("optimizer", "rng", "journal")],
        *manifest["trace_pages"],
    ]


def _forge_checkpoint(
    cartridge: Path,
    checkpoint: TrainingCheckpoint,
    mutate,
    extra_payloads: tuple[bytes, ...] = (),
) -> TrainingCheckpoint:
    manifest = _manifest(cartridge, checkpoint)
    extra_locations = stage_training_pages(cartridge, extra_payloads) if extra_payloads else ()
    mutation_locations = mutate(manifest, extra_locations) or ()
    payload = canonical_bytes(manifest)
    manifest_location = stage_training_pages(cartridge, (payload,))[0]
    manifest_digest = digest_bytes(payload)
    locations = {
        location.page_digest: location
        for location in (
            *page_locations(cartridge, checkpoint.work_root),
            *extra_locations,
            *mutation_locations,
            manifest_location,
        )
    }
    ordered = _ordered_pages(manifest, manifest_digest)
    forged_root = append_staged_training_delta(
        cartridge,
        manifest["parent_root"],
        "adapter" if manifest["tier"] == "A" else "certificate_recovery",
        tuple(locations[digest] for digest in ordered),
        manifest_digest,
    )
    return TrainingCheckpoint(
        manifest["job_id"],
        manifest["parent_root"],
        forged_root,
        manifest_digest,
        manifest["step"],
        manifest["total_steps"],
    )


def _train(
    cartridge: Path,
    parent_root: str,
    parameters: tuple[tuple[str, str], ...],
    operation: str,
    batches: tuple[tuple[float, ...], ...],
    transaction_id: str,
    *,
    precision: str = "FP32",
    calibrations: tuple[dict, ...] = (),
) -> tuple[TrainingCheckpoint, dict]:
    checkpoint = prepare_training(
        cartridge,
        parent_root,
        operation,
        parameters,
        batches,
        random_seed=17,
        window_limit_bytes=32 * 1024,
        calibration_records=calibrations,
        delta_precision=precision,
    )
    checkpoint = _run(checkpoint, cartridge)
    result = commit_training(cartridge, checkpoint, transaction_id)
    return checkpoint, load_training_artifact(cartridge, result.root_digest)


def test_q21_q24_q70_all_advertised_operations_use_their_declared_training_evidence(tmp_path):
    """Q21/Q24/Q70 acceptance: every Tier-A operation and Tier-B recovery changes a frozen quantized base through its own evidence."""

    source, parent_root, parameters = _quantized_parent(tmp_path / "tier-a-source")
    outputs = {}
    cases = (
        ("ADAPTER_SFT", SFT_BATCHES, "FP32"),
        ("ADAPTER_SFT", SFT_BATCHES, "BF16"),
        ("ADAPTER_CONTINUED_PRETRAINING", (CONTINUATION_BATCH,), "FP32"),
        ("OFFLINE_ADAPTER_DPO", (PREFERENCE_BATCH,), "FP32"),
    )
    objective_roles = {
        "ADAPTER_SFT": "instruction_response",
        "ADAPTER_CONTINUED_PRETRAINING": "causal_continuation",
        "OFFLINE_ADAPTER_DPO": "preference_pair",
    }
    objective_cases = {
        "ADAPTER_SFT": "mlx.autograd_lora_mse.f32.rank1.2x3_3x2",
        "ADAPTER_CONTINUED_PRETRAINING": "mlx.autograd_lora_mse.f32.rank1.2x3_3x2",
        "OFFLINE_ADAPTER_DPO": "mlx.autograd_lora_dpo.f32.rank1.2x3_3x2",
    }
    for ordinal, (operation, batches, precision) in enumerate(cases):
        cartridge = tmp_path / f"tier-a-{ordinal}"
        shutil.copytree(source, cartridge)
        _, artifact = _train(
            cartridge,
            parent_root,
            parameters,
            operation,
            batches,
            f"s21-tier-a-{ordinal}",
            precision=precision,
        )
        assert artifact["operation"] == operation
        assert artifact["delta_precision"] == precision
        assert artifact["adapter_rank"] == 1 and artifact["adapter_scale"] == "1"
        assert artifact["operator_cases"] == [objective_cases[operation], "mlx.sgd.f32.3"]
        assert artifact["master_pages"] == []
        assert artifact["base_precision"] == "i8-symmetric;scale=1;zero_point=0"
        assert {tuple(row["codec"].items()) for row in artifact["base_pages"]} == {
            (("name", "i8-symmetric"), ("scale", "1"), ("zero_point", 0))
        }
        child_root = pin_generation(cartridge).root_digest
        optimizer_state = json.loads(read_training_page(
            cartridge, child_root, artifact["state_pages"]["optimizer"]
        ))
        assert optimizer_state["case_id"] == artifact["operator_cases"][1]
        assert {
            json.loads(read_training_page(cartridge, child_root, row["page_digest"]))["role"]
            for row in artifact["objective_pages"]
        } == {objective_roles[operation]}
        outputs[(operation, precision)] = _delta_payloads(
            cartridge, child_root, artifact
        )
    assert outputs[("ADAPTER_SFT", "FP32")] != outputs[("ADAPTER_CONTINUED_PRETRAINING", "FP32")]
    assert outputs[("ADAPTER_SFT", "FP32")] != outputs[("OFFLINE_ADAPTER_DPO", "FP32")]

    changed_source, changed_root, changed_parameters = _quantized_parent(
        tmp_path / "changed-base",
        ((-1, -1, 0, 1, 2, 3), (3, 1, -1, -3, 2, 0)),
    )
    _, changed_artifact = _train(
        changed_source,
        changed_root,
        changed_parameters,
        "ADAPTER_SFT",
        (SFT_BATCHES[0],),
        "s21-changed-base",
    )
    reference = tmp_path / "reference-base"
    shutil.copytree(source, reference)
    _, reference_artifact = _train(
        reference,
        parent_root,
        parameters,
        "ADAPTER_SFT",
        (SFT_BATCHES[0],),
        "s21-reference-base",
    )
    assert _delta_payloads(
        changed_source, pin_generation(changed_source).root_digest, changed_artifact
    ) != _delta_payloads(reference, pin_generation(reference).root_digest, reference_artifact)

    scaled_source, scaled_root, scaled_parameters = _quantized_parent(
        tmp_path / "scaled-base",
        precision="i8-symmetric;scale=0.5;zero_point=0",
    )
    _, scaled_artifact = _train(
        scaled_source,
        scaled_root,
        scaled_parameters,
        "ADAPTER_SFT",
        (SFT_BATCHES[0],),
        "s21-scaled-base",
    )
    assert _delta_payloads(
        scaled_source, pin_generation(scaled_source).root_digest, scaled_artifact
    ) != _delta_payloads(reference, pin_generation(reference).root_digest, reference_artifact)
    implicit_source, implicit_root, implicit_parameters = _quantized_parent(
        tmp_path / "implicit-codec",
        precision="q8-implicit",
    )
    with pytest.raises(CassetteError) as caught:
        prepare_training(
            implicit_source,
            implicit_root,
            "ADAPTER_SFT",
            implicit_parameters,
            (SFT_BATCHES[0],),
            random_seed=1,
            window_limit_bytes=32 * 1024,
        )
    assert caught.value.code == "TRAINING_UNSUPPORTED"

    before_refusal = {
        str(path.relative_to(source)): digest_bytes(path.read_bytes())
        for path in source.rglob("*") if path.is_file()
    }
    for operation, precision in (("FULL_WEIGHT_ADAM", "FP32"), ("ADAPTER_SFT", "Q4")):
        with pytest.raises(CassetteError) as caught:
            prepare_training(
                source,
                parent_root,
                operation,
                parameters,
                (SFT_BATCHES[0],),
                random_seed=1,
                window_limit_bytes=32 * 1024,
                delta_precision=precision,
            )
        assert caught.value.code == "TRAINING_UNSUPPORTED"
    with pytest.raises(CassetteError) as caught:
        prepare_training(
            source,
            parent_root,
            "ADAPTER_SFT",
            parameters,
            ((float("nan"), *SFT_BATCHES[0][1:]),),
            random_seed=1,
            window_limit_bytes=32 * 1024,
        )
    assert caught.value.code == "INVALID_REQUEST"
    assert before_refusal == {
        str(path.relative_to(source)): digest_bytes(path.read_bytes())
        for path in source.rglob("*") if path.is_file()
    }

    compiled, compiled_root, compiled_parameters = _compiled_parent(tmp_path / "tier-b-source")
    alternate = tmp_path / "tier-b-alternate"
    missing = tmp_path / "tier-b-missing"
    shutil.copytree(compiled, alternate)
    shutil.copytree(compiled, missing)
    calibrations = _calibration_records("s21")
    broker = CanonicalBroker(tmp_path / "operations")
    compiled_record = load_root(compiled, compiled_root)
    profile = _profile("s21-tier-b")
    profile.update(
        model_revision=compiled_record["identity"],
        source_parent=compiled_record["parents"][0],
        plan_id=compiled_record["plans"][0]["execution_plan"]["plan_id"],
        training_tier="B",
        precision=compiled_record["provenance"]["identity_material"]["precision_scheme"],
    )

    async def activate(lease: ScheduledLease, capability: dict) -> None:
        assert lease.kind == "SWITCH"
        assert capability["model_revision"] == compiled_record["identity"]

    broker.register_capability(
        "model/s21-tier-b", profile, activate, schedule=_schedule(profile, 0),
        cartridge=compiled, root_digest=compiled_root,
    )
    negotiation = broker.negotiate({"model_ref": "model/s21-tier-b", "training_tier": "B"})
    request = _request(negotiation, "s21-tier-b", "context-s21-tier-b", operation="train")

    def recover() -> dict:
        checkpoint = prepare_training(
            compiled,
            compiled_root,
            "COMPILED_RECOVERY",
            compiled_parameters,
            (RECOVERY_BATCH,),
            random_seed=71,
            window_limit_bytes=32 * 1024,
            calibration_records=calibrations,
        )
        return commit_training(compiled, advance_training(compiled, checkpoint), "s21-tier-b-child").record()

    async def worker(lease: ScheduledLease) -> dict:
        assert lease.kind == "WRITE"
        return await asyncio.to_thread(recover)

    dispatched = asyncio.run(broker.dispatch(
        "trainer", "context-s21-tier-b", request, negotiation, "WRITE", worker
    ))
    broker.close()
    assert dispatched["state"] == "SUCCEEDED", dispatched
    result = dispatched["result"]["value"]
    artifact = load_training_artifact(compiled, result["root_digest"])
    assert result["committed_boundary"] == result["child_id"]
    assert artifact["parent_certificate_digest"] == compiled_record["plans"][0]["certificate"]["certificate_id"]
    assert artifact["operator_cases"] == [
        "mlx.autograd_calibration_mse.f32.1_2x3_3x2_2x2_1", "mlx.sgd.f32.1",
    ]
    assert artifact["adapter_rank"] is None and artifact["adapter_scale"] is None
    assert [row["parameter_id"] for row in artifact["delta_pages"]] == [
        f"recovery.{kind}"
        for kind in ("condition", "atom", "description", "estimator", "observation", "precision")
    ]
    assert load_root(compiled, result["root_digest"])["deltas"][-1]["kind"] == "certificate_recovery"
    assert json.loads(read_training_page(
        compiled, result["root_digest"], artifact["state_pages"]["optimizer"]
    ))["case_id"] == "mlx.sgd.f32.1"
    assert not _contains_certificate(artifact)
    assert json.loads(read_training_page(
        compiled, result["root_digest"], artifact["objective_pages"][0]["page_digest"]
    ))["role"] == "certificate_recovery"
    observed_calibrations = tuple(
        json.loads(read_training_page(compiled, result["root_digest"], row["page_digest"]))["record"]
        for row in artifact["calibration_pages"]
    )
    assert observed_calibrations == calibrations
    expected_recovery = _expected_payloads(
        compiled,
        artifact,
        (RECOVERY_BATCH,),
        tuple(float(row["loss"]) for row in calibrations),
    )
    observed_recovery = _delta_payloads(compiled, result["root_digest"], artifact)
    assert set(observed_recovery) == set(expected_recovery)
    for parameter_id in observed_recovery:
        assert observed_recovery[parameter_id] == pytest.approx(
            expected_recovery[parameter_id], abs=1e-6, rel=0.0
        )
    _replay_traces(compiled, result["root_digest"], artifact)

    changed_calibrations = tuple(
        {**row, "loss": "0.9" if row["kind"] == "condition" else row["loss"]}
        for row in calibrations
    )
    _, alternate_artifact = _train(
        alternate,
        compiled_root,
        compiled_parameters,
        "COMPILED_RECOVERY",
        (RECOVERY_BATCH,),
        "s21-tier-b-alternate",
        calibrations=changed_calibrations,
    )
    assert _delta_payloads(compiled, result["root_digest"], artifact) != _delta_payloads(
        alternate, pin_generation(alternate).root_digest, alternate_artifact
    )
    with pytest.raises(CassetteError) as caught:
        prepare_training(
            missing,
            compiled_root,
            "COMPILED_RECOVERY",
            compiled_parameters,
            (RECOVERY_BATCH,),
            random_seed=72,
            window_limit_bytes=32 * 1024,
            calibration_records=calibrations[:-1],
        )
    assert caught.value.code == "TRAINING_UNSUPPORTED"


def test_q22_q25_q73_hostile_checkpoints_never_replace_the_frozen_parent(tmp_path):
    """Q22/Q25/Q73 acceptance: restart is exact, the parent stays immutable, and resealed hostile checkpoints cannot commit."""

    cartridge, parent_root, parameters = _quantized_parent(tmp_path / "durable-source")
    parent_pin = pin_generation(cartridge)
    parent_record = load_root(cartridge, parent_root)
    parent_pages = {
        location.page_digest: read_training_page(cartridge, parent_root, location.page_digest)
        for location in page_locations(cartridge, parent_root)
    }
    initial = prepare_training(
        cartridge,
        parent_root,
        "ADAPTER_SFT",
        parameters,
        SFT_BATCHES,
        random_seed=17,
        window_limit_bytes=32 * 1024,
    )
    assert pin_generation(cartridge) == parent_pin
    control = tmp_path / "control-cartridge"
    resumed = tmp_path / "resumed-cartridge"
    shutil.copytree(cartridge, control)
    shutil.copytree(cartridge, resumed)
    control_checkpoint = _run(initial, control)
    _kill_before_checkpoint_root(resumed, initial)
    resumed_checkpoint = _run(initial, resumed)
    assert resumed_checkpoint == control_checkpoint
    control_result = commit_training(control, control_checkpoint, "s21-sft-child")
    resumed_result = commit_training(resumed, resumed_checkpoint, "s21-sft-child")
    assert resumed_result == control_result
    assert load_training_artifact(control, control_result.root_digest) == load_training_artifact(
        resumed, resumed_result.root_digest
    )
    restart = load_transaction_context(control, "s21-sft-child")
    assert (restart.optimizer_step, restart.data_cursor, restart.random_seed) == (2, 2, 17)
    assert load_root(control, parent_root) == parent_record
    assert {
        digest: read_training_page(control, parent_root, digest) for digest in parent_pages
    } == parent_pages
    child = load_root(control, control_result.root_digest)
    assert child["parents"] == [parent_record["identity"]]
    assert child["deltas"][-1]["base_identity"] == parent_record["identity"]
    assert rollback_generation(resumed, "s21-rollback").root_digest == parent_root

    def restart_case(
        label: str,
        source: Path,
        root_digest: str,
        parameter_rows: tuple[tuple[str, str], ...],
        operation: str,
        batches: tuple[tuple[float, ...], ...],
        *,
        precision: str = "FP32",
        calibrations: tuple[dict, ...] = (),
    ) -> None:
        prepared = prepare_training(
            source,
            root_digest,
            operation,
            parameter_rows,
            batches,
            random_seed=29,
            window_limit_bytes=32 * 1024,
            calibration_records=calibrations,
            delta_precision=precision,
        )
        uninterrupted = tmp_path / f"restart-{label}-control"
        interrupted = tmp_path / f"restart-{label}-interrupted"
        shutil.copytree(source, uninterrupted)
        shutil.copytree(source, interrupted)
        expected_checkpoint = _run(prepared, uninterrupted)
        _kill_before_checkpoint_root(interrupted, prepared)
        observed_checkpoint = _run(prepared, interrupted)
        assert observed_checkpoint == expected_checkpoint
        expected_result = commit_training(
            uninterrupted, expected_checkpoint, f"s21-restart-{label}"
        )
        observed_result = commit_training(
            interrupted, observed_checkpoint, f"s21-restart-{label}"
        )
        assert observed_result == expected_result
        assert load_training_artifact(
            interrupted, observed_result.root_digest
        ) == load_training_artifact(uninterrupted, expected_result.root_digest)

    restart_source, restart_root, restart_parameters = _quantized_parent(
        tmp_path / "restart-tier-a-source"
    )
    restart_case(
        "sft-bf16",
        restart_source,
        restart_root,
        restart_parameters,
        "ADAPTER_SFT",
        (SFT_BATCHES[0],),
        precision="BF16",
    )
    for label, operation, batches in (
        ("continued", "ADAPTER_CONTINUED_PRETRAINING", (CONTINUATION_BATCH,)),
        ("dpo", "OFFLINE_ADAPTER_DPO", (PREFERENCE_BATCH,)),
    ):
        source, root_digest, parameter_rows = _quantized_parent(
            tmp_path / f"restart-{label}-source"
        )
        restart_case(label, source, root_digest, parameter_rows, operation, batches)
    compiled, compiled_root, compiled_parameters = _compiled_parent(
        tmp_path / "restart-tier-b-source"
    )
    restart_case(
        "compiled-recovery",
        compiled,
        compiled_root,
        compiled_parameters,
        "COMPILED_RECOVERY",
        (RECOVERY_BATCH,),
        calibrations=_calibration_records("restart"),
    )

    attack_source = tmp_path / "attack-source"
    shutil.copytree(cartridge, attack_source)
    first_step = advance_training(attack_source, initial)
    mutations = {
        "hidden-master": lambda manifest, _: manifest["master_pages"].append(
            manifest["objective_pages"][0]["page_digest"]
        ),
        "cursor-drift": lambda manifest, _: manifest.__setitem__(
            "data_cursor", manifest["data_cursor"] + 1
        ),
        "missing-trace": lambda manifest, _: manifest["trace_pages"].clear(),
        "peak-over-limit": lambda manifest, _: manifest.__setitem__(
            "declared_peak_bytes", manifest["window_limit_bytes"] + 1
        ),
        "page-tuple": lambda manifest, _: manifest["delta_pages"][0].__setitem__(
            "parameter_id", "foreign.adapter"
        ),
        "base-tuple": lambda manifest, _: manifest["base_pages"][0].__setitem__(
            "tensor_id", "foreign.weight"
        ),
        "codec-tuple": lambda manifest, _: manifest["base_pages"][0].__setitem__(
            "codec", {"name": "i8-symmetric", "scale": "0.5", "zero_point": 0}
        ),
    }
    for name, mutation in mutations.items():
        hostile = tmp_path / f"hostile-{name}"
        shutil.copytree(attack_source, hostile)
        forged = _forge_checkpoint(hostile, first_step, mutation)
        with pytest.raises(CassetteError) as caught:
            advance_training(hostile, forged)
        assert caught.value.code in {"GRADIENT_INVALID", "MEMORY_BUDGET_EXCEEDED", "ROOT_INVALID", "TRAINING_UNSUPPORTED"}
        assert pin_generation(hostile) == parent_pin

    adapter = json.loads(read_training_page(
        attack_source, first_step.work_root, _manifest(attack_source, first_step)["delta_pages"][0]["page_digest"]
    ))
    corruptions = {
        "nonfinite": (("0000c07f" * 5) + "00000000", "adapter tensor contains NaN or infinity"),
        "wrong-arity": ("00000000", "adapter tensor page disagrees with its declared tuple"),
    }
    for name, (encoded, expected_detail) in corruptions.items():
        hostile = tmp_path / f"hostile-{name}"
        shutil.copytree(attack_source, hostile)
        bad_page = canonical_bytes({**adapter, "payload_hex": encoded})

        def replace_page(manifest, locations):
            manifest["delta_pages"][0]["page_digest"] = locations[0].page_digest
            journal = canonical_bytes({
                "format": "cassette-training-v1",
                "role": "journal",
                "job_id": manifest["job_id"],
                "step": manifest["step"],
                "status": "STEP_COMPLETE",
                "ordered_delta_pages": [row["page_digest"] for row in manifest["delta_pages"]],
            })
            journal_location = stage_training_pages(hostile, (journal,))[0]
            manifest["state_pages"]["journal"] = journal_location.page_digest
            return (journal_location,)

        forged = _forge_checkpoint(hostile, first_step, replace_page, (bad_page,))
        with pytest.raises(CassetteError) as caught:
            advance_training(hostile, forged)
        assert caught.value.code in {"GRADIENT_INVALID", "ROOT_INVALID"}
        assert expected_detail in caught.value.detail
        assert pin_generation(hostile) == parent_pin

    overflow = prepare_training(
        cartridge,
        parent_root,
        "ADAPTER_SFT",
        parameters,
        ((3.0e38,) * 10,),
        random_seed=1,
        window_limit_bytes=32 * 1024,
    )
    with pytest.raises(CassetteError) as caught:
        advance_training(cartridge, overflow)
    assert caught.value.code == "GRADIENT_INVALID"
    assert "non-finite or malformed delta" in caught.value.detail

    low_memory = prepare_training(
        cartridge,
        parent_root,
        "ADAPTER_SFT",
        parameters,
        (SFT_BATCHES[0],),
        random_seed=1,
        window_limit_bytes=1,
    )
    before = {path: path.stat().st_size for path in cartridge.rglob("*") if path.is_file()}
    with pytest.raises(CassetteError) as caught:
        advance_training(cartridge, low_memory)
    assert caught.value.code == "MEMORY_BUDGET_EXCEEDED"
    assert before == {path: path.stat().st_size for path in cartridge.rglob("*") if path.is_file()}


def test_q23_q71_q72_trace_and_unpaged_oracle_cover_every_live_tensor_window(tmp_path):
    """Q23/Q71/Q72 acceptance: drive-resident paged updates equal an independent unpaged oracle and their live intervals replay exactly."""

    source, parent_root, parameters = _quantized_parent(tmp_path / "oracle-source")
    cases = (
        ("ADAPTER_SFT", SFT_BATCHES, "FP32"),
        ("ADAPTER_SFT", SFT_BATCHES, "BF16"),
        ("ADAPTER_CONTINUED_PRETRAINING", (CONTINUATION_BATCH,), "FP32"),
        ("OFFLINE_ADAPTER_DPO", (PREFERENCE_BATCH,), "FP32"),
    )
    roots = []
    for ordinal, (operation, batches, precision) in enumerate(cases):
        cartridge = tmp_path / f"oracle-{ordinal}"
        shutil.copytree(source, cartridge)
        _, artifact = _train(
            cartridge,
            parent_root,
            parameters,
            operation,
            batches,
            f"s21-oracle-{ordinal}",
            precision=precision,
        )
        root_digest = pin_generation(cartridge).root_digest
        observed = _delta_payloads(cartridge, root_digest, artifact)
        expected = _expected_payloads(cartridge, artifact, batches)
        tolerance = 1e-6 if precision == "FP32" else 0.0
        assert set(observed) == set(expected)
        for parameter_id in observed:
            assert observed[parameter_id] == pytest.approx(
                expected[parameter_id], abs=tolerance, rel=0.0
            )
        _replay_traces(cartridge, root_digest, artifact)
        for trace_digest in artifact["trace_pages"]:
            trace = json.loads(read_training_page(cartridge, root_digest, trace_digest))
            actions = [(row["action"], row["tensor_id"]) for row in trace["events"]]
            for parameter_id in [row["parameter_id"] for row in artifact["delta_pages"]]:
                assert actions.index(("LOAD", f"base:{parameter_id}")) < actions.index(
                    ("PRODUCE", f"gradient:{parameter_id}")
                )
                assert actions.index(("PERSIST", f"child:{parameter_id}")) < actions.index(
                    ("RETIRE", f"base:{parameter_id}")
                )
        roots.append(cartridge)

    tree = ast.parse((Path(__file__).resolve().parent.parent / "trainer.py").read_text())
    update = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "_update_delta"
    )
    numerical_closures = [
        node for node in ast.walk(update)
        if isinstance(node, ast.FunctionDef) and node.name in {"effective", "loss"}
    ]
    assert numerical_closures
    assert not [
        node
        for function in numerical_closures
        for node in ast.walk(function)
        if isinstance(node, (ast.BinOp, ast.UnaryOp))
    ]
    imports = {
        node.names[0].name.split(".", 1)[0]
        for node in ast.walk(tree) if isinstance(node, ast.Import)
    } | {
        (node.module or "").split(".", 1)[0]
        for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
    }
    calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    } | {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert not imports & {"os", "pathlib", "tempfile"}
    assert not calls & {"open", "Path", "read_bytes", "write_bytes", "NamedTemporaryFile"}
    local_path = str(tmp_path).encode()
    assert all(
        local_path not in path.read_bytes()
        for cartridge in roots
        for path in cartridge.rglob("*") if path.is_file()
    )


def _child_kill(cartridge: str, checkpoint_payload: str) -> None:
    checkpoint = TrainingCheckpoint(**json.loads(checkpoint_payload))

    def boundary(*args, **kwargs):
        print("BOUNDARY:CHECKPOINT_ROOT", flush=True)
        signal.pause()

    trainer_module.append_staged_training_delta = boundary
    advance_training(cartridge, checkpoint)


if __name__ == "__main__" and len(sys.argv) == 4 and sys.argv[1] == "_s21_kill":
    _child_kill(sys.argv[2], sys.argv[3])
