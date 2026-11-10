# Exact relevance packets under refining predicates

A predicate can name many possible records before it names one. Raw prefetch keeps
every possible record. This note gives a different, exact option for a declared
algebraic source: load one packet that represents the entire predicate cell,
then contract that packet as ordinary control reveals more bits. The packet does
not know the future bit. It represents both branches until the bit arrives.

This is a finite mathematical schedule. It is neither a Cassette runtime design
nor a claim that ordinary floating-point weight pages have the required
algebraic form.

## 1. Exact source contract

Let \(u\in\{0,1\}^r\) be a record identifier in a declared, fixed bit order.
A source record contains \(P\) words over a finite field of characteristic two,
and has the algebraic normal form

\[
 W(u)=\bigoplus_{\substack{S\subseteq[r]\\|S|\le D}}
          C_S\prod_{i\in S}u_i,\qquad C_S\in\mathbb F^P. \tag{1}
\]

Each original record is \(W(u)\). This is a source promise, not a conclusion
from having a compact packet. General independent records need not satisfy it.

Suppose the first \(h\) bits form the known prefix \(p\), and \(t=r-h\) suffix
bits remain unknown. Restricting (1) gives a degree-\(\le D\) polynomial in
those suffix bits. Its exact coefficient count is

\[
 \kappa_D(t)=\sum_{j=0}^{\min(D,t)}\binom tj. \tag{2}
\]

The joint construction lays out those \(\kappa_D(t)\) coefficient arrays without
storing a private full packet for every prefix:

1. the constant \(W(p,0^t)\) is one original record;
2. coefficients of degrees \(1,\ldots,D-1\) are one precompiled node packet
   indexed by \((h,p)\);
3. degree-\(D\) tail-only coefficients are one suffix of a global degree-\(D\)
   bank, ordered by increasing minimum variable.

The three objects contain exactly \(\kappa_D(t)P\) field words; for \(D=1\),
there are at most two objects. Their values, identifiers, basis convention,
direct fixed-width bitstring encoding, and consuming-operation format are
all charged. The root-owned prefix-jet-packets.md records this construction;
the joint agent has independently checked it. This note assumes the stated
layout only to derive the schedule.

Once the next suffix bit \(x\) is about to become known, write the current
restricted polynomial as

\[
 F(x,z)=A(z)\mathbin{\oplus}xB(z). \tag{3}
\]

Before \(x\) arrives, compute each low-degree coefficient
\(A_S\oplus B_S\) into the storage occupied by \(B_S\), retaining \(A_S\).
When \(x=0\), retain \(A\); when \(x=1\), retain the overwritten \(B\) and
the shared degree-\(D\) arrays. Thus the selected restriction has exactly

\[
 \kappa_D(t-1)P \tag{4}
\]

field words. No output coefficient array is added. The direct algebraic
part of preparation uses

\[
 G_D(t)=\kappa_{D-1}(t-1)P \tag{5}
\]

word XORs. Equation (5) follows because \(B\) has
\(\kappa_{D-1}(t-1)\) coefficients. Address generation, packet-byte
traffic, pointer selection, branch selection, and any scratch are further
work; they are not represented by the XOR count. An implementation may claim
the zero-extra-payload transition only if its write order is proved safe for
its actual allocation and extents.

If this preparation runs before every remaining bit, the final selected
restriction is its constant \(W(u)\); no terminal polynomial evaluation is
needed. A schedule that stops contracting early must instead charge its direct
evaluation, at most \(\kappa_D(t)P\) word XORs for the retained \(t\)-bit
restriction. No relevance oracle, semantic-nearest-weight rule, or estimated
matrix product enters this construction.

## 2. Schedule and resource theorem

Let one cold \(P\)-word array require \(\ell\) seconds of read service. Let
\(L_{h,p}\) be the actual service time for the three declared extents of the
packet at \((h,p)\), including transfer of all \(\kappa_D(t)P\) words and
request overhead. It is not legitimate to count three extents as three
constant-time reads: the degree-\(D\) suffix itself can contain many arrays.

Let \(a_{\rm xor}\) be the available rate of field-word XORs. Let
\(\Pi_{h,p}\) be the certified wall time to prepare (3), including the
\(G_D(t)\) XORs, address generation, packet-byte memory traffic, pointer and
branch selection, allocator work, and any scratch initialization. In
particular,

\[
 \Pi_{h,p}\ge {G_D(t)\over a_{\rm xor}}, \tag{5a}
\]

but the right side is sufficient only when \(a_{\rm xor}\) has been measured
or certified as an effective whole-preparation rate for this exact layout.

Let \(B_{\rm normal}(s)\) contain every normal query, activation, output,
request, and ordinary arithmetic buffer at time \(s\), and let
\(B_{\rm meta}(h,p)\) contain packet addresses, predicate state,
pointer/compaction state, and direct bitstring-format state. The field words
are direct fixed-width bitstrings under XOR, so this schedule charges no
fictional field-conversion object. Let one field word occupy \(w\) bytes.

Consider an exact prefix \(p\) at \(s_h\); ordinary computation produces its
next unresolved bit \(x\) at \(s_{h+1}\). A no-stall schedule is:

1. issue the three packet extents only after \(p\) is exact;
2. load all \(\kappa_D(t)P\) arrays;
3. while ordinary arithmetic still runs, prepare (3);
4. when \(x\) is exact, logically retain the selected
   \(\kappa_D(t-1)P\) arrays and make only physically releasable storage
   available to later work.

With separate read and arithmetic resources, this schedule meets the next-bit
deadline exactly when

\[
 L_{h,p}+\Pi_{h,p}\le s_{h+1}-s_h. \tag{6}
\]

The initial load must finish before preparation can read its inputs, so the
terms add. The condition is necessary and sufficient for the listed schedule
under its exclusive-resource assumptions.

Logical liveness and physical allocation are different. Let
\(R_{h,p,x}\) be the number of packet bytes that the actual allocator has
released or compacted into reusable RAM by the time the later normal peak
occurs. It includes every charged copy, scratch region, pointer table, and
compaction operation required to obtain that release. The packet-related RAM
conditions are

\[
 \begin{aligned}
 B_{\rm normal}(s)+B_{\rm meta}(h,p)+\kappa_D(t)Pw
       &\le M &&\text{while loaded or prepared},\\
 B_{\rm normal}(s_{h+1})+B_{\rm meta}(h+1,p x)
       +\kappa_D(t)Pw-R_{h,p,x}
       &\le M &&\text{after selection}. \tag{7}
 \end{aligned}
\]

Equation (4) says only that \(\kappa_D(t-1)P\) arrays remain logically
necessary. To replace the second line of (7) by a
\(\kappa_D(t-1)Pw\) charge, the implementation must prove

\[
 R_{h,p,x}\ge
 [\kappa_D(t)-\kappa_D(t-1)]Pw. \tag{7a}
\]

Individually releasable page-sized arrays can satisfy (7a). A fixed contiguous
allocation normally cannot: selecting a branch leaves its original slot
reserved unless a separately charged compaction path runs. The construction
therefore does not by itself lower physical peak RAM.

If preparation shares arithmetic lanes with normal execution, a necessary
demand condition is that, in every interval \(I\) ending at a predicate
deadline, normal arithmetic demand plus released packet-preparation demand
does not exceed the available arithmetic service in \(I\). If packet reads
share the drive with normal page reads, \(L_{h,p}\) must likewise arise from
a feasible joint I/O schedule. These interval demand inequalities are not a
generic sufficient test: a specified scheduler, release times, priorities,
and a feasible schedule are required for sufficiency. The packet cannot hide
contention by calling ordinary arithmetic or other reads “overlap.”

For several refinements, apply (6) to the first fetched packet and then,
after each selected branch, schedule the next full \(\Pi\) preparation before
the next predicate. A new external packet is unnecessary while the current
packet remains resident. If RAM forces eviction, its later reload must satisfy
a new \(L_{h,p}\) deadline and loses the claimed no-stall path.

## 3. Concrete source, predicate, and time family

Set \(r=8\), \(D=2\), and use (1). At \(s_1\), ordinary control has
exactly determined the first two identifier bits. It therefore selects one of
four disjoint 64-record prefix cells, while the remaining six bits remain
unknown. At \(s_2\), the next bit becomes exact. At \(s_\star>s_2\), the
remaining five bits become exact together, and the record is required at
\(D_0\).

The selected prefix packet has

\[
 \kappa_2(6)=1+6+\binom62=22 \tag{8}
\]

\(P\)-word arrays: one original constant, six degree-one arrays, and fifteen
degree-two tail arrays. It reads those objects only after \(s_1\). It executes
the complete preparation with wall time \(\Pi_{2,p}\) before \(s_2\), so the
logical packet becomes

\[
 \kappa_2(5)=16 \tag{9}
\]

arrays after the next bit. The five remaining bits are unavailable until
\(s_\star\). At that time the packet directly evaluates the 16-array
restriction; let \(\Delta_{\rm dec}\) include every address, word traffic,
XOR, output-write, and consumption operation of this last exact decode.
The decoder can overwrite the restriction's constant coefficient with the
result, XORing in each selected nonconstant coefficient. That schedule adds
scalar scratch but no separate output array; another schedule must charge its
output allocation.

The declared no-stall conditions are

\[
 L_{2,p}+\Pi_{2,p}\le s_2-s_1,\qquad
 s_\star-s_2<\ell,\qquad
 \Delta_{\rm dec}\le D_0-s_\star<\ell. \tag{10}
\]

The packet's physical field-word allocation is at most \(22P\), plus the
normal and metadata charges in (7). Its *logical* live payload becomes
\(16P\) at \(s_2\); its physical allocation becomes \(16P\) only if (7a) is
proved for the declared page granularity or charged compaction route.

### Comparator boundary

No equal-RAM separation from an uncoded asynchronous prefetcher is claimed
here. A raw read may be issued before a predicate boundary and complete after
it; two adjacent intervals shorter than one record-read time do not prevent
that carry-in. A valid lower bound against that stronger class needs a
device-level account of outstanding requests, transfer buffers, queue depth,
release times, and completion order. This note has not supplied it.

The closest stronger comparators are explicit. A basis-record decoder may read
selected original evaluations and interpolate the record; it must charge its
basis reads, coefficients, arithmetic, retained arrays, and the same release
times. A full degree-\(\le2\) coefficient checkpoint contains
\(1+r+\binom r2=37\) \(P\)-word arrays in this family and can evaluate any
record, but its external layout, all-coefficient read latency, and resident
working state must also be charged. Either may win in a particular layout.

The valid claim from this family is narrower: if the source satisfies (1), the
listed packet has 22 logical arrays, its first refinement has 16, and equations
(6)--(7a) state exactly what must be proved before calling its read and
contraction path no-stall or RAM-reducing.

## 4. Storage and all-coefficient traps

The root-owned layout reports additional external storage at most

\[
 2(D-1)N+\binom rD \tag{13}
\]

\(P\)-word arrays beyond \(N=2^r\) originals. Equation (13) is the
proved payload accounting bound. Headers, alignment, and durable indexes add
their own bytes. It is not runtime RAM, and it does not make the extra packet
objects free.

Three failure modes are immediate.

- Materializing every later predicate packet recreates the source in another
  form. The stored \(C_1\) packet may save a read only because it is a declared
  external object with a limited node-sharing construction.
- A global coefficient checkpoint avoids per-node packets but requires reading
  every coefficient array needed for evaluation. If its arrays are not already
  resident, that all-coefficient scan belongs to the same deadline and I/O
  ledger.
- If the source does not satisfy (1), or if the packet extents serialize above
  the declared \(L_{h,p}\), the rank/count calculation yields no no-stall
  result.

The record returned by this construction is the declared direct fixed-width
bitstring record. A different consuming operation requires its own exact
format contract; it cannot be assumed from the packet algebra.

## 5. Prior-art boundary

The Boolean low-degree form in (1) is the established Reed--Muller family, not
a new representation. Its primary antecedents are
[Muller (1954)](https://doi.org/10.1109/irepgelc.1954.6499441), which treats
Boolean "plus polynomials" with exclusive-or terms, and
[Reed (1954)](https://doi.org/10.1109/TIT.1954.1057465), which gives the
corresponding multiple-error-correcting-code construction and decoder. Coded
caching also stores combinations before demand:
[Maddah-Ali and Niesen (2014)](https://doi.org/10.1109/TIT.2014.2306938).
Their theorem concerns a multiuser shared-link demand model, not this
single-query, predicate-revealed, contraction-and-deadline objective.

The result here is a conditional exact schedule and an explicit comparator
boundary. It does not establish originality of the ordered-prefix layout, its
in-place preparation, or the combined scheduling objective. A novelty audit must search coded storage and caching, locally
decodable/evaluable codes, online caching with prediction, and cache-aware
real-time scheduling for this exact combination.
