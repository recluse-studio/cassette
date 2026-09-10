# finite_advice_stiefel_orbit_lower.md — finite source-trained advice lower bound on the rectangular identity-Gram orbit; depends on fixed_gram_orbit_static_oracle_minimax_independent_proof.md and ../../MATHS.md.

## Model and result

Let \(p>q\), let the source range over the Stiefel manifold

\[
\mathcal V_{p,q}=\{A\in\mathbb R^{p\times q}:A^TA=I_q\},
\]

and let a source-trained encoder assign one of \(N\) advice labels to each
source. The resulting measurable cells \(C_1,\ldots,C_N\) partition
\(\mathcal V_{p,q}\). Advice label \(a\) chooses a source- and
query-independent support law \(p^a_S\) and Borel decoders

\[
F^a_S(A_{:S},x).
\]

The decoder receives the label, the support index, the selected columns,
and the query. It may otherwise be arbitrary. Suppose, for every
\(A\in C_a\) and every unit \(x\),

\[
\sum_Sp^a_S\|F^a_S(A_{:S},x)-Ax\|_2^2\le C.
\tag{1}
\]

Exact unbiasedness is not needed for the lower bound below. Thus it also
applies to the narrower exactly unbiased class.

Assume each advice-specific law has expected reads at most
\(\bar s<q\):

\[
\sum_Sp^a_S|S|\le\bar s.
\tag{2}
\]

Put \(d=1-\bar s/q>0\), and let

\[
H_q=q\,2^{q-1}
\tag{3}
\]

be the number of pairs \((S,j)\) with \(S\subseteq[q]\) and \(j\notin S\).
Then every such finite-advice scheme satisfies

\[
\boxed{\qquad
C\ge
\ d\,(NH_q\sqrt p)^{-\,2/(p-q)}.
\qquad}
\tag{4}
\]

For \(N=2^b\), achieving \(C\le cd\) for any fixed \(0<c<1\)
requires

\[
b\ge {p-q\over2}\log_2(1/c)
-\log_2(H_q\sqrt p).
\]

Thus a fixed fractional reduction below \(d\) requires advice growing
linearly in the rectangular complement dimension \(p-q\). For fixed
\(q\) and \(\bar s<q\), this rules out a dimension-uniform extension in
which a fixed number of source-trained advice bits makes uniform error tend
to zero.

Under the stronger hard cap \(|S|\le s<q\) for every outcome, put
\(H_{q,s}=q\sum_{k=0}^s\binom{q-1}k\). The hard-cap bound is

\[
\boxed{\qquad
C\ge \left(1-\frac sq\right)
(NH_{q,s}\sqrt p)^{-\,2/(p-s-1)}.
\qquad}
\tag{5}
\]

## Proof

Use normalized invariant probability measure \(\mu\) on
\(\mathcal V_{p,q}\). Fix one nonnull cell \(C_a\) and one
\(A\in C_a\). Sum (1) over the \(q\) coordinate queries \(e_j\), then
discard the terms with \(j\in S\):

\[
\sum_{S}\sum_{j\notin S}p^a_S
\left\|F^a_S(A_{:S},e_j)-A_{:j}\right\|_2^2
\le qC.
\tag{6}
\]

The total weight in this sum is

\[
\sum_Sp^a_S(q-|S|)
=q-\sum_Sp^a_S|S|
\ge q-\bar s=qd.
\tag{7}
\]

Therefore, for this \(A\), at least one pair \((S,j)\) with \(j\notin S\)
and \(p^a_S>0\) satisfies

\[
\left\|F^a_S(A_{:S},e_j)-A_{:j}\right\|_2
\le\sqrt{C/d}=:\delta.
\tag{8}
\]

The selected pair may vary with \(A\). The case \(\delta\ge1\) gives
\(C\ge d\), which is stronger than (4). Assume \(\delta<1\).
If \(\delta=0\), every fixed-pair reconstruction event below is a
singleton cap in a positive-dimensional conditional sphere and has
measure zero. Its finite union cannot cover a nonnull cell. Thus
\(C=0\) is impossible, and the remaining argument may assume
\(0<\delta<1\).

Fix any proper pair \((S,j)\) and condition on the selected frame
\(X=A_{:S}\), of size \(k=|S|\). Under \(\mu\), the missing column
\(A_{:j}\), conditional
on \(X\), is uniform on the unit sphere in
\(\operatorname{span}(X)^\perp\), a space of dimension

\[
n=p-k\ge p-q+1\ge2.
\]

For a uniform vector \(V\) on the unit sphere in an \(n\)-dimensional
Euclidean space and every fixed \(z\), the elementary spherical-cap bound

\[
\Pr(\|V-z\|_2\le\delta)\le\sqrt n\,\delta^{\,n-1}
\tag{9}
\]

holds for \(0<\delta<1\). To see this, project \(z\) into the sphere's
ambient space. The largest possible cap has first coordinate at least
\(\sqrt{1-\delta^2}\). For \(n\ge3\), integrate the first-coordinate
density

\[
{\Gamma(n/2)\over\sqrt\pi\,\Gamma((n-1)/2)}
(1-t^2)^{(n-3)/2}
\]

over that cap, using the bound on its normalizing constant by \(\sqrt n\),
cap length at most \(\delta^2\), and \(1-t^2\le\delta^2\). For \(n=2\),
the cap is an arc of normalized length at most \(\delta\), which is also
bounded by \(\sqrt2\delta\).

For every fixed pair \((S,j)\), the sources satisfying (8) for that pair
occupy at most one such cap in every conditioned fiber. Fubini
disintegration and the cap estimate (9) imply

\[
\mu\left(C_a\cap\bigcup_{\substack{S\subsetneq[q]\\j\notin S}}
\left\{A:\left\|F^a_S(A_{:S},e_j)-A_{:j}\right\|\le\delta\right\}\right)
\le H_q\sqrt p\,\delta^{\,p-q}.
\tag{10}
\]

By (8), the union on the left contains \(C_a\). The cells cover the orbit,
so summing (10) yields

\[
1\le NH_q\sqrt p\,(C/d)^{(p-q)/2}.
\]

Rearranging proves (4).

For a hard cap, only pairs with \(|S|\le s\) occur. Their number is
\(H_{q,s}\), their cap exponent is at least \(p-s-1\), and (7) holds with
\(d=1-s/q\). The same proof gives

\[
1\le NH_{q,s}\sqrt p\,
\left({C\over1-s/q}\right)^{(p-s-1)/2},
\]

which is (5).

## Finite right-basis catalog corollary

The same bounds hold if each advice label \(a\) selects one fixed
orthogonal right basis \(Q_a\), the support law selects columns of

\[
 B=AQ_a,
\]

and the decoder receives \(B_{:S}\), the label, and the original query
\(x\).  The risk is still measured against \(Ax\).  Indeed, apply the
uniform risk assumption to \(x=Q_ae_j\).  Its target is

\[
 A Q_a e_j=B_{:j}.
\]

For fixed \(a\), the right action \(A\mapsto AQ_a\) preserves the
Stiefel measure, and it maps \(C_a\) to a measurable cell of equal
measure.  The missing-pair argument and its conditional cap law therefore
apply verbatim to \(B\).  Thus a finite source-trained choice from any
predeclared orthogonal-basis catalog does not evade (4) or (5), even if
the label-specific decoder performs arbitrary uncharged internal
computation.

## Quantifiers and boundary

The exact nonattainment-safe form is: for every advice scheme and every
claimed uniform bound \(C_0\) strictly below the right side of (4), or
below the applicable right side of (5), there are
\(A\in\mathcal V_{p,q}\) and \(\|x\|_2=1\) for which the expected error
exceeds \(C_0\). Equivalently, the uniform risk supremum is at least the
displayed bound, but this proof does not assert that the supremum is
attained. Symbolically,

\[
\forall\text{ measurable }N\text{-cell advice partitions and decoders},
\quad
\forall C_0\text{ strictly below the applicable bound},\quad
\exists A\in\mathcal V_{p,q},\ \exists\|x\|_2=1
\]

with expected error greater than \(C_0\). The hard source may depend on the
full advice scheme. The proof neither identifies it nor supplies a
finite-word source.

The condition \(p>q\) is essential. At \(p=q=2\), the conditional sphere
after observing one column has only two points. One advice bit can
distinguish the determinant components and supports the exact one-column
reconstruction using the rotation \(J\). The continuous complement sphere
is precisely what restores the finite-advice lower bound in the rectangular
orbit.

This is a uniform-risk result for source-trained support schedules with
finite advice. It does not recover the exact water value \(\nu_s(G)\), and
it does not cover unbounded advice, source-trained resident state taking
more than \(N\) distinct values, approximate source labels, or
physical-page costs. A finite \(N\)-state codebook may contain arbitrary
resident matrices or functions; it is already covered because the
label-specific decoder may use arbitrary fixed data. No novelty claim is
made.
