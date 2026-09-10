# A rational finite-advice cover for the two-column orbit

Status: proved as an upper construction in the one-column, fair-coin,
exact-unbiasedness model of
`two_column_unbiased_finite_advice_lower.md`.  The covering and
control-variate ingredients are standard.  This note makes no claim about
sharp exponents, resident-byte optimality, or a Cassette page realization.

Let

\[
 \mathcal V_{p,2}=\{A=[a,b]\in\mathbb R^{p\times2}:A^TA=I_2\},
 \qquad p\ge3.
 \tag{1}
\]

For every \(0<\varepsilon\le1\), there is a finite, rational resident
codebook \(R_j=[a_j^0,b_j^0]\in\mathbb Q^{p\times2}\), \(1\le j\le N\),
such that every \(A\in\mathcal V_{p,2}\) has a selected label \(j(A)\)
with

\[
 \|A-R_{j(A)}\|_{\mathrm{op}}\le\varepsilon,
 \qquad
 N\le\left(1+\frac{4\sqrt2}{\varepsilon}\right)^{2p}.
 \tag{2}
\]

Given this label, sample either original column with probability \(1/2\).
For a query \(x=(x_1,x_2)^T\), form the resident baseline

\[
 c_j(x)=-a_j^0x_1+b_j^0x_2.
 \tag{3}
\]

On reading column \(a\), return \(2ax_1+c_j(x)\); on reading \(b\),
return \(2bx_2-c_j(x)\).  The estimator is exactly unbiased for every
source and query, and has uniform risk

\[
 \sup_{A\in\mathcal V_{p,2}}\sup_{\|x\|_2=1}
 \mathbb E\|\widehat y-Ax\|_2^2\le\varepsilon^2.
 \tag{4}
\]

Thus for a target \(0<C\le1\), taking \(\varepsilon=\sqrt C\) gives

\[
 \lceil\log_2N\rceil
 \le\left\lceil2p\log_2\!\left(1+\frac{4\sqrt2}{\sqrt C}\right)\right\rceil.
 \tag{5}
\]

For \(0<C<1\), the forthcoming conditional-cap lower theorem in
`finite_advice_unbiased_static_conditional_cap_lower.md`, specialized to \(q=2,s=1\),
requires

\[
 \log_2N\ge1+\frac{p-2}{2}\log_2(1/C).
 \tag{6}
\]

Consequently the upper and lower label counts both have leading order
\(p\log(1/C)\) as \(C\downarrow0\).  The elementary upper has at most
the factor \(2p/(p-2)\le6\) larger leading coefficient.  This does not
establish a sharp exponent or a matching constant.

## The estimator

For source \(A=[a,b]\), let \(R_j=[a_0,b_0]\) be its selected resident
pair.  Averaging the two branch outputs gives

\[
 \frac12(2ax_1+c_j)+\frac12(2bx_2-c_j)=Ax,
 \tag{7}
\]

so exact unbiasedness is algebraic and does not depend on the quality of
the approximation.  Each branch error has the same norm, with opposite
sign:

\[
 (2ax_1+c_j)-Ax=(a-a_0)x_1-(b-b_0)x_2,
 \tag{8}
\]

and the second branch error is the negative of (8).  Therefore

\[
 \mathbb E\|\widehat y-Ax\|_2^2
 =\|(A-R_j)\operatorname{diag}(1,-1)x\|_2^2
 \le\|A-R_j\|_{\mathrm{op}}^2\|x\|_2^2,
 \tag{9}
\]

which proves (4) from (2).  The coin uses one unbiased random bit per
query.  Its support size is exactly one original column in every outcome.

## An elementary rational cover

View \(\mathbb R^{p\times2}\) as Euclidean space of dimension \(2p\)
with Frobenius norm.  Every frame in \(\mathcal V_{p,2}\) has Frobenius
norm \(\sqrt2\).  Take a maximal \(\varepsilon/2\)-separated subset
\(\{C_j\}_{j=1}^{N_0}\) of \(\mathcal V_{p,2}\) in that norm.  Maximality
makes it an \(\varepsilon/2\)-net.  The disjoint ambient balls of radius
\(\varepsilon/4\) around the \(C_j\)'s all lie in the ball of radius
\(\sqrt2+\varepsilon/4\).  Comparing Euclidean volumes gives

\[
 N_0\le
 \left(\frac{\sqrt2+\varepsilon/4}{\varepsilon/4}\right)^{2p}
 =\left(1+\frac{4\sqrt2}{\varepsilon}\right)^{2p}.
 \tag{10}
\]

This is a real cover only.  To make the resident entries finite words, put

\[
 M=\left\lceil\frac{\sqrt{2p}}{\varepsilon}\right\rceil
 \tag{11}
\]

and round every entry of each \(C_j\) to its nearest member of
\(M^{-1}\mathbb Z\), calling the result \(R_j\).  Since every entry of a
frame lies in \([-1,1]\), every numerator lies in \(\{-M,\ldots,M\}\).
Moreover,

\[
 \|C_j-R_j\|_F
 \le\frac{\sqrt{2p}}{2M}\le\frac\varepsilon2.
 \tag{12}
\]

For an \(A\) within \(\varepsilon/2\) of \(C_j\), equations (12) and
\(\|\cdot\|_{\mathrm{op}}\le\|\cdot\|_F\) yield (2).  The rounded
matrices need not be orthonormal.  They are legal because they are only
resident baselines in (3), not replacement source columns.

## What finite-word accounting this does and does not provide

The real packing argument alone does not define a finite-word resident
object.  The rounding above does: one common denominator \(M\), plus
\(2p\) signed numerators in \([-M,M]\), specifies each codeword exactly.
With

\[
 w=\left\lceil\log_2(2M+1)\right\rceil,
 \tag{13}
\]

a literal table of all codewords occupies at most

\[
 2pNw+O(\log M+\log N)
 \tag{14}
\]

shared resident bits, under a declared fixed-width rational-word format.
The selected source label costs \(\lceil\log_2N\rceil\) further bits per
source.  The fair sampler adds no label-specific probabilities.

For an exact rational source frame, the encoder can choose the least index
minimizing \(\|A-R_j\|_F\); all comparisons are rational and ties can be
resolved by index.  Exact source-to-label computation is not needed for
the abstract measurable-label theorem, but it is available in this
rational source convention.  If the query is rational as well, the
estimator remains unbiased in exact rational arithmetic in the correct
sense: its random output has mean exactly \(Ax\).  Individual sampled
outputs do not equal \(Ax\).

For arbitrary real source entries, the rational resident table still
defines the formal real-arithmetic estimator and preserves exact mean.
It does not, by itself, provide a finite binary representation for those
source values, the query, or their arithmetic.  Likewise, (14) is a
literal shared-table account, not a procedural-description bound.  Since
\(N\) is exponential in the label-bit bound, this construction matches
the lower result only for the number of source-selected advice bits; it
does not match total resident storage.

## Scope

The construction stays within the theorem's fixed fair sampling law and
one-original-column read cap.  It uses a source-selected label and a
fixed rational resident state indexed by that label.  It does not price
the original source payload, page layout, query arithmetic, activation
workspace, or a physical Cassette interpreter.

## Addendum: arbitrary column count

Let \(p>q\ge2\) and let \(A=[a_1,\ldots,a_q]\in\mathcal V_{p,q}\).
Choose a resident matrix \(B=[b_1,\ldots,b_q]\), then sample an index
\(J\) uniformly from \([q]\) and return

\[
 \widehat y=Bx+q(a_J-b_J)x_J.
 \tag{15}
\]

For every \(A,B,x\), this is exactly unbiased:

\[
 \mathbb E\widehat y
 =Bx+\sum_{j=1}^q(a_j-b_j)x_j=Ax.
 \tag{16}
\]

Writing \(d_j=a_j-b_j\) and \(D=A-B\), direct expansion gives the
exact variance identity

\[
 \mathbb E\|\widehat y-Ax\|_2^2
 =q\sum_{j=1}^q\|d_j\|_2^2x_j^2-\|Dx\|_2^2.
 \tag{17}
\]

In particular, if \(\|d_j\|_2\le\eta\) for every \(j\), then the risk
is at most \(q\eta^2\|x\|_2^2\).

One direct Stiefel cover follows by the same volume comparison used above.
An \(\varepsilon\)-Frobenius net of \(\mathcal V_{p,q}\) can have size

\[
 \left(1+\frac{4\sqrt q}{\varepsilon}\right)^{pq};
 \tag{18}
\]

the elementary baseline estimate \(\|A-B\|_F\le\varepsilon\) then
makes (17) at most \(q\varepsilon^2\).  A factorized construction is
better for this estimator.  Take a rational \(\eta\)-net of the unit
sphere in \(\mathbb R^p\), with

\[
 N_1\le\left(1+\frac4\eta\right)^p,
 \qquad
 \eta=\sqrt{C/q}.
 \tag{19}
\]

Choose \(b_j\) independently from this same net to approximate \(a_j\).
The source label is the resulting \(q\)-tuple of prototype indices, so

\[
 N=N_1^q\le\left(1+4\sqrt{q/C}\right)^{pq},
 \qquad
 \mathbb E\|\widehat y-Ax\|_2^2\le C\|x\|_2^2.
 \tag{20}
\]

For completeness, (19) has the same rational realization as the
two-column cover: take a maximal \(\eta/2\)-separated sphere net, whose
cardinality is at most \((1+4/\eta)^p\), and round each center coordinate
to the nearest multiple of \(1/M\), where

\[
 M=\left\lceil\frac{\sqrt p}{\eta}\right\rceil.
 \tag{21}
\]

The rounding error is at most \(\eta/2\) in Euclidean norm.  The common
prototype table uses
\(pN_1\lceil\log_2(2M+1)\rceil+O(\log M+\log N_1)\) shared
rational-table bits.  It is not necessary to materialize its
\(N_1^q\) possible \(q\)-tuples: the selected label stores \(q\) prototype
indices, and the decoder forms \(Bx\) from those selected prototypes.

For \(0<C<q-1\), the conditional-cap lower theorem at \(s=1\) gives

\[
 \log_2N\ge
 1+\frac{p-q}{2}\log_2\!\left(\frac{q-1}{C}\right).
 \tag{22}
\]

For fixed \(q\), (20) and (22) both have order
\(p\log(1/C)\) as \(C\downarrow0\); the elementary upper has a
factor-of-order \(q\) larger leading coefficient.  This comparison does
not show that either dependence is sharp.  When \(q\) grows,
(20) costs order \(pq\log(q/C)\) label bits, while (22) scales with
\(p-q\).  This construction therefore does not match the lower bound's
dependence on growing \(q\).

The general construction also needs an exact uniform \(q\)-way draw per
query.  When \(q\) is a power of two this uses exactly \(\log_2q\) fair
bits.  For other \(q\), rejection sampling gives a finite expected
fair-bit cost of order \(\log q\) but no finite worst-case bit cap.  This
randomness account is separate from the resident table and source-label
accounts above.
