<!-- Machine-stage review and bounded remediation; depends on repository instructions, the execution queue, governing acceptance authorities, one frozen machine-attempt manifest, and any prior review envelope. -->
# Machine attempt procedure

Review one completed machine attempt or a declared ordered batch against its declared assertions.
Challenge the implementation and its evidence. If a defect is proved and the profile permits
remediation, apply the bounded repair procedure. The review does not close, reorder, or redefine a
stage. A batch freezes its ID, ordered members, and per-stage attempts and close records; report
separate questions, evidence, findings, disposition, and verdict for every member. An earlier
repair invalidates dependent later evidence until replayed.

## Boundary

- Apply only to STATIC, FIXTURE, INTEGRATION, or PLATFORM evidence. Never mount a physical drive,
  use a credential, contact a live service, download a model, or claim `LIVE`.
- L01-L03 and construction of L04 use the bootstrap profile under the queue. Evidence records inherit the target profile. Freeze an off-tree immutable manifest containing stage
  and attempt IDs, source commit and tree, lock, matrix, runbook, assertion-set and predecessor
  bootstrap-manifest digests, declared commands, raw outputs, and every inspected file digest. Do
  not require a campaign namespace, review lease, expansion registry, or dependency graph before the
  owning stage creates it. Use one off-tree atomic bootstrap-review head keyed by stage, attempt, and
  manifest digest. Each immutable review record names the current head and may compare and swap it
  once; reject a stale head or fork. Bootstrap review is read-only and permits no remediation.
- The integrated L04 candidate uses the normal profile once its bootstrap proof establishes the required machinery. Subsequent L04 machine attempts, POST-SELECTION-MACHINE-PASS within L05, and later eligible machine repairs use the normal profile. Resolve membership from the current queue; never apply this profile to live or reference-service work. Freeze stage ID, attempt
  ID, parent revision, tree, lock, matrix, runbook, expansion-registry, active dependency-graph,
  assertion-set, required-level, machine-attempt-manifest, and prior-review-envelope digests before
  inspection.
- Assertions are closed. Add no metric, threshold, test requirement, dependency, authority,
  permission, status rule, or model-specific branch.
- Under the normal profile, acquire one exclusive review lease for
  `(stage_id, attempt_id, machine_attempt_digest)` with
  atomic create-or-compare-and-swap. The review base must equal the attempt manifest's parent SHA.
  Record holder, UTC acquisition/expiry, release, abandonment, succession, prior lease digest when
  succeeded, and isolated worktree. An expired or abandoned lease may be succeeded only by
  compare-and-swap naming its digest. A second reviewer may read but may not remediate. Release only
  after the review envelope is sealed.
- Work only in an isolated clean child worktree from the frozen parent. If the parent does not
  resolve, the tree is dirty, HEAD diverges, or another lease owns the tuple, return `QUEUE_ROUTE`.
  Never repair the shared execution checkout.
- A normal machine-attempt manifest is immutable. Inspect it with `lstat` without following links;
  accept only directories and regular files whose link count is one. Its recursive manifest lists
  every relative path, object type, and regular-file content digest. Reject extra, missing, renamed,
  substituted, or type-changed paths, symbolic or hard links, sockets, devices, FIFOs, and other
  special objects. The separately sealed review envelope uses the same rule.
- A machine attempt consumes one of five slots when its frozen manifest starts the first declared
  command. Preflight, review, remediation, and waiting consume no slot. A counted capture failure
  seals every recoverable artifact and the missing-item list. The fifth non-PASS attempt makes the
  record `BLOCKED`; a sixth requires a queue decision.
- One normal review session lasts at most twenty minutes. An attempt may have at most five append-only
  review envelopes. A timed-out review seals `INCOMPLETE` and does not consume an attempt. A resumed
  review gets a new review ID, linked lease, and prior-envelope pointer equal to the current head,
  then atomically compares and swaps that head to its sealed envelope digest. A stale expected head
  or fork fails. The fifth incomplete review returns `QUEUE_ROUTE`. Bootstrap review follows the
  same five-record limit and atomic-head rule, but uses no campaign lease.

## Shared review standard

Apply the adversarial examination in [SKILL.md](../SKILL.md): trace implementation, design fresh
challenges, prove the instrument can detect the relevant failure, and evaluate supported improvements.
The procedures below do not replace that examination. A clean result requires both.

## Review

1. Recompute the attempt manifest, require exact namespace equality, and recompute every cited
   raw-artifact digest. Missing evidence makes the affected assertion `NOT_RUN`; reviewer inference
   cannot fill it.
2. For each assertion, record the predicate, raw deciding artifact, reported and independently
   replayed values, nearest false pass, and discriminator result.
3. Classify status as `PASS`, `FAIL`, `NOT_RUN`, or `BLOCKED`, and level as `STATIC`, `FIXTURE`,
   `INTEGRATION`, or `PLATFORM`. Never write `LIVE`.
4. Name one primary cause and any contributing causes. Only product implementation, mathematical
   implementation, collector, or verifier defects qualify for automatic remediation.
5. Route authority gaps, environment limits, live-evidence needs, principal actions, performance
   or Q38 outcomes, and repairs above the bound to the queue.
6. Under the normal profile, emit one invalidation class: `replay_only`, `assertion_local_rerun`,
   `machine_proof_rerun_required`, `physical_requalification_required`, or
   `mechanism_revision_new_campaign_required`. Derive and seal its scope from the latest sealed
   graph successor whose ancestry contains the attempt-bound graph and has preserved every inherited
   node, edge, evidence level, assertion owner, permission binding, and terminal-state meaning.
   Record both graph digests.
   Except for `replay_only`, list at least one exact invalidated ID and every affected
   logical-operation and physical-qualification lineage. If a narrow class is not proved, use the
   broader class.
7. Under the normal profile, seal the review envelope, require its prior-envelope digest to equal
   the current head, atomically compare and swap that head to the new envelope digest, then release
   the lease. Under the bootstrap profile, seal the read-only record against its manifest and
   atomically advance the bootstrap-review head.
   The queue alone schedules a rerun, reopens dependencies, marks `BLOCKED`, or closes.

## One bounded remediation

Bootstrap review may not remediate. Under the normal profile, one attempt may produce at most one
accepted child commit for one named declared assertion. The complete remediation may
change at most forty executable lines total and may add no dependency, assertion, threshold,
authority, permission, model-specific branch, or unrelated cleanup.
Use `tools/ledger.py remediation-diff --parent <sha> --child <sha>`. Its versioned allowlist is the
Python source in the AGENTS removal map plus `tools/campaign.py`. It rejects generated, test,
documentation, lock, schema, and unknown paths; its pinned parser excludes comments and docstrings;
and it counts parent-relative added plus deleted executable lines. Record its normalized JSON digest
and count.

An accepted remediation seals `REMEDIATED` and terminates that attempt's review history. No later
review or second automatic repair may descend from it. The queue must create a new machine attempt
on the exact child revision.

1. On the frozen parent, run one discriminating probe that fails for the assertion. Record command,
   input, raw output digest, and parent SHA.
2. Make the smallest correction in the isolated child worktree.
3. Stage it, recheck the lease, queue tuple, paths, line bound, and linear ancestry, then create the
   sole child commit. Change no byte afterward.
4. Run the same probe on exact child commit R+1 and require PASS. A test-only edit cannot satisfy this step.
5. On exact R+1, run a guard-removal or equivalent nearest-false-pass control and require it to fail.
6. Run the complete repository suite and ledger on exact R+1. Record a failing child as rejected and
   leave it isolated; never publish it as accepted remediation.

The review envelope records the named assertion, parent and child SHAs, changed paths, normalized
diff digest, executable line count, parent-red, child-green, mutation, suite, and ledger digests,
plus invalidation scope digest, exact IDs, operation lineages, and qualification lineages. Child
proof is machine evidence only; it does not rewrite the parent attempt.

If the repair exceeds the bound, touches another assertion, changes authority, or cannot descend
cleanly from the parent, make no commit. Return a bounded queue item naming the failed assertion,
required change, invalidation scope, and rerun target.

## Review envelope and baton

The normal envelope contains its review ID, prior-envelope pointer, expected and new review-set
heads, all frozen identities
and lease history; one row per assertion with source trace, reviewer-designed challenge, expected
and observed results; raw replay and mutation artifacts; supported improvement recommendations
with benefit, tradeoff, and verification method, plus rejected candidates and reasons; cause and route; remediation lineage or `none`; invalidation; and every
disposable artifact created and removed. State: “This review made no live-state claim or live-state
change.”

End with exactly one route:

- `PASS_READY`: every applicable assertion is `PASS` at its required level and the adversarial
  examination above is complete; the queue may apply its closure rule.
- `INCOMPLETE`: name every `NOT_RUN` or `BLOCKED` assertion and its exact prerequisite or missing
  evidence.
- `REMEDIATED`: queue may schedule a new machine attempt on the exact child revision after applying
  invalidation.
- `QUEUE_ROUTE`: name the blocker, authority gap, invalidation, or out-of-bound repair required.

A bootstrap review uses the same routes except `REMEDIATED`, which is forbidden.
