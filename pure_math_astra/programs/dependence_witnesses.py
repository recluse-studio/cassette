# dependence_witnesses.py — exact checks of finite sampling witnesses; no repository imports.
from fractions import Fraction as F
from itertools import combinations
import json
from pathlib import Path


def moments(law, q, s):
    assert sum(law.values()) == 1
    assert all(len(subset) == s and mass > 0 for subset, mass in law.items())
    marginal = [sum(mass for subset, mass in law.items() if i in subset)
                for i in range(q)]
    pair = {(i, j): sum(mass for subset, mass in law.items()
                        if i in subset and j in subset)
            for i, j in combinations(range(q), 2)}
    covariance = {(i, j): value - marginal[i] * marginal[j]
                  for (i, j), value in pair.items()}
    return marginal, pair, covariance


def determinant(matrix):
    rows = [[F(value) for value in row] for row in matrix]
    result = F(1)
    for column in range(len(rows)):
        pivot = next((i for i in range(column, len(rows))
                      if rows[i][column]), None)
        if pivot is None:
            return F(0)
        if pivot != column:
            rows[pivot], rows[column] = rows[column], rows[pivot]
            result = -result
        pivot_value = rows[column][column]
        result *= pivot_value
        rows[column] = [value / pivot_value for value in rows[column]]
        for i in range(column + 1, len(rows)):
            factor = rows[i][column]
            rows[i] = [left - factor * right
                       for left, right in zip(rows[i], rows[column])]
    return result


def two_block_witness():
    weighted = {
        (0, 1, 3): 3, (0, 1, 4): 3, (0, 1, 5): 2,
        (0, 2, 3): 1, (1, 2, 4): 1, (0, 2, 4): 2,
        (1, 2, 3): 2, (0, 2, 5): 3, (1, 2, 5): 3,
        (0, 4, 5): 1, (1, 3, 5): 1, (2, 3, 4): 3,
    }
    law = {subset: F(weight, 25) for subset, weight in weighted.items()}
    marginal, pair, covariance = moments(law, 6, 3)
    assert marginal == [F(3, 5)] * 3 + [F(2, 5)] * 3
    defects = {(i, j): covariance[i, j]
               for i in range(3) for j in range(3, 6)
               if covariance[i, j]}
    assert defects == {(0, 3): F(-2, 25), (1, 4): F(-2, 25)}
    return {"outcomes": len(law), "denominator": 25,
            "cross_covariance": {str(key): str(value)
                                 for key, value in defects.items()}}


def seven_cycle_witness():
    representatives = [(0, 1, 2), (0, 1, 3), (0, 1, 4),
                       (0, 1, 5), (0, 2, 4)]
    orbit_mass = [F(1, 35), F(3, 70), F(11, 35), F(1, 70), F(3, 5)]
    law = {}
    for subset, mass in zip(representatives, orbit_mass):
        for shift in range(7):
            rotated = tuple(sorted((i + shift) % 7 for i in subset))
            assert rotated not in law
            law[rotated] = mass / 7
    marginal, pair, covariance = moments(law, 7, 3)
    assert len(law) == 35
    assert marginal == [F(3, 7)] * 7
    cycle_edges = {tuple(sorted((i, (i + 1) % 7))) for i in range(7)}
    assert all(value == (F(-6, 49) if edge in cycle_edges else 0)
               for edge, value in covariance.items())

    selected = ["012", "013", "014", "015", "016", "023", "024",
                "025", "026", "034", "035", "036", "045", "046",
                "056", "123", "124", "125", "126", "134", "234"]
    columns = [tuple(int(i) for i in text) for text in selected]
    noncycle_pairs = sorted(set(pair) - cycle_edges)
    matrix = [[1 for subset in columns]]
    matrix.extend([[int(i in subset) for subset in columns] for i in range(6)])
    matrix.extend([[int(i in subset and j in subset) for subset in columns]
                   for i, j in noncycle_pairs])
    minor = determinant(matrix)
    assert abs(minor) == 1
    return {"outcomes": len(law), "smallest_probability": str(min(law.values())),
            "cycle_covariance": "-6/49", "other_covariances": "0",
            "incidence_minor_size": len(matrix),
            "incidence_minor_determinant": str(minor)}


def five_cycle_witness():
    marginal_target = [F(38, 100), F(39, 100), F(40, 100),
                       F(41, 100), F(42, 100)]
    variance = [p * (1 - p) for p in marginal_target]
    edge_weight = [sum((-1) ** offset * variance[(i - offset) % 5]
                       for offset in range(5)) / 2 for i in range(5)]
    law = {}
    edge_map = {tuple(sorted((i, (i + 1) % 5))): edge_weight[i]
                for i in range(5)}
    for i, j in combinations(range(5), 2):
        law[i, j] = marginal_target[i] * marginal_target[j] - edge_map.get((i, j), 0)
    marginal, pair, covariance = moments(law, 5, 2)
    assert marginal == marginal_target
    assert all(value == -edge_map.get(edge, 0)
               for edge, value in covariance.items())
    assert sum(bool(value) for value in covariance.values()) == 5
    assert all(marginal[i] + marginal[j] != 1
               for i, j in combinations(range(5), 2))
    return {"marginals": [str(value) for value in marginal],
            "outcomes": len(law), "covariance_support": 5,
            "smallest_probability": str(min(law.values()))}


if __name__ == "__main__":
    report = {
        "arithmetic": "exact rational; no floating-point tolerance",
        "scope": "finite witness verification, not a general theorem or production test",
        "two_block": two_block_witness(),
        "five_cycle": five_cycle_witness(),
        "seven_cycle": seven_cycle_witness(),
    }
    target = Path(__file__).resolve().parents[1] / "notes" / "dependence-witness-checks.json"
    target.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
