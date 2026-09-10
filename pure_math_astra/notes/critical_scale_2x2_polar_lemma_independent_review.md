# Independent reconstruction of the finite polar lemma and graph barrier

Status: the finite lemma is verified for real \(2\times2\) matrices. Its
\(q=4,s=2\) consequence is verified for real coefficient-unbiased laws with
hard support at most two. This review addresses correctness only.

## Sign reduction and the finite lemma

Let \(R,C\) be diagonal sign matrices and \(K'=RKC\). Feasibility of
\((u',n')\) for \(K'\) transfers to feasibility of

\[
u=Ru',\qquad n=Cn'
\]

for \(K\), because

\[
n+K^Tu=C(n'+K'^Tu'),\qquad
I+K^TK=C(I+K'^TK')C.
\]

The coordinate boxes also transfer after multiplication by their column
signs. Signs can therefore make the diagonal \((-\alpha,-\delta)\), with
\(\alpha,\delta\ge0\), and then conjugation by
\(\operatorname{diag}(-1,1)\) makes \(b+c\le0\) without changing that
diagonal.

If \(K+K^T\preceq0\), then

\[
(I+K)^T(I+K)\preceq I+K^TK
\]

and hence

\[
(I+K)(I+K^TK)^{-1}(I+K)^T\preceq I.
\]

Thus every \(n=u\) passes the ellipsoid condition; the interval argument
below supplies the coordinate boxes, including the one-point interval when
\(b+c=0\).

In the remaining branch the symmetric part is indefinite. Set

\[
e=-(b+c)>0,\quad w=(b-c)/2,\quad
z=\delta-\alpha,\quad \sigma=\alpha+\delta,\quad
k^2=e^2/4-\alpha\delta>0.
\]

The last strict inequality is equivalent to
\(\det(K+K^T)=-4k^2<0\). Also

\[
b=w-e/2,\qquad c=-w-e/2,\qquad
D=\det K=w^2-k^2,\qquad \sigma^2=z^2+4\alpha\delta.
\]

Put \(n=u=(1,x)\), \(x>0\). The diagonal boxes hold from
\(\alpha,\delta\ge0\). The cross boxes reduce exactly to

\[
x^2+2bx-1\le0,\qquad x^2-2cx-1\ge0.
\]

For \(h=(1-x^2)/(2x)\), this is the interval condition

\[
h\in I=[w-e/2,w+e/2].
\]

Every \(h\in\mathbb R\) corresponds to exactly one positive
\(x=\sqrt{1+h^2}-h\).

Let \(N=A+2Bx+Cx^2\) be the ellipsoid numerator from Equation (9) in
critical_scale_2x2_polar_lemma_proof.md. Direct substitution gives

\[
{N\over1+x^2}=-\sigma(1+D)+
{\bigl[z(1-D)-2ew\bigr]h-2wz-e(1-D)\over\sqrt{1+h^2}}. \tag{R1}
\]

The coefficient calculation is exact. With \(x=\tan\theta\),
\(0<\theta<\pi/2\),

\[
{h\over\sqrt{1+h^2}}=\cos(2\theta),\qquad
{1\over\sqrt{1+h^2}}=\sin(2\theta).
\]

Thus the constant, cosine, and sine coefficients are, in that order,

\[
-\sigma(1+D),\qquad z(1-D)-2ew,\qquad -e(1-D)-2wz.
\]

This confirms the original Equation (11); my earlier claim that its labels
were reversed was incorrect.

Within this indefinite branch, if \(D\ge-1\), choose \(h=w\). Equation
(R1) becomes

\[
-(1+D)\left(\sigma+{zw\over\sqrt{1+w^2}}\right)
-{e(1+w^2+k^2)\over\sqrt{1+w^2}}<0.
\]

The first term is nonpositive because \(\sigma\ge|z|\). The second is
strictly negative. The restriction to the indefinite branch must remain
visible: the negative-semidefinite branch was settled separately.

If \(D<-1\), set \(L=-1-D\) and
\(\gamma=4\alpha\delta=e^2-4k^2\). Then \(e/2>|w|\), so \(0\in I\), and
(R1) becomes

\[
\sigma L+
{[(L+2)z-2ew]h-2wz-e(L+2)\over\sqrt{1+h^2}},
\qquad \sigma=\sqrt{z^2+\gamma}. \tag{R2}
\]

Clip \(h=-z/e\) to \(I\). If it lies in \(I\), the value is

\[
\sigma L-(L+2)\sqrt{z^2+e^2}<0,
\]

because \(\gamma<e^2\).

For a lower-endpoint clip, write \(v=e/2-w>0\). Then \(z>ev\), and
multiplying (R2) by \(\sqrt{1+v^2}\) gives

\[
f(z)=L\sqrt{1+v^2}\sqrt{z^2+\gamma}
-(Lv+e)z+e(2wv-L-2).
\]

The identities

\[
(L+2)v+2w=Lv+e,\qquad
0\le{\gamma\over4}=ve-v^2-L-1
\]

give \(L<ve\). Therefore, for \(z\ge ev\),

\[
f'(z)\le L(\sqrt{1+v^2}-v)-e<0,
\]

using \(\sqrt{1+v^2}-v<1/v\). At \(z=ev\), the interior expression
applies at the endpoint and is strictly negative. Hence the lower-clipped
case is negative. The exact symmetry
\((z,w,h)\mapsto(-z,-w,-h)\) preserves (R2) and turns an upper clip into
a lower clip. This proves all cases.

Normalization and inverse sign maps preserve both norms. The finite lemma
therefore holds with

\[
\|u\|_2=\|n\|_2=1.
\]

## Graph-chart transfer and the uniform bound

The graph transfer in exact_graph_chart_polar_bridge_review.md is correct
once the preceding lemma supplies \(\rho=1\). A maximum \(2\times2\) row
minor gives, after coordinate permutation,

\[
\operatorname{range}P=\operatorname{range}\begin{pmatrix}I_2\\Z\end{pmatrix},
\qquad \|Z\|_{\rm op}\le2.
\]

For

\[
H=\begin{pmatrix}I&Z^T\\ Z&ZZ^T+r^2I\end{pmatrix},
\qquad K=Z^T/r,
\]

the vector \(z_0=(u,Zu+rn)\) is in the at-most-two atomic polar of \(H\).
For a mixed high-low pair, the exact Schur complement is

\[
u_m^2+
{(rn_j+Z_{jm'}u_{m'})^2\over r^2+Z_{jm'}^2}\le1,
\]

which is exactly the corresponding finite-lemma box. The high-high and
low-low pairs are respectively the unit and ellipsoid conditions. Each
singleton is contained in a two-coordinate principal block, so no support
condition is omitted.

The resolvent calculation gives

\[
\Psi_2(H)\ge r/8\qquad (0<r\le1/8).
\]

The auxiliary metric has the needed orientation relative to the actual
projector metric:

\[
G_r(P)=P+r^2(I-P)\succeq H/45.
\]

Here \(G_r(P)\succeq H'/5\), while the graph coordinates
\((w,t)=(x_H+Z^Tx_L,rx_L)\) give \(x^THx\le9x^TH'x\). Monotonicity in
the metric yields

\[
\Psi_2(G_r(P))\ge{\Psi_2(H)\over45}\ge {r\over360}
\qquad (0<r\le1/8).
\]

For \(r\ge1/8\), \(G_r(P)\succeq r^2I_4\) and
\(\Psi_2(I_4)=1\). Uniform selection of a two-subset and inverse inclusion
weight \(2\) gives the upper bound \(1\); the equal-coordinate unit query
gives the lower bound. Thus

\[
\Psi_2(G_r(P))\ge r^2\ge r/8,
\]

which is stronger than \(r/360\). Consequently,

\[
\Psi_2\bigl(P+r^2(I-P)\bigr)\ge r/360
\]

for every real rank-two projector \(P\) on \(\mathbb R^4\) and
\(0<r\le1\).

For the diagonal projector, select the high coordinate pair with probability
\(1/(1+r)\) and the low pair with probability \(r/(1+r)\), applying the
reciprocal Horvitz--Thompson weight to selected coordinates. For every
query \(x\), this law is unbiased and has risk operator

\[
\mathbb E[(L-I)^*G_r(P)(L-I)]=rI_4.
\]

It follows that the order \(r\) is sharp over real rank-two bases in this
declared model. This expectation is a risk operator. It is not a
query-independent covariance matrix of the sampled vector.

