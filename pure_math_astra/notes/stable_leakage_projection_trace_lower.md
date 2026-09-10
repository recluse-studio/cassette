# stable_leakage_projection_trace_lower.md — deterministic trace stability under small nonlocal output leakage; depends on fixed_gram_orbit_static_oracle_minimax_independent_proof.md and MATHS.md.

Status: proved.  This is a finite-query deterministic inequality.  It
does not establish that a finite-advice decoder has the displayed leakage
property; that is a separate concentration or geometric step.

## Statement

Fix \(A\in\mathbb R^{p\times q}\) with \(A^TA=G>0\), put
\(V=\operatorname{span}(A)\), and fix a source- and query-static support
law \((p_S)\).  At each query in a specified finite set, let the (possibly
internally randomized) output after support \(S\) be \(F_S\).  Assume

\[
 \mathbb E_{S,\xi}F_S=Ax,
 \qquad
 \mathbb E_{S,\xi}\|F_S-Ax\|^2\le C,
 \tag{1}
\]

where \(\xi\) denotes source-independent internal randomness.  Write
\(V_S=\operatorname{span}(A_{:S})\), and suppose pointwise in \(S,\xi\)
that

\[
 \bigl\|P_{V\cap V_S^\perp}F_S\bigr\|
 \le\epsilon\|F_S\|.
 \tag{2}
\]

Set

\[
 H=\sum_Sp_SP_{V_S}\big|_V,
 \qquad
 K_C=A(G+CI)^{-1}A^T\big|_V.
 \tag{3}
\]

Assume \(0<\delta<1\), \(\epsilon\ge0\), and \(C\ge0\).
Let \(\mathcal N\) be a Euclidean \(\delta\)-net of the unit sphere in
\(\mathbb R^q\), and assume (1)--(2) hold at the unit queries

\[
 x_z={(G+CI)^{-1/2}z\over
           \|(G+CI)^{-1/2}z\|},
 \qquad z\in\mathcal N.
 \tag{4}
\]

Then, with \(a=1-\delta^2/2\),

\[
 \boxed{\quad H\succeq a^2K_C-2a\epsilon I_V.\quad}
 \tag{5}
\]

Consequently, if \(\bar s=\sum_Sp_S|S|\), then

\[
 \boxed{\quad
 \bar s\ge a^2\operatorname{tr}\bigl(G(G+CI)^{-1}\bigr)
                 -2aq\epsilon.
 \quad}
 \tag{6}
\]

This has no dependence on \(\min_{S:p_S>0}p_S\) or on the condition
number of \(M=\sum_Sp_SE_SG_{SS}^{-1}E_S^T\).

## Proof

For one query, write \(y=Ax\) and

\[
 B=\mathbb E_{S,\xi}\|F_S\|^2.
\]

Exactness gives the variance identity

\[
 B=\mathbb E\|F_S-y\|^2+\|y\|^2
 \le C+x^TGx.
 \tag{7}
\]

For \(w\in V\), decompose it orthogonally as
\(w=P_{V_S}w+w_S^\perp\), where
\(w_S^\perp\in V\cap V_S^\perp\).  The component of \(F_S\) in
\(V^\perp\) is orthogonal to \(w\), so Cauchy--Schwarz and (2) give

\[
 \begin{aligned}
 |\langle w,y\rangle|
 &=\left|\mathbb E\langle w,F_S\rangle\right|\\
 &\le
 \sqrt{\mathbb E\|P_{V_S}w\|^2}\sqrt B+
 \sqrt{\mathbb E\|w_S^\perp\|^2}
 \sqrt{\mathbb E\|P_{V\cap V_S^\perp}F_S\|^2}\\
 &\le\bigl(\sqrt{w^THw}+\epsilon\|w\|\bigr)\sqrt B.
 \end{aligned}
 \tag{8}
\]

The second line uses Cauchy--Schwarz over the joint law of \((S,\xi)\).
This is why no individual support probability is inverted.  With (7),

\[
 { |\langle w,Ax\rangle|\over\sqrt{C+x^TGx}}
 \le\sqrt{w^THw}+\epsilon\|w\|.
 \tag{9}
\]

For \(x=x_z\) from (4), direct cancellation gives

\[
 {Ax_z\over\sqrt{C+x_z^TGx_z}}
 =A(G+CI)^{-1/2}z.
 \tag{10}
\]

For each nonzero \(w\), take a net point within \(\delta\) of the unit
vector parallel to \((G+CI)^{-1/2}A^Tw\).  Its inner product with that
unit vector is at least \(a\).  Equation (9) therefore yields

\[
 a\sqrt{w^TK_Cw}
 \le\sqrt{w^THw}+\epsilon\|w\|.
 \tag{11}
\]

The matrix \(K_C\) satisfies \(0\preceq K_C\preceq I_V\), because its
nonzero eigenvalues are those of
\(G(G+CI)^{-1}\).  Squaring (11), with the negative right-hand case
handled by \(w^THw\ge0\), gives

\[
 w^THw\ge a^2w^TK_Cw-2a\epsilon\|w\|^2.
 \tag{12}
\]

This is (5).  Finally, \(G>0\) makes every selected column family
independent, so \(\operatorname{rank}P_{V_S}=|S|\).  Taking traces in
(5) gives

\[
 \bar s=\operatorname{tr}H
 \ge a^2\operatorname{tr}K_C-2aq\epsilon
 =a^2\operatorname{tr}\bigl(G(G+CI)^{-1}\bigr)-2aq\epsilon,
\]

which is (6).

## Water-level form

Let \(f_G(v)=\operatorname{tr}(G(G+vI)^{-1})\).  If a schedule has
\(\bar s\le s\), (6) implies

\[
 f_G(C)\le {s+2aq\epsilon\over a^2}.
 \tag{13}
\]

Whenever the right side is strictly between zero and \(q\), monotonicity
of \(f_G\) gives the stable spectral-water lower bound

\[
 C\ge f_G^{-1}\!\left({s+2aq\epsilon\over a^2}\right).
 \tag{14}
\]

At \(\epsilon=0\), letting \(\delta\downarrow0\) recovers the usual
trace lower bound.  For positive \(\epsilon\), (14) quantifies exactly
how much leakage and finite-query-net resolution the trace proof absorbs.

The construction of a finite \(\delta\)-net uses no source information:
the queries in (4) depend only on the declared \(G,C,\delta\).  The
number of queries is finite, for example at most
\((1+2/\delta)^q\) by the standard Euclidean covering argument.
