# Fixed-basis equality as an edge-independence design

This note studies an ideal fixed encoded-input basis. It proves an exact
attainment criterion for the marginal lower bound in
`coded_basis_rigidity.md`, then gives one graph obstruction and one small
counterexample to a tempting matching characterization. It does not assert
novelty, a finite-byte encoding bound, or an unrestricted Cassette lower bound.

Let \(R\in\mathbb F^{p\times q}\) have full column rank, put
\(G=R^*R\succ0\), and fix \(1\leq s<q\). An outcome has the form

\[
 Z_b=RD_b,\qquad D_b=\operatorname{Diag}(b_1,\ldots,b_q),
 \qquad |\operatorname{supp}b|\leq s,
\]

with \(\mathbb ED_b=I\). The weights may be complex and may depend on the
whole selected support. Let

\[
 \Phi_s(G)=\inf\lambda_{\max}\bigl(\mathbb E[D_b^*GD_b]-G\bigr).
\]

Write \(a_i=G_{ii}\), and let \(u>0\) solve

\[
 \sum_{i=1}^q\theta_i=s,
 \qquad \theta_i=\frac{a_i}{a_i+u}. \tag{1}
\]

The marginal argument gives \(\Phi_s(G)\geq u\). Let \(E(G)\) be the
nonzero off-diagonal support graph: \(ij\in E(G)\) exactly when \(i\ne j\)
and \(G_{ij}\ne0\).

## 1. Exact equality criterion

**Theorem 1.** The following are equivalent.

1. \(\Phi_s(G)=u\).
2. There is a random exactly-\(s\) subset \(S\subseteq[q]\) such that

   \[
   \Pr(i\in S)=\theta_i,
   \qquad
   \Pr(i,j\in S)=\theta_i\theta_j\quad(ij\in E(G)). \tag{2}
   \]

When either condition holds, every optimal fixed-basis law has, almost surely,

\[
 b_i=\frac{\mathbf1\{i\in S\}}{\theta_i}, \tag{3}
\]

for a subset law satisfying (2). Thus arbitrary complex and
support-dependent weights supply no additional equality cases.

**Proof.** The fixed-basis problem attains its infimum: conditional averaging
on each of its finitely many legal supports does not increase the second
moment in PSD order, and the resulting finite semidefinite formulation is
closed and level-bounded. This is proved in
`coded_basis_rigidity.md`.

Suppose an attaining law has covariance

\[
 Q=\mathbb E[D_b^*GD_b]-G\preceq uI.
\]

Put \(\vartheta_i=\Pr(b_i\ne0)\). Since each outcome has at most \(s\)
nonzero entries,

\[
 \sum_i\vartheta_i\leq s. \tag{4}
\]

Cauchy--Schwarz and \(\mathbb Eb_i=1\) give

\[
 \mathbb E|b_i|^2\geq\frac1{\vartheta_i}.
\]

The \(i\)-th diagonal inequality in \(Q\preceq uI\) therefore implies

\[
 u\geq a_i\bigl(\mathbb E|b_i|^2-1\bigr)
 \geq a_i\left(\frac1{\vartheta_i}-1\right),
 \qquad
 \vartheta_i\geq\theta_i. \tag{5}
\]

Equations (1), (4), and (5) force \(\vartheta_i=\theta_i\) for every \(i\),
and all preceding inequalities are equalities. Equality in Cauchy--Schwarz
forces \(b_i\) to be the constant \(1/\theta_i\) on \(\{b_i\ne0\}\). In
particular, these constants are positive real even when complex weights were
allowed. Also \(\mathbb E|\operatorname{supp}b|=s\), so the support has
exactly \(s\) elements almost surely.

Now \(Q_{ii}=u\) for every \(i\). Since \(uI-Q\succeq0\) has zero diagonal,
it is the zero matrix. Hence \(Q=uI\). For \(i\ne j\), (3) gives

\[
 Q_{ij}=G_{ij}\left(
 \frac{\Pr(i,j\in S)}{\theta_i\theta_j}-1\right).
\]

For every Gram edge this vanishes precisely when (2) holds. This proves
necessity.

Conversely, a subset law satisfying (2), with the weights in (3), is unbiased,
has rank exactly \(s\), and has covariance diagonal entries

\[
 a_i\left(\frac1{\theta_i}-1\right)=u.
\]

Its off-diagonal covariance is zero on every nonzero Gram entry by (2), and
is automatically zero where \(G_{ij}=0\). Thus \(Q=uI\), so
\(\Phi_s(G)\leq u\). The marginal lower bound gives equality. \(\square\)

The theorem reduces equality to a finite moment-polytope membership question.
This is an exact reformulation, not by itself a new combinatorial theorem:
there are \(\binom qs\) subset probabilities and the equations in (2).

## 2. Uniform energies and balanced signs

Suppose \(q=2s\) and \(a_i=a\) for all \(i\). Then \(u=a\) and
\(\theta_i=1/2\). With

\[
 Y_i=2\mathbf1\{i\in S\}-1,
\]

condition (2) becomes

\[
 Y_i\in\{-1,1\},\qquad \sum_iY_i=0\ \text{almost surely},\qquad
 \mathbb EY_i=0,\qquad \mathbb E(Y_iY_j)=0\quad(ij\in E(G)). \tag{6}
\]

Equivalently, the zero vector on the edge coordinates must belong to the edge
projection of the balanced cut-moment polytope

\[
 \operatorname{conv}\{(y_iy_j)_{ij\in E(G)}:
 y\in\{-1,1\}^q,\ \mathbf1^Ty=0\}. \tag{7}
\]

Formula (7) is useful for exact finite linear programming and dual separating
certificates. It is a translation of Theorem 1, so it is not claimed here as
an advance in cut-polytope theory.

### A sufficient matching construction

Let \(H=\overline{E(G)}\) be the graph of Gram nonedges. If \(H\) has a
perfect matching, independently select one endpoint from each matching pair.
Every selected set has size \(s\), every vertex has marginal \(1/2\), and
any Gram edge joins two different matching pairs. Its endpoints are therefore
independent. By Theorem 1, \(\Phi_s(G)=a\).

### Perfect matching is not necessary

A fourteen-coordinate parity construction in
`balanced_support_pair_designs.md` already proves this point. The following
six-coordinate construction is a smaller, differently structured witness.
Take \(q=6\), \(s=3\), and name the vertices \(a,b,1,2,3,4\). Let the Gram
support graph be the clique on \(\{1,2,3,4\}\), with \(a\) and \(b\)
isolated. Its nonedge graph \(H\) contains \(ab\) and all eight edges from
\(\{a,b\}\) to \(\{1,2,3,4\}\), and contains no leaf--leaf edge. It has no
perfect matching: four leaves can be matched only to the two vertices \(a,b\).

Nevertheless, use this exactly-three-subset law:

- with probability \(1/2\), take \(\{a,b\}\) together with a uniformly
  chosen one of \(\{1,2,3,4\}\);
- with probability \(1/2\), take a uniformly chosen three-subset of
  \(\{1,2,3,4\}\).

Every vertex has marginal \(1/2\). A pair of leaves occurs together only in
the second branch, where its conditional probability is \(1/2\); hence its
unconditional probability is \(1/4\). These are all Gram edges, so Theorem 1
applies.

For a concrete positive-definite Gram matrix, take

\[
 G_\epsilon=I_6+\epsilon\begin{pmatrix}0_{2\times2}&0\\0&A_{K_4}\end{pmatrix},
 \qquad 0<\epsilon<\frac13.
\]

It has uniform diagonal, the required support graph, and \(\Phi_3(G_\epsilon)=1\).
Thus absence of a perfect matching in the Gram-nonedge graph is not an
impossibility criterion.

## 3. A sharp clique obstruction

The preceding example is a warning against matching necessity. A different
constraint is exact and applies to every graph containing a large clique.

**Theorem 2.** Assume \(q=2s\), \(a_i=a\), and equality \(\Phi_s(G)=a\).
If \(E(G)\) contains a clique \(C\) of size \(m\), put

\[
 L=\max(0,m-s),\qquad U=\min(m,s).
\]

Then

\[
 \frac m4\leq\left(U-\frac m2\right)\left(\frac m2-L\right). \tag{8}
\]

In particular, if \(m>s\), equality is impossible whenever

\[
 m>(2s-m)^2. \tag{9}
\]

For the graph consisting of this \(m\)-clique and \(2s-m\) isolated
vertices, condition (8) is also sufficient. Thus (8) is a sharp obstruction
for that graph family.

**Proof.** Under equality, Theorem 1 supplies a balanced subset law. Let
\(K=|S\cap C|\). The marginal and pair constraints on the clique give

\[
 \mathbb EK=\frac m2,
 \qquad
 \mathbb E[K(K-1)]=\frac{m(m-1)}4,
 \qquad
 \operatorname{Var}K=\frac m4. \tag{10}
\]

Because \(|S|=s\), the integer \(K\) lies in \([L,U]\). The elementary
bounded-variable variance bound gives

\[
 \operatorname{Var}K\leq(U-\mathbb EK)(\mathbb EK-L),
\]

which is (8). If \(m>s\), the right side is \((2s-m)^2/4\), giving (9).

For sharpness in the clique-plus-isolates graph, the feasible distributions on
integers \(K\in[L,U]\) with mean \(m/2\) form a convex set. At this fixed
mean, their variances fill the interval from the minimum discrete variance to
the endpoint variance on the right side of (8). The target \(m/4\) is at
least the minimum: it is \(0\) when \(m\) is even and \(1/4\) when \(m\) is
odd. Thus (8) supplies a law for \(K\) with the moments in (10). Conditional
on \(K\), select a uniform \(K\)-subset of \(C\) and a uniform
\((s-K)\)-subset of the isolates. The marginal and pair calculations reverse
(10), so all clique vertices have marginal \(1/2\) and all clique pairs have
joint probability \(1/4\). The isolates also have marginal \(1/2\). Theorem
1 now proves equality. \(\square\)

## 4. Cassette scope and remaining question

Theorems 1 and 2 concern the ideal model in which a declared encoded basis is
fixed, each execution reads at most \(s\) encoded columns, and no cost is
assigned to the basis transform or its evaluation. They establish an exact
access-cap boundary inside that model: equality in the marginal lower bound is
controlled by edge-local pairwise independence, and a sufficiently dominant
correlated clique forbids it.

They do not state what transform can be stored in Cassette's resident-byte
class, how its query transform is evaluated, or whether the fixed-basis model
is the right restriction for a given atom. A consequential next question is to
prove a comparable obstruction for a declared finite-byte transform family.
Without such a result, this remains a structural result about one encoded-basis
access class rather than a general Cassette resource law.
