# Joint-summary scale experiment with exact source recovery

This bounded experiment compares exact region filters that return an original signed-16 gate
row, then an original payload record for the ordinary downstream calculation. It is a research
fence under [MATHS section 12](../../MATHS.md), adapted from the packed helpers and
source-reader conventions in [phase-quotient-experiment.md](phase-quotient-experiment.md) and
[remainder-sum-experiment.md](remainder-sum-experiment.md). It changes neither product code nor
an independent mathematics root.

The result is narrow. On the independent, structured, and near-tie generated families, the
pair-total and scalar-dual interpretations did not reduce a single fixed-candidate source fetch
beyond propagated boxes at the tested scales. They added interpretation work. A deliberately
coupled source exposes a small useful region: at 48 by 256, pair total reduces aggregate candidate
rows from 426 to 423 and gate bytes from 213,504 to 211,456; the scalar dual reduces them further
to 422 and 210,944. At 128 by 64 the corresponding counts are 450, 446, and 440 candidates, with
57,088, 56,576, and 55,808 gate bytes. These are logical source reads under one declared policy,
not a speed result.

## Source operation and common guide

For an available integer query \(x\), the source operation is

\[
 \nu_A(x)=\min\operatorname*{arg\,max}_{i<m} A_i x.
\]

Every route uses the selected original payload record in an ordinary integer matrix--vector
product. The gate and payload bytes remain in a temporary source file. A non-singleton filter
reads every retained original gate row, uses the least-index exact score rule, reads the winning
original payload, and checks the payload product against the full source reference. A singleton
reads no gate row before its payload. This is a **fixed candidate-set fetch policy**. It does not
include adaptive source-bound refinement after an early exact gate read, so it does not establish
superiority over a fully optimized exact-MIPS implementation.

The `Reader` receives a second full source byte string only to assert that each `pread` returned
the expected original byte range. The routing functions receive decoded guide fields and the file
reader; they do not receive the compiler's gate matrix or residual matrix.

For each positive \(\Delta=2^k\), a source compiler forms

\[
 A_{ij}=c_j+\Delta Q_{ij}+e_{ij},\qquad 0\le e_{ij}\le w_j,
\]

and encodes the source-derived fields

\[
 t_i=\sum_j e_{ij},\quad u_j=\sum_i e_{ij},\quad
 \ell_{ij}=\max(0,t_i-W+w_j),\quad
 v_{ij}=\min(w_j,t_i),\quad L_j=\sum_i\ell_{ij},\quad V_j=\sum_i v_{ij},
\]

where \(W=\sum_jw_j\). The propagated, pair-total, and scalar-dual routes consume exactly the
same packed \(Q,w,t,u,L,V\) guide. Thus a difference among their source reads is an interpretation
difference, never extra source metadata. The quotient baseline stores \(Q,w\); the row-sum
baseline stores \(Q,w,t\); exact centered and exact split are lossless comparators with their own
smaller required fields.

The direct joint codec packs \(u,L,V\) as one concatenated bit string; it does not separately
round each vector to a byte. This matters at small widths. The code also constructs and decodes a
smaller equivalent saturated-slack variant. This fence's variant is a dense clipped-field codec:
it writes the flags and active slack payloads as one packed stream. It is not the separate
mode-byte or sparse layout studied elsewhere, and its byte figures must not be treated as that
format's full-storage cost:

\[
 \alpha_j=\min(2w_j,u_j-L_j),\qquad
 \beta_j=\min(2w_j,V_j-u_j).
\]

For every \(w_j>0\), each slack receives a neutral flag. A nonneutral value uses
\(\lceil\log_2(2w_j)\rceil\) bits; a missing value denotes \(2w_j\). The JSON reports both the
direct-guide bytes used by the literal field codec and the saturated-slack guide bytes. The route
uses capped slacks and the compiler asserts a saturated-codec pack/decode round trip, so both
variants give the same propagated and pair constraints. The saturated figure is an alternative
encoded guide, not free metadata; this fence does not separately implement its streaming decoder.

The interpretations are as follows.

- `quotient` uses \(\sum_jw_j|x_j|\).
- `row_sums` uses the row total and \(0\le e_{ij}\le w_j\). It builds two query-sorted capacity
  and weighted-score prefixes once, then obtains each row's two support extrema with a binary
  search.
- `propagated` applies the column-total box bounds
  \(\ell_{ij}+\max(0,r_{ij}-\beta_j)\le e_{ij}\le
  \ell_{ij}+\min(r_{ij},\alpha_j)\), where \(r_{ij}=v_{ij}-\ell_{ij}\), and evaluates bounded
  support exactly.
- `pair_total` uses the pair-sum support relaxation from
  [pair-total-support.md](pair-total-support.md), intersected with propagated candidates.
- `pair_dual` uses the scalar-dual projected certificate from
  [pair-dual-refinement.md](pair-dual-refinement.md). It skips an ambiguous pair whenever every
  column has \(\alpha_j=\beta_j=2w_j\), because the cross-row cap is then neutral. This fence
  sorts every transformed \(|2x-z|\) trial explicitly and records `dual_trial_sorts`. Its
  observed work therefore differs from the proposed shared-order merge algorithm with
  \(O(d\log d+md\log X)\) work. It does not claim that merge cost or its implementation.

## Finite scope and accounting

The main grid contains independent signed-16 gates, structured residuals, near ties, and a
coupled residual family. It covers 48 by 64, 48 by 256, and 128 by 64 gates; each source has 49
integer queries, including zero. There are 19 configurations per main case: exact centered plus
exact split, quotient, row sums, propagation, pair total, and scalar dual at step sizes 4, 8, and
12. The grid therefore records \(4\cdot3\cdot19\cdot49=11{,}172\) exact routes. A fixed-phase
4-by-4 dual-tie witness adds seven configurations and 343 routes, for **11,515** exact routes in
[the saved result](joint-scale-results.json). Every route matched the original winner, original
payload bytes, and ordinary payload product.

The largest raw fixture, 48 by 256, contains a 6,291,456-byte payload table plus its gate rows;
it is below the declared 20 MiB fixture-source budget. The result records encoded guide fields,
query-coordinate and source-score accumulator widths, interpretation counters, logical source read bytes and requests, and
unique 4,096-byte source pages within each route. For simplicity, this Python fence decodes whole
packed guide fields into lists and materializes some interval state. That test state is unmeasured
extra memory. The source-score width does not bound scalar-dual trial values or other interpreter intermediates. The fence therefore makes no packed-interpreter RAM or peak-RAM claim. A packed
streaming schedule needs a separate proof. The 4,096-byte page figure is a coalescing model with
no retained route cache. It is not a count of physical-drive requests and does not establish
latency, bandwidth, or throughput.

The direct and saturated guides make the same decisions. At 8 bits, the neutral-column families
show the limit sharply: pair-total and dual retain exactly the propagated candidate totals while
pair-total performs extra segment work. For example, independent 48 by 256 retains 136 aggregate
candidate rows and reads 61,952 gate bytes under each of the three joint interpreters. Structured
48 by 256 retains 2,302 and reads 1,178,112 under each. Near-tie 128 by 64 retains 2,644 and
reads 338,304 under each. The dual route performs no multiplier trials in these cases because each
ambiguous comparison is neutral.

The coupled family isolates the contrary case at four-bit precision. Its direct and saturated
joint guides are 554 and 545 bytes at 48 by 256, and 437 and 427 bytes at 128 by 64. Under the
same saturated-guide budget, pair dual is the lowest logical-gate-read route in those two cases.
The 48-by-64 coupled case remains negative: propagation, pair total, and dual each read 40,320
gate bytes. The result therefore identifies a source- and query-dependent frontier rather than a
generic gain.

The fixed-phase dual-tie witness makes the stronger distinction explicit. Its target query is
\((-24,-10,-27,1)\); the original source scores are \((848,848,-153,-51)\). Propagation and pair
total retain rows \((0,1)\); the dual certificate retains only row \(0\), respecting the source
tie rule. Across the witness's 49 queries, that changes aggregate fixed-policy gate reads from 400
to 384 bytes and singleton routes from 24 to 25. Its 74-byte direct joint guide has a 71-byte
saturated alternative. Exact centered needs 69 bytes and exact split 70 bytes on this tiny source,
so the witness is an interpretation improvement, not a universal RAM win.

## Reproducible standard-library fence

Run the following from the repository root. It uses only generated sources and temporary local
files. The code shares the existing research fences' packed-header, phase, bit-packing, source
identity, original-record, and exact-refinement conventions; it does not import product modules.

```python
from collections import Counter
from hashlib import sha256
from math import ceil
from os import pread
from pathlib import Path
from random import Random
from struct import calcsize, pack, unpack
from tempfile import TemporaryDirectory
import json

SEED = 2026092201
HEADER = '<4sHHBQQ32s'
assert calcsize(HEADER) == 57
SIZES = ((48, 64), (48, 256), (128, 64))
FAMILIES = ('independent', 'structured', 'near_ties', 'coupled_witness')
STEP_BITS = (4, 8, 12)
QUERY_COUNT = 49


def pack_bits(values, widths):
    value = offset = 0
    for item, width in zip(values, widths):
        assert width >= 0 and 0 <= item < (1 << width)
        value |= item << offset
        offset += width
    return value.to_bytes((offset + 7) // 8, 'little')


def get_bits(blob, base, offset, width):
    if width == 0:
        return 0
    start, shift = divmod(offset, 8)
    count = (shift + width + 7) // 8
    return (int.from_bytes(blob[base + start:base + start + count], 'little') >> shift) & ((1 << width) - 1)


def bit_width(maximum):
    return maximum.bit_length()


def signed_bits(bound):
    return (bound + 1).bit_length() + 1


def phase_for_column(values, step):
    residues = sorted({value % step for value in values})
    gaps = [(step if len(residues) == 1 else (residue - residues[i - 1]) % step,
             -residue, residue)
            for i, residue in enumerate(residues)]
    return max(gaps)[2]


def compile_joint(matrix, step_bits, gate_base, payload_base, source_id, phase_optimal=True):
    rows, dimensions, step = len(matrix), len(matrix[0]), 1 << step_bits
    phases = [phase_for_column([row[j] for row in matrix], step) if phase_optimal else 0 for j in range(dimensions)]
    raw_q = [[(value - phases[j]) // step for j, value in enumerate(row)] for row in matrix]
    raw_e = [[(value - phases[j]) % step for j, value in enumerate(row)] for row in matrix]
    q_min = [min(row[j] for row in raw_q) for j in range(dimensions)]
    e_min = [min(row[j] for row in raw_e) for j in range(dimensions)]
    q = [[value - q_min[j] for j, value in enumerate(row)] for row in raw_q]
    e = [[value - e_min[j] for j, value in enumerate(row)] for row in raw_e]
    widths = [max(row[j] for row in q).bit_length() for j in range(dimensions)]
    w = [max(row[j] for row in e) for j in range(dimensions)]
    total_w = sum(w)
    t = [sum(row) for row in e]
    u = [sum(row[j] for row in e) for j in range(dimensions)]
    lower = [[max(0, total - total_w + wj) for wj in w] for total in t]
    upper = [[min(wj, total) for wj in w] for total in t]
    L = [sum(row[j] for row in lower) for j in range(dimensions)]
    V = [sum(row[j] for row in upper) for j in range(dimensions)]
    q_bits = rows * sum(widths)
    w_bits = dimensions * step_bits
    t_width = bit_width(total_w)
    t_bits = rows * t_width
    column_widths = [bit_width(rows * wj) for wj in w]
    u_bits = sum(column_widths)
    l_bits = sum(column_widths)
    v_bits = sum(column_widths)
    encoded = pack(HEADER, b'JSC1', rows, dimensions, step_bits, gate_base, payload_base, source_id)
    encoded += bytes(widths)
    encoded += pack_bits([value for row in q for value in row], widths * rows)
    encoded += pack_bits(w, [step_bits] * dimensions)
    encoded += pack_bits(t, [t_width] * rows)
    encoded += pack_bits(u + L + V, column_widths * 3)
    expected = 57 + dimensions + ceil(q_bits / 8) + ceil(w_bits / 8) + ceil(t_bits / 8) + ceil((u_bits + l_bits + v_bits) / 8)
    assert len(encoded) == expected
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            common = phases[j] + step * q_min[j] + e_min[j]
            assert value == common + step * q[i][j] + e[i][j]
            assert 0 <= e[i][j] <= w[j]
    alpha, beta = [u[j] - L[j] for j in range(dimensions)], [V[j] - u[j] for j in range(dimensions)]
    assert all(0 <= alpha[j] <= rows * w[j] and 0 <= beta[j] <= rows * w[j] for j in range(dimensions))
    capped_alpha = [min(value, 2 * wj) for value, wj in zip(alpha, w)]
    capped_beta = [min(value, 2 * wj) for value, wj in zip(beta, w)]
    flags, values, value_widths = [], [], []
    for j, wj in enumerate(w):
        if not wj:
            continue
        width = (2 * wj - 1).bit_length()
        for slack in (capped_alpha[j], capped_beta[j]):
            active = slack < 2 * wj
            flags.append(int(active))
            if active:
                values.append(slack)
                value_widths.append(width)
    slack_bits = len(flags) + sum(value_widths)
    slack_blob = pack_bits(flags + values, [1] * len(flags) + value_widths)
    assert len(slack_blob) == ceil(slack_bits / 8)
    offset, recovered_alpha, recovered_beta = len(flags), [], []
    flag_offset = 0
    for j, wj in enumerate(w):
        if not wj:
            recovered_alpha.append(0); recovered_beta.append(0)
            continue
        width = (2 * wj - 1).bit_length()
        pair = []
        for _ in range(2):
            active = get_bits(slack_blob, 0, flag_offset, 1)
            flag_offset += 1
            if active:
                pair.append(get_bits(slack_blob, 0, offset, width))
                offset += width
            else:
                pair.append(2 * wj)
        recovered_alpha.append(pair[0]); recovered_beta.append(pair[1])
    assert (recovered_alpha, recovered_beta) == (capped_alpha, capped_beta)
    qw_bytes = 57 + dimensions + ceil(q_bits / 8) + ceil(w_bits / 8)
    prefix_bytes = qw_bytes + ceil(t_bits / 8)
    qw_blob = encoded[:qw_bytes]
    qwt_blob = encoded[:prefix_bytes]
    saturated_blob = qwt_blob + slack_blob
    assert len(saturated_blob) == prefix_bytes + ceil(slack_bits / 8)
    return dict(blob=encoded, qw_blob=qw_blob, qwt_blob=qwt_blob, rows=rows, dimensions=dimensions, step=step, q=q, e=e,
                widths=widths, w=w, t=t, u=u, L=L, V=V, alpha=capped_alpha, beta=capped_beta,
                total_w=total_w,
                fields_bits=dict(header=57 * 8, widths=dimensions * 8, Q=q_bits,
                                 w=w_bits, t=t_bits, u=u_bits, L=l_bits, V=v_bits,
                                 saturated_slack=slack_bits),
                saturated_slack_bits=slack_bits,
                saturated_slack_guide_bytes=len(saturated_blob), qw_guide_bytes=len(qw_blob), qwt_guide_bytes=len(qwt_blob))


def compile_centered(matrix, gate_base, payload_base, source_id):
    rows, dimensions = len(matrix), len(matrix[0])
    minima = [min(row[j] for row in matrix) for j in range(dimensions)]
    q = [[value - minima[j] for j, value in enumerate(row)] for row in matrix]
    widths = [max(row[j] for row in q).bit_length() for j in range(dimensions)]
    blob = pack(HEADER, b'EXC1', rows, dimensions, 0, gate_base, payload_base, source_id)
    blob += bytes(widths) + pack_bits([value for row in q for value in row], widths * rows)
    assert len(blob) == 57 + dimensions + ceil(rows * sum(widths) / 8)
    return dict(blob=blob, q=q, widths=widths)


def compile_split(joint):
    rows, dimensions = joint['rows'], joint['dimensions']
    widths = [bit_width(value) for value in joint['w']]
    payload = pack_bits([value for row in joint['e'] for value in row], widths * rows)
    prefix = joint['blob'][:57 + dimensions + ceil(rows * sum(joint['widths']) / 8) + ceil(dimensions * (joint['step'].bit_length() - 1) / 8)]
    return dict(blob=prefix + payload, residual_bits=rows * sum(widths),
                fields_bits=dict(header=57 * 8, widths=dimensions * 8,
                                 Q=joint['fields_bits']['Q'], w=joint['fields_bits']['w'],
                                 residual=rows * sum(widths)))


def decode_qw(blob, source_id, expected_magic):
    magic, rows, dimensions, step_bits, gate_base, payload_base, identity = unpack(HEADER, blob[:57])
    assert magic == expected_magic and identity == source_id
    widths = list(blob[57:57 + dimensions])
    q_bits, q_base = rows * sum(widths), 57 + dimensions
    q = []
    for i in range(rows):
        offset = i * sum(widths)
        row = []
        for width in widths:
            row.append(get_bits(blob, q_base, offset, width))
            offset += width
        q.append(tuple(row))
    w_base = q_base + ceil(q_bits / 8)
    w = [get_bits(blob, w_base, j * step_bits, step_bits) for j in range(dimensions)]
    return dict(blob=blob, rows=rows, dimensions=dimensions, step=1 << step_bits,
                step_bits=step_bits, gate_base=gate_base, payload_base=payload_base,
                widths=tuple(widths), q=tuple(q), w=tuple(w), qw_end=w_base + ceil(dimensions * step_bits / 8))


def decode_qwt(blob, source_id, allow_trailing=False):
    runtime = decode_qw(blob, source_id, b'JSC1')
    rows, w = runtime['rows'], runtime['w']
    total_w, t_width = sum(w), bit_width(sum(w))
    t_base = runtime['qw_end']
    t = tuple(get_bits(blob, t_base, i * t_width, t_width) for i in range(rows))
    expected = t_base + ceil(rows * t_width / 8)
    assert len(blob) >= expected if allow_trailing else len(blob) == expected
    runtime.update(t=t, total_w=total_w)
    return runtime


def decode_joint(blob, source_id):
    runtime = decode_qwt(blob, source_id, allow_trailing=True)
    rows, dimensions, w = runtime['rows'], runtime['dimensions'], runtime['w']
    total_w, t_width = runtime['total_w'], bit_width(runtime['total_w'])
    t_base = runtime['qw_end']
    column_widths = [bit_width(rows * wj) for wj in w]
    column_base = t_base + ceil(rows * t_width / 8)
    offset = 0
    values = []
    for _ in range(3):
        row = []
        for width in column_widths:
            row.append(get_bits(blob, column_base, offset, width))
            offset += width
        values.append(tuple(row))
    u, L, V = values
    alpha = tuple(min(2 * wj, uj - lj) for wj, uj, lj in zip(w, u, L))
    beta = tuple(min(2 * wj, vj - uj) for wj, vj, uj in zip(w, V, u))
    assert all(0 <= a <= 2 * wj and 0 <= b <= 2 * wj for a, b, wj in zip(alpha, beta, w))
    runtime.update(u=u, L=L, V=V, alpha=alpha, beta=beta)
    return runtime


def decode_centered(blob, source_id):
    runtime = decode_qw(blob, source_id, b'EXC1')
    assert runtime['step_bits'] == 0 and all(value == 0 for value in runtime['w'])
    return runtime


def decode_split(blob, source_id):
    runtime = decode_qw(blob, source_id, b'JSC1')
    residual_widths = [bit_width(value) for value in runtime['w']]
    residual_base = runtime['qw_end']
    e = []
    for i in range(runtime['rows']):
        offset, row = i * sum(residual_widths), []
        for width in residual_widths:
            row.append(get_bits(blob, residual_base, offset, width))
            offset += width
        e.append(tuple(row))
    runtime.update(e=tuple(e))
    return runtime


class Reader:
    def __init__(self, stream, source_id, expected):
        self.stream, self.source_id, self.expected = stream, source_id, expected
        self.bytes, self.requests = Counter(), Counter()
        self.pages, self.page_bytes = set(), 0

    def start_route(self):
        self.pages.clear()

    def finish_route(self):
        self.page_bytes += 4096 * len(self.pages)

    def read(self, kind, offset, count):
        raw = pread(self.stream.fileno(), count, offset)
        assert len(raw) == count and raw == self.expected[offset:offset + count]
        self.bytes[kind] += count
        self.requests[kind] += 1
        self.pages.update(range(offset // 4096, (offset + count - 1) // 4096 + 1))
        return raw


def score_q(qrow, query, counters):
    counters['coarse_terms'] += len(query)
    return sum(a * x for a, x in zip(qrow, query))


def query_orders(query):
    return (tuple(sorted(range(len(query)), key=lambda j: (query[j], j))),
            tuple(sorted(range(len(query)), key=lambda j: (-query[j], j))))


def support_bounds(lower, upper, total, query, counters, orders=None):
    left = total - sum(lower)
    capacity = [hi - lo for lo, hi in zip(lower, upper)]
    shift = sum(a * x for a, x in zip(lower, query))
    assert 0 <= left <= sum(capacity)
    if orders is None:
        orders = query_orders(query)
        counters['support_sorts'] += 2
    def one(order):
        remaining, value = left, shift
        for j in order:
            if remaining == 0:
                break
            take = min(remaining, capacity[j])
            value += take * query[j]
            remaining -= take
            counters['support_coordinate_visits'] += 1
        assert remaining == 0
        return value
    return one(orders[0]), one(orders[1])


def row_sum_intervals(joint, query, counters):
    from bisect import bisect_left
    orders = query_orders(query)
    counters['row_sum_prefix_sorts'] += 2
    prefixes = []
    for order in orders:
        units, weighted = [0], [0]
        for j in order:
            units.append(units[-1] + joint['w'][j])
            weighted.append(weighted[-1] + joint['w'][j] * query[j])
        prefixes.append((order, units, weighted))
    def at(total, prefix):
        if total == 0:
            counters['row_sum_prefix_lookups'] += 1
            return 0
        order, units, weighted = prefix
        at_index = bisect_left(units, total)
        before = at_index - 1
        counters['row_sum_prefix_lookups'] += 1
        return weighted[before] + (total - units[before]) * query[order[before]]
    return [(at(total, prefixes[0]), at(total, prefixes[1])) for total in joint['t']]


def independent_intervals(joint, query, counters):
    return row_sum_intervals(joint, query, counters)


def propagated_intervals(joint, query, counters):
    orders = query_orders(query)
    counters['propagated_query_sorts'] += 2
    intervals = []
    for total in joint['t']:
        lo, hi = [], []
        for wj, alpha, beta in zip(joint['w'], joint['alpha'], joint['beta']):
            l = max(0, total - joint['total_w'] + wj)
            v = min(wj, total)
            r = v - l
            lo.append(l + max(0, r - beta))
            hi.append(l + min(r, alpha))
        intervals.append(support_bounds(tuple(lo), tuple(hi), total, query, counters, orders))
    return intervals


def candidate_from_intervals(joint, intervals, query, counters):
    coarse = [joint['step'] * score_q(row, query, counters) for row in joint['q']]
    lower = [base + interval[0] for base, interval in zip(coarse, intervals)]
    upper = [base + interval[1] for base, interval in zip(coarse, intervals)]
    anchor = min(range(joint['rows']), key=lambda i: (-lower[i], i))
    return anchor, tuple(i for i in range(joint['rows'])
                         if i == anchor or upper[i] > lower[anchor] or
                         (upper[i] == lower[anchor] and i < anchor))


def pair_bound(joint, challenger, anchor, query, counters, order):
    lo, hi, favored, other = [], [], [], []
    for wj, alpha, beta in zip(joint['w'], joint['alpha'], joint['beta']):
        ti, tk = joint['t'][challenger], joint['t'][anchor]
        li, vi = max(0, ti - joint['total_w'] + wj), min(wj, ti)
        lk, vk = max(0, tk - joint['total_w'] + wj), min(wj, tk)
        ri, rk = vi - li, vk - lk
        lo.append(li + lk + max(0, ri + rk - beta))
        hi.append(li + lk + min(ri + rk, alpha))
        if query[len(lo) - 1] >= 0:
            favored.append(vi); other.append(lk)
        else:
            favored.append(vk); other.append(li)
    def value(j, s):
        return abs(query[j]) * min(2 * favored[j] - s, s - 2 * other[j])
    current = list(lo)
    result = sum(value(j, current[j]) for j in range(joint['dimensions']))
    remaining = joint['t'][challenger] + joint['t'][anchor] - sum(current)
    for rising, traversal in ((True, reversed(order)), (False, iter(order))):
        for j in traversal:
            turn = min(hi[j], favored[j] + other[j])
            up = max(0, turn - lo[j])
            capacity = up if rising else hi[j] - lo[j] - up
            take = min(remaining, capacity)
            result += take * abs(query[j]) * (1 if rising else -1)
            remaining -= take
            counters['pair_segment_visits'] += 1
            if remaining == 0:
                break
        if remaining == 0:
            break
    assert remaining == 0
    return result


def candidates_quotient(joint, query, counters):
    scores = [score_q(row, query, counters) for row in joint['q']]
    anchor = min(range(joint['rows']), key=lambda i: (-scores[i], i))
    bound = sum(w * abs(x) for w, x in zip(joint['w'], query))
    return anchor, tuple(i for i in range(joint['rows'])
                         if i == anchor or joint['step'] * (scores[anchor] - scores[i]) < bound or
                         (joint['step'] * (scores[anchor] - scores[i]) == bound and i < anchor))


def candidates_pair(joint, query, counters):
    order = tuple(sorted(range(joint['dimensions']), key=lambda j: (abs(query[j]), j)))
    counters['pair_query_sorts'] += 1
    anchor, cheap = candidate_from_intervals(joint, propagated_intervals(joint, query, counters), query, counters)
    anchor_q = score_q(joint['q'][anchor], query, counters)
    kept = [anchor]
    for i in cheap:
        if i == anchor:
            continue
        upper = joint['step'] * (score_q(joint['q'][i], query, counters) - anchor_q)
        upper += pair_bound(joint, i, anchor, query, counters, order)
        if upper > 0 or (upper == 0 and i < anchor):
            kept.append(i)
    return anchor, tuple(sorted(kept))


def pair_dual_bound(joint, challenger, anchor, query, counters):
    if all(alpha == 2 * wj and beta == 2 * wj
           for alpha, beta, wj in zip(joint['alpha'], joint['beta'], joint['w'])):
        counters['dual_neutral_pairs_skipped'] += 1
        return None
    delta = joint['t'][challenger] - joint['t'][anchor]
    def objective(z):
        transformed = tuple(2 * value - z for value in query)
        order = tuple(sorted(range(joint['dimensions']), key=lambda j: (abs(transformed[j]), j)))
        counters['dual_trial_sorts'] += 1
        counters['dual_trials'] += 1
        return z * delta + pair_bound(joint, challenger, anchor, transformed, counters, order)
    lo, hi = 2 * min(query), 2 * max(query)
    while lo < hi:
        middle = (lo + hi) // 2
        if objective(middle + 1) >= objective(middle):
            hi = middle
        else:
            lo = middle + 1
    value = objective(lo)
    assert value % 2 == 0
    return value // 2


def candidates_pair_dual(joint, query, counters):
    anchor, cheap = candidate_from_intervals(joint, propagated_intervals(joint, query, counters), query, counters)
    anchor_q = score_q(joint['q'][anchor], query, counters)
    kept = [anchor]
    for i in cheap:
        if i == anchor:
            continue
        residual_upper = pair_dual_bound(joint, i, anchor, query, counters)
        if residual_upper is None:
            kept.append(i)
            continue
        upper = joint['step'] * (score_q(joint['q'][i], query, counters) - anchor_q) + residual_upper
        if upper > 0 or (upper == 0 and i < anchor):
            kept.append(i)
    return anchor, tuple(sorted(kept))


def refine(candidate, rows, dimensions, gate_base, payload_base, query, source, counters):
    candidate = tuple(candidate)
    counters['candidate_rows'] += len(candidate)
    counters['max_candidates'] = max(counters['max_candidates'], len(candidate))
    counters['singleton_routes'] += len(candidate) == 1
    if len(candidate) == 1:
        winner = candidate[0]
    else:
        best, winner = None, candidate[0]
        for i in candidate:
            raw = source.read('gate', gate_base + i * dimensions * 2, dimensions * 2)
            score = sum(a * x for a, x in zip(unpack('<' + 'h' * dimensions, raw), query))
            counters['exact_gate_terms'] += dimensions
            if best is None or score > best or (score == best and i < winner):
                best, winner = score, i
    payload_size = 2 * dimensions * dimensions
    payload = source.read('payload', payload_base + winner * payload_size, payload_size)
    return winner, payload


def exact_centered(centered, query, source, gate_base, payload_base, counters):
    scores = [score_q(row, query, counters) for row in centered['q']]
    winner = min(range(len(scores)), key=lambda i: (-scores[i], i))
    counters['candidate_rows'] += 1; counters['singleton_routes'] += 1; counters['max_candidates'] = max(counters['max_candidates'], 1)
    d = len(query)
    return winner, source.read('payload', payload_base + winner * 2 * d * d, 2 * d * d)


def exact_split(joint, query, source, gate_base, payload_base, counters):
    scores = []
    for qrow, erow in zip(joint['q'], joint['e']):
        counters['coarse_terms'] += 2 * len(query)
        scores.append(sum((joint['step'] * q + e) * x for q, e, x in zip(qrow, erow, query)))
    winner = min(range(len(scores)), key=lambda i: (-scores[i], i))
    counters['candidate_rows'] += 1; counters['singleton_routes'] += 1; counters['max_candidates'] = max(counters['max_candidates'], 1)
    d = len(query)
    return winner, source.read('payload', payload_base + winner * 2 * d * d, 2 * d * d)


def make_source(family, rows, dimensions, rng):
    if family == 'dual_tie_witness':
        assert (rows, dimensions) == (4, 4)
        gates = ((3, 0, 3, 1001), (0, 1, 0, 858), (3, 0, 3, 0), (1, 0, 1, 0))
        payloads = [tuple(rng.randrange(-127, 128) for _ in range(dimensions * dimensions)) for _ in range(rows)]
        gate_bytes = b''.join(pack('<' + 'h' * dimensions, *row) for row in gates)
        payload_bytes = b''.join(pack('<' + 'h' * (dimensions * dimensions), *row) for row in payloads)
        data = gate_bytes + payload_bytes
        queries = [(0,) * dimensions, (-24, -10, -27, 1)]
        for _ in range(QUERY_COUNT - len(queries)):
            query = tuple(rng.randrange(-31, 32) for _ in range(dimensions))
            queries.append(query if any(query) else (1,) + query[1:])
        return gates, payloads, data, tuple(queries), len(gate_bytes)
    step = 256
    base = [rng.randrange(-4000, 4001) for _ in range(dimensions)]
    gates = []
    if family == 'independent':
        for i in range(rows):
            gates.append(tuple(rng.randrange(-12000, 12001) for _ in range(dimensions)))
    elif family == 'structured':
        templates = [rng.randrange(-16, 17) for _ in range(dimensions)]
        for i in range(rows):
            group = i % 4
            row = []
            for j in range(dimensions):
                quotient = templates[j] + (group if j % 3 else -group) + rng.randrange(-2, 3)
                residual = (37 * (i % 8) + 19 * (j % 7) + (i // 8) * (j % 5)) % step
                row.append(base[j] + step * quotient + residual)
            gates.append(tuple(row))
    elif family == 'near_ties':
        direction = [rng.choice((-1, 1)) for _ in range(dimensions)]
        for i in range(rows):
            row = []
            for j in range(dimensions):
                quotient = (i % 3) - 1 if j % 5 else 0
                residual = (129 + direction[j] * ((i * 3 + j) % 7)) % step
                row.append(base[j] + step * quotient + residual)
            gates.append(tuple(row))
    else:
        witness = ((5, 0, 10), (0, 10, 0), (10, 0, 10), (0, 0, 10))
        for i in range(rows):
            row = [0] * dimensions
            if i < 4:
                row[:3] = witness[i]
                if i == 0:
                    row[1] += 16
            else:
                row[0] = -16000 - i
            gates.append(tuple(row))
    assert all(-32768 <= value <= 32767 for row in gates for value in row)
    payloads = []
    for i in range(rows):
        payloads.append(tuple(rng.randrange(-127, 128) for _ in range(dimensions * dimensions)))
    gate_bytes = b''.join(pack('<' + 'h' * dimensions, *row) for row in gates)
    payload_bytes = b''.join(pack('<' + 'h' * (dimensions * dimensions), *row) for row in payloads)
    data = gate_bytes + payload_bytes
    assert len(data) < 20 * 1024 * 1024
    queries = [(0,) * dimensions]
    if family == 'coupled_witness':
        queries.append((-1, 1) + (0,) * (dimensions - 2))
    for q in range(QUERY_COUNT - len(queries)):
        query = tuple(rng.randrange(-31, 32) for _ in range(dimensions))
        queries.append(query if any(query) else (1,) + query[1:])
    return gates, payloads, data, tuple(queries), len(gate_bytes)


def ordinary(payload, query, dimensions):
    values = unpack('<' + 'h' * (dimensions * dimensions), payload)
    return tuple(sum(values[r * dimensions + j] * query[j] for j in range(dimensions)) for r in range(dimensions))



def run_case(family, rows, dimensions, rng, step_values=STEP_BITS):
    gates, payloads, data, queries, payload_base = make_source(family, rows, dimensions, rng)
    source_id = sha256(data).digest()
    gate_base = 0
    centered_compiled = compile_centered(gates, gate_base, payload_base, source_id)
    centered = decode_centered(centered_compiled['blob'], source_id)
    references = []
    for query in queries:
        scores = [sum(a * x for a, x in zip(row, query)) for row in gates]
        winner = min(range(rows), key=lambda i: (-scores[i], i))
        payload = pack('<' + 'h' * (dimensions * dimensions), *payloads[winner])
        references.append((winner, payload, ordinary(payload, query, dimensions)))
    configs = [('exact_centered', None)]
    for bits in step_values:
        configs += [('exact_split', bits), ('quotient', bits), ('row_sums', bits), ('propagated', bits), ('pair_total', bits), ('pair_dual', bits)]
    result = []
    with TemporaryDirectory(prefix='cassette-joint-scale-') as scratch:
        path = Path(scratch) / 'source.bin'; path.write_bytes(data)
        for method, bits in configs:
            compiled = compile_joint(gates, bits, gate_base, payload_base, source_id,
                                     phase_optimal=(family != 'dual_tie_witness')) if bits else None
            split_compiled = compile_split(compiled) if method == 'exact_split' else None
            guide = (centered_compiled['blob'] if method == 'exact_centered' else
                     split_compiled['blob'] if method == 'exact_split' else
                     compiled['qw_blob'] if method == 'quotient' else
                     compiled['qwt_blob'] if method == 'row_sums' else compiled['blob'])
            runtime = (decode_qw(guide, source_id, b'JSC1') if method == 'quotient' else
                       decode_qwt(guide, source_id) if method == 'row_sums' else
                       decode_joint(guide, source_id) if method in ('propagated', 'pair_total', 'pair_dual') else None)
            split_runtime = decode_split(guide, source_id) if method == 'exact_split' else None
            if method == 'quotient':
                assert 't' not in runtime and 'u' not in runtime and 'L' not in runtime and 'V' not in runtime
            if method == 'row_sums':
                assert 't' in runtime and 'u' not in runtime and 'L' not in runtime and 'V' not in runtime
            counters = Counter()
            with path.open('rb') as stream:
                source = Reader(stream, source_id, data)
                for query, expected in zip(queries, references):
                    source.start_route()
                    if method == 'exact_centered':
                        winner, payload = exact_centered(centered, query, source, gate_base, payload_base, counters)
                    elif method == 'exact_split':
                        winner, payload = exact_split(split_runtime, query, source, gate_base, payload_base, counters)
                    elif method == 'quotient':
                        _, candidate = candidates_quotient(runtime, query, counters)
                        winner, payload = refine(candidate, rows, dimensions, gate_base, payload_base, query, source, counters)
                    elif method == 'row_sums':
                        _, candidate = candidate_from_intervals(runtime, independent_intervals(runtime, query, counters), query, counters)
                        winner, payload = refine(candidate, rows, dimensions, gate_base, payload_base, query, source, counters)
                    elif method == 'propagated':
                        _, candidate = candidate_from_intervals(runtime, propagated_intervals(runtime, query, counters), query, counters)
                        winner, payload = refine(candidate, rows, dimensions, gate_base, payload_base, query, source, counters)
                    elif method == 'pair_total':
                        _, candidate = candidates_pair(runtime, query, counters)
                        winner, payload = refine(candidate, rows, dimensions, gate_base, payload_base, query, source, counters)
                    else:
                        _, candidate = candidates_pair_dual(runtime, query, counters)
                        winner, payload = refine(candidate, rows, dimensions, gate_base, payload_base, query, source, counters)
                    if family == 'dual_tie_witness' and query == (-24, -10, -27, 1):
                        if method in ('propagated', 'pair_total'):
                            assert candidate == (0, 1)
                        if method == 'pair_dual':
                            assert candidate == (0,)
                    source.finish_route()
                    assert (winner, payload, ordinary(payload, query, dimensions)) == expected
            maximum = max(abs(v) for row in gates for v in row)
            query_bound = max(max(abs(v) for v in query) for query in queries)
            fields = (dict(centered_Q=rows * sum(centered_compiled['widths']), header=57 * 8, widths=dimensions * 8)
                      if method == 'exact_centered' else split_compiled['fields_bits']
                      if method == 'exact_split' else
                      dict(header=57 * 8, widths=dimensions * 8, Q=compiled['fields_bits']['Q'], w=compiled['fields_bits']['w'])
                      if method == 'quotient' else
                      dict(header=57 * 8, widths=dimensions * 8, Q=compiled['fields_bits']['Q'], w=compiled['fields_bits']['w'], t=compiled['fields_bits']['t'])
                      if method == 'row_sums' else compiled['fields_bits'])
            numeric_widths = dict(query_coordinate_bits=signed_bits(query_bound),
                                  source_score_accumulator_bits=signed_bits(dimensions * maximum * query_bound))
            result.append(dict(family=family, rows=rows, dimensions=dimensions, method=method,
                               step_bits=bits or 0, guide_bytes=len(guide), guide_field_bits=fields,
                               saturated_slack_metadata_bits=(compiled['saturated_slack_bits'] if method in ('propagated', 'pair_total', 'pair_dual') else None),
                               saturated_slack_guide_bytes=(compiled['saturated_slack_guide_bytes'] if method in ('propagated', 'pair_total', 'pair_dual') else None),
                               source_bytes=len(data), payload_record_bytes=2 * dimensions * dimensions,
                               read_bytes=dict(source.bytes), requests=dict(source.requests),
                               modeled_unique_source_page_bytes=source.page_bytes,
                               calculations=dict(counters), numeric_widths=numeric_widths,
                               output_sha256=sha256(repr(references).encode()).hexdigest()))
    return result

report = []
for family_index, family in enumerate(FAMILIES):
    for size_index, (rows, dimensions) in enumerate(SIZES):
        report.extend(run_case(family, rows, dimensions, Random(SEED + family_index * 100 + size_index)))
report.extend(run_case('dual_tie_witness', 4, 4, Random(SEED + 999), step_values=(2,)))
print(json.dumps(dict(seed=SEED, source_families=list(FAMILIES), sizes=[list(size) for size in SIZES],
                      queries_per_case=QUERY_COUNT, scope='generated signed-int16 gates and payloads; packed-byte, logical-read, and work accounting; full packed fields decoded into unmeasured Python test state; exact original-row/payload reads; no hardware timing or RAM claim',
                      results=report), indent=2))
```

## Comparator boundary

The exact-centered guide is the lossless centered-gate baseline. Exact split is the lossless
quotient-plus-residual baseline. Each precision is measured on the same source/query pair, and the
JSON preserves its actual guide fields and byte costs. The experiment does not call the joint
methods a global optimum: phase choice, precision choice, source layout, adaptive gate refinement,
and the dual's proposed order-merge implementation remain separate optimization dimensions.

The pair-total resource allocation and the scalar dual are established mathematical primitives in
this form. The finite result supports two narrower claims: pair information can improve the
fixed-candidate query-to-original-weight path on a coupled residual source, and common balanced or
near-tie sources can erase that gain while retaining its work. It does not establish a novel
complete-path advantage for a real model or a physical storage device.
