# test_s19_compiler.py — F2 fixture for contained streaming compilation, total maps, certificates, resume, and publication guards; depends on broker.py, compiler.py, errors.py, pager.py, store.py, tests/compiler_fixture.py.
"""S19 attacks every authority that can turn hostile model bytes into a callable revision."""

from __future__ import annotations

import ast
import copy
from fractions import Fraction
import inspect
from itertools import combinations, permutations
import os
from pathlib import Path
import sys

import pytest

from broker import AcquisitionContext, CanonicalBroker
import compiler
from compiler import PreparedRevision, plan_revision, prepare_revision, verify_bundle_structure
from compiler_fixture import artifact as compiler_artifact, sharded_artifacts
from errors import CassetteError
from pager import admit_schedule
import pager
from sources import Artifact, ResolvedSource
from store import (
    ArtifactIdentity,
    CapacityCoordinator,
    IdentityTuple,
    PAGE_BYTES,
    canonical_bytes,
    derive_root,
    digest_bytes,
    extent_footprint,
    load_root,
    model_identity,
    measure_extent_footprint,
    page_locations,
    recover_generation,
    stage_conversion_extent,
    verify_root_content,
)

pytestmark = pytest.mark.skipif(sys.platform != "darwin", reason="S19 requires macOS clonefile and F_FULLFSYNC")


def _source(material: IdentityTuple) -> dict:
    return {
        "source_kind": material.source_kind,
        "source_alias": material.source_alias,
        "locator": material.canonical_locator,
        "requested_revision": material.requested_revision,
        "immutable_revision": material.immutable_revision,
        "identity": model_identity(material),
        "artifacts": [
            {"path": item.path, "size": item.size, "digest": item.digest}
            for item in material.artifacts
        ],
        "license_digest": material.license_digest,
    }


def _resolved(source: dict) -> ResolvedSource:
    return ResolvedSource(
        source_kind=source["source_kind"],
        locator=source["locator"],
        immutable_revision=source["immutable_revision"],
        identity=source["identity"],
        artifacts=tuple(
            Artifact(
                path=item["path"],
                size=item["size"],
                digest=item["digest"],
                range_uri=f"fixture://{item['path']}",
                validator="fixture-validator",
            )
            for item in source["artifacts"]
        ),
        metadata_assets=(),
        auth_scope="fixture-public",
        license_digest=source["license_digest"],
        credential_ref=None,
        license_acceptance_ref=None,
    )


def _case(tmp_path: Path, label: str, *, artifact_path: str = "model.safetensors", mutate=None):
    cartridge = tmp_path / label
    incoming = cartridge / "incoming"
    incoming.mkdir(parents=True)
    payload, material, manifest = compiler_artifact(
        "huggingface",
        f"recluse/{label}",
        "git-sha1:" + "a" * 40,
        "blake3:" + "b" * 64,
        artifact_path,
        label=label,
        mutate_manifest=mutate,
    )
    path = incoming / "physical.safetensors"
    path.write_bytes(payload)
    descriptor = os.open(path, os.O_RDWR)
    source = _source(material)
    extents = {
        artifact_path: {
            "fd": descriptor,
            "offset": 0,
            "length": len(payload),
            "operation_id": f"op-{label}",
        }
    }
    return cartridge, path, descriptor, payload, source, extents, manifest


def _derived_material(root: dict, bundle: dict) -> IdentityTuple:
    provenance = root["provenance"]
    record = provenance["identity_material"]
    return IdentityTuple(
        revision_kind="executable",
        source_kind=record["source_kind"],
        source_alias=provenance["source_alias"],
        canonical_locator=record["locator"],
        requested_revision=provenance["requested_revision"],
        immutable_revision=record["immutable_revision"],
        artifacts=tuple(ArtifactIdentity(**item) for item in record["artifacts"]),
        format_versions=tuple(tuple(item) for item in record["format_versions"]),
        tensor_index_digest=record["tensor_index_digest"],
        config_digest=record["config_digest"],
        architecture=record["architecture"],
        operator_set=tuple(record["operator_set"]),
        tokenizer_digest=record["tokenizer_digest"],
        processor_digest=record["processor_digest"],
        template_digest=record["template_digest"],
        precision_scheme=record["precision_scheme"],
        license_digest=record["license_digest"],
        parent_ids=tuple(record["parent_ids"]),
        transform_manifest_digest=digest_bytes(canonical_bytes(bundle)),
    )


def _forge(cartridge: Path, valid_root: dict, bundle: dict) -> str:
    return derive_root(
        cartridge,
        bundle["source_root"],
        _derived_material(valid_root, bundle),
        (bundle,),
    )


def _content_path(cartridge: Path, directory: str, digest: str) -> Path:
    return cartridge / directory / digest.removeprefix("blake3:")


def _exact(real: int | Fraction, imaginary: int | Fraction = 0):
    return (Fraction(real), Fraction(imaginary))


def _oracle_multiply(left, right):
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def _oracle_determinant(matrix):
    size = len(matrix)
    total = _exact(0)
    for order in permutations(range(size)):
        term = _exact(1)
        for row, column in enumerate(order):
            term = _oracle_multiply(term, matrix[row][column])
        inversions = sum(
            order[left] > order[right]
            for left in range(size)
            for right in range(left + 1, size)
        )
        total = (
            total[0] + (-term[0] if inversions % 2 else term[0]),
            total[1] + (-term[1] if inversions % 2 else term[1]),
        )
    return total


def _oracle_rank(matrix):
    row_count = len(matrix)
    column_count = len(matrix[0])
    for size in range(min(row_count, column_count), 0, -1):
        for row_indexes in combinations(range(row_count), size):
            for column_indexes in combinations(range(column_count), size):
                minor = [
                    [matrix[row][column] for column in column_indexes]
                    for row in row_indexes
                ]
                if _oracle_determinant(minor) != _exact(0):
                    return size
    return 0


def _algorithm_shape(function):
    tree = ast.parse(inspect.getsource(function))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            node.name = "_"
            node.returns = None
        elif isinstance(node, ast.arg):
            node.arg = "_"
            node.annotation = None
        elif isinstance(node, ast.Name):
            node.id = "_"
    return ast.dump(tree, include_attributes=False)


def test_q4_q5_q19_q30_q40_q51_q55_q58_q60_q62_streaming_compiler_earns_publication(tmp_path):
    """Q4/Q5/Q19/Q30/Q40/Q51/Q55/Q58/Q60/Q62 acceptance: hostile bytes cannot outrun complete proof."""

    # Q55/Q30: reject every executable-material class and every absent generated tuple before
    # any candidate object exists. The marker proves the template was data, never an instruction.
    marker = tmp_path / "template-executed"

    def auto_map(document):
        document["model"]["auto_map"] = {"AutoModel": "remote.Model"}

    def template(document):
        document["model"]["template_source"] = (
            "{{ cycler.__init__.__globals__.os.system('touch " + str(marker) + "') }}"
        )

    def custom_operator(document):
        row = document["operator_inventory"][0]
        row.update(case_id="custom.fused", operator="custom_fused")
        document["evidence"]["execution_contract"]["operations"][0]["operator_case_id"] = "custom.fused"

    def absent_tuple(document):
        document["operator_inventory"][0]["input_shapes"] = [[7, 7], [7, 7]]

    hostile = (
        ("pickle", "model.pkl", None, "CONTAINMENT_REJECTED"),
        ("native", "model.dylib", None, "CONTAINMENT_REJECTED"),
        ("traversal", "../model.safetensors", None, "CONTAINMENT_REJECTED"),
        ("auto-map", "model.safetensors", auto_map, "CONTAINMENT_REJECTED"),
        ("template", "model.safetensors", template, "CONTAINMENT_REJECTED"),
        ("custom-op", "model.safetensors", custom_operator, "CONTAINMENT_REJECTED"),
        ("absent-tuple", "model.safetensors", absent_tuple, "UNSUPPORTED_OPERATOR"),
    )
    for label, artifact_path, mutate, code in hostile:
        cartridge, _, descriptor, _, source, extents, _ = _case(
            tmp_path, f"hostile-{label}", artifact_path=artifact_path, mutate=mutate
        )
        try:
            with pytest.raises(CassetteError) as refused:
                plan_revision(source, extents, cartridge)
            assert refused.value.code == code
            assert not (cartridge / "roots").exists()
            assert not (cartridge / "segments").exists()
        finally:
            os.close(descriptor)
    assert not marker.exists()

    compiler_tree = ast.parse(Path(compiler.__file__).read_text())
    forbidden_calls = {
        node.func.id
        for node in ast.walk(compiler_tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        and node.func.id in {"eval", "exec", "compile", "__import__"}
    }
    forbidden_imports = {
        alias.name.split(".")[0]
        for node in ast.walk(compiler_tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
        if alias.name.split(".")[0] in {"ctypes", "importlib", "pickle", "socket", "subprocess", "urllib"}
    }
    assert forbidden_calls == set()
    assert forbidden_imports == set()
    assert tuple(AcquisitionContext.__dataclass_fields__) == (
        "adapter", "capacity_controller", "transfers", "cartridge",
    )

    # Q19: compiler derivation and pager admission use different elimination, determinant,
    # contraction, and loss procedures. Literal answers and a combinatorial minors oracle judge
    # both authorities without deriving the expected result through either production path.
    for helper_name in ("_multiply", "_divide", "_rank", "_determinant", "_inner", "_witness_loss"):
        assert _algorithm_shape(getattr(compiler, helper_name)) != _algorithm_shape(
            getattr(pager, helper_name)
        )
    arithmetic_cases = (
        [[_exact(0), _exact(0), _exact(0)], [_exact(0), _exact(0), _exact(0)]],
        [[_exact(1), _exact(2), _exact(3)], [_exact(2), _exact(4), _exact(6)]],
        [[_exact(0), _exact(1), _exact(2)], [_exact(1), _exact(0), _exact(3)], [_exact(4), _exact(5), _exact(6)]],
        [[_exact(1), _exact(0), _exact(1)], [_exact(0), _exact(1), _exact(1)]],
        [[_exact(1, 1), _exact(2)], [_exact(0, -1), _exact(3, 2)]],
    )
    for matrix in arithmetic_cases:
        expected_rank = _oracle_rank(matrix)
        assert compiler._rank(matrix) == expected_rank
        assert pager._rank(matrix) == expected_rank
        if len(matrix) == len(matrix[0]):
            expected_determinant = _oracle_determinant(matrix)
            assert compiler._determinant(matrix) == expected_determinant
            assert pager._determinant(matrix) == expected_determinant

    left = [_exact(1, 1), _exact(2)]
    right = [_exact(3, -1), _exact(1, 2)]
    metric = [[_exact(2), _exact(0)], [_exact(0), _exact(3)]]
    assert compiler._inner(left, metric, right) == _exact(10, 4)
    assert pager._inner(left, metric, right) == _exact(10, 4)
    target = [_exact(1), _exact(2)]
    atom = [_exact(1), _exact(1)]
    assert compiler._witness_loss(target, atom, metric, "literal-witness") == Fraction(6, 5)
    assert pager._witness_loss(target, atom, metric, "literal-witness") == Fraction(6, 5)

    # Q19: certificate serialization preserves an exact loss beyond float precision.
    assert compiler._number(Fraction(401, 100300), "exact-loss", "witness loss") == "401/100300"
    assert compiler._number(Fraction(1, 4), "exact-loss", "witness loss") == 0.25
    assert compiler._number(Fraction(2**53 + 1), "exact-loss", "witness loss") == "9007199254740993/1"
    for outside_domain in (Fraction(-1), Fraction(10**301), Fraction(1, 10**130 + 1)):
        with pytest.raises(CassetteError) as scalar_refused:
            compiler._number(outside_domain, "exact-loss", "witness loss")
        assert scalar_refused.value.code == "CAPABILITY_MISMATCH"

    def rational_witness(document):
        document["eta_rep"] = 1.0
        document["evidence"]["observation_contract"]["confidence"] = "0.95000000000000000001"
        atom = document["evidence"]["atoms"][0]
        atom["matrix"] = [[1, 0], [0, 4]]
        atom["description"]["reconstruction"] = [[1, 0], [0, 4]]
        atom["description"]["estimator_calibration"]["atom_norm_squared"] = "17"

    rational_cartridge, _, rational_fd, _, rational_source, rational_extents, _ = _case(
        tmp_path, "rational-witness", mutate=rational_witness
    )
    try:
        rational_plan = plan_revision(rational_source, rational_extents, rational_cartridge)
        rational_prepared = prepare_revision(
            rational_source, rational_extents, rational_cartridge, rational_plan,
            capacity_coordinator=CapacityCoordinator(rational_cartridge), operation_id="s19-rational",
        )
        rational_bundle = load_root(rational_cartridge, rational_prepared.candidate_root)["plans"][0]
        assert rational_bundle["certificate"]["atoms"][0]["witness_losses"][0]["loss"] == "9/17"
        assert Fraction(rational_bundle["certificate"]["observation_contract"]["confidence"]) == Fraction("0.95000000000000000001")
        admit_schedule(
            rational_bundle["execution_plan"], rational_bundle["certificate"],
            rational_bundle["evidence"], rational_bundle["profile"],
        )
    finally:
        os.close(rational_fd)

    indefinite_metric = [[_exact(1), _exact(0)], [_exact(0), _exact(-1)]]
    for witness_loss in (compiler._witness_loss, pager._witness_loss):
        with pytest.raises(CassetteError) as impossible_loss:
            witness_loss(
                [_exact(1), _exact(0)],
                [_exact(2), _exact(1)],
                indefinite_metric,
                "impossible-witness",
            )
        assert impossible_loss.value.code == "CAPABILITY_MISMATCH"

    # Q4: the production extent primitive must execute identity, shrink, and grow without a
    # second complete checkpoint. A corrupt uncommitted grow extent must resume to exact bytes.
    conversion_cartridge = tmp_path / "q4-conversions"
    conversion_cartridge.mkdir()
    conversion_source = conversion_cartridge / "source.bin"
    conversion_bytes = bytes(range(251)) * ((PAGE_BYTES + 8191) // 251 + 1)
    conversion_bytes = conversion_bytes[: PAGE_BYTES + 8191]
    conversion_source.write_bytes(conversion_bytes)
    conversion_fd = os.open(conversion_source, os.O_RDONLY)
    try:
        conversion_cases = (
            ("identity", conversion_bytes, ()),
            ("shrink", conversion_bytes[:-8191], ()),
            (
                "grow",
                conversion_bytes + b"G" * PAGE_BYTES + b"tail-growth",
                (b"G" * PAGE_BYTES, b"tail-growth"),
            ),
        )
        for mode, target_bytes, growth in conversion_cases:
            target_digest = digest_bytes(target_bytes)
            if mode == "grow":
                segment_directory = conversion_cartridge / "segments"
                segment_directory.mkdir(exist_ok=True)
                pending = segment_directory / f".{target_digest.removeprefix('blake3:')}.pending"
                pending.write_bytes(b"interrupted-grow")
            target_path = stage_conversion_extent(
                conversion_fd,
                conversion_cartridge,
                len(target_bytes),
                target_digest,
                f"q4-{mode}",
                growth,
            )
            target_fd = os.open(target_path, os.O_RDONLY)
            try:
                footprint = measure_extent_footprint(
                    (conversion_fd,), (target_fd,), f"q4-{mode}"
                )
            finally:
                os.close(target_fd)
            assert target_path.read_bytes() == target_bytes
            assert footprint["source_extent_bytes"] == len(conversion_bytes)
            assert footprint["target_extent_bytes"] == len(target_bytes)
            assert footprint["allocated_peak_bytes"] <= (
                max(len(conversion_bytes), len(target_bytes)) + PAGE_BYTES
            )
            assert stage_conversion_extent(
                conversion_fd,
                conversion_cartridge,
                len(target_bytes),
                target_digest,
                f"q4-{mode}-resume",
                growth,
            ) == target_path
    finally:
        os.close(conversion_fd)

    # Q58: a second valid artifact makes tensor-to-container assignment observable. Swapping or
    # duplicating that preimage must disagree with the Q1 tensor-index digest bound into the root.
    sharded_cartridge = tmp_path / "sharded-map"
    sharded_incoming = sharded_cartridge / "incoming"
    sharded_incoming.mkdir(parents=True)
    shard_names = ("a.safetensors", "b.safetensors")
    shard_payloads, shard_material, _ = sharded_artifacts(
        "huggingface",
        "recluse/sharded-map",
        "git-sha1:" + "c" * 40,
        "blake3:" + "d" * 64,
        shard_names,
        label="sharded-map",
    )
    shard_fds = {}
    try:
        shard_extents = {}
        for name in shard_names:
            local_path = sharded_incoming / name
            local_path.write_bytes(shard_payloads[name])
            shard_fds[name] = os.open(local_path, os.O_RDWR)
            shard_extents[name] = {
                "fd": shard_fds[name],
                "offset": 0,
                "length": len(shard_payloads[name]),
                "operation_id": "op-sharded-map",
            }
        shard_source = _source(shard_material)
        shard_plan = plan_revision(shard_source, shard_extents, sharded_cartridge)
        shard_prepared = prepare_revision(
            shard_source, shard_extents, sharded_cartridge, shard_plan,
            capacity_coordinator=CapacityCoordinator(sharded_cartridge), operation_id="s19-review",
        )
        shard_root = load_root(sharded_cartridge, shard_prepared.candidate_root)
        shard_bundle = shard_root["plans"][0]
        swapped = copy.deepcopy(shard_bundle)
        first, second = swapped["tensor_inventory"]
        first["artifact_path"], second["artifact_path"] = (
            second["artifact_path"], first["artifact_path"]
        )
        duplicated_inventory = copy.deepcopy(shard_bundle)
        duplicated_inventory["tensor_inventory"].append(
            copy.deepcopy(duplicated_inventory["tensor_inventory"][0])
        )
        for label, attacked in (("swapped", swapped), ("duplicated", duplicated_inventory)):
            attacked_root = _forge(sharded_cartridge, shard_root, attacked)
            with pytest.raises(CassetteError) as refused:
                verify_bundle_structure(
                    sharded_cartridge,
                    attacked_root,
                    shard_source["identity"],
                    shard_plan,
                    {name: row["fd"] for name, row in shard_extents.items()},
                )
            assert refused.value.code == "CAPABILITY_MISMATCH", label
            assert recover_generation(sharded_cartridge) is None
    finally:
        for descriptor in shard_fds.values():
            os.close(descriptor)

    # Q51: planning does not authorize completed extents. One changed payload byte must fail on
    # the same read used for page adoption, before a root or generation can exist.
    changed_cartridge, changed_path, changed_fd, changed_payload, changed_source, changed_extents, _ = _case(
        tmp_path, "changed-completed-extent"
    )
    try:
        changed_plan = plan_revision(changed_source, changed_extents, changed_cartridge)
        os.pwrite(changed_fd, bytes([changed_payload[-1] ^ 1]), len(changed_payload) - 1)
        with pytest.raises(CassetteError) as changed:
            prepare_revision(changed_source, changed_extents, changed_cartridge, changed_plan, capacity_coordinator=CapacityCoordinator(changed_cartridge), operation_id="s19-review")
        assert changed.value.code == "SOURCE_REVISION_CHANGED"
        assert recover_generation(changed_cartridge) is None
        assert not (changed_cartridge / "roots").exists()
        os.pwrite(changed_fd, changed_payload[-1:], len(changed_payload) - 1)
    finally:
        os.close(changed_fd)

    # Q4/Q19/Q40/Q58/Q62: the valid case derives its target from tensor bytes, accounts every
    # contribution, binds every proof object, and verifies every page before publication.
    cartridge, source_path, descriptor, valid_payload, source, extents, manifest = _case(tmp_path, "valid")
    try:
        plan_digest = plan_revision(source, extents, cartridge)
        retained_source_path = source_path.with_name("descriptor-bound.safetensors")
        source_path.rename(retained_source_path)
        source_path.write_bytes(b"P" * len(valid_payload))
        prepared = prepare_revision(source, extents, cartridge, plan_digest, capacity_coordinator=CapacityCoordinator(cartridge), operation_id="s19-review")
        root = load_root(cartridge, prepared.candidate_root)
        plan, certificate, evidence, profile, compiled_identity = verify_bundle_structure(
            cartridge,
            prepared.candidate_root,
            source["identity"],
            plan_digest,
            {name: row["fd"] for name, row in extents.items()},
        )
        schedule = admit_schedule(plan, certificate, evidence, profile)
        assert compiled_identity == root["identity"] != source["identity"]
        assert certificate["target"]["target_digest"] == digest_bytes(canonical_bytes({
            "field": "REAL",
            "shape": [2, 2],
            "values": [
                [["1", "0"], ["0", "0"]],
                [["0", "0"], ["1", "0"]],
            ],
        }))
        assert schedule.steps[0].atom_id == "atom.identity"
        assert recover_generation(cartridge) is None
        verify_root_content(cartridge, prepared.candidate_root)

        bundle = root["plans"][0]
        contribution = bundle["contribution_map"]
        assert contribution["totals"] == {
            "tensor_count": 1,
            "element_count": 4,
            "byte_count": 16,
            "source_artifact_bytes": source["artifacts"][0]["size"],
            "container_overhead_bytes": source["artifacts"][0]["size"] - 16,
            "semantic_asset_count": 3,
            "operator_count": 1,
        }
        assert contribution["tensors"][0]["atom_relations"]
        assert contribution["certificate_id"] == certificate["certificate_id"]

        # Q5/Q19/Q62: a structurally valid root can still carry a false mathematical claim.
        # Source binding and broker verification must refuse the claim before publication.
        false_certificate = copy.deepcopy(bundle)
        false_certificate["certificate"]["condition_metrics"][0]["metric_digest"] = digest_bytes(
            b"schema-valid but mathematically false metric"
        )
        false_root = _forge(cartridge, root, false_certificate)
        with pytest.raises(CassetteError) as source_mismatch:
            verify_bundle_structure(cartridge, false_root, source["identity"], plan_digest)
        assert source_mismatch.value.code == "CAPABILITY_MISMATCH"
        with pytest.raises(CassetteError) as false_claim:
            CanonicalBroker._verify_prepared(
                "op-" + "f" * 64,
                cartridge,
                _resolved(source),
                plan_digest,
                PreparedRevision(
                    prepared.source_identity,
                    prepared.verified_artifacts,
                    prepared.plan_digest,
                    false_root,
                ),
                extents,
            )
        assert false_claim.value.code == "CAPABILITY_MISMATCH"
        assert recover_generation(cartridge) is None

        source_root_digest = bundle["source_root"]
        source_location = page_locations(cartridge, source_root_digest)[0]
        segment_path = _content_path(cartridge, "segments", source_location.segment_id)
        source_stat = retained_source_path.stat()
        segment_stat = segment_path.stat()
        assert source_stat.st_dev == segment_stat.st_dev
        assert source_stat.st_ino != segment_stat.st_ino
        assert source_stat.st_blocks == segment_stat.st_blocks
        metrics = bundle["extent_metrics"]
        footprint = extent_footprint(
            cartridge,
            source_root_digest,
            {name: row["fd"] for name, row in extents.items()},
        )
        assert metrics["parameter_storage"] == "FCLONEFILEAT_VERIFIED_EXTENTS"
        assert metrics["physical_measurement"] == "DARWIN_F_LOG2PHYS_EXT"
        assert metrics["observed_within_declared_peak"] is True
        assert footprint["shared_allocated_bytes"] > 0
        assert footprint["allocated_peak_bytes"] == (
            footprint["source_allocated_bytes"]
            + footprint["target_allocated_bytes"]
            - footprint["shared_allocated_bytes"]
        )
        assert metrics["declared_peak_bytes"] == (
            max(metrics["source_extent_bytes"], metrics["target_extent_bytes"])
            + metrics["window_bytes"]
            + metrics["journal_bytes"]
            + metrics["integrity_bytes"]
            + metrics["rollback_delta_bytes"]
            + metrics["precision_bytes"]
            + metrics["reserve_bytes"]
        )
        assert (
            footprint["allocated_peak_bytes"] + metrics["integrity_bytes"]
            <= metrics["declared_peak_bytes"]
        )

        # Q58 mutations are valid immutable roots with invalid semantics. Each must fail before
        # activation, so root integrity cannot be mistaken for a complete contribution proof.
        attacks = {}
        removed = copy.deepcopy(bundle)
        removed["contribution_map"]["tensors"] = []
        attacks["omitted"] = removed
        duplicated = copy.deepcopy(bundle)
        duplicated["contribution_map"]["tensors"].append(
            copy.deepcopy(duplicated["contribution_map"]["tensors"][0])
        )
        attacks["duplicated"] = duplicated
        mismapped = copy.deepcopy(bundle)
        mismapped["contribution_map"]["tensors"][0]["executable_tensor"] = "foreign.weight"
        attacks["mis-mapped"] = mismapped
        unreachable = copy.deepcopy(bundle)
        unreachable["contribution_map"]["tensors"][0]["atom_relations"] = []
        attacks["unreachable"] = unreachable
        detached = copy.deepcopy(bundle)
        detached["certificate"]["atoms"][0]["description"]["residual_relation_digest"] = digest_bytes(b"detached")
        attacks["detached"] = detached
        missing_asset = copy.deepcopy(bundle)
        missing_asset["contribution_map"]["semantic_assets"].pop()
        attacks["missing-semantic-asset"] = missing_asset
        missing_operator = copy.deepcopy(bundle)
        missing_operator["contribution_map"]["operators"].pop()
        attacks["missing-operator"] = missing_operator
        for label, attacked_bundle in attacks.items():
            attacked_root = _forge(cartridge, root, attacked_bundle)
            with pytest.raises(CassetteError) as refused:
                verify_bundle_structure(cartridge, attacked_root, source["identity"], plan_digest)
            assert refused.value.code in {"CAPABILITY_MISMATCH", "ROOT_INVALID"}, label
            assert recover_generation(cartridge) is None

        # Q62 candidate guard: page, index, and root damage are each detected before generation.
        segment_bytes = segment_path.read_bytes()
        segment_path.chmod(0o600)
        segment_path.write_bytes(bytes([segment_bytes[0] ^ 1]) + segment_bytes[1:])
        with pytest.raises(CassetteError) as corrupt_page:
            verify_root_content(cartridge, prepared.candidate_root)
        assert corrupt_page.value.code == "PAGE_CORRUPT"
        segment_path.write_bytes(segment_bytes)
        segment_path.chmod(0o400)

        index_path = _content_path(cartridge, "indexes", prepared.candidate_root)
        index_bytes = index_path.read_bytes()
        index_path.write_bytes(index_bytes[:-1])
        with pytest.raises(CassetteError) as corrupt_index:
            load_root(cartridge, prepared.candidate_root)
        assert corrupt_index.value.code == "ROOT_INVALID"
        index_path.write_bytes(index_bytes)

        root_path = _content_path(cartridge, "roots", prepared.candidate_root)
        root_bytes = root_path.read_bytes()
        root_path.write_bytes(root_bytes[:-1])
        with pytest.raises(CassetteError) as corrupt_root:
            load_root(cartridge, prepared.candidate_root)
        assert corrupt_root.value.code == "ROOT_INVALID"
        root_path.write_bytes(root_bytes)

        # Q60/Q62: corrupt immutable metadata must be refused. Missing uncommitted metadata
        # and interrupted temporary writes can be reconstructed from the verified source.
        source_root_path = _content_path(cartridge, "roots", source_root_digest)
        source_index_path = _content_path(cartridge, "indexes", source_root_digest)
        resume_targets = (
            (root_path, root_bytes),
            (index_path, index_bytes),
            (source_root_path, source_root_path.read_bytes()),
            (source_index_path, source_index_path.read_bytes()),
        )
        for path, payload in resume_targets:
            corrupt_payload = payload[: max(1, len(payload) // 2)]
            path.write_bytes(corrupt_payload)
            with pytest.raises(CassetteError) as corrupt_resume:
                prepare_revision(source, extents, cartridge, plan_digest, capacity_coordinator=CapacityCoordinator(cartridge), operation_id="s19-review")
            assert corrupt_resume.value.code == "ROOT_INVALID"
            assert path.read_bytes() == corrupt_payload
            assert recover_generation(cartridge) is None
            path.unlink()
            resumed = prepare_revision(source, extents, cartridge, plan_digest, capacity_coordinator=CapacityCoordinator(cartridge), operation_id="s19-review")
            assert resumed == prepared
            assert path.read_bytes() == payload
        segment_path.unlink()
        resumed = prepare_revision(source, extents, cartridge, plan_digest, capacity_coordinator=CapacityCoordinator(cartridge), operation_id="s19-review")
        assert resumed == prepared
        assert segment_path.read_bytes() == segment_bytes
        pending = root_path.with_name(f".{root_path.name}.pending")
        root_path.unlink()
        pending.write_bytes(b"interrupted temporary")
        assert prepare_revision(source, extents, cartridge, plan_digest, capacity_coordinator=CapacityCoordinator(cartridge), operation_id="s19-review") == prepared
        assert not pending.exists()
        assert recover_generation(cartridge) is None

        os.pwrite(descriptor, b"X", len(valid_payload) - 1)
        assert segment_path.read_bytes() == segment_bytes
        verify_root_content(cartridge, prepared.candidate_root)

        secret = b"credential-that-must-never-reach-the-compiler"
        assert not any(secret in path.read_bytes() for path in cartridge.rglob("*") if path.is_file())
    finally:
        os.close(descriptor)


def test_q1_q19_q60_initial_proof_binds_source_values_and_composes_risk(tmp_path):
    """Q1/Q19/Q60: initial proof binds verified source values and cannot assert an unproved joint risk."""
    cartridge, _, descriptor, _, source, extents, manifest = _case(tmp_path, "source-proof")
    try:
        plan_digest = plan_revision(source, extents, cartridge)
        prepared = prepare_revision(
            source, extents, cartridge, plan_digest,
            capacity_coordinator=CapacityCoordinator(cartridge), operation_id="s19-source-proof",
        )
        root = load_root(cartridge, prepared.candidate_root)
        plan, certificate, evidence, profile, _ = verify_bundle_structure(
            cartridge, prepared.candidate_root, source["identity"], plan_digest,
        )
        admit_schedule(plan, certificate, evidence, profile)
        bundle = root["plans"][0]
        # Q1/Q19/Q58/Q60: a self-consistent proof for different values must fail source binding.
        substituted = copy.deepcopy(bundle)
        substituted["evidence"]["target"]["source_values"] = [2, 0, 0, 1]
        atom = substituted["evidence"]["atoms"][0]
        atom["matrix"] = [[2, 0], [0, 1]]
        atom["description"]["reconstruction"] = [[2, 0], [0, 1]]
        atom["description"]["estimator_calibration"]["atom_norm_squared"] = "5"
        substituted["certificate"] = compiler._certificate(
            substituted["evidence"], manifest["eta_rep"], manifest["rank_budget"], manifest["operation_bounds"]
        )
        source_root = load_root(cartridge, bundle["source_root"])
        substituted["contribution_map"] = compiler._contribution_map(
            source_root, bundle["source_root"], substituted["certificate"],
            manifest["target_tensor"], bundle["operator_inventory"], bundle["tensor_inventory"],
        )
        substituted["execution_plan"] = compiler._execution_plan(
            source_root, bundle["source_root"], substituted["certificate"], profile,
            substituted["contribution_map"], bundle["operator_inventory"], manifest["prior_mode_failures"], cartridge,
        )
        proof = {key: substituted[key] for key in (
            "operator_inventory", "tensor_inventory", "evidence", "certificate", "profile", "contribution_map", "execution_plan",
        )}
        substituted["extent_metrics"] = compiler._extent_metrics(
            source_root, proof, sum(location.length for location in page_locations(cartridge, bundle["source_root"]))
        )
        admit_schedule(substituted["execution_plan"], substituted["certificate"], substituted["evidence"], profile)
        substituted_root = _forge(cartridge, root, substituted)
        with pytest.raises(CassetteError) as substituted_source:
            verify_bundle_structure(cartridge, substituted_root, source["identity"], plan_digest)
        assert substituted_source.value.code == "CAPABILITY_MISMATCH"

        # Q19: one declared number cannot prove dependence among three repeated events.
        for bound, accepted in (("1/4", False), ("3/4", True)):
            risk_evidence = copy.deepcopy(evidence)
            risk_evidence["trace_contract"]["steps"] = [
                {**risk_evidence["trace_contract"]["steps"][0], "step": step} for step in range(3)
            ]
            risk_evidence["execution_contract"]["risk_composition"] = {
                "kind": "DECLARED_DEPENDENCE", "proof": {"total_bound": bound},
            }
            bounds = [{**row, "delta_exec": "1/4"} for row in manifest["operation_bounds"]]
            if accepted:
                derived = compiler._certificate(risk_evidence, manifest["eta_rep"], manifest["rank_budget"], bounds)
                assert derived["resources"]["delta_exec_total"] == 0.75
            else:
                with pytest.raises(CassetteError) as unproved:
                    compiler._certificate(risk_evidence, manifest["eta_rep"], manifest["rank_budget"], bounds)
                assert unproved.value.code == "CAPABILITY_MISMATCH"

    finally:
        os.close(descriptor)
