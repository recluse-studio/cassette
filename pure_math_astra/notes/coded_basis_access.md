# Unrestricted coded-basis rank access

This note concerns an ideal finite-dimensional estimator class. It is separate
from physical page access: a random access may return a globally coded rank-
limited operator. The result does not assert novelty, does not establish a
Cassette implementation, and does not price exact finite encodings.

Let \(R\in\mathbb F^{p\times q}\) have rank \(r>0\), with nonzero singular
values \(\sigma_1,\ldots,\sigma_r\). Fix an integer \(s\geq1\). Consider all
random matrices \(Z\) such that

\[
 \mathbb E Z=R,\qquad \operatorname{rank}Z\leq s\quad\text{almost surely}.
\]

Their worst-unit-query mean-square covariance is

\[
 \lambda_{\max}\bigl(\mathbb E[Z^*Z]-R^*R\bigr).
\]

## Theorem

If \(s\geq r\), the minimum is zero. If \(1\leq s<r\), the minimum is the
unique \(t>0\) satisfying

\[
 \sum_{i=1}^r\frac{\sigma_i^2}{\sigma_i^2+t}=s. \tag{1}
\]

### Necessity

Put \(H=\mathbb E[Z^*Z]\), and let \(P_Z\) be the orthogonal projection onto
\(\operatorname{ran}Z\). Since \(P_ZZ=Z\),

\[
 \begin{pmatrix}P_Z&Z\\Z^*&Z^*Z\end{pmatrix}
 =\begin{pmatrix}P_Z\\Z^*\end{pmatrix}
  \begin{pmatrix}P_Z&Z\end{pmatrix}\succeq0.
\]

Taking expectations gives

\[
 \begin{pmatrix}K&R\\R^*&H\end{pmatrix}\succeq0,
 \qquad K=\mathbb E P_Z,
 \qquad \operatorname{tr}K\leq s. \tag{2}
\]

The generalized Schur complement of (2) gives

\[
 \operatorname{tr}(RH^\dagger R^*)\leq\operatorname{tr}K\leq s. \tag{3}
\]

Here the range condition needed for the pseudoinverse follows from positivity of
the block matrix. Suppose the covariance has largest eigenvalue at most \(t\).
Then \(H-R^*R\preceq tI\), hence

\[
 H\preceq R^*R+tI=:M.
\]

For every vector \(y\in\operatorname{ran}H\), the variational identity

\[
 y^*H^\dagger y
 =\sup_x\{2\operatorname{Re}(x^*y)-x^*Hx\}
 \geq y^*M^{-1}y
\]

uses \(H\preceq M\). Apply it to \(y=R^*x\), trace over an orthonormal basis,
and combine with (3):

\[
 s\geq\operatorname{tr}(RH^\dagger R^*)
 \geq\operatorname{tr}(R(R^*R+tI)^{-1}R^*)
 =\sum_{i=1}^r\frac{\sigma_i^2}{\sigma_i^2+t}. \tag{4}
\]

For \(s<r\), the last function is continuous and strictly decreasing from \(r\)
to zero, so (4) forces \(t\) to be at least the unique root in (1). For
\(s\geq r\), taking \(Z=R\) gives the zero lower endpoint.

### Sufficiency

Write a singular-value decomposition

\[
 R=\sum_{i=1}^r\sigma_i u_iv_i^*.
\]

For the root \(t\) in (1), set

\[
 \pi_i=\frac{\sigma_i^2}{\sigma_i^2+t}.
\]

Then \(0<\pi_i<1\) and \(\sum_i\pi_i=s\). The hypersimplex identity says
that every vector in \([0,1]^r\) with integer coordinate sum \(s\) is a convex
combination of incidence vectors of \(s\)-element subsets. Indeed, a vertex of
the polytope \(\{z\in[0,1]^r:\sum_i z_i=s\}\) cannot have two fractional
coordinates, because they admit opposite small perturbations that retain the sum.
An integer sum then forces every vertex to be a zero-one vector with exactly \(s\)
ones. Choose a random subset \(S\subseteq\{1,\ldots,r\}\) of exact size \(s\) with
\(\Pr(i\in S)=\pi_i\), and define

\[
 Z_S=\sum_{i\in S}\frac{\sigma_i}{\pi_i}u_iv_i^*.
\]

Then \(\mathbb EZ_S=R\), \(\operatorname{rank}Z_S\leq s\), and orthogonality
of the singular vectors gives

\[
 \mathbb E[Z_S^*Z_S]
 =\sum_{i=1}^r\frac{\sigma_i^2}{\pi_i}v_iv_i^*
 =\sum_{i=1}^r(\sigma_i^2+t)v_iv_i^*.
\]

Subtracting \(R^*R\) leaves \(t\) on the right singular subspace and zero on
its orthogonal complement. The largest covariance eigenvalue is exactly \(t\),
which meets the lower bound. \(\square\)

## Scope and resource boundary

The theorem permits arbitrary exact real or complex singular vectors and a random
rank-\(s\) coded operator. It is not a literal page-column theorem. Forming
\(Z_Sx\) requires access to the selected left singular vectors and resident or
otherwise declared right-basis coefficients \(v_i^*\); the latter alone require
on the order of \(rq\) scalars in a dense representation. Actual byte cost also
depends on finite precision, encoding, decoder work, subset metadata, physical
page layout, and the trace-level access schedule. Those resources must be declared
before this ideal covariance optimum can alter a Cassette certificate.
