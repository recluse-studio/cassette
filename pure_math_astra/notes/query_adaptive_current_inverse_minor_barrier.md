# Current inverse-block lower bounds near the exceptional projector locus

Status: the finite-dimensional bounds below are proved. They do not establish
one lower bound proportional to \(r\) for every plane outside an \(O(r)\)
tube around the exceptional locus. In particular, no unproved passage from
Plucker scale to Grassmann distance is used.

Let \(P=EE^T\) be a real rank-two orthogonal projector on \(\mathbb R^4\),
let \(F\) be an orthonormal frame for \(\ker P\), and put

\[
 G_r=P+r^2(I-P),\qquad 0<r\leq1.
\tag{1}
\]

For each coordinate pair \(S\), write \(E_S,F_S\) for its two selected
rows and define the current inverse block on the kernel-coordinate plane

\[
 B_S(r)=F_S^T\bigl(r^2I_2+(1-r^2)E_SE_S^T\bigr)^{-1}F_S.
\tag{2}
\]

Thus every object in (2) is evaluated at the current projector, rather than
at a singular limiting one. Define

\[
 \Lambda_r(P)=\min_{\|y\|_2=1}\ \max_{|S|=2}y^TB_S(r)y.
\tag{3}
\]

## Exact current-kernel certificate

For every rank-two projector \(P\),

\[
 \boxed{\quad
 \Psi_2(G_r)\ge \Lambda_r(P)^{-1}-r^2.
 \quad}
\tag{4}
\]

The right side is permitted to be negative, in which case the statement is
trivial but still correct. To prove (4), choose a unit minimizer \(y\) in
(3), put \(f=Fy\), and set \(u=f/\sqrt{\Lambda_r(P)}\). The definition of
\(B_S\) gives

\[
 u_S^T(G_r)_{SS}^{-1}u_S\le1
 \qquad (|S|=2).
\tag{5}
\]

Thus \(u\) belongs to the two-sparse atomic polar. If an ellipsoid
variance bound \(v\) were valid, atomic polarity would require

\[
 1\ge u^T(G_r+vI)^{-1}u
   ={1\over\Lambda_r(P)(r^2+v)},
\tag{6}
\]

because \(f\in\ker P\). Rearranging proves (4). This preserves the
original exact-mean condition \(\mathbb EY=x\): (5)--(6) use the atomic
polar characterization of that same unbiased problem.

## Plucker and row-direction form

Let \(\lambda_{S,+}\ge\lambda_{S,-}\) be the eigenvalues of
\(P_{SS}=E_SE_S^T\). If

\[
 \tau_S=P_{ii}+P_{jj},\qquad p_S=\det(E_{i,:},E_{j,:})
 \quad(S=\{i,j\}),
\tag{7}
\]

then

\[
 \lambda_{S,\pm}={\tau_S\pm\sqrt{\tau_S^2-4p_S^2}\over2}.
\tag{8}
\]

The two eigenvalues of \(B_S(r)\) are

\[
 h_r(\lambda_{S,+}),\quad h_r(\lambda_{S,-}),
 \qquad
 h_r(\lambda)={1-\lambda\over r^2+(1-r^2)\lambda}.
\tag{9}
\]

Indeed, \(F_SF_S^T=I_2-P_{SS}\), which commutes with the inverse in
(2). The nonzero spectra of \(B_S\) and

\[
 \bigl(r^2I_2+(1-r^2)P_{SS}\bigr)^{-1/2}
 (I_2-P_{SS})
 \bigl(r^2I_2+(1-r^2)P_{SS}\bigr)^{-1/2}
\tag{10}
\]

coincide, proving (9). When \(\lambda<1\), an associated unit direction
in the kernel-coordinate plane is

\[
 w_{S,\lambda}={F_S^Tv_{S,\lambda}\over\sqrt{1-\lambda}},
\tag{11}
\]

where \(v_{S,\lambda}\) is a unit eigenvector of \(P_{SS}\). Hence (3)
is exactly a six-direction, weighted minimax problem on a circle:

\[
 y^TB_Sy=
 h_r(\lambda_{S,+})|\langle y,w_{S,+}\rangle|^2+
 h_r(\lambda_{S,-})|\langle y,w_{S,-}\rangle|^2.
\tag{12}
\]

Formula (12) is the requested current weighted-row-direction form. It
retains the rotations of the small inverse eigendirections that invalidate
the fixed-limit argument in the sparse-null filter.

## A uniform minor barrier away from every singular coordinate pair

Put

\[
 \mu(P)=\min_{|S|=2}\lambda_{S,-}.
\tag{13}
\]

Since \(h_r\) decreases on \([0,1]\), (9) gives
\(B_S(r)\preceq h_r(\mu(P))I_2\). Thus \(\Lambda_r(P)\le
h_r(\mu(P))\), and (4) yields the sharper, \(r\)-independent bound

\[
 \boxed{\quad
 \Psi_2(G_r)\ge {\mu(P)\over1-\mu(P)}.
 \quad}
\tag{14}
\]

The Plucker expression gives the entirely explicit corollary

\[
 \lambda_{S,-}={p_S^2\over\lambda_{S,+}}
 \ge p_S^2,
\qquad
\Psi_2(G_r)\ge
 {p_*(P)^2\over 1-p_*(P)^2},
\quad p_*(P)=\min_{i<j}|p_{ij}|.
\tag{15}
\]

This is stronger than the older \(\mu-r^2\) witness estimate. For a
family with \(p_*(P_r)\gg r\), it supplies a nonvanishing current-minor
barrier of order \(p_*(P_r)^2\), even though its distance divided by \(r\)
may diverge. It need not be order \(r\): for example
\(p_*(P_r)=r^{3/4}\) gives only order \(r^{3/2}\). The inequality alone
therefore cannot close the global square-root question.

## A one-singular-pair certificate

The minimum-Plucker bound vanishes as soon as one coordinate pair is
exactly singular. The directional form still gives a quantitative result.
Suppose one pair \(S_0\) has rank one, every other pair has
\(\lambda_{S,-}\ge\mu>0\), and write
\(\alpha=\lambda_{S_0,+}\in(0,1)\). Choose \(y\) perpendicular to the
large-weight direction \(w_{S_0,-}\) in (12). Then

\[
 y^TB_{S_0}(r)y=h_r(\alpha),
 \qquad y^TB_S(r)y\le h_r(\mu)\quad(S\ne S_0).
\tag{16}
\]

Consequently

\[
 \boxed{\quad
 \Psi_2(G_r)\ge
 \min\left\{\frac{\alpha}{1-\alpha},
              \frac{\mu}{1-\mu}\right\}.
 \quad}
\tag{17}
\]

The same proof applies to several rank-one singular pairs when all their
large-weight directions \(w_{S,-}\) span one line. A rank-zero coordinate
pair, or singular-pair directions spanning the full kernel-coordinate
plane, is not covered. Those are precisely the configurations in which a
kernel-only witness can fail at the exceptional direct-sum strata.

## Relation to the exceptional-tube estimate

Let \(d(P,\mathcal E)=\inf_{P_0\in\mathcal E}\|P-P_0\|_{\rm op}\).
The already proved tube comparison gives, without any new limiting claim,

\[
 \Psi_2(G_r(P))\ge
 \frac{r}{800\,[1+d(P,\mathcal E)/r]^2}.
\tag{18}
\]

Combining only proved inequalities gives the hybrid certificate

\[
 \Psi_2(G_r(P))\ge
 \max\left\{
 {r\over800[1+d(P,\mathcal E)/r]^2},\
 {\mu(P)\over1-\mu(P)}
 \right\},
\tag{19}
\]

with (17) replacing the second term on the one-singular-pair stratum.
Equation (19) remains quantitative when \(d(P,\mathcal E)/r\to\infty\),
but it does not imply a uniform multiple of \(r\) in that regime. A link
from distance to \(\mathcal E\) to either \(p_*\) or the directionally
refined \(\Lambda_r\) would be an additional theorem, not a consequence
of this calculation.
