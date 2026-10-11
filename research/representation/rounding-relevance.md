# Rounding-cell relevance for sequential finite-precision products

**Status.** This note derives a sufficient exact block-omission rule for one
ordinary calculation: a fixed-order binary round-to-nearest matrix-vector
product whose multiply and add are separate operations. It uses a resident
exponent atlas derived from source weights, then returns unchanged source
weights for every block that the atlas cannot omit. The rule is narrower than
real-number nullspace reasoning. It proves numerical accumulator parity only
under its declared IEEE-style semantics and says nothing about uncharged flags,
contractions, or exceptional values.

## 1. Declared source operation

Let \(W=(w_{rj})\) be a finite binary floating-point matrix with \(p\) output
rows and \(n\) input coordinates. The drive stores fixed-stride column blocks
\(B\subseteq\{1,\ldots,n\}\), together with the source-encoded weights in
each block. A row accumulator reaches the beginning of a contiguous block
\(B\) in a known finite, nonzero, normal value \(a_r\) with finite adjacent
floats. The declared ordinary operation processes the block in increasing
column order:

\[
 a_r^{(j)}=\operatorname{RN}\left(a_r^{(j-1)}
              +\operatorname{RN}(w_{rj}x_j)\right),
 \qquad j\in B,
 \tag{1}
\]

where \(\operatorname{RN}\) is binary round-to-nearest, ties-to-even, in a
named format, and \(a_r^{(j-1)}\) is the result from the preceding column.
The source and runtime state are restricted to finite values and an execution
in which exception flags are not part of the observable result. The fixed loop
order, rounding mode, absence of contraction, and handling of signed zero are
part of the operation identity. Changing any of them changes the theorem.

If every update in a block rounds back to the accumulator with which the
block began, the pager can omit that block without reading its weights. The
resulting accumulator bits are the same as a normal execution of (1); no
approximation to \(Wx\) is substituted for source weights.

## 2. A source-derived exponent atlas

For a finite nonzero floating value \(y\), define its strict binary upper
exponent by

\[
 u(y)=\min\{e\in\mathbb Z:|y|<2^e\}.
 \tag{2}
\]

Set \(u(0)=-\infty\). At construction, the encoder reads each source weight
and records

\[
 e_{rj}=u(w_{rj}).
 \tag{3}
\]

The resident exponent atlas contains these values, a zero code, the named
floating format and execution mode, the fixed block layout, and the source
identity. It does not contain coefficient mantissas or replace a source block.
Its construction scans the complete source table once and rejects a source
containing a value outside the declared finite-value domain.

At runtime, the interpreter derives \(h_j=u(x_j)\) from each available input
coordinate. For a row and block it computes the max-plus envelope

\[
 K_{rB}(x)=\max_{j\in B}\bigl(e_{rj}+h_j+1\bigr),
 \tag{4}
\]

with terms involving a zero operand omitted. This is an integer calculation.
It needs no read of the source weights in \(B\).

For a finite nonzero normal accumulator \(a\) with finite neighbors, let
\(a^-<a<a^+\) be its adjacent floats and define the conservative rounding-cell
radius

\[
 \tau(a)=\frac12\min(a-a^-,a^+-a).
 \tag{5}
\]

The interpreter omits \(B\) precisely when, for every output row,

\[
 2^{K_{rB}(x)}<\tau(a_r).
 \tag{6}
\]

It evaluates (6) with exact integer exponents and the format's known dyadic
spacing, never through a rounded real logarithm. A zero, subnormal, maximum
finite, infinite, or NaN accumulator is a conservative failure of this test:
the interpreter reads the block and executes (1).

The physical address of a surviving block is derived from its declared fixed
stride. A failed test produces the logical region

\[
 S(x,a)=\{B:\text{(6) fails for at least one row}\},
 \tag{7}
\]

and maps each \(B\in S\) to its source byte range by the layout formula. The
pager reads, validates, and returns those original weight bytes to the normal
loop. An omitted block has no reconstitution obligation because its declared
ordinary loop leaves every accumulator unchanged.

## 3. Exactness proof

**Lemma 1 — rounded-product bound.** If \(w\) and \(x\) are finite nonzero
operands and, for some finite normal \(a\) with finite neighbors,
\(2^{u(w)+u(x)+1}<\tau(a)\), then

\[
 \left|\operatorname{RN}(wx)\right|<2^{u(w)+u(x)+1}.
 \tag{8}
\]

**Proof.** Definition (2) gives \(|wx|<2^{u(w)+u(x)}\). Round-to-nearest can
raise the magnitude to the next power-of-two boundary, but not beyond twice
that strict bound. Under (6) the bound is far below a finite normal
accumulator's rounding radius, so the product cannot overflow. Thus (8)
holds, including the case in which the product underflows to a signed zero.
\(\square\)

**Lemma 2 — strict rounding cell.** For a finite nonzero normal \(a\) with
finite neighbors, any finite \(q\) satisfying \(|q|<\tau(a)\) obeys

\[
 \operatorname{RN}(a+q)=a.
 \tag{9}
\]

**Proof.** The open interval
\((a-(a-a^-)/2,\,a+(a^+-a)/2)\) rounds to \(a\). The smaller half-gap in
(5) lies strictly inside that interval on both sides. Strict inequality
excludes a midpoint tie, so parity of endpoint significands is irrelevant.
\(\square\)

**Theorem 1 — exact split multiply-add block omission.** If (6) holds for a
contiguous block \(B\), omitting \(B\) leaves every accumulator bit produced
by (1) unchanged.

**Proof.** Take any row \(r\). Lemma 1 and (4) give

\[
 \left|\operatorname{RN}(w_{rj}x_j)\right|
 <2^{K_{rB}(x)}<\tau(a_r)
\]

for every \(j\in B\). Lemma 2 shows that the first update returns \(a_r\).
The same statement applies to the next update because its input accumulator
is still \(a_r\), and induction covers the contiguous block. The argument is
independent across rows. The omitted block and the normal loop therefore end
with identical accumulator bits. \(\square\)

The theorem establishes relevance from actual finite-precision behavior. It
does not argue that a small real-valued block product is negligible, and it
does not use a real-algebra cancellation that a floating loop might fail to
reproduce.

## 4. Why the atlas is sharper than a scalar block norm

A scalar exponent summary stores

\[
 E_{rB}=\max_{j\in B}e_{rj},
 \qquad H_B(x)=\max_{j\in B}h_j,
\]

and can use only the weaker bound

\[
 K^{\rm scalar}_{rB}=E_{rB}+H_B(x)+1.
 \tag{10}
\]

Equation (4) is never larger than (10), and can be much smaller when the
largest coefficient and largest input magnitude occupy different coordinates.
For binary64, take one row with \(a=1\), a two-column block, and

\[
 (w_1,w_2)=(2^{20},2^{-60}),
 \qquad (x_1,x_2)=(2^{-80},1).
\]

At \(a=1\), (5) gives \(\tau(a)=2^{-54}\). The atlas has \(K_B=-57\), so
(6) certifies omission. The scalar summary has \(K^{\rm scalar}_B=23\), so
it must read the block. Both actual products are \(2^{-60}\), and both
separate rounded additions return the binary64 value one. The improvement
comes from preserving coefficient/input alignment, not from estimating a sum.

The price is real. For one row with \(d\) columns, restrict the source family
to dense nonzero weights \(w_j=2^{e_j}\), where
\(e_j\in\{0,\ldots,L-1\}\). Define the full max-plus envelope

\[
 f_e(h)=\max_j(e_j+h_j+1).
 \tag{11}
\]

For coordinate \(k\), choose a permitted exponent query with \(h_k=0\) and
\(h_j=-L\) for \(j\ne k\). Then \(f_e(h)=e_k+1\). Hence the values of
\(f_e\) on this query family determine every exponent \(e_k\). Any resident
representation that computes the exact envelope (11) for all such runtime
states must distinguish \(L^d\) exponent patterns and needs at least
\(d\log_2L\) bits in the worst case. This lower bound is only for the named
max-plus-envelope class, but it shows why arbitrary dense coefficients do not
admit a generally compact aligned bound.

## 5. Resource account and interpreter

Suppose an atlas exponent uses \(b_e\) encoded bits, including its zero code.
For a \(p\times n\) source matrix its resident payload is \(pnb_e\) bits, plus
format, layout, source identity, and block-boundary metadata. A block scan
performs \(p|B|\) integer additions/comparisons to obtain (4), and keeps one
current maximum per output row. This work can be substantial even when the
block is omitted; it is not an I/O-free speed claim.

For a block that passes (6), peak additional memory is the per-row maxima, the
already-required accumulator vector, and the atlas. For a block that fails,
peak memory also includes its fetched source bytes, integrity workspace,
decoded source weights, and the ordinary calculation's live state. If blocks
are streamed, the fetched-weight component is one block; if the ordinary
kernel pins multiple blocks, all pinned bytes are charged. The representation
therefore trades resident exponent metadata and integer scan work for avoided
source reads only on blocks whose actual rounded updates are inert.

The construction handles later inputs and later accumulator states because it
recomputes (4)--(6) from available state. It never treats a previous selected
region as a free answer. For fixed-size physical blocks,

\[
 \operatorname{offset}(B)=\operatorname{base}+
                           \operatorname{index}(B)\operatorname{stride},
\]

so location costs no resident directory. Unequal blocks require a charged
address structure or its own read transcript.

## 6. Boundaries that defeat the certificate

* **Dense active input.** With \(x_j=1\), nontrivial weight exponents, and
  ordinary accumulators near one, (6) fails for every dense block. The
  interpreter reads the full table. This is the expected adversarial case.

* **Midpoint ties.** Replacing \(<\) in (6) with \(\le\) is wrong for a tie
  whose even endpoint is the neighboring float. The strict cell is less
  permissive, but it avoids a source-dependent parity table.

* **Signed zero and subnormals.** The current rule never omits a block at a
  zero or subnormal accumulator. A special rule would need exact IEEE
  sign-of-zero and gradual-underflow behavior for every skipped update.

* **FMA and contraction.** For a declared fused update
  \(a\leftarrow\operatorname{RN}(a+wx)\), the proof works with
  \(K^{\rm FMA}_{rB}=\max_j(e_{rj}+h_j)\), because there is no rounded product.
  A compiler that contracts a reference split operation, or splits a reference
  FMA, changes the required certificate and invalidates Theorem 1.

* **Observable flags and traps.** An inexact, underflow, overflow, or
  signaling-NaN flag can be visible even when the numerical accumulator does
  not move. If flags or traps are part of the normal operation's output, a
  skipped block requires a second certificate for their exact behavior.

* **Exceptional source values.** The source scan rejects NaNs and infinities.
  It cannot use exponent metadata to establish their ordinary arithmetic
  behavior without a format-specific exceptional-value analysis.

## 7. Primary-source comparison

The mechanism collides with established numerical-analysis methods. Moore's
[*Interval Analysis*](https://books.google.com/books/about/Interval_Analysis.html?id=csQ-AAAAIAAJ)
introduced the interval-arithmetic line in which bounded values certify
conclusions without evaluating every exact path. Goubault and
Putot's [static analysis of numerical algorithms](https://doi.org/10.1007/11823230_3)
uses an abstract domain to bound finite-precision behavior, and Shewchuk's
[adaptive precision arithmetic](https://people.eecs.berkeley.edu/~jrs/papers/robustr.pdf)
uses inexpensive bounds before a more expensive exact route. The
[IEEE 754-2019 standard](https://standards.ieee.org/ieee/754/6210/) is a direct
authority for treating formats, rounding, operation sequence, and exceptions
as part of the semantics.

Those works make the central ingredients familiar: a sound magnitude bound, a
rounding-aware guard, and a fallback when the guard cannot decide. This note
adds the external-memory interpretation contract and the max-plus alignment
lower bound, but a bounded primary-source search did not establish that either
is new. The retained value is a falsifiable baseline: the certificate is exact
only for the stated finite operation, its atlas has a charged \(pnb_e\)-bit
cost, and generic dense sources force the full atlas or source reads. No
originality claim follows.
