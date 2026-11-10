# Normal-cell packets for exact future weight regions

**Status.** This note corrects a necessary rank premise, then gives a narrow
joint construction.  An exact source score comparison derives a non-prefix
cell of possible records from a query-prefix state.  A separately certified
low-degree source record field lets a packet of rank
\(\min(k+1,|C|)\) reconstruct the finally selected original record exactly.
The construction is a Reed--Solomon interpolation specialization coupled to
a normal-cell gate.  It is not a claim for arbitrary weight tables.

## 1. The full Boolean field has no restricted-rank saving

Let \(U=\{0,1\}^r\), and let

\[
 \mathcal V_{\rm full}=\operatorname{span}\{u^S:S\subseteq[r]\}
 \tag{1}
\]

over any field.  For every \(C\subseteq U\),

\[
 \dim(\mathcal V_{\rm full}|_C)=|C|.
 \tag{2}
\]

Indeed, the Boolean monomials span every function on \(U\): for
\(v\in U\), the indicator
\(\prod_{j:v_j=1}u_j\prod_{j:v_j=0}(1-u_j)\) expands in (1).  Their
restrictions include every indicator on \(C\).  Thus a field
\(T(u)=\sum_{S\subseteq[r]}C_Su^S\) with unrestricted coefficients has no
packet rank below the number of possible branch records.  A smaller
preread packet requires a certified proper coefficient subspace, not merely
a geometrically small cell.

## 2. A cell derived from actual source gate scores

Let records have integer identities \(i\in\{0,\ldots,N-1\}\).  Each record
contains a source-format payload \(V_i\), plus the actual dyadic gate score
vector

\[
 a_i=(i,-i^2).
 \tag{3}
\]

A source-construction scan reads every score header and verifies (3) exactly.
The runtime gate state is \(x(t)=(t,1)\), where a query prefix leaves the
exact future scalar in a closed dyadic interval \([L,U]\).  The actual gate
score is

\[
 \langle a_i,x(t)\rangle=ti-i^2.
 \tag{4}
\]

For a completed query, the tie-broken selected region is

\[
 i_*(t)=\min\operatorname*{argmax}_{0\le i<N}(ti-i^2)
       =\operatorname{clip}_{[0,N-1]}
          \left\lceil\frac{t-1}{2}\right\rceil.
 \tag{5}
\]

The last equality follows by completing the square.  It chooses the lower
index at the midpoint tie.

Before the suffix is known, the possible cell is derived from source scores:

\[
 C_{L,U}=\{i_*(t):L\le t\le U\}
        =\{i_*(L),i_*(L)+1,\ldots,i_*(U)\}.
 \tag{6}
\]

It is a contiguous normal-cell interval, not a literal query prefix or a
supplied branch label.  Two exact endpoint evaluations produce its complete
representation \((\ell,h)\), with \(\ell=i_*(L)\) and \(h=i_*(U)\).  No
source read is needed to discover this cell after the score relation has
been certified.

## 3. Certified record field and minimum packet rank

Fix a field \(F=\mathbb F_{2^b}\) with public basis and \(N\le|F|\).  Encode
each of the \(P\) original \(b\)-bit words of \(V_i\) as one element of
\(F\).  Let \(\xi_i\in F\) be the canonical distinct field encoding of
record identity \(i\).

The source belongs to the degree-\(k\) record-field class if, for every word
position \(q\in\{1,\ldots,P\}\), there is a polynomial \(f_q\in F[z]\) of
degree at most \(k\) such that

\[
 V_i[q]=f_q(\xi_i)\qquad(0\le i<N).
 \tag{7}
\]

This is a lossless structural promise about the original words.  A
construction scan reads all \(NP\) words, interpolates each \(f_q\) from the
first \(k+1\) records, and checks (7) at every remaining record.  The
external table may retain the original record layout; no approximate weights
or surrogate products enter the construction.

For a possible cell \(C=C_{L,U}\), define the admissible record-field space

\[
 \mathcal V_k|_C=
 \{(f(\xi_i))_{i\in C}:\deg f\le k\}.
 \tag{8}
\]

**Theorem 1 — exact cell packet dimension.**

\[
 d_C=\dim\mathcal V_k|_C=\min(k+1,|C|).
 \tag{9}
\]

**Proof.**  Evaluation at distinct field points gives a Vandermonde matrix.
Any \(m\le k+1\) rows are linearly independent, while the polynomial space
has dimension \(k+1\).  Taking \(m=|C|\) proves (9). \(\square\)

Choose the first \(d_C\) record identities in \(C\) as anchors.  Their
values form a rank-\(d_C\) packet *per word position*.  After the exact gate
returns \(i_*=i_*(t)\), compute Lagrange coefficients
\(\lambda_j(i_*)\) for those anchors and return, word by word,

\[
 \widehat V_{i_*}[q]=
 \sum_{j=0}^{d_C-1}\lambda_j(i_*)V_{\ell+j}[q].
 \tag{10}
\]

Equation (7) and interpolation prove

\[
 \widehat V_{i_*}=V_{i_*}
 \tag{11}
\]

bit-for-bit in the declared source word encoding.  The normal calculation
receives (11), not the packet's linear combination as an approximate
activation.

The rank is also necessary for a packet that must reconstitute every
candidate record in \(C\).  Fewer than \(d_C\) field evaluations leave a
nonzero degree-\(k\) polynomial vanishing at all read anchors and differing
at some unanchored candidate.  Applying that polynomial to one word
position yields two valid sources with identical smaller packets but
different required source words.

## 4. Exact read, RAM, and work account

Let one fixed-stride source record occupy \(R\) bytes, including its
identity, length, and digest header.  The anchor addresses are
\(\operatorname{base}+(\ell+j)R\); no directory is read.  A record header is
checked before its words enter (10).  The completed gate itself makes no
discovery read and resolves the final physical identity in \(O(1)\) exact
integer operations.

The rank statement does **not** by itself make prereading RAM-small.  Before
the query suffix resolves, the \(P\) word positions are independent degree
\(k\) polynomials.  An exact packet able to answer every final
\(i_*\in C\) must retain

\[
 d_CP\quad\text{field elements, or }d_CPb\text{ bits},
 \tag{12}
\]

up to record headers.  Otherwise two valid record fields agree on the
retained information and differ at a later possible target.  This is the
same Vandermonde lower bound applied independently to each word position.

There are therefore two honest schedules.

1. **Prefetch schedule.**  Read \(d_C\) complete anchors before suffix
   resolution: \(d_C\) requests and \(d_CR\) bytes.  Hold the anchors or an
   equivalent coefficient packet until the suffix arrives.  Its peak has at
   least \(8d_CR\) payload-buffer bits, plus resident routing state, the
   query-prefix state, and later normal-calculation workspace.  External
   temporary storage merely moves this amount into charged writes and later
   reads.

2. **Post-resolution reconstruction.**  After the gate selects \(i_*\),
   reread the \(d_C\) anchors and stream their word contributions into one
   \(P\)-word accumulator.  Peak packet RAM is

   \[
    8R+Pb+O\!\left(d_Cb+b\log N\right)\quad\text{bits},
    \tag{13}
   \]

   but it still reads \(d_CR\) bytes after the selection.  It does not beat
   one direct \(R\)-byte read when the original target record is available
   at that address.

Direct interpolation costs \(O(d_C^2)\) field operations to form the weights
and \(O(Pd_C)\) field multiply-adds to reconstruct the selected record.
Construction costs \(NP\) source-word reads, interpolation and verification
work, and the exact certificate or retained compiler receipt.  If the normal
calculation requires further workspace, it is added to (12) or (13) rather
than hidden in the packet claim.

Thus the normal-cell construction makes region determination compact, and
Theorem 1 states the exact packet dimension, but this low-degree field alone
does not supply the requested rapid, low-RAM exact reconstitution.  A real
improvement would require an additional verified cross-word constraint that
reduces the \(d_CP\)-element information content, or a physical layout in
which the direct target record is materially more expensive than the
anchors under the same byte and latency account.

## 5. Stress cases and collision boundary

* **Arbitrary source words.**  If (7) is absent, the full evaluation space
  on \(C\) has dimension \(|C|\), by the same argument as (2).  No smaller
  lossless packet can prepare every candidate record.

* **One corrupted payload word.**  Changing a single unchecked word can
  preserve all gate scores while invalidating (10).  Full source-word
  verification is therefore necessary; a score certificate alone proves
  only relevance, not reconstitution.

* **Tie boundary.**  At \(t=2i+1\), records \(i\) and \(i+1\) have equal
  actual gate scores.  Floating-point rounding can change the selected
  region and hence the exact required payload.  Formula (5) uses declared
  dyadic integer arithmetic and selects \(i\).

The packet is standard polynomial interpolation, closely related to
Reed--Solomon evaluation codes and to coded caching or coded storage.  The
mathematical correction over the unrestricted Boolean-field proposal is
specific: it identifies the exact condition under which a rank drop is
possible, proves the minimum rank, and proves that the rank is not by itself
a low-RAM preread packet.  It does not establish novelty.  Any novelty claim
would need a source family whose actual model score and record fields satisfy
both certificates, plus a comparison against the strongest applicable exact
coded-storage and support-function method.

## 6. Collision audit

Reed and Solomon's [polynomial-code construction](https://doi.org/10.1137/0108018)
is the direct antecedent for (7)--(11): field values of a bounded-degree
polynomial are reconstructed from enough distinct evaluations.  Maddah-Ali
and Niesen's [coded-caching result](https://doi.org/10.1109/TIT.2014.2306938)
also makes prefetch memory and later delivery separate resources.  Those
sources make it untenable to call interpolation or a coded preread packet
new.

The retained observation is instead a boundary that the standard code view
does not make automatic for this task: a score-derived normal cell can name
a non-prefix candidate set exactly, but a packet for an unresolved exact
record must retain its full per-word rank or pay the later rereads.  A
candidate that claims both rapid supply and low RAM must defeat this
persistence requirement through a further certified cross-word relation,
not by relabelling an interpolation packet.
