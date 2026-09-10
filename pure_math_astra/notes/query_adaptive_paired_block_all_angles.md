# Exact query-adaptive value for two identical rotated high--low blocks

Status: exact real calculation for the paired \(q=4,s=2\) family. It
extends the 45-degree calculation in
query_adaptive_q4_sqrt_eta_block.md to every rotation angle. It makes no
global basis-optimality or novelty claim.

## 1. Statement

Let \(0<\eta<1\), put \(r=\sqrt\eta\), and let

\[
H=Q_\theta
\begin{pmatrix}1&0\\0&r^2\end{pmatrix}
Q_\theta^T
=
\begin{pmatrix}A&C\\C&B\end{pmatrix}.
\tag{1}
\]

Thus

\[
A+B=1+r^2,\qquad AB-C^2=r^2.
\tag{2}
\]

For

\[
G=\operatorname{Diag}(H,H),
\tag{3}
\]

the real query-adaptive two-coordinate value is

\[
\Psi_2(G)=r.
\tag{4}
\]

The angle \(\theta\) is arbitrary. Coordinate permutations and signs merely
change the displayed block coordinates, so no angle-range restriction is
needed.

## 2. Polar constraints

Write a polar vector as \(u=(v_1,v_2)\), with \(v_1,v_2\in\mathbb R^2\),
and define

\[
q(v)=v^TH^{-1}v,\qquad
m(v)=\max\left\{\frac{v_1^2}{A},\frac{v_2^2}{B}\right\}.
\tag{5}
\]

The polar of the two-sparse atomic body is exactly

\[
q(v_1)\le1,\qquad q(v_2)\le1,\qquad
m(v_1)+m(v_2)\le1.
\tag{6}
\]

The first two inequalities are the two within-block coordinate pairs. A
cross-block coordinate pair has diagonal principal Gram matrix with
diagonal entries chosen from \(A,B\). Maximizing its four inequalities is
exactly the final condition in (6). Singleton constraints are implied by
the corresponding two-coordinate constraints.

The ellipsoid-polar equivalence from query_adaptive_atomic_dual.md says
that

\[
u^T(G+rI)^{-1}u\le1
\quad\hbox{for every polar }u
\tag{7}
\]

implies \(\Psi_2(G)\le r\). A polar vector with equality in (7) proves the
opposite inequality, because the left side is strictly decreasing in a
putative value smaller than \(r\).

## 3. A block identity and the upper bound

Because \(H\) has eigenvalues \(1,r^2\), spectral calculus gives

\[
(1+r)(H+rI)^{-1}
=\frac r{1+r}H^{-1}+\frac1{1+r}I.
\tag{8}
\]

Also, the definition of \(m\) and (2) give

\[
\|v\|_2^2
\le m(v)(A+B)
=m(v)(1+r^2).
\tag{9}
\]

Combining (8), (9), and (6) yields

\[
\begin{aligned}
(1+r)u^T(G+rI)^{-1}u
&=\frac r{1+r}\bigl(q(v_1)+q(v_2)\bigr)
  +\frac1{1+r}\bigl(\|v_1\|_2^2+\|v_2\|_2^2\bigr)\\
&\le\frac{2r+1+r^2}{1+r}
=1+r.
\end{aligned}
\tag{10}
\]

Thus (7) holds and \(\Psi_2(G)\le r\).

## 4. A polar witness for every angle

Put

\[
\rho=\frac{|C|}{\sqrt{AB}}\in[0,1),\qquad
\sigma=
\begin{cases}
\operatorname{sign}C,&C\ne0,\\
1,&C=0,
\end{cases}
\tag{11}
\]

and define

\[
v_-=
\sqrt{\frac{1-\rho}{2}}
\begin{pmatrix}\sqrt A\\-\sigma\sqrt B\end{pmatrix},
\qquad
v_+=
\sqrt{\frac{1+\rho}{2}}
\begin{pmatrix}\sqrt A\\ \sigma\sqrt B\end{pmatrix}.
\tag{12}
\]

Direct use of (2) gives

\[
q(v_-)=q(v_+)=1,\qquad
m(v_-)=\frac{1-\rho}{2},\qquad
m(v_+)=\frac{1+\rho}{2}.
\tag{13}
\]

Hence \(u=v_-\oplus v_+\) obeys every polar constraint in (6). Moreover,

\[
v_-v_-^T+v_+v_+^T=H.
\tag{14}
\]

Therefore

\[
u^T(G+rI)^{-1}u
=\operatorname{tr}\bigl((H+rI)^{-1}H\bigr)
=\frac1{1+r}+\frac{r^2}{r^2+r}
=1.
\tag{15}
\]

For every \(0\le\lambda<r\), the same expression with \(r\) replaced by
\(\lambda\) is strictly greater than one. The ellipsoid-polar equivalence therefore
gives \(\Psi_2(G)\ge r\), completing (4).

## 5. Scope

This exact witness resolves the identical-block paired-rotation family. It
does not prove a \(\sqrt\eta\) lower bound for arbitrary rank-two
projectors, where the two coordinate blocks need not have the same
principal matrix. It does not state an encoded-byte, finite-precision, or
physical page-read result.
