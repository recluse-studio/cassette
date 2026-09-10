# Independent review: finite advice lower bound for two-column unbiased decoding

Verdict: correct under the stated static one-column oracle model, provided
"additional output randomness" means a source-independent Borel Markov
kernel conditional on the declared state, read column, and query.  Under
that standard interpretation, conditional expectation reduces the decoder
to Borel deterministic branch maps.  I found no mathematical defect in the
claimed bound

\[
 C\ge 2^{-2/(p-2)}N^{-4/(p-2)}
\]

for \(p\ge3\).  This is a correctness review only; it makes no claim about
originality or Cassette significance.

## 1. Model and random branch outputs

For a state with \(0<\theta<1\), finite squared risk at a source frame
implies finite second moment, hence integrability, of each branch output:
each branch appears with a positive fixed probability in a nonnegative
risk average.  Replacing the conditional output by its conditional mean
preserves the exact mean and weakly decreases every squared error by
Jensen's inequality.  Thus it is enough to use Borel functions
\(F_1(a,x)\) and \(F_2(b,x)\).

This reduction needs the usual formal meaning of randomized Borel decoder:
a Borel probability kernel, or a Borel function of its legal inputs and an
independent random seed.  If a branch could draw uncharged,
source-dependent hidden information after the state was chosen, it would
not be a decoder with the declared information pattern.  The main note
should state this convention explicitly; with it, no regularity gap
remains.

The cases \(\theta=1\) and \(\theta=0\) occupy null source cells.  For
example, when \(\theta=1\), exactness for \(e_2\) makes the first branch
output equal to \(b\).  Conditional on a fixed \(a\), this confines \(b\)
to at most one point of \(S^{p-1}\cap a^\perp\), a nonatomic sphere of
dimension \(p-2\ge1\).  Fubini proves nullity.  A finite number of labels
keeps their union null.  This proof does not deteriorate as a nonzero
\(\theta\) tends to zero.

## 2. Exact-mean bundle and countable shared values

For a nondegenerate state, exactness for \(e_1,e_2\) is exactly

\[
 f(a)=g(b),
\]

with

\[
 f(a)=\bigl(\theta F_1(a,e_1)-a,\ \theta F_1(a,e_2)\bigr),
\quad
 g(b)=\bigl(-(1-\theta)F_2(b,e_1),\ b-(1-\theta)F_2(b,e_2)\bigr).
\]

The compact equatorial-averaging atomic-matching theorem applies to this
event on the whole Stiefel distribution.  Intersecting with a measurable
label cell can only reduce the event.  Therefore almost every frame in
that cell has a value in the common countable atom set of \(f_\#\sigma\)
and \(g_\#\sigma\).  No finite atom assertion enters the proof.

For a shared value \(y=(y_1,y_2)\), direct substitution gives

\[
 R(A,e_1)=\frac{\|(1-\theta)a+y_1\|^2}{\theta(1-\theta)},
\qquad
 R(A,e_2)=\frac{\|y_2-\theta b\|^2}{\theta(1-\theta)}.
\]

The uniform risk premise consequently confines the relevant first and
second column sets to balls of radii

\[
 \delta_a=\sqrt{C\theta/(1-\theta)},
 \qquad
 \delta_b=\sqrt{C(1-\theta)/\theta},
 \qquad \delta_a\delta_b=C.
\]

These identities use both coordinate-query risk bounds at the same frame.
They do not assume that a single query-independent output law is optimal;
the theorem requires one static decoder, so its two branch maps can be
bundled simultaneously.

## 3. Radius, atom, and small-set bookkeeping

Assume \(C<1\).  If \(\theta\le1/2\), then
\(\delta_a\le\sqrt C<1\); otherwise
\(\delta_b\le\sqrt C<1\).  This selects one side for the entire label,
including arbitrarily unbalanced nonzero probabilities.

For \(0\le\delta<1\), the normalized spherical measure of every
Euclidean ball intersection satisfies

\[
 \sigma(S^{p-1}\cap B(z,\delta))\le\tfrac12\delta^{p-1}.
\]

The exceptional centre \(z=0\) has empty intersection for \(\delta<1\).
For nonzero \(z\), minimizing the cap threshold over \(\|z\|\) gives
\(\sqrt{1-\delta^2}\), and the beta-integral bound gives the displayed
constant.  Thus the chosen-side atom sets have measure at most

\[
 h=\tfrac12 C^{(p-1)/2}.
\]

The restriction \(C<1\) is essential at precisely this step: a unit ball
centred at zero contains the entire sphere, whereas all chosen radii above
are strictly below one.  The theorem separately treats \(C\ge1\), and
the \(C=0\) case makes every cell null.

For each shared atom, the first- and second-column preimages are disjoint
within their respective countable families.  Enlarging a label cell to the
associated Stiefel rectangle only increases its measure.  The small-set
estimate therefore applies without any product-measure assumption:

\[
 \sum_i\langle 1_{A_i},T1_{B_i}\rangle
 \le\sqrt{D_p}\,h^{(p-2)/(2(p-1))}.
\]

Its proof is sound.  The two-step kernel is
\(C_p(1-t^2)^{-1/2}\); its weak-\(L^{p-1}\) tail gives
\(\sup_a\int_Bk(a^Tb)d\sigma(b)\le D_p\sigma(B)^{(p-2)/(p-1)}\).
Cauchy--Schwarz, self-adjointness of \(T\), and monotone convergence give
the countable disjoint-family estimate.  The constants yield

\[
 1\le N\sqrt{D_p}\,
 2^{-(p-2)/(2(p-1))} C^{(p-2)/4}.
\]

Since \(D_p\le2\), this implies the stated lower bound.  The exponent
calculation is exact:
\((p-1)/2\cdot(p-2)/(2(p-1))=(p-2)/4\).

## 4. Label-specific bases and quantifiers

If state \(\ell\) reads \(AQ_\ell\), use the transformed source
\(\widetilde A=AQ_\ell\) and original queries \(x=Q_\ell e_1\) and
\(x=Q_\ell e_2\).  Then \(Ax=\widetilde A e_j\).  Right multiplication
preserves uniform Stiefel measure, so the estimate applies to each
transformed label cell and then to the original cells.  This handles a
fixed label-specific basis.  It does not handle an additional
source-dependent basis inside a label.

The proof needs finite \(N\) only to discard the degenerate support cells
and to sum the state-cell bounds.  It allows countably many shared atoms
within each cell.  It also uses the supremum over all unit queries exactly
where it invokes both \(e_1\) and \(e_2\), or their label-specific
preimages.  A query-dependent sampling schedule, a mixture of different
read cardinalities, or extra source-dependent state is outside the
proved model.

## Conclusion

Subject to the standard measurable-kernel interpretation of conditional
randomness, the proof establishes the stated finite-advice lower bound.
The only recommended revision is to make that interpretation explicit in
the random-output reduction.  I found no further false pass in the
countability, small-probability, endpoint, fixed-basis, or simultaneous
query steps.

## Reviewed dependencies

- [Main theorem](two_column_unbiased_finite_advice_lower.md).
- [Atomic matching](stiefel_orthogonality_operator_atomic_matching.md).
- [Small-set geometry](stiefel_orthogonality_small_set_bound.md).
