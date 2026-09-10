# Case-A generic rank-two matrices admit an asymptotic finite-polar witness

Status: proved for the generic case-A sign stratum under scalar dilation
\(K\mapsto tK\).  This is a subcase of the real rank-two three-polar
problem.  It does not settle the other sign strata or entry/minor-zero
boundaries.

For equal-size \(E,J\subseteq[3]\), write

\[
 \mathcal P_{EJ}(t;u,n)=
 (n_J+tK_{E,J}^{T}u_E)^T
 (I+t^2K_{E,J}^{T}K_{E,J})^{-1}
 (n_J+tK_{E,J}^{T}u_E). \tag{1}
\]

The finite-polar inequalities are
\(\mathcal P_{EJ}(t;u,n)\leq\|u_E\|_2^2\).  We prove that, in the
case below, one pair \(u,n\), each separately rescaled to unit norm,
satisfies every inequality strictly for all sufficiently large \(t\).

## 1. Case-A normalization and a common inverse pairing

Let \(K\) have rank two, with no zero entry or two-by-two minor.  Let
\(g^TK=0\), \(Kh=0\), and put

\[
 M=D_gKD_h,\qquad D_g=\operatorname{diag}(g),\quad
 D_h=\operatorname{diag}(h). \tag{2}
\]

Suppose that, after the sign normalization of the sign-pivot note, \(M\)
is in case \(A\) and its upper-left minor is negative.  Then

\[
 M=\begin{pmatrix}
 -a&-b&a+b\\
 -c&-d&c+d\\
 a+c&b+d&-(a+b+c+d)
 \end{pmatrix},
 \quad a,b,c,d>0,\quad ad-bc<0. \tag{3}
\]

Choose initially

\[
 \alpha_0=(1,0,-1)^T,\qquad \beta_0=(0,1,-1)^T. \tag{4}
\]

For the rows \(E=\{1,3\}\) and columns \(J=\{2,3\}\), direct inversion
gives

\[
 \alpha_{0,E}^{T}M_{E,J}^{-T}\beta_{0,J}
 =-\frac{c}{bc-ad}<0. \tag{5}
\]

The same value occurs for every two-element \(E,J\).  More generally,
if \(\mathbf1^T\alpha=\mathbf1^T\beta=0\), define

\[
 q_{EJ}=\alpha_E^TM_{E,J}^{-T}\beta_J. \tag{6}
\]

For fixed \(E,J\), let \(y\) be supported on \(E\), with
\(M_{E,J}^Ty_E=\beta_J\).  The entries of \(M^Ty\) on \(J\) equal
\(\beta_J\).  Both \(M^Ty\) and \(\beta\) have coordinate sum zero, so
their remaining entries agree as well: \(M^Ty=\beta\).  Any two
solutions differ by a multiple of \(\mathbf1\), and
\(\alpha^T\mathbf1=0\).  Hence

\[
 q_{EJ}=\alpha^Ty
\]

is independent of \(E,J\).  In particular, (5) proves the asserted
common value for \(\alpha_0,\beta_0\).

Now take sufficiently small \(\epsilon,\delta>0\) and set

\[
 \alpha=(1,\epsilon,-1-\epsilon)^T,\qquad
 \beta=(\delta,1,-1-\delta)^T. \tag{7}
\]

Their coordinate signs are \((+,+,-)\), and their sums vanish.  The
common pairing \(q=q_{EJ}\) is continuous in \((\epsilon,\delta)\), so
(5) gives a choice with \(q<0\).  Define

\[
 u=D_g^{-1}\alpha,\qquad n=D_h^{-1}\beta. \tag{8}
\]

Both vectors are nonzero.  Also \(g^Tu=h^Tn=0\), so

\[
 u\in\operatorname{range}K,\qquad n\in\operatorname{range}K^T. \tag{9}
\]

## 2. All support sizes have a negative first correction

For singleton \(E=\{i\}\), \(J=\{j\}\), expansion of (1) gives

\[
 \mathcal P_{EJ}(t;u,n)
 =u_i^2+\frac{2}{t}\frac{u_in_j}{K_{ij}}+O(t^{-2})
 =u_i^2+\frac{2}{t}\frac{\alpha_i\beta_j}{M_{ij}}+O(t^{-2}).
 \tag{10}
\]

The sign pattern in (3) is the negative outer product of
\((+,+,-)\) with itself.  Thus every coefficient
\(\alpha_i\beta_j/M_{ij}\) is strictly negative.

For two-element \(E,J\), the corresponding submatrix is invertible and

\[
 \mathcal P_{EJ}(t;u,n)
 =\|u_E\|_2^2+
 \frac{2}{t}u_E^TK_{E,J}^{-T}n_J+O(t^{-2})
 =\|u_E\|_2^2+\frac{2q}{t}+O(t^{-2}). \tag{11}
\]

The last identity follows from (2), (6), and (8).

For full support, let \(K=U\Sigma V^T\) be a thin singular-value
decomposition.  By (9), write \(u=Ux\) and \(n=Vy\).  Equation (1)
becomes

\[
 \mathcal P_{[3],[3]}(t;u,n)
 =\sum_{\ell=1}^2
 \frac{(y_\ell+t\sigma_\ell x_\ell)^2}
 {1+t^2\sigma_\ell^2}
 =\|u\|_2^2+
 \frac{2}{t}u^T(K^+)^Tn+O(t^{-2}). \tag{12}
\]

To identify the cross term, put \(w=(K^+)^Tn\) and
\(z=D_g^{-1}w\).  From \(K^Tw=n\) and (2), \(M^Tz=\beta\).  Therefore
\(\alpha^Tz=q\) by the argument after (6), while

\[
 u^Tw=(D_g^{-1}\alpha)^TD_gz=\alpha^Tz=q. \tag{13}
\]

Thus the full-support correction in (12) is also \(2q/t<0\).

There are finitely many \(E,J\).  Equations (10)--(12) therefore imply
that all finite-polar inequalities are strict once \(t\geq t_0(K,\epsilon,
\delta)\).  In fact \(u\) and \(n\) may be normalized separately.  If
\(\widehat u=c_u u\) and \(\widehat n=c_n n\), with \(c_u,c_n>0\), the
leading term in each expansion is \(c_u^2\|u_E\|_2^2\).  Its first
correction is \(c_uc_n\) times the negative coefficient in
(10)--(12).  Hence the same finite-support argument applies after taking
\(c_u=\|u\|_2^{-1}\) and \(c_n=\|n\|_2^{-1}\).  The witness can therefore
be required to satisfy

\[
 \|\widehat u\|_2=\|\widehat n\|_2=1. \tag{14}
\]

The proof uses the exact singleton, proper-support, and full-support
conditions.  It gives no bound uniform in \(K\), and it does not extend
without further work to cases \(B\), \(C\), or a zero entry or minor.
