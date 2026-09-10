# q4_query_adaptive_barrier_prior_art_comparison.md — bounded primary-source comparison for the real q=4, s=2 query-adaptive coefficient barrier; depends on ../notes/critical_scale_2x2_polar_lemma_proof.md, ../notes/exact_graph_chart_polar_bridge_review.md, ../../MATHS.md.

# Query-adaptive q=4 barrier: bounded prior-art comparison

## The statement assessed

For a real rank-two orthogonal projector \(P\) on \(\mathbb R^4\), put

\[
G_r(P)=P+r^2(I-P),\qquad 0<r\le 1,
\]

and define

\[
\Psi_2(G)=
\sup_{\|x\|_2=1}\
\inf_{\substack{\mathbb E Y=x\\ \|Y\|_0\le2\ {\rm a.s.}}}
\mathbb E\,(Y-x)^T G(Y-x).
\tag{1}
\]

The inner distribution may depend on \(x\). It must have exact coefficient
mean, and every realized output has at most two nonzero coordinates.

The two internal proof notes named above derive

\[
\Psi_2(G_r(P))\ge r/360
\quad\hbox{for every real rank-two }P\hbox{ and }0<r\le1.
\tag{2}
\]

For a coordinate rank-two projector, a query-dependent exact-mean
two-coordinate law gives \(\Psi_2\le r\). Thus this is a basis-uniform
order-\(r\) lower bound with a matching-order upper in at least one basis.
It is not a theorem about fixed samplers, arbitrary decoders, encoded byte
cost, or arbitrary representations.

This note compares (2) with three primary sources actually read on 6
September 2026. It does not infer originality from a bounded search.

## Closest source: efficient unbiased sparsification

Leighton Barnes, Stephen Cameron, Timothy Chow, Emma Cohen, Keith Frankston,
Benjamin Howard, Fred Kochman, Daniel Scheinerman, and Jeffrey VanderKam,
[*Efficient Unbiased Sparsification*](https://arxiv.org/abs/2402.14925),
arXiv:2402.14925v2, 24 July 2024. I read Definition I.2, Lemma 1 and its
proof, Theorems 1--2, and the stated reduction to inclusion probabilities.

Their Definition I.2 is nearly the inner feasible class in (1): for a fixed
\(p\in\mathbb R^n\), a random \(Q\) has at most \(m\) nonzero entries and
\(\mathbb EQ=p\). Lemma 1 conditions on the realized support facet and uses
Jensen's inequality to replace \(Q\) by one deterministic point on each
facet without increasing any convex divergence. This is the same
conditional-mean reduction used when formulating finite support-law
optimizations here.

Their Theorem 1 characterizes efficient laws for a convex
permutation-invariant divergence, among nonnegative outputs. Their Theorem
2 characterizes the optimum for a strictly convex additively separable
divergence. In particular, a *diagonal* weighted square loss
\(\sum_i g_i(Q_i-p_i)^2\) fits their separable framework after fixing a query.
Consequently, the coordinate-projector upper side of (2), and the
hard-support exact-mean optimization behind it, are established
sparsification territory. Their theorem is stated for a positive target in
one orthant; for squared loss, coordinate sign changes and deletion of zero
coordinates give the corresponding pointwise construction for an arbitrary
real query.

The source does not cover the lower side of (2). The quadratic form in (1)
is generally nonseparable when \(P\) is rotated; its off-diagonal terms
couple output coordinates. Theorem 2 therefore does not apply to
\(G_r(P)\) for an arbitrary \(P\). Its optimization is pointwise in a fixed
coordinate system and supplies no assertion that every rotated
rank-two/two-low-eigenvalue ellipsoid has a worst query with variance
\(\Omega(r)\). The source's own proof reduces separable loss to marginal
inclusion probabilities; the graph-chart polar argument in the internal
notes is needed precisely because those marginals no longer determine
off-diagonal covariance risk.

## Atomic geometry: the k-support norm

Andreas Argyriou, Rina Foygel, and Nathan Srebro,
[*Sparse Prediction with the k-Support Norm*](https://proceedings.neurips.cc/paper_files/paper/2012/file/99bcfcd754a98ce89cb86f73acc04645-Paper.pdf),
NeurIPS 2012. I read its convex-hull definition, variational formula, dual
calculation, and the displayed derivation of that dual.

The paper defines the \(k\)-support ball as

\[
\operatorname{conv}\{w:\|w\|_0\le k,\ \|w\|_2\le1\},
\tag{3}
\]

and proves that its dual norm is the Euclidean norm of the \(k\) largest
coordinates. This is the standard Euclidean atomic body underlying a hard
coordinate-support constraint. It explains why a Euclidean sparse mean
problem admits a finite atomic polar test.

It does not include the random exact-mean second-moment problem in (1).
In particular, its polar sections use the Euclidean \(\ell_2\) ball on each
coordinate support. The internal proof needs the distinct, metric-dependent
conditions

\[
z_S^T(G_r(P))_{SS}^{-1}z_S\le1\qquad(|S|\le2)
\tag{4}
\]

and then shows that one such polar point violates the resolvent ellipsoid at
scale \(v\asymp r\). That resolvent step controls all exact-mean
distributions by convex duality; it has no counterpart in the k-support
norm's convex-hull calculation. Thus the source supplies a standard
geometric language and a caution: (2) is not a new convex relaxation of
coordinate sparsity.

## Rotation and communication lower bounds

Ananda Theertha Suresh, Felix X. Yu, Sanjiv Kumar, and H. Brendan McMahan,
[*Distributed Mean Estimation with Limited Communication*](https://proceedings.mlr.press/v70/suresh17a/suresh17a.pdf),
ICML 2017, pages 3329--3337. I read its communication model, Theorems
1, 3, and 5 with the associated rotation and lower-bound arguments.

This source proves that a structured random Hadamard-sign rotation can
improve the Euclidean mean-square error of stochastic quantization
(Theorem 3), and it proves a minimax bit-versus-MSE lower bound for its
distributed mean-estimation protocol class (Theorems 1 and 5). Its proof
explicitly uses a separate statistical-estimation lower bound and a
communication-cost reduction. It is useful counterweight to any claim that
basis choice is an unstudied issue: rotations and their effect on coordinate
compression are established.

Its model is still not (1). Each client communicates a quantized vector to
estimate an empirical mean; the resource is an expected bit count across
clients. The theorem neither requires every reconstruction to have a
two-coordinate support nor imposes exact coefficient unbiasedness for each
individual query in an anisotropic metric. It also does not fix the
two-eigenvalue family \(P+r^2(I-P)\), let the distribution vary with one
query, and take a supremum over every query after that optimization.
Therefore its minimax lower bound neither proves nor contradicts (2).

## What the comparison establishes

| Item | Supported conclusion | Scope limit |
|---|---|---|
| Hard sparse exact-mean laws | Established directly by Barnes et al. for a fixed vector and separable/permutation-invariant losses. | Does not handle a rotated Gram's cross-coordinate covariance. |
| Sparse atomic convex geometry | Established by Argyriou--Foygel--Srebro. | It describes a Euclidean convex hull, not a query-adaptive covariance infimum. |
| Basis changes under communication constraints | Established by Suresh--Yu--Kumar--McMahan. | Its bit-constrained multi-client model is not the hard two-support coefficient model. |
| Uniform order-\(r\) barrier over every real rank-two \(P\) in \(\mathbb R^4\) | No checked source states it or makes it immediate. | Three sources are not an exhaustive literature search. |

The source collision is therefore partial, not absent. The elementary
unbiased sparse-vector problem, support conditioning, Euclidean atomic body,
and the relevance of rotations are known. The precise remaining step is the
uniform finite-dimensional assertion that the metric-dependent atomic polar
always contains a point with a resolvent excess at scale \(r\), despite an
arbitrary real coordinate orientation.

## Three separate verdicts

**Correctness.** The stated lower bound is supported internally by the
finite two-by-two polar proof and its graph-chart transfer. This source
review did not re-prove every displayed algebraic identity, and no external
paper is being used as a correctness substitute. The externally checked
sources are consistent with the theorem's model and reveal no contradiction.

**Originality.** Unresolved. The closest source, Barnes et al., already
studies unbiased almost-sure \(m\)-sparse vectors with exact means and exact
pointwise optimization. The claimed new step must therefore be stated
narrowly, if it survives broader checking: a real, basis-uniform,
metric-coupled \(\Omega(r)\) worst-query lower bound for the
rank-two-on-four-coordinate family. The bounded three-source reading does
not verify that this formulation is new, routine, or previously implicit in
a general theorem.

**Significance.** Conditional but substantive within the coefficient model.
Equation (2) says that changing the real coordinate basis cannot improve the
small eigenvalue's exponent below linear order, even when a sampler adapts
to the query and uses arbitrary nonlinear output weights. It separates a
genuine basis-uniform impossibility boundary from the coordinatewise
formulas already solved by unbiased sparsification. Under Cassette's
authority, that mathematical fact only concerns the one-step execution-risk
field after a plan declares \(R^TR=G_r(P)\) and implements \(RY\). It does
not settle resident-description bytes, sampler metadata, physical page
grouping, encoded fresh traffic, rounding bias, or sequential risk
composition. MATHS.md Sections 5--8 require those fields separately.

## Search boundary

I searched and read the three sources above under the terms unbiased
sparsification, hard sparse unbiased vector compression, k-support atomic
norms, randomized basis rotation, and communication-constrained mean
estimation. I did not complete a systematic search of approximation-width
monographs, all information-based-complexity work on randomized ellipsoid
approximation, or every compressor lower-bound family. This note makes no
publication, priority, patent, or product-novelty claim.
