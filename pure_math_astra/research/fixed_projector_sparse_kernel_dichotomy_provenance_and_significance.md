# fixed_projector_sparse_kernel_dichotomy_provenance_and_significance.md — bounded provenance and Cassette-scope assessment of the fixed-projector sparse-kernel dichotomy; depends on ../notes/fixed_projector_sparse_kernel_dichotomy.md, ../notes/fixed_projector_sparse_kernel_dichotomy_independent_review.md, ../notes/k4_diagonal_and_full_linear_rate_separation.md, fixed_projector_volume_sampling_prior_work.md, ../../MATHS.md.

# Fixed-projector sparse-kernel dichotomy: provenance and scope

## Scope and current correctness status

This is a bounded adversarial provenance and consequence check.  It does not
assess publication readiness or establish originality from a search result.

The fixed-projector theorem has an independent mathematical reconstruction in
`../notes/fixed_projector_sparse_kernel_dichotomy_independent_review.md`.
That review supports the stated real, fixed-\(P\), hard-cap conclusion:

\[
 F_k(P+r^2(I-P))
 =
 \begin{cases}
 \Theta_P(r),&W=\ker P,\\
 \Theta_P(1),&W\ne\ker P,
 \end{cases}
\tag{1}
\]

for each \(F_k\in\{\Psi_k,\nu_k\}\), where \(P\) has rank \(k\) on \(\mathbb R^{2k}\), and \(W\) is the span of
null vectors supported on at most \(k\) coordinates.  The constants are not
uniform over projectors.  This assessment takes that proved statement as its
starting point.

Subsequent work gives an explicit repeated-block comparison in
[the K4 page note](../notes/k4_dyadic_full_linear_page_accounting.md)
and [its bounded-bit sampler](../notes/k4_bounded_bit_full_linear_sampler.md).
Those notes supply finite metadata and sampling costs for a declared
original-column format. Their deliberately restricted page and comparator
assumptions do not settle the broader significance question assessed here.

## The exact matroid reformulation

Choose \(A\in\mathbb R^{k\times2k}\) with \(AA^*=I_k\) and \(P=A^*A\).
Let \(\mathcal C_{\le k}(A)\) be the circuit vectors of the represented
column matroid of \(A\) whose supports have cardinality at most \(k\).  Then

\[
 W=\operatorname{span}\mathcal C_{\le k}(A).
\tag{2}
\]

This is elementary but matters for provenance.  A circuit vector in the
right-hand side is a null vector on a support of size at most \(k\), hence is
in \(W\).  Conversely, take \(v\in\ker A\) supported on \(S\),
\(|S|\le k\).  If its support is not minimal, choose a nonzero null vector
with minimal support contained in \(\operatorname{supp}v\), scale it to cancel
one nonzero coordinate of \(v\), and iterate.  This writes \(v\) as a sum of
circuit vectors supported in \(S\).  The iteration terminates because the
support strictly decreases.

Thus the classification condition is the familiar circuit-space condition

\[
 \ker A=\operatorname{span}\mathcal C_{\le k}(A),
\tag{3}
\]

not a new kind of nullspace object.  It asks whether the kernel is generated
by the *short* circuits, rather than by all circuits.

The closest source actually read is Franz Király and Louis Theran,
[*Matroid Regression*](https://arxiv.org/abs/1403.0873), arXiv:1403.0873
(2014), Proposition 3.2 and Lemma 3.6.  It identifies circuit supports with
minimal-support kernel vectors and explicitly uses the standard fact that
such vectors span the kernel.  Its problem is local estimation in sparse
linear systems, with circuit-based linear estimators.  It does not study the
short-circuit truncation in (3), a vanishing eigenvalue \(r^2\), or a
worst-query hard-cap risk.

## Established ingredients

The proof imports, or closely parallels, several established ideas.

| Ingredient in (1) | Closest checked primary source | What is established | Limit for (1) |
|---|---|---|---|
| Short null generators and their span | Király--Theran, Proposition 3.2 and Lemma 3.6 | Circuit vectors are minimal-support dependencies and all minimal-support kernel vectors span the kernel. | It gives no threshold-\(k\) risk dichotomy. |
| High-space unbiased law | Michał Dereziński and Manfred K. Warmuth, [*Reverse Iterative Volume Sampling for Linear Regression*](https://jmlr.csail.mit.edu/papers/volume19/17-781/17-781.pdf), JMLR 19 (2018), Theorems 5--6 | Exact-size volume sampling gives an unbiased pseudoinverse and projection estimator; the inverse second moment has the required \(q-k+1\) upper bound without full support. | It has no sparse nullspace branch, support-event lower bound, or metric \(P+r^2(I-P)\). |
| Conditional-mean reduction for a hard support cap | Leo Barnes et al., [*Efficient Unbiased Sparsification*](https://arxiv.org/html/2402.14925v2), arXiv:2402.14925v2, Definition I.2 and Lemma 1 | Unbiased \(m\)-sparse random vectors and conditioning on each support facet are standard. | Their exact optimization theorems require nonnegative outputs and separable or permutation-invariant divergences; \(y^T(P+r^2N)y\) is generally neither. |
| Fixed-input unbiased atomic compression | Hanlin Wang et al., [*ATOMO: Communication-Efficient Learning via Atomic Sparsification*](https://proceedings.neurips.cc/paper_files/paper/2018/file/33b3214d792caf311e1f00fd22b392c5-Paper.pdf), NeurIPS 2018, Sections 2--5 | A fixed atomic decomposition, inclusion probabilities, variance, and a representation-dependent communication account are established. | ATOMO uses independent Bernoulli inclusion and an expected sparsity budget.  It does not optimize all almost-sure \(k\)-sparse laws or derive (1). |
| Singular fixed-query design | Guillaume Sagnol, [*Computing Optimal Designs of Multiresponse Experiments Reduces to Second-Order Cone Programming*](https://arxiv.org/pdf/0912.5467), 2011, Theorems 3.1, 3.3, 4.3, and 5.1 | Finite multiresponse \(c\)-optimal design has an SOCP/SDP formulation, including a singular information matrix when the target is estimable. | It treats one specified estimand and a design criterion.  It does not take the outer worst-query supremum, impose the same hard support on every realized output, or state a small-\(r\) circuit-span rate classification. |

The volume-sampling translation is recorded separately in
`fixed_projector_volume_sampling_prior_work.md`; in particular, its use here
is an established matrix identity rather than a new estimator.

## The support-event converse

The lower half of (1) is not supplied by the checked sources in this form.
Its argument is a finite-support estimate with two distinct cases:

1. If short circuits span the kernel, a generic high-space query forces any
   output that carries enough null mean to place nonzero probability on a
   singular support.  High-space displacement bounds that probability; then
   Cauchy--Schwarz forces a reciprocal null second moment.  Balancing it
   against the \(r^2\) null metric produces order \(r\).
2. If short circuits do not span the kernel, a null functional annihilating
   every short-circuit direction factors through every allowed support's
   high projection.  The corresponding null query has a fixed positive
   high-space error floor.

This is more specific than the standard fact that circuits span a kernel, and
more specific than a singular \(c\)-optimal-design formulation.  It may still
be a routine finite-dimensional consequence once those two frameworks are
combined.  In this bounded pass, no checked primary source states this
support-event dichotomy or the exact criterion (3).  That is a limit of the
search, not evidence of novelty.

The theorem's *form* should therefore be described conservatively: a clean
classification assembled from standard circuit, Cauchy--Binet, and convex
estimation tools, with the direct prior-art status of the assembled
small-\(r\) statement unresolved.

## What it changes in the declared Cassette execution model

The mathematical construction has a direct execution interpretation only
after a plan declares a residual factor \(R\) with

\[
 R^*R=P+r^2(I-P).
\tag{4}
\]

For a coefficient output \(Y\), fetching exactly the columns indexed by
\(\operatorname{supp}Y\) and returning \(RY\) is unbiased for \(Rx\) when
\(\mathbb E Y=x\), and its mean-square output error is

\[
 \mathbb E\|R(Y-x)\|_2^2
 =\mathbb E(Y-x)^T(P+r^2(I-P))(Y-x).
\tag{5}
\]

Thus, for this declared residual and coordinate system, the first branch of
(1) proves that a common random \(k\)-column law can reach an \(O(r)\)
one-step worst-query variance.  The \(K_4\) specialization additionally
proves that the narrower class of diagonal, coordinatewise weights retains a
constant error floor.  This is a distinction between two legal
coefficient laws with the same per-outcome column cap, provided their
coefficient maps and sampler are declared resident metadata.

That distinction does not yet give a Cassette resource frontier.  MATHS
allows residual column sampling as a sufficient execution law
([MATHS.md](../../MATHS.md) lines 390--435), but it requires any actual plan
to account separately for resident reconstruction, exact sampling metadata,
and encoded fresh traffic (lines 437--492).  The theorem is fixed-dimensional
and its constants depend on \(P\); it supplies neither an asymptotic family
nor bounds for the resident maps \(H_S\), the sparse-null mixture, random-bit
generation, selector work, page grouping, or encoded-byte reads.  It also
does not compare total description bytes with a competing description.

Accordingly, the supported Cassette consequence is narrow: a plan may not
replace general \(k\)-row coefficient laws by diagonal Horvitz--Thompson
weights when certifying variance under the same fresh-column cap.  The
unresolved bridge to a consequential execution result is an explicit growing
family of residual factors and a finite-word implementation for which the
full-law metadata and read accounting remain controlled while every declared
diagonal or otherwise restricted comparator has a provably worse certified
fresh-traffic/error tradeoff.  That bridge concerns the execution fields,
not unrelated atom-compatibility certificates.

The certificate fields that such a bridge must fill are distinct resident
description and metadata bytes, peak and total fresh traffic, and composed
execution risk; MATHS lists them at lines 730--772.  Equation (1) proves only
the one-step risk part of such an execution claim.

## Search boundary

I read the cited primary theorem statements and relevant proofs or setup:
the Dereziński--Warmuth JMLR paper, the Király--Theran preprint, Barnes et
al.'s primary arXiv HTML, the ATOMO NeurIPS PDF, and Sagnol's primary
preprint/PDF.  I did not complete a systematic search of matroid circuit
spaces with a cardinality truncation, parametric singular optimal-design
asymptotics, or data-access lower bounds.  This note neither asserts that
the dichotomy is original nor treats a search miss as an originality result.
