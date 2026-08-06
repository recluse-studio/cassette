# test_s04_identity.py — S04 fixtures for Q1 identity and Q32 digest authority; depends on errors.py, store.py, tools/ledger.py.
"""S04 proves the literal Q1 clauses and prevents another product digest authority."""

from dataclasses import replace
from pathlib import Path

import pytest

from errors import CassetteError
from store import ArtifactIdentity, IdentityTuple, canonical_bytes, digest_bytes, model_identity
from tools.ledger import check_identity_authority, top_level_imports


def resolved_identity() -> IdentityTuple:
    return IdentityTuple(
        revision_kind="source",
        source_kind="huggingface",
        source_alias="moonshotai/Kimi-K3@main",
        canonical_locator="moonshotai/Kimi-K3",
        requested_revision="main",
        immutable_revision="git-sha1:9f62e4e9fffbd0a83ddd60e1c209d828994b3569",
        artifacts=(
            ArtifactIdentity("model-00002-of-00002.safetensors", 1, digest_bytes(b"\x02")),
            ArtifactIdentity("model-00001-of-00002.safetensors", 1, digest_bytes(b"\x00")),
        ),
        format_versions=(("safetensors", "1"), ("transformers-config", "4.57")),
        tensor_index_digest=digest_bytes(b"tensor-index"),
        config_digest=digest_bytes(b"config"),
        architecture="KimiK3ForConditionalGeneration",
        operator_set=("rms_norm", "matmul", "attention"),
        tokenizer_digest=digest_bytes(b"tokenizer"),
        processor_digest=digest_bytes(b"processor"),
        template_digest=digest_bytes(b"template"),
        precision_scheme="bf16",
        license_digest=digest_bytes(b"license"),
        parent_ids=(),
        transform_manifest_digest=None,
    )


def test_q1_distinct_source_aliases_converge_after_immutable_resolution():
    """Q1 acceptance: distinct aliases resolved to one canonical source revision obtain one I."""
    repo_alias = resolved_identity()
    url_alias = replace(
        repo_alias,
        source_alias="https://huggingface.co/moonshotai/Kimi-K3/tree/main",
        requested_revision="refs/heads/main",
        artifacts=tuple(reversed(repo_alias.artifacts)),
        format_versions=tuple(reversed(repo_alias.format_versions)),
        operator_set=tuple(reversed(repo_alias.operator_set)),
    )
    assert repo_alias.source_alias != url_alias.source_alias
    assert repo_alias.requested_revision != url_alias.requested_revision
    assert model_identity(repo_alias) == model_identity(url_alias)
    assert model_identity(repo_alias) == (
        "blake3:004434622abf8f7c012a2c2db6ab16ec70ba54aa1f5c6b783b644f64a66c6278"
    )
    assert digest_bytes(b"") == (
        "blake3:af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"
    )
    assert canonical_bytes({"\ufffd": 1, "\U0001f600": 2}).decode() == '{"\U0001f600":2,"\ufffd":1}'


def test_q1_byte_semantic_source_and_ancestry_changes_diverge():
    """Q1 acceptance: every required byte, semantic, source, precision, and ancestry change diverges."""
    base = resolved_identity()
    variants = (
        replace(base, artifacts=(replace(base.artifacts[0], digest=digest_bytes(b"\x03")),
                                 *base.artifacts[1:])),
        replace(base, tokenizer_digest=digest_bytes(b"tokenizeS")),
        replace(base, template_digest=digest_bytes(b"templatf")),
        replace(base, operator_set=(*base.operator_set, "vision_encoder")),
        replace(base, precision_scheme="int4-group64"),
        replace(base, source_kind="ollama"),
        replace(base, canonical_locator="another/model"),
        replace(base, immutable_revision="git-sha1:8f62e4e9fffbd0a83ddd60e1c209d828994b3569"),
    )
    base_identity = model_identity(base)
    assert all(model_identity(variant) != base_identity for variant in variants)

    child = replace(
        base,
        revision_kind="tuned",
        parent_ids=(base_identity,),
        transform_manifest_digest=digest_bytes(b"training-manifest"),
    )
    assert model_identity(child) != base_identity
    assert model_identity(replace(child, parent_ids=(digest_bytes(b"another-parent"),))) != model_identity(child)
    assert model_identity(replace(child, transform_manifest_digest=digest_bytes(b"other-transform"))) != model_identity(child)


def test_q1_mutable_incomplete_unresolved_and_unbound_material_is_rejected():
    """Q1 acceptance: mutable-only, malformed, incomplete, and incorrectly bound revisions mint no I."""
    base = resolved_identity()
    for tag in ("main", "latest", "HEAD", "v1.0", "refs/heads/main"):
        with pytest.raises(CassetteError) as mutable:
            model_identity(replace(base, requested_revision=tag, immutable_revision=None))
        assert mutable.value.code == "IDENTITY_MISMATCH"
        assert "no immutable resolution" in mutable.value.detail
        with pytest.raises(CassetteError):
            model_identity(replace(base, immutable_revision=tag))

    incomplete = (
        replace(base, source_kind=""), replace(base, source_alias=""),
        replace(base, canonical_locator=""),
        replace(base, artifacts=()), replace(base, format_versions=()),
        replace(base, tensor_index_digest=""), replace(base, config_digest=""),
        replace(base, architecture=""), replace(base, operator_set=()),
        replace(base, tokenizer_digest="not-a-digest"), replace(base, processor_digest="x"),
        replace(base, template_digest="sha256:12"), replace(base, precision_scheme=""),
        replace(base, license_digest="blake3:not-hex"),
        replace(base, immutable_revision=base.immutable_revision + "\n"),
        replace(base, architecture=" KimiK3ForConditionalGeneration "),
        replace(base, artifacts=(replace(base.artifacts[0], digest="not-a-digest"),
                                 *base.artifacts[1:])),
    )
    for material in incomplete:
        with pytest.raises(CassetteError) as rejected:
            model_identity(material)
        assert rejected.value.code == "IDENTITY_MISMATCH"

    parent = digest_bytes(b"parent")
    transform = digest_bytes(b"transform")
    unbound = (
        replace(base, parent_ids=(parent,)),
        replace(base, transform_manifest_digest=transform),
        replace(base, revision_kind="tuned"),
        replace(base, revision_kind="tuned", parent_ids=(parent,)),
        replace(base, revision_kind="tuned", transform_manifest_digest=transform),
        replace(base, revision_kind="unknown"),
    )
    for material in unbound:
        with pytest.raises(CassetteError):
            model_identity(material)


def test_no_duplicate_identity_or_transaction_authority(tmp_path):
    """no_duplicate_identity_or_transaction_authority: product digest imports are confined to store.py."""
    authorities = {"blake3", "hashlib", "rfc8785"}
    forbidden_source = tmp_path / "sources.py"
    forbidden_source.write_text("import hashlib, blake3\nimport rfc8785\n", encoding="utf-8")
    imported = top_level_imports(tmp_path, Path("sources.py"))
    assert imported == authorities
    assert check_identity_authority(Path("store.py"), imported) == []
    assert check_identity_authority(Path("sources.py"), imported) == [
        "sources.py: imports ['blake3', 'hashlib', 'rfc8785'] outside store.py "
        "(Q32 identity authority confinement)"
    ]
