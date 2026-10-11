# Exact routing experiment results

The saved [JSON report](remainder-sum-results.json) records seed 2026092101, four generated source families, 55 configurations per family, and 387 dependent routing events per configuration. All 85,140 route executions returned the same selected original payload bytes and normal calculation results as their full-source reference. The configurations reuse the same 129 input texts within each family; this is not 85,140 independent test inputs.

Every configuration reads 111,456 selected-payload bytes and 117,696 embedding bytes. The methods differ in resident guide bytes, discovery reads, and interpretation work. The source file is 51,072 bytes, including 3,456 original gate bytes across three layers.

| Source family | Representation | Step bits | Guide bytes, all layers | Gate bytes requested | Gate page bytes, coalesced per route | Extra support coordinates | Integer square roots |
|---|---|---:|---:|---:|---:|---:|---:|
| independent | exact_centered | 0 | 3,231 | 0 | 0 | 0 | 0 |
| independent | quotient | 8 | 1,563 | 6,720 | 577,536 | 0 | 0 |
| independent | sums | 8 | 1,785 | 5,928 | 520,192 | 240,521 | 0 |
| independent | moments | 8 | 2,145 | 4,176 | 376,832 | 240,521 | 37,152 |
| shared_remainders | exact_split | 8 | 2,355 | 0 | 0 | 0 | 0 |
| shared_remainders | quotient | 8 | 1,287 | 2,736 | 192,512 | 0 | 0 |
| shared_remainders | sums | 8 | 1,437 | 2,616 | 184,320 | 245,158 | 0 |
| shared_remainders | moments | 8 | 1,653 | 2,088 | 135,168 | 245,158 | 37,152 |
| near_ties | exact_centered | 0 | 1,071 | 0 | 0 | 0 | 0 |
| near_ties | quotient | 8 | 243 | 442,368 | 2,097,152 | 0 | 0 |
| near_ties | sums | 8 | 375 | 442,152 | 2,097,152 | 237,102 | 0 |
| near_ties | moments | 8 | 555 | 442,152 | 2,097,152 | 237,102 | 37,152 |
| duplicate_rows | exact_centered | 0 | 207 | 0 | 0 | 0 | 0 |
| duplicate_rows | quotient | 8 | 243 | 0 | 0 | 0 | 0 |
| duplicate_rows | sums | 8 | 249 | 0 | 0 | 0 | 0 |
| duplicate_rows | moments | 8 | 249 | 0 | 0 | 0 | 37,152 |

The sum and moment rows use one block of 12 coordinates. The page column assumes 4,096-byte pages and counts each distinct gate page once within each route, with no cache retained across routes. Requested bytes, this modeled page count, and actual external-drive latency are separate quantities. Payload and embedding transfers still remain.

## What the comparison establishes

- Arbitrary generated source matrices satisfy the exact routing proof; no fitted source structure is assumed for correctness. Near ties can make the smallest guides read every original gate row.
- At step eight in the independent family, adding sums reduces gate requests from 6,720 to 5,928 bytes; adding squared sums reduces them to 4,176 bytes. Guide sizes rise from 1,563 to 1,785 to 2,145 bytes, with substantial added support work. This is a tradeoff, not overall dominance.
- The shared-remainder family admits a 2,355-byte exact split representation, versus 2,961 bytes for its exact centered representation. Both need no gate reads. A singleton-summary candidate would match the former bytes while wasting support work, so the stronger exact split comparator supersedes that candidate.
- Smaller logical reads do not necessarily reduce rounded page traffic: the near-tie family pays the same gate-page count across the displayed quotient, sum, and moment rows.
- The generated operation chooses a payload by an exact integer argmax. A dense layer that consumes every numeric gate score has a different recovery obligation. These results do not establish selective execution of an arbitrary dense language model.

## Comparison status

The sweep covers step exponents 4, 8, and 12, two phase rules, four block sizes for sums, and three for moments, plus exact centered and exact split comparators. It is a finite experiment, not an exhaustive optimum over all precision allocations, phases, transformations, source layouts, or exact MIPS algorithms. The proven finite phase optimum is separately scoped in [finite-routing-frontier.md](finite-routing-frontier.md).

The quotient, knapsack, centered-moment, and lossless-residual ingredients have established antecedents. The experiment proves exact source-record use and exposes resource tradeoffs. It has not proved a novel complete-path advantage over the fully improved established frontier.
