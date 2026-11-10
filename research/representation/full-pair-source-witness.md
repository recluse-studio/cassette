# Packed original-weight replay for the full-pair witness

This replay makes the full-pair witness pass through the required source path:
a resident guide derives the needed region from the query, its header resolves
the original payload offset, and the ordinary calculation consumes the
source-precision payload. The candidate interpreter receives no residual
matrix and makes no original gate read.

The general support solver from full-pair-polymatroid.md passed its current
independent review and finite fence. This replay invokes that solver on its
packed \(Q,w,t,u\) fields. The binary quota result in
full-aggregate-feasibility.md is an independent check for this particular
zero-anchor case. The replay is a finite source check; it makes no RAM,
hardware, novelty, or general-model claim.

## 1. Exact source and resident fields

\[
 E=\begin{pmatrix}
 0&0&0&0\\
 0&0&1&1\\
 0&1&0&0\\
 1&1&0&1
 \end{pmatrix},\quad
 Q_0=Q_1=(1,0,0,0),\quad Q_2=Q_3=(0,0,0,0).
\]

The source gate is \(A=2Q+E\), the query is
\(x=(1,-1,1,-1)\), and the original scores are
\((2,2,-1,-1)\). The least-index winner is zero. The derived values are

\[
 w=(1,1,1,1),\qquad t=(0,2,1,3),\qquad u=(1,2,1,2).
\]

The temporary source has four little-endian signed-16-bit gate rows at offsets
\(8i\), followed by four 32-byte signed-16-bit payload matrices at
\(32+32i\). The established quotient header records magic, shape, step,
both bases, and a 32-byte source digest. Fixed int16 strides follow from the
declared scalar encoding and dimension.

The concrete complete formats are:

| Format | Stored fields after the 57-byte locator header | Bytes |
|---|---|---:|
| Exact centered | column bit widths and 20 packed exact gate bits | 64 |
| Fixed/adaptive | quotient, widths, and four row totals | 65 |
| Full pair | quotient, widths, four row totals, four column totals | 67 |

The full-pair decoder derives all bit widths from rows, dimensions, and
decoded widths. It has no model-specific table outside the packed guide.

## 2. Source-region result

The row-total interpreter excludes rows two and three but retains row one:
its coarse difference against row zero is zero and its independent support is
two. Both its fixed and source-order adaptive variants consequently read gate
rows zero and one.

The full-pair interpreter supplies only

\[
 (w,u,\{1,3\},t_1,t_0)
 =((1,1,1,1),(1,2,1,2),(1,3),2,0)
\]

to FullPairSupport. It obtains support zero. With zero coarse difference,
the tie rule excludes row one. The candidate region is therefore \(\{0\}\).
No \(E\) value enters the candidate interpreter. Equivalently, the independent
binary quota is \(p_2+p_4\geq1\), hence
\(x^Tp=2-2(p_2+p_4)\leq0\).

The projected-pair interpreter uses the *same* 67-byte \(Q,w,t,u\) guide. It
derives its row envelopes and their \(L,V\) sums algebraically from \(t,w\);
it does not read \(E\). Its projected support for row one is two, so it retains
rows zero and one and reads 16 gate bytes. The full support value zero is
therefore a strict interpretation gain at identical resident guide content.

## 3. Reproducible packed replay

The compiler and verifier see the source residuals. Candidate routing receives
only a guide, query, digest-bound reader, and FullPairSupport. The verifier
reads every original gate row. The center comparator decodes its full packed
gate and needs no discovery read.

~~~python
from collections import Counter
from hashlib import sha256
from os import pread
from pathlib import Path
from struct import pack, unpack
from tempfile import TemporaryDirectory
import json

def definitions(name, marker):
    text = Path('research/representation/' + name).read_text()
    fence = chr(96) * 3
    code = text.split(fence + 'python\n')[1].split('\n' + fence)[0].split(marker)[0]
    scope = {}
    exec(compile(code, name, 'exec'), scope)
    return scope

base = definitions('phase-quotient-experiment.md', "texts = ['']")
pair = definitions('full-pair-polymatroid.md', '\nSEED = ')
projected = definitions('pair-dual-refinement.md', '\nloose = ')
E = ((0, 0, 0, 0), (0, 0, 1, 1), (0, 1, 0, 0), (1, 1, 0, 1))
Q = ((1, 0, 0, 0), (1, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0))
x = (1, -1, 1, -1)
gate = tuple(tuple(2 * q + e for q, e in zip(qrow, erow)) for qrow, erow in zip(Q, E))
payloads = tuple(pack('<16h', *(16 * i + j - 31 for j in range(16))) for i in range(4))
source_bytes = pack('<16h', *(v for row in gate for v in row)) + b''.join(payloads)
identity = sha256(source_bytes).digest()

def offsets(guide):
    magic, rows, dimensions, bits, gate_base, payload_base, source_id = unpack(base['HEADER'], guide[:57])
    widths = tuple(guide[57:57 + dimensions])
    qbase = 57 + dimensions
    sbase = qbase + (rows * sum(widths) + 7) // 8
    tail = sbase + (dimensions * bits + 7) // 8
    return magic, rows, dimensions, bits, gate_base, payload_base, source_id, widths, qbase, sbase, tail

def compile_summary(full):
    core = bytearray(base['compile_guide'](gate, 1, False, 0, 32, identity))
    core[:4] = b'FPW1' if full else b'FRW1'
    _, rows, dimensions, _, _, _, _, _, _, _, tail = offsets(core)
    totals = tuple(map(sum, E))
    columns = tuple(map(sum, zip(*E)))
    widths = (1,) * dimensions
    total_bits = sum(widths).bit_length()
    column_widths = tuple((rows * width).bit_length() for width in widths)
    core.extend(base['pack_bits'](totals, (total_bits,) * rows))
    if full:
        core.extend(base['pack_bits'](columns, column_widths))
    expected = tail + (rows * total_bits + 7) // 8
    if full:
        expected += (sum(column_widths) + 7) // 8
    assert len(core) == expected
    return bytes(core)

fixed, full = compile_summary(False), compile_summary(True)
centered = base['compile_guide'](gate, 0, False, 0, 32, identity)
assert tuple(map(len, (centered, fixed, full))) == (64, 65, 67)

class Reader:
    def __init__(self, stream):
        self.stream, self.bytes, self.requests = stream, Counter(), Counter()
    def read(self, kind, offset, count):
        value = pread(self.stream.fileno(), count, offset)
        assert len(value) == count
        self.bytes[kind] += count
        self.requests[kind] += 1
        return value

def decode(guide, want_columns):
    magic, rows, dimensions, bits, gb, pb, source_id, widths, qb, sb, tail = offsets(guide)
    assert magic == (b'FPW1' if want_columns else b'FRW1')
    assert source_id == identity and bits == 1 and widths == (1, 0, 0, 0)
    w = tuple(base['get_bits'](guide, sb, j, 1) for j in range(dimensions))
    total_bits = sum(w).bit_length()
    totals = tuple(base['get_bits'](guide, tail, total_bits * i, total_bits) for i in range(rows))
    column_base = tail + (rows * total_bits + 7) // 8
    column_widths = tuple((rows * width).bit_length() for width in w)
    columns = None
    if want_columns:
        offset = 0
        decoded = []
        for width in column_widths:
            decoded.append(base['get_bits'](guide, column_base, offset, width))
            offset += width
        columns = tuple(decoded)
    return rows, dimensions, gb, pb, widths, w, totals, columns, qb

def coarse(guide, rows, widths, qbase):
    values = []
    for i in range(rows):
        score, at = 0, i * sum(widths)
        for coordinate, width in zip(x, widths):
            score += coordinate * base['get_bits'](guide, qbase, at, width)
            at += width
        values.append(2 * score)
    return tuple(values)

def independent_support(total, widths, upper):
    remaining = total
    value = 0
    for j in sorted(range(len(widths)), key=lambda j: (x[j], j), reverse=upper):
        take = min(remaining, widths[j])
        value += take * x[j]
        remaining -= take
    assert remaining == 0
    return value

def resolve(retained, reader, gate_base, payload_base, dimensions):
    gate_stride = 2 * dimensions
    payload_stride = 2 * dimensions * dimensions
    if len(retained) == 1:
        winner = retained[0]
    else:
        scores = []
        for i in retained:
            raw = reader.read('gate', gate_base + gate_stride * i, gate_stride)
            scores.append((sum(a * b for a, b in zip(unpack('<' + 'h' * dimensions, raw), x)), -i))
        winner = -max(scores)[1]
    return winner, reader.read('payload', payload_base + payload_stride * winner, payload_stride)

def fixed_route(guide, reader, adaptive):
    rows, dimensions, gb, pb, widths, w, totals, _, qb = decode(guide, False)
    c = coarse(guide, rows, widths, qb)
    lower = tuple(c[i] + independent_support(totals[i], w, False) for i in range(rows))
    upper = tuple(c[i] + independent_support(totals[i], w, True) for i in range(rows))
    anchor = max(range(rows), key=lambda i: (lower[i], -i))
    initial = [anchor] + [i for i in range(rows) if i != anchor and
               (upper[i] > lower[anchor] or (upper[i] == lower[anchor] and i < anchor))]
    if not adaptive:
        return tuple(sorted(initial)), resolve(tuple(sorted(initial)), reader, gb, pb, dimensions)
    raw = reader.read('gate', gb + 2 * dimensions * anchor, 2 * dimensions)
    best = sum(a * b for a, b in zip(unpack('<' + 'h' * dimensions, raw), x))
    common_upper = best - lower[anchor]
    retained = [anchor]
    for i in initial:
        if i == anchor:
            continue
        if upper[i] + common_upper < best or (upper[i] + common_upper == best and i > anchor):
            continue
        raw = reader.read('gate', gb + 2 * dimensions * i, 2 * dimensions)
        value = sum(a * b for a, b in zip(unpack('<' + 'h' * dimensions, raw), x))
        if value > best or (value == best and i < anchor):
            anchor, best = i, value
        common_upper = min(common_upper, value - lower[i])
        retained.append(i)
    return tuple(retained), (anchor, reader.read('payload', pb + 2 * dimensions * dimensions * anchor,
                                                  2 * dimensions * dimensions))

def full_pair_route(guide, reader):
    rows, dimensions, gb, pb, widths, w, totals, columns, qb = decode(guide, True)
    c = coarse(guide, rows, widths, qb)
    anchor = max(range(rows), key=lambda i: (c[i], -i))
    retained = [anchor]
    supports = {}
    for i in range(rows):
        if i == anchor:
            continue
        omitted = tuple(totals[j] for j in range(rows) if j not in (i, anchor))
        support = pair['FullPairSupport'](w, columns, omitted, totals[i], totals[anchor]).exact(x)
        supports[i] = support
        difference = c[i] - c[anchor] + support
        if difference > 0 or (difference == 0 and i < anchor):
            retained.append(i)
    winner, payload = resolve(tuple(retained), reader, gb, pb, dimensions)
    return tuple(retained), supports, winner, payload

def projected_pair_route(guide, reader):
    rows, dimensions, gb, pb, widths, w, totals, columns, qb = decode(guide, True)
    whole = sum(w)
    lower = tuple(tuple(max(0, total - whole + width) for width in w) for total in totals)
    upper = tuple(tuple(min(width, total) for width in w) for total in totals)
    summary = totals, columns, lower, upper, tuple(map(sum, zip(*lower))), tuple(map(sum, zip(*upper)))
    c = coarse(guide, rows, widths, qb)
    anchor = max(range(rows), key=lambda i: (c[i], -i))
    retained, supports = [anchor], {}
    for i in range(rows):
        if i == anchor:
            continue
        support = projected['projected_support'](w, summary, i, anchor, x)
        supports[i] = support
        difference = c[i] - c[anchor] + support
        if difference > 0 or (difference == 0 and i < anchor):
            retained.append(i)
    winner, payload = resolve(tuple(retained), reader, gb, pb, dimensions)
    return tuple(retained), supports, winner, payload

def centered_route(guide, reader):
    magic, rows, dimensions, bits, gb, pb, source_id, widths, qb, _, _ = offsets(guide)
    assert magic == b'PQR1' and bits == 0 and source_id == identity
    scores = []
    for i in range(rows):
        score, at = 0, i * sum(widths)
        for coordinate, width in zip(x, widths):
            score += coordinate * base['get_bits'](guide, qb, at, width)
            at += width
        scores.append(score)
    return (max(range(rows), key=lambda i: (scores[i], -i)),), gb, pb, dimensions

def reference_route(reader, guide):
    _, rows, dimensions, _, gate_base, payload_base, source_id, _, _, _, _ = offsets(guide)
    assert source_id == identity
    scores = []
    for i in range(rows):
        raw = reader.read('gate', gate_base + 2 * dimensions * i, 2 * dimensions)
        scores.append(sum(a * b for a, b in zip(unpack('<' + 'h' * dimensions, raw), x)))
    winner = max(range(rows), key=lambda i: (scores[i], -i))
    return tuple(scores), winner, reader.read('payload', payload_base + 2 * dimensions * dimensions * winner,
                                               2 * dimensions * dimensions)

with TemporaryDirectory(prefix='cassette-full-pair-source-') as scratch:
    path = Path(scratch) / 'source.bin'
    path.write_bytes(source_bytes)
    assert sha256(path.read_bytes()).digest() == identity
    with path.open('rb') as stream:
        reader = Reader(stream); retained, supports, winner, payload = full_pair_route(full, reader)
        full_record = dict(retained=retained, supports=supports, winner=winner,
                           reads=dict(reader.bytes), output=base['ordinary_product'](payload, x))
    with path.open('rb') as stream:
        reader = Reader(stream); retained, supports, winner, payload = projected_pair_route(full, reader)
        projected_record = dict(retained=retained, supports=supports, winner=winner,
                                reads=dict(reader.bytes), output=base['ordinary_product'](payload, x))
    with path.open('rb') as stream:
        reader = Reader(stream); retained, (winner, payload) = fixed_route(fixed, reader, False)
        fixed_record = dict(retained=retained, winner=winner, reads=dict(reader.bytes),
                            output=base['ordinary_product'](payload, x))
    with path.open('rb') as stream:
        reader = Reader(stream); retained, (winner, payload) = fixed_route(fixed, reader, True)
        adaptive_record = dict(retained=retained, winner=winner, reads=dict(reader.bytes),
                               output=base['ordinary_product'](payload, x))
    with path.open('rb') as stream:
        reader = Reader(stream); retained, gb, pb, dimensions = centered_route(centered, reader)
        winner, payload = resolve(retained, reader, gb, pb, dimensions)
        centered_record = dict(retained=retained, winner=winner, reads=dict(reader.bytes),
                               output=base['ordinary_product'](payload, x))
    with path.open('rb') as stream:
        reader = Reader(stream); scores, winner, payload = reference_route(reader, full)
        reference = dict(scores=scores, winner=winner, reads=dict(reader.bytes),
                         output=base['ordinary_product'](payload, x))

assert full_record['supports'] == {1: 0, 2: 1, 3: 1}
assert projected_record['supports'][1] == 2
assert full_record['retained'] == centered_record['retained'] == (0,)
assert projected_record['retained'] == (0, 1)
assert fixed_record['retained'] == adaptive_record['retained'] == (0, 1)
assert full_record['reads'] == centered_record['reads'] == {'payload': 32}
assert projected_record['reads'] == {'gate': 16, 'payload': 32}
assert fixed_record['reads'] == adaptive_record['reads'] == {'gate': 16, 'payload': 32}
assert reference['scores'] == (2, 2, -1, -1)
assert reference['reads'] == {'gate': 32, 'payload': 32}
assert all(record['winner'] == reference['winner'] == 0
           for record in (full_record, projected_record, fixed_record, adaptive_record, centered_record))
assert len({record['output'] for record in (full_record, fixed_record, adaptive_record, centered_record,
                                             projected_record, reference)}) == 1
print(json.dumps(dict(source_sha256=identity.hex(), source_bytes=len(source_bytes),
                      guide_bytes=dict(centered=len(centered), fixed=len(fixed), full_pair=len(full)),
                      full_pair=full_record, projected_pair=projected_record,
                      fixed=fixed_record, adaptive=adaptive_record,
                      centered=centered_record, reference=reference,
                      scope='temporary int16 source; logical pread bytes only'),
                 indent=2))
~~~

The fence asserts the following:

~~~text
full-pair guide: 67 bytes; exact-centered guide: 64 bytes
full-pair and exact-centered discovery reads: 0 gate bytes
projected-pair, fixed, and source-order adaptive discovery reads: 16 gate bytes
all methods select row 0, fetch its original 32-byte payload, and return the same ordinary output
~~~

## 4. Boundary

The exact centered guide is three bytes smaller and also makes zero discovery
reads. This witness therefore is not a resident-memory win. At the same
67-byte \(Q,w,t,u\) guide, full support prevents two original gate reads that
projected support still requires. It also prevents the reads made by the
smaller row-total guide, including its source-order adaptive update.

The 160-byte source fits within one conventional 4,096-byte page. Logical
pread counts here do not prove a transfer, latency, throughput, or peak-RAM
difference. The Python verifier's objects and counters are verification state,
not a packed interpreter memory schedule.
