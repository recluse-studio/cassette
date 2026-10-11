# Improvement hypothesis: frozen experiment

Frozen on 2026-09-29 before generating the new cases or viewing their results.
Authority: MATHS.md section 12, especially exact recovery and total peak memory.
This record implements the principal's hypothesis direction without changing it.

## Claim and verdict

**H0: The proposed methods improve the complete query-to-original-weights path.**
An improvement preserves every exact winner, original payload, and ordinary integer
calculation, reduces peak memory, and does not increase supply time or discovery reads.
This is a conjunction of claims; a speed gain alone does not prove the conjunction.
We also test the narrower claim that full-pair support improves the same-information
calculation. That subclaim cannot establish the complete-path claim.

Correctness and finite resource inequalities are directly decidable on these fixtures.
One mismatch rejects exactness in the stated domain. One resource regression refutes
universal dominance on the tested set. A finite pass supports only that tested scope.

For measured performance, test necessary consequences of H0 for each metric:
H0 requires strict memory improvement, so its statistical consequence is that the
probability of equal or greater allocation is at most one half. For time and reads,
the consequence is that the probability of a strict regression is at most one half.
H1 says the relevant probability exceeds one half. These consequences are weaker
than universal improvement; rejecting one rejects that necessary condition. Count
memory ties as failures to improve, count other ties as non-losses, and compute the
exact upper Binomial(n, 1/2) tail. Apply Bonferroni over
all 20 predeclared tests, rejecting at 0.05/20. The family contains two support tests
(peak allocations and elapsed time) and 18 route tests (three candidates by two
comparators by the same two metrics plus gate bytes). Failure to reject is inconclusive;
it does not prove improvement. Report wins, ties, losses, and effect ratios as well.
No timing repeat or query within a source is counted as an independent source case.

The paired sign-test construction follows the [NIST sign-test reference](https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/signtest.htm).
Time and read ties are included conservatively. The independence assumption concerns
generated source cases, not real language-model traffic. Shared machine state can
correlate timing signs; timing p-values are conditional on the independent-sign model
and do not remove that measurement limitation.

## Fixed cases and comparisons

1. **Same-information support:** seed 2026092901; 32 independent source cases, with
   size drawn uniformly from 8 by 8, 16 by 16, and 32 by 32, and family drawn uniformly
   from independent residuals, mostly-zero residuals, and boundary-valued residuals.
   Widths range from 0 through 15. Each case has a fresh query in [-31,31]. Compare
   the canonical full-pair solver with an integral transportation solver using shortest
   paths, node potentials, and Dijkstra. Include graph/preparation costs. Verify both
   against the prior Bellman-Ford flow oracle before measuring. No residual table is
   passed to a solver. The [university algorithm notes](https://courses.grainger.illinois.edu/cs473/sp2016/notes/25bis-mincostflow.pdf)
   describe this established optimization; it improves the previous comparator but
   is not a certified best implementation of every applicable established algorithm.
2. **Complete routes:** seed 2026092902; 32 independent cases with size drawn uniformly
   from 12 by 16 and 24 by 32, and source family drawn uniformly from independent,
   shared structure, near ties, and coupled residuals. Use the existing scale
   experiment's source generators with nine queries per source, including zero.
   Use step size 256 with the existing source-derived phase choice. Compare full-pair,
   projected scalar-dual, and pair-total interpretation against adaptive row sums
   and exact centered encoding. Include a streamed full-source route descriptively.
   All uncertain routes use the same adaptive original-score refinement and least-index
   tie rule. A compact Q,w,t,u guide serves full-pair. Projected guides use the existing
   direct Q,w,t,u,L,V encoding, with their bytes fully charged. This run evaluates
   those retained implementations; it does not optimize their codecs after results.
3. Replay the earlier 4-by-4 full-pair source witness separately. Its published
   64-byte exact-centered versus 67-byte full-pair guide is known before this run;
   it is a regression check, not a new independent observation or p-value.

Each route reads a generated temporary local source containing signed-16 gate rows
and signed-16 square payload matrices. Verify source identity before timing, derive
every offset from the guide header, fetch the original payload, and perform the same
integer matrix-vector product. The verifier retains reference material outside the
candidate interface. Candidates receive only packed guide bytes, query, and a reader.
No candidate receives a source matrix, residual matrix, or expected answer.

Every route must make exactly one same-sized payload read. Every gate request has
exactly 2d bytes. Assert these equalities for every call: within a source case, gate
bytes then determine total transferred bytes and total request counts. Retain both
counts in the raw record. A change to variable-sized or directory reads would require
separate access statistics and cannot inherit this simplification.

## Measurement and accounting

- Record packed guide bytes, source bytes, logical gate and payload requests/bytes,
  exact winner and output, and charged traced Python allocation peak. Memory tracing
  begins before copying the resident guide, constructing query objects, decoding,
  routing, reading, unpacking the original payload, and calculating normally. Charge
  retained reader and output objects. Shared interpreter code and process baseline
  are excluded explicitly. This measures the complete Python call's allocations,
  not process RSS, physical RAM, or the future packed product runtime.
- Time separately with tracing disabled. Include guide preparation and decode, source
  reads, and ordinary calculation. Three rounds alternate/shuffle method order using
  seed 2026092903; use each route's median. Use aggregate median query time, maximum
  measured allocation peak, and total gate bytes as the source-case statistics.
- For support calls, likewise include copied guide/query objects and preparation;
  use three timed repetitions and one separately traced call. Record exact equality.
- The source fixtures are local and expected to be cached. Logical-read savings
  cannot establish cable, external-drive, or model-inference speed. Do not evict the
  user's caches or inspect external drives. Do not substitute an assumed latency.
- Bind the protocol, executable fence, and imported definitions by SHA-256. Save all
  case-level results, including regressions. No optional stopping or case deletion.
  A correctness failure stops only dependent measurements and is retained explicitly.
  If a fixture budget or implementation error prevents execution, record it and any
  repair; do not silently change a hypothesis or source distribution.

## Acceptance and end state

Retain a reproducible executable fence, raw results, and a short verdict for each
claim. Report complete-path evidence separately from support-only evidence. Research
success requires the complete advantage and novelty conditions in MATHS section 12;
this finite experiment may reject a claim or leave that larger objective open.

Pre-execution review tightened the strict-memory criterion and made the request-count
equivalence explicit. The review also identified that traced Python allocation cannot
establish physical peak RAM and that timing signs can share machine noise. These
boundaries are retained; no allocation or cached-file pass closes the physical goal.
