# Rational physical-query net for the rounded trace lower

Status: proved.  This supplies a finite rational test alphabet for the
lower-bound proof.  It does not quantify its numerator or denominator
width, and it does not establish a native arithmetic implementation.

Fix \(G\succ0\), \(C\ge0\), \(q\ge2\), and \(0<\delta<1\).  Put

\[
 S=(G+CI)^{1/2}
\]

and let

\[
 \mathbb S_{\mathbb Q}^{q-1}
 =\{x\in\mathbb Q^q:\|x\|_2=1\}.
\]

This set is dense in the real unit sphere for \(q\ge2\).  For example,
the usual rational stereographic parametrization of the sphere maps the
dense set \(\mathbb Q^{q-1}\) into
\(\mathbb S_{\mathbb Q}^{q-1}\) and misses at most one point.  The map

\[
 T(x)=\frac{Sx}{\|Sx\|_2}
 \quad\text{on }\mathbb S^{q-1}
\tag{1}
\]

is a homeomorphism, with inverse (y\mapsto S^{-1}y/\|S^{-1}y\|_2).
Consequently \(D=T(\mathbb S_{\mathbb Q}^{q-1})\) is dense in the unit
sphere.

Choose a maximal subset \(Z\subset D\) whose distinct points have
Euclidean distance strictly greater than \(\delta\).  Such a set is
finite: the open balls of radius \(\delta/2\) around its points are
disjoint and lie in the ball of radius \(1+\delta/2\), so

\[
 |Z|\le\left(1+\frac2\delta\right)^q.
\tag{2}
\]

Maximality says that every point of the dense set (D) lies at distance at
most \(\delta\) from \(Z\).  Continuity and density then give the same
closed-ball cover of the whole sphere.  In particular, for every unit
vector \(v\), some \(z\in Z\) satisfies

\[
 \langle z,v\rangle\ge1-\frac{\delta^2}{2}.
\tag{3}
\]

For each \(z\in Z\), let \(x(z)\in\mathbb S_{\mathbb Q}^{q-1}\) be the
rational unit vector with \(T(x(z))=z\).  It is a valid physical query.
Moreover, the normalization used in the trace proof recovers it exactly:

\[
 \frac{(G+CI)^{-1/2}z}
 {\|(G+CI)^{-1/2}z\|_2}
 =x(z).
\tag{4}
\]

Indeed, if \(z=Sx/\|Sx\|\) and \(\|x\|=1\), then
\((G+CI)^{-1/2}z=x/\|Sx\|\), whose norm is \(1/\|Sx\|\).  Thus the
identity used in the lower proof remains literal:

\[
 \frac{A x(z)}{\sqrt{C+x(z)^TGx(z)}}
 =A(G+CI)^{-1/2}z.
\tag{5}
\]

The rational alphabet \(\{x(z):z\in Z\}\) is fixed from
\(G,C,\delta\) before the source, state label, support law, or decoder is
chosen.  Replacing the earlier net by this alphabet leaves the union-bound
cardinality, the coefficient \(a=1-\delta^2/2\), and every deterministic
trace inequality unchanged.

Every element of this finite alphabet has a finite rational representation,
but this construction supplies no useful uniform bound on its word width.
It is therefore a mathematical compatibility statement with exact-rational
query arithmetic, not an execution-cost result.
