# Paused research and product handoff

Research stopped at Drew's explicit direction. Do not resume discovery,
proof development, source searches, experiments, reviews, or manuscript
work without a new instruction. This checkpoint supersedes the active
next-step wording in RESEARCH_ROUTE.md. Production was not changed by
this investigation.

## Results Drew asked to retain

1. [Explicit K4 sampler](notes/k4_bounded_bit_full_linear_sampler.md).
   An implementation candidate for six-coordinate blocks with Gram metric
   \(P+r^2(I-P)\), where \(P\) is the K4 cut-space projector and
   \(r=2^{-\ell}\), \(\ell\ge1\). It specifies twenty integer prototypes,
   exact branch probabilities, three selected columns, and at most
   \(\ell+4\) fair bits. Its comparison with diagonal sampling and its
   original-column layout remain restricted.
2. [Query-dependent basis improvement](notes/query_adaptive_general_basis_reversal.md).
   Retain as a compiler-design theorem: for the stated nonscalar real
   spectra and intermediate caps, basis and sampling choices can improve
   worst-query error together. A strict theorem does not establish a net
   implementation saving.
3. [Finite-advice lower bound](notes/finite_advice_spectral_trace_lower.md).
   Retain as a certificate result for its finite-state static decoder and
   source-family model. It is not itself an executable product feature.
4. [Uniform four-coordinate obstruction](notes/q4_and_finiteword_cassette_significance_assessment.md).
   Retain as a constraint on optimization within its real-basis, two-read
   model. It rules out an asymptotic improvement there.

## Additional implementation candidate completed before the pause

The [explicit four-coordinate sampler](notes/explicit_sum_preserving_two_sparse_sampler.md)
has an [integer reference implementation](programs/equicorrelation_two_rule_sampler.py),
[a general independent reconstruction](notes/sum_preserving_two_sparse_real_sampler_review.md),
and [an implementation review](notes/explicit_integer_sampler_and_corollary_review.md).
For real blocks with Gram metric \(\mathbf1\mathbf1^T+\eta I_4\),
it preserves the query mean and coordinate sum, selects at most two
columns, and has ideal squared error at most
\((5/3)\eta\|x\|^2\). The formula applies for every \(\eta>0\).
It needs no catalog. Its exact integer sampling has a proved expected
random-bit cost and an unbounded rejection tail.

The [saved exact audit](notes/equicorrelation-two-rule-exact-audit.json)
covers 2,401 integer queries and the actual ticket map.
The [resource account](notes/explicit_integer_sampler_resource_account.md)
counts the integer representation and gives conditional column-record
examples. These are implementation inputs, not production-ready changes.

## Remaining product integration blockers

For either sampler, product work would still need to:

- identify and certify blocks satisfying the required Gram structure,
  or establish the admitted approximation error;
- connect the sampler to compiler plans, pager execution, source-column
  addressing, and Cassette's separate error and resource certificates;
- verify the chosen random source and actual native arithmetic path;
- establish that fresh-byte savings survive the workload's layout,
  resident state, cache behavior, and execution costs.

No representative production workload or native Cassette execution has
proved a net saving. No result has passed the complete originality and
sufficient-significance assessment. No manuscript exists.

## Current arithmetic records and unfinished draft

The following notes were saved before the pause. They have different review
boundaries and must not be promoted automatically into native guarantees:

- [Explicit finite-word separation](notes/explicit_sampler_finite_word_separation.md):
  reviewed arithmetic for the stated rounded-source model.
- [Bounded-bias trace extension](notes/biased_rounded_column_trace_lower.md):
  a completed proof note, not a native-arithmetic validation.
- [Fixed-width dyadic query net](notes/fixed_width_dyadic_query_trace_net.md):
  completed construction; fixed 13-bit coordinates apply only to one block.
- [Binary32 arithmetic account](notes/explicit_sampler_binary32_error_account.md):
  conditional on its stated arithmetic model; combined review and reference
  verification were not completed before the pause.
- [Bounded primary-source comparison](research/explicit_two_rule_sampler_primary_comparison.md):
  treats the two-rule sampler as an elementary useful specialization, not
  an accepted original contribution.

A proposed directional eigenquery lower was being investigated when the
pause arrived. Its subagent was interrupted. The proposal is unreviewed
and must not be included in accepted quantitative claims.

Directional draft file present at checkpoint: no.
