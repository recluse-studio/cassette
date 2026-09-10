# Orthogonality averaging is compact, and common values are atomic

Status: proved.  This is a measure-theoretic restriction on positive-measure
matching under one orthogonality step.  It does not by itself prove a
finite-advice or water-level theorem.

Let \(p\ge3\), let \(\sigma\) be normalized surface measure on
\(S^{p-1}\), and define

\[
 (T\varphi)(a)=\int_{S^{p-1}\cap a^\perp}\varphi(b)\,d\sigma_a(b),
 \tag{1}
\]

where \(\sigma_a\) is normalized measure on the equatorial sphere.  Thus
\((a,b)\) has the uniform ordered Stiefel-two-frame law exactly when
\(a\sim\sigma\) and \(b\) is sampled by (1).

## The compactness of \(T\)

The Stiefel law is invariant under swapping \(a,b\), so \(T\) is a
self-adjoint contraction on \(L^2(\sigma)\).

Fix \(a\), first sample \(b\perp a\), then sample \(a'\perp b\).  With
\(t=a^Ta'\), the conditional density of \(t\) is proportional to

\[
 (1-t^2)^{(p-4)/2},\qquad -1<t<1,
 \tag{2}
\]

because it is one coordinate of a uniform point on \(S^{p-2}\).  For a
uniform \(a'\in S^{p-1}\), the corresponding density is proportional to

\[
 (1-t^2)^{(p-3)/2}. \tag{3}
\]

Consequently

\[
 (T^2\varphi)(a)=\int_{S^{p-1}}k(a^Ta')\varphi(a')\,d\sigma(a'),
 \qquad
 k(t)={C_p\over\sqrt{1-t^2}},
 \tag{4}
\]

for a positive normalization constant \(C_p\).  The kernel is integrable
against \(\sigma\).  At \(p=3\), its resulting one-dimensional density is
proportional to \((1-t^2)^{-1/2}\), which remains integrable at both
endpoints; larger \(p\) only improve that exponent.

Let \(k_M=\min\{k,M\}\), and let \(K_M\) be its integral operator.  Each
\(K_M\) is Hilbert--Schmidt, hence compact.  The positive tail has constant
row integral

\[
 \rho_M=\int(k-k_M)(a^Ta')\,d\sigma(a')\longrightarrow0.
 \tag{5}
\]

The same holds for column integrals, so Schur's bound gives

\[
 \|T^2-K_M\|_{2\to2}\le\rho_M\longrightarrow0.
 \tag{6}
\]

Therefore \(T^2\) is compact.  If \(x_m\rightharpoonup0\) in
\(L^2(\sigma)\), compactness makes \(T^2x_m\to0\) in norm; self-adjointness
then gives

\[
 \|Tx_m\|_2^2=\langle x_m,T^2x_m\rangle\longrightarrow0.
 \tag{7}
\]

Thus \(T\) is compact.

## Atomicity of a shared value

Let \(f,g:S^{p-1}\to\mathbb R^d\) be Borel, and let

\[
 \mu=f_\#\sigma,\qquad\nu=g_\#\sigma.
 \tag{8}
\]

For the uniform Stiefel pair \((a,b)\), define the matching measure

\[
 \eta(D)=\mathbb P\bigl(f(a)=g(b)\in D\bigr)
 \tag{9}
\]

on Borel \(D\subseteq\mathbb R^d\).  Then

\[
 \eta\bigl(\mathbb R^d\setminus
 (\operatorname{At}(\mu)\cap\operatorname{At}(\nu))\bigr)=0,
 \tag{10}
\]

where \(\operatorname{At}(\mu)=\{y:\mu\{y\}>0\}\), and likewise for
\(\nu\).  Each atom set is countable.

To prove (10), values that are atoms of \(\mu\) but not \(\nu\) contribute
zero: for each such \(y\),

\[
 \mathbb P(f(a)=g(b)=y)\le\mathbb P(g(b)=y)=0,
 \tag{11}
\]

and a countable union remains null.  The symmetric statement holds for
atoms of \(\nu\) that are not atoms of \(\mu\).

It remains to exclude a match in

\[
 D=\mathbb R^d\setminus
 (\operatorname{At}(\mu)\cup\operatorname{At}(\nu)).
 \tag{12}
\]

The finite measure \(\lambda=\mu|_D+\nu|_D\) is nonatomic.  For every
\(\delta>0\), nonatomic divisibility gives a finite measurable partition

\[
 D=D_1\mathbin{\dot\cup}\cdots\mathbin{\dot\cup}D_N,
 \qquad \lambda(D_i)\le\delta.
 \tag{13}
\]

Set \(A_i=f^{-1}(D_i)\) and \(B_i=g^{-1}(D_i)\).  If a diffuse match
occurs, it lies in one common cell, so

\[
 \mathbb P(f(a)=g(b)\in D)
 \le\sum_{i=1}^N\langle\mathbf1_{A_i},T\mathbf1_{B_i}\rangle.
 \tag{14}
\]

Fix \(\varepsilon>0\).  Compactness of \(T\) gives a finite-rank
operator

\[
 R=\sum_{m=1}^M u_m\otimes v_m,
 \qquad\|T-R\|_{2\to2}\le\varepsilon.
 \tag{15}
\]

The remainder in (14) is bounded by

\[
 \begin{aligned}
 \sum_i|\langle\mathbf1_{A_i},(T-R)\mathbf1_{B_i}\rangle|
 &\le\varepsilon\sum_i\sqrt{\mu(D_i)\nu(D_i)}\\
 &\le\varepsilon.
 \end{aligned}
 \tag{16}
\]

For a rank-one summand, Cauchy--Schwarz inside each cell gives

\[
 \sum_i|\langle\mathbf1_{A_i},u_m\rangle|
          |\langle v_m,\mathbf1_{B_i}\rangle|
 \le\|u_m\|_2\|v_m\|_2
 \sqrt{\max_i\mu(D_i)\max_i\nu(D_i)}.
 \tag{17}
\]

This tends to zero with \(\delta\), without any boundedness assumption on
the \(L^2\) factors.  Summing the finite family in (15), then sending
\(\delta\downarrow0\), makes the finite-rank part of (14) vanish.  Equation
(16) leaves at most \(\varepsilon\); since \(\varepsilon\) is arbitrary,
the diffuse matching probability is zero.  This proves (10).

## Scope

The proof uses standard compact-integral-operator and nonatomic-partition
methods.  It shows only that a positive-measure equality \(f(a)=g(b)\) can
occur at values that are atoms of both marginal value laws.  It does not
say that the functions are constant, that their images are finite, or that
finite resident advice follows from the matching restriction.
