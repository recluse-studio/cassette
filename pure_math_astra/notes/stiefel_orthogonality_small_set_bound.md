# Small-set bound for equatorial averaging

Status: proved.  This is a quantitative consequence of the compactness
calculation for equatorial averaging.  It uses standard weak-Lorentz and
Cauchy--Schwarz arguments; it makes no originality claim.

Let \(p\ge3\), let \(\sigma\) be normalized surface measure on
\(S^{p-1}\), and let

\[
 (T\varphi)(a)=\int_{S^{p-1}\cap a^\perp}\varphi(b)\,d\sigma_a(b).
 \tag{1}
\]

The two-step operator has kernel

\[
 (T^2\varphi)(a)=\int_{S^{p-1}} k(a^Tb)\varphi(b)\,d\sigma(b),
 \qquad
 k(t)=\frac{C_p}{\sqrt{1-t^2}},
 \tag{2}
\]

where

\[
 C_p=
 \frac{\Gamma((p-1)/2)^2}
      {\Gamma((p-2)/2)\Gamma(p/2)}.
 \tag{3}
\]

Put

\[
 \alpha=\frac{p-2}{p-1},
 \qquad
 D_p=\frac{p-1}{p-2}C_p.
 \tag{4}
\]

Then every Borel \(B\subseteq S^{p-1}\) satisfies

\[
 \sup_{a\in S^{p-1}}\int_B k(a^Tb)\,d\sigma(b)
 \le D_p\,\sigma(B)^\alpha.
 \tag{5}
\]

Moreover, if \((A_i)\) and \((B_i)\) are finite or countable disjoint
families of Borel sets, with

\[
 \sum_i\sigma(A_i)\le1,\qquad
 \sum_i\sigma(B_i)\le1,\qquad
 \sup_i\sigma(B_i)\le h,
 \tag{6}
\]

then

\[
 \sum_i\langle\mathbf1_{A_i},T\mathbf1_{B_i}\rangle
 \le \sqrt{D_p}\,h^{\alpha/2}.
 \tag{7}
\]

The constant is bounded uniformly in dimension:

\[
 D_p\le\frac{p-1}{p-2}\le2.
 \tag{8}
\]

For \(p=3\), \(C_3=2/\pi\), \(D_3=4/\pi\), and (5) has the
endpoint exponent \(1/2\).

## Proof of the kernel small-set bound

Fix \(a\).  The coordinate \(t=a^Tb\) of a uniform \(b\) has density

\[
 c_p(1-t^2)^{(p-3)/2},
 \qquad
 c_p=\frac{\Gamma(p/2)}{\sqrt\pi\,\Gamma((p-1)/2)}.
 \tag{9}
\]

Let \(r=p-1\) and \(d=(C_p/\lambda)^2\).  If \(\lambda>C_p\), then
\(0<d<1\), and the \(k\)-superlevel set consists of the two caps
\(\lvert t\rvert>\sqrt{1-d}\).  With \(q=r/2=(p-1)/2\), its measure is

\[
 \begin{aligned}
 \sigma\{b:k(a^Tb)>\lambda\}
 &=c_p\int_0^d s^{q-1}(1-s)^{-1/2}\,ds\\
 &\le d^q=(C_p/\lambda)^r.
 \end{aligned}
 \tag{10}
\]

For the inequality, divide the integral by \(d^q\), substitute
\(s=du\), and observe that

\[
 c_p\int_0^1u^{q-1}(1-du)^{-1/2}\,du
\tag{11}
\]

increases with \(d\in(0,1]\) and equals one at \(d=1\), by the beta
integral.  If \(0<\lambda\le C_p\), the same upper bound in (10) is at
least one and is therefore automatic.  Thus \(k(a^T\cdot)\) has weak
\(L^r\) quasi-norm at most \(C_p\), uniformly in \(a\).

The decreasing rearrangement bound

\[
 k(a^T\cdot)^*(s)\le C_p s^{-1/r},\qquad0<s<1,
 \tag{12}
\]

and the layer-cake/rearrangement inequality now give

\[
 \int_B k(a^Tb)\,d\sigma(b)
 \le\int_0^{\sigma(B)}C_p s^{-1/r}\,ds
 =D_p\sigma(B)^{1-1/r}.
 \tag{13}
\]

This is (5).  Finally, log-convexity of \(\Gamma\), at the midpoint of
\((p-2)/2\) and \(p/2\), gives \(C_p\le1\), proving (8).

## Proof of the disjoint-cell estimate

The operator \(T\) is self-adjoint.  For each \(i\), Cauchy--Schwarz and
(2) give

\[
 \begin{aligned}
 \lvert\langle\mathbf1_{A_i},T\mathbf1_{B_i}\rangle\rvert
 &\le\sigma(A_i)^{1/2}
      \langle\mathbf1_{B_i},T^2\mathbf1_{B_i}\rangle^{1/2},\\
 \langle\mathbf1_{B_i},T^2\mathbf1_{B_i}\rangle
 &\le D_p\sigma(B_i)^{1+\alpha}
 \le D_p h^\alpha\sigma(B_i).
 \end{aligned}
 \tag{14}
\]

Applying Cauchy--Schwarz to the sum and using (6) yields

\[
 \begin{aligned}
 \sum_i\lvert\langle\mathbf1_{A_i},T\mathbf1_{B_i}\rangle\rvert
 &\le\Bigl(\sum_i\sigma(A_i)\Bigr)^{1/2}
      \Bigl(\sum_i\langle\mathbf1_{B_i},T^2\mathbf1_{B_i}\rangle\Bigr)^{1/2}\\
 &\le\sqrt{D_p}\,h^{\alpha/2}.
 \end{aligned}
 \tag{15}
\]

Monotone convergence extends the displayed calculation from finite to
countable families.  This proves (7).

## Scope

The exponent in (5) is the weak-\(L^{p-1}\) endpoint forced by the polar
singularity of (2).  The result bounds correlations of small disjoint
value cells.  It does not establish a lower bound for a particular
finite-advice, decoder, or variance model without an additional argument
that turns that model into families satisfying (6).
