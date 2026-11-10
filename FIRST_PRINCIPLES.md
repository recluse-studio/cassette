# First principles — original Cassette specification and progress

The governing specification is the August 31, 2026 source at
`074f594a0bacc4c08e953acf4539f129eb1f041d`. The original remit, mathematics,
research decisions, question queue, acceptance matrix, live runbook and S28 closeout
have been restored from that source. Later specification additions and campaign
procedures are withdrawn. Their text is retained off-tree as history.

The original result is a full model on an external drive, usable through consumer
Apple hardware and the named agents, trainable on the drive when compatible,
with the original capability, speed, reliability and minimum-code requirements.

## What is done

These checks record the August implementation results. They do not claim a fresh
run of today's source or a passing live product.

- [x] Storage identities, page layout, transactions, integrity and cartridge lifecycle
  were implemented and checked on scratch cartridges (S01–S08).
- [x] Source handling, resumable verified transfers and compatibility decisions were
  implemented and checked against controlled source servers (S09–S11).
- [x] Mathematical plans, paging and the small complete transformer path were
  implemented and checked (S12–S15).
- [x] Broker, scheduling and named-agent protocol adapters were implemented and
  checked (S16–S18).
- [x] Compilation, hardware plans and both training paths were implemented and
  checked on the declared fixtures (S19–S22).
- [x] Failure handling, export, update, removal, integration and code accounting
  were checked within the machine phase (S23–S27).
- [x] The machine phase closed on August 31 with 307 passing tests and a passing
  ledger at its recorded source (S28).
- [ ] Complete live storage qualification under the original contract.
- [ ] Complete real-source acquisition under the original contract.
- [ ] Demonstrate the dense and sparse mechanisms on real models.
- [ ] Demonstrate the full frontier-model execution, training and client requirements.
- [ ] Complete the final clean-root run and reproducible completion result.

The existing September checkpoint records a real 4,096-byte write to LaCie,
verification, restart recovery and repeated-operation handling. That is useful
partial evidence, not a full model download or a complete drive qualification.
Its source is commit `9d6b41a4a4850d8899c0216090f5e244ae5e1329`.
No complete original live-stage pass was found in the inspected records.

## What remains for the acquisition work called stage 5

This heading preserves Drew's reference to the acquisition step. Its original
requirements are the August L01 storage and L02 acquisition requirements below;
the later L05–L10 queue supplies no additional conditions.

- [x] Measure the actual drive's read/write behavior for its required use and
  verify that committed data remains correct after remount. (2026-11-10: Cassette's drive
  check passed for this download; remount proved on the cartridge volume, not by
  unplugging the LaCie. The full Q42 long-duration profile has not been run.)
- [x] Exercise Cassette's acquisition path with a real tiny Ollama model downloaded
  directly to the drive, preserving its exact source identity. (2026-11-10: `smollm:135m`.)
- [x] Interrupt and resume a real transfer, then verify every final file against
  its expected digest. Keep model files off the Mac's internal storage. (2026-11-10)
- [x] Verify that the Ollama manifest and blobs preserve the complete model identity.
  (2026-11-10: pinned manifest digest and all five blob digests verified.)

These are the immediate acquisition checks. Complete original L02 closure still
requires its named full-model source rows. The Tinker row consumes a trained
child model, so that particular proof needs the training result; it is not a
prerequisite for exercising the tiny Ollama transfer. Neither that dependency
nor the full-model performance work adds machinery to the small acquisition check.

Drew has directed that basic acquisition use a real tiny Ollama model.
`smollm2:135m` is listed by Ollama at 271 MB:
https://ollama.com/library/smollm2:135m
The installed Ollama CLI reports version 0.40.11. This model provides a concrete
small input for the download, byte-verification and interrupted-transfer work;
it adds no stage or acceptance requirement. It has not been downloaded by this task.
The original large-model capacity, quality and performance claims remain separate.

## The original live stages

| Original stage | What it must demonstrate | Current closure |
|---|---|---|
| L01 | Actual storage performance, reliable saved data and required writable-drive behavior. | Incomplete; partial physical evidence exists. |
| L02 | Real Hugging Face, Ollama and Tinker acquisition/re-import, exact model identity and resumed transfers, with model bytes on the external drive. | Incomplete. |
| L03 | Dense F4 followed by sparse F5: the original quality, reduced byte use, training and resource bounds on real models. | No complete live pass found. |
| L04 | Original frontier execution and comparisons, sustained operation, all named clients, compatible training, failure recovery and offline operation. | No complete live pass found. |
| L05 | Repeat the complete original matrix from clean source and clean cartridges; reproduce code accounting and offline proof; emit the completion digest only if every required row passes. | Not complete. |

The August file calls the final whole-system proof L05. Clearing that original
L05 requires all five rows of this table. The later acquisition label does not
change that requirement or convert completed machine work into live proof.

## Restoration worklog

- Drew ordered the August specification restored, later additions ignored, completed
  work checked off, and the remaining acquisition work explained plainly.
- Drew clarified that basic acquisition should use an available real tiny Ollama model.
- The restored source owns product requirements. This file reports progress and maps
  the familiar acquisition label; it creates no new gate, test, reviewer or stage.
- Existing implementation and raw evidence remain available for reuse against the
  original requirements. Post-August code, test names and campaign records do not
  create requirements merely by existing.
- This task restores documents and reports status. It does not resume the old test
  campaign, download a model, certify the current executable or publish a release.
- 2026-11-10: Drew asked for the remaining work on the Linear board, labelled `cassette`,
  with no human approval or review gates, and for execution through to completion.
  Cards REC-374 to REC-378 track original L01–L05 in dependency order.
- 2026-11-10 hardware observation, before any L01 measurement: the attached host is an
  M4 MacBook Air with 24 GB (Mac16,13, macOS 27.0.1 build 26A434) and the attached drive
  is a LaCie Rugged USB-C 5 TB, APFS, on a 5 Gb/s USB link. The matrix classes are
  `c1_air_32` (M5, 32 GB), `c2_max_128`, `c3_ultra_512`, and NVMe storage on USB4 40 Gb/s
  or Thunderbolt 5. No attached device matches a matrix class. L01 stays TODO; nothing
  was measured, downloaded or remounted in this session.
- 2026-11-10 hardware amendment, at Drew's instruction: the acceptance hardware is his
  MacBook Air, optionally his Mac mini as a lesser machine, and the available LaCie drives.
  `research/ACCEPTANCE_MATRIX.yaml` now declares `c1_air_24`, optional `c2_mini` and
  `s1_lacie_usb`; the M5/Max/Ultra and NVMe classes are withdrawn. The Qwen row moves to the
  Air; the Kimi K3 portability row and its two training rows move to the mini and apply only
  when the mini is enrolled; the Ultra-only native teacher row is withdrawn. Models, gates
  and thresholds are unchanged. This supersedes the remit's sentence that the work is not
  for Drew's specific hardware, for acceptance purposes only. `PHASE_LIVE_RUNBOOK.md` carries
  the same names. Generated schemas and machine fixtures were not regenerated: the current
  generator expects the withdrawn October queue and cannot run against the restored files.
  Replaced text: /Volumes/LaCie/drewwiberg-lacie/codex-runtime/cassette-hardware-amendment-20261110
- 2026-11-10 L01 start, state and raw output under
  /Volumes/LaCie/drewwiberg-lacie/codex-runtime/cassette-l01-20261110. Cassette's `drives`
  lists the LaCie (APFS, 3.85 TB available). The first public Ollama connection failed with
  SOURCE_UNAVAILABLE under Q52: Ollama omits an empty `q` from its next-page link and
  `sources.py` required it. One-line repair in the continuation check; a non-empty query
  must still be echoed. The connection then succeeded and `select-model` froze
  `smollm2:135m` at manifest sha256:9077fe9d…, one 270,885,952-byte GGUF layer, zero bytes
  downloaded. `select-drive` on folder `drewwiberg-lacie/Cassette-cartridge-20261110` was
  started; its inventory result is not yet recorded. No measurement, remount or payload
  transfer has run. The existing test suite was not rerun after the repair.
- 2026-11-10 shared-drive working method, at Drew's instruction: existing drive content is
  untouched and other agents keep using the drive while Cassette runs. Cassette's cartridge is
  an APFS volume inside one growable image file on the LaCie,
  `/Volumes/LaCie/drewwiberg-lacie/cassette-cartridge/CassetteCartridge.asif` (2 TB ceiling,
  volume UUID ec9a65ac-c5af-43d3-83f7-05a255df45e8, folder `Cassette`). No product code changed
  for this. Remount proof ejects and reattaches only that volume; the LaCie stays mounted.
  This proves Cassette's commit path across a filesystem remount. It is not a physical unplug
  of the LaCie. The whole-LaCie inventory started earlier was stopped unfinished and is unused.
- 2026-11-10 basic acquisition result. Model changed at Drew's instruction to the smallest
  viable Ollama model: `smollm:135m`, manifest sha256:b0b2a461…0133, 91,727,296-byte GGUF plus
  four small blobs. Go operation op-7c5c7c7e… failed terminally with SOURCE_REVISION_CHANGED
  (HTTP 412): the registry redirects blob reads to a storage origin whose own ETag can never
  equal the digest sent in If-Match. Repair in `sources.py`: on a cross-origin redirect of a
  content-addressed `/blobs/<digest>` path, drop If-Match; the final digest check is unchanged.
  The failed operation is retained. New operation op-5c9be7a4…: durability hold, cartridge
  remount verified, drive check PASS, transfer interrupted by SIGINT after the 8 MiB
  checkpoint, resumed under the same key from that checkpoint, SUCCEEDED with 91,739,413
  verified bytes. An independent `shasum -a 256` of the stored GGUF equals
  eb2c714d…9b94. No model-sized file was found on the internal disk. Tests
  `test_s09_sources`, `test_s10_transfer` and `test_l05_ollama` pass (7) after both repairs;
  the full suite and ledger were not run. L01 and L02 stay open: the long-duration Q42
  profile, the Hugging Face models and the Tinker row are not done.
- 2026-11-10 Drew's direction: take charge and keep the work moving without waiting on him. Card
  REC-396 added at his instruction: after the live tests, compare measured performance with MATHS.md.
- 2026-11-10 Hugging Face acquisition through the CLI: `HuggingFaceTB/SmolLM2-135M-Instruct` at
  git-sha1:12fd25f7…, 25 files, 1,969,841,187 verified bytes, operation key `hf-smol-go`, SUCCEEDED.
  Its weights are BF16; the native path accepts only F32, so this model cannot yet be run.
- 2026-11-10 first real model run from the drive. `Felladrin/Llama-160M-Chat-v1` (Apache-2.0, F32,
  git-sha1:3701ea6a…) was acquired and published through the product prepare operation on
  `/Volumes/CassetteCartridge/Live160` (root blake3:26d20cde…, identity blake3:d6ed8e38…). Asked
  "What is the capital of France?", it answered "The capital of France is Paris." Drivers and raw
  output: /Volumes/LaCie/drewwiberg-lacie/codex-runtime/cassette-live-20261110.
  Four repairs were needed before a real repository could be prepared or run usefully:
  (1) `broker.py` passed every repository JSON file to the compiler, which rejects unknown files; it
  now passes only the compiler's admitted semantic files. (2) `compiler.py` refused the ordinary
  ChatML template because it joins text with `+`; bounded text addition is now admitted.
  (3) `compiler.py` required a shard-index byte total that real indexes may omit; a declared total
  must still be exact. (4) Generation re-read every weight and ran a full durable generation
  commit for every token: 96 s per token, of which about 85% was drive flushes and re-verification.
  `pager.py` now keeps verified weights in memory for the operation (already charged by Q47
  admission) and `broker.py` commits the context when the operation completes, pauses, is held or
  is cancelled. Measured after: 24 tokens in 157 s end to end; model computation is under 0.1 s per
  token after load; the remaining per-token cost is one durable operation-log append (2–3 s on this
  drive) and the single closing commit takes about 175 s. `tests/test_l02_native.py` and
  `tests/test_l03_execution.py` pass (5) after the repairs; the pause observer in the L02 test now
  yields at every worker boundary instead of relying on slow commits.
- 2026-11-10 findings that bear on L03 and L04, from reading the code, not from a gate run:
  (a) The compiled path (`compiler._native_head_windows`) transforms only the output matrix, one
  2x2 block per durably committed window, in exact rational arithmetic, and the compiled runtime
  accepts only prompts identical to its observed cases. For this 160M model that is 6,144,000
  windows. It cannot reduce bytes read per token on a real model, so the F4 predicates cannot be
  met by the present mechanism. No F4 result is claimed; the gate has not been run.
  (b) The attached 5 TB LaCie Rugged behaves as a spinning disk: one F_FULLFSYNC costs 1–3 s on it
  (macOS reports no media type for it; the 5 TB Rugged is sold as a hard disk). The Q68
  floors (10 tokens/s, 100 ms per token) cannot be met by any path that flushes per token on this
  drive. The remit names flash or SSD storage.
  (c) Native execution requires the whole model in memory (Q47 admission), so on the 24 GB Air it
  covers models up to roughly 4 GB of F32 weights. Models larger than memory depend on (a).
- 2026-11-10 full suite after the repairs: 76 passed, 8 failed, 3 collection errors (528 s). Every
  failure is in ledger, schema, campaign or matrix bookkeeping (`test_s01`, `test_s03`, `test_s23`,
  `test_s26`, `test_s27`, `test_l04_campaign`, `test_live_stage_acceptance`): the tools and fixtures
  still expect the withdrawn October documents and the pre-amendment matrix. No model, store,
  source, pager, trainer or broker behaviour test fails. The bookkeeping is not yet repaired.
- 2026-11-10 BF16 weights admitted: `compiler.py` accepts F32 or BF16 native weights and records the
  precision; `pager.py` widens BF16 exactly to float32. The compiled output-window reader refuses
  BF16 by name. `HuggingFaceTB/SmolLM-135M-Instruct` (BF16, git-sha1:b5f4b394…) was prepared on
  `/Volumes/CassetteCartridge/LiveSmol` (root blake3:df33446c…) and answered "The capital of France
  is Paris, which is the largest city in France and the". That run took 905 s for 16 tokens while
  the drive was busy with other work; it is a correctness result, not a speed measurement.
- 2026-11-10 Drew asked for the build story to be updated and for local commits and pushes to the
  open-source remote when sensible. `BUILD_STORY.md` has the November chapter. Snapshot commit
  32a107d and history join 53a3a5e were pushed to `origin/main` (previously 2692c30). Research files
  that existed only on the published branch were restored first; nothing published was deleted.
  The stale `~/cassette` checkout and its uncommitted October edits were left untouched.
- 2026-11-10 Drew's direction: rebuilds are not on the plan. The existing compiled path is to be run
  on real models and its faults fixed one at a time; nothing is redesigned. Cards REC-398 to REC-405
  track the further work (mid-sized model, chat templates, prepare/run command, client endpoints,
  existing big-model path on a real model, training on a real model, drive saves, checking tools).
- 2026-11-10 memory admission sized to the request: `pager.NativeTransformer` takes an optional
  operation horizon and admits context and activation memory for the positions the operation can
  reach instead of the whole source context; a step past the admitted horizon is refused.
  `broker.generate_native` passes prompt plus requested tokens for text requests.
- 2026-11-10 existing compiled path, first measurement on a real model (Live160, 160M, output
  matrix 32000x768). Fault fixed first: teacher capture multiplied the whole admitted peak,
  weights included, by the node count and refused the model; it now adds one retained activation
  per node for the actual input. Then, unchanged otherwise: capture of one 34-token case took 239 s
  and produced 222,702,746 bytes of observations; `prepare_native_compiled` with `max_windows=2`
  took 268 s, 134 s per window. The matrix has 6,144,000 windows: about 9,500 days at this rate.
  Each window is one 2x2 block with a 16-byte description, so the complete description is the
  size of the matrix it describes, only the output matrix is transformed, and the runtime accepts
  only the observed prompt. This is a probe, not the F4 gate. Raw output:
  /Volumes/LaCie/drewwiberg-lacie/codex-runtime/cassette-live-20261110/compile-probe.out
- 2026-11-10 checking tools: `tests/test_s23_failure_rows.py` now treats October campaign metadata as
  optional in the restored matrix; with it, `test_s23`, `test_s26_machine_gate` and
  `test_s26_phase_machine` collect and 256 of 257 pass. The remaining failure cites the withdrawn
  `adaptive_capacity_control` matrix block.
- 2026-11-10 chat templates (REC-399). The contained renderer now uses the reference renderer's
  block trimming and absent-field behaviour, and admits attribute reads, loop position, bounded
  concatenation and counter addition, `raise_exception`, `namespace`, a fixed list of harmless
  string and mapping methods, and bounded `format`, `join`, `list`, `map`, `selectattr` and
  related filters. Token variables stored as objects are passed by their content. Imports,
  macros, multiplication, powers, `replace` and other calls stay refused, and the loop and size
  bounds stay. Checked against the reference settings on a four-message conversation: identical
  output for SmolLM-135M-Instruct, SmolLM2-135M-Instruct, Llama-160M-Chat, TinyLlama-1.1B-Chat,
  Qwen3-4B, Qwen2.5-0.5B-Instruct, Qwen3-30B-A3B, Qwen3-235B-A22B-Instruct-2507, Llama-4-Scout
  (unsloth mirror), Mistral-7B-Instruct-v0.3, Phi-3-mini and DeepSeek-R1-Distill-Qwen-1.5B.
  Still refused: Llama-3.2 (reads the current date, which would make rendering depend on the
  day) and SmolLM3 (template syntax extension). Kimi-K3's template was not publicly readable.
  Checker: /Volumes/LaCie/drewwiberg-lacie/codex-runtime/cassette-live-20261110/template_check.py
- 2026-11-10 drive flush measurement while a download was running: F_FULLFSYNC of one 4 KiB write,
  eight samples each: LaCie directly, median 3.8 s (0.7–6.5 s); Cassette's image volume on the
  LaCie, median 10.8 s (6.6–16.9 s); the Mac's internal disk, median 5 ms. Internet throughput to
  Hugging Face measured 32 MB/s in the same minute. The 1.7B download (3.4 GB,
  `HuggingFaceTB/SmolLM-1.7B-Instruct`) is therefore limited by per-chunk durable checkpoints on
  this drive and is still running. Only this one external drive is attached.
- 2026-11-10 prepare and ask commands (REC-400). `cli.py` gains `prepare` and `ask`; `broker.py` gains
  `prepare_selected` and `ask_selected`, which reopen the recorded drive selection, reuse a
  completed download's verified extents and call the existing prepare state machine and native
  generation; `pager.memory_profile` reads the machine's memory. Live on the cartridge volume:
  `prepare --acquisition` published SmolLM2-135M-Instruct from the earlier `go` download without
  downloading again (generation 1, model identity blake3:03ec4396…), and `ask` answered "The
  capital of France is Paris." Two faults fixed on the way: pickled side files such as
  `training_args.bin` are now left out of preparation instead of refusing the whole repository
  (they are never opened), and generation now stops at the source's declared end-of-sequence
  token. Tests `test_l02_native`, `test_l03_execution`, `test_l05_entry`, `test_s09_sources` and
  `test_s16_broker` pass (13).
- 2026-11-10 client listener (REC-401). `cli.py` gains `serve`, which starts the existing adapter
  listener for a named client on the selected drive's published model, with an optional short
  model name. The real Ollama program (0.40.15), pointed at Cassette with `OLLAMA_HOST`, ran
  `ollama run smollm2 "What is the capital of France?"` and printed "The capital of France is
  Paris." (190 s, mostly the closing commit on this drive). Faults a real client exposed, each
  fixed: no idempotency key from ordinary clients (the listener issues one); ordinary transport
  headers and empty provider fields treated as unimplemented extensions; liveness and version
  probes and HEAD unsupported; the model-detail request's extra empty fields refused; one
  listener served only one surface (the request path now selects it); the generate endpoint
  streamed chat-shaped frames (new generated event format `ollama_generate_ndjson`); answers
  defaulted to one token (now the remaining context, at most 256, or the compiled horizon);
  the end marker's text was shown and the finish reason was always `length`.
- 2026-11-10 checking tools (REC-405). `tools/genschema.py` runs again on the restored documents: the
  withdrawn October campaign contract is emitted only when its queue block exists. A fresh run
  reproduced every checked-in schema file byte for byte before the Ollama format was added.
  `schema/tables.py` and `schema/MANIFEST.json` were regenerated, not hand-edited.
  `tests/test_s03_schema.py` passes again. `tools/ledger.py` admits the `cli` to `adapters` import.
  Tests passing after this batch: `test_l02_native`, `test_l03_execution`, `test_s03_schema`,
  `test_s16_broker`, `test_s17_broker`, `test_s18_adapters`, `test_l05_entry` (17).
- 2026-11-10 speed with the drive taken out (REC-404, REC-396). The 160M model was prepared and run
  on a temporary cartridge on the Mac's internal disk, as a measurement only; the temporary copy
  was deleted afterwards. Prepare: 102 s including the download. One question, ten tokens, end to
  end: 61 s. A profile showed the model's arithmetic at about 0.5 s per token and the closing
  commit at 35 s, because `store._verify_dependency_paths` re-hashed every segment and page of
  the whole model at each of about thirty journal steps. Repair: each root's dependencies are
  hashed in full at least once per process, and re-hashed whenever any dependency file's device,
  inode, size, modification time or change time differs; an unchanged set is not hashed again.
  This bears on Q60: bytes are still never trusted without a hash in the same process. After the
  repair the same question takes 6.8 s end to end on internal storage and 98 s on the LaCie
  cartridge volume (previously over 190 s); the remainder on the LaCie is its flush latency.
  Tests after the repair: `test_s05`–`test_s08`, `test_s23_failure_rows`, `test_s24`, `test_s25`,
  `test_l02_native`, `test_l03_execution` pass (143).
- 2026-11-10 the 1.7B model (REC-398). `HuggingFaceTB/SmolLM-1.7B-Instruct` (git-sha1:e2384271…,
  3,422,777,952-byte BF16 shard) was downloaded and verified on `/Volumes/CassetteCartridge/Live1700`
  in 7,011 s, then refused at preparation with MODEL_UNSUPPORTED: zero-copy adoption requires
  each shard to fit one 1 GiB segment (Q57 bounds a segment at 1 GiB, Q4 forbids a full-copy
  fallback). Published models commonly use 3–5 GB shards. The verified download is retained.
  The existing route for larger shards is the source-byte recipe (`qualify-composition`), which
  has not yet been exercised on this model.

Restoration evidence and the replaced documents: /Volumes/LaCie/drewwiberg-lacie/codex-runtime/cassette-first-principles-20261102T020519Z
