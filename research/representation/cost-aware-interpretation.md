# Interpreting residual geometry when reads have unequal costs

This investigation asks whether a resident description of relationships among residual pages
can improve their sampling probabilities. It derives an exact optimizer for one stated
estimator class. The proof is complete below; independent review and originality assessment
remain open. The result does not yet establish a better weight representation.

## The quantities the interpreter would need

For a fixed query, partition a residual action into contributions
\(v_j=R_{G_j}x_{G_j}\in\mathbb R^p\). Reading group \(G_j\) has deterministic positive
cost \(c_j\). Delete zero contributions from the sampling support. Write

\[
a_j=\|v_j\|^2>0,\qquad b=\left\|\sum_jv_j\right\|^2,
\qquad C(\pi)=\sum_jc_j\pi_j.
\]

One categorical draw returns \(v_J/\pi_J\). Its expectation is the complete residual action,
and its mean-square error is

\[
V(\pi)=\sum_j a_j/\pi_j-b.
\]

For a fixed, independently chosen sample count \(s\), averaging independent draws has
mean-square error \(V(\pi)/s\) and expected read cost \(sC(\pi)\). Their product is
\(F(\pi)=C(\pi)V(\pi)\). This objective excludes query setup, decoder overhead, repeated-read
reuse, sample-count rounding, and hard read caps; each must be added for a physical comparison.
It also fixes the representation and page partition while optimizing the sampling law.

## Exact optimization over every categorical law

**Proposition C1, derived here.** Let \(a_j,c_j>0\), and let
\(0\le\beta\le(\sum_j\sqrt{a_j})^2\). Over all positive probability vectors, minimize

\[
F_\beta(\pi)=C(\pi)\left(\sum_j a_j/\pi_j-\beta\right).
\]

There is a unique \(\rho\ge0\) satisfying

\[
\sum_j\sqrt{\frac{a_j}{\beta+\rho c_j}}=1. \tag{C1}
\]

When \(\beta=0\), the value at \(\rho=0\) is interpreted as an infinite right limit.
Define \(\pi_j^*=\sqrt{a_j/(\beta+\rho c_j)}\) and
\(C^*=\sum_jc_j\pi_j^*\). Then

\[
\min_\pi F_\beta(\pi)=\rho(C^*)^2,\qquad
\operatorname*{argmin}_\pi F_\beta(\pi)=\{\pi^*\}. \tag{C2}
\]

**Proof.** The left side of (C1) decreases continuously to zero as \(\rho\) increases. Its
value at zero is at least one, so exactly one nonnegative root exists. For any probability
vector \(\pi\), substitution of
\(a_j=(\pi_j^*)^2(\beta+\rho c_j)\) gives

\[
F_\beta(\pi)=\beta C(\pi)
\left(\sum_j\frac{(\pi_j^*)^2}{\pi_j}-1\right)
+\rho C(\pi)\sum_j\frac{c_j(\pi_j^*)^2}{\pi_j}.
\]

Cauchy--Schwarz gives
\(\sum_j(\pi_j^*)^2/\pi_j\ge1\) and
\(C(\pi)\sum_jc_j(\pi_j^*)^2/\pi_j\ge(C^*)^2\).
Therefore the displayed expression is at least \(\rho(C^*)^2\), attained at \(\pi^*\).
If \(\beta>0\), equality in the first inequality forces \(\pi=\pi^*\); when
\(\beta=0\), \(\rho>0\), and equality in the second does so. This proves uniqueness. □

Taking \(\beta=b\) solves the exact cost-times-variance problem for this estimator class.
Taking a certified \(0\le\beta\le b\) gives a valid upper bound and solves that upper-bound
problem exactly. Knowing a lower bound on the squared answer norm can change the optimal law
when the read costs differ. The lower bound does not supply the answer vector.

## A representation that supplies the missing information

Let \(G=R^TR\). For a column partition, each diagonal block \(G_{jj}\) determines
\(a_j=x_{G_j}^TG_{jj}x_{G_j}\), while \(b=x^TGx\). Thus a Gram representation supplies the
quantities in C1 without retaining the output orientation of \(R\). A full real symmetric Gram
matrix takes \(q(q+1)/2\) encoded scalar slots and \(O(q^2)\) query arithmetic, before
precision certificates and layout metadata. It can exceed the weight storage when \(p\) is
small, and it can be smaller for tall matrices. Neither case proves a net saving.

A smaller description can store \(H=Q^TR\), where \(Q\) has orthonormal columns. Then
\(\|Hx\|^2\le b\), so \(\beta=\|Hx\|^2\) is admissible. A rank-\(k\) description of
this form stores \(kq\) scalars without the \(pk\) output-basis scalars. It needs a separate
description of the page contribution norms, which is \(q\) scalars for single-column pages.
For wider pages, within-page Gram blocks or certified bounds replace that diagonal table.

In finite arithmetic, store \(\widetilde H\) with a certificate
\(\|H-\widetilde H\|_{\rm op}\le e\). The admissible lower bound becomes

\[
\beta(x)=\left(\max\{0,\|\widetilde Hx\|-e\|x\|\}\right)^2.
\]

If upper certificates \(u_j\ge a_j\) replace exact norms, optimize
\(C(\pi)(\sum_j u_j/\pi_j-\beta)\). The result remains an error upper bound, since
\(\sum_j a_j/\pi_j-b\le\sum_j u_j/\pi_j-\beta\). Evaluating the displayed formulas
also needs outward rounding or an explicit arithmetic-error allowance. A representable positive
law may approximate C1; recomputing its bound is required instead of asserting exact optimality.

## Explicit stress cases

1. **Unequal costs.** Take \(v_1=(1,0)\), \(v_2=(-2,1)\), and costs \((1,9)\).
   Then \(a=(1,5)\), \(b=2\), \(\rho=2\), and C1 gives
   \(\pi^*=(1/2,1/2)\), with \(F=50\). The optimum for the second-moment bound
   \(\beta=0\) instead uses approximately \((0.572949,0.427051)\), whose actual
   cost-times-variance is \(50.583592\). The former reduces that objective by approximately
   1.1537 percent. This is a two-group arithmetic example, not a device measurement.
2. **Equal costs.** C1 reduces to \(\pi_j^*\propto\sqrt{a_j}\) for every admissible
   \(\beta\). Extra global Gram information cannot improve this sampling law. It can tighten
   a certificate, but the additional memory has not improved the estimator.
3. **Exact cancellation.** If \(\sum_jv_j=0\), then \(b=0\), and C1 is the established
   square-root cost law. This proposed improvement disappears.
4. **Positive alignment.** If all contributions point in the same direction, then
   \(b=(\sum_j\sqrt{a_j})^2\), \(\rho=0\), and the optimal estimator has zero variance.
   It still reads a contribution. A stronger structured-source comparator may already store or
   fetch that shared direction and must be included.
5. **Hidden output basis.** The small \(H\) representation supplies an energy bound but cannot
   itself emit a \(p\)-dimensional residual vector. Its interpreter still pays for fresh
   weight contributions. The absent basis is not free computation.
6. **Fixed precision or a hard budget.** Irrational ideal probabilities require approximation,
   and independent draws can repeat pages. C2 solves neither the best finite-randomness law nor
   the best cached, correlated, or adaptive hard-budget scheme.

## An exact finite-source limit on the relationship description

**Proposition C2, derived here.** For every integer \(q\ge2\), there is a family of finite
matrices with entries in \(\{-1,0,1\}\) such that any source-independent interpreter which
selects the exact C1-optimal one-column law for every two-coordinate query, using only resident
bits and no preliminary external reads, needs at least \(\binom q2\) source-dependent bits.
The column costs are fixed, positive, and pairwise distinct. Unlimited interpretation arithmetic
is allowed; this is an information bound, not a runtime bound.

**Proof.** Choose one independent sign \(\sigma_{ij}\in\{-1,1\}\) for each \(i<j\).
Form \(A_\sigma\) with one row \(e_i^T+\sigma_{ij}e_j^T\) for each pair and one row
\(e_i^T\) for each coordinate. It has \(q+\binom q2\) rows and \(q\) columns, with

\[
(A_\sigma^TA_\sigma)_{ii}=q,
\qquad (A_\sigma^TA_\sigma)_{ij}=\sigma_{ij}.
\]

The Gram matrix is positive definite: for every \(x\),
\(x^TGx\ge q\|x\|^2-\sum_{i<j}2|x_ix_j|\ge\|x\|^2\).
For query \(e_i+e_j\), the two nonzero contributions have energies \(a_i=a_j=q\),
and their squared sum is \(b_{ij}=2q+2\sigma_{ij}\). Given the exact optimal law
\((\pi_i,\pi_j)\), equation C1 yields

\[
b_{ij}=\frac{c_jq/\pi_i^2-c_iq/\pi_j^2}{c_j-c_i}.
\]

Thus the interpreter's laws for all pair queries determine every independent sign. If two
different sign matrices shared a resident state, the interpreter would return the same law on
the pair where their signs differ, contradicting this identity and C1's uniqueness. The
\(2^{\binom q2}\) sources therefore need distinct resident states, which requires at least
\(\binom q2\) bits. □

This proof identifies the cost of demanding the exact optimizer on every source in this family.
An approximate law, restricted query class, preliminary geometry reads, or a more structured
source can change the bound. The next construction question is quantitative: how much of C1's
advantage survives a smaller finite description when exact selection is relaxed by a stated
factor? The sign family supplies a reproducible adversary for that question.

## Reproduction of the numerical attack

On 2026-09-20, Python's standard library checked 700 generated instances and 70,000 competing
probability vectors with seed 20260920. For each dimension from 2 through 8, 100 instances used
four-dimensional vectors with integer coordinates drawn uniformly from -5 through 5 and integer
costs drawn uniformly from 1 through 100. Zero vectors were removed. The root was bracketed by
doubling and bisected 90 times. Each instance was challenged with 100 normalized independent
exponential vectors. No challenger lowered the proposed optimum; the identity in C2 agreed to
relative tolerance \(10^{-8}\). These finite checks attack mistakes in the formula; the proof
above establishes the full-simplex result.

The exact two-group case can be reproduced without numerical optimization:

```python
from math import sqrt
a, costs, b = [1, 5], [1, 9], 2
raw = [sqrt(value / cost) for value, cost in zip(a, costs)]
probabilities = [value / sum(raw) for value in raw]
score = sum(c * p for c, p in zip(costs, probabilities)) * (
    sum(value / p for value, p in zip(a, probabilities)) - b
)
assert abs(score - 50.58359213500126) < 1e-12
assert sum(c / 2 for c in costs) * (sum(2 * value for value in a) - b) == 50
```

## Prior-work attack and disposition

The inverse-probability estimator and low-rank control variate are established. Cugini, Atif,
and Subaşı's [2026 primary preprint, Theorem 1](https://arxiv.org/html/2603.13495v1#S2.Thmtheorem1)
optimizes a cost-times-second-moment bound, giving the \(\beta=0\) law. Its objective drops the
squared mean. C1 retains that term or a certified lower bound on it. Related variance-cost
optimization appears in [Sbert, Havran, and Szirmay-Kalos, 2016](https://dcgi.fel.cvut.cz/~havran/ARTICLES/sberthavranszirmay-kalos2016.pdf)
for multiple importance sampling. Neither search coverage nor this elementary derivation
establishes originality of C1.

The retained result is an exact optimization tool for an improved established baseline. The
representation that makes its inputs cheap remains a construction problem. Equal page costs
remove its sampling-law advantage, and its extra information must win an equal-byte comparison
against storing a better approximation, a transform, or useful weights. Those comparisons remain
open.
