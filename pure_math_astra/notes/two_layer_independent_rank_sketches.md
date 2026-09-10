# Two-layer independent rank sketches: exact covariance transport and a sharp product gap

Status: finite-dimensional theorem for independent unbiased *rank*-capped
random operators.  It is a sequential-risk result, not a byte, traffic, or
implementation theorem.  It supplies one operation-specific law of the kind
required by MATHS.md section 6.

Let

\[
 B\colon\mathbb F^q\to\mathbb F^n,
 \qquad A\colon\mathbb F^n\to\mathbb F^m,
\]

and let independent random operators \(\widehat A,\widehat B\) satisfy

\[
 \mathbb E\widehat A=A,
 \qquad \mathbb E\widehat B=B.
\]

Write \(\Delta_A=\widehat A-A\), \(\Delta_B=\widehat B-B\), and put

\[
 C_A=\mathbb E\Delta_A^*\Delta_A,
 \qquad
 \mathcal C_B[M]=\mathbb E\Delta_B^*M\Delta_B\quad(M\succeq0).
\tag{1}
\]

The matrix \(C_A\) is the full worst-query covariance certificate of the
first layer, not merely a scalar bound on it.

## Theorem: exact transport and an unavoidable interaction term

The sequential estimator \(\widehat A\widehat B\) is unbiased for \(AB\),
and its exact right second-moment error is

\[
\begin{aligned}
 C_{A\circ B}^{\rm seq}
 &:=\mathbb E(\widehat A\widehat B-AB)^*
                    (\widehat A\widehat B-AB)\\
 &=B^*C_A B+\mathcal C_B[A^*A+C_A]\\
 &=B^*C_A B+\mathcal C_B[A^*A]+\mathcal C_B[C_A].
\tag{2}
\end{aligned}
\]

Consequently, the usual two linearized layer terms omit the positive
semidefinite interaction

\[
 \mathcal C_B[C_A]\succeq0.
\tag{3}
\]

It vanishes if and only if

\[
 C_A^{1/2}\Delta_B=0\quad\hbox{almost surely}.
\tag{4}
\]

Thus an independent second-layer sketch avoids multiplying first-layer
noise only when all of its fluctuations lie in directions in which the
first-layer sketch is exact.  Independence and centering alone do not give
that condition.

### Proof

Independence gives

\[
 \mathbb E(\widehat A\widehat B)
 =\mathbb E\widehat A\,\mathbb E\widehat B=AB.
\]

Expand the error as

\[
 \widehat A\widehat B-AB
 =\Delta_A B+A\Delta_B+\Delta_A\Delta_B.
\tag{5}
\]

Every cross second moment between the three terms is zero: condition first
on the factor that occurs linearly and use its zero mean.  The three square
terms are, respectively,

\[
 B^*C_A B,
 \qquad
 \mathcal C_B[A^*A],
 \qquad
 \mathcal C_B[C_A].
\]

This proves (2).  Since the last term is the expectation of

\[
 (C_A^{1/2}\Delta_B)^*(C_A^{1/2}\Delta_B),
\]

it is zero precisely under (4).  \(\square\)

Equation (2) also has the recursive reading

\[
 \mathbb E\widehat A^*\widehat A=A^*A+C_A;
\]

the downstream sketch must therefore be analyzed in the inflated metric
\(A^*A+C_A\).  A scalar layer risk generally loses the information needed
for that analysis.

## Sharp rank-one product separation

The interaction law is not only an accounting correction.  A direct,
product-specific representation can have zero risk while a legal
independent layerwise rank sketch has a sharp positive trace risk under a
declared layer certificate.

Fix \(a,b>0\), \(v\ge ab\), and let

\[
 A=\begin{bmatrix}a&0\\0&b\end{bmatrix},
 \qquad
 B=e_1\colon\mathbb F\to\mathbb F^2.
\tag{6}
\]

Let \(\widehat A\) range over all random matrices with

\[
 \mathbb E\widehat A=A,
 \qquad \operatorname{rank}\widehat A\le1\quad\hbox{almost surely},
 \qquad C_A\preceq vI_2.
\tag{7}
\]

Take \(\widehat B=B\) deterministically.  Then every such sequential
execution obeys

\[
 \mathbb E\|\widehat A\widehat B-AB\|_2^2
 =(C_A)_{11}\ \ge\ \frac{a^2b^2}{v}.
\tag{8}
\]

The bound is attained by the rank-one law

\[
 \widehat A=
 \begin{cases}
   \dfrac{a}{p}e_1e_1^*,&\text{with probability }p,\\[4pt]
   \dfrac{b}{1-p}e_2e_2^*,&\text{with probability }1-p,
 \end{cases}
 \qquad
 p=\frac{v}{b^2+v}.
\tag{9}
\]

In contrast, \(AB=ae_1\) has rank one, so the direct product sketch
\(\widehat C=AB\) is deterministic and has zero covariance under the same
rank-one cap.

### Proof of the lower bound

Put

\[
 H=\mathbb E\widehat A^*\widehat A=A^*A+C_A.
\]

The rank-constrained second-moment theorem in
`rank_constrained_second_moments.md` gives

\[
 \operatorname{tr}(AH^{-1}A^*)\le1.
\tag{10}
\]

For completeness, its short necessity argument is enough here.  If
\(P_{\widehat A}\) projects onto the column range of \(\widehat A\), then

\[
 \begin{bmatrix}
 P_{\widehat A}&\widehat A\\
 \widehat A^*&\widehat A^*\widehat A
 \end{bmatrix}\succeq0.
\]

After expectation, the Schur complement gives
\(\mathbb EP_{\widehat A}\succeq AH^{-1}A^*\).  Its trace is at most one,
which proves (10).

Write

\[
 C_A=\begin{bmatrix}x&z\\\overline z&y\end{bmatrix}.
\]

Since \(C_A\preceq vI\), \(y\le v\).  Direct inversion of the two by two
matrix \(H\) gives

\[
 \operatorname{tr}(AH^{-1}A^*)
 \ge
 \frac{a^2}{a^2+x}+\frac{b^2}{b^2+y}
 \ge
 \frac{a^2}{a^2+x}+\frac{b^2}{b^2+v}.
\tag{11}
\]

Combining (10) and (11) gives \(x\ge a^2b^2/v\), which is (8).
For (9), direct calculation gives

\[
 C_A=\operatorname{Diag}\left(\frac{a^2b^2}{v},v\right)\preceq vI,
\]

where the final inequality is exactly \(v\ge ab\).  Its sequential error
on \(B=e_1\) equals the first diagonal entry, so equality holds.
\(\square\)

## What the separation means, and what it does not

Mathematically, a direct rank-capped product class is at least as expressive
as independent layerwise rank sketches: \(\widehat A\widehat B\) itself is
an unbiased direct product sketch, of rank at most
\(\min(\operatorname{rank}\widehat A,\operatorname{rank}\widehat B)\).
Thus a direct optimum can only improve the risk if it is allowed to use the
same random product law.  The example shows strict improvement when it may
instead use the deterministic low-rank product.

Operationally, that deterministic option is not free.  It replaces the
two-layer representation by a resident product-specific vector \(AB\), or
by an equivalent factorization and decoder.  A plan must charge its stored
product bytes, metadata, compilation work, selection observation, and read
traffic.  The theorem proves neither that this replacement saves bytes nor
that it is legal for a shared multi-trace schedule.

The useful sequential conclusion is narrower.  A scalar certificate
\(C_A\preceq vI\) cannot be inserted into a universal quadrature rule.  In
the sharp example, relaxing the *global* layer bound from \(v\) to a larger
value permits the rank-one law to move its error into the unexecuted second
direction, reducing the protected trace error as \(a^2b^2/v\).  Any
multi-step allocation theorem must therefore propagate the covariance matrix
through the actual downstream map, and must separately decide whether a
product-specific resident representation is admissible and worth its
resource cost.
