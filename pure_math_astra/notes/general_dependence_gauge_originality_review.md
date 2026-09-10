# Originality and significance review: dependence-support gauge on an isospectral orbit

Status: bounded adversarial review of a prospective general theorem, completed
5 September 2026.  No novelty or resource-capability claim is accepted.

## Conditional mathematical assessment

Let \(T=\{\{i,j\}:i<j,\ a_i\ne a_j\}\), let
\[
 d=\beta|T|,\qquad \beta=\dim_{\mathbb R}\mathbb F,
\]
and let \(\mathcal C\) be the set of correlation arrays
\[
 C_{ij}=\frac{\pi_{ij}}{p_ip_j}-1
\]
arising from exactly-\(s\) subset laws with marginals
\(p_i=a_i/(a_i+t)\).  This is a compact polytope: it is the linear image of
the finite simplex of laws on size-\(s\) subsets with fixed marginals.

For a tangent coordinate vector \(B\in\mathbb F^T\), define
\[
 g(B)=\min_{C\in\mathcal C}\|B\circ C\|.
\tag{1}
\]
The proposed local normal form is
\[
 \Phi_s(G_B)-t\asymp\|B\|^2+g(B).
\tag{2}
\]
The arbitrary-weight lower direction has a credible route through the
Cauchy-defect and PSD-slack reduction already proved in
\(\texttt{local_basis_variance_dichotomy.md}\).  The spectral conversion is
sound: a nonzero Hermitian off-diagonal first-order matrix has largest
eigenvalue comparable, in fixed dimension, to its Frobenius norm because it
has trace zero.

Let
\[
 k=\min_{C\in\mathcal C}|\operatorname{supp}_T C|.
\tag{3}
\]
If (1) is uniformly comparable to
\[
 h(B)=\min_{C\in\mathcal C}\|B_{\operatorname{supp}_T C}\|,
\tag{4}
\]
then the \(\varepsilon\)-sublevel set has volume
\[
 \Theta\!\left(\varepsilon^{\beta k}
 (\sqrt\varepsilon)^{\beta(|T|-k)}\right)
 =
 \Theta(\varepsilon^\kappa),\qquad
 \kappa=\frac{d+\beta k}{2}.
\tag{5}
\]
The smallest support patterns dominate; patterns with more nonzero
correlations give smaller-volume strata.  This part is an elementary
anisotropic-box calculation after the normal form is established.

The compact zero-pattern argument does give the required uniform
comparison; the earlier review's objection was mistaken.  For every
infeasible coordinate zero set \(Z\), compactness gives
\[
 \epsilon_Z=\min_{C\in\mathcal C}\max_{i\in Z}|C_i|>0.
\]
There are only finitely many patterns.  Choose \(\eta\) below half the
smallest positive \(\epsilon_Z\).  For any \(C\), the coordinates where
\(|C_i|<\eta\) form a feasible zero set; otherwise they contradict its
\(\epsilon_Z\).  A feasible correlation array vanishing there has support
inside the complementary coordinates.  Hence, for coordinatewise Euclidean
norms,
\[
 \|B\circ C\|\geq\eta\min_{S\text{ feasible}}\|B_S\|.
\]
The reverse inequality follows by choosing one bounded representative for
each of finitely many feasible support patterns.  If every zero pattern is
feasible, then \(0\in\mathcal C\) and both gauges vanish.  Thus compactness
and finiteness of coordinate patterns suffice; polyhedrality is useful
context but not needed for this comparison.

The same caveat applies to the finite-library upper bound.  Haar volume
\(\Theta(\varepsilon^\kappa)\) gives the lower bound
\[
 K=\Omega(\varepsilon^{-\kappa})
\]
once the global sublevel set is confined to finitely many coordinate charts.
A random-library upper
\[
 K=O(\varepsilon^{-\kappa}\log(1/\varepsilon))
\]
also needs a uniform inner-sublevel/enlargement relation.  It is plausible
from the polyhedral gauge and smooth orbit charts.  It is not a consequence
of volume alone.  In fixed dimension, a deterministic anisotropic covering
may remove the logarithm, so the random upper should not be called sharp.

## Nearest established fields

The components have established antecedents.

- Fixed-size designs with specified first- and second-order inclusion
  probabilities are a classical survey-sampling problem.  Bondesson,
  [*On Sampling with Prescribed Second-order Inclusion Probabilities*](https://doi.org/10.1111/j.1467-9469.2012.00808.x),
  studies this domain.  Hedayat and Rao,
  [*Sampling plans excluding contiguous units*](https://doi.org/10.1016/0378-3758(88)90070-5),
  explicitly study fixed-size designs with prescribed zero pair inclusions.
  These sources make the pair-moment polytope and zero-pattern language
  familiar; they do not state the present spectral tangent gauge.
- Dai, Liu, and Rider,
  [*Quantization Bounds on Grassmann Manifolds and Applications to MIMO
  Communications*](https://doi.org/10.1109/TIT.2007.915691), give
  small-ball and random-code high-rate bounds for invariant chordal
  distortion.  Zador,
  [*Asymptotic Quantization Error of Continuous Signals and the Quantization
  Dimension*](https://doi.org/10.1109/TIT.1982.1056490), is an older
  high-rate Euclidean quantization source.
- These quantization theorems convert a known local ball/sublevel volume
  into codebook scaling.  They do not derive the basis-dependent,
  nonsmooth gauge (1), whose linear term is selected by a fixed-cardinality
  pair-design polytope.

Thus a general non-Euclidean quantization theorem would make the final
covering exponent routine **after** (2), (4), and the Haar sublevel-volume
calculation.  It does not trivialize the sampling-to-gauge derivation.
Conversely, deriving (2) only for one four-coordinate chart is not enough to
distinguish the work from a specialized application of standard
stratified-sampling arithmetic plus anisotropic covering.

No exact collision was found in this bounded primary-source pass: none of
the sources read combines arbitrary support-dependent unbiased weights,
worst-query spectral covariance, isospectral tangent coordinates, and
support-minimizing pair-correlation patterns.  This is an absence result
only for the sources named here, not a novelty conclusion.

## What would count as a meaningful advance

The prospective theorem becomes more than a four-coordinate calculation if
it proves all of the following for arbitrary multiplicities, cap, and
field:

1. an exact first-order reduction from arbitrary diagonal weights to the
   fixed-marginal pair-inclusion polytope;
2. the uniform local gauge (2), including the polyhedral comparison to
   feasible correlation-support patterns;
3. the exponent \(\kappa=(d+\beta k)/2\) and a matching finite-library
   covering theorem across the full isospectral orbit;
4. a combinatorial characterization or usable bounds for \(k\) from the
   fractional block allocations and the allowed cross-edge graph.

Items 1--4 would be a coherent theorem linking hard read-count arithmetic to
quantization dimension.  It would still concern a declared transform library
and diagonal thinning.

Cassette significance requires one further theorem or model contract:
a library of \(K\) transforms must be represented by a declared resident
description, its index and basis-selection information must have an explicit
byte cost, and its execution must feed the Q19 certificate's fresh-read,
observation, sequential, and quality fields.  Without this, the result
counts ideal transforms; it does not bound bytes or alter a demonstrated
service frontier.

