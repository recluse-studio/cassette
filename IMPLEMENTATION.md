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
    status: DONE 2026-08-06 — step commit 8cf0d10; R1 repair d763d74; R2 repair 3958650; final S01 hardening a89a3ec and closure repair bc1453b (exact assertion authorities, fail-closed Git evidence, anchored commit fields, isolated boundary fixtures); fresh-context review clean; suite 11 passed, ledger clean; pins pytest==9.1.1 / python ==3.13.* (revisit recorded at S06)

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
    invariants: [Q62 acceptance (corrupt page/index/root/parity), Q53 acceptance (exact-boundary and fragmented reservation)]
    expected_size: medium
    done_when: full suite + ledger green
    depends: [S06]
    status: DONE 2026-08-07 — step commit 66af96f; committed clean-clone suite 20 passed in 27.74 seconds; ledger clean with 1,475 product LOC, 787 test LOC, 324 tool LOC, one process, one runtime, the three existing exact dependency pins, and no violation
    closeout:
      - clause: "Q53 exact-boundary capacity admission"
        test_or_probe: "tests/test_s07_integrity_capacity.py::test_q53_exact_boundary_and_fragmented_reservation"
        input: "Reserve one operation on a 200 GiB device with committed=23 bytes, inflight=41 bytes, candidate=59 bytes, repair=1 GiB, allocatable verified free bytes equal to the exact requirement, and one exact-extent preallocator."
        expected: "Use checked unsigned arithmetic; compute safety as max(8 GiB, 5% of device bytes); admit equality only after preallocating the complete required extent."
        observed: "The phase total was 1,073,741,947 bytes, safety was 10,737,418,240 bytes, and the sole preallocation request was the exact 11,811,160,187-byte requirement. Equality admitted the operation."
      - clause: "Q53 fragmented and overflowing reservation fails before transfer or mutation"
        test_or_probe: "tests/test_s07_integrity_capacity.py::test_q53_exact_boundary_and_fragmented_reservation"
        input: "Offer the same 11,811,160,187 verified free bytes as fragments of 11,811,160,186 and 1 byte, then separately add 1 to the maximum unsigned 64-bit phase value while supplying an allocator that records any call."
        expected: "Reject verified free space that cannot furnish the required extent; reject arithmetic overflow before preallocation, transfer, or model mutation."
        observed: "Both cases returned CAPACITY_EXCEEDED. The fragmented case named failed preallocation; the overflow case named unsigned 64-bit arithmetic and never called the allocator. The sentinel model bytes remained unchanged."
      - clause: "Q53 repair-set admission precedes repair-object mutation"
        test_or_probe: "the insufficient and exact repair reservations in tests/test_s07_integrity_capacity.py::test_q62_corrupt_page_index_root_and_parity_repair"
        input: "Attempt repair-set creation first with one repair byte, then with 1 GiB, for a two-page root whose exact root replica, index replica, parity object, and canonical repair manifest total 4,162 bytes."
        expected: "Write no repair path unless the completed reservation covers every repair-set byte; admit the exact object set under the sufficient reservation."
        observed: "The one-byte repair phase returned CAPACITY_EXCEEDED before the repair directory existed. The 1 GiB phase admitted one 4,162-byte immutable repair set with root blake3:3b021143f70becbf1b7d59ce4586b9d908b01840800a3cbd0e7305673c8ccbd2 and index blake3:05173b67ff0af5f9acfbd19449d5b6ba4bcb289733ba62aa83f02952fc06ca92."
      - clause: "Q62 corrupt page detection, quarantine, parity repair, and exact digest restoration"
        test_or_probe: "the page phases of tests/test_s07_integrity_capacity.py::test_q62_corrupt_page_index_root_and_parity_repair"
        input: "Flip one byte inside page blake3:149d80aea7939e97b857b058b5e0efa787e6afc78c6468285d32b5fa62b9da74, attempt tensor use, verify without mutation, reject an insufficient replacement reservation, then repair from declared parity and its verified peer page."
        expected: "Detection precedes use; integrity moves VALID to SUSPECT to VERIFYING to CORRUPT, then through REPAIRING to VALID only after new immutable bytes match the original digest; a failed reservation changes no corrupt byte."
        observed: "The tensor read returned PAGE_CORRUPT before yielding bytes. Verification named only the exact page. The insufficient repair left the corrupt segment byte-identical. The admitted repair quarantined the corrupt object, restored the exact 37-byte segment digest blake3:d0d04c23dde3e5239ea24446bf3e410afafa6377f85443e3979b962536e0c487, and returned b'alpha-page-contents'."
      - clause: "Q62 corrupt index repair"
        test_or_probe: "the index phase of tests/test_s07_integrity_capacity.py::test_q62_corrupt_page_index_root_and_parity_repair"
        input: "Flip one byte in the live fixed-record index, attempt root loading, and repair from the verified immutable index replica."
        expected: "Reject the index before root use; follow the declared integrity states; restore bytes whose digest equals the recorded index digest."
        observed: "Root loading returned ROOT_INVALID. Repair traversed SUSPECT, VERIFYING, CORRUPT, REPAIRING, and VALID; the restored index matched its original bytes and blake3:05173b67ff0af5f9acfbd19449d5b6ba4bcb289733ba62aa83f02952fc06ca92."
      - clause: "Q62 corrupt root repair"
        test_or_probe: "the root phase of tests/test_s07_integrity_capacity.py::test_q62_corrupt_page_index_root_and_parity_repair"
        input: "Flip one byte in the live canonical root, attempt root loading, and repair from the verified immutable root replica."
        expected: "Reject the root before use; follow the declared integrity states; restore canonical bytes whose digest equals the original root identity."
        observed: "Root loading returned ROOT_INVALID. Repair traversed SUSPECT, VERIFYING, CORRUPT, REPAIRING, and VALID; the restored bytes matched root blake3:3b021143f70becbf1b7d59ce4586b9d908b01840800a3cbd0e7305673c8ccbd2 and decoded to the original root."
      - clause: "Q62 corrupt parity repair"
        test_or_probe: "the parity phase of tests/test_s07_integrity_capacity.py::test_q62_corrupt_page_index_root_and_parity_repair"
        input: "Flip one byte in parity object blake3:2ab7f6d5ecb853c570c04c20a59b15c88d8b755125b8fde9128a168e025fa9fd while both source pages remain valid, verify the revision, and repair parity from those pages."
        expected: "A corrupt optional parity object does not make valid model pages unavailable, but repair traverses the declared states and restores the declared parity digest."
        observed: "Verification kept the revision available and marked the parity object CORRUPT. Repair traversed SUSPECT, VERIFYING, CORRUPT, REPAIRING, and VALID, then reproduced the original parity bytes and digest."
      - clause: "Q62 unrecoverable page blocks affected runs with its exact identity"
        test_or_probe: "the simultaneous page/parity and verified-source phases of tests/test_s07_integrity_capacity.py::test_q62_corrupt_page_index_root_and_parity_repair"
        input: "Corrupt the alpha page and its sole parity object together, attempt repair and run admission, then supply the exact alpha payload as a digest-verified source page and repair again."
        expected: "When local copy, verified source, and parity cannot produce the page, end at UNAVAILABLE and reject new use with its exact page ID. Once a higher-order source supplies exact bytes, restore the page and parity without changing logical identity."
        observed: "Repair returned unavailable_pages containing only blake3:149d80aea7939e97b857b058b5e0efa787e6afc78c6468285d32b5fa62b9da74. Run admission returned PAGE_CORRUPT with object_id page:blake3:149d80aea7939e97b857b058b5e0efa787e6afc78c6468285d32b5fa62b9da74. The verified source then restored b'alpha-page-contents', the original parity digest, and the unchanged root."

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
