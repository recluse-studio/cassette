# errors.py — canonical typed error vocabulary and shape (Q6; Q32 single error authority); depends on (none).
"""The one error authority (Q32). Every failure anywhere in Cassette is a CassetteError.

Shape is Q6's contract exactly: {code, object_id, failed_invariant, retryability, detail}.
The code set is closed: constructing an error with an unknown code or retryability is itself a
defect and raises ValueError. Codes are grouped by the authority that emits them; the Qn in each
comment names the packet that defines the failure. Adding a code is a recorded vocabulary change,
never an ad-hoc string.
"""

from __future__ import annotations

from dataclasses import dataclass

RETRYABILITY = frozenset({"retryable", "terminal"})

CODES = frozenset({
    # identity and sources (Q1, Q9, Q51, Q54)
    "IDENTITY_MISMATCH",
    "SOURCE_UNAVAILABLE",
    "SOURCE_REVISION_CHANGED",
    "AUTH_REQUIRED",
    "DELTA_BASE_MISMATCH",
    # admission (Q28, Q47, Q53, Q74)
    "CAPACITY_EXCEEDED",
    "MEMORY_BUDGET_EXCEEDED",
    "ENDURANCE_EXCEEDED",
    "THERMAL_LIMIT",
    # cartridge lifecycle and integrity (Q44, Q49, Q62)
    "CARTRIDGE_DISCONNECTED",
    "CARTRIDGE_READ_ONLY",
    "CARTRIDGE_IDENTITY_MISMATCH",
    "DURABILITY_UNSUPPORTED",
    "PAGE_CORRUPT",
    "ROOT_INVALID",
    # execution (Q7, Q20, Q56, Q64, Q66)
    "WORKING_SET_TIMEOUT",
    "UNSUPPORTED_OPERATOR",
    "CAPABILITY_MISMATCH",
    "MODEL_UNSUPPORTED",
    "METADATA_INSUFFICIENT",
    # protocol and operations (Q5, Q6, Q65)
    "INVALID_REQUEST",
    "IDEMPOTENCY_CONFLICT",
    "OPERATION_NOT_FOUND",
    "OPERATION_CANCELLED",
    "OVERLOADED",
    # training (Q21, Q24, Q25, Q70-Q75)
    "GRADIENT_INVALID",
    "TRAINING_UNSUPPORTED",
    # containment and provenance (Q55, Q79)
    "CONTAINMENT_REJECTED",
    "PROVENANCE_VIOLATION",
})


@dataclass(frozen=True)
class CassetteError(Exception):
    """Q6 error shape. Frozen: an error is a fact, not a mutable object."""

    code: str
    object_id: str
    failed_invariant: str
    retryability: str
    detail: str = ""

    def __post_init__(self) -> None:
        if self.code not in CODES:
            raise ValueError(f"unknown error code {self.code!r}; the vocabulary is closed (Q6/Q32)")
        if self.retryability not in RETRYABILITY:
            raise ValueError(f"retryability must be one of {sorted(RETRYABILITY)}, got {self.retryability!r}")
        if not self.object_id:
            raise ValueError("object_id is required (Q6)")
        if not self.failed_invariant:
            raise ValueError("failed_invariant is required (Q6)")

    def payload(self) -> dict:
        """Exactly the five Q6 fields, protocol-ready."""
        return {
            "code": self.code,
            "object_id": self.object_id,
            "failed_invariant": self.failed_invariant,
            "retryability": self.retryability,
            "detail": self.detail,
        }

    def __str__(self) -> str:
        suffix = f" — {self.detail}" if self.detail else ""
        return f"{self.code}({self.object_id}): {self.failed_invariant}{suffix}"
