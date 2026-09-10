# Anisotropic variance sublevels on \(\operatorname{Gr}_{\mathbb F}(2,4)\)

Status: a local fixed-basis description result. It does not establish a
general Cassette lower bound or an originality claim.

## 1. Statement

Let \(\mathbb F\) be \(\mathbb R\) or \(\mathbb C\), put

\[
 G_P=\tfrac13 I+\tfrac83P,\qquad
 P\in\operatorname{Gr}_{\mathbb F}(2,4),
\tag{1}
\]

and let \(\Phi_2(G_P)\) be the least fixed-coordinate diagonal-thinning
variance with at most two selected columns. The unrestricted spectral
water level is \(t=1\), since the eigenvalues \(3,3,1/3,1/3\) obey

\[
 2\frac3{3+1}+2\frac{1/3}{1/3+1}=2.
\tag{2}
\]

At \(P_0=\operatorname{Diag}(1,1,0,0)\), use the graph chart

\[
 P(B)=
 \begin{pmatrix}
 (I+B^*B)^{-1}&(I+B^*B)^{-1}B^*\\
 B(I+B^*B)^{-1}&B(I+B^*B)^{-1}B^*
 \end{pmatrix},
 \qquad B\in\mathbb F^{2\times2}.
\tag{3}
\]

Write \(D(B)\) and \(O(B)\) for the diagonal and off-diagonal parts of
\(B\), respectively. There are positive constants \(c,C,\eta\), depending
only on the field, such that, for \(\lVert B\rVert_F<\eta\),

\[
 c\left(\lVert B\rVert_F^2+
 \min\{\lVert D(B)\rVert_F,\lVert O(B)\rVert_F\}\right)
 \leq\Phi_2(G_{P(B)})-1
\tag{4}
\]

\[
 \leq
 C\left(\lVert B\rVert_F^2+
 \min\{\lVert D(B)\rVert_F,\lVert O(B)\rVert_F\}\right).
\tag{5}
\]

Thus the first-order zero cone has two transverse branches in this chart:
one with \(B\) diagonal and one with \(B\) antidiagonal. Along either branch
the excess is quadratic; generic directions have a linear excess.

## 2. The two exact capped laws

At \(P_0\), the water-level marginals are

\[
 p=(3/4,3/4,1/4,1/4).
\tag{6}
\]

Every law on two-element subsets with these marginals has pair
probabilities

\[
 \begin{array}{c|cccccc}
 \{i,j\}&12&34&13&24&14&23\\ \hline
 q_{ij}&1/2+y&y&z&z&1/4-y-z&1/4-y-z,
 \end{array}
\tag{7}
\]

where \(y\geq0\) and \(0\leq z\leq1/4-y\). This follows by solving the
four marginal equations; the total-probability equation follows from their
sum.

For a selected subset \(S\), use the diagonal Horvitz--Thompson estimator

\[
 Z_S=\sum_{i\in S}\frac{R_i e_i^*}{p_i},
 \qquad R^*R=G_{P(B)}.
\tag{8}
\]

It has exactly two selected columns and \(\mathbb E Z_S=R\). Its covariance
\(C=\mathbb E Z_S^*Z_S-G_{P(B)}\) has entries

\[
 C_{ii}=G_{ii}(p_i^{-1}-1),\qquad
 C_{ij}=G_{ij}\left(\frac{q_{ij}}{p_ip_j}-1\right).
\tag{9}
\]

The unnormalized cross-block coefficients, before division by
\(p_ip_j=3/16\), are

\[
 M(y,z)=
 \begin{pmatrix}
 z-3/16&1/16-y-z\\
 1/16-y-z&z-3/16
 \end{pmatrix}.
\tag{10}
\]

The choice \((y,z)=(0,3/16)\) makes the diagonal entries of \(M\) zero.
The choice \((y,z)=(0,1/16)\) makes its off-diagonal entries zero. Since

\[
 G_{P(B),\,\{1,2\},\,\{3,4\}}
 =\tfrac83B^*+O(\lVert B\rVert_F^3)
\tag{11}
\]

and all within-block off-diagonal entries and diagonal changes are
\(O(\lVert B\rVert_F^2)\), (9) gives the two bounds

\[
 \Phi_2(G_{P(B)})-1
 \leq C\left(\lVert B\rVert_F^2+\lVert O(B)\rVert_F\right),
\tag{12}
\]

\[
 \Phi_2(G_{P(B)})-1
 \leq C\left(\lVert B\rVert_F^2+\lVert D(B)\rVert_F\right).
\tag{13}
\]

This proves (5).

## 3. Why no third first-order branch exists

Let

\[
 \delta=\Phi_2(G_{P(B)})-1,\qquad h=\lVert B\rVert_F.
\]

Take an arbitrarily near-optimal diagonal estimator and write it as
\(Z=R\operatorname{Diag}(\xi)\). Let \(I_i=\mathbf1_{\{\xi_i\ne0\}}\),
\(\theta_i=\mathbb E I_i\), and \(q_{ij}=\mathbb E I_iI_j\). The hard cap
is \(\sum_iI_i\leq2\).

The diagonal covariance inequality and Cauchy--Schwarz give

\[
 \mathbb E|\xi_i|^2\geq\theta_i^{-1},\qquad
 \theta_i\geq p_i-O(\delta+h^2).
\tag{14}
\]

Because \(\sum_i\theta_i\leq2=\sum_ip_i\), this implies

\[
 \theta_i=p_i+O(\delta+h^2),\qquad
 \mathbb E(2-\textstyle\sum_i I_i)=O(\delta+h^2).
\tag{15}
\]

The same diagonal estimates give the Cauchy defects

\[
 \mathbb E\left|\xi_i-\frac{I_i}{\theta_i}\right|^2
 =\mathbb E|\xi_i|^2-\theta_i^{-1}
 =O(\delta+h^2).
\tag{16}
\]

Consequently, the pair moments satisfy

\[
 \mathbb E(\overline{\xi_i}\xi_j)
 =\frac{q_{ij}}{\theta_i\theta_j}+O(\sqrt{\delta+h^2}).
\tag{17}
\]

Equations (15) and the almost-full two-element support imply that the
cross-block matrix \((q_{ij})\) differs entrywise by
\(O(\delta+h^2)\) from a matrix of the form (7). This is only a four-variable
linear calculation: solve the marginal equations after charging every
missing selected slot to the error in (15).

Let \(C=\mathbb E Z^*Z-G_{P(B)}\). Since
\(\lambda_{\max}(C)\leq1+\delta\),

\[
 S=(1+\delta)I-C\succeq0.
\tag{18}
\]

The lower diagonal bounds from (14)--(16) yield
\(S_{ii}=O(\delta+h^2)\). Hence

\[
 \lVert C_{\{1,2\},\{3,4\}}\rVert_{\mathrm{op}}
 \leq O(\delta+h^2).
\tag{19}
\]

Combining (10), (11), and (17)--(19) gives, for some admissible \(y,z\),

\[
 \lVert M(y,z)\circ B\rVert_F
 \leq C\bigl(\delta+h^2+h\sqrt{\delta+h^2}+h^3\bigr).
\tag{20}
\]

Here \(\circ\) denotes entrywise multiplication. Since

\[
 |(z-3/16)+(1/16-y-z)|=1/8+y\geq1/8,
\tag{21}
\]

either the common diagonal coefficient of \(M\) or its common
off-diagonal coefficient has magnitude at least \(1/16\). Therefore

\[
 \min\{\lVert D(B)\rVert_F,\lVert O(B)\rVert_F\}
 \leq16\lVert M(y,z)\circ B\rVert_F.
\tag{22}
\]

The quantitative rigidity bound in coded_basis_rigidity.md is uniform
on this compact orbit. Together with (11), it gives

\[
 \delta\geq c_0h^2.
\tag{23}
\]

Insert (23) into (20)--(22), shrinking the chart if necessary. This gives

\[
 \min\{\lVert D(B)\rVert_F,\lVert O(B)\rVert_F\}\leq C_0\delta.
\tag{24}
\]

Equations (23) and (24) prove (4). The argument also identifies the
obstruction: the exact two-column cap makes cross-block pairwise
independence impossible for all four cross edges, because the expected
upper-block count is \(3/2\), not an integer.

## 4. Haar volume and finite transform libraries

Put \(\beta=1\) over \(\mathbb R\) and \(\beta=2\) over \(\mathbb C\).
The diagonal and off-diagonal parts of \(B\) each have real dimension
\(2\beta\). By (4)--(5), the local sublevel set

\[
 \{\Phi_2(G_{P(B)})-1\leq\varepsilon\}
\tag{25}
\]

is, up to constant dilations, the union of two product sets:

\[
 \{\lVert D(B)\rVert_F\lesssim\varepsilon,\ 
   \lVert O(B)\rVert_F\lesssim\sqrt\varepsilon\}
\tag{26}
\]

and the same set with \(D\) and \(O\) exchanged. Each has Lebesgue volume
\(\Theta(\varepsilon^{3\beta})\). The graph-chart Haar density is smooth
and strictly positive at zero. Hence the local Haar volume is

\[
 \Theta(\varepsilon^{3\beta}).
\tag{27}
\]

The six coordinate rank-two projections are the only zero-variance-excess
points by fixed-basis rigidity. Compactness and (23) put every sufficiently
small global sublevel set into their coordinate charts. Thus its total Haar
volume is also \(\Theta(\varepsilon^{3\beta})\).

For a declared library of \(K\) orthogonal or unitary transforms to achieve
\(\Phi_2(V_j^*G_PV_j)\leq1+\varepsilon\) for every \(P\), Haar measure
therefore gives the necessary condition

\[
 K\geq c\,\varepsilon^{-3\beta}.
\tag{28}
\]

This is a fixed finite-library cardinality statement only. It does not
count the physical storage, decoder, or selection metadata of a transform.

There is also a standard probabilistic covering upper bound

\[
 K=O\!\left(\varepsilon^{-3\beta}\log\frac1\varepsilon\right).
\tag{29}
\]

To see it, use a fixed inner version of either product set in (26). A Haar
random transform places its associated coordinate projection uniformly on
the Grassmannian, so it covers a fixed point with probability
\(\Theta(\varepsilon^{3\beta})\). Cover the compact Grassmannian first by
an ordinary \(O(\varepsilon)\)-net, of size
\(O(\varepsilon^{-4\beta})\). If every net point lies in an inner product
set, the margin in its thin direction extends coverage to its
\(O(\varepsilon)\)-ball. A union bound over that net gives (29).

The exponent \(3\beta\) is exact for the sublevel volume. Whether the
logarithm in this elementary library construction can be removed requires
a sharper covering construction; it is not settled here.
