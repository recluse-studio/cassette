# Executable improvement-hypothesis experiment

This standard-library research fence executes the frozen protocol in
[improvement-hypothesis-protocol.md](improvement-hypothesis-protocol.md).
Run from the repository root. It writes generated JSON evidence beside this file;
temporary source files are removed when the run ends. It imports no product code.

```python
# Improvement experiment; depends on the protocol and the research fences loaded below.
from bisect import bisect_left
from collections import Counter
import gc
from hashlib import sha256
from heapq import heappop, heappush
import json
from math import comb
from os import pread
from pathlib import Path
import platform
from random import Random
from statistics import median
from struct import pack, unpack
import sys
from tempfile import TemporaryDirectory
from time import perf_counter_ns
import tracemalloc

ROOT = Path('research/representation')
DEFINITION_HASHES = {}


def load_definitions(name, end_marker):
    text = (ROOT / name).read_text()
    code = text.split('```python\n', 1)[1].split(end_marker, 1)[0]
    DEFINITION_HASHES[name] = sha256(code.encode()).hexdigest()
    namespace = {}
    exec(compile(code, name, 'exec'), namespace)
    return namespace


joint = load_definitions('joint-scale-experiment.md', '\ndef run_case(')
joint['QUERY_COUNT'] = 9
pair = load_definitions('full-pair-polymatroid.md', '\nSEED = ')
reference = load_definitions('full-pair-flow-comparison.md', '\nSEED = ')
FullPairSupport = pair['FullPairSupport']
get_bits, pack_bits = joint['get_bits'], joint['pack_bits']
HEADER = joint['HEADER']
METHODS = ('row_sums', 'exact_centered', 'stream', 'pair_total', 'pair_dual', 'full_pair')
CANDIDATES = ('pair_total', 'pair_dual', 'full_pair')
COMPARATORS = ('row_sums', 'exact_centered')
ORDER_RNG = Random(2026092903)


def shortest_path_flow(widths, totals, columns, query):
    """MATHS 12.9: exact integral support, using all margins and capacities."""
    m, d = len(totals), len(widths)
    source, row_base, column_base, sink = 0, 1, 1 + m, 1 + m + d
    graph = [[] for _ in range(sink + 1)]

    def add_edge(left, right, capacity, cost):
        graph[left].append([right, len(graph[right]), capacity, cost])
        graph[right].append([left, len(graph[left]) - 1, 0, -cost])

    for i, total in enumerate(totals):
        add_edge(source, row_base + i, total, 0)
        for j, width in enumerate(widths):
            cost = -query[j] if i == 0 else query[j] if i == 1 else 0
            add_edge(row_base + i, column_base + j, width, cost)
    for j, total in enumerate(columns):
        add_edge(column_base + j, sink, total, 0)
    # A virtual zero-cost source reaches every vertex for initial feasible potentials.
    potential = [0] * len(graph)
    for _ in range(len(graph) - 1):
        changed = False
        for left, edges in enumerate(graph):
            for right, _, capacity, cost in edges:
                if capacity and potential[right] > potential[left] + cost:
                    potential[right] = potential[left] + cost
                    changed = True
        if not changed:
            break
    sent = value = 0
    required = sum(totals)
    while sent < required:
        distance, parent = [None] * len(graph), [None] * len(graph)
        distance[source] = 0
        heap = [(0, source)]
        while heap:
            dist, left = heappop(heap)
            if distance[left] != dist:
                continue
            for index, (right, _, capacity, cost) in enumerate(graph[left]):
                if not capacity:
                    continue
                reduced = cost + potential[left] - potential[right]
                assert reduced >= 0
                proposed = dist + reduced
                if distance[right] is None or proposed < distance[right]:
                    distance[right], parent[right] = proposed, (left, index)
                    heappush(heap, (proposed, right))
        assert distance[sink] is not None
        farthest = max(value for value in distance if value is not None)
        for vertex, dist in enumerate(distance):
            potential[vertex] += farthest if dist is None else dist
        amount, vertex = required - sent, sink
        while vertex != source:
            left, index = parent[vertex]
            amount = min(amount, graph[left][index][2])
            vertex = left
        vertex = sink
        while vertex != source:
            left, index = parent[vertex]
            edge = graph[left][index]
            edge[2] -= amount
            graph[vertex][edge[1]][2] += amount
            value += amount * edge[3]
            vertex = left
        sent += amount
    return -value


def support_call(method, packed):
    resident = memoryview(packed).tobytes()
    m, d = unpack('<HH', resident[:4])
    values = unpack('<' + 'q' * (2 * d + m + d), resident[4:])
    w, t, u, x = values[:d], values[d:d + m], values[d + m:d + m + d], values[d + m + d:]
    if method == 'full_pair':
        return FullPairSupport(w, u, t[2:], t[0], t[1]).exact(x)
    return shortest_path_flow(w, t, u, x)


def traced_peak(call):
    gc.collect()
    tracemalloc.start()
    try:
        result = call()
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return result, peak


def time_methods(calls, expected):
    samples = {name: [] for name in calls}
    for _ in range(3):
        order = list(calls)
        ORDER_RNG.shuffle(order)
        for name in order:
            gc.collect()
            started = perf_counter_ns()
            result = calls[name]()
            elapsed = perf_counter_ns() - started
            assert result == expected[name]
            samples[name].append(elapsed)
    return samples


def support_experiment():
    rng, records = Random(2026092901), []
    for case in range(32):
        m, d = rng.choice(((8, 8), (16, 16), (32, 32)))
        family = rng.choice(('independent', 'mostly_zero', 'boundary'))
        w = tuple(rng.randrange(16) for _ in range(d))
        rows = []
        for _ in range(m):
            rows.append(tuple(rng.randrange(width + 1) if family == 'independent' else
                              (rng.randrange(width + 1) if rng.randrange(8) == 0 else 0)
                              if family == 'mostly_zero' else rng.choice((0, width)) for width in w))
        t, u = tuple(map(sum, rows)), tuple(map(sum, zip(*rows)))
        x = tuple(rng.randrange(-31, 32) for _ in range(d))
        expected = reference['max_cost_transport'](w, t, u, x)[0]
        packed = pack('<HH', m, d) + pack('<' + 'q' * (3 * d + m), *(w + t + u + x))
        del rows
        calls = {name: (lambda name=name: support_call(name, packed)) for name in ('full_pair', 'flow')}
        facts = {}
        for name, call in calls.items():
            value, peak = traced_peak(call)
            assert value == expected
            facts[name] = dict(peak_bytes=peak)
        samples = time_methods(calls, {name: expected for name in calls})
        for name in calls:
            facts[name].update(time_ns=median(samples[name]), timing_samples_ns=samples[name])
        records.append(dict(case=case, rows=m, dimensions=d, family=family, support=expected,
                            packed_bytes=len(packed), methods=facts))
    return records


class SourceReader:
    def __init__(self, fd, source_id):
        self.fd, self.source_id = fd, source_id
        self.gate_bytes = self.gate_requests = self.payload_bytes = self.payload_requests = 0

    def read(self, kind, offset, count):
        raw = pread(self.fd, count, offset)
        assert len(raw) == count
        if kind == 'gate':
            self.gate_bytes += count
            self.gate_requests += 1
        else:
            self.payload_bytes += count
            self.payload_requests += 1
        return raw


def decode_metadata(blob, identity, method):
    magic, m, d, bits, gb, pb, source_id = unpack(HEADER, blob[:57])
    assert source_id == identity
    if method == 'stream':
        assert magic == b'STR1' and len(blob) == 57
        return dict(rows=m, dimensions=d, gate_base=gb, payload_base=pb)
    assert magic == (b'EXC1' if method == 'exact_centered' else b'JSC1')
    widths, qbase = tuple(blob[57:57 + d]), 57 + d
    row_bits = sum(widths)
    runtime = dict(rows=m, dimensions=d, gate_base=gb, payload_base=pb, widths=widths,
                   qbase=qbase, row_bits=row_bits, step=1 << bits)
    if method == 'exact_centered':
        assert bits == 0 and len(blob) == qbase + (m * row_bits + 7) // 8
        return runtime
    wb = qbase + (m * row_bits + 7) // 8
    w = tuple(get_bits(blob, wb, j * bits, bits) for j in range(d))
    tb, tw = wb + (d * bits + 7) // 8, sum(w).bit_length()
    t = tuple(get_bits(blob, tb, i * tw, tw) for i in range(m))
    runtime.update(w=w, t=t, total_w=sum(w))
    if method == 'row_sums':
        assert len(blob) == tb + (m * tw + 7) // 8
        return runtime
    ub = tb + (m * tw + 7) // 8
    column_widths = tuple((m * width).bit_length() for width in w)
    offset, fields = 0, []
    for _ in range(1 if method == 'full_pair' else 3):
        values = []
        for width in column_widths:
            values.append(get_bits(blob, ub, offset, width))
            offset += width
        fields.append(tuple(values))
    assert len(blob) == ub + (offset + 7) // 8
    if method == 'full_pair':
        u = fields[0]
        L = tuple(sum(max(0, total - runtime['total_w'] + width) for total in t) for width in w)
        V = tuple(sum(min(width, total) for total in t) for width in w)
    else:
        u, L, V = fields
    runtime.update(u=u, alpha=tuple(min(2 * width, col - lo) for width, col, lo in zip(w, u, L)),
                   beta=tuple(min(2 * width, hi - col) for width, col, hi in zip(w, u, V)))
    return runtime


def route_call(method, packed, query_bytes, source_handle):
    """MATHS 12.1-12.3: guide, exact selection, original bytes, ordinary calculation."""
    blob = memoryview(packed).tobytes()
    query = unpack('<' + 'h' * (len(query_bytes) // 2), query_bytes)
    fd, identity = source_handle
    source = SourceReader(fd, memoryview(identity).tobytes())
    runtime = decode_metadata(blob, source.source_id, method)
    m, d = runtime['rows'], runtime['dimensions']
    assert len(query) == d
    gb, pb = runtime['gate_base'], runtime['payload_base']

    def source_score(i):
        raw = source.read('gate', gb + 2 * d * i, 2 * d)
        return sum(a * b for a, b in zip(unpack('<' + 'h' * d, raw), query))

    def coarse_score(i):
        score, offset = 0, i * runtime['row_bits']
        for coefficient, width in zip(query, runtime['widths']):
            score += coefficient * get_bits(blob, runtime['qbase'], offset, width)
            offset += width
        return runtime['step'] * score

    if method in ('stream', 'exact_centered'):
        scorer = source_score if method == 'stream' else coarse_score
        winner, best = 0, scorer(0)
        for i in range(1, m):
            value = scorer(i)
            if value > best:
                winner, best = i, value
    else:
        counters = Counter()
        intervals = joint['row_sum_intervals'](runtime, query, counters) if method == 'row_sums' else joint['propagated_intervals'](runtime, query, counters)
        coarse = tuple(coarse_score(i) for i in range(m))
        lower = tuple(base + bounds[0] for base, bounds in zip(coarse, intervals))
        upper = tuple(base + bounds[1] for base, bounds in zip(coarse, intervals))
        anchor = max(range(m), key=lambda i: (lower[i], -i))
        retained = [anchor]
        order = tuple(sorted(range(d), key=lambda j: (abs(query[j]), j))) if method == 'pair_total' else None
        for i in range(m):
            if i == anchor or upper[i] < lower[anchor] or (upper[i] == lower[anchor] and i > anchor):
                continue
            bound = None
            if method == 'full_pair':
                omitted = tuple(runtime['t'][j] for j in range(m) if j not in (i, anchor))
                bound = FullPairSupport(runtime['w'], runtime['u'], omitted,
                                        runtime['t'][i], runtime['t'][anchor]).exact(query)
            elif method == 'pair_dual':
                bound = joint['pair_dual_bound'](runtime, i, anchor, query, counters)
            elif method == 'pair_total':
                bound = joint['pair_bound'](runtime, i, anchor, query, counters, order)
            if bound is not None:
                difference = coarse[i] - coarse[anchor] + bound
                if difference < 0 or (difference == 0 and i > anchor):
                    continue
            retained.append(i)
        winner = anchor
        if len(retained) > 1:
            best = source_score(anchor)
            common_upper = best - lower[anchor]
            for i in retained[1:]:
                if upper[i] + common_upper < best or (upper[i] + common_upper == best and i > winner):
                    continue
                value = source_score(i)
                if value > best or (value == best and i < winner):
                    winner, best = i, value
                common_upper = min(common_upper, value - lower[i])
    payload = source.read('payload', pb + winner * 2 * d * d, 2 * d * d)
    output = joint['ordinary'](payload, query, d)
    return (winner, payload, output, source.gate_bytes, source.gate_requests,
            source.payload_bytes, source.payload_requests)


def route_experiment():
    rng, records = Random(2026092902), []
    with TemporaryDirectory(prefix='cassette-hypothesis-') as scratch:
        path = Path(scratch) / 'source.bin'
        for case in range(32):
            m, d = rng.choice(((12, 16), (24, 32)))
            family = rng.choice(joint['FAMILIES'])
            gate, payloads, raw, queries, pb = joint['make_source'](family, m, d, rng)
            identity = sha256(raw).digest()
            path.write_bytes(raw)
            assert sha256(path.read_bytes()).digest() == identity
            compiled = joint['compile_joint'](gate, 8, 0, pb, identity)
            full = compiled['qwt_blob'] + pack_bits(compiled['u'], [(m * width).bit_length() for width in compiled['w']])
            guides = dict(row_sums=compiled['qwt_blob'], full_pair=full,
                          pair_total=compiled['blob'], pair_dual=compiled['blob'],
                          exact_centered=joint['compile_centered'](gate, 0, pb, identity)['blob'],
                          stream=pack(HEADER, b'STR1', m, d, 0, 0, pb, identity))
            expected = []
            for query in queries:
                scores = [sum(a * b for a, b in zip(row, query)) for row in gate]
                winner = max(range(m), key=lambda i: (scores[i], -i))
                payload = pack('<' + 'h' * (d * d), *payloads[winner])
                expected.append((winner, payload, joint['ordinary'](payload, query, d)))
            raw_size = len(raw)
            del gate, payloads, raw, compiled
            facts = {name: dict(guide_bytes=len(blob), queries=[]) for name, blob in guides.items()}
            with path.open('rb', buffering=0) as source:
                verified_source_handle = source.fileno(), identity
                for query_index, query in enumerate(queries):
                    encoded_query = pack('<' + 'h' * d, *query)
                    calls = {name: (lambda name=name: route_call(name, guides[name], encoded_query,
                                                               verified_source_handle)) for name in METHODS}
                    results = {}
                    for name in METHODS:
                        result, peak = traced_peak(calls[name])
                        assert result[:3] == expected[query_index], (case, query_index, name)
                        assert result[3] == result[4] * 2 * d
                        assert result[5:] == (2 * d * d, 1)
                        results[name] = result
                        facts[name]['queries'].append(dict(winner=result[0], output=list(result[2]),
                            payload_sha256=sha256(result[1]).hexdigest(), peak_bytes=peak,
                            gate_bytes=result[3], gate_requests=result[4], payload_bytes=result[5],
                            payload_requests=result[6]))
                    samples = time_methods(calls, results)
                    for name in METHODS:
                        facts[name]['queries'][-1].update(time_ns=median(samples[name]),
                                                         timing_samples_ns=samples[name])
            for name, values in facts.items():
                runs = values['queries']
                values.update(peak_bytes=max(run['peak_bytes'] for run in runs),
                              time_ns=median(run['time_ns'] for run in runs),
                              gate_bytes=sum(run['gate_bytes'] for run in runs))
            records.append(dict(case=case, rows=m, dimensions=d, family=family,
                                source_bytes=raw_size, methods=facts))
            print(json.dumps(dict(progress='route_case', case=case, family=family)), flush=True)
    return records


def sign_record(records, candidate, comparator, metric):
    pairs = [(case['methods'][candidate][metric], case['methods'][comparator][metric]) for case in records]
    losses = sum(left > right for left, right in pairs)
    wins = sum(left < right for left, right in pairs)
    n = len(pairs)
    failures = n - wins if metric == 'peak_bytes' else losses
    p = sum(comb(n, k) for k in range(failures, n + 1)) / (2 ** n)
    ratios = [left / right for left, right in pairs if right]
    return dict(candidate=candidate, comparator=comparator, metric=metric, source_cases=n,
                wins=wins, ties=n - wins - losses, losses=losses, failures_for_test=failures, p_improvement_failure=p,
                reject_improvement=p <= 0.05 / 20,
                median_ratio_excluding_zero_comparator=median(ratios) if ratios else None,
                ratio_min=min(ratios) if ratios else None, ratio_max=max(ratios) if ratios else None)


support_records = support_experiment()
print(json.dumps(dict(progress='support_complete', cases=len(support_records))), flush=True)
route_records = route_experiment()
tests = [sign_record(support_records, 'full_pair', 'flow', metric) for metric in ('peak_bytes', 'time_ns')]
tests += [sign_record(route_records, candidate, comparator, metric)
          for candidate in CANDIDATES for comparator in COMPARATORS
          for metric in ('peak_bytes', 'time_ns', 'gate_bytes')]
assert len(tests) == 20
protocol = ROOT / 'improvement-hypothesis-protocol.md'
experiment = ROOT / 'improvement-hypothesis-experiment.md'
report = dict(status='PASS_EXACTNESS', python=sys.version, machine=platform.machine(),
              protocol_sha256=sha256(protocol.read_bytes()).hexdigest(),
              experiment_sha256=sha256(experiment.read_bytes()).hexdigest(),
              definition_sha256=DEFINITION_HASHES, support=support_records, routes=route_records,
              statistical_tests=tests, alpha_family=0.05, test_count=20,
              route_executions=32 * 9 * len(METHODS), support_cases=32)
(ROOT / 'improvement-hypothesis-results.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(dict(status=report['status'], route_executions=report['route_executions'],
                     statistical_tests=tests), indent=2))
```
