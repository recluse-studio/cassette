# Scalar boxes and the full ellipsoid do not suffice at rank three

Status: exact counterexample to a shortcut in the finite rank-three polar
system. It does not refute the finite lemma, which may choose different
vectors u,n.

The rank-two proof checks scalar boxes and one full ellipsoid. At rank
three the proper two-by-two submatrix conditions add real restrictions.
Take

\[
 K=\begin{pmatrix}1&2&0\\1&2&0\\0&0&0\end{pmatrix},
 \qquad
 u=\frac1{\sqrt3}(-1,-1,1)^T,\qquad
 n=\frac1{\sqrt3}(1,0,0)^T.
\]

Here ||u||=1 and ||n||=1/sqrt(3). All nine scalar conditions

\[
 \frac{(n_j+K_{mj}u_m)^2}{1+K_{mj}^2}\le u_m^2
\]

hold. In column one, the two nonzero-row numerators vanish and the
third row is equality. In column two the normalized squared ratio is
4/5 on rows one and two, and zero on row three. Column three is zero.

For the full ellipsoid,

\[
 I+K^TK=
 \begin{pmatrix}3&4&0\\4&9&0\\0&0&1\end{pmatrix},
 \qquad n+K^Tu=\frac1{\sqrt3}(-1,-4,0)^T.
\]

The inverse of the leading block is

\[
 \frac1{11}\begin{pmatrix}9&-4\\-4&3\end{pmatrix}.
\]

Thus the full ellipsoid value is 25/33<1, so that test also passes.
But for E=J={1,2}, the same quadratic expression has value 25/33,
whereas its required right side is ||u_E||^2=2/3=22/33. It fails
by exactly 1/11.

Consequently the rank-three finite lemma cannot be established by
retaining only the nine scalar boxes and the full ellipsoid. A proof
must control its proper square-submatrix constraints as well. This
example preserves an exact obstruction for the next investigation.
