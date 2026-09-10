# skew3_proper_gap_certificate.py — exact integer proper-minor certificate for rank-two skew 3x3 polar gaps; depends on pure_math_astra/notes/rank_two_general_skew_polar_algebra_certificate.md.
"""Regenerate and verify the finite coefficient certificate for nine 2x2 gaps.

The polynomial ring is Z[s,z,d].  After removing a common monomial s^a z^b
from each gap, substitute s=1+h and z=1+h+j.  The emitted coefficient lists
use the deterministic monomial order (h exponent, j exponent, d exponent).
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, permutations
from math import comb
from pathlib import Path
from typing import Iterable

Exponent = tuple[int, int, int]


@dataclass(frozen=True)
class Polynomial:
    terms: dict[Exponent, int]

    def __post_init__(self) -> None:
        object.__setattr__(self, "terms", {key: value for key, value in self.terms.items() if value})

    @classmethod
    def constant(cls, value: int) -> "Polynomial":
        return cls({(0, 0, 0): value})

    def __add__(self, other: "Polynomial | int") -> "Polynomial":
        right = promote(other)
        result: defaultdict[Exponent, int] = defaultdict(int, self.terms)
        for exponent, coefficient in right.terms.items():
            result[exponent] += coefficient
        return Polynomial(dict(result))

    __radd__ = __add__

    def __neg__(self) -> "Polynomial":
        return Polynomial({exponent: -coefficient for exponent, coefficient in self.terms.items()})

    def __sub__(self, other: "Polynomial | int") -> "Polynomial":
        return self + -promote(other)

    def __rsub__(self, other: "Polynomial | int") -> "Polynomial":
        return promote(other) + -self

    def __mul__(self, other: "Polynomial | int") -> "Polynomial":
        right = promote(other)
        result: defaultdict[Exponent, int] = defaultdict(int)
        for (first_h, first_j, first_d), first_coefficient in self.terms.items():
            for (second_h, second_j, second_d), second_coefficient in right.terms.items():
                result[(first_h + second_h, first_j + second_j, first_d + second_d)] += (
                    first_coefficient * second_coefficient
                )
        return Polynomial(dict(result))

    __rmul__ = __mul__

    def __pow__(self, power: int) -> "Polynomial":
        result = Polynomial.constant(1)
        for _ in range(power):
            result *= self
        return result


def promote(value: Polynomial | int) -> Polynomial:
    return value if isinstance(value, Polynomial) else Polynomial.constant(value)


ZERO = Polynomial.constant(0)
ONE = Polynomial.constant(1)
S = Polynomial({(1, 0, 0): 1})
Z = Polynomial({(0, 1, 0): 1})
D = Polynomial({(0, 0, 1): 1})


def determinant(matrix: list[list[Polynomial]]) -> Polynomial:
    size = len(matrix)
    result = ZERO
    for permutation in permutations(range(size)):
        inversions = sum(
            permutation[first] > permutation[second]
            for first in range(size)
            for second in range(first + 1, size)
        )
        product = Polynomial.constant(-1 if inversions % 2 else 1)
        for row, column in enumerate(permutation):
            product *= matrix[row][column]
        result += product
    return result


def minor(matrix: list[list[Polynomial]], row: int, column: int) -> list[list[Polynomial]]:
    return [current[:column] + current[column + 1 :] for index, current in enumerate(matrix) if index != row]


def adjugate_quadratic(matrix: list[list[Polynomial]], vector: list[Polynomial]) -> Polynomial:
    result = ZERO
    size = len(matrix)
    for row in range(size):
        for column in range(size):
            cofactor = determinant(minor(matrix, column, row))
            if (row + column) % 2:
                cofactor = -cofactor
            result += vector[row] * cofactor * vector[column]
    return result


def scaled_skew_matrix() -> list[list[Polynomial]]:
    scale = 2 * S * Z
    lower_entry = Z * (S * S - ONE)
    middle_entry = S * (Z * Z - ONE)
    upper_entry = middle_entry + scale * D
    return [
        [ZERO, lower_entry, -middle_entry],
        [-lower_entry, ZERO, upper_entry],
        [middle_entry, -upper_entry, ZERO],
    ]


def gap_for_sets(rows: tuple[int, int], columns: tuple[int, int]) -> Polynomial:
    matrix = scaled_skew_matrix()
    scale = 2 * S * Z
    raw_u = [ONE, -S, -Z]
    raw_n = [ONE, -S, Z]
    vector = [scale * raw_n[column] + sum(matrix[row][column] * raw_u[row] for row in rows) for column in columns]
    gram = [
        [
            (scale * scale if first_column == second_column else ZERO)
            + sum(matrix[row][first_column] * matrix[row][second_column] for row in rows)
            for second_column in columns
        ]
        for first_column in columns
    ]
    squared_u = sum(raw_u[row] * raw_u[row] for row in rows)
    return squared_u * determinant(gram) - adjugate_quadratic(gram, vector)


def common_s_z_factor(polynomial: Polynomial) -> tuple[int, int]:
    if not polynomial.terms:
        return 0, 0
    return (
        min(exponent[0] for exponent in polynomial.terms),
        min(exponent[1] for exponent in polynomial.terms),
    )


def remove_s_z_factor(polynomial: Polynomial, factor: tuple[int, int]) -> Polynomial:
    first, second = factor
    return Polynomial({(h - first, j - second, d): coefficient for (h, j, d), coefficient in polynomial.terms.items()})


def substitute_to_h_j(polynomial: Polynomial) -> Polynomial:
    """Apply s=1+h and z=1+h+j, preserving the exponent order h,j,d."""
    result: defaultdict[Exponent, int] = defaultdict(int)
    for (s_power, z_power, d_power), coefficient in polynomial.terms.items():
        for h_from_s in range(s_power + 1):
            s_coefficient = comb(s_power, h_from_s)
            for h_from_z in range(z_power + 1):
                z_h_coefficient = comb(z_power, h_from_z)
                for j_from_z in range(z_power - h_from_z + 1):
                    z_j_coefficient = comb(z_power - h_from_z, j_from_z)
                    result[(h_from_s + h_from_z, j_from_z, d_power)] += (
                        coefficient * s_coefficient * z_h_coefficient * z_j_coefficient
                    )
    return Polynomial(dict(result))


def label(indices: Iterable[int]) -> str:
    return "".join(str(index + 1) for index in indices)


def certificate() -> dict[str, object]:
    pairs = list(combinations(range(3), 2))
    gaps: dict[str, object] = {}
    for rows in pairs:
        for columns in pairs:
            raw_gap = gap_for_sets(rows, columns)
            factor = common_s_z_factor(raw_gap)
            reduced_gap = remove_s_z_factor(raw_gap, factor)
            expanded_gap = substitute_to_h_j(reduced_gap)
            if any(coefficient < 0 for coefficient in expanded_gap.terms.values()):
                raise AssertionError(f"negative coefficient for rows={rows}, columns={columns}")
            gaps[f"{label(rows)}|{label(columns)}"] = {
                "common_factor": {"s": factor[0], "z": factor[1]},
                "terms_h_j_d": [
                    [h_power, j_power, d_power, coefficient]
                    for (h_power, j_power, d_power), coefficient in sorted(expanded_gap.terms.items())
                ],
            }
    return {
        "schema": "skew3-proper-gap-certificate-v1",
        "variables": ["h", "j", "d"],
        "substitution": {"s": "1+h", "z": "1+h+j", "a_minus_b": "d"},
        "scaled_entries": {
            "D": "2*s*z",
            "C": "z*(s^2-1)",
            "B": "s*(z^2-1)",
            "A": "B+D*d",
        },
        "gaps": gaps,
    }


def verify_compact_gap_identities() -> None:
    """Check the nine compact raw-gap formulas after clearing (2*s*z)^4."""
    inverse_s = Polynomial({(-1, 0, 0): 1})
    inverse_z = Polynomial({(0, -1, 0): 1})
    half = Fraction(1, 2)
    c_value = half * (S - inverse_s)
    gamma = half * (S + inverse_s)
    b_value = half * (Z - inverse_z)
    beta = half * (Z + inverse_z)
    a_value = b_value + D
    scale = 2 * S * Z
    compact = {
        ((0, 1), (0, 1)): ZERO,
        ((0, 1), (0, 2)): 2 * a_value * gamma * beta,
        ((0, 1), (1, 2)): 2
        * gamma
        * (a_value * S * (gamma * beta - b_value * c_value) + c_value * (S * gamma + b_value * Z)),
        ((0, 2), (0, 1)): 2 * gamma * (2 * b_value * Z * gamma + a_value * (b_value + Z)),
        ((0, 2), (0, 2)): 4 * b_value * Z * (ONE + b_value * b_value),
        ((0, 2), (1, 2)): 2
        * beta
        * (a_value * Z * (gamma * beta - b_value * c_value) + b_value * (Z * beta + c_value * S)),
        ((1, 2), (0, 1)): gamma * gamma * (Z * Z - S * S)
        + 2 * b_value * S * gamma * Z
        + 2 * a_value * S * gamma * (b_value * S + Z * gamma),
        ((1, 2), (0, 2)): 4 * b_value * Z * D * D
        + 2 * Z * (gamma + (S + 4) * b_value * b_value + b_value * c_value * Z) * D
        + b_value * b_value * (S * S + Z * Z - 2)
        + 2 * b_value * Z * gamma * (ONE + S)
        + 2 * S * b_value * b_value * b_value * Z
        + 2 * b_value * b_value * c_value * Z * Z,
        ((1, 2), (1, 2)): 4 * a_value * S * Z * (ONE + a_value * a_value),
    }
    for pair, formula in compact.items():
        if (gap_for_sets(*pair) - scale**4 * formula).terms:
            raise AssertionError(f"compact identity mismatch for {pair}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path, help="write the deterministic JSON certificate")
    parser.add_argument("--check", type=Path, help="compare the regenerated certificate with JSON")
    arguments = parser.parse_args()
    verify_compact_gap_identities()
    generated = certificate()
    serialized = json.dumps(generated, indent=2, sort_keys=True) + "\n"
    if arguments.write:
        arguments.write.write_text(serialized)
    if arguments.check:
        expected = json.loads(arguments.check.read_text())
        if expected != generated:
            raise SystemExit(f"certificate mismatch: {arguments.check}")
    if not arguments.write and not arguments.check:
        print(serialized, end="")


if __name__ == "__main__":
    main()
