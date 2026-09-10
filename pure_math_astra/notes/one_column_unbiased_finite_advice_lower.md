# Finite advice preserves the one-column unbiased error floor

Status: proved and independently reconstructed. The stronger
[conditional-cap theorem](/Users/drewwiberg/cassette/pure_math_astra/notes/finite_advice_unbiased_static_conditional_cap_lower.md)
supersedes this bound and covers general static support laws. The
rectangular-operator argument remains method history. No originality or
sufficient application-significance finding is made.

## Model and conclusion

Let \(p>q\ge2\). A source is an ordered orthonormal \(q\)-frame
\(A=[a_1,\ldots,a_q]\in{\cal V}_{p,q}\). A measurable encoder selects
one of at most \(N\) fixed states. In a state \(\ell\), a decoder samples
exactly one column, with probabilities
\((\pi_{\ell,1},\ldots,\pi_{\ell,q})\) fixed for that state. It may return
any Borel function of the state, observed column, and query, with
additional internal randomness. Its random conditional law depends only
on those inputs and is Borel; its seed is independent of the source.

Assume exact mean recovery for every source and query, and uniform risk
\[
 \mathbb E[\widehat y\mid A,x]=Ax,\qquad
 \sup_{A,\ \|x\|=1}\mathbb E[\|\widehat y-Ax\|^2\mid A,x]\le C.
 \tag{1}
\]
Define
\[
 \kappa_{p,q}=
 \frac{\Gamma((p-q+1)/2)\Gamma((p-1)/2)}
      {\Gamma((p-q)/2)\Gamma(p/2)},\qquad
 D_{p,q}=\frac{p-1}{p-q}\kappa_{p,q}.
 \tag{2}
\]
Then
\[
 \boxed{\quad C\ge(q-1)
 \left(\frac{p-q}{p-1}\right)^{2/(p-q)}
 N^{-4/(p-q)}.\quad}
 \tag{3}
\]
In particular, when \(p\ge2q\) and \(N\le2^b\),
\[
 C\ge(q-1)\,2^{-(4b+2)/(p-q)}.
 \tag{4}
\]
If \(p\ge2q\) and \(b=o(p-q)\), this tends to the exact no-advice
one-column value \(q-1\) in relative terms. Uniform sampling, with output
\(q a_jx_j\), attains that value for every frame and every unit query.

For \(0<C<q-1\), the proof gives the stronger intermediate inequality
\[
 1\le N\sqrt{D_{p,q}}\,
 2^{-(p-q)/(2(p-1))}
 \left(\frac{C}{q-1}\right)^{(p-q)/4}.
 \tag{5}
\]
As in the two-column argument, (5) is restricted to \(C<q-1\).

A state may choose a fixed right orthogonal basis \(Q_\ell\in O(q)\).
Reads then return columns of \(AQ_\ell\), and queries transform by
\(Q_\ell^T\). All conclusions remain valid.

## A rectangular orthogonality operator

Let \(\sigma\) be uniform measure on \(S^{p-1}\), and let \(\tau\) be
uniform measure on \({\cal V}_{p,q-1}\). Couple \(a\) and \(W\) by a
uniform \(q\)-frame: \(a\) is one column and \(W\) is the ordered
remaining frame. Thus \(a\) is uniform on the sphere perpendicular to
\(W\), and \(W\), conditional on \(a\), is a uniform \((q-1)\)-frame in
\(a^\perp\).

Define
\[
 T:L^2(\sigma)\longrightarrow L^2(\tau),\qquad
 (Tf)(W)=\mathbb E[f(a)\mid W].
 \tag{6}
\]
Its adjoint averages \(W\) conditional on \(a\). Consequently \(T^*T\)
samples \(W\perp a\), then \(a'\perp W\). For fixed \(W\), the subspace
\(W^\perp\) has dimension \(p-q+1\) and contains \(a\). The density of
\(t=a^Ta'\) is proportional to
\((1-t^2)^{(p-q-2)/2}\). Comparing with the sphere-coordinate density
\((1-t^2)^{(p-3)/2}\), and using rotational invariance around \(a\),
gives
\[
 (T^*Tf)(a)=\int k(a^Ta')f(a')\,d\sigma(a'),\qquad
 k(t)=\frac{\kappa_{p,q}}{(1-t^2)^{(q-1)/2}}.
 \tag{7}
\]
The normalizing constant is exactly (2), by the two coordinate-density
normalizers. Since \(p>q\), the resulting endpoint exponent
\((p-q-2)/2\) is greater than \(-1\); the kernel is integrable.

Truncating \(k\) gives Hilbert--Schmidt operators. Its positive tails
have constant row and column integrals tending to zero, so Schur's
inequality proves that \(T^*T\) is compact. If \(f_n\) is weakly null,
\[
 \|Tf_n\|^2=\langle f_n,T^*Tf_n\rangle\longrightarrow0.
\]
Hence \(T\) is compact. This proof includes the boundary \(p=q+1\),
where the second-step coordinate density has exponent \(-1/2\).

## Shared values and small cells

The compact-operator atomic matching proof applies between these two
different probability spaces without alteration. Explicitly, for Borel
maps \(f:S^{p-1}\to\mathbb R^d\) and
\(g:{\cal V}_{p,q-1}\to\mathbb R^d\), the match event
\(f(a)=g(W)\) has, almost surely, a value in the countable set
\[
 \operatorname{At}(f_\#\sigma)\cap\operatorname{At}(g_\#\tau).
 \tag{8}
\]
For completeness, partition the part where neither marginal has atoms
into finite value cells of marginal masses at most \(\delta\).
The sum of their matching rectangle measures is
\(\sum_i\langle 1_{B_i},T1_{A_i}\rangle\). Approximate the compact
operator \(T\) in norm by a finite-rank operator. The norm remainder
contributes at most \(\varepsilon\sum_i\sqrt{\sigma(A_i)\tau(B_i)}
\le\varepsilon\). Each rank-one term contributes at most a fixed
product of two \(L^2\) norms times
\(\sqrt{\max_i\sigma(A_i)\max_i\tau(B_i)}\), which tends to zero.
Atoms of only one marginal give null matches by a countable union.
This proves (8).

Put
\[
 r=\frac{p-1}{q-1}>1,\qquad
 \alpha=1-\frac1r=\frac{p-q}{p-1}.
 \tag{9}
\]
The polar-cap estimate gives the kernel tail
\[
 \sigma\{a':k(a^Ta')>\lambda\}
 \le \left(\frac{\kappa_{p,q}}{\lambda}\right)^r.
 \tag{10}
\]
Indeed, for \(\lambda>\kappa_{p,q}\) the two caps have angular sine
\((\kappa_{p,q}/\lambda)^{1/(q-1)}\), and their total measure is at
most that sine to the power \(p-1\). For smaller \(\lambda\), the
right-hand side is at least one.

Layer-cake integration, split where
\((\kappa_{p,q}/\lambda)^r=\sigma(B)\), yields
\[
 \sup_a\int_B k(a^Ta')\,d\sigma(a')
 \le \frac{r}{r-1}\kappa_{p,q}\,\sigma(B)^\alpha
 =D_{p,q}\sigma(B)^\alpha.
 \tag{11}
\]
The kernel integrates to one and
\((1-t^2)^{-(q-1)/2}\ge1\), so
\(0<\kappa_{p,q}\le1\). In particular,
\[
 D_{p,q}\le\frac{p-1}{p-q}.
 \tag{12}
\]

For countable disjoint sphere cells \(A_i\) and frame cells \(B_i\),
with \(\sup_i\sigma(A_i)\le h\), (11) gives
\[
 \begin{aligned}
 \|T1_{A_i}\|^2
 &=\langle1_{A_i},T^*T1_{A_i}\rangle\\
 &\le D_{p,q}\sigma(A_i)^{1+\alpha}
 \le D_{p,q}h^\alpha\sigma(A_i).
 \end{aligned}
\]
Cauchy--Schwarz across both the operator pairing and the cell index gives
\[
 \sum_i\langle1_{B_i},T1_{A_i}\rangle
 \le\sqrt{D_{p,q}}\,h^{\alpha/2}.
 \tag{13}
\]
Each family's total measure is at most one. Thus (13) controls countably
many shared values, without a finite atom-count assumption.

## One coordinate query per state

Conditional means remove internal output randomness by Jensen's
inequality, preserving exactness and reducing risk. Their Borel
extensions outside integrable used inputs may be arbitrary.

If a state has \(\pi_j=0\), exactness at \(x=e_j\) predicts \(a_j\)
from the other columns alone. Conditional on those columns, \(a_j\)
is uniform on a sphere of dimension \(p-q\ge1\). Each specified point
has zero conditional measure. Such a state cell has zero Stiefel measure.
We may therefore discard these finitely many null cells.

For a remaining state choose an index with \(0<\pi_j\le1/q\), put
\(\theta=\pi_j<1\), write \(a=a_j\), and write \(W\) for the remaining
columns. Let \(F(a)\) be the branch output for column \(j\) at \(x=e_j\),
and let
\[
 H(W)=\frac1{1-\theta}\sum_{i\ne j}\pi_i F_i(a_i,e_j).
 \tag{14}
\]
This is a Borel function of the remaining frame. Exactness on the state
cell says
\[
 \theta F(a)+(1-\theta)H(W)=a.
 \tag{15}
\]
Define \(f(a)=\theta F(a)-a\) and \(g(W)=-(1-\theta)H(W)\).
Equation (15) is precisely their equality. By (8), their shared value
belongs to a countable set of atoms, almost everywhere in the state cell.

On a shared value \(c\), Jensen's inequality over the branches other
than \(j\), followed by (15), gives the coordinate-query risk lower bound
\[
 \begin{aligned}
 C&\ge\theta\|F(a)-a\|^2+
                (1-\theta)\|H(W)-a\|^2\\
  &=\frac{\|(1-\theta)a+c\|^2}{\theta(1-\theta)}.
 \end{aligned}
 \tag{16}
\]
Consequently
\[
 \left\|a+\frac{c}{1-\theta}\right\|
 \le\sqrt{\frac{C\theta}{1-\theta}}
 \le\sqrt{\frac{C}{q-1}}=:\delta.
 \tag{17}
\]
If \(C<q-1\), then \(\delta<1\). A Euclidean ball of that radius,
with any center, cuts sphere measure at most
\[
 h=\frac12\delta^{p-1}
   =\frac12\left(\frac C{q-1}\right)^{(p-1)/2}.
 \tag{18}
\]
The proof is the elementary cap calculation in the two-column note:
the ball lies in the cap with axial threshold \(\sqrt{1-\delta^2}\);
substitution into the beta integral bounds its measure by
\(\delta^{p-1}/2\).

For each shared atom \(c_i\), let \(A_i=f^{-1}\{c_i\}\) intersected
with the ball (17), and let \(B_i=g^{-1}\{c_i\}\). These two families
are countable and disjoint. The state cell is almost everywhere contained
in their matching rectangles. Equations (13) and (18) therefore bound
its measure by
\[
 \sqrt{D_{p,q}}\,
 2^{-(p-q)/(2(p-1))}
 \left(\frac C{q-1}\right)^{(p-q)/4}.
 \tag{19}
\]
The at most \(N\) state cells cover the orbit, proving (5).
Using (12) and discarding the power of two in (19) gives (3) when
\(0<C<q-1\). At \(C=0\), every cell has measure zero, contradicting
the cover. At \(C\ge q-1\), (3) follows directly.

When \(p\ge2q\), (12) is at most two. Substituting \(N\le2^b\) gives
(4). For uniform sampling and output \(q a_jx_j\), orthonormality gives
\(\mathbb E\|\widehat y\|^2=q\|x\|^2\), while exactness gives
\(\|Ax\|^2=\|x\|^2\); hence the risk equals
\((q-1)\|x\|^2\). This verifies the stated attainable comparison.

## Bases, limits, and the open extension

For a label-specific right basis \(Q_\ell\), work on the transformed
cell \(AQ_\ell\) and use original query \(Q_\ell e_j\). Stiefel measure
and unit query norm are preserved. Each transformed cell has the same
measure as its original cell, so the finite-cell sum still applies.

This theorem concerns exactly one observed column and a static
probability vector per state. It does not cover arbitrary supports of
size \(s>1\), a source-dependent probability vector inside one state,
query-dependent sampling, or general page encodings. The condition
\(p>q\) is used in the nonatomic missing-column conditional law and in
the compactness of the rectangular operator.

For a relative target \(C\le\zeta(q-1)\), \(0<\zeta<1\), and
\(p\ge2q\), (4) requires
\[
 b\ge\frac{p-q}{4}\log_2(1/\zeta)-\frac12.
 \tag{20}
\]
The earlier lower bound for biased outputs has a different error scale.
Exact unbiasedness now preserves the full one-column error scale in
the small-advice regime. Whether an analogous result holds at the
intermediate read caps used by the equicorrelation adaptivity example
remains unresolved. This supporting theorem does not yet extend that
example to source-trained nonlinear decoders.

## Local proof sources

- [Complete independent reconstruction](/Users/drewwiberg/cassette/pure_math_astra/notes/one_column_unbiased_finite_advice_lower_independent_review.md).
- [Two-column proof and cap bound](/Users/drewwiberg/cassette/pure_math_astra/notes/two_column_unbiased_finite_advice_lower.md).
- [Compact atomic matching](/Users/drewwiberg/cassette/pure_math_astra/notes/stiefel_orthogonality_operator_atomic_matching.md).
- [Independent atomicity review](/Users/drewwiberg/cassette/pure_math_astra/notes/stiefel_orthogonality_operator_atomic_matching_independent_review.md).
- [Equatorial small-set estimate](/Users/drewwiberg/cassette/pure_math_astra/notes/stiefel_orthogonality_small_set_bound.md).
