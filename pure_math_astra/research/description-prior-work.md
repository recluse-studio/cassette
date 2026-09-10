# Prior-work challenge: low-rank descriptions with sampled residual access

**Scope.** This is a bounded primary-source challenge to the current
description problem, not a novelty conclusion. The object under investigation
is a fixed matrix \(A\), a resident rank-\(k\) matrix \(B\), and the iid
unbiased one-column correction

\[
B x+\frac{(A-B)_j x_j}{\pi_j},\qquad j\sim\pi.
\]

Its worst-query one-sample variance is

\[
\nu(A-B)=\min_{\pi\in\Delta_q}\lambda_{\max}\!\left(
\operatorname{diag}\!\left(\frac{\|(A-B)_j\|^2}{\pi_j}\right)
-(A-B)^*(A-B)\right).
\tag{P1}
\]

The papers below were read at their linked primary versions. They establish
nearby methods and prevent an overbroad claim; none is evidence that (P1) is
new.

## Directly relevant sampled matrix products

**Drineas--Kannan--Mahoney (2006), _Fast Monte Carlo Algorithms for Matrices
I: Approximating Matrix Multiplication_.**
[Author-hosted SIAM paper](https://www.cs.yale.edu/homes/mmahoney/pubs/matrix1_SICOMP.pdf).

Read: abstract, computational model, and the sampled-inner-index construction.
The algorithm samples an inner index independently, rescales the corresponding
outer product, and analyzes approximate products through Frobenius-norm error
and related probability bounds. This is the closest source for the iid,
importance-rescaled coordinate mechanism. It does not retain an arbitrary
rank-\(k\) deterministic matrix \(B\) while sampling \(A-B\), does not optimize
the residual sampling probabilities jointly with \(B\), and does not minimize
the maximum quadratic-form variance over all query vectors. Its matrix-product
setting also has a second input factor, whereas (P1) treats the query as
adversarial after the sampling law is fixed.

**Frieze--Kannan--Vempala (1998 preprint; JACM version 2004), _Fast
Monte-Carlo Algorithms for Finding Low-Rank Approximations_.**
[Primary preprint PDF](https://www.cs.princeton.edu/courses/archive/spring04/cos598B/bib/FriezeKV-lowrank.pdf);
[JACM DOI](https://doi.org/10.1145/1039488.1039494).

Read: abstract and main problem statement. It uses random access/sampling to
construct a rank-\(k\) approximation with a Frobenius-norm guarantee relative
to the best rank-\(k\) approximation. It supplies the standard low-rank
approximation side of the present construction, but it has no resident-plus-
unbiased-residual representation and no covariance-eigenvalue objective.

## Low-rank control variates

**Meyer--Musco--Musco--Woodruff (2021), _Hutch++: Optimal Stochastic Trace
Estimation_.**
[Primary paper / full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC8553228/);
[author PDF](https://www.chrismusco.com/hutchplusplus.pdf).

Read: abstract, Algorithm 1, Theorem 1, and the explanation of the residual
variance reduction. Hutch++ forms a low-rank range \(Q\), evaluates
\(\operatorname{tr}(Q^*AQ)\) exactly, and applies a stochastic trace estimator
to \((I-QQ^*)A(I-QQ^*)\). It proves a query-complexity improvement for
estimating the scalar trace of a PSD matrix from matrix-vector-product access.
This is the closest structural precedent for “deterministic low rank plus
random residual.” It differs materially from (P1): its random probes are dense
sign vectors, its access oracle is matrix-vector multiplication, its target is a
scalar trace, and its guarantee is not the exact maximum variance of an
unbiased matrix-vector estimator under one fresh column access.

**Fairbanks--Doostan--Ketelsen--Iaccarino (2017), _A Low-rank Control
Variate for Multilevel Monte Carlo Simulation of High-dimensional Uncertain
Systems_.**
[Primary arXiv version](https://arxiv.org/abs/1611.02213);
[journal DOI](https://doi.org/10.1016/j.jcp.2017.03.060).

Read: abstract, introduction, control-variate construction, and sampling-cost
discussion. The paper builds an interpolative low-rank surrogate from
coarse/fine model samples and uses it as a multilevel control variate for a
quantity of interest. Its optimization is scalar MSE and cost across model
levels, with a pilot run and fitted control coefficient. It neither poses nor
solves the fixed-matrix, iid coordinate-access minimax problem (P1).

## Coordinate sampling with deterministic work

**Gupta--Sidford (2018), _Exploiting Numerical Sparsity for Efficient
Learning_.**
[NeurIPS primary PDF](https://proceedings.neurips.cc/paper_files/paper/2018/file/4a1590df1d5968d41b855005bb8b67bf-Paper.pdf).

Read: abstract, problem formulation, and the stated coordinate-sampling/SVRG
method. The paper uses exact treatment of selected coordinates together with
randomized coordinate estimates to reduce per-iteration work for regression and
top-eigenvector computation under numerical-sparsity assumptions. It is a
close precedent for deterministic-head plus sampled-tail estimators, but the
head is selected within vector/gradient estimators rather than being an
arbitrary resident rank-\(k\) matrix. Its bounds serve iterative optimization;
they do not solve (P1) or use \(\lambda_{\max}\) of the exact estimator
covariance as the criterion.

## What the comparison supports, and what it blocks

Verified overlap: iid importance-rescaled sampling, low-rank approximation,
and low-rank-plus-random-residual variance reduction each have established
primary precedents. Therefore “use a low-rank control variate and importance
sample the residual” is not an original claim.

Verified distinction: the sources read do not state the joint fixed-matrix
optimization (P1), under a single fresh column per query, with an operator
covariance objective uniform in the query vector. This is only a statement
about these sources and their stated results, not evidence of novelty.

The closest nontrivial obstruction is consequential. The current weighted-SVD
result exactly minimizes an energy envelope, so it is a routine combination of
the envelope identity and weighted Eckart--Young--Mirsky. To clear the prior-
work boundary, a candidate needs a result about (P1) itself: for example, an
exact solvable characterization of the joint rank-\(k\) optimum, a strictly
better worst-query guarantee with a proved sharp constant, or an impossibility
theorem that changes the feasible description/access tradeoff. A theorem only
for freely chosen residual Gram matrices is insufficient unless it also
preserves the affine constraint \(A-B\) with \(\operatorname{rank}B\leq k\).

Search terms used included: “optimal sampling matrix multiplication variance,”
“low-rank control variate matrix,” “randomized matrix-vector multiplication
importance sampling,” “variance reduction randomized matrix multiplication,”
and “coordinate sampling low-rank approximation.” The search was bounded to
the sources above and cannot establish absence of a closer result.
