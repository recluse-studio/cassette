# Critical-scale 2x2 polar algebra: exact reduction and remaining lemma

Status: the finite algebra below is exact. Its formerly open scalar lemma
is now proved in `critical_scale_2x2_polar_lemma_proof.md`, with independent
reconstruction in `critical_scale_2x2_scalar_n_equals_u_review.md`. The
historical reduction, failed endpoint shortcut, and former open questions
below are retained as the record that led to that proof. Numerical checks
are explicitly labelled as such.

For \(K\in\mathbb R^{2\times2}\), consider nonzero \(u\) and \(n\) subject to

\[
 |n_j+u_mK_{mj}|\le |u_m|\sqrt{1+K_{mj}^2}\quad(m,j=1,2),
\tag{1}
\]

and

\[
 (n+K^Tu)^T(I+K^TK)^{-1}(n+K^Tu)\le\|u\|_2^2.
\tag{2}
\]

The desired statement is the existence of a universal \(c>0\) with
\(\|n\|\ge c\|u\|\), perhaps with \(c=1\).

## Exact simplifications

The coordinate sign changes \(u\mapsto D_Hu\), \(n\mapsto D_Ln\),
\(K\mapsto D_HKD_L\), for diagonal sign matrices, preserve (1), (2), and
both norms.  Choose signs so the two diagonal entries of the transformed
matrix are nonpositive.  Write it as

\[
 K=\begin{pmatrix}a&b\\c&d\end{pmatrix},\qquad a,d\le0.
\tag{3}
\]

There is then a useful norm-preserving candidate family,

\[
 u=n=(1,x)^T.
\tag{4}
\]

The two diagonal inequalities in (1) hold automatically.  The remaining
two are exactly

\[
 |x+b|\le\sqrt{1+b^2},\qquad
 |1+cx|\le |x|\sqrt{1+c^2}.
\tag{5}
\]

The first restricts \(x\) to

\[
 I_b=[-b-\sqrt{1+b^2},\,-b+\sqrt{1+b^2}],
\tag{6}
\]

whose endpoints have product \(-1\).  Squaring the second gives

\[
 x^2-2cx-1\ge0.
\tag{7}
\]

The admissible set \(I_b\cap\{x:(7)\}\) is nonempty: one of the positive
endpoint products or the negative endpoint products is at least one.  Thus
the coordinatewise part alone always admits a pair with \(\|n\|=\|u\|\).

For this family, the remaining ellipsoidal condition is the one-variable
inequality

\[
 F_K(x):=
 \frac{((I+K^T)(1,x)^T)^T(I+K^TK)^{-1}
              ((I+K^T)(1,x)^T)}{1+x^2}\le1.
\tag{8}
\]

Accordingly, the following finite lemma is sufficient for the strong
conjecture:

> For every real \(K\) with nonpositive diagonal, the nonempty set in
> (6)--(7) contains an \(x\) with \(F_K(x)\le1\).

This reduction is sharper than the tempting choice \(n=-K^Tu\).  That
choice makes (2) trivial, but its four coordinate conditions require a
single ratio \(|u_2/u_1|\) to satisfy conflicting bounds from different
columns, which need not happen.

## What has and has not been established

The sign reduction and equations (5)--(8) are direct substitutions, so they
are proved.  The finite lemma concerns only the special family \(n=u\);
it is sufficient for \(c=1\), but is not equivalent to unrestricted
feasibility.  It would be invalid to infer it only from the fact that
\(F_K\) has some direction with value at most one: that direction need not
lie in the coordinate-feasible set.

**Numerical evidence only.** A dense angular search over random matrices
covering singular values from roughly \(10^{-8}\) to \(10^8\), together with
structured diagonal, anti-diagonal, rank-one, and mixed-sign cases, found
feasible pairs with \(\|n\|\ge\|u\|\).  This supports \(c=1\), but cannot
prove the finite lemma or rule out a narrow counterexample.

An exact resolution can now concentrate on the rational quadratic in (8)
over the two explicit interval rays in (6)--(7).  No asymptotic passage from
the original Gram problem is used in this note.

## Endpoint failure and the remaining quadratic lemma

Writing \(K=\bigl(\begin{smallmatrix}a&b\\c&d\end{smallmatrix}\bigr)\),
direct expansion gives

\[
 \det(I+K^TK)(1+x^2)(F_K(x)-1)=A+2Bx+Cx^2,
\tag{9}
\]

where

\[
 \begin{aligned}
 A&=2a(1+d^2)+b^2-c^2-2bcd,\\
 C&=2d(1+a^2)+c^2-b^2-2abc,\\
 B&=(b+c)(1-ad+bc)+(a-d)(c-b).
 \end{aligned}
\tag{10}
\]

An endpoint proof is false.  For example, the rational matrix

\[
 K=\begin{pmatrix}-1&-6\\-136&-19\end{pmatrix}
\tag{11}
\]

has feasible interval

\[
 [-136+\sqrt{18497},\ 6+\sqrt{37}].
\tag{12}
\]

Both endpoint values of the numerator in (9) are positive.  Its exact
coefficients are

\[
 A=11824,\qquad B=-115656,\qquad C=20016,
\tag{13}
\]

so its vertex \(-B/C\) lies in the interval and has negative value.  Thus
the finite lemma requires an interior quadratic argument.

The remaining exact target is: on the feasible interval, either an endpoint
has \(A+2Bx+Cx^2\le0\), or \(C>0\), the vertex \(-B/C\) lies in the interval,
and \(B^2\ge AC\).  Proving this dichotomy proves the sufficient \(n=u\)
lemma.  The displayed rational example verifies why neither endpoint signs
nor compactness alone can replace that step.

## Determinant identity and the exact endpoint calculation

Put \(M=I+K^TK\) and

\[
 Q=(I+K)M^{-1}(I+K^T)-I.
\tag{14}
\]

The numerator in (9) is \(\det(M)(1,x)Q(1,x)^T\). Its coefficient
matrix is therefore \(\det(M)Q\), and

\[
 AC-B^2=\det(M)\,[4ad-(b+c)^2].
\tag{15}
\]

Here is a direct proof. Sylvester's determinant identity gives

\[
 \det Q
 =\frac{\det\{M-(I+K^T)(I+K)\}}{\det M}
 =\frac{\det(K+K^T)}{\det M}
 =\frac{4ad-(b+c)^2}{\det M}.
\tag{16}
\]

The first equality has no sign error in dimension two: the intermediate
matrix is \(-(K+K^T)\), whose determinant is unchanged. Multiplying by
\(\det(M)^2\) proves (15). If

\[
 4ad\ge(b+c)^2,
\tag{17}
\]

then \(K+K^T\preceq0\), because \(a,d\le0\). Thus

\[
 (I+K)^T(I+K)\preceq M.
\]

After congruence by \(M^{-1/2}\), this implies

\[
 (I+K)M^{-1}(I+K)^T\preceq I,
\]

so \(Q\preceq0\) and every coordinate-feasible \(x\) satisfies (8).
The only unresolved case is consequently

\[
 4ad<(b+c)^2,
\tag{18}
\]

where (15) makes the quadratic in (9) indefinite.

For completeness, both claimed positive endpoint signs in the rational
example are exact. At

\[
 L=\sqrt{18497}-136,
\]

the relation \(L^2+272L-1=0\) gives

\[
 N(L)=31840-5{,}675{,}664L
 =31840-\frac{5{,}675{,}664}{\sqrt{18497}+136}>0.
\tag{19}
\]

The last inequality is equivalent to

\[
 \sqrt{18497}>\frac{84089}{1990},
\]

and follows on squaring positive quantities, since

\[
 18497>\frac{7070959921}{3960100}.
\]

At \(U=6+\sqrt{37}\), direct substitution gives

\[
 N(U)=85120+8880\sqrt{37}>0.
\tag{20}
\]

The vertex is \(x_*=115656/20016=4819/834\). It lies strictly between
\(L\) and \(U\): \(0<L<1<x_*<6<U\). Finally,

\[
 N(x_*)=\frac{AC-B^2}{C}
 =-\frac{13139641152}{20016}<0.
\tag{21}
\]

Thus (11) is an exact interior-witness example, rather than numerical
endpoint evidence.

The coordinate-feasible set can also be written without an intersection.
If \(b+c>0\), it is the negative interval

\[
 [-b-\sqrt{1+b^2},\ c-\sqrt{1+c^2}],
\tag{22}
\]

and if \(b+c<0\), it is the positive interval

\[
 [c+\sqrt{1+c^2},\ -b+\sqrt{1+b^2}].
\tag{23}
\]

Indeed, the endpoints of (6) are the roots of
\(x^2+2bx-1\), and the boundary roots in (7) are those of
\(x^2-2cx-1\). Their ordering follows after writing
\(b=\sinh\beta\), \(c=\sinh\gamma\): the roots are
\(-e^\beta,e^{-\beta}\) and \(e^\gamma,-e^{-\gamma}\), respectively.
If \(b+c=0\), their intersections consist of the two common endpoints.
This exceptional case belongs to (17), since \(ad\ge0=(b+c)^2/4\), so it
requires no indefinite-cone argument.
