# Necessary escape conditions for a collapsing rank-two graph sequence

Status: proved as a necessary-condition result.  It does not construct a
collapsing sequence or prove a uniform lower bound over all rank-two graph
charts.

Fix \(k=3\).  Let \(r_\ell\downarrow0\), and let \(P_\ell\) be real
rank-three orthogonal projectors on \(\mathbb R^6\).  For each \(\ell\),
choose a max-volume coordinate chart

\[
\operatorname{range}P_\ell=\operatorname{range}
\begin{pmatrix}I_3\\Z_\ell\end{pmatrix},
\qquad \|Z_\ell\|_{\rm op}\le3,
\qquad K_\ell={Z_\ell^T\over r_\ell}. \tag{1}
\]

Assume \(\operatorname{rank}K_\ell=2\), and suppose

\[
{\Psi_3(P_\ell+r_\ell^2(I-P_\ell))\over r_\ell}\longrightarrow0.
\tag{2}
\]

Then all three conditions below are necessary:

\[
\min_{j\in[3]}\|(K_\ell)_{:,j}\|_2\longrightarrow\infty,
\qquad \sigma_2(K_\ell)\longrightarrow\infty, \tag{3}
\]

and the normalized directions \(D_\ell=K_\ell/\|K_\ell\|_{\rm op}\)
approach the nongeneric rank-two boundary.  More precisely, with

\[
\mathcal B=
\left\{D:\|D\|_{\rm op}=1,\quad
\operatorname{rank}D\le1\ \text{or}\ D_{ij}=0\ \text{for some }i,j
\ \text{or}\ \det D_{E,J}=0\ \text{for some }|E|=|J|=2\right\}, \tag{4}
\]

one has

\[
\operatorname{dist}(D_\ell,\mathcal B)\longrightarrow0. \tag{5}
\]

The distance may be taken in any fixed finite-dimensional matrix norm.

## Bounded columns and second singular values

If the first limit in (3) failed, then after passing to a subsequence and
fixing a column index, one column of \(K_\ell\) would have norm at most a
fixed \(C\).  The bounded-column finite-polar lemma supplies a witness
with null norm at least

\[
\rho(C)={1\over10(\sqrt{1+C^2}+C)}. \tag{6}
\]

The graph-chart lower transfer uses only this witness norm and
\(\|Z_\ell\|\le3\); it gives a positive lower bound for the ratio in
(2), depending on \(C\) but not on \(\ell\).  This contradicts (2).
The same finite-union argument over three columns proves the first limit in
(3).

The second limit is the singular-value truncation discriminator in
`bounded_second_singular_value_graph_lower.md`.  A subsequence with
\(\sigma_2(K_\ell)\le C\) is within \(Cr_\ell\), at the projector level,
of a rank-one graph chart.  The rank-one graph lower then again gives a
positive lower bound for (2).  These two arguments use coordinate
permutations only; no general orthogonal change of the hard coordinate
support model is invoked.

## Compact generic directions

Suppose instead that (5) failed.  After a subsequence,
\(\operatorname{dist}(D_\ell,\mathcal B)\ge\varepsilon>0\).  The
operator-norm unit sphere is compact.  Intersect the closed
positive-distance set with the closed condition \(\operatorname{rank}D\le2\):

\[
F=\{D:\|D\|_{\rm op}=1,\ \operatorname{rank}D\le2,
\ \operatorname{dist}(D,\mathcal B)\ge\varepsilon\}. \tag{7}
\]

It contains the subsequence.  Since \(\mathcal B\) includes every
rank-at-most-one matrix, every member of \(F\) has rank two; its positive
distance from the remaining pieces of \(\mathcal B\) makes every entry
and every two-by-two minor nonzero.  Thus \(F\) is a compact subset of the generic direction set
\(\mathcal G\) in `generic_rank_two_compact_direction_uniformity.md`.

The second limit in (3) implies \(\|K_\ell\|_{\rm op}\to\infty\).  Write

\[
K_\ell=t_\ell D_\ell,\qquad t_\ell=\|K_\ell\|_{\rm op}. \tag{8}
\]

The compact-direction theorem provides one \(T_F\) such that, for all
large \(\ell\), the finite three-polar inequalities for \(K_\ell\) have
witnesses with \(\|n\|\ge1/2\).  The graph reduction transfers this to

\[
\Psi_3(P_\ell+r_\ell^2(I-P_\ell))
\ge {r_\ell\over
2\cdot4(3^2+2)(1+3^2)(1+2\cdot3^2)}
={r_\ell\over16720}. \tag{9}
\]

contrary to (2).  Its comparison constant is controlled by
\(\|Z_\ell\|\le3\), not by \(\|K_\ell\|\); therefore the arbitrarily
large dilation \(t_\ell\) does not weaken the lower bound (9).

## Boundary

Equations (3)--(5) are only an escape filter.  They leave open sequences
that simultaneously have every column norm and their second singular value
diverge while their normalized directions approach a zero-entry,
zero-minor, or rank-one boundary stratum.  Nothing here says that such a
sequence attains a small ratio in (2).
