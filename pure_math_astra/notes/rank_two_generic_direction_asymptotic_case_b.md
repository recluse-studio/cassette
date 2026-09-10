# Asymptotic unit witness for the generic rank-two Case B direction

Status: proved for the Case B zero-sum sign chart below.  This is an
asymptotic existence result for each fixed direction.  It supplies no
uniform threshold over directions and does not cover the other generic sign
charts.

For a real matrix \(L\), the finite polar constraints considered here are

\[
 (n_J+L_{E,J}^Tu_E)^T
 (I+L_{E,J}^TL_{E,J})^{-1}
 (n_J+L_{E,J}^Tu_E)\leq \|u_E\|_2^2
 \tag{1}
\]

for all \(E,J\subseteq[3]\) with \(|E|=|J|\).  The construction below
gives unit \(u,n\) for which (1) holds with \(L=tK\) once \(t\) is
sufficiently large.

## 1. The normalized Case B chart

Let \(K\) have rank two, all entries and all two-by-two minors nonzero,
and unit left and right kernels \(g,h\):

\[
 g^TK=0,\qquad Kh=0.
 \tag{2}
\]

Thus every coordinate of \(g\) and \(h\) is nonzero.  Put

\[
 M=D_gKD_h,
 \qquad D_g=\operatorname{diag}(g),\quad D_h=\operatorname{diag}(h).
 \tag{3}
\]

Then \(M\mathbf1=\mathbf1^TM=0\).  Assume that, in the present row and
column order, \(M\) is the Case B chart

\[
 M=
 \begin{pmatrix}
 -a&-b&a+b\\
 -c&d&c-d\\
 a+c&b-d&d-a-b-c
 \end{pmatrix},
 \qquad a,b,c>0,\quad d>a+b+c.
 \tag{4}
\]

Its upper-left minor is \(-D\), where

\[
 D=ad+bc>0.
 \tag{5}
\]

The signs in (4) are exactly the Case B sign table.  No positivity
assumption on the original kernel coordinates is made.  Their signs will
cancel from the scalar tests.

Choose

\[
 \beta=(0,1,-1)^T,
 \qquad
 \alpha=(1,-1,\varepsilon)^T,
 \qquad 0<\varepsilon<\frac{a+c}{c}.
 \tag{6}
\]

Define raw vectors

\[
 u_0=D_g^{-1}\alpha,
 \qquad n_0=D_h^{-1}\beta,
 \qquad
 u=\frac{u_0}{\|u_0\|_2},\quad
 n=\frac{n_0}{\|n_0\|_2}.
 \tag{7}
\]

Positive independent normalization only rescales \(\alpha\) and
\(\beta\), so it preserves every strict sign proved below.  In particular,
the construction is valid when coordinates of \(g\) or \(h\) have mixed
signs.

## 2. Proper-support cross terms

The following identity is the key calculation.  Let \(E=[3]\setminus\{i\}\)
and \(J=[3]\setminus\{j\}\).  If \(\mathbf1^T\beta=0\), choose \(v\)
with

\[
 M^Tv=\beta.
 \tag{8}
\]

Such \(v\) exists because \(\operatorname{range}(M^T)=\mathbf1^\perp\),
and is unique modulo adding a multiple of \(\mathbf1\).  Then

\[
 u_{0,E}^TK_{E,J}^{-T}n_{0,J}
 =\alpha_E^TM_{E,J}^{-T}\beta_J
 =\sum_{\ell\ne i}\alpha_\ell(v_\ell-v_i).
 \tag{9}
\]

To prove the second equality, column sums of \(M\) give

\[
 M_{E,J}^T(v_E-v_i\mathbf1_E)
 =M_{E,J}^Tv_E+v_iM_{i,J}^T
 =\beta_J.
 \tag{10}
\]

This proves (9), and also shows that its value is independent of the deleted
column \(j\).  If additionally \(\mathbf1^T\alpha=0\), the right side of
(9) would equal \(\alpha^Tv\).  The present construction instead needs
\(\mathbf1^T\alpha=\varepsilon\ne0\) for the full-support gap.

For (4) and (6), one solution of (8) is

\[
 v=-\frac1D(a+c,0,a)^T.
 \tag{11}
\]

Substitution in (9) gives the three possible values, one for each deleted
row:

\[
 \begin{aligned}
 C_1&=\frac{-(a+c)+\varepsilon c}{D}<0,\\
 C_2&=-\frac{a+c+\varepsilon a}{D}<0,\\
 C_3&=-\frac{a+c}{D}<0.
 \end{aligned}
 \tag{12}
\]

Hence every one of the nine proper two-coordinate cross terms is strictly
negative, both before and after the positive normalizations in (7).

For an invertible square matrix \(B\), direct expansion gives

\[
 \begin{aligned}
 &(n+tB^Tu)^T(I+t^2B^TB)^{-1}(n+tB^Tu)-\|u\|_2^2\\
 &\hspace{30mm}=\frac{2}{t}u^TB^{-T}n+O(t^{-2})
 \qquad(t\to\infty).
 \end{aligned}
 \tag{13}
\]

Every proper \(K_{E,J}\) is invertible by hypothesis.  Equations
(12)--(13), over the finite set of nine pairs, prove all proper constraints
strictly for all sufficiently large \(t\).

## 3. Scalar constraints

For every entry,

\[
 K_{ij}u_{0,i}n_{0,j}
 =\frac{M_{ij}\alpha_i\beta_j}{g_i^2h_j^2}.
 \tag{14}
\]

Thus signs of \(g_i,h_j\) do not matter.  The columns \(j=2,3\) of the
sign table (4), combined with

\[
 \operatorname{sign}\alpha=(+,-,+),
 \qquad
 \operatorname{sign}(\beta_2,\beta_3)=(+,-),
 \tag{15}
\]

show that (14) is strictly negative for all six pairs with \(j=2,3\).
For \(j=1\), \(n_{0,1}=0\), while every \(u_{0,i}\ne0\).  The scalar
gap is then exact:

\[
 \frac{(tK_{i1}u_i)^2}{1+t^2K_{i1}^2}-u_i^2
 =-\frac{u_i^2}{1+t^2K_{i1}^2}<0.
 \tag{16}
\]

For the other six scalars, the one-dimensional version of (13), together
with strict negativity in (14), proves the constraints for all sufficiently
large \(t\).

## 4. Full support

The transformed vectors satisfy

\[
 h^Tn_0=\mathbf1^T\beta=0,
 \qquad
 g^Tu_0=\mathbf1^T\alpha=\varepsilon\ne0.
 \tag{17}
\]

Both properties survive the normalizations in (7).  Since \(h\) and \(g\)
are unit kernels of \(K\), \(n\perp h\) belongs to
\(\operatorname{range}(K^T)\), and spectral decomposition of \(K^TK\)
gives

\[
 \lim_{t\to\infty}
 (n+tK^Tu)^T(I+t^2K^TK)^{-1}(n+tK^Tu)
 =\|P_{g^\perp}u\|_2^2
 =1-(g^Tu)^2<1.
 \tag{18}
\]

Thus the full-support constraint is strict for all sufficiently large \(t\).
The empty constraint is void.  Combining (12), (16), and (18), and taking
the maximum of their finitely many thresholds, proves (1) for \(L=tK\).

## Scope

This proof handles the displayed Case B sign chart and its direct
coordinate relabelings.  It does not prove a uniform threshold as entries or
minors approach zero, and it does not resolve the Case A or Case C charts.
It is an algebraic subcase of the finite-polar problem, not a general
rank-two result.
