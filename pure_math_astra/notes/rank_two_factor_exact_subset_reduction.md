# Exact two-dimensional reduction of rank-two three-polar constraints

Status: exact reduction and an obstruction to one natural cancellation
ansatz.  This does not prove or disprove the finite three-polar lemma.

Let \(K\in\mathbb R^{3\times3}\) have rank two.  Choose a factorization

\[
 K=AB^T,\qquad A,B\in\mathbb R^{3\times2},\qquad B^TB=I_2, \tag{1}
\]

and let \(h\in\mathbb R^3\) be the unit vector with \(B^Th=0\).  Write
\(a_i^T\) and \(b_j^T\) for the rows of \(A\) and \(B\).  Every
\(n\in\mathbb R^3\) has the unique form

\[
 n=Bv+zh,\quad v\in\mathbb R^2,\quad z\in\mathbb R,\quad
 \|n\|_2^2=\|v\|_2^2+z^2. \tag{2}
\]

For \(E\subseteq[3]\), set

\[
 H_E=A_E^TA_E,\quad w_E=v+A_E^Tu_E. \tag{3}
\]

The following formulas retain the exact \(J\)-dependence.  In particular,
they do not replace \(B_J^TB_J\) by \(I\).

## 1. The common two-dimensional formula

For \(|E|=|J|\), put

\[
 C_J=B_J^TB_J,\quad d_J=B_J^Th_J,\quad R_{EJ}=(I+H_EC_J)^{-1}. \tag{4}
\]

The polar left side is exactly

\[
 w_E^TC_JR_{EJ}w_E
 +2z\,d_J^TR_{EJ}w_E
 +z^2\left(\|h_J\|_2^2-d_J^TR_{EJ}H_Ed_J\right). \tag{5}
\]

To prove (5), use

\[
 K_{E,J}=A_EB_J^T,\quad
 n_J+K_{E,J}^Tu_E=B_Jw_E+zh_J, \tag{6}
\]

and Woodbury's identities

\[
 \begin{aligned}
 B_J^T(I+B_JH_EB_J^T)^{-1}B_J&=C_JR_{EJ},\\
 h_J^T(I+B_JH_EB_J^T)^{-1}B_J&=d_J^TR_{EJ},\\
 h_J^T(I+B_JH_EB_J^T)^{-1}h_J
 &=\|h_J\|_2^2-d_J^TR_{EJ}H_Ed_J.
 \end{aligned} \tag{7}
\]

Although \(R_{EJ}\) need not be symmetric, the scalar in (5) is real;
\(C_JR_{EJ}=(I+C_JH_E)^{-1}C_J\) is symmetric.

## 2. The three support sizes

For a singleton \(E=\{i\}\), \(J=\{j\}\), (5) is the scalar box

\[
 \frac{\bigl(b_j^T(v+a_i u_i)+zh_j\bigr)^2}
 {1+(a_i^Tb_j)^2}\leq u_i^2. \tag{8}
\]

For full support, \(C_{[3]}=I_2\), \(d_{[3]}=0\), and
\(\|h\|=1\).  The condition is the two-dimensional ellipsoid

\[
 (v+A^Tu)^T(I+A^TA)^{-1}(v+A^Tu)+z^2\leq1. \tag{9}
\]

The proper two-by-two conditions have an especially useful complement
form.  Let \(J=[3]\setminus\{\ell\}\).  Orthogonal completion of
\([B\ h]\) gives

\[
 C_J=I_2-b_\ell b_\ell^T,\quad
 d_J=-b_\ell h_\ell,\quad
 \|b_\ell\|_2^2+h_\ell^2=1. \tag{10}
\]

If \(h_\ell\ne0\), then \(B_J\) is invertible and

\[
 B_J^{-1}h_J=-\frac{b_\ell}{h_\ell},\quad
 C_J^{-1}=I_2+\frac{b_\ell b_\ell^T}{h_\ell^2}. \tag{11}
\]

Congruencing the inverse in the original polar expression by \(B_J\)
therefore gives the exact two-dimensional inequality

\[
 \left(w_E-z\frac{b_\ell}{h_\ell}\right)^T
 \left(H_E+I_2+\frac{b_\ell b_\ell^T}{h_\ell^2}\right)^{-1}
 \left(w_E-z\frac{b_\ell}{h_\ell}\right)
 \leq\|u_E\|_2^2,
 \tag{12}
\]

for every two-element \(E\).  Equation (12) is not a relaxation.

If \(h_\ell=0\), then \(\|b_\ell\|=1\), \(B_J\) has rank one, and
let \(d\) be either unit vector orthogonal to \(b_\ell\).  In this
boundary case the exact condition is

\[
 z^2+\frac{(d^Tw_E)^2}{1+d^TH_Ed}\leq\|u_E\|_2^2. \tag{13}
\]

Thus the only singularity in the complement formula is explicit; it is not
legitimate to discard it by the bound \(C_J\preceq I\).

## 3. An obstruction to full residual cancellation

A tempting choice is \(v=-A^Tu\), which makes the full residual in (9)
equal to \(zh\).  Taking in addition \(u\in\ker A^T\) makes \(v=0\)
and removes the \(A\)-term from (9).  This cannot be a uniform proof
route.

Take

\[
 A=\begin{pmatrix}0&0\\1&0\\0&1\end{pmatrix},
 \qquad h=\frac1{\sqrt3}(1,1,1)^T, \tag{14}
\]

and choose any orthonormal \(B\) spanning \(h^\perp\).  Then \(K=AB^T\)
has rank two and \(\ker A^T=\operatorname{span}\{e_1\}\).  The
cancellation ansatz forces \(u=\pm e_1\), \(v=0\), and \(n=zh\).
For \(E=\{2\}\) and any singleton \(J=\{j\}\), its right side in (8)
is zero, while its numerator is \(zh_j\).  Since every \(h_j\ne0\),
the condition forces \(z=0\).

This does not give a counterexample to the finite polar lemma: it rules out
only the simultaneous choices \(v=-A^Tu\) and \(u\in\ker A^T\).  A
general witness must retain nonkernel components of \(u\), or retain a
nonzero \(v+A^Tu\), to satisfy zero or nearly zero coordinate components.

The next direct route is now finite and support-sensitive: solve the nine
boxes (8), the nine complement ellipsoids (12)--(13), and the full
ellipsoid (9), over \((u,v,z)\) with \(\|u\|=1\).  The right-kernel
coordinates \((b_\ell,h_\ell)\) expose the actual boundary strata instead
of hiding them in the matrices \(B_J\).
