# Established methods for compact weight representations

This record asks a narrow question. Given one immutable weight matrix on the
cartridge, what established construction already gives the best defensible
resident representation before Cassette claims new mathematics? The answer
depends on the contract. A two-bit model file, a rank-​(k) factorization, and a
one-page unbiased correction can all make a matrix look smaller, while making
different promises about the returned vector, the bytes held in memory, and the
work performed after a query arrives.

This is a bounded primary-source review completed on 2026-09-20. It records
methods whose sources were read at their primary paper or proceedings page,
along with their stated objectives and the costs that a Cassette comparison must
charge. It does not establish that this list exhausts the literature, that a
method is current best for every model or device, or that a paper's reported
perplexity transfers to the Cassette cartridge.

## The comparison target

Fix a finite encoded matrix $A\in\mathbb F^{p\times q}$, a declared page layout,
and a query $x\in\mathcal X\subseteq\mathbb F^q$. A compilation method produces
resident bits $z_A$, external objects $d_A$, and a source-independent
interpreter. On each query the interpreter may decode $z_A$, issue at most
$s$ fresh page reads, and return $\widehat y$. It must report the following
independently.

| Quantity | What the comparison charges |
| --- | --- |
| Resident state | Code payload, scales, zero points, codebooks, transforms, sampling tables, page indexes, decoder state, and peak working buffers. Shared tables are amortized only when their sharing relation is fixed in the cartridge. |
| External state | The authoritative source, any residual copy, selected columns, pages, redundancy, and indexes. A second full matrix is charged as a second full matrix. |
| Query work | Decoding, transform application, dense or structured products, page selection, I/O requests, and residual correction. |
| Construction | Source scans, calibration data, optimization, arithmetic, temporary external storage, and peak construction memory. |
| Error | A deterministic error, bias, mean-square error, and tail bound over the declared query class. These quantities do not substitute for one another. |

The strict operator objective for a static, fresh-residual method is

\[
\mathcal E_{\mathcal X}(B,\pi,s)
=\sup_{x\in\mathcal X,\ \|x\|_2\le1}
\mathbb E\|Y_{B,\pi,s}(x)-Ax\|_2^2,
\]

where $B$ is reconstructed from the resident code and $Y$ may read the
declared residual pages. If exactness is claimed, the contract is
\(Y(x)=Ax\) for every declared query, not merely low perplexity on a calibration
set. This target specializes the resident-description and fresh-probe model in
[MATHS.md](../../MATHS.md). It deliberately does not treat a model benchmark,
an average reconstruction loss, or a sequential throughput number as the same
objective.

### Hard comparator definition

For a fixed source, layout, resident-byte budget $b_r$, external-byte budget
$b_e$, peak working-memory budget $m$, and hard fresh-read limit $s$, define

\[
\operatorname{OPT}_{\mathcal C}(A;b_r,b_e,m,s)
=\inf_{(z,d,I)\in\mathcal C}
  \mathcal E_{\mathcal X}(I(z,d,\cdot);A),
\]

where \(\mathcal C\) is the explicitly declared representation class. The
comparison is valid only if \(\mathcal C\) states whether it permits arbitrary
finite-precision codes, a learned source-specific decoder, query-dependent
sampling, transformed pages, and biased output. A new method may beat a named
subclass, but it must not be described as better than all compact
representations unless the comparison class actually contains them.

The strongest defensible baseline has two levels.

1. **Oracle lower comparator.** For the declared class \(\mathcal C\), compare
   against \(\operatorname{OPT}_{\mathcal C}\). This is the correct hard
   comparator even when it is not computationally available. It prevents a
   method from claiming a win merely because it beats truncated SVD or a chosen
   quantizer.
2. **Constructive established baseline.** For a linear, source-specific
   resident head and fixed residual-column sampling, evaluate every legal
   factorization and quantized/structured encoding under the same byte ledger;
   for each decoded $B$, use the best admissible residual law and compute the
   exact or certified worst-query error. A full search is required only over a
   finite, enumerated class. The currently practical fallback is the
   byte-accounted weighted low-rank surrogate below, the balanced-feature
   sampler, and the quantized and structured families in this record. It is
   not a universal optimum.

The two levels serve different jobs. The oracle defines the claim's ceiling;
the constructive suite gives an implementation target. Neither lets a method
hide a codebook, a decoder, or a residual copy in an uncharged category.

## Established compact representations

### Dense low rank and weighted low rank

The Eckart--Young--Mirsky construction uses a truncated SVD
\(A\approx U_r\Sigma_rV_r^*\). At a stored coefficient width of \(w\) bytes,
the ordinary two-factor payload costs \(w r(p+q)\) bytes, excluding dimensions,
scales, and any encoded-factor headers. Query evaluation is
\(U_r(\Sigma_r(V_r^*x))\), with \(O(r(p+q))\) arithmetic rather than
\(O(pq)\). It minimizes Frobenius error among rank-$r$ matrices, which is a
deterministic and generally biased approximation of $Ax$.

For Cassette's fixed-law residual objective, `pure_math_astra` derives a more
appropriate constructive surrogate: choose a diagonal column weighting, compute
its truncated SVD, reconstruct $B$, and importance-sample columns of
\(A-B\). The result is a certified factor-two approximation to the best
dense rank-$r$ residual-access variance under that surrogate. It is not an exact
solution of the coupled rank-constrained covariance problem, and its scalar
account is not yet a finite-byte encoder. See
[dense_description_surrogate.md](../../pure_math_astra/notes/dense_description_surrogate.md)
and the bounded prior-work assessment in
[description-prior-work.md](../../pure_math_astra/research/description-prior-work.md).

This distinction has a small exact counterexample. For

\[
A=\begin{pmatrix}2&1\\0&1\end{pmatrix},\qquad r=1,
\]

the projection onto the first output coordinate leaves one residual column and
therefore permits a zero-variance one-column correction. The rank-one truncated
SVD leaves two nonzero residual columns, so its fixed-law residual variance is
strictly positive. Thus a Frobenius-optimal head is not a baseline for the
operator covariance objective merely because it is a best SVD. The derivation
and boundary appear in
[resident_description_and_pages.md](../../pure_math_astra/notes/resident_description_and_pages.md).

[Barnes--Cameron--Howard (2025)](https://arxiv.org/abs/2505.09647) is also a
current exact comparator: for a fixed matrix, it constructs an unbiased random
rank-at-most-$r$ matrix that minimizes expected Frobenius error. That theorem
optimizes matrix-valued rank sampling and Frobenius loss. It neither imposes a
resident-byte budget nor represents its draw by original-column page reads, so
it cannot establish the cartridge frontier; it does rule out treating unbiased
random low rank by itself as new.

### Scalar and groupwise post-training quantization

[GPTQ](https://arxiv.org/abs/2210.17323) constructs a low-bit weight-only
quantization with an approximate second-order objective. Its reported method
uses one-shot sequential quantization and a calibration-derived Hessian
approximation; its stated target is accurate generative-model inference after
3- or 4-bit quantization, not an unbiased matrix-vector estimator or a
page-read frontier. [AWQ](https://arxiv.org/abs/2306.00978) uses activation
statistics to choose equivalent per-channel scaling before hardware-oriented
weight-only quantization. It avoids backpropagation and reports model-task
performance and kernel speed, again not a uniform operator guarantee.

For either family, the real resident encoding includes at least the packed
weight codes, quantization scales, and group or channel identifiers. If a group
has $g$ weights, $n$ codes at $b$ bits require $nb/8$ bytes before the
per-group parameters and file alignment. The query decoder performs unpacking,
scale application, and the quantized matrix-vector product. It returns
$\widetilde A x$, which is biased for $Ax$ whenever $\widetilde A\ne A$.
Neither paper supplies an external exact residual mechanism. A Cassette test
may use either code as a resident head, but must store or page-address
\(A-\widetilde A\) separately before it calls the result exact or unbiased.

[SpQR](https://arxiv.org/abs/2306.03078) is the relevant sparse-plus-quantized
variant. It preserves selected outliers at higher precision and quantizes the
remainder; the payload therefore includes low-bit codes, scales, outlier values,
and outlier indices. Its decoder adds the sparse high-precision correction while
performing inference. The paper's near-lossless empirical result is a strong
compression baseline, but it remains a deterministic approximation unless its
stored outliers and quantized values reconstruct every source weight exactly.

The more recent [VPTQ](https://arxiv.org/abs/2409.17066) is a mandatory
extreme-low-bit vector-code comparator. It optimizes a second-order vector
quantization objective and adds residual/outlier quantization; its encoded
state is vector-code indices, codebooks, scales, and any residual or outlier
values and addresses. Its reported target is calibrated language-model quality
at one to two bits, not a uniform operator error. Thus it is a strong **biased**
rate--quality baseline once its actual codebooks and decoder are charged, not
evidence of exactness from a compact file alone.

### Vector codebooks, lattice codebooks, and trellises

[QuIP](https://arxiv.org/abs/2307.13304) applies incoherence processing and
adaptive rounding to a quadratic proxy objective. It provides a theory for its
quantization setting, but the theorem concerns that setting; it does not certify
bounded external residual access. [QuIP#](https://arxiv.org/abs/2402.04396)
adds randomized Hadamard incoherence processing, lattice-derived vector
codebooks, and fine-tuning. [AQLM](https://arxiv.org/abs/2401.06118) represents
weight blocks through learned additive codebooks, and [QTIP](https://arxiv.org/abs/2406.11235)
uses trellis-coded quantization to obtain high effective vector dimension without
an exponentially large lookup table.

The byte account is not just “bits per weight.” For a codebook method it is
packed block indices plus every codebook, scale, transform seed or sign pattern,
and decoder state that cannot be regenerated by the source-independent
interpreter. Additive codebooks require several indices and vector additions per
decoded block. Lattice lookup requires an index-to-vector reconstruction.
Trellis decoding requires state transitions or their arithmetic equivalent.
Randomized Hadamard processing charges the signs or reproducible seed and the
transform work on the appropriate operand. These methods report compact,
fast, deterministic decoded weights; none returns the original $Ax$ by fresh
page correction under the target above.

This family is a strong practical **biased** weight-code baseline at very
low rate because it includes vector rather than scalar codes, structured
incoherence transforms, and learned codebooks. It must be included before a
new codebook claim is made. It cannot by itself settle the resident-plus-page
objective, because its reported distortion and language-model metrics do not
bound \(\mathcal E_{\mathcal X}\) for an arbitrary declared query class.

### Low rank plus quantized components and adaptation methods

[LoftQ](https://arxiv.org/abs/2310.08659) alternates quantization with a
low-rank initialization for LoRA fine-tuning. [LQ-LoRA](https://arxiv.org/abs/2311.12023)
iteratively decomposes a pretrained matrix into a high-precision low-rank part
and a quantized part, with a memory-budget allocation over matrices. These are
important comparators because they already join a structured dense component to
a compressed residual-like component.

Their payload is the low-rank factors, the quantized matrix codes, scales and
other quantizer metadata, plus any trainable adapter state. A query evaluates
both terms and adds them. The papers' guarantees and evaluations concern
fine-tuning quality, reconstruction objectives, or task metrics. The
quantized term is still part of the deterministic stored model, not a
randomized external residual read. A method that describes “low rank plus
compressed remainder” as new must therefore show a different representation,
error contract, or page-access result.

[CALDERA](https://arxiv.org/abs/2405.18886) makes the closest established
low-rank/low-precision construction explicit: it optimizes a calibrated

\[
\min_{Q,L,R}\lVert(Q+LR-W)X^T\rVert_F^2
\]

subject to low-precision formats, and stores a quantized $Q+LR$. It must be
compared at the actual three payload widths, including scales and factor
metadata. Its theorem bounds that calibration-weighted approximation problem;
it does not make the decoded product exact or furnish a fresh-page estimator.
[SVDQuant](https://arxiv.org/abs/2411.05007) similarly combines a low-bit
branch with a high-precision low-rank branch after moving activation outliers
into the weights. Its result concerns 4-bit diffusion inference, and its
runtime gain depends on a fused GPU engine. It is therefore a relevant hybrid
representation comparator, while its reported speed and visual-quality claims
are not a proof for a cartridge decoder. [SpinQuant](https://arxiv.org/abs/2405.16406)
also makes learned full-precision-preserving rotations a required transform
baseline for model architectures where those rotations are legal; their
quantized execution remains an approximation and their rotations and query
work must be charged here.

### Tensor and structured matrix representations

[Tensorizing Neural Networks](https://proceedings.neurips.cc/paper/2015/file/6855456e2fe46a9d49d3d3af4f57443d-Paper.pdf)
uses tensor-train factors in place of large dense layers. For tensorized input
and output modes, the stored core count is
\(\sum_i r_{i-1}n_i m_i r_i\) coefficients before each coefficient's encoded
width, dimensions, and headers; query evaluation contracts those cores in an
order that determines peak workspace. The cited work studies network
compression, so its final function is an approximation after retraining or
fine-tuning, not an exact residual-access estimator.

[Monarch](https://arxiv.org/abs/2204.00595) supplies another serious structured
baseline. It approximates dense weights with a product of block-diagonal
factors and gives an analytic optimum for its stated dense-to-Monarch
approximation problem. Its code is the two block-diagonal factors and required
permutations; its query cost is the corresponding structured products. This is
far more than a low-rank baseline, but it remains a deterministic structured
replacement unless paired with a separately charged correction path.

Tensor and structured methods deserve a full finite search only after the
tensorization, ranks, block sizes, precisions, factor layout, workspace, and
interpreter are fixed. A claimed parameter count is insufficient. Reshaping
changes the representation class, and a beneficial factorization can have a
decoder or temporary buffer that violates the resident budget.

### CUR, column selection, sketches, and sampled products

[Relative-error CUR](https://arxiv.org/abs/0708.3696) constructs
approximations from selected original columns and rows. A conventional CUR
payload charges the stored columns $C$, rows $R$, coupling matrix $U$,
and all selected indices; its query uses $C U (R x)$. It offers useful
relative-error guarantees for its matrix-approximation objective, and its use
of original columns fits a page-oriented storage system. It does not, by
itself, supply one fresh page read per query or an unbiased correction of an
arbitrary omitted matrix.

Importance-sampled matrix multiplication is the direct ancestor of residual
column correction. The primary comparison already records
[Drineas--Kannan--Mahoney](https://www.cs.yale.edu/homes/mmahoney/pubs/matrix1_SICOMP.pdf):
sample an inner index, rescale the outer product, and bound approximate product
error. In a Cassette execution, if $R=A-B$ and the query is known before the
draw, the one-sample law

\[
\pi_j\propto\|R_{:j}\|_2\,|x_j|
\]

minimizes the coordinate-sampling second moment among such laws. It needs
query-time normalization and an addressable probability structure. A fixed law
can be compiled before the query but loses that adaptivity. These are different
comparators and must not share a claimed bound without the required metadata
and scheduling proof.

### Balanced feature sampling without a resident left factor

There is a materially stronger constructive comparator than static residual
sampling. Factor a source matrix as

\[
A=UV+E,\qquad U\in\mathbb F^{p\times r},\quad
V\in\mathbb F^{r\times q},
\]

store only the finite-precision right factor $V$ resident, and, after a query
$x$, draw a sparse random $w$ satisfying

\[
\mathbb E w=x,\qquad Vw=Vx\ \text{almost surely}.
\tag{1}
\]

The decoder reads the original columns in $\operatorname{supp}w$ and returns
$Aw$. It never stores $U$. Equation (1) gives the exact identities

\[
\mathbb E[Aw]=Ax,\qquad Aw-Ax=E(w-x).
\tag{2}
\]

Consequently its output mean-square loss is precisely

\[
\mathbb E\lVert E(w-x)\rVert_2^2
=\mathbb E[(w-x)^*E^*E(w-x)].
\tag{3}
\]

This changes the byte frontier: the resident payload is $wrq$ bytes for $V$
before its dimensions, precision, sampler state, and page index; the fresh
traffic is the union of pages containing sampled original columns, rather than
a stored $U$ or a separately materialized residual. Decoding charges the sparse
coefficient construction and the sum of sampled $p$-entry columns, as well as
page-location work. Construction still needs a factorization and a law that can
enforce (1). The method cannot call $U$ free: it is absent at inference because
the original source columns supply its contribution, not because it has vanished
from the construction account.

This construction must be compared with three established results.

* [Barnes et al., *Efficient Unbiased Sparsification*](https://arxiv.org/html/2402.14925v2)
  define an unbiased $m$-sparsification by $\mathbb EQ(x)=x$ and support at
  most $m$. Their results minimize named vector divergences under stated
  separability or permutation-invariance conditions. They do **not** impose
  $VQ(x)=Vx$ or optimize the coupled Gram loss (3). They are direct prior art
  for the unbiased sparse-vector component, not a theorem for this constrained
  decoder.
* [Deville and Tille's cube method](https://doi.org/10.1093/biomet/91.4.893)
  is the classical sampling-design route for balancing auxiliary totals while
  selecting a sample with prescribed inclusion probabilities. The later
  [Tille--Rivest exact-balance analysis](https://academic.oup.com/biomet/article/112/4/asaf058/8210742)
  makes the limitation sharp: exact binary balance is an integer-feasibility
  question; total unimodularity plus integral right-hand side is a sufficient
  condition. These sources support a possible constructor for finite support
  laws, but neither proves feasibility for arbitrary real $Vx$, arbitrary
  weights $w$, or an optimal loss in (3).
* Astra's [atomic-dual derivation](../../pure_math_astra/notes/query_adaptive_atomic_dual.md)
  gives an exact convex characterization, for positive-definite $G$, of

  \[
  \inf_{\mathbb Ew=x,\ \lVert w\rVert_0\le s}
  \mathbb E(w-x)^*G(w-x).
  \]

  It includes a finite SOCP and dual. It does not apply by substitution with
  $G=E^*E$: that Gram may be
  singular, and its required mean constraint is stronger than $Vw=Vx$.
  It is nevertheless the correct benchmark once a full-mean, positive-definite
  subproblem is claimed.

The strongest defensible constructive baseline for an **unbiased, source-column
decoder** is therefore: optimize a finite-precision $V$, a declared sparse law
meeting (1), and its actual page layout against (3), alongside a full byte and
construction ledger. It is stronger than independent coordinate sampling,
because it makes the $UVx$ component exact without keeping $U$ resident. It is
not a universal optimum: feasibility, support size, finite-precision balance,
and the optimal Gram-loss law remain open for a general source.

### Exact signed-sum hard-cap sparsification: source challenge

Consider the narrower real-vector class used by the current four-coordinate
construction: a law $Y_x$ with $\lVert Y_x\rVert_0\le s$ almost surely,
\(\mathbb EY_x=x\), and

\[
\mathbf 1^TY_x=\mathbf 1^Tx\quad\text{almost surely},
\tag{4}
\]

for every signed $x\in\mathbb R^4$. The reported target is the exact minimax
value $\sqrt{13}-2$ for $s=2$ under squared Euclidean relative error. A bounded
primary-source search found relevant predecessors but no source establishing
this exact signed, pathwise-affine, four-coordinate value or mechanism.
That is a search result, not an originality finding.

* Barnes et al. explicitly identify pathwise preservation of the coordinate sum
  as an additional desired condition. Their positive-orthant,
  permutation-invariant construction does preserve that sum, but their theorem
  is proved among nonnegative sparsifications. In its separate
  non-permutation-invariant EUS setting, the paper asks how an added ordinary
  sum constraint changes the optimum. A signed vector cannot be reduced to this
  result by coordinatewise sign flips, because those
  flips preserve the $\ell_1$ sum, not $\mathbf1^Tx$.
* [Weare--Webber (2026)](https://doi.org/10.1002/cpa.70012) give hard-cap,
  unbiased pivotal sparsification and prove Euclidean optimality for their
  unconstrained class. Their stated pathwise invariant is
  $\lVert Y_x\rVert_1=\lVert x\rVert_1$, not (4). The distinction is concrete:
  with $x=(1,1,-1)$ and a two-coordinate outcome, the usual equal-magnitude
  rescaling gives either signed total $3$ or $0$, whereas $\mathbf1^Tx=1$.
  Thus that pivotal mechanism does not directly meet the signed-sum contract.
* The source search for the literal value and for signed, affine-constrained
  unbiased sparsification returned no primary collision. It cannot establish
  absence. A complete originality claim still requires a theorem-level search
  through survey-sampling calibration, dependent rounding, convex-envelope,
  and randomized numerical-linear-algebra literature, followed by comparison
  with the final decoder rather than its value alone.

The immediate mathematical comparison is therefore precise: an external result
already covers the positive-orthant fixed-sum case, and another covers the
unconstrained signed Euclidean case. Neither currently identified source proves
the claimed signed, pathwise-sum, hard-cap minimax result. The full proof must
still be checked independently, including the supremum over all nonzero real
four-vectors and the completeness of the proposed outcome family.

| Primary source | What the source actually proves or constructs | Containment result for the signed real (q=4,s=2) problem |
| --- | --- | --- |
| Barnes et al. (2024), [EUS](https://arxiv.org/html/2402.14925v2) | A hard-(m), unbiased sparse vector; for positive vectors and a permutation-invariant divergence, an efficient nonnegative fixed-sum law. Separately, the paper asks how an ordinary sum constraint changes its non-permutation-invariant EUS optimum. | **Partial containment only.** It covers the positive orthant of the affine constraint, not all signed queries or the stated minimax value. |
| Weare--Webber (2026), [pivotal sparsification](https://doi.org/10.1002/cpa.70012) | Hard-cap, unbiased vector sparsification; Euclidean optimality in the unconstrained class and pathwise (ell_1)-norm preservation. | **No containment.** A signed (ell_1) invariant is not the affine signed-sum invariant. |
| Deville--Tille (2004), [cube method](https://doi.org/10.1093/biomet/91.4.893), and [Tille--Rivest (2025)](https://academic.oup.com/biomet/article/112/4/asaf058/8210742) | Random (0/1) sample indicators with prescribed inclusion probabilities and auxiliary-total balance; the flight phase preserves balance, while exact terminal balance has an integer-feasibility boundary. | **No containment.** These results do not optimize real sparse outcome values under Euclidean loss; exact balance is not assured for arbitrary real constraints. They are constructor antecedents, not the claimed optimizer. |
| Gandhi--Khuller--Parthasarathy--Srinivasan (2006), [dependent rounding](https://www.cs.umd.edu/~srin/PDF/2006/depround-jou.pdf) | Rounds fractional bipartite-edge variables to (0/1), preserving marginals and giving probability-one degree rounding guarantees. | **No containment.** Its integral output and graph-degree constraints do not yield arbitrary signed coefficients (Y), the required affine equality, or a Euclidean minimax theorem. |
| Argyriou--Foygel--Srebro (2012), [(k)-support norm](https://arxiv.org/abs/1204.5043) | The convex hull/gauge of (k)-sparse Euclidean atoms; it supplies the convex-envelope geometry for the unrestricted mean-constrained problem. | **No containment.** The affine slice (mathbf1^TY=mathbf1^Tx) changes the atom set and its gauge; the source does not evaluate that sliced (q=4,k=2) minimax value. |

This table establishes a demanding prior-art boundary, not novelty. The new
mechanism may still be an instance of a more general affine-sliced atomic-norm
or balanced-rounding theorem not found in this finite source pass. A defensible
originality claim requires that final theorem-level comparison and an independent
audit of the construction's lower bound and equality cases.

### Claimed all-real extension: exact source boundary and proof obligation

The proposed extension fixes hard support at two and asks for the least second
moment among laws satisfying the ordinary, pathwise coordinate-sum condition.
For \(t=\mathbf1^Tx\geq0\), let \(P\) be the sum of positive coordinates,
\(N\) the absolute sum of negative coordinates, and \(h=\max_i x_i\). The
reported value of \(\inf\mathbb E\lVert Y\rVert_2^2\) is

\[
 \begin{cases}
 P^2+N^2,&N\geq t/2,\\
 t^2/2+4tN,&N<t/2\text{ and }h\leq t/2+2N,\\
 2th-t^2+2(P+N-h)^2,&\text{otherwise.}
 \end{cases}
\tag{5}
\]

The internal decoder now gives a rational sampler and matching upper bound in
[four-coordinate-decoder.md](four-coordinate-decoder.md). This record
independently checks its three lower-bound certificates: use constant dual
values \(2P,-2N\) in the first case; \(0,-4t\) in the second; and, in the
third, zero at a maximum positive coordinate, \(-2t+4L\) at the other positive
coordinates, and \(-2t-4L\) at negative coordinates, where \(L=P+N-h\). The
case conditions make the indicated pair lines maximal. This checks the
lower-bound algebra; it is not a substitute for an independent proof audit of
the all-\(n\) construction or its finite-arithmetic realization. The
zero-probability positive-negative branch in Case B needs an explicit
\(N=0\) convention, because its displayed conditional probabilities otherwise
divide by zero.

The closest direct source is Barnes et al.'s EUS paper. It handles an
unconstrained signed reduction by coordinatewise sign changes for squared
Euclidean loss, but that transformation preserves a signed weighted total,
not \(\mathbf1^TY=\mathbf1^Tx\). Its nonnegative, permutation-invariant
theorem does preserve the ordinary sum. Separately, its Section IV asks how an
additional ordinary-sum constraint changes the optimum in its
non-permutation-invariant EUS setting. That is a close open-problem boundary,
not the same signed-Euclidean hard-two theorem and not a proof of (5). The
bounded primary search
also found no collision in pivotal sparsification, cube/calibration sampling,
or dependent rounding. It does not establish novelty.

### Independent audit: global constant implied by the three-case formula

This calculation is conditional on the claimed three-case value (5). It audits
what that value implies; it does not prove the matching all-dimensional sampler.
For \(n\geq2\), its worst normalized second moment is

\[
 C_n=\max_{0\leq l\leq\lfloor n/2\rfloor}
 \frac{n-8l+\sqrt{n^2+48nl}}4.
\tag{6}
\]

The corresponding squared-error constant is \(C_n-1\), because unbiasedness
makes \(\mathbb E\lVert Y-x\rVert_2^2=\mathbb E\lVert Y\rVert_2^2-
\lVert x\rVert_2^2\). The maximizing integer \(l\) is one of
\(\lfloor n/6\rfloor,\lceil n/6\rceil\), after comparing the two values. In
particular, \(C_n=2n/3\) when \(6\) divides \(n\), so the variance ratio is
\(2n/3-1\).

Here is the audit. Let \(k\) be the number of positive coordinates and \(l\)
the number of negative coordinates. In the middle case, Cauchy gives
\(\lVert x\rVert_2^2\geq P^2/k+N^2/l\), and the largest generalized
Rayleigh quotient of

\[
 \frac{P^2/2+3PN-7N^2/2}{P^2/k+N^2/l}
\]

is

\[
 \frac{k-7l+\sqrt{(k+7l)^2+36kl}}4.
\tag{7}
\]

Its positive eigenvector has \(P/N>3\) exactly when \(k>l\), which is the
interior condition for that case. Equal positive coordinates meet its maximum-
coordinate condition for every \(k\geq2\). With \(k=n-l\), (7) becomes (6).
For fixed \(n\), its continuous relaxation is
\((1-8u+\sqrt{1+48u})n/4\), whose unique maximum is at \(u=1/6\).

The first case cannot exceed this result: when \(k\leq l\), its maximum over
\(1\leq P/N\leq3\) is at most \((k+l)/2\leq n/2\); when \(k>l\), its endpoint
\(P/N=3\) is dominated by (7). In the third case, write \(P=h+U\), where
\(h\) is the anchored maximum. The claimed numerator is

\[
 h^2+U^2+6UN+N^2.
\]

For the third case, fix every nonanchor coordinate and write its squared
norm as \(d\). Since \(d\leq U^2+N^2\), the actual quotient
\((h^2+U^2+6UN+N^2)/(h^2+d)\) decreases with \(h\). Its smallest allowed
\(h=U+3N\) is the middle-case boundary, so the second-case bound (7) applies
there. Equivalently, when \(k\geq2,l\geq1\), Cauchy's sharp lower bound is
\(d\geq U^2/(k-1)+N^2/l\); the \(k-1\), rather than \(k\), is essential.
The all-positive and one-positive edge cases are at most \(n/2\) or reduce
directly to the same boundary bound. Coordinates equal to zero cannot enlarge
the result: increasing \(k\) while holding \(l\) fixed only increases (7), so a
support of size below \(n\) is dominated by its zero-filled \(n\)-coordinate
comparison.

This audit finds no algebraic counterexample to (6). It leaves one decisive
obligation: prove that the claimed rational law attains all three values for
every real \(n\), including zero coordinates and all boundary cases.

### Control variates and lower-bound context

[Hutch++](https://arxiv.org/abs/2010.09649) combines a low-rank approximation
with stochastic estimation of a residual and proves query complexity for the
trace of a PSD matrix available through matrix-vector products. It is the
closest high-level precedent for “deterministic head plus random residual,” yet
its output is a scalar trace, its access oracle differs, and it does not solve
the vector-valued page-resident problem. Its lower bound therefore cannot be
ported as a Cassette lower bound.

[Larsen and Nelson](https://arxiv.org/abs/1411.2404) prove a lower bound for
linear Johnson--Lindenstrauss embeddings on a finite point set. This limits one
specific form of uniform linear dimensionality reduction. It does not lower
bound source-specific encodings with arbitrary decoders, quantized codebooks,
or residual pages. Likewise, streaming and communication lower bounds for
matrix rank or low-rank approximation are relevant pressure, not direct
impossibility theorems for this cartridge contract. A valid lower-bound claim
must keep the encoder's source knowledge, finite precision, decoder class,
query class, and permitted fresh reads explicit.

## Stress tests that reject easy claims

The following finite cases are not performance tests. They expose which
assumption a proposed theorem must carry.

| Claim under pressure | Exact stress case | Consequence |
| --- | --- | --- |
| “A small Frobenius tail is the right residual objective.” | \(A=\left(\begin{smallmatrix}2&1\\0&1\end{smallmatrix}\right)\), rank one. A coordinate projection leaves one residual column; truncated SVD leaves two. | Frobenius-optimal and fixed-law variance-optimal heads differ. |
| “Quantization is an exact compact description.” | One scalar $A=[\alpha]$ whose permitted codebook has no codeword $\alpha$. | Deterministic decoding returns $\widetilde\alpha x\ne\alpha x$ for $x\ne0$. An exact claim needs an additional correction path. |
| “One unread residual page can be inferred from another.” | Let residual page blocks contain independent nonzero contributions and permit queries supported on either block. | Exact execution under the original-block visibility model must read every nonzero residual page; a one-page exact claim needs a declared resident transform or a structural relation. |
| “A source-trained decoder is free.” | Put all entries of $A$ into a source-specific interpreter table and set the nominal code to zero. | The table is a representation and its bits, evaluation work, and workspace are chargeable. |
| “A transform removes page cost.” | Apply a dense orthogonal transform before coding, then require original-coordinate queries. | The transformed query, transform parameters or seed, inverse relation, and transformed-page layout enter the resident, arithmetic, or external account. |

The third case is the hard-cap page law in
[resident_description_and_pages.md](../../pure_math_astra/notes/resident_description_and_pages.md).
It has a stated boundary: a resident query transform can change the visibility
model. That boundary is productive, because it names a real research avenue,
but the transform, its precision, and its decoding work then become the thing
that must be constructed and priced.

## A solved scalar allocation subproblem; construction remains open

For fixed residual contributions $v_j$, squared norms $a_j=\|v_j\|_2^2$,
costs $c_j>0$, and $b=\|\sum_j v_j\|_2^2$, the root investigation has proved
the optimizer of the narrow scalar objective

\[
F(\pi)=\left(\sum_jc_j\pi_j\right)
\left(\sum_j\frac{a_j}{\pi_j}-b\right)
\]

over the positive simplex:

\[
\pi_j^*=\sqrt{\frac{a_j}{b+\rho c_j}},
\qquad \sum_j\pi_j^*=1,
\]

with \(\rho\ge0\) chosen by normalization, including the \(\rho=0\) aligned
endpoint. The proof uses
\(a_j=(\pi_j^*)^2(b+\rho c_j)\), then Cauchy--Schwarz on
\(\sum_jc_j\pi_j\) and \(\sum_jc_j(\pi_j^*)^2/\pi_j\). It proves an allocation
law, not a representation constructor, a Gram-loss optimum, or an advantage
over equal-cost sampling. In particular, equal costs reduce the formula to
\(\pi_j\propto\sqrt{a_j}\), so this result supplies no independent construction
route in that regime. It differs from optimizing a second moment alone because
the \(-b\) covariance term changes the objective. The nearby
[Resource-Optimal Importance Sampling](https://arxiv.org/abs/2603.13495)
optimizes a cost-times-second-moment criterion in a different quantum setting;
it is relevant prior-art pressure, but it does not by itself settle the
cost-times-variance formula above.

For a representation-construction result, all of the following remain unproved.

1. A finite-byte representation class must construct a $B$ whose residual
   geometry yields a better certified frontier than every listed applicable
   baseline at equal resident bytes, peak workspace, fresh-byte cap, and query
   class.
2. The compiler must account for residual norms, the sampling law, codebooks,
   transforms, page addresses, finite precision, and construction workspace.
   A real-valued factor count is not that proof.
3. The decoder and correction must compose through an actual model trace under
   the separate Q19 certificate fields. A one-layer variance result does not
   establish frontier-model capability.
4. The source comparison must examine the final theorem and mechanism, not
   merely the method's vocabulary. The current review rules out a claim that
   low rank, residual sampling, importance sampling, codebooks, or structured
   matrices were pioneered here.

Until those conditions are met, the appropriate claim is narrower: Cassette
has an explicitly stated comparison target and a demanding established-method
suite. The representation-construction result remains open.

## Primary sources consulted

- Frantar et al., [GPTQ](https://arxiv.org/abs/2210.17323).
- Barnes, Cameron, and Howard, [On Unbiased Low-Rank Approximation with Minimum Distortion](https://arxiv.org/abs/2505.09647).
- Lin et al., [AWQ](https://arxiv.org/abs/2306.00978).
- Dettmers et al., [SpQR](https://arxiv.org/abs/2306.03078).
- Liu et al., [VPTQ](https://arxiv.org/abs/2409.17066).
- Chee et al., [QuIP](https://arxiv.org/abs/2307.13304).
- Tseng et al., [QuIP#](https://arxiv.org/abs/2402.04396).
- Egiazarian et al., [AQLM](https://arxiv.org/abs/2401.06118).
- Tseng et al., [QTIP](https://arxiv.org/abs/2406.11235).
- Li et al., [LoftQ](https://arxiv.org/abs/2310.08659).
- Guo et al., [LQ-LoRA](https://arxiv.org/abs/2311.12023).
- Saha et al., [CALDERA](https://arxiv.org/abs/2405.18886).
- Li et al., [SVDQuant](https://arxiv.org/abs/2411.05007).
- Liu et al., [SpinQuant](https://arxiv.org/abs/2405.16406).
- Novikov et al., [Tensorizing Neural Networks](https://proceedings.neurips.cc/paper/2015/file/6855456e2fe46a9d49d3d3af4f57443d-Paper.pdf).
- Dao et al., [Monarch](https://arxiv.org/abs/2204.00595).
- Drineas, Mahoney, and Muthukrishnan, [Relative-error CUR](https://arxiv.org/abs/0708.3696).
- Drineas, Kannan, and Mahoney, [sampled matrix multiplication](https://www.cs.yale.edu/homes/mmahoney/pubs/matrix1_SICOMP.pdf).
- Barnes et al., [Efficient Unbiased Sparsification](https://arxiv.org/html/2402.14925v2).
- Weare and Webber, [Randomly Sparsified Richardson Iteration: A Dimension-Independent Sparse Linear Solver](https://doi.org/10.1002/cpa.70012).
- Gandhi, Khuller, Parthasarathy, and Srinivasan, [Dependent Rounding and its Applications to Approximation Algorithms](https://www.cs.umd.edu/~srin/PDF/2006/depround-jou.pdf).
- Deville and Tille, [Efficient balanced sampling: the cube method](https://doi.org/10.1093/biomet/91.4.893).
- Tille and Rivest, [Existence and applications of finite-population samples that are exactly balanced](https://academic.oup.com/biomet/article/112/4/asaf058/8210742).
- Meyer et al., [Hutch++](https://arxiv.org/abs/2010.09649).
- Larsen and Nelson, [linear dimensionality-reduction lower bound](https://arxiv.org/abs/1411.2404).
- Cugini, Atif, and Subasi, [Resource-Optimal Importance Sampling](https://arxiv.org/abs/2603.13495).

The source list is a starting comparator record, not a declaration that no
stronger applicable method exists. Any subsequent construction must refresh
the relevant primary-source search before making a superiority claim.
