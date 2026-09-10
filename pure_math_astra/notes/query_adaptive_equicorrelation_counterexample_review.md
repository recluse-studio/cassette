# Independent audit of the complex equicorrelation counterexample

Status: correctness review of the proposed bound
\(\Psi_{2,\mathbb C}(\mathbf1\mathbf1^*+\eta I_4)\leq(1999/1000)\eta\)
for sufficiently small positive \(\eta\).  The argument below verifies the
reduction and constants.  It does not make an originality claim.

Put \(G_\eta=\mathbf1\mathbf1^*+\eta I_4\), and let \(z\) obey the
complex two-sparse polar constraints.  Direct two-by-two inversion gives

\[
 |z_i-z_j|^2+\eta(|z_i|^2+|z_j|^2)\leq\eta(2+\eta)
 \qquad(i<j).
\tag{1}
\]

For \(c>0\), polar ellipsoid containment at variance \(c\eta\) is exactly

\[
 {W\over(1+c)\eta}+{4a^2\over4+(1+c)\eta}\leq1,
 \qquad
 a=\left|{1\over4}\sum_i z_i\right|,\quad
 W=\sum_i|z_i-a|^2,
\tag{2}
\]

after a harmless common phase makes the mean \(a\) nonnegative real.
Thus (2) retains the full coordinate-mean problem through atomic polarity.

## Verified compactness estimates

Write \(y_i=z_i-a\), so \(\sum_i y_i=0\), and set \(D=1-a^2\).
Summing (1) over all six pairs uses

\[
 \sum_{i<j}|y_i-y_j|^2=4W,
 \qquad
 \sum_{i<j}(|z_i|^2+|z_j|^2)=3(4a^2+W),
\tag{3}
\]

and yields

\[
 (4+3\eta)W\leq12\eta D+6\eta^2.
\tag{4}
\]

In particular \(D\geq-\eta/2\).  This also supplies the auxiliary bound
needed below when \(D/\eta\to+\infty\).

Let \(\delta=\max_{i<j}|z_i-z_j|\).  Planar Jung gives
\(W\leq4\delta^2/3\).  For a pair attaining \(\delta\),

\[
 |z_i|^2+|z_j|^2
 \geq2a^2-2a|y_i+y_j|
 \geq2a^2-2a\sqrt W.
\tag{5}
\]

The last inequality follows from \(y_i+y_j=-(y_k+y_l)\): its square is at
most both \(2(|y_i|^2+|y_j|^2)\) and
\(2(|y_k|^2+|y_l|^2)\), hence at most \(W\).  Substitution in (1) verifies

\[
 W\leq{8\over3}\eta D+{4\over3}\eta^2
       +{8\over3}\eta a\sqrt W.
\tag{6}
\]

If \(D/\eta\to+\infty\), (4) first gives
\(W=O(\eta D)\); division of (6) by \(\eta D\) then gives

\[
 {W\over\eta D}\leq{8\over3}+o(1).
\tag{7}
\]

Using the first term of (2) and the bound
\(4a^2/[4+(1+c)\eta]\leq1-D\), this excludes a violation of (2) for
every fixed \(c>5/3\).  This part of the proposed compactness split is
sound.

If \(D/\eta\) is bounded, (6) implies \(W=O(\eta^2)\), while
\(a=1+O(\eta)\).  Thus, after a subsequence,

\[
 z_i=1+\eta(m+q_i)+o(\eta),
 \qquad \sum_iq_i=0,
\tag{8}
\]

where the phase convention makes \(m\) real.  The limiting pair constraints
are

\[
 4m+H\leq1,
 \qquad
 H=\max_{i<j}\bigl(|q_i-q_j|^2+2\operatorname{Re}(q_i+q_j)\bigr).
\tag{9}
\]

Putting \(V=\sum_i|q_i|^2\), the coefficient of \(\eta\) in the left
side of (2) minus one is at most

\[
 {1-c-2H\over4}+{V\over1+c}.
\tag{10}
\]

It is nonpositive exactly when

\[
 c\geq C(q):=\sqrt{(1-H)^2+4V}-H.
\tag{11}
\]

This verifies the stated boundary threshold.

## Verified uniform boundary gap

The average over the six quantities defining \(H\) is \(2V/3\), so

\[
 H\geq{2V\over3}.
\tag{12}
\]

Since \(C\) decreases in \(H\), for \(V\leq1024\),

\[
 C(q)\leq
 \sqrt{\left(1-{2V\over3}\right)^2+4V}-{2V\over3}
 =\sqrt{\left(2+{2V\over3}\right)^2-3}-{2V\over3}
 \leq2-{9\over4108}.
\tag{13}
\]

The final estimate follows because the displayed function increases with
\(V\), and at \(V=1024\) its gap below two is at least
\(3/(4+4\cdot1024/3)=9/4108\).

For the other range, Jung and (5) give

\[
 H\geq {3V\over4}-2\sqrt V\geq{11V\over16}
 \qquad(V\geq1024).
\tag{14}
\]

The second inequality is exactly where the cutoff \(1024=32^2\) is used.
Monotonicity in \(H\), followed by squaring positive sides, gives

\[
 C(q)\leq{21\over11}+{8\over11V}<1.911.
\tag{15}
\]

For completeness, if \(h=11V/16\) and
\(d=21/11+8/(11V)\), then

\[
 (h+d)^2-\bigl((h-1)^2+4V\bigr)=d^2\geq0,
\tag{16}
\]

which proves (15) without an uncontrolled expansion.

Equations (13)--(15) give the strict uniform bound

\[
 C(q)\leq2-{9\over4108}<1.998<1.999.
\tag{17}
\]

Therefore a violating bounded-boundary sequence at \(c=1999/1000\) is
impossible by (10)--(11), while (7) excludes the only other asymptotic
regime.  The proposed sufficiently-small-\(\eta\) upper bound is supported.

## Audit conclusion

I found no false pass in the pair-polar formula, the Jung step, the
large-\(V\) constant, or the compactness dichotomy.  A full proof should
state the final contradiction sequentially: assume \(\eta_n\downarrow0\)
and a polar \(z^{(n)}\) violates (2), phase-normalize its mean, then pass to
the two alternatives for \(D_n/\eta_n\).  This avoids claiming an explicit
threshold \(\eta_0\), which the compactness proof does not calculate.
