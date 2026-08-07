# test_s05_store.py — S05 scratch-cartridge fixture for Q57 import, relocation, and span resolution; depends on errors.py, schema/validator.py, store.py.
"""S05 proves each named Q57 clause against one real SafeTensors byte layout."""

from dataclasses import replace
import json
from pathlib import Path

import pytest

from errors import CassetteError
from schema.validator import validate
from store import (
    ArtifactIdentity,
    IdentityTuple,
    PAGE_BYTES,
    canonical_bytes,
    digest_bytes,
    import_safetensors,
    load_root,
    model_identity,
    page_locations,
    read_tensor,
    repack_segments,
)


def _write_safetensors(path: Path, tensors: tuple[tuple[str, str, tuple[int, ...], bytes], ...]) -> None:
    offset = 0
    header = {"__metadata__": {"fixture": "S05"}}
    payloads = []
    for name, dtype, shape, payload in tensors:
        header[name] = {
            "dtype": dtype,
            "shape": list(shape),
            "data_offsets": [offset, offset + len(payload)],
        }
        payloads.append(payload)
        offset += len(payload)
    encoded = json.dumps(header, separators=(",", ":")).encode()
    encoded += b" " * (-len(encoded) % 8)
    path.write_bytes(len(encoded).to_bytes(8, "little") + encoded + b"".join(payloads))


def _identity(*sources: Path) -> IdentityTuple:
    artifacts = tuple(
        ArtifactIdentity(path.name, path.stat().st_size, digest_bytes(path.read_bytes()))
        for path in sorted(sources)
    )
    return IdentityTuple(
        revision_kind="executable",
        source_kind="huggingface",
        source_alias="fixture/model@main",
        canonical_locator="fixture/model",
        requested_revision="main",
        immutable_revision="git-sha1:0123456789abcdef0123456789abcdef01234567",
        artifacts=artifacts,
        format_versions=(("safetensors", "0.6.2"),),
        tensor_index_digest=digest_bytes(b"S05 tensor index"),
        config_digest=digest_bytes(b"S05 config"),
        architecture="S05BoundaryTransformer",
        operator_set=("attention", "matmul", "rms_norm"),
        tokenizer_digest=digest_bytes(b"S05 tokenizer"),
        processor_digest=digest_bytes(b"S05 processor"),
        template_digest=digest_bytes(b"S05 template"),
        precision_scheme="u8-fixture",
        license_digest=digest_bytes(b"S05 license"),
        parent_ids=(digest_bytes(b"S05 parent"),),
        transform_manifest_digest=digest_bytes(b"S05 transform"),
    )


def _write_root_variant(cartridge: Path, base_digest: str, root: dict) -> str:
    payload = canonical_bytes(root)
    root_digest = digest_bytes(payload)
    (cartridge / "roots" / root_digest[7:]).write_bytes(payload)
    (cartridge / "indexes" / root_digest[7:]).write_bytes(
        (cartridge / "indexes" / base_digest[7:]).read_bytes()
    )
    return root_digest


def test_q57_safetensors_import_relocation_and_span_resolution(tmp_path):
    """Q57 acceptance: bind SafeTensors to Q1, repack physically, and resolve every span."""

    head = b"A" * (PAGE_BYTES - 3)
    crossing = b"0123456789"
    tail = b"B" * 13
    first_source = tmp_path / "model-00001-of-00002.safetensors"
    second_source = tmp_path / "model-00002-of-00002.safetensors"
    cartridge = tmp_path / "cartridge"
    _write_safetensors(first_source, (
        ("head", "U8", (len(head),), head),
        ("crossing", "U8", (len(crossing),), crossing),
    ))
    _write_safetensors(second_source, (
        ("tail", "U8", (len(tail),), tail),
    ))
    material = _identity(first_source, second_source)
    sources = {
        second_source.name: second_source,
        first_source.name: first_source,
    }

    false_material = replace(
        material,
        artifacts=(
            replace(material.artifacts[0], digest=digest_bytes(b"unrelated artifact")),
            *material.artifacts[1:],
        ),
    )
    with pytest.raises(CassetteError) as rejected:
        import_safetensors(sources, tmp_path / "rejected-cartridge", false_material)
    assert rejected.value.code == "IDENTITY_MISMATCH"
    assert not (tmp_path / "rejected-cartridge" / "roots").exists()

    root_digest = import_safetensors(sources, cartridge, material)
    assert import_safetensors(
        {first_source.name: first_source, second_source.name: second_source},
        tmp_path / "ordered-cartridge",
        material,
    ) == root_digest
    root_before = load_root(cartridge, root_digest)
    maps = {tensor_map["semantic_tensor_id"]: tensor_map for tensor_map in root_before["tensor_maps"]}
    assert validate("root", root_before) == []
    assert root_before["identity"] == model_identity(material)
    assert root_before["parents"] == list(material.parent_ids)
    assert root_before["operators"] == sorted(material.operator_set)
    assert root_before["semantic_assets"] == {
        "processor": material.processor_digest,
        "template": material.template_digest,
        "tokenizer": material.tokenizer_digest,
    }
    assert root_before["provenance"]["identity_material"]["artifacts"] == [
        {"path": artifact.path, "size": artifact.size, "digest": artifact.digest}
        for artifact in material.artifacts
    ]
    assert set(maps) == {"head", "crossing", "tail"}
    assert [container["path"] for container in root_before["provenance"]["containers"]] == [
        first_source.name, second_source.name,
    ]
    assert len(page_locations(cartridge, root_digest)) == 3
    page_only_digest = digest_bytes(canonical_bytes([
        {"page_digest": location.page_digest, "length": location.length}
        for location in page_locations(cartridge, root_digest)
    ]))
    assert root_before["integrity_root"] != page_only_digest

    false_identity_root = {**root_before, "identity": digest_bytes(b"unrelated identity")}
    false_identity_digest = _write_root_variant(cartridge, root_digest, false_identity_root)
    with pytest.raises(CassetteError) as false_identity:
        load_root(cartridge, false_identity_digest)
    assert false_identity.value.code == "ROOT_INVALID"
    assert "Q1 identity" in false_identity.value.detail

    uncovered_manifest = {**root_before, "plans": ["uncovered mutation"]}
    uncovered_digest = _write_root_variant(cartridge, root_digest, uncovered_manifest)
    with pytest.raises(CassetteError) as uncovered:
        load_root(cartridge, uncovered_digest)
    assert uncovered.value.code == "ROOT_INVALID"
    assert "integrity aggregate" in uncovered.value.detail

    assert read_tensor(cartridge, root_digest, "head") == head
    assert read_tensor(cartridge, root_digest, "crossing") == crossing
    assert read_tensor(cartridge, root_digest, "tail") == tail
    assert [
        (span["offset"], span["length"], span["tensor_offset"])
        for span in maps["crossing"]["spans"]
    ] == [(PAGE_BYTES - 3, 3, 0), (0, 7, 3)]

    before = {location.page_digest: (location.segment_id, location.offset)
              for location in page_locations(cartridge, root_digest)}
    physical_order = tuple(
        location.page_digest
        for location in sorted(page_locations(cartridge, root_digest),
                               key=lambda location: (location.segment_id, location.offset))
    )
    assert repack_segments(cartridge, root_digest, tuple(reversed(physical_order))) == root_digest
    after = {location.page_digest: (location.segment_id, location.offset)
             for location in page_locations(cartridge, root_digest)}
    assert after != before
    assert load_root(cartridge, root_digest) == root_before
    assert read_tensor(cartridge, root_digest, "head") == head
    assert read_tensor(cartridge, root_digest, "crossing") == crossing
    assert read_tensor(cartridge, root_digest, "tail") == tail
