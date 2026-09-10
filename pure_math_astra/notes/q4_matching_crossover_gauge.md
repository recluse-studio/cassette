# The q=4 matching crossover: an exact cross-covariance gauge

Status: a local exact calculation for full covariance support in the
fixed-basis, exactly-two-subset model. It supplies a crossover gauge near a
reciprocal matching. It makes no claim about a byte model, transform
covering, or novelty.

## 1. Marginals and coordinates

Fix

\[
0<a,b<1,\qquad
a\ne\frac12,\quad b\ne\frac12,\qquad
a\ne b,\qquad a+b\ne1,
\tag{1}
\]

and let

\[
p(h)=(a,\ 1-a+h,\ b,\ 1-b-h).
\tag{2}
\]

For sufficiently small nonzero \(h\), these are interior marginals summing
to two. At \(h=0\), the complementary pairs are \(12\) and \(34\). The
conditions in (1) say that the four base marginals are distinct and that
there is no other complementary pair.

An exactly-two-subset law is specified by six nonnegative pair masses
\(z_{ij}=\Pr\{S=\{i,j\}\}\). Put

\[
x=z_{12},\qquad \xi=z_{13},\qquad r=\xi-ab.
\tag{3}
\]

The marginal equations force

\[
\begin{array}{c|cccccc}
ij&12&13&14&23&24&34\\ \hline
z_{ij}
&x&ab+r&a-x-ab-r&b-x+h-ab-r&1-a-b+ab+r&x-h .
\end{array}
\tag{4}
\]

Conversely, every \(x,r\) making the six quantities in (4) nonnegative is
one legal law. Thus the entire local transport polytope is explicit. In
particular,

\[
x\ge\max\{0,h\}.
\tag{5}
\]

The other four inequalities in (4) are strict at
\((h,x,r)=(0,0,0)\), because \(0<a,b<1\). They therefore impose no
first-order restriction on \(x,r\) in a bounded neighborhood of that
point.

Let \(c_{ij}=z_{ij}-p_i(h)p_j(h)\). The four cross-pair covariances, in
the order \((13,14,23,24)\), are

\[
c_\times(h;x,r)=
\left(
r,\
ah-x-r,\
(1-b)h-x-r,\
r+(b-a)h+h^2
\right).
\tag{6}
\]

The two within-pair covariances are

\[
c_{12}=x-a(1-a)-ah,\qquad
c_{34}=x-b(1-b)-(1-b)h.
\tag{7}
\]

At \(h=0\), \(x=r=0\) gives zero cross covariance and the two nonzero
within-pair covariances \(-a(1-a)\) and \(-b(1-b)\).

## 2. First-order transport geometry

For \(h\ne0\), write \(x=\alpha h\), \(r=\rho h\). From (5),

\[
\alpha\ge1\quad(h>0),\qquad
\alpha\le0\quad(h<0).
\tag{8}
\]

For every bounded pair \((\alpha,\rho)\), the remaining inequalities in
(4) hold for sufficiently small \(|h|\). Dividing (6) by \(h\) gives the
limiting cross-covariance map

\[
\ell(\alpha,\rho)=
\left(
\rho,\
a-\alpha-\rho,\
1-b-\alpha-\rho,\
\rho+b-a
\right).
\tag{9}
\]

Hence the two tangent sets are

\[
\mathcal L_+=\{\ell(\alpha,\rho):\alpha\ge1,\ \rho\in\mathbb R\},
\qquad
\mathcal L_-=\{\ell(\alpha,\rho):\alpha\le0,\ \rho\in\mathbb R\}.
\tag{10}
\]

They are closed unbounded polyhedra. Thus the full rescaled transport
polytope has no literal compact limit. The compact object relevant to a
small cross-covariance gauge is its bounded slice. For \(M>0\), set

\[
\mathcal P_\pm(M)=
\mathcal L_\pm\cap[-M,M]^4.
\tag{11}
\]

This is a compact polytope. The sets

\[
\left\{
\frac{c_\times(h;x,r)}{h}:
\|c_\times(h;x,r)\|_\infty\le M|h|,\
(x,r)\text{ satisfies (4)}
\right\}
\tag{12}
\]

converge to \(\mathcal P_+(M)\) as \(h\downarrow0\), and to
\(\mathcal P_-(M)\) as \(h\uparrow0\), in Hausdorff distance. Indeed,
(6) differs from \(h\ell(\alpha,\rho)\) only by \(h^2e_{24}\).
Boundedness in (12), together with
\(c_{13}+c_{14}=ah-x\), bounds \(\alpha\), and
\(c_{13}=r\) bounds \(\rho\). The strict inequalities noted after (5)
then pass to the limit and lift every point of (11) for small \(|h|\).

This gives the requested first-order classification without treating a
numerical search as evidence.

## 3. Exact zero patterns

Every one of the four cross covariances can be made exactly zero while the
other three remain \(O(|h|)\). Use

\[
x_*(h)=\max\{h,0\}
\tag{13}
\]

and choose \(r\), respectively, as

\[
0,\qquad
ah-x_*(h),\qquad
(1-b)h-x_*(h),\qquad
(a-b)h-h^2.
\tag{14}
\]

These choices set \(c_{13},c_{14},c_{23},c_{24}\), respectively, to zero.
For small \(|h|\), (4) is nonnegative because it is a perturbation of the
strictly positive cross-pair law at \(h=0\), while (13) is precisely the
constraint needed for \(z_{12},z_{34}\).

No two cross covariances can vanish simultaneously for any sufficiently
small \(h\ne0\).
There are six pairs to check. Two follow directly from

\[
c_{14}-c_{23}=(a+b-1)h,\qquad
c_{24}-c_{13}=(b-a)h+h^2.
\tag{15}
\]

For the other four, solving the indicated two zero equations gives

\[
x=ah,\quad x=(1-b)h,\quad
x=bh+h^2,\quad x=(1-a)h+h^2,
\tag{16}
\]

for the pairs \((13,14),(13,23),(14,24),(23,24)\), respectively.
For \(h>0\), each right side is less than \(h\) when \(|h|\) is small; for
\(h<0\), each is negative. Both conclusions contradict (5). This proves
the claim.

The exact support transition is therefore sharp: at \(h=0\), the matching
law has two covariance edges; at every small nonzero \(h\), a law can have
one zero cross edge but cannot have two. The full q=4 classification then
gives total covariance support five when no other accidental complementary
pair is introduced.

## 4. Uniform weighted cross gauge

Let

\[
m=\min\{a,1-a,b,1-b,|a-b|,|a+b-1|\}>0
\tag{17}
\]

and restrict to \(0<|h|<h_0\), for a fixed \(h_0\) small enough that
\(|h|<m/4\). From (5), (6), and (15)--(16), every pair of distinct cross
coordinates contains one coordinate of magnitude at least

\[
\gamma |h|,\qquad \gamma=m/4.
\tag{18}
\]

For example,
\(\max\{|c_{14}|,|c_{23}|\}\ge|a+b-1||h|/2\), while
\(\max\{|c_{13}|,|c_{14}|\}\ge
\min\{a,1-a\}|h|/2\) follows from
\(c_{13}+c_{14}=ah-x\) and (5). The remaining four pairs follow by the
same two displayed identities and their analogues
\(c_{14}+c_{24}=bh-x+h^2\) and
\(c_{23}+c_{24}=(1-a)h-x+h^2\). Reducing to \(\gamma\) makes the estimate
uniform.

Let \(B=(B_{13},B_{14},B_{23},B_{24})\) be any real or complex cross-block
coordinate vector. Define the cross gauge

\[
g_h(B)=
\min_{(x,r)\text{ legal}}
\left\|B\circ c_\times(h;x,r)\right\|_2
\tag{19}
\]

and let \(\mathcal A=\bigcup_{i=1}^4\mathbb F e_i\) be the union of the
four coordinate axes. Since

\[
\operatorname{dist}(B,\mathcal A)
=\min_i\|B_{\{1,2,3,4\}\setminus\{i\}}\|_2,
\tag{20}
\]

(18) implies

\[
g_h(B)\ge
\gamma|h|\,\operatorname{dist}(B,\mathcal A).
\tag{21}
\]

Indeed, at most one cross coordinate can have magnitude below
\(\gamma|h|\), so at least the three coordinates outside one axis have that
lower bound.

Conversely, the four laws in (13)--(14) have a prescribed zero coordinate
and all other cross covariances bounded by \(\Gamma|h|\), for a constant
\(\Gamma=\Gamma(a,b)\). Choose the zero coordinate whose complementary
three-vector has least norm. Then

\[
g_h(B)\le
\Gamma|h|\,\operatorname{dist}(B,\mathcal A).
\tag{22}
\]

Equations (21)--(22) prove the proposed uniform gauge. It is a
two-sided comparison, not an equality with a canonical constant.

For the zero-coordinate constructions, (7) gives

\[
c_{12}=-a(1-a)+O(|h|),\qquad
c_{34}=-b(1-b)+O(|h|).
\tag{23}
\]

Thus the two matching edges remain order one throughout this crossover
family. The gauge isolates the new cross-block penalty; it does not erase
the within-pair part of the sampling covariance.

## 5. Rational example

For

\[
a=\frac15,\qquad b=\frac7{20},
\tag{24}
\]

the base marginals are
\((1/5,4/5,7/20,13/20)\), and

\[
m=\min\left\{
\frac15,\frac45,\frac7{20},\frac{13}{20},
\frac3{20},\frac9{20}
\right\}=\frac3{20}.
\tag{25}
\]

Hence (21) holds, for example, with
\(\gamma=3/80\) throughout any sufficiently small punctured interval such
as \(0<|h|<3/80\). All claims above are symbolic in \(a,b,h\); this
rational instance is only a concrete parameter choice.

## 6. Scope

The result concerns pair probabilities for exactly two selected coordinates
and the full covariance-support graph. It gives the local
\(|h|\operatorname{dist}(B,\mathcal A)\) factor needed for a separate
finite-precision crossover analysis.

Equations (21)--(22) are cross-only. They cannot be added blindly to a
claimed formula for the full weighted covariance gauge: laws with \(x\)
away from zero can alter or cancel within-pair covariances while creating
different cross-block behavior. The matching constructions in (13)--(14)
keep the within-pair coefficients order one by (23), but this note does not
prove that all away-from-matching branches are uniformly dominated in a
full local volume calculation. It therefore derives no covering exponent.

It does not describe a transform library, price metadata, or establish
physical page-read feasibility.
