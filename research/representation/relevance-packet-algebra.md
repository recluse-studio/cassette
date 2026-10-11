# Exact relevance packets for Boolean-subcube refinement

**Status: proved rank theorem and a restricted checkpoint construction.** The
construction reconstructs exact source records after a predicate has narrowed
the possible record identifier to a declared Boolean subcube. It does not
rank records, infer predicates, or decide that a supplied cell is relevant.

## 1. Source contract

Let \(\mathbb K=\mathbb F_{2^b}\). Fix a reversible map between one
\(b\)-bit source word and one element of \(\mathbb K\). The field elements
in this note are therefore an exact transport encoding of original source
words, not replacement model weights.

There are \(2^r\) external records, indexed by \(u\in\{0,1\}^r\). Each
record has \(P\) source words. Fix a monomial support
\(\mathcal F\subseteq2^{[r]}\), and let its coefficient arrays be
\(C_S:S\in\mathcal F\), with \(C_S\in\mathbb K^P\). The declared source
family is

\[
 T(u)=\sum_{S\in\mathcal F}C_S\prod_{j\in S}u_j\in\mathbb K^P.
 \tag{1}
\]

The exact record is recovered by applying the inverse word map coordinate by
coordinate to \(T(u)\). No numerical approximation enters (1).

A predicate supplies a cell

\[
 C=C(A,a)=\{u\in\{0,1\}^r:u_j=a_j\text{ for }j\in A\},
 \tag{2}
\]

where \(A\subseteq[r]\) and \(a\in\{0,1\}^A\). Future computation may
later reveal the remaining bits of \(u\), but no further external read is
permitted after the preload packet for \(C\) arrives.

## 2. The exact restriction rank

Write \(Z(a)=\{j\in A:a_j=0\}\) and let \(U=[r]\setminus A\) be the free
coordinates. A monomial indexed by \(S\) vanishes on \(C\) when
\(S\cap Z(a)\ne\varnothing\); otherwise its restriction is the monomial
indexed by \(S\cap U\). Define

\[
 \mathcal R_C=
 \{S\cap U:S\in\mathcal F,\ S\cap Z(a)=\varnothing\},
 \qquad d_C=|\mathcal R_C|.
 \tag{3}
\]

The distinct Boolean monomials indexed by \(\mathcal R_C\) are linearly
independent as functions on \(\{0,1\}^U\), over every field. Hence \(d_C\)
is the dimension of the evaluation space of the restrictions of the declared
monomials, rather than merely an upper bound.

For every \(R\in\mathcal R_C\), combine the source-specific arrays as

\[
 D_R(C)=
 \sum_{\substack{S\in\mathcal F:\ S\cap U=R\\ S\cap Z(a)=\varnothing}}
 C_S.
 \tag{4}
\]

Then, for every \(u\in C\),

\[
 T(u)=\sum_{R\in\mathcal R_C}D_R(C)\prod_{j\in R}u_j.
 \tag{5}
\]

Equation (5) is a **relevance packet**: it holds all information needed to
reconstitute any later exact record in the supplied cell.

### Theorem 1 — universal preload lower bound

For fixed \(\mathcal F\) and cell \(C\), every zero-error packet that
recovers every \(T(u)\), \(u\in C\), for arbitrary coefficient arrays
\(C_S\in\mathbb K^P\), needs at least

\[
 d_C P b\quad\text{bits}.
 \tag{6}
\]

The \(d_C\) arrays in (4) meet this bound exactly. The query-dependent basis
labels require \(O(d_C\log r)\) bits if \(\mathcal R_C\) is not fixed by the
cell type; the cell address itself requires \(|A|\) predicate bits.

**Proof.** The restriction map from the coefficient arrays to functions on
\(C\) has image \(\mathbb K^{d_C\times P}\), because the monomial functions
in (3) are independent and the source arrays are arbitrary. It therefore
has \(2^{bd_CP}\) distinct possible restrictions. A zero-error packet must
distinguish them: otherwise one packet would lead to the same reconstitution
for two different restrictions. This proves (6). Equation (5) supplies one
coefficient array for each basis function and is injective in the restriction,
so it matches the bound. \(\square\)

The theorem permits arbitrary linear combinations of source coefficients.
Restricting a packet to raw source records would be weaker and would not prove
the claimed optimum.

## 3. The defeated query-time candidate

Storing only the source coefficient arrays \(C_S\) does not create a useful
preload packet. To form (4) for a general cell, an interpreter must inspect
all \(|\mathcal F|\) arrays in the worst case, even when
\(d_C\ll|\mathcal F|\). It has moved the I/O from record reconstitution to
packet formation.

Likewise, pre-storing packets for every Boolean cell is not a remedy. The
singleton cells alone store one arbitrary \(P\)-word record apiece, requiring
\(2^rPb\) bits before headers. That is the original record table in another
order. A reusable scheme needs a restricted cell family and a local
restriction operation.

## 4. Checkpoint atlas for prefix refinement

The following construction supplies that restricted family. It is deliberately
limited to predicates that reveal record-ID bits in a fixed order. For a prefix
\(a\in\{0,1\}^L\), define

\[
 C_{a,L}=\{u:u_{1:L}=a\}.
 \tag{7}
\]

Take the nontrivial complete low-degree support

\[
 \mathcal F_k=\{S\subseteq[r]:|S|\le k\},
 \qquad N(r,k)=\sum_{j=0}^{k}{r\choose j}.
 \tag{8}
\]

Every prefix cell has the fixed restriction rank

\[
 d_{r-L,k}=N(r-L,k).
 \tag{9}
\]

For one chosen checkpoint level \(L<r\), precompute (4) for every
\(C_{a,L}\). Store each packet at the direct array address \(a\); its
monomial ordering is fixed, so it needs no per-packet basis labels or hash
lookup. Its source-specific payload is exactly
\(N(r-L,k)P\) field words. The checkpoint atlas costs

\[
 2^L N(r-L,k)Pb
 \tag{10}
\]

bits, in addition to the root coefficient atlas \(N(r,k)Pb\). It stores
\(2^L\), rather than \(2^r\), packets.

When another identifier bit \(x\) becomes known after preload, the
interpreter restricts the resident packet locally. If \(x\) has value
\(v\in\{0,1\}\), it replaces the remaining arrays by

\[
 D'_R=D_R+vD_{R\cup\{x\}}
 \quad(R\subseteq\text{remaining variables}),
 \tag{11}
\]

with absent arrays interpreted as zero. This uses no external coefficient
read. Repeating (11) until all bits are known leaves the single array
\(D'_\varnothing=T(u)\), the exact \(P\)-word source record.

### Theorem 2 — reusable checkpoint packet

For the degree-\(k\) family (8), a packet preloaded from a prefix checkpoint
\(C_{a,L}\) reconstitutes every later exact record in that cell with no later
external read. It has the information-theoretically minimum payload
\(N(r-L,k)Pb\) bits for that cell, takes one direct logical packet-record
lookup and \(1+\lceil N(r-L,k)Pb/\ell\rceil\) packed \(\ell\)-bit block
reads including its header, and uses

\[
 O\bigl(N(r-L,k)P b+N(r-L,k)\log r\bigr)
 \tag{12}
\]

RAM while the packet is live, beyond the returned \(Pb\) bits.

**Proof.** Equations (9) and Theorem 1 prove minimum packet size. Direct
addressing reads the packet without a directory scan. Formula (11) is the
identity \(x^0=1\), \(x^1=v\) applied to (5); induction over revealed bits
proves exact reconstitution and absence of later reads. The live coefficient
arrays and their fixed-order bookkeeping give (12). \(\square\)

The source-specific work is charged: building a level reads the root
coefficient arrays and writes every packet in (10). It is an offline encoding
cost, not a hidden query-time operation. A query sends the prefix address
\(a\), reads one packet, and performs at most
\(O(PN(r-L,k))\) field additions for each subsequent bit refinement.

## 5. Resource frontier and a concrete family

The raw record table costs \(2^rPb\) bits. The checkpoint-to-raw ratio is

\[
 {N(r,k)+2^L N(r-L,k)\over2^r}.
 \tag{13}
\]

For fixed \(k\) and \(L\le r-c\log_2 r\), this ratio vanishes as \(r\)
grows when \(c>k\). The construction is therefore strictly smaller than
the full table while supporting a packet for every prefix at level \(L\).
It is not generally smaller than the root coefficient atlas alone; the cache
pays for avoiding query-time scans.

For example, with \(r=32\), \(k=2\), \(L=12\), and \(P=256\), the root has
\(N(32,2)=529\) arrays. Every packet has \(N(20,2)=211\) arrays, and the
checkpoint atlas contains 4,096 packets. Its source-specific coefficient
payload is 864,256 field words, whereas the raw table has
\(2^{32}\cdot256\) words. The packet is minimal for each declared prefix,
but its 211 arrays are not tiny RAM; Theorem 1 says no universal zero-error
packet for that cell can be smaller.

The limit is sharp. If a predicate fixes a nonprefix set of bits, this atlas
does not necessarily contain its minimum packet. Using the nearest earlier
prefix packet remains exact, but it may be larger than \(d_CPb\). Caching all
such arbitrary cells returns to the exponential-cell failure above. Thus the
construction is a real locality result for ordered refinement, not a generic
solution to relevance-conditioned prefetch.

## 6. Collision check and remaining obstacle

The polynomial language is Reed--Muller-like: low-degree Boolean polynomial
evaluation is a classical coding construction. Locally decodable source coding
is also established; Makhdoumi, Huang, Médard, and Polyanskiy explicitly
study [On Locally Decodable Source Coding](https://arxiv.org/abs/1308.5239).
Their framing and the classical polynomial basis collide with the broad idea
of retrieving a small part of a coded source.

The narrow theorem here differs in its contract: it gives the exact
restriction-space rank for a **known predicate cell**, permits arbitrary
linear source-specific coefficient arrays in a preload packet, and shows why
an ordered checkpoint cache avoids the otherwise necessary coefficient scan.
Those differences are not evidence of novelty. No claim of a new code,
prefetch method, or representation theorem should be made without a focused
primary-source comparison to subcube restriction caches and coded prefetch.

The remaining obstacle is semantic and structural. A runtime must supply a
prefix predicate before this atlas helps. Learned records must also satisfy
the declared low-degree source family exactly. If either condition fails, the
construction has no safe fallback: it must refuse the packet rather than
approximate the original weights.
