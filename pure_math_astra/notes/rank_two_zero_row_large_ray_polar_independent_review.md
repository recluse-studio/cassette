# Independent review: the generic zero-row large-ray polar witness

Verdict: correct under the stated fixed generic direction assumptions.  The
threshold is direction-dependent.  This is a useful resolved stratum, not
a uniform finite-polar theorem.

Let

\[
 K_0=\begin{pmatrix}R\\0\ 0\ 0\end{pmatrix},
\]

where every entry and every \(2\times2\) minor of \(R\in\mathbb R^{2\times3}\)
is nonzero.  For a selected column \(j\), set

\[
 a=(2\|R_{:,j}\|_2)^{-1},\quad
 u_{\rm top}=-aR_{:,j},\quad
 u_3=\sqrt3/2,\quad n=e_j/2.
\]

Then \(\|u\|_2=1\) and \(\|n\|_2=1/2\).

## Scalar and top two-by-two checks

For a top scalar in selected column \(j\), with
\(\kappa=R_{ij}\), the numerator gap after multiplying by
\(1+t^2\kappa^2\) is exactly

\[
 a^2\kappa^2-\frac14+ta\kappa^2.
\]

It is positive for sufficiently large \(t\), because the entry assumption
gives \(\kappa\ne0\).  All other top scalar constraints are contractions,
and zero-row scalar constraints have left side at most \(1/4<3/4\).

For \(E=\{1,2\}\), every \(B=K_{0,E,J}\) is invertible by the minor
assumption.  If \(j\in J\), write \(e\) for the position of the original
column \(j\) inside \(J\).  Since \(Be=R_{:,j}\),

\[
 u_{\rm top}^TB^{-T}n_J
 =(-aBe)^TB^{-T}(e/2)=-a/2.
\]

Hence the coefficient of \(t^{-1}\) in the polar left side is
\(-a\), as claimed.  It gives strict eventual feasibility.  If
\(j\notin J\), the same block is a strict finite-\(t\) contraction.

## Mixed and full supports

For \(E=\{i,3\}\), the block has one nonzero row \(v\).  Orthogonal
decomposition of \(n_J\) into \(\operatorname{span}(v^T)\) and
\(\ker v\) gives the exact large-\(t\) limit

\[
 u_i^2+\|P_{\ker v}n_J\|_2^2
 \le u_i^2+\frac14
 <u_i^2+\frac34=\|u_E\|_2^2.
\]

This verifies the rank-one mixed-block step and supplies a fixed strict
gap.

For full support, \(R\) has rank two.  The singular-value decomposition
of \(K_0\) gives

\[
 \lim_{t\to\infty}\mathcal P_{[3],[3]}(t;u,n)
 =\|u_{\rm top}\|_2^2+\|P_{\ker R}n\|_2^2
 \le\frac14+\frac14=\frac12<1.
\]

Thus the full “quarter plus quarter” bound is valid.

There are finitely many constraints.  Their strict eventual gaps yield
\(T(K_0)<\infty\).  The proof supplies no uniform \(T\): the scalar
growth and the inverse-block expansions deteriorate as a selected entry or
top \(2\times2\) minor approaches zero.  These generic assumptions are
therefore necessary for the stated proof route.

This direct large-ray subcase does not establish the arbitrary
rank-two finite-polar lemma, a stable perturbation theorem, or a Cassette
resource boundary.  It should not be treated as a substantive novelty
result on its own.
