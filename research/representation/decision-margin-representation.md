# Exact decision-margin guide for external gate records

A router can discard the part of every gate score that every row shares, then
use a bounded residual span to decide which original gate rows still need a
read. This note proves that construction for arbitrary finite integer gate
matrices. It also records the decisive limitation: a centered scalar interval
index can encode exactly the same quotient and residual span, so the result is
a correct exact interpreter and a strict improvement over row-independent
boxes, but not yet a new representation theorem over the strongest established
comparison class.

## 1. Contract

Let the canonical external source contain a signed (B)-bit integer gate row
(a_i\in\mathbb Z^d) and an arbitrary payload record (P_i), for every
(i\in\{0,\ldots,m-1\}). At runtime an integer vector
(x\in\mathbb Z^d) is already available. The ordinary gate chooses

\[
 \nu_A(x)=\min\operatorname*{arg\,max}_{0\leq i<m} a_i^T x,
 \tag{1}
\]

then reads the original payload (P_{\nu_A(x)}) and gives it to the declared
normal calculation. An affine bias is included by adding a coordinate of
(x) fixed to one. This note proves the gate choice only. It neither derives
(x) from a prompt nor replaces the payload calculation.

The guide has no source row and no table indexed by possible queries. It holds
lossy, source-derived integer coefficients and certificates. If its certificate
cannot exclude a row, the interpreter reads that row at source precision before
making the final choice.

## 2. Quotient code and residual-span certificate

Fix a power-of-two step \(\Delta=2^k\), where \(k\geq1\), and a phase
\(g_j\in\{0,\ldots,\Delta-1\}\) for each coordinate. Write

\[
 a_{ij}=\Delta q_{ij}+g_j+r_{ij},\qquad
 q_{ij}=\left\lfloor\frac{a_{ij}-g_j}{\Delta}\right\rfloor,
 \qquad 0\leq r_{ij}<\Delta .
 \tag{2}
\]

For every coordinate let

\[
 \mu_j=\min_iq_{ij},\qquad Q_{ij}=q_{ij}-\mu_j,
 \qquad w_j=\max_i r_{ij}-\min_i r_{ij}.
 \tag{3}
\]

The resident code consists of the nonnegative matrix \(Q\) and the widths
\(w\); it deliberately omits \(\mu\), \(g\), and the individual residuals.
For every pair of rows,

\[
 a_i^Tx-a_\ell^Tx
 =\Delta(Q_i-Q_\ell)^Tx+(r_i-r_\ell)^Tx.
 \tag{4}
\]

The discarded term
\(\sum_j(\Delta\mu_j+g_j)x_j\) is identical for every row. It is score
information, but it is not ordering information.

For the current query define

\[
 h_i=Q_i^Tx,\qquad
 k_x=\min\operatorname*{arg\,max}_i h_i,
 \qquad E(x)=\sum_{j=1}^d w_j|x_j|.
 \tag{5}
\]

After a scan of the guide, retain the following rows for source-precision
refinement:

\[
 S(x)=\{k_x\}\cup\left\{i:
 D_i<E(x)\ \text{or}\ \bigl(D_i=E(x)\ \text{and}\ i<k_x\bigr)\right\},
 \quad
 D_i=\Delta(h_{k_x}-h_i).
 \tag{6}
\]

The strictness in (6) is the tie rule. It is needed even when every arithmetic
operation is exact.

**Theorem 1 — exact decision-margin refinement.** For every finite integer
matrix (A), every phase, and every integer query (x),
\(\nu_A(x)\in S(x)\). Reading the original gate rows in (S(x)) and applying
(1) to those rows returns \(\nu_A(x)\) exactly.

**Proof.** From (3),

\[
 (r_i-r_{k_x})^Tx\leq\sum_j|r_{ij}-r_{k_xj}|\,|x_j|\leq E(x).
 \tag{7}
\]

Equation (4) therefore gives

\[
 a_i^Tx-a_{k_x}^Tx\leq-D_i+E(x).
 \tag{8}
\]

If \(D_i>E(x)\), row (i) loses strictly. If equality holds, it cannot
outscore (k_x), and it also loses a tie when (i>k_x). Those are precisely
the rows excluded by (6). Conversely, if (i<k_x) is the exact winner, it
must tie or exceed (k_x), so (8) implies \(D_i\leq E(x)\); if (i>k_x) is
the exact winner, it must exceed (k_x), so \(D_i<E(x)\). Thus the exact
winner remains in (S(x)). The final source-precision comparison, with the
same least-index tie rule, returns it. \(\square\)

The bound is minimax sharp for this summary. Given only a pair's (Q) values
and the widths (w), choose the two residual vectors at the opposite stored
endpoints in each coordinate, selecting the endpoint by the sign of (x_j).
Those compatible source rows attain the right side of (7). A smaller uniform
error allowance would reject a possible winner.

## 3. Interpreter, reads, and working state

The source layout separates each fixed-width gate record from its fixed-width
payload record. A query uses two guide scans and one source refinement pass.

1. Scan (Q), calculate (h_i), and retain only \(k_x\) and \(h_{k_x}\).
2. Scan (Q) again. For each (i) satisfying (6), read its original gate
   record, calculate (a_i^Tx), and update the exact least-index maximum.
   No candidate bitset or candidate-row array is required.
3. Read and verify the winning original payload record, then run the ordinary
   payload operation.

If \(|x_j|\leq X_j\), useful exact register widths are

\[
 \begin{aligned}
 b_h&=1+\left\lceil\log_2\left(1+\sum_j H_jX_j\right)\right\rceil,
 &H_j&=\max_iQ_{ij},\\
 b_D&=1+\left\lceil\log_2\left(1+\Delta\sum_jH_jX_j\right)\right\rceil,\\
 b_E&=\left\lceil\log_2\left(1+\sum_jw_jX_j\right)\right\rceil,\\
 b_A&=1+\left\lceil\log_2\left(1+d(2^{B-1}-1)\max_jX_j\right)\right\rceil.
 \end{aligned}
 \tag{9}
\]

The guide requires

\[
 B_{\rm guide}=m\sum_{j=1}^d\left\lceil\log_2(H_j+1)\right\rceil+kd
 \tag{10}
\]

payload bits before its ordinary header, source digest, dimensions, and scalar
format. The first term packs (Q) by coordinate; the second records the
widths. The build manifest additionally charges (kd) phase bits if it must
reconstruct the guide from the source, although phases and \(\mu\) are not
needed by the runtime interpreter.

Besides the resident guide, peak routing RAM comprises the query
\(\sum_j\lceil\log_2(2X_j+1)\rceil\) bits, four accumulators bounded by
(9), two row identifiers, and one (dB)-bit source-gate buffer. It does not
contain (S(x)). The subsequent payload buffer and the normal operation's
workspace must be added to the peak by the payload contract.

With a packed gate record of \(L_G=\lceil dB/8\rceil+u_G\) bytes, including
its stated header, and physical page size \(P\), refinement reads at most
\(|S(x)|\lceil L_G/P\rceil\) pages if every record is separately aligned.
Coalescing adjacent records can only reduce that count. The route then reads
one payload record, whose page count is a separate declared quantity. The
arithmetic count is \(2md+|S(x)|d\) multiply-accumulate terms, plus exact
comparisons and record validation.

A guide is valid only for the gate-component digest from which (2)--(3) were
built. Any gate-row update rejects the old guide before use and requires a
fresh full guide scan; a changed row can alter a column minimum and every
translated code in that column. A payload-only update does not change the
routing theorem if gate and payload identities are separately bound and the
selected payload record is still verified. Binding one whole-source digest is
also correct, but it invalidates more often.

## 4. Choosing phases, then intersecting certificates

For one coordinate, take the distinct residues of the source values modulo
\(\Delta\), order them around a circle of circumference \(\Delta\), and let
\(G_j\) be their largest adjacent circular gap. A phase placed at the endpoint
of that gap attains

\[
 \min_{g_j}w_j=\Delta-G_j.
 \tag{11}
\]

The proof cuts the circular residue set immediately after a largest empty arc.
Every linear presentation has to cover the complement of some circular gap;
the largest gap gives the shortest complement. This is a construction-time
optimum for the width alone.

It is not an optimum for the retained set. For

\[
 A=\begin{pmatrix}2&0\\5&2\\3&0\\-2&4\end{pmatrix},\quad
 \Delta=4,\quad x=(-2,-1),
 \tag{12}
\]

phase \(g=(0,0)\) has coordinate widths \((2,2)\), which minimize their
sum. It produces (E=6), coarse scores \((-2,-4,-2,-1)\), and
\(S=\{0,2,3\}\). Phase \(g=(3,0)\) has the larger widths \((3,2)\), hence
\(E=8\), but coarse scores \((-2,-4,-4,-1)\) and \(S=\{0,3\}\). The
second certificate costs more residual uncertainty and still eliminates one
extra source row because it places more useful separation in the quotient.

This suggests a finite query-conditioned strengthening. Store (L) complete
phase certificates \((Q^{(\ell)},w^{(\ell)})\), derive each
\(S_\ell(x)\) by (6), and refine only

\[
 S_\cap(x)=\bigcap_{\ell=1}^L S_\ell(x).
 \tag{13}
\]

**Proposition 2 — phase-intersection interpreter.** The exact winner belongs
to \(S_\cap(x)\), so exact refinement over the intersection is correct.

**Proof.** Theorem 1 applies independently to every stored phase. The exact
winner belongs to each resulting set, hence to their intersection. \(\square\)

This costs the sum of the (L) guide sizes in (10), plus each width vector and
manifest phase. It still streams the final source records and needs no
candidate set in RAM. It is not a free query-adaptive phase: the phase codes
must have been stored before the query arrives.

A small instance shows the effect. Add the common carrier
\((2^{20},2^{20})\) to every row of

\[
 \begin{pmatrix}-3&4\\2&5\\5&7\\-3&1\\3&-2\end{pmatrix},
 \qquad x=(2,1),\qquad\Delta=4.
 \tag{14}
\]

The carrier changes no ordering, and row 2 is the exact winner. The phases
\((2,3)\) and \((3,2)\) each have widths \((3,3)\), two-bit quotient entries,
and retained sets \(\{1,2\}\) and \(\{2,4\}\), respectively. Their
intersection is \(\{2\}\). Excluding headers, two certificates use 48
resident bits: 40 quotient bits and eight width bits. The uncompressed
five-by-two signed 22-bit gate matrix uses 220 bits. The interpreter reads one
source gate row and one payload record for this query; either certificate
alone needs two gate-row reads.

## 5. Block-sum residual certificates

The span certificate forgets every residual coordinate once it has recorded a
column width. A stronger source-derived guide retains one exact integer sum per
row and coordinate block, while still omitting the individual residuals.

Shift the residuals in (2) by their column minima. There is a common vector
(c), which is again irrelevant to order, such that

\[
 a_i=c+\Delta Q_i+e_i,\qquad 0\leq e_{ij}\leq w_j.
 \tag{17}
\]

Partition the coordinates into nonempty blocks
(mathcal B=(B_1,\ldots,B_g)), and store

\[
 t_{ib}=\sum_{j\in B_b}e_{ij},\qquad
 0\leq t_{ib}\leq T_b:=\sum_{j\in B_b}w_j.
 \tag{18}
\]

For a query, the best possible contribution of a block subject to this stored
row sum is

\[
 \begin{aligned}
 U_b(t;x)&=\max\left\{\sum_{j\in B_b}e_jx_j:
        0\leq e_j\leq w_j,\ \sum_{j\in B_b}e_j=t,\ e_j\in\mathbb Z\right\},\\
 L_b(t;x)&=\min\left\{\sum_{j\in B_b}e_jx_j:
        0\leq e_j\leq w_j,\ \sum_{j\in B_b}e_j=t,\ e_j\in\mathbb Z\right\}.
 \end{aligned}
 \tag{19}
\]

To calculate (U_b), order the coordinates of the block by decreasing
(x_j), then fill the capacities (w_j) in that order until (t) units have
been assigned. For (L_b), use increasing order. An exchange of one unit from
a lower-(x) coordinate to a higher-(x) coordinate never decreases the
objective, so this integer greedy rule proves (19). This is the bounded
integer knapsack or rearrangement argument, not an unproved heuristic.

Set

\[
 \ell_i=\Delta Q_i^Tx+\sum_{b=1}^gL_b(t_{ib};x),\qquad
 u_i=\Delta Q_i^Tx+\sum_{b=1}^gU_b(t_{ib};x),
 \tag{20}
\]

and take (k=\min\operatorname*{arg\,max}_i\ell_i). The block-sum survivor
set is

\[
 S_{\mathcal B}(x)=\{i:u_i>\ell_k\ \text{or}\ (u_i=\ell_k\ \text{and}\ i\leq k)\}.
 \tag{21}
\]

**Theorem 3 — exact block-sum refinement.** Reading the original gate rows in
(S_{\mathcal B}(x)), then selecting their source-precision least-index
maximum, returns \(\nu_A(x)\).

**Proof.** The actual residual vector of row (i) is feasible in (19), so its
source score, after the same omitted common term for every row, lies in
([\ell_i,u_i]). Row (k)'s actual score is at least \(\ell_k\). Hence a row
with (u_i<\ell_k) loses strictly, while a row with (u_i=\ell_k) cannot
outscore (k) and loses the tie if (i>k). These are the rows excluded in
(21); every possible exact winner remains. The final exact comparison proves
the result. \(\square\)

For a fixed row, (19) is the exact upper and lower support function of the
box-plus-sum set described by (w) and (t_{ib}). It is not automatically the
jointly tight uncertainty set for all rows: the globally recorded facts that
some row attains each column minimum and maximum can couple different rows,
while this small guide does not record which rows do so. The theorem needs only
safe intervals. It does not claim a global information-theoretic optimum.

The extra guide payload is

\[
 B_{\rm sum}=m\sum_{b=1}^g\left\lceil\log_2(T_b+1)\right\rceil
 \tag{22}
\]

bits, in addition to (10). Singleton blocks recover every (e_{ij}), making
routing exact from the guide but approaching a full gate-difference encoding.
One block stores only one residual sum per row and leaves substantial ambiguity.
The latter ambiguity is useful: with (w=(4,4)), (t=4), the two residuals
((4,0)) and ((3,1)) have the same stored sum but have different inner
products against ((1,-1)). The guide cannot silently substitute either for
the original gate row.

The block partition also changes working state. A fast exact interpreter sorts
the coordinates of each block once per query, retaining coordinate indices and
capacity/value prefixes. This takes (O(d\log d)) comparisons, (O(d)
integer words of scratch, and then (O(g\log(d/g))) predecessor searches per
row when blocks are balanced. A strict small-RAM variant repeatedly finds the
next largest or smallest unsaturated query coordinate; it uses (O(1)) words
beyond (x) and the score registers, but costs (O(\sum_b|B_b|^2)) comparisons
per evaluated row. Neither route has an uncharged oracle for (19).

For a concrete strict gain over the width-only guide, let \(\Delta=16\),
(x=(1,1)), one block (B=\{1,2\}), and, after the omitted common carrier,
let two rows have the same quotient (Q=(0,0)) and residuals

\[
 e_0=(0,0),\qquad e_1=(4,0).
 \tag{23}
\]

Here (w=(4,0)), (t_{01}=0), and (t_{11}=4). The width-only certificate
retains both rows because its common error allowance is four. Equation (19)
gives the point intervals \([0,0]\) and \([4,4]\), so (21) reads only row 1
before reading its same original payload. The two stored sums add six bits to the width guide; the existing two 4-bit
width fields use eight bits. A large shared integer carrier can raise the
source-row width arbitrarily without changing either guide count. This is a
measured source-read advantage over the previous quotient-span interpreter,
not an advantage over every exact interval representation.

## 6. Endpoint-tagged sums: a sharper correlated certificate

The block sum still forgets which rows realize a residual endpoint. That loss is
visible in a two-row block. Store, for every coordinate with (w_j>0), the
least row identifiers

\[
 \alpha_j=\min\{i:e_{ij}=0\},\qquad
 \beta_j=\min\{i:e_{ij}=w_j\}.
 \tag{24}
\]

These tags add

\[
 B_{\rm tag}=2\sum_{j:w_j>0}\left\lceil\log_2m\right\rceil
 \tag{25}
\]

bits. They do not store a coefficient value. For a row (i) and block (B_b),
they merely fix the entries indexed by

\[
 F_{ib}=\{j\in B_b:i=\alpha_j\ \text{or}\ i=\beta_j\}.
 \tag{26}
\]

The fixed value is zero for an \(\alpha\) tag and (w_j) for a \(\beta\) tag.
Subtract its sum from (t_{ib}), delete those coordinates from the bounded
integer knapsack in (19), and call the resulting endpoints
(L_b^{\rm tag}(t_{ib};x)) and (U_b^{\rm tag}(t_{ib};x)), after adding the
known fixed dot-product contribution. Replacing (L_b,U_b) in (20)--(21) by
these tagged bounds gives another exact survivor set.

**Theorem 4 — endpoint tags preserve exactness and only tighten.** The tagged
interpreter returns the exact least-index winner. Its interval for every row is
contained in the corresponding block-sum interval.

**Proof.** The actual residual vector obeys the box, sum, and every tagged
coordinate equality, so it remains feasible in the reduced knapsack problem.
The proof of Theorem 3 therefore still applies. Adding equalities only removes
feasible vectors, which can raise a lower bound and lower an upper bound; it
cannot widen an interval. \(\square\)

The tags supply a small but real correlation. Let one block have (w=(4,4)),
residuals (e_0=(0,4)), (e_1=(4,0)), equal sums (t_{01}=t_{11}=4), and
query (x=(1,-1)). The untagged support interval for each row is
\([-4,4]\), so it retains both rows. The endpoint tags identify every
coordinate in this two-row instance. They give exact residual scores
\(-4\) and (4\), retaining only row 1 before its original payload read.
The example does not rely on a structural promise about the gate matrix; the
encoder measured these endpoints from this finite source.

Tags change the arithmetic accounting. The interpreter may scan all (d) tags
while evaluating a row and run the reduced greedy bound, which keeps the
working state in the same (O(d))-word sorted-prefix regime as Section 5 and
adds at most (O(md)) tag tests over the guide scan. An implementation that
wants faster per-row bound updates needs per-row inverse tag lists or modified
prefix structures; those are further source-derived metadata and must be
charged. This note claims neither list for free.

Endpoint tags still do not identify every residual coordinate. When (m>2),
a row can have an untagged interior residual and the final source read remains
necessary whenever its tagged interval survives. The representation stays a
filter-and-refine guide rather than a replacement gate table.

## 7. Centered second moment: a stronger conventional bound

A block sum is not the only small statistic available. Store also the exact
second residual moment

\[
 v_{ib}=\sum_{j\in B_b}e_{ij}^2,
 \qquad 0\leq v_{ib}\leq V_b:=\sum_{j\in B_b}w_j^2.
 \tag{27}
\]

Let \(n_b=|B_b|\), \(S_b=\sum_{j\in B_b}x_j\), and
\(X_{2b}=\sum_{j\in B_b}x_j^2\). Centering both vectors and applying
Cauchy--Schwarz yields, for the actual block residual product
\(R_{ib}=\sum_{j\in B_b}e_{ij}x_j\),

\[
 \left|n_bR_{ib}-t_{ib}S_b\right|
 \leq
 \sqrt{\bigl(n_bv_{ib}-t_{ib}^2\bigr)
             \bigl(n_bX_{2b}-S_b^2\bigr)}.
 \tag{28}
\]

Put \(z_{ib}\) equal to the integer square root of the nonnegative product
on the right. The exact safe integer interval is

\[
 L^{(2)}_{ib}=\left\lceil\frac{t_{ib}S_b-z_{ib}}{n_b}\right\rceil,
 \qquad
 U^{(2)}_{ib}=\left\lfloor\frac{t_{ib}S_b+z_{ib}}{n_b}\right\rfloor.
 \tag{29}
\]

Using \(z=\lfloor\sqrt D\rfloor\) in (29) is valid even when \(D\) is not a
square: an integer divided by \(n_b\) cannot cross another integer boundary
when its numerator changes by the fractional part of \(\sqrt D\). Intersect
\([L^{(2)}_{ib},U^{(2)}_{ib}]\) with the capped-sum interval from (19), block
by block, before applying Theorem 3. Both intervals contain the source value,
so their intersection does too.

The added storage is

\[
 B_{\rm square}=m\sum_{b=1}^g
 \left\lceil\log_2(V_b+1)\right\rceil.
 \tag{30}
\]

When every width is less than \(2^k\), a block of (n_b) coordinates needs at
most \(2k+\lceil\log_2n_b\rceil\) bits for this statistic. Query work adds
one sum and one sum of squares per block, one exact integer square root per
row-block, and interval intersection. It stores moments of the residuals, not
partial source weights.

This conventional moment bound can be strictly sharper than a residual
\(\ell_2\)-norm bound because it also uses the sum. Take one three-coordinate
block with \(w=(2,2,2)\), query (x=(1,-1,0)), and source residual rows

\[
 e_0=(0,0,0),\qquad e_1=(1,1,1),\qquad e_2=(2,2,2).
 \tag{31}
\]

Give rows 0 and 1 the same quotient (Q=(0,0,0)), and row 2 the quotient
\((0,2,0)\), with \(\Delta=8\). The exact least-index winner is row 0. The
sum-only interval of row 1 is \([-2,2]\), so it survives against row 0.
For row 1, however, \(t=3\), \(v=3\), \(S=0\), and the right side of (28)
is zero. Its moment interval is exactly \([0,0]\), so the tie rule removes it.
A norm-only bound has radius \(\sqrt{6}\) and remains wider.

This result narrows the honest comparison. The capped-sum and endpoint tags
are not automatically stronger than all inexpensive exact filters; a scalar
second moment costs little enough that it belongs in the baseline. FEXIPRO's
transformed and scaled integer filters can retain still more per-coordinate
information, so no bit-for-bit dominance over that broader class follows from
(27)--(30).

## 8. Row-and-column residual totals: exact joint pair bounds

The previous certificates bound each row separately. A source also supplies a
small cross-row statistic for every coordinate:

\[
 u_j=\sum_{i=0}^{m-1}e_{ij},\qquad 0\leq u_j\leq mw_j.
 \tag{32}
\]

Together with one-block row sums (t_i=\sum_je_{ij}), the widths, and the
column totals, compatible residual matrices form the bounded transportation
set

\[
 \mathcal T=\left\{Z\in\mathbb Z^{m\times d}:
 0\leq Z_{ij}\leq w_j,\quad
 \sum_jZ_{ij}=t_i,\quad
 \sum_iZ_{ij}=u_j\right\}.
 \tag{33}
\]

For a proposed challenger (i) and anchor (k), calculate

\[
 M_{ik}(x)=\max_{Z\in\mathcal T}\sum_{j=1}^dx_j(Z_{ij}-Z_{kj}).
 \tag{34}
\]

This is an integral min-cost flow after negating the objective: source-to-row
arcs impose the (t_i) supplies, row-to-coordinate arcs have capacity (w_j),
and coordinate-to-sink arcs impose the (u_j) demands. The row-(i) arcs have
cost \(-x_j\), row-(k) arcs cost \(+x_j\), and the remaining row arcs cost
zero. All capacities and supplies are integers, so the standard network-flow
integrality theorem gives an integer optimum for (34).

Let (C_{ik}=\Delta(Q_i-Q_k)^Tx). For any chosen anchor (k), retain

\[
 S_{\rm flow}(k,x)=\{k\}\cup
 \left\{i\ne k:C_{ik}+M_{ik}(x)>0\ \text{or}\
  \bigl(C_{ik}+M_{ik}(x)=0\ \text{and}\ i<k\bigr)\right\}.
 \tag{35}
\]

**Theorem 5 — transportation-pair refinement.** Exact source refinement over
(S_{\rm flow}(k,x)) returns the least-index maximum of the source gate rows.

**Proof.** The actual residual matrix belongs to \(\mathcal T\). Therefore
\(e_i^Tx-e_k^Tx\leq M_{ik}(x)\). If a row is excluded by (35), it cannot
outscore (k), and it loses equality when its index is larger. A true winner
must beat (k) when its index is larger and must tie or beat (k) when its
index is smaller, so it cannot be excluded. The final source-precision
comparison proves the claim. \(\square\)

The extra guide cost is only

\[
 B_{\rm column}=\sum_{j=1}^d\left\lceil\log_2(mw_j+1)\right\rceil
 \tag{36}
\]

bits beyond widths and the row sums. It records derived aggregate residual
counts, not a source row or a query-answer table. A changed gate component
invalidates these totals together with every other guide field; they are bound
to the same gate digest.

The joint constraint can be strictly stronger than independent row support.
Let \(\Delta=4\), \(x=(1,-1)\), \(w=(3,3)\), and take three residual rows

\[
 E=\begin{pmatrix}2&0\\0&3\\3&3\end{pmatrix},\qquad
 (t_0,t_1,t_2)=(2,3,6),\qquad (u_1,u_2)=(5,6).
 \tag{37}
\]

Set (Q_0=(1,0)) and (Q_1=Q_2=(0,0)). Row 0 has source score 6, row 1
has score \(-3\), and row 2 has score 0, so row 0 wins. Row sums alone allow
row 0 a residual score as low as \(-2\) and row 1 as high as 3. Their
independent comparison therefore permits row 1: \(-4+3-(-2)=1\). The three
matrices satisfying all row sums, column totals, and capacities give
row-1-minus-row-0 residual differences 3, \(-1\), and \(-5\). Thus
\(M_{10}=3\), the full bound is \(-4+3=-1\), and (35) removes row 1 before
any source gate read.

There is a hard resource turn. For general (m,d), calculating (34) for each
challenger with a conventional exact min-cost-flow method holds residual
capacities or flows on (md) row-coordinate arcs, plus row and coordinate
potentials. It needs \(\Omega(md)\) mutable machine words in the direct
representation, and capacity-scaling or successive-shortest-path work that is
far larger than the two linear guide scans in Section 3. The two-row special
case collapses to a bounded knapsack because a column total determines the
other row. For arbitrary (m), no small-RAM local solver is supplied here.
The guide is exact, but this interpreter currently fails the intended minimal
RAM character unless the flow state itself has an independently justified
external, replayable schedule.

The later [full-pair construction](full-pair-polymatroid.md) addresses this specific
working-state gap. It derives the same full support from a suffix-slack allocation
and a scalar dual, using \(O(m+d)\) working words. That result supersedes the absence
of a small-state solver in this section; it does not establish a better complete
RAM or latency frontier than the strongest established implementation.

## 9. Comparator, strict narrow gain, and decisive defeat

A row-independent floor-quantization certificate knows only
\(0\leq r_{ij}<\Delta\). Its pairwise error allowance is

\[
 E_{\rm independent}(x)=(\Delta-1)\sum_j|x_j|,
 \tag{15}
\]

whereas the quotient-span certificate uses \(E(x)\leq E_{\rm independent}(x)\).
The inequality is strict whenever some coordinate's actual residues occupy a
proper subinterval. For example, with \(\Delta=16\), \(x=(1,1)\), and rows

\[
 a_0=(2^{20},2^{20}),\qquad a_1=(2^{20}+16,2^{20}),
 \tag{16}
\]

all residual widths are zero. The quotient-span guide proves that only row 1
can win. The independent guide has error 30 and cannot exclude row 0 from its
16-point coarse deficit. Thus the construction has a real complete-chain gain
against that intentionally narrower comparator: one source gate-row read
rather than two, then the same one original payload read.

That is not the strongest fair comparator. A centered scalar interval guide
may retain the same translated quotients (Q) and the common interval
\([\min_i r_{ij},\max_i r_{ij}]\) for each coordinate. Subtracting its two
row intervals gives exactly \([-w_j,w_j]\), hence exactly (6). It has the
same guide bits, arithmetic, reads, and tie treatment as this note. The
quotient-span construction is therefore a transparent reformulation of that
centered guide, with the useful interpretation that common score information
has been factored out. It does not strictly beat the optimized centered class.

Nor does it guarantee a source-read gain. A stored phase can leave every
coarse contender within its residual band, in which case \(|S(x)|=m\) and the
interpreter performs a full source-gate scan. The second phase in (13) can
help on a particular query, but a collection of phase tables is a familiar
multi-codebook tradeoff and can become larger than the original gate block.
The construction imposes no favorable gate structure; it exposes, rather than
removes, this adverse case.

## 10. Reproducible finite checks

The following standard-library check verifies the two phase examples, the
least-index tie rule, block and centered-moment calculations, the transportation
witness, and the containment theorem by exhaustive queries on a small integer
cube.

```python
from itertools import product

DELTA = 4

def guide(rows, phase, query):
    q = [[(a - g) // DELTA for a, g in zip(row, phase)] for row in rows]
    minima = [min(row[j] for row in q) for j in range(len(query))]
    code = [[value - minima[j] for j, value in enumerate(row)] for row in q]
    residual = [[(a - g) % DELTA for a, g in zip(row, phase)] for row in rows]
    width = [max(row[j] for row in residual) - min(row[j] for row in residual)
             for j in range(len(query))]
    coarse = [sum(a * x for a, x in zip(row, query)) for row in code]
    pivot = max(range(len(rows)), key=lambda i: (coarse[i], -i))
    error = sum(w * abs(x) for w, x in zip(width, query))
    keep = set()
    for i in range(len(rows)):
        deficit = DELTA * sum((code[pivot][j] - code[i][j]) * query[j]
                              for j in range(len(query)))
        if i == pivot or deficit < error or (deficit == error and i < pivot):
            keep.add(i)
    return tuple(width), tuple(coarse), keep

def winner(rows, query):
    return max(range(len(rows)), key=lambda i:
               (sum(a * x for a, x in zip(rows[i], query)), -i))

phase_rows = ((2, 0), (5, 2), (3, 0), (-2, 4))
assert guide(phase_rows, (0, 0), (-2, -1)) == ((2, 2), (-2, -4, -2, -1), {0, 2, 3})
assert guide(phase_rows, (3, 0), (-2, -1)) == ((3, 2), (-2, -4, -4, -1), {0, 3})

base = ((-3, 4), (2, 5), (5, 7), (-3, 1), (3, -2))
carrier = 1 << 20
rows = tuple(tuple(carrier + a for a in row) for row in base)
x = (2, 1)
a = guide(rows, (2, 3), x)
b = guide(rows, (3, 2), x)
assert a[2] == {1, 2} and b[2] == {2, 4} and a[2] & b[2] == {2}
assert winner(rows, x) == 2

def block_bounds(capacity, total, query):
    def greedy(order):
        left, value = total, 0
        for j in order:
            take = min(left, capacity[j])
            value += take * query[j]
            left -= take
        assert left == 0
        return value
    return (greedy(sorted(range(len(query)), key=lambda j: query[j])),
            greedy(sorted(range(len(query)), key=lambda j: -query[j])))

# Equation (23): exact residual-sum intervals beat the width-only interval.
assert block_bounds((4, 0), 0, (1, 1)) == (0, 0)
assert block_bounds((4, 0), 4, (1, 1)) == (4, 4)

# Equation (31): centered moment bounds can collapse a nontrivial sum interval.
def moment_bounds(t, v, query):
    n, total, squares = len(query), sum(query), sum(z * z for z in query)
    discriminant = (n * v - t * t) * (n * squares - total * total)
    root = isqrt(discriminant)
    return ((t * total - root + n - 1) // n, (t * total + root) // n)

from math import isqrt
assert moment_bounds(3, 3, (1, -1, 0)) == (0, 0)

# Equation (37): column totals rule out independent per-row extremes.
capacity, row_total, column_total = (3, 3), (2, 3, 6), (5, 6)
residual_rows = tuple(product(range(4), repeat=2))
transport = [matrix for matrix in product(residual_rows, repeat=3)
             if tuple(map(sum, matrix)) == row_total
             and tuple(sum(row[j] for row in matrix) for j in range(2)) == column_total]
difference = [sum((matrix[1][j] - matrix[0][j]) * (1, -1)[j]
                  for j in range(2)) for matrix in transport]
assert difference == [3, -1, -5] and max(difference) == 3
for query in product(range(-2, 3), repeat=2):
    exact = winner(rows, query)
    for phase in product(range(DELTA), repeat=2):
        assert exact in guide(rows, phase, query)[2]
print("PASS: exact containment, ties, phase tradeoff, block, moment, and flow bounds")
```

## 11. Source challenge and remaining obstacle

This is an exact MIPS-style selection problem, although its contract is more
narrowly concerned with obtaining original external records after selection.
Ram and Gray's [exact branch-and-bound MIPS work](https://arxiv.org/abs/1202.6101)
already uses data-structure bounds to prune inner-product candidates. Abuzaid,
Sethi, Bailis, and Zaharia's [exact MIPS comparison](https://arxiv.org/abs/1706.01449)
reports that no one exact method dominates all inputs, including cases where a
hardware-efficient scan wins. Quantization-based MIPS is also an established
area, although Guo et al.'s [QUIP method](https://proceedings.mlr.press/v51/guo16a.html)
is approximate and therefore cannot supply this note's source-precision final
step. More directly, Li, Chan, Yiu, and Mamoulis's
[FEXIPRO](https://www4.comp.polyu.edu.hk/~csmlyiu/conf/SIGMOD17_fexipro.pdf)
uses integer approximations as exact upper-bound filters before source-precision
inner products. Its transformed and scaled bounds are a stronger established
comparison than an uncentered residual box. The present phase quotient and
block-sum certificate are compatible with that filter-and-refine pattern; they
are not a basis for a generic novelty assertion.

The primary-source check leaves no basis to call common-mode cancellation,
scalar residual intervals, multiple coarse codes, or the exact filter-refine
pattern new. The transportation step is standard integral min-cost-flow
mathematics, so the row-and-column totals are a stronger representation
candidate, not an originality result. Its direct solver violates the small-RAM
objective in the arbitrary case.

The remaining mathematical obstacle is narrower and harder: find a jointly
constrained residual representation that beats scaled integer filters and
per-item moment summaries at the same encoded-bit budget, while its exact
interpreter keeps only local working state and streams source refinements. The
block sums, endpoint tags, moments, and transportation witness improve named
weaker comparators; this note has not proved that any of them crosses that
stronger line.
