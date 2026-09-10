# Case C: a finite-polar witness along every generic rank-two ray

The [sign classification](rank_two_sign_consistent_inverse_pivot.md) reduces a real rank-two matrix with nonzero entries and nonzero two-by-two minors to three normalized sign cases. This note proves the remaining case C along a fixed dilated direction. Together with the [case A proof](rank_two_case_a_asymptotic_multisupport.md) and [case B proof](rank_two_generic_direction_asymptotic_case_b.md), it gives a norm bound independent of the direction, but a dilation threshold that may depend on it. It does not establish the uniform finite three-polar lemma.

## Normalization and choice of pivot

Let \(K\in\mathbb R^{3\times3}\) have rank two, with every entry and every two-by-two minor nonzero. Choose unit left and right kernel vectors \(g,h\), and put

\[
M=\operatorname{diag}(g)K\operatorname{diag}(h).
\tag{1}
\]

The kernel vectors have no zero coordinates. The rows and columns of \(M\) sum to zero. In case C, coordinate permutations and a global sign put \(M\) in the form

\[
M=\begin{pmatrix}
-a&-b&a+b\\
-c&d&c-d\\
a+c&b-d&d-a-b-c
\end{pmatrix},
\tag{2}
\]

where

\[
a,b,c,d>0,\qquad \max\{b,c\}<d<a+b+c.
\tag{3}
\]

Its admissible pivots form the matching \((1,3),(2,2),(3,1)\). Since both kernel vectors have unit norm, at least one matching pair \((i,j)\) satisfies \(|g_i|\ge|h_j|\). Relabel the positive matching entries to bring that pair to \((1,3)\). The sign pattern remains case C, so (2)--(3) still hold with relabeled parameters. Thus assume

\[
|g_1|\ge|h_3|>0.
\tag{4}
\]

The signs of \(g,h\) need not be positive. They will occur squared in every scalar sign test.

## Witness and all proper inverse pairings

For a positive \(\varepsilon\), set

\[
\alpha=(-1,\varepsilon,\varepsilon)^T,\qquad
\beta=e_3,\qquad
u_0=\operatorname{diag}(g)^{-1}\alpha,\qquad
n_0=\operatorname{diag}(h)^{-1}\beta.
\tag{5}
\]

Normalize them separately:

\[
u=u_0/\|u_0\|,\qquad
n=\frac{n_0}{2\|n_0\|}.
\tag{6}
\]

Then \(\|u\|=1\) and \(\|n\|=1/2\). For each row \(i\), the product \(M_{i3}\alpha_i\beta_3\) is strictly negative. Consequently \(K_{i3}u_i n_3<0\). The other two coordinates of \(n\) vanish.

Put \(D=ad+bc>0\). For a two-element row set \(E\) and a two-element column set \(J\) containing 3, the raw inverse pairing is

\[
u_{0,E}^TK_{EJ}^{-T}n_{0,J}
=\alpha_E^TM_{EJ}^{-T}\beta_J.
\tag{7}
\]

Direct inversion gives the following numerators; every entry is divided by \(D\):

\[
\begin{array}{c|cc}
&J=\{1,3\}&J=\{2,3\}\\\hline
E=\{1,2\}&-c-a\varepsilon&-d+b\varepsilon\\
E=\{1,3\}&-(a+c)+a\varepsilon&-(d-b)-b\varepsilon\\
E=\{2,3\}&-(a+2c)\varepsilon&(b-2d)\varepsilon
\end{array}.
\tag{8}
\]

Choose

\[
0<\varepsilon<\min\{1/2,d/b,(a+c)/a\}.
\tag{9}
\]

Every pairing in (8) is then strictly negative. Normalization in (6) multiplies each pairing by the same positive scalar, so its sign is unchanged. If \(3\notin J\), then \(n_J=0\), and no inverse sign argument is needed.

## Scalar, proper, and full constraints after dilation

The finite-polar constraint for \(tK\) is

\[
(n_J+tK_{EJ}^Tu_E)^T
(I+t^2K_{EJ}^TK_{EJ})^{-1}
(n_J+tK_{EJ}^Tu_E)\le\|u_E\|^2
\tag{10}
\]

for every equally sized \(E,J\subseteq[3]\).

For a singleton with \(j=3\), subtracting the right side after multiplying by the positive denominator gives exactly

\[
n_3^2+2tK_{i3}u_i n_3-u_i^2.
\tag{11}
\]

Its linear coefficient is strictly negative, so (11) is negative for all sufficiently large \(t\). For \(j\ne3\), its value is \(-u_i^2<0\).

For a proper two-by-two matrix \(B=K_{EJ}\), invertibility and a fixed-matrix expansion give

\[
(n_J+tB^Tu_E)^T(I+t^2B^TB)^{-1}(n_J+tB^Tu_E)
=\|u_E\|^2+\frac2t u_E^TB^{-T}n_J+O_K(t^{-2}).
\tag{12}
\]

If \(3\in J\), (8) makes the first correction strictly negative. If \(3\notin J\), the exact contraction

\[
t^2B(I+t^2B^TB)^{-1}B^T\preceq I
\tag{13}
\]

already proves (10).

For full support, a singular-value decomposition of \(K\) gives the limit

\[
\lim_{t\to\infty}
(n+tK^Tu)^T(I+t^2K^TK)^{-1}(n+tK^Tu)
=1-|g^Tu|^2+|h^Tn|^2.
\tag{14}
\]

As \(\varepsilon\downarrow0\), \(|g^Tu|\to|g_1|\), while \(|h^Tn|=|h_3|/2\). By (4), reducing \(\varepsilon\) in (9) further ensures

\[
|g^Tu|>\frac34|g_1|\ge\frac34|h_3|>|h^Tn|.
\tag{15}
\]

The full limit in (14) is therefore strictly below one. It follows that the full constraint also holds for all sufficiently large \(t\). There are finitely many constraints, so one finite threshold \(T(K)\) works for all of them.

If a matching pair has the strict inequality \(|g_i|>|h_j|\), one may instead normalize \(n\) to unit norm and choose \(\varepsilon\) small enough that \(|g^Tu|>|h_j|\). The same argument then gives both witness norms equal to one. The half-norm construction covers the balanced matching case as well.

## What the three cases establish

For every fixed real rank-two direction \(K\) with nonzero entries and nonzero two-by-two minors, there is a finite \(T(K)\) such that every \(tK\), \(t\ge T(K)\), has a finite-three-polar witness with

\[
\|u\|=1,\qquad\|n\|\ge1/2.
\tag{16}
\]

Cases A and B supply unit \(n\); case C supplies (6). Signed coordinate changes, coordinate permutations, and replacing \(K\) by \(-K\) preserve feasibility after the corresponding changes of signs in the witness.

The norm constant in (16) is common to all generic directions. The threshold is not. In particular, (16) gives no uniform control when a direction approaches a zero entry, a zero proper minor, or lower rank while its dilation grows. Those moving directions remain the next obstruction to the uniform finite lemma.
