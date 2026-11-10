# Historical sampled-execution investigation — superseded objective

The principal identified this investigation as addressing the wrong objective. Its results
concern sampled matrix-product error. They do not establish a minimum-RAM mathematical
representation that precisely locates relevant weight regions and returns their original
values for normal calculations. In particular, the 7.39% result is not progress evidence for
that goal. The current objective and active work are in [README.md](README.md) and
[MATHS.md section 12](../../MATHS.md).

The record below preserves the mathematical work under its original assumptions. Its
scoped sampling claims are historical findings, not accepted deliverables for the corrected
representation, routing, and reconstitution objective.

## Results from the first parallel investigation

| Route | Mathematical result | Comparison outcome |
|---|---|---|
| Established representations | Primary-source review of low rank, weighted low rank, scalar/vector/trellis quantization, sparse corrections, tensor and structured factors, CUR, and balanced sampling | Supplies the comparison families; no universal winner or literature exhaustion claimed |
| Tagged Walsh pages | Exact query cancellation from a short tag representation; sharp separation from every one-column importance law on the declared query | Rejected as novel: a charged resident transform and external output factor reproduce every operation and cost |
| Quantized feature balance | Exact reduction to a changed residual; explicit finite rational example introduces error where exact balance had none | Supplies a counterexample to an unqualified improvement claim; a jointly optimized bit/error advantage remains open |
| Unequal read costs, C1 | Exact optimizer over the full positive categorical simplex for cost times variance, with a global proof | Retained as an improved established sampling baseline; exact sampler inputs and their construction are charged separately |
| Exact-law information, C2 | A finite source family forces at least one resident bit per independent pair relationship when exact optimal laws are selected without preliminary reads | Identifies the information cost of the exact interpretation requirement; an approximate frontier remains open |
| Approximate Gram interpretation, M1 | Relative quadratic accuracy transfers an optimal sparse decoder's risk within a proved factor | Retained baseline; a small absolute Gram error alone can yield an arbitrarily poor relative result |
| Finite static/adaptive separation | The existing finite-advice theorem gains an explicit aligned-record consequence | Retained restricted corollary; it does not defeat established query-adaptive or coded-page methods |
| Exact signed-balance interpretation | Three explicit cases attain the optimum among all unbiased, hard-two-sparse, sum-preserving laws in every real dimension | Retained theorem, with matching duals and exact dyadic sampling; no source-dependent decoder table |
| Dimension-dependent worst case | Exact maximum over the query class; four coordinates give squared-error ratio \(\sqrt{13}-2\) | Retained theorem, independently checked; 3.29103% reduction from the earlier four-coordinate rule's sharp bound |
| Optimized spectral-column interpretation | Unique \(\rho\) solving \(\sum_i\lambda_i/(\lambda_i+\rho)=m\) is the exact global risk constant | Exhausts all unbiased coefficient laws within the fixed orthogonal-column basis and hard read cap, including query-dependent and correlated choices |
| Coupled column representation | A fixed Hadamard mixing plus exact signed interpretation preserves the dominant contribution in each fetched pair | Strict worst-query win over the optimized spectral-column basis when the declared four-column spectrum has leading/residual ratio \(s>9\); finite width and metadata are charged |
| Finite common-mode frontier | A dual witness gives a necessary lower bound for a stronger interpreter that allows the coordinate sum to vary | Retained obstruction; sufficiency and a matching explicit decoder remain open |

The strongest relevant interpreter comparator permits query-dependent correlated support,
arbitrary signed coefficients, and exact preservation of stored features. Restricting it to
independent draws would discard known improvements. Within a stated hard-support class,
[metric-interpretation.md](metric-interpretation.md) records a convex formulation of the exact
optimum. Its combinatorial size is an interpretation cost, not an excuse to compare only with
a weak law.

## Independent mathematical checks

The geometry agent independently reconstructed C1 and C2 and checked M1 and its counterexample.
Its review found the proofs sound under their stated assumptions. C1 requires positive costs
and positive energies on the sampling support. C2 requires exact selection, no preliminary
geometry reads, and accounting for every source-dependent state, including identifiers.

Root review corrected three statements in the joint-construction note before acceptance. A
complex feature system has up to twice as many real balance constraints. A zero feature action
does not imply a zero full answer when the residual is nonzero. A nonzero quantization error
need not produce variance if the sampler never varies in that direction. The revised note
restricts the real support theorem correctly and uses a concrete rational counterexample.

Root review also changed the geometric candidate's physical read statement from exactly
\(2m\) records to at most \(2m\), matching its support guarantee.

The source-review lane independently checked all three signed-decoder samplers and their dual
certificates. It also reconstructed the dimension bound and supplied an independent fixed-law
proof of the spectral minimax upper bound. The geometry lane checked the joint construction,
the exact spectral comparator, and the strict \(s>9\) comparison. Root review corrected the
zero-mass conditional branch, a random-bit bound, and the distinction between an algebraic
real-query extremum and a fixed finite query format before retaining the results.

Hadamard preconditioning before sampling is established, including in
[Preconditioned Data Sparsification](https://arxiv.org/abs/1511.00152). The checked sources did
not supply the exact all-real signed-sum formula or the coupled-column comparison proved here.
That finding supports continued originality review; it does not establish priority.

## Recorded finite attacks

| Check | Inputs and observation |
|---|---|
| C1 simplex optimizer | 700 generated vector/cost instances; 70,000 competing probability vectors; no violation of the proposed optimum |
| C1 arithmetic example | Exact optimum 50 versus approximately 50.583592 for the second-moment-optimized law under the same actual objective |
| C2 encoded-sign recovery | All 64 four-column sign sources, with all six pair queries each; 384 recovered relationships, maximum floating error below \(7.2\times10^{-15}\) |
| Gram perturbation attack | Absolute Gram errors tending to zero give true-risk ratios approximately 5.05, 50.005, and 500.0005 |
| Quantized feature attack | Exact rational arithmetic at \(e=1/10\) gives error \(1/400\) with a unit output direction |
| Four-coordinate dual inequality | 100,000 generated dual/query-sum cases; no inequality violation; the proposed extremal query attains equality to floating precision |
| Exact signed decoder | 19,520 nonzero integer queries in dimensions 2 through 6; exact rational checks of probability, mean, sum, support, output precision, and equality to the dual bound all pass |
| Spectral minimax | 540 generated spectra/read caps and 27,000 competing queries; every witness agrees with the exact formula, with largest relative floating gap below \(4.1\times10^{-15}\) |
| Shared finite representation comparison | All 83,520 nonzero integer queries in \([-8,8]^4\), spectrum \((16,1,1,1)\): spectral peak \(376/217\), coupled peak \(69/43\), exact worst-case reduction \(1195/16168\), or 7.391143% |

The proofs carry the quantified claims. These checks only test the algebra and numerical
formulas on their declared finite cases. No model benchmark, physical-drive measurement,
native-runtime performance gain, or release acceptance was run or inferred.

## What the strongest completed comparison establishes

The spectral comparator is an optimum over a complete, declared interpretation class. Its
source columns are orthogonal; every estimator returns a combination of at most the allowed
number of fetched columns. The proof permits arbitrary signed coefficients, correlations,
and query-dependent selection. The new construction changes the stored column basis and uses
the exact signed interpreter. Both alternatives retain the source and materialize four encoded
column records under the common format, resident-basis, and certificate account in
[the joint construction](four-coordinate-decoder.md).

For a spectrum proportional to \((16,1,1,1)\), the real-query worst-case constants are
approximately 1.732928 and 1.605551, giving a 7.350379% reduction. The separately enumerated
finite query format gives 7.391143%. As the leading spectral value grows, the real-query
reduction approaches 19.722436%. These percentages describe mean-square error at the declared
read cap; they are not throughput, RAM, model-quality, or hardware measurements.

## Remaining work against the principal's endpoint

The completed construction improves an optimized spectral basis. The established comparison
also includes alternative transform codes, quantization, low-rank corrections, stored features,
and source-dependent page layouts. A strict advantage over that wider applicable collection,
an independently sustained originality claim for the combined mechanism, and the Cassette
condition/observation/composition guarantees remain unproved. The finite common-mode lower
bound identifies a further possible interpretation improvement whose matching upper bound is
still absent. The requested endpoint retains those unresolved obligations.

Research files are local working-tree additions. `MATHS.md` section 12 records the programme
without admitting a production kernel or changing the existing release gates. The independent
`pure_math_astra` and `pure_math_lab` files remain unchanged.
