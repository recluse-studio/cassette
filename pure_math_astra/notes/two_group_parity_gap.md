# An exact parity gap for two symmetric coordinate groups

Status: a verified exact family in the fixed-basis model.  It is a
quantitative parity obstruction, not an originality claim or a general
classification theorem.

Let \(q=2n\), \(s=n\), and let \(n\geq1\).  Partition the coordinates into
two groups \(A,B\), each of size \(n\), and set
\[
G=\begin{bmatrix}I_n&\eta J_n\\\eta J_n&I_n\end{bmatrix},
\qquad 0<\eta<1/n,\qquad \rho=n\eta.
\tag{1}
\]
The matrix is positive definite because its two exceptional eigenvalues are
\(1\pm\rho\).

For the fixed-basis class \(Z=RD_b\), with at most \(n\) nonzero diagonal
weights and \(\mathbb ED_b=I\), the exact optimum is
\[
\Phi_n(G)=
\begin{cases}
1,&n\text{ even},\\[1mm]
\displaystyle
1+\frac{\rho}{n^2+\frac{\rho}{2}(n^2-1)},&n\text{ odd}.
\end{cases}
\tag{2}
\]

## Symmetric lower bound

Randomly permute coordinates within \(A\) and \(B\), then independently
average with the group swap.  This preserves unbiasedness and the support
cap, while convexity of the largest eigenvalue does not increase the
objective.  It is therefore enough to lower-bound a symmetrized law.

For an outcome, let \(k,l\) be the numbers of nonzero weights in \(A,B\),
respectively, and let \(U,V\) be the sums of those weights.  Thus
\(k+l\leq n\).  After symmetrization, let
\[
d=\mathbb E\frac{|U|^2/k+|V|^2/l}{2n},
\qquad
c=\frac{\mathbb E(\overline UV)}{n^2},
\tag{3}
\]
where the displayed \(d\) is a lower bound for the true common diagonal
second moment; zero-size terms are omitted.  The group swap makes \(c\)
real, and unbiasedness gives \(\mathbb EU=\mathbb EV=n\).

The symmetrized covariance has diagonal at least \(d-1\) and cross block
\(\eta(c-1)J_n\).  Hence its largest eigenvalue is at least
\[
d-1+\rho|c-1|
\geq d-1+\rho(1-c).
\tag{4}
\]
The same lower bound follows directly if the within-outcome weights have not
been replaced by their group averages, because Cauchy--Schwarz gives (3).

For fixed \(k,l\), the Hermitian quadratic form
\[
\frac{|U|^2/k+|V|^2/l}{2n}
-\rho\frac{\operatorname{Re}(\overline UV)}{n^2}
\tag{5}
\]
is bounded below by
\[
\frac{|U+V|^2}{h(k,l)},\qquad
h(k,l)=
\frac{2n(k+l+2\rho kl/n)}{1-\rho^2kl/n^2}.
\tag{6}
\]
This is the two-variable Cauchy inequality for the positive matrix
\[
\frac1{2n}
\begin{bmatrix}1/k&-\rho/n\\-\rho/n&1/l\end{bmatrix}.
\]
The expression \(h(k,l)\) increases with \(k+l\) and \(kl\).  Under
\(k+l\leq n\), it is maximized at
\[
k+l=n,\qquad kl=\left\lfloor\frac{n^2}{4}\right\rfloor.
\tag{7}
\]
Write \(z=\lfloor n^2/4\rfloor/n^2\).  Averaging (6) and using
\(\mathbb E(U+V)=2n\) gives
\[
d-\rho c\geq
\frac{2(1-\rho^2z)}{1+2\rho z}.
\tag{8}
\]
Combining (4) and (8) yields
\[
\Phi_n(G)\geq
\frac{1+\rho-2\rho z}{1+2\rho z}.
\tag{9}
\]
For even \(n\), \(z=1/4\) and this is one.  For odd \(n\),
\(z=(n^2-1)/(4n^2)\), and (9) is the second value in (2).

## Attainment

Choose \(k+l=n\) with \(kl=\lfloor n^2/4\rfloor\).  In one orientation,
choose a uniform \(k\)-subset of \(A\) and a uniform \(l\)-subset of \(B\),
independently, and give selected coordinates the real weights
\[
\alpha=\frac{2n(n+\rho l)}{n^2+2\rho kl},
\qquad
\beta=\frac{2n(n+\rho k)}{n^2+2\rho kl},
\tag{10}
\]
respectively.  With probability one half, swap the two groups and their
roles.  Each outcome has exactly \(n\) nonzero weights, and
\[
k\alpha+l\beta=2n,
\]
so the swapped mixture is unbiased coordinatewise.  Equality holds in (6)
on every outcome, and \(c\leq1\).  More explicitly,
\[
c-1=
-\frac{n^2(n^2-4kl)}{(n^2+2\rho kl)^2}.
\tag{11}
\]
For even \(n\), this is zero.  For odd \(n\), \(n^2-4kl=1\), which is the
factor implicitly used in the odd formula.  Thus every inequality above is
an equality, proving (2).

This construction uses real weights.  The lower bound already covers
complex weights: replace \(\overline UV\) by its real part in (5), and use
\(\mathbb E|U+V|^2\geq|\mathbb E(U+V)|^2\).

## What the family isolates

The even case has a balanced half-subset law and reaches the marginal
variance one.  The odd case cannot split both groups evenly; the exact
excess in (2) quantifies that parity cost in a dense rank-two interaction.
This is stronger than a bare nonattainability statement, but it concerns a
highly symmetric fixed-basis family.  Extending it to an arbitrary edge
moment design problem, or proving a nontrivial information bound for a
finite encoded-basis library, remains open.
