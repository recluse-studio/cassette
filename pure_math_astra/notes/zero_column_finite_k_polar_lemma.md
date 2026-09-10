# A uniform finite-polar witness when one column vanishes

For every real \(k\times k\) matrix with a zero column, the finite \(k\)-polar lemma holds with

\[
\rho_k=\binom{2k-1}{k}^{-1}.
\tag{1}
\]

This includes singular matrices of every rank. The bound is uniform in all remaining entries and holds at every scale. It is a subcase of the [finite graph system](rank_k_graph_chart_reduction.md), not a proof of that system for arbitrary matrices. The signed-sum ingredient is the equal-weight form of Bang's lemma, as stated in Lemma 5 of [Ball's primary paper](https://discovery.ucl.ac.uk/id/eprint/12546/1/12546.pdf). [The source comparison](../research/zero_column_polar_signed_sum_prior_work.md) records that precedent. The construction below is a short application of established techniques and does not by itself establish the substantive original advance required by the goal.

## A finite separation lemma

Let \(w_1,\ldots,w_L\) be unit vectors in a real Euclidean space. Choose signs \(\sigma_i\in\{-1,1\}\) maximizing

\[
\left\|v\right\|^2,
\qquad v=\sum_{i=1}^L\sigma_i w_i.
\tag{2}
\]

A maximizer exists because there are finitely many sign choices. Flipping sign \(i\) cannot increase the squared norm, so

\[
\|v-2\sigma_iw_i\|^2-\|v\|^2
=4-4\sigma_iw_i^Tv\le0.
\tag{3}
\]

Thus \(\sigma_iw_i^Tv\ge1\) for every \(i\), in particular \(v\ne0\). Since \(\|v\|\le L\), the unit vector \(u=v/\|v\|\) satisfies

\[
|w_i^Tu|\ge\frac1{\|v\|}\ge\frac1L
\qquad(1\le i\le L).
\tag{4}
\]

Repeated or dependent normals cause no difficulty.

## One normal for each relevant square submatrix

Let \(K\in\mathbb R^{k\times k}\), and suppose its column \(j_0\) is zero. For every pair \(E,J\subseteq[k]\) with

\[
|E|=|J|=j\ge1,\qquad j_0\in J,
\tag{5}
\]

put \(B=K_{E,J}\). Its rank is at most \(j-1\). Choose a unit vector \(w_{EJ}\in\mathbb R^k\), supported on \(E\), whose restriction to \(E\) is orthogonal to the column space of \(B\). Such a vector exists because that column space is a proper subspace of \(\mathbb R^E\).

The number of pairs in (5) is

\[
L=\sum_{j=1}^k\binom kj\binom{k-1}{j-1}
=\binom{2k-1}{k}.
\tag{6}
\]

For the identity, choose \(k\) elements from two disjoint sets of sizes \(k\) and \(k-1\). Taking \(j\) elements from the first leaves \(k-j\) from the second, with \(\binom{k-1}{k-j}=\binom{k-1}{j-1}\).

Apply (2)--(4) to these \(L\) normals. The resulting unit \(u\) satisfies

\[
\operatorname{dist}\bigl(u_E,\operatorname{range}B\bigr)
\ge |w_{EJ}^Tu|\ge1/L
\tag{7}
\]

for every pair in (5). Set

\[
n=L^{-1}e_{j_0}.
\tag{8}
\]

## Verification of every finite-polar constraint

For any equally sized \(E,J\), again write \(B=K_{E,J}\). We must prove

\[
(n_J+B^Tu_E)^T(I+B^TB)^{-1}(n_J+B^Tu_E)
\le\|u_E\|^2.
\tag{9}
\]

If \(j_0\notin J\), then \(n_J=0\), and

\[
B(I+B^TB)^{-1}B^T\preceq I
\tag{10}
\]

proves (9). The empty support is void.

If \(j_0\in J\), then \(Bn_J=0\). Consequently

\[
(I+B^TB)^{-1}n_J=n_J,
\qquad
n_J^T(I+B^TB)^{-1}B^Tu_E=0.
\tag{11}
\]

The left side of (9) is exactly

\[
L^{-2}+u_E^TB(I+B^TB)^{-1}B^Tu_E.
\tag{12}
\]

The singular values of \(B(I+B^TB)^{-1}B^T\) on \(\operatorname{range}B\) are \(\sigma^2/(1+\sigma^2)\le1\), and it vanishes on the orthogonal complement. Thus (12) is at most

\[
L^{-2}+\|\operatorname{proj}_{\operatorname{range}B}u_E\|^2
\le\|u_E\|^2,
\tag{13}
\]

where the last inequality is (7). This proves (9) for every support, including singular proper submatrices and full support. Equations (4) and (8) give \(\|u\|=1\), \(\|n\|=1/L\), proving (1).

## Scope of the result

For \(k=3\), the constant is \(\rho_3=1/10\). No dilation threshold, nonzero-minor assumption, or rank-two assumption is needed. The zero column must be exact: a small nonzero column need not leave \(n_J\) in \(\ker B\), so the cancellation in (11) cannot be carried unchanged into a perturbation argument.

This proof does not give a corresponding zero-row theorem by transposition. Transposing the finite-polar expression does not preserve the same inequality after merely exchanging \(u\) and \(n\). The next section replaces exact kernel cancellation with a Schur-complement bound and thereby includes a bounded nonzero column.

## Extension: one bounded column, with every other column arbitrary

The following Schur-complement argument extends the construction beyond an exact zero column. Fix any column \(j_0\) of an arbitrary real \(K\), and suppose \(\|K_{:,j_0}\|\le C\). Then a finite-polar witness exists with

\[
\|u\|=1,\qquad
\|n\|=\frac{1}{L(\sqrt{1+C^2}+C)}.
\tag{14}
\]

For each pair (5), remove the distinguished column from \(K_{E,J}\), leaving a matrix \(D\) with \(j\) rows and \(j-1\) columns. Choose the normal \(w_{EJ}\) orthogonal to \(\operatorname{range}D\). The same signed-sum argument gives a common unit \(u\) whose distance from every such range is at least \(c=1/L\).

Write \(b=K_{E,j_0}\) and \(R=(I+DD^T)^{-1}\). Set

\[
U=u_E^TRu_E,\qquad B=b^TRb,\qquad m=b^TRu_E.
\tag{15}
\]

The distance construction and contraction of \(R\) imply

\[
U\ge c^2,\qquad 0\le B\le C^2,\qquad |m|\le\sqrt{UB}.
\tag{16}
\]

Take \(n=\tau e_{j_0}\). Schur-complementing \(I+D^TD\) in the polar matrix gives the exact identity

\[
\begin{aligned}
&(n_J+K_{E,J}^Tu_E)^T
(I+K_{E,J}^TK_{E,J})^{-1}
(n_J+K_{E,J}^Tu_E)\\
&\qquad=\|u_E\|^2-U+\frac{(\tau+m)^2}{1+B}.
\end{aligned}
\tag{17}
\]

Thus the support constraint is precisely \(|\tau+m|\le\sqrt{U(1+B)}\). Its interval of legal \(\tau\) contains the symmetric interval of radius

\[
\begin{aligned}
\sqrt{U(1+B)}-|m|
&\ge\sqrt U(\sqrt{1+B}-\sqrt B)\\
&\ge\frac{c}{\sqrt{1+C^2}+C}.
\end{aligned}
\tag{18}
\]

Choose \(\tau\) equal to the final positive quantity, independently of the support. Every constraint with \(j_0\in J\) now holds by (17)--(18). Constraints omitting \(j_0\) retain \(n_J=0\) and follow from (10). This proves (14), including all singular submatrices.

No entry or norm of any other column appears in (14). The column attaining \(C=\min_j\|K_{:,j}\|\) gives the strongest bound of this form. It supplies a uniform norm floor for every family with one uniformly bounded column, even when all other columns diverge. The unrestricted finite lemma remains open because this floor tends to zero when every column norm tends to infinity.
