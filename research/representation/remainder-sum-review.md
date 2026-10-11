# Review and pair-overlap refinement for remainder-sum certificates

**Status.** The reviewed sum certificate is correct under its stated integer
model. Its independent row intervals discard a second kind of source
information: two residual rows can occupy the same coordinates. For binary
remainders, one overlap count per candidate row and block restores a useful
piece of that correlation. The resulting filter remains a classical
transportation-support bound, not a claim of new mathematics.

## 1. Independent review of the existing certificate

Write one block's feasible residual set as

\[
 \mathcal F_b(t)=\left\{z\in\mathbb Z^{B_b}:
 0\le z_j\le w_j,\ \sum_{j\in B_b}z_j=t\right\}.
 \tag{R1}
\]

The greedy proof for the reviewed \(U_{ib}\) is sound. If a feasible vector
puts positive mass on a coordinate with smaller \(x_j\), while a coordinate
with larger \(x_j\) has unused capacity, an integral transfer weakly improves
the objective. Repeating the transfer reaches descending greedy fill; equality
of query coordinates only creates several optimal fills. The ascending proof
for \(L_{ib}\) is the same. Thus the support bounds are tight for the
information retained in (R1), though their extremizers can differ from the
source residual.

The candidate containment claim is also sound. Let \(k\) be the least index
maximizing \(\ell_i\). For any excluded row \(i\), either
\(u_i<\ell_k\), which rules out a source win because
\(s_i\le u_i<\ell_k\le s_k\), or \(u_i=\ell_k\) and \(i>k\). In the second
case \(s_i\le s_k\), and the source's least-index tie rule favors \(k\).

Refinement requires a little more care than the reviewed prose gives, but the
claim survives it. A refined block partition imposes the old block-total
constraint plus new child totals, so its feasible set is a subset of the old
one. Hence \(\ell'_i\ge\ell_i\) and \(u'_i\le u_i\). If a row was excluded
strictly, it remains below every new anchor because
\(\ell'_{k'}\ge\ell'_k\ge\ell_k\). If it was excluded only by equality, then
\(u_i=\ell_k\) and \(i>k\). Either the new anchor exceeds \(\ell_k\), which
excludes the row strictly, or it equals \(\ell_k\). In the latter case row
\(k\) still attains that value, so the least new anchor has \(k'\le k<i\);
the equality exclusion persists. The canonical candidate set therefore cannot
grow, including ties.

The certificate does not hide its source information for free. Construction
must inspect every residual to form the sums, preserve the quotient guide and
common-term convention, retain the block layout, and bind all summaries to the
source identity. At runtime it must charge the sorted-coordinate order,
prefix capacity and weighted-capacity arrays or an equivalent scan, live
bounds, and exact follow-up reads. A reduction in candidate rows does not
necessarily reduce physical page reads. These conditions are stated in the
reviewed note; they remain necessary.

## 2. Exhaustive small-model challenge

The following finite check used binary capacities \(w=(1,1,1)\), three rows,
all residual triples in \(\{0,1\}^3\), quotient values in
\(\{-1,0,1\}^3\), and all queries in \(\{-1,0,1\}^3\). Scores were

\[
 s_i=q_i\sum_jx_j+\sum_je_{ij}x_j.
 \tag{R2}
\]

It checked source-winner containment for the reviewed candidate rule and
candidate inclusion along the partition chain
\(\{012\}\preceq\{0,12\}\preceq\{0,1,2\}\).

~~~python
from itertools import product

residuals = tuple(product((0, 1), repeat=3))
queries = tuple(product((-1, 0, 1), repeat=3))
parts = (((0, 1, 2),), ((0,), (1, 2)), ((0,), (1,), (2,)))

def extrema(total, block, x):
    values = [
        sum(z[k] * x[j] for k, j in enumerate(block))
        for z in product((0, 1), repeat=len(block))
        if sum(z) == total
    ]
    return min(values), max(values)

def candidate(rows, q, partition, x):
    lower, upper = [], []
    for row, qi in zip(rows, q):
        lo = hi = qi * sum(x)
        for block in partition:
            a, b = extrema(sum(row[j] for j in block), block, x)
            lo, hi = lo + a, hi + b
        lower.append(lo)
        upper.append(hi)
    k = max(range(3), key=lambda i: (lower[i], -i))
    return {i for i in range(3)
            if i == k or upper[i] > lower[k]
            or (upper[i] == lower[k] and i < k)}

checked = ties = 0
for rows in product(residuals, repeat=3):
    for q in product((-1, 0, 1), repeat=3):
        for x in queries:
            checked += 1
            score = tuple(qi * sum(x) + sum(a * b for a, b in zip(row, x))
                          for row, qi in zip(rows, q))
            winner = max(range(3), key=lambda i: (score[i], -i))
            ties += sum(s == score[winner] for s in score) > 1
            chain = [candidate(rows, q, part, x) for part in parts]
            assert all(winner in c for c in chain)
            assert chain[1] <= chain[0] and chain[2] <= chain[1]
print(checked, ties)
~~~

The check covered 13,824 sources and 27 queries, hence 373,248 source-query
cases and 746,496 refinement comparisons. It found 133,596 source-score ties,
zero containment failures, and zero monotonicity failures. This finite result
supports the proof; it does not replace it.

## 3. A compact pair-overlap refinement

The following construction specializes to binary residuals
\(e_{ij}\in\{0,1\}\), which is a valid source family under the reviewed
decomposition. Fix source row \(0\) as a permanent reference; its least index
makes its tie behavior convenient. Keep the reviewed block sums

\[
 t_{ib}=\sum_{j\in B_b}e_{ij},
 \tag{R3}
\]

and add, for every \(i>0\), the source-derived overlap count

\[
 c_{ib}=\sum_{j\in B_b}e_{ij}e_{0j}.
 \tag{R4}
\]

No residual coordinate is retained. Given \((t_{ib},t_{0b},c_{ib})\), the
four binary pair-pattern counts in block \(b\) are fixed:

\[
 n_{10}=t_{ib}-c_{ib},\quad
 n_{01}=t_{0b}-c_{ib},\quad
 n_{11}=c_{ib},\quad
 n_{00}=|B_b|-t_{ib}-t_{0b}+c_{ib}.
 \tag{R5}
\]

Let \(x_{b,(1)}\ge\cdots\ge x_{b,(d_b)}\) sort the query coordinates of
the block. The tight support upper bound for the residual score difference is

\[
 D^+_{i0b}(x)=
 \sum_{r=1}^{n_{10}}x_{b,(r)}
 -\sum_{r=d_b-n_{01}+1}^{d_b}x_{b,(r)}.
 \tag{R6}
\]

An empty sum is zero. The lower support bound swaps the top and bottom
segments:

\[
 D^-_{i0b}(x)=
 \sum_{r=d_b-n_{10}+1}^{d_b}x_{b,(r)}
 -\sum_{r=1}^{n_{01}}x_{b,(r)}.
 \tag{R7}
\]

**Theorem 1 — tight binary pair bound.** Equations (R6) and (R7) are the
maximum and minimum of \((e_i-e_0)_{B_b}^{T}x_{B_b}\) over every binary pair
of residual vectors having the summaries (R3)--(R4).

**Proof.** A \(10\) coordinate contributes \(+x_j\), an \(01\) coordinate
contributes \(-x_j\), and \(00\) and \(11\) contribute zero. To maximize,
place the \(n_{10}\) positive coordinates at the largest query coordinates
and the \(n_{01}\) negative coordinates at the smallest. They fit disjointly
because \(n_{10}+n_{01}\le d_b\), a consequence of the nonnegative \(n_{00}\)
and \(n_{11}\) in (R5). Assign \(n_{11}\) remaining coordinates to overlap
and the rest to \(00\). This realizes (R6). The reversed placement realizes
(R7), and the usual exchange argument proves optimality. \(\square\)

The quotient guide's common term cancels in the difference. Define

\[
 V^+_{i0}(x)=\Delta(Q_i-Q_0)x+\sum_bD^+_{i0b}(x).
 \tag{R8}
\]

The reference-pair candidate set is

\[
 C_{\rm pair}(x)=\{0\}\cup\{i>0:V^+_{i0}(x)>0\}.
 \tag{R9}
\]

**Theorem 2 — exact reference-pair filtering.** The source least-index
winner belongs to \(C_{\rm pair}(x)\). Intersecting it with the reviewed
independent-sum candidate set preserves exactness.

**Proof.** If \(i>0\) is excluded, (R8) upper-bounds its true score
difference from row zero by a nonpositive number. It cannot beat row zero,
and row zero wins any equality. Thus an excluded row cannot be the source
winner. Each filter separately contains that winner, so their intersection
does too. Fetching original gate rows for the intersection and applying the
source tie rule is exact. \(\square\)

Refining a block stores child sums and child overlaps that add to parent
values. The child constraints define a subset of the parent pair-feasible set,
so \(D^+_{i0b}\) cannot increase. Therefore \(C_{\rm pair}\), and its
intersection with the independent candidate set, cannot grow under
refinement. Equality causes no special failure here: all nonreference rows
have a larger index than the fixed reference and are excluded whenever their
upper difference is zero. The exhaustive family in Section 2 found zero
reference-pair refinement failures across its 746,496 partition comparisons,
including its 133,596 tied-score cases.

## 4. Improvement, cost, and limits

The independent row summaries allow row \(i\) to put its one residual at the
largest coordinate while row zero puts its one residual at the smallest, even
when the source says they occupy the same coordinate. For a two-coordinate
block with \(x=(1,-1)\) and \(t_i=t_0=c_i=1\), independent
upper-minus-lower reasoning permits a difference of \(2\). The pair summary
gives \(n_{10}=n_{01}=0\) and the exact difference \(0\). If row zero has the
same quotient score, every later row with this summary is discarded without a
gate read.

The extra resident payload is one overlap count per nonreference row and
block. With binary blocks of length \(d_b\), each count uses
\(\lceil\log_2(d_b+1)\rceil\) bits. The reviewed sums use \(m\) such counts
per block; the pair refinement adds \(m-1\). Its packed metadata is almost
twice the independent-sum payload, plus reference identity and layout. It is
not a free correlation.

Sorting a block once and retaining prefix sums of sorted \(x\) gives each pair
support bound in \(O(1)\) after the sort. The interpreter still charges the
sorted order, prefix sums, per-row upper difference, candidate state,
source-row buffers, selected payload, and normal calculation workspace. It
can reduce requested gate rows without reducing a rounded physical page count.
Singleton blocks make the independent sums exact, so pair overlaps add no
selection benefit there.

The same exhaustive family above tested (R9), the independent filter, and
their intersection. For each partition it found zero containment failures in
373,248 source-query cases. The table reports total candidate rows divided by
cases; lower is better.

~~~python
# Run after the preceding exhaustive check.
def pair_upper(row, reference, partition, x):
    result = 0
    for block in partition:
        total = sum(row[j] for j in block)
        reference_total = sum(reference[j] for j in block)
        overlap = sum(row[j] * reference[j] for j in block)
        positive = total - overlap
        negative = reference_total - overlap
        ordered = sorted((x[j] for j in block), reverse=True)
        result += sum(ordered[:positive])
        result -= sum(ordered[len(block) - negative:])
    return result

def pair_candidate(rows, q, partition, x):
    result = {0}
    for i in (1, 2):
        upper = (q[i] - q[0]) * sum(x)
        upper += pair_upper(rows[i], rows[0], partition, x)
        if upper > 0:
            result.add(i)
    return result

totals = [[0, 0, 0] for _ in parts]
for rows in product(residuals, repeat=3):
    for q in product((-1, 0, 1), repeat=3):
        for x in queries:
            score = tuple(qi * sum(x) + sum(a * b for a, b in zip(row, x))
                          for row, qi in zip(rows, q))
            winner = max(range(3), key=lambda i: (score[i], -i))
            for index, partition in enumerate(parts):
                independent = candidate(rows, q, partition, x)
                paired = pair_candidate(rows, q, partition, x)
                intersection = independent & paired
                assert winner in paired and winner in intersection
                totals[index][0] += len(independent)
                totals[index][1] += len(paired)
                totals[index][2] += len(intersection)
assert totals == [
    [709830, 818592, 671292],
    [526848, 714048, 504256],
    [373248, 643776, 373248],
]
~~~

| Partition | Independent | Reference-pair | Intersection | Intersection improvement |
|---|---:|---:|---:|---:|
| \(\{012\}\) | \(709{,}830/373{,}248\) | \(818{,}592/373{,}248\) | \(671{,}292/373{,}248\) | 38,538 fewer rows |
| \(\{0,12\}\) | \(526{,}848/373{,}248\) | \(714{,}048/373{,}248\) | \(504{,}256/373{,}248\) | 22,592 fewer rows |
| \(\{0,1,2\}\) | \(373{,}248/373{,}248\) | \(643{,}776/373{,}248\) | \(373{,}248/373{,}248\) | 0 fewer rows |

The pair filter alone is often weaker because it compares every row only with
row zero. Its value comes from an exact intersection with the independent
filter. The table measures logical candidate rows, not original gate reads, source pages,
elapsed time, or end-to-end RAM. A singleton candidate needs no original gate read.

## 5. Literature collision and remaining gap

The new bound is the support function of a binary contingency-table class:
the overlap fixes the \(00,01,10,11\) margins, and rearrangement assigns the
positive and negative patterns to query order statistics. The relevant
rearrangement principle is classical; see Hardy, Littlewood, and Pólya's
[1926 maximum-bilinear-form paper](https://doi.org/10.1112/plms/s2-25.1.265).
It also belongs beside interval-pruning work such as
[FEXIPRO](https://hub.hku.hk/handle/10722/245443), which uses partial,
integer-bound, and exact-refinement stages for exact inner-product retrieval.

The construction has not shown a better frontier than stronger established
filters, nor an advantage after source-page and total-RAM accounting. Its
retained result is narrower: pair-overlap counts give a proved strictly
smaller exact candidate set on a finite dense binary-residual family, while
their nearly doubled summary payload and reference-only blind spot remain
visible.

## 6. Bounded review of the dense-ReLU operation

I reviewed the current
[dense-ReLU construction](dense-relu-relevance.md), its
[seven-configuration comparison](dense-relu-comparison.md), and its JSON
record. The exact-integer proof is sound within its declared operation. The
common offset \(h\) is retained, as threshold comparison requires; a bound
\(u_i\le0\) correctly proves a zero ReLU activation, including an exact
threshold tie; and every uncertain up-projection row is fetched from the
original source before its activation is decided. A positive activation then
causes the original down-projection column to be fetched and accumulated in
the declared hidden-index order. The guide never replaces a contributing
activation or down-projection weight.

The first review found two accounting omissions. The returned active-index
list was a verification artifact with uncharged growth, and the ordinary
hidden-index accumulation order was implicit. The current construction fixes
both: it identifies the trace as test-only, states its bounded encoded size and
Python-container overhead, and specifies the source order
\(i=0,1,\ldots,m-1\). A packed product interpreter may omit that trace; if it
retains it, the trace belongs in peak RAM.

The present record has seven configurations over 129 inputs and three
dependent layers, for 2,709 exact layer evaluations. Each reported
configuration matches the reference output and active-index trace, while the
byte-verifying reader checks every fetched source range. The streamed
comparator is material: it already reads original up rows, computes exact
ReLU values, and skips original down columns for zero activations. Those
down-column omissions are therefore not credited to the representation.

This review does not extend to floating-point kernels, other activations,
process peak RAM, page-level latency, or a trained model. The current
construction correctly confines its claim to generated dense integer ReLU
fixtures, encoded guide bytes, logical reads, and separately reported
arithmetic work.

## 8. Bounded review of pair-total support

I independently reviewed [pair-total support](pair-total-support.md) and its
saved result. The signed-coordinate formula is correct. For \(x_j\geq0\),
the largest feasible \(p_j\) at a fixed \(s_j=p_j+q_j\) is
\(\min(v_{ij},s_j-\ell_{kj})\), so
\(x_j(p_j-q_j)=|x_j|\min(2v_{ij}-s_j,s_j-2\ell_{kj})\). For
\(x_j<0\), exchanging the two rows gives the stated formula. The two affine
pieces meet at \(v_{\rm favored,j}+\ell_{\rm other,j}\), giving a concave
tent even when the permitted interval clips away either side of that point.

The greedy proof is sound for the stated relaxation. Starting at \(a_j\), the
first available increments have slope \(+|x_j|\) and capacity
\(\max(0,\min(b_j,v_{\rm favored,j}+\ell_{\rm other,j})-a_j)\); the
remaining increments have slope \(-|x_j|\). Visiting every positive segment
in descending \(|x_j|\), then every negative segment in ascending
\(|x_j|\), is a valid nonincreasing marginal-slope allocation. It also
respects a coordinate's precedence. A zero query coordinate has two
zero-slope segments; the prescribed positive pass precedes its negative pass,
so feasibility does not depend on a hidden tie convention. The source pair
is feasible for the retained total, which proves that enough capacity exists.

The one sorted \(|x|\) order can be reused across every anchor--challenger
pair. It costs \(O(d\log d)\) query arithmetic and \(O(d)\) order and segment
scratch, while the per-pair scan costs \(O(d)\). The guide acquires no new
field beyond \(Q,w,t,u,L,V\), but this is not zero information cost: those
fields, their integer widths, their layout, and any work used to recompute
the envelopes remain charged. The stated word bound is not a byte or peak
process-RAM bound.

I reran a stronger exhaustive check over all 19 nonnegative three-entry
column patterns with minimum zero, hence all \(19^3=6{,}859\) normalized
three-row, three-column sources. Across all 27 ternary queries and both
challengers against row zero, the check covered 370,386 source--pair--query
cases. It found zero failures of either greedy equality with exhaustive
pair-total optimization or actual-score containment. This complements the
saved 81,000 containment and 4,050 relaxation-optimality checks; it does not
prove the theorem beyond its algebraic assumptions.

The strict replay is internally consistent: original gate scores
\((2,2,-2,0)\) yield the certified difference bounds \((0,1,0)\), so the
least-index rule retains rows \(\{0,2\}\); reading their original source
records returns the same 18-byte payload and normal product \((1,1,1)\) as
the four-row baseline. The loose witness is equally necessary to the scope:
with residual rows \((0,1),(1,0),(0,0)\), query \((1,1)\), and equal pair
row totals one, the relaxation reaches two whereas projected flow reaches
zero. Thus the result is an exact greedy solver for a pair-total relaxation,
not a replacement for projected transportation and not a same-resource
dominance result. The cited sorted-marginal allocation principle is
established mathematics; novelty of the particular summary/interpreter
combination remains unproved.
