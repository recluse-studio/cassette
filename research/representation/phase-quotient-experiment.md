# Executable query-to-original-weight experiment

This experiment tests the complete conditional path in
[phase-quotient-routing.md](phase-quotient-routing.md). Text becomes byte tokens; original
embedding rows produce the state; three successive source-defined choices select original
matrix records; ordinary integer matrix products and clipping produce each later state.
The reference and both representations receive the same text and original model bytes.

The fixtures contain arbitrary generated integer weights. They are not trained language
models and do not answer the text's questions. The fixture establishes exact routing,
source-byte recovery, and read counts across dependent calculations. It does not establish
language quality, physical external-drive speed, or a model-scale RAM improvement.

The compiler may inspect the complete source. The candidate interpreter receives only a
packed guide, current state, and a file reader. It never receives the reference winner or
the source gate matrix in memory. Scratch source files are created and removed by the
experiment. Read sizes are actual `pread` lengths; the backing file is a local scratch file,
not a physical external-drive qualification.

The guide contains a 57-byte header: magic, dimensions, step exponent, gate and payload byte
offsets, and 32 bytes of source identity. It then contains one byte per quotient-column bit
width, packed row quotients, and packed remainder widths. The script verifies the actual
encoded length. Its Python object memory is not the packed-interpreter RAM bound.

```python
from collections import Counter
from hashlib import sha256
from math import ceil
from os import pread
from pathlib import Path
from random import Random
from struct import pack, unpack, calcsize
from tempfile import TemporaryDirectory
import json

SEED = 2026092101
ROWS, DIMENSIONS, LAYERS, STEP_BITS = 48, 12, 3, 8
HEADER = '<4sHHBQQ32s'
assert calcsize(HEADER) == 57

def pack_bits(values, widths):
    result, offset = 0, 0
    for value, width in zip(values, widths):
        assert 0 <= value < (1 << width)
        result |= value << offset
        offset += width
    return result.to_bytes((offset + 7) // 8, 'little')

def get_bits(blob, base, offset, width):
    if width == 0:
        return 0
    first, shift = divmod(offset, 8)
    count = (shift + width + 7) // 8
    value = int.from_bytes(blob[base + first:base + first + count], 'little')
    return (value >> shift) & ((1 << width) - 1)

def compile_guide(matrix, step_bits, rotate, gate_base, payload_base, source_id):
    rows, dimensions, step = len(matrix), len(matrix[0]), 1 << step_bits
    phases = []
    for j in range(dimensions):
        residues = sorted({row[j] % step for row in matrix})
        gaps = [(step if len(residues) == 1 else
                 (residue - residues[i - 1]) % step, -residue, residue)
                for i, residue in enumerate(residues)]
        phases.append(max(gaps)[2] if rotate else 0)
    quotient = [[(value - phases[j]) // step for j, value in enumerate(row)]
                for row in matrix]
    residues = [[(value - phases[j]) % step for j, value in enumerate(row)]
                for row in matrix]
    minima = [min(row[j] for row in quotient) for j in range(dimensions)]
    quotient = [[value - minima[j] for j, value in enumerate(row)] for row in quotient]
    widths = [max(row[j] for row in quotient).bit_length() for j in range(dimensions)]
    spread = [max(row[j] for row in residues) - min(row[j] for row in residues)
              for j in range(dimensions)]
    encoded = pack(HEADER, b'PQR1', rows, dimensions, step_bits,
                   gate_base, payload_base, source_id)
    encoded += bytes(widths)
    encoded += pack_bits([v for row in quotient for v in row], widths * rows)
    encoded += pack_bits(spread, [step_bits] * dimensions)
    expected = 57 + dimensions + ceil(rows * sum(widths) / 8) + ceil(dimensions * step_bits / 8)
    assert len(encoded) == expected
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            common = phases[j] + (1 << step_bits) * minima[j] + min(r[j] for r in residues)
            error = value - common - (1 << step_bits) * quotient[i][j]
            assert 0 <= error <= spread[j]
    return encoded

class SourceReader:
    def __init__(self, stream, source_id):
        self.stream = stream
        self.source_id = source_id
        self.bytes = Counter()
        self.requests = Counter()

    def read(self, kind, offset, count):
        result = pread(self.stream.fileno(), count, offset)
        assert len(result) == count
        self.bytes[kind] += count
        self.requests[kind] += 1
        return result

def route(guide, query, source, counters):
    magic, rows, dimensions, step_bits, gate_base, payload_base, identity = unpack(HEADER, guide[:57])
    assert magic == b'PQR1' and len(query) == dimensions
    assert identity == source.source_id
    widths = guide[57:57 + dimensions]
    row_bits = sum(widths)
    quotient_base = 57 + dimensions
    spread_base = quotient_base + ceil(rows * row_bits / 8)
    bound = sum(get_bits(guide, spread_base, j * step_bits, step_bits) * abs(x)
                for j, x in enumerate(query))

    def coarse_score(row):
        offset, total = row * row_bits, 0
        for x, width in zip(query, widths):
            total += x * get_bits(guide, quotient_base, offset, width)
            offset += width
        counters['coarse_terms'] += dimensions
        return total

    leader, best = 0, coarse_score(0)
    for i in range(1, rows):
        score = coarse_score(i)
        if score > best:
            leader, best = i, score
    winner, exact_best, count = leader, None, 0
    for i in range(rows):
        gap = (best - coarse_score(i)) << step_bits
        eligible = i == leader or gap < bound or (gap == bound and i < leader)
        if not eligible:
            continue
        count += 1
        if i == leader and count == 1:
            continue
        if exact_best is None:
            raw = source.read('gate', gate_base + leader * 2 * dimensions, 2 * dimensions)
            original = unpack('<' + 'h' * dimensions, raw)
            exact_best = sum(a * x for a, x in zip(original, query))
            counters['exact_gate_terms'] += dimensions
        if i == leader:
            continue
        raw = source.read('gate', gate_base + i * 2 * dimensions, 2 * dimensions)
        original = unpack('<' + 'h' * dimensions, raw)
        score = sum(a * x for a, x in zip(original, query))
        counters['exact_gate_terms'] += dimensions
        if score > exact_best or (score == exact_best and i < winner):
            winner, exact_best = i, score
    counters['route_calls'] += 1
    counters['singleton_routes'] += count == 1
    counters['max_candidates'] = max(counters['max_candidates'], count)
    payload_size = 2 * dimensions * dimensions
    payload = source.read('payload', payload_base + winner * payload_size, payload_size)
    return winner, payload

def clip(value):
    return min(31, max(-31, value))

def ordinary_product(payload, query):
    dimensions = len(query)
    values = unpack('<' + 'h' * (dimensions * dimensions), payload)
    return tuple(clip(sum(values[i * dimensions + j] * query[j]
                          for j in range(dimensions))) for i in range(dimensions))

def initial_state(text, source):
    state = [0] * DIMENSIONS
    for token in text.encode('utf-8'):
        raw = source.read('embedding', token * 2 * DIMENSIONS, 2 * DIMENSIONS)
        row = unpack('<' + 'h' * DIMENSIONS, raw)
        state = [a + b for a, b in zip(state, row)]
    return tuple(map(clip, state))

def make_source(name, generator):
    embeddings = [[generator.randrange(-7, 8) for _ in range(DIMENSIONS)] for _ in range(256)]
    data = bytearray(pack('<' + 'h' * (256 * DIMENSIONS), *(v for row in embeddings for v in row)))
    models, locations = [], []
    for layer in range(LAYERS):
        common = [generator.randrange(-7000, 7000) for _ in range(DIMENSIONS)]
        if name == 'independent':
            gate = [[generator.randrange(-8192, 8192) for _ in range(DIMENSIONS)] for _ in range(ROWS)]
        elif name == 'shared_remainders':
            gate = [[common[j] + 256 * generator.randrange(-8, 9) + generator.randrange(-8, 9)
                     for j in range(DIMENSIONS)] for _ in range(ROWS)]
        elif name == 'near_ties':
            gate = [[common[j] + generator.randrange(-4, 5) for j in range(DIMENSIONS)] for _ in range(ROWS)]
        elif name == 'duplicate_rows':
            gate = [list(common) for _ in range(ROWS)]
        else:
            raise ValueError(name)
        payloads = [pack('<' + 'h' * (DIMENSIONS * DIMENSIONS),
                         *(generator.randrange(-8, 9) for _ in range(DIMENSIONS * DIMENSIONS)))
                    for _ in range(ROWS)]
        gate_base = len(data)
        data.extend(pack('<' + 'h' * (ROWS * DIMENSIONS), *(v for row in gate for v in row)))
        payload_base = len(data)
        for payload in payloads:
            data.extend(payload)
        models.append((gate, payloads))
        locations.append((gate_base, payload_base))
    return bytes(data), embeddings, models, locations

texts = [''] + [f'Calculate {i * 37 - 2000} times {i % 19 - 9}, then add {i * i}.'
                for i in range(128)]
report = []
with TemporaryDirectory(prefix='cassette-routing-') as scratch:
    for case_index, name in enumerate(('independent', 'shared_remainders', 'near_ties', 'duplicate_rows')):
        data, embeddings, models, locations = make_source(name, Random(SEED + case_index))
        source_id = sha256(data).digest()
        source_path = Path(scratch) / (name + '.bin')
        source_path.write_bytes(data)
        reference = []
        for text in texts:
            query = tuple(clip(sum(embeddings[token][j] for token in text.encode('utf-8')))
                          for j in range(DIMENSIONS))
            steps = []
            for gate, payloads in models:
                winner = max(range(ROWS), key=lambda i: (sum(a * x for a, x in zip(gate[i], query)), -i))
                query = ordinary_product(payloads[winner], query)
                steps.append((winner, payloads[winner], query))
            reference.append(steps)
        for rotate in (False, True):
            guides = [compile_guide(gate, STEP_BITS, rotate, *location, source_id)
                      for (gate, _), location in zip(models, locations)]
            counters, observed_hash = Counter(), sha256()
            with source_path.open('rb') as stream:
                source = SourceReader(stream, source_id)
                for text, expected in zip(texts, reference):
                    query = initial_state(text, source)
                    for guide, (want_index, want_payload, want_query) in zip(guides, expected):
                        index, payload = route(guide, query, source, counters)
                        assert index == want_index and payload == want_payload
                        query = ordinary_product(payload, query)
                        assert query == want_query
                        observed_hash.update(pack('<H', index) + bytes(x + 31 for x in query))
            report.append(dict(case=name, phase='width_optimal' if rotate else 'zero',
                               guide_bytes=sum(map(len, guides)),
                               full_gate_bytes=LAYERS * ROWS * DIMENSIONS * 2,
                               input_count=len(texts), source_bytes=len(data),
                               read_bytes=dict(source.bytes), requests=dict(source.requests),
                               calculations=dict(counters), output_sha256=observed_hash.hexdigest()))
print(json.dumps(dict(seed=SEED, rows=ROWS, dimensions=DIMENSIONS, layers=LAYERS,
                     scope='synthetic exact integer routing; no hardware timing', results=report), indent=2))
```

The extended [sum and moment experiment](remainder-sum-experiment.md) includes these eight
configurations and records their counts in [its JSON report](remainder-sum-results.json).
That comparison adds exact centered and split encodings. The finite phase optimum has a
separate declared small-domain proof. A win over phase zero alone is not a win over the
best established method.
