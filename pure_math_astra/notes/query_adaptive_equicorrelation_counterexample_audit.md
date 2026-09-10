# Equicorrelation rank-one audit for a possible complex counterexample; depends on query_adaptive_atomic_dual.md, query_adaptive_subspace_containment.md.

Status: exact reductions and a decisive limitation of the zero-sum route.
No global complex upper bound below the water level is proved here.

Later resolution: query_adaptive_complex_water_counterexample.md closes
the constant-vector boundary and the finite-eta passage. Two independent
correctness reconstructions support Psi_complex(11^T+eta I_4)<=1.999 eta
for all sufficiently small eta, strictly below the spectral water level.
This note preserves the intermediate reduction and its former gap.

Let

\[
 G_\eta=\mathbf1\mathbf1^*+\eta I_4,\qquad \eta>0.
\tag{1}
\]

Its spectral water level for \(s=2\) is exactly

\[
 t_2(G_\eta)=\sqrt{1+4\eta+\eta^2}-1
              =2\eta-\frac32\eta^2+O(\eta^3).
\tag{2}
\]

Thus a global complex adaptive upper bound \(c\eta\) with \(c<2\) would
disprove a universal complex water-level lower benchmark.

## 1. Exact complex polar constraints

For every coordinate pair \(i,j\), direct inversion gives

\[
 z_{ij}^*G_{\eta,ij}^{-1}z_{ij}
 ={ |z_i-z_j|^2+\eta(|z_i|^2+|z_j|^2)\over\eta(2+\eta)}.
\tag{3}
\]

Hence a complex polar vector is exactly a four-point configuration in the
complex plane satisfying

\[
 |z_i-z_j|^2+\eta(|z_i|^2+|z_j|^2)\le\eta(2+\eta)
 \quad(i<j).
\tag{4}
\]

At a candidate variance level \(v=c\eta\), its ellipsoid value is

\[
 z^*(G_\eta+c\eta I)^{-1}z
 ={\|z-\bar z\mathbf1\|_2^2\over(1+c)\eta}
 +{4|\bar z|^2\over4+(1+c)\eta},
 \qquad \bar z={1\over4}\sum_i z_i.
\tag{5}
\]

Equations (4)--(5) are an exact global formulation; they include every
query through atomic polarity and do not weaken \(\mathbb EY=x\):
\(\Psi_{2,\mathbb C}(G_\eta)\le c\eta\) holds exactly when every
configuration satisfying (4) has (5) at most one.

## 2. What the zero-sum calculation proves, and what it cannot prove

The constant polar vector

\[
 z_i=\sqrt{1+\eta/2}\quad(i=1,\ldots,4)
\tag{6}
\]

saturates every inequality in (4). At \(v=\eta\), equation (5) equals
one, and it is larger than one for every \(v<\eta\). Therefore

\[
 \Psi_{2,\mathbb C}(G_\eta)\ge\eta.
\tag{7}
\]

No scheme with coefficient below one can work globally.

For a zero-sum query, two-sparse atoms proportional to roots
\(e_i-e_j\) preserve the high coordinate exactly and have cost only in the
\(\eta I\) part. This makes a coefficient near one plausible on that
restricted query class. It does not furnish a global sampler: an outcome
with root sum zero cannot have the same high coordinate as a query with
nonzero \(\sum_i x_i\). Mixing it with a high-sum outcome introduces a
rank-one error, which is not of order \(\eta\) unless the mixing is
controlled at the same scale.

Thus the root calculation alone neither proves \(\Psi_{2,\mathbb C}<t_2\)
nor contradicts the rank-two spectrahedral benchmark.

## 3. The remaining leading-order geometry

Write

\[
 z_i=a+\sqrt\eta\,q_i,\qquad \sum_iq_i=0.
\tag{8}
\]

Every bounded polar sequence has bounded \(a\) and \(q\). Dividing (4)
by \(\eta\) and taking a limit gives

\[
 |q_i-q_j|^2+2|a|^2\le2.
\tag{9}
\]

At the same scale, (5) tends to

\[
 |a|^2+{\|q\|_2^2\over1+c}.
\tag{10}
\]

Let \(D=\max_{i<j}|q_i-q_j|\). The planar Jung bound puts four complex
points of diameter \(D\) in a disk of radius at most \(D/\sqrt3\), hence

\[
 \|q\|_2^2\le{4\over3}D^2
 \le{8\over3}(1-|a|^2).
\tag{11}
\]

This coarse universal estimate would make the right side of (10) at most
one for \(c\ge5/3\), away from its equality boundary. It is not a finite-
\(\eta\) proof: at \(|a|=1\), \(q=0\), the limiting inequality is tight
while the order-\(\eta\) terms decide containment. A valid counterexample
requires that missing boundary analysis, or an explicit unbiased scheme
that handles nonzero-sum queries.

The exact reduction narrows the issue to a constrained four-point planar
problem. It does not justify claiming a coefficient below two.
