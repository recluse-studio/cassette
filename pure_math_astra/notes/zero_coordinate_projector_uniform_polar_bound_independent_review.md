# Independent review: uniform polar lower bound at a zero projector coordinate

Verdict: `zero_coordinate_projector_uniform_polar_bound.md` is correct as
stated.  It gives a nonasymptotic bound for every rank-\(k\) projector on
\(\mathbb R^{2k}\) with one zero coordinate.  The neighborhood statement has
the claimed \((1+C)^{-2}\) factor.

Let \(P=VV^T\), where \(V\in\mathbb R^{2k\times k}\) has orthonormal
columns, and assume \(Pe_{j_0}=0\).  Then row \(j_0\) of \(V\) vanishes.
Put

\[
 L=\binom{2k-1}{k},\qquad c={1\over L},\qquad
 G_r=P+r^2(I-P),\qquad 0<r\le1.
 \tag{1}
\]

## 1. One polar vector for every support

For each \(k\)-set \(S\) containing \(j_0\), choose a unit vector

\[
 w_S\in\ker V_{S\setminus\{j_0\},:}.
 \tag{2}
\]

It exists because the displayed matrix has only \(k-1\) rows.  There are
\(\binom{2k-1}{k-1}=L\) such sets.  The signed-sum calculation from the
zero-column review supplies a unit \(u\in\mathbb R^k\) with

\[
 |w_S^Tu|\ge c \tag{3}
\]

simultaneously for all those sets.  Set

\[
 z=Vu+cr e_{j_0}. \tag{4}
\]

For \(S\) not containing \(j_0\), put \(B=V_{S,:}\).  Since \(B\) is a
row restriction of an isometry, its singular values are at most one, and

\[
 B^T\bigl(r^2I+(1-r^2)BB^T\bigr)^{-1}B
 \preceq P_{\operatorname{range}(B^T)}. \tag{5}
\]

This bounds the \(S\)-polar form of \(z_S=Bu\) by \(1\).

For \(S\) containing \(j_0\), the zero row splits the principal block into
\(r^2\) at \(j_0\) and

\[
 r^2I+(1-r^2)BB^T,\qquad B=V_{S\setminus\{j_0\},:}.
\]

Equations (3) and (5) give

\[
 \begin{aligned}
 z_S^T(G_r)_{SS}^{-1}z_S
 &\le c^2+\|P_{\operatorname{range}(B^T)}u\|_2^2\\
 &\le c^2+1-|w_S^Tu|^2\le1.
 \end{aligned}
 \tag{6}
\]

Thus every \(k\)-support polar inequality holds.  A smaller support \(T\)
is contained in some \(k\)-set \(S\).  For a positive definite block

\[
 H_{SS}=\begin{pmatrix}A&C\\C^T&D\end{pmatrix},
 \qquad A=H_{TT},
\]

block completion gives

\[
 z_S^TH_{SS}^{-1}z_S
 =z_T^TA^{-1}z_T+
 (z_{S\setminus T}-C^TA^{-1}z_T)^T
 (D-C^TA^{-1}C)^{-1}
 (z_{S\setminus T}-C^TA^{-1}z_T).
 \tag{7}
\]

Hence the smaller-support form is no larger than the containing one.  This
verifies the required at-most-\(k\) atomic polarity, including \(k=1\) and
all singular restrictions of \(V\).

## 2. Exact threshold and the \(r\)-linear lower bound

The summands in (4) lie in orthogonal eigenspaces of \(G_r\), so

\[
 z^T(G_r+vI)^{-1}z
 ={1\over1+v}+{c^2r^2\over r^2+v}. \tag{8}
\]

The equation that this equals one is

\[
 f_r(v):=v^2+(1-c^2)r^2v-c^2r^2=0. \tag{9}
\]

Its positive root is exactly

\[
 v_r={\sqrt{(1-c^2)^2r^4+4c^2r^2}-(1-c^2)r^2\over2}. \tag{10}
\]

The polar ellipsoid criterion makes every \(v<v_r\) impossible, hence
\(\Psi_k(G_r)\ge v_r\).

There is also the independent floor \(\Psi_k(G_r)\ge r^2\).  Indeed,
\(G_r\succeq r^2I\).  For the uniform unit query

\[
 x={1\over\sqrt{2k}}\mathbf1,
\]

every \(k\)-sparse unbiased \(Y\) satisfies

\[
 \mathbb E\|Y\|_2^2
 \ge {\mathbb E\|Y\|_1^2\over k}
 \ge {\|\mathbb EY\|_1^2\over k}=2.
 \tag{11}
\]

Thus its Euclidean risk is at least one. Uniformly choosing a \(k\)-set
and returning twice the retained coordinates of any unit query gives risk
\(\sum_i x_i^2(2-1)=1\). Hence \(\Psi_k(I_{2k})=1\); the lower half
alone already proves the needed \(r^2\) floor.

Set

\[
 a={c\over\sqrt{2-c^2}}={1\over\sqrt{2L^2-1}}. \tag{12}
\]

For \(r\ge a\), \(r^2\ge ar\).  For \(0<r\le a\), \(f_r\) is strictly
increasing on \([0,\infty)\), and

\[
 \begin{aligned}
 f_r(ar)
 &=r^2\bigl[a^2-c^2+(1-c^2)ar\bigr]\\
 &\le r^2\bigl[(2-c^2)a^2-c^2\bigr]=0.
 \end{aligned}
 \tag{13}
\]

So \(v_r\ge ar\).  Together with the \(r^2\) floor this proves

\[
 \Psi_k(G_r)\ge {r\over\sqrt{2L^2-1}}. \tag{14}
\]

This remains valid for \(k=1\): then \(L=c=a=1\), the only containing
support has \(B=0\), and (9) has positive root \(v_r=r\).

## 3. The tube comparison and a nearby zero-coordinate projector

For any orthogonal projector \(Q\),

\[
 G_r(Q)^{1/2}=rI+(1-r)Q. \tag{15}
\]

If \(\|P-P_0\|_{\rm op}\le Cr\), then

\[
 \begin{aligned}
 \|G_r(P_0)^{1/2}x\|_2
 &\le\|G_r(P)^{1/2}x\|_2+Cr\|x\|_2\\
 &\le(1+C)\|G_r(P)^{1/2}x\|_2,
 \end{aligned}
 \tag{16}
\]

because the smallest singular value of \(G_r(P)^{1/2}\) is \(r\).  Thus

\[
 G_r(P)\succeq(1+C)^{-2}G_r(P_0). \tag{17}
\]

Monotonicity and positive homogeneity of the exact-mean coefficient risk
then multiply (14) by \((1+C)^{-2}\).

Finally, take any rank-\(k\) projector \(P\) and a coordinate \(e_j\) with
\(\delta=\|Pe_j\|_2<1\).  If \(\delta>0\), set

\[
 f={Pe_j\over\delta}=\delta e_j+\sqrt{1-\delta^2}\,w,
 \qquad w\perp e_j,\quad\|w\|_2=1. \tag{18}
\]

Every high-space vector orthogonal to \(f\) is orthogonal to \(e_j\), hence
also to \(w\).  Replacing \(f\) by \(w\) in an orthonormal basis of
\(\operatorname{range}(P)\) produces a rank-\(k\) projector \(P_0\) with

\[
 P_0e_j=0,\qquad\|P-P_0\|_{\rm op}=\delta. \tag{19}
\]

The final equality is the sine of the one altered principal angle.  For
\(\delta=0\), take \(P_0=P\).  Therefore \(\|Pe_j\|_2\le Cr<1\) implies

\[
 \Psi_k(G_r(P))\ge
 {r\over(1+C)^2\sqrt{2L^2-1}}. \tag{20}
\]

No asymptotic limit or moving-direction compactness argument appears in
this proof.  The only geometric hypothesis is the displayed tube bound.

## 4. Bounded critical graph column

Suppose the high space is represented by the graph frame

\[
 V=\begin{pmatrix}I\\Z\end{pmatrix}(I+Z^TZ)^{-1/2},
 \qquad K={Z^T\over r}.
 \tag{21}
\]

If column \(j\) of \(K\) has norm at most \(C\), then row \(j\) of \(Z\)
has norm at most \(Cr\).  The corresponding low-coordinate row of \(V\)
therefore has norm at most \(Cr\), because

\[
 \|(I+Z^TZ)^{-1/2}\|_{\rm op}\le1.
 \tag{22}
\]

For \(P=VV^T\), this row norm equals

\[
 \|Pe_{\mathrm{low},j}\|_2=\|V_{\mathrm{low},j,:}\|_2\le Cr.
 \tag{23}
\]

If \(Cr<1\), Equation (20) applies directly.  If \(Cr\ge1\), then
\(C>0\) and the Euclidean floor gives

\[
 \Psi_k(G_r(P))\ge r^2\ge{r\over C}
 \ge {r\over(1+C)^2\sqrt{2L^2-1}}.
 \tag{24}
\]

Thus the bound in (20) holds uniformly whenever one critical graph column
has norm at most \(C\), with no bounds on the other columns.  This is a
fixed numerical condition on a possibly moving graph family; it does not
cover a family for which every critical column norm diverges.
