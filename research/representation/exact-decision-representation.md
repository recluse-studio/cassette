# Exact region selection with a smaller arithmetic representation

This lane investigates how the mathematical information needed to select a source region can
be smaller than the numerical information stored in the weights that determine that selection.
The returned region contains original weights. The resident arithmetic object is used to find
the region; it is not used as replacement weights in the subsequent normal calculation.

**Status:** the finite-domain construction below is proved within its stated representation
class. A finite instance has a certified minimum coefficient width. The construction overlaps
established sign-preserving weight reduction; it is not a novelty claim or a result for
arbitrary model execution.

## 1. A source operation whose relevance is derived

The source contains rational row vectors \(a_1,\ldots,a_m\), an available integer runtime
vector \(v\in\mathcal V\subset\mathbb Z^d\), and arbitrary external weight regions
\(T_1,\ldots,T_m\). The ordinary operation selects

\[
\nu_A(v)=\min\operatorname*{arg\,max}_{i\in[m]}a_i^Tv
\]

and performs its declared normal calculation using \(T_{\nu_A(v)}\). The set \(\mathcal V\)
is the entire declared runtime-state domain, not an observed sample. An affine gate is included
by appending a coordinate equal to one. The source's tie rule is part of the operation.

This is a conditional operation in a model, not an assumption that a raw user prompt already
names a weight region. The preceding normal operations must produce \(v\) from the user query.
The construction does not accelerate those preceding operations or predict later states.

## 2. An arithmetic representation of the region choice

For \(b\ge1\), let

\[
\mathcal I_b=\{-2^{b-1},\ldots,2^{b-1}-1\}.
\]

Seek integer rows \(c_1,\ldots,c_m\in\mathcal I_b^d\), with \(c_m=0\), satisfying the following
constraints for every \(v\in\mathcal V\). Put \(i=\nu_A(v)\). Then

\[
(c_i-c_j)^Tv\ge
\begin{cases}
1,&j<i,\\
0,&j>i.
\end{cases}
\tag{R1}
\]

The runtime evaluates these new integer rows on \(v\) and applies the same least-index tie
rule. Their values need not equal the original gate scores.

**Theorem R1.** The constraints (R1) are necessary and sufficient for
\(\nu_C(v)=\nu_A(v)\) on every \(v\in\mathcal V\).

**Proof.** If \(j<i\), a tie would make the smaller index \(j\) win, so the selected row must
exceed it strictly. Both dot products are integers, making strict excess equivalent to a
difference of at least one. If \(j>i\), a tie retains \(i\), so a nonnegative difference
suffices. These conditions against every competitor are exactly the stated winner and tie
rule. The same argument proves necessity. \(\square\)

Subtracting \(a_m\) from every source row preserves all score differences. Multiplying all
remaining rational coefficients by a common positive denominator yields a feasible integer
system for some finite \(b\). Thus

\[
b_*=\min\{b:\text{there exists a system satisfying (R1)}\}
\tag{R2}
\]

is finite when the source and state domain are finite.

Exhaustive finite feasibility at increasing \(b\) constructs a minimizer and certifies that
no smaller uniform-width integer-row representation with the same dimensions and interpreter
works. The persistent coefficient payload is exactly \((m-1)db_*\) bits. This optimum is
restricted to the stated arithmetic representation, not to every possible program or encoding.
Construction may be expensive; the number of systems searched and domain constraints is part
of its offline work.

## 3. Exact source values and physical location

Place the source regions in canonical identifier order, with a declared equal record span
\(L\). The source identity, base extent, \(L\), scalar format, and source tie rule are charged
metadata. Once the arithmetic representation computes \(i\), the offset is

\[
\operatorname{offset}(i)=\operatorname{base}+(i-1)L.
\]

The record is read and its identity, shape, scalar encoding, and bytes are verified. Its
original payload \(T_i\) is supplied to the normal calculation. A source with unequal record
lengths requires a separately charged offset mechanism; the constant-stride equation does not
cover it.

This path has no sampled output. It computes the exact branch identifier and returns the
entire original region for that branch. The original routing rows and every \(T_i\) remain
in the source record. If later ordinary operations also require the original gate values,
their source weights and calculations must be included in the requested packet; preserving
the branch identifier alone does not reproduce those values.

## 4. RAM and work

Suppose \(|v_j|\le X\). An exact dot-product accumulator needs enough signed bits for
\(d2^{b_*-1}X\); the query and iterator, maximum value, selected identifier, and address
registers are charged separately. A scan of the \(m-1\) stored rows uses \(O(md)\) integer
operations with one live score accumulator. It does not need a table of answers for all
queries in \(\mathcal V\).

For one cold selection and return, the total peak includes the encoded coefficient rows,
metadata and source identity, input state, arithmetic registers, the fetched region, validation
workspace, and normal-calculation workspace. The route has no discovery read under this
contract and one region-record fetch. Record size and fetch time are not reduced merely
because the routing representation is smaller.

If routing scores themselves occupy only a small fraction of the model's existing working
memory, this construction's benefit is limited to that fraction. No end-to-end RAM or speed
improvement follows until the relevant operation and its actual resident closure are counted.

## 5. What would distinguish further mathematics

The construction proves that exact region selection has its own representation problem:
source gate values can vary without changing any selected region. It supplies a finite,
checkable baseline for that distinction. The next target is an algebraic characterization or
constructive solver that produces a smaller representation or a cheaper exact interpreter
than this coefficient search, together with a lower bound under the same state domain.

Stress cases must include ties, states absent from the declared domain, source changes that
move a decision boundary, large integer accumulators, and any normal operation that needs
the numerical gate scores as well as their ordering. Success on a few sample states is not
an exact-routing certificate.

## 6. A finite optimum and its domain boundary

For

\[
A=\begin{pmatrix}1000001&999999\\-1000003&999997\\0&0\end{pmatrix},
\qquad \mathcal V=\{-2,-1,0,1,2\}^2,
\]

all 16 possible one-bit systems in (R1) fail. A two-bit system succeeds:

\[
C=\begin{pmatrix}1&1\\-1&1\\0&0\end{pmatrix}.
\]

Exhaustive evaluation of the complete 25-state domain certifies \(b_*=2\). The four
nonzero-row coefficient positions require eight payload bits in this class; their source
integers require 21 signed bits apiece, or 84 bits in the corresponding fixed-width encoding.
Neither count includes the model's other weights, query, metadata, or accumulators.

The state \((1000000,-1000001)\), outside the certified domain, makes source row 1 win
while the representation chooses row 3. Domain coverage is necessary even for this small
example. The following exact Python check reproduces both results:

```python
from itertools import product

source = ((1000001, 999999), (-1000003, 999997), (0, 0))
queries = tuple(product(range(-2, 3), repeat=2))

def winner(rows, query):
    return max(range(len(rows)), key=lambda i:
               (sum(a * x for a, x in zip(rows[i], query)), -i))

expected = tuple(winner(source, query) for query in queries)
for width in (1, 2):
    values = range(-(1 << (width - 1)), 1 << (width - 1))
    found = None
    examined = 0
    for coefficients in product(values, repeat=4):
        examined += 1
        candidate = (coefficients[:2], coefficients[2:], (0, 0))
        if all(winner(candidate, query) == target
               for query, target in zip(queries, expected)):
            found = candidate
            break
    if width == 1:
        assert examined == 16 and found is None
    else:
        assert found == ((1, 1), (-1, 1), (0, 0)) and examined == 248
        outside = (1000000, -1000001)
        assert winner(source, outside) == 0 and winner(found, outside) == 2
print('PASS: minimum width 2; 25 states; out-of-domain counterexample')
```

## 7. Primary-source comparison

Etscheid, Kratsch, Mnich, and Röglin's
[Polynomial Kernels for Weighted Problems](https://arxiv.org/abs/1507.03439)
uses Frank–Tardos number compression. Its
[journal theorem 1](https://doi.org/10.1016/j.jcss.2016.06.004) gives integer coefficients
that preserve rational dot-product signs over bounded integer test vectors. Applying that
idea to score differences is an established comparator for exact routing. Thus retaining
decisions while discarding irrelevant coefficient precision is not itself new mathematics.
The exhaustive width certificate above solves one small instance; it does not show an
advantage over optimized established weight reduction on model-scale gates.
