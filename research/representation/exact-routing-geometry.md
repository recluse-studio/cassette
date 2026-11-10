# Algebraic exact routing to a drive-resident weight region

**Status.** This note proves one bounded construction.  A finite-field
polynomial derives the needed region from a query and a charged resident
state, resolves a physical record without a region-address table, and returns
the record's exact source weights to an ordinary calculation.  Its routing
state is information-theoretically minimal for its declared family.  The
construction is a specialized parametric direct-address scheme, not a claim
of a new general index or a solution for arbitrary weight tables.

## 1. A source family with derived regions

Fix a finite field \(K=\mathbb F_{2^r}\), represented in one fixed public
polynomial basis, and choose \(0\le d<|K|\).  The irreducible basis
polynomial, field encoding, record stride, source scalar format, and ordinary
calculation are fixed, source-independent rules.

A source is

\[
 W=(\theta,(V_y)_{y\in K}),\qquad
 \theta=(\theta_0,\ldots,\theta_d)\in K^{d+1},
 \tag{1}
\]

where each \(V_y\) is an arbitrary source-precision weight region of exactly
\(L\) payload bits.  The regions contain the actual weights; no relation
between their values is assumed.  The source stores the records in canonical
field-label order.  With a fixed \(h\)-bit record header and 4096-byte
alignment, one record occupies

\[
 P=4096\left\lceil\frac{\lceil L/8\rceil+h/8}{4096}\right\rceil
 \quad\hbox{bytes}.
 \tag{2}
\]

For query \(x\in K\), define the algebraically derived label

\[
 y=p_\theta(x)=\sum_{j=0}^d\theta_jx^j,
 \tag{3}
\]

and the required logical region

\[
 S_\theta(x)=\{y\}.
 \tag{4}
\]

The declared ordinary calculation is any fixed operation
\(\mathcal N(V_y,x)\) that consumes the source-format region \(V_y\): for
example, the usual multiplication of a weight tile represented by \(V_y\)
with the supplied query state.  Its reference result is

\[
 F(W,x)=\mathcal N(V_{p_\theta(x)},x).
 \tag{5}
\]

This family is deliberately narrow.  The relevant region is not supplied as
a query field or a stored query-to-address table.  It is derived by
evaluation of a source-dependent algebraic relation, while the source
weights remain arbitrary and drive-resident.

## 2. Construction and exact path

The resident abstraction is the coefficient vector

\[
 z_W=\theta,
 \qquad |z_W|=(d+1)r\ \hbox{bits},
 \tag{6}
\]

together with fixed format tags, source identity, base offset, and the
public field rule.  These latter fields have declared fixed widths
\(b_{\rm fmt}\); they are not hidden in the interpreter.

The interpreter uses Horner evaluation,

\[
 a\leftarrow\theta_d;\qquad a\leftarrow ax+\theta_j
 \quad(j=d-1,\ldots,0),
 \tag{7}
\]

then takes \(y=a\).  The canonical \(r\)-bit field encoding of \(y\) is also
its ordinal in the physical order.  It therefore resolves the exact record
without a source-dependent directory:

\[
 \operatorname{offset}(y)=\operatorname{base}+P\operatorname{ord}(y).
 \tag{8}
\]

The one fetched record must contain its canonical label, fixed length, and
source digest in the header.  The interpreter verifies all three, emits its
payload byte-for-byte as \(\widehat V_y\), and supplies
\(\widehat V_y\) to \(\mathcal N\).

**Theorem 1 — exact derived routing.**  For every source (1) and query
\(x\in K\), this interpreter performs zero discovery reads, one fresh
\(P\)-byte record read, and returns

\[
 \widehat V_{p_\theta(x)}=V_{p_\theta(x)}
 \tag{9}
\]

at source precision.  Hence its ordinary result equals \(F(W,x)\).

**Proof.**  Horner's identity proves that (7) equals (3).  Canonical order
and fixed stride make (8) the physical location of that label.  The record
header check rejects any different label, length, or payload.  Passing the
check makes the payload identical to the source record \(V_y\), rather than
an estimate of a product involving it.  Substitution into the defining
ordinary operation (5) proves the final claim. \(\square\)

The relevance relation is checkable and sufficient:

\[
 \mathcal R_W(x,S)
 \quad\Longleftrightarrow\quad S=\{p_\theta(x)\}.
 \tag{10}
\]

If \(W'\) agrees with \(W\) on \(S\), then \(F(W',x)=F(W,x)\).  This proves
sufficiency without assuming that a small region is known in advance.

## 3. State lower bound and resource account

The coefficient state is optimal for exact no-discovery routing over this
family.

**Theorem 2 — routing-state lower bound.**  Let a deterministic
source-independent interpreter receive \(x\in K\), make no external read
before naming \(S_\theta(x)\), and be correct for every
\(\theta\in K^{d+1}\).  Its source-dependent resident state has at least

\[
 (d+1)r\quad\hbox{bits}.
 \tag{11}
\]

**Proof.**  Since \(d<|K|\), different polynomials of degree at most \(d\)
are different functions \(K\to K\).  There are therefore
\(|K|^{d+1}=2^{(d+1)r}\) distinct relevance maps.  Two sources assigned the
same resident bit string induce the same deterministic map, so a correct
interpreter needs at least that many distinct states. \(\square\)

A flat resident table of all labels needs \(|K|r\) bits even before physical
offsets are recorded.  When \(d+1\ll|K|\), (6) is exponentially smaller than
that table, and Theorem 2 says that no smaller no-discovery state supports
the whole polynomial family.

The total peak-RAM claim remains more modest.  Let \(M_{\mathcal N}\) be the
declared additional peak workspace of the ordinary calculation after its
exact region is available.  In a polynomial-basis implementation, field
multiplication needs at most a \(2r-1\)-bit unreduced product.  The routing
phase therefore fits in

\[
 (d+1)r+b_{\rm fmt}+5r
 \tag{12}
\]

bits: coefficients, query, accumulator/address word, and multiplication
scratch.  During exact reconstruction and ordinary calculation, the bound is

\[
 (d+1)r+b_{\rm fmt}+r+8P+M_{\mathcal N}\quad\hbox{bits}.
 \tag{13}
\]

The \(8P\) term is the fetched aligned record buffer; if the ordinary
calculation retains a separate decoded copy, that copy belongs in
\(M_{\mathcal N}\).  Thus the declared peak is the maximum of (12) and
(13), not merely the \((d+1)r\)-bit coefficient payload.  Interpretation
uses \(d\) field multiplications and additions, or \(O(dr^2)\) elementary
bit operations with schoolbook polynomial-basis multiplication.  Source
construction reads and writes the \(|K|\) records, or \(|K|P\) bytes, plus
the \((d+1)r\)-bit coefficient manifest; it does not obtain the routing
relation for free.

## 4. Attacks on the construction

The theorem is exact because of its promise.  Removing the promise removes
the compression.

* **Arbitrary routing map.**  Replace \(p_\theta\) by an unrestricted
  function \(f:K\to K\).  There are \(|K|^{|K|}\) maps, so the same
  no-discovery counting argument requires \(|K|r\) resident bits.  A one
  record relevant region does not imply a small resolver.

* **Variable physical layout.**  Keep (3), but permute records by an
  arbitrary source-dependent permutation \(\pi\).  Address resolution now
  needs \(\pi(y)\).  Without a resident permutation table, the interpreter
  must read a directory or search the source; those are discovery reads and
  temporary state, not a free consequence of the polynomial label.

* **Surrogate output.**  Replacing the record read by a predicted tile
  product can preserve a numerical tolerance while failing (9).  It cannot
  be supplied to a normal calculation whose contract requires the
  source-format weights \(V_y\).

* **Polynomial collision language.**  Different queries may intentionally
  share a label and hence a region.  This is not a hash collision to be
  tolerated probabilistically: the source family defines those queries as
  requiring the same exact region.  If a workload instead requires distinct
  regions for them, (3) is the wrong relevance relation.

## 5. Literature collision and the remaining gap

The closest established mechanisms are hashing and static dictionaries.
Carter and Wegman's [universal hash classes](https://doi.org/10.1016/0022-0000(79)90044-8)
include rapidly evaluated finite-field polynomial families, but their
guarantee is randomized collision control for storage and retrieval.  The
present construction uses one stored polynomial deterministically and treats
its output as the exact semantic region label.  Fredman, Komlós, and
Szemerédi's [static sparse-table construction](https://doi.org/10.1145/828.1884)
gives constant-time access with a stored dictionary structure.  Here
canonical dense field order removes the directory only because every label
has a fixed-stride record.

These differences do not make the construction novel in the ordinary data
structure sense.  It is best described as an exact parametric direct-address
layout with an optimal description length for a polynomial routing family.
Its contribution to the corrected research is narrower: it proves all four
stages—derived relevance, physical location, exact reconstitution, and
peak-RAM accounting—without replacing returned weights by an approximate
\(Ax\).

The open problem is whether a real model's required-region relation has
enough verified algebraic structure to enter a comparably small family, while
its exact physical layout remains locally invertible.  This note supplies no
such model-wide relation and no advantage over the strongest applicable
index for an arbitrary source.

## 6. Implicit normal cells from an actual source score table

The polynomial-label family above still defines relevance by a routing
function.  The following different family derives relevance from the source's
own comparison calculation.

Let the \(i\)-th external record, \(0\le i<N\), contain an arbitrary
source-precision payload \(V_i\) and a two-coordinate dyadic score vector
\(a_i\in\mathbb D^2\).  A runtime state supplies a two-coordinate dyadic
gate query \(x\in\mathbb D^2\).  The declared gate is the ordinary exact
comparison

\[
 i_*(x)=\min\operatorname*{argmax}_{0\le i<N}\langle a_i,x\rangle.
 \tag{14}
\]

The minimum fixes ties in original record order.  The next normal calculation
receives the unchanged source payload \(V_{i_*(x)}\).

Consider the source class satisfying the checked affine-parabola identity

\[
 a_i=a_0+i u+i^2v
 \qquad(0\le i<N),
 \tag{15}
\]

for source-dependent dyadic vectors \(u,v\in\mathbb D^2\).  The payloads
\(V_i\) remain unrestricted.  Equation (15) is a geometric promise about
the *actual score vectors* stored in the source records, not a definition of
a preferred record label.

The resident routing representation keeps only

\[
 z_W=(u,v,N,\text{dyadic formats},\text{source identity}),
 \tag{16}
\]

with exact self-delimiting bit length \(b_{\rm par}\).  The common offset
\(a_0\) does not affect (14), so it is not resident routing state.  At
construction, the encoder reads all \(N\) score headers and, when \(N\ge3\),
sets
\[
 v=(a_2-2a_1+a_0)/2,\qquad u=a_1-a_0-v,
\]
then verifies (15) for every remaining header using exact dyadic arithmetic.  Cases \(N=1,2\) store the necessary first difference directly.
The verification transcript and source identity bind the resident state to
the checked source; no unverified assertion of (15) is used at runtime.

For \(N\ge3\), put

\[
 \alpha=\langle u,x\rangle,\qquad\beta=\langle v,x\rangle.
 \tag{17}
\]

The source score difference from the first record is

\[
 \langle a_i,x\rangle-\langle a_0,x\rangle=\alpha i+\beta i^2.
 \tag{18}
\]

Thus the normal-cell interpreter computes the winner without reading score
headers:

\[
 \begin{cases}
 \beta>0 &: \text{compare }0\text{ and }N-1;\\
 \beta=0 &: \text{choose }N-1\text{ if }\alpha>0,\text{ otherwise }0;\\
 \beta<0 &: \text{compare the clamped integer neighbours of }
              -\alpha/(2\beta).
 \end{cases}
 \tag{19}
\]

All comparisons use integer cross-products after clearing the declared
dyadic denominators.  In the last line, equality of the two neighbour scores
selects the smaller index.  The output index resolves physical location by
the fixed-stride formula

\[
 \operatorname{offset}(i)=\operatorname{base}+iP.
 \tag{20}
\]

**Theorem 3 — exact implicit normal-cell routing.**  On every checked source
satisfying (15), rule (19) returns exactly the tie-broken maximizer (14).
It performs zero discovery reads, one \(P\)-byte payload-record read, and
returns the source-format \(V_{i_*(x)}\) unchanged to the normal
calculation.

**Proof.**  Equation (18) reduces the actual source score comparison to a
quadratic on the finite integer interval \([0,N-1]\).  A convex quadratic
has its maximum at an endpoint, a nonconstant affine function at one
endpoint, and a concave quadratic at the one or two integers nearest its
continuous vertex.  These are precisely the cases in (19), including the
declared tie rule.  Fixed stride proves (20); record label, length, and
digest checks then reconstitute the named payload exactly. \(\square\)

Geometrically, the vectors \(a_i\) form an affine image of the discrete
parabola.  Their normal-cell arrangement has \(N\) possible winning records,
yet its boundaries are reconstructed from the two vectors \(u,v\) and the
range endpoint \(N-1\).  The construction therefore replaces an explicit
\(N\times2\) score table in RAM by \(b_{\rm par}=O(w+\log N)\) exact bits
when the dyadic parameter width is \(w\).  It does not replace the external
payload table, whose records are still individually retrieved at source
precision.

The runtime routing workspace consists of \(x,\alpha,\beta\), a constant
number of integer products, two candidate indices, and the fixed arithmetic
format.  Its bit length is \(O(w+b_x+\log N)\), where \(b_x\) is the query
width.  The total peak must still include (16), this workspace, the
\(8P\)-bit record buffer, and the declared normal-calculation workspace.
Construction scans \(N\) score headers, requires constant-many score-vector
words beyond the input/output stream, and records \(N\) header reads.  It
does not claim a smaller total RAM when the fetched payload or normal
calculation dominates.

Two attacks mark the boundary.

* A single off-parabola perturbation of \(a_k\) can create or erase a normal
  cell for record \(k\).  The construction must reject that source at its
  exact header check; storing only \(u,v\) after an approximate fit would
  fetch a wrong exact region.
* An arbitrary convex \(N\)-gon has \(N\) independently movable normal
  boundaries.  The two-vector representation cannot encode those
  perturbations.  A compact support-function description here depends on
  the certified affine-parabola relation, not merely on the fact that a
  maximizer exists.

This is an implicit support-function representation, not a generic compact
index.  Its closest established setting is exact linear optimization over a
convex hull and normal-fan point location.  The subsequent literature check
must test whether the affine-parabola specialization contributes anything
beyond that standard geometry.


## 7. Collision audit

This construction falls within established convex-geometric query methods.
The gate (14) is exact maximum-inner-product search over a finite point set,
equivalently evaluation of its support function and location in its normal
fan.  Dobkin and Kirkpatrick's
[preprocessed-polyhedra work](https://www.cs.princeton.edu/research/techreps/781)
explicitly uses hierarchical convex representations to answer separation
queries; generic normal-fan point location is therefore not a new routing
mechanism.  Ram and Gray's [maximum-inner-product search
formulation](https://arxiv.org/abs/1202.6101) is also a direct collision at
the score-maximization layer, although it studies general tree-based search
rather than this exact parametric family.

The affine-parabola formula replaces a generic \(N\)-boundary normal fan by
its two generating directions and a range endpoint.  That is an elementary
closed-form support-function specialization.  It does not support a
standalone novelty claim.  Its retained value is narrower and contractual:
the score relation is certified from actual source headers; ties use exact
dyadic arithmetic; physical address resolution has no directory; and the
unchanged winning payload is fetched for normal arithmetic.

A genuine advance would need a verified score geometry arising in a
nontrivial full weight table, a state smaller than the strongest applicable
exact support-function or indexing representation under the same record
layout, and a proof that construction verification, address metadata, exact
payload reconstruction, and peak RAM remain within the claimed budget.
