# Spectral-threshold limits for the fixed-projector support-event lower bound

Status: this note proves a uniform separated-stratum subcase and gives an
exact \(k=3\) family showing why a support classification by small singular
values does not justify the high-space event estimate used in that proof.
It does not disprove a uniform theorem obtained from additional finite
polar geometry.

Let \(P\) be a real rank-\(k\) projector on \(\mathbb R^{2k}\),
\(N=I-P\), and \(G_r=P+r^2N\). For a support \(S\), let

\[
\sigma_S=\sigma_{\min}(P|_{\mathbb R^S})
\]

when the restriction is injective.

## A proved separated-stratum subcase

Suppose there are fixed numbers \(\sigma_0,d_0>0\) such that

\[
\sigma_S\ge\sigma_0
\quad\text{for every injective support }S,\ |S|\le k, \tag{1}
\]

and there is a unit \(u\in\operatorname{range}P\) with

\[
\operatorname{dist}(u,P\mathbb R^S)\ge d_0
\quad\text{for every noninjective support }S,\ |S|\le k. \tag{2}
\]

Assume first that the noninjective-support family is nonempty. If it is
empty, every allowed output satisfies
\(\|NY\|\le\sigma_0^{-1}\|PY\|\). At a unit null query \(x=n\),
exact mean and Cauchy--Schwarz give
\[
1=\|\mathbb E NY\|\le
\sigma_0^{-1}(\mathbb E\|PY\|^2)^{1/2}.
\]
Its risk is therefore at least \(\sigma_0^2\), uniformly over this
class. This is stronger than \(\sigma_0^2r\) for \(r\le1\).

Then the support-event proof is uniform over this class:

\[
\Psi_k(P+r^2(I-P))\ge c(\sigma_0,d_0)\,r
\qquad(0<r\le1). \tag{3}
\]

Indeed, (1) gives \(\|Ny\|\le\sigma_0^{-1}\|Py\|\) on every
injective support. Set \(M=\max\{1,\sigma_0^{-1}\}\), choose any unit
\(n\in\ker P\), and put

\[
a=(1+16M^2)^{-1/2},\qquad b=4Ma,\qquad x=au+bn.
\]

The event split from the fixed-projector note gives, for every finite-risk
exact-mean output with risk \(V<a^2\),

\[
V^2+r^2b^2V\ge {r^2a^2d_0^2b^2\over4}. \tag{4}
\]

Writing \(w=V/r\), the positive root of

\[
w^2+b^2w={a^2d_0^2b^2\over4}
\]

is a positive lower bound for \(w\); the case \(V\ge a^2\) supplies the
other bound. This proves (3). It is a genuine uniform result only on the
separated class (1)--(2), not on its closure.

## The near-singular full-support obstruction

For \(k=3\), let

\[
U_\varepsilon={1\over\sqrt{1+\varepsilon^2}}
\begin{pmatrix}I_3\\ \varepsilon I_3\end{pmatrix},
\qquad
P_\varepsilon=U_\varepsilon U_\varepsilon^T,
\qquad \varepsilon>0. \tag{5}
\]

Take the low coordinate support \(L=\{4,5,6\}\). The restriction
\(P_\varepsilon|_{\mathbb R^L}\) is injective, has three equal singular
values

\[
{\varepsilon\over\sqrt{1+\varepsilon^2}}, \tag{6}
\]

and nevertheless satisfies

\[
P_\varepsilon\mathbb R^L=\operatorname{range}P_\varepsilon. \tag{7}
\]

For if \(u=U_\varepsilon w\), then

\[
y=(0,\;a\sqrt{1+\varepsilon^2}\,w/\varepsilon)^T\in\mathbb R^L
\quad\Longrightarrow\quad
P_\varepsilon y=au. \tag{8}
\]

Consequently, for every spectral threshold \(\tau>0\), choosing
\(\varepsilon<\tau\) produces a \(\tau\)-bad full support \(L\) on which
an arbitrary high component \(au\) can be realized with zero high
residual. No estimate of the form

\[
\Pr(Y\text{ uses a }\tau\text{-bad support})
\le {V\over a^2d^2} \tag{9}
\]

can follow from the high-space risk, because the required distance is zero.

This is not a counterexample to order \(r\). The kernel of \(P_\varepsilon\)
has the orthonormal basis

\[
{1\over\sqrt{1+\varepsilon^2}}
(-\varepsilon e_i+e_{i+3}),\qquad i=1,2,3,
\]

whose vectors are two-sparse. Thus it lies in the sparse-kernel branch of
the fixed-projector dichotomy. It is a counterexample only to the proposed
spectral classification of support events.

## The remaining threshold inequality

Let \(\mathcal G_\tau\) be the injective supports with
\(\sigma_S\ge\tau\), and let \(\mathcal B_\tau\) contain the other
supports. On \(\mathcal G_\tau\),

\[
\|Ny\|\le\tau^{-1}\|Py\|.
\]

For the mixed query \(x=au+bn\) and an arbitrary exact-mean output of risk
\(V\), this alone gives only

\[
\left\|\mathbb E[NY1_{\mathcal G_\tau}]\right\|
\le {a+\sqrt V\over\tau}. \tag{10}
\]

To force at least \(b/2\) of the null mean onto \(\mathcal B_\tau\), one
would need

\[
a+\sqrt V<{b\tau\over2}. \tag{11}
\]

At a target \(V=O(r)\) with \(b\) bounded below, (11) already requires
\(\tau\gtrsim\sqrt r\), even if \(a\) is negligible. But the family
(5)--(8) shows that the complementary \(\tau\)-bad full supports have no
universal high-space distance. Therefore this threshold split cannot
supply (9) with a positive distance independent of the projector.

One remaining approach is to use relations among the near-kernel
directions across several supports. The open finite \(k\)-polar system
of rank_k_graph_chart_reduction.md retains those relations.
