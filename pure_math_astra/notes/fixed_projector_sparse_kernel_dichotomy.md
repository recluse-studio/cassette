# Fixed-projector sparse-kernel dichotomy for adaptive hard-cap estimation

Status: proved for fixed real projectors, with independent reconstruction
in fixed_projector_sparse_kernel_dichotomy_independent_review.md and root
reconstruction of the assembled argument. The statement concerns both the
query-adaptive exact-mean problem and the fixed-law linear problem. Its
constants can deteriorate as the projector moves, so it does not imply a
uniform Grassmannian result. Originality and sufficient application
significance remain unassessed.

Let \(P\) be a real rank-\(k\) orthogonal projector on \(\mathbb R^{2k}\),
let \(N=I-P\), and, for \(0<r\le1\), put

\[
 G_r=P+r^2N.
\tag{1}
\]

For the hard support cap \(k\), define

\[
 \Psi_k(G_r)=\sup_{\|x\|_2=1}
 \inf_{\substack{\mathbb EY=x\\\|Y\|_0\le k\ {\rm a.s.}}}
 \mathbb E\,(Y-x)^TG_r(Y-x).
\tag{2}
\]

For comparison, let \(\nu_k(G_r)\) be the corresponding fixed-law value:
the infimum of the displayed worst-query risk over random linear maps \(L\)
with \(\mathbb EL=I\) and at most \(k\) nonzero output rows almost surely.
Every such law is available to the inner infimum in (2), so
\(\Psi_k(G_r)\le\nu_k(G_r)\).

For a coordinate support \(S\), identify \(\mathbb R^S\) with vectors
supported in \(S\), and set

\[
 W=\operatorname{span}\{\ker(P|_{\mathbb R^S}):|S|\le k\}\subseteq\ker P.
\tag{3}
\]

A support is *singular* when \(P|_{\mathbb R^S}\) is noninjective,
equivalently when \(P_{SS}\) is singular.  This is not the same as saying
that its image has dimension below \(k\): every support of size below \(k\)
has such an image, even when the restriction is injective.

## The dichotomy

**Theorem.**  For every fixed \(P\), exactly one of the following holds.

\[
 \begin{aligned}
 W=\ker P&\quad\Longrightarrow\quad
 \Psi_k(G_r)=\Theta_P(r),\quad\nu_k(G_r)=\Theta_P(r),\\
 W\ne\ker P&\quad\Longrightarrow\quad
 \Psi_k(G_r)=\Theta_P(1),\quad\nu_k(G_r)=\Theta_P(1).
 \end{aligned}
\tag{4}
\]

The subscript on \(\Theta_P\) means that both constants may depend on
\(P\).

## Sparse-kernel case: the upper bound

Assume \(W=\ker P\).  Because there are finitely many supports, choose a
finite basis \(n_1,\ldots,n_m\) of \(\ker P\), each vector supported on at
most \(k\) coordinates.  Choose a row-orthonormal
\(A\in\mathbb R^{k\times 2k}\) with \(P=A^TA\).  For an increasing
\(k\)-subset \(S\), let \(A_S\) be the associated column submatrix,
\(E_S\) coordinate insertion, and

\[
 \mathcal F=\{S:\det A_S\ne0\},\qquad
 p_S=\det(A_S)^2,\qquad H_S=E_SA_S^{-1}A.
\tag{5}
\]

Cauchy--Binet gives \(\sum_{S\in\mathcal F}p_S=1\), and its
entrywise derivative gives the adjugate identity

\[
 \sum_{S\in\mathcal F}p_SH_S=P.
\tag{6}
\]

Thus, if \(S\) has law \(p_S\) and \(Y_H=H_Sx\), then

\[
 \operatorname{supp}Y_H\subseteq S,\qquad
 PY_H=Px,\qquad \mathbb EY_H=Px.
\tag{7}
\]

The cofactor Cauchy--Binet identity is

\[
 \sum_{|S|=k}\operatorname{adj}(A_S)^T\operatorname{adj}(A_S)
 =(2k-k+1)I_k=(k+1)I_k.
\tag{8}
\]

It follows by applying Cauchy--Binet to the \((k-1)\)-row minors; the
off-diagonal terms vanish by row orthogonality.  The omitted singular
supports contribute positive-semidefinite terms to (8).  Since
\(p_SA_S^{-T}A_S^{-1}=\operatorname{adj}(A_S)^T\operatorname{adj}(A_S)\)
on \(\mathcal F\), this implies

\[
 \mathbb E\|Y_H\|_2^2\le(k+1)\|Px\|_2^2,\qquad
 \mathbb E\|NY_H\|_2^2\le k\|Px\|_2^2.
\tag{9}
\]

For \(w\in\ker P\), write \(w=\sum_j c_j(w)n_j\) using a fixed linear
coefficient map.  If \(J\) is uniform on \(\{1,\ldots,m\}\), define

\[
 Y_N=m c_J(Nx)n_J.
\tag{10}
\]

Every outcome is \(k\)-sparse, \(PY_N=0\), and \(\mathbb EY_N=Nx\).
Because this is a fixed finite construction, some \(C_N<\infty\) satisfies

\[
 \mathbb E\|Y_N\|_2^2\le C_N\|Nx\|_2^2.
\tag{11}
\]

Mix the two outputs with \(\rho=\min(r,1/2)\):

\[
 Y=\begin{cases}
  Y_H/(1-\rho),&\text{with probability }1-\rho,\\
  Y_N/\rho,&\text{with probability }\rho.
 \end{cases}
\tag{12}
\]

The two outputs are not added, so each outcome remains \(k\)-sparse, and
\(\mathbb EY=x\).  The high-space terms are of order \(\rho\), the
low-space terms are of order \(r^2/\rho\), by (9) and (11).  Explicitly,
for unit \(x\),

\[
\mathbb E\,(Y-x)^TG_r(Y-x)
\le \rho+{\rho^2\over1-\rho}+(2k+2)r^2+{C_Nr^2\over\rho}.
\tag{13}
\]

For (13), \(\mathbb ENY_H=0\), so the high-branch low-space contribution
is at most \(2kr^2+r^2\); the two high-space contributions are the first
two terms.  The low-branch low-space contribution is at most
\(C_Nr^2/\rho\) by exact unbiasedness of \(Y_N\).

Hence \(\nu_k(G_r)\le C_Pr\), because (12) is a fixed random linear law;
therefore \(\Psi_k(G_r)\le C_Pr\) as well.

## Sparse-kernel case: the lower bound

Let \(\mathcal D\) and \(\mathcal I\) be respectively the singular and
injective supports of size at most \(k\).  Since \(W=\ker P\ne0\),
\(\mathcal D\) is nonempty.  Each \(P\mathbb R^S\) for \(S\in\mathcal D\)
is a proper subspace of \(\operatorname{range}P\).  Choose a unit
\(u\in\operatorname{range}P\) outside their finite union, and let

\[
 d=\min_{S\in\mathcal D}\operatorname{dist}(u,P\mathbb R^S)>0,\qquad
 M=\max_{\substack{S\in\mathcal I\\S\ne\varnothing}}
 \sup_{0\ne y\in\mathbb R^S}{\|Ny\|_2\over\|Py\|_2},\qquad
 \mu=\max(1,M).
\tag{14}
\]

Both constants are finite. The empty support is omitted from the maximum;
the zero output satisfies the injective bound automatically. There is a
nonempty injective support because P has positive rank.
Choose a unit \(n\in\ker P\), set

\[
 a={1\over\sqrt{1+16\mu^2}},\qquad b=4\mu a,\qquad x=au+bn,
\tag{15}
\]

and let \(V\) be the risk of any admissible \(Y\) with \(\mathbb EY=x\).
An infinite risk already satisfies the lower bound. For finite V, positive
definiteness of G_r gives the second moments needed below.
If \(D\) is the event that the realized support is singular, with
\(p=\Pr(D)\), then

\[
 p\le{V\over a^2d^2}.
\tag{16}
\]

When \(V<a^2\), injective outcomes satisfy \(\|NY\|\le\mu\|PY\|\), so

\[
 \left\|\mathbb E[NY1_{D^c}]\right\|_2
 \le\mu(a+\sqrt V)<{b\over2}.
\tag{17}
\]

As \(\mathbb ENY=bn\), (17) forces a nonzero conditional mean on D,
so p>0. The case V=0 is impossible by (16)-(17). Eventwise
Cauchy--Schwarz and (16) therefore give

\[
 \mathbb E\|NY\|_2^2\ge{b^2\over4p}
 \ge{a^2d^2b^2\over4V}.
\tag{18}
\]

Since
\(\mathbb E\|N(Y-x)\|_2^2=\mathbb E\|NY\|_2^2-b^2\), it follows that

\[
 V^2+r^2b^2V\ge{r^2a^2d^2b^2\over4}.
\tag{19}
\]

If \(V<a^2\), divide (19) by \(r^2\) and use \(r\le1\).  If
\(V\ge a^2\), use \(V\ge a^2r\).  In either case,

\[
 V\ge c_Pr,\qquad
 c_P=\min\left\{a^2,
 {\sqrt{b^4+a^2d^2b^2}-b^2\over2}\right\}>0.
\tag{20}
\]

This lower bound was proved for \(\Psi_k\), hence also lower-bounds
\(\nu_k\) because \(\Psi_k\le\nu_k\).  Combined with the fixed-law
construction (12), it proves the first row of (4).

## Nonsparse-kernel case

Assume \(W\ne\ker P\), and choose a unit
\(n\in\ker P\cap W^\perp\).  On every coordinate support \(S\) of size
at most \(k\), the functional \(y\mapsto\langle n,y\rangle\) annihilates
\(\ker(P|_{\mathbb R^S})\).  It therefore factors through
\(P|_{\mathbb R^S}\).  Finiteness of the support family supplies a finite,
positive \(C\) such that

\[
 |\langle n,y\rangle|\le C\|Py\|_2
 \qquad(y\text{ supported on some }S, |S|\le k).
\tag{21}
\]

For the query \(x=n\), every admissible estimator consequently satisfies

\[
 1=\langle n,\mathbb EY\rangle
 \le C\sqrt{\mathbb E\|PY\|_2^2},\qquad
 \mathbb E\,(Y-n)^TG_r(Y-n)\ge {1\over C^2}.
\tag{22}
\]

This argument does not need a singular support.  In particular, if the
singular-support family is empty then \(W=0\), and this branch applies.
For the matching finite upper bound, choose a coordinate uniformly and
output \(2k\,x_i e_i\).  It is unbiased and one-sparse, with Euclidean
risk \(2k-1\); since \(G_r\preceq I\),

\[
 {1\over C^2}\le\Psi_k(G_r)\le\nu_k(G_r)\le2k-1.
\tag{23}
\]

The lower bound here is again for \(\Psi_k\), hence also for \(\nu_k\);
the coordinate law is fixed.  This proves the second row of (4), including
\(k=1\).

## Sharpening for the \(K_4\) cut projector

For the rank-three \(K_4\) cut-space projector, let \(c_1,\ldots,c_4\)
be the four unit oriented triangle cycles.  A direct edge-incidence
calculation gives the tight-frame identity

\[
 \sum_{i=1}^4c_ic_i^T={4\over3}N.
\tag{24}
\]

Thus \(Y_N=3c_Ic_I^Tx\), with \(I\) uniform on the four faces, is
three-sparse and satisfies

\[
 \mathbb EY_N=Nx,\qquad \mathbb E\|Y_N\|_2^2=3\|Nx\|_2^2.
\tag{25}
\]

Use the volume high law above and mix with
\(\rho=r/(1+r)\).  Writing \(h=\|Px\|_2^2\) and \(\ell=\|Nx\|_2^2\),
the high-law mean is \(\mathbb ENY_H=0\), (9) gives
\(\mathbb E\|NY_H\|_2^2\le3h\), and direct expansion gives

\[
 \mathbb E\,(Y-x)^TG_r(Y-x)
 \le\bigl[r+3r^2(1+r)\bigr]h+
 \bigl[3r+2r^2\bigr]\ell
 \le7r.
\tag{26}
\]

Therefore \(\nu_3(P+r^2N)\le7r\), and hence
\(\Psi_3(P+r^2N)\le7r\), for \(0<r\le1\).  Together with the
support-splitting lower bound, this yields \(\Theta_P(r)\) for both
quantifiers at this fixed projector.  The ingredients here are standard
Cauchy--Binet and finite-frame identities; this note makes no novelty claim.
