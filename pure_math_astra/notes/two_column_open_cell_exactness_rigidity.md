# Local exact-mean rigidity for two one-column decoders

Status: proved under an explicit \(C^1\) decoder assumption.  The original
Borel-decoder model is not silently strengthened by this argument.
The later [geometric proof](/Users/drewwiberg/cassette/pure_math_astra/notes/two_column_open_cell_exact_rigidity.md)
removes all regularity assumptions on the decoder. This note preserves
the earlier differentiable route.

Let \(p\ge3\), and let \(U\) be a connected open subset of the real
Stiefel manifold

\[
 \mathcal V_{p,2}=\{(a,b):\|a\|_2=\|b\|_2=1,\ a^Tb=0\}.
\]

Fix a query \(x=(x_1,x_2)\).  Suppose one-column decoders obey exact
mean recovery on \(U\):

\[
 F_1(a,x)+F_2(b,x)=2x_1a+2x_2b
 \qquad((a,b)\in U). \tag{1}
\]

Assume only for this theorem that \(F_1(\,\cdot\,,x)\) is \(C^1\) on
\(\pi_1(U)\subset S^{p-1}\) and \(F_2(\,\cdot\,,x)\) is \(C^1\) on
\(\pi_2(U)\).  The projections are open because the Stiefel projections
are submersions.

## The rigidity theorem

There is a vector \(c_U(x)\in\mathbb R^p\) such that

\[
 F_1(a,x)=2x_1a+c_U(x),\qquad
 F_2(b,x)=2x_2b-c_U(x)
 \qquad((a,b)\in U). \tag{2}
\]

Thus, on an open connected source cell, smooth exactness permits no
frame-dependent nonlinear correction beyond the resident affine
translation \(c_U(x)\).  The vector may depend arbitrarily on the query
and the advice label; this is a functional-equation statement, not a
resident-byte bound or a risk lower bound.

## Proof

Set

\[
 g(a)=F_1(a,x)-2x_1a,\qquad
 h(b)=F_2(b,x)-2x_2b. \tag{3}
\]

Equation (1) becomes

\[
 g(a)+h(b)=0\qquad((a,b)\in U). \tag{4}
\]

Fix \(a\in\pi_1(U)\).  Its fiber

\[
 U_a=\{b\in S^{p-1}\cap a^\perp:(a,b)\in U\}
\]

is a nonempty open subset of the unit sphere in \(a^\perp\).  For
\(b\in U_a\) and \(z\in a^\perp\cap b^\perp\), choose a differentiable
unit-sphere curve \(a(t)\in b^\perp\) with \(a(0)=a\) and \(a'(0)=z\).
For small \(t\), \((a(t),b)\in U\).  Differentiating (4) gives

\[
 Dg(a)[z]=0
 \qquad\left(z\in a^\perp\cap b^\perp,\ b\in U_a\right). \tag{5}
\]

For any scalar component of \(g\), the associated linear functional on
\(a^\perp\) vanishes on \(b^\perp\cap a^\perp\).  Its Riesz vector in
\(a^\perp\) must therefore lie in \(\operatorname{span}\{b\}\).  Since
\(p\ge3\), the open fiber \(U_a\) contains two nonparallel vectors
\(b,b'\).  The same Riesz vector lies in both one-dimensional spans and
is zero.  Applying this to every component gives

\[
 Dg(a)=0. \tag{6}
\]

The argument with the two coordinates exchanged gives \(Dh(b)=0\) on
\(\pi_2(U)\).  Both projections are connected, as continuous images of
the connected set \(U\).  Hence \(g\equiv c_U(x)\) and
\(h\equiv-c_U(x)\), which proves (2).

## Why the stated scope matters

For \(p=2\), the completion fiber of one observed unit column consists of
two points.  It has no two nonparallel local completions, so the argument
in (5)--(6) fails.  This is consistent with the determinant-bit
reconstruction on \(O(2)\).

For merely Borel \(F_1,F_2\), differentiating (4) is unavailable.  The
same conclusion would require an exact connectivity proof for the
bipartite incidence graph whose vertices are observed columns and whose
edges are frames in \(U\).  A measure-theoretic assertion alone is
insufficient because (4) is pointwise.  This note neither proves that
graph result nor supplies a Borel counterexample.

The result uses an open cell.  A positive-measure cell with empty interior
does not provide the local completion fibers used above.
