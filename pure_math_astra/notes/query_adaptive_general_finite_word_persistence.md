# Finite-word persistence for the real query-adaptive reversal — rational catalog realization; depends on query_adaptive_general_basis_reversal.md, encoded_column_rounding_bound.md, MATHS.md.

Status: a finite rational realization of the strict local theorem in
`query_adaptive_general_basis_reversal.md`. It is a mathematical and
resource-accounting lemma. It does not establish a native floating-point
execution certificate, physical-page traffic, or a Cassette acceptance row.

## 1. Risk is continuous in a finite HT catalog

For an exactly-\(s\) subset law \(\mu\) on \([q]\), let

\[
 \theta_i=\sum_{S\ni i}\mu_S,
 \qquad
 A_S(\theta)=\operatorname{Diag}(1_{i\in S}/\theta_i)-I.
\tag{1}
\]

The HT estimator for query \(x\) has risk

\[
 \mathcal R(G,\mu;x)=x^TC(G,\mu)x,
 \qquad
 C(G,\mu)=\sum_{|S|=s}\mu_S A_S(\theta)^T G A_S(\theta).
\tag{2}
\]

This formula includes all pair-inclusion terms. It does not replace them
by a diagonal covariance expression.

Fix \(\rho>0\). On the set

\[
 \|G\|_{\mathrm{op}}\le M,
 \qquad \theta_i\ge\rho\quad(i\in[q]),
\tag{3}
\]

the right side of (2) is uniformly continuous in \((G,\mu)\). This is
immediate from its finite sum: each entry is a polynomial in \(G\) and
the masses, divided only by products of marginals bounded below by
\(\rho\). For a catalog \(\boldsymbol\mu=(\mu^1,\ldots,\mu^N)\), define

\[
 F(G,\boldsymbol\mu)=
 \max_{\|x\|_2=1}\min_{1\le\ell\le N}
 \mathcal R(G,\mu^\ell;x).
\tag{4}
\]

The maximum is over a compact sphere and the minimum is finite. Hence
\(F\) is uniformly continuous on (3), provided every catalog marginal is
at least \(\rho\).

The spectral water level \(t_s(G)\), defined by

\[
 \sum_{j=1}^q {\lambda_j(G)\over \lambda_j(G)+t}=s,
\tag{5}
\]

is continuous on the positive-definite cone for \(1\le s<q\). Eigenvalues
are continuous and the strictly decreasing left side has a unique positive
root. These observations give the following persistence statement.

> **Finite-catalog persistence lemma.** Suppose \(G_0\succ0\) and a
> finite exactly-\(s\) HT catalog \(\boldsymbol\mu_0\), with all
> marginals positive, obey
> \[
> F(G_0,\boldsymbol\mu_0)\le t_s(G_0)-\gamma
> \tag{6}
> \]
> for some \(\gamma>0\). There is a neighborhood \(\mathcal U\) of
> \((G_0,\boldsymbol\mu_0)\) such that every \((G,\boldsymbol\mu)\in
> \mathcal U\) obeys
> \[
> F(G,\boldsymbol\mu)\le t_s(G)-\gamma/3.
> \tag{7}
> \]

To prove it, choose the neighborhood so that the changes in \(F\) and in
\(t_s\) are each at most \(\gamma/3\). Equation (7) follows from (6).
The constants \(1/3\) are inessential; their purpose is to make the
strict slack explicit.

## 2. Rational fixed-size laws and rational HT coefficients

Apply the lemma to the \(q+2\)-law strict catalog in
`query_adaptive_general_basis_reversal.md`.

First choose a rational point \(\widehat p\) on the affine hypersimplex
\(\sum_i\widehat p_i=s\), arbitrarily close to its real interior point
\(p\). Choose a positive rational transfer size \(\widehat\zeta\) small
enough that

\[
 \widehat\theta^k=
 \widehat p+\widehat\zeta(f_k-q^{-1}\mathbf1)
\tag{8}
\]

has every coordinate in \((0,1)\). These are the `q` transfer-law
marginals. They are rational and sum exactly to \(s\).

The uniform-shift construction from the general theorem then supplies an
exactly-\(s\) law with those marginals. With rational cumulative endpoints,
partitioning \([0,1)\) at all endpoints makes the selected subset constant
on finitely many half-open intervals. Their lengths are rational. Thus the
apparently continuous shift is equivalent to a finite rational subset law;
it has rational probabilities and rational HT weights
\(1/\widehat\theta_i^k\).

For either pair law, take its at-most-\(q+1\)-atom real decomposition from
the general theorem and replace its positive masses by nearby nonnegative
rationals summing exactly to one. Its marginals and selected-pair moment
become rational and remain arbitrarily close to the original ones. The
support cap remains exactly \(s\). This already gives a rational law close
enough for the persistence lemma.

Equivalently, the moment polytope is the convex hull of finitely many
integer subset-moment vectors. A rational point represented using an
affinely independent set of at most \(q+1\) such vectors has rational
barycentric coordinates. This gives rational pair laws with the same
\(q+1\)-atom bound whenever one chooses a rational moment point in that
simplex. No irrational probability or irrational HT coefficient is needed.

All rational approximations can be chosen sufficiently close that the
catalog satisfies (7) at the original \(G_0\). The strict gap, rather than
an exact formula for its size, is what permits this replacement.

## 3. A rational source family with no eigenbasis oracle

Choose distinct positive rationals \(d_1,\ldots,d_q\), set

\[
 R_0=\begin{pmatrix}\operatorname{Diag}(d_1,\ldots,d_q)\\0\end{pmatrix}
 \in\mathbb Q^{m\times q}\quad(m\ge q),
 \qquad D=R_0^TR_0=\operatorname{Diag}(d_i^2),
\tag{9}
\]

and choose a nonzero sufficiently small rational plane rotation \(Q\).
For example, a rational \(z\) gives

\[
 \cos\tau={1-z^2\over1+z^2},\qquad
 \sin\tau={2z\over1+z^2}.
\tag{10}
\]

Use the plane joining a largest and a smallest diagonal entry, as in the
general theorem. Store

\[
 P_0=R_0Q^T\in\mathbb Q^{m\times q},\qquad z_x=Qx.
\tag{11}
\]

Then \(P_0z_x=R_0x\), while

\[
 P_0^TP_0=QDQ^T=G_0.
\tag{12}
\]

The strict theorem and Section 2 therefore give an entirely rational
payload, rational subset probabilities, and rational HT coefficients with
strict risk below \(t_s(G_0)\). The water level itself can be irrational;
it is an analytical comparator, not data that the sampler must encode,
compute, or use at runtime.

This construction extends to an open real neighborhood. Keep the rational
plane rotation \(Q\) and rational catalog fixed. For every source \(R\)
near \(R_0\), use \(P=RQ^T\). Its encoded Gram matrix
\(Q R^TR Q^T\) stays near \(G_0\), so the persistence lemma gives

\[
 F(QR^TRQ^T,\widehat{\boldsymbol\mu})
 <t_s(QR^TRQ^T).
\tag{13}
\]

For every rational \(R\) in that neighborhood, \(P\), the transformed
query, the catalog, and every HT weight remain rational. Under exact
rational arithmetic, the random returned vector has mean exactly \(Rx\).
Individual sampled outputs need not equal \(Rx\). The set of rational
sources is not itself open; the correct statement is an open real
neighborhood whose rational points form a dense finite-word subfamily. No
source-specific eigendecomposition is used in (13).

## 4. The linear-time selector also persists

Continuity of \(F\) alone only proves that some catalog minimizer exists.
The score selector from the real theorem requires a separate argument.
Choose numbers

\[
 0<u_-<u_+<w_iw_j,
\tag{14}
\]

where \(i,j\) are the extreme rotated coordinates. The pair-law argument
has a uniform strict gap on \(|x_ix_j|\ge u_-\). On the compact region
\(|x_ix_j|\le u_+\), the original score spread

\[
 \Delta(x)=\max_r {a_rx_r^2\over p_r^2}
              -\min_r {a_rx_r^2\over p_r^2}
\tag{15}
\]

has a positive minimum \(\Delta_+\). Choose a rational threshold
\(h\in(u_-,u_+)\). The finite selector uses a pair law when
\(|x_ix_j|\ge h\), choosing its sign from the rational off-diagonal entry,
and otherwise uses a transfer law.

For the rational transfer catalog, define the rational scores

\[
 \widehat e_r(x)={\widehat a_r x_r^2\over\widehat p_r^2}.
\tag{16}
\]

Uniform approximation makes \(|\widehat e_r-e_r|\le e\) on the unit
sphere. Choosing \(e<\Delta_+/4\), an index maximizing \(\widehat e_r\)
has original score within \(2e\) of the original maximum. Equivalently,
the rational score spread is at least \(\Delta_+-2e>0\) on the transfer
branch. The first derivative of its rational transfer risk is therefore
at most

\[
 -{\Delta_+-2e\over q}.
\tag{17}
\]

Choose the positive rational transfer size small enough that the uniformly
bounded second derivative leaves half this gap. Uniform perturbation of
the finitely many law risks then preserves both branch gaps. Thus the
finite rational realization retains the stated \(O(q)\) score evaluation,
one threshold comparison, and one sign test. This argument is only about
exact field arithmetic and catalog selection; it makes no floating-point
claim.

## 5. What the finite realization costs and what it does not prove

The encoded payload has exactly \(mq\) scalar entries. Every catalog law
chooses exactly \(s\) columns, so the abstract individually addressable
column model reads exactly \(ms\) payload scalars per query before page
grouping. The rational plane transform in (11) changes two query
coordinates; its arithmetic and its two rational parameters are metadata,
not fresh-column traffic.

The two pair laws store at most \(2(q+1)\) subset identities and rational
probabilities. The transfer laws need only store \(\widehat p\),
\(\widehat\zeta\), and the selected index \(k\); their fixed-size sampler
is generated from rational cumulative intervals rather than from \(q\)
stored probability tables. The selector still evaluates \(q\) scalar
scores, as in the general theorem. Bit lengths, random-bit generation,
transform workspace, query arithmetic, physical page reads, and the
separate peak and total metadata accounts remain declared resource fields
under MATHS.md; this lemma does not turn the \(ms\) abstract count into a
physical-traffic bound.

The result is exact only in a rational arithmetic model. If source entries,
the query transform, or execution are rounded, the returned mean is toward
the represented rational source and the bias-inclusive bound in
`encoded_column_rounding_bound.md` is required. No native floating-point
claim follows from this finite-word persistence lemma.
