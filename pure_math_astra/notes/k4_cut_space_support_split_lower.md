# A support-splitting lower bound for the \(K_4\) cut-space projector

Status: proved.  This is an alternative order-\(r\) lower bound for the
same \(q=6\), \(s=3\) stratum as
`k4_cut_space_q6s3_order_r_lower.md`.  It applies directly to arbitrary
query-adaptive and nonlinear estimators with exact mean; it does not require
a fixed sampling law.

Use the oriented edge order \((12,13,14,23,24,34)\), let \(P\) be the
cut-space projector of \(K_4\), and write \(N=I-P\).  Set

\[
 G_r=P+r^2N,\qquad 0<r\le1.
\tag{1}
\]

Let \(u\) be the unit cut vector induced by the vertex potential
\((1,1,-1,-1)^T/2\), as in the companion note.  Call a support \(S\)
*singular* when \(P\) is noninjective on \(\mathbb R^S\), equivalently when
\(P_{SS}\) is singular; call it *injective* otherwise.  Under the
three-edge cap, the singular supports are exactly the triangles.  A triangle
image under \(P\) is a
two-dimensional subspace of the cut space whose orthogonal complement is
the normalized potential that is constant on the triangle and opposite at
the omitted vertex.  The four such complements have inner-product magnitude
\(1/\sqrt3\) with \(u\).  Therefore

\[
 \operatorname{dist}(u,P\mathbb R^S)\ge d:={1\over\sqrt3}
 \quad\text{for every singular support }S,\ |S|\le3.
\tag{2}
\]

For every injective support \(S\), \(P_{SS}\) has smallest eigenvalue at
least \(1/16\).  For a tree triple this follows from
\(\det P_{SS}=1/16\) and \(P_{SS}\preceq I\); a smaller forest can be
extended by zero coordinates to a tree.  Hence every vector \(y\) supported
on an injective \(S\) obeys

\[
 \|Ny\|_2\le\|y\|_2\le4\|Py\|_2.
\tag{3}
\]

Choose any unit cycle vector \(n\in\ker P\) and define

\[
 a={1\over\sqrt{257}},\qquad b={16\over\sqrt{257}},\qquad
 x=au+bn.
\tag{4}
\]

Then \(\|x\|_2=1\) and \(4a=b/4\).  Consider an arbitrary random output
\(Y\) satisfying

\[
 \mathbb EY=x,\qquad \|Y\|_0\le3\quad\text{almost surely},
\tag{5}
\]

and put

\[
 V=\mathbb E\,(Y-x)^TG_r(Y-x).
\tag{6}
\]

Let \(D\) be the event that the support of \(Y\) is singular and
write \(p=\Pr(D)\).  From (2), every outcome in \(D\) has

\[
 \|P(Y-x)\|_2\ge ad,
 \qquad p\le {V\over a^2d^2}.
\tag{7}
\]

Suppose first that \(V<a^2\).  On the complementary, injective event,
(3), the exact mean, and Cauchy--Schwarz give

\[
 \begin{aligned}
 \left\|\mathbb E\,[NY\,1_{D^c}]\right\|_2
 &\le4\mathbb E\|PY\|_2\\
 &\le4\left(\|Px\|_2+
              \sqrt{\mathbb E\|P(Y-x)\|_2^2}\right)\\
 &\le4(a+\sqrt V)<{b\over2}.
 \end{aligned}
\tag{8}
\]

If \(V=0\), (7) makes \(p=0\), while (8) implies
\(\|\mathbb ENY\|_2<b/2\), contradicting \(\mathbb ENY=bn\).  Hence
\(V>0\).  Since \(\mathbb ENY=bn\), equation (8) gives

\[
 \left\|\mathbb E\,[NY\,1_D]\right\|_2>{b\over2}.
\tag{9}
\]

In particular \(p>0\).  The eventwise Cauchy--Schwarz inequality and (7)
imply

\[
 \mathbb E\|NY\|_2^2
 \ge {b^2\over4p}
 \ge {a^2d^2b^2\over4V}.
\tag{10}
\]

Because \(\mathbb ENY=bn\),

\[
 \mathbb E\|N(Y-x)\|_2^2
 =\mathbb E\|NY\|_2^2-b^2.
\tag{11}
\]

Combining (6), (10), and (11) yields

\[
 V^2+r^2b^2V\ge {r^2a^2d^2b^2\over4}.
\tag{12}
\]

Put

\[
 c_*={\sqrt{65536+256/3}-256\over514}>0.
\tag{13}
\]

With the values in (4) and \(d^2=1/3\), equation (12), after division by
\(r^2\), implies \(V/r\ge c_*\): indeed
\((V/r)^2+r b^2(V/r)\ge a^2d^2b^2/4\), while \(r\le1\).

If instead \(V\ge a^2\), then \(V\ge a^2r\ge c_*r\).  Thus every
admissible exact-mean output for the one fixed query (4) satisfies

\[
 V\ge c_*r.
\tag{14}
\]

Taking the infimum over all laws in (5), then the supremum over unit
queries, proves

\[
 \Psi_3(P+r^2(I-P))\ge c_*r
 \qquad(0<r\le1).
\tag{15}
\]

The proof uses neither a pure-null query nor a fixed linear estimator.  Its
only K4-specific inputs are the positive distance in (2) from the selected
cut direction to every triangle image and the finite inverse bound in (3)
for forests.
