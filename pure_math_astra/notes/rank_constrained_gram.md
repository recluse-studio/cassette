# Rank-constrained Gram geometry for equal column energies

Status: a complete theoretical argument has survived two independent reconstructions. This
remains an isolated research result, not an accepted breakthrough. The user rejected the earlier
premature transition to literature review. No novelty or publication-readiness claim follows.

## Exact statement

Fix \(\mathbb F\in\{\mathbb R,\mathbb C\}\) and integers \(1\le p<q\). For \(G\succeq0\)
with diagonal one define
\[
\nu(G)=\min_{\pi_i>0,\ \sum_i\pi_i=1}
\lambda_{\max}(D_\pi-G),\qquad D_\pi=\operatorname{diag}(1/\pi_i).
\]
Then
\[
\min_{\substack{G\succeq0,\ \operatorname{diag}G=\mathbf1\\\operatorname{rank}G\le p}}
\nu(G)=u_{p,q}:=\frac{q-1+\sqrt{(q-1)^2+4(q-p+1)}}2.
\tag{1}
\]
Equality holds exactly for
\[
G=J_{q-p+1}\oplus I_{p-1}
\tag{2}
\]
up to coordinate permutation and diagonal orthogonal/unitary conjugation. The optimal
probabilities are \(1/u_{p,q}\) on the collinear group and \(1/(u_{p,q}+1)\) on each singleton.

The unrestricted fixed-diagonal lower bound is \(q-1\), attained only by \(I_q\).
Formula (1) computes the gap forced by fewer than \(q\) output dimensions. It concerns
the exact declared estimator class; rank does not price resident bytes or physical I/O.

## A common first-order witness

Represent \(G=R^*R\) by a \(p\times q\) matrix of unit columns. The unit-column frame
space is compact. Since
\[
\lambda_{\max}(D_\pi-G)\ge1/\pi_i-1
\]
and the uniform law gives a value at most \(q\), a joint minimizer exists with
\(\pi_i\ge1/(q+1)\). Put \(Q=D_\pi-G\), \(t=\lambda_{\max}(Q)\), and \(S=D_\pi-tI\).
The diagonal bound implies \(t\ge q-1>0\).

There is one density matrix \(X\succeq0\), \(\operatorname{tr}X=1\), supported on the
top eigenspace of \(Q\), such that
\[
X_{ii}=c\pi_i^2,\quad c>0,\qquad RX=R\Lambda
\tag{3}
\]
for a real diagonal matrix \(\Lambda=\operatorname{diag}(\lambda_i)\).

Here is the required joint stationarity argument. On the tangent space of the product
of unit-column spheres and the open probability simplex, the directional derivative of
\(\lambda_{\max}(Q)\) is the maximum of the linear forms
\(\operatorname{tr}(X\,dQ)\) over all top-eigenspace density matrices. Their image in the
tangent dual space is compact and convex. If it did not contain zero, strict separation
would produce a tangent direction on which every form is negative, contradicting local
minimality. Thus one density matrix annihilates all joint tangent variations.

Probability variations give \(X_{ii}/\pi_i^2=c=(\sum_i\pi_i^2)^{-1}>0\). The real
differential in a frame variation is
\(-2\operatorname{Re}\operatorname{tr}(XR^*\,dR)\). Normality to each real or complex
unit sphere gives \((RX)_{:i}=\lambda_i r_i\), with \(\lambda_i\) real. This proves (3).
Lower actual rank introduces no singular rank constraint: the ambient variables remain
all unit-column \(p\times q\) matrices.

Complementary support and (3) imply
\[
GX=SX=G\Lambda,\qquad
SX=G\Lambda,\qquad
\lambda_i=s_iX_{ii}=c\,s_i\pi_i^2.
\tag{4}
\]

## Connected Gram components

Join two distinct indices when \(G_{ij}\ne0\). Gram components are orthogonal direct
summands. Equation (4) and its adjoint give
\[
s_iX_{ij}=G_{ij}\lambda_j,\qquad
X_{ij}s_j=\lambda_iG_{ij}.
\]
Consequently an edge implies \(s_i\lambda_i=s_j\lambda_j\), or
\[
|1-t\pi_i|=|1-t\pi_j|.
\tag{5}
\]
Every connected component therefore has a common value \(z\ge0\). Zero and nonzero
shifts cannot share an edge. If \(s_i=0\) and \(s_j\ne0\), then \(\lambda_j\ne0\),
so the first displayed relation forces \(G_{ij}=0\).

For a component \(C\), let \(n=|C|\), \(r=\operatorname{rank}G_C\), and
\(w=\sum_{i\in C}\pi_i\).

### Zero shifts

When \(z=0\), every \(\pi_i=1/t\), so \(w=n/t\). The principal block \(X_{CC}\)
has positive diagonal and satisfies \(G_CX_{CC}=0\); hence \(r<n\). Cross-block entries
of \(X\) between distinct zero-shift components may exist and are not assumed zero.
The component mass obeys
\[
w=\frac nt\ge\frac{n-r+1}{t}+\frac{r-1}{t+1},
\tag{6}
\]
with equality exactly when \(r=1\).

### Nonzero shifts

When \(z>0\), put \(\sigma_i=\operatorname{sign}s_i\),
\(\Sigma=\operatorname{diag}(\sigma_i)\), and \(\Pi=\operatorname{diag}(\pi_i)\).
Equations (3)--(5) give
\[
s_i=\sigma_i z/\pi_i,\qquad
\lambda_i=c\sigma_i z\pi_i,\qquad
X_{CC}=c\Pi\Sigma G_C\Sigma\Pi.
\tag{7}
\]
Thus \(X_{CC}\) has rank \(r\). In this branch its rows to other Gram components
vanish by (4), because \(S_C\) is invertible.

Write \(Y_C=G_C-S_C=tI-Q_C\succeq0\). Complementary support gives
\(Y_CX_{CC}=0\), hence \(\operatorname{rank}Y_C\le n-r\).
If \(n_+\) counts positive shifts, then
\((G_C)_{++}\succeq(S_C)_{++}\succ0\), so \(n_+\le r\).
The negative-shift principal block of \(Y_C\) is positive definite, giving
\(n_-=n-n_+\le n-r\). Therefore
\[
n_+=r,\qquad n_-=n-r.
\tag{8}
\]

Using (7) in complementary support yields \(G_C\Pi\Sigma G_C=zG_C\).
For a full-row-rank factor \(R_C\) in dimension \(r\), this is equivalent to
\[
R_C\Pi\Sigma R_C^*=zI_r.
\]
Taking traces and using the unit column norms gives \(\sum_{i\in C}\sigma_i\pi_i=rz\).
Positive shifts have probability \((1-z)/t\), and negative shifts have probability
\((1+z)/t\). Equation (8) then gives
\[
z=\frac{2r-n}{n+rt}>0,\qquad
w=\frac1t\left(n-\frac{(2r-n)^2}{n+rt}\right).
\tag{9}
\]

If \(r=n\), \(X_{CC}\) is positive definite and \(Y_C=0\), so \(G_C=S_C\) is diagonal.
Connectedness forces \(n=r=1\). This singleton has mass \(1/(t+1)\); it must be
handled separately in the final sum.

For every other nonzero-shift component, \(r<n<2r\), hence \(r\ge2\), and
\[
w>\frac{n-r+1}{t}+\frac{r-1}{t+1}.
\tag{10}
\]
Indeed, after multiplying the difference by \(t\), positivity is equivalent to
\[
(r-1)(n+rt)>(2r-n)^2(t+1).
\]
Since \(n\ge r+1\) and \(0<2r-n\le r-1\), the difference is at least
\[
(r-1)\bigl(r+1+rt-(r-1)(t+1)\bigr)=(r-1)(t+2)>0.
\]

## Global aggregation and equality

Compare every nonsingleton component of size \(n\) and rank \(r\), using (6) or (10),
with a collinear group of size \(n-r+1\) and \(r-1\) singletons. Original singleton
components contribute \(1/(t+1)\) separately.

Let \(r_{\rm total}\le p\) be the total Gram rank and \(b\) the number of nonsingleton
components. Every nonsingleton component is singular by the preceding classification.
Since \(q>p\), at least one such component exists. Thus \(b\ge1\). Summing gives
\[
1\ge
\frac{q-r_{\rm total}+b}{t}
+\frac{r_{\rm total}-b}{t+1}
\ge
\frac{q-p+1}{t}+\frac{p-1}{t+1}.
\tag{11}
\]
The final expression strictly decreases on \(t>0\), and equals one at \(u_{p,q}\).
This proves the lower bound.

Let \(m=q-p+1\). For \(G_\star=J_m\oplus I_{p-1}\), assign probability \(1/u_{p,q}\)
to each of the first \(m\) coordinates and \(1/(u_{p,q}+1)\) to the rest. They sum
to one. The covariance eigenvalues are \(u_{p,q}\) with multiplicity \(q-1\) and
\(u_{p,q}-m\). Thus the lower bound is attained.

Equality in (11) forces \(r_{\rm total}=p\) and \(b=1\). The strict comparison (10)
excludes every nonsingleton nonzero-shift component. Equality in (6) forces the one
zero-shift component to have rank one. A rank-one Gram block with diagonal one is
diagonal-unitarily equivalent to \(J_m\). All other components are singletons. This
proves (2).

## Reconstruction record and remaining work

Two independent agents reconstructed the global argument. Both required the common-\(X\)
separation argument to be explicit. One emphasized that \(X\) need not be globally block
diagonal among zero-shift components. The other emphasized separate accounting for
singletons. Both points are incorporated above. An earlier independent direct
\(p=2,q=3\) proof agrees with \(u_{2,3}=1+\sqrt3\).

The finite grid in extremal-search.json contains 1,473,171 angle/probability evaluations
for the real \(p=2,q=3\) case and found no smaller value. The proof does not use that
search. Unequal energies, physical page costs, and joint resident-description selection
remain open research directions. No literature conclusion has been drawn.

