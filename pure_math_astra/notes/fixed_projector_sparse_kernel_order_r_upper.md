# An order-r upper bound from sparse kernel generators

Status: proved.  This finite-dimensional result constructs one
query-independent random linear law for each fixed \(P,r\).  It therefore
applies both to the query-adaptive exact-mean problem and to the fixed-law
linear minimax problem.  It makes no encoded-byte or diagonal-HT claim.

For a real orthogonal projector \(P\) of rank \(k\), set

\[
 G_r=P+r^2(I-P),\qquad 0<r\le1,
\tag{1}
\]

and define

\[
 \Psi_k(G_r)=\sup_{\|x\|_2=1}
 \inf_{\substack{\mathbb EY=x\\\|Y\|_0\le k\ {\rm a.s.}}}
 \mathbb E\,(Y-x)^TG_r(Y-x).
\tag{2}
\]

## The fixed-projector theorem

**Theorem.**  Suppose that \(\ker P\) has a basis
\(n_1,\ldots,n_m\), each supported on at most \(k\) coordinates.  Then
there is a finite constant \(C_P\) and a fixed unbiased random linear law
with output support at most \(k\) such that

\[
\Psi_k(G_r)\le C_Pr\qquad(0<r\le1).
\tag{3}
\]

Here \(\nu_k(G_r)\) denotes the minimax risk over fixed unbiased random
linear maps with at most \(k\) nonzero output rows.  The same bound holds
for \(\nu_k(G_r)\), since the construction below uses fixed random linear
maps.  The constant depends on the fixed projector and on a chosen sparse
kernel basis.  It is not uniform as \(P\) varies.

Choose a row-orthonormal matrix \(A\in\mathbb R^{k\times q}\) with
\(P=A^TA\).  For an increasing coordinate \(k\)-subset \(S\), write \(A_S\) for the
corresponding \(k\times k\) column submatrix and \(E_S\) for coordinate
insertion.  Let

\[
 \mathcal F=\{S:\det A_S\ne0\},\qquad
 p_S=\det(A_S)^2,\qquad
 H_S=E_SA_S^{-1}A.
\tag{4}
\]

Cauchy--Binet gives \(\sum_{S\in\mathcal F}p_S=\det(AA^T)=1\).  It
also gives the mean identity

\[
 \sum_{S\in\mathcal F}p_SH_S=P.
\tag{5}
\]

For completeness, differentiate the Cauchy--Binet identity
\(\det(AA^T)=\sum_S\det(A_S)^2\) with respect to every entry of \(A\).
At \(AA^T=I\), the transpose of the derivative identity is
\(\sum_S\det(A_S)^2E_SA_S^{-1}=A^T\), which becomes (5) after right
multiplication by \(A\).  This is the usual volume-sampling adjugate
identity.

Let \(S\) have probabilities \(p_S\) and put \(Y_H=H_Sx\).  Every
outcome has support at most \(k\), and

\[
 AY_H=Ax,\qquad PY_H=Px,\qquad \mathbb EY_H=Px.
\tag{6}
\]

Set \(C_H=\max_{S\in\mathcal F}\|H_S\|_{\rm op}<\infty\).  Thus, for
unit \(x\),

\[
 \mathbb E\|(I-P)Y_H\|_2^2\le C_H^2.
\tag{7}
\]

For \(w\in\ker P\), write \(w=\sum_{j=1}^m c_j(w)n_j\), where the
coefficient map \(c\) is any fixed linear inverse of the displayed basis.
Let \(J\) be uniform on \(\{1,\ldots,m\}\) and define

\[
 Y_N=m c_J((I-P)x)n_J.
\tag{8}
\]

Again every outcome has support at most \(k\), while

\[
 PY_N=0,\qquad \mathbb EY_N=(I-P)x,\qquad
 \mathbb E\|Y_N\|_2^2\le C_N\|(I-P)x\|_2^2
\tag{9}
\]

for a finite \(C_N\), because the maps and the set of vectors are fixed.

Take \(\rho=\min(r,1/2)\).  Independently choose the following two
outcomes:

\[
 Y=\begin{cases}
  Y_H/(1-\rho),&\text{with probability }1-\rho,\\
  Y_N/\rho,&\text{with probability }\rho.
 \end{cases}
\tag{10}
\]

The outcomes are never added, so the hard support cap remains \(k\).  Both
branches are fixed linear maps of \(x\), and their probabilities depend only
on \(P,r\).  By (6) and (9), \(\mathbb EY=x\) exactly.  Direct orthogonal
decomposition of its risk gives, for unit \(x\),

\[
 \begin{aligned}
 \mathbb E\,(Y-x)^TG_r(Y-x)
 &\le \rho+{\rho^2\over1-\rho}
      +(4C_H^2+2)r^2+{C_Nr^2\over\rho}.
 \end{aligned}
\tag{11}
\]

Indeed, the two high-space terms are
\(\rho^2\|Px\|^2/(1-\rho)\) and \(\rho\|Px\|^2\).  On the high
branch, the low-space term is bounded with
\(\|a-b\|^2\le2\|a\|^2+2\|b\|^2\), (7), and
\((1-\rho)^{-1}\le2\).  On the low branch, exact unbiasedness in (9)
gives

\[
 \rho r^2\mathbb E\|Y_N/\rho-(I-P)x\|_2^2
 \le {C_Nr^2\over\rho}.
\tag{12}
\]

For \(r\le1/2\), (11) is at most
\((C_N+2C_H^2+3)r\).  For \(1/2\le r\le1\), (11) is at most
\(3+4C_H^2+2C_N\), hence at most
\(2(3+4C_H^2+2C_N)r\).  This proves (3).

## The \(K_4\) cut-space projector

Use edge order \((12,13,14,23,24,34)\).  For its rank-three cut-space
projector, the full-rank three-edge supports in (4) are exactly the sixteen
trees.  The tree calculation
\(\lambda_{\min}(P_{SS})\ge1/16\) gives \(C_H\le4\).

A sparse basis of the cycle space is

\[
 n_{123}=(1,-1,0,1,0,0)^T,\qquad
 n_{124}=(1,0,-1,0,1,0)^T,\qquad
 n_{134}=(0,1,-1,0,0,1)^T.
\tag{13}
\]

Each vector has support three.  Their Gram matrix has eigenvalues \(1,4,4\).
For the uniform construction (8), this gives

\[
 \mathbb E\|Y_N\|_2^2=9\|c((I-P)x)\|_2^2
 \le9\|(I-P)x\|_2^2,
\tag{14}
\]

so \(C_N=9\) is valid.  Consequently,

\[
\nu_3(P+r^2(I-P))\le44r\quad(0<r\le1/2),
\qquad
\nu_3(P+r^2(I-P))\le170r\quad(0<r\le1).
\tag{15}
\]

The same bounds hold for \(\Psi_3\). Together with the lower bounds in the
two companion K4 notes, this proves that both \(\Psi_3(P+r^2(I-P))\)
and \(\nu_3(P+r^2(I-P))\) are \(\Theta_P(r)\) for this fixed projector.
It does not assert that the two values are equal.

The later fixed_projector_sparse_kernel_dichotomy.md supplies the
converse and sharpens this K4 upper to \(\nu_3\le7r\), hence
\(\Psi_3\le7r\), using all four triangle cycles as a tight frame.
Neither note proves a uniform statement over moving projectors.
