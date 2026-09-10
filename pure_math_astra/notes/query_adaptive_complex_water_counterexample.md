# A complex query-adaptive counterexample to the general spectral water lower bound

Status: proved, with two independent correctness reconstructions recorded in
query_adaptive_complex_water_counterexample_review.md and
query_adaptive_equicorrelation_counterexample_review.md.
This is an obstruction to a proposed research route, not a novelty or
significance claim. It does not resolve the two-high, two-low spectral family.

Let G_eta = 11* + eta I_4, where eta > 0 and 1 has four entries equal to one.
Queries, estimators, and polar vectors may be complex; G_eta is real. The
query-adaptive value retains E Y = x and the hard bound ||Y||_0 <= 2.

The claim is that, for all sufficiently small positive eta,

\[
 \Psi_{2,\mathbb C}(G_\eta)\le {1999\over1000}\eta
 < t_2(G_\eta),
 \qquad
 t_2(G_\eta)=\sqrt{1+4\eta+\eta^2}-1.
 \tag{1}
\]

The threshold in eta is not made explicit. The proof supplies existence
by a sequential compactness argument with a strict limiting gap. The
constant 1999/1000 is deliberately loose.

## 1. Exact finite-eta criterion

The atomic dual established in query_adaptive_atomic_dual.md and the exact
inversion in query_adaptive_equicorrelation_counterexample_audit.md give
the following criterion. A polar vector z consists of four complex points
satisfying

\[
 |z_i-z_j|^2+\eta(|z_i|^2+|z_j|^2)\le\eta(2+\eta)
 \quad(i<j).
 \tag{2}
\]

Write a = (sum_i z_i)/4, A = |a|^2, and W = sum_i |z_i-a|^2.
For k = 1+c, the required containment at variance c eta is exactly

\[
 {W\over k\eta}+{4A\over4+k\eta}\le1
 \quad\text{for every vector satisfying (2).}
 \tag{3}
\]

This criterion includes every query. It does not replace the coordinate
mean constraint with a weaker output mean constraint at eta = 0.
The pair constraints imply the singleton constraints: minimizing a pair's
positive quadratic form over its other coordinate gives |z_i|^2/G_ii.
Thus listing the six pairs is exact for the at-most-two-coordinate cap.

## 2. An elementary planar diameter estimate

For four complex points q_i with mean zero, let V = sum_i |q_i|^2 and
let d be their diameter. Then

\[
 V\le {4\over3}d^2.
 \tag{4}
\]

Here is a proof of the planar disk estimate used in (4). A smallest
enclosing disk has either two antipodal boundary points or three boundary
points whose triangle contains the center. Otherwise its center can move
toward the boundary points and its radius can decrease. In the first case
its radius is at most d/2. In the second, the three central arcs are each
at most pi and sum to 2 pi, so at least one arc is at least 2 pi/3. Its
chord has length at least sqrt(3) times the radius. Thus the radius is at
most d/sqrt(3). If b is the center of this disk, the zero mean gives
sum_i |q_i|^2 <= sum_i |q_i-b|^2 <= 4d^2/3. The same estimate applies
after subtracting the mean of any four points.

Also, for a zero-mean quadruple,

\[
 |q_i+q_j|\le\sqrt V.
 \tag{5}
\]

Indeed, the other two points sum to minus this pair sum. Applying
|u|^2+|v|^2 >= |u+v|^2/2 to both pairs proves (5).

## 3. A strict bound for the limiting constant-vector boundary

For a zero-mean complex quadruple q, define

\[
 H=\max_{i<j}\bigl(|q_i-q_j|^2+2\operatorname{Re}(q_i+q_j)\bigr).
 \tag{6}
\]

Summing over the six pairs, and separately applying (4)-(5) to a
diameter pair, gives the two bounds

\[
 H\ge {2V\over3},
 \qquad H\ge {3V\over4}-2\sqrt V.
 \tag{7}
\]

Suppose w_i = m+q_i satisfies the boundary inequalities

\[
 |w_i-w_j|^2+2\operatorname{Re}(w_i+w_j)\le1.
 \tag{8}
\]

Then 4 Re(m)+H <= 1. The coefficient of eta in (3), minus one, for
z_i = 1+eta w_i is

\[
 B_c(w)=2\operatorname{Re}m-{1+c\over4}+{V\over1+c}.
 \tag{9}
\]

Using the largest permissible Re(m), the relevant root of B_c = 0
is bounded by

\[
 C(q)=\sqrt{(1-H)^2+4V}-H.
 \tag{10}
\]

More precisely, (10) is the root obtained with 4 Re(m)=1-H. Any larger
c with 1+c > 0 gives B_c(w) < 0. Increasing c decreases (9) by at least
one quarter of the increment.

We now bound (10) uniformly below 2. For fixed V, its right side is
nonincreasing in H. If 0 <= V <= 1024, the first bound in (7) yields

\[
 C(q)\le\sqrt{1+{8V\over3}+{4V^2\over9}}-{2V\over3}
 \le 2-{9\over4108}=:c_b.
 \tag{11}
\]

To check the last inequality, put L = 2V/3. The difference between 2
and the preceding expression equals
3/(2+L+sqrt(L^2+4L+1)). Its denominator is at most 4+2L, which is at
most 4108/3 on this interval.

If V >= 1024, the second bound in (7) gives H >= 11V/16. Put h = 11V/16
and d = 21/11. Then 2h(d+1)=4V and d^2>1, so
(h+d)^2-((h-1)^2+4V)=d^2-1>0. Both quantities being squared are
nonnegative. This proves

\[
 C(q)\le {21\over11}<1.911<c_b.
 \tag{12}
\]

Thus every boundary vector (8) satisfies B_c(w) < 0 for c > c_b. In
particular this holds at c = 1999/1000. The gap is uniform: by (9),
B_c(w) <= -(c-c_b)/4.

## 4. The finite-eta passage

Fix c = 1999/1000 and k = 1+c. Suppose, contrary to (1), that a sequence
eta -> 0 has polar vectors violating (3). A common complex phase preserves
all constraints and the ellipsoid value, so arrange a >= 0. Put D = 1-A.

Summing (2) gives

\[
 (4+3\eta)W+12\eta A\le12\eta+6\eta^2.
 \tag{13}
\]

In particular A <= 1+eta/2, so D >= -eta/2 and a is bounded.

For w_i = z_i-a, equation (5) gives |w_i+w_j| <= sqrt(W). Therefore
|z_i|^2+|z_j|^2 >= 2A-2a sqrt(W). Applying (2) to a diameter pair,
then (4), yields

\[
 W\le {8\over3}\eta D+{4\over3}\eta^2
          +{8\over3}\eta a\sqrt W.
 \tag{14}
\]

Every sequence has a subsequence of one of the following two types.

First, suppose D/eta -> +infinity. Dividing (14) by eta D and solving
the resulting quadratic bound on sqrt(W/(eta D)) gives

\[
 \limsup {W\over\eta D}\le {8\over3}.
 \tag{15}
\]

The excess of the left side of (3) over one is at most
-D+W/(k eta). Since k > 8/3, (15) makes that excess negative eventually,
a contradiction.

Second, suppose D/eta is bounded above. Its lower bound is -1/2.
Equation (14), as a quadratic inequality in sqrt(W), now implies
W = O(eta^2). Also a-1 = -D/(a+1) = O(eta). Consequently the four
points u_i = (z_i-1)/eta remain bounded. Pass to a convergent subsequence
u -> u_0. Expanding (2), dividing by eta^2, and taking the limit gives
exactly (8) for u_0. Expanding the excess in (3), dividing by eta, and
taking the limit gives B_c(u_0). Section 3 makes this limit strictly
negative, again contradicting a violation.

The contradiction proves (3) for all sufficiently small eta. Finally,
t_2(G_eta)/eta -> 2 > 1999/1000, which proves the strict comparison in (1).

## 5. Consequence and boundary of the result

The proposed universal inequality Psi_complex(G) >= t_2(G) is false.
Allowing complex
queries does not restore that benchmark for every real positive Gram
matrix. The real adaptive value is no larger than the complex value, so
the same upper bound also holds for real queries.

The spectrum here has one large eigenvalue and three small eigenvalues.
This counterexample does not settle the family with two eigenvalues equal
to one and two equal to eta. It supplies no finite-word sampler, page
bound, or accepted original advance for Cassette. The proof uses the
classical planar enclosing-disk estimate, which is established geometry.

## 6. Consequence for the proposed rank-two SDP certificate

Let K_S = E_S G_SS^{-1} E_S^T and t = t_2(G_eta). For any positive
semidefinite real X of rank at most two satisfying tr(K_S X) <= 1,
write X = aa^T+bb^T and z = a+ib. The proved containment at c eta gives
tr((G_eta+c eta I)^{-1}X) <= 1. Since t > c eta for small eta,

\[
 \operatorname{tr}((G_\eta+tI)^{-1}X)
 \le {4+(1+c)\eta\over4+\eta+t}<1.
 \tag{16}
\]

The matrix comparison behind this inequality follows by checking the two
eigenvalues: the ratio (lambda+c eta)/(lambda+t) increases with lambda,
whose largest value is 4+eta.

By contrast, X=G_eta/2 satisfies all six pair equalities and has objective
one. Consequently the universal rank-two objective certificate proposed in
query_adaptive_rank_two_spectrahedron.md cannot hold, even for this family
of pair-principal-inverse forms. This conclusion does not assert that the
rank-two feasible set is empty; it gives an explicit strict upper bound
on its objective.

## Source boundary for the planar geometry

The disk estimate in Section 2 is the planar case of Jung's enclosing-ball
theorem. The bibliographic record checked during this calculation is
Heinrich Jung, Ueber die kleinste Kugel, die eine raeumliche Figur
einschliesst, Journal fuer die reine und angewandte Mathematik 123 (1901),
241-257, [EuDML record](https://eudml.org/doc/149122).
The record was retrieved through search; a direct full-page fetch timed
out. The original article has not been read in this check. Section 2 gives
the elementary planar proof needed here. This bibliographic check is not
an originality assessment of the present sampling statement.
