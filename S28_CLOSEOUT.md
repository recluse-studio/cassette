# S28 PHASE MACHINE closeout report

S28 closes the agent-buildable machine and prepares one live campaign. It does not claim that a
real source, physical cartridge, F4 model, F5 model, frontier row, hosted comparison, or Q80 release
has run.

## Scope and source state

- Baseline revision: `804a849` (`Record S26 review method and authority correction — Q36`).
- Queue authority: `IMPLEMENTATION.md`.
- Release authority: `research/ACCEPTANCE_MATRIX.yaml`, schema version 4,
  `blake3:372ddc5da3c64fd837bc95c2a0bca8a5aecc5d47862a1bf306f9f807dbde34c4`.
- Machine evidence: S26 gate
  `blake3:f7c9a1e53346eef5053fc3b759e1f8236a5cae14ce4486f1806fa9a0a5d2a9d7` and S27 report
  `sha256:bb278c5360658b37db770b02213ac5e993b0d3770c02cbcf0c7a34914bbc5343`.
- S28 artifacts: this report and `PHASE_LIVE_RUNBOOK.md`,
  `blake3:b180c539716c8f717a4d6eacf515888e80273c4ab8cac775ee6fddde4cf6ffe0`.
- Product, test, tool, generated, dependency, process, runtime, kernel, and model-branch changes:
  none.

The repository was clean before S28 work began. The system data volume had 55 GiB free, above the
repository's 10 percent stop threshold. The work made no source request, downloaded no model,
inspected no attached storage or local model cache, touched no physical external drive, and started
no live campaign.

## Acceptance record

### Every S-step is resolved

- Test or probe: parse the PHASE MACHINE block in `IMPLEMENTATION.md`, enumerate S01 through S27,
  and read each step's current `status` field.
- Input: the current queue at baseline revision `804a849`.
- Expected: all 27 prerequisite steps are `DONE` or `BLOCKED` with a report, and S27 is `DONE`.
- Observed: all 27 prerequisite steps are `DONE`; zero are `TODO`, `IN_PROGRESS`, or `BLOCKED`.
  S27 records implementation commit `d2893852b0700fbbd1b08467cf377169d8dfb93c`, 307 passing tests,
  zero failed acceptance rows, twelve consequential removal proofs, and
  `J=(0,0,10806,1,1,5,0,0,0)`.

### Blocked-step summary is complete

- Test or probe: filter the same S01–S27 status enumeration for `BLOCKED`.
- Input: every current PHASE MACHINE prerequisite status.
- Expected: name each blocked step, report, root cause, and dependent consequence; if none exists,
  record an explicit empty summary.
- Observed: no S01–S27 step is blocked. The blocked-step summary is empty, and S28 has no blocked
  dependency.

### The Phase Live runbook comes from matrix authority

- Test or probe: resolve the S26 deferred-live projection against the exact matrix sections, then
  compare every runbook phase, model revision, source row, fixture gate, execution row, workload,
  client, training row, live failure injection, offline row, completion contract, and prohibited
  claim with that projection and the matrix.
- Input: `research/ACCEPTANCE_MATRIX.yaml` and
  `tests/fixtures/s26_deferred_live_rows.json` at their recorded digests.
- Expected: one ordered L01–L05 campaign with the principal present; all live evidence begins
  `NOT_RUN`; no fixture-only path or machine result receives a live label.
- Observed: `PHASE_LIVE_RUNBOOK.md` carries L01 storage qualification; L02 live acquisition; L03
  ordered F4 and F5 gates; L04 complete execution, workload, protocol, training, failure, offline,
  privacy, and accounting rows; and L05 Q80 completion from clean roots. It retains every prohibited
  claim and the `READY_FOR_LIVE_FALSIFICATION_ONLY` machine outcome.

## Verification

The S27 resume gate ran before any S28 file changed:

```text
.venv/bin/python -B -m pytest -q -p no:cacheprovider
307 passed in 179.42s

.venv/bin/python tools/ledger.py
violations: []
J: (0,0,10806,1,1,5,0,0,0)
```

The complete post-artifact suite then passed `307/307` in 172.71 seconds. A fresh ledger readback
reported zero violations and the same J tuple; the two documentation artifacts changed no counted
source, test, tool, generated, dependency, process, runtime, kernel, branch, authority, or binary
surface.

After the S28 artifacts are committed, the close commit records the step commit, the final complete
suite, ledger result, artifact digests, and repository state in `IMPLEMENTATION.md`. Until that
close commit exists, S28 remains `TODO` and PHASE LIVE remains ineligible.

## Q30 repair addendum

A post-close review reproduced one false pass in the Q30 ledger guard: `broker.py` could obtain MLX
through `pager._mlx_runtime()` without importing MLX directly. Source repair `0c3e72a` makes direct
and indirect access outside `pager.py` and `trainer.py` fail the same confinement check. The clean
Q29/Q78 proof then passed 307 tests with zero skips, twelve controls, twelve deletion failures, and
twelve executable-bypass failures. The current report is
`sha256:bb278c5360658b37db770b02213ac5e993b0d3770c02cbcf0c7a34914bbc5343`, with
`J=(0,0,10806,1,1,5,0,0,0)`. The repaired runbook identity above supersedes its original S28
identity for the Phase Live preflight; the original closeout remains preserved in Git history.

## Handoff boundary

The next eligible work after the S28 close commit is L01 with the principal present. L01 may inspect
and qualify the explicitly authorized physical paths; L02 owns the first live model-source request.
The matrix result remains `NOT_RUN`, and Cassette is not a completed live product until L05 produces
one reproducible Q80 completion digest.
