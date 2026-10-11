# Exact region routing from a quotient and a remainder certificate

**Research question.** Can the resident representation discard numerical information that
does not affect a region choice, yet identify that region exactly for arbitrary source gate
matrices? The construction below answers this question for an integer affine-choice operation.
It does not require polynomial, low-rank, or sparse source weights. Its advantage is instance
dependent and its originality remains under investigation.

This is research under MATHS section 12. It introduces no product numerical kernel or runtime
path. The associated experiment exercises the Q19/Q58 distinction between a source-derived
selector and complete recovery of the selected original weights; it does not pass a release row.

## 1. The ordinary source operation

The source contains an arbitrary integer matrix \(A\in\mathbb Z^{m\times d}\) and arbitrary
fixed-size original payload records \(W_0,\ldots,W_{m-1}\). Given the available integer state
\(x\), the ordinary operation chooses

\[
 i_*(x)=\min\operatorname*{argmax}_{i<m} A_i x
\]

and performs its ordinary calculation with \(W_{i_*}\). An affine operation appends a
constant coordinate to \(x\). Exact integer accumulation is the reference arithmetic;
an arbitrary floating-point router is not covered by exchanging its arithmetic for integers.
The gate's numerical scores have no later use in this operation. If an operation consumes
those scores, their recovery and calculation require a separate account.

The source's prior ordinary operations produce \(x\). No label of the relevant record is
included in \(x\). The construction derives that label from the certified representation.

## 2. Compile the quotient representation

Fix a positive integer step \(\Delta\), conveniently \(2^k\). Choose one phase
\(g_j\in\{0,\ldots,\Delta-1\}\) per coordinate. Define

\[
 q_{ij}=\left\lfloor\frac{a_{ij}-g_j}{\Delta}\right\rfloor,
 \qquad r_{ij}=a_{ij}-g_j-\Delta q_{ij},\quad 0\le r_{ij}<\Delta.
\]

Subtract the column minimum \(c_j=\min_i q_{ij}\), obtaining the nonnegative quotient
\(Q_{ij}=q_{ij}-c_j\). Let

\[
 w_j=\max_i r_{ij}-\min_i r_{ij},\qquad
 h_j=g_j+\Delta c_j+\min_i r_{ij}.
\]

There are exact, source-dependent remainders \(e_{ij}\in[0,w_j]\cap\mathbb Z\) with

\[
 a_{ij}=h_j+\Delta Q_{ij}+e_{ij}.                              \tag{1}
\]

The resident representation stores only \(Q\), \(w\), \(\Delta\), dimensions, bit widths,
and source/layout identity. It does not store \(h\), the phases, or individual remainders.
The common term \(hx\) is identical in every row score and cannot change which row wins.
The source gate and every payload remain external at their original precision.

Compilation reads every source gate entry and verifies (1), the quotient range, and the
remainder widths. A changed source invalidates the certificate; rounding a fitted relation
into an asserted equality is not permitted.

## 3. Interpret the representation and recover the region

Compute \(s_i=Q_i x\), let \(k\) be its least-index maximizer, and put

\[
 B(x)=\sum_{j=1}^d w_j|x_j|.                                  \tag{2}
\]

Retain \(k\) and each other row \(i\) satisfying

\[
 \Delta(s_k-s_i)<B(x),\quad\text{or}\quad
 \Delta(s_k-s_i)=B(x)\ \text{and}\ i<k.                       \tag{3}
\]

Call this set \(S(x)\). If it contains only \(k\), the exact winner is already known.
Otherwise, retrieve each original gate row in \(S(x)\), evaluate its original score exactly,
and choose the least-index maximum. Finally, retrieve \(W_{i_*}\), recover its original
words and shape, and pass those weights to the ordinary calculation.

**Theorem 1 — exact candidate containment.** For every integer source matrix, every chosen
phase vector, and every integer query state, \(i_*(x)\in S(x)\). The interpreter above
returns exactly the source's winner, including its tie rule.

**Proof.** By (1),
\[
 A_kx-A_ix=\Delta(s_k-s_i)+(e_k-e_i)x
 \ge\Delta(s_k-s_i)-B(x).
\]
If the quotient gap exceeds \(B(x)\), row \(i\) cannot win. If it equals \(B(x)\),
the source score of \(k\) is at least that of \(i\); for \(k<i\), the source tie rule
also excludes \(i\). These are precisely the excluded rows. Comparing all remaining source
scores returns the exact winner. \(\square\)

At \(x=0\), \(B(x)=0\), and the rule immediately selects row zero without a source-gate
read. At a difficult boundary, the candidate set may contain all rows. The method remains
exact and pays the full gate-read cost; it does not silently choose an approximate winner.

If payload records have \(L\) bytes and gate rows have \(G\) bytes, fixed strides give
the locations \(\mathrm{payload\_base}+i_*L\) and \(\mathrm{gate\_base}+iG\). A real
container's indexes, validation, headers, and block rounding add their actual reads. The
experiment's raw-record layout is explicitly smaller than Cassette's durable container.

## 4. Choose a phase by a proved one-coordinate optimum

For one coordinate, sort its distinct source residues modulo \(\Delta\) around a circle.
Let \(H\) be the largest cyclic gap between consecutive residues, including the wrap gap.
With one distinct residue, define \(H=\Delta\). Choose \(g\) as the residue immediately
after a largest gap. Then

\[
 \min_g\{\max_i r_i(g)-\min_i r_i(g)\}=\Delta-H.              \tag{4}
\]

**Proof.** Cutting the circle at phase \(g\) unwraps the residues onto an interval of
length \(\Delta\). Their span is \(\Delta\) minus the cyclic gap containing the cut,
with endpoint cuts assigned consistently. No omitted gap exceeds \(H\); cutting after a
largest gap attains \(\Delta-H\). \(\square\)

This minimizes each \(w_j\), hence the bound (2) simultaneously for every \(x\). It does
**not** prove that the candidate set is smallest: changing the phase also changes \(Q\)
and therefore the quotient score gaps. Nor does it minimize RAM automatically, since the
quotient range may gain a bit. The joint objective must account for both effects.

Only cuts at observed residue boundaries need consideration. Between consecutive residues,
all row quotients change by the same integer or remain unchanged; normalization removes a
common change, and the remainder width remains unchanged. Thus at most \(m\) distinct
representations per coordinate, rather than \(\Delta\), enter a finite phase search.

## 5. Encoded memory, work, reads, and deadlines

Let \(b_j=\lceil\log_2(1+\max_i Q_{ij})\rceil\), with \(b_j=0\) for an all-zero column.
The packed coefficient payload uses \(m\sum_j b_j\) bits; widths use \(d\log_2\Delta\)
bits for power-of-two \(\Delta\). The format must also encode \(b_j\), dimensions,
the step, address bases, and source identity. Neither a Python list nor a machine word of
unbounded precision proves this bit cost has been realized.

An interpreter can use two streaming passes over packed \(Q\): one to find \(k,s_k\),
one to apply (3) and fetch eligible gate rows one at a time. It needs no \(m\)-entry score
array or candidate list. Its scratch consists of bounded integer accumulators, row indices,
a gate-row buffer, and the current best original score. The gate buffer is released before
fetching the payload. With state/work buffers counted once, the model-related payload peak is

\[
 \mathrm{guide\ bytes}+\max(G,L),                            \tag{5}
\]

plus decoding scratch, source metadata, the current input, and ordinary output/workspace.
This is a cost model for a packed implementation; the Python research harness has its own
larger memory use and does not measure (5).

Routing requires two passes of \(md\) integer multiply-adds and \(|S|d\) additional
ordinary gate operations if \(|S|>1\). It reads zero gate bytes for a singleton and
\(|S|G\) otherwise, followed by exactly \(L\) payload bytes. Query-state range bounds
determine exact accumulator widths. All candidates use the same original weights downstream.

The guide trades resident memory and arithmetic for external gate reads. A streaming source
scan has a smaller guide but reads \(mG\); a fully resident gate matrix reads no gate bytes.
The selected payload transfer remains. An advantage over either comparator requires a joint
RAM/read/work/deadline comparison, not a claim that reducing one count reduces all counts.

## 6. Required stress and comparison

The executable comparison uses independent dense coefficients, shared remainders, nearly tied
rows, duplicate rows, zero states, changing winners, and signed query states. It compares the
fixed phase with the per-coordinate width optimum, then with finite joint phase optimization
where exhaustive search is feasible. Every output must match the ordinary reference and every
retrieved payload must match its original bytes. The source family is not restricted to the
examples on which the guide saves reads.

Primary-source review must challenge the construction against exact maximum-inner-product
search, scalar grid offset optimization, interval-based pruning, and sign-preserving number
compression. No absence of a search result constitutes a novelty certificate.
