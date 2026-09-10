# Independent review of the 3+1 uniform lower bound; depends on query_adaptive_3plus1_uniform_lower.md.

Verdict: **correct**, with an explicit admissible constant

\[
 c={1\over512}.
\tag{1}
\]

This review checks only the fixed (3+1) stratum in the reviewed note. It
does not extend the conclusion to moving general rank-two planes.

## 1. Polar feasibility

In Case 1, the two-coordinate constraints follow from

\[
 \|u_S\|_{H_S^{-1}}\le1,\qquad
 \|rh_S\|_{H_S^{-1}}\le1,
\tag{2}
\]

because \(H_S\succeq r^2I\). Hence the triangle inequality gives
\(\|z_S\|_{H_S^{-1}}\le\alpha+\rho=5/8\). This covers every pair inside
the three-coordinate block.

For pairs using the singleton, the second and third normalized coordinate
squares are at most \(\alpha^2\). For the first, with
\(a\ge1/\sqrt3\), \(b\le a\), and \(D=\sqrt{a^2+b^2}\),

\[
 {z_1^2\over H_{11}}
 \le\left(\alpha+{r\rho b\over aD}\right)^2
 \le\left(\alpha+\sqrt3r\rho\right)^2
 \le\alpha^2+4r\rho
\tag{3}
\]

for \(0<r\le1\). Thus the reviewed choice
\(w^2=1-\alpha^2-4r\rho\) makes all singleton constraints valid and
remains positive. No coordinate-face exception occurs: condition
\(b\ge Kr\) is exactly what makes the second coordinate nonnegative.

In Case 2, the signed standardized vector has two coordinates of magnitude
\(1/\sqrt2\). A two-by-two correlation matrix with nonnegative
correlation \(\gamma\) gives polar value \(1/(1+\gamma)\le1\), and every
pair with the singleton has value one. This verifies all six constraints.

## 2. Explicit small-r constants

Take the reviewed values

\[
 K={1\over4},\quad \alpha={1\over2},\quad \rho={1\over8},
 \quad C=4,\quad c_0={1\over512},\quad r_0=c_0.
\tag{4}
\]

For Case 1 and \(r\le c_0\), equation (14) of the reviewed note gives

\[
 y^T(G+c_0rI)^{-1}y-1
 \ge r\left({\rho^2\over2c_0}-4\rho-c_0\right)>0.
\tag{5}
\]

Here \(\rho^2/(2c_0)=4\), whereas \(4\rho+c_0<1\). This establishes the
polar violation uniformly in the first case.

For Case 2, put

\[
 \ell={9-\sqrt{17}\over64}>{1\over16}.
\tag{6}
\]

The \((1,2)\) summand in the reviewed identity (20) proves
\(L\ge\ell r^2\) already for \(r\le c_0\). To see the uniformity directly,
write \(u_2=rt\), \(u_3=rs\), with \(0\le s\le t\le1/4\). Its square
root difference, divided by \(r\), is bounded below by

\[
 \sqrt{1+t^2-{25\over128}r^2}-t
 \ge\sqrt{1-{25\over128}r^2}-{1\over4}
 >{\sqrt{17}-1\over8}.
\tag{7}
\]

Squaring and using \(2L\) at least this summand yields (6). The exact
expression in the reviewed equation (19) is increasing in \(L\), and for
\(r\le c_0\) it gives

\[
 y^T(G+c_0rI)^{-1}y-1
 \ge r\left({\ell\over2c_0}-c_0(1+\ell)\right)>0.
\tag{8}
\]

Thus the same \(c_0\) works in both cases.

## 3. The remaining range and scope

For \(r\ge r_0\), \(G\succeq r^2I\) and the diagonal value
\(\Psi_2(I_4)=1\) give

\[
 \Psi_2(G)\ge r^2\ge r_0r=c_0r.
\tag{9}
\]

The proof therefore establishes the claimed bound for every
\(0<r\le1\), uniformly over all unit \(u\). The only qualification is
scope, already stated in the reviewed note: this argument uses the fixed
rank-one three-coordinate block and does not provide a compactness theorem
for general \(P_r\) approaching that stratum.
