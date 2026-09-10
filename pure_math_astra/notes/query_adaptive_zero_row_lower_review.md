# Uniform lower bound for a rank-two plane with a zero coordinate row

Status: independent verification of an exact real polar argument.  It
concerns the query-adaptive two-sparse value only.

Let \(P=EE^T\) be a rank-two orthogonal projector on \(\mathbb R^4\), where
\(E\in\mathbb R^{4\times2}\) has orthonormal columns.  Suppose the fourth
row of \(E\) is zero.  For

\[
 G_r=P+r^2(I-P),\qquad0<r\leq1,
\tag{1}
\]

the exact polar lower bound is

\[
 \Psi_2(G_r)\geq v_r:={\sqrt{9r^4+16r^2}-3r^2\over8}
 \geq {r\over4}.
\tag{2}
\]

## Row-line choice

The at most three nonzero rows \(E_i\in\mathbb R^2\) determine unoriented
lines in \(\mathbb RP^1\), a circle of length \(\pi\).  One gap between
these at most three lines has length at least \(\pi/3\).  Choose a unit
vector \(u\in\mathbb R^2\) at the midpoint of that gap.  Then

\[
 { |E_i u|^2\over P_{ii}}\leq\cos^2(\pi/6)={3\over4}
 \quad\text{for every nonzero row }E_i.
\tag{3}
\]

The inequality is vacuous for another zero row.

## Polar witness

Set

\[
 z=Eu+{r\over2}e_4.
\tag{4}
\]

For a two-coordinate set \(S\) that omits coordinate four, write
\(B=E_S\).  Its principal Gram block is

\[
 (G_r)_{SS}=r^2I+(1-r^2)BB^T.
\tag{5}
\]

Every nonzero eigenvalue of

\[
 B^T(r^2I+(1-r^2)BB^T)^{-1}B
\tag{6}
\]

has the form

\[
 {\sigma^2\over r^2+(1-r^2)\sigma^2}\leq1,
\tag{7}
\]

because \(\sigma^2\leq1\): \(B\) is a row submatrix of an isometry.
This proves the polar constraint for all such \(S\), including singular
principal blocks of \(P\).

For \(S=\{i,4\}\), the principal block is diagonal because \(P_{i4}=0\).
Thus (3) gives

\[
 z_S^T(G_r)_{SS}^{-1}z_S
 ={ |E_i u|^2\over r^2+(1-r^2)P_{ii}}+{1\over4}
 \leq {3\over4}+{1\over4}=1.
\tag{8}
\]

Hence \(z\) is a legal real polar vector.

The two summands in (4) lie respectively in \(\operatorname{range}P\) and
\(\ker P\), so for any \(v\geq0\),

\[
 z^T(G_r+vI)^{-1}z
 ={1\over1+v}+{r^2\over4(r^2+v)}.
\tag{9}
\]

The positive solution of the equation that sets (9) equal to one is

\[
 v_r={\sqrt{9r^4+16r^2}-3r^2\over8}.
\tag{10}
\]

For every \(v<v_r\), the quadratic form (9) is strictly greater than one,
so atomic polarity gives \(\Psi_2(G_r)\geq v\).  Taking
\(v\uparrow v_r\) gives the first inequality in (2).  The bound
\(v_r\geq r/4\) follows after moving \(3r^2\) to the other side and
squaring: it is exactly \(r\leq1\).  This is sharp for the displayed
witness as \(r\downarrow0\), since \(v_r/r\to1/2\).

## Exact tube transfer

If \(P_0\) has a zero coordinate row and
\(\|P-P_0\|_{\rm op}\leq Kr\), then

\[
 \Psi_2(P+r^2(I-P))
 \geq {r\over4(1+K)^2}.
\tag{11}
\]

Indeed, the square-root comparison in
`query_adaptive_exceptional_strata_tube.md` gives
\(G_r(P_0)\preceq(1+K)^2G_r(P)\), and the exact-mean infimum preserves this
Loewner comparison.

This result covers nonexceptional zero-row planes as well as the
zero-coordinate degenerations of the exceptional strata.
