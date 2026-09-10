# Independent exact review of the rank-two skew-cycle certificate

Status: verified. The certificate proves the real finite three-polar lemma
for the displayed family \(K_t\), \(t\ge0\), with \(\rho_3=1\). This is
only a family result.

Let

\[
K_t=t\begin{pmatrix}0&1&-1\\-1&0&1\\1&-1&0\end{pmatrix},
\qquad
s=t+\sqrt{1+t^2},\qquad
D=\sqrt{1+2s^2}.
\]

The map \(t\mapsto s\) is a bijection from \([0,\infty)\) to
\([1,\infty)\), with \(t=(s-s^{-1})/2\). The unnormalized certificate is

\[
\widetilde u=(1,-s,-s)^T,\qquad
\widetilde n=(1,-s,s)^T.
\]

Both squared norms equal \(D^2\). For each nonvoid pair \((E,J)\), the
normalized inequality is therefore equivalent to

\[
\Delta_{EJ}
=\|\widetilde u_E\|^2\det M_{EJ}
-v_{EJ}^T\operatorname{adj}(M_{EJ})v_{EJ}\ge0,
\]

where

\[
M_{EJ}=I+K_{E,J}^TK_{E,J},\qquad
v_{EJ}=\widetilde n_J+K_{E,J}^T\widetilde u_E.
\]

The cancellation of \(D^{-2}\) is valid on both sides, and each \(M_{EJ}\)
is positive definite. This includes \(t=0\), where \(K_t=0\).

## Exact table check

I recomputed all determinants and adjugate quadratic forms in the Laurent
polynomial ring \(\mathbb Q[s,s^{-1}]\), substituting
\(t=(s-s^{-1})/2\). Matrix determinants were expanded by permutations and
adjugates by cofactors; every coefficient was a rational number. No
floating-point evaluation or sampling was used.

The result agrees exactly with every entry in the author table:

- all nine singleton gaps in Equation (7);
- all nine two-by-two gaps in Equation (8);
- the full-support gap in Equation (9).

Equivalently, for each listed nonzero entry, direct coefficient comparison
gave

\[
\Delta_{EJ}=s^m\sum_{\ell\ge1}c_\ell(s-1)^\ell
\]

with precisely the stated \(m\) and \(c_\ell\). The zero entries simplify
identically to zero. Thus all nineteen nonvoid constraints are covered:
nine scalar, nine proper two-by-two, and one full three-by-three condition.

Every listed coefficient is positive. Hence each nonzero gap is
nonnegative for \(s\ge1\), with equality allowed at \(s=1\). This verifies
both the endpoint \(t=0\) and arbitrarily large \(t\); no limiting
continuity argument is needed.

## Scope and wording

The finite certificate itself does not depend on how a scalar feasible
interval is parametrized. The current author note calls its branch endpoint
\(z=s\), while the concurrent endpoint derivation is described as
\(z=1\) for an interval \([1,s]\). Those labels should be reconciled before
being presented as one parametrization. They do not affect the determinant
certificate verified here.

A bare spacing token in Equation (1) was repaired by inserting its missing
backslash.
All display and inline delimiter pairs in the author note are balanced.
