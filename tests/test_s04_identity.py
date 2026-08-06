# test_s04_identity.py — S04 fixtures for Q1 canonical model identity; depends on errors.py, store.py.
"""S04 proves alias convergence, byte and semantic divergence, and mutable-only rejection."""

import hashlib
from dataclasses import replace

import pytest

from errors import CassetteError
from store import ArtifactIdentity, IdentityTuple, model_identity


def digest(payload: bytes) -> str:
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def resolved_identity() -> IdentityTuple:
    return IdentityTuple(
        source_kind="huggingface",
        locator="moonshotai/Kimi-K3",
        immutable_revision="9f62e4e9fffbd0a83ddd60e1c209d828994b3569",
        artifacts=(
            ArtifactIdentity("model-00002-of-00002.safetensors", 1, digest(b"\x02")),
            ArtifactIdentity("model-00001-of-00002.safetensors", 1, digest(b"\x00")),
        ),
        format_versions=(("safetensors", "1"), ("transformers-config", "4.57")),
        tensor_index_digest=digest(b"tensor-index"),
        config_digest=digest(b"config"),
        architecture="KimiK3ForConditionalGeneration",
        operator_set=("rms_norm", "matmul", "attention"),
        tokenizer_digest=digest(b"tokenizer"),
        processor_digest=digest(b"processor"),
        template_digest=digest(b"template"),
        precision_scheme="bf16",
        license_digest=digest(b"license"),
        parent_ids=(),
        transform_manifest_digest=digest(b"source-import-v1"),
    )


def test_q1_source_aliases_converge_after_resolution():
    """Q1 acceptance: two aliases resolved to one immutable tuple obtain one stable identity."""
    repo_alias = resolved_identity()
    url_alias = replace(
        repo_alias,
        artifacts=tuple(reversed(repo_alias.artifacts)),
        format_versions=tuple(reversed(repo_alias.format_versions)),
        operator_set=tuple(reversed(repo_alias.operator_set)),
    )
    assert model_identity(repo_alias) == model_identity(url_alias)
    assert model_identity(repo_alias) == (
        "sha256:e277badb11047d0d21dd094e225fd078e5fcc046e1d41776c6f244ab01fa1bae"
    )


def test_q1_byte_and_semantic_changes_diverge():
    """Q1 acceptance: tensor byte, tokenizer, template, operator, precision, and ancestry changes diverge."""
    base = resolved_identity()
    tensor_byte_changed = replace(
        base,
        artifacts=(replace(base.artifacts[0], digest=digest(b"\x03")), *base.artifacts[1:]),
    )
    variants = (
        tensor_byte_changed,
        replace(base, tokenizer_digest=digest(b"tokenizeS")),
        replace(base, template_digest=digest(b"templatf")),
        replace(base, operator_set=(*base.operator_set, "vision_encoder")),
        replace(base, precision_scheme="int4-group64"),
        replace(base, parent_ids=("sha256:parent",)),
        replace(base, transform_manifest_digest=digest(b"source-import-v2")),
    )
    base_identity = model_identity(base)
    assert all(model_identity(variant) != base_identity for variant in variants)


def test_q1_mutable_only_and_incomplete_tuples_are_rejected():
    """Q1 acceptance: a mutable-only locator and every absent required tuple member are rejected."""
    base = resolved_identity()
    with pytest.raises(CassetteError) as caught:
        model_identity(replace(base, immutable_revision=""))
    assert caught.value.code == "PROVENANCE_VIOLATION"
    assert caught.value.failed_invariant == "Q1: complete immutable identity tuple required"
    assert "mutable locator" in caught.value.detail

    incomplete = (
        replace(base, source_kind=""), replace(base, locator=""), replace(base, artifacts=()),
        replace(base, format_versions=()), replace(base, tensor_index_digest=""),
        replace(base, config_digest=""), replace(base, architecture=""),
        replace(base, operator_set=()), replace(base, tokenizer_digest=""),
        replace(base, processor_digest=""), replace(base, template_digest=""),
        replace(base, precision_scheme=""), replace(base, license_digest=""),
        replace(base, transform_manifest_digest=""),
    )
    for material in incomplete:
        with pytest.raises(CassetteError) as rejected:
            model_identity(material)
        assert rejected.value.code == "PROVENANCE_VIOLATION"
