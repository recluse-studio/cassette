# Cross-region totals with bounded interpretation memory

This independently derived refinement applies to the integer remainder representation
\(A_{ij}=h_j+\Delta Q_{ij}+e_{ij}\), \(0\le e_{ij}\le w_j\). It tests whether
relationships between rows can improve relevance without an \(m\times d\) runtime solver.
The operation remains exact source routing or exact integer ReLU, followed by original
weight retrieval. Bound propagation itself is established mathematics; no novelty claim
follows from this construction.

## Compile the cross-region representation

For one coordinate block, retain the row totals \(t_i=\sum_je_{ij}\). Put
\(W=\sum_jw_j\). A row's total already implies

\[
 l_{ij}=\max(0,t_i-W+w_j)\le e_{ij}\le
 v_{ij}=\min(w_j,t_i).
\]

Store each exact column total \(u_j=\sum_ie_{ij}\), and optionally the aggregates
\(L_j=\sum_il_{ij}\), \(V_j=\sum_iv_{ij}\). The aggregates can instead be derived
once per query from resident row totals, using \(O(md)\) arithmetic and \(O(d)\)
temporary accumulators. No original residual row is fetched to obtain them. Storing them
trades that work for resident bits; the cost cannot disappear from both accounts.

Each of \(u_j,L_j,V_j\) lies in \([0,mw_j]\), so direct encoding charges
\(\lceil\log_2(mw_j+1)\rceil\) bits per retained field and column, plus format metadata.
These are sums derived across source rows, not a partial collection of original weights.

## Interpret one row at a time

For the current row, combine its own bounds with every other row's summed bounds:

\[
 a_{ij}=\max(l_{ij},u_j-V_j+v_{ij}),\qquad
 b_{ij}=\min(v_{ij},u_j-L_j+l_{ij}).                              \tag{1}
\]

**Theorem.** The source residual satisfies \(a_{ij}\le e_{ij}\le b_{ij}\).
Its row score is enclosed by the greedy support bounds for

\[
 e_i=a_i+z_i,\quad 0\le z_{ij}\le b_{ij}-a_{ij},\quad
 \sum_jz_{ij}=t_i-\sum_ja_{ij}.                                 \tag{2}
\]

**Proof.** The exact column equality gives
\(e_{ij}=u_j-\sum_{r\ne i}e_{rj}\). Bounding the remaining rows above and below
gives the second terms of (1); intersecting with the row's prior bounds is safe. The
actual source supplies a feasible point, so \(a\le b\) and the remaining total in
(2) lies between zero and the summed capacities. The existing greedy support theorem
therefore bounds the exact row score after adding \(a_i x\). ∎

Every refined interval is contained in its old row-sum interval. The least-index
maximum-lower-bound candidate rule consequently cannot add a candidate, including ties.
For ReLU, a new nonpositive upper bound proves a new exact zero contribution. A failed
bound still causes original source reads; it never substitutes a coarse score.

Sort query coordinates once for the block. Each row forms (1), its shifted total, and
two greedy supports with \(O(d)\) scratch and \(O(d)\) arithmetic after sorting. Row
scores need not be retained simultaneously. The full interpreter has \(O(md)\)
arithmetic plus sorting and source refinement, with \(O(d)\) score-support scratch.
Multi-block use repeats this construction per block. Input, output, packed guide,
verification, source buffers, and normal arithmetic remain additional memory.

## A witness that defeats an unnecessarily expensive solver

Take \(\Delta=4\), \(x=(1,-1)\), \(w=(3,3)\), and

\[
 E=\begin{pmatrix}2&0\\0&3\\3&3\end{pmatrix},\qquad
 Q=\begin{pmatrix}1&0\\0&0\\0&0\end{pmatrix}.
\]

The row totals are \((2,3,6)\), and column totals are \((5,6)\). Independent row sums
give source-score intervals \([2,6],[-3,3],[0,0]\), retaining rows zero and one.
The last row's total forces both its residuals to three. Equation (1) then bounds row
one's first residual by two. Its total is three, so its score is at most one, below
row zero's lower bound of two. The refined candidate set contains only row zero.

A general transportation solver also proves that exclusion. This cheaper construction
already obtains it, so this witness cannot establish an advantage for that solver.
A projected-flow candidate must beat this propagated-box comparator at the same
representation budget and charge its additional working state and arithmetic.

## Reproducible finite stress

This standard-library check enumerates binary residual matrices, coarse offsets, and a
complete signed-query cube. It verifies source containment, interval containment, and
candidate inclusion rather than assuming a reference region label.

```python
from itertools import product
import json

def bounds(capacity, total, query, lower=None):
    lower = lower or (0,) * len(query)
    shift = sum(a * x for a, x in zip(lower, query))
    def support(reverse):
        left, score = total, shift
        for j in sorted(range(len(query)), key=lambda j: query[j], reverse=reverse):
            take = min(left, capacity[j])
            score += take * query[j]
            left -= take
        assert left == 0
        return score
    return support(False), support(True)

def compile_boxes(residual, capacity):
    totals = [sum(row) for row in residual]
    columns = list(map(sum, zip(*residual)))
    whole = sum(capacity)
    lower = [[max(0, total - whole + w) for w in capacity] for total in totals]
    upper = [[min(w, total) for w in capacity] for total in totals]
    lower_sums, upper_sums = list(map(sum, zip(*lower))), list(map(sum, zip(*upper)))
    tightened = []
    for i in range(len(residual)):
        a = [max(lower[i][j], columns[j] - upper_sums[j] + upper[i][j]) for j in range(len(capacity))]
        b = [min(upper[i][j], columns[j] - lower_sums[j] + lower[i][j]) for j in range(len(capacity))]
        assert all(a[j] <= residual[i][j] <= b[j] for j in range(len(capacity)))
        tightened.append((a, [hi - lo for lo, hi in zip(a, b)], totals[i] - sum(a)))
    return totals, tightened

def candidates(intervals):
    k = max(range(len(intervals)), key=lambda i: (intervals[i][0], -i))
    return {i for i, (lo, hi) in enumerate(intervals)
            if i == k or hi > intervals[k][0] or (hi == intervals[k][0] and i < k)}

residual = ((2, 0), (0, 3), (3, 3))
totals, boxes = compile_boxes(residual, (3, 3))
query = (1, -1)
old = [bounds((3, 3), total, query) for total in totals]
new = [bounds(capacity, total, query, a) for a, capacity, total in boxes]
old[0] = tuple(v + 4 for v in old[0])
new[0] = tuple(v + 4 for v in new[0])
assert candidates(old) == {0, 1} and candidates(new) == {0}

row_values = tuple(product((0, 1), repeat=3))
queries = tuple(product((-1, 0, 1), repeat=3))
checks = old_candidates = new_candidates = strict_cases = 0
for residual in product(row_values, repeat=3):
    totals, boxes = compile_boxes(residual, (1, 1, 1))
    for offsets in product((-1, 0, 1), repeat=3):
        for query in queries:
            coarse = [2 * q * sum(query) for q in offsets]
            old = [tuple(c + v for v in bounds((1, 1, 1), t, query)) for c, t in zip(coarse, totals)]
            new = [tuple(c + v for v in bounds(capacity, t, query, a))
                   for c, (a, capacity, t) in zip(coarse, boxes)]
            scores = [c + sum(a * x for a, x in zip(row, query)) for c, row in zip(coarse, residual)]
            winner = max(range(3), key=lambda i: (scores[i], -i))
            before, after = candidates(old), candidates(new)
            assert winner in after and after <= before
            assert all(lo <= score <= hi for (lo, hi), score in zip(new, scores))
            assert all(lo <= nlo <= nhi <= hi for (lo, hi), (nlo, nhi) in zip(old, new))
            checks += 1
            old_candidates += len(before)
            new_candidates += len(after)
            strict_cases += before != after
print(json.dumps(dict(source_query_cases=checks, old_candidate_rows=old_candidates,
                     new_candidate_rows=new_candidates, strictly_smaller_cases=strict_cases), indent=2))
```

This finite comparison gives extra column information to the refined method. It tests
correctness and the value of that information; it is not a same-budget novelty result.

The [saved run](column-sum-results.json) passed 373,248 source-query cases. Total candidate
rows fell from 640,440 to 515,958; 90,438 cases had a strictly smaller set. These are
candidate counts, not drive reads. The fixture is deliberately too small to show a RAM
win: its nine binary residual entries need nine bits, while direct encoding of three row
totals and three column totals needs twelve bits. A complete residual representation is
therefore the stronger memory comparator for this fixture. Larger dimensions do not by
themselves prove that the column totals tighten useful bounds; source structure and the
read/work frontier still decide that question.
