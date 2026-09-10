# The rank-two spectrahedral benchmark for complex adaptive sampling; depends on query_adaptive_atomic_dual.md, query_adaptive_subspace_containment.md.

Status: an exact rank-reduction formulation. It neither proves the complex
water-level lower bound nor gives a counterexample.

Later resolution: query_adaptive_complex_water_counterexample.md proves
that the proposed universal rank-two objective certificate fails for
G=11^T+eta I_4 at sufficiently small positive eta. Every rank-two feasible
matrix has objective strictly below one, while G/2 has objective one.
The reductions below remain valid; universal existence is now disproved.

Let \(G\succ0\) be real symmetric of size \(4\), let \(s=2\), and define

\[
 K_{ij}=E_{ij}G_{\{i,j\},\{i,j\}}^{-1}E_{ij}^T
 \qquad(1\le i<j\le4).
\tag{1}
\]

Consider the compact spectrahedron

\[
 \mathcal X_G=\{X\succeq0:\operatorname{tr}(K_{ij}X)=1
                        \text{ for all }i<j\}.
\tag{2}
\]

It is nonempty because \(G/2\in\mathcal X_G\). It is compact: the
principal two-by-two blocks satisfy
\(0\preceq X_{\{i,j\},\{i,j\}}\preceq G_{\{i,j\},\{i,j\}}\), since a
positive semidefinite matrix with trace one after congruence by
\(G_{\{i,j\},\{i,j\}}^{-1/2}\) has largest eigenvalue at most one.

## 1. What a rank-two point would prove

If \(X\in\mathcal X_G\) has real rank at most two, write

\[
 X=aa^T+bb^T,\qquad z=a+ib\in\mathbb C^4.
\tag{3}
\]

Every pair then satisfies the complex polar equality

\[
 z_{ij}^*G_{ij}^{-1}z_{ij}
 =\operatorname{tr}(K_{ij}X)=1.
\tag{4}
\]

Let \(t=t_2(G)\) solve

\[
 \sum_{\ell=1}^4{\lambda_\ell(G)\over\lambda_\ell(G)+t}=2.
\tag{5}
\]

If, in addition,

\[
 \operatorname{tr}((G+tI)^{-1}X)\ge1,
\tag{6}
\]

the complex polar test gives \(\Psi_{2,\mathbb C}(G)\ge t\). The reverse
inequality is not automatic for an arbitrary basis, so (6) is only a
lower-benchmark route.

The full-rank point \(G/2\) has exactly the target objective:

\[
 \operatorname{tr}((G+tI)^{-1}G/2)=1.
\tag{7}
\]

Thus the unresolved issue is not feasibility of (2), but whether its
water-level objective admits a rank-two point of value at least one.

## 2. A concrete finite algebraic reduction

Write \(g_{ij}=G_{ij}\) and \(x_i=X_{ii}\). If every off-diagonal
\(g_{ij}\) is nonzero, each equality in (2) determines the corresponding
off-diagonal entry of \(X\):

\[
 X_{ij}={g_{jj}x_i+g_{ii}x_j-
                 (g_{ii}g_{jj}-g_{ij}^2)\over2g_{ij}}.
\tag{8}
\]

Consequently \(\mathcal X_G\) is an affine four-parameter family before
the positive-semidefinite condition. A rank-two solution must make all
three-by-three minors of the matrix obtained from (8) vanish, while
retaining positivity and (6). This is a finite real algebraic problem in
the four diagonal variables. The dimension count gives no existence result:
the rank-two locus has codimension three in the ten-dimensional symmetric
matrix space, but the six affine equations are special and may meet it
nontransversely or miss it.

When some \(g_{ij}=0\), equation (8) is replaced by a constraint on
\(x_i,x_j\) and leaves \(X_{ij}\) free. This is the diagonal-type regime
where explicit complex phase constructions can be available; it cannot be
used to infer the generic case.

## 3. Why standard rank bounds do not settle the issue

The real Pataki bound applied to an extreme point of (2) gives only

\[
 r(r+1)/2\le6,\qquad r\le3.
\tag{9}
\]

Maximizing the objective in (6) can add one active affine constraint, so
the same conclusion remains rank at most three. Rank three is insufficient
for the representation (3).

Using a complex Hermitian SDP does not repair this gap. Its complex Pataki
bound can give a rank-two Hermitian optimizer from six real equalities, but
a rank-two Hermitian matrix is a sum of two complex rank-one factors. Its
real part can have real rank four and need not equal \(aa^T+bb^T\) for one
complex vector \(a+ib\). The complex polar witness required in (4)
corresponds to a *real* rank-two matrix, or equivalently one complex vector,
not merely a complex rank-two SDP solution.

Therefore no standard rank-reduction theorem presently supplies the needed
rank-two point. A valid proof must use the special pair-principal-inverse
structure in (1), solve the algebraic system (8), or exhibit a real \(G\)
for which that system has no positive rank-two point satisfying (6).
