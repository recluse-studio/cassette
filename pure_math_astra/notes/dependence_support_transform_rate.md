# Sampling dependence and the size of a transform library

Status: candidate argument with independent mathematical reconstruction.
This is a candidate theorem in a restricted encoded-column model. Correctness,
originality, and significance remain separate review questions.

## 1. Fixed spectrum and read model

Fix a field \(\mathbb F\), with \(\beta=1\) for \(\mathbb R\) and \(\beta=2\)
for \(\mathbb C\). Let \(D=\operatorname{Diag}(a_1,\ldots,a_q)\succ0\) have
at least two distinct eigenvalues, and fix \(1\le s<q\). Define
\[
 \sum_i\frac{a_i}{a_i+t}=s,\qquad p_i=\frac{a_i}{a_i+t}.
 \tag{1}
\]
Let \(\mathcal O_D\) be its orthogonal or unitary conjugacy orbit. Set
\[
 T=\{\{i,j\}:i<j,\ a_i\ne a_j\},\quad N=|T|,\quad d=\beta N.
 \tag{2}
\]
Thus \(d\) is the real dimension of the orbit.

In a fixed basis, a legal estimator has coefficient vector \(b\) with
\(\mathbb Eb=\mathbf1\), at most \(s\) nonzero entries on every outcome, and
finite second moment. Its worst-query variance is
\[
 \lambda_{\max}\bigl(\mathbb E[D_b^*GD_b]-G\bigr).
\]
Write \(\Phi_s(G)\) for the optimum over all such laws, including complex,
subset-dependent weights. The unrestricted unbiased rank-\(s\) ideal is the
same number \(t\) throughout \(\mathcal O_D\).

Let \(\mathcal P(p)\) be the compact polytope of laws on exactly-\(s\)
subsets whose marginals are \(p\). It is nonempty by the hypersimplex
convex-hull identity. Each law \(\mu\) defines the real coefficients
\[
 c_{ij}(\mu)=\frac{\mathbb E_\mu[I_iI_j]}{p_ip_j}-1,\qquad \{i,j\}\in T.
\]
Let \(\mathcal C\subset\mathbb R^T\) be the compact set of these vectors.
Define the integer
\[
 k=\min_{c\in\mathcal C}|\operatorname{supp}c|.
 \tag{3}
\]
Only pairs from different eigenspaces count in (3). Dependence within an
eigenspace does not create first-order error under a basis perturbation.

## 2. Claims

There is a smooth local coordinate \(B\in\mathbb F^T\) for the orbit near
\(D\), with \(B=0\) at \(D\), such that
\[
 \Phi_s(G(B))-t
 \asymp \|B\|_2^2+
 \min_{c\in\mathcal C}\|B\mathbin{\circ}c\|_2.
 \tag{4}
\]
All comparisons use positive constants depending on the fixed spectrum,
dimension, and read cap, throughout a sufficiently small neighborhood.

For normalized invariant measure \(\mu_D\) on the orbit, (4) implies
\[
 \mu_D\{G:\Phi_s(G)\le t+\varepsilon\}
 =\Theta(\varepsilon^\kappa),\qquad
 \kappa=\frac{\beta(N+k)}2.
 \tag{5}
\]

Let \(K_*(\varepsilon)\) be the smallest size of a fixed transform library
such that every \(G\in\mathcal O_D\) has some library transform \(V\) with
\[
 \Phi_s(V^*GV)\le t+\varepsilon.
\]
Then, for sufficiently small positive \(\varepsilon\),
\[
 c\varepsilon^{-\kappa}
 \le K_*(\varepsilon)
 \le C\varepsilon^{-\kappa}.
 \tag{6}
\]
The upper bound can use one common, fixed subset law and its fixed HT
weights for every transform. It does not require a separately encoded
source-dependent sampling law.

Consequently, if the transform is selected solely by a fixed-length index
into such a declared library,
\[
 \lim_{\varepsilon\downarrow0}
 \frac{\lceil\log_2 K_*(\varepsilon)\rceil}
      {\log_2(1/\varepsilon)}
 =\kappa.
 \tag{7}
\]
In fact, the index length is \(\kappa\log_2(1/\varepsilon)+O(1)\).
Equation (7) concerns the transform index. The shared library and sampler,
the encoded columns, and evaluation resources remain distinct costs.

## 3. Local coordinates and the quadratic lower bound

For each cross-eigenspace pair, choose a skew-Hermitian entry
\(K_{ij}=B_{ij}/(a_j-a_i)\), with \(K_{ji}=-\overline K_{ij}\), and put
all within-eigenspace blocks of \(K\) equal to zero. Set
\[
 G(B)=e^KDe^{-K}.
\]
The derivative at zero is \([K,D]\), whose cross entries are \(B_{ij}\).
These entries span the tangent space of the orbit. The inverse function
theorem on the orbit therefore makes this a coordinate chart after
shrinking its domain. In this chart,
\[
 G_{ii}(B)=a_i+O(\|B\|^2),\quad
 G_{ij}(B)=B_{ij}+O(\|B\|^2)\quad(\{i,j\}\in T),
 \tag{8}
\]
and the remaining off-diagonal entries are \(O(\|B\|^2)\).

The quantitative rigidity inequality in the coded-basis rigidity note is
uniform on the compact orbit:
\[
 \Phi_s(G)-t\ge c_0\|\operatorname{off}G\|_F^2.
\]
Its coefficient is strictly positive because \(D\succ0\) and \(t>0\).
In the local chart this gives
\[
 \delta(B):=\Phi_s(G(B))-t\ge c_1\|B\|^2.
 \tag{9}
\]

## 4. Upper bound in the local comparison

Fix any law in \(\mathcal P(p)\) and use \(b_i=I_i/p_i\). At \(D\), its
covariance is \(tI\). Its cross-eigenspace covariance at \(G(B)\) is
\[
 Q_{ij}=G_{ij}(B)c_{ij}.
\]
All coefficients are bounded uniformly over \(\mathcal P(p)\), since
\(p_i>0\). Equation (8), including the within-eigenspace entries and
diagonal, gives
\[
 \lambda_{\max}(Q)-t
 \le C\bigl(\|B\|^2+\|B\circ c\|_2\bigr).
\]
The compact set \(\mathcal C\) attains the minimum on the right. This
proves the upper bound in (4).

## 5. Reducing arbitrary near-optimal weights to a fixed-marginal law

For \(\eta>0\), take a coefficient law whose variance is at most
\(t+\delta(B)+\eta\). Write \(r=\|B\|\), \(\delta=\delta(B)\),
\(\Delta=\delta+\eta\), and
\[
 I_i=\mathbf1_{\{b_i\ne0\}},\quad
 \theta_i=\mathbb EI_i,\quad d_i=G_{ii}(B),\quad
 \ell_i=\frac{d_i}{d_i+t+\Delta}.
\]
The near-equality argument in the local-dichotomy note gives, uniformly
for small \(B\),
\[
 \theta_i\ge\ell_i,\quad
 \sum_i(\theta_i-\ell_i)\le C\Delta,\quad
 s-\sum_i\theta_i\le C\Delta,
 \tag{10}
\]
\[
 \theta_i=p_i+O(\Delta+r^2),\qquad
 \mathbb E\left|b_i-\frac{I_i}{\theta_i}\right|^2\le C\Delta.
 \tag{11}
\]
For completeness, (10) follows from
\[
 \sum_i\frac{d_i}{d_i+t}\ge s
\]
by diagonal majorization and isospectrality, together with bounded
derivatives in the denominator. Marginal Cauchy and the diagonal
covariance bound imply \(\theta_i\ge\ell_i\). The defect in (11) equals
\(\mathbb E|b_i|^2-1/\theta_i\), bounded by
\(1/\ell_i-1/\theta_i=O(\Delta)\).

We need an actual law with marginals exactly \(p\), not just their limit.
First pad every support of size below \(s\) to size \(s\) by a fixed rule.
The probability of changing an outcome is at most
\(\mathbb E(s-\sum I_i)=O(\Delta)\). Let the padded law have marginals
\(p+e\). Then
\[
 \sum_i e_i=0,\qquad \|e\|_\infty=O(\Delta+r^2).
\]
Put \(\rho=\tfrac12\min_i\{p_i,1-p_i\}>0\). If \(h=\|e\|_\infty>0\),
the vector
\[
 z=p-\rho e/h
\]
belongs to \([0,1]^q\) and sums to \(s\); an exact-size law with marginals
\(z\) exists. Mix that law into the padded law with weight
\(h/(\rho+h)\). The resulting law \(\mu_0\) has marginals exactly \(p\),
and its total variation distance from the original indicator law is
\(O(\Delta+r^2)\). If \(e=0\), use the padded law directly.

Let \(c^0\in\mathcal C\) be the coefficients of \(\mu_0\). Bounded second
moments, Cauchy, (11), and the total variation estimate imply
\[
 \mathbb E[\overline b_i b_j]-1
 =c^0_{ij}+O(\sqrt\Delta+r^2).
 \tag{12}
\]
This estimate holds for arbitrary complex weights.

Let \(M=(t+\Delta)I-Q\succeq0\). As in the local-dichotomy proof,
\[
 0\le M_{ii}
 \le d_i(1/\ell_i-1/\theta_i)\le C\Delta.
\]
Therefore \(|Q_{ij}|=|M_{ij}|\le C\Delta\) off the diagonal. Combining
this bound with (8) and (12) gives
\[
 \min_{c\in\mathcal C}\|B\circ c\|_2
 \le \|B\circ c^0\|_2
 \le C(\Delta+r\sqrt\Delta+r^2)
 \le C'(\Delta+r^2).
 \tag{13}
\]
By (9), \(r^2\le\delta/c_1\). Thus (13) is at most
\(C''(\delta+\eta)\), with a constant uniform for small \(\eta\).
Letting \(\eta\downarrow0\), then combining with (9), proves the lower
bound in (4). No attainment assumption is needed.

## 6. A finite coordinate-support lemma

For any nonempty compact \(\mathcal C\subset\mathbb R^N\), let
\(\mathcal S=\{\operatorname{supp}c:c\in\mathcal C\}\). Then
\[
 \min_{c\in\mathcal C}\|B\circ c\|_2
 \asymp \min_{S\in\mathcal S}\|B_S\|_2.
 \tag{14}
\]
If \(0\in\mathcal C\), both sides vanish identically. Otherwise, call a
coordinate set \(Z\) feasible when some \(c\in\mathcal C\) vanishes on all
of \(Z\). For each infeasible \(Z\), compactness gives
\[
 \eta_Z=\min_{c\in\mathcal C}\max_{i\in Z}|c_i|>0.
\]
There are finitely many coordinate sets. Take \(\eta>0\) smaller than
every such \(\eta_Z\). For any \(c\), the set
\(Z(c)=\{i:|c_i|<\eta\}\) must be feasible. Choose \(c'\) vanishing there,
with support \(S\subseteq Z(c)^c\). Then
\[
 \|B\circ c\|_2\ge\eta\|B_{Z(c)^c}\|_2
 \ge\eta\|B_S\|_2
 \ge\eta\min_{S'\in\mathcal S}\|B_{S'}\|_2.
\]
The upper bound follows from boundedness of \(\mathcal C\), choosing a
representative for each of its finitely many support patterns. This
proves (14). The proof needs compactness and finitely many coordinates;
a polyhedral hypothesis is unnecessary.

## 7. Volume of acceptable bases

In a smooth orbit chart, invariant measure has a smooth positive density.
Equations (4) and (14) reduce the local sublevel volume, up to constants,
to that of
\[
 \left\{B:\|B\|^2+\min_{S\in\mathcal S}\|B_S\|\le\varepsilon\right\}.
\]
This is a finite union over \(S\). For a fixed support \(S\), its
\(\beta|S|\) real coordinates have size \(O(\varepsilon)\), and its other
\(d-\beta|S|\) coordinates have size \(O(\sqrt\varepsilon)\). Both a
containing product ball and a contained product ball have volume
\[
 \Theta\left(
 \varepsilon^{\beta|S|+(d-\beta|S|)/2}
 \right).
\]
The smallest support has size \(k\); the finite union therefore has
volume \(\Theta(\varepsilon^{(d+\beta k)/2})\).

The orbit has finitely many diagonal matrices, obtained by permuting
the fixed eigenvalues. Outside small neighborhoods of those points,
rigidity and compactness give a positive variance gap. The same local
argument applies at each point, with permuted coordinates and unchanged
\(k\). Summing their volumes proves (5).

## 8. A uniform transform library

A library transform \(V\) accepts the conjugate of the sublevel set in
(5), with the same invariant measure. Covering the orbit requires the
sum of the measures of these sets to be at least one. This proves the
lower bound in (6).

For the upper bound, fix once and for all a law in \(\mathcal P(p)\)
whose cross-eigenspace coefficient vector has support \(k\). Use its HT
weights for every codeword. The local upper proof shows that this one
law has a set of acceptable Gram matrices of invariant measure at least
\(c\varepsilon^\kappa\). The companion note
anisotropic_transform_box_cover.md proves a deterministic cover by
\(O(\varepsilon^{-\kappa})\) translates of one such anisotropic box.
Wide coordinates have scale \(\sqrt\varepsilon\), and thin coordinates
have scale \(\varepsilon\). Smooth section frames change by
\(O(\sqrt\varepsilon)\) between intersecting boxes, so they mix wide
coordinates into thin ones only at scale \(O(\varepsilon)\). Uniform
box composition and maximal packing therefore give a cover with at most
a constant times the inverse box volume. This proves the upper bound
in (6). The same note gives a regular-grid construction for a procedural
decoder.

The earlier random-cover argument gives a weaker bound and remains useful
as an independent existence check:

Its variance is uniformly Lipschitz in the Gram matrix. In fact,
\[
 Q_b(G')-Q_b(G)
 =\mathbb E[D_b^*(G'-G)D_b]-(G'-G),
\]
so its operator norm is bounded by
\[
 L\|G'-G\|,\qquad L=1+\mathbb E\|D_b\|_{\rm op}^2<\infty.
\]
The largest eigenvalue has the same Lipschitz bound.

A compact smooth \(d\)-dimensional orbit has a metric
\(\varepsilon/(4L)\)-net with at most \(C\varepsilon^{-d}\) points.
Independent Haar transforms send any fixed net point into the
\(\varepsilon/2\) acceptable set with probability at least
\(c'\varepsilon^\kappa\). For
\[
 K=C'\varepsilon^{-\kappa}\log(1/\varepsilon)
\]
with a sufficiently large constant, the union bound makes the probability
of missing any net point strictly less than one. Such a library exists.
Lipschitz continuity extends its guarantee from the net to the whole
orbit. Its logarithmic factor is absent from the deterministic cover.

Neither argument asserts that a smallest library can be found efficiently.
The regular-grid construction specifies its codewords; efficient index
selection and numerical decoding need their own resource bounds.

## 9. An exact zero-dependence criterion

Let the distinct eigenvalue blocks have sizes \(m_g\) and common marginal
probabilities \(p_g\). Then
\[
 k=0\quad\Longleftrightarrow\quad m_gp_g\in\mathbb Z
 \text{ for every block }g.
 \tag{15}
\]
For necessity, let \(N_g\) be the selected count in block \(g\). Zero
cross-block covariance gives
\(\operatorname{Cov}(N_g,N_h)=0\) for \(g\ne h\). Their sum is always
\(s\), so
\[
 0=\operatorname{Var}\Bigl(\sum_g N_g\Bigr)
   =\sum_g\operatorname{Var}N_g.
\]
Every count is constant and equal to its integral mean. For sufficiency,
sample a uniform fixed-size subset independently in each block, using
the integral count \(m_gp_g\).

When \(k>0\), computing it is a separate sampling-design problem. The
exponent theorem does not conceal that combinatorial problem as an
efficient closed formula.

## 10. Encoding and application boundary

The model represented by the theorem is executable in exact arithmetic:
for a source operator \(R\), choose one library transform \(V\), store the
columns of \(RV\), compute \(z=V^*x\) with the declared transform decoder,
read at most \(s\) selected encoded columns, and sum their weighted
contributions. The common sampler and its weights are declared globally.
The compiler selects the index; the query uses that index.

A complete resource statement must record the shared library and decoder,
their precision and evaluation cost, the common subset law, the per-atom
index, the stored encoded columns, and the size of each read unit.
Equation (7) accounts only for the index when the transform decoder uses
that index alone. It allows comparison between transform families in that
declared model. It does not replace Cassette's total description,
metadata, execution, or sequential error fields.

The finite-precision version remains unresolved here. Approximate
transforms, sampling probabilities, and arithmetic require an explicit
error and unbiasedness analysis before a byte-level implementation claim.
The theorem does not yet authorize a Q19 production certificate or a
paper closeout.

## 11. Review targets

An independent reviewer must reconstruct the arbitrary-weight reduction
in Section 5, the coordinate-support comparison, the orbit-volume
argument, and the deterministic common-sampler box cover. A separate source
comparison must determine what is original in the local comparison (4);
the volume and random-cover steps use standard geometry.

The structural values of \(k\), finite-precision realization, and total
resource accounting are the next discriminating questions. No candidate
has yet passed correctness, originality, and consequential significance
together.
