# Exact graph-chart bridge from the 2x2 polar lemma to the q=4 barrier

Status: every finite-dimensional implication in this note is proved. The
previously missing finite premise is now proved with rho=1 in
`critical_scale_2x2_polar_lemma_proof.md` and independently reconstructed in
`critical_scale_2x2_scalar_n_equals_u_review.md`. The parameterized argument
below is retained so that the transfer can be checked separately. It uses
no rare-event limit or asymptotic passage.

Let \(P\) be a real rank-two orthogonal projector on \(\mathbb R^4\) and

\[
 G_r(P)=P+r^2(I-P),\qquad 0<r\le1.
\tag{1}
\]

## A bounded graph chart

After a coordinate permutation, the range of \(P\) has the graph form

\[
 \operatorname{range}P=\operatorname{range}A,\qquad
 A=\begin{pmatrix}I_2\\ Z\end{pmatrix},
 \qquad \|Z\|_{\rm op}\le2.
\tag{2}
\]

To prove this, take a full-rank four-by-two frame for the range and choose a
row pair with maximal absolute two-by-two determinant. Right-multiply by
the inverse of that pivot pair. The selected rows become \(I_2\). If a
remaining row is \((z_1,z_2)\), its determinants with the two pivot rows
are \(-z_1\) and \(z_2\). Maximality makes both coordinates at most one in
absolute value. Hence \(\|Z\|_{\rm op}\le\|Z\|_F\le2\).

Define the positive matrix

\[
 H=\begin{pmatrix}
 I_2&Z^T\\
 Z&ZZ^T+r^2I_2
 \end{pmatrix}.
\tag{3}
\]

It is the Gram \(TT^T\) of

\[
 T=\begin{pmatrix}I_2&0\\ Z&rI_2\end{pmatrix}.
\tag{4}
\]

## Exact transfer of the finite polar conditions

Put \(K=Z^T/r\). Suppose there are vectors \(u,n\in\mathbb R^2\) with
\(\|u\|_2=1\) such that

\[
 |n_j+u_mK_{mj}|
 \le |u_m|\sqrt{1+K_{mj}^2}
 \qquad(m,j=1,2),
\tag{5}
\]

and

\[
 (n+K^Tu)^T(I_2+K^TK)^{-1}(n+K^Tu)\le1.
\tag{6}
\]

Set

\[
 z=(u,Zu+rn)^T.
\tag{7}
\]

Then \(z\) belongs to the two-sparse atomic polar for \(H\):

\[
 z_S^TH_{SS}^{-1}z_S\le1
 \qquad(|S|=2).
\tag{8}
\]

There are six pairs. The high-high pair gives \(\|u\|^2=1\). The low-low
pair gives (6), because

\[
 Zu+rn=r(K^Tu+n),\qquad
 H_{LL}=r^2(I_2+K^TK).
\tag{9}
\]

For a high coordinate \(m\) and a low coordinate \(j\), let \(m'\) be
the other high index. Schur complementation of the high entry gives

\[
 z_{\{m,j\}}^TH_{\{m,j\}}^{-1}z_{\{m,j\}}
 =u_m^2+
 {\bigl(rn_j+Z_{jm'}u_{m'}\bigr)^2
  \over r^2+Z_{jm'}^2}.
\tag{10}
\]

Since \(1-u_m^2=u_{m'}^2\), (10) is at most one exactly when the
corresponding inequality in (5) holds. Thus the four cross pairs are also
covered. Singleton support constraints are dominated by a containing pair,
so (8) is the complete at-most-two polar test.

## Explicit conditional lower bound for H

Assume the following finite-lemma premise for some fixed
\(\rho>0\): for every real two-by-two \(K\), there are \(u,n\) satisfying
(5)--(6), \(\|u\|=1\), and

\[
 \|n\|_2\ge\rho.
\tag{11}
\]

Let

\[
 c_\rho=\min\left\{{\rho\over8},{1\over8}\right\}.
\tag{12}
\]

Then, for \(0<r\le c_\rho\),

\[
 \Psi_2(H)\ge c_\rho r.
\tag{13}
\]

For verification, put \(v=c_\rho r\). Block inversion of \(H+vI\)
gives the exact identity

\[
 \begin{aligned}
 z^T(H+vI)^{-1}z
 &= {1\over1+v}+a^TS^{-1}a,\\
 a&=rn+{v\over1+v}Zu,\\
 S&=(r^2+v)I_2+{v\over1+v}ZZ^T.
 \end{aligned}
\tag{14}
\]

As \(r\le c_\rho\), \(\|Z\|\le2\), and \(c_\rho\le\rho/8\),

\[
 \|a\|\ge r\rho-2c_\rho r\ge {r\rho\over2},
 \qquad
 \lambda_{\max}(S)\le r^2+5c_\rho r\le6c_\rho r.
\tag{15}
\]

Therefore

\[
 z^T(H+vI)^{-1}z-1
 \ge r\left({\rho^2\over24c_\rho}
             -{c_\rho\over1+c_\rho r}\right)>0.
\tag{16}
\]

The strict final inequality follows from \(c_\rho\le\rho/8\), which
implies \(\rho^2/(24c_\rho)>c_\rho\). Atomic polarity and (8) prove
(13).

## Comparison to the actual projector metric

Set

\[
 F=\begin{pmatrix}-Z^T\\I_2\end{pmatrix},
 \qquad H'=AA^T+r^2FF^T.
\tag{17}
\]

The columns of \(F\) span \(\ker P\). Since
\(A^TA=I+Z^TZ\preceq5I\) and
\(F^TF=I+ZZ^T\preceq5I\),

\[
 AA^T\preceq5P,\qquad FF^T\preceq5(I-P),
 \qquad G_r(P)\succeq {1\over5}H'.
\tag{18}
\]

For \(x=(x_H,x_L)\), make the invertible coordinate change

\[
 w=x_H+Z^Tx_L,\qquad t=rx_L.
\tag{19}
\]

The two quadratic forms are exactly

\[
 x^THx=\|w\|^2+\|t\|^2,
\tag{20}
\]

and

\[
 x^TH'x=\|w\|^2+
 \|(I_2+ZZ^T)t-rZw\|^2.
\tag{21}
\]

Write the vector inside the second norm in (21) as \(s\). Because
\(\|(I_2+ZZ^T)^{-1}\|\le1\),

\[
 \|t\|\le\|s\|+r\|Z\|\,\|w\|
 \le\|s\|+2\|w\|.
\tag{22}
\]

Hence

\[
 \|w\|^2+\|t\|^2
 \le9\|w\|^2+2\|s\|^2
 \le9\bigl(\|w\|^2+\|s\|^2\bigr).
\tag{23}
\]

Equations (18) and (23) give the uniform Loewner comparison

\[
 \boxed{\quad G_r(P)\succeq {1\over45}H.\quad}
\tag{24}
\]

The orientation is important: \(H\) is an auxiliary graph-chart Gram,
not \(G_r(P)\), and (24) transfers lower bounds from \(H\) to \(G_r(P)\).

## Conditional global q=4 conclusion

Under premise (11), equations (13) and (24) imply

\[
 \Psi_2(G_r(P))\ge {c_\rho\over45}r
 \qquad(0<r\le c_\rho).
\tag{25}
\]

For \(r\ge c_\rho\), the elementary comparison
\(G_r(P)\succeq r^2I_4\), together with
\(\Psi_2(I_4)=1\), gives
\(\Psi_2(G_r(P))\ge r^2\ge c_\rho r\). Thus the all-range conditional
bound is

\[
 \boxed{\quad
 \Psi_2(G_r(P))\ge {c_\rho\over45}r
 \qquad(0<r\le1).
 \quad}
\tag{26}
\]

The proved finite lemma now supplies \(\rho=1\), so
\(c_\rho=1/8\) and (26) gives the all-range bound \(r/360\).
The current proof and its independent scalar reconstruction are linked
at the top of this note. The old numerical evidence is no longer the
authority for this premise.
