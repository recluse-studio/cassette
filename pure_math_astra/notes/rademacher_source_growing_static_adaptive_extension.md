# Independent dyadic Rademacher sources for the growing static/adaptive gap

Status: the finite-dimensional construction below is proved, conditional on
the finite block catalog used in
`finite_word_growing_static_adaptive_separation.md`. It remains a
column-linear, abstract support-count comparison. It does not price source
storage, a decoder, random bits, or physical reads.

This note replaces the shared-row-sign Hadamard isometry by an independent
Rademacher matrix. The replacement removes that one-column shared-sign
structure and reduces the required output dimension from a quadratic to a
linear function of the block count, at fixed error constants.

Let \(t=5m\), \(q=4m\), and let \(R_0\in\mathbb Q^{t\times q}\) be the
block-diagonal factor with

\[
 R_0^TR_0=G=H_\eta^{\oplus m},
 \qquad H_\eta=\mathbf1\mathbf1^T+\eta I_4,
\tag{1}
\]

where \(r^2=\eta\) and \(r\) is dyadic. Let \(\mathcal B\) be the range
of a fixed source-independent \(b\)-bit interpreter. For every
\(B\in\mathcal B\), let \(S_B\) be the real span of the real and imaginary
parts of its columns; then \(\dim S_B\le2q\).

Fix the dyadic constants

\[
 \delta={1\over16},\qquad \zeta={1\over256},\qquad
 a=1-\zeta-\delta^2={127\over128}.
\tag{2}
\]

Choose \(p=4^k\ge t\), and let \(U\in\mathbb Q^{p\times t}\) have
independent entries \(\pm p^{-1/2}\). The next two sections give explicit
probability bounds for the two properties needed of one common realization
of \(U\).

## Avoiding every decoded column span

For fixed unit vectors \(v\in\mathbb R^t\) and \(w\in\mathbb R^p\),
Rademacher Hoeffding gives

\[
 \Pr\{|w^TUv|\ge h\}\le2e^{-ph^2/2}.
\tag{3}
\]

Indeed, the displayed scalar is a sum of independent signs with squared
coefficient sum \(p^{-1}\). Take quarter-nets in the unit spheres of
\(\mathbb R^t\) and \(S_B\), of sizes at most \(9^t\) and
\(9^{\dim S_B}\). For any matrix \(M\), the two-sided quarter-net estimate
is

\[
 \|M\|_{\rm op}
 \le2\max_{v,w\ \mathrm{in\ the\ two\ nets}}|w^TMv|.
\tag{4}
\]

At \(h=\delta/2\), a union bound therefore gives

\[
 \Pr\left\{\max_{B\in\mathcal B}\|P_{S_B}U\|_{\rm op}>\delta\right\}
 \le2\exp\left[b\log2+(t+2q)\log9-{p\delta^2\over8}\right].
\tag{5}
\]

## Near-isometry without a quadratic dimension cost

Write the unscaled rows of \(\sqrt pU\) as independent sign vectors
\(\epsilon_i\in\{-1,1\}^t\). Then

\[
 U^TU-I_t={1\over p}\sum_{i=1}^pX_i,
 \qquad X_i=\epsilon_i\epsilon_i^T-I_t.
\tag{6}
\]

For a self-contained scalar route, fix a unit \(v\) and put
\(X=\epsilon\cdot v\), \(Y=X^2-1\). The Rademacher subgaussian tail
\(\Pr\{|X|\ge u\}\le2e^{-u^2/2}\) implies, for every integer \(j\ge2\),

\[
 \mathbb E|Y|^j
 \le2^{j-1}\bigl(\mathbb E|X|^{2j}+1\bigr)
 \le2^{2j+1}j!
 \le{j!\over2}\,64\,8^{j-2}.
\tag{7}
\]

The first moment estimate follows by integrating the subgaussian tail. The
last display is Bernstein's moment condition with variance proxy \(64\)
and scale \(8\). Scalar Bernstein consequently gives, for \(0<h\le1\),

\[
 \Pr\left\{\left|\|Uv\|_2^2-1\right|\ge h\right\}
 \le2e^{-ph^2/144}.
\tag{8}
\]

Apply (8) at \(h=\zeta/2\) to a quarter-net of \(\mathbb S^{t-1}\). The
standard symmetric quadratic-form net estimate gives

\[
 \Pr\{\|U^TU-I_t\|_{\rm op}>\zeta\}
 \le2\exp\left[t\log9-{p\zeta^2\over576}\right].
\tag{9}
\]

This is the step that avoids the weaker entrywise Hoeffding estimate, whose
range bound would introduce an unnecessary \(t^2\) scale.

If

\[
 2e^{\,b\log2+(t+2q)\log9-p\delta^2/8}
 +2e^{\,t\log9-p\zeta^2/576}<1,
\tag{10}
\]

there is one dyadic realization obeying both

\[
 \|P_{S_B}U\|_{\rm op}\le\delta\quad(B\in\mathcal B),
 \qquad
 (1-\zeta)I_t\preceq U^TU\preceq(1+\zeta)I_t.
\tag{11}
\]

Rounding the least sufficient \(p\) to a power of four changes it by at
most a factor of four. Since \(t=5m\) and \(q=4m\), (10) admits

\[
 p=O(m+b),
\tag{12}
\]

with the displayed fixed \(\delta,\zeta\) constants. For a fixed \(\eta\)
and a shared finite block catalog, the common-budget choice
\(b=O_\eta(\log m)\) therefore gives \(p=O_\eta(m)\).

## Gram comparison and the adaptive upper bound

Set \(A=UR_0\). Equation (11) gives

\[
 (1-\zeta)G\preceq A^*A\preceq(1+\zeta)G.
\tag{13}
\]

The fixed finite two-column catalog from the cited growing separation has
block-Gram risk at most \((19/10)\eta\). Its blockwise product construction
has exact mean and at most \(2m\) selected original columns. The upper
comparison in (13) therefore gives

\[
 \sup_{\|x\|=1}\mathbb E\|A(Y-x)\|_2^2
 \le c\eta,
 \qquad c={19\over10}(1+\zeta)={4883\over2560}.
\tag{14}
\]

Block orthogonality is used to bound the catalog risk in the reference Gram
\(G\); the final comparison in (13), rather than block orthogonality of
\(A^*A\), transfers that bound to the Rademacher source.

## Residual separation and the static support lower bound

For every decoded \(B\) and every complex \(x\), (11) gives

\[
 |\langle UR_0x,Bx\rangle|
 \le\delta\|R_0x\|_2\|Bx\|_2.
\tag{15}
\]

Completing the square and using the lower comparison in (13) yields

\[
 \begin{aligned}
 \|(A-B)x\|_2^2
 &\ge\|UR_0x\|_2^2+\|Bx\|_2^2
      -2\delta\|R_0x\|_2\|Bx\|_2\\
 &\ge(1-\zeta-\delta^2)\|R_0x\|_2^2.
 \end{aligned}
\tag{16}
\]

Hence

\[
 (A-B)^*(A-B)\succeq aG.
\tag{17}
\]

Grant the static comparator an arbitrary fixed support law, global support
allocation, a free unitary column encoding, free sampling metadata, and
retained coefficients linear in the complete query. If it matches the
adaptive error \(c\eta\), the trace-water argument gives

\[
 {s\over m}\ge
 {a(4+\eta)\over a(4+\eta)+c\eta}+{3a\over a+c}.
\tag{18}
\]

For \(\eta\le1/100\),

\[
 \begin{aligned}
 {a(4+\eta)\over a(4+\eta)+c\eta}
 &\ge1-{c\eta\over4a}
 \ge1-{4883\over1016000},\\
 {3a\over a+c}&={7620\over7423}=1+{197\over7423}.
 \end{aligned}
\tag{19}
\]

The excess over two in (18) is at least

\[
 {197\over7423}-{4883\over1016000}
 ={163905491\over7541768000}
 ={1\over50}+{13070131\over7541768000}
 >{1\over50}.
\tag{20}
\]

Thus every such static comparator needs more than
\((2+1/50)m\) selected columns, while the adaptive construction uses at
most \(2m\).

## Scope

The construction produces a dyadic source with independent sign patterns
across its factor coordinates. It remains a worst-case source selected after
the complete finite interpreter range is fixed. It allows source-trained
encoders and charged decoder parameters, because their complete state is
one of the \(2^b\) interpreter words. It does not cover a free
source-dependent decoder, nonlinear resident reconstruction, query-selected
reconstruction, or output maps outside the span of the selected source
columns. The support cap remains abstract; no source-byte, page, alignment,
cache, memory, random-bit, or latency claim follows.
