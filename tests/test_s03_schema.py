# test_s03_schema.py — S03 fixtures for Q6/Q9/Q31/Q50/Q57 contract conformance (F0); depends on tools/genschema.py, schema/validator.py, tools/ledger.py.
"""S03: generated validators round-trip golden fixtures and reject malformed ones (Q6/Q9/Q31/Q50/Q57)."""

import shutil
from pathlib import Path

from schema.validator import validate
from tools.genschema import emit
from tools.ledger import check_generated_integrity

REPO = Path(__file__).resolve().parent.parent

GOLDEN = {
    "error": {
        "code": "PAGE_CORRUPT",
        "object_id": "page:blake3:00ff",
        "failed_invariant": "Q62: digest must match before residency",
        "retryability": "terminal",
        "detail": "",
    },
    "request": {
        "protocol_version": "1",
        "operation": "run",
        "idempotency_key": "k-1",
        "arguments": {},
    },
    "operation": {
        "operation_id": "op-1",
        "kind": "acquire",
        "state": "RUNNING",
        "progress": 0.5,
    },
    "run_event": {"run_id": "r-1", "sequence": 3, "type": "output_delta", "payload": {"text": "x"}},
    "source_descriptor": {"kind": "huggingface", "locator": "org/model"},
    "remote_metadata_field": {
        "name": "total_bytes",
        "value": 1560936091448,
        "trust": "EVIDENCE_DIGESTED",
        "authority": "hf api",
    },
    "root": {
        "identity": "I-abc",
        "parents": [],
        "provenance": {},
        "semantic_assets": {},
        "tensor_maps": [],
        "operators": [],
        "plans": [],
        "deltas": [],
        "integrity_root": "merkle-abc",
    },
}


def test_golden_valid_instances_pass():
    """Q6 Q9 Q31 Q50 Q57: every contract accepts its golden instance."""
    for kind, obj in GOLDEN.items():
        assert validate(kind, obj) == [], f"{kind} golden rejected"


def test_malformed_instances_rejected():
    """Q6 Q9 Q31 Q50 Q57: missing fields, wrong types, unknown fields, bad enums, bad refs all fail."""
    missing = dict(GOLDEN["error"])
    del missing["code"]
    assert any("required field missing" in d for d in validate("error", missing))
    wrong_type = dict(GOLDEN["run_event"], sequence="three")
    assert any("expected int" in d for d in validate("run_event", wrong_type))
    bool_int = dict(GOLDEN["run_event"], sequence=True)
    assert any("bool is not a" in d for d in validate("run_event", bool_int))
    unknown = dict(GOLDEN["source_descriptor"], surprise=1)
    assert any("unknown field" in d for d in validate("source_descriptor", unknown))
    bad_enum = dict(GOLDEN["remote_metadata_field"], trust="GUESSED")
    assert any("not in enum" in d for d in validate("remote_metadata_field", bad_enum))
    bad_ref = dict(GOLDEN["operation"], error={"code": "PAGE_CORRUPT"})
    assert any("required field missing" in d for d in validate("operation", bad_ref))
    assert validate("no_such_kind", {}) == ["unknown contract kind 'no_such_kind'"]


def test_generator_idempotent_and_integrity_enforced(tmp_path):
    """Q57 and q78_exact_accounting: regeneration is byte-identical; drift and missing manifests fail closed."""
    out1, out2 = tmp_path / "a" / "schema", tmp_path / "b" / "schema"
    manifest1, manifest2 = emit(out1), emit(out2)
    assert manifest1 == manifest2
    for name in manifest1:
        assert (out1 / name).read_bytes() == (out2 / name).read_bytes()

    committed = {
        p.relative_to(REPO / "schema").as_posix(): p.read_bytes()
        for p in sorted((REPO / "schema").rglob("*"))
        if p.is_file() and p.name != "MANIFEST.json" and "__pycache__" not in p.parts
    }
    fresh = {name: (out1 / name).read_bytes() for name in manifest1}
    assert committed == fresh, "committed schema/ drifted from the generator"

    status, violations = check_generated_integrity(tmp_path / "a")
    assert (status, violations) == ("ran", [])
    (out1 / "error.json").write_text((out1 / "error.json").read_text() + " ")
    status, violations = check_generated_integrity(tmp_path / "a")
    assert status == "ran" and any("hand-edited or drifted" in v for v in violations)
    shutil.copytree(out2, tmp_path / "c" / "schema")
    (tmp_path / "c" / "schema" / "MANIFEST.json").unlink()
    status, violations = check_generated_integrity(tmp_path / "c")
    assert status == "failed" and any("without MANIFEST.json" in v for v in violations)
