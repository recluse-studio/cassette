# Prior-work challenge: fixed versus query-adaptive sampling

Status: bounded source check for
[`adaptive_sampling_gap.md`](../notes/adaptive_sampling_gap.md). This note
records overlap and limits; it makes no originality claim.

Let \(G=R^TR\), \(a=\operatorname{diag}G\), and

\[
 M_t=D_{\sqrt a}(tI+G)^{-1}D_{\sqrt a}.
\]

The local note proves the threshold identities

\[
 \nu(R)\leq t\iff \operatorname{DiagMaj}(M_t):=
 \min_{D\ \mathrm{diagonal},\ D\succeq M_t}\operatorname{tr}D\leq1,
\]

\[
 \mu(R)\leq t\iff \operatorname{Sign}(M_t):=
 \max_{s\in\{\pm1\}^q}s^TM_ts\leq1.
\]

The dual of \(\operatorname{DiagMaj}\) is
\(\max\{\operatorname{tr}(M_tZ):Z\succeq0,\ Z_{ii}=1\}\).

## Sources read and the exact overlap

1. Joel A. Tropp, [*Column Subset Selection, Matrix Factorization, and
   Eigenvalue Optimization* (2009), Theorem 2.2 and Theorem
   3.1](https://tropp.caltech.edu/reports/Tro08-Column-Subset-TR.pdf).
   This primary report states a finite-dimensional Pietsch factorization:
   for a real matrix \(B\), there are a nonnegative diagonal \(D\) with
   \(\operatorname{tr}D^2=1\) and \(B=TD\), where
   \(\lVert T\rVert\leq\sqrt{\pi/2}\lVert B\rVert_{\infty\to2}\).
   It also gives the equivalent matrix condition
   \(B^TB\preceq\alpha^2D^2\).

   Put \(B_t=(tI+G)^{-1/2}D_{\sqrt a}\), so that
   \(B_t^TB_t=M_t\). Minimizing \(\alpha^2\) in Tropp's matrix condition
   is exactly \(\operatorname{DiagMaj}(M_t)\): write
   \(H=\alpha^2D^2\), then \(H\) is diagonal, \(H\succeq M_t\), and
   \(\operatorname{tr}H=\alpha^2\), and conversely normalize any such
   \(H\). Also
   \(\lVert B_t\rVert_{\infty\to2}^2=\operatorname{Sign}(M_t)\).
   Therefore the pointwise inequality

   \[
   \operatorname{DiagMaj}(M)\leq(\pi/2)\operatorname{Sign}(M)
   \tag{P}
   \]

   for positive-semidefinite \(M\) is a direct Pietsch consequence. The
   diagonal-majorizer threshold is consequently a standard factorization
   object, not a new SDP relaxation.

2. Jop Briët, Fernando M. de Oliveira Filho, and Frank Vallentin,
   [*A sub-constant improvement in approximating the positive
   semidefinite Grothendieck problem* (2010), Sections 1--2 and
   Theorem 1.1](https://optimization-online.org/wp-content/uploads/2009/10/2443.pdf).
   This primary paper defines the sign problem and its correlation-matrix
   SDP for a PSD matrix. It records and proves the real \(2/\pi\) rounding
   bound, equivalently (P), and says that \(2/\pi\) is sharp for unrestricted
   PSD matrices as dimension grows. Its finite-rank refinements concern the
   rank of the SDP vectors or the matrix, not the inverse family \(M_t\).

3. Yu. Nesterov, [*Semidefinite relaxation and nonconvex quadratic
   optimization* (1998)](https://doi.org/10.1080/10556789808805690).
   The publisher record identifies the diagonal-quadratic SDP relaxation and
   its \(\pi/2\)-factor accuracy. The full proof was not accessible in this
   bounded check. The stated PSD comparison used above was checked directly
   in the Briët--de Oliveira Filho--Vallentin primary paper rather than
   inferred from the publisher abstract.

4. Jack Kiefer and Jacob Wolfowitz, [*The Equivalence of Two Extremum
   Problems* (1960)](https://doi.org/10.4153/CJM-1960-030-4), and
   [*Optimum Designs in Regression Problems* (1959)](https://doi.org/10.1214/AOMS/1177706252).
   These are the primary optimal-design references located for the
   E-/c-optimal-design terminology. Their stated subject is an information
   matrix formed by a probability design measure and prediction/contrast
   criteria. That differs from the present covariance
   \(\operatorname{diag}(a_i/\pi_i)-G\), whose negative Gram term is part
   of the same coordinate-sampling estimator. I did not obtain the full
   articles in this bounded check, so this entry supplies terminology and
   scope only, not a theorem comparison.

## Consequences for the local results

The inversion and SDP duality in the threshold display are elementary, but
their identification with Pietsch factorization and the generic \(\pi/2\)
constant are classical. The Gaussian proof of
\(\mu(R)\geq(2/\pi)\nu(R)\) in the local note is an application of the
same real PSD rounding constant. The sources read do not state that precise
fixed-law-versus-query-adaptive variance theorem; that observation alone does
not establish novelty.

The sharp unrestricted PSD Grothendieck examples do not settle the Cassette
ratio. Here \(M_t\) is constrained by

\[
 M_t^{-1}=D_{1/\sqrt a}(tI+G)D_{1/\sqrt a},\qquad
 G\succeq0,\quad \operatorname{diag}G=a,
\]

and the threshold matrix changes with \(t\). Thus a sharp pointwise
SDP/sign gap does not automatically produce a residual with
\(\nu(R)/\mu(R)=\pi/2\). Conversely, no source in this bounded search gave
a sharper comparison for this inverse, prescribed-diagonal family or a
theorem fixing the global adaptivity gap. That is a search limit, not an
absence-of-literature conclusion.

The rank-one real constant \(3/(2\sqrt2)\) in the local note arises from a
subset-balance argument. None of the sources read identifies it as the sharp
constant for the constrained family. The current mathematical question
remains whether that rank-one constant controls all real residuals, or
whether a higher-rank inverse family produces a larger gap below \(\pi/2\).
