# test_s20_hardware_plans.py — Q11/Q59 portable-plan acceptance over one immutable executable capacity; depends on compiler.py, errors.py, store.py, tests/compiler_fixture.py, tests/test_s13_pager.py.
"""Prove plan replacement and selection without copied weights or mutable certificate budgets."""

from __future__ import annotations

import copy
import hashlib
from pathlib import Path
import struct

import pytest

import compiler
from compiler import prepare_hardware_plans, select_hardware_plan, verify_hardware_plans
from compiler_fixture import manifest
from errors import CassetteError
from store import (
    ArtifactIdentity,
    IdentityTuple,
    PAGE_BYTES,
    PageLocation,
    canonical_bytes,
    derive_root,
    digest_bytes,
    import_safetensors,
    inspect_safetensors,
    load_root,
    model_identity,
    page_index_byte_count,
    page_locations,
    repack_segments,
)
from test_s13_pager import _fixture as q19_fresh_fixture

GIB = 1024**3


def _digest(value: object) -> str:
    return digest_bytes(canonical_bytes(value))


def _seal(document: dict, field: str) -> None:
    document[field] = _digest({name: value for name, value in document.items() if name != field})


def _compiled_fixture(tmp_path: Path):
    """Build the platform-neutral immutable S19 boundary that S20 is specified to consume."""

    cartridge = tmp_path / "cartridge"
    incoming = cartridge / "incoming"
    incoming.mkdir(parents=True)
    document = manifest("s20-hardware-plans")
    weights = struct.pack("<4f", 1.0, 0.0, 0.0, 1.0)
    padding = b"\0" * (32 * 1024 * 1024)
    metadata = canonical_bytes(document).decode()
    header = {
        "__metadata__": {"cassette.compiler.v1": metadata},
        "padding": {
            "dtype": "U8",
            "shape": [len(padding)],
            "data_offsets": [len(weights), len(weights) + len(padding)],
        },
        "weight": {"dtype": "F32", "shape": [2, 2], "data_offsets": [0, len(weights)]},
    }
    encoded = canonical_bytes(header)
    encoded += b" " * (-len(encoded) % 8)
    payload = len(encoded).to_bytes(8, "little") + encoded + weights + padding
    artifact_path = "model.safetensors"
    path = incoming / artifact_path
    path.write_bytes(payload)
    tensor_index = [
        {
            "artifact_path": artifact_path,
            "semantic_tensor_id": "padding",
            "dtype": "U8",
            "shape": [len(padding)],
            "offset": len(weights),
            "length": len(padding),
        },
        {
            "artifact_path": artifact_path,
            "semantic_tensor_id": "weight",
            "dtype": "F32",
            "shape": [2, 2],
            "offset": 0,
            "length": len(weights),
        },
    ]
    material = IdentityTuple(
        revision_kind="source",
        source_kind="huggingface",
        source_alias="recluse/s20-hardware-plans",
        canonical_locator="recluse/s20-hardware-plans",
        requested_revision=None,
        immutable_revision="git-sha1:" + "2" * 40,
        artifacts=(ArtifactIdentity(
            artifact_path,
            len(payload),
            "sha256:" + hashlib.sha256(payload).hexdigest(),
        ),),
        format_versions=tuple(tuple(item) for item in document["model"]["format_versions"]),
        tensor_index_digest=_digest(tensor_index),
        config_digest=_digest(document["model"]["config"]),
        architecture=document["model"]["architecture"],
        operator_set=tuple(sorted({row["operator"] for row in document["operator_inventory"]})),
        tokenizer_digest=document["model"]["tokenizer_digest"],
        processor_digest=document["model"]["processor_digest"],
        template_digest=document["model"]["template_digest"],
        precision_scheme=document["model"]["precision_scheme"],
        license_digest="blake3:" + "3" * 64,
        parent_ids=(),
        transform_manifest_digest=None,
    )
    source_root_digest = import_safetensors({artifact_path: path}, cartridge, material)
    source_root = load_root(cartridge, source_root_digest)
    inspected = inspect_safetensors(path, material.artifacts[0].digest)
    tensors = sorted(
        [{"artifact_path": artifact_path, **tensor} for tensor in inspected["tensors"]],
        key=lambda row: row["semantic_tensor_id"],
    )
    values, shape = compiler._decode_tensor(
        source_root, cartridge, source_root_digest, document["target_tensor"]
    )
    evidence = copy.deepcopy(document["evidence"])
    evidence["target"]["source_values"] = values
    assert evidence["target"]["source_shape"] == shape
    certificate = compiler._certificate(
        evidence, document["eta_rep"], document["rank_budget"], document["operation_bounds"]
    )
    tensor_inventory = compiler._tensor_inventory(tensors, source_root, source_root_digest)
    contribution = compiler._contribution_map(
        source_root,
        source_root_digest,
        certificate,
        document["target_tensor"],
        document["operator_inventory"],
        tensor_inventory,
    )
    base_plan = compiler._execution_plan(
        source_root,
        source_root_digest,
        certificate,
        document["profile"],
        contribution,
        document["operator_inventory"],
        document["prior_mode_failures"],
        cartridge,
    )
    proof = {
        "operator_inventory": document["operator_inventory"],
        "tensor_inventory": tensor_inventory,
        "evidence": evidence,
        "certificate": certificate,
        "profile": document["profile"],
        "contribution_map": contribution,
        "execution_plan": base_plan,
    }
    plan_digest = _digest({"s20": "platform-neutral-prerequisite"})
    source_identity = model_identity(material)
    bundle = {
        "version": "s19-compiler-v1",
        "source_identity": source_identity,
        "source_root": source_root_digest,
        "preparation_plan_digest": plan_digest,
        **proof,
        "extent_metrics": compiler._extent_metrics(
            source_root,
            proof,
            sum(location.length for location in page_locations(cartridge, source_root_digest)),
        ),
    }
    compiled_material = IdentityTuple(
        revision_kind="executable",
        source_kind=material.source_kind,
        source_alias=material.source_alias,
        canonical_locator=material.canonical_locator,
        requested_revision=material.requested_revision,
        immutable_revision=material.immutable_revision,
        artifacts=material.artifacts,
        format_versions=tuple((*material.format_versions, ("cassette", "s19-compiler-v1"))),
        tensor_index_digest=material.tensor_index_digest,
        config_digest=material.config_digest,
        architecture=material.architecture,
        operator_set=material.operator_set,
        tokenizer_digest=material.tokenizer_digest,
        processor_digest=material.processor_digest,
        template_digest=material.template_digest,
        precision_scheme=material.precision_scheme,
        license_digest=material.license_digest,
        parent_ids=(source_identity,),
        transform_manifest_digest=_digest(bundle),
    )
    compiled_root = derive_root(cartridge, source_root_digest, compiled_material, (bundle,))
    compiler.verify_bundle_structure(cartridge, compiled_root, source_identity, plan_digest)
    return cartridge, compiled_root, source_identity, plan_digest, certificate


def _specifications(cartridge: Path, root_digest: str, certificate: dict) -> list[dict]:
    pages = [
        location.page_digest
        for location in sorted(
            page_locations(cartridge, root_digest),
            key=lambda item: (item.segment_id, item.offset),
        )
    ]
    cases = sorted({
        row["operator_case_id"] for row in certificate["execution_contract"]["operations"]
    })
    assert cases
    classes = (
        ("c1-air-32", "c1_air_32", "s1_usb4_nvme_2tb", 32 * GIB, 500_000_000, 2_000_000, 2_000_000_000_000, False, 1, 1),
        ("c2-max-128", "c2_max_128", "s2_tb5_nvme_2tb", 128 * GIB, 1_000_000_000, 1_000_000, 2_000_000_000_000, False, 2, 2),
        ("c3-ultra-512", "c3_ultra_512", "s3_tb5_nvme_4tb_writable", 512 * GIB, 2_000_000_000, 500_000, 4_000_000_000_000, True, 8, 4),
    )
    result = []
    for name, apple, storage, memory, bandwidth, latency, capacity, writable, group_size, depth in classes:
        result.append({
            "plan_name": name,
            "profile_predicate": {
                "apple_class": apple,
                "storage_class": storage,
                "request_class": "INFERENCE",
                "minimum_unified_memory_bytes": memory,
                "minimum_recommended_working_set_bytes": memory,
                "minimum_sustained_read_bytes_per_second": bandwidth,
                "maximum_p99_read_latency_ns": latency,
                "minimum_storage_capacity_bytes": capacity,
                "requires_writable_storage": writable,
                "profile_evidence_digest": _digest({
                    "apple_class": apple,
                    "storage_class": storage,
                    "qualification": "Q42-fixture",
                }),
            },
            "page_order": pages,
            "read_groups": [pages[index:index + group_size] for index in range(0, len(pages), group_size)],
            "io_queue_depth": depth,
            "prefetch_policy": {
                "kind": "NONE" if name == "c1-air-32" else "ORDERED",
                "lookahead_pages": 0 if name == "c1-air-32" else min(group_size, len(pages)),
            },
        })
    return result


def _measured(spec: dict, certificate: dict) -> dict:
    predicate = spec["profile_predicate"]
    return {
        "apple_class": predicate["apple_class"],
        "storage_class": predicate["storage_class"],
        "request_class": predicate["request_class"],
        "unified_memory_bytes": predicate["minimum_unified_memory_bytes"],
        "recommended_max_working_set_bytes": predicate["minimum_recommended_working_set_bytes"],
        "sustained_read_bytes_per_second": predicate["minimum_sustained_read_bytes_per_second"],
        "p99_read_latency_ns": predicate["maximum_p99_read_latency_ns"],
        "storage_capacity_bytes": predicate["minimum_storage_capacity_bytes"],
        "operator_case_ids": sorted({
            row["operator_case_id"] for row in certificate["execution_contract"]["operations"]
        }),
        "apple_features": ["apple_silicon", "metal"],
        "writable_storage": predicate["requires_writable_storage"],
    }


def test_q11_q59_certified_hardware_plans_switch_without_weight_duplication(tmp_path):
    """Q11/Q59 acceptance: add, delete, and select exact-budget plans over unchanged pages."""

    cartridge, compiled_root, source_identity, plan_digest, certificate = _compiled_fixture(tmp_path)
    compiled = load_root(cartridge, compiled_root)
    source_mapping = page_locations(cartridge, compiled["plans"][0]["source_root"])
    repack_segments(
        cartridge,
        compiled_root,
        tuple(reversed([location.page_digest for location in source_mapping])),
    )
    mapping = page_locations(cartridge, compiled_root)
    assert mapping != source_mapping
    specifications = _specifications(cartridge, compiled_root, certificate)
    segment_snapshot = {
        path.name: (path.stat().st_ino, path.stat().st_size, path.stat().st_mtime_ns, digest_bytes(path.read_bytes()))
        for path in (cartridge / "segments").iterdir()
    }

    one_plan_root = prepare_hardware_plans(
        cartridge, compiled_root, source_identity, plan_digest, specifications[:1]
    )
    all_plan_root = prepare_hardware_plans(
        cartridge, one_plan_root, source_identity, plan_digest, specifications
    )
    assert prepare_hardware_plans(
        cartridge, compiled_root, source_identity, plan_digest, list(reversed(specifications))
    ) == all_plan_root
    two_plan_root = prepare_hardware_plans(
        cartridge, all_plan_root, source_identity, plan_digest, specifications[1:]
    )
    for root_digest in (one_plan_root, all_plan_root, two_plan_root):
        root = load_root(cartridge, root_digest)
        assert root["identity"] == compiled["identity"]
        assert root["tensor_maps"] == compiled["tensor_maps"]
        assert page_locations(cartridge, root_digest) == mapping
    assert segment_snapshot == {
        path.name: (path.stat().st_ino, path.stat().st_size, path.stat().st_mtime_ns, digest_bytes(path.read_bytes()))
        for path in (cartridge / "segments").iterdir()
    }

    plans = verify_hardware_plans(
        cartridge, all_plan_root, source_identity, plan_digest
    )
    assert [plan["plan_name"] for plan in plans] == [
        "c1-air-32", "c2-max-128", "c3-ultra-512"
    ]
    for plan in plans:
        assert plan["q19_certificate_digest"] == certificate["certificate_id"]
        assert plan["weight_payload_bytes"] == 0
        assert plan["description_budget"] == {"peak_bytes": 16, "total_bytes": 16}
        assert plan["metadata_budget"] == {"peak_bytes": 256, "total_bytes": 256}
        assert plan["fresh_sample_or_exact_read_budget"] == {
            "mode": "EXACT",
            "samples_peak": 0,
            "samples_total": 0,
            "traffic_peak": 0,
            "traffic_total": 0,
            "traffic_unit": "SCALARS",
            "physical_bytes_peak": 0,
            "physical_bytes_total": 0,
            "physical_page_reads_peak": 0,
            "physical_page_reads_total": 0,
            "certified_latency_ns_total": 0,
        }

    fresh_base_plan, fresh_certificate, _, _ = q19_fresh_fixture()
    fresh_page = PageLocation(
        digest_bytes(b"fresh-page"), digest_bytes(b"fresh-segment"), 0, PAGE_BYTES
    )
    fresh_base_plan["page_map_digest"] = _digest([
        {"page_digest": fresh_page.page_digest, "length": fresh_page.length}
    ])
    _seal(fresh_base_plan, "plan_id")
    fresh_spec = copy.deepcopy(specifications[0])
    fresh_spec["plan_name"] = "fresh-budget"
    fresh_spec["page_order"] = [fresh_page.page_digest]
    fresh_spec["read_groups"] = [[fresh_page.page_digest]]
    fresh_plan, _ = compiler._hardware_plan(
        fresh_spec, fresh_base_plan, fresh_certificate, (fresh_page,), 76
    )
    assert fresh_plan["description_budget"] == {"peak_bytes": 1024, "total_bytes": 3072}
    assert fresh_plan["metadata_budget"] == {"peak_bytes": 256, "total_bytes": 768}
    assert fresh_plan["fresh_sample_or_exact_read_budget"] == {
        "mode": "FRESH",
        "samples_peak": 3,
        "samples_total": 9,
        "traffic_peak": 9,
        "traffic_total": 27,
        "traffic_unit": "SCALARS",
        "physical_bytes_peak": 4096,
        "physical_bytes_total": 12_288,
        "physical_page_reads_peak": 1,
        "physical_page_reads_total": 3,
        "certified_latency_ns_total": 3000,
    }
    planned_root = load_root(cartridge, all_plan_root)
    allowance = sum(location.length for location in mapping) // 100
    assert sum(len(canonical_bytes(plan)) for plan in plans) <= allowance
    assert len(canonical_bytes(planned_root["plans"])) + page_index_byte_count(
        cartridge, all_plan_root
    ) <= allowance

    for spec in specifications:
        selected = select_hardware_plan(
            cartridge,
            all_plan_root,
            source_identity,
            plan_digest,
            _measured(spec, certificate),
        )
        assert selected.plan["plan_name"] == spec["plan_name"]
        assert selected.certificate_id == certificate["certificate_id"]
        assert selected.predicted_total_latency_ns > 0
    faster_c1 = copy.deepcopy(specifications[0])
    faster_c1["plan_name"] = "c1-air-32-coalesced"
    pages = faster_c1["page_order"]
    faster_c1["read_groups"] = [pages[index:index + 8] for index in range(0, len(pages), 8)]
    faster_c1["io_queue_depth"] = 4
    choice_root = prepare_hardware_plans(
        cartridge,
        compiled_root,
        source_identity,
        plan_digest,
        [specifications[0], faster_c1],
    )
    assert select_hardware_plan(
        cartridge,
        choice_root,
        source_identity,
        plan_digest,
        _measured(specifications[0], certificate),
    ).plan["plan_name"] == "c1-air-32-coalesced"
    insufficient = _measured(specifications[0], certificate)
    insufficient["sustained_read_bytes_per_second"] -= 1
    with pytest.raises(CassetteError) as no_plan:
        select_hardware_plan(
            cartridge, all_plan_root, source_identity, plan_digest, insufficient
        )
    assert no_plan.value.code == "CAPABILITY_MISMATCH"

    hostile_spec = copy.deepcopy(specifications[0])
    hostile_spec["weight_payload"] = "copied parameter bytes"
    with pytest.raises(CassetteError) as copied_input:
        prepare_hardware_plans(
            cartridge, compiled_root, source_identity, plan_digest, [hostile_spec]
        )
    assert copied_input.value.code == "INVALID_REQUEST"
    noncontiguous = copy.deepcopy(specifications[1])
    noncontiguous["page_order"][:2] = reversed(noncontiguous["page_order"][:2])
    noncontiguous["read_groups"][0][:2] = reversed(noncontiguous["read_groups"][0][:2])
    with pytest.raises(CassetteError) as false_coalescing:
        prepare_hardware_plans(
            cartridge, compiled_root, source_identity, plan_digest, [noncontiguous]
        )
    assert false_coalescing.value.code == "CAPABILITY_MISMATCH"

    for field, member in (
        ("description_budget", "total_bytes"),
        ("metadata_budget", "total_bytes"),
        ("fresh_sample_or_exact_read_budget", "traffic_total"),
        (None, "weight_payload_bytes"),
        ("expected_metrics", "predicted_total_latency_ns"),
        ("memory_schedule", "description_bytes_peak"),
    ):
        attacked = copy.deepcopy(planned_root["plans"][1])
        plan = attacked["plans"][0]
        if field is None:
            plan[member] = 1
        else:
            plan[field][member] += 1
        _seal(plan, "plan_id")
        _seal(attacked, "catalog_id")
        forged = derive_root(
            cartridge,
            planned_root["plans"][0]["source_root"],
            compiler._compiled_identity_material(planned_root),
            (planned_root["plans"][0], attacked),
        )
        with pytest.raises(CassetteError) as detached:
            verify_hardware_plans(cartridge, forged, source_identity, plan_digest)
        assert detached.value.code == "CAPABILITY_MISMATCH", (field, member)

    excessive = []
    for index in range(128):
        spec = copy.deepcopy(specifications[0])
        spec["plan_name"] = f"metadata-overflow-{index:03d}"
        excessive.append(spec)
    with pytest.raises(CassetteError) as metadata_overflow:
        prepare_hardware_plans(
            cartridge, compiled_root, source_identity, plan_digest, excessive
        )
    assert metadata_overflow.value.code == "CAPACITY_EXCEEDED"
