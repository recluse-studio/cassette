# Primary comparison: Boolean quadratic polytopes and the dependence gauge

Status: bounded source challenge, 5 September 2026.  This note asks whether
Boolean-quadratic/correlation-polytope theory already makes the proposed
dependence gauge and transform-index exponent immediate.  It does not make a
novelty claim.

## The exact relation

For an exactly-`s` subset law, put `x_i=I_i` and `y_ij=I_i I_j`.  Its first
and second inclusion moments lie in

```
 QP(q,s) = conv{(x,y): x in {0,1}^q, sum_i x_i=s,
                         y_ij=x_i x_j}.
```

Fixing `E x=p`, restricting to the cross-eigenvalue edge set `T`, and applying
the invertible coordinatewise affine map

```
 E y_ij  ->  c_ij = E y_ij/(p_i p_j)-1
```

gives exactly the candidate set `C`.  Thus its pair-moment polytope is not
new.  Its minimum support number `k` is a nonconvex support-minimization
problem on a fixed-marginal affine slice/projection of `QP(q,s)`.

## What the accessible primary sources actually prove

### Mehrotra (1997): nearby, but an upper-cardinality polytope

Anuj Mehrotra, [*Cardinality constrained Boolean quadratic
polytope*](https://doi.org/10.1016/S0166-218X(97)00039-5), *Discrete Applied
Mathematics* 79 (1997), 137--154, states in its available abstract that it
studies the polyhedral structure of an integer-programming formulation,
provides many facet-defining inequalities, and discusses difficult separation
problems.  The accessible bibliographic discussion identifies Mehrotra's
constraint as `sum_i x_i <= k`, not equality.  It therefore supplies an
upper-cardinality ancestor, not the exact-size moment slice used here.

The exact-size class is still closely related: the strict `QP(q,s)` is a
face of the unrestricted Boolean quadric polytope.  Faye--Trinh prove this
as Proposition 3.2 by intersecting two clique faces; equivalently, for binary
`x`, the linearized objective `-(sum_i x_i-s)^2` is zero exactly at
cardinality `s` and negative otherwise.  This observation makes Mehrotra
relevant background, but none of the accessible Mehrotra statement is a
theorem about fixed marginals, sparse deviations from independence, or
sensitivity of a spectral covariance optimum.

### Faye--Trinh (2005): the exact-size primary predecessor

Alain Faye and Quoc-An Trinh, [*A polyhedral approach for a constrained
quadratic 0--1 problem*](https://doi.org/10.1016/j.dam.2004.02.020), *Discrete
Applied Mathematics* 149 (2005), 87--100, is the closest exact-size source.
Its accessible full technical-report manuscript explicitly defines
`QP(n,k)=conv{(x,y): sum x_i=k, y_ij=x_i x_j}`, distinguishes that equality
case from Mehrotra's upper-bound case, and studies its relation to Padberg's
polytope and families of facets for cutting planes.  The report says that it
gives a complete description for `k=2` and `k=n-2`, investigates a facet
family in general, and uses those facets computationally.  Its target is
linear optimization over the lifted polytope.  Its Proposition 3.2 proves
`QP(n,k)` is a face of `QP(n)`, and Consequence 3.2 lifts each facet of that
face to a facet of `QP(n)` modulo the affine-hull equalities.  A direct search
of the manuscript finds no normal-cone or sensitivity theorem.

This is a direct collision with the proposed work's *combinatorial domain*,
not with its claimed increment.  Its stated results do not contain:

1. a fixed-marginal slice `E x=p` together with the support minimization of
   `E y_ij-p_i p_j`;
2. an arbitrary complex, support-dependent unbiased coefficient law;
3. a reduction of near-optimal spectral covariance to the fixed-marginal
   slice;
4. an isospectral-orbit normal form, Haar sublevel exponent, or transform
   codebook rate.

The manuscript is substantial direct evidence for those limits because its
sections are devoted to affine hulls, facet operations, facet families, and a
cutting-plane routine.  The published 2005 full text was not separately
accessible in this pass, so this is a scope comparison to the available
primary manuscript and published abstract, not a certification that no hidden
theorem appears in the final version.

### Padberg (1989) and Pitowsky (1991): unrestricted domain and probability

Manfred Padberg, [*The Boolean quadric polytope: Some characteristics,
facets and relatives*](https://doi.org/10.1007/BF01589101), *Mathematical
Programming* 45 (1989), 139--172, studies the unrestricted linearized
quadratic binary polytope.  Its accessible abstract lists three facet
families, symmetry, sparse-form variants, and linear-optimization
consequences.  It does not state a fixed-cardinality, fixed-marginal
dependence-support theorem.

Itamar Pitowsky, [*Correlation polytopes: their geometry and
complexity*](https://doi.org/10.1007/BF01594946), *Mathematical Programming*
50 (1991), 395--414, defines correlation polytopes from event probabilities,
proves membership and facet-complexity results, and describes symmetries.
The directly available abstract reports these results.  A later source cites
Pitowsky's Theorem 1.1 for the representation equivalence between a point of
the correlation polytope and a system of events with the stated first and
pair probabilities.  That is precisely the standard moment interpretation
above.  The primary full text was paywalled in this pass; I did not infer an
unread sensitivity theorem from it.

## Why normal-fan and sensitivity facts do not give the candidate theorem

For a polytope, a normal cone describes which **linear** objectives maximize
on one of its faces.  The candidate does not optimize a linear objective over
`C`.  It first minimizes a largest-eigenvalue covariance over arbitrary
complex weighted laws, then shows that every near minimizer induces a nearby
point in the fixed-marginal moment slice.  Its first-order term is the
nonconvex quantity

```
 min_{c in C} ||B circ c||,
```

where the zero coordinates of `c` can be selected differently for different
directions `B`.  This is neither the support function of `C` nor a normal-cone
derivative of a linear program.  A general parametric-LP theorem would only
describe the piecewise-linear value of a *linear* objective over `C`; it does
not establish the arbitrary-weight reduction, the PSD slack estimates, or the
minimum-support gauge.

Once the local gauge is proved, the rest divides cleanly:

- the compact zero-pattern comparison is an elementary finite-dimensional
  fact about `C`;
- the anisotropic sublevel volume and Haar covering are standard geometry and
  quantization;
- neither is supplied by the Boolean-polytope sources as an isospectral
  spectral-covariance theorem.

No accessible theorem in Mehrotra, Faye--Trinh, Padberg, or Pitowsky makes
the complete candidate immediate.  This is a bounded noncollision result,
not evidence that an equivalent theorem does not exist elsewhere.

## Consequence for the originality gate

The candidate's defensible possible increment is narrow and testable:

> Under a hard exact support cap, arbitrary complex support-dependent
> unbiased estimators that are near-optimal for worst-query covariance reduce
> locally to a fixed-marginal pair-moment slice; the sparsest dependence
> pattern in that slice sets an anisotropic isospectral-orbit volume and a
> transform-index exponent.

The fixed-size moment polytope, its facets, and its probability
interpretation are established prior work.  The dimension and random-cover
steps are established geometry once the local gauge exists.  To pass
originality, a further source check must search for this full bridge in
work on parametric semidefinite optimization, optimal experimental design,
and correlation-polytope moment problems, using the displayed statement as
the query rather than the word "sampling."

## Source-access limits

Mehrotra's primary paper was accessible only through its abstract/metadata;
the displayed citations in later work confirm it treats the `<= k` case.
Faye--Trinh's full technical report was accessible and is the basis for the
exact-size comparison; the published paper's abstract was accessible but not
its body.  Padberg and Pitowsky were accessible through abstracts/metadata,
not complete primary text.  None of these limits permits a positive novelty
finding.
