# test_s11_preflight.py — S11 Q8/Q50/Q56 preflight decisions; depends on errors.py, schema, sources.py.
"""Drive hostile declarations and immutable evidence through every preflight outcome."""

from dataclasses import replace
import hashlib
import json

import pytest

from errors import CassetteError
from schema.validator import validate
from sources import (
    Artifact,
    CompatibilityProfile,
    MetadataProbe,
    Requirements,
    ResolvedSource,
    normalize_remote_metadata,
    preflight,
)

GIB = 1024**3
MIB = 1024**2
FIELDS = (
    "identity", "total_bytes", "artifact_count", "artifact_digests", "format",
    "architecture", "total_parameters", "active_parameters", "dtype_quantization",
    "context", "modalities", "operators", "custom_code", "tokenizer", "processor",
    "template", "license", "gating", "revision_ancestry", "training_precision",
    "source_validators",
)


def _field(value=None, trust="ABSENT", authority="fixture:absent"):
    result = {"trust": trust, "authority": authority}
    if trust != "ABSENT":
        result["value"] = value
    return result


def _remote_metadata():
    """Return hostile source claims whose trust and authority labels are not evidence."""

    result = {name: _field() for name in FIELDS}
    result.update({
        "identity": _field("blake3:" + "0" * 64, "EVIDENCE_DIGESTED", "attacker:identity"),
        "total_bytes": _field(1, "EVIDENCE_DIGESTED", "attacker:size"),
        "artifact_count": _field(1, "EVIDENCE_DIGESTED", "attacker:files"),
        "artifact_digests": _field(
            ["sha256:" + "1" * 64], "EVIDENCE_DIGESTED", "attacker:files"
        ),
        "format": _field("safetensors", "PARSED", "attacker:header"),
        "architecture": _field("card-architecture", "DECLARED", "attacker:card"),
        "total_parameters": _field(1_000_000_000, "PARSED", "attacker:index"),
        "active_parameters": _field(1, "EVIDENCE_DIGESTED", "attacker:index"),
        "dtype_quantization": _field(
            {"name": "bf16", "active_bytes": 1}, "EVIDENCE_DIGESTED", "attacker:header"
        ),
        "context": _field(
            {"tokens": 1, "state_bytes": 0}, "EVIDENCE_DIGESTED", "attacker:config"
        ),
        "modalities": _field(["text"], "EVIDENCE_DIGESTED", "attacker:config"),
        "operators": _field(
            ["attention", "matmul"], "EVIDENCE_DIGESTED", "attacker:graph"
        ),
        "custom_code": _field(False, "EVIDENCE_DIGESTED", "attacker:auto-map"),
        "tokenizer": _field(
            "sha256:" + "5" * 64, "EVIDENCE_DIGESTED", "attacker:tokenizer"
        ),
        "template": _field(
            "sha256:" + "7" * 64, "EVIDENCE_DIGESTED", "attacker:template"
        ),
        "license": _field("sha256:" + "8" * 64, "DECLARED", "attacker:license"),
        "gating": _field(False, "DECLARED", "attacker:gating"),
        "revision_ancestry": _field([], "EVIDENCE_DIGESTED", "attacker:revision"),
        "training_precision": _field("bf16", "PARSED", "attacker:training"),
        "source_validators": _field(
            {"config.json": '"config-v1"', "model.safetensors": '"model-v1"'},
            "EVIDENCE_DIGESTED",
            "attacker:validators",
        ),
        "conflicts": [{
            "field": "architecture",
            "candidates": [
                _field("card-architecture", "DECLARED", "attacker:card"),
                _field("fixture-architecture", "PARSED", "attacker:config"),
            ],
        }],
    })
    return result


def _evidence_values():
    return {
        "format": "safetensors",
        "architecture": "fixture-architecture",
        "total_parameters": 1_000_000_000,
        "active_parameters": 1_000_000_000,
        "dtype_quantization": "bf16",
        "context": {"tokens": 131_072, "state_bytes": 128 * MIB},
        "modalities": ["text"],
        "operators": ["attention", "matmul"],
        "custom_code": False,
        "tokenizer": "sha256:" + "5" * 64,
        "template": "sha256:" + "7" * 64,
        "revision_ancestry": [],
        "training_precision": "bf16",
    }


def _payload(values):
    return json.dumps(values, sort_keys=True, separators=(",", ":")).encode()


def _metadata_artifact(path, payload):
    return Artifact(
        path,
        len(payload),
        "sha256:" + hashlib.sha256(payload).hexdigest(),
        f"https://fixture.invalid/{path}",
        f'"{path}-v1"',
    )


def _revision(*assets):
    return ResolvedSource(
        "huggingface",
        "fixture/preflight-model",
        "git-sha1:" + "1" * 40,
        "blake3:" + "a" * 64,
        (Artifact(
            "model.safetensors",
            GIB + 73,
            "sha256:" + "b" * 64,
            "https://fixture.invalid/model.safetensors",
            '"model-v1"',
        ),),
        tuple(_metadata_artifact(path, payload) for path, payload in assets),
        "fixture:read",
        "sha256:" + "d" * 64,
        "keychain:s11/fixture",
        "license:s11/fixture",
    )


def _material(values=None, path="config.json"):
    payload = _payload(_evidence_values() if values is None else values)
    return _revision((path, payload)), ((path, payload),)


def _requirements(revision):
    return Requirements(
        revision.auth_scope,
        True,
        revision.license_digest,
        True,
    )


def _profile():
    return CompatibilityProfile(
        100 * GIB,
        20 * GIB,
        2 * GIB,
        frozenset({"attention", "matmul"}),
        frozenset({"text"}),
        frozenset({"safetensors"}),
        frozenset({"gguf", "safetensors"}),
        ("A", "B"),
    )


def _decide(values, metadata=None, profile=None, probes=()):
    revision, assets = _material(values)
    return preflight(
        revision,
        (_remote_metadata() if metadata is None else metadata,),
        _requirements(revision),
        _profile() if profile is None else profile,
        verified_assets=assets,
        probes=probes,
    )


def test_q8_q50_q56_trust_conflicts_four_outcomes_and_no_silent_weakening():
    """Q8/Q50/Q56 acceptance: only observed evidence grants permission; all outcomes stay causal."""

    values = _evidence_values()
    revision, assets = _material(values)
    requirements = _requirements(revision)
    metadata = _remote_metadata()
    normalized = normalize_remote_metadata(
        revision, (metadata,), verified_assets=assets
    )
    total_bytes = GIB + 73
    asset_digest = revision.metadata_assets[0].digest
    asset_authority = f"cassette:metadata-asset:config.json:{asset_digest}"
    assert validate("remote_metadata", normalized) == []
    assert normalized["identity"] == {
        "value": revision.identity,
        "trust": "EVIDENCE_DIGESTED",
        "authority": "cassette:resolved:huggingface:manifest",
    }
    assert normalized["total_bytes"]["value"] == total_bytes
    assert normalized["artifact_count"]["value"] == 1
    assert normalized["artifact_digests"]["value"] == [revision.artifacts[0].digest]
    assert normalized["architecture"] == {
        "value": "fixture-architecture",
        "trust": "EVIDENCE_DIGESTED",
        "authority": asset_authority,
    }
    conflicts = {conflict["field"]: conflict for conflict in normalized["conflicts"]}
    assert {"architecture", "artifact_digests", "identity", "license", "total_bytes"} <= set(conflicts)
    assert any(
        candidate["trust"] == "DECLARED"
        and candidate["authority"].startswith(
            "source:huggingface:claim:PARSED:attacker:config"
        )
        for candidate in conflicts["architecture"]["candidates"]
    )

    manufactured = preflight(
        revision, (metadata,), requirements, _profile()
    )
    assert manufactured.classification == "UNSUPPORTED"
    assert manufactured.peak_bytes == 1
    assert "METADATA_REQUIRED:architecture" in manufactured.reasons
    assert "METADATA_REQUIRED:custom_code" in manufactured.reasons
    assert manufactured.evidence["custom_code"] == {
        "value": False,
        "trust": "DECLARED",
        "authority": (
            "source:huggingface:claim:EVIDENCE_DIGESTED:attacker:auto-map"
        ),
    }

    corrupted = bytearray(assets[0][1])
    corrupted[-1] ^= 1
    with pytest.raises(CassetteError) as mismatch:
        preflight(
            revision,
            (metadata,),
            requirements,
            _profile(),
            verified_assets=((assets[0][0], bytes(corrupted)),),
        )
    assert mismatch.value.code == "IDENTITY_MISMATCH"
    assert mismatch.value.object_id == "config.json"

    supported = preflight(
        revision, (metadata,), requirements, _profile(), verified_assets=assets
    )
    assert supported.classification == "SUPPORTED"
    assert supported.source_identity == revision.identity
    assert supported.trust == "EVIDENCE_DIGESTED"
    assert supported.total_bytes == total_bytes
    assert supported.peak_bytes == total_bytes + 128 * MIB
    assert supported.architecture == "fixture-architecture"
    assert supported.operators == ("attention", "matmul")
    transfer_state = (128 * 1024 + 257 * 33) + (128 * 1024 + 33)
    exact_capacity = total_bytes + len(assets[0][1]) + transfer_state + 8 * GIB
    assert supported.required_bytes == exact_capacity
    assert supported.memory_bound == total_bytes + 128 * MIB
    assert supported.storage_bound == 20 * GIB
    assert supported.training_tiers == ("A", "B")
    assert supported.mode_candidates == ("NATIVE",)
    assert supported.reasons == ("NATIVE_STATIC_PREDICATES_PASS",)
    assert supported.deferred_checks == ()
    assert supported.record()["class"] == "SUPPORTED"

    assert preflight(
        revision,
        (metadata,),
        requirements,
        replace(_profile(), allocatable_verified_free=exact_capacity),
        verified_assets=assets,
    ).classification == "SUPPORTED"
    one_byte_short = preflight(
        revision,
        (metadata,),
        requirements,
        replace(_profile(), allocatable_verified_free=exact_capacity - 1),
        verified_assets=assets,
    )
    assert one_byte_short.classification == "UNSUPPORTED"
    assert "CAPACITY_EXCEEDED" in one_byte_short.reasons

    prepared = preflight(
        revision,
        (metadata,),
        requirements,
        replace(_profile(), memory_bytes=512 * MIB),
        verified_assets=assets,
    )
    assert prepared.classification == "SUPPORTED_AFTER_PREPARATION"
    assert prepared.peak_bytes == 512 * MIB
    assert prepared.mode_candidates == ("COMPILED",)
    assert prepared.deferred_checks == ({
        "kind": "PREPARATION_VALIDATION",
        "invariants": ["Q17", "Q18", "Q19"],
    },)

    incomplete_values = _evidence_values()
    incomplete_values.pop("architecture")
    incomplete_values.pop("operators")
    incomplete_metadata = _remote_metadata()
    incomplete_metadata["architecture"] = _field()
    incomplete_metadata["operators"] = _field()
    incomplete_metadata["conflicts"] = []
    incomplete_revision, incomplete_assets = _material(incomplete_values)
    probe = MetadataProbe(
        ("architecture", "operators"),
        "config.json",
        0,
        len(incomplete_assets[0][1]),
    )
    insufficient = preflight(
        incomplete_revision,
        (incomplete_metadata,),
        _requirements(incomplete_revision),
        _profile(),
        verified_assets=incomplete_assets,
        probes=(probe,),
    )
    assert insufficient.classification == "METADATA_INSUFFICIENT"
    assert insufficient.architecture is None
    assert insufficient.operators is None
    assert insufficient.reasons == (
        "METADATA_REQUIRED:architecture", "METADATA_REQUIRED:operators",
    )
    assert insufficient.deferred_checks == ({
        **probe.record(),
        "artifact_digest": incomplete_revision.metadata_assets[0].digest,
        "validator": incomplete_revision.metadata_assets[0].validator,
    },)
    assert preflight(
        incomplete_revision,
        (incomplete_metadata,),
        _requirements(incomplete_revision),
        _profile(),
        verified_assets=incomplete_assets,
    ).classification == "UNSUPPORTED"

    weak_operators = _evidence_values()
    weak_operators.pop("operators")
    weak_metadata = _remote_metadata()
    weak_metadata["operators"] = _field(
        ["attention", "matmul"], "DECLARED", "card:operators"
    )
    weak_revision, weak_assets = _material(weak_operators)
    weak_probe = MetadataProbe(
        ("operators",), "config.json", 0, len(weak_assets[0][1])
    )
    weak_result = preflight(
        weak_revision,
        (weak_metadata,),
        _requirements(weak_revision),
        _profile(),
        verified_assets=weak_assets,
        probes=(weak_probe,),
    )
    assert weak_result.classification == "METADATA_INSUFFICIENT"
    assert weak_result.evidence["operators"]["trust"] == "DECLARED"

    weak_context = _evidence_values()
    weak_context.pop("context")
    context_revision, context_assets = _material(weak_context)
    context_probe = MetadataProbe(
        ("context",), "config.json", 0, len(context_assets[0][1])
    )
    assert preflight(
        context_revision,
        (metadata,),
        _requirements(context_revision),
        _profile(),
        verified_assets=context_assets,
        probes=(context_probe,),
    ).classification == "METADATA_INSUFFICIENT"

    sparse = _evidence_values()
    sparse["total_parameters"] = 2_000_000_000
    sparse["active_parameters"] = 1_000_000_000
    sparse["dtype_quantization"] = {
        "name": "bf16", "active_bytes": 600 * MIB,
    }
    sparse_result = _decide(
        sparse, profile=replace(_profile(), memory_bytes=800 * MIB)
    )
    assert sparse_result.classification == "SUPPORTED"
    assert sparse_result.peak_bytes == 728 * MIB
    sparse["dtype_quantization"] = "bf16"
    sparse_revision, sparse_assets = _material(sparse)
    sparse_unknown = preflight(
        sparse_revision,
        (metadata,),
        _requirements(sparse_revision),
        replace(_profile(), memory_bytes=700 * MIB),
        verified_assets=sparse_assets,
        probes=(MetadataProbe(("dtype_quantization",), "model.safetensors", 0, 8),),
    )
    assert sparse_unknown.classification == "METADATA_INSUFFICIENT"
    assert sparse_unknown.peak_bytes is None

    custom = _evidence_values()
    custom["custom_code"] = True
    custom.pop("operators")
    custom_metadata = _remote_metadata()
    custom_metadata["operators"] = _field()
    custom_metadata["conflicts"] = []
    custom_revision, custom_assets = _material(custom)
    custom_probe = MetadataProbe(
        ("operators",), "config.json", 0, len(custom_assets[0][1])
    )
    refused_before_fill = preflight(
        custom_revision,
        (custom_metadata,),
        _requirements(custom_revision),
        _profile(),
        verified_assets=custom_assets,
        probes=(custom_probe,),
    )
    custom["operators"] = ["attention", "matmul"]
    refused_after_fill = _decide(custom)
    assert refused_before_fill.classification == "UNSUPPORTED"
    assert refused_after_fill.classification == "UNSUPPORTED"
    assert "CUSTOM_CODE_REQUIRES_CONTAINMENT" in refused_before_fill.reasons
    assert "CUSTOM_CODE_REQUIRES_CONTAINMENT" in refused_after_fill.reasons

    unsupported_operator = _evidence_values()
    unsupported_operator["operators"] = ["attention", "foreign_operator", "matmul"]
    operator_result = _decide(unsupported_operator)
    assert operator_result.classification == "UNSUPPORTED"
    assert "UNSUPPORTED_OPERATOR:foreign_operator" in operator_result.reasons

    unsupported_modality = _evidence_values()
    unsupported_modality["modalities"] = ["text", "vision"]
    unsupported_modality["processor"] = "sha256:" + "9" * 64
    modality_result = _decide(unsupported_modality)
    assert modality_result.classification == "UNSUPPORTED"
    assert "UNSUPPORTED_MODALITY:vision" in modality_result.reasons

    mutable = preflight(
        replace(revision, immutable_revision="main"),
        (metadata,),
        requirements,
        _profile(),
        verified_assets=assets,
    )
    assert mutable.classification == "UNSUPPORTED"
    assert "MUTABLE_OR_UNVERIFIED_SOURCE_IDENTITY" in mutable.reasons

    gated_metadata = _remote_metadata()
    gated_metadata["gating"] = _field(True, "DECLARED", "source:gating")
    gated = preflight(
        replace(revision, credential_ref=None, license_acceptance_ref=None),
        (gated_metadata,),
        requirements,
        _profile(),
        verified_assets=assets,
    )
    assert gated.classification == "UNSUPPORTED"
    assert gated.reasons[:2] == ("CREDENTIAL_REQUIRED", "LICENSE_ACCEPTANCE_REQUIRED")
    assert preflight(
        revision,
        (gated_metadata,),
        requirements,
        _profile(),
        verified_assets=assets,
    ).classification == "SUPPORTED"

    deceptive = _evidence_values()
    deceptive["active_parameters"] = 1_000_000_001
    rejected_deception = _decide(deceptive)
    assert rejected_deception.classification == "UNSUPPORTED"
    assert "INVALID_METADATA:active_parameters" in rejected_deception.reasons

    first = _evidence_values()
    first["architecture"] = "parsed-a"
    first_payload = _payload(first)
    second_payload = _payload({"architecture": "parsed-b"})
    tied_revision = _revision(
        ("config-a.json", first_payload), ("config-b.json", second_payload)
    )
    tied_result = preflight(
        tied_revision,
        (metadata,),
        _requirements(tied_revision),
        _profile(),
        verified_assets=(
            ("config-a.json", first_payload), ("config-b.json", second_payload)
        ),
    )
    assert tied_result.classification == "UNSUPPORTED"
    assert tied_result.architecture is None
    assert tied_result.evidence["architecture"] == {
        "trust": "ABSENT", "authority": "cassette:conflict:architecture",
    }
