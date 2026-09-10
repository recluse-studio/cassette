# Prior-work challenge: fixed-basis spectral covariance and pairwise designs

Status: bounded primary-source comparison, completed 5 September 2026.  This
note identifies nearby results and their precise limits.  It makes no
originality claim.

## The present mathematical problem

In the fixed coordinate basis, an outcome has the form
\[
 Z=RD_b,\qquad |\operatorname{supp} b|\leq s,\qquad \mathbb ED_b=I,
\]
with \(G=R^*R\).  Its covariance is
\[
 C=\mathbb E(D_b^*GD_b)-G,
\]
and the objective is \(\lambda_{\max}C\).  This is a worst-direction
quadratic criterion.  It permits arbitrary support-dependent weights; it is
not merely an inclusion-probability problem.

The two relevant internal results are the exact two-group parity value in
\(\texttt{two_group_parity_gap.md}\), and the marginal-attainment bound in
\(\texttt{coded_basis_rigidity.md}\).  The latter gives
\[
 \Phi_s(G)\geq u_s,\qquad
 \sum_i\frac{G_{ii}}{G_{ii}+u_s}=s.
\]
For diagonal \(G\), the bound is attainable by a fixed-size design with the
specified first-order inclusion probabilities.  Away from a diagonal Gram
matrix, the unresolved issue is the joint second moments and, with
support-dependent weights, more than those moments.

## Barnes et al.: a close support-budget analogue, but not this criterion

L. Barnes, S. Cameron, T. Chow, E. Cohen, K. Frankston, B. Howard,
F. Kochman, D. Scheinerman, and J. VanderKam, *Efficient Unbiased
Sparsification*, arXiv:2402.14925v2, 2024,
[full text](https://arxiv.org/html/2402.14925v2).

Their random vector \(Q\in\mathbb R^n\) is supported on at most \(m\)
coordinates and satisfies \(\mathbb EQ=p\).  Their objective is
\(\mathbb E\,\operatorname{Div}(Q,p)\), for either a
permutation-invariant divergence or an additively separable divergence.
Their squared-Euclidean example is therefore a scalar sum of coordinate
losses.  The central reduction optimizes survivor marginals and then invokes
a fixed-cardinality sampling law with those marginals.

This overlaps with the present model in three concrete ways:

1. it uses a hard support cap and unbiased, support-dependent coordinate
   weights;
2. it uses the same feasibility polytope for first-order inclusion
   probabilities, \(\sum_i\pi_i=m\), \(0\leq\pi_i\leq1\);
3. its heavy/light rule resembles diagonal water filling.

It does not settle the present problem.  A general quadratic loss
\((q-p)^*A(q-p)\) with non-diagonal \(A\) is not additively separable and
usually is not permutation invariant.  Barnes et al. explicitly list
squared Mahalanobis distance as an unanswered example of this kind.  Their
optimality proof neither controls the pair moments
\(\mathbb E(\overline b_i b_j)\) nor a spectral matrix inequality
\(C\preceq tI\).  Thus it does not prove marginal attainment, the
two-group parity formula, or an isospectral local law.

This is positive prior art for the *diagonal* water-filling mechanism and for
the fixed-cardinality marginal polytope.  It is not a collision with
fixed-basis worst-query covariance optimization.

## Argyriou--Foygel--Srebro: a deterministic convex hull, not a sampling law

A. Argyriou, R. Foygel, and N. Srebro, *Sparse Prediction with the
\(k\)-Support Norm*, arXiv:1204.5043v2, 2012,
[full text](https://arxiv.org/html/1204.5043v2).

This paper derives the \(k\)-support norm as the convex hull/relaxation of a
deterministic vector constraint: at most \(k\) nonzero coordinates together
with an \(\ell_2\) bound.  Its losses are prediction/regularization losses
over a deterministic coefficient vector.  It has no random unbiased
coordinate estimator, no fixed-cardinality support distribution, and no
second-moment matrix \(C\).

The norm's sorted-coordinate formula may be useful intuition for why
capped-proportional allocations recur.  It gives no theorem about the
spectral covariance objective above, pairwise balance, or local rotation of a
Gram matrix.  Treating it as a proof of any of those statements would be a
domain error.

## Pairwise inclusion designs: the closest direct survey-sampling source

L. Bondesson, *On Sampling with Prescribed Second-order Inclusion
Probabilities*, Scandinavian Journal of Statistics 39 (2012), 813--829,
[DOI](https://doi.org/10.1111/j.1467-9469.2012.00808.x).

Bondesson studies fixed-size sampling with prescribed second-order inclusion
probabilities.  The principal construction is a quadratic exponential
conditional-Poisson family, CP(2), with parameter fitting and sampling
methods.  This is directly relevant to the equal-weight
Horvitz--Thompson submodel: there,
\[
 \mathbb E(D_bGD_b)-G
\]
is determined by first- and second-order inclusion probabilities.  It
confirms that prescribed pair moments are a recognized fixed-size sampling
problem.

It still does not give a general solution to the present optimization.
The paper constructs and studies a particular design family; its abstract
does not claim that every feasible pair-moment array is representable, nor
that CP(2) minimizes \(\lambda_{\max}C\) for an arbitrary Hermitian Gram
matrix.  The present class is broader than equal-weight HT estimators, so a
pair-inclusion characterization alone would not decide it.

For comparison, J.-C. Deville and Y. Tillé, *Efficient balanced sampling:
the cube method*, Biometrika 91 (2004), 893--912,
[DOI](https://doi.org/10.1093/biomet/91.4.893), balances
Horvitz--Thompson totals for chosen auxiliary variables, with equal or
unequal first-order inclusions.  That is a linear balance constraint.  It is
not a theorem of prescribed pair inclusion or spectral covariance
optimality.  These sources establish a substantial neighbouring field, but
no source read here settles full fixed-basis spectral covariance
optimization.

## Assessment of the exact parity formula

The two-group formula is an elementary but nontrivial symmetric optimization
once the full arbitrary-weight covariance model has been formulated:
symmetrization, a two-variable positive quadratic form, and fixed-size
arithmetic produce its value.  It should not be described as novel merely
because these source papers do not state it.  The sources read here are not
an exhaustive novelty search, and they do not exclude an equivalent result
in survey-design, correlation-polytope, or optimal-design literature.

What is supported is narrower: neither Barnes et al. nor
Argyriou--Foygel--Srebro contains this covariance problem, and Bondesson's
prescribed-pair construction does not state the parity value or optimize this
spectral objective.

## Two-eigenvalue local-orbit proposal: exact qualification needed

Let
\[
 G_0=\operatorname{diag}(\alpha I_r,\beta I_{q-r}),\qquad \alpha\ne\beta,
\]
and let \(t\) solve
\[
 r\frac{\alpha}{\alpha+t}+(q-r)\frac{\beta}{\beta+t}=s.
\]
The diagonal optimum has within-block inclusion probabilities
\[
 \pi_\alpha=\frac{\alpha}{\alpha+t},\qquad
 \pi_\beta=\frac{\beta}{\beta+t}.
\]
For an infinitesimal cross-block rotation, the off-diagonal Gram block is
first order in the rotation angle, while the diagonal and within-block
changes are second order.

There is a direct sufficiency mechanism when
\(r\pi_\alpha\) and \((q-r)\pi_\beta\) are integers.  Select exactly those
numbers uniformly and independently inside the two blocks, use HT weights,
and retain the product law across blocks.  The cross pair moments then factor
exactly, so the first-order cross-block covariance vanishes.  The remaining
Gram perturbation is second order.  This proves an \(O(\theta^2)\) *upper
construction* for that block-symmetric setting.

The converse needs more hypotheses than the prospective wording states.  At
the diagonal equality point, equality in the coordinate Cauchy bounds forces
the HT magnitude on every selected coordinate.  If a dense first-order
cross-block direction is to have no first-order covariance, every cross
pair must factor.  Fixed total size then forces the number selected from
each block to be constant: summing the factorized cross moments gives zero
variance for that block count.  Hence its expectation must be integral.
This supports the claimed mechanism, but a complete theorem must explicitly
establish the equality conditions for arbitrary complex weights and phrase
the conclusion for a fixed rotation direction.

In particular, “uniform linear excess in every direction whose entries are
nonzero” is false if “uniform” means one positive constant over all such
directions: normalized dense directions can approach a direction with a
zero entry, and their first-order coefficient can tend to zero.  A valid
version would give a positive, direction-dependent linear coefficient under
a stated normalization and lower bound on the relevant cross entries.  The
quadratic marginal lower bound does not prove such a linear effect; it only
supplies a universal \(O(\theta^2)\) lower scale.

No source read in this bounded pass supplies a general theorem for this
local-orbit statement.  Its correctness and prior art need a separate proof
and a wider search before it can carry an originality claim.

