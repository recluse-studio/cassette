# Growing direct sums: adaptive hard caps versus global fixed linear laws

Status: the direct-sum upper bound and fixed-linear lower bound are proved.
They concern a complex query-adaptive coordinate-sparsification model. They
do not supply a finite-byte resident description, a physical read bound, or
a description-aware resource separation.

Let

\[
 H_\eta=\mathbf1\mathbf1^*+\eta I_4,\qquad
 G_{m,\eta}=\operatorname{Diag}(H_\eta,\ldots,H_\eta)
 \quad(m\text{ copies}),
\tag{1}
\]

where \(\eta>0\). The global dimension is \(q=4m\) and the hard support
cap is \(s=2m\). All query and estimator vectors in this note are complex.
The one-block result already proved in
`query_adaptive_complex_water_counterexample.md` is that, for all
sufficiently small \(\eta\),

\[
 \Psi_{2,\mathbb C}(H_\eta)\le c\eta,
 \qquad c={1999\over1000}.
\tag{2}
\]

## Direct-sum adaptive upper bound

More generally, for positive definite block Grams \(G_b\) and nonnegative
integer caps \(s_b\),

\[
 \Psi_{\sum_b s_b}\!\left(\bigoplus_bG_b\right)
 \le\max_b\Psi_{s_b}(G_b).
\tag{3}
\]

For a query \(x=(x_b)_b\), take in block \(b\) a law with mean \(x_b\),
support at most \(s_b\), and risk at most
\(\Psi_{s_b}(G_b)\|x_b\|_2^2\). This follows from the homogeneity of the
one-query optimization. Concatenate the independent block outputs. The
result has exact mean \(x\), support at most \(\sum_bs_b\), and, because
its Gram is block diagonal, risk

\[
 \sum_b\mathbb E(Y_b-x_b)^*G_b(Y_b-x_b)
 \le\sum_b\Psi_{s_b}(G_b)\|x_b\|_2^2.
\tag{4}
\]

For a unit query, (4) is at most the right side of (3). Independence is
convenient for constructing the joint law but is not needed for the displayed
risk identity.

Applying (3) with every \(s_b=2\) and (2) gives

\[
 \boxed{\quad
 \Psi_{2m,\mathbb C}(G_{m,\eta})\le {1999\over1000}\eta
 \quad}
\tag{5}
\]

for every \(m\) in the same sufficiently-small-\(\eta\) range as (2).
The bound is uniform in \(m\), so it also applies to any chosen growth
schedule \(m=m(\eta)\).

## What global cross-block support allocation can change

The converse of (3) is false. When \(m\ge2\), a query supported entirely
in one four-coordinate block may be returned deterministically: the global
cap \(2m\) permits all four of its coordinates. Therefore block-supported
queries do not prove
\(\Psi_{2m}(G_{m,\eta})\ge\Psi_2(H_\eta)\).

For one fixed query, the exact inverse-hull representation makes the
remaining coupling explicit. For every global support \(S\), write
\(S_b\) for its coordinates in block \(b\), and put

\[
 K_S=\bigoplus_{b=1}^m
 E_{S_b}(H_\eta)_{S_bS_b}^{-1}E_{S_b}^*.
\tag{6}
\]

Then the query risk is exactly

\[
 \phi_{G_{m,\eta}}(x)=
 \inf_{\alpha}
 \left[x^*\left(\sum_{|S|\le2m}\alpha_SK_S\right)^\dagger x
       -x^*G_{m,\eta}x\right],
\tag{7}
\]

with the usual range condition. Each mixture matrix in (7) is block
diagonal, but the common distribution \(\alpha\) couples its block
components through \(|S|\le2m\) on every outcome. This is the exact
location of possible cross-block allocation gains. Equation (7) does not
reduce to a maximum or sum of the one-block values.

## A global fixed-linear lower bound that allows allocation

Define \(\nu_s(G)\) as the optimum worst-query covariance among all
query-independent support laws \(\alpha_S\) and all query-independent
linear maps \(L_S\) satisfying

\[
 \operatorname{rowsupp}(L_S)\subseteq S,qquad
 \sum_S\alpha_SL_S=I,qquad |S|\le s.
\tag{8}
\]

The retained coordinates of \(L_Sx\) may depend on the full query \(x\).
Thus this is broader than Horvitz--Thompson thinning, and its supports may
allocate the full global cap across blocks in arbitrary ways.

The inverse-hull reduction gives the optimum in this class as

\[
 \nu_s(G)=
 \inf_{\alpha}\lambda_{\max}\left(M(\alpha)^{-1}-G\right),
 \qquad M(\alpha)=\sum_S\alpha_SK_S,
\tag{9}
\]

where singular mixtures are interpreted by the limiting feasible value.
For every support, \(\operatorname{tr}(GK_S)=|S|\), so

\[
 \operatorname{tr}(GM(\alpha))\le s.
\tag{10}
\]

If the matrix in (9) were at most \(vI\), then
\(M(\alpha)\succeq(G+vI)^{-1}\). Taking the positive \(G\)-trace and
using (10) yields

\[
 s\ge\operatorname{tr}\bigl(G(G+vI)^{-1}\bigr).
\tag{11}
\]

Consequently

\[
 \nu_s(G)\ge t_s(G),
 \qquad
 \operatorname{tr}\bigl(G(G+t_s(G)I)^{-1}\bigr)=s.
\tag{12}
\]

This proof has already allowed global support allocation; no separate
blockwise fixed-law assumption enters it.

For (1), the spectrum has \(m\) copies of \(4+\eta\) and \(3m\) copies
of \(\eta\). With \(s=2m\), the water equation in (12), divided by \(m\),
is

\[
 {4+\eta\over4+\eta+t}+{3\eta\over\eta+t}=2.
\tag{13}
\]

Its positive root is

\[
 t=t_2(H_\eta)=\sqrt{1+4\eta+\eta^2}-1=2\eta+O(\eta^2),
\tag{14}
\]

independent of \(m\). Combining (5), (12), and (14), for all sufficiently
small \(\eta\), proves the strict global-class separation

\[
 \boxed{\quad
 \Psi_{2m,\mathbb C}(G_{m,\eta})
 \le1.999\eta
 <t_2(H_\eta)
 \le\nu_{2m}(G_{m,\eta}).
 \quad}
\tag{15}
\]

The strict inequality follows from \(t_2(H_\eta)/\eta\to2\). It persists
at every \(m\), including growing \(m\), but the present numerical
constant makes its certified relative gap small.

## Resident descriptions do not follow from the Gram separation

Equation (15) compares two execution classes for a *fixed residual Gram*
and a fixed coordinate layout. It does not compare resident-byte frontiers.
A resident reconstruction \(B\) changes the residual from \(R=A-B\) to a
new matrix, and therefore changes both its Gram and the columns that a
support refers to. The Gram in (1) names neither an atom \(A\), a legal
reconstruction class, nor the bytes needed to reconstruct \(B\).

A precise description-aware class would have to fix an atom \(A\), budgets
\((b_{\rm desc},b_{\rm meta})\), a declared class
\(\mathcal C_{b_{\rm desc},b_{\rm meta}}(A)\), and, if coordinates are
changed, a declared transform class \(\mathcal Q_{b_{\rm meta}}\). Its
abstract one-call value is

\[
 \inf_{\substack{B\in\mathcal C_{b_{\rm desc},b_{\rm meta}}(A)\\
                  Q\in\mathcal Q_{b_{\rm meta}}}}
 \Psi_{2m,\mathbb C}
 \left(Q(A-B)^*(A-B)Q^*\right),
\tag{16}
\]

where the sampler reads at most \(2m\) declared encoded residual columns,
has exact mean in the transformed query coordinates, and all residual
addressing and sampling data are charged. A fixed-linear comparator must be
allowed the same \((B,Q)\) class and byte budgets.

If arbitrary \(B=A\) is allowed, (16) is zero; this consumes whatever
resident description is required and says nothing at a common byte budget.
If a dense diagonalizing \(Q\) is allowed, its representation, query
application, encoded-column layout, and metadata likewise require a
separate charge. Therefore no claim that a resident description removes or
preserves (15) is justified until this class, its byte accounting, and its
source-column access rule are declared.
