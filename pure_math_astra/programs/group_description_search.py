# group_description_search.py — finite search for the dense-description approximation ratio; depends on no repository files.
import itertools
import json

import numpy as np


def subset_values(groups, retained):
    totals = np.array([sum(group) for group in groups])
    heads = np.array([max(group) for group in groups])
    imbalances = np.maximum(0, 2 * heads - totals)
    subsets = np.array(list(itertools.combinations(range(len(groups)), retained)))
    selected_totals = totals[subsets]
    selected_imbalances = imbalances[subsets]
    total = selected_totals.sum(axis=1)
    head = heads[subsets].max(axis=1)
    surrogate = np.where(2 * head <= total, total, 2 * np.sqrt(head * (total - head)))
    low, high = np.zeros(len(subsets)), total.copy()
    for _ in range(65):
        middle = (low + high) / 2
        mass = (selected_totals / middle[:, None]
                - selected_imbalances ** 2
                / (middle[:, None] * (middle[:, None] + selected_totals))).sum(axis=1)
        above = mass > 1
        low = np.where(above, middle, low)
        high = np.where(above, high, middle)
    return subsets, surrogate, (low + high) / 2


def search():
    rng = np.random.default_rng(2026090603)
    best = {"ratio": 1.0}
    cases = 0
    for group_count in range(3, 8):
        for retained in range(2, group_count):
            for _ in range(300):
                groups = []
                for _ in range(group_count):
                    entries = int(rng.integers(1, 5))
                    energies = np.exp(rng.uniform(-3, 3, entries))
                    groups.append(energies.tolist())
                subsets, surrogate, exact = subset_values(groups, retained)
                chosen = int(np.argmin(surrogate))
                optimum = int(np.argmin(exact))
                ratio = float(exact[chosen] / exact[optimum])
                if ratio > best["ratio"]:
                    best = {
                        "ratio": ratio, "groups": groups, "retained_groups": retained,
                        "surrogate_choice": subsets[chosen].tolist(),
                        "exact_choice": subsets[optimum].tolist(),
                        "chosen_variance": float(exact[chosen]),
                        "optimal_variance": float(exact[optimum]),
                        "chosen_surrogate": float(surrogate[chosen]),
                        "optimal_variance_surrogate": float(surrogate[optimum]),
                    }
                cases += 1
    return {"seed": 2026090603, "cases": cases, "largest_ratio": best,
            "golden_ratio": float((1 + np.sqrt(5)) / 2),
            "boundary": "Finite floating-point search over orthogonal rank-one groups; not proof of an approximation factor."}


if __name__ == "__main__":
    print(json.dumps(search(), indent=2))

