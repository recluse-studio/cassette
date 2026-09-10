# Fixed transform libraries: a Grassmann covering consequence

Status: supporting finite-library result. It is not a general Cassette lower
bound, and it makes no originality claim.

## 1. Declared model

Fix a field \(\mathbb F\in\{\mathbb R,\mathbb C\}\), integers
\(0<s<q\), and a library

\[
 \mathcal V=\{V_1,\ldots,V_K\}\subset O(q)\ \text{or}\ U(q).
\]

The source Gram matrix ranges over the full isospectral orbit

\[
 G_P=I+\alpha P,\qquad P\in\operatorname{Gr}_{\mathbb F}(r,q),
 \qquad \alpha>0,
\tag{1}
\]

where \(P\) is a rank-\(r\) orthogonal projection. Every \(G_P\) is
positive definite. A scheme chooses an already-declared \(V_j\), then uses
unbiased diagonal thinning of at most \(s\) columns in that basis. Its best
variance is \(\Phi_s(V_j^*G_PV_j)\). The unrestricted rank-\(s\) ideal is
the unique \(t=t_s(G_P)>0\) satisfying

\[
 \frac{r(1+\alpha)}{1+\alpha+t}
 +\frac{q-r}{1+t}=s.
\tag{2}

This is a deliberately narrow model. The library index, its decoding rule,
and every resident datum used to select \(V_j\) belong to the declared
description cost. General decoders, transforms inferred from fresh pages,
and nonlibrary transforms are outside the statement.

Write \(A=1+\alpha\), and define the chordal Grassmann distance by

\[
 d_c(P,Q)^2=\tfrac12\lVert P-Q\rVert_F^2.
\tag{3}

For the symmetric central regime \(q=2r\), \(s=r\), equation (2) gives

\[
 t=\sqrt A.
\tag{4}

## 2. From the variance gap to a covering condition

For a chosen \(V\), put \(Q=V^*PV\). The quantitative fixed-basis gap in
`coded_basis_rigidity.md` gives

\[
 \Phi_s(I+\alpha Q)-t
 \geq c_V\alpha^2\lVert Q-\operatorname{Diag}Q\rVert_F^2,
\tag{5}

where

\[
 c_V=
 \frac{t}{(A+t)^3\sum_i a_i/(a_i+t)^2},
 \qquad a_i=1+\alpha Q_{ii}.
\tag{6}

Since \(1\leq a_i\leq A\), a basis-independent valid constant is

\[
 c_0=\frac{t}{q(A+t)^3h},
 \qquad
 h=\max_{1\leq x\leq A}\frac{x}{(x+t)^2}.
\tag{7}

For every rank-\(r\) projection \(Q\), let \(S\) index its \(r\) largest
diagonal entries and put \(P_S=\operatorname{Diag}\mathbf1_S\). If
\(\delta=r-\sum_{i\in S}Q_{ii}\), then

\[
 d_c(Q,P_S)^2=\delta
 \leq\sum_iQ_{ii}(1-Q_{ii})
 =\lVert Q-\operatorname{Diag}Q\rVert_F^2.
\tag{8}

Indeed, with \(d_i=Q_{ii}\) and
\(\tau=\min_{i\in S}d_i\),

\[
 \sum_i d_i(1-d_i)-\delta
 =\sum_{i\in S}d_i(1-d_i)-\sum_{i\notin S}d_i^2
 \geq \tau\delta-\tau\delta=0.
\]

Here \(\sum_{i\in S}(1-d_i)=\delta=\sum_{i\notin S}d_i\), while
\(d_i\geq\tau\) on \(S\) and \(d_i\leq\tau\) off \(S\). Thus (5)
implies

\[
 \Phi_s(V^*G_PV)-t
 \geq c_0\alpha^2
 \min_{|S|=r}d_c(P,VP_SV^*)^2.
\tag{9}

Suppose the library is required to achieve additive error \(\varepsilon>0\)
for every source in (1):

\[
 \min_{1\leq j\leq K}\Phi_s(V_j^*G_PV_j)\leq t+\varepsilon
 \quad\text{for every }P.
\tag{10}

Then the \(K\binom qr\) centers \(V_jP_SV_j^*\) cover the Grassmannian at
radius

\[
 \rho=\sqrt{\frac{\varepsilon}{c_0\alpha^2}}.
\tag{11}

This is the whole lower-bound mechanism. It uses no claim about a physical
encoding of a matrix, only the finite cardinality of the declared library.

In the central case, \(t=\sqrt A\) lies in \([1,A]\), so
\(h=1/(4\sqrt A)\) and

\[
 c_0=\frac{4}{q\sqrt A(1+\sqrt A)^3}.
\tag{12}

Consequently

\[
 \rho^2=
 \frac{\varepsilon q\sqrt A(1+\sqrt A)^3}{4\alpha^2}.
\tag{13}

## 3. Explicit Grassmann volume consequence

Let \(\mu\) be normalized invariant measure on the Grassmannian. Covering
by the centers in (10) requires

\[
 K\binom qr\mu(B_{d_c}(\rho))\geq1,
 \qquad
 K\geq\frac{1}{\binom qr\mu(B_{d_c}(\rho))}.
\tag{14}

Wei Dai, Youjian Liu, and Brian Rider,
[*Quantization Bounds on Grassmann Manifolds and Applications to MIMO
Communications* (2008), Theorem 1](https://doi.org/10.1109/TIT.2007.915691),
derive the required small-ball volumes. Their full primary proof was checked.
For \(0<\rho\leq1\), over \(\mathbb C\),

\[
 \mu(B_{d_c}(\rho))=c_{q,r,2}\rho^{2r(q-r)},
 \qquad
 c_{q,r,2}=
 \frac{\prod_{i=1}^r (q-i)!/(r-i)!}{(r(q-r))!}
 \quad(r\leq q/2),
\tag{15}

with the complementary-rank formula when \(r>q/2\). Therefore

\[
 K\geq
 \frac1{\binom qr c_{q,r,2}}
 \left(\frac{c_0\alpha^2}{\varepsilon}\right)^{r(q-r)}.
\tag{16}

Over \(\mathbb R\), their theorem gives, as \(\rho\downarrow0\),

\[
 \mu(B_{d_c}(\rho))
 =c_{q,r,1}\rho^{r(q-r)}(1+o(1)),
\tag{17}

where \(c_{q,r,1}\) is their explicit invariant-integral constant. Hence

\[
 K\geq
 \frac{1+o(1)}{\binom qr c_{q,r,1}}
 \left(\frac{c_0\alpha^2}{\varepsilon}\right)^{r(q-r)/2}.
\tag{18}

Equations (16)--(18) are standard volume-covering corollaries. If a transform
is identified solely by an index into this library, it needs at least
\(\lceil\log_2K\rceil\) distinguishable labels. That is not an encoded-byte
lower bound: the transforms, the index code, and selection data can have
other costs, and a model with general resident decoders is outside this
finite-library argument.

## 4. Fixed-count cancellation at an arithmetic two-block point

The lower gap does not itself give a matching upper bound. A general
fixed-size sampler has pair-inclusion terms in its covariance; omitting them
is wrong. At an arithmetic two-block point they can be cancelled exactly.

Let

\[
 G_P=\lambda_-I+(\lambda_+-\lambda_-)P,\qquad
 \lambda_+>\lambda_->0,
\tag{19}
\]

where \(P\) has rank \(m\) in dimension \(m+n\). Put

\[
 \frac{m\lambda_+}{\lambda_++t}
 +\frac{n\lambda_-}{\lambda_-+t}=s,\qquad
 p_+=\frac{\lambda_+}{\lambda_++t},\qquad
 p_-=\frac{\lambda_-}{\lambda_-+t}.
\tag{20}
\]

Here \(t>0\) is the unique root. Thus \(s=mp_++np_-\). Assume that
\(k=mp_+\) is an integer. At \(P_0=\operatorname{Diag}(I_m,0_n)\),
independently select a uniform
\(k\)-subset of the first block and a uniform \((s-k)\)-subset of the
second. For a selected set \(S\), use

\[
 Z_S=\sum_{i\in S}\frac{R_i e_i^*}{p_{g(i)}},
 \qquad R^*R=G_P,
\tag{21}
\]

where \(g(i)\in\{+,-\}\) is the coordinate block. This sampler selects
exactly \(s\) columns and has \(\mathbb E Z_S=R\).

For a fixed-size diagonal Horvitz--Thompson sampler, direct expansion gives

\[
 \bigl(\mathbb E Z_S^*Z_S-G_P\bigr)_{ii}
 =G_{ii}(\pi_i^{-1}-1),\qquad
 \bigl(\mathbb E Z_S^*Z_S-G_P\bigr)_{ij}
 =G_{ij}\left(\frac{\pi_{ij}}{\pi_i\pi_j}-1\right)\quad(i\ne j).
\tag{22}
\]

Here \(\pi_i=p_+\) or \(p_-\), and the independent block selections give
\(\pi_{ij}=p_+p_-\) across blocks. Cross-block covariance therefore
vanishes. At \(P=P_0\), the covariance is \(tI\), since
\(\lambda_\pm(p_\pm^{-1}-1)=t\).

Write a nearby projection in blocks as

\[
 P=\begin{pmatrix}I_m-X&C\\C^*&Y\end{pmatrix}.
\]

The projection identities give \(X,Y\succeq0\) and

\[
 \operatorname{tr}X=\operatorname{tr}Y
 =d_c(P,P_0)^2=:\delta,\qquad
 \lVert X\rVert_F,\lVert Y\rVert_F\leq\delta.
\tag{23}
\]

For \(m,n>1\), the same-block pair coefficients are

\[
 \beta_+=-\frac{1-p_+}{p_+(m-1)},\qquad
 \beta_-=-\frac{1-p_-}{p_-(n-1)}.
\tag{24}
\]

Thus the covariance perturbation from \(tI\) is block diagonal, with

\[
 \begin{aligned}
 D_+&=-(\lambda_+-\lambda_-)
 \left[\frac{t}{\lambda_+}\operatorname{Diag}X+
       \beta_+\operatorname{Off}X\right],\\
 D_-&=(\lambda_+-\lambda_-)
 \left[\frac{t}{\lambda_-}\operatorname{Diag}Y+
       \beta_-\operatorname{Off}Y\right].
 \end{aligned}
\tag{25}
\]

Consequently

\[
 \Phi_s(G_P)\leq t+C\,d_c(P,P_0)^2,
\tag{26}
\]

where

\[
 C=(\lambda_+-\lambda_-)
 \max\left\{
 \frac{t}{\lambda_+}+\frac{1-p_+}{p_+(m-1)},
 \frac{t}{\lambda_-}+\frac{1-p_-}{p_-(n-1)}
 \right\}.
\tag{27}
\]

For \(m=n=r\), \(\lambda_+=3\), \(\lambda_-=1/3\), \(s=r\), and
\(4\mid r\), the root in (20) is \(t=1\), \(p_+=3/4\), and
\(C=8r/(r-1)\).

The integrality condition is exact for pairwise cancellation within this
sampler class. If every cross-block pair has \(\pi_{ij}=p_+p_-\), and
\(N_+\) is the first-block count, then

\[
 \mathbb E[N_+(s-N_+)]=mp_+\,np_-
 \quad\Longrightarrow\quad \operatorname{Var}(N_+)=0.
\tag{28}
\]

Hence \(N_+=mp_+\) almost surely, so \(mp_+\in\mathbb Z\). Conversely,
(21) realizes this condition. This is a condition for the declared
inverse-probability sampler and cancellation of every cross-block tangent;
it does not classify all unbiased diagonal estimators.

For contrast, \(q=2\), \(m=n=s=1\) has no nontrivial integral block count.
If \(P_\theta\) projects onto \((\cos\theta,\sin\theta)\) and
\(G=I+\alpha P_\theta\), put \(A=1+\alpha\) and
\(c=|G_{12}|=\alpha|\sin\theta\cos\theta|\). Direct minimization gives

\[
 \Phi_1(G)=\sqrt{A+c^2}+c,\qquad
 \Phi_1(G)-\sqrt A=\Theta(d_c(P_\theta,P_{\{1\}})).
\tag{29}
\]

The low-dimensional case has a linear defect; the integral fixed-count
regime has quadratic cancellation. The volume lower bound remains standard
supporting geometry. Matching upper rates require this sampler design and
its arithmetic condition.
