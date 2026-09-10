# A uniform order-\(r\) lower bound in the \(K_4\) cut-space stratum

Status: proved for this fixed \(q=6\), \(s=3\), real projector stratum.
It neither proves the corresponding statement for every rank-three
projector nor gives an adaptive upper bound.

Orient the six edges of \(K_4\) as

\[
 (12,13,14,23,24,34).
\tag{1}
\]

Let \(P\) be the orthogonal projector onto its three-dimensional cut
space, and put

\[
 G_r=P+r^2(I-P),\qquad0<r\le1.
\tag{2}
\]

The claim is

\[
 \Psi_3(G_r)\ge {r\over1024}.
\tag{3}
\]

The argument keeps the exact coordinate mean and the outcome support cap
of three coordinates throughout.

## A cut--cycle polar vector

Let the vertex potential be
\(f=(1,1,-1,-1)^T/2\), and write its oriented edge differences divided by
two as

\[
 u=\left(0,{1\over2},{1\over2},{1\over2},{1\over2},0\right)^T.
\tag{4}
\]

Then \(u\in\operatorname{range}P\) and \(\|u\|_2=1\).  Let

\[
 n={1\over3}(1,-1,0,1,0,0)^T.
\tag{5}
\]

This is the oriented \(123\) triangle cycle divided by three.  Hence
\(n\in\ker P\) and \(\|n\|_2^2=1/3\).  For

\[
 \alpha=1-8r,\qquad z=\alpha u+rn,
\tag{6}
\]

we show that \(z\) belongs to the at-most-three-coordinate atomic polar
whenever \(0<r\le1/1024\).

Every three-edge subset is either a spanning tree or a triangle.  A subset
of one or two edges is a forest and extends to a spanning tree; its polar
constraint follows from that of the larger principal block.  It is therefore
enough to check these two kinds of three-edge subsets.

## Tree triples

For a spanning tree \(T\), \(P_{TT}\) is positive definite and

\[
 \lambda_{\min}(P_{TT})\ge {1\over16}.
\tag{7}
\]

Indeed, writing the oriented incidence vectors in an orthonormal basis of
the zero-sum vertex space gives the rows of a frame with Gram \(P\).  A
tree incidence matrix has nonzero Gram determinant four.  The edge frame
has the additional factor \(1/2\), so
\(\det P_{TT}=4/4^3=1/16\).  Since \(P\) is a projector,
\(\lambda_{\max}(P_{TT})\le1\), proving (7).  The same lower bound holds
for one- and two-edge forests directly.

Because \(G_{r,TT}\succeq P_{TT}\), and because a row submatrix of an
isometry has contraction norm,

\[
 u_T^TP_{TT}^{-1}u_T\le1,\qquad
 n_T^TP_{TT}^{-1}n_T\le {16\over3}.
\tag{8}
\]

Cauchy--Schwarz and (6) now give

\[
 \begin{aligned}
 z_T^TG_{r,TT}^{-1}z_T
 &\le \alpha^2+{8\over\sqrt3}r+{16\over3}r^2\\
 &\le1+r\left(-16+{8\over\sqrt3}\right)
       +r^2\left(64+{16\over3}\right)<1.
 \end{aligned}
\tag{9}
\]

The final inequality holds for \(r\le1/1024\).

## Triangle triples

For any triangle \(T\), \(P_{TT}\) has two eigenvalues \(3/4\) and one
zero eigenvalue.  The high component in (4) obeys

\[
 \|u_T\|_2^2={1\over2},\qquad
 u_T^TP_{TT}^{\dagger}u_T={2\over3}.
\tag{10}
\]

The null direction is the oriented triangle cycle.  For (5), its squared
null component is \(1/3\) on the \(123\) triangle and \(1/27\) on each
of the other three triangles.  In particular,

\[
 \|\Pi_{\ker P_{TT}}n_T\|_2^2\le {1\over3},\qquad
 \|\Pi_{\operatorname{range}P_{TT}}n_T\|_2\le {1\over\sqrt3}.
\tag{11}
\]

On the range of \(P_{TT}\), the corresponding eigenvalue of \(G_{r,TT}\)
is \(3/4+r^2/4\), while on its null line it is \(r^2\).  Thus

\[
 \begin{aligned}
 z_T^TG_{r,TT}^{-1}z_T
 &\le {4\over3}\left({\alpha\over\sqrt2}
                       +{r\over\sqrt3}\right)^2+{1\over3}\\
 &\le1-9r+44r^2<1.
 \end{aligned}
\tag{12}
\]

Again this holds for \(r\le1/1024\).  Equations (9) and (12) prove the
claimed polar feasibility of \(z\).

## Resolvent excess

Put \(v=r/1024\).  The cut and cycle components in (6) are orthogonal, so

\[
 z^T(G_r+vI)^{-1}z
 ={\alpha^2\over1+v}+{r^2/3\over r^2+v}.
\tag{13}
\]

For \(r\le1/1024\),

\[
 {\alpha^2\over1+v}
 \ge1-\left(16+{1\over1024}\right)r,
 \qquad
 {r^2/3\over r^2+v}
 ={r\over3(r+1/1024)}\ge {512\over3}r.
\tag{14}
\]

The sum in (14) is strictly greater than one.  Atomic polarity therefore
proves (3) in the small-\(r\) range.

For \(r\ge1/1024\), \(G_r\succeq r^2I_6\).  At
\(x=\mathbf1/\sqrt6\), every random \(Y\) with \(\mathbb EY=x\) and
\(\|Y\|_0\le3\) obeys

\[
 \mathbb E\|Y\|_2^2
 \ge {1\over3}\mathbb E\|Y\|_1^2
 \ge {1\over3}\|\mathbb EY\|_1^2=2.
\tag{15}
\]

Hence \(\Psi_3(I_6)\ge1\), and monotonicity gives
\(\Psi_3(G_r)\ge r^2\ge r/1024\).  This completes the proof of (3).

The witness is mixed: its cut component controls every tree triple, while
its cycle component uses the slack of every triangle triple.  Pure-null
queries alone do not establish this order-\(r\) barrier.
