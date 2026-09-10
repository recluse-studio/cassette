# Independent reconstruction of the rank-one finite \(k\)-polar lemma

Status: verified for real rank-at-most-one matrices. This note derives the
resulting uniform graph-chart and \(O(r)\)-tube consequences. It does not
address rank-two or higher finite polar geometry.

## Finite lemma

Write \(K=ab^T\) with \(\|b\|_2=1\). This is always possible for
nonzero rank-one \(K\). For \(K=0\), choose an arbitrary unit \(b\) and
put \(a=0\). Define

\[
w_i={1\over1+|a_i|},\qquad
R=\left(\sum_iw_i^2\right)^{1/2},\qquad
u_i=-{\operatorname{sgn}(a_i)w_i\over R},\qquad
n={b\over\sqrt{k}}. \tag{R1}
\]

At \(a_i=0\), any fixed sign convention works. Thus

\[
\|u\|_2=1,\qquad\|n\|_2={1\over\sqrt{k}}. \tag{R2}
\]

For nonempty \(E\) and any \(J\) of the same cardinality, set

\[
A=\|a_E\|^2,\quad B=\|b_J\|^2,\quad
W=\|w_E\|,\quad Q=\sum_{i\in E}|a_i|w_i,\quad
d={1\over\sqrt{k}}.
\]

Then

\[
a_E^Tu_E=-Q/R,\qquad
\|u_E\|=W/R,\qquad
n_J+K_{E,J}^Tu_E=(d-Q/R)b_J. \tag{R3}
\]

The Sherman--Morrison formula is valid even when \(A=0\) or \(B=0\), and
gives

\[
b_J^T(I+A b_Jb_J^T)^{-1}b_J={B\over1+AB}
\le {1\over1+A}, \tag{R4}
\]

because \(0\le B\le1\). It remains to prove

\[
|d-Q/R|\le {W\sqrt{1+A}\over R}. \tag{R5}
\]

Cauchy--Schwarz gives \(Q\le W\sqrt A\), which proves the lower endpoint.
For any \(i\in E\),

\[
Q+W\sqrt{1+A}
\ge {|a_i|+\sqrt{1+a_i^2}\over1+|a_i|}\ge1. \tag{R6}
\]

The first inequality uses \(Q\ge|a_i|w_i\),
\(W\ge w_i\), and \(\sqrt{1+A}\ge\sqrt{1+a_i^2}\).
As \(R\le\sqrt k\), (R6) gives the upper endpoint in (R5). Combining
(R4) and (R5) yields every required square-submatrix inequality.

When \(K=0\), this proof remains literal: \(R=\sqrt k\), \(Q=A=0\), and
(R5) reads \(1/\sqrt k\le\sqrt{|E|/k}\). Thus zero rows, zero columns,
and the full zero matrix need no exceptional argument. If \(E\) is empty,
then \(J\) is empty as well and the condition is void. Therefore

\[
\rho_k\ge {1\over\sqrt k}
\]

for the real rank-at-most-one finite \(k\)-polar lemma.

## Uniform rank-one graph consequence

Let \(P\) be a real rank-\(k\) projector on \(\mathbb R^{2k}\). Suppose
that, after a coordinate permutation, its range has a max-volume graph
chart

\[
\operatorname{range}P=\operatorname{range}
\begin{pmatrix}I_k\\Z\end{pmatrix},
\qquad \operatorname{rank}Z\le1. \tag{R7}
\]

Then \(K=Z^T/r\) has rank at most one for every \(r>0\), so the finite
lemma supplies \(\rho_k=1/\sqrt k\) in the graph reduction. Substitution
into its explicit constant yields

\[
\boxed{
\Psi_k\bigl(P+r^2(I-P)\bigr)\ge
{r\over
4\sqrt k\,(k^2+2)(1+k^2)(1+2k^2)}
}
\qquad(0<r\le1). \tag{R8}
\]

The coordinate permutation preserves the support-cap problem and its value.
This is a uniform bound over the stated chart locus.

## \(O(r)\)-tube transfer

Let \(P_0\) be any projector in the rank-one graph locus (R7), and suppose

\[
\|P-P_0\|_{\rm op}\le Kr,\qquad K\ge0. \tag{R9}
\]

For every orthogonal projector \(Q\),

\[
G_r(Q)^{1/2}=rI+(1-r)Q.
\]

Hence, for every vector \(x\),

\[
\|G_r(P_0)^{1/2}x\|
\le\|G_r(P)^{1/2}x\|+Kr\|x\|
\le(1+K)\|G_r(P)^{1/2}x\|, \tag{R10}
\]

because \(G_r(P)\succeq r^2I\). Thus

\[
G_r(P_0)\preceq(1+K)^2G_r(P). \tag{R11}
\]

The exact-mean, hard-\(k\)-support infimum is monotone in the metric, so
(R8)--(R11) give

\[
\boxed{
\Psi_k\bigl(P+r^2(I-P)\bigr)\ge
{r\over
4(1+K)^2\sqrt k\,(k^2+2)(1+k^2)(1+2k^2)}
}.
\tag{R12}
\]

This is valid for a fixed tube multiplier \(K\). It is a real-field
statement and does not cover a basis change that changes the coordinate
support model.

