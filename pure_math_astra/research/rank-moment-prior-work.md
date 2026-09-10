# Prior-work challenge: unbiased rank-constrained second moments

Status: bounded source check for
[`rank_constrained_second_moments.md`](../notes/rank_constrained_second_moments.md).
No originality claim follows from this note.

The local theorem characterizes the upper second moments of an unbiased,
almost-sure rank-\(s\) random matrix:

\[
 \exists Z:\ \mathbb EZ=R,\quad \operatorname{rank}Z\leq s\ \mathrm{a.s.},
 \quad \mathbb E Z^*Z\preceq H
\]

if and only if

\[
 H\succeq R^*R,\qquad \operatorname{tr}(RH^\dagger R^*)\leq s.
\tag{M}
\]

## Barnes--Cameron--Howard checked in full

Leighton Pate Barnes, Stephen Cameron, and Benjamin Howard,
[*On Unbiased Low-Rank Approximation with Minimum Distortion* (arXiv
v2, 2026), pp. 1--6](https://arxiv.org/pdf/2505.09647), studies the same
unbiased, almost-sure rank cap. Its objective is the scalar

\[
 \mathbb E\lVert Z-R\rVert_F^2
 =\operatorname{tr}(\mathbb EZ^*Z-R^*R).
\]

Its full proof does not state (M). The lower bound on pp. 3 and 5 fixes a
matrix \(B\), uses unbiasedness to rewrite the scalar Frobenius variance,
then bounds it by the best deterministic rank-\(s\) approximation to
\(R-B\) through Eckart--Young--Mirsky. The construction on pp. 2 and 5
uses singular-component probabilities proportional to singular values, with
large components included deterministically. It establishes the optimal
*trace* of the second moment, but does not control its Loewner order and does
not introduce a candidate matrix \(H\).

Therefore (M) is not an immediate consequence of the theorem proved in that
paper by simply whitening: its Frobenius-optimal sampler generally has a
different second-moment matrix from the sampler in (M). The scalar frontier
obtained by minimizing \(\operatorname{tr}H\) under (M) does reproduce the
same proportional-to-singular-value allocation, so BCH is a close prior
result for that corollary.

The paper itself cites F. Benzing, M. M. Gauy, A. Mujika, A. Martinsson, and
A. Steger, [*Optimal Kronecker-Sum Approximation of Real Time Recurrent
Learning* (ICML 2019), supplementary Appendix
A](https://proceedings.mlr.press/v97/benzing19a/benzing19a-supp.pdf).
That appendix also defines unbiased rank-\(s\) matrix approximation with
Frobenius variance, proves a dual scalar lower bound, and constructs
Frobenius optimizers. It likewise contains no matrix upper-second-moment
feasibility theorem of form (M).

## The closest convex-analytic framework

Dimitris Bertsimas, Ryan Cory-Wright, and Jean Pauphilet,
[*A New Perspective on Low-Rank Optimization* (2023), Sections 3.1--3.5,
especially Theorem 3.2](https://arxiv.org/abs/2105.05947), proves exact
convex-hull descriptions for classes of rank-constrained spectral epigraphs.
It uses two ingredients that also occur in (M):

* the convex hull of rank-at-most-\(s\) orthogonal projections is
  \(\{Y:0\preceq Y\preceq I,\operatorname{tr}Y\leq s\}\); and
* the quadratic matrix perspective contains \(X^*Y^\dagger X\), with a
  Schur-complement representation.

That paper concerns deterministic low-rank optimization and scalar spectral
objectives. It does not formulate random unbiased matrices, the upper moment
matrix \(H\), or equivalence (M). It nevertheless identifies the main
convex-analytic pieces as established machinery.

## Assessment of the intellectual step

The proof of (M) is short after whitening. Necessity is the standard block
moment inequality
\(
\bigl[\begin{smallmatrix}K&R\\R^*&H\end{smallmatrix}\bigr]\succeq0
\)
with \(K\) an expected rank-\(s\) range projection. For sufficiency, the
singular values \(\theta_i\) of \(RH^{\dagger/2}\) satisfy
\(0\leq\theta_i\leq1\) and \(\sum_i\theta_i^2\leq s\); the polytope
\(
\{\pi\in[0,1]^r:\sum_i\pi_i\leq s\}
\)
is the convex hull of incidence vectors of subsets of size at most \(s\).
Sampling with marginals \(\pi_i=\theta_i^2\) gives the required moment
bound directly.

**Reasoned assessment.** The sources checked do not state this exact
matrix-valued moment equivalence. But its proof combines standard Schur
complements, projection-polytope convexification, and singular-value
sampling. It should therefore be treated as a routine strengthening of the
known unbiased low-rank approximation framework until a source search or a
distinct consequence establishes otherwise. The exact formula remains useful
as a model correction: any objective monotone in \(\mathbb EZ^*Z-R^*R\) can
be posed over the explicit feasible region in (M), but it has no direct
encoded-byte or page-access content.
