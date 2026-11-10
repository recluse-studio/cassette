# Bounded hypothesis-test review

The independent reviewer checked the hypothesis direction, sign-test implementation,
source-input boundary, and read-count equivalence. The root retained the primary
experiment and all implementation work.

Before the first run, review made memory ties explicit failures to improve and added
assertions that every route reads one same-sized payload and fixed-sized gate rows.
The frozen protocol digest is
`2ad0b2d0c68133d67a235099564d7725f1b2badce8453c53d2604fb638f956b6`.

After the first run, review confirmed the statistical implementation and access-count
equivalence. It found two interface/reporting defects: the source identity arrived as
a separate argument instead of part of the verified reader boundary; and the memory
p-value field was called `p_regression` although memory ties also count as failures.
The experiment now groups file descriptor and already-verified identity into one source
handle and names the field `p_improvement_failure`. The candidate still copies the
identity into its measured reader object. The handle conveys no source weights or
expected output. The same source-handle convention applies to every method.

The first results remain in `improvement-hypothesis-initial-results.json`. The complete
frozen case set is rerun after these two repairs; no source distribution, method,
seed, metric, decision threshold, or case-selection rule changes. The current result
binds the revised executable digest. This is a repair verification, not a second
independent statistical sample. The protocol is not rewritten after observing results.

The final independent check passed both repairs and confirmed that methods, cases,
metrics, and statistical rules remained unchanged. The root's final evidence check
verified file digests, all 1,728 retained payload/output records, access accounting,
and all 20 statistical decisions.

The reviewer also confirmed limits that remain material: traced Python allocations
do not establish physical total RAM, and shared machine state can correlate timing
signs. Neither the support comparison nor the local-file route comparison establishes
a physical-drive, frontier-model, or novelty result.
