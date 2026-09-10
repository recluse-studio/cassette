# Cassette consequence audit for the q=4 query-adaptive basis question; depends on MATHS.md, pure_math_lab/RESEARCH_LEDGER.md, query_adaptive_atomic_dual.md, procedural_transform_decoder.md, encoded_column_rounding_bound.md.

Status: bounded consequence audit. This is neither a manuscript proposal nor
an originality assessment.

## Exact fact: what the q=4 value measures

Let \(R=A-B\) be the residual after one declared resident description, let
\(Q\) be an orthogonal or unitary query transform, and store the encoded
columns of

\[
 P=RQ^*.
\]

For query \(x\), put \(z=Qx\). Any random \(Y\) with
\(\mathbb EY=z\) and \(\|Y\|_0\le s\) produces the unbiased answer

\[
 Bx+PY,
 \qquad
 \mathbb E(Bx+PY)=Ax,
\]

and its conditional squared error is

\[
 \mathbb E\|P(Y-z)\|_2^2.
\tag{1}
\]

Since \(P^*P=QR^*RQ^*\), \(\Psi_s(QR^*RQ^*)\) is exactly the best
worst-query one-call variance within this encoded-column, exact-mean,
at-most-\(s\)-fresh-column model. This is a direct identification with the
atomic definition in `query_adaptive_atomic_dual.md:7-19`, not a new
theorem. It preserves the mean constraint \(\mathbb EY=z\), rather than
replacing it by equality only after applying \(P\).

The identification touches Cassette's execution layer, not its condition
geometry: MATHS fixes an atom \(A\), a resident reconstruction \(B\), and
the residual \(R=A-B\) separately (`MATHS.md:390-405`). It is compatible
with fresh reads only when the selected columns of \(P\) are legal declared
source objects.

## What either q=4 result would change

**Verified conditional consequence of a lower bound.** If

\[
 \inf_Q\Psi_2\!\left(Q\operatorname{Diag}(1,1,\eta,\eta)Q^*\right)
 \ge c\sqrt\eta,
\tag{2}
\]

then no one-call, two-column, exact-mean encoded sketch can certify a
smaller worst-query variance for a residual with precisely that Gram
spectrum. It would rule out a basis-selection escape within this narrow
execution class. In particular, a one-call certificate restricted to this
class cannot have a uniform squared-error upper bound below
\(c\sqrt\eta\) in residual-Gram units; comparison with Cassette's
relative \(\varepsilon_{\rm exec}\) requires the separately declared
normalization by \(\|A\|_F^2\).

**Verified conditional consequence of an upper bound.** An explicit
finite-word \(Q\) and sparse query law with
\(\Psi_2=o(\sqrt\eta)\) would give a legal abstract two-column sketch with
strictly lower one-call variance. It could improve the execution-error
field of an otherwise declared residual plan. This is stronger than merely
showing a favorable eigenbasis: the selector may depend on the observed
query, while every outcome still has support at most two.

**Reasoned limit.** Neither statement alone yields a fresh-traffic theorem.
Equation (2) concerns one sketch. Cassette's present sufficient averaging
bound uses independent corrections and a separately declared sample count
(`MATHS.md:425-435`, `MATHS.md:458-464`). A lower bound on arbitrary
multi-call, history-dependent, page-constrained estimators does not follow
from (2). Conversely, an upper bound does not certify a physical read cost:
the present conversion from a column read to scalar or byte traffic is
explicitly still required (`MATHS.md:491-492`).

## Why q=4 alone remains too small

The fixed four-coordinate problem has no growing payload, transform, or
metadata scale. It therefore cannot establish a nonconstant byte or traffic
frontier. Cassette keeps description bytes, metadata bytes, fresh-sample
counts, and fresh traffic as distinct fields (`MATHS.md:727-767`), and it
requires a per-atom description, sampling law, operation bound, and physical
conversion record (`MATHS.md:774-782`). A Gram spectrum alone supplies none
of these.

In particular, optimizing over an abstract \(Q\) silently removes a cost
unless its representation and activation are declared. The current
finite-word transform account separates encoded payload \(pqB_P\), the
\(psB_P\) abstract selected-column movement, \(q^2\) transform workspace,
and arithmetic (`procedural_transform_decoder.md:265-307`). It also states
that its exact mean is toward the represented source and that source-class
membership and index selection are not supplied procedures
(`procedural_transform_decoder.md:379-405`). The q=4 complex counterexample
itself supplies neither a finite-word sampler nor a page bound
(`query_adaptive_complex_water_counterexample.md:218-222`).

The error field is also incomplete. Stored columns, a stored transform, and
arithmetic contribute deterministic bias and additional variance unless
their numerical bounds are declared (`encoded_column_rounding_bound.md:23-94`);
the laboratory asymptotic alone may lie below a fixed-precision error floor
(`encoded_column_rounding_bound.md:128-139`). Finally, no one-step result
supplies sequential composition or observation adequacy
(`MATHS.md:618-651`, `MATHS.md:702-725`).

## One bridge theorem that would be consequential

For a declared finite-word encoded-column description class, define

\[
 \mathcal V_{b,s}(A)=
 \inf_{\substack{B\in\mathcal C_b(A),\\
                  Q\in\mathcal Q_{b_{\rm meta}}}}
 \Psi_s\!\left(Q(A-B)^*(A-B)Q^*\right),
\tag{3}
\]

where \(\mathcal Q_{b_{\rm meta}}\) is a declared transform family whose
decoder, sampler, and encoded columns \((A-B)Q^*\) are all counted. The
estimator class remains exactly (1): it sees \(z=Qx\), reads at most \(s\)
declared encoded columns, and returns an exact-mean sum of those columns.

The consequential question is: **for a growing rational residual family
with \(R_{m,\eta}^*R_{m,\eta}=\operatorname{Diag}(I_m,\eta I_m)\), what
are matching upper and lower bounds for \(\mathcal V_{b,s}(R_{m,\eta})\)
as functions of \((m,s,\eta,b,b_{\rm meta})\), with an explicit
finite-word sampler and the abstract fresh-read count \(ps\)?**

This theorem would connect a real source family to the description-distortion
contract (`MATHS.md:437-489`) and could alter certified
\(\varepsilon_{\rm exec}\), \(s^{\max}\), and abstract
\(t_{\rm fresh}^{\max}\) together. It does not widen access assumptions:
every allowed output is still a sum of at most \(s\) encoded columns, and
every transform, law, and payload has an explicit account. A physical-page
claim would remain a later conversion obligation.

## Candid assessment

The q=4 lower-or-upper problem is a useful discriminator for the exact
adaptive-sampling model. By itself it changes neither Cassette's declared
description curve nor a certificate resource frontier. The growing
description-aware theorem in (3), rather than a resolution of one fixed
four-dimensional spectrum, is the missing mathematical bridge.
