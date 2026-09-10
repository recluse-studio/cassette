# Query-adaptive sparse sampling as an atomic norm

Status: an exact positive-definite reformulation of the query-adaptive
problem. It gives no novelty claim and does not resolve the basis-optimized
ratio.

Let \(G\succ0\) be real symmetric or complex Hermitian, and define

\[
 \Psi_s(G)=
 \sup_{\|x\|_2=1}
 \inf_{\substack{\mathbb EY=x\\\|Y\|_0\le s\ {\rm a.s.}}}
 \mathbb E (Y-x)^*G(Y-x).
\tag{1}
\]

The mean constraint in (1) is exactly \(\mathbb EY=x\). It must not be
weakened to \(R\mathbb EY=Rx\), even when \(G=R^*R\) is later allowed to be
singular.

## 1. Exact convex program for one query

Let

\[
 \mathcal A_s(G)=
 \{y:\|y\|_0\le s,\ y^*Gy\le1\},\qquad
 \mathcal K_s(G)=\operatorname{conv}\mathcal A_s(G),
\tag{2}
\]

and let \(\gamma_{s,G}\) be the gauge of the symmetric convex body
\(\mathcal K_s(G)\). Then

\[
 \inf_{\substack{\mathbb EY=x\\\|Y\|_0\le s}}
 \mathbb E Y^*GY
 =\gamma_{s,G}(x)^2.
\tag{3}
\]

Indeed, if \(Y\) is any legal estimator, write
\(a=Y/\sqrt{Y^*GY}\) on the nonzero event. Then
\(\gamma_{s,G}(x)\le\mathbb E\sqrt{Y^*GY}\), so Jensen gives the lower
bound in (3). Conversely, an atomic representation
\(x=\lambda\sum_j\alpha_j a_j\), with
\(\lambda=\gamma_{s,G}(x)\), \(\alpha_j\ge0\), \(\sum_j\alpha_j=1\), and
\(a_j\in\mathcal A_s(G)\), is realized by \(Y=\lambda a_j\) with
probability \(\alpha_j\). Its second moment is at most \(\lambda^2\).

Consequently

\[
 \Psi_s(G)=
 \max_{\|x\|_2=1}\left[
 \gamma_{s,G}(x)^2-x^*Gx
 \right].
\tag{4}
\]

For fixed \(x\), the gauge is the finite SOCP

\[
 \gamma_{s,G}(x)=
 \min_{\substack{x=\sum_{|S|\le s}z_S\\
                 \operatorname{supp}z_S\subseteq S}}
 \sum_{|S|\le s}\sqrt{z_S^*G_{SS}z_S}.
\tag{5}
\]

Its dual norm is

\[
 \gamma_{s,G}^*(u)=
 \max_{|S|\le s}\sqrt{u_S^*G_{SS}^{-1}u_S}.
\tag{6}
\]

Equations (4)--(6) are an exact computable representation: (5) is a
finite, though exponentially indexed, SOCP. The outer maximum in (4) is
not generally convex.

## 2. Diagonal spectra attain the spectral water level

Let \(D=\operatorname{Diag}(a_i)\succ0\), and let \(t=t_s(D)\) solve

\[
 \sum_i\frac{a_i}{a_i+t}=s.
\tag{7}
\]

An exact-size HT law with marginals \(p_i=a_i/(a_i+t)\) has covariance
\(tI\), so \(\Psi_s(D)\le t\).

For the reverse inequality, put

\[
 x_i=\frac{\sqrt{a_i}/(a_i+t)}
 {\left(\sum_j a_j/(a_j+t)^2\right)^{1/2}},
\qquad
 u_i=\frac{\sqrt{a_i}}{\sqrt s}.
\tag{8}
\]

The vector \(u\) is dual feasible in (6), because every set \(S\) of at
most \(s\) coordinates has
\(\sum_{i\in S}u_i^2/a_i\le1\). Thus

\[
 \gamma_{s,D}(x)^2\ge
 \frac{s}{\sum_i a_i/(a_i+t)^2}.
\]

Subtracting \(x^*Dx\) gives exactly \(t\), since

\[
 \sum_i\frac{a_i}{a_i+t}
 -\sum_i\frac{a_i^2}{(a_i+t)^2}
 =t\sum_i\frac{a_i}{(a_i+t)^2}.
\tag{9}
\]

Therefore

\[
 \Psi_s(D)=t_s(D).
\tag{10}
\]

In particular, for a fixed spectrum,

\[
 \inf_{V\in O(q)\ {\rm or}\ U(q)}
 \Psi_s(V^*DV)\le t_s(D).
\tag{11}
\]

## 3. What the representation does and does not bound

For a fixed non-eigenbasis, \(\Psi_s(G)/t_s(G)\) can be arbitrarily large.
For example, take \(s=1\) and

\[
 G_\eta=\mathbf1\mathbf1^*+\eta I,\qquad\eta>0.
\]

Its spectral water level satisfies

\[
 t_1(G_\eta)\sim\sqrt{q(q-1)\eta}
\quad(\eta\downarrow0).
\tag{12}
\]

In the displayed coordinate basis, choose a balanced sign vector when
\(q\) is even. The \(s=1\) formula from (4) gives
\(\Psi_1(G_\eta)\ge q+O(\eta)\). Hence the fixed-basis ratio diverges.
Diagonalizing \(G_\eta\) restores equality in (10). This example does not
answer the optimized-basis question.

The atomic representation gives no present proof that

\[
 \inf_V\Psi_s(V^*DV)\ge c\,t_s(D)
\tag{13}
\]

for a dimension-free \(c>0\), nor a counterexample making the ratio tend
to zero. A vanishing-ratio construction would need sparse unbiased
estimators that suppress the expensive eigenspace for every query. A
dimension-free lower bound would need a vector \(x\) that defeats every
such query-dependent atomic decomposition. Both are global statements
about the body \(\mathcal K_s(G)\), and neither follows from the
fixed-operator transform cover.

The positive-definite assumption is essential to (5)--(6). If \(G\) is
singular, the atomic set in (2) is unbounded in null directions and the
gauge can be degenerate. That limit requires a separate formulation with
the full mean constraint in (1); it cannot be justified by replacing it
with equality after applying \(R\).
