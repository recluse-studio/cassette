# Independent correctness review of the complex adaptive-water counterexample; depends on query_adaptive_atomic_dual.md, query_adaptive_complex_water_counterexample.md.

Status: correctness review only. The claimed strict complex counterexample is
correct after one local replacement in the large-\(V\) estimate below. This
is neither a novelty nor a Cassette-significance assessment.

## Claim reviewed

For

\[
 G_\eta=\mathbf1\mathbf1^*+\eta I_4,\qquad \eta>0,
\]

with complex queries and two-sparse unbiased estimators, put

\[
 \Psi_{2,\mathbb C}(G_\eta)=
 \sup_{\|x\|_2=1}\inf_{\mathbb EY=x,\ \|Y\|_0\le2}
 \mathbb E(Y-x)^*G_\eta(Y-x).
\]

Then, for all sufficiently small \(\eta>0\),

\[
 \Psi_{2,\mathbb C}(G_\eta)\le {1999\over1000}\eta
 <t_2(G_\eta),
 \qquad
 t_2(G_\eta)=\sqrt{1+4\eta+\eta^2}-1.
\tag{1}
\]

The final strict inequality follows from \(t_2(G_\eta)/\eta\to2\).
The stated water-level formula follows on inserting the eigenvalues
\(4+\eta,\eta,\eta,\eta\) in the size-two water equation and solving its
quadratic.

## 1. Exact polar test

The atomic-dual criterion reduces \(\Psi_{2,\mathbb C}(G_\eta)\le c\eta\)
to containment of its polar unit ball in the ellipsoid of \(G_\eta+c\eta I\).
For a pair \(i,j\), direct inversion gives the polar condition

\[
 |z_i-z_j|^2+\eta(|z_i|^2+|z_j|^2)\le\eta(2+\eta).
\tag{2}
\]

Pair conditions suffice: for fixed \(z_i\), minimizing the left-side
quadratic form over its other coordinate gives
\( |z_i|^2/(1+\eta)\le1\), which is precisely the singleton condition.

Let \(a=\frac14\sum_i z_i\), \(A=|a|^2\), and
\(W=\sum_i|z_i-a|^2\). The exact ellipsoid test is

\[
 {W\over(1+c)\eta}+{4A\over4+(1+c)\eta}\le1.
\tag{3}
\]

Thus (2)--(3) retain the full condition \(\mathbb EY=x\); they do not pass
to a singular-model surrogate.

## 2. Boundary model and its strict gap

For a zero-mean complex quadruple \(q\), set

\[
 V=\sum_i|q_i|^2,
 \qquad
 H=\max_{i<j}\bigl(|q_i-q_j|^2+2\operatorname{Re}(q_i+q_j)\bigr).
\tag{4}
\]

The pair average yields \(H\ge2V/3\). If \(d\) is the diameter, planar
Jung gives \(V\le4d^2/3\). For a diameter pair,
\(|q_i+q_j|\le\sqrt V\), because the complementary pair has the opposite
sum. Hence

\[
 H\ge {2V\over3},
 \qquad H\ge {3V\over4}-2\sqrt V.
\tag{5}
\]

At the constant-vector boundary write \(z_i=1+\eta w_i\),
\(w_i=m+q_i\), and \(\sum_iq_i=0\). Dividing (2) by \(\eta^2\) and
taking \(\eta\downarrow0\) gives

\[
 4\operatorname{Re}m+H\le1.
\tag{6}
\]

The first-order coefficient of the left side of (3), minus one, is

\[
 B_c(w)=2\operatorname{Re}m-{1+c\over4}+{V\over1+c}.
\tag{7}
\]

Using equality in (6), its zero occurs at

\[
 C(q)=\sqrt{(1-H)^2+4V}-H.
\tag{8}
\]

The expression decreases with \(H\). For \(0\le V\le1024\), the first
bound in (5) and rationalization give

\[
 C(q)\le2-{9\over4108}=:c_b.
\tag{9}
\]

Indeed, the gap from two is

\[
 {3\over2+2V/3+\sqrt{1+8V/3+4V^2/9}}
 \ge {9\over4108}.
\]

For \(V\ge1024\), the second bound in (5) gives \(H\ge11V/16\). Put
\(\alpha=11/16\). Direct squaring, rather than the looser square-root
estimate, gives

\[
 \sqrt{(\alpha V-1)^2+4V}-\alpha V
 \le {2\over\alpha}-1={21\over11}<c_b.
\tag{10}
\]

To verify (10), add \(\alpha V\) and square: the linear and quadratic
terms match, while the remaining right-side constant is
\((2/\alpha-1)^2\ge1\). This replaces an over-loose intermediate
justification in the reviewed note; the claimed bound itself is valid.

Consequently, for \(c=1999/1000>c_b\), every boundary vector satisfies

\[
 B_c(w)\le-{c-c_b\over4}<0.
\tag{11}
\]

## 3. Finite-eta passage

Suppose, for contradiction, that (3) fails along \(\eta\downarrow0\).
Multiply each polar vector by a common phase so \(a\ge0\), and set
\(D=1-A\). Summing (2) over the six pairs gives

\[
 (4+3\eta)W+12\eta A\le12\eta+6\eta^2.
\tag{12}
\]

Thus \(D\ge-\eta/2\). For the centered values \(v_i=z_i-a\), their
zero sum implies \(|v_i+v_j|\le\sqrt W\). Applying (2) to a diameter
pair and then planar Jung gives

\[
 W\le {8\over3}\eta D+{4\over3}\eta^2
       +{8\over3}\eta a\sqrt W.
\tag{13}
\]

If \(D/\eta\to+\infty\), (12) first gives \(W=O(\eta D)\). Dividing
(13) by \(\eta D\), or solving its quadratic form, then gives

\[
 \limsup {W\over\eta D}\le{8\over3}.
\tag{14}
\]

The excess in (3) is at most \(W/((1+c)\eta)-D\), which is eventually
negative because \(1+c>8/3\). This contradicts failure of (3).

Otherwise, pass to a subsequence on which \(D/\eta\) is bounded above.
Together with \(D\ge-\eta/2\), (13) gives \(W=O(\eta^2)\), and
\(a-1=-D/(a+1)=O(\eta)\). Therefore
\(u_i=(z_i-1)/\eta\) is bounded. A further convergent subsequence has a
limit satisfying (6). Dividing the excess in (3) by \(\eta\) gives the
limit \(B_c(u)\), which is strictly negative by (11). This is incompatible
with a positive excess. Both subsequential alternatives contradict the
assumption, proving (3) for all sufficiently small \(\eta\).

## Verdict and scope

**Correct, with the large-\(V\) derivation repaired as in (10).** The
argument provides an existential family of complex two-sparse unbiased
estimators through the atomic convex formulation. It disproves the proposed
general complex water-level lower benchmark. It does not decide the
two-high/two-low family, supply a finite-word sampler, or establish
originality or consequential Cassette significance.
