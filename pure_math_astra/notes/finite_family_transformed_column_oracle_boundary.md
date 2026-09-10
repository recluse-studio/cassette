# A finite source corpus collapses under a free transformed-column oracle

Status: proved model boundary.  This is an obstruction to extending a
continuous-orbit finite-advice lower bound to arbitrary finite source
families when transformed columns, decoder tables, and scalar precision are
uncharged.  It makes no novelty claim.

## Finite-family identification in one read

Let \(A_1,\ldots,A_N\in\mathbb R^{p\times q}\) be distinct.  There is an
orthogonal \(Q\in O(q)\) for which the first transformed columns

\[
 A_iQe_1\qquad(1\le i\le N)
 \tag{1}
\]

are pairwise distinct.

Indeed, for every pair \(i\ne j\), \(A_i-A_j\ne0\), so
\(\ker(A_i-A_j)\) is a proper linear subspace of \(\mathbb R^q\).  A
finite union of proper linear subspaces cannot cover \(\mathbb R^q\).
Choose a unit vector

\[
 v\notin\bigcup_{i<j}\ker(A_i-A_j),
 \tag{2}
\]

and extend \(v\) to an orthonormal basis, defining \(Qe_1=v\).  Then
\((A_i-A_j)v\ne0\) for every pair, proving (1).

Suppose a decoder may read the exact vector \(A_iQe_1\), has a free
shared table of all values in (1), and may use arbitrary exact real
arithmetic.  The one read identifies \(i\).  It can then return
\(A_ix\) from its table for every query \(x\).  This has zero
source-selected advice and zero error.  The result depends essentially on
the finite corpus, the free table, the fixed but uncharged transform, and
the exact unbounded-precision fetched value.

## A balanced-base packing transform

The preceding argument is not merely existential.  Fix integers \(M\ge1\)
and

\[
 B=2M+1,\qquad
 v=\frac{(1,B,\ldots,B^{q-1})^T}
 {\sqrt{\sum_{j=0}^{q-1}B^{2j}}}.
 \tag{3}
\]

Extend \(v\) to an orthogonal \(Q\).  For every integer matrix
\(A=(a_{rj})\in[-M,M]^{p\times q}\), the \(r\)-th coordinate of its
first transformed column is

\[
 (Av)_r=\frac{z_r}{\sqrt{\sum_{j=0}^{q-1}B^{2j}}},
 \qquad
 z_r=\sum_{j=1}^q a_{rj}B^{j-1}.
 \tag{4}
\]

The signed digit expansion is unique.  If two expansions agree, their
difference has coefficients in \([-(B-1),B-1]\).  Reducing modulo \(B\)
forces its constant coefficient to vanish; division by \(B\) and
induction force all remaining coefficients to vanish.  Thus one exact
packed scalar \(z_r\) determines the full row of \(q\) original entries,
and the one fetched transformed column determines the entire matrix.

## The byte account does not collapse

The full integer source cube has

\[
 \bigl|[-M,M]^{p\times q}\bigr|=B^{pq}
 \tag{5}
\]

members. Any lossless fixed-width or prefix-free binary representation that distinguishes all
of them therefore needs at least

\[
 pq\log_2B
 \tag{6}
\]

bits in the worst case.  In the packing above, each \(z_r\) takes exactly
\(B^q\) possible values, so its finite binary encoding needs at least
\(q\log_2B\) bits in the worst case.  Across the \(p\) packed values this
is again (6), apart from integer rounding of code lengths.

The transform has traded \(q\) scalar words per row for one scalar whose
exact value carries \(q\) base-\(B\) digits.  It has not reduced the
finite-byte information content.  The normalized vector in (3) also
contains a generally irrational normalization factor, so treating it as a
free exact resident transform is itself stronger than a fixed finite-word
model.

## Consequence for the advice lower bound

The continuous-orbit theorem in
`finite_advice_spectral_trace_lower.md` constrains a fixed finite
set of decoder states over an uncountable source orbit.  The construction
above shows that no theorem of that form can extend unchanged to an
arbitrary finite-word source corpus if it permits all of the following:

1. a free fixed query transform and transformed-column storage;
2. a free shared decoder table indexed by exact fetched values; and
3. one fetched real scalar of unbounded precision at the cost of one word.

For a finite corpus, those permissions allow exact source identification
in one transformed-column read. A finite-word theorem therefore needs an
explicit observation format and fetched-bit count. If a claimed storage
result permits these transforms and tables, their description costs also
matter. Restricting the theorem to original columns is another declared
model. This is a modeling boundary, not evidence
against the continuous-orbit result or a complete Cassette resource lower
bound.
