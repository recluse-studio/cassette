# Fixed-basis rigidity at the unrestricted coded-access optimum

This note proves an equality-case statement for an ideal coded-access model. It
does not assert novelty and does not imply a byte lower bound for Cassette.

Let \(R\in\mathbb F^{p\times q}\) have full column rank, let \(G=R^*R\succ0\),
and fix an integer \(1\leq s<q\).  In the fixed input-coordinate basis, restrict
random outcomes to

\[
 Z_b=RD_b,
 \qquad D_b=\operatorname{Diag}(b_1,\ldots,b_q),
 \qquad |\operatorname{supp}b|\leq s\quad\text{almost surely}, \tag{1}
\]

where \(b\) may be real or complex and may depend on the selected support. Assume
\(\mathbb E D_b=I\) and \(\mathbb E[Z_b^*Z_b]\) is finite.  Thus the estimator
is unbiased and its rank is at most \(s\) on every outcome.

Let \(t_*>0\) be the unique root

\[
 \operatorname{tr}\bigl(G(G+t_*I)^{-1}\bigr)=s. \tag{2}
\]

The unrestricted coded-basis theorem gives \(t_*\) as the best possible
worst-query covariance among *all* unbiased rank-\(s\) random matrices.

Define \(\Phi_s(G)\) as the infimum of
\(\lambda_{\max}(\mathbb E[Z_b^*Z_b]-G)\) over the fixed-basis class (1).

## Primary marginal proof and quantitative gap

Let \(a_i=G_{ii}\), and let \(u_s>0\) be the unique number satisfying

\[
 \sum_{i=1}^q\frac{a_i}{a_i+u_s}=s. \tag{M1}
\]

Then

\[
 \Phi_s(G)\geq u_s\geq t_*. \tag{M2}
\]

Equality throughout holds if and only if \(G\) is diagonal.

**Proof.**  Put \(\theta_i=\Pr(b_i\ne0)\). The hard rank cap gives
\(\sum_i\theta_i\leq s\). Since \(\mathbb Eb_i=1\), Cauchy--Schwarz on the
event \(b_i\ne0\) gives

\[
 \mathbb E|b_i|^2\geq\frac1{\theta_i}. \tag{M3}
\]

If the covariance is bounded above by \(tI\), its \(i\)-th diagonal gives

\[
 a_i(\mathbb E|b_i|^2-1)\leq t.
\]

Combining with (M3) yields

\[
 \theta_i\geq\frac{a_i}{a_i+t},
 \qquad
 \sum_i\frac{a_i}{a_i+t}\leq s. \tag{M4}
\]

The left side decreases strictly in \(t\), proving \(t\geq u_s\).

Let \(\lambda_1,\ldots,\lambda_q\) be the eigenvalues of \(G\). The diagonal
vector \(a\) is majorized by \(\lambda\). For fixed positive \(t\),
\(x\mapsto x/(x+t)\) is strictly concave, so

\[
 \sum_i\frac{a_i}{a_i+t}\geq
 \sum_i\frac{\lambda_i}{\lambda_i+t}. \tag{M5}
\]

At \(t=t_*\), the right side is \(s\). Equality in (M5) is possible only when
the diagonal is a permutation of the eigenvalue vector. Then
\(\operatorname{tr}G^2=\sum_i a_i^2\), which forces every off-diagonal entry
of \(G\) to vanish. Conversely, when \(G\) is diagonal, set
\(\pi_i=a_i/(a_i+t_*)\), take an exact-size \(s\)-subset with these
inclusion probabilities, and put \(b_i=\mathbf 1\{i\in S\}/\pi_i\).
Then \(\mathbb E[Z_b^*Z_b]=G+t_*I\). This proves (M2) and its equality
characterization. \(\square\)

This argument also gives a quantitative, basis-dependent lower bound. Put
\(D=\operatorname{Diag}(G)\), \(E=G-D\), and \(\Lambda=\lambda_{\max}(G)\).
At \(t=t_*\), define

\[
 J=\sum_i\frac{a_i}{a_i+t}-\sum_i\frac{\lambda_i}{\lambda_i+t}
 =t\left[\operatorname{tr}(G+tI)^{-1}-\sum_i\frac1{a_i+t}\right],
\]

and \(L=\sum_i a_i/(a_i+t)^2\). Along \(G(z)=D+zE\), the first derivative of
\(\operatorname{tr}(G(z)+tI)^{-1}\) at zero vanishes because \(E\) has zero
diagonal. Its second derivative is

\[
 2\operatorname{tr}\bigl(M_z^{-1}E M_z^{-1}E M_z^{-1}\bigr),
 \qquad M_z=G(z)+tI.
\]

Since \(0\preceq G(z)\preceq\Lambda I\), write the trace as
\(\operatorname{tr}[(M_z^{-1/2}EM_z^{-1/2})^2M_z^{-1}]\). The minimum
eigenvalue of \(M_z^{-1}\) is at least \((\Lambda+t)^{-1}\), and the
Frobenius norm of \(M_z^{-1/2}EM_z^{-1/2}\) is at least
\((\Lambda+t)^{-1}\|E\|_F\). Thus the displayed second derivative is at
least \(2\|E\|_F^2/(\Lambda+t)^3\). Integrating gives

\[
 J\geq\frac{t\|E\|_F^2}{(\Lambda+t)^3}. \tag{M6}
\]

Finally, if \(F(x)=\sum_i a_i/(a_i+x)\), then
\(J=F(t)-F(u_s)\leq L(u_s-t)\), because \(-F'(x)\) decreases in \(x\). Hence

\[
 \Phi_s(G)-t_*
 \geq u_s-t_*
 \geq
 \frac{t_*\|G-\operatorname{Diag}G\|_F^2}
 {(\Lambda+t_*)^3\sum_i a_i/(a_i+t_*)^2}. \tag{M7}
\]

The quadratic dependence on off-diagonal size cannot generally be improved to a
bound linear in \(\|G-\operatorname{Diag}G\|_F\). For \(q=4\), \(s=2\), and

\[
 G=\operatorname{blockdiag}\left(
 \begin{pmatrix}1&e\\e&1\end{pmatrix},
 \begin{pmatrix}1&e\\e&1\end{pmatrix}
 \right),\qquad 0<e<1,
\]

the unrestricted root is \(t_*=\sqrt{1-e^2}\). In the fixed basis, select one
coordinate from \(\{1,3\}\) and one from \(\{2,4\}\), independently and
uniformly, and weight each selected coordinate by two. The two nonzero Gram edges
have joint inclusion probability \(1/4\), so their covariance entries vanish;
the covariance is \(I\). The marginal lower bound has \(u_s=1\), hence
\(\Phi_s(G)=1\). Therefore

\[
 \Phi_s(G)-t_*=1-\sqrt{1-e^2}=\frac{e^2}{2}+O(e^4),
 \qquad \|G-\operatorname{Diag}G\|_F^2=4e^2.
\]

## Alternative equality analysis

## Theorem

The fixed-coordinate class (1) attains covariance bound \(t_*\),

\[
 \lambda_{\max}\!\left(\mathbb E[Z_b^*Z_b]-G\right)=t_*, \tag{3}
\]

if and only if \(G\) is diagonal. Equivalently, the columns of \(R\) are
pairwise orthogonal in the fixed encoded basis.

### Necessity

Put \(H=\mathbb E[Z_b^*Z_b]\), and let \(P_b\) project onto
\(\operatorname{ran}Z_b\). The positive block identity

\[
 \begin{pmatrix}P_b&Z_b\\Z_b^*&Z_b^*Z_b\end{pmatrix}\succeq0
\]

gives, after expectation,

\[
 \begin{pmatrix}K&R\\R^*&H\end{pmatrix}\succeq0,
 \qquad K=\mathbb EP_b,
 \qquad \operatorname{tr}K\leq s. \tag{4}
\]

The generalized Schur complement and full column rank give

\[
 s\geq\operatorname{tr}(RH^{-1}R^*)
 \geq\operatorname{tr}\bigl(R(G+t_*I)^{-1}R^*\bigr)=s. \tag{5}
\]

Here \(H\) is invertible: positivity in (4) forces
\(\operatorname{ran}R^*\subseteq\operatorname{ran}H\), while
\(\operatorname{ran}R^*=\mathbb F^q\). The second inequality in (5) uses
\(H\preceq G+t_*I\), which follows from (3), and inverse order. Equality in the
trace chain forces

\[
 H=G+t_*I,
 \qquad K=R H^{-1}R^*. \tag{6}
\]

Indeed, \(H^{-1}-(G+t_*I)^{-1}\succeq0\), and its trace after congruence by a
full-column-rank \(R\) is zero only when it vanishes. The Schur-complement
remainder \(K-RH^{-1}R^*\succeq0\) likewise has trace zero.

The expected block in (4) now has zero Schur complement. Its kernel contains
every vector

\[
 \binom{x}{-H^{-1}R^*x}.
\]

Every individual positive block has zero quadratic form on this kernel: the
expectation of its nonnegative quadratic form is zero. Factoring its block as
\(\binom{P_b}{Z_b^*}(P_b\ Z_b)\) therefore gives, almost surely,

\[
 P_b=Z_bH^{-1}R^*=RD_bH^{-1}R^*. \tag{7}
\]

Since \(P_b\) is Hermitian and \(R\) has a left inverse, (7) implies
\(D_bH^{-1}\) is Hermitian. The diagonal entries of \(H^{-1}\) are strictly
positive, so this condition first forces every \(b_i\) to be real, and then
forces

\[
 D_bH^{-1}=H^{-1}D_b.
\]

Thus \(D_b\) commutes with \(H\), and hence with \(G=H-t_*I\). Each realized
vector \(b\) is consequently constant on every connected component of the graph
whose edges are the nonzero off-diagonal entries of \(G\).

Finally use \(P_b^2=P_b\) in (7). Cancelling the full-column-rank factors \(R\)
and \(R^*\) gives

\[
 D_bH^{-1}GD_bH^{-1}=D_bH^{-1}. \tag{8}
\]

On a connected component on which the common value of \(b\) is nonzero, (8)
reduces to

\[
 bG=H=G+t_*I.
\]

Hence that Gram block is a scalar multiple of the identity, so it has no
off-diagonal edge. A component containing an edge must therefore have value zero
on every outcome. But \(\mathbb E b_i=1\) forbids this for every coordinate in
such a component. The graph has no edges, and \(G\) is diagonal.

The argument remains valid for unbounded random weights, provided the stated
second moment is finite: all equalities are almost-sure consequences of a
nonnegative integrable quadratic form with expectation zero. It needs only
rank at most \(s\), not exact rank on every outcome.

### Sufficiency

If \(G=\operatorname{Diag}(a_i)\), let

\[
 \pi_i=\frac{a_i}{a_i+t_*}.
\]

Equation (2) gives \(\sum_i\pi_i=s\). Choose an exact-size \(s\)-subset with
these inclusion probabilities and set \(b_i=\mathbf1\{i\in S\}/\pi_i\). Then
\(\mathbb ED_b=I\), \(\operatorname{rank}Z_b=s\) almost surely, and

\[
 \mathbb E[Z_b^*Z_b]
 =\operatorname{Diag}(a_i/\pi_i)=G+t_*I.
\]

Therefore (3) holds. \(\square\)

## Convex formulation and attainment for the full fixed-basis class

The preceding rigidity result concerns the optimum of the whole class (1), not
only a particular Horvitz--Thompson weighting rule. This subsection gives an exact
finite convex formulation of that class.

Let \(\mathcal S_s=\{S\subseteq\{1,\ldots,q\}:|S|\leq s\}\). Conditional on
the realized legal support \(S\), replace a random weight vector \(b\) by its
conditional mean \(\bar b_S=\mathbb E[b\mid S]\). This preserves the global
mean and support constraint. It can only decrease the second moment in PSD order:

\[
 \mathbb E[D_b^*GD_b\mid S]-D_{\bar b_S}^*GD_{\bar b_S}
 =\mathbb E\left[D_{b-\bar b_S}^*G D_{b-\bar b_S}\mid S\right]\succeq0. \tag{9}
\]

Thus one deterministic vector \(b_S\), supported on \(S\), suffices for every
legal subset. Write \(p_S\) for its probability and \(v_S=p_Sb_S\). The mean
constraint is \(\sum_Sv_S=\mathbf1\), with \((v_S)_i=0\) for \(i\notin S\).
For \(p_S>0\), its second-moment contribution is

\[
 p_SD_{b_S}^*GD_{b_S}
 =\frac{(R D_{v_S})^*(R D_{v_S})}{p_S}. \tag{10}
\]

Consequently the exact fixed-basis optimum is the value of the semidefinite
program

\[
 \begin{aligned}
 \Phi_s(G)=\min\ &t\\
 \text{subject to }\quad
 &p_S\geq0,\quad \sum_{S\in\mathcal S_s}p_S=1,\quad
   \sum_{S\in\mathcal S_s}v_S=\mathbf1,\\
 &(v_S)_i=0\quad(i\notin S),\qquad t\geq0,\\
 &\begin{pmatrix}
 G+tI_q & (R D_{v_{S_1}})^* & \cdots & (R D_{v_{S_N}})^*\\
 R D_{v_{S_1}} & p_{S_1}I_p & & 0\\
 \vdots & & \ddots & \\
 R D_{v_{S_N}} & 0 & & p_{S_N}I_p
 \end{pmatrix}\succeq0,
 \end{aligned} \tag{11}
\]

where \(S_1,\ldots,S_N\) enumerate \(\mathcal S_s\). All variables and
constraints in (11) are affine apart from the positive-semidefinite cone, so this
is a finite convex SDP, although its subset list can be exponential in \(q\).

**Proof of equivalence.** Equation (9) maps every admissible random weighting
law to deterministic conditional weights without worsening covariance. For those
weights, the Schur complement of (11) is exactly

\[
 \sum_S\frac{(R D_{v_S})^*(R D_{v_S})}{p_S}\preceq G+tI_q. \tag{12}
\]

Conversely, an SDP point with \(p_S>0\) defines the outcome
\(b_S=v_S/p_S\) with probability \(p_S\). The zero-probability convention is
automatic: a PSD block with lower diagonal block \(p_SI_p=0\) forces
\(R D_{v_S}=0\), and full column rank of \(R\) then forces \(v_S=0\). Thus
(12) is its second-moment bound, while \(\sum_Sv_S=\mathbf1\) gives unbiasedness.
This proves equivalence.

The SDP attains its finite optimum. A finite feasible upper bound exists by
sampling singleton supports with finite inverse-probability weights. Restrict to a
level \(t\leq t_0\) below such a bound. Taking traces in (12) gives

\[
 \sum_S\frac{\|R D_{v_S}\|_F^2}{p_S}
 \leq\operatorname{tr}G+qt_0. \tag{13}
\]

Because \(R\) has full column rank, (13) bounds every \(v_S\); the probability
simplex is compact, the support and mean constraints are closed, and the LMI is
closed under the zero-probability convention. A minimizing subsequence therefore
has a feasible limit.

Since the unrestricted theorem gives \(\Phi_s(G)\geq t_*\), and the rigidity
theorem above characterizes equality, this attainment result has one exact
consequence: for every fixed non-diagonal positive-definite \(G\),

\[
 \Phi_s(G)>t_*.
\]

The positive gap is instance-specific. The earlier quantitative inequality
(M7) bounds it in terms of distance from diagonal structure.

The earlier all-but-one Horvitz--Thompson question is a strict subclass. There the
support law is restricted to complements of singleton pages and the nonzero weights
are fixed by marginal inclusion probabilities. In (11), weights may depend on the
entire selected subset and all supports of size at most \(s\) are allowed. Thus
the HT scalar parametrization is not needed to optimize this broader fixed-basis
class.

## Scope

This rigidity concerns one fixed coordinate basis with diagonal thinning and
subset-dependent scalar weights. It says that such a basis cannot attain the
unrestricted ideal rank-access variance when its residual columns are correlated.
Inequality (M7) quantifies the positive gap. A finite codebook or byte
consequence requires a separate encoding theorem. The unrestricted construction
itself uses a dense singular basis; representing that basis at finite precision
must be charged to a declared description and metadata budget.
