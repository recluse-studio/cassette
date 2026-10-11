# Zonotopal score certificates for exact region routing

**Status.** This is a proved source-family construction, with a matching
finite information bound in one binary subfamily. It identifies one required
external weight record from the source's actual argmax score table, then
returns that original record to ordinary arithmetic. Its geometric mechanism
is classical: linear optimization over a Boolean cube, equivalently the
support map of a zonotope. It is not a novelty claim and does not apply to an
arbitrary dense score table.

## 1. Source operation and certificate family

Let \(r,d\geq1\), \(m=2^r\), and let records be indexed by bit vectors
\(z\in\{0,1\}^r\). Their canonical physical ordinal is

\[
 \operatorname{id}(z)=\sum_{\ell=0}^{r-1}2^\ell z_\ell.                 \tag{1}
\]

Record \(z\) contains an arbitrary source-precision payload \(V_z\) of fixed
encoded span \(P\) bytes, including its fixed header. Its gate header contains
an integer row \(a_z\in\mathbb Z^d\). Given an integer runtime state
\(x\in\mathcal X\subseteq\mathbb Z^d\), the declared ordinary operation is

\[
 \nu_A(x)=\operatorname*{arg\,min}_{z\in
   \operatorname*{arg\,max}_{y\in\{0,1\}^r}a_y^Tx}\operatorname{id}(z),
 \qquad F(A,V,x)=\mathcal N(V_{\nu_A(x)},x).                              \tag{2}
\]

where \(\mathcal N\) is the stated normal calculation. It receives an
original payload, not a gate estimate or an estimated product. Equation \(2\)
is deliberately an argmax operation: if later code consumes all gate scores,
softmax values, or a different tie rule, this certificate alone is
insufficient.

The encoder admits a source only after it proves the **Boolean-generator
identity**

\[
 a_z=a_0+\sum_{\ell=0}^{r-1}z_\ell g_\ell
 \quad\text{for every }z\in\{0,1\}^r,                                  \tag{3}
\]

for integer generator rows \(g_\ell\in\mathbb Z^d\). It derives
\(g_\ell=a_{e_\ell}-a_0\) from the source headers, then verifies (3) for all
\(m\) headers using exact integer arithmetic. Thus the relation is a
certificate about the actual source score table. It is not a desired routing
label supplied by the query.

The resident abstraction is

\[
 Z_A=(g_0,\ldots,g_{r-1},\ r,d,\ P,\operatorname{base},
       \operatorname{format},\operatorname{tie},\operatorname{source\ id}). \tag{4}
\]

The common row \(a_0\) is intentionally absent: it adds the same
\(a_0^Tx\) to every comparison in equation \(2\). The record layout must be canonical
bit order with fixed stride. A source-dependent permutation of records needs
its own charged map and is outside this construction.

## 2. Interpreter, relevance, and exact reconstitution

For each generator, the interpreter calculates the exact signed difference

\[
 \delta_\ell=g_\ell^Tx,
 \qquad
 \widehat z_\ell=\mathbf1\{\delta_\ell>0\}.                              \tag{5}
\]

It resolves one location without a directory read:

\[
 \operatorname{offset}(\widehat z)
   =\operatorname{base}+P\operatorname{id}(\widehat z).                  \tag{6}
\]

It then reads that one encoded record, checks its canonical bit label, length,
format, and source-integrity binding, and passes the unaltered payload as
\(\widehat V_{\widehat z}\) to \(\mathcal N\). The check rejects a stale,
misaddressed, or differently encoded record; it does not turn a failed check
into a fallback result.

**Theorem 1 — exact zonotopal relevance.** Under (3), canonical layout, and
the least-ordinal tie rule in (2),

\[
 \widehat z=\nu_A(x),\qquad
 \widehat V_{\widehat z}=V_{\nu_A(x)},\qquad
 \mathcal N(\widehat V_{\widehat z},x)=F(A,V,x).                          \tag{7}
\]

**Proof.** Substitution of (3) gives

\[
 a_z^Tx=a_0^Tx+\sum_{\ell=0}^{r-1}z_\ell\delta_\ell.                    \tag{8}
\]

Each bit is independent. A maximizing label has \(z_\ell=1\) when
\(\delta_\ell>0\), \(z_\ell=0\) when \(\delta_\ell<0\), and either value
when \(\delta_\ell=0\). Among the latter labels, equation \(1\) is minimized by zero in
every tied bit. This is exactly equation \(5\), proving the first equality. Equation \(6\) therefore names the selected source record. The successful record checks
make its returned payload byte-for-byte \(V_{\nu_A(x)}\); substituting that
identity into \(2\) proves the remaining two equalities. \(\square\)

The checkable relevance relation is consequently

\[
 \mathcal R_A(x,S)\quad\Longleftrightarrow\quad
 S=\{\widehat z\}\text{ as calculated by (5)}.                           \tag{9}
\]

It is sufficient because changing payloads outside \(S\) cannot change (2).
It is not a claim that a generic dense product has a one-record relevant
region.

## 3. Information, reads, and peak RAM

Let \(b_g\) encode one signed generator entry, \(b_x\) encode one query entry,
and assume \(|g_{\ell j}|\leq G\), \(|x_j|\leq X\). One exact accumulator
for equation \(5\) requires at least

\[
 b_\delta=1+\left\lceil\log_2(dGX+1)\right\rceil                       \tag{10}
\]

signed bits, subject to the declared integer implementation's multiplication
scratch. Let \(b_{\rm meta}\) be the encoded length of every field in (4)
other than \(G=(g_{\ell j})\), including source identity and address format.
The resident source-dependent payload is

\[
 M_{\rm abstraction}=rd\,b_g+b_{\rm meta}\quad\hbox{bits}.               \tag{11}
\]

The routing phase can stream generators, retaining the query, one accumulator,
the \(r\)-bit label, address and loop state. A direct schedule allocates

\[
 M_{\rm route}=rd\,b_g+b_{\rm meta}+db_x+r+b_\delta+b_{\rm mult}+b_{\rm addr}
 \quad\hbox{bits}.                                                        \tag{12}
\]

Here \(b_{\rm mult}\) is the declared exact product-and-add scratch rather
than an uncharged machine word. After the one logical \(P\)-byte record read, its charged peak is

\[
 M_{\rm schedule}=
 \max\{M_{\rm route},\ rd\,b_g+b_{\rm meta}+db_x+r+8P+
       M_{\rm verify}+M_{\mathcal N}\}.                                  \tag{13}
\]

The second term charges the source record buffer, validation/decoding state,
and ordinary-calculation workspace. Whether \(\mathcal N\) streams or retains
a decoded copy changes \(M_{\mathcal N}\); the guide does not make that copy
free. Equation \(13\) is a charged schedule expression, conditional on the
declared values of its symbolic workspace terms. Additional live state raises
that peak; it is not absorbed by the representation bound.

At runtime the construction makes zero discovery reads and one logical
record read of \(P\) bytes, plus whatever store-level integrity objects the
storage contract requires. It performs \(rd\) integer multiply-adds, \(r\)
sign tests, and constant-time address arithmetic. Construction reads all
\(md\) gate-header entries, derives \(G\), verifies (3), and binds the
certificate to an immutable source identity. A stored source digest alone
cannot detect later arbitrary drive mutation; the surrounding store must
supply its separately charged manifest and integrity protocol.

The source payload itself remains arbitrary. For any fixed selected label,
two sources may have identical \(Z_A\) and differ in one byte of \(V_z\). An
interpreter that returns \(V_z\) exactly must therefore retain a lossless copy
of that byte or read an external object that determines it. In this
construction it reads the selected original record; the guide is never a
payload substitute.

## 4. A finite optimality result within a binary header family

The following lower bound isolates the information that routing, rather than
payload recovery, must retain. Set

\[
 \mathcal X=\{e_1,\ldots,e_d\},\qquad
 g_{\ell j}\in\{-1,+1\},\qquad a_0=0.                                  \tag{14}
\]

Every binary matrix \(G\in\{-1,+1\}^{r\times d}\) defines a valid source
header table through (3), while every payload family remains arbitrary. For a
basis query,

\[
 \nu_A(e_j)_\ell=\mathbf1\{g_{\ell j}=+1\}.                              \tag{15}
\]

**Theorem 2 — \(rd\)-bit no-discovery lower bound.** A deterministic,
source-independent interpreter that receives \(x\in\mathcal X\), reads no
external object before naming the selected record, and is exact for every
source in (14), needs at least \(rd\) source-dependent resident bits.

**Proof.** Equation (15) recovers every entry of \(G\) from the routing map:
\(g_{\ell j}=2\nu_A(e_j)_\ell-1\). The \(2^{rd}\) binary matrices therefore
induce \(2^{rd}\) distinct relevance maps. Two sources assigned the same
resident state would make the deterministic interpreter return the same map,
which is wrong for one source. It needs at least
\(\log_2(2^{rd})=rd\) bits. \(\square\)

Storing the signs of \(G\) attains this bound, apart from fixed metadata. A
literal resident score table stores \(2^r d\) values from \([-r,r]\), requiring
at least \(2^r d\lceil\log_2(2r+1)\rceil\) fixed-width bits in that baseline.
The generator certificate is exponentially smaller in \(r\) than that
literal table.

This is not a global minimum. On the finite query domain \(14\), a direct
lookup table of the \(d\) selected \(r\)-bit labels also uses exactly \(rd\)
bits and matches the lower bound. For a larger declared state set, compare
\(rd\,b_g+b_{\rm meta}\) against a charged lookup table of
\(|\mathcal X|r\) bits, a full score table, and any source reads they require.
The generator form is useful only in a regime where its exact arithmetic and
metadata beat those stronger alternatives.

## 5. Stress tests

The following finite check uses arbitrary payload bytes, constructs the full
source score table from the generators, enumerates exact source argmaxes, and
then verifies both routing and original-payload recovery. It also rejects a
one-entry header corruption that breaks (3).

~~~python
from itertools import product

G = ((2, -1), (-3, 4), (1, 1))
r, d = len(G), len(G[0])

def ordinal(z):
    return sum(bit << ell for ell, bit in enumerate(z))

labels = tuple(sorted(product((0, 1), repeat=r), key=ordinal))

def row(z):
    return tuple(sum(z[ell] * G[ell][j] for ell in range(r)) for j in range(d))

def dot(a, x):
    return sum(left * right for left, right in zip(a, x))

def routed_label(x):
    return tuple(int(dot(generator, x) > 0) for generator in G)

headers = tuple(row(z) for z in labels)
payloads = tuple(bytes((17 * ordinal(z) + k) % 256 for k in range(11))
                 for z in labels)
for x in product(range(-2, 3), repeat=d):
    full = min(labels, key=lambda z: (-dot(headers[ordinal(z)], x), ordinal(z)))
    routed = routed_label(x)
    assert routed == full
    # Fixed-stride addressing is the canonical ordinal in this in-memory fixture.
    assert payloads[ordinal(routed)] == payloads[ordinal(full)]
    # The normal calculation uses the recovered source bytes, not a score surrogate.
    assert sum(payloads[ordinal(routed)][j] * x[j % d] for j in range(11)) == \
           sum(payloads[ordinal(full)][j] * x[j % d] for j in range(11))

corrupt = list(headers)
corrupt[ordinal((1, 1, 1))] = (corrupt[ordinal((1, 1, 1))][0] + 1,
                               corrupt[ordinal((1, 1, 1))][1])
assert any(corrupt[ordinal(z)] != row(z) for z in labels)
print({"queries": 25, "records": len(labels), "payload_bytes_per_record": 11})
~~~

The construction fails, or loses its stated saving, in several discriminating
cases.

- If one source header violates (3), the compiler rejects it. Silently using
  its derived \(G\) can route to a wrong original record.
- If physical records have an arbitrary source-dependent permutation, the
  interpreter needs a label-to-offset map or discovery read. A map with one
  \(r\)-bit ordinal per record is already \(2^r r\) bits before integrity
  metadata.
- If the normal operation consumes the numerical gate scores after selection,
  the omitted common row and generator reconstruction do not reproduce those
  values. The original gate information must then be recovered under a new
  contract.
- If the score rows are unrestricted, changing one row can change its winning
  cone while preserving every proposed short generator certificate. The source
  family admits no such certificate, and the theorem gives no pruning or
  routing benefit.
- One logical record can occupy a whole physical page or more. The one-record
  read count neither proves low latency nor a small peak allocation.

## 6. Classical collision and remaining gap

Geometrically, the score points in (3) are the image of the Boolean cube, and
their convex hull is the translated zonotope

\[
 a_0+\sum_{\ell=0}^{r-1}[0,g_\ell].                                      \tag{16}
\]

The sign tests in (5) choose its support vertex in the query direction. The
query cells are the cones cut by the central hyperplanes
\(g_\ell^Tx=0\). This is established zonotope and hyperplane-arrangement
geometry, not a new decision representation. The normal-fan relation is
explicit in the primary research treatment
[Ardila, Castillo, Eur, and Postnikov (2020)](https://doi.org/10.1016/j.aim.2020.107039);
the broader arrangement and oriented-matroid setting is classical, including
[Folkman and Lawrence (1978)](https://doi.org/10.1016/0095-8956(78)90039-4)
and [Zaslavsky (1975)](https://doi.org/10.1090/memo/0154).

The strongest applicable established comparator is therefore the same
zonotope support-map factorization, plus direct lookup on a finite query
domain. The present derivation contributes a Cassette-complete accounting of
source certification, fixed-stride address resolution, original-record return,
and the \(rd\)-bit lower bound for the binary no-discovery class. It does not
establish mathematical novelty, superiority to that comparator, a benefit for
unstructured score matrices, or a frontier-model source family. Those are the
remaining gaps.
