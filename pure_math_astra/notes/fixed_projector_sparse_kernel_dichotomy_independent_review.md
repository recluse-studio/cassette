# Independent review of the fixed-projector sparse-kernel dichotomy

Status: the dichotomy in fixed_projector_sparse_kernel_dichotomy.md is
correct for fixed real rank-\(k\) projectors on \(\mathbb R^{2k}\).
The empty-support convention identified below has been repaired in the
theorem. The lower bounds concern all query-adaptive exact-mean
coefficient laws with the hard cap. The upper constructions are also
query-independent full linear laws, so the dichotomy holds for both
Psi_k and nu_k.

Let \(P\) be a rank-\(k\) real orthogonal projector, \(N=I-P\), and

\[
G_r=P+r^2N,\qquad0<r\le1.
\]

For supports of size at most \(k\), define

\[
W=\operatorname{span}\{\ker(P|_{\mathbb R^S}):|S|\le k\}.
\]

## The sparse-kernel upper bound

If \(W=\ker P\), then finite-dimensionality supplies a basis
\(n_1,\ldots,n_m\) of \(\ker P\), each with support at most \(k\).

Choose \(A\in\mathbb R^{k\times2k}\) with \(AA^T=I_k\) and \(P=A^TA\).
For a full-rank \(k\)-column set \(S\), put

\[
p_S=\det(A_S)^2,\qquad H_S=E_SA_S^{-1}A.
\]

The differentiated Cauchy--Binet identity is exact. For an arbitrary
increment \(D\),

\[
D\det(AA^T)[D]=2\langle A,D\rangle_F,
\]

whereas differentiation of
\(\det(AA^T)=\sum_{|S|=k}\det(A_S)^2\) gives

\[
2\left\langle\sum_Sp_SA_S^{-T}E_S^T,D\right\rangle_F.
\]

Therefore

\[
\sum_Sp_SE_SA_S^{-1}=A^T,\qquad
\sum_Sp_SH_S=P. \tag{R1}
\]

Thus the volume law \(Y_H=H_Sx\) is supported on \(S\), has
\(PY_H=Px\) in every outcome, and has \(\mathbb EY_H=Px\).

The cofactor Cauchy--Binet identity used in the assembled note is also
correct:

\[
\sum_{|S|=k}\operatorname{adj}(A_S)^T\operatorname{adj}(A_S)
=(k+1)I_k.
\]

The singular minors have positive-semidefinite cofactor contributions.
Consequently,

\[
\mathbb E\|Y_H\|^2\le(k+1)\|Px\|^2,\qquad
\mathbb E\|NY_H\|^2\le k\|Px\|^2. \tag{R2}
\]

The second inequality follows by subtracting the deterministic
\(\|PY_H\|^2=\|Px\|^2\).

A fixed sparse-kernel law \(Y_N\), obtained by selecting a basis vector and
applying the reciprocal coefficient weight, has
\(\mathbb EY_N=Nx\), \(PY_N=0\), hard support at most \(k\), and finite
second moment bounded by \(C_N\|Nx\|^2\). Mixing \(Y_H/(1-\rho)\) and
\(Y_N/\rho\) without adding outcomes preserves the hard cap and gives
exact mean. With \(\rho=\min(r,1/2)\), the high-space risk is
\(O(\rho)\), while the low-space risk is \(O(r^2/\rho)\), uniformly over
unit queries. Hence

\[
\Psi_k(P+r^2N)\le C_Pr. \tag{R3}
\]

The construction has no hidden moment issue: each branch has a finite
second moment because only finitely many fixed matrices and sparse basis
vectors occur.

Every branch is a fixed linear map of x, and every probability depends on
P,r alone. Consequently (R3) holds with nu_k on its left as well.
The one-coordinate law in the nonsparse branch has the same property.

## The sparse-kernel lower bound

Assume \(W=\ker P\). Singular supports are nonempty in this branch, since
\(\ker P\) has dimension \(k>0\). Their images \(P\mathbb R^S\) are
proper subspaces of \(\operatorname{range}P\): a singular restriction has
rank strictly below \(\dim\mathbb R^S\le k\). A unit vector \(u\) can
therefore avoid their finite union, and

\[
d=\min_{S\ {\rm singular}}\operatorname{dist}(u,P\mathbb R^S)>0.
\]

On each injective nonempty support, finite-dimensional injectivity gives

\[
\|Ny\|\le M\|Py\| .
\]

Take \(M\) at least one. This harmless enlargement is necessary when the
optimal displayed maximum is zero, as for a coordinate projector. Put

\[
a=(1+16M^2)^{-1/2},\qquad b=4Ma,\qquad
x=au+bn,
\]

where \(n\) is a unit vector in \(\ker P\). Then \(x\) is unit.

Let \(Y\) be any admissible exact-mean output and let \(V\) be its risk.
If \(V=\infty\), the desired lower bound is immediate. Otherwise its
second moment is finite because \(G_r\succ0\), so every Cauchy--Schwarz
step below is legitimate. Let \(D\) be the event that the actual support
of \(Y\) is singular and \(p=\Pr(D)\). Every outcome in \(D\) has

\[
\|P(Y-x)\|\ge ad,\qquad p\le {V\over a^2d^2}. \tag{R4}
\]

If \(V<a^2\), injective outcomes give

\[
\left\|\mathbb E[NY1_{D^c}]\right\|
\le M\mathbb E\|PY\|
\le M(a+\sqrt V)<b/2. \tag{R5}
\]

Exact mean gives \(\mathbb ENY=bn\), hence

\[
\left\|\mathbb E[NY1_D]\right\|>b/2.
\]

The eventwise Cauchy--Schwarz inequality and (R4) yield

\[
\mathbb E\|NY\|^2\ge{b^2\over4p}
\ge{a^2d^2b^2\over4V}. \tag{R6}
\]

Since
\(\mathbb E\|N(Y-x)\|^2=\mathbb E\|NY\|^2-b^2\), it follows that

\[
V^2+r^2b^2V\ge{r^2a^2d^2b^2\over4}. \tag{R7}
\]

Writing \(w=V/r\) and using \(r\le1\), (R7) gives
\(w^2+b^2w\ge a^2d^2b^2/4\). Thus \(w\) is at least the positive root of
that last quadratic. If \(V\ge a^2\), then \(V\ge a^2r\). The two cases
give \(V\ge c_Pr\) for a positive constant depending only on \(P\).
Combined with (R3), this proves \(\Theta_P(r)\).


## The nonsparse-kernel branch

If \(W\ne\ker P\), choose a unit \(n\in\ker P\cap W^\perp\). On every
support \(S\), the functional \(y\mapsto\langle n,y\rangle\) vanishes on
\(\ker(P|_{\mathbb R^S})\), so it factors through
\(P|_{\mathbb R^S}\). Since there are only finitely many supports, there
is a finite \(C\) such that

\[
|\langle n,y\rangle|\le C\|Py\|
\]

for every \(k\)-sparse \(y\). The constant is positive: otherwise its
singleton-support inequalities would force \(n=0\).

For the query \(x=n\), every finite-risk exact-mean estimator obeys

\[
1=\langle n,\mathbb EY\rangle
\le C\sqrt{\mathbb E\|PY\|^2}.
\]

Because \(Pn=0\), its \(G_r\)-risk is at least \(1/C^2\), uniformly in
\(r\). A uniform one-coordinate Horvitz--Thompson law gives the matching
finite upper bound: choose \(i\) uniformly in \([2k]\) and output
\(2k\,x_ie_i\). Its Euclidean risk is \(2k-1\), and \(G_r\preceq I\).
Therefore

\[
\Psi_k(P+r^2N)=\Theta_P(1). \tag{R8}
\]

This branch covers an empty singular-support family. In the stated
rank-\(k\) setting, such a family implies \(W=0\), hence it necessarily
falls in the nonsparse branch.

For \(k=1\), the same proof is valid. A coordinate rank-one projector has
a one-sparse kernel vector and lies in the order-\(r\) branch. A
non-coordinate rank-one projector has no one-sparse kernel vector, so
\(W=0\) and lies in the order-one branch.

## Review finding

The assembled dichotomy is mathematically sound. The only formal convention
needed for complete literal coverage is to omit the empty support from the
maximum defining \(M\) in its Equation (14), or define its supremum to be
zero. The zero output itself satisfies the injective inequality
automatically. This convention does not alter any estimate or conclusion.



## Narrow check of the K4 class consequence

The arithmetic in k4_diagonal_and_full_linear_rate_separation.md is correct
in its stated fixed edge-coordinate representation.

For a diagonal law, let \(d_i=D_{ii}\) and
\(p_i=\Pr(d_i\ne0)\). Exact mean gives
\(\mathbb E d_i=1\), so Cauchy--Schwarz on the event \(d_i\ne0\) gives
\(\mathbb E d_i^2\ge1/p_i\). The hard cap gives
\(\sum_i p_i\le3\). Since every diagonal entry of \(G_r\) equals
\(g=(1+r^2)/2\),

\[
\operatorname{tr}\mathbb E[(D-I)^TG_r(D-I)]
\ge g\left(\sum_i p_i^{-1}-6\right)\ge6g.
\]

Hence \(\Phi_3(G_r)\ge g\).

For uniform three-subset sampling with diagonal selected weight two, the
centered diagonal multiplier has second moments one on the diagonal and
\(-1/5\) off it. Entrywise multiplication with \(G_r\) gives

\[
C={6\over5}gI-{1\over5}G_r.
\]

The eigenvalues of \(G_r\) are \(1\) and \(r^2\), each threefold. For
\(0<r\le1\), the largest eigenvalue of \(C\) is

\[
{6\over5}g-{r^2\over5}
={3\over5}+{2r^2\over5}.
\]

Thus the displayed diagonal bounds are valid.

The volume-plus-cycle mixture is a common random row-sparse linear operator:
its outcome law depends on \(P,r\), but not on \(x\), and each component has
at most three nonzero output rows. It therefore gives a bound for
\(\nu_3\), not merely for \(\Psi_3\). The arbitrary-law lower bound for
\(\Psi_3\), together with \(\Psi_3\le\nu_3\le\Phi_3\), yields

\[
\Psi_3(G_r)=\Theta(r),\qquad
\nu_3(G_r)=\Theta(r),\qquad
\Phi_3(G_r)=\Theta(1).
\]

The quantifiers do not allow a free orthogonal coordinate change. The
separation is between declared coefficient classes in the original fixed
edge representation.
