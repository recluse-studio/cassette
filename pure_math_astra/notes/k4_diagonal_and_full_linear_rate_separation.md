# A fixed-coordinate rate separation between two linear coefficient classes

Status: an exact consequence of the K4 projector and the fixed-projector
upper construction. This is a comparison of declared coefficient classes
in one fixed coordinate representation. It is not a resource frontier
over freely changed source encodings, and it makes no originality claim.

Let P be the K4 cut-space projector in edge order (12,13,14,23,24,34),
and let G_r=P+r^2(I-P), 0<r<=1. Every diagonal entry of P is 1/2,
so every diagonal entry of G_r equals g=(1+r^2)/2.

Distinguish these three values:

* Phi_3 uses a query-independent random diagonal matrix D, with ED=I
  and at most three nonzero diagonal entries in each outcome.
* nu_3 uses a query-independent random full matrix L, with EL=I and
  at most three nonzero rows in each outcome.
* Psi_3 permits the law of an exactly unbiased three-sparse coefficient
  vector to be chosen after the complete query is supplied.

The ordering is Psi_3<=nu_3<=Phi_3. Off-support query coordinates may
contribute to retained coefficients in nu_3; diagonal weighting lacks
that freedom.

## Diagonal lower and upper bounds

Write d_i=D_{ii}, and let p_i=Pr(d_i!=0). Since E d_i=1, every p_i>0,
and Cauchy--Schwarz gives E d_i^2>=1/p_i. The support cap gives
sum_i p_i<=3. The risk operator is

\[
 C=\mathbb E[(D-I)^TG_r(D-I)].
\]

Its trace satisfies

\[
 \operatorname{tr}C
 =g\sum_{i=1}^6(\mathbb E d_i^2-1)
 \ge g\left(\sum_{i=1}^6p_i^{-1}-6\right)
 \ge6g.
\]

The last inequality follows from
(sum p_i)(sum p_i^{-1})>=36. Every law has
lambda_max(C)>=tr(C)/6>=g. Taking its infimum gives

\[
 \Phi_3(G_r)\ge\frac{1+r^2}{2}.
\]

For an upper bound, choose a uniform three-subset of the six coordinates
and put d_i=2 on that subset and zero elsewhere. The centered coefficient
second moments are 1 on the diagonal and -1/5 off the diagonal. Hence

\[
 C=\frac65gI-\frac15G_r,
 \qquad
 \lambda_{\max}(C)=\frac35+\frac25r^2.
\]

Consequently

\[
 \frac12+\frac12r^2
 \le\Phi_3(G_r)\le\frac35+\frac25r^2.
\]

In particular the optimal diagonal class retains a positive error floor
as r tends to zero.

## Full linear coefficients and query-dependent laws

The volume-sampled high-space law and sparse cycle law in
fixed_projector_sparse_kernel_order_r_upper.md use probabilities that
depend on P,r but not on x. Their retained outputs are linear maps of x.
Their mixture is therefore a common random full operator with mean I
and at most three nonzero rows. Its finite O(r) bound applies to nu_3,
and hence to Psi_3 as well.

The arbitrary exact-mean lower bound in
k4_cut_space_q6s3_order_r_lower.md gives Psi_3(G_r)>=r/1024. Thus

\[
 \Psi_3(G_r)=\Theta(r),\qquad
 \nu_3(G_r)=\Theta(r),\qquad
 \Phi_3(G_r)=\Theta(1)
 \quad(r\downarrow0).
\]

The full linear law already changes the error order in this fixed
representation; selecting a law after the query is not needed for that
change. A free orthogonal re-encoding could diagonalize G_r and change
the diagonal class itself. Charging that new source payload and its
description is a separate problem. The theorem therefore identifies a
coefficient-representation distinction, not an impossibility for every
execution plan that can access the same matrix action.
