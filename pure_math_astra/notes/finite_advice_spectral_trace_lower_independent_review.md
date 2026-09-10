# Independent review: finite-advice spectral trace lower bound

Verdict: the synthesis is correct after one support-bookkeeping repair.
In the random-output reduction and the concentration union, discard every
support with \(w_{\ell,S}=0\) before taking a conditional mean. A zero-mass
branch need not have an integrable output law, and it is never used by
exactness, risk, or the trace. With that repair, the theorem, advice bound,
and stated equicorrelation corollary follow in the declared finite-state
oracle model. This is a correctness review only; it makes no originality or
application-significance finding.

## 1. Measurable branch reduction and finite union

For a positive-probability support in a selected state, finite uniform
squared risk makes the branch output integrable at every legal used input.
A source-independent Borel output kernel then has a Borel conditional mean
on its Borel integrability set; assigning zero off that set gives a global
Borel branch function. Jensen preserves exactness and cannot increase risk
on the state cell. This is all the later proof needs.

The same statement is not justified for a zero-probability support: risk
places no integrability condition on that branch. It must simply be
removed. The number of remaining supports is still at most \(2^q\), so
all displayed union bounds are unchanged. Arbitrarily small *positive*
probabilities cause no problem. No probability is inverted in the trace
step.

For fixed \((\ell,S,z)\), conditional Haar concentration gives

\[
 \Pr\{\|P_{E_{\ell,S}}F_{\ell,S}\|>\epsilon\|F_{\ell,S}\|\}
 \le2^{(q-|S|)/2}e^{-(p-|S|)\epsilon^2/4}.
\]

The label-specific fixed basis is absorbed by replacing the Gram factor
\(R\) by \(RQ_\ell\). The physical queries are
\(Q_\ell(G_\ell+CI)^{-1/2}z\), normalized. Thus each state contributes
only \(|\mathcal Z|\) query values, not a product of different state query
sets. The complete union has at most \(N2^q|\mathcal Z|\) events, which
proves the stated \(\beta\) bound.

Crucially, concentration is taken on the full orbit for every fixed state
before the source encoder chooses its label. A source in the simultaneous
good event is therefore good for its selected state as well. Conditioning
first on a source-label cell would fail because that cell could select the
rare alignment event.

## 2. The finite-query trace bridge

For a selected state and a tested unit query, exact mean and risk give

\[
 B=\sum_Sw_S\|F_S\|^2
  =R(A,x)+\|Ax\|^2\le C+x^TGx.
\]

Splitting an output into its observed-span component, its unobserved
source-span component, and its component outside \(\operatorname{span}A\)
gives

\[
 |\langle u,Ax\rangle|
 \le(\sqrt{u^THu}+\epsilon\|u\|)\sqrt B.
\]

This uses Cauchy--Schwarz over the support law and no lower bound on a
support probability. At
\(x_z=(G+CI)^{-1/2}z/\|(G+CI)^{-1/2}z\|\), the identity

\[
 \frac{Ax_z}{\sqrt{C+x_z^TGx_z}}
 =A(G+CI)^{-1/2}z
\]

is exact: after multiplying the denominator squared by
\(\|(G+CI)^{-1/2}z\|^2\), the two terms combine to \(\|z\|^2=1\).

The net next approximates only the fixed linear functional
\(z\mapsto u^TA(G+CI)^{-1/2}z\). It never compares a decoder output at
nearby queries. Thus arbitrary Borel query dependence creates no gap.
The resulting quadratic inequality

\[
 a\sqrt{u^TK_Cu}\le\sqrt{u^THu}+\epsilon\|u\|
\]

implies
\(H\succeq a^2K_C-2a\epsilon I\). If the term on the right after
subtraction is nonpositive, \(H\succeq0\) suffices; otherwise square and
use \(K_C\preceq I\). Taking traces proves

\[
 s_{\ell(A)}\ge a^2f_G(C)-2aq\epsilon.
\]

This reconstruction covers \(C=0\): \(G+CI\) remains positive definite,
the finite test queries remain defined, and no division by \(C\) occurs.
It also proves the source-measure statement
\(\mu\{A:s_{\ell(A)}<L\}\le\beta\), because that set is contained in
the complement of the simultaneous good event. The source in the
nonempty good event depends on the finite decoder architecture; no claim
selects one source for all architectures.

## 3. Advice deficit calculation

With \(\Delta=f_G(C)-s\), \(\gamma=\Delta/q\),
\(\epsilon=\gamma/8\), and \(\delta=\sqrt\gamma/2\), one has
\(a^2\ge1-\gamma/4\) and \(f_G(C)\le q\). Hence

\[
 a^2f_G(C)-2aq\epsilon
 \ge f_G(C)-\Delta/4-\Delta/4
 =s+\Delta/2.
\]

A uniform cap \(s\) forces the low-read set to have measure one, so the
source-measure estimate forces \(\beta\ge1\). Rearrangement gives

\[
 \log N\ge\frac{(p-q)\gamma^2}{256}
 -\frac{3q}{2}\log2-q\log(1+4/\sqrt\gamma),
\]

and division by \(\log2\) gives the displayed bit bound. Negative right
sides are correctly noninformative.

## 4. Equicorrelation check and comparator

For one block, the spectrum is \(4+\eta,\eta,\eta,\eta\). At
\(C=19\eta/10\),

\[
 f_{H_\eta}(C)
 =\frac{4+\eta}{4+(29/10)\eta}+\frac{30}{29}
 \ge\frac{4010}{4029}+\frac{30}{29}
 =\frac{237160}{116841}.
\]

With \(a=19999/20000\), \(q=4m\), and \(\epsilon=1/1000\), the trace
lower bound is exactly

\[
 a^2m\frac{237160}{116841}-2a(4m)/1000
 =m\frac{2362016033293}{1168410000000}
 >\frac{101}{50}m,
\]

with the stated excess. The exponent in the required dimension condition
is likewise \(4/\epsilon^2=4{,}000{,}000\), and
\(3q/2=6m\), so equation (22) is correct.

The existing adaptive construction is on the same full Gram orbit and
uses the same Euclidean output-risk metric: for every \(A\) with
\(A^TA=H_\eta^{\oplus m}\), a coefficient law \(Lx\) is implemented as
\(ALx\), has exact mean \(Ax\), and has squared output risk
\((Lx-x)^TG(Lx-x)\). Its real finite catalog has hard cap \(2m\) and,
for sufficiently small \(\eta\), risk at most \(1.9\eta\). This is a
query-dependent support law, while the lower theorem concerns a static
law within each finite source-selected state; the comparison is therefore
within the announced distinct oracle classes.

## Required repair

In `finite_advice_spectral_trace_lower.md`, replace references to “all
state/support/query triples” after the conditional-mean reduction by
“all positive-probability state/support/query triples,” and say that
zero-mass supports are discarded before that reduction. The numerical
factor and every subsequent conclusion remain unchanged.
