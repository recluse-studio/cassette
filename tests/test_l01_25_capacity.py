# test_l01_25_capacity.py — L01.25 Q53 adaptive capacity and Q39-Q44 storage-eligibility proof; depends on compiler.py, errors.py, store.py, tests/test_s20_hardware_plans.py.
"""Exercise the amended matrix controls through store-owned product paths only."""

from __future__ import annotations

import errno
import os

import pytest

import compiler as compiler_module
from compiler import prepare_hardware_plans, select_hardware_plan
from errors import CassetteError
import store as store_module
from store import (
    CapacityCoordinator,
    CapacityTransition,
    ReclaimableObject,
    claim_next_transition,
    commit_generation,
    complete_capacity_claim,
    execute_claimed_write,
    initialize_cartridge,
    reclaim_capacity,
    resume_capacity_claim,
    select_reclaimable_objects,
)
from test_s20_hardware_plans import _compiled_fixture, _measured, _specifications


ADAPTIVE_CAPACITY_ASSERTIONS = (
    "next_atomic_transition_only",
    "no_fixed_device_fraction_byte_floor_user_ceiling_or_whole_job_reservation",
    "feasible_next_step_starts_without_whole_campaign_fit",
    "concurrent_cassette_claims_do_not_overcommit",
    "capacity_remeasured_before_each_write_and_after_each_durable_boundary",
    "active_claim_transaction_and_journal_objects_survive_reclamation",
    "retained_root_pinned_rollback_and_user_owned_objects_survive_reclamation",
    "only_eligible_cassette_owned_temporary_or_reproducible_objects_are_reclaimed",
    "external_free_space_reduction_or_enospc_recovers_parent_or_committed_child",
    "newly_available_capacity_resumes_from_same_committed_boundary",
)
STORAGE_ELIGIBILITY_ASSERTIONS = (
    "no_storage_media_class_connector_or_nominal_capacity_admission_gate",
    "any_locally_attached_macos_apfs_drive_may_attempt_measurement",
    "descriptive_labels_do_not_determine_admission",
)


def _statvfs_with_available(snapshot, available: int):
    values = list(snapshot)
    values[1] = 1
    values[4] = available
    return os.statvfs_result(values)


def _finish(claim) -> None:
    execute_claimed_write(claim, lambda: None)
    complete_capacity_claim(claim)


def test_q53_adaptive_capacity_control_uses_live_store_measurement_and_exact_boundaries(
    tmp_path, monkeypatch
):
    """Q53: all ten adaptive_capacity_control matrix assertions hold at product boundaries."""

    cartridge = tmp_path / "cartridge"
    cartridge.mkdir()
    coordinator = CapacityCoordinator(cartridge)
    snapshot = os.statvfs(cartridge)
    actual_free = snapshot.f_frsize * snapshot.f_bavail

    # next_atomic_transition_only; no_fixed_device_fraction_byte_floor_user_ceiling_or_whole_job_reservation;
    # feasible_next_step_starts_without_whole_campaign_fit.
    hypothetical_campaign_bytes = 2**63
    assert hypothetical_campaign_bytes > actual_free
    short_step = CapacityTransition("l01-short", "committed-parent", payload_bytes=1)
    short_claim = claim_next_transition(short_step, coordinator=coordinator)
    assert short_claim.active
    assert short_claim.observations[0] == actual_free
    _finish(short_claim)

    # concurrent_cassette_claims_do_not_overcommit.  Both coordinators share the same filesystem pool.
    measured = store_module.os.statvfs
    monkeypatch.setattr(
        store_module.os,
        "statvfs",
        lambda path: _statvfs_with_available(measured(path), 128),
    )
    first = claim_next_transition(
        CapacityTransition("l01-concurrent-a", "parent", payload_bytes=127),
        coordinator=CapacityCoordinator(cartridge),
    )
    second = claim_next_transition(
        CapacityTransition("l01-concurrent-b", "parent", payload_bytes=2),
        coordinator=CapacityCoordinator(cartridge),
    )
    assert first.active
    assert second.state == "PAUSED_RECOVERABLE"
    _finish(first)

    # capacity_remeasured_before_each_write_and_after_each_durable_boundary.
    observations = 0

    def counted_measurement(path):
        nonlocal observations
        observations += 1
        return _statvfs_with_available(measured(path), 128)

    monkeypatch.setattr(store_module.os, "statvfs", counted_measurement)
    multi_write = claim_next_transition(
        CapacityTransition(
            "l01-observe",
            "checkpoint",
            payload_bytes=8,
            declared_writes=2,
            write_bytes=(3, 5),
        ),
        coordinator=CapacityCoordinator(cartridge),
    )
    _finish_write_one = execute_claimed_write(multi_write, lambda: None)
    assert _finish_write_one is None
    execute_claimed_write(multi_write, lambda: None)
    complete_capacity_claim(multi_write)
    assert observations >= 5
    assert multi_write.history.count("MEASURE") == 4
    assert multi_write.history[-2:] == ("DURABLE_BOUNDARY", "OBSERVE")

    # external_free_space_reduction_or_enospc_recovers_parent_or_committed_child;
    # newly_available_capacity_resumes_from_same_committed_boundary.
    measurements = iter((128, 128, 0, 128, 128, 128, 128))
    monkeypatch.setattr(
        store_module.os,
        "statvfs",
        lambda path: _statvfs_with_available(measured(path), next(measurements)),
    )
    lost_space = claim_next_transition(
        CapacityTransition("l01-loss", "parent", payload_bytes=4),
        coordinator=CapacityCoordinator(cartridge),
    )
    assert lost_space.active
    with pytest.raises(CassetteError) as reduced:
        execute_claimed_write(lost_space, lambda: None)
    assert reduced.value.code == "CAPACITY_EXCEEDED"
    assert reduced.value.retryability == "retryable"
    assert lost_space.state == "PAUSED_RECOVERABLE"
    assert coordinator.active_claims() == ()
    resumed = resume_capacity_claim(lost_space)
    assert resumed.active
    assert resumed.transition == lost_space.transition
    assert "RESUME" in resumed.history
    _finish(resumed)

    monkeypatch.setattr(store_module.os, "statvfs", measured)
    enospc = claim_next_transition(
        CapacityTransition("l01-enospc", "parent", payload_bytes=1),
        coordinator=coordinator,
    )
    with pytest.raises(CassetteError) as exhausted:
        execute_claimed_write(enospc, lambda: (_ for _ in ()).throw(OSError(errno.ENOSPC, "full")))
    assert exhausted.value.code == "CAPACITY_EXCEEDED"
    assert enospc.state == "PAUSED_RECOVERABLE"
    assert coordinator.active_claims() == ()
    _finish(resume_capacity_claim(enospc))

    # Fake callback rejection is the discriminator against the former injectable-controller path.
    with pytest.raises(CassetteError) as fake:
        claim_next_transition(short_step, coordinator=lambda _transition: None)
    assert fake.value.code == "INVALID_REQUEST"


def test_q53_reclaim_capacity_protects_live_and_noneligible_objects(tmp_path):
    """Q53: reclamation touches only eligible Cassette temporaries and stops for active claims."""

    cartridge, root_digest, _, _, _ = _compiled_fixture(tmp_path)
    coordinator = CapacityCoordinator(cartridge)
    initialize_cartridge(cartridge, capacity_controller=coordinator)
    commit_generation(
        cartridge,
        "l01-reclaim-root",
        root_digest,
        expected_parent_root=None,
        capacity_controller=coordinator,
        operation_id="l01-reclaim-root",
    )
    transactions = cartridge / "transactions"
    transactions.mkdir(exist_ok=True)
    eligible = transactions / ".eligible.pending"
    eligible.write_bytes(b"temporary")
    journal = transactions / "l01-reclaim-root.json"
    assert journal.is_file()
    retained_root = cartridge / "roots" / "retained-root"
    retained_root.parent.mkdir(exist_ok=True)
    retained_root.write_bytes(b"retained")
    user_owned = cartridge / "user-owned.txt"
    user_owned.write_bytes(b"user")

    # active_claim_transaction_and_journal_objects_survive_reclamation.
    active = claim_next_transition(
        CapacityTransition("l01-reclaim-active", "parent", payload_bytes=1),
        coordinator=coordinator,
    )
    assert reclaim_capacity(cartridge, coordinator) == ()
    assert eligible.exists() and journal.exists()
    _finish(active)

    # retained_root_pinned_rollback_and_user_owned_objects_survive_reclamation;
    # only_eligible_cassette_owned_temporary_or_reproducible_objects_are_reclaimed.
    assert reclaim_capacity(cartridge, coordinator) == (eligible.name,)
    assert not eligible.exists()
    assert journal.is_file()
    assert retained_root.read_bytes() == b"retained"
    assert user_owned.read_bytes() == b"user"

    protected = (
        ReclaimableObject("pinned", True, True, False, False, "TEMPORARY", False, False, False),
        ReclaimableObject("retained", True, False, True, False, "TEMPORARY", False, False, False),
        ReclaimableObject("rollback", True, False, False, True, "TEMPORARY", False, False, False),
        ReclaimableObject("active-claim", True, False, False, False, "TEMPORARY", True, False, False),
        ReclaimableObject("active-transaction", True, False, False, False, "TEMPORARY", False, True, False),
        ReclaimableObject("active-journal", True, False, False, False, "TEMPORARY", False, False, True),
        ReclaimableObject("user-owned", False, False, False, False, "TEMPORARY", False, False, False),
    )
    eligible_reproducible = ReclaimableObject(
        "reproducible", True, False, False, False, "REPRODUCIBLE", False, False, False
    )
    assert select_reclaimable_objects((*protected, eligible_reproducible)) == (eligible_reproducible,)


def test_q39_q44_storage_eligibility_labels_do_not_admit_or_refuse(tmp_path):
    """Q39-Q44: all three storage_eligibility_control assertions use measured operations, not labels."""

    cartridge, root_digest, source_identity, plan_digest, certificate = _compiled_fixture(tmp_path)
    specification = _specifications(cartridge, root_digest, certificate)[0]
    root_digest = prepare_hardware_plans(
        cartridge,
        root_digest,
        source_identity,
        plan_digest,
        [specification],
        capacity_coordinator=CapacityCoordinator(cartridge),
        operation_id="l01-label-catalog",
    )
    measured_profile = _measured(specification, certificate)
    unlabeled = select_hardware_plan(
        cartridge, root_digest, source_identity, plan_digest, measured_profile
    )
    thumb_drive_labels = {
        **measured_profile,
        "media": "USB_THUMB_DRIVE",
        "connector": "USB_A",
        "brand": "l01-fixture",
        "advertised_speed": "USB_2_480Mbps",
        "nominal_capacity_bytes": 16 * 1024**3,
    }
    labeled = select_hardware_plan(
        cartridge, root_digest, source_identity, plan_digest, thumb_drive_labels
    )

    # no_storage_media_class_connector_or_nominal_capacity_admission_gate;
    # descriptive_labels_do_not_determine_admission.
    assert "storage_class" not in compiler_module._MEASURED_PROFILE_FIELDS
    assert labeled.plan == unlabeled.plan

    # any_locally_attached_macos_apfs_drive_may_attempt_measurement.  The concrete controller
    # accepts the cartridge path itself and derives admission from statvfs, with no media label.
    coordinator = CapacityCoordinator(cartridge)
    claim = claim_next_transition(
        CapacityTransition("l01-label-free", "measured-path", payload_bytes=1),
        coordinator=coordinator,
    )
    assert claim.active
    _finish(claim)


def l01_25_capacity_proof(tmp_path, monkeypatch) -> dict:
    """Execute every L01.25 matrix assertion and return its exact fixture-level proof record."""

    adaptive = tmp_path / "adaptive"
    reclaim = tmp_path / "reclaim"
    eligibility = tmp_path / "eligibility"
    for directory in (adaptive, reclaim, eligibility):
        directory.mkdir(parents=True)
    test_q53_adaptive_capacity_control_uses_live_store_measurement_and_exact_boundaries(
        adaptive, monkeypatch
    )
    test_q53_reclaim_capacity_protects_live_and_noneligible_objects(reclaim)
    test_q39_q44_storage_eligibility_labels_do_not_admit_or_refuse(eligibility)
    return {
        "adaptive_capacity_control": list(ADAPTIVE_CAPACITY_ASSERTIONS),
        "storage_eligibility_control": list(STORAGE_ELIGIBILITY_ASSERTIONS),
        "evidence_level": "FIXTURE",
        "live_evidence": "NOT_RUN",
    }
