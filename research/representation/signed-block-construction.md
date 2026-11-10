# Three-bit signed-block interpretation for four drive-resident columns

**Status.** This is a finite representation-and-interpretation construction
for one four-column block.  It improves a specified prior local two-rule
decoder under the same signed block code, source records, and hard two-column
read cap.  Its ingredients overlap established sparsification and balancing
methods; the exact decoder formula remains under collision review.  This note
makes no general representation, page-code, RAM, or originality claim.

## 1. Finite source and resident description

Let \(A\in\mathbb D^{p\times4}\), where \(\mathbb D\) is a declared finite
dyadic scalar format.  Store its four original columns as independently
addressable aligned records.  If each scalar uses \(w\) payload bits, declare

\[
 P_{\rm col}=4096\left\lceil
 \frac{\lceil pw/8\rceil+64}{4096}\right\rceil
 \quad\hbox{bytes per column record}.
 \tag{1}
\]

The 64-byte header contains only fixed format and integrity fields.  A fresh
selected column fetches exactly \(P_{\rm col}/4096\) physical pages in this
layout.  The construction does not use packed transformed pages, a resident
output basis, or a source-dependent cache.

Set

\[
 P=I-\frac{\mathbf1\mathbf1^T}{4}.
 \tag{2}
\]

There are eight diagonal sign matrices \(D=\operatorname{diag}(d)\), up to
the irrelevant global replacement \(D\mapsto-D\).  Fix the representative
with \(d_1=1\), so its index consumes exactly three resident bits.  Define

\[
 \eta_D=\|ADP\|_{\mathrm{op}}^2
       =\lambda_{\max}(PDA^TADP).
 \tag{3}
\]

An encoder selects an index \(D_*\) that minimizes (3), or selects a stated
candidate \(D\) with a stated certified bound.  The resident description is

\[
 S(A)=(\text{source identity},\ \operatorname{index}(D),\
       U,\ \mathcal C).
 \tag{4}
\]

Here \(U\in\mathbb D\) is a dyadic upper bound and \(\mathcal C\) is an
exact rational positive-semidefinite certificate for

\[
 UI_4-PDA^TADP\succeq0.
 \tag{5}
\]

One concrete certificate is a permutation, a unit lower triangular rational
matrix, and a nonnegative rational diagonal in an exact \(LDL^T\)
factorization of the left side of (5).  Let \(b_{\rm id}\), \(b_U\), and
\(b_{\mathcal C}\) denote their self-delimiting bit counts.  The
source-dependent resident cost is exactly

\[
 b_{\rm resident}=b_{\rm id}+3+b_U+b_{\mathcal C}\quad\hbox{bits},
 \tag{6}
\]

plus fixed interpreter code and the fixed record-format tag.  Nothing in
(4) contains a \(p\)-entry vector or a reconstructed output basis.

For every \(\delta>0\), an exact finite encoder can choose the minimizer in
(3), then choose a dyadic \(U\) with

\[
 \eta_{D_*}\le U\le(1+\delta)\eta_{D_*};
 \tag{7}
\]

when \(\eta_{D_*}=0\), take \(U=0\).  Comparison of the eight
constant-dimensional algebraic eigenvalue problems and production of the
rational certificate are finite source-construction work.  Their arithmetic
and certificate length are charged by \(b_{\mathcal C}\), rather than being
treated as a free resident transform.  The runtime guarantee below needs
only (5), so it is valid even when the encoder stores a looser \(U\).

## 2. Query-time interpretation

On query \(x\in\mathbb R^4\), form

\[
 z=Dx.
 \tag{8}
\]

Use the exact three-regime signed-sum two-sparse decoder from
[four-coordinate-decoder.md](four-coordinate-decoder.md), specialized to
four coordinates, to draw \(Y\) such that

\[
 \mathbb EY=z,\qquad\|Y\|_0\le2,\qquad
 \mathbf1^TY=\mathbf1^Tz\quad\hbox{almost surely},
 \tag{9}
\]

and

\[
 \mathbb E\|Y-z\|_2^2
 \le\gamma\|z\|_2^2,\qquad
 \gamma=\sqrt{13}-2.
 \tag{10}
\]

Return

\[
 \widehat{Ax}=ADY.
 \tag{11}
\]

This reads at most the two original source columns named by the realized
support of \(Y\).  It is unbiased because

\[
 \mathbb E\widehat{Ax}=AD\,\mathbb EY=ADz=Ax.
 \tag{12}
\]

Also \(\mathbf1^T(Y-z)=0\), hence \(P(Y-z)=Y-z\).  From (5),

\[
 \begin{aligned}
 \mathbb E\|\widehat{Ax}-Ax\|_2^2
 &=\mathbb E\|ADP(Y-z)\|_2^2\\
 &\le U\,\mathbb E\|Y-z\|_2^2\\
 &\le(\sqrt{13}-2)U\|x\|_2^2.
 \end{aligned}
 \tag{13}
\]

The sign map does not hide source reachability.  For any source coordinate
\(j\), query \(x=d_j e_j\).  Then \(z=e_j\), and unbiasedness in (9)
requires a positive-probability outcome whose support contains \(j\).
Across the declared query class, every original column remains reachable.

## 3. Exact resource account

The construction has two distinct phases.

| Resource | Source construction | One cold query |
| --- | --- | --- |
| Original-record traffic | At most ten record fetches, \(10P_{\rm col}\) bytes, suffice to form the four norms and six cross-products of \(A^TA\) with two record buffers. | At most two record fetches, \(2P_{\rm col}\) bytes. |
| Page reads | At most \(10P_{\rm col}/4096\) aligned pages. | At most \(2P_{\rm col}/4096\) aligned pages. |
| Resident source-dependent state | The bit string in (6). | The same string in (6); no new source state. |
| Transforms | Eight signs are inspected during construction; one selected diagonal sign map is stored as three bits. | Four sign flips to form \(z\); no dense transform. |
| Query law | None is permanently stored beyond the fixed decoder. | The exact three-regime law emits one pair; it uses no source-dependent probabilities or flows. |
| Peak working memory | Two column-record buffers, a \(4\times4\) dyadic Gram accumulator, and the certificate workspace. | Four query words, \(O(1)\) auxiliary scalar words, one column-record buffer streamed twice, and a \(p\)-entry output accumulator. |
| Arithmetic | Ten length-\(p\) dyadic dot-product passes, eight constant-dimensional spectral comparisons, and exact certificate formation. | Four sign flips; constant-many scans and integer operations for the three-regime decoder; two coefficient-times-column accumulations. |
| Random bits | None. | At most three integer draws. Rejection sampling has a geometric retry tail; any hard latency cap needs a separately declared failure rule. |

For a dyadic query, the three-regime decoder is exact: every nonzero
coefficient has at most one more fractional bit than the query.  It uses at
most three integer-ticket draws, and its auxiliary words have the query's
bit width up to a fixed constant in this four-coordinate block.  Exact
dyadic/rational accumulation in (11) preserves the mean and the bound in
(13).  A floating implementation must instead add its coefficient and
accumulation bias/variance to (13).  This note supplies no hardware timing,
allocator measurement, or physical-drive result.

## 4. What the construction improves

The prior local two-rule signed-sum decoder has worst-case coefficient

\[
 \gamma_{\rm two}=\frac{19+3\sqrt2}{14}\approx1.66018862051.
 \tag{14}
\]

With the *same* selected \(D\), the same certificate \(U\), the same
resident description, and the same hard two-column read cap, (13) replaces
\(\gamma_{\rm two}U\|x\|_2^2\) by \(\gamma U\|x\|_2^2\).  The relative
decrease of this stated error bound is

\[
 \frac{\gamma_{\rm two}-\gamma}{\gamma_{\rm two}}
 \approx0.0329103.
 \tag{15}
\]

That is a \(3.29103\%\) reduction in the declared bound.  It does not prove
an equal-query-arithmetic win: the old two-rule sampler is simpler than the
exact three-regime optimal decoder.  It also does not compare against an
arbitrary encoded-page representation, an optimized source-dependent basis,
or a general-dimensional sparsifier.

## 5. Countercases and limits

The sign description is not an automatic representation gain.

* **Flat Gram.** If \(A^TA=\alpha I_4\), then
  \(\eta_D=\alpha\) for every sign code.  The three bits select among tied
  descriptions and reveal no useful geometry.

* **Common mode.** If
  \(A^TA=\mathbf1\mathbf1^T+\eta I_4\), the all-equal sign class gives
  \(\eta_D=\eta\).  Any nonconstant sign pattern satisfies
  \(\|Pd\|_2^2\in\{3,4\}\), hence has
  \(\eta_D\in\{\eta+3,\eta+4\}\).  The best code is therefore the ordinary
  all-equal class, which has no nontrivial sign transform.

* **Near-common Gram.** If
  \(A^TA=\mathbf1\mathbf1^T+\eta I_4+E\) with
  \(\|E\|_{\mathrm{op}}\le\rho<3/2\), the all-equal class obeys
  \(\eta_D\le\eta+\rho\), while every nonconstant class obeys
  \(\eta_D\ge\eta+3-\rho\).  The code remains all-equal.  This is the
  regime that reduces to the exact Gram corollary in the companion note,
  rather than creating a new sign-encoding effect.

The construction is a compact finite interpreter, but the source still owns
four full drive-resident columns and the query still owns a \(p\)-entry
output.  Its value is a clean, charged local baseline.  The larger endpoint
requires a source family and comparison proving a better joint
error/read/RAM frontier than the strongest applicable established method.
