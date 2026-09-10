# A two-scale rank-one-direction escape family has a uniform polar witness

Status: proved for the explicit family below.  This is one surviving
rank-one-direction escape regime from `rank_two_graph_escape_conditions.md`.
It neither treats arbitrary rank-one boundary approaches nor supplies a
counterexample to the finite three-polar lemma.

Let

\[
 e=(1,1,1)^T,\qquad w=(1,-1,0)^T,
 \qquad K_{t,\tau}=t ee^T+\tau ww^T,
 \tag{1}
\]

where \(t\ge1/4\) and \(\lvert\tau\rvert\le t\).  The witness below
works for every such \(\tau\), including \(\tau=0\).  When
\(\tau=\tau_t\ne0\), \(\lvert\tau_t\rvert\to\infty\), and
\(\tau_t/t\to0\), the matrices have rank two, every column norm tends to
infinity, and

\[
 \sigma_2(K_{t,\tau_t})=2\lvert\tau_t\rvert\longrightarrow\infty,
 \qquad
 \frac{K_{t,\tau_t}}{\|K_{t,\tau_t}\|_{\rm op}}
 \longrightarrow\frac{ee^T}{3}.
 \tag{2}
\]

The limiting rank-one matrix has no zero entry.  Nevertheless there is a
fixed finite-polar witness: for every \(t\ge1/4\) and
\(\lvert\tau\rvert\le t\),

\[
 u=-\frac e{\sqrt3},\qquad n=\frac e{2\sqrt3},
 \qquad\|u\|_2=1,\quad\|n\|_2=\frac12,
 \tag{3}
\]

satisfy, for all equal-cardinality \(E,J\subseteq[3]\),

\[
 (n_J+K_{t,\tau,E,J}^Tu_E)^T
 (I+K_{t,\tau,E,J}^TK_{t,\tau,E,J})^{-1}
 (n_J+K_{t,\tau,E,J}^Tu_E)
 \le\|u_E\|_2^2.
 \tag{4}
\]

Thus this family cannot realize the small-ratio escape sought in
`rank_two_graph_escape_conditions.md`.  No coordinate rotation is used;
the witness is written in the original support coordinates.

## The escape conditions hold

The vectors \(e\) and \(w\) are orthogonal.  When \(\tau\ne0\), the
nonzero eigenvalues of the symmetric matrix \(K_{t,\tau}\) are \(3t\)
and \(2\tau\), which proves (2).  Its \(j\)-th column is

\[
 te+\tau w_jw.
 \tag{5}
\]

Under the escape scaling \(\tau_t/t\to0\), all three column norms are
asymptotic to \(\sqrt3t\).  Equation (2) gives the stated rank-one
normalized limit.

## Empty, singleton, and full supports

The empty support condition is void.  For a singleton \(E=\{i\}\),
\(J=\{j\}\), write

\[
 \kappa=(K_{t,\tau})_{ij}=t+\tau w_iw_j.
 \tag{6}
\]

The bound \(\lvert\tau\rvert\le t\) makes \(\kappa\ge0\).  Substitution of (3)
turns the scalar condition into

\[
 \frac{(1/2-\kappa)^2}{3(1+\kappa^2)}\le\frac13,
 \tag{7}
\]

which follows from \(1/4-\kappa\le1\).  Thus every singleton
condition holds.

For full support, both \(u\) and \(n\) lie in the \(e\)-eigenspace.
The left side of (4) is therefore

\[
 \frac{(1/2-3t)^2}{1+9t^2}\le1,
 \tag{8}
\]

again because \(1/4-3t\le1\).  This proves the full condition.

## Proper two-by-two supports

Fix two-element sets \(E,J\).  Put
\(e_E=\mathbf1_E\), and \(w_E=(w_i)_{i\in E}\), with analogous
notation for \(J\).  Then

\[
 B=K_{t,\tau,E,J}=t e_Ee_J^T+\tau w_Ew_J^T.
 \tag{9}
\]

Every pair \((e_E,w_E)\) is a basis of \(\mathbb R^2\): for the three
possible \(E\)'s its determinant is, up to ordering, \(-2,-1,1\).
Thus every matrix in (9) is invertible when \(\tau\ne0\).  Write

\[
 V_E=[e_E\ w_E],\qquad V_J=[e_J\ w_J],
 \qquad B=V_E\begin{pmatrix}t&0\\0&\tau\end{pmatrix}V_J^T.
 \tag{10}
\]

Set \(v=B^{-T}n_J\).  The dominant direction cancels the weak scale
exactly:

\[
 v=\frac1{2\sqrt3t}V_E^{-T}e_1.
 \tag{11}
\]

Indeed, \(n_J=V_Je_1/(2\sqrt3)\), so the \(\tau^{-1}\) coordinate in
\(B^{-T}\) is absent.  For the three possible row sets \(E\), direct
inversion gives

\[
 \|V_E^{-T}e_1\|_2^2\in\left\{\frac12,1,1\right\}.
 \tag{12}
\]

The exact identity

\[
 B(I+B^TB)^{-1}B^T=I-(I+BB^T)^{-1}
 \tag{13}
\]

now makes the polar gap, left side minus \(\|u_E\|_2^2\), equal to

\[
 2u_E^Tv+\|v\|_2^2
 -(u_E+v)^T(I+BB^T)^{-1}(u_E+v).
 \tag{14}
\]

It is at most its first two terms.  Since
\(u_E=-V_Ee_1/\sqrt3\), equations (11)--(12) yield

\[
 2u_E^Tv=-\frac1{3t},
 \qquad
 \|v\|_2^2\le\frac1{12t^2}.
 \tag{15}
\]

Thus every proper two-by-two condition holds whenever \(t\ge1/4\),
independently of the nonzero value of \(\tau\).  At \(\tau=0\), the
original left side in (4) is continuous in the entries of \(B\), so the
same inequality follows by taking \(\tau\to0\).  This proves every
proper condition and completes the proof of (3)--(4).

## What this does and does not discriminate

The family meets all three necessary escape conditions: unbounded columns,
unbounded second singular value, and an all-nonzero rank-one normalized
limit.  It is therefore a direct test of the remaining regime, rather
than a bounded-column or fixed-generic-direction reduction.

The proper-block argument is independent of the weak scale \(\tau\), not
merely of its rate of divergence.  Thus neither the critical scale
\(\lvert\tau\rvert\asymp\sqrt t\) nor a slower nonzero scale produces a
counterexample in this aligned family.  A counterexample, if one exists,
must exploit changing coordinate factor geometry rather than only two
singular values on fixed orthogonal directions.

## Fixed-factor extension

The cancellation in (11) is algebraic.  Here is the corresponding
fixed-factor statement, included to identify its exact scope.

Let \(a,c,b,d\in\mathbb R^3\) satisfy the following conditions:

\[
 [a\ c]\text{ and }[b\ d]\text{ have column rank two};
 \quad a_ib_j\ne0\text{ for all }i,j;
 \tag{16}
\]

and every two-row submatrix of \([a\ c]\) and every two-row submatrix of
\([b\ d]\) is invertible.  Put

\[
 K_{t,\tau}=tab^T+\tau cd^T,
 \qquad
 u=-\frac a{\|a\|_2},\qquad
 n=\frac{b}{2\|b\|_2}.
 \tag{17}
\]

There are constants \(T,\delta>0\), depending only on the four fixed
vectors, such that every \(t\ge T\) and \(0<|\tau|\le\delta t\) obey all
finite three-polar inequalities with this \(u,n\).  The same conclusion
holds at \(\tau=0\) by continuity.

For a proper block, write

\[
 K_{E,J}=V_E\begin{pmatrix}t&0\\0&\tau\end{pmatrix}W_J^T,
 \qquad V_E=[a_E\ c_E],\quad W_J=[b_J\ d_J].
 \tag{18}
\]

If \(v=K_{E,J}^{-T}n_J\), then

\[
 v=\frac1{2\|b\|_2t}V_E^{-T}e_1,
 \qquad
 2u_E^Tv=-\frac1{\|a\|_2\|b\|_2t}.
 \tag{19}
\]

The exact gap identity (14) and the finite family of \(V_E\)'s show that
the negative \(t^{-1}\) term dominates \(\|v\|^2=O(t^{-2})\), uniformly
in nonzero \(\tau\).  The full support has the same proof.  Put
\(V=[a\ c]\) and choose

\[
v=\frac1{2\|b\|_2t}
 V(V^TV)^{-1}e_1,
\tag{20}
\]

so \(K_{t,\tau}^Tv=n\) and again \(2u^Tv=-1/(\|a\|_2\|b\|_2t)\).
The scalar constraints hold for all large \(t\): after multiplication by
their positive denominators, their right-side slack is

\[
 u_i^2-n_j^2-2(K_{t,\tau})_{ij}u_in_j,
 \tag{21}
\]

whose last term is positive of order \(t\) by (16) after choosing
\(\delta\) sufficiently small.  This proves the extension.

The extension does not cover moving factors whose two-row determinants or
nonzero leading coordinates collapse with \(t\).  Those losses can make
the constants hidden in (19) diverge and remain a genuine discriminator
for the general moving graph problem.
