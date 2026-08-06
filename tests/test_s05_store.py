# test_s05_store.py — S05 scratch-cartridge fixture for Q57 import, relocation, and span resolution; depends on schema/validator.py, store.py.
"""S05 proves each named Q57 clause against one real SafeTensors byte layout."""

import json
from pathlib import Path

from schema.validator import validate
from store import (
    PAGE_BYTES,
    digest_bytes,
    import_safetensors,
    load_root,
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


def test_q57_safetensors_import_relocation_and_span_resolution(tmp_path):
    """Q57 acceptance: import SafeTensors, repack physically, preserve the root, and resolve all spans."""

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

    root_digest = import_safetensors(
        (second_source, first_source), cartridge, digest_bytes(b"S05 model identity")
    )
    root_before = load_root(cartridge, root_digest)
    maps = {tensor_map["semantic_tensor_id"]: tensor_map for tensor_map in root_before["tensor_maps"]}
    assert validate("root", root_before) == []
    assert set(maps) == {"head", "crossing", "tail"}
    assert [artifact["name"] for artifact in root_before["provenance"]["artifacts"]] == [
        first_source.name, second_source.name,
    ]
    assert len(page_locations(cartridge, root_digest)) == 3

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
