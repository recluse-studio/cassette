# minimax_residual_sampling.py — finite falsification searches for the isolated residual-access theorem; depends on no repo file.
"""Search small real cases for counterexamples; numerical output is not a proof."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import isclose, sqrt
from random import Random


Matrix = list[list[float]]


def transpose(matrix: Matrix) -> Matrix:
    return [list(column) for column in zip(*matrix, strict=True)]


def multiply(left: Matrix, right: Matrix) -> Matrix:
    right_t = transpose(right)
    return [
        [sum(a * b for a, b in zip(row, column, strict=True)) for column in right_t]
        for row in left
    ]


def gram(matrix: Matrix) -> Matrix:
    return multiply(transpose(matrix), matrix)


def matvec(matrix: Matrix, vector: list[float]) -> list[float]:
    return [sum(value * coordinate for value, coordinate in zip(row, vector, strict=True)) for row in matrix]


def squared_norm(vector: list[float]) -> float:
    return sum(value * value for value in vector)


def direct_one_sample_mse(
    residual: Matrix,
    probabilities: list[float],
    query: list[float],
) -> float:
    """Enumerate sampling outcomes without using the covariance identity."""
    target = matvec(residual, query)
    error = 0.0
    for column_index, probability in enumerate(probabilities):
        sampled = [
            row[column_index] * query[column_index] / probability
            for row in residual
        ]
        difference = [
            estimate - exact
            for estimate, exact in zip(sampled, target, strict=True)
        ]
        error += probability * squared_norm(difference)
    return error


def covariance_matrix(residual: Matrix, probabilities: list[float]) -> Matrix:
    residual_gram = gram(residual)
    column_energy = [residual_gram[index][index] for index in range(len(residual_gram))]
    covariance = [row[:] for row in residual_gram]
    for row_index in range(len(covariance)):
        for column_index in range(len(covariance)):
            covariance[row_index][column_index] *= -1.0
        covariance[row_index][row_index] += column_energy[row_index] / probabilities[row_index]
    return covariance


def quadratic_form(matrix: Matrix, vector: list[float]) -> float:
    return sum(
        vector[row_index] * matrix[row_index][column_index] * vector[column_index]
        for row_index in range(len(vector))
        for column_index in range(len(vector))
    )


def largest_symmetric_eigenvalue(matrix: Matrix, sweeps: int = 80) -> float:
    """Return the largest eigenvalue through cyclic Jacobi diagonalization."""
    work = [row[:] for row in matrix]
    size = len(work)
    if size == 1:
        return work[0][0]
    for _ in range(sweeps):
        pivot = max(
            ((abs(work[i][j]), i, j) for i in range(size) for j in range(i + 1, size)),
            default=(0.0, 0, 0),
        )
        magnitude, row_index, column_index = pivot
        if magnitude < 1e-13:
            break
        diagonal_gap = work[column_index][column_index] - work[row_index][row_index]
        angle_tangent = (
            1.0
            if isclose(diagonal_gap, 0.0, abs_tol=1e-30)
            else (2.0 * work[row_index][column_index])
            / (diagonal_gap + (1.0 if diagonal_gap >= 0.0 else -1.0) * sqrt(
                diagonal_gap * diagonal_gap
                + 4.0 * work[row_index][column_index] * work[row_index][column_index]
            ))
        )
        cosine = 1.0 / sqrt(1.0 + angle_tangent * angle_tangent)
        sine = angle_tangent * cosine
        old_rr = work[row_index][row_index]
        old_cc = work[column_index][column_index]
        old_rc = work[row_index][column_index]
        work[row_index][row_index] = (
            cosine * cosine * old_rr
            - 2.0 * sine * cosine * old_rc
            + sine * sine * old_cc
        )
        work[column_index][column_index] = (
            sine * sine * old_rr
            + 2.0 * sine * cosine * old_rc
            + cosine * cosine * old_cc
        )
        work[row_index][column_index] = 0.0
        work[column_index][row_index] = 0.0
        for index in range(size):
            if index in (row_index, column_index):
                continue
            old_ir = work[index][row_index]
            old_ic = work[index][column_index]
            work[index][row_index] = cosine * old_ir - sine * old_ic
            work[row_index][index] = work[index][row_index]
            work[index][column_index] = sine * old_ir + cosine * old_ic
            work[column_index][index] = work[index][column_index]
    return max(work[index][index] for index in range(size))


def numerical_worst_variance(residual: Matrix, probabilities: list[float]) -> float:
    return largest_symmetric_eigenvalue(covariance_matrix(residual, probabilities))


def squared_norm_sampling(residual: Matrix) -> list[float]:
    residual_gram = gram(residual)
    energy = [residual_gram[index][index] for index in range(len(residual_gram))]
    total = sum(energy)
    return [value / total for value in energy]


def two_column_closed_form(residual: Matrix) -> tuple[list[float], float]:
    residual_gram = gram(residual)
    first_energy = residual_gram[0][0]
    second_energy = residual_gram[1][1]
    cross = abs(residual_gram[0][1])
    first_norm = sqrt(first_energy)
    second_norm = sqrt(second_energy)
    probabilities = [
        first_norm / (first_norm + second_norm),
        second_norm / (first_norm + second_norm),
    ]
    return probabilities, sqrt(first_energy * second_energy) + cross


def two_column_dual_grid(residual: Matrix, denominator: int) -> float:
    residual_gram = gram(residual)
    first_energy = residual_gram[0][0]
    second_energy = residual_gram[1][1]
    cross = residual_gram[0][1]
    best = float("-inf")
    for count in range(denominator + 1):
        first_diagonal = count / denominator
        second_diagonal = 1.0 - first_diagonal
        off_diagonal = (
            -1.0 if cross >= 0.0 else 1.0
        ) * sqrt(first_diagonal * second_diagonal)
        reciprocal_term = (
            sqrt(first_energy * first_diagonal)
            + sqrt(second_energy * second_diagonal)
        ) ** 2
        gram_term = (
            first_energy * first_diagonal
            + second_energy * second_diagonal
            + 2.0 * cross * off_diagonal
        )
        best = max(best, reciprocal_term - gram_term)
    return best


def simplex_grid(size: int, denominator: int) -> list[list[float]]:
    points: list[list[float]] = []
    for counts in product(range(1, denominator), repeat=size - 1):
        used = sum(counts)
        final = denominator - used
        if final > 0:
            points.append([*(count / denominator for count in counts), final / denominator])
    return points


@dataclass(frozen=True)
class SearchResult:
    probabilities: list[float]
    variance: float


def grid_minimax(residual: Matrix, denominator: int) -> SearchResult:
    size = len(residual[0])
    candidates = (
        SearchResult(probabilities, numerical_worst_variance(residual, probabilities))
        for probabilities in simplex_grid(size, denominator)
    )
    return min(candidates, key=lambda candidate: candidate.variance)


def orthogonal_waterfill(energies: list[float]) -> SearchResult:
    if len(energies) == 1:
        return SearchResult([1.0], 0.0)
    lower = 0.0
    upper = max(energies) * len(energies)
    for _ in range(100):
        middle = (lower + upper) / 2.0
        total = sum(energy / (energy + middle) for energy in energies)
        if total > 1.0:
            lower = middle
        else:
            upper = middle
    variance = (lower + upper) / 2.0
    probabilities = [energy / (energy + variance) for energy in energies]
    return SearchResult(probabilities, variance)


def rank_one_closed_form(energies: list[float]) -> SearchResult:
    total = sum(energies)
    if len(energies) == 1:
        return SearchResult([1.0], 0.0)
    dominant_index = max(range(len(energies)), key=energies.__getitem__)
    dominant = energies[dominant_index]
    tail = total - dominant
    if dominant <= total / 2.0:
        return SearchResult([energy / total for energy in energies], total)
    root_dominant = sqrt(dominant)
    root_tail = sqrt(tail)
    denominator = root_dominant + root_tail
    probabilities = [
        root_dominant / denominator
        if index == dominant_index
        else energy / (root_tail * denominator)
        for index, energy in enumerate(energies)
    ]
    return SearchResult(probabilities, 2.0 * sqrt(dominant * tail))


def random_matrix(random: Random, rows: int, columns: int) -> Matrix:
    return [
        [float(random.randint(-7, 7)) for _ in range(columns)]
        for _ in range(rows)
    ]


def run_two_column_falsification() -> None:
    random = Random(20260905)
    maximum_formula_gap = 0.0
    maximum_dual_grid_gap = 0.0
    minimum_grid_advantage = float("inf")
    checked = 0
    for _ in range(160):
        residual = random_matrix(random, rows=4, columns=2)
        residual_gram = gram(residual)
        if residual_gram[0][0] == 0.0 or residual_gram[1][1] == 0.0:
            continue
        probabilities, formula_variance = two_column_closed_form(residual)
        evaluated_variance = numerical_worst_variance(residual, probabilities)
        grid_result = grid_minimax(residual, denominator=600)
        dual_grid_value = two_column_dual_grid(residual, denominator=4000)
        if not isclose(formula_variance, evaluated_variance, rel_tol=1e-11, abs_tol=1e-11):
            raise AssertionError("two-column formula disagrees with its covariance evaluation")
        if grid_result.variance + 1e-10 < evaluated_variance:
            raise AssertionError("a grid point beats the claimed two-column minimizer")
        if dual_grid_value > formula_variance + 1e-9:
            raise AssertionError("the density-matrix dual grid exceeds the claimed optimum")
        maximum_formula_gap = max(maximum_formula_gap, abs(formula_variance - evaluated_variance))
        maximum_dual_grid_gap = max(
            maximum_dual_grid_gap,
            formula_variance - dual_grid_value,
        )
        minimum_grid_advantage = min(
            minimum_grid_advantage,
            grid_result.variance - evaluated_variance,
        )
        checked += 1
    print(f"two-column cases checked: {checked}")
    print(f"maximum closed-form evaluation gap: {maximum_formula_gap:.3e}")
    print(f"maximum closed-form minus dual-grid value: {maximum_dual_grid_gap:.3e}")
    print(f"smallest grid value minus closed form: {minimum_grid_advantage:.3e}")


def run_estimator_identity_falsification() -> None:
    random = Random(112358)
    maximum_gap = 0.0
    for _ in range(400):
        residual = random_matrix(random, rows=3, columns=3)
        raw_probabilities = [random.uniform(0.05, 1.0) for _ in range(3)]
        probability_total = sum(raw_probabilities)
        probabilities = [value / probability_total for value in raw_probabilities]
        query = [random.uniform(-2.0, 2.0) for _ in range(3)]
        direct = direct_one_sample_mse(residual, probabilities, query)
        covariance = quadratic_form(covariance_matrix(residual, probabilities), query)
        maximum_gap = max(maximum_gap, abs(direct - covariance))
        if not isclose(direct, covariance, rel_tol=1e-11, abs_tol=1e-10):
            raise AssertionError("outcome enumeration disagrees with the covariance identity")
    print(f"estimator/covariance cases checked: 400")
    print(f"maximum direct-enumeration gap: {maximum_gap:.3e}")


def run_orthogonal_falsification() -> None:
    random = Random(271828)
    largest_equalization_gap = 0.0
    smallest_grid_advantage = float("inf")
    for _ in range(30):
        energies = [float(random.randint(1, 100)) for _ in range(3)]
        result = orthogonal_waterfill(energies)
        diagonal_variances = [
            energy * (1.0 / probability - 1.0)
            for energy, probability in zip(energies, result.probabilities, strict=True)
        ]
        gap = max(abs(value - result.variance) for value in diagonal_variances)
        largest_equalization_gap = max(largest_equalization_gap, gap)
        if gap > 1e-10:
            raise AssertionError("water-filling does not equalize the active diagonal variances")
        if not isclose(sum(result.probabilities), 1.0, rel_tol=0.0, abs_tol=1e-12):
            raise AssertionError("water-filling probabilities do not sum to one")
        residual = [
            [sqrt(energies[row]) if row == column else 0.0 for column in range(3)]
            for row in range(3)
        ]
        grid_result = grid_minimax(residual, denominator=120)
        smallest_grid_advantage = min(
            smallest_grid_advantage,
            grid_result.variance - result.variance,
        )
        if grid_result.variance + 1e-9 < result.variance:
            raise AssertionError("a grid point beats the orthogonal water-filling solution")
    print("orthogonal three-column cases checked: 30")
    print(f"largest water-filling equalization gap: {largest_equalization_gap:.3e}")
    print(f"smallest orthogonal grid value minus closed form: {smallest_grid_advantage:.3e}")


def run_rank_one_falsification() -> None:
    random = Random(161803)
    maximum_formula_gap = 0.0
    smallest_grid_advantage = float("inf")
    balanced_cases = 0
    dominant_cases = 0
    for _ in range(80):
        energies = [float(random.randint(1, 100)) for _ in range(3)]
        result = rank_one_closed_form(energies)
        residual = [[sqrt(energy) for energy in energies]]
        evaluated_variance = numerical_worst_variance(residual, result.probabilities)
        grid_result = grid_minimax(residual, denominator=160)
        maximum_formula_gap = max(
            maximum_formula_gap,
            abs(result.variance - evaluated_variance),
        )
        smallest_grid_advantage = min(
            smallest_grid_advantage,
            grid_result.variance - result.variance,
        )
        if not isclose(result.variance, evaluated_variance, rel_tol=1e-10, abs_tol=1e-10):
            raise AssertionError("rank-one formula disagrees with its covariance evaluation")
        if grid_result.variance + 1e-9 < result.variance:
            raise AssertionError("a grid point beats the claimed rank-one minimizer")
        if max(energies) <= sum(energies) / 2.0:
            balanced_cases += 1
        else:
            dominant_cases += 1
    print(
        "rank-one three-column cases checked: "
        f"{balanced_cases + dominant_cases} "
        f"({balanced_cases} balanced, {dominant_cases} dominant)"
    )
    print(f"maximum rank-one formula gap: {maximum_formula_gap:.3e}")
    print(f"smallest rank-one grid value minus closed form: {smallest_grid_advantage:.3e}")


def show_unbounded_improvement_family() -> None:
    print("orthogonal two-column family")
    print("ratio  frobenius-law variance  minimax variance  improvement")
    for ratio in (1, 4, 16, 64, 256, 1024, 4096):
        residual = [[sqrt(float(ratio)), 0.0], [0.0, 1.0]]
        frobenius_variance = numerical_worst_variance(residual, squared_norm_sampling(residual))
        probabilities, minimax_formula = two_column_closed_form(residual)
        improvement = frobenius_variance / minimax_formula
        print(
            f"{ratio:5d}  {frobenius_variance:22.8f}  "
            f"{minimax_formula:16.8f}  {improvement:11.6f}  p={probabilities}"
        )


if __name__ == "__main__":
    run_estimator_identity_falsification()
    run_two_column_falsification()
    run_orthogonal_falsification()
    run_rank_one_falsification()
    show_unbounded_improvement_family()
