# test_s02_errors.py — S02 fixtures for Q6 error schema conformance; depends on errors.py.
"""S02: the error vocabulary is closed, the shape is Q6's exactly, and payloads round-trip."""

import json

import pytest

from errors import CODES, RETRYABILITY, CassetteError


def make(code="PAGE_CORRUPT", retryability="terminal"):
    return CassetteError(
        code=code,
        object_id="page:blake3:00ff",
        failed_invariant="Q62: page digest must match before residency",
        retryability=retryability,
    )


def test_error_shape_is_q6_exactly_and_round_trips():
    """Q6: Error={code,object_id,failed_invariant,retryability,detail} — no more, no less."""
    err = make()
    payload = err.payload()
    assert set(payload) == {"code", "object_id", "failed_invariant", "retryability", "detail"}
    assert json.loads(json.dumps(payload)) == payload
    assert isinstance(err, Exception)
    with pytest.raises(CassetteError):
        raise err


def test_vocabulary_is_closed_q6_q32():
    """Q6/Q32: one error authority — unknown codes, retryabilities, and empty fields are defects."""
    with pytest.raises(ValueError):
        make(code="SOMETHING_NEW")
    with pytest.raises(ValueError):
        make(retryability="maybe")
    with pytest.raises(ValueError):
        CassetteError(code="PAGE_CORRUPT", object_id="", failed_invariant="x", retryability="terminal")
    with pytest.raises(ValueError):
        CassetteError(code="PAGE_CORRUPT", object_id="x", failed_invariant="", retryability="terminal")


def test_every_code_constructs_q6():
    """Q6: every code in the closed set is usable with both retryability values."""
    for code in sorted(CODES):
        for retry in sorted(RETRYABILITY):
            err = make(code=code, retryability=retry)
            assert err.payload()["code"] == code
