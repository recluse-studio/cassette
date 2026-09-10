# fixed_projector_volume_sampling_prior_work.md — primary-source check for volume-sampled projector reconstruction used in the sparse-kernel upper bound; depends on ../notes/fixed_projector_sparse_kernel_order_r_upper.md.

# Volume sampling as an established ingredient

## Scope and verdict

This is a bounded provenance check for the volume-sampled high-space law in
`fixed_projector_sparse_kernel_order_r_upper.md`.  The two required identities
are established consequences of fixed-size volume sampling.  They are not new
ingredients of the fixed-projector dichotomy.

The source checked was:

* Michał Dereziński and Manfred K. Warmuth, [*Reverse Iterative Volume
  Sampling for Linear Regression*](https://jmlr.csail.mit.edu/papers/volume19/17-781/17-781.pdf),
  *Journal of Machine Learning Research* 19 (2018), Theorems 5 and 6 and their
  proofs.  The companion preprint is [*Unbiased estimates for linear regression
  via volume sampling*](https://arxiv.org/abs/1705.06908).

The paper treats a full-column-rank tall matrix \(X\in\mathbb R^{q\times k}\),
and samples exactly \(s\geq k\) rows with probability proportional to
\(\det(X_S^*X_S)\).  It proves unbiasedness of the sampled pseudoinverse
(Theorem 5).  Its Theorem 6 gives an exact inverse-second-moment formula when
every size-\(s\) subset has positive volume, and a positive-semidefinite upper
bound when some subsets have zero volume.

This note does not assess the novelty of the combined sparse-kernel upper
bound, the support-event lower bound, or the proposed dichotomy.  It only
identifies the imported matrix facts.

## Exact correspondence

Let \(P=A^*A\in\mathbb R^{q\times q}\), where

\[
A\in\mathbb R^{k\times q},\qquad AA^*=I_k.
\]

Put \(X=A^*\in\mathbb R^{q\times k}\).  Thus \(X^*X=I_k\), and a
size-\(k\) volume sample has law

\[
 \Pr\{S\}=\det(A_S)^2,\qquad |S|=k,\quad \det A_S\ne0.
\tag{1}
\]

Cauchy--Binet normalizes (1), since

\[
 \sum_{|S|=k}\det(A_S)^2=\det(AA^*)=1.
\]

For a sampled basis \(S\), write

\[
 H_S=E_SA_S^{-1}A.
\tag{2}
\]

The row-selection convention in the source gives

\[
 (I_SX)^+=A_S^{-*}E_S^*,\qquad
 H_S=\bigl(X(I_SX)^+\bigr)^*.
\tag{3}
\]

Theorem 5 of Dereziński--Warmuth says

\[
 \mathbb E\,(I_SX)^+=X^+.
\]

Taking adjoints after left multiplication by \(X\), and using \(XX^*=P\),
therefore yields the required projector reconstruction:

\[
 \boxed{\mathbb E H_S=P.}
\tag{4}
\]

No full-spark hypothesis enters (4).  A singular coordinate \(k\)-set has
zero determinant and hence zero probability; the random inverse in (2) is
only evaluated on bases.  At least one such basis exists because \(A\) has row
rank \(k\).

## The second-moment bound and its equality condition

For \(y=Ax\), (2) gives

\[
 \|H_Sx\|_2^2
 =y^*A_S^{-*}A_S^{-1}y.
\tag{5}
\]

At \(s=k\), Theorem 6 of the checked source specializes, because \(X^*X=I_k\),
to

\[
 \mathbb E\,[A_S^{-*}A_S^{-1}]\preceq(q-k+1)I_k.
\tag{6}
\]

Consequently,

\[
 \boxed{\mathbb E\|H_Sx\|_2^2
 \leq(q-k+1)\|Ax\|_2^2
 =(q-k+1)\|Px\|_2^2.}
\tag{7}
\]

If every coordinate \(k\)-subset is a basis, equivalently every size-\(k\)
subset has positive volume, the source's equality formula applies and (6)--(7)
are equalities for every \(x\).  If some subsets are singular, its stated
replacement is the one-sided semidefinite inequality (6).  Thus full spark is
needed only for exact equality, not for the upper bound used in the fixed-
projector construction.

The result is real as stated in the checked paper.  The algebraic identities
extend verbatim to a complex matrix with adjoints and squared moduli in (1),
but that extension was not needed for the present real fixed-projector notes.

## What the source does and does not supply

The primary result arises in least-squares regression and calls (4) an
unbiased pseudoinverse estimator.  Under (3), it is precisely the high-space
random linear law required here; it already has hard support size \(k\).
It does not supply the sparse null-law, the query-adaptive selector, or either
side of the fixed-projector order dichotomy.  Those remain separate arguments.

No claim about the novelty or consequential significance of the full
dichotomy follows from this bounded source check.
