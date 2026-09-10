# Finite coefficient certificate for the proper skew-three polar gaps

Status: exact finite algebraic certificate for the nine proper
\(2\times2\) gaps of the normalized real skew-three candidate.  The
coefficient list is stored in
`rank_two_general_skew_proper_gap_coefficients.json`; it is part of this
certificate, not a numerical record.  The companion standard-library
regenerator is `../programs/skew3_proper_gap_certificate.py`.

Assume

\[
 K=\begin{pmatrix}0&c&-b\\-c&0&a\\b&-a&0\end{pmatrix},\qquad
 a\ge b\ge c\ge0,
\tag{1}
\]

and use the raw vectors

\[
 u_0=(1,-s,-z)^T,\qquad n_0=(1,-s,z)^T,\qquad
 s=c+\sqrt{1+c^2},\qquad z=b+\sqrt{1+b^2}.
\tag{2}
\]

The normalized vectors are \(u=u_0/\|u_0\|\) and
\(n=n_0/\|u_0\|\).  For \(|E|=|J|=2\), define the raw determinant gap

\[
 \Gamma_{EJ}=\|u_{0,E}\|_2^2\det(I+K_{E,J}^TK_{E,J})
 -v_{EJ}^T\operatorname{adj}(I+K_{E,J}^TK_{E,J})v_{EJ},
\quad v_{EJ}=n_{0,J}+K_{E,J}^Tu_{0,E}.
\tag{3}
\]

Positivity of \(I+K_{E,J}^TK_{E,J}\) shows that
\(\Gamma_{EJ}\ge0\) is exactly the desired proper polar inequality.

Set

\[
 h=s-1,\qquad j=z-s,\qquad d=a-b,\qquad D=2sz,
\tag{4}
\]

so \(h,j,d\ge0\).  The JSON record for each \(E|J\) is the exact
identity

\[
 D^4\Gamma_{EJ}=s^{\alpha_{EJ}}z^{\beta_{EJ}}
 \sum_{p,q,r\ge0}c^{EJ}_{pqr}h^pj^qd^r.
\tag{5}
\]

The record lists every nonzero \((p,q,r,c^{EJ}_{pqr})\) in lexicographic
monomial order \((h,j,d)\).  Every listed coefficient is a positive
integer.  Since \(s,z,D>0\), (5) proves every proper-gap inequality by a
finite exact identity.

The common factors and coefficient counts grouped by the power of \(d\)
are as follows.  Rows and columns use support labels \(12,13,23\).

\[
 \begin{array}{c|ccc}
 E\backslash J&12&13&23\\ \hline
 12&0&s^3z^2[24,18]&s^2z^2[34,22]\\
 13&s^2z^2[34,22]&s^4z^2[27]&s^3z^2[34,21]\\
 23&s^2z^2[39,30]&s^3z^2[41,33,19]&s^5z^2[27,21,14,10]
 \end{array}.
\tag{6}
\]

For example, the entry \(s^3z^2[24,18]\) means that the factored
polynomial has 24 positive \(h,j\) monomials at \(d^0\) and 18 at \(d^1\).
Thus the coefficient file has 470 positive monomials in total, rather than
the larger expansion before common factors are removed.

The following compact table gives the raw gaps directly.  Let
\(\gamma=\sqrt{1+c^2}\), \(\beta=\sqrt{1+b^2}\), and \(d=a-b\).
Rows and columns are ordered as \(12,13,23\):

\[
\begin{pmatrix}
0&2a\gamma\beta&2\gamma\{as(\gamma\beta-bc)+c(s\gamma+bz)\}\\
2\gamma\{2bz\gamma+a(b+z)\}&4bz(1+b^2)&2\beta\{az(\gamma\beta-bc)+b(z\beta+cs)\}\\
\gamma^2(z^2-s^2)+2bs\gamma z+2as\gamma(bs+z\gamma)&R&4asz(1+a^2)
\end{pmatrix},
\tag{7}
\]

where

\[
\begin{aligned}
R={}&4bzd^2+2z\{\gamma+(s+4)b^2+bcz\}d+b^2(s^2+z^2-2)\\
&+2bz\gamma(1+s)+2sb^3z+2b^2cz^2.
\end{aligned}
\tag{8}
\]

Every entry in (7)--(8) is nonnegative: \(z\ge s\ge1\),
\(\gamma>c\), \(\beta>b\), and therefore
\(\gamma\beta-bc>0\).  Thus this table alone proves all nine proper
conditions.  The JSON coefficient list remains a reproducible finite
identity check for the six dense off-diagonal expansions.

There is also a short unscaled identity that checks the matrix convention.
For every real \(2\times2\) matrix \(A\), with matching vectors \(u,n\),

\[
 \begin{aligned}
 &\|u\|_2^2\det(I+A^TA)-(n+A^Tu)^T\operatorname{adj}(I+A^TA)(n+A^Tu)\\
 &\quad=\|u\|_2^2-\|n\|_2^2+\|\operatorname{adj}(A)u\|_2^2
 -\|\operatorname{adj}(A)^Tn\|_2^2
 -2u^T\bigl(A+\det(A)\operatorname{adj}(A)^T\bigr)n.
 \end{aligned}
\tag{9}
\]

For the principal pairs, (7) gives exactly

\[
 \Gamma_{12,12}=0,\qquad
 \Gamma_{13,13}=4bz(1+b^2),\qquad
 \Gamma_{23,23}=4asz(1+a^2).
\tag{10}
\]

For the off-diagonal pair \(E=12,J=13\), put
\(\gamma=s-c=\sqrt{1+c^2}\) and
\(\beta=z-b=\sqrt{1+b^2}\).  Then

\[
 v_{12,13}=(s\gamma,\beta-as)^T,\qquad
 I+K_{12,13}^TK_{12,13}=
 \begin{pmatrix}\gamma^2&-ac\\-ac&\beta^2+a^2\end{pmatrix},
\tag{11}
\]

whose determinant is \(\gamma^2\beta^2+a^2\).  Using
\(s(\gamma-c)=1\), direct cancellation in (9) gives

\[
 \Gamma_{12,13}=2a\gamma\beta\ge0.
\tag{12}
\]

Equation (9) derives the table by six direct two-by-two expansions; equation
(12) shows one of them in detail.  Equation (5), with the attached complete
coefficient list, is an independent finite identity check for that table.
