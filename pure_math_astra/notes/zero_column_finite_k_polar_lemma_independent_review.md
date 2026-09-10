# Independent review: a zero column gives a uniform finite \(k\)-polar witness

Verdict: the proposed zero-column lemma is correct.  It requires no rank
assumption on \(K\).  Its constant depends only on \(k\), not on the
nonzero entries of \(K\).

Let \(K\in\mathbb R^{k\times k}\) have a zero column \(j_0\).  Put

\[
 L=\binom{2k-1}{k},\qquad c={1\over L}.
 \tag{1}
\]

Then there are \(u,n\in\mathbb R^k\) satisfying

\[
 \|u\|_2=1,\qquad\|n\|_2=c,
 \tag{2}
\]

and, for every equally sized \(E,J\subseteq[k]\),

\[
 (n_J+K_{E,J}^Tu_E)^T(I+K_{E,J}^TK_{E,J})^{-1}
 (n_J+K_{E,J}^Tu_E)\leq\|u_E\|_2^2.
 \tag{3}
\]

## 1. The finite family of orthogonal directions

Index a family by all pairs \((E,J)\) with

\[
 |E|=|J|=r,\qquad j_0\in J,\qquad 1\leq r\leq k.
 \tag{4}
\]

For one such pair, \(B=K_{E,J}\) has a zero column, so

\[
 \operatorname{rank}B\leq r-1.
 \tag{5}
\]

Choose a unit \(w_{EJ}\in\mathbb R^k\), supported on \(E\), whose
restriction to \(E\) is orthogonal to \(\operatorname{range}(B)\subseteq
\mathbb R^E\).  Such a vector exists by (5).  The number of pairs is

\[
 \sum_{r=1}^k\binom{k}{r}\binom{k-1}{r-1}
 =\binom{2k-1}{k}=L,
 \tag{6}
\]

by Vandermonde's identity.

Write these unit vectors as \(w_1,\ldots,w_L\).  Choose signs
\(\sigma_a\in\{-1,1\}\) that maximize

\[
 \left\|v\right\|_2^2,\qquad v=\sum_{a=1}^L\sigma_aw_a.
 \tag{7}
\]

Flipping only the \(a\)-th sign cannot increase (7).  Since

\[
 \|v\|_2^2-\|v-2\sigma_aw_a\|_2^2
 =4\bigl(\sigma_aw_a^Tv-1\bigr),
 \tag{8}
\]

maximality gives

\[
 \sigma_aw_a^Tv\geq1\qquad(a=1,\ldots,L).
 \tag{9}
\]

In particular \(v\ne0\).  The triangle inequality gives
\(\|v\|_2\leq L\), hence, for \(u=v/\|v\|_2\),

\[
 |w_a^Tu|={\sigma_aw_a^Tv\over\|v\|_2}\geq {1\over L}=c
 \qquad(a=1,\ldots,L).
 \tag{10}
\]

Set

\[
 n=ce_{j_0}. \tag{11}
\]

This proves (2).

## 2. Blocks that contain the zero column

Fix \(E,J\) from (4), and write \(B=K_{E,J}\).  In the coordinates of
\(J\), the component \(n_J\) equals \(ce_{j_0}\).  Because the original
\(j_0\)-th column of \(K\) vanishes,

\[
 Bn_J=0. \tag{12}
\]

Let \(R=(I+B^TB)^{-1}\).  Equation (12) gives \(Rn_J=n_J\), while
\(n_J^TRB^Tu_E=0\).  Therefore the left side of (3) is exactly

\[
 c^2+u_E^TB(I+B^TB)^{-1}B^Tu_E.
 \tag{13}
\]

The second matrix in (13) is bounded by the orthogonal projector onto the
column range of \(B\):

\[
 B(I+B^TB)^{-1}B^T\preceq P_{\operatorname{range}(B)}.
 \tag{14}
\]

The selected \(w_{EJ}\) is a unit vector orthogonal to that range.  By
(10),

\[
 \operatorname{dist}(u_E,\operatorname{range}(B))
 \geq |w_{EJ}^Tu|\geq c.
 \tag{15}
\]

Thus (13)--(15) yield

\[
 \begin{aligned}
 c^2+u_E^TB(I+B^TB)^{-1}B^Tu_E
 &\leq c^2+\|P_{\operatorname{range}(B)}u_E\|_2^2\\
 &\leq\|u_E\|_2^2,
 \end{aligned}
 \tag{16}
\]

which is (3) for every block containing \(j_0\).  This includes full
support and singleton blocks; it also permits \(B=0\).

## 3. Blocks that omit the zero column

If \(j_0\notin J\), then \(n_J=0\).  For any square block
\(B=K_{E,J}\),

\[
 \begin{aligned}
 &(tB^Tu_E)^T(I+t^2B^TB)^{-1}(tB^Tu_E)\\
 &=u_E^T\bigl[t^2B(I+t^2B^TB)^{-1}B^T\bigr]u_E
 \leq\|u_E\|_2^2
 \end{aligned}
 \tag{17}
\]

for every \(t\geq0\), since the bracket has eigenvalues
\(s^2t^2/(1+s^2t^2)\in[0,1]\).  Taking \(t=1\) proves (3).  The empty
block is void.

## Scope

The proof is uniform across the zero-column stratum in the precise sense
that \(c=1/\binom{2k-1}{k}\) depends only on the dimension \(k\).  It does
not assert an optimal constant, a result for matrices with no zero column,
or a new sign-sum principle.  The sign choice in (7)--(10) is an elementary
finite balancing argument; this note makes no novelty claim about it.
