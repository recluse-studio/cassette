# Unequal paired rotations at the square-root scale — exact polar reduction; depends on query_adaptive_atomic_dual.md, query_adaptive_q4_sqrt_eta_block.md.

Status: a proved asymptotic result for one rotated and one unrotated
two-coordinate block. It does not settle arbitrary two-planes.

Let \(r=\sqrt\eta\), let \(\theta=kr\) for fixed \(k\ge0\), and put

\[
 G_r=\operatorname{Diag}(H_r,D_r),\qquad
 D_r=\operatorname{Diag}(1,r^2),
\tag{1}
\]

where

\[
 H_r=
 \begin{pmatrix}c&-s\\s&c\end{pmatrix}
 \begin{pmatrix}1&0\\0&r^2\end{pmatrix}
 \begin{pmatrix}c&s\\-s&c\end{pmatrix}
 =\begin{pmatrix}A&C\\C&B\end{pmatrix},
\tag{2}
\]

with \(c=\cos\theta\), \(s=\sin\theta\),
\(A=c^2+r^2s^2\), and \(B=s^2+r^2c^2\). Thus only the first high/low
coordinate pair is rotated.

Then

\[
 r-{k\over2}r^2+O_k(r^3)\ \le\ \Psi_2(G_r)\ \le\ r.
\tag{3}
\]

In particular,

\[
 {\Psi_2(G_r)\over\sqrt\eta}\longrightarrow1
 \qquad(\eta\downarrow0).
\tag{4}
\]

The strict fixed-\(\eta\) eigenbasis reversal is consistent with (3): its
improvement can be lower order when the rotation itself is \(k\sqrt\eta\).

## 1. Exact two-scalar polar reduction

For a vector \(u=(v,w)\in\mathbb R^2\oplus\mathbb R^2\), define

\[
 \alpha(v)=\max\left\{{|v_1|\over\sqrt A},{|v_2|\over\sqrt B}\right\},
 \qquad
 \beta(w)=\max\left\{|w_1|,{|w_2|\over r}\right\}.
\tag{5}
\]

The polar of the two-sparse atom body is exactly the set of vectors obeying

\[
 v^TH_r^{-1}v\le1,\qquad
 w^TD_r^{-1}w\le1,\qquad
 \alpha(v)^2+\beta(w)^2\le1.
\tag{6}
\]

The first two inequalities come from the two within-block supports. The
four cross-block supports have diagonal principal Grams, and their four
inequalities are equivalent to the final maximum condition in (6).

For \(a\in[0,1]\), set

\[
 \begin{aligned}
 F_H(t,a)&=\max_{\substack{v^TH_r^{-1}v\le1\\\alpha(v)\le a}}
                  v^T(H_r+tI)^{-1}v,\\
 F_D(t,a)&=\max_{\substack{w^TD_r^{-1}w\le1\\\beta(w)\le a}}
                  w^T(D_r+tI)^{-1}w.
 \end{aligned}
\tag{7}
\]

Both functions are nondecreasing in \(a\). Hence the exact polar maximum
is

\[
 M_r(t)=\max_{0\le a\le1}
 \left[F_H(t,a)+F_D\left(t,\sqrt{1-a^2}\right)\right].
\tag{8}
\]

By atomic polarity,

\[
 \Psi_2(G_r)=\inf\{t\ge0:M_r(t)\le1\}.
\tag{9}
\]

This is already a one-scalar reduction once \(F_H\) is evaluated. That
remaining evaluation is one-dimensional. Write

\[
 v=\rho\bigl(c\cos\varphi-s\sin\varphi,
                s\cos\varphi+c\sin\varphi\bigr).
\tag{10}
\]

For fixed \(a,\varphi\), the largest legal radius is

\[
 \rho_{a}(\varphi)=\min\left\{
 {1\over\sqrt{\cos^2\varphi+r^{-2}\sin^2\varphi}},
 {a\sqrt A\over|c\cos\varphi-s\sin\varphi|},
 {a\sqrt B\over|s\cos\varphi+c\sin\varphi|}
 \right\},
\tag{11}
\]

where a quotient with zero denominator is omitted. Therefore

\[
 F_H(t,a)=\max_\varphi \rho_a(\varphi)^2
 \left({\cos^2\varphi\over1+t}
       +{\sin^2\varphi\over r^2+t}\right).
\tag{12}
\]

The other block is explicit. Put
\(L_1=(1+t)^{-1}\) and \(L_2=r^2/(r^2+t)\). Then

\[
 F_D(t,b)=
 \begin{cases}
 b^2(L_1+L_2),&0\le b\le2^{-1/2},\\
 b^2L_1+(1-b^2)L_2,&2^{-1/2}\le b\le1.
 \end{cases}
\tag{13}
\]

Equations (8), (12), and (13) reduce the global four-dimensional polar
test to two scalar maximizations, \(a\) and \(\varphi\), and a monotone
one-dimensional threshold in \(t\).

## 2. A polar witness gives the lower asymptotic bound

Let \(e_+=(c,s)\) and \(e_-=(-s,c)\), and put \(d=2^{-1/2}\). Consider

\[
 v=d(e_+-r e_-),\qquad w=d(1,r).
\tag{14}
\]

Both within-block inequalities in (6) hold with equality. For fixed
\(k>0\) and sufficiently small \(r\), the first coordinate determines
\(\alpha(v)\), while \(\beta(w)=d\). More precisely,

\[
 \alpha(v)^2=d^2\,{(c+rs)^2\over A}
           =d^2\left(1+{2rcs\over A}\right).
\tag{15}
\]

Set

\[
 \zeta={rcs\over A},\qquad \lambda=(1+\zeta)^{-1/2}.
\tag{16}
\]

Then \(\lambda(v,w)\) is polar feasible: its cross constraint is an
equality and scaling preserves its two within-block constraints. The same
formula also holds at \(k=0\), where \(\zeta=0\).

Its resolvent value is

\[
 \lambda^2\left({1\over1+t}+{r^2\over r^2+t}\right).
\tag{17}
\]

Let \(t_r\in(0,r]\) solve

\[
 {1\over1+t_r}+{r^2\over r^2+t_r}=1+\zeta.
\tag{18}
\]

Since

\[
 {1\over1+t}+{r^2\over r^2+t}-1
 ={r^2-t^2\over(1+t)(r^2+t)},
\tag{19}
\]

this is equivalently

\[
 r^2-t_r^2=\zeta(1+t_r)(r^2+t_r).
\tag{20}
\]

The polar witness is outside the \(t\)-ellipsoid whenever \(t<t_r\), so
\(\Psi_2(G_r)\ge t_r\). As \(\zeta=kr^2+O_k(r^4)\), equation (20) gives

\[
 t_r=r-{k\over2}r^2+O_k(r^3).
\tag{21}
\]

Thus \(\liminf\Psi_2(G_r)/r\ge1\).

## 3. Exact two-block upper bound and equality classification

The upper bound does not require the critical scaling or a rotation formula.
Let \(H_1,H_2\) be arbitrary real symmetric positive matrices with the
same eigenvalues \(1,r^2\), and set

\[
 G=\operatorname{Diag}(H_1,H_2).
\tag{22}
\]

Write \(A_i=(H_i)_{11}\), \(B_i=(H_i)_{22}\), and, for a polar vector
\(u=(v_1,v_2)\), put

\[
 q_i=v_i^TH_i^{-1}v_i,
 \qquad m_i=\max\left\{{(v_i)_1^2\over A_i},{(v_i)_2^2\over B_i}\right\}.
\tag{23}
\]

The six two-coordinate polar constraints are exactly

\[
 q_1\le1,\qquad q_2\le1,\qquad m_1+m_2\le1.
\tag{24}
\]

The degree-two identity for the eigenvalues \(1,r^2\) gives

\[
 (H_i+rI)^{-1}={rH_i^{-1}+I\over(1+r)^2}.
\tag{25}
\]

Also, coordinatewise use of the definition of \(m_i\) gives

\[
 \|v_i\|_2^2\le(A_i+B_i)m_i=(1+r^2)m_i.
\tag{26}
\]

Combining (24)--(26),

\[
 \begin{aligned}
 u^T(G+rI)^{-1}u
 &= {r(q_1+q_2)+\|v_1\|_2^2+\|v_2\|_2^2\over(1+r)^2}\\
 &\le {2r+1+r^2\over(1+r)^2}=1.
 \end{aligned}
\tag{27}
\]

Polar containment proves the exact bound

\[
 \Psi_2(G)\le r.
\tag{28}
\]

For the real equality condition, let

\[
 \rho_i={(H_i)_{12}\over\sqrt{A_iB_i}}\in(-1,1).
\tag{29}
\]

Equality in (27) requires \(q_i=1\), equality in (26), and
\(m_1+m_2=1\). Equality in (26) means that the two normalized coordinate
magnitudes in block \(i\) both equal \(\sqrt{m_i}\). If their signs have
product \(\sigma_i\in\{-1,1\}\), direct inversion of the normalized
correlation matrix gives

\[
 q_i={2m_i\over1+\sigma_i\rho_i}.
\tag{30}
\]

Thus \(q_i=1\) permits exactly

\[
 m_i={1\pm|\rho_i|\over2}.
\tag{31}
\]

The two values can sum to one exactly when
\(|\rho_1|=|\rho_2|\). Conversely, when those magnitudes agree, choose
the plus sign in one block and the minus sign in the other. The resulting
polar vector has resolvent value one at \(t=r\), and hence value greater
than one for every \(t<r\). Therefore

\[
 \boxed{\ \Psi_2(G)=r\quad\Longleftrightarrow\quad
         |\rho_1|=|\rho_2|\ }\qquad\text{over the real field.}
\tag{32}
\]

If the magnitudes differ, the compact polar body has strict containment at
\(t=r\), so continuity gives \(\Psi_2(G)<r\).

The field distinction is sharp. For two real-symmetric blocks considered
over the complex field, take normalized coordinate magnitudes
\(\sqrt{m_i}=2^{-1/2}\) and choose their relative phase \(\phi_i\) with
\(\cos\phi_i=\rho_i\). Then

\[
 q_i={1-\rho_i\cos\phi_i\over1-\rho_i^2}=1,
 \qquad m_1+m_2=1.
\tag{33}
\]

The same polar witness proves \(\Psi_{2,\mathbb C}(G)=r\) for every pair
of block angles. This complex statement concerns the complex version of
the atomic model; the real strict classification in (32) remains separate.

Taking \(H_1=H_r\) and \(H_2=D_r\) in (28), then combining it with (21),
proves (3).
