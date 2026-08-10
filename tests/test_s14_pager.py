# test_s14_pager.py — F3 fixture for certified page readiness and selection failure (Q20/Q64); depends on errors.py, pager.py, store.py, tests/test_s05_store.py, tests/test_s13_pager.py.
"""S14 proves exact and seeded page execution ends before use whenever its contract fails."""

from __future__ import annotations

import asyncio
import copy
from dataclasses import replace
from pathlib import Path
import platform

import pytest

import pager
from errors import CassetteError
from store import digest_bytes, import_safetensors, load_root, page_locations
from tests.test_s05_store import _identity, _write_safetensors
from tests.test_s13_pager import ATOMS, _bind, _digest, _fixture, _normal_matrix, _seal


pytestmark = pytest.mark.skipif(
    platform.system() != "Darwin" or platform.machine() != "arm64",
    reason="S14 requires arm64 macOS with MLX Metal for the page-consumer fence",
)


def _stochastic_fixture(root_digest: str, pages: dict[str, str]):
    plan, certificate, evidence, profile = _fixture()
    atom_claims = {row["atom_id"]: row for row in certificate["atoms"]}
    for atom in evidence["atoms"]:
        reconstruction = atom["description"]["reconstruction"]
        reconstruction[0][1] -= 2
        residual = [
            [value - rebuilt for value, rebuilt in zip(row, rebuilt_row, strict=True)]
            for row, rebuilt_row in zip(atom["matrix"], reconstruction, strict=True)
        ]
        calibration = atom["description"]["estimator_calibration"]
        calibration["distortion"] = "5"
        claim = atom_claims[atom["atom_id"]]["description"]
        claim.update(
            reconstruction_digest=_digest(_normal_matrix(reconstruction)),
            residual_relation_digest=_digest(_normal_matrix(residual)),
            distortion_bound=5.0,
            estimator_calibration_digest=_digest(calibration),
        )

    law = evidence["execution_contract"]["sampling_laws"][0]
    law["law"]["atom_distributions"] = [
        {
            "atom_id": atom_id,
            "columns": [
                {"column": 0, "probability": "1/5"},
                {"column": 1, "probability": "4/5"},
            ],
        }
        for atom_id in ATOMS
    ]
    certificate["execution_contract"]["sampling_laws"][0]["law_digest"] = _digest(
        law["law"]
    )

    for row in evidence["trace_contract"]["steps"]:
        row.update(fresh_samples=16, fresh_traffic=48)
    for row in certificate["resource_tables"]["per_trace_step"]:
        row.update(fresh_samples=16, fresh_traffic=48)
    for row in certificate["resource_tables"]["per_atom"]:
        row.update(
            fresh_samples_max=16,
            fresh_samples_total=16,
            fresh_traffic_max=48,
            fresh_traffic_total=48,
        )
    certificate["resource_tables"]["per_operation"][0].update(
        fresh_samples_max=16,
        fresh_samples_total=48,
        fresh_traffic_max=48,
        fresh_traffic_total=144,
    )
    certificate["resources"].update(
        fresh_samples_max=16,
        fresh_samples_total=48,
        fresh_traffic_max=48,
        fresh_traffic_total=144,
    )
    plan["resource_limits"] = copy.deepcopy(certificate["resources"])
    for conversion in (
        evidence["physical_conversion"]["conversion_rows"][0],
        certificate["physical_conversion"]["conversion_rows"][0],
    ):
        conversion.update(probes=16, page_reads=3)
    certificate["physical_conversion"]["conversion_digest"] = _digest(
        certificate["physical_conversion"]["conversion_rows"]
    )
    schedule_rows = []
    for row in certificate["resource_tables"]["per_trace_step"]:
        schedule_row = {
            name: value
            for name, value in row.items()
            if name not in {"epsilon_exec", "delta_exec"}
        }
        schedule_row.update(epsilon_exec="1/2", delta_exec="1/4")
        schedule_rows.append(schedule_row)
    certificate["trace_contract"]["schedule_digest"] = _digest({
        "prefix_policy": evidence["trace_contract"]["prefix_policy"],
        "steps": schedule_rows,
    })
    _bind(plan, certificate, profile)

    page_map = {
        "root_digest": root_digest,
        "steps": [
            {
                "step": step,
                "operation_id": row["operation_id"],
                "atom_id": row["atom_id"],
                "description_digest": _digest(
                    atom_claims[row["atom_id"]]["description"]
                ),
                "exact_pages": [pages["description"]],
                "sample_units": [
                    {"unit": 0, "page_digests": [pages["residual.zero"]]},
                    {"unit": 1, "page_digests": [pages["residual.one"]]},
                ],
            }
            for step, row in enumerate(evidence["trace_contract"]["steps"])
        ],
    }
    plan["page_map_digest"] = _digest(page_map)
    _seal(plan, "plan_id")
    return plan, certificate, evidence, profile, page_map


def _selection(certificate: dict, evidence: dict, step: int, seed: int = 7):
    trace = evidence["trace_contract"]["steps"][step]
    atom_id = trace["atom_id"]
    condition = next(
        row["condition_id"]
        for row in certificate["compatibility"]["cover"]
        if row["atom_id"] == atom_id
    )
    atom = next(row for row in certificate["atoms"] if row["atom_id"] == atom_id)
    face = next(
        row for row in certificate["compatibility"]["service_faces"]
        if row["face_id"] == atom["service_face_id"]
    )
    load_bytes = certificate["physical_conversion"]["conversion_rows"][0]["bytes"]
    return pager.CompiledSelection(
        observed_condition=condition,
        atom_id=atom_id,
        service_face=tuple(face["condition_ids"]),
        certificate_digest=certificate["certificate_id"],
        description_digest=_digest(atom["description"]),
        execution_seed_or_exact_schedule=seed,
        bytes=load_bytes,
    )


def _corrupt_pages(
    cartridge: Path,
    locations: dict[str, object],
    page_digests: tuple[str, ...],
) -> dict[Path, bytes]:
    originals = {}
    mutations = {}
    for page_digest in page_digests:
        location = locations[page_digest]
        path = cartridge / "segments" / location.segment_id[7:]
        if path not in originals:
            originals[path] = path.read_bytes()
            mutations[path] = bytearray(originals[path])
        mutations[path][location.offset] ^= 0xFF
    for path, payload in mutations.items():
        path.write_bytes(payload)
    return originals


def _restore_pages(originals: dict[Path, bytes]) -> None:
    for path, payload in originals.items():
        path.write_bytes(payload)


def _assert_error(code: str, awaitable, invariant: str | None = None):
    async def run():
        with pytest.raises(CassetteError) as caught:
            await awaitable
        assert caught.value.code == code
        if invariant is not None:
            assert caught.value.failed_invariant == invariant
        return caught.value

    return run()


def test_q20_q64_f3_page_readiness_replay_and_selection_failure(tmp_path):
    """Q20/Q64 acceptance: every exact or sampled page is valid before use, replayable, or ends with one typed error."""

    cartridge = tmp_path / "cartridge"
    sources = {}
    for name, payload in {
        "description": b"S14 exact compiled description",
        "residual.zero": b"S14 residual column zero",
        "residual.one": b"S14 residual column one",
    }.items():
        path = tmp_path / f"{name}.safetensors"
        _write_safetensors(path, ((name, "U8", (len(payload),), payload),))
        sources[path.name] = path
    root_digest = import_safetensors(sources, cartridge, _identity(*sources.values()))
    root = load_root(cartridge, root_digest)
    pages = {
        row["semantic_tensor_id"]: row["spans"][0]["page_digest"]
        for row in root["tensor_maps"]
    }
    locations = {
        location.page_digest: location
        for location in page_locations(cartridge, root_digest)
    }
    plan, certificate, evidence, profile, page_map = _stochastic_fixture(
        root_digest, pages
    )

    underread_plan = copy.deepcopy(plan)
    underread_certificate = copy.deepcopy(certificate)
    underread_evidence = copy.deepcopy(evidence)
    underread_certificate["physical_conversion"]["conversion_rows"][0][
        "page_reads"
    ] = 2
    underread_evidence["physical_conversion"]["conversion_rows"][0][
        "page_reads"
    ] = 2
    underread_certificate["physical_conversion"]["conversion_digest"] = _digest(
        underread_certificate["physical_conversion"]["conversion_rows"]
    )
    _bind(underread_plan, underread_certificate, profile)
    with pytest.raises(CassetteError) as underread:
        pager.CertifiedPager(
            cartridge,
            underread_plan,
            underread_certificate,
            underread_evidence,
            profile,
            page_map,
        )
    assert underread.value.failed_invariant == "Q20: certified page-read count"

    async def exercise():
        route = (pages["description"], pages["residual.zero"])
        baseline = await pager.NativePager(cartridge, root_digest).execute(
            route, pager.NativePrefetch((), 0.0, 0)
        )
        false_high_pager = pager.NativePager(cartridge, root_digest)
        false_high = await false_high_pager.execute(
            route,
            pager.NativePrefetch(
                (pages["residual.one"],),
                1.0,
                locations[pages["residual.one"]].length,
            ),
        )
        false_low = await pager.NativePager(cartridge, root_digest).execute(
            route,
            pager.NativePrefetch(
                (pages["description"],),
                0.0,
                locations[pages["description"]].length,
            ),
        )
        assert baseline.output_digest == false_high.output_digest == false_low.output_digest
        assert baseline.planned_pages == false_high.planned_pages == false_low.planned_pages == route
        assert pages["residual.one"] not in false_high.planned_pages
        assert all(
            [target for page, _, target in baseline.transitions if page == page_digest]
            == ["ACQUIRING", "HASHED", "RESIDENT", "GPU_SUBMITTED", "RECLAIMABLE"]
            for page_digest in route
        )

        missing = digest_bytes(b"S14 absent exact page")
        absent_native = pager.NativePager(cartridge, root_digest)
        await _assert_error(
            "PAGE_CORRUPT",
            absent_native.execute(
                (missing,), pager.NativePrefetch((), 0.0, 0)
            ),
        )
        assert not any(
            target == "GPU_SUBMITTED"
            for _, _, target in absent_native.last_attempt_transitions
        )

        exact_originals = _corrupt_pages(
            cartridge, locations, (pages["description"],)
        )
        corrupt_native = pager.NativePager(cartridge, root_digest)
        await _assert_error(
            "PAGE_CORRUPT",
            corrupt_native.execute(route, pager.NativePrefetch((), 0.0, 0)),
        )
        assert not any(
            target == "GPU_SUBMITTED"
            for _, _, target in corrupt_native.last_attempt_transitions
        )
        corrupt_exact_compiled = pager.CertifiedPager(
            cartridge, plan, certificate, evidence, profile, page_map
        )
        await _assert_error(
            "PAGE_CORRUPT",
            corrupt_exact_compiled.execute(_selection(certificate, evidence, 0)),
        )
        assert corrupt_exact_compiled.next_step == 0
        assert corrupt_exact_compiled.last_committed is None
        assert not any(
            target == "GPU_SUBMITTED"
            for _, _, target in corrupt_exact_compiled.last_attempt_transitions
        )
        _restore_pages(exact_originals)

        validation_cases = [
            ("Q64: immutable compiled certificate", replace(
                _selection(certificate, evidence, 0),
                certificate_digest=digest_bytes(b"S14 stale certificate"),
            )),
            ("Q20: certified fresh-random seed contract", replace(
                _selection(certificate, evidence, 0),
                execution_seed_or_exact_schedule=-1,
            )),
            ("Q64: certified service face", replace(
                _selection(certificate, evidence, 0),
                service_face=("condition.forged",),
            )),
            ("Q64: certified observation support", replace(
                _selection(certificate, evidence, 0),
                observed_condition="condition.off-support",
            )),
        ]
        for invariant, invalid_selection in validation_cases:
            candidate = pager.CertifiedPager(
                cartridge, plan, certificate, evidence, profile, page_map
            )
            await _assert_error(
                "CAPABILITY_MISMATCH",
                candidate.execute(invalid_selection),
                invariant,
            )
            assert candidate.next_step == 0
            assert candidate.last_committed is None
            assert candidate.last_attempt_transitions == ()

        timed = pager.CertifiedPager(
            cartridge, plan, certificate, evidence, profile, page_map
        )
        first_selection = _selection(certificate, evidence, 0)
        first_commit = await timed.execute(first_selection)
        timed_selection = _selection(certificate, evidence, 1)
        await _assert_error(
            "WORKING_SET_TIMEOUT",
            timed.execute(timed_selection, timeout_seconds=0),
            "Q20: page readiness before command submission",
        )
        assert timed.next_step == 1
        assert timed.last_committed == first_commit
        assert timed.replay_selection == timed_selection
        assert not any(
            target == "GPU_SUBMITTED"
            for _, _, target in timed.last_attempt_transitions
        )

        cancelled = pager.CertifiedPager(
            cartridge, plan, certificate, evidence, profile, page_map
        )
        cancel_event = asyncio.Event()
        cancel_event.set()
        await _assert_error(
            "OPERATION_CANCELLED",
            cancelled.execute(first_selection, cancel_event=cancel_event),
        )
        assert cancelled.next_step == 0
        assert cancelled.last_committed is None
        assert cancelled.replay_selection == first_selection
        retry = await cancelled.execute(first_selection)
        assert retry.step == 0
        assert cancelled.next_step == 1
        assert cancelled.replay_selection is None

        replay_a = await pager.CertifiedPager(
            cartridge, plan, certificate, evidence, profile, page_map
        ).execute(_selection(certificate, evidence, 0, seed=7))
        replay_b = await pager.CertifiedPager(
            cartridge, plan, certificate, evidence, profile, page_map
        ).execute(_selection(certificate, evidence, 0, seed=7))
        alternate = await pager.CertifiedPager(
            cartridge, plan, certificate, evidence, profile, page_map
        ).execute(_selection(certificate, evidence, 0, seed=11))
        assert replay_a.sample_units == replay_b.sample_units
        assert replay_a.output_digest == replay_b.output_digest
        assert replay_a.sample_units == (
            1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1
        )
        assert alternate.sample_units == (
            1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1
        )
        assert replay_a.output_digest != alternate.output_digest

        absent_map = copy.deepcopy(page_map)
        absent_sample = digest_bytes(b"S14 absent sampled correction page")
        for row in absent_map["steps"]:
            for unit in row["sample_units"]:
                unit["page_digests"] = [absent_sample]
        absent_plan = copy.deepcopy(plan)
        absent_plan["page_map_digest"] = _digest(absent_map)
        _seal(absent_plan, "plan_id")
        absent_compiled = pager.CertifiedPager(
            cartridge,
            absent_plan,
            certificate,
            evidence,
            profile,
            absent_map,
        )
        await _assert_error(
            "PAGE_CORRUPT",
            absent_compiled.execute(first_selection),
        )
        assert absent_compiled.next_step == 0
        assert absent_compiled.last_committed is None
        assert not any(
            target == "GPU_SUBMITTED"
            for _, _, target in absent_compiled.last_attempt_transitions
        )

        absent_exact_map = copy.deepcopy(page_map)
        absent_exact = digest_bytes(b"S14 absent compiled exact page")
        for row in absent_exact_map["steps"]:
            row["exact_pages"] = [absent_exact]
        absent_exact_plan = copy.deepcopy(plan)
        absent_exact_plan["page_map_digest"] = _digest(absent_exact_map)
        _seal(absent_exact_plan, "plan_id")
        absent_exact_compiled = pager.CertifiedPager(
            cartridge,
            absent_exact_plan,
            certificate,
            evidence,
            profile,
            absent_exact_map,
        )
        await _assert_error(
            "PAGE_CORRUPT",
            absent_exact_compiled.execute(first_selection),
        )
        assert absent_exact_compiled.next_step == 0
        assert absent_exact_compiled.last_committed is None
        assert not any(
            target == "GPU_SUBMITTED"
            for _, _, target in absent_exact_compiled.last_attempt_transitions
        )

        sampled_originals = _corrupt_pages(
            cartridge,
            locations,
            (pages["residual.zero"], pages["residual.one"]),
        )
        corrupt_compiled = pager.CertifiedPager(
            cartridge, plan, certificate, evidence, profile, page_map
        )
        await _assert_error(
            "PAGE_CORRUPT",
            corrupt_compiled.execute(first_selection),
        )
        assert corrupt_compiled.next_step == 0
        assert corrupt_compiled.last_committed is None
        assert not any(
            target == "GPU_SUBMITTED"
            for _, _, target in corrupt_compiled.last_attempt_transitions
        )
        _restore_pages(sampled_originals)

        horizon = pager.CertifiedPager(
            cartridge, plan, certificate, evidence, profile, page_map
        )
        for step in range(3):
            assert (await horizon.execute(
                _selection(certificate, evidence, step)
            )).step == step
        committed = horizon.last_committed
        await _assert_error(
            "CAPABILITY_MISMATCH",
            horizon.execute(_selection(certificate, evidence, 0)),
        )
        assert horizon.next_step == 3
        assert horizon.last_committed == committed
        assert horizon.last_attempt_transitions == ()

    asyncio.run(exercise())
