# A full-support nine-coordinate odd-cycle design

This note extends the open odd-cycle covariance-support family from
\(q=5,s=2\) and \(q=7,s=3\) to \(q=9,s=4\). It is an exact finite orbit
construction. It does not prove the construction for all odd dimensions, a
byte bound, or novelty.

Index coordinates modulo nine. Set

\[
 s=4,\qquad p_i=\frac49,
 \qquad v=p_i(1-p_i)=\frac{20}{81}.
\]

The target pair moments are

\[
 \Pr(i,i+1\in S)=\frac2{27},
 \qquad
 \Pr(i,j\in S)=\frac{16}{81}
 \quad(j-i\not\equiv\pm1). \tag{1}
\]

Thus the target covariance is \(-10/81=-v/2\) on the nine-cycle and zero on
every noncycle pair.

## 1. Exact cyclic law

For each representative \(R\) below, let \(\mathcal O(R)\) be its nine
cyclic rotations. Assign the displayed total mass to the orbit, then distribute
that mass uniformly over its nine four-subsets. The four middle columns count
within the representative the pairs at circular distances \(1,2,3,4\).

\[
\begin{array}{c|c|c|c|c|c}
 R&5400\,\Pr(\mathcal O(R))&n_1&n_2&n_3&n_4\\ \hline
0123&12&3&2&1&0\\
0124&20&2&2&1&1\\
0125&30&2&1&1&2\\
0126&30&2&1&1&2\\
0127&20&2&2&1&1\\
0134&30&2&1&2&1\\
0135&60&1&2&1&2\\
0136&553&1&1&3&1\\
0137&60&1&2&2&1\\
0145&60&2&0&1&3\\
0146&1898&1&1&2&2\\
0147&553&1&1&3&1\\
0157&60&1&2&1&2\\
0246&2014&0&3&1&2
\end{array} \tag{2}
\]

The orbit masses in (2) sum to one and are all positive, so every one of the
\(\binom94=126\) four-subsets has positive probability. Rotation invariance
makes every coordinate marginal \(4/9\). For a fixed pair at circular distance
\(d\), its inclusion probability is

\[
 \frac1{9}\sum_R \Pr(\mathcal O(R))n_d.
\]

Substitution from (2) gives

\[
 \left(\frac2{27},\frac{16}{81},\frac{16}{81},\frac{16}{81}\right),
\]

which proves (1).

## 2. Persistence to a simple spectrum

The target moments remain feasible for all sufficiently small perturbations of
the marginals with \(\sum_i p_i=4\), while retaining noncycle moments
\(\Pr(i,j\in S)=p_ip_j\). This is a finite linear-algebra fact.

Use normalization, the first eight coordinate marginals, and the 27 noncycle
pair moments. The resulting \(36\times126\) incidence matrix has rank 36.
An explicit unit-determinant minor uses the columns

\[
\begin{gathered}
0123,0124,0125,0126,0127,0128,0134,0135,0136,0137,0138,0145,0146,0147,0148,\\
0156,0157,0158,0167,0168,0178,0234,0235,0236,0237,0238,0245,0345,1234,1235,\\
1236,1237,1238,1245,1345,2345.
\end{gathered} \tag{3}
\]

The omitted ninth marginal follows from the exact-size relation. The only
affine relation among normalization, all nine marginals, and the 27 noncycle
moments is \(\sum_i p_i=4\).

Keep the 90 probabilities outside (3) fixed at their strictly positive values
from (2), and solve the 36 selected probabilities by the inverse of this
minor. The solution varies continuously with the target moments and remains
strictly positive in a sufficiently small neighborhood. The cycle covariances
remain nonzero because they equal \(-10/81\) at the center.

Choose a nearby vector with all \(p_i\) distinct and no pair summing to one.
The covariance-support graph is then exactly \(C_9\). The leaf-pair bound in
`full_spectrum_covariance_support.md` gives \(k\geq9\), and the construction
gives

\[
 k=9. \tag{4}
\]

With \(a_i=tp_i/(1-p_i)\) for fixed \(t>0\), this yields an open
full-simple-spectrum diagonal family.

## 3. Limit of the present evidence

The constructions at \(q=5,7,9\) establish three odd-dimensional open
families. Their orbit weights do not yet reveal a dimension-uniform formula.
The all-odd \(q=2s+1\) statement remains open in this lab.
