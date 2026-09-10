# Resident descriptions and hard-capped page access

This note records finite-dimensional statements about the fixed, query-independent
residual-access model. It does not assert novelty, does not change `MATHS.md`, and
does not supply a byte-level implementation. The word “description” has two
different meanings below. The rank-only statements allow arbitrary dense real or
complex matrices with exact coefficients. Cassette instead admits only a declared
encoded-byte and metadata class; rank is not a substitute for that class.

## 1. Fixed-law residual variance

Let \(R\in\mathbb F^{p\times q}\), \(G=R^*R\succeq0\), and write
\(a_j=G_{jj}\). For a positive probability vector \(\pi\), one residual-column
Horvitz--Thompson draw has worst-unit-query covariance

\[
 Q_\pi(G)=\operatorname{Diag}(a_j/\pi_j)-G,
 \qquad
 \nu(G)=\inf_\pi\lambda_{\max}(Q_\pi(G)).
\]

Zero diagonal entries may be deleted, or the expression may be interpreted by its
continuous boundary extension. In particular, a residual supported on one column
has \(\nu=0\): the sampling law concentrates on that column. This says that the
random residual correction has zero variance. It says neither that the page has
zero cost nor that it is resident.

### Lemma 1 (PSD monotonicity)

If \(G,H\succeq0\), then \(\nu(G+H)\geq\nu(G)\).

**Proof.** For every \(\pi\),

\[
 Q_\pi(G+H)=Q_\pi(G)+Q_\pi(H).
\]

The second summand is positive semidefinite because it is the covariance matrix
of the one-column Horvitz--Thompson estimator for a Gram matrix \(H\). Hence
\(\lambda_{\max}(Q_\pi(G+H))\geq\lambda_{\max}(Q_\pi(G))\geq\nu(G)\).
Taking the infimum over \(\pi\) proves the claim. \(\square\)

We use the established zero criterion

\[
 \nu(R^*R)=0 \quad\Longleftrightarrow\quad
 R\text{ has at most one nonzero column}. \tag{1}
\]

For completeness, suppose two columns \(i,h\) have \(a_i,a_h>0\).  For every
\(\pi\), \(\lambda_{\max}(Q_\pi)\geq
a_i(1/\pi_i-1)\).  If a sequence of such largest eigenvalues tended to zero,
then \(\pi_i\) would tend to one.  The same argument makes \(\pi_h\) tend to
one, which is impossible for a probability vector.  Thus \(\nu>0\) with two
nonzero columns. The reverse direction is the boundary law described above.

## 2. Rank-only resident descriptions reduce to output projections

For an exact dense rank budget \(k\), define

\[
 d_k(A)=\inf_{\operatorname{rank}B\leq k}
 \nu\bigl((A-B)^*(A-B)\bigr).
\]

### Theorem 2 (projection reduction)

\[
 d_k(A)=
 \min_{\substack{P=P^*=P^2\\\operatorname{rank}P\leq k}}
 \nu\bigl(A^*(I-P)A\bigr). \tag{2}
\]

In particular, a rank-only optimum exists and can be chosen as \(B=PA\).

**Proof.** Let \(B\) have rank at most \(k\), and let \(P\) be the orthogonal
projection onto \(\operatorname{ran}B\). Then

\[
 A-B=(I-P)A+(PA-B).
\]

The two terms have orthogonal output ranges. Therefore

\[
 (A-B)^*(A-B)
 =A^*(I-P)A+(PA-B)^*(PA-B).
\]

Lemma 1 gives the lower bound by \(\nu(A^*(I-P)A)\). Conversely, for every
admissible \(P\), the choice \(B=PA\) has rank at most \(k\) and makes the
second summand vanish. This proves equality of the infima.

The set of orthogonal projections of rank at most \(k\) is a finite union of
compact Grassmannians. The density-matrix dual for \(\nu\) makes \(\nu\)
continuous on the positive semidefinite cone. Thus the right side attains its
minimum. \(\square\)

This theorem is deliberately narrow. A dense projection normally requires dense
coefficients and a decoder. Equation (2) does not establish that \(PA\) belongs
to Cassette's \(\mathcal C_{b_{\rm desc},b_{\rm meta}}(A)\), that it fits a byte
budget after quantization, or that its residual pages can be addressed within the
metadata budget.

### Corollary 3 (the exact zero criterion)

\[
 d_k(A)=0
 \quad\Longleftrightarrow\quad
 \exists j:\ \operatorname{rank}(A_{:\,[q]\setminus\{j\}})\leq k. \tag{3}
\]

**Proof.** If the displayed deletion has rank at most \(k\), project onto its
column span. The residual has at most column \(j\) nonzero, so (1) gives zero.

Conversely, attainment in Theorem 2 gives a projection \(P\) for which
\(\nu(A^*(I-P)A)=0\). By (1), \((I-P)A\) has at most one nonzero column \(j\).
Every other column of \(A\) is then in \(\operatorname{ran}P\), so its deletion
has rank at most \(\operatorname{rank}P\leq k\). \(\square\)

If \(r=\operatorname{rank}A\), deleting one column lowers rank by at most one.
Consequently \(d_k(A)>0\) for \(k\leq r-2\); \(d_k(A)=0\) for \(k\geq r\); and
at \(k=r-1\) it vanishes exactly when some column is a coloop, namely when its
deletion lowers rank. The positivity assertion is genuine rather than merely an
unattained infimum, by compact attainment in Theorem 2.

### Theorem 4 (codimension-one scalar spectral identity)

Assume \(A\in\mathbb F^{p\times q}\) has full row rank, put \(S=AA^*\), and
write \(a_j=A_{:j}\), \(C_j=a_ja_j^*\), and \(B_j=S-C_j\).  Then

\[
 d_{p-1}(A)=
 \min_{1\leq j\leq q}\ \inf_{0<s\leq1}
 \lambda_{\min}\bigl(sC_j+s^{-1}B_j\bigr). \tag{4}
\]

**Proof.**  We first prove the rank-one formula used below.  Let
\(G=zz^*\), \(\alpha_i=|z_i|^2\), \(T=\sum_i\alpha_i\), and
\(m=\max_i\alpha_i\).  With \(b=T-m\),

\[
 \nu(zz^*)=
 \inf_{0<s\leq1}\left(sm+\frac b s\right)
 =
 \begin{cases}
 T,&m\leq b,\\
 2\sqrt{mb},&m\geq b.
 \end{cases} \tag{5}
\]

For the dominant lower bound, compress \(Q_\pi\) to the span of the dominant
coordinate and the normalized tail \(z_{-h}/\sqrt b\).  If \(p=\pi_h\),
Cauchy--Schwarz makes the lower-right diagonal entry at least
\(bp/(1-p)\).  The compression therefore has largest eigenvalue at least that
of

\[
 \begin{pmatrix}
 m(1-p)/p&-\sqrt{mb}\\
 -\sqrt{mb}&bp/(1-p)
 \end{pmatrix},
\]

whose determinant is zero and whose nonzero eigenvalue is
\(m(1-p)/p+bp/(1-p)\).  Minimizing in \(p\) gives \(2\sqrt{mb}\).

If \(m\leq b\), the density-matrix dual gives the stronger lower bound \(T\).
Indeed, choose vectors of lengths \(\alpha_i/\sqrt T\) which close to a polygon;
such vectors exist precisely because no length exceeds the sum of the others.
Their Gram matrix \(X\) is positive semidefinite, has trace one and diagonal
\(\alpha_i/T\), and satisfies \(Xz=0\), after absorbing the phases of \(z\).
The dual value is then
\((\sum_i\sqrt{\alpha_iX_{ii}})^2-z^*Xz=T\).

For the matching balanced upper bound, take \(\pi_i=\alpha_i/T\); then
\(Q_\pi=TI-zz^*\).  In the dominant case take

\[
 \pi_h=\frac{\sqrt m}{\sqrt m+\sqrt b},\qquad
 \pi_i=\frac{\alpha_i}{b}\frac{\sqrt b}{\sqrt m+\sqrt b}\quad(i\ne h).
\]

The two-dimensional compression has largest eigenvalue \(2\sqrt{mb}\), while
the tail-orthogonal eigenvalues equal \(b+\sqrt{mb}\leq2\sqrt{mb}\).  This
proves (5), including its one-column boundary by continuity.  The scalar minimum
in (5) follows directly by minimizing \(sm+b/s\) on \((0,1]\).

Return now to \(d_{p-1}\).  In (2), a projection of rank below \(p-1\) may be
enlarged to one of rank \(p-1\); its residual Gram decreases in PSD order, so
Lemma 1 shows that this cannot worsen the objective.  Write the complementary
rank-one projection as \(uu^*\), \(\|u\|=1\).  The residual Gram is rank one,
with

\[
 T=u^*Su,\qquad \alpha_j=u^*C_ju,\qquad m=\max_j\alpha_j.
\]

For \(0<s\leq1\),

\[
 s\alpha_j+\frac{T-\alpha_j}{s}
 =\frac Ts-\left(\frac1s-s\right)\alpha_j,
\]

so minimizing over \(j\) selects a largest \(\alpha_j\).  Formula (5) and
interchange of infima over the product of \(u\), \(j\), and \(s\) yield

\[
 d_{p-1}(A)=\min_{j,s}\min_{\|u\|=1}
 u^*(sC_j+s^{-1}B_j)u,
\]

which is (4). \(\square\)

There is one important boundary in (4).  If \(B_j\succ0\), then
\(\lambda_{\min}(sC_j+s^{-1}B_j)\to\infty\) as \(s\downarrow0\), so its
infimum is attained at a positive \(s\); a bottom eigenvector gives an optimal
residual direction.  If \(B_j\) is singular, full row rank of \(S=B_j+C_j\)
forces \(\operatorname{rank}B_j=p-1\) and
\(\ker B_j\cap\ker C_j=\{0\}\).  For unit \(u\in\ker B_j\),

\[
 \lambda_{\min}(sC_j+s^{-1}B_j)\leq s\,u^*C_ju\longrightarrow0.
\]

The scalar infimum is then zero but is not attained at positive \(s\).  The
outer projection is nevertheless attained: that \(u\) is orthogonal to every
column except possibly \(j\), so the residual has one nonzero column and has
zero variance under (1).

### Example 5 (SVD truncation need not minimize access variance)

Take

\[
 A=\begin{pmatrix}2&1\\0&1\end{pmatrix},\qquad k=1.
\]

With \(P=e_1e_1^*\), \(PA\) has rank one and

\[
 A-PA=\begin{pmatrix}0&0\\0&1\end{pmatrix}.
\]

Thus \(d_1(A)=0\). The top left singular vector of \(A\) is neither coordinate
axis, since \(AA^*=\bigl(\begin{smallmatrix}5&1\\1&1\end{smallmatrix}\bigr)\).
Its rank-one SVD residual has two nonzero columns, hence has strictly positive
\(\nu\) by (1). The spectral head is strictly suboptimal for this rank-only
objective. This does not compare byte-bounded descriptions.

## 3. Hard-capped grouped pages

Partition residual columns into page blocks \(R=[R_1\ \cdots\ R_m]\), with
corresponding query blocks \(x_g\). Let \(B\) contain all resident linear
contributions. The following visibility model is explicit: for an acquired page
set \(S\),

\[
 Y_S(x)=Bx+\sum_{g\in S}L_{Sg}x_g, \tag{4}
\]

where \(L_{Sg}\) may use the acquired block, the set \(S\), and resident metadata.
No unrepresented \(R_g\) may contribute when \(g\notin S\). This is the model
in which “only pages read may contribute” has mathematical content.

### Theorem 5 (hard-cap zero-variance law)

Suppose every supported \(S\) obeys \(\sum_{g\in S}c_g\leq C\), where \(c_g\)
is the actual page-byte cost. An unbiased estimator of form (4) has zero variance
for every query if and only if every page in

\[
 H=\{g:R_g=A_g-B_g\ne0\}
\]

belongs to every supported set \(S\). Equivalently, exact execution is possible
under this model if and only if

\[
 \sum_{g\in H}c_g\leq C. \tag{5}
\]

For a cardinality cap \(|S|\leq s\), replace (5) by \(|H|\leq s\).

**Proof.** Unbiased zero variance implies \(Y_S(x)=Ax\) for every supported
\(S\) and every \(x\). If \(g\notin S\), choose \(x\) supported only on page
\(g\). The sum in (4) vanishes and gives \(B_gx_g=A_gx_g\) for every \(x_g\),
so \(R_g=0\). Hence every nonzero residual page is always included.

Conversely, if every page in \(H\) fits under the cap, choose it deterministically
and use \(L_{Sg}=R_g\). Then (4) equals \(Ax\) identically. \(\square\)

No correlation among page outputs changes this theorem. Even if two \(R_g\)'s
are collinear, their query blocks are independently variable. In particular, an
exact plan with one fresh page has residual support on at most one page; every other
page must already be reconstructed by \(B\). This is a variance statement with a
hard physical cap, not an expected-traffic assertion.

#### Scope boundary: a resident query transform changes the model

The preceding conclusion applies only to the visibility decomposition (4), which
forbids an unread query block from entering the correction. It is not a general
hard-cap impossibility theorem for a system permitted to store and decode a global
linear transform of the query.

For example, suppose every singleton residual column has the form
\(R_{:g}=c_gu\), with a fixed nonzero vector \(u\). Store the coefficients
\((c_g)_g\) resident. On reading any page \(g_0\) with \(c_{g_0}\ne0\), recover
\(u=R_{:g_0}/c_{g_0}\) and return

\[
 u\sum_g c_gx_g=Rx.
\]

This is exact with one acquired page even though most original pages are omitted.
It is legal only when the coefficient payload, its precision, the decoder, and
the query transform are declared resident resources. Algebraically it factors as
\(R=PF\), where \(F:x\mapsto\sum_gc_gx_g\) is resident and \(P:z\mapsto uz\)
is supplied by the acquired page. It is excluded by (4), not contradicted by
Theorem 5. Any application of that theorem must state this visibility restriction.

### Proposition 6 (pairwise law for fixed-subset Horvitz--Thompson sampling)

Let \(S\) be a random hard-safe page subset, let \(\pi_g=\Pr(g\in S)>0\), and
let \(\pi_{gh}=\Pr(g,h\in S)\), with \(\pi_{gg}=\pi_g\). The canonical estimator

\[
 Z_S(x)=\sum_{g\in S}\frac{R_gx_g}{\pi_g}
\]

is unbiased. Its worst-unit-query covariance has \((g,h)\) block

\[
 [Q]_{gh}=
 \left(\frac{\pi_{gh}}{\pi_g\pi_h}-1\right)R_g^*R_h. \tag{6}
\]

**Proof.** Write \(I_g=\mathbf1\{g\in S\}\). The coefficient of
\(R_gx_g\) is \(I_g/\pi_g-1\), whose mean is zero. Its pairwise second moment
is \(\pi_{gh}/(\pi_g\pi_h)-1\). Expanding the squared norm gives (6).
\(\square\)

Thus pairwise inclusion moments determine the covariance of this *specified*
Horvitz--Thompson class. They do not themselves prove that a hard-safe sampling
law exists. The exact feasible object is

\[
 \operatorname{conv}\{(z,zz^*):z\in\{0,1\}^m,\ \sum_gc_gz_g\leq C\}. \tag{7}
\]

For an exact-cardinality design add \(\mathbf1^*z=s\). Membership in (7)
supplies a distribution supported on legal subsets. Marginal identities, local
probability bounds, and positive-semidefinite conditions alone are not such a
construction. If one permits arbitrary subset-dependent control variates beyond
(6), further conditional coefficient moments enter and the pairwise formula is no
longer the whole optimization.

## 4. Omitting exactly one singleton page

Now take singleton pages and omit \(J\) with probabilities \(w_i\geq0\),
\(\sum_iw_i=1\). Every realized subset reads the other \(q-1\) pages. Put

\[
 \pi_i=1-w_i,\qquad c_i=\frac{w_i}{1-w_i}.
\]

The Horvitz--Thompson correction is

\[
 Z_J(x)=\sum_{i\ne J}\frac{r_ix_i}{1-w_i}.
\]

For every active residual column \(a_i>0\), unbiasedness requires \(w_i<1\).
The boundary \(w_i=0\) is legal: page \(i\) is then read on every realization
and its odds are \(c_i=0\). A boundary \(w_i=1\) gives zero inclusion probability
to page \(i\) and is inadmissible unless \(R_{:i}=0\), in which case that column
should first be deleted from the residual problem.

### Proposition 7 (correct all-but-one covariance)

For \(G=R^*R\), the covariance matrix is

\[
 Q(w)=\operatorname{Diag}\!\left(\frac{a_iw_i}{(1-w_i)^2}\right)
       -D_cGD_c,\qquad D_c=\operatorname{Diag}(c_i). \tag{8}
\]

Equivalently, \(Q_{ii}=a_ic_i\) and \(Q_{ij}=-c_ic_jG_{ij}\) for \(i\ne j\).

**Proof.** With \(v_i=r_ix_i\), the error when \(J=j\) is

\[
 E_j=\sum_{i\ne j}c_iv_i-v_j.
\]

For a fixed \(i\), its random coefficient has second moment

\[
 (1-w_i)c_i^2+w_i=c_i.
\]

For \(i\ne h\), its cross moment is

\[
 (1-w_i-w_h)c_ic_h-w_ic_h-w_hc_i=-c_ic_h.

\]

Substitution into \(\mathbb E\|E_J\|_2^2\) proves (8). \(\square\)

The alternative expression with a **plus** \(D_cGD_c\) has the wrong
off-diagonal sign. Omission events are negatively correlated.

The exact all-but-one minimax problem in this estimator class is therefore

\[
 \inf_{\substack{w_i\geq0,\ \sum_iw_i=1\\w_i<1\ \mathrm{when}\ a_i>0}}
\lambda_{\max}(Q(w)). \tag{9}
\]

When \(q=2\), omission probabilities are the complementary singleton inclusion
probabilities, so (9) is exactly the ordinary one-column problem and inherits its
convex formulation. The issue below begins at \(q\geq3\): it is not the
independent singleton problem with a renamed probability vector.
The matrix map in (8) is not Loewner-convex in \(w\), so the usual matrix-convex
epigraph route does not establish convexity of (9). For example, take
\(G=\mathbf1\mathbf1^*\),

\[
 u=(1/10,1/5,7/10),\quad
 v=(1/5,1/10,7/10),\quad m=(u+v)/2.
\]

For the vector \(\mathbf1\), direct substitution gives

\[
 \mathbf1^*Q(u)\mathbf1=\mathbf1^*Q(v)\mathbf1=103/108,
 \qquad
 \mathbf1^*Q(m)\mathbf1=847/867,
\]

and

\[
 \mathbf1^*\left(\frac{Q(u)+Q(v)}2-Q(m)\right)\mathbf1
 =-\frac{725}{31212}<0.
\]

Thus \(Q((u+v)/2)\npreceq[Q(u)+Q(v)]/2\). Reparameterizing by odds does not
give a convex feasible domain: its constraint is

\[
 \sum_i\frac{c_i}{1+c_i}=1,
\]

an equality level set of a nonlinear concave function. These facts do not by
themselves prove that the scalar objective in (9) is nonconvex; they show that a
convex-program or minimax-dual claim requires an additional argument.

For an explicit failure of convexity of the odds feasible set, the odds vectors
corresponding to \(u\) and \(v\) above are
\((1/9,1/4,7/3)\) and \((1/4,1/9,7/3)\).  Their midpoint is
\((13/72,13/72,7/3)\), for which

\[
 2\frac{13}{85}+\frac7{10}=\frac{171}{170}\ne1.
\]

It therefore does not represent a legal omission law.

### Interior scalar-curvature reduction

There is a precise remaining route to scalar convexity.  Let \(w(t)=w+th\),
where \(\mathbf1^*h=0\) and every active coordinate remains strictly between zero
and one.  Put \(D=\operatorname{Diag}(c_i)\),
\(D_1=\operatorname{Diag}(\dot c_i)\), and
\(D_2=\operatorname{Diag}(\ddot c_i)\), where

\[
 \dot c_i=\frac{h_i}{(1-w_i)^2},\qquad
 \ddot c_i=\frac{2h_i^2}{(1-w_i)^3}.
\]

Direct differentiation of (8) gives

\[
 \dot Q=
 \operatorname{Diag}\bigl(a_i\dot c_i(1+2c_i)\bigr)
 -D_1GD-DGD_1,
\]

\[
 \ddot Q=
 \operatorname{Diag}\bigl(a_i[\ddot c_i(1+2c_i)+2\dot c_i^2]\bigr)
 -D_2GD-DGD_2-2D_1GD_1. \tag{11}
\]

If the top eigenvalue \(\lambda\) of \(Q\) is simple, with unit eigenvector
\(x\), standard Hermitian eigenvalue perturbation gives

\[
 \ddot\lambda
 =x^*\ddot Qx+
 2\sum_{\ell:\,\lambda_\ell<\lambda}
 \frac{|x_\ell^*\dot Qx|^2}{\lambda-\lambda_\ell}. \tag{12}
\]

The second term is nonnegative.  Formula (11) has no sign in PSD order, as the
preceding example shows.  Thus a proof of scalar convexity would have to prove
that the nonnegative eigenvector-rotation term in (12) always compensates every
negative top-ray term, including the multiple-eigenvalue boundary by a separate
spectral-subdifferential argument.  No such inequality is proved here.  Conversely,
an analytic scalar counterexample can be obtained by finding \(G,w,h\) for which
the right side of (12) is negative at a simple top eigenvalue.  This reduction is
valid only in the interior; at \(w_i=0\), it supplies a one-sided boundary problem.

The always-valid spectral variational representation is only

\[
 \inf_{w\in\Delta_q^\circ}\ \max_{X\succeq0,\ \operatorname{tr}X=1}
 \operatorname{tr}(XQ(w)). \tag{10}
\]

Unlike the independent-column problem, (8) supplies neither a proved
convex--concave structure nor a justified interchange of the infimum and maximum.
Whether (9) nevertheless has a useful exact dual or a different convex
reparameterization is open in this note. Any such result must retain the hard
per-subset page cap and the restricted estimator class stated above.

### Fixed-level diagonal feasibility reformulation

For \(t>0\) and an interior omission law, (8) also has the factorization

\[
 Q(w)=D_c\left[\operatorname{Diag}\left(\frac{a_i}{w_i}\right)-G\right]D_c.
\]

Consequently, congruence by the invertible \(D_c\) gives the exact equivalence

\[
 Q(w)\preceq tI
 \quad\Longleftrightarrow\quad
 G\succeq\operatorname{Diag}(f_i(w_i;t)), \tag{13}
\]

where

\[
 f_i(w;t)=\frac{a_i}{w}-\frac{t(1-w)^2}{w^2}.
\]

The diagonal condition in (13) forces
\(w_i\leq t/(a_i+t)\).  On that interval,

\[
 f_i'(w;t)=\frac{2t-(a_i+2t)w}{w^3}>0,
 \qquad
 f_i''(w;t)=\frac{2[(a_i+2t)w-3t]}{w^4}<0. \tag{14}
\]

Thus \(f_i\) has an increasing convex inverse on \(( -\infty,a_i]\), namely

\[
 h_i(u;t)=
 \frac{2t}{a_i+2t+\sqrt{a_i^2+4t(a_i-u)}}. \tag{15}
\]

Define the downward-closed spectrahedron

\[
 \mathcal U_G=\{u\in\mathbb R^q:G-\operatorname{Diag}(u)\succeq0\}.
\]

Its diagonal inequalities already imply \(u_i\leq a_i\).  Equations
(13)--(15) prove the following exact level-set test:

\[
 \exists\ w\in\Delta_q^\circ:\ Q(w)\preceq tI
 \quad\Longleftrightarrow\quad
 \exists\ u\in\mathcal U_G:\ \sum_i h_i(u_i;t)\geq1. \tag{16}
\]

For the forward direction, take \(u_i=f_i(w_i;t)\), so that the sum in (16)
is one.  Conversely, set \(w_i=h_i(u_i;t)\).  If the resulting sum exceeds
one, decrease selected \(u_i\)'s continuously until it equals one; downward
closure of \(\mathcal U_G\) preserves feasibility, and (15) makes the resulting
\(w\) a probability vector.  Equation (13) then applies.

The formula is an exact reformulation, not a convex optimization certificate:
each \(h_i\) is convex, and (16) maximizes their sum over a convex spectrahedron.
At a legal always-read boundary \(w_i=0\), one has \(u_i\to-\infty\) and
\(h_i(u_i;t)\to0\). Thus the closed-simplex version replaces the existential
condition on the right of (16) by its supremum being at least one; a limiting
maximizer represents an always-read coordinate. An active \(w_i=1\) remains
inadmissible as stated above.
