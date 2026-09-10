# Independent review: Stiefel atomic matching and the two-column oracle consequence

Verdict: the compactness and atomicity theorem is correct for \(p\ge3\).
The stated two-column application is also correct after the two coordinate
queries are bundled into one shared value.  It yields countably many
label-specific ball pairs almost everywhere, not a finite atom count.

## 1. Orthogonality operator

For the normalized orthogonality averaging operator

\[
 (T\varphi)(a)=\int_{S^{p-1}\cap a^\perp}\varphi(b)\,d\sigma_a(b),
\]

Stiefel swap invariance makes \(T\) self-adjoint and contractive on
\(L^2(S^{p-1})\).  After two steps, the density relative to uniform sphere
measure is

\[
 k(a^Ta')=\frac{C_p}{\sqrt{1-(a^Ta')^2}}.
\]

Indeed, conditional on \(a\), the first coordinate of the second-step
point has density proportional to
\((1-t^2)^{(p-4)/2}\), while a uniform point of \(S^{p-1}\) has density
proportional to \((1-t^2)^{(p-3)/2}\).  At \(p=3\), this produces the
integrable arcsine singularity \((1-t^2)^{-1/2}\).  Thus truncating \(k\)
gives Hilbert--Schmidt kernels, while the positive tails have row and
column integrals tending to zero.  Schur's test proves that \(T^2\) is
compact.

If \(x_m\rightharpoonup0\) in \(L^2\), then \(T^2x_m\to0\) in norm.
Weak convergence makes \((x_m)\) bounded, and self-adjointness gives

\[
 \|Tx_m\|_2^2=\langle x_m,T^2x_m\rangle\longrightarrow0.
\]

This is the standard weak-null characterization of compactness, so \(T\)
is compact.  The \(p=3\) endpoint causes no gap.

## 2. Common values are atomic

For arbitrary Borel maps \(f,g:S^{p-1}\to\mathbb R^d\), the compactness
argument in the reviewed note correctly proves that the event
\(f(a)=g(b)\), under the uniform Stiefel pair law, has values only in

\[
 \operatorname{At}(f_\#\sigma)\cap\operatorname{At}(g_\#\sigma)
\]

up to null events.  Both atom sets are countable.  The nonatomic partition
step is valid because the restricted sum of the two pushforward measures
has finite nonatomic mass.  The finite-rank approximation controls the
diffuse diagonal without a boundedness condition on \(f\) or \(g\).

The result applies unchanged after intersecting the equality event with
any measurable advice cell: an event restricted to a cell is a subset of
the full matching event.  This is essential.  The two columns of a Stiefel
frame are not independent, so a product-measure atom argument would not
be valid; compactness of \(T\) supplies the required dependence control.

## 3. Exact-mean bundle for one advice label

Fix one label with fixed support probabilities
\(\theta\) for support \(\{1\}\) and \(1-\theta\) for support \(\{2\}\),
where \(0<\theta<1\).  Let \(F_1(a,x)\) and \(F_2(b,x)\) be arbitrary
Borel outputs.  Exact mean recovery on its cell \(C\) says

\[
 \theta F_1(a,x)+(1-\theta)F_2(b,x)=ax_1+bx_2.
\]

Bundle the two coordinate queries into Borel maps to
\(\mathbb R^p\times\mathbb R^p\):

\[
 \begin{aligned}
 f(a)&=\bigl(\theta F_1(a,e_1)-a,\ \theta F_1(a,e_2)\bigr),\\
 g(b)&=\bigl(-(1-\theta)F_2(b,e_1),\
 b-(1-\theta)F_2(b,e_2)\bigr).
 \end{aligned} \tag{1}
\]

The two exact-mean equations say \(f(a)=g(b)\) for every frame in \(C\).
By Section 2, for Stiefel-almost every frame in \(C\), this common value
belongs to a countable set \(Y\) of simultaneous atoms.  Thus \(C\) is,
up to its conditional null set, partitioned by the shared values
\(y=(y_1,y_2)\in Y\).  No finite bound on \(|Y|\) follows.

## 4. Risk balls on one shared atom

Suppose the worst unit-query expected squared error is at most \(C\).
In particular, the two coordinate-query risks are at most \(C\).  On the
shared-value event \(f(a)=g(b)=y\), the \(e_1\) errors are both multiples
of

\[
 d_1=y_1+(1-\theta)a:
\qquad
 F_1(a,e_1)-a=\frac{d_1}{\theta},\quad
 F_2(b,e_1)-a=-\frac{d_1}{1-\theta}. \tag{2}
\]

Their weighted risk is exactly

\[
 \theta\left\|\frac{d_1}{\theta}\right\|_2^2+
 (1-\theta)\left\|\frac{d_1}{1-\theta}\right\|_2^2
 =\frac{\|d_1\|_2^2}{\theta(1-\theta)}
 \le C. \tag{3}
\]

Therefore

\[
 \left\|a+\frac{y_1}{1-\theta}\right\|_2
 \le\sqrt{\frac{C\theta}{1-\theta}}. \tag{4}
\]

Likewise, the \(e_2\) errors are multiples of
\(d_2=y_2-\theta b\), giving

\[
 \left\|b-\frac{y_2}{\theta}\right\|_2
 \le\sqrt{\frac{C(1-\theta)}{\theta}}. \tag{5}
\]

Hence each shared atom confines the ordered frame to one product of two
explicit Euclidean balls, intersected with the Stiefel relation.

The condition \(C<1\) is not needed for (4)--(5).  It may matter only in
a later geometric separation argument; neither radius is necessarily below
one when \(\theta\) is highly unbalanced.

## 5. Quantifiers and limits

The conclusion holds separately for every finite advice label whose
support probabilities are fixed throughout that label cell.  A finite
union of countable atom sets remains countable, but the proof provides no
finite atom count, no ball-covering lower bound, and no water-level
recovery.  It permits arbitrary Borel outputs and uses exact mean recovery
only on the relevant label cell.  A query-dependent support probability,
or a probability that varies with the source inside the label cell, does
not fit the displayed bundle and requires a different argument.
