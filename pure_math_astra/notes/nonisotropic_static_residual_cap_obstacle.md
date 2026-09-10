# nonisotropic_static_residual_cap_obstacle.md — exact Schur-innovation scope of the finite-advice conditional-cap argument; depends on finite_advice_unbiased_static_conditional_cap_lower.md and MATHS.md.

Status: proved reduction and explicit limitation.  It identifies what the
direct conditional-cap proof supplies for a fixed nonidentity Gram matrix.
It does not prove a spectral-water lower bound in that setting.

## Conditional innovation

Let \(G>0\), and let the source orbit be

\[
 \mathcal O_G=\{A\in\mathbb R^{p\times q}:A^TA=G\},\qquad p>q.
\]

Fix a coordinate \(j\), write \(W=A_{:-j}\), and condition on \(W\)
under invariant orbit measure.  The conditional law of \(a_j=A_{:j}\)
has the regression form

\[
 a_j=W G_{-j,-j}^{-1}G_{-j,j}+\sqrt{d_j}\,u,
 \qquad
 d_j=G_{jj}-G_{j,-j}G_{-j,-j}^{-1}G_{-j,j}
 ={1\over(G^{-1})_{jj}},
 \tag{1}
\]

where \(u\) is uniform on the unit sphere in
\(\operatorname{span}(W)^\perp\), whose ambient dimension is
\(p-q+1\).  This follows by writing \(A=UG^{1/2}\) with a uniform
Stiefel \(U\), then taking the ordinary conditional Schur complement.

Thus for any Borel predictor \(H(W)\), and \(0<\delta<\sqrt{d_j}\),

\[
 \Pr\{\|a_j-H(W)\|\le\delta\mid W\}
 \le {1\over2}\left({\delta^2\over d_j}\right)^{(p-q)/2}.
 \tag{2}
\]

Only the component of \(H-WG_{-j,-j}^{-1}G_{-j,j}\) perpendicular to
\(\operatorname{span}(W)\) matters; projecting onto that space and
scaling by \(\sqrt{d_j}\) reduces (2) to the unit-sphere cap bound.

## The exact coordinate-wise consequence

Consider one advice label with a source- and query-static support law
\(w_S\), inclusion probabilities
\(\theta_j=\sum_{S\ni j}w_S\), and expected read count at most
\(0<s<q\).  The omitted-branch average \(H_j(W)\) is well-defined for
every \(\theta_j<1\), including \(\theta_j=0\).  For
\(0<\theta_j<1\), the exact-mean/Jensen calculation in the
identity-Gram proof remains valid at the query \(e_j\): branches omitting
\(j\) form a predictor \(H_j(W)\), and

\[
 R(A,e_j)\ge {1-\theta_j\over\theta_j}
 \|H_j(W)-a_j\|^2.
 \tag{3}
\]

Define \(t_{\rm Schur}(G,s)>0\) by

\[
 \sum_{j=1}^q {d_j\over d_j+t_{\rm Schur}}=s.
 \tag{4}
\]

There is an index \(j\) for which

\[
 d_j{1-\theta_j\over\theta_j}\ge t_{\rm Schur}(G,s).
 \tag{5}
\]

For otherwise every \(j\) would satisfy
\(\theta_j>d_j/(d_j+t_{\rm Schur})\), whose sum is larger than \(s\).
Combining (2), (3), and (5) gives the direct finite-advice lower bound

\[
 C\ge t_{\rm Schur}(G,s)
 \min\!\left\{1,
 \left({2\over N}\right)^{2/(p-q)}\right\}.
 \tag{6}
\]

The proof has the same cell-by-cell Fubini argument as the identity-Gram
theorem.  A zero inclusion probability forces a graph over \(W\), hence
a null cell.  Formula (6) is therefore a correct extension of that
argument, rather than a spectral statement.  At \(C=0\), every remaining
cell has a singleton conditional innovation fiber and is null; thus the
endpoint is covered without dividing by \(C\).

## Why this is insufficient for the equicorrelation example

For

\[
 H_\eta=\mathbf1\mathbf1^T+\eta I_4,
 \qquad \eta>0,
 \tag{7}
\]

the inverse formula for \(aI+b\mathbf1\mathbf1^T\) gives

\[
 (H_\eta^{-1})_{jj}={\eta+3\over\eta(\eta+4)},
 \qquad
 d_j={\eta(\eta+4)\over\eta+3}
 ={4\over3}\eta+O(\eta^2).
 \tag{8}
\]

At read budget \(s=2\), all four innovations agree, so (4) gives

\[
 t_{\rm Schur}(H_\eta,2)=d_j
 ={4\over3}\eta+O(\eta^2).
 \tag{9}
\]

This is below a target static error threshold \(1.9\eta\).  It also
falls below the fixed-linear spectral water level, which is
\(2\eta+O(\eta^2)\) for this spectrum.  Consequently the direct
conditional-cap method cannot establish the required static lower bound
for that example.

## Basis dependence

If a label may choose a fixed right orthogonal basis \(Q\), the same
calculation uses

\[
 d_j(Q)={1\over(Q^TG^{-1}Q)_{jj}}.
 \tag{10}
\]

Hence \(t_{\rm Schur}(Q^TGQ,s)\) is not visibly invariant under \(Q\).
For example, with \(q=2\), \(s=1\), and
\(G=\operatorname{diag}(4,1)\), the eigenbasis gives
\(t_{\rm Schur}=2\), whereas the \(45^\circ\) rotation gives
\(d_1=d_2=8/5\) and \(t_{\rm Schur}=8/5\).  A lower bound intended to
cover a finite label-specific basis catalog must therefore control the
minimum of this basis-dependent Schur quantity or use a different
argument.  The coordinate proof alone supplies only the harmonic floor
below, which is insufficient for the target equicorrelation threshold.

## A basis-uniform harmonic floor

Let \(h_j=(Q^TG^{-1}Q)_{jj}=1/d_j(Q)\).  For fixed \(t>0\), the map
\(h\mapsto(1+th)^{-1}\) is convex.  Jensen's inequality therefore gives

\[
 \sum_{j=1}^q\frac{1}{1+t h_j}
 \ge \frac{q}{1+t\,\operatorname{tr}(G^{-1})/q}.
 \tag{11}
\]

The left side decreases in \(t\) and equals \(s\) at
\(t=t_{\rm Schur}(Q^TGQ,s)\).  Evaluating (11) at the value for which the
right side is \(s\) proves the basis-uniform bound

\[
 t_{\rm Schur}(Q^TGQ,s)
 \ge \frac{q(q/s-1)}{\operatorname{tr}(G^{-1})}.
 \tag{12}
\]

For \(H_\eta\) in its original basis, all inverse diagonal entries agree,
so equality holds in (12).  Its best basis-uniform coordinate-cap floor is
therefore \(\frac43\eta+O(\eta^2)\) at \(q=4,s=2\), still below
\(1.9\eta\).
