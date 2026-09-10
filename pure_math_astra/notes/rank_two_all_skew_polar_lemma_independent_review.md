# Independent exact review of the all-skew \(3\times3\) certificate

Status: the proposed certificate is correct for every real skew
\(3\times3\) matrix after the stated normal form. This verifies all scalar,
proper two-by-two, and full three-by-three finite polar conditions. No
claim is made beyond this skew family.

Normalize to

\[
K=\begin{pmatrix}0&c&-b\\-c&0&a\\b&-a&0\end{pmatrix},
\qquad a\ge b\ge c\ge0,
\]

and put

\[
\gamma=\sqrt{1+c^2},\quad \beta=\sqrt{1+b^2},\quad
s=c+\gamma,\quad z=b+\beta,\quad d=a-b.
\]

The raw vectors

\[
u_0=(1,-s,-z)^T,\qquad n_0=(1,-s,z)^T
\]

have the same squared norm \(1+s^2+z^2\). Thus dividing both by
\(\sqrt{1+s^2+z^2}\) turns the raw determinant gaps into the normalized
finite polar inequalities.

## Exact algebraic reconstruction

I recomputed each gap in the quotient polynomial ring

\[
\mathbb Q[a,b,c,s,z]/
(s^2-2cs-1,\ z^2-2bz-1).
\]

This is exact rational arithmetic. It proves the proposed two-by-two table
entry by entry:

\[
\begin{pmatrix}
0&
2a\gamma\beta&
2\gamma\{as(\gamma\beta-bc)+c(s\gamma+bz)\}\\
2\gamma\{2bz\gamma+a(b+z)\}&
4bz(1+b^2)&
2\beta\{az(\gamma\beta-bc)+b(z\beta+cs)\}\\
\gamma^2(z^2-s^2)+2bs\gamma z+2as\gamma(bs+z\gamma)&
\begin{aligned}
&4bzd^2+2z\{\gamma+(s+4)b^2+bcz\}d\\
&+b^2(s^2+z^2-2)+2bz\gamma(1+s)\\
&+2sb^3z+2b^2cz^2
\end{aligned}&
4asz(1+a^2)
\end{pmatrix}. \tag{R1}
\]

Rows and columns are \(12,13,23\). Each displayed expression is
nonnegative:

\[
\gamma\beta-bc>0,\qquad z\ge s\ge1,\qquad d\ge0.
\]

In particular, every summand in the long \(23|13\) entry is nonnegative.
This handles all nine proper square-submatrix conditions.

The nine scalar gaps are six exact zeros and the following three
nonnegative expressions:

\[
\Delta_{2|3}=2(as z+cs-bz),\qquad
\Delta_{3|1}=4bz,\qquad
\Delta_{3|2}=2(as z+bz-cs). \tag{R2}
\]

For the first expression in (R2),
\(as z-bz\ge bz(s-1)\ge0\). For the third,
\(bz\ge cs\), since \(b\ge c\) and \(z\ge s\). Hence every scalar
condition holds.

For the full support, the raw numerator before division by
\((1+a^2+b^2+c^2)(1+s^2+z^2)\) is exactly

\[
4z\bigl[(b+as)-c(a-bs)\bigr]
=4z\bigl[b+a(s-c)+bcs\bigr]\ge0. \tag{R3}
\]

It is strictly positive except at the zero matrix. Thus the full condition
also holds, including the all-zero endpoint.

The endpoint cases and large parameters require no continuity argument:
all inequalities are exact for \(a,b,c\) in the closed normal-form cone.

## Normal-form invariance

Signed coordinate permutations preserve the finite polar system because
they permute coordinate supports and conjugate all principal submatrices.
A certificate transforms with the same signed permutation.

A signed permutation can reorder the three absolute skew entries. Diagonal
sign conjugation preserves their sign product, while \(K\mapsto-K\) reverses
it. Together they put every real skew \(3\times3\) matrix into the displayed
normal form. The operation \(K\mapsto-K\) preserves feasibility: replace
\(u\) by \(-u\) and retain \(n\), so
\(n+(-K)^T(-u)=n+K^Tu\).

Therefore the certificate proves the finite three-polar lemma with
\(\|n\|=1\) for all real skew \(3\times3\) matrices.

The proof table is independent of the separate scalar-interval endpoint
description. If both are retained, their endpoint parameter names should be
made consistent. The determinant proof itself does not depend on that
choice.
