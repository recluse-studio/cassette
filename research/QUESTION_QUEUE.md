---
artifact_id: cassette-build-directed-question-queue
version: 2
amended: 2026-08-05
amendment_authority: ORIGINAL_REMIT.md (amended 2026-08-05)
scope_mode: GENERAL_PRODUCT
question_count: 80
producer: research-agent
consumer: implementation-agent
communication_mode: agent-to-agent
answer_language: formal-mathematical-computational
completion_target: fully-working-cassette
human_interface_deliverables: excluded
named_instance_inspection: forbidden-unless-explicitly-added
---

# Cassette Build-Directed Question Queue

This queue governs research for a complete open-source Cassette system. Each answer must become a
mathematical, computational, storage, training, reliability, or machine-protocol decision that a
high-capability implementation agent can consume without repeating the research.

## Binding result

Cassette accepts an agent-issued source descriptor for a selected downloadable model from sources
such as Hugging Face, Ollama, or Tinker; writes the authoritative model directly to external USB-C
flash or SSD storage; prepares and executes the model through macOS and Apple Silicon without
relocating the full authoritative model to internal storage; permits compatible fine-tuning and
post-training against the model where it resides; and exposes the resulting capability to Codex,
Ollama, OpenClaw, Hermes, and custom agents through machine-readable protocols.

The completed system must deliver frontier-class capability on consumer Apple hardware: for every
tuple Cassette declares compatible it must satisfy absolute usability floors, decisively exceed the
strongest model the same machine can run unaided, close more than half the measured capability gap
between that unaided alternative and the selected model's own full-capacity reference, and measure
and publish the remaining gap to the laboratory service rather than gate on it (amended remit,
2026-08-05; RESEARCH.md v2, Q13/Q68). Cassette must contain the minimum original executable code
consistent with correctness, reliability, and portability.

The external cartridge is the authoritative parameter and training store. Apple hardware supplies
computation, memory, and I/O coordination against that store; the research must never reframe the
system as a conventional Mac-resident model deployment.

## Scope controls

- Treat Apple Silicon Macs, macOS storage and compute paths, USB-C flash and SSD devices, model
  architectures, source services, and agent protocols as general product classes.
- Use public, reproducible, controlled reference configurations when measurements are required.
- Do not inspect or infer facts from the current Mac, attached volumes, installed runtimes, local
  model caches, signed-in accounts, current directory, or personal client settings.
- Treat Kimi K3-class models as frontier-scale acceptance references, not as Cassette's sole model
  architecture or product definition.
- Exclude human-facing UI, onboarding, explanation, and subjective usability from the research
  deliverables. A separate control surface may consume Cassette later; this queue defines the
  machine system beneath it.
- Reject remote inference as a substitute for drive-resident execution.
- Reject a paper, survey, simulator, benchmark harness, prototype, or small-model proof as the final
  result. Such artifacts may answer bounded questions only when their result enters the complete
  implementation contract.

## Required answer packet

The research agent must close each question with this packet:

```yaml
question_id: Qn
state: CLOSED | SUPERSEDED
decision: exact declarative answer
formal_contract:
  symbols: equations, tensor shapes, state transitions, protocol fields, units, or invariants
  applicability: supported product classes and version boundaries
evidence:
  - status: SPECIFIED | OBSERVED | MEASURED | INFERRED | CHOSEN
    result: decisive evidence
build_instruction: exact component behavior required from the implementation agent
acceptance_check: setup, operation, expected result, and failure condition
depends_on: [Qn]
reopen_only_if: exact changed condition or failed acceptance check
```

Answers must address agents. Do not produce explanatory copy for a person, user-interface language,
recommendation menus, or invitations to choose among ordinary reversible engineering decisions.
A blocked investigation remains active and produces no completion packet. A closed packet must give
the implementation agent enough formal structure, build instruction, and executable proof to act
without translating an agent answer into a human decision.

## Shared symbols

| Symbol | Meaning |
|---|---|
| \(P\) | Complete parameter set represented by the selected model revision. |
| \(D\) | Authoritative parameter and training state stored on the external cartridge. |
| \(W(r,t)\) | Parameter working set resident in unified memory for request \(r\) at generation step \(t\). |
| \(C(t)\) | Reusable parameter-page cache at step \(t\). |
| \(K(r,t)\) | KV and recurrent context state for request \(r\) at step \(t\). |
| \(M\) | Unified-memory budget available to Cassette after operating-system and agent reserves. |
| \(S_{peak}\) | Maximum cartridge capacity consumed during download, preparation, inference, or training. |
| \(B_s\) | Sustained external-storage bandwidth under the declared access pattern. |
| \(B_m\) | Sustained Apple unified-memory bandwidth available to model execution. |
| \(L_a\) | Request admission and cartridge assembly latency. |
| \(L_p\) | Prompt-prefill latency. |
| \(L_d\) | Decode latency per generated token. |
| \(R_d\) | Sustained decode rate in tokens per second. |
| \(Q_b\) | Quality score of the matched laboratory baseline. |
| \(Q_c\) | Quality score of Cassette under an equivalent agent workload. |
| \(T\) | Deterministic or trained transformation from source model representation to cartridge representation. |

## Research directions

### D1 — Model identity and residency

Define what constitutes the full model, which representation is authoritative, which transient
copies are permitted, and which invariants prove that the cartridge retains the model's complete
capacity.

### D2 — Mathematical capability preservation

Formalize numerical equivalence, acceptable approximation, routing fidelity, long-tail capacity,
quality variance, and the tests that distinguish preserved model behavior from a smaller surrogate.

### D3 — Apple computation and memory architecture

Resolve the macOS and Apple Silicon data path, unified-memory budget, CPU, GPU, and Neural Engine
execution eligibility, copy boundaries, synchronization, and sustained thermal envelope across
supported hardware classes.

### D4 — External storage and USB transport

Resolve USB-C transport classes, bridge behavior, filesystem effects, block access, sustained
bandwidth, latency, power, thermal behavior, and removable-media lifecycle.

### D5 — Model acquisition and compatibility

Resolve source-service protocols, metadata preflight, resumable transfer, model-format parsing,
architecture qualification, custom code, and revision updates.

### D6 — Cartridge representation and compilation

Define the on-drive tensor or page format, bounded-space transformation, hardware plans, integrity
metadata, precision layers, and compilation recovery.

### D7 — Drive-resident inference runtime

Define prefill, decode, page loading, caching, eviction, compute scheduling, misses, context state,
concurrency, cancellation, and model switching.

### D8 — Working-set routing and adaptive precision

Define shared and conditional parameters, request-level selection, token-level correction, page
churn, memory adaptation, precision refinement, and post-training effects on those structures.

### D9 — Drive-resident training

Define supported training operations, gradients, optimizer state, master weights, update semantics,
write cost, recovery, and continued compatibility with inference and agent protocols.

### D10 — Durability, versioning, and recovery

Define atomic state transitions, checksums, rollback, power-loss recovery, disconnect behavior,
corruption repair, model revisions, and cartridge lifetime.

### D11 — Agent-to-agent protocols

Define model discovery, capability negotiation, request and streaming schemas, reasoning state, tool
calls, cancellation, errors, training operations, and compatibility with named agent systems.

### D12 — Minimum-code architecture

Assign semantic decisions to the model, execution fidelity to a thin harness, numerical work to
existing kernels where valid, and model-specific variation to data rather than duplicated code.

### D13 — Trust, provenance, and containment

Define artifact identity, source verification, custom-code containment, credential boundaries,
internal-storage exclusion, privacy, and proof that no remote model substitutes for the cartridge.

### D14 — Performance and quality evaluation

Define matched baselines, workload distributions, cold and warm timing, sustained and tail behavior,
quality metrics, variance, failure thresholds, and reproducible result records.

### D15 — Full-scale qualification

Define the binding model-class, Apple-compute-class, storage-class, training, failure, and protocol
matrix whose passage constitutes a complete Cassette release.

### D16 — Demonstrated novelty and open-source boundary

Identify Cassette's demonstrated technical contribution after the mechanism works, perform a
bounded collision check, and preserve reproducible open-source construction without allowing
novelty research to replace engineering.

## Question queue

### Q1 — Canonical full-model identity

Resolve whether \(P\) means original source weights, an official quantized release, a Cassette
transformation, or a formally equivalent family of representations. Emit a canonical identity
tuple covering source revision, tensors, configuration, tokenizer, templates, executable model
code, precision, and every invariant that \(T\) must preserve.

Directions: D1, D5, D6.

### Q2 — Permitted transient residency

Resolve which subsets of \(D\) may enter \(W(r,t)\), \(C(t)\), and other volatile buffers; their
maximum size, lifetime, sharing, eviction, and zeroization rules; and the condition proving that no
full authoritative checkpoint has migrated to internal storage. Emit a residency matrix and
machine-checkable byte, lifetime, and destination invariants for every buffer class.

Directions: D1, D3, D7.

### Q3 — Source preservation and compiled authority

Resolve whether Cassette preserves the source representation unchanged, replaces it with a compiled
representation, or retains an immutable provenance layer plus an authoritative executable layer.
Emit the identity, recovery, and version relation between those layers without requiring duplicate
full checkpoints.

Directions: D1, D6, D10.

### Q4 — Peak conversion storage bound

Derive \(S_{peak}\) during direct download and transformation as a function of source shards,
compiled pages, temporary extents, integrity metadata, rollback state, precision layers, and free
space. Emit a bounded-space algorithm that cannot require two complete copies of \(P\).

Directions: D4, D6, D10.

### Q5 — Machine transition from source descriptor to callable model

Define the idempotent state machine that accepts a model-source descriptor and cartridge descriptor,
downloads and verifies the artifact, determines compatibility, prepares the representation, and
publishes a callable model identity to agent clients. Emit states, transitions, errors, resumability,
and durable commit points.

Directions: D5, D6, D7, D11.

### Q6 — Machine control contract

Define the smallest agent-callable control contract for model selection, cartridge selection,
download, preparation, activation, inference, training, status, cancellation, recovery, and removal.
Emit request, response, error, idempotency, and capability-discovery schemas; exclude GUI and
human-interaction requirements.

Directions: D11, D12.

### Q7 — Architecture compatibility taxonomy

Determine which dense, sparse MoE, multimodal, conventional-attention, linear-attention, recurrent,
quantized, and custom-operator architectures Cassette can execute or transform while satisfying its
quality and performance contracts. Emit explicit capability predicates and unsupported conditions.

Directions: D5, D6, D7.

### Q8 — Pre-download suitability decision

Determine which remotely available metadata is sufficient to classify model compatibility, required
capacity, expected working-set behavior, training support, and missing custom operations before
transferring the full artifact. Emit a deterministic preflight record and the conditions that require
deferred inspection.

Directions: D5, D13.

### Q9 — Source-service input contracts

Define the authoritative model, revision, shard, metadata, tokenizer, license, and authentication
contracts for Hugging Face, Ollama, Tinker, and extensible future sources. Emit one normalized source
descriptor consumed by the acquisition engine.

Directions: D5, D11.

### Q10 — Preservation of model interaction semantics

Determine how Cassette preserves tokenization, chat rendering, control tokens, reasoning state,
sampling, structured output, multimodal preprocessing, tool calls, context management, and custom
model operations. Emit a semantic compatibility manifest bound to the model identity from Q1.

Directions: D5, D7, D11.

### Q11 — Cartridge portability across Apple and storage classes

Determine whether one cartridge representation can carry multiple execution plans for different
Apple memory budgets and external-storage envelopes without duplicating \(P\). Emit the portable
core, profile-specific metadata, runtime-selection function, and conditions requiring recompilation.

Directions: D3, D4, D6, D8.

### Q12 — Agent-observable service metrics

Define the metric vector for near-laboratory behavior, including \(L_a\), \(L_p\), \(L_d\), \(R_d\),
total agent-task time, interruption count, error rate, and \(Q_c/Q_b\). Emit units, measurement
boundaries, cold and warm states, and aggregation rules.

Directions: D2, D14.

### Q13 — Laboratory baseline contract

Define the exact hosted configuration against which Cassette is compared: model revision, precision,
sampler, reasoning effort, context policy, tool harness, concurrency, output limits, and service-side
features. Emit a baseline manifest that prevents comparison with a different effective system.

Directions: D2, D14.

### Q14 — Request latency decomposition

Determine which stages contribute to end-to-end agent response time and whether model preparation or
working-set assembly belongs to request latency. Emit
\(L_{total}=L_a+L_p+nL_d+L_{protocol}+L_{tool}\), with each term's start, stop, cache state, and
accounting rule.

Directions: D4, D7, D14.

### Q15 — Workload coverage requirement

Determine the workload distribution over which the near-laboratory contract must hold, including
ordinary, adversarial, long-tail, cold, warm, domain-shifting, and extended agent sessions. Emit
coverage weights, exclusion rules, percentile requirements, and the maximum permitted unsupported
fraction for a declared compatible model.

Directions: D2, D14, D15.

### Q16 — Capability-complete evaluation workloads

Define agent workloads covering long context, vision, reasoning, coding, tool use, structured output,
multi-turn state, cancellation, and recovery. Emit machine-executable inputs, expected invariants,
quality measures, and protocol traces rather than human preference judgments.

Directions: D2, D11, D14.

### Q17 — Quality and numerical variance

Determine acceptable variance across repeated Cassette and laboratory runs while separating sampler
variance from transformation error, numerical precision, routing differences, and harness effects.
Emit statistical tests, sample counts, confidence bounds, and hard regression thresholds.

Directions: D2, D14.

### Q18 — Preservation of long-tail parameter capacity

Determine whether transformed routing and bounded working sets preserve rare capabilities encoded in
\(P\), rather than reproducing only common tasks. Emit long-tail probes, attribution or ablation
tests, required quality ratios, and evidence that unavailable pages have not become permanently
unreachable.

Directions: D2, D8, D14.

### Q19 — Request-level working-set stability

Measure and formalize stability of \(W(r,t)\) across generation using page-union size, weighted
Jaccard overlap, bytes loaded, churn rate, route entropy, and quality impact. Emit the stability
condition under which prompt-persistent paging is admitted.

Directions: D2, D8.

### Q20 — Mid-generation working-set miss semantics

Define the state transition when generation requires parameters outside the prepared working set.
Emit detection, asynchronous acquisition, synchronization, timeout, fallback, output-integrity, and
cache-update rules that preserve the model result without uncontrolled stalls.

Directions: D7, D8, D10.

### Q21 — Supported training operation set

Determine which operations Cassette must support for compatible models: adapters, LoRA, supervised
fine-tuning, preference optimization, continued pretraining, router recovery, precision recovery, and
full-weight updates. Emit capability predicates and numerical requirements for each operation.

Directions: D9.

### Q22 — Base mutation and derivative-state model

Determine whether training mutates authoritative base pages, writes immutable deltas, creates a new
version graph, or uses a hybrid. Emit the algebra for composing base weights and ordered deltas, the
commit semantics, and the identity of each resulting model revision.

Directions: D1, D9, D10.

### Q23 — Placement of training state

Determine where datasets, gradients, optimizer moments, master parameters, temporary activations,
checkpoints, journals, and recovery records reside during training. Emit a storage and memory
placement function with peak capacities, lifetimes, and forbidden internal-storage states.

Directions: D4, D9, D10.

### Q24 — Training quantized parameters

Determine how quantized or progressively refinable cartridge weights accept updates without silently
requiring a complete high-precision checkpoint on internal storage. Emit the update mathematics,
master-state representation, error accumulation bounds, and quality-recovery procedure.

Directions: D2, D8, D9.

### Q25 — Training interruption and rollback

Define behavior under process failure, drive removal, power loss, insufficient capacity, corrupted
pages, invalid gradients, and cancelled jobs. Emit transaction boundaries, write ordering, journal
records, rollback invariants, and restart semantics.

Directions: D9, D10.

### Q26 — Post-training interoperability

Determine how tuned cartridge revisions remain addressable by Cassette's agent protocols and, where
the target runtime contract permits, exportable to standard model formats or runtimes. Emit revision,
adapter, merge, tokenizer, and capability metadata requirements.

Directions: D6, D9, D11.

### Q27 — Training invalidation graph

Determine which changes to weights, routing, precision, tokenizer, context behavior, or operators
invalidate page placement, prompt routing, caches, hardware plans, quality proofs, or compatibility
manifests. Emit an explicit dependency graph and minimal recomputation rules.

Directions: D6, D8, D9.

### Q28 — Training write cost and cartridge endurance

Derive bytes written, write amplification, random-write rate, checkpoint overhead, thermal load, and
expected storage lifetime for every supported training mode. Emit admission thresholds and scheduling
constraints by storage class.

Directions: D4, D9, D10.

### Q29 — Binding minimum-code metric

Define the objective used to minimize Cassette's original executable code, separating authored lines,
generated code, binary size, dependency surface, processes, language runtimes, duplicated logic, and
model-specific branches. Emit a measurable optimization target and non-negotiable correctness terms.

Directions: D12.

### Q30 — Numerical kernel ownership

Determine which existing Apple, MLX, llama.cpp, Metal, Metal Performance Shaders, Accelerate, Core
ML, or other open kernels can execute each required operator without violating Cassette's storage
and quality contracts. Emit an operator dispatch table and identify only the irreducible new kernels.

Directions: D3, D7, D12.

### Q31 — Single agent protocol surface

Determine whether one canonical Cassette protocol can satisfy Codex, Ollama, OpenClaw, Hermes, and
custom agents through generated or declarative adapters. Emit the canonical schema, adapter rules,
and irreducible deviations.

Directions: D11, D12.

### Q32 — Shared implementation across lifecycle operations

Determine which parsing, hashing, streaming, paging, scheduling, versioning, and protocol machinery
can be shared across download, verification, compilation, inference, training, export, and recovery.
Emit one component graph with no parallel authorities.

Directions: D5, D6, D7, D9, D12.

### Q33 — Data-driven versus executable behavior

Determine which architecture, layout, routing, precision, compatibility, and protocol variation can
be represented in manifests or generated plans rather than handwritten branches. Emit the boundary
between semantic model decisions, declarative data, deterministic harness code, and numerical kernels.

Directions: D6, D12.

### Q34 — Exact demonstrated contribution

Determine which complete-system behavior constitutes Cassette's novel contribution: general
drive-resident model execution, post-training compilation, writable cartridge training, adaptive
precision, near-laboratory agent service, minimum-code integration, or a required combination. Emit
one claim whose terms correspond to live-proven behavior.

Directions: D15, D16.

### Q35 — Bounded collision check

After Q34 is backed by a working system, determine whether an existing public system or patent
implements every material element of the exact claim. Emit collisions, distinctions, search boundary,
and any required claim correction; do not substitute this check for engineering.

Directions: D16.

### Q36 — Diagnostic fixture ladder

Determine the smallest controlled artifacts that isolate parser, layout, paging, kernel, routing,
training, and protocol defects without becoming Cassette's completion target. Emit a fixture ladder
whose final mandatory stage is the full-scale acceptance model from Q39 and Q80.

Directions: D2, D6, D7, D15.

### Q37 — Scale-transfer evidence

Determine which mathematical bounds and controlled measurements justify transfer from diagnostic
fixtures to frontier-scale total parameters, active parameters, page counts, context state, and
training state. Emit scaling functions, observed breakpoints, and mandatory full-scale confirmations.

Directions: D2, D14, D15.

### Q38 — Compatibility-bound falsification

Define the lower-bound results that classify one model, Apple-compute, and storage tuple as
incompatible, including bytes per token, compute, quality loss, latency, working-set instability, and
training-state requirements. Emit exclusion thresholds, a causal record, and the next mechanism or
supported tuple to test; no failed tuple may terminate complete-system work or redefine a partial
artifact as Cassette.

Directions: D2, D14, D15.

### Q39 — Binding controlled-reference matrix

Select a reproducible matrix of frontier-scale model classes, Apple-compute classes, unified-memory
budgets, USB-C storage classes, model source services, and agent clients for the first complete
release. Emit representative boundaries and no personal-device assumptions.

Directions: D3, D4, D14, D15.

### Q40 — Native structure versus model transformation

Determine, per architecture class, whether Cassette can exploit existing sparsity and routing without
changing the model or must apply deterministic reorganization, quantization recovery, router training,
or broader post-training. Emit the least invasive transformation that satisfies Q12–Q20.

Directions: D2, D6, D8.

### Q41 — Supported physical cartridge classes

Determine which removable flash, SATA SSD, and NVMe SSD media exposed through USB 3.x, USB4, or
Thunderbolt over USB-C satisfy Cassette's capacity, sustained I/O, durability, removability, and
protocol requirements. Emit predicates over media, transport, bridge, and enclosure classes rather
than brand-specific endorsements.

Directions: D4, D15.

### Q42 — Sustained storage qualification

Define the cold, warm, sequential, random, mixed, queued, and long-duration measurements that produce
\(B_s\), latency distributions, and write limits for a storage class. Emit pass conditions tied to
model access patterns rather than advertised peak bandwidth.

Directions: D4, D14.

### Q43 — Transport and enclosure variables

Determine how cable, port protocol, hub, bridge controller, firmware, queue depth, alignment, SLC
cache exhaustion, thermal throttling, power delivery, and command flush behavior alter Cassette's
operating envelope. Emit variables the runtime profiler must measure or obtain.

Directions: D4, D10, D14.

### Q44 — Filesystem and allocation contract

Determine the filesystem, extent allocation, alignment, sparse-file, cloning, encryption, durability,
flush, and portability semantics required by cartridge pages and training transactions. Emit the
supported filesystem contract and disqualifying behaviors.

Directions: D4, D6, D10.

### Q45 — Storage-to-compute copy path

Determine the macOS path from external block storage through filesystem and virtual-memory layers to
CPU- and GPU-visible buffers and, where eligible, Neural Engine execution resources. Emit the minimum
copy count, DMA and synchronization opportunities, alignment requirements, and conditions for
asynchronous direct loading.

Directions: D3, D4, D7.

### Q46 — Operating-system interference model

Determine how unified buffer caching, compression, swap, memory pressure, filesystem maintenance,
indexing, backup, encryption, and power management alter model residency, timing, privacy, or internal
storage use. Emit controls, observations, and unsupported states across macOS versions.

Directions: D3, D4, D10, D13.

### Q47 — Unified-memory budget function

Define \(M\) as a runtime function of physical memory, operating-system reserve, other agent
processes, executable state, \(W(r,t)\), \(C(t)\), \(K(r,t)\), activations, and training state. Emit
admission and eviction rules that prevent uncontrolled macOS swap.

Directions: D3, D7, D8.

### Q48 — Sustained Apple and storage thermal envelope

Determine how fanless and actively cooled Apple-compute classes and external-storage classes change
\(B_m\), \(B_s\), compute throughput, and training writes over long sessions. Emit sustained operating
curves and throttling-aware scheduling rules.

Directions: D3, D4, D14.

### Q49 — Removable-cartridge lifecycle

Define state transitions for disconnect, reconnect, sleep, wake, bus reset, port migration, changed
volume identity, read-only remount, and device replacement during every lifecycle operation. Emit
agent-visible errors, resumability, identity checks, and durable invariants.

Directions: D4, D10, D11.

### Q50 — Remote metadata preflight

Determine which source metadata provides model size, architecture, precision, active parameters,
context, custom operations, tokenizer, license, revisions, shard digests, and training requirements
before download. Emit normalized fields, trust levels, and missing-data behavior.

Directions: D5, D13.

### Q51 — Resumable multi-terabyte transfer

Define content-addressed, ranged, parallel, resumable direct-to-cartridge transfer with incremental
integrity verification. Emit chunk identity, partial-state format, retry rules, source revision locks,
and final commit proof without rereading the entire artifact.

Directions: D5, D10, D13.

### Q52 — Minimal source-adapter boundary

Determine the smallest adapter interface that normalizes Hugging Face object storage and manifests,
Ollama blobs, Tinker outputs, authentication, revisions, and future sources. Emit a declarative
adapter contract and prevent source-specific lifecycle forks.

Directions: D5, D11, D12.

### Q53 — Cartridge capacity admission

Derive required free space before download, transformation, rollback, precision refinement, training,
optimizer state, and updates. Emit an admission equation over \(S_{peak}\) and a no-overcommit rule
that remains valid across lifecycle transitions.

Directions: D4, D5, D6, D9.

### Q54 — Revision and delta acquisition

Determine when a model revision can be applied through verified shard or page deltas instead of a
complete redownload. Emit ancestry checks, delta integrity, compilation invalidation, rollback, and
source reconciliation rules.

Directions: D5, D6, D10.

### Q55 — Custom-code containment

Determine how Cassette inspects model configuration and artifacts without executing untrusted code,
then contains any custom operations required for compilation, inference, or training. Emit trust
boundaries, allowed capabilities, reproducible build inputs, and rejection conditions.

Directions: D5, D13.

### Q56 — Compatibility decision before transfer

Define the preflight classifier that returns `SUPPORTED`, `SUPPORTED_AFTER_PREPARATION`,
`METADATA_INSUFFICIENT`, or `UNSUPPORTED` before costly transfer whenever the source contract permits.
Emit reasons, required resources, and the exact deferred checks for insufficient metadata.

Directions: D5, D13, D15.

### Q57 — Canonical cartridge representation

Determine whether one on-drive representation can serve source preservation, executable paging,
adaptive precision, training, integrity, and export, or whether linked representations are necessary.
Emit tensor/page schemas, indexes, alignment, provenance, and authority rules.

Directions: D1, D6.

### Q58 — Proof of complete parameter capacity

Define the invariant proving that every parameter, expert, precision contribution, tokenizer asset,
operator, and required model semantic from Q1 remains represented and addressable after \(T\). Emit
bijective mappings or explicit lossy transformations with bounded quality evidence.

Directions: D1, D2, D6.

### Q59 — Multiple hardware plans without weight duplication

Determine how one cartridge stores layouts, page orders, cache policies, precision budgets, and
kernel plans for several Apple and storage classes while sharing the same parameter bytes. Emit the
selection function and metadata-size bound.

Directions: D3, D6, D8.

### Q60 — Recoverable compilation transaction

Define a streaming compiler that resumes after interruption without trusting incomplete pages,
indexes, or manifests. Emit write ordering, temporary identity, page verification, commit markers,
garbage collection, and rollback semantics.

Directions: D6, D10.

### Q61 — Layout evolution after training

Determine how changed activations, routing, precision, tensors, tokenizer state, or operators alter
page clusters and execution plans. Emit incremental layout-update rules, thresholds requiring full
recompilation, and preservation of prior valid revisions.

Directions: D6, D8, D9.

### Q62 — Page integrity and repair

Define page-level checksums, Merkle or equivalent aggregate identity, background verification,
source reacquisition, parity or replication options, and model availability during repair. Emit the
corruption state machine and agent-visible failure contract.

Directions: D5, D6, D10, D13.

### Q63 — Runtime state placement

Define where dense parameters, routed parameters, attention state, \(W(r,t)\), \(C(t)\), \(K(r,t)\),
activations, logits, protocol buffers, and speculative state reside during prefill and decode. Emit a
time-indexed placement and transfer schedule constrained by \(M\), \(B_s\), and \(B_m\).

Directions: D3, D4, D7, D8.

### Q64 — Working-set prediction failure

Determine how the runtime detects an incorrect request-level prediction before quality diverges,
loads corrective pages, preserves deterministic token semantics, and updates future routing. Emit
confidence measures, miss thresholds, synchronization, and bounded-stall behavior.

Directions: D7, D8, D14.

### Q65 — Concurrent agent requests and model switching

Determine whether the first complete release supports concurrent requests, independent contexts,
multiple agent clients, and multiple cartridge models. Emit scheduling, fairness, cache isolation,
page-churn bounds, cancellation, and admission rules.

Directions: D7, D11, D14.

### Q66 — Long-context, multimodal, reasoning, and tool semantics

Determine how context growth, vision encoders, reasoning history, structured output, dynamic tools,
and multi-turn agent state alter storage, compute, protocol, quality, and working-set requirements.
Emit capability-specific execution and acceptance contracts.

Directions: D2, D7, D11, D14.

### Q67 — Baseline equivalence manifest

For each evaluated model revision, construct the exact equivalence record joining weights, templates,
sampler, reasoning effort, context policy, tools, agent harness, output limits, and provider-side
features. Emit which hidden or unavailable service features prevent a valid parity claim.

Directions: D2, D11, D14.

### Q68 — Numeric near-laboratory thresholds

Set binding thresholds for \(L_a\), \(L_p\), \(L_d\), \(R_d\), total task time, error rate,
availability, and \(Q_c/Q_b\) by compatible class. Emit absolute limits and baseline-relative ratios
that the implementation must pass.

Directions: D2, D14, D15.

### Q69 — Tail latency and temporal variability

Determine acceptable p50, p95, p99, maximum stall, jitter, throughput decay, and thermal-session
variation for agent workloads. Emit distributional acceptance tests; do not reduce performance to a
single average or peak.

Directions: D7, D14.

### Q70 — Mandatory training matrix

Select the training and post-training operations that every compatible cartridge, or each declared
compatibility tier, must complete for the first release. Emit model classes, data sizes, update scope,
time and storage bounds, quality criteria, and resulting revision checks.

Directions: D9, D15.

### Q71 — Drive-resident training dataflow

Define the per-step production, consumption, transfer, update, and retirement schedule for batches,
activations, gradients, optimizer state, master values, parameter pages, journals, checkpoints, and
deltas. Emit a time-indexed dataflow graph that satisfies Q23 placement, overlaps lawful I/O with
compute, stays within \(M\), and proves that prohibited full-state copies cannot appear on internal
storage.

Directions: D4, D9, D10.

### Q72 — Paged optimizer execution without hidden full masters

Determine how Q24's update mathematics executes page by page at frontier scale without assembling a
hidden full high-precision model on internal storage or in unified memory. Emit page ordering,
optimizer-state joins, accumulation precision, synchronization, transfer volume, memory bounds, and
the equivalence test against the unpaged update.

Directions: D1, D8, D9, D13.

### Q73 — Atomic model-version commits

Determine whether training commits immutable deltas, replacement pages, or consolidated revisions.
Emit version identifiers, dependency order, atomic root update, reader isolation, rollback, garbage
collection, and verification before a revision becomes callable.

Directions: D1, D9, D10.

### Q74 — Training endurance and resource admission

Define model- and storage-class admission from projected bytes written, write amplification, free
space, temperature, power, duration, and checkpoint cadence. Emit rejection and throttling rules that
protect cartridge integrity while completing admitted jobs.

Directions: D4, D9, D10.

### Q75 — Incremental recompilation after tuning

Determine which trained changes can update routing, precision, page placement, quality evidence, and
hardware plans incrementally. Emit dependency hashes, affected-component closure, recomputation
algorithm, and conditions requiring a complete new cartridge revision.

Directions: D6, D8, D9, D10.

### Q76 — Named-agent conformance adapters

Map the canonical protocol from Q31 to the exact model-discovery, request, streaming, reasoning,
tool, cancellation, error, training, and status semantics required by Codex, Ollama, OpenClaw,
Hermes, and custom endpoints. Emit a field-and-state translation matrix, minimal adapters, and
machine-executable bidirectional conformance tests.

Directions: D11, D12.

### Q77 — Capability and harness negotiation

Define how an agent discovers context limits, modalities, reasoning fields, tool semantics, structured
output, training capabilities, performance tier, cartridge revision, and required conversation state.
Emit machine-readable capability negotiation that preserves each model's effective harness behavior.

Directions: D2, D11.

### Q78 — Proof of minimum executable code

Apply Q29 to the completed architecture. Emit a component-by-component accounting of authored code,
generated plans, reused kernels, dependencies, protocol adapters, and duplicated behavior; then prove
that removing any remaining original component violates a named acceptance condition.

Directions: D12, D15.

### Q79 — Provenance, privacy, and local-execution proof

Define how Cassette proves model-source identity, shard and page integrity, custom-code containment,
credential isolation, absence of unintended internal full-model copies, absence of hidden remote
inference, and privacy of prompts, outputs, and training data. Emit auditable evidence and failure
conditions for each claim.

Directions: D1, D3, D4, D5, D13.

### Q80 — Non-negotiable complete-system acceptance matrix

Define the exact frontier-scale model classes, Apple-compute classes, USB-C storage classes, source
services, inference workloads, training operations, agent clients, lifecycle failures, quality
thresholds, latency thresholds, code-minimum proof, offline conditions, and recovery cases whose live
pass marks Cassette complete. Emit a machine-executable acceptance matrix; no paper, prototype,
simulator, personal-device anecdote, remote-model substitution, or human-facing demonstration may
replace any required row.

Directions: D11, D12, D14, D15, D16.
