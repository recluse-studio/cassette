# test_s11_preflight.py — S11 Q8/Q50/Q56 preflight decisions; depends on schema, sources.
"""Drive contradictory immutable evidence through every declared preflight outcome."""

from dataclasses import replace

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


def _metadata():
    result = {name: _field() for name in FIELDS}
    result.update({
        "identity": _field("blake3:" + "0" * 64, "DECLARED", "card:identity"),
        "total_bytes": _field(1, "EVIDENCE_DIGESTED", "manifest:deceptive-size"),
        "artifact_count": _field(1, "DECLARED", "card:files"),
        "artifact_digests": _field(["sha256:" + "1" * 64], "DECLARED", "card:files"),
        "format": _field("safetensors", "PARSED", "header:model"),
        "architecture": _field("card-architecture", "DECLARED", "card:model"),
        "total_parameters": _field(1_000_000_000, "PARSED", "index:model"),
        "active_parameters": _field(1_000_000_000, "PARSED", "index:model"),
        "dtype_quantization": _field("bf16", "PARSED", "header:model"),
        "context": _field(
            {"tokens": 131_072, "state_bytes": 128 * MIB},
            "PARSED",
            "config:model",
        ),
        "modalities": _field(["text"], "PARSED", "config:model"),
        "operators": _field(["attention", "matmul"], "PARSED", "graph:model"),
        "custom_code": _field(False, "PARSED", "config:model"),
        "tokenizer": _field("sha256:" + "5" * 64, "EVIDENCE_DIGESTED", "manifest:tokenizer"),
        "template": _field("sha256:" + "7" * 64, "EVIDENCE_DIGESTED", "manifest:template"),
        "license": _field("sha256:" + "8" * 64, "DECLARED", "card:license"),
        "gating": _field(False, "DECLARED", "source:gating"),
        "revision_ancestry": _field([], "EVIDENCE_DIGESTED", "manifest:revision"),
        "training_precision": _field("bf16", "PARSED", "config:training"),
        "source_validators": _field(
            {"config.json": '"config-v1"', "model.safetensors": '"model-v1"'},
            "EVIDENCE_DIGESTED",
            "manifest:validators",
        ),
        "conflicts": [{
            "field": "architecture",
            "candidates": [
                _field("card-architecture", "DECLARED", "card:model"),
                _field("fixture-architecture", "PARSED", "config:model"),
            ],
        }],
    })
    return result


def _revision():
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
        (Artifact(
            "config.json",
            101,
            "sha256:" + "c" * 64,
            "https://fixture.invalid/config.json",
            '"config-v1"',
        ),),
        "fixture:read",
        "sha256:" + "d" * 64,
        "keychain:s11/fixture",
        "license:s11/fixture",
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


def test_q8_q50_q56_trust_conflicts_four_outcomes_and_no_silent_weakening():
    """Q8/Q50/Q56 acceptance: exact trust wins, conflicts survive, and all four outcomes are causal."""

    revision = _revision()
    requirements = Requirements(
        revision.auth_scope,
        True,
        revision.license_digest,
        True,
    )
    metadata = _metadata()
    normalized = normalize_remote_metadata(revision, (metadata,))
    total_bytes = GIB + 73
    assert validate("remote_metadata", normalized) == []
    assert normalized["identity"] == {
        "value": revision.identity,
        "trust": "EVIDENCE_DIGESTED",
        "authority": "cassette:resolved:huggingface:manifest",
    }
    assert normalized["total_bytes"]["value"] == total_bytes
    assert normalized["artifact_count"]["value"] == 1
    assert normalized["artifact_digests"]["value"] == [
        revision.artifacts[0].digest,
    ]
    assert normalized["architecture"] == _field(
        "fixture-architecture", "PARSED", "config:model"
    )
    conflicts = {conflict["field"]: conflict for conflict in normalized["conflicts"]}
    assert {"architecture", "artifact_digests", "identity", "license", "total_bytes"} <= set(conflicts)
    assert {candidate["value"] for candidate in conflicts["architecture"]["candidates"]} == {
        "card-architecture", "fixture-architecture",
    }

    supported = preflight(revision, (metadata,), requirements, _profile())
    assert supported.classification == "SUPPORTED"
    assert supported.source_identity == revision.identity
    assert supported.trust == "EVIDENCE_DIGESTED"
    assert supported.total_bytes == total_bytes
    assert supported.peak_bytes == total_bytes + 128 * MIB
    assert supported.architecture == "fixture-architecture"
    assert supported.operators == ("attention", "matmul")
    transfer_state = (128 * 1024 + 257 * 33) + (128 * 1024 + 33)
    assert supported.required_bytes == total_bytes + 101 + transfer_state + 8 * GIB
    assert supported.memory_bound == total_bytes + 128 * MIB
    assert supported.storage_bound == 20 * GIB
    assert supported.training_tiers == ("A", "B")
    assert supported.mode_candidates == ("NATIVE",)
    assert supported.reasons == ("NATIVE_STATIC_PREDICATES_PASS",)
    assert supported.deferred_checks == ()
    assert supported.record()["class"] == "SUPPORTED"

    exact_capacity = total_bytes + 101 + transfer_state + 8 * GIB
    assert preflight(
        revision,
        (metadata,),
        requirements,
        replace(_profile(), allocatable_verified_free=exact_capacity),
    ).classification == "SUPPORTED"
    one_byte_short = preflight(
        revision,
        (metadata,),
        requirements,
        replace(_profile(), allocatable_verified_free=exact_capacity - 1),
    )
    assert one_byte_short.classification == "UNSUPPORTED"
    assert "CAPACITY_EXCEEDED" in one_byte_short.reasons

    prepared = preflight(
        revision,
        (metadata,),
        requirements,
        replace(_profile(), memory_bytes=512 * 1024**2),
    )
    assert prepared.classification == "SUPPORTED_AFTER_PREPARATION"
    assert prepared.peak_bytes == 512 * MIB
    assert prepared.mode_candidates == ("COMPILED",)
    assert prepared.deferred_checks == ({
        "kind": "PREPARATION_VALIDATION",
        "invariants": ["Q17", "Q18", "Q19"],
    },)

    incomplete = _metadata()
    incomplete["architecture"] = _field()
    incomplete["operators"] = _field()
    incomplete["conflicts"] = []
    probe = MetadataProbe(("architecture", "operators"), "config.json", 0, 101)
    insufficient = preflight(
        revision,
        (incomplete,),
        requirements,
        _profile(),
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
        "artifact_digest": revision.metadata_assets[0].digest,
        "validator": revision.metadata_assets[0].validator,
    },)
    undecidable = preflight(revision, (incomplete,), requirements, _profile())
    assert undecidable.classification == "UNSUPPORTED"
    assert "UNDECIDABLE_METADATA:architecture" in undecidable.reasons
    assert "UNDECIDABLE_METADATA:operators" in undecidable.reasons

    weak = _metadata()
    weak["operators"] = _field(
        ["attention", "matmul"], "DECLARED", "card:operators"
    )
    weak_result = preflight(
        revision,
        (weak,),
        requirements,
        _profile(),
        probes=(MetadataProbe(("operators",), "config.json", 0, 101),),
    )
    assert weak_result.classification == "METADATA_INSUFFICIENT"
    assert weak_result.operators == ("attention", "matmul")
    assert weak_result.evidence["operators"]["trust"] == "DECLARED"

    weak_context = _metadata()
    weak_context["context"] = _field(
        {"tokens": 131_072, "state_bytes": 128 * MIB},
        "DECLARED",
        "card:context",
    )
    weak_context_result = preflight(
        revision,
        (weak_context,),
        requirements,
        _profile(),
        probes=(MetadataProbe(("context",), "config.json", 0, 101),),
    )
    assert weak_context_result.classification == "METADATA_INSUFFICIENT"

    sparse = _metadata()
    sparse["total_parameters"] = _field(
        2_000_000_000, "PARSED", "index:model"
    )
    sparse["active_parameters"] = _field(
        1_000_000_000, "PARSED", "index:model"
    )
    sparse["dtype_quantization"] = _field(
        {"name": "bf16", "active_bytes": 600 * 1024**2},
        "PARSED",
        "header:model",
    )
    sparse_result = preflight(
        revision,
        (sparse,),
        requirements,
        replace(_profile(), memory_bytes=800 * MIB),
    )
    assert sparse_result.classification == "SUPPORTED"
    assert sparse_result.peak_bytes == 728 * MIB
    sparse["dtype_quantization"] = _field("bf16", "PARSED", "header:model")
    sparse_unknown = preflight(
        revision,
        (sparse,),
        requirements,
        replace(_profile(), memory_bytes=700 * MIB),
        probes=(MetadataProbe(("dtype_quantization",), "model.safetensors", 0, 8),),
    )
    assert sparse_unknown.classification == "METADATA_INSUFFICIENT"
    assert sparse_unknown.peak_bytes is None

    custom = _metadata()
    custom["operators"] = _field()
    custom["custom_code"] = _field(True, "PARSED", "config:auto-map")
    custom["conflicts"].append({
        "field": "custom_code",
        "candidates": [
            _field(False, "DECLARED", "card:custom-code"),
            _field(True, "PARSED", "config:auto-map"),
        ],
    })
    refused_before_fill = preflight(
        revision, (custom,), requirements, _profile(), probes=(probe,)
    )
    custom["operators"] = metadata["operators"]
    refused_after_fill = preflight(revision, (custom,), requirements, _profile())
    assert refused_before_fill.classification == "UNSUPPORTED"
    assert refused_after_fill.classification == "UNSUPPORTED"
    assert "CUSTOM_CODE_REQUIRES_CONTAINMENT" in refused_before_fill.reasons
    assert "CUSTOM_CODE_REQUIRES_CONTAINMENT" in refused_after_fill.reasons
    assert refused_after_fill.evidence["custom_code"]["value"] is True

    unsupported_operator = _metadata()
    unsupported_operator["operators"] = _field(
        ["attention", "foreign_operator", "matmul"], "PARSED", "graph:model"
    )
    operator_result = preflight(
        revision, (unsupported_operator,), requirements, _profile()
    )
    assert operator_result.classification == "UNSUPPORTED"
    assert "UNSUPPORTED_OPERATOR:foreign_operator" in operator_result.reasons

    unsupported_modality = _metadata()
    unsupported_modality["modalities"] = _field(
        ["text", "vision"], "PARSED", "config:model"
    )
    unsupported_modality["processor"] = _field(
        "sha256:" + "9" * 64, "EVIDENCE_DIGESTED", "manifest:processor"
    )
    modality_result = preflight(
        revision, (unsupported_modality,), requirements, _profile()
    )
    assert modality_result.classification == "UNSUPPORTED"
    assert "UNSUPPORTED_MODALITY:vision" in modality_result.reasons

    mutable = preflight(
        replace(revision, immutable_revision="main"),
        (metadata,),
        requirements,
        _profile(),
    )
    assert mutable.classification == "UNSUPPORTED"
    assert "MUTABLE_OR_UNVERIFIED_SOURCE_IDENTITY" in mutable.reasons

    gated_metadata = _metadata()
    gated_metadata["gating"] = _field(True, "DECLARED", "source:gating")
    gated = preflight(
        replace(revision, credential_ref=None, license_acceptance_ref=None),
        (gated_metadata,),
        requirements,
        _profile(),
    )
    assert gated.classification == "UNSUPPORTED"
    assert gated.reasons[:2] == ("CREDENTIAL_REQUIRED", "LICENSE_ACCEPTANCE_REQUIRED")
    admitted_gated = preflight(
        revision, (gated_metadata,), requirements, _profile()
    )
    assert admitted_gated.classification == "SUPPORTED"

    deceptive = _metadata()
    deceptive["active_parameters"] = _field(
        1_000_000_001, "PARSED", "index:deceptive"
    )
    rejected_deception = preflight(
        revision, (deceptive,), requirements, _profile()
    )
    assert rejected_deception.classification == "UNSUPPORTED"
    assert "INVALID_METADATA:active_parameters" in rejected_deception.reasons

    tied = _metadata()
    tied["architecture"] = _field("parsed-a", "PARSED", "config:a")
    tied["conflicts"] = [{
        "field": "architecture",
        "candidates": [
            _field("parsed-a", "PARSED", "config:a"),
            _field("parsed-b", "EVIDENCE_DIGESTED", "manifest:b"),
        ],
    }]
    tied_result = preflight(
        revision,
        (tied,),
        requirements,
        _profile(),
        probes=(MetadataProbe(("architecture",), "config.json", 0, 101),),
    )
    assert tied_result.classification == "METADATA_INSUFFICIENT"
    assert tied_result.architecture is None
    assert tied_result.evidence["architecture"] == {
        "trust": "ABSENT", "authority": "cassette:conflict:architecture",
    }
