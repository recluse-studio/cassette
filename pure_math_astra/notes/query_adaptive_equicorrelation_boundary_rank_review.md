# Independent review of the rank-two equicorrelation boundary bound

Status: correctness review of
`query_adaptive_equicorrelation_boundary_rank_bound.md`.  The reviewed
argument supports its claimed bound; this note makes no originality claim.

The slack identity is correct.  Summing the six pair quantities gives
\(\epsilon=H-2V/3\), and projection by
\(P=I-\mathbf1\mathbf1^T/4\) gives

\[
 B={H\over2}P-2P\operatorname{Diag}(a)P+{1\over2}PEP.
\tag{1}
\]

When \(E=0\), the trace calculation uses

\[
 \operatorname{tr}(P\operatorname{Diag}(a)P)^2={\|a\|_2^2\over2},
\tag{2}
\]

which is correct because \(\sum_i a_i=0\).  Together with
\(\operatorname{rank}B\le2\), it gives the stated zero-slack check
\(V\le3+2\sqrt3\).

For general slack, the Frobenius estimates are valid:

\[
 \|B\|_F\ge {V\over\sqrt2},\qquad
 \left\|{1\over2}PEP\right\|_F\le3\sqrt2\,\epsilon.
\tag{3}
\]

Thus the necessary inequality used in the contradiction follows.  If
\(C(q)\ge189/100\), then \(H\ge0\) makes the preliminary squaring
order-preserving and yields

\[
 \epsilon\le {22\over867}V-{89\over200}=:\bar\epsilon.
\tag{4}
\]

After replacing \(\epsilon\) by \(\bar\epsilon\), the exact squared
difference is

\[
 {25\over167042}V^2+{4193\over5780}V+{546549\over160000},
\tag{5}
\]

which is positive.  The rational coefficients in (4)--(5) were checked by
direct expansion.  This contradicts the necessary Frobenius inequality, so
\(C(q)<189/100\) pointwise.

The strict uniform gap is also valid.  The Jung tail bound

\[
 H\ge {3V\over4}-2\sqrt V
\tag{6}
\]

exceeds \(25V/36-11/25\) for \(V\ge4096\).  The latter is exactly the
threshold for \(C(q)\le47/25\).  Hence any sequence approaching
\(189/100\) has bounded \(V\); compactness of mean-zero quadruples at
bounded \(V\), continuity of \(C\), and the pointwise strict inequality
make the gap uniform.  This is the form required by the finite-\(\eta\)
compactness argument in the preceding equicorrelation proof.

The author note now explicitly states the positivity and monotonicity facts
needed before its two squaring steps, handles \(V=0\) in the zero-slack
aside, and repairs its display delimiters.
