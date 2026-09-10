# Encoded query bases change the page-access model

Status: model correction and supporting mathematics. This note neither changes
the Cassette model nor claims novelty.

## 1. The fixed-column result has a narrow access hypothesis

Let an operator have a factorization

\[
 A=PF,\qquad P\in\mathbb F^{p\times m},\quad F\in\mathbb F^{m\times q}.
\]

If \(F\) is resident, a query first forms \(z=Fx\), then a paged-column
draw returns \(P_{:j}z_j/\pi_j\). Its expectation is \(PFx=Ax\). This
preserves the operator and the query flattening, but it changes the paged
coordinates from the original columns of \(A\) to the columns of \(P\).

For example, let \(R=uw^*\), where every entry of \(w\) may be nonzero.
The original residual has many nonzero columns. Yet with \(P=u\) and
\(F=w^*\), it has one paged column. Taking that column with probability one
returns \(Rx\) exactly. Thus a zero-variance theorem stated in terms of
visible original columns applies only when those columns are the admissible
pages. It does not survive an allowed resident change of query coordinates.

The distinction carries a real resource cost. A dense resident \(F\) has
\(mq\) scalar coefficients before metadata, quantization, or decoder costs;
applying it also has a query-time cost. The rank of \(F\), or of \(PF\), does
not establish an encoded-byte bound. Conversely, a page theorem that omits
the possibility of resident \(F\) cannot be a lower bound for a model that
admits it.

## 2. Unrestricted unbiased rank-\(s\) operator variance

For a fixed \(R\in\mathbb F^{p\times q}\), define

\[
 V_s(R)=\inf_{\substack{\mathbb E Z=R\\
                    \operatorname{rank}Z\leq s\ \mathrm{a.s.}}}
 \lambda_{\max}\!\left(\mathbb E Z^*Z-R^*R\right).
\tag{1}
\]

Here \(Z\) is an arbitrary random linear operator; (1) does not itself
charge an encoding, a page layout, or evaluation of a realization of \(Z\).
Let \(\sigma_1,\ldots,\sigma_r>0\) be the nonzero singular values of \(R\).

### Theorem

For an integer \(1\leq s<r\), there is a unique \(t>0\) satisfying

\[
 \sum_{i=1}^r\frac{\sigma_i^2}{\sigma_i^2+t}=s,
\tag{2}
\]

and \(V_s(R)=t\). If \(s\geq r\), then \(V_s(R)=0\), attained by
\(Z=R\). The result holds over either \(\mathbb R\) or \(\mathbb C\).

### Proof: construction

Write \(R=\sum_{i=1}^r\sigma_i u_iv_i^*\). For the \(t\) in (2), put

\[
 \pi_i=\frac{\sigma_i^2}{\sigma_i^2+t}.
\]

Then \(0<\pi_i<1\) and \(\sum_i\pi_i=s\). The hypersimplex identity says
that every vector in \([0,1]^r\) whose coordinates sum to the integer \(s\)
is a convex combination of incidence vectors of \(s\)-element subsets.
Choose an \(s\)-element random subset \(S\) having these marginals and set

\[
 Z_S=\sum_{i\in S}\frac{\sigma_i}{\pi_i}u_iv_i^*.
\]

Each realization has rank at most \(s\), and \(\mathbb EZ_S=R\). The left
singular vectors are orthonormal, so no cross terms remain in \(Z_S^*Z_S\):

\[
 \mathbb EZ_S^*Z_S-R^*R
 =\sum_{i=1}^r\sigma_i^2(\pi_i^{-1}-1)v_iv_i^*
 =t\sum_{i=1}^rv_iv_i^*.
\]

Its largest eigenvalue is \(t\), proving \(V_s(R)\leq t\).

### Proof: lower bound

Let \(Z\) be any admissible estimator, put \(H=\mathbb EZ^*Z\), and let
\(P_Z\) be the orthogonal projection onto \(\operatorname{ran}Z\). For each
outcome,

\[
 \begin{pmatrix}P_Z&Z\\ Z^*&Z^*Z\end{pmatrix}
 =\begin{pmatrix}P_Z\\Z^*\end{pmatrix}
  \begin{pmatrix}P_Z&Z\end{pmatrix}\succeq0.
\]

Taking expectations gives

\[
 \begin{pmatrix}K&R\\R^*&H\end{pmatrix}\succeq0,
 \qquad K=\mathbb EP_Z,\qquad \operatorname{tr}K\leq s.
\tag{3}
\]

The generalized Schur complement in (3) yields
\(RH^\dagger R^*\preceq K\); hence

\[
 s\geq\operatorname{tr}(RH^\dagger R^*).
\tag{4}
\]

Suppose \(\lambda_{\max}(H-R^*R)\leq c\). Then
\(H\preceq R^*R+cI\). The range inclusion supplied by (3), together with
order reversal under inversion on that range, gives

\[
 \operatorname{tr}(RH^\dagger R^*)
 \geq\operatorname{tr}\!\left(R(R^*R+cI)^{-1}R^*\right)
 =\sum_{i=1}^r\frac{\sigma_i^2}{\sigma_i^2+c}.
\tag{5}
\]

The right side strictly decreases in \(c>0\). Equations (2), (4), and (5)
therefore force \(c\geq t\). This proves the opposite inequality and the
theorem. \(\square\)

The construction can be realized in the encoded-basis form: choose
\(P_{:i}=\sigma_i u_i\) and let row \(i\) of \(F\) be \(v_i^*\). A sampled
subset reads at most \(s\) columns of \(P\), while \(F\) is dense resident
data. It is an illustrative scalar model, not a finite-byte Cassette claim.

## 3. Primary-source comparison

Erich Novak, [*Optimal Linear Randomized Methods for Linear Operators in
Hilbert Spaces* (1992), Section
3](https://www.researchgate.net/publication/220171688_Optimal_linear_randomized_methods_for_linear_operators_in_Hilbert_spaces),
studies random orthogonal projections \(S\circ P_\omega\) approximating a
compact diagonal operator \(S\). The method is an approximation, not an
unbiased estimator of \(S\). Its worst-unit-input mean-square error has
coordinate form \((1-W_i)\sigma_i^2\), and its optimal projection
inclusions satisfy \(W_i=1-\alpha/\sigma_i^2\) on their active set.

That is related water filling, but it is not (1): the latter requires
\(\mathbb EZ=R\), has covariance \(\mathbb EZ^*Z-R^*R\), and has marginal
probabilities \(\sigma_i^2/(\sigma_i^2+t)\). Novak's theorem therefore does
not verify the displayed formula, nor does it show it is new.

The closest located source is Leighton Pate Barnes, Stephen Cameron, and
Benjamin Howard, [*On Unbiased Low-Rank Approximation with Minimum
Distortion* (2025), Sections 1--3](https://arxiv.org/abs/2505.09647). It
optimizes over all unbiased, almost-sure rank-\(s\) random matrices, as in
(1), but its objective is \(\mathbb E\lVert Z-R\rVert_F^2\). Its singular
component sampler uses probabilities proportional to \(\sigma_i\), with
always-included heavy components. That is a different optimization from the
spectral covariance criterion in (1), which yields (2). The source is a close
structural precedent; this bounded check found no source proving the exact
operator-norm covariance value above. That is a search limit, not a novelty
claim.

## 4. Consequence for further work

The correct unresolved resource question is not abstract rank. It is whether a
declared resident transform \(F\), including its encoded bytes and query
evaluation, together with the paged representation and access cost of \(P\),
can improve a stated Cassette certificate. Any lower bound must name that
combined class. Any claimed benefit must charge both halves of the
factorization.
