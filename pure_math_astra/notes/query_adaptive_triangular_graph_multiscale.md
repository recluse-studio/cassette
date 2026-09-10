# A triangular graph family and its zero-row containment

Status: exact graph and polar calculation.  The zero-row containment and a
null-space witness together prove a uniform square-root lower bound for this
whole triangular family.  They do not prove a global bound over all rank-two
planes.

Let \(0<d\leq1\), set

\[
 Z_d=\begin{pmatrix}d&d\\0&d^2\end{pmatrix},
 \qquad F_d=\begin{pmatrix}I_2\\Z_d\end{pmatrix},
 \qquad P_d=F_d(F_d^TF_d)^{-1}F_d^T.
\tag{1}
\]

The high plane is in the max-volume graph chart: its pivot minor is one,
every entry of \(Z_d\) has magnitude at most one, and
\(\det Z_d=d^3\).  The row directions are \((1,0)\), \((0,1)\),
\((d,d)\), and \((0,d^2)\).  Thus this is not a direct sum of two
rank-one coordinate blocks, although rows two and four are parallel.

Put

\[
 \Delta=1+2d^2+d^4+d^6.
\tag{2}
\]

Direct inversion gives

\[
 (I+Z_d^TZ_d)^{-1}
 ={1\over\Delta}
 \begin{pmatrix}1+d^2+d^4&-d^2\\-d^2&1+d^2\end{pmatrix}.
\tag{3}
\]

The six two-row minors of \(F_d\), in the order
\(12,13,14,23,24,34\), are

\[
 1,\quad d,\quad d^2,\quad-d,\quad0,\quad d^3.
\tag{4}
\]

Consequently

\[
 \det (P_d)_{SS}={\det(F_d)_S^2\over\Delta}.
\tag{5}
\]

This displays three nonzero minor scales \(1,d^2,d^4,d^6\), alongside
the exactly singular pair \(24\).  In particular, when \(r\ll d\ll1\),
the family is outside every fixed \(Kr\) tube around the coordinate-plane
exceptional projector, but it is not covered by a uniform lower bound from
a fixed positive minor.

## A compatible kernel witness

The vector

\[
 u_d=\left(-d,-{d\over1+d^4},1,-{d^3\over1+d^4}\right)^T
\tag{6}
\]

belongs to \(\ker P_d\).  Indeed, the two entries of \(F_d^Tu_d\) are

\[
 -d+d=0,
 \qquad
 -{d\over1+d^4}+d-{d^5\over1+d^4}=0.
\tag{7}
\]

The adjustment in the fourth coordinate is forced by the singular pair:

\[
 (u_d)_{\{2,4\}}
 =-{d\over1+d^4}(1,d^2),
\tag{8}
\]

which lies in the range of \((P_d)_{\{2,4\}}\). Without this adjustment,
the \(24\) pair would produce an \(r^{-2}\) polar penalty.

For every nonsingular pair other than \(34\), the determinant list (5),
the bound \(\lambda_{\max}((P_d)_{SS})\leq1\), and the coordinate sizes in
(6) give

\[
 (u_d)_S^T(P_d)_{SS}^{-1}(u_d)_S\leq {20\over d^2}.
\tag{9}
\]

The apparently worse \(34\) pair is also only order \(d^{-2}\).  Its
principal block is

\[
 (P_d)_{\{3,4\}}={1\over\Delta}
 \begin{pmatrix}d^2(2+d^4)&d^3\\d^3&d^4(1+d^2)\end{pmatrix},
\tag{10}
\]

and direct inversion gives

\[
 (u_d)_{\{3,4\}}^T(P_d)_{\{3,4\}}^{-1}(u_d)_{\{3,4\}}
 ={1+d^2\over d^2}+{2\over1+d^4}
 +{d^2(2+d^4)\over(1+d^4)^2}
 \leq {5\over d^2}.
\tag{11}
\]

For the singular pair \(24\), the range relation (8) and its rank-one
pseudoinverse give a value at most \(5d^2\).  Thus all six pair forms obey

\[
 \max_{|S|=2}(u_d)_S^T(P_d)_{SS}^{\dagger}(u_d)_S
 \leq {20\over d^2}.
\tag{12}
\]

Now set \(G_{r,d}=P_d+r^2(I-P_d)\).  On the positive eigenspace of every
principal block, \((G_{r,d})_{SS}\succeq(P_d)_{SS}\), and (8) handles its
only singular block.  Hence

\[
 \widehat u_d={d\over\sqrt{20}}u_d
\tag{13}
\]

is feasible for the two-sparse polar of \(G_{r,d}\).  Since
\(u_d\in\ker P_d\) and \(\|u_d\|^2\geq1\),

\[
 \widehat u_d^T(G_{r,d}+vI)^{-1}\widehat u_d
 \geq {d^2/20\over r^2+v}.
\tag{14}
\]

Atomic polarity therefore proves the explicit lower certificate

\[
 \Psi_2(G_{r,d})\geq {d^2\over20}-r^2.
\tag{15}
\]

## Resolution in the stated multiscale band

The weak null-space certificate (15) misses a closer degeneration.  Let
\(F_{d,0}\) be \(F_d\) with its fourth row replaced by zero, and let
\(P_{d,0}\) project onto its column range.  This is a rank-two plane with a
zero fourth coordinate row.  For every vector \(F_da\) in the range of
\(F_d\),

\[
 \operatorname{dist}(F_da,\operatorname{range}F_{d,0})
 \leq d^2|a_2|\leq d^2\|F_da\|.
\tag{16}
\]

The equality of the two plane dimensions and the principal-angle identity
therefore give

\[
 \|P_d-P_{d,0}\|_{\rm op}\leq d^2.
\tag{17}
\]

The zero-row polar theorem applies with \(K=d^2/r\), so

\[
 \Psi_2(G_{r,d})\geq {r\over4(1+d^2/r)^2}.
\tag{18}
\]

Consequently, throughout the intended band \(d^2=o(r)\), including
\(d=r^\alpha\) for \(1/2<\alpha<1\),

\[
 \Psi_2(G_{r,d})\geq (1-o(1)){r\over4}.
\tag{19}
\]

Thus this triangular multiscale family is not an \(o(r)\) counterexample.
Equation (15) remains a valid but weaker null-space certificate; the
zero-row containment supplies the needed mixed high--low witness in the
band asked about here.

## Uniform bound over all \(d\) and \(r\)

The two certificates also cover the complementary scales.  If \(d^2\leq r\),
(18) gives

\[
 \Psi_2(G_{r,d})\geq {r\over16}.
\tag{20}
\]

If \(d^2\geq r\) and \(r\leq1/40\), the null-space bound (15) gives

\[
 \Psi_2(G_{r,d})\geq {d^2\over20}-r^2
 \geq {r\over20}-r^2\geq {r\over40}.
\tag{21}
\]

For completeness, \(G_{r,d}\succeq r^2I\).  At
\(x=(1,1,1,1)^T/2\), every random \(Y\) with at most two nonzero
coordinates and \(\mathbb EY=x\) satisfies

\[
 \mathbb E\|Y\|_2^2
 \geq \tfrac12\mathbb E\|Y\|_1^2
 \geq \tfrac12(\mathbb E\|Y\|_1)^2
 \geq \tfrac12\|\mathbb EY\|_1^2=2.
\tag{22}
\]

Hence \(\Psi_2(I_4)\geq1\), and monotonicity gives
\(\Psi_2(G_{r,d})\geq r^2\).  When \(r\geq1/40\), this is at least
\(r/40\).  The three cases prove

\[
 \boxed{\displaystyle \Psi_2(G_{r,d})\geq {r\over40}
 \quad(0<d\leq1,\ 0<r\leq1).}
\tag{23}
\]

This argument uses the larger zero-row locus.  Its containment statement is
separate from, and stronger in this family than, proximity to the exceptional
direct-sum rank-one-block locus.
