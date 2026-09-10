# Binary32 error account for the explicit two-rule sampler

Status: conditional finite-arithmetic bound.  This note assumes the exact
binary32 model stated below.  It does not establish any property of MLX,
Apple hardware, compiler contraction, or a native Cassette execution path.

## Arithmetic and source model

Let

\[
 \eta=\frac1{256},\qquad G=H_\eta^{\oplus m},\qquad
 H_\eta=\mathbf1\mathbf1^T+\eta I_4,\qquad A^TA=G.
 \tag{1}
\]

Set \(q=4m\), let \(W=\operatorname{fl}_{32}(A)\) entrywise, and assume
IEEE binary32 round-to-nearest, ties-to-even.  The account uses the stated
normal-plus-subnormal model

\[
 |\operatorname{fl}_{32}(z)-z|\le u|z|+a,
 \qquad u=2^{-24},\qquad a=2^{-150}.
 \tag{2}
\]

Every arithmetic operation below is assumed correctly rounded under (2),
with no overflow, invalid operation, or exceptional-value substitution.
The standard accumulation notation is

\[
 \gamma_k=\frac{ku}{1-ku}\qquad(ku<1).
 \tag{3}
\]

IEEE 754 specifies the binary formats and correctly rounded basic
operations; the usual \(\gamma_k\) dot-product bound is the standard
finite-precision estimate.  The relevant references are [IEEE Std
754-2019](https://standards.ieee.org/ieee/315/6210/) and N. Higham,
[*Accuracy and Stability of Numerical Algorithms*, Chapter
3](https://epubs.siam.org/doi/10.1137/1.9780898718027.ch3).  Equation (2)
is an explicit stronger modeling assumption at the subnormal boundary; it
is not being inferred from an MLX implementation.

## Storage perturbation

Writing \(E=W-A\), (2) gives entrywise

\[
 |E|\le u|A|+a\mathbf1.
\]

Consequently

\[
 \begin{aligned}
 \|W-A\|_{\rm op}
 &\le\|E\|_F\\
 &\le u\|A\|_F+a\sqrt{pq}\\
 &=u\sqrt{\operatorname{tr}G}+2^{-150}\sqrt{pq}
 =:r_s.
 \end{aligned}
 \tag{4}
\]

Here

\[
 \operatorname{tr}G=4m(1+\eta)=\frac{257m}{64}.
 \tag{5}
\]

Thus (4) is a storage-conversion bound only.  It neither assumes nor proves
that a page reader or matrix kernel returns the same arithmetic result.

## Exact binary32 sampler coefficients

Let every four-coordinate query block be supplied as

\[
 x_i=\frac{z_i}{2048},
 \qquad z_i\in[-2048,2048]\cap\mathbb Z.
 \tag{6}
\]

This is the nonunit dyadic query alphabet used by the finite net argument.
Every nonzero query satisfies \(\|x\|_2\ge2^{-11}\).  The rule selector
compares the integers

\[
 3\Bigl(\sum_i z_i\Bigr)^2
 \quad\hbox{and}\quad
 4\sum_i z_i^2,
 \tag{7}
\]

so its decision has no floating-point error.

For the uniform-pair rule, its two nonzero values have the form

\[
 \frac{T+3(z_i-z_j)}{4096},\qquad
 \frac{T-3(z_i-z_j)}{4096},\qquad T=\sum_i z_i.
 \tag{8}
\]

Their numerators have magnitude less than \(2^{15}\), hence at most
fifteen significant binary digits.  The transport rule returns

\[
 \frac{P}{2048}\quad\hbox{or}\quad-\frac{N}{2048},
 \qquad P=\sum_{z_i>0}z_i,\qquad N=\sum_{z_i<0}(-z_i),
 \tag{9}
\]

whose numerators have magnitude at most \(2^{13}\).  Both forms are dyadic
and require at most fifteen significant bits.  They are therefore exactly
representable as finite normal binary32 values.  Exact integer sampling of
the rational branch probabilities is unchanged from the sampler note.  In
particular, rounding is absent from the selector, probability comparison,
and output-coefficient construction.

## Norms of the sampled vector

For one selected uniform pair, write \(U_{ij}x=Y^{ij}\).  Since

\[
 \|U_{ij}x\|_2^2
 =\frac12(\mathbf1^Tx)^2+\frac92(x_i-x_j)^2,
\]

and the two defining row directions are orthogonal, the nonzero eigenvalues
of \(U_{ij}^TU_{ij}\) are \(2\) and \(9\).  Therefore

\[
 \|U_{ij}\|_{\rm op}=3.
 \tag{10}
\]

For the transport rule,

\[
 \|Y^F\|_2^2=P^2+N^2\le(P+N)^2
 =\|x\|_1^2\le4\|x\|_2^2.
 \tag{11}
\]

Applying either rule independently in every block yields, outcome by
outcome,

\[
 \|Y\|_2\le3\|x\|_2.
 \tag{12}
\]

## Accumulated matrix--vector error

Let \(\widehat y=\operatorname{fl}_{32}(WY)\), with each output coordinate
formed by accumulating at most \(k=2m\) products.  Standard dot-product
analysis under the normal part of (2), together with a direct propagation
of its additive part, gives componentwise

\[
 |\widehat y-WY|
 \le\gamma_{2m}|W||Y|+\alpha_{2m}\mathbf1,
 \qquad
 \alpha_{2m}=\frac{4m\,2^{-150}}{1-2mu}.
 \tag{13}
\]

The additive term is deliberately conservative: a length-\(2m\) dot product
has fewer than \(4m\) rounded elementary operations, and repeated relative
amplification is bounded by \(1/(1-2mu)\).  For a nonzero alphabet query,
(12), (4), and \(\|\,|W|\,\|_{\rm op}\le\|W\|_F\) imply

\[
 \begin{aligned}
 \|\widehat y-WY\|_2
 &\le\gamma_{2m}\bigl\|\,|W|\,|Y|\bigr\|_2
      +\sqrt p\,\alpha_{2m}\\
 &\le\left[
      3\gamma_{2m}\left(\sqrt{\operatorname{tr}G}+r_s\right)
      +2048\sqrt p\,\alpha_{2m}\right]\|x\|_2
 =:b_a\|x\|_2.
 \end{aligned}
 \tag{14}
\]

The first line is the requested matrix form.  The second makes the bound
relative over the declared finite alphabet without replacing the entrywise
absolute-value matrix by \(W\) itself.

For the zero query, the sampler returns zero and the implementation must
return zero without a matrix--vector accumulation.  Thus (14) also holds
at zero.  If \(a(Y)=\widehat y-WY\), then (14) gives both

\[
 \|\mathbb E\widehat y-Wx\|_2=\|\mathbb Ea(Y)\|_2\le b_a\|x\|_2
 \tag{15}
\]

and \(\bigl(\mathbb E\|a(Y)\|_2^2\bigr)^{1/2}\le b_a\|x\|_2\).  This is a
bias allowance caused by specified arithmetic; it is not exact
unbiasedness after the matrix--vector accumulation.

## Risk bound

The exact sampler has \(\mathbf1^T(Y-x)=0\) in every block.  Hence

\[
 \|A(Y-x)\|_2=\sqrt\eta\,\|Y-x\|_2.
 \tag{16}
\]

Combining (4), the sampler variance bound, (14), and Minkowski's inequality
gives for every alphabet query

\[
 \left(\mathbb E\|\widehat y-Wx\|_2^2\right)^{1/2}
 \le\left[\sqrt{\frac53}\,(\sqrt\eta+r_s)+b_a\right]\|x\|_2.
 \tag{17}
\]

Thus the squared risk is at most the square of the right side of (17).

## Explicit one-block margin and its necessary dimension condition

For \(m=1\), equations (4), (5), and (14) become

\[
 \begin{aligned}
 s&=\sqrt{\operatorname{tr}G}=\frac{\sqrt{257}}8,\\
 \gamma_2&=\frac{2^{-23}}{1-2^{-23}},\\
 r_s&\le 2^{-27}\sqrt{257}+2^{-149}\sqrt p,\\
 b_a&\le3\gamma_2(s+r_s)
       +\frac{2^{-137}}{1-2^{-23}}\sqrt p.
 \end{aligned}
 \tag{18}
\]

The non-subnormal parts evaluate as

\[
 2^{-27}\sqrt{257}<1.195\mathbin{\cdot}10^{-7},
 \qquad
 3\gamma_2\left(\frac{\sqrt{257}}8+2^{-27}\sqrt{257}\right)
 <7.167\mathbin{\cdot}10^{-7}.
 \tag{19}
\]

There can be no \(p\)-uniform conclusion from the additive subnormal model:
the terms in (18) grow as \(\sqrt p\).  A sufficient explicit condition is

\[
 p\le2^{244}.
 \tag{20}
\]

Indeed, \(\sqrt p\le2^{122}\), so the subnormal contribution to \(r_s\)
is \(2^{-27}\), while the subnormal contribution to \(b_a\) is at most
\(2^{-15}/(1-2^{-23})\).  Together with
\(\sqrt{257}<16.032\) and
\(\gamma_2<1.193\mathbin{\cdot}10^{-7}\), equation (18) gives

\[
 r_s<1.270\mathbin{\cdot}10^{-7},
 \qquad
 b_a<3.1235\mathbin{\cdot}10^{-5}.
 \tag{21}
\]

Consequently

\[
 r_s+b_a<3.1362\mathbin{\cdot}10^{-5}
 <\frac{\sqrt\eta}{1000}=6.25\mathbin{\cdot}10^{-5}.
 \tag{22}
\]

Since \(\sqrt{5/3}>1\), the stated margin therefore proves, under (20),

\[
 \begin{aligned}
 \left(\sqrt{\frac53}(\sqrt\eta+r_s)+b_a\right)^2
 &\le \frac53\eta\left(1+\frac1{1000}\right)^2\\
 &<\frac{27}{16}\eta
 =:C.
 \end{aligned}
 \tag{23}
\]

Equations (17) and (23) give
\(\mathbb E\|\widehat y-Wx\|_2^2\le C\|x\|_2^2\) on the declared
alphabet, while (15) gives bias at most \(b_a\|x\|_2\).

For reference, direct substitution of the conservative \(p=2^{244}\)
bound into (17) gives a squared-risk bound below
\(0.006519\), while \(C=27/4096=0.006591796875\).  The displayed decimal
is only a readability check; (23) is the proof.

The conclusion is limited to the declared binary32 operations, the exact
integer sampler, the no-exception scale condition, and the explicit
dimension condition (20).  It does not prove that an actual MLX path uses
those operations, preserves their order, or meets this error bound.
