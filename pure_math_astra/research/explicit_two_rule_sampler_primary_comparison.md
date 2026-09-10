# Bounded primary-source comparison: explicit sum-preserving two-sparse sampler

Scope: this record compares only the two rules in
`../notes/explicit_sum_preserving_two_sparse_sampler.md` and their real
review in `../notes/sum_preserving_two_sparse_real_sampler_review.md`.
It does not make an originality finding, assess Cassette significance, or
claim that this bounded search is exhaustive.

## Candidate being tested

For every \(x\in\mathbb R^4\), the candidate selects between a uniform
two-coordinate rule and a positive--negative transport rule.  It returns a
random \(Y\) satisfying

\[
 \mathbb EY=x,\qquad \|Y\|_0\le2,\qquad
 \mathbf1^TY=\mathbf1^Tx\quad\text{almost surely},
\]

with Euclidean variance at most \(5\|x\|_2^2/3\).  The material constraint
is the *signed* coordinate sum, not merely preservation of
\(\|x\|_1\).

## Primary sources read

| Source and URL | Exact portions read | Established result | Comparison with the candidate |
|---|---|---|---|
| J. Weare and R. J. Webber, [*Randomly sparsified Richardson iteration: A dimension-independent sparse linear solver*](https://onlinelibrary.wiley.com/doi/10.1002/cpa.70012), *Communications on Pure and Applied Mathematics* 79 (2026), 89--122. | Section 5.1, Algorithms 5.1--5.2 and their stated invariant; Section 5.2, Proposition 5.2 and proof through its selection-probability optimization. | The pivotal rule has hard support cap (m), exact mean, and exact preservation of the input \(\ell_1\)-norm.  Proposition 5.2 proves that it minimizes Euclidean mean-square error among all unbiased hard-(m)-sparse outputs with no further invariant.  The proof reduces the problem to inclusion probabilities and solves a convex program. | This is the closest direct collision.  If all coordinates of \(x\) are nonnegative or all are nonpositive, the signed sum equals plus or minus its \(\ell_1\)-mass, so pivotal sparsification already supplies a stronger sum-preserving hard-two rule.  For mixed signs, its output rescales retained entries by positive inclusion factors and preserves \(\|x\|_1\), while its signed coordinate sum generally changes.  Its optimality theorem therefore does not imply either candidate rule or the (5/3) bound under the signed-sum constraint. |
| L. Barnes, S. Cameron, T. Chow, E. Cohen, K. Frankston, B. Howard, F. Kochman, D. Scheinerman, and J. VanderKam, [*Efficient Unbiased Sparsification*](https://arxiv.org/html/2402.14925), arXiv:2402.14925v2 (2024). | Introduction, Sections I-A and I-B, Lemma 1 and its Appendix A-A proof, Theorem 1 and its stated scope, plus Section III's contrast with additively separable divergences. | For a positive vector, the paper characterizes Euclidean-efficient hard-(m) unbiased sparsifications among nonnegative outputs.  Its preservative outputs sample specified marginals, place equal mass on light selected coordinates, and preserve the coordinate sum.  Facet concentration is exactly conditional Jensen. | This independently confirms that fixed-size specified-marginal sampling, conditional Jensen, and sum preservation on the nonnegative simplex are established.  The theorem is restricted to a common orthant; its sign-flip observation preserves absolute mass, not the original signed sum across mixed signs.  It does not produce the candidate's pairwise affine rule, positive--negative transport law, or all-real (5/3) estimate. |
| J.-C. Deville and Y. Tillé, [*Efficient balanced sampling: The cube method*](https://doc.rero.ch/record/296198/files/914893.pdf), *Biometrika* 91 (2004), 893--912. | Summary and opening definition of balanced sampling in the author-hosted primary PDF. | Balanced sampling uses a fixed-size sampling design whose Horvitz--Thompson estimator reproduces declared auxiliary totals, with equal or unequal inclusion probabilities. | This is the standard calibration/dependent-rounding family closest to the word “sum preserving.”  It samples a subset and calibrates an estimator.  It does not state the candidate's random sparse replacement-vector problem, its coordinate amplitudes, or its worst-case Euclidean coefficient. |

## What is routine, and what is not supplied by these sources

**Verified standard ingredients.**  Conditional Jensen after a support is
chosen; importance sampling from positive and negative masses; prescribed
inclusion marginals; and fixed-cardinality dependent rounding are all
standard methods.  The two candidate laws are elementary instances of those
methods.  The equicorrelation step

\[
 e\perp\mathbf1\quad\Longrightarrow\quad
 e^T(\mathbf1\mathbf1^T+\eta I)e=\eta\|e\|_2^2
\]

is direct algebra.  Blockwise application is therefore a routine corollary
once the all-real signed-sum sampler has been proved.

**Verified non-implication.**  The two closest optimality theorems optimize
over all unbiased sparse vectors, or over nonnegative sparse vectors.  They
do not retain the affine constraint
\(\mathbf1^TY=\mathbf1^Tx\) when \(x\) has both signs.  The signed-mass
transport rule supplies that missing constraint by choosing one positive and
one negative coordinate; the uniform-pair rule handles the complementary
large-sum regime.  This comparison establishes a difference of hypotheses,
not a claim that the short four-coordinate construction is nonroutine.

**Reasoned assessment.**  The construction should be treated as a useful
explicit specialization, not as a candidate originality result.  Its
nontrivial-looking constant comes from a two-case comparison of elementary
variance formulas.  The finite-word and equicorrelation consequences remove
a previously nonconstructive catalog, but they are direct consequences of
the specialized sampler rather than a new use of pivotal sampling or survey
calibration.

## Search limit

The pass read the theorem and proof portions stated for the first two
sources.  The cube-method source was used only to locate the established
balanced-sampling model; no theorem from it is invoked.  Searches also
covered the terms “sum-preserving unbiased sparsification,” “dependent
rounding,” “survey calibration,” and “randomized vector sparsification.”
No conclusion about priority follows from this bounded comparison.

Root rechecked the Barnes et al. HTML introduction, its algorithm and sign-flip qualification, and the nonnegative-output restriction in Section II. The comparison now explicitly restricts signed-sum preservation to inputs whose coordinates all have the same sign; an arbitrary fixed orthant may contain mixed signs. The Wiley page did not load through the root web request; its reported sections remain the delegated source reading recorded above.
