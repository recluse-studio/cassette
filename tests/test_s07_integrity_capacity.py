# test_s07_integrity_capacity.py — S07 F1 fixtures for Q53 reservation and Q62 repair; depends on errors.py, store.py.
"""S07 proves exact admission and object-by-object repair on a scratch cartridge."""

import json
from pathlib import Path

import pytest

from errors import CassetteError
from store import (
    ArtifactIdentity,
    CapacityPhase,
    IdentityTuple,
    create_repair_set,
    digest_bytes,
    import_safetensors,
    load_root,
    page_locations,
    read_tensor,
    repair_revision,
    require_revision,
    reserve_capacity,
    verify_revision,
)

GIB = 1024**3


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
            ArtifactIdentity(path.name, path.stat().st_size, digest_bytes(path.read_bytes()))
            for path in sorted(sources)
        ),
        format_versions=(("safetensors", "0.6.2"),),
        tensor_index_digest=digest_bytes(b"S07 tensor index"),
        config_digest=digest_bytes(b"S07 config"),
        architecture="S07IntegrityTransformer",
        operator_set=("attention", "matmul"),
        tokenizer_digest=digest_bytes(b"S07 tokenizer"),
        processor_digest=digest_bytes(b"S07 processor"),
        template_digest=digest_bytes(b"S07 template"),
        precision_scheme="u8-fixture",
        license_digest=digest_bytes(b"S07 license"),
        parent_ids=(digest_bytes(b"S07 parent"),),
        transform_manifest_digest=digest_bytes(b"S07 transform"),
    )


def _corrupt(path: Path, offset: int = 0) -> None:
    payload = bytearray(path.read_bytes())
    payload[offset] ^= 0xFF
    path.write_bytes(payload)


def _states(report, object_id: str) -> list[str]:
    return [state for subject, _, state in report.transitions if subject == object_id]


def test_q53_exact_boundary_and_fragmented_reservation():
    """Q53 acceptance: exact capacity passes; fragmented and overflowing reservations fail first."""

    device_bytes = 200 * GIB
    phase = CapacityPhase(committed=23, inflight=41, candidate=59, repair=1 * GIB)
    expected = phase.total + 10 * GIB
    requested = []

    exact = reserve_capacity(
        "s07-exact",
        device_bytes=device_bytes,
        allocatable_verified_free=expected,
        phases=(phase,),
        reserve_extent=lambda length: requested.append(length) is None,
    )
    assert exact.required_bytes == expected
    assert exact.safety_bytes == 10 * GIB
    assert requested == [expected]

    fragments = (expected - 1, 1)
    untouched_model_bytes = b"no transfer or mutation"
    with pytest.raises(CassetteError) as fragmented:
        reserve_capacity(
            "s07-fragmented",
            device_bytes=device_bytes,
            allocatable_verified_free=sum(fragments),
            phases=(phase,),
            reserve_extent=lambda length: any(fragment >= length for fragment in fragments),
        )
    assert fragmented.value.code == "CAPACITY_EXCEEDED"
    assert "preallocate" in fragmented.value.detail
    assert untouched_model_bytes == b"no transfer or mutation"

    allocator_called = False

    def forbidden_allocator(_):
        nonlocal allocator_called
        allocator_called = True
        return True

    with pytest.raises(CassetteError) as overflow:
        reserve_capacity(
            "s07-overflow",
            device_bytes=2**64 - 1,
            allocatable_verified_free=2**64 - 1,
            phases=(CapacityPhase(committed=2**64 - 1, inflight=1),),
            reserve_extent=forbidden_allocator,
        )
    assert overflow.value.code == "CAPACITY_EXCEEDED"
    assert "unsigned 64-bit" in overflow.value.detail
    assert allocator_called is False


def test_q62_corrupt_page_index_root_and_parity_repair(tmp_path):
    """Q62 acceptance: detect each object before use, repair exact bytes, and block exact pages."""

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
    root = load_root(cartridge, root_digest)
    insufficient = reserve_capacity(
        "s07-insufficient-repair",
        device_bytes=200 * GIB,
        allocatable_verified_free=10 * GIB + 1,
        phases=(CapacityPhase(repair=1),),
        reserve_extent=lambda _: True,
    )
    with pytest.raises(CassetteError) as repair_capacity:
        create_repair_set(cartridge, root_digest, insufficient)
    assert repair_capacity.value.code == "CAPACITY_EXCEEDED"
    assert not (cartridge / "repair").exists()

    phase = CapacityPhase(repair=1 * GIB)
    reservation = reserve_capacity(
        "s07-repair-set",
        device_bytes=200 * GIB,
        allocatable_verified_free=phase.total + 10 * GIB,
        phases=(phase,),
        reserve_extent=lambda _: True,
    )
    repair_set = create_repair_set(cartridge, root_digest, reservation)
    assert repair_set.required_bytes <= phase.repair
    assert verify_revision(cartridge, root_digest).available

    locations = {location.page_digest: location for location in page_locations(cartridge, root_digest)}
    alpha_digest = next(
        tensor_map["spans"][0]["page_digest"]
        for tensor_map in root["tensor_maps"]
        if tensor_map["semantic_tensor_id"] == "alpha"
    )
    alpha_location = locations[alpha_digest]
    segment_path = cartridge / "segments" / alpha_location.segment_id[7:]
    segment_bytes = segment_path.read_bytes()
    _corrupt(segment_path, alpha_location.offset)
    with pytest.raises(CassetteError) as page_use:
        read_tensor(cartridge, root_digest, "alpha")
    assert page_use.value.code == "PAGE_CORRUPT"
    page_report = verify_revision(cartridge, root_digest)
    assert page_report.unavailable_pages == (alpha_digest,)
    assert _states(page_report, f"page:{alpha_digest}") == ["SUSPECT", "VERIFYING", "CORRUPT"]
    corrupt_segment_bytes = segment_path.read_bytes()
    with pytest.raises(CassetteError) as repair_extent:
        repair_revision(cartridge, root_digest, insufficient)
    assert repair_extent.value.code == "CAPACITY_EXCEEDED"
    assert segment_path.read_bytes() == corrupt_segment_bytes
    page_repair = repair_revision(cartridge, root_digest, reservation)
    assert _states(page_repair, f"page:{alpha_digest}") == [
        "SUSPECT", "VERIFYING", "CORRUPT", "REPAIRING", "VALID",
    ]
    assert segment_path.read_bytes() == segment_bytes
    assert digest_bytes(segment_path.read_bytes()) == alpha_location.segment_id
    assert read_tensor(cartridge, root_digest, "alpha") == alpha

    index_path = cartridge / "indexes" / root_digest[7:]
    index_bytes = index_path.read_bytes()
    _corrupt(index_path)
    with pytest.raises(CassetteError) as index_use:
        load_root(cartridge, root_digest)
    assert index_use.value.code == "ROOT_INVALID"
    index_repair = repair_revision(cartridge, root_digest, reservation)
    assert _states(index_repair, f"index:{root_digest}") == [
        "SUSPECT", "VERIFYING", "CORRUPT", "REPAIRING", "VALID",
    ]
    assert index_path.read_bytes() == index_bytes
    assert digest_bytes(index_path.read_bytes()) == repair_set.index_digest
    assert load_root(cartridge, root_digest) == root

    root_path = cartridge / "roots" / root_digest[7:]
    root_bytes = root_path.read_bytes()
    _corrupt(root_path)
    with pytest.raises(CassetteError) as root_use:
        load_root(cartridge, root_digest)
    assert root_use.value.code == "ROOT_INVALID"
    root_repair = repair_revision(cartridge, root_digest, reservation)
    assert _states(root_repair, f"root:{root_digest}") == [
        "SUSPECT", "VERIFYING", "CORRUPT", "REPAIRING", "VALID",
    ]
    assert root_path.read_bytes() == root_bytes
    assert digest_bytes(root_path.read_bytes()) == root_digest

    parity_digest = repair_set.parity_digests[0]
    parity_path = cartridge / "repair" / "objects" / parity_digest[7:]
    parity_bytes = parity_path.read_bytes()
    _corrupt(parity_path)
    parity_report = verify_revision(cartridge, root_digest)
    assert parity_report.available
    assert dict(parity_report.states)[f"parity:{parity_digest}"] == "CORRUPT"
    parity_repair = repair_revision(cartridge, root_digest, reservation)
    assert _states(parity_repair, f"parity:{parity_digest}") == [
        "SUSPECT", "VERIFYING", "CORRUPT", "REPAIRING", "VALID",
    ]
    assert parity_path.read_bytes() == parity_bytes
    assert digest_bytes(parity_path.read_bytes()) == parity_digest

    _corrupt(segment_path, alpha_location.offset)
    _corrupt(parity_path)
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
    assert digest_bytes(parity_path.read_bytes()) == parity_digest
    assert load_root(cartridge, root_digest) == root
    assert any((cartridge / "quarantine").iterdir())
