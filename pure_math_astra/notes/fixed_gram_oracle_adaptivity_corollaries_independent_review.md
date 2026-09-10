# fixed_gram_oracle_adaptivity_corollaries_independent_review.md — independent review of orbit-oracle basis, growing-gap, and source-trained-schedule corollaries; depends on fixed_gram_orbit_static_oracle_minimax_independent_proof.md, query_adaptive_general_basis_reversal.md, query_adaptive_finite_catalog_bridge.md, and ../../MATHS.md.

## Verdict

All four proposed corollaries follow in their stated real oracle models.
The static lower statements concern source- and query-independent support
laws. The \(O(2)\) example shows exactly why a source-trained schedule lies
outside that model. No novelty or Cassette-goal acceptance follows from
these correctness checks.

## 1. A free fixed right basis does not improve the static orbit value

Let \(Q\in O(q)\) be fixed before the source and query. Replacing source
columns \(A\) by \(AQ\) and query \(x\) by \(Q^Tx\) leaves the target
action unchanged. Its orbit Gram matrix is

\[
(AQ)^T(AQ)=Q^TGQ.
\]

The fixed-Gram orbit identity gives the arbitrary-nonlinear static value
\(\nu_s(Q^TGQ)\). The trace water lower bound depends only on the
eigenvalues, so

\[
\nu_s(Q^TGQ)\ge t_s(G)
\qquad\text{for every }Q.
\tag{1}
\]

Choose \(Q\) to diagonalize \(G\), with
\(Q^TGQ=\operatorname{Diag}(\lambda_i)\). Let \(t=t_s(G)\) and
\(\theta_i=\lambda_i/(\lambda_i+t)\). The \(\theta_i\) lie in \((0,1)\)
and sum to \(s\), so an exactly-\(s\) subset law with those marginals
exists. Its Horvitz--Thompson operator

\[
L=\operatorname{Diag}(1_{i\in S}/\theta_i)
\]

is operator-unbiased and has diagonal risk

\[
\lambda_i(\theta_i^{-1}-1)=t
\]

in every coordinate. Thus its worst-unit-query risk is \(t\), proving

\[
\inf_{Q\in O(q)}\nu_s(Q^TGQ)=t_s(G).
\tag{2}
\]

This establishes the claimed free-fixed-basis static benchmark.

## 2. General real basis reversal becomes an oracle separation

For \(q\ge4\), \(2\le s\le q-2\), and any nonscalar positive spectrum,
the reviewed basis-reversal theorem supplies a real rotation with Gram
matrix \(G\) such that

\[
\Psi_s(G)<t_s(G).
\tag{3}
\]

The query-dependent fixed-Gram orbit identity makes \(\Psi_s(G)\) the
minimax value for arbitrary nonlinear source-independent query-adaptive
oracles. Equations (1)--(2) make \(t_s(G)\) the best static arbitrary
nonlinear value even after a free fixed right orthogonal basis. Therefore
(3) is a strict real oracle adaptivity separation. This uses the
basis-reversal theorem's local constants; it supplies no uniform factor
over all spectra or dimensions.

## 3. The equicorrelation family has a growing expected-read gap

Let

\[
G=(\mathbf1\mathbf1^T+\eta I_4)^{\oplus m},
\]

where \(\eta\) is one of the sufficiently small positive parameters for
which the reviewed finite rational real catalog has hard support \(2m\)
and risk at most \(19\eta/10\). Assume also \(\eta\le1/100\).

The catalog gives a query-dependent orbit oracle. For any source
\(A\) with \(A^TA=G\), its output risk is exactly its coefficient
\(G\)-risk. It therefore has uniform orbit risk at most \(19\eta/10\).

Now allow a static arbitrary nonlinear decoder a free fixed right basis
\(Q\), but require its support schedule to be independent of both \(A\)
and \(x\). Its transformed Gram is \(Q^TGQ\). If its uniform orbit risk is
at most \(19\eta/10\), the orbit identity and the expected-read trace
identity give

\[
\begin{aligned}
\frac{\bar s}{m}
&\ge
\frac{4+\eta}{4+(29/10)\eta}+\frac3{29/10}\\
&=
\frac{4+\eta}{4+2.9\eta}+\frac{30}{29}\\
&\ge
\frac{4010}{4029}+\frac{30}{29}\\
&=
\frac{237160}{116841}
>\frac{101}{50}.
\end{aligned}
\tag{4}
\]

The first summand decreases with \(\eta\), so the third line uses
\(\eta\le1/100\). This bound concerns expected selected columns; occasional
full reads do not evade it. The adaptive upper law still has a hard \(2m\)
support cap.

The orbit theorem permits \(p=q\), so no Gaussian lift is needed. The
strict statement has the quantifiers

\[
\text{for every static decoder with }\bar s\le(101/50)m,\quad
\text{there exist }A\in\mathcal O_G,\ \|x\|_2=1
\]

for which its risk exceeds \(19\eta/10\). It does not name one source
that defeats every decoder, and it is not a finite-word or physical-page
claim.

## 4. Why source-trained schedules are outside the lower theorem

Let

\[
J=\begin{pmatrix}0&-1\\1&0\end{pmatrix},
\qquad A=[a_1\ a_2]\in O(2).
\]

If \(\det A=+1\), then \(a_2=Ja_1\). Select column \(1\), and reconstruct

\[
A=[a_1\ Ja_1].
\]

If \(\det A=-1\), then \(a_2=-Ja_1\), hence \(a_1=Ja_2\). Select column
\(2\), and reconstruct

\[
A=[Ja_2\ a_2].
\]

Thus the source-dependent rule “choose column \(1\) for determinant \(+1\),
column \(2\) for determinant \(-1\)” plus the selected-index bit and one
observed column reconstructs every \(A\in O(2)\) exactly. The signs are
correct because \(J^2=-I\).

This does not contradict the orbit lower bound. The selected support and
the branch bit depend on the source, while the lower theorem fixes the
schedule before the source and charges no free source-dependent resident
state. Any use of this rule must declare how that branch bit and its
source-dependent selection are supplied and charged.

## Scope

The results are real, exact-unbiased oracle statements. They permit
arbitrary nonlinear static decoding after selected-column access, but not
source-trained schedules or resident source-dependent decoder state. The
finite rational catalog gives an abstract finite law, not page, byte,
latency, or sequential-execution evidence.
