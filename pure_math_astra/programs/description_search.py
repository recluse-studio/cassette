# description_search.py — finite attacks on spectral residual descriptions; depends on no repository files.
import json
import platform

import numpy as np


def spectral_bounds(matrix, tolerance=1e-6):
    """Return numerical primal and dual bounds; floating-point bounds are not certificates."""
    energies = np.sum(abs(matrix) ** 2, axis=0).real
    active = energies > 1e-25 * max(float(energies.sum()), 1e-100)
    matrix, energies = matrix[:, active], energies[active]
    count = len(energies)
    if count <= 1:
        return 0.0, 0.0
    scale = float(energies.sum())
    gram = matrix.conj().T @ matrix / scale
    energies = energies / scale
    probabilities = energies.copy()
    threshold = 2.0
    equality = np.r_[0.0, np.ones(count)]
    identity = np.eye(count)
    final_density = identity / count

    for barrier in (0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001, 0.0000001):
        for _ in range(50):
            slack = threshold * identity + gram - np.diag(energies / probabilities)
            inverse = np.linalg.inv(slack)
            inverse = (inverse + inverse.conj().T) / 2
            square = inverse @ inverse
            diagonal = inverse.diagonal().real
            slope = energies / probabilities ** 2
            gradient = np.r_[1 - barrier * np.trace(inverse).real,
                             -barrier * slope * diagonal]
            hessian = np.empty((count + 1, count + 1))
            hessian[0, 0] = barrier * np.trace(square).real
            hessian[0, 1:] = hessian[1:, 0] = barrier * slope * square.diagonal().real
            hessian[1:, 1:] = barrier * np.outer(slope, slope) * abs(inverse) ** 2
            hessian[1:, 1:] += np.diag(2 * barrier * energies * diagonal / probabilities ** 3)
            system = np.zeros((count + 2, count + 2))
            system[:-1, :-1] = hessian
            system[-1, :-1] = system[:-1, -1] = equality
            right = np.r_[-gradient, 0.0]
            try:
                direction = np.linalg.solve(system, right)[:-1]
            except np.linalg.LinAlgError:
                break
            decrease = float(gradient @ direction)
            if -decrease < max(1e-13, barrier * 1e-7):
                break
            old_value = threshold - barrier * np.linalg.slogdet(slack)[1]
            step = 1.0
            accepted = False
            for _ in range(45):
                next_threshold = threshold + step * direction[0]
                next_probabilities = probabilities + step * direction[1:]
                if min(next_probabilities) > 0:
                    next_slack = next_threshold * identity + gram - np.diag(energies / next_probabilities)
                    eigenvalues = np.linalg.eigvalsh(next_slack)
                    if eigenvalues[0] > 0:
                        next_value = next_threshold - barrier * np.log(eigenvalues).sum()
                        if next_value <= old_value + 0.01 * step * decrease:
                            threshold, probabilities = next_threshold, next_probabilities
                            accepted = True
                            break
                step /= 2
            if not accepted:
                break
        slack = threshold * identity + gram - np.diag(energies / probabilities)
        inverse = np.linalg.inv(slack)
        final_density = inverse / np.trace(inverse).real
        covariance = np.diag(energies / probabilities) - gram
        upper = float(np.linalg.eigvalsh(covariance)[-1])
        lower = float(np.sum(np.sqrt(energies * final_density.diagonal().real)) ** 2
                      - np.trace(final_density @ gram).real)
        if upper - lower < tolerance:
            return scale * max(0, lower), scale * upper
    return scale * max(0, lower), scale * upper


def rank_envelope(energies, rank):
    energies = np.sort(np.asarray(energies))[::-1]
    tail = float(energies[rank - 1:].sum())
    imbalance = max(0, 2 * energies[rank - 1] - tail)
    low, high = 0.0, float(energies.sum())
    for _ in range(90):
        middle = (low + high) / 2
        mass = np.sum(energies[:rank - 1] / (middle + energies[:rank - 1]))
        mass += tail / middle - imbalance ** 2 / (middle * (tail + middle))
        if mass > 1:
            low = middle
        else:
            high = middle
    return (low + high) / 2


def canonical_frame(energies, rank):
    energies = np.sort(np.asarray(energies))[::-1]
    frame = np.zeros((rank, len(energies)))
    for index in range(rank - 1):
        frame[index, index] = np.sqrt(energies[index])
    frame[-1, rank - 1:] = np.sqrt(energies[rank - 1:])
    return frame


def weighted_description(matrix, rank, grid):
    best_value, best_residual, best_choice = float("inf"), None, None
    for column in range(matrix.shape[1]):
        for parameter in grid:
            roots = np.full(matrix.shape[1], 1 / np.sqrt(parameter))
            roots[column] = np.sqrt(parameter)
            weighted = matrix * roots
            left, singular, right = np.linalg.svd(weighted, full_matrices=False)
            description = ((left[:, :rank] * singular[:rank]) @ right[:rank, :]) / roots
            residual = matrix - description
            value = float(np.sum(abs(residual * roots) ** 2))
            if value < best_value:
                best_value, best_residual = value, residual
                best_choice = [column, float(parameter)]
    return best_value, best_residual, best_choice


def run_search():
    rng = np.random.default_rng(2026090602)
    largest_gap = 0.0
    smallest_envelope_margin = float("inf")
    largest_attainment_error = 0.0
    envelope_cases = 0
    for dimension in (1, 2, 3):
        for columns in range(dimension + 1, dimension + 4):
            for field in ("real", "complex"):
                for _ in range(6):
                    energies = np.exp(rng.uniform(-5, 5, columns))
                    energies /= energies.sum()
                    matrix = rng.normal(size=(dimension, columns))
                    if field == "complex":
                        matrix = matrix + 1j * rng.normal(size=matrix.shape)
                    matrix *= np.sqrt(energies) / np.linalg.norm(matrix, axis=0)
                    lower, upper = spectral_bounds(matrix)
                    envelope = rank_envelope(energies, dimension)
                    smallest_envelope_margin = min(smallest_envelope_margin, upper - envelope)
                    largest_gap = max(largest_gap, upper - lower)
                    canonical = canonical_frame(energies, dimension)
                    canonical_lower, canonical_upper = spectral_bounds(canonical)
                    largest_attainment_error = max(largest_attainment_error, abs(canonical_upper - envelope))
                    assert upper >= envelope - 1e-7
                    assert canonical_lower <= envelope + 1e-7
                    assert abs(canonical_upper - envelope) < 1e-5
                    envelope_cases += 1

    best_separation = None
    for trial in range(30):
        matrix = rng.normal(size=(3, 4)) * np.exp(rng.uniform(-1, 1, 4))
        matrix /= np.linalg.norm(matrix)
        surrogate, residual, choice = weighted_description(matrix, 1, np.geomspace(0.01, 1, 65))
        selected_lower, selected_upper = spectral_bounds(residual)
        best_competitor = selected_upper
        best_direction = None
        for _ in range(60):
            direction = rng.normal(size=3)
            direction /= np.linalg.norm(direction)
            competitor = matrix - np.outer(direction, direction @ matrix)
            lower, upper = spectral_bounds(competitor, tolerance=3e-6)
            if upper < best_competitor:
                best_competitor, best_direction = upper, direction.tolist()
        separation = selected_lower - best_competitor
        if best_separation is None or separation > best_separation["lower_minus_competitor_upper"]:
            best_separation = {
                "trial": trial, "matrix": matrix.tolist(), "surrogate": surrogate,
                "selected_spectral_interval": [selected_lower, selected_upper],
                "choice": choice, "competitor_upper": best_competitor,
                "competitor_direction": best_direction,
                "lower_minus_competitor_upper": separation,
            }
    return {
        "python": platform.python_version(), "numpy": np.__version__, "seed": 2026090602,
        "rank_envelope_cases": envelope_cases, "largest_numerical_duality_gap": largest_gap,
        "smallest_sampled_value_minus_envelope": smallest_envelope_margin,
        "largest_canonical_attainment_error": largest_attainment_error,
        "weighted_description_separation": best_separation,
        "boundary": "Finite floating-point falsification. Numerical intervals are not exact certificates.",
    }


if __name__ == "__main__":
    print(json.dumps(run_search(), indent=2))

