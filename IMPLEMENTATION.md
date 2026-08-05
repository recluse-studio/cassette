# IMPLEMENTATION.md — Cassette execution queue

This file is the order and state authority for building Cassette. AGENTS.md governs how code is
written; this file governs what is built next, what is already done, and when an agent stops.
The step queue below is the implementation counterpart of research/QUESTION_QUEUE.md: numbered,
dependency-ordered, machine-checkable, resumable.

## Execution protocol

**Command grammar.** The principal issues commands like "Execute S01 through S05", "execute the
next five steps", or "continue the queue". An agent executes the named range in order and does
not stop between steps.

**Straight line.** Work proceeds forward only. A step marked DONE is never reopened unless a
later step's invariant fails and names it — a regression reopens through a named failing
invariant, never through preference, style, or refactoring appetite.

**Per-step ritual.**
1. Read this file. Find the step. Verify its depends are DONE.
2. Make the step's invariants pass with the smallest change (AGENTS.md workflow).
3. Run done_when: the full test suite plus tools/ledger, not just the step's tests. Green means
   green everywhere — regressions never accumulate silently.
4. Set status DONE with date and commit hash. Commit with the AGENTS.md commit test answers plus
   the step id. Move to the next step immediately.

**Resume ritual (agent restart, platform restart, new session).**
1. Read this file top to bottom. The queue statuses are ground truth; git log corroborates.
2. Re-run done_when for the most recent DONE step. If green, continue at the first TODO whose
   depends are satisfied and whose env matches the platform. If red, that step reverts to
   IN_PROGRESS and is finished first.
3. Never redo DONE work. Never start a step whose depends are not DONE.

**Loop guards.**
- Attempt budget: three materially distinct approaches per step. If the third fails, set status
  BLOCKED with a report — what was tried, exact errors, the suspected cause, the invariant that
  will not pass — then continue with the next step that does not depend on it. Blocked is a
  recorded state, never a silent skip.
- Scope lock: touch only the step's listed files, plus discovered files recorded with one-line
  reasons. Work not demanded by the step's invariants is deferred to its own step or deleted.
- Size tripwire: exceeding roughly twice the step's expected size means stop and re-read the
  ledger contract — the design is being fought, and the contract wins.
- No polishing loops: formatting, renaming, and restructuring of DONE code are defects unless a
  named invariant demands them.

**Check-in policy.** Stopping to ask the principal is rare and reserved for: a remit-level
decision the ledger genuinely does not answer; credentials, purchases, or physical hardware; two
steps BLOCKED on the same root cause; or an action that is destructive or irreversible outside
this repository. Everything else is decided from the ledger, recorded in the step's notes, and
the work continues.

**Phase boundary.** PHASE MACHINE contains every step buildable and verifiable by agents alone:
scratch cartridges are APFS disk images, sources are deterministic fixture servers, storage
profiles are simulated from recorded class data, and small real models are downloaded by the
agent where a step says so. No PHASE MACHINE step asks the principal to test, plug in, or
observe anything. PHASE LIVE is one campaign, run with the principal present, against real
drives, real transfers, and the real matrix. It begins only when every PHASE MACHINE step is
DONE or BLOCKED-with-report.

**Environments.** env: any — runs anywhere Python runs. env: macos — requires Apple Silicon
(MLX/Metal, F_FULLFSYNC). env: macos+hardware — PHASE LIVE only. An agent on the wrong platform
takes the next eligible step or reports; it does not simulate a platform it lacks and call it
proven.

## PHASE MACHINE

```yaml
steps:
  - id: S01
    title: Scaffold and accounting skeleton
    env: any
    files: [pyproject.toml, tools/ledger.py]
    invariants: [Q29 acceptance (reproducible accounting, partial)]
    expected_size: small
    done_when: ledger runs clean on the tree; interpreter and dependency pins recorded
    depends: []
    status: DONE 2026-08-05 — ledger clean (exit 0), suite 2 passed, pins pytest==9.1.1 / python ==3.13.* (product pin, revisit recorded at S06); commit "S01"

  - id: S02
    title: Canonical error vocabulary
    env: any
    files: [errors.py]
    invariants: [Q6 error schema conformance]
    expected_size: small
    done_when: full suite + ledger green
    depends: [S01]
    status: TODO

  - id: S03
    title: Generated schemas and validators
    env: any
    files: [schema/ (generated), tools/ledger.py]
    invariants: [Q6/Q31 request-operation-event schemas, Q9 SourceDescriptor, Q50 preflight record, Q57 root and manifest schemas; F0 malformed/valid fixtures]
    expected_size: medium
    done_when: generated validators round-trip golden fixtures; hand-edit detection in ledger
    depends: [S02]
    status: TODO

  - id: S04
    title: Identity engine
    env: any
    files: [store.py]
    invariants: [Q1 acceptance (alias convergence, single-byte divergence, mutable-only rejection)]
    expected_size: small
    done_when: full suite + ledger green
    depends: [S03]
    status: TODO

  - id: S05
    title: Content pages, segments, TensorMap
    env: any
    files: [store.py]
    invariants: [Q57 acceptance (SafeTensors import, relocate without logical change, span resolution) on scratch cartridge images]
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S04]
    status: TODO

  - id: S06
    title: Transaction journal and atomic generations
    env: macos
    files: [store.py]
    invariants: [Q60 acceptance, Q73 acceptance, Q25 transaction subset — process-kill injection at every durable boundary, remount verification; F1 fixtures]
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S05]
    status: TODO

  - id: S07
    title: Integrity, repair states, capacity reservation
    env: any
    files: [store.py]
    invariants: [Q62 acceptance (corrupt page/index/root/parity), Q53 acceptance (exact-boundary and fragmented reservation)]
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S06]
    status: TODO

  - id: S08
    title: Cartridge lifecycle state machine
    env: macos
    files: [store.py]
    invariants: [Q49 acceptance (simulable subset - unmount, remount, identity mismatch, read-only, via disk images)]
    expected_size: small
    done_when: full suite + ledger green
    depends: [S07]
    status: TODO

  - id: S09
    title: Source adapter boundary and fixture server
    env: any
    files: [sources.py, tests/fixture_server.py]
    invariants: [Q52 acceptance (fixture-server substitution, five operations), Q9 acceptance (secret-free descriptor)]
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S03]
    status: TODO

  - id: S10
    title: Resumable verified transfer
    env: any
    files: [sources.py]
    invariants: [Q51 acceptance (random interruption, corrupt chunks, validator change, no post-completion reread) against the fixture server]
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S09, S07]
    status: TODO

  - id: S11
    title: Preflight and compatibility decision
    env: any
    files: [sources.py]
    invariants: [Q8/Q50 acceptance (trust states, contradictory fixtures), Q56 acceptance (four outcomes, no silent weakening)]
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S09]
    status: TODO

  - id: S12
    title: Runtime dispatch and golden operators
    env: macos
    files: [pager.py, schema/ (generated dispatch table)]
    invariants: [Q30 acceptance (golden tensors per dispatched dtype/shape/operator against reference), F2 fixtures; mlx confinement check in ledger]
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S03, S01]
    status: TODO

  - id: S13
    title: Memory budget and residency schedules
    env: any
    files: [pager.py]
    invariants: [Q47 acceptance (boundary sweeps on simulated profiles), Q63 schedule generation subset]
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S12]
    status: TODO

  - id: S14
    title: Page readiness, miss recovery, prediction hooks
    env: macos
    files: [pager.py]
    invariants: [Q20 acceptance (forced miss, corruption, timeout, cancel — replay-equal or typed termination), Q64 acceptance subset; F3 tiny-model fixtures]
    expected_size: large
    done_when: full suite + ledger green
    depends: [S13, S08]
    status: TODO

  - id: S15
    title: F3 end-to-end - tiny transformer from cartridge
    env: macos
    files: [pager.py]
    invariants: [F3 stage gates (forced misses, KV rollback), Q63 acceptance (trace equals schedule, no hidden allocation)]
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S14, S05]
    status: TODO

  - id: S16
    title: Canonical broker
    env: any
    files: [broker.py]
    invariants: [Q5 acceptance (interrupt every transition, idempotent replay), Q6 acceptance (double issue, cancel every phase, typed failures, monotonic events)]
    expected_size: large
    done_when: full suite + ledger green
    depends: [S03, S07]
    status: TODO

  - id: S17
    title: Scheduler, leases, negotiation
    env: any
    files: [broker.py]
    invariants: [Q65 acceptance (competing clients, switches, no stale cache), Q77 acceptance (exact pre-admission accept/reject)]
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S16]
    status: TODO

  - id: S18
    title: Named-agent adapters
    env: any
    files: [adapters/ (generated maps + shims)]
    invariants: [Q76 acceptance (bidirectional golden traces per named client), Q31 acceptance (round-trip without loss, capability rejection not fabrication)]
    expected_size: large
    done_when: full suite + ledger green
    depends: [S17]
    status: TODO

  - id: S19
    title: Streaming compiler and contribution map
    env: macos
    files: [compiler.py]
    invariants: [Q4 acceptance (peak-extent instrumentation, interruption, resume), Q58 acceptance (total map, structural failure on omission), Q60 resume on small dense model]
    expected_size: large
    done_when: full suite + ledger green
    depends: [S05, S06, S12]
    status: TODO

  - id: S20
    title: Plans and invalidation graph
    env: any
    files: [compiler.py]
    invariants: [Q11/Q59 acceptance (plan switch, zero weight payload in plans), Q27/Q75 acceptance (exact invalidation closure per change class)]
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S19]
    status: TODO

  - id: S21
    title: Trainer - paged Tier A on cartridge
    env: macos
    files: [trainer.py]
    invariants: [Q71 acceptance (tensor lifetime trace), Q72 acceptance (paged vs unpaged equivalence), Q73 child commit, Q25 interrupt/resume bit-exact, Q23 placement trace]
    expected_size: large
    done_when: full suite + ledger green
    depends: [S15, S06]
    status: TODO

  - id: S22
    title: Trainer - metering and admission
    env: any
    files: [trainer.py]
    invariants: [Q28 acceptance (projected vs metered writes on simulated profiles), Q74 acceptance (injection fixtures - low space, endurance, estimate drift)]
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S21]
    status: TODO

  - id: S23
    title: Failure-row generator
    env: any
    files: [tests/ (generated harness)]
    invariants: [matrix failure_rows injections x operations expanded from data; every simulable injection green]
    expected_size: medium
    done_when: full suite + ledger green; non-simulable injections enumerated for PHASE LIVE
    depends: [S18, S20, S22]
    status: TODO

  - id: S24
    title: F4 trace tooling and teacher capture
    env: macos
    files: [compiler.py, tools/ (analysis, generated)]
    invariants: [Q40 teacher trace capture on a permissively licensed 3-8B dense model (agent downloads via sources.py), Q19 metric computation machinery]
    expected_size: medium
    done_when: full suite + ledger green; trace corpus committed by digest
    depends: [S19, S10]
    status: TODO

  - id: S25
    title: F4 compile and simulator replay
    env: macos
    files: [compiler.py, tools/ (simulator, generated)]
    invariants: [prompt-persistent 3-8B revision built end-to-end; Q19 stability metrics computed; Q37 retention-versus-compression curves emitted against recorded storage-class profiles]
    expected_size: large
    done_when: full suite + ledger green; curves committed
    depends: [S24, S20]
    status: TODO

  - id: S26
    title: F4 GATE evaluation
    env: macos
    files: []
    invariants: [Q36 F4 GATE - touched_bytes<=0.25*native_active, Q19 stability, paired lower95CI(Qc/Q_teacher)>=0.95 within predeclared training budget]
    expected_size: medium
    done_when: gate outcome recorded PASS or Q38-FALSIFIED with report; either outcome completes the step
    depends: [S25, S21]
    status: TODO

  - id: S27
    title: Full accounting and removal map
    env: any
    files: [tools/ledger.py]
    invariants: [Q29 acceptance (reproduce J from clean checkout), Q78 removal map recorded per file]
    expected_size: medium
    done_when: full suite + ledger green; J report committed
    depends: [S23, S26]
    status: TODO

  - id: S28
    title: PHASE MACHINE closeout
    env: any
    files: []
    invariants: [every S-step DONE or BLOCKED-with-report; blocked report summary; PHASE LIVE runbook generated from matrix rows]
    expected_size: small
    done_when: closeout report committed; principal notified that the live campaign is ready
    depends: [S27]
    status: TODO
```

## PHASE LIVE — one campaign, principal present

```yaml
steps:
  - id: L01
    title: Storage qualification on real drives
    env: macos+hardware
    invariants: [Q41-Q44 acceptance - measured profiles, durable-flush qualification, falsified classes recorded]
    status: TODO
  - id: L02
    title: Live acquisition to cartridge
    env: macos+hardware
    invariants: [matrix source_rows - pinned revisions, ranged resume, digest pass, no internal model file]
    depends: [L01]
    status: TODO
  - id: L03
    title: F5 at 20-120B and F5 GATE
    env: macos+hardware
    invariants: [Q36 F5 GATE - predicates at scale, Q37 predicted frontier point vs E-011 budget; PASS or Q38-FALSIFIED recorded]
    depends: [L02]
    status: TODO
  - id: L04
    title: Frontier rows per matrix
    env: macos+hardware
    invariants: [execution_rows, workload_suites, protocol_cross_product, training_rows, remaining failure_rows, offline_and_privacy_rows]
    depends: [L03]
    status: TODO
  - id: L05
    title: Q80 completion run
    env: macos+hardware
    invariants: [complete matrix from clean checkout and blank qualified cartridges; one reproducible completion digest]
    depends: [L04]
    status: TODO
```

## Status vocabulary

TODO, IN_PROGRESS (with started date), DONE (with date and commit hash), BLOCKED (with report:
approaches tried, exact errors, suspected cause, failing invariant). No other statuses exist.
A BLOCKED step is revisited only when its root cause is resolved by a later step or a recorded
decision — never by retrying the same approach a fourth time.
