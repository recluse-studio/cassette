# Packed-guide replay of the stronger pair interpretation

The scalar-dual method can exclude a row that survives both propagated row bounds and
pair-total bounds. This fixture proves that narrower claim through original file reads.
It also compares the full guide size with a lossless centered guide; the latter is
smaller in this tiny case. The fixture therefore establishes an interpretation gain,
not a winning memory frontier or a model-scale result.

The original gate is \(A=4Q+E\), with

\[
 E=\begin{pmatrix}3&0&3&1\\0&1&0&2\\3&0&3&0\\1&0&1&0\end{pmatrix},
 \qquad Q=\begin{pmatrix}0&0&0&250\\0&0&0&214\\0&0&0&0\\0&0&0&0\end{pmatrix},
 \qquad x=(-24,-10,-27,1).
\]

The exact source scores are \((848,848,-153,-51)\), so the least-index winner is
zero. Propagated residual intervals have lower endpoints \((-163,-81,-153,-54)\)
and upper endpoints \((-107,-8,-80,2)\). For row one against row zero, the separate
upper difference is 155, pair-total support is 164, and scalar-dual support is 144.
The coarse difference is \(-144\). Only the dual bound proves that row one cannot
beat row zero under the required tie rule. Other rows are already excluded.

The interpreter below receives packed \(Q,w,t\), the packed clipped slacks, source
identity and layout, and the available query. It receives neither \(E\) nor original
gate entries. To reuse the verified support evaluator, it supplies algebraic stand-ins
\((u',L',V')=(\alpha,0,\alpha+\beta)\). Those stand-ins reproduce only the
eliminated single and pair constraints. They are not original column totals or a
reconstituted aggregate row, and no aggregate-row equality is applied to them.

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from hashlib import sha256
from os import pread
from struct import pack, unpack
from math import ceil
import json

def definitions(name, marker):
    text = Path('research/representation/' + name).read_text()
    code = text.split('```python\n')[1].split('\n```')[0].split(marker)[0]
    result = {}
    exec(compile(code, name, 'exec'), result)
    return result

base = definitions('remainder-sum-experiment.md', "\ntexts = ['']")
codec = definitions('saturated-slack-representation.md', '\npatterns = ')
dual = definitions('pair-dual-refinement.md', '\nloose = ')

residual = ((3, 0, 3, 1), (0, 1, 0, 2), (3, 0, 3, 0), (1, 0, 1, 0))
quotients = ((0, 0, 0, 250), (0, 0, 0, 214), (0, 0, 0, 0), (0, 0, 0, 0))
gate = [tuple(4 * q + e for q, e in zip(qrow, erow))
        for qrow, erow in zip(quotients, residual)]
payloads = [pack('<16h', *(i * 16 + j - 31 for j in range(16))) for i in range(4)]
source_bytes = pack('<16h', *(v for row in gate for v in row)) + b''.join(payloads)
identity = sha256(source_bytes).digest()
packed_base = base['compile_sums'](gate, 2, False, 4, 0, 32, identity)
full_summary = dual['summaries'](residual, (3, 1, 3, 2))
totals, columns, _, _, lower, upper = full_summary
packed_slack = codec['encode_slack']((3, 1, 3, 2),
                                     [u - lo for u, lo in zip(columns, lower)],
                                     [hi - u for u, hi in zip(columns, upper)])
exact_guide = base['compile_guide'](gate, 0, False, 0, 32, identity)

def interpret(guide, slack_code, query, source_identity, method):
    magic, rows, dimensions, bits, gate_base, payload_base, source_id = unpack(base['HEADER'], guide[:57])
    assert magic == b'PQR1' and source_id == source_identity and dimensions == len(query)
    widths = guide[57:57 + dimensions]
    row_bits, quotient_base = sum(widths), 57 + dimensions
    spread_base = quotient_base + ceil(rows * row_bits / 8)
    get = base['get_bits']
    spread = tuple(get(guide, spread_base, j * bits, bits) for j in range(dimensions))
    block_base = spread_base + ceil(dimensions * bits / 8)
    assert unpack('<H', guide[block_base:block_base + 2])[0] == dimensions
    whole = sum(spread)
    totals = tuple(get(guide, block_base + 2, i * whole.bit_length(), whole.bit_length()) for i in range(rows))
    slacks = codec['decode_slack'](slack_code, spread)
    lower = tuple(tuple(max(0, t - whole + w) for w in spread) for t in totals)
    upper = tuple(tuple(min(w, t) for w in spread) for t in totals)
    alpha = tuple(a for a, _ in slacks)
    virtual_columns = alpha
    virtual_lower = (0,) * dimensions
    virtual_upper = tuple(a + b for a, b in slacks)
    summary = totals, virtual_columns, lower, upper, virtual_lower, virtual_upper
    coarse = []
    for i in range(rows):
        value, offset = 0, i * row_bits
        for x, width in zip(query, widths):
            value += x * get(guide, quotient_base, offset, width)
            offset += width
        coarse.append(value << bits)

    def support(i, coefficients):
        lo = [a + max(0, b - a - beta) for a, b, (_, beta) in zip(lower[i], upper[i], slacks)]
        hi = [a + min(b - a, alpha) for a, b, (alpha, _) in zip(lower[i], upper[i], slacks)]
        value = sum(a * x for a, x in zip(lo, coefficients))
        remaining = totals[i] - sum(lo)
        for j in sorted(range(dimensions), key=lambda j: coefficients[j], reverse=True):
            take = min(remaining, hi[j] - lo[j])
            remaining -= take
            value += take * coefficients[j]
        assert remaining == 0
        return value

    intervals = [(coarse[i] - support(i, tuple(-x for x in query)),
                  coarse[i] + support(i, query)) for i in range(rows)]
    anchor = max(range(rows), key=lambda i: (intervals[i][0], -i))
    retained = [anchor]
    comparisons = {}
    for i in range(rows):
        if i == anchor:
            continue
        threshold = intervals[i][1] - intervals[anchor][0]
        if threshold < 0 or (threshold == 0 and i > anchor):
            continue
        if method == 'dual':
            doubled, _ = dual['dual_search'](spread, summary, i, anchor, query)
            assert doubled % 2 == 0
            bound = doubled // 2
        else:
            bound = dual['pair_support'](spread, summary, i, anchor, query)
        difference = coarse[i] - coarse[anchor] + bound
        comparisons[i] = difference
        if difference > 0 or (difference == 0 and i < anchor):
            retained.append(i)
    return sorted(retained), gate_base, payload_base, comparisons

query = (-24, -10, -27, 1)
records = []
with TemporaryDirectory(prefix='cassette-dual-replay-') as scratch:
    source_path = Path(scratch) / 'source.bin'
    source_path.write_bytes(source_bytes)
    assert sha256(source_path.read_bytes()).digest() == identity
    for method in ('pair_total', 'dual'):
        retained, gate_base, payload_base, comparisons = interpret(packed_base, packed_slack, query, identity, method)
        gate_reads = []
        with source_path.open('rb') as stream:
            if len(retained) == 1:
                winner = retained[0]
            else:
                scores = []
                for i in retained:
                    raw = pread(stream.fileno(), 8, gate_base + i * 8)
                    gate_reads.append(i)
                    scores.append((sum(a * x for a, x in zip(unpack('<4h', raw), query)), -i))
                winner = -max(scores)[1]
            payload = pread(stream.fileno(), 32, payload_base + winner * 32)
        assert winner == 0 and payload == payloads[0]
        weights = unpack('<16h', payload)
        output = [sum(weights[i * 4 + j] * query[j] for j in range(4)) for i in range(4)]
        records.append(dict(method=method, retained=retained, gate_reads=gate_reads,
                            gate_bytes=8 * len(gate_reads), payload_bytes=len(payload),
                            guide_bytes=len(packed_base) + len(packed_slack),
                            comparison_upper_differences=comparisons, output=output))
assert records[0]['retained'] == [0, 1] and records[1]['retained'] == [0]
assert records[0]['output'] == records[1]['output']
print(json.dumps(dict(source_sha256=identity.hex(), source_bytes=len(source_bytes),
                     exact_centered_guide_bytes=len(exact_guide), replays=records), indent=2))
```

The fixture materializes four row intervals and reference bytes for verification. It is
not the streaming peak-memory schedule. The 160-byte source occupies less than one
4,096-byte page; the different gate requests provide no physical-drive latency evidence.
Source binding is verified once on the temporary immutable file, with the same boundary
as the earlier generated-source experiments.

The [saved replay](dual-original-weight-results.json) reports a 74-byte joint guide
under both interpretations. Pair-total interpretation reads 16 original gate bytes;
scalar-dual interpretation reads none. Both read the same 32-byte original payload and
return \((1799,1559,1319,1079)\) under ordinary integer matrix multiplication. The
complete centered guide takes 69 bytes and also needs no gate discovery reads. It wins
the guide-size comparison on this source. That stronger comparator remains part of the
research result rather than being hidden by the same-guide interpretation gain.
