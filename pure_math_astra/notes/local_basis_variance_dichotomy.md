# Local basis error: a linear or quadratic gap

Status: supporting theorem under a declared fixed-basis sampling model.
The argument has been independently reconstructed. Its originality and
significance have not passed the research goal.

## Model and statement

Let \(D=\operatorname{Diag}(a_1,\ldots,a_q)\succ0\), let \(1\le s<q\), and
let \(t>0\) solve
\[
 \sum_i\frac{a_i}{a_i+t}=s.
\]
Write \(p_i=a_i/(a_i+t)\). Consider an isospectral family of positive
definite Gram matrices with
\[
 G(\tau)=D+\tau E+O(\tau^2),\qquad \tau\longrightarrow0,
\]
where \(E=E^*\ne0\) and \(\operatorname{Diag}E=0\). The remainder is in
operator norm; finite dimension makes the choice of matrix norm immaterial.

For each Gram matrix, \(\Phi_s(G)\) is the least largest eigenvalue of
\[
 Q=\mathbb E[D_b^*GD_b]-G
\]
among random vectors \(b\in\mathbb F^q\) satisfying
\(\mathbb Eb=\mathbf1\), \(|\operatorname{supp}b|\le s\) almost surely, and
finite second moment. The weights may be complex and may depend on the
whole subset. The ideal variance over unrestricted unbiased rank-at-most-\(s\)
random operators is \(t\), which is constant on this isospectral family.

Exactly one of the following cases holds.

1. There is a law on exactly-\(s\) subsets with marginal probabilities
   \(p_i\) and joint probabilities \(p_ip_j\) for every pair with
   \(E_{ij}\ne0\). Then
   \[
   \Phi_s(G(\tau))-t=\Theta(\tau^2).
   \]
2. There is no such law. Then
   \[
   \Phi_s(G(\tau))-t=\Theta(|\tau|).
   \]

All constants are local to the fixed path, spectrum, dimension, and read cap.
The linear lower constant is not uniform over dense directions approaching
a direction with zero entries. The result charges reads in this diagonal
thinning model. It does not supply a lower bound for general page decoders.

## Proof

The fixed-basis SDP in the coded-basis rigidity note attains its optimum.
The marginal lower bound and quantitative rigidity inequality in that note
also apply to every matrix here.

First, suppose the subset law in case 1 exists. Keep that law fixed and put
\(b_i=I_i/p_i\), where \(I_i\) is its inclusion indicator. Its covariance is
\[
 Q_{ii}=G_{ii}(\tau)(p_i^{-1}-1)=t+O(\tau^2),
\]
\[
 Q_{ij}=G_{ij}(\tau)
       \left(\frac{\mathbb E[I_iI_j]}{p_ip_j}-1\right),\quad i\ne j.
\]
If \(E_{ij}\ne0\), the coefficient in parentheses is zero. Otherwise
\(G_{ij}(\tau)=O(\tau^2)\). Thus \(Q=tI+O(\tau^2)\), proving the quadratic
upper bound. Quantitative rigidity gives a lower bound that is a positive
constant times \(\|\operatorname{off}G(\tau)\|_F^2\) throughout a sufficiently
small neighborhood of \(D\). Since \(E\ne0\), that norm squared is
\(\Theta(\tau^2)\). This proves case 1.

An exact-\(s\) law with marginals \(p\) always exists: \(0<p_i<1\) and
\(\sum_i p_i=s\), so \(p\) belongs to the convex hull of the size-\(s\)
indicator vectors. Any such law, with fixed HT weights, gives
\(Q=tI+O(|\tau|)\). Hence the upper bound in case 2 is automatic.

It remains to prove that an excess smaller than linear forces the subset
law in case 1. Suppose, toward that implication, that a sequence of
nonzero \(\tau\) tending to zero has optimal excess
\[
 \delta=\Phi_s(G(\tau))-t=o(|\tau|).
\]
Take an optimal random vector \(b\) at each point. Let
\[
 I_i=\mathbf1_{\{b_i\ne0\}},\quad
 \theta_i=\mathbb E I_i,\quad
 d_i=G_{ii}(\tau),\quad
 \ell_i=\frac{d_i}{d_i+t+\delta}.
\]
Marginal Cauchy gives
\[
 \mathbb E|b_i|^2\ge\frac1{\theta_i},\qquad
 \theta_i\ge\ell_i,\qquad \sum_i\theta_i\le s.
\]
The diagonal of a Hermitian matrix is majorized by its eigenvalues, and
\(x/(x+t)\) is concave. Isospectrality therefore gives
\[
 \sum_i\frac{d_i}{d_i+t}\ge s.
\]
The derivatives in the scalar denominator are uniformly bounded near
\(D\). Consequently
\[
 0\le \sum_i(\theta_i-\ell_i)
 \le s-\sum_i\ell_i\le C\delta.
 \tag{1}
\]
All \(\ell_i\) stay bounded away from zero, so (1) implies
\[
 \theta_i=p_i+O(\delta+\tau^2),\qquad
 \mathbb E|b_i|^2-\frac1{\theta_i}
 \le\frac1{\ell_i}-\frac1{\theta_i}=O(\delta).
 \tag{2}
\]
The latter defect is exactly
\[
 \mathbb E\left|b_i-\frac{I_i}{\theta_i}\right|^2.
 \tag{3}
\]
This identity uses \(\mathbb Eb_i=1\) and remains valid for complex \(b_i\).
Bounded second moments and Cauchy then imply
\[
 \mathbb E[\overline b_i b_j]
 =\frac{\mathbb E[I_iI_j]}{\theta_i\theta_j}+O(\sqrt\delta).
 \tag{4}
\]

Let \(M=(t+\delta)I-Q\succeq0\). Its diagonal obeys the stronger bound
\[
 0\le M_{ii}
 \le d_i\left(\frac1{\ell_i}-\frac1{\theta_i}\right)
 \le C\delta.
 \tag{5}
\]
Every two-by-two principal minor of \(M\) is positive semidefinite. Thus
\[
 |Q_{ij}|=|M_{ij}|\le\sqrt{M_{ii}M_{jj}}\le C\delta
 \quad(i\ne j).
 \tag{6}
\]
For \(E_{ij}\ne0\), \(G_{ij}(\tau)=\tau E_{ij}+O(\tau^2)\), and
\[
 Q_{ij}=G_{ij}(\tau)
       \bigl(\mathbb E[\overline b_i b_j]-1\bigr).
\]
Dividing (6) by \(G_{ij}(\tau)\), then using (4), yields
\[
 \frac{\mathbb E[I_iI_j]}{\theta_i\theta_j}\longrightarrow1.
 \tag{7}
\]

The laws of the indicator vectors lie in the compact simplex on subsets
of size at most \(s\). Pass to a convergent subsequence. Equation (2) gives
marginals \(p_i\), whose sum is \(s\); the limiting law must therefore put
all its mass on size-\(s\) subsets. Equation (7) gives the required edge
pair probabilities \(p_ip_j\). This proves the implication.

If case 1 is infeasible and no positive linear lower constant existed,
one could choose a sequence with \(\delta/|\tau|\to0\), contradicting that
implication. The linear upper bound already proved completes case 2.
\(\square\)

## Two eigenvalue blocks

Suppose \(D\) has eigenvalue \(a\) on \(m\) coordinates and eigenvalue \(b\)
on \(n\) coordinates. Put
\[
 p=\frac a{a+t},\quad r=\frac b{b+t},\quad mp+nr=s.
\]
A tangent direction to this isospectral orbit has only cross-block entries.
If every cross-block entry of the direction is nonzero, the quadratic
case holds exactly when \(mp\) is an integer.

Indeed, let \(K,L\) be the selected counts in the two blocks. Cross-block
pair independence gives \(\operatorname{Cov}(K,L)=0\). Since \(K+L=s\)
almost surely,
\[
 \operatorname{Cov}(K,L)=-\operatorname{Var}K.
\]
Thus \(K=mp\) almost surely, forcing integrality. Conversely, when \(mp=k\)
is integral, choose a uniform \(k\)-subset in the first block and a uniform
\((s-k)\)-subset in the second block, independently. Its marginals and
cross-block pair moments have the required values.

The word “every” matters. A direction with some zero cross entries may
admit a suitable design even when the block count is not integral.
Different directions at the same eigenbasis can therefore have different
orders of variance excess.

## What this changes, and what remains open

This result classifies the local error order of a fixed encoded basis.
It shows that the expected number of selected columns in an eigenspace
can determine whether a small basis error costs first or second order
variance. Orthogonality alone does not describe that local cost.

The theorem does not yet determine the number of transforms needed to
cover an isospectral orbit at a given excess. Directions with zero entries
may dominate the volume of the set of acceptable bases. The next question
is to calculate that volume from the feasible sampling designs, while
retaining the finite-library and decoder assumptions. The four-coordinate,
two-read case is the first unresolved calculation.

No claim of substantive originality is accepted here. The proof uses
marginal equality, finite moment compactness, and the earlier quantitative
rigidity bound. A primary-source comparison must determine whether the
classification is already present or follows routinely from existing
sampling and sensitivity results.

