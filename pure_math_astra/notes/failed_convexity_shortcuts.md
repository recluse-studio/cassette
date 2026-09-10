# Failed convexity shortcuts

These counterexamples preserve failed approaches. They do not prove the research
questions impossible, and they do not establish originality of another route.

## Expected-cost intensity variables

For iid sampling, let \(c_i>0\) be page costs, let
\(m=\sum_i c_i\pi_i\), and put \(w_i=\pi_i/m\).
Then \(\sum_i c_iw_i=1\), \(W=\sum_iw_i=1/m\), and the expected-cost-normalized
covariance is
\[
mQ_\pi(G)=\operatorname{diag}(a_i/w_i)-G/W.                    \tag{1}
\]
This is an asymptotic expected-cost model. It is not a guarantee that every
realized sample path fits a fixed total byte cap.

The scalar largest-eigenvalue objective in (1) is not convex on the physical
affine slice. Take
\[
G=\begin{pmatrix}1/100&1\\1&100\end{pmatrix},\qquad
c=(1,3),\qquad w(x)=(x,(1-x)/3),\quad 0<x<1.
\]
The covariance in (1) is positive semidefinite of rank one, so its largest
eigenvalue is its trace:
\[
f(x)=\frac{1-x}{100x(1+2x)}
+\frac{900x}{(1-x)(1+2x)}.
\]
At \(x_-=1/25\), \(x_0=9/200=(x_-+x_+)/2\), and \(x_+=1/20\),
\[
f(x_-)=629/18,\quad
f(x_0)=7326481/187371,\quad
f(x_+)=90361/2090.
\]
Exact rational subtraction gives
\[
f(x_0)-\frac{f(x_-)+f(x_+)}2
=\frac{512603}{43511710}>0.
\]
Thus the homogenization does not supply a convex optimal-design problem.
An earlier reconstruction expressed the two-by-two eigenvalues with radicals;
the rank-one determinant identity simplifies them to these rational values.

## Fractional residual projections at a fixed sampling law

Let \(A=I_q\), let the law be uniform, and consider residual projections of
rank \(d\), where \(1\le d<q\). For a projection \(W\),
\[
Q=q\operatorname{diag}(W)-W.
\]
Relax the projection to \(0\preceq W\preceq I,\operatorname{tr}W=d\).
Every feasible matrix has \(\operatorname{tr}Q=(q-1)d\), so the relaxed
objective is at least \(d(q-1)/q\). The fractional matrix \(W=(d/q)I\)
attains that value.

No rank-\(d\) projection attains it. Equality in the trace bound forces
\(Q=d(q-1)I/q\). Its off-diagonal entries force \(W\) to be diagonal,
and its diagonal entries force every entry of \(W\) to be \(d/q\).
That is not a projection. Compactness of the rank-\(d\) Grassmannian
gives a strict gap.

This does not produce a gap after optimizing the sampling law. With the
zero-column extension of \(\nu\), a coordinate projection has variance
\(d-1\), and the fractional relaxation cannot improve it. For \(d\ge2\),
write \(w_i=W_{ii}\in[0,1]\), \(\sum_iw_i=d\). The diagonal covariance
constraints at threshold \(t\) imply
\[
1\ge\sum_i\frac{w_i}{w_i+t}.
\]
The sum is concave on the diagonal hypersimplex, and its minimum at a
vertex is \(d/(1+t)\). Hence \(t\ge d-1\), attained by a coordinate
projection. For \(d=1\), both optima are zero.

Therefore a fixed-law integrality gap cannot stand in for a joint
description-and-law gap. The latter question remains open here.

## The first-order spectral rule is not a global solution

At a jointly stationary residual projection and law, a common top-eigenspace
density \(X\) gives the operator
\[
K=A\operatorname{diag}(X_{ii}/\pi_i)A^*-AXA^*.
\]
Projection variations give an invariant-subspace condition. They do not
justify replacing the projection by a globally lowest eigenspace of a
fixed \(K\): changing the projection also changes the optimal law and
spectral density. The terms \(w/\pi\) in the joint payoff are not jointly
convex. A minimax exchange requires a separate argument.

## Hard-cap omission probabilities

The all-but-one covariance and its distinct matrix-convexity obstruction
are in resident_description_and_pages.md. That note has not proved
nonconvexity of its scalar largest-eigenvalue objective. The preceding
expected-cost scalar counterexample applies to a different model and
must not be imported into that question.

