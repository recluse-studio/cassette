# k4_dyadic_full_linear_page_accounting.md — exact rational K4 full-linear sampler and conditional original-column page accounting; depends on fixed_projector_sparse_kernel_dichotomy.md, k4_diagonal_and_full_linear_rate_separation.md, rademacher_source_growing_static_adaptive_extension.md, ../../MATHS.md.

# Dyadic K4 full-linear law and fixed-layout page accounting

## Scope

This note makes the $K_4$ full-linear upper law finite and exact.  It then
gives a conditional, one-call page-traffic comparison against diagonal
coefficient laws in a declared original-column format.  It does not establish
a general description frontier, a hardware measurement, or a converse for
decoders that can change the source encoding.

Use edge order

\[
 (12,13,14,23,24,34),
\]

and let $D$ be the oriented $4\times6$ vertex--edge incidence matrix of
$K_4$.  The cut-space projector and cycle-space projector are

\[
 P={1\over4}D^TD,\qquad N=I-P.
\tag{1}
\]

For $r=2^{-\ell}$, with integer $\ell\ge1$, set

\[
 G_r=P+r^2N,\qquad R_\ell=P+rN.
\tag{2}
\]

Thus $R_\ell^TR_\ell=G_r$.  All entries of $R_\ell$ are dyadic.  With
one common denominator $2^{\ell+2}$, their signed numerators have absolute
value below $2^{\ell+2}$: diagonal entries are

\[
 {2^\ell+1\over2^{\ell+1}},
\]

and every nonzero off-diagonal entry is, up to its incidence sign,

\[
 {2^\ell-1\over2^{\ell+2}}.
\tag{3}
\]

## The twenty exact prototype maps

For each of the sixteen spanning trees $T\subset E(K_4)$, define

\[
 H_T=E_T(P_{TT})^{-1}P_{T,:}.
\tag{4}
\]

For each of the four oriented triangular faces $f$, let $c_f\in\{0,1,-1\}^6$
be its raw cycle vector and define

\[
 C_f=c_fc_f^T.
\tag{5}
\]

The following identities are exact:

\[
 {1\over16}\sum_T H_T=P,\qquad
 {1\over4}\sum_fC_f=N.
\tag{6}
\]

The first is the rank-three volume-sampling identity: every tree has

\[
 \det P_{TT}={1\over16}.
\]

The second follows from the raw-cycle tight frame

\[
 \sum_fc_fc_f^T=4N.
\]

There is no hidden irrational arithmetic.  A tree's incidence columns form
a $\mathbb Z$-basis for the cut vector of every edge.  Equivalently,

\[
 H_T\in\{0,1,-1\}^{6\times6}.
\tag{7}
\]

This can also be checked directly from $4P=D^TD$: each tree Gram has
integer adjugate and determinant $4$, and the coordinate of a chord is its
signed fundamental-path vector.  Likewise $C_f\in\{0,1,-1\}^{6\times6}$.
Every one of these twenty maps has exactly three nonzero output rows.

Define twenty $r$-dependent maps by

\[
 L_T^{\rm H}=(1+r)H_T={2^\ell+1\over2^\ell}H_T,
 \qquad
 L_f^{\rm N}={1+r\over r}C_f=(2^\ell+1)C_f.
\tag{8}
\]

Give each high map and low map respectively the probabilities

\[
 \Pr(L_T^{\rm H})={2^\ell\over16(2^\ell+1)},
 \qquad
 \Pr(L_f^{\rm N})={1\over4(2^\ell+1)}.
\tag{9}
\]

Equations (6)--(9) give

\[
 \mathbb E L=I.
\tag{10}
\]

The high-map entries are zero or signed copies of the reduced dyadic fraction

\[
 {2^\ell+1\over2^\ell};
\]

their numerator has $\ell+1$ binary digits.  Low-map entries are integers
of absolute value at most $2^\ell+1$, again with $\ell+1$ binary digits.
All probabilities have common integer denominator

\[
 M=16(2^\ell+1),
\tag{11}

\]

with weights $2^\ell$ for each high map and $4$ for each low map.  For
$\ell\ge1$, $M$ has $\ell+5$ binary digits.

The sharp K4 calculation cited in
`fixed_projector_sparse_kernel_dichotomy.md` applies to this law:

\[
 \lambda_{\max}\mathbb E[(L-I)^TG_r(L-I)]\le7r.
\tag{12}
\]

Thus $R_\ell Lx$ is an unbiased estimate of $R_\ell x$, uses exactly
three selected original columns in every outcome, and has worst-unit-query
mean-square output error at most $7r$.

## A finite binary catalogue and an exact sampler

The catalogue can be named without storing arbitrary reals:

\[
 (\ell,\ \text{lexicographic tree }T\in\mathcal T(K_4),\
 \text{oriented face }f\in\mathcal F(K_4),\ \mathrm H/\mathrm N).
\tag{13}
\]

The fixed prototype table has $20\cdot6\cdot6=720$ entries in
$\{0,1,-1\}$.  A literal two-bit-per-entry serialization uses at most

\[
 1440\ \text{bits}.
\tag{14}
\]

It is a deliberately simple upper bound; a fixed incidence-matrix grammar
and the tree/face enumeration compress it further.  If $\gamma(n)$ denotes
the Elias gamma code, the variable record for $\ell$ uses exactly

\[
 |\gamma(\ell+1)|=2\lfloor\log_2(\ell+1)\rfloor+1
\tag{15}
\]

bits.  A fixed sampler rule and this finite table are shared metadata, not
one record per query or per repeated block.

Here is an exact fair-bit sampler.  Repeatedly draw an $(\ell+1)$-bit
integer $U$ uniformly from $\{0,\ldots,2^{\ell+1}-1\}$, rejecting it if

\[
 U>2^\ell.
\]

If $U<2^\ell$, draw four more fair bits and use them as the tree index.  If
$U=2^\ell$, draw two more fair bits and use them as the face index.  The
accepted branch has $2^\ell+1$ equally likely values, so this realizes
(9) exactly.  Its expected fair-bit use per block is

\[
 b_{\rm rng}(\ell)
 ={(\ell+1)2^{\ell+1}\over2^\ell+1}
 +{4\,2^\ell+2\over2^\ell+1}
 <2(\ell+1)+4.
\tag{16}
\]

The worst-case number of fair bits is unbounded: rejection can recur
arbitrarily often.  This is unavoidable for a bounded fair-bit procedure,
because the low-branch probability $1/(2^\ell+1)$ is non-dyadic.  The
number of rejected trials has tail at most $2^{-j}$ after $j$ trials,
since one trial succeeds with probability

\[
 {2^\ell+1\over2^{\ell+1}}>\frac12.
\tag{17}
\]

An execution contract that has a hard random-bit or latency cap therefore
needs an additional declared randomness primitive or an approximation rule;
(16) is an expected-cost statement only.

## Repeated fixed-layout family

Let

\[
 \mathcal R_{m,\ell}=I_m\otimes R_\ell,
 \qquad q=6m.
\tag{18}

\]

The original columns are indexed in a regular $m$-block layout, six columns
per block.  In every block draw (9) independently and use the corresponding
map.  The product law has mean $I_q$, exactly $3m$ nonzero output rows on
every outcome, and by additivity of the block Gram,

\[
 \sup_{\|x\|_2=1}
 \mathbb E\|\mathcal R_{m,\ell}(Lx-x)\|_2^2
\le7r.
\tag{19}
\]

The expected random-bit count is $m b_{\rm rng}(\ell)$, still with no
finite worst-case bound.  A regular layout needs only the shared prototype
table, $\ell$, and $m$.  Under the literal serialization above, its
variable layout record costs another

\[
 2\lfloor\log_2(m+1)\rfloor+1
\tag{20}
\]

bits for $\gamma(m+1)$, plus a fixed format tag and fixed sampler-rule
description.  It does not require a $20^m$-element joint-law table.

## Diagonal lower bound and page traffic

Consider a diagonal random coefficient law $D$, with $\mathbb ED=I$.
Let $p_i=\Pr(D_{ii}\ne0)$ and let

\[
 \bar s=\mathbb E|\operatorname{supp}D|=\sum_{i=1}^{6m}p_i.
\tag{21}

\]

Suppose its residual Gram obeys the blockwise Loewner lower bound

\[
 G_{\rm res}\succeq
 a\,\bigl(I_m\otimes G_r\bigr),\qquad a>0.
\tag{22}

\]

Since every diagonal entry of $G_r$ is $(1+r^2)/2$, exact mean and
Cauchy--Schwarz imply

\[
 \begin{aligned}
 \lambda_{\max}\mathbb E[(D-I)^TG_{\rm res}(D-I)]
 &\ge {a(1+r^2)\over2}
 \left({6m\over\bar s}-1\right).
 \end{aligned}
\tag{23}
\]

Indeed, $\mathbb E D_{ii}^2\ge1/p_i$, while
$\sum_i p_i=\bar s$; take the trace and use

\[
 \sum_i{1\over p_i}\ge{(6m)^2\over\bar s}.
\]

The same inequality holds if only a hard support cap $s$ is known, by
putting $\bar s\le s$.  Matching the $7r$ bound in (19) therefore
requires

\[
 \bar s\ge
 {6m\over 1+14r/[a(1+r^2)]}.
\tag{24}
\]

For fixed $a>0$, the required expected selected-column count tends to
$6m$ as $r\downarrow0$, whereas (19) always selects $3m$ columns.

Now declare a narrow physical source format.  Store each of the $q=6m$
original columns as one aligned, uncompressed dense page containing all
$q$ real scalar words, regardless of zeros outside its own K4 block.  Let

\[
 B_{\rm page}=qw+h_{\rm page}
\tag{25}

\]

be its fixed page size in bits: $w$ is the exact fixed-width scalar-word
allocation and $h_{\rm page}$ its fixed header.  For the direct dyadic
factor in (18), a shared denominator and signed numerator representation
exists with $w\ge\ell+3$ data bits, before any chosen format overhead.

Declare that the full-linear sampler fetches all three pages named by its
selected tree or face before evaluating whether a resulting coefficient
cancels.  It then reads exactly

\[
 T_{\rm full}=3mB_{\rm page}
\tag{26}

\]

fresh page bits on every outcome.  For the diagonal comparison choose a query
having no zero coordinates.  Then every selected nonzero diagonal coefficient
needs its corresponding original page.  A diagonal law satisfying the same
risk bound has expected fresh page traffic at least

\[
 T_{\rm diag}\ge
 {6m\over1+14r/[a(1+r^2)]}\,B_{\rm page}.
\tag{27}

\]

Thus, in this explicitly padded page format,

\[
 {T_{\rm diag}\over T_{\rm full}}
 \ge {2\over1+14r/[a(1+r^2)]}
 \longrightarrow2.
\tag{28}
\]

This is an exact one-call expected-traffic comparison under the stated
format.  The source payload itself is $6mB_{\rm page}$ bits.  Because
$B_{\rm page}=6mw+h_{\rm page}$, both traffic values scale quadratically
in $m$ for this deliberately dense page convention.  The convention makes
the column-count difference physically visible; it is not a storage-optimal
format for the block-diagonal factor.

## Which coordinate transforms this model excludes

The source-coordinate promise in the preceding paragraph is precise: a
selected coefficient $y_j$ fetches the stored page for the original column
$(\mathcal R_{m,\ell})_{:j}$ and contributes that column times $y_j$.
It permits signed permutations of pages, including block permutations,
because they merely relabel or sign original columns.

It excludes every nonmonomial right transform $Q$.  For such a transform,
the transformed coordinate column

\[
 \mathcal R_{m,\ell}Qe_j
\]

is generally a combination of several original pages rather than one stored
original column.  Realizing it requires one of three changes to the model:

1. materialize and store pages for $\mathcal R_{m,\ell}Q$, which changes
   the source payload and page layout;
2. fetch every original page used by $Qe_j$, which changes the fresh-read
   count; or
3. use a source-dependent resident decoder or a different encoded-page
   representation, which changes the declared execution class.

The diagonal lower bound is therefore a comparison only in the fixed
original-column format.  It does not apply after an uncharged dense basis
change, including a diagonalizing basis for $G_r$.

## Optional finite-interpreter lift

The direct source in (18) makes (24)--(28) exact with $a=1$ and $B=0$.
To cover a comparator that may choose a resident reconstruction from a fixed
finite $b$-bit interpreter, use the Rademacher-avoidance argument of
`rademacher_source_growing_static_adaptive_extension.md` with
$\mathcal R_{m,\ell}$ in place of its reference factor.  It supplies a
dyadic $p\times6m$ near-isometry $U$, with $p=O(m+b)$, such that for
every decoded $B$,

\[
 (U\mathcal R_{m,\ell}-B)^T(U\mathcal R_{m,\ell}-B)
\succeq a\,\mathcal R_{m,\ell}^T\mathcal R_{m,\ell},
\qquad a=1-\zeta-\delta^2>0.
\tag{29}
\]

The upper law is unchanged in coefficient coordinates, while its error is
at most $7(1+\zeta)r$.  Equation (24) then holds with $7r$ replaced by
$7(1+\zeta)r$.  The $p$-entry original columns of
$U\mathcal R_{m,\ell}$ can again be stored as dense aligned pages.  If
$p=4^k$, they have a common dyadic denominator $2^{k+\ell+2}$; their
signed numerators have magnitude below $6\cdot2^{\ell+2}$, so a shared
fixed-point format is exact.

This lift still excludes nonmonomial right transforms and uncharged
source-dependent decoders.  It converts the diagonal comparison into one
against the stated finite interpreter range, but does not prove a lower
bound for every Cassette description or page format.
