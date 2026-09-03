---
name: live-stage-review
description: Adversarially review one live, hardware-in-the-loop, source-service, model-bearing, or principal-assisted attempt from its immutable execution bundle; replay every declared assertion, prove the nearest false pass, apply at most one bounded implementation remediation on an isolated child revision, declare invalidation, seal a separate review envelope, and return the attempt to the queue without closing it. Use only after a live attempt begins. Do not use for machine-only fixture work, queue authoring, or stage closure.
---

<!-- Live-attempt review and bounded remediation; depends on repository instructions, the execution queue, governing acceptance authorities, one immutable execution bundle, its attempt binding and action templates, and any prior review envelope. -->
# Live Stage Review

Review one live attempt. Preserve what happened. Test whether the evidence can distinguish the
claimed behavior from its nearest false pass. Repair one small implementation defect only when the
failed assertion, parent revision, and child proof are exact. Return control to the queue.

## Hard boundary

- The reviewer never closes, reorders, or redefines a stage. Assertions, thresholds, baselines,
  evidence levels, permission classes, and outcome rules remain closed during review.
- The reviewer never performs a principal action, contacts a live account or service, mounts or
  writes a model-bearing drive, or changes an active live operation. Scratch replay is machine
  evidence and never upgrades a LIVE result.
- The sealed execution bundle is immutable. Inspect it with `lstat` without following links and
  accept only directories and regular files whose link count is one. Its canonical recursive
  manifest enumerates every relative path, object type, and regular-file content digest. Reject any
  extra, missing, renamed, substituted, or type-changed path, symbolic or hard link, socket, device,
  FIFO, or other special object. The review report uses the same exact-namespace rule in a separate
  immutable envelope.
- A rerun compares immutable `card_template` and `principal_action_template` digests. Timestamps,
  observations, attempt bindings, and operation IDs must be new. Freshly record the source revision;
  it may equal the prior attempt unless remediation or invalidation requires an exact child. Reuse a
  template only when disk, paths, permission, physical action, cues, and stop conditions are unchanged.
- Use one exclusive review lease for `(stage_id, attempt_id, execution_bundle_digest)`. Acquire it
  with atomic create-or-compare-and-swap. Its review base must equal the attempt binding's execution
  revision. Preserve acquisition, expiry, release, abandonment, and succession records. An expired
  or abandoned lease may be succeeded only by compare-and-swap naming the prior lease digest. A
  second reviewer may read but may not remediate. Release the lease only after the review envelope
  is sealed.
- Run mutations and probes only in a disposable isolated worktree or fixture created from the exact
  frozen parent. Never repair the shared execution checkout or capture unrelated dirty work.
- One review session lasts at most twenty minutes. An attempt may have at most five append-only
  review envelopes. Running out of review time seals `INCOMPLETE`, marks unreached checks `NOT_RUN`,
  and does not consume an execution attempt. A resumed review gets a new review ID and linked lease,
  names the current head as its prior envelope, and atomically compares and swaps that exact head to
  its sealed envelope digest. A stale expected head or fork fails. The fifth incomplete review
  returns `QUEUE_ROUTE`. An accepted `REMEDIATED` envelope terminates that attempt's review history;
  the queue must create a new attempt on the exact child revision.

## Freeze before inspection

Record and verify:

1. stage ID, attempt ID/number/kind, `rerun_of`, and the queue entry that authorized it;
2. full execution commit, tree digest, lock, matrix, runbook, expansion-registry, and frozen
   dependency-graph digests plus the closed assertion-set digest;
3. required evidence level for each assertion;
4. action-template digests and the attempt-binding digest;
5. execution-bundle digest, logical-operation lineage, fresh operation IDs, recovery boundaries,
   and state at seal;
6. previous attempt and review-envelope identities; and
7. reviewer environment, isolated-worktree identity, lease holder, acquisition UTC, expiry UTC,
   prior lease digest when succeeded, and proof that the review base equals the execution revision.

If a frozen identity cannot be resolved exactly, or a counted attempt has no sealed execution or
capture-failure bundle, stop with `QUEUE_ROUTE`.

## Review workflow

1. **Verify evidence integrity.** Recompute the canonical recursive execution manifest, require
   exact namespace equality, and recompute every raw-file digest. Check timestamp order, cue before action, action before observation, final command before
   seal, and post-write telemetry after the write. Compare rerun template digests and require a new
   binding plus fresh operation IDs or an exact compatible-resume record.

2. **Check applicability.** Each evidence item is `APPLICABLE` or `NOT_APPLICABLE`. An N/A entry
   cites the governing authority. N/A cannot remove a declared assertion. Missing applicable raw
   evidence makes its assertion `NOT_RUN`; a collector or verifier defect remains eligible for the
   bounded remediation route, but the attempt remains unchanged.

3. **Form one discriminator per assertion.** Record the exact predicate, raw deciding artifact,
   reported value, independently replayed value, nearest false pass, and operation that separates
   them. A summary, derived table, or prior review is not the raw artifact.

4. **Replay from raw data.** Recompute byte and content digests, before/after deltas, Q53 arithmetic,
   durable order, checkpoint/resume ranges, inventory changes, resource distributions, statistical
   plans, and gate outcomes as applicable. Re-execute agent-only logic only on scratch fixtures. A
   repaired verifier never changes the original attempt. When `replay_only` is proved and every raw
   input already exists, create a separate verification-replay record; otherwise require a new live
   attempt.

5. **Attack the evidence.** Cross-check drive/host/time identity, command and operation ordering,
   source and local digests, internal-file scans, profile binding, inventory scope, and background
   terminal state. Remove or invert the guard in a disposable child. If the instrument would report
   the same result, the affected assertion is `FAIL` or `NOT_RUN`, never a nonblocking observation.

6. **Classify exactly.** Assertion status is `PASS`, `FAIL`, `NOT_RUN`, or `BLOCKED`; evidence level
   is `STATIC`, `FIXTURE`, `INTEGRATION`, `PLATFORM`, or `LIVE`. Name one primary cause and any
   contributing causes from: product implementation, mathematical implementation, collector,
   verifier, mechanism performance, principal template, environment/account/hardware/permission,
   or `AUTHORITY_GAP`.

7. **Route the cause.** Product, mathematical, collector, or verifier implementation defects may
   use bounded automatic remediation. A principal-template defect requires a queue-approved
   successor template. An environment, account, hardware, permission, or service limitation is
   `BLOCKED` until its prerequisite changes. A missing or ambiguous baseline, identity, assertion,
   threshold, evidence level, outcome rule, or safety permission is `AUTHORITY_GAP`; only the queue
   or governing authority may amend it. A mechanism-performance failure follows Q38.

8. **Declare invalidation.** Emit exactly one class:
   - `replay_only`: verifier/reporting changed and all required immutable raw inputs exist;
   - `assertion_local_rerun`: one live assertion needs a new attempt but its prerequisites remain valid;
   - `machine_proof_rerun_required`: machine behavior, schema, certificate, or operation semantics changed;
   - `physical_requalification_required`: a change can affect the drive × host × operation × plan profile;
   - `mechanism_revision_new_campaign_required`: the mechanism or F4/F5 result changed.

   Derive the scope from the latest sealed graph successor whose ancestry contains the attempt-bound
   graph and preserves every inherited node, edge, evidence level, assertion owner, permission
   binding, and terminal-state meaning; record both graph digests and seal the scope. Except for `replay_only`, list at least one
   exact invalidated attempt/evidence ID plus every affected logical-operation and
   physical-qualification lineage. If the narrower class is not proved, choose the broader class.
   Do not resume an operation across revisions without an exact compatible durable boundary and
   proof digest.

9. **Seal the review envelope.** Include its review ID, reviewed bundle or prior envelope,
   prior-envelope digest, expected and new review-set heads, all frozen identities, lease history,
   per-assertion rows, replay/mutation artifacts, cause/routing, remediation lineage, invalidation,
   disposable environments created and removed, and the exact baton. Require the prior digest to
   equal the current head, atomically compare and swap the head to this envelope digest, then release
   the lease.

## Bounded automatic remediation

One execution attempt may produce at most one accepted remediation commit for one named declared
assertion. The complete remediation may change no more than forty executable lines total and may add no dependency,
assertion, threshold, authority, permission, model-specific branch, or unrelated cleanup.
Use `tools/ledger.py remediation-diff --parent <sha> --child <sha>`. Its versioned allowlist is the
Python source in the AGENTS removal map plus `tools/campaign.py`. It rejects generated, test,
documentation, lock, schema, and unknown paths; its pinned parser excludes comments and docstrings;
and it counts parent-relative added plus deleted executable lines. Record its normalized JSON digest
and count.

An accepted remediation seals `REMEDIATED` and terminates this attempt's review history. No later
review or second automatic repair may descend from it. The queue must create a new attempt on the
exact child revision.

The proof is ordered:

1. On parent R, run a discriminating probe that fails for the named assertion. Record command,
   input, raw output digest, and full parent SHA.
2. In the isolated clean child worktree, make the smallest product or instrument correction.
3. Stage it, recheck the lease, paths, line bound, and linear ancestry, then create the sole child
   commit R+1 under the repository commit law. Change no byte afterward.
4. On exact commit R+1, run the same probe and require PASS. A test-only edit cannot satisfy this step.
5. On exact R+1, run the nearest-false-pass mutation or sensitivity probe and require it to fail.
6. Run the complete repository suite and ledger on exact R+1. Record a failing child as rejected and
   leave it isolated; never publish it as accepted remediation.

Record named assertion, parent SHA, child SHA, changed paths, normalized diff digest,
executable-line count, parent-red
digest, child-green digest, mutation digest, suite digest, ledger digest, and invalidation class.
The failed attempt and its evidence level do not change. A new live attempt proves the repair.

If the smallest credible repair exceeds the bound, touches a second assertion, changes authority,
or cannot descend cleanly from the frozen revision, make no commit. Return a bounded queue item with
the failed assertion, required change, invalidation scope, and exact rerun target.

## Nearest false passes

- A fixture, recording, loopback route, or configuration presented as LIVE.
- Identity inferred from a volume name or path instead of disk ID, APFS UUID, host, and same-session
  telemetry.
- A digest of a summary or manifest where the raw bytes were required.
- A cue printed after the target operation was already terminal.
- A kill after terminal state, or a restart that rereads all work but is labelled resume.
- One capacity or profile measurement reused where the assertion requires each transition or exact
  operation-plan binding.
- Telemetry from another mount, host, port, cable, or time window.
- Inventory compared by name alone, stored on the protected drive, or allowed to ignore aggregate
  byte changes.
- A missing declared assertion, a PASS for an undeclared assertion, or Q38 falsification relabelled
  as PASS.
- A threshold, budget, candidate set, or statistical plan frozen after result data existed.
- A bundle sealed while its claimed terminal operation remained active.
- Green created by a skip, deselection, platform gate, or changed test rather than product behavior.
- An instrument whose output survives removal of the behavior it claims to observe.

## Review envelope

Write these sections in order:

1. Scope and frozen identities.
2. Execution-bundle integrity and template/binding lineage.
3. Per-assertion status, level, raw artifact, replay, false pass, and discriminator.
4. Cross-artifact and sensitivity findings.
5. Primary and contributing cause; failure route.
6. Remediation lineage and complete gate, or `none`.
7. Invalidation class, scope digest, invalidated IDs, operation lineages, and qualification lineages.
8. Prior, expected, and new review-history heads; lease release; disposable-environment cleanup;
   and baton.

State: “This review changed no execution bundle, action template, principal action, assertion,
threshold, authority, permission, or live state. Machine replay does not change a live assertion's
status or evidence level.”

End with exactly one baton:

- `PASS_READY`: every applicable assertion is `PASS` at its required level; the queue may apply its
  closure rule.
- `INCOMPLETE`: name every `NOT_RUN` or `BLOCKED` assertion and its exact prerequisite or missing
  evidence.
- `REMEDIATED`: queue may schedule a new attempt on the exact child revision after applying the
  recorded invalidation route.
- `QUEUE_ROUTE`: name the Q38, authority, template, environment, compatibility, or out-of-bound
  action required.
