# Cassette — Philosophy

Recorded 2026-08-05. This is why Cassette exists and what it stands for. Every value claimed here
is bound to the machinery that enforces it. In this repository, a value without an acceptance row
is marketing.

## Why this exists

Frontier-class open weights already exist and are already public. The capability has been
released; it is locked behind datacenter hardware. The weights are free — the capability is not.
Cassette adds no new capability to the world. It removes an infrastructure barrier to capability
that model publishers have already chosen to give away, and it hands that capability to the
person who owns an ordinary machine.

## The claims, and what enforces them

**Privacy.** Inference and training on a Cassette cartridge can be proven to leave no byte of the
user's material off the machine. Not promised — proven: release fails unless every execution and
training row passes with external network disabled, sockets traced, and internal storage scanned
(Q79; offline_and_privacy_rows in research/ACCEPTANCE_MATRIX.yaml). No hosted service can
structurally offer this.

**Sovereignty.** A model on a cartridge you own cannot be deprecated, re-priced, re-aligned, or
turned off. Callable revisions are immutable, identity is content-addressed, and the cartridge —
not any server, and not the Mac — is the authoritative store (Q1, Q22, Q49, Q57, Q73). A verified
cartridge is also an archival artifact: it preserves a model, with complete provenance, after its
hosting disappears.

**Honesty.** Cassette never overstates what it delivers. The measured gap to the laboratory
service is computed and published for every row; suppressing an unfavorable measurement is a
failed release; parity language may be used only where parity actually passes; papers, simulators,
small models, and demonstrations are forbidden as completion evidence (Q68 honesty vector,
forbidden_completion_evidence, falsified_claims). This repository has already falsified one of its
own acceptance rows by static arithmetic and recorded the result rather than softening the bound
(E-011). That is the standard.

**Provenance and lawfulness.** Cassette operates only on lawfully published weights. License
identity is part of a model's canonical identity tuple, and the audit bundle traces every byte
from source revision to cartridge page (Q1 license_digest, Q51, Q79). Cassette is not a vehicle
for leaked or unlicensed weights.

**No fabricated capability.** Adapters may not invent reasoning, tools, cancellation, or training
semantics a model does not have; unsupported means unsupported (Q76 no_fabricated_feature, Q77).

**Accessibility, with its honest boundary.** The thesis is frontier-class capability on the
machine people already own. The release gate measures Cassette against that machine's own unaided
ceiling, not against a datacenter (Q68 value gate versus B_native). The boundary stated plainly:
the first release presumes a consumer Mac and an external drive. That reaches anyone with an
ordinary laptop, not just anyone with a datacenter. It does not reach everyone, and this project
will not claim that it does.

## What Cassette is not

Cassette is neutral infrastructure. It moves bytes, proves identity, and executes what a
publisher released. It does not strip safety training, does not ship jailbreaks, and does not
select or favor models by permissiveness. Whether frontier weights should be published openly is
a live societal debate that belongs to publishers and the public; Cassette inherits that debate
rather than settling it, and it adds nothing to the risk side beyond convenience — everything it
enables was already possible for anyone with rented hardware. What it changes is who receives the
benefits that were already released but not yet reachable: privacy, permanence, and capability.

## The principle

Every value above is enforced by a row that can fail. When a claim and a measurement conflict,
the measurement wins and is published. A value without an acceptance row is marketing.
