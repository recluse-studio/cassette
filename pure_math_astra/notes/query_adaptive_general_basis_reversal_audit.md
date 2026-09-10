# Independent audit: general real query-adaptive basis reversal

Reviewed source: `query_adaptive_general_basis_reversal.md`.

Status: the mathematical proof is supported after an independent
reconstruction.  This audit does not grant an originality or Cassette
significance pass.

## Correctness

Let \(p\in(0,1)^q\) have integer sum \(s\), and fix \(i,j\).  Put
\(R=s-p_i-p_j\).  If \(z=\Pr(i,j\in S)\) for an exactly-\(s\) subset,
the four pair-status masses are

\[
 z,\quad p_i-z,\quad p_j-z,\quad 1-p_i-p_j+z.
\tag{1}
\]

They give the lower and first two upper bounds in the source note.  Conditional
on the status, the residual subset has size \(s-2,s-1,s-1,s\), respectively.
Combining the two exactly-one statuses gives the weighted Minkowski sum used
there.  Its support function on an indicator set of size \(k\) is exactly

\[
 z\min(k,s-2)+(p_i+p_j-2z)\min(k,s-1)
 +(1-p_i-p_j+z)\min(k,s).
\tag{2}
\]

The standard ordered-weight decomposition proves that these subset inequalities
and the fixed total characterize the sum: after sorting a linear functional,
write it as a constant plus nonnegative increments of prefix indicators.
For \(k\le s-2\), (2) is \(k\), so coordinate upper bounds suffice.  For
\(k\ge s\), it is \(R\), so nonnegativity and the fixed total suffice.  At
\(k=s-1\), it is \(s-1-z\).  Maximizing the residual marginal sum over such
sets gives \(T\), the sum of the largest \(s-1\) residual marginals.  Hence

\[
 z\in[\max(0,p_i+p_j-1),\ \min(p_i,p_j,s-1-T)].
\tag{3}
\]

This establishes both necessity and sufficiency of the interval.  To make the
last construction explicit, if the aggregate exactly-one residual point is
\(b y\), use the same \(y\in\Delta(s-1,q-2)\) conditional on the \(i\)-only
and \(j\)-only statuses, with their separate masses in (1).  Thus the two
individual marginals, not merely their sum, are correct.

For the extreme marginals \(\alpha=\max p\) and \(d=\min p\), the source
note's slack proof is valid.  With \(C=R-T\), the assumption \(s\le q-2\)
makes the complement defining \(C\) nonempty, so \(C\ge d\).  Also
\(T\le(s-1)\alpha\), hence

\[
 C\ge s(1-\alpha)-d\ge2(1-\alpha)-d.
\tag{4}
\]

Therefore \(C\ge1-\alpha\), and

\[
 s-1-T-\alpha d=C-(1-\alpha)(1-d)
 \ge(1-\alpha)d>0.
\tag{5}
\]

The other interval inequalities are strict at \(z=\alpha d\).  Thus the
two fixed laws with pair moments \(p_ip_j\pm\delta\) exist.  This is the
hard combinatorial step; it is correct.

For diagonal \(D\), conditioning on coordinate inclusion and applying
Cauchy gives the stated marginal program.  Equality with the water-level
upper bound forces the interior marginal vector \(p\) to minimize that
program.  A zero coordinate of \(x\) makes an interior marginal transfer
strictly favorable, so all coordinates are nonzero; the Lagrange equations
then give \(a_r x_r^2/p_r^2\) constant.  This yields precisely the signed
amplitude vector in the source note.  Thus the only unit worst queries for
the diagonal problem are its finite sign orbit.

For the rotated metric, an HT law with marginals \(p\) has off-diagonal
risk contribution

\[
 2g_\tau x_i x_j\left(\frac{z}{p_ip_j}-1\right).
\tag{6}
\]

Choosing the sign of the available deviation in \(z\) makes this
\(-2\delta|g_\tau x_ix_j|/(p_ip_j)\).  Since \(g_\tau\) is a nonzero
multiple of \(\tau+O(\tau^3)\), this proves a uniform linear gain on a
neighborhood of every diagonal maximizer.  The diagonal perturbations are
only \(O(\tau^2)\).

On the complement, the spread \(\Delta=\max e_r-\min e_r\) has a positive
minimum by compactness.  In direction \(f_k-q^{-1}\mathbf1\), the diagonal
HT risk derivative is

\[
 -e_k+q^{-1}\sum_r e_r\le-\Delta/q
\tag{7}
\]

when \(k\) is a maximizer.  A fixed small marginal shift gives a fixed gap;
the metric perturbation is uniformly \(O(|\tau|)\), since the Euclidean
second error moment of every catalog HT law is uniformly bounded.  Combining
the two compact regions gives \(\Psi_s(G_\tau)\le t-c|\tau|\), after
shrinking the \(\tau\) interval.  This handles the supremum over all unit
queries, rather than only the finite diagonal maximizer set.

The catalog count is also correct.  It has two pair-moment laws plus \(q\)
marginal-transfer laws.  Any strictly interior integral-sum marginal vector
has an exact-size subset law.  The cyclic-interval construction in the
source note realizes each transfer law without storing a full probability
table.  For each pair law, the point \((p,z)\) lies in the convex hull of
fixed-size subset incidence vectors augmented by their \(ij\) product.  The
affine dimension is at most \(q\), because \(\sum p=s\); Caratheodory gives
at most \(q+1\) subset outcomes per pair law.

## Boundaries and corrections

The proof is real: complex phases can eliminate the real cross term in (6).
It uses \(2\le s\le q-2\) essentially.  The strict extreme-pair interval
argument needs a residual coordinate outside the largest \(s-1\) set; it
does not extend as written to \(s=q-1\), and the endpoint \(s=1\) has no
pair-inclusion freedom.

The rank-\(s\) fixed-law water-level ideal is a different execution class
from coordinate-hard-cap sampling.  It can use dense rank-\(s\) maps.  The
theorem correctly compares quantifiers as a mathematical benchmark, but it
does not make that ideal a physical \(s\)-column read baseline.  The new
catalog itself is coordinate-hard-cap and uses exactly \(s\) selected columns
per outcome.

The phrase “q+2 fixed HT subset laws” counts laws, not their random subset
outcomes.  The two exceptional laws need finite support of at most \(q+1\)
outcomes each; their probabilities and the rotation still require a declared
finite-precision representation before any byte claim.

## Contribution assessment

The cited atomic-norm and sparsification sources do not directly imply this
theorem.  They supply the inner, fixed-query Euclidean support-gauge problem,
or one-input variance-optimal atomic sampling.  The present argument adds a
nonseparable positive-Gram metric, a worst-query supremum, hard exact support,
and an isospectral perturbation whose finite catalog controls every query.

That does not make the generalization automatically a large independent
advance.  Once the four-coordinate construction is known, its extension is
an elementary but careful synthesis of hypersimplex marginal geometry,
first-order HT risk, and compactness.  The exact pair interval is a slice of
the standard fixed-cardinality marginal/correlation polytope, not a new
polyhedral object.  The meaningful mathematical increment is the uniform
worst-query conclusion with only \(q+2\) procedural laws.  Its Cassette
consequence remains conditional on a declared representation for the
rotation, probabilities, query transform, and page-level reads; it does not
by itself establish a byte or traffic frontier.
