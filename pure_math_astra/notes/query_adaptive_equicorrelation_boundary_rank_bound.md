# Rank-two boundary bound for the equicorrelation adaptive sketch; depends on query_adaptive_complex_water_counterexample.md, query_adaptive_complex_water_counterexample_review.md.

Status: a sharper supporting boundary estimate. It makes no originality or
Cassette-sufficiency claim.

Let \(q\in\mathbb C^4\) have \(\sum_iq_i=0\), write
\(a=\operatorname{Re}q\), \(b=\operatorname{Im}q\), and set

\[
 B=aa^T+bb^T,\qquad V=\operatorname{tr}B,
 \qquad
 H=\max_{i<j}\bigl(|q_i-q_j|^2+2(a_i+a_j)\bigr).
\tag{1}
\]

The boundary threshold is

\[
 C(q)=\sqrt{(1-H)^2+4V}-H.
\tag{2}
\]

We prove

\[
 \sup_{\sum_iq_i=0}C(q)<{189\over100}.
\tag{3}
\]

This improves the earlier coarse constant below \(1.998\). Combined with
the already-proved finite-\(\eta\) passage, it permits the same
equicorrelation counterexample with any fixed coefficient larger than
\(189/100\).

## 1. The slack identity

Put \(P=I-\mathbf1\mathbf1^T/4\),

\[
 e_{ij}=H-\bigl(|q_i-q_j|^2+2(a_i+a_j)\bigr)\ge0
 \quad(i<j),
\]

and let \(E\) be the symmetric matrix with off-diagonal entries \(e_{ij}\)
and zero diagonal. Summing the six pair expressions gives

\[
 \epsilon:=H-{2V\over3}={1\over6}\sum_{i<j}e_{ij}\ge0.
\tag{4}
\]

Then

\[
 B={H\over2}P-2P\operatorname{Diag}(a)P+{1\over2}PEP.
\tag{5}
\]

To verify (5), let \(F\) have zero diagonal and the pair expressions as
its off-diagonal entries. Directly,

\[
 F=(d+2a)\mathbf1^T+\mathbf1(d+2a)^T-2B-4\operatorname{Diag}(a),
 \qquad d_i=B_{ii}.
\]

Since \(E=H(\mathbf1\mathbf1^T-I)-F\), multiplication by \(P\) on both
sides gives \(PEP=-HP+2B+4P\operatorname{Diag}(a)P\), which is (5).
The signs in (5) are therefore fixed by the off-diagonal slack definition.

When \(E=0\), put \(\alpha=\|a\|_2^2\). Since
\(\operatorname{tr}(P\operatorname{Diag}(a)P)^2=\alpha/2\), (5) gives

\[
 \operatorname{tr}B^2={V^2\over3}+2\alpha.
\tag{6}
\]

On the other hand,
\(\operatorname{tr}B^2=\alpha^2+(V-\alpha)^2+2(a\cdot b)^2\). Thus

\[
 {V^2\over3}+2\alpha\ge\alpha^2+(V-\alpha)^2.
\tag{7}
\]

If \(V=0\), then \(q=0\) and the displayed conclusion is immediate.
For \(V>0\), write \(t=\alpha/V\).  Maximizing
\(t/(t^2-t+1/3)\) over \(0\le t\le1\) gives

\[
 V\le3+2\sqrt3
 \qquad(E=0).
\tag{8}
\]

The maximum occurs at \(t=1/\sqrt3\). As a check on the real case,
\(q=(1/2,1/2,1/2,-3/2)\) has \(V=3\), \(H=2\), zero slack, and
\(C(q)=\sqrt{13}-2\).

## 2. A uniform bound below 1.89

Write the right side of (5) as \(B=M+R\), with

\[
 M={H\over2}P-2P\operatorname{Diag}(a)P,
 \qquad R={1\over2}PEP.
\]

The same trace calculation as above and \(\|a\|^2\le V\) give

\[
 \|M\|_F^2={3H^2\over4}+2\|a\|_2^2
 \le {3H^2\over4}+2V.
\tag{9}
\]

Also, \(\sum_{i<j}e_{ij}=6\epsilon\), so

\[
 \|R\|_F\le{1\over2}\|E\|_F
 \le3\sqrt2\,\epsilon.
\tag{10}
\]

Because \(B\succeq0\), \(\operatorname{rank}B\le2\), and
\(\operatorname{tr}B=V\), its Frobenius norm is at least \(V/\sqrt2\).
Equations (9)--(10) therefore imply the necessary inequality

\[
 {V\over\sqrt2}
 \le\sqrt{{3H^2\over4}+2V}+3\sqrt2\,\epsilon.
\tag{11}
\]

Assume for contradiction that \(C(q)\ge c=189/100\).  By (4),
\(H=2V/3+\epsilon\ge0\), so \(H+c>0\).  Moving \(H\) to the other
side of (2) and then squaring therefore preserves the inequality and gives

\[
 \epsilon\le\bar\epsilon:={22\over867}V-{89\over200}.
\tag{12}
\]

For fixed \(V\), the right side of (11), after writing
\(H=2V/3+\epsilon\), increases with \(\epsilon\ge0\): both its radical
and its final linear term do.  If (12) can hold, then
\(\bar\epsilon\ge\epsilon\ge0\), so replacing \(\epsilon\) by
\(\bar\epsilon\) preserves (11).  Moreover,

\[
 {V\over\sqrt2}-3\sqrt2\,\bar\epsilon>0.
\]

Indeed, after substituting (12), this quantity is
\(245\sqrt2V/578+267\sqrt2/200\).  We may therefore subtract the final
term from the right side of (11) and square.  The difference between the
square of the resulting left side and the square of the remaining radical is

\[
 {V^2\over6}-7V\bar\epsilon+{69\over4}\bar\epsilon^2-2V
 ={25\over167042}V^2+{4193\over5780}V+{546549\over160000}>0.
\tag{13}
\]

This contradicts (11). Hence \(C(q)<189/100\) pointwise.

The gap is uniform. The planar diameter estimate already used in the
equicorrelation proof gives

\[
 H\ge{3V\over4}-2\sqrt V.
\tag{14}
\]

For \(V\ge4096\), its right side is at least
\(25V/36-11/25\), which is exactly the threshold equivalent to
\(C(q)\le47/25\).  To see the stated comparison, its difference from that
threshold is \(V/18-2\sqrt V+11/25\), which is positive at \(V=4096\)
and increasing for \(\sqrt V\ge64\).  Hence a sequence with \(C(q)\)
tending to \(189/100\)
has bounded \(V\). Mean-zero quadruples with bounded \(V\) form a compact
set, and \(C\) is continuous there. Since equality in (3) is impossible,
the maximum on that compact set is strictly below \(189/100\), proving
(3).

## Consequence and limit

The finite-\(\eta\) dichotomy in
`query_adaptive_complex_water_counterexample.md` applies whenever the
boundary coefficient is uniformly below the selected \(c\). Thus it yields

\[
 \Psi_{2,\mathbb C}(\mathbf1\mathbf1^*+\eta I_4)
 \le {189\over100}\eta
\]

for all sufficiently small \(\eta>0\). This remains an existential
adaptive-sampler statement. It does not supply a finite-word selector,
physical page bound, or a growing Cassette resource frontier.
