# The finite \(k\)-polar lemma for rank-one matrices

Status: proved.  This verifies the finite polar lemma for every real
rank-one \(K\), for every \(k\ge2\), including every proper square
submatrix condition.  It does not establish the lemma for higher-rank
\(K\), and it makes no originality or resource-significance claim.

## Statement

Let \(K\in\mathbb R^{k\times k}\) have rank at most one.  There are
vectors \(u,n\in\mathbb R^k\) such that

\[
 \|u\|_2=1,\qquad \|n\|_2={1\over\sqrt{k}},
\tag{1}
\]

and, for every \(E,J\subseteq[k]\) with \(|E|=|J|\),

\[
 (n_J+K_{E,J}^Tu_E)^T
 (I+K_{E,J}^TK_{E,J})^{-1}
 (n_J+K_{E,J}^Tu_E)
 \le\|u_E\|_2^2.
\tag{2}
\]

Thus the rank-one subclass of the finite \(k\)-polar lemma holds with
\(\rho_k\ge1/\sqrt{k}\).

## Normalized factorization

Write

\[
 K=ab^T,\qquad \|b\|_2=1.
\tag{3}
\]

For nonzero \(K\), obtain (3) by absorbing the norm of an arbitrary right
factor into \(a\).  For \(K=0\), choose any unit \(b\) and set \(a=0\).
Put

\[
 w_i={1\over1+|a_i|},\qquad
 R=\left(\sum_{i=1}^kw_i^2\right)^{1/2},\qquad
 u_i=-{\operatorname{sgn}(a_i)w_i\over R},\qquad
 n={b\over\sqrt{k}}.
\tag{4}
\]

At a zero coordinate of \(a\), take \(\operatorname{sgn}(a_i)=1\).
Equation (1) follows immediately from (4).

Fix a nonempty \(E\), and write

\[
 A=\|a_E\|_2^2,\qquad B=\|b_J\|_2^2,\qquad
 W=\left(\sum_{i\in E}w_i^2\right)^{1/2},\qquad
 Q=\sum_{i\in E}{|a_i|\over1+|a_i|},\qquad
 d={1\over\sqrt{k}}.
\tag{5}
\]

Then \(B\le1\),

\[
 a_E^Tu_E=-{Q\over R},\qquad
 \|u_E\|_2={W\over R},\qquad
 n_J+K_{E,J}^Tu_E=\left(d-{Q\over R}\right)b_J.
\tag{6}
\]

Sherman--Morrison therefore reduces the left side of (2) to

\[
 \left(d-{Q\over R}\right)^2{B\over1+AB}
 \le {\left(d-Q/R\right)^2\over1+A}.
\tag{7}
\]

It remains only to show

\[
 \left|d-{Q\over R}\right|
 \le{W\sqrt{1+A}\over R}.
\tag{8}
\]

## The subset inequality

Cauchy--Schwarz gives

\[
 Q=\sum_{i\in E}|a_i|w_i\le W\sqrt A.
\tag{9}
\]

Hence the lower endpoint in (8) is nonpositive:

\[
 {Q-W\sqrt{1+A}\over R}\le0.
\tag{10}
\]

For every \(i\in E\),

\[
 Q+W\sqrt{1+A}
 \ge {|a_i|+\sqrt{1+a_i^2}\over1+|a_i|}
 \ge1.
\tag{11}
\]

Since \(R\le\sqrt{k}\), (11) gives

\[
 d={1\over\sqrt{k}}\le {1\over R}
 \le {Q+W\sqrt{1+A}\over R}.
\tag{12}
\]

Equations (10) and (12) put \(d\) in the interval centered at \(Q/R\)
with radius \(W\sqrt{1+A}/R\), proving (8).  Combining (7), (8), and
\(\|u_E\|_2^2=W^2/R^2\) proves (2).  The \(E=J=\varnothing\) condition
is void.

The proof used only \(B\le1\), so it handles each allowed \(J\) at once.
In particular, it verifies the coupled conditions for all proper square
submatrices rather than replacing them by scalar boxes and the full
ellipsoid.
