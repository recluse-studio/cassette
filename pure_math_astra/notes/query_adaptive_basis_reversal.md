# Query-dependent sampling reverses the eigenbasis comparison

Status: a proved local result in a declared real, hard-cap model, with an
independent reconstruction of the local argument. It is supporting
mathematics. Originality, the size of the possible global improvement, and
the complete Cassette resource consequence remain open.

The change of quantifiers matters. A single random linear operator must
serve all queries with one law. Here the sampler chooses a law after seeing
the query. Each chosen law still produces an unbiased answer, and every
outcome reads at most two columns.

## Model and statement

For a positive definite real 4×4 matrix G, define

\[
 \phi_G(x)=\inf\{\mathbb E[(Y-x)^TG(Y-x)]:
                  \mathbb EY=x,\ \|Y\|_0\le2\ {\rm a.s.}\},
 \quad
 \Psi_2(G)=\sup_{\|x\|_2=1}\phi_G(x).
 \tag{1}
\]

The infimum admits arbitrary support-dependent coefficient values and laws
depending on x. If a stored real matrix R has R^TR=G, the returned vector
RY is unbiased for Rx. It reads the columns in the support of Y.
Positive definiteness makes this equivalent to the mean constraint in (1);
there is no hidden use of a source nullspace.

Let D=Diag(a_1,…,a_4)>0 be nonscalar, and define

\[
 \sum_{i=1}^4\frac{a_i}{a_i+t}=2,\qquad
 p_i=\frac{a_i}{a_i+t}.
 \tag{2}
\]

Choose i with largest a_i and j with smallest a_j. Let Q_τ rotate the
i,j coordinate plane by τ, and put G_τ=Q_τ D Q_τ^T. Then

\[
 \Psi_2(D)=t,\qquad
 \Psi_2(G_\tau)\le t-c|\tau|
 \quad(0<|\tau|<\tau_0)
 \tag{3}
\]

for constants c,τ_0>0 depending on D.

Moreover, the upper bound uses a catalog of at most fourteen fixed
exactly-two-subset laws. After seeing x, the sampler chooses one catalog
law and then uses its HT coefficients. The catalog can remain fixed for
all sufficiently small τ. The same four stored columns serve every law.

The earlier rank-constrained-second-moment theorem makes t the optimum
among unbiased random rank-at-most-two linear operators with one law
independent of x. Therefore t is not a lower bound for (1). Equation (3)
also disproves eigenbasis optimality for this query-dependent class.

## The diagonal optimum and all its maximizing queries

For diagonal D, coordinatewise Cauchy gives the exact reduction

\[
 \phi_D(x)=
 \min_{\substack{0\le\theta_i\le1\\\sum_i\theta_i=2}}
 \sum_i a_i x_i^2(\theta_i^{-1}-1).
 \tag{4}
\]

Use the conventions 0/0=0 and positive/0=+∞. The lower bound follows by
putting θ_i=Pr(Y_i≠0) and applying
E Y_i²≥x_i²/θ_i. If the resulting marginals sum to less than two,
increasing some marginals cannot raise the displayed objective. Conversely,
every θ in the hypersimplex is the marginal vector of an exactly-two
subset law, and Y_i=x_i I_i/θ_i attains the bound. Indices with x_i=0
may be included with zero returned coefficient.

The feasible vector p in (2) gives φ_D(x)≤t||x||². Define

\[
 w_i=\frac{\sqrt{a_i}/(a_i+t)}
           {(\sum_\ell a_\ell/(a_\ell+t)^2)^{1/2}} .
 \tag{5}
\]

Every w_i is positive. The maximizing unit queries are exactly the
sixteen sign choices x_i=±w_i.

To prove this equality statement, if p minimizes (4), its interior
first-order conditions require all a_i x_i²/p_i² to be equal. If a
coordinate of x vanished, the corresponding derivative would be zero,
while another derivative would be strictly negative; a feasible marginal
transfer would improve the objective. Thus equality requires (5), up to
sign. Conversely, at those amplitudes Cauchy gives the matching lower
bound in (4), because sqrt(a_i)|x_i| is proportional to p_i.
The diagonal value is therefore t.

## Strict pair-inclusion freedom

For four marginals summing to two, the attainable probability z of
including i,j together is exactly

\[
 L=\max(0,p_i+p_j-1)\le z\le
 U=\min(p_i,p_j,1-p_k,1-p_\ell),
 \tag{6}
\]

where k,ℓ are the other two indices. The lower endpoint makes the
complementary pair mass z+1-p_i-p_j nonnegative. The upper endpoints
make the remaining 2×2 transport margins nonnegative; those margins
have equal total mass and hence a nonnegative transport table exists.

For the largest and smallest marginals, p_i p_j lies strictly between
L and U. Here is a direct bound for the only less immediate upper
constraint. Write the sorted marginals as α≥b≥c≥d, so α+d is the
selected pair sum. If α+d≤1, then b≤α gives

\[
 1-b-\alpha d\ge1-\alpha(1+d)\ge d^2>0 .
 \tag{7}
\]

If α+d≥1, then c≥d and the sum constraint give b≤2-α-2d, so

\[
 1-b-\alpha d
 \ge\alpha(1-d)+2d-1\ge d^2>0 .
 \tag{8}
\]

Thus αd<1-b≤1-c. The other endpoints are strict because every
marginal is in (0,1):
αd<d≤α and αd-(α+d-1)=(1-α)(1-d)>0.

Choose δ>0 with [p_i p_j-δ,p_i p_j+δ]⊂(L,U).
There are two fixed laws ν_- and ν_+ with marginals p and pair inclusion
p_i p_j-δ and p_i p_j+δ, respectively.

## Improvement near the hard diagonal queries

For a p-marginal HT law, Y_r=x_r I_r/p_r. The rotation changes only the
i,j off-diagonal entry and the corresponding two diagonal entries:

\[
 g_\tau=(G_\tau)_{ij}
       =\pm(a_i-a_j)\sin\tau\cos\tau,\qquad
 (G_\tau)_{rr}=a_r+O(\tau^2).
 \tag{9}
\]

Consequently the smaller of the exact risks of ν_- and ν_+ is

\[
 t\|x\|^2+O(\tau^2)\|x\|^2
       -\frac{2\delta}{p_i p_j}|g_\tau x_i x_j|.
 \tag{10}
\]

The constants in the quadratic term are uniform on the unit sphere.
Select ν_- when g_τ x_i x_j≥0 and ν_+ otherwise.
Since a_i≠a_j, |g_τ| is bounded below by a positive multiple of |τ|.

Fix 0<u<w_i w_j. On the portion |x_i x_j|≥u of the unit sphere,
(10) is at most t-c_1|τ| for sufficiently small nonzero τ.
That portion contains all diagonal maximizing queries.

## A finite catalog controls the other queries

This step prevents a pointwise improvement at the sixteen maximizers
from being mistaken for a uniform theorem.

Put

\[
 e_r(x)=a_r x_r^2/p_r^2,\qquad
 \Delta(x)=\max_r e_r(x)-\min_r e_r(x).
 \tag{11}
\]

The only unit vectors where Δ vanishes have amplitudes w. Hence on the
compact set |x_i x_j|≤u,

\[
 \Delta(x)\ge\Delta_0>0 .
 \tag{12}
\]

For each ordered pair k≠ℓ include in the catalog any fixed exactly-two
law with marginals

\[
 \theta^{k\ell}=p+\eta f_k-\eta f_\ell ,
 \tag{13}
\]

where f_k denotes the kth standard coordinate vector. Choose η>0 less
than half of every p_r and 1-p_r.
There are twelve ordered pairs, and all their marginal vectors are legal.

For a given x in the compact set, choose k maximizing e_k(x) and ℓ
minimizing e_ℓ(x). Differentiating the diagonal HT risk at η=0 gives
-Δ(x). Its second derivative is uniformly bounded because all marginals
stay bounded away from zero. Thus, after reducing the fixed η if needed,

\[
 \mathbb E[(Y-x)^TD(Y-x)]
 \le t-\eta\Delta_0/2 .
 \tag{14}
\]

This bound is uniform in x in that set. For every catalog law its
Euclidean second error moment is bounded uniformly on the unit sphere:

\[
 \mathbb E\|Y-x\|^2
   =\sum_r x_r^2(1/\theta_r^{k\ell}-1)\le C .
 \tag{15}
\]

Changing D to G_τ changes (14) by at most
C||G_τ-D||=O(|τ|). For small |τ| the catalog therefore gives a risk
at most t-ηΔ_0/4 on the entire complementary region.
Combining this fixed gap with (10) proves (3).

The rule can be stated explicitly: use the sign-selected p-marginal law
when |x_i x_j|≥u||x||²; otherwise use the ordered marginal-transfer
law selected by the largest and smallest values in (11). Normalize by
||x|| only for the proof. At x=0 return zero.

## What changes for the application

This construction changes one real mathematical benchmark: two-column
query-dependent sampling can attain a smaller worst-query variance than
any single unbiased random rank-two linear operator, even with positive
definite source Gram matrix. No product is precomputed, no output net is
stored, and no source-kernel relaxation is used.

All catalog laws use the same encoded-column payload. The extra objects
are at most fourteen subset probability tables, their marginal weights,
and a declared query selector. A column selected twice is not needed;
every outcome uses an exactly-two subset. Reading two columns still costs
2m scalar values for an m×4 payload before page alignment and grouping.
The basis rotation must be stored or decoded, and the query must be
transformed when the source starts in another basis.

These are exact-arithmetic mathematical counts. Finite source precision,
sampler rounding, query-selection rounding, and physical page conversion
remain separate obligations. The local gain can be small and its constants
depend on D. The proof does not show a dimension-free factor improvement
or a vanishing ratio to the fixed-operator benchmark.

## Boundaries and next question

The proof is real. For complex queries, an adversary can choose phases
with Re(g_τ conjugate(x_i)x_j)=0; the sign argument does not establish
the same strict decrease.

The exact atomic-gauge reformulation in query_adaptive_atomic_dual.md
provides the larger problem:

\[
 \inf_{Q\in O(q)} \Psi_s(QDQ^T).
 \tag{16}
\]

Its relation to t_s(D), including the best possible improvement and its
cost, remains open here. A general theorem about (16) would be substantially
stronger than this local four-coordinate separation.
