# Full aggregate feasibility from row totals and shared column widths

The projected transportation certificate replaces every unexamined residual row
with one aggregate row. That replacement can admit a column total that no
collection of the omitted rows can realize. This note gives an exact test for
that missing condition when every residual entry in column \(j\) lies in
\([0,w_j]\). The test identifies candidates to discard before any original
gate row is read. It neither changes the source weights nor supplies the
ordinary calculation: a surviving winner is still resolved and fetched at
source precision.

The construction is a bounded transportation feasibility test, specialized so
that a general family of column-subset cuts becomes \(n+1\) scalar
inequalities. The network-flow argument is classical; no novelty claim is
made.

## 1. Exact omitted-row criterion

Fix the \(n\) rows not being compared. Their retained exact residual totals
are \(t_1,\ldots,t_n\), and each coordinate has the common integral capacity
\(w_j\). Write

\[
  0\leq \tau_1\leq\cdots\leq\tau_n
\]

for those totals in nondecreasing order, set

\[
  T_r=\sum_{h=1}^r\tau_h,\qquad T_0=0,\qquad T=T_n,
\]

and let \(z_j\) be the residual column amount required from the omitted rows.
For example, after proposing compared rows \(p,q\), the column identity
forces

\[
 z=u-p-q. \tag{1}
\]

**Theorem 1 — exact aggregate feasibility.** There is an integral matrix
\(e\in\mathbb Z_{\geq0}^{n\times d}\) satisfying

\[
 e_{hj}\leq w_j,\qquad
 \sum_j e_{hj}=t_h,\qquad
 \sum_h e_{hj}=z_j                                      \tag{2}
\]

if and only if

\[
 z_j\geq0,\qquad \sum_jz_j=T,\qquad
 \sum_j(z_j-sw_j)_+\leq T_{n-s}
 \quad\text{for every }s\in\{0,\ldots,n\}.               \tag{3}
\]

Here \(a_+=\max(a,0)\). In particular, the \(s=n\) inequality rejects
\(z_j>nw_j\). A zero-width coordinate must have \(z_j=0\).

**Proof.** Form the usual source--row--column--sink network. The source-to-row
and column-to-sink arcs have the exact amounts \(t_h\) and \(z_j\); each
row-to-column arc has capacity \(w_j\). The column-subset cut conditions are

\[
 z(S)\leq\sum_{h=1}^n\min(t_h,w(S))
 \quad\text{for every }S\subseteq\{1,\ldots,d\}.         \tag{4}
\]

They are sufficient by max-flow/min-cut, and integral capacities give an
integral flow. This is the bounded matrix form of Gale's feasibility theorem;
Gale explicitly records the integral-flow conclusion for integral capacities
and demands in [Gale (1957)](https://msp.org/pjm/1957/7-2/pjm-v7-n2-p04-p.pdf).

For every nonnegative integer \(a\),

\[
 \sum_h\min(t_h,a)=\min_{0\leq s\leq n}\{sa+T_{n-s}\}.    \tag{5}
\]

Choose \(s\) as the number of \(t_h\)'s strictly greater than \(a\) to attain
the equality. Substituting (5) into (4), it is enough and necessary that, for
each \(s\),

\[
 z(S)-s w(S)\leq T_{n-s}\quad\text{for every }S.         \tag{6}
\]

For fixed \(s\), the left side is maximized independently in each coordinate:
include exactly the coordinates for which \(z_j-sw_j>0\). Its maximum is the
left side of (3). Thus (3) and all cuts (4) are equivalent. \(\square\)

The theorem uses the uncapped exact total \(u\) in (1). The clipped slack
fields \(\alpha,\beta\) from the smaller guide do not determine \(u-p-q\), so
they cannot support this stronger test without additional source-derived
information.

## 2. Fast exact separation

The \(n+1\) inequalities in (3) need not all be evaluated. Reject immediately
when a width-zero coordinate has positive \(z_j\), when some \(z_j<0\), when
\(\sum_jz_j\ne T\), or when \(z_j>nw_j\). For every remaining coordinate with
\(z_j>0\), define its integer expiry

\[
 c_j=\left\lceil\frac{z_j}{w_j}\right\rceil .
\]

On any integer interval on which the active set
\(A=\{j:c_j>s\}\) is fixed, let

\[
 D(s)=\sum_{j\in A}z_j-s\sum_{j\in A}w_j-T_{n-s}.        \tag{7}
\]

This is the possible violation at \(s\). Its forward difference is

\[
 D(s+1)-D(s)=\tau_{n-s}-\sum_{j\in A}w_j.                 \tag{8}
\]

As \(s\) increases, the first term in (8) is nonincreasing. Hence \(D\) is
discretely concave on that interval. Put

\[
 q_A=\#\{h:\tau_h>\textstyle\sum_{j\in A}w_j\}.
\]

The maximum on an active interval \([L,R]\) is reached at
\(\operatorname{clamp}(q_A,L,R)\). Equal totals make a flat maximum; the
chosen point remains valid.

Sort the \(c_j\)'s once, removing all coordinates with the same expiry
together. Check the clamped point in each of at most \(d+1\) intervals
intersecting \(0,\ldots,n\). A sorted \(\tau\) list and prefix array answer
\(q_A\) by binary search and \(T_{n-s}\) by index. The resulting exact
feasibility check costs

\[
 O(n\log n+d\log d+d\log n)
\]

arithmetic after \(z\) is formed, and \(O(n+d)\) mutable words. The \(n\log n\)
sort is a per-omitted-set preprocessing cost. Reusing it across changing
compared pairs needs a separately derived removal-aware structure; this note
does not claim that reuse.

Let \(W=\sum_jw_j\). Each stored total, prefix total, \(z_j\), and positive
sum \(F(s)=\sum_j(z_j-sw_j)_+\) needs
\(\lceil\log_2(T+1)\rceil\) bits; a signed \(D(s)\) needs one additional sign
bit. The active width sum needs \(\lceil\log_2(W+1)\rceil\) bits, and direct
evaluation of \(sW_A\) needs
\(\lceil\log_2(nW+1)\rceil\) bits before subtraction. The early coordinate
check makes every stored expiry lie in \([1,n]\). A resident implementation
must charge the uncapped \(u_j\), the \(t_h\) data or their
sorted-and-identifiable equivalent, widths, event/order metadata, and this
scratch. It must also separately charge the original gate rows and payloads
fetched after the certificate.

## 3. A cut that can sharpen support before a source read

The criterion gives more than a yes/no completion check. If (3) fails at
\((s,S)\), where

\[
 S=\{j:z_j-sw_j>0\},
\]

then every full completion satisfies the valid omitted-row inequality

\[
 (p+q)(S)\geq u(S)-s w(S)-T_{n-s}.                        \tag{9}
\]

It follows directly by substituting \(z=u-p-q\) into (6). Intersecting a
projected pair optimization with (9) can lower its support bound. This is an
exact valid inequality for the full transportation polytope. It is not a
claim of a complete support solver: further cuts may still be required.

Here is a strict finite witness. Let the four residual rows, in their original
source order, be

\[
 E=
 \begin{pmatrix}
  0&0&0&0\\
  0&0&1&1\\
  0&1&0&0\\
  1&1&0&1
 \end{pmatrix},
\quad
 w=(1,1,1,1),
\quad
 u=(1,2,1,2).
\]

Compare row one \(p\) with the zero anchor \(q\), and take
\(x=(1,-1,1,-1)\). The two omitted row totals are \(1,3\). The projected
aggregate permits \(p=(1,0,1,0)\), whose support is two. But with \(s=1\) and
\(S=\{2,4\}\), (9) says \(p_2+p_4\geq1\). Because
\(\sum_jp_j=2\),

\[
 x^Tp=2-2(p_2+p_4)\leq0.                                 \tag{10}
\]

The full aggregate maximum is therefore zero, attained by the actual source
row \(p=(0,0,1,1)\). Thus this one cut eliminates a projected false candidate
without reading its original gate row. If a larger routing construction has
already reduced the same query to original scores \((2,2,-1,-1)\), with the
least-index anchor at zero, the projected bound retains row one on a tie and
this cut excludes it. The original gate source remains authoritative for every
row that survives.

## 4. Exact binary one-row support, without a transportation matrix

There is a stronger specialization when \(w_j=1\) for every coordinate and
only one candidate row \(p\) is variable. The remaining \(n\) rows have totals
\(t_h\), and the complete column total is \(u\), so their demanded aggregate is
\(z=u-p\). This does not cover a general pair comparison; it is an exact
single-row support problem.

**Theorem 2 — nested quota representation.** Assume the source margins satisfy
\(\sum_j u_j=t_i+\sum_h t_h\). Let \(p\) be binary, satisfy
\(p_j\leq u_j\), and have \(\sum_jp_j=t_i\). Define

\[
 J_s=\{j:u_j\geq s+1\},\qquad
 r_s=\sum_j(u_j-s)_+-T_{n-s}.
\]

Then that row \(p\) has a full completion by the omitted rows if and only if

\[
 \sum_{j\in J_s}p_j\geq r_s\quad(0\leq s\leq n).         \tag{11}
\]

**Proof.** In Theorem 1 substitute \(z=u-p\). Since \(p_j\in\{0,1\}\),

\[
 (u_j-p_j-s)_+=
 \begin{cases}
   u_j-s-p_j,&u_j\geq s+1,\\
   0,&u_j\leq s.
\end{cases}
\]

The condition \(p_j\leq u_j\) gives \(z_j\geq0\), and
\(\sum_j u_j=T+t_i\) gives \(\sum_jz_j=T\). Rearranging the remaining
inequalities in (3) gives exactly (11). The equivalence therefore inherits
both directions and integral completion from Theorem 1. \(\square\)

The \(J_s\)'s are nested after columns are ordered by decreasing \(u_j\).
This turns the full one-row support calculation into a weighted chain-quota
selection, not an \(n\)-by-\(d\) flow.

Set \(y_j=1-p_j\). Then \(\sum_jy_j=d-t_i\), and (11) becomes prefix upper
quotas

\[
 \sum_{j\in J_s}y_j\leq c_s,\qquad
 c_s=|J_s|-\sum_j(u_j-s)_++T_{n-s}.                       \tag{12}
\]

To maximize \(x^Tp=\sum_jx_j-x^Ty\), minimize \(x^Ty\) over the binary
vectors satisfying (12) and the final cardinality. Coordinates with \(u_j=0\)
force \(p_j=0\), hence force \(y_j=1\). Insert those forced terms first and
reduce the selectable final capacity by their count. Scan the remaining
coordinates in decreasing \(u_j\), add each \(x_j\) to a max-cost heap, and,
at every distinct constrained prefix, remove its largest \(x_j\)'s until the
heap size is at most that prefix's \(c_s\). At the all-coordinate constraint,
use the reduced final capacity. The heap and forced terms then contain a
minimum-cost feasible \(y\).

This is the greedy algorithm for a nested laminar matroid. A direct exchange
argument is more precise. The constraints on a processed prefix define a
chain matroid. Adding the next coordinate is a direct sum with a singleton
matroid. Imposing that prefix's quota truncates the resulting matroid.
The heap rule retains the least-cost greedy basis after each truncation, so
induction over the prefixes proves its optimality. The final quota fixes its
cardinality at \(d-t_i\). This argument permits negative query coefficients;
the rank, rather than a sign condition, fixes the selected count.

It is unnecessary to retain every \(s\). On an interval where \(J_s\) is one
fixed prefix of length \(r\), let \(U=\sum_{j\in J_s}u_j\). Equation (12) is

\[
 c_s=(s+1)r-U+T_{n-s}.                                    \tag{13}
\]

Its forward difference is \(r-\tau_{n-s}\), which is nondecreasing in \(s\).
Thus \(c_s\) is discretely convex, and only its minimum in that interval
constrains the same prefix. The minimum is attained at the interval-clamped
value

\[
 \#\{a:\tau_a>r\}.                                        \tag{14}
\]

The ordered \(u\) values define at most \(d\) prefixes. A sorted omitted-total
array and prefix sums therefore derive the effective quotas in
\(O(n\log n+d\log n+d\log d)\) arithmetic, then solve the support by
\(O(d\log d)\) heap work and \(O(n+d)\) words. This resource claim includes
the row-total sort and the heap, but not a removal-aware reuse scheme across
different candidate rows.

The strict witness above is already an example: (11) at \(s=1\) requires
\(p_2+p_4\geq1\), and the chain-quota solver returns support zero rather than
the projected support two. This is a concrete exact relevance refinement for
the binary, single-candidate class. It is not a generic replacement for
pairwise or arbitrary-width transportation.

## 5. Reproducible finite fence

The following standard-library fence exhaustively compares (3) to explicit
matrices in a small case, then checks the strict witness. It exercises 29,664
matching-total aggregate cases for \(n=d=3\).

~~~python
from itertools import product

def row_vectors(total, widths):
    return [v for v in product(*(range(w + 1) for w in widths))
            if sum(v) == total]

def cut_feasible(z, totals, widths):
    if any(value < 0 for value in z) or sum(z) != sum(totals):
        return False
    if any(width == 0 and value for value, width in zip(z, widths)):
        return False
    tau = sorted(totals)
    prefix = [0]
    for value in tau:
        prefix.append(prefix[-1] + value)
    n = len(totals)
    return all(sum(max(0, value - s * width)
                   for value, width in zip(z, widths)) <= prefix[n - s]
               for s in range(n + 1))

checks = 0
for widths in product(range(3), repeat=3):
    whole = sum(widths)
    for totals in product(range(whole + 1), repeat=3):
        rows = [row_vectors(total, widths) for total in totals]
        actual = {tuple(map(sum, zip(*matrix)))
                  for matrix in product(*rows)}
        for z in product(*(range(3 * width + 1) for width in widths)):
            if sum(z) != sum(totals):
                continue
            checks += 1
            assert cut_feasible(z, totals, widths) == (z in actual)

E = ((0, 0, 0, 0), (0, 0, 1, 1), (0, 1, 0, 0), (1, 1, 0, 1))
widths = (1, 1, 1, 1)
u = tuple(map(sum, zip(*E)))
p_candidates = row_vectors(2, widths)
projected = max(sum(x * value for x, value in zip((1, -1, 1, -1), p))
                for p in p_candidates
                if all(0 <= u_j - p_j <= 2 for u_j, p_j in zip(u, p)))
full = max(sum(x * value for x, value in zip((1, -1, 1, -1), p))
           for p in p_candidates
           if cut_feasible(tuple(u_j - p_j for u_j, p_j in zip(u, p)),
                           (1, 3), widths))
assert projected == 2
assert full == 0
assert not cut_feasible((0, 2, 0, 2), (1, 3), widths)
print({"aggregate_cases": checks, "projected_support": projected,
       "full_support": full, "result": "PASS"})
~~~

The following independent binary fence checks both the quota equivalence and
the heap solver over every three-row binary source with four columns and every
ternary query.

~~~python
from itertools import product
from heapq import heappush, heappop

def cut_feasible(z, totals, widths):
    if any(value < 0 for value in z) or sum(z) != sum(totals):
        return False
    tau = sorted(totals)
    prefix = [0]
    for value in tau:
        prefix.append(prefix[-1] + value)
    n = len(totals)
    return all(sum(max(0, value - s * width)
                   for value, width in zip(z, widths)) <= prefix[n - s]
               for s in range(n + 1))

def quota_feasible(p, u, omitted):
    if any(value > total for value, total in zip(p, u)):
        return False
    tau = sorted(omitted)
    prefix = [0]
    for value in tau:
        prefix.append(prefix[-1] + value)
    n = len(omitted)
    for s in range(n + 1):
        chosen = sum(value for value, total in zip(p, u) if total >= s + 1)
        required = sum(max(0, total - s) for total in u) - prefix[n - s]
        if chosen < required:
            return False
    return True

def heap_support(u, omitted, row_total, query):
    d, n = len(u), len(omitted)
    tau = sorted(omitted)
    prefix = [0]
    for value in tau:
        prefix.append(prefix[-1] + value)
    forced = {j for j, total in enumerate(u) if total == 0}
    capacity = d - row_total - len(forced)
    order = sorted((j for j, total in enumerate(u) if total > 0),
                   key=lambda j: (-u[j], j))
    quotas = {}
    for s in range(n + 1):
        active = tuple(j for j in order if u[j] >= s + 1)
        quota = len(active) - sum(max(0, total - s) for total in u) + prefix[n - s]
        quotas[active] = min(quotas.get(active, quota), quota)
    heap = []
    for at, j in enumerate(order, 1):
        heappush(heap, (-query[j], j))
        while len(heap) > quotas.get(tuple(order[:at]), capacity):
            heappop(heap)
    while len(heap) > capacity:
        heappop(heap)
    assert len(heap) == capacity
    omitted_by_p = forced | {j for _, j in heap}
    p = tuple(0 if j in omitted_by_p else 1 for j in range(d))
    return sum(coefficient * value for coefficient, value in zip(query, p)), p

binary_checks = 0
for source in product(product((0, 1), repeat=4), repeat=3):
    candidate, *other_rows = source
    u = tuple(map(sum, zip(*source)))
    totals = tuple(map(sum, other_rows))
    candidate_total = sum(candidate)
    for query in product((-1, 0, 1), repeat=4):
        feasible = []
        for p in product((0, 1), repeat=4):
            if sum(p) != candidate_total or any(value > total for value, total in zip(p, u)):
                continue
            full = cut_feasible(tuple(total - value for total, value in zip(u, p)),
                                totals, (1, 1, 1, 1))
            assert full == quota_feasible(p, u, totals)
            if full:
                feasible.append((sum(value * coefficient
                                     for value, coefficient in zip(p, query)), p))
        expected = max(feasible)
        found, selected = heap_support(u, totals, candidate_total, query)
        assert found == expected[0]
        assert quota_feasible(selected, u, totals)
        binary_checks += 1
print({"binary_sources": 4096, "queries_per_source": 81,
       "support_checks": binary_checks, "result": "PASS"})
~~~

The declared results are:

~~~text
{'aggregate_cases': 29664, 'projected_support': 2, 'full_support': 0, 'result': 'PASS'}
{'binary_sources': 4096, 'queries_per_source': 81, 'support_checks': 331776, 'result': 'PASS'}
~~~

## 6. Scope and classical boundary

The reduction is a useful interpretation refinement only when the guide can
afford exact omitted-row totals and uncapped column totals, and when avoiding
an original gate read offsets its added resident state and arithmetic. It does
not establish a total-RAM frontier, a physical read-latency gain, or a result
for arbitrary floating-point gate arithmetic. It applies to the declared
integer residual construction and resolves relevance; original source records
are still fetched byte-exactly and passed to ordinary arithmetic.

The underlying bounded-table feasibility and integral-flow facts are classical.
Gale's 1957 cut theorem is the direct source for the proof. Brualdi's
[1983 article](https://www.sciencedirect.com/science/article/pii/0012365X83900535)
is a directly relevant network-flow comparison by title, but this note makes
no detailed attribution beyond that verified bibliographic connection. The
contribution here is only the explicit specialization, its fast scalar
separation schedule, and the finite routing witness; their originality has
not been established.
