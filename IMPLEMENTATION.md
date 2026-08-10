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
    invariants: [Q57 acceptance (SafeTensors import, relocate without logical change, span resolution) on scratch cartridge images]
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
    acceptance_boundary: "S08 proves the shared Q49 lifecycle authority and APFS-image fixture against the store operations available at this step. Q49's injection at every concrete operation phase remains open for acquisition, compilation, inference prefill, inference decode, training, export, repair, and removal; S23 owns that matrix expansion after those operations exist."
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
    dependency_admission: "mlx==0.31.0 at release commit 365d6f29b47686a9f5401f6a9ec5825fee162d69; subset: core/fast operators, explicit-key categorical sampling, autograd, and SGD; serves Q30. Its Darwin wheel supplies the existing Metal kernels that replace every Cassette numerical kernel."
    invariants: [Q30 acceptance (golden tensors per dispatched dtype/shape/operator against reference), Q33/Q40 acceptance (generated bounded schema represents every MATHS.md certificate dimension without executable or model-specific payload), F2 valid/malformed certificate and golden-operator fixtures; mlx confinement check in ledger]
    acceptance_boundary: "S12 proves bounded generated schemas, exact membership in the generated Q30 dispatch, and faithful execution of the ten declared golden MLX operator/dtype/shape rows. S12 does not prove that an independently supplied certificate is mathematically true or internally reconciled with source evidence. S13 owns independent recomputation from canonical source evidence and rejection of contradictory certificate claims."
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S03, S01]
    historical_status: "DONE 2026-08-09 — original step 73997e0; platform-gate repair 26a0913; complete macOS suite 28 passed in 46.17 seconds with no skips; synthetic Linux gate skipped before MLX or pager import; ledger clean with 2,813 product LOC, 2,136 test LOC, 406 tool LOC, 74 generated LOC, one process, one Python runtime, and five exact dependency pins"
    status: DONE 2026-08-09 — audit remediation 306055ddefb4e5d5a735c3dc5e4ae6e09b7d57c0 parses real Mach-O dependencies, binds generated certificate dimensions to MATHS.md, supplies the complete isolated proof command, states S12's structural/execution boundary, preserves S13 as the next TODO, and assigns deferred Q55/Q30 work to S19/S24; focused S03 and S12 fixtures passed 4/4 and 3/3, the complete macOS suite passed 28/28 in 1,024.50 seconds with no platform skips, and the ledger remained clean
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
    files: [pager.py]
    invariants: [F3 stage gates (one exact description and one fresh-residual-sampling description, forced page failures, seeded reproduction, KV rollback), Q19 certificate remains valid across the declared trace horizon, Q63 acceptance (trace equals certified schedule, no hidden allocation or traffic)]
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S14, S05]
    status: TODO

  - id: S16
    title: Canonical broker
    env: any
    files: [broker.py]
    invariants: [Q5 acceptance (interrupt every transition, idempotent replay), Q6 acceptance (double issue, cancel every phase, typed failures, monotonic events), Q52 acceptance (the production acquisition state machine is unchanged across every source adapter)]
    acceptance_boundary: "SOURCE_VERIFIED records that Q51 completed successfully; it does not make the source bytes callable or prove their present contents. The broker may advance toward PUBLISHED only after the owning preparation operation returns current-byte verification and a verified canonical root. The broker never reads source extents or treats PartialState as that verification."
    expected_size: large
    done_when: full suite + ledger green
    depends: [S03, S07, S10]
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
    title: Streaming compiler, contribution map, and mathematical certificate
    env: macos
    files: [compiler.py]
    invariants: [Q4 acceptance (peak-extent instrumentation, interruption, resume), Q19/Q40 acceptance (derive immutable condition metrics, atom witnesses, service faces, cover, observation contract, descriptions/residuals, execution-risk and composition certificate from canonical inputs), Q30 source-driven tuple inventory (discover required tensor dtypes, operator signatures, shapes, and parameters from verified model material; expand only generated dispatch data or terminate with UNSUPPORTED_OPERATOR without fallback), Q55 executable-material containment (reject malicious pickle, templates, path traversal, auto-map/custom-code declarations, native libraries, and custom operators before code execution, network access, credential access, or unsafe loading), Q58 acceptance (total source-to-atom/description/residual map, structural failure on omission or detached certificate relation), Q60 resume on small dense model, Q51/Q60 source-consumption boundary (recompute each immutable source object's authoritative whole digest on the same reads used by compilation and reject changed completed extents before candidate-root publication), Q62 publication guard (verify canonical pages, mathematical certificate, and candidate root before generation publication)]
    acceptance_boundary: "PartialState and its mutable chunk records locate resumable work but do not authorize present bytes. S19 is the first consumer of attacker-controlled model material as executable structure, so it owns Q55 containment before any parser, loader, compiler action, network request, or credential lookup can honor that material. It inventories the model's required Q30 tuples from verified source evidence; an absent tuple is a typed refusal, not a private kernel or silent fallback. Compilation hashes each complete source object while consuming it, compares the result with immutable Q1/Q9 evidence before publication, and emits no root when the extent changed after transfer completion. This is not a separate post-completion transfer reread: the compiler hashes the bytes it must already read. After canonical publication, Q62 owns at-rest verification."
    expected_size: large
    done_when: full suite + ledger green
    depends: [S05, S06, S10, S12]
    status: TODO

  - id: S20
    title: Certified hardware plans and mathematical invalidation graph
    env: any
    files: [compiler.py]
    invariants: [Q11/Q59 acceptance (plan switch over one certificate, zero weight payload in plans, exact description/metadata/fresh-traffic budgets), Q27/Q61/Q75 acceptance (exact invalidation closure for condition metrics, atoms, cover, observation, description, residual estimator, composition, precision, and semantic changes)]
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S19]
    status: TODO

  - id: S21
    title: Trainer - paged Tier A and compiled-certificate Tier B
    env: macos
    files: [trainer.py]
    invariants: [Q21/Q70 Tier-A operations on frozen cartridge pages, Q21/Q70 Tier-B recovery operations over immutable condition/atom/description/estimator/observation/precision calibration records, Q71 acceptance (tensor lifetime trace), Q72 acceptance (paged vs unpaged equivalence), Q73 child commit, Q25 interrupt/resume bit-exact, Q23 placement trace; Tier-B output is a committed training artifact consumed through store and broker, never a trainer-owned certificate]
    expected_size: large
    done_when: full suite + ledger green
    depends: [S15, S06, S20]
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
    invariants: [Q49 acceptance across every concrete operation phase - acquisition, compilation, inference prefill, inference decode, training, export, repair, and removal; matrix failure_rows injections x operations expanded from data; every simulable injection green]
    expected_size: medium
    done_when: full suite + ledger green; non-simulable injections enumerated for PHASE LIVE
    depends: [S10, S18, S20, S22]
    status: TODO

  - id: S24
    title: F4 protected-condition, metric, and teacher capture
    env: macos
    files: [compiler.py, tools/ (analysis, generated)]
    invariants: [Q40 immutable teacher trace capture on a permissively licensed 3-8B dense model (agent downloads via sources.py), Q18 protected condition/test-law construction including rare and off-support cases, Q19 condition-metric and compatibility-certificate input generation, Q30 representative-model expansion (execute and re-golden every source-discovered operator/dtype/shape tuple through generated dispatch against the real 3-8B model; unsupported tuples terminate without fallback), Q51-to-Q58 integration (change one completed source byte after S10 returns and require S19 to reject it against the immutable whole-object digest before trace or root emission; preserve the clean path without a separate transfer reread)]
    expected_size: medium
    done_when: full suite + ledger green; trace corpus committed by digest
    depends: [S19, S10]
    status: TODO

  - id: S25
    title: F4 certified compile and resource-frontier replay
    env: macos
    files: [compiler.py, tools/ (simulator, generated)]
    invariants: [Q19-certified 3-8B revision built end-to-end; every protected condition covered or causally excluded; exact and fresh-stochastic paths replay under their declared contracts; Q70 Tier-A training completes on the dense fixture; Q70 Tier-B recovery consumes S21's committed calibration artifacts, regenerates every invalidated condition/atom/description/estimator/observation/precision witness, publishes one Q73 child, and matches a clean certificate derivation; Q37 curves emitted over atom count, rank, peak and total description/metadata bytes, peak and total fresh traffic, composed execution error/risk, horizon, quality, and service against recorded storage-class profiles]
    expected_size: large
    done_when: full suite + ledger green; curves committed
    depends: [S24, S20, S21]
    status: TODO

  - id: S26
    title: F4 GATE evaluation
    env: macos
    files: []
    invariants: [Q36 F4 GATE - train_dense_fixture_tier_a and train_dense_fixture_tier_b both PASS, complete independently recomputed Q19 certificate over the frozen protected set, touched_bytes<=0.25*native_active, declared execution risk passes, and paired lower95CI(Qc/Q_teacher)>=0.95 within the predeclared training budget]
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
    invariants: [matrix source_rows - actual Hugging Face, Ollama, and Tinker request/authentication/manifest/range wires from pinned revisions, ranged resume, digest pass, no fixture-only route, no internal model file]
    depends: [L01]
    status: TODO
  - id: L03
    title: F5 at 20-120B and F5 GATE
    env: macos+hardware
    invariants: [Q36 F5 GATE - train_sparse_fixture_tier_a and train_sparse_fixture_tier_b both PASS, Q19 predicates and peak/total resources at scale, Tier-B recovery regenerated every invalidated witness, Q37 predicted frontier point vs E-011 budget; PASS or Q38-FALSIFIED recorded]
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
