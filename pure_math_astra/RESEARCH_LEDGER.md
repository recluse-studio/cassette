# Mathematical research ledger

## Starting state

The preceding task completed the documentation reading and archive. That was evidence-gathering progress; it did not discover or validate a new theorem. The current source files still match the archived reading. Existing pure_math_lab work is treated as prior local work.

## Initial questions

1. Which geometric constraints materially sharpen the compatibility/atom theory beyond its current universal realization theorem?
2. What exact resource law becomes available when page samples may be correlated or drawn without replacement?
3. At fixed residual-column energies, what are the sharp extremes of the minimax covariance invariant, and what geometry forces equality?
4. Does independent reconstruction reveal a failure in the production foundation that changes the theoretical problem?

The first three questions are independent investigations. The fourth checks the premises they consume. No lead result or novelty claim has been accepted.

## Candidate 1: fixed-energy extremal geometry

Initial derivation suggests that orthogonal columns uniquely minimize the spectral sampling invariant among realizable Gram matrices with a fixed positive diagonal. Rank-one residuals maximize it. The dominant-energy upper bound appears to have rank-one equality rigidity, while the balanced case is governed by a prescribed-diagonal density matrix supported on the Gram kernel. A written proof and adversarial reconstruction are next; the claim remains provisional.

## User correction: premature literature transition

The user rejected the move to literature review because the theoretical investigation had not been deep enough. That correction is binding. The fixed-energy bounds remain provisional supporting lemmas; they are not accepted as the requested breakthrough. Literature review and paper production are paused. Continue theoretical derivation and counterexample pressure without converting a short successful lemma into the end state.

At that checkpoint, the active unresolved problem was the exact minimum spectral sampling variance for a fixed-rank Gram matrix with prescribed diagonal. The equal-energy block construction supplied only an upper bound.

## Revised objective

The user supplied a fuller objective in `/Users/drewwiberg/.codex/attachments/98149c9a-4e8a-48fb-b692-1c7d106c140c/goal-objective.md`. It now governs the investigation. A candidate must separately establish mathematical correctness, originality beyond the closest prior work, and a material consequence under assumptions Cassette can satisfy. Independent agreement about a proof addresses only correctness. Literature may inform and challenge the investigation throughout; starting it does not end discovery. Discovery ends only after the complete case survives adversarial assessment, and manuscript review may reopen it.

## Surviving work and current questions

The equal-energy rank-constrained minimum now has a complete proof and two independent reconstructions, recorded in `notes/rank_constrained_gram.md`. It remains supporting work. A prescribed-energy generalization is written in `notes/prescribed_energy_rank.md`: stationary Gram components can be replaced by rank-one blocks at no greater sampling mass, and a rearrangement inequality concentrates all dependence into the smallest-energy group. Independent reconstruction is in progress.

The central significance question is still open: actual residual directions are fixed, so a best-geometry theorem does not by itself give Cassette a way to achieve that geometry. Resident-description selection may supply an admissible freedom, but its cost and consequences need a separate argument. The next investigations must confront that obstruction, rather than treating an abstract sharp extremum as an application result.

A cost-normalized iid sampling lane found an exact nonconvexity obstruction to the proposed intensity formulation. A resident-description lane derived a projection reduction and a codimension-one scalar spectral formula; a proposed fractional-projector relaxation remains unresolved. These are mathematical leads, not accepted advances.

The exact rational expected-cost counterexample and the distinction between fixed-law and joint fractional-projector gaps are preserved in `notes/failed_convexity_shortcuts.md`.

## Further results and failed conjectures

The prescribed-energy rank theorem survived independent reconstruction. Its full proof uses a common spectral subgradient, strict component replacement, and probability normalization. It is a sharp lower envelope; no general legal description is known to realize its geometry.

The dense-description envelope gives a factor-two approximation through weighted SVD. A primary-source challenge in `research/description-prior-work.md` identifies its ingredients as established methods; the combination is not being offered as a substantive original result. Its limitation is now exact: `notes/dense_description_surrogate.md` and `notes/orthogonal_group_descriptions.md` contain a family where its achieved variance approaches twice the true optimum. A proposed golden-ratio improvement failed.

For an atom whose columns form orthogonal rank-one groups, `notes/orthogonal_group_descriptions.md` proves the exact dense rank-k description optimum. A concave sampling-mass bound on projection diagonals shows an optimum can capture whole groups. The theorem also solves the fractional-projector relaxation for that class. It is a special structural result; significance for general Cassette atoms remains unestablished. General relative stability fails when a perturbation introduces a new residual direction. A restricted relative bound survives exact columnwise residual rescaling.

`notes/resident_description_and_pages.md` preserves the projection reduction, zero-column-deletion criterion, codimension-one spectral formula, page-cap exactness law, and all-but-one Horvitz--Thompson covariance. Its covariance is not matrix convex in omission probabilities. Scalar largest-eigenvalue convexity remains unresolved; absence of a numerical counterexample is not a proof.

## Unresolved questions from the fixed-coordinate model

1. Does the fractional-projector relaxation remain exact after optimizing the sampling law for arbitrary fixed atoms? A strict gap at a fixed law has been proved, but that gap disappears after optimizing the law in the same example. Searches have not supplied an exact counterexample to the joint problem. A proof or gap would change the available formulation of the true resident-description optimum.
2. Is the all-but-one hard-cap sampling objective convex at the scalar spectral level despite failure of matrix convexity? The distinction matters to exact optimization under a per-realization page limit. A proof or analytic scalar counterexample is needed.
3. What is the sharp worst-query gain from letting sampling depend on the observed query? For real rank-one residuals, the adaptive objective reduces to a weighted partition problem and the exact fixed/adaptive ratio is at most 3/(2 sqrt(2)). The general problem has a semidefinite formulation related to positive-semidefinite quadratic optimization. Independent derivation is in progress; no general sharp constant is accepted.

The next step is to discriminate these questions mathematically. Producing a manuscript now would not satisfy the goal. Correctness, originality, and consequential significance have not all passed for any candidate.

## Encoded-basis correction and current frontier

The original-column access class is narrower than Cassette's possible encoded descriptions. For a rank-one residual R=u v*, a resident v* and one acquired column u compute every query exactly. This preserves the original operator. It defeats any claimed universal lower bound based only on how many original residual columns are nonzero. The page-visibility note now states this counterexample and retains its zero-variance result only under its explicit restriction on unread query blocks.

`notes/rank_constrained_second_moments.md` characterizes the second-moment upper bounds H attainable by an unbiased random operator of almost-sure rank at most s: H must dominate R*R and tr(R H^dagger R*) must be at most s. A projection-moment lower bound and a finite singular-vector subset construction prove both directions. `notes/coded_basis_access.md` derives the exact worst-query variance root from that characterization. `notes/encoded_basis_model_correction.md` records the distinct access model and primary-source comparison.

The strongest new structural constraint is in `notes/coded_basis_rigidity.md`: for full-column-rank R and 1 <= s < q, unbiased diagonal thinning in a fixed basis attains the unrestricted coded optimum exactly if and only if the encoded columns are orthogonal. The theorem allows subset-dependent weights; it is not confined to Horvitz--Thompson weights.

The quantitative variance gap now has a short proof. Marginal inclusion probabilities give a diagonal-energy water level, and convexity of the trace inverse separates that level from the spectral optimum by an explicit multiple of squared off-diagonal Frobenius norm. A four-coordinate, two-read example proves quadratic order is necessary. Both calculations survived independent reconstruction. This simpler argument demotes the earlier lengthy equality proof as a source of intellectual difficulty; standard convexity suffices for the stated result.

The next consequential question is what this gap forces a byte-bounded transform family to encode. The numerical gap alone does not give a finite-precision metadata lower bound. A proof must retain the encoded query transform, its evaluation, the paged factor, and every information channel used to decode them. A restricted transform library or encoded sequence of plane rotations may give a tractable declared class, but no result for either has been proved here. The general real adaptivity gap and joint-description fractional relaxation remain open secondary questions.

Primary-source checks in `research/rank-moment-prior-work.md` did not find the full Loewner moment statement in the closest unbiased low-rank papers. They did identify its proof as a short use of established matrix-perspective, Schur-complement, and subset-polytope machinery. It therefore remains supporting structure. `research/adaptivity-prior-work.md` likewise identifies the threshold SDP/sign comparison as classical Pietsch and PSD-Grothendieck structure. Absence of an exact statement in these bounded reads is not evidence of sufficient originality.

No candidate has passed the complete correctness, originality, and significance assessment. Discovery remains open; manuscript production has not begun.

## Isolation checkpoint

This investigation has written only in `pure_math_astra`. Comparisons against its 103-file tracked baseline first found 11 changed tracked files outside the laboratory, then 15, with HEAD unchanged. The latest paths and hashes are in `isolation-checkpoint.json`. The provenance of those checkout changes was not determined here. `MATHS.md` and the other core mathematical source authorities still matched the baseline. The later `AGENTS.md` change adds campaign ownership/accounting entries and does not change this mathematical task. The laboratory does not alter or adopt those outside changes, and the checkout as a whole must not be described as unchanged.

## Finite falsification records

- `notes/description-search.json`: 108 real/complex prescribed-energy cases plus a finite search for a weighted-description failure. The later exact families supersede its approximate failure example.
- `notes/group-description-search.json`: 4,500 group instances. A ratio above the golden ratio led to the exact family proving factor-two sharpness.
- `notes/adaptive-gap-search.json`: 420 real matrices, with query-adaptive values obtained by enumerating signs. No sampled ratio exceeded the rank-one three-equal-energy example. This does not bound the general ratio.

All numerical intervals are floating-point results. They are counterexample-search aids, not exact certificates or theorem proofs.

## From sampling designs to a transform-index rate

The user again rejected treating the earlier lemmas as a novel or sufficient
result. The investigation continues under the full long-horizon objective.

The marginal equality question now has an exact answer:
notes/fixed_basis_edge_independence.md proves that attaining the diagonal
water level is equivalent to an exact-size subset law with the prescribed
marginals and pair independence on every nonzero Gram edge. Equality forces
arbitrary complex, support-dependent weights to become HT weights.
notes/two_group_parity_gap.md also gives an exact two-block parity penalty
after optimizing over the entire coefficient class.

The next result is a general local classification, written in
notes/local_basis_variance_dichotomy.md. At an eigenbasis, variance excess
under a fixed nonzero isospectral tangent direction is quadratic precisely
when a subset law can cancel every tangent edge; otherwise it is linear.
The proof reduces arbitrary near-optimal weights to an exact-size HT law
through their Cauchy defects and the positive semidefinite covariance slack.
Independent reconstruction checked the complex case and supports smaller
than the cap. For a dense direction between two eigenvalue blocks, the
quadratic case is equivalent to an integral expected read count in each
block. Constants depend on the direction; they cannot be uniform over dense
directions approaching a zero pattern.

The principal current candidate is
notes/dependence_support_transform_rate.md. For a positive spectrum, let
T contain the unordered pairs from distinct eigenspaces, let N=|T|, and
let k be the minimum number of nonzero cross-eigenspace covariances among
exact-size laws with the ideal inclusion marginals. If beta is one over
the reals and two over the complexes, the candidate proves a uniform local
comparison between variance excess and

    squared tangent size + minimum weighted tangent size over feasible pair laws.

A finite coordinate-support lemma then gives the Haar sublevel exponent
kappa=beta(N+k)/2. The original random cover gave a logarithmic factor.
The later deterministic construction in
notes/anisotropic_transform_box_cover.md removes it:

    K(epsilon) = Theta(epsilon^(-kappa)).

One common HT law works for all codewords. The note also constructs regular
grids in smooth section charts, so a codeword can be generated from chart
and grid indices. A dense stored table with K matrices is not compulsory.
This is a declared transform model, not a lower bound for unrestricted page
decoders.

notes/dependence_support_transform_rate_review.md supports the general
proof. Its initial objection to SDP attainment was withdrawn after the
reviewer read the existing complex SDP proof. The main theorem now uses
eta-optimal laws anyway, making that dependency unnecessary. Another
reviewer's objection that the coordinate-support lemma required a polytope
was also withdrawn: compactness and finitely many coordinate patterns are
enough.

The finite-library note originally used an invalid general HT covariance
simplification. That expression has been removed. Every current upper
construction supplies a legal exact-size law and its pair moments.
The corrected two-block fixed-count construction proves a quadratic bound
where expected block counts are integral; the two-coordinate linear example
does not rule out those higher-dimensional cases.

## Computed dependence-support values

The support invariant is not left entirely implicit.

- notes/q4_full_spectrum_support.md gives the complete full-covariance
  classification for four coordinates and two reads: k=2 when a pair of
  inclusion marginals sums to one, and k=5 otherwise. For simple spectra,
  the first condition is reciprocal pairing of eigenvalues about t squared.
- notes/two_block_dependence_support.md gives k=2 for three coordinates
  in each block, three reads, and marginals 3/5 and 2/5. A one-pair design
  is impossible although the count-variance bound alone permits it.
- notes/full_spectrum_covariance_support.md proves the leaf-pair rule and
  k >= q-M, where M is the maximum number of disjoint complementary
  marginal pairs. It gives sharp open simple-spectrum families with k=q
  at q=5 and q=7.
- notes/odd_cycle_q9.md extends that open-family construction to q=9.
  The all-odd-dimensional construction remains open.

programs/dependence_witnesses.py independently checks the two-block law,
one distinct-marginal five-cycle law, the positive seven-cycle law, and
its unit-determinant perturbation minor using exact rational arithmetic.
The output is notes/dependence-witness-checks.json. These finite checks
verify the stated witnesses, not the general transform theorem.

## What still prevents acceptance

The three-part assessment in
notes/dependence_support_transform_rate_assessment.md did not accept
originality or consequential application significance. It predates the
deterministic procedural cover, so its O(K) stored-table objection is not
a requirement of the latest construction. Total costs still need a declared
account: shared atlas and decoder, sampling law, index, encoded columns,
working precision, transform evaluation, and fresh bytes.

notes/finite_word_shared_transform_boundary.md provides a conditional
rational/Gaussian-rational realization and separates source bias from
sampling. Its dense-table account is one implementation, not the only
possible decoder. notes/encoded_column_rounding_bound.md gives a separate
bias-inclusive MSE bound for approximate stored columns, an approximate
query transform, and bounded arithmetic error. No native arithmetic bound
or production certificate has been established.

The closest combinatorial domain is already classical. The direct
comparison in notes/boolean_polytope_primary_comparison.md identifies
Faye--Trinh's exact-size Boolean quadric polytope as the correct predecessor;
Mehrotra's earlier formulation uses an at-most cardinality constraint.
The accessible exact-size manuscript treats affine hulls, faces, facets,
and cutting planes. It does not derive the arbitrary-weight spectral
reduction or the orbit exponent. That bounded comparison does not establish
originality. Parametric SDP and minimax sensitivity are the next direct
source challenge.

Current discriminating work is therefore:

1. finish a complete procedural-decoder cost account, including encoded
   payload and working precision;
2. test whether a general sensitivity theorem already implies the local
   comparison under its actual hypotheses;
3. extend or delimit the support invariant beyond the proved low-dimensional
   families;
4. require a fresh correctness/originality/significance assessment of the
   final candidate before any discovery closeout.

No manuscript has been started, and no candidate has passed all three
required gates. The goal remains active and unfinished.

## Decoder and sensitivity checkpoint

notes/procedural_transform_decoder.md now gives the conditional decoder
account. It uses regular grids in enlarged rational Cayley charts, while
targets lie in compact chart cores. Ordinary coordinate rounding alone is
insufficient: a uniform implicit-function argument first chooses the thin
center and a wide displacement, then rounds the thin center at scale epsilon.
The resulting index has kappa log2(1/epsilon)+O_D(1) bits with externally
declared resolution. Shared atlas, sampler, encoded payload, transform
workspace, and arithmetic are charged separately. Decoding costs O(q^3)
exact field operations at activation; evaluation with the transform retained
costs O(q^2+ps), where p is the output dimension. Forming the encoded payload
costs O(pq^2).

A fixed source word length defines a finite source class and does not inherit
the continuum asymptotic lower exponent. The note states that limitation.
Its conditional lower extension uses a rational source R0 on the fixed
spectral orbit and source precision growing as O_D(log(1/epsilon)); rational
rotations give an epsilon-net, and uniform Lipschitz continuity of Phi_s
transfers the orbit lower bound to that growing finite-word family. This
qualification is necessary, not a choice of presentation.

notes/parametric_sdp_sensitivity_comparison.md identifies a further prior-art
pressure point. A finite perspective-SDP lift and conic value sensitivity can
recover the first-order minimax derivative after the HT optimizer face is
calculated. That weakens any standalone originality claim for the first-order
reduction. The general sensitivity results read do not automatically supply
the positive quadratic branch at the degenerate diagonal optimum, the exact
dependence-support values, or the full codebook rate. A direct comparison of
the complete bridge remains open.

The next review must assess the current general theorem together with the
procedural decoder, the source-precision qualification, the rounding bound,
and the exact support classifications. It must not reuse the older explicit
table cost as a necessary objection. It also must not count an abstract
operation bound as native execution evidence. The all-odd cycle construction
and a broader structural formula for k remain mathematical questions.

This checkpoint preserves progress without accepting novelty, sufficient
significance, or a manuscript transition.

## General real query-dependent reversal and the unresolved rate question

The user again rejected novelty and sufficiency. The acceptance target is
unchanged. The new work tests the application gap and a different execution
class; it does not promote an index theorem to a paper result.

The fixed-operator four-coordinate crossover is now proved in
notes/q4_uniform_crossover_volume.md. For marginals
(a,1-a+h,b,1-b-h), the acceptable orbit volume has uniform order

    ε^(5β/2) min(√ε, ε/|h|)^(3β).

Its regimes meet at ε of order h². The proof covers the entire covariance
polygon: a neighborhood of the reciprocal matching dominates, while all
other branches contribute a smaller order. A false single-branch formula
for the full gauge is not needed. Independent review corrected the group
cover to use a stabilizer-saturated inverse-closed set and the right
translate-product order. Both corrections are in the note.

The source and cost reviews still leave that candidate short of the goal.
notes/transform_payload_frontier_obstruction.md shows that its procedural
index saves transform metadata against the declared dense-table baseline.
The mq encoded payload, ms fresh scalar traffic, and dense transform
workspace remain. The saving is lower order than the payload when m≫q
under the stated common-precision model. No total-byte frontier follows.

A more consequential distinction emerged from the query quantifier. Define

    Ψ_s(G) = sup_{||x||=1} inf_{EY=x, support(Y)≤s}
             E[(Y-x)^T G(Y-x)].

The law inside the infimum may depend on x. This differs from Φ_s, which
optimizes one random operator before any query arrives. The exact atomic
gauge and polar representation are proved in
notes/query_adaptive_atomic_dual.md.

Root first proved the real q=4,s=2 reversal in
notes/query_adaptive_basis_reversal.md. The stronger result is now in
notes/query_adaptive_general_basis_reversal.md:

- For every nonscalar real positive spectrum and every 2≤s≤q−2, an
  isospectral rotation between the largest and smallest energies decreases
  Ψ_s below the diagonal water level t by at least c|τ| locally.
- The proof characterizes all diagonal worst queries, proves strict
  pair-inclusion freedom, and controls the whole unit sphere. Improving
  only its finite sign-maximizer set would not suffice.
- The exact interval for pair inclusion z is
  [max(0,p_i+p_j−1), min(p_i,p_j,s−1−T)], where T is the sum of the
  largest s−1 remaining marginals. A weighted sum of hypersimplices
  proves both necessity and sufficiency.
- Only q+2 fixed HT laws are needed: two pair-moment laws and q marginal
  transfers. An O(q) query selector chooses one. All outcomes select
  exactly s columns from the same payload.
- This beats the mathematical optimum for a fixed unbiased random
  rank-at-most-s operator. That comparison is between execution classes;
  the fixed-rank ideal is not itself a physical s-column baseline.

notes/query_adaptive_general_basis_reversal_audit.md independently
reconstructs the general proof. It supports correctness, while judging the
extension from the four-coordinate mechanism elementary once its marginal
geometry is available. The existing primary comparison,
notes/query_adaptive_mahalanobis_primary_comparison.md, identifies the
atomic-norm and sparsification antecedents. It does not establish novelty.

notes/query_adaptive_general_finite_word_persistence.md gives a rational
source, rational plane rotation, and rational laws with a strict surviving
gap. Its mean is exactly the represented source action; random outcomes
are not exact source actions. A review requested explicit stability of the
O(q) selector after rational perturbation, since continuity of the best
catalog value alone proves existence of a selector, not that particular
selector's cost. Native rounding and physical page accounting remain open.

The important unresolved question is now quantitative:

    How small can inf_Q Ψ_s(Q D Q^T) be compared with t_s(D)?

The stress family D_η=diag(1,1,η,η), s=2, has t=√η. The question is
whether a varying basis can give o(√η), or whether a uniform lower bound
of order √η survives all bases. A fixed 45-degree paired block basis
has exactly √η; a failed transported dual witness gives no general lower
bound. Generic transverse rank-two planes have a positive obstruction.
Approaching singular coordinate-minor strata is the remaining difficulty.
The block proof and Plücker classification are in
notes/query_adaptive_q4_sqrt_eta_block.md. The critical-scale rare-event
and polar route in notes/q4_adaptive_small_eigenvalue_asymptotics.md
is explicitly unproved.

programs/adaptive_polar_probe.py implements a numerical polar support
oracle with separate primal and Lagrange-dual values, plus local query
ascent. The outer search gives witnesses, never a global upper bound.
An initial Newton stopping tolerance caused a line-search failure; it was
revised, and the diagonal benchmark returned its known water level within
the reported numerical gap. Equal paired rotations and one-block rotations
have been probed. Those calculations guide the exact question and prove
neither an exponent nor global optimality.

The two-layer analysis in notes/two_layer_independent_rank_sketches.md
also records a positive interaction term omitted by naive error addition.
It is supporting work; no universal sequential allocation theorem follows.

The finite-word review corrections are now complete. The note states
unbiasedness precisely and proves stability of its rational O(q) selector
through overlapping branch regions and a uniform bound on score
perturbations. Continuity of the best catalog value alone was insufficient
for that selector-cost claim.

The numerical paired-block conjecture now has an exact proof, recorded in
notes/query_adaptive_paired_block_all_angles.md and strengthened in
notes/query_adaptive_q4_unequal_paired_polar.md. If G is the direct sum
of two real 2×2 blocks with the same eigenvalues (1,η), then Ψ_2(G)≤√η.
Over the reals, equality holds exactly when the two normalized
off-diagonal correlation magnitudes agree. Over the complexes, equality
holds for every such pair of blocks. This field distinction follows from
the exact polar equality conditions; it is not a numerical inference.
For one k√η-rotated block and one unrotated block, the sharper bounds are

    √η − (k/2)η + O_k(η^(3/2)) ≤ Ψ_2 ≤ √η.

Thus the ratio tends to one in that scaling. This closes that structured
route to an exponent improvement.

notes/query_adaptive_sparse_null_stratum_filter.md proves a different
fixed-projector obstruction. If the kernel of a rank-two projector P is
not spanned by its at-most-two-coordinate null vectors, then
Ψ_2(P+η(I−P))≥c(P)−η with c(P)>0. In four coordinates the exceptional
fixed projectors are direct sums of two rank-one coordinate blocks, with
possible zero coordinates. This is a pointwise statement in P. A varying
P_η can approach singular principal blocks at different rates; ordinary
compactness does not transfer the bound uniformly. That multiscale
continuation remains open.

Selected numerical probe output is preserved in
notes/adaptive-polar-probe-results.json. The exact block proofs supersede
the corresponding numerical guesses. The output still carries its local
search and floating-point limitations.

The latest primary comparison found a substantial classical connection.
notes/query_adaptive_inverse_hull_design_audit.md identifies the
fixed-query inverse-hull optimization as finite multiresponse c-optimal
experimental design. That reduction is established mathematics. For
K_S=E_S G_SS^{-1} E_S^T and M=sum_S α_S K_S, the inner adaptive
second moment is inf_α x^T M^{-1}x, with the appropriate range/limit
convention. A broader fixed-linear column class has covariance
M^{-1}−G; it permits subset-dependent linear coefficient maps and
differs from the earlier diagonal-HT class Φ_s. Its optimum ν_s is
at least t, with equality precisely when (G+tI)^{-1} lies in the
convex hull of the K_S.

For the two-block family, an explicit transport mixture attains ν_s=t
at every pair of angles, while real query-dependent Ψ_s is strictly
smaller when the normalized correlations differ. This is a precise
separation between the two quantifiers, not a new experimental-design
duality.

notes/query_adaptive_subspace_containment.md states an equivalent
geometric discriminator. The transformed coordinate s-planes must satisfy

    max_S ||Proj_{G^(1/2) E_S} z||²
      ≥ z^T G(G+vI)^{-1} z for every z.

All planes come from one common invertible dictionary. The unresolved
multiscale problem can be attacked through this containment or the
inverse-hull form. Neither permits substituting arbitrary independent
planes or dropping the coefficient mean constraint.

No candidate has passed the complete correctness, originality, and
significance assessment. No manuscript has begun. All new files remain
inside pure_math_astra, and the goal remains active and unfinished.

## Continuation: uniform exceptional bounds and failure of the complex benchmark

The current objective was reread before this continuation. The user has
rejected novelty and sufficiency claims; the complete goal threshold remains
unchanged. Correct supporting mathematics does not authorize a paper.

The fixed 3+1 lower bound is now uniform in every unit three-coordinate
high vector, including vanishing coordinates. The proof in
notes/query_adaptive_3plus1_uniform_lower.md uses two explicit polar
witnesses. Independent reconstruction in
notes/query_adaptive_3plus1_uniform_lower_review.md supplies c=1/512
for Psi_2((uu^T+eta(I-uu^T)) direct-sum [1])>=c sqrt(eta).

notes/query_adaptive_exceptional_strata_tube.md extends that result to
every exceptional fixed rank-two projector, including the 2+2 strata and
their zero-coordinate boundaries. The absolute constant can be 1/800.
For G_r(P)=P+r^2(I-P), the exact square-root identity

    sqrt(G_r(P)) = r I + (1-r)P

gives G_r(P0)<=(1+K)^2 G_r(P) whenever ||P-P0||_op<=Kr. Monotonicity
of the same exact-mean adaptive problem therefore proves

    Psi_2(G_r(P)) >= r/[800(1+K)^2].

Root reconstructed this comparison and the 2+2 polar argument. The bound
removes every fixed-width-in-r tube from the search for an o(r) basis
family. It does not control distance/r tending to infinity. The fixed-P
sparse-null proof also remains pointwise; it cannot close that gap through
unqualified compactness. The exact limiting-plane note
notes/query_adaptive_subspace_limit_obstruction.md explains the active
constraints that defeat a strict-margin compactness argument.

The independent finite critical-scale calculation progressed to an exact
quadratic obstruction, recorded in
notes/critical_scale_2x2_polar_algebra.md. For K=[[a,b],[c,d]] with a,d<=0
and n=u=(1,x), the remaining polar condition has numerator A+2Bx+Cx^2.
Root derived its coefficients and the determinant identity

    AC-B^2 = det(I+K^T K) [4ad-(b+c)^2].

The negative-semidefinite symmetric-part case is settled. The indefinite
case still requires an intersection between a negative quadratic cone and
the exact coordinate-feasible interval. The rational matrix
K=[[-1,-6],[-136,-19]] has positive numerator at both feasible endpoints
and a negative interior vertex. Thus the endpoint-only shortcut is false.
No number of successful numerical searches proves the remaining lemma;
further enlargement of that search was stopped. Its candidate n=u family
is sufficient for a stronger result, not equivalent to all feasible laws.
The tube theorem already settles the uniform-order question when the
critical matrix K stays bounded. The finite lemma matters chiefly for a
sharper constant or for a justified passage through unbounded K.

A separate proposed route has now been disproved. The rank-two SDP lift in
notes/query_adaptive_rank_two_spectrahedron.md was exact, but did not prove
that complex queries restore the spectral water lower bound. The
equicorrelation family G_eta=11*+eta I_4 is a counterexample:

    Psi_{2,C}(G_eta) <= (1999/1000) eta < t_2(G_eta)
    for all sufficiently small positive eta.

The full proof is notes/query_adaptive_complex_water_counterexample.md.
Its first stage is an exact four-point planar polar formulation. The
ordinary small-eta limit has an unresolved constant-vector boundary, so a
zero-sum query calculation alone was insufficient. Root resolved that
boundary by setting z_i=1+eta w_i and defining, for mean-zero q,

    V=sum |q_i|^2,
    H=max_{i<j} (|q_i-q_j|^2+2 Re(q_i+q_j)).

Pair averaging gives H>=2V/3. The classical planar enclosing-disk bound
gives H>=3V/4-2 sqrt(V). Together they place the boundary threshold
sqrt((1-H)^2+4V)-H at most 2-9/4108. A two-case sequential argument,
separating (1-|mean z|^2)/eta bounded from unbounded, then closes the
finite-eta passage with a strict gap. The proof does not calculate an
explicit eta threshold or construct a finite-word sampler.

Two agents independently reconstructed the proof:
notes/query_adaptive_complex_water_counterexample_review.md and
notes/query_adaptive_equicorrelation_counterexample_review.md. Root made
the large-V estimate explicit by direct squaring in response to review.
The planar enclosing-disk estimate has an elementary proof in the note.
A bibliographic search verified Jung's 1901 article record; a direct
full-page fetch timed out, and the original article was not read in this
check. This is geometry attribution, not an originality assessment.

The counterexample also disproves the universal rank-two objective
certificate for the six pair-principal-inverse matrices. Every rank-two
real PSD feasible matrix has water-resolvent objective strictly below
one, while G_eta/2 is feasible with objective one. This supplies a concrete
reason that standard SDP rank reduction cannot prove the proposed
universal complex benchmark. The real-versus-complex multiplicative
variance comparison remains unresolved; the phase-rounding baseline
obstruction is preserved in
notes/query_adaptive_real_complex_comparison.md.

The next main discriminator remains the two-high, two-low spectrum under
varying bases. The counterexample has one high and three low eigenvalues.
It cannot settle that question or supply the requested Cassette resource
advance by analogy. Work should target the regime outside the proved
O(r) tubes, or derive an equally consequential obstruction or construction
under a different mathematically justified route. No claim has passed
the combined correctness, originality, and significance assessment.

Isolation checkpoint: HEAD remains
890583f6df8f79f2ee6f529a6bd690d75610ab1c. The same 15 tracked files listed
at the prior checkpoint are modified in the shared checkout. This
continuation made its writes only inside pure_math_astra. It made no
production edit, commit, push, publication, or manuscript. The goal is
active and unfinished.

## Continuation: closing the real q=4 order question

The objective was reread. The user has rejected premature novelty and
sufficiency claims. The complete goal threshold remains unchanged.
This continuation produced a new complete proof of the formerly open
varying-basis order bound; it did not accept a manuscript candidate.

Several supporting routes first became sharper. The current-inverse
certificate in notes/query_adaptive_current_inverse_minor_barrier.md
uses B_S=F_S^T(G_r)_{SS}^{-1}F_S and
Lambda=min_{||y||=1} max_S y^T B_S y, giving
Psi_2(G_r)>=1/Lambda-r^2. It avoids taking singular principal-block
limits before evaluating the constraint. Its principal-minor corollaries
remain pointwise and did not themselves close the varying-basis problem.

The zero-row argument in notes/query_adaptive_zero_row_lower_review.md
proves, for every real rank-two P with one zero coordinate row,

    Psi_2(G_r(P)) >= [sqrt(9r^4+16r^2)-3r^2]/8 >= r/4.

Its witness chooses a direction in the largest projective gap among at
most three high-frame row lines. Adding r/2 in the zero coordinate gives
a polar vector whose resolvent is explicit. This covers a larger locus
than the former exceptional strata. The same square-root comparison
extends it to a Kr tube with constant 1/[4(1+K)^2].

The triangular graph family Z_d=[[d,d],[0,d^2]] is consequently settled:
notes/query_adaptive_triangular_graph_multiscale.md combines the
zero-row tube lower r/[4(1+d^2/r)^2] with the current-kernel lower
d^2/20-r^2 and the elementary r^2 bound. It gives r/40 for every
0<d,r<=1. The previously open intermediate scaling is no longer open.

The decisive reduction is notes/exact_graph_chart_polar_bridge_review.md.
A maximum-volume row pair gives a graph chart A=[I;Z], ||Z||<=2.
For H=[[I,Z^T],[Z,ZZ^T+r^2I]] and K=Z^T/r, the finite polar constraints
on unit u and n transfer exactly to z=(u,Zu+rn). The proof gives
G_r(P)>=H/45 and an explicit block-resolvent estimate. Any universal
feasible ||n||>=rho would imply Psi_2(G_r(P))>=c_rho r/45, with
c_rho=min(rho/8,1/8). No rare-event or asymptotic passage remains.

Root proved the missing finite lemma with rho=1 in
notes/critical_scale_2x2_polar_lemma_proof.md. After coordinate signs,
write K=[[-alpha,b],[c,-delta]], alpha,delta>=0, b+c=-e<0.
The negative-semidefinite symmetric-part case was already settled.
For the remaining branch set

    w=(b-c)/2, z=delta-alpha, sigma=alpha+delta,
    k^2=e^2/4-alpha delta>0, D=det K=w^2-k^2.

The n=u=(1,x) candidate is coordinate-feasible exactly when
h=(1-x^2)/(2x) lies in [w-e/2,w+e/2]. The ellipsoid numerator, divided
by 1+x^2, is

    -sigma(1+D)
    + ([z(1-D)-2ew]h - 2wz - e(1-D))/sqrt(1+h^2).

When D>=-1, h=w makes it strictly negative. When D<-1, put L=-1-D
and clip h=-z/e to the feasible interval. The interior value is
L sqrt(z^2+gamma)-(L+2)sqrt(z^2+e^2)<0, where
gamma=4alpha delta. At the lower clipped endpoint h=-v, v=e/2-w,
the scaled expression f(z) has f'(z)<0 on z>=ev. The exact condition
gamma>=0 gives L<=ev-v^2-1<ev, which proves the derivative sign;
at z=ev the interior formula is already negative. Coordinate exchange
settles the upper clip. The construction normalizes to ||u||=||n||=1.

Independent reconstructions are in
notes/critical_scale_2x2_scalar_n_equals_u_review.md and
notes/critical_scale_2x2_polar_lemma_independent_review.md. The latter
also reconstructs the graph transfer, including inverse sign changes,
single-support domination, the Loewner comparison, and all 0<r<=1.
A proposed sine/cosine labeling objection was checked and withdrawn:
with x=tan(theta), the original coefficient order is correct. The proof
now states that parametrization explicitly.

The resulting theorem is

    r/360 <= inf_{rank P=2, P real orthogonal on R^4}
             Psi_2(P+r^2(I-P)) <= r.

The upper law in a diagonal basis chooses the two high coordinates with
probability 1/(1+r), or the two low coordinates with probability r/(1+r),
and rescales by reciprocal probabilities. Its risk operator is r I_4.
Thus arbitrary varying real bases cannot yield o(r). This closes the
specific two-high, two-low order question. It does not identify the best
constant, establish originality, or give a general representation or
page-access lower bound.

## Continuation: a stronger complex gap and a growing finite-word family

The separate one-high, three-low equicorrelation calculation improved
from 1.999 eta to 1.89 eta. The supporting proof is
notes/query_adaptive_equicorrelation_boundary_rank_bound.md, with
independent reconstruction in
notes/query_adaptive_equicorrelation_boundary_rank_review.md.

For mean-zero complex q=a+ib, write B=aa^T+bb^T, V=tr B,
H=max_{i<j}(|q_i-q_j|^2+2(a_i+a_j)), and epsilon=H-2V/3.
The exact pair-slack identity writes
B=(H/2)P-2P Diag(a)P+(1/2)PEP. Rank B<=2 then gives
V/sqrt(2)<=sqrt(3H^2/4+2V)+3sqrt(2)epsilon.
Assuming the boundary threshold sqrt((1-H)^2+4V)-H>=1.89
forces epsilon<=22V/867-89/200. Substituting that upper bound
and squaring positive sides yields a polynomial with all positive
coefficients, contradicting the rank inequality. The planar tail
estimate and compactness make the gap uniform. The already reviewed
finite-eta passage consequently gives Psi_{2,C}(11*+eta I)<=1.89 eta
for sufficiently small eta.

The finite-catalog bridge in
notes/query_adaptive_finite_catalog_bridge.md converts an arbitrary
fixed positive Gram's adaptive laws to a finite rational catalog of
individually operator-unbiased laws, with any prescribed additive risk
tolerance. Its construction extends a finite fixed-query law to a linear
mean-identity law, covers the query sphere, rationally perturbs its
probabilities and coefficients, and corrects each mean row exactly.
Repeated identical four-coordinate blocks share one catalog; no product
catalog of exponentially many outcomes needs to be stored. Its size and
coefficient precision are finite but not numerically bounded here.

notes/finite_word_growing_static_adaptive_separation.md assembles an
exact-Gram Hadamard construction: q=4m, a shared catalog uses 2m columns
with risk<=1.9 eta, and every allowed static common unbiased linear law,
after a resident matrix from a fixed b-bit interpreter, needs more than
(2+1/50)m columns. The finite-codebook quantifiers and dyadic construction
are reconstructed in
notes/finite_description_codebook_lower_bridge_review.md and
notes/finite_word_growing_static_adaptive_separation_review.md.
Source-trained encoders and decoder parameters are covered when all
source-dependent state is charged to the finite interpreter word. A free
source-dependent decoder would change the quantifiers.

The extension in
notes/rademacher_source_growing_static_adaptive_extension.md replaces
the Hadamard shared-row signs by independent signs in a dyadic matrix U.
For delta=1/16 and zeta=1/256, simultaneous finite-codebook avoidance
and near-isometry follow from

    2 exp[b log2+(t+2q)log9-p delta^2/8]
    +2 exp[t log9-p zeta^2/576] < 1,

with t=5m and p a power of four. The second estimate uses a scalar
Bernstein moment bound and a quadratic-form quarter-net, so p=O(m+b)
suffices. The actual source Gram lies between (1-zeta)G and
(1+zeta)G. Every decoded residual Gram is at least
aG, a=1-zeta-delta^2=127/128. The adaptive risk is at most
c eta, c=(19/10)(1+zeta)=4883/2560, while the static trace lower gives

    s/m >= a(4+eta)/(a(4+eta)+c eta)+3a/(a+c)
         > 2+1/50     (eta<=1/100).

Root reconstructed the probability, complexification, Loewner, and exact
fraction steps in
notes/rademacher_source_growing_static_adaptive_review.md.
For fixed sufficiently small dyadic eta, a sufficiently large
b=O_eta(log(m+2)) and p=O_eta(m) can satisfy the construction and hold
the shared catalog plus regular addressing records. The constants do not
give numerical resident bytes. Neither source construction proves a lower
bound for nonlinear computations outside the span of fetched columns.

The bounded primary comparison is
research/growing_static_adaptive_separation_prior_work.md. It identifies
established unbiased compression, classical multiresponse c-optimal
design, compactness/rational approximation, and finite-class net arguments.
The adaptive-information literature uses a different unknown-input
measurement model; this theorem's query is already supplied. The primary
article attribution was corrected to Krieg, Novak, and Ullrich against
the tool-visible article. The search did not establish originality of
the exact conjunction and did not exhaust matrix-data-structure,
communication, or restricted-oracle lower bounds.

The separate adversarial assessment is
notes/finite_word_growing_static_adaptive_significance_assessment.md.
It accepts correctness within the declared column-linear class. It does
not accept originality or sufficient Cassette significance. Its initial
stale correctness status and quadratic-dimension limitation were corrected
against the independent reviews and Rademacher extension. A narrow
execution theorem need not solve unrelated certificate fields; the real
remaining limitations are the source/comparator class, explicit catalog
and selector accounting, and the consequence for a declared physical
source-access format. Standard amplification of a four-dimensional gap
is not, by itself, evidence of a substantive original advance.

The next active mathematical targets are the six-coordinate, three-read
case (including the K4 cut/cycle projector), and the exact higher-dimensional
graph-chart finite lemma. The completed q=4 theorem must not be reopened
as if only numerical evidence existed. Quantitative catalog construction
and a broader, physically declared execution consequence remain separate
open routes. No manuscript has begun.

Isolation checkpoint: HEAD is
890583f6df8f79f2ee6f529a6bd690d75610ab1c. The same 15 tracked paths from
the prior checkpoint remain modified in the shared checkout; this record
does not assign their provenance or call the checkout unchanged. This
continuation wrote only inside pure_math_astra. It made no production
edit, commit, push, or publication. The complete goal remains active
and unfinished.

## Continuation: the fixed-projector dichotomy in every dimension

The higher-rank investigation produced a complete fixed-projector
classification, while leaving the moving-projector problem open.
The proof is notes/fixed_projector_sparse_kernel_dichotomy.md and the
independent reconstruction is
notes/fixed_projector_sparse_kernel_dichotomy_independent_review.md.
Root also reconstructed the complete argument and incorporated the
reviewer's empty-support convention.

For a fixed real rank-k projector P on R^{2k}, define

    W = span{ker P intersect R^S : |S|<=k}.

Here a singular support means that P restricted to its coordinate space
is noninjective, equivalently P_SS is singular. A support of size below k
may be injective despite its proper image; those meanings are not
interchangeable. The theorem is

    W=ker P  => Psi_k(P+r²(I-P)) and nu_k(P+r²(I-P)) are Theta_P(r);
    W!=ker P => both values are Theta_P(1).

The lower bound in the first branch uses a unit high vector u at positive
distance d from all singular-support images and a finite inverse bound M
on all nonempty injective supports. Put mu=max(1,M), a=(1+16mu²)^(-1/2),
b=4mu a, and choose x=au+bn with n a unit kernel vector. A law of small
risk V can visit singular supports with probability at most V/(a²d²).
Its injective outcomes carry less than half the required kernel mean.
Eventwise Cauchy-Schwarz then gives

    V²+r²b²V >= r² a²d²b²/4.

This proves c_P r for arbitrary query-dependent exact-mean coefficient
laws. Infinite-risk laws are trivial; finite risk gives all required
second moments. The zero output satisfies the injective inequality
without entering the maximum of nonzero-vector quotients.

For the upper bound, volume sample a full-rank k-subset S of a
row-orthonormal high frame A, with probability det(A_S)². The output
H_S x=E_S A_S^(-1)A x preserves Px in every outcome and has mean Px.
The cofactor identity gives E||H_Sx||²<=(k+1)||Px||², including
singular coordinate subsets by omitting their positive-semidefinite
cofactor contributions. A finite sparse basis of the kernel supplies a
second linear law with mean (I-P)x and finite second moment. Mix the
rescaled outputs rather than adding them. Probability of order r balances
the high-space error against r² times the low-space second moment.
Every resulting operator has at most k nonzero rows and mean I.
Its probabilities are independent of the query, so it bounds nu_k as
well as Psi_k. An earlier statement limiting this construction to
query-dependent laws was corrected.

If W is proper, choose unit n in ker P orthogonal to W. On every
allowed coordinate support the functional <n,y> factors through Py.
The finite support family therefore gives |<n,y>|<=C||Py||.
At the query n, exact mean forces E||PY||²>=1/C², independently of r.
A fixed coordinate-sampling law supplies the finite upper bound.
The two branches include k=1 and the case with no singular supports.
Their constants depend on P; compactness has not made them uniform.

The K4 cut/cycle stratum supplies a concrete connected example.
notes/k4_cut_space_q6s3_order_r_lower.md gives r/1024 through a
mixed cut-cycle polar witness. The independent root reconstruction is
notes/higher_rank_support_and_chart_review.md. The alternative event
proof in notes/k4_cut_space_support_split_lower.md has explicit
distance d=1/sqrt(3) from triangle images and forest inverse bound M=4.
The four unit triangle cycles form a tight frame:
sum_i c_i c_i^T=(4/3)(I-P). The resulting kernel law has second moment
3||(I-P)x||². Mixing it with the volume high law at probability
r/(1+r) gives the explicit upper nu_3<=7r, and hence Psi_3<=7r.

Root's additional consequence is
notes/k4_diagonal_and_full_linear_rate_separation.md. In the original
six edge coordinates, all diagonal entries of G_r equal (1+r²)/2.
Any common diagonal coefficient law with mean I and hard support three
has trace risk at least six times that value, by its marginal
probabilities and Cauchy-Schwarz. Uniform three-subset sampling supplies
the upper, giving

    (1+r²)/2 <= Phi_3(G_r) <= 3/5+2r²/5,
    Psi_3(G_r)=Theta(r),  nu_3(G_r)=Theta(r).

The independent dichotomy review also checks this arithmetic. Thus full
linear retained coefficients change the error order in this fixed
representation; query-selected laws are not needed for that change.
A free orthogonal re-encoding would change the diagonal comparison.
This is not a universal source-access or representation lower bound.

The bounded primary ingredient check is
research/fixed_projector_volume_sampling_prior_work.md. It reads
Dereziński and Warmuth, Reverse Iterative Volume Sampling for Linear
Regression, JMLR 19 (2018), Theorems 5 and 6 and their proofs.
The exact projector mean and second-moment inequality are established
volume-sampling results. Their upper inequality requires no full-spark
hypothesis; the all-subsets-positive condition supplies equality.
No originality inference about the full dichotomy follows from this
ingredient check.

The next uniform target is stated exactly in
notes/rank_k_graph_chart_reduction.md. For each real k-by-k K, seek
unit u and n with a uniform ||n||>=rho_k>0 satisfying, for every
E,J subset [k] of equal size j,

    (n_J+K_EJ^T u_E)^T (I+K_EJ^T K_EJ)^(-1)
      (n_J+K_EJ^T u_E) <= ||u_E||².

All mixed-support and singular-minor reductions are exact. Root checked
the conditional graph and resolvent transfer, which would give

    Psi_k(P+r²(I-P))
      >= rho_k r/[4(k²+2)(1+k²)(1+2k²)]

uniformly over real rank-k projectors if that finite lemma holds.
It is proved at k=2 by the completed scalar argument and remains OPEN
at k>=3. The fixed-P dichotomy supplies no uniform bound on its
degenerating constants.

The new results are supporting mathematics with independent correctness
checks. The global q4 theorem and full fixed-P dichotomy still need their
own careful originality and significance assessment. The separate
finite-word growing-gap assessment remains unpassed on those two
questions. No manuscript or production change has been made. The full
goal remains active and unfinished.

The next rank-three shortcut already has an exact counterexample:
notes/rank_three_proper_submatrix_obstruction.md uses
K=[[1,2,0],[1,2,0],[0,0,0]], u=(-1,-1,1)/sqrt(3), and
n=(1,0,0)/sqrt(3). All scalar boxes and the full ellipsoid pass, but
the E=J={1,2} constraint is 25/33>22/33. This does not refute the
finite lemma; it prevents dropping the proper submatrix constraints.

## Continuation: rank-one charts, all skew three-by-three charts, and bounded sampling

This continuation remains discovery work. No result has passed the combined
correctness, originality, and sufficient Cassette significance assessment.
The previously proved global real four-coordinate theorem and fixed-P
dichotomy are not treated as authorization to begin a manuscript.

The finite rank-one lemma is now proved in every dimension:
notes/rank_one_finite_k_polar_lemma.md, independently reconstructed in
notes/rank_one_finite_k_polar_lemma_independent_review.md. For K=ab^T,
||b||=1, use w_i=1/(1+|a_i|), R=||w||,
u_i=-sgn(a_i)w_i/R, and n=b/sqrt(k). The zero matrix is included by
taking a=0 and an arbitrary unit b. Every E,J constraint reduces by
Sherman-Morrison to an interval centered at Q/R, with radius
W sqrt(1+A)/R. Here A=||a_E||², W=||w_E||, and
Q=sum_E |a_i|w_i. Cauchy-Schwarz makes its lower endpoint nonpositive;
Q+W sqrt(1+A)>=1 and R<=sqrt(k) put 1/sqrt(k) below its upper endpoint.
This proves rho_k=1/sqrt(k) for all rank-at-most-one K, including every
proper submatrix. The graph consequence has coefficient
1/[4 sqrt(k)(k²+2)(1+k²)(1+2k²)], with a further factor
(1+K0)^(-2) in a projector tube of radius K0 r.

notes/rank_two_partial_monomial_polar_subcase.md preserves the elementary
rank-two subcase with disjoint active rows and columns. An inactive column
gives n=e_j/sqrt(3), while u has equal coordinates. Its diagonal inverse
calculation does not extend to correlated rank-two factors.

The correlated skew case has now been proved in full:
notes/rank_two_general_skew_polar_lemma.md. It supersedes the equal-entry
cycle subcase in notes/rank_two_skew_cycle_polar_lemma.md, whose independent
review remains notes/rank_two_skew_cycle_polar_lemma_independent_review.md.
Every real skew 3-by-3 K can be normalized by signed coordinate permutations
and K -> -K to cyclic entries a>=b>=c>=0. Put
gamma=sqrt(1+c²), beta=sqrt(1+b²), s=c+gamma, z=b+beta.
The raw witness is u=(1,-s,-z), n=(1,-s,z), normalized by their common
norm. Both resulting vectors have norm one.

All nine scalar boxes follow from s²-1=2cs and z²-1=2bz.
The nine proper two-by-two determinant gaps have explicit nonnegative
formulas. Most cancel to low-degree factors; the hardest gap, E=23,J=13,
becomes a nonnegative quadratic in d=a-b:

    4bz d² + 2z[gamma+(s+4)b²+bcz]d
    + b²(s²+z²-2) + 2bz gamma(1+s) + 2s b³z + 2b²c z².

The full gap numerator is 4z gamma(a+bs), also nonnegative.
This is an algebraic proof for all finite parameters, including zero
entries and arbitrarily large matrices. It does not rely on a numerical
search or on continuity from a bounded parameter grid.

Two independent algebraic reconstructions support this proof:
notes/rank_two_all_skew_polar_lemma_independent_review.md uses the quotient
relations s²-2cs-1=0 and z²-2bz-1=0;
notes/rank_two_general_skew_polar_algebra_certificate.md gives a separate
Laurent-polynomial reconstruction and the compact positive table.
programs/skew3_proper_gap_certificate.py deterministically checks the
attached notes/rank_two_general_skew_proper_gap_coefficients.json and
all compact identities after denominators are cleared. Root reran that
exact check successfully. The expanded certificate has 470 positive
monomials after common factors are removed; the short identities are
the main proof. The earlier expansion-only review is preserved in
notes/rank_two_general_skew_polar_algebra_review.md.

Thus rho_3=1 on all real skew matrices. The existing graph transfer gives
Psi_3(P+r²(I-P))>=r/8360 for rank-three projectors whose maximum-volume
chart is skew, uniformly even when those skew charts vary with r.
notes/rank_two_coordinate_preserving_skew_reduction_obstruction.md shows
why this does not solve general rank-two K: a full-support rank-two matrix
cannot acquire a zero diagonal under monomial row/column changes, and the
finite graph pivots do not cover its eight-dimensional parameter locus
with a three-dimensional skew family. The remaining rank-two normal form
is K=[[A,Ax],[y^T A,y^T A x]], with A invertible 2-by-2 and x,y in R².

Two failed general shortcuts are now explicit.
notes/uniform_rank_k_support_threshold_obstruction.md proves the support
event lower bound uniformly when both injective singular values and
distances from singular support images have uniform positive bounds.
But the frame [I;epsilon I]/sqrt(1+epsilon²) has an injective low support
with a small singular value whose image is the whole high space. Thus a
small-singular-value support need not force any high-space displacement.
This refutes the proposed event estimate, not the desired uniform theorem.

notes/finite_polar_trace_obstruction_to_quadratic_sprocedure.md records a
different limitation. Every square-submatrix polar inequality has a
trace-zero joint quadratic matrix. A nonnegative multiplier certificate
for ||n||²<=rho²||u||² with rho<1 would therefore have negative trace
while being positive semidefinite. The basic lifted relaxation always has
the feasible moment I_(2k)/k, with equal u and n traces. This prevents
that relaxation from refuting rho=1. It supplies no rank-one witness:
explicit coupled quadratic forms can have the same trace property and
an arbitrarily small feasible norm ratio. The special coupling between
submatrices of one K remains the mathematical issue.

The fixed-P dichotomy now has a bounded provenance assessment:
research/fixed_projector_sparse_kernel_dichotomy_provenance_and_significance.md.
Its short sparse null generators are exactly the represented matroid's
circuit vectors with support at most k. Circuit decomposition and the
volume-sampling mean/moment identities are established ingredients.
No checked source supplied the complete small-r support-event dichotomy,
but this finite comparison does not establish its originality or rule out
a routine derivation from existing frameworks.

The K4 consequence is now finite and quantitatively declared.
notes/k4_dyadic_full_linear_page_accounting.md gives sixteen integer tree
prototypes and four integer cycle prototypes, a 1440-bit literal shared
table, dyadic sources with r=2^(-ell), and an exact twenty-map law.
Its rejection sampler has only an expected random-bit bound.
Root removed that limitation in notes/k4_bounded_bit_full_linear_sampler.md:
use H_T with mass 1-2r, 2H_T with mass r, and C_f/r with mass r,
uniformly within the sixteen-tree or four-face branch.
The mean is exactly I. Every map has three nonzero rows and integer
entries. The exact sampler uses at most ell+4 fair bits per block.
Its risk is at most

    (2r+3r²+6r³)||Px||² + (3r-r²)||(I-P)x||² <= 5r||x||².

The m-block product uses 3m columns, at most m(ell+4) random bits,
and the same shared twenty-prototype table with integer scales 1,2,2^ell.
For a diagonal mean-I law with expected support sbar and residual Gram
at least a times the block metric, trace averaging gives risk at least
a(1+r²)/2*(6m/sbar-1). Matching 5r requires

    sbar >= 6m/[1+10r/(a(1+r²))].

Under the explicitly declared original-column page format, its expected
fresh traffic divided by the full law's traffic is therefore at least
2/[1+10r/(a(1+r²))], tending to two as r decreases to zero.
notes/k4_dyadic_full_linear_page_accounting_independent_review.md reconstructs
both samplers, the moment bounds, metadata, diagonal trace inequality, and
conditional finite-interpreter lift. The format is deliberately dense and
the comparator remains restricted. A source-dependent procedural decoder,
an uncharged basis change, arbitrary page encodings, native arithmetic,
and a universal Cassette resource frontier are not covered.

Next discriminators: resolve the general rank-two finite system without
discarding proper minors; determine whether subset coupling yields a real
rank-one witness beyond the trace-blind relaxation; and test the strongest
surviving theorem against closer primary results and a sufficiently
consequential application class. Correctness of the new subcases does not
settle novelty or significance. The goal remains active and unfinished.

Isolation and retrieval check for this continuation: HEAD remains
890583f6df8f79f2ee6f529a6bd690d75610ab1c. Git reports the same fifteen
tracked modified paths observed at its start, plus the two existing lab
directories. This is a path/status observation, not an assertion that
other tasks' file contents were unchanged. All writes in this continuation
were under pure_math_astra. Eighteen selected notes and index files passed
math-delimiter nesting, environment nesting, local-link, and whitespace
checks after malformed bare math commands were repaired. The exact skew
coefficient check passed; no production suite or runtime was invoked.

## Continuation: nonlinear oracles, finite advice, and generic rank-two rays

The objective was reread before continuing. The user rejected novelty and
sufficiency claims and reiterated the long horizon. No result has passed
the originality and significance gates; no manuscript has begun. The work
below remains supporting mathematics and candidate development.

The bounded primary comparison in
research/q4_query_adaptive_barrier_prior_art_comparison.md reads the
unbiased-sparsification, k-support-norm, and rotated mean-estimation
predecessors. It identifies established ingredients without establishing
priority for the exact real four-coordinate lower bound.
notes/q4_and_finiteword_cassette_significance_assessment.md gives the exact
execution identity yhat=Bx+RZ, EY=x, and the conditional q=4 consequence
epsilon_exec²>=r/[720(1+r²)] when R^T R=P+r²(I-P), B=0, and ||x||=1.
It also identifies the finite-word growing gap as a resource consequence
within a declared execution class. Its actual source, finite catalog,
page, and composition accounts remain to be supplied. A reviewer initially
treated a frontier over every legal encoding as mandatory. That invented
requirement was corrected: a significant result under assumptions Cassette
can actually satisfy may qualify under the objective. This correction does
not accept any current result or reduce the originality requirement.

### Arbitrary nonlinear output in a fixed-Gram oracle

notes/gaussian_static_oracle_first_chaos_reduction.md establishes the
Gaussian projection route for a static support law chosen before source
and query. An initially proposed Haar average was not pointwise justified
by Gaussian L² alone. Finite row signed-permutation averaging repairs it;
Gaussian first-chaos projection then yields column-linear coefficients and
the inverse-hull program. These are established methods, as recorded in
research/gaussian_static_oracle_primary_method_comparison.md.

notes/gaussian_static_nonlinear_oracle_minimax_gap.md and its independent
review give the all-source normalized minimax comparison using
Gamma_G(A)=||AG^(-1/2)||op² and the Gaussian norm bound. They retain
their scope, but a cleaner orbit argument now removes the normalization
loss from the growing-gap consequence.

notes/fixed_gram_orbit_static_oracle_minimax_independent_proof.md proves
the exact identities on the whole real orbit O_G={A:A^T A=G}, p>=q:

    static hard-cap nonlinear oracle value = nu_s(G);
    query-dependent hard-cap nonlinear oracle value = Psi_s(G).

The support law is independent of A, and the decoder has no source-trained
resident state. A finite uniform risk bound makes O(p)-Haar averaging
pointwise legitimate. Equivariance, the observed-frame stabilizer, and
transitivity force the averaged output to A_S c_S(x), with coefficients
independent of A. Exactness gives sum p_S E_S c_S=x. The fixed-law optimum
is x^T(M^(-1)-G)x, where M=sum p_S E_S G_SS^(-1) E_S^T. For query-dependent
schedules, lower-bound each fixed query first; a finite quadratic catalog
with a Borel selector supplies the matching upper infimum. The hard-cap
identity is separate from the expected-read trace inequality.

notes/fixed_gram_orbit_nonlinear_oracle_reduction_independent_review.md
reconstructs both identities. Root caught and corrected an overstatement
in the review: Haar averaging bounds risk by the orbit average and then
the supremum, not by the original decoder's risk at each individual A.
The full O(p) orbit is essential. On SO(2), one observed column determines
the second by the fixed 90-degree rotation.

notes/fixed_gram_oracle_adaptivity_separation.md and
notes/fixed_gram_oracle_adaptivity_corollaries_independent_review.md combine
these identities with the existing adaptive constructions. Granting the
static decoder a free fixed right orthogonal basis gives exact benchmark
t_s(G): spectral water is the invariant lower bound, and an eigenbasis
size-s Horvitz--Thompson law attains it. Thus the earlier real basis-reversal
theorem becomes a strict oracle improvement for every nonscalar spectrum
at q>=4 and 2<=s<=q-2, even against arbitrary nonlinear static outputs.

For G=(11^T+eta I_4) in m blocks, fixed sufficiently small eta<=1/100,
the shared finite real catalog has hard cap 2m and risk <=1.9 eta. Every
static nonlinear oracle attaining that risk on the entire orbit, even
after a free fixed right basis, requires expected reads satisfying

    sbar/m >= (4+eta)/(4+2.9 eta)+30/29
           >= 4010/4029+30/29
            = 237160/116841 > 101/50.

The exact excess over 101/50 is 57059/5842050. Here p=q is allowed.
The lower quantifier is for every competing decoder there exist a source
and unit query; it does not produce one common hard source for all
decoders. This oracle theorem and the earlier finite-word trained-linear
theorem are incomparable.

The trained-schedule boundary is constructive. For A in O(2), select
column 1 when det A=1 and column 2 when det A=-1. The selected index and
column reconstruct A=[a,Ja] or A=[Jb,b] respectively. One source-dependent
index therefore defeats the source-independent lower theorem. Any attempt
to include trained schedules must account for this information.

research/fixed_gram_orbit_invariant_method_comparison.md reads the compact
Haar/Hunt--Stein precedent and primary information-based-complexity work.
The averaging, stabilizer argument, and quadratic optimization are standard
machinery. Their use here is not an originality finding. The exact
all-orbit unbiased random-support coupling and the assembled adaptive
consequence still need a closer statement and significance assessment.

### Finite trained advice: a separate lower bound

notes/finite_advice_stiefel_orbit_lower.md now allows the source to choose
one of N measurable advice cells on the rectangular orbit A^T A=I_q,
p>q. The state may decode an arbitrary resident matrix or function. Its
support law is fixed within the label and before the query; its output may
be nonlinear and even biased. A label-specific fixed right orthogonal
basis is also allowed. With every label's expected reads <=sbar<q, put
d=1-sbar/q and H_q=q*2^(q-1). Uniform squared risk C obeys

    C >= d*(N H_q sqrt(p))^(-2/(p-q)).

For hard cap s<q, replace d by 1-s/q, H_q by
H_(q,s)=q*sum_(k=0)^s binom(q-1,k), and the denominator exponent by p-s-1.
Root strengthened an earlier bound that lost a factor 2^q outside the
exponent. Summing risk over coordinate queries forces some missing
support-coordinate pair to have small error at each source. The pair may
vary with the source; a union over labels and pairs is therefore required.
Conditioned on the observed frame, the missing column is uniform on a
complement sphere, and each decoder prediction covers at most one small
cap. This proves the displayed lower. The right-basis extension uses the
coordinate queries of each label's basis and invariance of the whole orbit.

notes/finite_advice_stiefel_orbit_lower_independent_review.md reconstructs
the proof, cap bound, zero-error case, support count, basis extension, and
nonattainment-safe quantifier. Query-dependent schedules do not preserve
the omitted-coordinate mass identity. At p=q=2 the remaining sphere has
only two points, recovering the orientation-bit exception.

For N=2^b and fixed q, beating a fixed fraction of d requires b growing
linearly with p-q. This is a real finite-advice obstruction, but it does
not retain the exact-mean coupling that yields spectral water. It therefore
does not extend the 1.9 eta adaptive separation to trained nonlinear
decoders. That stronger lower remains open.

### Generic rank-two directions now cover all three sign cases

notes/rank_two_factor_exact_subset_reduction.md and its independent review
retain the exact two-dimensional support equations for K=AB^T, B^T B=I.
Writing n=Bv+zh exposes all scalar boxes, nine proper complement
ellipsoids, and the full ellipsoid. It also disproves the simultaneous
ansatz v=-A^T u and u in ker A^T using a zero row of A. The exact
J-dependent matrix cannot be replaced by the identity.

notes/rank_two_sign_consistent_inverse_pivot.md proves a generic rank-two
sign pivot, but the admissible pivots need not contain a perfect matching.
In normalized sign case A the only pivots are (1,2),(2,1). Correctly unit
kernel vectors g_epsilon and h_epsilon give a family where every admissible
ratio |g_i|/|h_j| tends to zero. An earlier illustrative h vector had the
wrong normalization for this norm comparison; it was replaced by the
separately normalized family. The sign lemma survives, while the proposed
single-pivot norm inference fails.

Root derived a shared proper-inverse identity. Let M=D_g K D_h have zero
row and column sums, alpha=D_g u, beta=D_h n, and sum beta=0. If M^T v=beta,
then for complementary E,J with deleted row i,

    alpha_E^T M_EJ^(-T) beta_J
        = sum_(ell!=i) alpha_ell*(v_ell-v_i),

independently of the deleted column. If sum alpha=0 as well, every proper
pairing is the same scalar alpha^T v. This makes constructions using
several coordinates tractable without discarding proper constraints.

notes/rank_two_case_a_asymptotic_multisupport.md uses small zero-sum
perturbations of alpha=(1,0,-1), beta=(0,1,-1). All scalar first corrections
are negative; every proper pairing and the full pseudoinverse pairing are
the same negative scalar. The vectors may be separately normalized to unit
norm. Hence one witness works for every sufficiently large dilation tK.

notes/rank_two_generic_direction_asymptotic_case_b.md uses beta=(0,1,-1)
and alpha=(1,-1,epsilon). The three possible proper pairings are strictly
negative, the nonzero scalar products have the required signs, and the
full limiting gap is strict because h^T n=0 but g^T u is nonzero. Both
witness norms are one; all support sizes are included.

Root completed case C in notes/rank_two_case_c_asymptotic_pivot.md. Its
positive entries form a matching, so some matching pair has |g_i|>=|h_j|
for unit kernel vectors. Place it at (1,3), choose alpha=(-1,epsilon,epsilon)
and beta=e_3, normalize u to one and n to one half, and take epsilon small.
Six explicit proper inverse numerators are negative; the remaining proper
supports contract exactly because n_J=0. The full limiting gap follows
from |g^T u|>(3/4)|g_1|>|h_3|/2=|h^T n|.

notes/rank_two_generic_ray_polar_independent_review.md recomputes the
six numerators and the matching, scalar, proper, and full arguments.
The combined theorem is:

    For every fixed real rank-two 3-by-3 K with nonzero entries and
    nonzero two-by-two minors, there are u,n and a finite T(K) such
    that ||u||=1, ||n||>=1/2, and all finite-three-polar constraints
    for tK hold for every t>=T(K).

The norm floor is common to these generic directions. The threshold is
not. Entry-zero and minor-zero limits, loss of rank, and moving directions
can still make the required threshold diverge. This theorem does not close
the uniform finite three-polar lemma or its moving-projector consequence.

Next discriminators: control the generic-ray thresholds near degenerating
rank-two directions, or construct a genuine moving-direction counterexample;
retain exact-mean constraints in a lower bound with finite trained nonlinear
advice; and identify a substantive intellectual step beyond the closest
primary results together with a realizable, consequential Cassette plan.
The discovery goal remains active and unfinished.

Isolation and retrieval check: all writes in this continuation remained
under pure_math_astra. HEAD is 890583f6df8f79f2ee6f529a6bd690d75610ab1c;
Git still reports the same fifteen tracked modified paths and the two
existing laboratory directories. This is a status/path observation, not a
content-equality claim about other tasks' changes. The data volume had
142 GiB free at the check. Twenty selected mathematical/source notes and
both retrieval files passed math-delimiter nesting, environment nesting,
local-link, and whitespace checks after small formatting repairs. The two
new exact read-gap fractions were checked with rational arithmetic. No
production code, production tests, runtime, commit, or publication was used.

### Further boundary work: one column may remain bounded

The investigation continued after the preceding checkpoint. Root proved
an exact uniform finite-polar subcase in every dimension, recorded in
notes/zero_column_finite_k_polar_lemma.md. If K has a zero column j0, choose
one unit normal to the column space of each square submatrix containing
j0. There are L=binom(2k-1,k) such pairs. For a signed sum v maximizing
its squared norm, a one-sign flip gives sigma_i*w_i^T v>=1. Thus the
normalized u has distance at least 1/L from every relevant column space.
Set n=e_j0/L. The polar quadratic splits exactly into ||n_J||² plus the
contractive column-space term; the distance supplies the missing amount.
All submatrix ranks and all entry magnitudes are covered. Independent
reconstruction is in
notes/zero_column_finite_k_polar_lemma_independent_review.md.

The argument extends to a nonzero column of norm at most C, with all
other columns arbitrary. Remove the distinguished column from each block
and apply the signed-sum argument to the remaining column space. If D
contains those columns, b is the distinguished column, and

    R=(I+DD^T)^(-1), U=u_E^T R u_E, B=b^T R b, m=b^T R u_E,

then U>=1/L², B<=C², and |m|<=sqrt(U B). The exact Schur-complement
formula for n=tau e_j0 is

    polar value = ||u_E||²-U+(tau+m)²/(1+B).

Every legal interval for tau therefore contains the same symmetric
interval of radius 1/[L(sqrt(1+C²)+C)]. Choosing its positive endpoint
gives a uniform witness for all constraints. The proof and its singular
blocks are independently reconstructed in
notes/bounded_column_finite_k_polar_independent_review.md. This covers
moving matrices with one bounded column; it leaves sequences with every
column norm diverging unresolved.

research/zero_column_polar_signed_sum_prior_work.md reads Bang's 1951 AMS
paper and Ball's 2001 Lemma 5. The signed-sum step is precisely the
equal-weight form of standard Bang lemma. The submatrix application and
Schur complement are short uses of established techniques. Their absence
as a verbatim statement from those papers supplies no substantive novelty
finding and does not meet the original-advance goal by itself.

Root then avoided the general graph-comparison losses in
notes/zero_coordinate_projector_uniform_polar_bound.md. For any real
rank-k P on R^(2k) with P e_j0=0, choose a high-space unit u separated
from the row spans of every (k-1)-row frame restriction. With c=1/L,
z=V u+c r e_j0 is a legal polar vector, and

    z^T(G_r(P)+vI)^(-1)z = 1/(1+v)+c²r²/(r²+v).

The positive root v_r satisfies v_r²+(1-c²)r²v_r-c²r²=0. Combining its
lower bound with Psi_k(G_r(P))>=r² yields the uniform result

    Psi_k(P+r²(I-P)) >= r/sqrt(2L²-1),  0<r<=1.

At k=3 this is r/sqrt(199). If P is within C r in operator norm of a
projector with a zero coordinate, the lower bound loses only (1+C)².
The square-root triangle inequality proves this comparison directly.
For delta=||P e_j||<1, replacing its one tilted high-space direction by
its projection into e_j-perp gives such a projector at exact distance
delta. Finally, a graph matrix K=Z^T/r with one column of norm at most C
has ||P e_low,j||<=C r. The same lower bound divided by (1+C)² therefore
covers that moving graph family; when C r>=1, the r² bound is stronger.
notes/zero_coordinate_projector_uniform_polar_bound_independent_review.md
reconstructs the polar vector, exact root, tube, and graph corollary,
including k=1 and singular restrictions.

A separate zero-row direction is covered by
notes/rank_two_zero_row_large_ray_polar.md and its independent review.
For K0=[R;0], with R a 2-by-3 matrix having nonzero entries and proper
minors, choose a selected column r_j, a=1/(2||r_j||), u_top=-a r_j,
u3=sqrt(3)/2, and n=e_j/2. The top proper-block cross coefficient is
-a/t, mixed blocks have strict limiting slack, and the full limit is at
most 1/2. The result holds beyond a direction-dependent threshold.
The review removed an invalid extension of one rank-one limit formula
to a zero vector, which the stated generic hypothesis already excludes.
This zero-row argument is not obtained by transposing the zero-column
theorem and supplies no uniform threshold at its own degenerate boundaries.

The remaining uniform question is sharper now: an escaping sequence
must leave every bounded-critical-column class. The generic rank-two ray
theorem does not control simultaneous growth and degenerating direction.
The existing rank-one graph tube suggests a further discriminator through
singular-value truncation; its exact chart hypotheses should be checked
before using it to exclude bounded second singular values. None of this
boundary work changes the unpassed originality or Cassette-significance
gates. The discovery goal remains active.

The eight additional proof, review, and source files are indexed in README.
They and the three subsequently edited retrieval/review files passed the
focused formatting and local-link checks after one missing TeX spacing
backslash was repaired. Root also corrected a review's symmetric-interval
radius from an unsupported lower inequality to its exact defining value,
and made the all-query Euclidean upper bound explicit. Git still showed
the same tracked path/status list at the final observation. All additional
writes remained in pure_math_astra; no production code changed and no
production test or runtime was run.


### Further investigation: exact unbiasedness, finite advice, and a simpler proof

The current objective and the prior research boundary were reread. The user's
rejection of premature novelty and sufficiency remains controlling. The
following work does not close either gate.

The graph investigation gained two uniformity filters. In
notes/bounded_second_singular_value_graph_lower.md, a graph K=Z^T/r with
sigma_2(K)<=C is within Cr in projector norm of its rank-one truncation.
The existing graph transfer needs only ||Z||<=k, so the truncated chart
need not itself be maximum-volume. Square-root metric comparison gives

    Psi_k(P+r²(I-P)) >=
    r/[4(1+C)² sqrt(k)(k²+2)(1+k²)(1+2k²)].

The note explicitly assumes k>=2. Root checked the truncation and graph
distance argument. notes/generic_rank_two_compact_direction_uniformity.md
constructs continuous local witnesses for cases A/B/C, preserves exact
kernel orthogonality where needed, and bounds the expansion remainders
before taking a finite cover. Pointwise thresholds alone would not justify
that result. notes/rank_two_graph_escape_conditions.md reconstructs the
combination: for k=3 and rank-two K, Psi/r tending to zero forces every
column norm and sigma_2(K) to diverge, while K/||K|| approaches the
nongeneric locus. The compact set explicitly includes rank<=2; omitting
that condition would admit unrelated rank-three directions. The moving
boundary regimes remain open.

A second line examined what exact mean imposes on nonlinear decoders.
notes/two_column_open_cell_exactness_rigidity.md first proved a C1
two-column open-cell theorem. Root removed all decoder regularity in
notes/two_column_open_cell_exact_rigidity.md. Exact incidence moves
preserve the residual; a finite composition has full tangent rank, so
the inverse function theorem on the geometric moves gives local
constancy. Connectedness gives a source-independent residual function
of the query. The independent reconstruction is
notes/two_column_open_cell_borel_rigidity_independent_review.md.
The result is pointwise on connected open source cells, for p>=3.
It does not cover arbitrary measurable cells by itself and does not
force the resident query function to be linear.

notes/stiefel_orthogonality_operator_atomic_matching.md and its independent
review then showed that equatorial averaging T is compact and that an
event f(a)=g(b) under the Stiefel pair law has values only at common
marginal atoms, almost surely. The proof uses a finite-rank approximation
and arbitrarily small nonatomic value partitions. The common atoms may
be countably infinite. notes/stiefel_orthogonality_small_set_bound.md gives
the quantitative estimate for disjoint value cells, using the exact
two-step kernel C_p/sqrt(1-t²), its weak-L^(p-1) tail, and Cauchy--Schwarz.
The endpoint p=3 is included; D_p=((p-1)/(p-2))C_p<=2.

These analytic ingredients yielded the first finite-advice exact-unbiased
bounds in notes/two_column_unbiased_finite_advice_lower.md and
notes/one_column_unbiased_finite_advice_lower.md. Both have independent
reconstructions. The latter uses the rectangular conditional averaging
operator from one column to the other q-1 columns; its squared kernel is
kappa_pq/(1-t²)^((q-1)/2), integrable precisely in the stated p>q range.
Internal random output laws were explicitly restricted to Borel laws of
the legal inputs with source-independent seeds. Otherwise the word
"randomness" could conceal extra source state.

Root then found a stronger direct argument. The operator route is
unnecessary for this decoder lower and is now marked as method history.
The decisive identity is the ordinary two-group exact-mean relation.
For a label-fixed support law, choose a coordinate with inclusion
probability theta<=s/q. At its coordinate query, average the outputs
that omit it into H(W), a function of the other columns. Exactness and
Jensen across the two support groups give

    R(A,e_j) >= ((1-theta)/theta) ||H(W)-a_j||².

This includes overlapping supports: the mean over branches containing
j may depend on all of A; no visibility restriction on that mean is
needed. Conditional on W, the omitted column is uniform on a sphere of
dimension p-q. If C<q/s-1, each label cell therefore has measure at most

    (1/2) (C/(q/s-1))^((p-q)/2).

Summing the N cells proves the main surviving result:

    C >= (q/s-1) min{1,(2/N)^(2/(p-q))}, p>q>=2, 0<s<q.

The complete proof is
notes/finite_advice_unbiased_static_conditional_cap_lower.md.
Independent reconstruction is recorded both in its named review and in
notes/static_support_residual_cap_lower.md. Zero inclusion probabilities
produce null cells; radius one is excluded from the cap step; the expected
read bound applies separately to each state. Empty supports, overlapping
supports, and label-specific fixed right bases are covered. The schedule
must be independent of source within the label and independent of query.
For N<=2^b, the simpler lower is (q/s-1)2^(-2b/(p-q)); a strict relative
target zeta<1 requires b>=1+(p-q)/2 log2(1/zeta). Uniform inclusion
attains q/s-1 without advice. Thus the exact isotropic error scale
survives when b=o(p-q).

notes/two_column_finite_advice_covering_upper.md supplies a standard
rational baseline construction. For two columns, a rounded Frobenius
net gives N<=(1+4sqrt(2)/sqrt(C))^(2p) and exact risk at most C.
Exact mean holds algebraically after source-dependent codeword choice.
The lower and upper label counts have p log(1/C) order at small C,
with different constants. A factorized rational sphere net extends
the upper construction to q columns, with N<=(1+4sqrt(q/C))^(pq).
It has a growing-q gap. The note separates source-label bits, shared
prototype-table bits, and sampling/arithmetic assumptions; it is not
a complete Cassette storage account.

The nonisotropic extension in
notes/nonisotropic_static_residual_cap_obstacle.md leaves a specific
failure of the direct route. Conditioning on other columns exposes
d_j=1/(G^-1)_jj, so the coordinate method sees the positive root
sum_j d_j/(d_j+t)=s. For H_eta=11^T+eta I4 at s=2 this is
eta(eta+4)/(eta+3), about 4eta/3, below the needed 1.9eta threshold.
The isotropic result therefore does not yet extend the adaptive/static
separation to trained nonlinear decoders on that spectrum.

research/two_column_finite_advice_primary_source_challenge.md records a
bounded primary comparison. Funk-transform smoothing, common-information
ideas, and unbiased sparsification are established ingredients. Root
corrected the Gacs-Korner page range using the author's publication list
and read the accessible Safaryan-Shulgin-Richtarik theorem statements.
Their compression-bit bound counts the entire compressed output; our
advice count leaves a continuous observed column available, so substituting
advice bits directly violates that premise. This rules out that direct
application only. The stronger cap argument itself is a short combination
of standard exact-mean and covering tools, and the unnecessary analytic
route cannot supply substantive originality for it.

The next discriminating questions remain mathematical: recover an adequate
nonisotropic lower with finite source advice, or find a contrary decoder;
resolve the simultaneous moving-boundary rank-two graph regimes. The
continuous source-orbit theorem also does not automatically produce a
finite-word hard family for arbitrary nonlinear decoders. A finite corpus
can have extra identification structure, so any finite-word consequence
needs its own proof. No candidate has passed all goal conditions.

All writes in this continuation remained inside pure_math_astra. The
tracked Git path/status list at the later observation matched the initial
list, which is only a path/status comparison, not proof of byte equality.
No production code, test, runtime, commit, or publication was used.

The final independent audit corrected two numerical examples in the Schur
note: diag(4,1) at s=1 has root 2, and its 45-degree rotation has root
8/5. It also corrected the direction of the disjoint-block exponent
comparison; for N>2, the larger conditional dimension gives a stronger
factor. The general overlapping-support theorem and its proof survived.
The audit verified the basis-uniform harmonic lower
q(q/s-1)/tr(G^-1), which the original equicorrelation coordinates attain.
This confirms why that coordinate argument remains insufficient for the
nonisotropic target. Endpoint definitions for theta=0 and C=0 were made
explicit in the supplementary proofs.

The nineteen new or continued proof, review, and source records and the
two retrieval files passed the focused check for nested/unmatched math,
TeX environments, missing local Markdown links, bare spacing commands,
and trailing whitespace. No additional production validation was run.
The goal remains active and unfinished. No manuscript was started.


### Further investigation: finite-word nonlinear comparison and the application decision

The user's status questions asked whether the investigation has a road to
a justified end and whether it has produced multiple material Cassette
improvements. The answer remains: a route and several mathematical results
exist; multiple demonstrated improvements do not. RESEARCH_ROUTE.md now
makes the active route and next decision directly retrievable. No paper
or completed-goal claim is warranted.

The main mathematical obstacle from the preceding entry was resolved.
Conditional Haar projection concentration controls arbitrary Borel branch
outputs simultaneously over finite source labels, positive-probability
supports, and a finite query net. The net approximates a linear dual
functional, never the decoder itself. Exact mean and the risk second
moment then imply a stable matrix trace inequality. This recovers the
nonisotropic spectral bound despite nonlinear decoding and finite source
advice. Independent reconstruction checked integrability extensions,
discarding zero-mass branches, finite-label quantifiers, and the advice
deficit and equicorrelation constants.

A finite-source extension needs a declared information format. An exact
transformed column can identify any finite family after a suitable shared
transform, with its precision hiding the full source payload. The saved
counterexample establishes this limitation. Original rounded columns
admit a different proof: lifting a decoder through coordinatewise rounding
still depends only on the observed continuous columns. Normalizing the
second moment before bounding the rounding error preserves the required
spectral scale. The weaker alternate bound that inflates the global risk
by the top eigenvalue is unnecessary for the final separation.

The adaptive construction also survives rounding. A shared rational
four-coordinate catalog has ideal risk at most 1.895 eta. Choosing
h<=sqrt(eta)/(10000sqrt(pq)) keeps rounded risk below 1.9 eta, exact mean
toward the stored source, and a hard 2m original-column cap. Taking real
parts matches the real lower model without increasing risk or support.
The combined independent review verified the exact constants. Root
consolidated the theorem and weakened the dual inequality before
substituting a uniform rounding constant, avoiding an unjustified
positive/negative-term substitution.

For sufficiently small dyadic eta, q=4m, and
p-4m>4,000,000(log N+6m log 2+4m log 201), every qualifying static
architecture has a rounded source requiring at least
(11807741126602841/5842634219605125)m expected original-column reads.
This exceeds 2.02m. The adaptive law uses at most 2m on every source.
The hard source depends on the static architecture. The source words
are finite. A separate rational-query net proof shows that one finite
rational unit-query alphabet suffices for the lower, with unchanged
covering constants; its word width is finite but unquantified.

The resource assessment leaves a decisive application question. Under
independently fetched equal-size original-column pages, the theorem gives
a conditional fresh-byte saving on the hard source. It does not count
the shared catalog, selector, exact sampler, query arithmetic, or peak
workspace. Root corrected the assessment to distinguish a cold-load
traffic total from peak resident memory, and to use a non-strict first
inequality when converting the hard adaptive cap into a byte gap.
The next concrete object is a serialized four-coordinate rational
catalog with a selector and sampler whose storage and work can be counted.
If those costs or the sufficient dimension prevent a consequential
application, that named obstruction should direct the mathematics.

The parallel geometric result supplies a fixed-factor two-scale witness
for rank-two charts approaching rank one. A proper-submatrix inverse
cancels dependence on the weak scale, removing the earlier unnecessary
restriction on its growth. Moving factors with collapsing minors remain
open. This geometry remains supporting work unless it changes the
application or originality case.

The bounded primary-source assessment does not accept originality.
Its finite-source concern is now resolved only in the declared
original-column class. No absence-of-prior-work certificate is required
or possible; the precise nonroutine intellectual advance still needs to
be established by comparison with the closest primary proofs.

All current writes remain inside pure_math_astra. The observed tracked
Git path/status list matches the prior list; this is not a byte-equality
claim about other ongoing work. No production code, production test,
native runtime, commit, push, or publication was performed here.
The goal remains active.


### Explicit pause and retained implementation candidates

Drew stopped the discovery loop. PAUSED_HANDOFF.md records his four retained
results, the subsequently completed explicit two-rule sampler and exact
integer audit, the remaining product integration blockers, and the
unreviewed arithmetic/directional work. The active directional-proof
subagent was interrupted; the other subagents had completed. No new
research or production work is authorized by this checkpoint.
