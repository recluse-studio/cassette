# Exact relevance in a dense layer with ReLU

This experiment supplies a second ordinary operation for MATHS section 12. It derives
relevance inside a dense layer rather than assuming an argmax gate selects one payload.
The source operation is the exact-integer layer

\[
 y=D\operatorname{ReLU}(Ux),\qquad \operatorname{ReLU}(a)=\max(0,a).
\]

Both source matrices remain external. A compact representation of \(U\) supplies an upper
bound for each original dot product. If the bound is nonpositive, that intermediate value
is exactly zero; its original \(U\) row and corresponding \(D\) column need not be read.
Otherwise the interpreter reads the original \(U\) row and computes the exact activation.
If the activation is positive, it reads the original \(D\) column and performs the normal
product and accumulation in the original hidden-index order. It never substitutes a
compressed score for an activation that contributes to the output.

## Representation and proof

Use \(U_{ij}=h_j+\Delta Q_{ij}+e_{ij}\), with the quotient, remainder capacities, block
sums, and optional squared sums from the earlier construction. Argmax routing could drop
\(h\), because its contribution was common to all scores. ReLU compares scores with zero,
so the representation must retain \(h\) and compute \(hx\). This experiment stores each
\(h_j\) in four signed bytes; that cost is part of the guide.

If the remainder support upper bound is \(b_i(x)\), define

\[
 u_i(x)=hx+\Delta Q_ix+b_i(x).
\]

The source activation score satisfies \(U_ix\le u_i\). Therefore \(u_i\le0\) proves
that the ReLU value is zero. Every row not so proved is read and resolved by its original
weights. Every nonzero activation uses the original corresponding down-projection column.
This proves equality with the dense source operation, including threshold ties. The proof
does not require sparsity or low rank in either source matrix. Savings require the query
to produce inactive intermediates that the representation can certify.

The declared operation uses exact integers. Replacing a floating-point layer by that
operation would change its contract; a separate outward-rounding proof is required for
its original kernel. ReLU has exact zero regions. Other nonlinearities need their own
relevance proof and cannot inherit this omission rule by analogy.

## Memory, transfer, and arithmetic

The resident model information is the guide, including \(h\). The interpreter also holds
the current input, output accumulators, block sorting/support scratch, and one source row
or column buffer. The implementation releases a row's decoded weights before reading its
down-projection column. A byte-level packed implementation must count their decoding and
integer accumulator widths; the Python process footprint is larger than these encoded
arrays. All layers' guides remain resident in the fixture and their encoded bytes add.
The returned active-index list is a verification trace. This harness allocates up to
\(m\lceil\log_2m\rceil\) encoded trace bits, plus its Python container overhead. A
packed interpreter that omits this test-only output need not allocate the trace; this
statement is not evidence that the current Python harness lacks it.

The source stores \(U\) by rows and \(D\) by columns, both lossless orderings. These fixed
strides require no resident pointer per coefficient. The reference applies identical
weights and the same hidden-index accumulation order, \(i=0,1,\ldots,m-1\).
Page rounding and integrity costs still add
to the logical byte counts. Neither a zero read nor a time improvement is assumed.

## Reproducible complete calculation

Run the Python fence from the repository root. It imports only earlier research-fence
definitions into a temporary interpreter, creates local scratch source files, and removes
them at the end. Each available state comes from an original embedding table or the
preceding exact layer. The fixture uses dense generated integer matrices, not a trained
language model. It verifies every fetched byte and final state against the full source.

```python
from pathlib import Path
prior = Path('research/representation/remainder-sum-experiment.md').read_text()
definitions = prior.split('```python\n')[1].split('\n```')[0].rsplit("\ntexts = ['']", 1)[0]
exec(compile(definitions, 'remainder-sum-experiment.md', 'exec'))

def compile_relu(matrix, step_bits, use_moments, block_size, gate_base, down_base, source_id):
    compiler = compile_moments if use_moments else compile_sums
    guide = compiler(matrix, step_bits, True, block_size, gate_base, down_base, source_id)
    rows, dimensions = len(matrix), len(matrix[0])
    widths = guide[57:57 + dimensions]
    row_bits, base = sum(widths), 57 + dimensions
    common = []
    column_offset = 0
    for j, width in enumerate(widths):
        common.append(min(matrix[i][j] - (get_bits(guide, base, i * row_bits + column_offset, width) << step_bits)
                          for i in range(rows)))
        column_offset += width
    return guide + pack('<' + 'i' * dimensions, *common)

def relu_layer(guide, query, source, counters, use_moments):
    magic, rows, dimensions, step_bits, gate_base, down_base, identity = unpack(HEADER, guide[:57])
    assert magic == b'PQR1' and identity == source.source_id and len(query) == dimensions
    widths = guide[57:57 + dimensions]
    row_bits, quotient_base = sum(widths), 57 + dimensions
    spread_base = quotient_base + ceil(rows * row_bits / 8)
    spread = [get_bits(guide, spread_base, j * step_bits, step_bits) for j in range(dimensions)]
    size_offset = spread_base + ceil(dimensions * step_bits / 8)
    block_size = unpack('<H', guide[size_offset:size_offset + 2])[0]
    blocks = [range(start, min(dimensions, start + block_size)) for start in range(0, dimensions, block_size)]
    orders = [sorted(block, key=lambda j: (-query[j], j)) for block in blocks]
    sum_widths = [sum(spread[j] for j in block).bit_length() for block in blocks]
    sum_row_bits, sums_base = sum(sum_widths), size_offset + 2
    square_widths = [sum(spread[j] ** 2 for j in block).bit_length() for block in blocks] if use_moments else []
    square_row_bits = sum(square_widths)
    squares_base = sums_base + ceil(rows * sum_row_bits / 8)
    common_base = squares_base + ceil(rows * square_row_bits / 8)
    assert len(guide) == common_base + 4 * dimensions
    common = unpack('<' + 'i' * dimensions, guide[common_base:])
    common_score = sum(a * x for a, x in zip(common, query))
    query_sums = [sum(query[j] for j in block) for block in blocks]
    query_squares = [sum(query[j] ** 2 for j in block) for block in blocks]
    output = [0] * dimensions
    active = []
    for i in range(rows):
        offset, score = i * row_bits, 0
        for x, width in zip(query, widths):
            score += x * get_bits(guide, quotient_base, offset, width)
            offset += width
        upper = common_score + (score << step_bits)
        sum_offset, square_offset = i * sum_row_bits, i * square_row_bits
        for b, (order, width) in enumerate(zip(orders, sum_widths)):
            total = get_bits(guide, sums_base, sum_offset, width)
            sum_offset += width
            left, bound = total, 0
            for j in order:
                if left == 0:
                    break
                take = min(left, spread[j])
                bound += take * query[j]
                left -= take
                counters['support_coordinates'] += 1
            assert left == 0
            if use_moments:
                square = get_bits(guide, squares_base, square_offset, square_widths[b])
                square_offset += square_widths[b]
                n, query_sum = len(order), query_sums[b]
                discriminant = (n * square - total * total) * (n * query_squares[b] - query_sum * query_sum)
                bound = min(bound, (total * query_sum + isqrt(discriminant)) // n)
                counters['integer_square_roots'] += 1
            upper += bound
        counters['coarse_terms'] += dimensions
        counters['hidden_rows'] += 1
        if upper <= 0:
            counters['certified_inactive'] += 1
            continue
        raw = source.read('up', gate_base + i * dimensions * 2, dimensions * 2)
        score = sum(a * x for a, x in zip(unpack('<' + 'h' * dimensions, raw), query))
        counters['source_up_terms'] += dimensions
        del raw
        if score <= 0:
            counters['refined_inactive'] += 1
            continue
        raw = source.read('down', down_base + i * dimensions * 2, dimensions * 2)
        column = unpack('<' + 'h' * dimensions, raw)
        output = [value + coefficient * score for value, coefficient in zip(output, column)]
        counters['source_down_terms'] += dimensions
        active.append(i)
        del raw, column
    counters['layers'] += 1
    return tuple(map(clip, output)), tuple(active)

def streamed_relu_layer(header, query, source, counters, use_moments=False):
    magic, rows, dimensions, step_bits, up_base, down_base, identity = unpack(HEADER, header)
    assert identity == source.source_id
    output, active = [0] * dimensions, []
    counters['layers'] += 1
    counters['hidden_rows'] += rows
    if not any(query):
        counters['certified_inactive'] += rows
        return tuple(output), ()
    for i in range(rows):
        raw = source.read('up', up_base + i * dimensions * 2, dimensions * 2)
        score = sum(a * x for a, x in zip(unpack('<' + 'h' * dimensions, raw), query))
        counters['source_up_terms'] += dimensions
        del raw
        if score <= 0:
            counters['refined_inactive'] += 1
            continue
        raw = source.read('down', down_base + i * dimensions * 2, dimensions * 2)
        column = unpack('<' + 'h' * dimensions, raw)
        output = [value + coefficient * score for value, coefficient in zip(output, column)]
        counters['source_down_terms'] += dimensions
        active.append(i)
        del raw, column
    return tuple(map(clip, output)), tuple(active)

class VerifiedReader(PageReader):
    def __init__(self, stream, source_id, expected):
        super().__init__(stream, source_id)
        self.expected = expected

    def read(self, kind, offset, count):
        raw = super().read(kind, offset, count)
        assert raw == self.expected[offset:offset + count]
        return raw

generator = Random(SEED + 20)
embeddings = [[generator.randrange(-7, 8) for _ in range(DIMENSIONS)] for _ in range(256)]
data = bytearray(pack('<' + 'h' * (256 * DIMENSIONS), *(v for row in embeddings for v in row)))
models, locations = [], []
for layer in range(LAYERS):
    up = [[generator.randrange(-8192, 8192) for _ in range(DIMENSIONS)] for _ in range(ROWS)]
    down = [[generator.randrange(-8, 9) for _ in range(DIMENSIONS)] for _ in range(ROWS)]
    up_base = len(data)
    data.extend(pack('<' + 'h' * (ROWS * DIMENSIONS), *(v for row in up for v in row)))
    down_base = len(data)
    data.extend(pack('<' + 'h' * (ROWS * DIMENSIONS), *(v for column in down for v in column)))
    models.append((up, down))
    locations.append((up_base, down_base))
data, report = bytes(data), []
source_id = sha256(data).digest()
texts = [''] + [f'Calculate {i * 37 - 2000} times {i % 19 - 9}, then add {i * i}.' for i in range(128)]
reference = []
for text in texts:
    query = tuple(clip(sum(embeddings[token][j] for token in text.encode('utf-8'))) for j in range(DIMENSIONS))
    steps = []
    for up, down in models:
        scores = [max(0, sum(a * x for a, x in zip(row, query))) for row in up]
        query = tuple(clip(sum(down[i][j] * scores[i] for i in range(ROWS))) for j in range(DIMENSIONS))
        steps.append((query, tuple(i for i, score in enumerate(scores) if score > 0)))
    reference.append(steps)
with TemporaryDirectory(prefix='cassette-relu-') as scratch:
    source_path = Path(scratch) / 'dense.bin'
    source_path.write_bytes(data)
    configurations = [('streamed', 0, False)] + [('represented', bits, moments) for bits in (4, 8, 12) for moments in (False, True)]
    for method, step_bits, use_moments in configurations:
            if method == 'streamed':
                guides = [pack(HEADER, b'PQR1', ROWS, DIMENSIONS, 0, *location, source_id) for location in locations]
                interpreter = streamed_relu_layer
            else:
                guides = [compile_relu(up, step_bits, use_moments, DIMENSIONS, *location, source_id)
                          for (up, _), location in zip(models, locations)]
                interpreter = relu_layer
            counters, output_hash = Counter(), sha256()
            with source_path.open('rb') as stream:
                source = VerifiedReader(stream, source_id, data)
                for text, expected in zip(texts, reference):
                    query = initial_state(text, source)
                    for guide, want in zip(guides, expected):
                        query, active = interpreter(guide, query, source, counters, use_moments)
                        assert (query, active) == want
                        output_hash.update(bytes(x + 31 for x in query) + bytes(active))
            report.append(dict(method=method, step_bits=step_bits, moments=use_moments,
                               guide_bytes=sum(map(len, guides)), source_model_bytes=2 * LAYERS * ROWS * DIMENSIONS * 2,
                               read_bytes=dict(source.bytes), requests=dict(source.requests),
                               rounded_bytes_per_request=dict(source.rounded), calculations=dict(counters),
                               output_sha256=output_hash.hexdigest()))
print(json.dumps(dict(seed=SEED + 20, source_sha256=source_id.hex(), inputs=len(texts),
                     rows=ROWS, dimensions=DIMENSIONS, layers=LAYERS,
                     scope='generated dense integer ReLU; original source bytes; no trained-model or drive-speed claim',
                     results=report), indent=2))
```

The verifier keeps the full reference source outside the candidate interpreter and checks
each returned read. That storage is test-oracle memory, not evidence of a measured small
Python process. A production reader would verify source identity through the existing
store contract rather than retain a second source copy. The packed-memory claim describes
the candidate's information requirements; this harness proves its calculations and reads.
