# Exact resident descriptions for orthogonal column groups

Status: a supporting structure theorem, independently reconstructed. Correctness,
originality, and significance remain separate questions. This is an ideal dense
rank-description model, not an unpriced finite-byte encoding theorem.

## Model

Partition the nonzero columns of \(A\) into \(m\) groups. Suppose
\[
A_{:j}=u_g v_j\quad(j\in g),
\]
where \(u_1,\ldots,u_m\) are orthonormal output vectors and every \(v_j\ne0\).
Thus each group is collinear, and distinct groups are orthogonal. The stored
input columns and their page addresses remain fixed.

Let \(a_j=|v_j|^2\),
\[
T_g=\sum_{j\in g}a_j,\qquad
\delta_g=(2\max_{j\in g}a_j-T_g)_+.
\]
For an arbitrary residual \(R\), delete its zero columns before defining
\[
\nu(R)=\min_{\pi>0,\ \sum\pi=1}
\lambda_{\max}\!\left(\operatorname{diag}(\|r_j\|^2/\pi_j)-R^*R\right).
\]
Set \(\nu(0)=0\). A nonzero residual with just one column has zero variance
but still requires one exact fresh column access.

For \(0\le k<m\), define the best dense rank-\(k\) description value
\[
d_k(A)=\min_{\operatorname{rank}B\le k}\nu(A-B),\qquad d=m-k.
\]

## Projection reduction

For any positive-semidefinite Gram increment \(H\),
\[
\operatorname{diag}(H_{jj}/\pi_j)-H\succeq0,
\]
by weighted Cauchy--Schwarz with \(\sum\pi_j=1\).
Consequently \(G_1\preceq G_2\) implies \(\nu(G_1)\le\nu(G_2)\).

First project a proposed description \(B\) into the column span of \(A\).
This does not increase rank or residual Gram. Then let \(P\) project onto
the range of that description. The decomposition
\[
A-B=(I-P)A+(PA-B)
\]
is output-orthogonal, so its Gram is at least \(A^*(I-P)A\).
Replacing \(B\) by \(PA\) cannot increase \(\nu\).
Enlarging \(P\) to rank \(k\) inside the span of \(A\) also cannot hurt.

It follows that the minimum can be taken over rank-\(k\) orthogonal
projections in the \(m\)-dimensional span of the \(u_g\).
This compact set also supplies attainment. Continuity of \(\nu\), including
zero columns, follows from its compact density-matrix dual; the square-root
terms in that dual are continuous.

Write \(W=I-P\) in the orthonormal \(u_g\) basis. Then \(W\) is a rank-\(d\)
projection. Its diagonal satisfies
\[
0\le w_g\le1,\qquad \sum_g w_g=d.                              \tag{1}
\]
The residual's principal Gram block on group \(g\) is \(w_g v_gv_g^*\).
Mixed projections may create cross-group residual correlations, but those
do not invalidate any principal-block covariance constraint.

## A mass bound that is concave in the projection diagonal

At a fixed threshold \(t>0\), the rank-one mass lemma from
prescribed_energy_rank.md implies that the total sampling mass \(P_g\)
on group \(g\) must satisfy
\[
P_g\ge \rho_g(w_g;t)
:=\frac{w_gT_g}{t}
-\frac{w_g^2\delta_g^2}{t(t+w_gT_g)}.                          \tag{2}
\]
At \(w_g=0\), the right side is zero. This is a necessary condition for
any residual covariance at most \(tI\), since its principal block must
also be at most \(tI\).

For each \(g\),
\[
\frac{\partial^2}{\partial w^2}\rho_g(w;t)
=-\frac{2\delta_g^2t}{(t+wT_g)^3}\le0.                         \tag{3}
\]
Thus \(\sum_g\rho_g(w_g;t)\) is concave on the hypersimplex (1).
Its minimum occurs at a vertex, where exactly \(d\) coordinates equal one.
Summing (2) therefore gives
\[
1\ge \min_{\substack{S\subseteq[m]\\|S|=d}}
\sum_{g\in S}\rho_g(1;t).                                     \tag{4}
\]

Conversely, if a set \(S\) satisfies the inequality in (4), capture all
groups outside \(S\) in \(B\). This is a rank-\(k\) description.
The residual groups are orthogonal, so the exact rank-one allocations
from the mass lemma give covariance at most \(tI\) at their stated mass.
If the total mass is less than one, distribute the surplus over active
coordinates; increasing these masses decreases the diagonal loading.
Hence (4) is sufficient as well as necessary.

The same lower bound applies to the full fractional relaxation
\(0\preceq W\preceq I,\operatorname{tr}W=d\). This relaxation is exact for
this class of source matrices after probabilities are optimized.

## Exact selection law

An optimum can always be chosen to capture whole groups. For each \(t>0\),
compute
\[
r_g(t)=\frac{T_g}{t}
-\frac{\delta_g^2}{t(t+T_g)}.
\]
Let \(L_d(t)\) be the sum of the \(d\) smallest values among \(r_1(t),\ldots,r_m(t)\).
Then
\[
d_k(A)\le t\quad\Longleftrightarrow\quad L_d(t)\le1.             \tag{5}
\]
The retained set may change as \(t\) changes. Ranking groups only by
Frobenius energy \(T_g\) generally gives the wrong description.

Each \(r_g(t)\) strictly decreases. If the optimum is positive, it is
the unique root of \(L_d(t)=1\). If \(d=1\) and a singleton group is
available, the optimum is zero: retain that one column and capture the
others. For \(d\ge2\), the optimum is positive. If \(k\ge m\), take \(B=A\)
and no residual access.

This proves existence of a group-diagonal optimum. It does not say every
optimum is group-diagonal: balanced groups have \(\delta_g=0\), making
(3) non-strict and allowing equality degeneracies.

## An exact phase transition and approximation obstruction

Take
\[
A=[\sqrt a\,e_1,\ \sqrt a\,e_2,\ \sqrt b\,e_3,\ \sqrt b\,e_3],
\qquad a,b>0,\qquad k=1.
\]
Capturing \(e_3\) leaves two orthogonal singleton columns and has variance
\(a\). Capturing \(e_1\) or \(e_2\) leaves one singleton of energy \(a\)
and one balanced rank-one group of total energy \(2b\). Its variance
\(t_b\) solves
\[
\frac{a}{t_b+a}+\frac{2b}{t_b}=1,
\qquad t_b=b+\sqrt{b^2+2ab}.
\]
The general theorem therefore gives the exact value
\[
d_1(A)=\min\{a,\ b+\sqrt{b^2+2ab}\}.                           \tag{6}
\]
The best description changes at \(b=a/4\). Real diagonal projections
attain the values, and the lower bound also holds for complex descriptions.

For \(a/4<b<a/2\), the weighted-SVD envelope minimizer described in
dense_description_surrogate.md captures one singleton direction.
To verify that choice directly, target a singleton with weight parameter
\(0<s\le1\). Its weighted row energies are \(as,a/s,2b/s\).
The top row energy is \(a/s\), so the squared rank-one tail is
\[
as+2b/s,
\]
minimized at \(s=\sqrt{2b/a}\), with value \(2\sqrt{2ab}\).
If the target is a duplicated column instead, the row energies are
\(a/s,a/s,b(s+s^{-1})\); the minimum tail is \(a+2b\), attained at \(s=1\).
The first choice is strictly better because
\[
(a+2b)^2-8ab=(a-2b)^2>0.
\]

Thus the envelope minimizer has exact variance \(t_b\), while the true
optimum is \(a\). Its exact approximation ratio is
\[
\frac{b+\sqrt{b^2+2ab}}{a},
\]
which tends to \(\varphi=(1+\sqrt5)/2\) as \(b\uparrow a/2\).
This family initially suggested testing a universal golden-ratio bound.
That conjecture has since failed: the sharp factor is two, as shown next.

For \(0<\epsilon<1/2\), use three orthogonal groups with energies
\(1\), \(\epsilon^2\), and the duplicate pair
\(x,x\), where \(x=\epsilon(1-\epsilon)\). Keep rank budget one.
Capturing the duplicate direction leaves two orthogonal singleton columns
and gives exact optimum \(\epsilon\). Every residual containing the
duplicate group has variance at least \(2x>\epsilon\), so the group
selection theorem proves this is the global optimum.

The surrogate instead captures the energy-one direction: its remaining
energies \(\epsilon^2,x,x\) are balanced and have envelope
\(2\epsilon-\epsilon^2<2\epsilon\), whereas the optimal description's
envelope is \(2\epsilon\). The third possible retained pair has envelope
\(2\sqrt{2x}>2\epsilon\). The choice is strict. Its exact variance is
\[
t_\epsilon=x+\sqrt{x^2+2x\epsilon^2}
=\epsilon\bigl(1-\epsilon+\sqrt{1-\epsilon^2}\bigr).
\]
Thus its achieved-variance ratio is
\(1-\epsilon+\sqrt{1-\epsilon^2}\to2\).
The general factor-two approximation guarantee is sharp even in this
orthogonal group class. This closes the golden-ratio conjecture.

## Application boundary

The description above is a legitimate dense rank-\(k\) factorization in
the same scalar model as MATHS.md Corollary 5.1. It preserves the original
input coordinates and reconstructs a sampled original column before
forming its residual. A dense factor payload and exact sampling table
must still be priced in the declared encoding.

The structure theorem applies when the source atom has the stated
orthogonal rank-one column groups. No general source matrix is assumed
to have them. A perturbation theorem, a broader attainable class, or a
different substantial consequence is needed before treating this special
case as the requested advance. Originality has not been established.

## Stability boundary: absorbable perturbations versus new residual rays

There is no general relative perturbation theorem for \(\nu\), even if the
unperturbed structured residual has zero variance. The obstruction is sharp at
the one-column endpoint. Let

\[
 R_0=[M e_1,\ 0],\qquad F=[0,\ \varepsilon e_2],\qquad M,\varepsilon>0.
\tag{7}
\]

Both \(R_0\) and \(F\) have only one nonzero column and hence have variance
zero. Their sum has orthogonal Gram matrix
\(\operatorname{diag}(M^2,\varepsilon^2)\). Writing
\(\pi_1=p\), its covariance eigenvalues are

\[
 M^2\frac{1-p}{p},\qquad \varepsilon^2\frac p{1-p}.
\]

They are equal at \(p=M/(M+\varepsilon)\), which proves

\[
 \nu(R_0+F)=M\varepsilon.                                    \tag{8}
\]

Thus \(\|F\|_F=\varepsilon\), but the variance change is linear in
\(\varepsilon\) with coefficient \(M\), rather than quadratic in the
perturbation. In particular, no universal bound of the form

\[
 \nu(R+F)\leq C\bigl(\nu(R)+\nu(F)+\|F\|_F^2\bigr)
\tag{9}
\]

can hold. No multiplicative estimate relative to \(\nu(R_0)\) can hold
either. Equation (8) shows that a leading residual-column scale is necessary
whenever a perturbation creates a new orthogonal residual ray. The usual
Frobenius continuity estimate has the correct first-order dependence in this
regime, up to its constant and its choice of leading scale.

There is, however, a precise relative regime that preserves the one-column
access model. If \(D\) is an invertible diagonal matrix, then for every
sampling law \(\pi\),

\[
 Q_\pi(RD)=D^*Q_\pi(R)D.
\tag{10}
\]

Consequently,

\[
 \bigl(\min_j|D_{jj}|\bigr)^2\nu(R)
 \leq \nu(RD) \leq
 \bigl(\max_j|D_{jj}|\bigr)^2\nu(R).                         \tag{11}
\]

For the upper inequality, use a minimizing law for \(R\) in (10) and the
operator norm of \(D\). For the lower inequality, apply the upper inequality
to \(RD\) and \(D^{-1}\). This proof works over both fields, allows phases,
and does not relabel or mix input coordinates.

The structured theorem therefore has the following usable, but conditional,
extension. Let \(P\) be a group-selecting rank-\(k\) projection that is
optimal for a structured \(A_0\), and let \(R_0=(I-P)A_0\). For an arbitrary
new source atom \(A\), suppose that its unrepresented part satisfies

\[
 (I-P)A=R_0D                                                     \tag{12}
\]

for a diagonal \(D\). The represented part \(PA\) is otherwise unrestricted.
Taking \(B=PA\) gives the actual residual \(R_0D\), so it is a legal
rank-\(k\) resident description without any coordinate or page change. If
\(1-\eta\leq|D_{jj}|\leq1+\eta\), then its certified variance obeys

\[
 \nu(A-B)\leq(1+\eta)^2d_k(A_0),                              \tag{13}
\]

and also has the lower comparison in (11) to the structured residual value.
All perturbation energy inside the captured range is absorbed exactly; only
leakage into a new residual ray matters. When (12) holds, the residual remains
in the orthogonal rank-one group class, so the exact selection law above may
be recomputed using the rescaled group energies rather than merely bounded.

Condition (12) is also close to necessary at the zero-variance endpoint:
zero variance requires the residual to have at most one nonzero column, and
(8) shows why an arbitrarily small new independent residual ray destroys that
property at first order. This does not give a broad near-structured theorem.
It identifies the exact structural condition under which the group solution is
stable relatively, and the sharp obstruction outside it.
