# Parametric SDP sensitivity versus the dependence-gauge normal form

Status: bounded primary-source challenge, 5 September 2026.  This note tests
whether standard value-function sensitivity makes the local sampling theorem
immediate.  It separates a recoverable first-order derivative from the
candidate's uniform quadratic normal form.

## Primary results examined

J.-F. Bonnans and R. Cominetti, [*Perturbed Optimization in Banach Spaces
I*](https://doi.org/10.1137/S0363012994267273), *SIAM Journal on Control and
Optimization* 34 (1996), 1151--1171, treats problems
`min f(x,u)` subject to `G(x,u) in K`, with `f` and `G` twice continuously
differentiable and `K` closed convex.  Its first- and second-order expansions
need directional constraint qualification; its complete solution sensitivity
discussion names uniqueness, multipliers, and second-order sufficient
conditions as the supporting assumptions.

J.-F. Bonnans, R. Cominetti, and A. Shapiro, [*Sensitivity Analysis of
Optimization Problems Under Second Order Regular
Constraints*](https://doi.org/10.1287/moor.23.4.806), *Mathematics of
Operations Research* 23 (1998), 806--831, establishes second-order regularity
for semidefinite optimization and derives Lipschitz/Hölder expansions under a
directional constraint qualification and various second-order sufficient
conditions.  Bonnans, Cominetti, and Shapiro, [*Second Order Optimality
Conditions Based on Parabolic Second Order Tangent
Sets*](https://doi.org/10.1137/S1052623496306760), *SIAM Journal on
Optimization* 9 (1999), 466--492, supplies the corresponding no-gap
second-order framework for smooth cone-constrained programs.

These are genuine general tools.  Their hypotheses and conclusions do not
by themselves identify the sampling problem's derivative or establish the
positive quadratic coefficient needed here.

## 1. A finite-dimensional conic representation exists

Index every support `S` of cardinality at most `s`.  For each `S`, use its
probability `alpha_S`, first moment `m_S`, and unnormalized second moment
`Z_S` of the coefficient subvector.  The perspective constraint is

```
 [ alpha_S  m_S^* ] >= 0,
 [ m_S      Z_S   ]
```

with `sum alpha_S=1` and `sum_S embed(m_S)=1`.  For positive `alpha_S`, this
is exactly the conditional mean/covariance condition for a random coefficient
on `S`.  The covariance matrix is affine in these moments for fixed Gram
matrix `G`, and the epigraph constraint

```
 tau I - ( E[D_b^* G D_b] - G ) >= 0
```

is an LMI whose coefficients depend smoothly and linearly on `G`.  Thus the
closure of the estimator problem is a finite parametric conic program.

There is one nonformal detail.  At `alpha_S=0`, the displayed perspective
cone permits a nonzero `Z_S`; it is a closure point corresponding to escaping
weights rather than an actual zero-probability outcome.  It can be deleted at
an optimum because `G` is positive definite and its contribution to the
second moment is PSD.  To apply a closed-cone sensitivity theorem to the
original estimator problem, one still needs a local level-boundedness/no-loss
argument.  It is available directly near `D`: an objective sublevel bounds
each diagonal sum `sum_S (Z_S)_{ii}` through `a_i>0`; PSD then bounds every
entry of `Z_S`, and the Schur constraint bounds `m_S`.  The probability
simplex is compact.  Strict feasibility is also available by taking all
`alpha_S>0`, choosing feasible first moments, making the `Z_S` blocks strictly
positive, and taking `tau` large.  Thus a standard conic first-derivative
theorem is likely applicable after these details are written.  The
Cauchy-defect proof is one direct way to do the same work, but it is not the
only route.

## 2. What first-order sensitivity would yield

At diagonal `D`, diagonal Cauchy equality identifies the optimum set.  If
`theta_i=P(i is read)`, then

```
 theta_i >= a_i/(a_i+t),     sum theta_i <= s,
```

and equality in the optimal diagonal bound forces

```
 theta_i=p_i=a_i/(a_i+t),    b_i=I_i/p_i a.s. on selection.
```

The remaining optimizer face is therefore the compact polytope `P(p)` of
exact-size subset laws.  Its cross first-order coefficient is

```
 H_c(B) = B circ c,  c_ij=E[I_i I_j]/(p_i p_j)-1.
```

One must also allow first-order changes of the diagonal allocations.  Put

```
 w_i = p_i^2/a_i = a_i/(a_i+t)^2.
```

If `h_i` is the resulting first-order diagonal covariance change, the
fixed-size constraint gives `sum_i w_i h_i=0`.  The linearized value problem
is therefore

```
 d(B) = min_{c in C, sum w_i h_i=0}
        lambda_max( Diag(h)+H_c(B) ).                         (1)
```

The usual trace-density formula for the largest eigenvalue and minimax
duality eliminate `h`:

```
 d(B) = min_{c in C} max_{X in X_w} <X,H_c(B)>,                (2)

 X_w = {X >= 0: tr X=1, diag X=w/sum_i w_i}.
```

The equality follows because minimizing `<X,Diag(h)>` under `w dot h=0` is
finite only when `diag X` is proportional to `w`; trace one fixes that
proportion.  The remaining expression is bilinear in `c` and `X`, so compact
convex minimax duality applies.  Formula (2), rather than an unqualified
Danskin formula over the HT face, is the relevant first epiderivative: a
nearby optimizer may change its diagonal marginals at first order.

It is uniformly equivalent to the candidate gauge.  Write
`D_w=Diag(w/sum w)`, whose smallest diagonal entry is `m>0`.  For a Hermitian
zero-diagonal `H`, `D_w+m H/||H||_F` is PSD after reducing `m` by a fixed
dimension-only factor, has trace one and the required diagonal, and gives a
linear lower bound on `max_{X in X_w}<X,H>`.  The operator-norm bound gives
the upper bound.  Hence, with constants depending only on the fixed diagonal,

```
 m' ||H||_F <= max_{X in X_w}<X,H> <= ||H||_F.
```

Minimizing over `c` gives

```
 d(B) is comparable to min_{c in C} ||B circ c||_F.           (3)
```

Thus a correctly verified first-order parametric-conic theorem can replace
part of the candidate's Section 5: it gives the same *linear* dependence
gauge after this explicit calculation.  It does not make that gauge appear
from the words "Danskin" or "normal cone."  The conic lift, exact base
optimizer characterization, allocation tangent calculation, minimax step,
and norm equivalence are all required.

## 3. Why standard quadratic-growth theorems do not finish the result

The proposed normal form is

```
 Phi_s(G(B))-t  comparable to  ||B||^2 + d(B).                (4)
```

A first-order sensitivity theorem can at most give

```
 Phi_s(G(rB))-t = r d(B) + o(r)
```

under its regularity hypotheses.  This leaves the directions where `d(B)=0`
unresolved.  Equation (4) needs both an `O(r^2)` construction and a *positive
uniform* `Omega(r^2)` lower bound on every such direction.

The standard strong conditions are not automatic here.

- The primal optimal set at `D` is the generally high-dimensional polytope
  `P(p)`, not a unique solution.
- The active spectral LMI is `tI-Q=0`, so its density multipliers form a
  non-singleton spectrahedron; after diagonal allocation is admitted they are
  exactly `X_w` in (2).
- The objective is a largest eigenvalue at a fully multiple eigenvalue and
  the original probability/weight formulation has a union-of-supports
  structure.  These are precisely the degeneracies for which generic strong
  regularity and unique-multiplier hypotheses do not follow from SDP
  second-order regularity.

Second-order regularity of the PSD cone means that the cone has an appropriate
second-order tangent calculus.  It does **not** assert quadratic growth of a
particular marginal value function.  To use the cited theorems one must still
verify a directional constraint qualification, identify the critical cone,
and prove a positive second-order sufficient condition on every critical
direction.  Those are not supplied by `D` being diagonal or by `G` being
positive definite.

Here the needed positive coefficient is the fixed-basis quantitative rigidity
bound, derived from the strict convexity of the diagonal trace-inverse
inequality.  It is a tailored verification of the missing quadratic-growth
condition.  The upper `O(r^2)` branch uses an exact cross-independent HT law
when a zero pattern is feasible and the fact that the isospectral chart has
only second-order diagonal change.  General sensitivity theory does not
construct that law or prove the required feasibility pattern.

## Conclusion for originality

General parametric SDP/minimax sensitivity places the first-order portion in
a standard framework and makes a first-order-only statement a routine
application *after* the conic formulation and calculation above.  It does
not make the full uniform normal form, its dependence-support identification,
or the `kappa` exponent immediate.

This weakens any claim that the whole result is wholly new.  The defensible
increment, if a wider source check finds no direct collision, is the
degenerate problem-specific bridge: arbitrary support-dependent complex
estimators, the exact allocation tangent/minimax derivative, compact
dependence-support geometry, and a separately verified quadratic branch.
The library volume and finite-grid rate are consequences once that bridge is
proved.

No originality gate passes on this bounded comparison alone.
