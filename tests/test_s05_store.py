# test_s05_store.py — S05 Q57 SafeTensors/GGUF import, ordered deltas, relocation, and span fixture; depends on errors.py, schema/validator.py, store.py.
"""S05 proves each assigned storage-level Q57 clause against real container bytes."""

from dataclasses import replace
import json
from pathlib import Path
import struct

from blake3 import blake3
import pytest

from errors import CassetteError
from schema.validator import validate
from store import (
    ArtifactIdentity,
    IdentityTuple,
    PAGE_BYTES,
    append_training_delta,
    canonical_bytes,
    digest_bytes,
    import_gguf,
    import_safetensors,
    load_root,
    model_identity,
    page_locations,
    read_training_delta,
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


def _write_gguf(
    path: Path, tensors: tuple[tuple[str, int, tuple[int, ...], bytes], ...]
) -> None:
    """Write the exact GGUF v3 subset exercised by the bounded importer."""

    def string(value: str) -> bytes:
        encoded = value.encode()
        return struct.pack("<Q", len(encoded)) + encoded

    header = bytearray(b"GGUF" + struct.pack("<IQQ", 3, len(tensors), 1))
    header.extend(string("general.alignment"))
    header.extend(struct.pack("<II", 4, 1))
    offset = 0
    payloads = []
    for name, tensor_type, shape, payload in tensors:
        header.extend(string(name))
        header.extend(struct.pack("<I", len(shape)))
        header.extend(b"".join(struct.pack("<Q", dimension) for dimension in shape))
        header.extend(struct.pack("<IQ", tensor_type, offset))
        payloads.append(payload)
        offset += len(payload)
    path.write_bytes(bytes(header) + b"".join(payloads))


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


def _write_root_variant(
    cartridge: Path, base_digest: str, root: dict, *, repair_integrity: bool = False
) -> str:
    if repair_integrity:
        manifest = {
            field: root[field]
            for field in sorted(set(root) - {"integrity_root", "semantic_assets"})
        }
        leaves = [{"kind": "manifest", "name": "root", "value": manifest}]
        leaves.extend(
            {"kind": "page", "digest": location.page_digest, "length": location.length}
            for location in page_locations(cartridge, base_digest)
        )
        leaves.extend(
            {"kind": "semantic_asset", "name": name, "value": value}
            for name, value in root["semantic_assets"].items()
        )
        encoded_leaves = sorted(map(canonical_bytes, leaves))
        layer = [blake3(b"\x00" + encoded).digest() for encoded in encoded_leaves]
        while len(layer) > 1:
            if len(layer) % 2:
                layer.append(layer[-1])
            layer = [
                blake3(b"\x01" + layer[index] + layer[index + 1]).digest()
                for index in range(0, len(layer), 2)
            ]
        root["integrity_root"] = f"blake3:{layer[0].hex()}"
    payload = canonical_bytes(root)
    root_digest = digest_bytes(payload)
    (cartridge / "roots" / root_digest[7:]).write_bytes(payload)
    (cartridge / "indexes" / root_digest[7:]).write_bytes(
        (cartridge / "indexes" / base_digest[7:]).read_bytes()
    )
    return root_digest


def test_q57_safetensors_import_relocation_and_span_resolution(tmp_path):
    """Q57 acceptance: import SafeTensors/GGUF, bind Q1, repack, and resolve every span."""

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

    uncovered_manifest = {**root_before, "plans": [{"uncovered": "mutation"}]}
    uncovered_digest = _write_root_variant(cartridge, root_digest, uncovered_manifest)
    with pytest.raises(CassetteError) as uncovered:
        load_root(cartridge, uncovered_digest)
    assert uncovered.value.code == "ROOT_INVALID"
    assert "integrity aggregate" in uncovered.value.detail

    assert read_tensor(cartridge, root_digest, "head") == head
    assert read_tensor(cartridge, root_digest, "crossing") == crossing
    assert read_tensor(cartridge, root_digest, "tail") == tail

    gguf_source = tmp_path / "model.gguf"
    gguf_cartridge = tmp_path / "gguf-cartridge"
    _write_gguf(
        gguf_source,
        (
            ("head", 24, (len(head),), head),
            ("crossing", 24, (len(crossing),), crossing),
            ("tail", 24, (len(tail),), tail),
        ),
    )
    gguf_material = replace(
        _identity(gguf_source),
        format_versions=(("gguf", "3"),),
        tensor_index_digest=digest_bytes(b"S05 GGUF tensor index"),
    )
    gguf_root_digest = import_gguf(
        {gguf_source.name: gguf_source}, gguf_cartridge, gguf_material
    )
    false_gguf_material = replace(
        gguf_material,
        artifacts=(
            replace(gguf_material.artifacts[0], digest=digest_bytes(b"foreign GGUF")),
        ),
    )
    with pytest.raises(CassetteError) as rejected_gguf:
        import_gguf(
            {gguf_source.name: gguf_source},
            tmp_path / "rejected-gguf-cartridge",
            false_gguf_material,
        )
    assert rejected_gguf.value.code == "IDENTITY_MISMATCH"
    gguf_root = load_root(gguf_cartridge, gguf_root_digest)
    gguf_maps = {
        tensor_map["semantic_tensor_id"]: tensor_map
        for tensor_map in gguf_root["tensor_maps"]
    }
    assert gguf_root["provenance"]["containers"] == [
        {
            "path": gguf_source.name,
            "format": "gguf",
            "metadata": {
                "alignment": "1",
                "metadata_digest": digest_bytes(canonical_bytes({"general.alignment": 1})),
                "version": "3",
            },
        }
    ]
    assert {tensor_map["codec"] for tensor_map in gguf_maps.values()} == {"gguf-block"}
    assert [
        (span["offset"], span["length"], span["tensor_offset"])
        for span in gguf_maps["crossing"]["spans"]
    ] == [(PAGE_BYTES - 3, 3, 0), (0, 7, 3)]
    assert read_tensor(gguf_cartridge, gguf_root_digest, "head") == head
    assert read_tensor(gguf_cartridge, gguf_root_digest, "crossing") == crossing
    assert read_tensor(gguf_cartridge, gguf_root_digest, "tail") == tail

    unsupported_gguf = tmp_path / "unsupported.gguf"
    _write_gguf(unsupported_gguf, (("unknown", 4_294_967_295, (1,), b"x"),))
    unsupported_material = replace(
        _identity(unsupported_gguf),
        format_versions=(("gguf", "3"),),
    )
    with pytest.raises(CassetteError) as unsupported:
        import_gguf(
            {unsupported_gguf.name: unsupported_gguf},
            tmp_path / "unsupported-gguf-cartridge",
            unsupported_material,
        )
    assert unsupported.value.code == "ROOT_INVALID"
    assert "unsupported type" in unsupported.value.detail

    delta_pages = (b"adapter-page-A", b"adapter-page-B")
    manifest_digest = digest_bytes(b"S05 ordered adapter manifest")
    delta_body = {
        "kind": "adapter",
        "base_identity": root_before["identity"],
        "ordered_page_digests": [digest_bytes(page) for page in delta_pages],
        "manifest_digest": manifest_digest,
    }
    delta_record = {"delta_id": digest_bytes(canonical_bytes(delta_body)), **delta_body}
    child_material = replace(
        material,
        revision_kind="tuned",
        parent_ids=(root_before["identity"],),
        transform_manifest_digest=digest_bytes(canonical_bytes([delta_record])),
    )
    child_root_digest = append_training_delta(
        cartridge,
        root_digest,
        child_material,
        "adapter",
        delta_pages,
        manifest_digest,
    )
    child_root = load_root(cartridge, child_root_digest)
    assert child_root["deltas"] == [delta_record]
    assert child_root["parents"] == [root_before["identity"]]
    assert child_root["identity"] == model_identity(child_material)
    assert read_training_delta(
        cartridge, child_root_digest, delta_record["delta_id"]
    ) == delta_pages
    assert len(page_locations(cartridge, child_root_digest)) == len(
        page_locations(cartridge, root_digest)
    ) + len(delta_pages)
    assert load_root(cartridge, root_digest) == root_before

    forged_delta_root = json.loads(json.dumps(child_root))
    forged_delta_root["deltas"][0]["manifest_digest"] = digest_bytes(b"forged manifest")
    forged_delta_digest = _write_root_variant(
        cartridge, child_root_digest, forged_delta_root, repair_integrity=True
    )
    with pytest.raises(CassetteError) as forged_delta:
        load_root(cartridge, forged_delta_digest)
    assert forged_delta.value.code == "ROOT_INVALID"
    assert "delta identity" in forged_delta.value.detail

    detached_material = replace(
        child_material,
        transform_manifest_digest=digest_bytes(b"detached but internally valid transform"),
    )
    detached_root = json.loads(json.dumps(child_root))
    detached_root["provenance"]["identity_material"]["transform_manifest_digest"] = (
        detached_material.transform_manifest_digest
    )
    detached_root["identity"] = model_identity(detached_material)
    detached_root_digest = _write_root_variant(
        cartridge, child_root_digest, detached_root, repair_integrity=True
    )
    with pytest.raises(CassetteError) as detached_record:
        load_root(cartridge, detached_root_digest)
    assert detached_record.value.code == "ROOT_INVALID"
    assert "complete ordered delta record" in detached_record.value.detail

    foreign_body = {**delta_body, "base_identity": digest_bytes(b"foreign parent")}
    foreign_delta = {"delta_id": digest_bytes(canonical_bytes(foreign_body)), **foreign_body}
    foreign_material = replace(
        child_material,
        transform_manifest_digest=digest_bytes(canonical_bytes([foreign_delta])),
    )
    foreign_root = json.loads(json.dumps(child_root))
    foreign_root["deltas"] = [foreign_delta]
    foreign_root["provenance"]["identity_material"]["transform_manifest_digest"] = (
        foreign_material.transform_manifest_digest
    )
    foreign_root["identity"] = model_identity(foreign_material)
    foreign_root_digest = _write_root_variant(
        cartridge, child_root_digest, foreign_root, repair_integrity=True
    )
    with pytest.raises(CassetteError) as foreign_parent:
        load_root(cartridge, foreign_root_digest)
    assert foreign_parent.value.code == "ROOT_INVALID"
    assert "immediate parent" in foreign_parent.value.detail

    child_order = tuple(
        location.page_digest
        for location in sorted(
            page_locations(cartridge, child_root_digest),
            key=lambda location: (location.segment_id, location.offset),
            reverse=True,
        )
    )
    assert repack_segments(cartridge, child_root_digest, child_order) == child_root_digest
    assert read_training_delta(
        cartridge, child_root_digest, delta_record["delta_id"]
    ) == delta_pages
    assert read_tensor(cartridge, child_root_digest, "crossing") == crossing

    false_child = replace(
        child_material,
        transform_manifest_digest=digest_bytes(b"unrelated delta transform"),
    )
    with pytest.raises(CassetteError) as detached_delta:
        append_training_delta(
            cartridge,
            root_digest,
            false_child,
            "adapter",
            delta_pages,
            manifest_digest,
        )
    assert detached_delta.value.code == "IDENTITY_MISMATCH"
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
