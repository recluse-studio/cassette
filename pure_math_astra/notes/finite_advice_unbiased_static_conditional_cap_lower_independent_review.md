# Independent review: finite advice lower bound under a static expected read cap

Verdict: the stated extension is correct in the declared isotropic Stiefel
model. Let \(p>q\ge2\) and \(0<s<q\). In each of at most \(N\) source-selected states,
let a fixed, source- and query-independent distribution choose a subset
\(S\subseteq\{1,\ldots,q\}\) with \(\mathbb E|S|\le s<q\). If the
output depends only on the state, \(A_S\), and the query, has a
source-independent Borel internal random law, is exactly unbiased for
every source and query, and has uniform squared risk at most \(C\), then

\[
 \boxed{\quad
 C\ge\left(\frac qs-1\right)
 \min\left\{1,\left(\frac2N\right)^{2/(p-q)}\right\}.
 \quad}
\]

This includes a hard cap \(|S|\le s\) as a special case. It is a
correctness review only; it makes no originality or application
significance finding.

## Reduction to one missing coordinate

For one fixed state, let

\[
 \theta_j=\mathbb P(j\in S).
\]

The fixed support law and \(\mathbb E|S|\le s\) give

\[
 \sum_{j=1}^q\theta_j=\mathbb E|S|\le s.
\]

Choose \(j\) with \(\theta=\theta_j\le s/q<1\). Write
\(a=a_j\), and let \(W=A_{-j}\) be the ordered remaining \(q-1\)
columns.

First average the Borel internal output kernel over its independent seed.
For the coordinate query \(e_j\), average the resulting deterministic
outputs over support outcomes in the two events \(j\in S\) and \(j\notin
S\). Call the two conditional means \(F(A)\) and \(H(W)\), respectively.
The second function depends on \(W\) alone: every support in its mixture
omits \(j\), so its legal observed columns are among the columns of \(W\).
This remains true for overlapping supports and for the empty support. No
visibility assertion about \(F\) is required.

Exactness gives

\[
 \theta F(A)+(1-\theta)H(W)=a.
 \tag{1}
\]

If \(\theta=0\), (1) would determine \(a\) from \(W\). Conditional on
\(W\), however, \(a\) is uniform on \(S^{p-q}\subset W^\perp\), a
nonatomic sphere because \(p>q\). Thus this state cell is null. A finite
union of states with such a selected coordinate is still null.

For \(0<\theta<1\), Jensen first within each support outcome and then
within the two groups yields, at every frame in the state cell,

\[
 \begin{aligned}
 R(A,e_j)
 &\ge\theta\|F(A)-a\|^2+(1-\theta)\|H(W)-a\|^2\\
 &=\frac{1-\theta}{\theta}\|H(W)-a\|^2.
 \end{aligned}
 \tag{2}
\]

The equality follows from (1). Therefore the uniform risk bound confines
all frames of the cell to

\[
 \|a-H(W)\|
 \le\sqrt{\frac{C\theta}{1-\theta}}
 \le\sqrt{\frac{C}{q/s-1}}=:\delta.
 \tag{3}
\]

## Conditional cap estimate

Suppose \(C<q/s-1\), so \(\delta<1\). Conditional on the ordered frame
\(W\), \(a\) is uniform on the unit sphere \(S^{p-q}\) in \(W^\perp\).
For any centre in that ambient space, a Euclidean ball of radius
\(\delta<1\) meets this sphere in normalized measure at most

\[
 \frac12\delta^{p-q}.
 \tag{4}
\]

Projecting the centre \(H(W)\) to \(W^\perp\) can only decrease its
distance to \(a\), so (4) applies even though \(H(W)\) need not lie in
\(W^\perp\). Equation (3), followed by Fubini for the uniform Stiefel
law in the order \((W,a)\), gives the state-cell bound

\[
 \mu(E_\ell)\le
 \frac12\left(\frac{C}{q/s-1}\right)^{(p-q)/2}.
 \tag{5}
\]

The encoder's state cells cover the Stiefel manifold. After discarding the
finite null union from \(\theta=0\), summing (5) proves

\[
 1\le\frac N2
 \left(\frac{C}{q/s-1}\right)^{(p-q)/2}.
 \tag{6}
\]

When \(C\ge q/s-1\), the boxed conclusion is immediate. When
\(C<q/s-1\), rearranging (6) gives its second term. This also covers
\(C=0\), for which every nondegenerate cell has zero conditional measure.

## Scope checks

The proof permits arbitrary Borel nonlinear decoders and any fixed subset
law inside each finite state. It uses an expected-read cap, so it is at
least as broad as a per-outcome hard cap. It requires the state-specific
support distribution to be independent of the source and query. A
source-dependent support law inside a single state, query-dependent
selection, encoded pages that reveal information about omitted columns, or
uncharged source-dependent decoder state are outside this statement.

A state-specific fixed right basis \(Q_\ell\) is harmless: replace the
source by \(AQ_\ell\) and use original query \(Q_\ell e_j\). Right
Stiefel invariance preserves each cell's measure before the finite sum.

The excluded endpoint \(s=0\) has no finite-risk exactly unbiased
decoder in this model: all supports are empty almost surely, so every
state would determine a missing column from the remaining frame and hence
have null Stiefel measure.
