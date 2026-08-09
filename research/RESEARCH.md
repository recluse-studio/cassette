---
artifact_id: cassette-build-directed-research
version: 3
amended: 2026-08-09
amendment_authority: ORIGINAL_REMIT.md and MATHS.md (mathematical cutover after S11)
scope_mode: GENERAL_PRODUCT
source_queue: research/QUESTION_QUEUE.md
research_status: COMPLETE
closed: 80
blocked: 0
superseded: 0
active: null
consumer: implementation-agent
communication_mode: agent-to-agent
---

# Cassette implementation research ledger

## Binding result

Cassette must accept an agent-issued descriptor for a downloadable model, write the authoritative
model and its mutable training history directly to an external USB-C flash or SSD cartridge, execute
and update compatible models through macOS and Apple Silicon without moving the full authoritative
checkpoint to internal storage, and expose inference and training operations to Codex, Ollama,
OpenClaw, Hermes, and custom agents through machine protocols.

For every tuple declared compatible, the completed implementation must pass the model-capability,
quality, latency, sustained-generation, storage, training, recovery, provenance, offline-execution,
and minimum-code rows defined by Q80. A paper, source inventory, equation, simulator, diagnostic
fixture, small-model run, remote inference path, or human-interface demonstration cannot satisfy a
missing row.

Amended 2026-08-05 under the amended remit: the release contest is the remit thesis —
frontier-class capability on consumer Apple classes — gated against the pinned native-alternative
baseline and the model's own full-capacity reference (Q13, Q68), with the laboratory gap measured
and published rather than gated. Revised packets: Q13, Q17, Q18, Q34, Q36, Q37, Q39, Q67, Q68,
Q70, Q80. E-011 records the static falsification that reclassified the former C3 native-parity row
as TEACHER_CORRECTNESS. Remit ruling on compute provenance: one-time frontier compilation may use
recorded external compute; runtime inference and training remain local, so Q79 is unchanged.

Amended 2026-08-09 after S11 and before S12: MATHS.md replaces the unproved assumption that every
compiled revision is a prompt-fixed working set selected by one router. Compiled plans now require
separate condition-compatibility, atom-capacity, description-distortion, execution-risk,
composition, and observation-adequacy records. Fresh residual sampling is admitted as a conditional
upper bound, not as a universal optimum or rate-distortion equality. Revised packets: Q7, Q11-Q12,
Q14, Q17-Q21, Q27, Q33-Q40, Q47, Q58-Q64, Q68-Q70, Q75, Q78, Q80. E-012 records the proof boundary.

## Scope and authority

- Product scope is `GENERAL_PRODUCT`: Apple Silicon and macOS classes, removable flash and SSD media
  carried over USB-C transports, downloadable model families, source services, and agent protocols.
- Evidence may use governing source code and contracts, official versioned specifications, published
  model artifacts, and deliberately identified reproducible reference configurations.
- Evidence must not inspect or infer from the current Mac, attached volumes, installed software,
  local model caches, personal accounts, signed-in sessions, or personal client configuration.
- Research may write this ledger and bounded evidence artifacts under `research/`. Research does not
  authorize Cassette implementation, publication, account mutation, or messages to external parties.
- [MATHS.md](../MATHS.md) is the sole mathematical authority for compiled representation and
  execution. A packet may specialize it but may not merge or omit its resource dimensions.
- The external cartridge remains the authoritative parameter, optimizer, checkpoint, journal, and
  trained-revision store. Unified memory may contain bounded transient working state; internal storage
  may contain Cassette code and non-model configuration, but no full checkpoint or prohibited training
  state.

## Shared evidence operations

| Evidence group | Governing questions | Decisive operation |
|---|---|---|
| G1 model identity and acquisition | Q1, Q3, Q7–Q10, Q50–Q58 | Trace official source manifests, model artifacts, formats, revision identities, and transfer contracts. |
| G2 Apple and removable-storage path | Q2, Q11, Q30, Q41–Q49, Q63 | Trace buffers, copies, synchronization, filesystems, transports, memory budgets, and sustained device-class limits. |
| G3 compiled geometry and execution | Q12–Q20, Q32–Q33, Q36–Q40, Q57–Q69 | Derive compatibility, atom, description, execution-risk, byte, and compute bounds, then choose the runtime and plan. |
| G4 drive-resident training and durability | Q21–Q28, Q53, Q60–Q62, Q70–Q75 | Trace tensor and optimizer lifetimes, write transactions, recovery, endurance, and invalidation. |
| G5 agent protocols | Q5–Q6, Q9–Q10, Q31, Q49, Q52, Q65–Q67, Q76–Q77 | Trace discovery, request, stream, tool, cancellation, error, and training semantics for each named client. |
| G6 qualification and proof | Q29, Q34–Q39, Q67–Q70, Q78–Q80 | Fix matched baselines, thresholds, code accounting, provenance, and the full live acceptance matrix. |

## Dependency order

1. Q1 fixes model identity; Q2–Q11 then fix authority, residency, acquisition, and compatibility.
2. Q12–Q20 fix measurable equivalence and the compiled resource certificate before a runtime transformation is chosen.
3. Q21–Q28 fix writable-model semantics before the on-cartridge format and transaction system close.
4. Q29–Q33 fix code ownership and protocol authority before component boundaries become binding.
5. Q36–Q40 and Q41–Q69 fix the controlled-reference, hardware, compiler, runtime, and evaluation path.
6. Q70–Q80 fix full-scale training, adapters, provenance, minimum-code proof, and release acceptance.
7. Q34 and Q35 close only after Q80 has live evidence; before that condition, neither question can
   produce a demonstrated novelty claim.

## Queue state

`Q1–Q80 CLOSED`; `0 BLOCKED`; `0 SUPERSEDED`.

The research queue is exhausted. The implementation is not present and no live-product claim is
made. [ACCEPTANCE_MATRIX.yaml](./ACCEPTANCE_MATRIX.yaml) begins at `NOT_RUN` and is the sole boundary
between this implementation contract and a complete Cassette release.

## Evidence records

Evidence records begin at E-001. Each record identifies a versioned subject, method, result, artifact,
and every supported question. `IMPLEMENTED` and `LIVE-PROVEN` remain forbidden until matching code and
end-to-end evidence exist.

## Decision records

Evidence identifiers resolve to [EVIDENCE.md](./EVIDENCE.md). The packet syntax below is binding
input to the implementation agent. `CLOSED` means the research question has one build decision; it
does not mean the corresponding component has been implemented or live-proven.

## Q1 — Canonical full-model identity

```yaml
question_id: Q1
state: CLOSED
decision: P is the complete semantic model revision named by an immutable identity tuple; source and Cassette representations are separate revisions of the same provenance graph, never aliases inferred from a repository name or filename.
formal_contract:
  symbols: "I = H(canonical(source_kind, locator, immutable_revision, artifacts[path,size,digest], format_versions, tensor_index_digest, config_digest, architecture, operator_set, tokenizer_digest, processor_digest, template_digest, precision_scheme, license_digest, parent_ids, transform_manifest_digest)); P(I) is complete iff every required artifact and semantic asset resolves by digest."
  applicability: "All source services and model classes. A mutable tag may locate an object but cannot identify P."
evidence:
  - status: OBSERVED
    result: "E-001 identifies Kimi K3 by one commit, 96 named shards, exact byte counts, tensor headers, configuration, and semantic assets."
  - status: SPECIFIED
    result: "E-002 establishes that container metadata and source manifests can supply immutable artifact identities."
build_instruction: "Canonicalize the tuple, hash it, reject missing tuple members, and bind every executable, tuned, or exported revision to parent identity and transform digest."
acceptance_check: "Resolve the same revision through two source aliases and obtain one I; alter one tokenizer, template, tensor byte, operator declaration, or precision descriptor and obtain a different I; reject a mutable-only identity."
depends_on: []
reopen_only_if: "A supported source cannot expose immutable bytes or a required semantic asset cannot be represented in the tuple."
```

## Q2 — Permitted transient residency

```yaml
question_id: Q2
state: CLOSED
decision: "Only bounded request working pages W, revision-keyed cache pages C, context K, activations A, runtime buffers R, and cryptographic transfer buffers may leave D; Cassette may create no persistent internal-storage file containing model, cache, optimizer, dataset, prompt, output, or training-state bytes."
formal_contract:
  symbols: "M_used(t)=M_exec+M_OSreserve+M_other+|W|+|C|+|K|+|A|+|R| <= M_admit=min(M_physical_safe, recommendedMaxWorkingSetSize); max_t |app_owned_model_bytes_on_internal_storage(t)|=0; |W union C| < |D_authoritative| for every admitted request. W lives through one run, K through its declared session, A/R through a command or step, and C until eviction or revision deactivation."
  applicability: "General macOS. The contract governs Cassette-owned allocations and files; public macOS APIs cannot prove that the OS never compresses or swaps any model-derived RAM byte."
evidence:
  - status: SPECIFIED
    result: "E-003 exposes the Metal working-set ceiling; E-005 and E-009 establish the storage and memory bounds."
  - status: CHOSEN
    result: "Hard no-swap is an admission policy checked by pressure observations, not an OS-wide provenance claim."
build_instruction: "Reserve OS and agent memory, admit before allocation, evict C before W or K, cancel before pressure crosses the hard limit, use cartridge-only temporary files, and zero credentials plus private prompt/training buffers when their lifetime ends."
acceptance_check: "Trace every Cassette open/write and allocation during Q80; fail on an internal model-bearing path, a budget overrun, a full authoritative checkpoint in application-owned memory, or continued allocation after hard pressure."
depends_on: [Q1]
reopen_only_if: "Apple publishes an enforceable per-process no-swap facility or a supported runtime hides unbounded internal model storage."
```

## Q3 — Source preservation and compiled authority

```yaml
question_id: Q3
state: CLOSED
decision: "A cartridge stores immutable provenance plus one or more immutable executable revisions; it need not retain source bytes after verified transformation, but it must retain their complete identity and the deterministic or trained transform record."
formal_contract:
  symbols: "I_exec = H(I_parent, T_id, T_inputs, executable_manifest); authority points to exactly one committed I_exec; recover(source) means reacquire by I_parent, not reconstruct source bytes from a lossy executable revision."
  applicability: "Native imports may make source and executable byte objects identical. Lossless compilation may share content pages. Lossy compilation creates a distinct revision and requires Q17/Q18 evidence."
evidence:
  - status: SPECIFIED
    result: "E-002 supplies source identities; E-007 supplies derivative state; E-009 proves why a transformed K3-class revision is required on smaller memory classes."
build_instruction: "Use a provenance DAG and one atomic authority pointer. Deduplicate identical pages by digest. Never call a transformed revision the source revision."
acceptance_check: "Delete reacquirable source payload after compilation, remount, resolve complete provenance and executable bytes, reproduce a lossless revision bit-for-bit, and require quality evidence for a lossy revision."
depends_on: [Q1]
reopen_only_if: "A source license requires byte retention or a transform cannot be reproduced from recorded inputs."
```

## Q4 — Peak conversion storage bound

```yaml
question_id: Q4
state: CLOSED
decision: "Cassette compiles by bounded streaming and extent reclamation; no algorithm may require simultaneous full source and full target checkpoints."
formal_contract:
  symbols: "S_peak <= max(S_source,S_target)+S_window+S_journal+S_integrity+S_rollback_delta+S_precision+S_reserve, where S_window is a declared bounded transform window, not Theta(|P|). In-place permutation uses cycle decomposition and O(page_size) scratch; shrinking transforms compact forward; growing transforms reserve only S_target-S_source additional bytes."
  applicability: "Transforms with global statistics may make read-only analysis passes but must store only bounded statistics. A transform requiring two full random-access copies is unsupported."
evidence:
  - status: OBSERVED
    result: "E-001 fixes a 1.560936 TB source example for exact admission tests."
  - status: INFERRED
    result: "Content-addressed committed output units can replace source extents once no future dependency uses them; missing source units remain reacquirable by Q1 identity."
build_instruction: "Plan dependency order before mutation, reserve the bound, write and hash one output unit, journal it, release only dead source extents, and atomically publish the final root."
acceptance_check: "Instrument allocated cartridge extents for identity, shrink, grow, interruption, and resume cases; fail if measured peak exceeds the declared equation or if recovery requires a second complete checkpoint."
depends_on: [Q1, Q3]
reopen_only_if: "A newly supported transformation has an unbounded dependency window."
```

## Q5 — Machine transition from source descriptor to callable model

```yaml
question_id: Q5
state: CLOSED
decision: "Preparation is an idempotent durable state machine whose only callable state is a verified published revision."
formal_contract:
  symbols: "EMPTY -> RESOLVED -> RESERVED -> ACQUIRING -> SOURCE_VERIFIED -> PLANNED -> PREPARING -> EXEC_VERIFIED -> PUBLISHED -> ACTIVE; any mutable state may enter PAUSED, CANCELLED, or FAILED and resume from its last hashed commit; PUBLISHED is created by one durable root-pointer commit."
  applicability: "Download, import, native preparation, compiled preparation, and revision update."
evidence:
  - status: SPECIFIED
    result: "E-002 provides source validators and range transfer; E-005 provides durable storage semantics; E-008 provides operation/status protocol requirements."
build_instruction: "Persist operation ID, idempotency key, source lock, capacity reservation, completed ranges, page hashes, plan hash, and candidate root. Repeated requests return the same operation or terminal result."
acceptance_check: "Interrupt every transition, restart and remount, replay the same idempotency key, and obtain either the same published identity or one typed terminal error; no partial revision may be discoverable or callable."
depends_on: [Q1, Q3, Q4]
reopen_only_if: "A source cannot lock revision identity or the selected filesystem cannot durably commit the root."
```

## Q6 — Machine control contract

```yaml
question_id: Q6
state: CLOSED
decision: "The control plane exposes capabilities, source resolution/acquisition, model preparation/activation, run, cancellation, operation status, training, recovery, and revision removal through one versioned request/event contract."
formal_contract:
  symbols: "Request={protocol_version,operation,idempotency_key,target?,arguments}; Operation={operation_id,kind,state,progress,result?,error?}; Error={code,object_id,failed_invariant,retryability,detail}; RunEvent={run_id,sequence,type,payload}; destructive remove requires exact immutable revision and reachability result."
  applicability: "Local Unix-domain or loopback transport first; adapters may expose other local transports. GUI behavior is outside the contract."
evidence:
  - status: SPECIFIED
    result: "E-008 demonstrates incompatible named-agent wires and common lifecycle needs."
build_instruction: "Implement one broker schema and generated validators. Keep long operations asynchronous. Make cancellation cooperative and terminal events sequence-complete."
acceptance_check: "Schema-conformance tests issue every operation twice with one idempotency key, cancel each cancellable phase, inject every typed failure, and verify one terminal state and monotonic event sequence."
depends_on: [Q5]
reopen_only_if: "A named client requires an operation that cannot be represented without semantic loss."
```

## Q7 — Architecture compatibility taxonomy

```yaml
question_id: Q7
state: CLOSED
decision: "Compatibility is a predicate over graph semantics, executable operators, representation, active-state bounds, transformability, and acceptance evidence; architecture labels alone never imply support."
formal_contract:
  symbols: "supported(I,h,s,mode) = parsed(I) and operators(I) subset dispatch(h) and state_bound(I,mode)<=M(h) and io_bound(I,mode,s) passes Q68 and semantics(I) represented and quality(I,mode) passes Q17/Q18 and (mode=NATIVE or compiled_certificate(I,mode) passes Q19). mode is NATIVE or COMPILED_CERTIFIED."
  applicability: "Dense models use NATIVE only when all active weights fit; sparse MoE may use native routing and prefetch; compiled modes use the MATHS.md certificate rather than an assumed router. Multimodal, linear-attention, and recurrent models require their processors and state transitions; quantized models require exact codecs; custom operators require Q55 containment."
evidence:
  - status: OBSERVED
    result: "E-001 shows that a sparse label does not make Kimi K3's 139.43 GB native active representation fit a 32 GB class."
  - status: SPECIFIED
    result: "E-006 identifies reusable operator runtimes."
build_instruction: "Emit a per-revision compatibility manifest with predicate inputs, mode, unsupported operators, memory/I/O bounds, training tier, evidence IDs, and the Q19 mathematical certificate for every compiled mode."
acceptance_check: "Evaluate representative dense, MoE, multimodal, recurrent/linear-attention, quantized, and custom-op fixtures; each result must be deterministic and any SUPPORTED result must lead to a passing Q80 row."
depends_on: [Q1, Q2]
reopen_only_if: "A new operator or representation gains a qualified dispatch path."
```

## Q8 — Pre-download suitability decision

```yaml
question_id: Q8
state: CLOSED
decision: "Remote preflight classifies only facts justified by immutable metadata and returns explicit unknowns; it never converts absent metadata into compatibility."
formal_contract:
  symbols: "Preflight={source_identity,trust:SOURCED_DIGESTED|SOURCE_DECLARED|PARSED|ABSENT,total_bytes,peak_bytes,architecture,operators,precision,total_parameters,active_parameters,context,assets,license,training_tiers,mode_candidates,required_deferred_checks,classification}."
  applicability: "All source adapters. Header range reads count as deferred metadata inspection, not full transfer."
evidence:
  - status: OBSERVED
    result: "E-001 derived exact Kimi K3 tensor and active-byte bounds from public API data plus ranged headers."
  - status: SPECIFIED
    result: "E-002 defines metadata and range capabilities."
build_instruction: "Resolve immutable revision, collect manifests, range-read safe headers when necessary, run Q7 and Q53 predicates, and return no stronger trust state than the evidence supports."
acceptance_check: "Preflight complete, incomplete, deceptive, mutable, gated, and custom-code model records; fail if a required unknown becomes zero, false, or SUPPORTED without a deferred check."
depends_on: [Q1, Q7]
reopen_only_if: "A source adds a stronger signed manifest or removes required metadata access."
```

## Q9 — Source-service input contracts

```yaml
question_id: Q9
state: CLOSED
decision: "One normalized descriptor identifies a source object; adapters resolve source-specific authentication and manifests without changing acquisition lifecycle semantics."
formal_contract:
  symbols: "SourceDescriptor={kind:huggingface|ollama|tinker|extension,locator,revision?,artifact_selector?,credential_ref?,license_acceptance_ref?,expected_identity?}; resolved output={immutable_revision,artifacts[path,size,digest,range_uri],metadata_assets,auth_scope,license_digest}."
  applicability: "Hugging Face repositories/revisions, Ollama manifests and blobs, exported Tinker weight objects, and future adapters satisfying Q52. Tinker is not presumed to be a universal full-model catalog."
evidence:
  - status: SPECIFIED
    result: "E-002 records the distinct source contracts; E-008 records Tinker operation boundaries."
build_instruction: "Keep credentials in an OS credential reference supplied at operation time; never serialize secrets into the descriptor, manifest, cartridge, log, or event."
acceptance_check: "Resolve one immutable fixture per source kind into the normalized output, expire credentials, move the cartridge, and prove the descriptor remains secret-free and source-specific code ends at the adapter boundary."
depends_on: [Q1, Q8]
reopen_only_if: "A source cannot expose immutable artifacts through resolve, enumerate, metadata, and range-read operations."
```

## Q10 — Preservation of model interaction semantics

```yaml
question_id: Q10
state: CLOSED
decision: "Every callable revision carries a semantic compatibility manifest; a weight graph without its tokenizer, renderer, processors, control-token rules, reasoning history, sampler semantics, tools, context policy, and custom operations is incomplete."
formal_contract:
  symbols: "S(I)={tokenizer,normalizer,chat_template,control_tokens,processor_by_modality,sampler_fields,reasoning_schema,tool_schema,structured_output_schema,context_transition,operator_contracts}; semantic_equivalent iff canonical inputs and state yield protocol-equivalent outputs under Q17."
  applicability: "All models. Capability fields may be exact, transformed, provider-managed, or unsupported; unsupported fields cannot be fabricated."
evidence:
  - status: OBSERVED
    result: "E-001 records Kimi K3's multimodal and preserved reasoning-history requirements."
  - status: SPECIFIED
    result: "E-008 identifies protocol-specific reasoning, tool, and stream forms."
build_instruction: "Bind every S member by digest to Q1, execute templates and preprocessors as data-defined or contained operations, and preserve reasoning/tool state across turns exactly as the model card requires."
acceptance_check: "Replay golden text, multimodal, reasoning, tool, structured-output, and multi-turn traces against the matched source harness; fail on token, state, field, order, or context-policy divergence beyond Q17."
depends_on: [Q1, Q7, Q9]
reopen_only_if: "A supported model introduces a semantic operation not representable in S."
```

## Q11 — Cartridge portability across Apple and storage classes

```yaml
question_id: Q11
state: CLOSED
decision: "One cartridge carries content-addressed parameter pages plus several small execution plans; plans select and schedule shared bytes but do not duplicate P."
formal_contract:
  symbols: "plan* = argmin_plan predicted_Ltotal(plan,h,s,request_class) subject to memory(plan,h)<=M(h), bandwidth(plan,s), operator(plan,h), and quality(plan) constraints; |plans+indexes| <= min(0.01*|P_bytes|, 4 GiB) per executable revision."
  applicability: "Plans may differ in read grouping, description budget, fresh-sampling budget, precision layers, kernel dispatch, and concurrency while retaining one mathematical certificate. Different atom values, condition metrics, description reconstruction, or trained selector semantics create a new executable revision, not merely a plan."
evidence:
  - status: SPECIFIED
    result: "E-003 and E-005 define compute and storage-class inputs; E-006 supports runtime plan variation over shared weights."
build_instruction: "Store hardware-neutral semantic pages once, profile the current declared class at activation, validate its measured envelope and Q19 resource certificate, and choose only a plan whose recorded assumptions hold."
acceptance_check: "Move the same cartridge among all Q39 classes, select the expected plan without rewriting weight pages, and reject or recompile when no plan satisfies the measured class."
depends_on: [Q1, Q3, Q7]
reopen_only_if: "A required kernel layout cannot reference shared semantic pages without material weight duplication."
```

## Q12 — Agent-observable service metrics

```yaml
question_id: Q12
state: CLOSED
decision: "Service behavior at every gate tier is evaluated by a vector that retains both agent-visible service and the mathematical resources consumed; neither may be collapsed to a token-rate average."
formal_contract:
  symbols: "V={La_ms,Lp_ms,Ld_ms[token],Rd_tok_s,Ttask_ms,interruptions,stalls,error_rate,availability,Qc_over_Qb,bytes_read,bytes_written,peak_UM,eta_rep,epsilon_exec,delta_exec_total,atom_count,rank_budget,description_bytes_peak,description_bytes_total,metadata_bytes_peak,metadata_bytes_total,fresh_samples_max,fresh_samples_total,fresh_bytes_max,fresh_bytes_total,certified_horizon}; report count, p50, p95, p99, max, mean, standard deviation, and 95% confidence interval per workload stratum, mathematical certificate, and resident state."
  applicability: "Cold means no reusable parameter/KV pages for the revision; warm means the declared cache state is pre-established and recorded; sustained means at least 30 minutes and 10,000 generated tokens unless a workload naturally exceeds both."
evidence:
  - status: INFERRED
    result: "E-009 separates storage, memory, and compute lower bounds."
build_instruction: "Timestamp request admission, certificate selection, description readiness, each fresh correction read, prefill begin/end, each committed token, stream delivery, tool transitions, and terminal result using a monotonic clock; record physical bytes, certificate identity, and thermal session position."
acceptance_check: "Recompute every aggregate from an append-only trace and reject results missing resident-state label, mathematical certificate, denominator, stratum, baseline ID, or tail distribution."
depends_on: [Q2]
reopen_only_if: "A supported protocol introduces an agent-visible latency phase absent from V."
```

## Q13 — Baseline contract: teacher, native-alternative, hosted

```yaml
question_id: Q13
state: CLOSED
revised: 2026-08-05 under the amended remit
decision: "Every comparison uses three pinned baselines: B_teacher, the selected model's own full-capacity reference execution; B_native, the strongest openly downloadable model executing natively within the target Apple class with no cartridge assistance; and B_hosted, the laboratory service where an equivalent one exists. Release gates bind to B_native and B_teacher; parity labels bind to B_teacher or B_hosted equivalence."
formal_contract:
  symbols: "B_teacher=H(reference_kind:hosted|self_hosted_full_capacity,provider_or_server_class,model_revision,precision_if_known,tokenizer,template,sampler,seed_or_trial_policy,reasoning_effort,context_policy,tools,tool_harness,modalities,output_schema,max_output,concurrency,date_region,hidden_features). B_native=H(model_revision,quantization,runtime_commit,apple_class,harness), selected at matrix freeze as argmax over NativeSet(class) of the Q16 aggregate, where NativeSet={openly downloadable instruct revisions whose Q7 native admission passes on the class with no cartridge}. B_hosted uses the B_teacher schema with reference_kind=hosted. Unknown required fields mark the affected baseline NON_EQUIVALENT."
  applicability: "One harness and one scorer set for Qc and every baseline. A NON_EQUIVALENT baseline is excluded from ratio gates and parity labels but never from honest reporting."
evidence:
  - status: OBSERVED
    result: "E-001 shows that Kimi K3 identity includes native precision, million-token context, vision, and reasoning-history semantics."
  - status: SPECIFIED
    result: "E-008 shows that harness and reasoning fields vary by endpoint."
  - status: CHOSEN
    result: "B_native operationalizes the amended remit thesis: the measured alternative is what the same consumer machine can do unaided."
build_instruction: "Persist all baseline manifests beside every evaluation trace; pin B_native per consumer class at matrix freeze and refresh it only by matrix revision; do not merge results across baseline identities or infer hidden provider settings."
acceptance_check: "Change one field of any baseline and require a new identity; attempt a ratio gate against a NON_EQUIVALENT baseline and require rejection; reproduce the B_native selection deterministically from the frozen candidate set."
depends_on: [Q1, Q10, Q12]
reopen_only_if: "A stronger reproducible baseline identity is published, or a superior native-class model appears before matrix freeze."
```

## Q14 — Request latency decomposition

```yaml
question_id: Q14
state: CLOSED
decision: "Condition selection, certificate validation, resident-description assembly, and prefill-required fresh reads are request latency and belong to La; prior model installation or compilation does not."
formal_contract:
  symbols: "Ltotal = Lqueue + La + Lp + sum_i(Ld_i) + Lprotocol + Ltool; La starts when an admitted request begins condition/certificate selection and ends when its description, metadata, and prefill-required pages are validated resident; Lp ends when the first decode step is ready; each Ld_i ends when token i is committed; protocol and tool time are separately measured, never hidden."
  applicability: "Cold and warm runs use the same boundaries. Download, model compilation, and training are lifecycle operation times reported separately."
evidence:
  - status: INFERRED
    result: "E-005 and E-009 show that assembly consumes externally bounded I/O and must be visible."
build_instruction: "Emit nested spans for condition selection, certificate validation, description assembly, fresh correction reads, and the existing latency phases with no overlapping double count; preserve both model-only and complete agent-task totals."
acceptance_check: "For every run, reconstruct wall-clock terminal time from spans within one clock-resolution unit; fail on omitted assembly, queue, tool, or stream delivery time."
depends_on: [Q12]
reopen_only_if: "A protocol changes the observable request start or terminal delivery boundary."
```

## Q15 — Workload coverage requirement

```yaml
question_id: Q15
state: CLOSED
decision: "A compatible capability is admitted only after a stratified workload with zero unsupported requests inside its declared capability envelope."
formal_contract:
  symbols: "Qualification weights: ordinary-warm 0.20, ordinary-cold 0.10, reasoning/coding/tools 0.20, long-context 0.15, multimodal 0.10 when declared, long-tail/domain-shift 0.15, adversarial 0.05, extended-session/recovery 0.05; redistribute an undeclared modality's weight proportionally before freezing the manifest. Required unsupported fraction=0; required completion fraction>=0.995."
  applicability: "Weights govern aggregate reporting, while Q17/Q18/Q68 hard floors still apply independently to every critical stratum."
evidence:
  - status: CHOSEN
    result: "The distribution prevents common warm prompts from concealing cold, long-tail, stateful, or recovery failures."
build_instruction: "Version a deterministic workload manifest, preserve seeds and artifacts, and assign every case to exactly one primary stratum plus optional capability tags."
acceptance_check: "Audit weights to 1.0, execute all cases, and fail compatibility for any unsupported in-envelope case or any missing critical stratum."
depends_on: [Q10, Q12, Q13]
reopen_only_if: "Observed production traces justify a new frozen distribution without reducing any critical coverage floor."
```

## Q16 — Capability-complete evaluation workloads

```yaml
question_id: Q16
state: CLOSED
decision: "Evaluation consists of machine-executable request fixtures and protocol invariants for every declared capability; subjective preference votes are non-binding."
formal_contract:
  symbols: "Case={case_id,B,input_bytes,conversation_state,tools,expected_protocol_trace,deterministic_invariants,scorer,timeout,resource_limits,tags}; suites include text, >=128k context and declared maximum-context boundary, vision, reasoning-state continuation, coding with executable tests, tool round trips, schema validation, multi-turn state, cancellation, disconnect, and restart."
  applicability: "A model is tested only for declared capabilities, but frontier reference rows must exercise every capability its matched laboratory service exposes."
evidence:
  - status: SPECIFIED
    result: "E-001 and E-008 identify multimodal, reasoning, tool, state, and protocol requirements."
build_instruction: "Store canonical inputs, expected state transitions, exact validators, and scorer versions; keep tool environments deterministic and network-disabled unless the case explicitly measures a local tool."
acceptance_check: "Replay the suite twice from clean cartridge roots and obtain identical deterministic invariants, complete traces, and scorer inputs."
depends_on: [Q10, Q13, Q15]
reopen_only_if: "A declared model or agent capability lacks an executable fixture and invariant."
```

## Q17 — Quality and numerical variance

```yaml
question_id: Q17
state: CLOSED
decision: "Native and transformed revisions use separate equivalence gates; output-sampler variance, compiled representation loss, and stochastic execution error are identified separately before any aggregate is estimated."
formal_contract:
  symbols: "For deterministic native runs, require identical rendered input, state transitions, and token sequence; if a reused kernel is non-bitwise, require same token sequence plus recorded max_abs_logit_error<=1e-3 and KL<=1e-4. For transformed runs, use paired prompts and seeds, >=30 paired stochastic trials per critical stratum, lower95CI(Qc/Qb)>=0.97 overall and >=0.95 per critical stratum; error or refusal regressions may not exceed 0.5 percentage points."
  applicability: "Ratios use the same scorer and denominator. The 0.97/0.95 bounds define the PARITY tier: required for NEAR_LABORATORY labels and for mildly transformed rows (Q40 modes 1-3). Q19-certified compiled frontier revisions are release-gated by Q68 FRONTIER_CLASS using this same paired methodology against B_native and B_teacher, with the full Qc/Q_teacher vector reported unconditionally. Prompt persistence is only one possible certified description specialization. Exact thresholds may be tightened per model, never weakened after compatibility publication without a new tier name."
evidence:
  - status: CHOSEN
    result: "Paired trials separate sampler and harness variance from transformation, precision, and routing effects."
build_instruction: "Log output-sampler seeds, compiled-execution seeds, atom and condition IDs, description and residual identities, logits where available, source-native routes, precision pages, harness IDs, and paired scores; attribute each divergence before aggregating it."
acceptance_check: "Inject output-sampler-only, representation, compiled-execution, quantization, source-routing, and harness perturbations and verify attribution; fail on either confidence-bound, declared Q19 risk bound, or hard-stratum regression."
depends_on: [Q12, Q13, Q15, Q16]
reopen_only_if: "A scorer lacks ratio meaning or a deterministic operator cannot satisfy the native trace condition."
```

## Q18 — Preservation of long-tail parameter capacity

```yaml
question_id: Q18
state: CLOSED
decision: "Complete capacity requires 100% source-contribution addressability plus behavioral evidence that rare and protected conditions remain covered and consequential; common-task imitation is insufficient."
formal_contract:
  symbols: "reachability = addressed_source_contributions/required_source_contributions = 1; partition contributions by activation-frequency decile plus never-observed set. A compiled certificate must cover every declared protected condition, retain every minimal-nonface or exclusion record, and declare its observation/test-law boundary. Reachability plus a statistically significant score/logit change under targeted contribution ablation where the teacher shows one bind every tier. Long-tail behavioral bounds are tiered: PARITY requires lower95CI(Qc/Q_teacher)>=0.95; FRONTIER_CLASS requires lower95CI(Qc/Q_native)>=1.15 on long-tail and capacity strata with the full Qc/Q_teacher long-tail vector reported (Q68)."
  applicability: "Native routing uses source route attribution. Compiled revisions use their MATHS.md atom cover, protected-condition law, total contribution map, and teacher activation/gradient/ablation evidence; off-support conditions are rejected or separately qualified, never inferred from similarity."
evidence:
  - status: INFERRED
    result: "Q1 identity and E-009 imply that omitted or permanently unreachable contributions define a smaller model, regardless of common benchmark score."
build_instruction: "Generate rare-domain and rare-route conditions from source traces, include never-observed contributions in adversarial search, compute the compatibility cover on the protected set, and store cover, exclusion, observation, and ablation evidence by revision."
acceptance_check: "Make one mapped contribution unreachable, remove one protected condition from the cover, and supply one off-support condition without a declared decision rule; require structural failure before activation and the applicable targeted behavioral failure."
depends_on: [Q1, Q15, Q17]
reopen_only_if: "A model contribution has no executable attribution or ablation boundary, requiring a different completeness proof."
```

## Q19 — Compiled compatibility and execution-resource certificate

```yaml
question_id: Q19
state: CLOSED
decision: "A compiled revision is callable only through a MATHS.md certificate that separately proves condition compatibility, atom capacity, description distortion, stochastic or deterministic execution error, observation adequacy, and the physical conversion to resident bytes and fresh traffic. A prompt-fixed page set is one optional description class, not the general mechanism."
formal_contract:
  symbols: "For every declared flattening and target T, certificate={field,shape,T_digest,conditions V,metric_digests C_v,eta_rep,rank r,atoms A_i,service_faces F_i,minimal_nonfaces,atom_cover,observation_contract,description_class,B_i,residual_relation,epsilon_exec,delta_exec_total,sampling_law?,per_atom_resource_tables,per_step_resource_tables,description_bytes_peak,description_bytes_total,metadata_bytes_peak,metadata_bytes_total,fresh_samples_max,fresh_samples_total,fresh_bytes_max,fresh_bytes_total,composition_maps,certified_horizon}. Require V=union_i F_i; rank(A_i)<=r; ell_v([A_i])<=eta_rep for v in F_i; every evaluated but excluded condition has a causal record; every stochastic estimator states fresh/private-coin and adversary hypotheses. For the MATHS.md residual sampler, E||Y-A_i x||^2<=||A_i-B_i||_F^2||x||^2/s and Pr(||Y-A_i x||>epsilon_exec||A_i||_F||x||)<=delta_exec under its declared sufficient sample bound, with operation-level risk composed into delta_exec_total. The physical schedule must satisfy Q47/Q68."
  applicability: "Certified separately by immutable revision, plan, Apple/storage class, protected condition and trace family, context range, and observation experiment. Native source routing remains semantic authority and does not require a compiled atom cover."
evidence:
  - status: INFERRED
    result: "E-012 proves that arbitrary higher-order compatibility obstructions can occur inside one orbit of ambient unitaries commuting with the declared coordinate projections. The compatibility complex is therefore not determined by an invariant constant on that orbit; examples with the same 1-skeleton also show that pairwise feasibility is insufficient. E-012 proves only an upper bound for fresh residual sampling; no rate-distortion converse is available."
build_instruction: "Generate the complete certificate from immutable teacher/target evidence, recompute rank and every witness loss, preserve the face cover and exclusions, validate the execution bound, then convert its resources to exact pages, bytes, memory, and measured latency. Store the certificate by digest in the executable revision."
acceptance_check: "On generated exact matrices, realize a face, a pairwise-compatible minimal nonface, a generic metric whose whitening changes rank, a valid residual sampler, a stale certificate, an uncovered protected condition, and an off-support condition. Admit only the exact covered cases whose mathematical and physical bounds both pass; recompute the certificate independently from canonical inputs."
depends_on: [Q12, Q15, Q17, Q18]
reopen_only_if: "A certified plan exposes a missing mathematical resource, a claimed theorem fails, or a less restrictive proved certificate can pass a tuple this contract excludes."
```

## Q20 — Certified page-readiness and execution-failure semantics

```yaml
question_id: Q20
state: CLOSED
decision: "Every page named by the selected native path or compiled certificate must be validated before its first consumer. An absent planned page stalls or terminates before the affected token; declared stochastic correction is planned execution, not a miss or fallback. Cassette never substitutes a smaller expert, remote result, zero page, or uncertified branch."
formal_contract:
  symbols: "PageState: ABSENT -> ACQUIRING -> HASHED -> RESIDENT -> GPU_SUBMITTED -> RECLAIMABLE, with FAILED terminal for that acquisition; invariant planned_pages(native_graph or certified_schedule,r,t,seed) subset validated_resident_pages before command submission. Timeout yields WORKING_SET_TIMEOUT and preserves replay input, certificate identity, execution seed, and last committed model state. Certificate mismatch or undeclared execution risk terminates before submission with one canonical typed error."
  applicability: "Native mode follows the source router exactly. Compiled mode follows its immutable atom, description, sampling, composition, and observation certificate; fresh samples are drawn only under the certificate's coin/adversary model."
evidence:
  - status: SPECIFIED
    result: "E-004 supplies asynchronous load and synchronization primitives; E-005 supplies disconnect/error conditions."
build_instruction: "Resolve the native route or compiled certificate before command encoding, schedule its declared reads, verify page digests, fence compute on readiness, checkpoint recurrent state before stochastic execution, and retain the exact seed and sample record required by Q17."
acceptance_check: "Force absent planned pages, corrupt sampled pages, stale descriptions, out-of-contract seeds, timeout, cancellation, and disconnect at every layer. Exact paths must equal a no-failure replay; stochastic paths must reproduce from their recorded seed and certificate or end before the affected token with one typed error."
depends_on: [Q2, Q10, Q19]
reopen_only_if: "A model graph cannot expose page requirements before an irreversible state update."
```

## Q21 — Supported training operation set

```yaml
question_id: Q21
state: CLOSED
decision: "Training support is tiered by persistent state and operator proof: Tier A requires adapter/LoRA SFT, adapter continued pretraining, and offline adapter DPO; Tier B adds recovery of the compiled compatibility, description, estimator, observation, and precision certificate; Tier C permits full-weight updates only for tuples whose exact state, I/O, endurance, and quality bounds pass admission."
formal_contract:
  symbols: "trainable(op,I,h,s) = gradients_supported(op,I) and state_bytes(op,I)<=capacity_free and peak_UM(op,I)<=M and projected_writes<=endurance_budget and exact_restart=true. Tier A has trainable parameter count N_a << |P|; Tier B restricts updates to atom/selector/description/estimator/observation calibration and precision-recovery tensors declared by the compiled revision; Tier C has N_train=|P_trainable|."
  applicability: "A compatible inference tuple need not qualify for Tier C. Every published training capability names model revision, operation, precision, optimizer, dataset bound, and storage class."
evidence:
  - status: INFERRED
    result: "E-007 proves that Kimi K3-scale full Adam state is tens of terabytes while LoRA state scales with adapter rank."
build_instruction: "Implement Tier A first on frozen cartridge pages, then Tier B for compiled models; expose Tier C only through the same predicate, never as an aspirational flag."
acceptance_check: "Run each advertised operation to a committed revision, restart exactly mid-job, verify numerical equivalence, and reject every operation whose state or endurance equation exceeds the cartridge class."
depends_on: [Q1, Q2, Q7]
reopen_only_if: "A new optimizer or low-state full-weight method proves a smaller exact persistent-state bound."
```

## Q22 — Base mutation and derivative-state model

```yaml
question_id: Q22
state: CLOSED
decision: "Callable revisions are immutable. Training writes a non-callable work branch and commits immutable adapter, replacement-page, or consolidated descendants; it never mutates a callable root in place."
formal_contract:
  symbols: "theta_v = compose(theta_parent, delta_v); LoRA page: W_v=W_parent+sBA; replacement page: page_v[id]=new_digest; revision_id=H(parent_id,ordered_delta_ids,semantic_manifest,training_manifest). Readers pin revision_id until completion."
  applicability: "Adapters may compose only when their declared base, order, tensor shapes, tokenizer, and operator contracts match. Consolidation creates a new child and leaves the parent valid until garbage collection."
evidence:
  - status: INFERRED
    result: "E-007 supplies LoRA algebra and exact restart state."
build_instruction: "Represent revisions as a content-addressed DAG, resolve ordered overlays at activation, and move the callable authority pointer only after Q73 verification."
acceptance_check: "Train while inference pins the parent; parent outputs and page hashes must remain unchanged, the child must resolve its exact composition, and rollback must restore the prior root without rewriting it."
depends_on: [Q1, Q3, Q21]
reopen_only_if: "A supported optimizer requires semantically in-place updates that cannot be isolated by page COW."
```

## Q23 — Placement of training state

```yaml
question_id: Q23
state: CLOSED
decision: "All persistent model-bearing training state resides on D; unified memory holds only the current bounded training window; internal storage holds no dataset, gradient spill, optimizer, master, checkpoint, journal, or training cache."
formal_contract:
  symbols: "place(dataset,base,delta,optimizer,master,checkpoint,journal,RNG,data_cursor)=D; place(current_batch,current_page,current_grad,current_optimizer_slice,activations)=UM while live; peak_D=S_model+S_data+S_state+S_candidate+S_journal+S_reserve; peak_UM=M_exec+batch+active_pages+grad_slices+optimizer_slices+activations+runtime <= M."
  applicability: "Memory pressure may reduce microbatch, checkpoint activations to D, or reject the job; it may not redirect spills to internal storage."
evidence:
  - status: INFERRED
    result: "E-007 fixes persistent optimizer requirements; E-005 fixes cartridge durability."
build_instruction: "Open every training path relative to the verified cartridge root, disable framework spill/cache paths or redirect them to transaction-scoped cartridge objects, and inventory all file descriptors."
acceptance_check: "Trace files and VM allocations through training, forced spill, restart, cancellation, and low-space failure; fail on any model-bearing internal path or undeclared memory peak."
depends_on: [Q2, Q21, Q22]
reopen_only_if: "A reused framework creates an uncontrollable hidden persistent state location."
```

## Q24 — Training quantized parameters

```yaml
question_id: Q24
state: CLOSED
decision: "Tier A and B train BF16/FP32 deltas over a frozen quantized base. Any quantized base-weight update requires an external high-precision master page and error-feedback codec state for only the page being updated; no hidden full master is permitted."
formal_contract:
  symbols: "Frozen base: W_eff=dequant(Q_W)+sBA. Base update page j: u_j=optimizer(master_j,g_j,state_j); q_j=Q(u_j+e_j); e'_j=u_j+e_j-dequant(q_j); persist(q_j,e'_j,state'_j,master'_j) atomically. Require ||e'_j|| and validation loss within codec-specific bounds."
  applicability: "If external master pages make Q53 or Q74 fail, base-weight training is unsupported while adapter training remains eligible. Progressively refinable pages update their canonical master then regenerate dependent bitplanes."
evidence:
  - status: INFERRED
    result: "E-007 establishes the master-state cost and LoRA alternative."
build_instruction: "Make quantization codecs explicit in the training manifest, join one master/state page at a time, retain error feedback, and run precision-recovery validation before child publication."
acceptance_check: "Compare paged updates with an unquantized reference for one step and a full training fixture; fail on hidden full-master allocation, unbounded residual, or Q17 quality regression."
depends_on: [Q21, Q23]
reopen_only_if: "A supported quantized optimizer proves equivalent updates without a master or residual state."
```

## Q25 — Training interruption and rollback

```yaml
question_id: Q25
state: CLOSED
decision: "Training recovery is transaction replay over immutable parent pages; no candidate page becomes callable before the entire child root is durable and verified."
formal_contract:
  symbols: "PREPARE -> WRITE_TEMP -> READBACK_HASH -> JOURNAL_PAGE -> WRITE_CANDIDATE_ROOT -> FULLFSYNC -> SWAP_GENERATION_POINTER -> FULLFSYNC -> COMMITTED; failure before pointer swap retains parent authority; failure after swap selects the highest valid generation whose root and dependencies verify."
  applicability: "Process death, cancellation, removal, bus reset, power loss, ENOSPC, invalid gradient, NaN/Inf, and corruption use the same transaction authority with typed causes."
evidence:
  - status: SPECIFIED
    result: "E-005 supplies APFS and synchronization constraints; E-007 supplies exact restart fields."
build_instruction: "Journal optimizer step, RNG, data cursor, loss scale, input digests, candidate pages, and expected parent. Never overwrite the last valid generation pointer."
acceptance_check: "Kill or disconnect after every durable write, remount, recover the parent or exact child, and compare the resumed next update bit-for-bit with uninterrupted execution."
depends_on: [Q22, Q23, Q24]
reopen_only_if: "A supported filesystem cannot provide the required durable ordering."
```

## Q26 — Post-training interoperability

```yaml
question_id: Q26
state: CLOSED
decision: "Every tuned child is immediately callable through the canonical protocol; export is an explicit, loss-accounted operation available only when a target format can represent the child's graph, precision, tokenizer, and delta semantics."
formal_contract:
  symbols: "Export(v,target) succeeds iff representable(graph_v,weights_v,precision_v,S_v,target); output identity=H(v,target_schema,export_transform,artifact_digests). Adapter export preserves base I and rank/scale; merged export creates full target tensors by cartridge-streaming."
  applicability: "SafeTensors or supported adapter formats serve training exchange; GGUF serves inference export when its operator and quantization schema is sufficient. Export may require target-sized free cartridge space but never internal model storage."
evidence:
  - status: SPECIFIED
    result: "E-002 distinguishes training and inference containers; E-008 supplies callable protocol identities."
build_instruction: "Publish the child to Cassette first, validate target representability, stream export to D, bind all semantic sidecars, and mark unsupported target features exactly."
acceptance_check: "Call the child through every declared adapter, export and re-import each eligible form, and pass Q10/Q17; reject an export that would drop a tokenizer, operator, precision contribution, or ordered delta."
depends_on: [Q10, Q21, Q22, Q25]
reopen_only_if: "A target format adds a previously absent required semantic representation."
```

## Q27 — Training invalidation graph

```yaml
question_id: Q27
state: CLOSED
decision: "Training invalidation follows content and mathematical-certificate dependencies, not broad rebuild folklore; only the transitive consumers of changed hashes are recomputed."
formal_contract:
  symbols: "weights -> {page_stats,page_layout,condition_metrics,compatibility_witnesses,atom_cover,description_distortion,residual_metadata,estimator_calibration,precision_calibration,kernel_plan,quality_proof,cache_key}; certificate member -> {dependent witnesses,plans,quality_proof,cache_key}; precision -> {page_bytes,description_residual,kernel_plan,quality_proof}; tokenizer/template/context/operators -> {semantic_manifest,protected_trace_corpus,observation_contract,condition_metrics,compatibility_certificate,plans,quality_proof,protocol_capabilities}; invalidate(x)=transitive_consumers(changed_digest(x))."
  applicability: "A cache is always revision-keyed and is invalidated by any resolved page or semantic digest change."
evidence:
  - status: INFERRED
    result: "Q1's immutable identity and E-006's plan/runtime boundary yield a hash-addressable dependency graph."
build_instruction: "Persist every MATHS.md certificate input and dependency edge in each revision; compute affected closure before training commit; carry forward only artifacts whose complete input vector is unchanged."
acceptance_check: "Mutate each dependency class independently and assert the exact invalidation set; fail on stale reuse or unrelated full recompilation."
depends_on: [Q1, Q10, Q22, Q24, Q26]
reopen_only_if: "A new generated artifact depends on an input absent from the graph."
```

## Q28 — Training write cost and cartridge endurance

```yaml
question_id: Q28
state: CLOSED
decision: "Training is admitted from projected physical writes and sustained thermal behavior, not free capacity alone."
formal_contract:
  symbols: "For N_t trainable parameters and U optimizer steps, W_logical >= U*N_t*(b_weight+b_m+b_v+b_master)+W_journal+W_checkpoints+W_deltas; Adam with 2-byte weight and FP32 moments is >=10*U*N_t B, or >=14*U*N_t B with FP32 master. W_physical=p95_write_amplification*W_logical. Admit only if lifetime_written+W_physical<=0.80*declared_endurance, W_physical<=0.20*remaining_endurance, capacity Q53 passes, and Q48 thermal floor holds."
  applicability: "If endurance or health telemetry is unavailable, writable training is unqualified for that storage class; read-only inference may still qualify."
evidence:
  - status: INFERRED
    result: "E-007 derives persistent byte floors; E-005 requires measured assembled-device behavior."
build_instruction: "Estimate before admission, meter actual host writes, include filesystem amplification and checkpoints, throttle at the qualified thermal curve, and stop before the reserved endurance bound is crossed."
acceptance_check: "Run synthetic and real declared training patterns past cache exhaustion, compare projected and measured physical writes, and fail if p95 amplification or temperature exceeds the admitted envelope."
depends_on: [Q21, Q23, Q25]
reopen_only_if: "A storage class exposes a stronger endurance contract or an optimizer changes the byte equation."
```

## Q29 — Binding minimum-code metric

```yaml
question_id: Q29
state: CLOSED
decision: "Minimum code is a lexicographic optimization after all correctness gates pass; fewer lines never excuses a missing invariant."
formal_contract:
  symbols: "Minimize J=(failed_acceptance_rows,new_numerical_kernels,authored_executable_LOC,independent_processes,language_runtimes,direct_dependencies,model_specific_branches,duplicate_authorities,shipped_binary_bytes) lexicographically. Generated schemas/plans and tests are reported separately; vendored code counts as dependency surface and bytes, not authored LOC."
  applicability: "Comments, docs, fixtures, and generated records do not reduce the executable count. A reused dependency is admissible only if its required subset and version are explicit."
evidence:
  - status: CHOSEN
    result: "Lexicographic order preserves complete-system behavior while forcing reuse and deletion after correctness."
build_instruction: "Maintain an automated component ledger from the build graph, source classifier, binary closure, process manifest, and branch table; reject duplicated parsers, schedulers, identities, or protocol authorities."
acceptance_check: "Reproduce J from a clean checkout; for each original executable component, remove it and identify the exact acceptance row that fails; any removable component must be deleted."
depends_on: [Q5, Q6, Q7, Q10, Q21]
reopen_only_if: "The build system cannot classify generated, authored, and dependency code reproducibly."
```

## Q30 — Numerical kernel ownership

```yaml
question_id: Q30
state: CLOSED
decision: "Cassette authors no general numerical kernel. It dispatches supported graphs to pinned MLX or ggml/llama.cpp kernels; direct Metal/MPS/Accelerate code is admitted only for a measured missing operator, while Core ML/ANE is optional whole-graph execution and never assumed page-addressable."
formal_contract:
  symbols: "Dispatch rows: {matmul,quantized_matmul,norm,RoPE,attention,convolution,embedding,sampling,autograd,optimizer}->MLX when representation-compatible; {GGUF decode,quantized matmul,MoE indexed matmul,attention,KV,sampling}->ggml/llama.cpp; file-range-to-GPU->Metal I/O; unsupported custom op->Q55; page-ready indexed gather->existing primitive else one Cassette kernel after Q29/Q68 proof."
  applicability: "Each model plan pins runtime commit, operator signature, dtype, shape limits, numerical tolerance, and Apple feature set. Mixing runtimes inside one graph is forbidden unless transfer cost and semantics pass Q68/Q17."
evidence:
  - status: OBSERVED
    result: "E-006 identifies existing loader, operator, backend, and state ownership; E-004 identifies Metal I/O."
build_instruction: "Generate the dispatch table from the graph manifest, probe every operator before download completion, and keep model variation in plans rather than handwritten branches."
acceptance_check: "Execute golden tensors for every dispatched dtype/shape/operator, compare against the source reference, audit linked symbols for undeclared kernels, and require a failed acceptance row before any new kernel is accepted."
depends_on: [Q7, Q17, Q29]
reopen_only_if: "A required operator lacks a conforming existing kernel or a direct fused kernel is the only measured route to Q68."
```

## Q31 — Single agent protocol surface

```yaml
question_id: Q31
state: CLOSED
decision: "Cassette owns one canonical semantic broker protocol and thin external adapters; it does not force incompatible clients onto one wire encoding."
formal_contract:
  symbols: "CapabilityProfile={protocol_version,model_refs,modalities,context,reasoning,tools,structured_output,streaming,cancellation,training,source,performance_tiers}; RunRequest={idempotency_key,model_ref,input,context_ref?,generation,reasoning?,output_schema?,tools?}; RunEvent={run_id,sequence,type:started|reasoning_delta|output_delta|tool_call|tool_result|usage|completed|cancelled|failed,payload}; Operation is Q6."
  applicability: "Canonical transport is local JSONL or local HTTP with generated JSON Schema; adapters translate Codex, OpenAI Responses, Ollama, OpenClaw, Hermes, and custom contracts."
evidence:
  - status: SPECIFIED
    result: "E-008 proves the named clients have different stream, state, cancellation, and training surfaces."
build_instruction: "Make the canonical event log authoritative. Generate validators and simple field adapters; preserve an extension namespace for lossless provider fields and mark lossy mappings unsupported."
acceptance_check: "Round-trip canonical fixtures through every adapter and back; all exact fields and state transitions must survive, and unsupported semantics must produce capability rejection rather than fabrication."
depends_on: [Q6, Q10]
reopen_only_if: "A client requires a conversation or event semantic that cannot be represented in the canonical log."
```

## Q32 — Shared implementation across lifecycle operations

```yaml
question_id: Q32
state: CLOSED
decision: "All lifecycle operations share one identity engine, content store, range reader, hash verifier, transaction journal, plan registry, scheduler, revision graph, and protocol operation log."
formal_contract:
  symbols: "source_adapter -> identity/resolver -> range_reader -> content_addressed_pages -> {compiler,executor,trainer,exporter}; all writers -> transaction_journal -> revision_graph; all commands -> operation_log -> canonical_broker. No component may own a second digest, revision, page-state, cancellation, or error authority."
  applicability: "Download, verify, compile, infer, train, export, repair, update, and remove are commands over the same objects and states."
evidence:
  - status: OBSERVED
    result: "E-006 identifies existing numerical/runtime ownership; E-008 identifies the single broker boundary."
build_instruction: "Expose narrow library functions for resolve, range-read, verify, page-state transition, transaction, and operation events; reject lifecycle-specific copies of them in code review and Q29 accounting."
acceptance_check: "Trace one page and one cancellation token through every lifecycle operation and verify one identity, one state machine, and one error vocabulary."
depends_on: [Q5, Q6, Q22, Q29, Q31]
reopen_only_if: "A lifecycle operation requires materially different durability or identity semantics that cannot share the primitive."
```

## Q33 — Data-driven versus executable behavior

```yaml
question_id: Q33
state: CLOSED
decision: "Model semantics, mathematical certificates, and plan variation are immutable data; the harness validates and executes that data; numerical meaning remains in existing kernels."
formal_contract:
  symbols: "Declarative={tensor graph,page map,layout,precision planes,native routing policy,MATHS certificate {flattening,conditions,metrics,atoms,faces,minimal_nonfaces,cover,observation contract,description,residual,estimator,risk,composition,horizon},hardware predicates,semantic manifest,protocol mapping,invalidation edges}; deterministic harness={parse,validate,state transitions,schedule,commit,adapt}; trained semantic decisions={compiled atoms or selector,description,estimator calibration,precision allocation}; kernels={operators}. Manifests may select only capabilities enumerated by the harness schema."
  applicability: "No manifest may inject executable code, arbitrary paths, shell commands, network calls, or unbounded allocation."
evidence:
  - status: OBSERVED
    result: "E-002 shows safe data containers; E-006 shows reusable kernels; E-008 shows adapters can be schema-driven only where semantics align."
build_instruction: "Generate certificates, plans, and adapter maps from schemas, validate every enum, digest, witness, and bound, and reserve handwritten code for state transitions or operators that cannot be represented declaratively."
acceptance_check: "Add a supported model, mathematical certificate, and hardware plan using data only; malformed or collapsed certificate dimensions must fail before allocation or execution; Q29 must expose every remaining model-specific branch."
depends_on: [Q7, Q10, Q29, Q30, Q31, Q32]
reopen_only_if: "A supported architecture has safe behavior that cannot be expressed in the bounded schema."
```

## Q34 — Exact demonstrated contribution

```yaml
question_id: Q34
state: CLOSED
decision: "Cassette's admissible contribution claim is the complete conjunction: a source-general compiler and runtime that creates an immutable, removable, authoritative, drive-resident model cartridge; transforms compatible full models into provenance-linked, MATHS-certified executable revisions when native active state does not fit; executes them through bounded Apple unified memory; supports cartridge-resident derivative training and atomic revisions; and serves named agents on consumer-class Apple hardware at Q68 FRONTIER_CLASS gates with dual-baseline honesty. No isolated ingredient or pure theorem is claimed as the product."
formal_contract:
  symbols: "claimable(Cassette) iff every material clause maps to at least one LIVE-PROVEN Q80 row and Q78 passes; otherwise public_claim_state=WITHHELD."
  applicability: "The claim covers only model, Apple-compute, storage, training, and protocol tuples that live-pass. It does not claim every model, every Mac, every USB-C drive, zero OS swap, or laboratory parity where Q13 is unavailable."
evidence:
  - status: CHOSEN
    result: "E-010 shows collisions for isolated flash loading, SSD streaming, prompt pruning, and checkpoint loading. The pre-cutover product conjunction remains the only candidate supported by that search; Q35 requires a new search against the implemented MATHS-certified mechanism before any contribution claim."
build_instruction: "Attach each claim clause to machine evidence IDs and suppress the contribution statement until those records are LIVE-PROVEN."
acceptance_check: "Delete any one conjunction clause from the implementation evidence map: if no live row proves it, the claim must not emit; if an isolated prior-art phrase appears, replace it with the exact conjunction."
depends_on: [Q19, Q21, Q31, Q39, Q40, Q68, Q78, Q80]
reopen_only_if: "Q80 behavior differs from the claim or Q35 locates the complete conjunction."
```

## Q35 — Bounded collision check

```yaml
question_id: Q35
state: CLOSED
decision: "The 2026-08-05 bounded search found material collisions for every then-declared separate mechanism but no public artifact implementing Q34's entire conjunction; the claim remains narrowed to the conjunction and requires a new post-implementation search against the MATHS-certified mechanism."
formal_contract:
  symbols: "Search boundary={Apple LLM in a Flash, Apple IFPruning, SwiftLM and MLX SSD streamers, llama.cpp/ggml paging, ServerlessLLM, model-pruning and storage patents located by exact mechanism terms}; pre-2026-08-09 result does not cover the compatibility-complex/atom-cover/description-probe conjunction; collision requires one system or patent mapping every material Q34 clause, not a bag of references."
  applicability: "Technical collision record only; not patentability, validity, infringement, or freedom-to-operate advice. Search date and query vocabulary are part of the record."
evidence:
  - status: OBSERVED
    result: "E-010 records candidates and distinctions. Apple covers flash-aware loading and prompt-fixed pruning; SwiftLM covers Apple SSD MoE streaming; neither located source covers the complete writable source-general cartridge system."
build_instruction: "Preserve the collision matrix, repeat it against final component names, code, claims, patents, and release date after Q80, and amend Q34 on any complete or materially broader collision."
acceptance_check: "For every candidate, map each Q34 clause to present, absent, or unknown with a primary-source citation; any candidate with no absent material clause reopens Q34 and blocks the claim."
depends_on: [Q34]
reopen_only_if: "Cassette's implemented mechanism changes or new public art appears before release."
```

## Q36 — Diagnostic fixture ladder

```yaml
question_id: Q36
state: CLOSED
decision: "Fixtures isolate defects in seven ascending stages; F4 and F5 are binding falsification gates for the frontier thesis, and no stage below the frontier rows can mark Cassette complete."
formal_contract:
  symbols: "F0 malformed/valid manifests and headers; F1 deterministic content pages, hashes, interruption, and repair; F2 golden operators plus malformed/valid MATHS certificates; F3 tiny transformer with certified deterministic and fresh-stochastic execution, forced page failures, and KV/recurrent rollback; F4 3B-8B dense transformation, quality recovery, Tier-A training, and Tier-B certificate recovery; F5 20B-120B sparse/multimodal plus Tier-A training, Tier-B certificate recovery, and all protocol adapters; F6 one full-scale model per Q39 compute boundary; F7 complete Q80 matrix. Promotion requires all lower-stage directly coupled invariants. F4 GATE (binding): a permissively licensed 3-8B dense model compiled to a Q19-certified revision with touched_bytes_per_token<=0.25*native_active_bytes must cover the frozen Q15/Q16 protected conditions, declare and validate its per-atom/per-step plus peak/total resource certificate, complete the Q70 dense-fixture Tier-A and Tier-B rows, and achieve paired lower95CI(Qc/Q_teacher)>=0.95 across Q15 strata within a predeclared training budget. F5 GATE (binding): a 20B-120B sparse model must satisfy the same predicates at scale, complete its Tier-A and Tier-B rows, and produce Q37 mathematical-resource-versus-quality/service frontier curves whose predicted feasible point clears Q68 FRONTIER_CLASS inside the E-011 C1 decode budget. A failed gate emits a Q38 record and a mechanism revision; no frontier compiled row may execute before both gates pass."
  applicability: "Fixtures may be generated and small. Only F6/F7 establish frontier scale, service behavior, or completion."
evidence:
  - status: CHOSEN
    result: "The ladder isolates parser, storage, numerical, routing, training, and protocol faults without permitting proof-of-concept substitution."
build_instruction: "Give every fixture an immutable input, mathematical certificate when compiled execution is involved, expected failure locus, and exact invariant; run the smallest stage that can disprove the changed behavior, then run mandatory F7 before release."
acceptance_check: "Inject one defect owned by each stage and require first failure at that stage; verify that an F0-F5 pass cannot set release state COMPLETE and that frontier compiled rows are refused while an F4/F5 gate is unpassed."
depends_on: [Q16, Q17, Q20, Q25, Q30, Q31]
reopen_only_if: "A new subsystem lacks an isolating fixture before F6."
```

## Q37 — Scale-transfer evidence

```yaml
question_id: Q37
state: CLOSED
decision: "Diagnostic success transfers only for invariants with proven bounds; performance, quality, thermal behavior, certificate coverage, execution risk, and recovery require full-scale confirmation, and F4/F5 mathematical-resource frontier predictions are binding preconditions for attempting any frontier row."
formal_contract:
  symbols: "N_pages=ceil(S_exec/page_bytes); metadata=O(N_pages); lookup=O(1) expected or O(log N_pages) worst; La>=D_load/Bs+N_reads*l_read; Ld>=max(Dmiss/Bs,Hmem/Bm,F/Ccompute); KV=layers*tokens*state_bytes_per_layer_token; Adam_state>=10N_train or 14N_train B. Any measured superlinear metadata, queue collapse, cache cliff, thermal decay, condition-cover failure, or certified-resource overflow is a breakpoint."
  applicability: "F0-F5 may prove parsing, hashing, transaction, and asymptotic memory. F6/F7 alone prove frontier service and training."
evidence:
  - status: OBSERVED
    result: "E-001 establishes a concrete breakpoint: Kimi K3's 113.60 GB fixed native text path exceeds a 32 GB class before selected experts and state."
  - status: INFERRED
    result: "E-007 and E-009 establish training, I/O, and memory scaling floors."
build_instruction: "Record predicted and observed curves over atom count, rank, description bytes, metadata bytes, fresh traffic, error/risk, horizon, page/model/context sizes, and physical service; mark the first >10% residual or resource cliff and force every full-scale matrix row across all predicted breakpoints."
acceptance_check: "Fit the declared scaling functions on lower stages, predict F6 resource bounds before execution, and fail transfer if any observed peak or total description, metadata, fresh-sample, or fresh-traffic resource, or any latency, exceeds its prediction by >10% without a revised causal model and repeated F6 run."
depends_on: [Q12, Q19, Q28, Q36]
reopen_only_if: "A full-scale row exposes an unmodeled breakpoint or nonlinearity."
```

## Q38 — Compatibility-bound falsification

```yaml
question_id: Q38
state: CLOSED
decision: "A tuple is incompatible when any physical lower bound, mathematical-certificate requirement, or measured hard gate fails; the failure excludes only that tuple and mechanism."
formal_contract:
  symbols: "INCOMPATIBLE if S_peak>free_reserved_capacity or minimum_live_state>M or max(Dfresh/Bs,Hmem/Bm,F/Ccompute)>Q68 latency bound or Q17/Q18 quality fails or Q19 certificate coverage/error/risk/observation/physical conversion fails or unsupported_operator exists or training_state/endurance exceeds Q28/Q53/Q74. Record={tuple,mode,bound,measured,evidence,cause,next_mode_or_tuple}."
  applicability: "A failed native mode may proceed to compiled mode; a failed storage class may move upward; a failed training tier does not erase eligible inference. No failure makes a paper, simulator, or smaller fixture the product."
evidence:
  - status: INFERRED
    result: "E-009 supplies service lower bounds; E-001 supplies a concrete native K3 memory falsification for the 32 GB class."
build_instruction: "Evaluate cheap static bounds before transfer, mathematical feasibility and measured class bounds before compilation, and quality/certificate validity after preparation; persist the first decisive causal failure and continue the matrix."
acceptance_check: "Construct one failure for each predicate and verify deterministic exclusion, exact causal record, no silent threshold relaxation, and continued execution of independent Q80 rows."
depends_on: [Q7, Q17, Q18, Q19, Q28, Q37]
reopen_only_if: "The failed mechanism changes enough to alter its decisive bound."
```

## Q39 — Binding controlled-reference matrix

```yaml
question_id: Q39
state: CLOSED
revised: 2026-08-05 under the amended remit
decision: "The first release uses three public Apple classes in declared roles — C1 consumer thesis target, C2 consumer-pro target, C3 build-and-teacher infrastructure — and three pinned frontier model boundaries with Kimi K3 as the level exemplar. The headline row is the frontier compiled cartridge on C1. The former native-parity row on C3 is reclassified TEACHER_CORRECTNESS after E-011's static falsification. All storage is qualified as an assembled class, never a brand or connector."
formal_contract:
  symbols: "C1={M5 MacBook Air,32GB,153GB/s,fanless,role=THESIS}; C2={M5 Max MacBook Pro,128GB,614GB/s,active cooling,role=CONSUMER_PRO}; C3={M3 Ultra Mac Studio,512GB,819GB/s,active cooling,role=INFRASTRUCTURE}. S1={APFS NVMe,USB4 40Gb/s,>=2TB}; S2={APFS NVMe,Thunderbolt5,>=2TB}; S3={APFS NVMe,Thunderbolt5,>=4TB,writable endurance qualified}. Models: K3=moonshotai/Kimi-K3@9f62e4e9fffbd0a83ddd60e1c209d828994b3569 (level exemplar); Scout=meta-llama/Llama-4-Scout-17B-16E-Instruct@92f3b1597a195b523d8d9e5700e57e4fbb8f20d3; Qwen=Qwen/Qwen3-235B-A22B-Instruct-2507@ac9c66cc9b46af7306746a9250f23d47083d689e. frontier_reference(class)={revision: open_downloadable(revision) and total_bytes(revision)>=1e12 and native_active_state(revision)>M_ceiling(class)}; substituting an equal-or-greater-level model with a smaller fixed-path fraction is a recorded remit-level decision. Mandatory rows={C1/S1/FRONTIER-COMPILED-CERTIFIED+TierA+B (thesis headline, Q68 FRONTIER_CLASS, Q19 certificate, precondition F5 gate), C1/S1/Scout-least-invasive-Q40-modes-1-to-3-else-Q38-fail, C2/S2/Qwen-least-invasive-Q40-modes-1-to-3-else-Q38-fail, C3/S2/K3-NATIVE (TEACHER_CORRECTNESS: routing and declared-capability correctness including 1,048,576-token context, absolute service report, teacher trace generation; no parity or value gate), C3/S3/K3-COMPILED-CERTIFIED+TierA+B (portability, certificate recovery, and training row, usability floors)}."
  applicability: "Source acquisition uses exact Hugging Face revisions; the same immutable artifacts are re-exposed as pinned Ollama blobs and Tinker-export descriptors for adapter conformance. Every named client runs against each callable capability tier through Q76. B_native for each consumer class is pinned at matrix freeze under Q13."
evidence:
  - status: OBSERVED
    result: "E-001 fixes K3; public Hugging Face APIs fixed Scout and Qwen revisions and reported 217,315,712,145 B and 470,211,497,053 B repository artifact totals respectively."
  - status: SPECIFIED
    result: "E-003 fixes Apple class ceilings; E-005 requires measured storage qualification."
  - status: INFERRED
    result: "E-011 falsifies native K3 service parity on C3 (5.87 tok/s ceiling against the 10 tok/s floor) and fixes the C1 compiled decode budget (15.3 GB touched per token at 100% utilization)."
build_instruction: "Encode the matrix in machine data, bind every compiled row to one Q19 certificate, measure each exact assembled storage path with Q42, pin source and runtime commits, pin B_native per consumer class at freeze, refuse frontier compiled rows before their F5 gate, and execute every mandatory row without substituting personal hardware anecdotes."
acceptance_check: "A clean runner enumerates exactly the mandatory rows, roles, source digests, baselines, clients, training tiers, gates, and preconditions; release fails if any row is absent, substituted, measured under an unqualified class, or executed with an unpassed gate; the TEACHER_CORRECTNESS row must be structurally unable to emit a parity or value label."
depends_on: [Q7, Q13, Q15, Q21, Q36, Q37, Q38]
reopen_only_if: "A named public artifact becomes unavailable, an Apple class leaves support, a superior frontier_reference is adopted by remit-level decision, or a static bound proves a row impossible and Q38 records the replacement mechanism rather than lowering the boundary."
```

## Q40 — Native structure versus model transformation

```yaml
question_id: Q40
state: CLOSED
decision: "Use the least invasive passing mode in this order: byte-identical layout, exact native sparsity, exact quantization/layout conversion, predictive prefetch with native routing, then a separately identified MATHS-certified compiled revision. The final mode is a certificate class, not a prescribed top-k, shared-core, or prompt-router decomposition."
formal_contract:
  symbols: "For each compiled tensor/operator target T and declared flattening, emit K_{eta,r}, atom witnesses {A_i}, service faces {F_i}, a cover of the protected condition set, observation contract, resident descriptions {B_i}, residual or exact execution relation, epsilon_exec, delta_exec_total, composition maps, certified horizon, and physical resource conversion as Q19. A shared core, sparse dictionary, block description, quantized description, or fresh residual sampler is admitted only as a declared specialization. Native prompt predictors may prefetch but never override source routing."
  applicability: "Dense models require complete native weights resident or a certified compiled representation. MoE models retain native router semantics when their active state passes; a compiled child may use different atoms or selectors only under its own Q1 identity and Q19 evidence. A matrix row whose allowed_q40_modes stop at mode 3 fails with a Q38 record when none passes; it may not advance silently into compiled mode. Compiled evaluation requires a separate Q19-certified row, compiled gate, and Q70 Tier-B path. Multimodal and recurrent components transform only with capability-specific condition, composition, and state proofs."
evidence:
  - status: INFERRED
    result: "E-001/E-009 prove K3's native fixed path cannot satisfy the 32 GB row. E-012 proves that invariants constant under the declared projection-commuting ambient unitaries, including their ordinary Hilbert data, do not determine low-rank condition compatibility; fresh residual sampling supplies only a conditional within-atom upper bound."
build_instruction: "Evaluate modes in order, stop at the first Q12-Q20 pass, derive condition metrics and the protected observation contract from immutable teacher traces, emit the complete Q19 certificate, train only its declared revision-owned objects, and issue a new Q1 identity for every lossy or trained transform."
acceptance_check: "For each architecture class, demonstrate that the selected mode is the least invasive passing mode by running the prior mode through Q38; compiled revisions must independently recompute and pass Q17-Q20, complete-capacity Q58, and every MATHS.md certificate dimension."
depends_on: [Q7, Q17, Q18, Q19, Q20, Q30, Q38, Q39]
reopen_only_if: "A less invasive mode gains a qualified plan, a certificate theorem fails, or the selected compiled representation fails Q17/Q18/Q19."
```

## Q41 — Supported physical cartridge classes

```yaml
question_id: Q41
state: CLOSED
decision: "A cartridge class is the measured tuple of media, controller, bridge, enclosure, transport, filesystem, capacity, power, thermal behavior, and durability; USB-C alone carries no compatibility meaning."
formal_contract:
  symbols: "eligible(s,mode)=capacity(s)>=Q53 and p05_sustained_Bs(s,pattern)>=required_Bs and p99_latency<=plan_limit and durable_flush(s)>=required(mode) and disconnect_identity=true and thermal_floor=true and, for training, endurance_known=true. Bs_service<=min(B_link_payload,B_bridge,B_media_steady,B_filesystem_cache)."
  applicability: "Removable flash, SATA SSD, and NVMe SSD may qualify. Low-end flash commonly remains acquisition/cold-store or read-only unless it passes the same predicate. Connector shape, brand, and advertised peak never qualify a class."
evidence:
  - status: SPECIFIED
    result: "E-005 separates transport, bridge, media, filesystem, and durability authorities."
build_instruction: "Create a signed profile from Q42 measurements and immutable class descriptors; bind each execution/training plan to minimum profile predicates, not product names."
acceptance_check: "Test devices sharing a USB-C connector but differing in bridge/media behavior; each must classify independently and a failed component must disqualify only the affected mode."
depends_on: [Q28, Q38]
reopen_only_if: "A new transport or media class exposes equivalent measurable and durable semantics."
```

## Q42 — Sustained storage qualification

```yaml
question_id: Q42
state: CLOSED
decision: "Storage qualification replays Cassette page patterns through cold, warm, queue-depth, cache-exhaustion, and long-duration phases and uses lower-tail sustained results."
formal_contract:
  symbols: "Measure read/write sizes {4KiB,64KiB,1MiB,4MiB,16MiB,32MiB}, alignments {4KiB,page}, patterns {sequential,uniform-random,Zipf-random,Q19-trace,mixed-training}, QD {1,2,4,8}, states {cold,warm}, and durations {until >=2*declared device cache or 30min, sustained >=60min}. Record throughput p05/p50/p95, latency p50/p95/p99/max, IOPS, host/device writes, errors, thermal-state events, and flush latency. Pass iff the p05 throughput and p99 latency satisfy every bound of the bound plan for the full sustained interval."
  applicability: "Measurements use files larger than host RAM for cold tests and verified uncached reads where supported; warm results are reported separately and never substitute for cold."
evidence:
  - status: INFERRED
    result: "E-005 requires assembled-path measurement; E-009 converts measured values into service bounds."
build_instruction: "Ship one bounded profiler that emits a content-addressed profile and uses captured native/compiled page traces, not a generic peak-only disk benchmark."
acceptance_check: "Throttle or exhaust a qualifying device's cache and require classification to follow sustained p05/p99 values; advertised link rate must never appear as measured Bs."
depends_on: [Q12, Q19, Q41]
reopen_only_if: "Live traces introduce a materially different I/O distribution."
```

## Q43 — Transport and enclosure variables

```yaml
question_id: Q43
state: CLOSED
decision: "The storage profile records every variable that can change the service or durability envelope and invalidates itself when the negotiated path changes."
formal_contract:
  symbols: "Profile inputs={media_type,capacity,logical_block,physical_block,controller,bridge_id,bridge_firmware,enclosure_id,transport_protocol,negotiated_rate,port_path,hub_path,cable_capability,power_contract,queue_depth,alignment,TRIM_support,write_cache,flush_result,encryption,filesystem,free_extents,SLC_cache_breakpoint,thermal_curve,SMART_or_health}; profile_id=H(inputs,measurements,OS_build,profiler_version)."
  applicability: "Unavailable telemetry is UNKNOWN, never an assumed pass. A port, hub, cable, firmware, filesystem, or OS change requires at least the dependent Q42 subset again."
evidence:
  - status: SPECIFIED
    result: "E-005 identifies transport and durability layers."
build_instruction: "Obtain public system descriptors where available, measure the rest, and feed only validated values to Q41/Q47/Q53/Q74."
acceptance_check: "Change cable, hub, port, bridge firmware, encryption, queue depth, or free-space fragmentation and verify the profile identity changes and dependent plans revalidate."
depends_on: [Q41, Q42]
reopen_only_if: "A new variable measurably alters service while absent from the profile."
```

## Q44 — Filesystem and allocation contract

```yaml
question_id: Q44
state: CLOSED
decision: "Writable first-release cartridges use locally attached APFS with verified durable synchronization; other filesystems are import/export or read-only until they pass an equivalent transaction qualification."
formal_contract:
  symbols: "Paths use lowercase digest names and never depend on case behavior. Physical page objects are 4 MiB canonical chunks aligned to >=4 KiB; read coalescing may form 1-32 MiB runs. Preallocate committed extents. Sparse files and clones are optional space optimizations, never correctness authorities. Commit requires data write -> readback hash -> fsync/F_FULLFSYNC -> root write -> atomic generation pointer -> fsync/F_FULLFSYNC -> remount verification."
  applicability: "APFS encryption is allowed only when Q42 passes. exFAT and network filesystems cannot host mutable authority in the first release."
evidence:
  - status: SPECIFIED
    result: "E-005 records APFS object and durable-flush authorities."
build_instruction: "Probe required operations at format/activation, reject unsupported flush or atomicity behavior for writable mode, and encode no correctness dependency on undocumented clone or sparse allocation behavior."
acceptance_check: "Run power-cut transaction fixtures under full, fragmented, encrypted, and read-only remount states; remount must expose exactly the last valid generation."
depends_on: [Q4, Q25, Q41]
reopen_only_if: "Another filesystem passes the identical durability, identity, allocation, and portability suite."
```

## Q45 — Storage-to-compute copy path

```yaml
question_id: Q45
state: CLOSED
decision: "The preferred GPU path encodes an exact cartridge file range into a preallocated Metal resource and fences compute on the I/O command event; the physical copy count remains measured and must not be advertised as zero-copy."
formal_contract:
  symbols: "GPU path: external blocks -> bridge/transport -> macOS filesystem/I/O -> Metal buffer -> kernel. CPU fallback: aligned pread -> bounded host buffer -> backend resource. Minimum application-visible copies are zero for Metal-I/O file-to-resource and one host fill for pread, but physical DMA/cache copies are implementation-defined. ANE path exists only through a qualified Core ML whole-model package."
  applicability: "Use 4 KiB file alignment and runtime-required resource alignment; coalesce adjacent page ranges; keep I/O and compute queues concurrent with explicit event dependencies."
evidence:
  - status: SPECIFIED
    result: "E-004 proves Metal asynchronous range loading and synchronization but not physical zero-copy; E-006 supplies fallback loaders."
build_instruction: "Implement Metal I/O through existing runtime hooks where possible, retain a measured pread fallback, expose bytes and fence times, and never route page-addressed execution to ANE without a public contract."
acceptance_check: "Trace cold and warm range loads, verify exact destination bytes before kernels, prove overlap without a readiness race, and report—not infer—the effective copies and bandwidth."
depends_on: [Q30, Q42, Q44]
reopen_only_if: "Apple publishes a stronger direct-storage or ANE page-resource contract."
```

## Q46 — Operating-system interference model

```yaml
question_id: Q46
state: CLOSED
decision: "Cassette controls its own files, cache policy, memory admission, and power assertions; OS page cache, compression, swap, indexing, backup, encryption, and power management remain observed interference, with unsupported states rejected rather than denied."
formal_contract:
  symbols: "Interference={memory_pressure,compressed_bytes,swap_delta,cache_state,thermal_state,power_state,indexing_IO,backup_IO,encryption,filesystem_maintenance}; run is valid only if internal Cassette model-file writes=0, pressure never reaches hard, profile assumptions hold, and no unaccounted competing I/O invalidates Q42. OS-wide model-byte swap absence is NOT_PROVABLE on general macOS."
  applicability: "Supported macOS versions are pinned in Q39/Q80 result manifests. Streaming may use documented no-cache advice; reusable pages use explicit C rather than relying on invisible OS cache state."
evidence:
  - status: SPECIFIED
    result: "E-003 exposes memory budget information; E-005/E-006 distinguish filesystem cache and application cache behavior."
build_instruction: "Request appropriate no-idle execution during active operations, disable cartridge indexing/backup where permitted and recorded, sample pressure/thermal/power state, abort on hard pressure, and disclose the narrow internal-storage claim."
acceptance_check: "Induce pressure, compression, competing I/O, sleep, encryption, and low-power states; require either bounded compliant execution or a typed unsupported/interrupted result without internal model files."
depends_on: [Q2, Q42, Q45]
reopen_only_if: "macOS adds enforceable isolation or removes a required observation/control."
```

## Q47 — Unified-memory budget function

```yaml
question_id: Q47
state: CLOSED
decision: "Cassette computes a conservative live memory budget before every admission and recomputes it as context, cache, other processes, and thermal state change."
formal_contract:
  symbols: "Reserve=max(4GiB,0.25*M_physical). M_ceiling=min(M_physical-Reserve,0.90*recommendedMaxWorkingSetSize). M=M_ceiling-M_exec-M_other_observed. Admit iff peak(|W|+|C|+|K|+|A|+|R|+training_window)<=M, where C includes the Q19 resident description and metadata and W includes declared fresh correction pages. Eviction order={unused speculative pages,cold C,precision corrections,recomputable activations}; W required for the current certified operation and committed K cannot be evicted. On hard pressure cancel before new allocation."
  applicability: "The 25% reserve is the first-release floor and may increase after controlled qualification, never decrease silently for a published plan."
evidence:
  - status: SPECIFIED
    result: "E-003 supplies physical and recommended working-set inputs; E-009 supplies the residency inequality."
build_instruction: "Use checked 64-bit byte arithmetic, import exact Q19 description/metadata/fresh-page maxima, predict maximum KV/training growth, expose the complete budget ledger, and bind plan selection to the minimum budget observed during qualification."
acceptance_check: "Sweep context, page cache, batch, and competing-memory loads to every boundary; no accepted operation may cause hard pressure or positive swap growth attributable to continued Cassette allocation."
depends_on: [Q2, Q12, Q19, Q23]
reopen_only_if: "Controlled class measurements prove a different reserve is required to maintain Q69."
```

## Q48 — Sustained Apple and storage thermal envelope

```yaml
question_id: Q48
state: CLOSED
decision: "Each compute/storage plan is qualified on a sustained curve; peak cold-device throughput is irrelevant after either Apple or cartridge throttles."
formal_contract:
  symbols: "Run each Q39 class for >=120 min and >=20,000 generated tokens for inference, and through >=2*SLC_cache_estimate writes plus >=120 min for training. Report five-minute windows of Rd,Bs,Bm_proxy,power_state,thermal_state,errors,host_writes. Pass iff every post-warmup window meets Q68, p05 throughput decay from first stable 20-minute window <=10%, no critical thermal state persists >60s, and no integrity error occurs."
  applicability: "Fanless and actively cooled classes retain separate curves. Missing external temperature telemetry is acceptable only when service and error behavior still pass; it remains UNKNOWN."
evidence:
  - status: INFERRED
    result: "E-003 class cooling differs; E-005 requires media cache-exhaustion and sustained measurement."
build_instruction: "Select queue depth, read grouping, concurrency, and write duty cycle from the sustained curve; throttle before the measured failure knee and reprofile when enclosure or environment class changes."
acceptance_check: "Run above and below the selected duty cycle on every class, observe the knee, and require the scheduler to remain on the passing side for the full interval."
depends_on: [Q12, Q28, Q39, Q42, Q47]
reopen_only_if: "A hardware, OS, enclosure, or cooling change moves the measured knee."
```

## Q49 — Removable-cartridge lifecycle

```yaml
question_id: Q49
state: CLOSED
decision: "Every operation is governed by a removable-volume identity state machine; disconnect invalidates all handles and no byte is trusted again until remount identity and root verification complete."
formal_contract:
  symbols: "UNMOUNTED -> MOUNTED_UNVERIFIED -> MOUNTED_VERIFIED -> ACTIVE -> QUIESCING -> MOUNTED_VERIFIED; any bus loss -> DISCONNECTED; sleep -> SLEEPING; reconnect/wake/port migration -> REVALIDATING; read-only -> READ_ONLY; digest/root failure -> FAILED. Identity={cartridge_uuid,filesystem_uuid,root_generation,root_digest}."
  applicability: "Download, compile, inference, training, export, repair, and removal. Device replacement with copied files is a new physical profile but may retain logical cartridge identity after complete verification."
evidence:
  - status: SPECIFIED
    result: "E-005 supplies Disk Arbitration and durability boundaries; E-008 supplies agent-visible errors and status."
build_instruction: "Close stale handles, stop command submission, preserve last committed token or training step, remount by exact identity, verify root and touched pages, then resume only resumable operations."
acceptance_check: "Inject disconnect, reconnect, sleep, wake, bus reset, port change, UUID mismatch, read-only remount, and cloned replacement at every operation phase; require deterministic state and no stale read or write."
depends_on: [Q5, Q20, Q25, Q44]
reopen_only_if: "A supported transport has lifecycle events not reducible to these states."
```

## Q50 — Remote metadata preflight

```yaml
question_id: Q50
state: CLOSED
decision: "Preflight normalizes every remotely knowable compatibility field with an independent trust state and records exact deferred checks for the rest."
formal_contract:
  symbols: "RemoteMetadata={identity,total_bytes,artifact_count,artifact_digests?,format,architecture,total_parameters,active_parameters?,dtype_quantization,context,modalities,operators?,custom_code,tokenizer,processor,template,license,gating,revision_ancestry,training_precision?,source_validators}; each field has {value,trust:EVIDENCE_DIGESTED|DECLARED|PARSED|ABSENT,authority}."
  applicability: "Repository cards are declarations; immutable manifests are sourced; safe header ranges are parsed; no field inherits another field's trust."
evidence:
  - status: OBSERVED
    result: "E-001 demonstrates exact size and tensor inference beyond a model card; E-002 supplies source and container contracts."
build_instruction: "Populate fields without executing code, compute capacity and architecture predicates, and carry ABSENT fields into Q56 rather than inventing defaults."
acceptance_check: "Feed contradictory card, config, manifest, and header fixtures; the highest-authority immutable bytes must prevail and every conflict must remain in the record."
depends_on: [Q1, Q8, Q9]
reopen_only_if: "A source exposes signed semantic metadata that changes the trust order."
```

## Q51 — Resumable multi-terabyte transfer

```yaml
question_id: Q51
state: CLOSED
decision: "Acquisition writes fixed chunks directly to reserved cartridge extents, verifies immutable source identity throughout, and commits only after both chunk-local and source-object integrity pass."
formal_contract:
  symbols: "TransferChunk={artifact_id,offset,length,BLAKE3_digest,state}; default length=4MiB except tail. PartialState={source_revision,object_size,validator,completed_interval_set,chunk_digests,contiguous_source_hash_offset,serialized_hash_state}. If authoritative chunk hashes exist, verify independently; otherwise advance the authoritative whole-object hash only over the contiguous completed prefix and checkpoint hash state. Final proof={all intervals covered,source validator unchanged,whole digest equal,all local chunk digests equal}; no post-completion full reread is required."
  applicability: "HTTP ranges, Ollama blobs, and equivalent immutable range sources. If neither a stable validator nor digest exists, transfer cannot become authoritative."
evidence:
  - status: SPECIFIED
    result: "E-002 provides range and immutable-source contracts."
build_instruction: "Preallocate D extents, schedule bounded parallel ranges, hash network bytes before write, read back each chunk once, checkpoint interval/hash state durably, and discard all progress if revision, size, validator, or expected digest changes."
acceptance_check: "Interrupt a multi-shard transfer at random byte ranges, corrupt network and local chunks, change the source validator, and resume; final commit must need no whole-artifact reread after completion and must reject every mismatch."
depends_on: [Q1, Q5, Q44, Q50]
reopen_only_if: "A source forbids ranges or supplies only mutable unverified objects."
```

## Q52 — Minimal source-adapter boundary

```yaml
question_id: Q52
state: CLOSED
decision: "A source adapter has five operations and owns no lifecycle state beyond authentication translation."
formal_contract:
  symbols: "Adapter={resolve(SourceDescriptor)->ResolvedSource, enumerate(revision)->Artifact[], read_metadata(revision,ranges?)->MetadataEvidence, open_range(artifact,offset,length,validator)->ByteStream, license_and_auth(revision)->Requirements}; all outputs use Q1/Q9/Q50 schemas and canonical errors."
  applicability: "Hugging Face, Ollama, Tinker exports, and future sources. Adapter code may construct requests and parse source responses; it may not allocate cartridge layouts, commit revisions, schedule compilation, or serve inference."
evidence:
  - status: SPECIFIED
    result: "E-002 and E-008 distinguish source semantics while exposing the common artifact operations."
build_instruction: "Implement adapters as stateless modules selected by descriptor kind; route credentials by opaque reference and all byte transfer through Q51."
acceptance_check: "Replace each source with a deterministic fixture server and run the same acquisition state machine unchanged; source-specific branches outside the adapter fail Q29."
depends_on: [Q5, Q9, Q31, Q50, Q51]
reopen_only_if: "A source requires a sixth semantic operation that cannot be expressed as one of the five."
```

## Q53 — Cartridge capacity admission

```yaml
question_id: Q53
state: CLOSED
decision: "Cassette reserves the maximum exact extent demand of the requested lifecycle transition before transferring or mutating any model byte and never overcommits that reservation."
formal_contract:
  symbols: "S_required=max_over_operation_phases(S_committed+S_inflight+S_candidate+S_rollback+S_optimizer+S_master+S_dataset+S_precision+S_journal+S_repair)+S_safety; S_safety=max(8GiB,0.05*S_device). Admit iff allocatable_verified_free>=S_required and every required extent can be preallocated; checked unsigned arithmetic is mandatory."
  applicability: "Download, transform, inference cache persistence, precision refinement, training, update, repair, export, rollback, and garbage collection each emit their phase vector. Filesystem-reported free bytes without successful reservation are insufficient."
evidence:
  - status: OBSERVED
    result: "E-001 fixes K3 source bytes; E-007 fixes optimizer lower bounds; E-005 fixes filesystem effects."
build_instruction: "Compute the phase maximum from immutable manifests and operation parameters, reserve it, expose the byte ledger, and release reservation only at terminal cleanup."
acceptance_check: "Test exact-boundary, fragmented, concurrent-reservation, growing-transform, training, and repair cases; fail before network or mutation when any phase exceeds available reserved capacity."
depends_on: [Q4, Q21, Q23, Q28, Q44]
reopen_only_if: "A lifecycle phase owns storage absent from the equation."
```

## Q54 — Revision and delta acquisition

```yaml
question_id: Q54
state: CLOSED
decision: "A revision update reuses unchanged content pages and downloads verified changed objects or deltas only when exact ancestry and target identity are known; otherwise it performs a complete immutable acquisition."
formal_contract:
  symbols: "ApplyDelta(base,target,d) iff I_base equals d.base_id and H(d)=declared_delta_digest and reconstruct(base,d) yields every target artifact digest and I_target. Unchanged page digest implies reuse. Changed source tensors invalidate the Q27 closure. The old root remains callable until target commit."
  applicability: "Source-supplied deltas, changed-shard reuse, and Cassette-generated page deltas. Binary patching without target digests is forbidden."
evidence:
  - status: SPECIFIED
    result: "E-002 provides immutable revisions and object digests; Q1/Q3 provide ancestry."
build_instruction: "Resolve target before transfer, compare artifact/page digests, acquire missing content through Q51, rebuild affected plans, and commit a child root through Q60/Q73."
acceptance_check: "Apply valid, wrong-base, corrupt, interrupted, and ancestry-fork deltas; only the valid target may publish and rollback must retain the exact base."
depends_on: [Q1, Q3, Q27, Q51, Q53]
reopen_only_if: "A source publishes a stronger authenticated delta protocol requiring additional identity fields."
```

## Q55 — Custom-code containment

```yaml
question_id: Q55
state: CLOSED
decision: "Cassette never executes repository-supplied model code during inspection or acquisition. First-release execution accepts only graphs whose operators exist in pinned trusted runtimes; arbitrary remote Python, pickle, shell, dynamic libraries, and `trust_remote_code` models are unsupported."
formal_contract:
  symbols: "inspectable iff artifacts in {SafeTensors,GGUF,JSON,text,image-processor-data,declared safe binary schema}; executable iff operator_set subset pinned_dispatch and no artifact requests code execution, network, credentials, arbitrary filesystem, JIT source, or unbounded allocation. Future plugin identity must include source digest, toolchain, dependency lock, sandbox policy, reproducible binary digest, and explicit capabilities."
  applicability: "Official operators integrated into a pinned MLX, ggml, llama.cpp, or Transformers-derived runtime are trusted build dependencies, not repository code."
evidence:
  - status: SPECIFIED
    result: "E-002 establishes data-only containers; E-006 establishes pinned runtime ownership."
build_instruction: "Parse with non-executing readers, reject pickle and executable auto-map paths, disable network in preparation/runtime, and keep credentials outside all model processes and cartridge objects."
acceptance_check: "Supply malicious pickle, template, path, auto-map, native library, and custom-op fixtures; none may execute or access network/credentials, and each must produce a typed containment rejection."
depends_on: [Q7, Q8, Q30, Q50]
reopen_only_if: "A mandatory Q39 operator lacks trusted implementation and a hermetic plugin path is built and qualified."
```

## Q56 — Compatibility decision before transfer

```yaml
question_id: Q56
state: CLOSED
decision: "Preflight returns exactly one of SUPPORTED, SUPPORTED_AFTER_PREPARATION, METADATA_INSUFFICIENT, or UNSUPPORTED with a complete causal record."
formal_contract:
  symbols: "SUPPORTED iff native plan predicates pass from DIGESTED/PARSED metadata; SUPPORTED_AFTER_PREPARATION iff a declared transform and all static resource/operator predicates pass but Q17-Q19 evidence must be generated; METADATA_INSUFFICIENT iff a bounded named range/header check can decide; UNSUPPORTED iff a decisive Q7/Q38/Q53/Q55 predicate fails. Result={class,reasons,required_bytes,memory_bound,storage_bound,training_tiers,deferred_checks,evidence}."
  applicability: "A compiled revision is not callable merely because preflight says SUPPORTED_AFTER_PREPARATION; it must pass preparation validation."
evidence:
  - status: INFERRED
    result: "Q7/Q8/Q38/Q50 supply deterministic predicates and trust states."
build_instruction: "Evaluate predicates in cheapest-failure order, preserve all unknowns, and return the exact range reads or transform validation needed next."
acceptance_check: "Golden records exercise all four outcomes; adding absent metadata may advance but never silently weaken a prior decisive UNSUPPORTED cause."
depends_on: [Q7, Q8, Q38, Q50, Q53, Q55]
reopen_only_if: "A fifth semantically distinct pre-transfer outcome appears."
```

## Q57 — Canonical cartridge representation

```yaml
question_id: Q57
state: CLOSED
decision: "Linked representations are necessary: immutable source provenance, content-addressed semantic pages, and immutable executable/training revision manifests share bytes but retain distinct authority."
formal_contract:
  symbols: "Page={digest:BLAKE3,length<=4MiB,payload}; Segment={segment_id,ordered_pages,<=1GiB}; TensorMap={semantic_tensor_id,shape,dtype,codec,plane,spans[(page_digest,offset,length,tensor_offset)]}; Root={Q1 identity,parents,provenance,semantic_assets,tensor_maps,operators,plans,deltas,integrity_root}. Manifests use RFC8785 canonical JSON; page indexes are sorted fixed-schema records whose logical digest is representation-independent. Authority is one durable root generation."
  applicability: "Source blobs may be retained or discarded under Q3. Precision corrections and training deltas are separate pages. Export reconstructs target tensors by TensorMap."
evidence:
  - status: SPECIFIED
    result: "E-002 shows no one source container serves safe source preservation, paging, training, and every export; E-005 supplies durable roots."
build_instruction: "Use 4 MiB canonical pages, coalesce adjacent reads by plan, deduplicate by digest, keep semantic tensors independent of physical segment order, and never edit committed segments or roots."
acceptance_check: "Import SafeTensors and GGUF, relocate/repack segments without changing logical root, resolve every tensor span, append training deltas, and export eligible forms with no duplicate parameter authority."
depends_on: [Q1, Q3, Q4, Q44, Q51]
reopen_only_if: "Q42 proves the 4 MiB content boundary prevents Q68 and a new canonical size passes all existing plans."
```

## Q58 — Proof of complete parameter capacity

```yaml
question_id: Q58
state: CLOSED
decision: "Compilation emits a total source-to-executable contribution map; lossless transforms prove bijection, while lossy transforms name every approximation and bind the Q19 atom, description, execution, composition, and observation certificate to Q17/Q18 evidence."
formal_contract:
  symbols: "Map m: source_contributions -> executable_contributions. Lossless requires m total, injective over value contributions, reconstructable, and digest-equal after inverse. Lossy requires m total with each source contribution classified {represented,merged,quantized,atom_conditioned,stochastically_corrected}; omitted is forbidden; every class records transform/error bound, atom/service-face relation, description/residual relation, and observation boundary. Semantic assets/operators require a total identity or explicit equivalent implementation map."
  applicability: "Parameters include routed/shared experts, embeddings, output heads, normalization, attention/recurrent/vision tensors, precision planes, tokenizer/processors/templates, and required operators."
evidence:
  - status: OBSERVED
    result: "E-001 enumerates 497,220 K3 tensors and exact category bytes, providing a frontier-scale completeness ledger."
  - status: INFERRED
    result: "Q18 supplies behavioral reachability for lossy conditional mappings."
build_instruction: "Emit the map while parsing source headers, reconcile source and destination byte/element counts, record transformations and Q19 certificate relations per span, and bind it to the executable root."
acceptance_check: "Account for every E-001 tensor and semantic asset; remove, duplicate, mis-map, make unreachable, or detach one contribution from its atom/description/residual certificate and require structural failure before model activation."
depends_on: [Q1, Q3, Q17, Q18, Q40, Q57]
reopen_only_if: "A model has non-tensor learned state not represented by the contribution taxonomy."
```

## Q59 — Multiple hardware plans without weight duplication

```yaml
question_id: Q59
state: CLOSED
decision: "Hardware plans contain references, schedules, mathematical-certificate specializations, and budgets only; all plans resolve the same semantic page digests and precision contributions."
formal_contract:
  symbols: "Plan={profile_predicate,Q19_certificate_digest,condition_selector,atom_refs,description_budget,metadata_budget,fresh_sample_or_exact_read_budget,error_risk_horizon,page_order,read_groups,precision_budget,kernel_dispatch,concurrency,prefetch_policy,memory_schedule,expected_metrics}; plan_weight_payload_bytes=0; sum(plan_metadata)<=min(0.01*S_exec,4GiB); select is Q11."
  applicability: "A plan may omit optional correction planes only if its revision-quality evidence covers that precision tier. A plan requiring different trained values creates a child revision."
evidence:
  - status: INFERRED
    result: "Q57 separates semantic pages from physical plans; E-003/E-005 supply profile dimensions."
build_instruction: "Generate plans from measured profiles and one immutable Q19 certificate, reference page digests and TensorMap spans, and store expected mathematical and physical bounds plus evidence IDs."
acceptance_check: "Add, delete, and switch plans while page payload digests and root capacity mapping remain unchanged; reject any plan carrying copied weights."
depends_on: [Q11, Q47, Q57]
reopen_only_if: "A kernel requires a duplicated packed weight form that cannot be generated transiently within Q68."
```

## Q60 — Recoverable compilation transaction

```yaml
question_id: Q60
state: CLOSED
decision: "Compilation is a resumable content transaction whose incomplete objects are never trusted by name, size, or prior process state—only by readback digest and a committed journal record."
formal_contract:
  symbols: "For each output page: PLAN -> ALLOCATE_TEMP -> WRITE -> READBACK_HASH -> COMMIT_PAGE_RECORD -> RELEASE_DEAD_SOURCE_EXTENT. Then WRITE_INDEX -> VERIFY_TOTAL_MAP -> WRITE_CANDIDATE_ROOT -> FULLFSYNC -> ATOMIC_GENERATION -> FULLFSYNC. Resume scans journal, rehashes only uncommitted or suspect pages, and reconstructs the remaining dependency frontier. GC deletes only unreachable temp extents after a valid root exists."
  applicability: "Native layout, deterministic conversion, quantization, Q19-certified compilation, and incremental recompilation."
evidence:
  - status: SPECIFIED
    result: "E-005 supplies durability; Q4 supplies bounded extent reclamation; Q57 supplies page/root identities."
build_instruction: "Persist transform version, inputs, random seeds, statistics, dependency order, and page results; ensure repeated execution produces the same logical root for deterministic transforms."
acceptance_check: "Terminate compilation after every write/flush/release point, corrupt temp and journal objects, remount, and obtain exact resume or typed unrecoverable-source reacquisition without exposing a partial root."
depends_on: [Q4, Q25, Q53, Q57, Q58]
reopen_only_if: "A compiler stage cannot declare a bounded deterministic resume frontier."
```

## Q61 — Layout evolution after training

```yaml
question_id: Q61
state: CLOSED
decision: "A tuned child reuses its parent's layout only while changed dependency hashes remain local and every reused mathematical witness and physical bound recomputes exactly; otherwise it compiles a new immutable layout while preserving the parent."
formal_contract:
  symbols: "Incremental layout is allowed iff operator/tokenizer/context schemas are unchanged; every carried condition metric, atom witness, service face, minimal-nonface record, cover, observation contract, description residual, estimator bound, composition map, and physical schedule recomputes from unchanged input digests; and Q17-Q19 pass after the Q27 closure. Any changed certificate input or failed witness requires a new certificate and every transitively dependent layout object."
  applicability: "Adapter-only children may share base layout and add delta gather plans when the recomputation predicate passes. Atom/selector, description, estimator, observation, precision, and base-page updates invoke Q27 closure."
evidence:
  - status: CHOSEN
    result: "Digest and route-distribution thresholds bound incremental plan drift without mutating a valid parent."
build_instruction: "Trace post-training protected conditions and activations, recompute the complete affected certificate closure, reuse only digest-identical unaffected objects, and publish all results as a child revision."
acceptance_check: "Change each certificate input independently; exact unchanged inputs must reuse only their unaffected Q27 objects, while every changed witness or bound must invalidate its complete transitive closure. The parent remains callable."
depends_on: [Q22, Q27, Q40, Q57, Q60]
reopen_only_if: "Full-scale evidence shows the thresholds admit stale layouts or force unnecessary full compilation."
```

## Q62 — Page integrity and repair

```yaml
question_id: Q62
state: CLOSED
decision: "Every page has an independent digest and every root has a Merkle aggregate; a mismatch removes the page from residency immediately and degrades the revision until verified repair completes."
formal_contract:
  symbols: "VALID -> SUSPECT -> VERIFYING -> VALID|CORRUPT -> REPAIRING -> VALID|UNAVAILABLE. Page identity=BLAKE3(payload); revision_integrity_root=Merkle(page identities,manifests,semantic assets). Repair source order={other verified local copy,source reacquisition by Q1/Q54,declared parity}; repaired bytes must match original page digest. New runs are rejected while any potentially addressable required page is UNAVAILABLE; pinned runs continue only if their complete possible page set is already VALID resident."
  applicability: "Background verification is rate-limited below Q69 budget. Optional parity or replication consumes Q53 capacity and never changes page identity."
evidence:
  - status: SPECIFIED
    result: "E-002 supplies source reacquisition; E-005 supplies removable failure states; Q57 supplies page/root identity."
build_instruction: "Verify on acquisition, before first residency, periodically by scrub policy, and after abnormal disconnect; quarantine corrupt segments and repair to new immutable extents."
acceptance_check: "Corrupt payload, index, manifest, root, and parity independently; detection must precede use, repair must restore the original digest, and unrecoverable state must block affected runs with exact page IDs."
depends_on: [Q20, Q49, Q54, Q57, Q60]
reopen_only_if: "The chosen digest or aggregate construction is broken or insufficient for partial repair."
```

## Q63 — Runtime state placement

```yaml
question_id: Q63
state: CLOSED
decision: "D retains the complete revision; unified memory contains the smallest frontier permitted by the selected native path or Q19 certificate, plus request state at each time, with explicit prefill and decode schedules."
formal_contract:
  symbols: "At activation: UM={runtime,plan and Q19 certificate metadata,admitted resident descriptions,empty reusable C}. At request assembly: select the certified condition/atom and load its description plus modality processors. Prefill layer l: UM={description_l,planned exact or sampled residual pages_l,K_partial,activations_l}; retire recomputable activations after layer. Decode t: UM={selected descriptions,planned correction pages,C,K_t,current activations,logits}; D={complete revision and all other pages,immutable context spill if plan permits}. Constraint is Q47; transfer schedule starts page l+1 only if it cannot evict pinned l/K. Protocol buffers are bounded host memory and never carry model pages."
  applicability: "Native resident mode may keep its complete active graph in C. Native streamed mode is compatible only if Q68 passes. Compiled mode follows its certified description, fresh-read, risk, and horizon budgets; it need not pin one prompt-selected set for the run."
evidence:
  - status: INFERRED
    result: "E-001 supplies exact K3 component bytes; E-004/E-006 supply load and compute paths; E-009 supplies bounds."
build_instruction: "Generate a time-indexed allocation/transfer plan from the Q19 certificate, tensor graph, page map, context limit, and profile; reserve maxima before admission and expose actual residency and fresh traffic by certificate category."
acceptance_check: "Trace prefill/decode for every Q39 architecture, compare each instant to the generated schedule and Q47, and fail on hidden model allocation, undeclared spill, or use-before-verify."
depends_on: [Q2, Q11, Q19, Q20, Q45, Q47, Q57, Q59]
reopen_only_if: "A new stateful operator requires a residency category or rollback rule absent from the schedule."
```

## Q64 — Condition selection and compiled-certificate failure

```yaml
question_id: Q64
state: CLOSED
decision: "Native prefetch prediction is an optimization under source routing. Compiled condition selection is semantic and may execute only inside the observation, protected-set, atom-cover, error-risk, and horizon contract of its immutable Q19 certificate; an out-of-contract observation is rejected before model divergence."
formal_contract:
  symbols: "Native prefetch emits {page_candidates,confidence,bytes}; low confidence expands conservatively or rejects. Compiled selection emits {observed_condition,atom_id,service_face,certificate_digest,description_digest,execution_seed_or_exact_schedule,bytes}. Require observed_condition in the certified protected support, atom_id covers it, the certified horizon is not exceeded, and every planned page is VALID_RESIDENT before its consumer. Any violation invokes Q20 before the affected operator. Updates after a terminal run create statistics for a future child certificate and cannot alter the current revision."
  applicability: "For source-native MoE, native router output defines the semantic path. For compiled revisions, the immutable observation contract and atom cover define admissible selection; a trained selector is one revision-owned implementation, not a universal router premise."
evidence:
  - status: INFERRED
    result: "Q19/Q20 separate stable prefetch from semantic routing; E-004 supplies synchronization."
build_instruction: "Validate observation support, service-face membership, certificate identity, horizon, and page requirements before command encoding; preserve the last committed token and recurrent checkpoint; log native-prefetch confidence or compiled selection, planned correction, and later child-calibration evidence separately."
acceptance_check: "Force false-high and false-low native prefetch confidence, forged atom membership, stale certificates, exhausted horizons, revealed fixed coins outside their adversary model, and adversarial domain shifts. Native outputs must equal an exact no-prefetch replay; compiled runs must reproduce under their certificate or terminate before divergence; future statistics cannot contaminate another revision."
depends_on: [Q19, Q20, Q62, Q63]
reopen_only_if: "An operator can consume an unknown parameter before exposing its identity, or a selector requires an observation relation absent from MATHS.md."
```

## Q65 — Concurrent agent requests and model switching

```yaml
question_id: Q65
state: CLOSED
decision: "The first release accepts concurrent clients but serializes model execution and cartridge mutation per active revision; concurrency exists in request queues and lawful I/O overlap, not simultaneous model graphs."
formal_contract:
  symbols: "Each client owns independent context and event sequence. Scheduler is deficit round-robin with age promotion; one run holds EXEC lease, one writer holds exclusive WRITE lease, and model activation holds SWITCH lease only when EXEC/WRITE are quiescent. Prefetch for the next run may use unreserved C but may not evict current pinned pages. Cache keys include revision,plan,precision,semantic state. Cancellation releases leases after last fenced command."
  applicability: "Multiple cartridges and models may be registered; one model revision is GPU-active per broker instance. A future parallel tier requires isolation and Q68 proof and is not implied."
evidence:
  - status: CHOSEN
    result: "Serialization minimizes page churn, cache interference, duplicated state, and original code while serving all named clients."
build_instruction: "Implement one scheduler and lease table, bound each queue, reject overload before allocation, and suspend training before inference only at committed step boundaries."
acceptance_check: "Submit competing clients, cancellations, switches, and training writes; verify fairness, isolated contexts/events, no stale cache use, no writer-reader race, and bounded page churn."
depends_on: [Q20, Q29, Q31, Q47, Q49, Q63]
reopen_only_if: "A Q80 service row cannot pass without parallel execution and a parallel design proves isolation."
```

## Q66 — Long-context, multimodal, reasoning, and tool semantics

```yaml
question_id: Q66
state: CLOSED
decision: "Each capability adds explicit graph, state, memory, and protocol obligations; Cassette may reduce a budget only through a separately qualified plan, never by silently truncating context, dropping vision, hiding reasoning, or changing tools."
formal_contract:
  symbols: "Long context adds K(tokens) and context-policy validation; multimodal adds processor_digest,encoder_pages,input limits; reasoning adds preserved reasoning events/history policy; structured output adds exact constrained-decoder/schema state; tools add ordered call/result events and resumed conversation state; recurrent models add checkpoint/restore state. Admission requires capability_state+W+C+A+R<=M and Q17/Q68 per capability stratum."
  applicability: "Capabilities absent from the source semantic manifest are UNSUPPORTED. Provider-managed hidden features prevent parity under Q67."
evidence:
  - status: OBSERVED
    result: "E-001 requires K3 vision and reasoning-history preservation; E-008 defines named protocol forms."
build_instruction: "Generate capability-specific execution schedules and adapter maps, include state growth in Q47, and preserve exact conversation history required by the model."
acceptance_check: "Run each Q16 capability at ordinary and boundary sizes; fail on truncation, field loss, wrong tool ordering, invalid schema, recurrent rollback drift, or hidden memory overrun."
depends_on: [Q10, Q16, Q31, Q47, Q63]
reopen_only_if: "A supported capability introduces new persistent or protocol state."
```

## Q67 — Baseline equivalence manifest

```yaml
question_id: Q67
state: CLOSED
decision: "Every comparison joins the cartridge revision to one exact baseline and labels each feature EXACT, BEST_EFFORT, PROVIDER_MANAGED, UNKNOWN, or UNSUPPORTED; any material UNKNOWN or PROVIDER_MANAGED feature blocks a parity claim."
formal_contract:
  symbols: "Equivalence={I_cassette,B_teacher,B_hosted?,B_native,weights_relation,tokenizer,template,sampler,seed_policy,reasoning_effort,reasoning_history,context_policy,modalities,tools,tool_harness,structured_output,max_output,concurrency,provider_features,field_statuses}; parity_equivalent=true iff all material statuses against B_teacher or B_hosted are EXACT and input/output state boundaries match; value and position gates (Q68) join Qc to B_native and B_teacher under one harness."
  applicability: "BEST_EFFORT may support ordinary use but cannot enter Qc/Qb parity. An official self-hosted full revision may serve as baseline when hosted internals are unavailable, but it must be named as such."
evidence:
  - status: SPECIFIED
    result: "E-008 exposes client/provider differences; Q13 defines baseline identity."
build_instruction: "Generate the manifest before evaluation, fetch no hidden defaults by inference, and bind it to every trace and published result."
acceptance_check: "Remove or hide one material provider feature and require parity status false; restore exact fields and require deterministic manifest identity."
depends_on: [Q10, Q13, Q31, Q66]
reopen_only_if: "A provider reveals or changes a previously hidden material feature."
```

## Q68 — Tiered service gates: floors, FRONTIER_CLASS, PARITY

```yaml
question_id: Q68
state: CLOSED
revised: 2026-08-05 under the amended remit
decision: "Service qualification is tiered. FRONTIER_CLASS is the release gate for Q19-certified compiled frontier rows: absolute usability floors, a value gate against B_native, a position gate against B_teacher, and the Q18 capacity proof. PARITY (NEAR_LABORATORY) is an additional label claimed only when the original ratio bounds actually pass. The full measured gap to the teacher and hosted references is always published. Incompatible tuples are rejected rather than relabeled, and thresholds may not be weakened to admit a failed tuple."
formal_contract:
  symbols: "Floors (all service rows): warm p95(first_committed_token)<=5s; cold p95<=15s; warm p95(Ld)<=100ms; sustained Rd>=10 tok/s; operation_error_rate<=0.005; qualified-session availability>=0.995; all Q48 post-warmup windows pass. Value gate (frontier rows, vs B_native): lower95CI(Qc/Q_native)>=1.05 overall, >=1.15 on long-tail and capacity strata, and no critical stratum lower95CI<1.00. Position gate (frontier rows): lower95CI[(Qc-Q_native)/(Q_teacher-Q_native)]>=0.50 per critical stratum where Q_teacher>Q_native. Honesty (all rows): the complete vector {Qc/Q_teacher, first-token, Ld, Rd, Ttask ratios against B_teacher and B_hosted when equivalent} is computed and published; suppressing a measured unfavorable component is a failed row. PARITY label: warm p95(first)<=1.25*baseline_p95; cold p95 within max(2.0*baseline_p95,baseline_p95+5s); warm p95(Ld)<=1.25*baseline; sustained Rd>=0.80*baseline_Rd; warm p95(Ttask)<=1.25*baseline; Q17/Q18 PARITY-tier thresholds pass."
  applicability: "FRONTIER_CLASS applies to Q19-certified compiled frontier rows. Mild-transform rows (Q40 modes 1-3, e.g. the Scout and Qwen rows) gate on floors plus the Q17 PARITY tier against their own B_teacher. TEACHER_CORRECTNESS rows gate on correctness and honest reporting only. Every ratio requires Q67 equivalence for the baseline it uses."
evidence:
  - status: CHOSEN
    result: "The tiered structure encodes the amended remit: the release contest is against what the same consumer machine can do unaided, the laboratory gap is measured and published rather than gated, and parity language is reserved for tuples that actually earn it."
build_instruction: "Evaluate every Q39/Q80 tuple without threshold tuning after results; report all vector components; classify failed tuples through Q38; bind every emitted label to its gate evidence IDs."
acceptance_check: "Recompute gates from raw traces and confidence intervals; one failed floor, value, or position bound must prevent FRONTIER_CLASS even when averages pass; emitting PARITY without every original ratio bound passing must be structurally impossible."
depends_on: [Q12, Q13, Q17, Q18, Q48, Q67]
reopen_only_if: "Measured user-experience evidence establishes stricter floors, the baseline contract changes, or a superior native alternative is published before matrix freeze; no reopening may weaken a bound to admit a failed tuple."
```

## Q69 — Tail latency and temporal variability

```yaml
question_id: Q69
state: CLOSED
decision: "Cassette controls tails and temporal decay explicitly; peak or mean throughput cannot pass a plan."
formal_contract:
  symbols: "Per stratum/cache/thermal phase require p99(Ld)<=2*p50(Ld), p95(Ld)<=1.5*p50(Ld), coefficient_of_variation(Ld)<=0.25 after warmup, max_stall<=max(10*p50(Ld),2s), p05 five-minute Rd>=0.90*first_stable_window_Rd, and all p95/p99 first-token/task bounds in Q68. Report bootstrap 95% intervals and autocorrelation by five-minute window."
  applicability: "Intentional tool wait, client backpressure, and queue time are separately labeled but remain in total task time; they cannot be removed from agent-visible metrics."
evidence:
  - status: INFERRED
    result: "E-005/E-009 show random-read and thermal variation enter token latency; Q12 provides trace boundaries."
build_instruction: "Preserve per-token distributions and session order, identify page miss, queue, compute, storage, thermal, and protocol causes, and schedule only within the passing curve."
acceptance_check: "Inject periodic storage delay and thermal decay that leave the mean unchanged; both must fail the tail/temporal gates."
depends_on: [Q12, Q20, Q42, Q48, Q64, Q68]
reopen_only_if: "A declared workload has a legitimate deterministic pause requiring a separate named stratum."
```

## Q70 — Mandatory training matrix

```yaml
question_id: Q70
state: CLOSED
decision: "The first release must complete Tier-A training on every compiled Q39 model row that declares training and Tier-B recovery on every Q19-certified row; full-weight frontier training is optional and may be incompatible by Q21."
formal_contract:
  symbols: "Tier-A qualification per row: LoRA/adapter SFT >=131072 train tokens, offline DPO >=1024 preference pairs, adapter continued pretraining >=1048576 tokens. Tier-B compiled rows: condition/atom/description/estimator/observation recovery and calibration >=32768 prompt-continuation traces plus precision recovery over every emitted precision tier. Mandatory rows include C1/S1/FRONTIER-COMPILED-CERTIFIED (K3 exemplar), C3/S3/K3-COMPILED-CERTIFIED, one dense F4 Tier-A/Tier-B fixture pair, and one sparse F5 Tier-A/Tier-B fixture pair. Each operation must fit Q53/Q74, finish within 1.25*its predeclared measured compute+I/O estimate, improve its operation-specific held-out score, regress Q16 general score by <=1 percentage point, and regenerate every invalidated Q19 witness."
  applicability: "The corpus, tokenizer, steps, optimizer, seeds, adapter rank, checkpoint cadence, and expected storage/time are frozen per test. Tier-C is advertised only if separately live-qualified."
evidence:
  - status: INFERRED
    result: "E-007 supports bounded adapter and recovery state while excluding K3 full Adam on 2 TB media."
build_instruction: "Encode training rows as Q80 data, perform all persistent writes on D, commit callable children, and rerun invalidated inference/quality/protocol evidence."
acceptance_check: "Complete, interrupt/resume, cancel/rollback, remount, and call each resulting child; fail on missed operation, hidden state, estimate overrun, non-improvement, general regression, or invalid revision identity."
depends_on: [Q21, Q24, Q28, Q39, Q53, Q61, Q68]
reopen_only_if: "A mandatory operation is mathematically inapplicable to a model class, in which case the class must declare and prove an equivalent post-training operation rather than silently omit training."
```

## Q71 — Drive-resident training dataflow

```yaml
question_id: Q71
state: CLOSED
decision: "Training streams one deterministic parameter/state window at a time from D, keeps only the live forward/backward frontier in unified memory, and returns every persistent result to a candidate branch on D."
formal_contract:
  symbols: "For accumulation window b: (1) read batch/token state D->UM; (2) for layers 1..L load validated parameter pages, forward, retain bounded activation checkpoint in UM or D, retire page unless backward-pinned; (3) for layers L..1 reload page and activation checkpoint, compute gradient slice, reduce in fixed order, write gradient slice D; (4) after all microbatches freeze-complete, join page gradient+optimizer+master from D, update once, write candidate page/state+journal to D, retire UM; (5) commit Q73. At all t, live_batch+live_pages+activations+gradient_slice+state_slice<=M."
  applicability: "Activation checkpointing to D is allowed training state; internal storage is forbidden. I/O overlap may prefetch only a page whose reservation cannot evict the current dependency frontier."
evidence:
  - status: INFERRED
    result: "E-007 supplies persistent state; E-004/E-005 supply asynchronous read and durable write boundaries."
build_instruction: "Generate the schedule from graph dependencies, microbatch, optimizer, and Q47; trace every tensor production, location, consumer, retirement, and durable commit."
acceptance_check: "Replay the trace into a byte-accurate simulator and live fixture, then assert no tensor exists outside its declared interval/location, no page is updated before full accumulation, and peak bounds match within allocator reserve."
depends_on: [Q23, Q25, Q47, Q60, Q70]
reopen_only_if: "A supported training algorithm has a dependency that cannot be represented by a bounded layer/page frontier."
```

## Q72 — Paged optimizer execution without hidden full masters

```yaml
question_id: Q72
state: CLOSED
decision: "Paged optimization is equivalent to an unpaged update only when all gradients refer to one frozen parameter revision and each parameter page is updated exactly once in a deterministic global step."
formal_contract:
  symbols: "Freeze theta_k for microbatches 1..B; g_k=sum_b g(theta_k,x_b) in fixed reduction order and precision. For pages j in canonical tensor/page order, load {theta_kj,g_kj,m_kj,v_kj,master_kj?,residual_kj?}, compute the same optimizer equations with global step k and hyperparameters, write child state, then discard. UM_peak<=one_parameter_window+one_gradient_window+one_optimizer_window+activations_frontier. Transfer volume is sum_j(bytes(theta_j)+bytes(g_j)+bytes(state_j)+bytes(child_j))."
  applicability: "Gradient accumulation, RNG counters, loss scale, clipping norm, and scheduler state are global. Global norm is computed in a complete read-only reduction pass before any page update."
evidence:
  - status: INFERRED
    result: "E-007 establishes exact Adam restart and page-local state joins."
build_instruction: "Persist gradients or sufficient deterministic recomputation on D, compute global reductions before mutation, update canonical order, and prohibit framework-created full masters."
acceptance_check: "For identical initial state and batches, compare every child weight, moment, step, RNG, and loss against an unpaged reference; require bitwise equality where kernels match or the Q17 numerical bound where reduction kernels differ."
depends_on: [Q24, Q25, Q71]
reopen_only_if: "An optimizer couples parameters through state beyond a bounded global reduction."
```

## Q73 — Atomic model-version commits

```yaml
question_id: Q73
state: CLOSED
decision: "Training commits immutable child pages or deltas behind a candidate root and changes callability with one durable generation pointer; readers never observe a mixed revision."
formal_contract:
  symbols: "child_id=H(parent_id,training_manifest,ordered_page_or_delta_digests,semantic_manifest); dependency order={payloads -> indexes -> child root -> verification -> generation pointer}. Reader pins {generation,child_id,root_digest}. Rollback selects prior valid generation. GC may reclaim an object iff reachability from all retained roots and active reader pins is zero and rollback retention has expired."
  applicability: "Adapters, replacement pages, compiled-certificate/precision recovery, and consolidated revisions. Callable roots are immutable."
evidence:
  - status: SPECIFIED
    result: "E-005 provides durable ordering; Q22/Q25 define version and transaction semantics."
build_instruction: "Read back and hash every dependency, full-sync root and pointer in order, retain at least the previous valid generation, and isolate readers by pinned root."
acceptance_check: "Crash at every dependency and pointer boundary while readers run; every reader must see all-parent or all-child bytes, remount must choose one valid generation, and GC must preserve pinned/rollback roots."
depends_on: [Q22, Q25, Q44, Q62, Q72]
reopen_only_if: "The filesystem cannot sustain atomic generation replacement under the tested failure model."
```

## Q74 — Training endurance and resource admission

```yaml
question_id: Q74
state: CLOSED
decision: "A training job starts only after reserving capacity, memory, sustained bandwidth, write endurance, thermal duty cycle, power state, and completion time from measured class data."
formal_contract:
  symbols: "JobEstimate={S_required,M_peak,read_bytes,logical_write_bytes,physical_write_p95,duration_p95,checkpoint_interval,power_required,thermal_duty}; admit iff Q47,Q53,Q28,Q42,Q48 all pass, external power is present for jobs >30min, free_after_job>=S_safety, projected lifetime<=0.80 endurance, and duration_p95<=declared job limit. Runtime throttles at 90% of thermal/write envelope and cancels safely at 100% before integrity risk."
  applicability: "Unknown endurance rejects mutable training for that class. User cancellation is always allowed at a Q25 boundary; resource exhaustion is not allowed to discover itself through partial writes."
evidence:
  - status: INFERRED
    result: "Q28/Q42/Q48/Q53 supply measured inputs and hard floors."
build_instruction: "Emit estimate and reservation before acceptance, meter actual values per checkpoint, revise remaining estimate, and pause or rollback if any hard bound would be crossed."
acceptance_check: "Inject low space, false endurance, power loss, thermal throttling, slow writes, and estimate drift; reject before start or stop at a recoverable boundary without crossing the reserved limit."
depends_on: [Q28, Q42, Q47, Q48, Q53, Q70]
reopen_only_if: "A supported storage class lacks a measurable resource needed by the predicate."
```

## Q75 — Incremental recompilation after tuning

```yaml
question_id: Q75
state: CLOSED
decision: "Post-training recompilation computes the transitive hash closure from changed trainable objects and mathematical-certificate inputs, and reuses every artifact whose complete input digest vector is unchanged."
formal_contract:
  symbols: "Changed={delta pages,replacement pages,condition metrics,atoms,selector,description,residual estimator,observation contract,precision residuals,tokenizer,operators,context}. affected=transitive_closure_Q27(Changed). Recompute in topological order {protected traces and activation stats -> condition metrics -> compatibility witnesses and atom cover -> descriptions/residuals/estimator calibration -> page maps -> precision calibration -> composition/horizon proof -> hardware plans -> quality/certificate evidence -> compatibility/protocol manifest}. Full certificate closure is required by Q61 or any semantic schema change."
  applicability: "Adapter-only revisions may add an overlay plan and rerun quality without repacking base pages; merged or base-updated revisions follow affected tensor spans."
evidence:
  - status: INFERRED
    result: "Q27 supplies dependencies; Q57/Q59 separate shared pages from plans."
build_instruction: "Hash every generator's complete inputs, including every MATHS.md certificate field, cache outputs by that hash, recompute affected closure on D, and publish through Q60/Q73 while retaining the prior revision."
acceptance_check: "For each change class, compare incremental output with clean full compilation: logical root, plans, and evidence inputs must match wherever deterministic, with no stale artifact reuse."
depends_on: [Q27, Q61, Q70, Q73]
reopen_only_if: "Incremental and clean compilation diverge beyond an explicitly stochastic recorded transform."
```

## Q76 — Named-agent conformance adapters

```yaml
question_id: Q76
state: CLOSED
decision: "Each named adapter translates only its documented surface and reports all other canonical capabilities as unsupported or Cassette extensions; no adapter fabricates reasoning, tools, cancellation, or training semantics."
formal_contract:
  symbols: "Codex provider maps OpenAI Responses request/SSE items and, when app-server integration is used, its exact generated initialize/thread/turn/item/interrupt schema. Ollama maps /api/tags,/api/show,/api/generate,/api/chat and NDJSON chunks; disconnect cancellation is exact only where documented, while canonical operation cancellation is a Cassette extension. OpenClaw maps /v1/responses,/v1/chat/completions and versioned Gateway agent/session events; model may denote an OpenClaw agent and must resolve explicitly. Hermes maps /v1/models,/v1/chat/completions,/v1/responses and agent events; raw Hermes weights do not imply this server contract. Custom endpoint is the canonical Q31 schema. Training/status use Q6 unless an external protocol has exact native fields."
  applicability: "Adapter versions are pinned to governing schemas; field status is EXACT, BEST_EFFORT, PROVIDER_MANAGED, or UNSUPPORTED."
evidence:
  - status: SPECIFIED
    result: "E-008 records the governing protocol authorities and their irreducible differences."
build_instruction: "Generate structural mappings, handwrite only stateful deviations, preserve event order and IDs, and keep model lifecycle operations in the canonical broker."
acceptance_check: "Run bidirectional golden traces for discovery, text, reasoning, tools, structured output, streaming, cancellation, errors, status, and training where supported; compare fields and state transitions to each pinned schema."
depends_on: [Q6, Q10, Q31, Q65, Q66]
reopen_only_if: "A named protocol version changes a material field or state transition."
```

## Q77 — Capability and harness negotiation

```yaml
question_id: Q77
state: CLOSED
decision: "Agents discover the exact callable revision and effective harness before sending a run; negotiation is immutable for the run and rejects unsupported requested features before model admission."
formal_contract:
  symbols: "NegotiatedCapability={cassette_protocol,adapter_version,model_revision,source_parent,execution_mode,plan_id,performance_tier,training_tier,modalities,input_limits,context_limit,reasoning_fields,reasoning_history_policy,tool_schema,structured_output,sampling,streaming,cancellation,conversation_state_contract}; negotiate(requested,available)->exact subset or CAPABILITY_MISMATCH."
  applicability: "Performance tier names bind Q68 evidence. A client alias resolves to one immutable model revision at negotiation and cannot drift during a run."
evidence:
  - status: SPECIFIED
    result: "E-008 supplies client capability surfaces; Q10/Q67 supply semantic and baseline fields."
build_instruction: "Expose machine-readable profiles through Q31 and adapters, include field provenance/status, pin the result to the run, and require renegotiation after model or plan switch."
acceptance_check: "Request every supported and unsupported capability combination, switch aliases concurrently, and prove exact pre-admission acceptance/rejection plus stable run identity."
depends_on: [Q10, Q31, Q67, Q76]
reopen_only_if: "A client needs dynamic mid-run capability negotiation not representable as an event."
```

## Q78 — Proof of minimum executable code

```yaml
question_id: Q78
state: CLOSED
decision: "The irreducible original architecture has six executable responsibilities—broker/state machine, identity/content/transaction store, source adapters, compiler/plan generator, pager/scheduler, and training coordinator—over reused numerical runtimes; all schemas, model plans, compatibility tables, and adapter field maps are generated or data."
formal_contract:
  symbols: "Required removal map: broker -> fails Q5/Q6/Q31/Q76; identity-store -> fails Q1/Q25/Q57/Q73; source-adapter boundary -> fails Q9/Q51/Q52; compiler/planner -> fails Q4/Q40/Q58/Q59; pager/scheduler -> fails Q20/Q47/Q63/Q65; trainer -> fails Q21/Q71/Q72/Q73. Q29 computes exact authored LOC, processes, runtimes, dependencies, branches, duplicate authorities, and binary bytes from the completed tree; current research supplies no false numeric code count."
  applicability: "Responsibilities may share one process and language module. A reused library replaces a responsibility only if it preserves all mapped invariants."
evidence:
  - status: INFERRED
    result: "E-006 supplies numerical ownership; Q29/Q32/Q33 remove duplicate lifecycle and model-specific code."
build_instruction: "Build one broker process where practical, link pinned runtimes, generate data surfaces, then run the automated Q29 ledger and deletion proof before Q80 completion."
acceptance_check: "The completed repository must emit exact counts and dependencies; remove each remaining component in isolation and require its mapped acceptance rows to fail, while any component with no unique failing row is deleted."
depends_on: [Q29, Q30, Q31, Q32, Q33, Q76]
reopen_only_if: "Implementation reveals another irreducible responsibility or one listed responsibility can be removed without a failed acceptance row."
```

## Q79 — Provenance, privacy, and local-execution proof

```yaml
question_id: Q79
state: CLOSED
decision: "Cassette proves narrow auditable facts: exact source and page identity, contained executable inputs, secret-free cartridge metadata, zero Cassette-owned internal model files, loopback-only model service during offline runs, and no remote inference process. It does not claim OS-wide absence of model-derived swap bytes."
formal_contract:
  symbols: "Evidence={Q1 source tuple,transfer log,page/Merkle verification,build/runtime commit and signature,custom_code verdict,credential-reference audit,file-open/write trace,internal-volume model-byte scan,process/network socket trace,packet capture or enforced egress deny,loopback client trace,prompt/output persistence trace,offline Q80 outputs}. Fail if any authoritative digest mismatch, secret serialization, non-loopback model request, undeclared prompt/training persistence, internal full checkpoint, or remote result enters a run."
  applicability: "Network may be enabled for explicit acquisition and source repair only. Inference and training proof runs disable external network before activation; local tool workloads use a separately declared tool boundary and cannot provide model inference."
evidence:
  - status: SPECIFIED
    result: "E-002/E-005/E-008 establish identity, storage, and local protocol boundaries; Q2 states the exact OS limitation."
build_instruction: "Generate an append-only audit bundle from source resolution through offline run, keep credentials in OS-held opaque references, redact private payloads while retaining digests, and bind evidence to code/model/profile IDs."
acceptance_check: "Run Q80 with external network physically or policy-disabled, attempt DNS/HTTP exfiltration and internal writes, inspect all process sockets/files, and fail every claim on an undeclared path; repeat after remount."
depends_on: [Q1, Q2, Q5, Q51, Q55, Q62, Q67, Q76]
reopen_only_if: "A runtime or OS path prevents auditable local-only enforcement."
```

## Q80 — Non-negotiable complete-system acceptance matrix

```yaml
question_id: Q80
state: CLOSED
decision: "Cassette is complete only when every REQUIRED row in research/ACCEPTANCE_MATRIX.yaml (v3) is LIVE-PROVEN under its declared role and gate tier — Q68 FRONTIER_CLASS for thesis rows, floors plus the Q17 PARITY tier for mild-transform rows, correctness for TEACHER_CORRECTNESS rows, with the F4/F5 gates passed before any frontier compiled row ran — against its exact immutable model, Apple class, measured cartridge class, source, workload, training, protocol, failure, privacy, and code identity; no partial substitute changes the result."
formal_contract:
  symbols: "complete = all(row.status==PASS for row in matrix where row.required) and all(evidence(row)==LIVE_PROVEN) and Q78_exact_accounting_pass and Q79_offline_pass. Any NOT_RUN, BLOCKED, SKIPPED, SUBSTITUTED, SIMULATED, REMOTE, or FAIL required row implies complete=false. Thresholds are Q17/Q18/Q19/Q48/Q68/Q69/Q70."
  applicability: "The matrix binds exact Q39 rows, all five named agent surfaces, source adapters, Tier-A/Tier-B training, long context/vision/reasoning/tools, disconnect/corruption/power/capacity failures, recovery, offline execution, provenance, and minimum-code proof."
evidence:
  - status: CHOSEN
    result: "The matrix file encodes the full release boundary derived by Q1-Q79; all rows begin NOT_RUN because this research operation did not implement Cassette."
build_instruction: "Make the matrix the release executable's sole completion authority, attach raw traces and immutable evidence IDs to each row, and prevent any UI, paper, diagnostic fixture, or manual override from setting PASS."
acceptance_check: "From a clean source checkout and blank qualified cartridges, execute the complete matrix; delete or fail any single required row and require complete=false; restore all live passes and require one reproducible completion digest."
depends_on: [Q1, Q5, Q10, Q12, Q17, Q18, Q19, Q21, Q25, Q29, Q39, Q48, Q51, Q58, Q62, Q68, Q69, Q70, Q73, Q76, Q78, Q79]
reopen_only_if: "The binding product result changes, a required public reference disappears, or live evidence exposes an omitted complete-system dimension."
```
