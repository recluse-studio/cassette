# Procedural finite-word decoder for an anisotropic transform cover

Status: conditional finite-word realization of the deterministic cover in
anisotropic_transform_box_cover.md. This note replaces an explicit table
of \(K\) matrices by a fixed rational atlas and a grid decoder. It is an
exact-arithmetic statement, not a byte certificate, a source-selection
algorithm, or a runtime result.

## 1. Model and result

Use the notation of dependence_support_transform_rate.md. Thus \(D\) is
fixed, \(d=\beta N\), \(k\) is the minimum dependence-support size, and

\[
\kappa=\frac{d+\beta k}{2}.
\tag{1}
\]

Fix a sufficiently small target \(0<\varepsilon<\varepsilon_0(D)\). The
fixed-law box argument supplies one exact-size HT law \(\mu_*\), a split of
the cross-eigenspace tangent coordinates

\[
\mathfrak m=W\oplus L,\qquad
\dim_{\mathbb R}W=d-\beta k,\quad
\dim_{\mathbb R}L=\beta k,
\tag{2}
\]

and constants for which a relative displacement of size
\(O(\sqrt\varepsilon)\) in \(W\) and \(O(\varepsilon)\) in \(L\) has
variance at most \(t+\varepsilon/2\). Reserve the other half of the slack
for rational approximation below.

For the finite-word counts, \(p\) and \(q\) are fixed structural
dimensions; constants written \(O_D(\cdot)\) may depend on those fixed
dimensions and on the declared spectral datum.

**Procedural decoder theorem.** There are constants depending only on the
fixed spectral datum \(D\), a finite rational atlas, and a deterministic
decoder such that a transform library achieving \(t+\varepsilon\) can be
addressed without storing its \(K\) matrices. A codeword index has

\[
b_{\rm index}(\varepsilon)
=\kappa\log_2(1/\varepsilon)+O_D(1)
\tag{3}
\]

bits for the constructed grid library when the target resolution is declared
externally. If the message must
also declare its dyadic resolution, it adds only
\(O(\log\log(1/\varepsilon))\) bits. The decoder outputs an exactly
orthogonal or unitary rational matrix \(V\); it does not look up a stored
matrix table.

The theorem concerns the transform index and its shared decoding rule. It
does not say that this index is the description size of an atom.

It is an upper construction. A fixed bound on the represented source-word
length produces a finite source class, so it cannot by itself support an
\(\varepsilon\downarrow0\) lower bound on the library size.

## 2. A fixed rational Cayley atlas

Let \(\mathsf G=O(q)\) over \(\mathbb R\), or \(U(q)\) over
\(\mathbb C\). Write \(\mathbb Q_{\mathbb F}=\mathbb Q\) in the first case
and \(\mathbb Q(i)\) in the second. For a skew-adjoint matrix \(A\), put

\[
\operatorname{cay}(A)=(I-A)(I+A)^{-1}.
\tag{4}
\]

If the entries of \(A\) lie in \(\mathbb Q_{\mathbb F}\), this matrix is
exactly orthogonal or unitary and its entries remain in
\(\mathbb Q_{\mathbb F}\). Restrict \(A\) to the off-eigenblock
skew-adjoint complement \(\mathfrak m\); its real coordinates are the
coordinates in (2). The map

\[
A\longmapsto
\operatorname{cay}(A)D\operatorname{cay}(A)^*
\tag{5}
\]

has derivative \(-2[A,D]\). It is therefore a local coordinate map on the
orbit after restriction to \(\mathfrak m\).

Compactness supplies finitely many enlarged such charts. Their centers may
be chosen in \(\mathsf G\cap\mathbb Q_{\mathbb F}^{q\times q}\): rational
orthogonal/unitary matrices are dense, and a sufficiently close rational
replacement of each center still has an open chart. More explicitly, fix
rational centers \(C_1,\ldots,C_J\), enlarged coordinate cubes
\(\mathcal B_\alpha\subset\mathfrak m\), and compact cores
\(\mathcal B'_\alpha\Subset\mathcal B_\alpha\), such that

\[
C_\alpha\operatorname{cay}(\mathcal B'_\alpha)D
\operatorname{cay}(\mathcal B'_\alpha)^*C_\alpha^*
\tag{6}
\]

cover the orbit. The fixed number \(J\), the centers, the coordinate order,
and the chart/core pairs are shared decoder data of size \(O_D(1)\).

This construction uses no rationality of the eigenvalues of \(D\). The
rational matrices parameterize changes of encoded input basis; \(D\) enters
only in the analytical variance and chart constants.

## 3. Decoder and index count

Let

\[
\ell=\left\lceil\log_2(1/\varepsilon)\right\rceil,\qquad
r_\ell=2^{-\lceil\ell/2\rceil}.
\]

Then \(r_\ell\asymp\sqrt\varepsilon\) and
\(2^{-\ell}\asymp\varepsilon\), with constants independent of
\(\varepsilon\). Choose one positive rational constant \(c\) smaller than
the local allowance. In every enlarged cube \(\mathcal B_\alpha\), choose
coordinates \(c=(x,y)\), where \(x\) has dimension \(d-\beta k\) and
\(y\) has dimension \(\beta k\). The \(x\)-directions agree with \(W\) at
the chart basepoint. Shrink the charts if necessary so that projection from
the transported wide space to the \(x\)-coordinates is uniformly
invertible on the enlarged cube. Grid the enlarged cube, not its core, with
spacings

\[
h_W=c r_\ell,\qquad h_L=c2^{-\ell}.
\tag{7}
\]

A codeword consists of a chart label \(\alpha\), a grid integer vector
\(n=(n_x,n_y)\), and the deterministic instruction

\[
n\longmapsto A(n)\longmapsto
V(n)=C_\alpha\operatorname{cay}(A(n)).
\tag{8}
\]

Here \(A(n)\) is assembled in the declared off-eigenblock basis from the
rational coordinates \(n_xh_W,n_yh_L\). The decoder first forms \(I\pm
A(n)\), then performs exact rational matrix inversion. It follows from
(4), rather than from numerical reorthogonalization, that the output is
exactly orthogonal/unitary.

The following point is essential. Ordinary coordinate rounding does not
itself control the relative \(W/L\) displacement when the local frames vary.
For a target \(G\) in the core \(\mathcal B'_\alpha\), first round only its
\(x\)-coordinate to \(x_g\), at distance \(O(h_W)\). Let
\(V_\alpha(c)=C_\alpha\operatorname{cay}(A(c))\). For \(u\in W\), denote by
\(K_c(u)\) the corresponding transported wide skew-adjoint generator and
set

\[
\Psi_\alpha(c,u)=
V_\alpha(c)e^{K_c(u)}D e^{-K_c(u)}V_\alpha(c)^*.
\tag{9}
\]

The derivative of
\[
(y_0,u)\longmapsto\Psi_\alpha((x_g,y_0),u)
\tag{10}
\]
is invertible uniformly on the chart: \(y_0\) supplies the remaining
quotient directions, while \(u\) supplies the \(x\)-directions through the
uniformly invertible wide projection. The uniform inverse-function theorem
therefore gives \(y_0\) in the enlarged cube and \(u=O(h_W)\) for which
\(\Psi_\alpha((x_g,y_0),u)=G\). Now round \(y_0\) to \(y_g\), at distance
\(O(h_L)\). Smooth dependence and BCH composition give

\[
V_\alpha(x_g,y_g)^*GV_\alpha(x_g,y_g)
=e^{K_c(u)+E}D e^{-(K_c(u)+E)},
\qquad \|E\|=O(h_L).
\tag{11}
\]

Thus its wide component is \(O(\sqrt\varepsilon)\) and its thin component
is \(O(\varepsilon)\). The fixed-law local box estimate, after reducing
\(c\), gives variance at most \(t+\varepsilon/2\). This is the selection
argument for a grid codeword.

Every grid point in an enlarged bounded chart has a bounded number of
integer choices per coordinate. Hence the number of codewords is at most

\[
J\,C_D
h_W^{-(d-\beta k)}h_L^{-\beta k}
\le C'_D\varepsilon^{-\kappa}.
\tag{12}
\]

Equation (12) proves (3). A fixed
enumeration of bounded integer boxes converts \((\alpha,n)\) to one index
and back without a table of codeword matrices.

For a self-describing message, encode \(\ell\) by a standard
self-delimiting integer code, then use the associated dyadic grid. This
costs \(O(\log\ell)=O(\log\log(1/\varepsilon))\) shared-message bits. If
\(\varepsilon\) is already a certificate field, \(\ell\) is not part of the
transform index and (3) is the relevant count.

## 4. One common rational sampler

The ideal law \(\mu_*\) may have irrational atom probabilities and
marginals. This does not force a per-codeword law. Choose an atom support
for \(\mu_*\) of size bounded only by \(D\), for example the finite support
from the affine-polytope argument in
finite_word_shared_transform_boundary.md. Round its masses to
nonnegative rationals with total-variation error \(O_D(\varepsilon)\),
renormalizing exactly. Encode the resulting common denominator and its
finitely many numerators in

\[
B_{\rm sampler}=O_D(\log(1/\varepsilon))
\tag{13}
\]

bits. Its rational marginals \(\widehat\theta_i>0\) and HT weights
\(1/\widehat\theta_i\) are derived from those masses.

Exact arithmetic then gives unbiasedness for every decoded \(V\):

\[
\mathbb E\left[
\sum_{i\in S}
\frac{RV e_i\,(V^*x)_i}{\widehat\theta_i}
\right]=Rx.
\tag{14}
\]

The sampler approximation changes the covariance continuously by
\(O_D(\varepsilon)\). With the slack reserved in Section 1, it changes the
\(t+\varepsilon/2\) ideal-law bound to \(t+\varepsilon\). It is shared once
by the entire library. It is not included in \(b_{\rm index}\).

## 5. Payload, workspace, and arithmetic are different accounts

Assume now that the represented source
\(R\in\mathbb Q_{\mathbb F}^{p\times q}\) has coordinate numerator and
denominator bit lengths at most \(L\). Grid coordinates and every entry of
the decoded \(V\) have bit length \(O_D(\log(1/\varepsilon))\):
fixed-size rational matrix addition, multiplication, and inversion increase
a coordinate bit length by only a fixed-dimensional constant factor. Thus
each entry of

\[
P=RV
\tag{15}
\]

has bit length

\[
B_P=O_D\bigl(L+\log(1/\varepsilon)\bigr).
\tag{16}
\]

Storing all encoded columns is consequently a payload of

\[
pq\,B_P
\tag{17}
\]

bits up to a fixed rational-word coding convention. Reading exactly \(s\)
encoded columns moves

\[
ps\,B_P
\tag{18}
\]

bits under an abstract individually addressable-column model. Page grouping,
alignment, compression, and source storage format can make the physical
traffic different; (15) is not a physical-page theorem.

The decoder needs a temporary \(q\times q\) rational matrix, hence

\[
q^2O_D(\log(1/\varepsilon))
\tag{19}
\]

bits of transform workspace, apart from exact-inversion scratch space of
the same fixed-dimensional order. Decoding one index, including inversion
of \(I+A(n)\) and multiplication by the rational chart center, takes
\(O(q^3)\) exact field operations by ordinary elimination. This is an
activation cost if the decoded \(V\) is retained; it is a per-query cost if
the decoder discards \(V\) between queries. Given an already decoded
rational \(V\), evaluation of (14) takes \(O(q^2+ps)\) exact field
operations: one transform of the query and \(s\) scaled column-vector
accumulations. If \(P=RV\) is regenerated instead of stored, that is a
further \(O(pq^2)\) field-operation cost. Operand and output bit lengths
also depend on the query representation and on the chosen
arbitrary-precision arithmetic. Thus these are operation counts, not
machine-time or fixed-word bounds.

Equations (3), (13), and (15)--(19) are separate quantities. In particular,
the absence of an \(O(K)\) transform table does not remove the encoded
column payload, the shared sampler, decoder workspace, or arithmetic.

## 6. When the continuum lower bound reaches finite-word sources

The \(\Omega(\varepsilon^{-\kappa})\) lower bound in the transform-cover
theorem is a statement about the whole continuous orbit. It does not
automatically apply when source words have one fixed maximum length \(L\):
that class is finite, and a constant library can cover it while codeword
precision increases.

There is a conditional growing-word version. Suppose there is one rational
represented source \(R_0\in\mathbb Q_{\mathbb F}^{p\times q}\), of entry
bit length \(L_0\), with

\[
R_0^*R_0\in\mathcal O_D.
\tag{20}
\]

Rational orthogonal/unitary matrices are dense. Bounded rational Cayley
charts therefore give an \(O(\varepsilon)\)-net
\(\mathcal U_\varepsilon\) of \(\mathsf G\), each member having entry bit
length \(O_D(\log(1/\varepsilon))\). The finite family

\[
\{R_0U:U\in\mathcal U_\varepsilon\}
\tag{21}
\]

has source-entry length \(O_D(L_0+\log(1/\varepsilon))\), and its Gram
matrices form an \(O_D(\varepsilon)\)-net of \(\mathcal O_D\).

For completeness, \(\Phi_s\) is uniformly Lipschitz on this compact
positive-definite orbit. A uniform exactly-\(s\) HT law gives
\(\Phi_s(G)\le C_D\). For any \(\eta\)-optimal coefficient law at \(G\),
with \(\eta\le1\), its covariance \(Q\) has
\(Q_{ii}\le C_D+1\). Since \(G_{ii}\ge\lambda_{\min}(D)>0\),

\[
\mathbb E|b_i|^2\le
1+\frac{C_D+1}{\lambda_{\min}(D)}.
\tag{22}
\]

Thus \(\mathbb E\|D_b\|^2\le C'_D\). For two orbit matrices \(G,G'\),

\[
\left\|
\mathbb E[D_b^*(G'-G)D_b]-(G'-G)
\right\|
\le (C'_D+1)\|G'-G\|.
\tag{23}
\]

Using the \(\eta\)-optimal law for \(G\) at \(G'\), then interchanging
\(G,G'\) and sending \(\eta\downarrow0\), proves the Lipschitz claim.
Therefore a library that reaches \(t+\varepsilon\) on the source net (21)
reaches \(t+C_D\varepsilon\) on the full orbit. The full-orbit volume lower
bound then yields

\[
K=\Omega_D(\varepsilon^{-\kappa})
\tag{24}
\]

for any finite-word source family that contains (21), for example under a
word budget \(L(\varepsilon)\ge C_D(L_0+\log(1/\varepsilon))\).

This conditional extension needs the rational orbit point in (20). Without
it, the note retains only the constructive upper bound for declared
represented sources; it does not assert a finite-word optimality exponent.

## 7. Source and spectral scope

The exact equality in (14) is toward the represented rational matrix \(R\).
For the variance guarantee, the represented source must additionally be
declared to satisfy the analytical spectral-class condition

\[
R^*R\in\mathcal O_D.
\tag{25}
\]

The orbit may have irrational eigenvalues or irrational eigenvectors even
when \(R\) has rational entries. That is not an obstruction to forming the
rational product \(RV\), nor to exact unbiasedness in (14). It is material
if a plan claims a finite-word procedure that verifies (25), computes the
ideal probabilities, or selects the covering index from the source: none of
those procedures is supplied here. This note assumes that the source class,
the target \(\varepsilon\), and a valid index have already been declared.

For a general finite-word approximation \(\widehat R\) of a real source, the
same calculation is exactly unbiased toward \(\widehat R\), not toward the
original \(R\). The deterministic source bias and arithmetic rounding must
enter a separate Cassette execution certificate, as in
encoded_column_rounding_bound.md.

No statement here establishes encoded-byte feasibility, a native or MLX
implementation, physical hard-cap compliance, selection-observation
adequacy, or sequential composition.
