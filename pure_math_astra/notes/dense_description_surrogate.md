# Dense low-rank description surrogate

This note records a certified surrogate for the residual-access variance of a
dense rank-constrained description.  It does not establish an exact solution
of the dense rank-constrained problem.  The argument combines the local
residual-access identity with weighted low-rank approximation; its originality
and its consequential significance for Cassette remain unestablished.

Let \(\mathbb F\) be \(\mathbb R\) or \(\mathbb C\).  For a residual matrix
\(R=[r_1\ \cdots\ r_q]\in\mathbb F^{p\times q}\), put

\[
a_i=\lVert r_i\rVert^2,\qquad T=\sum_i a_i,\qquad A=\max_i a_i.
\]

For \(a_i>0\), define

\[
 \nu(R)=\min_{\pi\in\Delta_q}\lambda_{\max}
 \left(\operatorname{diag}(a_i/\pi_i)-R^*R\right).
\]

Zero columns may be deleted before this definition and restored with zero
sampling probability.  The one-column case is understood by continuity:
\(\nu(R)=0\).

Define the energy envelope

\[
 U(R)=
 \begin{cases}
 T,&A\leq T/2,\\[2mm]
 2\sqrt{A(T-A)},&A>T/2.
 \end{cases}
\tag{1}
\]

When \(T=A\), the second expression is \(0\).  Equivalently,

\[
 U(R)=\min_{j\in[q]}\ \inf_{0<s\leq1}
 \left(s\lVert r_j\rVert^2+s^{-1}\sum_{i\ne j}\lVert r_i\rVert^2\right).
\tag{2}
\]

## The envelope theorem

**Theorem 1.**  For every residual \(R\),

\[
 \frac{U(R)}2\leq \nu(R)\leq U(R).
\tag{3}
\]

Both inequalities hold over the real and complex fields.

**Proof of the upper bound.**  First suppose \(A\leq T/2\).  Set
\(\pi_i=a_i/T\).  Then

\[
 \operatorname{diag}(a_i/\pi_i)-R^*R=TI-R^*R\preceq TI,
\]

so \(\nu(R)\leq T=U(R)\).

Now suppose \(A>T/2\), let \(h\) attain \(A\), set \(B=T-A\), and put
\(c=\sqrt{AB}\).  If \(B=0\), take \(\pi_h=1\); then the matrix above is
zero and the claim follows.  Otherwise take

\[
 \pi_h=\frac{\sqrt A}{\sqrt A+\sqrt B},\qquad
 \pi_i=\frac{a_i}{\sqrt B(\sqrt A+\sqrt B)}\quad(i\ne h).
\tag{4}
\]

Write \(R=[r_h\ R_{-h}]\), let \(x=(x_h,x_{-h})\), and set
\(u=r_hx_h\), \(v=R_{-h}x_{-h}\).  With
\(\alpha=\sqrt{B/A}=c/A\), the elementary Hilbert-space inequality gives

\[
 \lVert u+v\rVert^2\geq (1-\alpha)\lVert u\rVert^2
 -(\alpha^{-1}-1)\lVert v\rVert^2.
\]

Since \(\lVert R_{-h}\rVert_{\rm op}^2\leq
\lVert R_{-h}\rVert_F^2=B\), its right side is at least

\[
 (A-c)|x_h|^2-(c-B)\lVert x_{-h}\rVert^2.
\]

The diagonal entries of \(\operatorname{diag}(a_i/\pi_i)-2cI\) are exactly
\(A-c\) at \(h\) and \(-(c-B)\) elsewhere.  Thus
\(R^*R\succeq\operatorname{diag}(a_i/\pi_i)-2cI\), whence
\(\nu(R)\leq2c=U(R)\).

**Proof of the lower bound.**  Use the residual-access dual formula

\[
 \nu(R)=\max_{X\succeq0,\ \operatorname{tr}X=1}
 \left[\left(\sum_i\sqrt{a_iX_{ii}}\right)^2-
 \operatorname{tr}(XR^*R)\right].
\tag{5}
\]

If \(A\leq T/2\), choose diagonal \(X\) with \(X_{ii}=a_i/T\).  The first
term in (5) is \(T\), while

\[
 \operatorname{tr}(XR^*R)=\frac{\sum_i a_i^2}{T}\leq A\leq T/2.
\]

Hence \(\nu(R)\geq T/2=U(R)/2\).

If \(A>T/2\) and \(B>0\), choose the diagonal \(X\) with

\[
 X_{hh}=\frac12,\qquad X_{ii}=\frac{a_i}{2B}\quad(i\ne h).
\]

The first term in (5) is \(T/2+\sqrt{AB}\), and the second is

\[
 \frac A2+\frac{\sum_{i\ne h}a_i^2}{2B}
 \leq \frac A2+\frac B2=\frac T2.
\]

Therefore \(\nu(R)\geq\sqrt{AB}=U(R)/2\).  The case \(B=0\) has both
sides zero.  The proof uses only Hermitian quadratic forms, so it applies to
both fields. \(\square\)

For two orthogonal residual columns of equal energy \(a\), direct evaluation
gives \(\nu=a\), whereas \(U=2a\).  Thus the constant two in (3) is sharp
for the pointwise envelope comparison.  The sharp family below also shows
that two is sharp for the variance achieved by the algorithm.

## Exact optimization of the surrogate by weighted SVD

Let \(M\in\mathbb F^{p\times q}\) be a dense description target, and fix a
rank budget \(k\).  Define

\[
 U_k(M)=\min_{\operatorname{rank}B\leq k}U(M-B).
\]

For \(j\in[q]\) and \(0<s\leq1\), let

\[
 W_{j,s}=\operatorname{diag}(w_1,\ldots,w_q),\qquad
 w_j=s,\quad w_i=s^{-1}\ (i\ne j).
\]

**Theorem 2.**

\[
 U_k(M)=\min_{j\in[q]}\ \inf_{0<s\leq1}
 \sum_{\ell>k}\sigma_\ell\!\left(MW_{j,s}^{1/2}\right)^2.
\tag{6}
\]

For each fixed \((j,s)\), if \(C_k\) is a truncated rank-\(k\) singular
value decomposition of \(MW_{j,s}^{1/2}\), then

\[
 B_{j,s}=C_kW_{j,s}^{-1/2}
\tag{7}
\]

has rank at most \(k\) and attains the corresponding expression in (6).

**Proof.**  Formula (2), applied to \(R=M-B\), says

\[
 U(M-B)=\min_j\inf_{0<s\leq1}
 \lVert(M-B)W_{j,s}^{1/2}\rVert_F^2.
\]

The finite minimum in \(j\) and the joint infimum in \((B,s)\) may be
reordered.  For fixed \((j,s)\), the change of variables
\(C=BW_{j,s}^{1/2}\) preserves rank and changes the objective into

\[
 \min_{\operatorname{rank}C\leq k}
 \lVert MW_{j,s}^{1/2}-C\rVert_F^2.
\]

The Eckart--Young--Mirsky theorem gives its value and the truncated-SVD
minimizer.  Undoing the change of variables gives (6) and (7). \(\square\)

The endpoint \(s\downarrow0\) deserves separate treatment.  If deletion of
column \(j\) leaves a matrix of rank at most \(k\), take \(B\) equal to \(M\)
on every other column and take \(B_j=0\).  Then \(M-B\) has at most one
nonzero column, so \(U(M-B)=\nu(M-B)=0\).  Although its variance is zero,
one fresh exact residual-column access is still required by the access model.

Conversely, if the matrix obtained by deleting column \(j\) has rank greater
than \(k\), its rank-\(k\) Frobenius tail is positive.  The weighted error
in (6) is then at least that positive tail multiplied by \(s^{-1}\), and it
diverges as \(s\downarrow0\).  In this case the infimum for that \(j\) is
attained away from the endpoint by continuity.  This establishes all endpoint
cases without treating an infinite weight as an ordinary matrix.

## Certified dense-description approximation

Choose \((j,s)\) minimizing (6), with the endpoint construction when it
applies, and call the resulting matrix \(B_U\).  Let \(B_\nu\) minimize
\(\nu(M-B)\) over \(\operatorname{rank}B\leq k\), assuming a minimizer or
reading the display with infima.  Theorem 1 yields

\[
 \nu(M-B_U)\leq U(M-B_U)
 \leq U(M-B_\nu)\leq2\nu(M-B_\nu).
\tag{8}
\]

Thus weighted SVD gives a factor-two certified approximation to the optimal
residual-access variance within the dense rank-\(k\) description class.
Equation (4), computed from the residual of \(B_U\), is an explicit sampling
law certifying the first inequality in (8).

### A sharp obstruction to exactness of the surrogate

The weighted-SVD surrogate is not an exact solution of the dense
rank-constrained problem.  Fix \(a>0\) and \(a/4<b<a/2\), and take

\[
 M=[\sqrt a\,e_1\ \ \sqrt a\,e_2\ \ \sqrt b\,e_3\ \ \sqrt b\,e_3]
 \in\mathbb R^{3\times4},\qquad k=1.
\tag{9}
\]

If \(j\) is one of the first two columns, the three orthogonal weighted
singular energies are \(as\), \(a/s\), and \(2b/s\).  The largest is
\(a/s\), because \(a>2b\).  The weighted rank-one tail is consequently

\[
 as+\frac{2b}{s},
\]

whose minimum on \((0,1]\) is \(2\sqrt{2ab}\), at
\(s=\sqrt{2b/a}\).  The SVD removes the *other* singleton column.

If \(j\) is one of the duplicated \(e_3\) columns, the top singular energy
is again \(a/s\): indeed
\(a/s>b(s+s^{-1})\) for \(0<s\leq1\), since \(b<a/2\).  Its tail is

\[
 \frac{a+b}{s}+bs,
\]

which is minimized at \(s=1\), with value \(a+2b\).  Since

\[
 (a+2b)^2-8ab=(a-2b)^2>0,
\]

the global surrogate minimizers are exactly the singleton-indexed choices
above (up to interchanging the two equal singleton columns).  Their residual
contains one orthogonal singleton of energy \(a\) and one collinear pair of
energies \(b,b\).

For that residual, the exact variance \(t\) is the unique positive solution
of

\[
 \frac{a}{t+a}+\frac{2b}{t}=1,
\]

namely

\[
 t=b+\sqrt{b^2+2ab}.
\tag{10}
\]

The equation follows directly from the block-diagonal Gram matrix: a
singleton orthogonal block requires mass \(a/(t+a)\), and the balanced
collinear two-column block requires mass \(2b/t\).  In contrast, the rank-one
description that removes the shared \(e_3\) direction leaves two orthogonal
columns of energy \(a\), whose exact variance is \(a\).  Thus the surrogate
output has ratio at least

\[
 \frac{b+\sqrt{b^2+2ab}}{a}>1
\]

against the optimal rank-one value, and this lower bound tends to
\(\varphi=(1+\sqrt5)/2\) as \(b\uparrow a/2\).  The competitor need not be
proved globally optimal for this conclusion: the optimum is at most \(a\).
This establishes neither a universal \(\varphi\) bound nor sharpness of the
factor two in (8).  The following asymmetric family settles the latter
question.

### Sharpness of the achieved factor two

Fix \(0<\delta<1/2\), put \(x=\delta(1-\delta)\), and take

\[
 M_\delta=[e_1\ \ \delta e_2\ \ \sqrt{x}\,e_3\ \ \sqrt{x}\,e_3]
 \in\mathbb R^{3\times4},\qquad k=1.
\tag{11}
\]

There are three orthogonal rank-one column groups, with energies \(1\),
\(\delta^2\), and \(x,x\).  Capturing the first group leaves the second and
third groups.  Their total residual energy is

\[
 \delta^2+2x=2\delta-\delta^2,
\]

and its largest individual energy is \(x\), which is at most half this
total.  Thus its envelope is \(2\delta-\delta^2\).  Capturing the third
group leaves the two singleton groups and has envelope \(2\delta\).
Capturing the second group leaves the first and third groups and has envelope

\[
 2\sqrt{2x}>2\delta.
\]

The first alternative is therefore the unique envelope minimizer.

Its exact variance is the positive root of

\[
 \frac{\delta^2}{t+\delta^2}+\frac{2x}{t}=1,
\]

namely

\[
 t_\delta=x+\sqrt{x^2+2x\delta^2}
 =\delta\left(1-\delta+\sqrt{1-\delta^2}\right).
\tag{12}
\]

The competing description that captures the duplicate direction leaves the
two orthogonal singleton columns, so its variance is \(\delta\).  This is
globally optimal.  Indeed, for an arbitrary rank-one description \(B\), let
\(P\) project onto its column space.  Orthogonal decomposition gives

\[
 (M_\delta-B)^*(M_\delta-B)
 =M_\delta^*(I-P)M_\delta+C^*C\succeq M_\delta^*(I-P)M_\delta.
\]

The map \(G\mapsto\operatorname{diag}(G_{ii}/\pi_i)-G\) is positive on
positive semidefinite matrices, so \(\nu\) is monotone in this order.  It
therefore suffices to consider \(W=I-P\).  Put
\(w_g=W_{gg}\).  Then \(0\leq w_g\leq1\) and \(\sum_gw_g=2\).  At a
variance level \(t\), the three principal group blocks require probability
masses at least

\[
 \frac{w_1}{t+w_1},\qquad
 \frac{\delta^2w_2}{t+\delta^2w_2},\qquad
 \frac{2xw_3}{t}.
\]

Their sum is concave on this hypersimplex, hence is at least its minimum at
a vertex.  At \(t=\delta\), the vertex retaining the two singleton groups
has mass exactly one, while each other vertex has mass strictly greater than
one.  The same holds a fortiori for \(t<\delta\).  Thus no mixed projection,
and hence no rank-one description, has variance below \(\delta\).
Consequently

\[
 \frac{\nu(M_\delta-B_U)}{\min_{\operatorname{rank}B\leq1}\nu(M_\delta-B)}
 =1-\delta+\sqrt{1-\delta^2}\longrightarrow2
 \quad(\delta\downarrow0).
\tag{13}
\]

Together with (8), this proves that the factor two is sharp even for an
orthogonal direct sum of rank-one column groups.  It also rules out a
universal golden-ratio bound for this weighted-SVD surrogate.  The family is
a sharp approximation obstruction, not an exact solution of the general
dense description problem.

## Representation and access accounting

If the selected SVD has effective rank \(h\leq k\), its ordinary dense
factorization has \(h(p+q+1)\) field scalars when stored as left singular
vectors, singular values, and right singular vectors.  An absorbed two-factor
form uses \(h(p+q)\) field coefficients.  The access description also needs
the declared residual-column sampling data and the source-address mapping;
for example, a length-\(q\) probability table or an equivalent exact sampler.

These are counts in the same approximate scalar model used in `MATHS.md` for
dense descriptions.  They are not a claim that arbitrary real or complex
field scalars have an exact finite-byte representation.  No dense residual
matrix need be stored.  On a sampled index \(i\), reconstruct \(B_{U,:i}\)
from the factors, fetch the original column \(M_{:i}\) through the declared
source address, form \(r_i=M_{:i}-B_{U,:i}\), and use the importance-corrected
fresh residual access.  This is one fresh exact component access per draw,
including the zero-variance one-column endpoint.

## Why this is not yet the exact rank-constrained theorem

The weighted-SVD reduction is exact for \(U\), because \(U\) depends only on
weighted residual column energies.  The exact objective \(\nu\) also depends
on the residual Gram geometry.  Even for two fixed residual columns it is
affected by their inner product, whereas a weighted Frobenius objective is
not.  Therefore an exact rank-\(k\) reduction requires a nonroutine new step:
either an extremal theorem that respects the affine constraint
\(R=M-B\), \(\operatorname{rank}B\leq k\), or a solution of the coupled
low-rank semidefinite minimax problem.  A free prescribed-Gram extremal result
does not automatically provide this step, since changing a residual Gram need
not preserve the existence of a rank-\(k\) correction from the fixed \(M\).

## Appendix: concentration among orthogonal rank-one blocks

This auxiliary result concerns only descriptions whose residual Gram is an
orthogonal direct sum of rank-one blocks.  It does not prove that arbitrary
dense rank-constrained residuals reduce to that class.

For a rank-one block with total energy \(A+B\), head energy \(A\geq B\), and
variance level \(t>0\), its probability mass is

\[
 \frac{A+B-F(A,B)}t,\qquad
 F(A,B)=\frac{(A-B)_+^2}{A+B+t}.
\tag{14}
\]

For \(A\geq C\) and \(B,D\geq0\),

\[
 F(A,B)+F(C,D)\leq F(A,0)+F(C,B+D).
\tag{15}
\]

To prove this, set \(L_A(B)=F(A,0)-F(A,B)\).  For \(B<A\),

\[
 L_A'(B)=\frac{(2A+t)^2}{(A+B+t)^2}-1,
\]

and this derivative is zero for \(B\geq A\).  At fixed \(B\), it is
nondecreasing in \(A\); hence \(L_A(B)\geq L_C(B)\).  Since
\(F(C,\cdot)\) is convex and decreasing,

\[
 F(C,D)-F(C,D+B)\leq L_C(B).
\]

Adding these two comparisons proves (15).  If the proposed new head is
larger than \(C\), the left-hand saving only grows, since \(F(H,S-H)\) is
nondecreasing in the head \(H\) at fixed total \(S\).

The concentration is strict when both moved tails are positive: if \(A>C\),
the derivative comparison is strict on the active interval; if \(A=C\),
strict convexity supplies the strict inequality.  It is also strict when a
nonsingleton head strictly exceeds a singleton head and its tail is positive.
The remaining equalities arise from a zero moved tail or tied heads with a
zero tail; ties may therefore leave multiple labelled partitions.

Repeated concentration makes the largest available heads singleton blocks.
If fewer than the permitted number of blocks are used, splitting a
nonsingleton block creates an additional singleton and improves the mass
unless an equality case applies.  Consequently, within this orthogonal
rank-one partition class with \(q>p\), one optimal labelled form has
\(a_1,\ldots,a_{p-1}\) as singleton blocks and
\(a_p,\ldots,a_q\) in the remaining rank-one block, after sorting
\(a_1\geq\cdots\geq a_q\).  Ties prevent a stronger uniqueness statement.
