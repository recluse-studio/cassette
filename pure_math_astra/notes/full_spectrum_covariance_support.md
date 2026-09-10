# Covariance-support topology under an exact subset cap

This note gives a support-graph lower bound for an exactly-\(s\) Bernoulli
subset law, an open simple-spectrum five-coordinate realization, and a
scalable balanced cycle realization. It does not claim a byte bound, a general
minimum-support formula, or novelty.

Let \(X_i=\mathbf1\{i\in S\}\), where \(|S|=s\) almost surely and

\[
 0<p_i=\mathbb EX_i<1.
\]

Let \(H\) be the covariance-support graph: \(ij\) is an edge exactly when
\(\operatorname{Cov}(X_i,X_j)\ne0\). Write \(k=|E(H)|\).

## 1. The leaf rule

**Theorem 1.** If \(i\) is a leaf of \(H\), with unique neighbor \(j\), then

\[
 p_i+p_j=1,\qquad X_i+X_j=1\quad\text{almost surely}, \tag{1}
\]

and \(j\) is also a leaf. Hence every component of \(H\) with at least three
vertices has minimum degree at least two.

**Proof.** The fixed-sum identity \(\sum_\ell X_\ell=s\) gives

\[
 0=\operatorname{Cov}\left(X_i,\sum_\ell X_\ell\right)
 =p_i(1-p_i)+\operatorname{Cov}(X_i,X_j).
\]

Thus

\[
 \operatorname{Cov}(X_i,X_j)=-p_i(1-p_i). \tag{2}
\]

Every Bernoulli covariance is at least
\(-\min\{p_ip_j,(1-p_i)(1-p_j)\}\). Applying this to (2) yields both
\(p_j\geq1-p_i\) and \(p_j\leq1-p_i\), proving the first equality in (1).
The pair probability is then zero, so \(X_i+X_j\) cannot equal two. It is
therefore \(\{0,1\}\)-valued with expectation one and equals one almost surely.
For \(\ell\notin\{i,j\}\),

\[
 \operatorname{Cov}(X_j,X_\ell)
 =-\operatorname{Cov}(X_i,X_\ell)=0,
\]

so \(j\) has no neighbor other than \(i\). \(\square\)

Let \(M\) be the maximum number of disjoint coordinate pairs \(ij\) with
\(p_i+p_j=1\). The leaf rule gives the structural lower bound

\[
 k\geq q-M. \tag{3}
\]

Indeed, if there are \(r\) two-vertex components, then \(r\leq M\). Every
remaining component has at least three vertices and at least as many edges as
vertices; isolated vertices are impossible because their variance is positive.
Therefore \(k\geq r+(q-2r)=q-r\geq q-M\).

For a generic simple spectrum, no two inclusion probabilities are
complementary, so \(M=0\) and \(k\geq q\). Simple eigenvalues alone do not
exclude a complementary pair; the genericity condition is needed.

## 2. A sharp open simple-spectrum family at \(q=5\), \(s=2\)

Index coordinates modulo five and take \(p_i\) in a sufficiently small
neighborhood of \(2/5\), subject to \(\sum_i p_i=2\). For the cycle edge
\(e_i=\{i,i+1\}\), define

\[
 b_i=p_i(1-p_i),
 \qquad
 w_i=\frac{b_i-b_{i-1}+b_{i-2}-b_{i-3}+b_{i-4}}2. \tag{4}
\]

Then \(w_{i-1}+w_i=b_i\). Define a law on the two-subsets by

\[
 \Pr(\{i,j\})=
 \begin{cases}
 p_ip_j-w_i,&\{i,j\}=e_i,\\
 p_ip_j,&\{i,j\}\text{ is not a cycle edge}.
 \end{cases} \tag{5}
\]

At \(p_i=2/5\), one has \(w_i=3/25\), cycle-pair probability \(1/25\), and
noncycle-pair probability \(4/25\). All ten probabilities are strictly
positive. By continuity, (5) remains nonnegative in a relative open
neighborhood of the uniform vector.

The row sum at coordinate \(i\) is

\[
 p_i\sum_{j\ne i}p_j-w_{i-1}-w_i
 =p_i(2-p_i)-p_i(1-p_i)=p_i.
\]

Thus the probabilities sum to one and have the stated marginals. Their
covariance vanishes off the cycle and equals \(-w_i\) on every cycle edge.
Choose a point in this neighborhood with all \(p_i\) distinct and no pair
summing to one. Then (3) gives \(k\geq5\), while (5) gives \(k=5\).

For a fixed \(t>0\), the diagonal values

\[
 a_i=\frac{tp_i}{1-p_i}
\]

are also distinct. Hence this is an open full-simple-spectrum diagonal family
for which the lower bound (3) is sharp.

## 3. A sharp open simple-spectrum family at \(q=7\), \(s=3\)

The same phenomenon occurs at a moderate cap. Set \(p_i=3/7\) and index
coordinates modulo seven. Let \(\mathcal O_0,\ldots,\mathcal O_4\) be the
rotation orbits of the triples

\[
 \{0,1,2\},\quad \{0,1,3\},\quad \{0,1,4\},\quad
 \{0,1,5\},\quad \{0,2,4\},
\]

respectively. Give the five orbits total masses

\[
 \frac1{35},\qquad \frac3{70},\qquad \frac{11}{35},\qquad
 \frac1{70},\qquad \frac35, \tag{6}
\]

and distribute each mass uniformly over its seven rotations. Every one of the
35 triples has positive probability. Direct cyclic counting gives

\[
 \Pr(i\in S)=\frac37,
 \qquad
 \Pr(i,i+1\in S)=\frac3{49},
 \qquad
 \Pr(i,j\in S)=\frac9{49}\quad(j-i\not\equiv\pm1).
 \tag{7}
\]

Thus the covariance is \(-6/49\) on the seven-cycle and zero off it.

This realization persists under arbitrary sufficiently small changes of the
marginal vector with \(\sum_i p_i=3\). To make that statement exact, impose
normalization, the first six marginals, and the 14 noncycle pair moments. The
resulting \(21\times35\) incidence matrix has rank 21. One explicit
unit-determinant minor uses the 21 columns

\[
 \begin{gathered}
012,013,014,015,016,023,024,025,026,034,035,036,045,046,056,\\
123,124,125,126,134,234,
 \end{gathered} \tag{8}
\]

where a string denotes its three-subset. The sole affine relation among the
22 moments before omitting the seventh marginal is
\(\sum_i p_i=3\). Keep the probability of every nonselected column in (8)
fixed, and solve the selected 21 probabilities through this invertible minor.
Since (6) is strictly positive on every triple, the solution remains positive
for every sufficiently small target perturbation.

For a nearby vector with distinct \(p_i\), no complementary pair, and
nonzero cycle covariances, prescribe every noncycle pair moment as \(p_ip_j\).
The preceding argument produces an exact-three subset law with covariance
support \(C_7\). The lower bound (3) has \(M=0\), so

\[
 k=7
\]

on this open full-simple-spectrum family. With \(a_i=tp_i/(1-p_i)\) for
fixed \(t>0\), these distinct marginal values give a simple diagonal spectrum.

## 4. A scalable moderate-cap cycle realization

The five-coordinate family uses \(s=2\). A different construction shows that
a cycle-only covariance pattern is nevertheless realizable at arbitrary
balanced exact caps.

Let \(q=2s\ge4\) and \(p_i=1/2\). On the cycle \(C_q\), let

\[
 M_0=\{\{0,1\},\{2,3\},\ldots,\{q-2,q-1\}\},
\]

and let \(M_1\) be its one-step rotation. Choose \(M_0\) or \(M_1\) with
probability \(1/2\). Independently choose one endpoint from every matched
pair. This always selects exactly \(s\) coordinates.

Every coordinate has marginal \(1/2\). A cycle edge belongs to one matching:
its pair probability is zero under that matching and \(1/4\) under the other,
so its covariance is \(-1/8\). Any noncycle pair lies in distinct matching
pairs under both choices, so its pair probability is \(1/4\) and its
covariance vanishes. Therefore

\[
 H=C_q,\qquad k=q. \tag{9}
\]

This construction has complementary marginals along matching edges and does
not minimize support: the matching-only law has support \(q/2\). Its role is
to establish exact realizability of the cycle covariance geometry at arbitrary
moderate exact caps. Perturbing it to a generic simple spectrum is a separate
problem; the matching mixture itself does not supply such a perturbation.

## 5. A boundary for the \(s=2\) uniform cycle ansatz

For \(s=2\), \(p_i=2/q\), and a \(d\)-regular covariance-support graph with
equal negative covariance on each support edge, exact row sums force

\[
 \operatorname{Cov}(X_i,X_j)=-\frac{p(1-p)}d
 \quad\text{on each support edge}.
\]

The associated pair probability is nonnegative only if

\[
 d\geq\frac{1-p}{p}=\frac q2-1. \tag{10}
\]

For a cycle, \(d=2\); (10) holds only when \(q\leq6\). Thus the five-cycle
construction cannot extend as a uniform two-read cycle construction to larger
odd dimensions. This is a nonnegativity obstruction, not merely a failure of
the covariance matrix to be PSD.
