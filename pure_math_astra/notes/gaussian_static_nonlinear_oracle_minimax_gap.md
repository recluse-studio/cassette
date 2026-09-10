# gaussian_static_nonlinear_oracle_minimax_gap.md — normalized minimax separation for universal static nonlinear column decoders; depends on gaussian_static_oracle_first_chaos_reduction.md, query_adaptive_finite_catalog_bridge.md, query_adaptive_equicorrelation_boundary_rank_bound.md.

# A minimax gap that allows nonlinear static decoders

The later [fixed-Gram orbit theorem](fixed_gram_oracle_adaptivity_separation.md)
gives exact static and query-dependent oracle identities on A^T A=G. Its
growing read-gap consequence permits p=q and removes this note's Gaussian
normalization loss. This note preserves the earlier method and its separate
all-source normalized formulation.

This theorem concerns universal column-oracle algorithms. Their static
access distribution is chosen before the source and query, but their output
may be any measurable function of the fetched column contents and the query.
No source-dependent resident information is supplied.

The conclusion is a minimax separation: for each static decoder there is
a source and query on which its normalized risk exceeds the target.
It does not select one fixed source defeating every possible decoder.
It is also not a finite-word source or arbitrary encoded-page theorem.

## The source normalization and oracle class

Fix \(G\succ0\) in \(\mathbb R^{q\times q}\) and \(p\ge q\). Sources range
over all real \(p\times q\) matrices \(A\). Define

\[
\Gamma_G(A)=\|AG^{-1/2}\|_{\rm op}^2.
\tag{1}
\]

This is a performance normalization. The decoder receives neither
\(\Gamma_G(A)\) nor any other source-dependent side information.
The matrix \(G\) and dimensions are fixed common parameters.

A static decoder chooses a distribution \(p_S\) on subsets of at most
\(s\) original columns, independently of \(A\) and \(x\). After receiving
\(A_{:S}\), it returns an arbitrary Borel function \(F_S(A_{:S},x)\).
Additional random output choices can be replaced by their conditional mean
given \(S,A_{:S},x\), which preserves the mean and lowers squared error.
Require exact unbiasedness for every real source and query:

\[
\sum_Sp_SF_S(A_{:S},x)=Ax.
\tag{2}
\]

Its uniform normalized risk is

\[
\mathcal R_G(F)=
\sup_{A\ne0}\ \sup_{\|x\|=1}
\frac{\sum_Sp_S\|F_S(A_{:S},x)-Ax\|^2}{\Gamma_G(A)}.
\tag{3}
\]

The decoder may mix output rows, use nonlinear functions of fetched
entries, and use nonlinear functions of \(x\). We impose no requirement
that its pointwise output lie in the span of the fetched columns.

## From Gaussian average risk to normalized minimax risk

Let \(U\) have independent \(N(0,1/p)\) entries and put
\(A=UG^{1/2}\). Then \(\Gamma_G(A)=\|U\|_{\rm op}^2\). Define

\[
\kappa_{p,q}=
\left(1+\sqrt{\frac qp}\right)^2+\frac4p.
\tag{4}
\]

For this Gaussian matrix,

\[
\mathbb E\Gamma_G(A)\le\kappa_{p,q}.
\tag{5}
\]

The mean norm bound is Gordon's inequality
\(\mathbb E\|U\|_{\rm op}\le1+\sqrt{q/p}\).
The norm is \(1/\sqrt p\)-Lipschitz as a function of the standard Gaussian
entries. Applying Gaussian concentration to it and its negative, then
integrating \(2t\,\Pr(|\|U\|-\mathbb E\|U\||>t)\), gives variance at
most \(4/p\). This proves (5).
These are established facts: see Roman Vershynin,
[*Introduction to the non-asymptotic analysis of random matrices*](https://arxiv.org/pdf/1011.3027),
Theorem 5.32, its Slepian proof, and Proposition 5.34, printed pages 20–21.
The expectation-to-second-moment calculation above uses those stated
bounds directly.

If \(\mathcal R_G(F)\) is infinite, any finite lower bound is immediate.
Otherwise (3) and (5) give, for every fixed unit \(x\),

\[
\mathbb E_{A,S}\|F_S(A_{:S},x)-Ax\|^2
\le\mathcal R_G(F)\,\kappa_{p,q}.
\tag{6}
\]

Finite risk in (3) also gives the Gaussian second moments required in the
first-chaos reduction. For the schedule \(p_S\), put

\[
M=\sum_Sp_SE_SG_{SS}^{-1}E_S^T.
\tag{7}
\]

Exactness for all queries implies \(M\succ0\). The independently
reconstructable first-chaos argument gives

\[
\mathbb E_{A,S}\|F_S(A_{:S},x)-Ax\|^2
\ge x^T(M^{-1}-G)x.
\tag{8}
\]

Choose a unit eigenvector of \(M^{-1}-G\) with largest eigenvalue.
No interchange of an expectation and a query-dependent supremum is needed.
Equations (6)–(8) imply

\[
\boxed{\quad
\mathcal R_G(F)\ge
\frac{\lambda_{\max}(M^{-1}-G)}{\kappa_{p,q}}
\ge\frac{\nu_s(G)}{\kappa_{p,q}}
\ge\frac{t_s(G)}{\kappa_{p,q}}.
\quad}
\tag{9}
\]

Here \(t_s(G)\) solves
\(\operatorname{tr}[G(G+tI)^{-1}]=s\) when \(0<s<q\).
All inequalities concern the same source-independent schedule class.
In particular, (9) does not infer a near-isometric hard source from an
unconditional expectation.

## A growing separation

Take \(q=4m\) and

\[
G=H_\eta^{\oplus m},\qquad H_\eta=\mathbf1\mathbf1^T+\eta I_4.
\tag{10}
\]

Choose a fixed sufficiently small \(\eta>0\), with \(\eta\le1/100\),
for which the proved adaptive bound and finite-catalog bridge give a
two-column block law with risk at most \(19\eta/10\).
The real version follows as well: for real queries and a real Gram,
taking the real part of a complex output preserves its exact mean,
does not enlarge its support, and does not increase its error.

Use the shared block catalog on each of the \(m\) query blocks.
It produces \(\mathbb E Y=x\), at most \(2m\) nonzero coefficients,
and

\[
\mathbb E(Y-x)^TG(Y-x)\le\frac{19}{10}\eta\|x\|^2.
\tag{11}
\]

For every real source \(A\), the matrix inequality

\[
A^TA\preceq\Gamma_G(A)G
\]

therefore gives

\[
\mathbb E\|A(Y-x)\|^2
\le\frac{19}{10}\eta\,\Gamma_G(A)\|x\|^2.
\tag{12}
\]

This is one universal upper construction. Its catalog selection depends
on the query, and it fetches at most \(2m\) original columns.

Now take \(p=65536q\). Since \(q\ge4\), (4) gives

\[
\kappa_{p,q}
\le1+\frac1{128}+\frac1{32768}
=\frac{33025}{32768}<\frac{101}{100}.
\tag{13}
\]

Suppose a static decoder of the stated class meets
\(\mathcal R_G(F)\le19\eta/10\). Equations (6)–(8) imply

\[
M^{-1}-G\preceq \frac{1919}{1000}\eta I.
\]

Since
\(\operatorname{tr}(GM)=\sum_Sp_S|S|\le s\), inversion and trace yield

\[
\begin{aligned}
\frac{s}{m}
&\ge
\frac{4+\eta}{4+\eta+(1919/1000)\eta}
 +\frac{3}{1+1919/1000}\\
&\ge
\frac{401000}{402919}+\frac{3000}{2919}\\
&=\frac{793092000}{392040187}
>\frac{101}{50}.
\end{aligned}
\tag{14}
\]

The second line uses \(\eta\le1/100\); the first fraction decreases
with \(\eta\). The final strict difference is exactly
\(58541113/19602009350>0\).
Thus every such static decoder needs more than
\((2+1/50)m\) columns to match (12) uniformly, while the query-selected
construction uses \(2m\).

The static lower bound needs only an expected read budget. If its schedule
may occasionally choose any subset of the \(q\) columns, put
\(\bar s=\sum_Sp_S|S|\). The same proof has
\(\operatorname{tr}(GM)=\bar s\), and (14) holds with \(\bar s\) in
place of \(s\). Thus a uniform matching static decoder needs more than
\((2+1/50)m\) expected columns, even though the upper construction never
uses more than \(2m\).

## What this result adds and what remains open

The lower bound permits nonlinear computation on fetched source contents
and outputs outside their span. That removes a decoder restriction from
the earlier column-linear comparison. Its quantifiers differ, however:
the schedule here is source-independent and the hard source may depend on
the decoder. The earlier finite-word theorem permits a source-trained
static schedule and chooses one source against a fixed finite resident
interpreter range. Neither theorem subsumes the other.

All-source exact unbiasedness is essential in the first-chaos reduction.
An average-unbiased decoder can use Gaussian conditional prediction
instead, and need not satisfy (8).
Source-dependent resident encodings, content-adaptive column selection,
finite-word source quantization, and a physical page conversion require
additional arguments. The value in (1) is not free source information
available to an execution.

The proof uses established Gaussian projection and concentration tools.
The originality and sufficient Cassette significance of the assembled
separation remain unassessed. A restricted oracle theorem can be relevant
under an explicit application contract; no universal Cassette frontier
is being made a prerequisite or claimed here.
