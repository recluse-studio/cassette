# Let original reads strengthen the remaining comparisons

This experiment strengthens the established comparator for MATHS section 12. The earlier
[sum experiment](remainder-sum-experiment.md) reads every row that survives its initial
bounds. An original row can also supply information that eliminates later reads. This
note derives that update without storing the common column vector discarded by argmax
compression. It uses the same packed representation and returns the same original payload.

## 1. A shared unknown can be bounded after a read

Write an original gate score as \(s_i=H+f_i\), where \(H=h\cdot x\) is common to
all rows and the guide proves \(l_i\le f_i\le u_i\). Reading original row \(i\)
gives the exact \(s_i\), hence

\[
 H\le s_i-l_i.
\]

Keep \(H^+=\min_{i\in F}(s_i-l_i)\) for the already fetched rows \(F\), and their
greatest exact score \(B\), with its least-index winner \(b\). For any remaining row,

\[
 s_j\le u_j+H^+.
\]

Exclude \(j\) when that upper bound is below \(B\), or equal to \(B\) with \(j>b\).
After each read, update \(H^+\) and \((B,b)\). No approximation enters the final
score. All arithmetic in this experiment is exact integer arithmetic.

Choose the initial anchor \(k\) with greatest lower bound, breaking ties by least index.
Delay its source read until another initially eligible row occurs. A singleton therefore
still needs no source gate read. After the anchor is read, the adaptive threshold
\(B-H^+\) is at least \(l_k\), since \(B\ge s_k\) and \(H^+\le s_k-l_k\).
Consequently this fixed-order policy never fetches a row that the original candidate-set
policy excluded. Equality ties preserve that statement: when the threshold equals \(l_k\),
the current exact winner either remains \(k\) or has the same source score and a smaller
index; a larger-score winner would make the threshold strictly greater.

This uses the familiar branch-and-bound principle of refining an incumbent. It is a
stronger comparator, not evidence that exact candidate refinement was invented here.
Row order remains the source order. A different order could improve reads and would
need its sorting, index storage, or repeated scans charged separately.

The added running common bound is one signed scalar, not a source-dependent vector.
Its encoded width must cover \(|s_i-l_i|\); the source score, quotient bound, residual
bound, and query magnitude determine that range. An arbitrary-precision integer is
charged by those bits and its arithmetic scratch, not counted as a fixed free word.

## 2. Compute row-sum bounds from shared prefixes

Sort query coordinates increasingly once. For capacities \(w_j\), store prefix
capacities \(C_r=\sum_{a<r}w_{j_a}\) and weighted prefixes
\(Z_r=\sum_{a<r}w_{j_a}x_{j_a}\). For a residual total \(t>0\), locate the first
\(r\) with \(C_r\ge t\). The minimum residual score is

\[
 L(t)=Z_{r-1}+(t-C_{r-1})x_{j_{r-1}},\qquad L(0)=0.
\]

The maximum is \(Z_d-L(W-t)\), by replacing each residual \(e_j\) with \(w_j-e_j\).
Binary search costs \(O(\log d)\) per support evaluation after shared
\(O(d\log d)\) preparation. Quotient scoring still costs \(O(md)\). The earlier
linear greedy supports remain correct but are not the strongest time comparator.

The two prefix arrays contain \(2(d+1)\) integers, and the query order contains \(d\)
indices. Prefix capacities fit \(\lceil\log_2(W+1)\rceil\) bits; signed weighted
prefixes fit one sign bit plus \(\lceil\log_2(WX+1)\rceil\) bits for
\(X=\max_j|x_j|\). Query values, decoded widths, source buffers, Python object overhead,
and scalar work remain additional memory. These formulas describe value widths; the
Python experiment does not claim bit-packed interpreter memory or measured peak RAM.

## 3. Original source experiment

Run the Python fence from the repository root. It reuses the original generated source,
source reader, packed guide, and ordinary payload operation. Each configuration executes
the same dependent three-layer paths as its reference. The compact source scores are used
only to identify a region; original payload bytes supply the normal calculation.

```python
from pathlib import Path
base_text = Path('research/representation/remainder-sum-experiment.md').read_text()
base_code = base_text.split('```python\n')[1].split('\n```')[0].split("\ntexts = ['']")[0]
exec(compile(base_code, 'remainder-sum-experiment.md', 'exec'))
from bisect import bisect_left

def prefix_route(guide, query, source, counters, adaptive):
    magic, rows, dimensions, step_bits, gate_base, payload_base, identity = unpack(HEADER, guide[:57])
    assert magic == b'PQR1' and identity == source.source_id
    widths = guide[57:57 + dimensions]
    row_bits, quotient_base = sum(widths), 57 + dimensions
    spread_base = quotient_base + ceil(rows * row_bits / 8)
    spread = [get_bits(guide, spread_base, j * step_bits, step_bits) for j in range(dimensions)]
    block_base = spread_base + ceil(dimensions * step_bits / 8)
    assert unpack('<H', guide[block_base:block_base + 2])[0] == dimensions
    sums_base, total_width = block_base + 2, sum(spread).bit_length()
    order = sorted(range(dimensions), key=lambda j: (query[j], j))
    capacity, weighted = [0], [0]
    for j in order:
        capacity.append(capacity[-1] + spread[j])
        weighted.append(weighted[-1] + spread[j] * query[j])
    counters['query_sort_calls'] += 1
    counters['prefix_coordinates'] += dimensions
    counters['max_prefix_integer_count'] = max(counters['max_prefix_integer_count'], 2 * (dimensions + 1))

    def support(total):
        counters['support_queries'] += 1
        if total == 0:
            return 0
        boundary = bisect_left(capacity, total)
        return weighted[boundary - 1] + (total - capacity[boundary - 1]) * query[order[boundary - 1]]

    def interval(i):
        score, offset = 0, i * row_bits
        for x, width in zip(query, widths):
            score += x * get_bits(guide, quotient_base, offset, width)
            offset += width
        counters['coarse_terms'] += dimensions
        score <<= step_bits
        total = get_bits(guide, sums_base, i * total_width, total_width)
        return score + support(total), score + weighted[-1] - support(capacity[-1] - total)

    leader, lower = 0, interval(0)[0]
    for i in range(1, rows):
        value = interval(i)[0]
        if value > lower:
            leader, lower = i, value

    def exact_score(i):
        raw = source.read('gate', gate_base + i * dimensions * 2, dimensions * 2)
        counters['exact_gate_terms'] += dimensions
        return sum(a * x for a, x in zip(unpack('<' + 'h' * dimensions, raw), query))

    winner, best, common_upper = leader, None, None
    candidate_count = 1
    for i in range(rows):
        if i == leader:
            continue
        lo, hi = interval(i)
        if hi < lower or (hi == lower and i > leader):
            continue
        candidate_count += 1
        if best is None:
            best = exact_score(leader)
            common_upper = best - lower
        if adaptive and (hi + common_upper < best or (hi + common_upper == best and i > winner)):
            counters['adaptive_skips'] += 1
            continue
        value = exact_score(i)
        if value > best or (value == best and i < winner):
            winner, best = i, value
        common_upper = min(common_upper, value - lo)
    counters['route_calls'] += 1
    counters['candidate_count'] += candidate_count
    counters['singleton_routes'] += candidate_count == 1
    size = 2 * dimensions * dimensions
    return winner, source.read('payload', payload_base + winner * size, size)

texts = [''] + [f'Calculate {i * 37 - 2000} times {i % 19 - 9}, then add {i * i}.' for i in range(128)]
report = []
with TemporaryDirectory(prefix='cassette-adaptive-') as scratch:
    for case_index, name in enumerate(('independent', 'shared_remainders', 'near_ties', 'duplicate_rows')):
        data, embeddings, models, locations = make_source(name, Random(SEED + case_index))
        source_id = sha256(data).digest()
        source_path = Path(scratch) / (name + '.bin')
        source_path.write_bytes(data)
        references = []
        for text in texts:
            query = tuple(clip(sum(embeddings[token][j] for token in text.encode('utf-8'))) for j in range(DIMENSIONS))
            steps = []
            for gate, payloads in models:
                winner = max(range(ROWS), key=lambda i: (sum(a * x for a, x in zip(gate[i], query)), -i))
                query = ordinary_product(payloads[winner], query)
                steps.append((winner, payloads[winner], query))
            references.append(steps)
        for step_bits in (4, 8, 12):
            guides = [compile_sums(gate, step_bits, True, DIMENSIONS, *location, source_id)
                      for (gate, _), location in zip(models, locations)]
            for adaptive in (False, True):
                counters, output_hash = Counter(), sha256()
                with source_path.open('rb') as stream:
                    source = PageReader(stream, source_id)
                    for text, steps in zip(texts, references):
                        query = initial_state(text, source)
                        for guide, (want_index, want_payload, want_query) in zip(guides, steps):
                            source.route_pages.clear()
                            index, payload = prefix_route(guide, query, source, counters, adaptive)
                            source.gate_pages_across_routes += len(source.route_pages)
                            assert index == want_index and payload == want_payload
                            query = ordinary_product(payload, query)
                            assert query == want_query
                            output_hash.update(pack('<H', index) + bytes(x + 31 for x in query))
                report.append(dict(case=name, step_bits=step_bits, adaptive=adaptive,
                                   guide_bytes=sum(map(len, guides)), read_bytes=dict(source.bytes),
                                   requests=dict(source.requests), calculations=dict(counters),
                                   unique_gate_page_bytes_per_route=4096 * source.gate_pages_across_routes,
                                   source_sha256=source_id.hex(), output_sha256=output_hash.hexdigest()))
for before, after in zip(report[::2], report[1::2]):
    assert after['read_bytes'].get('gate', 0) <= before['read_bytes'].get('gate', 0)
    assert before['output_sha256'] == after['output_sha256']
print(json.dumps(dict(seed=SEED, rows=ROWS, dimensions=DIMENSIONS, layers=LAYERS,
                     input_count=len(texts), configurations=len(report),
                     scope='generated integer source; fixed row order; no timing or peak-RAM measurement',
                     results=report), indent=2))
```

The source identity and immutable-fixture assumption are inherited from the base
experiment. These replays do not add durable source verification. Reference source and
reference outputs remain test-only objects; they are not supplied to the interpreter.

## 4. Comparator consequence

The [saved run](adaptive-source-results.json) passes 9,288 complete routing operations
across 24 configurations. Every original payload and dependent output agrees with the
full-source reference. Both policies have identical guide bytes. The strongest reduction
in this finite set occurs for independent source rows at step exponent 12: logical gate
bytes fall from 209,352 to 163,248. The modeled coalesced 4,096-byte page total changes
only from 2,060,288 to 2,052,096 bytes. Logical-byte savings therefore do not imply the
same physical-transfer saving. At step exponent 4 that source needs 336 gate bytes under
either policy. Near-tie sources still require 436,320 gate bytes after refinement, versus
442,152 before it; the representation remains weak there.

Prior fixed-candidate read counts remain accurate for their declared policy. They do not
establish superiority over this stronger policy, different read orders, or fully optimized
exact inner-product search. A new representation must face these stronger comparisons.
The primary [FEXIPRO paper](https://www4.comp.polyu.edu.hk/~csmlyiu/conf/SIGMOD17_fexipro.pdf)
already combines bounded filters with exact refinement; that broad mechanism is established.

## 5. Exhaustive bound-update check

This separate finite check covers every three-row assignment of lower bound, actual
value, and upper bound in \(\{0,1,2\}\), three common shifts, and all six read orders.
It passes 18,000 cases; 1,755 use fewer original rows than the fixed-candidate policy.
The winner is always exact, including ties. It checks the update theorem rather than
physical reads, which the preceding experiment already exercises.

```python
from itertools import product, permutations
states_per_row = [(lo, value, hi) for lo in range(3) for hi in range(lo, 3)
                  for value in range(lo, hi + 1)]
checks = strict = 0
for states in product(states_per_row, repeat=3):
    leader = max(range(3), key=lambda i: (states[i][0], -i))
    floor = states[leader][0]
    initial = {i for i in range(3) if i == leader or states[i][2] > floor
               or (states[i][2] == floor and i < leader)}
    for common in (-3, 0, 3):
        scores = [common + state[1] for state in states]
        expected = max(range(3), key=lambda i: (scores[i], -i))
        for order in permutations(range(3)):
            winner, best, common_upper, read = leader, None, None, set()
            for i in order:
                if i == leader or i not in initial:
                    continue
                if best is None:
                    best, common_upper = scores[leader], scores[leader] - floor
                    read.add(leader)
                upper = states[i][2] + common_upper
                if upper < best or (upper == best and i > winner):
                    continue
                read.add(i)
                if scores[i] > best or (scores[i] == best and i < winner):
                    winner, best = i, scores[i]
                common_upper = min(common_upper, scores[i] - states[i][0])
            fixed_reads = initial if len(initial) > 1 else set()
            assert winner == expected and read <= fixed_reads
            checks += 1
            strict += len(read) < len(fixed_reads)
assert (checks, strict) == (18000, 1755)
print(dict(exact_interval_cases=checks, strictly_fewer_read_cases=strict))
```

## 6. Independent audit

I reviewed this construction as a stronger established comparator for exact
filter-and-refine interpretation. Its common-free update is sound:
from \(s_i=H+f_i\) and \(f_i\ge l_i\), a fetched original row gives
\(H\le s_i-l_i\). Hence \(H^+=\min(s_i-l_i)\) gives every unfetched row the
safe upper score \(u_j+H^+\). The exclusion rule is tie-correct because equality
can eliminate only an index larger than the current exact least-index winner.

The fixed source-order policy reads a subset of its initial eligible set. Once
it reads the anchor, \(B-H^+\ge l_k\), where \(k\) has the greatest initial
lower bound. Later tightening can only raise that threshold. A row excluded by
the initial lower/upper rule therefore cannot become eligible. If equality holds,
the initial rule already preserves only indices that can beat the anchor under
the least-index convention. A singleton initial set reads no original gate.

The sorted-prefix support formula is also correct for the stated row-total box:
it fills the least query coordinates to minimize the residual product, and uses
the capacity complement to maximize it. The source identity check in the fence
binds the packed guide to the generated immutable source. Guide scores choose
which original gate records to fetch; the fetched records choose the winner; the
fetched original payload supplies the ordinary operation. No guide value reaches
the payload calculation.

I checked the saved JSON rather than rerunning the dependent experiment. It has
24 configurations and \(24\cdot387=9{,}288\) route operations. For each
before/after pair, guide bytes and output hashes match, and adaptive logical
gate bytes do not increase. Selected rows are:

| Source and step | Fixed logical gate bytes | Adaptive logical gate bytes | Fixed / adaptive modeled page bytes |
|---|---:|---:|---:|
| independent, 12 | 209,352 | 163,248 | 2,060,288 / 2,052,096 |
| shared remainders, 12 | 439,656 | 437,856 | 2,097,152 / 2,097,152 |
| near ties, 4 | 442,152 | 436,320 | 2,097,152 / 2,097,152 |
| duplicate rows, all steps | 0 | 0 | 0 / 0 |

The separate abstract-order fence has \(10^3\cdot3\cdot6=18{,}000\) cases and
asserts exact winners and read-set inclusion; its stated 1,755 strict reductions
were not rerun in this audit. The adaptive method is an established
filter-and-refine improvement and the relevant baseline for read counts. A
pair-certificate method can strengthen comparisons before any original read;
this method instead strengthens later comparisons after an original read.
