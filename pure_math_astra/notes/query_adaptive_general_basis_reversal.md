# Eigenbases and real query-dependent sampling at intermediate read caps

Status: generalization of query_adaptive_basis_reversal.md. The earlier
note proves the four-coordinate case with fourteen laws. This note covers
every dimension and intermediate cap with q+2 laws. The mathematical
statement, originality, and global application significance remain separate
questions.

## Theorem

Fix q≥4 and 2≤s≤q−2. For a positive definite real matrix G, define

\[
 \phi_G(x)=\inf_{\mathbb EY=x,\ \|Y\|_0\le s}
          \mathbb E[(Y-x)^TG(Y-x)],\qquad
 \Psi_s(G)=\sup_{\|x\|=1}\phi_G(x).
 \tag{1}
\]

The support bound holds on every outcome, and the law may depend on x.
Let D=Diag(a_1,…,a_q)>0 be nonscalar, and set

\[
 \sum_i\frac{a_i}{a_i+t}=s,\qquad p_i=\frac{a_i}{a_i+t}.
 \tag{2}
\]

Let Q_τ rotate the coordinate plane joining an index of largest a_i and
an index of smallest a_j. Then there exist c,τ_0>0 such that

\[
 \Psi_s(D)=t,\qquad
 \Psi_s(Q_\tau DQ_\tau^T)\le t-c|\tau|
 \quad(0<|\tau|<\tau_0).
 \tag{3}
\]

At most q+2 fixed HT subset laws, selected using the query, give the
upper bound. The laws can remain fixed throughout this τ interval.
They use one common encoded-column payload and exactly s selected columns.

Thus every nonscalar real eigenbasis fails to minimize this worst-query
variance at every intermediate cap. The quantity t remains the optimum
for a single unbiased random rank-at-most-s operator whose law is fixed
before seeing x. That different quantifier prevents it from lower-bounding
(1).

## Exact attainable interval for one pair

Fix interior marginals p with sum s and a pair i,j. Let T be the sum of
the largest s−1 marginals outside that pair. The attainable pair-inclusion
probability z is exactly the interval

\[
 \max(0,p_i+p_j-1)\le z\le
 \min(p_i,p_j,s-1-T).
 \tag{4}
\]

To prove sufficiency, as well as necessity, condition on including both,
exactly one, or neither of i,j. The remaining count is s−2, s−1, or s,
with probabilities z, p_i+p_j−2z, and 1-p_i-p_j+z. Consequently the
remaining marginal vector must lie in the weighted Minkowski sum of the
three corresponding hypersimplices.

For k remaining coordinates its maximum coordinate sum in that sum is

\[
 F(k)=z\min(k,s-2)+(p_i+p_j-2z)\min(k,s-1)
                  +(1-p_i-p_j+z)\min(k,s).
 \tag{5}
\]

All subset inequalities with these upper bounds, together with the fixed
total, suffice. Indeed, order the coordinates of any real linear
functional. Express its weights as a constant plus nonnegative differences
times prefix indicators. The subset inequalities bound that functional by
the same support function as the Minkowski sum: each hypersimplex attains
its maximum by selecting the required number of largest weights.
Separation of compact convex sets proves membership.

When k≤s−2, the inequalities follow from p_r≤1. When k≥s, they follow
from nonnegativity and the fixed total s-p_i-p_j. The only additional
size is k=s−1, for which F(k)=s−1−z. This yields z≤s−1−T.
The other bounds in (4) give nonnegative probabilities for all four
pair statuses. A conditional remaining-subset law for the exactly-one
category can be used for either of its two statuses, with respective
probabilities p_i-z and p_j-z. Thus all original marginals are realized.

For the largest and smallest marginals α=max p and d=min p, their
product lies strictly inside (4). Let C be the sum of the remaining
q−s−1 marginals after the largest s−1 outside entries are removed.
This set is nonempty. Put u_0=1−α. Since every remaining marginal
is at least d and T≤(s−1)α,

\[
 C\ge d,\qquad C=s-\alpha-d-T
       \ge s(1-\alpha)-d\ge2u_0-d.
 \tag{6}
\]

Hence C≥max(d,2u_0-d)≥u_0, and therefore

\[
 s-1-T-\alpha d=C-u_0(1-d)\ge u_0d>0.
 \tag{7}
\]

The other upper bounds are strict because αd<d≤α. The lower bounds
are strict because αd>0 and
αd-(α+d-1)=(1-α)(1-d)>0.

Choose δ>0 so that p_i p_j±δ both lie inside (4). Two fixed
exactly-s laws ν_-,ν_+ realize those pair probabilities while retaining
all marginals p.

## Diagonal value and its equality set

Coordinatewise Cauchy and the hypersimplex identity give

\[
 \phi_D(x)=
 \min_{\substack{0\le\theta_r\le1\\\sum_r\theta_r=s}}
       \sum_r a_r x_r^2(\theta_r^{-1}-1).
 \tag{8}
\]

The conventions are 0/0=0 and positive/0=+∞. Marginals summing to less
than s may be increased without raising the objective. An exactly-s
law with the resulting marginals and coefficients x_r I_r/θ_r attains
the displayed value.

Using θ=p gives φ_D(x)≤t||x||². On the unit sphere equality holds
exactly when

\[
 |x_r|=w_r,\qquad
 w_r=\frac{\sqrt{a_r}/(a_r+t)}
            {(\sum_\ell a_\ell/(a_\ell+t)^2)^{1/2}} .
 \tag{9}
\]

For necessity, p is interior, so its minimizing first-order conditions
require all a_r x_r²/p_r² to be equal. A zero x coordinate would allow
a strictly improving marginal transfer, since another coordinate is
nonzero. These conditions give (9). Conversely, Cauchy attains equality
there, because sqrt(a_r)|x_r| is proportional to p_r. Thus Ψ_s(D)=t,
and its maximizing unit queries are the 2^q real sign choices of w.

## Two laws near the diagonal maximizers

Write G_τ=Q_τ DQ_τ^T. Its only off-diagonal entries are the selected pair,
with g_τ=±(a_i-a_j)sinτ cosτ; its diagonal changes are O(τ²).
The smaller risk of the p-marginal laws ν_- and ν_+ is therefore

\[
 t\|x\|^2+O(\tau^2)\|x\|^2
       -\frac{2\delta}{p_i p_j}|g_\tau x_i x_j|.
 \tag{10}
\]

Select the pair probability below p_i p_j when g_τ x_i x_j≥0, and
the one above it otherwise. Fix 0<u<w_i w_j. On |x_i x_j|≥u
on the unit sphere, (10) is at most t-c_1|τ| for small nonzero τ.
The eigenvalues at i,j differ because D is nonscalar.

## q further laws away from those maximizers

Define

\[
 e_r(x)=a_r x_r^2/p_r^2,\qquad
 \Delta(x)=\max_r e_r(x)-\min_r e_r(x).
 \tag{11}
\]

The only unit vectors with Δ=0 have amplitudes w. The compact region
|x_i x_j|≤u therefore has Δ≥Δ_0>0.

For each k, choose one fixed exactly-s law with marginals

\[
 \theta^k=p+\eta(f_k-q^{-1}\mathbf1),
 \tag{12}
\]

where f_k is a standard coordinate vector. Choose fixed η>0 small
enough that every marginal remains strictly between zero and one.
For any x in that compact region, take k maximizing e_k(x). The
derivative at η=0 of the diagonal HT risk is

\[
 -e_k(x)+q^{-1}\sum_r e_r(x)\le-\Delta_0/q.
 \tag{13}
\]

The second derivative is uniformly bounded because all θ^k stay away
from zero. Reducing η if necessary makes the diagonal risk at most
t-ηΔ_0/(2q), uniformly on the region.

For each of these laws,
E||Y-x||²=sum_r x_r²(1/θ_r^k-1) is uniformly bounded on the unit sphere.
Changing D to G_τ therefore changes the risk by O(|τ|), uniformly in x
and k. For small |τ| a gap of ηΔ_0/(4q) remains.
Together with (10) this proves (3), using q+2 fixed laws.

The selector is explicit. If |x_i x_j|≥u||x||², use the appropriate
pair-probability law according to the sign in (10). Otherwise choose
k maximizing a_k x_k²/p_k² and use θ^k. At x=0 return zero.
The selector uses O(q) scalar arithmetic and comparisons.

## Finite representation of the catalog

The q transfer laws need not be stored as q full tables. Each marginal
vector (12) is determined by p,η,k. One exact fixed-size construction
uses a uniform shift U∈[0,1): form cumulative marginal sums, and include
coordinate r if its interval contains one of U,U+1,…,U+s−1. Intervals
have length at most one and the total is s, so exactly s distinct
coordinates are selected, with the required marginals. Half-open intervals
fix endpoint conventions.

For ν_- and ν_+, the moment vector (p,z) lies in a convex hull of
affine dimension at most q: the marginal sum fixes one of q marginal
dimensions, and z adds one. Each law can therefore use at most q+1
subset outcomes by the finite-dimensional convex-hull theorem. A source
representation stores two lists of at most q+1 subsets, their
probabilities, p,η,u, and the chosen rotation. Subset identities cost
O(qs log q) bits; the scalar probabilities and parameters remain separately
represented. This is an existence bound for the compiler's finite output,
not a bound on the effort required to find it.

All laws read the same encoded payload. An m×q source still needs its
mq encoded scalars and reads ms scalar values per query before page
grouping. The query transform and finite arithmetic require their own
accounts. The theorem lowers the exact worst-query variance while holding
that column count fixed; it does not by itself reduce stored source bytes.

## Remaining mathematical question

The proof is real. Continuous complex phases can make the real part of the
selected cross term vanish, so the argument does not give (3) there.
The endpoint caps s=1 and s=q−1 lack the strict pair-inclusion freedom
used in (4)–(7).

The result is local, with constants depending on D,q,s. It does not
establish a uniform factor or a different asymptotic error rate.
The harder problem is to determine

\[
 \inf_{Q\in O(q)}\Psi_s(QDQ^T)
 \tag{14}
\]

and compare it sharply with t_s(D), with a declared sampler and its costs.
The current four-coordinate stress case has spectrum (1,1,η,η) and
t=√η. Whether the infimum in (14) can be o(√η) remains unresolved.
