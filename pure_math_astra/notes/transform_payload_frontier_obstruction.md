# Procedural transforms do not reduce encoded-column traffic

Status: a finite-word resource comparison for the restricted encoded-column
model. It gives a concrete obstruction and a conditional metadata saving.
It is not a Cassette resource certificate.

## 1. Compared representations

Let \(R\in\mathbb Q_{\mathbb F}^{m\times q}\) have entry word length at
most \(L\), and put

\[
 \ell=\left\lceil\log_2(1/\varepsilon)\right\rceil.
\]

Use the procedural decoder theorem at fixed spectral datum \(D\), dimension
\(q\), and read cap \(s\). Its encoded matrix is

\[
 P=RV,
\]

with entries of length

\[
 B_P=O_D(L+\ell).
\tag{1}
\]

The common rational sampler costs \(O_D(\ell)\) shared bits, and each atom
has a transform index of length

\[
 b_{\rm index}=\kappa\ell+O_D(1).
\tag{2}
\]

For comparison, define a dense-table baseline that stores the same encoded
matrix \(P\), together with a separately stored dense transform \(V\) at
the same \(O(\varepsilon)\) operational resolution. Its transform table
uses \(q^2\ell+O_D(1)\) bits per distinct transform. This is the only
finite-word interpretation under which “store the exact dense eigenbasis”
has a definite cost: a literal exact eigenbasis of a rational Gram matrix
may contain irrational entries and is not itself a fixed-word object.

## 2. Resource obstruction theorem

Assume each scheme stores \(P\) and answers a query by reading exactly \(s\)
individually addressable encoded columns. For \(A\) atoms whose transforms
are distinct, the procedural representation and the dense-table baseline
have, up to lower-order shared terms,

\[
 B_{\rm proc}^{\rm total}
=A\bigl[mqB_P+\kappa\ell+O_D(1)\bigr]+O_D(\ell),
\tag{3}
\]

\[
 B_{\rm table}^{\rm total}
=A\bigl[mqB_P+q^2\ell+O_D(1)\bigr].
\tag{4}
\]

Both have abstract fresh traffic

\[
 T_{\rm fresh}=msB_P
\tag{5}
\]

bits per query. Both need a dense transform-sized resident object during
query execution under the stated decoder: the table baseline keeps \(V\),
while the procedural decoder forms a \(q\)-by-\(q\) rational matrix. Thus
both have transform workspace or residency of order

\[
 q^2O_D(\ell)
\tag{6}
\]

bits, before any active encoded-column buffers.

**Proof.** Equations (1)--(2) are the procedural decoder bounds. The
encoded matrix contains \(mq\) words in either representation, which gives
(3)--(4). A fresh correction reads \(s\) full \(m\)-entry columns in either
case, proving (5). The procedural Cayley decoder explicitly forms and
inverts a \(q\)-by-\(q\) matrix; the stored-table route retains a matrix of
the same order. This gives (6). \(\square\)

The procedural route therefore saves only transform-description bits:

\[
 B_{\rm table}^{\rm total}-B_{\rm proc}^{\rm total}
=A(q^2-\kappa)\ell+O_D(A+\ell).
\tag{7}
\]

The coefficient is positive:

\[
 \kappa=\frac{\beta(N+k)}2\leq\beta N<q^2,
\tag{8}
\]

because \(N\leq q(q-1)/2\), \(k\leq N\), and
\(\beta\in\{1,2\}\). A direct orbit-coordinate eigenbasis encoding has
dimension \(d=\beta N\), so the corresponding saving is only

\[
 (d-\kappa)\ell=\frac{\beta(N-k)}2\ell.
\tag{9}
\]

This identifies the actual source of the gain: the variance theorem reduces
the resolution required in transform coordinates with zero covariance
coefficients. It does not compress the encoded matrix.

## 3. Consequences for a resource frontier

Under a fixed rational-word convention that charges every stored encoded
scalar \(\Theta_D(L+\ell)\) bits, the maximum table-saving fraction of the
mandatory payload is bounded by

\[
 \frac{(q^2-\kappa)\ell}{mqB_P}
\leq O_D\!\left(\frac qm\right).
\tag{10}
\]

It tends to zero for \(m/q\to\infty\), even before the sampler and decoder
are charged. Equation (5) is unchanged. Equation (6) is unchanged in
order. Thus, in this model, procedural transform coding cannot improve the
fresh-traffic coordinate or the dense-transform peak-residency coordinate
of the resource vector. In the \(m\gg q\) regime it also cannot create a
leading-order total-description improvement.

Without this word convention, (1) is only an upper bound on the bit length
of \(P\); accidental cancellations or a different payload code can change
the comparison. The invariant scalar-count statement remains that both
routes retain \(mq\) encoded entries and read \(ms\) entries.

There is a conditional total-metadata advantage when many atoms have
distinct transforms and \(m\) is comparable to \(q\) or smaller. That is a
trade in \(b_{\rm desc}^{\rm total}\), not a proof of improvement in
\(b_{\rm desc}^{\rm peak}\), \(t_{\rm fresh}^{\max}\), or
\(t_{\rm fresh}^{\rm total}\). MATHS.md requires those resource coordinates
to remain separate.

## 4. Growing dimensions and finite-word lower bounds

The transform-cover lower bound becomes a finite-word lower bound only for
source families containing an \(O(\varepsilon)\)-net of the orbit. The
procedural decoder gives one sufficient condition:

\[
 L(\varepsilon)\geq L_0+C_D\ell.
\tag{11}
\]

This is a fixed-\(D\), fixed-\(q\) statement. If \(q\), the spectral
condition number, a minimum eigenvalue, or an eigenvalue gap grows or
shrinks with \(\varepsilon\), then \(C_D\), the atlas size, rational
arithmetic constants, and \(\kappa\) can vary. Equations (7)--(11) give no
uniform growing-dimension frontier without explicit non-asymptotic bounds
on those quantities.

The exact dense eigenbasis baseline has the same limitation. A rational
source need not have a rational eigenbasis, so an “exact” table needs a
separate algebraic-number or approximation model. The comparison above
holds only when both routes use the same declared operational transform
accuracy and the same encoded-column payload precision.

## 5. What would move the frontier

To obtain a nontrivial fresh-traffic or peak-byte consequence, a further
theorem must change one of the quantities untouched above. Examples include
a structured transform application using subquadratic resident workspace,
a page layout in which selected encoded columns cost fewer physical bytes,
or a representation that avoids storing all \(mq\) entries of \(RV\).
The current transform-cover theorem proves none of these. Its established
consequence is the conditional transform-metadata saving (7).
