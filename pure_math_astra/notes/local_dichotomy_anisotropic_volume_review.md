# Review: local variance dichotomy and the proposed anisotropic Grassmann volume

Status: independent proof check and bounded originality/significance challenge,
completed 5 September 2026.  This note does not accept a novelty or
resource-capability claim.

## Verification of the local dichotomy

The proof in \(\texttt{local_basis_variance_dichotomy.md}\) is correct as
written, assuming the cited fixed-basis SDP attainment result.

For the near-equality argument, set
\[
 d_i=G_{ii}(\tau),\quad
 \theta_i=\Pr(b_i\ne0),\quad
 \ell_i=\frac{d_i}{d_i+t+\delta}.
\]
The implications
\[
 \mathbb E|b_i|^2\geq\theta_i^{-1},\quad
 Q_{ii}\leq t+\delta,\quad
 \theta_i\geq\ell_i
\]
are valid.  Since diagonal majorization and concavity give
\(\sum_i d_i/(d_i+t)\geq s\), bounded denominator derivatives yield
\[
 0\leq\sum_i(\theta_i-\ell_i)\leq C\delta.
\]
Isospectrality and \(\operatorname{Diag}E=0\) give
\(d_i=a_i+O(\tau^2)\); hence
\[
 \theta_i=p_i+O(\delta+\tau^2).
\]

The exact complex identity
\[
 \mathbb E\left|b_i-\frac{I_i}{\theta_i}\right|^2
 =\mathbb E|b_i|^2-\frac1{\theta_i}
\]
follows from \(I_i b_i=b_i\) and \(\mathbb Eb_i=1\).  It justifies the
pair-moment approximation in equation (4).

The key PSD slack step is also correct.  For
\[
 M=(t+\delta)I-Q\succeq0,
\]
one has exactly
\[
 M_{ii}=d_i\left(\ell_i^{-1}-\mathbb E|b_i|^2\right)
 \leq d_i(\ell_i^{-1}-\theta_i^{-1})=O(\delta).
\]
The \(2\times2\) principal-minor inequality gives
\[
 |Q_{ij}|=|M_{ij}|\leq\sqrt{M_{ii}M_{jj}}=O(\delta).
\]
On an edge \(E_{ij}\ne0\), division by
\(G_{ij}(\tau)=\tau E_{ij}+O(\tau^2)\), with
\(\delta=o(|\tau|)\), forces the limiting HT pair moment to factor.  Compact
indicator-law convergence then supplies an exact-size limit law with
marginals \(p\).  Conversely, fixed HT weights give the stated \(O(|\tau|)\)
upper bound.

No defect was found in equations (1)--(7).  Two scope conditions should stay
visible: \(1\le s<q\) makes every \(p_i\) interior, and the use of an
optimizer relies on the SDP-attainment theorem already cited in the note.

## The \(q=4,\ s=2\) anisotropic exponent

For spectrum
\[
 (3,3,1/3,1/3),
\]
the unrestricted water level is \(t=1\), and the high-eigenspace inclusion
probability is \(3/4\).  Its expected selected count is \(3/2\), so the
two-block integrality condition fails.

Near a coordinate high-eigenspace, a \(2\times2\) cross chart \(B\) has real
dimension \(4\beta\), where
\[
 \beta=\dim_{\mathbb R}\mathbb F
 =
 \begin{cases}1,&\mathbb F=\mathbb R,\\2,&\mathbb F=\mathbb C.\end{cases}
\]
The diagonal and off-diagonal parts each have real dimension \(2\beta\).
If the conjectured local comparison
\[
 \Phi_2-t\asymp
 \|B\|^2+\min\{\|\operatorname{diag}B\|,\|\operatorname{off}B\|\}
\tag{A}
\]
holds uniformly in the chart, then its \(\varepsilon\)-sublevel set is,
up to fixed constants, the union of two rectangles:
\[
 \|\operatorname{diag}B\|\lesssim\varepsilon,\quad
 \|\operatorname{off}B\|\lesssim\sqrt\varepsilon,
\]
and the same display with the two parts interchanged.  Each has volume
\[
 \varepsilon^{2\beta}(\sqrt\varepsilon)^{2\beta}
 =\varepsilon^{3\beta}.
\]
Their overlap has lower order.  Thus the local acceptable volume is indeed
\(\Theta(\varepsilon^{3\beta})\).

This calculation does **not** follow from the raywise linear/quadratic
dichotomy alone.  To use it, a proof of (A) needs a uniform two-sided bound
over the whole chart.  In particular it must exclude directions approaching
the diagonal or off-diagonal axes from losing their linear coefficient at a
rate faster than the displayed minimum.  The combinatorial sampler
classification, not ordinary Grassmann geometry, is where that work lies.

Given uniform (A), the covering consequences are standard:

- a library needs \(\Omega(\varepsilon^{-3\beta})\) local centers, modulo
  the constant number of coordinate charts/projections;
- a random-cover argument can give
  \(O(\varepsilon^{-3\beta}\log(1/\varepsilon))\) under a uniform
  enlargement condition;
- in fixed dimension, a deterministic anisotropic grid may remove the
  logarithm.  The random logarithm should not be presented as an optimal
  upper rate without checking this.

For comparison, \(\operatorname{Gr}_{\mathbb F}(2,4)\) has real dimension
\(4\beta\).  Ordinary squared-chordal distortion has small-ball volume
\(\varepsilon^{2\beta}\) and codebook exponent \(2\beta\); ordinary linear
chordal distortion has volume \(\varepsilon^{4\beta}\) and exponent
\(4\beta\).  The proposed \(3\beta\) lies between them because two real
coordinate blocks need \(O(\varepsilon)\) accuracy while the other two need
only \(O(\sqrt\varepsilon)\).

## Existing quantization and sampling work

Dai, Liu, and Rider,
[*Quantization Bounds on Grassmann Manifolds and Applications to MIMO
Communications*](https://doi.org/10.1109/TIT.2007.915691), derive
small-ball volume and high-rate codebook bounds for chordal metric balls.
Their framework makes the covering step routine once a ball volume is known,
but it does not provide (A): the proposed sublevel set is a
basis-dependent union of anisotropic tubes, not an invariant chordal ball.

A generic non-Euclidean or anisotropic quantization theorem would likewise
settle only the final volume-to-covering conversion if it assumed comparable
sublevel volumes or an appropriate quasi-metric.  It would not trivialize
the sampling calculation that produces those volumes.  The cost in (A) is
not a smooth invariant Finsler metric at the coordinate plane; its
\(\min\) structure records two distinct cancellation designs.

The sampling ingredient itself uses standard fixed-size unequal-probability
and stratified-allocation facts.  Bondesson,
[*On Sampling with Prescribed Second-order Inclusion Probabilities*](https://doi.org/10.1111/j.1467-9469.2012.00808.x),
is close terminology.  The arithmetic fact that a fixed stratum count must
be integral is elementary survey sampling.  No source read in this bounded
pass states the link from that arithmetic obstruction to anisotropic
Grassmann sublevel volume.  That absence is not an originality result.

## What would make it materially stronger

The four-coordinate exponent is a useful test case, not a consequential
resource theorem.  A meaningful generalization would characterize, for
arbitrary two-block sizes \(m,n\), cap \(s\), and cross-edge support pattern,
the local sublevel volume of
\[
 \Phi_s\!\left(V^*
 [\lambda_-I+(\lambda_+-\lambda_-)P]V\right)-t
\]
near every coordinate plane.  Its exponent should be expressed through the
fractional block allocation and the combinatorial set of pair-independence
cancellation designs.  It must include both a uniform local comparison like
(A) and matching finite-library lower and constructive upper bounds.

Only after that general theorem can a Cassette-relevant result be attempted:
the transform library must be a declared resident description class, its
index and selection information must have explicit byte cost, and the chosen
transform must enter the Q19 execution certificate with fresh-read,
sequential, observation, and quality fields.  Without those links,
\(\varepsilon^{-3\beta}\) counts ideal chart centers, not executable bytes
or a changed service capability.

