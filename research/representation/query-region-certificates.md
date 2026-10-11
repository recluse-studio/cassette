# Exact query-region certificates for dense gated operations

**Status.** This note gives a narrow exact relevance construction for a
standard gated dense operation, then proves why it cannot extend to arbitrary
dense matrix products without a source certificate.  The construction uses
an exact gate-zero certificate to omit whole drive-resident payload blocks.
It returns every active block's original weights to the ordinary calculation.
It is a structured sparse-gating specialization, not a general solution or a
novelty claim.

## 1. Source family and ordinary operation

Fix \(N\) fixed-stride external payload records.  Record \(i\) contains an
arbitrary dense source-precision matrix \(E_i\in\mathbb D^{p\times n}\) of
\(R\) encoded bytes.  This first construction is restricted to finite,
nonexceptional rational or integer scalar values and an ordinary operation
whose gate branch uses the exact sign below before it evaluates a payload
term.  It does not cover NaNs, infinities, or a floating-point
implementation whose rounded gate sign has not been separately certified.
Record \(i\) also has a source gate header containing the
coefficient and bias of the affine gate

\[
 g_i(t)=it+\frac{\Delta-Di^2}{D}
       =\frac{iT+\Delta-Di^2}{D},
 \qquad t=\frac{T}{D},\quad 0\le i<N.
 \tag{1}
\]

Here \(D>0\) and \(\Delta\) are source-certified integers, while \(T\)
is the current signed query integer.  Thus the header contains the
source-fixed affine coefficient \(i\) and bias \((\Delta-Di^2)/D\);
\(t=T/D\) is an exact scalar already available from runtime state.  It can be
one coordinate or a declared exact projection of the input.  The full
ordinary gated dense calculation is

\[
 F(t,z)=\sum_{i=0}^{N-1}\operatorname{ReLU}(g_i(t))\,E_i z,
 \tag{2}
\]

where \(z\in\mathbb D^n\) is the current dense input.  The result in (2) is
not estimated: every included \(E_i\) is used by the usual exact or declared
finite-precision matrix-vector calculation.

The declared source-routing semantics are part of this family: compute
\(Q(i)\) by exact integer arithmetic, omit the term without evaluating
\(E_i z\) when \(Q(i)\le0\), and otherwise evaluate the positive-gate term
in the declared normal order.  This is a branch certificate for an actual
gated operation.  It is not an algebraic rewrite of an implementation that
first evaluates every payload matrix and later multiplies by a rounded zero.

At construction, the encoder scans all \(N\) source gate headers and checks
the source-fixed coefficient and bias in (1) with integer arithmetic.  It
retains the certificate

\[
 z_W=(D,\Delta,N,\text{scalar format},\text{record stride},
       \text{source identity}).
 \tag{3}
\]

The records themselves, including all matrices \(E_i\), remain external.
The gate relation is a certificate about actual source gate values, rather
than a query-supplied list of relevant experts.

## 2. Derived exact region

Put

\[
 Q(i)=-Di^2+Ti+\Delta.
 \tag{4}
\]

The exact active region is

\[
 S(t)=\{i\in\{0,\ldots,N-1\}:Q(i)>0\}.
 \tag{5}
\]

Completing the square gives

\[
 4D Q(i)=T^2+4D\Delta-(2Di-T)^2.
 \tag{6}
\]

Consequently \(S(t)\) is either empty or one contiguous interval of integer
identities.  Its two endpoints can be found with exact integer comparison
and two binary searches on the increasing and decreasing sides of the
concave quadratic.  This costs \(O(\log N)\) evaluations of (4), no source
read, and no floating-point root calculation.  A gate with \(Q(i)=0\) is
inactive by the declared ReLU convention.

The physical region identity follows from the fixed layout:

\[
 \operatorname{offset}(i)=\operatorname{base}+iR.
 \tag{7}
\]

Thus the complete exact interpreter is: derive \(S(t)=[\ell,h]\), fetch and
verify the \(h-\ell+1\) records in that interval, return their unmodified
matrices to the normal evaluation of (2), and omit every other payload
record.

**Theorem 1 — exact gate-zero relevance.**  For every checked source in this
family, the interpreter reads no inactive payload record and returns the
same value as (2).

**Proof.**  Equations (4)--(6) prove that the derived interval equals the
indices whose ReLU multiplier is strictly positive.  For every \(i\notin
S(t)\), \(\operatorname{ReLU}(g_i(t))=0\), so changing \(E_i\) cannot change
(2).  For every \(i\in S(t)\), the interpreter reads the source record and
performs its stated term in (2).  The retained and omitted sums therefore
equal the original sum exactly. \(\square\)

This is a relevance proof, not an output approximation: it establishes that
whole payload matrices are annihilated by an exact gate before their contents
are consulted.

## 3. Reads, RAM, and a necessary-block lower bound

Let \(m(t)=|S(t)|\).  The interpreter recovers

\[
 m(t)\ \text{logical payload records}\quad m(t)R\ \text{payload bytes}.
 \tag{8}
\]

The device may service these records through one coalesced interval request
or through \(m(t)\) record requests; that physical request count belongs in
the access transcript.  Construction reads and validates all \(N\) gate
headers once.  The interpreter uses
\(O(\log N+b_T+b_D+b_\Delta)\) bits beyond the declared query state to find
the endpoints, where the \(b\)'s are the signed integer widths.
Peak RAM includes that state, the resident certificate (3), one record
buffer or the exact accumulation schedule required by (2), every currently
needed active matrix, and the normal calculation's output and workspace.
Streaming one active matrix at a time can keep the payload portion to one
\(R\)-byte buffer plus the ordinary output accumulator, if that calculation
permits accumulation in the declared order.  A calculation that pins all
active matrices must charge all \(m(t)R\) bytes instead.

For this source family under exact product semantics, active matrices are
generically necessary.  Suppose \(z\) has a nonzero coordinate and
\(i\in S(t)\).  Altering one entry of \(E_i\) in the corresponding input
column changes at least one output coordinate of (2).  Therefore no method
correct for every arbitrary payload family \((E_i)\) may omit, without a
resident lossless copy or an external read, an active record.  Under the
required contract that normal arithmetic receives original matrices, this
gives the lower bound of \(m(t)\) source-record recoveries for the active
interval.

The same argument gives a broader obstruction.

**Theorem 2 — arbitrary dense-product block obstruction.**  Under exact
product semantics, partition an arbitrary \(W\in\mathbb D^{p\times n}\)
into column blocks \(W_B\).  If a query \(x\) has a nonzero coordinate in
block \(B\), then no source-independent exact relevance rule can certify
\(W_B\) unnecessary for \(Wx\) over the full arbitrary-matrix class.

**Proof.**  Hold every other block fixed and change one entry in the column
of \(W_B\) corresponding to a nonzero coordinate of \(x\).  The product
changes.  Thus two valid sources have the same query and all other records,
but disagree on the required result.  A rule that omits \(B\) for both is
wrong for one of them. \(\square\)

The theorem names the missing premise precisely: exact block omission for a
dense nonzero input requires a verified source relation, an exact query
annihilator, or a resident/external lossless representation of the omitted
block's contribution.  It cannot follow from a small generic router.

## 4. Source-derived annihilator certificate

The gate construction proves exact irrelevance through a source gate.  A
second, more algebraic path can prove it directly from the payload.  It is
useful only on a source family with an actual common right nullspace.

For this section, require the source values and the declared reference
product to be exact over a field \(\mathbb F\).  Fixed-point source values
may be embedded in the rationals.  Let \(G\) be a contiguous physical group
of whole dense matrices, each with the same \(n\) input coordinates, and
stack those matrices vertically into \(W_G\).  During construction, read
the source blocks in \(G\), compute the nonzero rows of the reduced
row-echelon form

\[
 A_G=\operatorname{nonzero\ rows}(\operatorname{RREF}(W_G)),
 \tag{9}
\]

and retain \(A_G\), its pivot convention, the physical endpoints of \(G\),
and the source identity.  The physical blocks remain external.  The
interpreter computes \(A_Gx\) exactly from the current input \(x\).  It
omits the whole group only when \(A_Gx=0\); otherwise it fetches the original
blocks in \(G\).  This certificate is derived from the actual source
matrices, rather than supplied as a label for a desired region.

**Theorem 3 — exact common-nullspace omission.**  The interpreter may omit
\(G\) exactly when \(A_Gx=0\).  In that case \(W_Gx=0\), so replacing the
group's contribution by zero gives the same ordinary dense product.

**Proof.**  The rows of \(A_G\) and \(W_G\) span the same subspace by (9).
Thus \(A_Gx=0\) if and only if every row of \(W_G\) has zero inner product
with \(x\), which is exactly \(W_Gx=0\).  The ordinary calculation therefore
receives no surrogate: an omitted group has a mathematically zero
contribution, while every non-omitted group is fetched at source precision
and passed to the usual calculation. \(\square\)

The test is a sufficient omission rule.  When \(A_Gx\ne0\), it does not try
to infer which individual block matters; it fetches the declared group.
For \(K\) arbitrary groups, their endpoints or membership need \(K\)-scale
metadata unless the layout itself derives them.  Fixed equal-size physical
ranges reduce location to arithmetic, but they do not make an arbitrary
group catalogue free.

Construction reads every payload block in \(G\) and performs the exact
row-reduction of its stacked matrix; it cannot discover this relation
without charging that source work.  The resident cost of one rank-\(r\)
certificate is its exact canonical row-space description, pivot locations,
group endpoints, and identity.
The interpretation work is \(O(rn)\) field operations and \(O(r)\) live
field elements if the dot products stream over \(x\).  If it omits the
group, it performs zero payload reads for that group.  Otherwise it reads
the complete range and supplies its source blocks to normal arithmetic.
Peak RAM includes the encoded \(A_G\), its live dot-product state, the
input representation, the output/accumulator, and the fetched block
schedule; the certificate does not hide the normal calculation workspace.

There is a sharp representation limit within the named class of exact
linear annihilator tests.  A test \(Bx=0\) recognizes the same omission
states as \(W_Gx=0\) for all \(x\) only if
\(\ker B=\ker W_G\), hence \(\operatorname{rank}B=r\).  For the information
bound, restrict to a finite subfamily with source values in
\(\mathbb F_q\).  Across its rank-\(r\) row spaces, the resident state must distinguish

\[
 {n\brack r}_q
 =\prod_{j=0}^{r-1}\frac{q^{n-j}-1}{q^{r-j}-1}
 \tag{10}
\]

possibilities.  It therefore needs at least
\(\lceil\log_2 {n\brack r}_q\rceil\) bits in the worst case, before location
metadata.  This follows by counting: two distinct row spaces have distinct
orthogonal kernels, so one resident certificate cannot represent both while
deciding all inputs exactly.  The lower bound applies to this linear-test
class, not to every conceivable external index.

This route has a real sparse-state family: matrices in \(G\) may all be
dense and nonzero while their rows lie in one \(r\)-dimensional source
subspace, and a current dense \(x\) may lie in its orthogonal complement.
Then the certificate omits dense, nonzero payload.  For a generic dense
group with full row space, however, \(r=n\), its common nullspace is zero,
and the condition holds only for \(x=0\).  The construction then saves
nothing.  It is standard row-space/nullspace algebra, not a new routing
method.

## 5. Stress cases

* **Dense active state.**  If \(\Delta\) is large enough that \(Q(i)>0\) for
  every \(i\), then \(m(t)=N\).  The construction reads every matrix and
  gains no external-byte advantage.

* **Broken header relation.**  A single gate header that violates (1) can
  create an omitted positive gate.  The construction scan must reject the
  source; fitting a parabola approximately is not a relevance certificate.

* **Boundary state.**  If \(T^2+4D\Delta=(2Di-T)^2\), the corresponding gate
  is exactly zero.  Replacing the strict comparison in (5) with a rounded
  root can change the selected region and hence the required source
  matrices.

* **Cancellation is irrelevant.**  Two active terms may cancel in the
  final output, but their matrices remain necessary under the arbitrary
  payload lower bound.  Output cancellation is not a certificate that their
  original weights can be omitted.

* **Finite floating-point evaluation.**  The nullspace theorem applies only
  when the declared ordinary product is exact over \(\mathbb F\), or when it
  rounds one exact product after the group contribution has been formed.
  A fixed-order floating-point dot product can round an algebraically zero
  \(W_Gx\) to a nonzero value.  Such an operation needs a stronger
  bit-level certificate or must retain the group.  The gate-zero theorem
  avoids this particular defect because its multiplier is established as
  the exact zero before the payload matrix is used.

* **Source-domain boundary.**  Equation (4) gives the branch used in this
  note only for the declared rational/integer source family.  It does not
  establish the sign of an arbitrary source floating-point gate after its
  native rounded operations.  Likewise, a NaN or infinity can defeat the
  usual zero-multiplier reasoning.  A general source needs a bit-level
  certificate of its own branch semantics before the gate theorem applies.

## 6. Collision audit

Exact zero-gating and sparse expert activation are established mechanisms.
Jacobs, Jordan, Nowlan, and Hinton's [adaptive mixture of local
experts](https://doi.org/10.1162/neco.1991.3.1.79) is a direct antecedent
for gated expert selection.  Shazeer et al.'s [sparsely-gated mixture of
experts](https://arxiv.org/abs/1701.06538) is the close modern model
collision.  The concave-quadratic interval calculation is elementary
algebra, and the physical contiguous-layout consequence is standard
indexing.

The retained result is only a complete exact certificate path for two
narrow families: construction checks actual gates or derives a common
nullspace from actual matrices; runtime derives an interval or tests that
nullspace; locations are computed without a directory for fixed ranges;
and required source matrices are returned unchanged.  It is classical
rank/nullspace and exact-gating work, not useful new joint
representation/interpretation mathematics by itself.

A stronger candidate would need a verified relation that annihilates a
substantial collection of blocks for realistic dense states while retaining
the lower-bound honesty of Theorem 2.  It must then beat an exact sparse or
gated baseline under the same source layout, active-region size, and
normal-calculation workspace.
