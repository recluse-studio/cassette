# Spectral residual-access complexity — canonical source report

Research cutoff: 5 September 2026.

This report is the source authority for the paper in `pure_math_lab/paper/`. It records the
mathematical result, proof status, collision search, and exact novelty boundary. It does not amend
Cassette's production mathematics or implementation.

## Executive conclusion

### Verified facts

1. Cassette's present residual correction samples column $j$ with probability proportional to
   $\lVert r_j\rVert_2^2$ and certifies worst-query mean-square error by the Frobenius residual.
2. For the same fixed, query-independent, with-replacement estimator, the exact worst-query
   covariance is

   \[
   Q_\pi=\operatorname{diag}(a_j/\pi_j)-R^*R,
   \qquad a_j=\lVert r_j\rVert_2^2.
   \]

3. Its exact one-access minimax value is

   \[
   \nu(R)=\min_{\pi\in\Delta_q^\circ}\lambda_{\max}(Q_\pi),
   \]

   and $s$ fresh independent accesses divide this value by $s$.
4. The minimax value has the exact density-matrix dual

   \[
   \nu(R)=
   \max_{X\succeq0,\operatorname{tr}X=1}
   \left[
   \left(\sum_j\sqrt{a_jX_{jj}}\right)^2-\operatorname{tr}(XR^*R)
   \right].
   \]

5. The dual produces a finite primal-dual certificate that remains valid when the largest
   covariance eigenvalue has multiplicity greater than one.
6. Exact closed forms have been proved for two columns, pairwise orthogonal columns, and every
   rank-one residual.
7. The current squared-column-norm law is minimax if and only if the normalized energy vector is
   the diagonal of a density matrix supported on the minimum-eigenvalue eigenspace of $R^*R$.
8. On normalized two-column orthogonal residuals, the ratio between the current law's exact
   variance and the minimax variance is unbounded.
9. Two independent proof reconstructions found and corrected one zero-access boundary error, then
   accepted the corrected covariance, dual, certificate, and closed forms. Finite programs also
   checked the covariance identity, the two-column dual and primal, orthogonal water filling, and
   both branches of the rank-one theorem.

### Reasoned novelty inference

Inverse-probability estimation, E-optimal covariance design, extreme-eigenvalue density witnesses,
and Frobenius-optimal matrix-product sampling are established mathematics. The broad problem is not
new. Within the bounded three-wave primary-source search recorded below, no source was found that
states the following exact package for the declared estimator class:

- query-independent residual-column or physical-page access;
- exact worst-unit-query mean-square complexity;
- the reciprocal-weight density-matrix dual and repeated-eigenvalue witness;
- the two-column and orthogonal closed forms;
- the exact squared-energy-law criterion;
- the balanced/dominant rank-one phase transition;
- the unbounded separation from squared-energy sampling.

The defensible claim is therefore narrow: the recorded search found no earlier source combining
these results. A finite search cannot prove that no equivalent result exists under different
language.

## Problem and access model

Let $R:\mathbb F^q\to\mathbb F^p$ be nonzero, where $\mathbb F$ is $\mathbb R$ or $\mathbb C$.
Delete zero columns. Write its columns as $r_j$, put $G=R^*R$, and let
$a_j=G_{jj}>0$. A single access draws $J\sim\pi$, independently of the eventual query $x$, and
returns

\[
Z_\pi(x)=\frac{r_Jx_J}{\pi_J}.
\]

The law is fixed before the query. This is the decisive distinction from a law proportional to
$|x_j|\lVert r_j\rVert$, which is optimal for one known query but requires query-dependent
normalization and scheduling.

The estimator is unbiased. Direct expansion gives

\[
\mathbb E\lVert Z_\pi(x)-Rx\rVert_2^2=x^*Q_\pi x,
\qquad
Q_\pi=\operatorname{diag}(a_j/\pi_j)-G\succeq0.
\]

For the arithmetic mean of $s$ fresh independent copies, covariance scales exactly by $1/s$.
Therefore $\nu(R)/s$ is the necessary and sufficient worst-unit-query mean-square error inside
this declared estimator class. Sampling without replacement can do better after enough distinct
accesses and is a different problem.

## Principal results and proof routes

### Global dual and certificate

The variational identity

\[
\lambda_{\max}(H)=
\max_{X\succeq0,\operatorname{tr}X=1}\operatorname{tr}(XH)
\]

turns the primal into a convex-concave game. Restricting $\pi_j\ge\rho>0$ permits Sion minimax.
Coercivity keeps the primal optimizer in the open simplex. For fixed $X$, Cauchy--Schwarz gives

\[
\inf_{\pi\in\Delta_q^\circ}
\sum_j\frac{a_jX_{jj}}{\pi_j}
=\left(\sum_j\sqrt{a_jX_{jj}}\right)^2.
\]

The restricted dual functions converge uniformly on the compact density-matrix set by Dini's
theorem. This proves the exact dual.

A proposed optimum is globally certified by $(\pi,t,X)$ satisfying

\[
Q_\pi\preceq tI,
\quad X\succeq0,
\quad\operatorname{tr}X=1,
\quad X(tI-Q_\pi)=0,
\]

and

\[
\pi_j=
\frac{\sqrt{a_jX_{jj}}}{\sum_k\sqrt{a_kX_{kk}}}.
\]

Every primal optimum admits such a witness. At an attained interior minimum, the
$\lambda_{\max}$ subdifferential consists of density matrices supported on the top eigenspace;
the simplex KKT condition makes $a_jX_{jj}/\pi_j^2$ constant and positive. This proves existence
even when the largest eigenvalue is multiple.

The same dual is an exact semidefinite/second-order-cone problem: put
$A_j=a_je_je_j^*$, $B=G$,
$b_j=\operatorname{tr}(XA_j)$ and introduce $z_{jk}^2\le b_jb_k$ as rotated-cone constraints.
Maximizing $\sum_jb_j+2\sum_{j<k}z_{jk}-\operatorname{tr}(XB)$ recovers the dual without
relaxation.

### Two columns

For column energies $a,b$ and cross inner product $c$,

\[
\pi^*=\frac{(\sqrt a,\sqrt b)}{\sqrt a+\sqrt b},
\qquad
\nu(R)=\sqrt{ab}+|c|.
\]

Writing $t=\pi_1/(1-\pi_1)$ makes the covariance a $2\times2$ positive matrix with constant
determinant $ab-|c|^2$ and trace $a/t+bt$. The arithmetic-geometric mean inequality minimizes the
trace uniquely.

### Orthogonal columns

For pairwise orthogonal columns, $\nu(R)$ is the unique $u\ge0$ satisfying

\[
\sum_j\frac{a_j}{a_j+u}=1,
\]

and $\pi_j^*=a_j/(a_j+u)$. The equation equalizes every active diagonal covariance. It is a
reciprocal water-filling law, not squared-energy sampling.

### Exact criterion for the existing law

Let $T=\operatorname{tr}G$ and $\pi_j^{\rm F}=a_j/T$. Then

\[
Q_{\pi^{\rm F}}=TI-G.
\]

Squared-energy sampling is minimax if and only if there is a density matrix $X$ with

\[
\operatorname{ran}X\subseteq E_{\min}(G),
\qquad
\operatorname{diag}X=(a_1/T,\ldots,a_q/T).
\]

Necessity and sufficiency follow from the convex KKT condition at $\pi^{\rm F}$. This theorem is
material to Cassette because it decides, from the residual Gram geometry, whether the current law
is already exact or is strictly improvable.

### Complete rank-one phase transition

Suppose $\operatorname{rank}R=1$, let $T=\sum_ja_j$, $a=\max_ja_j$, and $b=T-a$. For at least
two nonzero columns,

\[
\nu(R)=
\begin{cases}
T,&a\le T/2,\\
2\sqrt{ab},&a>T/2.
\end{cases}
\]

In the balanced regime, squared-energy sampling is uniquely minimax. In the dominant regime, for
the unique dominant index $h$,

\[
\pi_h^*=\frac{\sqrt a}{\sqrt a+\sqrt b},
\qquad
\pi_j^*=\frac{a_j}{\sqrt b(\sqrt a+\sqrt b)}\quad(j\ne h).
\]

The proof factors the dual density matrix into Gram vectors. The balanced threshold is precisely
the polygon-closure condition for lengths $a_j/\sqrt T$. In the dominant case, a two-block
compression and Cauchy--Schwarz reduce the problem to the dominant column against its aggregated
tail.

### Page components

For a physically fixed decomposition $R=\sum_gR_g$, one categorical page access returns
$R_Jx/\pi_J$. The exact covariance and dual are

\[
Q_\pi=\sum_g\frac{R_g^*R_g}{\pi_g}-R^*R,
\]

\[
\nu(R_1,\ldots,R_m)=
\max_{X\succeq0,\operatorname{tr}X=1}
\left[
\left(\sum_g\sqrt{\operatorname{tr}(XR_g^*R_g)}\right)^2
-\operatorname{tr}(XR^*R)
\right].
\]

The invariant is zero exactly when $R_g=\pi_gR$ for every $g$ under some probability vector.
The physical decomposition must be fixed first; arbitrary proportional splitting would game the
invariant.

Allowing a different independent categorical law at each access cannot improve the ordinary
arithmetic mean. If $\bar\pi$ is the average of those laws, coordinatewise convexity of
$u\mapsto1/u$ gives the Loewner inequality between their average covariance and $Q_{\bar\pi}$.
This is an estimator-class boundary result, not part of the novelty claim.

## Material consequence for Cassette

For two orthogonal residual columns with $a\ge b>0$, the existing squared-energy law has exact
worst-query variance $a$. The minimax value is $\sqrt{ab}$. Their ratio is $\sqrt{a/b}$ and tends
to infinity while $a+b=1$. The result is therefore not a smaller constant in the old bound.

It changes the mathematical description objective. At fixed resident description and metadata
budgets, define

\[
D_A^{\rm mm}(b_{\rm desc},b_{\rm meta})
=\inf_{B\in\mathcal C_{b_{\rm desc},b_{\rm meta}}(A)}\nu(A-B).
\]

A Frobenius-optimal reconstruction need not minimize this invariant. If adopted later, a Cassette
plan could use a primal-dual witness to certify an exact worst-query mean-square sample count,
rather than only the present sufficient Frobenius count. This report does not authorize that
production change.

## Primary-source collision matrix

| Candidate element | Closest primary source | Exact comparison | Verdict |
|---|---|---|---|
| Unequal-probability with-replacement estimator | [Hansen and Hurwitz (1943)](https://doi.org/10.1214/aoms/1177731356) | Establishes inverse-probability estimation from finite populations. | Prior art. |
| E-optimal covariance sampling | [Imberg, Axelson-Fisk, and Jonasson (2023), equations (8)–(9), Table 1](https://arxiv.org/abs/2304.03019) | Multinomial inverse-probability covariance and minimization of its largest eigenvalue. | Strong broad collision. |
| Square-root stationary law at a simple top eigenvalue | [Imberg et al. (2023), Lemma 2(c), Proposition 1, equation (13)](https://arxiv.org/abs/2304.03019) | Uses one leading eigenvector and gives stationary square-root weights. | Prior art for the differentiable case. |
| Convex global reciprocal E-optimal problem | [Imberg et al. (2023), Sections 3 and 7](https://arxiv.org/abs/2304.03019) | In the reviewed sections, no global solution of this reciprocal-weight objective was found; here Loewner convexity makes the fixed reciprocal objective convex. | No exact collision found in the recorded search. |
| Extreme-eigenvalue density witness | [Kiefer (1974)](https://doi.org/10.1214/aos/1176342810); [Harman and Rosa (2018), Section 2](https://arxiv.org/abs/1808.00731) | General E-optimal equivalence theory uses trace-one PSD mixtures on the extremal eigenspace. | General witness pattern is prior art. |
| Reciprocal density-matrix dual | Same E-optimal sources | Their design information is affine in weights; they do not minimize reciprocal weights inside the eigenvalue and then close the dual. | No exact collision found. |
| Categorical sampled matrix products | [Drineas, Kannan, and Mahoney (2006), Section 4.1 and Lemmas 3–4](https://doi.org/10.1137/S0097539704442684) | Same estimator ancestry; optimizes expected Frobenius error with a norm-product law. | Estimator prior art; objective distinct. |
| Expected-variance importance law | [Eriksson-Bique et al. (2011), Sections 2–4](https://doi.org/10.1137/10080659X) | Optimizes expectation under a distribution and gives a query-dependent retrieval law. | Distinct from one fixed worst-query law. |
| Spectral Gram approximation | [Holodnak and Ipsen (2015), Sections 3–5](https://doi.org/10.1137/130940116) | Gives probabilistic two-norm bounds for sampled outer products approximating a Gram matrix. | Different random object and bound. |
| Entrywise spectral sparsification | [Achlioptas and McSherry (2007)](https://doi.org/10.1145/1219092.1219097) | Samples or quantizes entries and bounds matrix approximation. | Different estimator and loss. |
| Optimal randomized Hilbert-space operators | [Novak (1992)](https://doi.org/10.1016/0885-064X(92)90032-7) | Optimizes random projections and stochastic widths, including water-filling-like inclusion probabilities. | Different information class and without-replacement geometry. |
| Specialized exact E-allocation | [Ravichandran et al. (2024), Theorem 1](https://doi.org/10.1515/jci-2023-0046) | Solves a diagonal factorial-design covariance and obtains variance-proportional allocation. | Specialized near precedent, not the Gram-coherent problem. |
| Prescribed diagonal/eigenspace geometry | [Horn (1954)](https://doi.org/10.2307/2372705) | Classical diagonal-versus-spectrum feasibility. | Ingredient prior art. |
| Balanced prescribed-norm geometry | [Casazza et al. (2006), Proposition 1 and the fundamental inequality](https://doi.org/10.1007/0-8176-4504-7_4) | The largest squared norm cannot exceed the appropriate share of total frame energy. | Polygon/frame ingredient; no minimax law. |
| Minimax interchange | [Sion (1958)](https://doi.org/10.2140/pjm.1958.8.171) | Supplies the compact convex-concave minimax theorem. | Proof tool, not collision. |

## Focused second-wave findings

The first wave searched randomized matrix multiplication, coordinate sampling, matrix
sparsification, and query matching. It established that the estimator is old and the familiar
norm-product or squared-energy laws optimize trace/Frobenius or query-specific losses.

The second wave searched unequal-probability subsampling, Hansen--Hurwitz and
Horvitz--Thompson design, E-optimality, experimental-design equivalence theorems, matrix
fractional minimax problems, elliptope diagonals, prescribed-norm frames, and randomized operator
approximation. It found the strong Imberg et al. broad collision and the Kiefer/Harman--Rosa
density-witness precedent. The recorded search found no exact source for the reciprocal dual, the
closed forms, or the energy-law criterion.

The final narrow wave searched exact formula fragments and the balanced/dominant rank-one split.
It found classical polygon and frame geometry but no paper connecting that threshold to the
reciprocal spectral sampling value or law.

Searches reached diminishing returns when new queries returned the same E-optimal design,
matrix-product sampling, frame, and survey-sampling sources without a closer equation-level
collision. The unresolved gap is terminology: an equivalent reciprocal spectral allocation result
may exist in paywalled or differently indexed literature.

## Claim-source ledger

| Paper claim | Status | Evidence |
|---|---|---|
| The estimator is unbiased and has covariance $Q_\pi$. | Proved here; ancestry known. | Direct finite expansion; Hansen--Hurwitz; Drineas et al. |
| Worst-unit-query MSE is $\lambda_{\max}(Q_\pi)$. | Proved here. | Rayleigh--Ritz. |
| The primal is convex and attains an interior minimum. | Proved here. | Loewner convexity and coercivity. |
| The density-matrix dual is exact. | Proved here. | Rayleigh--Ritz, Sion, Cauchy--Schwarz, Dini. |
| The witness is necessary and sufficient. | Proved here. | Saddle-point equality and complementary support. |
| Two-column formula. | Proved here; independently reconstructed. | Constant determinant and minimum trace. |
| Orthogonal water filling. | Proved here; independently reconstructed. | Diagonal epigraph feasibility. |
| Squared-energy iff criterion. | Proved here; independently reconstructed. | Convex KKT at $TI-G$. |
| Rank-one phase transition. | Proved here; independently reconstructed. | Polygon closure and two-block compression. |
| Unbounded normalized separation. | Proved here and numerically illustrated. | Two orthogonal columns with $a/b\to\infty$. |
| Time-varying independent laws cannot improve the ordinary mean. | Proved here as a boundary result; no novelty claim. | Coordinatewise Jensen inequality and Loewner order. |
| No source in the recorded search states the listed conjunction for the declared estimator class. | Verified only within recorded search. | Collision matrix and three search waves. |
| The exact package is globally novel. | Not verifiable by finite search. | Paper must use “to our knowledge” and state the search boundary. |

## Falsification record

The standard-library program `pure_math_lab/minimax_residual_sampling.py` performs four independent
finite checks:

1. direct enumeration of estimator outcomes against the covariance quadratic form;
2. grid search of the two-column primal and density-matrix dual against the closed form;
3. simplex search against orthogonal water filling; and
4. simplex search against the balanced and dominant rank-one formulas.

The program is a counterexample search, not a proof. The written proofs and independent
reconstructions are the mathematical evidence.

One early statement set the access count to zero whenever $\nu(R)=0$. A one-column nonzero
residual disproved it: one access is exact, but zero accesses do not evaluate the residual. The
correct rule is zero accesses only for $R=0$; otherwise the declared estimator needs at least one.

## Paper claim boundary

The paper may claim:

> We give an exact analysis of the declared fixed, query-independent, categorical with-replacement
> estimator. Within the recorded search, we found no earlier source combining the reciprocal
> density-matrix dual, a certificate valid at repeated top eigenvalues, the stated closed forms,
> and the squared-energy optimality criterion.

The paper may not claim:

- invention of inverse-probability sampling;
- invention of E-optimal covariance design;
- invention of density witnesses for extremal eigenvalues;
- global optimality among sampling without replacement, adaptive laws, query-dependent laws, or
  arbitrary randomized linear algorithms; or
- proof that no equivalent theorem exists anywhere in the literature.
