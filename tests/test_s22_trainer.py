# test_s22_trainer.py — S22 training write projection, resource admission, and checkpoint metering fixture; depends on errors.py, store.py, trainer.py, tests/test_s21_trainer.py.
"""Disprove admission or continuation whenever one Q28/Q74 resource claim fails."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

import pytest

from errors import CassetteError
from store import canonical_bytes, digest_bytes, read_training_page, release_capacity
from test_s21_trainer import (
    SFT_BATCHES,
    _manifest as training_manifest,
    _quantized_parent,
    prepare_training as prepare_paged_training,
)
import trainer as trainer_module
from trainer import (
    TrainingObservation,
    TrainingResourceProfile,
    TrainingWorkload,
    admit_training,
    assess_training_observation,
    prepare_training,
)


GIB = 1024**3
MIB = 1024**2


class ExtentPool:
    """Record the exact reservation boundary without simulating storage behavior."""

    def __init__(self, available: int) -> None:
        self.available = available
        self.reserved: list[int] = []
        self.released: list[int] = []

    def reserve(self, length: int) -> bool:
        if length > self.available:
            return False
        self.available -= length
        self.reserved.append(length)
        return True

    def release(self, length: int) -> bool:
        self.available += length
        self.released.append(length)
        return True


def _workload(**changes) -> TrainingWorkload:
    values = {
        "request_digest": digest_bytes(b"s22-training-request"),
        "committed_bytes": 2 * GIB,
        "rollback_bytes": GIB,
        "dataset_bytes": 512 * MIB,
        "candidate_bytes": GIB,
        "optimizer_bytes": 256 * MIB,
        "master_bytes": 128 * MIB,
        "journal_bytes": 64 * MIB,
        "read_bytes": 4 * GIB,
        "memory_peak_bytes": 2 * GIB,
        "optimizer_steps": 8,
        "trainable_parameters": 1024,
        "weight_bytes_per_parameter": 4,
        "checkpoint_interval": 2,
    }
    values.update(changes)
    return TrainingWorkload(**values)


def _profile(**changes) -> TrainingResourceProfile:
    values = {
        "profile_evidence_digest": digest_bytes(b"s22-cache-exhausted-mixed-training-profile"),
        "device_bytes": 100 * GIB,
        "physical_memory_bytes": 32 * GIB,
        "recommended_max_working_set_bytes": 24 * GIB,
        "executor_memory_bytes": GIB,
        "other_memory_bytes": GIB,
        "sustained_read_bytes_per_second": GIB,
        "sustained_write_bytes_per_second": 512 * MIB,
        "minimum_sustained_read_bytes_per_second": 512 * MIB,
        "minimum_sustained_write_bytes_per_second": 256 * MIB,
        "write_amplification_p95_numerator": 3,
        "write_amplification_p95_denominator": 2,
        "declared_endurance_bytes": 100 * GIB,
        "lifetime_written_bytes": 10 * GIB,
        "predicted_thermal_duty_ppm": 400_000,
        "maximum_thermal_duty_ppm": 800_000,
        "maximum_write_duty_ppm": 800_000,
        "external_power": True,
        "job_limit_seconds": 10_000,
        "compute_nanoseconds_per_update_p95": 1_000_000,
    }
    values.update(changes)
    return TrainingResourceProfile(**values)


def _admit(workload=None, profile=None):
    selected_workload = _workload() if workload is None else workload
    selected_profile = _profile() if profile is None else profile
    pool = ExtentPool(20 * GIB)
    admission = admit_training(
        selected_workload,
        selected_profile,
        allocatable_verified_free=pool.available,
        reserve_extent=pool.reserve,
        release_extent=pool.release,
    )
    return admission, pool


def _observation(
    admission,
    *,
    prior=None,
    checkpoint=0,
    logical_write_bytes=512 * MIB,
    read_bytes=GIB,
    physical_write_bytes=768 * MIB,
    elapsed_nanoseconds=3_000_000_000,
    sustained_read_bytes_per_second=GIB,
    sustained_write_bytes_per_second=512 * MIB,
    thermal_duty_ppm=400_000,
    write_duty_ppm=500_000,
    external_power=True,
):
    observation = TrainingObservation(
        checkpoint,
        logical_write_bytes,
        read_bytes,
        physical_write_bytes,
        elapsed_nanoseconds,
        sustained_read_bytes_per_second,
        sustained_write_bytes_per_second,
        thermal_duty_ppm,
        write_duty_ppm,
        external_power,
    )
    return assess_training_observation(
        admission,
        logical_write_bytes=logical_write_bytes,
        read_bytes=read_bytes,
        prior=prior,
        observation=observation,
    )


def test_q28_projected_and_metered_writes_share_one_exact_endurance_envelope(tmp_path):
    """Q28: derive projection, admit equality, and prove every live and durable meter bound."""

    logical = 512 * MIB + GIB + 256 * MIB + 128 * MIB + 64 * MIB
    physical = logical * 3 // 2
    boundary_profile = _profile(
        declared_endurance_bytes=20 * physical,
        lifetime_written_bytes=15 * physical,
    )
    admission, pool = _admit(profile=boundary_profile)
    estimate = admission.estimate

    phase = 2 * GIB + GIB + 512 * MIB + GIB + 256 * MIB + 128 * MIB + 64 * MIB
    required = phase + 8 * GIB
    assert estimate.logical_write_bytes == logical
    assert estimate.physical_write_p95 == physical
    assert estimate.S_required == required
    assert estimate.M_peak == 2 * GIB
    assert estimate.duration_p95 == 10
    assert estimate.write_duty == 581_250
    assert pool.reserved == [required]
    assert boundary_profile.lifetime_written_bytes + physical == (
        boundary_profile.declared_endurance_bytes * 4 // 5
    )
    assert physical == (
        boundary_profile.declared_endurance_bytes - boundary_profile.lifetime_written_bytes
    ) // 5

    accepted = _observation(admission)
    assert accepted.physical_write_bytes == 768 * MIB

    with pytest.raises(CassetteError) as drift:
        _observation(admission, physical_write_bytes=768 * MIB + 1)
    assert drift.value.code == "ENDURANCE_EXCEEDED"
    assert "p95 projection" in drift.value.detail

    mismatched = replace(accepted, logical_write_bytes=accepted.logical_write_bytes + 1)
    with pytest.raises(CassetteError) as foreign_meter:
        assess_training_observation(
            admission,
            logical_write_bytes=accepted.logical_write_bytes,
            read_bytes=accepted.read_bytes,
            prior=None,
            observation=mismatched,
        )
    assert foreign_meter.value.code == "INVALID_REQUEST"

    release_capacity(admission.reservation)
    release_capacity(admission.reservation)
    assert pool.released == [required]
    assert pool.available == 20 * GIB

    calls = []
    with pytest.raises(CassetteError) as beyond_boundary:
        admit_training(
            _workload(),
            replace(boundary_profile, lifetime_written_bytes=15 * physical + 1),
            allocatable_verified_free=20 * GIB,
            reserve_extent=lambda length: calls.append(length) or True,
            release_extent=lambda _length: True,
        )
    assert beyond_boundary.value.code == "ENDURANCE_EXCEEDED"
    assert calls == []

    odd_workload = _workload(journal_bytes=64 * MIB + 1)
    odd_admission, odd_pool = _admit(odd_workload)
    assert odd_admission.estimate.physical_write_p95 == (
        odd_admission.estimate.logical_write_bytes * 3 + 1
    ) // 2
    release_capacity(odd_admission.reservation)
    assert odd_pool.released == [odd_admission.estimate.S_required]

    metered, meter_pool = _admit()
    meter_estimate = metered.estimate
    for label, changes in (
        (
            "live logical estimate",
            {
                "logical_write_bytes": meter_estimate.logical_write_bytes + 1,
                "read_bytes": 0,
            },
        ),
        (
            "live read estimate",
            {
                "logical_write_bytes": 0,
                "read_bytes": meter_estimate.read_bytes + 1,
            },
        ),
    ):
        with pytest.raises(CassetteError) as over_estimate:
            _observation(
                metered,
                physical_write_bytes=0,
                elapsed_nanoseconds=0,
                **changes,
            )
        assert over_estimate.value.code == "ENDURANCE_EXCEEDED", label
        assert "complete admitted estimate" in over_estimate.value.detail, label
    release_capacity(metered.reservation)
    assert meter_pool.released == [metered.estimate.S_required]

    sequenced, sequence_pool = _admit()
    first = _observation(
        sequenced,
        logical_write_bytes=512 * MIB,
        read_bytes=GIB,
        physical_write_bytes=600 * MIB,
        elapsed_nanoseconds=3_000_000_000,
    )
    increasing = {
        "logical_write_bytes": 600 * MIB,
        "read_bytes": 2 * GIB,
        "physical_write_bytes": 650 * MIB,
        "elapsed_nanoseconds": 4_000_000_000,
    }
    for field, value in (
        ("logical_write_bytes", first.logical_write_bytes - 1),
        ("read_bytes", first.read_bytes - 1),
        ("physical_write_bytes", first.physical_write_bytes - 1),
        ("elapsed_nanoseconds", first.elapsed_nanoseconds - 1),
    ):
        with pytest.raises(CassetteError) as decreasing:
            _observation(
                sequenced,
                prior=first,
                checkpoint=1,
                **{**increasing, field: value},
            )
        assert decreasing.value.code == "INVALID_REQUEST", field
        assert "advance monotonically" in decreasing.value.detail, field
    release_capacity(sequenced.reservation)
    assert sequence_pool.released == [sequenced.estimate.S_required]

    cartridge, parent_root, parameters = _quantized_parent(tmp_path / "metered-checkpoint")
    checkpoint = prepare_paged_training(
        cartridge,
        parent_root,
        "ADAPTER_SFT",
        parameters,
        SFT_BATCHES,
        random_seed=22,
        window_limit_bytes=32 * 1024,
    )
    manifest = training_manifest(cartridge, checkpoint)
    manifest_payload = canonical_bytes(manifest)
    material_digests = [
        *[row["page_digest"] for row in manifest["objective_pages"]],
        *[row["page_digest"] for row in manifest["calibration_pages"]],
        *[row["page_digest"] for row in manifest["delta_pages"]],
        *manifest["state_pages"].values(),
    ]
    material_bytes = sum(
        len(read_training_page(cartridge, checkpoint.work_root, page_digest))
        for page_digest in material_digests
    )
    assert manifest["meter"]["logical_write_bytes"] == material_bytes + len(manifest_payload)

    for field in ("logical_write_bytes", "read_bytes"):
        forged_manifest = deepcopy(manifest)
        forged_manifest["meter"][field] = forged_manifest["admission"]["estimate"][field] + 1
        with pytest.raises(CassetteError) as forged_meter:
            trainer_module._manifest_shape(forged_manifest, f"s22:durable:{field}")
        assert forged_meter.value.code == "ENDURANCE_EXCEEDED", field
        assert "durable meter" in forged_meter.value.detail, field


def test_q74_injections_refuse_before_start_or_at_one_recoverable_boundary():
    """Q74: low space, false endurance, power loss, heat, slow writes, and drift all fail typed."""

    with pytest.raises(CassetteError) as absent_admission:
        prepare_training(
            object(),
            "not-a-root",
            "ADAPTER_SFT",
            (),
            (),
            random_seed=0,
            window_limit_bytes=1,
        )
    assert absent_admission.value.code == "INVALID_REQUEST"
    assert absent_admission.value.object_id == "training:admission"

    projected_physical = 2_976 * MIB
    preflight = (
        ("low space", _workload(), _profile(), 12 * GIB, "CAPACITY_EXCEEDED"),
        ("zero space", _workload(), _profile(), 0, "CAPACITY_EXCEEDED"),
        (
            "unknown endurance",
            _workload(),
            _profile(declared_endurance_bytes=None),
            20 * GIB,
            "ENDURANCE_EXCEEDED",
        ),
        (
            "unknown health",
            _workload(),
            _profile(lifetime_written_bytes=None),
            20 * GIB,
            "ENDURANCE_EXCEEDED",
        ),
        (
            "false endurance",
            _workload(),
            _profile(declared_endurance_bytes=16 * GIB, lifetime_written_bytes=13 * GIB),
            20 * GIB,
            "ENDURANCE_EXCEEDED",
        ),
        (
            "raw update floor",
            _workload(candidate_bytes=32_767),
            _profile(),
            20 * GIB,
            "ENDURANCE_EXCEEDED",
        ),
        (
            "lifetime exceeds endurance",
            _workload(),
            _profile(
                declared_endurance_bytes=100 * GIB,
                lifetime_written_bytes=100 * GIB + 1,
            ),
            20 * GIB,
            "ENDURANCE_EXCEEDED",
        ),
        (
            "eighty-percent lifetime ceiling",
            _workload(),
            _profile(
                declared_endurance_bytes=100 * projected_physical,
                lifetime_written_bytes=79 * projected_physical + 1,
            ),
            20 * GIB,
            "ENDURANCE_EXCEEDED",
        ),
        (
            "one-fifth remaining-endurance ceiling",
            _workload(),
            _profile(
                declared_endurance_bytes=4 * projected_physical,
                lifetime_written_bytes=0,
            ),
            20 * GIB,
            "ENDURANCE_EXCEEDED",
        ),
        (
            "write sum overflow",
            _workload(
                dataset_bytes=2**52,
                candidate_bytes=2**52,
                optimizer_bytes=2**52,
                master_bytes=2**52,
                journal_bytes=2**52,
            ),
            _profile(),
            20 * GIB,
            "CAPACITY_EXCEEDED",
        ),
        (
            "malformed request identity",
            _workload(request_digest=7),
            _profile(),
            20 * GIB,
            "INVALID_REQUEST",
        ),
        (
            "memory peak",
            _workload(memory_peak_bytes=20 * GIB),
            _profile(),
            20 * GIB,
            "MEMORY_BUDGET_EXCEEDED",
        ),
        (
            "unqualified storage",
            _workload(),
            _profile(sustained_write_bytes_per_second=256 * MIB - 1),
            20 * GIB,
            "CAPABILITY_MISMATCH",
        ),
        (
            "predicted thermal knee",
            _workload(),
            _profile(predicted_thermal_duty_ppm=800_000),
            20 * GIB,
            "THERMAL_LIMIT",
        ),
        (
            "declared completion limit",
            _workload(),
            _profile(job_limit_seconds=9),
            20 * GIB,
            "CAPABILITY_MISMATCH",
        ),
        (
            "missing compute measurement",
            _workload(),
            _profile(compute_nanoseconds_per_update_p95=0),
            20 * GIB,
            "INVALID_REQUEST",
        ),
        (
            "missing thermal measurement",
            _workload(),
            _profile(predicted_thermal_duty_ppm=0),
            20 * GIB,
            "INVALID_REQUEST",
        ),
        (
            "missing required power",
            _workload(read_bytes=2 * 1024 * GIB),
            _profile(external_power=False),
            20 * GIB,
            "OPERATION_CANCELLED",
        ),
    )
    for label, workload, profile, free, code in preflight:
        calls = []
        with pytest.raises(CassetteError) as refused:
            admit_training(
                workload,
                profile,
                allocatable_verified_free=free,
                reserve_extent=lambda length: calls.append(length) or True,
                release_extent=lambda _length: True,
            )
        assert refused.value.code == code, label
        if label == "lifetime exceeds endurance":
            assert refused.value.detail == "reported lifetime writes exceed declared endurance"
        assert calls == [], label

    admission, pool = _admit()
    runtime = (
        ("thermal throttle", {"thermal_duty_ppm": 720_000}, "THERMAL_LIMIT", "retryable"),
        ("thermal stop", {"thermal_duty_ppm": 800_000}, "THERMAL_LIMIT", "terminal"),
        ("write throttle", {"write_duty_ppm": 720_000}, "OVERLOADED", "retryable"),
        (
            "write stop",
            {"write_duty_ppm": 800_000},
            "ENDURANCE_EXCEEDED",
            "terminal",
        ),
        (
            "slow writes",
            {"sustained_write_bytes_per_second": 256 * MIB - 1},
            "OVERLOADED",
            "retryable",
        ),
        (
            "estimate drift",
            {"physical_write_bytes": 768 * MIB + 1},
            "ENDURANCE_EXCEEDED",
            "terminal",
        ),
        (
            "completion drift",
            {"elapsed_nanoseconds": 10_000_000_000_000},
            "OVERLOADED",
            "retryable",
        ),
    )
    for label, changes, code, retryability in runtime:
        with pytest.raises(CassetteError) as refused:
            _observation(admission, **changes)
        assert (refused.value.code, refused.value.retryability) == (code, retryability), label
    with pytest.raises(CassetteError) as forged_admission:
        _observation(replace(admission, reservation=object()))
    assert forged_admission.value.code == "INVALID_REQUEST"
    for forged in (
        replace(
            admission,
            profile=replace(admission.profile, sustained_write_bytes_per_second=300 * MIB),
        ),
        replace(
            admission,
            estimate=replace(admission.estimate, physical_write_p95=1),
        ),
    ):
        with pytest.raises(CassetteError) as detached_evidence:
            _observation(forged)
        assert detached_evidence.value.code == "ROOT_INVALID"
    release_capacity(admission.reservation)
    assert pool.released == [admission.estimate.S_required]
    with pytest.raises(CassetteError) as released_admission:
        _observation(admission)
    assert released_admission.value.code == "INVALID_REQUEST"

    long_workload = _workload(read_bytes=2 * 1024 * GIB)
    long_admission, long_pool = _admit(long_workload)
    assert long_admission.estimate.power_required is True
    with pytest.raises(CassetteError) as power_loss:
        _observation(
            long_admission,
            logical_write_bytes=0,
            read_bytes=0,
            physical_write_bytes=0,
            elapsed_nanoseconds=0,
            external_power=False,
        )
    assert (power_loss.value.code, power_loss.value.retryability) == (
        "OPERATION_CANCELLED",
        "retryable",
    )
    release_capacity(long_admission.reservation)
    assert long_pool.released == [long_admission.estimate.S_required]

    sequenced, sequence_pool = _admit()
    first = _observation(sequenced)
    forged = replace(first, checkpoint=2)
    with pytest.raises(CassetteError) as skipped_boundary:
        assess_training_observation(
            sequenced,
            logical_write_bytes=forged.logical_write_bytes,
            read_bytes=forged.read_bytes,
            prior=first,
            observation=forged,
        )
    assert skipped_boundary.value.code == "INVALID_REQUEST"
    release_capacity(sequenced.reservation)
    assert sequence_pool.released == [sequenced.estimate.S_required]
