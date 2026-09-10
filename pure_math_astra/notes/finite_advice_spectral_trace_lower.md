# A spectral read lower bound with finite source advice

Status: proved and independently reconstructed.
The two supporting lemmas have separate proofs. Originality,
sufficient application significance, and finite-word realization remain
unestablished.

## Model

Fix a real positive definite \(G\in\mathbb R^{q\times q}\), with
\(p>q\ge2\), and give
\[
 {\cal O}_G=\{A\in\mathbb R^{p\times q}:A^TA=G\}
\]
its invariant probability measure \(\mu\). A measurable encoder chooses
one of at most \(N\ge1\) fixed decoder states from the source \(A\).

State \(\ell\) has a fixed right orthogonal basis \(Q_\ell\in O(q)\)
and a fixed support law \((w_{\ell,S})_{S\subseteq[q]}\). Its support law
is independent of the source inside that state and independent of the
query. A read returns the columns \((AQ_\ell)_S\). Each branch output is
a Borel function of the state, support, observed columns, and query.
Source-independent internal randomness through a Borel conditional law
of those inputs is allowed.

The selected state must satisfy, for every source and query,
\[
 \mathbb E[\widehat y\mid A,x]=Ax,
 \qquad
 \sup_{A,\ \|x\|=1}
       \mathbb E[\|\widehat y-Ax\|^2\mid A,x]\le C,
 \quad C\ge0.
 \tag{1}
\]
Write
\[
 f_G(C)=\operatorname{tr}\bigl(G(G+CI)^{-1}\bigr),\qquad
 s_\ell=\sum_S w_{\ell,S}|S|.
 \tag{2}
\]

## Quantitative statement

Choose \(0<\epsilon<1\), \(0<\delta<1\), and put
\[
 a=1-\delta^2/2,\qquad
 L=a^2 f_G(C)-2aq\epsilon,
 \tag{3}
\]
\[
 \beta=
 N\,2^{3q/2}(1+2/\delta)^q
       \exp\!\left(-\frac{(p-q)\epsilon^2}{4}\right).
 \tag{4}
\]
Then
\[
 \boxed{\quad
 \mu\{A:s_{\ell(A)}<L\}\le\min\{1,\beta\}.
 \quad}
 \tag{5}
\]
In particular, if every selected state has expected read count at most
\(s\), and
\[
 p-q>\frac4{\epsilon^2}
 \left(\log N+\frac{3q}{2}\log2+
                     q\log(1+2/\delta)\right),
 \tag{6}
\]
then
\[
 \boxed{\quad
 s\ge a^2 f_G(C)-2aq\epsilon.
 \quad}
 \tag{7}
\]
All logarithms in (4)--(6) are natural. The statement covers overlapping
supports, empty supports, and states with arbitrarily small positive
support probabilities. It assumes no continuity of the decoder or encoder
and no lower bound on those probabilities.

## Conditional projection control

Discard supports with zero probability in each state. Replace each
remaining randomized branch by its conditional mean over the
source-independent internal law. On inputs used by the selected state,
finite risk guarantees integrability. Extend this mean by zero elsewhere
when it is not integrable. The extension is Borel, preserves (1), and
reduces risk. It therefore suffices to treat deterministic branch maps.

For state \(\ell\), set \(A_\ell=AQ_\ell\),
\(G_\ell=Q_\ell^TGQ_\ell\), \(V=\operatorname{span}(A)\), and
\(V_{\ell,S}=\operatorname{span}((A_\ell)_S)\).
Conditional on the observed columns, the subspace
\[
 E_{\ell,S}=V\cap V_{\ell,S}^\perp
\]
is a uniform \((q-|S|)\)-plane inside the \((p-|S|)\)-dimensional
space \(V_{\ell,S}^\perp\). This follows by conditioning a uniform
Stiefel isometry on its restriction to the known coefficient subspace.

For any Borel branch map and fixed query, normalize its component
perpendicular to \(V_{\ell,S}\), when nonzero. Conditional on the
observation, this is one fixed direction \(v\). For a uniform
\(d\)-plane in \(\mathbb R^n\), the squared projection \(X\) of \(v\)
has beta moments
\[
 \mathbb EX^k=\frac{(d/2)_k}{(n/2)_k}.
\]
Thus, for \(0<\lambda<1\),
\[
 \mathbb E e^{\lambda nX/2}
 \le\sum_{k\ge0}\frac{\lambda^k(d/2)_k}{k!}
 =(1-\lambda)^{-d/2}.
\]
Markov at \(\lambda=1/2\) gives
\[
 \Pr\{X>\epsilon^2\}
 \le2^{d/2}e^{-n\epsilon^2/4}.
 \tag{8}
\]
When \(d=0\), the projection event is empty. No bound on the norm or
variation of the branch function is used.

Choose one Euclidean \(\delta\)-net \({\cal Z}\) of the unit sphere
in \(\mathbb R^q\), with
\[
 |{\cal Z}|\le(1+2/\delta)^q.
\]
For each state and \(z\in{\cal Z}\), use the physical query
\[
 x_{\ell,z}=Q_\ell
 \frac{(G_\ell+CI)^{-1/2}z}
      {\|(G_\ell+CI)^{-1/2}z\|}.
 \tag{9}
\]
These queries are fixed before the source is selected. Different states
may have different query sets, each of the same bounded cardinality.

Apply (8) to all positive-probability state/support/query triples. There are at most
\(N2^q|{\cal Z}|\) triples, \(d\le q\), and \(n\ge p-q\).
The union bound gives an event \(\Omega\) of measure at least
\(1-\min\{1,\beta\}\) on which
\[
 \|P_{E_{\ell,S}}F_{\ell,S}\|
 \le\epsilon\|F_{\ell,S}\|
 \tag{10}
\]
for every triple. The stronger bound relative to the perpendicular
component also holds. Independence between these events is unnecessary.

This event was formed over every fixed state before applying the source
encoder. Hence it includes the branch maps and test queries of the state
actually chosen at every \(A\in\Omega\). Conditioning on the encoder's
state cell before applying (8) would not justify this step.

## The deterministic trace step

Fix \(A\in\Omega\) and its selected state. Work in that state's
coordinates, abbreviating \(A_\ell,G_\ell\) by \(A,G\). For the moment
these symbols describe the rotated source; its spectrum is unchanged.

Put
\[
 H=\sum_S w_S P_{V_S}\big|_V,\qquad
 K_C=A(G+CI)^{-1}A^T\big|_V.
 \tag{11}
\]
For a test query \(x\), exactness gives
\[
 B:=\sum_Sw_S\|F_S\|^2
 =R(A,x)+\|Ax\|^2\le C+x^TGx.
 \tag{12}
\]
For any \(u\in V\), split its inner product with each output along
\(V_S\) and \(V\cap V_S^\perp\). Cauchy--Schwarz over the support law
and (10) give
\[
 |\langle u,Ax\rangle|
 \le\bigl(\sqrt{u^THu}+\epsilon\|u\|\bigr)\sqrt B.
 \tag{13}
\]
No support probability is inverted.

At the unrotated test coordinate
\(x_z=(G+CI)^{-1/2}z/\|(G+CI)^{-1/2}z\|\), one has the exact cancellation
\[
 \frac{Ax_z}{\sqrt{C+x_z^TGx_z}}
       =A(G+CI)^{-1/2}z.
 \tag{14}
\]
For a fixed \(u\), choose a net point within \(\delta\) of the unit
direction of \((G+CI)^{-1/2}A^Tu\). Its inner product with that direction
is at least \(a=1-\delta^2/2\). Equations (12)--(14), used only at that
finite test query, therefore yield
\[
 a\sqrt{u^TK_Cu}
 \le\sqrt{u^THu}+\epsilon\|u\|.
 \tag{15}
\]
There is no extension of the decoder's output between nearby queries.
The net approximates a linear functional of \(z\), not the decoder.

Since \(0\preceq K_C\preceq I_V\), (15) implies
\[
 H\succeq a^2K_C-2a\epsilon I_V.
 \tag{16}
\]
For example, when \(a\sqrt{u^TK_Cu}>\epsilon\|u\|\), square the positive
difference and bound \(\sqrt{u^TK_Cu}\le\|u\|\). In the other case the
right side of the corresponding quadratic inequality is nonpositive,
so \(H\succeq0\) suffices.

The selected columns are independent because \(G>0\). Hence
\(\operatorname{tr}P_{V_S}=|S|\), and (16) gives
\[
 s_{\ell(A)}=\operatorname{tr}H
 \ge a^2\operatorname{tr}K_C-2aq\epsilon
 =a^2 f_G(C)-2aq\epsilon=L.
 \tag{17}
\]
Trace and \(f_G(C)\) are invariant under the label-specific right basis.
Every \(A\in\Omega\) satisfies (17), proving (5). If (6) holds, then
\(\beta<1\), so \(\Omega\) is nonempty and (7) follows.

## Advice required for a spectral read deficit

Suppose the architecture has a uniform expected read cap \(s\), and
\[
 \Delta=f_G(C)-s>0,\qquad \gamma=\Delta/q\in(0,1].
\]
Choose \(\epsilon=\gamma/8\), \(\delta=\sqrt\gamma/2\).
Since \(a^2\ge1-\delta^2\) and \(f_G(C)\le q\), (3) gives
\(L\ge s+\Delta/2>s\). Thus (5) forces \(\beta\ge1\). Rearranging
(4) yields the necessary advice bound
\[
 \log N\ge
 \frac{(p-q)\gamma^2}{256}
 -\frac{3q}{2}\log2
 -q\log(1+4/\sqrt\gamma).
 \tag{18}
\]
When \(N\le2^b\),
\[
 b\ge\frac{(p-q)\gamma^2}{256\log2}
       -\frac{3q}{2}
       -q\log_2(1+4/\sqrt\gamma).
 \tag{19}
\]
Negative right sides are allowed and give no useful restriction. For a
fixed positive normalized spectral deficit, the bound grows linearly
with the unfixed output dimension once it dominates the displayed
\(q\)-dependent subtraction.

## Explicit equicorrelation consequence

Let \(q=4m\), \(G=H_\eta^{\oplus m}\),
\(H_\eta=\mathbf1\mathbf1^T+\eta I_4\), \(0<\eta\le1/100\), and
\(C=(19/10)\eta\). Direct evaluation gives
\[
 f_G(C)
 =m\left(\frac{4+\eta}{4+(29/10)\eta}+\frac{30}{29}\right)
 \ge m\,\frac{237160}{116841}.
 \tag{20}
\]
Set \(\epsilon=1/1000\), \(\delta=1/100\), so \(a=19999/20000\).
Then
\[
 L\ge m\,\frac{2362016033293}{1168410000000}
 >\frac{101}{50}m,
 \tag{21}
\]
with exact positive excess
\(1827833293m/1168410000000\). Therefore, if
\[
 p-4m>
 4{,}000{,}000\left(
 \log N+6m\log2+4m\log201\right),
 \tag{22}
\]
no such finite-advice static architecture can achieve uniform risk
\(1.9\eta\) while keeping every selected state's expected reads at most
\(2.02m\).

For sufficiently small \(\eta\) within the displayed range, the existing
query-selected construction has hard cap \(2m\) and risk at most
\(1.9\eta\) on this same orbit. Independent reconstruction checks
the combined corollary. Equation (22) therefore extends that separation to
source-trained nonlinear static decoders with finitely many states and
label-specific fixed bases. The dimension constant in (22) is large;
the proof establishes a linear dependence on \(m+\log N\), not an
optimized or practically measured threshold.

## Boundaries and source of the argument

The result concerns a full continuous Gram orbit, exactly unbiased
outputs, finite source state, and static support laws. It permits arbitrary
Borel nonlinear decoders and finite catalogs of fixed real basis matrices.
It does not apply to uncharged continuously varying source state, support
probabilities that adapt to the query or observed values, or general
encodings that let a fetched column reveal other source data.

A continuous-orbit lower bound does not automatically give a finite-word
hard family for arbitrary nonlinear decoders. The theorem also leaves
physical pages, shared interpreter/table bytes, and arithmetic precision
unaccounted. These limitations must be addressed in any claimed Cassette
consequence.

The proof uses conditional Haar-subspace concentration, a finite union
bound, and a deterministic dual trace estimate. Whether their combination
is a substantive original advance requires its own primary-source and
significance assessment. It is not established by this proof note.

## Proof dependencies

- [Independent reconstruction of the complete theorem and corollary](/Users/drewwiberg/cassette/pure_math_astra/notes/finite_advice_spectral_trace_lower_independent_review.md).
- [Conditional projection concentration](/Users/drewwiberg/cassette/pure_math_astra/notes/nonisotropic_finite_advice_projection_concentration.md).
- [Deterministic stable trace estimate](/Users/drewwiberg/cassette/pure_math_astra/notes/stable_leakage_projection_trace_lower.md).
- [Earlier exact no-advice orbit theorem](/Users/drewwiberg/cassette/pure_math_astra/notes/fixed_gram_orbit_static_oracle_minimax_independent_proof.md).
- [Existing query-selected orbit construction](/Users/drewwiberg/cassette/pure_math_astra/notes/fixed_gram_oracle_adaptivity_separation.md).
