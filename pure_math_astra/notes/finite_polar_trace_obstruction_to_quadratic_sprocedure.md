# Trace obstruction to a quadratic S-procedure for the finite polar lemma

Status: proved limitation of a proof method.  It neither disproves a
rank-one polar witness nor supplies one.

Let \(S_E\) denote coordinate restriction to \(E\), let
\(A=K_{E,J}\), and set

\[
 R=(I+A^TA)^{-1}. \tag{1}
\]

The finite polar inequality is equivalent to \(z^TQ_{EJ}z\leq0\), for
\(z=(u,n)\), with

\[
 Q_{EJ}=
 \begin{pmatrix}
 S_E^T[-(I+AA^T)^{-1}]S_E&S_E^TAR S_J\\
 S_J^TRA^TS_E&S_J^TRS_J
 \end{pmatrix}. \tag{2}
\]

The empty-set constraint has \(Q_{\varnothing\varnothing}=0\).

## 1. Exact expansion and trace identity

Expanding the left side of the polar inequality and moving
\(\|u_E\|^2\) to the left gives the local upper-left block

\[
 ARA^T-I=-(I+AA^T)^{-1}, \tag{3}
\]

which proves (2).  The nonzero eigenvalues of \(AA^T\) and \(A^TA\)
are the same, including multiplicities; here both matrices are square of
the same order.  Hence

\[
 \operatorname{tr}Q_{EJ}
 =-\operatorname{tr}(I+AA^T)^{-1}
   +\operatorname{tr}(I+A^TA)^{-1}=0. \tag{4}
\]

The off-diagonal blocks do not affect this identity.  In particular, it is
valid for singular and zero submatrices, because each selected
submatrix in the finite system is square.

## 2. No homogeneous nonnegative quadratic-multiplier proof below one

To derive the homogeneous conclusion

\[
 \|n\|_2^2\leq\rho^2\|u\|_2^2 \tag{5}
\]

from the inequalities \(z^TQ_{EJ}z\leq0\) by the usual nonnegative
quadratic S-procedure, one would need nonnegative multipliers
\(\lambda_{EJ}\) such that

\[
 \sum_{E,J}\lambda_{EJ}Q_{EJ}-D_\rho\succeq0,\qquad
 D_\rho=\operatorname{diag}(-\rho^2I_k,I_k). \tag{6}
\]

Indeed, (6) implies \(z^TD_\rho z\leq\sum\lambda_{EJ}z^TQ_{EJ}z\leq0\).
But (4) makes the trace of the left side of (6)

\[
 -\operatorname{tr}D_\rho=-k(1-\rho^2). \tag{7}
\]

It is negative for \(\rho<1\), whereas a positive semidefinite matrix has
nonnegative trace.  Thus this certificate cannot prove any uniform upper
bound strictly below one.  At \(\rho=1\), its trace is zero, so positive
semidefiniteness would force equality in (6); that exceptional possibility
does not produce a strict disproof of \(\rho=1\).

## 3. The basic lifted SDP has the same blind spot

Drop the rank-one constraint in \(X=zz^T\) and consider the standard
relaxation

\[
 X=\begin{pmatrix}U&C\\C^T&N\end{pmatrix}\succeq0,\qquad
 \operatorname{tr}U=1,\qquad
 \operatorname{tr}(Q_{EJ}X)\leq0, \tag{8}
\]

with objective \(\operatorname{tr}N\).  The isotropic moment

\[
 X_0={1\over k}I_{2k} \tag{9}
\]

satisfies \(\operatorname{tr}U=\operatorname{tr}N=1\), and (4) gives
\(\operatorname{tr}(Q_{EJ}X_0)=0\) for every finite polar constraint.
Consequently this relaxation always has value at least one.  It cannot
certify that every rank-one feasible pair with \(\|u\|=1\) has
\(\|n\|<1\).

## 4. A strict-sign scalar-polar integrality obstruction

The rank-one failure persists even if every form has a strictly negative
upper block and a strictly positive lower block, exactly as in a nonzero
scalar polar constraint.  Fix \(B>0\), and impose

\[
 n^2-u^2+2Bun\leq0,
 \qquad n^2-u^2-2Bun\leq0. \tag{10}
\]

Their matrices are

\[
 \begin{pmatrix}-1&B\\B&1\end{pmatrix},
 \qquad
 \begin{pmatrix}-1&-B\\-B&1\end{pmatrix}. \tag{11}
\]

They have trace zero, negative upper block, and positive lower block.  For
\(u\ne0\), put \(t=|n/u|\).  The two inequalities in (10) imply

\[
 t^2+2Bt-1\leq0,
 \qquad
 t\leq\sqrt{1+B^2}-B. \tag{12}
\]

The last quantity tends to zero as \(B\) tends to infinity.  Nevertheless
\(X=I_2\) is positive semidefinite, has \(U=N=1\), and satisfies both
lifted constraints with equality.

Moreover, each form in (10) is a positive multiple of an actual scalar
polar form.  For \(\kappa\in\mathbb R\),

\[
 (1+\kappa^2)\left[
 \frac{(n+\kappa u)^2}{1+\kappa^2}-u^2\right]
 =n^2-u^2+2\kappa un. \tag{13}
\]

Thus the inverse-block structure and the strict signs alone do not yield
rank reduction.  The pair uses \(\kappa=B\) and \(\kappa=-B\), which
cannot both arise from the sole scalar submatrix of one fixed \(k=1\)
matrix \(K\).  Any positive rank-reduction result must therefore exploit
the subset coupling among the constraints of one common \(K\).

## 5. What the trace identity does not imply

The isotropic feasible moment is an integrality obstruction, not evidence
for an exact rank reduction.  The following two-variable trace-zero family
shows the distinction.  For scalar \(u,n\), impose

\[
 2un\leq0,\qquad -2un\leq0,\qquad n^2-u^2\leq0. \tag{14}
\]

Its three quadratic matrices are respectively

\[
 \begin{pmatrix}0&1\\1&0\end{pmatrix},\qquad
 \begin{pmatrix}0&-1\\-1&0\end{pmatrix},\qquad
 \begin{pmatrix}-1&0\\0&1\end{pmatrix}; \tag{15}
\]

all have trace zero.  The first two inequalities force \(un=0\).  If
\(u\ne0\), the actual feasible point has \(n=0\); hence no positive
ratio \(|n|/|u|\) is feasible.  Yet \(X=I_2\) is positive semidefinite,
has \(U=N=1\), and makes every lifted constraint in (14) an equality.

Thus trace zero alone cannot turn (9) into a rank-one witness.  A possible
rank-reduction theorem for the finite polar matrices would have to exploit
their special inverse blocks, their subset coupling, and perhaps the
rank restriction on \(K\).  The trace calculation neither proves nor
rules out such a theorem; it rules out only the basic quadratic multiplier
and first-moment SDP routes to a strict \(\rho<1\) bound.
