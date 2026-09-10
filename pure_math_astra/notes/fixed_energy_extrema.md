# Fixed-energy extrema of spectral sampling variance

Status: provisional supporting theorem, reconstructed independently by the foundation-review agent.
The user rejected the premature move to literature review. Theoretical investigation continues;
this result is not accepted as the requested breakthrough.

## Problem

Let \(\mathbb F\) be \(\mathbb R\) or \(\mathbb C\), let \(q\ge2\), and fix
\(a=(a_1,\ldots,a_q)\in(0,\infty)^q\). Write
\[
T=\sum_j a_j,\qquad A=\max_j a_j,\qquad B=T-A.
\]
For a Hermitian positive-semidefinite matrix \(G\) with diagonal \(a\), define
\[
\nu(G)=\min_{\pi_j>0,\ \sum_j\pi_j=1}
\lambda_{\max}\bigl(D_\pi-G\bigr),
\qquad D_\pi=\operatorname{diag}(a_j/\pi_j).
\]
When \(G=R^*R\), this is the worst-unit-query mean-square error of the optimal fixed,
query-independent, one-column inverse-probability estimator for \(Rx\). This invariant and its
dual were established in the earlier local laboratory. The new question is its variation over
all Gram geometries with the same column energies.

Every minimum above is attained in the open simplex. Indeed,
\(\lambda_{\max}(D_\pi-G)\ge a_j(\pi_j^{-1}-1)\), so a bounded sublevel set stays away from
every simplex face. The uniform law gives a finite comparison value.

## Theorem 1: sharp extremal interval and equality

Let \(u>0\) be the unique solution of
\[
\sum_j\frac{a_j}{a_j+u}=1.
\]
Then every Gram matrix with diagonal \(a\) satisfies
\[
u\le\nu(G)\le
U(a):=
\begin{cases}
T,&A\le B,\\
2\sqrt{AB},&A>B.
\end{cases}
\]
Both endpoints are attained over all such Gram matrices.

1. The lower equality holds if and only if \(G=\operatorname{diag}(a)\).
2. Every rank-one Gram matrix attains the upper endpoint.
3. If \(A>B\), upper equality holds if and only if \(G\) has rank one.
4. If \(A\le B\), upper equality holds if and only if there is a density matrix
   \(X\succeq0\), \(\operatorname{tr}X=1\), satisfying
   \[
   \operatorname{ran}X\subseteq\ker G,\qquad X_{jj}=a_j/T.
   \]

For residuals \(R\in\mathbb F^{p\times q}\), the lower endpoint is realizable only when \(p\ge q\).
The upper endpoint is realizable for every \(p\ge1\). If \(p<q\), the minimum over that
fixed-dimensional class is strictly larger than \(u\); its exact value is a separate question.

### Proof of the lower endpoint

For any probability vector,
\[
\lambda_{\max}(D_\pi-G)\ge\max_j a_j(\pi_j^{-1}-1).
\]
If the right side is at most \(t\), then \(\pi_j\ge a_j/(a_j+t)\), hence
\(\sum_j a_j/(a_j+t)\le1\), which forces \(t\ge u\).
For diagonal \(G\), choosing \(\pi_j=a_j/(a_j+u)\) gives \(D_\pi-G=uI\).

Conversely, suppose \(\nu(G)=u\) and take an attaining law. The same coordinate bounds and
normalization force \(\pi_j=a_j/(a_j+u)\) for every \(j\). Thus \(uI-(D_\pi-G)\) is
positive semidefinite with zero diagonal. A positive-semidefinite matrix satisfies
\(|H_{ij}|^2\le H_{ii}H_{jj}\); consequently this matrix is zero and \(G\) is diagonal.

### Proof of the upper bound when one energy dominates

Relabel so \(a_1=A>B\), set \(\kappa=\sqrt{AB}\), and use
\[
\pi_1=\frac{\sqrt A}{\sqrt A+\sqrt B},\qquad
\pi_j=\frac{a_j}{\sqrt B(\sqrt A+\sqrt B)}\quad(j>1).
\]
Write
\[
G=\begin{pmatrix}A&z^*\\z&H\end{pmatrix},
\qquad H\succeq0,\quad \operatorname{tr}H=B.
\]
The proposed law gives
\[
2\kappa I-(D_\pi-G)
=\begin{pmatrix}
\kappa&z^*\\
z&H+(\kappa-B)I
\end{pmatrix}.
\]
Let \(c=\kappa-B>0\). Positivity of \(G\) implies
\(z=H^{1/2}v\) for some \(v\in\operatorname{ran}H\) with \(\|v\|^2\le A\).
One way to see this is to use the Schur complement at its positive scalar entry \(A\):
\(H-zz^*/A\succeq0\), which gives the range inclusion and
\(z^*H^\dagger z\le A\).
Therefore
\[
\begin{aligned}
z^*(H+cI)^{-1}z
&=v^*H(H+cI)^{-1}v\\
&\le A\,\frac{\lambda_{\max}(H)}{\lambda_{\max}(H)+c}\\
&\le A\,\frac B{B+c}=\kappa.
\end{aligned}
\]
The Schur complement proves the displayed block matrix is positive semidefinite. Hence the
proposed law gives \(\lambda_{\max}(D_\pi-G)\le2\kappa\).

If \(\nu(G)=2\kappa\), this proposed law must attain that value. Its block certificate is
singular. Since \(H+cI\succ0\), its scalar Schur complement is zero, so every inequality in
the preceding chain is an equality. In particular \(\lambda_{\max}(H)=\operatorname{tr}H=B\),
which makes \(H\) rank one. Equality also gives \(\|v\|^2=A\) in its top eigenspace.
Thus \(H=zz^*/A\), and \(G\) is rank one.

### Rank-one lower witness in the dominant case

By diagonal unitary conjugation, a rank-one Gram matrix may be written \(G=ww^*\) with
\(w_j=\sqrt{a_j}\). Let
\[
r_1=1/\sqrt2,\qquad
r_j=-\sqrt{a_j/(2B)}\quad(j>1).
\]
This is a unit vector. For every probability law, Cauchy--Schwarz gives
\[
\begin{aligned}
r^*(D_\pi-ww^*)r
&=\sum_j\frac{a_j|r_j|^2}{\pi_j}-|w^*r|^2\\
&\ge \frac{(\sqrt A+\sqrt B)^2}{2}
-\frac{(\sqrt A-\sqrt B)^2}{2}
=2\sqrt{AB}.
\end{aligned}
\]
The upper bound is therefore exact for rank-one \(G\).

### Balanced case and its equality geometry

The energy law \(\pi_j=a_j/T\) gives \(D_\pi-G=TI-G\), hence \(\nu(G)\le T\).
If a density matrix \(X\) has the stated diagonal and is supported in \(\ker G\), then for
every \(\pi\),
\[
\lambda_{\max}(D_\pi-G)\ge\operatorname{tr}X(D_\pi-G)
=\frac1T\sum_j\frac{a_j^2}{\pi_j}\ge T.
\]
This proves sufficiency of the equality criterion.

For necessity, suppose \(\nu(G)=T\). The energy law is then optimal and
\(\lambda_{\min}(G)=0\). The subdifferential of the largest-eigenvalue function at \(TI-G\)
consists of density matrices supported on \(\ker G\). Convex first-order optimality on the
open probability simplex therefore supplies such an \(X\) for which
\[
\frac{a_jX_{jj}}{(a_j/T)^2}
\]
is independent of \(j\). Since \(\operatorname{tr}X=1\), this condition gives \(X_{jj}=a_j/T\).
This invokes the same finite-dimensional eigenvalue optimality lemma used in the earlier lab;
the literature comparison must credit that known tool.

For rank-one \(G=ww^*\), choose vectors \(v_j\in\mathbb R^2\) of length
\(\sqrt{a_j/T}\) such that \(\sum_j\sqrt{a_j}v_j=0\).
Their weighted lengths are \(a_j/\sqrt T\), so such vectors exist precisely when the largest
length is no greater than the sum of the others, namely \(A\le B\). Their Gram matrix
\(X_{ij}=\langle v_i,v_j\rangle\) is a density matrix with the required diagonal and
annihilates \(w\). The real construction also works over \(\mathbb C\).
This proves the remaining attainment assertion.

### Fixed output dimension

The diagonal Gram matrix has rank \(q\), so it is unavailable when \(p<q\).
The set of positive-semidefinite matrices with fixed diagonal \(a\) and rank at most \(p\)
is compact. The function \(\nu\) is continuous there: a uniform comparison law and the
coordinate coercivity bound restrict all minimizers to one common compact subset of the
probability simplex, after which continuity follows from minimization over that set.
Thus the fixed-rank minimum is attained. The lower equality characterization excludes \(u\),
so that minimum is strictly larger. This is a strict gap statement, not a formula for the gap.

## Consequence to investigate

The fixed energies determine the entire sharp uncertainty interval for the spectral variance
before angles are known. In the dominant regime, the explicit energy-only probability law is
simultaneously safe for every Gram geometry and is attained by rank-one residuals. Consequently,
\[
\min_\pi\ \max_{\substack{G\succeq0\\\operatorname{diag}G=a}}
\lambda_{\max}(D_\pi-G)
=\max_{\substack{G\succeq0\\\operatorname{diag}G=a}}\nu(G)
=U(a).
\]
The upper inequality uses the same explicit law for all \(G\); the lower inequality uses the
rank-one witness. In the balanced regime the common law is \(\pi=a/T\).
This is a robust-design saddle value, not an appeal to a general convex-concave minimax
interchange. The joint objective is not assumed concave in \(G\).

The common robust law is unique. Any robust-optimal law is optimal for a rank-one Gram matrix;
the earlier lab proves uniqueness of that law in both energy regimes. A standalone paper must
either prove the uniqueness step here or state and prove the required rank-one lemma.

For Cassette, this suggests an exact worst-geometry certificate using column-energy metadata
alone. It reduces the current Frobenius upper bound from \(T\) to \(2\sqrt{AB}\) when one
residual column contains more than half the energy. This ratio is unbounded as \(B/A\to0\).
The statement concerns the declared coordinate sampler and mean-square error. It does not
prove practical speed, a general lower bound for all algorithms, or an end-to-end model guarantee.

## Open extension

For equal energies and \(1\le p<q\), a construction using one collinear group of
\(m=q-p+1\) unit columns and \(p-1\) orthogonal singleton columns gives
\[
\nu(G)=\frac{q-1+\sqrt{(q-1)^2+4m}}2.
\]
The formula follows by assigning equal probability within the collinear group and equal
probability to each singleton, then equalizing the group-nullspace and singleton eigenvalues.
Whether this construction globally minimizes \(\nu\) at fixed rank is unproved here.
