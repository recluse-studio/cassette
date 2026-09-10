# A sign-consistent inverse pivot exists for every generic rank-two \(3\times3\) matrix

Status: proved.  The term “sign-consistent inverse pivot” is used only in
this working note.  This is a sign lemma for the proposed asymptotic
construction; it does not by itself produce a finite-polar witness.

Let \(K\in\mathbb R^{3\times3}\) have rank two, with every entry and every
two-by-two minor nonzero.  Then some pivot \((i,j)\) has

\[
 K_{ij}K_{m\ell}
 \det K_{(i,m),(j,\ell)}>0
 \tag{1}
\]

for every \(m\ne i\) and \(\ell\ne j\).  The row and column orders in the
minor are exactly \((i,m)\) and \((j,\ell)\).  Equivalently, every inverse
diagonal entry of every two-by-two submatrix containing \((i,j)\) has the
same sign as \(K_{ij}\).

## 1. Factor and kernel normalization

Write \(K=AB^T\), with \(A,B\in\mathbb R^{3\times2}\).  For ordered
pairs of distinct indices,

\[
 \det K_{(i,m),(j,\ell)}
 =\det A_{(i,m),:}\det B_{(j,\ell),:}. \tag{2}
\]

This is the oriented Cauchy--Binet identity in rank two.  It explains the
oriented-matroid form of (1), but the following kernel normalization gives a
short proof.

Let \(g\ne0\) and \(h\ne0\) span respectively the left and right kernels:

\[
 g^TK=0,\qquad Kh=0. \tag{3}
\]

All coordinates of \(g\) and \(h\) are nonzero.  For example, a zero
coordinate of \(g\) would make the two rows complementary to it dependent,
contrary to the nonzero-minor hypothesis.  Set

\[
 M=\operatorname{diag}(g)K\operatorname{diag}(h). \tag{4}
\]

Then \(M\mathbf 1=0\) and \(\mathbf1^TM=0\).  Multiplication by arbitrary
nonzero diagonal row and column factors preserves the sign in (1), because
the total multiplier is

\[
 (g_i h_j g_m h_\ell)^2>0. \tag{5}
\]

This normalization is only a proof device for the sign lemma.  It is not an
isometry of the finite polar inequalities.

## 2. Three zero-sum sign tables

Every row and every column of \(M\) has both signs.  Replace \(M\) by
\(-M\), if needed, so that it has at most four positive entries.  It then
has either three or four positive entries.  With three, they form a perfect
matching.  With four, the positive bipartite graph has degree sequences
\((2,1,1)\) on both sides; its two degree-two vertices are either adjacent
or nonadjacent.  Thus row and column permutations, together with a global
sign, reduce the sign table to exactly one of

\[
 \begin{array}{c|c|c}
 \text{case}&\operatorname{sign}M&\text{valid pivot}\\ \hline
 A&\begin{pmatrix}-&-&+\\-&-&+\\+&+&-\end{pmatrix}&(1,2)\\[6pt]
 B&\begin{pmatrix}-&-&+\\-&+&-\\+&-&+\end{pmatrix}&(1,1)\\[6pt]
 C&\begin{pmatrix}-&-&+\\-&+&-\\+&-&-\end{pmatrix}&(1,3).
 \end{array} \tag{6}
\]

Let \(\Delta=\det M_{(1,2),(1,2)}\).  In cases \(B\) and \(C\), writing
the first four entries as \((-A,-B,-C,D)\), with \(A,B,C,D>0\), gives

\[
 \Delta=-AD-BC<0. \tag{7}
\]

In case \(A\), the interchange of columns one and two preserves the sign
table and reverses \(\Delta\), so we may also arrange \(\Delta<0\).
Because \(M\mathbf1=\mathbf1^TM=0\) and its rank is two,

\[
 \operatorname{adj}M=\Delta\,\mathbf1\mathbf1^T. \tag{8}
\]

Equation (8) fixes the sign of every ordered two-by-two minor from the sign
of \(\Delta\).  For completeness, substituting \(\Delta<0\) into the
four products in (1) gives

\[
 \begin{array}{c|c}
 \text{case and pivot}&
 \bigl(\operatorname{sign}[M_{ij}M_{m\ell}
 \det M_{(i,m),(j,\ell)}]\bigr)_{{m\ne i},{\ell\ne j}}\\ \hline
 A,(1,2)&\begin{pmatrix}+&+\\+&+\end{pmatrix}\\[5pt]
 B,(1,1)&\begin{pmatrix}+&+\\+&+\end{pmatrix}\\[5pt]
 C,(1,3)&\begin{pmatrix}+&+\\+&+\end{pmatrix}.
 \end{array} \tag{9}
\]

This is a four-sign verification in each of the three exhaustive cases.

Row and column permutations merely relabel the resulting pivot.  Equation
(5) transfers its four strict signs from \(M\) back to \(K\), proving
(1).

## 3. Consequence and boundary

For a two-by-two submatrix whose ordered rows and columns are
\((i,m)\) and \((j,\ell)\), its inverse entry at the pivot is

\[
\bigl(K_{(i,m),(j,\ell)}^{-1}\bigr)_{j,i}
 ={K_{m\ell}\over\det K_{(i,m),(j,\ell)}}. \tag{10}
\]

Thus (1) is exactly the requested common sign for all four proper inverse
diagonal terms.  It supplies the sign part of the proposed pivot-centered
asymptotic construction.  It does not control their magnitudes, the full
rank-two kernel inequality, or matrices on the excluded entry/minor-zero
strata.

## 4. The admissible pivots need not contain a perfect matching

The stronger matching statement is false.  Directly checking all nine
pivots in the three exhaustive sign tables of (6), with \(\Delta<0\), gives

\[
 \begin{array}{c|c}
 \text{case}&\{(i,j):\text{(1) holds}\}\\ \hline
 A&\{(1,2),(2,1)\}\\
 B&\{(1,1),(1,3),(3,1)\}\\
 C&\{(1,3),(2,2),(3,1)\}.
 \end{array} \tag{11}
\]

Only case \(C\) contains a perfect matching.  Case \(A\), for example,
is realized by

\[
 M=\begin{pmatrix}-1&-2&3\\-3&-4&7\\4&6&-10\end{pmatrix}. \tag{12}
\]

Its row and column sums vanish, its rank is two, and
\(\det M_{(1,2),(1,2)}=-2\).  Every entry and every two-by-two minor is
nonzero, while (11) gives only the two pivots \((1,2)\) and \((2,1)\).

The failure also defeats the proposed kernel-norm inference, rather than
merely the matching proof of it.  For \(0<\varepsilon<1\), define the
unit left and right kernel vectors

\[
 g_\varepsilon={(\varepsilon,\varepsilon,1)^T\over
 \sqrt{1+2\varepsilon^2}},\qquad
 h_\varepsilon={(1,1,\varepsilon)^T\over
 \sqrt{2+\varepsilon^2}}. \tag{13}
\]

Set

\[
 K_\varepsilon=
 \operatorname{diag}(g_\varepsilon)^{-1}M
 \operatorname{diag}(h_\varepsilon)^{-1}. \tag{14}
\]

Then \(g_\varepsilon^TK_\varepsilon=0\) and
\(K_\varepsilon h_\varepsilon=0\), because \(\mathbf1^TM=0\) and
\(M\mathbf1=0\).  Positive diagonal scaling preserves every entry and
minor sign, hence preserves the exact admissible-pivot set
\(\{(1,2),(2,1)\}\) from (12).  At both admissible pivots, the relevant
kernel-coordinate ratio is

\[
 { |g_{\varepsilon,1}|\over |h_{\varepsilon,2}|}
 ={ |g_{\varepsilon,2}|\over |h_{\varepsilon,1}|}
 =\varepsilon\sqrt{\frac{2+\varepsilon^2}
 {1+2\varepsilon^2}}\longrightarrow0. \tag{15}
\]

Thus an admissible generic rank-two pivot need not obey a uniform lower
bound of the form \(|g_i|\ge c|h_j|\) for unit kernel vectors.  The
sign-pivot lemma remains useful, but a uniform full-ellipsoid construction
must combine more than one pivot or use a different choice of its leading
coordinates.
