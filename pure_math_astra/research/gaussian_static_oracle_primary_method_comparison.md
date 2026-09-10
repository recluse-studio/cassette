# Primary-method comparison for the Gaussian static-oracle reduction

Scope: two primary average-case IBC sources were read to test the method in
`../notes/gaussian_static_oracle_first_chaos_reduction.md` and
`../notes/gaussian_static_nonlinear_oracle_minimax_gap.md`.  This is a
method comparison, not an originality finding.

## Sources read

1. G. W. Wasilkowski, [*Optimal algorithms for linear problems with
   Gaussian measures*](https://doi.org/10.1216/RMJ-1986-16-4-727), *Rocky
   Mountain Journal of Mathematics* 16 (1986), 727--749.  I read the
   available full-text rendering of its conditional-measure theorem and
   Theorems 4.1--4.4 at
   [this copy](https://paperzz.com/doc/7208297/optimal-algorithms-for-linear-problems-with).

2. J. F. Traub, G. W. Wasilkowski, and H. Woźniakowski, [*Average case
   optimality for linear problems*](https://iiif.library.cmu.edu/file/Traub_box00029_fld00003_bdl0001_doc0001/Traub_box00029_fld00003_bdl0001_doc0001.pdf),
   *Theoretical Computer Science* 29 (1984), 1--25.  I read its model,
   Theorem 3.7, and Theorem 4.2 in the linked primary scan.

The first source is the closer Gaussian theorem.  The second is the closer
finite-dimensional fixed-linear-information predecessor; its radially
invariant model includes isotropic Gaussian choices but is not restricted to
them.

## What is established in those sources

For a fixed nonadaptive linear information operator, Wasilkowski proves that
the conditional law under a Gaussian input is Gaussian, with an explicitly
identified conditional mean and covariance (Theorem 3.1).  Theorem 4.1 then
identifies an optimal algorithm as a translated spline: the conditional mean
plus a fixed Bayes-optimal translation.  For convex symmetric loss, Theorem
4.3 makes the unshifted spline optimal.  Theorem 4.2 replaces an adaptive
linear information operator by a nonadaptive one of the same cardinality
with no larger average radius.

Traub--Wasilkowski--Woźniakowski prove the analogous finite-dimensional
statement for their orthogonally invariant average-case model.  Their
Theorem 3.7 makes the linear spline the unique optimal average-error
algorithm for a fixed linear information operator, among measurable
algorithms with defined average error.  Their Theorem 4.2 selects optimal
linear information from the leading eigendirections of the relevant
operator.

These are direct precedents for the standard part of the new argument:
under squared loss, a Gaussian linear target observed through fixed linear
information has a linear Bayes reconstruction.  Conditional expectation,
orthogonal projection in Gaussian \(L^2\), and removal of higher chaos from
an unconstrained Bayes estimator are established machinery, not a new
method here.

## The exact-mean distinction

The new static oracle does not minimize Bayes error separately on each
support.  It must satisfy, for every real source \(A\) and every query
\(x\),

\[
 \sum_S p_S F_S(A_{:S},x)=Ax. \tag{1}
\]

For the Gaussian model with row covariance \(G/p\), the branchwise Bayes
estimator from the standard conditional-mean theorem is

\[
 \mathbb E[Ax\mid A_{:S}]
 =A_{:S}G_{SS}^{-1}G_{S,:}x. \tag{2}
\]

Writing

\[
 M=\sum_Sp_SE_SG_{SS}^{-1}E_S^T,
\]

the mixture of these individually Bayes-optimal branches equals \(AMGx\),
not \(Ax\).  Equality for every \(A,x\) would require \(MG=I\).  If
supports have size at most \(s<q\), this is impossible because

\[
 \operatorname{tr}(GM)=\sum_Sp_S|S|\leq s<q
 =\operatorname{tr}I. \tag{3}
\]

Thus the exact all-source mean constraint rules out the usual conditional
mean as the decoder.  The new first-chaos step instead preserves (1) and
produces coupled coefficients \(c_S(x)\) satisfying

\[
 \sum_Sp_SE_Sc_S(x)=x. \tag{4}
\]

Minimizing their joint first-chaos risk yields \(x^T(M^{-1}-G)x\).  This
is not the branchwise conditional-mean optimization proved in either source.

## Random supports and normalized minimax risk

Both primary sources treat a deterministic information operator, with
adaptivity meaning that later linear observations may depend on earlier
observed values.  A fixed random support law can be conditioned on its
support, so their Bayes argument applies branch by branch.  It does not
enforce the cross-branch identity (1).  The cited theorems therefore do not
give the principal-inverse lower program for a randomized support mixture
under exactness.

Likewise, neither source studies

\[
 \sup_{A\ne0}\sup_{\|x\|=1}
 \frac{\mathbb E_S\|F_S(A_{:S},x)-Ax\|^2}
 {\|AG^{-1/2}\|_{\rm op}^2}, \tag{5}
\]

nor a comparison against a catalog selected after the query is supplied.
The Gaussian draw and operator-norm expectation in the new note convert its
Bayes lower bound into this normalized minimax statement.  That conversion,
and the query-selected upper construction, are additional steps rather than
consequences of the cited average-case optimality theorems.

This bounded check does not establish that no paper treats the exact
all-source-unbiased randomized-support problem, or that the assembled
minimax separation is original.  It establishes only that the two closest
primary theorems actually read solve the unconstrained Bayes reconstruction
problem, while the new lower bound depends on the extra coupling (1).
