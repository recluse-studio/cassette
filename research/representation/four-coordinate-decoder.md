# Exact signed-sum two-sparse decoder

**Status: proved pointwise decoder for every real dimension.** This note gives a
three-regime law attaining the minimum second moment among all real unbiased
outputs with hard support at most two and exact coordinate sum in every
outcome. It replaces the six-pair cone program as the primary decoder. The
cone program remains below as an independent finite-dimensional reference.

The pointwise proof is independent of the separate global calculations in
`four-coordinate-optimality.md` and `dimension-optimality.md`. Those files
address worst-query constants; this one supplies the exact decoder used in
that comparison.

## 1. Problem and dual

For \(x\in\mathbb R^n\) with \(n\ge2\), define

\[
 t=\mathbf1^{\mathsf T}x,\qquad
 \phi(x)=\inf\left\{\mathbb E\|Y\|_2^2:
 \mathbb EY=x,\ \|Y\|_0\le2,\ \mathbf1^{\mathsf T}Y=t\
 \text{almost surely}\right\}.
 \tag{1}
\]

Then \(J(x)=\phi(x)-\|x\|_2^2\).

The zero vector returns zero. For nonzero \(x\), replace \(x\) by \(-x\) if
\(t<0\), run the decoder, and negate its output. Hence assume \(t\ge0\).
Put

\[
 P=\sum_{x_i>0}x_i,\qquad
 N=\sum_{x_i<0}(-x_i),\qquad
 t=P-N,
 \tag{2}
\]

and let \(h=\max_i x_i\) over positive coordinates.

For a dual vector \(\lambda\in\mathbb R^n\), the conjugate of the squared
norm over the two-coordinate affine atom on pair \(ij\) is

\[
 q_{ij}(\lambda)
 ={t\over2}(\lambda_i+\lambda_j)-{t^2\over2}
   +{(\lambda_i-\lambda_j)^2\over8}.
 \tag{3}
\]

Indeed, write an atom as
\(t(e_i+e_j)/2+a(e_i-e_j)\) and maximize
\(\lambda^{\mathsf T}Y-\|Y\|_2^2\) in \(a\). Finite-dimensional convex
duality gives

\[
 \phi(x)=\sup_{\lambda\in\mathbb R^n}
 \left\{\lambda^{\mathsf T}x-\max_{i<j}q_{ij}(\lambda)\right\}.
 \tag{4}
\]

The three laws below provide a feasible primal law and a \(\lambda\) whose
value in (4) is the same. They are therefore pointwise optimal.

## 2. Case A: positive-negative transport

Suppose

\[
 N\ge {t\over2}.
 \tag{5}
\]

This includes every nonzero \(t=0\) query. Choose \(i\) among positive
coordinates with probability \(x_i/P\), choose \(j\) among negative
coordinates with probability \((-x_j)/N\), independently, and return

\[
 Y=Pe_i-Ne_j.
 \tag{6}
\]

The mean is \(x\), the support has two coordinates, and every outcome has
sum \(P-N=t\). Its second moment is

\[
 \phi_A=P^2+N^2.
 \tag{7}
\]

For the matching dual, take

\[
 \lambda_i=
 \begin{cases}
 2P,&x_i>0,\\
 -2N,&x_i<0,\\
 0,&x_i=0.
 \end{cases}
 \tag{8}
\]

A positive-negative pair has \(q_{ij}=P^2+N^2\). The condition (5) is
equivalent to \(P\le3N\), and direct substitution shows that positive-positive,
negative-negative, and pairs involving a zero coordinate have no larger
value. Since
\(\lambda^{\mathsf T}x=2(P^2+N^2)\), (4) equals (7).

## 3. Case B: mixed positive-positive and positive-negative pairs

Suppose

\[
 N<{t\over2},
 \qquad
 h\le {t\over2}+2N.
 \tag{9}
\]

Put \(M=2N/t\). Choose nonnegative numbers \(r_i\), indexed by positive
coordinates, such that

\[
 \max\left(0,{2x_i/t-(1-M)\over3}\right)
 \le r_i\le {2x_i\over3t},
 \qquad
 \sum_i r_i=M.
 \tag{10}
\]

They exist. Let \(T_0=t/2-N\). If two or more lower bounds in (10) are
active, their sum is at most

\[
 {2(P-2T_0)\over3t}={2N\over t}=M.
\]

If exactly one is active, the same conclusion is equivalent to the second
condition in (9). The sum of the upper bounds is at least \(M\) because
\(N<t/2\). Greedy filling between lower and upper endpoints now produces
\(r\).

When \(N=0\), take \(r_i=0\) for every positive coordinate. The
positive-negative branch below then has probability zero and is omitted; no
conditional distribution with a zero denominator is formed.

Define

\[
 d_i={2x_i\over t}-3r_i.
 \tag{11}
\]

Then \(0\le d_i\le1-M\) and \(\sum_i d_i=2(1-M)\). A fractional pair
distribution of total mass \(1-M\) with degrees \(d_i\) exists: normalize
the degrees by \(1-M\), partition an interval of length two into consecutive
intervals of those lengths, draw \(U\) uniformly from \([0,1)\), and select
the two intervals containing \(U\) and \(U+1\). Each normalized degree is at
most one, so the two selected coordinates are distinct.

Use the following two branches.

- With probability \(M\), choose a positive coordinate \(i\) with
  conditional probability \(r_i/M\), choose a negative coordinate \(j\)
  with conditional probability \((-x_j)/N\), and return
  \[
  Y={3t\over2}e_i-{t\over2}e_j.
  \tag{12}
  \]
- With probability \(1-M\), choose a positive-positive pair from the
  degree distribution above, and return
  \[
  Y={t\over2}(e_i+e_j).
  \tag{13}
  \]

The negative coordinates receive exactly their target mean in (12), and
(11) makes the positive means exact. Every outcome sums to \(t\). Its second
moment is

\[
 \phi_B=M{5t^2\over2}+(1-M){t^2\over2}
       ={t^2\over2}+4tN.
 \tag{14}
\]

For the dual choose \(\lambda_i=0\) on positive coordinates,
\(\lambda_i=-4t\) on negative coordinates, and zero on inactive
coordinates. Positive-positive and positive-negative pairs both give

\[
 \max q_{ij}=-{t^2\over2};
\]

negative-negative pairs are lower. Also
\(\lambda^{\mathsf T}x=4tN\), so (4) equals (14).

## 4. Case C: a dominant positive anchor

Suppose

\[
 N<{t\over2},
 \qquad
 h>{t\over2}+2N.
 \tag{15}
\]

Choose an anchor \(a\) with \(x_a=h\), and put

\[
 L=P+N-h=t+2N-h<{t\over2}.
 \tag{16}
\]

If \(L=0\), return \(x\) deterministically. Its dual certificate is
\(\lambda_a=2t\), \(\lambda_i=0\) for \(i\ne a\). Otherwise choose an index
\(j\ne a\) with probability \(|x_j|/L\), and return

\[
 Y=\operatorname{sign}(x_j)L e_j+
       \left(t-\operatorname{sign}(x_j)L\right)e_a.
 \tag{17}
\]

The expected value at each nonanchor coordinate is \(x_j\), and the anchor
mean is \(t-\sum_{j\ne a}x_j=h\). Thus the mean and sum invariants are exact.
The second moment is

\[
 \phi_C=2th-t^2+2L^2.
 \tag{18}
\]

For the matching dual set

\[
\lambda_a=0,\qquad
\lambda_i=-2t+4L\quad(x_i>0,\ i\ne a),\qquad
\lambda_i=-2t-4L\quad(x_i<0),\qquad
\lambda_i=-2t+4L\quad(x_i=0).
\tag{19}
\]

Pairs joining the anchor to an active nonanchor have

\[
 q_{ai}=-t^2+2L^2.
\]

The remaining pair types do not exceed this value because \(L<t/2\); for a
positive-negative nonanchor pair the difference is
\(3t^2/2-6L^2>0\). Finally,

\[
 \lambda^{\mathsf T}x-\max q_{ij}
 =2th-t^2+2L^2,
\]

which proves optimality.

Together, Cases A--C prove the following result.

### Theorem 1 — exact arbitrary-dimension decoder

For \(n\ge2\), the three-regime decoder attains \(\phi(x)\) for every
\(x\in\mathbb R^n\). For \(n=1\), the sole feasible output is \(Y=x\)
deterministically, so the same conclusion is immediate.
It uses at most two coordinates in every outcome, preserves the signed
coordinate sum exactly, and has no source-dependent persistent state.

The result is homogeneous: scaling \(x\) scales every output and every
second moment by the same factor. It is an exact coefficient-decoder theorem,
not an encoded-page or matrix-runtime result.

## 5. Exact dyadic implementation

Let the query entries be dyadic,

\[
 x_i={a_i\over2^d},\qquad a_i\in\mathbb Z,\qquad
 A=\max_i|a_i|.
 \tag{20}
\]

Apply the sign flip to the integers if necessary, and write integer
\(P,N,T=P-N\), with \(T\ge0\). Every nonzero output coefficient below has
denominator at most \(2^{d+1}\).

Case A selects positive and negative integer masses independently and returns
\(P/2^d\) and \(-N/2^d\).

In Case B, choose integers \(R_i\) by greedy filling so that

\[
 \max(0,2a_i-T+2N)\le R_i\le2a_i,
 \qquad
 \sum_iR_i=6N.
 \tag{21}
\]

Then \(r_i=R_i/(3T)\). Use a positive-negative branch of probability
\(2N/T\). In that branch, choose

\[
 \Pr(i\mid\mathrm{pn})={R_i\over6N},\qquad
 \Pr(j\mid\mathrm{pn})={-a_j\over N},
\]

and return

\[
 {3T\over2^{d+1}}e_i-{T\over2^{d+1}}e_j.
 \tag{22}
\]

If \(N=0\), omit this branch before evaluating either displayed conditional
probability. Equation (21) then gives \(R_i=0\), and the
positive-positive branch alone is the exact law.

Otherwise, with probability \(1-2N/T\), use the positive-positive branch.
Set

\[
 D_i={2a_i-R_i\over T-2N}.
 \tag{23}
\]

The \(D_i\)'s are inclusion probabilities in \([0,1]\) and sum to two.
Choose an integer \(U\) uniformly from
\(\{0,\ldots,T-2N-1\}\), partition the integer interval
\([0,2(T-2N))\) into positive-coordinate intervals of lengths
\(2a_i-R_i\), and select the intervals containing \(U\) and \(U+(T-2N)\).
Return \(T/2^{d+1}\) on both selected coordinates. This is exact
systematic sampling of the required pair degree law.

Case C selects \(j\ne a\) from integer masses \(|a_j|\), then returns

\[
 {\operatorname{sign}(a_j)L\over2^d}e_j+
 {T-\operatorname{sign}(a_j)L\over2^d}e_a.
 \tag{24}
\]

Thus the finite implementation is not a numerical approximation of the
real decoder. For a query with \(b\)-bit integer numerators, all intermediate
masses have \(O(b+\log n)\) bits and every output numerator is bounded in
absolute value by \(4nA\) at denominator \(2^{d+1}\).

At most three exact integer draws occur per query: the Case-B branch and,
only in its positive-negative branch, one positive and one negative draw.
Every ticket total is at most \(6nA\). Rejection from the next power of two
therefore uses fewer than \(2\lceil\log_2(6nA+1)\rceil\) fair bits in
expectation per draw. The probability that one such draw needs more than
\(r\) trials is below \(2^{-r}\); three draws give a union bound below
\(3\cdot2^{-r}\). The decoder scans \(O(n)\) coordinates. It needs only
\(O(b+\log n)\)-bit scalar workspace beyond the query and output: Case B
recomputes each greedy \(R_i\) and each interval endpoint during a constant
number of passes, rather than retaining an \(n\)-entry \(R\) array. Every
outcome names at most two original columns/pages.

The random-bit tail, physical encoded-byte cost of a named column, cache
state, and arithmetic behavior of a native kernel remain separate resource
claims.

## 6. Four-coordinate constant

For the symmetric four-coordinate family

\[
 x=(r,r,r,-1),\qquad
 r={5+2\sqrt {13}\over9},
\]

the earlier positive-positive/positive-negative construction has ratio
\(\sqrt {13}-2\). The exact decoder proves that no other two-sparse,
signed-sum-preserving law improves that pointwise value. The separate global
argument is recorded in `four-coordinate-optimality.md`; the arbitrary-
dimension counterpart is recorded in `dimension-optimality.md`. Neither
global statement follows merely from the pointwise decoder.

## 7. Six-pair cone program: independent reference

For \(n=4\), the earlier six-edge perspective program remains an independent
description of the same optimum:

\[
 \phi(x)=
 \min_{\substack{p\ge0,\ \mathbf1^{\mathsf T}p=1\\
                 x=\frac t2Cp+Bf}}
 \left\{{t^2\over2}+2\sum_{e\in K_4}{f_e^2\over p_e}\right\}.
 \tag{25}
\]

Conditional Jensen proves this representation, and the three-regime result
now supplies its closed-form optimizer without an SOCP. The cone program
remains useful as a small independent numerical and symbolic check.

## 8. Prior-work collision check

The ingredients are established in nearby forms.

- Barnes et al., [Efficient Unbiased Sparsification](https://arxiv.org/html/2402.14925v2), study hard unbiased sparsification and explicitly discuss sum-preserving outputs. Their checked results use permutation-invariant or separable losses and an orthant-preserving sign treatment. They do not, from the checked source, state the mixed-sign, signed-sum affine atom problem or the three-regime exact formula here.
- Deville and Tillé's [cube method](https://doc.rero.ch/record/296198/files/914893.pdf) is established fixed-size balanced sampling. The Case-B systematic pair distribution is a small exact instance of this general rounding family.
- Weare and Webber, [Randomly sparsified Richardson iteration](https://onlinelibrary.wiley.com/doi/10.1002/cpa.70012), give pivotal hard sparsification with exact mean and \(\ell_1\)-mass preservation. On a common-sign input that is stronger than signed-sum preservation. It does not impose the mixed-sign invariant outcome by outcome.
- Anaraki and Becker, [Preconditioned data sparsification for big data with applications to PCA and k-means](https://arxiv.org/abs/1511.00152), combine a preconditioning transform with sparsification. That establishes the broad transform-then-sparsify pattern; it does not, from the checked description, supply the declared four-record Gram calculation, the exact two-read minimax comparison, or the affine signed-sum decoder used here.

Conditional Jensen, transport sampling, dependent rounding, and integer ticket
sampling are therefore not novel claims. The exact all-real formula is a
narrower object and needs a complete primary-source review before any
originality conclusion.

## 9. Limits

The decoder alone optimizes coefficient error only. Sections 10--11 add one
declared four-record representation and its matrix-product bound. They do not
establish a sequential execution guarantee, a generic resident codebook
result, or the separate observation and composition certificates required by
MATHS.md.

## 10. Fully optimized spectral-page comparator

This section fixes a narrow comparator. It is the four transformed columns
whose Gram matrix is diagonal; it is not a lower bound for every possible
four-record encoding.

Let \(Q\) be a declared real orthogonal right basis and suppose

\[
 C=AQ,\qquad C^{\mathsf T}C
 =\eta\operatorname{diag}(s,1,1,1),
 \qquad \eta>0,\quad s>1.
 \tag{26}
\]

For the rank-one family in the request,
\(A^{\mathsf T}A=\alpha dd^{\mathsf T}+\eta I\), take the first column of
\(Q\) to be \(d/2\). Then

\[
 s={4\alpha+\eta\over\eta}=1+{4\alpha\over\eta}.
 \tag{27}
\]

For a query \(c=Q^{\mathsf T}x\), consider *every* unbiased estimator
returned as \(CZ\), where \(Z\) has at most two nonzero transformed
coefficients and only the corresponding \(C\) column records are fetched.
This comparator permits every coefficient law in that read model; it does
not permit an arbitrary resident output basis. Put
\(p_i=\Pr(Z_i\ne0)\). Conditional Jensen gives

\[
 \mathbb E Z_i^2\ge {c_i^2\over p_i},
 \qquad 0\le p_i\le1,\qquad \sum_i p_i\le2.
 \tag{28}
\]

Conversely, every such \(p\) is a convex combination of subsets of
\(\{0,1,2,3\}\) of size at most two. Select one of those subsets and use
\(Z_i=c_i/p_i\) when it contains \(i\). Thus (28) is sharp, and the exact
pointwise optimum is

\[
 \inf_Z\mathbb E\|C(Z-c)\|_2^2
 =\min_{\substack{0\le p_i\le1\\\sum p_i\le2}}
 \sum_i \eta(s,1,1,1)_i c_i^2\left({1\over p_i}-1\right).
 \tag{29}
\]

This is the weighted hard-sparsification calculation used by established
EUS-style sampling. It has been derived here because the comparison needs
the optimum over the whole stated estimator class, rather than a particular
two-rule sampler.

Define

\[
 k_s={\sqrt{s^2+14s+1}-s-1\over2},
 \qquad
 \Gamma_{\rm spec}(s)={k_s+1\over2}
 ={1-s+\sqrt{s^2+14s+1}\over4}.
 \tag{30}
\]

### Theorem 2 — exact spectral-page worst case

The exact global risk of (29) is

\[
 \sup_{c\ne0}{\inf_Z\mathbb E\|C(Z-c)\|_2^2\over\|c\|_2^2}
 =\eta\Gamma_{\rm spec}(s).
 \tag{31}
\]

**Proof.** Set fixed inclusion probabilities

\[
 p_0={2k_s\over k_s+3},\qquad
 p_1=p_2=p_3={2\over k_s+3}.
 \tag{32}
\]

The positive root \(k_s\) satisfies

\[
 k_s^2+(s+1)k_s-3s=0,\qquad 1<k_s<3.
 \tag{33}
\]

Hence (32) is feasible and both coordinate risks are the same:

\[
 s\left({1\over p_0}-1\right)
 ={1\over p_1}-1={k_s+1\over2}.
 \tag{34}
\]

The law attaining (32) gives risk at most
\(\eta\Gamma_{\rm spec}(s)\|c\|_2^2\) for every query. For the reverse
inequality, take three residual magnitudes equal to \(u\) and set

\[
 |c_0|={k_su\over\sqrt{s}},\qquad |c_1|=|c_2|=|c_3|=u.
 \tag{35}
\]

The KKT rule for (29) makes its optimal inclusions proportional to
\(\sqrt{s}|c_0|,|c_1|,|c_2|,|c_3|=(k_su,u,u,u)\), which is precisely (32).
No inclusion is capped because \(k_s<3\). Equality holds in (28), so this
single real query has ratio \(\eta\Gamma_{\rm spec}(s)\). \(\square\)

The formula increases from \(\eta\) at \(s=1\) to \(2\eta\) as
\(s\to\infty\). If \(\gamma=\sqrt{13}-2\) is the exact signed-sum
two-sparse coefficient constant, then

\[
 \Gamma_{\rm spec}(s)
 \begin{cases}
 <\gamma,&1<s<9,\\
 =\gamma,&s=9,\\
 >\gamma,&s>9.
 \end{cases}
 \tag{36}
\]

For (27), the strict regime is \(\alpha>2\eta\). Thus the signed decoder
has a strict worst-query advantage of
\(\eta[\Gamma_{\rm spec}(s)-\gamma]\) over this fully optimized
spectral-page comparator exactly in that regime. At \(s=16\), for example,
the comparator constant is
\((\sqrt{481}-15)/4\approx1.7329\), while the signed decoder constant is
\(\sqrt{13}-2\approx1.6056\).

There is also a strictly finite dyadic witness at \(s=16\): take
\(c=(3/4,1,1,1)\). The optimized spectral law includes the leading record
with probability one and each residual record with probability \(1/3\).
Its risk is \(6\), \(\|c\|_2^2=57/16\), and its ratio is
\(32/19\approx1.68421\). The signed decoder has risk at most
\(\gamma\|c\|_2^2\) in the matched joint layout, proving a finite-format
improvement of at least \(1-19\gamma/32\approx4.67\%\) on this witness.
The larger real-continuous worst-case gap at \(s=16\) is about \(7.35\%\);
it is not asserted for this dyadic witness without a separate approximation
certificate.

An exact fixed-format enumeration supplies a stronger finite statement for
this same \(s=16\) comparison. It evaluates all 83,520 nonzero integer
queries in \(\{-8,\ldots,8\}^4\), uses exact rational arithmetic for both
pointwise-optimal spectral EUS and the coupled signed decoder, and represents
the Hadamard query transform with one fractional bit.

| Fixed query family | Spectral peak | Joint signed peak | Relative reduction |
|---|---:|---:|---:|
| \(c\in\{-8,\ldots,8\}^4\setminus\{0\}\), \(s=16\) | \(376/217\) | \(69/43\) | \(1195/16168\approx7.39114\%\) |

The spectral peak occurs at \((-5,-8,-8,-8)\); the joint peak occurs at
\((-8,-6,-6,6)\). The two maxima need not occur at the same query. The
reproducible exact calculation and its scope are recorded in
[finite-checks.md](finite-checks.md). This is a finite query-family result,
not a claim about all models or page representations.

The calculation has a useful general form. If orthogonal page norms squared
are \(\lambda_1,\ldots,\lambda_n>0\) and the hard cap is \(m<n\), there is a
unique \(\rho>0\) with

\[
 \sum_{i=1}^n {\lambda_i\over\lambda_i+\rho}=m.
 \tag{37}
\]

The exact global optimum over all unbiased hard-\(m\)-sparse estimators is
\(\rho\). Indeed, use fixed inclusions
\(p_i=\lambda_i/(\lambda_i+\rho)\); their sum is \(m\), and their coordinate
risks all equal \(\rho\). Equality is attained at a query with
\(c_i\) proportional to \(\sqrt{\lambda_i}/(\lambda_i+\rho)\), because its
uncapped KKT inclusions are the same \(p_i\). Equation (30) is (37) for
\(\lambda=\eta(s,1,1,1)\) and \(m=2\).

## 11. Joint page construction

The preceding comparison becomes a representation-and-interpretation pair
when the pages are changed before the query. Let \(H\) be the fixed
symmetric normalized four-by-four Hadamard matrix whose first row and column
are \(\mathbf1^{\mathsf T}/2\), and define

\[
 B=C H=AQH,\qquad z=H Q^{\mathsf T}x.
 \tag{40}
\]

Then \(Ax=Bz\), \(\|z\|_2=\|x\|_2\), and direct multiplication gives

\[
 B^{\mathsf T}B
 =\eta I+{\eta(s-1)\over4}\mathbf1\mathbf1^{\mathsf T}.
 \tag{41}
\]

Apply Theorem 1 to \(z\), fetching the at-most-two column records named by
its output \(Y\). It preserves \(\mathbf1^{\mathsf T}Y=\mathbf1^{\mathsf T}z\) in
every outcome. Therefore the rank-one term in (41) cancels exactly, and

\[
 \mathbb E\|B(Y-z)\|_2^2
 =\eta\mathbb E\|Y-z\|_2^2
 \le\eta\gamma\|x\|_2^2.
 \tag{42}
\]

The bound is sharp under the four-coordinate global result. Combined with
(31), (42) is a strict worst-case improvement over the named spectral-page
encoding when \(s>9\). It makes no claim against an unrestricted transform
codebook or a non-two-sparse decoder.

For an exact finite comparison, restrict to a declared dyadic \(Q\), dyadic
source column entries, and the fixed dyadic \(H\). A dyadic eigenbasis is a
declared source-family assumption here; a general dyadic \(A\) need not have
one. Each alternative preserves \(A\) as its source and materializes its own
four transformed \(p\)-entry column records: the comparator stores \(C\),
while the joint construction stores \(B\). Choose one common exact dyadic
scale and \(w\)-bit field width that represents both record families; padding
is part of the comparator's charged layout. With a fixed 64-byte record
header, each column record uses

\[
 P_{\rm col}=4096\left\lceil{\lceil pw/8\rceil+64\over4096}\right\rceil
 \quad\hbox{bytes}.
 \tag{43}
\]

Both layouts therefore occupy exactly \(4P_{\rm col}\) encoded bytes, have
the same query precision and resident \(Q\) descriptor, and read at most two
records, hence at most \(2P_{\rm col}\) physical bytes. Each layout uses a
same-size fixed transform header; \(H\) is selected by that header and is
fixed data rather than an additional resident codebook. The joint layout
still charges its transformed-record construction, the \(H\) query multiply,
and the Gram certificate (41). The source scale, \(w\), header size, and
record span must be declared; no floating-point equality is presumed. If
\(Q\)'s entries have declared denominator \(2^{d_Q}\), the common query
workspace reserves that denominator and one further fractional bit for
\(H Q^{\mathsf T}x\); the spectral comparator receives the same unused
fractional-bit headroom.

The \(s=16\) finite grid has one concrete common layout. Set \(Q=I\),
\(A=C=\operatorname{diag}(4,1,1,1)\), and \(B=CH\). At dyadic scale
\(1/2\), signed width \(w=8\) represents every scalar exactly: the largest
spectral-record mantissa is \(8\), while the joint-record mantissas are
\(4\) and \(\pm1\). With \(p=4\), (43) gives
\(P_{\rm col}=4096\) bytes, so each layout occupies 16,384 encoded bytes
and any two-record output reads at most 8,192 physical bytes. The integer
grid is padded to the same denominator-two query workspace format used by
\(Hc\). Both alternatives may use a common 32-bit scalar workspace with
three fractional bits for realized coefficients and output accumulation.
For this grid, spectral masses are at most 56 in total, so the uncapped
leading coefficient has denominator at most eight; capped and residual
coefficients fit the same format. The signed decoder's half-integer input
and at-most-one additional fractional bit also fit. The finite bounds in
section 5 put its intermediate integer masses well within the same width.

Hadamard mixing, diagonal spectral storage, and unbiased hard
sparsification are established ingredients. The exact combination above is
a candidate construction under primary-source review, not an established
novelty claim.

The same argument also gives an anisotropic certificate. If
\(C^{\mathsf T}C=\operatorname{diag}(\lambda_0,\lambda_1,\lambda_2,
\lambda_3)\), use the same \(H\) with the \(\lambda_0\) direction first.
The signed decoder cancels that direction exactly after mixing. The remaining
quadratic form has operator norm
\(\max(\lambda_1,\lambda_2,\lambda_3)\), so its global risk is at most

\[
 \gamma\max(\lambda_1,\lambda_2,\lambda_3).
 \tag{44}
\]

The diagonal spectral-page comparator has exact global risk \(\rho\) from
(37). Therefore (44) is a strict certified improvement whenever

\[
 \gamma\max(\lambda_1,\lambda_2,\lambda_3)<\rho.
 \tag{45}
\]

This is an open condition on the declared spectrum. It is an upper bound for
the joint decoder, sufficient for a strict comparison; it does not assert
its exact anisotropic worst-query constant.
