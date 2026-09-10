# Finite resident-codebook lower bridge: proof audit

Status: the finite-codebook theorem below is proved under its stated
source-independent-codebook restriction. It is a worst-case source
construction, not a lower bound for source-trained, source-specific, or
continuously parameterized descriptions. It does not establish a physical
byte or page-read frontier.

Fix positive integers \(t\le p\), \(q\), a rational real matrix
\(R_0\in\mathbb R^{t\times q}\), and

\[
 G=R_0^TR_0\succ0.
\tag{1}
\]

Let \(\mathcal B=\{B_1,\ldots,B_N\}\subset\mathbb C^{p\times q}\) be
the range of a fixed source-independent interpreter on at most \(b\) bits,
with \(N\le2^b\). An encoder may inspect the source and choose its word;
that choice remains covered by this whole finite range.
For each codeword, let

\[
 S_j=\operatorname{span}_{\mathbb R}
 \{\operatorname{Re}(B_j)_{:k},\operatorname{Im}(B_j)_{:k}:1\le k\le q\}
 \subseteq\mathbb R^p.
\tag{2}
\]

Thus \(\dim S_j\le2q\).

## A rational isometry avoiding the whole codebook

Fix \(0<\delta<1\). Suppose

\[
 3\exp\left[b\log2+(t+2q)\log9-{p\delta^2\over64}\right]<1.
\tag{3}
\]

Then there is a real rational isometry \(U\in\mathbb Q^{p\times t}\),
\(U^TU=I_t\), such that

\[
 \|P_{S_j}U\|_{\rm op}<\delta
 \qquad(j=1,\ldots,N).
\tag{4}
\]

For the real-Haar existence step, fix unit vectors \(v\in\mathbb R^t\)
and \(w\in S_j\). The scalar \(w^TUv\) has the law of the first
coordinate of a uniform point on \(\mathbb S^{p-1}\). If \(0<a\le1\),
writing that point as \(g/\|g\|\) for a standard Gaussian gives

\[
 \Pr\{|w^TUv|\ge a\}
 \le2e^{-pa^2/4}+e^{-p/16}
 \le3e^{-pa^2/16}.
\tag{5}
\]

For the first inequality, split according to
\(\|g\|^2\ge p/2\); the one-dimensional Gaussian tail bounds the first
part and the standard chi-square lower-tail Chernoff bound controls the
second. The constants in (5) are deliberately loose.

Take quarter-nets in \(\mathbb S^{t-1}\) and in
\(S_j\cap\mathbb S^{p-1}\). Their cardinalities are at most \(9^t\) and
\(9^{\dim S_j}\), respectively. The standard two-sided operator-net
inequality is

\[
 \|P_{S_j}U\|_{\rm op}
 \le2\max_{v,w\ \mathrm{in\ the\ two\ quarter\text{-}nets}}|w^TUv|.
\tag{6}
\]

It is essential here that the approximation error is bounded by one half of
the *unknown operator norm*, not by an absolute one half: this is why
quarter-nets yield the threshold \(a=\delta/2\). Union bounding (5) at
that threshold over all codewords and net pairs gives exactly the left side
of (3). Hence some real isometry obeys (4), with strict margin.

Rational isometries are dense in the real Stiefel manifold. One direct
route is to approximate an orthogonal extension of the chosen isometry by
rational Cayley transforms of rational skew-symmetric matrices, using a
fixed rational reflection if the other determinant component is needed, and
take its first \(t\) columns. Since the inequalities in (4) are strict and
projection norms vary continuously with \(U\), a sufficiently close rational
isometry retains (4).

## The residual-Gram lower bound

Set

\[
 A=UR_0\in\mathbb Q^{p\times q}.
\tag{7}
\]

For every codeword \(B_j\) and every \(x\in\mathbb C^q\),

\[
 |\langle Ax,B_jx\rangle|
 \le\delta\|Ax\|_2\|B_jx\|_2.
\tag{8}
\]

Indeed, both real and imaginary parts of \(Ax\) lie in \(\operatorname{range}U\),
while those of \(B_jx\) lie in \(S_j\). By (4), the real projection onto
\(\operatorname{range}U\), restricted to \(S_j\), has norm at most
\(\delta\); the same is true after complexification. Project \(B_jx\)
onto that complexified range and apply Cauchy--Schwarz to prove (8).

Completing the square in the two nonnegative norms gives the stronger form

\[
 \begin{aligned}
 \|(A-B_j)x\|_2^2
 &\ge\|Ax\|_2^2+\|B_jx\|_2^2
       -2\delta\|Ax\|_2\|B_jx\|_2\\
 &\ge(1-\delta^2)\|Ax\|_2^2\\
 &=(1-\delta^2)x^*Gx.
 \end{aligned}
\tag{9}
\]

Thus, in particular,

\[
 (A-B_j)^*(A-B_j)\succeq(1-\delta)G
 \qquad(j=1,\ldots,N).
\tag{10}
\]

The weaker constant in (10) is the one needed when the theorem is stated
with a \(1-\delta\) distortion allowance. Equation (9) is the actual
consequence of the angular separation.

## Fixed-linear consequence and its exact scope

Let \(R_j=A-B_j\). For any positive Gram \(H\), let \(t_s(H)\) solve

\[
 \operatorname{tr}\bigl(H(H+t_s(H)I)^{-1}\bigr)=s.
\tag{11}
\]

The global fixed-linear support class, including arbitrary fixed laws over
all supports of size at most \(s\) and retained coefficients depending
linearly on the full query, obeys

\[
 \nu_s(H)\ge t_s(H).
\tag{12}
\]

This is the trace certificate. It therefore already permits global support
allocation and full-query linear coefficients. Since the water level is
Loewner-monotone and positively homogeneous, (10) implies

\[
 \nu_s(R_j^*R_j)
 \ge t_s(R_j^*R_j)
 \ge(1-\delta)t_s(G).
\tag{13}
\]

A free orthogonal or unitary column encoding \(Q\) replaces the residual
Gram by \(Q^*R_j^*R_jQ\), which has the same water level. It cannot evade
(13) within this fixed-linear execution class.

For the repeated equicorrelation family, take rational \(r>0\),
\(\eta=r^2\), and use one rational five-by-four factor

\[
 R_{\rm block}=
 \begin{pmatrix}\mathbf1^T\\rI_4\end{pmatrix},
 \qquad R_{\rm block}^TR_{\rm block}=\mathbf1\mathbf1^T+\eta I_4.
\tag{14}
\]

Its \(m\)-block direct sum has \(t=5m\) and \(q=4m\), so (3) gives an
explicit ambient output dimension sufficient to defeat every fixed
\(b\)-bit codebook in this class.

## Boundaries that the proof does not cross

The source \(A=UR_0\) is chosen *after* the finite interpreter range is
fixed. The result therefore says that no one such finite range uniformly
removes the fixed-linear water benchmark over this constructed source
family. A source-trained encoder, and source-trained decoder parameters,
remain covered when their complete resulting state is included in the
\(b\)-bit word consumed by that one fixed interpreter. The argument fails
only if a source-dependent decoder, decoder state, side information, or
continuous parameter is available without being represented in those
\(b\) bits. In particular, if the class permits the source-specific
reconstruction \(B=A\) without charging its source-dependent payload, its
residual is zero and this construction has no contrary conclusion.

The bit parameter in this theorem counts only a finite choice among the
listed matrices. To use it as a resident-description theorem, one must also
declare how every \(B_j\), its decoder, residual addressing data, sampling
law, precision, and any column transform are represented and charged.
Nothing here converts the abstract support cap into page reads or physical
bytes.

## An exact dyadic Hadamard alternative

The Haar proof establishes existence but does not by itself bound the
arithmetic representation of its rational Stiefel approximation. For a
slightly larger ambient dimension, a Walsh--Hadamard construction gives an
exact dyadic isometry.

Choose \(p=4^k\ge t\), let \(W_p\) be the normalized Walsh--Hadamard
matrix, and let \(V=W_{p,:,1:t}\) be its first \(t\) columns. For a sign
vector \(\epsilon\in\{-1,1\}^p\), set

\[
 U_\epsilon=\operatorname{Diag}(\epsilon)V.
\tag{15}
\]

Every \(U_\epsilon\) is an isometry with entries \(\pm p^{-1/2}=\pm2^{-k}\).
For fixed unit \(x\in\mathbb R^t\) and \(w\in\mathbb R^p\), independent
uniform signs give

\[
 w^TU_\epsilon x=
 \sum_{i=1}^p\epsilon_iw_i(Vx)_i,
 \qquad
 \sum_iw_i^2(Vx)_i^2\le {t\over p}\|w\|_2^2.
\tag{16}
\]

The last inequality follows from
\( |(Vx)_i|\le\sqrt{t/p}\|x\|_2 \). Rademacher Hoeffding therefore gives

\[
 \Pr\{|w^TU_\epsilon x|\ge a\}
 \le2\exp\left(-{pa^2\over2t}\right).
\tag{17}
\]

Use the same quarter-nets and the same multiplicative estimate (6). At
\(a=\delta/2\), union bounding all codewords and net pairs gives an
admissible sign vector whenever

\[
 2\exp\left[
 b\log2+(t+2q)\log9-{p\delta^2\over8t}
 \right]<1.
\tag{18}
\]

The resulting dyadic \(U_\epsilon\) obeys (4), so every conclusion from
(7)--(13) applies without a density argument. Choosing the first power
\(p=4^k\) above the threshold in (18) gives

\[
 p=O\left({t\,[b+t+q]\over\delta^2}\right),
\tag{19}
\]

where the implicit constant includes rounding to the next power of four.
This is weaker in ambient dimension than (3) when \(t\) grows, but it
makes the source factor exactly dyadic.

For the repeated equicorrelation example, take dyadic \(r>0\),
\(\eta=r^2\), and use the block factor in (14). Every column of
\(A=U_\epsilon R_0\) then has entries of the form

\[
 {\pm1\pm r\over\sqrt p}.
\tag{20}
\]

They are dyadic rationals with word length \(O(\log p+\operatorname{word}(r))\).
This controls the arithmetic representation of the adversarially
constructed source matrix. It does not by itself price storage of that
matrix, the sign vector, a codebook matrix, or any decoder in Cassette's
resident-byte model.
