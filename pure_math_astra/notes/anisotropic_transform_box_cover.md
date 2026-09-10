# Deterministic anisotropic transform covers

Status: a covering lemma for the restricted fixed-transform, fixed-sampler
model. It removes the logarithm from the existence bound in
dependence_support_transform_rate.md. The construction is standard local
Lie-group geometry; this note makes no originality claim.

## 1. Local box supplied by one common sampler

Use the notation of dependence_support_transform_rate.md. Choose once and
for all \(\mu_*\in\mathcal P(p)\) whose coefficient vector \(c_*\) has
minimum support size \(k\), and use the HT weights \(I_i/p_i\). This law
and these weights are fixed for every codeword.

Let \(\mathsf G\) be \(O(q)\) or \(U(q)\), and let

\[
 \mathsf H=\prod_g O(m_g)\quad\hbox{or}\quad\prod_g U(m_g)
\]

be the stabilizer of \(D\). The orbit is the compact homogeneous manifold
\(\mathsf M=\mathsf G/\mathsf H\). In the cross-eigenspace tangent space
\(\mathfrak m\), split the coordinate directions into

\[
 \mathfrak m=W\oplus L,
\]

where \(L\) consists of the \(k\) field coordinates in
\(\operatorname{supp}c_*\). Thus

\[
 \dim_{\mathbb R}L=\beta k,\qquad
 \dim_{\mathbb R}W=d-\beta k.
\tag{1}
\]

For \(0<r\ll1\), define the local anisotropic box

\[
 E_r=\{X=X_W+X_L\in\mathfrak m:
 \lVert X_W\rVert\le r,\ \lVert X_L\rVert\le r^2\}.
\tag{2}
\]

The local HT upper bound gives constants \(a,r_0>0\) such that

\[
 X\in E_{ar}\quad\Longrightarrow\quad
 \lambda_{\max}\bigl(Q_{\mu_*}(e^XDe^{-X})\bigr)\le t+r^2
\tag{3}
\]

for \(0<r<r_0\). Indeed,
\(\lVert X\rVert^2=O(r^2)\), while
\(\lVert X\circ c_*\rVert=O(r^2)\). Thus every translate of
\(E_{ar}\) is acceptable using the same \(\mu_*\) and the same HT weights.

The invariant volume of its image in \(\mathsf M\) satisfies

\[
 \operatorname{vol}(E_r\cdot D)
 \asymp r^{\dim W+2\dim L}
 =r^{d+\beta k}=r^{2\kappa}.
\tag{4}
\]

## 2. Uniform box composition

Choose a finite atlas of local sections of
\(\mathsf G\to\mathsf G/\mathsf H\), and compact subcharts whose interiors
cover \(\mathsf M\). There are constants \(A,r_1>0\), uniform over these
subcharts, such that the following local engulfing property holds for
\(0<r<r_1\) and centers in the same subchart:

\[
 (E_r\cdot D)\cap(gE_r\cdot D)\ne\varnothing
 \quad\Longrightarrow\quad
 E_r\cdot D\subset gE_{Ar}\cdot D,
\tag{5}
\]

after choosing the lifts supplied by that section.

To prove this, use a reductive complement
\(\mathfrak g=\mathfrak h\oplus\mathfrak m\) and local exponential
coordinates. For \(X,Y\in E_r\), the BCH expansion has

\[
 \operatorname{pr}_W\log(e^Xe^Y)=O(r),\qquad
 \operatorname{pr}_L\log(e^Xe^Y)=O(r^2).
\tag{6}
\]

The first statement follows from the linear terms. In the second, the
linear \(L\)-terms have size \(O(r^2)\), and every bracket with two
\(W\)-terms has size \(O(r^2)\); all remaining BCH terms are smaller.
An \(\mathfrak h\)-component is also \(O(r^2)\). Refactorizing it through a
local section changes the \(\mathfrak m\)-coordinate by \(O(r^2)\), which
fits the \(L\)-scale and is smaller than the \(W\)-scale. As centers move a
wide distance \(O(r)\) within one section chart, their stabilizer frames
also vary by \(O(r)\). Such a frame change sends a wide \(O(r)\) component
into \(L\) by \(O(r^2)\), and a thin \(O(r^2)\) component into \(W\) by
\(O(r^3)\). Thus it also preserves the box scales. Compactness of the
finitely many subcharts makes the constants uniform.

This is the ordinary ball-box argument for weighted exponential boxes. No
bracket-generating hypothesis is needed: brackets of wide directions are
already of the thin scale \(r^2\).

## 3. Maximal packing gives a deterministic cover

Fix \(r=\sqrt\varepsilon\), and choose \(b>0\) so small that
\(E_{Abr}\cdot D\) is contained in the acceptable set in (3). In every
compact subchart, select a maximal disjoint family of the section-framed
sets

\[
 g_\nu E_{br}\cdot D\subset\mathsf M.
\tag{7}
\]

By (5), maximality implies that the dilated sets cover that subchart.
The finite subcharts cover \(\mathsf M\), so the union of all their
dilated families covers \(\mathsf M\):

\[
 g_\nu E_{Abr}\cdot D
\tag{8}
\]

cover \(\mathsf M\). Each selected translate has volume bounded below by
\(c(br)^{2\kappa}\). Since invariant volume is normalized, their number
satisfies

\[
 K\le C r^{-2\kappa}=C\varepsilon^{-\kappa}.
\tag{9}
\]

Choose the library transform \(V_\nu=g_\nu\). If a source Gram matrix lies
in (8), then \(V_\nu^*GV_\nu\) lies in the local box in (3). The fixed law
\(\mu_*\) and its fixed HT weights therefore attain variance at most
\(t+\varepsilon\), while every outcome reads exactly \(s\) encoded columns.
No source-dependent sampler, probability vector, or extra sampler metadata
is required.

The Haar-volume lower bound from dependence_support_transform_rate.md is
\(K\ge c\varepsilon^{-\kappa}\). Consequently

\[
 K_*(\varepsilon)=\Theta(\varepsilon^{-\kappa})
\tag{10}
\]

in the declared fixed-library model.

## 4. Boundary

The construction covers the abstract compact flag orbit. It does not bound
the cost of storing the transforms, choosing their index, evaluating a
decoder, or representing probabilities and weights at finite precision.
The shared sampler is common because it is chosen before the library is
constructed; the library consists only of transform codewords.

## 5. Regular-grid codewords and a deterministic decoder

The packing proof establishes the cardinality bound but does not itself name
the codewords. The following finite-atlas construction does.

Choose finitely many enlarged smooth section charts \(U_\alpha\) and compact
cores \(K_\alpha\subset U_\alpha\) whose interiors cover \(\mathsf M\).
Write a chart coordinate as

\[
 c=(x,y),\qquad x\in\mathbb R^{d-\beta k},\quad
 y\in\mathbb R^{\beta k},
\tag{11}
\]

and choose it so that \(x\) is the projection onto \(W\) at one basepoint.
After shrinking \(U_\alpha\), the projection from the transported wide
space \(W_c\) onto the \(x\)-coordinates is uniformly invertible throughout
the core and a fixed enlargement of it.

Let \(V(c)\) be the smooth section lift. For \(u\in W\), let \(K(u)\) be
the corresponding skew-Hermitian wide generator and define

\[
 \Psi(c,u)=V(c)e^{K(u)}De^{-K(u)}V(c)^*.
\tag{12}
\]

Fix a grid scale \(\delta\asymp\sqrt\varepsilon\). For a target
\(G\in K_\alpha\), round its \(x\)-coordinate to an \(x\)-grid point
\(x_g\) at distance \(O(\delta)\). The map

\[
 (y_0,u)\longmapsto\Psi((x_g,y_0),u)
\tag{13}
\]

has an invertible derivative in the \((y_0,u)\) variables: variation in
\(y_0\) supplies the quotient directions, while variation in \(u\) supplies
the \(x\)-directions through the uniformly invertible projection
\(W_c\to\mathbb R^{d-\beta k}\). The uniform inverse-function theorem gives
\(y_0\) in the enlarged chart and \(u=O(\delta)\) such that (13) equals
\(G\).

Round \(y_0\) to a \(y\)-grid point \(y_g\) at distance \(O(\delta^2)\).
Smooth dependence of the section and BCH composition give

\[
 V(x_g,y_g)^*GV(x_g,y_g)
 =e^{K(u)+E}D e^{-(K(u)+E)},
 \qquad \lVert E\rVert=O(\delta^2),
\tag{14}
\]

in cross-eigenspace coordinates. Its wide component is \(O(\delta)\) and
its thin component is \(O(\delta^2)\). After reducing the fixed grid
constants, the common HT law from Section 1 therefore has variance at most
\(t+\varepsilon\).

The \(x\)-grid has \(O(\delta^{-(d-\beta k)})\) points and the \(y\)-grid
has \(O(\delta^{-2\beta k})\) points. Across the finite atlas,

\[
 K=O\bigl(\delta^{-(d-\beta k)-2\beta k}\bigr)
  =O(\varepsilon^{-\kappa}).
\tag{15}
\]

These are actual grid codewords, not an existential packing family.

For a computable exact-arithmetic parametrization, take each \(V(c)\) in
off-eigenblock Cayley coordinates:

\[
 \operatorname{Cay}(H)=(I-H)(I+H)^{-1},
 \qquad H^*=-H,
\tag{16}
\]

with a fixed rational orthogonal or unitary chart center on the left.
Rational Cayley parameters are dense in the relevant chart domains. By
compactness, finitely many rational-centered charts and compact cores may
be chosen once, independently of \(\varepsilon\). Choose a rational
\(\delta\) comparable to \(\sqrt\varepsilon\), for example by reciprocal
integer rounding, and use rational grid coordinates. The chart label and
grid coordinates then decode deterministically to \(V(c)\), without a
table of \(K\) resident matrices.

This exact-arithmetic observation does not settle finite-precision error,
the cost of evaluating Cayley transforms, the cost of selecting an index,
or the total encoded-byte cost. The finite atlas and decoder are shared
resources and must be declared in any application of the theorem.
