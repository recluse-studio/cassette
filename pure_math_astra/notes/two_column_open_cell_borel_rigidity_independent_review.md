# Independent review: Borel-free rigidity on an open two-column Stiefel cell

Verdict: correct.  The construction proves local constancy using only the
pointwise functional equation and openness of the Stiefel cell.  It needs
no Borel, continuity, or differentiability condition on either decoder.

Let \(p\ge3\), let \(U\subset\mathcal V_{p,2}\) be connected and open, and
suppose arbitrary functions satisfy

\[
 f(a)+g(b)=0\qquad((a,b)\in U). \tag{1}
\]

Then \(f\) is constant on \(\pi_1(U)\) and \(g\) is the opposite constant
on \(\pi_2(U)\).  Applied pointwise in the query to

\[
 f(a)=F_1(a,x)-2x_1a,\qquad
 g(b)=F_2(b,x)-2x_2b,
\]

this proves the affine form in the companion smooth note without imposing
its \(C^1\) hypothesis.

## 1. Local frame moves

Fix \((a_0,b_0)\in U\), and take an orthonormal basis

\[
 c_1,\ldots,c_{p-2}
\]

of \(\operatorname{span}(a_0,b_0)^\perp\).  Choose sufficiently small
\(\theta\ne0\).  Use the \(p-1\) pairs

\[
 (w_\ell,b_\ell)=(c_\ell,b_0)
 \quad(1\le\ell\le p-2), \tag{2}
\]

and

\[
 w_{p-1}=\cos\theta\,c_1-\sin\theta\,b_0,\qquad
 b_{p-1}=\cos\theta\,b_0+\sin\theta\,c_1. \tag{3}
\]

Every \(b_\ell\) is orthogonal to \(a_0\), every \(w_\ell\) is orthogonal
to both \(a_0\) and \(b_\ell\), and the \(w_\ell\) form a basis of
\(a_0^\perp\).  The final claim remains true for \(p=3\): the two vectors
\(c_1\) and \(\cos\theta c_1-\sin\theta b_0\) are independent.  By
openness, \(\theta\) may be chosen so that every \((a_0,b_\ell)\) lies in
\(U\).

For \(a\) in a sufficiently small sphere neighborhood of \(a_0\), define

\[
 b_\ell(a)=
 \frac{P_{a^\perp}b_\ell}{\|P_{a^\perp}b_\ell\|_2},\qquad
 w_\ell(a)=
 \frac{P_{\operatorname{span}(a,b_\ell(a))^\perp}w_\ell}
 {\|P_{\operatorname{span}(a,b_\ell(a))^\perp}w_\ell\|_2}. \tag{4}
\]

The denominators are nonzero near \(a_0\), since at \(a_0\) they equal
one.  These maps are smooth there.  Put

\[
 T_\ell(a,t)=\cos(t)a+\sin(t)w_\ell(a). \tag{5}
\]

Both \((a,b_\ell(a))\) and \((T_\ell(a,t),b_\ell(a))\) are Stiefel frames.
At \(a=a_0,t=0\), they are the frames chosen in (2)--(3).  Since \(U\) is
open and the collection is finite, one common sufficiently small
neighborhood and time interval keep all these frames in \(U\).  Applying
(1) twice with the same second column yields the exact identity

\[
 f(T_\ell(a,t))=f(a). \tag{6}
\]

No regularity of \(f\) or \(g\) enters (6).

## 2. Local constancy

Compose the moves:

\[
 \Phi(t_1,\ldots,t_{p-1})
 =T_{p-1}(\cdots T_1(a_0,t_1)\cdots,t_{p-1}). \tag{7}
\]

After shrinking the parameter cube, all intermediate points remain in the
common neighborhood from Section 1.  Equation (6) gives

\[
 f(\Phi(t))=f(a_0). \tag{8}
\]

At the origin, the derivative of \(\Phi\) has columns
\(w_1,\ldots,w_{p-1}\).  Later maps contribute the identity derivative in
their first argument at time zero, because \(T_\ell(a,0)=a\).  The columns
are a basis of \(T_{a_0}S^{p-1}=a_0^\perp\).  The inverse function theorem
on the sphere therefore makes \(\Phi\) map a parameter neighborhood onto
an open neighborhood of \(a_0\).  Equation (8) proves that \(f\) is
locally constant at \(a_0\).

The same construction with the roles of \(a,b\) exchanged makes \(g\)
locally constant.  The projections of connected \(U\) are connected
continuous images.  A locally constant function on a connected space is
constant, which proves the claim.

## 3. Scope

The argument fails at \(p=2\): there is no \(c_1\), and the completion
fiber is discrete.  It also needs a cell with nonempty open interior; a
positive-measure set without such a patch is not covered.  It establishes
functional-equation rigidity only.  It neither prices the remaining
label-dependent translation nor gives a sampling-risk or resource result.
