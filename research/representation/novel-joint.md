# Joint representation and interpretation search: tagged Walsh pages

**Disposition: rejected as a novelty claim.** This note proves a sharp cancellation separation from an optimized one-column Horvitz--Thompson class. The construction then loses, exactly, to the broader established class that stores a charged resident query transform and interprets external pages as its output factor. It therefore does not close the representation programme.

The immediate question was whether a small resident codebook could tell the interpreter that a full external page cancels for the present query. It can. The harder question is whether that is more than a factorization already available to the strongest comparator. It is not.

## Declared class and charged representation

Let \(b=2^d\), let \(H_b\in\{-1,1\}^{b\times b}\) be a Walsh matrix with
\(H_bH_b^{\mathsf T}=bI_b\), and fix \(P\le m\). A source is partitioned into
\(P\) physical pages of \(b\) columns:

\[
 A=[A_1\ \cdots\ A_P],\qquad
 A_g=u_g h_{\tau_g}^{\mathsf T},\qquad
 u_g^*u_h=\mathbf1\{g=h\},\quad \tau_g\in[b].
 \tag{1}
\]

Here \(h_i^{\mathsf T}\) is Walsh row \(i\), and each \(u_g\) is a finite-word
external vector. The full \(m\)-by-\(Pb\) source remains external; (1) is a
verified source contract, not a replacement source format.

The persistent source-dependent resident word is

\[
 Z=(b,P,\tau_1,\ldots,\tau_P,\text{canonical page order}).
 \tag{2}
\]

It costs \(P\log_2b\) tag bits plus self-delimiting headers. The source scan
that admits (1) reads \(Pbmw\) encoded source bits for \(w\)-bit entries,
holds an anchor vector and comparison buffer, and creates no derivative
external object. A noncanonical layout must add its complete page map to
\(Z\). The Walsh generator is source-independent and is not charged as a
source codebook.

For a query \(x=(x_1,\ldots,x_P)\), define

\[
 \alpha_g=h_{\tau_g}^{\mathsf T}x_g,\qquad
 {\cal I}_Z(x)=\sum_{g:\alpha_g\ne0}\alpha_g u_g .
 \tag{3}
\]

The interpreter calculates all \(\alpha_g\) resident, reads the anchor of
exactly each active physical page, and accumulates the result. It needs
\(P(b-1)\) sign additions/subtractions, an \(m\)-coordinate output, a decoded
anchor buffer, and optionally \(P\) coefficient scalars. Its fresh-page count
is \(\#\{g:\alpha_g\ne0\}\); each such count means the full encoded page byte
length, not one algebraic column.

### Theorem 1 — exact interpretation

For every source satisfying (1) and every query \(x\), \({\cal I}_Z(x)=Ax\).

**Proof.**

\[
 Ax=\sum_gA_gx_g
 =\sum_gu_g(h_{\tau_g}^{\mathsf T}x_g)
 =\sum_g\alpha_gu_g.
\]

Terms whose coefficient is zero need no external anchor. Every remaining term
uses its page anchor. \(\square\)

The theorem is exact only in exact field arithmetic. In finite arithmetic,
a zero-read decision requires a certified exact zero for every \(\alpha_g\).

## Exact win against the complete one-column class

Define \(\mathsf{ColHT}_1\) to be every one-draw estimator

\[
 Y_i(x)={A_{:i}x_i\over p_i(x)},\qquad i\sim p(x),\qquad p_i(x)>0,
 \tag{4}
\]

with a fully query-dependent probability law. It may retain the same tag word
\(Z\), but it may not use a cross-column aggregate before its draw. This is the
ordinary one-column residual mechanism, optimized over its whole stated class.

Choose \(\sigma_g\ne\tau_g\) and the unit query

\[
 x_g={h_{\sigma_g}\over\sqrt{Pb}}.
 \tag{5}
\]

Then \(\alpha_g=0\) and \(Ax=0\).

### Theorem 2 — sharp cancellation cost

For (1) and (5),

\[
 \inf_{p\in\mathsf{ColHT}_1}\mathbb E\|Y_i(x)-Ax\|_2^2=Pb.
 \tag{6}
\]

Uniform probability over the \(Pb\) columns is the unique optimum. The average
of \(s\) independent optimal draws has error \(Pb/s\), so it needs at least
\(Pb/\varepsilon^2\) independent one-column access draws for mean-square
error at most \(\varepsilon^2\). The interpreter (3) has exact zero error and
zero fresh page reads. A storage implementation may cache a page across several
column draws; that is a separate cache-byte and scheduling contract, so this
theorem does not turn the draw count into a physical-I/O lower bound.

**Proof.** Each source contribution has norm

\[
 \|A_{g,:\ell}x_{g,\ell}\|_2={1\over\sqrt{Pb}}.
\]

Since the target is zero,

\[
 \mathbb E\|Y_i\|_2^2
 =\sum_{g,\ell}{1/(Pb)\over p_{g\ell}}
 \ge\left(\sum_{g,\ell}{1\over\sqrt{Pb}}\right)^2=Pb.
\]

Cauchy--Schwarz gives the inequality and equality fixes the uniform law.
Independent averaging divides covariance. \(\square\)

A reproducible exact instance has \(P=3\), \(b=4\), tags \((0,1,2)\), and
query rows \((1,2,3)\). The three Walsh inner products are \((0,0,0)\), so
the interpreter reads zero pages while the optimized one-draw value in (6) is
12.

## The stronger established comparator ties it

Set

\[
 (F_Zx)_g=h_{\tau_g}^{\mathsf T}x_g,\qquad
 U=[u_1\ \cdots\ u_P].
 \tag{7}
\]

Then

\[
 A=UF_Z.
 \tag{8}
\]

A factor interpreter that stores the tags for \(F_Z\), calculates \(F_Zx\),
and reads the anchors that supply needed columns of \(U\) has exactly the
persistent bits, peak working values, external source, arithmetic, fresh reads,
and output of (3). It reproduces the proposed frontier point exactly.

This collision is already explicit in
pure_math_astra/notes/resident_description_and_pages.md: its scope boundary
permits a charged resident query transform \(F\) and an acquired factor \(P\)
in \(R=PF\). Equations (7)--(8) are a Walsh-tagged special case. The proposed
method has therefore not beaten the broad comparator; it has supplied an
especially transparent instance of it.

The primary-source collision is also clear for the sampling half. Drineas,
Kannan, and Mahoney, Fast Monte Carlo Algorithms for Matrices I:
Approximating Matrix Multiplication, SIAM Journal on Computing 36(1), 2006,
establish the sampled inner-index, importance-rescaled mechanism. The primary
paper checked is https://www.cs.yale.edu/homes/mmahoney/pubs/matrix1_SICOMP.pdf.
The fast Walsh transform is established as well; Moustakides and Asimakis,
Fast delta Hadamard transform, Applied Optics 20(17), 1981, records its
standard arithmetic reduction at
https://opg.optica.org/ao/abstract.cfm?uri=ao-20-17-3058. A bounded search on
2026-09-20 found no claim for this exact page spelling, but the internal
factorization collision is already decisive.

## Stronger baseline: right factor plus balanced sparse decoder

The relevant baseline is stronger still. State its support theorem first over
the real field. Suppose

\[
 A=UV+E,\qquad V\in\mathbb R^{k\times q}
 \tag{9}
\]

and only the finite-word right factor \(V\) is resident. For a real query \(x\),
put \(L=\|x\|_1\), let \(s_j=\operatorname{sign}(x_j)\), and set
\(z_j=s_jV_{:j}\). A balanced coefficient decoder chooses a random
\(w\in\mathbb R^q\) satisfying

\[
 \mathbb Ew=x,\qquad Vw=Vx\ \text{almost surely},\qquad
 \|w\|_1=L,\qquad\|w\|_0\le k+1.
 \tag{10}
\]

Such a law exists. Let \(\mu_j=|x_j|/L\). The polytope

\[
 {\cal P}=\{\lambda\ge0:\mathbf1^{\mathsf T}\lambda=1,\
                 \sum_j\lambda_jz_j=\sum_j\mu_jz_j\}
\]

contains \(\mu\). Its vertices have support at most \(k+1\), since the
normalization and at most \(k\) independent balance equations determine a
basic feasible point. Decompose \(\mu\) into vertices of \({\cal P}\), draw
one vertex \(\lambda\), and set \(w_j=Ls_j\lambda_j\). This proves (10).

For complex \(V\), split the balance equation into real and imaginary parts.
The same argument then gives support at most \(2k+1\), unless additional
structure reduces the real rank. It is incorrect to quote the real \(k+1\)
bound without this field qualification.

Reading the support of \(w\) and returning \(Aw\) is unbiased, and the
dominant factor cancels in every outcome:

\[
 Aw-Ax=E(w-x),\qquad
 \mathbb E\|Aw-Ax\|_2^2
 \le\|E\|_{\rm op}^2\bigl(\mathbb E\|w\|_2^2-\|x\|_2^2\bigr)
 \le\|E\|_{\rm op}^2(L^2-\|x\|_2^2).
 \tag{11}
\]

This can use less resident payload than storing \(U\), depending on the
encoded shapes and precisions, and it subsumes the Walsh example: choose \(V=F_Z\). If \(E=0\) and \(Vx=0\), the
interpreter can return zero before sampling. For a general residual \(E\),
\(Vx=0\) alone leaves the correction \(Ex\). The construction is a
finite-dimensional balanced-sampling and Caratheodory mechanism, not a new
decoder. Relevant current primary work includes Barnes et al., Efficient
Unbiased Sparsification (2024), https://arxiv.org/html/2402.14925v2, and
exact balanced finite-population sampling (2025),
https://academic.oup.com/biomet/article/112/4/asaf058/8210742.

## Attempted finite-bit improvement and exact reduction

A tempting modification stores a quantized \(\widehat V\), imposes
\(\widehat Vw=\widehat Vx\), and calls the saved factor bits a joint
improvement. Algebra says otherwise. Put

\[
 \Delta=V-\widehat V,\qquad
 A=U\widehat V+\underbrace{(E+U\Delta)}_{\widehat E}.
 \tag{12}
\]

The same decoder then obeys exactly

\[
 Aw-Ax=\widehat E(w-x).
 \tag{13}
\]

Thus quantized balance is simply the established balanced decoder applied to
the different residual \(\widehat E\). Any claimed gain must compare the
encoded cost of \(\widehat V\) with the enlarged residual risk in (13); the
balance step supplies no new mathematical mechanism.

The failure is sharp even when the original residual vanishes. Take \(q=3\),
\(A=uv^{\mathsf T}\), \(E=0\), and, for \(0<\epsilon<1/2\), set

\[
v=(1,1+2\epsilon,1),\qquad
\widehat v=(1,1+\epsilon,1-\epsilon),\qquad
x=(1/2,1/4,1/4).
\]

The two outcomes

\[
w^{(1)}=(1,0,0),\qquad w^{(2)}=(0,1/2,1/2),
\]

each with probability one half, obey \(\mathbb Ew=x\) and
\(\widehat v^{\mathsf T}w=\widehat v^{\mathsf T}x=1\) almost surely. Yet
the two values of \(v^{\mathsf T}(w-x)\) are \(-\epsilon/2\) and
\(\epsilon/2\), so its output mean-square error is exactly
\(\|u\|_2^2\epsilon^2/4\). Exact \(V\)-balance instead makes the rank-one
source output exact in every outcome. In general, \(\widehat V\)-balance leaves

\[
Aw-Ax=u\,(v-\widehat v)^{\mathsf T}(w-x).
\tag{14}
\]

This explicit finite-word example defeats the unqualified claim that approximate
balance preserves an exact-factor advantage. It is not a lower bound against
every possible coded descriptor.

A finite Gram approximation gives another established baseline, not a new
route. Let \(\operatorname{OPT}_G\) be the minimum quadratic risk over the
declared hard-sparse unbiased coefficient laws. If
\((1-\epsilon)G\preceq\widehat G\preceq(1+\epsilon)G\), then a
\(\widehat G\)-optimal law has true risk at most
\((1+\epsilon)/(1-\epsilon)\operatorname{OPT}_G\): first use
\(G\preceq\widehat G/(1-\epsilon)\), then use the \(\widehat G\) optimum,
and finally \(\widehat G\preceq(1+\epsilon)G\) on a \(G\)-optimal law.
This does not price the Gram descriptor, solve the exponentially indexed atomic
decoder, or beat the balanced factor baseline.

## Stress tests and remaining obstacle

| Attack | Consequence |
|---|---|
| Aligned dense Walsh query | Every page is active; (3) reads all \(P\) pages. |
| Sparse query | It generally reads one full physical page, not one column's bytes. |
| Basis change | A generic right orthogonal transform destroys (1); tags are layout facts, not spectral invariants. |
| One-entry perturbation | For \(\widetilde A_g=A_g+E_g\), a cancelling query has unseen output \(\sum_gE_gx_g\). Exactness then requires further evidence or reads. The class has no robust open neighbourhood. |
| Finite precision | A rounding residue in an alleged zero \(\alpha_g\) invalidates the zero-read claim unless an explicit numerical certificate controls it. |
| Metadata growth | Permutations, mixed widths, codebooks, and candidate transforms all add charged maps and tables. |
| Output and query buffers | The tag word is not peak residency; both buffers remain charged. |
| General \(A\) | The source class has \(P\) anchors and tags, while a general finite-word matrix has independent coordinates. No arbitrary-source conclusion follows. |

The exact unresolved problem is now narrow and hard: produce an encoded
descriptor and efficient sparse interpreter whose equal-bit error/read
frontier strictly improves the charged right-factor plus balanced-decoder
frontier in (9)--(11), or prove a lower bound that rules this out on a source
class broader than the Walsh rank-one-page variety. Neither the tagged-page
construction, a quantized right factor, nor a spectrally approximate Gram
does that. No production consequence follows from this note; MATHS.md still
requires separate finite-arithmetic, physical-read, and sequential-composition
certificates.
