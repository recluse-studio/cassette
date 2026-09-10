# Independent review: bounded-column finite-polar extension

Verdict: Equations (14)--(18) of
`zero_column_finite_k_polar_lemma.md` are correct.  They prove the finite
polar lemma for every real \(k\times k\) matrix having one column with
Euclidean norm at most \(C\), with witness norm

\[
\lVert n\rVert_2={1\over L(\sqrt{1+C^2}+C)},
\qquad L=\binom{2k-1}{k}. \tag{1}
\]

The result is uniform over every other column.  It includes \(C=0\), when
it recovers the earlier exact-zero-column construction.

## Common direction

Fix the bounded column \(j_0\).  For each nonempty equal-size pair
\(E,J\) with \(j_0\in J\), remove column \(j_0\) from
\(K_{E,J}\), leaving \(D\in\mathbb R^{j\times(j-1)}\).  A unit normal
in \(\mathbb R^E\) to \(\operatorname{range}D\) exists, including when
\(j=1\), where \(D\) has no columns.  Extending these normals by zero
outside \(E\), the signed-sum lemma supplies one unit \(u\in\mathbb R^k\)
with

\[
\operatorname{dist}(u_E,\operatorname{range}D)\ge c={1\over L} \tag{2}
\]

for every such pair.  Repeated normals, nonunique normals, and a
higher-dimensional orthogonal complement do not change that argument:
one unit normal is selected for each of the finitely many pairs.

## Exact Schur-complement calculation

Permute the columns in \(J\), only within this calculation, so that
\(K_{E,J}=[D\ b]\), where \(b=K_{E,j_0}\).  Put

\[
R=(I+DD^T)^{-1},\quad U=u_E^TRu_E,\quad
B=b^TRb,\quad m=b^TRu_E. \tag{3}
\]

The distance in (2) lies in \(\ker D^T\).  Since \(R\) is the identity
there and has eigenvalues in \((0,1]\),

\[
U\ge c^2. \tag{4}
\]

Also \(0\le B\le\lVert b\rVert_2^2\le C^2\), and Cauchy--Schwarz in
the positive inner product induced by \(R\) gives

\[
|m|\le\sqrt{UB}. \tag{5}
\]

For \(n=\tau e_{j_0}\), set \(x=D^Tu_E\) and
\(y=b^Tu_E+\tau\).  Block inversion at
\(A=I+D^TD\) has Schur complement

\[
1+b^Tb-b^TDA^{-1}D^Tb=1+b^TRb=1+B. \tag{6}
\]

Moreover \(DA^{-1}D^T=I-R\).  Thus the polar quadratic form is exactly

\[
\begin{aligned}
&\begin{pmatrix}x\\y\end{pmatrix}^T
\left(I+[D\ b]^T[D\ b]\right)^{-1}
\begin{pmatrix}x\\y\end{pmatrix}\\
&\quad=u_E^T(I-R)u_E+
 {\left(y-b^TDA^{-1}x\right)^2\over1+B}\\
&\quad=\lVert u_E\rVert_2^2-U+{(\tau+m)^2\over1+B}. \tag{7}
\end{aligned}
\]

This confirms both the sign and the transpose in Eq. (17).

The constraint is therefore equivalent to

\[
|\tau+m|\le\sqrt{U(1+B)}. \tag{8}
\]

Its permitted interval contains \([-r,r]\), where

\[
r=\sqrt{U(1+B)}-|m|
\ge\sqrt U(\sqrt{1+B}-\sqrt B)
\ge {c\over\sqrt{1+C^2}+C}. \tag{9}
\]

The last step uses that \(b\mapsto\sqrt{1+b}-\sqrt b\) decreases for
\(b\ge0\) and \(B\le C^2\).  Hence the common positive choice

\[
\tau={c\over\sqrt{1+C^2}+C} \tag{10}
\]

works simultaneously for every support containing \(j_0\).  Supports
omitting it have \(n_J=0\) and follow from
\(D(I+D^TD)^{-1}D^T\preceq I\), with \(D\) there replaced by their whole
support block.

## Scope

No bound on other columns enters the proof.  The result requires an actual
upper bound \(C\) on one full column, so a family qualifies only when the
same \(C\) applies throughout the family.  This argument does not prove a
uniform lower norm floor when all column norms diverge.
