# Exact finite-polar certificate for the rank-two skew cycle

Status: proved for this one-parameter rank-two family.  This does not prove
the finite three-polar lemma for arbitrary rank-two matrices.

Let

\[
 K_t=t\begin{pmatrix}0&1&-1\\-1&0&1\\1&-1&0\end{pmatrix},\qquad t\ge0,
\tag{1}
\]

and set

\[
 s=t+\sqrt{1+t^2},\qquad D=\sqrt{1+2s^2}.
\tag{2}
\]

Then \(s\ge1\) and \(t=(s-s^{-1})/2\).  Define

\[
 u={1\over D}(1,-s,-s)^T,\qquad
 n={1\over D}(1,-s,s)^T.
\tag{3}
\]

Both vectors have unit norm.  They satisfy every finite polar inequality

\[
 (n_J+K_{E,J}^Tu_E)^T
 (I+K_{E,J}^TK_{E,J})^{-1}
 (n_J+K_{E,J}^Tu_E)
 \le\|u_E\|_2^2
\tag{4}
\]

for all \(E,J\subseteq[3]\) with \(|E|=|J|\).  Thus this correlated
rank-two family admits \(\rho_3=1\), uniformly in \(t\).

## Determinant-gap verification

Put \(\widetilde u=(1,-s,-s)^T\) and
\(\widetilde n=(1,-s,s)^T\).  For each nonempty pair \((E,J)\), let

\[
 M_{EJ}=I+K_{E,J}^TK_{E,J},\qquad
 \Delta_{EJ}=\|\widetilde u_E\|_2^2\det M_{EJ}
 -v_{EJ}^T\operatorname{adj}(M_{EJ})v_{EJ},
\tag{5}
\]

where \(v_{EJ}=\widetilde n_J+K_{E,J}^T\widetilde u_E\).  Since
\(M_{EJ}\) is positive definite, (4) is equivalent to
\(\Delta_{EJ}\ge0\).  The common factor \(D^{-2}\) cancels from this
equivalence.

Write \(x=s-1\).  The following tables give exact determinant expansions.
An entry \((m;c_1,\ldots,c_d)\) means

\[
 \Delta_{EJ}=s^m\sum_{\ell=1}^dc_\ell x^\ell.
\tag{6}
\]

Every listed coefficient is positive, so every listed gap is nonnegative
for \(s\ge1\).  A zero denotes an exact equality.

For singleton sets, with rows indexed by \(E=1,2,3\) and columns by
\(J=1,2,3\), the gap table is

\[
 \begin{pmatrix}
 0&0&0\\
 0&0&(1;2,1)\\
 (0;4,2)&(1;2,1)&0
 \end{pmatrix}.
\tag{7}
\]

For two-element sets, order both \(E\) and \(J\) as \(12,13,23\).  The
entries are

\[
 \begin{pmatrix}
 0&(-3;2,5,6,4,3/2,1/4)&(-1;4,8,7,3,1/2)\\
 (-3;6,23,36,31,31/2,17/4,1/2)&(-2;4,10,12,8,3,1/2)&(-1;4,8,7,3,1/2)\\
 (0;4,8,7,3,1/2)&(-2;4,12,23,26,31/2,9/2,1/2)&(-1;4,10,12,8,3,1/2)
\end{pmatrix}.
\tag{8}
\]

The full-support gap is

\[
 \Delta_{[3],[3]}
 =s^{-3}\left(8x+32x^2+78x^3+122x^4+123x^5
 +80x^6+{65\over2}x^7+{15\over2}x^8+{3\over4}x^9\right).
\tag{9}
\]

Equations (7)--(9) prove every nonvoid condition.  They arise by direct
expansion of matrices of order at most three after substituting
\(t=(s-s^{-1})/2\); no numerical feasibility inference is used.

The certificate uses the \((+,+,-)\) scalar-box branch and the endpoint
\(z=s\) of the proposed interval.  The proper two-by-two table is essential:
checking only the scalar boxes and the full ellipsoid would not prove (4).
