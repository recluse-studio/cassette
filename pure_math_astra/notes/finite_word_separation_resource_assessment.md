# Resource assessment for the finite-word original-column separation

Status: bounded accounting assessment.  The cited lower and upper establish a
finite-word gap in original-column **read count** for one adversarial rounded
source.  They do not yet establish an end-to-end Cassette resource
improvement.

This note uses the resource fields in `MATHS.md`: resident description and
metadata bytes, fresh bytes, physical page conversion, and execution work are
separate quantities.  It does not combine bytes and arithmetic into one
number without a declared exchange rate.

## What is proved

Fix the equicorrelation parameters from
`rounded_original_column_equicorrelation_combined_independent_review.md`:

\[
 q=4m,\qquad C=1.9\eta,\qquad
 h\le\frac{\sqrt\eta}{10000\sqrt{pq}}.
 \tag{1}
\]

For the finite rounded family \(\mathcal W_h\), the adaptive construction
has exact coefficient mean, risk below \(C\), and a hard cap of \(2m\)
reads of stored, original columns.  The static finite-advice lower says that,
after any static architecture with at most \(N\) source states is fixed and
provided

\[
 p-4m>4{,}000{,}000
 \bigl(\ln N+6m\ln2+4m\ln201\bigr),
 \tag{2}
\]

there is a rounded source \(W\) on which a static protocol at the same risk
must have expected original-column count strictly greater than \(2.02m\).
Thus the established read-count margin at that source is

\[
 g:=\mathbb E|S_{\rm static}|-2m>0.02m.
 \tag{3}
\]

The hard source depends on the fixed static architecture.  Equation (3) is
not a source-uniform lower bound, and it says nothing about a static protocol
whose support law may change with the query.

For dyadic \(h\), each source entry has the exact signed-integer width

\[
 w_h=\left\lceil\log_2\left(2\left\lceil
 \frac{\sqrt{4+\eta}}h+\frac12\right\rceil+1\right)\right\rceil.
 \tag{4}
\]

Both protocols can store the same \(p\times4m\) rounded source, so the
common source payload is

\[
 B_{\rm source}=4mpw_h\quad\hbox{bits}.
 \tag{5}
\]

It cancels from a comparison that retains the same source.  The adaptive
fresh payload bound before physical layout is \(2mpw_h\) bits per query.

## A physical-page condition

Let \(P_{\rm col}\) be the actual transferred bytes for one original
column.  It must include the declared scalar packing, record header,
alignment, and page movement.  For example, a one-column independently
addressable page may have

\[
 P_{\rm col}=P_{\rm align}
 \left\lceil
 \frac{\lceil pw_h/8\rceil+P_{\rm header}}{P_{\rm align}}
 \right\rceil
 \tag{6}
\]

after choosing the repository's exact header and alignment convention.  The
formula is only an example; it is not a Cassette layout declaration.

Under the following additional layout condition, (3) becomes a byte gap:

each original column occupies a distinct independently fetched page of
\(P_{\rm col}\) bytes, and acquiring a support means acquiring those pages.
Then, at the hard source,

\[
 B^{\rm fresh}_{\rm static}-B^{\rm fresh}_{\rm adaptive}
 \ge gP_{\rm col}>0.02mP_{\rm col}
 \tag{7}
\]

in expected bytes per query.  The adaptive side has a hard upper bound
\(2mP_{\rm col}\).

This implication fails without the layout condition.  A page may bundle
several original columns; a page-cache hit may cost no new transfer; or a
physical plan may add address and group-read costs.  The mathematical support
count must therefore be converted through a declared page profile before it
can certify \(b_{\rm fresh}\).

## The costs that the proof does not price

The adaptive upper uses one shared, finite rational catalog for a
four-coordinate block.  Let

\[
 B_{\rm cat},\quad B_{\rm selector},\quad B_{\rm sampler},\quad
 b^{\rm op}_{\rm adaptive},\quad c^{\rm op}_{\rm adaptive}
 \tag{8}
\]

respectively denote its resident catalog bytes, selector bytes, exact-sampler
bytes, per-query metadata traffic bytes, and per-query arithmetic operations.
The catalog is shared across all \(m\) blocks, but selector and sampling work
normally scale with \(m\).  For a concrete catalog, that work has the form
\(c^{\rm op}_{\rm adaptive}=m(c_{\rm select}+c_{\rm sample})+
c_{\rm assemble}\); its value depends on the represented selector and
sampler, not just on finite-catalog existence.  These quantities have not
been constructed or bounded in the cited upper.

A concrete catalog with laws \(\ell=1,\ldots,K\), outcomes
\(r=1,\ldots,R_\ell\), and rational two-row \(4\times4\) outcome matrices
would admit the literal account

\[
 B_{\rm cat}=
 \sum_{\ell=1}^{K}\sum_{r=1}^{R_\ell}
 \bigl(B(L_{\ell r})+B(\Pr\{r\mid\ell\})+B({\rm support}_{\ell r})\bigr)
 +B({\rm law\ index}) .
 \tag{9}
\]

A two-row matrix has at most eight nonzero real coefficients, but their
numerator and denominator widths, the number of outcomes, and the selector's
risk-form data are all presently unknown.  A rational probability also does
not by itself bound random-bit use: an exact sampler needs a stated method,
for example a common denominator with rejection accounting.

The static theorem permits arbitrary Borel decoders.  It consequently gives
no upper or lower bound on a static decoder's resident byte size.  If a
source-selected state must remain available after the source is stored, its
label can be stored in \(\lceil\log_2N\rceil\) bits per source, plus an encoding of
the state decoder.  If the state is recomputed later by rereading the whole
source, that computation and read path must instead be charged.  The theorem
alone does not choose either implementation.

More specifically, for a static protocol to evade the lower through a
failure of the union-bound condition \(\beta<1\), its state count must obey

\[
 \log_2N\ge
 \frac{(p-q)\epsilon^2}{4\ln2}
 -\frac{3q}{2}-q\log_2(1+2/\delta).
 \tag{10}
\]

When the right side is positive, this is an information lower bound on a
persistently available state label.  It remains silent about the byte size of
the label's decoder program or table.

Finally, exactness in the upper's finite-word execution account is literal
for rational queries with declared exact rational arithmetic and an exact
sampler.  No native Cassette representation, query precision policy, output
workspace bound, or execution-time certificate is constructed.

## Parameterized break-even condition

Compare the two protocols at the lower theorem's hard source and over \(R\)
queries.  Let

\[
 \begin{aligned}
 B^{\rm res}_{\rm adaptive}&=B_{\rm cat}+B_{\rm selector}+B_{\rm sampler}
     +B_{\rm layout},\\
 B^{\rm res}_{\rm static}&=B_{\rm state}+B_{\rm static\ decoder}
 \end{aligned}
 \tag{11}
\]

be declared resident totals, and let \(b^{\rm op}_{\rm adaptive}\) and
\(b^{\rm op}_{\rm static}\) be per-query metadata traffic measured in bytes.
The source payload (5) cancels. Define a traffic scenario that loads the
declared resident material once and then performs \(R\) queries, with no
source-page caching between queries. With the one-column-page condition,
the adaptive protocol has a smaller total transferred byte count whenever

\[
 R\left[gP_{\rm col}
      -\bigl(b^{\rm op}_{\rm adaptive}-b^{\rm op}_{\rm static}\bigr)\right]
 >B^{\rm res}_{\rm adaptive}-B^{\rm res}_{\rm static}.
 \tag{12}
\]

A sufficient version using only the proved count margin replaces \(g\) by
\(0.02m\).  The bracket must be positive.  If it is positive and the
right-hand side is positive, the explicit break-even horizon is

\[
 R>
 \frac{B^{\rm res}_{\rm adaptive}-B^{\rm res}_{\rm static}}
 {0.02mP_{\rm col}-
  (b^{\rm op}_{\rm adaptive}-b^{\rm op}_{\rm static})}.
 \tag{13}
\]

Peak resident memory remains a separate comparison of (11); repeated
traffic savings cannot reduce it. Arithmetic also remains separate:

\[
 c^{\rm op}_{\rm adaptive}\le c^{\rm op}_{\rm budget}
 \tag{14}
\]

or a separately justified conversion from operations to the selected
Cassette cost.  It is invalid to use the fetched-byte saving in (12) to pay
for unmeasured selector arithmetic.

## Assessment boundary and deciding next step

**Proved existence.**  In the stated finite rounded-source, original-column
model, a query-adaptive finite rational catalog has a hard \(2m\)-column
upper, while a finite-advice static protocol has the architecture-dependent
hard-source lower (3).  With a one-column physical-page layout, this induces
the conditional fresh-byte gap (7).

**Not constructed.**  There is no serialized rational catalog, exact
sampler, selector, page profile, resident-byte total, or native Cassette
execution.  The lower's permissive static model also prevents a direct
resident-space lower bound for its competitor.

**Single deciding construction.**  Construct and serialize the shared
four-coordinate rational catalog at the stated \(1.895\eta\) ideal risk,
including its exact selector and sampler, then record \(B_{\rm cat}\),
\(B_{\rm selector}\), \(B_{\rm sampler}\), per-query metadata traffic, and
operation count under one declared original-column page layout.  Substitution
in (12), together with separate resident-memory and work checks, decides whether this separation pays for its own execution resources
for a chosen \((p,m,\eta,R)\).  Until that construction exists, the result is
a conditional page-byte opportunity, not an end-to-end resource improvement.
