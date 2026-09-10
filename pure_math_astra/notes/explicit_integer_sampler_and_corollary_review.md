# Independent review: integer two-rule sampler and finite-word corollary

Status: the implementation and the displayed corollary arithmetic check out
within the declared rational-query, rounded-original-column model. This is a
correctness review only. It does not assess originality or Cassette
significance.

## Actual integer map

Let a block query be \(x_i=a_i/2^b\), with integers \(a_i\), and let
\(T=\sum_i a_i\). The program returns an integer vector \(B\), interpreted
as \(Y=B/2^{b+1}\).

For the uniform-pair branch, pair_output returns, on \(\{i,j\}\),

\[
 B_i=T+3(a_i-a_j),\qquad B_j=2T-B_i.
\]

Thus \(B_i/2^{b+1}=t/2+3(x_i-x_j)/2\), exactly the uniform-pair outcome.
Its sum is \(2T\), and averaging the six pair tickets gives
\(\mathbb EB=2a\).

For the sign-flow branch, sample_block separately assigns one positive
ticket and one negative ticket. If their integer masses are

\[
 P=\sum_i(a_i)_+,\qquad N=\sum_i(-a_i)_+,
\]

the output is \(2Pe_I-2Ne_J\), with the obvious singleton rule when one
mass is zero. Dividing by \(2^{b+1}\) gives the stated mass-transport law.
Positive and negative selected indices are disjoint. This covers total-zero
nonzero inputs, zero coordinates, and one-sign inputs. The all-zero input
takes the separate zero branch. Consequently every actual output, not only
the enumerated distribution, has support at most two, coordinate sum
\(2T\), and pointwise mean \(2a\).

The rule test

\[
 3T^2\mathrel{\ge}4\sum_i a_i^2
\]

is the exact integer form of \(t^2\ge4\|x\|_2^2/3\). The equality convention
selects the uniform-pair law, which remains within the proved \(5/3\)
bound.

## Coefficient growth and randomness

Put \(A=\max_i|a_i|\). In the pair branch,

\[
 B_i=4a_i-2a_j+a_k+a_l
\]

for the two remaining coordinates \(k,l\); the same form holds after
interchanging \(i,j\). Hence \(|B_i|\le8A\). In the flow branch,
\(|B_i|\) is either \(2P\) or \(2N\), also at most \(8A\). The program's
finite audit asserts this bound on its grid, but this identity is the
general proof.

The helper uniform_integer(bound, getbits) uses
\(w=\operatorname{bit\_length}(\texttt{bound}-1)\) fresh fair bits on each
attempt. Its acceptance probability is
\(\texttt{bound}/2^w\), which is at least \(1/2\), except that it is one
for an exact power of two; bound \(1\) takes no bits. Thus

\[
 \mathbb E[\text{bits}]
 =\frac{w2^w}{\texttt{bound}}\le2w,
 \qquad
 \Pr\{\text{attempts}>k\}\le2^{-k}.
\]

For the uniform-pair branch the exact expectation is
\(3\cdot8/6=4\) bits and the failure probability after \(k\) three-bit
blocks is \(4^{-k}\). For each nonempty sign mass, the same formulas apply
with bound \(P\) or \(N\). If input numerators use the usual signed
two's-complement \(b\)-bit convention, then \(P,N\le2^{b+1}\), so each
selection has width at most \(b+1\), expected cost at most \(2(b+1)\), and
the two selections together have expected cost at most \(4(b+1)\). A
simple combined tail is

\[
 \Pr\{\text{total sign-flow bits}>2k(b+1)\}\le2^{1-k}.
\]

The prose should define “signed \(b\)-bit” explicitly. Under a different
meaning of \(b\), its output-width statement requires a corresponding
shift. Under the two's-complement convention, \(|B|\le2^{b+2}\), and a
signed \(b+3\)-bit output numerator is sufficient. Equality is possible at
the negative two's-complement endpoint in the flow branch.

The executed audit() is a useful finite check of 2,401 small inputs, and
its ticket-map checks exercise sample_block itself. It is not the general
proof; the identities above supply that proof.

## Corollary arithmetic

For \(\eta=1/256\), \(C=27\eta/16\), and
\(G=H_\eta^{\oplus m}\), the adaptive error bound is

\[
 \frac53(\sqrt\eta+r_0)^2
 \le\frac{1002001}{600000}\eta
 <\frac{27}{16}\eta,
\]

with exact gap \(10499\eta/600000\). This uses the sum-preserving property
block by block. It is valid for the real sampler.

The trace calculation is also correct:

\[
 f_{H_\eta}(C)
 =\frac{16400}{16427}+\frac{48}{43}
 =\frac{1493696}{706361}.
\]

With \(\epsilon=1/250\), \(\delta=1/20\),
\(\alpha_0=3995/4004\), and \(\epsilon_0=1251/250250\), the conservative
per-block bound equals

\[
 \alpha_0^2f_{H_\eta}(C)-8\alpha_0\epsilon_0
 =\frac{2811004608947}{1361104669925}
 =\frac{103}{50}
 +\frac{14257977803}{2722209339850}>2.06.
\]

As in the earlier rounded lower, substituting the conservative
\(\alpha_0\) in both terms uses that
\(\alpha\mapsto\alpha^2f-8\alpha\epsilon_0\) is increasing over the
relevant interval. Here this is immediate from
\(\alpha f>4\epsilon_0\). The corollary should state that monotonicity
line if it is intended to stand alone.

The dimension condition follows exactly from the general union bound:
\(4/\epsilon^2=250000\), \(q=4m\), and
\(1+2/\delta=41\). Both illustrative choices of \(p,L,w_h\), the squared
grid checks, and the packed payload products are arithmetically correct.

## Scope correction

The selected sampler is pointwise unbiased for each query:

\[
 \mathbb E[Y\mid x]=x.
\]

It is not one fixed operator-unbiased law \(\mathbb E L=I\), because the
sign-flow probabilities and the branch selector depend on \(x\). The
corollary is therefore a query-adaptive upper versus a static finite-advice
lower. Calling the selected nonlinear mapping “operator-unbiased” would be
incorrect; “pointwise coefficient-unbiased query-adaptive law” is exact.

The payload count concerns rounded source entries and original-column
fetches. It does not price a physical page layout, the query numerator and
denominator format, integer workspace, rejection-tail latency, source
state, or a native Cassette path.
