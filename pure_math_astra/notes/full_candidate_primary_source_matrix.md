# Primary-source novelty challenge: dependence-support transform rate

Status: bounded adversarial comparison, not a novelty finding.  It reads the
candidate in `dependence_support_transform_rate.md`,
`anisotropic_transform_box_cover.md`, `procedural_transform_decoder.md`, and
`q4_full_spectrum_support.md`.  The relevant claim is narrow: a hard-
`s`, unbiased, worst-query *spectral covariance* loss has a local normal
form whose linear part is controlled by the smallest feasible cross-pair
dependence support.  That local normal form then gives a transform-library
index exponent.  This note distinguishes that claim from the ordinary
high-rate covering calculation.

## Result of the challenge

No source read here is a complete collision.  Nor does the search establish
absence of one.  The candidate has **not passed originality**.

Three pieces are standard or become standard once the loss-specific work is
done:

1. A smooth compact homogeneous manifold has local coordinates and a smooth
   invariant density.  Covering a sublevel body of volume
   `Theta(epsilon^kappa)` takes reciprocal-order many codewords.  A
   rational-chart grid is a standard way to make such a cover procedural.
2. Fixed-size inclusion and pair-moment feasibility live in a cardinality
   constrained Boolean quadratic polytope.  The covariance-support parameter
   is a problem on that known object.
3. A finite semidefinite perspective lift puts the fixed-basis optimization
   inside parametric conic optimization.  General directional and second
   order sensitivity results are a serious route to its first-order value
   function.

The only potential mathematical increment left after those reductions is the
following conjunction:

* arbitrary subset-dependent real or complex weights reduce, uniformly near
  an eigenbasis, to the exact-marginal fixed-size dependence set;
* the resulting spectral value has the two-sided, *uniform* local estimate
  
  `Phi_s(G(B))-t asymp ||B||^2 + min_{c in C} ||B circle c||`;
* the zero patterns of the exact-size dependence polytope turn this estimate
  into the exponent `(beta(N+k))/2`, including the reciprocal-spectrum
  phase in the four-coordinate example.

The primary results below do not prove that conjunction.  Conversely, the
candidate notes have not yet supplied a source-independent proof that none
of them, or a nearby result on weighted/homogeneous covering, already
implies it.  This is therefore a research discriminator, not a novelty pass.

## Source comparison matrix

| Primary source read | Exact result or pages read | Assumptions and loss | What it settles here | Missing bridge to the candidate |
|---|---|---|---|---|
| W. Dai, Y. Liu, B. Rider, *Quantization Bounds on Grassmann Manifolds and Applications to MIMO Communications*, IEEE Trans. IT 54 (2008), 1108–1123, [arXiv:cs/0603039](https://arxiv.org/abs/cs/0603039) | Intro and Sections II–IV; in particular Theorem 1's small chordal-ball volume and Corollary 3 / Theorem 2's packing and rate-distortion calculation. The preprint states the manifold dimension `beta p(n-p)`, volume leading term `c delta^{beta p(n-p)}`, and a reciprocal-volume code calculation. | Uniform source on a Grassmann manifold; squared chordal distance; expected distortion and metric-ball packings. | The ordinary conversion “local volume exponent -> high-rate cardinality exponent” is old. It cannot be presented as the advance. | Candidate orbit is a general flag orbit, and its acceptable set is not an invariant chordal ball. More importantly, its loss is optimal spectral covariance of a hard-cardinality unbiased estimator. Dai–Liu–Rider has no sampling law, inclusion covariance, or `k`-dependent thin directions. |
| B. Mondal, S. Dutta, R. W. Heath Jr., *Quantization on the Grassmann Manifold*, IEEE Trans. Signal Processing 55 (2007), 4208–4216, [DOI](https://doi.org/10.1109/TSP.2007.896112) | Full text, pp. 1–13 of the accessible manuscript: definition of `N`-point Grassmann quantizer and chordal-power distortion; Lemmas 1–2 reduce a Voronoi region to an equal-volume ball; Section III gives the large-rate distortion framework. | Complex Grassmannian; power `d^r` of chordal distance; average distortion. It explicitly frames the setting as high-resolution quantization. | Reinforces that local-volume/rate arguments and manifold quantizer coordinates are familiar. Its equal-volume ball method is a close methodological analogue only. | No nonsmooth spectral maximum, no exact unbiasedness, no fixed `s` support, no mixture over sampling laws. A locally quadratic perceptual distortion mentioned in its bibliography is not the candidate's mixed quadratic-plus-linear local loss. |
| W. Dai, B. Rider, Y. Liu, *Unequal Dimensional Small Balls and Quantization on Grassmann Manifolds*, IEEE Trans. IT 54 (2008), 4231–4242, [arXiv:0705.2278](https://arxiv.org/abs/0705.2278) | Abstract and Sections I/IV of the primary preprint: small balls with centers in a different Grassmannian and asymptotically identical high-rate bounds. | Chordal metric, uniform invariant geometry, plane matching. | Rules out describing the candidate merely as “a new unequal-dimensional Grassmann codebook exponent.” That topic is already developed. | Different dimensions of subspaces do not create the candidate's anisotropic directions. The paper contains no covariance design, hard sample cap, or dependence-support combinatorics. |
| S. Barnes et al., *Efficient Unbiased Sparsification*, arXiv:2402.14925v2, [HTML](https://arxiv.org/html/2402.14925v2) | Definition of unbiased `m`-sparsification and concentrated distributions; Lemma 2; Sections II–IV, especially the generalization/open-question discussion. | Vector target; at most `m` nonzeros; convex divergence, with closed-form conclusions requiring additive separability and permutation invariance. | It is close in the use of unbiased hard-support random vectors, and shows this is not an unstudied language. It also provides a useful contrast: sparse unbiased laws can require an optimization over supports and conditional values. | Its objective is an expected scalar divergence. The paper does not optimize `lambda_max(E[D_b^* G D_b]-G)`, allows neither Gram-coupled pair terms nor the orbit perturbation, and its structural results rely on separability/permutation invariance absent here. It is not a collision. |
| E. Bondesson, *On Sampling with Prescribed Second-Order Inclusion Probabilities*, Biometrics 68 (2012), 1055–1063, [DOI](https://doi.org/10.1111/j.1467-9469.2012.00808.x) | Abstract and bibliographic record: construction of fixed-size sampling designs with prescribed second-order inclusion probabilities. | Fixed-size survey samples; first- and second-order inclusion probabilities. | The pair-moment component of `C` belongs to established sampling-design territory. It cautions against claiming pairwise-law feasibility itself. | It does not minimize covariance support, couple those moments to a matrix spectral loss, or derive a transform-cover exponent. |
| J.-F. Bonnans and R. Cominetti, *Perturbed Optimization in Banach Spaces I*, SIAM J. Control Optim. 34 (1996), 1151–1171, [DOI](https://doi.org/10.1137/S0363012994267273); J.-F. Bonnans, R. Cominetti, A. Shapiro, *Sensitivity Analysis of Optimization Problems Under Second Order Regular Constraints*, Math. Oper. Res. 23 (1998), 806–831, [DOI](https://doi.org/10.1287/moor.23.4.806); J.-F. Bonnans, R. Cominetti, A. Shapiro, *Second Order Optimality Conditions Based on Parabolic Second Order Tangent Sets*, SIAM J. Optim. 9 (1999), 466–492, [DOI](https://doi.org/10.1137/S1052623496306760) | Abstracts and accessible copies: the 1996 paper gives first/second-order value sensitivity under a weak directional CQ and a no-gap condition; the 1998 paper gives Lipschitz/Hölder expansions under directional CQ and second-order sufficient conditions and says semidefinite optimization satisfies its second-order regularity condition; the 1999 paper supplies the parabolic-tangent/SO-regularity framework and again identifies SDP as a covered cone class. | Smooth parameter-dependent cone programs, subject to stated CQs, multiplier and second-order conditions. | A finite perspective SDP lift of the estimator law makes standard first directional sensitivity highly relevant. The candidate's first-order support functional is therefore not evidence of novelty by itself. | The candidate's base point has a whole face of HT sampling laws and a non-simple top eigenvalue. The source hypotheses do not automatically provide unique multipliers, strong regularity, or a quadratic-growth modulus. One must verify the specific tangent problem and prove the uniform quadratic branch; citing parametric SDP theory alone is insufficient. A direct derivation may yet make the whole normal form a routine application. |
| A. Shapiro and J.-F. Bonnans, *Sensitivity Analysis of Parametrized Programs under Cone Constraints*, SIAM J. Control Optim. 30 (1992), 1409–1422, [DOI](https://doi.org/10.1137/0330075) | Abstract: establishes local behavior and Lipschitz stability of epsilon-optimal solutions under cone constraints and SOSC, using second-order expansions. | Banach-space cone constraints and SOSC. | Same warning in a more direct form: a perturbation theorem can supply stability after its hypotheses are demonstrated. | Does not identify the exact-size moment polytope, calculate the derivative as a dependence-gauge, or yield the support-count exponent. |
| E. Faye and H. Trinh, *The Cardinality Constrained Boolean Quadric Polytope*, technical report, 2005, accessible full text through [ResearchGate](https://www.researchgate.net/publication/267950434_The_Cardinality_Constrained_Boolean_Quadric_Polytope) | Proposition 3.2 and Consequence 3.2: the equality-cardinality Boolean quadric polytope is a face of the ordinary Boolean quadric polytope, permitting lifted facet information. | Convex hull of `(x_i,x_i x_j)` with fixed cardinality. | Exact-size first/second inclusion arrays are a familiar polyhedral object. The `C` set is an affine image/slice of it. | Facet and polytope structure do not calculate the candidate's optimal spectral covariance, its arbitrary-weight reduction, or the orbit normal form. But this source removes any claim that the pair-moment domain itself is new. |

## Explicit comparison with the candidate's proof steps

### A. The covering exponent is a conditional corollary

Assume equation (4) in `dependence_support_transform_rate.md`, and assume
the common-law weighted box construction.  Then the box has wide radii
`sqrt(epsilon)` in `beta(N-k)` real coordinates and thin radii `epsilon` in
`beta k` coordinates.  Its volume is

`epsilon^{beta(N-k)/2 + beta k} = epsilon^{beta(N+k)/2}`.

Maximal packing plus a finite atlas yields the reciprocal cardinality.
This is the same geometric conversion that underlies the Grassmann sources,
only for a nonisotropic body.  The deterministic grid and the Cayley
decoder make the upper bound constructive, but do not alter that conclusion.
They are not an originality basis.

### B. What parametric SDP can plausibly make routine

For each support `S`, introduce a probability `alpha_S`, a conditional
first moment `m_S`, and a conditional second moment `Z_S`, with

`[[alpha_S, m_S^*], [m_S, Z_S]] >= 0`.

After embedding each support in the full coordinate space, the constraints
`sum alpha_S=1`, `sum m_S=1`, and the spectral covariance epigraph are
finite affine/semidefinite constraints.  At a positive diagonal base point,
near-optimal sublevels bound the diagonals of `Z_S`; Cauchy/Schur then bound
the remaining lifted variables.  Thus the apparent perspective closure can
be controlled locally.  This is the concrete reason the Bonnans--Cominetti--
Shapiro theory is relevant rather than a keyword match.

At the diagonal point, Cauchy equality forces HT conditional weights and
the marginal vector `p_i=a_i/(a_i+t)`.  Linearizing the spectral epigraph
then gives the dependence term `B circle c`, subject to diagonal allocation
directions.  That calculation is specific and must be supplied.  Once it is
supplied, general directional value-function theory is a credible source of
the *existence* of a first-order term.  It still does not by itself prove:

* equality of the full arbitrary-weight tangent value with
  `min_c ||B circle c||` up to uniform constants;
* the quadratic lower bound in directions where a feasible `c` kills all
  first-order coordinates;
* persistence of the same constants over the required flag charts.

The source theorems require hypotheses such as a directional CQ and a
second-order sufficient/no-gap condition.  The multiplicity of HT laws and
of top-eigenvalue dual densities means those hypotheses cannot be assumed
from Slater alone.  A proof that verifies them and derives the stated gauge
could make the candidate a tailored application; a proof that shows their
failure but still proves the gauge would be stronger evidence of a distinct
result.  Neither outcome is presently documented.

### C. The four-coordinate reciprocal phase is supporting mathematics

The `q=4,s=2` calculation says `k=2` precisely if some pair of inclusion
marginals is complementary, and otherwise `k=5`.  With energy marginals,
that is `a_i a_j=t^2`.  This is a precise finite transport/covariance fact,
not a general transform-coding theorem.  It is useful because it exposes a
discrete phase in the proposed exponent.  The sources above neither state
this calculation nor make it surprising enough to support a broad claim by
itself.

## Significance boundary

Within the declared model, the theorem would give a real capability:
one globally shared fixed-size sampler and a procedural transform index
whose asymptotic exponent changes with the attainable dependence support.
The procedural note correctly avoids an `O(K)` stored-matrix table.

It does **not** establish a Cassette total-description frontier.  In
particular, `kappa log(1/epsilon)+O(1)` counts a transform index when the
resolution and shared decoder are declared.  It excludes the encoded-column
payload, sampler representation, decoder workspace and operations,
source-to-index selection, source approximation error, page granularity,
and finite-arithmetic execution.  Exact unbiasedness in the rational model
is toward the represented `R`, not automatically toward an unquantized
source.  These are separate fields under `MATHS.md`; no source comparison
changes that boundary.

Accordingly, the current candidate could become mathematically worthwhile
only if the loss-specific normal form survives a direct derivation and a
closer collision search in weighted/homogeneous quantization and SDP
eigenvalue sensitivity.  It is not yet a consequential resource theorem.

## Source-access limits

All entries above are primary papers or primary technical reports.  Dai et
al. and Barnes were read in author-hosted arXiv HTML/preprint form;
Mondal et al. and Faye--Trinh were read through accessible author-uploaded
full text; the Bonnans--Cominetti--Shapiro claims were checked against the
publisher abstracts and accessible copies/metadata.  Paywalled publisher
PDFs were not obtained where an accessible source did not expose the full
proof.  This review did not locate and read a primary theorem specifically
for high-rate covering under a mixed weighted gauge such as
`||x||^2+||x_L||`; it therefore makes no absence claim about that source
family.
