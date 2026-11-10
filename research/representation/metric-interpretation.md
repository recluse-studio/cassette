# A relationship representation and its strongest sparse interpreter

A representation can describe which coefficient errors are expensive without storing the
output directions of the weight matrix. The Gram matrix supplies exactly that information.
The construction below is an established-method baseline, assembled from quadratic error,
convex decomposition, and the existing Cassette atomic-norm analysis. It is not a novelty claim.

## Exact interpretation with a hard column limit

Fix a real matrix \(A\), a query \(x\), and \(G=A^TA\succ0\). An interpreter chooses a
random coefficient vector \(Y\) with \(\mathbb EY=x\) and at most \(s\) nonzero entries.
It reads those original columns and returns \(AY\). The answer is unbiased, and its risk is

\[
\mathbb E\|AY-Ax\|^2=\operatorname{tr}(G\operatorname{Cov}(Y)). \tag{M1}
\]

The full output basis of \(A\) is absent from this selection problem. It remains in the
external columns and is used when the answer is formed. The covariance depends on both the
query and the law, so a fixed coordinate probability table is only a restricted interpreter.

The best such law has a finite convex formulation. Let \(S\) range over all subsets of
\([q]\) of size at most \(s\). Give each subset a probability \(\theta_S\) and an
unconditional mean contribution \(z_S\), supported in \(S\). Minimize

\[
\sum_S\frac{z_S^TGz_S}{\theta_S}-x^TGx,
\quad \sum_S\theta_S=1,\quad \sum_Sz_S=x,\quad\theta_S\ge0. \tag{M2}
\]

At \(\theta_S=0\), the perspective term is zero if \(z_S=0\) and infinite otherwise.
Every feasible solution gives the law \(Y=z_S/\theta_S\) with probability \(\theta_S\).
Conversely, condition any admissible law on a subset containing its support and replace each
conditional distribution by its mean. Jensen's inequality preserves feasibility and cannot
increase the quadratic risk. Thus M2 optimizes the whole stated class, including correlated,
query-dependent support and arbitrary coefficients. This is the perspective form of the
[existing atomic-norm formulation](../../pure_math_astra/notes/query_adaptive_atomic_dual.md).

There are exponentially many possible subsets. Exact optimization in this formulation is an
oracle baseline, not a fast runtime algorithm. Its ideal real coefficients also need a separate
finite-precision construction before a byte-level comparison can use them.

## What an approximate relationship code preserves

**Proposition M1, proved below as a baseline guarantee.** Suppose the decoded representation
\(\widetilde G\) has a verified relative quadratic bound

\[
(1-\epsilon)G\preceq\widetilde G\preceq(1+\epsilon)G,
\qquad0\le\epsilon<1. \tag{M3}
\]

For a fixed query, let \(Y_*\) minimize the risk under \(G\), and let
\(\widetilde Y\) minimize the risk under \(\widetilde G\), in the same nonempty class of
unbiased laws with the same hard support bound. Then

\[
\mathbb E\|A(\widetilde Y-x)\|^2
\le\frac{1+\epsilon}{1-\epsilon}
\mathbb E\|A(Y_*-x)\|^2. \tag{M4}
\]

**Proof.** Every covariance matrix is positive semidefinite. Taking its trace against M3 gives
\((1-\epsilon)\operatorname{tr}(G C)\le\operatorname{tr}(\widetilde G C)
\le(1+\epsilon)\operatorname{tr}(G C)\). Apply the first inequality to
\(C=\operatorname{Cov}(\widetilde Y)\), use the minimizing property of
\(\widetilde Y\), and apply the second inequality to
\(C=\operatorname{Cov}(Y_*)\). Equation M1 finishes the proof. Infima and arbitrarily
near-optimal laws give the same bound when an optimizer is not assumed. □

If the interpreter is only \(\alpha\)-optimal under \(\widetilde G\), the right side of
M4 is multiplied by \(\alpha\). A certified additive optimization gap \(h\) instead adds
\(h/(1-\epsilon)\). This keeps representation error and interpretation error separate.

## Stress test: additive Gram accuracy can lose an arbitrarily large factor

Let \(G=\operatorname{diag}(1,\eta^2)\),
\(\widetilde G=\operatorname{diag}(1,\eta)\), \(0<\eta<1\), take \(x=(1,1)^T\),
and allow one sampled column. The exact optimum under \(G\) has probabilities proportional
to \((1,\eta)\) and risk \(2\eta\). The optimum under \(\widetilde G\) has probabilities
proportional to \((1,\sqrt\eta)\). Its true risk is
\(\sqrt\eta+\eta^{3/2}\). The ratio is

\[
\frac{1+\eta}{2\sqrt\eta}\longrightarrow\infty,
\]

although \(\|\widetilde G-G\|_{\rm op}=\eta-\eta^2\to0\). A small absolute error
in the relationship table does not supply M3. Weak directions determine the relative condition.

## Construction and resource question

A direct symmetric Gram representation uses \(q(q+1)/2\) encoded coefficients, before
rounding certificates and metadata. A low-rank-plus-diagonal form
\(\widetilde G=D+H^TH\) uses \(q+kq\) coefficients, where \(H\) has \(k\) rows.
Its advantage depends on finding and certifying M3 with small \(k\), small coefficient widths,
and affordable query interpretation. Merely writing this form does not establish that a given
source permits it.

Every method using the same relationship code is allowed to exploit it in the comparison.
In particular, a novel probability rule must face M2 or a certified approximation to M2,
rather than claiming a win over independent column draws alone. The open construction problem
is to produce a compact relationship code and a computationally affordable interpreter that
jointly improve the equal-byte error/read frontier.

The primary-source literature also includes
[Efficient Unbiased Sparsification, 2024](https://arxiv.org/html/2402.14925v2), which solves
important separable and permutation-invariant loss classes, and
[exact balanced finite-population sampling, 2025](https://academic.oup.com/biomet/article/112/4/asaf058/8210742),
which studies exact balancing constraints. Their assumptions and decoder mechanisms belong in
the comparison before feature-preserving or sparse unbiased interpretation is claimed as new.
