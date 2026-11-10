# Exact full-pair interpretation with a bounded working set

The joint guide already stores residual row totals and column totals. Earlier pair
interpreters replaced the other rows with a single bounded row, losing some of the
information those totals contain. This construction uses all the totals to recover
the exact pair bound. It stores working arrays indexed by rows and columns, without
materializing a row-by-column transportation matrix.

The result concerns integer residuals with a shared capacity for each column. It is
an interpretation of a compact summary, not a reconstruction of the residual matrix.
The selected original weights remain the inputs to the ordinary model calculation.

## 1. Information and objective

Let the full residual table satisfy

\[
0\le e_{ij}\le w_j,\qquad \sum_j e_{ij}=t_i,
\qquad \sum_i e_{ij}=u_j.
\]

The guide retains the exact integers \(w,t,u\), alongside the quotient representation,
source identity, and physical locators. These fields come from one valid source table.
Clipped pair slacks cannot replace the exact column totals in this construction.

For two distinguished rows \(p,q\), retain their totals \(t_p,t_q\), and write the
remaining \(n\) row totals as \(a_1,\ldots,a_n\). Put

\[
K=t_p+t_q,\quad \delta=t_p-t_q,\quad T=\sum_h a_h.
\]

The required support is the largest \(x^T(p-q)\) over **all** residual tables that
have the stored totals and capacities. That maximum is a safe pair comparison for
the original table. It need not equal the original pair's actual score difference.

## 2. A partial pair occupies an integral polymatroid

First relax the separate distinguished-row totals, retaining their sum. Let
\(r=p+q\), with \(0\le r_j\le2w_j\). For a partial allocation \(r\), the other rows
must fit below the remaining column capacities \(v=u-r\). Sort their totals in
descending order and let \(A_k\) be the sum of the largest \(k\), with \(A_0=0\).
The exact feasibility conditions are

\[
v\ge0,\qquad
S_k(r)=\sum_j\min(v_j,kw_j)-A_k\ge0
\quad(1\le k\le n).                                      \tag{1}
\]

These are the row-subset cuts of the source--row--column--sink network. For a row
subset of size \(k\), the strongest demand is \(A_k\); each column can receive at
most \(\min(v_j,kw_j)\). Integral capacities make the criterion exact for integer
tables. Unlike an exact aggregate check, a partial allocation may leave unused
column capacity. At \(\sum_j r_j=K\), the remaining capacity sums to \(T\), so the
other rows fill it exactly.

For completeness, this partial-allocation family is an integral polymatroid after
the coordinate bounds are imposed. Define

\[
f(S)=\sum_h\min(a_h,w(S)),\qquad
g(S)=u(S)+f(V\setminus S)-T.                              \tag{2}
\]

Here \(V\) is the column set. The column-cut form of (1) is \(r(S)\le g(S)\) for
every \(S\subseteq V\). The function \(f\) is submodular because it is a sum of
concave functions of a nonnegative modular weight. Complementation preserves
submodularity, so \(g\) is submodular. Source feasibility gives \(g(S)\ge0\),
\(g(\varnothing)=0\), and \(g(V)=K\).

For nonnegative \(r\), replacing \(g\) by its monotone closure
\(\bar g(S)=\min_{B\supseteq S}g(B)\) preserves all inequalities and yields a
normalized, nondecreasing, integral submodular rank. Intersecting with
\(r_j\le c_j=\min(2w_j,u_j)\) is the coordinate-cap restriction with rank

\[
h(S)=\min_{B\subseteq S}\left[\bar g(B)+c(S\setminus B)\right].
\]

The explicit \(u_j\) cap records the already required \(v_j\ge0\). A valid
original source supplies a feasible allocation of total \(K\); the restricted
rank is therefore exactly \(K\). Every feasible partial allocation extends to
that rank.

## 3. Exact concave allocation through suffix slack

At a fixed combined coordinate \(r_j\), maximizing \(c_j(p_j-q_j)\) gives

\[
\phi_j(r_j)=|c_j|\min(r_j,2w_j-r_j).                     \tag{3}
\]

Its first \(w_j\) integer increments each have value \(|c_j|\); its next \(w_j\)
increments each have value \(-|c_j|\). Greedy selection of the greatest feasible
remaining marginal increment maximizes a separable concave objective over an
integral polymatroid of fixed rank. One proof expands each coordinate into ordered
unit copies: the polymatroid becomes a matroid, and nonincreasing marginal weights
allow the standard weighted greedy rule to respect the copy order.

A feasibility check needs no matrix. If \(v_j>0\) and \(w_j>0\), decrementing
\(v_j\) by one changes (1) by

\[
S_k\longmapsto S_k-1\quad\text{exactly when}
k\ge h_j=\lceil v_j/w_j\rceil.                          \tag{4}
\]

The increment is feasible exactly when the affected suffix has minimum at least
one. If \(h_j>n\), it affects no cut. A suffix range-add/minimum tree answers the
check and applies the update. A failed increment stays infeasible after further
allocations, so that coordinate can be removed from the heap.

Equal marginal increments can be batched. The exact batch is the smallest of:

1. The number of increments before \(\lceil v_j/w_j\rceil\) changes.
2. The number before \(r_j=w_j\) or \(r_j=2w_j\).
3. The current minimum affected suffix slack.
4. The remaining total allocation \(K-\sum_jr_j\).

The first quantity is \(v_j-(h_j-1)w_j\). This also enforces \(r_j\le u_j\).
A coordinate moves by at most \(2w_j\), crosses at most two expiry boundaries,
and crosses one marginal-value boundary. Including a final failed check, there
are at most five heap visits per coordinate. The number of iterations therefore
does not grow with the numeric magnitude of a weight.

Denote the resulting exact relaxed support by \(\Psi_{\rm full}(c)\).

## 4. Restore both row totals with one scalar

The same partial-duality argument as in
[the projected pair refinement](pair-dual-refinement.md) now gives

\[
M_{pq}^{\rm full}(x)=\min_{\mu\in\mathbb R}
\left[\mu\delta+\Psi_{\rm full}(x-\mu\mathbf1)\right].   \tag{5}
\]

Both the relaxed and separately constrained problems are integral network-flow
polytopes. Linear-programming strong duality proves (5); integrality makes it an
identity for the integer support as well.

For integer queries, define

\[
F(z)=z\delta+\Psi_{\rm full}(2x-z\mathbf1).
\]

The greedy order can change only at \(\mu=x_j\) or
\(\mu=(x_j+x_l)/2\): these are exactly the sign and absolute-value order changes
of its marginal weights. Between those points the same deterministic greedy
allocation is optimal, so the relaxed support is affine. Thus the convex
objective has a minimum on the doubled integer grid. The outer intervals are
affine and bounded below by any feasible constrained value, so an optimum lies
in \([2\min x,2\max x]\). Adjacent-value binary search is exact, and

\[
M_{pq}^{\rm full}(x)=\tfrac12\min_{z\in\mathbb Z} F(z).
\]

The minimum is even. Equal query coordinates, zero widths, zero row totals, and
an empty omitted-row set require no altered optimization rule.

One allocation can also supply a subgradient, avoiding two support evaluations
per search step. For an optimal combined allocation \(r\), set

\[
D=\sum_j\operatorname{sign}(2x_j-z)\min(r_j,2w_j-r_j).
\]

Then \(\delta-D\) is a subgradient of \(F\). A zero coefficient uses the feasible
fractional split \(p_j=q_j=r_j/2\); the relaxed network's linear-programming
support permits that split even when \(r_j\) is odd. A zero subgradient certifies
the minimum. A negative subgradient retains the midpoint as the left endpoint;
a positive one retains it as the right endpoint. Retaining the midpoint avoids
skipping a minimum at a corner. Once only two adjacent integers remain, compare
their objective values. Cache the two endpoint values so that each search step
needs one new allocation and at most two final endpoints remain unevaluated.

This is the strongest uniformly valid pair upper bound obtainable from these
exact residual margins and capacities alone. If a proposed smaller bound lies
below this maximum, a feasible table with the same stored fields violates it.
This statement concerns the pair comparison and this fixed information set.
It does not prove that pairwise filtering is the best complete routing strategy,
or that these are the best mathematical values to store.

## 5. Working state and work

Sort the omitted totals once. Build the initial \(S_k\) by sorting column expiry
events \(\lceil u_j/w_j\rceil\); between events, the unsaturated columns contribute
\(k\sum w_j\), and the saturated columns contribute \(\sum u_j\). Preparation
costs \(O(n\log n+d\log d+n)\) arithmetic and \(O(n+d)\) words.

One relaxed evaluation makes \(O(d)\) heap visits and suffix operations. A live
tree records each node it changes once. At the end of an evaluation it restores
only those nodes from the initial tree. This avoids copying all \(n\) leaves for
every scalar trial. The touched-node list has at most the tree's \(O(n)\) nodes;
its work is bounded by the \(O(d\log(n+1))\) operations that caused the changes.
One evaluation therefore costs

\[
O\bigl(d\log(d+1)+d\log(n+1)\bigr)
\]

after preparation. Binary search uses \(O(1+\log(1+\max x-\min x))\) evaluations.
The total working state is \(O(n+d)\) words, including the initial/live trees,
lazy updates, touched-node bookkeeping, coordinate allocations, and heap.
Preparation for a different omitted-row set is additional; this note does not
make that work free across every challenger.

The Python fence uses ordinary recursive methods for its tree. Nested recursive
closures were removed after allocation measurements exposed self-retaining cycles.
A release check disables cyclic garbage collection and verifies that disposing of
the solver immediately releases its tree. This implementation detail matters to
the measured working set; the algorithm's word bound alone would not catch it.

These are word-operation bounds, not measured latency or Python peak RAM. Put
\(W=\sum_jw_j\), \(m=n+2\), and \(X=\max_j|x_j|\). Source-derived sums need
\(O(\log(1+mW))\) bits, tree updates also need a sign, coordinate/index fields
need their own bounds, and the doubled objective is safely bounded in magnitude
by \(6XW\). Coarse quotient scores and original-weight buffers remain separate
charges. A full source-bound runtime and a hardware measurement are still needed.

The flow, polymatroid greedy rule, scalar dual, and range-add tree are established
mathematics and algorithms. The proposed specialization must face a direct prior-art
and optimized-comparator challenge before any novelty or best-method claim.

## 6. Reproducible standard-library fence

This fence is research code. It exercises exact full support against explicitly
enumerated residual completions, including arbitrary-width and zero-width columns.
Its input is the guide's totals and widths; the brute reference alone sees source
rows. Run it from the repository root and preserve its JSON output.

```python
from heapq import heappush, heappop
from itertools import product
from random import Random
import json
import gc
import weakref

class SuffixSlack:
    def __init__(self, values, infinity):
        self.n, self.infinity = len(values), infinity
        self.minimum = [infinity] * (4 * max(1, self.n))
        self.lazy = [0] * len(self.minimum)
        self.marked = [False] * len(self.minimum)
        self.changed = []
        if self.n:
            self.build(1, 0, self.n, values)
        self.initial = self.minimum.copy()

    def build(self, node, left, right, values):
        if right - left == 1:
            self.minimum[node] = values[left]
            return
        middle = (left + right) // 2
        self.build(2 * node, left, middle, values)
        self.build(2 * node + 1, middle, right, values)
        self.minimum[node] = min(self.minimum[2 * node], self.minimum[2 * node + 1])

    def apply(self, node, change):
        if not self.marked[node]:
            self.marked[node] = True
            self.changed.append(node)
        self.minimum[node] += change
        self.lazy[node] += change

    def push(self, node):
        change = self.lazy[node]
        if change:
            self.apply(2 * node, change)
            self.apply(2 * node + 1, change)
            self.lazy[node] = 0

    def suffix_min(self, first):
        return self.visit_min(1, 0, self.n, first) if first < self.n else self.infinity

    def visit_min(self, node, left, right, first):
        if right <= first:
            return self.infinity
        if first <= left:
            return self.minimum[node]
        self.push(node)
        middle = (left + right) // 2
        return min(self.visit_min(2 * node, left, middle, first),
                   self.visit_min(2 * node + 1, middle, right, first))

    def suffix_add(self, first, change):
        if first < self.n:
            self.visit_add(1, 0, self.n, first, change)

    def visit_add(self, node, left, right, first, change):
        if right <= first:
            return
        if first <= left:
            self.apply(node, change)
            return
        self.push(node)
        middle = (left + right) // 2
        self.visit_add(2 * node, left, middle, first, change)
        self.visit_add(2 * node + 1, middle, right, first, change)
        if not self.marked[node]:
            self.marked[node] = True
            self.changed.append(node)
        self.minimum[node] = min(self.minimum[2 * node], self.minimum[2 * node + 1])

    def reset(self):
        count = len(self.changed)
        for node in self.changed:
            self.minimum[node] = self.initial[node]
            self.lazy[node] = 0
            self.marked[node] = False
        self.changed.clear()
        return count


class FullPairSupport:
    def __init__(self, widths, columns, omitted, first_total, second_total):
        self.widths, self.columns = tuple(widths), tuple(columns)
        self.total, self.difference = first_total + second_total, first_total - second_total
        self.n = len(omitted)
        assert len(widths) == len(columns) and len(widths) > 0
        assert all(w >= 0 and 0 <= u <= (self.n + 2) * w for w, u in zip(widths, columns))
        assert sum(columns) == self.total + sum(omitted)
        events = sorted(((u + w - 1) // w, w, u)
                        for w, u in zip(widths, columns) if w and u)
        active_width = sum(w for _, w, _ in events)
        expired_value = top = at = 0
        slack = []
        for k, row_total in enumerate(sorted(omitted, reverse=True), 1):
            while at < len(events) and events[at][0] <= k:
                _, w, u = events[at]
                active_width -= w
                expired_value += u
                at += 1
            top += row_total
            slack.append(expired_value + k * active_width - top)
        assert all(value >= 0 for value in slack)
        self.tree = SuffixSlack(slack, sum(columns) + 1)
        self.evaluations = self.heap_visits = self.restored_nodes = 0

    def allocate(self, coefficients):
        assert len(coefficients) == len(self.widths)
        allocated = [0] * len(self.widths)
        heap = []
        for j, (w, u, coefficient) in enumerate(zip(self.widths, self.columns, coefficients)):
            if w and u:
                heappush(heap, (-abs(coefficient), j))
        taken = value = visits = 0
        try:
            while taken < self.total:
                assert heap, 'The guide has no feasible full pair completion.'
                negative_gain, j = heappop(heap)
                visits += 1
                w, r = self.widths[j], allocated[j]
                remaining_column = self.columns[j] - r
                threshold = (remaining_column + w - 1) // w
                slope_capacity = w - r if r < w else 2 * w - r
                amount = min(remaining_column - (threshold - 1) * w,
                             slope_capacity, self.tree.suffix_min(threshold - 1),
                             self.total - taken)
                if amount == 0:
                    continue
                assert amount > 0
                allocated[j] += amount
                taken += amount
                value -= negative_gain * amount
                self.tree.suffix_add(threshold - 1, -amount)
                if allocated[j] < 2 * w and allocated[j] < self.columns[j]:
                    gain = abs(coefficients[j]) if allocated[j] < w else -abs(coefficients[j])
                    heappush(heap, (-gain, j))
            assert visits <= 5 * len(self.widths)
            difference = sum((1 if c > 0 else -1 if c < 0 else 0) * min(r, 2 * w - r)
                             for c, r, w in zip(coefficients, allocated, self.widths))
            return value, difference
        finally:
            self.evaluations += 1
            self.heap_visits += visits
            self.restored_nodes += self.tree.reset()

    def relaxed(self, coefficients):
        return self.allocate(coefficients)[0]

    def exact(self, query):
        def objective(z):
            value, difference = self.allocate(tuple(2 * x - z for x in query))
            return z * self.difference + value, self.difference - difference
        left, right = 2 * min(query), 2 * max(query)
        left_value = right_value = None
        while right - left > 1:
            middle = (left + right) // 2
            value, slope = objective(middle)
            if slope == 0:
                assert value % 2 == 0
                return value // 2
            if slope < 0:
                left, left_value = middle, value
            else:
                right, right_value = middle, value
        if left_value is None:
            left_value = objective(left)[0]
        if right_value is None:
            right_value = left_value if left == right else objective(right)[0]
        value = min(left_value, right_value)
        assert value % 2 == 0
        return value // 2


SEED = 2026092301
rng = Random(SEED)
cases = []
for n, dimensions, capacity, count in ((0, 3, 2, 24), (1, 3, 2, 24),
                                      (2, 3, 2, 180), (3, 4, 1, 24)):
    for _ in range(count):
        widths = tuple(rng.randrange(capacity + 1) for _ in range(dimensions))
        source = tuple(tuple(rng.randrange(w + 1) for w in widths) for _ in range(n + 2))
        cases.append((widths, source))
checks = relaxed_checks = evaluations = heap_visits = restored_nodes = 0
for widths, source in cases:
    columns = tuple(map(sum, zip(*source)))
    totals = tuple(map(sum, source))
    possible_rows = tuple(product(*(range(w + 1) for w in widths)))
    omitted_rows = [tuple(row for row in possible_rows if sum(row) == total)
                    for total in totals[2:]]
    completions = {tuple(map(sum, zip(*rows))) for rows in product(*omitted_rows)} if omitted_rows else {(0,) * len(widths)}
    pairs = [(p, q) for p in possible_rows if sum(p) == totals[0]
             for q in possible_rows if sum(q) == totals[1]
             if tuple(u - a - b for u, a, b in zip(columns, p, q)) in completions]
    combined = [r for r in product(*(range(2 * w + 1) for w in widths))
                if sum(r) == sum(totals[:2])
                and tuple(u - a for u, a in zip(columns, r)) in completions]
    solver = FullPairSupport(widths, columns, totals[2:], totals[0], totals[1])
    for query in product((-1, 0, 1), repeat=len(widths)):
        truth = max(sum(x * (a - b) for x, a, b in zip(query, p, q)) for p, q in pairs)
        relaxed_truth = max(sum(abs(x) * min(a, 2 * w - a) for x, a, w in zip(query, r, widths))
                            for r in combined)
        assert solver.relaxed(query) == relaxed_truth
        assert solver.exact(query) == truth
        assert not solver.tree.changed and solver.tree.minimum == solver.tree.initial
        assert not any(solver.tree.lazy)
        checks += 1
        relaxed_checks += 1
    evaluations += solver.evaluations
    heap_visits += solver.heap_visits
    restored_nodes += solver.restored_nodes
witness = FullPairSupport((1, 1, 1, 1), (1, 2, 1, 2), (1, 3), 2, 0)
assert witness.exact((1, -1, 1, -1)) == 0
wide_checks = scaled_heap_visits = 0
for widths, source in cases[::6]:
    columns = tuple(map(sum, zip(*source)))
    totals = tuple(map(sum, source))
    rows = tuple(product(*(range(w + 1) for w in widths)))
    other = [tuple(row for row in rows if sum(row) == total) for total in totals[2:]]
    completions = {tuple(map(sum, zip(*group))) for group in product(*other)} if other else {(0,) * len(widths)}
    pairs = [(p, q) for p in rows if sum(p) == totals[0]
             for q in rows if sum(q) == totals[1]
             if tuple(u - a - b for u, a, b in zip(columns, p, q)) in completions]
    for _ in range(4):
        query = tuple(rng.randrange(-10**6, 10**6 + 1) for _ in widths)
        truth = max(sum(x * (a - b) for x, a, b in zip(query, p, q)) for p, q in pairs)
        for factor in (1, 257, 2**30):
            solver = FullPairSupport(tuple(factor * w for w in widths),
                                     tuple(factor * u for u in columns),
                                     tuple(factor * t for t in totals[2:]),
                                     factor * totals[0], factor * totals[1])
            assert solver.exact(query) == factor * truth
            assert solver.heap_visits <= 5 * len(widths) * solver.evaluations
            scaled_heap_visits += solver.heap_visits
            wide_checks += 1
tree_checks = 0
for length in (1, 2, 3, 7, 16, 31, 64):
    initial = [rng.randrange(1000) for _ in range(length)]
    tree = SuffixSlack(initial, 10**9)
    for trial in range(20):
        expected = initial.copy()
        for _ in range(25):
            first = rng.randrange(length)
            assert tree.suffix_min(first) == min(expected[first:])
            amount = rng.randrange(min(expected[first:]) + 1)
            tree.suffix_add(first, -amount)
            for at in range(first, length):
                expected[at] -= amount
            tree_checks += 1
        tree.reset()
        assert tree.minimum == tree.initial and not any(tree.lazy)
gc_was_enabled = gc.isenabled()
gc.disable()
try:
    temporary_solver = FullPairSupport((1, 1, 1, 1), (1, 2, 1, 2), (1, 3), 2, 0)
    tree_reference = weakref.ref(temporary_solver.tree)
    assert temporary_solver.exact((1, -1, 1, -1)) == 0
    del temporary_solver
    assert tree_reference() is None
finally:
    if gc_was_enabled:
        gc.enable()
print(json.dumps(dict(seed=SEED, source_cases=len(cases), full_pair_checks=checks,
                      relaxed_checks=relaxed_checks, evaluations=evaluations,
                      heap_visits=heap_visits, restored_nodes=restored_nodes,
                      wide_scaled_checks=wide_checks, scaled_heap_visits=scaled_heap_visits,
                      suffix_tree_checks=tree_checks,
                      tree_released_without_cyclic_gc=True,
                      strict_witness_full_support=0, result='PASS'), indent=2))
```

The persisted [finite result](full-pair-results.json) records the exercised domain.
The wide-query checks compare scaled instances with exhaustive unscaled optima.
Network integrality and dilation imply that multiplying all margins and capacities
by an integer multiplies the exact support by that integer. The checks therefore
exercise large weight magnitudes without enumerating their individual units.
It is not an asymptotic benchmark, a test on real model weights, or a novelty proof.


## 7. Independent review

**Review outcome.** The theorem now gives the exact fixed-margin pair upper bound:
\(M_{pq}^{\rm full}(x)\) is the largest possible residual score difference for
rows \(p,q\) among every integral table consistent with the stored widths, column
totals, and all row totals. It is not the score difference of the hidden source
table unless that table is fetched, and it does not establish a complete routing
policy.

I independently checked the two points that previously needed an explicit
argument. The monotone closure \(\bar g\), followed by the cap-convolution
\(h(S)=\min_{B\subseteq S}[\bar g(B)+c(S\setminus B)]\), is the needed
integral polymatroid rank. The cap \(c_j=\min(2w_j,u_j)\) keeps both the
pair capacity and the remaining-column capacity in the same family. The full
network supplies the separately constrained problem, so scalar duality restores
\(t_p,t_q\) without inventing a synthetic aggregate row. The suffix update acts
only from \(\lceil v_j/w_j\rceil\); a threshold beyond \(n\) has no cut to
update. These details make the batched greedy rule and its rollback accounting
consistent with the stated feasibility test.

I also checked the final one-evaluation scalar search. At a coefficient vector
\(c=2x-z\mathbf1\), the allocation has a feasible difference vector with
\(D=\sum_j\operatorname{sign}(c_j)\min(r_j,2w_j-r_j)\). At \(c_j=0\), the
fractional split \(p_j=q_j=r_j/2\) supplies the required support subgradient.
Thus \(\delta-D\) is a subgradient of the convex doubled objective. Its sign
keeps the correct side of the integer bracket, and comparison of the two final
adjacent endpoints preserves exactness. Caching changes the number of oracle
calls; it does not change the represented source information or the theorem.

I reran the embedded standard-library fence with that final search. It passed 252
source cases, 8,100 exact full-pair comparisons, 8,100 relaxed comparisons, 504
integer-dilation comparisons at factors \(1\), \(257\), and \(2^{30}\), and
3,500 suffix-tree/replay checks. The finite run used 21,305 primary support
evaluations, 55,268 primary heap visits, and 9,114 scaled heap visits. These are
finite operation counts from the fenced Python oracle. They do not measure peak
RAM, physical read latency, or a win over an optimized established routing method.

The \(O(n+d)\) claim is a working-state bound in machine words with the bit
charges stated in Section 5. It does not include original gate records,
coarse-score state, a query-independent guide, or work reused across every
challenger. Polymatroid greedy optimization, flow duality, and range trees are
established tools. This review therefore supports the exactness and bounded-state
claims only; novelty and a practical advantage remain unproved.


**Lifetime review.** The tree refactor changes the fence implementation, not the
allocation or scalar-search mathematics. The recursive operations are now ordinary
`SuffixSlack` methods, so no nested function retained by the tree captures the
solver or the tree itself. I reran the new weak-reference check with cyclic garbage
collection disabled: after `temporary_solver` is deleted, its tree weak reference
is empty. The full fence retained the same exactness and operation counters. This
proves immediate release for that exercised CPython object graph; it does not
measure process RSS or prove a hardware memory limit.

## 8. Primary-source and comparator challenge

[Federgruen and Groenevelt (1986)](https://business.columbia.edu/sites/default/files-efs/pubfiles/4071/federgruen_greedy_procedure.pdf)
prove greedy optimality for concave orders on polymatroids and discuss network-flow
output sets and the cost of membership checks. The full author-hosted paper was
read. It covers the optimization principle used here. Its generalized symmetric
subclass has a rank depending on one weighted subset sum; this note has not shown
that its capped complementary rank belongs to that narrower subclass.

[Groenevelt (1991)](https://www.sciencedirect.com/science/article/pii/037722179190300K)
describes two exact algorithms for separable concave polymatroid optimization,
including discrete network cases. Only the publisher abstract was available in
this review, so no implementation or complexity equivalence is inferred from it.
[Shenmaier (2003)](https://doi.org/10.1016/S0166-218X(03)00435-9)
also records the greedy characterization for separable concave integer programs.
These sources preclude calling the general greedy theorem a new mathematical result.

The bounded search did not identify this exact suffix-slack representation,
two-piece batched allocation, or its restoration schedule in those sources.
That absence leaves the specialization unclassified; it does not establish novelty.

A fair exact reference solves the original full transportation problem directly,
using the same \(w,t,u,x\), with nonzero costs only on the two distinguished rows.
It obtains the same support without original residual-table access and without
the outer scalar search. An explicit residual graph uses \(\Theta(md)\) arcs.
That is a valid implementation comparator, not a lower bound on every established
specialized method. General polymatroid algorithms supplied with the same compact
membership structure form a second required comparator. Across several challengers,
both sides must account for preparation, retained topology, and reusable state.
