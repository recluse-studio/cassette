# Full-pair support against an explicit transportation-flow oracle

This comparison asks one narrow question. Given only the exact compiled widths, row totals, and column totals, does the canonical full-pair interpreter return the same support as an ordinary integral transportation flow that preserves every row and column margin?

It does on the declared finite set. The result verifies equality of returned support values; it does not establish a speed ranking, a peak-RAM result, or a new optimization theorem.

## Object and common information

For a query vector \(x\), both paths compute the largest possible residual score difference for rows 0 and 1, subject to

\[
0\le e_{ij}\le w_j,\qquad \sum_j e_{ij}=t_i,\qquad \sum_i e_{ij}=u_j.
\]

Both paths receive only \((w,t,u,x)\). The generated source table constructs a valid guide, then the experiment deletes that table before measurements begin. Neither path reads an original residual table or replays an original file. Source identity has no role in this support-only oracle.

The flow reference sends \(\sum_i t_i\) units through a source, **every** row, every row-to-column edge, every column, and a sink. Source-to-row capacity is \(t_i\), row-to-column capacity is \(w_j\), and column-to-sink capacity is \(u_j\). Costs are \(x_j\) for row 0, \(-x_j\) for row 1, and zero for the other rows. Its integral max-cost value is therefore the same exact support objective. The explicit graph has \(m+md+d\) forward arcs and twice as many residual records.

The fence loads the canonical `FullPairSupport` declaration from [full-pair-polymatroid.md](full-pair-polymatroid.md), rather than copying it. The saved run binds that declaration through the text digest `f04eeb91a293d8c460107a5efbe0fae7498a946272d9cfd703c5dcb7f9a3a5fb`, Python 3.14.6, and `arm64`. Each measured call rebuilds the full-pair sorted-slack preparation; the flow call rebuilds its graph. There is no warm start, shared preprocessing, hidden source matrix, or uncharged preparation across queries.

## Declared finite comparison

The fixed grid contains four seeded integer queries for each of 8 by 8, 16 by 16, and 32 by 32 generated tables, then four queries on an 8 by 8 padding of the earlier four-coordinate hard witness. That is 16 comparisons, below the declared limit of 18. The largest generated table has \(32\cdot32\) signed-16-representable entries, or 2,048 packed bytes, well below the 20 MiB source-fixture limit.

| Guide | Queries | Support values | Forward arcs | Residual records | Full-pair declared array slots |
|---|---:|---|---:|---:|---:|
| seeded 8 by 8 | 4 | 407, 391, 449, 719 | 80 | 160 | 112 |
| seeded 16 by 16 | 4 | 1,574, 1,556, 1,867, 1,433 | 288 | 576 | 256 |
| seeded 32 by 32 | 4 | 2,584, 3,590, 2,286, 2,902 | 1,088 | 2,176 | 544 |
| padded hard witness, 8 by 8 | 4 | -26, 144, 94, 8 | 80 | 160 | 112 |

Every support value agreed exactly. The complete per-query record is [full-pair-flow-comparison-results.json](full-pair-flow-comparison-results.json).

`logical_solver_array_slots` counts named list slots in the research wrapper: four suffix-tree arrays, an allocation vector, and a query-coefficient vector. It leaves out Python object headers, heap entries, changed-node lists, recursion frames, and allocator behavior. It is a transparent structural count, not a RAM measurement.

## Observed Python allocations and elapsed time

The allocation column is the additional `tracemalloc` peak while each build-and-solve call runs, with the immutable guide and query already held and `gc.collect()` completed before tracing starts. It is an interpreter-allocation observation, not process RAM, physical RAM, or the future packed-runtime peak. Timings were measured separately with tracing disabled, after `gc.collect()`, and are medians of three cold build-and-solve calls in this Python implementation. They do not compare optimized algorithms or predict runtime hardware performance.

| Guide | Full-pair traced peak, bytes | Flow traced peak, bytes | Full-pair median time, ns | Flow median time, ns |
|---|---:|---:|---:|---:|
| seeded 8 by 8 | 4,864–5,336 | 20,656–21,072 | 103,458–462,250 | 1,322,584–1,520,208 |
| seeded 16 by 16 | 7,600–7,824 | 64,400–65,200 | 261,125–823,292 | 12,798,917–16,009,375 |
| seeded 32 by 32 | 13,720–13,880 | 227,088–227,248 | 944,041–2,432,792 | 202,508,167–227,731,958 |
| padded hard witness, 8 by 8 | 3,640–3,960 | 19,472–19,984 | 78,500–183,625 | 179,750–396,958 |

This standard-library flow implementation allocates more traced Python memory and takes longer on all 16 calls. That is a property of these two unoptimized Python programs and this cold-call protocol. A specialized transportation or network-polymatroid implementation can avoid portions of the explicit graph, and the result does not determine a general best method.

## Comparator boundary

The explicit graph is a valid exact reference because it preserves the same margins and cell capacities, includes all unscored rows, and uses no original residual values after compilation. It is not an exhaustive strongest comparator. A fair later comparison must keep the same information boundary while adding a named specialized established algorithm, with equivalent preprocessing and warm-reuse rules on both paths.

The full-pair interpreter remains an interpretation of stored margins. It is not a complete routing policy, an original-weight reconstruction, a live-storage result, or a novelty claim.

## Reproducible standard-library fence

The script below creates only generated fixtures, compiles \((w,t,u)\), deletes each source table, loads the canonical implementation, and then compares the two support values. It uses only the Python standard library.

```python
from __future__ import annotations

import gc
import hashlib
from pathlib import Path
import platform
from random import Random
from statistics import median
import sys
from time import perf_counter_ns
import json
import tracemalloc


def load_canonical_full_pair_support():
    document = Path('research/representation/full-pair-polymatroid.md').read_text()
    start = document.index('```python\n') + len('```python\n')
    end = document.index('\nSEED = ', start)
    namespace = {}
    exec(document[start:end], namespace)
    return namespace['FullPairSupport'], hashlib.sha256(document[start:end].encode()).hexdigest()


FullPairSupport, CANONICAL_DEFINITION_SHA256 = load_canonical_full_pair_support()


def max_cost_transport(widths, totals, columns, query):
    rows, dimensions = len(totals), len(widths)
    source = 0
    row_base = 1
    column_base = row_base + rows
    sink = column_base + dimensions
    vertices = sink + 1
    graph = [[] for _ in range(vertices)]

    def add_edge(left, right, capacity, cost):
        graph[left].append([right, len(graph[right]), capacity, cost])
        graph[right].append([left, len(graph[left]) - 1, 0, -cost])

    for row, total in enumerate(totals):
        add_edge(source, row_base + row, total, 0)
    for row in range(rows):
        for column, width in enumerate(widths):
            cost = query[column] if row == 0 else -query[column] if row == 1 else 0
            add_edge(row_base + row, column_base + column, width, cost)
    for column, total in enumerate(columns):
        add_edge(column_base + column, sink, total, 0)

    required = sum(totals)
    sent = value = 0
    while sent < required:
        distance = [None] * vertices
        parent = [None] * vertices
        distance[source] = 0
        for _ in range(vertices - 1):
            changed = False
            for left, edges in enumerate(graph):
                if distance[left] is None:
                    continue
                for edge_at, edge in enumerate(edges):
                    right, _, capacity, cost = edge
                    proposal = distance[left] + cost
                    if capacity and (distance[right] is None or proposal > distance[right]):
                        distance[right] = proposal
                        parent[right] = (left, edge_at)
                        changed = True
            if not changed:
                break
        assert parent[sink] is not None
        amount = required - sent
        vertex = sink
        while vertex != source:
            previous, edge_at = parent[vertex]
            amount = min(amount, graph[previous][edge_at][2])
            vertex = previous
        vertex = sink
        while vertex != source:
            previous, edge_at = parent[vertex]
            edge = graph[previous][edge_at]
            edge[2] -= amount
            graph[vertex][edge[1]][2] += amount
            vertex = previous
        sent += amount
        value += amount * distance[sink]
    forward_arcs = rows + rows * dimensions + dimensions
    return value, dict(vertices=vertices, forward_arcs=forward_arcs,
                       residual_arc_records=2 * forward_arcs, solver_array_slots=3 * vertices)


def compile_guide(widths, source):
    return dict(widths=tuple(widths), totals=tuple(map(sum, source)),
                columns=tuple(map(sum, zip(*source))))


def full_pair_call(guide, query):
    solver = FullPairSupport(guide['widths'], guide['columns'], guide['totals'][2:],
                             guide['totals'][0], guide['totals'][1])
    value = solver.exact(query)
    omitted_rows, dimensions = len(guide['totals']) - 2, len(guide['widths'])
    return value, dict(tree_array_slots=16 * max(1, omitted_rows), allocation_slots=dimensions,
                       query_coefficient_slots=dimensions,
                       logical_solver_array_slots=16 * max(1, omitted_rows) + 2 * dimensions)


def allocation_measurement(call):
    gc.collect()
    tracemalloc.start()
    value, facts = call()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return value, facts, dict(additional_python_peak_bytes=peak)


def timing_measurement(call, repeats=3):
    values = []
    for _ in range(repeats):
        gc.collect()
        started = perf_counter_ns()
        value, _ = call()
        values.append(perf_counter_ns() - started)
    return value, dict(wall_time_median_ns=int(median(values)), wall_time_repeats=repeats)


def random_source(rows, dimensions, rng):
    widths = tuple(rng.randrange(1, 7) for _ in range(dimensions))
    return widths, tuple(tuple(rng.randrange(width + 1) for width in widths) for _ in range(rows))


def padded_witness():
    width_head = (3, 1, 3, 2)
    source_head = ((3, 0, 3, 1), (0, 1, 0, 2), (3, 0, 3, 0), (1, 0, 1, 0))
    widths = width_head + (0, 0, 0, 0)
    source = tuple(row + (0, 0, 0, 0) for row in source_head) + ((0,) * 8,) * 4
    return widths, source


SEED = 2026092401
rng = Random(SEED)
instances = []
for rows, dimensions in ((8, 8), (16, 16), (32, 32)):
    widths, source = random_source(rows, dimensions, rng)
    guide = compile_guide(widths, source)
    del source
    queries = []
    for _ in range(4):
        query = tuple(rng.randrange(-63, 64) for _ in range(dimensions))
        queries.append(query if any(query) else (1,) + (0,) * (dimensions - 1))
    instances.append((f'seeded_{rows}x{dimensions}', guide, queries))
widths, source = padded_witness()
witness = compile_guide(widths, source)
del source
instances.append(('padded_dual_tie_8x8', witness,
                  ((-24, -10, -27, 1, 0, 0, 0, 0), (24, 10, 27, -1, 0, 0, 0, 0),
                   (9, -5, 17, -11, 0, 0, 0, 0), (1, -1, 1, -1, 0, 0, 0, 0))))

results = []
for name, guide, queries in instances:
    for query_index, query in enumerate(queries):
        full_value, full_facts, full_allocation = allocation_measurement(lambda: full_pair_call(guide, query))
        flow_value, flow_facts, flow_allocation = allocation_measurement(
            lambda: max_cost_transport(guide['widths'], guide['totals'], guide['columns'], query))
        timed_full_value, full_timing = timing_measurement(lambda: full_pair_call(guide, query))
        timed_flow_value, flow_timing = timing_measurement(
            lambda: max_cost_transport(guide['widths'], guide['totals'], guide['columns'], query))
        assert full_value == flow_value == timed_full_value == timed_flow_value, (name, query_index)
        results.append(dict(name=name, query_index=query_index, rows=len(guide['totals']),
                            dimensions=len(guide['widths']), query=query, support=full_value,
                            full_pair=dict(**full_facts, **full_allocation, **full_timing),
                            explicit_flow=dict(**flow_facts, **flow_allocation, **flow_timing)))

assert len(results) == 16
print(json.dumps(dict(seed=SEED, comparisons=len(results), exact_support_agreement=True,
                      canonical_loader='executes the canonical Markdown fence through the declaration before SEED',
                      canonical_definition_sha256=CANONICAL_DEFINITION_SHA256,
                      python_version=sys.version,
                      platform_machine=platform.machine(),
                      measurement='single Python process; inputs held before tracemalloc; gc.collect before each measured call; preparation included; allocation and timing collected separately',
                      generated_fixture_max_signed16_bytes=32 * 32 * 2,
                      original_fixture_discarded_after_compile=True,
                      results=results), indent=2))
```

The saved JSON is the result of the fence as written. It records the canonical-definition digest, host interpreter metadata, support agreement, graph counts, structural array counts, separately collected Python allocation peaks, and separately collected three-run timing medians. No drive, model, original source file, or production path was used.
