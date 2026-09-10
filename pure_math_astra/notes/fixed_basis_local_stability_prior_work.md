# Local stability of fixed-basis sampling: prior-work and significance challenge

Status: bounded comparison and theorem-scope audit, completed 5 September 2026.
This note does not accept a novelty or Cassette-significance claim.

## Candidate local theorem and the equality face

Let \(D=\operatorname{Diag}(a_1,\ldots,a_q)\succ0\), \(1\le s<q\), and
let \(t>0\) solve
\[
 \sum_i\frac{a_i}{a_i+t}=s,\qquad p_i=\frac{a_i}{a_i+t}.
\tag{1}
\]
Thus \(0<p_i<1\) and \(\sum_i p_i=s\).  Let
\[
 G(\tau)=D+\tau E+O(\tau^2)
\tag{2}
\]
be a \(C^2\) isospectral Hermitian path with \(E\ne0\) off diagonal.  An
isospectral path has constant unrestricted water level \(t\), and its
diagonal changes only at second order.

The proposed dichotomy is:
\[
 \Phi_s(G(\tau))-t=
 \begin{cases}
 \Theta(\tau^2),&
 \text{if a size-\(s\) support law with marginals \(p\) has}\\
 &\quad\Pr(i,j\in S)=p_ip_j\ \text{on every edge }E_{ij}\ne0,\\
 \Theta(|\tau|),&\text{otherwise.}
 \end{cases}
\tag{3}
\]
The constants may depend on the fixed path and direction.  They cannot be
uniform over all dense \(E\) without a normalization and a lower bound on
the relevant entries.

The upper half of the first case is direct.  Use the stated support law and
the HT weights \(b_i=\mathbf1\{i\in S\}/p_i\).  At \(\tau=0\), its covariance
is \(tI\).  In the first derivative, the \(ij\) entry is
\[
 E_{ij}\left(\frac{\Pr(i,j\in S)}{p_ip_j}-1\right).
\tag{4}
\]
It vanishes on every nonzero entry of \(E\), so the covariance is
\(tI+O(\tau^2)\).  The quadratic lower bound in
\(\texttt{coded_basis_rigidity.md}\), applied to the nonzero first-order
off-diagonal part \(\tau E\), gives a matching
\(\Omega(\tau^2)\) lower bound.

The second case requires one substantive analytical lemma before it is a
proof, rather than a plausible expansion.

**Near-equality reduction lemma needed.**  Suppose
\[
 \lambda_{\max}\!\bigl(\mathbb E(D_b^*G(\tau_m)D_b)-G(\tau_m)\bigr)
 \le t+o(|\tau_m|)
\tag{5}
\]
along \(\tau_m\to0\).  Then, after a subsequence, the support law converges
to a probability distribution on size-\(s\) subsets with marginals \(p\);
the nonzero weights converge in \(L^2\) to the HT values
\(\mathbf1\{i\in S\}/p_i\); and the first-order covariance is (4).

The required ingredients are elementary but must be written carefully:

1. the diagonal spectral bound and coordinate Cauchy--Schwarz force
   \(\Pr(b_i\ne0)\to p_i\) and
   \(\mathbb E|b_i|^2\to1/p_i\);
2. since \(\sum_i p_i=s\) and support is at most \(s\), supports become
   exact-size in the limit;
3. equality in Cauchy--Schwarz gives the HT value, including its complex
   phase, on every selected coordinate;
4. the finite simplex of support laws is compact.

If no limiting support law factorizes on every edge of \(E\), the matrix in
(4) is nonzero, Hermitian, and has zero diagonal.  Hence it has a positive
largest eigenvalue.  Compactness of the equality-face support polytope then
makes the minimum positive for each fixed signed direction.  This proves the
linear lower term, provided the near-equality reduction lemma is proved.
The same argument works on both sides of zero, with the sign of \(E\)
reversed.

This identifies the exact point that is not merely a first-order formal
calculation: arbitrary, unbounded, support-dependent weights must be shown
not to evade the HT equality face.  The earlier marginal proof supplies the
necessary coercive second-moment bounds, but the sequential compactness and
first-order passage should be stated as a lemma in any final theorem.

## Two eigenblocks

For
\[
 D=\operatorname{diag}(\alpha I_r,\beta I_m),\qquad \alpha\ne\beta,
\]
write \(K\) for the selected number from the first block.  If every
cross-block entry of \(E\) is nonzero, factorization in (3) says
\[
 \mathbb E(I_iI_j)=p_\alpha p_\beta
 \quad (i\text{ in block one},\ j\text{ in block two}).
\]
Summing gives
\[
 \mathbb E[K(s-K)]=(\mathbb EK)(s-\mathbb EK).
\]
Therefore \(\operatorname{Var}K=0\), so
\[
 rp_\alpha=\mathbb EK\in\mathbb Z,
 \qquad mp_\beta=s-rp_\alpha\in\mathbb Z.
\tag{6}
\]
Conversely, if these counts are integers, choose exactly the stated number
uniformly in each block, independently between blocks.  This realizes the
marginals and all cross-block pair products.  Thus the two-block
integrality criterion is exact, subject to the near-equality reduction lemma
for the linear half.

## What is standard, and what is model-specific

Several components are standard facts with established names.

- The set
  \[
  \{p\in[0,1]^q:\sum_i p_i=s\}
  =\operatorname{conv}\{\mathbf1_S:|S|=s\}
  \]
  is the hypersimplex, equivalently the base polytope of the uniform
  matroid.  See J. Edmonds, *Submodular functions, matroids, and certain
  polyhedra* (1970), bibliographic record
  [here](https://cir.nii.ac.jp/crid/1572261550435570688).
- Equality in the coordinate Cauchy--Schwarz bound is the ordinary
  Horvitz--Thompson equality condition: conditional on inclusion, the
  unbiased coordinate weight is fixed.
- Fixed-size sampling with prescribed first- and second-order inclusion
  probabilities is established survey-sampling terminology.  Bondesson,
  *On Sampling with Prescribed Second-order Inclusion Probabilities*
  (2012), [DOI](https://doi.org/10.1111/j.1467-9469.2012.00808.x), is the
  closest source read.  In survey language, (6) is a fixed allocation to two
  strata, and the sufficiency construction is independent stratified
  sampling.
- The passage from a compact equality set to a first-order value is a
  directional-sensitivity argument in the style of Danskin's max-min
  theorem; see J. M. Danskin, *The Theory of Max-Min, with Applications*,
  SIAM J. Appl. Math. 14 (1966),
  [DOI](https://doi.org/10.1137/0114053).

The entire dichotomy is not a routine quoted corollary of any one of these
sources.  They do not supply its arbitrary-weight near-equality reduction,
the spectral objective, or the exact edgewise factorization criterion.
Conversely, the theorem is assembled from familiar hypersimplex geometry,
HT equality, fixed-stratum arithmetic, and first-order spectral
sensitivity.  The appropriate description is therefore a model-specific
stability lemma unless a broader prior-art search finds an equivalent
formulation.

Terms that help literature searching are: *fixed-size unequal-probability
sampling*, *prescribed first- and second-order inclusion probabilities*,
*Horvitz--Thompson variance*, *stratified fixed allocation*, *directional
sensitivity of optimal value*, and *hypersimplex*.  “Basis quantization” and
“combinatorial covariance” are useful internal labels, not established names
for this theorem.  “Optimal unbiased sparsification stability” describes the
model but is too recent/broad to presume a standard literature term.

Barnes et al., *Efficient Unbiased Sparsification*,
[arXiv:2402.14925](https://arxiv.org/abs/2402.14925), remains nearby but
does not cover this result: it treats expected separable or
permutation-invariant divergence, explicitly leaves nonseparable
Mahalanobis loss open, and does not optimize a worst-query covariance
matrix.

## Consequence boundary for Cassette

Even if proved, (3) is a local sensitivity theorem for one restricted
coded-access class.  By itself it neither prices a resident description nor
changes the fresh-I/O or quality certificates in \(\texttt{MATHS.md}\).
It says that a coordinate basis can be locally expensive when the optimal
block read counts are nonintegral; it does not show that Cassette must use
such a basis, that a legal transform cannot avoid it, or how many bytes a
transform costs.

A materially consequential next theorem would have to make the
basis--description tradeoff finite.  One concrete target is:

> For a declared \(d\)-dimensional isospectral orbit and every resident
> transform library \(\mathcal L\) of at most \(N\) encodable transforms,
> prove a lower bound on
> \[
> \sup_{G\text{ in a declared orbit region}}
> \min_{U\in\mathcal L}
> \left[\Phi_s(U^*GU)-t\right]
> \]
> in terms of \(N\), orbit covering radius, and the nonintegral allocation
> gap; then pair it with an explicit transform encoding and selection
> metadata cost of at least \(\lceil\log_2N\rceil\) bits.

No such bound is claimed here.  A proof would turn local directional cost
into a finite resident-byte versus worst-query-risk curve.  To matter for
Cassette, that curve would still need to enter a declared Q19 plan with a
legal description class, exact selection observation, fresh-read accounting,
and the sequential and quality certificates that MATHS.md keeps separate.

