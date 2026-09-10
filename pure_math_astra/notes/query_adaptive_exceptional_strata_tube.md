# Uniform square-root obstruction on exceptional projector strata and tubes

Status: proved real finite-dimensional calculation.  It concerns only the
query-adaptive atomic value with an exact coordinate mean.  It makes no
claim about finite descriptions, bytes, or novelty.

For a rank-two orthogonal projector \(P\) on \(\mathbb R^4\), write

\[
 G_r(P)=P+r^2(I-P),\qquad 0<r\leq1.
\tag{1}
\]

This note proves two statements.

1. With \(c_0=1/800\),

   \[
   \Psi_2(G_r(P_0))\geq c_0r
   \tag{2}
   \]

   for every exceptional direct-sum rank-two projector \(P_0\): two
   rank-one coordinate blocks (the \(2+2\) stratum), one rank-one
   three-coordinate block plus a singleton (the \(3+1\) stratum), and
   their zero-coordinate degenerations.

2. If \(\|P-P_0\|_{\rm op}\leq Kr\), where \(K\) is fixed, then

   \[
   \Psi_2(G_r(P))\geq {c_0\over(1+K)^2}r.
   \tag{3}
   \]

Thus every fixed-radius-in-\(r\) Grassmann tube around the exceptional
locus has a square-root lower bound.  The result does not control approach
rates with \(\|P-P_0\|/r\to\infty\).

## 1. The 2+2 stratum away from its 3+1 boundary

After coordinate signs and swaps, write a \(2+2\) projector as

\[
 P=(u_1u_1^T)\oplus(u_2u_2^T),
 \qquad
 u_i=(\cos\theta_i,\sin\theta_i),
 \quad0\leq\theta_i\leq\pi/4.
\tag{4}
\]

Let \(h_i=(\sin\theta_i,-\cos\theta_i)\).  The two blocks of \(G_r(P)\)
are \(H_i=u_iu_i^T+r^2h_ih_i^T\).  For a polar vector
\(z=(z_1,z_2)\), with one two-vector per block, set

\[
 q_i=z_i^TH_i^{-1}z_i,
 \qquad
 m_i=\max_j{(z_i)_j^2\over(H_i)_{jj}}.
\tag{5}
\]

Listing the six coordinate pairs gives the exact constraints

\[
 q_1\leq1,\qquad q_2\leq1,\qquad m_1+m_2\leq1.
\tag{6}
\]

Assume

\[
 \sin\theta_i\geq r/4\quad(i=1,2).
\tag{7}
\]

Fix \(\rho=1/16\), put \(c=r_0=1/512\), and suppose \(0<r\leq r_0\).
Define

\[
 \alpha^2={1\over2}-3r\rho,
 \qquad z_i=\alpha u_i+r\rho h_i.
\tag{8}
\]

The block eigenbasis makes

\[
 q_i=\alpha^2+\rho^2<1.
\tag{9}
\]

For the first coordinate of a block, write \(c=\cos\theta_i\) and
\(s=\sin\theta_i\).  Since \(s\leq c\),

\[
 { (\alpha c+r\rho s)^2\over c^2+r^2s^2}
 \leq (\alpha+r\rho)^2
 \leq\alpha^2+3r\rho.
\tag{10}
\]

For the second coordinate, (7) and \(\rho\leq\alpha/4\) give

\[
 0\leq\alpha s-r\rho c\leq\alpha s,
\tag{11}
\]

so its normalized square is at most \(\alpha^2\).  Hence

\[
 m_1+m_2\leq2\alpha^2+6r\rho=1.
\tag{12}
\]

Thus \(z\) is polar feasible.

For \(v=cr\), its ellipsoid value is exactly

\[
 z^T(G_r(P)+crI)^{-1}z
 ={2\alpha^2\over1+cr}+{2r^2\rho^2\over r^2+cr}
 ={1-6r\rho\over1+cr}+{2r\rho^2\over r+c}.
\tag{13}
\]

Subtracting one from (13) gives

\[
 z^T(G_r(P)+crI)^{-1}z-1
 =r\left({2\rho^2\over r+c}-{c+6\rho\over1+cr}\right).
\tag{14}
\]

Since \(r\leq c\), the right side is at least

\[
 r\left({\rho^2\over c}-c-6\rho\right)>0.
\tag{15}
\]

Here \(\rho^2/c=2\), while \(c+6\rho<3/8\).  Atomic polarity therefore
gives \(\Psi_2(G_r(P))>r/512\) in the regime (7).

## 2. The boundary of 2+2 belongs to a 3+1 tube

If \(\sin\theta_1<r/4\), replace the first rank-one block in (4) by the
coordinate singleton \(e_1e_1^T\).  Keep the second block and treat the
unused second coordinate as a zero coordinate in the three-coordinate
block.  The resulting projector \(P_0\) is a \(3+1\) projector, and

\[
 \|P-P_0\|_{\rm op}
 =\|u_1u_1^T-e_1e_1^T\|_{\rm op}
 =\sin\theta_1<r/4.
\tag{16}
\]

The same argument applies if the second angle is small.  The proved
\(3+1\) bound in `query_adaptive_3plus1_uniform_lower.md` is
\(\Psi_2(G_r(P_0))\geq r/512\), including its zero-coordinate cases.
Equation (22), with \(K=1/4\), therefore gives

\[
 \Psi_2(G_r(P))\geq {r/512\over(5/4)^2}={r\over800}.
\tag{17}
\]

Thus (2) holds for all of the \(2+2\) stratum after the tube comparison
below.

The remaining exceptional patterns have one or two zero coordinate rows.
After a permutation they are already a \(3+1\) projector with a zero entry
in its three-coordinate rank-one vector.  They are therefore covered by
the same cited calculation.

## 3. Exact Gram comparison on a Grassmann tube

The square roots have the particularly simple form

\[
 G_r(P)^{1/2}=rI+(1-r)P.
\tag{18}
\]

Suppose \(\|P-P_0\|_{\rm op}\leq Kr\).  For every \(x\), (18) gives

\[
 \begin{aligned}
 \|G_r(P_0)^{1/2}x\|_2
 &\leq\|G_r(P)^{1/2}x\|_2+(1-r)Kr\|x\|_2\\
 &\leq(1+K)\|G_r(P)^{1/2}x\|_2,
 \end{aligned}
\tag{19}
\]

because \(G_r(P)\succeq r^2I\).  Equivalently,

\[
 G_r(P_0)\preceq(1+K)^2G_r(P).
\tag{20}
\]

For any fixed legal estimator \(Y\) and query \(x\), (20) implies

\[
 \mathbb E(Y-x)^TG_r(P_0)(Y-x)
 \leq(1+K)^2
 \mathbb E(Y-x)^TG_r(P)(Y-x).
\tag{21}
\]

Taking the infimum over the same exact-mean, two-sparse laws and then the
supremum over unit queries yields

\[
 \Psi_2(G_r(P))\geq{\Psi_2(G_r(P_0))\over(1+K)^2}.
\tag{22}
\]

This proves (3).

## 4. Completing the range of r

The direct polar constructions establish the claimed bounds for
\(0<r\leq1/512\).  When \(r\geq1/512\), every \(G_r(P)\succeq r^2I\), and

\[
 \Psi_2(G_r(P))\geq r^2\Psi_2(I_4)=r^2\geq {r\over512}>{r\over800}.
\tag{23}
\]

Thus \(c_0=1/800\) holds for all \(0<r\leq1\).

## Scope

This is a real-field result.  The tube parameter is the operator-norm
Grassmann distance between projectors.  The proof does not establish a
uniform lower bound for a sequence of projectors whose distance from every
exceptional stratum is larger than order \(r\) but still tends to zero.
