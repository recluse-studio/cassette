# PHASE LIVE runbook

S28 handed Cassette from deterministic machine proof to one live campaign with the principal
present. On 2026-09-02, before any live model write, the principal amended the storage eligibility
and capacity contracts. S28 remains historical machine evidence. L01.25 implements and proves the
amended Q53 behavior using fixtures only. L01.5 then qualifies physical storage paths under
Q39-Q44 with the principal present. L02 may move a live model byte only after both steps pass.
F4 selection and baseline metadata may establish the exact profile requests after L01.25 and before
the source-entry L01.5 gate; they make no live header request and move no model payload. Every live
row remains `NOT_RUN`.

IMPLEMENTATION.md contains four non-drive preparation stages, L01-L04, followed by six drive/live
stages, L05-L10. L01 is reopened for Q30 repair; its completed recovery proof remains retained.
Physical drive qualification and acquisition belong to L05, measured baselines to L06, F4 to L07,
F5 to L08, the full runtime matrix to L09 and clean replay to L10. These execution-stage numbers are
separate from the matrix phase labels used below. Consolidated preparation has no verified duration
estimate. Operation receipts remain evidence within their owning stage.

## Authority and identity

This runbook is a human-executable projection of `research/ACCEPTANCE_MATRIX.yaml`. The matrix
remains the release authority. The S26 and S28 artifacts record the superseded schema-version-4
machine baseline; they do not prove the 2026-09-02 amendments. If this runbook disagrees with the
current matrix, stop and correct the projection before touching a source account, model, or
physical drive.

| Record | Immutable identity |
|---|---|
| Acceptance matrix `cassette-first-complete-release`, schema version 5 | `blake3:6d909b678d85c17a900426a33b60b92b0616ecae5ef620ca4962d9116d860140` |
| Deferred-live projection, `s26-deferred-live-v4` | `blake3:21a64f61e1c68a444c6b8ef5903caf2d9451ad1ba652d33820fac3e0e4a19f6c` |
| Amended S26 machine fixture | `blake3:ef484712e4f2bca5c416632e765ddffd23de2f619c6fbd18f71def4c4559fa83` |
| S27 complete J report | `sha256:f53067994cfda7c568b2e02747bd470af6c45b9d1913008b00186017b5871200` |

The live claim is `DEFERRED_TO_PHASE_LIVE_NOT_RUN`. The matrix-declared deferral outcome is
`CONTRACT_AMENDMENT_REQUIRES_L01_25_MACHINE_PROOF`; the retained machine-baseline claim is
`PHASE_MACHINE_BASELINE_CONTRACT_AMENDMENT_PENDING`. Its exact prohibited-evidence labels are
`F4_PASS`, `F5_PASS`, `frontier_capability`, `hosted_comparison`, and
`physical_drive_performance`. Those labels require the live evidence named below.

The prior consolidated L01 run passed 315 tests and all twelve removal/bypass triples. A fresh
review then reproduced computed-import false passes under Q30, superseding its closure. The repaired
attempt must complete the suite, ledger and J proof before L02 becomes eligible. IMPLEMENTATION.md
retains the prior evidence and owns the new attempt.
The matrix retains its deferral declarations; every physical and real-model claim remains NOT_RUN.

## Coding time and independent verification

Active coding time and resume rules are owned by IMPLEMENTATION.md. Test runs, downloads,
compilation, training, physical measurements, review, evidence capture and waiting are outside
the agent coding budget. Keep their owner stage IN_PROGRESS until its required proof completes.
A long operation retains its durable receipt and recovery boundary; it does not require a new
build stage for each checkpoint or result.

Independent verification still recomputes every declared assertion from raw inputs. Use the
existing broker and store paths for live work, and resumable verification where the evidence
size requires it. Retain complete coverage and exact input identities. No timing limit permits
a sample, copied digest or partial result to replace the required proof.

## Campaign controls

Use one campaign directory on the candidate external cartridge during L01.5 and on the qualified
cartridge thereafter. Creating that directory is the first approved bounded L01.5 write and occurs
only after the protected-content inventory below. Record its path in the evidence manifest; do not
place model, dataset, optimizer, checkpoint, journal, prompt, output, or other model-bearing bytes on
internal storage. The checkout may retain Cassette source, non-model configuration, and redacted
evidence digests.

### Run cards and cartridge preservation

These controls govern live human approval and user-owned hardware. They add no product acceptance
row, but an action taken without them cannot supply usable live evidence.

Before a bounded live storage action, append one run card to an off-drive campaign control record.
After the campaign directory exists, mirror each card into its append-only campaign manifest. The
card records:

- the campaign ID, matrix row, operation, exact command or product entrypoint, and expected result;
- the physical disk identity, APFS volume UUID, current mount path, measured operation-plan profile
  identity, controller, enclosure, cable, port, and power state;
- one permission class: `READ_ONLY`, `CAMPAIGN_DIRECTORY_WRITE`, `PHYSICAL_FAULT`, or
  `DESTRUCTIVE`;
- the exact paths in scope, expected read and write behavior, stop conditions, and evidence paths;
- for each write-bearing atomic transition, Q53's observed available bytes `A_t`, exact next claim
  `E_n`, recovery boundary, active claims, and later observed growth or write amplification;
- health, temperature, host-write, device-write, and endurance readings that the hardware exposes;
  and
- the off-drive identity of the protected-content inventory described below.

Every write-bearing record binds the digest of its approved card. The principal either approves
that exact card in the record or the binding cites an earlier immutable general campaign approval
whose disk, root, permission, command class, byte-claim rule, and stop conditions contain it exactly.
An explicit `principal_action: none` never removes this lineage. Physical faults, path mutations,
destructive actions, and new permission classes always require a fresh cue.

Before the first write to a data-bearing drive, create an inventory outside that drive for every
pre-existing top-level entry. Record only its name, object type, and aggregate logical byte count,
then retain the identity of that inventory record. For a top-level folder, the aggregate count may
include its descendants, but the inventory records no descendants. It records no per-file hashes,
modification times, link targets, or recursive item list. Name and exclude volatile filesystem-owned
top-level paths such as Spotlight, trash, and filesystem-event data. Cassette writes only inside its
recorded campaign root and may never reclaim, rename, or replace pre-existing content. Recompute the
same coarse inventory after each bounded write campaign. An unexplained top-level addition, removal,
type change, or aggregate-byte change stops writes, preserves both inventories and the hardware
traces, and leaves the affected work `BLOCKED` unless a declared acceptance assertion itself failed,
in which case the owning row is `FAIL`. This benchmark detects broad size changes; it is not
content-integrity proof and cannot prove that physical wear or controller risk was absent.

General campaign approval covers only the recorded campaign root and ordinary operations. It does
not authorize formatting, erasure, repartitioning, filesystem repair, firmware changes, endurance
stress, or a physical fault injection. Each such action requires separate approval naming the exact
physical disk and action. A data-bearing drive may serve ordinary L01.5-L05 rows from a clean Cassette
campaign root; it need not be blank. Destructive and physical-fault rows use separately approved
hardware and never inherit authority from an ordinary campaign card.

Q53 has no fixed byte floor, device percentage, user ceiling, or whole-job reservation. Before each
atomic write transition, the controller measures current allocatable space, derives and claims only
the exact additional bytes needed to reach the next durable boundary and preserve recovery, then
remeasures before each write and after the boundary. A claim coordinates Cassette writers; it does
not reserve filesystem bytes against another macOS process. The controller may reclaim only
Cassette-owned objects that are unpinned, unreachable from every retained root, outside rollback
retention, declared `TEMPORARY` or `REPRODUCIBLE`, and unreferenced by an active claim, transaction,
or journal. If space changes after the claim or a write returns `ENOSPC`, recover the exact parent or
committed child and pause before another transition. Unknown future training output is not a
capacity failure.

When a live action fails, stop that action and preserve its card, raw trace, last valid state,
hardware state, and first decisive cause. Do not patch and continue inside the same evidence claim.
Classify the result, propose the bounded repair, and identify the proof that must rerun. A mechanism
change creates a governed machine revision and invalidates dependent live evidence; an F4 or F5
mechanism failure starts a new campaign after renewed L01.25 machine proof and affected L01.5
physical qualification. Independent rows may
continue only on a still-safe, separately approved physical path.

Seal execution evidence once. Use `lstat` without following links and accept only directories and
regular files whose link count is one. The recursive manifest lists every relative path, object
type, and regular-file content digest. An extra, missing, renamed, substituted, or type-changed path,
symbolic or hard link, socket, device, FIFO, or other special object fails exact namespace equality.
A review never writes into that sealed bundle. It writes a separate
review envelope that names the execution-bundle digest, source revision, assertion-set digest,
review lease, replay evidence, remediation lineage, and invalidation decision. A rerun reuses the
principal-approved action-card and cue-script template digests only when its physical scope,
permission, cues, and stop conditions are unchanged. It always records a new attempt binding with
fresh timestamps, observations, and operation IDs. It freshly records the source revision, which
may equal the prior attempt unless remediation requires a child. Fixture replay or a repair
commit never upgrades the failed attempt's evidence level or result.

A counted attempt always seals a bundle. If capture fails, seal every recoverable raw artifact, the
missing-item list, and the last valid operation state; mark the affected assertion `NOT_RUN`. A null
bundle means only that an uncounted preflight stopped before execution. A review lease is an atomic
create-or-compare-and-swap record keyed by stage, attempt, and execution-bundle digest. Its review
base must equal the execution revision. Preserve released, expired, abandoned, and succeeded lease
records; a successor names the prior lease digest. Review invalidation comes from the frozen
dependency graph and names every affected attempt, operation lineage, and physical qualification.
Reviews form an append-only history. Each twenty-minute review has its own ID, names the current
head as its prior envelope, records the lease-chain digest, and atomically compares and swaps that
head to its sealed envelope digest. A stale expected head or fork fails. A fifth incomplete review
returns to the queue. An accepted `REMEDIATED` envelope ends that attempt's review history; a new
attempt on the exact child is mandatory, so several forty-line repairs cannot accumulate against one
execution claim. A repaired verifier never changes the original attempt. It may create a separate replay
record only when every required raw byte was already sealed and no physical observation must be
repeated. Automatic remediation uses the versioned ledger diff counter, commits the isolated child
first, and runs every green probe, mutation, suite, and ledger check on that exact commit.

The dependency graph is an append-only chain under one atomic head. L26 proves the builder and emits
only a provisional preselection graph. POST-SELECTION-MACHINE-PASS seals the first execution-eligible post-F4-selection
revision; every later materializer names and atomically succeeds the current head before its records
can run. A successor preserves every inherited node, literal edge, evidence level, assertion owner,
permission binding, and terminal-state meaning byte-for-byte; it may add only materializer-authorized
nodes and edges. Any deletion, rewrite, or retargeting fails. Each attempt binds the active digest.
Invalidation uses the latest sealed successor whose ancestry contains that attempt digest. FINAL-PROVENANCE seals
the final source graph; Q80-MATERIALIZE preserves LIVE predecessor reachability through intermediate frozen nodes, binding their exact machine/reference proofs in Q80.

L01-L03 repair and close the amended baseline. L31 requires the
complete green machine gate, J reproduction and Q78 proof before physical participation.
POST-SELECTION-MACHINE-PASS refreshes the matrix/runbook identities and repeats the named
machine checks after F4 selection. Retained S26/S28 artifacts remain historical evidence.

For each live attempt retain the exact source, tree, lock, matrix, runbook, expansion and graph
identities with the approved templates, fresh operation ID, raw output and independent review.
Only complete qualifying evidence closes an assertion. Missing inputs remain NOT_RUN or BLOCKED.

## L01.25 — implement and prove adaptive capacity

First replace the superseded whole-operation reservation path with Q53's adaptive next-transition
controller, including a feasible next step that begins without whole-campaign fit. In separately named
machine-only records, remove storage-media, storage-class, connector, and nominal-capacity admission
gates from product code and generated schema inputs. Prove the claim, observation, safe reclamation,
pause, resume, and gate removal with deterministic machine fixtures. This step requires no principal
participation and may not inspect, mount, inventory, or write a physical drive; request a live source;
or move a model byte.

L01.25 passes only after L01-L31 establish the amended capacity and complete source, runtime,
compiler, training, endpoint and campaign paths. The final machine gate runs the full suite,
ledger, J and pre-live Q78 proof. Use the bootstrap machine-review profile while constructing
L27, then verify that frozen integrated candidate under the normal profile. L28-L31 and
POST-SELECTION-MACHINE-PASS use normal machine review. Physical proof begins afterward.

## L01.5 — qualify actual storage paths

With the principal present, qualify each actual locally attached APFS path for the operation it will
run:

- Apple classes: `c1_air_32`, `c2_max_128`, `c3_ultra_512`.
- Storage profile family: `external_apfs_measured`; every result binds the exact drive, operation,
  and plan.
- Governing qualification: `Q41-Q44`.
- Optional comparison profiles, when the matching hardware is available:
  `s1_usb4_nvme_2tb`, `s2_tb5_nvme_2tb`, and `s3_tb5_nvme_4tb_writable`.

Use the bound operation plan to select Q42 read and write sizes, alignments, access patterns, queue
depths, cold and warm states, cache-crossing behavior, write duty, and duration. Record p05, p50,
and p95 throughput; p50, p95, p99, and maximum latency; IOPS; host and device writes; flush latency;
errors; and thermal events. A writable training operation also requires endurance and health
evidence. Verify Q44 durable ordering through write, readback hash, `F_FULLFSYNC`, root publication,
atomic generation, a second `F_FULLFSYNC`, and remount.

Qualification is repeated for every exact drive, assembled path, Apple host, operation, and plan
used later. The initial L01.5 gate qualifies each selected model's header and acquisition plans plus
the Ollama plan before any payload moves. F4-COMPILE-PLAN/F5-COMPILE-PLAN qualify intended compilation plans only. After F4-CERTIFICATE/F5-CERTIFICATE publishes a verified certificate,
model_inference_qualification qualifies that exact F4/F5 runtime plan before any inference.
Execution rows likewise qualify preparation before PREPARE_START and the actual runtime after
PREPARE_VERIFY through RUN_QUALIFY_START/VERIFY. Training, execution, failure,
export, repair, and removal records each materialize their own exact profiles. A later concrete plan or path must revalidate its dependent Q42 subset
before that operation begins. Missing qualification blocks only that operation; changing a cable,
port, host, plan, or mechanism never inherits an earlier profile by name.

The source-entry L01.5 gate passes when L01.25, the inventory and campaign-root proof, and the exact
header, acquisition, and Ollama physical profiles pass. It then permits L02 header and payload work.
Later profile records retain the L01.5 label but gate only their exact consumer; they do not defer or
redefine the source-entry gate. A drive that fails one operation remains eligible for others. Media
type, connector, nominal capacity, optional reference profile, and advertised link rate cannot
substitute for or prevent measured qualification. L01.5 itself requests no live source and moves no
model byte.

## L02 — acquire immutable source material directly to cartridges

Satisfy the three required source rows in their dependency order. First select the exact F4 model
and immutable revision, amend the matrix, refresh the runbook identity, and repeat the machine gate
before any header or payload byte moves. Then freeze Q13/Q67 reference and candidate inputs and the executable workload manifests.
Source-entry profiles use the exact bounded header/acquisition wire plans and pass before source
headers or payload. Candidate measurement and native selection follow acquisition; teacher capture
then supplies the named compilation and comparison inputs. No certified inference plan is assumed
before compilation. This order is defined by the literal queue dependencies.

- `source_huggingface_all_immutable_models`
- `source_ollama_content_addressed_reimport`
- `source_tinker_export_reimport`

Lock and preserve these immutable model revisions:

| Model ID | Source locator | Revision |
|---|---|---|
| `kimi_k3` | `moonshotai/Kimi-K3` | `9f62e4e9fffbd0a83ddd60e1c209d828994b3569` |
| `llama_4_scout` | `meta-llama/Llama-4-Scout-17B-16E-Instruct` | `92f3b1597a195b523d8d9e5700e57e4fbb8f20d3` |
| `qwen3_235b_a22b` | `Qwen/Qwen3-235B-A22B-Instruct-2507` | `ac9c66cc9b46af7306746a9250f23d47083d689e` |

First run the immutable Hugging Face acquisitions and the Scout-backed Ollama re-import through the
production acquisition state machine. For Hugging Face, prove the actual resolve, authentication, license, manifest, metadata, and range
wires; admit each exact Q53 transfer step; interrupt and resume ranged acquisition; verify the
immutable source and final local digests; and retain no internal model file. For Ollama, re-expose
the pinned Scout revision through content-addressed manifests and blobs while preserving semantic
identity. Later, run the Tinker derivative row. It remains an L02-labelled source obligation, but its input is a Q70 child and
therefore runs only after the dense F4 Tier-A child passes. It must finish before Q80; it does not
block entry to F4 or F5. Export and re-import that child while preserving weights, parent, and
training provenance. A loopback fixture route cannot satisfy L02.

Acquire the selected permissively licensed 3–8B dense F4 model directly to the qualified external
cartridge during this step. Record its immutable revision and license evidence before any model
byte moves. The immutable Hugging Face and Ollama source obligations must have exact digest closure
before their consumers run. The derivative Tinker obligation closes later under its explicit Q70
precondition. No source row is waived or replaced.

Every header audit has its own bounded record. Native candidates and remote workload datasets
have explicit source-acquisition dependencies under the same qualification and containment rules. Every Hugging Face, F4, Ollama, and Tinker transfer
has separate start and terminal-verification records. A transfer start depends on its exact passing
physical profile and header audit; a verify record binds the same logical operation started by its
matching start.

## L03 — run the F4 and F5 falsification gates in order

Run `f4_gate` first on the matrix class `3-8B dense, permissive license`. Its compiled revision
must cover the frozen Q15/Q16 conditions, independently recompute every Q19 atom, rank, resource,
error, risk, and horizon field, complete `train_dense_fixture_tier_a` and
`train_dense_fixture_tier_b`, touch no more than one quarter of native active bytes per token, and
achieve `lower95CI(Qc/Q_teacher) >= 0.95` in every Q15 stratum inside the predeclared training
budget.

Each F4 or F5 compilation `START` record prints and receives approval for its exact
`CAMPAIGN_DIRECTORY_WRITE` card before it creates the first durable boundary. Its later `VERIFY`
record performs no new principal action.

After F4 passes, run `f5_gate` on the pinned `llama_4_scout` revision
`92f3b1597a195b523d8d9e5700e57e4fbb8f20d3`, which supplies the matrix class `20-120B sparse`.
It must pass the F4 predicates at scale,
complete `train_sparse_fixture_tier_a` and `train_sparse_fixture_tier_b`, and emit Q37
mathematical-resource-versus-quality/service curves whose predicted feasible point clears Q68
`FRONTIER_CLASS` inside the E-011 C1 decode budget.

If either gate fails, preserve the raw result, set the gate row to `FAIL` with
`Q38_FALSIFIED`, emit the exact Q38 record, and refuse its frontier compiled dependents and L05.
Independent Scout, Qwen, and native-teacher rows may continue only when their own prerequisites and
physical paths remain valid. Repairing the failed mechanism creates a governed machine revision,
repeats its required L01.25 machine proof and affected L01.5 qualification, and begins a new live
campaign for invalidated work. L03 passes only when both gates have live `PASS` evidence in order.

## L04 — execute every remaining matrix row

### Execution and workloads

Run all five execution rows against their exact model, Apple, storage, mode, context, and gate
tier:

- `exec_c1_frontier_compiled`
- `exec_c1_scout_least_invasive`
- `exec_c2_qwen_least_invasive`
- `exec_c3_k3_native_teacher`
- `exec_c3_k3_compiled_portability`

For each row, `QUALIFY_START`, `PREPARE_START`, and `RUN_START` bind separate exact cards.
Preparation may include full F6 compilation. RUN_QUALIFY_START/VERIFY then measures the actual
prepared runtime plan; it cannot inherit the preparation profile.
The corresponding verify records require no new action unless their sealed template says otherwise.

For each row, execute `capability_complete_q16` and `sustained_q48`. The capability suite includes
ordinary warm and cold requests, reasoning, coding with executable tests, tool round trips,
structured output, multi-turn state, declared context boundaries, declared modalities,
cancellation, and recovery. The sustained suite runs for at least 120 minutes and 20,000 generated
tokens and must keep every post-warmup window inside the row's gate tier with throughput decay at
or below 10 percent and no integrity error.

The C1 frontier row requires Q68 usability floors, value against `b_native_c1`, position against
`b_teacher`, Q18 capacity proof, an independently recomputed Q19 certificate, and the complete
honesty vector. Scout and Qwen use only Q40 modes 1–3 and require floors plus the Q17 parity tier;
if none passes, record the row failure under Q38 rather than advancing to compiled mode. The C3
native K3 row is `TEACHER_CORRECTNESS`; it may emit no `FRONTIER_CLASS`, `PARITY`, or
`NEAR_LABORATORY` label. The C3 compiled K3 row must use the same cartridge pages as the C1 row
without weight duplication and must pass its Q19, Q18, portability, and usability obligations.

### Protocol cross-product

Run `every_execution_row_every_named_agent` over every execution row and each client: `codex`,
`ollama`, `openclaw`, `hermes`, and `custom`. Retain discovery and negotiation, text streaming,
reasoning where declared, tool calls and results, structured output where declared, cancellation,
typed error, and status traces. Each mapping must pass Q76 bidirectional conformance and Q77 stable
capability identity without fabricating an unsupported feature.

### Training rows

Run every required training row:

- `train_c1_frontier_tier_a`
- `train_c1_frontier_tier_b`
- `train_c1_scout_tier_a`
- `train_c3_frontier_tier_a`
- `train_c3_frontier_tier_b`
- `train_dense_fixture_tier_a`
- `train_dense_fixture_tier_b`
- `train_sparse_fixture_tier_a`
- `train_sparse_fixture_tier_b`

Each row must pass Q23 placement, Q25 interruption and resume, Q28 physical-write metering, Q53
adaptive capacity control at every durable unit, Q70 quality, Q71 dataflow, Q72 optimizer
equivalence, Q73 atomic child
publication, Q74 endurance admission, named-client callability, and the Tier-B invalidation and
clean-derivation requirements where applicable.

### Training thermal proof

The training_thermal family gives every declared training operation and exact host/drive/plan a
PLAN, qualification, START and VERIFY. PLAN freezes the Q48 duty experiment before the normal
TRAIN run. An exact qualifying interval from that run may be reused only with complete raw proof;
otherwise the dedicated thermal START runs the same production training path. Every required
interval lasts at least 120 minutes and writes at least twice the evidence-based SLC cache estimate,
with above/below-duty-cycle evidence on each applicable Apple class and the unchanged Q74 endurance
admission. Unknown mandatory cache evidence blocks the volume claim. An evidenced absence of SLC cache may
produce a zero SLC estimate; the complete duration, duty-cycle and service proof still applies.
TRAINING-THERMAL-ALL-PASS is required before FINAL-PROVENANCE and its producers belong in Q80 replay.

Every inference, training, protocol and sustained operation keeps external networking disabled
from activation through terminal evidence capture. Overlapping operations hold separate leases;
restore networking only after the last lease closes under its exact cue. Training START capture
never restores access while the job remains active. A missing interval requires a new attempt.

### Live failure rows

Expand every live injection across acquisition, compilation, inference prefill, inference decode,
training, export, repair, and removal:

- `cartridge_disconnect`
- `reconnect_same_identity`
- `reconnect_wrong_identity`
- `sleep_wake`
- `bus_reset`
- `port_migration`
- `readonly_remount`
- `insufficient_capacity_before_start`
- `insufficient_capacity_during_candidate_write`
- `source_revision_change_during_transfer`

Before any coordinate runs, `FAILURE-MATERIALIZE` resolves the eight operation subjects and source
artifacts, creates the eight starting profile requests, expands exactly eighty coordinates, and
extends the graph with 320 base records plus the 112 requalification records fixed below.

Every coordinate uses the operation subject and source artifact fixed in the matrix, creates a
fresh logical operation, and binds one exact starting physical profile. Its `ARM` record receives
an exact ordinary write card before creating the durable pre-injection boundary. It has separate arm,
injection, recovery, and verification records. ARM holds the exact active failure locus until
INJECT; the latter verifies the same operation and barrier before issuing its cue. An idle, terminal
or wrong-boundary operation cannot satisfy an in-flight fault assertion. The matrix deterministically adds requalification
start and verify records for disconnect, either reconnect, sleep/wake, bus reset, port migration,
and read-only remount; it omits both for the two capacity injections and source-revision change. No
runtime observation may alter that graph. A changed drive, cable, port, host, path, plan, or
mechanism still blocks resumed I/O until the declared profile passes. Every coordinate must preserve no partial callable revision, the exact typed error, parent or exact
child recovery, no stale handle use, no uncommitted token, and no internal model file.

Each disconnect, same-identity reconnect, wrong-identity reconnect, sleep/wake, bus reset, or port
migration session requires a separate `PHYSICAL_FAULT` card naming the exact physical disk and
action. Read-only remount, capacity-filler, and source-revision-change sessions require their own
bounded path-specific cards. Corruption, interruption, and every other agent-executed injection also
requires an approved card naming the exact disk, path, byte or state bound, and stop conditions. A
general campaign card authorizes none of those actions.

### Offline and privacy rows

Run `offline_inference_all_execution_rows` over every execution row and
`offline_training_all_training_rows` over every declared operation of every training row with
external network disabled and
only the declared loopback agent protocol available. Retain process, socket, file-open, file-write,
credential, prompt/output persistence, source identity, page identity, and internal-volume traces.
Any remote model or gradient request, DNS or external socket, internal full checkpoint, secret
serialization, or undeclared persistence fails the owning row.

L04 runtime work passes only after both F4 and F5 are `PASS` and every expanded workload, protocol,
training, failure, offline, and privacy row has live `PASS` evidence. Then run the final Q79 proof
and the second Q78 exact-accounting checkpoint; those results close L04 before Q80. Preserve a failed row and its independent rows; do not
replace the failed result with a simulator or a smaller model.

## L05 — execute Q80 from clean roots

Start from the clean source revision and clean Cassette campaign roots on qualified APFS external
drives. Preserve and recheck the off-drive inventory of any pre-existing content. Materialize one
flat replay record for every LIVE product/physical node in the full prerequisite closure of all
required matrix and supplemental terminal owners plus FINAL-PROVENANCE. Traverse intermediate nodes of every
evidence level first. Freeze declared machine and REFERENCE_ONLY records as exact input bindings,
and preserve precedence between retained LIVE nodes across excluded intermediate nodes. Missing
producer, owner, reference binding or either Q78 checkpoint rejects expansion. Include the new
checkpoint, verification-work and training-thermal producers. Record exact source/replay counts,
contracted edges and graph digests; all must reproduce.
Re-run those records through production paths, preserving all raw traces and
immutable evidence IDs. Each L05 matrix-phase receipt binds its exact principal actions. These receipts remain within L37. Re-run the complete Python suite and
ledger, reproduce Q78 exact accounting, and complete Q79. Final closure performs no hidden long job.

Compute the completion digest only when every required expanded row is `PASS` and `LIVE_PROVEN`,
both fixture gates passed before any frontier compiled row ran, every compiled row carries an
independently recomputable Q19 certificate, Q78 and Q79 pass, and no required runtime result came
from a remote model or personal-device anecdote. The digest preimage must include the source
revision, lockfile, acceptance matrix, runbook, model revisions, hardware profiles, row outcomes,
raw-evidence identities, and exact row expansion.

If one required row is `NOT_RUN`, `BLOCKED`, `SKIPPED`, `SUBSTITUTED`, `SIMULATED`, `REMOTE`, or
`FAIL`, `research/ACCEPTANCE_MATRIX.yaml` must not set `result.status: PASS`. Use the exact campaign
status above: `INCOMPLETE`, `FAIL`, or `BLOCKED` once qualifying live work has begun and no operation
is active; use `RUNNING` while one is active. Retain the non-passing campaign outcome in its sealed evidence bundle. Only a
complete, reproducible live campaign may set the matrix result to `PASS` and attach its completion
digest and evidence bundle.

## Campaign close

Record the final worktree, source revision, cartridge identities, active processes, mounts, free
space, row-status summary, evidence-bundle identity, and completion digest or exact blocking rows.
Close agent-created servers, test runners, browser sessions, temporary mounts, and other campaign
environments. Preserve source cartridges, accepted evidence, and user-owned hardware state; delete
only agent-created temporary artifacts whose evidentiary purpose has ended.
