# Exact rank-\(k\) graph-chart reduction for hard \(k\)-coordinate sampling

Status: root reconstructed this reduction and its conditional steps have
been independently checked. The finite \(k\)-polar lemma remains **OPEN**
for every \(k\ge3\). No claim is made that the \(k=2\) proof extends, or
that this establishes an unconditional general rank-\(k\) lower bound.

Fix \(k\ge2\). For a real rank-\(k\) orthogonal projector \(P\) on
\(\mathbb R^{2k}\), let

\[
G_r(P)=P+r^2(I-P),\qquad 0<r\le1.
\]

Write \(\Psi_k(G)\) for the worst-unit-query minimum quadratic risk among
unbiased random coefficient vectors with support at most \(k\).

## 1. A uniformly bounded graph chart

After a coordinate permutation,

\[
\operatorname{range}P
 =\operatorname{range}A,\qquad
A=\begin{pmatrix}I_k\\ Z\end{pmatrix},
\qquad \|Z\|_{\rm op}\le k. \tag{1}
\]

Take a \(2k\times k\) full-rank frame for \(\operatorname{range}P\), choose
a row \(k\)-tuple with maximum absolute determinant, and right-multiply by
the inverse of that row block. Each selected row becomes a row of \(I_k\).
Replacing its \(i\)-th selected row by any remaining row gives a determinant
equal, up to sign, to the \(i\)-th entry of that remaining row. Maximality
therefore bounds every entry of \(Z\) by one. Hence
\(\|Z\|_{\rm op}\le\|Z\|_F\le k\).

Define

\[
H_r(Z)=
\begin{pmatrix}
 I_k&Z^T\\
 Z&ZZ^T+r^2I_k
\end{pmatrix},
\qquad K=Z^T/r. \tag{2}
\]

The matrix \(H_r(Z)\) is positive definite for \(r>0\).

## 2. The exact finite polar system

Let \(u,n\in\mathbb R^k\), with \(\|u\|_2=1\), and set

\[
z_0=(u,Zu+rn)^T. \tag{3}
\]

For \(0\le j\le k\), let \(E,J\subseteq[k]\) have
\(|E|=|J|=j\). Define \(I=[k]\setminus E\); then
\(|I|+|J|=k\). The polar constraint on the support comprising high
coordinates \(I\) and low coordinates \(J\) is exactly

\[
\boxed{\quad
 (n_J+K_{E,J}^Tu_E)^T
 (I_j+K_{E,J}^TK_{E,J})^{-1}
 (n_J+K_{E,J}^Tu_E)
 \le \|u_E\|_2^2.
 \quad} \tag{4}
\]

For \(j=0\), (4) is void and the full-high support has value
\(\|u\|_2^2=1\). For \(j=k\), (4) is the full low-support ellipsoid
condition

\[
(n+K^Tu)^T(I_k+K^TK)^{-1}(n+K^Tu)\le1. \tag{5}
\]

To prove (4), Schur complement the high block \(I_{|I|}\) in the principal
matrix on \(I\cup J\). Its Schur complement is

\[
r^2I_j+Z_{J,E}Z_{J,E}^T,
\]

and the residual coordinate vector is

\[
rn_J+Z_{J,E}u_E.
\]

Dividing by \(r\) gives (4), because
\(Z_{J,E}/r=K_{E,J}^T\). This derivation does not require
\(K_{E,J}\) to be invertible: \(I_j+K_{E,J}^TK_{E,J}\) is always positive
definite.

The system (4) covers every at-most-\(k\) support. Indeed, any smaller
support extends to a support of size \(k\). If \(T\subseteq S\) and
\(H_{r,S}\) is positive definite, block inversion gives

\[
z_{0,S}^TH_{r,S}^{-1}z_{0,S}
\ge z_{0,T}^TH_{r,T}^{-1}z_{0,T}. \tag{6}
\]

Thus the size-\(k\) inequalities imply every smaller-support inequality.


## 3. The exact remaining finite lemma

The rank-\(k\) graph route is reduced to the following statement.

**Finite \(k\)-polar lemma.** There is a number \(\rho_k>0\) such that,
for every real \(K\in\mathbb R^{k\times k}\), there are
\(u,n\in\mathbb R^k\) with

\[
\|u\|_2=1,\qquad \|n\|_2\ge\rho_k,
\]

which satisfy (4) for every \(j\) and every pair
\(E,J\subseteq[k]\) with \(|E|=|J|=j\).

One may replace \(\rho_k\) by \(\min\{\rho_k,1\}\), so assume from now on
that \(0<\rho_k\le1\).

This is not an immediate extension of the \(k=2\) scalar proof. At
\(k=2\), the nontrivial proper constraints have \(j=1\), and the two
cross boxes reduce to a single scalar interval after sign normalization.
For \(k\ge3\), the \(j=1\) constraints already form \(k^2\) simultaneous
boxes, while every \(2\le j\le k-1\) adds coupled matrix inequalities for
all square submatrices. The one-angle \(n=u\) construction therefore does
not supply this lemma without a new argument.

## 4. Conditional lower bound for the graph metric

Assume the finite \(k\)-polar lemma. Put

\[
c_k={\rho_k\over4(k^2+2)}. \tag{7}
\]

For \(0<r\le c_k\), set \(v=c_kr\). Block inversion of \(H_r(Z)+vI\)
at the high block gives

\[
z_0^T(H_r(Z)+vI)^{-1}z_0
={1\over1+v}+a^TS^{-1}a, \tag{8}
\]

where

\[
a=rn+{v\over1+v}Zu,\qquad
S=(r^2+v)I_k+{v\over1+v}ZZ^T. \tag{9}
\]

The chart bound \(\|Z\|\le k\) yields

\[
\|a\|_2\ge r\rho_k-c_krk\ge{r\rho_k\over2}, \tag{10}
\]

and, since \(r^2\le c_kr\),

\[
\lambda_{\max}(S)
 \le r^2+v+v\|Z\|^2
 \le c_kr(k^2+2). \tag{11}
\]

Consequently,

\[
\begin{aligned}
z_0^T(H_r(Z)+vI)^{-1}z_0-1
&\ge r\left[
{\rho_k^2\over4c_k(k^2+2)}
-{c_k\over1+c_kr}
\right]\\
&>0. \tag{12}
\end{aligned}
\]

The bracket is positive because the first term equals \(\rho_k\) by (7),
whereas \(c_k<\rho_k\). The atomic-polar ellipsoid criterion and
(4)--(6) therefore imply

\[
\Psi_k(H_r(Z))\ge c_kr
\qquad(0<r\le c_k). \tag{13}
\]


## 5. Transfer to the projector metric

Set

\[
F=\begin{pmatrix}-Z^T\\I_k\end{pmatrix},
\qquad H'=AA^T+r^2FF^T. \tag{14}
\]

The columns of \(F\) span \(\ker P\). With \(M_k=1+k^2\),

\[
AA^T\preceq M_kP,\qquad
FF^T\preceq M_k(I-P),
\]

so

\[
G_r(P)\succeq {1\over M_k}H'. \tag{15}
\]

For \(x=(x_H,x_L)\), make the invertible coordinate change

\[
w=x_H+Z^Tx_L,\qquad t=rx_L.
\]

Then, exactly,

\[
x^TH_r(Z)x=\|w\|^2+\|t\|^2, \tag{16}
\]

and

\[
x^TH'x=\|w\|^2+
\|(I_k+ZZ^T)t-rZw\|^2. \tag{17}
\]

Set \(s=(I_k+ZZ^T)t-rZw\), the vector inside the final norm in (17).
Then

\[
\|t\|\le\|s\|+r\|Z\|\,\|w\|
\le\|s\|+k\|w\|.
\]

Therefore

\[
\|w\|^2+\|t\|^2
\le(1+2k^2)\bigl(\|w\|^2+\|s\|^2\bigr). \tag{18}
\]

Equations (15)--(18) give

\[
G_r(P)\succeq
{1\over(1+k^2)(1+2k^2)}\,H_r(Z). \tag{19}
\]

Monotonicity of the exact-mean infimum in the metric transfers (13) to

\[
\Psi_k(G_r(P))\ge
{\rho_k\over
4(k^2+2)(1+k^2)(1+2k^2)}\,r
\qquad(0<r\le c_k). \tag{20}
\]

For \(r\ge c_k\), \(G_r(P)\succeq r^2I_{2k}\) and

\[
\Psi_k(I_{2k})=1. \tag{21}
\]

For the upper bound in (21), sample a uniform \(k\)-subset and multiply
its selected coordinates by two. For the lower bound, use the unit query
with all \(2k\) coordinates equal. Every \(k\)-sparse outcome \(Y\)
satisfies \(\|Y\|_1^2\le k\|Y\|_2^2\), and therefore

\[
\mathbb E\|Y\|_2^2\ge
{(\mathbb E\|Y\|_1)^2\over k}
\ge {\|\mathbb EY\|_1^2\over k}=2.
\]

Unbiasedness then makes its squared error at least one. Thus
\(\Psi_k(G_r(P))\ge r^2\ge c_kr\), which is stronger than (20).

Hence the finite \(k\)-polar lemma would imply the uniform explicit bound

\[
\boxed{
\Psi_k\bigl(P+r^2(I-P)\bigr)\ge
{\rho_k\over
4(k^2+2)(1+k^2)(1+2k^2)}\,r
}
\]

for every real rank-\(k\) projector \(P\) on \(\mathbb R^{2k}\) and
\(0<r\le1\).

The unresolved mathematical target is precisely the finite \(k\)-polar
lemma in Section 3. The chart, all support inequalities, singular-minor
handling, and the conditional transfer above require no additional
asymptotic or limiting argument.
