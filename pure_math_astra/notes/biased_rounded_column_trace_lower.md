# Rounded original-column trace lower with declared output bias

Status: proved extension of the finite rounded-source original-column trace
lower.  Exact coefficient mean is replaced by a uniform declared output-bias
bound.  This is a mathematical statement about the stated Borel protocol
model; it does not validate floating-point arithmetic or native Cassette
execution.

## Model

Fix \(G\succ0\), \(p>q\ge2\), and a rounded source family

\[
 \mathcal W_h=\{W=\operatorname{round}_h(A):A^TA=G\},
 \qquad
 \|W-A\|_{\rm op}\le r_0.
 \tag{1}
\]

A fixed finite-state static architecture has at most \(N\) source states.
In state \(\ell\), it draws an original-column support \(S\) from a law
\(w_{\ell,S}\) independent of the query and source.  Its Borel branch
output sees only \(W_S\), with source-independent internal randomness.  For
every rounded source in its selected state and every unit query \(x\),
assume

\[
 \mathbb E\|F-Wx\|_2^2\le C,
 \qquad
 \|\mathbb EF-Wx\|_2\le b.
 \tag{2}
\]

The bias is an output-space bias.  Equivalently, a homogeneous version may
state the two bounds as \(C\|x\|_2^2\) and \(b\|x\|_2\) for arbitrary
queries.  The proof below uses only unit queries and does not assume that a
nonlinear decoder is homogeneous.

Discard zero-probability supports.  Conditional expectation over a branch's
seed gives deterministic Borel maps \(f_{\ell,S}(W_S,x)\), without increasing
the MSE in (2) and without changing its aggregate mean or bias.  Lift them
to the continuous orbit by

\[
 \widetilde f_{\ell,S}(A_S,x)=
 f_{\ell,S}(\operatorname{round}_h(A_S),x),
 \tag{3}
\]

extending a map by zero on unused grid inputs if needed.  The lift remains a
Borel function of precisely its observed columns.

## The concentration event is unchanged

Fix \(0<\epsilon,\delta<1\), and use the same finite net of unit queries

\[
 x_z=\frac{(G+CI)^{-1/2}z}
 {\|(G+CI)^{-1/2}z\|_2},
 \qquad z\in\mathcal Z,
 \qquad |\mathcal Z|\le(1+2/\delta)^q.
 \tag{4}
\]

For each fixed \((\ell,S,z)\), conditional Haar-subspace concentration
applies to (3), before a rounded source selects its state.  The union over
all states, positive-probability supports, and net queries therefore has
exactly the former failure bound

\[
 \beta=N2^{3q/2}(1+2/\delta)^q
 \exp\left(-\frac{(p-q)\epsilon^2}{4}\right).
 \tag{5}
\]

Thus every \(A\) in the good event is simultaneously good for the state
selected by \(W=\operatorname{round}_h(A)\).  Neither output exactness nor
unbiasedness is used to form this event.

## Biased deterministic trace step

Fix a good \(A\), its rounded source \(W\), its selected state, and one of
the unit queries in (4).  Let \(V=\operatorname{span}(A)\), and define

\[
 H=\sum_Sw_SP_{\operatorname{span}(A_S)}\big|_V,
 \qquad
 K_C=A(G+CI)^{-1}A^T\big|_V,
 \qquad
 B=\sum_Sw_S\|\widetilde f_S(A_S,x)\|_2^2.
 \tag{6}
\]

Write \(\mu=\sum_Sw_S\widetilde f_S(A_S,x)\).  Jensen and (2) give

\[
 \begin{aligned}
 B
 &\le\mathbb E\|F\|_2^2\\
 &=\mathbb E\|F-Wx\|_2^2
   +2\langle\mathbb EF-Wx,Wx\rangle+\|Wx\|_2^2\\
 &\le C+2b\|Wx\|_2+\|Wx\|_2^2\\
 &\le C+(\|Ax\|_2+r_0+b)^2.
 \end{aligned}
 \tag{7}
\]

Put

\[
 D_x=\sqrt{C+x^TGx},\qquad
 \rho=r_0+b,\qquad
 \zeta=\frac{\rho}{\sqrt{C+\lambda_{\min}(G)}}.
 \tag{8}
\]

The elementary inequality
\(\sqrt{C+(a+\rho)^2}\le\sqrt{C+a^2}+\rho\) and (7) imply

\[
 \sqrt B\le D_x+\rho\le(1+\zeta)D_x.
 \tag{9}
\]

For \(u\in V\), the good-event leakage estimate and Cauchy--Schwarz over
the support law give

\[
 |\langle u,\mu\rangle|
 \le\bigl(\sqrt{u^THu}+\epsilon\|u\|_2\bigr)\sqrt B.
 \tag{10}
\]

The mean is now only approximately \(Wx\), but (1) and (2) give

\[
 \begin{aligned}
 |\langle u,Ax\rangle|
 &\le |\langle u,\mu\rangle|+\|u\|_2\|\mu-Wx\|_2
       +r_0\|u\|_2\\
 &\le\bigl(\sqrt{u^THu}+\epsilon\|u\|_2\bigr)\sqrt B
       +\rho\|u\|_2.
 \end{aligned}
 \tag{11}
\]

Divide by \(D_x\), use (9), and use \(D_x\ge
\sqrt{C+\lambda_{\min}(G)}\).  Then

\[
 \frac{|\langle u,Ax\rangle|}{D_x}
 \le(1+\zeta)\sqrt{u^THu}
 +\bigl[\epsilon(1+\zeta)+\zeta\bigr]\|u\|_2.
 \tag{12}
\]

For the special unit queries (4), the exact algebraic identity

\[
 \frac{Ax_z}{D_{x_z}}=A(G+CI)^{-1/2}z
 \tag{13}
\]

is unchanged.  The original finite-net duality and two-case squaring proof
therefore yields

\[
 H\succeq\alpha^2K_C-2\alpha\epsilon'I_V,
 \qquad
 \alpha=\frac{1-\delta^2/2}{1+\zeta},
 \qquad
 \epsilon'=\epsilon+\frac{\zeta}{1+\zeta}.
 \tag{14}
\]

Taking traces gives the same lower form with the enlarged radius:

\[
 s_{\ell(W)}=\operatorname{tr}H
 \ge\alpha^2 f_G(C)-2\alpha q\epsilon'.
 \tag{15}
\]

If \(\beta<1\), some rounded source lies in the good event, so no fixed
finite-state static architecture that has expected support count below the
right side of (15) can satisfy (2) for every rounded source and unit query.

## Scope

The only change from the exact-mean lower is
\(r_0\mapsto r_0+b\) in \(\zeta\) and in the dual remainder.  The support
law must still be static within each source state.  The result does not cover
query-dependent support schedules, does not turn a floating implementation
into an exact sampler, and does not supply the required numerical value of
\(b\).  A finite-arithmetic application must prove a uniform output-space
bias bound in the same norm as (2), then substitute it into (8).
