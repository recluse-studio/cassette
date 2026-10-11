# Exact query lookahead from a compact address certificate

## Claim boundary

A resident object cannot reveal a future page that depends on an unread weight
value, an unresolved token, or another unavailable datum. It can still do a
useful narrower job: represent the **exact set of pages that remain possible**
under the runtime facts already available, then start those reads while ordinary
arithmetic resolves the remaining control.

This note gives one finite construction. It neither assumes that semantically
similar queries use similar weights nor estimates a matrix product. Its pages
hold the authoritative weights outside RAM. Every resident and transient object
appears in the account below.

The construction is a mathematical candidate. Its Boolean compression and
prefetch ingredients are established; no originality claim follows.

## 1. Execution model

Let a compiled suffix have \(Q=2^r\) equally sized weight regions, with page
identities

\[
 \{p_0,p_0+1,\ldots,p_0+Q-1\}.
 \tag{1}
\]

The suffix's normal control arithmetic produces an exact bit word

\[
 b=(b_1,\ldots,b_r)\in\{0,1\}^r,\qquad
 b_i=\mathbf 1\{g_i(u)\geq0\},
 \tag{2}
\]

where \(u\) is already available query/runtime state and every \(g_i\) is
evaluated in the declared finite arithmetic. A tie rule belongs to the
contract. The suffix reads the one region

\[
 p(b)=p_0+\sum_{i=1}^r b_i2^{r-i}.
 \tag{3}
\]

A region may name a fixed page group rather than one page; replace one by that
declared group everywhere below.

At lookahead time, the first \(h\) bits have been produced by ordinary
arithmetic. Write their integer value as

\[
 \beta=\sum_{i=1}^h b_i2^{h-i}.
 \tag{4}
\]

The remaining \(r-h\) bits are unresolved, but they are not guessed. PQAC
requires a declared **prefix-complete** control contract: after every permitted
observed prefix, every suffix word in \(\{0,1\}^{r-h}\) is a legal continuation.
The **prefix quotient address certificate** (PQAC) then returns

\[
 {\cal I}(b_{1:h})=
 \{p_0+\beta2^{r-h},\ldots,
       p_0+(\beta+1)2^{r-h}-1\}.
 \tag{5}
\]

Equation (5) is an exact future-region set: every legal completion of the
unresolved word maps into it, and every page in it is reached by the
corresponding completion. It is a compact interval description, not a resident
copy of the pages.

A compiler may replace the radix address (3) with a reduced ordered
multi-terminal decision diagram \(D\). Its leaves name page groups; its internal
nodes test declared control bits. If only some bit words are legal, a second
exact feasibility diagram \(C\) represents those words. Restrict both diagrams
by known bits and take the union of the \(D\)-leaves reachable through \(C\).
That gives the exact possible-region set for the declared suffix. Without
\(C\), PQAC is exact only under the prefix-complete contract; otherwise its
interval is merely a sound superset.

The control program itself is not free. If (2) is already normal arithmetic,
PQAC stores operation identifiers and the bit order. If lookahead adds a
separate affine or polynomial guard program, every coefficient, threshold,
rounding rule, and guard-evaluation operation is resident or transient cost.

## 2. Exactness theorem

**Theorem 1 — exact may-read set.** Suppose the suffix contract is
prefix-complete and says that every completion \(b\in\{0,1\}^r\) reads exactly
\(p(b)\) from (3), and the first \(h\) bits have the observed value in (4).
Then (5) is precisely

\[
 \{p(b_{1:h},c):c\in\{0,1\}^{r-h}\}.
 \tag{6}
\]

If all \(r\) bits are known, the set is the actual future region singleton.

**Proof.** Substitution in (3) gives

\[
 p(b)=p_0+\beta2^{r-h}
       +\sum_{j=1}^{r-h}c_j2^{r-h-j}.
\]

The final sum ranges once over every integer from \(0\) through
\(2^{r-h}-1\). Thus it produces each member of (5), and no other page.
\(\square\)

The word “may” is essential. When \(r-h>0\), (5) is not generally the actual
future singleton. It is the complete set that must be considered if reads begin
before the remaining bits are available.

**Lemma 2 — no earlier exact singleton without information.** Let two legal
external states have the same resident certificate and the same observed prefix,
but let an unread datum select distinct future pages \(p\ne p'\). No algorithm
that sees only that shared information can output the actual singleton page set
before reading the datum.

**Proof.** The algorithm has the same input in both states and therefore returns
the same set. It fails in at least one state. \(\square\)

The alternatives are explicit: read the controlling datum, retain a resident
certificate that determines it, or prefetch the exact union of its remaining
possibilities. A relevance oracle is not among them.

## 3. Byte, arithmetic, and latency account

Let a region occupy \(P\) bytes, a page identifier use \(b_p\) bits, and an
address use \(b_a\) bits. The persistent PQAC payload is

\[
 B_{\rm PQAC,res}\ \geq\
 b_a+2\lceil\log_2(r+1)\rceil+b_{\rm guard}.
 \tag{7}
\]

The two logarithmic fields record the declared word length and split point.
The observed prefix value is transient: it costs \(h\) bits unless it already
occupies a charged normal-control register. The interval generator needs one
additional \(b_a\)-bit cursor. Here \(b_{\rm guard}\) is zero only when the
guard operation identifiers refer to already-required normal arithmetic. It
otherwise includes the complete finite guard representation. A general diagram
with \(N\) internal nodes and \(L\) singleton-page leaves requires at least its
node tags, variable indices, child pointers, and page identifiers; a simple
explicit account is

\[
 B_D =
 N\!\left(1+\lceil\log_2 r\rceil+
             2\lceil\log_2(N+L)\rceil\right)
 +L\lceil\log_2 Q\rceil
 \quad\text{bits},
 \tag{8}
\]

before the guard representation and allocator metadata. A leaf naming a group
of \(g\) arbitrary pages adds at least \(g\lceil\log_2Q\rceil\) identifier bits
under this direct encoding. This is a charge, not a compression guarantee. Some
functions require exponentially many decision nodes.

For PQAC, \(k=|{\cal I}|=2^{r-h}\) regions are issued at lookahead time. A
sparse transient issue list needs at least \(kb_p\) bits, or a streaming interval
generator needs \(O(b_a)\) bits but emits \(k\) requests. Holding every cold
region until the remaining control word resolves needs \(kP\) bytes. Let
\(B_{\rm normal,hold}\) be the exact peak of query, output, ordinary temporary,
control, and queue buffers during that holding window. Full-union prefetch
therefore admits RAM exactly when

\[
 B_{\rm resident}+B_{\rm normal,hold}+kP\ \leq\ M_{\rm available}.
 \tag{9}
\]

Here \(B_{\rm resident}\) includes (7) or (8), page indexes, the interpreter,
and any source-dependent guard data. A full-run peak may replace
\(B_{\rm normal,hold}\) conservatively, but then (9) is sufficient rather than
necessary. No part of the external weights is counted as resident merely
because its address is known.

Assume \(c\) independent read lanes, identical cold-region service bound
\(\ell\), no cache hits, and a common deadline: all members of \({\cal I}\)
may be the next consumed region once the remaining control word resolves. Let
\(\Delta\) be the time after the lookahead calculation completes and before
that earliest possible consumption. Fetching the whole exact may-read interval
hides its cold-read time if and only if

\[
 \left\lceil{k\over c}\right\rceil\ell\ \leq\ \Delta
 \quad\text{and}\quad (9)\text{ holds}.
 \tag{10}
\]

The condition is necessary and sufficient under these deliberately uniform,
common-deadline assumptions: \(k\) jobs require \(\lceil k/c\rceil\) service
waves, and the pages must remain available. For distinct deadlines \(d_p\), all released after
lookahead time \(t_0\), the corresponding exact lane condition is

\[
 \left|\{p\in S:d_p\leq\tau\}\right|
 \leq c\left\lfloor{\tau-t_0\over\ell}\right\rfloor
 \quad\text{for every page deadline }\tau,
 \tag{11}
\]

with a compatible buffer-retention schedule. Equation (11) is the scheduler
test; it is not a device measurement.

The certificate evaluation itself must finish before requests issue. For PQAC
it takes \(O(h)\) already-required guard decisions plus fixed-width address
arithmetic. A decision diagram takes its restricted traversal and leaf-union
work, which must be added to the left side of the applicable deadline.

## 4. A sharp, finite reduction

Take \(Q=2^{20}\) regions and a 20-bit address word. If 18 high-order guard
bits are available while ordinary arithmetic still has time for the two
remaining guards, PQAC reduces the exact possible set from \(1{,}048{,}576\)
regions to four. Its resident payload is the address base, the known prefix,
the bit count, and the declared guard references; the observed prefix is a
charged transient control word. PQAC does not contain a million-entry route
table.

With four read lanes, (10) reduces to \(\ell\leq\Delta\), and (9) requires
four region buffers in addition to normal working memory. Once the last two
bits arrive, one of those four is the actual region. This is a real overlap
opportunity. It is also a bounded one: the construction saves no cold reads if
only one lane exists and \(4\ell>\Delta\), or if four buffers do not fit.

The same arithmetic shows the limit. With no prefix bits, \(k=Q\); the compact
certificate has merely described a whole-model prefetch. With a unique page
that depends on an unread external bit, Lemma 2 forbids an earlier singleton.
With a general guard map whose reduced diagram has \(\Theta(Q)\) leaves, the
resident representation has traded the page directory for another page-scale
object.

## 5. What is candidate mathematics, and what is established

The candidate is the **certified coupling** of three exact objects:

1. a finite-arithmetic guard signature;
2. a compact symbolic quotient of its unresolved completions into external
   page regions; and
3. an explicit RAM-and-deadline admission theorem such as (9)--(11).

The value is narrow. It can prove that a particular compiler plan has a smaller
exact prefetch frontier than its full region set, before the runtime finishes
normal control arithmetic. It cannot prove that an arbitrary model has small
frontiers, that page IDs encode semantic relevance, or that a physical device
will meet \(\ell\).

The primitives are established. Bryant's ordered binary decision diagrams
represent Boolean functions by reduced directed acyclic graphs and can be
compact for some functions while exponential in the worst case. Mowry, Lam,
and Gupta use compiler analysis to issue data prefetches for predictable matrix
references; their method weighs miss likelihood and overhead rather than
certifying a complete symbolic may-read set. Sparse mixture-of-experts routing
selects a small expert set from a learned gate, but it is an architectural
conditional-computation mechanism, not an exact lookahead proof for an
external page plan.

The bounded primary-source pass found no source stating the specific
finite-arithmetic PQAC contract or the combined exactness, RAM, and latency
conditions above. That is a non-collision observation, not evidence of
originality. A claim of new mathematics would require a wider program-analysis,
symbolic-execution, storage-prefetch, and conditional-computation review.

## Primary sources

- Randal E. Bryant, [*Graph-Based Algorithms for Boolean Function
  Manipulation*](https://doi.org/10.1109/TC.1986.1676819), *IEEE Transactions
  on Computers* 35(8), 677--691, 1986.
- Todd C. Mowry, Monica S. Lam, and Anoop Gupta, [*Design and Evaluation of a
  Compiler Algorithm for Prefetching*](https://doi.org/10.1145/143365.143488),
  ASPLOS, 1992.
- Noam Shazeer et al., [*Outrageously Large Neural Networks: The
  Sparsely-Gated Mixture-of-Experts Layer*](https://arxiv.org/abs/1701.06538),
  2017.
