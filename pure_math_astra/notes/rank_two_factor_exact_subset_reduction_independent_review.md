# rank_two_factor_exact_subset_reduction_independent_review.md — independent review of the rank-two factor subset reduction and sign-consistent pivot obstruction; depends on rank_two_factor_exact_subset_reduction.md, rank_two_sign_consistent_inverse_pivot.md.

# Independent review: rank-two subset reduction and inverse pivots

## Verdict

The exact subset reduction is correct, including its \(h_\ell=0\) boundary
formula. The sign-consistent inverse-pivot lemma is correct under its stated
generic hypotheses. The three zero-sum sign patterns and the listed
admissible-pivot sets are exhaustive. The \(\varepsilon\)-scaled example
correctly disproves both a perfect-matching strengthening and the proposed
kernel-magnitude inference.

None of these facts is a counterexample to the finite three-polar lemma.
They only eliminate one pivot-centered route to proving it.

## 1. Reconstructing the factor reduction

Let

\[
K=AB^T,\qquad B^TB=I_2,\qquad B^Th=0,\qquad \|h\|_2=1,
\]

and write \(n=Bv+zh\). For \(E,J\subseteq[3]\), set

\[
H_E=A_E^TA_E,\quad C_J=B_J^TB_J,\quad
d_J=B_J^Th_J,\quad w_E=v+A_E^Tu_E.
\]

Then

\[
n_J+K_{E,J}^Tu_E=B_Jw_E+zh_J.
\tag{1}
\]

Put \(L=I+B_JH_EB_J^T\). Woodbury gives

\[
\begin{aligned}
B_J^TL^{-1}B_J&=C_J(I+H_EC_J)^{-1},\\
h_J^TL^{-1}B_J&=d_J^T(I+H_EC_J)^{-1},\\
h_J^TL^{-1}h_J
&=\|h_J\|_2^2-d_J^T(I+H_EC_J)^{-1}H_Ed_J.
\end{aligned}
\tag{2}
\]

Expanding (1) against \(L^{-1}\) gives exactly equation (5) of the
reviewed reduction note. The possible nonsymmetry of
\((I+H_EC_J)^{-1}\) is harmless: its two appearances are scalar cross
terms, while

\[
C_J(I+H_EC_J)^{-1}=(I+C_JH_E)^{-1}C_J
\]

is symmetric.

For \(J=[3]\), \(C_J=I_2\), \(d_J=0\), so the full-support condition is

\[
(v+A^Tu)^T(I+A^TA)^{-1}(v+A^Tu)+z^2\le1.
\tag{3}
\]

This uses the \(J\)-dependent matrix \(C_J\) in every proper support. It
does not replace it by \(I_2\).

## 2. Complement formula, including \(h_\ell=0\)

Let \(J=[3]\setminus\{\ell\}\). Orthogonality of \([B\ h]\) gives

\[
C_J=I_2-b_\ell b_\ell^T,\qquad
d_J=-b_\ell h_\ell,\qquad
\|b_\ell\|_2^2+h_\ell^2=1.
\tag{4}
\]

### Nonzero complement coordinate

If \(h_\ell\ne0\), then \(C_J\) is positive definite, hence \(B_J\) is
invertible. Since \(B^Th=0\),

\[
B_J^Th_J=-b_\ell h_\ell.
\]

The vector \(-b_\ell/h_\ell\) has the same image under \(B_J\) as \(h_J\):
after applying \(B_J^T\), both sides equal \(-b_\ell h_\ell\). Therefore

\[
B_J^{-1}h_J=-\frac{b_\ell}{h_\ell}.
\tag{5}
\]

Sherman--Morrison gives

\[
C_J^{-1}=I_2+\frac{b_\ell b_\ell^T}{h_\ell^2}.
\tag{6}
\]

Also

\[
I+B_JH_EB_J^T
=B_J(C_J^{-1}+H_E)B_J^T.
\tag{7}
\]

Substitution of (5)--(7) into the original quadratic form yields

\[
\left(w_E-z\frac{b_\ell}{h_\ell}\right)^T
\left(H_E+I_2+\frac{b_\ell b_\ell^T}{h_\ell^2}\right)^{-1}
\left(w_E-z\frac{b_\ell}{h_\ell}\right)
\le\|u_E\|_2^2.
\tag{8}
\]

Thus the reviewed equation (12) is exact.

### Zero complement coordinate

If \(h_\ell=0\), then \(\|b_\ell\|_2=1\), and \(C_J\) has rank one.
Choose a unit \(d\perp b_\ell\). There is a unit \(a\in\mathbb R^2\)
orthogonal to \(h_J\) such that

\[
B_J=ad^T.
\]

Indeed, \(B_J^TB_J=dd^T\). Thus

\[
B_Jw_E+zh_J=a(d^Tw_E)+zh_J,
\]

and \(a,h_J\) are an orthonormal basis of \(\mathbb R^2\). Since

\[
I+B_JH_EB_J^T
=I+(d^TH_Ed)aa^T,
\]

the exact proper-support condition is

\[
z^2+\frac{(d^Tw_E)^2}{1+d^TH_Ed}\le\|u_E\|_2^2.
\tag{9}
\]

This verifies the reviewed boundary formula. It also shows why taking an
\(h_\ell\to0\) limit in (8) without separating the surviving \(d\)-direction
is invalid.

## 3. Exhaustive sign audit

For a generic rank-two \(K\), let nonzero left and right kernel vectors be
\(g,h\), and define

\[
M=\operatorname{diag}(g)K\operatorname{diag}(h).
\]

Then \(M\mathbf1=\mathbf0\) and \(\mathbf1^TM=\mathbf0^T\). Every row and
column has both signs. After a global sign change, there are either three or
four positive entries:

- with three, each row and column has exactly one, so they form a perfect
  matching;
- with four, the positive row degrees and positive column degrees are both
  \((2,1,1)\); the two degree-two vertices are either adjacent or
  nonadjacent.

Up to row and column permutations, these are precisely

\[
A=\begin{pmatrix}-&-&+\\-&-&+\\+&+&-\end{pmatrix},\quad
B=\begin{pmatrix}-&-&+\\-&+&-\\+&-&+\end{pmatrix},\quad
C=\begin{pmatrix}-&-&+\\-&+&-\\+&-&-\end{pmatrix}.
\tag{10}
\]

This proves the exhaustiveness claimed in the reviewed note.

Let \(\Delta=\det M_{(1,2),(1,2)}\). In cases \(B,C\), the upper-left
block has signs

\[
\begin{pmatrix}-A_0&-B_0\\-C_0&D_0\end{pmatrix},
\qquad A_0,B_0,C_0,D_0>0,
\]

so \(\Delta=-A_0D_0-B_0C_0<0\). In case \(A\), swapping the first two
columns preserves its sign table and reverses \(\Delta\), so the labels can
again be chosen with \(\Delta<0\).

Writing a zero-row/zero-column-sum matrix by its upper-left block directly
shows

\[
\operatorname{adj}M=\Delta\,\mathbf1\mathbf1^T.
\tag{11}
\]

For example, if the upper-left block is
\(\begin{psmallmatrix}a&b\\c&d\end{psmallmatrix}\), the bottom-right
cofactor is

\[
d(a+b+c+d)-(b+d)(c+d)=ad-bc=\Delta.
\]

Equation (11), the sign tables (10), and \(\Delta<0\) yield the following
complete direct check of

\[
M_{ij}M_{m\ell}\det M_{(i,m),(j,\ell)}>0
\quad(m\ne i,\ \ell\ne j).
\tag{12}
\]

\[
\begin{array}{c|c}
\text{sign table}&\text{all admissible pivots}\\ \hline
A&\{(1,2),(2,1)\}\\
B&\{(1,1),(1,3),(3,1)\}\\
C&\{(1,3),(2,2),(3,1)\}.
\end{array}
\tag{13}
\]

As a numerical exact check of all three rows of (13), take respectively

\[
\begin{aligned}
M_A&=\begin{pmatrix}-1&-2&3\\-3&-4&7\\4&6&-10\end{pmatrix},\\
M_B&=\begin{pmatrix}-1&-2&3\\-3&7&-4\\4&-5&1\end{pmatrix},\\
M_C&=\begin{pmatrix}-1&-2&3\\-3&4&-1\\4&-2&-2\end{pmatrix}.
\end{aligned}
\tag{14}
\]

Each has zero row and column sums, rank two, no zero entry or two-by-two
minor, and \(\Delta=-2,-13,-10\), respectively. Substitution in (12)
gives exactly the three pivot sets in (13).

Finally, diagonal scaling transfers (12): if
\(K=D_rMD_c\), the product in (12) is multiplied by

\[
(r_ir_mc_jc_\ell)^2>0.
\tag{15}
\]

The sign-pivot theorem is therefore correct, including its orientation
convention for ordered minors.

## 4. Exact failure of matching and kernel-magnitude control

The \(A\) example in (14) has only the two admissible pivots

\[
(1,2),\qquad(2,1),
\tag{16}
\]

which share rows and columns. Hence the admissible-pivot relation need not
contain a perfect matching.

For \(0<\varepsilon\), set

\[
g=\frac{(\varepsilon,\varepsilon,1)^T}
{\sqrt{1+2\varepsilon^2}},\qquad
h=\frac{(1,1,\varepsilon)^T}
{\sqrt{2+\varepsilon^2}},
\]

and

\[
K_\varepsilon=
\operatorname{diag}(g)^{-1}M_A\operatorname{diag}(h)^{-1}.
\tag{17}
\]

Then

\[
g^TK_\varepsilon=\mathbf0^T,\qquad K_\varepsilon h=\mathbf0,
\tag{18}
\]

and the exact admissible-pivot set remains (16) by (15). At either allowed
pivot,

\[
\frac{|g_1|}{|h_2|}
=\frac{|g_2|}{|h_1|}
=\varepsilon
\sqrt{\frac{2+\varepsilon^2}{1+2\varepsilon^2}}
\longrightarrow0
\quad(\varepsilon\downarrow0).
\tag{19}
\]

Thus neither a perfect matching nor an admissible pivot satisfying a
uniform lower comparison \(|g_i|\gtrsim|h_j|\) follows from the
sign-consistency lemma. This is an exact counterexample to that proposed
auxiliary inference, not to a polar feasibility statement.

## Scope

The reviewed arguments prove a precise reduction and a precise obstruction.
They do not produce a \(K\) for which the finite three-polar conditions are
infeasible, and they do not refute any finite-polar lemma. Any such claim
would require an independent failure of the full singleton, proper-subset,
and full-support constraints.

