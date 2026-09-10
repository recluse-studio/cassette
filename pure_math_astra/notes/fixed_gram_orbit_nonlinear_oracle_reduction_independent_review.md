# fixed_gram_orbit_nonlinear_oracle_reduction_independent_review.md — independent audit of the fixed-Gram orbit reduction for source-independent nonlinear column oracles; depends on gaussian_static_oracle_first_chaos_reduction.md and ../../MATHS.md.

# Independent review: fixed-Gram orbit nonlinear-oracle reduction

## Verdict

The proposed reduction is correct under the stated full real orthogonal-orbit
model. For a fixed source- and query-independent support law, arbitrary
Borel output functions of the acquired columns cannot improve the minimax
value beyond the fixed-linear inverse-hull value

\[
\lambda_{\max}(M^{-1}-G),
\qquad
M=\sum_Sp_SE_SG_{SS}^{-1}E_S^T.
\tag{1}
\]

Minimizing (1) over legal support laws gives \(\nu_s(G)\). The conclusion
uses the whole group \(O(p)\), not merely \(SO(p)\), and it fails under
several excluded information models recorded below.

## 1. Exact model

Fix \(G\succ0\), \(p\ge q\), and a distribution \(p_S\) on supports
\(S\subseteq[q]\). The law is fixed before both source and query. Sources
range over

\[
\mathcal O_G=\{A\in\mathbb R^{p\times q}:A^TA=G\}.
\tag{2}
\]

For every positive-probability \(S\), let

\[
F_S:\mathbb R^{p\times |S|}\times\mathbb R^q\longrightarrow\mathbb R^p
\]

be Borel. Assume pointwise exactness

\[
\sum_Sp_SF_S(A_S,x)=Ax
\quad(A\in\mathcal O_G,\ x\in\mathbb R^q),
\tag{3}
\]

and a finite uniform unit-query risk

\[
\sum_Sp_S\|F_S(A_S,x)-Ax\|_2^2\le C
\quad(A\in\mathcal O_G,\ \|x\|_2=1).
\tag{4}
\]

Only (4) for the one unit query currently being analyzed is needed below.
It makes the Haar averages integrable. Supports with \(p_S=0\) can be
discarded.

## 2. Haar symmetrization is legitimate

For fixed unit \(x\), define on every observed orbit

\[
\overline F_S(X,x)
=\int_{O(p)}Q^TF_S(QX,x)\,dQ,
\tag{5}
\]

with normalized Haar measure. If \(X=A_S\), then (4) implies

\[
\|F_S(QX,x)\|_2
\le\|QAx\|_2+\sqrt{C/p_S},
\tag{6}
\]

for every \(Q\in O(p)\). Thus (5) is pointwise Bochner integrable. The
bound uses the uniform source risk; mere Borel measurability would not
justify this step.

Equation (3) at \(QA\), followed by multiplication by \(Q^T\) and Haar
averaging, proves

\[
\sum_Sp_S\overline F_S(A_S,x)=Ax.
\tag{7}
\]

A change of variables in Haar measure gives equivariance:

\[
\overline F_S(QX,x)=Q\overline F_S(X,x).
\tag{8}
\]

Jensen's inequality gives the orbit-averaged comparison

\[
\sum_Sp_S\|\overline F_S(A_S,x)-Ax\|_2^2
\le
\int_{O(p)}
\sum_Sp_S\|F_S((QA)_S,x)-QAx\|_2^2\,dQ
\le C.
\tag{9}
\]

The first inequality does not compare with the original risk at the same
\(A\), which need not be constant around the orbit. It proves instead that
symmetrization cannot increase the supremum of the risk over
\(\mathcal O_G\), which is the comparison used in the lower bound.

## 3. Stabilizers remove orientation and nonlinear content

For each \(S\), \(G_{SS}\succ0\), so \(X=A_S\) has full column rank.
The stabilizer of \(X\) in \(O(p)\) fixes \(\operatorname{span}X\)
pointwise and contains all orthogonal transformations on its complement.
Its fixed-vector space is \(\operatorname{span}X\). This remains true when
\(X\) is square and invertible, where the span is all of \(\mathbb R^p\).

By (8),

\[
\overline F_S(X,x)\in\operatorname{span}X.
\]

There is therefore a unique coefficient vector \(c_S(X,x)\) such that

\[
\overline F_S(X,x)=Xc_S(X,x).
\tag{10}
\]

Equivariance makes \(c_S(QX,x)=c_S(X,x)\). The set of observed matrices
for one support is exactly

\[
\{X\in\mathbb R^{p\times|S|}:X^TX=G_{SS}\}.
\tag{11}
\]

Indeed, any such \(X\) is an \(O(p)\)-image of one reference \(A_S\), and
the same left transformation extends that reference \(A\) to an element of
\(\mathcal O_G\). Since \(O(p)\) is transitive on (11),

\[
c_S(X,x)=c_S(x)
\tag{12}
\]

is independent of the source.

This disposes of the apparent orientation, determinant, cross-product, and
other nonlinear-content loopholes: all such information is changed by some
orthogonal transformation fixing the acquired columns. Averaging over that
transformation removes it without raising the worst-source risk.

## 4. The exact finite program

Substitution of (10)--(12) into (7) gives

\[
\sum_Sp_SE_Sc_S(x)=x.
\tag{13}
\]

In particular, all coordinates must occur in positive-probability supports.
It follows that \(M\) in (1) is positive definite.

For every \(A\in\mathcal O_G\), (13) gives

\[
\begin{aligned}
\sum_Sp_S\|A(E_Sc_S(x)-x)\|_2^2
&=\sum_Sp_S c_S(x)^TG_{SS}c_S(x)-x^TGx.
\end{aligned}
\tag{14}
\]

Minimizing the first term subject to (13) yields

\[
c_S^\star(x)=G_{SS}^{-1}E_S^TM^{-1}x,
\tag{15}
\]

and the exact value

\[
x^T(M^{-1}-G)x.
\tag{16}
\]

The proposed decoder may choose \(c_S(x)\) nonlinearly in \(x\), but (16)
is a pointwise convex lower bound for each \(x\). Hence

\[
\sup_{\|x\|_2=1}\ \sup_{A\in\mathcal O_G}
\sum_Sp_S\|F_S(A_S,x)-Ax\|_2^2
\ge\lambda_{\max}(M^{-1}-G).
\tag{17}
\]

Conversely, the linear rule

\[
F_S^\star(A_S,x)=A_SG_{SS}^{-1}E_S^TM^{-1}x
\tag{18}
\]

is Borel, pointwise exactly unbiased on every source, and attains (16).
Thus (17) is equality for the fixed support law. Infimizing over laws with
\(|S|\le s\) gives precisely \(\nu_s(G)\).

## 5. Query-dependent extension

Allow a Borel support law \(p_S(x)\), selected after \(x\) but independent
of \(A\), with

\[
p_S(x)>0\quad\Longrightarrow\quad |S|\le s.
\tag{19}
\]

For each fixed \(x\), the Haar argument applies with this one law and gives
the same conditional-support coefficient program. Its pointwise value is

\[
\phi_G(x)=
\inf_{\substack{\mathbb EY=x\\\|Y\|_0\le s\ {\rm a.s.}}}
\mathbb E(Y-x)^TG(Y-x).
\tag{20}
\]

Thus every such decoder has worst-orbit risk at least
\(\sup_{\|x\|=1}\phi_G(x)=\Psi_s(G)\). This lower argument is pointwise in
\(x\); measurability of the schedule is a model requirement, not an
infimum--supremum interchange.

The finite-catalog upper construction is measurable. For every
\(\varepsilon>0\), the finite-catalog bridge supplies laws
\(\mathscr L^1,\ldots,\mathscr L^K\), each operator-unbiased and row-\(s\)
sparse, such that at least one law has risk at most
\(\Psi_s(G)+\varepsilon\) at each unit \(x\). Their risks are continuous
quadratic forms. Selecting the first minimizer makes the catalog index
\(k(x)\) Borel on the unit sphere, and extending by \(k(x/\|x\|)\) away
from zero remains Borel.

There is one implicit but valid decoder step. A sampled law can have several
row-sparse operators with the same support. Conditional on the selected
catalog law and support \(S\), replace its output operator by
\(\overline L_{S,k}=\mathbb E[L\mid S,k]\). Then

\[
F_S(A_S,x)=A_S\,\overline L_{S,k(x)}x
\tag{21}
\]

depends only on the acquired columns and \(x\), preserves exact
unbiasedness, and cannot increase squared risk. Its schedule is the
support marginal induced by \(\mathscr L^{k(x)}\). This supplies the
literal Borel \(F_S(A_S,x)\) model, without granting the decoder hidden
access to a sampled full operator.

The conclusion is exactly the hard-cap value \(\Psi_s(G)\), because every
operator outcome in the catalog has at most \(s\) nonzero rows. It must not
be widened to a class satisfying only
\(\sum_Sp_S(x)|S|\le s\). That is an expected-read model; it may place
positive mass on supports larger than \(s\) and has a different pointwise
coefficient program. The static trace identity for expected reads does not
prove a hard-cap \(\Psi_s\) statement.

## 6. Attacks and exact boundaries

### Full \(O(p)\), rather than \(SO(p)\), is essential

Take \(p=q=2\), \(s=1\), and \(G=I_2\). Restrict sources to the
orientation-preserving orbit \(SO(2)\). Given the first column
\(a=Ae_1\), the second is \(Je_1\) in that moving frame:

\[
Ae_2=Ja,\qquad
J=\begin{pmatrix}0&-1\\1&0\end{pmatrix}.
\]

The one-column nonlinear-orientation rule

\[
F_{\{1\}}(a,x)=a x_1+(Ja)x_2
\tag{22}
\]

returns \(Ax\) exactly with zero error. Yet the fixed-linear value for
the full \(O(2)\) one-coordinate class is positive:
\(\nu_1(I_2)=1\), attained by the symmetric law
\(M=\tfrac12I_2\), for which \(M^{-1}-G=I_2\). The rule in (19) is
\(SO(2)\)-equivariant but is destroyed by an ambient reflection. Hence the
full \(O(p)\) orbit and its reflection stabilizers are necessary.

More generally, on an oriented \(SO(q)\) orbit a generic \(q-1\) frame has
a distinguished oriented normal. It can carry precisely the missing
orientation information. This is the higher-dimensional version of (19).

### Known Gram data does not evade the full-orbit theorem

For a fixed support \(S\), known \(G\) determines the projection of an
unobserved column onto \(\operatorname{span}A_S\). Its component in the
orthogonal complement is still moved by \(O(p-|S|)\) while \(A_S\) remains
fixed. The full orbit therefore supplies no canonical missing vector. This
is exactly the stabilizer argument in Section 3.

### Schedule or resident information changes the problem

The proof does not cover a support distribution that depends on \(A\) or on
\(x\), a resident source-dependent encoding, or extra side information
passed to \(F_S\). Such information need not be invariant under the
stabilizer of \(A_S\), and the same support weights are unavailable in
(7). Query-dependent schedule selection leads to a different, adaptive
value rather than \(\nu_s(G)\).

### Other necessary boundaries

The argument uses \(G\succ0\) to make each \(G_{SS}\) invertible and the
coefficients in (10) unique. Singular Gram matrices require a
pseudoinverse/range formulation. A finite uniform risk or another
integrability assumption is required for the pointwise Haar average. Extra
output randomness does not enlarge the class: conditional expectation given
\((S,A_S,x)\) preserves (3) and cannot increase squared risk.

## Scope

This is an exact theorem for an ideal real finite-dimensional column oracle.
It proves neither a finite-word decoder bound nor a Cassette page, byte,
metadata, rounding, or sequential-execution result. Those resource fields
remain separate under MATHS.md.
