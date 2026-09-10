# Prescribed-energy rank constraint

Status: a supporting theorem whose stationary-component argument and partition
argument survived independent reconstruction. This note makes no
claim of originality, sufficient significance, or publication readiness. The revised
goal requires separate assessments of those questions.

## Question and statement

The fixed-law residual estimator has covariance
\[
Q_\pi(G)=\operatorname{diag}(a_i/\pi_i)-G,\qquad a_i=G_{ii}>0,
\quad \nu(G)=\min_{\pi>0,\ \mathbf1^T\pi=1}\lambda_{\max}Q_\pi(G).
\]
Its coordinates are the stored columns; they are not freely interchangeable with
a dense right rotation of the source operator.

For \(1\le p<q\), prescribe energies \(a_1\ge\cdots\ge a_q>0\).
Put
\[
T_*=\sum_{i=p}^q a_i,\qquad \delta=(2a_p-T_*)_+,
\]
and let \(t_*>0\) be the unique solution of
\[
M(t):=\sum_{i<p}\frac{a_i}{t+a_i}
       +\frac{T_*}{t}-\frac{\delta^2}{t(T_*+t)}=1.                 \tag{1}
\]
Then
\[
\min_{\substack{G\succeq0,\ \operatorname{diag}G=a\\
                 \operatorname{rank}G\le p}}\nu(G)=t_* .         \tag{2}
\]
A minimizer consists of the largest \(p-1\) energies in orthogonal singleton
columns and the remaining \(q-p+1\) columns collinear in one further orthogonal
direction. Diagonal phases do not affect the value.

The theorem concerns the best geometry among matrices with prescribed energies
and a rank limit. It does not say that a given residual admits that geometry,
or that altering its column directions preserves the source operator. A direct
Cassette consequence must respect this distinction.

## Exact mass needed by a rank-one block

Fix a variance level \(t>0\). For a rank-one Gram block \(vv^*\), let
\(a_i=|v_i|^2>0\), \(T=\sum a_i\), and \(A=\max a_i\). Permit unnormalized
positive sampling masses \(x_i\), and define the least total mass by
\[
\rho(T,A;t)=
\min\left\{\sum_i x_i:
\operatorname{diag}(a_i/x_i)-vv^*\preceq tI\right\}.
\]
The exact formula is
\[
\rho(T,A;t)=\frac{T}{t}
-\frac{(2A-T)_+^2}{t(T+t)}.                                    \tag{3}
\]
For a singleton this becomes \(A/(t+A)\).

Here is a direct proof for a block with at least two entries. Set
\(s_i=a_i/x_i-t\). The condition is \(vv^*-\operatorname{diag}s\succeq0\).
At most one \(s_i\) can be positive, by restricting to the positive diagonal
subspace and comparing ranks. If none is positive, the least mass is \(T/t\),
attained by \(x_i=a_i/t\).

Suppose the positive shift is \(\alpha=s_h>0\), with head energy \(A_h=a_h\).
Every other shift must be strictly negative: a zero shift paired with the
positive shift gives a negative principal determinant. Write those shifts as
\(-\beta_i\), where \(0<\beta_i<t\), and put \(B=T-A_h>0\).
The Schur complement gives
\[
\alpha\le\frac{A_h}{1+\sum_{i\ne h}a_i/\beta_i}.
\]
Mass decreases with \(\alpha\), so equality is optimal. For fixed
\(C=\sum_{i\ne h}a_i/\beta_i\), Jensen's inequality applied to the convex
function \(u\mapsto u/(tu-1)\), \(u>1/t\), gives
\[
\sum_{i\ne h}\frac{a_i}{t-\beta_i}
\ge\frac{BC}{tC-B},
\]
with equality when all \(\beta_i=B/C\). Thus minimize, for \(0<\beta<t\),
\[
\phi(\beta)=
\frac{A_h(B+\beta)}{tB+(t+A_h)\beta}+\frac{B}{t-\beta}.
\]
Its derivative has the sign of
\[
\frac1{(t-\beta)^2}
-\frac{A_h^2}{[tB+(t+A_h)\beta]^2}.
\]
If \(A_h\le B\), its infimum is \(T/t\) at the zero-shift boundary.
If \(A_h>B\), its unique minimizer is
\[
\beta=\frac{t(A_h-B)}{t+2A_h}.
\]
Substitution gives (3). Such a dominant head, if it exists, is the unique
largest energy. This proves the formula, including the balanced boundary.

For a dominant head \(A>B=T-A\), explicit minimizing masses are
\[
x_h=\frac{A(t+2B)}{t(T+t)},\qquad
x_i=\frac{a_i(t+2A)}{t(T+t)}\quad(i\ne h).                       \tag{4}
\]
For \(A\le B\), use \(x_i=a_i/t\). These masses are local quantities;
they become probabilities only after all orthogonal blocks have total mass one.

## Joint stationarity without a rank-manifold assumption

Factor \(G=R^*R\), where \(R\in\mathbb F^{p\times q}\),
\(\mathbb F=\mathbb R\) or \(\mathbb C\), and \(\|r_i\|^2=a_i\).
This is a product of spheres, including matrices of rank less than \(p\).
It avoids treating the rank-constrained Gram set as a smooth manifold.

Let \(T_0=\sum a_i\). Sampling proportionally to energy gives
\(Q=T_0I-G\preceq T_0I\). The diagonal bound
\(\lambda_{\max}Q\ge a_i/\pi_i-a_i\) confines every improving law to
\(\pi_i\ge a_i/(T_0+a_i)>0\). Thus a joint minimizer exists.
Its value \(t\) is positive because \(q>p\ge1\) and all energies are positive;
if \(Q=0\), its diagonal would require \(\pi_i=1\) for every \(i\).

At a joint minimizer there is one density matrix \(X\succeq0\),
\(\operatorname{tr}X=1\), with \(QX=tX\), such that
\[
X_{ii}=c\pi_i^2/a_i,\quad c>0,\qquad RX=R\Lambda,               \tag{5}
\]
where \(\Lambda\) is real diagonal. To obtain a common witness, restrict the
top-eigenspace density matrices to the joint tangent space of the spheres
and simplex. Their differential images form a compact convex set.
If zero were outside it, strict separation would produce a direction with
negative maximal directional derivative, contrary to local minimality.
Probability variations and real or complex sphere normality then give (5).

Put \(D=\operatorname{diag}(a_i/\pi_i)\), \(S=D-tI\), and \(s_i=S_{ii}\).
From \(GX=SX=G\Lambda\) and its adjoint,
\[
\lambda_i=s_iX_{ii}/a_i=c\,s_i\pi_i^2/a_i^2.
\]
Whenever \(G_{ij}\ne0\), \(s_i\lambda_i=s_j\lambda_j\), hence
\[
|1-t\pi_i/a_i|=|1-t\pi_j/a_j|.                                \tag{6}
\]

## The mass of each connected Gram component

Connect two indices when their off-diagonal Gram entry is nonzero.
Let a connected block have size \(n\), rank \(r\), energy sum \(T\),
and probability mass \(w\). Equation (6) gives a common \(z\ge0\).

If \(z=0\), all \(\pi_i=a_i/t\), so \(w=T/t\). The principal block of
\(X\) has positive diagonal and lies in the Gram kernel, so \(r<n\).
Cross-component entries of \(X\) may exist between zero-shift blocks;
no global block-diagonality of \(X\) is assumed.

If \(z>0\), put \(W=\operatorname{diag}(\pi_i/a_i)\) on this block
and \(\Sigma=\operatorname{diag}(\operatorname{sign}s_i)\). Then
\[
X_{CC}=cW\Sigma G_C\Sigma W,\qquad
G_CW\Sigma G_C=zG_C.                                          \tag{7}
\]
Thus \(\operatorname{rank}X_{CC}=r\). Also \(Y_C=G_C-S_C\succeq0\)
annihilates \(X_{CC}\), so \(\operatorname{rank}Y_C\le n-r\).
The positive-shift principal Gram block is positive definite, so there
are at most \(r\) positive shifts. The negative-shift principal block
of \(Y_C\) is positive definite, so there are at most \(n-r\) negative
shifts. Since no shift is zero, there are exactly \(r\) positive shifts.

A full-row-rank factor of (7) gives
\(R_CW\Sigma R_C^*=zI_r\). Taking traces yields
\(\sum\sigma_i\pi_i=rz\). If \(P\) is the positive-shift index set and
\(\Delta=2\sum_{i\in P}a_i-T\), then
\[
z=\frac{\Delta}{T+rt}>0,\qquad
w=\frac1t\left(T-\frac{\Delta^2}{T+rt}\right).                  \tag{8}
\]
A full-rank connected component has \(X_{CC}\succ0\), hence \(Y_C=0\)
and diagonal \(G_C\). Connectedness forces it to be a singleton.

## Replacing a singular component

Sort a singular component's energies as \(b_1\ge\cdots\ge b_n>0\).
Keep its rank \(r<n\), and replace its geometry by \(r-1\) singleton
columns of energies \(b_1,\ldots,b_{r-1}\) and a rank-one block on the rest.
Let
\[
L=\sum_{i<r}b_i,\quad B=\sum_{i>r}b_i,\quad T=L+b_r+B.
\]
The replacement saves, relative to mass \(T/t\),
\[
\frac Ht,\qquad
H=\sum_{i<r}\frac{b_i^2}{t+b_i}
+\frac{(b_r-B)_+^2}{t+b_r+B}.                                 \tag{9}
\]
A zero-shift component has mass \(T/t\), so replacement cannot cost more.
It costs strictly less if \(r>1\).

For a nonzero-shift component, its \(r\) positive shifts obey
\(0<\Delta\le\Delta_{\max}=L+b_r-B\).
If \(b_r\ge B\), weighted Cauchy--Schwarz gives
\[
H\ge\frac{(L+b_r-B)^2}{T+rt}
\ge\frac{\Delta^2}{T+rt}.                                     \tag{10}
\]
If \(b_r<B\), then \(r>1\), and
\[
H\ge\frac{L^2}{L+(r-1)t}
>\frac{(L+b_r-B)^2}{T+rt}
\ge\frac{\Delta^2}{T+rt}.                                     \tag{11}
\]
Comparison with (8) proves replacement cannot increase mass.
For \(r>1\), (10) is also strict: \(B>0\) and
\(b_i/(t+b_i)>(b_r-B)/(t+b_r+B)\) for every \(i<r\), so the
Cauchy--Schwarz equality conditions cannot hold.

Consequently a global minimizer can be replaced, at no greater mass and
no greater rank, by a partition into orthogonal rank-one blocks.
This implication uses the stationarity of a joint global minimizer;
it does not assert that every arbitrary Gram component satisfies (8).

## Concentrating the rank-one partition

For head energy \(A\) and tail energy \(B\), write
\[
F(A,B)=\frac{(A-B)_+^2}{A+B+t}.
\]
At fixed \(t\), minimizing partition mass is equivalent to maximizing
the sum of \(F\) over its blocks.

For \(A\ge C>0\) and \(B,D\ge0\),
\[
F(A,B)+F(C,D)\le F(A,0)+F(C,B+D).                              \tag{12}
\]
Define \(L_A(B)=F(A,0)-F(A,B)\). Its derivative is
\[
L_A'(B)=
\begin{cases}
(2A+t)^2/(A+B+t)^2-1,&B<A,\\
0,&B\ge A.
\end{cases}
\]
For fixed \(B\), this is nondecreasing in \(A\), since
\((2A+t)/(A+B+t)\) increases with \(A\).
Also \(F(C,\cdot)\) is convex and decreasing. Therefore
\[
L_A(B)\ge L_C(B)\ge F(C,D)-F(C,D+B),
\]
which is (12).

Use (12) to isolate the largest remaining head and move its tail into
another block. The new block might contain a larger head than \(C\);
this only improves its saving, because at fixed total \(S\),
\((2H-S)_+^2/(S+t)\) is nondecreasing in \(H\). Repeat until only one
nonsingleton block remains. If fewer than \(p\) blocks were present,
splitting a positive tail entry into a new singleton strictly increases
the saving. Thus the canonical \(p\)-block partition minimizes mass.

Its mass is \(M(t)\) from (1). Every term strictly decreases.
For the last block, write \(A=a_p\), \(B=T_*-A>0\).
In the dominant case its mass is
\((T_*t+4AB)/(t(T_*+t))\), which has negative derivative.
Moreover \(M(t)\to\infty\) at zero and \(M(t)\to0\) at infinity.
Thus (1) has exactly one positive solution.

## Completing the minimization

At a joint minimizer of value \(t\), component replacement followed by
partition concentration proves \(1\ge M(t)\), so \(t\ge t_*\).
For the canonical geometry, assign each singleton mass \(a_i/(t_*+a_i)\)
and use (4), or the balanced masses, on the final block. Their sum is
one. Every covariance block is at most \(t_*I\), proving attainment.

To turn a strict mass improvement into a strict objective improvement, add
the unused positive probability mass to every coordinate. Every diagonal
entry of the loading then decreases strictly, so the new covariance has
largest eigenvalue strictly below the old threshold. This respects the
rank bound. Equality classification additionally uses strictness of the
partition-concentration inequalities; that step is recorded separately
when its reconstruction finishes.

## Boundaries and next discriminators

- Zero-energy columns are removed from the active support. The statement
  above assumes all prescribed energies are positive.
- The theorem handles both real and complex Gram geometry.
- A source residual with fixed directions only inherits the lower bound.
  Achieving the minimizing geometry requires a separate admissible operation.
- Equal energies recover the formula in rank_constrained_gram.md.
- Rank one recovers the earlier local rank-one sampling formula.
- Correctness does not establish originality. The revised objective also
  requires a consequential application and comparison with closest primary work.
