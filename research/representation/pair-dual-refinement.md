# Scalar dual recovery of projected pair totals

The pair-total interpreter is fast because it drops the separate residual totals of
the compared rows. That omission can matter: it gives an upper bound of two on a
case whose projected bound is zero. This note restores the missing difference of
those totals with one scalar multiplier. For the declared three-row projected
transportation model, the resulting minimum is exactly the projected bound. It
keeps the source gate and payload external, and it supplies only a safe relevance
certificate before those original records are read.

This is an exact specialization of linear-programming duality and parametric
resource allocation, not an originality claim. The contribution here is a
source-guide formulation, an integer multiplier search, and a bounded check of
the stated construction.

## 1. Source, guide, and the compressed pair constraints

Let the immutable external source contain arbitrary integer gate rows
(a_i\in\mathbb Z^d), along with original payload records. The runtime already
has an integer query (x\in\mathbb Z^d), and the required region is the
least-index winner

\[
 \nu_A(x)=\min\operatorname*{arg\,max}_i a_i^T x.
 \tag{1}
\]

A compiler fixes an integer step \(\Delta>0\) and stores a derived guide from

\[
 a_i=c+\Delta Q_i+e_i,\qquad 0\le e_{ij}\le w_j.
 \tag{2}
\]

The common row \(c\) cancels in (1). It is not needed at runtime. The guide
stores \(Q\), the widths \(w\), and the residual row totals

\[
 t_i=\sum_j e_{ij}.
 \tag{3}
\]

The full source retains \(a_i\) and its payload. The guide never substitutes
for a gate score used by the later ordinary calculation.

For a residual row of total \(t_i\), define \(W=\sum_jw_j\) and

\[
 \ell_{ij}=\max\{0,t_i-W+w_j\},\qquad
 v_{ij}=\min\{w_j,t_i\},\qquad r_{ij}=v_{ij}-\ell_{ij}.
 \tag{4}
\]

The earlier projected construction also used the source-derived column total
\(u_j=\sum_i e_{ij}\) and the aggregate envelope
\(L_j=\sum_i\ell_{ij}\), \(V_j=\sum_i v_{ij}\). For every compared pair, only
the following capped slacks are needed:

\[
 \alpha_j=\min\{2w_j,u_j-L_j\},\qquad
 \beta_j=\min\{2w_j,V_j-u_j\}.
 \tag{5}
\]

For challenger \(i\) and anchor \(k\), write \(p=e_i\), \(q=e_k\), and
\(s=p+q\). The projected aggregate-row constraints are exactly

\[
 \begin{aligned}
 a_{ikj}&=\ell_{ij}+\ell_{kj}
       +\max\{0,r_{ij}+r_{kj}-\beta_j\},\\
 b_{ikj}&=\ell_{ij}+\ell_{kj}
       +\min\{r_{ij}+r_{kj},\alpha_j\},\\
 a_{ikj}&\le s_j\le b_{ikj},\qquad
 \sum_j s_j=t_i+t_k.
 \end{aligned}
 \tag{6}
\]

To check (6), substitute \(V_j-u_j=\beta_j\) and \(u_j-L_j=\alpha_j\)
before the caps into the earlier formula

\[
 \max\{\ell_i+\ell_k,u-V+v_i+v_k\}\le s
 \le\min\{v_i+v_k,u-L+\ell_i+\ell_k\}.
 \tag{7}
\]

No cap changes (6), because \(0\le r_{ij}+r_{kj}\le2w_j\). Thus values of
\(u_j-L_j\) or \(V_j-u_j\) above \(2w_j\) have the same effect as the
neutral cap \(2w_j\). The capped slacks preserve these eliminated pair
constraints only. They do not reconstruct \(u_j\), \(L_j\), \(V_j\), or an
aggregate row; a different flow interpreter must retain those fields or solve
the eliminated \(p,q\) network used below.

For each nonzero width, encode \(\alpha_j\) and \(\beta_j\) with one neutral
flag each. When a value is below \(2w_j\), its payload takes
\(\lceil\log_2(2w_j)\rceil\) bits; when it equals \(2w_j\), the flag alone
means “neutral cap.” The replacement for \((u,L,V)\) therefore occupies exactly

\[
 2\,|\{j:w_j>0\}|+
 \sum_{j:w_j>0}
 \left(\mathbf1_{\alpha_j<2w_j}+\mathbf1_{\beta_j<2w_j}\right)
 \lceil\log_2(2w_j)\rceil
 \tag{8}
\]

bits, apart from the existing packed \(Q,w,t\) fields and the guide header.
This is an exact field count, not a complete cartridge-byte claim.

## 2. The pair-total relaxation and its missing equality

For a real coefficient vector \(y\), let \(\Psi_{ik}(y)\) maximize
\(y^T(p-q)\) subject to (6), the coordinate split bounds

\[
 \max\{\ell_{ij},s_j-v_{kj}\}\le p_j\le
 \min\{v_{ij},s_j-\ell_{kj}\},\qquad q_j=s_j-p_j,
 \tag{9}
\]

and integer variables. This is precisely the pair-total support problem. At a
fixed \(s_j\), it assigns the whole split toward the row favoured by the sign
of \(y_j\). Each coordinate has a rising and falling marginal segment, with
slopes \(+|y_j|\) and \(-|y_j|\), so the two-segment greedy calculation returns
\(\Psi_{ik}(y)\) exactly.

The projected transportation bound restores the two individual row totals:

\[
 M^{\rm proj}_{ik}(x)=\max x^T(p-q)
 \quad\text{subject to (6), (9),}\quad
 \sum_jp_j=t_i,\quad\sum_jq_j=t_k.
 \tag{10}
\]

Because \(\sum_js_j=t_i+t_k\), the two equalities in (10) are equivalent to
one equality

\[
 \mathbf1^T(p-q)=\delta_{ik},\qquad \delta_{ik}=t_i-t_k.
 \tag{11}
\]

The pair-total construction loses exactly (11). It does not lose a vector of
row information.

## 3. Exact scalar-dual theorem

**Theorem 1.** For every integer guide satisfying (2)–(6), every pair \((i,k)\),
and every real query \(x\),

\[
 M^{\rm proj}_{ik}(x)=
 \min_{\mu\in\mathbb R}
 \left\{\mu\delta_{ik}+\Psi_{ik}(x-\mu\mathbf1)\right\}.
 \tag{12}
\]

**Proof.** Let \(R\) be the continuous polytope defined by (6) and (9), with
the single sum \(\sum s=t_i+t_k\), and let \(D=p-q\). Adding (11) gives the
polytope in (10).

Both relevant polytopes are integral without reconstructing \(u,L,V\) or an
aggregate vector. For \(R\), make one pair-supply node of supply \(t_i+t_k\).
It has two parallel arcs, labelled \(p_j\) and \(q_j\), to each coordinate node,
with bounds \( [\ell_{ij},v_{ij}] \) and \( [\ell_{kj},v_{kj}] \). Each coordinate
node has an arc to the sink with bounds \( [a_{ikj},b_{ikj}] \). For (10),
split the supply node into a \(p\) source of supply \(t_i\) and a \(q\) source
of supply \(t_k\), leaving the coordinate-to-sink arcs unchanged. These are
bounded network-flow polytopes with integral data. Their constraint matrices are
totally unimodular, so the continuous and integer optima agree.

Relax (11) with an unrestricted multiplier \(\mu\). Its Lagrangian objective is

\[
 x^TD-\mu(\mathbf1^TD-\delta_{ik})
 =\mu\delta_{ik}+(x-\mu\mathbf1)^TD.
 \tag{13}
\]

Linear-programming strong duality gives the minimum over \(\mu\) of the maximum
over \(R\). By integrality and the exact two-segment greedy calculation, that
maximum is \(\Psi_{ik}(x-\mu\mathbf1)\). This proves (12). \(\square\)

This proof is narrower than a full source transportation claim. The aggregate
row remains a relaxation of all noncompared source rows, so (12) equals the
projected certificate and may still be larger than the true maximum residual
score difference.

## 4. Finite exact multiplier search

Let \(z=2\mu\). For integer \(x\), define the integer-valued function

\[
 F_{ik}(z)=z\delta_{ik}+\Psi_{ik}(2x-z\mathbf1).
 \tag{14}
\]

Homogeneity of \(\Psi\) gives \(F_{ik}(z)=2\bigl(\mu\delta_{ik}+
\Psi_{ik}(x-\mu\mathbf1)\bigr)\). Consequently,

\[
 M^{\rm proj}_{ik}(x)=\frac12
 \min_{z\in\mathbb Z}F_{ik}(z).
 \tag{15}
\]

The division is exact at the minimum by Theorem 1 because the projected
integer optimum is doubled. A nonminimal \(F_{ik}\) can be odd. Do not round
an arbitrary nonminimal value.

The only real breakpoints of (12) occur at

\[
 \mu=x_j\quad\text{or}\quad \mu=\frac{x_j+x_h}{2}.
 \tag{16}
\]

Between two consecutive values in (16), every sign of \(x_j-\mu\) is fixed and
the ordering of all \(|x_j-\mu|\) is fixed. The pair-total greedy routine then
uses the same segment capacities in the same order, hence produces one affine
function on that interval. A minimum occurs at an endpoint, or the whole
interval is flat and either endpoint has the same value. Twice every value in
(16) is an integer. The infinite rays outside the smallest and largest \(x_j\)
need no extra candidate. Evaluating the actual feasible source pair gives a
finite lower bound on (12) for every \(\mu\), so neither affine ray can fall
without bound. A linear ray bounded below has its minimum at the endpoint or is
constant there.

There is no need to materialize the \(O(d^2)\) values in (16). Equation (14) is
the maximum of affine functions of \(z\), plus an affine term, and is therefore
discretely convex. Its exact minimum lies in

\[
 2\min_jx_j\le z\le2\max_jx_j.
 \tag{17}
\]

The first integer \(z\) with nonnegative forward difference is found by:

```text
lo = 2 * min(x)
hi = 2 * max(x)
while lo < hi:
    middle = (lo + hi) // 2
    if F(middle + 1) >= F(middle):
        hi = middle
    else:
        lo = middle + 1
return F(lo) / 2
```

This handles negative coefficients and ties without a floating-point comparison.
A half-integer multiplier is necessary in general. For

\[
 e=\bigl((2,0,1),(2,3,0),(0,3,0)\bigr),\quad
 x=(-2,-1,-1),\quad i=1,\quad k=0,
 \tag{18}
\]

the optimum has \(z=-3\), hence \(\mu=-3/2\), and the projected value is
\(-1\). Restricting \(\mu\) to integers would miss this minimizer.

## 5. Interpreter costs and exact retrieval

Sort the coordinates by \(x_j\) once. For a trial \(z\), form the order of
\(|2x_j-z|\) by merging the two monotone arms on either side of \(z/2\); this
costs \(O(d)\) comparisons and one \(O(d)\)-word index buffer. It avoids a new
sort at every multiplier value. The pair-total greedy routine then streams a
compared pair in \(O(d)\) arithmetic using that shared order.

Let

\[
 b_x=\left\lceil\log_2\bigl(2(\max_jx_j-\min_jx_j)+1\bigr)\right\rceil.
 \tag{19}
\]

Sequentially refining all \(m-1\) challengers costs
\(O(d\log d+m d(1+b_x))\) arithmetic and \(O(d)\) mutable words, beyond reading
or scanning the existing guide. The binary paths, and usually the trial orders,
can differ by challenger because their capacities and \(\delta_{ik}\) differ.
The sorted query and the two-arm order procedure are shared; this derivation
does not prove a common multiplier sweep for all challengers.

The word width must hold query products, capacities, and the values in (14).
For example, a safe count is \(O(\log(1+W\|x\|_\infty))\) bits for the
residual objective part, with separate charged width for the quotient dot
products. This is a working-word bound, not a byte measurement.

For each challenger use

\[
 \Delta(Q_i-Q_k)^Tx+M^{\rm proj}_{ik}(x)
 \tag{20}
\]

as an upper bound on its exact source-score difference. Retain the anchor and
any challenger whose bound is positive, or whose bound is zero and whose index
is smaller than the anchor. If one row remains, it is already the least-index
winner and no original gate record is read. Otherwise retrieve only the
retained original gate records, calculate their exact scores under (1), apply
the least-index tie rule, and retrieve that winner's original payload for the
normal calculation. The guide supplies relevance; it does not supply the
calculation result.

A guide generation is valid only for the immutable source generation from which
\(Q,w,t,\alpha,\beta\) were compiled. Changing any source gate row can change
all five guide components, including the global slacks. A generation digest on
the guide and on every source record is therefore required; a mismatch rejects
the guide rather than applying a stale certificate.

## 6. Bounded executable fence

The fence below enumerates the projected transportation polytope on small
integer sources, compares it with the scalar-dual result, checks the finite
breakpoint set, and checks containment of the actual source residual. It also
includes the counterexample in which bare pair-total support is loose.

```python
from itertools import product
from random import Random


def summaries(residual, width):
    totals = tuple(map(sum, residual))
    columns = tuple(map(sum, zip(*residual)))
    whole = sum(width)
    lower = tuple(tuple(max(0, total - whole + width_j) for width_j in width)
                  for total in totals)
    upper = tuple(tuple(min(width_j, total) for width_j in width)
                  for total in totals)
    return totals, columns, lower, upper, tuple(map(sum, zip(*lower))), tuple(map(sum, zip(*upper)))


def pair_segments(width, summary, i, k, query):
    totals, columns, lower, upper, all_lower, all_upper = summary
    segments = []
    for j, coefficient in enumerate(query):
        a = max(lower[i][j] + lower[k][j],
                columns[j] - all_upper[j] + upper[i][j] + upper[k][j])
        b = min(upper[i][j] + upper[k][j],
                columns[j] - all_lower[j] + lower[i][j] + lower[k][j])
        alpha = min(2 * width[j], columns[j] - all_lower[j])
        beta = min(2 * width[j], all_upper[j] - columns[j])
        range_sum = ((upper[i][j] - lower[i][j]) +
                     (upper[k][j] - lower[k][j]))
        assert a == lower[i][j] + lower[k][j] + max(0, range_sum - beta)
        assert b == lower[i][j] + lower[k][j] + min(range_sum, alpha)
        favored, other = ((upper[i][j], lower[k][j]) if coefficient >= 0
                           else (upper[k][j], lower[i][j]))
        segments.append((a, b, favored, other))
    assert sum(a for a, _, _, _ in segments) <= totals[i] + totals[k] <= sum(b for _, b, _, _ in segments)
    return segments


def pair_support(width, summary, i, k, query, order=None):
    totals = summary[0]
    segments = pair_segments(width, summary, i, k, query)
    value = sum(abs(x) * min(2 * favored - a, a - 2 * other)
                for (a, _, favored, other), x in zip(segments, query))
    remaining = totals[i] + totals[k] - sum(a for a, _, _, _ in segments)
    if order is None:
        order = sorted(range(len(query)), key=lambda j: abs(query[j]))
    for rising, indices in ((True, reversed(order)), (False, iter(order))):
        for j in indices:
            a, b, favored, other = segments[j]
            rising_capacity = max(0, min(b, favored + other) - a)
            capacity = rising_capacity if rising else b - a - rising_capacity
            take = min(remaining, capacity)
            value += take * abs(query[j]) * (1 if rising else -1)
            remaining -= take
    assert remaining == 0
    return value


def projected_support(width, summary, i, k, query):
    totals, columns, lower, upper, all_lower, all_upper = summary
    values = []
    for p in product(*(range(lower[i][j], upper[i][j] + 1) for j in range(len(width)))):
        if sum(p) != totals[i]:
            continue
        for q in product(*(range(lower[k][j], upper[k][j] + 1) for j in range(len(width)))):
            if sum(q) != totals[k]:
                continue
            z = tuple(columns[j] - p[j] - q[j] for j in range(len(width)))
            if all(all_lower[j] - lower[i][j] - lower[k][j] <= z[j] <=
                   all_upper[j] - upper[i][j] - upper[k][j] for j in range(len(width))):
                values.append(sum(query[j] * (p[j] - q[j]) for j in range(len(width))))
    assert values
    return max(values)


def shifted_absolute_order(query, two_mu, order_by_query):
    split = 0
    while split < len(order_by_query) and 2 * query[order_by_query[split]] < two_mu:
        split += 1
    left, right, order = split - 1, split, []
    while left >= 0 or right < len(order_by_query):
        left_distance = (abs(2 * query[order_by_query[left]] - two_mu)
                         if left >= 0 else None)
        right_distance = (abs(2 * query[order_by_query[right]] - two_mu)
                          if right < len(order_by_query) else None)
        if right_distance is None or (left_distance is not None and left_distance <= right_distance):
            order.append(order_by_query[left])
            left -= 1
        else:
            order.append(order_by_query[right])
            right += 1
    return order


def dual_search(width, summary, i, k, query, order_by_query=None):
    delta = summary[0][i] - summary[0][k]
    lo, hi = 2 * min(query), 2 * max(query)
    if order_by_query is None:
        order_by_query = sorted(range(len(query)), key=lambda j: (query[j], j))

    def objective(two_mu):
        shifted = tuple(2 * x - two_mu for x in query)
        order = shifted_absolute_order(query, two_mu, order_by_query)
        return two_mu * delta + pair_support(width, summary, i, k, shifted, order)

    while lo < hi:
        middle = (lo + hi) // 2
        if objective(middle + 1) >= objective(middle):
            hi = middle
        else:
            lo = middle + 1
    return objective(lo), lo


def finite_breakpoint_minimum(width, summary, i, k, query):
    delta = summary[0][i] - summary[0][k]
    candidates = {2 * x for x in query}
    candidates |= {left + right for left in query for right in query}
    return min(z * delta + pair_support(width, summary, i, k,
                                         tuple(2 * x - z for x in query))
               for z in candidates)


loose = ((0, 1), (1, 0), (0, 0))
loose_summary = summaries(loose, (1, 1))
assert pair_support((1, 1), loose_summary, 1, 0, (1, 1)) == 2
assert projected_support((1, 1), loose_summary, 1, 0, (1, 1)) == 0
assert dual_search((1, 1), loose_summary, 1, 0, (1, 1)) == (0, 2)

half_step = ((2, 0, 1), (2, 3, 0), (0, 3, 0))
half_summary = summaries(half_step, (2, 3, 1))
assert dual_search((2, 3, 1), half_summary, 1, 0, (-2, -1, -1)) == (-2, -3)

random = Random(20260920)
checks = 0
for _ in range(180):
    rows, dimensions = 3, random.choice((2, 3))
    raw = [[random.randrange(4) for _ in range(dimensions)] for _ in range(rows)]
    minimum = list(map(min, zip(*raw)))
    residual = tuple(tuple(value - minimum[j] for j, value in enumerate(row)) for row in raw)
    width = tuple(map(max, zip(*residual)))
    summary = summaries(residual, width)
    for query in product(range(-2, 3), repeat=dimensions):
        order_by_query = sorted(range(dimensions), key=lambda j: (query[j], j))
        for i in range(1, rows):
            direct = projected_support(width, summary, i, 0, query)
            doubled, two_mu = dual_search(width, summary, i, 0, query, order_by_query)
            actual = sum((residual[i][j] - residual[0][j]) * query[j] for j in range(dimensions))
            assert actual <= direct
            assert doubled == 2 * direct, (residual, width, query, i, direct, doubled, two_mu)
            assert doubled == finite_breakpoint_minimum(width, summary, i, 0, query)
            checks += 1
print({'seed': 20260920, 'projected_dual_checks': checks, 'result': 'PASS'})
```

Executed with the repository Python interpreter, this prints:

```text
{'seed': 20260920, 'projected_dual_checks': 28200, 'result': 'PASS'}
```

The `dual_search` routine executes the two-arm order merge, but it holds small
toy summaries in memory. `projected_support` and `finite_breakpoint_minimum`
are enumerative oracles, not the streaming interpreter. The fence does not
measure physical I/O and does not establish a result beyond its finite source
and query domain.

## 7. Comparator, collision check, and remaining boundary

The strongest directly comparable established method is a specialized
single-side-constraint network dual or a separable resource-allocation solver,
not a generic dense min-cost-flow implementation. Bryson's accessible primary
abstract for [the 1993 network-dual paper](https://www.sciencedirect.com/science/article/pii/030505489390017D)
explicitly describes solving network Lagrangian relaxations through parametric
programming. Its references identify the earlier 1991 single-side-constraint paper;
that earlier paper's full text was not accessible in the parent source check.
The checked material does not establish this source-guide specialization or the
doubled half-grid search. Vidal, Gribel, and Jaillet's [primary 2018 resource-allocation paper](https://doi.org/10.1287/ijoo.2018.0004)
also gives exact algorithms for integer resource allocation with a global sum
and nested bounds. These sources establish the broader multiplier and specialized
optimization approaches; they do not establish the particular half-grid derivation here.

For exact inner-product filtering, Li, Chan, Yiu, and Mamoulis's
[FEXIPRO paper](https://www4.comp.polyu.edu.hk/~csmlyiu/conf/SIGMOD17_fexipro.pdf)
already gives a different exact filter-and-refine route using transformed and
integer-approximated vectors. This construction does not supersede that class;
it adds a source-correlation certificate to the declared phase guide.

The result proved here is a strict mathematical improvement over bare
pair-total support: it equals the stronger projected bound for every declared
pair, including the former loose example. Its extra work has a real tradeoff:
\(b_x\) dual evaluations per challenger can lose to an optimized specialized
transportation or resource-allocation solver, and the guide still requires an
\(m\)-row scan unless a separate representation locates candidate rows. No
novelty, global best-method, physical-read, or end-to-end latency claim follows.

## 8. Independent review

I found the scalar-dual proof sound for the declared projected transportation
model. The two separate row totals reduce to the one difference equality
\(\mathbf1^T(p-q)=t_i-t_k\) because the pair-total constraint already fixes
\(\sum_j(p_j+q_j)\). The described bounded networks have integral lower and
upper capacities, so their continuous linear-program optima equal their
integer optima. Lagrangian duality then gives (12); the aggregate row remains
the stated relaxation of all noncompared source rows.

The review found and the parent corrected one domain mismatch: Section 2 now defines
\(\Psi_{ik}(y)\) for real coefficient vectors, as Theorem 1 requires when it applies
the function to \(x-\mu\mathbf1\). The two-segment greedy proof works unchanged.
The executable multiplier search retains integer coefficients throughout.

The doubled grid is correct. A fixed greedy order changes only when a shifted
coordinate crosses zero or two shifted absolute values tie, giving candidate
endpoints \(z=2x_j\) and \(z=x_j+x_h\). On each intervening interval the
dual objective is affine; a finite lower bound supplied by the feasible
projected source pair prevents either outer ray from falling indefinitely.
Thus a minimizer lies on the integer doubled grid. Since \(F\) is a maximum
of affine functions plus an affine term, its forward differences are
nondecreasing. The binary search returns the first minimizer, including a
flat interval or a tied endpoint. Its final division is exact only at that
minimum, as the note states.

The two-arm merge returns nondecreasing
\(\lvert2x_j-z\rvert\). Equal distances may be taken from either arm:
equal-slope greedy segments have the same objective, while a zero coefficient
has zero contribution regardless of the provisional favored-row convention.
The executable fence now accepts a supplied sorted query order and computes
that order once per query before checking its two challengers, matching the
shared-sort work claim. I reran the documented fence after this correction:
28,200 projected-dual oracle comparisons passed.

The \(O(d\log d+md(1+b_x))\) arithmetic and \(O(d)\)-word scratch claims are
sound for sequential challenger refinement, with the sorted query order and
one trial-order buffer counted. They are not packed-byte, simultaneous-pair,
or physical-I/O measurements. The cited single-side-constraint and
resource-allocation literature is the appropriate classical boundary; this
review finds no support for a novelty or best-method claim beyond the exact
projected-bound specialization.

The companion original-file replay has the right source-information boundary.
Its dual interpreter receives packed \(Q,w,t\), clipped slacks, layout, source
identity, and query, but no residual or original gate entry. The virtual
\((u',L',V')=(\alpha,0,\alpha+\beta)\) values reproduce only the eliminated
constraints, which is sufficient for this bound evaluator and is not a hidden
reconstitution of the original columns. On the stated fixture, the pair-total
path reads original gate rows zero and one, whereas the dual certificate
leaves only row zero and reads no gate record; both retrieve the identical
32-byte original payload and produce the same ordinary output.

I separately replayed the 69-byte exact-centered comparator on that same
temporary source: it selected row zero, read only its 32-byte payload, and
returned the identical bytes. Thus the reported 74-byte dual guide is not a
RAM-frontier win even on the favorable gate-read witness. The replay verifies
the fixture's source digest once before reads. Its raw records carry no
per-read integrity header, so the result remains conditional on the declared
immutable-fixture boundary rather than proving a production storage-integrity
path. Its materialized arrays are verification state, not evidence for a
streaming peak-RAM claim.
