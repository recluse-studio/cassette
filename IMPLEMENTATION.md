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
later step's invariant fails and names it, or a review names a failing invariant against the
step's own rows — a regression reopens through a named failing invariant, never through
preference, style, or refactoring appetite.

**Per-step ritual.**
1. Read this file. Find the step. Verify its depends are DONE.
2. Make the step's invariants pass with the smallest change (AGENTS.md workflow).
3. Run done_when: the full test suite plus tools/ledger, not just the step's tests. Green means
   green everywhere — regressions never accumulate silently.
   Record elapsed time only as diagnostic context unless the governing row declares a latency
   threshold; test count, skip count, and invariant results are the completion evidence.
4. Before marking the step DONE, list every acceptance clause named by the step. For each clause,
   record the exact test or probe, the exact input changed or failure injected, the expected
   result, and the observed result. A test name or total passing-test count is not evidence. Any
   missing clause keeps the step IN_PROGRESS.
5. Close in two commits, because a commit cannot contain its own hash: first the step commit
   (code and tests), then a close commit that sets this file's status to DONE with date and the
   step commit's hash. Every commit — step, close, repair, docs — answers the AGENTS.md commit
   test; close-commit answers may be short but must exist, and tools/ledger enforces this
   mechanically for every commit after the law baseline. The queue authority is never left dirty.

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

**Phase boundary.** PHASE MACHINE contains S00 through S28 and uses only deterministic generated or
checked-in model fixtures, loopback source fixtures, scratch cartridge images, and simulated
recorded storage classes. It performs no live model download, touches no physical external drive,
inspects no attached storage or local model cache, and asks the principal for no physical action.
S28 closes this machine and emits the runbook. PHASE LIVE begins only afterward, with the principal
present, and owns the first live source request, selected real-model download, physical-drive use,
and real matrix execution. No audit, research obligation, or dependency correction may move those
inputs earlier.

**Environments.** env: any — runs anywhere Python runs. env: macos — requires Apple Silicon
(MLX/Metal, F_FULLFSYNC). env: macos+hardware — PHASE LIVE only. An agent on the wrong platform
takes the next eligible step or reports; it does not simulate a platform it lacks and call it
proven.

## PHASE MACHINE

**Mathematical cutover, 2026-08-09.** S01-S11 remain closed: none implements a compiled selector,
rank decomposition, prompt-fixed page set, or stochastic correction scheme. MATHS.md now governs
S12 onward. Every future compiled plan separates condition compatibility, atom capacity,
description distortion, execution error/risk, composition, observation adequacy, and physical
resources. The former prompt-persistent/router mechanism remains eligible only as a certified
special case.

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
    historical_status: "DONE 2026-08-07 — repair b718da2 adds fail-closed append-only correction records for immutable published messages; full suite 20 passed in 27.37 seconds; ledger clean with 1,512 product LOC, 930 test LOC, 356 tool LOC, one process, one runtime, and the three existing exact dependency pins"
    status: DONE 2026-08-09 — audit remediation 306055ddefb4e5d5a735c3dc5e4ae6e09b7d57c0 replaces recursive ownership with Git-governed source discovery and pyvenv.cfg environment boundaries; focused S01 fixtures passed 5/5, the complete macOS suite passed 28/28 in 1,024.50 seconds, and the ledger remained clean at 2,813 product LOC, 2,237 test LOC, 470 tool LOC, 74 generated LOC, one process, one runtime, and five exact pins
    audit_remediation_closeout:
      - clause: "Q29 accounting excludes foreign environments without hiding governed new source"
        test_or_probe: "tests/test_s01_ledger.py::test_ledger_reproducible_from_clean_checkout at 306055d plus the complete S01 file"
        input: "Create real Python environments under local-python and build/runtime-3.13, each containing a hostile foreign_runtime.py that imports mlx and store; then add an untracked compiler.py and stage trainer.py."
        expected: "Both environments leave the byte-identical clean ledger report unchanged. The untracked and staged Cassette files enter files_checked, accounting, header, import-graph, and runtime-confinement checks."
        observed: "The environment-bearing report remained byte-identical. The governed report named exactly compiler.py and trainer.py as additions, rejected compiler.py's MLX and sibling imports, and the complete S01 file passed 5 tests."
      - clause: "The governed-source boundary is consequential"
        test_or_probe: "guard-removal mutation in a disposable clone of 306055d"
        input: "Replace Git-governed discovery with recursive Python-file discovery, then rerun the Q29 fixture."
        expected: "The fixture fails because foreign environment files contaminate J and policy scans."
        observed: "The fixture failed: both foreign_runtime.py files entered files_checked, product LOC rose from 2,813 to 2,817, and six false header, import, and MLX-confinement violations appeared. The disposable clone was deleted."

  - id: S02
    title: Canonical error vocabulary
    env: any
    files: [errors.py]
    invariants: [Q6 error schema conformance]
    expected_size: small
    done_when: full suite + ledger green
    depends: [S01]
    status: DONE 2026-08-05 — step commit 28bca29; reopened by review R1 (repaired d763d74: Q6 payload type enforcement), R2 clean for S02 rows; suite 5 passed, ledger clean. Environment note: the sandbox mount permits rename but not unlink on git lock files, so agents sweep them into .git/stale-locks/ before and after git operations. No principal action required.

  - id: S03
    title: Generated schemas and validators
    env: any
    files: [schema/ (generated), tools/ledger.py]
    invariants: [Q6/Q31 request-operation-event schemas, Q9 SourceDescriptor, Q50 preflight record, Q57 root and manifest schemas; F0 malformed/valid fixtures]
    expected_size: medium
    done_when: generated validators round-trip golden fixtures; hand-edit detection in ledger
    depends: [S02]
    status: DONE 2026-08-06 — prior draft 14c2d99 was not accepted; definitive repair aad81b9 emits the complete Q6/Q9/Q31/Q50/Q57 Draft 2020-12 contract set, validates full golden JSON round-trips and malformed F0 records, and regenerates during ledger integrity checks; pinned Python 3.13 / pytest 9.1.1 suite 12 passed after the repair commit, all 12 schemas passed Draft 2020-12 metaschema validation, ledger clean

  - id: S04
    title: Identity engine
    env: any
    files: [store.py]
    invariants: [Q1 acceptance (alias convergence, single-byte divergence, mutable-only rejection)]
    expected_size: small
    done_when: full suite + ledger green
    depends: [S03]
    status: DONE 2026-08-06 — remediation step commit 9893075; literal source_alias and requested_revision probes converge after one canonical locator and immutable digest, a one-byte artifact change diverges, mutable references and malformed digest evidence mint no identity, and derived revisions require both BLAKE3 parent identities and a BLAKE3 transform digest; exact blake3==1.0.9 and rfc8785==0.1.4 dependencies replace the split SHA-256/custom-JSON authority; discovered scope records those pins in pyproject.toml, confines product identity primitives through tools/ledger.py, and executes the Q1/Q32 clauses in tests/test_s04_identity.py; committed-HEAD suite 16 passed, ledger clean with 147 product LOC and no violations

  - id: S05
    title: Content pages, segments, TensorMap
    env: any
    files: [store.py]
    invariants: [Q57 storage acceptance (SafeTensors and bounded GGUF import, relocate without logical change, span resolution, ordered training-delta append) on scratch cartridge images]
    acceptance_boundary: "S05 owns the container-to-canonical-page representation that does not depend on a trained child: verified SafeTensors and GGUF import, TensorMap resolution, representation-independent repacking, and immutable ordered delta-page append. S24 owns Q57's eligible-export clause together with Q26, after S21 supplies real tuned-child composition and callability; export cannot be proved honestly before those semantics exist."
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S04]
    status: DONE 2026-08-06 — repair step commit 12719d9; Python 3.13 full suite 17 passed; ledger clean with 540 product LOC and no new dependency; official safetensors==0.6.2 writer probe recovered 4,194,311 exact bytes
    closeout:
      - clause: "SafeTensors import"
        test_or_probe: "tests/test_s05_store.py::test_q57_safetensors_import_relocation_and_span_resolution plus an independent safetensors==0.6.2 writer probe"
        input: "Two v0.6.2 shards supplied by canonical path in reverse insertion order: head=4,194,301 U8 bytes and crossing=10 U8 bytes in shard 1; tail=13 U8 bytes in shard 2. First supply a complete Q1 tuple with one unrelated artifact digest, then the tuple whose paths, sizes, and digests match the files. Bind a parent, three operators, and tokenizer/processor/template digests. The independent writer supplies one 4,194,311-byte U8 tensor."
        expected: "Reject the unrelated Q1 evidence without publishing a root. For valid evidence, derive the identity inside the importer; retain the canonical Q1 preimage; bind parents, operators, and semantic assets from it; cover pages, manifests, and semantic assets with the root aggregate; produce the same logical root for either source-map order; recover every byte."
        observed: "The false tuple terminated with IDENTITY_MISMATCH and produced no root. Both source orders produced root blake3:0354082adb25adf24c6984743663095844df91151e8bbd0dca4aa7a3e51f6347 with identity blake3:a43cccce52c8101e1859c78dcb66d35232e55f1836ed39e6e9dd83031d944f88 and integrity root blake3:f630a6c61097a6c632a891f9344f7021f37f8f36e842345028597ea5cda27b2b. Reload rejected an identity mutation and a manifest mutation omitted from the aggregate. The independent writer produced root blake3:1295b2f03f7471b87654a5db0c51d80f36e98089fe6a029d1be97e23200e5f0e and recovered all 4,194,311 bytes."
      - clause: "Relocate without logical change"
        test_or_probe: "tests/test_s05_store.py::test_q57_safetensors_import_relocation_and_span_resolution and the matching direct layout probe"
        input: "Reverse the active order of all three page digests and repack the scratch cartridge."
        expected: "Physical segment identity or page offsets change; logical root, tensor maps, and resolved bytes do not change."
        observed: "Active segment changed from blake3:d8468d3ddbace21feb32173f2882bfd9e3d9215a55e04e7ea243b4a97a4653c7 to blake3:cb8d67ca90694c59a2af8b774c601c913efd214a2a57db9f91a6fa83932aed83; the root remained blake3:0354082adb25adf24c6984743663095844df91151e8bbd0dca4aa7a3e51f6347; identity, integrity aggregate, tensor maps, and every resolved byte remained exact."
      - clause: "Span resolution"
        test_or_probe: "tests/test_s05_store.py::test_q57_safetensors_import_relocation_and_span_resolution and the matching direct span probe"
        input: "Place the 10-byte tensor 3 bytes before the 4 MiB page boundary, then resolve it before and after repacking."
        expected: "Spans (offset=4,194,301,length=3,tensor_offset=0) and (offset=0,length=7,tensor_offset=3) reconstruct b'0123456789'."
        observed: "The emitted spans matched both tuples exactly, and the reconstructed tensor equaled b'0123456789' before and after repacking."

  - id: S06
    title: Transaction journal and atomic generations
    env: macos
    files: [store.py]
    invariants: [Q60 acceptance, Q73 acceptance, Q25 transaction subset — process-kill injection at every durable boundary, remount verification; F1 fixtures]
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S05]
    status: DONE 2026-08-07 — original step aabe102 and close c266598; definitive review repair 31bf248; committed repair passed from a clean clone under CPython 3.13.14 with 18 tests in 29.88 seconds and a clean ledger at 1,062 product LOC, 651 test LOC, one runtime, one product process, and no new dependency or numerical kernel
    closeout:
      - clause: "Q25 transaction subset and Q60/Q73 process death at every durable boundary"
        test_or_probe: "tests/test_s06_transactions.py::test_q25_q60_q73_process_death_remount_resume_and_reader_isolation"
        input: "Publish a one-segment child root over generation 1. Start a fresh writer process for PREPARE and for every later journal boundary: candidate write, readback hash, candidate full-sync, candidate-root verification, entry to FULLFSYNC, each segment/index/root file full-sync, each dependency-directory sync, dependency re-verification, generation-pointer swap, pointer-file full-sync, generation-directory sync, cartridge-directory sync, and COMMITTED verification. Kill each writer with SIGKILL after it reports the durable state, then detach and reattach the 64 MiB APFS cartridge image."
        expected: "Before the pointer swap, remount exposes generation 1 and its exact parent bytes. From a persisted pointer swap onward, remount exposes generation 2 and its exact child bytes. Repeating the journal transition after death is idempotent; no candidate root becomes callable early."
        observed: "Eighteen writer processes were killed and followed by eighteen APFS detach/reattach cycles. Every remount before SWAP_GENERATION_POINTER selected generation 1 and b'parent-generation-bytes'; every remount from the swap through COMMITTED selected generation 2 and b'exact-child-generation'. Replaying the completed transaction returned the same generation-2 pin, while changing its candidate under the same idempotency key returned IDEMPOTENCY_CONFLICT."
      - clause: "Q60 corrupt temporary and journal recovery without a partial callable root"
        test_or_probe: "the corrupt-temp and corrupt-journal phases of tests/test_s06_transactions.py::test_q25_q60_q73_process_death_remount_resume_and_reader_isolation"
        input: "Replace the WRITE_TEMP candidate with b'corrupt candidate', remount, and resume from a journal containing operation version fixture-transform-v1, two input digests, seed 17, statistics and RNG digests, optimizer step 23, data cursor 29, hexadecimal loss scale, and the exact sorted page results. Separately replace a prepared generation-5 journal with b'corrupt journal' and remount."
        expected: "A suspect uncommitted candidate is rebuilt from its digest-bound journal and publishes the exact child. A journal whose provenance cannot be recovered returns one typed reacquisition error, leaves the current generation callable, and publishes no partial generation."
        observed: "The candidate was rewritten, read back, full-synced, and committed as generation 4 with the exact child tensor bytes; every restart field and page result survived in canonical journal bytes. The corrupt journal returned SOURCE_UNAVAILABLE, generation 4 remained callable, and no generation-5 pointer existed."
      - clause: "Q73 all-parent/all-child reader isolation, highest-valid recovery, rollback retention, and GC safety"
        test_or_probe: "the concurrent-reader, corrupt-generation, rollback, and garbage-collection phases of tests/test_s06_transactions.py::test_q25_q60_q73_process_death_remount_resume_and_reader_isolation"
        input: "Run a separately pinned parent reader for 200 exact reads during each of the eighteen writer boundaries; corrupt generation 4's pointer bytes and remount; restore its exact bytes; publish the prior root as generation 3; create .orphan.pending and material/.material-orphan.pending, then invoke collection."
        expected: "The old reader never observes child or mixed bytes. Recovery skips an invalid highest generation and selects the highest remaining valid generation. Rollback publishes the prior root without rewriting or deleting either revision. GC reports and removes exactly the two unreachable transaction temporaries and preserves every retained or pinned root."
        observed: "All 3,600 concurrent parent reads returned b'parent-generation-bytes'. With generation 4 corrupt, remount selected valid generation 3; restoring the exact pointer restored generation 4. Rollback made the parent root generation 3 while the generation-2 child remained readable. Collection reported and removed exactly .orphan.pending and .material-orphan.pending, retained generation files 1, 2, and 3, and both pinned roots still returned exact bytes."
      - clause: "F1 APFS durability fixture and S01 interpreter-pin revisit"
        test_or_probe: "the complete S06 fixture plus committed-HEAD full suite and tools/ledger.py"
        input: "Run on arm64 macOS 26.5.2 with an APFS sparse cartridge, os.fsync plus fcntl.F_FULLFSYNC, hdiutil detach/reattach, CPython 3.13.14, pytest 9.1.1, blake3 1.0.9, and rfc8785 0.1.4."
        expected: "Real macOS durable synchronization and remount pass without changing the recorded Python 3.13 pin, adding a dependency, leaving a mounted fixture, or violating J."
        observed: "The committed-HEAD suite passed 18 tests in 21.53 seconds; the ledger reported 986 product LOC, 524 test LOC, 324 tool LOC, one Python runtime, one product process, the three existing exact dependency pins, and zero violations. CPython 3.13.14 satisfied the existing ==3.13.* pin, and hdiutil reported no remaining S06 mount."
    repair_closeout:
      - clause: "Q60 exact restart material survives on the cartridge rather than only as an unverifiable digest"
        test_or_probe: "the restart-material phases of tests/test_s06_transactions.py::test_q25_q60_q73_process_death_remount_resume_and_reader_isolation"
        input: "Begin corrupt-temp with exact statistics bytes b'S06 statistics', RNG bytes b'S06 RNG state', seed 17, optimizer step 23, data cursor 29, loss scale 0x1.0000000000000p+0, two input roots, and sorted page results. Corrupt each content-addressed restart object independently, remount, restore its exact bytes, reconstruct TransactionContext from the cartridge, and resume with that reconstructed object. Separately kill object publication after raw write, readback, F_FULLFSYNC, atomic replace, and material-directory sync."
        expected: "A missing or corrupt restart object returns SOURCE_UNAVAILABLE before a transition. Restored objects reconstruct the original context byte-for-byte and commit the exact child. Death at any material-object boundary leaves no journal or callable child and retries idempotently from the retained parent."
        observed: "Both corruptions returned SOURCE_UNAVAILABLE while generation 3 remained exact; both restored objects reconstructed a TransactionContext equal to the original and committed generation 4. Five material-publication writers were killed at the five internal boundaries; every remount retained generation 4, exposed no premature journal for the interrupted transaction, and accepted an exact retry."
      - clause: "Q73 child_id is the declared parent, training, ordered-page, and semantic-manifest hash"
        test_or_probe: "the independent _q73_child_id calculation and canonical child-id substitution in tests/test_s06_transactions.py::test_q25_q60_q73_process_death_remount_resume_and_reader_isolation"
        input: "Independently hash parent_id, the complete training manifest, sorted page digests, and the root's identity, parents, semantic assets, tensor maps, operators, and deltas. Then replace generation 4's child_id with the well-formed Q1 identity, recompute the envelope digest and canonical JSON, full-sync it, and remount."
        expected: "Every published child_id equals the independent Q73 formula. A canonically valid envelope carrying the prior Q1 identity is not accepted as the child identity; recovery selects the highest remaining valid generation."
        observed: "Generations 1, 2, 3, and 4 matched the independent formula. The rehashed Q1 substitution returned ROOT_INVALID, and recovery selected exact rollback generation 3 until the original generation-4 bytes were restored."
      - clause: "Q25/Q60/Q73 process death covers actions before journaling and every journal primitive boundary"
        test_or_probe: "the before_journal and journal_write/readback/fullsync/replace/directory_sync matrix in tests/test_s06_transactions.py::test_q25_q60_q73_process_death_remount_resume_and_reader_isolation"
        input: "For PREPARE and all seventeen later transitions, stop immediately before the journal update, then kill the writer and remount. Sixteen later transitions first execute their candidate write, readback, file or directory sync, dependency verification, generation rename, or committed verification. WRITE_CANDIDATE_ROOT to FULLFSYNC has no separate production action before its journal publication. Across the first five transitions, also kill inside durable journal replacement after write, readback, F_FULLFSYNC, os.replace, and directory sync. Keep one parent-root reader running for 200 reads during every killed writer."
        expected: "Before journal replacement, recovery repeats the prior transition without losing the completed idempotent action; after replacement, it resumes from the new transition. A generation rename makes the exact child callable even if the journal still names the prior state. Every reader remains pinned to all-parent bytes."
        observed: "Twenty-three transaction writers and five restart-object writers were killed at the corrected boundaries. Every remount selected the exact prior or next journal frontier dictated by whether replacement had occurred; the generation-rename window selected the exact child and resumed from the stale journal; all 5,600 concurrent parent reads returned b'parent-generation-bytes'."
      - clause: "S06 platform proof does not block env:any work on an ineligible runner"
        test_or_probe: "the module-level skip condition in tests/test_s06_transactions.py plus the clean-clone arm64 macOS proof"
        input: "Collect the fixture on any runner; execute it only when platform.system() is Darwin and platform.machine() is arm64. On arm64 macOS, run the complete suite from committed repair 31bf248 with dependencies installed outside the checkout."
        expected: "An ineligible runner reports the explicit APFS/F_FULLFSYNC requirement rather than a failed invariant; only an executed arm64 macOS fixture supplies S06 platform evidence. The eligible committed checkout passes the full suite and ledger without repository-local environment artifacts."
        observed: "The fixture now declares its exact skip condition instead of asserting the platform. The clean arm64 macOS clone executed all 18 tests in 29.88 seconds; tools/ledger.py reported 1,062 product LOC, 651 test LOC, 324 tool LOC, three existing exact pins, and zero violations; no S06 mount or repository-local runtime remained."

  - id: S07
    title: Integrity, repair states, capacity reservation
    env: any
    files: [store.py]
    invariants: [Q62 acceptance (corrupt payload/index/manifest/root/parity, repair, exact unavailable pages), Q53 acceptance (exact-boundary, fragmented, concurrent-reservation, growing-transform, training, and repair)]
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S06]
    status: DONE 2026-08-07 — reopened at a3d67a1; complete storage contract fa2a68c; closeout 425c384; independent mutation proof 1b14712; Q29 gate repair b718da2; full suite 20 passed in 27.37 seconds; ledger clean with 1,512 product LOC, 930 test LOC, 356 tool LOC, one process, one runtime, and the three existing exact dependency pins
    closeout:
      - clause: "Q53 exact boundary, phase maximum, safety floor, and terminal release"
        test_or_probe: "tests/test_s07_integrity_capacity.py::test_q53_exact_fragmented_concurrent_growing_training_and_repair_capacity"
        input: "Reserve phases of 800 and 1,300 bytes on a 200 GiB device with exactly 10 GiB plus 1,300 bytes free; repeat on a 100 GiB device; release the first reservation twice."
        expected: "Use the phase maximum rather than their sum, apply max(8 GiB, 5% of device), admit equality through one exact preallocation, and release the owned extent once at terminal cleanup."
        observed: "The 200 GiB case requested exactly 10,737,419,540 bytes with 10 GiB safety; the 100 GiB case used 8 GiB safety. Equality admitted. Two cleanup calls produced one exact release and left the immutable reservation inactive."
      - clause: "Q53 fragmented, concurrent, and overflowing reservations"
        test_or_probe: "tests/test_s07_integrity_capacity.py::test_q53_exact_fragmented_concurrent_growing_training_and_repair_capacity"
        input: "Offer sufficient aggregate bytes in two undersized fragments; race two operations against one exact extent while both receive the same stale free-byte report; add one byte to the maximum unsigned phase value."
        expected: "Reject fragmentation, admit exactly one concurrent owner, and reject overflow before any allocator call."
        observed: "Fragmentation returned CAPACITY_EXCEEDED. The locked extent boundary admitted one racer and rejected one, then recovered the complete extent on one release. Overflow returned CAPACITY_EXCEEDED without calling the allocator."
      - clause: "Q53 growing-transform phase admission"
        test_or_probe: "tests/test_s07_integrity_capacity.py::test_q53_exact_fragmented_concurrent_growing_training_and_repair_capacity"
        input: "Declare transform phases of 5 GiB plus 1 byte and 13 GiB plus 1 byte on a 400 GiB device, then offer exactly 33 GiB plus 1 byte and one byte less."
        expected: "Reserve the later growth peak plus 20 GiB safety; reject the short case before mutation."
        observed: "The exact 35,433,480,193-byte extent admitted. One byte less returned CAPACITY_EXCEEDED before preallocation; the transform-source sentinel remained unchanged."
      - clause: "Q53 training phase admission"
        test_or_probe: "tests/test_s07_integrity_capacity.py::test_q53_exact_fragmented_concurrent_growing_training_and_repair_capacity"
        input: "Declare one 20 GiB plus 17 byte training phase containing committed, candidate, rollback, optimizer, master, dataset, precision, and journal bytes on a 400 GiB device; offer exactly 40 GiB plus 17 bytes and one byte less."
        expected: "Account for the complete training state, reserve the exact phase plus safety, and reject the short case before mutation."
        observed: "The exact 42,949,672,977-byte extent admitted. One byte less returned CAPACITY_EXCEEDED before preallocation; the training-revision sentinel remained unchanged."
      - clause: "Q53 repair admission and reservation lifetime"
        test_or_probe: "tests/test_s07_integrity_capacity.py::test_q53_exact_fragmented_concurrent_growing_training_and_repair_capacity"
        input: "Create a repair set first under a one-byte repair phase, then under 1 GiB; release the admitted reservation and attempt repair with it."
        expected: "Reject before creating repair paths when the phase cannot contain the repair set; write only under an active sufficient reservation; reject use after terminal release."
        observed: "The one-byte case returned CAPACITY_EXCEEDED with no repair directory. The 1 GiB case created the set. Its released reservation then returned INVALID_REQUEST before repair mutation."
      - clause: "Q62 corrupt payload detection and parity repair"
        test_or_probe: "tests/test_s07_integrity_capacity.py::test_q62_corrupt_payload_index_manifest_root_and_parity_repair"
        input: "Flip one alpha-page byte, attempt tensor use, verify, and repair from the independently checked XOR parity and valid beta page."
        expected: "Reject before yielding tensor bytes; name only the corrupt page; traverse CORRUPT through REPAIRING to VALID; restore the original page and segment identities."
        observed: "Tensor use returned PAGE_CORRUPT. Verification named only blake3:149d80aea7939e97b857b058b5e0efa787e6afc78c6468285d32b5fa62b9da74. Repair restored b'alpha-page-contents' and the original segment digest."
      - clause: "Q62 corrupt index repair"
        test_or_probe: "tests/test_s07_integrity_capacity.py::test_q62_corrupt_payload_index_manifest_root_and_parity_repair"
        input: "Flip one fixed-record index byte, attempt root loading, and repair from the verified index copy."
        expected: "Reject before root use and restore the exact original index digest through the declared states."
        observed: "Root loading returned ROOT_INVALID; repair traversed SUSPECT, VERIFYING, CORRUPT, REPAIRING, VALID and restored byte-identical index content."
      - clause: "Q62 corrupt integrity-manifest repair"
        test_or_probe: "tests/test_s07_integrity_capacity.py::test_q62_corrupt_payload_index_manifest_root_and_parity_repair"
        input: "Flip one byte in the primary integrity repair manifest while retaining its independently verified replica, then verify, require, and repair the revision."
        expected: "Detect the manifest before run use, mark every potentially addressable page unavailable, preserve the replica, and restore the primary manifest to its original digest."
        observed: "Verification traversed the manifest to CORRUPT and returned both exact page IDs; require_revision returned PAGE_CORRUPT; repair traversed REPAIRING to VALID and restored byte-identical manifest content while the replica remained unchanged."
      - clause: "Q62 corrupt root repair"
        test_or_probe: "tests/test_s07_integrity_capacity.py::test_q62_corrupt_payload_index_manifest_root_and_parity_repair"
        input: "Flip one canonical-root byte, attempt root loading, and repair from the verified immutable root copy."
        expected: "Reject before root use and restore the exact original root identity through the declared states."
        observed: "Root loading returned ROOT_INVALID; repair traversed SUSPECT, VERIFYING, CORRUPT, REPAIRING, VALID and restored canonical bytes whose direct BLAKE3 equals the unchanged root identity."
      - clause: "Q62 corrupt parity repair"
        test_or_probe: "tests/test_s07_integrity_capacity.py::test_q62_corrupt_payload_index_manifest_root_and_parity_repair"
        input: "Flip one parity byte while both pages remain valid, verify, and rebuild parity from those pages."
        expected: "Keep valid model pages available while marking parity CORRUPT; restore the independently computed XOR bytes and original parity digest."
        observed: "The revision remained available; parity traversed SUSPECT, VERIFYING, CORRUPT, REPAIRING, VALID and returned byte-identically to the direct XOR oracle."
      - clause: "Q62 unrecoverable page and verified-source restoration"
        test_or_probe: "tests/test_s07_integrity_capacity.py::test_q62_corrupt_payload_index_manifest_root_and_parity_repair"
        input: "Corrupt alpha and its sole parity together; first supply a source payload that fails its declared digest, then attempt repair without a source, require the revision, and finally supply exact alpha bytes."
        expected: "Reject an invalid source before mutation; end the unrecoverable page at UNAVAILABLE; reject the affected run with its exact page ID; accept only exact source bytes and preserve logical identity."
        observed: "The invalid source returned INVALID_REQUEST with segment and parity unchanged. Repair without a source named only the alpha page UNAVAILABLE; run admission returned PAGE_CORRUPT with that page object_id. Exact source bytes restored page, parity, root, and availability."
      - clause: "S07 fixtures state the contract independently"
        test_or_probe: "three disposable clean-checkout mutation runs against tests/test_s07_integrity_capacity.py"
        input: "Replace phase maximum with phase sum; force a corrupt primary manifest to report valid; undercount the two physical manifest copies as one."
        expected: "The Q53 fixture must reject the arithmetic mutation; the Q62 fixture must reject both manifest mutations."
        observed: "All three mutants failed at the intended independent assertion: exact required bytes, exact unavailable page IDs, and exact repair-set physical bytes, respectively. The disposable clones were then removed."
      - clause: "S07 full regression and accounting gate"
        test_or_probe: "the complete pinned Python 3.13 suite and tools/ledger.py from committed repair b718da2"
        input: "Run every fixture, including the clean-checkout Q29 reproduction, then recompute J, tracked artifacts, generated integrity, commit law, imports, citations, pins, and runtime confinement."
        expected: "Every test passes and the ledger reports no violation before S07 becomes DONE."
        observed: "All 20 tests passed in 27.37 seconds. The ledger reported zero violations, 1,512 product LOC, 930 test LOC, 356 tool LOC, 58 generated LOC, one process, one Python runtime, and the three existing exact pins."

  - id: S08
    title: Cartridge lifecycle state machine
    env: macos
    files: [store.py, AGENTS.md]
    discovered_scope: "AGENTS.md records store.py as the sole writer of the Q49 identity marker."
    invariants: [Q49 acceptance (APFS-image state machine - unmount/remount, disconnect/reconnect, sleep/wake, bus reset, port migration, logical/filesystem UUID mismatch, read-only remount, verified cloned replacement, no stale access)]
    acceptance_boundary: "S08 proves the shared Q49 lifecycle authority and APFS-image fixture against the store operations available at this step. S23 owns failure-row coordinate generation and the shared-authority preflight. S24 completes the fixture export and exact revision-removal entrypoints. S26 owns Q49 injection through all eight concrete operation paths after those operations exist."
    expected_size: small
    done_when: full suite + ledger green
    depends: [S07]
    status: DONE 2026-08-07 — step commit 44e044c; committed-step suite 21 passed in 38.36 seconds; ledger clean with 1,702 product LOC, 1,121 test LOC, 356 tool LOC, one process, one runtime, and the three existing exact dependency pins
    closeout:
      - clause: "Q49 durable logical identity, exact mount identity, unmount/remount, and stale-access rejection"
        test_or_probe: "tests/test_s08_lifecycle.py::test_q49_disconnect_remount_identity_readonly_and_replacement"
        input: "Initialize logical cartridge UUID 11111111-2222-4333-8444-555555555555 on a 64 MiB APFS sparse image containing generation 1 and root blake3:7a20484b11d4ad86e833208b1503da6105c47d97b12de2c8a906d123ee2339a4; read its tensor through one access token, quiesce, unmount, detach, and reattach the same image at another mount path."
        expected: "The marker survives durable readback; Identity contains the logical UUID, actual filesystem UUID, generation 1, and the exact root; unmount invalidates the old token; remount verifies the complete generation before granting a new operation path."
        observed: "The first mount entered MOUNTED_UNVERIFIED then MOUNTED_VERIFIED and returned the exact four-part identity. The token read b'S08 removable cartridge bytes', became CARTRIDGE_DISCONNECTED after unmount, and never resolved again. Reattachment at the second path returned the same identity and bytes."
      - clause: "Q49 disconnect/reconnect, sleep/wake, bus reset, and port migration"
        test_or_probe: "the active-access event phases of tests/test_s08_lifecycle.py::test_q49_disconnect_remount_identity_readonly_and_replacement"
        input: "Issue port_migration and bus_reset during active reads, sleep during an active read, and disconnect during an active write authority; detach and reattach the sparse image between each event and recovery."
        expected: "Each event invalidates its access before another filesystem call; bus and port changes enter REVALIDATING, sleep enters SLEEPING then wake enters REVALIDATING, disconnect enters DISCONNECTED, and no operation resumes before exact remount verification."
        observed: "Every old access returned CARTRIDGE_DISCONNECTED. Each remount rehashed generation dependencies and returned MOUNTED_VERIFIED with the same logical UUID, filesystem UUID, generation, root, and tensor bytes."
      - clause: "Q49 logical UUID mismatch, physical UUID mismatch, and verified cloned replacement"
        test_or_probe: "the identity-mismatch and replacement phases of tests/test_s08_lifecycle.py::test_q49_disconnect_remount_identity_readonly_and_replacement"
        input: "Replace the canonical marker temporarily with logical UUID aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee. Separately copy the complete cartridge to a second 64 MiB APFS image whose diskutil VolumeUUID differs, then mount it first as an ordinary reconnect and again as an explicit replacement."
        expected: "A different logical UUID always fails. A different filesystem UUID fails ordinary reconnect. Explicit replacement succeeds only when the logical UUID and exact generation/root snapshot survive complete dependency verification."
        observed: "The alternate logical marker and ordinary clone mount each returned CARTRIDGE_IDENTITY_MISMATCH and state FAILED. After exact marker restoration, the source remounted. The explicit clone replacement retained logical UUID 11111111-2222-4333-8444-555555555555 and the generation-1 root while adopting only the new filesystem UUID."
      - clause: "Q49 root and touched-page verification before activation"
        test_or_probe: "the corrupt-root and corrupt-segment phases of tests/test_s08_lifecycle.py::test_q49_disconnect_remount_identity_readonly_and_replacement"
        input: "Replace the canonical root with b'corrupt root', then restore it; independently flip byte zero in page and segment blake3:8cc7d590b9e7d1d34a7d4285a71e276d3edd7424db1ddd4cb586d58a7801dcc6 before remount."
        expected: "Canonical-root corruption returns ROOT_INVALID; a valid root over corrupt payload returns PAGE_CORRUPT; both leave the lifecycle FAILED with no operation path, and exact restoration permits complete revalidation."
        observed: "Both corruptions failed before MOUNTED_VERIFIED. Restoring the exact root and segment bytes allowed remount and recovered the original root and tensor bytes."
      - clause: "Q49 read-only remount"
        test_or_probe: "the hdiutil -readonly phase of tests/test_s08_lifecycle.py::test_q49_disconnect_remount_identity_readonly_and_replacement"
        input: "Detach the verified replacement image and reattach it with hdiutil -readonly; request one write operation and one read operation."
        expected: "The lifecycle derives the mount flag from statvfs, enters READ_ONLY after full identity/root verification, rejects write authority before returning a path, and permits verified reads."
        observed: "The state was READ_ONLY; the write request returned CARTRIDGE_READ_ONLY and created no sentinel; the read request returned the exact tensor bytes and remained READ_ONLY after finish."
      - clause: "S08 fixture states the lifecycle contract independently"
        test_or_probe: "three disposable committed-checkout mutation runs against tests/test_s08_lifecycle.py"
        input: "Replace recover_generation with pin_generation, force read_only=False, and replace access invalidation with pass."
        expected: "The fixture must fail respectively on corrupt-page remount admission, actual read-only state, and retained stale operation access."
        observed: "All three mutants failed at the intended independent boundary, and their disposable clones were removed."
      - clause: "S08 full regression and accounting gate"
        test_or_probe: "the complete pinned Python 3.13 suite and tools/ledger.py from step commit 44e044c"
        input: "Run all fixtures on arm64 macOS 26.5.2 under CPython 3.13.14 with bytecode and pytest caches disabled, then recompute J, commit law, generated integrity, imports, citations, pins, and runtime confinement."
        expected: "Every test passes, the ledger reports no violation, no new dependency or process appears, BUILD_STORY.md remains outside the S08 commit, and no S06/S08 disk image remains mounted."
        observed: "All 21 tests passed in 38.36 seconds. The ledger reported zero violations, 1,702 product LOC, 1,121 test LOC, 356 tool LOC, 58 generated LOC, one process, one Python runtime, and the same three exact pins. No S06 or S08 image remained mounted."

  - id: S09
    title: Source adapter boundary and fixture server
    env: any
    files: [sources.py, tests/fixture_server.py, tests/test_s09_sources.py]
    discovered_scope: "tests/test_s09_sources.py executes the Q9/Q52 invariants; the original row named its reusable fixture server but no collectible test module."
    invariants: [Q52 acceptance (fixture-server substitution, five operations), Q9 acceptance (secret-free descriptor)]
    acceptance_boundary: "S09 proves that one kind-blind caller uses the same five-operation adapter contract over Hugging Face, Ollama, and Tinker fixture wires, with no adapter-owned lifecycle state. It does not claim contact with live source services: L02 must prove the actual request, authentication, manifest, and range wires without a fixture-only route. Q52's final production acquisition-state-machine reuse remains open until S16; S16 owns that Q5 machine after S10 supplies verified transfer."
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S03]
    status: DONE 2026-08-08 — remediation commit eff4c63; committed-step suite 23 passed in 53.03 seconds; ledger clean with 1,992 product LOC, 1,484 test LOC, 356 tool LOC, one process, one runtime, and the three existing exact dependency pins
    prior_status: DONE 2026-08-08 — step commit 884db76; committed-step suite 23 passed in 41.30 seconds; ledger clean with 1,943 product LOC, 1,396 test LOC, 356 tool LOC, one process, one runtime, and the three existing exact dependency pins
    reopen:
      failed_invariant: "Q9 requires authentication translation to retain source authority and keep credential material outside foreign endpoints; Q52 requires the fixture to disprove stable-revision artifact replacement."
      reproduced: "A same-origin range redirected to another local HTTP origin and delivered both Authorization and X-Cassette-License-Acceptance there. A publicly constructed ResolvedSource delivered the same credential to a foreign range_uri. Removing enumerate's artifact-equality comparison still left the original S09 fixture green."
    closeout:
      - clause: "Q52 five-operation adapter boundary and deterministic source substitution"
        test_or_probe: "tests/test_s09_sources.py::test_q52_five_operations_run_unchanged_against_each_source_fixture plus the matching direct adapter probe"
        input: "Present Hugging Face, Ollama, and Tinker manifests with different revision, identity, artifact, metadata-asset, auth, and license field paths. Drive each through one kind-blind caller in the fixed order resolve, enumerate, read_metadata, open_range, license_and_auth."
        expected: "SourceAdapter exposes exactly those five public operations, returns one normalized immutable shape, retains no mutable lifecycle state, and requires no source-specific caller branch."
        observed: "All three fixtures used the same caller and exact operation order. The frozen adapter fields were byte-for-byte equal before and after the sequence. The public callable set contained exactly five names; no sixth source operation existed."
      - clause: "Q9 immutable revision, artifacts, metadata assets, auth scope, and license normalization"
        test_or_probe: "the literal independent oracles in tests/test_s09_sources.py and the direct three-source probe"
        input: "Resolve aliases main, latest, and checkpoint-7 to three distinct immutable revisions and source wire shapes; enumerate one model artifact and one metadata asset per revision; read four validator-bound bytes directly in the probe."
        expected: "Each result retains the exact immutable revision, identity, canonical path, byte count, SHA-256, range URI, metadata identity, auth scope, and license digest supplied by its source evidence."
        observed: "Hugging Face resolved git-sha1:1111111111111111111111111111111111111111 and model.safetensors at 27 bytes with SHA-256 41bfd772f5bd199da3675c36f472a7cebc5b6573e2885f3b1ad9acbbbe8c3a61. Ollama resolved sha256:2222222222222222222222222222222222222222222222222222222222222222 and model.gguf at 22 bytes with SHA-256 44e38c3ab3e8255b93b4b0ab8aa37311aa60e966de26abfcf98db18c20835d24. Tinker resolved sha256:3333333333333333333333333333333333333333333333333333333333333333 and weights.safetensors at 22 bytes with SHA-256 6d0504e46fefef5b2f5db2f1b135b367b1e310e6c23c30acf83615dd0c3ce35a. Direct ranges returned hex 68756767, 6f6c6c61, and 74696e6b respectively."
      - clause: "Q9 secret-free descriptor, credential expiry, and cartridge movement"
        test_or_probe: "tests/test_s09_sources.py::test_q9_descriptor_and_records_remain_secret_free_after_expiry_and_move"
        input: "Supply the fixture bearer secret only through three keychain-style opaque references, serialize the descriptor plus normalized result and requirements to cartridge-a, rename that directory to cartridge-b, clear the credential provider, and attempt every resolution again. Also inject a token field, a credential_ref equal to credential material, a failing credential provider, a wrong expected identity, and a foreign range origin."
        expected: "No secret enters a descriptor, result, requirement, request record, error, or moved cartridge file. Expired references return AUTH_REQUIRED before network I/O; direct credential material and malformed descriptors return INVALID_REQUEST; wrong identity returns IDENTITY_MISMATCH; a foreign credential-bearing range authority is refused."
        observed: "All three moved cartridge files remained secret-free and retained only their opaque references. Clearing the provider returned AUTH_REQUIRED for all three kinds without another server request. Every injected credential, identity, and range-origin failure returned the expected canonical error without exposing the secret."
      - clause: "Q52 immutable enumeration, range validator, and source-code confinement"
        test_or_probe: "the manifest-drift, stale-validator, request-log, and AST phases of tests/test_s09_sources.py"
        input: "Change the Hugging Face enumeration revision after resolve; send a stale If-Match validator for its first byte; inspect every sanitized server request and every product branch outside sources.py."
        expected: "Enumeration or range evidence that leaves the resolved revision returns SOURCE_REVISION_CHANGED with the exact locator or artifact path. Authorization and license-reference translation reaches every operation without entering logs, and source-kind conditionals remain inside the adapter boundary."
        observed: "The changed manifest returned SOURCE_REVISION_CHANGED for fixture/huggingface-model. The HTTP 412 returned SOURCE_REVISION_CHANGED for model.safetensors. All fifteen passing operation requests carried authentication and license acceptance while their retained records contained booleans only; the AST check found no Hugging Face, Ollama, or Tinker branch outside sources.py."
      - clause: "Q52 production acquisition-state-machine ownership remains executable rather than implied"
        test_or_probe: "the S09 acceptance_boundary and S16 queue row in IMPLEMENTATION.md"
        input: "Reconcile Q52's production acquisition-state-machine clause with a step whose adapter is forbidden to own lifecycle state and with S10/S16 still TODO."
        expected: "S09 closes only the stateless adapter and fixture boundary. S16 names the unchanged cross-source production state-machine proof and depends on S10, which supplies verified transfer."
        observed: "S09 now states that boundary explicitly. S16 carries Q52 production reuse in its invariants and depends on S10; no lifecycle state or transfer journal was added to sources.py."
      - clause: "S09 full regression and accounting gate"
        test_or_probe: "the complete pinned Python 3.13 suite and tools/ledger.py from step commit 884db76"
        input: "Run every fixture on arm64 macOS 26.5.2 under CPython 3.13.14 with bytecode and pytest caches disabled, then recompute J, commit law, generated integrity, tracked artifacts, imports, citations, pins, and runtime confinement."
        expected: "Every test passes, the ledger reports no violation, the S06/S08 APFS fixtures leave no image mounted, and S09 adds no dependency, process, language runtime, numerical kernel, or duplicate authority."
        observed: "All 23 tests passed in 41.30 seconds. The ledger reported zero violations, 1,943 product LOC, 1,396 test LOC, 356 tool LOC, 58 generated LOC, one product process, one Python runtime, and the same three exact pins. No S06 or S08 image remained mounted."
      - clause: "Q9 credential authority at construction, use, redirect, and transport boundaries"
        test_or_probe: "the redirect, forged-record, control-redirect, and cleartext phases of tests/test_s09_sources.py::test_q9_descriptor_and_records_remain_secret_free_after_expiry_and_move plus an independent two-server probe"
        input: "Resolve a same-origin range that redirects to a second HTTP origin; construct a foreign-range Artifact and ResolvedSource directly; redirect a control request across origins; configure a non-loopback cleartext endpoint."
        expected: "A range redirect may deliver bytes only after Authorization and X-Cassette-License-Acceptance are removed. A forged range fails before credential lookup or network I/O. A control redirect may not leave its source origin. A remote credential-bearing endpoint requires HTTPS; loopback fixture HTTP remains permitted."
        observed: "The independent range probe returned b'x' while its destination recorded both sensitive headers as None. The forged record returned SOURCE_UNAVAILABLE with no destination request. The fixture refused the cross-origin control redirect and non-loopback HTTP endpoint with canonical errors."
      - clause: "Q52 stable-revision artifact replacement and fixture independence"
        test_or_probe: "the artifact_size_override phase of tests/test_s09_sources.py::test_q52_five_operations_run_unchanged_against_each_source_fixture and three in-memory mutation runs"
        input: "Keep the immutable revision unchanged while changing the enumerated artifact size. Separately remove artifact equality, cross-origin header scrubbing, and use-time range-authority validation."
        expected: "The real implementation returns SOURCE_REVISION_CHANGED for artifact-only drift. Each removed guard must fail the fixture at its own boundary."
        observed: "Artifact-only drift returned SOURCE_REVISION_CHANGED for fixture/huggingface-model. The artifact-comparison and use-time-authority mutants each failed with DID NOT RAISE CassetteError; the redirect-scrub mutant failed the exact no-sensitive-header assertion."
      - clause: "S09 fixture evidence does not impersonate live source compatibility"
        test_or_probe: "the S09 acceptance_boundary and L02 queue row in IMPLEMENTATION.md"
        input: "Compare the deterministic fixture request route with the live Hugging Face, Ollama, and Tinker acquisition claim."
        expected: "S09 may close its deterministic adapter boundary but may not claim live source contact; L02 must reject a fixture-only route and prove actual request, authentication, manifest, and range behavior."
        observed: "The S09 boundary now states that exclusion directly, and L02 names the actual three-source wires plus the no-fixture-only requirement."
      - clause: "S09 remediation regression and accounting gate"
        test_or_probe: "the complete pinned Python 3.13 suite and tools/ledger.py from remediation commit eff4c63"
        input: "Run all fixtures on arm64 macOS under CPython 3.13 with bytecode and pytest caches disabled, then recompute commit law, generated integrity, tracked artifacts, imports, citations, pins, and runtime confinement."
        expected: "Every fixture passes and the repair adds no dependency, process, runtime, numerical kernel, model-specific branch, or duplicate authority."
        observed: "All 23 tests passed in 53.03 seconds. The ledger reported zero violations, 1,992 product LOC, 1,484 test LOC, 356 tool LOC, 58 generated LOC, one process, one Python runtime, and the same three exact dependency pins."

  - id: S10
    title: Resumable verified transfer
    env: any
    files: [sources.py]
    discovered_scope: "tests/test_s10_transfer.py and tests/fixture_server.py execute Q51; store.py retains the sole digest authority; pyproject.toml pins the admitted continuation-state primitive; AGENTS.md records sources.py as the transfer-extent writer. errors.py and the existing S02 fixture correct an observed Q6 failure where frozen exception fields replaced an uncaught CassetteError at a generator-context boundary. sources.py remains one Q78 source boundary above 800 physical lines because splitting transfer from source authority would create another L2 authority and more plumbing."
    dependency_admission: "resumablesha256==1.0; subset: SHA-256 __getstate__/__setstate__ only; serves Q51 serialized_hash_state and one-readback transfer; Unlicense, 53,584-byte abi3 extension, no runtime dependencies or install hooks. The stdlib hashlib object cannot export continuation state, and prefix reconstruction reread completed cartridge bytes, so the dependency replaces authored cryptography and closes the measured Q51 gap."
    invariants: [Q51 acceptance (random interruption, corrupt chunks, validator change, no post-completion reread) against the fixture server]
    acceptance_boundary: "A completed Q51 PartialState proves the transfer that produced it and permits transfer_artifact to return without a post-completion whole-object reread. It is not present-byte authority after return. A later consumer must verify the source extent against its immutable Q1/Q9 whole-object digest while consuming those bytes; S19 owns that read-time verification, S24 executes the first S10-to-S19 integration, and Q62 begins only after canonical pages and a root exist."
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S09, S07]
    status: DONE 2026-08-08 — step commit 51744c9; Q6 context-boundary repair 32293f2; committed suite 24 passed in 41.56 seconds; ledger clean with 2,303 product LOC, 1,768 test LOC, 356 tool LOC, one process, one runtime, and four exact dependency pins
    closeout:
      - clause: "Q51 fixed chunks, bounded parallel ranges, and store-granted cartridge extents"
        test_or_probe: "tests/test_s10_transfer.py::test_q51_random_interruption_corruption_validator_resume_without_final_reread"
        input: "Resolve two immutable Hugging Face fixture shards of 8,388,925 and 12,583,823 bytes. Grant separate pre-opened, pre-sized data and checkpoint extents under one active Q53 reservation, then schedule 4 MiB ranges with a fixture delay that makes overlap observable."
        expected: "Every non-tail range is exactly 4 MiB, at most two ranges are active, writes remain inside the granted extents, and transfer cannot begin without capacity for all data and checkpoint bytes."
        observed: "The two shards used three and four fixed chunks respectively; the server observed exactly two concurrent ranges. The active reservation covered 21,235,123 transfer bytes plus Q53 safety, and releasing it made the next call fail with CAPACITY_EXCEEDED before network or checkpoint mutation."
      - clause: "Q51 random interruption, durable PartialState, and true hash continuation"
        test_or_probe: "the interrupted-tail, resumed-offset, and serialized-state phases of the S10 fixture"
        input: "Close a range response at a seeded random byte within the first shard's tail after two complete chunks. Invoke transfer again with the same immutable revision, extents, and validator."
        expected: "The interruption is retryable, the two completed chunks remain durable, resume restores SHA-256 at offset 8,388,608, and only the missing tail is requested again."
        observed: "The first call returned SOURCE_UNAVAILABLE and retained exactly the first 8,388,608 bytes. Resume restored sha256-state-v1 at that offset, verified both local chunks, requested only the missing tail, and produced the exact source SHA-256. A forged state counter was rejected before restoration."
      - clause: "Q51 network, local, and checkpoint corruption rejection"
        test_or_probe: "the source-corruption, local-corruption, checkpoint-readback, and chunk-record phases of the S10 fixture"
        input: "Corrupt a network tail without authoritative chunk hashes; corrupt a network first chunk with authoritative BLAKE3 hashes; alter one completed local byte; alter one durable chunk record; and return changed bytes during checkpoint-header and chunk-record readback."
        expected: "Whole-object SHA-256 catches unmanifested source corruption; authoritative BLAKE3 catches manifested corruption before write; local and checkpoint mismatches stop before further network use; every checkpoint write is read back before durable synchronization."
        observed: "Every injected path terminated with the exact typed failure. The authoritative network mismatch left its data chunk zeroed, local and record corruption caused no source request, and changed checkpoint readbacks returned DURABILITY_UNSUPPORTED."
      - clause: "Q51 source identity and validator remain immutable across every parallel result"
        test_or_probe: "the revision, size, digest, validator, chunk-manifest, live-412, and mixed-concurrent phases of the S10 fixture"
        input: "Resume retained progress after changing each checkpoint identity member separately. Then combine one truncated range with a simultaneous validator failure in the other in-flight range."
        expected: "Every identity change discards retained progress. Any SOURCE_REVISION_CHANGED result outranks another concurrent retryable failure, and the next valid attempt starts from byte zero."
        observed: "Revision, size, expected digest, validator, and authoritative chunk-manifest drift each returned SOURCE_REVISION_CHANGED. HTTP 412 did the same. The mixed batch also returned SOURCE_REVISION_CHANGED, and the following request set covered all four ranges from offset zero."
      - clause: "Q51 final proof requires no post-completion whole-artifact reread"
        test_or_probe: "the tracked-pread completion replay in the S10 fixture"
        input: "Complete the first shard, retain its interval set, chunk digests, whole SHA-256 continuation, and checkpoint aggregate, then call transfer again while recording every read against its data extent."
        expected: "All intervals and local chunk identities remain accounted for, the whole digest equals the immutable source digest, and replay returns the same PartialState without reading model data."
        observed: "The completed interval was exactly [0,8,388,925), all three BLAKE3 chunk digests matched independent oracles, the restored SHA-256 matched hashlib, and replay made zero data-extent reads."
      - clause: "Q9 secrets and Q53 reservation authority do not enter transfer state"
        test_or_probe: "the cartridge scan and terminal reservation phase of the S10 fixture"
        input: "Resolve through an opaque credential reference whose provider returns a sentinel bearer secret, complete both shards, scan every cartridge file, release the reservation, and retry."
        expected: "No credential material is serialized. A released reservation stops transfer before network or mutation."
        observed: "No cartridge byte contained the sentinel secret. The released reservation produced CAPACITY_EXCEEDED with an unchanged checkpoint and no additional server request."
      - clause: "The S10 fixture is capable of disproving its critical guards"
        test_or_probe: "eleven one-at-a-time mutations in a detached worktree at 51744c9"
        input: "Remove final whole-digest comparison, local-resume verification, checkpoint-record aggregation, checkpoint identity binding, completed-state early return, authoritative network-chunk verification, the two-range bound, serialized SHA restoration, concurrent revision-failure priority, checkpoint write readback, and active-reservation admission."
        expected: "Each mutant fails the Q51 fixture at the behavior governed by the removed guard."
        observed: "All eleven mutants failed. None reached a green S10 fixture; the failures occurred at their intended corruption, resume, concurrency, reread, durability, or admission assertions."
      - clause: "Q6 typed transfer errors survive ordinary generator-context boundaries"
        test_or_probe: "tests/test_s02_errors.py::test_error_shape_is_q6_exactly_and_round_trips and the direct contextlib reproduction"
        input: "Raise one CassetteError through a generator-based context manager."
        expected: "The caller receives the original five-field CassetteError rather than a replacement exception created while Python attaches traceback metadata."
        observed: "The pre-repair class returned FrozenInstanceError. Commit 32293f2 removed only the incompatible frozen constraint; the same probe and fixture now receive the original CassetteError object."
      - clause: "S10 complete regression and accounting gate"
        test_or_probe: "the complete pinned Python 3.13 suite and tools/ledger.py from remediation commit 32293f2"
        input: "Run every fixture on arm64 macOS 26.5.2 under CPython 3.13.14 with bytecode and pytest caches disabled, then recompute commit law, generated integrity, tracked artifacts, imports, citations, pins, and runtime confinement."
        expected: "Every test passes; no S06/S08 image remains mounted; the ledger reports no violation, new process, runtime, model branch, numerical kernel, or duplicate authority."
        observed: "All 24 tests passed in 41.56 seconds. The ledger reported zero violations, 2,303 product LOC, 1,768 test LOC, 356 tool LOC, 58 generated LOC, one process, one Python runtime, and four exact dependency pins. No S06 or S08 image remained mounted."

  - id: S11
    title: Preflight and compatibility decision
    env: any
    files: [sources.py]
    discovered_scope: "tests/test_s11_preflight.py executes Q8/Q50/Q56. store.py exposes the existing Q53 calculation as one pure capacity_requirement so preflight and physical reservation cannot become separate byte authorities. sources.py remains the sole Q78 source, metadata, preflight, and transfer authority despite exceeding 800 physical lines; splitting the decision from its immutable source evidence would create another L2 authority and more plumbing."
    invariants: [Q8/Q50 acceptance (trust states, contradictory fixtures), Q56 acceptance (four outcomes, no silent weakening)]
    acceptance_boundary: "S11 proves the four preflight decisions from deterministic source-fixture evidence whose immutable bytes Cassette verifies itself. It does not prove the live Hugging Face, Ollama, or Tinker request, authentication, gating, license, manifest, or range wires; L02 owns those live-source checks and must show that no fixture-only route survives."
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S09]
    status: DONE 2026-08-08 — initial implementation e399d60; trust-provenance repair 97a43e7; clean suite 25 passed in 57.94 seconds with no skips; ledger clean with 2,723 product LOC, 1,955 test LOC, 356 tool LOC, one process, one Python runtime, and four exact dependency pins
    reopened_by: "Q8/Q50/Q56 trust-provenance failure reproduced at bf881af: SourceAdapter accepted remote trust and authority labels, normalize_remote_metadata converted those labels directly into decision priority, and only Q9 material fields were replaced by Cassette-derived evidence. A forged architecture, one active byte, zero context state, supported operators, and custom_code false therefore produced SUPPORTED with attacker:self authority."
    closeout:
      - clause: "Q50 independent trust states, immutable authority, and retained contradictions"
        test_or_probe: "tests/test_s11_preflight.py::test_q8_q50_q56_trust_conflicts_four_outcomes_and_no_silent_weakening"
        input: "Submit one complete generated Q50 record whose card, config, source manifest, and parsed header evidence disagree about identity, bytes, artifact digests, and architecture. Add an equal-strength parsed-versus-digested architecture conflict."
        expected: "Cassette-derived immutable Q9 artifact facts win for identity and exact artifact material; parsed config beats a declaration; every distinct contradiction remains recorded; unresolved peer immutable evidence becomes ABSENT rather than an invented winner."
        observed: "The normalized record conformed to the generated schema. It retained all five deliberate conflicts, selected the exact resolved identity, model byte count, artifact count and digest, selected parsed architecture over its card declaration, and returned the tied architecture as ABSENT with its conflict intact."
      - clause: "Q8 complete, incomplete, deceptive, mutable, gated, and custom-code records never acquire invented facts"
        test_or_probe: "the complete, incomplete, active-parameter deception, mutable revision, gating, custom-code, weak-operator, and weak-context phases of the S11 fixture"
        input: "Remove architecture and operators; present declared-only operators or context; make active parameters exceed total parameters; replace the immutable revision with main; remove required credential and license references; and set parsed custom_code true before and after filling unrelated missing metadata."
        expected: "Unknowns remain None with exact bounded checks, malformed or mutable evidence is UNSUPPORTED, gating remains explicit, and neither false nor SUPPORTED is invented for absent or declaration-only technical facts."
        observed: "Bounded unknowns returned METADATA_INSUFFICIENT and exact validator-bound ranges; the same unknowns without a deciding range returned UNSUPPORTED. Deceptive, mutable, ungated-authority, and custom-code inputs each retained their decisive cause, and filling operators did not weaken custom-code refusal."
      - clause: "Q56 emits exactly four causal outcomes and cannot silently weaken a decisive refusal"
        test_or_probe: "the native, preparation, bounded-range, unsupported-operator, unsupported-modality, and custom-code phases of the S11 fixture"
        input: "Evaluate strong native evidence, a transformable model above native memory, bounded missing metadata, a foreign operator, an unrepresented vision modality, and custom code with then without unrelated unknowns."
        expected: "The only classes are SUPPORTED, SUPPORTED_AFTER_PREPARATION, METADATA_INSUFFICIENT, and UNSUPPORTED. Preparation names Q17/Q18/Q19; a decisive unsupported cause survives added metadata."
        observed: "All four classes occurred. Native support named one NATIVE mode; preparation named COMPILED and exact Q17/Q18/Q19 validation; bounded unknowns named their source range; foreign operator, vision modality, and custom code remained UNSUPPORTED with exact causes."
      - clause: "Q53 preflight capacity includes every source payload, every Q51 checkpoint extent, and safety"
        test_or_probe: "the independent exact-capacity calculation and one-byte-short phase of the S11 fixture"
        input: "Preflight a 1 GiB plus 73 byte model artifact and a 101 byte metadata artifact. Independently calculate both 128 KiB plus 33-byte-per-4-MiB transfer-state extents and the 8 GiB Q53 safety reserve."
        expected: "Equality admits; one byte less returns UNSUPPORTED with CAPACITY_EXCEEDED. Preflight reuses the same Q53 calculation later used by physical reservation."
        observed: "Required capacity was exactly both payloads plus 270,658 checkpoint bytes plus 8 GiB. Equality returned SUPPORTED; one byte less returned UNSUPPORTED. reserve_capacity now consumes the same CapacityRequirement fields rather than maintaining duplicate arithmetic."
      - clause: "Native memory accounts for runtime context and representation support"
        test_or_probe: "the dense, sparse-active-byte, missing-active-bound, weak-context, and unsupported-modality phases of the S11 fixture"
        input: "Supply a parsed 131,072-token context with a 128 MiB state bound; supply a sparse model with and without an exact active-byte bound; weaken context to DECLARED; and request vision against a text-only profile."
        expected: "Native peak is weights plus context state. Sparse support requires a strong active-byte bound when the full representation does not fit. Declared context requires inspection, and an unsupported modality is refused even when its processor exists."
        observed: "Dense peak included the 128 MiB state; sparse peak was exactly 728 MiB from 600 MiB active weights plus state; missing active bytes returned METADATA_INSUFFICIENT; declared context did the same; vision returned UNSUPPORTED_MODALITY:vision."
      - clause: "The S11 fixture can disprove its consequential guards"
        test_or_probe: "ten one-at-a-time mutations in disposable copies of step commit e399d60"
        input: "Weaken resolved-manifest authority; remove custom-code refusal; allow declared operators; omit metadata payload capacity; choose one equal-trust conflict; drop Q18/Q19 preparation proof; omit transfer checkpoint capacity; omit context memory; allow declared context and modality evidence; and ignore unsupported modalities."
        expected: "Each mutation makes the S11 fixture fail at the behavior owned by the changed guard."
        observed: "All ten mutations were caught independently. Every run failed the single Q8/Q50/Q56 fixture; none produced a false green. The disposable mutation tree was removed afterward."
      - clause: "S11 complete regression, accounting, and environment gate"
        test_or_probe: "the pinned CPython 3.13 complete suite, tools/ledger.py, git diff checking, and hdiutil inspection after step commit e399d60"
        input: "Run all fixtures on arm64 macOS with bytecode and pytest caches disabled; recompute commit law, generated integrity, tracked artifacts, imports, citations, pins, and runtime confinement; inspect mounted images."
        expected: "All fixtures pass without a platform skip, the ledger reports no violation or new dependency/process/runtime/kernel/authority, the patch is clean, and no Cassette image remains mounted."
        observed: "A first final run exposed a transient busy-volume detach in S06 and therefore did not close the gate. After detaching only that orphaned test image, S06 passed alone in 35.30 seconds and the clean complete run passed all 25 tests in 52.89 seconds. The ledger reported zero violations, 2,677 product LOC, 1,910 test LOC, 356 tool LOC, 58 generated LOC, one process, one Python runtime, and the same four pins. No Cassette test image remained mounted."
    correction_closeout:
      - clause: "Q8/Q50/Q56 trust derives from verified evidence rather than source labels"
        test_or_probe: "direct hostile reproduction at bf881af followed by the repaired S09 and S11 fixtures at 97a43e7"
        input: "Let a hostile source label invented architecture, active-byte, context-state, operator, and custom-code claims EVIDENCE_DIGESTED or PARSED with attacker-controlled authority."
        expected: "Remote labels remain declarations and cannot produce SUPPORTED. Cassette grants strong trust only after it verifies the complete immutable metadata asset against the resolved artifact digest."
        observed: "Before repair, the forged record returned SUPPORTED with attacker:self authority. After repair, adapter claims are DECLARED; the same evidence is UNSUPPORTED until digest-matched immutable asset bytes are supplied, and same-length corrupt bytes return IDENTITY_MISMATCH."
      - clause: "Strong metadata remains bound to resolved immutable cartridge bytes"
        test_or_probe: "tests/test_s11_preflight.py verified-asset, corrupt-asset, contradiction, and four-outcome phases"
        input: "Supply complete metadata bytes whose path, size, digest, JSON shape, and generated Q50 fields either agree with or contradict the resolved revision."
        expected: "Only exact resolved bytes receive EVIDENCE_DIGESTED authority; malformed, foreign, duplicate, incomplete, or digest-mismatched material cannot become decision evidence."
        observed: "The verified asset received Cassette-owned digest authority and drove the declared decision. Corrupt bytes were refused before normalization, while equal strong contradictions remained ABSENT and produced UNSUPPORTED."
      - clause: "The repaired fixture can disprove every consequential trust guard"
        test_or_probe: "six one-at-a-time mutations in a disposable copy of repair commit 97a43e7"
        input: "Restore source labels, bypass sanitation, preserve self-asserted strong trust, skip immutable-asset digest comparison, admit DECLARED technical claims, or reduce verified evidence to declaration priority."
        expected: "Each mutation makes the repaired fixture fail."
        observed: "All six mutations failed independently. The disposable tree was deleted after the runs."
      - clause: "S11 trust repair complete gate"
        test_or_probe: "the complete pinned Python suite, tools/ledger.py, git diff checking, and mounted-image inspection after 97a43e7"
        input: "Run every fixture with bytecode and pytest caches disabled, recompute the ledger, inspect the patch, and confirm no Cassette test image remains mounted."
        expected: "All fixtures pass; the ledger and patch are clean; no new dependency, process, runtime, numerical kernel, model branch, or authority appears; no test image remains mounted."
        observed: "All 25 tests passed in 57.94 seconds with no skips. The ledger reported zero violations, 2,723 product LOC, 1,955 test LOC, 356 tool LOC, 58 generated LOC, one process, one Python runtime, and the same four exact pins. The patch was clean and no Cassette S06 or S08 image remained mounted."

  - id: S12
    title: Mathematical-plan schemas, runtime dispatch, and golden operators
    env: macos
    files: [pager.py, tools/genschema.py, schema/ (generated dispatch and Q19 certificate tables)]
    discovered_scope: "tests/test_s12_pager.py executes the F2/Q30/Q33/Q40 boundary and owns an early platform gate so future env:any full-suite runs skip before importing MLX; tests/test_s03_schema.py admits the new generated contracts without weakening S03; pyproject.toml and uv.lock pin the MLX release executed by the generated dispatch table. The pre-S12 mathematical-authority amendment is a required input and remains distinct from the S12 implementation changes. tools/genschema.py remains the sole generated-contract authority above 800 physical lines; splitting it would create schema plumbing and a second authority."
    dependency_admission: "mlx==0.31.0 at release commit 365d6f29b47686a9f5401f6a9ec5825fee162d69; subset: core/fast matmul, quantized matmul, RMS norm, traditional RoPE at offsets zero and one, scaled dot-product and causal attention, convolution, embedding, add, SiLU, explicit-key categorical sampling, autograd, and SGD; serves Q30. Its Darwin wheel supplies the existing Metal kernels that replace every Cassette numerical kernel."
    invariants: [Q30 acceptance (golden tensors per dispatched dtype/shape/operator against reference), Q33/Q40 acceptance (generated bounded schema represents every MATHS.md certificate dimension without executable or model-specific payload), F2 valid/malformed certificate and golden-operator fixtures; mlx confinement check in ledger]
    acceptance_boundary: "S12 proves bounded generated schemas, exact membership in the generated Q30 dispatch, and faithful execution of the sixteen declared golden MLX operator/dtype/shape rows. Ten rows closed S12; S15 added six generated rows for the complete F3 decoder without adding an authored kernel. S12 does not prove that an independently supplied certificate is mathematically true or internally reconciled with source evidence. S13 owns independent recomputation from canonical source evidence and rejection of contradictory certificate claims."
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S03, S01]
    historical_status: "DONE 2026-08-09 — original step 73997e0; platform-gate repair 26a0913; complete macOS suite 28 passed in 46.17 seconds with no skips; synthetic Linux gate skipped before MLX or pager import; ledger clean with 2,813 product LOC, 2,136 test LOC, 406 tool LOC, 74 generated LOC, one process, one Python runtime, and five exact dependency pins"
    status: DONE 2026-09-01 — Q30 indirect-runtime confinement repair 0c3e72a48d0478a036cc1fa037515b8051589394 closes the review-reproduced broker false pass while preserving the prior audit remediation 306055ddefb4e5d5a735c3dc5e4ae6e09b7d57c0; the focused Q30 fixture passed, the complete proof passed 307/307 with zero skips, and the repaired ledger and J report are green
    reopened_by: "S12 test-harness portability failure reproduced after ec551de: with MLX unavailable, test_s12_pager.py reached its module-level MLX import and aborted collection; with MLX installed under a synthetic Linux platform, the golden operator fixture ran and failed at Q30's Apple Silicon Metal guard instead of skipping. Future env:any steps therefore could not satisfy their complete-suite gate outside macOS."
    closeout:
      - clause: "Q33/Q40 bounded data represents every separate MATHS.md certificate dimension and the least-invasive compiled mode"
        test_or_probe: "tests/test_s12_pager.py::test_q33_q40_f2_certificate_dimensions_are_bounded_data_and_fail_before_execution plus Draft 2020-12 metaschema validation"
        input: "Validate two data-only target variants; remove each of target, condition metrics, compatibility, atoms, description, observation, execution, and trace; collapse the resource vector; add code, command, model family, path, URL, or weight payload; exceed the four prior modes; supply infinity; reorder Q40 failures; alter the dispatch; mismatch the target; and name a foreign operator."
        expected: "Each valid certificate and plan conforms to bounded generated schemas and uses the exact fifth Q40 mode only after four ordered Q38 records. Every malformed, collapsed, executable, model-specific, stale, or foreign case terminates before MLX allocation."
        observed: "Both target variants passed the same code path. All three generated contracts passed the official Draft 2020-12 metaschema. Every object, array, string, integer, and number is structurally bounded; each hostile case returned its typed invariant failure, and Metal peak memory did not increase during malformed-plan validation."
      - clause: "Q30 dispatch executes every declared operator, dtype, shape, parameter tuple, and tolerance through the pinned MLX release"
        test_or_probe: "tests/test_s12_pager.py::test_q30_f2_every_generated_operator_dtype_and_shape_matches_an_independent_golden_reference"
        input: "Execute the generated float32 and uint32 rows for matmul, affine four-bit quantized matmul, RMS norm, traditional RoPE, scaled dot-product attention, convolution, embedding, explicit-key categorical sampling, autograd, and SGD; then submit a wrong shape and an absent custom case."
        expected: "Every result matches independent literal or scalar reference arithmetic within its declared tolerance. Wrong signatures and undeclared operators terminate with canonical typed errors. No Cassette numerical kernel or repository-linked native binary exists."
        observed: "All ten rows matched their references on MLX 0.31.0 over Apple Silicon Metal. Wrong shape returned INVALID_REQUEST; the custom case returned UNSUPPORTED_OPERATOR. AST inspection found no authored arithmetic in the ten wrappers, tracked sources contained no native kernel language, and otool found no repository-linked MLX binary."
      - clause: "The S12 fixtures can disprove every consequential schema, dispatch, operator, and confinement guard"
        test_or_probe: "eight one-at-a-time mutations in detached disposable worktrees at step commit 73997e0"
        input: "Make description optional; disable array maxima; accept non-finite numbers; compare only the dispatch digest; admit a foreign certificate operator; add one to MLX matmul output; bypass dtype and shape admission; or permit MLX imports in compiler.py."
        expected: "Each mutation makes the fixture for the removed guard fail."
        observed: "All eight mutants failed independently at the intended assertion. None produced a false green, and all agent-created worktrees were removed afterward."
      - clause: "Q30 runtime ownership remains confined and the complete S12 regression and accounting gate passes"
        test_or_probe: "tests/test_s12_pager.py::test_q30_ledger_confines_mlx_to_pager_and_trainer, the complete pinned CPython 3.13 suite, tools/ledger.py, hdiutil inspection, and git diff checking after 73997e0"
        input: "Inject an MLX import into a hostile compiler authority; run every fixture on arm64 macOS with bytecode and pytest caches disabled; regenerate and hash every schema; recompute imports, citations, pins, commit law, tracked artifacts, runtime confinement, and J; inspect mounted images and the patch."
        expected: "The hostile import fails confinement. Every fixture passes without a platform skip; generated files and the lock are reproducible; the ledger reports no violation, duplicate authority, model branch, extra runtime, process, or authored kernel; no Cassette test image remains mounted."
        observed: "The hostile compiler import was rejected and its guard-removal mutant failed. The complete suite passed all 28 tests in 46.32 seconds with no skips. The ledger reported zero violations, 2,813 product LOC, 2,133 test LOC, 406 tool LOC, 74 generated LOC, one process, one Python runtime, and five exact pins. No Cassette S06 or S08 image was mounted, and the repository retained 97 GiB free."
    correction_closeout:
      - clause: "An env:macos S12 fixture cannot abort or fail a future non-Darwin complete-suite run"
        test_or_probe: "synthetic Linux module-load probe with an import blocker before and after repair 26a0913"
        input: "Override platform.system to Linux and platform.machine to x86_64, then make any import of mlx, mlx.*, or pager raise immediately while loading tests/test_s12_pager.py. Separately run the Q30 golden fixture with MLX installed under the same synthetic platform."
        expected: "Before repair, the module reaches MLX during collection or reaches Q30 execution and fails. After repair, pytest skips the module before either platform-bound import; no S12 test runs or fails outside its declared environment."
        observed: "Before repair, the import blocker reported platform import reached: mlx, and the installed-runtime probe failed with CAPABILITY_MISMATCH at the Apple Silicon Metal guard. After repair, the same blocker remained untouched and the module raised the explicit S12 non-Darwin skip."
      - clause: "The platform guard is consequential and preserves all accepted macOS behavior"
        test_or_probe: "one guard-removal mutant, tests/test_s12_pager.py on real arm64 macOS, the complete pinned suite, tools/ledger.py, hdiutil inspection, and git diff checking after 26a0913"
        input: "Remove only the early skip from a disposable test-file copy and repeat the import-blocker probe; restore the guard and execute all three S12 fixtures plus every repository fixture on Apple Silicon Metal."
        expected: "The mutant reaches the forbidden MLX import. The repaired source skips only outside Darwin arm64, while all original Q30/Q33/Q40 evidence and repository invariants remain green on the declared platform."
        observed: "The mutant was caught at mlx. The repaired S12 file passed all three fixtures in 0.53 seconds; the complete suite passed all 28 tests in 46.17 seconds with no skips. The ledger reported zero violations, 2,813 product LOC, 2,136 test LOC, 406 tool LOC, 74 generated LOC, one process, one Python runtime, and five exact pins. No Cassette image was mounted, and only the pre-existing untracked presentation directory remained."
    audit_remediation_closeout:
      - clause: "Q30 native-link proof examines actual Mach-O dependencies and repository ownership"
        test_or_probe: "tests/test_s12_pager.py::test_q30_f2_every_generated_operator_dtype_and_shape_matches_an_independent_golden_reference at 306055d"
        input: "Inspect the in-repository MLX installation, then rewrite a copied Mach-O consumer to load a Git-tracked libcassette.dylib in a disposable repository."
        expected: "The MLX binary's own heading and location do not count as a dependency. The actual tracked native dependency is detected."
        observed: "MLX produced no repository-owned dependency. The rewritten consumer resolved exactly libcassette.dylib. Neutralizing the ownership helper made the fixture fail at that exact assertion."
      - clause: "MATHS.md section 8 is the sole machine authority for implemented certificate dimensions"
        test_or_probe: "tests/test_s03_schema.py::test_generator_is_deterministic_and_ledger_rejects_coordinated_hand_edits at 306055d"
        input: "Remove, duplicate, corrupt, duplicate a dimension in, add to, remove from, rename in, and reorder the bounded MATHS.md authority block; regenerate only where the contract permits it."
        expected: "Malformed or schema-disagreeing authority fails generation. Reordering makes committed output stale, and regeneration reflects the new order."
        observed: "Every malformed or set-changing mutation failed. Reordering caused generated-integrity failure before regeneration; regenerated tables reflected the MATHS.md order and then passed integrity. Schema regeneration on the accepted source produced zero diff."
      - clause: "The two MATHS.md guards are independently consequential"
        test_or_probe: "two one-at-a-time guard-removal mutations in disposable clones of 306055d"
        input: "First remove schema-to-MATHS dimension reconciliation. Then, separately, emit dimensions from schema order instead of the parsed MATHS.md block."
        expected: "The first mutant admits an added mathematical dimension. The second mutant hides stale generated output after an authority-order change."
        observed: "The first fixture failed because new_dimension regenerated successfully. The second failed because the reordered MATHS.md block produced no generated-integrity violation. Both disposable clones were deleted."
      - clause: "S12 closes only bounded representation and declared golden execution"
        test_or_probe: "IMPLEMENTATION.md queue audit, presentation assertions, browser inspection, focused S12 fixtures, complete suite, and ledger at 306055d"
        input: "Inspect the S12/S13 boundary, all eight contradictory certificate classes, future Q55/Q30 owners, and every corrected field-manual slide; execute all repository fixtures on arm64 macOS."
        expected: "S12 claims no semantic truth it did not recompute. S13 remains TODO and owns all eight contradictions. S19 owns Q55 plus tuple discovery/refusal, S24 owns representative-model execution and re-goldening, and the presentation distinguishes fixture, image, and live-hardware proof."
        observed: "The queue and presentation state those boundaries explicitly. All 28 tests passed in 1,024.50 seconds with S06, S08, and S12 executed; the ledger reported zero violations and no new dependency, process, runtime, language, kernel, or model branch."
    q30_confinement_repair_closeout:
      - clause: "Q30 runtime confinement rejects indirect MLX acquisition outside pager.py and trainer.py"
        test_or_probe: "tests/test_s12_pager.py::test_q30_ledger_confines_mlx_to_pager_and_trainer plus the pre-repair synthetic broker probe and the complete Q29/Q78 proof at source repair 0c3e72a48d0478a036cc1fa037515b8051589394"
        input: "Let broker.py import pager, obtain the runtime through pager._mlx_runtime(), and call mx.synchronize() without importing mlx directly. Retain the original hostile compiler.py direct-import case."
        expected: "The pre-repair ledger admits the indirect broker path, proving the false pass. The repaired ledger rejects both paths as Q30 confinement violations while pager.py and trainer.py retain sole MLX ownership."
        observed: "The original ledger returned no confinement violation for the broker fixture. After repair, the focused Q30 fixture passed; the clean complete proof passed 307 tests with zero skips, twelve controls, twelve deletion failures, and twelve executable-bypass failures. No product module gained an MLX reference, runtime, dependency, process, kernel, or model branch."

  - id: S13
    title: Compatibility-certificate validation, memory budget, and residency schedules
    env: any
    files: [pager.py]
    discovered_scope: "tests/test_s13_pager.py is the single F2 fixture for Q19/Q47/Q63 and keeps the certificate, evidence, plan, and profile as four disjoint mutable object graphs. pager.py remains the sole Q78 pager and scheduler authority above 800 physical lines: the added exact validation arithmetic, certificate admission, memory ledger, and schedule result all control the same pre-execution boundary, while splitting them would add cross-file plumbing or a second admission authority. MLX imports are lazy so this validation boundary remains executable on env:any without widening numerical-runtime ownership."
    invariants: [Q19 acceptance (independently recompute flattening, ranks, witness losses, service faces, minimal nonfaces, atom cover, observation contract, description distortion, execution error/risk, composition maps, and horizon on exact generated matrices), Q47 acceptance (boundary sweeps on simulated profiles), Q63 certified schedule generation subset]
    acceptance_injections: [aggregate/resource-table disagreement, atom-count/catalog disagreement, resource/trace horizon disagreement, aggregate/operation epsilon disagreement, peak resource greater than total resource, plan limits beneath certified demand, compatibility/resource eta disagreement, atom rank above the declared rank budget]
    acceptance_boundary: "S13 receives structurally valid S12 records and independently recomputes their mathematical claims from canonical exact evidence. Minimal nonfaces require an exact robust cycle proof rather than absence from an atom catalog; fresh residual execution requires the recomputed private-coin column law, sufficient sample count, exact scalar traffic, and reconciled physical probes. Every contradiction terminates before CertifiedSchedule exists. S13 emits the certified mathematical and memory schedule only; S14 owns page readiness, execution, and selection failure."
    expected_size: large
    done_when: full suite + ledger green
    depends: [S12]
    status: DONE 2026-08-09 — implementation f4d323f3040e182bab320dd584df2a5c9dc1137c independently recomputes the complete S13 Q19 certificate boundary, admits Q47 memory only at or below the conservative limit, emits the Q63 schedule subset, rejects every declared contradiction before admission, and keeps MLX confined to lazy execution; numeric-boundary repair 095b02ca8b2401091f31caa370497e88f4a98f82 bounds canonical exact scalars before construction and converts unrepresentable derived claims into typed refusal; the final repair suite passed 29/29 in 142.70 seconds with no skips, generated schemas reproduced byte-for-byte, and the ledger remained clean
    closeout:
      - clause: "Q19 exact compatibility claims are recomputed from canonical evidence rather than reconciled against the certificate's own tables"
        test_or_probe: "tests/test_s13_pager.py::test_q19_q47_q63_f2_exact_certificate_recomputation_precedes_bounded_schedule_admission and the pre-change eight-case admission probe"
        input: "Use a three-by-three exact real target with three positive-definite projector-plus-delta condition metrics, three rank-one atoms serving the AB, AC, and BC faces, one unbalanced ABC cycle, one reconstruction residual per atom, a fresh private-column law, one operation composition map, and a three-step trace. Before implementation, submit all eight queue-listed contradictory certificate or plan variants."
        expected: "Recompute flattening, target and metric digests, positive-definite witnesses, ranks, condition losses, service faces, the complete minimal-nonface family, cover, observation support and selector, description distortion, estimator calibration, residual probabilities, execution error and risk, operation composition, resource tables, aggregates, physical conversion, and horizon. The exact valid tuple admits; each contradiction terminates before schedule admission."
        observed: "The valid evidence recomputed rank one for all three atoms, losses 401/100300 on each served condition and 601/300 off its face, the three pair faces, and ABC as the sole proved minimal nonface. A positive-definite Gram lower bound verified the unbalanced cycle without trusting catalog omission. The fresh law recomputed probability one on residual column zero, three samples, nine scalar reads, epsilon 1/2, per-step delta 1/4, and union risk 3/4. Before the change all eight contradictions admitted; afterward all eight returned typed refusal before CertifiedSchedule."
      - clause: "Q47 conservative unified-memory admission passes exact boundaries and rejects the next byte"
        test_or_probe: "the Q47 profile sweep inside tests/test_s13_pager.py::test_q19_q47_q63_f2_exact_certificate_recomputation_precedes_bounded_schedule_admission"
        input: "Place the exact admissible remainder independently in activation, cache, context, runtime-buffer, and training-window bytes; then add one byte. Repeat with competing-memory at its boundary, physical memory 16 GiB plus one byte, and a 10 GiB recommended working-set limit on a 32 GiB profile."
        expected: "Reserve max(4 GiB, ceil(physical/4)); cap at min(physical minus reserve, floor(0.90 times recommended)); subtract execution and observed competing memory; admit equality; reject one byte above it with MEMORY_BUDGET_EXCEEDED."
        observed: "The 16 GiB profile reserved 4 GiB, exposed a 12 GiB ceiling and 10 GiB available after execution and competing memory, and admitted a 10 GiB peak in every resident category. Each one-byte excess failed. The 16 GiB plus one profile reserved 4 GiB plus one, while the recommended-limited profile capped at exactly 9 GiB."
      - clause: "Q63 emits one time-indexed schedule whose residency and transfers equal the certified trace and physical rows"
        test_or_probe: "the accepted schedule assertions and underreported-traffic/probe attacks in tests/test_s13_pager.py"
        input: "Admit three contiguous trace steps over atom.ab, atom.ac, and atom.bc with 1,024 description bytes, 256 metadata bytes, three fresh samples, nine scalar reads, one page read, 4,096 load bytes, and 4,096 dynamic bytes per step. Separately make every internally reconciled trace report eight scalar reads, then make an internally reconciled physical row report two probes."
        expected: "Return immutable ResidencyStep rows in trace order only for the exact certified demands. Recompute p times samples as scalar traffic and require the physical probe unit and count to equal the sampling law and operation peak."
        observed: "The admitted schedule contained exactly steps 0, 1, and 2 with the declared atom order and byte categories. The fully resealed eight-scalar trace and two-probe conversion both terminated with CAPABILITY_MISMATCH before a schedule was returned."
      - clause: "The S13 fixture independently protects every consequential admission guard"
        test_or_probe: "thirteen one-at-a-time mutations in disposable copies of f4d323f3040e182bab320dd584df2a5c9dc1137c's source state"
        input: "Disable exact numeric comparison, aggregate reconciliation, plan limits, memory refusal, sample-traffic recomputation, physical-probe reconciliation, sampling-law recomputation, nonface mathematics, proof presence, certificate identity, plan identity, rank-budget refusal, or trace-horizon reconciliation."
        expected: "Each removed guard makes the single S13 fixture fail, while certificate, canonical evidence, plan, and profile share no mutable object."
        observed: "All thirteen mutants failed independently at the removed boundary. The fixture's object-identity audit found zero shared mutable objects across the four authorities. Every disposable copy and generated-output directory was removed afterward."
      - clause: "The complete S13 regression, generated-integrity, accounting, and local cleanup gates pass"
        test_or_probe: "the complete pinned CPython 3.13 suite, isolated tools/genschema.py reproduction, tools/ledger.py, git diff checking, hdiutil inspection, and system-volume inspection after f4d323f3040e182bab320dd584df2a5c9dc1137c"
        input: "Run every repository fixture on arm64 macOS with bytecode and pytest caches disabled; regenerate schemas into a disposable directory; recompute commit law, generated integrity, tracked artifacts, imports, citations, pins, runtime confinement, and J; inspect mounted images, temporary bytecode, free space, and the patch."
        expected: "Every fixture passes without a skip; generated files differ by zero bytes; the ledger reports no violation or added dependency, process, runtime, language, model branch, generated output, or executable model kernel; no Cassette image or agent-created temporary remains mounted or stored."
        observed: "All 29 tests passed in 372.18 seconds with no skips. Schema regeneration produced zero diff. The ledger reported zero violations, 3,493 product LOC, 2,502 test LOC, 470 tool LOC, 74 generated LOC, one process, one Python runtime, and the same five exact dependency pins. No Cassette image remained mounted, 92 GiB remained free, and only the pre-existing Build Story edit remained outside S13."
      - clause: "Q19/Q6 bounds canonical exact scalars before construction and gives out-of-domain derived numbers one typed terminal path"
        test_or_probe: "the hostile-scalar and resealed-derived-range injections inside tests/test_s13_pager.py, direct independent replay, and two one-at-a-time guard removals against 095b02ca8b2401091f31caa370497e88f4a98f82"
        input: "Submit the compact exponent bomb 1e1000000000, the reviewer's 1e1000 string and 10**400 integer, then reseal a structurally valid target containing 1e200 so exact witness-loss arithmetic exceeds the finite certificate-number domain. Separately remove the exact-scalar bit boundary and the OverflowError-to-CassetteError conversion."
        expected: "Refuse hostile scalar construction with INVALID_REQUEST; refuse the finite parsed input's unrepresentable derived loss with CAPABILITY_MISMATCH; never leak OverflowError or emit CertifiedSchedule. Each removed guard must make the independent S13 fixture fail."
        observed: "The three hostile scalars returned INVALID_REQUEST at Q19: canonical source scalar. The resealed 1e200 target returned CAPABILITY_MISMATCH at Q19: witness loss condition.a. Removing either new guard made the fixture fail at that boundary. The first complete macOS run passed 28 tests and encountered one S06 hdiutil device-busy error; after stopping the agent-created stale exponent-probe process and detaching its temporary APFS image, the unchanged suite passed 29/29 in 142.70 seconds. Schema reproduction was byte-identical; the ledger reported zero violations, 3,508 product LOC, 2,519 test LOC, 470 tool LOC, 74 generated LOC, one process, one runtime, and the same five exact pins. No Cassette image or probe process remained, 89 GiB remained free, and the pre-existing Build Story edit remained untouched."

  - id: S14
    title: Certified page readiness, stochastic correction, and selection failure
    env: macos
    files: [pager.py]
    discovered_scope: "tests/test_s14_pager.py is the single F3 fixture for Q20/Q64. It imports the disjoint S13 certificate fixture, writes three real SafeTensors pages into one scratch cartridge, and submits only freshly verified bytes through pinned MLX. pager.py remains the sole Q78 pager and scheduler authority above 800 physical lines because page acquisition, certificate-bound selection, and command fencing share one state and one failure boundary; splitting them would add a second pager authority or cross-file plumbing."
    invariants: [Q20 acceptance (forced absent/corrupt exact and sampled pages, stale certificate, out-of-contract seed, timeout, cancel — exact replay or seeded certified replay or typed termination), Q64 acceptance (native prefetch remains non-semantic; compiled selection rejects forged faces, off-support observations, and exhausted horizons); F3 tiny-model fixtures]
    acceptance_injections: [false-high native prefetch, false-low native prefetch, absent native exact page, corrupt native exact page, absent compiled exact page, corrupt compiled exact page, absent sampled page, corrupt sampled page, stale certificate, negative execution seed, forged service face, off-support observation, zero-second page-readiness timeout, pre-set cancellation, exhausted horizon, certified page-read count below the possible sampled-page union, boolean and floating page-map steps and sample units, extra sampling-catalog unit, forged and noncanonical page-map material, malformed native route and prefetch records, malformed compiled selection fields, invalid cancellation control, oversized timeout and prefetch confidence, illegal page-state transition]
    acceptance_boundary: "S14 resolves and validates every native or certificate-planned page, records the seeded correction schedule, and fences one real MLX command on the complete validated set. It does not claim transformer logits, recurrent-state mutation, or KV rollback: S15 owns the end-to-end exact-description and fresh-residual tiny transformer."
    expected_size: large
    done_when: full suite + ledger green
    depends: [S13, S08]
    status: DONE 2026-08-09 — implementation e26278aadc6a2d3bd293038b509aabb69e26b9f9 plus the 2026-08-09 typed-boundary correction binds native execution to the source route, binds compiled execution to the recomputed Q19 certificate and immutable page map, validates every scalar and page identity before Python container or event use, validates every exact and sampled page before one pinned MLX submission, reproduces the certified 1/5-to-4/5 residual schedule from its recorded seed, and preserves replay state on typed failure; the corrected suite passed 30/30 in 127.53 seconds and the ledger reported zero violations with no new dependency, process, runtime, language, kernel, or model branch
    closeout:
      - clause: "Q64 native prefetch cannot change the source-native semantic route"
        test_or_probe: "the false-high, false-low, and no-prefetch executions in tests/test_s14_pager.py::test_q20_q64_f3_page_readiness_replay_and_selection_failure at e26278aadc6a2d3bd293038b509aabb69e26b9f9"
        input: "Execute the same two-page source route with no candidates, confidence one on a valid non-route residual page, and confidence zero on only the first required page."
        expected: "Prediction may order a required read but may neither add to nor remove from the source route. All three executions must submit the complete exact route and return one identical route-dependent result."
        observed: "All three executions returned NATIVE_EXACT over the same two page identities and the same output digest. The false-high residual page never entered planned_pages, while the false-low record still acquired both source pages. Each required page followed ABSENT to ACQUIRING to HASHED to RESIDENT to GPU_SUBMITTED to RECLAIMABLE."
      - clause: "Q20 absent or corrupt exact pages terminate before their first consumer"
        test_or_probe: "the native and compiled exact-page failures in tests/test_s14_pager.py"
        input: "Name a valid BLAKE3 digest absent from the physical index, then flip one byte at the indexed offset of the exact description page. Run both source-native and compiled-certified acquisition against the affected exact page."
        expected: "Return PAGE_CORRUPT before GPU submission, publish no compiled PageExecution, preserve the schedule step, and consume no altered byte."
        observed: "Every absent or corrupt exact-page attempt returned PAGE_CORRUPT. Native and compiled transition records contained no GPU_SUBMITTED state; the compiled pager remained at step zero with last_committed unset. Restoring the original segment bytes restored execution without changing page identity."
      - clause: "Q20 fresh stochastic pages follow the immutable law and replay exactly from the recorded seed"
        test_or_probe: "the two-column seeded replay plus absent and corrupt sampled-page injections in tests/test_s14_pager.py"
        input: "Use two residual columns with exact probabilities 1/5 and 4/5, sixteen fresh draws, three possible physical pages, seed 7 twice, and seed 11 once. Then map both sample units to an absent digest and, separately, corrupt both indexed residual pages."
        expected: "The same certificate and seed produce the same sample record and output. Another allowed seed follows the same certified distribution but may produce another record. Any absent or corrupt sampled page returns PAGE_CORRUPT before the affected command and leaves the step uncommitted."
        observed: "Seed 7 reproduced (1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1) and one identical output digest on both fresh pagers. Seed 11 produced (1,1,0,1,1,1,1,1,1,1,1,1,0,1,1,1) and another output digest. Both absent and corrupt sampled-page attacks returned PAGE_CORRUPT with no GPU_SUBMITTED transition, no committed result, and next_step still zero."
      - clause: "Q64 compiled selection rejects stale identity, foreign support, forged faces, and an exhausted horizon before page I/O"
        test_or_probe: "the four pre-acquisition selection attacks and fourth-step horizon attack in tests/test_s14_pager.py"
        input: "Replace the admitted certificate digest, set the observed condition outside protected support, replace the certified service face with condition.forged, and execute once beyond the three-step trace horizon."
        expected: "Return one canonical typed error at the exact failed relation before any page transition or state advance; preserve the last valid commit when the horizon is exhausted."
        observed: "Each attack returned CAPABILITY_MISMATCH at, respectively, Q64 immutable compiled certificate, certified observation support, certified service face, or certified execution horizon. All pre-acquisition attempts had empty transition records. After three valid commits, the fourth attempt left next_step at three and retained the step-two PageExecution byte-for-byte."
      - clause: "Q20 out-of-contract seeds, timeout, and cancellation preserve the replay boundary"
        test_or_probe: "the negative-seed, zero-second deadline, pre-set cancellation, and retry sequence in tests/test_s14_pager.py"
        input: "Submit seed -1; after committing step zero, set the step-one page-readiness deadline to zero; on a fresh pager, set the cancellation event before step zero and then retry the same CompiledSelection without cancellation."
        expected: "Reject the seed before I/O. Timeout with WORKING_SET_TIMEOUT and cancel with OPERATION_CANCELLED before submission. Preserve certificate identity, selection including seed, next step, and last committed result so the identical request can replay."
        observed: "Seed -1 returned CAPABILITY_MISMATCH at the fresh-random seed contract with no transitions. The timed step entered no GPU_SUBMITTED state, retained the complete step-zero commit, kept next_step at one, and retained the step-one replay selection. The cancelled first step retained its selection and step zero; its immediate retry committed successfully and cleared replay_selection."
      - clause: "The compiled page map cannot understate the union of pages reachable under fresh sampling"
        test_or_probe: "the two-read physical-row injection in tests/test_s14_pager.py and the corrected all-unit route check in pager.py"
        input: "Keep one exact page and two certified residual-unit pages but reseal the otherwise valid physical conversion at two page reads instead of three."
        expected: "Reject before execution because one seeded step can draw both residual units and therefore require the union of all three pages."
        observed: "CertifiedPager construction returned CAPABILITY_MISMATCH at Q20 certified page-read count. This injection was added after internal review found that checking each residual unit separately would admit the understated two-read row."
      - clause: "The S14 fixture independently protects certificate identity and page-content verification"
        test_or_probe: "two one-at-a-time guard removals in disposable copies of e26278aadc6a2d3bd293038b509aabb69e26b9f9's source state"
        input: "First remove the runtime comparison between CompiledSelection.certificate_digest and the admitted certificate. Then replace store._read_page with an unchecked segment slice in the S14 acquisition path."
        expected: "The first mutant must accept the stale selection and fail the fixture. The second must consume the deliberately corrupted exact page and fail the fixture."
        observed: "The stale-certificate mutant failed because the expected CassetteError was not raised. The unchecked-read mutant failed at the corrupt exact-page injection for the same reason. Both disposable copies were removed."
      - clause: "The complete S14 regression, accounting, and local-cleanup gates pass"
        test_or_probe: "the complete pinned CPython 3.13 suite, tools/ledger.py, git diff checking, mounted-image inspection, process inspection, and system-volume inspection on the e26278a source state"
        input: "Run every repository fixture on arm64 macOS with bytecode and pytest caches disabled; recompute commit law, generated integrity, tracked artifacts, imports, citations, pins, runtime confinement, and J; inspect the patch, mounted images, agent-created processes, bytecode, and free space."
        expected: "Every fixture passes without a skip; the ledger reports no violation or added dependency, process, runtime, language, generated output, numerical kernel, or model branch; no S14 scratch cartridge, mutation copy, mounted image, or agent-created test process remains."
        observed: "All 30 tests passed in 227.34 seconds with no skips. The ledger reported zero violations, 3,798 product LOC, 2,724 test LOC, 470 tool LOC, 74 generated LOC, one process, one Python runtime, and the same five exact dependency pins. No Cassette image or S14 process remained, the two mutation copies and S14 bytecode were removed, and 88 GiB remained free."
      - clause: "Q20 page-map steps, descriptions, and sample-unit catalogs use exact declared types and identities"
        test_or_probe: "the resealed boolean, floating-point, extra-unit, and forged-description page maps in tests/test_s14_pager.py plus direct replay against the corrected pager"
        input: "Replace integer step or unit zero with equal-valued false or 0.0, append unit two over an existing page so the physical union does not expose it, replace the description digest with another canonical BLAKE3 identity, and insert a noncanonical Python object into the page map; reseal each JSON-representable plan."
        expected: "Reject every map before runtime-step publication with CAPABILITY_MISMATCH at the exact schedule, sampling-catalog, or description relation; Python numeric equality must not admit a differently typed record."
        observed: "Boolean and floating steps returned Q20 certified schedule page relation; boolean and floating units plus the extra catalog unit returned Q20 certified sampling page catalog; the foreign digest returned Q20 immutable compiled description; noncanonical material returned Q20 immutable page-map identity instead of leaking the store's Q1 error. No malformed runtime step or PageExecution was published."
      - clause: "Q20/Q64 malformed runtime records terminate through the canonical Q6 error boundary"
        test_or_probe: "the malformed native route, native prefetch, compiled selection, and cancellation injections in tests/test_s14_pager.py plus a separate direct replay of the original review probes"
        input: "Supply no native route, no prefetch candidate collection, non-string certificate/condition/atom/description fields, a non-tuple service face, a non-asyncio cancellation object, a 10^400-second timeout, and 10^400 as prefetch confidence."
        expected: "Reject before hashing, set or dictionary lookup, event invocation, page transition, or MLX submission with INVALID_REQUEST or the declared typed capability error; no TypeError, AttributeError, or ValueError may escape."
        observed: "All fourteen direct probes returned CassetteError. Malformed native route and prefetch collections returned INVALID_REQUEST at their named relation; malformed compiled fields returned INVALID_REQUEST at Q64 compiled selection record; invalid cancellation controls returned INVALID_REQUEST at Q20 cancellation control; oversized timeout and confidence values returned INVALID_REQUEST at their bounded numeric relation. Pager state and transitions remained uncommitted."
      - clause: "The corrected S14 guards are independently load-bearing and the complete close gate passes"
        test_or_probe: "eleven one-at-a-time disposable mutations, the complete pinned CPython 3.13 macOS suite, tools/ledger.py, git diff checking, mount/process inspection, and temporary-path inspection"
        input: "Disable integer typing, identifier typing, digest typing, page-map error remapping, transition legality, deadline bounds, cancellation typing, timeout-code mapping, prefetch-confidence bounds, description binding, and sampling-catalog equality separately; then run the complete repository gate on the unmutated correction."
        expected: "Every mutant must fail the S14 fixture. The unmutated tree must pass every repository test and ledger check without a skip or violation, and leave no Cassette image, mutation copy, or S14 process."
        observed: "All eleven mutants failed the S14 fixture at the removed guard. The unmutated tree passed 30/30 tests in 127.53 seconds. The ledger reported zero violations, 3,829 product LOC, 2,776 test LOC, 470 tool LOC, 74 generated LOC, one process, one runtime, and the same five exact pins. No Cassette image, mutation directory, S14 process, or agent-created pager bytecode remained; 82 GiB remained free."

  - id: S15
    title: F3 end-to-end - certified tiny transformer from cartridge
    env: macos
    files: [pager.py, tools/genschema.py, schema/ (generated dispatch)]
    discovered_scope: "tests/test_s15_pager.py is the single F3 fixture for Q19/Q36/Q63. S15 extends the generated Q30 dispatch by six bounded cases and executes one complete diagnostic pre-norm causal decoder: embedding, RMS normalization, Q/K/V projections, positional rotation, causal attention, attention projection and residual, RMS normalization, certified FFN-up description, SiLU, FFN-down and residual, final RMS normalization, and vocabulary projection. pager.py remains the sole execution authority above 800 physical lines because certificate-to-page binding, page readiness, generated MLX dispatch, recurrent commit, and allocation/traffic tracing share one state boundary; splitting that authority would create prohibited pager plumbing or a second runtime authority."
    invariants: [F3 stage gates (one exact description and one fresh-residual-sampling description through the complete nonlinear decoder, forced page failures, seeded reproduction, one-token decode from committed K/V, and KV rollback), Q19 certificate remains valid across the declared trace horizon and its execution error/risk bounds agree with exhaustive observed outcomes, Q63 acceptance (trace equals certified schedule, no hidden allocation or traffic)]
    acceptance_boundary: "S15 proves one diagnostic four-wide float32 pre-norm causal decoder through generated MLX embedding, RMSNorm, matmul, RoPE, causal attention, add, SiLU, and vocabulary-projection cases. It binds every fixed parameter page plus the exact or sampled FFN-up correction through one protected graph, executes exact two-token prefill and one-token fresh decode from committed K/V, and exhaustively checks all four finite correction outcomes against the admitted local error, composed output-error, and risk bounds. It does not claim a general compiler, arbitrary graph tuples, quantized end-to-end execution, source-driven model preparation, model quality, production context growth, or frontier-scale service. S19 and S24 own source-derived representative tuples and quantized execution where the admitted model requires them; Q36 F4 and F5 remain later binding gates."
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S14, S05]
    historical_status: DONE 2026-08-10 — implementation bc2aaa00ae0dfb099cef95b18fd40d4c49840fd1 executes exact prefill and seeded fresh decode from verified cartridge pages through generated MLX embedding, three projections, and attention; commits operative K/V only after the complete trace passes; the final arm64 macOS suite passed 31/31 in 45.41 seconds and the ledger remained clean at 4,059 product LOC, 3,068 test LOC, 470 tool LOC, 74 generated LOC, one process, one runtime, and five exact pins
    status: DONE 2026-08-10 — complete-decoder repair 692d96e and one-token recurrent-state repair d3d1e04 execute the full protected nonlinear graph, reconcile observed execution error and risk, and make committed K/V necessary for decode; the final arm64 macOS suite passed 31/31 in 41.22 seconds and the ledger remained clean at 4,141 product LOC, 3,265 test LOC, 470 tool LOC, 74 generated LOC, one process, one runtime, and five exact pins
    reopened_by: "Opus 5 Max's S15 review identified three blocking proof gaps in bc2aaa: the executed graph ended at flattened attention output rather than a transformer vocabulary projection, the sampled map remained on a linear value path where expected-output equality was automatic, and admitted execution error/risk were never compared with observed execution. Direct inspection and attacks reproduced all three. A fourth fixture weakness appeared during repair: disabling committed K/V consumption left the first repaired overlapping-token fixture green, because the same token at the same position recomputed the same key and value. S15 therefore remained open until a true one-token decode made prior K/V load-bearing and the cache-consumption mutant failed."
    closeout:
      - clause: "F3 stage gate executes one exact description and one fresh-residual-sampling description as one tiny transformer"
        test_or_probe: "tests/test_s15_pager.py::test_q19_q36_q63_f3_transformer_trace_seed_and_kv_rollback plus its independent Python transformer and estimator oracle at bc2aaa00ae0dfb099cef95b18fd40d4c49840fd1"
        input: "Import separate SafeTensors pages for two 120-byte descriptions of one certified A:R3->R2 map: exact B=A, and fresh B=0 with three transposed estimator pages at probabilities 1/4, 1/4, and 1/2. Execute prefill tokens (0,1) and decode tokens (2,3)."
        expected: "Load model pages from the cartridge, dispatch only the generated embedding, matmul, and attention tuples, produce logits equal to an independently computed graph, and make the probability-weighted fresh outputs equal the exact output."
        observed: "Exact prefill read four pages and 120 bytes; fresh decode read five pages and 144 bytes. Each trace named embedding, three matmuls, and attention. Both logits matched the independent oracle within 1e-6, and the three weighted estimator outputs matched exact decode within 1e-12."
      - clause: "F3 forced exact and sampled page failures terminate before the affected model use"
        test_or_probe: "the exact-page, selected-sample, and unselected-sample corruption injections in the S15 fixture"
        input: "Corrupt the exact V page before prefill; after one committed prefill, corrupt seed 7's selected unit-2 correction page; separately corrupt one correction page that seed 7 does not select."
        expected: "Required corruption returns PAGE_CORRUPT before GPU submission or recurrent mutation. An unselected corrupt page causes no read and no output change. Restoring the selected page permits exact replay."
        observed: "Both required corruptions returned PAGE_CORRUPT with no GPU_SUBMITTED transition. The unselected page was absent from the planned route and decode remained byte-identical. Restored retry reproduced the clean logits and final KV digest."
      - clause: "F3 seeded execution reproduces one immutable correction choice"
        test_or_probe: "two complete seed-7 runs, the bounded alternate-seed sweep, and the post-closeout direct seed probe"
        input: "Run the same certificate, exact schedule digest, tokens, and seed 7 twice; then run seeds 8 through 63 until the first different legal sample appears."
        expected: "The same seed reproduces sampled units, page route, logits, and KV bytes; a seed selecting another unit changes the stochastic result without changing the certificate."
        observed: "Seed 7 selected unit (2,) twice and reproduced logits plus KV digest blake3:4ad7c3b1f434c9e0097d67e896e5b01ae6a7565a07cce9fb654b99e7e6bcd07e. Seed 8 selected unit (0,) and changed both logits and KV digest."
      - clause: "F3 K/V state is operative and rolls back on failure"
        test_or_probe: "history substitution, selected-page failure after prefill, retry, horizon, and runtime-allocation failure inside the S15 fixture"
        input: "Hold decode tokens and seed fixed while changing only the prefill history; snapshot the 32-byte prefill K/V state; then fail the selected decode page and retry it after byte restoration."
        expected: "Prior K/V changes decode, failed decode preserves the last committed 32 bytes and step, and retry alone extends the state to the admitted 64-byte horizon."
        observed: "Changing only prefill tokens changed decode logits and KV identity. Selected-page failure left next_step=1, the exact 32-byte snapshot, and the prefill result intact; retry produced the clean 64-byte state. The recurrent-state guard-removal mutant failed the independent decode oracle."
      - clause: "Q19 remains valid across the declared exact and fresh horizon"
        test_or_probe: "certificate admission, transposed semantic-page substitutions, exact/fresh execution, and exhausted-horizon injection in the S15 fixture"
        input: "Use a rank-2 A in R(2x3), exact reconstruction A, zero fresh reconstruction, certified column probabilities, composition coefficient 2, and a two-step coherent trace. Reseal page maps that substitute same-length wrong description or correction pages; then request a third step."
        expected: "Bind A to the physical A-transpose projection representation, bind every sampled column estimator to its physical transpose, preserve the conservative attention propagation bound, and reject semantic substitutions or a step beyond h=2."
        observed: "The admitted certificate recomputed rank, zero representation loss, distortion 4, norm-squared 4, fresh traffic 2, epsilon aggregate 4, risk 1/2, and horizon 2. Wrong same-length pages failed their exact semantic relation, and the third request returned Q64 certified execution horizon without changing KV."
      - clause: "Q63 observed traffic and model memory equal the certified schedule with no hidden allocation"
        test_or_probe: "literal trace assertions, physical-row plus-one attacks, and the runtime-buffer mismatch injection in the S15 fixture"
        input: "Trace both instants; separately raise the certified exact load by one byte, dynamic memory by one byte, or runtime-buffer claim from the measured 36 bytes to 37 while leaving execution unchanged."
        expected: "Every planned page, generated operator, loaded byte, model tensor, activation, KV reservation, MLX peak, and total model byte maps to the admitted schedule; any reconciled overstatement or unobserved allocation claim fails."
        observed: "Prefill reported description/metadata/load/dynamic/live bytes 120/144/120/384/612; decode reported 120/251/144/515/743. Both observed 120 model-tensor bytes, 128 activation bytes, 64 reserved KV bytes, 36 MLX runtime bytes, and a 284-byte Metal peak. Both plus-one physical attacks failed at Q63 schedule equality; the 37-byte runtime claim failed before commit."
      - clause: "The S15 guards and complete repository close gate remain consequential"
        test_or_probe: "seven one-at-a-time disposable mutations, the complete pinned CPython 3.13 macOS suite, tools/ledger.py, git diff checking, and temporary-environment cleanup"
        input: "Remove description-page binding, correction-page binding, schedule equality, recurrent-state consumption, runtime-allocation equality, transpose binding, or the certified V projection separately; then run every repository fixture and the ledger on the accepted tree."
        expected: "Every mutant fails the single S15 fixture. The accepted tree passes every test and ledger check with no skip, dependency, kernel, process, runtime, model branch, or generated-file change."
        observed: "All seven mutants failed at the damaged semantic, resource, recurrent, allocation, orientation, or graph assertion. The accepted tree passed 31/31 tests in 45.41 seconds; the ledger reported zero violations and the same five exact pins. The disposable mutant trees were moved to Trash and no Cassette test image remained mounted."
    remediation_closeout:
      - clause: "Q36 F3 executes a complete diagnostic causal decoder and returns vocabulary logits"
        test_or_probe: "tests/test_s15_pager.py::test_q19_q36_q63_f3_decoder_trace_nonlinear_risk_and_kv_rollback plus its independent scalar decoder oracle after 692d96e"
        input: "Load signed and fractional four-wide parameters from twelve verified cartridge pages, then execute exact prefill tokens (0,1) and fresh one-token decode token (2) through the protected generated operator sequence."
        expected: "Execute embedding, attention pre-normalization, Q/K/V projection, position-dependent RoPE, causal attention, attention projection and residual, FFN pre-normalization, certified FFN-up, SiLU, FFN-down and residual, final normalization, and vocabulary projection. Return only the final position's four vocabulary logits."
        observed: "Both paths executed the complete graph through MLX and matched the independent scalar oracle within 2e-5. The protected target includes negative quarter values and sixteenth fractions. Each step returned a four-value vocabulary vector rather than a flattened attention tensor."
      - clause: "Q19 fresh residual execution remains stochastic after nonlinear composition and its declared error and risk are observed"
        test_or_probe: "the exhaustive four-outcome estimator, SiLU, decoder-output, and low-bound contradiction phases of the S15 fixture"
        input: "Use correction probabilities 16/49, 16/49, 16/49, and 1/49; execute every deterministic seed-selected outcome through SiLU and the remaining decoder; then admit a separately sealed certificate whose propagation coefficient is 1/20 instead of 21/100."
        expected: "The probability-weighted stochastic vocabulary output may differ from exact output after nonlinear composition. Every observed local and final error satisfies the accepted 21/100 propagation bound, local and final event risks satisfy delta 1/2, and the understated 1/20 bound fails the independent observed-outcome audit even though S13 can admit its internally coherent arithmetic."
        observed: "Weighted stochastic logits differed from exact logits. The exhaustive outcomes reproduced expected local squared error, local risk 1/49, final risk zero, and aggregate epsilon 0.315. The 1/20 certificate reached execution but failed the observation audit, proving that S15 now checks execution evidence rather than certificate consistency alone."
      - clause: "Every physical parameter and generated operator remains bound to one immutable protected graph"
        test_or_probe: "foreign fixed-page, base-page, correction-page, operator, graph-digest, and exact-type injections in the S15 fixture"
        input: "Substitute same-length pages for fixed graph roles, the exact FFN base, or a sampled correction; alter one operator case; alter only the plan's tensor-graph digest; and replace unsigned graph integers with equal-valued floats."
        expected: "The generic S13 pager may admit structurally coherent records, but the F3 execution authority rejects every graph, semantic-page, operator-tuple, or scalar-type mismatch before MLX submission."
        observed: "Every substitution terminated at its Q19/Q30/Q36 relation. The plan's tensor-graph digest equals the protected trace-family digest, all fixed and exact/fresh parameter roles are page-bound, and floating-point lookalikes cannot satisfy graph integers."
      - clause: "One-token decode consumes committed K/V and failed work cannot change recurrent state"
        test_or_probe: "the first cache-consumption mutation, the repaired one-token decode oracle, a second cache-consumption mutation, history substitution, selected-page corruption, retry, runtime-allocation failure, and horizon exhaustion"
        input: "First disable the repaired decoder's prior-K/V branch while it still accepted overlapping two-token decode input. After that mutant survives, change the public decode contract to one new token, bind a padding token in the fixed two-position graph, replace that padding position's K/V from the committed prefill state, and disable prior-K/V consumption again."
        expected: "The first escape must prevent closeout. In the corrected graph, decode output and K/V identity depend on the committed history; removing cache consumption fails the fixture. Page, allocation, and horizon failures preserve the last committed snapshot and permit exact replay."
        observed: "The first repair was not sufficient: one of twelve mutants stayed green because the overlapping token at the same position recomputed byte-equivalent K/V. After the one-token correction, the cache-consumption mutant failed, changing prefill history changed decode logits and KV identity, and every injected failure preserved the 32-byte checkpoint until a successful retry extended it to the certified 64-byte horizon."
      - clause: "Q63 traffic and memory describe the complete graph without hidden allocation"
        test_or_probe: "literal trace assertions, physical-row plus-one attacks, runtime-buffer mismatch, and measured MLX peak in the S15 fixture"
        input: "Execute both steps with twelve planned page reads and 624 loaded bytes; then overstate physical bytes, dynamic memory, or runtime-buffer bytes by one while leaving execution unchanged."
        expected: "Observed page reads, loaded bytes, model tensors, activations, K/V reservation, runtime buffers, Metal peak, dynamic memory, and live memory equal the admitted schedule exactly."
        observed: "Both steps read twelve pages and 624 bytes, held 624 model-tensor bytes and 680 activation bytes, reserved 64 KV bytes, observed zero unaccounted runtime bytes, and measured a 1,304-byte Metal peak. Exact metadata/dynamic/live bytes were 141/1,389/2,133; fresh metadata/dynamic/live bytes were 360/1,608/2,352. Every plus-one claim failed before recurrent commit."
      - clause: "The repaired S15 fixture can disprove its consequential guards and the complete repository gate passes"
        test_or_probe: "two disposable mutation campaigns, the complete pinned CPython 3.13 macOS suite, tools/ledger.py, git diff checking, mount inspection, and temporary-environment inspection after d3d1e04"
        input: "Mutate graph identity, graph integer typing, route binding, base and correction semantics, estimator probability scaling, KV consumption, RoPE, SiLU, vocabulary projection, and runtime allocation one at a time."
        expected: "No consequential mutation remains green. The accepted tree passes every repository fixture and ledger check with no skip or violation and leaves no mounted Cassette image."
        observed: "The first twelve-mutant campaign exposed one surviving cache-consumption mutant and blocked closeout. After the one-token repair, all eleven final mutants failed at the removed behavior. The accepted tree passed 31/31 tests in 41.22 seconds; the ledger reported zero violations, 4,141 product LOC, 3,265 test LOC, 470 tool LOC, 74 generated LOC, one process, one Python runtime, and five exact pins. No Cassette image remained mounted."

  - id: S16
    title: Canonical broker
    env: any
    files: [broker.py]
    discovered_scope: "tests/test_s16_broker.py is the single F1 fixture for Q5/Q6/Q52, and AGENTS.md records broker.py as the sole writer of canonical operation logs, broker ownership, and ordered operation events. broker.py remains the one Q78 broker authority above 800 physical lines because durable record validation, Q5 phase ownership, Q6 idempotency/cancellation/events, and Q52 source orchestration all mutate one operation record; splitting them would create a second operation-log authority or cross-file state plumbing."
    invariants: [Q5 acceptance (interrupt every transition, idempotent replay), Q6 acceptance (double issue, cancel every phase, typed failures, monotonic events), Q52 acceptance (the production acquisition state machine is unchanged across every source adapter)]
    acceptance_boundary: "SOURCE_VERIFIED records that Q51 completed successfully; it does not make the source bytes callable or prove their present contents. The broker may advance toward PUBLISHED only after the owning preparation operation returns current-byte verification and a verified canonical root. The broker never reads source extents or treats PartialState as that verification. S16 proves this production state machine with deterministic source fixtures and explicit F1 plan/prepare seams because compiler.py does not exist yet; it does not claim live source wires or a production compiler binding. L02 owns the live Hugging Face, Ollama, and Tinker wires. S19 must replace the F1 seams with the canonical broker-to-compiler binding, S24 must replay that complete path on deterministic generated fixture material, and L03 must replay it on the first real model after S28."
    expected_size: large
    done_when: full suite + ledger green
    depends: [S03, S07, S10]
    status: DONE 2026-08-10 — ownership and durable-record remediation 39d36aeeb6ba7fbb66decf2aec7c8b8346f9424e plus explicit pause-event proof 142289849b05e5cfba2921f848d21886a58dcdb6; every corrected guard failed independently when removed; the final complete pinned macOS suite passed 32/32 in 97.31 seconds and the ledger reported zero violations at 4,762 product LOC, 3,650 test LOC, 470 tool LOC, 74 generated LOC, one process, one runtime, and the same five exact pins
    reopened_by: "Opus 5 Max and Kimi K3 Max independently exposed S16 proof gaps. GPT-5.6 Sol Ultra reproduced the cross-instance duplicate worker and inert forged non-prepare phase before reopening the row."
    prior_status: DONE 2026-08-10 — implementation 497a4a3f009097e17cd79650ffa526b4cdb4316f and closeout b0ebce21ee70d9b8c0a449b5f49747ffdaf94e73 claimed Q5/Q6/Q52 complete after 32/32 tests, but the fixture did not protect paused advancement or cross-instance ownership
    closeout:
      - clause: "Q5 resumes every source-to-callable transition from one durable idempotency record and exposes no revision before PUBLISHED"
        test_or_probe: "tests/test_s16_broker.py::test_q5_q6_q52_durable_idempotent_broker_is_source_blind_and_terminal_exact at 497a4a3f009097e17cd79650ffa526b4cdb4316f"
        input: "For each of the three deterministic source fixtures, issue one prepare request twice, execute exactly one transition, reconstruct CanonicalBroker from the operation-log directory, rename the scratch cartridge between every transition, and replay the same request. Attempt callable_revision before each pre-publication phase, at PUBLISHED, after ACTIVE, and after terminal replay; then change the target under the same idempotency key."
        expected: "Persist the literal EMPTY through ACTIVE prefix once, retain one operation ID across every restart and path move, refuse every pre-PUBLISHED call, expose the store-verified generation at PUBLISHED, return the same terminal result without another source request, and reject changed request material with IDEMPOTENCY_CONFLICT."
        observed: "Hugging Face, Ollama, and Tinker each followed EMPTY, RESOLVED, RESERVED, ACQUIRING, SOURCE_VERIFIED, PLANNED, PREPARING, EXEC_VERIFIED, PUBLISHED, and ACTIVE exactly once. Every pre-publication call returned OPERATION_NOT_FOUND; PUBLISHED and ACTIVE returned the same verified root; terminal replay made zero source requests; changed target material returned IDEMPOTENCY_CONFLICT."
      - clause: "Q6 double issue, cooperative cancellation, canonical typed failure, and event sequencing have one terminal result"
        test_or_probe: "the generated operation/error/cancellation cross-product in tests/test_s16_broker.py plus the concurrent-worker probe"
        input: "Issue nine representative lifecycle operation names twice; inject each of the 29 errors in errors.CODES through the production execute path; cancel snapshots at EMPTY through EXEC_VERIFIED; cancel one live asynchronous worker; and submit the same successful operation concurrently twice."
        expected: "Bind each repeated request to one operation, preserve each exact CassetteError, cancel every mutable phase with OPERATION_CANCELLED, keep every event sequence contiguous from zero, append exactly one matching terminal event, and invoke the concurrent worker once."
        observed: "Every repeated request returned one operation ID. All 29 error codes survived exactly into FAILED or CANCELLED as appropriate. All eight mutable Q5 phases and the live worker cancelled with one terminal event. Every sequence was contiguous, and the concurrent duplicate invoked its worker once and returned one byte-identical terminal operation to both callers."
      - clause: "Q52 substitutes every declared source adapter without changing the production acquisition state machine"
        test_or_probe: "the three-source acquisition loop and source-branch AST audit in tests/test_s16_broker.py"
        input: "Serve distinct Hugging Face, Ollama, and Tinker control wires carrying one valid SafeTensors artifact each, then run each through CanonicalBroker with no source-specific caller branch. Scan broker.py control branches for all three source-kind literals."
        expected: "Call resolve, enumerate, metadata, requirements, and range through one fixed broker path; emit one identical Q5 phase trace for every source; retain credentials only as opaque references; and contain every source-kind branch inside sources.py."
        observed: "Each source produced the same five calls in the order resolve, artifacts, metadata, requirements, range and the same ten-phase broker trace. The AST audit found no source-kind branch in broker.py, and the durable operation logs contained no fixture credential bytes."
      - clause: "SOURCE_VERIFIED is resume evidence only; publication requires fresh preparation evidence, plan identity, source binding, and a verified canonical root"
        test_or_probe: "the PartialState, changed-artifact, changed-plan, foreign-root, changed-reservation, and premature-call attacks in tests/test_s16_broker.py"
        input: "At PREPARING, return a PartialState instead of PreparedRevision; alter the verified artifact digest; alter the plan digest; return a valid root bound to a foreign canonical locator; and at RESERVED replace the live reservation with another byte record. Attempt publication or callable access after each attack."
        expected: "Reject PartialState with CAPABILITY_MISMATCH, reject changed byte/plan/root evidence with IDENTITY_MISMATCH, reject reservation drift with IDEMPOTENCY_CONFLICT, publish no attacked operation, and never read a source extent inside broker.py."
        observed: "Every attack terminated at its named boundary with the expected typed code. No attacked operation reached EXEC_VERIFIED or PUBLISHED. The broker accepted current-byte evidence only as PreparedRevision, independently loaded the canonical root through store.py, compared its Q1 material with the durable source lock, and never opened or read a transfer extent."
      - clause: "The S16 fixture protects its consequential guards and the repository gate passes"
        test_or_probe: "eight one-at-a-time disposable mutations, the complete pinned CPython 3.13 suite, tools/ledger.py, git diff checking, mount inspection, and system-volume inspection"
        input: "Remove idempotency conflict detection, callable gating, PartialState refusal, live-capacity binding, terminal-event mapping, current-byte evidence comparison, plan binding, or candidate-root binding one at a time. Then run every repository fixture and the accounting ledger on the accepted tree."
        expected: "Each removed guard makes the S16 fixture fail. The accepted tree passes every fixture and ledger check with no mounted scratch image, generated drift, structural violation, or unrecorded J increase."
        observed: "All eight mutants failed independently. The complete suite passed 32 tests in 47.29 seconds with no skips. The ledger reported zero violations, 4,724 product LOC, 3,523 test LOC, 470 tool LOC, 74 generated LOC, one process, one Python runtime, and the same five exact pins. No Cassette or pytest image remained mounted, and 86 GiB remained free."
      - clause: "Q5 pauses every mutable acquisition phase and resumes from the exact durable checkpoint"
        test_or_probe: "the generated eight-phase pause/restart loop and live-worker pause in tests/test_s16_broker.py"
        input: "At EMPTY through EXEC_VERIFIED, pause an independently cloned durable operation, attempt advancement before and after closing and reconstructing the broker, compare the complete paused record bytes, resume, and compare phase, checkpoint, event sequence, and terminal-event absence. Separately pause a live generic worker, try to execute a forbidden replacement worker while paused, reconstruct the broker, resume, and complete."
        expected: "No paused operation advances or mutates its record. Every restart returns the same PAUSED operation and checkpoint. Resume changes only the declared control state and event. Live work stops cooperatively, stays stopped until resume, and then reaches one terminal result."
        observed: "All eight mutable Q5 phases retained byte-identical paused records across two blocked advance attempts and one broker reconstruction. Every resume retained the exact phase and checkpoint with a contiguous nonterminal event stream. The live worker stopped, the forbidden worker was never called, reconstruction returned the same PAUSED operation, and resume completed once from EMPTY."
      - clause: "Q6 admits one live broker owner per canonical operation log across instances and processes"
        test_or_probe: "the same-process owner, child-process owner, closed-owner, and process-death recovery probes in tests/test_s16_broker.py"
        input: "Open one operation log through CanonicalBroker, attempt a second instance in the same process, close the owner and try to use the closed object, acquire the same log in a child process, attempt a parent owner, terminate the child without broker cleanup, and reacquire the log."
        expected: "Each competing owner fails with retryable OVERLOADED before worker execution or record mutation. A closed object cannot write. Clean close and process death release the kernel authority, after which one replacement owner reads the exact existing operation."
        observed: "Both same-process and cross-process competitors returned OVERLOADED. The closed object returned OVERLOADED. After clean close and after forced child-process death, one replacement acquired the log and returned the byte-identical operation; no duplicate worker could begin."
      - clause: "Q6 durable records reject impossible generic phases, foreign checkpoints, and terminal/event disagreement through typed errors"
        test_or_probe: "the generic phase/checkpoint forgeries and isolated terminal-without-event injection in tests/test_s16_broker.py"
        input: "Recompute valid envelope digests after assigning ACTIVE to a pending run, adding a foreign checkpoint to an EMPTY run, or deleting the sole completed event from a successful run."
        expected: "Reject every forged record with ROOT_INVALID before projection or use; no inert impossible phase and no raw IndexError may escape."
        observed: "All three records returned ROOT_INVALID. Non-prepare records now require literal EMPTY phase and an empty checkpoint, and terminal state/event agreement is isolated by a fixture that fails when its guard is removed."
      - clause: "Q6 pause and cancel return one public operation shape in every control state"
        test_or_probe: "the per-phase inactive controls and live-worker control in tests/test_s16_broker.py"
        input: "Pause or cancel inactive durable operations and compare their fields with the public operation schema returned by live control paths."
        expected: "Return only operation_id, kind, state, progress, and the applicable canonical error; never expose the internal checkpoint, requests, flags, or event array according to whether work happens to be active."
        observed: "Inactive pause and cancel now return the same public projection as live control. Removing either projection wrapper makes the S16 fixture fail."
      - clause: "S16 states its F1 boundary and assigns the real compiler integration without closing it early"
        test_or_probe: "the corrected S16, S19, and S24 rows in IMPLEMENTATION.md"
        input: "Reconcile the fixture-supplied plan and prepare callables, deterministic source servers, absent compiler.py, and later real-model campaign against the implementation queue."
        expected: "Keep the production Q5 state machine in S16, state that F1 uses explicit plan/prepare seams and fixture wires, assign canonical broker-to-compiler binding to S19, require S24 to replay the complete path on deterministic generated fixture material, and defer the first real-model replay to L03 after S28."
        observed: "S16 now names the F1 and live-wire limits. S19 depends on S16, may modify broker.py, and must remove arbitrary caller-supplied revision production. S24 requires a deterministic generated-fixture broker-to-compiler replay. L02 retains live source-wire ownership, and L03 retains the first real-model replay after S28."
      - clause: "The S16 remediation guards are independently load-bearing and the complete repository gate passes"
        test_or_probe: "eight disposable one-at-a-time mutations, the complete pinned CPython 3.13 macOS suite, tools/ledger.py, mount/process inspection, and temporary-path inspection"
        input: "Remove the execute pause gate, acquisition pause gate, canonical owner lock, closed-owner gate, generic-record grammar, terminal-state/event guard, public pause projection, or public cancel projection separately; then execute the accepted tree from the pinned environment."
        expected: "Every mutant fails the S16 fixture. The accepted tree passes every repository test and accounting check without a skip, mounted image, surviving child, mutation tree, dependency, process, runtime, numerical kernel, or model-specific branch increase."
        observed: "All eight mutants failed at the removed behavior. After the explicit event assertions landed, the accepted tree passed 32/32 tests in 97.31 seconds. The ledger reported zero violations, 4,762 product LOC, 3,650 test LOC, 470 tool LOC, 74 generated LOC, one process, one Python runtime, and the same five exact pins. No Cassette image, pytest process, child broker, or mutation directory remained; 85 GiB remained free."

  - id: S17
    title: Scheduler, leases, negotiation
    env: any
    files: [broker.py, pager.py, tools/genschema.py, schema/ (generated Q77 contracts)]
    discovered_scope: "tests/test_s17_broker.py remains the single executable Q47/Q65/Q77 broker fixture. pager.py exposes the cache_bytes term already admitted by Q47; broker.py consumes that term without recomputing the memory formula and derives every page length through store.py from one verified root index. tools/genschema.py emits the request, callable-profile, negotiated-result, and field-table authorities for Q77. No dependency, process, runtime, on-disk object type, adapter, numerical kernel, or model-specific branch is introduced. broker.py remains the one Q78 broker authority above 800 physical lines because negotiation, queue admission, leases, activation, cache identity, cancellation, and canonical operation events meet at one run-admission boundary; splitting them would create a second scheduler or operation authority."
    invariants: [Q47/Q65 cache-byte acceptance (verified page lengths, exact boundary, active-plan prefetch budget), Q65 acceptance (competing clients, switches, no stale cache), Q77 acceptance (generated exact pre-admission accept/reject)]
    acceptance_boundary: "S17 proves the broker scheduler, generated Q77 boundary, and byte-denominated cache-admission ledger against a real scratch cartridge root containing canonical full and tail pages. The fixture supplies the immutable CertifiedSchedule because compiler.py does not exist yet, and the broker tracks admitted page identities and lengths rather than loading MLX buffers itself. S19 owns the production compiler-to-broker binding of a recomputed schedule, root, and page catalog; S21 owns a trainer-produced committed boundary; S24 executes those bindings with pager residency on deterministic generated fixture material; L03 executes them on real models after S28. These absent-producer integrations remain open and named; S17 does not claim them."
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S16]
    historical_status: "DONE 2026-08-10 — implementation 0d9ed90795696befc72fb14a276f85f3c46e250d; eighteen consequential guards failed independently when removed; the complete pinned macOS suite passed 33/33 in 89.60 seconds and the ledger reported zero violations at 5,231 product LOC, 4,110 test LOC, 470 tool LOC, 74 generated LOC, one process, one runtime, and the same five exact pins"
    status: "DONE 2026-08-10 — remediation e616fdccd8ff4974cb403acece08d902e64c48fc; ten new consequential guards failed independently when removed; the final complete pinned macOS suite passed 33/33 in 154.02 seconds and the ledger reported zero violations at 5,241 product LOC, 4,247 test LOC, 478 tool LOC, 92 generated LOC, one process, one runtime, and the same five exact pins"
    closeout:
      - clause: "Q77 exposes every capability field with provenance, negotiates one exact immutable subset, and rejects unsupported or forged material before admission"
        test_or_probe: "tests/test_s17_broker.py::test_q47_q65_q77_exact_negotiation_fair_leases_switches_and_cache_identity plus the negotiation-bytes, reuse, table-bound, activation-authority, and exact-revision-shadow mutations"
        input: "Register profiles covering all nineteen Q77 capability fields and their provenance; request supported subsets, valid unsupported values, and BEST_EFFORT-only features; submit unknown fields, malformed values, forged revision and context-limit records, concurrent reuse of one negotiation, a 1,025th unadmitted negotiation, a conflicting activation authority, and an alias equal to another exact revision."
        expected: "Return one machine-readable immutable exact subset with field evidence. Reject every unsupported, malformed, forged, stale, reused, overloaded, conflicting, or shadowing request before an operation record, queue entry, lease, cache allocation, activation, or worker exists."
        observed: "The supported request retained the exact requested limits and explicit false features. Every negative combination returned its canonical typed error before an operation file existed. One negotiation admitted one run only, including under concurrent reuse; the pending table stopped at 1,024; activation conflicts and exact-revision shadowing were refused."
      - clause: "Q77 keeps an admitted run on its negotiated revision while concurrent alias changes invalidate every unadmitted stale negotiation"
        test_or_probe: "the active-run, queued-old-run, stale-unadmitted, new-run, and scheduler-lock alias-race sections of the S17 fixture"
        input: "Negotiate three requests through one alias at revision A, admit an active and a queued request, switch the alias to revision B, dispatch the stale unadmitted request, negotiate and dispatch a new B request, and separately change an alias while dispatch waits for the scheduler lock."
        expected: "Keep both admitted runs pinned to A. Reject the stale unadmitted and lock-race requests before durable admission. Run the new request on B. Activate A once and B once; never substitute the alias's later target into an admitted run."
        observed: "The active and queued requests completed on A, both stale paths returned CAPABILITY_MISMATCH without operation files, the new request completed on B, and the activation trace contained exactly A then B."
      - clause: "Q65 dispatches competing clients through bounded deficit round robin with deterministic age promotion and isolated context events"
        test_or_probe: "the literal two-client dispatch trace, expensive-request age trace, context/event assertions, per-client queue attack, and global queue attack in the S17 fixture"
        input: "Queue two equal-cost jobs for each of two clients behind one held lease; queue one cost-sixteen job against cheap jobs; submit a ninth queued job for one client and a sixty-fifth job globally; then inspect contexts and event sequences."
        expected: "Dispatch a1, b1, a2, b2; promote the expensive job after the declared age threshold; reject both queue overflows before operation creation; preserve each request's context and contiguous private event sequence."
        observed: "Dispatch order was exactly a1, b1, a2, b2. The expensive job ran after cheap-0 through cheap-3 with one recorded age promotion. Per-client depth stopped at eight, global depth stopped at sixty-four, both excess requests left no operation file, and contexts and event sequences remained disjoint."
      - clause: "Q65 serializes EXEC, WRITE, and SWITCH leases; training yields only at a committed boundary; cancellation and pause release no resource before the final fenced command"
        test_or_probe: "the WRITE/EXEC exclusion, invalid training result, active cancellation finalizer, pause/resume lease-epoch, forged-lease, and stale-lease sections of the S17 fixture"
        input: "Hold a WRITE lease while an EXEC request waits; return a valid and then an absent committed_boundary; cancel active execution whose finalizer inspects its live lease; pause and resume one operation; and use forged and released lease objects against cache access."
        expected: "Never overlap WRITE with EXEC or SWITCH. Admit the waiting inference only after the training boundary is durable. Reject training without an immutable boundary. Keep the cancelled lease live through worker finalization, then release it. Issue a fresh lease epoch on resume and reject every forged or stale lease."
        observed: "The lease table held WRITE alone until its committed digest returned, then admitted EXEC. Missing committed_boundary failed. The cancellation finalizer observed its lease still live; the terminal cancellation event followed finalization. Resume issued a different epoch and lease ID, and old, released, and forged leases all failed before cache use."
      - clause: "Q65 binds cache identity to revision, plan, precision, and semantic state while Q47-byte prefetch preserves pinned pages and bounds churn"
        test_or_probe: "the A-to-B switch over verified full pages and cache-byte trace plus separate one-field cache-key mutations for revision, plan, precision, and semantic state"
        input: "Pin two canonical four-mebibyte revision-A pages inside a sixteen-mebibyte admitted cache budget, prefetch four canonical revision-B pages while A remains active, release A, activate B, and inspect every cache key, byte total, page length, and churn counter. Mutate each cache-key coordinate out of the production tuple one at a time."
        expected: "Use the exact four-coordinate key and the active Q47 budget in bytes. Fill only eight unreserved mebibytes during prefetch, evict no pinned A page, perform exactly two full-page evictions after A releases, expose only B pages to B, and reject access through an A or forged lease."
        observed: "Every lease carried the exact revision, plan, precision, and semantic-state tuple. Prefetch held exactly sixteen mebibytes: two pinned A pages and two B pages. Activation of B caused exactly two full-page evictions; B then held four verified pages and could not use A's released authority. Each cache-key-coordinate mutation failed the fixture independently."
      - clause: "The S17 proof surface makes each consequential admission, fairness, lease, switch, cache, cancellation, and authority guard load-bearing"
        test_or_probe: "eighteen one-at-a-time disposable mutations, the complete pinned CPython 3.13 macOS suite, tools/ledger.py, git diff checking, mount inspection, and system-volume inspection"
        input: "Remove negotiation-byte equality, stale-alias purge, lock-race revalidation, pinned-page protection, age promotion, queue bounds, negotiation-table bounds, WRITE boundary validation, lease epochs, live-lease equality, negotiation single use, cancellation fencing, each of four cache-key coordinates, activation authority, or exact-revision-shadow refusal separately; then execute the accepted tree."
        expected: "Every mutant fails at the removed behavior. The accepted tree passes every repository fixture and accounting check without a mounted scratch image, surviving mutation tree, dependency, process, runtime, schema, numerical kernel, or model-specific branch increase."
        observed: "All eighteen mutants failed decisively; none timed out. The accepted tree passed 33/33 tests in 89.60 seconds. The ledger reported zero violations, 5,231 product LOC, 4,110 test LOC, 470 tool LOC, 74 generated LOC, one process, one Python runtime, and the same five exact pins. No Cassette image remained mounted, all disposable mutation trees were removed, and 83 GiB remained free."
      - clause: "Q47 and Q65 admit cache work in verified bytes rather than page count"
        test_or_probe: "the canonical full-page, tail-page, exact-equality, equality-minus-one, same-count, unknown-page, active-budget, and A-to-B traces in tests/test_s17_broker.py"
        input: "Import six distinct four-mebibyte pages and one nine-byte tail into one scratch cartridge. Bind callable profiles to pager schedules and that verified root; admit the tail at nine bytes and a full page at 4,194,304 bytes; offer the same one full page to a nine-byte budget and to a 4,194,303-byte budget; offer an absent digest; then queue a 4,194,304-byte page for a wider plan while the nine-byte plan remains pinned."
        expected: "Derive every length from store.page_locations. Admit equality. Reject the same-count larger page, equality minus one, and the absent page before an operation record. During cross-plan prefetch, retain the active plan's nine-byte Q47 budget and its pin; adopt the wider budget only after quiescence."
        observed: "The broker reported the exact nine-byte and 4,194,304-byte cache totals. Both over-budget cases returned MEMORY_BUDGET_EXCEEDED and the absent digest returned PAGE_CORRUPT before an operation file existed. While the tail lease was live, the full page did not enter the cache and the exposed budget remained nine bytes; after release and switch, the budget became 4,194,313 bytes and the full page admitted without evicting the tail."
      - clause: "Q77 request, callable-profile, negotiated-result, field list, and provenance shapes have one generated authority used by the broker"
        test_or_probe: "tests/test_s03_schema.py and the generated-validation attacks inside tests/test_s17_broker.py"
        input: "Generate all Q77 records and the nineteen-field table; validate exact golden records; then omit provenance, duplicate a set-valued field, use a boolean as an integer limit, submit an unknown provenance status, and remove one generated field from the authority."
        expected: "Keep the Q31 capability_profile contract intact. Reject every malformed Q77 request or profile through generated validation, reject drift between Q77's literal acceptance field set and the generated table, and emit one shared provenance record rather than duplicating it in every field."
        observed: "The Q31 record remained unchanged. capability_request, callable_capability, negotiated_capability, and capability_field_provenance regenerated deterministically and passed round-trip validation. Every malformed case failed before registration or negotiation; removing one generated Q77 field failed the independent literal field check. Replacing the shared provenance reference with an unconstrained object failed the S17 fixture."
      - clause: "S17 states rather than hides the producers and physical execution that do not yet exist"
        test_or_probe: "the S17 acceptance_boundary and the S19, S21, and S24 queue rows"
        input: "Reconcile the fixture-created CertifiedSchedule, verified scratch root, broker cache-admission ledger, absent compiler.py, absent trainer.py, and later real-model campaign against the implementation queue."
        expected: "Claim only scheduling, Q77 negotiation, and byte-accounted cache admission here. Assign compiler-produced schedules and page catalogs to S19, trainer-produced committed boundaries to S21, and real pager residency through the complete model path to S24."
        observed: "The S17 boundary now names all three fixture seams and their owners. No absent producer or physical MLX residency is reported as implemented by S17."
      - clause: "The S17 remediation guards and generated authorities are independently load-bearing"
        test_or_probe: "ten one-at-a-time disposable mutations, the complete pinned CPython 3.13 macOS suite, tools/ledger.py, git diff checking, mount inspection, temporary-path inspection, and system-volume inspection"
        input: "Replace the propagated Q47 cache term with zero; remove byte admission; replace verified lengths with one; bypass callable and request validation; spend the queued plan's budget instead of the active plan's; count inserted pages as one byte; bypass the absent-page guard; remove one generated Q77 field; or replace generated provenance references with unconstrained objects."
        expected: "Every mutant fails its owning fixture. The accepted tree passes the complete suite and accounting gate with no surviving mutation tree, agent-created image, dependency, process, runtime, kernel, or model branch."
        observed: "All ten mutants failed independently. One initial schedule mutation survived because its assertion used a zero cache term; the fixture was corrected to exercise a nonzero cache boundary, after which all ten failed. The final accepted tree passed 33/33 tests in 154.02 seconds. The ledger reported zero violations, 5,241 product LOC, 4,247 test LOC, 478 tool LOC, 92 generated LOC, one process, one Python runtime, and the same five exact pins. The disposable trees were removed, no agent-created image remained mounted, and 83 GiB remained free."

  - id: S18
    title: Named-agent adapters
    env: any
    files: [adapters/ (generated maps + shims)]
    invariants: [Q76 acceptance (bidirectional golden traces per named client), Q31 acceptance (round-trip without loss, capability rejection not fabrication)]
    discovered_scope: "tests/test_s18_adapters.py is the single Q31/Q76 fixture. tools/genschema.py and schema/tables.py remain the one generated contract and field-map authority; research/S18_PROTOCOL_EVIDENCE.json is independent observed upstream evidence, not a runtime authority; tests/test_s03_schema.py admits the bounded Q31 extension namespace. adapters/__init__.py is the sole stateless L3 shim and imports only errors.py and schema/. S18 adds no dependency, process, runtime, on-disk object, numerical kernel, model-specific branch, or lifecycle authority."
    acceptance_boundary: "S18 proves structural bidirectional conformance and exact capability refusal for the five pinned named-client contracts. Codex uses Cassette as an OpenAI Responses provider; S18 neither uses nor emulates Codex app-server, and Q76 reopens if that conditional integration is added. OpenClaw Gateway v4 maps the exact chat.send request and chat-event subset; reasoning, tool, usage, and full-error events absent from that exact subset terminate as unsupported instead of becoming invented Gateway events. The row ends at translation: it does not open a listener or claim the live client-by-execution-row campaign assigned to L04 after callable revisions exist. The adapter cannot schedule, load, train, publish, or mutate a model; the canonical broker and store remain authoritative."
    expected_size: large
    done_when: full suite + ledger green
    depends: [S17]
    status: DONE 2026-08-10 — implementation d7052aa53568d671d1f488b60e1a6296c3778f17, hostile-wire hardening 2e96354568ab809a69153c0842aef1d6efc5ef52, and protocol-evidence/Gateway-v4 remediation 589be7cf42fa3484b2342935c38d6c3e29fcdf28; final-closeout CPython 3.13 macOS suite 34/34 in 114.05 seconds; ledger clean at 5,846 product LOC, 4,594 test LOC, 498 tool LOC, 95 generated LOC, five exact dependencies, one process, and one Python runtime
    closeout:
      - clause: "Q76 pins one explicit discovery and request/event surface for Codex, Ollama, OpenClaw, Hermes, and custom clients"
        test_or_probe: "the independent observed pin, source-digest, route, field-status, discovery-sidecar, alias, and server-contract assertions in tests/test_s18_adapters.py and research/S18_PROTOCOL_EVIDENCE.json"
        input: "Construct one Q31 capability profile for each adapter. Compare generated maps with the independently recorded upstream commits and routes: OpenAI Responses 9c8e1216bdaee0b020d1253ab7cc03a32eb36efe; Ollama a836eb8c3cc21a30020aadc70a1cc06012a4ef01; OpenClaw 810c3510ee6102e7a263553f871a11233708e275; Hermes a98aee47cecddab9ab9f58fc3a3b94b25f78d394; and canonical Cassette Q31 v1. Re-fetch and SHA-256 ten complete source files at those commits. Remove or stale the sidecar, change a native model ID, duplicate one model authority in encoder input and in a forged decoder sidecar, put provider authority inside that sidecar, name an absent model in an extension, alter an Ollama /api/show request, omit the OpenClaw alias, and omit the Hermes server contract."
        expected: "Round-trip discovery only when native rows, exact generated field/surface statuses, and canonical profiles agree. Reject native names as proof of capability, duplicate model authority in either direction, sidecar-owned provider fields, unmapped extension models, stale maps, an implicit OpenClaw agent, or raw Hermes weights presented as a server contract."
        observed: "All five valid profiles returned exactly equal canonical JSON records. A direct probe against d7052aa reproduced an accepted forged sidecar containing two profiles for revision:model-a; 2e96354 moved uniqueness into one validator used by both directions, and the same probe now returns CAPABILITY_MISMATCH. Every recorded source digest reproduced from its exact upstream commit. Every other hostile discovery change also terminated with CAPABILITY_MISMATCH or INVALID_REQUEST before acceptance. Ollama emitted and verified /api/tags plus one /api/show request; OpenClaw discovery resolved revision:model-a only through openclaw/main while Gateway requests derived the exact raw main agentId; Hermes required server_contract=True."
      - clause: "Q31 canonical requests round-trip without field loss, while unsupported semantics are rejected rather than fabricated"
        test_or_probe: "the default and alternate-route request traces plus hostile extension, blocked-field, credential, exact-JSON, and collision injections in tests/test_s18_adapters.py"
        input: "Round-trip canonical text, context, generation, reasoning, tools, structured output, streaming, and provider-only body/header fields through Responses, Ollama chat/generate, OpenClaw responses/chat/Gateway, Hermes responses/chat/agent, and custom JSONL. Then inject unsupported reasoning, structured output, context, tools, seed, and stop semantics; collide provider fields with mapped fields; supply another provider namespace, a credential header, case-duplicate headers, CRLF and NUL header values, and non-JSON bytes."
        expected: "Preserve every exact canonical field and every safe provider-only field under the selected extension namespace. Treat HTTP header names case-insensitively, reject ambiguous or unsafe fields, strip inbound credentials, refuse outbound credentials, and return CAPABILITY_MISMATCH for any non-exact semantic instead of translating it approximately."
        observed: "Every valid request returned exactly to its input, including empty and nonempty provider fields. OpenClaw's HTTP agent alias, Gateway raw agentId, required Gateway idempotency mirror and session key, Ollama's think/format/options fields, Responses reasoning/schema fields, and each alternate route matched the pinned golden. Every unsupported or hostile input was refused with the canonical typed error; no credential entered a canonical record, and case-colliding or control-bearing headers did not cross the boundary."
      - clause: "Q76 ordered streaming, errors, and terminal state transitions survive every named event wire"
        test_or_probe: "the seven-event full traces, OpenClaw HTTP six-event traces, exact Gateway chat-event subset, cancellation/failure traces, malformed event containers, reordered frames, duplicate sequence, unknown selector, and terminal-transition checks in tests/test_s18_adapters.py"
        input: "Encode and decode started, reasoning_delta where exact, output_delta, tool_call, tool_result, usage, and completed events with fixed run IDs and contiguous sequences. For Gateway v4, encode only started/status, output/delta, completed/final, and cancelled/aborted with the required session key; refuse reasoning, tools, usage, and full failure rather than inventing session.* events. Repeat cancelled and failed terminal traces where exact, preserve one provider-only frame field, submit None/dict/string/tuple containers, duplicate a sequence, change one run ID, append an event after completion, reorder provider frames, provide an unknown selector, and encode duplicate JSON members inside a provider tool argument."
        expected: "Preserve IDs, order, payloads, provider residue, and terminal states exactly; reject a gap, duplicate, foreign run ID, event after a terminal, ambiguous selector, duplicate JSON member, or unsupported reasoning event before treating the stream as canonical."
        observed: "Codex, Ollama, Hermes, custom, OpenClaw Responses/chat, and the exact OpenClaw Gateway chat-event subset round-tripped their complete supported traces. Cancellation and typed failure survived for all five adapters through an exact surface; Gateway cancellation survived through chat/aborted while its unsupported event semantics terminated with CAPABILITY_MISMATCH. Every malformed event container returned INVALID_REQUEST. Separate sequence, run-ID, post-terminal, reorder, selector, duplicate-JSON, and unsupported-event attacks also terminated before acceptance."
      - clause: "Q6 cancellation, status, and training retain exact operation identity and action semantics"
        test_or_probe: "the native-control, Q6-extension, custom-JSONL, route-identity, action, target, and argument assertions in tests/test_s18_adapters.py"
        input: "Round-trip one cancel request, one failed status record, and one training request through every adapter. Use native Responses /v1/responses/{run_id}/cancel and Hermes /v1/runs/{run_id}/stop only with empty arguments; use Q6 records for Ollama/OpenClaw cancellation and every non-custom status/training path; use canonical JSONL for custom. Change the status route, exchange train and cancel operations, remove cancellation and training targets, add unsupported native arguments, and place ../ in a route ID."
        expected: "Retain the idempotency key, target, operation, status, progress, and typed failure. Reject the wrong action, absent target, route disagreement, unsafe route ID, or lossy native argument before dispatch."
        observed: "Every valid operation returned exactly to its canonical record and every path matched its declared route, including a lowercase HTTP spelling of Idempotency-Key on native decode. A first hostile campaign exposed that custom JSONL decode checked schema shape but not action-specific operation and target semantics; adapters/__init__.py now enforces both. Missing-target encoder and decoder mutations fail independently, and all malformed operations return INVALID_REQUEST or CAPABILITY_MISMATCH."
      - clause: "Generated authority, refusal guards, and the declared S18 gate are independently load-bearing"
        test_or_probe: "twenty-four one-at-a-time disposable mutations; tests/test_s03_schema.py; the complete committed macOS suite; tools/ledger.py; git diff, mount, temporary-path, and system-volume checks"
        input: "Independently disable or corrupt exact-feature refusal, the Hermes server-contract guard, OpenClaw aliasing, provider-residue preservation, sequence continuity, run identity, terminal finality, blocked-wire refusal, discovery identity reconciliation, duplicate capability authority, sidecar extension ownership, operation-route identity, credential refusal, case-duplicate and control-bearing header refusal, Ollama show reconciliation, the model codec, operation-target encoding, custom JSONL target decoding, duplicate-JSON refusal, native header case handling, field status, surface status, and custom action semantics. Regenerate all schemas and maps, then execute the complete repository gate from commit 2e96354568ab809a69153c0842aef1d6efc5ef52."
        expected: "Every weakened guard fails its owning fixture. Generated files reproduce from their one authority. The accepted commit passes the full suite and accounting gate without a surviving mutation tree, agent-created mount, dependency, process, runtime, numerical kernel, model branch, or duplicate authority."
        observed: "All twenty-four mutants failed independently. The first target mutation initially survived because native route validation still rejected an empty run ID; expanding the injection to targetless training exposed the missing proof, and a separate custom-decode mutation exposed the first product defect. The closeout audit then reproduced the forged-sidecar defect against d7052aa and added independent run-ID, terminal, JSON, header, status-map, and action attacks before 2e96354. The final committed tree passed 34/34 tests in 95.54 seconds. The ledger reported zero violations, 5,815 product LOC, 4,537 test LOC, 495 tool LOC, 95 generated LOC, five exact pins, one process, and one Python runtime. Both disposable mutation trees were moved to Trash, no agent-created image remained mounted, and 81 GiB remained free."
      - clause: "The S18 review remediation is evidence-linked, shape-closed, and independently load-bearing"
        test_or_probe: "exact upstream SHA-256 replay; direct malformed-container probes; five one-at-a-time disposable mutations; tests/test_s03_schema.py; tests/test_s18_adapters.py; the complete CPython 3.13 macOS suite; tools/ledger.py; git diff, mount, temporary-path, and system-volume checks"
        input: "Fetch all ten recorded upstream files at their four exact commits and compare complete SHA-256 digests. Remove the encoder list guard, decoder list guard, required Gateway session-field guard, mirrored-idempotency equality guard, and generated-map/evidence pin agreement separately. Exercise None, object, string, and tuple event containers in both canonical directions; alter a Gateway request ID; omit its session key; and submit every unsupported Gateway event semantic."
        expected: "Every source byte digest reproduces. Every malformed container returns INVALID_REQUEST. Every weakened guard fails the Q31/Q76 fixture. OpenClaw Gateway emits only pinned chat.send and chat-event fields, while Codex remains explicitly on the Responses-provider branch of Q76. The accepted tree passes the full suite and ledger without a new dependency, process, runtime, numerical kernel, model-specific branch, surviving mutation tree, or mounted image."
        observed: "All ten upstream source digests reproduced. Both direct event directions rejected all four malformed container shapes with INVALID_REQUEST. All five mutants failed independently after one discarded harness run was found to be importing the accepted checkout instead of the disposable copy. Gateway v4 emitted the required mirrored idempotency key, raw main agentId, session key, and status/delta/final/aborted chat states; every absent semantic was refused. The accepted remediation commit 589be7c passed 34/34 tests in 102.92 seconds; the final closeout tree passed 34/34 again in 114.05 seconds. The ledger reported zero violations, 5,846 product LOC, 4,594 test LOC, 498 tool LOC, 95 generated LOC, five exact pins, one process, and one Python runtime. No disposable tree or mounted image remained, and 79 GiB remained free."

  - id: S19
    title: Streaming compiler, contribution map, and mathematical certificate
    env: macos
    files: [compiler.py, broker.py, store.py]
    discovered_scope: "store.py is modified because it remains the sole writer of source roots, content segments, indexes, derived roots, and generation dependencies; it now supplies descriptor-bound SafeTensors adoption, APFS copy-on-write conversion extents, durable derived roots, and Darwin physical-extent measurement. tests/compiler_fixture.py and tests/test_s19_compiler.py are the single small-dense S19 evidence surface, and tests/test_s16_broker.py replaces its retired caller-function seam with the production compiler binding. tests/test_s01_ledger.py replaces compiler.py and trainer.py as disposable hostile fixture names because compiler.py became governed production source in this row and trainer.py remains reserved by the queue. compiler.py remains the sole compiler authority above 800 physical lines because containment, source inventory, Q19 proof emission, Q58 reconciliation, plan construction, and candidate derivation share one publication decision; splitting them would create proof plumbing or duplicate authority. No dependency, process, runtime, model-family branch, generated contract, on-disk object type, or executable numerical runtime is added. S19 proves the declared small-dense boundary; S24 owns deterministic fixture-source discovery, tuple expansion, and complete machine replay, while L03 owns representative real-model execution after S28."
    invariants: [Q4 acceptance (peak-extent instrumentation, interruption, resume), Q5 production preparation binding (the canonical broker invokes compiler-owned plan and prepare operations through durable store objects rather than accepting an arbitrary caller-supplied revision producer), Q19/Q40 acceptance (derive immutable condition metrics, atom witnesses, service faces, cover, observation contract, descriptions/residuals, execution-risk and composition certificate from canonical inputs), Q30 source-driven tuple inventory (discover required tensor dtypes, operator signatures, shapes, and parameters from verified model material; expand only generated dispatch data or terminate with UNSUPPORTED_OPERATOR without fallback), Q55 executable-material containment (reject malicious pickle, templates, path traversal, auto-map/custom-code declarations, native libraries, and custom operators before code execution, network access, credential access, or unsafe loading), Q58 acceptance (total source-to-atom/description/residual map, structural failure on omission or detached certificate relation), Q60 resume on small dense model, Q51/Q60 source-consumption boundary (recompute each immutable source object's authoritative whole digest on the same reads used by compilation and reject changed completed extents before candidate-root publication), Q62 publication guard (verify canonical pages, mathematical certificate, and candidate root before generation publication)]
    acceptance_boundary: "PartialState and its mutable chunk records locate resumable work but do not authorize present bytes. S19 is the first consumer of attacker-controlled model material as executable structure, so it owns Q55 containment before any parser, loader, compiler action, network request, credential lookup, or store transform can honor that material. compiler.py contains no dynamic execution or FFI; its store.py dependency binds the platform fclonefileat primitive, but that primitive receives only verified, store-controlled descriptors and no hostile model field can select a library, symbol, path, or call shape. It inventories the model's required Q30 tuples from verified source evidence; an absent tuple is a typed refusal, not a private kernel or silent fallback. Compilation hashes each complete source object while consuming it, compares the result with immutable Q1/Q9 evidence before publication, and emits no root when the extent changed after transfer completion. This is not a separate post-completion transfer reread: the compiler hashes the bytes it must already read. S19 also closes S16's explicit F1 seam: the production broker must dispatch planning and preparation to compiler.py through committed store objects, and no public caller may supply an arbitrary function that authors a candidate revision. After canonical publication, Q62 owns at-rest verification."
    expected_size: large
    done_when: full suite + ledger green
    depends: [S05, S06, S10, S12, S16]
    historical_status: "DONE 2026-08-10 — implementation 3e3c9dc72c0fe6409efa315cb2f7e0d510e0c50c and governed-source fixture remediation b01afb71b0386d59e564f1748d3d87c38048ad03; the complete pinned CPython 3.13 macOS suite passed 35/35 in 88.50 seconds; the ledger reported zero violations at 6,909 product LOC, 4,872 test LOC, 498 tool LOC, 95 generated LOC, five exact dependencies, one process, and one Python runtime"
    status: "DONE 2026-08-11 — review remediation ee15bd4994bddb5939d116325ec11d81367e9ea8 replaces copied pager arithmetic with independent forward elimination, Bareiss determinants, direct contraction, and explicit residual evaluation; proof lock 482208a9170e575a8664f6bf714f4e00a77185e7 makes any return to structurally copied helpers fail the S19 fixture; impossible negative witness loss now returns CAPABILITY_MISMATCH; compiler.verify_bundle_structure names its structural boundary; store.py appears in the S19 file manifest; the complete pinned CPython 3.13 macOS suite passed 35/35 in 59.88 seconds and the ledger reported zero violations at 6,918 product LOC, 4,937 test LOC, 498 tool LOC, 95 generated LOC, five exact dependencies, one process, and one Python runtime"
    closeout:
      - clause: "Q55 containment and Q30 tuple admission precede executable interpretation"
        test_or_probe: "the hostile artifact, manifest, generated-tuple, static-import, and broker-context attacks in tests/test_s19_compiler.py"
        input: "Present pickle and native-library suffixes, path traversal, auto-map declarations, an executable template, a custom operator, and a generated operator case with a changed shape. Inspect compiler.py for dynamic execution and network-capable imports, and inspect AcquisitionContext for caller-supplied preparation authority."
        expected: "Reject executable material with CONTAINMENT_REJECTED and absent generated tuples with UNSUPPORTED_OPERATOR before a root, segment, code execution, network request, or credential lookup exists. Keep the broker context limited to its adapter, reservation, store extents, and cartridge."
        observed: "Every hostile artifact or declaration returned the declared typed error before roots or segments existed; the template marker was never created. compiler.py contains no eval, exec, compile, dynamic import, subprocess, socket, pickle, ctypes, or URL client, and AcquisitionContext has exactly four fixed fields with no caller plan or prepare function."
      - clause: "Q4 measures identity, shrink, grow, interruption, and resume without a second complete parameter checkpoint"
        test_or_probe: "the production stage_conversion_extent and F_LOG2PHYS_EXT traces in tests/test_s19_compiler.py"
        input: "Apply identity, shrink, and page-bounded grow transforms to a real APFS file; leave an invalid interrupted grow extent; repeat each completed transform; replace the source pathname after planning while retaining the exact descriptor; and inspect logical and physical ranges for the source and candidate segment."
        expected: "Adopt the exact descriptor through APFS copy-on-write, never a pathname or hard link; resume to exact immutable bytes; retain different inodes with shared physical blocks; and keep measured allocated peak at or below max(source,target) plus one canonical page and declared integrity material."
        observed: "All three transforms produced their exact target digest and repeated idempotently. The interrupted pending extent repaired, pathname substitution could not alter adopted bytes, source mutation after clone could not alter the candidate, and F_LOG2PHYS_EXT reported shared blocks with an allocated peak inside the declared equation."
      - clause: "Q51 present-byte authority is earned on the same complete reads that create canonical source pages"
        test_or_probe: "the post-plan byte mutation and descriptor-substitution attacks in tests/test_s19_compiler.py"
        input: "Plan from a completed transfer, change its final source byte, then prepare. Separately rename and replace the visible pathname after planning while leaving the verified source descriptor open."
        expected: "Reject changed completed bytes with SOURCE_REVISION_CHANGED before candidate-root publication. Consume the original descriptor rather than reopening a caller-controlled path."
        observed: "The changed extent emitted SOURCE_REVISION_CHANGED with no root or generation. The replacement pathname was ignored; the adopted segment matched the descriptor-bound source, remained a distinct copy-on-write inode, and passed complete page verification."
      - clause: "Q19 and Q40 derive one immutable mathematical certificate from canonical target and evidence bytes"
        test_or_probe: "the exact small-dense certificate derivation, structurally distinct pager recomputation, literal answers, combinatorial minors oracle, impossible-loss injection, and 800-matrix exact arithmetic sweep in tests/test_s19_compiler.py and the S19 remediation record"
        input: "Decode the canonical source tensor and derive its complete Q19/Q40 proof through compiler.py. Recompute admission through pager.py using different multiplication, division, elimination, determinant, contraction, and loss procedures. Judge both paths against literal inner-product and witness-loss answers plus permutation determinants and minor ranks; submit a metric that yields the impossible loss -1/3; and normalize the six helper syntax trees to detect copied algorithms."
        expected: "Bind every derived claim into the certificate ID, executable plan, transform manifest, and child identity. Require two structurally distinct arithmetic paths to agree with external exact oracles before generation. Reject a negative recomputed loss with CAPABILITY_MISMATCH, and fail the fixture if either path is copied into the other."
        observed: "Compiler derivation retained Gauss-Jordan elimination and closed-form loss; pager admission now uses forward elimination, Bareiss determinant evaluation, direct contraction, and explicit residual norms. Both matched literal values and combinatorial oracles across the fixture and an additional 800 exact random matrices. Both rejected the -1/3 witness with CAPABILITY_MISMATCH, all six normalized helper shapes differed, and pager admission reproduced the certificate and exact one-step schedule."
      - clause: "Q58 accounts for every source artifact, tensor, semantic asset, operator, and certificate relation"
        test_or_probe: "the two-shard artifact-preimage attack plus omission, duplication, mis-map, reachability, detached-relation, semantic-asset, and operator attacks in tests/test_s19_compiler.py"
        input: "Compile two independently identified SafeTensors shards, swap their tensor-to-artifact assignments, duplicate one assignment, then forge otherwise immutable candidate roots that omit or duplicate tensors, mis-map a tensor, remove atom reachability, detach a residual relation, or omit one semantic asset or operator."
        expected: "Recompute the Q1 tensor-index preimage and the complete Q58 map from the canonical source root; reject every structurally valid but semantically incomplete or detached candidate before activation."
        observed: "Artifact swaps and duplicates disagreed with the Q1 tensor-index digest. Every total-map attack returned CAPABILITY_MISMATCH or ROOT_INVALID, and no generation existed after any refusal."
      - clause: "Q5 and Q62 make the canonical broker the sole compiler caller and block false or corrupt candidates before publication"
        test_or_probe: "the production S16 replay and the forged-certificate, corrupt-page, corrupt-index, and corrupt-root attacks in tests/test_s16_broker.py and tests/test_s19_compiler.py"
        input: "Run every S16 acquisition phase through compiler.plan_revision and compiler.prepare_revision. Then forge a schema-valid candidate whose condition-metric digest is mathematically false, and separately corrupt its page payload, index, and root bytes."
        expected: "Permit no arbitrary revision producer. Recompute certificate truth through pager.py and verify all candidate bytes through store.py before commit_generation; reject every false or corrupt candidate with a canonical typed error and no generation."
        observed: "The production broker completed its durable phase replay without caller functions. compiler.verify_bundle_structure accepted the deliberately schema-valid false claim as structural, but CanonicalBroker rejected it through independent pager recomputation. Page corruption returned PAGE_CORRUPT; index and root corruption returned ROOT_INVALID; none published."
      - clause: "Q60 resumes deterministic small-dense compilation from incomplete content without exposing a partial root"
        test_or_probe: "the source-root, source-index, candidate-root, candidate-index, deleted-segment, and pending-root replay cases in tests/test_s19_compiler.py plus the durable S16 phase replay"
        input: "Truncate each content-addressed metadata object, delete the adopted segment, leave a stale pending root, and repeat preparation from the same immutable plan and source descriptor."
        expected: "Rehash or replace incomplete objects, recreate only missing content, return the exact candidate root, and leave generation absent until the broker completes its separately journaled durable publication."
        observed: "Every replay returned the identical PreparedRevision and restored exact bytes. The stale pending root disappeared, the deleted segment returned from the verified descriptor, and recover_generation remained empty throughout direct compilation."
      - clause: "The declared S19 gate passes without widening Cassette's runtime or dependency surface"
        test_or_probe: "the complete pinned CPython 3.13 macOS suite, tools/ledger.py, git diff checking, mount inspection, and system-volume inspection"
        input: "Execute every repository invariant after the production compiler binding and inspect accounting, generated integrity, mounts, and disk capacity."
        expected: "Pass the full suite and ledger with no skip, generated drift, dependency, process, runtime, model branch, duplicate authority, surviving mounted image, or undeclared J increase."
        observed: "The first committed-tree rerun exposed that S01's hostile-source fixture still used compiler.py as a disposable future filename; b01afb71b0386d59e564f1748d3d87c38048ad03 replaced both future-reserved names. Review then exposed copied certificate arithmetic and an impossible negative loss accepted by pager.py; ee15bd4994bddb5939d116325ec11d81367e9ea8 and 482208a9170e575a8664f6bf714f4e00a77185e7 repaired and protected the independent gate. The final committed remediation tree passed 35/35 in 59.88 seconds. The ledger reported zero violations, 6,918 product LOC, 4,937 test LOC, 498 tool LOC, 95 generated LOC, five exact dependencies, one process, and one Python runtime. No Cassette image remained mounted, and 80 GiB remained free."

  - id: S20
    title: Certified hardware plans
    env: any
    files: [compiler.py, store.py, tools/genschema.py, schema/ (generated)]
    discovered_scope: "store.py changes because it remains the sole root and fixed-record page-index writer: derive_root admits an exact same-identity plan-manifest replacement while preserving the selected root's verified physical index, and page_index_byte_count exposes the private index encoding's verified byte cost without letting compiler.py open cartridge paths. tools/genschema.py and schema/ provide the one generated Q33 authority for persisted hardware plans and catalogs; tests/test_s03_schema.py admits those contracts into the exact generated set, while tests/test_s20_hardware_plans.py is the single Q11/Q33/Q59 executable evidence surface and reuses the established nonzero-fresh Q19 fixture from tests/test_s13_pager.py. compiler.py remains the sole compiler authority above 800 physical lines because certificate specialization, page grouping, plan sealing, profile admission, and selection form one publication decision; splitting them would add plan plumbing or a second plan authority. No dependency, process, runtime, numerical kernel, model-family branch, on-disk object type, or copied weight form is added."
    invariants: [Q11/Q59 acceptance (plan switch over one certificate, zero weight payload in plans, exact description/metadata/fresh-traffic budgets), Q33 acceptance (generated bounded hardware-plan and catalog contracts reject malformed or collapsed data before semantic reconstruction)]
    acceptance_boundary: "S20 stores one replaceable hardware-plan catalog beside the immutable S19 preparation bundle. The catalog is covered by root integrity but excluded from the executable transform identity, so adding, deleting, or replacing physical policy changes the root manifest without changing the executable identity, tensor map, page payloads, precision contribution, or physical index. Every persisted catalog and plan must first pass its generated bounded Q33 contract; compiler.py then independently regenerates the plan from its certificate, canonical pages, and physical index. Every plan references the complete unique page set of this compiled revision; a later optional precision omission requires its own revision-quality evidence under Q59. Selection validates one measured profile against its recorded Q42 evidence reference and minimum envelope, then minimizes the recomputed I/O latency bound among matching plans. S20 proves this policy over the recorded Q39 classes; it does not claim that a fixture profile is a live Q42 device qualification or that PHASE LIVE has run."
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S19]
    historical_status: "DONE 2026-08-11 — step commit b8c63c834a6b2caeac6a9e85f1ae1c14bbcc953f attaches sealed metadata-only hardware catalogs to same-identity executable roots, preserves repacked physical page mappings, derives all mathematical budgets from one Q19 certificate, rejects false coalescing and copied weights, bounds plans plus indexes, and selects the minimum predicted-latency plan whose measured envelope passes; the complete pinned CPython 3.13 macOS suite passed 37/37 in 59.27 seconds and the ledger reported zero violations at 7,299 product LOC, 5,277 test LOC, 570 tool LOC, 106 generated LOC, five exact dependencies, one process, and one Python runtime"
    status: "DONE 2026-08-11 — remediation commit 3f08ab62e99069583b32e0cca167c8d9ff884827 gives persisted hardware plans and catalogs exact generated Q33 contracts, validates their bounded shape before semantic reconstruction, preserves the attacked root's selected physical index, and makes removal of the catalog-binding guard fail its owning assertion; the complete pinned CPython 3.13 macOS suite passed 37/37 in 82.40 seconds and the ledger reported zero violations at 7,306 product LOC, 5,291 test LOC, 577 tool LOC, 108 generated LOC, five exact dependencies, one process, and one Python runtime"
    closeout:
      - clause: "Q33 gives every persisted hardware plan and catalog one generated bounded contract before semantic reconstruction"
        test_or_probe: "tests/test_s03_schema.py generated-contract fixtures plus tests/test_s20_hardware_plans.py::test_q11_q33_q59_certified_hardware_plans_switch_without_weight_duplication"
        input: "Generate and round-trip a complete hardware plan and catalog; remove a required budget, set weight_payload_bytes to one, and replace a catalog plan with opaque text. Then load accepted S20 catalogs through compiler.py."
        expected: "Emit deterministic exact schemas with no open object, unbounded array, unbounded string, or unbounded number; reject malformed persisted data as ROOT_INVALID before certificate, page, or budget reconstruction; retain semantic regeneration as the separate truth check."
        observed: "The generated set now contains hardware_plan.json and hardware_plan_catalog.json. The schema fixture rejected every malformed shape and bound; compiler.py validated generated records on creation and refused malformed persisted catalogs before semantic regeneration."
      - clause: "Q11 selects the expected plan across every recorded Q39 Apple/storage class and rejects an unmatched measured envelope"
        test_or_probe: "tests/test_s20_hardware_plans.py::test_q11_q33_q59_certified_hardware_plans_switch_without_weight_duplication plus the exact closeout replay"
        input: "Present C1/S1, C2/S2, and C3/S3 inference profiles at their plan floors; present two C1/S1 plans with different contiguous grouping and queue depth; then reduce C1 sustained bandwidth by one byte per second below its predicate."
        expected: "Select the sole class-matching plan, choose the lower predicted-total-latency plan when two qualify, and return CAPABILITY_MISMATCH with recompile direction when none qualifies."
        observed: "C1, C2, and C3 selected c1-air-32, c2-max-128, and c3-ultra-512 at recomputed bounds of 22,777,248 ns, 9,388,624 ns, and 4,694,312 ns. The two-plan C1 replay selected c1-air-32-coalesced. One byte per second below the C1 bandwidth floor returned CAPABILITY_MISMATCH."
      - clause: "Q59 adds, deletes, and switches plans without changing executable identity, tensor capacity, page payloads, or the selected physical index"
        test_or_probe: "the one-plan, three-plan, two-plan, reversed-input, pre-repacked-index, and segment snapshot cases in tests/test_s20_hardware_plans.py"
        input: "Reverse-repack the compiled root, snapshot every segment inode, size, modification time, and digest, then derive sibling catalogs containing one, three, and two plans; rebuild the three-plan catalog from reversed specification order."
        expected: "Produce distinct plan-root manifests with one executable identity and byte-exact tensor and physical-page mappings; write no segment; make specification order irrelevant."
        observed: "The one-, three-, and two-plan roots were blake3:dceeda01ceb5183b63e351b2e55d1a090056a224a8ed7a9964409bfeccc23136, blake3:73dde1446537f4c684f1fd6db6f8008e53d6e7b85d692b0aa20637c88df7359d, and blake3:0ba834475493bfe02df59f808ce250afa3a27e0c9d690a99026cdf454868d3b8. All retained executable identity blake3:c11e71f42610f8ca47b9ae78fd2ac7d1e31b6017de2f826db5ece1b22ff753aa and the repacked index; every segment tuple remained byte-identical. Reversing specification order reproduced the same three-plan root."
      - clause: "Every plan contains references and schedules only; copied parameter authority is structurally impossible"
        test_or_probe: "the hostile specification and resealed persisted-plan attacks in tests/test_s20_hardware_plans.py"
        input: "Add a weight_payload field carrying text to a plan specification; separately change a persisted plan's weight_payload_bytes from zero to one and reseal both plan and catalog IDs."
        expected: "Reject the extra payload field as INVALID_REQUEST and the resealed nonzero payload claim as ROOT_INVALID at the generated contract before selection."
        observed: "The specification was shape-refused with INVALID_REQUEST. The generated persisted-plan contract rejected the fully resealed nonzero weight_payload_bytes claim as ROOT_INVALID. Every accepted plan records weight_payload_bytes=0."
      - clause: "Description, metadata, fresh sampling, physical reads, execution error, risk, and horizon remain exact Q19 certificate specializations"
        test_or_probe: "the exact S19 certificate case, the nonzero-fresh S13 certificate reuse, and six independently resealed field attacks in tests/test_s20_hardware_plans.py"
        input: "Generate plans from the exact certificate and the established fresh certificate; then alter description total, metadata total, fresh traffic total, predicted total latency, memory-schedule description peak, and weight payload independently, resealing both identity layers each time."
        expected: "Emit literal certificate values for exact and fresh paths and reject every internally resealed divergence through independent catalog regeneration."
        observed: "The exact path emitted description 16/16 bytes, metadata 256/256 bytes, and zero fresh samples, traffic, pages, bytes, and latency. The fresh path emitted description 1,024/3,072 bytes, metadata 256/768 bytes, samples 3/9, scalar traffic 9/27, physical bytes 4,096/12,288, page reads 1/3, and 3,000 ns certified total latency. Five shape-valid resealed divergences returned CAPABILITY_MISMATCH; the copied-weight divergence returned ROOT_INVALID at the generated contract."
      - clause: "Physical read groups and plan metadata are executable, bounded claims rather than decorative labels"
        test_or_probe: "the reversed-range, 128-plan overflow, metadata accounting, and five one-at-a-time guard-removal mutations"
        input: "Reverse two pages inside one claimed read group while keeping the group/order partition self-consistent; submit 128 otherwise valid plans; then independently remove the metadata cap, bandwidth predicate, latency minimization, certificate-derived description budget, and catalog-to-certificate regeneration check in disposable trees."
        expected: "Reject a noncontiguous range, reject plans or plans-plus-index above min(1 percent of executable bytes, 4 GiB), and make every removed guard fail the fixture."
        observed: "False coalescing returned CAPABILITY_MISMATCH. The accepted three-plan root used 9,054 plan-metadata bytes and 24,392 total plans-plus-index bytes under an 83,886-byte allowance; 128 plans returned CAPACITY_EXCEEDED. The repaired forged-catalog case preserved the selected physical index; removing only the catalog-to-certificate check then admitted a false 17-byte description budget and failed its owning assertion. Every guard-removal mutation failed, and each disposable tree was moved to Trash."
      - clause: "The declared S20 gate passes without widening Cassette's numerical or runtime surface"
        test_or_probe: "the complete pinned CPython 3.13 macOS suite, tools/ledger.py, diff checking, process inspection, mount inspection, and system-volume inspection"
        input: "Execute every repository invariant after certified hardware-plan attachment and inspect accounting, generated integrity, running test environments, mounted cartridge images, and free space."
        expected: "Pass the complete suite and ledger with no skip, generated drift, dependency, process, runtime, numerical kernel, model branch, duplicate authority, surviving test process, or mounted image."
        observed: "The original pre-commit tree passed 37/37 tests in 59.27 seconds, with zero ledger violations at 7,299 product LOC, 5,277 test LOC, 570 tool LOC, and 106 generated LOC. The final Q33 and fixture remediation worktree passed 37/37 in 162.41 seconds; the ledger again reported zero violations, now at 7,306 product LOC, 5,291 test LOC, 577 tool LOC, and 108 generated LOC, with the same five exact pins, one process, and one Python runtime."

  - id: S21
    title: Trainer - paged Tier A and compiled-certificate Tier B
    env: macos
    files: [trainer.py]
    invariants: [Q21/Q70 Tier-A operations on frozen cartridge pages, Q21/Q70 Tier-B recovery operations over immutable condition/atom/description/estimator/observation/precision calibration records, Q22 immutable work branch and exact ordered child composition while parent readers remain pinned, Q23 placement trace, Q24 paged BF16/FP32 delta training over a frozen quantized base with no hidden full master, Q25 interrupt/resume bit-exact, Q71 acceptance (tensor lifetime trace), Q72 acceptance (paged vs unpaged equivalence), Q73 child commit; Tier-B output is a committed training artifact consumed through store and broker, never a trainer-owned certificate]
    expected_size: large
    done_when: full suite + ledger green
    depends: [S15, S06, S20]
    status: DONE 2026-08-12 — step commit 32e241fa4174cfc905c7f7e68d9e97fb0f257217; complete arm64 macOS suite 40/40 in 65.34 seconds; ledger clean at 8,133 product LOC, 5,750 test LOC, 577 tool LOC, 108 generated LOC, five exact dependencies, one process, and one Python runtime
    discovered_scope: "store.py changes because it remains the sole writer of staged training pages, immutable work roots, certificate-recovery deltas, and generation transactions; no trainer opens cartridge paths. tools/genschema.py and schema/tables.py add data-only Q30 rank-one-adapter and scalar-certificate-recovery autograd signatures, pager.py dispatches those signatures only through existing MLX primitives, and tests/test_s12_pager.py executes them against literal independent gradients while rejecting authored arithmetic in every reachable executor. tests/test_s21_trainer.py is split into the Q21/Q24/Q70 operation fixture, the Q22/Q25/Q73 hostile durable-checkpoint fixture, and the Q23/Q71/Q72 lifetime-and-oracle fixture. tests/compiler_fixture.py admits one optional tensor tuple so the existing compiler path can produce an I8 certified parent without a second compiler fixture. AGENTS.md records trainer.py in the Q78 removal map. trainer.py remains the sole training authority above 800 physical lines because operation admission, durable restart state, page-window execution, adapter or certificate-recovery updates, trace validation, and child publication share one checkpoint state machine; splitting them would create trainer plumbing or a second training authority. No dependency, process, runtime, authored numerical kernel, model-family branch, protocol, or on-disk writer is added."
    acceptance_boundary: "S21 executes two real F1 primitives. Tier A dequantizes one explicitly recorded I8 codec, keeps the frozen parent tensor live through a rank-one MLX adapter loss, and updates BF16 or FP32 adapter state through supervised, continuation, or pairwise-preference evidence. SFT and continued pretraining intentionally share the generated mean-squared-error primitive; their contract distinction is the durable instruction-response or causal-continuation evidence role, not a second numerical loss. Tier B keeps the same parent tensor live while six distinct condition, atom, description, estimator, observation, and precision records each update their own committed recovery tensor; it does not disguise those outputs as adapter pages or claim that the recovered artifact is itself a validated Q19 certificate. Independent unpaged oracles reproduce both child forms. S25 owns deterministic fixture-scale integration and its Q70 accounting; L03 owns representative real-model scale-out after S28. Neither may replace this frozen-parent, durable-state, operation-semantics, or hostile-checkpoint contract."
    closeout:
      - clause: "Q21/Q24/Q70 Tier-A SFT, continued pretraining, and DPO update BF16 or FP32 adapters over a frozen quantized parent"
        test_or_probe: "tests/test_s21_trainer.py::test_q21_q24_q70_all_advertised_operations_use_their_declared_training_evidence"
        input: "Train FP32 and BF16 SFT, FP32 causal continuation, and FP32 pairwise DPO over two explicit I8 parent windows; change only parent bytes or codec scale; inject an implicit codec, unsupported full-weight operation, unsupported delta precision, and NaN evidence."
        expected: "Each admitted operation commits its declared generated loss and optimizer cases without a master page; the base, codec, operation, precision, and evidence affect the child; every unsupported tuple refuses before cartridge mutation."
        observed: "All four admitted paths committed ordered rank-one adapter deltas with no master pages. Parent-byte and scale changes changed the output, SFT/continuation/DPO remained semantically distinct, and every unsupported or non-finite input returned TRAINING_UNSUPPORTED or INVALID_REQUEST without changing source bytes."
      - clause: "Q21/Q70 Tier-B recovery consumes immutable condition, atom, description, estimator, observation, and precision calibration records through store and broker"
        test_or_probe: "tests/test_s21_trainer.py::test_q21_q24_q70_all_advertised_operations_use_their_declared_training_evidence"
        input: "Dispatch COMPILED_RECOVERY through CanonicalBroker against one Q19-bearing compiled parent with six 32,768-sample calibration records; change only the condition loss, then omit the precision record."
        expected: "Commit six certificate-recovery tensors whose values depend on their records, preserve the parent certificate digest, expose the child through the canonical store/broker result, refuse an incomplete record set, and never label the artifact as a Q19 certificate or adapter."
        observed: "The broker returned SUCCEEDED at the committed child boundary; six recovery tensors matched the independent oracle and changed with condition loss, all calibration records round-tripped, the incomplete set returned TRAINING_UNSUPPORTED, and the artifact contained no certificate object or adapter rank/scale."
      - clause: "Q22 immutable work branch and exact ordered child composition while parent readers remain pinned"
        test_or_probe: "tests/test_s21_trainer.py::test_q22_q25_q73_hostile_checkpoints_never_replace_the_frozen_parent"
        input: "Pin the parent before preparation, complete and commit a child in separate cartridge copies, compare every parent page and root afterward, inspect child parent/base identity, and roll the generation pointer back."
        expected: "Preparation and work writes never move or mutate the callable parent; the child names the exact parent and ordered delta base; rollback restores the original root without rewriting it."
        observed: "The parent pin, root, and every page remained byte-identical; both child copies were identical and named the parent identity; rollback selected the original root."
      - clause: "Q25 interruption and resume are bit-exact for every advertised S21 operation"
        test_or_probe: "tests/test_s21_trainer.py::test_q22_q25_q73_hostile_checkpoints_never_replace_the_frozen_parent using _kill_before_checkpoint_root"
        input: "Send SIGKILL at the staged-page/checkpoint-root boundary during BF16 SFT, FP32 continued pretraining, FP32 DPO, and compiled recovery, then restart each job from its last durable checkpoint."
        expected: "Each resumed checkpoint, transaction coordinate, committed result, and loaded training artifact equals its uninterrupted control exactly."
        observed: "All four interrupted operations reproduced the uninterrupted checkpoint and immutable child; optimizer step, data cursor, and random seed remained exact."
      - clause: "Q23/Q71 persistent state stays on the cartridge and every unified-memory tensor has one bounded live interval"
        test_or_probe: "tests/test_s21_trainer.py::test_q23_q71_q72_trace_and_unpaged_oracle_cover_every_live_tensor_window"
        input: "Replay each ordered LOAD, PRODUCE, PERSIST, and RETIRE event for every parameter and step; recompute logical and MLX peaks; search every cartridge object for the scratch host path."
        expected: "Only live tensors occupy UM, every child persists to D before its base retires, no tensor remains live after the step, measured peak stays within the declared window, and no internal or scratch path enters durable state."
        observed: "Every trace replayed with an empty terminal live set, exact parameter order and peaks, base-before-gradient and persist-before-retire ordering, bounded MLX windows, and no scratch path in any cartridge object."
      - clause: "Q72 paged updates equal an independently derived unpaged update"
        test_or_probe: "tests/test_s21_trainer.py::test_q23_q71_q72_trace_and_unpaged_oracle_cover_every_live_tensor_window plus tests/test_s12_pager.py generated-autograd literals"
        input: "Compare paged MLX SFT, continued-pretraining, DPO, BF16, FP32, and six-kind recovery outputs against pure-Python chain-rule or scalar-recovery oracles; inspect every reachable executor for authored numerical arithmetic."
        expected: "FP32 results agree within 1e-6, BF16 results agree bit-exactly, every recovery tensor agrees independently, and MLX arithmetic remains confined to generated Q30 dispatch."
        observed: "Every output met its stated tolerance, generated literal gradients passed, and the executor inspection found no unadmitted authored numerical kernel."
      - clause: "Q73 publishes one complete immutable child and hostile durable state never becomes callable"
        test_or_probe: "tests/test_s21_trainer.py::test_q22_q25_q73_hostile_checkpoints_never_replace_the_frozen_parent"
        input: "Reseal checkpoints with a hidden master, cursor drift, missing trace, over-limit peak, foreign delta/base tuple, substituted codec, non-finite delta, or wrong arity; also force numerical overflow and a one-byte memory window."
        expected: "Reject each candidate with one canonical typed error before pointer mutation; leave the parent generation callable; publish only a completely verified child."
        observed: "Every hostile candidate returned GRADIENT_INVALID, MEMORY_BUDGET_EXCEEDED, ROOT_INVALID, or TRAINING_UNSUPPORTED as appropriate, every generation remained pinned to the parent, and admitted controls published one complete child."
      - clause: "Q21 generated operation semantics have one executable dispatch authority"
        test_or_probe: "disposable-tree P8 guard-removal mutation against tests/test_s21_trainer.py"
        input: "Force the executed DPO loss-case lookup to the valid MSE dispatch row while preserving the persisted DPO operation declaration and pairwise numerical branch."
        expected: "The repaired fixture rejects the valid-but-wrong generated row through the independent expected-loss contract."
        observed: "Before repair all three S21 tests passed under the mutation; after repair all three failed with UNSUPPORTED_OPERATOR at generated autograd parameter validation."
      - clause: "S21 done_when"
        test_or_probe: "complete pinned CPython 3.13 arm64 macOS suite, tools/ledger.py, git diff check, process inspection, mount inspection, and system-volume inspection after Entry 65"
        input: "Execute every reachable repository invariant after the final generated-case repair and attributed Build Story append."
        expected: "No test failure or skip, generated drift, dependency violation, second process/runtime, authored numerical kernel, model branch, duplicate authority, surviving test process, mounted cartridge image, or low-space condition."
        observed: "40/40 tests passed in 65.34 seconds; ledger violations were empty at 8,133 product, 5,750 test, 577 tool, and 108 generated LOC; diff check was clean, no test process or cartridge mount remained, and the system data volume retained 77 GiB free."

  - id: S22
    title: Trainer - metering and admission
    env: any
    files: [trainer.py]
    invariants: [Q28 acceptance (projected vs metered writes on simulated profiles), Q74 acceptance (injection fixtures - low space, endurance, estimate drift)]
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S21]
    status: DONE 2026-08-13 — step commit b4f0cac34da265d5f049248eba2cdffc2556e060; complete arm64 macOS suite 42/42 in 173.03 seconds; ledger clean at 8,511 product LOC, 5,960 test LOC, 577 tool LOC, 108 generated LOC, five exact dependencies, one process, and one Python runtime
    acceptance_boundary: "S22 implements generic preflight, reservation, and per-checkpoint metering against recorded storage-class evidence, then executes Q28/Q74 with simulated cache-exhausted profiles on every platform. It does not claim a physical drive measurement: L01 qualifies real assembled storage paths, and L04 executes the accepted training rows against those profiles."
    discovered_scope: "tests/test_s22_trainer.py is the single env:any Q28/Q74 fixture; tests/test_s21_trainer.py routes the existing MLX training paths through the now-mandatory admission and observation contract. trainer.py remains the sole training authority above 800 physical lines because request derivation, resource admission, durable metering, checkpoint execution, and publication share one state machine. S22 reuses store.py's Q53 reservation and release authority and adds no writer, dependency, process, runtime, generated contract, numerical kernel, model-family branch, or protocol."
    closeout:
      - clause: "Q28 derives one exact write, duration, memory, and capacity estimate before reservation"
        test_or_probe: "tests/test_s22_trainer.py::test_q28_projected_and_metered_writes_share_one_exact_endurance_envelope"
        input: "Independently sum dataset, candidate, optimizer, master, and journal bytes; apply the measured 3/2 write-amplification ratio; admit exactly at both endurance ceilings; add one byte to an odd logical projection; reserve against the complete Q53 phase maximum plus operating-system safety."
        expected: "Reproduce every estimate field, round physical writes upward, admit equality, and reserve one exact extent only after every resource check passes."
        observed: "The fixture derived 1,984 MiB of logical writes and 2,976 MiB at p95, admitted equality at 80 percent lifetime endurance and 20 percent of remaining endurance, rounded the odd projection upward, and made one reservation for the exact phase requirement plus 8 GiB safety."
      - clause: "Q28/Q74 refuse every independent preflight resource contradiction before reservation or cartridge mutation"
        test_or_probe: "tests/test_s22_trainer.py::test_q74_injections_refuse_before_start_or_at_one_recoverable_boundary"
        input: "Inject low or zero allocatable space, absent endurance or health evidence, a 32,767-byte candidate below the 32,768-byte raw update floor, lifetime writes one byte beyond declared endurance, isolated lifetime and remaining-endurance overruns, checked-sum overflow, malformed identity, excess memory, insufficient storage, thermal saturation, impossible duration, missing measurements, and absent required power."
        expected: "Return the canonical typed refusal for the first broken condition, call no allocator, and preserve an unmutated cartridge boundary."
        observed: "Every injection returned CAPACITY_EXCEEDED, ENDURANCE_EXCEEDED, INVALID_REQUEST, MEMORY_BUDGET_EXCEEDED, CAPABILITY_MISMATCH, THERMAL_LIMIT, or OPERATION_CANCELLED as declared, with zero reservation calls. The exhausted-device case named its specific preflight diagnosis instead of passing through a later generic endurance refusal."
      - clause: "The durable Q28 meter accounts for its own manifest and both live and reloaded counters remain beneath one admission"
        test_or_probe: "the real scratch-cartridge checkpoint, live counter attacks, and independently forged durable manifests in tests/test_s22_trainer.py"
        input: "Create one admitted SFT work root, sum every newly written objective, delta, and state page independently, add the final canonical manifest length, and compare that total with the stored logical meter. Then exceed logical writes or reads by one byte first through assess_training_observation and separately inside a reloaded manifest."
        expected: "Reach an exact self-consistent meter fixed point; reject live telemetry and persisted evidence independently when either exceeds the admitted complete-job estimate."
        observed: "The durable logical counter equalled the independently read material pages plus the canonical manifest byte length. Both live attacks returned ENDURANCE_EXCEEDED at the observation boundary, and both durable attacks returned ENDURANCE_EXCEEDED at manifest validation. The two enforcement sites remain because they guard distinct trust boundaries."
      - clause: "Q74 cumulative observations cannot move backward and each recoverable or terminal runtime boundary remains typed"
        test_or_probe: "the four one-field decrement sequences and runtime injection table in tests/test_s22_trainer.py"
        input: "Advance one accepted observation, then decrease logical writes, reads, physical writes, or elapsed time independently while every other field increases. Separately inject thermal throttle or stop, write throttle or stop, slow storage, p95 drift, completion drift, power loss, skipped checkpoints, forged admission evidence, and a released reservation."
        expected: "Reject every decreasing or detached record, distinguish retryable from terminal limits, and permit no write after release or before the next exact checkpoint."
        observed: "Each isolated decrement returned INVALID_REQUEST for the monotonicity invariant. Runtime limits returned their declared code and retryability, power loss remained recoverable, forged or released admission failed, and skipped checkpoint two was refused."
      - clause: "Every S22 admission and meter guard is load-bearing under hostile removal"
        test_or_probe: "twelve disposable-tree mutations against tests/test_s22_trainer.py, including one assertion-derived control"
        input: "Drop one projection term as the control, then independently bypass manifest fixed-point convergence, each of four monotonic counters, live estimate enforcement, durable estimate enforcement, the raw update floor, exhausted endurance, the 80-percent lifetime ceiling, and the one-fifth remaining-endurance ceiling."
        expected: "The control and every targeted guard removal fail an owning S22 assertion without collection, syntax, import, or platform failure."
        observed: "All twelve mutations were killed. The first exhausted-endurance mutation initially survived because a later guard returned the same error code; requiring the exact early diagnosis killed the repaired mutation and proved guard order rather than generic failure. Every disposable tree was deleted after its result."
      - clause: "S22 done_when"
        test_or_probe: "complete pinned CPython 3.13 arm64 macOS suite, tools/ledger.py, diff checking, mutation cleanup, mount inspection, process inspection, and system-volume inspection"
        input: "Execute every reachable invariant after the complete S22 proof, then inspect accounting, generated integrity, remaining test environments, mounted cartridge images, and free space."
        expected: "Pass the full suite and ledger with no skip, generated drift, dependency, process, runtime, numerical kernel, model branch, duplicate authority, surviving disposable tree, mounted image, or low-space condition."
        observed: "The step tree passed 42/42 tests in 173.03 seconds. The ledger reported zero violations at 8,511 product LOC, 5,960 test LOC, 577 tool LOC, and 108 generated LOC, with five exact pins, one process, and one Python runtime. No mutation tree remained, and the system data volume retained 80 GiB free."

  - id: S23
    title: Failure-row generator and shared-authority preflight
    env: any
    files: [sources.py, tests/test_s23_failure_rows.py]
    invariants: [the exact failure_rows 8-operation by 16-injection coordinate set and six assertions are generated from research/ACCEPTANCE_MATRIX.yaml; Q49 shared removable-volume lifecycle behavior is exercised across the matrix labels and read/write access classes; shared capacity, integrity, source, gradient-validation, and broker failures preserve the exact callable root; every caller-visible broker event equals the independently recovered durable event frontier; S26 retains the complete matrix through eight concrete operation entrypoints]
    acceptance_boundary: "S23 generates all 128 failure-row coordinates and executes the machine-observable preflight supplied by the shared lifecycle, capacity, integrity, source, trainer-validation, and broker authorities. An operation name in this fixture selects a broker kind, an access label, or a read/write class; it does not prove that acquisition, compilation, prefill, decode, training, export, repair, or removal reached its concrete product entrypoint. S24 completes the missing fixture operations, including export and exact revision removal. S26 then replays all 128 coordinates and six assertions through the eight concrete entrypoints. S23 uses one generated deterministic model fixture on a scratch cartridge and loopback source evidence only. Physical USB-C detach and reattach, a copied replacement on actual media, host sleep with active external I/O, bus reset, port migration, an actual read-only external remount, live-source revision drift, and real-drive exhaustion remain L04 manifestations after S28."
    discovered_scope: "tests/test_s23_failure_rows.py parses the bounded matrix authority without a YAML dependency and independently fixes its expected eight operations, sixteen injections, and six assertions. Review proved that fourteen injection executors converged on shared authorities and that export and removal lacked product entrypoints, so the prior concrete-operation claim was false even though all 128 parameterized cases ran. The repaired fixture names that boundary and replaces payload-key scanning with an exact comparison between caller-visible events and the canonical events independently recovered from the durable broker record. The existing stale-handle proof remains: every lifecycle outcome sets stale_attempted and records the typed refusal. The first S23 run also exposed one sources.py classification defect: pwrite ENOSPC, EDQUOT, and EFBIG were reported as CARTRIDGE_DISCONNECTED. sources.py returns CAPACITY_EXCEEDED for those capacity causes and retains CARTRIDGE_DISCONNECTED for unavailable-handle causes. No model-specific branch, numerical kernel, dependency, runtime, writer, protocol, or physical-hardware input was added."
    expected_size: medium
    done_when: full suite + ledger green; concrete operation-entrypoint obligations assigned to S24 and S26; non-simulable physical manifestations enumerated for PHASE LIVE
    depends: [S10, S18, S20, S22]
    historical_status: DONE 2026-08-14 — step commit 94daccaaa71ce2f1257b201c385581afd80cd7a8 and close commit 8af6635aa9ecb4b1323b3cc46ae6c95efb2fadd8; later hostile review proved that 128 parameterized cases had been misreported as 128 concrete operation executions and that no_uncommitted_token inspected payload key names instead of a commit frontier
    status: DONE 2026-08-14 — repair step commit 7e7ca861b161105bbdb0bb03a9c453e009223eea; the complete arm64 macOS suite passed 170/170 in 81.36 seconds; the ledger remained clean at 8,514 product LOC, 6,365 test LOC, 577 tool LOC, and 108 generated LOC; the durable-frontier mutant failed its owning row and the stale-refusal mutant failed all 56 lifecycle rows; S24 owns fixture export and exact revision removal, and S26 owns the complete concrete-operation matrix
    closeout:
      - clause: "The failure_rows authority generates one complete, unique operation-by-injection coordinate set"
        test_or_probe: "tests/test_s23_failure_rows.py::test_q49_failure_rows_generate_complete_matrix_and_execute_shared_authorities"
        input: "Read failure_rows directly from research/ACCEPTANCE_MATRIX.yaml, compare its bounded fields with an independent literal contract, and expand operations by injections with itertools.product."
        expected: "Retain required=true, the exact eight operations, sixteen injections, six assertions, and 128 unique coordinates; no handwritten subset or silent unknown injection may pass collection. Do not infer concrete operation execution from coordinate generation."
        observed: "The fixture generated all 128 coordinates and fixed the complete matrix independently. Its test name, module description, and queue boundary now identify the executed behavior as a shared-authority preflight rather than eight concrete product paths."
      - clause: "Q49 invalidates every old shared-authority access and restores only a completely revalidated identity"
        test_or_probe: "the seven lifecycle injections across every generated operation row in tests/test_s23_failure_rows.py"
        input: "Create one lifecycle access carrying each matrix operation label and its declared read/write class; inject disconnect, verified cloned replacement under the same logical identity, wrong-identity reconnect, sleep/wake, bus reset, port migration, and a read-only remount through the filesystem-profile boundary."
        expected: "Set stale_attempted on every invalidation and refuse the old access with CARTRIDGE_DISCONNECTED; admit a different filesystem UUID only through explicit replacement of the exact four-part logical root; refuse an ordinary wrong-filesystem reconnect; admit read-class access but reject write-class access on read-only media."
        observed: "All 56 shared lifecycle rows set stale_attempted=true and stale_refused=true. Exact copied identity, wrong identity, and read-only access behavior matched the shared Q49 authority. A mutation that replaced the typed stale-access resolution with INVALID_REQUEST failed all 56 lifecycle rows at no_stale_handle_use. Concrete operation entrypoints remain S26 evidence."
      - clause: "Every shared machine-simulable failure preflight preserves exact content and emits its declared typed result"
        test_or_probe: "the process-death, capacity, corruption, source-revision, gradient, and cancellation injections in tests/test_s23_failure_rows.py plus the directly coupled S10 transfer fixture"
        input: "Terminate a real broker subprocess after its durable started, running, and successful-terminal records; refuse capacity before allocation; write one partial byte and raise ENOSPC; corrupt one page, index, or root; change the loopback source validator inside transfer_artifact; decode a NaN gradient page; and cancel a live broker worker."
        expected: "At each shared authority, recover the exact durable record, return OPERATION_CANCELLED, CAPACITY_EXCEEDED, PAGE_CORRUPT, ROOT_INVALID, SOURCE_REVISION_CHANGED, or GRADIENT_INVALID, preserve the canonical root byte-for-byte, publish no partial generation, and create no internal model file."
        observed: "The shared preflight returned each declared typed result and preserved the exact root. The first ENOSPC run had returned CARTRIDGE_DISCONNECTED; the existing cause-specific sources.py repair remains correct. No result is described as concrete operation execution."
      - clause: "Caller-visible broker output cannot advance beyond its durable commit frontier"
        test_or_probe: "the independent operation-log reader and hostile visible-only output event inside tests/test_s23_failure_rows.py::test_q49_failure_rows_generate_complete_matrix_and_execute_shared_authorities"
        input: "After process death and cooperative cancellation, compare every caller-visible event with the event sequence independently decoded, canonicalized, and re-digested from the broker's committed record. Then append a visible-only output_delta whose payload uses the previously unrecognized key output."
        expected: "The exact committed and visible sequences agree for valid work. The visible-only event fails regardless of its payload key. S26 separately binds inference output delivery to the concrete pager decode commit."
        observed: "The exact frontiers agreed. The hostile output event failed because it had no durable counterpart; no token, text, content, output, or other payload-name list participates in the decision. Replacing the frontier assertion with a no-op made that hostile event survive and failed its owning acquisition/process-death row."
      - clause: "The complete concrete-operation matrix remains open at its executable owner"
        test_or_probe: "S23, S24, and S26 acceptance boundaries reconciled with Q6, Q49, and failure_rows"
        input: "Trace acquisition, compilation, prefill, decode, training, export, repair, and removal to their product entrypoints and identify every operation absent at S23."
        expected: "Do not claim concrete matrix execution from labels. Require S24 to implement fixture export and exact revision removal, then require S26 to run all eight entrypoints against all sixteen injections and six assertions."
        observed: "Export and revision removal were absent, and fourteen S23 injection executors converged on shared authorities. S24 now owns both missing operations. S26 now rejects name-only dispatch and owns the complete 128-row operation integration."
      - clause: "Only physical manifestations remain for PHASE LIVE"
        test_or_probe: "S23 acceptance boundary reconciled with L04 remaining failure_rows"
        input: "Separate machine-observable state and byte behavior from events that require a selected physical cartridge or live source."
        expected: "Retain after S28 the actual USB-C detach and same/wrong-volume reattach rows, host sleep with active external I/O, USB bus reset, physical port migration, actual external read-only remount, live-source revision drift, and real-drive exhaustion after reservation."
        observed: "Those physical and live-source manifestations remain assigned to L04. S23 claims only fixture-observable shared behavior, and no physical event is claimed from a scratch directory, profile boundary, or loopback server."
      - clause: "S23 done_when"
        test_or_probe: "complete pinned CPython 3.13 arm64 macOS suite, tools/ledger.py, git diff checking, process inspection, mount inspection, temporary-fixture cleanup, and system-volume inspection"
        input: "Run every reachable repository invariant after the matrix-boundary and durable-frontier repair, then inspect structural accounting and residual environments."
        expected: "Pass the full suite and ledger without skip, generated drift, dependency, process, runtime, numerical-kernel, model-branch, duplicate-authority, surviving test process, mounted Cassette image, retained S23 temporary tree, or low-space condition."
        observed: "170/170 tests passed in 81.36 seconds. The ledger reported zero violations at 8,514 product LOC, 6,365 test LOC, 577 tool LOC, and 108 generated LOC, with five exact dependencies, one process, and one Python runtime. No test process or Cassette image remained, every S23 pytest or mutation tree created by the repair was deleted, and the system data volume retained 78 GiB free."

  - id: S24
    title: Machine interoperability, revision removal, delta acquisition, and protected fixture capture
    env: macos
    files: [sources.py, store.py, compiler.py, trainer.py, broker.py, adapters/__init__.py, tools/ (analysis, generated), AGENTS.md]
    invariants: [Q26 acceptance (every tuned fixture child is callable through every declared adapter; stream each representable SafeTensors, adapter, or GGUF form on the scratch cartridge; re-import and pass Q10/Q17; reject any target that loses graph, tokenizer, operator, precision, or ordered-delta semantics), Q57 acceptance remainder (consume S05's verified ordered deltas and export eligible forms without a second parameter authority), Q54 acceptance (apply valid, wrong-base, corrupt, interrupted, and ancestry-fork fixture deltas; reuse only digest-identical content; publish only the exact verified target; retain the callable base on every refusal or rollback), Q6 revision-removal acceptance (require one exact immutable revision and independently recomputed reachability result; refuse the current, reachable, ambiguous, or malformed target; retain every governed byte on refusal; expose the operation through the canonical broker), Q40 immutable teacher trace capture from a deterministic generated dense fixture, Q18 protected condition/test-law construction including rare and off-support fixture cases, Q19 condition-metric and compatibility-certificate input generation, Q30 fixture-discovered operator/dtype/shape expansion through generated dispatch, Q51-to-Q58 fixture integration, Q5 broker-to-compiler replay without the S16 fixture seam]
    acceptance_boundary: "S24 completes every machine-side source, export, update, exact revision-removal, and interoperability operation against generated or checked-in deterministic fixture material on scratch cartridges. Removal is a Q6 operation over an exact immutable revision and one recomputed reachability result; it is not Q78 component deletion. S24 makes no live source request, downloads no model, touches no physical external drive, and makes no F4 quality or scale claim. L02 owns the first live acquisition and L03 owns the real 3-8B and 20-120B gates after S28."
    discovered_scope: "tests/test_s24_interoperability.py is the single arm64 macOS fixture joining Q51 acquisition, Q5 compilation replay, Q26 export and adapter calls, Q54 immutable updates, and Q6 revision removal. tools/capture_fixture.py authors the checked-in Q18/Q19/Q40 teacher corpus only through the generated Q30 MLX dispatch; its immutable corpus digest is blake3:6d5c088dc42b82f8b96e8c189ac39783c23b96e332b6bcb9de16ec0f9070d4bc. SafeTensors and GGUF full exports, portable adapter exports, and the eligible rank-one merged export stream on scratch cartridges; every derivative remains marked non-authoritative and carries separately bound source and artifact semantics. trainer.py exposes verified adapter material as data, pager.py alone executes the generated merge tuple, broker.py alone composes the operation, and store.py remains the sole writer of export, update, removal, and generation objects. AGENTS.md records that one-writer assignment and maps tools/capture_fixture.py to Q40. Tier-B certificate regeneration remains S25; the complete concrete eight-operation failure matrix remains S26; live sources, real models, and physical external media remain L02-L04 after S28."
    expected_size: large
    done_when: full suite + ledger green; fixture trace corpus committed by digest
    depends: [S10, S18, S19, S21, S22, S23]
    historical_status: DONE 2026-08-21 — step commit d8c1133b764dec837104176d1e9f486a6a42d907; complete arm64 macOS suite 172/172 in 117.75 seconds; ledger clean at 9,439 product LOC, 6,838 test LOC, 615 tool LOC, and 109 generated LOC, with five exact dependencies, one process, and one Python runtime; protected trace corpus committed at blake3:6d5c088dc42b82f8b96e8c189ac39783c23b96e332b6bcb9de16ec0f9070d4bc
    status: DONE 2026-08-23 — remediation commit 53d7e8bb5f3b80f57b718eac01ce0895abded9a8; complete arm64 macOS suite 172/172 in 136.76 seconds; ledger clean at 9,439 product LOC, 6,949 test LOC, 615 tool LOC, and 109 generated LOC, with five exact dependencies, one process, and one Python runtime; all ten disputed Q26/Q54 guards independently killed by removal; protected trace corpus retained at blake3:6d5c088dc42b82f8b96e8c189ac39783c23b96e332b6bcb9de16ec0f9070d4bc
    closeout:
      - clause: "Q18/Q19/Q30/Q40 protected fixture evidence is immutable, discriminating, and executable"
        test_or_probe: "tests/test_s24_interoperability.py::test_q18_q19_q30_q40_protected_teacher_trace_is_immutable_and_executable plus byte-identical tools/capture_fixture.py regeneration"
        input: "Capture common and rare generated dense conditions through the pinned MLX tuple, ablate one contribution, retain an explicit off-support decision, and independently attack the observation contract with ALLOW and a missing selector."
        expected: "Bind the corpus by digest, keep the common trace unchanged under the declared ablation, change the rare trace, exclude off-support input causally, and reject either hostile observation contract before publication."
        observed: "The checked-in corpus regenerated byte-for-byte at blake3:6d5c088dc42b82f8b96e8c189ac39783c23b96e332b6bcb9de16ec0f9070d4bc. Both hostile contracts failed before a generation became callable. The generated dispatch table gained the exact 3x2-by-2x2 fixture tuple and the rank-one I8-plus-F32 adapter merge tuple, each with an independent golden result."
      - clause: "Q5/Q26/Q51-Q58 source replay and derivative interchange preserve executable material and semantic authority"
        test_or_probe: "tests/test_s24_interoperability.py::test_q5_q6_q26_q51_q54_q57_q58_machine_interoperability_update_and_removal"
        input: "Run Hugging Face and Tinker fixture acquisition through Q51 and the canonical Q5 compiler path; complete Ollama acquisition to its current typed SafeTensors-only compiler boundary; export full SafeTensors and GGUF forms; copy only the export package; re-import it; remove tokenizer, operator, precision, or graph-plan evidence independently; and submit a one-byte-short reservation."
        expected: "Reach the same compiler through each source adapter, reject the currently unrepresentable compiler input without fabrication, stream only after exact admission, reproduce every tensor and Q17 teacher output, preserve the complete source semantic record, describe the standalone artifact honestly, and accept no semantic-loss export."
        observed: "Hugging Face and Tinker published verified compiled roots through one state machine. Ollama acquired its GGUF bytes and returned MODEL_UNSUPPORTED at the declared compiler boundary. Both full export forms re-imported from portable packages with exact tensors and teacher logits. Every semantic-loss attack returned ROOT_INVALID, the forged binding returned IDENTITY_MISMATCH, and the short reservation changed no cartridge byte."
      - clause: "Q26 tuned children remain callable and each eligible exchange form preserves its actual representation"
        test_or_probe: "the Tier-A/Tier-B adapter loop, portable adapter round trip, and merged SafeTensors/GGUF round trips in tests/test_s24_interoperability.py"
        input: "Call one Tier-A and one Tier-B child through every generated named adapter; export and re-import the Tier-A adapter; merge one direct rank-one adapter through the generated MLX tuple into both full targets; and request all three forms from the Tier-B recovery child."
        expected: "Each declared adapter reaches the exact immutable child and executes one real MLX result; adapter exchange reconstructs the exact child over its bound base; merged artifacts contain the independently expected F32 tensors while retaining source delta provenance outside the standalone artifact; an ineligible Tier-B form fails typed."
        observed: "Every named adapter dispatched both children and returned computed logits. Adapter re-import reconstructed the exact Tier-A root. SafeTensors and GGUF merged artifacts matched independently computed bytes, retained the source ordered delta in provenance, declared no delta inside the standalone merged artifact, and re-imported at float32-merged-adapter-v1. Tier-B exports returned MODEL_UNSUPPORTED without approximation."
      - clause: "Q54 publishes only an exact verified child while every invalid or incomplete delta leaves the base callable"
        test_or_probe: "the direct and canonical-broker revision-delta sequences in tests/test_s24_interoperability.py"
        input: "Apply a valid same-shape page delta, another base, corrupt changed bytes, an absent changed payload, an ancestry fork, and one byte less than the exact candidate-plus-publication reservation; then roll back the published child."
        expected: "Reuse only digest-identical page locations, stage no target under failed admission, publish only the reconstructed target through Q60/Q73, reject every invalid case with one canonical error, and restore the original generation without rewriting its root."
        observed: "The valid target alone published and matched its precomputed root and identity. Unchanged pages retained their exact physical locations. Wrong-base and fork cases returned DELTA_BASE_MISMATCH, corrupt bytes returned PAGE_CORRUPT, the absent payload returned SOURCE_UNAVAILABLE, and short admission returned CAPACITY_EXCEEDED without mutation. Rollback restored the exact base root."
      - clause: "Q6 exact revision removal recomputes reachability and removes only the proved unreachable storage closure"
        test_or_probe: "the current, reachable, malformed, ambiguous, forged, short-admission, repair-object, success, and retry cases in tests/test_s24_interoperability.py"
        input: "Request removal by exact root or identity across current, historical-reachable, ambiguous, malformed, and unreachable roots; forge a self-consistent-looking catalog digest; create Q62 repair primary, replica, root, index, and parity objects; and admit one byte below the exact tombstone demand."
        expected: "Recompute the catalog and generation ancestry, refuse every stale or non-unique proof without changing bytes, preserve shared segments and repair objects, durably tombstone one exact unreachable root, remove its unique index/segments/repair closure, and replay the broker result idempotently."
        observed: "Every refusal preserved an exact cartridge snapshot. The forged proof returned INVALID_REQUEST. Short admission wrote no tombstone. Successful removal deleted only the enumerated orphan root, index, unique segments, repair manifests, and unshared repair objects; the callable generation remained exact, and replay returned the same terminal broker result."
      - clause: "The S24 guards distinguish real contract proof from adjacent green results"
        test_or_probe: "four disposable-tree guard-removal mutations against tests/test_s24_interoperability.py"
        input: "Disable export semantic binding, bypass independent reachability comparison, omit Q62 repair objects from the removable closure, and introduce trainer-side numerical execution into adapter material extraction."
        expected: "Each mutation fails the assertion owned by the removed authority rather than through syntax, import, collection, or platform failure."
        observed: "All four mutations were killed: coherent graph-plan loss was accepted only when semantic binding vanished; forged reachability survived only when recomputation vanished; repair-path coverage failed when its closure was omitted; and the numerical-authority AST guard failed when trainer.py called its runtime. Every disposable tree was removed afterward."
      - clause: "S24 done_when"
        test_or_probe: "complete pinned CPython 3.13 arm64 macOS suite, tools/ledger.py, generated-schema reproduction, trace regeneration, diff checking, process inspection, mount inspection, temporary-fixture cleanup, and system-volume inspection"
        input: "Execute every reachable invariant after the final numerical-authority and portable-semantics corrections, then inspect accounting, generated output, immutable fixture output, residual environments, and storage pressure."
        expected: "Pass the full suite and ledger without skip, generated drift, trace drift, dependency, process, runtime, authored numerical kernel, model-family branch, duplicate authority, surviving test process, mounted Cassette image, retained mutation tree, or low-space condition."
        observed: "172/172 tests passed in 117.75 seconds. The ledger reported zero violations at 9,439 product LOC, 6,838 test LOC, 615 tool LOC, and 109 generated LOC, with five exact pins, one process, and one Python runtime. Generated schemas and the trace corpus reproduced exactly, diff checking was clean, no test process or Cassette image remained, all disposable S24 trees were deleted, and the system data volume retained 93 GiB free."
    remediation_closeout:
      - clause: "Q26 export refusal is proved at the target and portable-package boundaries"
        test_or_probe: "independent hostile export records plus ten isolated guard-removal mutations against tests/test_s24_interoperability.py"
        input: "Present GGUF with an otherwise valid unsupported U8 tensor or foreign operator; detach an adapter plan from its delta; forge a tuned source-history binding; make export mode disagree with ordered history; duplicate the selected delta; and replace an adapter page while coherently resealing artifact, plan, source, and export identities without calling store.py's private manifest builder."
        expected: "SafeTensors remains representable where declared; GGUF refuses unsupported precision or operators with MODEL_UNSUPPORTED; every detached or fabricated adapter package fails with the exact Q26 typed error before target mutation; removal of any governing refusal makes the fixture fail."
        observed: "The intact fixture refused every attack at its named boundary. Removing the operator, dtype, adapter-plan tuple, tuned-history, mode-history, exact-delta, or adapter-page guard independently made the owning assertion fail; no adjacent checksum failure was accepted as proof."
      - clause: "Q54 delta identity is proved from independent hostile material"
        test_or_probe: "the data-driven base_identity, delta_digest, and target_identity attacks in tests/test_s24_interoperability.py plus isolated removal of each corresponding store.py guard"
        input: "Change the declared base identity and reseal the delta; change only the declared delta digest; or change the target identity and reseal the delta while preserving valid payload bytes and a complete reservation."
        expected: "Return DELTA_BASE_MISMATCH, PAGE_CORRUPT, or IDENTITY_MISMATCH with the exact named cause, preserve the complete cartridge snapshot, and make the fixture fail if the corresponding refusal is removed."
        observed: "All three attacks returned the exact code and detail without mutation. Each isolated guard removal changed or eliminated that result and failed the fixture. The deliberate current-versus-reachable removal redundancy remained unchanged because either guard independently enforces Q6 rather than masking an unproved S24 clause."
      - clause: "S24 remediation done_when"
        test_or_probe: "complete pinned CPython 3.13 arm64 macOS suite, tools/ledger.py, fresh schema and protected-trace reproduction, diff checking, mount inspection, temporary cleanup, and system-volume inspection"
        input: "Run the complete repository after the Q26/Q54 proof repair and restore every mutation before inspection."
        expected: "Pass 172 reachable tests and the ledger with no product-code change, generated drift, trace drift, mounted Cassette image, retained mutation tree, or low-space condition."
        observed: "172/172 tests passed in 136.76 seconds. The ledger reported zero violations at 9,439 product LOC, 6,949 test LOC, 615 tool LOC, and 109 generated LOC. Generated schemas and the protected trace reproduced byte-identically; compiler.py and store.py matched the committed production implementation after every mutation; no Cassette image remained mounted; and the system data volume retained more than 85 GiB free."

  - id: S25
    title: Machine invalidation, certified compile, and resource-frontier replay
    env: macos
    files: [compiler.py, tools/ (simulator, generated)]
    invariants: [Q27/Q61/Q75 acceptance (mutate each fixture weight, condition metric, atom, cover, observation, description, residual estimator, composition, precision, tokenizer, template, context, and operator dependency independently; recompute the exact transitive closure; compare incremental output with a clean full compile; preserve the callable parent), one Q19-certified deterministic fixture revision built end-to-end; every protected fixture condition covered or causally excluded; exact and fresh-stochastic paths replay under their declared contracts; Q70 Tier-A fixture training completes; Q70 Tier-B recovery consumes S21's committed calibration artifacts, regenerates every invalidated witness, publishes one Q73 child, and matches a clean certificate derivation; Q37 mathematical-resource curves emitted against simulated recorded storage-class profiles]
    acceptance_boundary: "S25 proves machine algorithms, dependency closure, and resource accounting on deterministic fixture material only. It does not download or evaluate a real model and does not claim F4 or F5 promotion. L03 executes those gates after S28."
    discovered_scope: "tests/test_s25_invalidation.py is the single arm64 macOS fixture for Q19/Q27/Q37/Q61/Q70/Q73/Q75. tools/resource_frontier.py emits the deterministic prediction-only Q37 cross-product, tools/generated/s25_resource_curves.json records it, and AGENTS.md maps that tool to Q37 under Q78. The implementation reuses unchanged store.py, trainer.py, pager.py, S21 training artifacts, S24 protected traces, and generated Q30 dispatch; it adds no live source, physical-storage path, numerical kernel, process, runtime, or dependency."
    expected_size: large
    done_when: full suite + ledger green; curves committed
    depends: [S20, S21, S24]
    status: DONE 2026-08-23 — step commit a7bf58d9b354b3e2d858386edfdb422278e38847; complete arm64 macOS suite 175/175 in 163.19 seconds; ledger clean at 9,792 product LOC, 7,182 test LOC, 690 tool LOC, and 109 generated LOC, with five exact dependencies, one process, and one Python runtime; 13 dependency classes plus 11 additional complete-input mutations matched exact closures and clean roots; prediction-only Q37 curves committed at blake3:8bd508e3a7ca8e6cdf584c8186ef83a0821651eccd642e5d4a5a4ddac9ff0baf
    closeout:
      - clause: "Q27/Q61/Q75 exact transitive invalidation, unchanged-input reuse, clean equivalence, and callable-parent preservation"
        test_or_probe: "tests/test_s25_invalidation.py::test_q19_q27_q61_q75_each_input_has_one_exact_incremental_closure_and_clean_root"
        input: "Compile and commit one S25 Q19 revision, then independently change weights, condition metric, atom, cover, observation, description, residual estimator, composition, precision, tokenizer, template, context, and operator. Separately change condition provenance, excluded-condition evidence, description contract, sampling-law work unit, operation bound, format version, architecture, config digest, processor digest, physical conversion, and prior-failure digest."
        expected: "Compute changed hashes before authorship; author only the exact topological closure; carry prior records only when their complete dependency vectors remain exact; make incremental root, plan, and derivation equal a clean compile; leave the committed parent current and byte-identical."
        observed: "Every primary mutation reported its one named axis. Exact invalidation sets were: weights={page_stats,page_layout,condition_metrics,compatibility_witnesses,atom_cover,description_distortion,residual_metadata,estimator_calibration,precision_calibration,composition_proof,kernel_plan,physical_schedule,quality_proof,protocol_capabilities,cache_key}; condition_metric={condition_metrics,compatibility_witnesses,atom_cover,description_distortion,residual_metadata,estimator_calibration,precision_calibration,composition_proof,kernel_plan,physical_schedule,quality_proof,protocol_capabilities,cache_key}; atom={compatibility_witnesses,atom_cover,description_distortion,residual_metadata,estimator_calibration,precision_calibration,composition_proof,kernel_plan,physical_schedule,quality_proof,protocol_capabilities,cache_key}; cover={observation_contract,atom_cover,composition_proof,kernel_plan,physical_schedule,quality_proof,protocol_capabilities,cache_key}; observation={protected_trace_corpus,observation_contract,condition_metrics,compatibility_witnesses,atom_cover,description_distortion,residual_metadata,estimator_calibration,precision_calibration,composition_proof,kernel_plan,physical_schedule,quality_proof,protocol_capabilities,cache_key}; description={description_distortion,residual_metadata,estimator_calibration,precision_calibration,composition_proof,kernel_plan,physical_schedule,quality_proof,protocol_capabilities,cache_key}; residual_estimator={residual_metadata,estimator_calibration,precision_calibration,composition_proof,kernel_plan,physical_schedule,quality_proof,protocol_capabilities,cache_key}; composition={protected_trace_corpus,observation_contract,condition_metrics,compatibility_witnesses,atom_cover,description_distortion,residual_metadata,estimator_calibration,precision_calibration,composition_proof,kernel_plan,physical_schedule,quality_proof,protocol_capabilities,cache_key}; precision={page_layout,semantic_manifest,description_distortion,residual_metadata,estimator_calibration,precision_calibration,composition_proof,kernel_plan,physical_schedule,quality_proof,protocol_capabilities,cache_key}; and tokenizer, template, context, or operator={protected_trace_corpus,semantic_manifest,observation_contract,condition_metrics,compatibility_witnesses,atom_cover,description_distortion,residual_metadata,estimator_calibration,precision_calibration,composition_proof,kernel_plan,physical_schedule,quality_proof,protocol_capabilities,cache_key}. All 11 secondary mutations entered the intended single axis and its same exact closure. Every affected record changed, every unaffected record remained exact, every incremental candidate equaled its clean root, plan, and derivation, and the committed parent remained selected and unchanged."
      - clause: "One deterministic Q19 revision covers or causally excludes every protected fixture condition"
        test_or_probe: "the certificate assertions and independent persisted-bundle verification in tests/test_s25_invalidation.py::test_q19_q27_q61_q75_each_input_has_one_exact_incremental_closure_and_clean_root"
        input: "Compile the checked-in S24 teacher evidence for common, rare, and off-support conditions through the S25 derivation and verify the resulting candidate from source bytes."
        expected: "Cover common and rare with an exact atom; exclude off-support only with its immutable causal evidence; bind the execution plan to the independently recomputed derivation."
        observed: "The certificate cover was exactly [{atom_id: atom, condition_id: common},{atom_id: atom, condition_id: rare}]. Off-support was excluded as OFF_SUPPORT with the BLAKE3 digest of {decision: REJECT, reason: no immutable teacher trace}. Reload recomputed the certificate, complete input graph, artifact records, recovery binding, plan, and root before accepting the candidate."
      - clause: "Exact and fresh-stochastic compiled paths replay under their declared contracts"
        test_or_probe: "tests/test_s25_invalidation.py::test_q19_q20_q37_q64_exact_and_fresh_replay_emit_only_simulated_machine_curves"
        input: "Execute the generated mlx.matmul.f32.3x2_2x2 exact case twice over the protected trace, then execute the seeded fresh residual path twice for three steps with seed 7."
        expected: "The exact path reproduces the teacher logits with no fresh traffic; the fresh path reproduces identical ordered output digests and retains its declared samples and traffic."
        observed: "Both exact runs returned [[1,0],[2,0],[-1,0]], eta_rep=1.0, fresh_traffic_total=0. Both three-step fresh runs returned the same ordered digest tuple with fresh_samples_total=48 and fresh_traffic_total=144."
      - clause: "Q70 Tier-A fixture training completes as one immutable child"
        test_or_probe: "the Tier-A branch in tests/test_s25_invalidation.py::test_q70_q73_q75_tier_a_and_tier_b_recovery_publish_only_clean_certified_children"
        input: "Run S21's frozen ADAPTER_SFT fixture batches against the quantized fixture parent and commit through the existing training transaction."
        expected: "Complete Tier A, publish one child, and retain the exact parent identity."
        observed: "Training completed with tier=A and operation=ADAPTER_SFT. The selected root named the original quantized identity as its sole parent and remained loadable."
      - clause: "Q70 Tier-B recovery consumes committed calibration artifacts, regenerates every invalidated witness, matches clean derivation, and publishes one Q73 child"
        test_or_probe: "the Tier-B, hostile-calibration, clean-recompile, and explicit-publication branches in tests/test_s25_invalidation.py::test_q70_q73_q75_tier_a_and_tier_b_recovery_publish_only_clean_certified_children"
        input: "Commit condition, atom, description, estimator, observation, and precision calibration pages at 32,768 samples each plus their six ordered delta pages. First substitute a foreign condition output digest; then consume the valid training root against its exact compiled parent."
        expected: "Reject detached calibration before candidate use; on valid evidence change exactly six certificate inputs, regenerate their complete closure, carry only unaffected page statistics, equal a clean certificate derivation, preserve the callable parent until explicit commit, and publish one immutable Q73 child."
        observed: "The foreign output returned CAPABILITY_MISMATCH. Valid recovery changed exactly condition_metric, atom, observation, description, residual_estimator, and precision; regenerated all 17 artifacts except page_stats; retained page_stats byte-for-byte; matched the clean candidate root, plan, and derivation; left the training generation current until commit_generation; then selected the one recovered child while both training and compiled-parent roots remained loadable."
      - clause: "Q37 emits separate mathematical-resource and predicted physical-service curves against simulated recorded storage classes"
        test_or_probe: "tools/resource_frontier.py byte-for-byte regeneration plus tests/test_s25_invalidation.py::test_q19_q20_q37_q64_exact_and_fresh_replay_emit_only_simulated_machine_curves"
        input: "Cross two exact/fresh resource vectors with fixture, simulated-35g, and simulated-120g scales and simulated USB-C flash, USB-C SSD, and Thunderbolt SSD classes."
        expected: "Emit all atom, rank, description, metadata, fresh-sample, fresh-traffic, error, risk, horizon, page, model, context, working-set, loaded-byte, and physical-service dimensions without touching hardware or claiming F4/F5."
        observed: "The 13,814-byte artifact reproduced exactly at blake3:8bd508e3a7ca8e6cdf584c8186ef83a0821651eccd642e5d4a5a4ddac9ff0baf with 18 points and claim PREDICTION_ONLY_NO_F4_F5_OR_PHYSICAL_QUALIFICATION. The independently checked fixture/exact/USB-C-flash point had page_count=1, metadata_bytes_total=332, predicted_loaded_bytes=348, predicted_physical_service_ns=2677, and predicted_working_set_bytes=4444."
      - clause: "The S25 guards are consequential rather than decorative"
        test_or_probe: "six isolated working-tree mutations, each restored before the completion gate"
        input: "Remove the cover-to-observation dependency edge; force all artifact records to be reported recomputed; remove recovery output-digest binding; detach execution plans from derivation IDs; add one nanosecond to the resource formula; disable unchanged-record carry-forward."
        expected: "Each mutation fails its owning fixture or returns the exact typed closure error."
        observed: "The six mutations respectively produced CAPABILITY_MISMATCH for observation_contract, failed the exact recomputed-artifact assertion, allowed the hostile calibration and failed its refusal assertion, made bundle verification reject the detached plan, failed byte-identical curve reproduction, and returned CAPABILITY_MISMATCH because artifact authorship no longer equaled the Q27 closure. All six guards were restored."
      - clause: "S25 done_when and machine-only boundary"
        test_or_probe: "complete pinned CPython 3.13 arm64 macOS suite, tools/ledger.py, generated-curve comparison, syntax compilation, diff checking, and system-volume inspection"
        input: "Run every reachable repository invariant after restoring all mutations; regenerate curves to standard output; inspect accounting, dependency, process, runtime, and free-space state."
        expected: "Pass the full suite and ledger; reproduce the committed curves; add no numerical kernel, process, runtime, dependency, model branch, live source, physical-drive access, F4 result, or F5 result."
        observed: "175/175 tests passed in 163.19 seconds. The ledger reported zero violations at 9,792 product LOC, 7,182 test LOC, 690 tool LOC, and 109 generated LOC, with five exact dependencies, one process, and one Python runtime. Curves reproduced byte-for-byte, diff checks were clean, and the system data volume retained 81 GiB free."
      - clause: "Post-close adversarial review of the Q27/Q61/Q75 refusal paths"
        test_or_probe: "three paired defect reproductions in clean archives of 7162acdd342a317938f02b422b308ab9289ebafb; each archive was discarded after the named S25 fixture ran"
        input: "Disable unchanged-record carry-forward; separately remove the cover-to-observation dependency edge; separately alter only an incremental candidate after its clean derivation. Distinguish those defect-plus-guard probes from deleting a guard while all inputs and derivations remain valid."
        expected: "A guarded inconsistency fails at the guard or an earlier independent verifier. A valid run need not enter a refusal branch, and the number of pytest.raises blocks is not an acceptance measure. No S25 obligation moves into S26 unless an S25 predicate remains unproved."
        observed: "Disabled carry-forward returned CAPABILITY_MISMATCH with 'artifact authorship differs from the exact Q27 dependency closure.' The missing dependency edge returned CAPABILITY_MISMATCH at the earlier clean bundle verifier for observation_contract, before a stale artifact could escape. The altered incremental candidate returned CAPABILITY_MISMATCH with 'incremental recompile differs from its clean full derivation.' The review's AGENTS.md scope claim was also false: S25's discovered_scope already names AGENTS.md, and the README change at 74e86f0 predates both S25 commits. No product or test defect reproduced, S25 remains DONE, and S26 retains only its declared integration obligations."

  - id: S26
    title: PHASE MACHINE integration gate
    env: macos
    files: [research/ACCEPTANCE_MATRIX.yaml, store.py, compiler.py, pager.py, trainer.py, tests/test_s21_trainer.py, tests/test_s23_failure_rows.py, tests/test_s25_invalidation.py, tests/test_s26_phase_machine.py, tests/test_s26_machine_gate.py, tests/fixtures/s26_machine_gate.json, tests/fixtures/s26_deferred_live_rows.json]
    invariants: [Q36 promotion readiness without promotion claim - every F0-F3 fixture invariant plus S24/S25 machine integration, Tier-A fixture training, Tier-B fixture recovery, independently recomputed Q19 certificate, invalidation closure, export/re-import, delta application, the complete failure_rows 8-operation by 16-injection by 6-assertion contract through concrete acquisition, compilation, prefill, decode, training, export, repair, and revision-removal entrypoints, and simulated resource accounting PASS; no operation coordinate may be satisfied only by a request label, idempotency key, lifecycle access label, or read/write class; no_uncommitted_token must compare delivered inference output with the pager's committed decode frontier; emit the exact real-model and hardware rows deferred to PHASE LIVE]
    acceptance_boundary: "S26 proves that the machine is internally complete and ready for live falsification. It reuses S23's generated coordinate authority but replaces its shared-authority preflight with each concrete operation's durable boundaries and failure behavior. It cannot emit F4 PASS, F5 PASS, frontier capability, physical-drive performance, or hosted-comparison claims because no real model, live source, or physical drive enters before S28."
    expected_size: medium
    done_when: machine gate outcome and deferred-live row manifest recorded; full suite + ledger green
    depends: [S25]
    discovered_scope: "S26's concrete integration replay exposed three seams rather than new components: CartridgeLifecycle invalidated its own access token, but pager instances retained a plain path across later prefill and decode calls; compilation wrote an unpublished candidate without consuming the shared Q53 reservation authority; and the v1 training trace included process-wide MLX allocation baselines in immutable child identity. store.py now supplies one lifecycle-bound path object and one exact capacity-demand check, pager.py re-resolves lifecycle binding before every page acquisition, compiler.py reserves its declared candidate phase before writing, and trainer.py persists operation-relative peak and net-retention evidence without ambient allocator state. Separate Q49 failure and Q36 successful-machine fixtures own the complete concrete-operation matrix, Tier-A/Tier-B recovery, independent Q19 admission, export/re-import, delta reconstruction, simulated accounting, and retained PHASE LIVE manifests. Post-close review exposed that the first deferred manifest invented eight physical-failure labels and exempted them from its matrix check. Matrix schema v4 now owns the exact Phase Live injection subset, phases, outcome, completion contract, and prohibited claims; the bounded parser exposes that subset, and the fixture resolves every field against its exact matrix section with no exemption list. No real model, live source, physical drive, cache, account, or live service enters the step."
    historical_status: DONE 2026-08-23 — implementation commits 4c0a5f347bd0dd11f6840d3d62c0c959ec5bf5b3 and 766b2a3; complete pinned CPython 3.13 arm64 macOS suite 304/304 in 154.21 seconds; ledger clean at 9,851 product LOC, 7,856 test LOC, 690 tool LOC, 109 generated LOC, five exact dependencies, one process, and one Python runtime
    status: DONE 2026-08-25 — post-close authority remediation e86f4c553e37f795a096b35d2556424026b93dae; acceptance-matrix schema v4 owns every deferred-live field, the fixture contains only exact matrix values, adjacent false passes fail, both product-guard mutations fail their owning coordinates, and the complete 304-test gate plus ledger are green
    closeout:
      - clause: "Q49 executes the complete eight-operation by sixteen-injection by six-assertion contract through concrete product entrypoints"
        test_or_probe: "tests/test_s26_phase_machine.py::test_q49_failure_rows_reach_every_concrete_operation_and_six_assertions"
        input: "Generate all 128 coordinates over acquisition, compilation, inference prefill, inference decode, training, export, repair, and revision removal; invoke each named public entrypoint under all 16 matrix injections and evaluate all six shared assertions."
        expected: "Every coordinate reaches its concrete operation, returns the matrix's exact result or typed error, preserves the parent, leaves no hidden write, refuses stale access, emits no uncommitted token, and resumes from the exact durable boundary."
        observed: "All 128 coordinates passed. sys.setprofile observed the exact public code object on every route; actual page, index, root, reservation, lifecycle, broker, pager, trainer, repair, and removal boundaries carried the injections. One hostile counterexample per shared assertion made its assertion fail, proving that no assertion passed only by construction."
      - clause: "Q49 lifecycle invalidation reaches already-constructed pager and operation objects"
        test_or_probe: "the disconnect, sleep/wake, bus-reset, port-migration, replacement, and read-only branches in tests/test_s26_phase_machine.py"
        input: "Bind each concrete operation to CartridgeLifecycle, invalidate the access epoch after object construction, attempt the stale operation, revalidate the exact cartridge identity, and resume through a fresh bound path."
        expected: "No retained plain path survives invalidation; stale use returns CARTRIDGE_DISCONNECTED, wrong media returns IDENTITY_MISMATCH, read-only mutation returns CARTRIDGE_READ_ONLY, and a valid remount resumes the same operation identity."
        observed: "BoundCartridge re-resolved identity, epoch, state, access mode, and path at each use. Pager prefill and decode re-resolved before page acquisition. Every stale access was refused, and every admitted resume produced the exact expected child or committed output."
      - clause: "Q53 compilation reserves the exact unpublished root-and-index candidate before mutation"
        test_or_probe: "the compilation capacity coordinates in tests/test_s26_phase_machine.py plus an omitted-admission probe"
        input: "Run recompilation with zero verified free bytes, allocator refusal, exact admission, and omitted capacity inputs; compare the store before and after every refused call."
        expected: "Refuse before candidate mutation unless one active reservation covers the exact canonical root payload plus fixed-record index and the shared 8 GiB safety reserve; release only terminally."
        observed: "Zero-space and fragmented-allocation coordinates returned CAPACITY_EXCEEDED without store mutation. Exact admission reserved once for 8 GiB plus the measured root-and-index bytes and released that same extent once. Omitted capacity returned typed INVALID_REQUEST with an unchanged store."
      - clause: "no_uncommitted_token is tied to the pager's committed transformer frontier"
        test_or_probe: "the inference-prefill and inference-decode routes plus _assert_tokens in tests/test_s26_phase_machine.py"
        input: "Inject every failure before, during, and after execution; compare delivered output digests with CertifiedPager.last_transformer.logits_digest rather than with request labels or expected fixture constants."
        expected: "Delivered output is a prefix of the pager's committed frontier, and no failed coordinate exposes bytes beyond that frontier."
        observed: "Both inference routes compared delivered digests to the pager-owned committed transformer record. The hostile extra-token sentinel failed the assertion, while all 32 inference coordinates passed without an uncommitted digest."
      - clause: "Q36 successful machine integration joins S24 and S25 without claiming live promotion"
        test_or_probe: "tests/test_s26_machine_gate.py::test_q36_phase_machine_integrates_success_path_and_records_only_live_deferrals"
        input: "Acquire and compile the loopback Hugging Face fixture; independently admit its Q19 plan in pager.py; export and re-import the full compiled artifact; train and reconstruct a Tier-A adapter child; recompile, train, recover, independently admit, and publish the Tier-B child; reproduce the simulated resource frontier."
        expected: "Every fixture-scale operation succeeds through its canonical authority, full and adapter exports reconstruct exact content and semantics, Tier B changes the six declared inputs and regenerates the exact 17-artifact closure while reusing only page_stats, and resource evidence remains prediction-only."
        observed: "The canonical machine outcome reproduced at blake3:0ca1307ddeef00acc477462740481c1c0fb50ed5145c80050bccb25b889c098a. The gate recorded 128 failure coordinates, exact compiled and reconstructed roots, six Tier-B changed inputs, 17 invalidated artifacts, one reused page_stats record, 18 simulated frontier points across three simulated profiles, and no F4, F5, hardware, hosted, or physical-performance claim."
      - clause: "Q16/Q25 deterministic child identity excludes unrelated process-wide MLX allocation state"
        test_or_probe: "tests/test_s26_machine_gate.py alone, after tests/test_s24_interoperability.py, and inside the complete suite"
        input: "Run the same Tier-A and Tier-B machine path in a fresh process and after S24 has left additional legitimate MLX runtime allocations alive."
        expected: "Persist operation-relative peak and net retained bytes, not ambient process baselines; identical tensors, losses, schedules, and retained-allocation results must produce identical child, delta, export, recovery, and plan identities."
        observed: "Before correction the complete suite ended 303 passed and one failed: S24 changed the persisted active baseline from 8 to 56 bytes although both executions had peak_delta_bytes=410, zero net retention, identical losses, and identical trained pages. cassette-training-trace-v2 removed ambient baselines, retained exact peak and zero-retention evidence, and made standalone, S24-preceded, and complete-suite identities byte-identical."
      - clause: "The S26 lifecycle, capacity, and shared-assertion guards are consequential"
        test_or_probe: "two disposable-tree product mutations plus six in-memory assertion sentinels; every disposable tree was discarded after its focused fixture"
        input: "Remove pager lifecycle re-resolution; remove compiler candidate-capacity admission; separately falsify each of parent preservation, hidden-write absence, exact failure, stale refusal, committed-token frontier, and exact resume."
        expected: "Each removed product guard or falsified assertion must fail the coordinate that owns it."
        observed: "The 2026-08-24 remediation replay removed pager re-resolution in one disposable tree and failed inference_decode-cartridge_disconnect because the stale pager returned success instead of CARTRIDGE_DISCONNECTED. A second disposable tree removed compiler admission and failed both compilation capacity coordinates because refused work returned success and exact admission made zero reservations. Each of the six hostile outcome sentinels also failed its named assertion. Both disposable trees were deleted after proof; the working tree retained both guards."
      - clause: "PHASE LIVE obligations remain exact and explicitly NOT_RUN"
        test_or_probe: "tests/fixtures/s26_deferred_live_rows.json plus the deferred-manifest checks in tests/test_s26_machine_gate.py"
        input: "Resolve every L01-L05 row and prohibited evidence label against the acceptance matrix without contacting a live source, downloading a model, mounting a drive, or manufacturing an F4/F5 result."
        expected: "Record the complete later campaign and its authority digest while emitting only READY_FOR_LIVE_FALSIFICATION_ONLY."
        observed: "The repaired canonical deferred manifest reproduced at blake3:23d9e57572d0580e0626fd958b89f0e600f8dfdfac93f41897375a29ad82adcf against acceptance-matrix schema v4 digest blake3:372ddc5da3c64fd837bc95c2a0bca8a5aecc5d47862a1bf306f9f807dbde34c4. L04 now cites the exact ten matrix-owned Phase Live injection IDs instead of eight fixture-authored labels, and L01-L05 resolve their classes, revisions, row IDs, gate records, workloads, completion contract, status, and prohibited claims from their exact matrix sections. Live evidence remains NOT_RUN."
      - clause: "Post-close deferred-live authority repair rejects adjacent false passes"
        test_or_probe: "the structural resolver and three hostile manifest substitutions in tests/test_s26_machine_gate.py"
        input: "Resolve every fixture value through its owning matrix section; then replace one Phase Live injection with the former unauthored physical_usb_c_detach_and_reattach label, replace it with the valid but wrong-section cancellation injection, and forge one immutable model revision while preserving valid JSON and all unrelated fields."
        expected: "Accept only the canonical projection. Reject an unknown label, a matrix-authored value borrowed from the wrong section, and a forged revision; keep the fixture and gate outcome canonical and digest-bound."
        observed: "The canonical projection passed. All three adjacent false passes raised assertion failures. The former exemption list is absent, all eight unauthored physical labels are absent from the deferred manifest and matrix authority, the one retained hostile label is refusal input only, the deferred manifest digest is blake3:23d9e57572d0580e0626fd958b89f0e600f8dfdfac93f41897375a29ad82adcf, and the machine-gate fixture digest is blake3:f7c9a1e53346eef5053fc3b759e1f8236a5cae14ce4486f1806fa9a0a5d2a9d7."
      - clause: "S26 done_when"
        test_or_probe: "complete pinned CPython 3.13 arm64 macOS suite after the deferred-authority repair, tools/ledger.py, canonical fixture readback, syntax compilation, diff checking, test-process inspection, and system-volume inspection"
        input: "Execute every reachable invariant after the schema-v4 authority correction and verify the exact machine and deferred manifests."
        expected: "Pass the complete suite and ledger with no generated drift, second process, runtime, dependency, numerical kernel, model branch, live source, real model, physical drive, or promotion claim."
        observed: "304/304 tests passed in 223.52 seconds. The ledger reported zero violations at 9,851 product LOC, 7,924 test LOC, 690 tool LOC, and 109 generated LOC, with five exact dependencies, one process, and one Python runtime. Both fixtures passed canonical-byte readback; diff checks were clean; no test runner or cartridge mount remained; and the system data volume retained 78 GiB free."

  - id: S27
    title: Full accounting and removal proof
    env: any
    files: [tools/ledger.py]
    invariants: [Q29 acceptance (reproduce complete J from a clean checkout), Q78 acceptance (delete each mapped product or tool file in isolation and observe its recorded acceptance authority fail; reject every stale, missing, or nonconsequential map entry)]
    acceptance_boundary: "S01's aggregate-audit remediation makes the per-file Q78 map incremental and ledger-enforced as each authority enters the tree. S27 does not postpone map authorship; it performs the completed-tree deletion experiment and emits the final J report."
    discovered_scope: "tests/test_s01_ledger.py moves from S01's partial-accounting key to the completed accounting authority. tests/test_s27_ledger.py independently fixes the nine-coordinate J order, injects a new kernel, process, model branch, duplicate digest authority, and binary closure, resolves all twelve map entries to direct authority-citing tests, and proves that mandatory import failure cannot make an otherwise inert owner consequential. tools/generated/s27_j_report.json is the canonical, evidence-digest-bound output produced only after the clean-checkout full suite and twelve isolated control, physical-deletion, and executable-bypass experiments pass. tools/ledger.py remains the single Q29/Q78 accounting and removal authority above 800 physical lines because splitting report measurement from deletion proof would create the second ledger Q29 and Q32 prohibit. No product module, runtime, dependency, process, numerical kernel, model branch, source request, model, service, or physical drive is added."
    expected_size: medium
    done_when: full suite + ledger green; J report committed
    depends: [S23, S26]
    status: DONE 2026-09-01 — original implementation d2893852b0700fbbd1b08467cf377169d8dfb93c; Q30 repair artifact commit 4c4744a80fd7e5ebcd58b31745a04c162cd52534 regenerated the complete proof at J=(0,0,10806,1,1,5,0,0,0), 307/307 tests with zero skips, twelve controls, twelve physical-deletion failures, and twelve owner-marked executable-bypass failures; canonical report sha256:bb278c5360658b37db770b02213ac5e993b0d3770c02cbcf0c7a34914bbc5343; ledger green
    closeout:
      - clause: "Q29 reproduces the complete nine-coordinate J tuple from one clean checkout"
        test_or_probe: "tools/ledger.py --prove-j in a detached clean worktree at d2893852b0700fbbd1b08467cf377169d8dfb93c plus tests/test_s27_ledger.py::test_q29_complete_j_classifies_every_surface_and_exposes_all_nine_coordinates"
        input: "Classify every governed source and binary; derive authored product and tool LOC, generated and test LOC, the process manifest, Python runtime pin, exact dependency manifest, numerical-kernel sites, model-specific branch table, duplicate-authority sites, and shipped binary closure; inject one new native kernel, process import, model-family branch, second digest authority, and NUL-bearing binary."
        expected: "Emit all nine J coordinates in Q29 order from the clean evidence tree; keep tests and generated code separate; report every injected surface in its exact coordinate; bind the report to the executable, fixture, schema, matrix, maths, lock, and instruction evidence."
        observed: "The injected tree reported authored.metal, subprocess, hostile.py:5, hashlib, and the seven-byte binary in their five exact surfaces. The clean checkout emitted J=(0,0,10795,1,1,5,0,0,0): zero failed acceptance rows, zero new kernels, 10,795 authored executable LOC, one process, one runtime, five direct dependencies, zero model-specific branches, zero duplicate authorities, and zero shipped binary bytes. Generated LOC remained 109 and test LOC remained 7,970 outside J."
      - clause: "Q78 deletes and semantically bypasses every mapped owner in isolation"
        test_or_probe: "the twelve removal_proofs in tools/generated/s27_j_report.json, each produced by one passing direct cited control, one physical deletion, byte-exact restoration, and one all-function executable bypass"
        input: "For each AGENTS.md removal-map entry, resolve one test that directly imports the owner and cites its sole mapped Q authority; run it unchanged; delete only that file and rerun; restore it byte-exactly; replace every executable function with the owner-specific Q78_BYPASS marker and rerun; restore again."
        expected: "Every control passes. Every deletion fails at the missing owner boundary. Every import-preserving bypass fails through the owner-specific marker, proving that mandatory import alone cannot establish necessity. No mutation survives into the next experiment."
        observed: "All twelve controls returned zero. All twelve physical deletions returned nonzero with the target module as witness. All twelve bypasses returned nonzero through their Q78_BYPASS marker: adapters/Q76, broker/Q5, compiler/Q58, errors/Q6, pager/Q19, sources/Q52, store/Q57, capture_fixture/Q40, genschema/Q33, ledger/Q29, resource_frontier/Q37, and trainer/Q21. The clean worktree was unchanged after the campaign."
      - clause: "Q78 rejects missing, stale, foreign-authority, and nonconsequential map entries"
        test_or_probe: "tests/test_s01_ledger.py::test_q78_removal_map_is_exact_and_authority_bound plus tests/test_s27_ledger.py::test_q78_isolated_deletion_rejects_a_nonconsequential_map_entry"
        input: "Omit a governed owner, name a nonexistent owner, name Q999, bind an owner to an authority absent from its header, and create one mandatory imported module whose cited assertion never executes its code."
        expected: "Reject every malformed or stale map before proof, and reject the mandatory-import example when physical deletion fails but executable bypass survives."
        observed: "The map checker rejected missing, stale, unknown, and undeclared authority bindings. The synthetic imported owner failed collection when deleted but its cited test passed after executable bypass, so S27 rejected it as nonconsequential."
      - clause: "S27 done_when and machine-only boundary"
        test_or_probe: "complete pinned CPython 3.13 arm64 macOS suite, detached clean-checkout proof generator, final tools/ledger.py readback, canonical report readback, diff checking, worktree inspection, process inspection, mount inspection, and system-volume inspection"
        input: "Run every PHASE MACHINE invariant, generate the report only from the committed clean source, validate it again from the working tree, and inspect for leaked test state or prohibited live inputs."
        expected: "Pass the complete suite and ledger; commit one canonical J report; retain no worktree, test process, mount, source request, downloaded model, external-drive operation, live-service evidence, F4 result, or F5 result."
        observed: "The complete suite passed 307/307 in 385.37 seconds before the implementation commit, and the detached committed checkout independently recorded 307 passed with zero skipped and zero failed acceptance rows. The final ledger reproduced the report with zero violations. The report is 4,954 canonical bytes at sha256:a59b5b975fbbdb34df13aafa8a9a2d8d2e283331b307746fbd2d0c35a65dd4a3. No temporary worktree, pytest process, or Cassette image remained; the system data volume retained 73 GiB free."
    q30_repair_accounting_closeout:
      - clause: "Q29 and Q78 are regenerated after the Q30 confinement repair"
        test_or_probe: "tools/ledger.py --prove-j from a clean isolated descendant of source repair 0c3e72a48d0478a036cc1fa037515b8051589394, followed by tools/ledger.py against artifact commit 4c4744a80fd7e5ebcd58b31745a04c162cd52534"
        input: "Recompute every J coordinate and the evidence digest, run the complete suite, and repeat all twelve control, physical-deletion, and executable-bypass experiments after adding the indirect-runtime guard and its existing-stage test case."
        expected: "Record the justified Q30 tool growth, preserve every zero-valued surface, and replace the stale S27 report only after the complete proof passes."
        observed: "The complete proof passed 307 tests with zero skips and all 36 removal experiments. The ledger reports zero violations and J=(0,0,10806,1,1,5,0,0,0). The 4,954-byte canonical report is sha256:bb278c5360658b37db770b02213ac5e993b0d3770c02cbcf0c7a34914bbc5343."

  - id: S28
    title: PHASE MACHINE closeout
    env: any
    files: []
    discovered_scope: "PHASE_LIVE_RUNBOOK.md is the matrix-derived human-executable L01-L05 handoff, and S28_CLOSEOUT.md records the prerequisite, blocked-step, artifact, evidence-status, and phase-boundary proof. Both are documentation artifacts; S28 adds no product code, test, tool, generated contract, dependency, process, runtime, numerical kernel, model branch, duplicate authority, or binary."
    invariants: [every S-step DONE or BLOCKED-with-report; blocked report summary; PHASE LIVE runbook generated from matrix rows]
    expected_size: small
    done_when: closeout report committed; principal notified that the live campaign is ready
    depends: [S27]
    status: DONE 2026-09-01 — original step commit c0dffeec3c78d57db1feb7d9341453a8e70c5c92; Q30 repair artifact commit 4c4744a80fd7e5ebcd58b31745a04c162cd52534 preserves all 27 resolved prerequisites and refreshes the matrix-derived L01-L05 runbook at blake3:b180c539716c8f717a4d6eacf515888e80273c4ab8cac775ee6fddde4cf6ffe0; the repaired complete proof passed 307/307 with zero skips and ledger J=(0,0,10806,1,1,5,0,0,0); PHASE MACHINE remains closed, PHASE LIVE is ready with the principal present, and all live evidence remains NOT_RUN
    closeout:
      - clause: "Every S-step is DONE or BLOCKED with a report"
        test_or_probe: "the S01-S27 status enumerator over the PHASE MACHINE block in IMPLEMENTATION.md at step commit c0dffeec3c78d57db1feb7d9341453a8e70c5c92"
        input: "Parse each current S01-S27 status after verifying S28 depends on S27."
        expected: "Enumerate exactly 27 prerequisite steps; each is DONE or BLOCKED with a report; S27 is DONE."
        observed: "The enumerator found exactly S01 through S27, all 27 statuses began DONE, no prerequisite was TODO or IN_PROGRESS, and S27 retained its complete Q29/Q78 closeout at d2893852b0700fbbd1b08467cf377169d8dfb93c."
      - clause: "The blocked report summary is complete"
        test_or_probe: "the BLOCKED filter over the same exact S01-S27 status population"
        input: "Select every prerequisite status whose current value begins BLOCKED and resolve its report and dependent consequence."
        expected: "List every blocked step and report, or record an explicit empty summary when none exists."
        observed: "The filter returned zero blocked steps. S28_CLOSEOUT.md records the empty blocked-step summary and confirms that S28 has no blocked dependency."
      - clause: "The PHASE LIVE runbook is generated from matrix rows"
        test_or_probe: "the exact-value projection comparison between research/ACCEPTANCE_MATRIX.yaml, tests/fixtures/s26_deferred_live_rows.json, and PHASE_LIVE_RUNBOOK.md"
        input: "Resolve every deferred phase value from acceptance-matrix schema version 4, require all 61 distinct matrix-derived values in the runbook, require L01-L05 in matrix order, and recompute the runbook digest."
        expected: "The runbook retains the matrix ID, schema, phase order, model revisions, source rows, fixture gates, execution rows, workloads, clients, training rows, live failure injections, offline rows, completion contract, NOT_RUN evidence status, machine outcome, and prohibited claims without inventing a live result."
        observed: "All 61 distinct values were present, L01-L05 were ordered, the exact ASCII matrix identifiers survived, and the runbook reproduced at blake3:ed2e5fe69a120aa23b90586a236a7be36b0587240d9de40db9cc3a1817c439cf. It retains DEFERRED_TO_PHASE_LIVE_NOT_RUN and READY_FOR_LIVE_FALSIFICATION_ONLY."
      - clause: "S28 done_when and machine-only boundary"
        test_or_probe: "the complete pinned CPython 3.13 suite at c0dffeec3c78d57db1feb7d9341453a8e70c5c92, tools/ledger.py, artifact digest readback, git status, process inspection, mount inspection, and system-volume inspection"
        input: "Verify the committed closeout report and runbook, execute every PHASE MACHINE fixture, recompute the complete ledger and J, and inspect for leaked or prohibited live state."
        expected: "Pass the complete suite and ledger; retain exact artifact identities; add no executable surface; leave no model download, live source request, physical-drive operation, live-service evidence, F4 result, F5 result, test process, or test mount."
        observed: "The exact step revision passed 307/307 tests in 171.36 seconds. The ledger reported zero violations and J=(0,0,10795,1,1,5,0,0,0). PHASE_LIVE_RUNBOOK.md is 13,610 bytes at blake3:ed2e5fe69a120aa23b90586a236a7be36b0587240d9de40db9cc3a1817c439cf; S28_CLOSEOUT.md is 4,607 bytes at sha256:39ad5fef0e80fa0151bc89fa8855de55c6a617f55da5022a821a856ad960c1fb. No Cassette test process or image remained, the system data volume retained 55 GiB free, and every live row remained NOT_RUN."
    q30_repair_handoff_closeout:
      - clause: "The Phase Live handoff resolves the repaired machine identities"
        test_or_probe: "artifact digest readback and tools/ledger.py after artifact commit 4c4744a80fd7e5ebcd58b31745a04c162cd52534"
        input: "Replace the superseded S27 report identity in the runbook, recompute the runbook and closeout identities, and preserve every matrix-derived L01-L05 value and every NOT_RUN live status."
        expected: "The pre-L01 identity check resolves the repaired report and runbook without changing the release matrix, introducing live evidence, or reopening a live row."
        observed: "PHASE_LIVE_RUNBOOK.md remains 13,610 bytes at blake3:b180c539716c8f717a4d6eacf515888e80273c4ab8cac775ee6fddde4cf6ffe0. S28_CLOSEOUT.md is 5,356 bytes at sha256:0fa627b6640e6b9198c4234da7adf2a49cd6b2d3608ae277e8bb70c86474098f. The ledger is green, the matrix remains schema version 4 at its recorded digest, and all live evidence remains NOT_RUN."
```

## PHASE LIVE — bounded sessions over one governed campaign

**Reconciliation, 2026-09-03.** The contract still has six phase labels: L01.25, L01.5, and
L02-L05. They remain the matrix gates. They are not working-session IDs. The earlier flat draft
named twenty-seven items but still hid repeated sessions, long-operation completion checks, and
matrix cross-products inside several items. This queue replaces that draft with fixed sessions and
matrix-expanded session records. Every executable record is flat. One record is one agent session
of at most twenty minutes.

No live result changed during this reconciliation. The adaptive-capacity and storage-eligibility
controls remain `NOT_RUN` until the amended machine gate passes. Every physical, source, model,
training, failure, offline, and completion row remains `NOT_RUN`.

### Preserved phase coverage

| Matrix phase | Flat records that satisfy it | Preserved work |
|---|---|---|
| L01.25 | L01-L13 | S28 ancestry; exact certificates; MLX confinement; plan-derived shapes; adaptive Q53; liberal drive admission; separately bounded campaign-tool authorities and hostile proof; full suite, ledger, and Q78 checkpoint |
| L01.5 | L17-L20 close the source-entry gate; later physical-qualification records gate only their exact consumers | off-drive inventory; campaign-root confinement; Q44 remount proof; exact drive × host × operation × plan profiles; full read, write, latency, IOPS, flush, thermal, health, and endurance records |
| L02 | L14-L16, L19-L20, header, acquisition, Ollama, and Tinker records | immutable pins; post-selection machine refresh; live source wires; header-only containment and tuple audit; direct-to-cartridge transfer, kill/resume, terminal digests; derivative-source round trips |
| L03 | L21-L32 plus F4/F5 inference and training records | F4 then F5 compilation, exact Q19 recomputation, inference traffic, Tier A/B, Q37 curves, and PASS or Q38 falsification |
| L04 | L33 plus execution, sustained, protocol, frontier-training, failure, offline, Q79, and final Q78 records | every required matrix expansion; no sample row or representative operation substitutes for a required coordinate |
| L05 | L34-L35 plus the materialized `Q80-*` replay records | dependency-preserving clean-root replay of every required live coordinate and one completion digest only after all rows pass |

### Session protocol

One session has four parts in order: resume (at most two minutes), read-only preparation (at most
seven), principal approval or action at the back (at most five), and the already printed approved
execution plus capture (at most six). No cartridge profile, header, transfer, training, fault, or
write begins during preparation. After the cue, the agent may run only the frozen command and may
not edit code, documentation, assertions, or the card. A record with no principal action may use the
unused action time, but the whole session remains at most twenty minutes. Credentials enter only
through the terminal or keychain as opaque references.

A long transfer, compile, training job, sustained run, or clean replay has a `START` record and a
separate `VERIFY` record. `START` closes only after the first durable boundary and one real
kill/resume proof. `VERIFY` is not eligible until the operation is terminal. An early terminal
check creates a preflight record and leaves the step `TODO`; normal waiting is neither `FAIL` nor
`BLOCKED` and consumes no attempt.

Matrix expansions are templates, not executable group stages. Before the first record in a family
runs, `tools/campaign.py` materializes every instance from the exact matrix order and any explicitly
named frozen Q15/Q16 condition or baseline manifest, gives it a stable flat ID, literal dependency
list, status, and empty attempt list, and seals the expansion digest. Each instance then runs and is
reviewed separately. The materialized list may add no row, operation, condition, baseline, client,
injection, threshold, or exception absent from those authorities.

The dependency graph has append-only revisions under one atomic compare-and-swap head. L10 proves
the expansion and graph builder against the preselection authorities; that provisional digest may
not bind a later execution. L15 succeeds it with the first post-F4-selection revision. L16, L19,
L21, L27, and each later declared materializer extend the current head before any new record becomes
eligible. Every successor names its parent graph digest and preserves every inherited node, literal
edge, evidence level, assertion owner, permission binding, and terminal-state meaning byte-for-byte.
It may add only nodes and edges authorized by its declared materializer. Deletion, rewrite, or
retargeting rejects succession; a governing-authority change that needs one starts a new graph root
under the recorded campaign-invalidation rule. Every attempt binds the exact active revision. A
review derives invalidation from the latest sealed successor whose ancestry contains the
attempt-bound graph, and records both digests. L33 seals the final source graph used by L34 and Q80.

L01-L11 bootstrap the campaign tool they will later use. They use the `machine-stage-review`
bootstrap profile. Each off-tree append-only bootstrap manifest records the stage and attempt IDs,
source commit and tree, lock, matrix, runbook, assertion-set and predecessor-manifest digests,
declared commands, raw outputs, and every inspected file digest. That profile requires no campaign
namespace, review lease, expansion registry, or dependency graph before the owning stage creates it.
Its off-tree bootstrap receipt has one atomic compare-and-swap head keyed by stage, attempt, and
manifest digest. Each review record names the current head and may advance it once; a stale head or
fork fails. At most five bootstrap review records exist per attempt, and the fifth incomplete review
returns `QUEUE_ROUTE`. Review is read-only, automatic remediation is disabled, and returns only
`PASS_READY`, `INCOMPLETE`, or `QUEUE_ROUTE`. L12 is the
first normal machine-stage review. It imports no claim: it verifies those same bytes and digests
through the completed namespace, lease, review-history, expansion, invalidation, and diff machinery.
A mismatch reopens the owning record. Automatic reviewer commits become eligible only after L12
passes, and no physical or live-source record becomes eligible until L12 and the L13 machine gate
pass.

### Evidence lineage

Machine-only L01-L11 attempts use the bootstrap profile above. L12, L13, and L15 use a frozen
machine-attempt manifest and the normal repo-local `machine-stage-review` profile. They require only
applicable STATIC, FIXTURE, INTEGRATION, or PLATFORM artifacts and never claim LIVE evidence. Fixed
record L14 and L16 onward, plus live expanded records, use `tools/campaign.py` and the repo-local
`live-stage-review` skill.

A live card has two immutable templates:

- `card_template`: operation, disk and paths, permission class, expected writes, required evidence,
  stop conditions, and row/assertion scope;
- `principal_action_template`: numbered cues and required observations, or an explicit no-action
  record.

Every live record that can write to the cartridge binds an approved card digest. The principal
either approves that exact card during the record or the binding cites an earlier immutable general
campaign approval whose disk, root, permission, command class, byte-claim rule, and stop conditions
contain the action exactly. `principal_action: none` never means approval-free. A physical fault,
path mutation, destructive action, new permission class, or action outside that exact scope always
requires a new principal cue.

Each execution has a new attempt binding. It records UTC times, observations, source commit and
tree, lock, matrix, runbook, expansion-registry, and dependency-graph digests, hardware and profile identities, fresh broker
operation IDs, durable boundaries, execution transcript, and logical-operation lineage. A rerun
reuses both template digests only when disk, paths, permission, physical action, cues, and stop
conditions are unchanged. It freshly records the source revision; that revision may equal the prior
attempt when no remediation or invalidation requires a child. It never reuses timestamps,
observations, or a terminal operation ID.

The execution bundle is sealed once. Sealing uses `lstat` without following links and accepts only
directories and regular files whose link count is one. Its canonical recursive manifest contains
every relative path, object type, and regular-file content digest, then hashes that manifest as the
namespace root. Exact namespace equality rejects an extra, missing, renamed, substituted, or
type-changed path, every symbolic or hard link, and every socket, device, FIFO, or other special
object. Review envelopes use the same rule in a separate immutable namespace. Every counted attempt has a bundle. If capture fails after an
attempt begins, `tools/campaign.py` seals a capture-failure bundle containing every recoverable raw
artifact, the exact missing-item list, and the last valid operation state; the affected assertions
remain `NOT_RUN`. A null bundle belongs only to an uncounted preflight. Every evidence item is
`APPLICABLE` or `NOT_APPLICABLE`; an
N/A item cites the authority that makes it irrelevant. N/A never applies to a declared assertion.
Applicable artifacts include, as the record requires: templates and binding; raw stdout/stderr;
before/after hardware, storage, memory, power, thermal, process, socket, and filesystem telemetry;
Q53 A_t/E_n transitions; broker logs; runtime memory; wall-clock parts; suite/ledger outputs;
off-drive inventories; and every raw-file digest. Missing evidence makes the dependent assertion
`NOT_RUN`.

The review report is a separately sealed review envelope. It names the immutable execution-bundle
digest, attempt binding, closed assertion-set digest, review base revision, reviewer environment,
exclusive review lease, replay and mutation artifacts, remediation lineage, and invalidation
decision. No reviewer adds, deletes, or rewrites a byte named by the execution manifest.

Each attempt record contains:

```yaml
attempt_id: <stage-id>-<three-digit-number>
number: <integer>
kind: initial | rerun
rerun_of: <attempt-id-or-null>
started_at_utc: <timestamp>
closure_outcome: INCOMPLETE | PASS | Q38_FALSIFIED
action_templates:
  card_template_digest: <blake3>
  principal_action_template_digest: <blake3>
binding:
  digest: <blake3>
  execution_revision: <full-sha>
  execution_tree_digest: <sha256>
  lock_digest: <sha256>
  matrix_digest: <blake3>
  runbook_digest: <blake3>
  expansion_registry_digest: <blake3>
  dependency_graph_digest: <blake3>
  assertion_set_digest: <blake3>
  execution_transcript_digest: <blake3>
  hardware_identity_digest: <blake3-or-null>
  operations:
    - logical_operation_id: <stable-id>
      operation_id: <fresh-id>
      resumes_operation_id: <id-or-null>
      recovery_boundary: <digest-or-null>
      state_at_seal: <state>
execution_bundle_digest: <blake3>
per_assertion:
  - assertion: <authority-key>
    applicability: APPLICABLE
    required_level: STATIC | FIXTURE | INTEGRATION | PLATFORM | LIVE
    status: PASS | FAIL | NOT_RUN | BLOCKED
    raw_artifact_digest: <digest-or-null>
review_history:
  head_digest: <blake3-or-null>
  entries:
    - review_id: <stage-id>-<attempt-number>-R<three-digit-number>
      review_of: <execution-bundle-or-prior-review-envelope-digest>
      prior_review_envelope_digest: <blake3-or-null>
      history_cas_expected_head: <blake3-or-null>
      history_cas_new_head: <blake3>
      review_lease_id: <id>
      lease_chain_digest: <blake3>
      review_report_digest: <blake3>
      review_base_revision: <full-sha>
      replay_evidence_level: STATIC | FIXTURE | INTEGRATION | PLATFORM
      does_not_change_original_attempt_status: true
      remediation:
        assertion: <authority-key-or-null>
        parent_sha: <full-sha-or-null>
        commit_sha: <full-sha-or-null>
        changed_paths: []
        executable_lines_changed: 0
        diff_digest: <blake3-or-null>
        red_probe_digest: <digest-or-null>
        mutation_proof_digest: <digest-or-null>
        full_gate_digest: <digest-or-null>
      invalidation_class: replay_only | assertion_local_rerun | machine_proof_rerun_required | physical_requalification_required | mechanism_revision_new_campaign_required
      invalidated_attempts: []
      invalidated_operation_lineages: []
      invalidated_qualification_lineages: []
      invalidation_graph_digest: <blake3>
      invalidation_scope_digest: <blake3>
```

Each machine and live record has five attempt slots. A machine attempt begins when its frozen
manifest starts the first declared command. A live attempt begins when an approved card is bound and
either a principal cue is printed or a live operation begins. A capture failure after either start
point still consumes the attempt and produces the capture-failure bundle described above. A
preflight that stops earlier, a review, a remediation, and normal background waiting do not. The
fifth non-PASS attempt sets the record `BLOCKED`; a sixth requires a recorded queue decision.

Review uses separate twenty-minute sessions and at most five review envelopes per execution
attempt. Each resumed review has a new review ID, names the current head as its prior envelope,
acquires a new linked lease, and atomically compares and swaps that exact head to its sealed envelope
digest. A stale expected head or fork is rejected. Time expiry seals an `INCOMPLETE` envelope with
every unreached assertion `NOT_RUN`; it does not consume an execution attempt. A fifth incomplete
review returns `QUEUE_ROUTE`; another review requires a recorded queue decision. An accepted
`REMEDIATED` envelope is terminal for that attempt's review history: no later review or second
automatic repair may descend from it. The queue must create a new execution attempt on the exact
child revision.

A verification-replay record is also append-only. It names its own ID, the original immutable
execution-bundle digest, original assertion, original required evidence level, repaired verifier
commit and tree, raw-input namespace root, replay command and output digests, status, and review
envelope. It changes no field of the original attempt.

### Review and remediation

One review lease exists for `(stage_id, attempt_id, execution_bundle_digest)`. The reviewer acquires
it with atomic create-or-compare-and-swap. Its `review_base_revision` must equal the attempt
binding's `execution_revision`. Lease records retain holder, creation, expiry, release, and any
abandonment. An expired or abandoned lease may be succeeded only by an atomic compare-and-swap that
names the prior lease digest; it is never overwritten or silently stolen. The reviewer works from a
fresh context in an isolated clean child worktree and rechecks the parent before any commit. A
remediation must descend linearly from the attempt revision. An unrelated
merge, rebase, dirty tree, base mismatch, or competing lease returns control to the queue.

Automatic remediation remains allowed for one named product-implementation,
mathematical-implementation, collector, or verifier defect. The complete remediation—not each
commit separately—may change at most forty executable lines, one assertion, no dependency, no
threshold, no authority, and no model-specific branch. The canonical command is
`tools/ledger.py remediation-diff --parent <sha> --child <sha>`. Its versioned allowlist is the
Python source in the AGENTS removal map plus `tools/campaign.py`. It rejects generated, test,
documentation, lock, schema, and unknown paths, emits normalized diff JSON, counts the
parent-relative sum of added and deleted executable lines, and excludes comments and docstrings by
its pinned Python parser. The review envelope records the JSON digest and count. One execution
attempt may produce at most one accepted remediation commit in total. An accepted remediation seals
`REMEDIATED`, terminates that review history, and requires a new attempt; serial repairs against one
old execution claim are forbidden.

One discriminating probe must fail on parent R. The reviewer then makes and commits the sole child
R+1 in the isolated worktree before running any green proof. The same probe must pass on exact
commit R+1; a relevant guard-removal or sensitivity probe must fail there; and that exact commit
must pass the full suite and ledger. No byte may change after R+1 is created. A rejected child
remains isolated and is recorded as rejected, never as accepted remediation. A changed test alone
never upgrades live evidence.

Missing evidence caused by a collector or verifier defect is remediation-eligible, but the original
attempt and its status never change. A lawful raw replay creates a separate verification-replay
record naming the original bundle, repaired verifier revision, assertion set, and replay artifacts.
It may satisfy closure at the original required evidence level only for `replay_only`, only when the
sealed original bundle already contains every required raw input, and only when no physical action
or observation must be repeated. Otherwise a new live attempt is required.

Every review names a primary cause and may name contributing causes. It also emits exactly one
invalidation class. Its scope is derived from the latest sealed graph successor whose ancestry
contains the attempt-bound graph. The review records that graph digest and seals the result as an
`invalidation_scope_digest`. Except for `replay_only`, the scope names at least one exact invalidated
attempt or evidence ID and every affected logical-operation and physical-qualification lineage. If
the narrower class cannot be proved, use the broader one. Product semantics,
durable formats, schemas, certificates, operation behavior, physical measurements, or mechanism
results changed by a repair force the corresponding machine proof, physical qualification, or new
campaign. Active live operations are not resumed across a revision unless the envelope proves the
exact compatible durable boundary.

A principal-template defect returns a successor template for queue approval. An account, hardware,
permission, service, or environment limitation is `BLOCKED` until that prerequisite changes. A
missing baseline, identity, assertion, threshold, evidence level, outcome rule, or other binding
standard is `AUTHORITY_GAP` and blocks closure until the governing document is amended. A
performance or mechanism failure follows Q38; it is not patched as an instrument defect.

The reviewer never closes a step. Its baton is `PASS_READY` only when every applicable assertion is
PASS at its required level; `INCOMPLETE` names every `NOT_RUN` or `BLOCKED` assertion;
`REMEDIATED` names the exact child and rerun route; and `QUEUE_ROUTE` names the governing decision.
`DONE/PASS` requires `PASS_READY` and the queue's closure check. A step that declares Q38 may be `DONE/Q38_FALSIFIED` when the
exact failure record is complete, but its row is `FAIL`, its PASS-dependent descendants remain
ineligible, and it cannot contribute to Q80. A queue-maintenance commit may append the immutable
attempt and review digests. Git history supplies the enclosing commit after the record is written;
the record never contains the hash of its own commit. A later, distinct queue-maintenance commit may
name a remediation commit. No queue commit may silently change assertions, dependencies, order, or
status.

### Principal actions

The principal acts only at the back of the named record:

- drive records: attach or move the named drive, confirm the printed physical identity, and approve
  a READ_ONLY or CAMPAIGN_DIRECTORY_WRITE card;
- model/source records: choose the F4 row, place credentials in the terminal, and accept a source
  license in the browser only when the live source requests it;
- training records: approve the exact drive, operation, plan, bounded current write, and endurance
  profile; unknown future output is not reserved;
- fault records: approve one PHYSICAL_FAULT card naming one disk and action, then perform only the
  printed cable, port, lid, or replacement-drive cue;
- offline records: disable and restore external networking on exact cues; and
- Q80 replay records: repeat only the card-specific action for that one replay session.

Formatting, erasure, repartitioning, repair, firmware changes, endurance stress, filler writes, and
physical faults never inherit authority from a general campaign card.

### Dependency rules

A plain dependency requires the predecessor record to close `DONE/PASS`. A dependency ending in
`@PASS` distinguishes a gate's PASS outcome from `DONE/Q38_FALSIFIED`. Every expanded record
carries literal predecessor IDs after materialization; phrases such as “matching record” below are
template rules that `tools/campaign.py` must resolve before sealing the expansion. An unresolved,
duplicate, cyclic, or ineligible edge rejects the expansion.

Preparation before a principal cue is read-only and may create only off-drive control records. No
profile, header, transfer, training, fault, or cartridge write begins before its exact card is
approved. After the cue, the agent may run only the already printed command within the approved
scope, then capture and seal evidence; it may not edit code, documentation, assertions, or the card.
The four session parts are resume (at most two minutes), preparation (at most seven), principal
approval or action (at most five), and approved execution plus capture (at most six). A record with
no principal action may use the unused action time, but the whole session remains at most twenty
minutes.

### Flat fixed queue

```yaml
phase_live_queue:
  schema_version: 3
  next_step: L01
  matrix_phases: [L01.25, L01.5, L02, L03, L04, L05]
  statuses: [TODO, IN_PROGRESS, DONE, BLOCKED]
  row_statuses: [NOT_RUN, RUNNING, PASS, FAIL, BLOCKED]
  campaign_result_statuses: [NOT_RUN, RUNNING, INCOMPLETE, PASS, FAIL, BLOCKED]
  materialized_record_contract:
    required_literal_fields: [evidence_level, matrix_assertion_owners]
    family_evidence_levels:
      baseline_freeze: INTEGRATION
      physical_qualification: LIVE
      source_header: LIVE
      acquisition: LIVE
      ollama_source: LIVE
      f4_inference: LIVE
      f5_inference: LIVE
      tinker_source: LIVE
      training: LIVE
      execution: LIVE
      sustained: LIVE
      protocol: LIVE
      failure_materialization: INTEGRATION
      live_failure: LIVE
      offline_inference: LIVE
      offline_training_audit: LIVE
      l04_runtime_closure: LIVE
      q80_clean_replay: LIVE
    matrix_assertion_owner_rules:
      - selector: every QUALIFY-<consumer-flat-id>-VERIFY
        owns: research/ACCEPTANCE_MATRIX.yaml#physical_storage_qualification.required_assertions[*]
      - selector: ACQ-<kimi_k3|llama_4_scout|qwen3_235b_a22b>-VERIFY
        owns: research/ACCEPTANCE_MATRIX.yaml#source_rows[id=source_huggingface_all_immutable_models].assertions[*]
      - selector: OLLAMA-VERIFY
        owns: research/ACCEPTANCE_MATRIX.yaml#source_rows[id=source_ollama_content_addressed_reimport].assertions[*]
      - selector: TINKER-VERIFY
        owns: research/ACCEPTANCE_MATRIX.yaml#source_rows[id=source_tinker_export_reimport].assertions[*]
      - selector: L26
        owns: research/ACCEPTANCE_MATRIX.yaml#fixture_gate_rows[id=f4_gate].pass_condition
      - selector: L32
        owns: research/ACCEPTANCE_MATRIX.yaml#fixture_gate_rows[id=f5_gate].pass_condition
      - selector: every TRAIN-<row>-<operation>-VERIFY
        owns: research/ACCEPTANCE_MATRIX.yaml#training_rows[id=<row>]+training_assertions.required_for_every_training_row[*]
      - selector: every EXEC-<row>-RUN_VERIFY
        owns: research/ACCEPTANCE_MATRIX.yaml#execution_rows[id=<row>]+workload_suites[id=capability_complete_q16].assertions[*]
      - selector: every SUSTAINED-<row>-VERIFY
        owns: research/ACCEPTANCE_MATRIX.yaml#workload_suites[id=sustained_q48].assertions[*]
      - selector: every PROTOCOL-<row>-<client>
        owns: research/ACCEPTANCE_MATRIX.yaml#protocol_cross_product.assertions[*]
      - selector: every FAILURE-<injection>-<operation>-VERIFY
        owns: research/ACCEPTANCE_MATRIX.yaml#failure_rows.assertions[*]
      - selector: every OFFLINE-INFERENCE-<row>-VERIFY
        owns: research/ACCEPTANCE_MATRIX.yaml#offline_and_privacy_rows[id=offline_inference_all_execution_rows].assertions[*]
      - selector: every OFFLINE-TRAINING-<row>-<operation>-VERIFY
        owns: research/ACCEPTANCE_MATRIX.yaml#offline_and_privacy_rows[id=offline_training_all_training_rows].assertions[*]
      - selector: L33
        owns: research/ACCEPTANCE_MATRIX.yaml#minimum_code_rows[id=q78_exact_accounting].assertions[*]
    pre_live_assertion_binding_rules:
      - authority: research/ACCEPTANCE_MATRIX.yaml#adaptive_capacity_control.required_assertions[*]
        sealed_by: L13
      - authority: research/ACCEPTANCE_MATRIX.yaml#storage_eligibility_control.required_assertions[*]
        sealed_by: L13
      - authority: research/ACCEPTANCE_MATRIX.yaml#baseline_freeze.assertions[*]
        sealed_by: BASELINES-ALL-PASS
      - authority: research/ACCEPTANCE_MATRIX.yaml#minimum_code_rows[id=q78_exact_accounting].assertions[*]
        sealed_by: [L13, L33]
    completion_contract_binding: L35
    default_matrix_assertion_owners: []
    completeness_rule: >-
      materialization resolves every selector to literal record IDs and literal authority keys;
      every assertion named by a live-owner rule has at least one terminal LIVE owner, every
      pre-live assertion has its exact sealed prior-proof binding, Q78 has both checkpoints, and
      every remaining required matrix assertion or completion clause is assigned to one of these
      rules; a missing, ambiguous, or out-of-matrix assignment rejects the graph revision
  dependency_graph_revision_contract:
    head_update: atomic_compare_and_swap
    successor_fields: [revision_digest, parent_graph_digest, expansion_registry_digest, materializer_record_id]
    provisional_graph: L10
    first_execution_eligible_graph: L15
    later_materializers: [L16, L19, L21, L24, L27, L30, FAILURE-MATERIALIZE, L34]
    attempt_binding: exact_active_graph_digest
    invalidation_graph: latest_sealed_successor_containing_attempt_graph
    q80_source_graph: final_L33_graph_head
    monotonic_extension_rule: >-
      every successor preserves inherited nodes, literal edges, evidence levels, assertion owners,
      permission bindings, and terminal-state meanings byte-for-byte and may add only records and
      edges authorized by its declared materializer; mutation, deletion, or retargeting rejects the
      successor
  fixed_steps:
    - id: L01
      matrix_phase: L01.25
      title: Freeze the amended machine starting point
      depends: [S28]
      evidence_level: STATIC
      principal_action: none
      work: >-
        Resolve the S28 close and lock without checkout; prove current ancestry; record source, tree,
        lock, matrix, and runbook identities; run the complete suite and ledger; retain the exact
        expected amendment failures.
      done_when: >-
        Every starting failure is explained by the amended Q53, J, or matrix work; any unrelated
        failure blocks L02.
      status: TODO
      attempts: []
    - id: L02
      matrix_phase: L01.25
      title: Repair exact certificate comparison and MLX confinement
      depends: [L01]
      evidence_level: FIXTURE
      principal_action: none
      work: >-
        Make the named S13 rational-collision and computed-MLX-import probes fail on the parent and
        pass on the child; kill both guards; run the full gate.
      done_when: >-
        Q19 certificate claims use exact declared rules and Q30 detects static and computed MLX
        acquisition outside pager.py and trainer.py.
      status: TODO
      attempts: []
    - id: L03
      matrix_phase: L01.25
      title: Generalize training and merge shapes from plan data
      depends: [L02]
      evidence_level: FIXTURE
      principal_action: none
      work: >-
        Add one non-2x3 tensor fixture; remove trainer and pager literal shapes in favor of plan,
        certificate, and tensor-map data; retain existing Q21, Q24, Q70, Q72, and Q30 behavior.
      done_when: >-
        Both shapes pass through the same production dataflow, full suite, ledger, and shape-source
        mutation.
      status: TODO
      attempts: []
    - id: L04
      matrix_phase: L01.25
      title: Prove adaptive capacity and liberal storage eligibility
      depends: [L03]
      evidence_level: FIXTURE
      principal_action: none
      work: >-
        Pass every adaptive-capacity and storage-eligibility assertion on scratch APFS images,
        including concurrent claims, reclamation exclusions, ENOSPC recovery, resume, and removal
        of fixed fraction, byte, whole-job, media, connector, class, and capacity gates.
      done_when: >-
        Every cited matrix assertion passes; no physical drive or live source was touched.
      carried_work: >-
        Existing unaccepted implementation and fixtures are present; L04 begins only after L01-L03
        close.
      status: TODO
      attempts: []
    - id: L05
      matrix_phase: L01.25
      title: Integrate the capacity amendment and make status honest
      depends: [L04]
      evidence_level: INTEGRATION
      principal_action: none
      work: >-
        Restore lifecycle checks at first filesystem use; regenerate canonical schema-v5 fixtures
        and J evidence; set both machine controls PASS only from the green committed result.
      done_when: >-
        The complete suite and ledger pass; J and evidence digests match the exact tree; matrix
        status matches observed proof.
      status: TODO
      attempts: []
    - id: L06
      matrix_phase: L01.25
      title: Build immutable action templates and fresh attempt bindings
      depends: [L05]
      evidence_level: FIXTURE
      principal_action: none
      work: >-
        Implement the card-template, principal-action-template, and per-execution binding records,
        including fresh operation IDs and the four frozen authority digests.
      done_when: >-
        Focused fixtures reject mutable templates, stale terminal IDs, absent authority identities,
        and an execution revision that differs from the review base.
      status: TODO
      attempts: []
    - id: L07
      matrix_phase: L01.25
      title: Build protected-content inventory and telemetry capture
      depends: [L06]
      evidence_level: FIXTURE
      principal_action: none
      work: >-
        Implement off-drive top-level name, type, and aggregate-byte inventory plus the fixed
        hardware, storage, memory, power, thermal, process, socket, and filesystem telemetry set.
      done_when: >-
        Focused fixtures detect additions, removals, type changes, and aggregate-byte changes while
        recording no descendant inventory or protected content.
      status: TODO
      attempts: []
    - id: L08
      matrix_phase: L01.25
      title: Build exact namespace sealing and capture-failure bundles
      depends: [L07]
      evidence_level: FIXTURE
      principal_action: none
      work: >-
        Implement lstat-based canonical recursive manifests for link-count-one regular files and
        directories in execution bundles and review envelopes; implement counted capture-failure
        bundles.
      done_when: >-
        Extra, missing, renamed, substituted, or type-changed paths fail exact namespace equality;
        symbolic links, hard links, sockets, devices, FIFOs, and other special objects fail; every
        counted interrupted capture seals recoverable artifacts and a missing-item list.
      status: TODO
      attempts: []
    - id: L09
      matrix_phase: L01.25
      title: Build append-only review history and atomic leases
      depends: [L08]
      evidence_level: FIXTURE
      principal_action: none
      work: >-
        Implement ordered review-history heads, atomic head compare-and-swap, and atomic
        create-or-compare-and-swap leases with expiry, release, abandonment, and digest-linked
        succession.
      done_when: >-
        Competing reviewers yield one writer; no review entry overwrites or forks another; stale
        history heads, base mismatch, silent lease theft, and broken lease ancestry fail.
      status: TODO
      attempts: []
    - id: L10
      matrix_phase: L01.25
      title: Build matrix expansion and versioned dependency graphs
      depends: [L09]
      evidence_level: FIXTURE
      principal_action: none
      work: >-
        Expand fixed and repeated records from matrix order; materialize literal edges, aggregate
        records, source selectors, evidence levels, matrix-assertion owners, and append-only graph
        revisions with an atomic head.
      done_when: >-
        Missing, duplicate, cyclic, unresolved, out-of-matrix, or order-unstable records fail; the
        same authorities reproduce byte-identical expansion and graph digests; deletion or rewrite
        of an inherited edge, evidence level, assertion owner, permission, or terminal meaning fails;
        the provisional preselection graph is marked ineligible for later execution.
      status: TODO
      attempts: []
    - id: L11
      matrix_phase: L01.25
      title: Build invalidation and remediation-diff accounting
      depends: [L10]
      evidence_level: FIXTURE
      principal_action: none
      work: >-
        Derive invalidation from the frozen graph; implement the versioned ledger remediation-diff
        command over the AGENTS removal-map source allowlist and tools/campaign.py.
      done_when: >-
        Non-replay invalidation names exact attempts, operation lineages, and qualification
        lineages; generated, test, documentation, and unknown-path edits route to the queue; the
        normalized diff and added-plus-deleted executable-line count reproduce.
      status: TODO
      attempts: []
    - id: L12
      matrix_phase: L01.25
      title: Prove the complete campaign tool on a scratch APFS image
      depends: [L06, L07, L08, L09, L10, L11]
      evidence_level: FIXTURE
      principal_action: none
      work: >-
        Run the integrated campaign tool against scratch APFS images with decoys, corrupt
        manifests, interrupted capture, extra files, rename attacks, outside-pointing symlinks,
        hard links, special files, stale review heads, competing leases, graph damage, serial
        remediation attempts, inherited-edge and owner rewrites under a valid parent digest, and
        attempted writes outside the scratch campaign root.
      done_when: >-
        Every hostile control fails at its owning assertion; accepted bundles and review histories
        reproduce without forks; one accepted remediation ends the old attempt's review history; no
        write escapes the scratch root; ledger ownership and removal checks pass.
      status: TODO
      attempts: []
    - id: L13
      matrix_phase: L01.25
      title: Close the amended machine gate and pre-live Q78 checkpoint
      depends: [L01, L02, L03, L04, L05, L06, L07, L08, L09, L10, L11, L12]
      evidence_level: INTEGRATION
      principal_action: none
      work: >-
        From the exact clean revision run full suite, ledger, J reproduction, Q78 removal proof,
        schema expansion, and both reviewer-skill validations; record source, tree, lock, matrix,
        runbook, expansion, and dependency-graph digests.
      done_when: >-
        Every machine assertion is PASS, both matrix controls are PASS, and no LIVE label exists.
      status: TODO
      attempts: []
    - id: L14
      matrix_phase: L02
      title: Pin the permissive F4 model and opaque credential
      depends: [L13]
      evidence_level: PLATFORM
      principal_action: >-
        Choose one printed candidate row and place any required token in the terminal or keychain.
      work: >-
        Resolve candidate immutable revisions, artifact bytes, and license evidence without moving
        model payload; write the exact selection through the matrix's canonical amendment path.
      done_when: >-
        The matrix contains the exact F4 model, immutable revision, and selection-record digest;
        license evidence and the secret-free credential reference resolve; no model payload moved.
      status: TODO
      attempts: []
    - id: L15
      matrix_phase: L02
      title: Refresh machine identities after the F4 selection
      depends: [L14]
      evidence_level: INTEGRATION
      principal_action: none
      work: >-
        Update the runbook matrix identity; rerun full suite, ledger, J reproduction, Q78 removal
        proof, schema expansion, and both reviewer-skill validations from the clean post-selection
        revision; invalidate the provisional L10 graph and atomically seal the exact post-selection
        expansion and dependency-graph revision.
      done_when: >-
        F4 authority is exact; matrix, runbook, expansion, and graph identities match; the new graph
        names L10 as its parent and is eligible for later bindings; machine assertions remain PASS;
        no model byte moved and no LIVE model result exists.
      status: TODO
      attempts: []
    - id: L16
      matrix_phase: L02
      title: Materialize Q13 and Q67 baseline-freeze records
      depends: [L15]
      evidence_level: INTEGRATION
      principal_action: none
      work: >-
        Expand one B_teacher and B_hosted freeze per applicable immutable model plus the complete
        B_native C1 and C2 candidate-set and selection records.
      done_when: >-
        Every baseline record has a literal identity, dependency, credential action template or
        no-action record, status, and empty attempt list; BASELINES-ALL-PASS has exact membership.
      status: TODO
      attempts: []
    - id: L17
      matrix_phase: L01.5
      title: Record drive identity and protected-content inventory
      depends: [BASELINES-ALL-PASS]
      evidence_level: LIVE
      principal_action: >-
        Attach the candidate drive, confirm the printed disk identifier and APFS UUID, and approve
        the READ_ONLY card.
      work: >-
        After approval, capture host and path telemetry and the off-drive top-level name, type, and
        aggregate-byte inventory.
      done_when: >-
        Identity and inventory are sealed; the drive has no recorded byte change.
      status: TODO
      attempts: []
    - id: L18
      matrix_phase: L01.5
      title: Create the campaign root and prove Q44 through remount
      depends: [L17]
      evidence_level: LIVE
      principal_action: >-
        Approve the exact CAMPAIGN_DIRECTORY_WRITE and PHYSICAL_FAULT cards; detach and reattach
        only on their printed cues.
      work: >-
        After approval, create the campaign root as the first write; execute write, readback hash,
        F_FULLFSYNC, root, pointer, F_FULLFSYNC; remount by exact identity; compare inventories.
      done_when: >-
        The exact generation survives remount and no top-level change exists outside the campaign
        root.
      status: TODO
      attempts: []
    - id: L19
      matrix_phase: L01.5
      title: Materialize source qualification and header records
      depends: [BASELINES-ALL-PASS, L18]
      evidence_level: INTEGRATION
      principal_action: none
      work: >-
        Materialize separate HEADER and ACQ physical-profile requests for F4, kimi_k3,
        llama_4_scout, and qwen3_235b_a22b, plus OLLAMA; materialize one header record per model.
      done_when: >-
        Every request has literal profile predecessors, action templates, statuses, and empty
        attempt lists; SOURCE-PROFILES-ALL-PASS and HEADERS-ALL-PASS have exact sealed memberships.
      status: TODO
      attempts: []
    - id: L20
      matrix_phase: L01.5
      title: Close source-entry physical qualification
      depends: [SOURCE-PROFILES-ALL-PASS]
      evidence_level: LIVE
      principal_action: none
      work: >-
        Recompute every HEADER, ACQ, and OLLAMA physical profile from its sealed bundle and
        reconcile the coarse protected-content inventory before any live source request.
      done_when: >-
        Every HEADER and ACQ profile and the OLLAMA profile are PASS; no live source request or
        model payload acquisition has begun.
      status: TODO
      attempts: []
    - id: L21
      matrix_phase: L03
      title: Materialize F4 compile and inference qualification
      depends: [ACQ-F4-VERIFY, L20]
      evidence_level: INTEGRATION
      principal_action: none
      work: >-
        Materialize exact F4 compile and inference physical-profile requests from the pinned model,
        current drive, host, path, and certified plans.
      done_when: >-
        F4-PROFILES-ALL-PASS has exactly the two required profile records with literal dependencies.
      status: TODO
      attempts: []
    - id: L22
      matrix_phase: L03
      title: Close F4 compile and inference qualification
      depends: [F4-PROFILES-ALL-PASS]
      evidence_level: LIVE
      principal_action: none
      work: >-
        Recompute both profile results and inventory effects from their sealed bundles.
      done_when: >-
        The exact F4 compile and inference paths are PASS; no profile is inherited by label.
      status: TODO
      attempts: []
    - id: L23
      matrix_phase: L03
      title: Start F4 compilation
      depends: [L22]
      evidence_level: LIVE
      principal_action: >-
        Approve the exact F4 compilation CAMPAIGN_DIRECTORY_WRITE card after its command, next-byte
        claim, paths, recovery boundary, and stop conditions are printed.
      work: >-
        Start Q19 compilation; prove the first durable boundary and one real kill and resume; leave
        the broker operation RUNNING or terminal.
      done_when: >-
        Start assertions pass and the exact logical operation is durably recoverable.
      status: TODO
      attempts: []
    - id: L24
      matrix_phase: L03
      title: Verify terminal F4 compilation and Q19 certificate
      depends: [L23]
      evidence_level: LIVE
      principal_action: none
      work: >-
        When terminal, verify source and executable digests, peak extent, containment, total map,
        resume, and independent exact recomputation of every Q19 field; materialize the frozen F4
        inference conditions and atomically extend the graph.
      done_when: >-
        One immutable F4 compiled revision is published, every certificate field recomputes, and
        the F4 inference records and aggregate reproduce from its frozen condition set.
      status: TODO
      attempts: []
    - id: L25
      matrix_phase: L03
      title: Close the expanded F4 inference proof
      depends: [F4-INFERENCE-ALL-PASS]
      evidence_level: LIVE
      principal_action: none
      work: >-
        Recompute every frozen Q15 and Q16 condition, touched-byte result, schedule, memory bound,
        corruption discriminator, and restoration result from the expanded records.
      done_when: >-
        Every F4 inference coordinate is PASS at LIVE evidence.
      status: TODO
      attempts: []
    - id: L26
      matrix_phase: L03
      title: Decide the F4 gate
      depends: [L25, TRAIN-train_dense_fixture_tier_a-ALL-PASS, TRAIN-train_dense_fixture_tier_b-ALL-PASS]
      evidence_level: LIVE
      principal_action: none
      work: >-
        Compute the predeclared paired Q17 and Q18 statistics and all Q36 predicates from raw
        evidence; emit PASS or FAIL with Q38_FALSIFIED.
      done_when: >-
        The exact gate record exists; only PASS satisfies L27 and the two frontier-compiled L04
        rows.
      status: TODO
      attempts: []
    - id: L27
      matrix_phase: L03
      title: Materialize pinned Scout F5 qualification
      depends: [L26@PASS, ACQ-llama_4_scout-VERIFY]
      evidence_level: INTEGRATION
      principal_action: none
      work: >-
        Bind the matrix-pinned Scout revision as F5 and materialize its exact compile and inference
        physical-profile requests.
      done_when: >-
        F5-PROFILES-ALL-PASS has exactly the two required profile records with literal dependencies.
      status: TODO
      attempts: []
    - id: L28
      matrix_phase: L03
      title: Close F5 compile and inference qualification
      depends: [F5-PROFILES-ALL-PASS]
      evidence_level: LIVE
      principal_action: none
      work: >-
        Recompute both profile results and inventory effects from their sealed bundles.
      done_when: >-
        The exact Scout F5 compile and inference paths are PASS.
      status: TODO
      attempts: []
    - id: L29
      matrix_phase: L03
      title: Start F5 compilation
      depends: [L28]
      evidence_level: LIVE
      principal_action: >-
        Approve the exact F5 compilation CAMPAIGN_DIRECTORY_WRITE card after its command, next-byte
        claim, paths, recovery boundary, and stop conditions are printed.
      work: >-
        Start the pinned Scout sparse Q19 compilation; prove the first durable boundary and one real
        kill and resume; leave the broker operation RUNNING or terminal.
      done_when: >-
        Start assertions pass and the exact logical operation is durably recoverable.
      status: TODO
      attempts: []
    - id: L30
      matrix_phase: L03
      title: Verify terminal F5 compilation and Q19 certificate
      depends: [L29]
      evidence_level: LIVE
      principal_action: none
      work: >-
        When terminal, verify source and executable digests, total contribution map, recovery,
        containment, and independent exact Q19 recomputation at sparse scale; materialize the frozen
        F5 inference conditions and atomically extend the graph.
      done_when: >-
        One immutable Scout F5 revision is published with every certificate field exact, and the F5
        inference records and aggregate reproduce from its frozen condition set.
      status: TODO
      attempts: []
    - id: L31
      matrix_phase: L03
      title: Close the expanded F5 inference proof
      depends: [F5-INFERENCE-ALL-PASS]
      evidence_level: LIVE
      principal_action: none
      work: >-
        Recompute every frozen condition, traffic bound, schedule, memory, corruption, risk, and
        horizon result from the expanded records.
      done_when: >-
        Every F5 inference coordinate is PASS at LIVE evidence.
      status: TODO
      attempts: []
    - id: L32
      matrix_phase: L03
      title: Decide the F5 gate from Q37 curves
      depends: [L31, TRAIN-train_sparse_fixture_tier_a-ALL-PASS, TRAIN-train_sparse_fixture_tier_b-ALL-PASS]
      evidence_level: LIVE
      principal_action: none
      work: >-
        Fit the predeclared mathematical-resource, quality, and service curves; compare the
        predicted feasible point with Q68 and E-011; emit PASS or FAIL with Q38_FALSIFIED.
      done_when: >-
        The exact F5 record exists; only PASS makes the two frontier-compiled L04 rows eligible and
        permits completion.
      status: TODO
      attempts: []
    - id: L33
      matrix_phase: L04
      title: Seal Q79 and final Q78 after every runtime row
      depends:
        - L04-RUNTIME-ALL-PASS
        - TINKER-VERIFY
        - ACQ-F4-VERIFY
        - ACQ-kimi_k3-VERIFY
        - ACQ-llama_4_scout-VERIFY
        - ACQ-qwen3_235b_a22b-VERIFY
        - OLLAMA-VERIFY
        - L26@PASS
        - L32@PASS
      evidence_level: LIVE
      principal_action: none
      work: >-
        Recompute Q79 provenance and privacy from raw traces; rerun full suite, ledger, J, and Q78
        removal proof from the exact clean tree; reconcile every required row; atomically seal the
        final source dependency-graph head for Q80.
      done_when: >-
        Q79 and q78_exact_accounting are PASS with immutable evidence and every required L04 runtime
        row is PASS; the final graph digest and owner-completeness report reproduce.
      status: TODO
      attempts: []
    - id: L34
      matrix_phase: L05
      title: Materialize the clean-root Q80 replay graph
      depends: [L33]
      evidence_level: INTEGRATION
      principal_action: none
      work: >-
        Compute the transitive LIVE prerequisite closure of every terminal record that owns a
        required matrix assertion plus L33; create one replay record per member and mirror every
        dependency edge.
      done_when: >-
        The sorted original-record list, source count, replay count, edge count, and graph digest
        reproduce; every replay record is TODO; Q80-ALL-PASS has exact one-to-one membership.
      status: TODO
      attempts: []
    - id: L35
      matrix_phase: L05
      title: Verify Q80 and emit or withhold the completion digest
      depends: [Q80-ALL-PASS]
      evidence_level: LIVE
      principal_action: none
      work: >-
        Recompute every row from raw clean-root replay evidence; rerun Q78 and Q79; verify gate
        order, inventories, identities, and forbidden substitutes; compute the canonical preimage.
      done_when: >-
        Set campaign result PASS and attach one digest only if every required row is PASS and
        LIVE_PROVEN; otherwise retain the exact non-passing result and sealed evidence bundle.
      status: TODO
      attempts: []

  expanded_session_families:
    - family: baseline_freeze
      matrix_phase: L02
      materialized_by: L16
      expand_over: every_applicable_model_x_B_teacher_and_B_hosted_plus_B_native_c1_and_B_native_c2
      records_per_coordinate: [FREEZE]
      id_format: BASELINE-<baseline-coordinate>-FREEZE
      dependencies:
        FREEZE: [L15]
      work: >-
        Freeze the exact model revision, source and compute provenance, prompts, decoding and tool
        settings, context, quantization, hardware and software, repeated-trial design, candidate set,
        deterministic selection, and honest NON_EQUIVALENT fields that apply to this one baseline.
      principal_action: >-
        Supply a hosted-reference credential only for the exact hosted coordinate and only as an
        opaque terminal or keychain reference; every other coordinate requires none.
      status_per_record: TODO
      attempts_per_record: []
      aggregate_record: BASELINES-ALL-PASS
      aggregate_dependencies: [every-BASELINE-<baseline-coordinate>-FREEZE]
      aggregate_rule: >-
        PASS only when every applicable baseline has one immutable manifest and no teacher trace or
        Q17, Q18, or Q68 comparison predates it.
    - family: physical_qualification
      matrix_phase: L01.5
      expand_over: every_exact_consumer_profile_request
      records_per_request: [START, VERIFY]
      id_format: QUALIFY-<consumer-flat-id>-<record>
      request_fields:
        - consumer_flat_id
        - physical_disk_id
        - apfs_volume_uuid
        - host_id
        - assembled_path_digest
        - operation
        - plan_digest
        - expected_read_write_shape
      dependencies:
        START: [literal_consumer_prerequisites_that_do_not_depend_on_this_profile]
        VERIFY: [matching-START]
      start_work: >-
        Prepare the exact card; after approval, begin the complete Q41-Q44 profile as a resumable
        broker operation and seal its first durable measurement window.
      verify_work: >-
        After terminal state, verify all plan sizes, alignments, patterns, cache crossing, p05, p50,
        p95, p99, maximum latency, IOPS, flushes, errors, thermal events, writes, health, endurance,
        Q44 ordering, and inventory effects that apply.
      principal_action: >-
        On START, attach or move the named drive when cued, confirm exact identity, and approve this
        one profile card. VERIFY requires none.
      path_change_rule: >-
        Any drive, cable, port, host, assembled path, plan, or mechanism change creates a new
        request and blocks resumed I/O until its VERIFY record passes.
      group_aggregate_id_format: <request-group>-ALL-PASS
      group_aggregate_rule: >-
        Materialization stages assign every request to one sealed group. The group aggregate lists
        every literal QUALIFY-<consumer-flat-id>-VERIFY member and passes only when all pass. L19
        creates SOURCE-PROFILES, L21 creates F4-PROFILES, and L27 creates F5-PROFILES.
      status_per_record: TODO
      attempts_per_record: []
    - family: source_header
      matrix_phase: L02
      materialized_by: L19
      instances: [F4, kimi_k3, llama_4_scout, qwen3_235b_a22b]
      records_per_instance: [RUN]
      id_format: HEADER-<instance>-RUN
      dependencies:
        RUN: [L20, BASELINES-ALL-PASS, QUALIFY-HEADER-<instance>-VERIFY]
      work: >-
        After approval, exercise live resolve, enumerate, metadata, license, authentication, and
        header-range paths; land only header bytes; inventory dtypes, shapes, operators, semantics,
        and execute no remote code.
      principal_action: >-
        Approve the exact HEADER CAMPAIGN_DIRECTORY_WRITE card; accept a source license in the
        browser only when the service requests it.
      status_per_record: TODO
      attempts_per_record: []
      aggregate_record: HEADERS-ALL-PASS
      aggregate_dependencies:
        - every HEADER-<instance>-RUN
      aggregate_rule: >-
        PASS only when all four literal header members pass and no model payload acquisition has begun.
    - family: acquisition
      matrix_phase: L02
      instances: [F4, kimi_k3, llama_4_scout, qwen3_235b_a22b]
      records_per_instance: [START, VERIFY]
      id_format: ACQ-<instance>-<record>
      dependencies:
        START: [L20, HEADER-<instance>-RUN, QUALIFY-ACQ-<instance>-VERIFY]
        VERIFY: [matching-START]
      start_work: >-
        After approval, start direct-to-cartridge ranged acquisition; prove per-transition Q53,
        first durable boundary, real kill and resume, and no internal model file.
      verify_work: >-
        After terminal state, prove immutable revision, complete intervals, final source and local
        digests, exact byte total, and no internal model file.
      principal_action: >-
        START requires the exact drive and write card; a different drive first requires its own
        physical-qualification request and PASS. VERIFY requires none.
      status_per_record: TODO
      attempts_per_record: []
    - family: ollama_source
      matrix_phase: L02
      instances: [source_ollama_content_addressed_reimport]
      records_per_instance: [START, VERIFY]
      id_format: OLLAMA-<record>
      dependencies:
        START: [ACQ-llama_4_scout-VERIFY, QUALIFY-OLLAMA-VERIFY]
        VERIFY: [matching-START]
      start_work: >-
        Re-expose the pinned Scout bytes as content-addressed Ollama manifests and blobs; start
        production-adapter reacquisition; prove the first durable boundary and kill and resume.
      verify_work: >-
        After terminal state, prove complete manifest and blob digests, semantic identity, source
        identity, and the shared Q5 lifecycle.
      principal_action: >-
        START requires the exact bounded drive-write card. VERIFY requires none.
      status_per_record: TODO
      attempts_per_record: []
    - family: f4_inference
      matrix_phase: L03
      materialized_by: L24
      expand_over: frozen_Q15_Q16_conditions_for_selected_F4
      records_per_coordinate: [START, VERIFY]
      id_format: F4-INFERENCE-<condition-digest>-<record>
      dependencies:
        START: [L24, QUALIFY-F4-INFERENCE-VERIFY]
        VERIFY: [matching-START]
      start_work: >-
        Start one frozen condition and seal the first committed result frontier.
      verify_work: >-
        Verify its quality inputs, touched bytes, schedule, memory, corrupt-page discriminator, and
        exact restoration result.
      principal_action: none
      status_per_record: TODO
      attempts_per_record: []
      aggregate_record: F4-INFERENCE-ALL-PASS
      aggregate_dependencies: [every-F4-INFERENCE-<condition-digest>-VERIFY]
    - family: f5_inference
      matrix_phase: L03
      materialized_by: L30
      expand_over: frozen_Q15_Q16_conditions_for_pinned_Scout_F5
      records_per_coordinate: [START, VERIFY]
      id_format: F5-INFERENCE-<condition-digest>-<record>
      dependencies:
        START: [L30, QUALIFY-F5-INFERENCE-VERIFY]
        VERIFY: [matching-START]
      start_work: >-
        Start one frozen sparse-scale condition and seal the first committed result frontier.
      verify_work: >-
        Verify its quality inputs, traffic bound, schedule, memory, corruption, error-risk, and
        horizon predicates.
      principal_action: none
      status_per_record: TODO
      attempts_per_record: []
      aggregate_record: F5-INFERENCE-ALL-PASS
      aggregate_dependencies: [every-F5-INFERENCE-<condition-digest>-VERIFY]
    - family: tinker_source
      matrix_phase: L02
      instances: [source_tinker_export_reimport]
      records_per_instance: [QUALIFY_START, QUALIFY_VERIFY, START, VERIFY]
      id_format: TINKER-<record>
      dependencies:
        QUALIFY_START: [TRAIN-train_dense_fixture_tier_a-ALL-PASS]
        QUALIFY_VERIFY: [matching-QUALIFY_START]
        START: [matching-QUALIFY_VERIFY]
        VERIFY: [matching-START]
      qualify_start_work: >-
        After approval, begin the exact export and re-import profile measurement.
      qualify_verify_work: >-
        Verify the terminal Q41-Q44 and Q74 profile.
      start_work: >-
        After approval, export the dense Tier-A child in Tinker form and begin production-wire
        re-import; prove first durable boundary and kill and resume.
      verify_work: >-
        Prove terminal weight identity, parent, training provenance, digests, and shared lifecycle.
      principal_action: >-
        QUALIFY_START and START each require their own exact bounded card; the other records require
        none.
      status_per_record: TODO
      attempts_per_record: []
    - family: training
      matrix_phase: L03_or_L04_from_matrix_row
      expand_over: training_rows_x_every_declared_operation
      records_per_coordinate: [QUALIFY_START, QUALIFY_VERIFY, START, VERIFY]
      id_format: TRAIN-<row>-<operation>-<record>
      dependencies:
        QUALIFY_START: [literal-row-dependencies]
        QUALIFY_VERIFY: [matching-QUALIFY_START]
        START: [matching-QUALIFY_VERIFY]
        VERIFY: [matching-START]
      row_dependencies:
        train_dense_fixture_tier_a: [L25]
        train_dense_fixture_tier_b: [TRAIN-train_dense_fixture_tier_a-ALL-PASS]
        train_sparse_fixture_tier_a: [L31, L26@PASS]
        train_sparse_fixture_tier_b: [TRAIN-train_sparse_fixture_tier_a-ALL-PASS]
        train_c1_frontier_tier_a: [EXEC-exec_c1_frontier_compiled-RUN_VERIFY]
        train_c1_frontier_tier_b: [TRAIN-train_c1_frontier_tier_a-ALL-PASS]
        train_c1_scout_tier_a: [EXEC-exec_c1_scout_least_invasive-RUN_VERIFY]
        train_c3_frontier_tier_a: [EXEC-exec_c3_k3_compiled_portability-RUN_VERIFY]
        train_c3_frontier_tier_b: [TRAIN-train_c3_frontier_tier_a-ALL-PASS]
      qualify_start_work: >-
        After approval, begin the exact training-plan Q41-Q44 and Q74 profile.
      qualify_verify_work: >-
        Verify terminal profile, writes, health, endurance, and inventory evidence.
      start_work: >-
        With Q79 tracing armed and external networking disabled, start the exact Q23, Q28, Q47,
        Q53, and Q74 operation; prove one Q25 kill and resume; leave it running.
      verify_work: >-
        Prove terminal Q70, Q71, Q72, Q73, measured writes, estimate bound, quality,
        non-regression, client callability, and Tier-B derivation where applicable.
      principal_action: >-
        QUALIFY_START requires the exact profile card. START requires the exact
        drive-operation-plan card and network-off cue; restore networking during capture. The other
        records require none.
      status_per_record: TODO
      attempts_per_record: []
      aggregate_record_per_row: ALL-PASS
      aggregate_id_format: TRAIN-<row>-ALL-PASS
      aggregate_dependencies: [every-TRAIN-<row>-<declared-operation>-VERIFY]
      aggregate_rule: >-
        PASS only when every operation declared by that exact matrix row is PASS at its required
        evidence level.
    - family: execution
      matrix_phase: L04
      expand_over: execution_rows
      records_per_row: [QUALIFY_START, QUALIFY_VERIFY, PREPARE_START, PREPARE_VERIFY, RUN_START, RUN_VERIFY]
      id_format: EXEC-<row>-<record>
      dependencies:
        QUALIFY_START: [literal-row-dependencies]
        QUALIFY_VERIFY: [matching-QUALIFY_START]
        PREPARE_START: [matching-QUALIFY_VERIFY]
        PREPARE_VERIFY: [matching-PREPARE_START]
        RUN_START: [matching-PREPARE_VERIFY]
        RUN_VERIFY: [matching-RUN_START]
      row_dependencies:
        exec_c1_frontier_compiled: [ACQ-kimi_k3-VERIFY, L26@PASS, L32@PASS]
        exec_c1_scout_least_invasive: [ACQ-llama_4_scout-VERIFY]
        exec_c2_qwen_least_invasive: [ACQ-qwen3_235b_a22b-VERIFY]
        exec_c3_k3_native_teacher: [ACQ-kimi_k3-VERIFY]
        exec_c3_k3_compiled_portability: [ACQ-kimi_k3-VERIFY, L26@PASS, L32@PASS]
      qualify_start_work: >-
        After approval, begin the row's exact drive, path, host, operation, and plan profile.
      qualify_verify_work: >-
        Verify terminal Q41-Q44 and applicable Q74 evidence.
      prepare_start_work: >-
        Start the least-invasive Q40 preparation; for compiled K3 rows start full-scale F6
        compilation; prove first durable boundary and kill and resume.
      prepare_verify_work: >-
        Verify terminal native or immutable prepared revision, prior-mode Q38 records, total map,
        and independent Q19 certificate when compiled.
      run_start_work: >-
        Start the complete Q16 capability suite and seal its first valid result frontier.
      run_verify_work: >-
        Verify every case, context boundary, gate, honesty vector, tail, capability, and forbidden
        label from raw evidence.
      principal_action: >-
        QUALIFY_START requires drive identity and the exact profile card. PREPARE_START and
        RUN_START each require an exact CAMPAIGN_DIRECTORY_WRITE card for that record's printed
        command, paths, next-byte claim, recovery boundary, and stop conditions. The verify records
        require none.
      status_per_record: TODO
      attempts_per_record: []
    - family: sustained
      matrix_phase: L04
      expand_over: execution_rows
      records_per_row: [START, VERIFY]
      id_format: SUSTAINED-<row>-<record>
      dependencies:
        START: [matching-EXEC-<row>-RUN_VERIFY]
        VERIFY: [matching-START]
      start_work: >-
        Start the 120-minute and 20000-token run with five-minute service, thermal, write, and
        integrity windows; verify the first two windows.
      verify_work: >-
        After terminal state, recompute every window, decay, tail, thermal, availability, and
        integrity assertion.
      principal_action: none
      status_per_record: TODO
      attempts_per_record: []
    - family: protocol
      matrix_phase: L04
      expand_over: execution_rows_x_agent_clients
      records_per_coordinate: [RUN]
      id_format: PROTOCOL-<row>-<client>
      dependencies:
        RUN: [matching-EXEC-<row>-RUN_VERIFY]
      work: >-
        Capture all eight required traces and prove Q76, Q77, and no fabricated feature for this
        one row and client mapping.
      principal_action: none
      status_per_record: TODO
      attempts_per_record: []
    - family: failure_materialization
      matrix_phase: L04
      records: [FAILURE-MATERIALIZE]
      dependencies:
        - HEADER-F4-RUN
        - ACQ-F4-VERIFY
        - L24
        - L25
        - TRAIN-train_dense_fixture_tier_a-ALL-PASS
      work: >-
        Resolve the eight matrix operation subjects to literal source artifacts and plans;
        materialize all eighty failure coordinates, the eight starting physical-profile requests,
        and the matrix-determined requalification nodes; atomically extend the graph.
      done_when: >-
        Operation bindings, 80 coordinates, 320 base records, 112 requalification records, profile
        requests, assertion owners, action templates, and every literal edge reproduce.
      principal_action: none
      status_per_record: TODO
      attempts_per_record: []
    - family: live_failure
      matrix_phase: L04
      materialized_by: FAILURE-MATERIALIZE
      expand_over: phase_live_injections_x_failure_operations
      base_records_per_coordinate: [ARM, INJECT, RECOVER, VERIFY]
      requalification_records: [REQUALIFY_START, REQUALIFY_VERIFY]
      requalification_rule: >-
        Materialize both requalification records exactly when the injection appears in
        matrix.failure_rows.requalification_after_recovery.required_for; omit both exactly when it
        appears in not_applicable_for. An injection in neither or both lists rejects expansion.
        This produces 320 base records plus 112 requalification records from the current matrix.
      id_format: FAILURE-<injection>-<operation>-<record>
      materialized_binding_fields:
        - source_artifact_record_id
        - source_artifact_digest
        - operation_plan_digest
        - physical_qualification_record_id
        - logical_operation_id
        - recovery_action_template_digest
        - requalification_required
      requalification_field_rule: >-
        requalification_required is true exactly for an injection listed in
        matrix.failure_rows.requalification_after_recovery.required_for and false exactly for one
        listed in not_applicable_for; no runtime observation may change the materialized value
      operation_subjects: matrix.failure_rows.phase_live_operation_bindings
      starting_profile_requests: >-
        FAILURE-MATERIALIZE creates the eight exact QUALIFY-FAILURE-<operation> profile requests;
        each profile START depends on FAILURE-MATERIALIZE and its literal source artifact. Every
        VERIFY must pass before the matching ARM records become eligible.
      dependencies:
        ARM: [FAILURE-MATERIALIZE, literal-source-artifact-record-id, literal-physical-qualification-record-id]
        INJECT: [matching-ARM]
        RECOVER: [matching-INJECT]
        REQUALIFY_START: [matching-RECOVER]
        REQUALIFY_VERIFY: [matching-REQUALIFY_START]
        VERIFY:
          always: [matching-RECOVER]
          when_requalification_required: [matching-REQUALIFY_VERIFY]
      arm_work: >-
        Create a fresh operation from its exact source artifact through the declared durable
        pre-injection boundary; reuse no prior terminal operation.
      inject_work: >-
        After exact approval, apply one injection and capture the immediate typed result.
      recover_work: >-
        After an exact recovery card when physical action is required, restore or refuse the named
        identity and seal the resulting boundary.
      requalify_start_work: >-
        After path-profile approval, start a new exact Q41-Q44 profile for any changed drive, cable,
        port, host, path, plan, or mechanism.
      requalify_verify_work: >-
        Verify the terminal replacement profile before any resumed I/O.
      verify_work: >-
        Prove all six failure assertions and inventory effects from the coordinate's own lineage.
      principal_action: >-
        ARM requires the exact coordinate's CAMPAIGN_DIRECTORY_WRITE card before creating its fresh
        durable operation. INJECT always requires its separate exact injection card. RECOVER
        requires a separate exact card when it changes physical state. REQUALIFY_START requires its
        own profile card. Perform only the printed cue; a general campaign approval never applies.
      status_per_record: TODO
      attempts_per_record: []
    - family: offline_inference
      matrix_phase: L04
      expand_over: execution_rows
      records_per_row: [START, VERIFY]
      id_format: OFFLINE-INFERENCE-<row>-<record>
      dependencies:
        START: [matching-EXEC-<row>-RUN_VERIFY]
        VERIFY: [matching-START]
      start_work: >-
        After the network-off cue, start the complete row through loopback while tracing processes,
        sockets, files, identities, credentials, and persistence.
      verify_work: >-
        Recompute every offline and privacy assertion and restore networking only on its sealed cue.
      principal_action: >-
        START requires the exact network-off cue; VERIFY requires the exact network-restore cue.
      status_per_record: TODO
      attempts_per_record: []
    - family: offline_training_audit
      matrix_phase: L04
      expand_over: training_rows_x_every_declared_operation
      records_per_coordinate: [VERIFY]
      id_format: OFFLINE-TRAINING-<row>-<operation>-VERIFY
      dependencies:
        VERIFY: [matching-TRAIN-<row>-<operation>-VERIFY]
      work: >-
        Verify this one operation's placement, socket, credential, and persistence traces; a
        missing trace requires a new matching TRAIN attempt.
      principal_action: none
      status_per_record: TODO
      attempts_per_record: []
    - family: l04_runtime_closure
      matrix_phase: L04
      records: [L04-RUNTIME-ALL-PASS]
      dependencies:
        - every EXEC-<row>-RUN_VERIFY
        - every SUSTAINED-<row>-VERIFY
        - every PROTOCOL-<row>-<client>
        - every L04 TRAIN-<row>-ALL-PASS
        - every FAILURE-<injection>-<operation>-VERIFY
        - every OFFLINE-INFERENCE-<row>-VERIFY
        - every OFFLINE-TRAINING-<row>-<operation>-VERIFY
      work: >-
        Resolve the sealed registry against every required runtime expansion and reject any
        missing, duplicate, ineligible, FAIL, BLOCKED, RUNNING, or NOT_RUN coordinate.
      done_when: >-
        PASS only when every required L04 runtime row is PASS; independent rows may run after a
        gate failure, but this aggregate cannot pass until both gates and their dependent rows pass.
      principal_action: none
      status_per_record: TODO
      attempts_per_record: []
    - family: q80_clean_replay
      matrix_phase: L05
      materialized_by: L34
      membership_rule: >-
        From materialized_record_contract, resolve every literal record whose evidence_level is LIVE
        and whose matrix_assertion_owners list is nonempty. Reject any required live assertion
        without a resolved owner or any required pre-live assertion without its sealed prior-proof
        binding. Add L33. Let V be their transitive prerequisite closure in L33's
        final sealed Phase Live graph, excluding the q80_clean_replay family itself. Keep only LIVE
        records and their LIVE aggregate records; treat pre-live authority selection and baseline
        records as frozen inputs, not repeatable choices. Sort V by canonical flat ID. The
        source_record_count and expected_replay_count both equal cardinality(V).
      edge_rule: >-
        For each original edge u to v with u and v in V, add Q80-u to Q80-v. No replay record may
        have an edge absent from that induced graph or omit one present in it.
      records_per_member: [REPLAY]
      id_format: Q80-<original-flat-id>
      lineage_rule: >-
        A replay START creates a fresh logical operation in one clean campaign root. Its replay
        VERIFY, recovery, and aggregate descendants bind that same replay logical operation and
        root, never the original campaign operation.
      work: >-
        Re-execute exactly one original record with a new binding, fresh operation ID where
        applicable, raw evidence, and review history.
      principal_action: >-
        Mirror the original record's one exact action template, or none when the original required
        none.
      status_per_record: TODO
      attempts_per_record: []
      aggregate_record: Q80-ALL-PASS
      aggregate_dependencies: [every-Q80-<original-flat-id>]
      aggregate_rule: >-
        PASS only when the one-to-one record and edge counts match the sealed source graph and every
        replay member is PASS at LIVE evidence.
```

## Status vocabulary

Queue status is `TODO`, `IN_PROGRESS`, `DONE`, or `BLOCKED`. Matrix row status is `NOT_RUN`,
`RUNNING`, `PASS`, `FAIL`, or `BLOCKED`. Closure outcome is `INCOMPLETE`, `PASS`, or
`Q38_FALSIFIED`. These vocabularies do not substitute for one another. A background operation may
be `RUNNING` while its `START` record is `DONE` and its `VERIFY` record remains `TODO`. Campaign
result status is `NOT_RUN`, `RUNNING`, `INCOMPLETE`, `PASS`, `FAIL`, or `BLOCKED` under the matrix
definitions. Only campaign `PASS` carries the Q80 completion digest.
