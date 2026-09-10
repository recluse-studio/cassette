# Two-column exactness on an open source cell forces a resident baseline

Let \(p\ge3\), and let \(U\) be a nonempty connected open subset of the real Stiefel manifold

\[
\mathcal V_{p,2}=\{(a,b)\in\mathbb R^p\times\mathbb R^p:
\|a\|=\|b\|=1,\ a^Tb=0\}.
\tag{1}
\]

Fix \(0<\theta<1\). A decoder observes column \(a\) with probability \(\theta\), and column \(b\) with probability \(1-\theta\). Suppose its functions satisfy, pointwise,

\[
\theta F_1(a,x)+(1-\theta)F_2(b,x)=a x_1+b x_2
\qquad((a,b)\in U,\ x\in\mathbb R^2).
\tag{2}
\]

The functions may be arbitrary; measurability and smoothness are not needed for this algebraic conclusion. There is a vector function \(c_U(x)\), independent of the source within \(U\), such that

\[
\boxed{
F_1(a,x)=\frac{a x_1+c_U(x)}{\theta},\qquad
F_2(b,x)=\frac{b x_2-c_U(x)}{1-\theta}.}
\tag{3}
\]

The conclusion holds on the two coordinate projections of \(U\). The function \(c_U\) may depend nonlinearly on the query; this theorem does not assert that it is a matrix applied to \(x\).

The [independent reconstruction](two_column_open_cell_borel_rigidity_independent_review.md) checks the geometric argument below. The earlier [differentiable proof](two_column_open_cell_exactness_rigidity.md) is retained as a weaker route. The present proof differentiates only explicit geometric maps, never the decoder functions. No originality or Cassette-goal acceptance is claimed.

## The incidence equation

Fix \(x\), and put

\[
f(a)=\theta F_1(a,x)-a x_1,\qquad
g(b)=(1-\theta)F_2(b,x)-b x_2.
\tag{4}
\]

Then \(f(a)+g(b)=0\) on \(U\). In particular, whenever both \((a,b)\) and \((a',b)\) lie in \(U\),

\[
f(a')=f(a).
\tag{5}
\]

We prove local constancy of \(f\) by composing finitely many moves of this exact form.

## Independent moves near one frame

Fix \((a_0,b_0)\in U\). Let \(c_1,\ldots,c_{p-2}\) be an orthonormal basis of \(\operatorname{span}(a_0,b_0)^\perp\). For \(1\le\ell\le p-2\), choose

\[
b_\ell=b_0,\qquad w_\ell=c_\ell.
\tag{6}
\]

For a sufficiently small nonzero angle \(\alpha\), choose one additional pair

\[
b_{p-1}=\cos\alpha\,b_0+\sin\alpha\,c_1,
\qquad
w_{p-1}=\cos\alpha\,c_1-\sin\alpha\,b_0.
\tag{7}
\]

Every \(b_\ell\) is perpendicular to \(a_0\), every \(w_\ell\) is perpendicular to both \(a_0\) and \(b_\ell\), and all these vectors have unit norm. Since \(U\) is open, \(\alpha\) can be chosen so that \((a_0,b_\ell)\in U\) for every \(\ell\). The \(p-1\) vectors \(w_\ell\) form a basis of \(T_{a_0}S^{p-1}=a_0^\perp\): the last has a nonzero \(b_0\) component, whereas the first \(p-2\) span its orthogonal complement in that tangent space.

For \(a\) near \(a_0\) on the unit sphere, define

\[
b_\ell(a)=\frac{b_\ell-(a^Tb_\ell)a}
{\|b_\ell-(a^Tb_\ell)a\|},
\tag{8}
\]

and

\[
w_\ell(a)=
\frac{(I-aa^T-b_\ell(a)b_\ell(a)^T)w_\ell}
{\|(I-aa^T-b_\ell(a)b_\ell(a)^T)w_\ell\|}.
\tag{9}
\]

The denominators equal one at \(a_0\), so these are smooth on some common neighborhood. Set

\[
T_\ell(a,t)=\cos t\,a+\sin t\,w_\ell(a).
\tag{10}
\]

Both \(a\) and \(T_\ell(a,t)\) are unit vectors perpendicular to \(b_\ell(a)\). By continuity and openness, one may choose the neighborhood and a common positive time interval small enough that

\[
(a,b_\ell(a))\in U,\qquad
(T_\ell(a,t),b_\ell(a))\in U
\tag{11}
\]

for every \(\ell\), every \(a\) in that neighborhood, and every sufficiently small \(t\). Equation (5) therefore gives the exact identity

\[
f(T_\ell(a,t))=f(a).
\tag{12}
\]

No limiting argument about values of \(f\) enters this identity.

## A finite composition reaches an open neighborhood

Starting at \(a_0\), compose the moves in (10):

\[
\Phi(t_1,\ldots,t_{p-1})
=T_{p-1}\bigl(\cdots T_2(T_1(a_0,t_1),t_2)\cdots,t_{p-1}\bigr).
\tag{13}
\]

Restrict the parameters to a sufficiently small neighborhood of zero so that every intermediate point stays in the common neighborhood used for (11). The map is smooth and has

\[
\Phi(0)=a_0,\qquad
\frac{\partial\Phi}{\partial t_\ell}(0)=w_\ell.
\tag{14}
\]

Its derivative is an isomorphism onto \(T_{a_0}S^{p-1}\). In a sphere coordinate chart, the inverse function theorem makes the image of a sufficiently small parameter neighborhood an open neighborhood of \(a_0\). Repeated application of (12) gives \(f(\Phi(t))=f(a_0)\) for every such \(t\). Hence \(f\) is locally constant on the first-column projection of \(U\).

That projection is connected because it is the continuous image of connected \(U\). A locally constant function on a connected set is constant, regardless of the function's regularity or codomain dimension. Thus \(f=c_U(x)\). The incidence equation forces \(g=-c_U(x)\) on the second-column projection. Substituting (4) proves (3).

## Boundaries

The proof needs \(p\ge3\) to choose \(c_1\) and the extra move in (7). For \(p=2\), an orientation-preserving frame has \(b=Ja\), where \(J\) is the fixed quarter-turn. One column then determines the entire frame; the conclusion fails.

Openness is also substantive. A positive-measure measurable advice cell need not contain a neighborhood supporting the moves in (11). The argument above supplies no result for such a cell merely by replacing openness with positive measure. It also does not cover a source-dependent support probability within one cell, more than two support branches, or a finite-word source family without this continuous orbit geometry.

For a connected open advice cell with a fixed support law, however, arbitrary dependence of the correction on fetched column content has disappeared from (3). What remains is a source-independent function of the query within that cell. This is a rigidity statement about exact mean recovery; it does not yet supply the quantitative finite-advice error bound needed for the growing adaptivity comparison.
