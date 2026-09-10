# Independent review: finite-word growing static/adaptive separation

Reviewed note:
`finite_word_growing_static_adaptive_separation.md`.

Verdict: **mathematically supported inside the declared column-linear
classes, conditional on the cited 1.89 boundary theorem and finite-catalog
bridge.** The result is a growing abstract source family with a linear
support-count gap. It is not a common-byte description frontier or a
physical access theorem.

## Verified adaptive upper bound and its quantifiers

The cited boundary result gives, for one fixed sufficiently small dyadic
\(\eta>0\),

\[
 \Psi_{2,\mathbb C}(H_\eta)\le1.89\eta.
\tag{1}
\]

The finite-catalog bridge, applied with additive tolerance \(\eta/100\),
therefore gives one fixed finite rational catalog of operator-unbiased,
two-row-sparse laws with risk at most \(1.9\eta\) for every unit block
query. This is a valid use of the bridge: each selected catalog law has
\(\mathbb EL=I\), although selection among laws depends on the observed
block query.

Concatenating one selected law for each of the \(m\) blocks has exact mean
and at most \(2m\) nonzero coordinates on every realization. Block
diagonality gives

\[
 \mathbb E\|A(Y-x)\|^2
 \le1.9\eta\sum_{j=1}^m\|x_j\|^2.
\tag{2}
\]

No product catalog of size \(K^m\) is required: the same fixed block
catalog is reused and the blockwise selector is run \(m\) times. This is
an abstract arithmetic construction. The cited catalog theorem supplies
neither a small numerical catalog nor a physical random-bit or latency
implementation.

## Verified finite-codebook lower construction

For \(\delta=1/10\), the dyadic Hadamard condition from the audited
codebook bridge is

\[
 2\exp\left[b\log2+(t+2q)\log9-{p\delta^2\over8t}\right]<1.
\tag{3}
\]

Here \(t=5m\), \(q=4m\), so \(t+2q=13m\) and (3) is exactly the
assembled note's

\[
 2\exp\left[b\log2+13m\log9-{p\over800t}\right]<1.
\tag{4}
\]

The resulting isometry avoids the real span of the real and imaginary
columns of every matrix decoded from the complete \(b\)-bit state range.
For \(A=UR_0\), completing the square gives the stronger bound

\[
 (A-B)^*(A-B)\succeq(1-\delta^2)A^*A
 ={99\over100}H_\eta^{\oplus m}.
\tag{5}
\]

This covers an encoder that trains on or inspects \(A\) and then chooses a
state: all possible resulting states must still be decoded by the one fixed
interpreter from at most \(2^b\) words. It does not cover free
source-dependent decoder state, side information, or continuous parameters
that are not represented in that state.

## Verified static lower bound

Let \(a=99/100\), \(c=19/10\), and let the residual Gram be \(R^*R\).
If a static comparator has worst-query variance at most \(c\eta\), the
trace certificate and (5) imply

\[
 \begin{aligned}
 s
 &\ge\operatorname{tr}\!\left(R^*R(R^*R+c\eta I)^{-1}\right)\\
 &\ge\operatorname{tr}\!\left(aG(aG+c\eta I)^{-1}\right)\\
 &=m\left[
 {a(4+\eta)\over a(4+\eta)+c\eta}
 +{3a\over a+c}\right].
 \end{aligned}
\tag{6}
\]

The first inequality follows because the water level of \(R^*R\) cannot
exceed \(c\eta\); the second uses Loewner monotonicity of
\(X\mapsto X(X+c\eta I)^{-1}\). This is the right argument for a global
support law. It has not silently imposed a two-read-per-block condition.

For \(\eta\le1/100\),

\[
 {a(4+\eta)\over a(4+\eta)+c\eta}
 \ge1-{c\eta\over4a}
 \ge1-{19\over3960},
 \qquad
 {3a\over a+c}={297\over289}=1+{8\over289}.
\tag{7}
\]

Since

\[
 {8\over289}-{19\over3960}>{1\over50},
\tag{8}
\]

(6) proves \(s>(2+1/50)m\). Orthogonal or unitary column encoding does
not change the water level. The lower class also already grants arbitrary
support allocation, free transform information, free sampling metadata, and
full-query linear retained coefficients. Those grants make the lower bound
stronger for the stated comparator; they do not cover nonlinear decoding or
nonlinear post-processing outside the selected-column span.

## Finite-state growth statement

For fixed \(\eta\), the rational block catalog and its selector have some
finite, but not numerically supplied, representation size \(C_\eta\). A
regular partition and dimensions require \(O(\log p+\log m)\) additional
bits in a declared abstract word model. Set

\[
 b_m=C_\eta+O(\log p_m+\log m).
\tag{9}
\]

Choosing the least dyadic \(p_m=4^k\) satisfying (4) gives

\[
 p_m=O_\eta\bigl(m(b_m+m)\bigr).
\tag{10}
\]

The self-consistent choice \(b_m=O_\eta(\log m)\) then gives
\(p_m=O_\eta(m^2)\) and \(\log p_m=O_\eta(\log m)\). This confirms the
assembled note's asymptotic accounting claim, but only in that declared
finite-word model. It does not provide a numerical value of \(C_\eta\), a
finite-word random sampler, or MATHS's peak/total description and metadata
fields.

## Scope findings

The assembled theorem correctly stops short of a physical or global
resource conclusion. In particular, it does not prove any of the following:

* a lower bound for arbitrary nonlinear resident reconstructions or
  source-dependent decoders with free state;
* a common resident-byte frontier, because the lower parameter \(b\) counts
  codeword choice while interpreter tables and the adaptive catalog need a
  separately declared charged representation;
* a source-byte, page, alignment, cache, memory, or latency separation;
* a lower bound after a nonunitary query representation change or a decoder
  that computes values outside the selected-column span.

The two stray plus signs identified in Sections 1 and 6 of the assembled
note were repaired. Root also corrected missing math-command escapes in
this review. These repairs do not change the proof.
