# rank_two_general_skew_polar_lemma.md — finite three-polar lemma for every real skew matrix; depends on rank_k_graph_chart_reduction.md, rank_two_skew_cycle_polar_lemma.md.

# The finite three-polar lemma for all real skew matrices

For every real skew \(3\times3\) matrix \(K\), there are vectors
\(u,n\in\mathbb R^3\), both of norm one, such that for every pair
\(E,J\subseteq[3]\) with \(|E|=|J|\),

\[
(n_J+K_{E,J}^Tu_E)^T
(I+K_{E,J}^TK_{E,J})^{-1}
(n_J+K_{E,J}^Tu_E)\le\|u_E\|^2.
\tag{1}
\]

The proof below checks every scalar, proper two-coordinate, and full
constraint by explicit identities. It includes the zero matrix and
unbounded matrix entries. It proves a three-parameter rank-two subclass,
not the finite lemma for arbitrary rank-two matrices.

## Normalization and the witness

Write a skew matrix as

\[
K=\begin{pmatrix}0&c&-b\\-c&0&a\\b&-a&0\end{pmatrix}.
\tag{2}
\]

Signed coordinate permutations, followed if necessary by \(K\mapsto-K\),
allow the normalization

\[
a\ge b\ge c\ge0.
\tag{3}
\]

Here is why this reduction preserves the problem. If \(Q\) is a signed
permutation and \(K'=\varepsilon Q^TKQ\), where \(\varepsilon=\pm1\),
a witness \(u',n'\) for \(K'\) gives a witness
\(u=\varepsilon Qu'\), \(n=Qn'\) for \(K\). Restricted signed
permutations preserve all the norms and inverses in (1).
The axial vector \(v=(a,b,c)\) of (2) transforms under conjugation to
\(\det(Q)Q^Tv\); the additional sign removes \(\det(Q)\).
Choose \(Q\) to order the absolute values of the three entries.

Put

\[
\gamma=\sqrt{1+c^2},\quad \beta=\sqrt{1+b^2},\quad
s=c+\gamma,\quad z=b+\beta,\quad d=a-b.
\tag{4}
\]

Thus \(z\ge s\ge1\), \(d\ge0\), and

\[
s^2-1=2cs,\quad z^2-1=2bz,\quad
1+cs=s\gamma,\quad
s(\gamma-c)=1,\quad z(\beta-b)=1.
\tag{5}
\]

Use the unnormalized vectors

\[
\widetilde u=(1,-s,-z)^T,\qquad
\widetilde n=(1,-s,z)^T,
\tag{6}
\]

then divide both by \(\sqrt{1+s^2+z^2}\). Because (1) is homogeneous
of degree two in \((u,n)\), it suffices to check (6).

## The nine scalar boxes

The diagonal boxes hold with equality because \(K_{ii}=0\) and
\(|\widetilde u_i|=|\widetilde n_i|\).
For the four boxes joining coordinate 1 to coordinates 2 or 3, (5) gives

\[
|-s+c|=\gamma,\qquad |1+cs|=s\gamma,
\]
\[
|z-b|=\beta,\qquad |1-bz|\le1+bz=z\beta.
\tag{7}
\]

The last two boxes are
\(|z-as|\le s\sqrt{1+a^2}\) and
\(|-s+az|\le z\sqrt{1+a^2}\).
Both follow from

\[
0<\frac{s}{z}\le1\le\frac{z}{s}
\le z\le a+\sqrt{1+a^2}
\]

and \(a-\sqrt{1+a^2}<0\).

## The nine proper two-coordinate constraints

For a \(2\times2\) submatrix \(A=K_{E,J}\), set

\[
M=I_2+A^TA,\qquad
w=\widetilde n_J+A^T\widetilde u_E,
\]
\[
\Delta_{E,J}
=\|\widetilde u_E\|^2\det M-w^T\operatorname{adj}(M)w.
\tag{8}
\]

Since \(M\) is positive definite, (1) is equivalent to
\(\Delta_{E,J}\ge0\). Write \(12,13,23\) for the three two-element
subsets. Direct expansion, using only (5), gives these nine identities:

\[
\Delta_{12,12}=0,
\tag{9}
\]
\[
\Delta_{12,13}=2a\gamma\beta,
\tag{10}
\]
\[
\Delta_{12,23}
=2\gamma\bigl[as(\gamma\beta-bc)+c(s\gamma+bz)\bigr],
\tag{11}
\]
\[
\Delta_{13,12}
=2\gamma\bigl[2bz\gamma+a(b+z)\bigr],
\tag{12}
\]
\[
\Delta_{13,13}=4bz(1+b^2),
\tag{13}
\]
\[
\Delta_{13,23}
=2\beta\bigl[az(\gamma\beta-bc)+b(z\beta+cs)\bigr],
\tag{14}
\]
\[
\Delta_{23,12}
=\gamma^2(z^2-s^2)+2bs\gamma z
 +2as\gamma(bs+z\gamma),
\tag{15}
\]
\[
\begin{aligned}
\Delta_{23,13}
={}&4bz\,d^2
 +2z\bigl[\gamma+(s+4)b^2+bcz\bigr]d\\
&+b^2(s^2+z^2-2)+2bz\gamma(1+s)
 +2sb^3z+2b^2cz^2,
\end{aligned}
\tag{16}
\]
\[
\Delta_{23,23}=4asz(1+a^2).
\tag{17}
\]

Every displayed term is nonnegative. In particular,
\(\gamma\beta>bc\), \(z^2\ge s^2\), and \(s^2+z^2\ge2\).

For completeness, the following expansions reconstruct the cancellations
in the less immediate identities. In (10),

\[
M=\begin{pmatrix}\gamma^2&-ac\\-ac&\beta^2+a^2\end{pmatrix},
\quad w=(s\gamma,\beta-as)^T,\quad
\det M=\gamma^2\beta^2+a^2.
\]

The constant and quadratic coefficients in \(a\) cancel by
\(2s\gamma=1+s^2\) and \(s(\gamma-c)=1\); the linear coefficient
is \(2\gamma\beta\).

For (11) and (14), the off-diagonal entry of \(M\) is \(-bc\).
The vector \(w\) is respectively
\((-\gamma,\beta-as)^T\) and \((az-\gamma,\beta)^T\).
Their quadratic coefficients in \(a\) cancel. The respective remaining
linear coefficients are \(2s\gamma(\gamma\beta-bc)\) and
\(2z\beta(\gamma\beta-bc)\). The constants simplify to the remaining
terms in (11) and (14), using
\(b^2+b\beta=bz\) and \(c^2+c\gamma=cs\).

For (12), \(w=(1-bz,az-\gamma)^T\) and
\(M_{11}=\beta^2\), \(M_{22}=\gamma^2+a^2\), \(M_{12}=-ab\).
The quadratic coefficient in \(a\) vanishes, the constant is
\(4bz\gamma^2\), and the linear coefficient is \(2\gamma(b+z)\).

For (15), \(w=(s\gamma-bz,az-s)^T\) and
\(M_{11}=\gamma^2+b^2\), \(M_{22}=1+a^2\), \(M_{12}=-ab\).
Its quadratic coefficient vanishes; its constant and linear coefficients
are the first two terms and the last term of (15).

For (16), \(w=(s\gamma-bz,z-as)^T\) and the same diagonal entries
of \(M\), with \(M_{12}=-ac\). Before substituting \(a=b+d\), (8) is

\[
4bz\,a^2+
2az(\gamma+sb^2+bcz)
b^2(s^2-z^2)+2bs\gamma z.
\tag{18}
\]

Substitution of \(a=b+d\) and \(4b^3z=2b^2(z^2-1)\) gives (16).
The principal identities (9), (13), and (17) follow at once from
\(A^TA\) being a scalar matrix.

## The full three-coordinate condition

For \(v=(a,b,c)^T\) and \(q=1+\|v\|^2\),

\[
K^TK=\|v\|^2I-vv^T,\qquad
(I+K^TK)^{-1}=\frac{I+vv^T}{q}.
\tag{19}
\]

Let \(w=\widetilde n+K^T\widetilde u\) and
\(U=\|\widetilde u\|^2=\|\widetilde n\|^2\). Since
\(\widetilde n-\widetilde u=2z e_3\), skew-symmetry gives

\[
\begin{aligned}
qU-\|w\|^2-(v^Tw)^2
&=(v^T\widetilde u)^2-(v^T\widetilde n)^2
  +2\widetilde n^TK\widetilde u\\
&=4z\bigl[b+as-c(a-bs)\bigr]\\
&=4z\gamma(a+bs)\ge0.
\end{aligned}
\tag{20}
\]

Equations (19)--(20) prove the full condition. The empty condition is void.
All nineteen nonvoid inequalities are now proved.

## Consequence and remaining boundary

The finite three-polar constant is therefore \(\rho_3=1\) on the entire
skew subclass. For a rank-three projector on \(\mathbb R^6\) whose
maximum-volume graph chart \(Z\) is skew, \(K=Z^T/r\) is skew for every
\(r>0\). The previously proved graph transfer gives

\[
\Psi_3(P+r^2(I-P))\ge\frac{r}{8360},
\qquad 0<r\le1.
\tag{21}
\]

The same bound applies to families of such charts that vary with \(r\).
No limiting nondegeneracy of the skew entries is required.

A generic rank-two matrix has additional coordinate parameters, including
nonzero diagonal entries. Signed permutations do not remove them.
The uniform finite three-polar problem outside this subclass remains open.
The present proof is supporting mathematics; no originality or sufficient
Cassette significance is inferred from its correctness.
