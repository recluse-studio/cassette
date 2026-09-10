# Fixed-Gram-orbit invariant-method comparison

Scope: this is a bounded method and provenance check for
`../notes/fixed_gram_orbit_static_oracle_minimax_independent_proof.md`.
It assesses the \(O(p)\)-invariance reduction, not the originality of its
precise final statement and not its significance as a Cassette result.

## Primary sources read

1. J. Kiefer, [*Invariance, Minimax Sequential Estimation, and Continuous
   Time Processes*](https://projecteuclid.org/journals/annals-of-mathematical-statistics/volume-28/issue-3/Invariance-Minimax-Sequential-Estimation-and-Continuous-Time-Processes/10.1214/aoms/1177706874.full),
   *Annals of Mathematical Statistics* 28 (1957), 573--601,
   [DOI](https://doi.org/10.1214/aoms/1177706874).  I read the primary
   article's indexed opening discussion and its displayed Hunt--Stein
   averaging formula.  It explicitly observes that for a compact invariant
   group, normalized Haar averaging of a decision rule produces an invariant
   rule with no greater supremum risk.  The publisher page itself exposed
   only an iframe to this reader during this check.

2. G. W. Wasilkowski, [*Information of Varying
   Cardinality*](https://www.researchgate.net/publication/256619980_Information_of_varying_cardinality),
   *Journal of Complexity* 2 (1986), 204--228,
   [DOI](https://doi.org/10.1016/0885-064X(86)90002-6).  I read the full
   available primary-text rendering: its definitions in Section 2, the
   worst-case construction in Proposition 3.1, and Theorem 4.1 with its
   proof setup in Section 6.  It considers a linear problem, arbitrary
   algorithms based on linear information, and information functionals or
   stopping rules that may depend on previously observed source values.

The first source is the closest precedent for the Haar step.  The second is
the closest read primary IBC comparison for source-adaptive information and
cardinality.  Neither is offered as an exhaustive search.

## What is standard here

**Fact.** Kiefer's compact-group case gives exactly the general move used in
the orbit proof: average a decision rule over normalized Haar measure, retain
equivariance, and do not increase invariant supremum risk.  In the present
setting the feasible set is also convex: the pointwise identity

\[
 \sum_S p_SF_S(A_{:S},x)=Ax
\]

is preserved by the same averaging.  Thus the proof's passage from an
arbitrary Borel decoder to an \(O(p)\)-equivariant decoder is standard
invariant-decision machinery, specialized to a compact group.

**Fact.** Once equivariance holds, the stabilizer of \(A_{:S}\) contains the
full orthogonal group on \(\operatorname{span}(A_{:S})^\perp\).  Its fixed
vectors are exactly \(\operatorname{span}(A_{:S})\).  The resulting form
\(F_S(A_{:S},x)=A_{:S}c_S(x)\), and the independence of \(c_S(x)\) from
the orbit point by transitivity, are direct finite-dimensional consequences
of this stabilizer calculation.  They are not a distinct general method.

**Fact.** With that form imposed, minimizing

\[
 \sum_Sp_Sc_S^TG_{SS}c_S-x^TGx
 \quad\text{subject to}\quad
 \sum_Sp_SE_Sc_S=x
\]

is an ordinary strictly convex quadratic program.  Its multiplier equations
give \(c_S=G_{SS}^{-1}E_S^TM^{-1}x\) and the value
\(x^T(M^{-1}-G)x\).  This is a generalized least-squares calculation, not
an invariant-decision innovation.

**Fact.** Wasilkowski's definitions make "adaptive" source-adaptive:
later linear functionals and termination can depend on earlier values of the
unknown input.  Its Theorem 4.1 replaces such Gaussian-average information
by nonadaptive information of comparable or no greater average cardinality
and radius under the stated convexity or semiconvexity hypotheses.  This
supports treating reductions from broad nonlinear information models to
fixed information as established IBC territory.  It does not supply the
orbit proof's exact formula.

## The constraint that remains outside those results

The orbit theorem requires one *shared random-support mixture* to be exactly
unbiased for every source in the orbit and every query:

\[
 \sum_Sp_SF_S(A_{:S},x)=Ax. \tag{1}
\]

After symmetrization this becomes the cross-branch coefficient condition

\[
 \sum_Sp_SE_Sc_S(x)=x. \tag{2}
\]

It couples outputs from different supports.  The standard IBC model in
Wasilkowski evaluates one source through a deterministic or source-adaptive
sequence of linear functionals and minimizes an average radius.  It neither
requires (1) nor optimizes a random-support mixture under (2).  Its
adaptivity is driven by observed source values, whereas the orbit note's
query-dependent extension selects the support distribution after an
externally supplied query \(x\), still independently of the source \(A\).
Those are different quantifier orders.

Kiefer likewise establishes the averaging principle rather than the
coefficient program.  Its decision rules are not constrained by an
all-parameter exact-mean identity such as (1), and its minimax theorem does
not identify \(M^{-1}-G\) for randomized coordinate supports.

**Inference.** The exact theorem is best described as a direct assembly of
classical compact-group symmetrization, an elementary stabilizer argument,
and a coupled quadratic program.  The method itself should not be presented
as new.  The two sources read do not establish whether this particular
all-orbit, support-randomized, exactly unbiased statement has already been
recorded elsewhere.

## Mathematical consequence within the stated oracle model

**Fact conditional on the orbit proof.** The reduction eliminates a possible
escape route: arbitrary nonlinear decoding of fetched columns cannot improve
the fixed-schedule minimax value on a full fixed-Gram orbit.  Every such
decoder is lower-bounded by the same coefficient program as a linear
decoder, and the displayed linear decoder attains it.  The trace identity
\(\operatorname{tr}(GM)=\mathbb E|S|\) then gives the same expected-read
lower bound even when the fixed schedule has variable support size.

**Limit.** This consequence is confined to real, full-rank fixed-Gram
orbits; a source- and query-independent schedule; pointwise exactness; and
the stated column-oracle observation model.  It does not settle a resident
transform, source-trained state, physical-page, finite-word, or general
Cassette execution question.

## Search limit

This check read one primary invariant-decision source and one primary IBC
source.  It establishes that the reduction's central techniques are standard
and that their published hypotheses omit the cross-support exactness above.
It does not establish novelty, priority, or absence of a closer result in
unbiased randomized linear estimation, invariant decision theory, or
information-based complexity.
