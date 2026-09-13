---
name: run-independent-build-review
description: Adversarially review one build stage or a declared ordered stage batch by tracing implementation, executing reviewer-designed challenges, and identifying supported defects and improvements. Use for code, build, machine-stage, and live-attempt review before acceptance, release, or handoff. One entrypoint covers live and non-live evidence; default to read-only work.
---

<!-- This skill defines a portable independent-review procedure; dependencies: the active request, repository instructions, governing authorities, frozen target state, and replayable evidence. -->
# Run Independent Build Review

## Select the review evidence

Start with the named claim and frozen candidate. A candidate may be one stage or a declared ordered
batch. Use read-only implementation and contract tracing by default. Run reviewer-designed mutation
work only when the claim cannot be decided otherwise; cross the live boundary only with explicit
authority. Use `references/machine-attempts.md` or `references/live-attempts.md` only for the
corresponding attempt class.

Review the declared result, not the implementer's confidence. A review is independent only when its questions, evidence, environment, and conclusion can expose a false green result.

## One review entrypoint

Use this skill for the whole review. Determine the evidence boundary from the requested claims and
governing contract; do not ask the user to choose another review skill.

- For code, static, fixture, integration, or platform review, use the workflow below.
- For a queue-managed non-live attempt, also read [the machine-attempt procedure](references/machine-attempts.md).
- For a sealed live attempt involving hardware, accounts, external services, model execution, or
  principal action, also read [the live-attempt procedure](references/live-attempts.md).
- A mixed review may need both internal procedures. Classify each claim separately; neither the
  project name nor the presence of a model makes every check live. Review missing live evidence as
  a gap, and continue independent checks that remain possible.

These references supply execution and evidence-handling details, not alternative skills or weaker
review standards. The adversarial examination below applies throughout. Ordinary code review needs
no campaign, lease, queue, or bundle architecture. A managed attempt follows its existing contract.
Review is read-only unless the active request or an explicitly authorized operating contract also
permits bounded remediation; an available repair procedure does not itself grant permission.

## Boundaries

- Default to read-only work. Without explicit remediation authority, do not edit, fix, commit, push, publish, or widen the target revision. An authorized isolated child remains separate from the frozen reviewed target.
- Establish the governing authorities and finite review questions before inspecting implementation details. Preserve conflicts; do not resolve them by invention.
- Preserve all user work. Capture state before the review and do not use destructive repository commands.
- Use mutations, fault injection, or destructive probes only in an isolated disposable copy, worktree, container, fixture, or environment that cannot affect the target.
- Keep implementer, reviewer, and executor roles distinct when the review requires independence. If they share a machine, account, or environment, disclose that limitation.
- Do not access live credentials, accounts, external services, or production systems unless the requester separately authorizes that boundary.
- A batch preserves every member's scope, acceptance, evidence, and verdict. Shared setup may run
  once, but a later green result cannot conceal a failed or unreviewed earlier member.

## Adversarial examination

Try to find a concrete way the implementation can violate each material review question. Read the
governing requirements, then trace the actual code and form failure hypotheses before relying on
the author's explanation or test results. Author summaries and previous reviews are claims to
investigate. A user-adopted specification remains authoritative regardless of who wrote it.

For each material question:

- Read the implementation from its real entrypoint through the deciding branches, relevant callees,
  state changes, and observable result. Cite file and symbol or line locations. Search results,
  comments, function names, and a list of opened files do not establish this trace.
- Identify assumptions that could fail within the declared behavior. Choose attacks from the code:
  boundary values, stale or conflicting state, alternate callers, interrupted operations, reordered
  events, or omitted input combinations where they matter. Explain which failure each attack could
  expose; a generic checklist is insufficient.
- Construct and run a reviewer-designed challenge that can distinguish correct behavior from that
  failure. Go beyond replaying the supplied examples: change a meaningful input, sequence, observer,
  or condition. Derive the expected result from the requirement. Existing helpers may be reused
  after checking that they preserve the condition being challenged.
- Observe the actual result or side effect at the deciding boundary. Verify that an earlier
  unrelated rejection did not prevent the challenge from reaching it. When a verdict relies on a
  guard or checker, remove, bypass, or contradict its assumption in a disposable target, or use an
  equivalent sensitivity control, and establish that the check detects the relevant difference.
- Inspect the author's tests and evidence for paths those checks cannot distinguish. Use them for
  comparison and regression evidence after establishing your own challenge.

These probes examine existing requirements; they do not add product requirements or authorize
changes to the reviewed implementation. Keep execution within the skill's isolation, profile, and
live-state boundaries. For a genuinely static question, show the source reasoning and counterexample
analysis. If required execution is unavailable, retain the static finding and mark the execution
gap explicitly; do not grant a behavioral pass.

Also examine the reviewed code for worthwhile improvements even when its correctness checks pass.
Consider simpler control flow, removable duplication, unnecessary work, clearer error recovery, or
stronger tests where the code supports the case. For each recommendation, cite the current code,
describe a concrete change, explain its benefit and tradeoff, and state how to verify the benefit.
Separate a proved defect, an unresolved hypothesis, and an optional improvement. A recommendation
does not become an acceptance failure unless it violates an existing requirement. Do not manufacture
findings or pad the report with generic advice; record the improvement candidates examined and why
they were recommended or rejected.

A clean verdict must identify the code paths examined, attacks actually executed, expected and
observed results, and remaining gaps. Replaying the author's green suite or agreeing with the
author's documentation is insufficient. Report an incomplete review when these checks remain
unperformed. Finding one defect does not finish the other material questions. Completion means the
bounded review was performed, not that the code is perfect or that a defect quota was met.

## Workflow

1. Freeze review scope. Record the requested decision, target revision, governing authorities in precedence order, finite questions, acceptance conditions, excluded areas, and external-state boundary. For a batch, also freeze its ID, exact ordered members, per-stage close records, and dependency graph; reject gaps, reordering, missing builder evidence, or cross-stage scope expansion.
2. Snapshot target state before any probe:
   - repository root, branch, HEAD, remotes if relevant, index state, and worktree status;
   - changed and untracked paths, including user-owned paths;
   - hashes or comparable identities for files and evidence that the review will rely on;
   - reviewer environment and executor environment identities.
3. Turn each review question into a claim with a named predicate, owning stage, entrypoint, expected observation, and nearest false pass. Use a control or contradiction pair when it can discriminate the result.
4. Inspect authorities and implementation separately. Record facts from each, then state only the inference the facts support. Do not accept comments, test names, dashboard counts, or closeout prose as proof without replayable evidence.
5. Replay the smallest credible proof for each claim. Prefer direct entry probes, independently constructed inputs, boundary observations, and negative controls. Record commands, inputs, outputs, environment identity, and result provenance.
6. When the claim depends on a failure boundary, test the intended failure in a disposable environment. Verify that the mutation applied, that the probe used the mutated target, and that the observed failure occurs for the named reason. A failed or misleading review instrument is a review finding, not automatically a production defect.
7. Classify every result as static, fixture, integration, platform, or live evidence. Do not represent fixture or platform evidence as live proof.
8. Reconcile results against the frozen acceptance conditions. Trace each failing foundation to dependent claims. In a batch, invalidate every later verdict whose proof depends on an earlier accepted finding until the affected evidence is replayed. Record untested claims as `NOT_RUN` and environmental prerequisites as `BLOCKED`.
9. Clean only disposable artifacts that the reviewer created and whose evidence has been retained. Re-read the target branch, HEAD, index, worktree status, and recorded file identities. Report any difference; do not repair it without authorization.

## Acceptance Checks

An independent review is complete only when:

- Authorities, review questions, target revision, and exclusions are explicit.
- The before-and-after target-state snapshots show that the review did not change the target.
- Each conclusion cites observed evidence and labels inference separately.
- Each material claim has a source trace and reviewer-designed challenge with observed results, or an explicit `NOT_RUN` or `BLOCKED` status. A static-only question records its counterexample analysis.
- Improvement candidates were examined and supported recommendations remain separate from defects.
- Controls, mutations, and adversarial probes ran only in a disposable environment and their reach was verified.
- The report distinguishes a production defect, an unproved claim, an environment limitation, and a defective review instrument.
- Evidence levels and remaining live gaps are explicit.
- Every batch member has its own questions, findings, evidence status, disposition, and verdict; the batch verdict cannot be cleaner than its least-complete member.

## Evidence Status Rules

- `PASS`: the frozen acceptance condition is satisfied by replayed, discriminating evidence at the required level.
- `FAIL`: credible evidence contradicts the acceptance condition.
- `NOT_RUN`: the required check was not run or cannot be identified.
- `BLOCKED`: a specific prerequisite outside the review boundary prevented the check.
- `STATIC`, `FIXTURE`, `INTEGRATION`, `PLATFORM`, and `LIVE` describe evidence level; they do not replace status.

Never infer `LIVE` from a test suite, a deployed artifact, or an authenticated-looking configuration. Never infer a production defect solely because a review harness, mutation, or fixture was defective.

## Output Contract

Return a bounded review report with these sections:

1. **Scope** — decision, target revision, authority order, questions, exclusions, and external boundary.
2. **State preservation** — before and after snapshots; identify every difference or state that could not be compared.
3. **Findings** — one row per review question, labelled with its owning stage, with status, evidence level, facts, inference, probe or replay, false pass/control, and exact gap.
4. **Defect classification** — production defects, unproved claims, environment limitations, and review-instrument defects as separate lists.
5. **Evidence ledger** — source traces, reviewer-designed attacks, expected and observed results, commands, inputs, outputs, identities, environment, and retention location. Include supported improvements with their benefit, tradeoff, and verification method, plus rejected candidates and reasons.
6. **Conclusion** — a separate verdict for every stage, the aggregate batch verdict when applicable, accepted conditions, failed conditions, `NOT_RUN` and `BLOCKED` conditions, dependent claims invalidated, and explicitly unreviewed areas. State whether the review itself is complete; any missing required source examination or challenge makes it incomplete even if the supplied tests passed.

State explicitly that the review made no implementation, repository, or external-state change unless separate authorization covered one.
