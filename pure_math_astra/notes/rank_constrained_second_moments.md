# Rank-constrained unbiased second moments

Status: a finite-dimensional matrix theorem.  It concerns an actual random
resident matrix \(Z\), whose entries may be dense, and does not by itself
supply a finite-byte representation or a Cassette access protocol.  No
originality claim is made.

Let \(\mathbb F\) be \(\mathbb R\) or \(\mathbb C\), let
\(R\in\mathbb F^{p\times q}\), put \(G=R^*R\), and let \(s\) be a
nonnegative integer.  All inequalities below are Loewner inequalities.

## Exact upper-bound characterization

**Theorem.**  For \(H\succeq0\), the following are equivalent.

1. There is a finitely supported random matrix \(Z\) such that
   \[
   \mathbb E Z=R,\qquad \operatorname{rank}Z\leq s\quad\text{almost surely},
   \qquad \mathbb E(Z^*Z)\preceq H.
   \tag{1}
   \]
2.
   \[
   H\succeq G,\qquad \operatorname{tr}(RH^\dagger R^*)\leq s.
   \tag{2}
   \]

The statement concerns an upper bound.  The construction need not have
\(\mathbb E(Z^*Z)=H\).

**Necessity.**  Jensen's identity gives
\[
\mathbb E(Z^*Z)-R^*R
=\mathbb E[(Z-R)^*(Z-R)]\succeq0,
\]
so \(H\succeq G\).  For each realization, let \(P_Z\) be the orthogonal
projection onto the column range of \(Z\).  Since \(P_ZZ=Z\),
\[
\begin{bmatrix}P_Z&Z\\Z^*&Z^*Z\end{bmatrix}\succeq0.
\]
After expectation and addition of
\(\operatorname{diag}(0,H-\mathbb E Z^*Z)\), this gives
\[
\begin{bmatrix}K&R\\R^*&H\end{bmatrix}\succeq0,
\qquad K=\mathbb E P_Z,\qquad \operatorname{tr}K\leq s.
\tag{3}
\]
Because \(H\succeq R^*R\), its null space is contained in the null space of
\(R\); hence \(\operatorname{range}R^*\subseteq\operatorname{range}H\).
The generalized Schur complement of (3) yields
\(K\succeq RH^\dagger R^*\).  Taking traces proves (2).

**Sufficiency.**  Set
\[
A=RH^{\dagger/2}.
\]
The block matrix
\[
\begin{bmatrix}I&R\\R^*&H\end{bmatrix}\succeq0
\]
follows from \(H-R^*R\succeq0\), so \(AA^*\preceq I\).  Take a thin singular
value decomposition
\[
A=U\operatorname{diag}(\theta_1,\ldots,\theta_r)V^*.
\]
Then \(0<\theta_i\leq1\) and
\(\sum_i\theta_i^2=\operatorname{tr}(RH^\dagger R^*)\leq s\).  Put
\(\pi_i=\theta_i^2\).  Since the polytope
\[
\{x\in[0,1]^r:\ \sum_i x_i\leq s\}
\]
has precisely zero-one vertices, there is a random subset
\(S\subseteq\{1,\ldots,r\}\), with \(|S|\leq s\) almost surely and
\(\mathbb P(i\in S)=\pi_i\).  Define
\[
Z_S=\sum_{i\in S}\frac{\theta_i}{\pi_i}\,
u_iv_i^*H^{1/2}.
\tag{4}
\]
The active probabilities are positive.  The rank is at most \(|S|\), and
\[
\mathbb E Z_S=AH^{1/2}=R,
\]
where the last equality uses
\(\operatorname{range}R^*\subseteq\operatorname{range}H\).  Orthogonality of
the \(u_i\)'s gives
\[
\mathbb E(Z_S^*Z_S)
=H^{1/2}VV^*H^{1/2}\preceq H.
\]
This proves (1).  Carathéodory's theorem gives a subset distribution with at
most \(r+1\) atoms, so no measurability issue remains.

## Covariance form

A covariance upper bound \(C\) is feasible,
\[
\mathbb E[(Z-R)^*(Z-R)]\preceq C,
\]
with the same rank and unbiasedness conditions, if and only if
\[
C\succeq0,\qquad
\operatorname{tr}\!\left(G(G+C)^\dagger\right)\leq s.
\tag{5}
\]
Indeed, apply the theorem to \(H=G+C\).  The needed range inclusion is
automatic from \(G+C\succeq G\).  The construction may have strictly smaller
covariance than \(C\), which is sufficient for an upper-bound statement.

## Frobenius-optimal frontier

The least possible second-moment trace is
\[
\min_{H\succeq G,\ \operatorname{tr}(GH^\dagger)\leq s}\operatorname{tr}H.
\tag{6}
\]
Let the nonzero singular values of \(R\) be
\(\sigma_1,\ldots,\sigma_r\).  If \(s\geq r\), the value is
\(\sum_i\sigma_i^2\), attained deterministically by \(Z=R\).  If \(s<r\),
there is a unique \(\tau>0\) such that
\[
\sum_{i=1}^r\min\{1,\sigma_i/\tau\}=s.
\tag{7}
\]
The optimum is
\[
H_*=V\operatorname{diag}\bigl(\max\{\sigma_i^2,\tau\sigma_i\}\bigr)V^*,
\qquad
\min\mathbb E\|Z\|_F^2
=\sum_i\max\{\sigma_i^2,\tau\sigma_i\}.
\tag{8}
\]
Here \(V\) is the right singular-vector matrix of \(R\).  One proof pins
\(H\) to the range of \(G\), applies the KKT equations to (6), and obtains
\(h_i=\max\{\sigma_i^2,\tau\sigma_i\}\).  More explicitly, take the
multiplier \(\tau^2\) for the trace constraint.  On a coordinate with
\(\sigma_i<\tau\), stationarity is
\(1-\tau^2\sigma_i^2/h_i^2=0\); on a coordinate with
\(\sigma_i\geq\tau\), the lower bound \(h_i\geq\sigma_i^2\) is active and
the remaining multiplier is \(1-\tau^2/\sigma_i^2\geq0\).  These KKT
conditions are sufficient because (6) is convex on the support of \(G\).
Equivalently, the construction
above samples singular directions with
\[
\pi_i=\frac{\sigma_i^2}{h_i}
=\min\{1,\sigma_i/\tau\}.
\tag{9}
\]
Thus the uncapped active probabilities are proportional to singular values.
This is the same proportional-to-\(\sigma_i\) form attributed to BCH 2025 in
the investigation prompt; this note records the mathematical consistency
only and does not verify that source or its assumptions.

The frontier is a second-moment result.  Converting its random dense
matrices into stored, finite-byte resident descriptions requires additional
representation and access arguments.
