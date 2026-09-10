# A rank-two partial-monomial subcase of the finite three-polar lemma

Status: proved subcase.  This note verifies all finite polar constraints for
a coordinate-separated rank-at-most-two family.  It does not prove the
finite lemma for arbitrary rank-two \(3\times3\) matrices, whose correlated
row and column factors remain open.

## Statement

Let

\[
 K=\sum_{h=1}^m\kappa_h e_{r_h}e_{c_h}^T,\qquad m\le2,
\tag{1}
\]

where the active row indices \(r_h\) are distinct and the active column
indices \(c_h\) are distinct.  Thus \(K\) is a partial monomial matrix of
rank at most two, allowing arbitrary real coefficients and zero rows or
columns.  There are vectors \(u,n\in\mathbb R^3\) with

\[
 \|u\|_2=1,\qquad \|n\|_2={1\over\sqrt3},
\tag{2}
\]

that satisfy every finite polar condition

\[
 (n_J+K_{E,J}^Tu_E)^T
 (I+K_{E,J}^TK_{E,J})^{-1}
 (n_J+K_{E,J}^Tu_E)
 \le\|u_E\|_2^2
\tag{3}
\]

for \(E,J\subseteq[3]\) with \(|E|=|J|\).  Hence this class has
\(\rho_3=1/\sqrt3\).

## Proof

Choose a column \(c_0\) outside \(\{c_1,\ldots,c_m\}\), which exists
because \(m\le2\), and set

\[
 u={1\over\sqrt3}(1,1,1)^T,\qquad n={1\over\sqrt3}e_{c_0}.
\tag{4}
\]

Fix \(E,J\) of common cardinality \(j\).  The nonzero coordinates of
\(K_{E,J}^Tu_E\) occur exactly at the active columns \(c_h\) for which

\[
 r_h\in E,\qquad c_h\in J.
\tag{5}
\]

Call their number \(q(E,J)\).  Because the active rows and columns are
distinct, \(K_{E,J}^TK_{E,J}\) is diagonal.  Therefore the left side of
(3) is

\[
 {1_{\{c_0\in J\}}\over3}
 +\sum_{\substack{h:\ r_h\in E,\ c_h\in J}}
 {\kappa_h^2\over3(1+\kappa_h^2)}.
\tag{6}
\]

If \(c_0\notin J\), then \(q(E,J)\le j\), and (6) is at most
\(j/3=\|u_E\|_2^2\).  If \(c_0\in J\), only \(j-1\) remaining columns
of \(J\) can be active.  Hence \(q(E,J)\le j-1\), and (6) is again at
most

\[
 {1+q(E,J)\over3}\le{j\over3}=\|u_E\|_2^2.
\tag{7}
\]

The \(j=0\) condition is void.  This proves (3).

The proof is stable under independent permutations of high and low
coordinates.  It includes rank-one and zero-matrix limits, but it relies on
disjoint active rows and columns.  It does not control an arbitrary rank-two
factorization \(K=AB^T\), where distinct active columns can share row
mass and the diagonal reduction in (6) is unavailable.
