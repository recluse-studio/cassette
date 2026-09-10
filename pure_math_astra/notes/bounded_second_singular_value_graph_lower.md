# A graph-chart lower bound from the second singular value

Status: proved for \(k\ge2\).  This is a coordinate-chart statement for real rank-\(k\)
projectors on \(\mathbb R^{2k}\).  It uses the existing rank-one finite
polar lemma and makes no claim for arbitrary coordinate changes.

Let \(k\ge2\), and let \(P\) be a rank-\(k\) orthogonal projector.  Select a max-volume
coordinate chart, so that after a coordinate permutation

\[
\operatorname{range}P=\operatorname{range}
\begin{pmatrix}I_k\\ Z\end{pmatrix},
\qquad \lVert Z\rVert_{\rm op}\le k. \tag{1}
\]

For \(0<r\le1\), put \(K=Z^T/r\).  Suppose

\[
\sigma_2(K)\le C. \tag{2}
\]

Then

\[
\boxed{
\Psi_k\bigl(P+r^2(I-P)\bigr)
\ge {r\over
4(1+C)^2\sqrt{k}(k^2+2)(1+k^2)(1+2k^2)}.}
\tag{3}
\]

## Singular-value truncation

Take a best rank-one singular-value truncation \(K_0\) of \(K\).  This
means that \(K_0\) retains a largest singular component; when \(K=0\),
take \(K_0=0\).  The operator-norm version of Eckart--Young gives

\[
\lVert K-K_0\rVert_{\rm op}=\sigma_2(K)\le C. \tag{4}
\]

Define

\[
Z_0=rK_0^T,\qquad
\operatorname{range}P_0=\operatorname{range}
\begin{pmatrix}I_k\\Z_0\end{pmatrix}. \tag{5}
\]

Then \(P_0\) is a rank-\(k\) orthogonal projector, \(\operatorname{rank}Z_0\le1\), and

\[
\lVert Z-Z_0\rVert_{\rm op}
=r\lVert K-K_0\rVert_{\rm op}\le Cr,\qquad
\lVert Z_0\rVert_{\rm op}\le\lVert Z\rVert_{\rm op}\le k. \tag{6}
\]

No max-volume property of the chart of \(P_0\) is required.  In the
rank-one graph proof, max volume is used only to obtain the displayed norm
bound; the same proof applies to any graph chart satisfying
\(\lVert Z_0\rVert\le k\).

## Graphs are one-Lipschitz in their slope

For two graphs over the same first coordinate space, let \(S_Z\) and
\(S_{Z_0}\) denote their ranges.  For \(v=(x,Zx)\in S_Z\),

\[
\operatorname{dist}(v,S_{Z_0})
\le\|(0,(Z-Z_0)x)\|
\le\lVert Z-Z_0\rVert_{\rm op}\,\|v\|. \tag{7}
\]

Taking the supremum over unit \(v\in S_Z\) bounds the largest sine of a
principal angle.  Equal-dimensional subspaces have the same largest sine
in either direction, and this sine equals the norm of the difference of
orthogonal projectors.  Therefore

\[
\lVert P-P_0\rVert_{\rm op}
\le\lVert Z-Z_0\rVert_{\rm op}
\le Cr. \tag{8}
\]

This uses a coordinate permutation only.  Such a permutation preserves the
hard coordinate-support model and the value of \(\Psi_k\); it is not an
invariance under a general orthogonal basis change.

## Transfer of the rank-one lower bound

For any orthogonal projector \(Q\),

\[
G_r(Q)^{1/2}=rI+(1-r)Q. \tag{9}
\]

By (8), for every \(x\),

\[
\begin{aligned}
\|G_r(P_0)^{1/2}x\|
&\le\|G_r(P)^{1/2}x\|+(1-r)\|P_0-P\|\|x\|\\
&\le(1+C)\|G_r(P)^{1/2}x\|,
\end{aligned} \tag{10}
\]

because \(G_r(P)\succeq r^2I\).  Hence

\[
G_r(P_0)\preceq(1+C)^2G_r(P). \tag{11}
\]

The verified rank-one graph lower bound, applied to \(P_0\) using (6), is

\[
\Psi_k(G_r(P_0))\ge
{r\over4\sqrt{k}(k^2+2)(1+k^2)(1+2k^2)}. \tag{12}
\]

Metric monotonicity of the exact-mean hard-support infimum and (11) give
\(\Psi_k(G_r(P))\ge(1+C)^{-2}\Psi_k(G_r(P_0))\), which is (3).

## Consequence for a vanishing ratio

Let \(r_\ell\downarrow0\), and choose a max-volume graph chart for each
\(P_\ell\), with \(K_\ell=Z_\ell^T/r_\ell\).  If

\[
\Psi_k\bigl(G_{r_\ell}(P_\ell)\bigr)/r_\ell\longrightarrow0,
\tag{13}
\]

then \(\sigma_2(K_\ell)\to\infty\).  Indeed, a subsequence with
\(\sigma_2(K_\ell)\le C\) would contradict the positive lower constant
in (3).  The same argument says more precisely that no choice of
max-volume chart can retain a bounded second singular value along such a
subsequence.
