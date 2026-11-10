# Exact finite checks for signed interpretation

The following standard-library calculation checks every nonzero integer query in
\(\{-2,-1,0,1,2\}^n\) for \(2\le n\le6\). It constructs the actual finite output
law, including the integer implementation of the positive-positive pair selection.
Every probability, mean, second moment, and dual objective uses exact rational arithmetic.

The run on 2026-09-20 passed **19,520 queries**: 13,650 in Case A, 5,650 in Case B,
and 220 in Case C. Every law had total probability one, the exact requested mean and sum,
at most two nonzero coordinates per outcome, and output denominators dividing two. Its
second moment equalled both the proposed formula and the independently evaluated dual bound.

| Dimension | Largest second-moment ratio on this grid | Proved global ratio |
|---|---:|---:|
| 2 | 1 | 1 |
| 3 | 1.833333333333 | 1.842329219213 |
| 4 | 2.5 | 2.605551275464 |
| 5 | 3.3 | 3.319705149025 |
| 6 | 4 | 4 |

The dimension-bound comparison in the final loop uses floating arithmetic; all primal/dual
equalities use `Fraction`. The grid is an algebra check. The proofs in the decoder and
dimension notes establish the quantified statements outside the grid.

```python
from fractions import Fraction as F
from itertools import combinations, product
from math import sqrt


def check_query(query):
    sign = -1 if sum(query) < 0 else 1
    query = tuple(sign * value for value in query)
    size = len(query)
    positive = [i for i, value in enumerate(query) if value > 0]
    negative = [i for i, value in enumerate(query) if value < 0]
    positive_mass = sum(query[i] for i in positive)
    negative_mass = -sum(query[i] for i in negative)
    total = positive_mass - negative_mass
    outcomes = []

    def add_outcome(probability, entries):
        if probability:
            output = [F(0)] * size
            for index, value in entries:
                output[index] = F(value)
            outcomes.append((F(probability), tuple(output)))

    if negative_mass >= F(total, 2):
        case = "A"
        for i in positive:
            for j in negative:
                probability = F(query[i], positive_mass) * F(-query[j], negative_mass)
                add_outcome(probability, [(i, positive_mass), (j, -negative_mass)])
        dual = [2 * positive_mass if value > 0 else
                -2 * negative_mass if value < 0 else 0 for value in query]
        second_moment = F(positive_mass**2 + negative_mass**2)
    elif max(query) <= F(total, 2) + 2 * negative_mass:
        case = "B"
        tickets = {i: max(0, 2 * query[i] - total + 2 * negative_mass)
                   for i in positive}
        remaining = 6 * negative_mass - sum(tickets.values())
        for i in positive:
            extra = min(remaining, 2 * query[i] - tickets[i])
            tickets[i] += extra
            remaining -= extra
        assert remaining == 0
        if negative_mass:
            for i in positive:
                for j in negative:
                    probability = (F(2 * negative_mass, total)
                                   * F(tickets[i], 6 * negative_mass)
                                   * F(-query[j], negative_mass))
                    add_outcome(probability, [(i, F(3 * total, 2)), (j, F(-total, 2))])
        half_length = total - 2 * negative_mass
        intervals = []
        endpoint = 0
        for i in positive:
            length = 2 * query[i] - tickets[i]
            intervals.append((i, endpoint, endpoint + length))
            endpoint += length
        assert endpoint == 2 * half_length
        for ticket in range(half_length):
            pair = [next(i for i, lower, upper in intervals if lower <= point < upper)
                    for point in (ticket, ticket + half_length)]
            assert pair[0] != pair[1]
            add_outcome(F(1, total), [(i, F(total, 2)) for i in pair])
        dual = [-4 * total if value < 0 else 0 for value in query]
        second_moment = F(total**2, 2) + 4 * total * negative_mass
    else:
        case = "C"
        anchor = max(positive, key=lambda i: query[i])
        largest = query[anchor]
        other_mass = positive_mass + negative_mass - largest
        if other_mass == 0:
            add_outcome(1, [(anchor, largest)])
            dual = [2 * total if i == anchor else 0 for i in range(size)]
        else:
            for j, value in enumerate(query):
                if j != anchor and value:
                    coefficient = other_mass if value > 0 else -other_mass
                    add_outcome(F(abs(value), other_mass),
                                [(j, coefficient), (anchor, total - coefficient)])
            dual = [0 if i == anchor else
                    -2 * total - 4 * other_mass if value < 0 else
                    -2 * total + 4 * other_mass for i, value in enumerate(query)]
        second_moment = F(2 * total * largest - total**2 + 2 * other_mass**2)

    assert sum(probability for probability, _ in outcomes) == 1
    mean = [sum(probability * output[i] for probability, output in outcomes)
            for i in range(size)]
    assert mean == list(query)
    for _, output in outcomes:
        assert sum(value != 0 for value in output) <= 2
        assert sum(output) == total
        assert all((2 * value).denominator == 1 for value in output)
    actual = sum(probability * sum(value**2 for value in output)
                 for probability, output in outcomes)
    pair_bound = max(F(total * (dual[i] + dual[j]), 2) - F(total**2, 2)
                     + F((dual[i] - dual[j])**2, 8)
                     for i, j in combinations(range(size), 2))
    lower_bound = sum(value * multiplier for value, multiplier in zip(query, dual)) - pair_bound
    assert actual == second_moment == lower_bound
    return case, float(second_moment / sum(value**2 for value in query))


counts = {case: 0 for case in "ABC"}
checked = 0
for size in range(2, 7):
    bound = max((size - 8 * count + sqrt(size**2 + 48 * size * count)) / 4
                for count in range(size // 2 + 1))
    largest_ratio = 0
    for query in product(range(-2, 3), repeat=size):
        if not any(query):
            continue
        case, ratio = check_query(query)
        counts[case] += 1
        checked += 1
        largest_ratio = max(largest_ratio, ratio)
        assert ratio <= bound + 1e-12
    print(size, largest_ratio, bound)
print(checked, counts)
```

## Exhaustive comparison on one shared finite query format

The second calculation fixes spectral column norms squared to \((16,1,1,1)\), sets
\(Q=I\), and checks all **83,520** nonzero queries in \(\{-8,\ldots,8\}^4\). Both
methods receive the same integer query. The coupled method applies the exact half-integer
Hadamard transform; its output coefficients require at most one further fractional bit.
The source record format must accommodate both encoded bases, as specified in the joint
construction. For the concrete source \(C=\operatorname{diag}(4,1,1,1)\), both \(C\)
and \(B=CH\) fit an eight-bit signed fixed-point scalar with one fractional bit. Each
alternative stores four equally sized column records and fetches at most two.

| Interpreter | Exact largest normalized squared error | A query attaining it |
|---|---:|---|
| Fully optimized spectral-column law | \(376/217\) | \((-5,-8,-8,-8)\) |
| Coupled pages and exact signed-balance law | \(69/43\) | \((-8,-6,-6,6)\) |

The exact reduction in the largest error on this shared finite set is
\(1195/16168\), approximately **7.391143%**. Every permitted spectral-column law is covered
by the pointwise optimum used here. The finite query enumeration exhausts this specified
set; it does not exhaust source matrices or representation schemes. The corresponding
real-query theorem gives approximately 7.350379%, since its two extrema need not occur on
this finite grid.

```python
from fractions import Fraction as F
from itertools import product

hadamard_signs = ((1, 1, 1, 1), (1, -1, 1, -1),
                  (1, 1, -1, -1), (1, -1, -1, 1))


def signed_second_moment(query):
    if sum(query) < 0:
        query = tuple(-value for value in query)
    positive_mass = sum(value for value in query if value > 0)
    negative_mass = -sum(value for value in query if value < 0)
    total = positive_mass - negative_mass
    largest = max(query)
    other_mass = positive_mass + negative_mass - largest
    if 2 * negative_mass >= total:
        return positive_mass**2 + negative_mass**2
    if 2 * largest <= total + 4 * negative_mass:
        return F(total**2, 2) + 4 * total * negative_mass
    return 2 * total * largest - total**2 + 2 * other_mass**2


peaks = {name: (F(-1), None) for name in ("spectral", "coupled")}
checked = 0
for query in product(range(-8, 9), repeat=4):
    squared_norm = sum(value**2 for value in query)
    if squared_norm == 0:
        continue
    masses = sorted((4 * abs(query[0]), abs(query[1]), abs(query[2]), abs(query[3])),
                    reverse=True)
    if masses[0] >= sum(masses[1:]):
        spectral_risk = F(sum(masses[1:])**2 - sum(value**2 for value in masses[1:]))
    else:
        spectral_risk = F(sum(masses)**2, 2) - sum(value**2 for value in masses)
    transformed = tuple(F(sum(coefficient * value for coefficient, value in zip(row, query)), 2)
                        for row in hadamard_signs)
    coupled_risk = signed_second_moment(transformed) - squared_norm
    for name, risk in (("spectral", spectral_risk), ("coupled", coupled_risk)):
        ratio = F(risk, squared_norm)
        if ratio > peaks[name][0]:
            peaks[name] = (ratio, query)
    checked += 1
assert checked == 83520
assert peaks["spectral"][0] == F(376, 217)
assert peaks["coupled"][0] == F(69, 43)
improvement = 1 - peaks["coupled"][0] / peaks["spectral"][0]
assert improvement == F(1195, 16168)
print(checked, peaks, improvement)
```
