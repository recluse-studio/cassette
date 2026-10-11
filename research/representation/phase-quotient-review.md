# Independent review of phase-quotient routing

This review reads the root construction and executes its embedded experiment
without changing either. It distinguishes an exact logical result from the
research harness's raw-file read counts. The representation is exact for the
declared integer affine gate once its candidate rows are read. Whether it
helps a drive-resident operation depends on candidate count, page layout,
deadline scheduling, and source binding.

## 1. Route proof and two-pass audit

The source route is the least-index maximum of \(A_i x\). The guide writes

\[
 A_i=h+\Delta Q_i+e_i,\qquad 0\le e_{ij}\le w_j.
\]

For coarse leader \(k\), the inequality

\[
 (A_k-A_i)x\ge\Delta(Q_k-Q_i)x-\sum_jw_j|x_j|
\]

proves the candidate rule in phase-quotient-routing.md. The strict versus
non-strict boundary is correct: an equal coarse gap excludes a larger-index
row because the source tie selects \(k\), but retains a smaller-index row.

The executable route uses two streaming passes over packed quotients. The
first finds the least-index coarse leader. The second recomputes each score,
tests eligibility, and reads exact source rows only where needed. It does not
need an \(m\)-entry score or candidate array.

Two deliberately adverse executions passed.

| Case | Source rows | Query | Required result | Observed result |
| --- | --- | --- | --- | --- |
| Middle leader with an earlier candidate | \((0,0),(256,255),(255,0)\) | \((1,1)\) | leader 1; candidates include 0, 1, 2; read leader once despite visiting 0 first | winner 1, original payload 1, three gate reads |
| Tie boundary for a smaller index | \((0,0),(256,1),(255,0)\) | \((1,1)\) | leader 1; row 0 remains because its coarse gap equals the bound and \(0<1\); row 2 excludes | winner 1, original payload 1, two gate reads |

The first case exercises the otherwise easy-to-miss branch where a candidate
with index below the leader causes the interpreter to load the leader before
the loop reaches it. The implementation reads the leader once, compares each
eligible row exactly, and returns the original payload bytes. The second
proves the source tie boundary is implemented, not merely stated.

The embedded full experiment also compiled and ran. It exercised four
generated families, 129 texts, three dependent routing layers, zero inputs,
duplicate rows, near ties, signed states, and original payload equality. The
reported output digests matched between phase-zero and width-optimal guides
within each source family.

## 2. Byte and source-binding audit

The guide's packed length is internally consistent for the experiment's
format:

\[
 57+d+
 \left\lceil{m\sum_jb_j\over8}\right\rceil+
 \left\lceil{d\,k\over8}\right\rceil
 \quad\text{bytes}, \tag{1}
\]

where 57 is the packed header, \(d\) stores the quotient widths, and the
last term stores fixed \(k\)-bit remainder widths. The quotient values are
packed row-major and decoded at offsets \(i\sum_jb_j\); the experiment's
expected-length assertion and all executed routes passed.

The current patch also compares the guide header identity with
SourceReader.source_id before any routing read. An independent mismatched
identity test passed: a guide whose embedded digest differed from the reader's
digest raised AssertionError before reads.

That is a manifest-binding assertion, not a per-query source-integrity proof.
The fixture computes source_id as sha256(data) before it opens the scratch
file, then passes that digest into SourceReader. Route does not hash the open
file, and the raw records carry no individual headers. The claim therefore
requires an immutable external source between offline manifest verification and
routing, or a separately proved durable-container identity and record-header
path. A mutation after the manifest digest is supplied is outside this harness.

The payload route itself is complete for the fixture: initial state reads
original embedding bytes; every ambiguous gate winner is independently
computed from original gate rows; the exact original payload bytes are read;
and ordinary_product consumes those bytes. The remaining source-mutability
boundary is a binding/integrity limit, not a failure of the algebraic candidate
theorem.

Logical pread counts are not physical-page counts. A gate row is \(G=2d\)
bytes and a payload is \(L=2d^2\) bytes. For a packed unaligned gate extent
starting at offset \(o\), one row can span

\[
 \left\lceil{(o\bmod4096)+G\over4096}\right\rceil \tag{2}
\]

pages. Several candidate rows can also share physical pages. The actual
physical requests depend on extent alignment, candidate identities, queue
coalescing, cache state, and read policy. The experiment uses raw scratch
pread calls, so its logical byte/request counts must not be presented as
durable-container or drive-page evidence.

## 3. Largest-gap phase and breakpoint review

For one coordinate, cutting the residue circle immediately after a largest
cyclic gap gives span \(\Delta-H\). The implementation chooses the residue
ending a maximum gap, with a deterministic smallest-residue tie break. Under

\[
 r_i(g)=(a_i-g)\bmod\Delta,
\]

that is the stated cut and is correct.

There are at most as many distinct stored \((Q_{\cdot j},w_j)\) pairs as
distinct source residues, hence at most \(m\), for a single coordinate. Moving
the discrete phase within an interval that contains no residue shifts
remainders together and leaves normalized quotients and width unchanged. The
representation at that interval is also represented at its next residue
boundary. The less-than-or-equal-to-\(m\) breakpoint claim is therefore valid
for this stored representation. It does not say there are at most \(m\)
numerical phase values, nor that independent largest-gap cuts minimize
candidate reads.

## 4. Deterministic dimension stress

I generated fresh matrices with seed 2026092102, \(m=48\),
\(\Delta=256\), 128 signed queries per dimension, and dimensions
\(d\in\{16,64,256,1024\}\). The phase for each column is its largest-gap
phase. Every candidate set was checked to contain the exact source winner.

The three source families are:

- independent: each gate entry uniform on \([-8192,8192]\);
- shared: common column value plus \(256q+r\), \(q\in[-8,8]\),
  \(r\in[-8,8]\);
- near: common column value plus \([-4,4]\).

The table gives encoded guide bytes, average and worst candidate rows,
average and worst exact gate rows actually read, average logical gate bytes,
and the ratio of logical gate bytes to one payload.

| Family | d | Encoded guide B | Avg / max candidates | Avg / max gate rows read | Avg logical gate B / payload B | Gate/payload |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| independent | 16 | 671 | 1.4922 / 4 | 0.8516 / 4 | 27.25 / 512 | 0.05322 |
| independent | 64 | 2,513 | 2.1484 / 9 | 1.7031 / 9 | 218 / 8,192 | 0.02661 |
| independent | 256 | 9,887 | 3.4922 / 12 | 3.2500 / 12 | 1,664 / 131,072 | 0.01270 |
| independent | 1024 | 39,413 | 10.1016 / 26 | 10.0938 / 26 | 20,672 / 2,097,152 | 0.00986 |
| shared | 16 | 569 | 1.0859 / 2 | 0.1719 / 2 | 5.50 / 512 | 0.01074 |
| shared | 64 | 2,057 | 1.2422 / 3 | 0.4531 / 3 | 58 / 8,192 | 0.00708 |
| shared | 256 | 8,093 | 1.5859 / 5 | 0.9375 / 5 | 480 / 131,072 | 0.00366 |
| shared | 1024 | 32,171 | 2.2734 / 7 | 1.8750 / 7 | 3,840 / 2,097,152 | 0.00183 |
| near | 16 | 89 | 48 / 48 | 48 / 48 | 1,536 / 512 | 3.00000 |
| near | 64 | 185 | 48 / 48 | 48 / 48 | 6,144 / 8,192 | 0.75000 |
| near | 256 | 569 | 48 / 48 | 48 / 48 | 24,576 / 131,072 | 0.18750 |
| near | 1024 | 2,105 | 48 / 48 | 48 / 48 | 98,304 / 2,097,152 | 0.04688 |

Encoded guide bytes include the 57-byte header, \(d\) quotient-width bytes,
and the actual packed quotient plus fixed-width remainder payload. A singleton
candidate performs zero original gate-row reads; otherwise every candidate row
is read. The table reports logical bytes only and intentionally gives no
physical-page-request count.

The stress exposes the central limitation. The bound in the candidate rule is

\[
 B(x)=\sum_jw_j|x_j|\le(\Delta-1)\lVert x\rVert_1. \tag{3}
\]

It grows linearly with dimension when widths and signed coordinate magnitudes
remain nonzero. The observed mean \(B(x)\) values were:

| Family | d=16 | d=64 | d=256 | d=1024 |
| --- | ---: | ---: | ---: | ---: |
| independent | 56,619 | 231,563 | 934,943 | 3,735,448 |
| shared | 3,962 | 16,093 | 64,083 | 256,509 |
| near | 1,959 | 8,145 | 32,278 | 128,986 |

The near family has the smallest guide and the worst routing result: every
query reads every gate row. This is the required counterpressure. Compact
guide bytes do not imply pruning. The independent family also loses
selectivity with dimension, from 1.49 to 10.10 average rows. The payload
becomes much larger than logical gate bytes at large \(d\), but the
independent case still performs about 10 logical gate-row reads before its
payload at \(d=1024\). Their physical-page behavior remains unmeasured under
the packed scratch layout.

For

\[
 A=\begin{pmatrix}8&-8\\5&-2\\-9&-10\end{pmatrix},\quad
 X=\{-2,-1,0,1,2\}^2\setminus\{(0,0)\},\quad\Delta=4,
\]

the independently width-minimizing phase \(g=(2,0)\) has widths \((2,2)\),
guide payload 19 bits under the actual fixed-width encoding, total candidate
count 31, total gate-row reads 14, and worst candidate count 2. Phase
\(g=(0,0)\) has larger widths \((3,2)\) but the same 19 guide bits, total
candidate count 29, total gate-row reads 10, and the same worst count 2. Thus width minimization fails even when it receives no resident-bit
advantage. This result does not alter the earlier note; it strengthens the
reason to retain the full phase frontier.

The following dependency-free check verifies the equal-bit counterexample.
The separate complete stress generator follows it. Both use Python standard
library only.

    from itertools import product
    from random import Random

    def guide(A, delta, phase):
        m, d = len(A), len(A[0])
        columns, widths, ranges = [], [], []
        for j in range(d):
            raw = [(A[i][j] - phase[j]) // delta for i in range(m)]
            rem = [(A[i][j] - phase[j]) % delta for i in range(m)]
            low = min(raw)
            column = [value - low for value in raw]
            columns.append(column)
            ranges.append(max(column))
            widths.append(max(rem) - min(rem))
        rows = tuple(tuple(columns[j][i] for j in range(d)) for i in range(m))
        bits = sum(
            m * value.bit_length()
            for value in ranges
        ) + len(ranges) * (delta - 1).bit_length()
        return rows, tuple(widths), bits

    def candidate(A, delta, phase, x):
        rows, widths, _ = guide(A, delta, phase)
        coarse = [sum(row[j] * x[j] for j in range(len(x))) for row in rows]
        leader = min(i for i, value in enumerate(coarse) if value == max(coarse))
        bound = sum(widths[j] * abs(x[j]) for j in range(len(x)))
        selected = tuple(
            i for i in range(len(A))
            if i == leader or
            delta * sum((rows[leader][j] - rows[i][j]) * x[j]
                        for j in range(len(x))) < bound or
            (delta * sum((rows[leader][j] - rows[i][j]) * x[j]
                         for j in range(len(x))) == bound and i < leader)
        )
        truth = [sum(A[i][j] * x[j] for j in range(len(x)))
                 for i in range(len(A))]
        assert min(i for i, value in enumerate(truth) if value == max(truth)) in selected
        return selected

    A = ((8, -8), (5, -2), (-9, -10))
    X = tuple(x for x in product(range(-2, 3), repeat=2) if x != (0, 0))
    for phase, expected in (((2, 0), (19, 31, 14, 2)), ((0, 0), (19, 29, 10, 2))):
        _, _, bits = guide(A, 4, phase)
        counts = tuple(len(candidate(A, 4, phase, x)) for x in X)
        gate_reads = tuple(0 if count == 1 else count for count in counts)
        assert (bits, sum(counts), sum(gate_reads), max(counts)) == expected
    print("PASS: equal-bit phase can fetch fewer candidates")

The following complete seeded generator reproduces the stress-table quantities.

    from random import Random

    STRESS_SEED, ROWS, DELTA, QUERY_COUNT = 2026092102, 48, 256, 128
    DIMENSIONS = (16, 64, 256, 1024)

    def largest_gap_phase(matrix):
        result = []
        for j in range(len(matrix[0])):
            residues = sorted({row[j] % DELTA for row in matrix})
            if len(residues) == 1:
                result.append(residues[0])
                continue
            gaps = [((residue - residues[i - 1]) % DELTA, residue)
                    for i, residue in enumerate(residues)]
            largest = max(gap for gap, _ in gaps)
            result.append(min(residue for gap, residue in gaps if gap == largest))
        return tuple(result)

    def stress_matrix(kind, dimensions, rng):
        common = [rng.randrange(-7000, 7001) for _ in range(dimensions)]
        if kind == "independent":
            return [[rng.randrange(-8192, 8193) for _ in range(dimensions)]
                    for _ in range(ROWS)]
        if kind == "shared":
            return [[common[j] + DELTA * rng.randrange(-8, 9) +
                     rng.randrange(-8, 9) for j in range(dimensions)]
                    for _ in range(ROWS)]
        return [[common[j] + rng.randrange(-4, 5) for j in range(dimensions)]
                for _ in range(ROWS)]

    def stress_guide(matrix, phase):
        columns, widths, ranges = [], [], []
        for j in range(len(phase)):
            raw = [(row[j] - phase[j]) // DELTA for row in matrix]
            remainders = [(row[j] - phase[j]) % DELTA for row in matrix]
            low = min(raw)
            column = [value - low for value in raw]
            columns.append(column)
            ranges.append(max(column))
            widths.append(max(remainders) - min(remainders))
        rows = tuple(tuple(columns[j][i] for j in range(len(phase)))
                     for i in range(ROWS))
        payload_bits = (
            ROWS * sum(value.bit_length() for value in ranges) +
            len(phase) * (DELTA - 1).bit_length()
        )
        return rows, tuple(widths), payload_bits

    def stress_summary(kind, dimensions, rng):
        matrix = stress_matrix(kind, dimensions, rng)
        phase = largest_gap_phase(matrix)
        rows, widths, payload_bits = stress_guide(matrix, phase)
        candidates, bounds = [], []
        for _ in range(QUERY_COUNT):
            x = tuple(rng.randrange(-31, 32) for _ in range(dimensions))
            x = x if any(x) else (1,) + x[1:]
            coarse = [sum(row[j] * x[j] for j in range(dimensions))
                      for row in rows]
            leader = min(i for i, value in enumerate(coarse)
                         if value == max(coarse))
            bound = sum(widths[j] * abs(x[j]) for j in range(dimensions))
            selected = tuple(
                i for i in range(ROWS)
                if i == leader or
                DELTA * sum((rows[leader][j] - rows[i][j]) * x[j]
                            for j in range(dimensions)) < bound or
                (DELTA * sum((rows[leader][j] - rows[i][j]) * x[j]
                             for j in range(dimensions)) == bound and i < leader)
            )
            source_scores = [sum(matrix[i][j] * x[j] for j in range(dimensions))
                             for i in range(ROWS)]
            winner = min(i for i, value in enumerate(source_scores)
                         if value == max(source_scores))
            assert winner in selected
            candidates.append(len(selected))
            bounds.append(bound)
        gate_reads = [0 if count == 1 else count for count in candidates]
        gate_bytes, payload_bytes = 2 * dimensions, 2 * dimensions * dimensions
        return dict(
            encoded_guide_bytes=57 + dimensions + (payload_bits + 7) // 8,
            average_candidates=sum(candidates) / QUERY_COUNT,
            maximum_candidates=max(candidates),
            average_gate_rows=sum(gate_reads) / QUERY_COUNT,
            maximum_gate_rows=max(gate_reads),
            average_gate_bytes=sum(gate_reads) * gate_bytes / QUERY_COUNT,
            gate_payload_ratio=(sum(gate_reads) * gate_bytes /
                                QUERY_COUNT / payload_bytes),
            average_bound=sum(bounds) / QUERY_COUNT,
        )

    for family_index, family in enumerate(("independent", "shared", "near")):
        for dimensions in DIMENSIONS:
            rng = Random(STRESS_SEED + family_index * 100000 + dimensions)
            print(family, dimensions, stress_summary(family, dimensions, rng))

## 6. Layerwise policy frontier

A three-layer experiment that forces one \(\Delta\), phase method, and block
layout across all layers compares only the diagonal part of the available
policy space. Exact routing preserves the state delivered to the next layer,
so the exact source state and output do not depend on which correct guide a
previous layer used. Layer costs can therefore be optimized independently
before combining them.

For layer \(\ell\), let its tested finite library produce nondominated vectors

\[
 {\cal P}_\ell\ni(b_\ell,r_\ell,w_\ell,s_\ell),
\]

where \(b_\ell\) is resident guide bits, \(r_\ell\) is the declared logical
read cost including its payload, \(w_\ell\) is route work, and \(s_\ell\) is
the layer's peak routing scratch beyond its resident guide and ordinary state.
The exact layerwise policy frontier is

\[
 \operatorname{ParetoMin}
 \left\{
 \left(\sum_{\ell=1}^{L}b_\ell,\\
       \sum_{\ell=1}^{L}r_\ell,\\
       \sum_{\ell=1}^{L}w_\ell,\\
       \max_{\ell=1}^{L}s_\ell\right):
 (b_\ell,r_\ell,w_\ell,s_\ell)\in{\cal P}_\ell
 \right\}. \tag{4}
\]

The addition of resident bits, reads, and work follows sequential execution.
Scratch takes a maximum only when the routing scratch is released between
layers; otherwise the live-state schedule must use its actual overlap. A
deadline objective is separate again: under strictly sequential service it
adds layer completion times, while overlapping I/O requires a complete
outstanding-request schedule.

Equation (4) is a finite Pareto convolution, not a global routing optimum.
It gives the best policy only over the tested layer libraries. A sweep over
three \(\Delta\) values is a bounded candidate library; it cannot support a
claim about all quantums, all phases, block sizes, or exact routing methods.

## 7. Bounded report and count audit

This audit reads the saved reports and their current executable fences; it
does not rerun either complete sweep. It covers
[remainder-sum-experiment.md](remainder-sum-experiment.md),
[remainder-sum-results.json](remainder-sum-results.json),
[remainder-sum-comparison.md](remainder-sum-comparison.md),
[dense-relu-relevance.md](dense-relu-relevance.md),
[dense-relu-results.json](dense-relu-results.json),
[dense-relu-comparison.md](dense-relu-comparison.md), MATHS section 12.7,
and the repository README as they stood on 2026-09-20.

The routing JSON contains 220 result objects: four generated source families
times 55 declared configurations. The fence declares 129 input texts and
three dependent layers, so \(220\cdot129\cdot3=85{,}140\) exact routing
operations. The 16 displayed routing rows agree with their matching saved
objects for guide bytes, requested gate bytes, modeled coalesced gate-page
bytes, support-coordinate visits, and integer square roots. The displayed
independent step-eight arithmetic also agrees with the objects: 6,720 minus
5,928 equals 792 requested gate bytes; 5,928 minus 4,176 equals 1,752.

The dense JSON contains seven declared configurations. Its 129 inputs and
three layers give \(7\cdot129\cdot3=2{,}709\) exact layer evaluations. All
seven displayed rows agree with the saved guide bytes, original up and down
bytes, and certified-inactive count. The reported step-eight difference in
up bytes, \(442{,}368-238{,}920=203{,}448\), and the reported 222,912 coarse
terms and 121,144 support visits also agree with the JSON.

The current fence source matches the reported finite libraries: the routing
fence constructs one exact-centered configuration and, for each of three
step sizes and two phase rules, exact split, quotient, four sum blocks, and
three moment blocks: \(1+3\cdot2\cdot9=55\). The dense fence constructs one
streamed configuration plus three step sizes times the presence or absence of
moments: \(1+3\cdot2=7\). The routing reader clears its gate-page set before
each route and adds the number of distinct gate pages after that route.

The 4,096-byte page fields are a declared model: per-request rounding and,
separately, unique gate pages within one route with no retained route cache.
They are neither physical external-drive request counts nor latency evidence.
Likewise, the reported guide figures are encoded resident-guide bytes. They
exclude buffers, interpreter objects, scratch, and verification state, so
they are not peak-RAM measurements. The comparison files state both limits;
MATHS section 12.7 preserves the distinction among guide bytes, scratch,
original-weight buffers, logical reads, modeled pages, and physical latency.

All local file targets and Markdown heading fragments reachable from the
audited documents resolved during this check. The audit found no mismatch in
the reported selected values or the stated scope.
