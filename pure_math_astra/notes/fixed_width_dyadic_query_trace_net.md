# Fixed-width dyadic query net for the biased rounded trace lower

Status: proved finite-alphabet replacement for the trace-test queries in the
four-coordinate equicorrelation case. The test queries are dyadic but not
unit vectors. This note does not price storage of the finite alphabet or
prove native arithmetic.

## Parameters

Let

\[
 \eta=\frac1{256},\qquad
 G=H_\eta=\mathbf1\mathbf1^T+\eta I_4,\qquad
 C=\frac{27}{16}\eta,
 \qquad S=(G+CI)^{1/2}.
\tag{1}
\]

The eigenvalues of \(G+CI\) are \(4+43/4096\) and \(43/4096\), the latter
with multiplicity three. Hence

\[
 \kappa(S)^2=\frac{16427}{43}<400,
 \qquad \kappa(S)<20.
\tag{2}
\]

Fix \(\delta=1/20\), \(B=11\), and \(h=2^{-B}\).

## Construction

Choose a Euclidean \(\delta/2\)-net \(Z\) of the unit sphere in
\(\mathbb R^4\), with

\[
 |Z|\le\left(1+\frac4\delta\right)^4=81^4.
\tag{3}
\]

For every \(z\in Z\), set

\[
 u_z=\frac{S^{-1}z}{\|S^{-1}z\|_2},
\tag{4}
\]

and round each coordinate of \(u_z\) to the nearest multiple of \(h\), with
one fixed tie rule. Denote the result by

\[
 x_z=\frac{a_z}{2^{11}}.
\tag{5}
\]

Each coordinate of \(a_z\) lies in \([-2048,2048]\). Thus every test query
uses four signed 13-bit numerators over the common dyadic denominator
\(2^{11}\). Rounding gives

\[
 \|x_z-u_z\|_2\le\frac{\sqrt4}{2\cdot2^{11}}=\frac1{2048}<1,
\tag{6}
\]

so every \(x_z\) is nonzero.

Define its spectral direction

\[
 \widehat z_x=\frac{Sx_z}{\|Sx_z\|_2}.
\tag{7}
\]

For nonzero vectors \(v,w\),

\[
 \left\|\frac v{\|v\|_2}-\frac w{\|w\|_2}\right\|_2
 \le\frac{2\|v-w\|_2}{\|w\|_2}.
\tag{8}
\]

Applying (8) to \(v=Sx_z\), \(w=Su_z\), then using (2) and (6), gives

\[
 \|\widehat z_x-z\|_2
 \le2\kappa(S)\|x_z-u_z\|_2
 <\frac{40}{2048}
 =\frac5{256}<\frac{\delta}{2}.
\tag{9}
\]

Every point of the sphere is within \(\delta/2\) of a member of \(Z\), and
that member's dyadic spectral direction is within \(\delta/2\) of it.
Therefore the finite set of directions \(\{\widehat z_x:z\in Z\}\) is a
\(\delta\)-net of the unit sphere. Duplicates after rounding only reduce the
alphabet size and do not affect this conclusion.

## Nonunit queries require no decoder homogeneity

Suppose the protocol contract, on every supplied query \(x\), is

\[
 \mathbb E\|F-Wx\|_2^2\le C\|x\|_2^2,
 \qquad
 \|\mathbb EF-Wx\|_2\le b\|x\|_2.
\tag{10}
\]

For a fixed nonzero dyadic test query \(x=x_z\), define only inside the
proof

\[
 \bar F_S(A_S)=\frac{F_S(A_S,x)}{\|x\|_2}.
\tag{11}
\]

This is a Borel function of the same observed columns. Dividing (10) by
\(\|x\|_2^2\) makes \(\bar F\) satisfy the unit-query MSE and bias bounds
relative to \(W(x/\|x\|_2)\). No assertion about the decoder at the
separately supplied unit vector \(x/\|x\|_2\) is made or needed.

The trace identity also survives exactly. With
\(\widehat x=x/\|x\|_2\),

\[
 \frac{A\widehat x}
 {\sqrt{C+\widehat x^TG\widehat x}}
 =\frac{Ax}{\sqrt{C\|x\|_2^2+x^TGx}}
 =AS^{-1}\widehat z_x.
\tag{12}
\]

Thus the finite-net duality in the biased rounded trace lower applies to
the dyadic alphabet, with its net coefficient
\(1-\delta^2/2\) unchanged. The concentration event is formed at the
actual fixed queries \(x_z\), and its leakage ratio is unchanged by the
positive scalar in (11).

## Union-bound consequence

The only union-bound change is the net count:

\[
 \beta_{\rm dyadic}
 \le N2^{3q/2}\left(1+\frac4\delta\right)^q
 \exp\left(-\frac{(p-q)\epsilon^2}{4}\right).
\tag{13}
\]

For this four-coordinate statement and \(\delta=1/20\), replace the
earlier term \(4\log41\) by \(4\log81\) in the sufficient
output-dimension condition.

For \(G=H_\eta^{\oplus m}\), the condition number remains below \(20\), but
the fixed \(B=11\) construction does not by itself give a net in
\(\mathbb R^{4m}\).  The rounding error is then
\(\sqrt m/2048\).  The same proof works after choosing

\[
 2^B>1600\sqrt m,
\tag{14}
\]

because \(2\kappa(S)\sqrt{4m}/(2\cdot2^B)<\delta/2\).  It then gives the
net term \(4m\log81\), with signed \(B+2\)-bit coordinate numerators.
Thus 13-bit coordinates are justified here only for \(m=1\). The finite
dyadic alphabet depends only on \(G,C,\delta,B\); it is fixed before the
source, source state, support law, and decoder are chosen.

The result supplies a compatible fixed-width mathematical query format. It
does not by itself declare the alphabet's resident representation, an input
API, an output representation, or a physical execution path.
