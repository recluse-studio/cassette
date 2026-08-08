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
    status: DONE 2026-08-07 — repair b718da2 adds fail-closed append-only correction records for immutable published messages; full suite 20 passed in 27.37 seconds; ledger clean with 1,512 product LOC, 930 test LOC, 356 tool LOC, one process, one runtime, and the three existing exact dependency pins

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
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S09, S07]
    status: IN_PROGRESS 2026-08-08

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
    invariants: [Q5 acceptance (interrupt every transition, idempotent replay), Q6 acceptance (double issue, cancel every phase, typed failures, monotonic events), Q52 acceptance (the production acquisition state machine is unchanged across every source adapter)]
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
    invariants: [Q49 acceptance across every concrete operation phase - acquisition, compilation, inference prefill, inference decode, training, export, repair, and removal; matrix failure_rows injections x operations expanded from data; every simulable injection green]
    expected_size: medium
    done_when: full suite + ledger green; non-simulable injections enumerated for PHASE LIVE
    depends: [S10, S18, S20, S22]
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
    invariants: [matrix source_rows - actual Hugging Face, Ollama, and Tinker request/authentication/manifest/range wires from pinned revisions, ranged resume, digest pass, no fixture-only route, no internal model file]
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
