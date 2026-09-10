# growing_static_adaptive_separation_prior_work.md — bounded primary-source collision check for the finite-word static/adaptive separation; depends on ../notes/finite_word_growing_static_adaptive_separation.md, ../notes/query_adaptive_mahalanobis_primary_comparison.md, ../notes/query_adaptive_inverse_hull_design_audit.md, adaptivity-prior-work.md.

## Status and exact target

This is a bounded collision check, not an originality finding or a
publication assessment.  The target is the theorem in
`finite_word_growing_static_adaptive_separation.md`: after a fixed
finite-word resident interpreter is fixed, a dyadic source is chosen for
which a fixed finite catalog of query-selected, two-column unbiased laws
uses at most \(2m\) columns, while every source-dependent resident matrix in
the interpreter range followed by a *query-independent* unbiased row-sparse
operator requires more than \((2+1/50)m\) rows at the same worst-query
quadratic error.

The relevant distinction is structural.  The query \(x\) is visible before
the adaptive law is selected.  A sampled outcome then reads source columns
and returns a random linear combination whose **mean** is \(Ax\).  The
static class selects its resident matrix and its operator law before \(x\).
Neither class learns \(x\) by reading source columns.  Results called
“adaptive approximation” often use a different order: later *measurements
of an unknown input* depend on earlier measured values.

## Primary results read

### Unbiased sparsification and compression

* L. Barnes et al., [*Efficient Unbiased
  Sparsification*](https://arxiv.org/html/2402.14925v2), arXiv:2402.14925v2,
  Definitions I.2--I.3, Lemmas 1--2, and the proof framework in Sections
  2--3.  The paper proves facet concentration for its convex-divergence
  problem and exact efficient laws for divergence families that are
  additively separable or permutation invariant.  It therefore contains the
  conditional-mean/finitely supported reduction used by the present work in
  a nearby setting.  A fixed-coordinate quadratic \(y^*Gy\) with a general
  positive nondiagonal \(G\) is neither class in that theorem.  The paper
  does not take a worst query, compare one common law with a
  query-selected law, impose a hard source-column read count in the stated
  model, or make a finite-resident-source claim.

* J. Weare and R. J. Webber, [*Randomly Sparsified Richardson
  Iteration: A Dimension-Independent Sparse Linear
  Solver*](https://doi.org/10.1002/cpa.70012), *Communications on Pure and
  Applied Mathematics* 79 (2026), Proposition 5.2 and its proof.  For one
  fixed complex vector, pivotal sparsification is unbiased, has a hard
  support cap, and minimizes Euclidean squared error among unbiased sparse
  random vectors.  This is a direct antecedent of the inner Euclidean
  problem.  It does not cover a nondiagonal Mahalanobis loss, the outer
  worst-query supremum, a common operator law, a basis/source choice, or a
  resident codebook lower bound.

* H. Wang et al., [*ATOMO: Communication-Efficient Learning via Atomic
  Sparsification*](https://proceedings.neurips.cc/paper_files/paper/2018/file/33b3214d792caf311e1f00fd22b392c5-Paper.pdf),
  NeurIPS 2018, Sections 2--4 and Theorem 4.  For a given atomic
  decomposition of one input vector, it optimizes inclusion probabilities
  for an expected sparsity budget and an inner-product variance objective.
  This makes ``selecting a representation can improve one-vector unbiased
  compression'' standard.  Its support cap is not almost sure, its law is
  not optimized over all joint support laws, and it has no common-law versus
  query-selected minimax gap or finite resident state.

These papers make the conditional-support reduction and fixed-input
unbiased compression standard.  They do not imply the growing separation.

### c-optimal design and finite query catalogues

For a fixed query, the inverse-hull formula

\[
  \inf_{\alpha}x^*\Bigl(\sum_{|S|=s}\alpha_S
  E_SG_{SS}^{-1}E_S^*\Bigr)^{-1}x
\]

is a finite multiresponse \(c\)-optimal design problem after setting
\(A_S=G_{SS}^{-1/2}E_S^*\).  This identification is classical:

* G. Elfving, [*Optimum Allocation in Linear Regression
  Theory*](https://doi.org/10.1214/AOMS/1177729442), *Annals of Mathematical
  Statistics* 23 (1952), gives the scalar geometric \(c\)-criterion.
* G. Sagnol, [*Computing Optimal Designs of Multiresponse Experiments
  Reduces to Second-Order Cone
  Programming*](https://arxiv.org/abs/0912.5467), *Journal of Statistical
  Planning and Inference* 141 (2011), Theorems 3.1 and 3.3 and their
  proofs, treats finite matrix-valued experiment information and its
  multiresponse \(c\)-optimal geometry.
* H. Dette and T. Holland-Letz, [*A Geometric Characterization of
  c-Optimal Designs for Heteroscedastic
  Regression*](https://arxiv.org/abs/0911.3801), *Annals of Statistics* 37
  (2009), gives a related matrix-information/ellipsoid formulation.

Thus the present *inner* query-specific design calculation is not a new
optimal-design principle.  The unmatched steps are the outer
\(\sup_x\inf_\alpha\) value under fixed coordinate support, the comparison
to one common operator-unbiased law, and the realization of the resulting
block laws by one source-independent finite rational catalog.  Ordinary
finite-support design theorems also do not price the catalog, select it from
the query under an operator-unbiased constraint, or bind it to a source
column-read model.

### Adaptive versus nonadaptive algorithms

The closest terminology collision is information-based complexity.

* J. F. Traub, G. W. Wasilkowski, and H. Wo\'zniakowski, [*Average Case
  Optimality for Linear
  Problems*](https://iiif.library.cmu.edu/file/Traub_box00029_fld00003_bdl0001_doc0001/Traub_box00029_fld00003_bdl0001_doc0001.pdf),
  *Journal of Complexity* 1 (1984), Section 5 and Corollary 5.2.  Its
  adaptive information operator chooses the next linear functional from
  earlier **values of the unknown input**.  The proof constructs a
  nonadaptive information operator of the same cardinality and establishes
  that adaptation does not help for its linear-problem average and
  worst-case models.
* N. S. Bakhvalov, [*On the Optimality of Linear Methods for Operator
  Approximation in Convex Classes of
  Functions*](https://www.mathnet.ru/eng/zvmmf6826), 1971, pp. 1014--1018;
  English translation, *USSR Computational Mathematics and Mathematical
  Physics* 11, 244--249.  The primary abstract states equality of the best
  errors of linear and arbitrary methods for a linear operator on a
  convex centrally symmetric class, in the stated \(C\)-norm framework.
* D. Krieg, E. Novak, and M. Ullrich, [*On the Power of Adaption and
  Randomization*](https://www.cambridge.org/core/journals/forum-of-mathematics-sigma/article/on-the-power-of-adaption-and-randomization/3633856556AFDE5A9942452F04CC5D39),
  *Forum of Mathematics, Sigma* (2025), Theorem 1.1 and Sections 1, 5, and
  6.  It gives rate comparisons for approximation of a linear operator on a
  convex input class when the resource is a number of linear measurements.
  It also records examples with substantial adaptive/randomized advantages
  in that measurement model.

None of these results implies the present theorem or refutes it.  In their
model, \(x\) is an unknown element that the algorithm interrogates through
at most \(n\) functionals.  In the present model, \(x\) is already given and
the scarce resource is which columns of a fixed, only partly resident source
are fetched.  Treating a free visible query as adaptive information would
erase the source-access restriction: if \(A\) were also freely known, the
algorithm could simply return \(Ax\).  That is not the stated execution
class.  The classical results remain a serious provenance constraint: a
claim of a general theorem about “the power of adaptation for linear
problems” would be false in scope and would collide with this literature.

### Finite resident states and source families

The finite-state step of the growing theorem is an elementary finite-class
probabilistic construction: a \(b\)-bit interpreter has at most \(2^b\)
matrices; a quarter-net and a Walsh--Hadamard sign choice give one left
rotation whose range is at a fixed angle from every decoded matrix range.
The final union bound is a codebook/Grassmannian-packing style argument.

The bounded search found Grassmannian-code results and rate-distortion or
vector-quantization results, but no primary theorem with the same
quantifier order: a source is selected after an arbitrary finite resident
matrix range is fixed, while the ensuing lower bound permits the encoder to
select any matrix in that range after seeing the source.  Standard lossy
coding instead fixes a source distribution and distortion criterion; usual
Grassmannian-code bounds count separated subspaces.  Neither alone gives
the residual Gram lower bound, the unrestricted common sparse-operator
water-level lower bound, or the adaptive block upper construction.

This should be treated as a standard proof device until a more focused
finite-codebook/oblivious-subspace literature pass either identifies it or
locates a sharper established theorem.  It is not evidence of originality.

## Collision verdict

No primary theorem read in this pass already yields the stated linear
static/adaptive read-count separation.  That is a limited, positive scope
comparison, not an absence-of-literature conclusion.

The ingredients divide as follows:

| Component | Provenance status in this pass |
|---|---|
| Conditional-mean reduction; fixed-vector unbiased sparsification | Classical/established in the cited sparsification literature. |
| Fixed-query inverse-hull optimization | Classical finite multiresponse \(c\)-optimal design. |
| Finite selectable approximation of a continuous query family | Standard compactness plus rational perturbation, conditional on the local proof. |
| Finite interpreter has a finite matrix range; net plus union bound finds a source far from it | Standard finite-class/packing technique. |
| Exact conjunction: finite resident source description, fixed source-column reads, one common unbiased operator versus a query-selected finite catalog, and a growing hard-cap gap | Not implied by the sources read.  Its prior-art status remains unestablished. |

The substantial mathematical burden therefore remains the exact conjunction,
not a new c-optimality or sparsification lemma.  Before any significance or
originality claim, a wider search should include IBC models with visible
parameters and restricted data access, oracle/communication lower bounds
for matrix--vector products with preprocessing, and finite-codebook
subspace-oblivious embedding or data-structure lower bounds.  Those areas
were not exhaustively reviewed here.

## Source-access limits

I read the cited theorem statements and relevant proofs/definitions in the
Barnes arXiv HTML, the Weare--Webber primary article, the ATOMO primary PDF,
the Sagnol primary preprint, the Traub--Wasilkowski--Wo\'zniakowski primary
PDF, the Bakhvalov primary record and abstract, and the
Krieg--Novak--Ullrich primary article.  The Bakhvalov full Russian text was available but this pass used
its stated abstract rather than a new translation.  I did not complete a
systematic review of data-structure, communication-complexity, or
subspace-oblivious-embedding lower bounds; this note makes no claim that
none supplies a closer collision.
