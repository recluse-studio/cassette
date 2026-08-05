# Cassette — Remit

Originally written as the project's opening statement. Amended 2026-08-05 to record my
clarifications of intent, given in direct conversation. The amended text below is authoritative
and governs every other document in this repository.

## Purpose

I want to do something with LLMs that no one has done and that will be very valuable, something we
can do together and I can make open source. Not another app, but something with an LLM itself.

The project is named **Cassette**. That name is mine. Names introduced by earlier research are not
the project name and do not define what I am trying to build.

The starting idea was being able to store an LLM downloaded from Hugging Face or Ollama on physical
storage, such as a 2 TB LaCie Rugged, and building a bridge that allows one to run the LLM on a
MacBook Air or another Mac. The LaCie was an example of the physical-storage class. It was not an
instruction to commit the project or its research to one drive, one Mac, or my specific hardware.

## The thesis

I was not trying to be severe. I was insisting on something novel that solves the real problem:
today it is impossible to run frontier models on consumer hardware. The thesis of Cassette is
storing the majority of everything on external storage and freeing consumer hardware to do the
work it was built to do.

Consumer Apple classes are therefore the target of the thesis. Larger Apple classes, such as a
512 GB Mac Studio, are build and teacher infrastructure — legitimate tools for compiling, tracing,
and verifying cartridges — not the machine the result is for.

## Components

Cassette begins with these components:

- macOS and an Apple architecture or device;
- an external USB-C drive using flash or SSD storage;
- a very large yet downloadable large language model. Kimi K3 names the level of model I want
  Cassette to enable a consumer to run — a level, not a binding artifact. A pinned K3 revision
  remains the working exemplar and evidence anchor, and substituting a different open
  frontier-class model of equal or greater level with more cartridge-compatible geometry is
  permitted as a recorded remit-level decision. A conveniently smaller model substituted for the
  level remains forbidden;
- downloadable model sources such as Hugging Face, Ollama, Tinker, and future equivalent sources;
- agent systems and endpoints including Codex, Ollama, OpenClaw, Hermes, and custom endpoints.

The intended operation is equally direct:

1. The user chooses a downloadable model from Hugging Face, Ollama, Tinker, or another supported
   source.
2. Cassette downloads the full model directly to the external drive.
3. The user does “something”—a button, a prompt, or some other control.
4. Cassette does things. The method remains open because discovering and building the right method
   is part of the work.
5. The model is now usable in Codex, Ollama, OpenClaw, Hermes, a custom endpoint, or another
   compatible agent system.

## What “not another app” means

I said this should not be another app. I did not say there could be no UI. Cassette may have a
button, prompt, interface, or other control surface where one is useful, but the valuable work must
be with the LLM itself and with the hardware and code that make the full drive-resident model usable.
The presence or absence of a UI does not settle whether Cassette has fulfilled the remit.

## Where the model lives

Do not drift into hosting the model on the Mac. The external physical drive is where the full local
model lives. The Mac supplies Apple computation, memory, and I/O coordination against that model;
it must not quietly become an ordinary Mac-resident model installation for which the external drive
is only an archive, download destination, or backup.

The hosted laboratory service is a comparison for experience and capability, not a substitute model
that Cassette may call behind the scenes. The result must come from the model downloaded to the
external physical drive and the Apple hardware working against it.

## Performance and capability

The performance language in the original text of this remit pointed at the type of experience I am
interested in; it was never a datacenter parity contract. Its binding meaning is this:

The completed result must deliver frontier-class capability on the consumer machine. For every
tuple Cassette declares compatible, the result must satisfy absolute usability floors; it must
decisively exceed the strongest model the same machine can run unaided, above all where parameter
capacity lives — long-tail knowledge and breadth; it must close more than half the measured
capability gap between that unaided alternative and the selected model's own full-capacity
reference; and it must measure and publish the remaining gap to the laboratory service honestly.
Laboratory parity may be claimed only where it actually passes. It is never the release gate.

“Approach” therefore means user experience, judged against what the consumer machine could
otherwise do. I remain unconcerned with the methods used to reach it. Cassette may do whatever
work is required at the model, hardware, and code levels, provided the completed result carries
the selected model's capacity provably — present, reachable, and consequential — and does not
redefine the selected model into a smaller achievement.

## Fine-tuning and post-training

The locally stored model, if it suits fine-tuning or post-training—not all models do—must accept
fine-tuning, post-training, or related updates where it sits on the external physical drive. The
operation must not depend on moving the full model or a hidden full training copy onto internal
storage. The resulting trained model must remain a usable Cassette model and remain available to the
same agent systems and endpoints.

## Compilation compute

The one-time compilation of a frontier cartridge — teacher tracing, transformation, and recovery
training — may use large non-Apple compute, provided the complete transform record is open and
reproducible and the resulting cartridge verifies by identity like any acquired artifact. Runtime
is a different matter: inference and training against the cartridge remain strictly local to Apple
hardware and the external drive, and no hosted service may ever be called at runtime.

## Minimum code

The code must be the absolute minimum amount of code physically possible while still producing the
fully working result. Cassette should contain original executable code only where that code is
necessary to make the complete system work.

Minimum code does not mean a partial result. It does not permit the work to omit model acquisition,
external-drive operation, inference, training where compatible, agent interoperability, quality, or
performance merely because those parts require code.

## Completion boundary

Assume the result is a fully working Cassette, not a research paper, a proven hypothesis, a small
proof-of-concept application, a simulator presented as the product, or any other half-measure.
Research artifacts and small tests may answer a bounded question, but they cannot replace the
complete operation from model selection and direct external-drive download through preparation,
use, compatible training, and agent access.

Completion is judged by the gates defined in this remit as encoded in
research/ACCEPTANCE_MATRIX.yaml. The severity of this remit lives in honesty and falsification,
not in datacenter parity.

## Research stance

I know the immediate reaction may be “unfortunately it cannot be done,” but I am asking the work to
think hard and research the nature of LLMs and hardware at a fundamental level. Research how to do
this at the hardware level and code level itself. Investigate how an external drive works, how
USB-C and its underlying transports work, how modern Mac architectures work, how very large models
are represented and downloaded, how Apple hardware moves and computes their parameters, and what
the code must do across those boundaries.

I specifically ask the work to stick to first principles: the maths, the physical capabilities, the
metal — not tricks or hyper-complicated harnesses. A transformation forced by the bandwidth
hierarchy is the mechanism. A harness that games an evaluation, a hidden remote call, or a silently
smaller model is a trick.

This is first-principles research, not secondary-source research wearing an engineering hat. Other
research, source code, specifications, and public systems may be consulted, but finding somebody
else’s paper or project is not the answer. The research must derive what Cassette needs from the
actual mathematics, formats, byte paths, memory paths, compute paths, storage behavior, protocols,
failure states, and code-level constraints that govern the complete system.

The research is general. It is not research for my specific hardware. Do not inspect the current
Mac, attached storage, installed runtimes, local model caches, or current client configuration and
call those things the target. Research Apple compute classes, external-drive classes, source
classes, model classes, and agent contracts in a reproducible form that can support many machines
and drives. A named physical instance becomes a target only if I explicitly name it as one later.

Research must not continue endlessly. Take the focused list of questions, answer each one
efficiently and expertly, reach a clear “this is the answer, moving on,” and continue down the list.
The purpose of every answer is to let a capable implementation model ingest the result and make
Cassette real without having to repeat the same research.

## Deliverable language

Research and implementation deliverables must speak directly to the high-level mathematical and
computational agent that will build Cassette. They are agent-to-agent communications, never
agent-to-human deliverables. State equations, byte bounds, hardware behavior, data structures, state
transitions, protocols, algorithms, acceptance conditions, and exact implementation instructions.
Do not replace those with product copy, a human tutorial, a recommendation menu, or an invitation
for a person to decide routine engineering details.

Work remains within this remit only while it is directed toward the complete sequence described
above: a selected full downloadable model, written directly to an external USB-C flash or SSD,
made usable through consumer Apple hardware at frontier-class capability as defined above,
trainable there when the model permits it, available to the named agent systems, open source, and
implemented with no more original executable code than the complete result actually requires.
