# Exact unbiasedness and finite advice in the two-column orbit

Status: proved and independently reconstructed. Originality and sufficient
Cassette significance remain unestablished.

The stronger [conditional-cap theorem](/Users/drewwiberg/cassette/pure_math_astra/notes/finite_advice_unbiased_static_conditional_cap_lower.md)
now supersedes this bound and removes the need for atomic matching in this
application. This note preserves the earlier analytic route.

## Statement

Let \(p\ge3\), and let
\[
 {\cal V}_{p,2}=\{A=[a,b]\in\mathbb R^{p\times2}:A^TA=I_2\}.
\]
A measurable source encoder selects a label \(\ell(A)\) from at most
\(N\ge1\) fixed decoder states. In state \(\ell\), the decoder reads
column one with probability \(\theta_\ell\in[0,1]\), and column two
otherwise. The probability is independent of the source within its
label cell and independent of the query.

Its output after reading a column may be any Borel function of the
label, that column, and the query. Additional output randomness is
allowed through a Borel conditional law determined only by those inputs;
its random seed is independent of the source. Suppose the decoder is exactly unbiased for every source and
query:
\[
 \mathbb E[\widehat y\mid A,x]=Ax.
 \tag{1}
\]
If, for some finite \(C\),
\[
 \sup_{A\in{\cal V}_{p,2}}\ \sup_{\|x\|_2=1}
 \mathbb E[\|\widehat y-Ax\|_2^2\mid A,x]\le C,
 \tag{2}
\]
then
\[
 \boxed{\quad C\ \ge\
       2^{-2/(p-2)}N^{-4/(p-2)}.\quad}
 \tag{3}
\]
Consequently, \(b\) bits of source-selected advice give
\[
 C\ge 2^{-(4b+2)/(p-2)}
 \qquad\text{when }N\le2^b.
 \tag{4}
\]
As \(b=o(p)\), the lower bound tends to one. A decoder with no advice
attains \(C=1\): choose each column with probability \(1/2\), and output
\(2ax_1\) or \(2bx_2\). Thus (4) recovers the sharp limiting one-column
unbiased error in that regime.

For \(C<1\), a more precise intermediate inequality is
\[
 1\le N\sqrt{D_p}\,
       2^{-(p-2)/(2(p-1))}C^{(p-2)/4},
 \quad
 D_p=\frac{p-1}{p-2}
 \frac{\Gamma((p-1)/2)^2}
 {\Gamma((p-2)/2)\Gamma(p/2)}
 \le2.
 \tag{5}
\]
Equation (5) applies only below one. It must not be extrapolated through
the spherical-ball discontinuity at radius one with center zero.

A state may also specify its own fixed right orthogonal basis
\(Q_\ell\in O(2)\): its legal reads are the columns of \(AQ_\ell\), and
its input query is \(Q_\ell^Tx\). The same bounds hold.

## Reducing output randomness

For each state, support, observed column, and query, replace a randomized
output by its conditional mean over internal randomness. The mean is a
Borel function wherever integrable. Extend it by zero elsewhere. At any
observed input used with positive probability on a source satisfying
(2), finite risk gives integrability. This replacement preserves (1)
and cannot increase (2), by Jensen's inequality.

It therefore suffices to prove the assertion for deterministic branch
outputs \(F_{\ell,1}(a,x)\) and \(F_{\ell,2}(b,x)\). The sampling of the
branch remains random.

## Deterministic support states have null cells

If \(\theta_\ell=1\), exactness at \(x=e_2\) requires
\[
 F_{\ell,1}(a,e_2)=b.
\]
For each fixed \(a\), uniform \(b\) ranges over \(S^{p-1}\cap a^\perp\).
This sphere has dimension \(p-2\ge1\), so each specified point has zero
conditional measure. Fubini's theorem makes the entire state cell null
under uniform Stiefel measure. The case \(\theta_\ell=0\) is symmetric,
using \(x=e_1\). There are only finitely many states. Removing these null
cells does not change their total covered measure, which is one.

## Exactness produces shared values

Fix a remaining state and abbreviate its probability by
\(0<\theta<1\). Write \(E\) for its source cell. The two coordinate-query
equations in (1) give
\[
 f(a)=g(b)\qquad ((a,b)\in E),
 \tag{6}
\]
where
\[
 \begin{aligned}
 f(a)&=(\theta F_1(a,e_1)-a,\ \theta F_1(a,e_2)),\\
 g(b)&=(-(1-\theta)F_2(b,e_1),\
                 b-(1-\theta)F_2(b,e_2)).
 \end{aligned}
 \tag{7}
\]
These are Borel maps from \(S^{p-1}\) into \(\mathbb R^{2p}\).

The atomic matching theorem says that under the uniform Stiefel law the
common value in (6) belongs, almost surely, to the countable intersection
of the atom sets of \(f_\#\sigma\) and \(g_\#\sigma\). It applies to the
cell because its match event is a subset of the unrestricted match event.
It does not require the cell to contain an open set, and it does not
give a finite number of atoms.

Index these shared atoms by \(y_i=(y_{i,1},y_{i,2})\). For a frame in
\(E\) with shared value \(y_i\), direct substitution in the two branch
errors gives
\[
 \begin{aligned}
 R(A,e_1)&=\frac{\|(1-\theta)a+y_{i,1}\|_2^2}
                          {\theta(1-\theta)},\\
 R(A,e_2)&=\frac{\|-\theta b+y_{i,2}\|_2^2}
                          {\theta(1-\theta)}.
 \end{aligned}
 \tag{8}
\]
Therefore (2) puts the two columns in the balls
\[
 \left\|a+\frac{y_{i,1}}{1-\theta}\right\|_2
       \le\delta_a:=\sqrt{\frac{C\theta}{1-\theta}},
 \qquad
 \left\|b-\frac{y_{i,2}}{\theta}\right\|_2
       \le\delta_b:=\sqrt{\frac{C(1-\theta)}{\theta}}.
 \tag{9}
\]
The product of the radii is \(C\). In particular, if \(C<1\), one
fixed side for this state has radius at most \(\sqrt C<1\).
Choose the first side when \(\theta\le1/2\), and the second otherwise.

## Spherical balls of radius less than one

For \(0\le\delta<1\) and any center \(z\in\mathbb R^p\),
\[
 \sigma\{v\in S^{p-1}:\|v-z\|_2\le\delta\}
 \le \frac12\delta^{p-1}.
 \tag{10}
\]
If \(z=0\), the intersection is empty. Otherwise put \(r=\|z\|_2\).
Membership requires
\[
 v^T\frac z r\ge
 \frac{1+r^2-\delta^2}{2r}\ge\sqrt{1-\delta^2}.
 \tag{11}
\]
The second inequality follows by completing
\((r-\sqrt{1-\delta^2})^2\ge0\).

For \(q=(p-1)/2\), the normalized measure of that cap is
\[
 \frac12
 \frac{\int_0^{\delta^2}s^{q-1}(1-s)^{-1/2}\,ds}
      {\int_0^1s^{q-1}(1-s)^{-1/2}\,ds}
 \le\frac12\delta^{2q}.
 \tag{12}
\]
To see the inequality, substitute \(s=\delta^2u\) in the numerator,
divide by \(\delta^{2q}\), and use
\((1-\delta^2u)^{-1/2}\le(1-u)^{-1/2}\).
The radius-zero case follows directly by nonatomicity.

## Bounding an entire advice cell

Intersect \(f^{-1}\{y_i\}\) and \(g^{-1}\{y_i\}\) with their respective
balls from (9), and call the resulting sets \(A_i\) and \(B_i\).
Each family is countable and disjoint. Almost every frame of \(E\)
belongs to one matching pair \(A_i\times B_i\).

Let \(T\) be equatorial averaging. The uniform Stiefel measure of a pair
rectangle is \(\langle\mathbf1_{A_i},T\mathbf1_{B_i}\rangle\).
The small-set estimate, together with self-adjointness of \(T\), gives
\[
 \sum_i\langle\mathbf1_{A_i},T\mathbf1_{B_i}\rangle
 \le\sqrt{D_p}\,h^{(p-2)/(2(p-1))}
 \tag{13}
\]
if every cell on either one of the two sides has sphere measure at most
\(h\). On the side selected after (9), (10) supplies
\[
 h=\frac12 C^{(p-1)/2}.
 \tag{14}
\]
Thus the Stiefel measure of this state cell is at most
\[
 \sqrt{D_p}\,
 2^{-(p-2)/(2(p-1))}C^{(p-2)/4}.
 \tag{15}
\]
This controls a countable collection of shared values without assigning
an artificial finite count to them.

The at most \(N\) state cells cover the whole Stiefel orbit. Summing (15)
proves (5). Dropping its factor \(2^{-(p-2)/(2(p-1))}\le1\) and using
\(D_p\le2\) gives
\[
 1\le N\sqrt2\,C^{(p-2)/4},
\]
which is (3) when \(C<1\). For \(C\ge1\), (3) holds directly. At \(C=0\),
(14)--(15) make every state cell null, contradicting the cover. This
also treats that endpoint without taking a logarithm.

## Fixed basis per label

For state \(\ell\), apply the preceding argument to
\(\widetilde A=AQ_\ell\) and queries
\(x=Q_\ell e_1,Q_\ell e_2\). Right multiplication preserves uniform
Stiefel measure. The transformed cell may differ between labels; each
cell has the same measure as its own transform, so (15) still bounds
each original cell. Summing those measures proves the same result.
The basis is fixed by the label. A further source-dependent basis
inside the label is outside this statement.

## Boundary and consequence

The theorem permits arbitrary Borel nonlinear branch outputs, arbitrary
measurable source-selected labels, and countably many shared residual
values within each label. It uses exact unbiasedness, a fixed sampling
probability within each label, and exactly one column read. It does not
cover a mixture of zero-column and two-column reads with the same mean
read count, a query-dependent sampling schedule, arbitrary page
encodings, or continuous uncharged resident advice.

At fixed error target \(0<C_0<1\), a protocol with error at most \(C_0\)
requires
\[
 b\ge \frac{p-2}{4}\log_2(1/C_0)-\frac12
 \tag{16}
\]
bits of source-selected state. A finite description cannot silently
remove the unbiased error cost in a growing output dimension.
This is a mathematical consequence in a declared column-oracle model,
not a completed physical storage or page-accounting theorem for Cassette.

The proof combines exact-mean identities, a compact spherical averaging
operator, atomic matching, and a weak-Lorentz small-set estimate.
Whether the complete statement is already known, is a routine
consequence in another formulation, or has sufficient application
significance remains to be established.

## Proof dependencies

- [Complete independent reconstruction](/Users/drewwiberg/cassette/pure_math_astra/notes/two_column_unbiased_finite_advice_lower_independent_review.md).
- [Atomic matching](/Users/drewwiberg/cassette/pure_math_astra/notes/stiefel_orthogonality_operator_atomic_matching.md).
- [Independent reconstruction and exact-mean bundle](/Users/drewwiberg/cassette/pure_math_astra/notes/stiefel_orthogonality_operator_atomic_matching_independent_review.md).
- [Small-set estimate](/Users/drewwiberg/cassette/pure_math_astra/notes/stiefel_orthogonality_small_set_bound.md).
