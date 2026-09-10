# Quantitative basis rigidity: proof route and resource question

Status: the proposed gap problem has a simpler solution through a marginal
sampling bound and convexity of the trace inverse. The complete bound and its
sharp quadratic-order example are recorded in coded_basis_rigidity.md and have
survived two independent calculations.
The identities below survive as an alternative route; they are not needed to
make the earlier equality proof look difficult. A metadata-cost theorem remains
unproved.

Fix a full-column-rank \(R\), put \(G=R^*R\succ0\), and let \(1\le s<q\).
Let \(t_*\) solve
\[
h(t_*):=\operatorname{tr}(G(G+t_*I)^{-1})=s.
\]
For a fixed encoded input basis, let \(\Phi_s(G)\) be the best variance
among \(Z=RD_b\), where \(D_b\) is diagonal, has at most \(s\) nonzero
entries almost surely, and \(\mathbb E D_b=I\).

The exact result in coded_basis_rigidity.md is
\[
\Phi_s(G)=t_*\quad\Longleftrightarrow\quad G\text{ is diagonal}.
\]
The new bound follows because every admissible law needs inclusion marginals
\(\theta_i\ge a_i/(a_i+t)\), while \(\sum_i\theta_i\le s\).
If \(u\) solves \(\sum_i a_i/(a_i+u)=s\), then \(\Phi_s(G)\ge u\).
Writing \(E=G-\operatorname{diag}G\), \(\Lambda=\lambda_{\max}(G)\), and
\(L=\sum_i a_i/(a_i+t_*)^2\), the trace-inverse Jensen gap gives
\[
\Phi_s(G)-t_*\ge u-t_*
\ge\frac{t_*\|E\|_F^2}{(\Lambda+t_*)^3L}.
\]
The route uses standard convexity. It does not establish a substantive original
advance by itself.

The current unresolved question is what a declared, byte-bounded query-transform
family must encode to reduce this gap. A finite transform library, a sequence
of encoded plane rotations, and a general decoder are different classes.
Any lower bound must count every information channel used to form the transform,
including metadata and fresh reads. A library covering argument alone does not
bound arbitrary Cassette descriptions.

## A defect identity available for the next proof

For any admissible \(Z\) with finite second moment, write
\[
H=\mathbb E Z^*Z,\quad P_Z=\operatorname{proj}(\operatorname{ran}Z),
\quad K=\mathbb E P_Z.
\]
Full column rank of \(R=\mathbb EZ\) implies \(H\succ0\).
The expected block-moment identity gives
\[
\mathbb E\|P_Z-ZH^{-1}R^*\|_F^2
=\operatorname{tr}K-\operatorname{tr}(RH^{-1}R^*).             \tag{1}
\]
To verify (1), multiply
\[
\begin{pmatrix}P_Z&Z\\Z^*&Z^*Z\end{pmatrix}
=[P_Z,Z]^*[P_Z,Z]
\]
on both sides by the block column \([I;-H^{-1}R^*]\), take expectations,
and then take the trace.

If \(H-G\preceq(t_*+\epsilon)I\), then
\[
0\le
\mathbb E\|P_Z-ZH^{-1}R^*\|_F^2
\le s-h(t_*+\epsilon).                                      \tag{2}
\]
The right side is at most
\[
\epsilon\sum_i\frac{\lambda_i(G)}
{(\lambda_i(G)+t_*)^2}.                                     \tag{3}
\]
Thus near-optimal variance forces an approximate version of the
projection identity that proved exact basis rigidity.

For real diagonal weights, Hermiticity of \(P_Z\) also implies
\[
\mathbb E\|[D_b,H^{-1}]\|_F^2
\le
\frac{4}{\lambda_{\min}(G)^2}
\bigl(s-h(t_*+\epsilon)\bigr).                               \tag{4}
\]
Indeed, the anti-Hermitian part of \(ZH^{-1}R^*=RD_bH^{-1}R^*\)
has norm at most twice its distance from \(P_Z\); congruence by \(R\)
has smallest Frobenius singular factor \(\lambda_{\min}(G)\).
For complex weights the corresponding expression is
\(D_bH^{-1}-H^{-1}D_b^*\); it must not be silently replaced by a commutator.

Equation (4) does not finish the proof. Some coordinates can share the
same random weight, so a small weighted commutator need not force every
off-diagonal entry to be small. The support cap, unbiasedness, idempotence
defect, and covariance condition must be used together.

## Boundary checks for a proposed quantitative theorem

- At \(s=1\), the exact two-column formula has a linear gap in a small
  off-diagonal perturbation. A quadratic bound might be valid but not sharp.
- For large stable rank and one fresh direction, the unrestricted optimum
  is already close to total energy. A fixed relative-accuracy target can
  therefore make basis information unnecessary. An entropy bound must
  state its accuracy and spectral regime.
- At rank deficiency, the full-column-rank rigidity proof does not apply.
- A finite transform-library bound is a statement about that declared
  library. Sampling metadata or a decoder may carry additional information;
  all channels used to reconstruct the query transform must be counted.
- A scalar coefficient count does not prove a finite-byte implementation.
  Quantization, residual bias, and arithmetic error need their own bounds.

The next discriminating step is a proved stability inequality from
(1)--(4), or an exact family showing why the proposed dependence fails.
