# extremal_geometry.py — finite attacks on fixed-energy Gram extrema; depends on no repository files.
import json
import platform

import numpy as np


def water_level(energies):
    low, high = 0.0, float(energies.sum())
    for _ in range(80):
        middle = (low + high) / 2
        if np.sum(energies / (energies + middle)) > 1:
            low = middle
        else:
            high = middle
    return (low + high) / 2


def fixed_energy_attacks():
    rng = np.random.default_rng(20260906)
    largest_upper_excess = -float('inf')
    smallest_lower_margin = float('inf')
    cases = 0
    for columns in range(2, 9):
        for output_dimension in range(1, columns + 1):
            for complex_field in (False, True):
                for _ in range(10):
                    matrix = rng.normal(size=(output_dimension, columns))
                    if complex_field:
                        matrix = matrix + 1j * rng.normal(size=matrix.shape)
                    matrix = matrix / np.linalg.norm(matrix, axis=0)
                    energies = np.exp(rng.uniform(-6, 6, columns))
                    energies = energies / energies.sum()
                    matrix = matrix * np.sqrt(energies)
                    gram = matrix.conj().T @ matrix
                    dominant = int(np.argmax(energies))
                    maximum = float(energies[dominant])
                    tail = 1.0 - maximum
                    if maximum > tail:
                        root = np.sqrt(maximum * tail)
                        probabilities = energies / (tail + root)
                        probabilities[dominant] = maximum / (maximum + root)
                        upper = 2 * root
                    else:
                        probabilities = energies.copy()
                        upper = 1.0
                    covariance = np.diag(energies / probabilities) - gram
                    value = float(np.linalg.eigvalsh(covariance)[-1])
                    largest_upper_excess = max(largest_upper_excess, value - upper)
                    random_law = rng.dirichlet(np.ones(columns))
                    random_value = float(np.linalg.eigvalsh(np.diag(energies / random_law) - gram)[-1])
                    lower = water_level(energies)
                    smallest_lower_margin = min(smallest_lower_margin, random_value - lower)
                    assert value <= upper + 2e-10, (energies, gram, value, upper)
                    assert random_value >= lower - 2e-10
                    cases += 1
    return {'cases': cases, 'largest_upper_excess': largest_upper_excess,
            'smallest_random_law_minus_lower': smallest_lower_margin}


def rank_two_three_column_attack():
    denominator = 60
    laws = np.array([(i, j, denominator-i-j)
                     for i in range(1, denominator-1)
                     for j in range(1, denominator-i)], dtype=float) / denominator
    diagonals = np.zeros((len(laws), 3, 3))
    diagonals[:, np.arange(3), np.arange(3)] = 1 / laws
    candidate = 1 + np.sqrt(3)
    best = {'value': candidate, 'angles': [0.0, 0.0, float(np.pi/2)],
            'law': [float((np.sqrt(3)-1)/2)] * 2 + [float(2-np.sqrt(3))],
            'source': 'analytic duplicated-pair construction'}
    cases = 0
    angles = np.linspace(0, np.pi, 41)
    for index, theta in enumerate(angles):
        for phi in angles[index:]:
            matrix = np.array([[1, np.cos(theta), np.cos(phi)], [0, np.sin(theta), np.sin(phi)]])
            gram = matrix.T @ matrix
            values = np.linalg.eigvalsh(diagonals-gram)[:, -1]
            winner = int(np.argmin(values))
            if values[winner] < best['value']:
                best = {'value': float(values[winner]), 'angles': [0.0, float(theta), float(phi)],
                        'law': laws[winner].tolist(), 'source': 'finite grid'}
            cases += len(laws)
    return {'evaluations': cases, 'conjectured_minimum': float(candidate), 'best': best,
            'counterexample_found': bool(best['value'] < candidate - 1e-9)}


if __name__ == '__main__':
    print(json.dumps({'python': platform.python_version(), 'numpy': np.__version__,
                      'seed': 20260906, 'fixed_energy': fixed_energy_attacks(),
                      'rank_two': rank_two_three_column_attack(),
                      'boundary': 'Finite floating-point counterexample search; not a proof.'}, indent=2))
