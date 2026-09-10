# Finite-word separation between static and query-selected column sampling

Status: the component proofs and their combination have an independent
correctness review. This note consolidates the result in one declared model.
Substantive originality and a material Cassette improvement remain open.

## Common source and access model

Choose a sufficiently small positive dyadic \(\eta\le1/100\) for which
\(\Psi_{2,\mathbb C}(H_\eta)\le1.89\eta\) holds. Put

\[
 H_\eta=\mathbf1\mathbf1^T+\eta I_4,\qquad
 G=H_\eta^{\oplus m},\qquad q=4m,\qquad C=19\eta/10.
\]

Fix a positive integer \(N\) and an integer \(p\) satisfying

\[
 p-4m>4{,}000{,}000
 \bigl(\log N+6m\log2+4m\log201\bigr).
 \tag{1}
\]

Logarithms in (1) are natural. Choose a dyadic step
\(h\le\sqrt\eta/(10000\sqrt{pq})\). The finite stored-source family is

\[
 \mathcal W_h=
 \{\operatorname{round}_h(A):A\in\mathbb R^{p\times q},\ A^TA=G\},
 \tag{2}
\]

with one fixed nearest-grid tie rule. A read reveals one complete original
column of \(W\). The target is \(Wx\). Both protocol classes must have
exact mean and expected squared Euclidean error at most \(C\) for every
unit query and every source in (2).

A static protocol may inspect the source in advance and select one of at
most \(N\) states. Each state specifies a support distribution independent
of the query and, within that state, independent of the source. Its decoder
may be an arbitrary Borel function of the read columns and query, with
source-independent internal randomness. All additional source-dependent
information belongs in the state. Shared decoder tables are unrestricted.
The lower does not assume a linear decoder.

The adaptive protocol uses a shared finite rational catalog and chooses a
catalog law from the query. Both classes read the same original columns.
A free dense transformed-column oracle is outside this declared model.

## Separation theorem

There is a query-selected law with exact mean \(Wx\), error below \(C\),
and at most \(2m\) original-column reads on every source in (2).

Every static protocol satisfying the same requirements has some source in
(2) whose selected state has expected read count at least

\[
 \frac{11807741126602841}{5842634219605125}\,m>2.02m.
 \tag{3}
\]

The hard source may depend on the static architecture. This is a uniform
guarantee over a declared source family, not a conclusion that a particular
production weight matrix is hard.

## Lower proof

Use the [rounded trace theorem](rounded_original_column_finite_advice_trace_lower.md)
with \(\epsilon=1/1000\), \(\delta=1/100\), and
\(a=19999/20000\). Condition (1) makes its simultaneous concentration
failure bound less than one. On a source in its good event, put

\[
 r_0=h\sqrt{pq}/2,\qquad
 \zeta=\frac{r_0}{\sqrt{C+\lambda_{\min}(G)}}\le\zeta_0=\frac1{20000}.
\]

In equation (14) of that proof, replace \(\zeta\) by \(\zeta_0\)
before dividing or squaring. Every right-hand coefficient increases.
The trace argument therefore applies directly with fixed constants

\[
 \alpha_0=\frac{a}{1+\zeta_0}=\frac{19999}{20001},\qquad
 \epsilon_0=\epsilon+\frac{\zeta_0}{1+\zeta_0}
 =\frac1{1000}+\frac1{20001}.
\]

This avoids substituting separate estimates into positive and negative
terms of a trace expression without checking their combined monotonicity.
The result is

\[
 s_{\ell(W)}\ge\alpha_0^2 f_G(C)-2\alpha_0q\epsilon_0,\qquad
 f_G(C)=\operatorname{tr}\bigl(G(G+CI)^{-1}\bigr).
\]

The block spectrum gives

\[
 \frac{f_G(C)}m
 =\frac{4+\eta}{4+(29/10)\eta}+\frac{30}{29}
 \ge\frac{237160}{116841}.
\]

The first term decreases with \(\eta\); the lower value is its value at
\(1/100\). Exact substitution yields

\[
 \alpha_0^2\frac{237160}{116841}-8\alpha_0\epsilon_0
 =\frac{11807741126602841}{5842634219605125}
 =\frac{101}{50}
  +\frac{11240006000977}{11685268439210250}.
\]

This proves (3). The good-event probability concerns continuous preimages
of rounded words, rather than uniform counting on (2).

The lower already follows from one finite rational unit-query alphabet:
[the rational-query net proof](finite_rational_query_trace_net.md) chooses
net centers from the transformed rational sphere, with the same covering
cardinality and trace constants. The alphabet is fixed from \(G,C,\delta\)
before the decoder is chosen. Its word width is finite but unquantified.
Thus this restriction matches the upper's exact rational-query model
without assuming that an arbitrary decoder is continuous in its query.

## Upper proof

The [rounded adaptive construction](original_column_rounded_equicorrelation_adaptive_upper.md)
uses one finite rational four-coordinate catalog, shared across all blocks.
Every chosen law has coefficient mean equal to its query block, at most
two nonzero output coordinates, and ideal risk at most
\((379/200)\eta\|x\|^2\). Since \(G\succeq\eta I\),

\[
 \|Wz\|\le(1+1/20000)\|Az\|.
\]

Consequently, the rounded risk is at most

\[
 \frac{379}{200}\left(\frac{20001}{20000}\right)^2\eta
 =\frac{151615160379}{80000000000}\eta<\frac{19}{10}\eta.
\]

Concatenation preserves coefficient mean \(x\) and the hard \(2m\)-column
cap. Multiplication by \(W\) gives exact mean \(Wx\).
For real sources and queries, take the real part of every complex catalog
outcome matrix. The mean persists, row support cannot grow, and squared
error cannot increase. The upper and lower therefore share the real model.

## Finite words and remaining costs

For \(h=2^{-L}\), let

\[
 N_h=\left\lceil\frac{\sqrt{4+\eta}}h+\frac12\right\rceil,\qquad
 w_h=\left\lceil\log_2(2N_h+1)\right\rceil.
\]

Each entry uses an integer in \([-N_h,N_h]\) and the shared dyadic scale.
A column has \(pw_h\) payload bits. Under equal-size original column pages,
the upper reads at most \(2mpw_h\) payload bits, while some source forces
the static class above \(2.02mpw_h\) expected payload bits.

That comparison does not price the catalog, selection, randomness,
arithmetic, headers, alignment, cache state, or source advice. The catalog
proof supplies no small constructed catalog or native runtime. Exact
rational queries, sampling, and arithmetic preserve the upper's mean
identity; native arithmetic needs its own error account. The sufficient
dimension condition (1) is large. A material production improvement is
therefore unestablished.

The [combined independent review](rounded_original_column_equicorrelation_combined_independent_review.md)
reconstructs both proofs and verifies the constants. Its real-field
clarification is included above. Its substitution concern is addressed by
weakening the earlier inequality before taking the trace.

[The resource assessment](finite_word_separation_resource_assessment.md)
states the conditional byte comparison and the unconstructed catalog costs.
