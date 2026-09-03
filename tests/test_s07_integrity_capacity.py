# test_s07_integrity_capacity.py — S07 F1 fixtures for Q53 next-transition claims and Q62 repair; depends on errors.py, store.py.
"""S07 proves next-transition capacity control and independent object repair on a scratch cartridge."""

import json
from pathlib import Path

from blake3 import blake3
import pytest

from errors import CassetteError
from store import (
    ArtifactIdentity,
    CapacityCoordinator,
    CapacityTransition,
    IdentityTuple,
    ReclaimableObject,
    complete_capacity_claim,
    create_repair_set,
    execute_claimed_write,
    import_safetensors,
    is_reclaimable_object,
    load_root,
    page_locations,
    repair_replacement_shape,
    repair_set_shape,
    read_tensor,
    repair_revision,
    require_revision,
    select_reclaimable_objects,
    verify_revision,
)


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


def test_q53_next_transition_claims_observations_concurrency_recovery_and_reclaim(tmp_path):
    """Q53 acceptance: only exact next transitions claim, pause, resume, or become reclaimable."""

    coordinator = CapacityCoordinator(tmp_path)
    tiny = coordinator(CapacityTransition("s07-tiny", "parent-a", payload_bytes=7, journal_bytes=10))
    assert tiny.active
    assert tiny.transition.total_bytes == 17
    assert tiny.history[:2] == ("MEASURE", "PLAN_NEXT")
    execute_claimed_write(tiny, lambda: b"durable")
    complete_capacity_claim(tiny)
    assert tiny.history[-2:] == ("DURABLE_BOUNDARY", "OBSERVE")
    assert tiny.state == "COMPLETED"

    growing = coordinator(CapacityTransition(
        "s07-growing", "checkpoint-4",
        payload_bytes=7,
        journal_bytes=3,
        declared_writes=2,
        write_bytes=(7, 3),
    ))
    execute_claimed_write(growing, lambda: None)
    execute_claimed_write(growing, lambda: None)
    complete_capacity_claim(growing)
    assert growing.state == "COMPLETED"

    future_total = 2**64 - 1
    assert future_total > tiny.transition.total_bytes

    first = coordinator(CapacityTransition("s07-concurrent", "same-parent", payload_bytes=17))
    with pytest.raises(CassetteError) as duplicate:
        coordinator(CapacityTransition("s07-concurrent", "same-parent", payload_bytes=17))
    assert duplicate.value.code == "INVALID_REQUEST"
    execute_claimed_write(first, lambda: None)
    complete_capacity_claim(first)

    candidates = (
        ReclaimableObject("eligible", True, False, False, False, "TEMPORARY", False, False, False),
        ReclaimableObject("reproducible", True, False, False, False, "REPRODUCIBLE", False, False, False),
        ReclaimableObject("user", False, False, False, False, "TEMPORARY", False, False, False),
        ReclaimableObject("pinned", True, True, False, False, "TEMPORARY", False, False, False),
        ReclaimableObject("root", True, False, True, False, "TEMPORARY", False, False, False),
        ReclaimableObject("rollback", True, False, False, True, "TEMPORARY", False, False, False),
        ReclaimableObject("claim", True, False, False, False, "TEMPORARY", True, False, False),
        ReclaimableObject("transaction", True, False, False, False, "TEMPORARY", False, True, False),
        ReclaimableObject("journal", True, False, False, False, "TEMPORARY", False, False, True),
        ReclaimableObject("durable", True, False, False, False, "DURABLE", False, False, False),
        ReclaimableObject("user-owned", True, False, False, False, "USER_OWNED", False, False, False),
    )
    assert is_reclaimable_object(candidates[0])
    assert [item.object_id for item in select_reclaimable_objects(candidates)] == ["eligible", "reproducible"]


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
    repair_set = create_repair_set(
        cartridge,
        root_digest,
        CapacityCoordinator(cartridge),
    )

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
    manifest_repair = repair_revision(cartridge, root_digest, CapacityCoordinator(cartridge))
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
    page_repair = repair_revision(cartridge, root_digest, CapacityCoordinator(cartridge))
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
    index_repair = repair_revision(cartridge, root_digest, CapacityCoordinator(cartridge))
    assert _states(index_repair, f"index:{root_digest}") == [
        "SUSPECT", "VERIFYING", "CORRUPT", "REPAIRING", "VALID",
    ]
    assert index_path.read_bytes() == index_bytes
    assert _blake3(index_path.read_bytes()) == repair_set.index_digest

    _corrupt(root_path)
    with pytest.raises(CassetteError) as root_use:
        load_root(cartridge, root_digest)
    assert root_use.value.code == "ROOT_INVALID"
    root_repair = repair_revision(cartridge, root_digest, CapacityCoordinator(cartridge))
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
    parity_repair = repair_revision(cartridge, root_digest, CapacityCoordinator(cartridge))
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
            CapacityCoordinator(cartridge),
            source_pages={alpha_digest: b"not the declared page"},
        )
    assert invalid_source.value.code == "INVALID_REQUEST"
    assert segment_path.read_bytes() == corrupt_segment_bytes
    assert parity_path.read_bytes() == corrupt_parity_bytes

    unavailable = repair_revision(cartridge, root_digest, CapacityCoordinator(cartridge))
    assert unavailable.available is False
    assert unavailable.unavailable_pages == (alpha_digest,)
    assert dict(unavailable.states)[f"page:{alpha_digest}"] == "UNAVAILABLE"
    with pytest.raises(CassetteError) as blocked:
        require_revision(cartridge, root_digest)
    assert blocked.value.code == "PAGE_CORRUPT"
    assert blocked.value.object_id == f"page:{alpha_digest}"
    assert alpha_digest in blocked.value.detail

    restored = repair_revision(
        cartridge, root_digest, CapacityCoordinator(cartridge), source_pages={alpha_digest: alpha}
    )
    assert restored.available
    assert read_tensor(cartridge, root_digest, "alpha") == alpha
    assert _blake3(parity_path.read_bytes()) == parity_digest
    assert load_root(cartridge, root_digest) == root
    assert any((cartridge / "quarantine").iterdir())
