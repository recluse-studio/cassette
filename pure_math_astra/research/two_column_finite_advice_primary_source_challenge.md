# Bounded primary-source challenge: two-column finite-advice lower

Scope: this note challenges the method in
`../notes/two_column_unbiased_finite_advice_lower.md` and
`../notes/stiefel_orthogonality_operator_atomic_matching.md`.  It is not an
exhaustive literature review and does not make an originality finding.

## Candidate theorem being tested

The candidate is a pointwise, worst-source result on the real Stiefel orbit
\(\mathcal V_{p,2}\).  An encoder sends one of at most \(N\) labels.  Each
label fixes a probability of reading exactly one column and may select a
fixed right \(O(2)\) basis.  Arbitrary Borel branch decoders must be
exactly unbiased for every source and every query.  The claim lower-bounds
uniform squared error by a power of \(N\), despite arbitrary nonlinear
branch functions.

The distinctive conditions are all material: one observed column, a label
chosen from the source, source-independent sampling within a label, exact
mean for every orbit point, and worst-case rather than distributional risk.

## Primary sources read

| Source and URL | Exact material read | What it establishes here | Why it is not an immediate corollary |
|---|---|---|---|
| P. Gács and J. Körner, *Common Information Is Far Less Than Mutual Information*, *Problems of Control and Information Theory* 2(2), 1973, 149–162, [author-hosted primary PDF](https://cs-web.bu.edu/faculty/gacs/papers/commoninf.pdf) | Opening formulation and the initial Section 2 definitions exposed by the primary PDF rendering. | It is the closest named notion of a deterministic common value \(f(X)=g(Y)\): common information is tied to deterministic interdependence rather than ordinary mutual information. | Its model is finite-alphabet, memoryless source coding and asks for a common variable on the full joint law.  The Stiefel argument only has equality on a label cell, may have countably many shared atoms, and needs a quantitative bound on the measure of every cell.  The 1973 result supplies neither its compact-operator atom lemma nor its \(N\)-label exponent. |
| A. K. Louis, M. Riplinger, M. Spiess, and E. Spodarev, *Inversion algorithms for the spherical Radon and cosine transform*, *Inverse Problems* 27 (2011), 035015, [full text](https://www.researchgate.net/publication/228931482_Inversion_algorithms_for_the_spherical_Radon_and_cosine_transform) and [DOI](https://doi.org/10.1088/0266-5611/27/3/035015) | Section 2, especially the self-adjoint identity in its equation (4), its spherical-harmonic discussion, and the displayed Sobolev smoothing estimate attributed there to Strichartz. | The equatorial averaging operator used in the Stiefel proof is the spherical Radon/Funk operator.  Its self-adjointness and smoothing are established analysis.  Together with compact Sobolev embedding, this gives an alternate standard route to compactness of \(T\) (odd functions are killed by equatorial symmetry). | This source studies inversion and regularization.  It does not state the event-local conclusion that \(f(a)=g(b)\) on a measurable subset can occur only at marginal atoms, nor the finite-rank/nonatomic partition argument or a finite-advice lower bound. |
| H. Wang, S. Sievert, Z. Charles, S. Liu, S. Wright, and D. Papailiopoulos, *ATOMO: Communication-Efficient Learning via Atomic Sparsification*, NeurIPS 2018, [primary PDF](https://proceedings.neurips.cc/paper_files/paper/2018/file/33b3214d792caf311e1f00fd22b392c5-Paper.pdf) | Pages 2–4: atomic estimator (2), Lemma 1, expected sparsity constraint (3), and Theorem 4 with its proof setup; pages 4–5 on coordinate versus SVD atoms and their stated communication accounting. | Unbiased atomic sparsification for a fixed input and a fixed atomic decomposition is established.  The paper explicitly treats the variance–sparsity optimization and compares coordinate and SVD representations. | ATOMO selects independent Bernoulli atoms for a known gradient under an *expected* sparsity constraint.  It has no hidden source on a Stiefel orbit, no one-observed-column branch information restriction, no finite source-selected label, and no pointwise exactness across all sources.  Its Theorem 4 therefore cannot produce the candidate lower bound. |

Two additional primary families were checked only at abstract or bibliographic level, so they are not used as theorem support:

* A. Wyner and J. Ziv, *The Rate-Distortion Function for Source Coding with Side Information at the Decoder*, *IEEE Transactions on Information Theory* 22(1), 1976, 1–10, [DOI record](https://doi.org/10.1109/TIT.1976.1055508).  Its classical i.i.d. average-distortion, coded-message setting differs from a uniform exact-unbiased one-column oracle.  Full primary text was not accessible in this bounded pass.
* M. Safaryan, E. Shulgin, and P. Richtárik, *Uncertainty Principle for Communication Compression in Distributed and Federated Learning and the Search for an Optimal Compressor*, *Information and Inference* (2021), [arXiv primary record](https://arxiv.org/abs/2002.08958).  The abstract describes variance–communication lower bounds for randomized compressors.  This pass did not establish a theorem whose hypotheses encode the candidate's observation restriction or finite advice, so it is not used as a collision.

## What follows from the sources

**Verified standard ingredient.**  The compactness step for equatorial
averaging is not a new transform fact.  The spherical-Radon literature gives
self-adjointness and positive Sobolev smoothing; alternatively the current
note proves compactness directly from the kernel of \(T^2\).  Either route
supports the analytic input to the atomic-matching lemma.

**Direct statement comparison.**  None of the primary theorem statements read has
all five candidate conditions at once.  In particular, Gács–Körner's global
common-variable setting cannot replace the event-local atomic argument, and
ATOMO's fixed-input variance minimization cannot replace the all-source
exactness constraint.

**Reasoned inference.**  The finite-advice lower is an assembly of standard
pieces—conditional expectation/Jensen, a compact Funk operator, atomic
common-value reasoning, spherical cap volume, and a label union bound.  The
specific assembly may still be routine in an unlocated source.  This bounded
search found no immediate-corollary route, which is not evidence that none
exists.

## Nearest mathematical discriminator

A direct collision would need a theorem with all of the following in one
model: a continuous dependent pair \((a,b)\) with orthogonality law;
arbitrary measurable functions of only one side; exact equality only on
encoder-selected measurable cells; a finite number of cells; and a
quantitative cell-measure or worst-case squared-error bound.  The named
common-information theorem loses the cell-local and quantitative pieces;
the spherical-Radon source loses the decoder and finite-label pieces; the
unbiased-compression source loses the dependent-observation and
source-uniform pieces.

## Source-access limit

The Gács–Körner PDF, the spherical-Radon full text, and the ATOMO full paper
were read at the portions stated above.  The Wyner–Ziv and Safaryan entries
were used only to set a boundary because full theorem text was not obtained
in this pass.  No conclusion about priority, novelty, or Cassette
significance follows from this source check.


## Root follow-up: bibliography and the accessible compression theorem

The Gács–Körner page range above was corrected to 149–162 using
[Gács's own publication list](https://cs-web.bu.edu/faculty/gacs/papers/publ.pdf),
entry 2. The search rendering of the scanned paper reports 119–162;
that rendering was not retained as the bibliographic authority.

The [Safaryan–Shulgin–Richtárik v3 HTML](https://arxiv.org/html/2002.08958v3)
was subsequently accessible. Root read Definitions 1–2, Theorems 1–2,
Lemma 1, the opening of Appendix A.1, and Appendix A.2's stated
rate-distortion derivation. Their unbiased bound is
omega/(omega+1) times 4^(b/d) at least one, with b encoding the entire
compressed output. Appendix A.1 begins with at most 2^b output vectors.
Here the observed column is continuous and uncharged by the advice count;
even one label permits infinitely many decoded outputs. Direct substitution
of advice bits for their output bits therefore violates that premise.
This comparison does not exclude another reduction or establish originality.

The [direct conditional-cap theorem](../notes/finite_advice_unbiased_static_conditional_cap_lower.md)
now supersedes the operator-based decoder bounds. Its short proof combines
exact mean, Jensen, and a conditional cap bound. The unnecessary transform
machinery cannot count as an original step in that theorem. A broader
primary-source comparison remains open.
