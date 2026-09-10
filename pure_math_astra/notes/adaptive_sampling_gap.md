# Fixed-law versus query-adaptive residual sampling

Status: supporting analysis only. The sharp real-field constant outside the
rank-one class is unresolved here; no novelty claim is made.

Let \(R\in\mathbb R^{p\times q}\), let \(G=R^TR\), and put
\(a_i=G_{ii}>0\). The fixed-law value is

\[
 \nu(R)=\min_{\pi\in\Delta_q}\lambda_{\max}
 \left(\operatorname{diag}(a_i/\pi_i)-G\right).
\]

If the sampling law may depend on the unit query \(x\), the optimal law is
proportional to \(\sqrt{a_i}|x_i|\). Its worst variance is

\[
 \mu(R)=\max_{\|x\|=1}
 \left[\left(\sum_i\sqrt{a_i}|x_i|\right)^2-x^TGx\right].
\tag{1}
\]

Hence \(\mu(R)\leq\nu(R)\): a fixed law is feasible in the query-dependent
problem, while a query-dependent law has more freedom.

## Sign formulation

For \(s\in\{\pm1\}^q\), write \(v_s=(s_i\sqrt{a_i})_i\). Then

\[
 \mu(R)=\max_{s\in\{\pm1\}^q}
 \lambda_{\max}(v_sv_s^T-G).
\tag{2}
\]

For the \(\leq\) direction, assign to each nonzero query \(x\) its coordinate
sign vector \(s\); the expression in (1) is then the Rayleigh quotient of
\(v_sv_s^T-G\). Conversely, let \(x\) be a top eigenvector for one such sign
matrix, and replace its sign vector by \(t_i=\operatorname{sign}(x_i)\).
Since \(|v_t^Tx|=\sum_i\sqrt{a_i}|x_i|\geq|v_s^Tx|\), the Rayleigh quotient
for the \(t\)-matrix is at least the original top eigenvalue. This proves (2).

## Exact rank-one evaluation over the real field

Suppose \(R=uw^T\) has rank one, and conjugate coordinates by signs so that
\(w_i=\sqrt{a_i}\geq0\). Let \(T=\sum_i a_i\). For a sign vector, let
\(S=\{i:s_i=1\}\) and \(A_S=\sum_{i\in S}a_i\). The only positive
eigenvalue of \(v_sv_s^T-ww^T\) is

\[
 2\sqrt{A_S(T-A_S)}.
\]

Therefore

\[
 \mu(R)=2\max_{S\subseteq[q]}\sqrt{A_S(T-A_S)}.
\tag{3}
\]

The fixed-law rank-one value is

\[
 \nu(R)=
 \begin{cases}
 T,&\max_i a_i\leq T/2,\\
 2\sqrt{A(T-A)},&A=\max_i a_i>T/2.
 \end{cases}
\tag{4}
\]

If \(A>T/2\), the subset containing the largest energy attains (4), so
\(\mu=\nu\). If \(A\leq T/2\), some subset has energy in
\([T/3,2T/3]\): add energies until the sum first reaches \(T/3\); if that
sum exceeds \(2T/3\), its final summand itself lies in \([T/3,T/2]\).
Equation (3) then gives

\[
 \mu(R)\geq\frac{2\sqrt2}{3}T,
 \qquad \frac{\nu(R)}{\mu(R)}\leq\frac3{2\sqrt2}.
\tag{5}
\]

Three equal energies attain equality. Thus the real rank-one adaptivity gap
is exactly \(3/(2\sqrt2)\).

Formula (3) also contains the weakly NP-hard PARTITION decision problem when
the rank-one instance is represented by its positive rational energy list:
\(\mu=T\) holds exactly when some subset has energy \(T/2\). This statement
depends on that representation. If an input format requires rational matrix
entries rather than a rational energy list or algebraic rank-one factor, a
separate encoding reduction is required.

## A general real-field bound

The fixed-law dual is

\[
 \nu(R)=\max_{X\succeq0,\ \operatorname{tr}X=1}
 \left[\left(\sum_i\sqrt{a_iX_{ii}}\right)^2-\operatorname{tr}(GX)\right].
\tag{6}
\]

Choose an optimizing \(X\) which, among matrices with its fixed diagonal,
minimizes \(m=\operatorname{tr}(GX)\). This choice is legitimate because the
first term in (6) depends only on the diagonal. Set

\[
 S=\sum_i\sqrt{a_iX_{ii}},\qquad d=\sum_i a_iX_{ii}.
\]

The diagonal matrix with the same diagonal as \(X\) is feasible in this
secondary minimization, so \(m\leq d\). Let \(y\sim N(0,X)\). For every
nonzero \(y\), homogeneity of (1) gives

\[
 \left(\sum_i\sqrt{a_i}|y_i|\right)^2-y^TGy
 \leq \mu(R)\|y\|^2.
\tag{7}
\]

For \(i\ne j\), the elementary bivariate-normal formula implies

\[
 \mathbb E|y_iy_j|\geq\frac2\pi\sqrt{X_{ii}X_{jj}}.
\]

Keeping the diagonal terms exactly yields

\[
 \mathbb E\left(\sum_i\sqrt{a_i}|y_i|\right)^2
 \geq d+\frac2\pi(S^2-d).
\]

Taking expectations in (7), using \(\mathbb E\|y\|^2=1\), gives

\[
 \begin{aligned}
 \mu(R)
 &\geq d+\frac2\pi(S^2-d)-m\\
 &=\frac2\pi(S^2-m)+\left(1-\frac2\pi\right)(d-m)\\
 &\geq\frac2\pi\nu(R).
 \end{aligned}
\tag{8}
\]

Consequently every real residual satisfies

\[
 1\leq\frac{\nu(R)}{\mu(R)}\leq\frac\pi2
\tag{9}
\]

when \(\mu(R)>0\). The rank-one example gives the lower obstruction
\(3/(2\sqrt2)\) for any smaller universal upper constant. Whether the
right-hand constant in (9) can be improved to \(3/(2\sqrt2)\), or to an
intermediate value, remains an open question in this investigation.

## Threshold formulation and its SDP gap

For \(t>0\), define

\[
 M_t=\operatorname{diag}(\sqrt a)\,(tI+G)^{-1}\operatorname{diag}(\sqrt a).
\tag{10}
\]

The fixed-law threshold has the equivalent forms

\[
 \nu(R)\leq t
 \quad\Longleftrightarrow\quad
 \min_{\substack{D\ \mathrm{diagonal}\\D\succeq M_t}}
 \operatorname{tr}D\leq1
 \quad\Longleftrightarrow\quad
 \max_{\substack{Z\succeq0\\Z_{ii}=1}}
 \operatorname{tr}(M_tZ)\leq1.
\tag{11}
\]

Indeed, \(\operatorname{diag}(a_i/\pi_i)\preceq tI+G\) is equivalent after
inversion and congruence to \(\operatorname{diag}(\pi)\succeq M_t\). A
diagonal majorant with trace below one may be increased diagonally to have
trace one. The final equivalence is semidefinite-program duality.

The adaptive threshold is

\[
 \mu(R)\leq t
 \quad\Longleftrightarrow\quad
 \max_{s\in\{\pm1\}^q}s^TM_ts\leq1.
\tag{12}
\]

This follows from (2) and the rank-one Schur complement condition
\(vv^T\preceq tI+G\Longleftrightarrow v^T(tI+G)^{-1}v\leq1\).

Thus, at each threshold, fixed sampling uses the correlation-matrix SDP and
adaptive sampling uses its sign-restricted counterpart. Since \(M_t\succeq0\),
Gaussian sign rounding gives the PSD Grothendieck comparison

\[
 \max_s s^TM_ts\geq\frac2\pi
 \max_{Z\succeq0,\ Z_{ii}=1}\operatorname{tr}(M_tZ).
\tag{13}
\]

Equation (13) does not by itself improve (9): changing \(t\) changes the
inverse matrix \(M_t\), so a pointwise SDP/sign ratio does not directly turn
into the same scalar ratio for \(\nu\) and \(\mu\). Its special inverse and
fixed-diagonal origin may still permit a stronger comparison; no proof is
recorded here.

## Complex rank-one contrast

For complex rank-one residuals, the gap disappears. In the balanced case,
take \(|x_i|=\sqrt{a_i/T}\). The lengths \(a_i/\sqrt T\) obey the polygon
inequality precisely when \(\max_i a_i\leq T/2\), so phases can make
\(w^*x=0\) and attain variance \(T\). In the dominant case, a two-block
query with the dominant coordinate and the normalized aggregate tail, each of
norm \(1/\sqrt2\), attains \(2\sqrt{A(T-A)}\). Comparing with (4) gives

\[
 \mu_{\mathbb C}(R)=\nu(R)\qquad\text{for rank-one }R.
\]

The real obstruction is discrete subset balance, not merely energy imbalance.
