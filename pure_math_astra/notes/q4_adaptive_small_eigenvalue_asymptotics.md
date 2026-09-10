# q=4 query-adaptive small-eigenvalue family — paired-rotation obstruction; depends on query_adaptive_atomic_dual.md, query_adaptive_basis_reversal.md.

Status: partial exact analysis of a hard asymptotic family. This note neither
proves a uniform lower bound nor constructs a basis with a smaller exponent.

Let

\[
 D_\eta=\operatorname {Diag}(1,1,\eta,\eta),\qquad 0<\eta<1,
 \qquad r=\sqrt\eta.
\tag{1}
\]

For `s=2`, its spectral water level is exactly \(t_2(D_\eta)=r\). The
question is whether

\[
 \inf_{Q\in O(4)}\Psi_2(QD_\eta Q^T)
\tag{2}
\]

can be \(o(r)\). The estimator in the definition of \(\Psi_2\) must satisfy
\(\mathbb EY=x\), not merely equality after projection onto the two large
eigendirections.

## 1. A paired rotation and its exact atomic dual constraints

Rotate the coordinate pairs \((1,3)\) and \((2,4)\) through the same angle
\(\theta\). In the reordered coordinates \((1,3,2,4)\), the Gram matrix is

\[
 G_{\eta,\theta}=\operatorname {Diag}(H,H),\qquad
 H=\begin{pmatrix}A&C\\C&B\end{pmatrix},
\tag{3}
\]

where, with \(c=\cos\theta\) and \(s=\sin\theta\),

\[
 A=c^2+\eta s^2,\qquad B=s^2+\eta c^2,
 \qquad C=(1-\eta)cs.
\tag{4}
\]

For a symmetric dual vector \(u=(v,v)\), \(v=(v_H,v_L)\), the dual norm
in equation (6) of `query_adaptive_atomic_dual.md` is exactly

\[
 M_\eta(u)^2=
 \max\left\{
 {2v_H^2\over A},\ {2v_L^2\over B},\
 {v_H^2\over A}+{v_L^2\over B},\ v^TH^{-1}v
 \right\}.
\tag{5}
\]

This follows by listing the six two-coordinate supports. The first two
terms use the same coordinate in the two blocks; the third uses unlike
coordinates in different blocks; and the last uses either whole block.
Singleton supports are dominated by the corresponding first or second
term.

For every such \(u\), atomic duality gives the rigorous lower certificate

\[
 \Psi_2(G_{\eta,\theta})\ \ge\
 \lambda_{\max}\!\left({uu^T\over M_\eta(u)^2}-G_{\eta,\theta}\right).
\tag{6}
\]

Indeed, \(\gamma_{2,G}(x)\ge u^Tx/M_\eta(u)\), then maximize the
resulting quadratic lower bound over unit \(x\).

Equation (5) identifies a real obstruction in the critical scaling
\(\theta=kr\). The diagonal-basis witness, transported through the
rotation, has

\[
 v_0={1\over\sqrt2}(c-rs,\ s+rc).
\tag{7}
\]

It has \(v_0^TH^{-1}v_0=1\), but its repeated-low-coordinate constraint is

\[
 {2(v_0)_L^2\over B}
 ={(k+1)^2\over k^2+1}+o(1)>1\qquad (k>0).
\tag{8}
\]

Thus the witness that proves the water-level lower bound in the eigenbasis
is not dual feasible after a critical paired rotation. This does *not* show
that (2) is \(o(r)\): it only rules out this direct transported-witness
proof of a uniform \(r\)-lower bound.

## 2. Why the singular limit cannot be used as a shortcut

At \(\eta=0\), let \(P_\theta\) denote the rank-two projection in (3).
Write the high coordinate in a block as

\[
 h=cx_H+sx_L.
\tag{9}
\]

Suppose both block values \(h_1,h_2\) are nonzero and an outcome obeys
\(P_\theta Y=P_\theta x\). Its support must contain one coordinate in each
block. In block \(j\), its only possible nonzero value is either
\(h_j/c\) on the high coordinate or \(h_j/s\) on the low coordinate.

Consequently, when \(h_1>0\) and \(x_{H,1}<0\), no probability mixture of
such outcomes can have first coordinate mean \(x_{H,1}\): every one has
that coordinate zero or positive. Hence there is no *zero high-error* law
for this query.

This fact is deliberately weaker than a positive lower bound for the
singular problem. Coefficients along
\((-s,c)\in\ker P_\theta\) can diverge while retaining a prescribed mean.
An argument that replaces \(\mathbb EY=x\) by \(P_\theta\mathbb EY=P_\theta x\)
would erase precisely this escape route and is invalid.

## 3. The exact high/null trade-off that remains to be controlled

The escape route has a concrete cost after restoring \(\eta>0\). Take a
query with the same bad sign pattern in both blocks, and set

\[
 d_j=-{a\over c}(-s,c)\quad\text{in block }j,
\tag{10}
\]

so that the low coordinate of \(x-d_1-d_2\) is zero in both blocks. The
vector \(d_j\) lies in \(\ker P_\theta\), has norm comparable to \(|a|\)
for small \(\theta\), and needs both coordinates of its block.

Any correction architecture that uses a total probability \(p\) on the
two block-supported null corrections and otherwise returns a two-high-
coordinate vector has the exact orders

\[
 \mathbb E\|P_\theta(Y-x)\|_2^2=\Theta(p),\qquad
 \eta\,\mathbb E\|(I-P_\theta)(Y-x)\|_2^2=\Theta(\eta/p).
\tag{11}
\]

For example, use the two null corrections with probabilities \(p/2,p/2\),
scaled by \(2/p\), and put the remaining mean into the high-coordinate
outcome, scaled by \(1/(1-p)\). Every outcome has at most two nonzero
coordinates. The two terms in (11) are obtained by direct expansion; the
first is the variance of the high projection between the zero-projection
corrections and the rescaled main outcome, while the second includes
\((p/2)(2\|d_j\|/p)^2\).

Minimizing this displayed trade-off yields order \(r\), not a smaller
order. It explains why a singular-limit construction alone cannot prove an
exponent improvement.

It is not a lower bound for arbitrary query-dependent laws. Such a law can
mix supports that do not preserve the high projection, so proving (2)
requires a coercive statement that reduces every law for at least one query
to a trade-off of the form (11), up to fixed constants.

## 4. Precise unresolved obstruction

A sufficient statement for a uniform lower bound within the paired family
is the following.

> **Paired coercivity lemma.** There are \(c_0,\theta_0>0\) such that, for
> \(0<\theta<\theta_0\), every two-sparse unbiased law for one of a fixed
> finite set of unit bad-sign queries obeys
> \[
> \mathbb E (Y-x)^TG_{\eta,\theta}(Y-x)\ge c_0\sqrt\eta
> \quad\text{for all sufficiently small }\eta.
> \]

The atom list in (5) makes this a finite convex-analytic inequality, but I
do not yet have a proof. Establishing it would prove the requested
\(c\sqrt\eta\) lower bound for this structured family. Refuting it by an
explicit coefficient-and-law construction with risk \(o(r)\), uniformly
over all unit queries, would instead settle the exponent question in the
opposite direction.

## 5. A separate critical-scale route for coupled rotations

This section records an unproved leading-order reduction. It is a route to
the paired coercivity lemma, not evidence for either outcome.

For a general coupled high/low rotation at scale \(r\), write its leading
Gram matrix in high/low block coordinates as

\[
 G_r=
 \begin{pmatrix}
 I+O(r^2)&rK+O(r^3)\\
 rK^T+O(r^3)&r^2(I+K^TK)+O(r^4)
 \end{pmatrix},
\tag{12}
\]

where \(K\) is a fixed real \(2\times2\) matrix. For a query
\(x=(u,v)\), a putative leading construction retains both high coordinates
on most outcomes. A rare event of probability \(r\alpha\), replacing high
coordinate \(m\) by low coordinate \(j\) with coefficient \(z/r\),
contributes low-mean amount \(w=\alpha z\). Its order-\(r\) cost is

\[
 \alpha\bigl((K_{mj}z-u_m)^2+z^2\bigr).
\tag{13}
\]

At fixed \(w\), minimizing the displayed expression over positive
\(\alpha\) gives

\[
 2|u_mw|\sqrt{1+K_{mj}^2}-2u_mK_{mj}w.
\tag{14}
\]

Similarly, an event replacing both high coordinates by two low coordinates
and carrying low-mean vector \(w\) has candidate cost

\[
 2\|u\|_2\sqrt{w^T(I+K^TK)w}-2u^TKw.
\tag{15}
\]

If one proves compactness of near-optimal laws at this scale and validates
the decomposition into these event types, their infimal convolution would
be the leading query cost divided by \(r\). Its candidate polar condition
for a dual low vector \(n\) is

\[
 |n_j+u_mK_{mj}|\le |u_m|\sqrt{1+K_{mj}^2}\quad(m,j=1,2),
 \qquad
 \|(I+K^TK)^{-1/2}(n+K^Tu)\|_2\le\|u\|_2.
\tag{16}
\]

Showing that some high vector \(u\) forces this polar body to contain a
dual vector of norm at least \(\|u\|_2\) would give a leading-order
\(\sqrt\eta\) obstruction. Conversely, an explicit valid limiting
decomposition for every \((u,v)\) with a smaller worst coefficient would
give a controlled counterexample. Neither implication has been proved
here.
