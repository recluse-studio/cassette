# Two-block designs with one exceptional cross pair

This note studies a bounded combinatorial problem arising in the fixed encoded
basis equality criterion. It proves an exact classification for the first
nontrivial case \(m=n=s=3\). It does not claim a general two-block theorem,
finite-byte transform result, or novelty.

Let \(A\) and \(B\) be disjoint coordinate blocks of sizes \(m\) and \(n\).
A random subset \(S\) always has size \(s\), and each coordinate in \(A\) has
marginal \(p\), while each coordinate in \(B\) has marginal \(r\), where

\[
 mp+nr=s. \tag{1}
\]

Fix distinguished coordinates \(a_0\in A\) and \(b_0\in B\). The design
condition is

\[
 \Pr(i,j\in S)=pr
 \quad(i\in A,\ j\in B,\ (i,j)\ne(a_0,b_0)). \tag{2}
\]

The pair \((a_0,b_0)\) is unconstrained. In the fixed-basis Gram problem,
(2) is exactly the condition that every nonzero cross-block Gram entry except
one has zero covariance at the marginal lower bound.

## 1. A general count identity

Let \(K=|S\cap A|\), and let \(X=\mathbf1\{a_0\in S\}\) and
\(Y=\mathbf1\{b_0\in S\}\). Since \(|S|=s\), summing the cross-block
covariances in (2) gives

\[
 \operatorname{Cov}(X,Y)=-\operatorname{Var}K. \tag{3}
\]

Consequently

\[
 \Pr(a_0,b_0\in S)=pr-\operatorname{Var}K. \tag{4}
\]

If \(f\) is the fractional part of \(mp\), integrality of \(K\) and the
Fréchet bounds for the exceptional Bernoulli pair imply the necessary bounds

\[
 f(1-f)\leq \operatorname{Var}K
 \leq \min\{pr,(1-p)(1-r)\}. \tag{5}
\]

**Proof.** All cross covariances except \(\operatorname{Cov}(X,Y)\) vanish.
Their sum is

\[
 \operatorname{Cov}(|S\cap A|,|S\cap B|)
 =\operatorname{Cov}(K,s-K)=-\operatorname{Var}K,
\]

which proves (3) and (4). An integer-valued random variable of mean \(mp\)
has variance at least \(f(1-f)\). Equation (4) must lie in the interval
\([\max(0,p+r-1),\min(p,r)]\), which gives the upper bound in (5). \(\square\)

The bounds are not sufficient. The classification below gives an exact small
counterexample: for \(p=3/5\), \(r=2/5\), they only require
\(4/25\leq\operatorname{Var}K\leq6/25\), yet no design exists.

## 2. Exact \(3+3\) classification

**Theorem.** Let \(m=n=s=3\), \(r=1-p\), and impose (2) on the eight
cross pairs other than \((a_0,b_0)\). Such a subset law exists if and only if

\[
 p\in\left\{0,\frac13,\frac12,\frac23,1\right\}. \tag{6}
\]

In particular, there is no law with \(p=3/5\) and \(r=2/5\).

### Orbit reduction

The condition is invariant under permutations of the two nondistinguished
coordinates in each block. Average any feasible law over those permutations.
It is therefore enough to assign probabilities \(z_{xiyj}\) to the ten
orbits

\[
 (x,i,y,j)\in\{0,1\}\times\{0,1,2\}\times\{0,1\}\times\{0,1,2\},
 \qquad x+i+y+j=3,
\]

where \(x=\mathbf1\{a_0\in S\}\), \(i=|S\cap(A\setminus\{a_0\})|\),
and similarly \(y,j\) describe block \(B\). Within an orbit, use the uniform
law on its coordinates.

The normalization, marginal, and eight pair equations reduce to

\[
 \mathbb Ex=p,\quad \mathbb Ei=2p,\quad
 \mathbb Ey=1-p,\quad \mathbb Ej=2(1-p),
\]

and

\[
 \mathbb E(xj/2)=p(1-p),\quad
 \mathbb E(iy/2)=p(1-p),\quad
 \mathbb E(ij)=4p(1-p), \tag{7}
\]

together with \(\sum z_{xiyj}=1\). Their coefficient matrix has rank
seven. Row reduction gives the following complete parameterization. Set

\[
 u=z_{1101},\qquad v=z_{1110},\qquad w=z_{1200}.
\]

The remaining orbit probabilities are

\[
\begin{array}{c|c}
\text{orbit}&\text{probability}\\ \hline
0012&1-4p+3p^2+(u+v)/2\\
0102&2p^2-u-2v-2w\\
0111&4p-8p^2+u+2v+4w\\
0201&v\\
0210&-p+3p^2-u/2-3v/2-2w\\
1002&p-2p^2+v+w\\
1011&2p^2-u-2v-2w\\
1101&u\\
1110&v\\
1200&w.
\end{array} \tag{8}
\]

Thus feasibility is exactly nonnegativity of the ten quantities in (8). This
is a rational finite orbit calculation, not a numerical inference.

### Excluding all other values of \(p\)

If \(0<p<1/3\), the \(0210\) entry in (8) is strictly negative because

\[
 -p+3p^2-u/2-3v/2-2w<0.
\]

For \(1/2<p<2/3\), nonnegativity of the \(0012\), \(0102\), and \(1002\)
entries gives respectively

\[
 \begin{aligned}
 u+v&\geq-2+8p-6p^2,\\
 u+2v+2w&\leq2p^2,\\
 v+w&\geq2p^2-p.
 \end{aligned} \tag{9}
\]

The first two inequalities imply

\[
 v+2w\leq2-8p+8p^2,
\]

while the third gives \(v+2w\geq2p^2-p\). Compatibility would require

\[
 6p^2-7p+2=6\left(p-\frac12\right)
 \left(p-\frac23\right)\geq0,
\]

which is false in that interval. Swapping the two blocks replaces \(p\) by
\(1-p\), excluding \(1/3<p<1/2\) and \(2/3<p<1\) as well.

### Constructions at the five feasible values

The endpoint laws are deterministic: select all of \(B\) for \(p=0\), or
all of \(A\) for \(p=1\). For \(p=1/3\), independently select a uniform
one-subset of \(A\) and a uniform two-subset of \(B\). For \(p=2/3\),
interchange the block roles. These designs make all nine cross pairs
independent.

For \(p=1/2\), use the following eight equally likely outcomes. With
probability \(1/2\), select \(b_0\), one uniformly chosen member of
\(A\setminus\{a_0\}\), and one uniformly chosen member of
\(B\setminus\{b_0\}\). With probability \(1/2\), select \(a_0\), one
uniformly chosen member of \(A\setminus\{a_0\}\), and one uniformly chosen
member of \(B\setminus\{b_0\}\). All marginals equal \(1/2\); every
cross pair except \((a_0,b_0)\) has joint probability \(1/4\), while the
exceptional pair has joint probability zero. This proves (6). \(\square\)

## 3. Fixed-basis consequence and scope

Take any positive-definite Gram matrix whose diagonal values give
\(\theta_i=3/5\) on a three-coordinate block and \(\theta_i=2/5\) on the
other, and whose nonzero cross-block support is \(K_{3,3}\) with one edge
removed. For example, choose the required positive diagonal and add a
sufficiently small nonzero Hermitian weight on those eight cross entries.
The fixed-basis equality theorem in `fixed_basis_edge_independence.md` and
this note imply

\[
 \Phi_3(G)>u.
\]

Thus a hard exact-three access cap cannot always concentrate the departure
from ideal cross-block independence on one zero Gram entry, even when the
integer count-variance bound permits such concentration.

This is an exact result for the fixed encoded-basis model. It does not bound
arbitrary resident transforms, their encoded bytes, or the full Cassette
description class.
