# finite_word_growing_static_adaptive_significance_assessment.md — current-evidence adversarial assessment of the finite-word growing static/adaptive separation; depends on ../../MATHS.md, finite_word_growing_static_adaptive_separation.md, rademacher_source_growing_static_adaptive_extension.md, query_adaptive_equicorrelation_boundary_rank_review.md, finite_word_growing_static_adaptive_separation_review.md, ../research/growing_static_adaptive_separation_prior_work.md.

## Revised verdict

The theorem is mathematically supported inside its declared column-linear
execution model. It proves a growing execution-layer separation: a fixed
finite query-selected catalog uses \(2m\) fresh columns, while every
pre-query resident reconstruction followed by one common unbiased
row-sparse operator needs more than \((2+1/50)m\) fresh columns at the
same worst-query quadratic error.

This is more than a repeated \(q=4\) calculation. The codebook construction
simultaneously handles every resident state of one fixed \(b\)-bit
interpreter, even when the encoder chooses a state after inspecting the
source. The Rademacher extension further gives a dyadic source with
\(p=O(m+b)\), so the lift does not require a quadratic output dimension.

The result does not yet pass the full Cassette research goal. Its originality
is unresolved, and its application consequence is limited to a restrictive
source/access and comparator model.

## 1. Correctness

### Current supported chain

1. The rank-two boundary inequality \(\sup C(q)<1.89\) was independently
   reconstructed in query_adaptive_equicorrelation_boundary_rank_review.md.
   The finite-\(\eta\) complex counterexample has two independent reviews.
   Together they give the strict \(q=4\) adaptive upper bound needed for
   the \(1.9\eta\) margin.

2. The finite-catalog bridge converts that per-query law into one finite
   rational catalog of individually operator-unbiased two-row laws. Reusing
   that catalog on \(m\) diagonal blocks gives exact mean, support at most
   \(2m\), and the stated blockwise worst-query bound. The assembly is
   independently checked in finite_word_growing_static_adaptive_separation_review.md.

3. The finite-state lower construction is valid in its stated quantifier
   order: fixing a source-independent \(b\)-bit interpreter leaves at most
   \(2^b\) decoded matrices. A net/union bound selects a source whose column
   factor avoids all their real column spans. The water-level argument then
   lower-bounds an arbitrary global common support law; it does not
   accidentally impose two reads per block.

4. The independent Rademacher construction replaces the Hadamard isometry.
   Its Hoeffding span-avoidance estimate and Bernstein/net near-isometry
   estimate give \(p=O(m+b)\) at the displayed constants. It preserves the
   strict support gap after the Gram comparisons.

### Exact scope, not a correctness defect

The theorem is a family for each fixed \((m,b,\text{interpreter})\); its
source is then chosen adversarially. It permits only source-dependent
information represented in the interpreter word. It compares selected-column
span estimators and excludes free source-dependent decoder state, nonlinear
resident reconstruction, query-selected reconstruction, and output maps
outside the selected-column span.

The shared finite catalog has no explicit numerical bit length, selector
cost, random-bit budget, or workspace bound. That limits a resource
instantiation; it does not invalidate the finite-word existence theorem.

**Correctness status: supported inside the declared model.** This is not a
claim about broader decoders, physical paging, or every Cassette execution
class.

## 2. Originality

| Step | Current provenance assessment |
|---|---|
| Conditional means and fixed-input unbiased sparsification | Established. |
| Fixed-query principal-inverse optimization | Classical multiresponse \(c\)-optimal design. |
| Finite catalog from a compact query family | Standard compactness plus rational perturbation. |
| Direct sum of \(q=4\) blocks | Routine tensorization. |
| Finite interpreter range, nets, and a source-avoidance union bound | Standard finite-class/packing technique. |
| Rademacher/Bernstein \(p=O(m+b)\) lift | A strong use of standard probabilistic tools; no novelty finding. |
| Rank-two boundary inequality yielding the \(1.9\eta\) law | Potentially nonroutine; prior-art status remains unresolved. |
| Full finite-word source/access conjunction | Not implied by sources read; prior-art status remains unresolved. |

The direct-sum/codebook mechanism is not automatically a routine
amplification in consequence: direct sum alone gives no lower bound against
a source-trained global reconstruction and global common support law. The
finite-interpreter avoidance argument supplies that missing comparison. Its
methods are familiar, however. It has not yet earned a substantive
originality claim without a focused primary-source comparison to
finite-dimensional convex geometry, sparse randomized approximation,
data-structure lower bounds, and restricted-access matrix--vector models.
The research goal correctly bars an absence-of-search inference.

**Originality status: not passed.**

## 3. Cassette significance

MATHS separates execution from condition compatibility, atom capacity,
traces, and observation. A theorem about one execution layer need not solve
the other layers to matter. Here the query is the actual supplied input to
the matrix action, so selecting a law from that query needs no separate
hidden-observation theorem.

Within the model, the theorem changes an available execution boundary: it
rules out treating a pre-query resident approximation plus one common sparse
correction operator as fresh-read optimal. The support advantage grows as
\(m/50\), survives source-trained selection of a resident state, and now
has linear ambient output dimension. That is a real mathematical
consequence, not only a four-dimensional curiosity.

Its significance for Cassette remains unproved because the theorem has not
connected that boundary to a source and access class Cassette can actually
use:

* The source is an adversarial dyadic Rademacher family selected after the
  finite interpreter range is fixed. No comparable result is shown for a
  declared Cassette source class.
* The comparator is specific: one pre-query resident reconstruction and one
  query-independent operator-unbiased law, with output in selected-column
  spans. Query-selected reconstructions, nonlinear decoders, and other
  encoded-page actions remain outside it.
* Support count is an abstract fresh-work unit. To turn the result into a
  page or byte claim, a source format, explicit catalog/selector bits, and a
  conversion from selected columns to physical traffic must be declared.
  MATHS requires that conversion when a plan consumes the theorem
  (MATHS.md, lines 491--492 and 774--782).

The remaining discriminating theorem is therefore quantitative and
model-specific: for one declared encoded-page format and source class, give
explicit catalog, selector, and random-bit costs, then prove a page- or
byte-level separation against every legal pre-query description in that
same format. That would turn the current abstract execution gap into a
Cassette resource frontier.

**Application-significance status: not passed.**

## Overall disposition

The theorem is preserved as independently supported execution-layer work.
It has not yet met the two remaining goal tests: established originality and
a consequential Cassette source/page frontier. Discovery should continue
from the quantitative source-class theorem above, not from a manuscript.
