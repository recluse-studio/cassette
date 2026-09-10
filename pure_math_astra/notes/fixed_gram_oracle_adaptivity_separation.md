# Fixed-Gram column oracles: exact values and an adaptivity gap

This note combines the [independent orbit proof](fixed_gram_orbit_static_oracle_minimax_independent_proof.md), the [finite catalog bridge](query_adaptive_finite_catalog_bridge.md), and the [real basis-reversal theorem](query_adaptive_general_basis_reversal.md). It strengthens the nonlinear-decoder consequence of the [Gaussian argument](gaussian_static_nonlinear_oracle_minimax_gap.md). The mathematical oracle is specified below. Originality and sufficient Cassette significance remain unresolved.

## Information and error

Let \(G\succ0\) be a known real \(q\times q\) matrix and let \(p\ge q\). The source ranges over the full set

\[
\mathcal O_G=\{A\in\mathbb R^{p\times q}:A^TA=G\}.
\]

A query is \(x\in\mathbb R^q\). After choosing a set \(S\subseteq[q]\), the decoder receives the exact columns \(A_{:S}\). Its output \(F_S(A_{:S},x)\) can be any Borel vector in \(\mathbb R^p\). The decoder has no source-dependent resident information. Its support law is independent of \(A\). Every admitted decoder is exactly unbiased on every source and query:

\[
\sum_S p_S(x)F_S(A_{:S},x)=Ax.
\tag{1}
\]

The error is the supremum, over \(A\in\mathcal O_G\) and \(\|x\|=1\), of the expected squared Euclidean output error. A static support law has \(p_S(x)=p_S\); its decoder may still use \(x\) nonlinearly. A query-dependent law may choose the support distribution after reading \(x\). The hard cap is \(|S|\le s\) almost surely.

Define the two coefficient values

\[
\nu_s(G)=\inf_{\substack{\mathbb EL=I\\
L\text{ has at most }s\text{ nonzero rows a.s.}}}
\lambda_{\max}\!\left(\mathbb E(L-I)^TG(L-I)\right),
\tag{2}
\]

where the random matrix law is fixed before \(x\), and

\[
\Psi_s(G)=\sup_{\|x\|=1}
\inf_{\substack{\mathbb EY=x\\\|Y\|_0\le s\text{ a.s.}}}
\mathbb E(Y-x)^TG(Y-x).
\tag{3}
\]

## The exact nonlinear-oracle identities

The static oracle minimax value is \(\nu_s(G)\). The query-dependent oracle minimax value is \(\Psi_s(G)\).

For completeness, the reduction has three distinct steps. Average a decoder over the full left orthogonal group \(O(p)\). Finite uniform risk bounds each positive-probability branch on its observed orbit, so this Haar integral exists. Jensen bounds the averaged risk by the orbit average of the original risk, and hence by its worst-source risk. It does not imply a comparison with the original risk at each individual source.

The averaged output is equivariant. Every orthogonal transformation fixing the observed columns must therefore fix that output. These transformations include every orthogonal action on the complement of their span. The output consequently has the form \(A_{:S}c_S(x)\). Transitivity on matrices with the same observed Gram matrix makes \(c_S(x)\) independent of \(A\). Exactness becomes \(\sum_Sp_SE_Sc_S(x)=x\).

For a fixed law, write

\[
M=\sum_{S:p_S>0}p_SE_SG_{SS}^{-1}E_S^T.
\tag{4}
\]

The empty support contributes zero. Exactness for every query requires \(M\succ0\). Quadratic minimization gives pointwise error \(x^T(M^{-1}-G)x\), attained by

\[
c_S(x)=G_{SS}^{-1}E_S^TM^{-1}x.
\tag{5}
\]

This proves the static identity. For a query-dependent law, fix \(x\) first and apply the same averaging. The lower bound is the inner value in (3); only then take the query supremum. A finite catalog of unbiased sparse linear laws supplies the reverse inequality to arbitrary positive tolerance. Selecting the first law with least quadratic risk is Borel. This proves the second identity without interchanging an infimum and a supremum. The query-dependent identity here uses the hard cap in (3).

## A free fixed basis does not lower the static value below spectral water

For an integer \(1\le s<q\), let \(t_s(G)>0\) be the unique solution of

\[
\operatorname{tr}\bigl(G(G+t_s(G)I)^{-1}\bigr)=s.
\tag{6}
\]

Grant a static decoder any orthogonal matrix \(Q\) chosen before the source and query, direct oracle access to columns of \(AQ\), and the transformed query \(Q^Tx\). Then

\[
\inf_{Q\in O(q)}\nu_s(Q^TGQ)=t_s(G).
\tag{7}
\]

To prove the lower bound, a static schedule with error at most \(v\) has \(M^{-1}-G\preceq vI\). Thus

\[
\mathbb E|S|=\operatorname{tr}(GM)
\ge\operatorname{tr}\bigl(G(G+vI)^{-1}\bigr).
\tag{8}
\]

A hard cap implies \(\mathbb E|S|\le s\), so \(v\ge t_s(G)\). This trace expression is invariant under orthogonal conjugation, proving the same bound for every \(Q\).

For attainment, diagonalize \(G\), with eigenvalues \(\lambda_i>0\), and set \(\pi_i=\lambda_i/(\lambda_i+t_s(G))\). These numbers lie in \((0,1)\) and sum to the integer \(s\). The convex hull of indicators of size-\(s\) subsets is \(\{z\in[0,1]^q:\sum_i z_i=s\}\): an extreme point cannot have two fractional coordinates, and the integer sum excludes exactly one. Hence a size-\(s\) law with these marginals exists. Return the coordinate estimator with diagonal weights \(\mathbf1_{\{i\in S\}}/\pi_i\). It is unbiased, and its risk matrix in this eigenbasis is

\[
\operatorname{diag}\bigl(\lambda_i(1/\pi_i-1)\bigr)=t_s(G)I.
\tag{9}
\]

This establishes (7) with arbitrary nonlinear decoders included in its lower bound.

## Strict improvement for every nonscalar spectrum at intermediate caps

Suppose \(q\ge4\), \(2\le s\le q-2\), and \(D\succ0\) is diagonal and nonscalar. The real basis-reversal theorem constructs rotations \(Q_\tau\), constants \(c,\tau_0>0\), and a catalog of at most \(q+2\) unbiased sparse laws such that

\[
G_\tau=Q_\tau DQ_\tau^T,
\qquad
\Psi_s(G_\tau)\le t_s(D)-c|\tau|
\quad(0<|\tau|<\tau_0).
\tag{10}
\]

On the source orbit \(\mathcal O_{G_\tau}\), a query-dependent column oracle therefore has strictly smaller worst-source, worst-query error than every static nonlinear oracle, including static oracles granted any free fixed right basis. Both use the same hard column cap. The constants depend on \(D,q,s\); this is a strict improvement, not a uniform multiplicative gap.

## A gap growing with the number of four-column blocks

Let \(H_\eta=\mathbf1\mathbf1^T+\eta I_4\). Fix a sufficiently small positive \(\eta\le1/100\) for which the proved finite catalog gives real-query risk at most \(19\eta/10\). Let

\[
G=H_\eta^{\oplus m},\qquad q=4m,\qquad p\ge q.
\tag{11}
\]

Applying the catalog within each block gives an exactly unbiased query-dependent decoder with hard cap \(2m\) and worst-source, worst-unit-query error at most \(19\eta/10\). The real catalog follows by taking real parts of the complex construction for this real Gram matrix; this preserves mean and support and cannot increase squared error. Summing the block risks gives the stated bound for unit queries in the whole space.

Consider any static nonlinear decoder that meets the same error on the whole orbit. A free fixed right orthogonal basis is again allowed. Its expected number of acquired columns \(\bar s\), without requiring a hard cap, obeys (8). The spectrum of each block is \(4+\eta,\eta,\eta,\eta\), so

\[
\begin{aligned}
\frac{\bar s}{m}
&\ge\frac{4+\eta}{4+(29/10)\eta}+\frac{30}{29}\\
&\ge\frac{4010}{4029}+\frac{30}{29}
=\frac{237160}{116841}
>\frac{101}{50}.
\end{aligned}
\tag{12}
\]

The second inequality uses that the first term decreases in \(\eta\) and \(\eta\le1/100\). The final strict gap is exactly

\[
\frac{237160}{116841}-\frac{101}{50}
=\frac{57059}{5842050}>0.
\tag{13}
\]

Thus, for every such static decoder with \(\bar s\le(2+1/50)m\), some source on the exact Gram orbit and some unit query violate the error target. The adaptive construction meets that target with at most \(2m\) columns on every execution. No large output dimension or Gaussian normalization factor is needed; \(p=q\) is permitted. The hard source may depend on the competing decoder. This does not assert one common hard source for all decoders.

## Why source-dependent support selection is a different information model

Even one selected index can communicate source information. Let \(p=q=2\), \(G=I_2\), and

\[
J=\begin{pmatrix}0&-1\\1&0\end{pmatrix}.
\]

For a source \(A\in O(2)\), choose column 1 if \(\det A=1\), and column 2 if \(\det A=-1\). In the first case, the observed column \(a=Ae_1\) determines \(A=[a,Ja]\). In the second case, the observed column \(b=Ae_2\) determines \(A=[Jb,b]\). Each reconstruction has the required determinant and observed column. The selected index identifies the applicable rule, so one read recovers \(Ax\) exactly for every \(x\). This source-dependent schedule beats the source-independent value \(\nu_1(I_2)=1\).

The full \(O(p)\) orbit also matters. If sources were restricted to \(SO(2)\), observing the first column would already determine the second through \(J\), even with a source-independent schedule.

## Consequence and remaining work

The theorem gives an exact execution-error comparison for a declared information class: the Gram matrix is common knowledge, payload access returns whole columns, support selection can depend on the query, and the decoder has no source-trained resident information. It removes the earlier restriction that competing outputs must be linear combinations of fetched columns. That restriction now follows from worst-orbit symmetry for an optimal static decoder.

This oracle consequence concerns one resource: acquired column count. Connecting it to Cassette requires an explicitly realizable source and plan class, the cost of the known Gram data and catalog, a physical page interpretation, and the relevant execution and composition certificates under MATHS.md. The theorem does not supply those accounts. The earlier finite-word separation permits source-trained static laws within a narrower linear decoder class; neither theorem contains the other. The Haar and quadratic arguments use established mathematical methods. Whether the combined adaptivity result contains a substantive original advance remains a separate open question.
