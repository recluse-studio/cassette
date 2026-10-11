# Exact weight packets prepared before a region choice resolves

**Status: independently derived construction, proved for the source family below; originality
unestablished.** The construction combines a small arithmetic locator, exact encoded weight
packets, and preparation before a pending branch resolves. It does not establish that a dense
model has this source structure or that its routing exposes the required branch order.

The source family's restriction coefficients are called a *jet* here. This name does not imply
analytic differentiation. Every operation on the encoding is a bitwise XOR; the decoded words
return to the model's ordinary arithmetic unchanged.

## 1. Source and control contracts

There are \(N=2^r\) source records. Each record contains \(P\) words of \(b\) bits, with
\(b\) a positive multiple of eight. Put \(L=Pb/8\) bytes. Let \(1\le D\le r\), and assume
the exact source identity

\[
 W(u)=\bigoplus_{S\subseteq[r],\ |S|\le D} C_S\prod_{j\in S}u_j,
 \qquad u\in\{0,1\}^r.                                      \tag{1}
\]

Each \(C_S\) is an array of \(P\) original-width words. Multiplication by a Boolean bit
means retain or zero the array; addition means XOR. Thus no finite-field multiplication or
numerical change of the model's scalar values is needed. Equation (1) applies separately to
every bit of every word. A complete Boolean Möbius transform constructs the coefficients.
The compiler must check that every coefficient of degree above \(D\) vanishes, or compare
the reconstructed value of every record with its source value. Sampling does not certify (1).

The next normal operation uses the record whose identifier is produced by declared ordinary
control calculations. These calculations reveal identifier bits in order. A known prefix
\(p\in\{0,1\}^h\) leaves \(t=r-h\) unresolved bits. The actual guard arithmetic,
its weights, and its workspace are separate charged work. The construction uses a prefix
already produced by that arithmetic; it does not derive a dense model's relevance relation.
Every suffix is assumed possible. A smaller feasible set requires its own proof and packet.

## 2. Exact information needed before the choice resolves

Restriction of (1) to a prefix gives

\[
 W(p,v)=\bigoplus_{R\subseteq\{h+1,\ldots,r\},\ |R|\le D}
 A_R(p)\prod_{j\in R}v_j,
\]

where

\[
 A_R(p)=\bigoplus_{S:\ S\cap\{h+1,\ldots,r\}=R}
 C_S\prod_{j\in S\cap[h]}p_j.                              \tag{2}
\]

Write \(\kappa_D(t)=\sum_{j=0}^{\min(D,t)}\binom tj\). The packet of coefficients in
(2) contains exactly \(\kappa_D(t)L\) bytes. It can reconstruct every remaining possible
record, without another source read after the identifier resolves.

**Theorem 1.** With no prior source-dependent information supplied for free, every universal
zero-error packet serving all completions of this prefix needs at least
\(\kappa_D(t)Pb\) source-information bits. The coefficient packet attains this bound.

**Proof.** The degree-at-most-\(D\) monomials on \(t\) Boolean variables are linearly
independent over \(\mathbb F_2\). Every assignment of their \(P b\)-bit coefficient
arrays occurs in the source family by setting coefficients involving prefix variables to
zero. There are \(2^{\kappa_D(t)Pb}\) distinct restricted record tables. Two such tables
cannot share the same entire resident state: some legal suffix would then require different
exact records from the same state. The packet supplies one coefficient for each independent
monomial and distinguishes all tables. \(\square\)

The bound includes source information already resident before packet arrival. Its source
family permits every coefficient assignment at the fixed observed prefix; if the guard itself
reveals source-dependent restrictions on those coefficients, condition the counting argument
on that information instead. It is a worst-case, fixed-capacity bound over the stated family.
It is not a lower bound for every
individual compressible source. It also does not cover schedules that read more source
information after the remaining control bits arrive.

## 3. A packet from at most three logical extents

A minimal packet is insufficient if forming it requires a source scan. The following external
layout makes its payload directly accessible.

1. Keep original records in binary identifier order. The constant coefficient is
   \(A_\varnothing(p)=W(p,0^t)\), at source-record index \(p2^t\).
2. Store all global degree-\(D\) coefficients by increasing minimum variable index, with
   a fixed ordering within each group. If \(|R|=D\), then \(A_R(p)=C_R\): no source
   monomial of greater degree can contribute. All \(R\) wholly inside the unresolved tail
   form a contiguous suffix, starting at coefficient index
   \(\binom rD-\binom tD\) and containing \(\binom tD\) arrays.
3. For every prefix length \(h<r\), store the coefficients of degrees
   \(1,\ldots,\min(D-1,r-h)\) for each binary prefix as one fixed-width record. Its
   length in coefficient arrays is
   \(j_D(t)=\sum_{j=1}^{\min(D-1,t)}\binom tj\). Its array offset is

   \[
   B_h+p j_D(r-h),\qquad
   B_h=\sum_{a=0}^{h-1}2^a j_D(r-a).                         \tag{3}
   \]

The locator computes (3), the source anchor, and the degree-\(D\) suffix from integers
\(r,D,h,p,L\) and three base addresses. No table with an entry for every prefix resides
in RAM. Binomial coefficients can be computed with integer arithmetic and constant-count
registers; their bit widths and arithmetic cost grow with \(r\), and are charged.

The three payloads contain exactly \(\kappa_D(t)L\) bytes in total. Empty extents are
omitted. For \(D=1\), only the source anchor and coefficient suffix are needed. For
\(t=0\), only the final original record is needed.

These are **logical contiguous payload extents**, not three physical blocks or a measured
three-request Cassette path. For block size \(Q\), an unaligned extent of \(x>0\) bytes
occupies at most \(1+\lceil x/Q\rceil\) blocks. Container headers, integrity proofs,
store lookups, alignment, request limits, and read buffers add their actual costs. Integrity
metadata cannot be silently placed in the small locator.

## 4. External storage

The layout stores this many \(P\)-word arrays before headers and alignment:

\[
 E_D(r)=2^r+
 \sum_{h=0}^{r-1}2^h\sum_{j=1}^{\min(D-1,r-h)}\binom{r-h}{j}
 +\binom rD.                                                 \tag{4}
\]

For \(j\ge1\),

\[
 \sum_{h=0}^{r-1}2^h\binom{r-h}{j}
 =2^r\sum_{t=1}^{r}\frac{\binom tj}{2^t}<2^{r+1}.
\]

Consequently, \(E_D(r)\le(2D-1)2^r+\binom rD\), with a strict inequality for
\(D>1\). In particular,

\[
 E_1(r)=2^r+r,\qquad
 E_2(r)=3\cdot2^r-r-2+\binom r2.                              \tag{5}
\]

Only levels at which prefetch can start need lower-jet records. Selecting those levels
reduces (4); an absent level requires waiting for a retained level or using a larger ancestor
packet. The model-specific level selection must be charged if stored.

## 5. Prepare both branches in the current packet

At the next unknown bit \(x\), write the restricted polynomial as
\(F(x,z)=A(z)\oplus xB(z)\). The degrees are at most \(D\) and \(D-1\), respectively.
For each \(|R|\le D-1\), replace the array holding \(B_R\) by \(A_R\oplus B_R\),
while retaining \(A_R\). Degree-\(D\) coefficients of \(A\) are shared by both branches.

Before \(x\) arrives, the packet therefore holds the two possible next coefficient packets
with shared highest-degree arrays. Their joint array count is

\[
 2\kappa_{D-1}(t-1)+\binom{t-1}{D}=\kappa_D(t).               \tag{6}
\]

Once \(x\) is known, select \(A_R\) for zero or the prepared \(A_R\oplus B_R\) for
one. Retain the shared highest-degree arrays. Exactly \(\kappa_D(t-1)\) arrays remain
mathematically live. Preparation costs \(P\kappa_{D-1}(t-1)\) word XORs and their reads
and writes. A word-at-a-time implementation needs only constant-count word registers beyond
the packet. Guards cannot be assumed to execute concurrently at no compute or memory cost.

### 5.1 Select without a pointer table or a post-guard payload copy

Let \(n\) be the number of bits unknown at initial packet arrival. Number those variables
in reveal order. Allocate the initial \(\kappa_D(n)\) arrays in the three-extent order:
constant first, lower-degree subsets next in fixed binary-mask order, and degree-\(D\)
subsets last in the bank's minimum-variable order. This is the canonical slot order.
After a local prefix \(a\) has resolved, the coefficient of a remaining subset \(R\) is
stored in the initial slot labelled

\[
 \phi_a(R)=R\cup\operatorname{last}_{D-|R|}\{j:a_j=1\},       \tag{7}
\]

where \(\operatorname{last}_k\) takes the most recent at most \(k\) resolved one positions.

**Theorem 2.** Equation (7) names distinct live slots, supports the branch preparation above
without overwriting another required value, and leaves the exact selected record in
\(\phi_a(\varnothing)\) when the final bit resolves.

**Proof.** At the empty prefix, \(\phi(R)=R\). At a new bit \(x=0\), the selected array
remains in \(\phi_a(R)\). At \(x=1\) and \(|R|<D\), its prepared value lies in
\(\phi_a(R\cup\{x\})\). Since \(x\) is the newest resolved position, adding it and
the previous \(D-|R|-1\) latest ones gives (7). For \(|R|=D\), no \(B_R\) exists,
and the original highest-degree array remains shared. Different tail sets remain different
after prefix positions are added, proving injectivity. The branch preparation pairs disjoint
slots, so scalar overwrites are safe. At the final prefix the restricted polynomial is
constant and equals the source record. \(\square\)

An \(n\)-bit prefix and integer subset-ranking arithmetic recover these addresses. A
\(\kappa_D(n)\)-entry pointer table is unnecessary. Formula (7) does not make ranking
free: a simple combinatorial-rank calculation uses \(O(n)\) binomial terms per address,
with source-independent arithmetic and explicitly bounded integer registers. Each of the
three incoming extents fills its own contiguous part of the canonical allocation. No initial
payload permutation is required. A container layout that prevents these destination ranges
must charge its additional buffers and copies.

The initial allocation remains reserved throughout this schedule. Discarding a branch
logically does **not** release bytes in a contiguous allocation. Its peak payload is
\(\kappa_D(n)L\); shrinking physical residency requires separately charged compaction or
individually releasable extents. With an unchanged allocation, the final record can be
returned as a view at (7), without a last-bit payload copy. Releasing the rest of that
allocation is a later memory-management action.

## 6. A sufficient schedule and its exact boundary

Suppose the prefix packet is available at time \(F\). Let \(\tau_j\) be the time local
guard \(j\) resolves, and let \(c_j\) bound all preparation after guard \(j-1\): XORs,
address calculations, and required layout work. On a reserved preparation resource, define

\[
 f_1=F+c_1,\qquad
 f_j=\max(f_{j-1},\tau_{j-1})+c_j\quad(j>1).                 \tag{8}
\]

If \(f_j\le\tau_j\) for every \(j\), the correct branch coefficients are already
prepared at every guard arrival. After the final guard, only charged identifier/address
selection remains before the normal operation can read the original record. If guards and
preparation share compute or memory bandwidth, their joint service schedule must imply the
\(c_j\) and \(\tau_j\) used here; separate optimistic timings do not prove (8).

Equation (8) is sufficient for this particular preparation schedule. A missed intermediate
deadline does not prove every possible algorithm stalls at the final use. The full peak RAM
also includes the locator, masks, arithmetic registers, integrity and read buffers, guards,
and the normal operation's live state. Count the final record view once, inside its packet.

## 7. Comparators that the candidate must beat

| Method on the same prefix/source family | Source payload retained | Payload extents before layout optimizations | Additional stored arrays |
|---|---:|---:|---:|
| Prefetch every possible original record | \(2^t L\) | One contiguous source interval | Zero |
| Fetch a Boolean interpolation basis of original records | \(\kappa_D(t)L\) | Up to \(\kappa_D(t)\), often mergeable | Zero |
| Fetch one precompiled complete prefix packet | \(\kappa_D(t)L\) | One | One packet per retained prefix |
| Fetch global coefficients, then restrict | Up to \(\kappa_D(r)L\) before a streaming schedule | One if contiguous | \(\kappa_D(r)\) |
| Prefix-jet layout (3) | \(\kappa_D(t)L\) | At most three | (4) minus \(2^r\) |

The interpolation basis consists of tail vectors of Hamming weight at most \(D\); its
evaluation matrix is triangular under inclusion and invertible. It already attains the
information bound. Reading its original records separately adds request costs but avoids
the candidate's compiled coefficient storage. Reordering or duplicating this basis is an
established competitor, not an impermissible improvement of the baseline.

Thus the candidate has no RAM advantage over the strongest interpolation-packet comparator.
Its question is whether a particular shared external layout and in-place preparation improve
the joint request/storage/work frontier. Full prefix packets can use the same contraction.
Neither low-degree coding nor equation (6) alone establishes novel mathematics.

## 8. Scope and remaining tests

At \(D=r\), \(\kappa_D(t)=2^t\); the packet saving disappears. An arbitrary change to
one source word can introduce high-degree coefficients and invalidate a low-degree atlas.
Irregular reveal order, source-dependent relevance predicates, guards requiring the packet's
own unknown record, and a short compute window require new analysis rather than reuse of the
prefix guarantee. The complete source identity and the control contract must both pass.

The [companion finite check](prefix-jet-checks.md) validates source inversion, every prefix
packet, every selected record, and physical slot formula (7). It passed 28 synthetic sources,
3,048 prefix packets, 11,260 exact record decodes, and 196,070 prepared coefficient pairs;
all 21 tested source mutations outside the certified degree were rejected.

## 9. Primary-source collision review

Dumer's [Recursive decoding of Reed–Muller codes](https://intra.ece.ucr.edu/~dumer/urb99.pdf),
section 1, states the Boolean low-degree evaluation family, its binomial dimension, and the
recursive \((u,u+v)\) decomposition. These directly precede (1), the packet dimension,
and the algebra behind branch preparation. Independently deriving those identities does not
make them new. That paper's error-correcting decoder is a different task from supplying exact
model records, but the difference does not establish novelty for the algebra used here.

The three-extent atlas and latest-one physical slot formula need a narrower layout and
evaluation literature review. They remain unattributed candidate refinements, not established
new mathematics or a proven advantage over all improved existing methods.

Bouillaguet's [Boolean polynomial evaluation paper](https://eprint.iacr.org/2022/1412.pdf),
sections 6–8, supplies stronger comparators: implicit monomial ranking, nearly in-place
enumeration, and in-place variable restriction. These precede the broad claims of low-memory
interpretation and restriction without a pointer table. Preserving both prepared branches
until an unknown guard arrives requires an explicit comparison; reversing an XOR update is
not evidence of a new algebraic principle.

The current [Liu et al. preprint](https://eprint.iacr.org/2026/040), revised 2026-09-16,
is titled *Polynomial Evaluation on Many Inputs with Bounded Hamming Weight over GF(2)*.
Its FESG algorithm supplies a newer structured-evaluation comparator. Its input enumeration
task differs from externally timed guards, so its time and memory claims cannot be copied
into this schedule without deriving the conversion.
