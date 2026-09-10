# Independent review of the dyadic K4 full-linear page accounting

Status: the finite K4 sampler and its conditional fixed-layout page comparison
are correct. The claim is a one-call expected-traffic statement in the
declared original-column page format. It is not a general byte or hardware
frontier.

## Exact finite sampler

Using rational arithmetic with the oriented K4 incidence matrix, I verified:

\[
\#\{\text{trees}\}=16,\qquad
\det(P_{TT})={1\over16}\quad\text{for every tree }T,
\]

\[
\sum_T H_T=16P,\qquad
\sum_f C_f=4N.
\]

Every \(H_T\) and \(C_f\) has entries in \(\{0,1,-1\}\) and exactly three
nonzero output rows. The first identity is the Cauchy--Binet mean identity;
the second is the oriented face-cycle tight frame. Thus the twenty maps in
the source note are exact rational prototypes.

For \(r=2^{-\ell}\), the high and low masses in Equation (9) sum to one:

\[
16{2^\ell\over16(2^\ell+1)}
+4{1\over4(2^\ell+1)}=1.
\]

Their scaled means are respectively \(P\) and \(N\), so
\(\mathbb EL=I\). The three-row support is literal for every outcome.

The common probability denominator is \(16(2^\ell+1)\), with high weights
\(2^\ell\) and low weights \(4\). The rejection sampler is exact: after
conditioning on acceptance, its \((\ell+1)\)-bit proposal is uniform on
\(2^\ell+1\) values. Its expected fair-bit count is

\[
{(\ell+1)2^{\ell+1}\over2^\ell+1}
+{4\,2^\ell+2\over2^\ell+1}.
\]

The stated strict bound follows. Its bit count is expected only; the
unbounded rejection tail prevents a hard random-bit or latency guarantee.

The shared-table accounting is also correct: \(20\cdot6\cdot6=720\)
ternary entries, hence a simple two-bit encoding uses 1440 bits. The
Elias gamma lengths for \(\ell+1\) and \(m+1\) are as stated. These are
shared format metadata, while the random tree/face selections are runtime
entropy rather than records stored once per block.

## Repeated blocks and the diagonal lower bound

The independent block product has mean identity and exactly \(3m\) nonzero
output rows. Its risk is the maximum of the identical block risks, so the
\(7r\) bound remains valid for a unit query in the \(6m\)-coordinate space.

For a diagonal law with \(\mathbb ED=I\), exact mean gives
\(\mathbb E D_{ii}^2\ge1/p_i\), and
\(\sum_i p_i=\bar s\). Under the residual comparison

\[
G_{\rm res}\succeq a(I_m\otimes G_r),
\]

trace averaging gives exactly

\[
\lambda_{\max}\mathbb E[(D-I)^TG_{\rm res}(D-I)]
\ge {a(1+r^2)\over2}\left({6m\over\bar s}-1\right).
\]

Solving against a \(7r\) full-linear risk gives the selected-column lower
bound in Equation (24). For a no-zero-coordinate query, every selected
diagonal coefficient requires its distinct original-column page. The page
ratio is therefore

\[
{T_{\rm diag}\over T_{\rm full}}
\ge {2\over1+14r/[a(1+r^2)]}.
\]

This is correct for fresh one-call traffic under the declared rule that the
full-linear method fetches all three named pages before coefficient
cancellation. It tends to two as \(r\) tends to zero. For a literal
full-linear traffic advantage at a finite \(r\), the denominator must be
below two, equivalently \(14r<a(1+r^2)\); the note should not be read as
claiming an advantage for every \(r\in(0,1]\).

The dense-page arithmetic is internally consistent. The direct dyadic
factor has a common denominator \(2^{\ell+2}\), and a signed fixed-point
word needs at least \(\ell+3\) data bits under the stated convention. The
quadratic-in-\(m\) traffic is a consequence of deliberately storing each
length-\(6m\) original column as a dense page.

## Conditional Rademacher lift

The optional lift is algebraically valid subject to the previously proved
finite-interpreter Rademacher construction. With \(t=q=6m\), the same
net-and-Bernstein argument gives a dyadic near-isometry \(U\) with
\(p=O(m+b)\), avoidance of every decoded column span, and

\[
(U\mathcal R_{m,\ell}-B)^T(U\mathcal R_{m,\ell}-B)
\succeq(1-\zeta-\delta^2)\,
\mathcal R_{m,\ell}^T\mathcal R_{m,\ell}.
\]

The coefficient law remains the same; the upper risk becomes at most
\(7(1+\zeta)r\). Hence the diagonal trace bound transfers with that
replacement and \(a=1-\zeta-\delta^2\). If \(p=4^h\), the denominator and
numerator bounds stated for \(U\mathcal R_{m,\ell}\) follow from summing at
most six nonzero entries per original K4 column.

This lift remains conditional on a fixed source-independent finite
interpreter range. It does not price the interpreter budget, decoder state,
fair-bit stream, or dense page payload against a different representation.
It also does not cover a free source-dependent decoder or a nonmonomial
right transform. Those are model boundaries, not consequences of the
finite K4 calculation.



## Bounded-bit alternative

The proposed dyadic alternative is correct for \(r=2^{-\ell}\le1/2\).
Use the following outcome masses:

\[
\Pr(H_T\text{ branch})=1-2r,\qquad
\Pr(2H_T\text{ branch})=r,\qquad
\Pr(C_f/r\text{ branch})=r,
\]

with trees uniform within either tree branch and faces uniform in the final
branch. Its mean is exactly

\[
(1-2r)P+2rP+N=I.
\]

It has three rows per outcome, uses only the original twenty prototypes
with integer scales \(1,2,2^\ell\), and has at most 36 distinct scaled
outcome maps.

Let \(h=\|Px\|^2\), \(\lambda=\|Nx\|^2\). The uniform tree law satisfies
\(\mathbb E\|NH_Tx\|^2\le3h\), while the uniform face law satisfies
\(\mathbb E\|C_fx\|^2=3\lambda\). Direct orthogonal expansion gives

\[
\mathbb E\|(P+rN)(L-I)x\|^2
\le(2r+3r^2+6r^3)h+(3r-r^2)\lambda.
\]

For \(0<r\le1/2\), this is at most \(5r\|x\|^2\).

The sampler draws one \(\ell\)-bit integer \(W\). It chooses \(C_f/r\) for
\(W=0\), \(2H_T\) for \(W=1\), and \(H_T\) otherwise, followed by two face
bits or four tree bits. Its worst-case fair-bit use is \(\ell+4\), and its
expectation is

\[
\ell+4(1-r)+2r=\ell+4-2r.
\]

Thus it removes the original sampler's unbounded rejection tail. If this
alternative replaces the original 20-map law in the page comparison, every
occurrence of \(7r\) in the diagonal matching condition may be improved to
\(5r\), changing \(14r/[a(1+r^2)]\) to
\(10r/[a(1+r^2)]\). The original 20-map sampler and its stated accounting
remain correct; this is a stronger optional law with 36 scaled outcomes.

