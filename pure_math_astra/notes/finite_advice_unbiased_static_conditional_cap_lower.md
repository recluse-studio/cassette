# Finite advice and static unbiased sampling: a conditional-cap lower bound

Status: proved and independently reconstructed. This direct
argument supersedes the weaker operator-based bounds for the same model.
It uses exact unbiasedness, conditional Jensen, and a sphere-covering
estimate. No substantive-originality or Cassette-significance claim is made.

## The theorem

Let \(p>q\ge2\), \(0<s<q\), and
\[
 {\cal V}_{p,q}=\{A\in\mathbb R^{p\times q}:A^TA=I_q\}.
\]
A measurable source encoder selects one of at most \(N\ge1\) fixed
states. Each state \(\ell\) has a probability law \(w_{\ell,S}\) on
subsets \(S\subseteq[q]\). This law is independent of the source within
that state and independent of the query. Assume
\[
 \sum_S w_{\ell,S}|S|\le s
 \quad\text{for every state.}
 \tag{1}
\]
After observing \(A_S\), the decoder returns an arbitrary Borel output
depending only on the label, \(S\), \(A_S\), and the query \(x\).
It may use a Borel random conditional law determined by these inputs,
with source-independent random seed.

Suppose, for every source and query,
\[
 \mathbb E[\widehat y\mid A,x]=Ax,
 \tag{2}
\]
and the uniform squared error is at most \(C<\infty\):
\[
 \sup_{A\in{\cal V}_{p,q},\ \|x\|=1}
 \mathbb E[\|\widehat y-Ax\|^2\mid A,x]\le C.
 \tag{3}
\]
Writing \(v_s=q/s-1>0\), one has
\[
 \boxed{\quad C\ge v_s\min\left\{1,
                  \left(\frac2N\right)^{2/(p-q)}\right\}.\quad}
 \tag{4}
\]
In particular, \(N\le2^b\) implies the simpler bound
\[
 C\ge v_s\,2^{-2b/(p-q)}.
 \tag{5}
\]
For a strict relative improvement \(C\le\zeta v_s\), \(0<\zeta<1\),
the sharper necessary condition is
\[
 b\ge1+\frac{p-q}{2}\log_2(1/\zeta).
 \tag{6}
\]

Hard support size at most an integer \(s\) implies (1). The theorem
also allows empty supports, overlapping supports, and variable support
sizes subject to (1). A state may specify a fixed right orthogonal
basis \(Q_\ell\in O(q)\), with reads from \(AQ_\ell\) and transformed
queries; the same conclusion holds.

For integer \(s\), uniform subsets of size \(s\), with output
\((q/s)A_Sx_S\), attain error \(v_s\) without advice. More generally,
for real \(s\in(0,q)\), independent column inclusion with probability
\(s/q\) attains the same error and expected read count. Thus when
\(b=o(p-q)\), (5) recovers the exact no-advice error scale.

## Exact mean amplifies a missing-column prediction bound

Replace each randomized branch by its conditional mean over internal
randomness. Jensen preserves (2) and reduces (3). Define its Borel
extension arbitrarily outside the integrable inputs that are used on
legal sources. We may work with deterministic branch outputs.

Fix a state and write \(E\) for its source cell. Set
\[
 \theta_j=\sum_{S\ni j}w_S.
\]
Summing inclusion probabilities gives
\(\sum_j\theta_j=\sum_Sw_S|S|\le s\), so choose an index \(j\) with
\(\theta=\theta_j\le s/q<1\). The choice depends only on the state.

Write \(a=a_j\) and \(W=A_{-j}\). For the unit query \(x=e_j\), average
all branch outputs that omit \(j\):
\[
 H(W)=\frac1{1-\theta}
       \sum_{S\not\ni j}w_S F_S(A_S,e_j).
 \tag{7}
\]
Every term is determined by \(W\), so \(H\) is a Borel function of
the other columns. If \(\theta>0\), also define
\[
 F(A)=\frac1\theta
       \sum_{S\ni j}w_S F_S(A_S,e_j).
 \tag{8}
\]
No restriction on the dependence of \(F\) on \(A\) is needed.
Exactness on the state cell gives
\[
 \theta F(A)+(1-\theta)H(W)=a.
 \tag{9}
\]
Jensen within the two groups and (9) now imply
\[
 \begin{aligned}
 R(A,e_j)
 &\ge\theta\|F(A)-a\|^2+
                   (1-\theta)\|H(W)-a\|^2\\
 &=\frac{1-\theta}{\theta}\|H(W)-a\|^2.
 \end{aligned}
 \tag{10}
\]
This is the decisive use of exact unbiasedness. Keeping only the risk
of the missing-column group would lose the factor \(1/\theta\).

If \(\theta>0\), (3) and (10) give, throughout \(E\),
\[
 \|H(W)-a\|\le
 \sqrt{\frac{C\theta}{1-\theta}}
 \le\sqrt{\frac{Cs}{q-s}}
 =\sqrt{\frac C{v_s}}.
 \tag{11}
\]
If \(\theta=0\), exactness (2) at \(e_j\) instead says \(H(W)=a\).

## Conditional spherical caps

Give \({\cal V}_{p,q}\) its uniform probability measure \(\mu\).
Conditional on the other \(q-1\) columns \(W\), the missing column
\(a\) is uniform on the unit sphere in \(W^\perp\). That subspace
has dimension
\[
 d=p-q+1\ge2.
 \tag{12}
\]
Projecting \(H(W)\) into \(W^\perp\) can only reduce its distance to
\(a\). A ball of radius \(0\le\delta<1\), with any center in a
\(d\)-dimensional Euclidean space, cuts normalized sphere measure at
most
\[
 \frac12\delta^{d-1}.
 \tag{13}
\]

Here is a direct proof. If the center is zero, the intersection is
empty. Otherwise write its norm as \(r>0\). Ball membership requires
the axial coordinate to be at least
\[
 \frac{1+r^2-\delta^2}{2r}\ge\sqrt{1-\delta^2}.
\]
The last inequality is equivalent to
\((r-\sqrt{1-\delta^2})^2\ge0\). With \(a_0=(d-1)/2>0\), the measure
of this axial cap is
\[
 \frac12\,
 \frac{\int_0^{\delta^2}u^{a_0-1}(1-u)^{-1/2}\,du}
      {\int_0^1u^{a_0-1}(1-u)^{-1/2}\,du}
 \le\frac12\delta^{2a_0}.
\]
Substitute \(u=\delta^2t\) in the numerator and use
\((1-\delta^2t)^{-1/2}\le(1-t)^{-1/2}\). At \(\delta=0\), use
nonatomicity. This proves (13), including \(d=2\).

If \(C<v_s\), set \(\delta=\sqrt{C/v_s}<1\). By (11), for every
fixed \(W\) the fiber of the state cell \(E\) lies inside the ball
covered by (13). Conditional integration therefore gives
\[
 \mu(E)\le\frac12
       \left(\frac C{v_s}\right)^{(p-q)/2}.
 \tag{14}
\]
When \(\theta=0\), the cell lies in the graph of \(H(W)\). Its
conditional fibers are singletons, hence null by (12); (14) holds
for this case as well.

The encoder's state cells cover the whole orbit and there are at most
\(N\) of them. Their indices \(j\), their predictors \(H\), and their
probabilities may differ; (14) has the same bound for each. Summing gives
\[
 1\le\frac N2\left(\frac C{v_s}\right)^{(p-q)/2}
 \qquad (C<v_s).
 \tag{15}
\]
If \(C=0\), every cell is null, a contradiction. For \(0<C<v_s\),
rearranging (15) gives (4). For \(C\ge v_s\), (4) follows directly.
Equations (5) and (6) are immediate consequences.

The restriction \(C<v_s\) in (15) is essential. At radius one,
a ball centered at zero contains the whole unit sphere, and (13)
does not extend to that endpoint.

## Basis and attained error

For a label-specific basis \(Q_\ell\), apply the same argument to
\(\widetilde A=AQ_\ell\) on the transformed cell. Choose the original
query \(x=Q_\ell e_j\). Right multiplication preserves uniform
Stiefel measure and the query has unit norm. The measure of each
transformed cell equals that of its original cell, so (14)--(15)
continue to hold label by label.

To verify the comparison sampler, let \(I_j\) indicate inclusion with
marginal probability \(s/q\), and output
\[
 \widehat y=\sum_j\frac q s I_j a_jx_j.
\]
Its mean is \(Ax\). Because the columns are orthonormal,
\[
 \mathbb E\|\widehat y-Ax\|^2
 =\sum_j x_j^2
   \mathbb E\left(\frac q s I_j-1\right)^2
 =\left(\frac q s-1\right)\|x\|^2.
\]
No independence between the indicators is needed for this calculation.
Uniform size-\(s\) subsets give the hard cap for integer \(s\);
independent Bernoulli indicators give the expected-count version for
all real \(s\in(0,q)\).

## What this changes, and what remains open

This result strengthens the earlier lower bound for arbitrary biased
outputs by using the exact-mean condition. It covers arbitrary nonlinear
static decoders with finitely many source-selected states. In the
identity-Gram orbit, a fixed fractional reduction of the no-advice
error requires a number of advice bits proportional to \(p-q\).

The proof is a short combination of conditional Jensen, exact-mean
algebra, and a standard cap-covering bound. The earlier compact-operator
and atomic-matching route is unnecessary for this theorem and gives
a weaker exponent. That analytic work remains valid supporting work;
it supplies no additional originality credit to the direct theorem.

This does not yet give the nonisotropic spectral bound needed by the
equicorrelation adaptivity example. For a general positive Gram matrix,
conditioning on all other columns leaves a squared innovation norm
\(1/(G^{-1})_{jj}\). A coordinate-wise version therefore sees Schur
complements, which can be smaller than the spectral error bound.
That gap is a next mathematical question, not a completed consequence.

The theorem prices the source-selected state count and sampled columns.
It does not price arbitrary source encodings, physical pages, resident
table size, or finite-precision execution. These resource questions and
the originality/significance assessment remain open.

## Related local records

- [Independent reconstruction](/Users/drewwiberg/cassette/pure_math_astra/notes/finite_advice_unbiased_static_conditional_cap_lower_independent_review.md).
- [Separate two-group reconstruction](/Users/drewwiberg/cassette/pure_math_astra/notes/static_support_residual_cap_lower.md).
- [Nonisotropic Schur-complement obstacle](/Users/drewwiberg/cassette/pure_math_astra/notes/nonisotropic_static_residual_cap_obstacle.md).
- [Earlier one-column operator argument](/Users/drewwiberg/cassette/pure_math_astra/notes/one_column_unbiased_finite_advice_lower.md).
- [Earlier two-column argument and review](/Users/drewwiberg/cassette/pure_math_astra/notes/two_column_unbiased_finite_advice_lower.md).
- [Rational covering upper construction](/Users/drewwiberg/cassette/pure_math_astra/notes/two_column_finite_advice_covering_upper.md).
- [Bounded source challenge](/Users/drewwiberg/cassette/pure_math_astra/research/two_column_finite_advice_primary_source_challenge.md).
