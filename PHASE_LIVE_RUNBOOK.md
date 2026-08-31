# PHASE LIVE runbook

S28 hands Cassette from deterministic machine proof to one live campaign with the principal
present. The campaign begins only after the S28 close commit recorded in `IMPLEMENTATION.md`; until
then, every live row remains `NOT_RUN`.

## Authority and identity

This runbook is a human-executable projection of `research/ACCEPTANCE_MATRIX.yaml` through the
matrix-bound deferred manifest at `tests/fixtures/s26_deferred_live_rows.json`. The matrix remains
the release authority. If this runbook disagrees with the matrix, stop and regenerate the runbook
from the matrix before touching a source account, model, or physical drive.

| Record | Immutable identity |
|---|---|
| Acceptance matrix `cassette-first-complete-release`, schema version 4 | `blake3:372ddc5da3c64fd837bc95c2a0bca8a5aecc5d47862a1bf306f9f807dbde34c4` |
| S26 deferred-live projection, `s26-deferred-live-v2` | `blake3:23d9e57572d0580e0626fd958b89f0e600f8dfdfac93f41897375a29ad82adcf` |
| S26 machine gate | `blake3:f7c9a1e53346eef5053fc3b759e1f8236a5cae14ce4486f1806fa9a0a5d2a9d7` |
| S27 complete J report | `sha256:a59b5b975fbbdb34df13aafa8a9a2d8d2e283331b307746fbd2d0c35a65dd4a3` |

The machine claim is `DEFERRED_TO_PHASE_LIVE_NOT_RUN`, and its outcome is
`READY_FOR_LIVE_FALSIFICATION_ONLY`. Its exact prohibited-evidence labels are `F4_PASS`, `F5_PASS`,
`frontier_capability`, `hosted_comparison`, and `physical_drive_performance`. Those labels require
the live evidence named below.

## Campaign controls

Use one campaign directory on a qualified external cartridge. Record its path in the evidence
manifest; do not place model, dataset, optimizer, checkpoint, journal, prompt, output, or other
model-bearing bytes on internal storage. The checkout may retain Cassette source, non-model
configuration, and redacted evidence digests.

Before L01, perform these checks and retain their raw output:

1. Check out the S28 close commit named in `IMPLEMENTATION.md`, verify a clean worktree, and record
   the exact commit and lockfile digest.
2. Run `.venv/bin/python -B -m pytest -q -p no:cacheprovider` and
   `.venv/bin/python tools/ledger.py`. Both must pass before live evidence can attach to the source
   revision.
3. Verify that the acceptance matrix and the three retained machine artifacts match the identities
   above. A mismatch invalidates this runbook.
4. Record the principal's presence and authorization for each source account, Apple machine, and
   physical cartridge used in the campaign. Account credentials remain opaque references and must
   not enter cartridge metadata, logs, or evidence payloads.
5. Record the Apple class, OS build, physical cartridge identity, filesystem, transport path,
   controller, bridge, enclosure, cable, port, capacity, health telemetry, power state, and free
   capacity. Do not infer a storage class from a connector or product name.
6. Check free space on the system data volume. If it is below 10 percent, stop growth, close the
   campaign processes, and choose a lower-internal-storage route before continuing.

Create one append-only campaign manifest containing the campaign ID, source commit, dependency
lock, matrix identity, runbook identity, principal-presence record, clocks and time zone, Apple and
storage profile identities, model identities, baseline identities, operation IDs, evidence paths,
row status, and terminal completion digest. Every raw trace must resolve from that manifest.

Use only these row states: `NOT_RUN`, `RUNNING`, `PASS`, `FAIL`, or `BLOCKED`. `PASS` requires the
row's declared live evidence. `SIMULATED`, `REMOTE`, `SUBSTITUTED`, and `SKIPPED` cannot satisfy a
required row.

## L01 — qualify the physical storage paths

Qualify the three matrix storage classes against the Apple classes used by later rows:

- Apple classes: `c1_air_32`, `c2_max_128`, `c3_ultra_512`.
- Storage classes: `s1_usb4_nvme_2tb`, `s2_tb5_nvme_2tb`,
  `s3_tb5_nvme_4tb_writable`.
- Governing qualification: `Q41-Q44`.

For each assembled path, run the Q42 read and write sizes, alignments, sequential and random
patterns, Q19 trace pattern, queue depths, cold and warm states, cache-exhaustion interval, and
sustained interval. Record p05, p50, and p95 throughput; p50, p95, p99, and maximum latency; IOPS;
host and device writes; flush latency; errors; and thermal events. Writable classes also require
endurance and health evidence. Verify Q44 durable ordering through write, readback hash,
`F_FULLFSYNC`, root publication, atomic generation, a second `F_FULLFSYNC`, and remount.

L01 passes only when every profile required by the later execution and training rows has a
content-addressed measured profile, its p05 and p99 values satisfy the bound plan for the full
sustained interval, and writable paths pass the durability and endurance predicates. Record a
failed assembled path as a Q38 tuple failure; do not replace measured values with advertised link
rates.

## L02 — acquire immutable source material directly to cartridges

Run the three required source rows through the production acquisition state machine:

- `source_huggingface_all_immutable_models`
- `source_ollama_content_addressed_reimport`
- `source_tinker_export_reimport`

Lock and preserve these immutable model revisions:

| Model ID | Source locator | Revision |
|---|---|---|
| `kimi_k3` | `moonshotai/Kimi-K3` | `9f62e4e9fffbd0a83ddd60e1c209d828994b3569` |
| `llama_4_scout` | `meta-llama/Llama-4-Scout-17B-16E-Instruct` | `92f3b1597a195b523d8d9e5700e57e4fbb8f20d3` |
| `qwen3_235b_a22b` | `Qwen/Qwen3-235B-A22B-Instruct-2507` | `ac9c66cc9b46af7306746a9250f23d47083d689e` |

For Hugging Face, prove the actual resolve, authentication, license, manifest, metadata, and range
wires; admit exact capacity before transfer; interrupt and resume ranged acquisition; verify the
immutable source and final local digests; and retain no internal model file. For Ollama, re-expose
the pinned Scout revision through content-addressed manifests and blobs while preserving semantic
identity. For Tinker, export and re-import the Q70 child revision while preserving weights, parent,
and training provenance. A loopback fixture route cannot satisfy L02.

Acquire the selected permissively licensed 3–8B dense F4 model directly to the qualified external
cartridge during this step. Record its immutable revision and license evidence before any model
byte moves. L02 passes only when all three source rows and the F4 acquisition have live traces and
exact digest closure.

## L03 — run the F4 and F5 falsification gates in order

Run `f4_gate` first on the matrix class `3-8B dense, permissive license`. Its compiled revision
must cover the frozen Q15/Q16 conditions, independently recompute every Q19 atom, rank, resource,
error, risk, and horizon field, complete `train_dense_fixture_tier_a` and
`train_dense_fixture_tier_b`, touch no more than one quarter of native active bytes per token, and
achieve `lower95CI(Qc/Q_teacher) >= 0.95` in every Q15 stratum inside the predeclared training
budget.

After F4 passes, run `f5_gate` on the matrix class `20-120B sparse`. It must pass the F4 predicates at scale,
complete `train_sparse_fixture_tier_a` and `train_sparse_fixture_tier_b`, and emit Q37
mathematical-resource-versus-quality/service curves whose predicted feasible point clears Q68
`FRONTIER_CLASS` inside the E-011 C1 decode budget.

If either gate fails, preserve the raw result, emit the exact Q38 record, stop before L04, repair
the mechanism in a new governed machine revision, repeat its required machine proof, and begin a
new live campaign from the new S28 close commit. L03 passes only when both gates have live `PASS`
evidence in order.

## L04 — execute every remaining matrix row

### Execution and workloads

Run all five execution rows against their exact model, Apple, storage, mode, context, and gate
tier:

- `exec_c1_s1_frontier_compiled`
- `exec_c1_s1_scout_least_invasive`
- `exec_c2_s2_qwen_least_invasive`
- `exec_c3_s2_k3_native_teacher`
- `exec_c3_s3_k3_compiled_portability`

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

- `train_c1_s1_frontier_tier_a`
- `train_c1_s1_frontier_tier_b`
- `train_c1_s1_scout_tier_a`
- `train_c3_s3_frontier_tier_a`
- `train_c3_s3_frontier_tier_b`
- `train_dense_fixture_tier_a`
- `train_dense_fixture_tier_b`
- `train_sparse_fixture_tier_a`
- `train_sparse_fixture_tier_b`

Each row must pass Q23 placement, Q25 interruption and resume, Q28 physical-write metering, Q53
capacity reservation, Q70 quality, Q71 dataflow, Q72 optimizer equivalence, Q73 atomic child
publication, Q74 endurance admission, named-client callability, and the Tier-B invalidation and
clean-derivation requirements where applicable.

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

Every coordinate must preserve no partial callable revision, the exact typed error, parent or exact
child recovery, no stale handle use, no uncommitted token, and no internal model file.

### Offline and privacy rows

Run `offline_inference_all_execution_rows` over every execution row and
`offline_training_all_training_rows` over every training row with external network disabled and
only the declared loopback agent protocol available. Retain process, socket, file-open, file-write,
credential, prompt/output persistence, source identity, page identity, and internal-volume traces.
Any remote model or gradient request, DNS or external socket, internal full checkpoint, secret
serialization, or undeclared persistence fails the owning row.

L04 passes only when every expanded workload, protocol, training, failure, offline, privacy, and
minimum-code row has live `PASS` evidence. Preserve a failed row and its independent rows; do not
replace the failed result with a simulator or a smaller model.

## L05 — execute Q80 from clean roots

Start from the clean S28 source revision and blank qualified cartridges. Re-run the complete matrix
through its production paths, preserving all raw traces and immutable evidence IDs. Re-run the
complete Python suite and ledger, reproduce Q78 exact accounting, and complete the Q79 offline proof.

Compute the completion digest only when every required expanded row is `PASS` and `LIVE_PROVEN`,
both fixture gates passed before any frontier compiled row ran, every compiled row carries an
independently recomputable Q19 certificate, Q78 and Q79 pass, and no required runtime result came
from a remote model or personal-device anecdote. The digest preimage must include the source
revision, lockfile, acceptance matrix, runbook, model revisions, hardware profiles, row outcomes,
raw-evidence identities, and exact row expansion.

If one required row is `NOT_RUN`, `BLOCKED`, `SKIPPED`, `SUBSTITUTED`, `SIMULATED`, `REMOTE`, or
`FAIL`, the campaign result remains incomplete and `research/ACCEPTANCE_MATRIX.yaml` must not set
`result.status: PASS`. Retain the non-passing campaign outcome in its evidence bundle. Only a
complete, reproducible live campaign may set the matrix result to `PASS` and attach its completion
digest and evidence bundle.

## Campaign close

Record the final worktree, source revision, cartridge identities, active processes, mounts, free
space, row-status summary, evidence-bundle identity, and completion digest or exact blocking rows.
Close agent-created servers, test runners, browser sessions, temporary mounts, and other campaign
environments. Preserve source cartridges, accepted evidence, and user-owned hardware state; delete
only agent-created temporary artifacts whose evidentiary purpose has ended.
