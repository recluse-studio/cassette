# Independent review: generic rank-two rays have a half-norm finite-polar witness

Verdict: the Case C construction in
`rank_two_case_c_asymptotic_pivot.md` is correct.  Together with the
already proved Case A and Case B constructions, it proves the stated
fixed-ray result.  The threshold cannot be read as uniform over varying
directions.

## 1. Case C normalization and matching relabeling

Let \(K\in\mathbb R^{3\times3}\) have rank two, no zero entry, and no
zero two-by-two minor.  For unit left and right kernels \(g,h\), set

\[
 M=D_gKD_h.
\]

Then \(M\mathbf1=\mathbf1^TM=0\), and all coordinates of \(g,h\) are
nonzero.  In the Case C sign stratum, independent row and column
permutations and, if needed, a global sign give

\[
 M=
 \begin{pmatrix}
 -a&-b&a+b\\
 -c&d&c-d\\
 a+c&b-d&d-a-b-c
 \end{pmatrix},
 \qquad a,b,c>0,\quad \max\{b,c\}<d<a+b+c.
 \tag{1}
\]

The three positive entries form the matching

\[
 (1,3),\quad(2,2),\quad(3,1). \tag{2}
\]

At least one pair \((i,j)\) in (2) obeys \(|g_i|\ge |h_j|\): otherwise
summing the three strict inequalities after squaring contradicts
\(\|g\|_2^2=\|h\|_2^2=1\).  Relabel that matched row to row one and its
matched column to column three; place the remaining matching edges at
\((2,2)\) and \((3,1)\).  All unmatched entries are negative, so the
result still has exactly the sign table (1); the zero row and column sums
then give the parameter inequalities in (1).  Signed row and column
permutations preserve every finite-polar inequality after the corresponding
signed permutation of \(u\) and \(n\).  Thus it is legitimate to assume

\[
 |g_1|\ge |h_3|. \tag{3}
\]

## 2. Reconstruction of the proper-support table

Take raw transformed coordinates

\[
 \alpha=(-1,\varepsilon,\varepsilon)^T,\qquad
 \beta=e_3,\qquad
 u_0=D_g^{-1}\alpha,\qquad n_0=D_h^{-1}\beta.
 \tag{4}
\]

For two-element \(E,J\), diagonal factors cancel exactly:

\[
 u_{0,E}^TK_{E,J}^{-T}n_{0,J}
 =\alpha_E^TM_{E,J}^{-T}\beta_J. \tag{5}
\]

Put \(D=ad+bc\).  When \(3\in J\), direct inversions give

\[
 D\,\alpha_E^TM_{E,J}^{-T}\beta_J=
 \begin{array}{c|cc}
 &J=13&J=23\\ \hline
 E=12&-c-a\varepsilon&-d+b\varepsilon\\
 E=13&-(a+c)+a\varepsilon&-(d-b)-b\varepsilon\\
 E=23&-(a+2c)\varepsilon&(b-2d)\varepsilon.
 \end{array}
 \tag{6}
\]

For example, with \(E=12,J=13\),

\[
 M_{12,13}^{-1}
 ={1\over D}
 \begin{pmatrix}c-d&-(a+b)\\c&-a\end{pmatrix},
\]

so the lower row against \((-1,\varepsilon)\) gives
\((-c-a\varepsilon)/D\).  The other five entries follow from the same
two-by-two inverse formula.  This independently verifies the table.

If

\[
 0<\varepsilon<\min\{1/2,d/b,(a+c)/a\}, \tag{7}
\]

each entry in (6) is strictly negative: use \(d>b\) for the fourth and
sixth entries.  If \(3\notin J\), then \(n_{0,J}=0\).

## 3. Every support size after dilation

Normalize

\[
 u={u_0\over\|u_0\|_2},\qquad
 n={n_0\over2\|n_0\|_2}.
 \tag{8}
\]

Thus \(\|u\|_2=1\) and \(\|n\|_2=1/2\).  Positive normalization
preserves all strict cross-term signs.

For scalar supports with \(j=3\), multiplication by the positive
denominator shows that the polar gap is exactly

\[
 n_3^2+2tK_{i3}u_in_3-u_i^2. \tag{9}
\]

Its linear coefficient is negative because

\[
 K_{i3}u_{0,i}n_{0,3}
 ={M_{i3}\alpha_i\over g_i^2h_3^2}<0.
 \tag{10}
\]

For \(j\ne3\), \(n_j=0\), and the multiplied gap is \(-u_i^2<0\).

For a proper invertible block \(B=K_{E,J}\), expansion gives

\[
 (n_J+tB^Tu_E)^T(I+t^2B^TB)^{-1}(n_J+tB^Tu_E)
 =\|u_E\|_2^2+{2\over t}u_E^TB^{-T}n_J+O(t^{-2}). \tag{11}
\]

When \(3\in J\), (6) makes the first correction negative.  When
\(3\notin J\), \(n_J=0\), and

\[
 t^2B(I+t^2B^TB)^{-1}B^T\preceq I \tag{12}
\]

proves the constraint directly.  These two arguments cover all nine proper
blocks.

For full support, decompose relative to the unit kernel directions.  The
singular-value expansion is

\[
 \lim_{t\to\infty}
 (n+tK^Tu)^T(I+t^2K^TK)^{-1}(n+tK^Tu)
 =1-|g^Tu|^2+|h^Tn|^2. \tag{13}
\]

As \(\varepsilon\downarrow0\), \(u\to-\operatorname{sign}(g_1)e_1\),
so \(|g^Tu|\to|g_1|\).  Meanwhile (8) gives

\[
 |h^Tn|={|h_3|\over2}. \tag{14}
\]

Choose \(\varepsilon\) still smaller, if necessary, so that

\[
 |g^Tu|>{3\over4}|g_1|\ge {3\over4}|h_3|>{|h_3|\over2}.
 \tag{15}
\]

The limit in (13) is then strictly less than one.  Scalar, proper, and full
constraints are all strict for sufficiently large \(t\); their finite
number yields one \(T(K)<\infty\).

## 4. Synthesis and quantifiers

Case A has a strictly negative first correction at every nonempty support
with unit \(u,n\).  Case B has strictly negative first corrections on its
six scalar constraints with \(j=2,3\) and on all proper supports; its
\(j=1\) scalar column
has an exact negative \(O(t^{-2})\) gap, and its full-support inequality has
a strict limiting gap.  It again uses unit \(u,n\).
The sign classification has only Cases A, B, and C, up to the isometries
above and \(K\mapsto-K\).  Therefore:

For every fixed real rank-two \(3\times3\) matrix \(K\) with no zero
entry or two-by-two minor, there are \(T(K)<\infty\) and witnesses
\(u,n\) such that every \(t\ge T(K)\) satisfies the finite-polar
constraints for \(tK\), with

\[
 \|u\|_2=1,\qquad \|n\|_2\ge\frac12.
 \tag{16}
\]

The witness and the threshold may depend on \(K\).  Statement (16) does
not imply a common threshold along a sequence \(K_r\) whose entries or
proper minors tend to zero, whose rank drops, or whose normalized direction
otherwise moves.  It consequently does not prove the uniform finite
three-polar lemma.
