# Finite-state geometry, an aligned-page separation, and the remaining comparator

**Status.** This note proves a finite, original-column, static-versus-query-adaptive
separation after charging a simple record layout.  It is a sharper resource
corollary of the existing finite-advice and two-rule-sampler work, not a new
geometric representation theorem.  In particular, it does not beat the best
known query-adaptive sparsification class, establish a general encoded-page
frontier, or establish novelty.

The useful point is exact and limited.  A finite resident description can
contain a dense rank-k reconstruction, a residual-norm table, an optimal
static sampling law, and a fixed coordinate transform.  Once every
source-dependent item is a b-bit state of a fixed interpreter, that entire
static family falls inside the finite-state lower bound.  On a finite rounded
source, the explicit query-dependent two-rule sampler then has a hard 2m
original-record cap, while every such static state that meets the same error
threshold has an expected read count greater than 2.1063m.  Uniform
4096-byte alignment turns the count statement into a fresh-byte and page
statement.  It does not turn it into a result for arbitrary encoded pages.

## 1. Declared finite model

Fix an integer m, set q=4m, and put

\[
 \eta=\frac1{256},\qquad
 H_\eta=\mathbf1\mathbf1^T+\eta I_4,\qquad
 G=H_\eta^{\oplus m},\qquad
 C=\frac{27}{16}\eta.
 \tag{1}
\]

The source family is the entrywise h-rounded orbit

\[
 \mathcal W_h=\{\operatorname{round}_h(A): A\in\mathbb R^{p\times q},\ A^TA=G\}.
 \tag{2}
\]

Rounding has a fixed tie rule and

\[
 r_0:=\frac h2\sqrt{pq}\le\frac{\sqrt\eta}{100000}.
 \tag{3}
\]

It is enough to choose a dyadic h=2^{-L} with

\[
 2^L\ge800000\sqrt{pq}.
 \tag{4}
\]

The source is therefore finite-word.  Since every entry of an unrounded
source has absolute value at most \(\sqrt{1+\eta}<2\), every rounded entry
has a signed fixed-width representation with at most \(w=L+3\) payload
bits.  This deliberately crude bound is enough for an aligned-record
calculation; it is not a compact source code.

One column occupies one independently addressable record:

\[
 P_{\rm col}=4096\left\lceil
 \frac{\lceil pw/8\rceil+64}{4096}
 \right\rceil\quad\text{bytes}.
 \tag{5}
\]

The record contains its fixed-width column payload and a 64-byte header.  A
fresh column read fetches its complete record.  Thus one column is exactly
\(P_{\rm col}/4096\) aligned physical pages in this declared layout.  No
claim is made for a packed, transformed, deduplicated, or cache-warm layout.

The compared static interpreter has at most \(2^b\) source-dependent
resident states.  A state may contain any finite encoded dense matrix B,
including a quantized rank-k factorization, a residual address map,
probabilities, a fixed right orthogonal transform, and arbitrary other
metadata.  After the state is selected, its distribution on original-column
supports is fixed before the query.  A branch may use the full query, its
state, and the selected original columns, and may be any Borel map.  It must
be unbiased for Wx and have mean-square error at most C for every W in (2)
and every unit query.  It may not read a transformed replacement column or
obtain information about an unselected original column.

This class contains the usual resident dense-description route

\[
 Wx=Bx+(W-B)x,
 \tag{6}
\]

with any fixed residual estimator, including the optimal law available
inside that static description.  It is larger than weighted SVD plus
independent importance sampling: B need not have a rank bound, the support
law need not factor by coordinate, and the branch output need not be linear.

The restriction that matters is static support conditional on the selected
source state.  A source-dependent program, transform table, cache, or
selector that is not encoded in those b bits is not a member of the class.
Neither is a support law selected after the query is observed.

## 2. The lifted finite-state theorem

Set

\[
 \epsilon=\frac1{1000},\qquad \delta=\frac1{100}.
 \tag{7}
\]

Suppose p satisfies

\[
 p-4m>
 4\cdot10^6\bigl(b\log2+6m\log2+4m\log201\bigr).
 \tag{8}
\]

The logs are natural.  Then, after the complete static interpreter has been
fixed, there is a source W in \(\mathcal W_h\) for which every declared
static state meeting the error cap C has expected original-record count

\[
 \mathbb E[\#\text{ fresh records}]>
 \frac{185979890388216457539}{88296890911329512500}m
 >2.1063m.
 \tag{9}
\]

### Proof

The rounded finite-advice trace theorem applies with \(N\le2^b\).  Its
failure probability is below one under (8), because q=4m and

\[
 2^{3q/2}(1+2/\delta)^q=2^{6m}201^{4m}.
 \tag{10}
\]

For (1), the trace term per four-column block is

\[
 \begin{aligned}
 f_{H_\eta}(C)
 &=\frac{4+\eta}{4+\eta+C}+\frac{3\eta}{\eta+C}\\
 &=\frac{16400}{16427}+\frac{48}{43}
 =\frac{1493696}{706361}.
 \end{aligned}
 \tag{11}
\]

The rounding factor in that theorem obeys

\[
 \zeta=\frac{r_0}{\sqrt{C+\lambda_{\min}(G)}}
 \le\frac1{100000},
 \quad
 a=1-\frac{\delta^2}{2}=\frac{19999}{20000},
 \quad
 \alpha\ge\alpha_0:=\frac{a}{1+1/100000}
 =\frac{99995}{100001}.
 \tag{12}
\]

Also

\[
 \epsilon'=\epsilon+\frac{\zeta}{1+\zeta}
 <\frac{101}{100000}.
 \tag{13}
\]

The trace lower bound gives, per block,

\[
 \frac{\mathbb E[\#\text{ records}]}m
 \ge \alpha^2 f_{H_\eta}(C)-8\alpha\epsilon'
 >\alpha_0^2\frac{1493696}{706361}-8\frac{101}{100000}.
 \tag{14}
\]

The final rational expression is the first fraction in (9), and subtracting
\(21/10\) leaves

\[
 \frac{556419474424481289}{88296890911329512500}>0.
 \tag{15}
\]

The source W is selected only after the finite static architecture is fixed.
That order is essential: (9) is a finite-state minimax statement, not one
universal source that defeats every possible interpreter. \(\square\)

The proof is a lifting, not a new lower-bound mechanism.  A b-bit dense
description has at most \(2^b\) decoded possibilities under a fixed
interpreter, so it enters the finite union before the orbit source is chosen.
The conditional-projection proof already allows nonlinear branch output and
free static transform data.  The finite state is the only information
boundary it needs.

## 3. Query-dependent upper route and physical account

Use the real four-coordinate uniform-pair/positive-negative transport
sampler blockwise.  For every block query x it returns Y with

\[
 \mathbb E[Y\mid x]=x,\qquad
 \|Y\|_0\le2,\qquad
 \mathbf1^TY=\mathbf1^Tx\quad\text{in every outcome},
 \tag{16}
\]

and

\[
 \mathbb E\|Y-x\|_2^2\le\frac53\|x\|_2^2.
 \tag{17}
\]

Concatenating the m block outputs gives a hard cap of at most 2m distinct
original columns.  The sum rule kills the rank-one term of each H_eta.  If W=A+E,
then \(\|E\|_{\rm op}\le r_0\), so

\[
 \mathbb E\|W(Y-x)\|_2^2
 \le\frac53(\sqrt\eta+r_0)^2\|x\|_2^2
 \le\frac{10000200001}{6000000000}\eta\|x\|_2^2
 <\frac{27}{16}\eta\|x\|_2^2.
 \tag{18}
\]

Thus the candidate and the lower class use the same source W, query norm,
precision model, error threshold, and original-column layout.  In a cold
request, the candidate reads at most

\[
 2mP_{\rm col}\ \text{bytes}
 \quad\text{and}\quad
 2m\frac{P_{\rm col}}{4096}\ \text{aligned pages}.
 \tag{19}
\]

Every matching static method in the stated class reads, in expectation,
more than

\[
 2.1063mP_{\rm col}\ \text{bytes}
 \quad\text{and}\quad
 2.1063m\frac{P_{\rm col}}{4096}\ \text{aligned pages}.
 \tag{20}
\]

The strict expected saving exceeds \(0.1063mP_{\rm col}\) bytes per cold
request.  It comes from a hard-versus-expected read comparison; it is not a
tail-latency bound for the candidate.

For a rational block query \(x_i=a_i/2^d\), the candidate's published
integer implementation uses a constant number of additions, squares,
comparisons, and scans per block.  Its selected coefficient numerators need
at most d+3 signed bits.  Uniform-pair selection consumes four fair bits in
expectation.  The transport branch uses at most \(4(d+1)\) fair bits in
expectation.  Across m blocks the expected fair-bit demand is at most
\(4m(d+1)\).  Rejection sampling makes that random-bit demand unbounded in
the worst case.  This is an unresolved request-latency condition, not an
implementation detail to hide.

The candidate has no source-trained dense reconstruction.  Its
source-dependent persistent state is only the regular-layout information,
the source identity, and the finite-word scale: \(O(\log p+\log m+\log L)\)
bits plus fixed format tags.  Let \(b_{\rm adaptive}\) be the actual bit
string for those fields under a declared self-delimiting encoding.  The
common-upper-budget comparison applies only when \(b\ge b_{\rm adaptive}\);
then the static method receives the same b-bit allowance even though the
candidate does not spend all of it.  This note does not calculate a concrete
\(b_{\rm adaptive}\), so its equal-budget statement is parametric rather
than a device-RAM measurement.  Candidate peak working memory still includes a query buffer,
one column-record buffer, and a p-entry output accumulator.  The theorem
does not prove a RAM advantage, because the same output and record buffers
are available to the comparator and no native allocator has been measured.

## 4. Exact four-coordinate comparator

The previous two-rule sampler is not the fully optimized query-adaptive
comparator.  The exact all-real, signed-sum, hard-two-sparse value is now
proved in [four-coordinate-optimality.md](four-coordinate-optimality.md):

\[
 \sup_{x\ne0}rac{\Phi(x)}{\|x\|_2^2}=\sqrt{13}-2
 pprox1.60555127546.
 	ag{21}
\]

Its finite six-pair decoder uses at most two original columns per outcome.
For the unrounded Gram in (1), it improves (17) to

\[
 \mathbb E\|A(Y-x)\|_2^2
 \le\eta(\sqrt{13}-2)\|x\|_2^2.
 	ag{22}
\]

This is a stronger established query-time baseline.  It changes neither the
finite-state lower-bound class nor its aligned-record comparison, and it
proves no resident representation, encoded-page, RAM, or novelty advantage.

A finite three-bit signed-block description applies that decoder to arbitrary
four-column dyadic sources in
[signed-block-construction.md](signed-block-construction.md).  It stores one
sign code and a checked spectral certificate, reads at most two original
records, and improves the prior local two-rule bound under that same
description.  Its countercases and comparator boundary are stated there.

## 5. Literature collision and what remains open

The mechanism is close to established work in three directions.

* Wang et al., [ATOMO: Communication-efficient Learning via Atomic
  Sparsification](https://proceedings.neurips.cc/paper_files/paper/2018/file/33b3214d792caf311e1f00fd22b392c5-Paper.pdf), optimize unbiased atomic
  sparsification for a chosen atomic representation.  Their abstract
  explicitly includes coordinate, singular-value, and Fourier atoms.  A
  claim that the present use of a changed basis or a sparse unbiased query
  is new would collide with that framework.
* Barnes et al., [Efficient Unbiased
  Sparsification](https://arxiv.org/html/2402.14925), characterize efficient
  hard-support unbiased sparsifications for their stated divergence classes.
  Their positive-vector and nonnegative-output hypotheses do not retain the
  signed affine invariant \(\mathbf1^TY=\mathbf1^Tx\) for mixed-sign
  queries, but they rule out treating fixed-cardinality sampling or
  conditional Jensen as new.
* Chiu and Demanet, [Sublinear Randomized Algorithms for Skeleton
  Decompositions](https://doi.org/10.1137/110852310), study sampled
  column/row skeleton decompositions.  This makes any attempt to recast a
  source-column basis plus interpolation coefficients as a new
  representation method untenable without a substantially different
  theorem and resource account.

The finite-state theorem above is also anticipated inside this repository by
the finite-word growing static/adaptive separation and the rounded
original-column finite-advice trace lower.  The new page arithmetic merely
makes their common source and aligned-record consequence explicit.  It is
not evidence of generic novelty.

The actual open gap has three parts.

1. **Best adaptive comparator.** Solve or tightly bound the all-real,
   four-coordinate, signed-sum, hard-two-sparse minimax programme.  The
   symmetric calculation in (24) shows that the current two-rule selector
   is not that solution.
2. **Encoded pages.** Extend a lower bound past original-column visibility.
   A coded page can reveal a combination of columns that the present trace
   argument forbids.  The codeword, decoder, transform accuracy, page
   payload, and query workspace must all be charged before this becomes an
   equal-resource comparison.
3. **Product relevance.** Convert a local matrix calculation into a Q19
   certificate with declared conditions, observation support, composition,
   page residency, finite arithmetic, and measured scheduling.  No result
   in this note does that.

The retained result is therefore a stress-tested restricted theorem and a
specific obstruction to overclaiming it.  The requested general
representation-and-interpretation advantage remains open.
