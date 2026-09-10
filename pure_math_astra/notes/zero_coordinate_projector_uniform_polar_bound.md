# A uniform bound for a projector with one zero coordinate

Let \(P\) be a real rank-\(k\) orthogonal projector on \(\mathbb R^{2k}\), and suppose \(Pe_{j_0}=0\) for some coordinate. Put

\[
L=\binom{2k-1}{k},\qquad
G_r(P)=P+r^2(I-P),\qquad0<r\le1.
\tag{1}
\]

Then the worst-unit-query, exactly unbiased, hard-\(k\)-sparse coefficient risk satisfies

\[
\boxed{\displaystyle
\Psi_k(G_r(P))\ge\frac{r}{\sqrt{2L^2-1}}.}
\tag{2}
\]

The proof uses the finite signed-sum separation lemma in [the zero-column note](zero_column_finite_k_polar_lemma.md), directly on the projector frame. It avoids the losses from the general graph-chart comparison. It does not apply to every projector, and it makes no originality claim.

## A common polar vector

Choose an isometry \(V\in\mathbb R^{2k\times k}\) with \(VV^T=P\). Row \(j_0\) of \(V\) is zero. For each set \(S\subseteq[2k]\) of size \(k\) containing \(j_0\), the matrix \(V_{S\setminus\{j_0\},:}\) has at most \(k-1\) rows. Choose a unit vector \(w_S\) in its kernel. There are exactly \(L\) such sets.

The signed-sum lemma supplies a unit \(u\in\mathbb R^k\) for which

\[
|w_S^Tu|\ge c:=1/L
\tag{3}
\]

for every such \(S\). Define

\[
z=Vu+cr e_{j_0}.
\tag{4}
\]

We check that \(z_S^T(G_r(P))_{SS}^{-1}z_S\le1\) for every size-\(k\) set \(S\). Smaller sets then follow by principal-block monotonicity.

For any row submatrix \(B\) of \(V\), all its nonzero singular values satisfy \(0<\sigma\le1\). Therefore

\[
B^T\bigl(r^2I+(1-r^2)BB^T\bigr)^{-1}B
\preceq\operatorname{proj}_{\operatorname{range}(B^T)},
\tag{5}
\]

because its nonzero eigenvalues are \(\sigma^2/[r^2+(1-r^2)\sigma^2]\le1\).

If \(j_0\notin S\), apply (5) with \(B=V_{S,:}\). The polar quadratic form is at most \(\|u\|^2=1\).

If \(j_0\in S\), the principal block splits into \(r^2\) at \(j_0\) and the block for \(B=V_{S\setminus\{j_0\},:}\). Its polar quadratic form is at most

\[
c^2+\|\operatorname{proj}_{\operatorname{range}(B^T)}u\|^2
\le c^2+1-|w_S^Tu|^2\le1.
\tag{6}
\]

Thus (4) is a legal sparse-atomic polar vector for all \(r\) in (1).

## Exact polar threshold and a uniform linear bound

The two terms in (4) lie in the high and low eigenspaces of \(G_r(P)\). Hence, for \(v\ge0\),

\[
z^T(G_r(P)+vI)^{-1}z
=\frac1{1+v}+\frac{c^2r^2}{r^2+v}.
\tag{7}
\]

The positive value making (7) equal one is

\[
v_r=\frac{\sqrt{(1-c^2)^2r^4+4c^2r^2}-(1-c^2)r^2}{2}.
\tag{8}
\]

The polar criterion gives \(\Psi_k(G_r(P))\ge v_r\): every \(v<v_r\) fails the containing-ellipsoid condition, and one then takes the supremum of those \(v\). Separately, \(G_r(P)\succeq r^2I\) and \(\Psi_k(I_{2k})=1\), so

\[
\Psi_k(G_r(P))\ge\max\{r^2,v_r\}.
\tag{9}
\]

Set \(a=c/\sqrt{2-c^2}=1/\sqrt{2L^2-1}\). If \(r\ge a\), then \(r^2\ge ar\). If \(r\le a\), evaluate the increasing positive-root polynomial from (8) at \(v=ar\):

\[
\begin{aligned}
(ar)^2+(1-c^2)r^2(ar)-c^2r^2
&=r^2\bigl[a^2-c^2+(1-c^2)ar\bigr]\\
&\le r^2\bigl[(2-c^2)a^2-c^2\bigr]=0.
\end{aligned}
\tag{10}
\]

It follows that \(v_r\ge ar\). Equation (9) proves (2) throughout \(0<r\le1\). At \(k=3\), the constant is \(1/\sqrt{199}\). For \(k=2\), the existing sharper planar argument gives \(r/4\); (2) gives \(r/\sqrt{17}\) and serves as the common-dimensional construction.

## A neighborhood with an explicit scale

Suppose \(P_0\) has a zero coordinate and

\[
\|P-P_0\|_{\rm op}\le Cr
\tag{11}
\]

for a fixed \(C\ge0\). Since

\[
G_r(P)^{1/2}=rI+(1-r)P,
\]

the triangle inequality and the smallest singular value \(r\) give, for every \(x\),

\[
\|G_r(P_0)^{1/2}x\|
\le\|G_r(P)^{1/2}x\|+Cr\|x\|
\le(1+C)\|G_r(P)^{1/2}x\|.
\tag{12}
\]

Consequently \(G_r(P)\succeq(1+C)^{-2}G_r(P_0)\). Monotonicity and homogeneity of the exact-mean coefficient risk yield

\[
\boxed{\displaystyle
\Psi_k(G_r(P))\ge
\frac{r}{(1+C)^2\sqrt{2L^2-1}}.}
\tag{13}
\]

For one coordinate, the hypothesis can be checked through \(\delta=\|Pe_j\|<1\). If \(\delta>0\), write the high-space unit vector \(Pe_j/\delta\) as

\[
\delta e_j+\sqrt{1-\delta^2}\,w,\qquad w\perp e_j,\quad\|w\|=1.
\]

The other \(k-1\) high-space basis vectors are orthogonal to both \(e_j\) and \(w\). Replacing the displayed vector by \(w\) gives a rank-\(k\) projector \(P_0\) with \(P_0e_j=0\) and \(\|P-P_0\|=\delta\), the sine of this single principal angle. If \(\delta=0\), take \(P_0=P\). Thus \(\|Pe_j\|\le Cr<1\) implies (13). Directions outside this declared scale neighborhood remain outside this proof.

## A bounded column in the critical graph matrix

Suppose a graph chart represents the high space as the columns of \([I;Z]\), and put \(K=Z^T/r\). If some column of \(K\) has norm at most \(C\), the corresponding row of \(Z\) has norm at most \(Cr\). An orthonormal high-space frame is

\[
V=\begin{pmatrix}I\\Z\end{pmatrix}(I+Z^TZ)^{-1/2}.
\]

Since the last factor has operator norm at most one, that low coordinate \(j\) obeys \(\|Pe_j\|=\|V_{j,:}\|\le Cr\). If \(Cr<1\), (13) applies. If \(Cr\ge1\), then \(C>0\) and the elementary bound \(\Psi_k(G_r(P))\ge r^2\ge r/C\) is at least as strong as (13). Therefore the same bound (13) holds uniformly whenever one critical graph column has norm at most \(C\), even if the other columns and the matrix direction vary. This does not control sequences in which every critical column norm diverges.
