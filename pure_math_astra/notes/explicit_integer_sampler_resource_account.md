# Integer representation and costs of the explicit two-rule sampler

Status: an explicit mathematical algorithm and conditional storage account.
The reference implementation has an exact finite audit. Native Cassette
execution and a material production improvement remain unproved.

## Input, output, and control

The [reference program](../programs/equicorrelation_two_rule_sampler.py)
accepts four signed integer numerators \(a_i\) for a common-scale query
\(x_i=a_i/2^b\). It returns four integers \(B_i\), at most two nonzero,
representing \(Y_i=B_i/2^{b+1}\). The scale is unchanged by selection and
sampling except for this one extra fractional bit.

Put \(T=\sum_i a_i\) and \(Q=\sum_i a_i^2\). Zero input returns zero.
If \(3T^2\ge4Q\), a uniform pair \(i<j\) gives

\[
 B_i=T+3(a_i-a_j),\qquad B_j=2T-B_i.
\]

Otherwise, put \(P=\sum_i(a_i)_+\) and \(N=\sum_i(-a_i)_+\). A positive
coordinate receives an integer ticket with probability \(a_i/P\), and a
negative coordinate receives one with probability \(-a_j/N\). Their output
numerators are \(2P\) and \(-2N\). A zero mass requires no ticket.
There is no division in the output coefficient calculation.

The [general proof](explicit_sum_preserving_two_sparse_sampler.md) supplies
the exact mean, sum preservation, hard support cap, and \(5/3\) risk bound.
The [independent reconstruction](sum_preserving_two_sparse_real_sampler_review.md)
also gives a sharper bound for selecting the smaller exact risk; the
reference program deliberately implements the simpler threshold just stated.

## Integer widths and randomness

Let \(A=\max_i|a_i|\). Both rules obey \(|B_i|\le8A\). For the uniform
rule, \(B_i=4a_i-2a_j+a_k+a_l\); the absolute coefficient sum is eight.
For the flow rule, each total mass is at most \(4A\).
The selector's largest square comparison is bounded by \(48A^2\).
Thus widths depend on the query's integer width, not on the height of the
source matrix or a stored catalog.

An exact uniform integer below \(M\ge1\) uses
\(k=\lceil\log_2 M\rceil\) fair bits per attempt and accepts an integer
below \(M\). For \(M=1\), no bits are needed. For \(M>1\),

\[
 \mathbb E[\text{bits}]=k\,\frac{2^k}{M}<2k,\qquad
 \Pr\{\text{more than }r\text{ attempts}\}
 =\left(1-\frac{M}{2^k}\right)^r<2^{-r}.
\]

Uniform pair selection uses \(M=6\), hence four expected bits. Flow
selection uses the independent totals \(P,N\), omitting zero totals.
If the input numerators use signed \(d\)-bit words, each nonzero mass is
less than \(2^{d+1}\). The expected random-bit count is at most
\(4(d+1)\) per block, including the cases where a mass is one.

This is an expected-cost and tail account. It does not supply a finite
worst-case cap on fair-bit consumption. For example, a uniformly selected
one-of-six outcome cannot be generated from a fixed finite fair-bit tree
without a rejection or failure branch. The theorem permits this declared
randomness model; a bounded-latency execution certificate would need to
account for the tail.

Selection takes four squares and a constant number of integer additions
and comparisons. Each weighted selection scans at most four coordinates.
It performs no search over a catalog. These are arithmetic-operation counts;
the integer widths above must accompany them in a bit-cost comparison.

For a source whose integer entries have magnitude at most \(M_s\),
accumulating \(2m\) selected products at the common doubled scale has
absolute numerator at most \(16mAM_s\). The resulting output can be
represented exactly with

\[
 1+\left\lceil\log_2(16mAM_s+1)\right\rceil
\]

signed accumulator bits per row. This is a packed integer representation,
not the memory footprint of Python integer objects.

## Declared column-record example

Use the finite sources in
[the explicit separation corollary](explicit_sampler_finite_word_separation.md).
Declare one independently addressed record per original column, a 64-byte
record header, packed fixed-width payload, and zero padding to a multiple
of 4096 bytes. A complete-column read fetches the entire record. It may
span many physical blocks; the argument does not identify it with one
4096-byte page.

For height \(p\) and scalar width \(w\), the record size is

\[
 P_{\rm col}=4096\left\lceil
 \frac{\lceil pw/8\rceil+64}{4096}\right\rceil.
\]

For one block, the exact accounts are:

| Source states allowed to the static decoder | \(p\) | \(w\) | Bytes per column record | Four source records | Adaptive two-record cap | Guaranteed saving over the static lower |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| \(1\) | 4,755,005 | 29 | 17,240,064 | 68,960,256 | 34,480,128 | More than \(25,860,096/25\) bytes/query |
| \(2^{256}\) | 49,171,005 | 30 | 184,393,728 | 737,574,912 | 368,787,456 | More than \(276,590,592/25\) bytes/query |

The saving uses only the proved \(0.06\)-column margin. It applies at the
static architecture's hard source, when selected records are freshly
fetched. The common source payload cancels. With signed 16-bit query
numerators, the exact accumulator widths in these two examples are at most
48 and 49 bits respectively.

The reference source file, including its audit code, occupies 7,431 bytes
at this checkpoint. That is a literal file size, not resident interpreter
memory. The sampler has no source-trained coefficients or finite-catalog
payload. Python code objects, the shared interpreter, input and output
objects, temporary allocation, and any physical source reader still need
their implementation-specific memory account.

## Evidence and next boundary

[The saved exact audit](equicorrelation-two-rule-exact-audit.json) checks all
2,401 integer vectors in \([-3,3]^4\). It enumerates the complete finite
output laws, verifies each mean and exact risk formula, and enumerates the
actual integer tickets passed through the reference sampling function.
Every selected outcome preserves the sum and uses at most two coordinates.
The finite grid's largest selected risk ratio is \(5/3\); its largest
expected fair-bit count is \(88/9\).

These checks verify the finite cases and ticket implementation. The
independently reconstructed algebra proves the general statement.
The remaining application questions concern the source family's relevance,
the static comparison's restrictions, physical execution, and arithmetic
error. The explicit construction resolves the catalog-size uncertainty;
it does not settle those other questions.
