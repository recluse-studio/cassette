# A proof of the finite two-by-two polar lemma

Status: root's complete analytic argument, independently reconstructed in
critical_scale_2x2_scalar_n_equals_u_review.md and
critical_scale_2x2_polar_lemma_independent_review.md. The consequence is a
uniform order bound in a specific four-coordinate coefficient-sampling
problem. Originality and sufficient application significance have not
been established.

The finite problem from critical_scale_2x2_polar_algebra.md asks whether
every real two-by-two matrix K admits vectors u,n with ||u||=1, ||n||>=rho,
and

\[
 |n_j+u_mK_{mj}|\le |u_m|\sqrt{1+K_{mj}^2}
 \quad(m,j=1,2),
 \qquad
 (n+K^Tu)^T(I+K^TK)^{-1}(n+K^Tu)\le1.
 \tag{1}
\]

The argument below proves rho=1. It establishes the sufficient n=u family
after coordinate sign changes. The vectors need not remain equal when
those changes are undone; their norms remain equal.

## 1. Signs and the scalar interval

Independent row and column sign changes preserve (1), upon applying the
row signs to u and the column signs to n. Choose them to make the two
diagonal entries nonpositive. A further simultaneous sign change in one
row and the corresponding column changes the signs of both off-diagonal
entries. Thus we may write

\[
 K=\begin{pmatrix}-\alpha&b\\c&-\delta\end{pmatrix},
 \qquad \alpha,\delta\ge0,\qquad b+c\le0.
 \tag{2}
\]

If K+K^T is negative semidefinite, then

\[
 (I+K)^T(I+K)\preceq I+K^TK
\]

implies

\[
 (I+K)(I+K^TK)^{-1}(I+K)^T\preceq I.
 \tag{3}
\]

Hence the ellipsoid condition holds for every n=u. The scalar interval
argument below, including its endpoint when b+c=0, supplies the coordinate
conditions. This settles that case.

Otherwise b+c<0. Put

\[
 e=-(b+c)>0,\quad w=(b-c)/2,\quad
 z=\delta-\alpha,\quad \sigma=\alpha+\delta,
 \quad k^2=e^2/4-\alpha\delta>0.
 \tag{4}
\]

Here k^2 is a positive scalar, not a matrix entry. We have

\[
 b=w-e/2,\quad c=-w-e/2,\quad
 D:=\det K=w^2-k^2,\quad
 \sigma^2=z^2+4\alpha\delta.
 \tag{5}
\]

Take u=n proportional to (1,x), with x>0. The diagonal conditions in
(1) follow from alpha,delta>=0. The cross conditions are equivalent to

\[
 b\le h\le-c,\qquad
 h=\frac{1-x^2}{2x},
 \tag{6}
\]

because their squares are x^2+2bx-1<=0 and
x^2-2cx-1>=0. Every real h has exactly one positive solution

\[
 x=\sqrt{1+h^2}-h.
 \tag{7}
\]

Thus the admissible interval is

\[
 I=[w-e/2,w+e/2].
 \tag{8}
\]

For the earlier negative-semidefinite case with b+c=0, this interval is
the single point h=b=-c, so it still supplies a feasible positive x.

## 2. Exact expression for the ellipsoid test

Let Delta=det(I+K^TK)>0. For u=n=(1,x), before normalization, the
ellipsoid inequality is equivalent to N(x)<=0, where

\[
 \begin{aligned}
 N(x)&=A+2Bx+Cx^2,\\
 A&=2a(1+d^2)+b^2-c^2-2bcd,\\
 C&=2d(1+a^2)+c^2-b^2-2abc,\\
 B&=(b+c)(1-ad+bc)+(a-d)(c-b),
 \qquad a=-\alpha,\ d=-\delta.
 \end{aligned}
 \tag{9}
\]

Indeed N(x)/Delta is the difference between
((I+K^T)(1,x)^T)^T(I+K^TK)^{-1}((I+K^T)(1,x)^T)
and 1+x^2. These are the exact coefficients from the earlier algebra note.
Substituting (4)-(6), and using
2x/(1+x^2)=1/sqrt(1+h^2), gives

\[
 \frac{N(x)}{1+x^2}
 =-\sigma(1+D)
 +\frac{[z(1-D)-2ew]h-2wz-e(1-D)}
 {\sqrt{1+h^2}}.
 \tag{10}
\]

For a direct coefficient check, write x=tan(theta), so the normalized
vector (1,x) is (cos(theta),sin(theta)). The constant, cos(2theta), and
sin(2theta) coefficients of the quadratic are respectively

\[
 -\sigma(1+D),\qquad z(1-D)-2ew,\qquad -e(1-D)-2wz.
 \tag{11}
\]

We next choose h in I that makes (10) negative.

## 3. The case D>=-1

Choose h=w, the midpoint of I. Equation (10) becomes

\[
 -(1+D)\left(\sigma+\frac{zw}{\sqrt{1+w^2}}\right)
 -\frac{e(1+w^2+k^2)}{\sqrt{1+w^2}}<0.
 \tag{12}
\]

The first summand is nonpositive: 1+D>=0 and sigma>=|z|.
The second is strictly negative because e>0 and k^2>0.

## 4. The case D<-1

Put

\[
 L=-1-D>0,\qquad
 k^2=L+w^2+1,\qquad
 \gamma=4\alpha\delta=e^2-4k^2\ge0.
 \tag{13}
\]

In particular e/2>|w|, so I contains zero. Equation (10) is now

\[
 \sigma L+
 \frac{[(L+2)z-2ew]h-2wz-e(L+2)}
 {\sqrt{1+h^2}},
 \qquad \sigma=\sqrt{z^2+\gamma}.
 \tag{14}
\]

Choose h by clipping -z/e to I, meaning the nearest point of I.

If -z/e lies in I, direct substitution gives

\[
 \frac{N(x)}{1+x^2}
 =\sigma L-(L+2)\sqrt{z^2+e^2}<0.
 \tag{15}
\]

The strict inequality follows from gamma=e^2-4k^2<e^2 and L>0.

Suppose instead that -z/e is below I. Write

\[
 v=e/2-w>0.
 \tag{16}
\]

Then h=-v is the lower endpoint and z>ev. After multiplying (14) by
sqrt(1+v^2), the expression to be bounded is

\[
 f(z)=L\sqrt{1+v^2}\sqrt{z^2+\gamma}
       -(Lv+e)z+e(2wv-L-2).
 \tag{17}
\]

The identity (L+2)v+2w=Lv+e gives the middle coefficient.
For fixed e,w,L, hence fixed gamma, and z>=ev>0,

\[
 f'(z)
 \le L(\sqrt{1+v^2}-v)-e<0.
 \tag{18}
\]

To justify the strict bound using only the stated parameters, (13) gives

\[
 0\le\gamma/4=ve-v^2-L-1,
 \qquad L<ve.
 \tag{19}
\]

Also sqrt(1+v^2)-v=1/(sqrt(1+v^2)+v)<1/v.
Together these imply (18). At z_0=ev, the unclipped direction is exactly
the endpoint. Equation (15) gives f(z_0)<0. Monotonicity therefore gives
f(z)<0 for every z>z_0.

The upper-endpoint case follows from the exact symmetry
(z,w,h)->(-z,-w,-h) of (14) and its interval. It changes an upper clip
to the lower clip just proved, while preserving sigma,e,L,gamma.

Thus all possible clips make (10) strictly negative.

## 5. The finite lemma and its four-coordinate consequence

In every case there is a coordinate-feasible x satisfying the ellipsoid
test. Normalize u=n=(1,x)/sqrt(1+x^2), then undo the initial sign changes.
This proves (1) with ||u||=||n||=1 for every real K.

The exact graph-chart comparison in
exact_graph_chart_polar_bridge_review.md now applies with rho=1 and
c_rho=1/8. Independent reconstruction also verifies this transfer, so
its formerly conditional conclusion becomes

\[
 \Psi_2\bigl(P+r^2(I-P)\bigr)\ge r/360
 \quad\text{for every real rank-two projector }P\text{ on }\mathbb R^4,
 \quad 0<r\le1.
 \tag{20}
\]

The exponent is sharp under basis choice. For the diagonal projector,
sample its two high coordinates with probability 1/(1+r), and its two
low coordinates with probability r/(1+r); rescale the selected query
coordinates by the reciprocal probability. The coefficient mean is
exactly the query, the support is always two, and each diagonal output
variance is r. Consequently

\[
 \frac r{360}\le
 \inf_{P:\,\operatorname{rank}P=2}
 \Psi_2\bigl(P+r^2(I-P)\bigr)\le r.
 \tag{21}
\]

This statement concerns real queries, arbitrary real bases, exact
coefficient unbiasedness, and hard two-coordinate support in four
coordinates. It is not a lower bound for arbitrary nonlinear source
decoders, arbitrary representations, or every Cassette execution plan.
The constant 1/360 is a sufficient comparison constant, not an optimum.
