# Uniform large-ray threshold on compact generic rank-two direction sets

Let

\[
 \mathcal G=\{K\in\mathbb R^{3\times3}:\operatorname{rank}K=2,
 \ \|K\|_{\rm op}=1,
 \ K_{ij}\ne0,\ \det K_{E,J}\ne0\text{ for all }|E|=|J|=2\}.
 \tag{1}
\]

The fixed-ray Case A, B, and C constructions imply the following compact
version.

**Theorem.** If \(F\subset\mathcal G\) is compact, then there is
\(T_F<\infty\) such that, for every \(K\in F\) and every \(t\ge T_F\),
there are real vectors \(u=u(K)\), \(n=n(K)\) with

\[
 \|u\|_2=1,\qquad\|n\|_2\ge\frac12,
 \tag{2}
\]

which satisfy every finite three-polar inequality for \(tK\).  The vectors
may depend on \(K\); the threshold does not.

The proof constructs local continuous witnesses before taking a finite
cover. Pointwise existence of unrelated thresholds \(T(K)\) would not
justify the conclusion.

## 1. Local continuous witness data

Fix \(K_0\in\mathcal G\).  On a sufficiently small relative neighborhood
of \(K_0\) in the rank-two stratum, choose unit left and right kernels

\[
 g(K)^TK=0,\qquad K h(K)=0
 \tag{3}
\]

continuously, with their signs fixed by positive inner product with
\(g(K_0)\) and \(h(K_0)\).  The nonzero-coordinate condition keeps every
coordinate of these two frames away from zero after shrinking the
neighborhood.  Hence

\[
 M(K)=D_{g(K)}KD_{h(K)}
 \tag{4}
\]

varies continuously and retains its local zero-sum sign chart.  Independent
signed row and column permutations, and \(K\mapsto-K\), are isometries of
the finite-polar system, so choose once at \(K_0\) the Case A, B, or C
normal form and retain it locally.

The formulas in the three case notes can then be chosen continuously:

* In Case A, first choose the small positive parameters
  \(\epsilon,\delta\) at \(K_0\) so every scalar and proper inverse pairing,
  and the full-support coefficient \(q(K_0)\), is strictly negative.  Keep
  those parameters fixed locally and recompute
  \(u(K)=D_{g(K)}^{-1}\alpha\) and
  \(n(K)=D_{h(K)}^{-1}\beta\), followed by separate normalization.  The
  zero-sum identities remain exact:
  \(g(K)^Tu(K)=h(K)^Tn(K)=0\).

* In Case B, take its displayed \(\epsilon\) strictly inside its allowed
  interval at \(K_0\), then recompute and normalize the displayed
  \(\alpha,\beta\).  Every proper inverse pairing and every scalar with
  \(j=2,3\) stays strictly negative.  Scalars with \(j=1\) retain
  \(n_j=0\) exactly.  The full limit has the fixed strict gap
  \(1-|g(K)^Tu(K)|^2<1\).

* In Case C, choose the matching pivot and the parameter \(\epsilon\) at
  \(K_0\) with strict table inequalities and strict full gap
  \(|g(K)^Tu(K)|>|h(K)^Tn(K)|\).  These inequalities persist locally.
  Normalize \(u\) to one and \(n\) to one half, as in the Case C proof.

All inverses used in scalar and proper constraints are continuous on this
neighborhood because their entries and two-by-two minors remain nonzero.
The witness norms are one in Cases A and B and one half in Case C.

## 2. Uniform local control of all supports

For any invertible fixed-size block \(B(K)\), and continuous local vectors,

\[
 \begin{aligned}
 &(n_J+tB(K)^Tu_E)^T(I+t^2B(K)^TB(K))^{-1}
 (n_J+tB(K)^Tu_E)-\|u_E\|_2^2\\
 &=\frac{2}{t}u_E^TB(K)^{-T}n_J+O(t^{-2}).
 \end{aligned}
 \tag{5}
\]

The remainder in (5) is uniform after shrinking the neighborhood: every
block inverse is bounded there, and the displayed expression is a rational
function of \(t^{-1}\), the entries of \(B\), \(u\), and \(n\).  Thus a
strictly negative coefficient bounded above by \(-\eta<0\) gives one local
threshold for all such supports.

When \(n_J=0\), no expansion is required.  For any square, including
singular, block \(B\),

\[
 t^2B(I+t^2B^TB)^{-1}B^T\preceq I,
 \tag{6}
\]

so the corresponding polar inequality holds for every \(t\ge0\).  This
covers the Case B \(j=1\) scalars and the Case C supports omitting its
distinguished column.

The full-support treatment has two distinct local mechanisms.

In Case A, the exact zero kernel components in Section 1 must be retained;
they make the limiting full value equal to one, rather than strictly below
it.  Since the positive singular values of \(K\) remain bounded away from
zero locally, the recomputed vectors obey the uniform expansion

\[
 \mathcal P_{[3],[3]}(t;u(K),n(K))-1
 ={2q(K)\over t}+O(t^{-2}),
 \qquad q(K)\le-\eta<0.
 \tag{7}
\]

This supplies the necessary local threshold.  Reusing a fixed witness while
letting \(K\) move would not preserve the two zero-kernel identities, so it
would not justify (7).

In Cases B and C, singular-value decomposition extends the full expression
continuously to \(t^{-1}=0\), with limiting value

\[
 1-|g(K)^Tu(K)|^2+|h(K)^Tn(K)|^2.
 \tag{8}

\]

The constructions have a strict gap below one at \(K_0\), hence on a
smaller neighborhood.  Uniform continuity in \((K,t^{-1})\) then gives a
single local full-support threshold.

The finite set of scalar, proper, and full supports therefore has one
threshold \(T_{K_0}\) on a neighborhood \(U_{K_0}\subset\mathcal G\),
with witnesses varying continuously on that neighborhood.

## 3. Finite cover

The sets \(U_{K_0}\) cover \(F\).  Compactness provides

\[
 F\subset U_{K_1}\cup\cdots\cup U_{K_m}.
 \tag{9}
\]

Set

\[
 T_F=\max_{1\leq a\leq m}T_{K_a}.
 \tag{10}
\]

For \(K\in F\), choose any covering neighborhood containing \(K\) and use
its local witness.  Equations (5)--(8) prove all finite-polar constraints
for every \(t\ge T_F\), proving the theorem.

## Boundary of the statement

This proof is uniform only on compact subsets of \(\mathcal G\).  The
following escape routes prevent this finite-cover argument from extending to
the whole normalized generic stratum:

* an entry tends to zero, so scalar inverse coefficients or a sign chart can
  lose its strict margin;
* a two-by-two minor tends to zero, so a proper-block inverse and the
  uniform remainder in (5) can diverge;
* the second nonzero singular value tends to zero, so rank two approaches
  rank one and the full-support expansion loses its uniform pseudoinverse
  bound.

The result makes no assertion about a common threshold along such moving
directions.  Those boundary regimes can require separate constructions;
for example, a genuine zero column has the independent uniform signed-sum
argument already recorded elsewhere.
