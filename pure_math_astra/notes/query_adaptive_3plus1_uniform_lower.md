# A uniform square-root lower bound on the exceptional 3+1 stratum

Status: proved finite-dimensional real calculation.  This is a lower bound
for the query-adaptive atomic problem only.  It makes no claim about bytes,
finite encoding, or novelty.

Let \(0<r\leq1\), let \(u\in\mathbb R^3\) have \(\|u\|=1\), and set

\[
 H=r^2I_3+(1-r^2)uu^T,
 \qquad G=H\oplus[1].
\tag{1}
\]

For the two-sparse, unbiased query-adaptive value

\[
 \Psi_2(G)=\sup_{\|x\|=1}\inf_{\mathbb EY=x,\ \|Y\|_0\leq2}
 \mathbb E (Y-x)^TG(Y-x),
\tag{2}
\]
there is an absolute constant \(c>0\) such that

\[
 \Psi_2(G)\geq c r.
\tag{3}
\]

Thus the direct-sum rank-one three-coordinate block plus one singleton does
not furnish an \(o(\sqrt\eta)\) counterexample when \(r=\sqrt\eta\).
The constant does not deteriorate as one or two coordinates of \(u\) tend to
zero.

## Polar test

For a vector \(y=(z,w)\in\mathbb R^3\oplus\mathbb R\), atomic duality says
that \(y\) belongs to the polar body precisely when

\[
 z_{\{i,j\}}^T H_{\{i,j\}}^{-1}z_{\{i,j\}}\leq1,
 \qquad
 \frac{z_i^2}{H_{ii}}+w^2\leq1
 \quad(i,j\in\{1,2,3\},\ i<j).
\tag{4}
\]

If (4) holds and

\[
 y^T(G+vI)^{-1}y>1,
\tag{5}
\]
then \(\Psi_2(G)>v\).  This is the polar ellipsoid-containment form of
`query_adaptive_atomic_dual.md`; the mean condition in (2) remains part of
that formulation.

Changing coordinate signs preserves both (2) and (4).  Permute the first
three coordinates and assume

\[
 a=u_1\geq b=u_2\geq u_3\geq0.
\tag{6}
\]

Only the small-\(r\) argument needs work.  Fixed numerical constants below
are deliberately loose.  They show existence, rather than optimize \(c\).

## Case 1: a non-negligible second coordinate

Put \(K=1/4\), \(\alpha=1/2\), \(\rho=1/8=\alpha K\), and suppose

\[
 b\geq Kr.
\tag{7}
\]

Set

\[
 h=\frac{(b,-a,0)}{\sqrt{a^2+b^2}},
 \qquad z=\alpha u+r\rho h,
 \qquad w^2=1-\alpha^2-Cr\rho,
\tag{8}
\]

where \(C\) is an absolute constant, for example \(C=4\), and take
\(r\leq r_0\) with \(r_0>0\) sufficiently small.  Notice that \(h\perp u\)
and \(\|h\|=1\).

For a two-coordinate set \(S\), write \(A=u_Su_S^T\).  Then

\[
 H_S=r^2I+(1-r^2)A,
 \quad
 u_S^TH_S^{-1}u_S
 =\frac{\|u_S\|^2}{r^2+(1-r^2)\|u_S\|^2}\leq1,
\tag{9}
\]

and direct Sherman--Morrison expansion gives

\[
 (rh_S)^TH_S^{-1}(rh_S)\leq\|h_S\|^2\leq1.
\tag{10}
\]

The triangle inequality for the \(H_S^{-1}\)-norm therefore yields

\[
 \|z_S\|_{H_S^{-1}}\leq\alpha+\rho=5/8<1.
\tag{11}
\]

The singleton constraints in (4) also hold.  Indeed, the second coordinate
of \(z\) lies between zero and \(\alpha b\), since

\[
 r\rho\frac a{\sqrt{a^2+b^2}}
 \leq r\rho=\alpha Kr\leq\alpha b.
\tag{12}
\]

The third coordinate is unchanged.  Hence their normalized squares are at
most \(\alpha^2\).  Since \(a\geq1/\sqrt3\), the first normalized square
satisfies, uniformly for small \(r\),

\[
 \frac{z_1^2}{H_{11}}\leq\alpha^2+Cr\rho.
\tag{13}
\]

This follows by substituting (8), using
\(b/(a\sqrt{a^2+b^2})\leq\sqrt3\), and enlarging \(C\) if necessary.
Equations (8), (12), and (13) give all the singleton inequalities.

For \(v=cr\), (8) and the high--low eigenspace decomposition give

\[
 y^T(G+crI)^{-1}y
 =\frac{1-Cr\rho}{1+cr}
   +\frac{r^2\rho^2}{r^2+cr}
 =\frac{1-Cr\rho}{1+cr}+\frac{r\rho^2}{r+c}.
\tag{14}
\]

Choose a fixed \(c>0\) so small that

\[
 \frac{\rho^2}{c}>2+C\rho.
\tag{15}
\]

For all sufficiently small \(r\), (14) is then strictly larger than one.
This proves (3) in Case 1.

## Case 2: nearly a coordinate high direction

Suppose now \(b<Kr\).  Put \(d_i=H_{ii}\), take the signs of \(u_i\) in
the formula below (with either sign if \(u_i=0\)), and define

\[
 z_i=\operatorname{sgn}(u_i)\sqrt{d_i/2},
 \qquad w=1/\sqrt2.
\tag{16}
\]

For a pair \(i,j\), after this sign change the correlation coefficient of
\(H_{\{i,j\}}\) is nonnegative.  Both standardized coordinates in (16)
equal \(1/\sqrt2\), so

\[
 z_{\{i,j\}}^TH_{\{i,j\}}^{-1}z_{\{i,j\}}
 =\frac1{1+\operatorname{corr}(H_{\{i,j\}})}\leq1.
\tag{17}
\]

The three remaining pair constraints hold with equality:
\(z_i^2/d_i+w^2=1\).  Thus (16) is polar feasible.

Let

\[
 N=\frac12\sum_i d_i=\frac{1+2r^2}{2},
 \qquad
 A=\frac12\left(\sum_i |u_i|\sqrt{d_i}\right)^2,
 \qquad L=N-A.
\tag{18}
\]

The high--low decomposition gives

\[
 y^T(G+crI)^{-1}y
 =\frac{1/2+A}{1+cr}+\frac L{r^2+cr}
 =\frac{1+r^2-L}{1+cr}+\frac L{r(r+c)}.
\tag{19}
\]

There is a uniform lower bound \(L\geq\ell r^2\) in this case.  To see it,
Cauchy--Schwarz in its two-vector form gives the exact identity

\[
 2L=\sum_{i<j}
 \left(\sqrt{u_i^2d_j}-\sqrt{u_j^2d_i}\right)^2.
\tag{20}
\]

Write \(b=rt\), where \(0\leq t\leq K\).  Since also \(u_3\leq Kr\),
the \((1,2)\) summand in (20), divided by \(r^2\), tends uniformly as
\(r\downarrow0\) to

\[
 \left(\sqrt{1+t^2}-t\right)^2
 \geq \left(\sqrt{1+K^2}-K\right)^2.
\tag{21}
\]

Hence, after decreasing \(r_0\) if needed,

\[
 L\geq\ell r^2,
 \qquad
 \ell=\frac18\left(\sqrt{1+K^2}-K\right)^2>0.
\tag{22}
\]

Substitution in (19) shows that its excess over one is positive for all
sufficiently small \(r\) whenever \(c<\ell/4\).  The positive term is of
order \(L/(cr)\geq(\ell/c)r\); the negative terms are at most \(cr+O(r^2)\).
This proves (3) in Case 2.

Take \(c\) smaller than the constants required in (15) and (22).  Both
cases then prove the same absolute lower bound for \(0<r\leq r_0\).
For \(r\geq r_0\), the elementary monotonicity bound

\[
 G\succeq r^2I,
 \qquad \Psi_2(G)\geq r^2\Psi_2(I_4)=r^2
\tag{23}
\]

supplies (3) after reducing \(c\) once more.  Here
\(\Psi_2(I_4)=1\) is the diagonal water-level formula.

## Scope

The argument uses the real signed-coordinate reduction.  It has not been
extended to complex phases.  It proves a uniform lower bound only on the
fixed exceptional \(3+1\) rank-one-block stratum (1).  It does not control
planes that approach that stratum while their singular coordinate-pair
directions split at several rates.
