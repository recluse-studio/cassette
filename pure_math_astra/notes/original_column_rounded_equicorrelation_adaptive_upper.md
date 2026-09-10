# A finite-word adaptive upper using rounded original columns

Status: proved conditional on the established complex equicorrelation
bound and the rational finite-catalog bridge.  The construction has exact
mean for the rounded source itself, a hard cap of \(2m\) original-column
reads, and worst-query risk below \(1.9\eta\).  It is not a physical-page
or complete Cassette resource theorem.

Fix a sufficiently small positive dyadic \(\eta\) for which

\[
 \Psi_{2,\mathbb C}(H_\eta)\le\frac{189}{100}\eta,
 \qquad H_\eta=\mathbf1\mathbf1^T+\eta I_4.
 \tag{1}
\]

The field is complex because (1) is the established complex result.  The
stored source may still have real entries; for a real source, \(^*\) below
is ordinary transpose.  Put \(q=4m\),

\[
 G=H_\eta^{\oplus m},\qquad A^*A=G,
 \tag{2}
\]

and round every real entry of \(A\) to its nearest multiple of a dyadic
step \(h\), with a fixed tie rule:

\[
 W=\operatorname{round}_h(A),\qquad E=W-A,
 \qquad r_0=\frac{h\sqrt{pq}}2.
 \tag{3}
\]

If

\[
 h\le\frac{\sqrt\eta}{10000\sqrt{pq}},
 \tag{4}
\]

then \(\|E\|_{\rm op}\le\|E\|_F\le r_0\le\sqrt\eta/20000\).

## Shared rational catalog and block aggregation

Apply the finite-catalog bridge with tolerance \(\eta/200\).  It gives
one fixed finite rational catalog of two-row-sparse, operator-unbiased laws
on \(\mathbb C^4\) such that, after seeing a nonzero four-coordinate block
\(x_g\), the selector chooses a law with

\[
 \mathbb E\,(Y_g-x_g)^*H_\eta(Y_g-x_g)
 \le\frac{379}{200}\eta\|x_g\|_2^2,
 \qquad
 \mathbb EY_g=x_g,
 \qquad\|Y_g\|_0\le2.
 \tag{5}
\]

For \(x=(x_1,\ldots,x_m)\), invoke the same selector separately on every
block and concatenate the outputs \(Y=(Y_1,\ldots,Y_m)\).  Each selected
block law is operator-unbiased, so

\[
 \mathbb EY=x,\qquad\|Y\|_0\le2m.
 \tag{6}
\]

The catalog is shared across blocks; no \(K^m\)-sized product table is
needed.  Because \(G\) is block diagonal, (5) gives

\[
 \mathbb E\|A(Y-x)\|_2^2
 =\mathbb E\,(Y-x)^*G(Y-x)
 \le\frac{379}{200}\eta\|x\|_2^2.
 \tag{7}
\]

## Transfer from the ideal source to the rounded source

For every coefficient vector \(z\), (2) gives

\[
 \|Az\|_2^2=z^*Gz\ge\eta\|z\|_2^2.
 \tag{8}
\]

Therefore

\[
 \|Wz\|_2\le\|Az\|_2+\|Ez\|_2
 \le\left(1+\frac{r_0}{\sqrt\eta}\right)\|Az\|_2.
 \tag{9}
\]

Taking \(z=Y-x\), then expectations in (7), gives

\[
 \begin{aligned}
 \mathbb E\|W(Y-x)\|_2^2
 &\le\left(1+\frac1{20000}\right)^2
       \frac{379}{200}\eta\|x\|_2^2\\
 &<1.001\cdot1.895\eta\|x\|_2^2
 <1.9\eta\|x\|_2^2.
 \end{aligned}
 \tag{10}
\]

The estimator returned from the selected original columns is \(WY\).
Equation (6) makes its mean exactly

\[
 \mathbb E(WY)=Wx,
 \tag{11}
\]

so rounding has introduced no bias relative to the stored source \(W\).
It only changes the risk through (9).  Every outcome uses at most \(2m\)
of the original columns of \(W\).

For the real source and query model used by the lower bound, replace every
complex catalog outcome matrix by its real part. Its real row support can
only shrink, and its mean remains the identity on real inputs. Since
\(W\) is real, \(W\operatorname{Re}Y=\operatorname{Re}(WY)\), whose
squared error from the real target \(Wx\) is at most the complex squared
error. The resulting catalog has real rational entries and satisfies the
same hard cap, exact mean, and risk bound.

## Finite-word source and query account

Let \(h=2^{-L}\).  Since \(\|A\|_{\rm op}^2=\|G\|_{\rm op}=4+\eta\),
every source entry has magnitude at most \(\sqrt{4+\eta}\).  Each rounded
entry is \(h n\), where

\[
 |n|\le N_h:=\left\lceil\frac{\sqrt{4+\eta}}h+\frac12\right\rceil.
 \tag{12}
\]

Thus the fixed signed integer width

\[
 w_h=\left\lceil\log_2(2N_h+1)\right\rceil
 \tag{13}
\]

encodes every stored real entry exactly.  One original column uses exactly
\(pw_h\) payload bits, or \(\lceil pw_h/8\rceil\) bytes under bit packing;
with byte-aligned scalar words it uses
\(p\lceil w_h/8\rceil\) bytes.  The hard cap therefore reads at most
\(2mpw_h\) payload bits before page headers, alignment, addressing, or
cache effects.  Those additional physical fields require a separate
layout declaration.

The rational catalog has rational coefficients and rational outcome
probabilities.  For rational complex queries, a declared exact rational
sampler and rational arithmetic preserve the coefficient identity
\(\mathbb EY=x\) exactly, hence (11) exactly.  The finite-catalog bridge
proves existence of such a catalog but does not provide a small numerical
catalog, a bounded random-bit sampler, or a native arithmetic proof.

## Model boundary

This construction reads columns of the stored matrix \(W\) in the original
four-coordinate block layout.  It does not replace them by arbitrary
columns of \(WQ\) for a source-family-dependent right transform \(Q\).
The latter permission can identify an arbitrary finite corpus from one
exact unbounded-precision transformed read, as shown in
`finite_family_transformed_column_oracle_boundary.md`; it is a different
access model and would hide payload precision.  Here the per-column
finite-word count is explicit, while the shared catalog and selector still
need their own declared resident-byte account.
