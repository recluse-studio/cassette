# Packed remainder-sum experiment

This executable experiment exercises MATHS section 12 and the proofs in
[remainder-sum-certificates.md](remainder-sum-certificates.md). Run the Python fence from
the repository root. It reuses the source generator, source reader, original arithmetic,
and quotient format from [phase-quotient-experiment.md](phase-quotient-experiment.md).
The compiler and full reference may inspect source matrices; the candidate interpreter
receives only its packed representation, the available state, and a source reader.

The exact centered-gate comparator uses step exponent zero: its packed coefficients retain
all row differences, discarding only a common column offset that cannot affect argmax.
It needs one score pass and no discovery reads. The sums candidate makes two streaming
passes and counts its additional support work. Both retrieve the same original payloads.
All current-layer and other-layer guides remain resident in this experiment; their total
encoded bytes are reported. Interpreter objects and arithmetic buffers are additional RAM.

The read-page model rounds each request to 4,096 bytes. It also counts unique gate pages
within each routing operation, modeling perfect coalescing for that operation. These are
two explicit read-accounting policies, not a latency measurement or a drive specification.
The source identity is established during fixture creation; revalidation costs on a real
source are outside these per-query counts and cannot be inferred to be zero.

```python
from pathlib import Path
base_text = Path('research/representation/phase-quotient-experiment.md').read_text()
base_code = base_text.split('```python\n')[1].split('\n```')[0].split("texts = ['']")[0]
exec(compile(base_code, 'phase-quotient-experiment.md', 'exec'))
from math import isqrt

def compile_sums(matrix, step_bits, rotate, block_size, gate_base, payload_base, source_id):
    base = compile_guide(matrix, step_bits, rotate, gate_base, payload_base, source_id)
    rows, dimensions = len(matrix), len(matrix[0])
    widths = base[57:57 + dimensions]
    row_bits, quotient_base = sum(widths), 57 + dimensions
    spread_base = quotient_base + ceil(rows * row_bits / 8)
    spread = [get_bits(base, spread_base, j * step_bits, step_bits) for j in range(dimensions)]
    residuals = []
    for i, row in enumerate(matrix):
        offset, residual = i * row_bits, []
        for j, width in enumerate(widths):
            residual.append(row[j] - (get_bits(base, quotient_base, offset, width) << step_bits))
            offset += width
        residuals.append(residual)
    common = [min(row[j] for row in residuals) for j in range(dimensions)]
    residuals = [[value - common[j] for j, value in enumerate(row)] for row in residuals]
    assert all(0 <= row[j] <= spread[j] for row in residuals for j in range(dimensions))
    blocks = [range(start, min(dimensions, start + block_size)) for start in range(0, dimensions, block_size)]
    sum_widths = [sum(spread[j] for j in block).bit_length() for block in blocks]
    totals = [sum(row[j] for j in block) for row in residuals for block in blocks]
    encoded = base + pack('<H', block_size) + pack_bits(totals, sum_widths * rows)
    assert len(encoded) == len(base) + 2 + ceil(rows * sum(sum_widths) / 8)
    return encoded

def compile_moments(matrix, step_bits, rotate, block_size, gate_base, payload_base, source_id):
    base = compile_sums(matrix, step_bits, rotate, block_size, gate_base, payload_base, source_id)
    rows, dimensions = len(matrix), len(matrix[0])
    widths = base[57:57 + dimensions]
    row_bits, quotient_base = sum(widths), 57 + dimensions
    spread_base = quotient_base + ceil(rows * row_bits / 8)
    spread = [get_bits(base, spread_base, j * step_bits, step_bits) for j in range(dimensions)]
    residuals = []
    for i, row in enumerate(matrix):
        offset, residual = i * row_bits, []
        for j, width in enumerate(widths):
            residual.append(row[j] - (get_bits(base, quotient_base, offset, width) << step_bits))
            offset += width
        residuals.append(residual)
    common = [min(row[j] for row in residuals) for j in range(dimensions)]
    residuals = [[value - common[j] for j, value in enumerate(row)] for row in residuals]
    blocks = [range(start, min(dimensions, start + block_size)) for start in range(0, dimensions, block_size)]
    square_widths = [sum(spread[j] ** 2 for j in block).bit_length() for block in blocks]
    squares = [sum(row[j] ** 2 for j in block) for row in residuals for block in blocks]
    return base + pack_bits(squares, square_widths * rows)

class PageReader(SourceReader):
    def __init__(self, stream, source_id):
        super().__init__(stream, source_id)
        self.rounded = Counter()
        self.route_pages = set()
        self.gate_pages_across_routes = 0

    def read(self, kind, offset, count):
        result = super().read(kind, offset, count)
        pages = range(offset // 4096, (offset + count - 1) // 4096 + 1)
        self.rounded[kind] += 4096 * len(pages)
        if kind == 'gate':
            self.route_pages.update(pages)
        return result

def choose_and_fetch(rows, dimensions, gate_base, payload_base, leader, eligible, query, source, counters):
    winner, exact_best, count = leader, None, 0
    for i in range(rows):
        if not eligible(i):
            continue
        count += 1
        if i == leader and count == 1:
            continue
        if exact_best is None:
            raw = source.read('gate', gate_base + leader * dimensions * 2, dimensions * 2)
            exact_best = sum(a * x for a, x in zip(unpack('<' + 'h' * dimensions, raw), query))
            counters['exact_gate_terms'] += dimensions
        if i == leader:
            continue
        raw = source.read('gate', gate_base + i * dimensions * 2, dimensions * 2)
        score = sum(a * x for a, x in zip(unpack('<' + 'h' * dimensions, raw), query))
        counters['exact_gate_terms'] += dimensions
        if score > exact_best or (score == exact_best and i < winner):
            winner, exact_best = i, score
    counters['route_calls'] += 1
    counters['singleton_routes'] += count == 1
    counters['candidate_count'] += count
    counters['max_candidates'] = max(counters['max_candidates'], count)
    size = 2 * dimensions * dimensions
    return winner, source.read('payload', payload_base + winner * size, size)

def sum_route(guide, query, source, counters, moments=False):
    magic, rows, dimensions, step_bits, gate_base, payload_base, identity = unpack(HEADER, guide[:57])
    assert magic == b'PQR1' and identity == source.source_id and len(query) == dimensions
    widths = guide[57:57 + dimensions]
    row_bits, quotient_base = sum(widths), 57 + dimensions
    spread_base = quotient_base + ceil(rows * row_bits / 8)
    spread = [get_bits(guide, spread_base, j * step_bits, step_bits) for j in range(dimensions)]
    base_size = spread_base + ceil(dimensions * step_bits / 8)
    block_size = unpack('<H', guide[base_size:base_size + 2])[0]
    blocks = [range(start, min(dimensions, start + block_size)) for start in range(0, dimensions, block_size)]
    orders = [sorted(block, key=lambda j: (query[j], j)) for block in blocks]
    sum_widths = [sum(spread[j] for j in block).bit_length() for block in blocks]
    sum_row_bits, sums_base = sum(sum_widths), base_size + 2
    square_widths = [sum(spread[j] ** 2 for j in block).bit_length() for block in blocks] if moments else []
    square_row_bits = sum(square_widths)
    squares_base = sums_base + ceil(rows * sum_row_bits / 8)
    query_sums = [sum(query[j] for j in block) for block in blocks] if moments else []
    query_squares = [sum(query[j] ** 2 for j in block) for block in blocks] if moments else []
    counters['query_sort_calls'] += len(blocks)
    counters['query_sorted_coordinates'] += dimensions
    counters['max_sorted_index_count'] = max(counters['max_sorted_index_count'], dimensions)

    def support(order, total):
        score = 0
        for j in order:
            if total == 0:
                break
            take = min(total, spread[j])
            score += take * query[j]
            total -= take
            counters['support_coordinates'] += 1
        assert total == 0
        return score

    def interval(row, upper):
        offset, score = row * row_bits, 0
        for x, width in zip(query, widths):
            score += x * get_bits(guide, quotient_base, offset, width)
            offset += width
        counters['coarse_terms'] += dimensions
        score <<= step_bits
        offset, square_offset = row * sum_row_bits, row * square_row_bits
        for b, (order, width) in enumerate(zip(orders, sum_widths)):
            total = get_bits(guide, sums_base, offset, width)
            offset += width
            bound = support(reversed(order) if upper else order, total)
            if moments:
                square = get_bits(guide, squares_base, square_offset, square_widths[b])
                square_offset += square_widths[b]
                n, query_sum = len(order), query_sums[b]
                discriminant = (n * square - total * total) * (n * query_squares[b] - query_sum * query_sum)
                assert discriminant >= 0
                radius = isqrt(discriminant)
                moment_bound = ((total * query_sum + radius) // n if upper
                                else -((radius - total * query_sum) // n))
                bound = min(bound, moment_bound) if upper else max(bound, moment_bound)
                counters['integer_square_roots'] += 1
            score += bound
        return score

    leader, lower = 0, interval(0, False)
    for i in range(1, rows):
        candidate = interval(i, False)
        if candidate > lower:
            leader, lower = i, candidate

    def eligible(i):
        upper = interval(i, True)
        return i == leader or upper > lower or (upper == lower and i < leader)
    return choose_and_fetch(rows, dimensions, gate_base, payload_base, leader,
                            eligible, query, source, counters)

def moment_route(guide, query, source, counters):
    return sum_route(guide, query, source, counters, moments=True)

def exact_centered_route(guide, query, source, counters):
    magic, rows, dimensions, step_bits, gate_base, payload_base, identity = unpack(HEADER, guide[:57])
    assert magic == b'PQR1' and step_bits == 0 and identity == source.source_id
    widths, leader, best = guide[57:57 + dimensions], 0, None
    row_bits, base = sum(widths), 57 + dimensions
    for i in range(rows):
        score, offset = 0, i * row_bits
        for x, width in zip(query, widths):
            score += x * get_bits(guide, base, offset, width)
            offset += width
        if best is None or score > best:
            leader, best = i, score
    counters['coarse_terms'] += rows * dimensions
    counters['route_calls'] += 1
    counters['singleton_routes'] += 1
    counters['candidate_count'] += 1
    counters['max_candidates'] = 1
    size = 2 * dimensions * dimensions
    return leader, source.read('payload', payload_base + leader * size, size)

def exact_split_route(guide, query, source, counters):
    magic, rows, dimensions, step_bits, gate_base, payload_base, identity = unpack(HEADER, guide[:57])
    assert magic == b'PQR1' and identity == source.source_id
    widths = guide[57:57 + dimensions]
    row_bits, quotient_base = sum(widths), 57 + dimensions
    spread_base = quotient_base + ceil(rows * row_bits / 8)
    spread = [get_bits(guide, spread_base, j * step_bits, step_bits) for j in range(dimensions)]
    sums_base = spread_base + ceil(dimensions * step_bits / 8) + 2
    assert unpack('<H', guide[sums_base - 2:sums_base])[0] == 1
    residual_widths = [width.bit_length() for width in spread]
    residual_bits = sum(residual_widths)
    leader, best = 0, None
    for i in range(rows):
        offset, residual_offset, score = i * row_bits, i * residual_bits, 0
        for x, width, residual_width in zip(query, widths, residual_widths):
            coefficient = (get_bits(guide, quotient_base, offset, width) << step_bits)
            coefficient += get_bits(guide, sums_base, residual_offset, residual_width)
            offset += width
            residual_offset += residual_width
            score += coefficient * x
        if best is None or score > best:
            leader, best = i, score
    counters['coarse_terms'] += rows * dimensions
    counters['route_calls'] += 1
    counters['singleton_routes'] += 1
    counters['candidate_count'] += 1
    counters['max_candidates'] = 1
    size = 2 * dimensions * dimensions
    return leader, source.read('payload', payload_base + leader * size, size)

texts = [''] + [f'Calculate {i * 37 - 2000} times {i % 19 - 9}, then add {i * i}.' for i in range(128)]
configurations = [('exact_centered', 0, False, 0)]
for step_bits in (4, 8, 12):
    for rotate in (False, True):
        configurations.append(('exact_split', step_bits, rotate, 1))
        configurations.append(('quotient', step_bits, rotate, 0))
        for block_size in (12, 4, 2, 1):
            configurations.append(('sums', step_bits, rotate, block_size))
        for block_size in (12, 4, 2):
            configurations.append(('moments', step_bits, rotate, block_size))
report = []
with TemporaryDirectory(prefix='cassette-remainder-') as scratch:
    for case_index, name in enumerate(('independent', 'shared_remainders', 'near_ties', 'duplicate_rows')):
        data, embeddings, models, locations = make_source(name, Random(SEED + case_index))
        source_id = sha256(data).digest()
        source_path = Path(scratch) / (name + '.bin')
        source_path.write_bytes(data)
        reference = []
        for text in texts:
            query = tuple(clip(sum(embeddings[token][j] for token in text.encode('utf-8'))) for j in range(DIMENSIONS))
            steps = []
            for gate, payloads in models:
                winner = max(range(ROWS), key=lambda i: (sum(a * x for a, x in zip(gate[i], query)), -i))
                query = ordinary_product(payloads[winner], query)
                steps.append((winner, payloads[winner], query))
            reference.append(steps)
        for method, step_bits, rotate, block_size in configurations:
            if method in ('sums', 'moments', 'exact_split'):
                compiler = compile_moments if method == 'moments' else compile_sums
                guides = [compiler(gate, step_bits, rotate, block_size, *location, source_id)
                          for (gate, _), location in zip(models, locations)]
                interpreter = {'moments': moment_route, 'sums': sum_route, 'exact_split': exact_split_route}[method]
            else:
                guides = [compile_guide(gate, step_bits, rotate, *location, source_id)
                          for (gate, _), location in zip(models, locations)]
                interpreter = exact_centered_route if method == 'exact_centered' else route
            counters, output_hash = Counter(), sha256()
            with source_path.open('rb') as stream:
                source = PageReader(stream, source_id)
                for text, expected in zip(texts, reference):
                    query = initial_state(text, source)
                    for guide, (want_index, want_payload, want_query) in zip(guides, expected):
                        source.route_pages.clear()
                        index, payload = interpreter(guide, query, source, counters)
                        source.gate_pages_across_routes += len(source.route_pages)
                        assert index == want_index and payload == want_payload
                        query = ordinary_product(payload, query)
                        assert query == want_query
                        output_hash.update(pack('<H', index) + bytes(x + 31 for x in query))
            report.append(dict(case=name, method=method, step_bits=step_bits,
                               phase='width_optimal' if rotate else 'zero', block_size=block_size,
                               guide_bytes=sum(map(len, guides)), source_sha256=source_id.hex(),
                               source_bytes=len(data), full_gate_bytes=LAYERS * ROWS * DIMENSIONS * 2,
                               read_bytes=dict(source.bytes), requests=dict(source.requests),
                               rounded_bytes_per_request=dict(source.rounded),
                               unique_gate_page_bytes_per_route=4096 * source.gate_pages_across_routes,
                               calculations=dict(counters), output_sha256=output_hash.hexdigest()))
print(json.dumps(dict(seed=SEED, rows=ROWS, dimensions=DIMENSIONS, layers=LAYERS,
                     input_count=len(texts), configuration_count=len(configurations),
                     scope='synthetic source; packed-byte accounting; exact original payloads; no hardware timing',
                     results=report), indent=2))
```
