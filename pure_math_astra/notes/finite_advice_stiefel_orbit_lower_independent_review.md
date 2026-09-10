# Independent review: finite-advice Stiefel-orbit lower bound

Status: verified under the stated finite-label, label-static model, subject
to the explicit \(C=0\) repair in Section 6.  This review checks
correctness only.  It makes no originality or resource-significance claim.

The reviewed result concerns \(A\in\mathcal V_{p,q}\), \(p>q\), a
measurable source-to-label map with \(N\) values, and for each label one
support distribution that is independent of both the source within that
label cell and the query.  A decoder may be an arbitrary Borel function of
the label, selected columns, support, and query.  Exact unbiasedness is
not used.

## 1. Missing-pair selection

For a fixed label \(a\), apply the uniform risk bound to the \(q\)
coordinate queries and retain only pairs for which \(j\notin S\).  This
gives

\[
 \sum_S\sum_{j\notin S}p_S^a e_{S,j}(A)\le qC,
 \qquad
 e_{S,j}(A)=\|F_S^a(A_{:S},e_j)-A_{:j}\|_2^2. \tag{1}
\]

Because the same law \(p^a\) occurs for every coordinate query,

\[
 \sum_S\sum_{j\notin S}p_S^a
 =q-\sum_Sp_S^a|S|
 \ge q-\bar s=qd. \tag{2}
\]

Thus one positive-weight pair obeys
\(e_{S,j}(A)\le C/d\).  This is a weighted-average argument; no
unbiasedness, linearity, or continuity of \(F_S^a\) enters it.

The number of possible pairs is exactly

\[
 \sum_{S\subseteq[q]}(q-|S|)
 =q\,2^{q-1}=H_q. \tag{3}
\]

Under \(|S|\le s\), the exact count is

\[
 \sum_{k=0}^s(q-k)\binom qk
 =q\sum_{k=0}^s\binom{q-1}k=H_{q,s}. \tag{4}
\]

Both counts used in the reviewed note are correct.

## 2. Conditional spherical cap

Condition on \(X=A_{:S}\), where \(k=|S|\).  Haar invariance of the
Stiefel law makes \(A_{:j}\), for \(j\notin S\), uniform on the unit sphere
of \(\operatorname{span}(X)^\perp\), whose ambient dimension is

\[
 n=p-k\ge p-q+1\ge2. \tag{5}
\]

For fixed \(X\), the Borel output \(F_S^a(X,e_j)\) is fixed.  Projecting
that output to \(\operatorname{span}(X)^\perp\) can only enlarge the
corresponding cap.  If \(V\) is uniform on \(S^{n-1}\), the largest
intersection with an Euclidean ball of radius \(0<\delta<1\) has cap
threshold at least \(\sqrt{1-\delta^2}\).  For \(n\ge3\), the
first-coordinate density and

\[
 1-\sqrt{1-\delta^2}\le\delta^2,\qquad
 1-t^2\le\delta^2
\]

give

\[
 \Pr(\|V-z\|_2\le\delta)\le\sqrt n\,\delta^{n-1}. \tag{6}
\]

The normalizing density constant is at most \(\sqrt n\).  For \(n=2\),
the maximal normalized arc length is at most \(\delta\), hence at most
\(\sqrt2\delta\).  Therefore the constant and exponent in the reviewed
cap inequality are valid.

For unrestricted supports, \(n-1=p-|S|-1\ge p-q\), so

\[
 \sqrt n\,\delta^{n-1}\le\sqrt p\,\delta^{p-q}. \tag{7}
\]

For a hard cap, the corresponding exponent is at least \(p-s-1\).
These are the claimed exponents.

## 3. Cells, union bound, and quantifiers

For one fixed label and pair, Fubini disintegration applies to the
measurable cap event, even though the advice cell can cut across the
conditional fibers.  Intersecting a cap event with its cell can only
decrease measure.  The finite union over (3), then the finite union over
the \(N\) cells, yields

\[
 1\le NH_q\sqrt p\,\delta^{p-q}. \tag{8}
\]

The same argument with (4) gives the hard-cap form.  Substituting
\(\delta^2=C/d\) proves the stated lower bounds.

No measurable choice of the successful pair is needed.  Pointwise
existence from (1)--(2) says that every source lies in a finite union of
already measurable pair events.  Thus arbitrary measurable advice cells
and arbitrary Borel nonlinear, biased decoders are covered.

The conclusion must remain supremum-safe: for every claimed bound strictly
below the displayed lower bound there exist a source and a unit query with
larger expected error.  This follows by contradiction from a strict
uniform upper bound.  The proof does not show that a worst source or query
attains the supremum.

## 4. Expected reads and hard cap

The expected-read theorem requires (2) separately for every advice label.
A budget averaged only over sources or labels would not imply (2) on every
cell and the proof would fail.  Occasional full reads are allowed in the
expected-read model; they simply contribute no missing pair on those
outcomes, while (2) forces enough omitted mass overall.

The hard-cap statement is a separate strengthening.  Its exponent
\(p-s-1\) uses a per-outcome cap, not an expected-read condition.

## 5. Exact boundaries and false passes

The proof does not extend to a query-dependent support law from the same
calculation.  If \(p_S^a\) is replaced by \(p_S^a(\,\cdot\mid x)\), then
the identity in (2) no longer follows after summing coordinate queries.
For example, the schedule for query \(e_j\) can always read coordinate
\(j\), using one read, so the retained coordinate-error mass can vanish.
This does not construct a low-risk query-adaptive scheme for every query;
it shows that the missing-pair proof is static-schedule-specific.

The condition \(p>q\) is also essential.  At \(p=q=2\), write the source
as \(A\in O(2)\), use one advice bit for \(\det A\), always read \(A_{:1}\),
and return

\[
 x_1A_{:1}+x_2(\det A)J A_{:1}. \tag{9}
\]

This reconstructs \(Ax\) exactly.  The conditional missing-column fiber
has only two points, so the spherical-cap exponent in (7) is unavailable.

Arbitrary *finite* labels are covered, regardless of what source property
selects a label, provided all source-dependent state is exhausted by that
label and the label-specific decoder and schedule are fixed.  In
particular, each of the finitely many labels may name an arbitrary resident
matrix or function.  The theorem excludes resident state with more than
\(N\) distinct source-dependent values, a source-dependent schedule within
one label cell, unbounded labels, adaptive later reads, or
source-dependent random seeds. Independent output randomness can be removed
by taking the conditional mean given the label, support, observed columns,
and query. Jensen's inequality preserves the risk upper bound and reduces
that case to the displayed deterministic Borel decoder model.

The same proof also covers a finite label-specific orthogonal right-basis
catalog when a selected column means a column of \(AQ_a\).  For label \(a\),
test the original query \(x=Q_ae_j\), whose target is
\(AQ_ae_j\).  The map \(A\mapsto AQ_a\) preserves the Stiefel law, so the
same missing-pair union and cap estimate apply after this change of
coordinates.  This extension still needs a support law fixed within each
label and a finite basis catalog.

## 6. One technical repair

The reviewed proof invokes the cap estimate only for \(0<\delta<1\).
When \(C=0\), it sets \(\delta=0\) and therefore needs one separate
sentence: every fixed pair event is a singleton cap in a sphere of
dimension at least one and has conditional measure zero; its finite union
cannot cover a nonnull advice cell, let alone the whole orbit.  Hence
\(C=0\) is impossible.  After this sentence, the proof may assume
\(0<\delta<1\).  This repair does not change either bound.
