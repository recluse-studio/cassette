# Finite linear-law catalog for query-adaptive sparse sketches; depends on query_adaptive_atomic_dual.md, MATHS.md, q4_adaptive_consequence_audit.md.

Status: proved bridge inside the abstract encoded-column model. It is not a
finite-word resource bound, a physical-page theorem, or a Cassette
sufficiency claim.

## Theorem

Let \(G\succ0\) be real symmetric or complex Hermitian, and let
\(1\le s\le q\). For every \(\varepsilon>0\), there is a finite catalog
of laws \(\mathscr L^1,\ldots,\mathscr L^K\) on linear maps
\(L:\mathbb F^q\to\mathbb F^q\) such that:

1. every outcome \(L\) has at most \(s\) nonzero rows;
2. every catalog law is unbiased as an operator, \(\mathbb EL=I\); and
3. after seeing \(x\ne0\), one catalog law can be selected with

\[
 \mathbb E\,(Lx-x)^*G(Lx-x)
 \le\bigl(\Psi_s(G)+\varepsilon\bigr)\|x\|_2^2.
\tag{1}
\]

Consequently, if \(P^*P=G\), the answer \(PLx\) is an unbiased sum of at
most \(s\) columns of \(P\) and has the same bound in output norm.

The theorem converts the query-dependent stochastic vector in the
definition of \(\Psi_s\) into a finite catalog of query-independent linear
laws. The *selection* remains query-dependent.

## Proof

It suffices to consider \(\|x_0\|_2=1\). Choose a legal law for a random
vector \(Y\) with

\[
 \mathbb EY=x_0,\qquad \|Y\|_0\le s\quad\hbox{a.s.},
 \qquad
 \mathbb E(Y-x_0)^*G(Y-x_0)
 \le\Psi_s(G)+\varepsilon/8.
\tag{2}
\]

There is a finite law with no larger risk. Label each outcome by one
size-\(s\) set containing its support; this is possible because \(s\le q\).
Discard labels of probability zero. Conditional on each remaining label
\(S\), replace \(Y\) by its conditional mean \(y_S\). It remains supported
in \(S\), preserves the total mean, and cannot increase the quadratic risk
by Jensen's inequality. Thus there are finitely many pairs \((p_\alpha,
S_\alpha,y_\alpha)\), with \(|S_\alpha|=s\), which satisfy (2).

Mix this law with weight \(\delta>0\) with uniform exact-size sampling:
choose every \(s\)-subset \(T\subseteq[q]\) with probability
\(\binom qs^{-1}\), and return \(D_Tx_0\), where

\[
 D_T={q\over s}\operatorname{Diag}(1_T).
\tag{3}
\]

The uniform component has mean \(x_0\), finite risk, and gives every
coordinate a positive marginal. Choosing \(\delta\) sufficiently small
makes the mixed law's risk at \(x_0\) at most
\(\Psi_s(G)+\varepsilon/4\). Its finitely many outcomes, indexed by
\(\alpha,S_\alpha,y_\alpha,p_\alpha)\), can again be merged within a common
label by Jensen; zero-probability outcomes are removed. Every exact-size
subset still has positive total probability because of the uniform mixture.

Let

\[
 \theta_i=\sum_\alpha p_\alpha 1_{i\in S_\alpha}>0,
 \qquad
 D_{S_\alpha}=\operatorname{Diag}(1_{S_\alpha}/\theta).
\tag{4}
\]

For each outcome define

\[
 L_\alpha=D_{S_\alpha}+
 (y_\alpha-D_{S_\alpha}x_0){x_0^*\over\|x_0\|_2^2}.
\tag{5}
\]

All rows of \(L_\alpha\) outside \(S_\alpha\) vanish. Moreover,

\[
 L_\alpha x_0=y_\alpha,
 \qquad
 \sum_\alpha p_\alpha D_{S_\alpha}=I,
 \qquad
 \sum_\alpha p_\alpha L_\alpha=I.
\tag{6}
\]

The last equality uses \(\sum p_\alpha y_\alpha=x_0\). Thus (5) is an
operator-unbiased, row-\(s\)-sparse law whose risk at \(x_0\) is the mixed
law's risk.

For this fixed law, put

\[
 r_{x_0}(x)=
 \mathbb E\,(Lx-x)^*G(Lx-x).
\tag{7}
\]

This is a continuous quadratic form in \(x\) and
\(r_{x_0}(x_0)\le\Psi_s(G)+\varepsilon/4\). Therefore an open neighborhood
\(U_{x_0}\) of \(x_0\) on the unit sphere satisfies
\(r_{x_0}(x)\le\Psi_s(G)+\varepsilon/2\). The unit sphere is compact, so
finitely many such neighborhoods cover it. Their laws are the requested
catalog. For arbitrary nonzero \(x\), use homogeneity; for \(x=0\), return
zero.

The construction is unchanged over \(\mathbb C\): the rank-one term in
(5) uses the Hermitian row \(x_0^*\), Jensen applies to the real convex
quadratic form, and all identities in (6) are complex-linear expectation
identities.

## Exact rational perturbation of a finite catalog

The preceding catalog can be approximated by an exactly unbiased rational
catalog without preserving its special form (5). This is useful only under
an exact rational-arithmetic model; it is not a floating-point result.

Fix one catalog law and retain the uniform-mixture outcomes, so every
size-\(s\) subset occurs with positive probability. Approximate its positive
masses by positive rationals \(\widehat p_\alpha\) summing to one. Let
\(\widehat\theta\) be the resulting rational marginal vector and write

\[
 \widehat L_\alpha=
 \operatorname{Diag}(1_{S_\alpha}/\widehat\theta)+H_\alpha.
\tag{8}
\]

Choose row-supported rational approximations to
\(L_\alpha-\operatorname{Diag}(1_{S_\alpha}/\widehat\theta)\). They need
not yet have zero weighted mean. For every row
index \(i\), choose one retained uniform outcome \(\alpha(i)\) with
\(i\in S_{\alpha(i)}\). If

\[
 E=\sum_\alpha\widehat p_\alpha H_\alpha,
\]

replace row \(i\) of \(H_{\alpha(i)}\) by that row minus
\(E_{i:}/\widehat p_{\alpha(i)}\). This correction is rational, stays in
an allowed row, and makes \(\sum\widehat p_\alpha H_\alpha=0\). Hence

\[
 \sum_\alpha\widehat p_\alpha\widehat L_\alpha=I
\tag{9}
\]

exactly. Rational entries are dense over \(\mathbb R\), and
\(\mathbb Q+i\mathbb Q\) is dense over \(\mathbb C\). By making the initial
approximations sufficiently close, the correction and every catalog risk
change uniformly on the unit sphere by an arbitrarily small amount. Keeping
that change below \(\varepsilon/2\) preserves (1) on the finite cover. This
argument handles zero masses by discarding
them before the uniform mixture; positive full coordinate coverage is then
provided by that mixture.

## Resource boundary

The theorem proves existence of a finite catalog, not a cheap one. A direct
representation stores each law's subset outcomes, probabilities, and up to
\(s q\) coefficients per outcome; it also needs a selector for its finite
sphere cover. Selecting the least risk law requires evaluating the stored
quadratic forms in (7), unless another selector is proved. Random-bit cost,
catalog bit length, transform workspace, and page grouping are absent from
this proof.

This is exactly the accounting boundary in MATHS: query-dependent sampling
needs its own metadata and scheduling account (`MATHS.md:494-511`), and
abstract sampled columns become physical traffic only after a declared
conversion (`MATHS.md:491-492`). It does, however, remove one possible
bridge objection: query dependence does not require a continuously indexed
family of stochastic laws for a fixed positive-definite \(G\).

## Repeated q=4 blocks

If a q=4 two-column law has worst-query variance \(v_\eta\), its direct
sum over \(m\) independent diagonal blocks gives an upper bound

\[
 \Psi_{2m}(G_\eta^{\oplus m})\le v_\eta.
\tag{10}
\]

Indeed, select one two-sparse law per block and concatenate their outputs;
the support is at most \(2m\), the mean is the whole query, and block
orthogonality adds the risks. This is only a product upper construction. An
identical block catalog need not be materialized as \(K^m\) joint laws: its
coefficients can be shared, while the selector runs separately in each
block. For fixed \(\eta\), that leaves the block-law coefficients
independent of \(m\), plus declared block layout and addressing, which cost
\(O(m)\) in general or \(O(\log m)\) for a regular partition. The query
work is \(O(mK)\) and the support bound is \(2m\).

It still gives no lower bound after a global basis may mix the blocks and
does not control \(\Psi_2\) for the \(4m\)-coordinate instance. Thus
repeated blocks do not by themselves produce the growing description-aware
frontier identified in `q4_adaptive_consequence_audit.md`.
