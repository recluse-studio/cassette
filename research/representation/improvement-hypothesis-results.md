# Improvement hypothesis: result

**Reject complete-path improvement for the three tested candidate implementations
at the frozen settings.** All returned original weights and ordinary results correctly.
All used more traced Python memory and took longer than both complete-route comparators
on every generated source case. None reduced discovery reads against adaptive row sums.

**Retain the narrower support-calculation gain.** Full-pair interpretation returned
the same exact mathematical bound as both flow implementations. Against the improved
flow implementation, it used less traced memory and took less time in all 32 cases.
This finite observation supports that scoped gain; non-rejection of H0 is not its proof.

## Frozen experiment and observed results

The [protocol](improvement-hypothesis-protocol.md) preceded case generation and results.
The [executable fence](improvement-hypothesis-experiment.md) binds its imported definitions
and protocol by digest. The [raw results](improvement-hypothesis-results.json) retain
case-level measurements, exact outputs, payload digests, counts, and timing repeats.
The [bounded review](improvement-hypothesis-review.md) records two repaired interface and
reporting defects. The final review passed those repairs. The first measurement remains
in [the initial result](improvement-hypothesis-initial-results.json); the rerun is not
another independent sample.

- Same-information support: 32 generated cases, with sizes 8 by 8, 16 by 16, or
  32 by 32. Full-pair, improved flow, and the earlier flow oracle agree exactly.
- Complete routes: 32 source cases, nine queries each, six methods: 1,728 distinct
  source/query/method checks. Timed repeats and allocation calls are repeated execution
  of these checks. They are not additional independent source observations.
- Source families: 11 independent, six structured, eight near-tie, and seven coupled
  cases. Gate sizes are 12 by 16 or 24 by 32. Quotient step is 256 throughout.
- Every route chooses the exact winner, fetches the exact original payload, and
  returns the same ordinary integer matrix-vector product as the full-source reference.

Each ratio below is the median of 32 paired source-case ratios. For a route case,
the memory statistic is its maximum measured allocation peak over nine queries;
the time statistic is its median query time, each query using three repetitions.
Ratios below 1 favor the candidate. The table reports Python allocation, not physical RAM.

| Candidate and comparison | Memory ratio | Time ratio | Gate reads |
|---|---:|---:|---|
| Full-pair support / improved flow support | 0.143 | 0.0824 | Neither reads a source |
| Pair-total route / adaptive row sums | 1.145 | 2.179 | Equal in all 32 cases |
| Projected scalar-dual route / adaptive row sums | 1.138 | 1.864 | Equal in all 32 cases |
| Full-pair route / adaptive row sums | 1.199 | 7.252 | Equal in all 32 cases |
| Pair-total route / exact centered | 1.589 | 2.691 | More in 30 cases; equal in two |
| Projected scalar-dual route / exact centered | 1.499 | 2.357 | More in 30 cases; equal in two |
| Full-pair route / exact centered | 1.622 | 10.761 | More in 30 cases; equal in two |

Across all 288 source/query pairs, adaptive row sums and each candidate read 71,200
gate bytes. Exact centered reads zero gate bytes. All six routes fetch one identical
payload per source/query pair. Gate requests have fixed length within each source;
the executable checks that byte totals and request totals therefore agree in direction.
The streamed reference reads 245,376 gate bytes. These are logical reads of cached
local files, not measured external-drive traffic.

The known 4-by-4 witness also replayed successfully. Its full-pair guide uses 67 bytes,
versus 64 for exact centered, and both need zero gate reads. The stronger full-pair
interpretation still removes the two gate reads required by projected interpretation
of the same guide. [Witness output](improvement-known-witness-results.json) records
this previously known, separately scoped counterexample.

## Hypothesis decision

The null asserts improvement. Exactness is a prerequisite; memory, time, and reads
are separate conditions. The observed complete-path resource regressions directly
contradict universal improvement on the fixed test set.

The [NIST paired sign-test construction](https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/signtest.htm)
also supplies a conditional statistical check. With source cases as the unit and
memory ties counted as failures to improve, each candidate loses all 32 memory and
time comparisons against both route comparators. Each upper-tail probability is
2^-32 = 2.3283e-10. The predeclared family has 20 tests and a Bonferroni threshold
of 0.0025. All 12 route memory/time null consequences are rejected. The three
gate-read comparisons against exact centered are also rejected: 30 losses in 32
cases give p = 1.2317e-7. The three gate-read comparisons against row sums tie.

Neither support-only test rejects the improvement hypothesis. The stronger statement
available from those fixtures is the directly observed win in all 32 cases: median
allocation is about 86% lower and elapsed time is about 12.1 times shorter than the
improved explicit-flow program. The comparator uses the established potentials and
Dijkstra refinement described in [the algorithm notes](https://courses.grainger.illinois.edu/cs473/sp2016/notes/25bis-mincostflow.pdf).
That program is a stronger comparator than the earlier repeated Bellman-Ford solver;
it is not a certified optimum over established implementations.

## Meaning for Cassette

The full-pair interpreter makes one mathematical operation cheaper. On these sources,
its extra routing work excludes no additional original reads after the existing
adaptive method, so that local gain does not produce a complete-path gain.

The result rejects these implementations at these settings. It does not reject every
encoding precision, future interpreter, or source family. The test measures all newly
allocated guide, query, reader, routing, fetched-payload, and normal-calculation objects
inside the Python call; shared interpreter objects, process baseline, and the already
open source handle are outside the trace. It does not establish physical peak RAM.
Timing signs may share machine noise, so their p-values depend on the stated
independent-sign assumption. The fixed resource regressions remain observable facts.

MATHS section 12 remains OPEN. A complete advantage on real model weights, physical
storage supply, a smallest possible RAM bound, and independently established novelty
remain unproved. This result changes neither product code nor release acceptance.
