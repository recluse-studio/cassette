# AGENTS.md — Cassette build rules

Read ORIGINAL_REMIT.md, research/RESEARCH.md, and research/ACCEPTANCE_MATRIX.yaml before writing
anything. This file operationalizes Q29/Q30/Q32/Q33/Q78 and binds every agent and every commit.
This is the only instruction authority in this repository; CLAUDE.md and
.github/copilot-instructions.md are pointers to it.

## The objective

Minimize J = (failed_acceptance_rows, new_numerical_kernels, authored_executable_LOC,
independent_processes, language_runtimes, direct_dependencies, model_specific_branches,
duplicate_authorities, shipped_binary_bytes) in that lexicographic order. Correctness is never
traded for fewer lines. After correctness, fewer lines beat everything ranked below them.

## Language and runtime

- Authored language: Python. The exact interpreter version is pinned in pyproject.toml at first
  commit and is part of the J dependency record. No other authored language exists in this repo.
- Numerical runtime: MLX at one pinned commit, recorded in the lockfile. Cassette authors no
  kernels (Q30).
- llama.cpp/ggml, or any native shim (ObjC/C/Swift), may be added only after a recorded
  acceptance-row failure the current path cannot pass, and it is counted in J.
- One process, asyncio. Threads only in an executor for blocking I/O. No web framework, no ORM,
  no plugin system, no logging framework — stdlib carries the broker and the store.

## Files

- Layout mirrors the Q78 component map: one module per authority — broker, store, sources,
  compiler, pager, trainer — plus shared primitives. File boundaries are authority boundaries;
  the Q78 removal map is recorded per file.
- Soft target <=400 lines per file; a file over 800 requires naming the authority boundary that
  justifies it in the commit. Never split a file to satisfy a count if it creates plumbing;
  never merge two authorities to shrink the count. Import lines are authored LOC — splitting
  has a cost, count it.
- Line 1 of every authored file is one comment: what the file is, and every repo file it depends
  on. Example:

  `# pager.py — working-set prediction, page residency, miss recovery (Q19/Q20/Q63/Q64); depends on store.py, errors.py.`

  tools/ledger verifies declared dependencies equal actual intra-repo imports; a mismatch fails
  the accounting.

## Structure

- Layers, imports point downward only, no cycles:
  - L0 primitives: errors.py, schema/ (generated)
  - L1 store.py — identity, content-addressed pages, transactions, integrity, capacity, cartridge
    lifecycle
  - L2 components: sources.py, compiler.py, pager.py, trainer.py
  - L3 broker.py, adapters/ (generated maps + thin shims)
- Sibling law: L2 components never import each other. They exchange exactly two things —
  committed store objects (content-addressed, journaled) and broker-dispatched operations.
  Every cross-component interaction is therefore durable, inspectable, and replayable.
- One-writer law: every on-disk object type has exactly one writer module, recorded in a table
  in this file as objects are introduced. store.py grants extents and handles; no other module
  opens cartridge paths.

  | On-disk object type | Sole writer |
  |---|---|
  | Immutable root manifests, fixed-record physical page indexes, and content segments | `store.py` |
  | Transaction journals, candidate-generation temporaries, and immutable generation pointers | `store.py` |
  | Acquired source bytes and resumable transfer checkpoints inside store-granted extents | `sources.py` |
  | Immutable logical cartridge identity marker | `store.py` |
  | Integrity repair manifests, verified replicas, parity objects, and quarantined extents | `store.py` |

- Runtime confinement: mlx imports exist only in pager.py (execution) and trainer.py (autograd),
  through the generated Q30 dispatch table. An mx.* reference anywhere else fails the ledger.
- State machines are the unit of design: a component implements its ledger-named machines
  (Q5, Q20, Q25, Q49, Q60, Q62, Q73) and introduces no ad-hoc states.
- tools/ledger enforces all of this mechanically: the import edge set against the allowed graph,
  runtime confinement, header-dependency truth, and the per-file removal map.

## Before writing code

0. IMPLEMENTATION.md is the order and state authority: it decides which step is next, records
   what is DONE, and defines the loop guards, resume ritual, and check-in policy. Work outside
   the current step is a defect. Do not stop to ask the principal anything the ledger answers.
1. Name the acceptance row (research/ACCEPTANCE_MATRIX.yaml or a Qn acceptance_check in
   research/RESEARCH.md) that fails today. No failing row, no code.
2. Search the pinned runtime and stdlib for an existing primitive. Reuse beats authorship.
3. A dependency is admitted only with: exact subset used, pinned version, and the row it serves.
4. Write the smallest change that passes the row, then delete whatever the row no longer needs.

## Hard prohibitions

- No new general numerical kernel, ever, without a Q30 admission record.
- No model-specific branches. Model variation lives in data — manifests, plans, dispatch tables
  (Q33). `if model_family == ...` is a defect.
- No second authority: one digest engine, one transaction journal, one revision graph, one
  scheduler, one error vocabulary, one protocol schema (Q32). A convenient second copy is a
  defect.
- No speculative abstraction: no interface with one implementation, no config for a value with
  one setting, no future hooks. The ledger's reopen clauses are the future mechanism.
- No silent fallbacks (Q20): a missing invariant terminates with a typed error; it never degrades
  quality or substitutes a result.
- No hand edits to generated files. Schemas, validators, and dispatch tables are generated from
  the ledger's contracts at build time and reported separately in the accounting.

## What is free

Comments, docstrings, type hints, fixtures, and tests do not count as product LOC (Q29). Write
them for clarity and proof. Never densify executable code to game the count — minimize scope,
not whitespace.

## Tests

- The test surface is the ledger, closed and complete: the acceptance_checks in
  research/RESEARCH.md and the rows and assertions in research/ACCEPTANCE_MATRIX.yaml. Tests
  execute those invariants. There is no other source of tests.
- Every test cites the invariant it executes — a Qn acceptance_check or a matrix row assertion —
  in its name or docstring. tools/ledger resolves every citation and lists orphans; an orphan
  test is deleted, not kept "for safety."
- One fixture per invariant per stage, at the smallest F-stage that can disprove it (Q36). A
  second test of the same invariant at the same stage is a defect.
- Coverage is invariant coverage: every acceptance_check reachable at the current stage has at
  least one fixture. Line coverage is never a target — line-coverage targets manufacture
  meaningless tests.
- Failure tests are generated, not hand-written: the harness expands the matrix's
  injections × operations cross-product from data (Q33 applied to tests).
- No mocks of repo-internal modules. The sibling law makes this natural: components meet through
  store objects, so tests run against a real store on a scratch cartridge image. Mock only true
  boundaries: source servers (deterministic fixtures per Q52), hardware profiles, clocks.
- Determinism: deterministic invariants replay bit-identically from a clean root (Q16);
  statistical checks predeclare seeds, trial counts, and confidence bounds (Q17). A flaky test
  is a defect in the test.
- Tests must be passable or decidable. TDD tests are passable by construction. F4/F5 are
  falsification gates, not tests: their failure is a recorded Q38 outcome with a named
  consequence. A test that cannot pass and whose failure means nothing is deleted.
- "Tests are free" (Q29) means they cost nothing in the accounting — not that they are
  unaccountable. An uncited test is not free; it is noise.

## Byte and durability discipline

- Every admission computes its byte budget (Q47/Q53) and asserts it before allocating.
- Every durable write follows Q44: write → readback hash → F_FULLFSYNC → root → atomic pointer →
  F_FULLFSYNC. Never trust a file by name, size, or prior process state (Q60).
- Every error is one of the canonical typed errors (Q6). Inventing an error shape is a defect.

## Accounting and deletion proof

- tools/ledger recomputes J from a clean checkout: authored LOC, deps with declared subsets,
  processes, branches, binary closure, and file-header dependency verification. Any commit that
  raises a J component names the failing row justifying it.
- Q78 removal map: for every original component, record the row that fails when it is deleted.
  A component with no such row is deleted now.

## The commit test

Every commit message answers three questions: (1) which row failed before this change; (2) what
was reused instead of authored; (3) what was deleted. "Nothing was deleted" is an acceptable
answer; an unanswered question is not.

Published history is not rewritten merely to repair a malformed commit message. One later,
otherwise compliant descendant commit may supply each missing answer exactly once as
`Commit-law repair <full-commit-sha> <Failed before|Reused instead of authored|Deleted>: <answer>`.
The target must be a governed ancestor, the named field must be absent from its original message,
and malformed, duplicate, prospective, unknown-target, or already-answered repairs fail the ledger.
