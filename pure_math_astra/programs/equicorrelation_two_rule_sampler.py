# equicorrelation_two_rule_sampler.py — exact integer realization and finite audit of the two-rule mathematical sampler; depends on no repository modules.

"""Research sampler for x_i = a_i / 2**b; return B_i with Y_i = B_i / 2**(b+1)."""

from fractions import Fraction
from itertools import combinations, product
import json
from pathlib import Path


PAIRS = tuple(combinations(range(4), 2))


def uniform_integer(bound, getbits):
    """Draw uniformly below bound from independent uniform getbits(k) calls."""
    if bound < 1:
        raise ValueError("The integer sampling bound must be positive.")
    width = (bound - 1).bit_length()
    if width == 0:
        return 0
    while True:
        candidate = getbits(width)
        if candidate < bound:
            return candidate


def selected_rule(numerators):
    """Select the proved 5/3 rule without dividing the query coordinates."""
    total = sum(numerators)
    square_norm = sum(value * value for value in numerators)
    if square_norm == 0:
        return "zero"
    return "uniform_pair" if 3 * total * total >= 4 * square_norm else "sign_flow"


def pair_output(numerators, pair):
    first, second = pair
    total = sum(numerators)
    output = [0] * 4
    output[first] = total + 3 * (numerators[first] - numerators[second])
    output[second] = 2 * total - output[first]
    return tuple(output)


def weighted_coordinate(weights, randbelow):
    """Assign each integer ticket to a coordinate with its stated weight."""
    ticket = randbelow(sum(weights))
    for index, weight in enumerate(weights):
        if ticket < weight:
            return index
        ticket -= weight
    raise ValueError("The integer sampler returned a ticket outside its bound.")


def sample_block(numerators, randbelow):
    """Sample doubled-scale integer coefficients using exact uniform tickets."""
    if len(numerators) != 4:
        raise ValueError("The sampler requires exactly four query numerators.")
    if any(type(value) is not int for value in numerators):
        raise TypeError("Every query numerator must be a Python integer.")
    rule = selected_rule(numerators)
    if rule == "zero":
        return (0, 0, 0, 0)
    if rule == "uniform_pair":
        return pair_output(numerators, PAIRS[randbelow(6)])
    output = [0] * 4
    for sign in (1, -1):
        weights = tuple(max(sign * value, 0) for value in numerators)
        mass = sum(weights)
        if mass:
            index = weighted_coordinate(weights, randbelow)
            output[index] = 2 * sign * mass
    return tuple(output)


def exact_outcomes(numerators, rule):
    """Enumerate a rule's complete finite distribution for the exact audit."""
    if rule == "zero":
        return [(Fraction(1), (0, 0, 0, 0))]
    if rule == "uniform_pair":
        return [(Fraction(1, 6), pair_output(numerators, pair)) for pair in PAIRS]
    groups = []
    for sign in (1, -1):
        weights = [(index, sign * value) for index, value in enumerate(numerators)
                   if sign * value > 0]
        mass = sum(weight for _, weight in weights)
        groups.append([(Fraction(weight, mass), index, 2 * sign * mass)
                       for index, weight in weights] if mass else [(Fraction(1), None, 0)])
    outcomes = []
    for positive, negative in product(*groups):
        output = [0] * 4
        for _, index, value in (positive, negative):
            if index is not None:
                output[index] = value
        outcomes.append((positive[0] * negative[0], tuple(output)))
    return outcomes


def expected_uniform_bits(bound):
    """Exact expected fair-bit count for the stated rejection sampler."""
    width = (bound - 1).bit_length()
    return Fraction(width * (1 << width), bound)


def audit():
    counts = {"zero": 0, "uniform_pair": 0, "sign_flow": 0}
    largest_ratio = Fraction(0)
    largest_bits = Fraction(0)
    witness = None
    for numerators in product(range(-3, 4), repeat=4):
        total = sum(numerators)
        square_norm = sum(value * value for value in numerators)
        positive = sum(max(value, 0) for value in numerators)
        negative = sum(max(-value, 0) for value in numerators)
        rule = selected_rule(numerators)
        counts[rule] += 1
        for tested_rule in ("uniform_pair", "sign_flow"):
            outcomes = exact_outcomes(numerators, tested_rule)
            assert sum(probability for probability, _ in outcomes) == 1
            mean = [sum(probability * output[i] for probability, output in outcomes)
                    for i in range(4)]
            assert mean == [2 * value for value in numerators]
            for _, output in outcomes:
                assert sum(value != 0 for value in output) <= 2
                assert sum(output) == 2 * total
                assert max(map(abs, output)) <= 8 * max(map(abs, numerators))
            risk = sum(probability * sum(Fraction(output[i] - 2 * numerators[i], 2)**2
                                         for i in range(4))
                       for probability, output in outcomes)
            expected = (2 * square_norm - Fraction(total * total, 4)
                        if tested_rule == "uniform_pair"
                        else positive * positive + negative * negative - square_norm)
            assert risk == expected
            if tested_rule == rule and square_norm:
                assert risk <= Fraction(5, 3) * square_norm
                ratio = risk / square_norm
                if ratio > largest_ratio:
                    largest_ratio, witness = ratio, numerators
        if rule == "uniform_pair":
            bits = expected_uniform_bits(6)
            for ticket in range(6):
                output = sample_block(numerators, lambda bound, ticket=ticket: ticket)
                assert output == pair_output(numerators, PAIRS[ticket])
        elif rule == "sign_flow":
            bits = sum(expected_uniform_bits(mass) for mass in (positive, negative) if mass)
            realized = {}
            for tickets in product(range(positive or 1), range(negative or 1)):
                used = iter(ticket for ticket, mass in zip(tickets, (positive, negative)) if mass)
                output = sample_block(numerators, lambda bound: next(used))
                realized[output] = realized.get(output, 0) + 1
            denominator = (positive or 1) * (negative or 1)
            assert {output: Fraction(count, denominator) for output, count in realized.items()} == {
                output: probability for probability, output in exact_outcomes(numerators, rule)}
        else:
            bits = Fraction(0)
            assert sample_block(numerators, lambda bound: 0) == (0, 0, 0, 0)
        largest_bits = max(largest_bits, bits)
    return {
        "scope": "Exact enumeration on integer queries in [-3,3]^4; finite verification, not the general proof.",
        "vectors": sum(counts.values()),
        "selected_rule_counts": counts,
        "largest_selected_risk_ratio": str(largest_ratio),
        "ratio_witness": witness,
        "largest_expected_random_bits_on_grid": str(largest_bits),
        "sampler_source_bytes": Path(__file__).stat().st_size,
        "randomness_contract": "Independent uniform integer tickets, or independent uniform bit blocks with rejection.",
        "native_cassette_execution": "NOT_RUN",
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
