# Cassette pure mathematics laboratory

This directory is an isolated research notebook. Production modules do not import it, and the
work here does not amend `MATHS.md`, schemas, plans, tests, or implementation status.

The laboratory has one purpose: derive and attack mathematical foundations that could materially
improve Cassette. Programs may search finite cases or falsify conjectures. They are never proofs.
A result advances only after a written proof survives independent reconstruction and a current
primary-source collision search.

The current lead problem asks for the exact residual-access cost of unbiased page-sampled matrix
execution. The existing Frobenius bound is sufficient. The laboratory is testing whether a
strictly sharper minimax invariant gives the necessary and sufficient mean-square certificate
inside the declared sampling model.

## Current artifacts

- `notes/minimax_residual_access.md` contains the working proofs.
- `minimax_residual_sampling.py` searches finite cases for counterexamples.
- `FALSIFICATION_RESULTS.md` records the fixed-seed run and its evidentiary limits.
- `report-source.md` records the primary-source collision search and claim boundary.
- `paper/spectral_residual_access.tex` is the manuscript source.
- `output/pdf/spectral-residual-access-complexity.pdf` is the rendered paper.

None of these files is a production authority. Adoption requires a separate decision and change.
