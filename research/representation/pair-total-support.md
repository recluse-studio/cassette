# Joint pair interpretation without a flow solver

This construction follows the strict example in
[projected transportation](projected-transport-representation.md). It retains the same
stored representation but replaces a general flow optimization with sorted integer
arithmetic. It is a new candidate derived in this investigation; its resource-allocation
ingredients are classical, and mathematical originality is not established.

## Derivation

For a challenger and anchor, write their residual rows as \(p,q\). Their known totals
are \(t_i,t_k\), and their coordinate bounds are \(\ell_i,v_i\) and
\(\ell_k,v_k\). All other rows aggregate to \(z\), with bounds

\[
 z_j^- =L_j-\ell_{ij}-\ell_{kj},\qquad
 z_j^+ =V_j-v_{ij}-v_{kj}.
\]

The exact column total gives \(p_j+q_j+z_j=u_j\). Define \(s_j=p_j+q_j\). Then

\[
 a_j=\max(\ell_{ij}+\ell_{kj},u_j-z_j^+)\le s_j\le
 b_j=\min(v_{ij}+v_{kj},u_j-z_j^-),\qquad
 \sum_js_j=t_i+t_k.                                           \tag{1}
\]

For a fixed \(s_j\), maximize \(x_j(p_j-q_j)\) over its feasible split. If
\(x_j\ge0\), the largest feasible \(p_j\) is \(\min(v_{ij},s_j-\ell_{kj})\),
giving

\[
 f_j(s)=|x_j|\min(2v_{ij}-s,s-2\ell_{kj}).                       \tag{2}
\]

For \(x_j<0\), exchange \(i,k\) in (2). Each \(f_j\) is a concave integer
piecewise-linear function: its slope is \(+|x_j|\) up to
\(s=v_{\rm favored,j}+\ell_{\rm other,j}\), then \(-|x_j|\).

Drop only the separate equalities \(\sum_jp_j=t_i\) and \(\sum_jq_j=t_k\),
retaining their sum (1). The resulting bound is

\[
 B_{ik}(x)=\max\{\sum_jf_j(s_j):a_j\le s_j\le b_j,
                  \ s_j\in\mathbb Z,\ \sum_js_j=t_i+t_k\}.     \tag{3}
\]

**Theorem 1 — sound joint support.**
\((e_i-e_k)x\le M^{\rm proj}_{ik}(x)\le B_{ik}(x)\).
The source pair satisfies the projected constraints. Every feasible projected pair
supplies a feasible \(s\) in (1), and its coordinate objective is bounded by (2).
Maximizing after removing separate row-total constraints can only increase that bound.

## Exact greedy interpretation

Start at \(s=a\), with objective \(\sum_jf_j(a_j)\). There are
\(t_i+t_k-\sum_ja_j\) units still to assign. Each coordinate supplies at most two
segments of available increments: a positive-slope segment followed by a negative-slope
segment. Allocate units to the available segments in decreasing slope order.

**Theorem 2 — exact optimum of the relaxation.** This procedure returns (3).
Every segment has an integer capacity and constant slope. The second segment of a
coordinate has no greater slope than its first, so sorting all segments respects their
precedence whenever their values differ. Zero-slope ties can be assigned in either order
because the objective is unchanged; the total assigned to that coordinate still gives a
valid \(s\). An exchange of one unit from a smaller used slope to a larger unused slope
cannot reduce the objective. Repeating exchanges gives exactly the stated allocation.
The source pair guarantees that the required total lies within the summed capacities.

The slope order depends only on \(x\), not on the source or compared rows. Sort
coordinates by \(|x_j|\) once per query. For every pair, visit positive segments in
descending order and negative segments in ascending order. Thus all \(m-1\) challenger
bounds cost \(O(d\log d+md)\) arithmetic, with \(O(d)\) mutable words, beyond the
existing guide scans. Integer widths depend on query magnitude and declared capacities;
these are word counts, not byte counts. The guide fields remain \(Q,w,t,u,L,V\).
Envelopes \(L,V\) may be recomputed instead of stored, with their work charged separately.

Use \(\Delta(Q_i-Q_k)x+B_{ik}(x)\) as an upper source-score difference. Exclude a row
when it is strictly negative, or zero with \(i>k\). Intersect this candidate set with
the cheaper independent candidate set. Uncertain rows are read at source precision;
the exact least-index winner then supplies its original payload to normal calculation.

## Strict example and information lost

For the projected-flow witness, the four source scores are \((2,2,-2,0)\). The
propagated separate-row method retains all four regions. The joint pair-total bound
against row zero is \((0,1,0)\) for the three challengers after adding coarse differences.
It therefore retains only rows zero and two, exactly matching the projected-flow filter
on this example. Both original rows are read to determine the winner; the payload read
is unchanged. This is a strict improvement in interpretation with the same guide fields.
It is not an equal-total-memory or hardware speed claim.

The pair-total relaxation can be weaker than projected flow because it may choose a
split whose separate row totals are wrong. The finite checks below compare its greedy
value with exhaustive pair-total optimization and test actual-source containment. They
do not prove equality with full or projected transportation in general.

For example, take residual rows \((0,1),(1,0),(0,0)\), compare row one to row zero,
and use \(x=(1,1)\). Both compared row totals are one, so their exact and projected
score difference is zero. Pair-total support may assign both available units to row one
and none to row zero, giving the looser upper bound two. The original row-sum filter
already resolves this case. Intersecting the filters retains that stronger conclusion.

## Reproducible finite checks

```python
from itertools import product
from random import Random
from os import pread
from pathlib import Path
from struct import pack, unpack
from tempfile import TemporaryDirectory
import json

def summaries(residual, width):
    totals = tuple(map(sum, residual))
    columns = tuple(map(sum, zip(*residual)))
    whole = sum(width)
    lower = [[max(0, total - whole + w) for w in width] for total in totals]
    upper = [[min(w, total) for w in width] for total in totals]
    return totals, columns, tuple(map(sum, zip(*lower))), tuple(map(sum, zip(*upper)))

def pair_segments(width, totals, columns, all_lower, all_upper, i, k, query):
    whole = sum(width)
    lo_i = [max(0, totals[i] - whole + w) for w in width]
    lo_k = [max(0, totals[k] - whole + w) for w in width]
    hi_i = [min(w, totals[i]) for w in width]
    hi_k = [min(w, totals[k]) for w in width]
    segments = []
    for j, x in enumerate(query):
        a = max(lo_i[j] + lo_k[j], columns[j] - all_upper[j] + hi_i[j] + hi_k[j])
        b = min(hi_i[j] + hi_k[j], columns[j] - all_lower[j] + lo_i[j] + lo_k[j])
        favored, other = (hi_i[j], lo_k[j]) if x >= 0 else (hi_k[j], lo_i[j])
        assert a <= b
        segments.append((a, b, favored, other))
    return segments

def value_at(s, segment, x):
    a, b, favored, other = segment
    return abs(x) * min(2 * favored - s, s - 2 * other)

def pair_bound(width, summary, i, k, query, order):
    totals, columns, all_lower, all_upper = summary
    segments = pair_segments(width, totals, columns, all_lower, all_upper, i, k, query)
    value = sum(value_at(segment[0], segment, x) for segment, x in zip(segments, query))
    left = totals[i] + totals[k] - sum(segment[0] for segment in segments)
    for positive, traversal in ((True, reversed(order)), (False, iter(order))):
        for j in traversal:
            a, b, favored, other = segments[j]
            rising = max(0, min(b, favored + other) - a)
            capacity = rising if positive else b - a - rising
            take = min(left, capacity)
            value += take * abs(query[j]) * (1 if positive else -1)
            left -= take
    assert left == 0
    return value

def exhaustive_pair_total(width, summary, i, k, query):
    totals, columns, all_lower, all_upper = summary
    segments = pair_segments(width, totals, columns, all_lower, all_upper, i, k, query)
    return max(sum(value_at(s, segment, x) for s, segment, x in zip(values, segments, query))
               for values in product(*(range(a, b + 1) for a, b, _, _ in segments))
               if sum(values) == totals[i] + totals[k])

E = ((1, 0, 2), (0, 2, 0), (2, 0, 2), (0, 0, 2))
width, query = (2, 2, 2), (-1, 1, 0)
summary = summaries(E, width)
order = sorted(range(3), key=lambda j: abs(query[j]))
differences = [pair_bound(width, summary, i, 0, query, order) - 3 for i in range(1, 4)]
assert differences == [0, 1, 0]
assert {0} | {i + 1 for i, difference in enumerate(differences) if difference > 0} == {0, 2}

loose = ((0, 1), (1, 0), (0, 0))
assert pair_bound((1, 1), summaries(loose, (1, 1)), 1, 0, (1, 1), (0, 1)) == 2
assert sum(loose[1]) - sum(loose[0]) == 0

generator = Random(2026092103)
checks = 0
for trial in range(1000):
    raw = [[generator.randrange(4) for _ in range(3)] for _ in range(4)]
    minima = list(map(min, zip(*raw)))
    residual = [[value - minima[j] for j, value in enumerate(row)] for row in raw]
    width = tuple(map(max, zip(*residual)))
    summary = summaries(residual, width)
    for query in product((-1, 0, 1), repeat=3):
        order = sorted(range(3), key=lambda j: abs(query[j]))
        for i in range(1, 4):
            bound = pair_bound(width, summary, i, 0, query, order)
            actual = sum((residual[i][j] - residual[0][j]) * query[j] for j in range(3))
            assert actual <= bound
            if trial < 50:
                assert bound == exhaustive_pair_total(width, summary, i, 0, query)
            checks += 1

# The source writer and reference are outside the summary-only bound interpreter.
query = (-1, 1, 0)
source_gate = ((1, 3, 2), (0, 2, 0), (2, 0, 2), (0, 0, 2))
payloads = [pack('<9h', *(i * 9 + j - 17 for j in range(9))) for i in range(4)]
source_bytes = pack('<12h', *(v for row in source_gate for v in row)) + b''.join(payloads)
transcripts = []
with TemporaryDirectory(prefix='cassette-pair-total-') as scratch:
    source_path = Path(scratch) / 'weights.bin'
    source_path.write_bytes(source_bytes)
    for retained in ((0, 1, 2, 3), tuple(sorted({0} | {i + 1 for i, b in enumerate(differences) if b > 0}))):
        exact_scores = []
        with source_path.open('rb') as stream:
            for i in retained:
                raw = pread(stream.fileno(), 6, i * 6)
                assert raw == source_bytes[i * 6:i * 6 + 6]
                exact_scores.append((sum(a * x for a, x in zip(unpack('<3h', raw), query)), -i))
            winner = -max(exact_scores)[1]
            raw_payload = pread(stream.fileno(), 18, 24 + winner * 18)
        assert winner == 0 and raw_payload == payloads[0]
        original = unpack('<9h', raw_payload)
        output = [sum(original[r * 3 + j] * query[j] for j in range(3)) for r in range(3)]
        assert output == [1, 1, 1]
        transcripts.append(dict(gate_indices=list(retained), gate_bytes=len(retained) * 6,
                                payload_bytes=len(raw_payload), output=output))
print(json.dumps(dict(seed=2026092103, actual_source_checks=checks,
                     exhaustive_relaxation_checks=50 * 27 * 3,
                     strict_witness_difference_bounds=differences,
                     original_record_replays=transcripts), indent=2))
```

The Python fence uses an \(O(d)\) segment list and shared query order for the greedy
interpreter. The exhaustive verifier separately enumerates feasible pair totals. Source
matrices belong to the compiler and verifier; the greedy interpreter receives only the
summary fields, indices, and available query. This is an executable interpretation of
the representation, not an implementation of a general flow solver.
The final two replays read original gate and payload bytes from a temporary source file.
They return the same original payload and normal matrix-product result, with gate reads
of 24 and 12 logical bytes respectively. The retained-row lists are explicit fixture
transcripts, not evidence of the streaming interpreter's memory allocation. These tiny
unaligned records provide no physical-drive speed measurement.

## Result and primary-source challenge

The [saved result](pair-total-results.json) records 81,000 actual-source containment
checks and 4,050 exhaustive checks of the relaxed optimum. The strict example keeps the
same two source rows as projected flow, while the loose example disproves general equality.
The [independent review](remainder-sum-review.md#8-bounded-review-of-pair-total-support)
also enumerated 370,386 cases across 6,859 normalized small sources and found no greedy
optimality or source-containment failure. The result applies to the declared relaxation.

Sorting marginal slopes for separable piecewise-linear resource allocation is established;
the primary paper [Resource allocation problems in decentralized energy management](https://link.springer.com/article/10.1007/s00291-017-0474-2)
proves the analogous greedy ordering for convex minimization. Negating the objective gives
the concave maximization principle used here. Thus the greedy theorem is not an originality
claim. The source-field projection and shared query order form the candidate under study.
A finite search cannot certify that their combination is absent from the literature, and
the example does not establish a win over every same-budget established representation.
