# Inverse-hull bridge: reconstruction and optimal-design comparison

Status: the two reductions and the paired-block construction are proved.
The c-optimal-design identification makes the inner inverse-hull reduction
standard optimal-design geometry.  It does not settle the query-adaptive
minimax or the physical access model.

Let \(G\succ0\), let \(E_S:\mathbb R^{|S|}\to\mathbb R^q\) be coordinate
embedding, and, for \(|S|=s\), define

\[
 K_S=E_SG_{SS}^{-1}E_S^T,qquad M(\alpha)=\sum_S\alpha_SK_S.
\tag{1}
\]

## 1. The query-adaptive inner problem

For one query \(x\), condition an arbitrary legal estimator on its support.
Strict convexity of the positive quadratic form makes its conditional mean
non-worse.  If that mean is \(E_Sm_S\) with probability \(\alpha_S\), then

\[
 \sum_S\alpha_SE_Sm_S=x,qquad
 \mathbb E[Y^TGY]=\sum_S\alpha_Sm_S^TG_{SS}m_S.
\tag{2}
\]

For a fixed \(\alpha\), the Lagrange equations give

\[
 m_S=G_{SS}^{-1}E_S^T\lambda,qquad M(\alpha)\lambda=x.
\tag{3}
\]

Thus the minimum is \(x^TM(\alpha)^\dagger x\) when
\(x\in\operatorname{range}M(\alpha)\), and is infinite otherwise.  Taking
the infimum over \(\alpha\), then subtracting the mean energy, proves

\[
 \phi_G(x)=\inf_\alpha x^TM(\alpha)^\dagger x-x^TGx.
\tag{4}
\]

The use of exactly \(s\) supports loses nothing: a vector with smaller
support may be assigned to any size-\(s\) superset with zero added
coordinates.  A full-support mixture gives \(M\succ0\), so (4) may also be
written as an infimum over positive-definite mixtures for every nonzero
query.

## 2. A common linear support law

Fix \(\alpha\) with \(M\succ0\).  Consider common laws that choose \(S\)
with probability \(\alpha_S\), return \(Y=L_Sx\), have rows outside \(S\)
equal to zero, and obey \(\sum_S\alpha_SL_S=I\).  The choice

\[
 L_S=K_SM^{-1}
\tag{5}
\]

is unbiased.  It is the unique minimum in positive-semidefinite covariance
order.  Indeed, if \(D_S=L_S-K_SM^{-1}\), then \(D_S\) has rows in \(S\),
\(\sum_S\alpha_SD_S=0\), and

\[
 K_SGD_S=D_S,qquad K_SGK_S=K_S.
\tag{6}

\]

Expanding the second moment makes both cross terms vanish and gives

\[
 \sum_S\alpha_SL_S^TGL_S
 =M^{-1}+\sum_S\alpha_SD_S^TGD_S\succeq M^{-1}.
\tag{7}
\]

At (5), the covariance quadratic form is \(x^T(M^{-1}-G)x\).  Hence the
common-law worst-query optimum is

\[
 \nu=\inf_{\alpha:\,M(\alpha)\succ0}
       \lambda_{\max}(M(\alpha)^{-1}-G).
\tag{8}
\]

The class in (8) is broader than diagonal HT sampling because a retained
coordinate coefficient may depend on all coordinates of \(x\).  It is a
common-law restriction of (4), because \(\alpha\) and the maps cannot then
depend on the query.  It remains a coordinate-support-\(s\) source read if
the full query vector is available to form those coefficients.

## 3. Trace certificate

For every support,

\[
 \operatorname{tr}(GK_S)=s,qquad\operatorname{tr}(GM(\alpha))=s.
\tag{9}
\]

Let \(t\) be the unique positive solution of

\[
 \operatorname{tr}\bigl(G(G+tI)^{-1}\bigr)=s.
\tag{10}
\]

If the value in (8) is at most \(v\), then
\(M^{-1}\preceq G+vI\), hence \(M\succeq(G+vI)^{-1}\).  Taking the
positive \(G\)-trace yields

\(s\ge\operatorname{tr}(G(G+vI)^{-1})\), so \(v\ge t\).  Equality at
\(v=t\) holds precisely when

\[
 (G+tI)^{-1}\in\operatorname{conv}\{K_S:|S|=s\}.
\tag{11}
\]

For necessity, equality of the two \(G\)-traces after the Loewner inequality
forces \(M=(G+tI)^{-1}\), since \(G\succ0\).  Sufficiency is immediate.

## 4. Two arbitrary paired blocks

Let \(q=4,s=2\), \(r=\sqrt\eta\), and

\[
 G=\operatorname{Diag}(H_1,H_2),
\tag{12}
\]

where each real symmetric block has eigenvalues \(1,r^2\).  Give each
within-block support probability \(r/(1+r)^2\).  For coordinate \(j\) in
either block, prescribe its total probability of appearing in a cross-block
support to be

\[
 \frac{G_{jj}}{(1+r)^2}.
\tag{13}
\]

The two block totals agree, because both traces equal \(1+r^2\).  A
nonnegative \(2\times2\) transport table therefore realizes the four cross
support weights.  Their total probability is \((1+r^2)/(1+r)^2\), and the
two whole-block weights add \(2r/(1+r)^2\), so all weights sum to one.

For a block \(H\), Cayley--Hamilton gives

\[
 H^{-1}=\frac{(1+r^2)I-H}{r^2},\qquad
 (H+rI)^{-1}=\frac{(1+r+r^2)I-H}{r(1+r)^2}.
\tag{14}
\]

The within-block contribution to \(M\) is
\(((1+r^2)I-H)/(r(1+r)^2)\).  Each cross support contributes only a diagonal
principal inverse.  Equation (13) therefore adds \(I/(1+r)^2\) in each
block, making

\[
 M=(G+rI)^{-1}.
\tag{15}
\]

The trace certificate proves \(\nu=r\), for every pair of block rotation
angles.  By the real polar classification in
`query_adaptive_q4_unequal_paired_polar.md`, the query-dependent
value satisfies \(\Psi_2(G)<r\) exactly when the two normalized block
correlation magnitudes differ.  Thus a common linear support law reaches
the water level while query-dependent support laws can strictly improve it;
the latter is not explained by failure of the common-law inverse hull.

## 5. Primary-source comparison

Equation (4) is a finite *multiresponse c-optimal design* problem.  Set
\(A_S=G_{SS}^{-1/2}E_S^T\); then \(A_S^TA_S=K_S\), and the information
matrix of an approximate design is exactly \(\sum_S\alpha_SK_S\).  The
criterion \(x^TM(\alpha)^{-1}x\) is the classical c-criterion.

* G. Elfving, [*Optimum Allocation in Linear Regression Theory*](https://doi.org/10.1214/AOMS/1177729442), *Annals of Mathematical Statistics* 23(2), 255--262 (1952), gives the original geometric c-optimal allocation result for scalar-response regressors.
* G. Sagnol, [*Computing Optimal Designs of Multiresponse Experiments Reduces to Second-Order Cone Programming*](https://arxiv.org/abs/0912.5467), *Journal of Statistical Planning and Inference* 141, 1684--1708 (2011), Theorems 3.1 and 3.3, extends the Elfving geometry to finite multiresponse experiments and gives the corresponding SOCP.  Its setup permits matrix-valued experiment information, exactly the level needed for \(K_S\).
* H. Dette and T. Holland-Letz, [*A Geometric Characterization of c-Optimal Designs for Heteroscedastic Regression*](https://arxiv.org/abs/0911.3801), *Annals of Statistics* 37(6B), 4088--4103 (2009), independently supplies an ellipsoidal/matrix-information generalization.
* J. Kiefer, [*Optimum Experimental Designs*](https://doi.org/10.1111/j.2517-6161.1959.tb00338.x), *JRSS B* 21, 272--319 (1959), is a primary source for the approximate-design criteria family that includes the ordinary E criterion.

These sources make the inverse-hull/c-optimal inner reduction standard after
the identification of the experiment matrices \(A_S\).  They do not supply
the source-specific principal-inverse dictionary, the trace identity (9), or
the paired-block mixture (13)--(15).  More importantly, (8) is not ordinary
E-optimality: E-optimality maximizes \(\lambda_{\min}(M)\), equivalently
minimizes \(\lambda_{\max}(M^{-1})\), whereas (8) minimizes
\(\lambda_{\max}(M^{-1}-G)\).  It is an offset variance criterion.  General
convex approximate-design machinery can formulate it, but the cited
classical E results do not by themselves prove the equality certificate or
the strict adaptive separation.

## Scope

The c-optimal-design identification lowers the novelty of the atomic
inverse-hull step.  The mathematical question retained here is the gap
between a single matrix-valued design in (8) and the query-selected designs
in (4), under the fixed coordinate-support dictionary.  Neither result is a
byte, finite-precision, or page-traffic theorem.
