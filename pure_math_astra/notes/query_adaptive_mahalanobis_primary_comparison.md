# Query-adaptive hard-cap Mahalanobis sparsification: primary-source comparison

Status: bounded source and convex-geometry review. It does not make a novelty
finding. The problem is

\[
 \Psi_s(G)=\sup_{\|x\|_2=1}\
 \inf_{\substack{\mathbb EY=x\\\|Y\|_0\le s\ \mathrm{a.s.}}}
 \mathbb E (Y-x)^*G(Y-x),\qquad G\succ0.
\tag{1}
\]

The law is allowed to depend on \(x\). This differs materially from a fixed
random operator or a fixed inclusion law serving every query.

## Verified reduction: this is an atomic support-gauge problem

For each coordinate set \(S\) with \(|S|\le s\), let

\[
 \mathcal A_{S,G}=\{z:\operatorname{supp}z\subseteq S,\ z^*Gz\le1\},
 \qquad
 \mathcal A_{s,G}=\bigcup_{|S|\le s}\mathcal A_{S,G},
\]

and let \(\|\cdot\|_{s,G}\) be the gauge of
\(\operatorname{conv}\mathcal A_{s,G}\). Then, for every fixed \(x\),

\[
 \inf_{\substack{\mathbb EY=x\\\|Y\|_0\le s\ \mathrm{a.s.}}}
 \mathbb E(Y-x)^*G(Y-x)
 =\|x\|_{s,G}^2-x^*Gx.
\tag{2}
\]

This is elementary convex analysis, but it identifies exactly which existing
objects are relevant. Condition any law on its support and replace each
conditional law by its conditional mean; strict convexity of \(z^*Gz\)
makes this non-worse. Write the atom probabilities as \(p_S\) and
\(z_S=p_S\mathbb E[Y\mid S]\). The second moment becomes

\[
 \sum_S\frac{z_S^*Gz_S}{p_S},\qquad \sum_Sz_S=x,\quad\sum_Sp_S=1.
\]

For a fixed decomposition \(x=\sum_Sz_S\), minimizing in \(p_S\) gives
\(p_S\) proportional to \(\sqrt{z_S^*Gz_S}\), and the value

\[
 \left(\sum_S\sqrt{z_S^*Gz_S}\right)^2.
\]

Taking the infimum over decompositions is precisely the square of the atomic
gauge. Subtract \(x^*Gx\), using unbiasedness, to obtain (2). The same proof
works over \(\mathbb C\), with Hermitian quadratic forms.

For \(G=I\), \(\|\cdot\|_{s,G}\) is the usual \(s\)-support norm. For a
positive diagonal \(D\), coordinate scaling preserves support, hence

\[
 \|x\|_{s,D}=\|D^{1/2}x\|_{s,I}.
\tag{3}
\]

For a nondiagonal Gram matrix, whitening sends coordinate-sparse atoms to
the dictionary \(\{G^{1/2}z:\|z\|_0\le s\}\); it does not preserve the
coordinate hard cap. Thus (2) is a general-dictionary atomic gauge, not a
standard diagonal \(s\)-support norm after a legal coordinate change.

## Direct relation to a fixed-law operator ideal

Let \(\nu_s(G)\) denote the optimum worst-query covariance of any
query-independent legal coordinate-sparse unbiased random operator in the
same basis. Every such operator produces a legal law \(Y_x\) for each fixed
\(x\). Therefore

\[
 \Psi_s(G)\le \nu_s(G).
\tag{4}
\]

This is only the minimax inequality: adapting after observing \(x\) is no
worse than committing beforehand. It is not a factor theorem. A reverse
inequality would have to control the cost of replacing the family of
query-specific atomic decompositions in (2) by one common law. None of the
sources read supplies that replacement. Grothendieck inequalities do not
apply directly: they compare a bilinear sign program to a vector relaxation,
whereas (2) is a convex-envelope/atomic-gauge problem with a query-indexed
probability law and a quadratic objective.

## Primary comparison matrix

| Source read | Exact theorem or scope read | What it covers | What it does not settle here |
|---|---|---|---|
| J. Weare and R. J. Webber, *Randomly Sparsified Richardson Iteration: A Dimension-Independent Sparse Linear Solver*, Communications on Pure and Applied Mathematics 79 (2026), 89–122, [DOI](https://doi.org/10.1002/cpa.70012) | Proposition 5.2, section 5.2: for every fixed complex vector \(v\), pivotal sparsification has at most \(m\) nonzeros, is unbiased, and minimizes Euclidean squared error among all unbiased \(m\)-sparse random vectors. Its proof conditions on the support and optimizes inclusion probabilities. | This is a direct exact precursor for the *per-query*, Euclidean, hard-cap problem. It validates the conditional-mean reduction used in (2), rather than merely providing a heuristic sampler. | It fixes the Euclidean metric and a given vector. It has no positive nondiagonal Mahalanobis metric, no supremum over unit queries, no basis/ispectral optimization, and no comparison with a query-independent operator law. |
| L. Barnes et al., *Efficient Unbiased Sparsification*, arXiv:2402.14925v2, [primary HTML](https://arxiv.org/html/2402.14925v2) | Definitions I.2–I.3 and Lemma 1 reduce a convex divergence to facet-concentrated laws; Lemma 2 and later results characterize classes that are additively separable or permutation invariant. | The concentration reduction applies in spirit to a convex quadratic loss. It establishes a close literature frame for optimizing a query-dependent sparse law. | \(y^*Gy\) is additively separable only when \(G\) is diagonal, and it is permutation invariant only in the scalar case. The paper does not solve the nonseparable positive-Gram problem, its unit-query minimax, or an isospectral basis choice. Its stated scope, not merely an “open Mahalanobis” sentence, leaves the present core outside its theorems. |
| H. Wang, S. Sievert, Z. Charles, S. Liu, D. Papailiopoulos, S. Wright, *ATOMO: Communication-Efficient Learning via Atomic Sparsification*, NeurIPS 2018, [primary paper](https://proceedings.neurips.cc/paper_files/paper/2018/file/33b3214d792caf311e1f00fd22b392c5-Paper.pdf) | Sections 2–4 and Theorem 4: given one atomic decomposition and an input gradient, it chooses inclusion probabilities to minimize variance in the specified inner-product norm under an expected sparsity budget. It explicitly compares coordinate and SVD atomic decompositions. | This is prior art for variance-optimal unbiased atomic sparsification and for a change of atomic decomposition improving variance. It is the closest warning against presenting “a better basis can reduce variance” as new. | ATOMO uses a fixed input, a selected decomposition, and an expected support budget with independent Bernoulli selectors. It does not optimize all hard-cap laws, a worst-query supremum, a rotation of a fixed physical coordinate-read system, or a common versus query-adaptive law gap. It also prices atomic communication differently across decompositions, which reinforces rather than removes the representation issue. |
| A. Argyriou, R. Foygel, N. Srebro, *Sparse Prediction with the k-Support Norm*, NeurIPS 2012, [primary paper](https://papers.neurips.cc/paper/4537-sparse-prediction-with-the-k-support-norm.pdf) | Section 2 and Definition 2.1: the \(k\)-support unit ball is the convex hull of \(k\)-sparse Euclidean unit vectors; its gauge has an infimal decomposition formula and its dual is the Euclidean norm of the largest \(k\) entries. | It is the exact convex geometry behind (2) for \(G=I\), and it gives correct terminology for the diagonal/scaled case. | It is a deterministic regularization result. It neither treats a nondiagonal metric with fixed coordinate sparsity nor an unbiased random estimator, a minimax-over-query criterion, or basis selection. |

## What this says about the proposed basis reversal

The claim that a nonscalar diagonal spectrum can admit an isospectral pair
rotation with

\[
 \Psi_s(V^*DV)<\Psi_s(D)
\]

is not a direct corollary of the sources above.

* Weare--Webber solve the inner infimum only for the Euclidean metric.
* Barnes does not cover the off-diagonal quadratic coupling.
* ATOMO makes an atomic decomposition choice useful for one input and a
  different communication model, but stops before the worst-query,
  hard-cap, isospectral minimax problem.
* The \(k\)-support norm identifies the Euclidean convex hull, while a pair
  rotation changes the dictionary geometry in (2).

The candidate's proposed linear decrease is therefore a substantive
mathematical statement if its \(q=4,s=2\) derivation is correct. It would
need a direct proof from (2), or an exact finite-dimensional support-law
calculation. It cannot be accepted merely as an instance of choosing a
better atomic basis, because that broader fact is already in ATOMO.

Conversely, this review has not found a primary theorem that rules out a
general minimax/factorization reduction. No originality conclusion follows
from that limited search.

## Consequential boundary

Equation (2) is a query-specific estimator result. To use it for Cassette,
a plan still has to declare how a query selects its support law, how the
selected coordinates are read, whether the basis transform is resident, and
how transform bytes, sampling metadata, and execution are charged. The
comparison with a query-independent operator ideal is mathematically valid
in (4), but says nothing by itself about traffic or total storage.

## Source-access limits

Weare--Webber was read in the open publisher full text; Barnes in its
author-hosted arXiv HTML; ATOMO in the official NeurIPS PDF; and
Argyriou--Foygel--Srebro in the accessible primary PDF. This bounded pass
did not locate a primary factorization or Grothendieck theorem that states a
dimension-free comparison between (1) and a fixed sparse-operator minimax
value. That is a source-access limit, not evidence that such a theorem is
absent.
