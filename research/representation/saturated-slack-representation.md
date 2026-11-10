# Preserve pair decisions with less stored information

This note serves MATHS section 12. It replaces the three column vectors used by
[column propagation](column-sum-propagation.md) and
[pair interpretation](pair-total-support.md) with clipped distances to two boundaries.
The replacement preserves every single-row interval and every projected pair feasible
set. It therefore preserves every resulting source fetch and original-weight calculation.
It does not reduce the quotient table or prove a small representation for a full model.

## 1. Information the interpreter actually uses

Let the integer residual table have row totals \(t_i\), coordinate widths \(w_j\),
and total width \(W=\sum_jw_j\). Define

\[
 l_{ij}=\max(0,t_i-W+w_j),\quad v_{ij}=\min(w_j,t_i),\quad
 r_{ij}=v_{ij}-l_{ij}.
\]

The existing compiler records column totals \(u_j\) and envelopes
\(L_j=\sum_i l_{ij}, V_j=\sum_i v_{ij}\). Replace those values by

\[
 \alpha_j=u_j-L_j,\qquad \beta_j=V_j-u_j.                 \tag{1}
\]

Both are nonnegative because the original source satisfies its row bounds. The propagated
single-row interval is exactly

\[
 l_{ij}+\max(0,r_{ij}-\beta_j)\ \le e_{ij}\le\
 l_{ij}+\min(r_{ij},\alpha_j).                            \tag{2}
\]

The pair-sum interval for distinct rows \(i,k\) is exactly

\[
 l_{ij}+l_{kj}+\max(0,r_{ij}+r_{kj}-\beta_j)
 \le e_{ij}+e_{kj}\le
 l_{ij}+l_{kj}+\min(r_{ij}+r_{kj},\alpha_j).              \tag{3}
\]

These are algebraic identities obtained by substituting (1) into the original bounds.
No source row values enter the interpreter.

**Theorem 1 — clipping preserves interpretation.** Replace \(\alpha_j,\beta_j\)
by \(\min(\alpha_j,2w_j),\min(\beta_j,2w_j)\). Equations (2) and (3) remain
unchanged for every row or distinct row pair and every query.

Proof: \(0\le r_{ij}\le w_j\), hence \(r_{ij}+r_{kj}\le2w_j\). A value beyond
\(2w_j\) cannot change either minimum or maximum. The row bounds, row totals, and
pair-sum bounds completely specify the projected pair feasible set. Its exact support,
the weaker pair-total support, and every comparison made from them are therefore unchanged.
Original source addressing, reads, and normal arithmetic are unchanged as well.

The sharper cap is the sum of the two largest \(r_{ij}\) at that coordinate. Computing
it from resident row totals costs a scan over the rows for each coordinate; storing it
adds model-dependent bits. The fixed cap \(2w_j\) avoids both costs. No minimum claim
over all possible encodings follows from Theorem 1.

## 2. Omit columns that cannot help

At a coordinate with \(\alpha_j,\beta_j\ge2w_j\), equation (3) is just the pair's
existing box. That column needs no additional numerical value. Its missing-field meaning
is fixed by the decoder, not inferred from the query.

**Theorem 2 — a complete neutral guide makes this joint refinement redundant.** If all
columns satisfy that condition, the projected pair feasible set is the product of the
two separate row polytopes. Its maximum difference equals the independent upper bound
for row \(i\) minus the independent lower bound for row \(k\).

Proof: all pair-sum constraints are redundant. The remaining box and row-total constraints
act separately on the two rows, so each optimum can be attained independently. The
pair-total relaxation contains that product and can only be looser. Intersecting its
candidate set with the existing row-bound candidate set cannot remove another row.

The compiler can therefore emit one neutral-mode byte, and the interpreter can skip
the whole joint step. This is a useful failure test: ordinary, balanced column totals
often carry no useful pair information, regardless of how precisely they are stored.
The finite experiment below measures that condition on its declared generated sources.
It does not establish the condition in a trained model.

## 3. Explicit packed encoding and resource boundary

Widths, row totals, quotient coefficients, shape, source identity, and physical offsets
remain in the shared guide. This codec replaces only \(u,L,V\). Its first byte selects:

- `0`: every coordinate is neutral; no further bytes.
- `1`: visit each nonzero-width coordinate in order; two flag bits say which slack is
  below \(2w_j\), followed by each present slack in \(\lceil\log_2(2w_j)\rceil\) bits.
- `2`: store an active-coordinate count in \(\lceil\log_2(d+1)\rceil\) bits, then
  increasing coordinate IDs in \(\lceil\log_2d\rceil\) bits, two flags, and present values.

A missing value means \(2w_j\); a zero-width coordinate needs no flag. Modes 1 and 2
are compared by their complete byte lengths, and the smaller is chosen. This is an exact
minimum over those two layouts, not over arbitrary codes. The all-neutral layout takes
one byte. Codec mode, coordinate IDs, count, flags, and byte padding are all charged.

The former three-vector layout costs
\(\lceil3\sum_j\lceil\log_2(mw_j+1)\rceil/8\rceil\) bytes when packed together.
The new dense layout costs at most
\(1+\lceil\sum_{j:w_j>0}(2+2\lceil\log_2(2w_j)\rceil)/8\rceil\).
Its numerical field widths no longer grow with row count. Some small guides can still
favor the old encoding; a compiler must compare complete costs rather than assume a win.

The decoder can stream coordinates with a bit cursor, recomputing row boxes from two row
totals and \(W\). It need not materialize \(u,L,V\) or decoded slack vectors. Existing
query order, pair segments, source buffers, arithmetic widths, and other-layer guides still
count toward peak RAM. The verifier below deliberately materializes lists to check all
bounds; its process size is not a measurement of that streaming schedule.

## 4. Reproducible checks

The codec and integer-bound checks use stdlib Python. Run this fence from the repository
root. The small exhaustive family includes every normalized three-row, three-column
table with entries in \(\{0,1,2\}\). Larger families are generated independently of
queries. All measurements concern representation bytes and exact bounds, not latency.

```python
from itertools import product
from pathlib import Path
from random import Random
import json

pair_text = Path('research/representation/pair-total-support.md').read_text()
pair_code = pair_text.split('```python\n')[1].split('\n```')[0].split('\nE = ')[0]
scope = {}
exec(compile(pair_code, 'pair-total-support.md', 'exec'), scope)
summaries, pair_bound = scope['summaries'], scope['pair_bound']

def pack_fields(fields):
    result, position = bytearray(), 0
    for value, width in fields:
        assert 0 <= value < (1 << width)
        for bit in range(width):
            if position % 8 == 0:
                result.append(0)
            result[position // 8] |= ((value >> bit) & 1) << (position % 8)
            position += 1
    return bytes(result)

def encode_slack(widths, lower_slack, upper_slack):
    dimensions = len(widths)
    dense, sparse, active = [], [], 0
    for j, (width, lower, upper) in enumerate(zip(widths, lower_slack, upper_slack)):
        assert min(lower, upper, width) >= 0
        if width == 0:
            continue
        cap, bits = 2 * width, (2 * width - 1).bit_length()
        flags = int(lower < cap) | (int(upper < cap) << 1)
        fields = [(flags, 2)]
        if flags & 1:
            fields.append((lower, bits))
        if flags & 2:
            fields.append((upper, bits))
        dense.extend(fields)
        if flags:
            active += 1
            sparse.append((j, (dimensions - 1).bit_length()))
            sparse.extend(fields)
    if active == 0:
        return b'\x00'
    dense_code = b'\x01' + pack_fields(dense)
    sparse_code = b'\x02' + pack_fields([(active, dimensions.bit_length())] + sparse)
    return min((dense_code, sparse_code), key=lambda data: (len(data), data[0]))

def decode_slack(encoded, widths):
    position = 8
    def take(bits):
        nonlocal position
        value = 0
        for bit in range(bits):
            value |= ((encoded[position // 8] >> (position % 8)) & 1) << bit
            position += 1
        return value
    result = [(2 * w, 2 * w) for w in widths]
    if encoded[0] == 0:
        assert encoded == b'\x00'
        return result
    assert encoded[0] in (1, 2)
    if encoded[0] == 1:
        indices = (j for j, w in enumerate(widths) if w)
    else:
        count = take(len(widths).bit_length())
        indices = (None for _ in range(count))
    previous = -1
    for j in indices:
        if j is None:
            j = take((len(widths) - 1).bit_length())
            assert previous < j < len(widths) and widths[j] > 0
            previous = j
        cap, bits = 2 * widths[j], (2 * widths[j] - 1).bit_length()
        flags = take(2)
        lower = take(bits) if flags & 1 else cap
        upper = take(bits) if flags & 2 else cap
        assert 0 <= lower <= cap and 0 <= upper <= cap
        result[j] = (lower, upper)
    assert len(encoded) == (position + 7) // 8
    return result

def check_source(source, queries):
    widths = tuple(map(max, zip(*source)))
    totals, columns, all_lower, all_upper = summaries(source, widths)
    alpha = [u - lo for u, lo in zip(columns, all_lower)]
    beta = [hi - u for u, hi in zip(columns, all_upper)]
    encoded = encode_slack(widths, alpha, beta)
    decoded = decode_slack(encoded, widths)
    assert decoded == [(min(a, 2 * w), min(b, 2 * w)) for w, a, b in zip(widths, alpha, beta)]
    whole = sum(widths)
    bounds = [[(max(0, t - whole + w), min(w, t)) for w in widths] for t in totals]
    singles = pairs = 0
    for i, row in enumerate(bounds):
        for j, (lo, hi) in enumerate(row):
            a, b = decoded[j]
            original = (max(lo, columns[j] - all_upper[j] + hi),
                        min(hi, columns[j] - all_lower[j] + lo))
            compact = (lo + max(0, hi - lo - b), lo + min(hi - lo, a))
            assert original == compact
            singles += 1
        for k in range(i):
            for j, ((li, vi), (lk, vk)) in enumerate(zip(row, bounds[k])):
                a, b = decoded[j]
                original = (max(li + lk, columns[j] - all_upper[j] + vi + vk),
                            min(vi + vk, columns[j] - all_lower[j] + li + lk))
                radius = vi + vk - li - lk
                compact = (li + lk + max(0, radius - b), li + lk + min(radius, a))
                assert original == compact
                pairs += 1
    summary = totals, columns, all_lower, all_upper
    compact_summary = (totals, tuple(a for a, _ in decoded), (0,) * len(widths),
                       tuple(a + b for a, b in decoded))
    query_checks = 0
    for query in queries:
        order = sorted(range(len(widths)), key=lambda j: abs(query[j]))
        for i in range(1, len(source)):
            original = pair_bound(widths, summary, i, 0, query, order)
            compact = pair_bound(widths, compact_summary, i, 0, query, order)
            assert original == compact
            query_checks += 1
    old_bits = 3 * sum((len(source) * w).bit_length() for w in widths)
    return dict(old_column_bytes=(old_bits + 7) // 8, compact_column_bytes=len(encoded),
                codec_mode=encoded[0], single_coordinate_checks=singles,
                pair_coordinate_checks=pairs, pair_query_checks=query_checks,
                active_coordinates=sum(a < 2 * w or b < 2 * w
                                       for w, a, b in zip(widths, alpha, beta)))

patterns = [column for column in product(range(3), repeat=3) if min(column) == 0]
totals = dict(sources=0, single_coordinate_checks=0, pair_coordinate_checks=0,
              pair_query_checks=0)
for columns in product(patterns, repeat=3):
    result = check_source(tuple(zip(*columns)), ())
    totals['sources'] += 1
    for field in totals:
        if field != 'sources':
            totals[field] += result[field]

generator = Random(2026092201)
families = []
for rows, dimensions in ((48, 64), (48, 256), (128, 64)):
    for family in ('balanced', 'one_sparse_column', 'binary_sparse'):
        source = [[generator.randrange(256) for _ in range(dimensions)] for _ in range(rows)]
        if family == 'one_sparse_column':
            for i in range(rows):
                source[i][0] = int(i == 0)
        if family == 'binary_sparse':
            source = [[0] * dimensions for _ in range(rows)]
            for j in range(dimensions):
                source[generator.randrange(rows)][j] = 1
        minima = tuple(map(min, zip(*source)))
        source = [[v - minima[j] for j, v in enumerate(row)] for row in source]
        queries = [tuple(generator.randrange(-31, 32) for _ in range(dimensions)) for _ in range(16)]
        result = check_source(source, queries)
        families.append(dict(family=family, rows=rows, dimensions=dimensions, **result))
print(json.dumps(dict(seed=2026092201, exhaustive=totals, larger_sources=families), indent=2))
```

## 5. Observed result and comparison boundary

The [saved run](saturated-slack-results.json) preserves 61,731 single-coordinate
bounds and 61,731 pair-coordinate bounds across all 6,859 small sources. Nine larger
sources add 70,656 single-coordinate checks, 2,643,456 pair-coordinate checks, and
10,608 query-dependent pair-support comparisons, all equal before and after encoding.

| Generated source | Rows × coordinates | Former column fields | Replacement | Active coordinates |
|---|---:|---:|---:|---:|
| Balanced integers | 48 × 256 | 1,344 bytes | 1 byte | 0 |
| One sparse column | 48 × 256 | 1,341 bytes | 4 bytes | 1 |
| One binary nonzero per column | 48 × 256 | 576 bytes | 97 bytes | 256 |

These are column-field bytes, not the complete representation. The balanced case proves
that the extra joint calculation can be skipped; its one-byte result is not a one-byte
representation of the source or its region decisions. The row totals, widths, quotient
table, identity, offsets, and interpreter workspace remain. The new representation retains
the old interpretation exactly, including cases where that interpretation cannot rule out
any source row. Total-RAM and speed claims require the complete-path comparison.

## 6. Established mathematics and next comparison

The identities use ordinary bound propagation and elimination of redundant inequalities.
Bounds propagation is established; see the primary paper
[Finite Domain Bounds Consistency Revisited](https://arxiv.org/abs/cs/0412021).
The particular clipped representation was derived here. Its derivation and finite checks
do not establish publication novelty. The relevant comparison is now against methods
given the same clipped information, with all other guide fields and work included.

## 7. Independent proof and codec review

I found no defect in the two stated theorems within the declared projected-pair
program. Substituting \(\alpha_j=u_j-L_j\) and \(\beta_j=V_j-u_j\) gives
the single bound as
\[
\max(l_{ij},u_j-V_j+v_{ij})
=l_{ij}+\max(0,r_{ij}-\beta_j)
\]
and its upper counterpart as
\[
\min(v_{ij},u_j-L_j+l_{ij})
=l_{ij}+\min(r_{ij},\alpha_j).
\]
For a pair, the same substitution replaces \(r_{ij}\) by
\(r_{ij}+r_{kj}\). Since each radius is at most \(w_j\), both formulas are
unchanged after either slack is clipped at \(2w_j\). This proves the
interpretation claim without depending on query signs or tie behavior.

Theorem 2 follows because neutral slacks make every retained pair-sum
inequality redundant. The remaining constraints are the Cartesian product of
the two separate row polytopes, including their individual row totals; hence
the maximum score difference is the independent-row maximum minus minimum.
The conclusion depends on the note's declared projected-pair feasible set:
an additional source-dependent joint constraint would need its own retained
field and is not covered by neutral-mode omission. Within this program, the
pair-total relaxation contains the product and cannot improve an independent
upper certificate, so intersection cannot exclude an additional row.

I also checked the codec boundary that is easy to miss: zero-width
coordinates, a one-coordinate sparse identifier with zero identifier bits,
all-neutral mode, and every present/missing slack combination. Exhaustive
round trips over every width vector in \(\{0,1,2\}^d\) for
\(d=1,2,3\), and every slack value from zero through its cap, covered
44,135 encodings with zero decode failures. The bit width
\(\operatorname{bit\_length}(2w_j-1)\) represents precisely the present
range \(0,\ldots,2w_j-1\); the omitted value is the cap. Dense-versus-sparse
selection compares padded byte lengths and charges both mode and sparse
coordinate identifiers.

The compressed fields preserve the old joint interpreter; they do not by
themselves establish lower total RAM, lower latency, or new mathematics. The
adaptive original-read refinement is a stronger exact comparator for
candidate reads: its maintained bound \(H^+=\min(s_i-l_i)\) is sound after
each source read. Any future read comparison must include it rather than
treating the earlier fixed-candidate policy as definitive.
