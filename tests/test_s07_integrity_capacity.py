# test_s07_integrity_capacity.py — S07 F1 fixtures for Q53 reservation and Q62 repair; depends on errors.py, store.py.
"""S07 proves complete storage admission and independent object repair on a scratch cartridge."""

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from threading import Barrier, Lock

from blake3 import blake3
import pytest

from errors import CassetteError
from store import (
    ArtifactIdentity,
    CapacityPhase,
    CapacityReservation,
    IdentityTuple,
    create_repair_set,
    import_safetensors,
    load_root,
    page_locations,
    read_tensor,
    release_capacity,
    repair_revision,
    require_revision,
    reserve_capacity,
    verify_revision,
)

GIB = 1024**3


class _ExtentPool:
    """A true storage-boundary fixture whose lock makes one extent admission atomic."""

    def __init__(self, available: int) -> None:
        self.available = available
        self.releases = 0
        self._lock = Lock()

    def reserve(self, length: int) -> bool:
        with self._lock:
            if length > self.available:
                return False
            self.available -= length
            return True

    def release(self, length: int) -> bool:
        with self._lock:
            self.available += length
            self.releases += 1
            return True


def _blake3(payload: bytes) -> str:
    return f"blake3:{blake3(payload).hexdigest()}"


def _write_safetensors(path: Path, name: str, payload: bytes) -> None:
    header = {
        "__metadata__": {"fixture": "S07"},
        name: {"dtype": "U8", "shape": [len(payload)], "data_offsets": [0, len(payload)]},
    }
    encoded = json.dumps(header, separators=(",", ":")).encode()
    encoded += b" " * (-len(encoded) % 8)
    path.write_bytes(len(encoded).to_bytes(8, "little") + encoded + payload)


def _identity(*sources: Path) -> IdentityTuple:
    return IdentityTuple(
        revision_kind="executable",
        source_kind="huggingface",
        source_alias="fixture/s07@main",
        canonical_locator="fixture/s07",
        requested_revision="main",
        immutable_revision="git-sha1:0123456789abcdef0123456789abcdef01234567",
        artifacts=tuple(
            ArtifactIdentity(path.name, path.stat().st_size, _blake3(path.read_bytes()))
            for path in sorted(sources)
        ),
        format_versions=(("safetensors", "0.6.2"),),
        tensor_index_digest=_blake3(b"S07 tensor index"),
        config_digest=_blake3(b"S07 config"),
        architecture="S07IntegrityTransformer",
        operator_set=("attention", "matmul"),
        tokenizer_digest=_blake3(b"S07 tokenizer"),
        processor_digest=_blake3(b"S07 processor"),
        template_digest=_blake3(b"S07 template"),
        precision_scheme="u8-fixture",
        license_digest=_blake3(b"S07 license"),
        parent_ids=(_blake3(b"S07 parent"),),
        transform_manifest_digest=_blake3(b"S07 transform"),
    )


def _corrupt(path: Path, offset: int = 0) -> None:
    payload = bytearray(path.read_bytes())
    payload[offset] ^= 0xFF
    path.write_bytes(payload)


def _xor(*payloads: bytes) -> bytes:
    width = max(map(len, payloads))
    output = bytearray(width)
    for payload in payloads:
        for offset, value in enumerate(payload):
            output[offset] ^= value
    return bytes(output)


def _states(report, object_id: str) -> list[str]:
    return [state for subject, _, state in report.transitions if subject == object_id]


def test_q53_exact_fragmented_concurrent_growing_training_and_repair_capacity(tmp_path):
    """Q53 acceptance: every named lifecycle case owns one exact extent until terminal cleanup."""

    requested = []
    released = []
    exact_required = 10 * GIB + 1_300
    exact = reserve_capacity(
        "s07-exact",
        device_bytes=200 * GIB,
        allocatable_verified_free=exact_required,
        phases=(
            CapacityPhase(committed=100, inflight=700),
            CapacityPhase(committed=400, candidate=900),
        ),
        reserve_extent=lambda length: requested.append(length) is None,
        release_extent=lambda length: released.append(length) is None,
    )
    assert exact.phase_totals == (800, 1_300)
    assert exact.safety_bytes == 10 * GIB
    assert exact.required_bytes == exact_required
    assert requested == [exact_required]
    assert exact.active

    allocator_called = False

    def forbidden_allocator(_length: int) -> bool:
        nonlocal allocator_called
        allocator_called = True
        return True

    with pytest.raises(CassetteError) as below_boundary:
        reserve_capacity(
            "s07-below-boundary",
            device_bytes=200 * GIB,
            allocatable_verified_free=exact_required - 1,
            phases=(CapacityPhase(committed=400, candidate=900),),
            reserve_extent=forbidden_allocator,
            release_extent=lambda _: True,
        )
    assert below_boundary.value.code == "CAPACITY_EXCEEDED"
    assert allocator_called is False

    small_device_required = 8 * GIB + 17
    small_device = reserve_capacity(
        "s07-eight-gib-safety",
        device_bytes=100 * GIB,
        allocatable_verified_free=small_device_required,
        phases=(CapacityPhase(journal=17),),
        reserve_extent=lambda length: length == small_device_required,
        release_extent=lambda _: True,
    )
    assert small_device.safety_bytes == 8 * GIB

    fragments = (exact_required - 1, 1)
    with pytest.raises(CassetteError) as fragmented:
        reserve_capacity(
            "s07-fragmented",
            device_bytes=200 * GIB,
            allocatable_verified_free=exact_required,
            phases=(CapacityPhase(committed=400, candidate=900),),
            reserve_extent=lambda length: any(fragment >= length for fragment in fragments),
            release_extent=lambda _: True,
        )
    assert fragmented.value.code == "CAPACITY_EXCEEDED"
    assert "preallocate" in fragmented.value.detail

    concurrent_required = 8 * GIB + 17
    pool = _ExtentPool(concurrent_required)
    barrier = Barrier(2)

    def compete(number: int) -> CapacityReservation | CassetteError:
        barrier.wait()
        try:
            return reserve_capacity(
                f"s07-concurrent-{number}",
                device_bytes=100 * GIB,
                allocatable_verified_free=concurrent_required,
                phases=(CapacityPhase(journal=17),),
                reserve_extent=pool.reserve,
                release_extent=pool.release,
            )
        except CassetteError as error:
            return error

    with ThreadPoolExecutor(max_workers=2) as executor:
        concurrent = tuple(executor.map(compete, (1, 2)))
    winners = [item for item in concurrent if isinstance(item, CapacityReservation)]
    losers = [item for item in concurrent if isinstance(item, CassetteError)]
    assert len(winners) == 1
    assert len(losers) == 1
    assert losers[0].code == "CAPACITY_EXCEEDED"
    assert pool.available == 0
    release_capacity(winners[0])
    release_capacity(winners[0])
    assert pool.available == concurrent_required
    assert pool.releases == 1
    assert winners[0].active is False

    transform_required = 33 * GIB + 1
    transform = reserve_capacity(
        "s07-growing-transform",
        device_bytes=400 * GIB,
        allocatable_verified_free=transform_required,
        phases=(
            CapacityPhase(committed=4 * GIB, inflight=1 * GIB, journal=1),
            CapacityPhase(
                committed=4 * GIB,
                candidate=3 * GIB,
                rollback=4 * GIB,
                precision=2 * GIB,
                journal=1,
            ),
        ),
        reserve_extent=lambda length: length == transform_required,
        release_extent=lambda _: True,
    )
    assert transform.phase_totals == (5 * GIB + 1, 13 * GIB + 1)
    transform_bytes = b"unmodified transform source"
    with pytest.raises(CassetteError):
        reserve_capacity(
            "s07-growing-transform-short",
            device_bytes=400 * GIB,
            allocatable_verified_free=transform_required - 1,
            phases=(
                CapacityPhase(committed=4 * GIB, inflight=1 * GIB, journal=1),
                CapacityPhase(
                    committed=4 * GIB,
                    candidate=3 * GIB,
                    rollback=4 * GIB,
                    precision=2 * GIB,
                    journal=1,
                ),
            ),
            reserve_extent=forbidden_allocator,
            release_extent=lambda _: True,
        )
    assert transform_bytes == b"unmodified transform source"
    assert allocator_called is False

    training_required = 40 * GIB + 17
    training = reserve_capacity(
        "s07-training",
        device_bytes=400 * GIB,
        allocatable_verified_free=training_required,
        phases=(CapacityPhase(
            committed=2 * GIB,
            candidate=1 * GIB,
            rollback=2 * GIB,
            optimizer=3 * GIB,
            master=4 * GIB,
            dataset=5 * GIB,
            precision=3 * GIB,
            journal=17,
        ),),
        reserve_extent=lambda length: length == training_required,
        release_extent=lambda _: True,
    )
    assert training.phase_totals == (20 * GIB + 17,)
    training_bytes = b"unmodified training revision"
    with pytest.raises(CassetteError):
        reserve_capacity(
            "s07-training-short",
            device_bytes=400 * GIB,
            allocatable_verified_free=training_required - 1,
            phases=(CapacityPhase(
                committed=2 * GIB,
                candidate=1 * GIB,
                rollback=2 * GIB,
                optimizer=3 * GIB,
                master=4 * GIB,
                dataset=5 * GIB,
                precision=3 * GIB,
                journal=17,
            ),),
            reserve_extent=forbidden_allocator,
            release_extent=lambda _: True,
        )
    assert training_bytes == b"unmodified training revision"
    assert allocator_called is False

    allocator_called = False
    with pytest.raises(CassetteError) as overflow:
        reserve_capacity(
            "s07-overflow",
            device_bytes=2**64 - 1,
            allocatable_verified_free=2**64 - 1,
            phases=(CapacityPhase(committed=2**64 - 1, inflight=1),),
            reserve_extent=forbidden_allocator,
            release_extent=lambda _: True,
        )
    assert overflow.value.code == "CAPACITY_EXCEEDED"
    assert "unsigned 64-bit" in overflow.value.detail
    assert allocator_called is False

    source = tmp_path / "repair.safetensors"
    _write_safetensors(source, "repair", b"repair-capacity-page")
    cartridge = tmp_path / "repair-cartridge"
    root_digest = import_safetensors({source.name: source}, cartridge, _identity(source))
    insufficient = reserve_capacity(
        "s07-insufficient-repair",
        device_bytes=200 * GIB,
        allocatable_verified_free=10 * GIB + 1,
        phases=(CapacityPhase(repair=1),),
        reserve_extent=lambda _: True,
        release_extent=lambda _: True,
    )
    with pytest.raises(CassetteError) as repair_capacity:
        create_repair_set(cartridge, root_digest, insufficient)
    assert repair_capacity.value.code == "CAPACITY_EXCEEDED"
    assert not (cartridge / "repair").exists()
    release_capacity(insufficient)

    repair_reservation = reserve_capacity(
        "s07-repair",
        device_bytes=200 * GIB,
        allocatable_verified_free=10 * GIB + 1 * GIB,
        phases=(CapacityPhase(repair=1 * GIB),),
        reserve_extent=lambda _: True,
        release_extent=lambda _: True,
    )
    create_repair_set(cartridge, root_digest, repair_reservation)
    release_capacity(repair_reservation)
    with pytest.raises(CassetteError) as released_repair:
        repair_revision(cartridge, root_digest, repair_reservation)
    assert released_repair.value.code == "INVALID_REQUEST"

    release_capacity(exact)
    release_capacity(small_device)
    release_capacity(transform)
    release_capacity(training)
    assert released == [exact_required]


def test_q62_corrupt_payload_index_manifest_root_and_parity_repair(tmp_path):
    """Q62 acceptance: every named object fails before use and returns to its original digest."""

    alpha = b"alpha-page-contents"
    beta = b"beta-page-contents"
    first = tmp_path / "model-00001-of-00002.safetensors"
    second = tmp_path / "model-00002-of-00002.safetensors"
    _write_safetensors(first, "alpha", alpha)
    _write_safetensors(second, "beta", beta)
    cartridge = tmp_path / "cartridge"
    root_digest = import_safetensors(
        {first.name: first, second.name: second}, cartridge, _identity(first, second)
    )
    reservation = reserve_capacity(
        "s07-integrity-repair",
        device_bytes=200 * GIB,
        allocatable_verified_free=11 * GIB,
        phases=(CapacityPhase(repair=1 * GIB),),
        reserve_extent=lambda _: True,
        release_extent=lambda _: True,
    )
    repair_set = create_repair_set(cartridge, root_digest, reservation)
    root = load_root(cartridge, root_digest)
    locations = {location.page_digest: location for location in page_locations(cartridge, root_digest)}
    alpha_digest = _blake3(alpha)
    beta_digest = _blake3(beta)
    required_pages = tuple(sorted((alpha_digest, beta_digest)))
    assert set(locations) == {alpha_digest, beta_digest}
    alpha_location = locations[alpha_digest]

    root_path = cartridge / "roots" / root_digest[7:]
    index_path = cartridge / "indexes" / root_digest[7:]
    segment_path = cartridge / "segments" / alpha_location.segment_id[7:]
    parity_digest = repair_set.parity_digests[0]
    parity_path = cartridge / "repair" / "objects" / parity_digest[7:]
    manifest_path = cartridge / "repair" / f"{root_digest[7:]}.json"
    manifest_replica_path = cartridge / "repair" / "manifests" / root_digest[7:]

    root_bytes = root_path.read_bytes()
    index_bytes = index_path.read_bytes()
    segment_bytes = segment_path.read_bytes()
    parity_bytes = parity_path.read_bytes()
    manifest_bytes = manifest_path.read_bytes()
    manifest_replica_bytes = manifest_replica_path.read_bytes()
    assert _blake3(root_bytes) == root_digest
    assert _blake3(index_bytes) == repair_set.index_digest
    assert _blake3(segment_bytes) == alpha_location.segment_id
    assert _blake3(parity_bytes) == parity_digest
    assert parity_bytes == _xor(alpha, beta)
    assert _blake3(manifest_bytes) == repair_set.manifest_digest
    assert manifest_replica_bytes == manifest_bytes
    assert len(repair_set.parity_digests) == 1
    assert repair_set.required_bytes == (
        len(root_bytes) + len(index_bytes) + len(parity_bytes) + 2 * len(manifest_bytes)
    )
    assert verify_revision(cartridge, root_digest).available

    _corrupt(manifest_path)
    manifest_report = verify_revision(cartridge, root_digest)
    manifest_id = f"manifest:{root_digest}"
    assert manifest_report.unavailable_pages == required_pages
    assert _states(manifest_report, manifest_id) == ["SUSPECT", "VERIFYING", "CORRUPT"]
    assert manifest_replica_path.read_bytes() == manifest_replica_bytes
    with pytest.raises(CassetteError) as manifest_use:
        require_revision(cartridge, root_digest)
    assert manifest_use.value.code == "PAGE_CORRUPT"
    assert all(digest in manifest_use.value.detail for digest in required_pages)
    manifest_repair = repair_revision(cartridge, root_digest, reservation)
    assert _states(manifest_repair, manifest_id) == [
        "SUSPECT", "VERIFYING", "CORRUPT", "REPAIRING", "VALID",
    ]
    assert manifest_path.read_bytes() == manifest_bytes
    assert _blake3(manifest_path.read_bytes()) == repair_set.manifest_digest

    _corrupt(segment_path, alpha_location.offset)
    with pytest.raises(CassetteError) as page_use:
        read_tensor(cartridge, root_digest, "alpha")
    assert page_use.value.code == "PAGE_CORRUPT"
    page_report = verify_revision(cartridge, root_digest)
    assert page_report.unavailable_pages == (alpha_digest,)
    assert _states(page_report, f"page:{alpha_digest}") == ["SUSPECT", "VERIFYING", "CORRUPT"]
    page_repair = repair_revision(cartridge, root_digest, reservation)
    assert _states(page_repair, f"page:{alpha_digest}") == [
        "SUSPECT", "VERIFYING", "CORRUPT", "REPAIRING", "VALID",
    ]
    assert segment_path.read_bytes() == segment_bytes
    assert _blake3(segment_path.read_bytes()) == alpha_location.segment_id
    assert read_tensor(cartridge, root_digest, "alpha") == alpha

    _corrupt(index_path)
    with pytest.raises(CassetteError) as index_use:
        load_root(cartridge, root_digest)
    assert index_use.value.code == "ROOT_INVALID"
    index_repair = repair_revision(cartridge, root_digest, reservation)
    assert _states(index_repair, f"index:{root_digest}") == [
        "SUSPECT", "VERIFYING", "CORRUPT", "REPAIRING", "VALID",
    ]
    assert index_path.read_bytes() == index_bytes
    assert _blake3(index_path.read_bytes()) == repair_set.index_digest

    _corrupt(root_path)
    with pytest.raises(CassetteError) as root_use:
        load_root(cartridge, root_digest)
    assert root_use.value.code == "ROOT_INVALID"
    root_repair = repair_revision(cartridge, root_digest, reservation)
    assert _states(root_repair, f"root:{root_digest}") == [
        "SUSPECT", "VERIFYING", "CORRUPT", "REPAIRING", "VALID",
    ]
    assert root_path.read_bytes() == root_bytes
    assert _blake3(root_path.read_bytes()) == root_digest
    assert load_root(cartridge, root_digest) == root

    _corrupt(parity_path)
    parity_report = verify_revision(cartridge, root_digest)
    assert parity_report.available
    assert dict(parity_report.states)[f"parity:{parity_digest}"] == "CORRUPT"
    parity_repair = repair_revision(cartridge, root_digest, reservation)
    assert _states(parity_repair, f"parity:{parity_digest}") == [
        "SUSPECT", "VERIFYING", "CORRUPT", "REPAIRING", "VALID",
    ]
    assert parity_path.read_bytes() == parity_bytes
    assert _blake3(parity_path.read_bytes()) == parity_digest

    _corrupt(segment_path, alpha_location.offset)
    _corrupt(parity_path)
    corrupt_segment_bytes = segment_path.read_bytes()
    corrupt_parity_bytes = parity_path.read_bytes()
    with pytest.raises(CassetteError) as invalid_source:
        repair_revision(
            cartridge,
            root_digest,
            reservation,
            source_pages={alpha_digest: b"not the declared page"},
        )
    assert invalid_source.value.code == "INVALID_REQUEST"
    assert segment_path.read_bytes() == corrupt_segment_bytes
    assert parity_path.read_bytes() == corrupt_parity_bytes

    unavailable = repair_revision(cartridge, root_digest, reservation)
    assert unavailable.available is False
    assert unavailable.unavailable_pages == (alpha_digest,)
    assert dict(unavailable.states)[f"page:{alpha_digest}"] == "UNAVAILABLE"
    with pytest.raises(CassetteError) as blocked:
        require_revision(cartridge, root_digest)
    assert blocked.value.code == "PAGE_CORRUPT"
    assert blocked.value.object_id == f"page:{alpha_digest}"
    assert alpha_digest in blocked.value.detail

    restored = repair_revision(
        cartridge, root_digest, reservation, source_pages={alpha_digest: alpha}
    )
    assert restored.available
    assert read_tensor(cartridge, root_digest, "alpha") == alpha
    assert _blake3(parity_path.read_bytes()) == parity_digest
    assert load_root(cartridge, root_digest) == root
    assert any((cartridge / "quarantine").iterdir())
    release_capacity(reservation)
