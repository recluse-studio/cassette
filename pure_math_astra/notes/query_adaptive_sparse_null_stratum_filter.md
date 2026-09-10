# Sparse-null stratum filter for the query-adaptive q=4, s=2 problem

Status: the fixed-projector theorem below is proved.  The proposed uniform
continuation near its exceptional strata is not proved here.

Let \(P\) be a real rank-two orthogonal projector on \(\mathbb R^4\), put

\[
 N(P)=\operatorname{span}\{z\in\ker P:\ |\operatorname{supp}z|\le2\},
 \qquad G_\eta=P+\eta(I-P),\quad \eta>0.
\tag{1}
\]

## Fixed-projector theorem

If \(N(P)\ne\ker P\), then there is a constant \(c(P)>0\) such that

\[
 \Psi_2(G_\eta)\ge c(P)-\eta.
\tag{2}
\]

Choose nonzero \(u\in\ker P\cap N(P)^\perp\).  For a coordinate pair
\(S\), every \(z_S\in\ker P_{SS}\), extended by zero off \(S\), belongs to
\(\ker P\): positivity gives

\[
 z_S^TP_{SS}z_S=0\quad\Longrightarrow\quad Pz=0.
\tag{3}
\]

Thus \(u_S\perp\ker P_{SS}\), so \(u_S\in\operatorname{range}P_{SS}\).
Consequently

\[
 C=\max_{|S|=2}u_S^TP_{SS}^{\dagger}u_S<\infty.
\tag{4}
\]

The maximum C is positive: if it vanished, each u_S in the range of
P_SS would vanish, forcing u=0. Replace \(u\) by \(u/\sqrt C\).
Every eigenvalue \(\lambda\)
of a principal block \(P_{SS}\) lies in \([0,1]\), and

\[
 (G_\eta)_{SS}=P_{SS}+\eta(I-P_{SS})
\tag{5}
\]

has eigenvalue \(\lambda+\eta(1-\lambda)\ge\lambda\) on the positive
eigenspace.  Since each \(u_S\) is in that eigenspace,

\[
 u_S^T(G_\eta)_{SS}^{-1}u_S\le1
\tag{6}

\]

for every \(S\).  The atomic polar characterization therefore makes \(u\)
dual feasible.  If \(v\) is any valid ellipsoid-containment variance bound,
then

\[
 1\ge u^T(G_\eta+vI)^{-1}u
   =\frac{\|u\|_2^2}{\eta+v},
\tag{7}
\]

and hence \(v\ge\|u\|_2^2-\eta\).  This proves (2).

## Exact exceptional strata

Take an orthonormal two-frame \(E\in\mathbb R^{4\times2}\) with
\(P=EE^T\).  Partition its nonzero coordinate rows into parallel-direction
classes, and let \(z\) be the number of zero rows and \(r\) the number of
nonzero classes.  A zero row contributes a one-sparse vector to \(N(P)\).
Within a class of size \(m\), the \(m-1\) linear relations are spanned by
two-sparse relations.  No two-sparse relation joins distinct nonzero classes.
Therefore

\[
 \dim N(P)=z+\sum_{\text{classes }C}(|C|-1)=4-r.
\tag{8}
\]

Since \(\dim\ker P=2\) and \(r\ge2\), equality \(N(P)=\ker P\) holds
exactly when \(r=2\). Choose unit direction representatives a_1,a_2 for
those two classes. In that case frame normalization has the form

\[
 w_1a_1a_1^T+w_2a_2a_2^T=I_2.
\tag{9}
\]

Taking trace and determinant shows \(w_1=w_2=1\) and
\(a_1\perp a_2\).  Hence \(P\) is a direct sum of two rank-one coordinate
blocks, with any remaining coordinates zero.  Up to permutation, the only
exceptional patterns are \(2+2\), \(3+1\), zero-plus-\(2+1\), and
two-zeros-plus-\(1+1\).

Thus a *fixed* projector with \(\Psi_2(G_\eta)\to0\) must lie in one of
these direct-sum strata.  This eliminates every fixed three- or four-direction
plane from a possible small-\(\eta\) optimizer.

## Why compactness does not yet make this uniform

The inverse forms in (6) are discontinuous at a singular principal block.
At a rank-one limiting block, a nearby positive block can have schematic
form

\[
 A_{\epsilon,\delta}=
 \begin{pmatrix}1&\epsilon\\
                 \epsilon&\epsilon^2+\delta^2\end{pmatrix}.
\tag{10}
\]

Its small eigenvalue is comparable to \(\delta^2\), while its small
eigenvector rotates from \((0,1)\) by order \(\epsilon\).  A vector made
orthogonal only to the limiting null vector can therefore have inverse
quadratic contribution of order \(\epsilon^2/\delta^2\).  This model occurs
as a principal row Gram block of a nearby two-plane: take the two row vectors
\((1,0)\) and \((\epsilon,\delta)\), complete them by two fixed rows that
span \(\mathbb R^2\), and normalize the resulting full-rank frame.

The example does not disprove a uniform lower bound.  One may instead choose
a witness orthogonal to the *current* smallest-eigenvalue direction.  With
several singular coordinate pairs, however, those directions can split at
different rates, and their exact orthogonality conditions need not be
simultaneously compatible inside \(\ker P\).  A proof must select the
dominant constraint by scale and show that the weaker constraints then have
enough eigenvalue to absorb the residual.  This is a stratified blow-up or
multiscale argument, not a consequence of continuity on the ordinary
Grassmannian.
