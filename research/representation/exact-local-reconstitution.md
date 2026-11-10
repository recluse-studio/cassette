# Exact local reconstitution from a sparse defect atlas

**Status: constructive theorem; no originality claim.** This note gives one
exact representation for a structured weight table. A caller supplies a
coordinate rectangle. The representation locates and reconstructs that
rectangle without materializing the full table or scanning its stored
coefficients. Choosing a relevant rectangle from a semantic query is a
separate retrieval problem and is deliberately outside this interface.

## 1. Interface, exact value model, and weight family

Let the original table be

\[
 W\in(\mathbb Z/2^b\mathbb Z)^{p\times q},
 \qquad p=mt,\quad q=nt,
 \qquad T=mn.
 \tag{1}
\]

Each element is its exact \(b\)-bit fixed-point or two's-complement word.
All additions and multiplications below occur in \(\mathbb Z/2^b\mathbb Z\).
The recovered word is therefore bit-identical to the source weight; its
ordinary numerical interpretation happens only after recovery.

Tile \(\tau=(a,c)\in[m]\times[n]\) contains coordinates
\((i,j)=(at+u,ct+v)\), where \(0\le u,v<t\). Let

\[
 \beta_{r}(z)={z\choose r}
 \tag{2}
\]

be reduced modulo \(2^b\) after its integer value is formed. Define a global
Newton chart of coordinate degree at most \(d\),

\[
 G(i,j)=\sum_{r=0}^{d}\sum_{s=0}^{d}
     g_{rs}\beta_r(i)\beta_s(j),
 \tag{3}
\]

and a tile-local Newton chart of degree at most \(e<t\),

\[
 D_\tau(u,v)=\sum_{r=0}^{e}\sum_{s=0}^{e}
     \delta_{\tau,rs}\beta_r(u)\beta_s(v).
 \tag{4}
\]

The **sparse defect atlas family** \(\mathcal F_{d,e,s}\) comprises all
tables for which a set \(S\subseteq[m]\times[n]\), \(|S|\le s\), satisfies

\[
 W_{at+u,ct+v}=G(at+u,ct+v)+
 \begin{cases}
 D_{(a,c)}(u,v),&(a,c)\in S,\\
 0,&(a,c)\notin S.
 \end{cases}
 \tag{5}
\]

This is not a vague smoothness assumption. It admits a global exact chart,
plus up to \(s\) independently chosen local charts. The local coefficients
are recoverable from their tile values by finite differences, so distinct
coefficient vectors give distinct local tiles whenever \(t\ge e+1\).

The requested interface is a half-open rectangle

\[
 R=[i_0,i_1)\times[j_0,j_1)\subseteq[p]\times[q].
 \tag{6}
\]

It determines the intersected tiles by integer division. It does **not**
answer which \(R\) a user, model, or retrieval policy should ask for.

## 2. Representation and address calculation

Keep the \((d+1)^2\) words \(g_{rs}\), the dimensions, and one first-level
hash seed resident. Put the defect set \(S\) in a static two-level perfect
hash table. Its first-level directory and second-level slot headers are
external records. A second-level header stores the full tile identifier and
either an absent mark or a pointer to that tile's \((e+1)^2\) coefficients.

For a requested tile identifier \(x=an+c\), the interpreter does this:

1. Read the first-level directory record at the resident-seed address of
   \(x\).
2. Use the returned bucket seed and offset to read one second-level slot
   header. Compare its stored tile identifier with \(x\).
3. Read the local coefficient record only when the identifiers agree.
4. Evaluate (3), add the evaluated (4) when present, and emit exactly the
   requested cells of the tile.

The static table exists with \(O(s)\) external words and two probes by the
standard Fredman--Komlós--Szemerédi construction. The representation does
not need its bucket seeds in RAM: the first probe retrieves the relevant
seed. Keys are retained in second-level slots, so a nondefect tile cannot be
mistaken for a defect through a hash collision.

## 3. Exact local-reconstitution theorem

### Theorem 1 — sparse defect atlas

For every \(W\in\mathcal F_{d,e,s}\), the representation above returns the
exact source word \(W_{ij}\) for every \((i,j)\in R\). It performs no scan
over unrelated defect coefficients or unrelated tiles.

For a rectangle intersecting \(K\) tiles, of which \(z\) are defects, it
uses at most

\[
 2K+z\left\lceil{(e+1)^2b\over \ell}\right\rceil
 \tag{7}
\]

external \(\ell\)-bit block reads when slot headers fit in one block and
defect payloads use packed blocks. Its peak interpreter workspace is

\[
 \kappa_0b+\kappa b+
 O\bigl((d+e)b+d\log p+d\log q+\log T\bigr)
 \tag{8}
\]

bits beyond the caller's output. Retaining a complete requested tile adds
the unavoidable \(t^2b\)-bit output buffer; streaming rows does not.
For fixed \(d\) and \(e\), this is \(O(b+\log(pq))\) RAM, independent of the
full \(pq\)-word table size.

For full-tile reconstruction, arithmetic is

\[
 O\bigl(Kt^2(d+1)^2+zt^2(e+1)^2\bigr)
 \tag{9}
\]

\(b\)-bit modular multiply-adds, plus local Pascal-table updates. A partial
rectangle evaluates only its requested cells after the same bounded tile
setup. Initializing and sweeping the Newton vectors adds
\(O\bigl(K[d^2+e^2+t(d+e)]\bigr)\) exact word operations; it does not
inspect unrelated encoded coefficients.

**Proof.** The two perfect-hash probes either find the unique record whose
stored key equals \(x\), or establish that \(x\notin S\). Thus the decoder
uses exactly the branch selected in (5). Equations (3)--(5) then give the
source word by ring equality, with no rounding step.

Newton coefficients are evaluated exactly. The required binomial vectors
inside a tile are generated with Pascal additions, using \(O(e)\) words.
At a tile boundary, the global binomial vectors are initialized by exact
integer products and divisions before reduction modulo \(2^b\), then swept
with Pascal additions. This takes the workspace in (8), never a table-sized
array. Each requested tile makes two index probes; only a confirmed defect
adds its packed local payload, proving (7). Separating the global and local
double sums gives (9). \(\square\)

The theorem concerns an uncorrupted external representation. It is not a
locally decodable error-correcting code, and it provides no repair guarantee
after a damaged record.

## 4. Bit cost and a resident-memory lower bound

Write \(\kappa_0=(d+1)^2\) and \(\kappa=(e+1)^2\). The chart words cost
\(\kappa_0b+s\kappa b\) bits. A static perfect-hash directory, slot keys,
seeds, and payload offsets add

\[
 O\bigl(s\log T+s\log s\bigr)
 \tag{10}
\]

bits. Hence the full representation has size

\[
 \kappa_0b+s\kappa b+O\bigl(s\log T+s\log s\bigr).
 \tag{11}
\]

This order has two simple limits.

First, require a defect-free tile to be reconstructed with no external read.
When \(p,q\ge d+1\), finite differences recover every \(g_{rs}\) from
the table. There are therefore \(2^{\kappa_0b}\) possible global charts.
Any exact zero-read resident state needs at least \(\kappa_0b\) bits. The
resident part of this construction meets that lower bound up to geometry and
address metadata.

Second, fix the global chart to zero, choose exactly \(s\) defect tiles, and
choose a nonzero local coefficient vector for each. Finite-difference
injectivity gives

\[
 \left|\mathcal F_{0,e,s}\right|
 \ge {T\choose s}\bigl(2^{\kappa b}-1\bigr)^s.
 \tag{12}
\]

Every exact representation of this subclass needs at least

\[
 \log_2{T\choose s}+s\log_2(2^{\kappa b}-1)
 \tag{13}
\]

bits across resident and external state. Formula (11) has the required
coefficient term and an explicit local-address term. It does not claim a
succinct-dictionary optimum for every \(s,T\); it claims constant-probe
addressing with a small resident state.

## 5. Concrete separation and defeated baselines

Take \(p=q=4096\), \(t=16\), \(b=16\), \(d=e=1\), and \(s=128\). Then
\(T=65{,}536\), \(\kappa_0=\kappa=4\), and a raw table costs 32 MiB. A
direct layout that assigns an independent affine chart to every tile costs

\[
 T\kappa b=4{,}194{,}304\ \text{bits}=512\ \text{KiB}
 \tag{14}
\]

before its record headers. The atlas uses 64 resident chart bits, 8,192
defect-coefficient bits, and its explicit sparse-address records. It still
reconstitutes any requested 16-by-16 tile exactly. A global affine chart
alone cannot represent even one independently chosen defect tile; the atlas
can represent 128.

The construction loses on an arbitrary table. If \(s=T\) and \(e=t-1\),
then \(\kappa=t^2\): the local payload is already a full tile and the hash
directory is pure overhead. It also rejects a residual tile outside the
declared degree \(e\). A checkerboard residual with \(e=0\), for example,
is not silently fitted or approximated; it is outside \(\mathcal F_{d,e,s}\).

## 6. Collision check and remaining obstacle

The address mechanism is established. Fredman, Komlós, and Szemerédi prove
linear-space static sparse-table storage with constant worst-case access in
[Storing a Sparse Table with \(O(1)\) Worst Case Access Time](https://doi.org/10.1145/828.1884).
The local-decoding framing is also established in source-coding work such as
[Compressing Sparse Sequences under Local Decodability Constraints](https://arxiv.org/abs/1504.02063).

Those sources make the ingredients unsurprising: sparse dictionaries,
locally readable compressed data, polynomial charts, and tiled storage each
have long histories. The theorem here is a narrow composition with exact
ring arithmetic, tile-coordinate addressing, and an explicit resident/read/
precision account. It should be described as a candidate construction, not
as an established new coding theorem, until a focused search finds or rules
out a prior sparse-polynomial-atlas result with the same contract.

The main open obstacle is model breadth. Real learned weights need not lie in
\(\mathcal F_{d,e,s}\), and an exact encoder must either certify the family
membership or reject the table. A relevance stage must also map a normal
calculation to rectangle (6). Neither task is supplied by the local
reconstructor.
