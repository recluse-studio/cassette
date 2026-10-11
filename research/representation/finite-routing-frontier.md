# Finite frontier for exact phase-quotient routing

The source gate, not a relevance oracle, decides which region matters. This
note studies a finite exact guide that stores coarse phase-quotient rows in
RAM, names a certified set of possible winners, reads the original gate rows
only for that set, then reads one original payload. It gives an exhaustive
phase optimizer over a complete finite query domain and separates the
independent residue-width objective from the actual candidate-fetch objective.

The construction is a finite comparator. It is not a claim that every gate
matrix has a useful quotient guide, nor a Cassette runtime design.

## 1. Source operation and exact route

Fix an arbitrary integer gate matrix

\[
 A\in\mathbb Z^{m\times d},
\]

a complete finite query domain \(X\subset\mathbb Z^d\), and arbitrary
external payload records \(T_1,\ldots,T_m\). The exact source route uses the
least-index tie rule:

\[
 f_A(x)=\min\operatorname*{arg\,max}_{i\in[m]} A_i x. \tag{1}
\]

The normal result consumes the original returned payload:

\[
 F(A,T,x)=\mathcal N(T_{f_A(x)},x). \tag{2}
\]

The source stores each full gate row \(A_i\) as an exact external record. A
guide can read a selected row, compute its exact dot product, and later read
the selected payload \(T_i\). A guide never replaces a gate value or payload
with an estimate.

## 2. Phase-quotient representation

Choose a positive integer quantum \(\Delta=2^k\) and a phase vector

\[
 g\in\{0,\ldots,\Delta-1\}^d. \tag{3}
\]

For each source entry, define

\[
 q_{ij}=\left\lfloor {A_{ij}-g_j\over\Delta}\right\rfloor,\qquad
 r_{ij}=(A_{ij}-g_j)\bmod\Delta. \tag{4}
\]

Normalize each quotient column by subtracting its minimum. This does not
change any row-score ordering on a fixed query. Let

\[
 Q_j=\max_iq_{ij}-\min_iq_{ij},\qquad
 w_j=\max_ir_{ij}-\min_ir_{ij}. \tag{5}
\]

The resident guide stores the normalized \(q_{ij}\), each \(w_j\), the fixed
\(\Delta\), dimensions, source identity, and the declared tie rule. The
construction phases and common vector \(h\) are compilation facts only: they
cancel from every row comparison and are not needed at runtime. With fixed
\(k=\log_2\Delta\)-bit width fields, the actual guide payload is

\[
 B_{\rm guide}(g)=
 m\sum_{j=1}^{d}\lceil\log_2(Q_j+1)\rceil+dk+B_{\rm format}. \tag{6}
\]

A zero quotient range uses zero value bits but still has its dimensions and
format charge in \(B_{\rm format}\). A different variable-width remainder
encoding must charge its width metadata separately; it is not this format.

For query \(x\), compute the coarse least-index leader

\[
 \kappa_g(x)=\min\operatorname*{arg\,max}_i q_i x
\]

and the residue uncertainty

\[
 D_g(x)=\sum_{j=1}^{d}w_j|x_j|. \tag{7}
\]

The candidate set is

\[
 S_g(x)=\{\kappa_g(x)\}\cup
 \left\{i:
 \begin{array}{l}
 \Delta(q_{\kappa_g(x)}-q_i)x<D_g(x),\quad\hbox{or}\\
 \Delta(q_{\kappa_g(x)}-q_i)x=D_g(x)\ \hbox{and}\ i<\kappa_g(x)
 \end{array}\right\}. \tag{8}
\]

If \(S_g(x)=\{\kappa_g(x)\}\), return that exact winner with zero gate-row
reads. Otherwise read every original gate row indexed by \(S_g(x)\), compute
its exact score \(A_i x\), choose \(f_A(x)\) with the source tie rule, then
read and verify only \(T_{f_A(x)}\).

### Theorem 1 — exact candidate containment

For every \(x\in X\),

\[
 f_A(x)\in S_g(x). \tag{9}
\]

**Proof.** Write \(A_i=g+\Delta q_i+r_i\). The common \(gx\) cancels between
two rows. For \(k=\kappa_g(x)\),

\[
 (A_k-A_i)x=
 \Delta(q_k-q_i)x+(r_k-r_i)x.
\]

The absolute value of the residue term is at most \(D_g(x)\). If \(i>k\) and
the coarse gap is at least \(D_g(x)\), the source score of \(k\) is at least
that of \(i\), and the least-index tie rule retains \(k\). If \(i<k\), a
strictly larger coarse gap is required for that conclusion. Every excluded
row therefore loses to \(k\) under the source rule. The exact winner cannot
be excluded. \(\square\)

The theorem permits a candidate set of all \(m\) rows. Exactness alone is not
compression.

## 3. The finite optimizer and its named optimum

For fixed \(A,X,\Delta\), there are exactly \(\Delta^d\) phase vectors. For
each \(g\), enumerate every \(x\in X\), calculate (4)--(8) with integer
arithmetic, verify (9) directly from the source scores, and record

\[
 \begin{aligned}
 C_{\rm sum}(g)&=\sum_{x\in X}|S_g(x)|,\\
 C_{\rm worst}(g)&=\max_{x\in X}|S_g(x)|,\\
 R_{\rm sum}(g)&=\sum_{x\in X}\rho(|S_g(x)|),\\
 R_{\rm worst}(g)&=\max_{x\in X}\rho(|S_g(x)|),\\
 W_{\rm route}(g)&=\max_{x\in X}
   \{\text{coarse dots, comparisons, candidate address work}\},\\
 B_{\rm guide}(g)&\text{ from (6)}. \tag{10}
 \end{aligned}
\]

Here \(\rho(1)=0\) and \(\rho(s)=s\) for \(s>1\). Candidate count and
gate-read count are separate because a certified singleton names its winner
without reading a source gate row.

The **phase-quotient frontier** is the nondominated set of

\[
 (B_{\rm guide}(g), C_{\rm worst}(g), C_{\rm sum}(g),
 R_{\rm worst}(g),R_{\rm sum}(g),W_{\rm route}(g)).
 \tag{11}
\]

Any scalar preference, such as lexicographic
\((R_{\rm worst},R_{\rm sum},B_{\rm guide},W_{\rm route})\), selects an exact
optimizer from this finite frontier. This is an optimum only among
representations of (3)--(8) at the declared \(\Delta\) and byte encoding. It
does not minimize all exact guides, arbitrary arithmetic programs, decision
diagrams, or source indexes.

**Theorem 2 — exhaustive phase optimum.** Enumeration of all
\(g\in\{0,\ldots,\Delta-1\}^d\), followed by the full-domain computation in
(10), returns exactly the frontier (11).

**Proof.** The phase space and domain are finite. Equations (4)--(8)
deterministically produce one correct guide and candidate set for each phase
by Theorem 1. Equation (10) evaluates every objective coordinate for every
guide. Removing exactly the dominated vectors produces (11). \(\square\)

This theorem is the lower-bound certificate within the class: a candidate
claiming a better vector must name a phase omitted from the finite set or
disagree with a recomputable full-domain value. It is not an information
lower bound outside the class.

## 4. Width minimization is not fetch minimization

For one column, choosing a phase at a largest cyclic gap among the entries
minimizes that column's residue width \(w_j\), hence its contribution to the
uncertainty bound \(D_g(x)\). It does not generally minimize the guide bits in
(6), because the normalized quotient range \(Q_j\) can gain a bit. It also
does not generally minimize (10): the coarse leader and the weighted
uncertainty couple all columns through each query.

The following complete finite counterexample demonstrates the distinction.
Take

\[
 A=\begin{pmatrix}
 -6&-5\\
 -5&-1\\
 -4&5
 \end{pmatrix},\quad
 X=\{-2,-1,0,1,2\}^2\setminus\{(0,0)\},\quad
 \Delta=4. \tag{12}
\]

Exhaustive enumeration of all sixteen phases gives a width-minimizing phase
\(g=(1,0)\) with

\[
 (w_1,w_2)=(2,2),\qquad
 (Q_1,Q_2)=(0,3),\qquad
 B_{\rm guide}-B_{\rm format}=10,\qquad
 C_{\rm sum}=34,\quad C_{\rm worst}=3. \tag{13}
\]

The phase \(g=(3,0)\) has the larger widths \((3,2)\) and a larger direct
guide payload under (6), yet

\[
 (Q_1,Q_2)=(1,3),\qquad
 B_{\rm guide}-B_{\rm format}=13,\qquad
 C_{\rm sum}=33,\quad C_{\rm worst}=3. \tag{14}
\]

Thus minimizing widths independently is not a theorem about guide bits, total
candidate count, or worst candidate count. The full phase frontier is the
required comparator.

The following self-contained Python check reproduces the phase search,
candidate containment, and the counterexample.

    from itertools import product

    A = ((-6, -5), (-5, -1), (-4, 5))
    X = tuple(x for x in product(range(-2, 3), repeat=2) if x != (0, 0))
    delta = 4
    m, d = len(A), len(A[0])

    def bits(range_value):
        return range_value.bit_length()

    def phase_data(g):
        columns, widths, quotient_ranges = [], [], []
        for j in range(d):
            raw = [(A[i][j] - g[j]) // delta for i in range(m)]
            residues = [(A[i][j] - g[j]) % delta for i in range(m)]
            low = min(raw)
            column = tuple(value - low for value in raw)
            columns.append(column)
            widths.append(max(residues) - min(residues))
            quotient_ranges.append(max(column))
        rows = tuple(tuple(columns[j][i] for j in range(d))
                     for i in range(m))
        guide_bits = (
            m * sum(bits(q_range) for q_range in quotient_ranges) +
            d * (delta - 1).bit_length()
        )
        return rows, tuple(widths), tuple(quotient_ranges), guide_bits

    def exact_winner(x):
        scores = tuple(sum(A[i][j] * x[j] for j in range(d)) for i in range(m))
        return min(i for i, score in enumerate(scores) if score == max(scores))

    def candidate(g, x):
        rows, widths, _, _ = phase_data(g)
        coarse = tuple(sum(rows[i][j] * x[j] for j in range(d))
                       for i in range(m))
        leader = min(i for i, score in enumerate(coarse) if score == max(coarse))
        uncertainty = sum(widths[j] * abs(x[j]) for j in range(d))
        selected = []
        for i in range(m):
            gap = delta * sum((rows[leader][j] - rows[i][j]) * x[j]
                              for j in range(d))
            if i == leader or gap < uncertainty or (gap == uncertainty and i < leader):
                selected.append(i)
        assert exact_winner(x) in selected
        return tuple(selected)

    frontier = []
    for g in product(range(delta), repeat=d):
        _, widths, ranges, guide_bits = phase_data(g)
        sizes = tuple(len(candidate(g, x)) for x in X)
        frontier.append((sum(widths), sum(sizes), max(sizes),
                         guide_bits, g, widths, ranges))

    width_best = min(item for item in frontier if item[0] == min(x[0] for x in frontier))
    candidate_best = min(frontier, key=lambda item: (item[1], item[2], item[3]))
    assert width_best[4:] == ((1, 0), (2, 2), (0, 3))
    assert width_best[:4] == (4, 34, 3, 10)
    assert candidate_best[4:] == ((3, 0), (3, 2), (1, 3))
    assert candidate_best[:4] == (5, 33, 3, 13)
    print("PASS: width minimizer and candidate minimizer differ")

The bit function returns \(\lceil\log_2(v+1)\rceil\) for a nonnegative
quotient range \(v\), including zero. The check charges the fixed two-bit
remainder width field per column. Phases are not runtime bits. Common source,
dimension, and interpreter fields belong in \(B_{\rm format}\) and do not
alter this comparison.

## 5. Scheduling and all outstanding reads

The candidate set is known after resident coarse arithmetic. A singleton
issues no gate-row read; otherwise a schedule may issue the exact original
gate-row reads for every member of \(S_g(x)\). After their verification and
exact source-score comparison, it issues the one payload read. No claim may
treat a gate-row read outstanding at a predicate or routing boundary as
absent.

For each query and concrete schedule policy \(\sigma\), record every request:
its object identity, request time, start, completion, lane, byte count,
in-flight buffer reservation, completion buffer, and release time. Let
\(L_\sigma(t)\) be the bytes in every such live or outstanding object. The
schedule is feasible only when

\[
 B_{\rm guide}(g)/8+B_{\rm normal}(t)+L_\sigma(t)\le M
 \quad\hbox{at every event time}, \tag{15}
\]

each lane has nonoverlapping jobs, every source row completes before its exact
comparison, and the payload completes before \(\mathcal N\) consumes it. The
end-to-end finish time includes resident coarse arithmetic, row reads, exact
row dots, candidate reduction, payload read and verification, and ordinary
calculation.

For a finite tick, lane, queue-depth, and release policy, enumeration of all
such schedules decides (15) and the deadline exactly for that device model.
Outside that declared policy, (15) is the accounting test, not a claim that a
per-interval count proves feasibility.

## 6. Comparator boundary and prior art

A full external gate scan reads all \(m\) rows before choosing a payload. The
phase quotient guide is useful only where the finite frontier shows
\(|S_g(x)|<m\) often enough to repay its resident bits, coarse arithmetic, and
source-row latency. A resident table of \(f_A(x)\) is another exact comparator;
it stores every route for \(X\) and may have zero gate-row reads, at its
declared domain-table bytes.

Reduced ordered decision diagrams already provide finite-function sharing:
[Bryant (1986)](https://doi.org/10.1109/TC.1986.1676819). Exact
sign-preserving integer coefficient reduction is also established in
[Frank and Tardos (1987)](https://doi.org/10.1007/BF02579200). Exact
maximum-inner-product search supplies a further systems comparator:
[Yu et al. (2017)](https://arxiv.org/abs/1706.01449).

The phase decomposition is a certified interval bound for an exact argmax, not
a new general form of routing mathematics. Those sources do not, from their
stated models, establish the finite phase frontier with external original gate
rows, one original payload read, and a schedule that charges outstanding
requests. Nor has this note shown that this combination is new. The finite
optimizer supplies a defensible baseline: a new guide must beat the complete
phase frontier under the same gate rows, full input domain, payload layout,
and outstanding-read schedule.

No novelty claim follows from this note. The candidate question is whether a
different finite representation can dominate this phase frontier and the
resident route table while preserving (1), original gate-row verification,
one original payload read, and (15).
