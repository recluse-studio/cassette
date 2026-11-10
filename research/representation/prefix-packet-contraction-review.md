# Review of exact prefix-packet contraction

**Status: the contraction is correct; the contiguous-shrink layout is
rejected.** This note proves the information bound, identifies the metadata
and preparation costs, verifies a scattered-slot realization, and gives a
narrow redundant-array construction that exposes the cost of contiguity.
Polynomial restriction and the in-place transform are classical; no novelty
claim follows from this review.

## 1. Contract and packet lower bound

Let \(\mathbb K\) be a characteristic-two field represented in a fixed
polynomial basis, so field addition is a bitwise XOR of \(b\)-bit words. A
\(P\)-word source record is a degree-at-most-\(D\) Boolean polynomial in
the \(n\) still-unknown identifier bits:

\[
 F(y)=\sum_{\substack{S\subseteq[n]\\|S|\le D}}A_S y_S,
 \qquad A_S\in\mathbb K^P,
 \qquad y_S=\prod_{j\in S}y_j.
 \tag{1}
\]

Put

\[
 \kappa_D(n)=\sum_{j=0}^{\min(D,n)}{n\choose j}.
 \tag{2}
\]

For arbitrary source-specific arrays \(A_S\), every zero-error packet that
must later produce \(F(y)\) for all \(y\in\{0,1\}^n\), without another
external read, needs \(\kappa_D(n)Pb\) bits. Boolean monomials of degree at
most \(D\) are linearly independent, so this is the restriction-space
dimension times the record width. The coefficient packet in (1) attains the
bound.

This lower bound charges all source information available before the later
bits arrive. Reading an original source row, a lower-degree packet, or a
resident coefficient array before the guard contributes to the same packet
information; it cannot evade the bound.

## 2. One-bit contraction

Split on the next unknown bit \(x\), with the remaining bits denoted by
\(z\):

\[
 F(x,z)=A(z)+xB(z),
 \tag{3}
\]

where \(\deg A\le D\) and \(\deg B\le D-1\). For every
\(S\subseteq[n-1]\) of size at most \(D-1\), overwrite the physical array
for \(B_S\) by

\[
 B_S\leftarrow A_S\mathbin{\mathsf{XOR}}B_S.
 \tag{4}
\]

Retain every \(A_S\), including the degree-\(D\) arrays that have no
counterpart in \(B\). Before the guard arrives, the same buffer therefore
contains both exact child packets:

\[
 \begin{array}{c|c}
 x=0&A_S\ (|S|\le D)\\
 x=1&A_S\mathbin{\mathsf{XOR}}B_S\ (|S|\le D-1),\quad
       A_S\ (|S|=D).
 \end{array}
 \tag{5}
\]

The number of arrays remains

\[
 \kappa_D(n-1)+\kappa_{D-1}(n-1)=\kappa_D(n).
 \tag{6}
\]

Thus contraction adds no payload memory. It performs
\(\kappa_{D-1}(n-1)P\) field XORs and the same number of payload writes.
A streaming implementation needs two \(b\)-bit word registers, a loop
counter, and address arithmetic; it does not need a temporary \(P\)-word
array. The preparation must finish after the parent packet arrives and before
the value of \(x\) is needed. If that deadline cannot fund the XORs in (4),
the schedule cannot claim that the selected child is ready when the guard arrives.

After a guard, either child has \(\kappa_D(n-1)\) arrays, containing
\(\kappa_D(n-1)P\) words. The bound in
Section 1 proves this is the minimum source payload for arbitrary degree-\(D\)
records on the surviving \(n-1\) bits.

## 3. Canonical slots: correct, but not physically shrinking

With original coefficients in canonical subset slots, let \(p\) be the
resolved prefix and let \(R\) be a subset of the still-unresolved positions.
Let \(L_q(p)\) denote the most recent \(q\) positions in \(p\) whose guard
value was one. The physical slot for the logical coefficient of \(R\) is

\[
 \phi_p(R)=R\cup L_{\min(D-|R|,\ \#1(p))}(p).
 \tag{7}
\]

This formula is correct. For a zero guard it leaves the selected slot alone.
For a one guard at position \(x\), the logical coefficient of \(R\) moves to
the already-overwritten slot of \(R\cup\{x\}\). If \(|R|<D\), that slot is

\[
 \phi_p(R\cup\{x\})
 =R\cup\{x\}\cup L_{\min(D-|R|-1,\#1(p))}(p),
 \tag{8}
\]

which is exactly (7) with \(x\) as the most recent one. If \(|R|=D\), the
coefficient is shared and remains in place. This proves the recurrence and
then (7) by induction.

The map \(\phi_p\) is injective because intersecting its image with the
unresolved positions recovers \(R\). Hence the targets in (4) neither
collide with each other nor overwrite a source of another update.

Formula (7) removes a \(\kappa_D(n)\)-entry pointer table and a postguard
coefficient copy. It does **not** by itself free RAM: the original packed
allocation still has \(\kappa_D(n)\) arrays, and a selected child is usually
a scattered view of it.

Metadata has a real tradeoff. Retaining the entire resolved-bit mask costs
\(O(r)\) bits. Retaining only the most recent \(D\) one positions costs
\(O(D\log r)\) bits and suffices for (7). Thus \(O(\log r)\) metadata is
possible when \(D\) is fixed. It is impossible uniformly in growing \(D\):
the last \(D\) one positions have \({h\choose D}\) possible states after a
prefix of length \(h\), requiring \(\Omega(\log {h\choose D})\) bits.

Canonical subset rank can be recomputed without a pointer table, but its cost
depends on the physical order. A colex degree order uses \(O(D)\) binomial
terms per coefficient; computing those terms or storing a lookup table is
an additional charge. The actual
three-extent order below uses binary-mask order for lower degrees; directly
counting bounded-weight masks below a mask uses \(O(r)\) binomial terms unless
an additional rank table is stored. An iterator may amortize rank updates,
but its stack and integer arithmetic must still be counted. Each mechanism
is a charged alternative, never a free constant-time pointer.

### Review of the three-extent prefix packet

The companion prefix-jet layout passes this review under its stated source
contract. At a known global prefix of length \(h\), restart the local slot
coordinates on the \(t=r-h\) unresolved variables. The incoming constant,
the lower-degree local coefficients in tail-mask order, and the degree-\(D\)
tail coefficients then fill the three portions of this *new local packet*
without an initial permutation. Formula (7) applies only to guards resolved
after that packet has arrived; applying its tags to the older global prefix
would be a coordinate error.

For degree \(D\), a local tail monomial \(R\) of degree \(D\) has coefficient
\(C_R\): adding any fixed-prefix variable would exceed the degree bound.
Ordering global degree-\(D\) subsets by increasing minimum variable therefore
makes the sets wholly inside the tail one contiguous suffix, at offset
\({r\choose D}-{t\choose D}\). The lower-jet packet has fixed width at each
level and an arithmetic address. Thus the three inputs are logical contiguous
extents with exactly \(\kappa_D(t)P\) payload words. They are not guaranteed
to be three physical blocks; headers, alignment, integrity records, and block
spans remain additional costs.

The reported finite check covers algebraic inversion, every small prefix,
every suffix decode, and the symbolic slot formula. It does not itself prove
a byte-level container rank. Such a rank exists from the stated local order:
rank the empty set first, masks of degree \(1\) through \(D-1\) next, and
degree-\(D\) masks by the declared minimum-variable rank. Its calculation
must still pay the combinatorial arithmetic described above.

## 4. Rejected zero-copy shrinking layout

I attempted to strengthen (7) by arranging three overlapping contiguous
blocks so that either branch could release the discarded part without a copy.
That claim is false. The apparent recurrence fails already for \(D=1\) and
three variables.

Let the next variable be \(x\), followed by \(y,z\), and write the four
coefficient arrays as \([a,c_z,c_y,c_x]\). A zero guard on \(x\) leaves the
child \([a,c_z,c_y]\), which is a valid low-first order for the next split.
A one guard instead leaves \([c_z,c_y,a\mathbin{\mathsf{XOR}}c_x]\).
The high-first order needed for the next \(y\) split is
\([c_y,c_z,a\mathbin{\mathsf{XOR}}c_x]\), with the first two arrays reversed.
Swapping them in the parent breaks the zero branch. The proposed two-order
recurrence therefore lacks its induction step.

No theorem of a copy-free contiguous shrink follows from this counterexample.
The safe choices remain: retain the full original allocation and use the
address formula (7); copy or compact the selected \(\kappa_D(n-1)P\) arrays;
or retain an explicit child pointer/view table. The last two choices must
charge their payload movement or metadata. A general impossibility theorem
for every possible packed permutation remains open here.

There is, however, a narrow sharp stress result. For \(n=3,D=1\), an initial
four-array packet contains \(a,c_z,c_y,c_x\). Requiring both first children
to be contiguous three-array leases forces the shared \(c_y,c_z\) arrays into
the two middle positions and the anchors \(a,c_x\) onto opposite ends. To
make both children contiguous after the next \(y\) guard, the \(x=0\) child
requires \(c_y\) at its outer end, while the \(x=1\) child requires \(c_y\)
at its opposite outer end. No permutation of the four arrays satisfies both.
An exhaustive check of all \(4!\) orders confirms this.

One redundant array repairs this particular case. The five-array word

\[
 [a,\ c_z,\ c_y,\ c_z,\ c_x]
 \tag{9}
\]

prepares the final slot as \(a\mathbin{\mathsf{XOR}}c_x\). The first leases
are \([a,c_z,c_y]\) for \(x=0\) and
\([c_y,c_z,a\mathbin{\mathsf{XOR}}c_x]\) for \(x=1\). Each then has two
contiguous two-array leases at the \(y\) guard. This is a concrete
storage-for-contiguity tradeoff, not a proof of the conjectured
\(2^{n-1}+1\)-array ruler-word layout for larger affine packets.

## 5. Adversarial checks and collision boundary

At \(D=1\), the rejected layout above exposes the smallest ordering failure.
At \(D\ge n\), contraction still reduces to the full Boolean cube with the
same Pascal identity. At a zero-heavy guard path, no XOR target is selected;
at a one-heavy path, every selected coefficient has the latest-one tag in
(7). These cases validate the contraction algebra but do not rescue the
rejected contiguity claim.

The algebra is a triangular change of polynomial coefficients, akin to the
standard Boolean restriction or zeta-transform recurrence. It should not be
called a new codec. Local source coding and polynomial local decoding already
occupy nearby territory; see Makhdoumi, Huang, Médard, and Polyanskiy's
[On Locally Decodable Source Coding](https://arxiv.org/abs/1308.5239).
More directly, Bouillaguet's [Boolean Polynomial Evaluation for the
Masses](https://eprint.iacr.org/2022/1412.pdf) gives in-place low-degree
Möbius and \((u,u+v)\)-style operations. The distinction that (4) preserves
both possible children before a guard resolves is too narrow to support an
originality claim without a direct dual-orientation comparison.

The remaining open problem is a valid packed layout that both supports the
three-extent prefix-jet preload and reduces physical residency after every
guard without a copy or a pointer table. This note does not solve predicate
selection, packet preload, source certification, or arbitrary nonprefix
refinement.
