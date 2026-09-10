# fixed_gram_orbit_static_oracle_minimax_independent_proof.md — exact minimax reduction for fixed-Gram-orbit static column oracles; depends on gaussian_static_oracle_first_chaos_reduction.md and ../../MATHS.md.

## Theorem

Fix \(G\in\mathbb R^{q\times q}\) positive definite and \(p\ge q\). Let

\[
\mathcal O_G=\{A\in\mathbb R^{p\times q}:A^TA=G\}.
\]

Fix a distribution \((p_S)\) on supports \(S\subseteq[q]\). It is chosen
before the source and query. A decoder observes only \(A_{:S}\), returns a
Borel vector \(F_S(A_{:S},x)\in\mathbb R^p\), and satisfies

\[
\sum_Sp_SF_S(A_{:S},x)=Ax
\qquad(A\in\mathcal O_G,\ x\in\mathbb R^q).
\tag{1}
\]

For this fixed schedule, define

\[
M=\sum_{S:p_S>0}p_SE_SG_{SS}^{-1}E_S^T.
\tag{2}
\]

Then \(M\succ0\), and the exact static-oracle minimax value is

\[
\inf_F\ \sup_{A\in\mathcal O_G}\ \sup_{\|x\|_2=1}
\sum_Sp_S\|F_S(A_{:S},x)-Ax\|_2^2
=\lambda_{\max}(M^{-1}-G).
\tag{3}
\]

The infimum ranges over arbitrary Borel decoders satisfying (1) and finite
uniform worst-source, worst-unit-query risk. Internal random output choices
do not change the value: conditional expectation given \((S,A_{:S},x)\)
preserves (1) and weakly lowers squared risk.

Consequently, minimizing (3) over an allowed family of source-independent
support schedules gives exactly that family's fixed-linear support value.
In particular, if \(\nu_s(G)\) denotes the infimum over the declared
hard-cap schedule class \(|S|\le s\), then the arbitrary nonlinear oracle
value equals \(\nu_s(G)\).

## Lower bound

Fix a decoder and a unit \(x\). For each positive-probability support,
finite uniform risk and \(A^TA=G\) imply

\[
\|F_S(A_{:S},x)\|_2
\le \|F_S(A_{:S},x)-Ax\|_2+\sqrt{x^TGx}
\le \sqrt{C/p_S}+\sqrt{x^TGx}
\tag{4}
\]

on the orbit, where \(C\) is the decoder's uniform risk bound. Thus all
terms in the following Haar average are pointwise integrable. Put

\[
\overline F_S(X,x)
=\int_{O(p)}O^TF_S(OX,x)\,d\mu(O),
\tag{5}
\]

where \(\mu\) is normalized Haar measure. For \(A\in\mathcal O_G\), every
\(OA\) also lies in \(\mathcal O_G\), so (1) gives

\[
\sum_Sp_S\overline F_S(A_{:S},x)=Ax.
\tag{6}
\]

Haar invariance gives left equivariance

\[
\overline F_S(QX,x)=Q\overline F_S(X,x)
\qquad(Q\in O(p)).
\tag{7}
\]

Jensen's inequality, followed by the uniform risk bound on \(OA\), shows
that the averaged decoder has no larger worst-orbit risk.

For \(X=A_{:S}\), the stabilizer

\[
\{Q\in O(p):QX=X\}
\]

acts as the full orthogonal group on \(\operatorname{span}(X)^\perp\).
Equations (7) and \(QX=X\) therefore force
\(\overline F_S(X,x)\in\operatorname{span}(X)\). Since
\(G_{SS}\succ0\), the columns of \(X\) are independent, so there is a
unique coefficient vector \(c_S(x)\) with

\[
\overline F_S(A_{:S},x)=A_{:S}c_S(x)=AE_Sc_S(x).
\tag{8}
\]

The coefficients do not depend on \(A\). Indeed, \(O(p)\) acts transitively
on \(\mathcal O_G\): if \(A,A'\in\mathcal O_G\), the isometry
\(Av\mapsto A'v\) on their column spans extends to an orthogonal matrix
\(Q\) with \(A'=QA\). Equation (7) and uniqueness in (8) then identify
the two coefficient vectors. For \(S=\varnothing\), the stabilizer is all
of \(O(p)\), so \(\overline F_\varnothing=0\); it contributes nothing.

Because every \(A\in\mathcal O_G\) has full column rank, (6) implies

\[
\sum_Sp_SE_Sc_S(x)=x.
\tag{9}
\]

The averaged risk is consequently

\[
\begin{aligned}
\sum_Sp_S\|\overline F_S(A_{:S},x)-Ax\|_2^2
&=\sum_Sp_S(E_Sc_S(x)-x)^TG(E_Sc_S(x)-x)\\
&=\sum_Sp_Sc_S(x)^TG_{SS}c_S(x)-x^TGx.
\end{aligned}
\tag{10}
\]

Minimizing (10) under (9) gives the Lagrange equations

\[
G_{SS}c_S=E_S^T\lambda,\qquad M\lambda=x.
\tag{11}
\]

Exactness for every query makes (9) feasible for every \(x\), hence
\(M\succ0\). The minimum of (10) is

\[
x^T(M^{-1}-G)x.
\tag{12}
\]

Taking the largest unit eigenvector proves the lower half of (3).

## Attainment by a linear decoder

For every support with \(p_S>0\), set

\[
c_S(x)=G_{SS}^{-1}E_S^TM^{-1}x,
\qquad
F_S(A_{:S},x)=A_{:S}c_S(x).
\tag{13}
\]

Then \(\sum_Sp_SE_Sc_S(x)=MM^{-1}x=x\), so (1) holds on the whole
orbit. Equation (10) equals (12) for every \(A\), and its unit-query
supremum is \(\lambda_{\max}(M^{-1}-G)\). This proves equality in (3).

## Expected reads

The proof uses no hard-cap property. If a schedule has expected support
count

\[
\bar s=\sum_Sp_S|S|,
\]

then its moment matrix obeys the exact identity

\[
\operatorname{tr}(GM)
=\sum_Sp_S\operatorname{tr}(G_{SS}G_{SS}^{-1})
=\bar s.
\tag{14}
\]

If its minimax risk is at most \(v\), then
\(M^{-1}-G\preceq vI\), hence

\[
M\succeq(G+vI)^{-1}
\quad\Longrightarrow\quad
\bar s\ge\operatorname{tr}\bigl(G(G+vI)^{-1}\bigr).
\tag{15}
\]

Thus every static source- and query-independent schedule, including one
that occasionally reads all \(q\) columns, obeys the same necessary
expected-read lower bound. A hard cap \(|S|\le s\) simply adds
\(\bar s\le s\).

## Scope

The result is real, uses a source-independent schedule, and assumes
pointwise exactness on the fixed Gram orbit. It permits arbitrary nonlinear
dependence on fetched columns and the query, and arbitrary output vectors.
It does not address source-trained resident state, schedules that depend on
the source or query, approximate or average-only unbiasedness, finite-word
source selection, or physical pages. The proof is an invariance and convex
quadratic reduction; no novelty claim is made.

## Query-dependent schedules

The same orbit argument gives the matching query-dependent identity. Allow
\(p_S(x)\) to be a measurable support law selected after \(x\), but still
independent of \(A\). For one fixed nonzero \(x\), a finite-risk decoder
has the pointwise orbit bound used in (4), so Haar averaging applies to
that one law. It reduces every exact decoder to coefficients
\(c_S(x)\) satisfying

\[
\sum_Sp_S(x)E_Sc_S(x)=x.
\tag{16}
\]

Define the pointwise sparse-coefficient value

\[
\phi_G(x)=
\inf_{\substack{\mathbb EY=x\\\|Y\|_0\le s\ {\rm a.s.}}}
\mathbb E(Y-x)^TG(Y-x).
\tag{17}
\]

Conditioning a feasible \(Y\) on its support and using Jensen shows that
the infimum in (17) is the same finite support-and-coefficient program
that results from (16). Conversely, each such coefficient program is
implemented by \(F_S(A_{:S},x)=A_{:S}c_S(x)\). Hence every
query-dependent orbit decoder has, for each \(x\),

\[
\sup_{A\in\mathcal O_G}
\sum_Sp_S(x)\|F_S(A_{:S},x)-Ax\|_2^2
\ge\phi_G(x).
\tag{18}
\]

Taking the outer supremum only now gives

\[
\inf_{(p_S(\cdot),F)}
\sup_{\|x\|=1}\sup_{A\in\mathcal O_G}
\sum_Sp_S(x)\|F_S(A_{:S},x)-Ax\|_2^2
\ge\sup_{\|x\|=1}\phi_G(x)
=\Psi_s(G).
\tag{19}
\]

There is no infimum--supremum interchange in (18)--(19).

For the converse, the finite-catalog bridge supplies, for every
\(\varepsilon>0\), finitely many operator-unbiased row-\(s\)-sparse laws.
For every unit \(x\), at least one has \(G\)-risk at most
\(\Psi_s(G)+\varepsilon\). Select the first least-risk law in a fixed
ordering. Since the finitely many risks are continuous quadratic forms,
this selector is Borel. If \(L\) is the selected law, return \(ALx\);
only the rows in its sampled support are needed, exactness holds for every
\(A\), and the output risk is the coefficient \(G\)-risk. This gives a
query-dependent decoder with worst-orbit risk at most
\(\Psi_s(G)+\varepsilon\). Letting \(\varepsilon\downarrow0\) proves

\[
\boxed{\quad
\inf_{(p_S(\cdot),F)}
\sup_{\|x\|=1}\sup_{A\in\mathcal O_G}
\sum_Sp_S(x)\|F_S(A_{:S},x)-Ax\|_2^2
=\Psi_s(G).
\quad}
\tag{20}
\]

Together with (3), the two exact orbit-oracle identities are static value
\(\nu_s(G)\) and query-dependent value \(\Psi_s(G)\) for the hard-cap
support class used above. The expected-read trace inequality (14)--(15) is
a separate static-schedule corollary; it does not define an expected-read
version of the query-dependent identity. The query-dependent upper
construction has a finite catalog, but its metadata, selector work,
random-bit cost, and page conversion remain outside this mathematical
identity.
