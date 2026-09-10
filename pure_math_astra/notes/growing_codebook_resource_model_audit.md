# Finite-codebook avoidance versus Cassette resource certificates

Status: a restricted execution theorem follows.  It does not yet compare
two complete Cassette resource certificates at a common resident-byte or
physical-read budget.

## The source-oblivious finite-codebook theorem

Fix a sufficiently small rational square \(\eta=r^2>0\), an integer
\(m\geq1\), and put

\[
 H_\eta=\mathbf1\mathbf1^*+\eta I_4,
 \qquad G=I_m\otimes H_\eta,
 \qquad q=4m,\quad s=2m.
\tag{1}
\]

One rational factor of \(H_\eta\) is

\[
 R_{\rm block}=
 \begin{pmatrix}\mathbf1^T\\rI_4\end{pmatrix},
 \qquad R_{\rm block}^*R_{\rm block}=H_\eta.
\tag{2}
\]

Let \(R_0=I_m\otimes R_{\rm block}\), whose row dimension is \(t=5m\).
Consider a finite family

\[
 \mathcal B=\{B_1,\ldots,B_N\}\subset\mathbb C^{p\times q},
 \qquad N\leq2^b,
\tag{3}
\]

fixed before the source is chosen.  The choice of one \(B_j\) is made once
for the source, before any query; it is not a query-selected reconstruction.

For a complex \(B_j\), let \(S_j\subset\mathbb R^p\) be the real span of
the real and imaginary parts of its columns.  It has dimension at most
\(2q\).  The standard Stiefel net argument gives a real rational isometry
\(U\in\mathbb Q^{p\times t}\) with

\[
 \|P_{S_j}U\|_{\rm op}<\delta\quad(1\leq j\leq N)
\tag{4}
\]

whenever

\[
 3\exp\!\left[b\log2+(t+2q)\log9-{p\delta^2\over64}\right]<1.
\tag{5}
\]

Here rationality follows by approximating a strict real-Stiefel solution by
rational Cayley coordinates.  Since \(t+2q=13m\), condition (5) is met for

\[
 p=O\!\left({b+m\over\delta^2}\right).
\tag{6}
\]

Set \(A=UR_0\).  Then \(A\) is rational and \(A^*A=G\).  For every
\(B_j\), the realification of (4) gives, for all complex \(x\),

\[
 \|(A-B_j)x\|_2^2
 \geq(1-\delta^2)\|Ax\|_2^2.
\tag{7}
\]

Indeed, the component of \(Ax\) in the complexification of \(S_j\) has
norm at most \(\delta\|Ax\|_2\).  The distance from \(Ax\) to every
vector \(B_jx\) in that subspace is therefore at least
\(\sqrt{1-\delta^2}\|Ax\|_2\).  Consequently

\[
 (A-B_j)^*(A-B_j)\succeq(1-\delta^2)G
 \succeq(1-\delta)G.
\tag{8}
\]

This is a worst-case source statement against a finite family fixed by the
charged decoder state.  Training is compatible with the theorem when every
resulting source-specific parameter is encoded in the bounded codeword and
a fixed interpreter decodes that word; its possible reconstructions then
still form a finite family.  The theorem does not apply when a
source-dependent decoder, continuous parameter, or other side information
is made available without that bounded representation.

## Exact restricted comparator

The following is the strongest direct consequence of (8).  After choosing
one \(B_j\), write \(R=A-B_j\).  Permit an arbitrary fixed unitary
coordinate transform \(Q\), free for this theorem, and a law on maps
\(L_S\) such that

\[
 \operatorname{rowsupp}(L_S)\subseteq S,qquad |S|\leq2m,qquad
 \mathbb E L_S=I.
\tag{9}
\]

The law and its maps are fixed before the query.  Its returned value has
the form

\[
 \widehat y(x)=B_jx+RQ^*L_SQx.
\tag{10}
\]

Thus it is exactly unbiased for \(Ax\) and reads at most \(2m\) declared
columns of \(RQ^*\) in the abstract encoded-column model.  The trace
certificate for all such global fixed-linear laws gives

\[
 \sup_{\|x\|_2=1}\mathbb E\|\widehat y(x)-Ax\|_2^2
 \geq\nu_{2m}(Q R^*RQ^*)
 \geq t_{2m}(R^*R)
 \geq(1-\delta)t_{2m}(G).
\tag{11}
\]

The last step uses (8), Loewner monotonicity and positive homogeneity of
the water level.  Unitary \(Q\) does not change the water level.  This
lower bound already grants the comparator unrestricted global allocation of
the \(2m\) supports, full-query *linear* coefficients in every retained
row, and free sampling-law metadata.  It does not grant a nonunitary
coordinate change: such a map changes the query norm and requires a
separate encoded-column and byte model.

For the Gram in (1),

\[
 t_{2m}(G)=\sqrt{1+4\eta+\eta^2}-1=2\eta+O(\eta^2).
\tag{12}
\]

On the other hand, with \(B=0\), the direct product of the fixed
four-coordinate query-adaptive catalogs gives

\[
 \sup_{\|x\|_2=1}\mathbb E\|A(Y(x)-x)\|_2^2
 \leq1.999\eta,
 \qquad \|Y(x)\|_0\leq2m,\quad\mathbb EY(x)=x.
\tag{13}
\]

For sufficiently small \(\eta\) and then sufficiently small \(\delta\),
(11)--(13) give a strict separation between this query-selected finite
catalog and every comparator in (9)--(10).  Both use the same rational
source matrix \(A\) and the same abstract cap of \(2m\) individually
addressable residual columns.

## What MATHS permits this to mean

This is a valid abstract execution comparison only under all of the
following declared restrictions:

1. The decoder family \(\mathcal B\) is fixed independently of the source,
   and encoding chooses one member once per source.
2. The reconstruction is linear action by that fixed \(B_j\).
   Query-chosen reconstructions and arbitrary nonlinear resident output maps
   are outside the comparator.  A trained parameter is permitted only when
   its resulting source-specific state is charged in the finite codeword
   decoded by the fixed interpreter.
3. The full query is an admitted observation for choosing the adaptive
   catalog law.  Its chosen law, random seed, and support schedule are
   recorded as query-dependent execution state.
4. Columns of \(RQ^*\) are declared individually addressable.  A column
   support count is only a mathematical work cap.  The free \(Q\) in the
   lower bound is an analytical strengthening; an actual nonidentity
   transform must also declare how its transformed columns are stored and
   addressed.
5. Arithmetic is exact over the represented rational field.  Rounding,
   finite random-bit generation, and bounded workspaces need their own
   error and byte records.

Under a fixed \(\eta\), a rational four-coordinate catalog has a finite
representation.  Reusing it blockwise yields an \(O_\eta(m)\) abstract
schedule and metadata representation if each block's selected law and
support are explicitly stored.  The finite-catalog bridge proves existence,
but gives neither its numerical constant nor a byte-bounded selector or
random-bit implementation.  MATHS therefore does not yet supply the
required \(b_{\rm meta}^{\rm peak}\), \(b_{\rm meta}^{\rm total}\), or
operation schedule record.

## The missing resource bridge

The parameter \(b\) in (3) counts a choice among matrices.  It is not,
by itself, either \(b_{\rm desc}^{\rm peak}\) or
\(b_{\rm desc}^{\rm total}\) in MATHS.  An arbitrary fixed codebook can
hide unbounded matrix data in its table or in decoder constants while its
selected index has only \(b\) bits.  Likewise, saying that every source has
\(pq\) rational “words” does not bound source bytes: the word lengths of
the rational entries may vary.

The one concrete missing bridge is a finite-word description class
\(\mathcal C_{b_{\rm desc},b_{\rm meta}}(A)\) that specifies an encoder,
a decoder, the charged representation of decoder tables and constants, and
a source-word format.  It must prove that both the selected \(B_j\) and all
residual-addressing data fit the stated peak and total byte fields.  Only
then can (11) be compared with the adaptive catalog at a common resident
budget.  MATHS also requires a separate conversion from the \(2m\) column
cap to pages, encoded bytes, memory, and latency; the theorem does not make
that conversion.
