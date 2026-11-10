# Projected transportation certificates for exact external gate routing

A full residual transportation bound can be exact and still ask for an
\(m\)-by-\(d\) mutable flow state. This note contracts every noncompared row
into one bounded aggregate row. The resulting three-row flow gives a safe
pairwise certificate with \(O(d)\) flow scratch. It strictly improves a
propagated box-and-row-sum comparator on a finite source, yet it is a
relaxation of full transportation and a standard min-cost-flow construction.
No novelty claim follows.

## 1. Source contract and existing quotient guide

The external source has integer gate rows \(a_i\in\mathbb Z^d\), arbitrary
external payload records \(P_i\), and the least-index rule

\[
 \nu_A(x)=\min\operatorname*{arg\,max}_i a_i^Tx
 \tag{1}
\]

for an already available integer runtime vector \(x\). After a fixed scalar
phase and column-minimum shift, every finite gate matrix has the form

\[
 a_i=c+\Delta Q_i+e_i,\qquad
 0\leq e_{ij}\leq w_j,
 \tag{2}
\]

where \(c\) is common to all rows and therefore does not affect (1),
\(\Delta\) is a positive integer step, \(Q_i\) is a nonnegative quotient row,
and \(w_j\) is the measured residual span in coordinate \(j\). The canonical
source keeps every \(a_i\) and \(P_i\); this guide does not replace either.

Store the one-block row totals and column totals

\[
 t_i=\sum_j e_{ij},\qquad u_j=\sum_i e_{ij},\qquad
 W=\sum_jw_j,\qquad T=\sum_it_i=\sum_ju_j.
 \tag{3}
\]

The query interpreter uses the guide to rule out gate rows. With several survivors,
it reads their original gate records and chooses by (1); a singleton is already decided.
It then reads the selected original payload. It derives relevance from the available
runtime state and does not use a coarse guide value in the normal payload calculation.

## 2. Row envelopes and a three-row projection

A row with total \(t_r\) has the coordinate bounds

\[
 \ell_{rj}=\max\{0,t_r-(W-w_j)\},\qquad
 v_{rj}=\min\{w_j,t_r\}.
 \tag{4}
\]

They follow because all coordinates other than \(j\) hold at most \(W-w_j\),
and coordinate \(j\) holds no more than either \(w_j\) or the row total.
Precompute their cross-row sums

\[
 L_j=\sum_r\ell_{rj},\qquad V_j=\sum_rv_{rj}.
 \tag{5}
\]

Fix a challenger \(i\) and an anchor \(k\). Combine every row other than
\(i,k\) into an aggregate residual \(z\). The actual aggregate obeys

\[
 \begin{aligned}
 \sum_jz_j&=T-t_i-t_k,\\
 L_j-\ell_{ij}-\ell_{kj}
 &\leq z_j\leq V_j-v_{ij}-v_{kj},\\
 e_{ij}+e_{kj}+z_j&=u_j.
 \end{aligned}
 \tag{6}
\]

The projected pair bound is

\[
 M^{\rm proj}_{ik}(x)=
 \max\sum_jx_j(p_j-q_j),
 \tag{7}
\]

where \(p,q,z\) satisfy (6), \(\sum_jp_j=t_i\),
\(\sum_jq_j=t_k\), and

\[
 \ell_{ij}\leq p_j\leq v_{ij},\qquad
 \ell_{kj}\leq q_j\leq v_{kj}.
 \tag{8}
\]

This is a three-row capacitated transportation problem. After subtracting
lower bounds, a source supplies the three row totals, the three rows connect
to each coordinate with their residual capacities, and coordinates demand
\(u_j\). Give the \(p\) arcs cost \(-x_j\), the \(q\) arcs cost \(+x_j\), and
the aggregate arcs cost zero. Integer capacities and supplies give an integral
optimum, so (7) is an exact integer upper bound for the stated relaxation.

**Theorem 1 — safe projected pair certificate.** For every source satisfying
equations (2)--(5),

\[
 (e_i-e_k)^Tx\leq M^{\rm proj}_{ik}(x).
 \tag{9}
\]

**Proof.** Set \(p=e_i\), \(q=e_k\), and
\(z=\sum_{r\ne i,k}e_r\). Equation (4) holds for every source row, so the
sum of the remaining rows lies within the coordinate bounds in (6). The row
and column equalities follow from (3). Thus the actual triple is feasible in
\(7\), and its objective is bounded by the optimum. \(\square\)

The projection deliberately discards which remaining row contributes to each
coordinate. It can only enlarge the feasible set relative to full
transportation. That loss is the price of reducing mutable flow state.

## 3. Exact filter-and-refine interpreter

Let

\[
 C_{ik}=\Delta(Q_i-Q_k)^Tx.
 \tag{10}
\]

Choose any anchor \(k\); a practical choice is the least row with the largest
safe lower score from a cheaper block, tag, or moment guide. Retain

\[
 S_{\rm proj}(k,x)=\{k\}\cup
 \left\{i\ne k:C_{ik}+M^{\rm proj}_{ik}(x)>0\ \text{or}\
 \bigl(C_{ik}+M^{\rm proj}_{ik}(x)=0\ \text{and}\ i<k\bigr)\right\}.
 \tag{11}
\]

**Theorem 2 — exact routing.** Reading the original gate records in
\(S_{\rm proj}(k,x)\), then applying the source least-index maximum to those
records, returns \(\nu_A(x)\).

**Proof.** By (2), the source score difference from \(i\) to \(k\) equals
\(C_{ik}+(e_i-e_k)^Tx\). Theorem 1 bounds it by
\(C_{ik}+M^{\rm proj}_{ik}(x)\). A row excluded by (11) cannot outscore
\(k\), and it loses equality when its index is larger. A true winner must beat
\(k\) when its index is larger and must tie or beat it when its index is
smaller, so it remains in the retained set. The exact source comparison then
applies precisely the tie rule in (1). \(\square\)

The flow guide never supplies payload weights. Once the exact gate winner is
known, the interpreter reads its canonical payload record, checks its stated
identity and encoding, and passes its original bytes to the normal operation.

## 4. Encoded bits, reads, arithmetic, and invalidation

The projected construction adds the following persistent fields to the
quotient, span, and row-total guide:

\[
 \begin{aligned}
 B_{\rm column}&=\sum_j\left\lceil\log_2(mw_j+1)\right\rceil,
 &\text{for }u_j,\\
 B_{\rm envelope}&=2\sum_j\left\lceil\log_2(mw_j+1)\right\rceil,
 &\text{for }(L_j,V_j).
 \end{aligned}
 \tag{12}
\]

The row totals use
\(m\lceil\log_2(W+1)\rceil\) bits. The envelopes can instead be recomputed
from all \(t_i\) with \(O(md)\) arithmetic and \(O(d)\) scratch; (12) charges
the choice that avoids that repeated work. Dimensions, signed encoding,
\(\Delta\), source gate digest, and physical record layout
remain resident metadata. Phase provenance belongs to the compilation artifact;
the runtime guide verifies its gate digest and does not need the phase.

For each challenger, a generic capacity-scaling or shortest-path min-cost-flow
implementation has three row nodes, \(d\) coordinate nodes, and \(3d\) bounded
row-to-coordinate arcs. It needs \(O(d)\) mutable integer words for capacities,
flows, predecessors, and potentials, rather than \(O(md)\). Its time remains
material: the route runs one exact flow optimization per retained-comparison
candidate. Write this cost as

\[
 O\bigl(m\,\mathrm{MCF}(3d,d+3,T)\bigr),
 \tag{13}
\]

in addition to guide scans. The notation does not hide a new numerical kernel;
it names a standard exact combinatorial optimization subroutine whose eventual
runtime admission would need its own product proof.

The interpreter holds the query, \(O(d)\) flow scratch, quotient score and
bound accumulators, two identifiers, and one source-gate-row buffer. The
asymptotic count is in signed machine words, not bytes: each word must hold the
largest needed signed query coordinate, capacity, supply, cost, potential, or
accumulator. Its bit width is therefore charged from the declared bounds on
\(x\), \(T\), \(w\), and the quotient score. It holds no \(m\)-element survivor
list. After selecting \(k\), it solves (7) for each row and defers reading
\(k\)'s source gate record until another survivor requires an exact comparison.
If \(S_{\rm proj}=\{k\}\), the guide proof selects \(k\) directly and the route
reads zero gate records before reading the one original payload record. If a
packed source gate record spans \(P_G\) physical pages, a non-singleton route
reads at most \(|S_{\rm proj}|P_G\) gate pages and one selected payload record,
before normal-calculation workspace. A gate-row update invalidates
\(Q,w,t,u,L,V\) through the gate digest; a payload-only update is independently
safe only when the gate and payload identities are separately verified.

## 5. A strict improvement over propagated boxes

Before invoking flow, column totals can cheaply tighten each row coordinate to

\[
 a_{rj}=\max\{\ell_{rj},u_j-V_j+v_{rj}\},\qquad
 b_{rj}=\min\{v_{rj},u_j-L_j+\ell_{rj}\}.
 \tag{14}
\]

A greedy bounded-sum support calculation over
\(a_{rj}\leq e_{rj}\leq b_{rj}\) and \(\sum_je_{rj}=t_r\) gives a stronger
per-row interval at \(O(d)\) scratch. It is the fair cheap comparator for
(7), because it already uses the same row totals, column totals, and envelope
metadata.

The flow certificate is strictly sharper on the following finite source. Let

\[
 \Delta=3,\quad x=(-1,1,0),\quad w=(2,2,2),
\]

and let the residual rows and their totals be

\[
 E=\begin{pmatrix}
 1&0&2\\
 0&2&0\\
 2&0&2\\
 0&0&2
 \end{pmatrix},\qquad
 t=(3,2,4,2),\qquad u=(3,2,6).
 \tag{15}
\]

Set \(Q_0=(0,1,0)\) and \(Q_1=Q_2=Q_3=0\). Row 0 and row 1 both have source
score 2, so the least-index rule selects row 0. For rows 0 and 1, (14) remains
the full box \([0,2]^3\); their propagated-box-plus-sum score intervals are
both \([-2,2]\). It therefore retains row 1 after the coarse deficit of
three, because \(-3+2-(-2)=1\).

The projected transportation problem gives
\(M^{\rm proj}_{10}(x)=3\). Hence its exact upper score difference is
\(-3+3=0\), and (11) removes row 1 because its index is larger. The intervals
\([-2,2]\) above are **residual-score** intervals. After the row-0 coarse
score of three, its full-score interval is \([1,5]\), while row 1's full-score
interval remains \([-2,2]\). The point is their pairwise propagated
comparison, not that the displayed residual intervals are full source scores.

For the full four-row gate, the projected upper source-score differences from
row 0 for rows \(0,1,2,3\) are \((0,0,1,0)\). Thus
\(S_{\rm proj}=\{0,2\}\). The propagated-box route retains
\(\{0,1,2,3\}\), so this instance reduces exact gate-record reads from four
to two, while both routes read the same one original payload record. It does
not form a singleton and does not avoid all gate reads. This is a strict
source-read advantage over the propagated box and row-total method at the same
\(Q,w,t,u,L,V\) fields, paid for by the extra flow arithmetic and scratch.
The improvement comes from enforcing the three rows' column competition
jointly, not from source-specific gate structure supplied by a caller. A
separate pair-sum relaxation may also remove this particular witness with a
cheaper greedy calculation; this witness proves a gap over propagated boxes,
not that a full flow solve is necessary for every strict gain.

## 6. The contraction is not full transportation

The same aggregation can be loose. Let \(w=(1,1,1,1)\),
\(x=(1,-1,1,-1)\), and

\[
 E=\begin{pmatrix}
 0&0&0&0\\
 0&0&1&1\\
 0&1&0&0\\
 1&1&0&1
 \end{pmatrix},\qquad
 t=(0,2,1,3),\qquad u=(1,2,1,2).
 \tag{16}
\]

For challenger 1 and anchor 0, exact full transportation has maximum residual
difference zero. The projected flow allows the aggregate vector
\(z=(0,2,0,2)\) and reports the larger bound two. That vector cannot be split
between the two remaining binary rows of totals one and three: both positive
two entries would force the total-one row to carry at least two units. The
projection therefore retains a row that full transportation would reject.

This counterexample is useful in two directions. It proves that \(O(d)\) flow
scratch was bought by a genuine relaxation, and it prevents a false claim that
the aggregate envelopes somehow encode the whole residual matrix.

## 7. Reproducible finite checks

```python
from itertools import product


def row_bounds(width, totals):
    full = sum(width)
    lower = [[max(0, total - (full - cap)) for cap in width]
             for total in totals]
    upper = [[min(cap, total) for cap in width] for total in totals]
    return lower, upper


def projected(width, totals, columns, challenger, anchor, query):
    lower, upper = row_bounds(width, totals)
    dimension = len(width)
    all_lower = [sum(row[j] for row in lower) for j in range(dimension)]
    all_upper = [sum(row[j] for row in upper) for j in range(dimension)]
    triples = []
    for p in product(*[range(lower[challenger][j], upper[challenger][j] + 1)
                       for j in range(dimension)]):
        if sum(p) != totals[challenger]:
            continue
        for q in product(*[range(lower[anchor][j], upper[anchor][j] + 1)
                           for j in range(dimension)]):
            if sum(q) != totals[anchor]:
                continue
            z = tuple(columns[j] - p[j] - q[j] for j in range(dimension))
            if sum(z) != sum(totals) - totals[challenger] - totals[anchor]:
                continue
            if all(all_lower[j] - lower[challenger][j] - lower[anchor][j]
                   <= z[j]
                   <= all_upper[j] - upper[challenger][j] - upper[anchor][j]
                   for j in range(dimension)):
                triples.append((p, q, z))
    return max(sum((p[j] - q[j]) * query[j] for j in range(dimension))
               for p, q, _ in triples)

def propagated_box(width, totals, columns, row):
    lower, upper = row_bounds(width, totals)
    all_lower = [sum(values[j] for values in lower) for j in range(len(width))]
    all_upper = [sum(values[j] for values in upper) for j in range(len(width))]
    return (tuple(max(lower[row][j], columns[j] - all_upper[j] + upper[row][j])
                  for j in range(len(width))),
            tuple(min(upper[row][j], columns[j] - all_lower[j] + lower[row][j])
                  for j in range(len(width))))


def bounded_support(lower, upper, total, query):
    values = [sum(entry * weight for entry, weight in zip(row, query))
              for row in product(*[range(lo, hi + 1) for lo, hi in zip(lower, upper)])
              if sum(row) == total]
    return min(values), max(values)


# Equation (15): projected flow removes row 1 after a three-point coarse loss.
width = (2, 2, 2)
totals = (3, 2, 4, 2)
columns = (3, 2, 6)
query = (-1, 1, 0)
assert propagated_box(width, totals, columns, 0) == ((0, 0, 0), (2, 2, 2))
assert propagated_box(width, totals, columns, 1) == ((0, 0, 0), (2, 2, 2))
assert bounded_support((0, 0, 0), (2, 2, 2), 3, query) == (-2, 2)
assert bounded_support((0, 0, 0), (2, 2, 2), 2, query) == (-2, 2)
assert projected(width, totals, columns, 1, 0, query) == 3
coarse_deficit = (0, -3, -3, -3)
projected_difference = tuple(
    0 if row == 0 else coarse_deficit[row] + projected(width, totals, columns, row, 0, query)
    for row in range(4))
cheap_interval = [bounded_support(*propagated_box(width, totals, columns, row),
                                  totals[row], query)
                  for row in range(4)]
cheap_survivors = {row for row in range(4)
                   if cheap_interval[row][1] - 3 > cheap_interval[0][0]}
projected_survivors = {0, 2}
assert projected_difference == (0, 0, 1, 0)
assert cheap_survivors == {0, 1, 2, 3} and projected_survivors == {0, 2}
residual = ((1, 0, 2), (0, 2, 0), (2, 0, 2), (0, 0, 2))
quotient = ((0, 1, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0))
assert tuple(3 * sum(q * x for q, x in zip(row, query)) +
             sum(e * x for e, x in zip(residual[index], query))
             for index, row in enumerate(quotient)) == (2, 2, -2, 0)

# Equation (16): aggregate projection is strictly looser than full transport.
width = (1, 1, 1, 1)
totals = (0, 2, 1, 3)
columns = (1, 2, 1, 2)
rows = tuple(product(range(2), repeat=4))
full = [matrix for matrix in product(rows, repeat=4)
        if tuple(map(sum, matrix)) == totals
        and tuple(sum(row[j] for row in matrix) for j in range(4)) == columns]
full_bound = max(sum((matrix[1][j] - matrix[0][j]) * (1, -1, 1, -1)[j]
                     for j in range(4)) for matrix in full)
projected_bound = projected(width, totals, columns, 1, 0, (1, -1, 1, -1))
assert full_bound == 0 and projected_bound == 2
print("PASS: projected flow prunes the strict witness and relaxes full transport")
```

The finite check enumerates and stores every feasible triple and, for the
second witness, every full residual matrix. It verifies the stated optima; it
does **not** implement the \(O(d)\)-word projected-flow solver claimed for
the interpreter. A runtime implementation needs an actual bounded-memory
min-cost-flow algorithm with the word widths charged in Section 4.

## 8. Source challenge and remaining obstacle

The underlying mathematics is ordinary capacitated transportation and
minimum-cost flow. Orlin's [minimum-cost-flow algorithm](https://doi.org/10.1145/42282.214090)
is a direct reminder that the optimization primitive is established. Exact
inner-product filters are also established: [FEXIPRO](https://www4.comp.polyu.edu.hk/~csmlyiu/conf/SIGMOD17_fexipro.pdf)
uses integer approximations as upper bounds before exact scores. This note's
contribution is a bounded derivation and a finite comparison, not a claim that
projecting a transportation polytope is new.

The remaining obstacle is now explicit. The direct projected-flow certificate
beats a fair propagated-box baseline on (15), but its \(O(d)\) scratch comes
with one exact flow optimization per compared row, and it can be looser than
full transportation as (16) shows. The subsequent
[pair-total construction](pair-total-support.md) supplies a cheaper relaxation that
retains the strict four-to-two witness with the same guide fields. One shared query
sort and linear passes replace flow optimization for that relaxation. A separate
example shows that its bound can be weaker; it does not compute (7) exactly in general.
