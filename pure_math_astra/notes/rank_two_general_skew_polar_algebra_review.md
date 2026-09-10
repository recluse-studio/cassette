# Independent algebra review of the general skew-three polar candidate

Status: independently reconstructed exact-expansion evidence; not a compact
human-readable factor proof.  The matrix identities below reduce every
condition to a finite polynomial positivity statement.  A complete theorem
should retain the parent exact coefficient certificate or an equivalent
factorization.

Normalize a real skew \(3\times3\) matrix to

\[
 K=\begin{pmatrix}0&c&-b\\-c&0&a\\b&-a&0\end{pmatrix},\qquad
 a\ge b\ge c\ge0.
\tag{1}
\]

Put

\[
 s=c+\sqrt{1+c^2},\qquad z=b+\sqrt{1+b^2},\qquad
 u_0=(1,-s,-z)^T,\qquad n_0=(1,-s,z)^T.
\tag{2}
\]

The candidate is \(u=u_0/\|u_0\|\), \(n=n_0/\|n_0\|\), so
\(\|n\|=1\).  For an exact polynomial calculation, set

\[
 h=s-1,\qquad j=z-s,\qquad d=a-b,\qquad D=2sz,
\tag{3}
\]

and multiply \(K\) by \(D\).  The resulting integer-polynomial matrix is

\[
 K_r=\begin{pmatrix}0&C&-B\\-C&0&A\\B&-A&0\end{pmatrix},quad
 C=z(s^2-1),quad B=s(z^2-1),quad A=B+Dd.
\tag{4}
\]

For each \(|E|=|J|=2\), define

\[
 M_{EJ}=D^2I+K_{r,EJ}^TK_{r,EJ},quad
 v_{EJ}=Dn_{0,J}+K_{r,EJ}^Tu_{0,E},quad
 \Delta_{EJ}=\|u_{0,E}\|^2\det M_{EJ}
 -v_{EJ}^T\operatorname{adj}(M_{EJ})v_{EJ}.
\tag{5}
\]

Because \(M_{EJ}\) is positive definite, \(\Delta_{EJ}\ge0\) is exactly
the proper polar condition.  Independent integer polynomial expansion of
(5) gave

\[
 \Delta_{EJ}=\sum_{q=0}^{q_{EJ}}d^qP_{EJ,q}(h,j),\qquad
 P_{EJ,q}\in\mathbb Z_{\ge0}[h,j].
\tag{6}
\]

The following table records \((q_{EJ};N_0,N_1,\ldots)\), where \(N_q\) is
the number of nonzero monomials in \(P_{EJ,q}\).  Rows and columns are
ordered as \(12,13,23\).

\[
 \begin{pmatrix}
 \text{zero}&(1;62,51)&(1;69,51)\\
 (1;69,51)&(0;80)&(1;80,60)\\
 (1;76,63)&(2;89,76,55)&(3;89,76,62,51)
 \end{pmatrix}.
\tag{7}
\]

No coefficient is negative.  The scalar conditions have the same property:
five are exact equalities, while the remaining four have respectively
\(47,24,51\) nonzero terms, with the indicated nonnegative coefficient
expansion.  The full \(3\times3\) gap has 496 nonzero monomials, degree
three in \(d\), and again no negative coefficient.

Thus the candidate is supported by an independent exact algebraic check,
not by numerical sampling.  Equation (7) is a compact audit index, not a
substitute for the full coefficient list.  This review did not find a
shorter positive-factor certificate for the dense \(h,j\) slices.
