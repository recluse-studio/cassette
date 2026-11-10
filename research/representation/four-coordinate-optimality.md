# Four-coordinate signed-sum two-sparse optimality

**Status.** This is an independently derived sharp theorem, checked by two
workspace derivations and finite numerical attacks.  It establishes an
optimized *query-time decoder* in four real coordinates.  It is not a
weight representation, a page-code lower bound, or an originality claim.
The construction and proof were developed jointly by the root task and this
geometry lane; no claim about priority follows from that fact.

## 1. Contract and finite decoder

For \(x\in\mathbb R^4\), write \(t=\mathbf1^Tx\), and define

\[
 \Phi(x)=\inf\left\{\mathbb E\|Y-x\|_2^2:
 \mathbb EY=x,\quad \|Y\|_0\le2,\quad
 \mathbf1^TY=\mathbf1^Tx\quad\hbox{almost surely}\right\}.
 \tag{1}
\]

The support condition permits one-coordinate outputs.  They cause no
technical exception: \(te_i\) lies on every pair line containing \(i\).

Every feasible law can be compressed to a finite six-pair law.  Let
\(E=\{ij:1\le i<j\le4\}\), orient each pair \(ij\) from \(i\) to \(j\),
and let \(B\) and \(C\) have columns \(e_i-e_j\) and \(e_i+e_j\),
respectively.  The closed-perspective programme is

\[
 \begin{aligned}
 \Phi(x)+\|x\|_2^2
 =\min_{\theta,z}\quad&\sum_{e\in E}\frac{\|z_e\|_2^2}{\theta_e}\\
 \text{subject to}\quad&\theta\ge0,\quad\mathbf1^T\theta=1,\quad
     \sum_e z_e=x,\\
 &\operatorname{supp}(z_e)\subseteq e,\quad
     \mathbf1^Tz_e=t\theta_e\quad(e\in E).
 \end{aligned}
 \tag{2}
\]

The closed-perspective convention is \(0/0=0\), while a nonzero numerator
at \(\theta_e=0\) is \(+\infty\).  Indeed, group a feasible law by its
selected pair and set \(z_e=\mathbb E[\mathbf1_{\{E=e\}}Y]\).
Conditional Jensen gives the objective in (2).  Conversely, conditionally
returning \(z_e/\theta_e\) on each positive-probability pair attains it.

The programme is nonempty with every \(\theta_e=1/6\): take
\(z_e=\theta_e t(e_i+e_j)/2+f_e(e_i-e_j)\), where
\(f_{ij}=(x_i-x_j)/4\).  A bounded objective sublevel is compact: each
nonnegative summand gives \(\|z_e\|_2^2\le C\theta_e\le C\), while the
simplex is compact.  The closed perspective makes the sublevel closed.  The
minimum therefore is attained.  This also makes the resulting finite convex
value function closed on its affine hyperplane, which justifies the Fenchel
step used below.

Writing \(p=\theta\) and parameterizing every edge flow by
\(z_e=p_e t(e_i+e_j)/2+f_e(e_i-e_j)\) reduces (2) to

\[
 \Phi(x)+\|x\|_2^2=
 \min_{\substack{p\ge0,\ \mathbf1^Tp=1\\
                 f\in\mathbb R^6,\\
                 x=\frac t2Cp+Bf}}
 \left\{\frac{t^2}{2}+2\sum_{e\in E}\frac{f_e^2}{p_e}\right\}.
 \tag{3}
\]

An optimizer emits pair \(e=ij\) with probability \(p_e\) and returns

\[
 Y_e=\frac t2(e_i+e_j)+\frac{f_e}{p_e}(e_i-e_j).
 \tag{4}
\]

Thus the optimum has at most six deterministic two-coordinate outcomes.
Equation (3) is a fixed six-pair second-order cone programme.  It supplies a
finite query-time interpretation once its arithmetic tolerance, random-bit
generator, and selected-column layout are separately charged.  The sharper
theorem below concerns its exact real value only.

## 2. Sharp theorem

**Theorem.** For every \(x\in\mathbb R^4\),

\[
 \Phi(x)\le(\sqrt{13}-2)\|x\|_2^2,
 \tag{5}
\]

and the constant is best possible.  Hence

\[
 \sup_{x\ne0}\frac{\Phi(x)}{\|x\|_2^2}=\sqrt{13}-2
 \approx1.60555127546.
 \tag{6}
\]

### Proof of the upper bound

Put \(M_t(x)=\Phi(x)+\|x\|_2^2\), on the hyperplane
\(\mathbf1^Tx=t\), and let

\[
 \kappa=\sqrt{13}-1.
 \tag{7}
\]

The convex-envelope dual of (2) is

\[
 M_t(x)=\sup_{\lambda\in\mathbb R^4}
 \left\{\lambda^Tx-\max_{i<j}q_{ij}(\lambda)\right\},
 \tag{8}
\]

where maximizing \(\lambda^Ty-\|y\|_2^2\) along
\(y_i+y_j=t\) gives

\[
 q_{ij}(\lambda)=\frac t2(\lambda_i+\lambda_j)-\frac{t^2}{2}
 +\frac{(\lambda_i-\lambda_j)^2}{8}.
 \tag{9}
\]

For a fixed \(t\) and \(\lambda\), the maximum of
\(\lambda^Tx-\kappa\|x\|_2^2\) on that hyperplane is

\[
 \frac{\|P\lambda\|_2^2}{4\kappa}
 +t\bar\lambda-\frac{\kappa t^2}{4},
 \qquad
 P=I-\frac{\mathbf1\mathbf1^T}{4},\quad
 \bar\lambda=\frac{\mathbf1^T\lambda}{4}.
 \tag{10}
\]

It therefore suffices to show that (10), minus the maximum in (8), is
nonpositive.  The assertion is homogeneous.  For \(t>0\), scale to \(t=1\),
order the four coordinates of \(\lambda\), and shift them to write

\[
 \lambda_1=0,\qquad\lambda_2=-a,\qquad\lambda_4=-b,
 \qquad0\le a\le b.
 \tag{11}
\]

For \(u\ge v\), the derivative of \(q(u,v)\) with respect to \(u\) is
\(1/2+(u-v)/4\ge0\).  The maximizing pair therefore contains
\(\lambda_1\).  Since the expression is convex in its other coordinate,

\[
 \max_{i<j}q_{ij}=\max\{q_{12},q_{14}\}.
 \tag{12}
\]

The left side of the desired inequality is convex in the remaining
coordinate \(\lambda_3\in[-b,-a]\).  Its maximum is consequently at
\(\lambda_3=-a\) or \(-b\).  Define

\[
 h(d)=-\frac d2-\frac12+\frac{d^2}{8}.
 \tag{13}
\]

Then \(q_{12}=h(a)\), \(q_{14}=h(b)\), and

\[
 h(b)-h(a)=\frac{(b-a)(a+b-4)}8.
 \tag{14}
\]

Multiply the desired inequality by \(16\kappa\).  If \(a+b\le4\), the
larger pair value is \(h(a)\), and the two endpoint choices for
\(\lambda_3\) give

\[
 \begin{aligned}
 N_1&=(4-2\kappa)a^2-4ab+3b^2-4\kappa b+8\kappa-4\kappa^2,\\
 N_2&=(3-2\kappa)a^2-4ab+4b^2+4\kappa a-8\kappa b+8\kappa-4\kappa^2.
 \end{aligned}
 \tag{15}
\]

Both are convex in \(b\in[a,4-a]\).  Their maxima are at \(b=a\) or
\(b=4-a\).  At the first endpoint both equal

\[
 (3-2\kappa)a^2-4\kappa a+8\kappa-4\kappa^2<0.
 \tag{16}
\]

At \(b=4-a\), both are convex in \(a\in[0,2]\), so only the endpoints
remain.  Their values at \((a,b)=(0,4)\) are

\[
 48-8\kappa-4\kappa^2=0,
 \qquad 64-24\kappa-4\kappa^2=16-16\kappa<0,
 \tag{17}
\]

and at \((2,2)\) both equal \(12-8\kappa-4\kappa^2<0\).

If \(a+b\ge4\), the larger pair value is \(h(b)\), producing

\[
 \begin{aligned}
 R_1&=4a^2-4ab+(3-2\kappa)b^2-8\kappa a+4\kappa b+8\kappa-4\kappa^2,\\
 R_2&=3a^2-4ab+(4-2\kappa)b^2-4\kappa a+8\kappa-4\kappa^2.
 \end{aligned}
 \tag{18}
\]

These are convex in \(a\).  At \(a=b\) they reduce to (16).  For
\(2\le b\le4\), the other endpoint \(a=4-b\) belongs to the preceding
boundary.  For \(b\ge4\), it is \(a=0\).  There \(R_1\) is concave and
decreases after its value \(0\) at \(b=4\); \(R_2\) decreases and is already
negative at \(b=4\).  This completes the case \(t>0\).  The identities use

\[
 \kappa^2+2\kappa=12.
 \tag{19}
\]

For \(t<0\), negate both \(x\) and \(Y\).  For \(t=0\), take the homogeneous
leading-coefficient limit of the just-proved dual inequality, equivalently
apply (8)--(10) with \(q_{ij}=(\lambda_i-\lambda_j)^2/8\).  The same bound
follows.  Therefore \(M_t(x)\le\kappa\|x\|_2^2\), which proves (5).
\(\square\)

### Equality witness

Let

\[
 r_*=\frac{5+2\sqrt{13}}9,
 \qquad x_*=(r_*,r_*,r_*,-1),
 \qquad t_*=3r_*-1.
 \tag{20}
\]

For every \(r\ge1\), use the following two-pair law on
\(x=(r,r,r,-1)\), with \(t=3r-1\).  Select a positive-positive pair,
uniformly among its three choices, with total probability \(1-2/t\), and
write \(t/2,t/2\) on it.  Select a positive-negative pair, uniformly among
its three choices, with total probability \(2/t\), and write
\(3t/2,-t/2\) on it.  The law preserves the coordinate sum outcome by
outcome and has mean \(x\).  Its squared-error ratio is

\[
 \frac{\mathbb E\|Y-x\|_2^2}{\|x\|_2^2}
 =\frac{\tfrac32r^2+9r-\tfrac92}{3r^2+1}.
 \tag{21}
\]

The derivative has the sign of \(-3(9r^2-10r-3)\); its maximum is at
\(r=r_*\), with value \(\sqrt{13}-2\).  The dual witness for the normalized
query \(x_*/t_*\) is

\[
 \lambda=(0,0,0,-4).
 \tag{22}
\]

It gives equality in the first value of (17), hence equality in (8) and
(10).  The feasible law and dual certificate match, proving sharpness.

## 3. Exact Gram corollary

Let \(A\in\mathbb R^{p\times4}\) obey

\[
 A^TA=\mathbf1\mathbf1^T+\eta I_4,
 \qquad \eta\ge0.
 \tag{23}
\]

For the optimal law in (1), each outcome has
\(\mathbf1^T(Y-x)=0\).  Thus

\[
 \begin{aligned}
 \mathbb E\|A(Y-x)\|_2^2
 &=\mathbb E (Y-x)^T(\mathbf1\mathbf1^T+\eta I_4)(Y-x)\\
 &=\eta\,\mathbb E\|Y-x\|_2^2\\
 &\le\eta(\sqrt{13}-2)\|x\|_2^2.
 \end{aligned}
 \tag{24}
\]

The decoder reads at most two original columns of \(A\) in one outcome.  For
an exact block-diagonal source with Gram
\(I_m\otimes(\mathbf1\mathbf1^T+\eta I_4)\), apply the law independently
on every four-coordinate query block.  The result reads at most \(2m\)
original columns and has error at most

\[
 \eta(\sqrt{13}-2)\|x\|_2^2.
 \tag{25}
\]

This improves the earlier \(5\eta/3\) bound for the same signed-sum,
two-column contract.  It is an established-method comparator improvement:
no resident source-dependent representation, encoded page, or RAM saving
has been proved here.

## 4. Collision review and boundary

The ingredients overlap known work.  Wang et al.,
[ATOMO](https://proceedings.neurips.cc/paper_files/paper/2018/file/33b3214d792caf311e1f00fd22b392c5-Paper.pdf),
optimize unbiased atomic sparsification across several atomic bases.  Barnes
et al., [Efficient Unbiased Sparsification](https://arxiv.org/html/2402.14925),
study hard unbiased sparsification and include coordinate-sum preservation
in their problem family.  Deville and Tillé's
[cube method](https://doi.org/10.1093/biomet/91.4.893) is an established
route for balanced random selection.  These sources rule out a general
novelty claim for unbiased hard sparsification, balancing, conditional
Jensen, or finite pair sampling.

The checked sources do not, by themselves, establish the exact all-real,
mixed-sign, pathwise signed-sum, four-coordinate constant in (6).  That is a
narrow non-collision observation, not proof that the theorem is new.  A
publication-level originality claim would require a dedicated search through
convex-envelope, survey-sampling, dependent-rounding, and randomized
numerical-linear-algebra results.

The result leaves the requested representation problem open.  A competitive
claim still needs a finite source code, charged decoder and random-bit
arithmetic, an addressable page format, a resident-RAM account, and an
optimal comparison against arbitrary encoded pages.
