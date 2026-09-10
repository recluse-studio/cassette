# Minimal cross-block dependence support under an exact subset cap

This note computes one dependence-support value in the ideal fixed-basis
subset model. It does not claim a finite-byte transform theorem or novelty.

Let \(A\) and \(B\) be blocks of sizes \(m\) and \(n\). A random subset
\(S\) has exactly \(s\) elements, every coordinate of \(A\) has inclusion
probability \(p\), and every coordinate of \(B\) has inclusion probability
\(r\), with

\[
 mp+nr=s. \tag{1}
\]

For \(i\in A\), \(j\in B\), write

\[
 C_{ij}=\Pr(i,j\in S)-pr.
\]

The cross-block dependence support is

\[
 k(A,B;p,r,s)=\min\bigl|\{(i,j):C_{ij}\ne0\}\bigr|, \tag{2}
\]

where the minimum ranges over all laws satisfying (1). In the local
fixed-basis Gram calculation, these are the cross-block entries at which the
ideal variance cancellation fails.

## 1. A universal count bound

Let \(K=|S\cap A|\), let \(f\) be the fractional part of \(mp\), and put

\[
 \gamma=\min\{pr,(1-p)(1-r)\}.
\]

Whenever \(0<p,r<1\),

\[
 k(A,B;p,r,s)\geq
 \left\lceil\frac{f(1-f)}{\gamma}\right\rceil. \tag{3}
\]

Also,

\[
 k(A,B;p,r,s)=0\quad\Longleftrightarrow\quad mp\in\mathbb Z. \tag{4}
\]

**Proof.** Since \(|S\cap B|=s-K\),

\[
 \sum_{i\in A,j\in B}C_{ij}
 =\operatorname{Cov}(K,s-K)=-\operatorname{Var}K. \tag{5}
\]

An integer-valued variable with mean \(mp\) has variance at least
\(f(1-f)\). Each Bernoulli cross covariance is at least \(-\gamma\), by the
Fréchet bounds. If only \(k\) entries are nonzero, (5) gives
\(\operatorname{Var}K\leq k\gamma\), proving (3).

If \(k=0\), (5) makes \(K\) constant, so \(mp\) is integral. Conversely,
if \(mp\) is integral, independently choose a uniform \(mp\)-subset of
\(A\) and a uniform \(nr\)-subset of \(B\). It has the desired marginals,
exact size, and zero cross covariance. \(\square\)

Bound (3) is sharp in some cases. For \(m=n=3\), \(s=3\), \(p=r=1/2\), it
gives \(k\geq1\), and the one-exception construction in
`two_block_single_defect_designs.md` attains one. For \(m=n=2\), \(s=2\),
\(p=3/4\), \(r=1/4\), it gives \(k\geq2\), agreeing with the known
\(2\times2\) calculation. It is not always sharp: the main result below has
count lower bound one but exact value two.

## 2. Exact value for the \(3+3\), \(3/5\)--\(2/5\) phase

**Theorem.** For

\[
 m=n=s=3,\qquad p=\frac35,\qquad r=\frac25,
\]

one has

\[
 k(A,B;3/5,2/5,3)=2. \tag{6}
\]

**Lower bound.** Here \(mp=9/5\), so no zero-support law exists by (4). A
single exceptional pair is impossible: the exact orbit calculation in
`two_block_single_defect_designs.md` proves that a \(3+3\) one-exception law
exists only at

\[
 p\in\{0,1/3,1/2,2/3,1\}.
\]

Since all one-pair locations are equivalent under separate permutations of the
two blocks, \(k\geq2\). Notice that the count bound alone gives only
\(\lceil(4/25)/(6/25)\rceil=1\). The stricter lower bound is therefore a
real support-placement obstruction, not merely an integrality calculation.

**Construction.** Name the coordinates

\[
 A=\{a_0,a_1,a_2\},\qquad B=\{b_0,b_1,b_2\}.
\]

Give the following exactly-three subsets the displayed integer weights, then
divide all weights by \(25\):

\[
\begin{array}{c|c@{\qquad}c|c}
S&25\Pr(S)&S&25\Pr(S)\\ \hline
\{a_0,a_1,b_0\}&3&\{a_0,a_1,b_1\}&3\\
\{a_0,a_1,b_2\}&2&\{a_0,a_2,b_0\}&1\\
\{a_1,a_2,b_1\}&1&\{a_0,a_2,b_1\}&2\\
\{a_1,a_2,b_0\}&2&\{a_0,a_2,b_2\}&3\\
\{a_1,a_2,b_2\}&3&\{a_0,b_1,b_2\}&1\\
\{a_1,b_0,b_2\}&1&\{a_2,b_0,b_1\}&3.
\end{array} \tag{7}
\]

Every \(a_i\) has total weight \(15\), and every \(b_j\) has total weight
\(10\). Thus their marginals are \(3/5\) and \(2/5\). The cross pair
weights are

\[
 \begin{array}{c|ccc}
 25\Pr(a_i,b_j\in S)&b_0&b_1&b_2\\ \hline
 a_0&4&6&6\\
 a_1&6&4&6\\
 a_2&6&6&6.
 \end{array} \tag{8}
\]

Therefore every cross covariance vanishes except

\[
 C_{a_0b_0}=C_{a_1b_1}=-\frac2{25}. \tag{9}
\]

This construction has

\[
 \Pr(K=1)=\frac15,\qquad \Pr(K=2)=\frac45,
 \qquad \operatorname{Var}K=\frac4{25}.
\]

The two exceptional covariances in (9) sum to \(-4/25\), exactly as (5)
requires. This proves (6). \(\square\)

## 3. Scope

The theorem gives a sharp support count for one two-block phase. It says that
when the ideal inclusion masses are \(3/5\) and \(2/5\), a hard exact-three
cap must leave at least two cross-block covariance entries uncancelled, while
two suffice. This is the input needed by a local variance normal form that
charges a separate rotation coordinate for each such entry.

The result does not itself prove a covering exponent, a finite transform
library bound, or a resource law for arbitrary resident descriptions. Those
consequences require the separate local-geometry and encoded-transform
arguments.
