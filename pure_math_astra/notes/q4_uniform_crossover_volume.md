# Uniform four-coordinate volume near a reciprocal spectrum

Status: a supporting theorem in the fixed, query-independent operator model.
The proof closes the full-volume question left open in
q4_matching_crossover_gauge.md. It does not establish originality or a
Cassette resource frontier.

Fix real numbers a,b strictly between zero and one, with a,b distinct from
one half, a≠b, and a+b≠1. Let

\[
 p(h)=(a,1-a+h,b,1-b-h),\qquad
 D(h)=\operatorname{Diag}\frac{p_i(h)}{1-p_i(h)} .
 \tag{1}
\]

For sufficiently small |h| the spectrum is positive and simple, its gaps
stay bounded below, and its rank-two water level is t=1. Write β=1 for the
real field and β=2 for the complex field. All constants below are uniform
for sufficiently small ε>0 and |h|, and may depend on a,b.

## Statement

Let μ_h denote normalized invariant measure on the conjugacy orbit of
D(h), and let Φ_2 be the optimal variance of a single unbiased random
operator with at most two encoded columns on each outcome. Then

\[
 \mu_h\{G:\Phi_2(G)\le1+\varepsilon\}
 \asymp \varepsilon^{5\beta/2}
   \min\{\sqrt{\varepsilon},\varepsilon/|h|\}^{3\beta},
 \tag{2}
\]

where ε/|h| is interpreted as infinity at h=0. Equivalently, the volume is

\[
 \asymp
 \begin{cases}
  \varepsilon^{4\beta},& |h|\le\sqrt{\varepsilon},\\
  |h|^{-3\beta}\varepsilon^{11\beta/2},
       & |h|\ge\sqrt{\varepsilon}.
 \end{cases}
 \tag{3}
\]

The minimum size of a transform library covering that orbit at excess
variance ε has the reciprocal order. In particular its index length is

\[
 4\beta\log_2(1/\varepsilon)
 +3\beta\log_2\max\{1,|h|/\sqrt{\varepsilon}\}+O(1).
 \tag{4}
\]

This is a two-parameter statement. Applying a fixed-h exponent and hiding
its h-dependent constant would miss the crossover at ε of order h².

## Uniform local reduction

Use six off-diagonal orbit coordinates B∈F^6 near a diagonal point, as in
dependence_support_transform_rate.md. The proof of its normal form is
uniform on this compact, positive, uniformly gapped spectral family:

\[
 \Phi_2(G_h(B))-1\asymp
 \|B\|_2^2+
 \min_{\nu\in\mathcal P(p(h))}
       \|B\circ c(\nu)\|_2 .
 \tag{5}
\]

Here c_ij=Cov(I_i,I_j)/(p_i p_j), and the law selects exactly two indices.
The proof retains this weighted minimum. Its comparison with a finite
unweighted support list has constants that collapse at h=0.

The quantities p_i p_j are bounded above and below by positive constants.
Thus unnormalized covariances may replace c in (5). Chart density is also
uniformly bounded above and below. Quantitative rigidity confines all
small sublevels to the finitely many diagonal neighborhoods, uniformly in h.
It therefore suffices to calculate the Euclidean volume of the sublevel in
(5) at one such neighborhood.

## The entire covariance polygon

Put x=Pr(S={1,2}) and r=Pr(S={1,3})−ab. The six pair masses are

\[
 (z_{12},z_{13},z_{14},z_{23},z_{24},z_{34})
 =(x,ab+r,a-x-ab-r,b-x+h-ab-r,
       1-a-b+ab+r,x-h).
 \tag{6}
\]

They must be nonnegative. These inequalities describe every legal law,
including laws away from the reciprocal matching. In particular
x≥max(0,h). Its matching covariances are

\[
 c_{12}=x-A-ah,\quad c_{34}=x-C-(1-b)h,\quad
 A=a(1-a),\quad C=b(1-b),
 \tag{7}
\]

and its cross covariances, ordered 13,14,23,24, are

\[
 (r,\ ah-x-r,\ (1-b)h-x-r,\ r+(b-a)h+h^2).
 \tag{8}
\]

The symbols c in (7)–(8) denote unnormalized covariances only.
A≠C follows from a≠b and a+b≠1.

The cross-gauge note proves the following two facts directly from (6)–(8).
Every pair of distinct cross entries contains an entry of magnitude at
least γ|h|, for some fixed γ>0. Also each prescribed cross entry can be
made zero while the other three have magnitude at most Γ|h|: take
x=max(0,h) and choose the corresponding r. Both matching entries then
stay bounded away from zero.

## Two compactness bounds for the remaining branches

At h=0 the covariance vector has the form

\[
 (x-A,x-C,r,-x-r,-x-r,r).
 \tag{9}
\]

No matching covariance can vanish together with a cross covariance in a
legal law. For example, x=A,r=0 forces

\[
 z_{14}=a(a-b),\qquad z_{23}=(1-a)(b-a),
 \tag{10}
\]

which have opposite signs. Likewise x=A,r=−x forces

\[
 z_{13}=a(a+b-1),\qquad
 z_{24}=(1-a)(1-a-b),
 \tag{11}
\]

which have opposite signs. For x=C,r=0 the conflicting masses are
z_14=(a-b)(1-b) and z_23=b(b-a). For x=C,r=−x they are
z_13=b(a+b-1) and z_24=(1-b)(1-a-b). The matching entries cannot both
vanish because A≠C.

Consequently there is η>0 such that every pair of coordinates involving a
matching entry has at least one magnitude ≥η, for all sufficiently small
|h|. To justify uniformity, a contrary sequence has a convergent subsequence
of feasible (h,x,r), since pair probabilities lie in [0,1]. Its limit at
h=0 would contradict (10), (11), or A≠C.

Combine this fact with the cross-pair bound. Every legal covariance vector
has at least five entries of magnitude ≥γ'|h|, with γ'>0 uniform.

Choose a fixed small neighborhood U of (x,r)=(0,0) in which both matching
entries remain bounded away from zero. Outside U, every feasible vector at
h=0 has at least four nonzero entries. Indeed, if r and x+r are nonzero,
all four cross entries are nonzero. If exactly one is zero, two cross
entries are nonzero and neither matching entry can vanish, by the preceding
argument. If both are zero, (x,r)=(0,0), which lies in U.

A second compactness argument now gives four entries of magnitude at least
η'>0 uniformly for all feasible laws outside U and small |h|. The selected
four coordinates may vary with the law. There are only finitely many
coordinate choices; no parameter integration is needed.

## Volume of the two branches

Set

\[
 w=\min\{\sqrt{\varepsilon},\varepsilon/|h|\}.
 \tag{12}
\]

A sublevel point in (5) has every coordinate O(√ε). If a minimizing law
lies in U, its two matching coordinates are O(ε), and at least three
cross coordinates are O(w). The remaining cross coordinate is O(√ε).
A finite union of such boxes has volume at most

\[
 C\varepsilon^{2\beta}w^{3\beta}\varepsilon^{\beta/2}.
 \tag{13}
\]

One of the explicit zero-cross-entry laws following (8) supplies a box of
this same order inside a suitably scaled sublevel. The law is common to
all B in that box. The quadratic term costs O(ε); the two matching
coordinates contribute O(ε), and the three other cross contributions
cost O(|h|w)≤O(ε). This proves the lower bound in (2).

For a minimizing law outside U, choose its four entries of magnitude ≥η'.
Those B coordinates are O(ε). Among the remaining two coordinates at least
one covariance has magnitude ≥γ'|h|, since at least five entries have
that size. The associated B coordinate is O(w); the last is O(√ε).
The finite union of these boxes has volume at most

\[
 C\varepsilon^{4\beta}w^\beta\varepsilon^{\beta/2}.
 \tag{14}
\]

The ratio of (14) to (13) is

\[
 (\varepsilon/w)^{2\beta}
 =\begin{cases}
   \varepsilon^\beta,&|h|\le\sqrt{\varepsilon},\\
   |h|^{2\beta},&|h|\ge\sqrt{\varepsilon}.
  \end{cases}
 \tag{15}
\]

It is bounded and tends to zero in the joint limit. Thus away-from-matching
laws cannot change the leading volume order, although they invalidate a
single matching-branch formula for the full gauge. Equations (13)–(15)
prove (2)–(3).

## Uniform library bound

The measure union bound gives the reciprocal-volume lower bound for any
library. For the upper bound use the common-law box from (13), with radii
ε,ε,w,w,w,√ε and small fixed prefactors. Every radius is between ε and
√ε. A product or inverse of two such local group elements has coordinate
sum or difference plus an O(ε) remainder, uniformly in h: its Taylor
remainder is quadratic in coordinates of norm O(√ε). This remainder fits
within a constant multiple of every coordinate radius.

For a simple spectrum the stabilizer H consists of coordinate signs in
the real case and coordinate phases in the complex case. For the centered
horizontal coordinate box, define the saturated lift

\[
 E=\{\exp(X)h:X\text{ belongs to the box},\ h\in H\}.
 \tag{16}
\]

Conjugation by H preserves each coordinate disk and the horizontal space.
The box is symmetric under X↦−X, so
h^{-1}exp(−X)=exp(−h^{-1}Xh)h^{-1} belongs to E whenever exp(X)h does.
Thus E is inverse-closed and EE^{-1}=E^{-1}E. The preceding product
estimate puts that set in a fixed dilation of E. Saturating by H is
essential: the horizontal section alone has zero group Haar measure in
the complex case. Haar disintegration over H makes the measure of E
comparable to the orbit-box measure, of the order in (13).

Choose disjoint left translates of a sufficiently small fixed dilation of
E until the collection is maximal. There can be at most reciprocal-order
many translates, by Haar measure. Maximality makes the translates of
EE^{-1} cover the group: an uncovered translate of E would be disjoint
from the collection and could be added. The product bound makes these
covering sets acceptable common-law boxes after adjusting fixed prefactors.
Projecting to the orbit proves the uniform upper bound and hence (4).

This packing proof supplies a cardinality bound. It does not supply a
uniformly cheap index selector or a finite-word arithmetic implementation.

## Interpretation and next boundary

The exact reciprocal locus does not create an isolated usable phenomenon:
its larger acceptable region persists while spectral mismatch |h| is at
most order √ε. Below that accuracy the generic exponent returns, with its
explicit |h| prefactor. This removes an ambiguity in applying the fixed
spectrum asymptotic to approximate spectra.

The result remains a restricted index theorem. It has not reduced encoded
payload, transform workspace, or fresh column traffic. Independent
reconstruction checked the covariance thresholds and branch-volume
comparison. A separate review required the explicit stabilizer saturation
and translate-product order in the group argument; both are now stated.
