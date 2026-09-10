# Coordinate-preserving reduction to the skew three-polar family

Status: a negative reduction result.  Coordinate-support-preserving
isometries carry the finite polar system to itself, but they cannot send a
general real rank-two \(3\times3\) matrix to the all-skew family.  This does
not disprove the finite three-polar lemma.

## 1. The exact symmetries of the finite system

Write \(\mathcal P(K;u,n)\) for the collection of inequalities

\[
 (n_J+K_{E,J}^T u_E)^T
 (I+K_{E,J}^TK_{E,J})^{-1}
 (n_J+K_{E,J}^Tu_E)\leq\|u_E\|_2^2
 \tag{1}
\]

over all \(E,J\subseteq[3]\) with \(|E|=|J|\).  Let \(U,V\) be signed
permutation matrices and put

\[
 K'=UKV^T,\qquad u'=Uu,\qquad n'=Vn. \tag{2}
\]

Then

\[
 \mathcal P(K;u,n)\quad\Longleftrightarrow\quad
 \mathcal P(K';u',n'). \tag{3}
\]

Indeed, a signed permutation maps every row set \(E\) and column set
\(J\) bijectively to sets \(E'\) and \(J'\) of the same cardinality.
Restricted signed permutations are orthogonal, so the left side of (1) and
the right side agree after conjugation.  In particular, (2) preserves both
\(\|u\|_2\) and \(\|n\|_2\).

This is the usable exact coordinate symmetry.  More generally, an
invertible linear map that preserves every vector's support cardinality
must be monomial: its action on each coordinate
axis is another coordinate axis, and invertibility forces those axes to be
distinct.  Thus support preservation does not admit an SVD rotation.

Non-unit diagonal factors are not exact symmetries of (1).  The obstruction
already occurs in one scalar box:

\[
 \frac{(n+\kappa u)^2}{1+\kappa^2}\leq u^2. \tag{4}
\]

Replacing \(\kappa\) by \(d\kappa\) changes the coefficient of \(u^2\)
after the Schur complement.  Even allowing scalar rescalings
\(u\mapsto\alpha u\), \(n\mapsto\beta n\), equality of the two quadratic
forms for all \(u,n\) would require

\[
 \frac{d^2}{1+d^2\kappa^2}=\frac1{1+\kappa^2},
\]

and hence \(d^2=1\).  Bounded diagonal conditioning can bound a *different*
metric, but it supplies neither an equivalence of (1) nor an automatic
transfer of a uniform polar constant.

## 2. A zero-pattern obstruction

Every nonzero real skew \(3\times3\) matrix has three prescribed zero
positions, its diagonal.  Signed permutations only move signs and rows or
columns, so a matrix that is signed-permutation equivalent to a skew matrix
must have a zero in each member of some row-column perfect matching.

The rank-two matrix

\[
 K_0=\begin{pmatrix}1&1&1\\1&2&3\\1&3&5\end{pmatrix} \tag{5}
\]

has determinant zero, since \(1(10-9)-(5-3)+(3-2)=0\), and has rank two
because its upper-left \(2\times2\) minor equals one.  It has no zero
entry.  Therefore no independent signed row and column permutations can
carry \(K_0\) to an all-skew matrix.  The same is true after arbitrary
nonzero diagonal row and column scalings: such scalings preserve the support
pattern.

This is not an isolated counterexample.  The rank-at-most-two variety in
\(\mathbb R^{3\times3}\) has dimension eight, while the all-skew family

\[
 \begin{pmatrix}0&c&-b\\-c&0&a\\b&-a&0\end{pmatrix} \tag{6}
\]

has dimension three.  The finite collection of signed row-column relabelings
does not change that dimension.  In particular, no exact
coordinate-support-preserving isometric reduction can cover a relatively
open subset of rank-two matrices.

## 3. Graph-chart pivots do not repair the reduction

Changing the maximum-volume graph pivot in the \(6\)-coordinate projector
problem is useful for bounding a graph matrix.  It is not a support-preserving
linear equivalence of the finite system (1): it changes which three original
coordinates are called high and replaces the graph parameter by a rational
chart transition.  There are only finitely many such pivots.

On every overlap, a pivot transition is an analytic coordinate map on the
Grassmann chart.  Requiring the resulting graph matrix to lie in the
three-dimensional skew family imposes a proper algebraic condition.  A finite
union of these proper conditions cannot contain the eight-dimensional
rank-two locus in the original graph chart.  Thus pivot selection can improve
conditioning, as in `rank_k_graph_chart_reduction.md`, but cannot generally
turn the unresolved finite three-polar problem into the skew case.

## 4. The remaining coordinate normal form

After independent row and column permutations, any rank-two matrix with a
nonzero \(2\times2\) minor has the exact support-respecting factorization

\[
 K=
 \begin{pmatrix}
 A&A x\\
 y^T A&y^T A x
 \end{pmatrix},
 \qquad A\in\operatorname{GL}_2(\mathbb R),\quad x,y\in\mathbb R^2.
 \tag{7}
\]

Here \(x=A^{-1}K_{[2],3}\) and \(y^T=K_{3,[2]}A^{-1}\); the lower-right
entry follows from rank two.  This has the full eight parameters of the
generic rank-two locus.  It preserves the actual row and column supports,
unlike an SVD.

Consequently the next finite equation is not a skew reduction.  It is to
find \(u,n\), uniformly over \((A,x,y)\) in (7), for the nineteen explicit
conditions (1): nine scalar boxes, nine \(2\times2\) Schur inequalities,
and the full ellipsoid.  The all-skew certificate supplies a useful
three-parameter slice of this normal form, but diagonal entries and the two
independent correlation vectors \(x,y\) are genuine remaining variables.

The conclusion is narrow: a general rank-two proof needs an argument that
uses those variables directly, or a new support-preserving transformation
that changes more than the existing Euclidean finite system allows.
