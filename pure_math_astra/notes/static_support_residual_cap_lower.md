# static_support_residual_cap_lower.md — direct finite-advice residual lower bound for static support laws on the identity-Gram Stiefel orbit; depends on finite_advice_stiefel_orbit_lower.md and two_column_unbiased_finite_advice_lower.md.

Status: proved under the stated static, label-local model.  This note
replaces the proposed disjoint-block compactness route in that model.  It
does not apply to a query-dependent support law, a source-dependent law
inside one advice label, or a nonidentity Gram matrix.

## Statement

Let \(p>q\), let \(A\) range over the real Stiefel manifold
\(\mathcal V_{p,q}\), and let a source encoder partition that manifold
into at most \(N\) measurable cells \(C_a\).  In cell \(a\), a decoder
uses a fixed support law \((p^a_S)_{S\subseteq[q]}\), independent of the
source in that cell and of the query.  On support \(S\), it observes
\(A_{:S}\) and returns a Borel output \(F^a_S(A_{:S},x)\).  Internal
randomness is allowed if it is independent of the source after these
inputs are fixed.

Suppose that the decoder is exactly unbiased on its own cell,

\[
 \sum_S p^a_S F^a_S(A_{:S},x)=Ax
 \quad(A\in C_a),
 \tag{1}
\]

and has uniform squared-error bound

\[
 \sum_S p^a_S\|F^a_S(A_{:S},x)-Ax\|_2^2\le C
 \quad(A\in C_a,\ \|x\|_2=1).
 \tag{2}
\]

Assume the expected number of observed columns is at most \(0<\bar s<q\)
for every label:

\[
 \sum_Sp^a_S|S|\le \bar s.
 \tag{3}
\]

Then

\[
 \boxed{
 C\ \ge\ {q-\bar s\over\bar s}\min\!\left\{1,
 \left({2\over N}\right)^{2/(p-q)}\right\}. }
 \tag{4}
\]

For a hard cap \(|S|\le s<q\), take \(\bar s=s\).  In particular, the
same result covers a law supported on any collection of overlapping
supports; it is not limited to a partition into equal-size blocks.

## Proof

First replace every randomized branch by its conditional mean given its
label, support, observed columns, and query.  Jensen preserves (1) and
can only reduce the left side of (2), so take the branch outputs to be
deterministic.

Fix a nonnull label cell \(C_a\).  Since

\[
 \sum_{j=1}^q\sum_{S\ni j}p^a_S
 =\sum_Sp^a_S|S|\le\bar s,
\]

there is an index \(j=j(a)\) whose inclusion probability

\[
\theta=\sum_{S\ni j}p^a_S
 \le {\bar s\over q}.
 \tag{5}
\]

Put \(W=A_{:-j}\).  Since \(\theta<1\), define the output mean over the
branches that omit \(j\),

\[
 H(W)={1\over1-\theta}
       \sum_{S\not\ni j}p^a_S F^a_S(A_{:S},e_j).
 \tag{6}
\]

Every term in (6) observes only columns of \(W\), so \(H\) is a Borel
function of \(W\), including when \(\theta=0\).  In that case, exactness at \(e_j\) gives
\(H(W)=a_j\).  Its conditional fiber is a singleton on a
positive-dimensional sphere and hence has measure zero, so the label cell
is null.  Remove such cells.  The selected \(\theta\) cannot equal one
because \(\theta\le\bar s/q<1\).

For the remaining labels, let \(a_j=A_{:j}\) and set

\[
 F_+(A,e_j)={1\over\theta}\sum_{S\ni j}
 p^a_SF^a_S(A_{:S},e_j).
\]

Exactness at \(e_j\) says

\[
 \theta F_+(A,e_j)+(1-\theta)H(W)=a_j,
 \tag{7}
\]

Jensen within each of the two groups and (7) give

\[
 \begin{aligned}
 R(A,e_j)
 &\ge\theta\|F_+(A,e_j)-a_j\|_2^2
       +(1-\theta)\|H(W)-a_j\|_2^2\\
 &= {1-\theta\over\theta}\|H(W)-a_j\|_2^2\\
 &\ge {q-\bar s\over\bar s}\|H(W)-a_j\|_2^2.
\end{aligned}
\tag{8}
\]

Indeed, (8) puts every source in \(C_a\) inside
\(\|a_j-H(W)\|\le\delta\), where
\(\delta^2=C\bar s/(q-\bar s)\).  If \(\delta\ge1\), (4) is immediate.  If
\(0\le\delta<1\), condition on \(W\).  The omitted column \(a_j\) is
uniform on the sphere in \(\operatorname{span}(W)^\perp\), an ambient
space of dimension \(p-q+1\).  The spherical-ball bound used in the
two-column note gives, for any fixed center,

\[
 \Pr\{\|a_j-H(W)\|_2\le\delta\mid W\}
 \le {1\over2}\delta^{p-q}.
 \tag{9}
\]

Projecting \(H(W)\) onto that perpendicular space can only enlarge the
event, so (9) also holds when \(H(W)\) is arbitrary.  Fubini yields
\(\mu(C_a)\le\tfrac12\delta^{p-q}\).  The \(N\) cells cover the
orbit, so \(1\le\tfrac N2\delta^{p-q}\), which proves (4).

## Consequence for the disjoint-block question

For \(m=q/s\) equal disjoint blocks with a per-label fixed law over the
blocks, \(\bar s=s\) and (4) becomes

\[
 C\ge (m-1)
 \min\!\left\{1,
 \left({2\over N}\right)^{2/(p-q)}\right\}.
 \tag{12}
\]

Using the entire omitted block instead of all other columns gives a cap
exponent \(p-q+s-1\).  For \(N>2\), its corresponding factor
\((2/N)^{2/(p-q+s-1)}\) is larger than the coordinate factor
\((2/N)^{2/(p-q)}\), so the block exponent gives a stronger lower bound
when its larger predictor geometry is available.  The coordinate argument
above is more general because it already permits overlapping supports.  No
compactness of the conditional Stiefel-to-Stiefel averaging operator is
needed for this finite-advice lower bound.

The argument is static-schedule-specific.  If the support law may depend
on the query, the least-inclusion coordinate in (5) may change with the
coordinate query; for example, a one-read law can select \(\{j\}\) at
query \(e_j\).  The proof therefore does not bound query-adaptive
sampling.

For a general fixed Gram matrix, conditioning on the other columns leaves
an innovation with squared norm \(1/(G^{-1})_{jj}\), rather than a unit
spherical column.  The present residual/cap calculation then has a
Gram-dependent scale and does not by itself resolve the near-singular
nonisotropic examples.
