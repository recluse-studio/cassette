# Exact routing with sums of discarded remainders

This construction strengthens [the quotient representation](phase-quotient-routing.md).
It applies to arbitrary integer source gates and recovers original payload weights. It
stores mathematical sums of discarded remainders, then interprets those sums using the
current state. This is a research construction under MATHS section 12, not a runtime change.

## Representation

Use the exact decomposition

\[
a_{ij}=h_j+\Delta Q_{ij}+e_{ij},\qquad 0\le e_{ij}\le w_j.
\]

Partition the coordinate indices into disjoint blocks \(B_1,\ldots,B_g\). In addition to
the quotient guide, store one integer per row and block:

\[
t_{ib}=\sum_{j\in B_b} e_{ij}.                                      \tag{1}
\]

These values are derived sums, not selected entries of the source gate. For a fixed block,
the encoded width is \(\lceil\log_2(1+\sum_{j\in B_b}w_j)\rceil\) bits, with zero bits
when every capacity is zero. The complete additional payload is the sum of these widths
times the number of rows, plus the block layout. Consecutive equal-size blocks require
only a block size and a rule for the final shorter block.

## Interpretation

For query state \(x\), define the exact support extrema permitted by each summary:

\[
U_{ib}(x)=\max\{\sum_{j\in B_b}z_jx_j:0\le z_j\le w_j,
                  \ z_j\in\mathbb Z,\ \sum_jz_j=t_{ib}\},           \tag{2}
\]

and define \(L_{ib}\) by replacing the maximum with a minimum. Compute the maximum by
filling \(t_{ib}\) units into coordinates in descending order of \(x_j\), up to each
capacity \(w_j\). Ascending order gives the minimum. Equal coordinates may use either
order. Negative query coordinates need no special case.

**Theorem 1 — tight summary bounds.** The greedy allocations attain (2) and its minimum.
Consequently the source score, after subtracting the common term \(hx\), lies in

\[
\ell_i=\Delta Q_ix+\sum_b L_{ib}(x),\qquad
u_i=\Delta Q_ix+\sum_b U_{ib}(x).                                 \tag{3}
\]

**Proof.** If an allocation gives positive mass to a smaller query coordinate while a
larger one has unused capacity, transferring their minimum available mass increases or
preserves the objective. Repeating this exchange yields the greedy allocation. Integer
capacities and totals keep every transfer integral. Blocks are independent, so their
extrema add. The actual source remainder satisfies every constraint. Thus (3) encloses
its score. Each extremum is attained by an integer remainder vector compatible with
these per-row summaries. It need not be the source's actual remainder vector. ∎

Take the least-index maximizer \(k\) of \(\ell_i\). Keep \(k\) and every row with
\(u_i>\ell_k\), or with \(u_i=\ell_k\) and \(i<k\). A singleton determines the
source winner. Otherwise read the original gate rows in this set, evaluate their original
scores, and apply the source tie rule. Read the winning original payload afterward.

**Theorem 2 — exact choice.** The candidate set contains the source's least-index maximum
for every integer query state. For an excluded row, its score is below the anchor's lower
bound or can only tie an earlier anchor. Comparing surviving original rows is therefore
exact. This argument requires no closeness assumption about the quotient approximation.

Refining a block partition preserves its old sum by adding the new sums. Therefore each
row's lower bound cannot decrease and its upper bound cannot increase. The canonical
candidate set cannot grow: an already excluded row remains below a new anchor of at least
the old lower bound, with the least-index rule preserving equality exclusions. Extra sums
can only reduce discovery reads under this rule, although their RAM and interpretation
costs grow. Singleton blocks expose every remainder and give exact gate choices without
gate reads. A directly packed, column-centered exact gate is usually a better endpoint.

## Cost and physical interpretation

Sort the query coordinates once per block. The order is shared by every row. Build prefix
capacity and weighted-capacity arrays in that order. A row's total \(t\) then selects a
prefix and at most one partly filled coordinate by binary search. The lower bound uses
the reverse order. This interpretation costs query sorting and bounded prefix arrays,
plus two support lookups per row and block. Those arrays occupy RAM and belong in the
peak. An interpreter can instead scan the sorted coordinates for each row, reducing
temporary arrays while performing more arithmetic. The executable experiment uses this
second route and counts inspected coordinates.

For fixed blocks the format adds two bytes of block size and the packed sum payload. Two
streaming passes find the anchor and refine candidates; an array of all row scores is not
needed. Source-row and selected-payload buffers retain the earlier account. Python object
allocation is not evidence of the packed implementation's peak RAM.

If reads are charged in physical pages, a reduction in requested gate bytes matters only
when it also reduces the pages or requests that must complete. The experiment records
4,096-byte rounded extents as a stated accounting model. That size is an assumption, not
a claim about the user's drive. It separately records requested bytes and unique pages
within one routing operation. Neither count measures external-drive latency.

## Established mathematics and comparison boundary

Greedy support of a bounded vector with a fixed sum is classical continuous/integer
knapsack structure. Interval pruning followed by exact score evaluation is established.
[FEXIPRO, SIGMOD 2017](https://www4.comp.polyu.edu.hk/~csmlyiu/conf/SIGMOD17_fexipro.pdf)
uses scaled integer approximations to bound inner products before exact refinement and
also combines other bounds and transformations. The quotient/sum construction is a
separately derived specialization; it does not establish that filtering with a compressed
integer representation is new, or that it beats FEXIPRO as a whole.

The experiment compares packed exact centered gates, several quotient precisions, both
phase rules, and several block sizes on the same dependent source operations. A frontier
over that finite family is a frontier over that family only. A global novelty or best-known
performance claim requires more evidence.

## Additional second-moment certificate

Also store \(v_{ib}=\sum_{j\in B_b}e_{ij}^2\). For one block with \(n\) coordinates,
let \(S=\sum_jx_j\), \(X_2=\sum_jx_j^2\), and \(R=\sum_je_{ij}x_j\). Centering
both vectors and applying Cauchy–Schwarz gives

\[
 (nR-tS)^2\le(nv-t^2)(nX_2-S^2)=D.                              \tag{4}
\]

Because \(nR-tS\) is an integer, compute \(r=\lfloor\sqrt D\rfloor\) by exact integer
square root. Then

\[
 \left\lceil\frac{tS-r}{n}\right\rceil\le R\le
 \left\lfloor\frac{tS+r}{n}\right\rfloor.                       \tag{5}
\]

Intersect (5) with the greedy interval. The intersection remains sound; it need not equal
the tight support of all vectors satisfying both moments and the box constraints. The
extra encoded payload per row and block uses
\(\lceil\log_2(1+\sum_{j\in B_b}w_j^2)\rceil\) bits. Query sums are shared among
rows; source-dependent sums and squares are charged per row. Integer square roots and
their operands require work and scratch beyond the sum-only interpreter.

This is the classical centered Cauchy–Schwarz bound, included to strengthen the comparison.
The fixture executes it with exact integers, so rounding an inward floating bound cannot
discard a true source winner. For singleton blocks the second moment adds no information.

## Stronger lossless comparator

Singleton sums recover every \(e_{ij}\). Their values and \(Q_{ij}\) can be decoded in
one streaming score pass as \(\Delta Q_{ij}+e_{ij}\), with no sorting, support calculation,
or source-gate read. This exact split representation can use fewer bits than a packed
centered gate if residuals occupy a short interval despite large source differences.
It is ordinary lossless residual coding after factoring out common columns. The experiment
includes that faster exact comparator; singleton sum bounds cannot be presented as an
advantage over it.
