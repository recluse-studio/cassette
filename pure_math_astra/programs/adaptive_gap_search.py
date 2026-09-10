# adaptive_gap_search.py — finite comparison of query-dependent and fixed sampling laws; depends on description_search.py.
import itertools
import json

import numpy as np

from description_search import spectral_bounds


def adaptive_value(matrix):
    gram = matrix.T @ matrix
    roots = np.linalg.norm(matrix, axis=0)
    signs = np.array([(1,) + tail for tail in itertools.product((-1, 1), repeat=len(roots) - 1)])
    vectors = signs * roots
    objectives = vectors[:, :, None] * vectors[:, None, :] - gram
    eigenvalues = np.linalg.eigvalsh(objectives)[:, -1]
    winner = int(np.argmax(eigenvalues))
    return float(eigenvalues[winner]), signs[winner].tolist()


def search():
    rng = np.random.default_rng(2026090604)
    best = {"ratio_upper": 0.0}
    cases = 0
    for columns in range(3, 9):
        for rows in range(1, min(5, columns)):
            for trial in range(20):
                matrix = rng.normal(size=(rows, columns))
                energies = np.exp(rng.uniform(-1, 1, columns))
                if trial % 5 == 0:
                    energies[:] = 1
                matrix *= np.sqrt(energies) / np.linalg.norm(matrix, axis=0)
                matrix /= np.linalg.norm(matrix)
                lower, upper = spectral_bounds(matrix)
                adaptive, signs = adaptive_value(matrix)
                ratio = upper / adaptive
                if ratio > best["ratio_upper"]:
                    best = {"ratio_upper": ratio, "ratio_lower": lower / adaptive,
                            "matrix": matrix.tolist(), "fixed_interval": [lower, upper],
                            "adaptive_value": adaptive, "signs": signs}
                assert adaptive <= upper + 1e-6
                cases += 1
    return {"seed": 2026090604, "cases": cases, "largest_observed_gap": best,
            "rank_one_sharp_ratio": float(3 / (2 * np.sqrt(2))),
            "boundary": "Real-field finite floating-point search; not an exact proof or bound over all matrices."}


if __name__ == "__main__":
    print(json.dumps(search(), indent=2))

