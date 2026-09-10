# adaptive_polar_probe.py — numerical falsification of the four-coordinate adaptive gauge; depends on no repository files.
"""Probe a convex polar problem and a nonconvex query search; neither proves a theorem."""

import argparse
import itertools
import json

import numpy as np


def polar_matrices(gram):
    matrices = []
    for indices in itertools.combinations(range(4), 2):
        block = np.zeros((4, 4))
        block[np.ix_(indices, indices)] = np.linalg.inv(
            gram[np.ix_(indices, indices)]
        )
        matrices.append(block)
    return np.array(matrices)


def support_bounds(matrices, query, initial=None):
    """Return numerical primal/dual bounds for the polar support function."""
    point = np.zeros(4) if initial is None else initial.copy()
    maximum = np.max(np.einsum("i,kij,j->k", point, matrices, point))
    if maximum >= 0.98:
        point *= np.sqrt(0.98 / maximum)
    for barrier in (0.3, 0.03, 0.003, 0.0003, 3e-5, 3e-6, 3e-7, 3e-8, 3e-9):
        for _ in range(65):
            products = matrices @ point
            slack = 1 - products @ point
            gradient = -query + 2 * barrier * np.sum(
                products / slack[:, None], axis=0
            )
            hessian = 2 * barrier * (
                np.sum(matrices / slack[:, None, None], axis=0)
                + 2 * np.einsum(
                    "ki,kj,k->ij", products, products, 1 / slack**2
                )
            )
            direction = np.linalg.solve(hessian, -gradient)
            decrement = -gradient @ direction
            if decrement < 1e-12:
                break
            objective = -query @ point - barrier * np.log(slack).sum()
            step = 1.0
            for _ in range(55):
                candidate = point + step * direction
                next_slack = 1 - np.einsum(
                    "i,kij,j->k", candidate, matrices, candidate
                )
                if np.min(next_slack) > 0:
                    next_objective = (
                        -query @ candidate - barrier * np.log(next_slack).sum()
                    )
                    if next_objective <= objective - 0.01 * step * decrement:
                        break
                step *= 0.5
            else:
                raise ArithmeticError("Polar Newton line search did not converge.")
            point = candidate
    slack = 1 - np.einsum("i,kij,j->k", point, matrices, point)
    multipliers = barrier / slack
    weighted_matrix = np.einsum("k,kij->ij", multipliers, matrices)
    lower = float(query @ point)
    upper = float(
        multipliers.sum()
        + 0.25 * query @ np.linalg.solve(weighted_matrix, query)
    )
    if upper + 1e-10 < lower or np.min(slack) <= 0:
        raise ArithmeticError("Numerical polar bounds failed their consistency check.")
    return lower, upper, point


def query_search(gram, seed=1701, iterations=25):
    """Find a numerical lower witness for Psi; the search supplies no global upper bound."""
    matrices = polar_matrices(gram)
    generator = np.random.default_rng(seed)
    starts = [
        np.array((1.0, *signs)) / 2
        for signs in itertools.product((-1.0, 1.0), repeat=3)
    ]
    starts.extend(generator.normal(size=(4, 4)))
    best = None
    maximum_polar_gap = 0.0
    for initial in starts:
        query = initial / np.linalg.norm(initial)
        lower, upper, polar = support_bounds(matrices, query)
        for _ in range(iterations):
            maximum_polar_gap = max(maximum_polar_gap, upper - lower)
            risk = lower**2 - query @ gram @ query
            if best is None or risk > best["risk_lower_witness"]:
                best = {
                    "risk_lower_witness": float(risk),
                    "risk_at_query_upper": float(upper**2 - query @ gram @ query),
                    "query": query.tolist(),
                }
            gradient = 2 * lower * polar - 2 * gram @ query
            gradient -= query * (query @ gradient)
            if np.linalg.norm(gradient) < 1e-8:
                break
            step = 1.0
            for _ in range(18):
                candidate = query + step * gradient
                candidate /= np.linalg.norm(candidate)
                trial = support_bounds(matrices, candidate, polar)
                trial_risk = trial[0] ** 2 - candidate @ gram @ candidate
                if trial_risk > risk + 1e-10:
                    query = candidate
                    lower, upper, polar = trial
                    break
                step *= 0.5
            else:
                break
    best["maximum_polar_support_gap"] = maximum_polar_gap
    return best


def paired_gram(eta, angle, second_angle=None):
    cosine, sine = np.cos(angle), np.sin(angle)
    rotation = np.array([[cosine, -sine], [sine, cosine]])
    block = rotation @ np.diag([1.0, eta]) @ rotation.T
    gram = np.zeros((4, 4))
    gram[:2, :2] = block
    if second_angle is None:
        gram[2:, 2:] = block
    else:
        cosine, sine = np.cos(second_angle), np.sin(second_angle)
        second_rotation = np.array([[cosine, -sine], [sine, cosine]])
        gram[2:, 2:] = second_rotation @ np.diag([1.0, eta]) @ second_rotation.T
    return gram


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--eta", type=float, default=0.01)
    parser.add_argument("--angles", type=float, nargs="+", default=[0, 0.5, 1])
    parser.add_argument("--iterations", type=int, default=25)
    parser.add_argument("--second-angle-multiple", type=float)
    arguments = parser.parse_args()
    if not 0 < arguments.eta <= 1:
        parser.error("eta must lie in (0,1].")
    water_level = np.sqrt(arguments.eta)
    for multiple in arguments.angles:
        second_angle = (
            None if arguments.second_angle_multiple is None
            else arguments.second_angle_multiple * water_level
        )
        result = query_search(
            paired_gram(arguments.eta, multiple * water_level, second_angle),
            iterations=arguments.iterations,
        )
        result.update(
            eta=arguments.eta,
            angle_over_sqrt_eta=multiple,
            second_angle_over_sqrt_eta=(
                multiple if second_angle is None
                else arguments.second_angle_multiple
            ),
            water_level=float(water_level),
            ratio_lower_witness=result["risk_lower_witness"] / water_level,
            status="NUMERICAL_WITNESS_ONLY",
        )
        print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
