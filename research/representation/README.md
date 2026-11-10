# Mathematical representation, exact routing, and local reconstitution

The active objective is to invent a mathematical representation that occupies as little RAM
as possible and lets calculations driven by the user query identify the correct regions of
the full external weight table. Those regions must be retrieved or reconstituted at source
precision, packaged, and supplied for normal calculations quickly enough to keep execution
moving. [MATHS.md section 12](../../MATHS.md) is the authority.

The representation is an object the machine calculates with. It is not an explanation of the
model, a smaller partial weight table by assumption, or an estimated answer in place of the
weights. Its mathematical form remains open.

## Current investigation

### Worklog and current direction

- 2026-09-29: The principal requests a null hypothesis that the new methods improve on
  established methods, followed by tests that can contradict or support that claim.
- Preserve the complete objective: minimal total RAM, exact region selection, original
  weight recovery, and ordinary calculation without a supply bottleneck.
- Freeze cases, comparisons, and verdict rules before new measurements. The root agent
  runs the experiment; a finite independent review may challenge the protocol and results.
- Completed: 32 support comparisons and 1,728 complete-route checks under the
  [frozen hypothesis protocol](improvement-hypothesis-protocol.md). All exactness checks
  pass. The complete-route improvement claim fails for all three tested candidates;
  the full-pair support calculation retains its narrower gain against improved flow.
- Current direction: retain the [negative complete-path result](improvement-hypothesis-results.md)
  as a constraint on further representation research. The requested hypothesis test is
  complete; the original research objective remains open. Physical drive speed and
  frontier-model performance remain unmeasured. Product code is unchanged.

The principal corrected the objective after the first investigation. The earlier 7.39%
result concerns error in sampled products and does not count toward this objective.
Its proofs and experiments remain in [the historical comparison](COMPARISON.md).

The new investigation derives constructions before searching for their nearest published
counterparts. Primary sources then challenge originality and provide strong comparators.
The work must prove the complete chain:

1. Encode the source's relevant mathematical structure in a small finite RAM representation.
2. Calculate with the query or available runtime state to identify the exact required region.
3. Resolve and read its external encoding, accounting for every intermediate lookup.
4. Return the original source-precision weights, with the right coordinates and layout.
5. Keep total peak RAM and supply time within the declared bounds throughout execution.

A region identifier already supplied by an oracle is not a solution to step 2. A local decoder
can make progress on steps 3 and 4 if it labels that supplied-region boundary explicitly.
An accurate output estimate is not reconstitution of weights.

## Active mathematical lanes

| Lane | Required result |
|---|---|
| Exact decision representation | Derive a compact arithmetic object that preserves region choices exactly while discarding source values irrelevant to those choices; return original payload weights separately. |
| Algebraic and geometric routing | Derive the relevant region from a stated source structure and runtime state, with all discovery work and locator state charged. |
| Exact local reconstitution | Derive local inversion that returns a requested original tile without materializing or scanning the whole encoded model. |
| Query lookahead and supply | Derive which regions can be identified early and the precise read, memory, and computation conditions that prevent a supply stall. |

Each lane must produce a construction or a discriminating counterexample, not just a restated
objective. Results enter the active record only after their proof and resource assumptions are
independently checked. A special source family must remain visibly special.

## Results under the corrected objective

The latest executable work tests two complete source operations. The
[routing comparison](remainder-sum-comparison.md) covers 220 source/configuration pairs,
each with 387 dependent choices and original-weight calculations. The
[dense ReLU comparison](dense-relu-comparison.md) covers seven configurations with 387
dependent layer calculations each. All match their full-source references exactly.
These are generated integer models. The reports distinguish encoded guide bytes from
peak RAM and requested bytes from physical-drive performance.

The new representations keep quotients, remainder sums, and optional squared sums in RAM.
Their interpreters prove which source choices or zero contributions can be ruled out,
then retrieve the original weights for the required ordinary calculations. Uncertainty
causes explicit source reads. Research on joint relationships between residuals follows
because separate per-row summaries discard information that can matter to relevance.

The latest pass shrinks the stored joint information without changing its comparisons,
then strengthens the interpretation without adding source information. The scalar-dual
calculation recovers the exact projected pair bound. Its packed source replay eliminates
two discovery reads, but a complete centered guide is smaller on that tiny source.
An improved adaptive-read comparator also makes earlier fixed-candidate read counts an
insufficient basis for a best-method claim. These results advance the mathematics while
keeping the complete resource comparison open.

The subsequent [full-pair interpreter](full-pair-polymatroid.md) uses all retained
row and column totals to calculate the exact pair bound, closing the earlier
transportation working-state gap with \(O(m+d)\) words. It uses batched changes to
a compact array of feasibility slacks, then an exact scalar search. This strengthens
interpretation without adding source fields to the uncapped marginal guide.
It still needs a complete resource comparison against specialized established
algorithms; the clipped guide cannot recover the totals that this stronger method uses.

| Mathematical result | Evidence and limit |
|---|---|
| [Improvement hypothesis test](improvement-hypothesis-results.md) | All 1,728 exact source/query/method checks pass. Three candidates use more traced memory and time than adaptive row sums and exact centered on all 32 source cases. Full-pair support separately beats improved flow in 32 cases. The whole-route improvement claim fails at the frozen settings. |
| [Quotient routing](phase-quotient-routing.md) | Exact containment for arbitrary integer gate matrices; packed interpreter and original payload recovery. The operation must select by argmax and not consume omitted numeric gate scores. |
| [Remainder sums and moments](remainder-sum-certificates.md) | Derived sums constrain interpretation without storing a partial set of source weights. Tight sum support and safe squared-sum bounds reduce some discovery reads at extra RAM/work cost. |
| [Independent sum review](remainder-sum-review.md) | Exhaustive tiny-domain containment and refinement checks, plus a sharper binary overlap representation with an explicit extra-memory cost. |
| [Dense ReLU relevance](dense-relu-relevance.md) | Proves exact zero activations before some source reads; all active calculations use original weights. Verified against a streamed comparator that already skips inactive down columns. |
| [Finite phase frontier](finite-routing-frontier.md) | Exhaustive optimum within its stated finite phase class. Minimizing residual width can lose even at the same guide-bit budget. |
| [Independent routing review](phase-quotient-review.md) | Tie, identity, encoding, dimensional stress, and page-accounting review; near ties expose full gate scans. |
| [Joint residual bounds](decision-margin-representation.md) | Endpoint tags, moments, and transport constraints derive sharper exact candidates; the generic transport solver's working memory is a material unresolved cost. |
| [Column-total propagation](column-sum-propagation.md) | Cross-region totals tighten per-row support using only dimension-sized scratch. Exhaustive tiny cases show strict candidate reductions, but direct totals use more bits than complete residuals in that tiny fixture. |
| [Projected joint interpretation](projected-transport-representation.md) | Aggregates other rows into one bounded row, reducing transportation working state to dimension-sized scratch. A checked case needs two original gate rows where propagated independent bounds need four, using the same guide; flow work remains additional cost. |
| [Pair-total interpretation](pair-total-support.md) | Retains that four-to-two reduction using one shared query sort and streaming integer arithmetic instead of a flow solver. Proved safe and checked against exhaustive relaxed optima; can be weaker than full projected interpretation. |
| [Clipped joint representation](saturated-slack-representation.md) | Keeps only boundary distances that can affect single or pair comparisons; proves exact equality after compression. All-neutral columns prove this joint information cannot improve separate row support. Includes an independent codec and proof review. |
| [Scalar-dual interpretation](pair-dual-refinement.md) | Exactly restores projected pair support through one scalar search, without a general flow solver or extra source information. Extra arithmetic and specialized established comparators remain material. |
| [Packed original-weight replay](dual-original-weight-check.md) | The dual bound removes two discovery reads after both earlier filters fail, then returns the original payload and normal result. Its 74-byte guide loses to a 69-byte complete centered guide on this tiny source. |
| [Stronger adaptive comparator](adaptive-source-refinement.md) | Original reads tighten a common-score bound and can eliminate subsequent reads; sorted query prefixes reduce support work. Same-guide improvements are verified on the earlier dependent paths. |
| [Boolean-generator decision certificate](relevance-information-bound.md) | Routes a certified structured source through generator signs, with a matching finite information bound. Classical zonotope support maps already implement this mechanism; arbitrary source tables need not admit it. |
| [Full aggregate feasibility](full-aggregate-feasibility.md) | Exact scalar cuts reject aggregates that cannot be split among the omitted rows. A binary specialization gives exact one-row support by nested quotas. Uses uncapped totals and explicitly charges row-sized workspace. |
| [Full-pair interpretation](full-pair-polymatroid.md) | Recovers the full transportation pair bound with batched suffix updates and a scalar dual, using row-sized and column-sized state. Small exhaustive, large-integer, rollback, and independent checks pass; novelty and a complete resource win remain unproved. |
| [Full-pair source replay](full-pair-source-witness.md) | Identical 67-byte guides produce different discovery reads under projected and full interpretation: two gate reads become zero, followed by the same original payload and calculation. A 64-byte lossless centered guide still wins the tiny guide-size comparison. |
| [Exact flow comparison](full-pair-flow-comparison.md) | Same compiled fields and exact supports across 16 cases. At 32 by 32, additional traced Python allocations are about 14 KB versus 227 KB for an explicit flow graph; timings also favor this implementation. Preparation is included, the source table is absent, and the strongest specialized comparator remains open. |
| [Larger projected comparison](joint-scale-experiment.md) | Original-weight replay across larger generated sources finds small gains on deliberately coupled cases and none beyond propagation on three other families. Decodes each method's actual guide; measures logical reads and work, with no measured-RAM or hardware-speed claim. |
| [Finite-precision relevance](rounding-relevance.md) | An exponent representation can certify exactly inert rounded updates under a fixed arithmetic contract; arbitrary dense sources can still force full reads. |
| [Exact decision representation](exact-decision-representation.md) | An arithmetic representation preserves all region choices on a declared finite input domain. Exhaustive search certifies a two-bit minimum coefficient width for one 25-state example. This overlaps established sign-preserving weight reduction. |
| [Source-derived geometric routing](exact-routing-geometry.md) | A checked quadratic arrangement of source gate vectors permits exact region selection from integer arithmetic. This is a special gate family, not a generic model routing solution. |
| [Exact local reconstitution](exact-local-reconstitution.md) | A global polynomial chart and addressed local corrections reconstruct requested original regions. The caller must still establish relevance. |
| [Exact lookahead](exact-query-lookahead.md) | Already resolved predicates identify the complete possible-region set. Unavailable control information cannot be treated as a known final region. |
| [Restriction packet lower bound](relevance-packet-algebra.md) | The dimension of the restricted source family gives the minimum source information needed to serve every unresolved choice without another read. An unrestricted record family gains no reduction merely from using polynomial notation. |
| [Prefix packets and physical slot rule](prefix-jet-packets.md) | A certified low-degree record family supplies an information-minimal packet from at most three logical payload extents. Branch preparation returns exact original records without a final payload copy. Physical RAM remains allocated unless a release or compaction mechanism is separately proved. |
| [Exact block-relevance certificates](query-region-certificates.md) | Source-certified zero gates and common nullspaces identify blocks that contribute exactly zero under the specified exact arithmetic. Both use established mathematics and require source structure; neither establishes a saving for arbitrary dense model inputs. |
| [Independent contraction review](prefix-packet-contraction-review.md) | Confirms the physical slot rule. Rejects a proposed layout that claimed both branches could always release a contiguous part of RAM without copying; the claim fails with three variables and four coefficient arrays. |
| [Supply schedule](relevance-packet-schedule.md) | Separates read completion, branch preparation, guard arrival, and final consumption. A proposed advantage over asynchronous raw prefetch was withdrawn because the comparison mishandled reads spanning predicate boundaries. |

The [reproducible prefix experiment](prefix-jet-checks.md) passed 28 synthetic sources,
3,048 prefix packets, 11,260 exact record decodes, and 196,070 coefficient-pair preparations.
It rejected all 21 tested source changes that violated the chosen degree bound. These counts
test the construction; they are not measurements of a real model or an external drive.

Primary-source checks identify known antecedents for integer decision compression, polynomial
restriction, interpolation, and nearly in-place evaluation. The prefix candidate reaches the
same minimum payload as a strong interpolation comparator. A novel advantage for the complete
query-to-weights path has not been established. The remaining physical-layout and deadline
claims receive separate independent review; unreviewed candidate improvements are not results.

## Quantities and correctness

The primary quantity is total peak RAM: resident representation, model-specific code and
metadata, interpreter state, routing scratch, read buffers, decoded weight regions, and normal
calculation workspace. Also record external storage, construction cost, discovery reads,
payload reads, decoding work, transfer completion times, and the first calculation that needs
each returned region.

Relevance, physical location, source-precision reconstruction, and normal execution are
separate correctness claims. Reading a region late, reconstructing the wrong region exactly,
or hiding a large index in the interpreter fails the relevant claim even if another passes.

The mathematical runtime state contains only information available at that point in the
calculation. A candidate must account for how the user query reaches that state and how later
states change the required regions. It may not assume that the entire execution's future
weight needs are known from the prompt.

## Comparison and completion

Compare methods on the same source and runtime-state family, exact region and value contract,
normal arithmetic, storage layout, total RAM ceiling, and allowed read/work budget. Claim the
smallest possible representation or peak RAM only with a matching lower bound or certified
optimum over the stated class. A tiny representation that forces a full scan has a different
supply cost from one that directly identifies a local region.

The requested endpoint remains novel representation and interpretation mathematics that
improves on the fully improved applicable established methods. A published method's framing
does not replace the objective, and a narrow theorem does not close the full endpoint.

The independent pure_math_astra and pure_math_lab roots remain unchanged. This directory is
research only; it does not admit a numerical kernel, alter the implementation queue, or claim
a physical-drive or full-model performance result.
