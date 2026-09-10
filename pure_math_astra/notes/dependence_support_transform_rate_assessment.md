# Adversarial assessment: dependence support and transform-library rate

Status: 5 September 2026.  This is a correctness, originality, and Cassette
significance assessment of `dependence_support_transform_rate.md`.  It does
not accept a paper claim, a byte frontier, or a production certificate.

## Verdict

The candidate has a sound-looking complete mathematical route in its stated
ideal encoded-column model.  I found no counterexample or unclosed inference
in the general local comparison, the Haar-volume exponent, or the common-law
library construction.  Its hardest reduction is now stronger than an
attainment-based argument because it uses an arbitrary `eta`-near minimizer.

That correctness conclusion is conditional on the already stated
fixed-basis rigidity inequality and the local near-equality estimates used in
Section 5.  Those estimates must remain proved lemmas, with their complex
version, rather than being imported as intuition.

Originality and consequential Cassette significance do not yet pass.  The
nearest exact combinatorial object is the fixed-marginal affine slice of the
fixed-cardinality Boolean quadratic polytope.  The bounded source pass does
not show that its support-minimization problem, or the resulting orbit rate,
is absent from that literature.  The theorem supplies an index exponent in a
declared exact encoded-column class; it does not supply a total-byte,
native-arithmetic, fresh-traffic, or sequential certificate.

## 1. Correctness review

### The arbitrary-weight lower bound survives the hard cases

Let `Delta=Phi_s(G(B))-t+eta`.  The nontrivial point is to start with an
arbitrary support-dependent complex coefficient law, whose supports may have
fewer than `s` coordinates, and arrive at a law in `P(p)`.

Section 5 does this correctly, subject to its quoted diagonal Cauchy and
near-equality lemmas.

1. The diagonal covariance inequality gives
   `theta_i >= d_i/(d_i+t+Delta)`.  Isospectrality and concavity of
   `x/(x+t)` give the required aggregate control.  Since the diagonal changes
   only by `O(||B||^2)`, this yields
   `theta_i=p_i+O(Delta+||B||^2)` and the stated Cauchy defect.
2. Padding a support to cardinality `s` changes the indicator law with
   probability at most `E(s-|supp b|)=O(Delta)`.  Thus it changes marginals
   only by the claimed amount.
3. If the padded marginals are `p+e`, then
   `z=p-rho e/||e||_infty` lies in the hypersimplex when
   `rho=1/2 min_i{p_i,1-p_i}`.  Mixing the padded law with a law of marginals
   `z` at weight `||e||_infty/(rho+||e||_infty)` gives *exactly* `p`.
   This calculation also covers all signs of `e`; no hidden positivity
   assumption is present.
4. Cauchy converts the magnitude defect into the `O(sqrt(Delta))` cross-moment
   defect, including for complex coefficients.  The PSD slack
   `(t+Delta)I-Q` has diagonal `O(Delta)`, so its off-diagonal entries, hence
   those of `Q`, are `O(Delta)`.  With
   `G_ij=B_ij+O(||B||^2)`, this gives (13).  The rigidity lower bound absorbs
   the residual `||B||^2`; then `eta` tends to zero.  No optimizer of
   `Phi_s` is assumed to exist.

This is the essential proof step.  It rules out an apparent escape in which
non-HT complex weights cancel a first-order Gram rotation without inducing a
nearby fixed-marginal pair design.

### The support gauge and volume argument are valid

The compact coordinate-support lemma is correct.  For each impossible zero
set `Z`, compactness makes
`min_c max_{i in Z}|c_i|` strictly positive.  Finitely many coordinate sets
give one uniform threshold.  This proves the lower comparison with feasible
support patterns; bounded representatives give the upper comparison.  The
argument needs neither polyhedrality nor a false positive lower bound for
individual nonzero correlations.

After that comparison, the sublevel set is a finite union of anisotropic
boxes.  A chosen feasible support of size `r` has `beta r` coordinates of
scale `epsilon` and the other `d-beta r` real coordinates of scale
`sqrt(epsilon)`.  The smallest feasible support size `k` therefore yields
`kappa=beta(N+k)/2`.  The finite set of diagonal points on the orbit and the
strict rigidity gap away from their neighborhoods complete the global Haar
volume conclusion.

For the library bound, the lower bound is the ordinary union-of-translates
measure bound.  The later deterministic box-cover note strengthens the upper
bound: one common HT law provides an anisotropic `sqrt(epsilon)` by
`epsilon` local box, and its BCH/packing argument gives a finite procedural
grid with `K=Theta(epsilon^-kappa)`.  This is a mathematical codebook
existence/construction result; it does not find a smallest codebook.

### Remaining correctness obligations

No defect was found, but the final proof should state these dependencies and
boundaries explicitly.

- Prove or cite in the same manuscript the complex version of the quoted
  Cauchy-defect and PSD-slack estimates.  Their use is valid, but the theorem
  depends on them.
- Define the norm on `B` and the invariant metric once.  In fixed dimension
  all norms are equivalent, but the chart, Lipschitz-net step, and constants
  should use one declared metric.
- Keep the target class exact: a source operator `R`, stored columns `RV e_i`,
  an exact transform decoder, and a query in a field where the indicated
  operations are exact.  The proof is not a statement about arbitrary
  floating-point arrays.
- The examples computing particular values of `k` are supporting results.
  The general theorem does not depend on an unverified closed formula for
  `k`; it defines `k` by the feasible-law polytope.

## 2. Originality review

The exact fixed-cardinality first- and second-moment object is already named
in polyhedral combinatorics.  If `x` is the incidence vector of an
exactly-`s` subset and `y_ij=x_i x_j`, then

```
conv{(x,y): x in {0,1}^q, sum x=s, y_ij=x_i x_j}
```

is the cardinality-constrained Boolean quadratic polytope.  Fixing
`E x=p`, projecting to cross-eigenspace entries, and applying the affine
rescaling `c_ij=E y_ij/(p_i p_j)-1` gives precisely the candidate's set
`C`.  Thus `k` is a minimum support question on an affine slice/projection of
that polytope.  This is much closer than generic fixed-size sampling.

Alain Faye and Quoc-An Trinh, [*A polyhedral approach for a constrained
quadratic 0--1 problem*](https://doi.org/10.1016/j.dam.2004.02.020), *Discrete
Applied Mathematics* 149 (2005), 87--100, is the nearest exact-cardinality
source.  Its accessible technical-report version defines this polytope and
studies its facets for linear optimization.  Anuj Mehrotra, [*Cardinality
constrained Boolean quadratic polytope*](https://doi.org/10.1016/S0166-218X(97)00039-5),
*Discrete Applied Mathematics* 79 (1997), 137--154, instead treats the
upper-cardinality `sum x_i <= k` predecessor.  Manfred Padberg, [*The Boolean quadric
polytope: Some characteristics, facets and
relatives*](https://doi.org/10.1007/BF01589101), *Mathematical Programming*
45 (1989), 139--172, is the corresponding unrestricted precursor.  Itamar
Pitowsky, [*Correlation polytopes: their geometry and
complexity*](https://doi.org/10.1007/BF01594946), *Mathematical Programming*
50 (1991), 395--414, is a second nearby correlation-polytope source.

The accessible Faye--Trinh technical report, and the abstracts/metadata for
the other sources, establish the object and their polyhedral focus.  They do
not establish whether a theorem elsewhere solves the precise sparse-deviation
problem on fixed-marginal slices.  That direct broader comparison remains the
required novelty discriminator.

The other closest primary-source families are narrower:

- Bondesson, [*On Sampling with Prescribed Second-order Inclusion
  Probabilities*](https://doi.org/10.1111/j.1467-9469.2012.00808.x), gives
  fixed-size prescribed-pair design constructions, not an arbitrary-weight
  spectral optimum or an isospectral tangent normal form.
- Hedayat and Rao, [*Sampling plans excluding contiguous
  units*](https://doi.org/10.1016/0378-3758(88)90070-5), concerns fixed-size
  zero-pair patterns.  It is relevant to support zero sets, not to the
  support-minimization plus spectral geometry here.
- Barnes et al., [*Efficient Unbiased
  Sparsification*](https://arxiv.org/html/2402.14925v2), solve separable or
  permutation-invariant divergence objectives and explicitly leave squared
  Mahalanobis distance outside their result.  This is a close support-budget
  antecedent, but it does not control the covariance matrix.
- Dai, Liu, and Rider, [*Quantization Bounds on Grassmann Manifolds and
  Applications to MIMO Communications*](https://doi.org/10.1109/TIT.2007.915691),
  provides the standard small-ball/random-code side of the library argument.
  It does not derive a nonsmooth sampling dependence gauge.

Therefore the plausible increment, if it survives the direct CBQP search,
is precise: arbitrary support-dependent unbiased weights reduce locally to a
fixed-marginal pair-moment slice; its sparsest correlation support sets a
new anisotropic orbit-volume and transform-index exponent.  The anisotropic
covering calculation itself is standard once that reduction is known.

The present bounded search does **not** establish originality.  Calling this
a substantive original advance now would overstate the evidence.  It is a
coherent candidate with one exact collision family still requiring a direct
theorem-by-theorem comparison.

## 3. Significance under Cassette's mathematical contract

In a declared ideal class, the theorem is a real mathematical capability.  A
finite library can be shared, one HT subset law can be shared across all
codewords, a source can select a transform index, and the estimator can read
at most `s` encoded columns while remaining exactly unbiased.  This does not
need a production implementation to be a valid conditional result.

The finite-word boundary correctly prevents a stronger conclusion.  A
rational transform codebook and rational sampler can preserve the index
exponent under exact rational/Gaussian-rational data and exact arithmetic.
For general finite-word source data, the estimator is unbiased for the stored
`R_hat`, not the original `R`; `(R_hat-R)x` is an additional deterministic
error.  Floating-point multiplication, accumulation, and sampling require a
separate numerical theorem.

Equation (7) is only an index asymptotic.  An explicit rational transform
table would cost order `K(epsilon) log(1/epsilon)` at fixed `q`.  The later
finite-atlas rational-grid construction avoids that table: the chart label
and grid coordinates decode a codeword procedurally, so its transform index
has `kappa log_2(1/epsilon)+O(1)` bits.  That removes one avoidable shared
storage term, but leaves a declared decoder, its evaluation work and
precision, and sampler cost.  Each atom also needs its encoded-column
payload.  For a dense transform, an index alone does not make `RV e_i`
readable: one must store the transformed columns, read more source data, or
declare and charge a decoder.  Those are materially different resident-byte
and fresh-traffic models.

This matches `MATHS.md`'s boundary.  Theorem 5 requires a *declared*
description class, a named reconstruction, residual-addressing and sampling
metadata bytes, and a physical conversion from probes to reads.  The
certificate separately requires peak and total description and metadata
bytes, fresh traffic, sequential risk, observation, and quality fields.
The transform-index result fills none of those total fields by itself.

Accordingly, this theorem cannot yet move a Cassette Q19 or resource-frontier
claim.  It matters mathematically because it identifies a possible
transform-library dimension law in a legal ideal class.  It becomes a
consequential Cassette advance only after a further theorem declares one
finite representation and proves a total cost/error tradeoff for it:

1. source and encoded-column representation precision;
2. shared codebook, decoder, sampler, and per-atom index bytes;
3. transformed-column residency or the charged source reads needed to form
   them;
4. numerical bias/variance and risk composition over the intended horizon;
5. conversion to the actual page/byte and observation contracts.

That is a significance requirement, not a request for immediate production
work.  Until it exists, the theorem counts a restricted ideal index and says
nothing about a general byte frontier.

## Decision

Correctness is provisionally supported, conditional on retaining the local
rigidity lemmas as proved dependencies.  Originality remains unverified
against cardinality-constrained Boolean quadratic/correlation-polytope work.
Cassette significance remains conditional on a finite-representation and
total-resource theorem.  The candidate therefore does not yet pass all
three required gates.
