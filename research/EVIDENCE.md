---
artifact_id: cassette-directed-research-evidence
scope_mode: GENERAL_PRODUCT
observed_at: 2026-08-05
consumer: implementation-agent
---

# Cassette evidence records

Every observation below concerns a public specification, immutable artifact, governing source tree,
or controlled derivation. No current Mac, attached volume, local runtime, model cache, account, or
personal configuration supplied evidence.

## E-001 — Kimi K3 immutable artifact inventory

- **Status:** `OBSERVED`.
- **Subject:** `moonshotai/Kimi-K3`, Hugging Face commit
  `9f62e4e9fffbd0a83ddd60e1c209d828994b3569`.
- **Method:** Query the public Hugging Face model API with blob sizes. Read the eight-byte length and
  JSON header of each of the 96 SafeTensors shards by HTTP byte range. Aggregate tensor byte ranges
  by layer and operator name. No weight payload was downloaded.
- **Result:** 96 shards occupy 1,560,936,091,448 B. Their 497,220 tensors contain
  1,560,860,324,864 B of payload. The text graph has 92 MoE layers, 896 routed experts per layer,
  16 selected experts per token per layer, and two shared experts. One routed expert occupies
  17,547,264 B in the published representation. The per-token routed selection therefore addresses
  25,829,572,608 B. Text weights outside individual routed experts occupy 113,601,829,888 B. The
  exact native text-active representation is therefore 139,431,402,496 B before KV state,
  activations, runtime buffers, and allocator reserve. Vision adds 802,428,928 B when invoked.
- **Artifact authorities:**
  `https://huggingface.co/api/models/moonshotai/Kimi-K3?blobs=true`,
  `https://huggingface.co/moonshotai/Kimi-K3/raw/9f62e4e9fffbd0a83ddd60e1c209d828994b3569/config.json`,
  `https://huggingface.co/moonshotai/Kimi-K3/blob/9f62e4e9fffbd0a83ddd60e1c209d828994b3569/README.md`.
- **Supported questions:** Q1, Q4, Q7, Q8, Q13, Q37–Q40, Q50, Q53, Q58, Q63, Q68, Q80.

## E-002 — Model container and acquisition contracts

- **Status:** `SPECIFIED`.
- **Result:** SafeTensors v0.6.2 begins with an eight-byte little-endian header length followed by a
  complete JSON tensor index whose non-overlapping byte ranges permit data-only parsing and range
  reads. GGUF v0.16.0 is a self-describing inference container intended for mapped loading; its
  filename alone is not a canonical model identity. HTTP range transfer is governed by RFC 9110 and
  remains resumable only while the entity validator or immutable source identity is unchanged.
  Hugging Face revisions and files, Ollama content-addressed blobs/manifests, and exported Tinker
  weight objects can be normalized, but their source semantics are not identical.
- **Authorities:**
  `https://github.com/huggingface/safetensors/blob/v0.6.2/README.md`,
  `https://github.com/ggml-org/ggml/blob/v0.16.0/docs/gguf.md`,
  `https://www.rfc-editor.org/rfc/rfc9110.html`,
  `https://huggingface.co/docs/huggingface_hub/v0.34.3/en/guides/download`,
  `https://github.com/ollama/ollama/blob/v0.32.5/docs/api.md`,
  `https://tinker-docs.thinkingmachines.ai/tutorials/core-concepts/weights/`.
- **Supported questions:** Q1, Q3–Q10, Q50–Q58.

## E-003 — Apple compute and unified-memory envelopes

- **Status:** `SPECIFIED`.
- **Result:** Current public Apple reference classes span a fanless 32 GB M5 MacBook Air at
  153 GB/s specified unified-memory bandwidth, an actively cooled M5 Max MacBook Pro at up to
  128 GB and 614 GB/s, and an M3 Ultra Mac Studio at up to 512 GB and 819 GB/s. These are class
  ceilings, not available Cassette budgets or sustained application measurements. Metal exposes
  `recommendedMaxWorkingSetSize`; admission must remain below both that value and a separately
  reserved physical-memory bound.
- **Authorities:** `https://www.apple.com/macbook-air/specs/`,
  `https://www.apple.com/macbook-pro/specs/`, `https://www.apple.com/mac-studio/specs/`,
  `https://developer.apple.com/documentation/metal/mtldevice/recommendedmaxworkingsetsize`.
- **Supported questions:** Q2, Q11–Q14, Q30, Q37–Q39, Q45–Q48, Q59, Q63, Q68–Q69, Q80.

## E-004 — Metal file-to-resource path

- **Status:** `SPECIFIED`.
- **Result:** Metal I/O command queues encode asynchronous loads from file handles and exact file
  ranges into GPU resources and provide explicit synchronization with compute. The public contract
  proves an asynchronous file-to-resource operation; it does not prove physical zero-copy DMA or a
  fixed copy count through every filesystem, bridge, and Apple generation.
- **Authorities:** `https://developer.apple.com/documentation/metal/mtliocommandqueue`,
  `https://developer.apple.com/documentation/metal/resource-loading`,
  `https://developer.apple.com/documentation/metal/mtliocommandbuffer/load(_:offset:size:sourceHandle:sourceHandleOffset:)`,
  `https://developer.apple.com/metal/Metal-Feature-Set-Tables.pdf`.
- **Supported questions:** Q2, Q30, Q45–Q48, Q63–Q65.

## E-005 — Removable-storage durability and transport

- **Status:** `SPECIFIED`.
- **Result:** USB-C defines a connector, not a service rate. The usable bound is
  `min(link payload, bridge, media steady state, filesystem/cache path)`. APFS provides the first
  release's writable cartridge semantics. Cassette must use durable file synchronization, including
  `F_FULLFSYNC` where supported, verify the committed root after remount, and treat an unsupported or
  failed durability primitive as a failed writable-cartridge qualification. USB and Thunderbolt
  headline rates remain upper bounds until cold, warm, mixed, queued, and thermally sustained tests
  measure the assembled class.
- **Authorities:**
  `https://developer.apple.com/support/apple-file-system/Apple-File-System-Reference.pdf`,
  `https://developer.apple.com/documentation/foundation/about-apple-file-system`,
  `https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/fsync.2.html`,
  `https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/fcntl.2.html`,
  `https://developer.apple.com/documentation/diskarbitration`,
  `https://www.usb.org/document-library/usb4r-specification-v20`.
- **Supported questions:** Q2, Q4, Q11–Q14, Q20, Q23, Q25, Q28, Q38–Q49, Q51, Q53, Q60, Q62–Q65,
  Q69, Q71, Q73–Q75, Q79–Q80.

## E-006 — Existing runtime ownership boundary

- **Status:** `OBSERVED`.
- **Result:** MLX already owns Apple tensor operators, deferred evaluation, file range loading through
  `pread`, streams, and events. llama.cpp and ggml already own GGUF parsing, mapped/direct file
  loading, tensor lookup, quantized kernels, backends, KV state, and serving primitives. Cassette's
  irreducible numerical work is page-readiness and indexed gather only when no existing primitive
  preserves the selected representation. Model identity, semantic page maps, prediction, miss
  recovery, immutable revision commits, and canonical agent envelopes remain Cassette control-plane
  responsibilities.
- **Authorities:**
  `https://github.com/ml-explore/mlx/blob/2c46b953db88965c4270cc7306eda6887a3247f2/mlx/io/load.cpp`,
  `https://github.com/ggml-org/llama.cpp/blob/360e1349f0009c5ad99d21e3c4546b707addc68a/src/llama-model-loader.cpp`,
  `https://github.com/ggml-org/ggml/tree/90951f99af1fbebef3fbdd58ff5b8715b0bb9c43`.
- **Supported questions:** Q7, Q10–Q11, Q20, Q29–Q33, Q40, Q45, Q57, Q59, Q63–Q66, Q78.

## E-007 — Training state and paged-update arithmetic

- **Status:** `INFERRED` from the AdamW and LoRA update definitions and storage byte widths.
- **Result:** Exact AdamW restart requires current weights, first and second moments, optimizer step,
  hyperparameters, random state, data cursor, loss scale, and all input identities. With FP16/BF16
  parameters and FP32 first and second moments, persistent logical state is at least 10 B/parameter;
  an FP32 master raises it to at least 14 B/parameter before checkpoints, journals, deltas, or device
  write amplification. Kimi K3-scale full Adam therefore exceeds 27.2 TB or 38.1 TB respectively,
  so a 2 TB cartridge cannot admit that operation. LoRA composes a frozen base with a bounded update
  `W' = W + sBA` and permits training state proportional to the adapter rank rather than all base
  parameters.
- **Supported questions:** Q21–Q28, Q38, Q53, Q57, Q60–Q62, Q70–Q75, Q80.

## E-008 — Named-agent protocol authorities

- **Status:** `SPECIFIED`.
- **Result:** Codex app-server is a versioned JSONL, JSON-RPC-like thread/turn/item protocol whose
  generated schema is the authority for one exact Codex build. OpenAI Responses uses HTTP and SSE.
  Ollama uses HTTP and streamed NDJSON. OpenClaw exposes OpenAI-compatible HTTP surfaces and its own
  versioned Gateway protocol. Hermes Agent exposes an OpenAI-compatible agent API; raw Hermes model
  weights do not define a client protocol. Tinker exposes training and checkpoint operations, while
  its OpenAI-compatible inference surface is beta and capability-limited. These contracts require a
  canonical broker with adapters; no single external wire format preserves all semantics.
- **Authorities:**
  `https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md`,
  `https://github.com/openai/openai-openapi`, `https://docs.ollama.com/api/introduction`,
  `https://github.com/openclaw/openclaw/blob/main/docs/gateway/protocol.md`,
  `https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/api-server.md`,
  `https://tinker-docs.thinkingmachines.ai/tinker/compatible-apis/openai/`.
- **Supported questions:** Q5–Q6, Q9–Q10, Q31–Q33, Q49, Q52, Q65–Q67, Q76–Q77, Q80.

## E-009 — First-principles service bounds

- **Status:** `INFERRED`.
- **Result:** For a decode step that misses `D_miss` storage bytes, moves `H_mem` unified-memory
  bytes, and performs `F` operations, `L_d >= max(D_miss/B_s, H_mem/B_m, F/C_compute)` and
  `R_d <= 1/L_d`. Assembly obeys `L_a >= D_load/B_s + N_reads*l_read`. Residency obeys
  `W + C + K + A + R <= M`. Applied to E-001, native Kimi K3 on a memory class that cannot retain
  its 113.60 GB fixed path must reread or transform that path; external streaming of the native fixed
  bytes on every token cannot approach a hosted service at consumer-removable-storage bandwidth.
  Therefore native mode is admissible only when its active graph and state fit. Smaller-memory K3
  support requires a distinct compiled revision whose fixed and conditional working set satisfies
  the same quality and service gates.
- **Supported questions:** Q2, Q4, Q7, Q11–Q20, Q37–Q48, Q53, Q59, Q63–Q70, Q80.

## E-010 — Bounded collision evidence

- **Status:** `OBSERVED`, bounded public search completed 2026-08-05; not a legal freedom-to-operate
  opinion.
- **Result:** Apple LLM in a Flash covers hardware-informed flash loading, activation reuse, and
  row-column bundling. Apple Instruction-Following Pruning covers prompt-conditioned fixed
  subnetworks. SwiftLM and related MLX projects cover Apple SSD expert streaming and caches.
  ServerlessLLM covers storage-native checkpoint loading. Public pruning patents cover model
  compression and conditioned pruning. The search found material collisions for every isolated
  ingredient, but no located artifact implemented the complete conjunction of: source-general
  direct acquisition to a removable authoritative cartridge; provenance-linked post-training
  compilation into prompt-persistent executable pages; bounded Apple execution; cartridge-resident
  writable derivative training and atomic revisions; named-agent protocol service; and one live
  frontier-scale release matrix. The conjunction remains a candidate contribution, contingent on
  Q80 live proof and a renewed search against the implemented mechanism.
- **Authorities:**
  `https://machinelearning.apple.com/research/efficient-large-language`,
  `https://machinelearning.apple.com/research/pruning-large-language`,
  `https://github.com/SharpAI/SwiftLM`, `https://github.com/ServerlessLLM/ServerlessLLM`,
  `https://patents.google.com/patent/WO2024072001A1`,
  `https://patents.google.com/patent/US20260073218A1`.
- **Supported questions:** Q34–Q35, Q40, Q78, Q80.

## E-011 — Static falsification of native frontier parity on C3, and the consumer decode budget

- **Status:** `INFERRED` from E-001 and E-003; recorded 2026-08-05 under the amended remit.
- **Method:** Apply the E-009 decode bound to E-001's exact native active byte count and E-003's
  specified class bandwidth ceilings. No measurement, no personal hardware.
- **Result:** Native Kimi K3 decode touches 139,431,402,496 B of active representation per token
  (E-001; excluding non-addressed embedding rows reduces this by at most ~2 GB). Against C3's
  819 GB/s specified ceiling: 139.4/819 = 170.2 ms per token, a ceiling of 5.87 tokens per second
  at 100% bandwidth utilization — below the Q68 10 tok/s floor before any storage, KV, scheduling,
  or utilization loss. The former native-parity claim on C3 is therefore Q38-falsified by static
  bound, and the row is reclassified TEACHER_CORRECTNESS (Q39 v2). The same bound fixes the
  consumer thesis budget: on C1 at 153 GB/s, sustained Rd >= 10 tok/s requires
  touched_bytes_per_token <= 15.3 GB at 100% utilization (~10.7 GB at 70%), which is the compiled
  working-set envelope that the Q36 F4/F5 gates and Q37 prediction curves must clear.
- **Supported questions:** Q36–Q40, Q63, Q68, Q80.

## Evidence status boundary

The records above establish specifications, artifact observations, and derived bounds. They do not
establish `IMPLEMENTED` or `LIVE-PROVEN`. Those statuses require the Q80 executable matrix against a
completed Cassette build.
