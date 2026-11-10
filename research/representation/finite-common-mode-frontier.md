# Necessary finite-common-mode frontier for unrestricted two-sparse decoding

**Status.** This note gives a dual lower bound for a stronger comparator than
the signed-sum decoder.  It does not prove that the displayed lower bound is
attained by an unrestricted decoder.  In particular, it does not replace the
proved signed-sum constant or establish a new representation advantage.

## Contract

Let

\[
 G_a=I_4+a\mathbf1\mathbf1^T,\qquad a\ge1,
 \tag{1}
\]

and let \(M_a(x)\) be the least \(\mathbb E Y^TG_aY\) over all laws with
\(\mathbb EY=x\) and \(\|Y\|_0\le2\).  Unlike the signed-sum decoder, this
class permits \(\mathbf1^TY\) to fluctuate.  A bound

\[
 M_a(x)-x^TG_ax\le c\|x\|_2^2\qquad\hbox{for every }x
 \tag{2}
\]

would dominate the signed-sum construction when applied to a source whose
Gram is \(\eta G_a\): the resulting matrix-product risk would be at most
\(\eta c\|x\|_2^2\).

The atomic dual gives a necessary and sufficient test for a proposed \(c\):

\[
 \lambda^T(G_a+cI_4)^{-1}\lambda
 \le\max_{|S|\le2}\lambda_S^T(G_a)_{SS}^{-1}\lambda_S
 \quad\hbox{for every }\lambda\in\mathbb R^4.
 \tag{3}
\]

The right side contains pairs; singleton supports are already included by a
pair with a zero selected coefficient.  Equation (3) follows by taking
Fenchel conjugates of the squared Gram norm on the union of two-coordinate
subspaces.  It is useful here because one violating dual vector disproves
(2).

## An explicit necessary bound

Set

\[
 b(a)=
 \frac{-(a^2-a-1)+
 \sqrt{(a^2-a-1)^2+6a(1+2a)(a+1)^2}}{(a+1)^2},
 \qquad c_{\rm lb}(a)=b(a)-1.
 \tag{4}
\]

Then every \(c\) satisfying (2) obeys

\[
 c\ge c_{\rm lb}(a).
 \tag{5}
\]

### Proof

Take

\[
 \lambda=(1,1,1,v),\qquad v=\frac{a-1}{a+1}.
 \tag{6}
\]

For a pair \(ij\),

\[
 \lambda_{\{i,j\}}^T(G_a)_{\{i,j\}}^{-1}\lambda_{\{i,j\}}
 =\frac{\lambda_i^2+\lambda_j^2+a(\lambda_i-\lambda_j)^2}{1+2a}.
 \tag{7}
\]

At (6), the positive-positive and positive-\(v\) pairs agree, so the right
side of (3) is

\[
 \frac{2}{1+2a}.
 \tag{8}
\]

Writing \(b=1+c\), direct inversion of \(bI_4+a\mathbf1\mathbf1^T\) gives

\[
 \lambda^T(G_a+cI_4)^{-1}\lambda
 =
 \frac{4\left[b(a^2+a+1)+3a\right]}
 {(a+1)^2b(b+4a)}.
 \tag{9}
\]

The equality of (8) and (9) is the positive-root equation

\[
 (a+1)^2b^2+2(a^2-a-1)b-6a(1+2a)=0.
 \tag{10}
\]

Its positive root is exactly (4).  For \(b<b(a)\), (9) exceeds (8), which
violates (3).  Fenchel duality then supplies a query on which every
unbiased two-sparse decoder has risk greater than \(c\|x\|_2^2\).
\(\square\)

The witness is all-positive for \(a>1\).  Any reduction that assumes dual
extrema have opposite signs misses this obstruction.

## Values and boundary

\[
 \begin{array}{c|cccc}
 a&1&2&10&100\\ \hline
 c_{\rm lb}(a)&1.3860009363&1.4732674110&1.5741815440&1.6022841772
 \end{array}
 \tag{11}
\]

Moreover,

\[
 \lim_{a\to\infty}c_{\rm lb}(a)=\sqrt{13}-2.
 \tag{12}
\]

The limit agrees with the proved signed-sum four-coordinate constant.  For
every finite \(a\), the lower-bound expression in (4) is below that limit.
It therefore does not certify that the signed-sum decoder is the best
unrestricted comparator at finite common-mode strength.

The gap is exact in only one direction.  Equation (5) says that a stronger
unrestricted decoder cannot have a universal coefficient below
\(c_{\rm lb}(a)\).  It does **not** construct a decoder with that
coefficient, prove the all-dual inequality (3) at equality, or establish a
strict performance separation from the signed-sum decoder.  Any such claim
still needs an all-\(\lambda\) sufficiency proof and a finite arithmetic,
page, byte, and RAM account.
