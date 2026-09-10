# A fixed large-ray finite-polar witness when one row is zero

Status: proved for the stated generic fixed direction.  The threshold below
may depend on the direction; this note supplies no uniform threshold as the
nonzero entries or the two-by-two minors approach zero.

Let

\[
K_0=\begin{pmatrix}R\\0\;0\;0\end{pmatrix}\in\mathbb R^{3\times3},
\qquad R\in\mathbb R^{2\times3}, \tag{1}
\]

where every entry of \(R\) and every two-by-two minor of \(R\) is nonzero.
In particular, \(R\) has row rank two.  For a fixed column \(j\), write
\(r=R_{:,j}\), choose

\[
a={1\over2\lVert r\rVert_2},\qquad
u_{\rm top}=-ar,\qquad
u_3={\sqrt3\over2},\qquad
n={1\over2}e_j. \tag{2}
\]

Thus \(u=(u_{\rm top},u_3)\) has norm one and \(\lVert n\rVert_2=1/2\).
I prove that \(u,n\) obey every finite-polar constraint for \(tK_0\), for
all sufficiently large \(t\).  Explicitly, for all equal-cardinality
\(E,J\subseteq[3]\), the required inequality is

\[
(n_J+tK_{0,E,J}^{T}u_E)^T
(I+t^2K_{0,E,J}^{T}K_{0,E,J})^{-1}
(n_J+tK_{0,E,J}^{T}u_E)
\le \lVert u_E\rVert_2^2. \tag{3}
\]

This is the finite-polar system in
`rank_k_graph_chart_reduction.md`, specialized to \(k=3\).

## Scalar constraints

For \(i\in\{1,2\}\) and the selected column \(j\), put
\(\kappa=(K_0)_{ij}=r_i\ne0\).  Since \(u_i=-a\kappa\), the difference
between the right side of (3), after multiplication by its positive
denominator, and the left numerator is

\[
a^2\kappa^2(1+t^2\kappa^2)-\left({1\over2}-ta\kappa^2\right)^2
=a^2\kappa^2-{1\over4}+ta\kappa^2. \tag{4}
\]

It is positive for all sufficiently large \(t\).  For \(i\in\{1,2\}\)
and \(j'\ne j\), \(n_{j'}=0\), so the left side equals

\[
{t^2(K_0)_{ij'}^2u_i^2\over1+t^2(K_0)_{ij'}^2}\le u_i^2. \tag{5}
\]

For the zero third row, the left side is \(n_{j'}^2\), which is at most
\(1/4<u_3^2=3/4\).

## Two-by-two constraints

First let \(E=\{1,2\}\), and let \(B=K_{0,E,J}\).  The minor assumption
makes every such \(B\) invertible.  If \(j\in J\), the selected column of
\(B\) is \(r\), in coordinates on \(J\), and the standard inverse
expansion gives

\[
\begin{aligned}
 &(n_J+tB^Tu_{\rm top})^T(I+t^2B^TB)^{-1}
 (n_J+tB^Tu_{\rm top})\\
 &\quad=\lVert u_{\rm top}\rVert_2^2+
 {2\over t}u_{\rm top}^TB^{-T}n_J+O(t^{-2})\\
 &\quad={1\over4}-{a\over t}+O(t^{-2}). \tag{6}
\end{aligned}
\]

Here the last equality is exact in its \(t^{-1}\) coefficient:

\[
u_{\rm top}^TB^{-T}n_J
=(-aBe_j)^TB^{-T}\left({1\over2}e_j\right)=-{a\over2}. \tag{7}
\]

The coordinate \(e_j\) in (7) means the position of the selected original
column inside \(J\); no unlicensed transpose replacement is used.  Thus
(3) holds strictly for all large \(t\).  If \(j\notin J\), then \(n_J=0\)
and the left side is strictly below \(\lVert u_{\rm top}\rVert_2^2\) at
all finite \(t\), because each singular-value multiplier
\(t^2\sigma^2/(1+t^2\sigma^2)\) is below one.

Now let \(E=\{i,3\}\) with \(i\in\{1,2\}\).  Write the nonzero row of
\(K_{0,E,J}\) as \(v\).  Decomposition of \(n_J\) into the span of
\(v^T\) and its orthogonal complement shows that the left side of (3)
converges to

\[
u_i^2+\lVert P_{\ker v}n_J\rVert_2^2
\le u_i^2+{1\over4}
<u_i^2+u_3^2=\lVert u_E\rVert_2^2. \tag{8}
\]

The entry hypothesis ensures \(v\ne0\), so the displayed limit applies.
Hence these six constraints also hold strictly for all large \(t\).

## Full constraint and conclusion

For \(E=J=[3]\), rank two of \(R\) gives the singular-value limit

\[
\lim_{t\to\infty}
(n+tK_0^Tu)^T(I+t^2K_0^TK_0)^{-1}(n+tK_0^Tu)
=\lVert u_{\rm top}\rVert_2^2+\lVert P_{\ker R}n\rVert_2^2
\le {1\over2}<1. \tag{9}
\]

The empty constraint is void.  The finite number of scalar, two-by-two,
and full constraints, together with their strict eventual gaps above,
yields a finite \(T(K_0)\) such that (3) holds for every \(t\ge T(K_0)\).

Consequently, every generic rank-two \(3\times3\) direction with exactly
one zero row has a large-ray finite-polar witness of null norm \(1/2\).
The argument uses invertibility of the top two-row two-by-two blocks only
in (6).  A direction with a zero top entry or a vanishing top two-row minor
requires a separate argument; it is not covered by continuity at a fixed,
unquantified threshold.
