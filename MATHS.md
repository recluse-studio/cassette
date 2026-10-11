# MATHS.md — Cassette mathematical authority

Recorded 2026-08-09, after S11 and before S12. This file is the mathematical authority for every
future compiler, plan, pager, and compiled-training decision. `ORIGINAL_REMIT.md` remains the intent
authority, `research/RESEARCH.md` remains the build-decision ledger, and
`research/ACCEPTANCE_MATRIX.yaml` remains the release authority. Where an older document assumes a
prompt-fixed working set, a top-`k` selector, or a trained router as the general compiled form, this
file supersedes that assumption.

The result is not one approximation formula. Cassette has four distinct mathematical problems:

1. determine which declared conditions one bounded representation can serve;
2. determine how many such representations, or atoms, are required;
3. determine how a chosen atom can be executed within resident-byte and fresh-I/O bounds; and
4. determine whether those one-step guarantees survive a trace and the observation available at
   selection time.

Collapsing these problems produced the old foundation. Separating them is the material improvement.

## Status language

Every statement in this file has one status.

- **PROVED HERE** means the proof appears here and uses only the declared definitions.
- **KNOWN** means a cited theorem supplies the result.
- **CONDITIONAL** means the result is proved under hypotheses that must appear in any consuming
  plan.
- **OPEN** means Cassette may measure or investigate the question but may not assume an answer.
- **REJECTED** means a prior claim has a counterexample or lacks the model needed to be a theorem.

No empirical result, numerical search, or test harness is evidence for the pure claims below.

## 1. Ambient model

Fix a field \(\mathbb F\in\{\mathbb R,\mathbb C\}\), a declared tensor flattening

\[
\mathcal H=\mathbb F^{p\times q},
\]

and a target \(T\in\mathcal H\). Rank always means matrix rank in this declared flattening. A
different flattening is a different mathematical model and must receive a different certificate.

Let \(V\) be a finite declared condition set. A condition may denote a workload stratum, a trace
state, a modality state, or another exact source of local relevance, but its meaning and provenance
must be fixed before a certificate is evaluated. Each \(v\in V\) carries a symmetric positive-
definite form over \(\mathbb R\), or a Hermitian positive-definite form over \(\mathbb C\), denoted
by \(C_v\succ0\):

\[
\langle X,Y\rangle_{C_v}
=\operatorname{vec}(X)^*C_v\operatorname{vec}(Y),
\qquad
\|X\|_{C_v}^2=\langle X,X\rangle_{C_v}.
\]

For nonzero \(A\), let \([A]\) denote its projective class and define the condition loss

\[
\ell_v([A])
=\inf_{c\in\mathbb F}\|T-cA\|_{C_v}^2
=\|T\|_{C_v}^2-
\frac{|\langle A,T\rangle_{C_v}|^2}{\|A\|_{C_v}^2}.
\]

The scalar removes an irrelevant global scale for that condition. It does not permit a different
matrix, rank, or tensor flattening.

For tolerance \(\eta\ge0\) and rank budget \(r\ge1\), define

\[
K_{\eta,r}
=\left\{
S\subseteq V:
\exists A\ne0,
\ \operatorname{rank}(A)\le r,
\ \ell_v([A])\le\eta\ \text{for every }v\in S
\right\}.
\]

### Proposition 1 — compatibility is a bifiltration

**Status: PROVED HERE.**

Each \(K_{\eta,r}\) is an abstract simplicial complex. Moreover,

\[
\eta\le\eta',\quad r\le r'
\quad\Longrightarrow\quad
K_{\eta,r}\subseteq K_{\eta',r'}.
\]

**Proof.** A witness for \(S\) is also a witness for every subset of \(S\). Increasing either
budget preserves every existing witness. \(\square\)

This is the first correction to the old foundation. Pairwise compatibility is not enough. A family
may have every pair compatible while its triple is not. The 1-skeleton, the pairwise feasibility
relation, and any invariant determined only by pairwise data therefore fail to determine the full
complex.

One boundary is immediate. If every \(C_v\) is positive definite and \(\eta=0\), then
\(\ell_v([A])=0\) implies \(T=cA\). The condition label disappears. Nontrivial condition geometry
therefore requires positive tolerance or deliberately semidefinite observation forms. Cassette uses
positive tolerance; it may not present a zero-tolerance positive-definite model as condition
sensitive.

## 2. Atom capacity

An atom is one projective rank-\(\le r\) witness. Its service face is

\[
F_A=\{v\in V:\ell_v([A])\le\eta\}\in K_{\eta,r}.
\]

Let

\[
a_{\min}(K)
=\min\left\{a:
V=F_1\cup\cdots\cup F_a,
\ F_i\in K
\right\}.
\]

Set the minimum of the empty set to \(+\infty\). This number is the least atom count needed to serve
every declared condition at fixed \((\eta,r)\).

Let \(H_K\) be the hypergraph on \(V\) whose hyperedges are the minimal nonfaces of \(K\). A weak
proper coloring of a hypergraph is a coloring with no monochromatic hyperedge. Define its weak
chromatic number as \(+\infty\) when a singleton is a hyperedge.

### Theorem 2 — atom count is weak hypergraph chromatic number

**Status: PROVED HERE.**

\[
a_{\min}(K)=\chi_{\mathrm w}(H_K).
\]

**Proof.** If a singleton is a nonface, neither a face cover nor a weak proper coloring exists, so
both sides are \(+\infty\). Otherwise, given a face cover, assign each vertex to one covering face.
The resulting color classes are subsets of faces and are therefore faces. No class contains a
minimal nonface, so the coloring is weakly proper. Conversely, every color class in a weakly proper
coloring is a face: if it were a nonface, it would contain a minimal nonface. The color classes
cover \(V\). \(\square\)

This theorem prices atom count only. It does not price resident bytes, metadata, fresh reads,
selection information, or sequential reuse. Those resources enter later and must not be hidden
inside the word “rank.”

## 3. Arbitrary higher-order obstructions occur

The following theorem explains why Cassette cannot replace the compatibility complex with its
1-skeleton, which records only pairwise feasibility, or with an invariant constant on the declared
projection-commuting ambient-unitary orbit.

### Theorem 3 — universal rank-one compatibility in one Hilbert orbit

**Status: PROVED HERE.**

Let \(n\ge2\), and let \(K\) be any finite simplicial complex on \(V=[n]\) that contains every
singleton. The case \(n=1\) is the immediate construction
\(T=[1],P_1=I,C_1=(1+\delta)I\). Set

\[
N=\sum_{\substack{F\subseteq V\\|F|\ge2}}|F|
=n(2^{n-1}-1).
\]

There exist a target \(T_K\in\mathbb F^{N\times N}\), mutually orthogonal coordinate projections
\(P_1,\ldots,P_n\) on the matrix Hilbert space, and constants \(\delta>0\) and \(\eta>0\) depending
only on \(n\), such that

\[
C_v=P_v+\delta I
\qquad\text{and}\qquad
K_{\eta,1}=K.
\]

For fixed \(n\), every tuple \((T_K,C_1,\ldots,C_n)\) lies in one orbit under block-unitary
operators on the ambient matrix Hilbert space that fix every \(P_v\), hence every \(C_v\). These
ambient unitaries do not generally preserve matrix rank.

#### Construction

Order the subsets \(F\subseteq V\), \(|F|\ge2\), lexicographically and place one \(|F|\times|F|\)
block for each subset along the diagonal of \(\mathbb F^{N\times N}\). All entries outside these
blocks, and all unassigned entries inside them, are zero in \(T_K\). Write
\(F=\{v_1<\cdots<v_s\}\). In its block, assign condition \(v_i\) the two coordinates

\[
(i,i),\qquad(i+1,i),
\]

where row indices are cyclic. Put target value \(1\) at \((i,i)\) and a unit-modulus gain
\(g_{F,i}\) at \((i+1,i)\). Use the canonical gains

\[
(g_{F,1},\ldots,g_{F,s})
=
\begin{cases}
(1,\ldots,1,-1),&F\text{ is a minimal nonface of }K,\\
(1,\ldots,1),&\text{otherwise}.
\end{cases}
\]

Thus the cycle gain is \(-1\) precisely for a minimal nonface and \(1\) otherwise, over either
declared field. Let \(P_v\) project onto all coordinates assigned to \(v\) over all blocks. These
coordinate sets are disjoint, so the \(P_v\) are mutually orthogonal.

#### Exact compatibility

Suppose \(A=xy^*\) and condition \(v_i\) matches its two target coordinates in one block, up to its
allowed scalar \(c_i\). Dividing the two nonzero equalities gives

\[
\frac{x_{i+1}}{x_i}=g_{F,i}.
\]

If every vertex of the block is selected, multiplication around the cycle requires
\(\prod_i g_{F,i}=1\). A minimal-nonface block violates that requirement.

If \(S\in K\), then no minimal-nonface block is selected in full. Every selected part of an
unbalanced cycle is a disjoint union of paths, and every balanced complete cycle is consistent.
The row and column coordinates of different blocks are independent, so these path solutions
assemble into one global rank-one matrix. Thus the exact coordinate observations realize precisely
the faces of \(K\).

#### Positive-definite metrics and one threshold

Write the selected-coordinate loss as

\[
\ell_v^{(0)}([A])
=\inf_{c\in\mathbb F}\|P_v(T_K-cA)\|_F^2.
\]

For \(\mathbb E\in\{\mathbb R,\mathbb C\}\) and \(2\le s\le n\), put
\(g^{(s)}=(1,\ldots,1,-1)\), use cyclic indices, and define

\[
d_{\mathbb E,s}=
\inf_{z\in\mathbb E^s\setminus\{0\}}
\max_{1\le i\le s}
\inf_{\alpha_i\in\mathbb E}
\left(
|1-\alpha_i z_i|^2+
|g_i^{(s)}-\alpha_i z_{i+1}|^2
\right).
\]

Each \(d_{\mathbb E,s}\) is positive. If one were zero, there would be sequences \(z^{(m)}\) and
\(\alpha_i^{(m)}\) for which every displayed pair of residuals tends to zero. Then every
\(z_i^{(m)}\) is eventually nonzero and

\[
\frac{z_{i+1}^{(m)}}{z_i^{(m)}}\longrightarrow g_i^{(s)}.
\]

The product of the left-hand ratios is exactly \(1\), while the product of their limits is \(-1\),
a contradiction. Hence

\[
d_n=\min_{\substack{\mathbb E\in\{\mathbb R,\mathbb C\}\\2\le s\le n}}
d_{\mathbb E,s}>0.
\]

For a global rank-one matrix \(A=xy^*\), restriction to column \(i\) of an unbalanced block and
the condition scalar combine into some \(\alpha_i\). The block formula therefore forces at least
one selected condition to have \(\ell_v^{(0)}([A])\ge d_{\mathbb F,s}\ge d_n\). If every row
factor in that block is zero, each two-coordinate loss is \(2\), while
\(d_{\mathbb F,s}\le2\) by taking every \(\alpha_i=0\), so the same conclusion holds.

Now take a face \(S\in K\). Set every selected condition scalar to \(1\). Inside each block, the
selected edges form disjoint paths, unless they form a complete balanced cycle. Assign a unit-
modulus starting value to each path and propagate the canonical gains; assign the corresponding
column factors so that every selected pair equals its target pair, and assign every unconstrained
factor any unit-modulus value. The independent block factors assemble into global vectors \(x,y\)
with unit-modulus coordinates. Thus \(A_S=xy^*\) matches every
selected \(P_vT_K\) exactly. Since \(T_K\) has \(2N\) unit-modulus entries and \(A_S\) has
\(N^2\) unit-modulus entries, the uniform bound

\[
\|T_K-A_S\|_F^2\le B_n,
\qquad
B_n=\left(\sqrt{2N}+N\right)^2
\]

holds for every complex \(K\), face \(S\), and selected condition. Choose, once for this \(n\),

\[
\delta=\frac{d_n}{4B_n},
\qquad
\eta=\frac{d_n}{2}.
\]

For every scalar \(c\),

\[
\|T_K-cA\|_{C_v}^2
=\|P_v(T_K-cA)\|_F^2+\delta\|T_K-cA\|_F^2,
\]

so \(C_v\)-loss is at least \(\ell_v^{(0)}\). Every face has \(C_v\)-loss at most
\(\delta B_n<\eta\). Every nonface contains a minimal
nonface, whose canonical block forces one condition's \(\ell_v^{(0)}\), and therefore its
\(C_v\)-loss, to be at least \(d_n>\eta\). If \(K\) is the full simplex, the face construction
supplies its global rank-one witness and the nonface clause is vacuous. This proves
\(K_{\eta,1}=K\) with constants that depend only on \(n\).

#### One ambient orbit

For each \(v\), the vector \(P_vT_K\) contains the same number of unit-modulus coordinates for
every \(K\), hence has the same norm. A unitary on each \(\operatorname{ran}P_v\) maps
\(P_vT_K\) to \(P_vT_L\). Their direct sum, extended by the identity on the unassigned coordinate
complement, commutes with every \(P_v\) and maps \(T_K\) to \(T_L\).
\(\square\)

The conclusion is exact and limited. Any invariant of \((T,C_1,\ldots,C_n)\) under ambient
unitaries that commute with every \(P_v\) is identical across these examples, yet their rank-one
compatibility complexes differ. The coordinate-labelled determinantal embedding detects the
difference. The theorem does not say that production workloads realize every complex, that \(N\)
is minimal, or that ambient unitaries are legal tensor transformations.

## 4. The whitening boundary

A tempting reduction is to whiten each condition metric and apply ordinary SVD. Whitening is exact
for the norm, but a generic whitening changes matrix rank.

### Theorem 4 — exact rank-preserving whitening is product-form

**Status: KNOWN, with the metric consequence proved here.**

Let \(W:\mathbb F^{p\times q}\to\mathbb F^{p\times q}\) be an invertible \(\mathbb F\)-linear map
that preserves the nonzero rank-one variety in both directions. When \(p,q\ge2\), Westwick's onto
decomposable-tensor preserver theorem gives

\[
W(A)=PAQ,
\]

or, when \(p=q\),

\[
W(A)=PA^{\mathsf T}Q,
\]

for invertible \(P,Q\). The second form occurs only when the two tensor factors have equal
dimension. This is the classical linear rank-preserver classification for a two-factor tensor
space. If \(p=1\), every linear map on row vectors is right multiplication by one \(Q\); if
\(q=1\), every linear map on column vectors is left multiplication by one \(P\). Thus the same
first form covers the one-dimensional-factor cases directly.

An exact linear whitening of a positive-definite form \(C\) is an invertible linear map satisfying

\[
\|W(A)\|_F^2=\langle A,A\rangle_C
\qquad\text{for every }A.
\]

Such a whitening preserves every matrix-rank constraint if and only if, up to the square transpose
identification,

\[
C=R^{\mathsf T}\otimes L,
\qquad L\succ0,\ R\succ0.
\]

Indeed,

\[
\|PAQ\|_F^2
=\operatorname{vec}(A)^*
\left((QQ^*)^{\mathsf T}\otimes P^*P\right)
\operatorname{vec}(A).
\]

Conversely, square roots of \(L\) and \(R\) construct such a whitening.

Generic \(C_v\) therefore cannot be whitened without changing the determinantal variety. Even when
every \(C_v\) is product-form, the family need not share one whitening. “Whiten, then truncate” is
an exact special case, not Cassette's general foundation.

## 5. Description and fresh-probe execution

The previous sections decide which atoms can serve which conditions. They do not decide how to
execute a chosen atom. Claude's loop supplied one useful result here, after its claimed converse and
universality are removed.

Fix a nonzero atom \(A\in\mathbb F^{p\times q}\). Let a resident description reconstruct
\(B\), and let \(R=A-B\). If \(R=0\), exact execution needs no residual samples. Otherwise define
the query-independent sampling law

\[
\pi_j=\frac{\|R_{:j}\|_2^2}{\|R\|_F^2}
\]

on \(J_R=\{j:R_{:j}\ne0\}\). For fresh independent samples \(I_1,\ldots,I_s\), where
\(s\in\mathbb N_{\ge1}\), set

\[
Y(x)
=Bx+\frac1s\sum_{k=1}^s
\frac{R_{:I_k}x_{I_k}}{\pi_{I_k}}.
\]

### Theorem 5 — fresh residual-sampling upper bound

**Status: PROVED HERE.**

For every fixed query \(x\),

\[
\mathbb E[Y(x)]=Ax
\]

and

\[
\mathbb E\|Y(x)-Ax\|_2^2
\le
\frac{\|A-B\|_F^2}{s}\|x\|_2^2.
\]

**Proof.** One sampled correction is unbiased. Its second moment is

\[
\sum_{j\in J_R} \pi_j
\frac{\|R_{:j}\|_2^2|x_j|^2}{\pi_j^2}
=\|R\|_F^2\sum_{j\in J_R}|x_j|^2
\le\|R\|_F^2\|x\|_2^2.
\]

The variance of the average of independent centered corrections is \(1/s\) times the single-sample
variance, which is no greater than that second moment. \(\square\)

Let \(\mathcal C_{b_{\rm desc},b_{\rm meta}}(A)\) be a nonempty declared class in which the payload
needed to reconstruct \(B\) fits in \(b_{\rm desc}\) resident bytes and the exact residual-addressing
and sampling metadata fits in \(b_{\rm meta}\) resident bytes. Define the individual-matrix
description-distortion curve

\[
D_A(b_{\rm desc},b_{\rm meta})
=\inf_{B\in\mathcal C_{b_{\rm desc},b_{\rm meta}}(A)}\|A-B\|_F^2.
\]

This is not Shannon rate-distortion: no source distribution, code ensemble, or converse has been
specified.

For a declared \(B\in\mathcal C_{b_{\rm desc},b_{\rm meta}}(A)\) and
\(\varepsilon_{\rm exec}>0\), mean-square Frobenius-relative execution error

\[
\mathbb E\|Y(x)-Ax\|_2^2
\le\varepsilon_{\rm exec}^2\|A\|_F^2\|x\|_2^2,
\]

is guaranteed when

\[
s\ge
\left\lceil
\frac{\|A-B\|_F^2}{\varepsilon_{\rm exec}^2\|A\|_F^2}
\right\rceil.
\]

For \(0<\delta_{\rm exec}<1\), consider the high-probability guarantee

\[
\Pr\!\left[
\|Y(x)-Ax\|_2>
\varepsilon_{\rm exec}\|A\|_F\|x\|_2
\right]\le\delta_{\rm exec},
\]

Markov's inequality gives the sufficient, not necessary, condition

\[
s\ge
\left\lceil
\frac{\|A-B\|_F^2}{
\delta_{\rm exec}\varepsilon_{\rm exec}^2\|A\|_F^2}
\right\rceil.
\]

If \(\mathcal C_{b_{\rm desc},b_{\rm meta}}(A)\) attains its infimum, \(\|A-B\|_F^2\) may be
replaced by \(D_A(b_{\rm desc},b_{\rm meta})\). Without attainment, for every \(\gamma>0\) there
is a description with residual at most \(D_A(b_{\rm desc},b_{\rm meta})+\gamma\), and the two
sufficient bounds use that quantity. The infimum alone never names an executable description.

If a sampled residual column costs \(p\) scalar reads, then \(t_{\rm fresh}=ps\). A real plan must
replace scalar reads with encoded bytes, read grouping, alignment, and the measured storage profile.

For a nonzero query with
\(Z(x)=\sum_j |x_j|\|R_{:j}\|_2>0\), Claude's query-dependent law

\[
\pi_j=\frac{|x_j|\|R_{:j}\|_2}{Z(x)}
\]

on the support where the numerator is nonzero minimizes the one-sample second moment among
coordinate-sampling laws. Cauchy--Schwarz gives

\[
\sum_{j:|x_j|\|R_{:j}\|_2>0}
\frac{\|R_{:j}\|_2^2|x_j|^2}{\pi_j}\ge Z(x)^2,
\]

with equality for this law, and \(Z(x)^2\le\|R\|_F^2\|x\|_2^2\). If \(Z(x)=0\), then \(Rx=0\)
and no residual sample is required. Query-dependent sampling needs per-query normalization and a
different metadata and scheduling account.

### Corollary 5.1 — a spectral head is one description class

**Status: KNOWN.**

For \(0\le k\le\min(p,q)\), truncated SVD minimizes \(\|A-B\|_F\) among reconstructions of
rank at most \(k\). A dense spectral
description costs approximately \(k(p+q+1)\) scalars before its residual-norm table. It need not
minimize distortion at a fixed byte budget across sparse, block, quantized, shared, or learned
description classes. Rank is not storage.

### Lemma 5.2 — Frobenius-basis action identity

**Status: PROVED HERE.**

For every Frobenius-orthonormal basis \(\{E_\alpha\}_{\alpha=1}^{pq}\) of
\(\mathbb F^{p\times q}\) and every \(x\in\mathbb F^q\),

\[
\sum_{\alpha=1}^{pq}\|E_\alpha x\|_2^2=p\|x\|_2^2.
\]

**Proof.** For the standard matrix-unit basis,
\(\sum_\alpha E_\alpha^*E_\alpha=pI_q\). An orthogonal or unitary change of Frobenius basis leaves
this sum unchanged. Multiplication on both sides by \(x^*\) and \(x\) gives the identity.
\(\square\)

The identity concerns complete orthonormal linear encodings. It does not lower-bound arbitrary
descriptions, preprocessing, or adaptive probes.

### Proposition 5.3 — unbounded-description endpoint

**Status: PROVED HERE.**

For \(0<\varepsilon<1\), let \(\mathcal N\) be an \(\varepsilon\)-net of the unit sphere of
\(\mathbb F^q\). A net exists with at most \((1+2/\varepsilon)^{d_{\mathbb F}q}\) points, where
\(d_{\mathbb R}=1\) and \(d_{\mathbb C}=2\). Store \(A\hat x\) for every \(\hat x\in\mathcal N\).
For a nonzero query \(x\), choose \(\hat x\) within \(\varepsilon\) of \(x/\|x\|_2\) and return
\(\|x\|_2A\hat x\). Then

\[
\|Ax-\|x\|_2A\hat x\|_2
\le\varepsilon\|A\|_2\|x\|_2
\le\varepsilon\|A\|_F\|x\|_2.
\]

**Proof.** Take a maximal \(\varepsilon\)-separated subset of the sphere, regarded in real dimension
\(d_{\mathbb F}q\). Maximality makes it a net. The disjoint radius-\(\varepsilon/2\) balls around
its points lie in the radius-\(1+\varepsilon/2\) ball, so volume comparison gives the stated
cardinality. The displayed error bound then follows from the operator-norm inequality. \(\square\)

The query reads \(p\) stored output scalars, but the description uses at most
\(p(1+2/\varepsilon)^{d_{\mathbb F}q}\) scalars and assumes that nearest-net lookup is free. This
endpoint proves that description size and fresh access form a trade-off. It says nothing about a
practical description class.

### Theorem 5.4 — restricted dictionary-subspace covering bound

**Status: CONDITIONAL.**

Let \(f_1,\ldots,f_D\in\mathbb F^q\) be fixed dictionary vectors, let
\(1\le k\le\min(D,q-1)\), and require every deterministic returned approximation to lie in the span
of at most \(k\) dictionary vectors. If every unit \(x\in\mathbb F^q\) is within
\(0<\varepsilon\le1/2\) of some permitted span, then

\[
1\le
\binom Dk C_{\mathbb F,q,k}\varepsilon^{d_{\mathbb F}(q-k)}
\]

for a finite constant \(C_{\mathbb F,q,k}\) independent of \(D\) and \(\varepsilon\). Consequently,

\[
k\log\frac{eD}{k}
\ge
d_{\mathbb F}(q-k)\log\frac1\varepsilon
-\log C_{\mathbb F,q,k}.
\]

**Proof.** The permitted outputs lie in the union of at most \(\binom Dk\) subspaces of
\(\mathbb F\)-dimension at most \(k\). Represent a uniform sphere point as \(G/\|G\|_2\), where
\(G\) has independent standard real or circular complex Gaussian coordinates. The squared norms
of its projections onto a fixed \(k\)-dimensional subspace and its orthogonal complement are
independent gamma variables with common scale and respective shape parameters \(b\) and \(a\).
Their normalized ratio shows that squared distance to the subspace has the beta law with
parameters

\[
a=\frac{d_{\mathbb F}(q-k)}2,
\qquad
b=\frac{d_{\mathbb F}k}2.
\]

Integrating its density from \(0\) to \(\varepsilon^2\) bounds the tube measure by
\(C_{\mathbb F,q,k}\varepsilon^{d_{\mathbb F}(q-k)}\), for example with
\(C_{\mathbb F,q,k}=\max\{1,(3/4)^{b-1}\}/(a\,\mathrm B(a,b))\). The union must cover the sphere.
Apply the union bound and \(\binom Dk\le(eD/k)^k\). \(\square\)

If a scheme observes all \(p\) row coordinates against each of \(k\) deterministically selected
dictionary vectors, so that \(t=pk\), then product measurements \(e_i f_\beta^*\) satisfy this
union-of-subspaces model only when query reconstruction is required to use a combination in the
span of those selected vectors. Product cells alone do not impose that rule.
General linear cells, nonlinear descriptions, unrestricted preprocessing, and randomized execution
do not satisfy the premise. Cassette may use the bound only when a plan declares the restricted
model.

## 6. Sequential execution is graded

A one-step complex does not determine a multi-layer or multi-token computation. Products, sums,
residual reuse, mutation, and re-encoding have different rank and error laws.

For horizon \(h\), let \(\mathcal P_h\) be a finite protected trace family, let
\(\mathbf u^{(h)}\) be its declared resource budget, and assume that at least one declared legal
schedule, normally the idle schedule, lies within \(\mathbf u^{(h)}\). If none does, the certificate
is infeasible and no trace complex is issued. Define

\[
\mathscr K_h(\mathbf u^{(h)})
=
\left\{
S\subseteq\mathcal P_h:
\text{one shared schedule serves every }\tau\in S
\text{ within }\mathbf u^{(h)}
\right\}.
\]

This collection is an abstract simplicial complex on protected traces. A prefix map is not
automatic. Suppose that every length-\(j\) prefix of a trace in \(\mathcal P_h\) belongs to
\(\mathcal P_j\), every legal schedule remains legal when restricted to a prefix, and the restricted
resource use satisfies \(\mathbf u^{(j)}\). Only under these coherence hypotheses does

\[
\rho_{h\to j}(S)
=\{\tau_{1:j}:\tau\in S\}
\in\mathscr K_j(\mathbf u^{(j)}),
\qquad j\le h.
\]

Every operation \(\Phi\) must declare its own rank-accounting map and loss-propagation bound. No
universal composition rule is assumed.

### Lemma 6 — conditional quadrature allocation

**Status: CONDITIONAL.**

Let the layer index set be finite, let \(a_\ell,c_\ell>0\), and suppose the linearized layer errors
are centered and independent while the Jacobians \(J_\ell\) are fixed. Suppose

\[
\mathbb E\|J_\ell e_\ell\|^2\le c_\ell^2\delta_\ell^2.
\]

Then the linearized sum satisfies

\[
\mathbb E\left\|\sum_\ell J_\ell e_\ell\right\|^2
\le\sum_\ell c_\ell^2\delta_\ell^2.
\]

Let the nonlinear remainder have root-mean-square norm at most \(\varepsilon_{\rm rem}\), fix a
total root-mean-square target \(\varepsilon>\varepsilon_{\rm rem}\), and set
\(\varepsilon_{\rm lin}=\varepsilon-\varepsilon_{\rm rem}\). Minkowski's inequality shows that it
is sufficient to give the linearized sum budget \(\varepsilon_{\rm lin}\). If layer \(\ell\) costs
\(a_\ell\delta_\ell^{-2}\), then

\[
\min_{\delta_\ell>0}
\left\{
\sum_\ell\frac{a_\ell}{\delta_\ell^2}:
\sum_\ell c_\ell^2\delta_\ell^2\le\varepsilon_{\rm lin}^2
\right\}
=
\frac{\left(\sum_\ell c_\ell\sqrt{a_\ell}\right)^2}
{\varepsilon_{\rm lin}^2}.
\]

Lagrange multipliers give

\[
\delta_\ell^2
=
\frac{\varepsilon_{\rm lin}^2\sqrt{a_\ell}}
{c_\ell\sum_j c_j\sqrt{a_j}},
\qquad
\frac{a_\ell}{\delta_\ell^2}\propto c_\ell\sqrt{a_\ell}.
\]

Without centering, independence or another orthogonality proof, fixed linearization, and a declared
remainder bound, this formula is not a composition theorem.

## 7. Observation adequacy

An atom selector sees an observation, not the latent task state. Training success on observed
prompts does not establish behavior off that support.

Represent a prompt, source packet, or compiler view as a statistical experiment \(E\) from a
finite latent-condition space to a finite observation space. The experiment \(E'\) Blackwell-
dominates \(E\) when

\[
E=G\circ E'
\]

for some stochastic garbling \(G\). The finite Blackwell comparison theorem says this is equivalent
to \(E'\) having no worse Bayes risk for every prior on the latent space, every finite action set,
and every bounded loss function.

Cassette need not prove universal Blackwell dominance. A certificate must instead declare one of:

- the protected decision family and losses for which dominance is proved; or
- the protected test law, its support, selector, sample count, confidence rule, and exact
  off-support rejection behavior.

Nominal source identity, prompt similarity, and high average quality establish none of these.

## 8. The resource certificate

A compiled plan is mathematically admissible only when it records

\[
\mathfrak R(\pi)=
\bigl(
\eta_{\rm rep},
\varepsilon_{\rm exec},
\delta_{\rm exec}^{\rm total};
a,r;
b_{\rm desc}^{\rm peak},b_{\rm desc}^{\rm total},
b_{\rm meta}^{\rm peak},b_{\rm meta}^{\rm total};
s^{\max},s^{\rm total},
t_{\rm fresh}^{\max},t_{\rm fresh}^{\rm total};
h
\bigr)
\]

against one immutable target, flattening, condition family, metric family, protected trace family,
and observation experiment.

The fields mean:

- \(\eta_{\rm rep}\): the maximum certified condition-wise representation loss;
- \(\varepsilon_{\rm exec}\): the composed execution-error scale over the certified operation;
- \(\delta_{\rm exec}^{\rm total}\): the composed execution-risk bound over that operation and
  horizon;
- \(a\): total atoms in the certified catalog;
- \(r\): maximum atom rank in the declared flattening;
- \(b_{\rm desc}^{\rm peak}\): maximum simultaneously resident reconstruction bytes;
- \(b_{\rm desc}^{\rm total}\): distinct reconstruction bytes stored across the atom catalog;
- \(b_{\rm meta}^{\rm peak}\): maximum simultaneously resident certificate and sampling metadata;
- \(b_{\rm meta}^{\rm total}\): distinct certificate and sampling-metadata bytes stored for the
  certified revision;
- \(s^{\max}\): maximum fresh samples, or another defined stochastic work unit, at one schedule
  step;
- \(s^{\rm total}\): maximum total fresh samples over one certified horizon;
- \(t_{\rm fresh}^{\max}\): maximum fresh scalar or byte traffic at one schedule step; and
- \(t_{\rm fresh}^{\rm total}\): maximum total fresh traffic over one certified horizon; and
- \(h\): certified trace horizon.

The certificate retains the per-atom, per-operation, and per-trace-step tables from which these
aggregates are computed, plus the risk-composition record that yields
\(\delta_{\rm exec}^{\rm total}\). A
maximum may not stand in for a total, and a total may not stand in for a peak.

The certificate also records:

1. the faces served by each atom, the complete minimal-nonface list, and a causal record for every
   excluded condition;
2. each witness loss and rank;
3. the description class, reconstruction, residual relation, and any sampling law;
4. the operation-specific composition map and error bound;
5. the observation/protected-set contract; and
6. the physical conversion from mathematical probes to page reads, bytes, memory, and latency.

The following block is the sole machine-readable authority for the certificate dimensions. The
schema generator must parse this exact bounded block and must reject any disagreement between it
and the implemented schema. The listed order is retained in generated inspection data; it does not
change the mathematical rank of one dimension relative to another.

<!-- CASSETTE_CERTIFICATE_DIMENSIONS_BEGIN -->
```json
{
  "mathematics": [
    "target",
    "condition_metrics",
    "compatibility",
    "atoms",
    "description_contract",
    "observation_contract",
    "execution_contract",
    "trace_contract"
  ],
  "resources": [
    "eta_rep",
    "epsilon_exec",
    "delta_exec_total",
    "atom_count",
    "max_atom_rank",
    "description_bytes_peak",
    "description_bytes_total",
    "metadata_bytes_peak",
    "metadata_bytes_total",
    "fresh_samples_max",
    "fresh_samples_total",
    "fresh_traffic_max",
    "fresh_traffic_total",
    "fresh_traffic_unit",
    "horizon"
  ],
  "tables": [
    "per_atom",
    "per_operation",
    "per_trace_step"
  ],
  "physical": [
    "conversion_rows",
    "conversion_digest"
  ]
}
```
<!-- CASSETTE_CERTIFICATE_DIMENSIONS_END -->

This vector is one point in a feasible resource set. Its undominated points form the Pareto
frontier. Cassette may select a plan only after the acceptance row fixes the feasible region. The
repository's lexicographic objective \(J\) then minimizes implementation cost; it does not erase
mathematical resource dimensions.

## 9. Claude loop: final disposition

Claude's loop reinforces one part of this foundation and conflicts with another.

| Claude claim | Disposition | Cassette use |
|---|---|---|
| Universal truncated-SVD Frobenius upper bound | Conditional upper bound | One dense rank-constrained description class. |
| Column sampling | Valid mean-square upper bound with fresh randomness | Theorem 5, after its storage and probability model is explicit. |
| Frobenius-basis conservation law | Valid | Lemma 5.2; explanatory only, not a bound for arbitrary descriptions. |
| Unbounded-storage net | Valid in a scalar-word model | Proposition 5.3; an exponential-description endpoint. |
| Product-dictionary sphere-covering bound | Valid only in the declared union-of-subspaces model | Theorem 5.4; optional for plans that adopt that model. |
| Layer allocation | Valid under first-order independent centered errors | Lemma 6, never a general sequential law. |
| Cache plus fresh residual sampling | Valid as an upper bound | The execution layer, separate from atom compatibility. |
| Worst-case output-relative \(\Omega(pq)\) for any storage | **REJECTED** | The perturbation argument assumes raw unencoded entries; low-rank and other structured classes contradict the universal statement. |
| Counting lower bound from output dimension | **REJECTED** | Rank and the storage/word model are missing. |
| Stable rank gives a probe lower bound | **REJECTED** | The displayed inequality supports no such lower bound. |
| Deterministic versus randomized universal separation | **REJECTED** | Only restricted raw-entry or product-cell versions were shown. |
| Reusing probes destroys randomization | **REJECTED** | It requires a revealed fixed sample, adaptive adversary, no fresh coins, and a restricted cell model. |
| \(t=pD_A(b_{\rm desc},b_{\rm meta})/(\varepsilon^2\|A\|_F^2)\) as equality | **REJECTED** | The sampler proves only a sufficient upper bound; no converse exists. |
| Sublinear execution iff rate-distortion compressible | **REJECTED** | With resident column-norm metadata, fresh sampling is sublinear for every square matrix at fixed Frobenius-relative mean-square error; no iff follows. |

The conflict produces the better result. Description distortion governs execution *inside one
chosen atom*. The compatibility bifiltration governs which conditions that atom can serve. Neither
quantity determines the other.

## 10. Literature and novelty boundary

Known components used above include:

- Marcus and Moyls, “Linear Transformations on Algebras of Matrices,” *Canadian Journal of
  Mathematics* 11 (1959), 61–66, DOI
  [10.4153/CJM-1959-008-0](https://doi.org/10.4153/CJM-1959-008-0), for the complex square
  rank-preserver precursor;
- Westwick, “Transformations on Tensor Spaces,” *Pacific Journal of Mathematics* 23 (1967),
  613–620, [primary paper](https://msp.org/pjm/1967/23-3/pjm-v23-n3-p21-p.pdf), for the onto
  decomposable-tensor preserver over an arbitrary field;
- Drineas, Kannan, and Mahoney, “Fast Monte Carlo Algorithms for Matrices I,” *SIAM Journal on
  Computing* 36 (2006), 132–157, DOI
  [10.1137/S0097539704442684](https://doi.org/10.1137/S0097539704442684);
- Eckart and Young, “The Approximation of One Matrix by Another of Lower Rank,” *Psychometrika* 1
  (1936), 211–218; and
- Blackwell, “Equivalent Comparisons of Experiments,” *Annals of Mathematical Statistics* 24
  (1953), 265–272, DOI
  [10.1214/aoms/1177729032](https://doi.org/10.1214/aoms/1177729032);
- Hadwin, Harrison, and Ward, “Rank-One Completions of Partial Matrices and Completely
  Rank-Nonincreasing Linear Functionals,” *Proceedings of the American Mathematical Society* 134
  (2006), 2169–2178, DOI
  [10.1090/S0002-9939-06-08094-4](https://doi.org/10.1090/S0002-9939-06-08094-4), for the cycle
  criterion in rank-one partial-matrix completion; and
- Boege, Petrović, and Sturmfels, “Marginal Independence Models,” *ISSAC 2022*, DOI
  [10.1145/3476446.3536193](https://doi.org/10.1145/3476446.3536193), which realizes simplicial
  complexes as rank-one marginalization patterns of tensors.

The explicit universal fixed-metric, single-ambient-orbit construction and proof in Theorem 3 were
derived in this work. The closest collisions found were the known cycle criterion for rank-one
partial-matrix completion and the realization of simplicial complexes as tensor-marginal rank
patterns. Neither gives condition-loss compatibility under positive-definite metrics, one shared
rank-one witness for every served face, a uniform positive threshold, and one ambient-unitary orbit
at once. The bounded source check recorded in E-012 did not locate that exact conjunction. The
search is not exhaustive. This file claims neither publication novelty, priority, nor patent
consequence.

## 11. Migration checklist

This checklist is part of the authority. A checked item means the old mathematical assumption was
removed, specialized, or proved irrelevant at the named surface.

- [x] `MATHS.md`: established the compatibility, atom-capacity, execution, sequential, and
  observation layers; recorded every accepted and rejected Claude claim.
- [x] `AGENTS.md`: require this authority before numerical, compiler, pager, or plan work; remove
  the prompt-fixed pager example.
- [x] `research/RESEARCH.md`: amend Q7, Q11–Q12, Q14, Q17–Q21, Q27, Q33–Q40, Q47, Q58–Q64,
  Q68–Q70, Q75, and Q80 where the old assumption entered.
- [x] `research/ACCEPTANCE_MATRIX.yaml`: replace prompt-persistent modes and router-recovery rows
  with compatibility-certified compiled execution and its resource certificate.
- [x] `research/QUESTION_QUEUE.md`: update the shared symbols, D2/D8, and affected question text so
  the queue no longer asks implementation to assume its former answer.
- [x] `research/EVIDENCE.md`: preserve the physical E-009/E-011 bounds while removing their
  prompt-fixed interpretation; add the mathematical amendment record.
- [x] `IMPLEMENTATION.md`: preserve S01–S11 and the user's existing S10/S19/S24 boundary edits;
  amend S12 onward before any pager or compiler implementation.
- [x] `README.md`: replace the shared-core/request-fixed-router account, update current S11 status,
  and link this authority.
- [x] `BUILD_STORY.md`: preserve the historical proposal and append the attributed correction.
- [x] `ORIGINAL_REMIT.md`: audited; it requires first-principles transformation but commits to no
  prompt-fixed router, top-\(k\) rule, or SVD foundation. No amendment required.
- [x] `PHILOSOPHY.md`: audited; its values and acceptance boundaries are independent of the old
  mathematics. No amendment required.
- [x] Existing product code (`errors.py`, `store.py`, `sources.py`): audited; S01–S11 implement no
  compiled selector, rank decomposition, prompt-fixed set, or sampling scheme. No code amendment is
  mathematically justified.
- [x] Existing generated schemas, generator, and tests: audited; they reserve generic plan data but
  encode no old compiled mathematics. Future certificate schemas belong to S12 and must be generated,
  not hand-edited.

Every listed item is checked only because its edit or no-change audit passed the discrepancy review.

## 12. Minimal abstraction, precise location, and exact reconstitution

**Status: OPEN.** The principal's correction in the performance-research thread on 2026-09-20
defines this section's objective.

Construct the smallest feasible mathematical abstraction in RAM that lets Cassette identify
the relevant region of the full external weight table, locate its encoded data, and retrieve
or reconstitute the required weights at their source precision. Return those weights for the
normal calculation. The mathematical abstraction may contain derived relations, encoded
structure, or other values; it need not be a partial table of original weights.

The active research record is
[research/representation/README.md](research/representation/README.md).

### 12.1 Objects and the complete path

Fix a finite source weight table \(W\), its shape and scalar encoding, and a declared class of
runtime states \(\mathcal S\). A runtime state \(s\) contains only information actually available
before the relevant weight fetch, including the operation to execute and its available inputs.
The encoder produces

\[
E(W)=(z_W,d_W),
\]

where \(z_W\) is the resident abstraction and \(d_W\) is the external representation retaining
the full source information. The interpreter and its fixed rules are source independent; every
model-dependent parameter, instruction, lookup entry, and precision witness is charged as
stored information.

The path has four separately proved stages.

1. **Interpret relevance.** From \(z_W\), \(s\), and explicitly charged external observations,
   identify a region \(S\) whose weights are sufficient for the declared next calculation.
2. **Resolve location.** Translate the region's logical coordinates into exact external byte
   ranges or encoded objects. Any intermediate directory reads belong to the read transcript.
3. **Reconstitute the table.** Read or decode those objects to produce the weights \(W|_S\),
   with their source values, precision, shape, order, and identity.
4. **Calculate normally.** Supply \(W|_S\) to the declared ordinary numerical operation.
   Release or reuse the region under a separately charged memory schedule.

The first stage concerns which weights matter. The second concerns where their data are.
Neither stage supplies the other for free. The third stage concerns the weight values
themselves; an estimate of a matrix product does not satisfy it.

### 12.2 Relevance and reconstitution obligations

A candidate must define a checkable relevance relation

\[
\mathcal R_W(s,S)
\]

that makes \(S\) sufficient for the declared next operation. Its meaning, construction,
available observations, and proof costs are part of the candidate. It is not a free oracle
that already knows which weights to fetch. The work must derive how the abstraction supplies
that information. A small sufficient region is an intended result to establish, not an
assumption inherited from a desired RAM budget.

For a read transcript \(\tau\), the reconstitution obligation is

\[
\operatorname{Decode}(z_W,S,\tau)=W|_S.
\]

Equality means recovery of the source-encoded weight values and their tensor positions.
A lossless external transformation is admissible if it supports this local inverse within the
declared resources. Merely proving that the whole source can eventually be inverted does not
prove bounded-memory access to one requested region.

The ordinary operation must receive the recovered weights, not a surrogate answer produced
by weighted samples. Its established arithmetic and ordering remain the reference. Any claim
that some source contributions can be skipped needs its own sufficiency proof. The same
abstraction must support later runtime states that need different regions of the model.

### 12.3 The quantity to minimize is total peak RAM

Measure simultaneous residency, including the mathematical representation and its workspace:

\[
M_{\rm peak}
=\max_t\left(
M_{\rm abstraction}(t)+M_{\rm metadata}(t)+M_{\rm interpreter}(t)
+M_{\rm reads}(t)+M_{\rm reconstitution}(t)
+M_{\rm weights}(t)+M_{\rm normal\ calculation}(t)
\right).
\]

All terms are encoded bytes. Source-specific code, caches, temporary decoded structures,
query state, and live accumulators must appear exactly once in this account. A single
arbitrary-precision number is charged by its encoded length and the workspace used to
interpret it. An external directory can replace a resident directory only with its reads
and transient memory recorded.

The research seeks the minimum achievable RAM requirement while satisfying relevance,
location, and reconstruction correctness. Report the accompanying external bytes, read
requests, transfer bytes, construction work, and interpretation/reconstruction work. State
the fixed constraints when claiming a minimum; trading unlimited scans or computation for
a smaller representation is a different resource point.

### 12.4 Research sequence and completion

Derive candidate abstractions and their interpretation/reconstitution rules from this
contract. Explore competing mathematical constructions in parallel. Use published work to
identify existing results, challenge originality, and construct strong comparators; it
does not determine the form of the new abstraction or replace the principal's objective.

Stress each candidate on representation collisions, indistinguishable runtime observations,
changes in the relevant region, precision boundaries, local decoding dependencies, and
hidden growth of resident or temporary state. Establish correctness before claiming a
smaller RAM requirement. Compare established and proposed methods on the same source,
runtime-state class, required source precision, normal calculation, and read/work constraints.

Completion requires a retained abstraction, an interpreter that establishes relevance and
location, exact local weight reconstitution, explicit peak-memory and access/work bounds,
and an independently challenged novelty claim. Its advantage must concern this complete
path against the fully improved applicable established comparator. A minimum or exhaustive
comparison requires a lower bound or certified optimum over its stated class.

### 12.5 Status of the earlier investigation

The earlier signed-sampling and coupled-column work optimized error in estimated matrix
products. Its 7.39% finite comparison does not establish a smaller abstraction, precise
relevance/location, or exact recovery of a needed weight region. It is not evidence of
success for this objective.

Those proofs and experiments remain recorded in
[research/representation/COMPARISON.md](research/representation/COMPARISON.md) as a
superseded research direction. They no longer appear here as accepted representation
deliverables. Section 5 retains its separately scoped execution theorem; it does not answer
section 12's abstraction and reconstitution problem. This correction does not change the
independently owned mathematics roots, product code, or existing release gates.

### 12.6 Current exact constructions and their boundary

The corrected investigation now has exact constructions for finite-domain decision
representations, source-certified geometric routing, local source-word reconstitution,
and packets prepared while a region choice remains unresolved. The derivations and their
source-family restrictions are indexed in
[the active research record](research/representation/README.md#results-under-the-corrected-objective).

For a Boolean degree-at-most-\(D\) record field with \(t\) unresolved identifier bits
and \(P\) words of \(b\) bits per record, the exact universal preload requirement is
\(Pb\sum_{j=0}^{\min(D,t)}\binom tj\) bits, counting all prior source-dependent
information. The lower bound assumes all coefficient assignments remain possible at the
observed prefix and no source reads occur after the remaining bits resolve. Restricted
coefficient packets attain it. The prefix construction provides their payload in at most
three logical extents and selects original source words after in-place branch preparation.
Headers, physical blocks, integrity metadata, addresses, and the calculation schedule
remain additional obligations.

The finite checks establish the stated exact identities on generated source families.
Known interpolation already matches the packet's information bound. Neither these checks
nor the new physical slot formula establishes novel mathematics superior to the strongest
applicable established method, or the required source structure in a frontier model.
Section 12 remains OPEN; the construction does not admit a product path or numerical kernel.

### 12.7 Query-derived relevance and original-weight experiments

The next constructions derive region choices from current inputs for arbitrary integer
source matrices within two declared operations. The
[quotient and remainder representation](research/representation/phase-quotient-routing.md)
preserves a source argmax by proving a candidate set, refining uncertain choices with
original gate rows, and returning the original winning weight record. The
[sum and moment refinements](research/representation/remainder-sum-certificates.md)
store derived mathematical values that constrain the discarded detail. A separate
[dense ReLU construction](research/representation/dense-relu-relevance.md) proves some
intermediate activations exactly zero before reading their source rows, then reads and
uses original up rows and down columns for all remaining nonzero contributions.

The common column contribution may be omitted for an argmax but must be retained for a
threshold comparison. This distinction is part of the relevance proof. Numerical scores
that feed later calculations are recovered from original weights, not silently replaced
by the representation's coarse values. Exact integer proofs do not establish parity with
an arbitrary floating-point kernel. A separately scoped
[rounding-cell certificate](research/representation/rounding-relevance.md) addresses
finite-precision omission only for its explicitly declared arithmetic and entry states.

The [routing comparison](research/representation/remainder-sum-comparison.md) records
220 source/configuration combinations and 85,140 exact route executions on generated
sources. The [dense comparison](research/representation/dense-relu-comparison.md) records
seven configurations and 2,709 exact layer evaluations. These are repeated executions on
declared finite fixture sets, not counts of independent real-model inputs. Encoded guide
bytes, interpreter scratch, original-weight buffers, logical reads, modeled pages, and
physical latency remain distinct costs. A compact guide can force a full source scan.

Independent review retained the core containment proofs and exposed source-binding,
tie, phase-selection, and memory-accounting boundaries. The comparisons now include exact
centered and split encodings, moment bounds, and a streamed dense baseline that already
skips down columns with zero activations. Established interval filtering, knapsack support,
Cauchy–Schwarz, and lossless residual coding cover those ingredients. Joint residual
relationships remain a research candidate; no novelty or best-method advantage is admitted
by these fixtures. Section 12's completion condition remains unchanged.

The [column-total refinement](research/representation/column-sum-propagation.md) and
[projected joint interpretation](research/representation/projected-transport-representation.md)
retain relationships between source regions. The latter replaces all noncompared residual
rows with one bounded aggregate row. Its exact optimization uses dimension-sized mutable
state and gives a safe, sometimes sharper comparison than separate row intervals using
the same stored fields. It is a relaxation of full joint interpretation, and one exact
optimization per challenger can still dominate latency. The finite witness establishes
strict pruning at the same guide content, not equal total work or a novel global optimum.

A subsequent [pair-total support construction](research/representation/pair-total-support.md)
relaxes the separate compared-row totals while preserving their sum and column competition.
Its two-piece concave coordinate objectives share a slope order determined only by the
query. One sort and streaming integer allocation compute all anchor comparisons in
\(O(d\log d+md)\) arithmetic and \(O(d)\) mutable words. It retains the same strict
four-to-two witness without a flow solver, but a separate counterexample proves that it
can be weaker than projected flow. Intersecting it with cheaper bounds preserves their
conclusions. The executable support interpreter passes 81,000 source-containment checks
and 4,050 exhaustive relaxed-optimum checks; these do not establish novelty or physical speed.

### 12.8 Smaller joint representation and stronger interpretation

The [clipped-slack representation](research/representation/saturated-slack-representation.md)
replaces the column vectors \(u,L,V\) with
\(\alpha_j=\min(u_j-L_j,2w_j)\) and
\(\beta_j=\min(V_j-u_j,2w_j)\). This preserves every propagated single-row
interval and every projected pair feasible set. A packed codec omits neutral values,
charges its flags and coordinates, and preserves all checked bounds. If every column
is neutral, projected pair interpretation equals separate row support: the joint step
can be skipped. A tiny code for that extra information does not make the complete
representation tiny; \(Q,w,t\), identity, addresses, and workspace remain charged.

The [scalar-dual refinement](research/representation/pair-dual-refinement.md) restores
the individual row totals omitted by pair-total support. For its declared projected
pair polytope,

\[
 M^{\rm proj}_{ik}(x)
 =\min_{\mu\in\mathbb R}\left[\mu(t_i-t_k)+B_{ik}(x-\mu\mathbf1)\right].
\]

For integer queries, the multiplier search is exact on a doubled integer grid.
Convexity permits adjacent-value binary search; merging two sorted query arms avoids
sorting at each evaluation. This recovers the projected bound with dimension-sized
working state and no additional source information. It may require more computation
than the weaker bound. The projected polytope still relaxes the full joint source,
and established specialized optimization remains a required comparator.

The [packed original-weight replay](research/representation/dual-original-weight-check.md)
shows a strict gain after intersecting the earlier row and pair bounds: two original
gate reads become zero while the selected original payload and ordinary calculation
remain identical. The complete joint guide is 74 bytes on that tiny source; a lossless
centered guide needs 69 bytes and also needs no gate discovery reads. The fixture
therefore proves a stronger interpretation, not a better complete resource frontier.

The [adaptive original-read comparator](research/representation/adaptive-source-refinement.md)
also strengthens the established baseline. A fetched original score \(s_i\), together
with its represented lower bound \(l_i\), gives a bound \(H\le s_i-l_i\) on the
discarded common score. Updating that bound and the exact incumbent can exclude later
reads without storing the common weight vector. Shared query prefixes accelerate
row-sum support. A new representation must face this refinement as well as stronger
read orders and exact compressed encodings. None of these results closes section 12.

### 12.9 Exact interpretation of all retained residual margins

The [full aggregate criterion](research/representation/full-aggregate-feasibility.md)
tests whether the unexamined rows can actually realize a proposed aggregate.
For omitted row totals sorted ascending, their prefix totals \(T_r\), and a
proposed column aggregate \(z\), integral completion is equivalent to

\[
z\ge0,\qquad \sum_jz_j=T_n,\qquad
\sum_j(z_j-sw_j)_+\le T_{n-s}\quad(0\le s\le n).
\]

An expiry-based separator checks this condition with row-sized and column-sized
working arrays. For binary residual capacities, the same constraints become nested
quotas and permit exact single-row support through a heap. These constructions
preserve the uncapped column totals; the earlier clipped slacks cannot substitute
for information they deliberately discard.

The [full-pair interpreter](research/representation/full-pair-polymatroid.md)
extends the result to arbitrary integral shared column capacities. It relaxes the
two distinguished row totals to their sum, allocates their combined column values
over an integral polymatroid, and restores the separate totals with an exact scalar
dual. An increment changes a suffix of the omitted-row feasibility slacks. Batched
suffix updates avoid both an explicit transportation matrix and iteration over
every integer weight unit. The working state uses \(O(m+d)\) words, with integer
widths, per-pair preparation, heap work, scalar trials, and touched-node restoration
charged separately.

This interpreter obtains the exact maximum pair difference over every residual
table with the guide's margins and capacities. It therefore extracts the strongest
universally valid pair upper bound available from those fields alone. This is a
statement about a fixed information set and one comparison, not the optimality of
the representation or the complete routing policy. Original source weights still
supply every ordinary calculation after selection.

Exhaustive small-domain references agree with the full-pair interpreter on 8,100
queries and with its relaxed allocation on the same queries. An additional 504
wide-query and integer-dilation checks exercise large weight magnitudes. The
research implementation and independent review establish this stated integer
operation; they do not measure a real model's peak RAM or physical supply time.

The [original-weight replay](research/representation/full-pair-source-witness.md)
uses the same 67-byte guide under projected and full interpretation. Full
interpretation eliminates two gate discovery reads, then retrieves the original
payload through decoded physical locators and returns the same ordinary result.
A 64-byte lossless centered guide also needs no discovery reads on that fixture.
The replay proves stronger interpretation of the same fields, not a complete
memory advantage. The final scalar search uses a subgradient from each allocation
to need one new support evaluation per step while preserving the exact bound.

The [explicit-flow comparison](research/representation/full-pair-flow-comparison.md)
returns identical exact supports in 16 comparisons using only the same compiled
widths and margins. Both measured paths include fresh preparation. On the four
32-by-32 cases, the canonical interpreter's additional traced Python allocation
peak is 13,720--13,880 bytes; the explicit transportation graph's is
227,088--227,248 bytes. Untraced timing also favors this interpreter in the declared
Python runs. These observations compare two implementations, not all established
methods, process RAM, model-scale inference, or physical storage performance.
The result binds the measured definitions by digest. A retained-closure defect
found during measurement was removed and checked with cyclic collection disabled.

The [larger projected comparison](research/representation/joint-scale-experiment.md)
also narrows the earlier evidence: independent, structured, and near-tie generated
families show no pair or scalar-dual read reduction beyond propagated bounds.
Deliberately coupled cases show small reductions under a fixed fetch policy.
That comparison predates full-pair interpretation and does not include the improved
adaptive-read policy. It cannot establish a best-method result. Classical flow,
polymatroid allocation, and specialized transportation methods remain comparators;
novelty and section 12's complete resource advantage remain OPEN.

### 12.10 Improvement hypothesis and complete-path falsification

The principal's 2026-09-29 instruction sets the null hypothesis to improvement.
The [frozen experiment](research/representation/improvement-hypothesis-protocol.md)
tests exactness, memory, elapsed time, and discovery reads separately. A finite pass
does not prove the general hypothesis, and non-rejection does not establish improvement.

The [retained result](research/representation/improvement-hypothesis-results.md) contains
32 same-information support comparisons and 1,728 original-weight route checks across
32 generated source cases. Every support, winner, original payload, and ordinary
integer output matches its reference. The full-pair support solver uses less traced
Python allocation and time in all 32 comparisons with an improved transportation
solver using potentials and Dijkstra; median paired ratios are 0.143 and 0.0824.

The complete-path result reverses that local ranking. At the frozen quotient step of
256 and gate sizes 12 by 16 or 24 by 32, pair-total, projected scalar-dual, and full-pair
routes use more traced allocation and time than both adaptive row sums and exact
centered in every source case. No candidate reduces gate reads against adaptive row
sums. The full-pair route's median paired allocation and time ratios against row sums
are 1.199 and 7.252. These observations reject complete-path dominance for the tested
implementations and settings. The predeclared one-sided tests reach the same conditional
conclusion after correction for 20 comparisons.

The allocation trace includes preparation, the copied guide, routing state, original
payload reads, and ordinary calculation, but excludes shared interpreter state and
process baseline. Cached local-file timing is not physical external-drive timing.
The source case is the statistical unit; queries, repeat measurements, and the repair
rerun are not additional independent samples. Section 12 remains OPEN, with no
new admission of a product path, numerical kernel, novelty claim, or model-scale win.
