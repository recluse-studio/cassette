# An exact square-root benchmark for the query-adaptive q=4, s=2 problem

Status: a proved calculation for one rotated eigenbasis.  It does not prove
that this basis minimizes the query-adaptive value over the full orthogonal
orbit.

Let \(0<\eta<1\), \(s=2\), and

\[
 G=\begin{pmatrix}G_0&0\\0&G_0\end{pmatrix},\qquad
 G_0=\frac12\begin{pmatrix}1+\eta&1-\eta\\1-\eta&1+\eta\end{pmatrix}.
\tag{1}
\]

Thus \(G\) has spectrum \((1,1,\eta,\eta)\).  It is obtained by applying
a \(45^\circ\) high--low rotation separately in coordinate pairs \(\{1,2\}\)
and \(\{3,4\}\).  In the notation of
`query_adaptive_atomic_dual.md`,

\[
 \Psi_2(G)=\sqrt\eta.
\tag{2}
\]

## Polar description

Put \(e_+=(1,1)/\sqrt2\), \(e_-=(1,-1)/\sqrt2\), and write a dual vector
in its two coordinate blocks as

\[
 u_{\{1,2\}}=r_1e_++\ell_1e_-,\qquad
 u_{\{3,4\}}=r_2e_++\ell_2e_-.
\tag{3}
\]

The polar of the two-sparse atom body consists exactly of the vectors that
satisfy

\[
 r_i^2+\frac{\ell_i^2}{\eta}\le1\quad(i=1,2),
\tag{4}
\]

and, from the four cross-block coordinate pairs,

\[
 (|r_1|+|\ell_1|)^2+(|r_2|+|\ell_2|)^2\le1+\eta.
\tag{5}
\]

Indeed, the two within-block principal matrices are \(G_0\).  Every cross
principal matrix is \(((1+\eta)/2)I_2\).  Maximizing the resulting four
cross inequalities over their independent signs gives (5).

For \(v=\sqrt\eta\), set \(e=\sqrt\eta\),
\(x_i=|r_i|\), \(y_i=|\ell_i|/e\), and
\(A=\sum_i x_i^2\), \(B=\sum_i y_i^2\).  Equations (4)--(5) imply

\[
 A+B\le2,\qquad A+e^2B\le1+e^2.
\tag{6}
\]

The second implication merely drops the nonnegative cross term in (5).
Taking \(e/(1+e)\) times the first inequality and \(1/(1+e)\) times the
second gives

\[
 A+eB\le1+e.
\tag{7}
\]

Since \(G+eI\) has eigenvalues \(1+e\) on the two \(e_+\) modes and
\(e^2+e=e(1+e)\) on the two \(e_-\) modes, (7) is precisely

\[
 u^*(G+eI)^{-1}u
 =\frac{e\sum_i r_i^2+\sum_i\ell_i^2}{e(1+e)}\le1.
\tag{8}
\]

The ellipsoid--atom-body equivalence therefore gives \(\Psi_2(G)\le e\).

## Sharp witness

Take one high unit mode in the first block and a scaled low unit mode in the
second:

\[
 u=e_+\oplus e\,e_-.
\tag{9}
\]

It obeys (4) with equality in both blocks.  Each cross-pair constraint is
also an equality, because its squared norm is \((1+\eta)/2\).  Thus \(u\)
lies in the polar body.  Any \(v\) for which the ellipsoid containment holds
must consequently satisfy

\[
 1\ge u^*(G+vI)^{-1}u
   =\frac1{1+v}+\frac\eta{\eta+v}.
\tag{10}
\]

After clearing positive denominators, (10) is equivalent to \(v^2\ge\eta\).
This proves the reverse inequality in (2).

## What remains invariantly open

For an arbitrary rank-two projector \(P\),
\(G=P+\eta(I-P)\), the same polar test is

\[
 \max_{|S|=2}u_S^*G_{SS}^{-1}u_S\le1.
\tag{11}
\]

The sharp witness (9) relies on its high and low modes occupying different
coordinate blocks while each cross principal matrix is scalar.  A generic
two-plane has no such coordinate separation.  A proof of
\(\Psi_2(P+\eta(I-P))\ge c\sqrt\eta\) uniformly in \(P\), or a basis family
with \(o(\sqrt\eta)\), must control (11) for every two-plane.  Equation (2)
only establishes the upper candidate \(\inf_P\Psi_2\le\sqrt\eta\); it is
not a global lower bound.

## The singular-minor reduction for a possible global lower bound

Let \(P\) be any real rank-two orthogonal projector and write
\(G_\eta=P+\eta(I-P)\).  If every two-coordinate principal block obeys

\[
 P_{SS}\succeq\delta I_2\qquad(|S|=2),
\tag{12}
\]

then the value has the stronger fixed-basis obstruction

\[
 \Psi_2(G_\eta)\ge\delta-\eta.
\tag{13}
\]

For a unit \(f\in\ker P\), every polar quadratic form is at most
\(1/\delta\) at \(f\), because \(G_{\eta,SS}\succeq P_{SS}\succeq\delta I\).
Hence \(\sqrt\delta f\) is polar feasible.  Ellipsoid containment gives
\(\delta/(\eta+v)\le1\), which is (13).  Thus a basis family with
\(\Psi_2(G_\eta)\to0\) must approach the locus where a coordinate
two-minor of \(P\) is singular.

This locus has a short exact Plucker classification.  Choose an oriented
orthonormal frame \(E\in\mathbb R^{4\times2}\) for the range of \(P\), and
put

\[
 p_{ij}=\det(E_{i,:},E_{j,:}).
\tag{14}
\]

Then

\[
 \det P_{\{i,j\},\{i,j\}}=p_{ij}^2,
 \qquad
 p_{12}p_{34}-p_{13}p_{24}+p_{14}p_{23}=0.
\tag{15}
\]

More concretely, \(p_{ij}=0\) exactly when the two coordinate rows of
\(E\) are parallel.  The zero-minor graph is therefore a union of cliques
of parallel-row classes, with a zero row adjacent to every vertex.  Up to
permutation, the possible rank-two patterns are: no zero edge; \(2+1+1\);
\(2+2\); \(3+1\); one zero row with three distinct directions; one zero row
with a \(2+1\) split; and two zero rows with two nonparallel remaining
rows.  The last is the coordinate eigenbasis stratum; the \(2+2\) stratum
contains (1).

Consequently a uniform square-root proof may be reduced to these finite
singular types plus quantitative control as a plane approaches one type.
The calculation above settles only one symmetric point of the \(2+2\)
stratum.
