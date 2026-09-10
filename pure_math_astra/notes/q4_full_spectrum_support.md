# Full covariance-support classification for four coordinates and two reads

This note classifies the full covariance-support graph of an exactly-two
subset law on four nondegenerate coordinates. It concerns all six pair
covariances, not a partial edge set or a repeated-eigenvalue block model. It
does not claim novelty or an encoded-byte consequence.

Let \(X_i=\mathbf1\{i\in S\}\), where \(|S|=2\) almost surely, and let

\[
 0<p_i=\mathbb EX_i<1,
 \qquad \sum_{i=1}^4p_i=2.
\]

Let \(k\) be the number of nonzero off-diagonal covariances.

## The classification

**Theorem.** One has

\[
 k_{\min}=
 \begin{cases}
 2,&p_i+p_j=1\text{ for some }i\ne j,\\
 5,&\text{otherwise}.
 \end{cases} \tag{1}
\]

### Which pair can be made independent?

Fix a proposed independent pair \(1,2\), and put
\(x=\Pr(X_1=X_2=1)\). Then

\[
 \Pr(X_3=X_4=1)=y=x+1-p_1-p_2. \tag{2}
\]

The remaining four two-subset probabilities form a \(2\times2\)
transportation table with row sums \(p_1-x,p_2-x\) and column sums
\(p_3-y,p_4-y\). Thus an exactly-two law with this value of \(x\) exists if
and only if

\[
 \max(0,p_1+p_2-1)
 \leq x\leq
 \min(p_1,p_2,1-p_3,1-p_4). \tag{3}
\]

Set \(x=p_1p_2\). The lower and the first two upper bounds are automatic.
The other two are equivalent to

\[
 p_1p_2+\max(p_3,p_4)\leq1. \tag{4}
\]

At least one pair always satisfies (4). Sort the four marginals as

\[
 a\geq b\geq c\geq d.
\]

If \(cd+a\leq1\), pair \((c,d)\) works. Otherwise
\(d>(1-a)/c\). Since \(b=2-a-c-d\),

\[
 \begin{aligned}
 ab+c-1
 &= (a+c-1)(1-a)-ad\\
 &<(1-a)\left(a+c-1-\frac ac\right)\\
 &=-\frac{(1-a)(1-c)(a+c)}c<0.
 \end{aligned} \tag{5}
\]

Hence \(ab+c<1\), so pair \((a,b)\) works. Every marginal vector therefore
admits a law with at least one zero covariance.

### Why two zero covariances force complementary marginals

Assume no pair of marginals sums to one. If two covariance entries vanish and
share a coordinate, that coordinate has degree at most one in the covariance
support graph. It cannot be isolated because its variance is positive. The
leaf rule then forces a complementary marginal pair, a contradiction.

The remaining possibility is two opposite zero entries, say

\[
 \operatorname{Cov}(X_1,X_3)=operatorname{Cov}(X_2,X_4)=0.
\]

Because \(X_1+X_2+X_3+X_4=2\),

\[
 \operatorname{Var}(X_1+X_3)=\operatorname{Var}(X_2+X_4).
\]

Using the two zero covariances gives

\[
 p_1(1-p_1)+p_3(1-p_3)
 =p_2(1-p_2)+p_4(1-p_4).
\]

Together with \(\sum_i p_i=2\), this is equivalent to

\[
 (1-p_1)(1-p_3)=p_2p_4,
 \qquad
 (1-p_1)+(1-p_3)=p_2+p_4. \tag{6}
\]

The two unordered positive pairs in (6) have the same sum and product, so

\[
 \{1-p_1,1-p_3\}=\{p_2,p_4\}.
\]

Again a complementary marginal pair follows. Therefore, in the
noncomplementary case, at most one covariance can vanish. The preceding
transport construction supplies one vanishing covariance, so \(k_{\min}=5\).

Finally, if \(p_1+p_2=1\), then \(p_3+p_4=1\). Independently choose one
coordinate from \(\{1,2\}\) with marginals \(p_1,p_2\), and one from
\(\{3,4\}\) with marginals \(p_3,p_4\). The only nonzero covariances are
inside the two complementary pairs. Hence \(k=2\). A one-edge support graph
would leave two nondegenerate vertices isolated, so no smaller value is
possible. This completes the proof. \(\square\)

## Fixed-basis spectral reading

For diagonal energies \(a_i>0\) and a fixed variance parameter \(t>0\), set

\[
 p_i=\frac{a_i}{a_i+t}.
\]

Then

\[
 p_i+p_j=1\quad\Longleftrightarrow\quad a_ia_j=t^2. \tag{7}
\]

Thus a simple diagonal spectrum can still lie on a reciprocal pair locus. In
the full six-edge covariance graph, a local transform-library expression of
the form

\[
 \kappa=\frac{\beta(|T|+k)}2,
 \qquad |T|=6,
\]

gives \(\kappa=4\beta\) on that locus and \(\kappa=11\beta/2\) for a
generic simple spectrum. This last statement uses the separate local-geometry
argument; the present theorem supplies only its exact covariance-support input.
