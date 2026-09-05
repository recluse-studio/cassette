<!-- Portable live-attempt review; the application's existing contract supplies authorities, schemas, identity, resource checks, budgets, tools, and invalidation meanings. -->
# Live attempt procedure

Review exactly one live attempt under the application's existing live-stage contract. Preserve what
happened. Test whether the sealed evidence distinguishes the claimed behavior from its nearest false
pass. Repair one small implementation defect only when the contract permits it and the parent and
child proofs are exact. Return control to the queue.

## Read the governing contract first

Read the queue entry and every authority that it names before inspecting the attempt. The application
may express these rules in one contract, several documents, a schema, or a run-card definition; do
not require a file with a particular name. Resolve and record their exact revision or content
digests. Extract:

- the closed assertion set, thresholds, baselines, evidence levels, statuses, and terminal outcomes;
- the application and external-resource identity fields, revision mechanism, dependency lock, and
  source-of-truth boundaries;
- the execution-bundle, capture-failure, review-envelope, lease, and lineage formats;
- action templates, approval and permission classes, principal cues, external-service boundaries,
  and emergency-stop or hold procedure;
- resource dimensions and the exact replay, measurement, and before/after procedures for each
  applicable assertion;
- finite session, review-history, and remediation limits;
- the isolated-child, allowed-path, diff-counting, mutation, and complete-gate procedures; and
- invalidation classes, scope calculation, dependency graph or equivalent lineage store, and
  cleanup rules.

The governing contract remains the acceptance authority. The review cannot add, remove, or weaken an
assertion, threshold, baseline, evidence level, permission, or outcome. If a required fact, command,
schema, identity, or boundary is missing or ambiguous, return `QUEUE_ROUTE`; never borrow a default
from another application or silently invent one.

## Hard boundary

- Never close, reorder, or redefine a stage. Assertions, thresholds, baselines, evidence levels,
  permissions, and outcome rules remain closed during review.
- Never perform a principal action, contact a live account or service, mount or write a protected
  resource, or change an active operation. If the governing contract declares an emergency stop or
  hold path and its safety condition is present, issue only that declared stop, record who or what
  issued it, and preserve the state. A safety stop is neither remediation nor evidence of a passing
  assertion.
- The sealed execution bundle is immutable. Inspect it with `lstat` without following links and
  build its canonical recursive manifest under the governing contract's namespace rule. If that rule
  does not define allowed object types, link handling, digest, traversal, and cleanup semantics,
  return `QUEUE_ROUTE`; an uncontrolled link or special object is never accepted. The review envelope
  uses a separate immutable namespace.
- Run mutations and probes only in a disposable isolated environment created from the exact frozen
  parent revision. Never repair the shared execution checkout or capture unrelated dirty work.
- A rerun reuses the execution-card, script, action-template, and principal-action-template digests
  declared by the contract only when scope, permissions, cues, physical or external actions, and stop
  conditions are unchanged. Timestamps, observations, attempt bindings, and any operation IDs are
  always new; a compatible resume must name its exact durable boundary.
- Use the finite limits stated by the governing contract. A review session may end with
  `INCOMPLETE`; it never waits for a long operation, consumes an execution attempt merely by
  waiting, or silently extends a review-history or remediation limit.

## Session and capture boundaries

Verify the contract's ordered session protocol before judging the behavior. Where it defines resume,
read-only preparation, principal approval or action, frozen execution, and capture as separate parts,
check every part, its time budget, and its transition in order. No live operation may begin during
read-only preparation. The principal action occurs only at its declared point. After the cue or
approval, the agent runs only the frozen command and capture procedure; it does not edit code,
documentation, assertions, thresholds, or the execution card. Credentials and other sensitive inputs
follow the contract's opaque-input rule. A missing or out-of-order segment, command, cue, observation,
or mandatory bundle field receives the contract's declared status, normally `NOT_RUN` or
`QUEUE_ROUTE`; the reviewer never fills it from a summary or assumption.

## Review lease and history

Acquire one exclusive review lease for the governing contract's review key, which must bind the stage,
attempt, and execution-bundle identity or an equally exact scope, using the application's atomic
create-or-compare-and-swap operation. The lease's review base must equal the attempt binding's
execution revision. Preserve acquisition, expiry, release, abandonment, and succession records. An
expired or abandoned lease may be succeeded only by a compare-and-swap that names the prior lease
digest. A second reviewer may read the attempt but may not remediate it. Release the lease only after
sealing the review envelope.

Review envelopes form an append-only history. A resumed review receives a new review ID, names the
current envelope head as its prior digest, acquires a new linked lease, and atomically compares and
swaps that exact head to its new sealed envelope digest. A stale expected head or fork fails. When a
review session ends before all checks are reached, seal `INCOMPLETE`, mark every unreached assertion
`NOT_RUN`, and consume no execution attempt. The contract's review-history limit routes the attempt
when exhausted. An accepted `REMEDIATED` envelope terminates that attempt's review history; the
queue must create a new attempt on the exact child revision.

## Freeze before inspection

Record and verify:

1. queue entry, stage ID, attempt ID/number/kind, `rerun_of`, and every authority and contract digest;
2. the closed assertion-set digest and required evidence level for each assertion;
3. immutable application revision, tree or artifact identity, dependency lock, and revision-provider
   evidence;
4. action-template and principal-action-template digests, approval and permission lineage, and the
   declared safety boundary;
5. execution-bundle or capture-failure digest, operation IDs, logical-operation lineage, recovery
   boundaries, and state at seal;
6. previous attempt and review-envelope identities, current review-history head, and the exclusive
   lease identity; and
7. reviewer environment, isolated-environment identity, acquisition UTC, expiry UTC, prior lease
   digest when succeeded, and proof that the review base equals the execution revision.

If a frozen identity cannot be resolved exactly, or a counted attempt has no sealed execution or
capture-failure bundle, stop with `QUEUE_ROUTE`.

When the contract declares an operation capable of outliving a session, require separate `START` and
terminal `VERIFY` records. `START` proves only the first declared durable boundary and any required
kill/resume discriminator. `VERIFY` is eligible only after the operation is terminal. A preflight
check or ordinary waiting period is not a terminal result.

## Shared review standard

Apply the adversarial examination in [SKILL.md](../SKILL.md): trace implementation, design fresh
challenges, prove the instrument can detect the relevant failure, and evaluate supported improvements.
The procedures below do not replace that examination. A clean result requires both.

## Review workflow

1. **Verify evidence integrity.** Recompute the canonical recursive manifest, require exact namespace
   equality, and recompute every raw-file digest. Check timestamp order, the contract's session-part
   order, cue before action, action before observation, final command before seal, and post-write
   telemetry after the write. Require every mandatory bundle field and compare card, script, and
   template digests. A rerun requires a new binding plus fresh operation IDs where operations exist,
   or an exact compatible-resume record.

2. **Check applicability.** Mark each evidence item `APPLICABLE` or `NOT_APPLICABLE`. An N/A entry
   cites the governing authority. N/A cannot remove a declared assertion. Missing applicable raw
   evidence makes its assertion `NOT_RUN`; a collector or verifier defect may be remediation-eligible,
   but the original attempt remains unchanged.

3. **Form one discriminator per assertion.** Record the exact predicate, raw deciding artifact,
   reported value, independently replayed value, nearest false pass, and operation that separates
   them. A summary, derived table, or earlier review is not the raw artifact.

4. **Replay from raw data.** Recompute every applicable identity, byte or resource claim,
   before/after delta, durable order, checkpoint/resume range, inventory change, statistical plan,
   and terminal outcome required by the contract. Re-execute agent-only logic only in the isolated
   environment. A repaired verifier never changes the original attempt. If every required raw input
   exists and no live observation is needed, create a separate verification-replay record; otherwise
   require a new live attempt.

5. **Attack the evidence.** Cross-check every required identity, host or service boundary, time
   window, command and operation order, source and local digest, internal-file or protected-content
   scope, resource/plan binding, and background terminal state. Remove or invert the guard in a
   disposable child. If the instrument reports the same result after the behavior it claims to
   observe is removed, classify the affected assertion `FAIL` or `NOT_RUN`, never as a nonblocking
   observation.

6. **Classify exactly.** Use the contract's normalized assertion statuses: `PASS`, `FAIL`, `NOT_RUN`,
   or `BLOCKED`, and its evidence ladder. Name one primary cause and any contributing causes from
   these core families: implementation, mathematical or semantic implementation, collector,
   verifier, mechanism performance, principal-action template, environment/account/hardware/
   permission/service, or `AUTHORITY_GAP`. The application may add a narrower cause but may not hide
   one of these families.

7. **Route the cause.** Product, mathematical/semantic, collector, or verifier defects may use
   bounded automatic remediation only under the contract. A principal-template defect requires a
   queue-approved successor template. An environment, account, hardware, permission, or service
   limitation is `BLOCKED` until its prerequisite changes. A missing or ambiguous baseline, identity,
   assertion, threshold, evidence level, outcome rule, or safety permission is `AUTHORITY_GAP`; only
   the queue or governing authority may amend it. A mechanism-performance failure follows the
   contract's mechanism-failure authority.

8. **Declare invalidation.** Emit exactly one contract-defined invalidation class. At minimum, the
   application must distinguish these meanings:

   - `replay_only`: reporting or verification changed and all required immutable raw inputs exist;
   - `assertion_local_rerun`: one assertion needs a new attempt while its prerequisites remain valid;
   - `implementation_proof_rerun_required`: implementation, schema, certificate, or operation
     semantics changed;
   - `resource_requalification_required`: a changed resource, environment, host, path, or plan can
     affect the qualification envelope; and
   - `mechanism_revision_new_campaign_required`: the mechanism or governing mechanism result
     changed.

   An application may use local names, but its contract must map each one to an exact meaning and
   preserve the distinction between replay, implementation proof, resource qualification, and
   mechanism change. Derive scope from the latest sealed graph or equivalent lineage successor whose
   ancestry contains the attempt-bound graph. It must preserve every inherited node, edge, evidence
   level, assertion owner, permission binding, and terminal-state meaning. Record both graph digests.
   Except for `replay_only`, list at least one exact invalidated attempt/evidence ID and every
   affected logical operation and resource-qualification lineage. If the narrower class is not
   proved, choose the broader contract-defined class. Never resume an operation across revisions
   without an exact compatible durable boundary and proof digest.

9. **Seal the review envelope.** Include the review ID, all governing-contract and authority
   digests, reviewed bundle or prior envelope, prior-envelope digest, expected and new review-set
   heads, all frozen identities, lease history, per-assertion rows, replay/mutation artifacts,
   cause/routing, remediation lineage, invalidation class and scope, disposable environments created
   and removed, and the exact baton. Require the prior digest to equal the current head, atomically
   compare and swap the head to this envelope digest, then release the lease.

## Bounded automatic remediation

Automatic remediation is available only when the governing contract supplies an immutable revision
provider, isolated-child procedure, allowed-path policy, normalized executable-change counter,
discriminating probe, nearest-false-pass mutation, and complete gate. If any one is absent, make no
automatic change and return `QUEUE_ROUTE`.

One execution attempt may produce at most one accepted remediation. Use the contract's stated maximum
total executable change; if the contract does not state one, return `QUEUE_ROUTE`. A remediation may
add no dependency, assertion, threshold, authority, permission, or unapproved policy branch. Enforce
the contract's versioned path allowlist and reject every path it does not explicitly admit, including
generated, test-only, documentation, lock, schema, or unrelated paths when the contract excludes
them. Its pinned parser must exclude comments and docstrings. Record the normalized diff digest and
count.

An accepted remediation is terminal for that attempt's review history. The queue must create a new
attempt on the exact child revision. No later review or second automatic repair may descend from the
remediated attempt.

The proof is ordered:

1. On parent revision `R`, run the contract's discriminating probe and require it to fail for the
   named assertion. Record command, input, raw-output digest, and full parent identity.
2. In the isolated clean child, make the smallest product or instrument correction.
3. Recheck the lease, paths, line bound, and linear ancestry. Create the sole child revision `R+1`
   under the application's revision law. Change no byte afterward.
4. On exact `R+1`, run the same probe and require `PASS`. A test-only edit cannot satisfy this step.
5. On exact `R+1`, run the nearest-false-pass mutation or sensitivity probe and require it to fail.
6. Run the contract's complete gate on exact `R+1`. Record a failing child as rejected and leave it
   isolated; never publish it as accepted remediation.

Record the named assertion, parent and child identities, changed paths, normalized diff digest,
executable-change count, parent-red digest, child-green digest, mutation digest, complete-gate
digest, application-ledger or equivalent verification digest, and invalidation class. The failed
attempt and its evidence level do not change. A new live attempt proves the repair.

If the smallest credible repair exceeds the bound, touches a second assertion, changes authority,
or cannot descend cleanly from the frozen revision, make no commit or artifact revision. Return a
bounded queue item with the failed assertion, required change, invalidation scope, and exact rerun
target.

## Nearest false passes

- A fixture, recording, loopback route, configuration, or external substitute presented as LIVE.
- Identity inferred from a human label or path instead of every contract-required identity field and
  same-session telemetry.
- A digest of a summary or manifest used where the raw bytes were required.
- A cue printed after the target operation was already terminal.
- A kill after terminal state, or a restart that rereads all work but is labelled resume.
- One resource or operation-profile measurement reused where the assertion requires each transition
  or exact binding.
- Telemetry from another host, account, resource, path, permission context, or time window.
- A protected-content or scope inventory compared by name alone, stored inside the subject under test,
  or allowed to ignore aggregate changes.
- A fixed percentage, floor, user ceiling, or whole-operation reservation substituted for an exact
  next-step resource claim when the contract requires adaptive admission.
- A missing declared assertion, a PASS for an undeclared assertion, or a mechanism falsification
  relabelled as PASS.
- A threshold, budget, candidate set, baseline, or statistical plan frozen after result data existed.
- A bundle sealed while its claimed terminal operation remained active.
- Green created by a skip, deselection, platform gate, changed test, or changed verifier rather than
  by the reviewed behavior.
- An instrument whose output survives removal of the behavior it claims to observe.
- An emergency condition ignored because the contract has no recorded stop or hold result.

## Review envelope

Write these sections in order:

1. Scope, governing contract, and frozen identities.
2. Execution-bundle integrity and action/binding lineage.
3. Per-assertion status, evidence level, source trace, raw artifact, reviewer-designed challenge,
   expected and observed results, replay, false pass, and discriminator.
4. Cross-artifact, resource, and sensitivity findings; supported improvements with benefit,
   tradeoff, and verification method, plus rejected candidates and reasons. Recommendations do not
   change the frozen assertions or authorize remediation.
5. Primary and contributing cause; failure route.
6. Remediation lineage and complete gate, or `none`.
7. Invalidation class, scope digest, invalidated IDs, operation lineages, and qualification lineages.
8. Prior, expected, and new review-history heads; lease release; disposable-environment cleanup;
   and baton.

State: “This review changed no execution bundle, action template, principal action, assertion,
threshold, authority, permission, or live state. Replay in a non-live environment does not change a
live assertion's status or evidence level.”

End with exactly one baton:

- `PASS_READY`: every applicable assertion is `PASS` at its required level and the adversarial
  examination above is complete; the queue may apply its closure rule.
- `INCOMPLETE`: name every `NOT_RUN` or `BLOCKED` assertion and its exact prerequisite or missing
  evidence.
- `REMEDIATED`: name the exact child revision and invalidation route; the queue may schedule a new
  attempt on that child.
- `QUEUE_ROUTE`: name the governing authority, contract, template, environment, compatibility,
  safety, or out-of-bound action required.
