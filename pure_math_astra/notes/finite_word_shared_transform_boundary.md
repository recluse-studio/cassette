# Finite-word boundary for a shared transform library and shared HT sampler

Status: conditional realization analysis for
\(\texttt{dependence_support_transform_rate.md}\), completed 5 September
2026.  It proves no physical-byte or native-runtime result.

## 1. Exact-arithmetic conditional model

Fix \(\varepsilon>0\), a finite transform library, and one exact-size law
\(\mu\) on subsets of \([q]\).  Suppose that all of the following are exact
objects in a declared arithmetic field:

- \(R\), or equivalently every stored encoded column \(R\widetilde V e_i\);
- a transform \(\widetilde V\) satisfying
  \(\widetilde V^*\widetilde V=I\);
- the atom probabilities of \(\mu\), its marginals
  \(\theta_i=\Pr_\mu(i\in S)>0\), and HT weights \(1/\theta_i\);
- the query \(x\).

For a sample \(S\sim\mu\), return
\[
 Y(x)=\sum_{i\in S}
 \frac{R\widetilde V e_i\,(\widetilde V^*x)_i}{\theta_i}.
\tag{1}
\]
Then
\[
 \mathbb EY(x)=R\widetilde V
 \operatorname{Diag}\!\left(\mathbb E\frac{\mathbf1\{i\in S\}}{\theta_i}\right)
 \widetilde V^*x=Rx.
\tag{2}
\]
Thus one shared law requires no per-atom sampling-law metadata.  It preserves
exact unbiasedness for every library index, provided the transform and
encoded columns are exact.  It always reads exactly \(s\) encoded columns.

This is an algebraic statement.  It does not establish finite machine-word
execution.

## 2. Rational transforms and rational sampling laws

Rational orthogonal matrices are dense in \(O(q)\).  On a bounded Cayley
chart, approximate a real skew-symmetric \(A\) by a rational skew-symmetric
\(\widehat A\), then set
\[
 \widetilde V=(I-\widehat A)(I+\widehat A)^{-1}.
\tag{3}
\]
This is exactly orthogonal over \(\mathbb Q\). Signed diagonal matrices
give explicit bounded charts. For any orthogonal \(V\), the average of
\(\det(I+SV)\) over diagonal signs \(S\) is one: expand the determinant
as a multilinear polynomial in the signs and average. Thus some sign choice
has \(|\det(I+SV)|\ge1\). Since \(\|I+SV\|\le2\), its smallest
singular value is at least \(2^{-(q-1)}\). The skew-symmetric Cayley
parameter \(A=(I-SV)(I+SV)^{-1}\) is therefore uniformly bounded in fixed
dimension. Approximate that parameter rationally and multiply (3) by
\(S\). This gives an \(O(\varepsilon)\)-close rational orthogonal
replacement for every library transform.

The same construction works over \(\mathbb Q(i)\): take a rational
skew-Hermitian \(\widehat A\) and use (3).  It yields an exactly unitary
matrix over \(\mathbb Q(i)\). The same signed-determinant average and
singular-value bound give bounded charts for \(U(q)\).
Therefore a finite ideal library with slack \(t+\varepsilon/4\) can be
replaced by a rational orthogonal/unitary library within \(O(\varepsilon)\).
The Gram and covariance maps are locally Lipschitz, so, after reducing the
ideal target by a fixed factor, the rational library still achieves
\(t+\varepsilon\).  The codebook exponent \(\kappa\) is unchanged.

The common law from the transform-rate theorem need not have rational
probabilities: its marginals \(p_i=a_i/(a_i+t)\) can be irrational.  This
does not obstruct unbiasedness.  Approximate its finitely many atom
probabilities by nonnegative rationals summing exactly to one.  Let the
resulting rational law be \(\widehat\mu\), with marginals
\(\widehat\theta_i\), and use the exact rational weights
\(1/\widehat\theta_i\).  Then (2) holds exactly with
\(\widehat\mu\), regardless of whether \(\widehat\theta=p\).

If
\[
 \|\widehat\mu-\mu\|_{\rm TV}\leq c\varepsilon,
\tag{4}
\]
all first- and second-order inclusion probabilities, and hence the
fixed-law covariance at the reference diagonal, change by \(O(\varepsilon)\).
Since the \(p_i\) are interior, \(\widehat\theta_i\) remain positive for
small \(\varepsilon\).  The rational law therefore preserves the
\(t+\varepsilon\) variance target after allocating constant-factor slack.
It does **not** preserve the ideal baseline \(t\) exactly.

A law attaining a correlation-support size \(k\) can be chosen with finite
atom support.  Fix its \(N-k\) zero cross-correlation equations together
with normalization and the marginal equations, then take an extreme point
of that affine section of the subset-law polytope. It has at most
\[
 L\le q+N-k
\tag{5}
\]
subset atoms, because this is an upper bound on the rank of the equality
constraints.  Rational approximation of these \(L\) masses to total
variation \(O(\varepsilon)\) gives a common finite sampler.

With a bounded Cayley chart and fixed \(q\), rational approximants of
accuracy \(O(\varepsilon)\) can be stored with
\(O_q(\log(1/\varepsilon))\) bits per transform.  A common rational law
with \(L\) atoms can be stored by integer numerators over one common
denominator using
\[
 O\!\left(L\log\frac{L}{\varepsilon}\right)
\tag{6}
\]
bits, up to a field-independent coding constant.  Exact sampling from this
law is possible from unbiased random bits by rejection sampling an integer
in the common denominator range.  A finite-state pseudorandom generator
does not itself establish the exact probability law.

For fixed \(\varepsilon\), a transparent conditional accounting is
\[
 B_{\rm shared}(\varepsilon)
 =
 B_{\rm decoder}
 +O_q\!\left(K(\varepsilon)\log\frac1\varepsilon\right)
 +O\!\left(L\log\frac{L}{\varepsilon}\right)
 +B_{\rm sampler}.
\tag{7}
\]
An atom then stores a transform index of
\(\lceil\log_2K(\varepsilon)\rceil\) bits, plus its encoded columns and
any atom identity.  Equation (7) makes clear why the index is not total
description: the shared table grows with both \(K\) and precision.

## 3. The source-quantization boundary

Exact rational \(\widetilde V\) does not make arbitrary source data exact.
If the stored source operator is \(\widehat R\), the scheme that encodes
its exact columns satisfies
\[
 \mathbb EY(x)=\widehat R x,
\tag{8}
\]
not \(Rx\).  The deterministic bias toward the original source is
\[
 (\widehat R-R)x,
\tag{9}
\]
and its squared norm belongs in the error certificate.  Sampling
unbiasedness cannot remove it.

If the stored encoded-column matrix is \(\widehat P\), define its
effective source operator as \(\widehat R=\widehat P\widetilde V^*\).
Equations (8)--(9) then apply to that operator. This covers stored columns
that approximate \(R\widetilde V e_i\). Exact
unbiasedness toward \(R\) requires exact columns, or a separately declared
unbiased randomized source-quantization mechanism with its own variance,
randomness, and storage proof.

A fixed-width floating-point implementation introduces further deterministic
rounding in \(V^*x\), HT multiplication, accumulation, and possibly the
stored columns.  It generally has
\[
 \mathbb EY_{\rm fl}(x)\ne Rx.
\]
An error bound needs a declared numerical model, word precision, exponent
range, summation order, conditioning bounds, and a comparison of rounding
bias and variance with the target \(\varepsilon\).  Exact algebraic
unbiasedness is not numerical evidence.

## 4. What the rate theorem can and cannot state

A rigorous conditional finite-word theorem can therefore say:

> Under an exact rational (or Gaussian-rational) source-and-query
> representation, exact arbitrary-precision arithmetic, fair-bit sampling,
> and a declared shared transform/sampler table, there exists a library with
> the same index exponent \(\kappa\), a rational common size-\(s\) HT law,
> and exact unbiasedness toward each represented source \(R\).

For general real/complex sources stored in finite words, replace “exact
unbiasedness toward \(R\)” by “exact unbiasedness toward the stored
\(\widehat R\),” and add the source approximation term (9).  There is no
unqualified finite-precision implementation theorem.

The encoded-column payload is also irreducible in this model.  A dense
basis transform mixes source columns; storing only its index does not make
the \(s\) transformed columns available without either storing
\(R\widetilde V\), reading more source data, or declaring another decoder.
Those alternatives have distinct resident-byte and fresh-read costs.  They
must remain separate from the transform-index exponent and from
\(B_{\rm shared}\).
