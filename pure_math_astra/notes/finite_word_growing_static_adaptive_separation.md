# A growing separation with finite resident matrix descriptions

Status: an assembled theorem in a declared column-linear execution model.
The sharper 1.89 boundary estimate has independent reconstruction in
query_adaptive_equicorrelation_boundary_rank_review.md, and the assembly is
reviewed in finite_word_growing_static_adaptive_separation_review.md.
This note does not assert originality or accept the result as sufficient
for the Cassette goal. The class and its exclusions are part of the statement.

The independent-sign construction in
rademacher_source_growing_static_adaptive_extension.md later reduces the
required row dimension from O_eta(m^2) to O_eta(m), with slightly changed
error constants. The exact-Gram Hadamard construction is retained below.

## 1. The two execution classes

Fix the dimensions, a source-independent interpreter, and a resident budget
b bits. Every complete b-bit resident state which reconstructs a matrix
produces some B in C^{p by q}; undefined words may be discarded. There are
at most 2^b resulting matrices. The encoder may inspect the source, train,
and choose any such state. Source-dependent learned parameters, programs,
and constants must be included in the state. Free source-dependent side
information is not an input to this interpreter.

The static class chooses B before the query. After any fixed orthogonal or
unitary column transform, it uses a query-independent random linear map L,
with E L=I and at most s nonzero rows in each outcome, to estimate the
residual action. Its random choice may depend on the source and its retained
coefficients may depend linearly on the complete query. We grant this class
free sampling metadata, free transform information, and exact residual
column access for the lower bound. Those grants enlarge the comparator.

The adaptive construction uses B=0 and selects a law from a fixed finite
block catalog after seeing each four-coordinate query block. Every catalog
law is individually operator-unbiased and has at most two nonzero rows.
Both classes therefore produce linear combinations of fetched columns;
the adaptive class changes its probability law with the query.

The theorem concerns the worst unit-query mean-square output error. It does
not cover nonlinear resident reconstruction, query-selected B, or arbitrary
computations on fetched encoded data that produce vectors outside the span
of the selected source columns. Those are different execution classes.

## 2. Statement

There is a sufficiently small positive dyadic r, fixed independently of m,
with eta=r^2 <= 1/100, and a finite rational two-column block catalog whose
worst-query variance at H_eta=11*+eta I_4 is at most (19/10)eta.

For every positive integer m, let q=4m and t=5m. Fix an interpreter as
above and a budget b. Choose p=4^k >= t large enough that

\[
 2\exp\left[b\log2+13m\log9-{p\over800t}\right]<1.
 \tag{1}
\]

There is a dyadic real source A of size p by 4m with

\[
 A^*A=H_\eta^{\oplus m}
 \tag{2}
\]

for which the adaptive construction uses at most 2m source columns and
has worst-query variance at most (19/10)eta. Every static comparator from
Section 1 achieving that same error must have

\[
 s>\left(2+{1\over50}\right)m.
 \tag{3}
\]

Thus the read-count difference grows at least linearly with m within the
declared execution classes. This is not a converse for every Cassette plan.

The common-budget comparison requires that b hold the adaptive records
described next. The static lower bound itself holds for every b satisfying
(1), without this additional upper-construction requirement.

The finite block catalog is shared across identical blocks. Its joint law
need not be stored as a catalog of exponentially many combinations. For a
fixed eta, the catalog has a fixed finite bit length independent of m.
Dimensions, the regular block partition, source identity, and addressing
must also fit the declared adaptive resident budget. The upper construction
is compared at budget b only when these finite records actually fit in b.
With a fixed regular column layout, the variable dimensions and addressing
parameters use O(log p+log m) bits; the catalog and fixed source parameter
use a finite constant depending on eta. Thus, for fixed eta, sufficiently
large b=O_eta(log(m+2)) and p=O_eta(m^2) can satisfy both requirements.
These asymptotic constants are not numerical resident-memory estimates.

## 3. The adaptive upper bound

The rank estimate in query_adaptive_equicorrelation_boundary_rank_bound.md,
together with the finite-eta passage in
query_adaptive_complex_water_counterexample.md, gives
Psi_{2,C}(H_eta) <= (189/100)eta for every sufficiently small eta.
The rational finite-catalog theorem in
query_adaptive_finite_catalog_bridge.md permits an extra eta/100, yielding
the catalog in Section 2. The source parameter may be chosen as a dyadic
square because such positive parameters approach zero.

Invoke the block selector separately on each four-coordinate block x_j,
draw its two-sparse output Y_j, and concatenate the results. The resulting
Y has E Y=x and at most 2m nonzero coordinates. Equation (2) makes the output
error exactly the sum of the block errors, so

\[
 \mathbb E\|A(Y-x)\|^2
 \le {19\over10}\eta\sum_{j=1}^m\|x_j\|^2
 ={19\over10}\eta\|x\|^2.
 \tag{4}
\]

Independence between blocks is available, though the block-diagonal Gram
already removes cross terms from this expectation. The selector can
evaluate the finitely many stored block risk quadratics. For K catalog
laws this takes O(mK) fixed-size quadratic evaluations. This is an
arithmetic-operation count, not a native execution or latency assertion.

## 4. A dyadic source defeating the finite resident range

Let R_0 be the direct sum of m copies of the five-by-four matrix [1*;rI_4].
Then R_0 is dyadic, has t=5m rows, and has Gram (2).

For each resident matrix B, form the real subspace spanned by the real and
imaginary parts of its columns. Its dimension is at most 2q. The audited
Hadamard construction in finite_description_codebook_lower_bridge_review.md
gives a sign vector epsilon for which

\[
 U=\operatorname{Diag}(\epsilon)W_{p,:,1:t},
 \qquad U^TU=I_t,
 \qquad\|P_{S_B}U\|_{\rm op}<{1\over10}
 \quad\text{for every decoded }B.
 \tag{5}
\]

Here W_p is the normalized Walsh-Hadamard matrix. The quarter-net union
bound is exactly (1): the tail exponent is p delta^2/(8t), with delta=1/10.
This choice is made after fixing the interpreter's entire finite range;
it is not claimed to be hard for every possible uncharged decoder at once.

Set A=UR_0. Since p=4^k, U has entries plus or minus 2^{-k}. Each source
entry has the form (plus or minus 1, plus or minus r)/sqrt(p), so A is
exactly dyadic with finite word length O(log p+word(r)).

For any decoded B and complex query x, the subspace angle gives
|<Ax,Bx>| <= ||Ax|| ||Bx||/10. Completing the square yields

\[
 \|(A-B)x\|^2\ge {99\over100}\|Ax\|^2,
 \qquad
 (A-B)^*(A-B)\succeq {99\over100}H_\eta^{\oplus m}.
 \tag{6}
\]

This lower bound applies to every B in the resident range, including the
one chosen by an encoder that has inspected A.

## 5. The static read lower bound

For a positive Gram G, a query-independent operator-unbiased row-s-sparse
linear law has worst-query variance at least the spectral water level
t_s(G), defined by tr(G(G+t_s I)^{-1})=s. This lower bound permits arbitrary
support allocation across the m blocks. Orthogonal or unitary changes of
column coordinates preserve the water level.

The water level is positively homogeneous and Loewner-monotone. Put
a=99/100 and c=19/10. If the static class has variance at most c eta, then
(6) and the water lower bound require

\[
 s\ge m\left[
 {a(4+\eta)\over a(4+\eta)+c\eta}
 +{3a\over a+c}\right].
 \tag{7}
\]

For eta <= 1/100, the quantity in brackets is bounded below by

\[
 2+{8\over289}-{19\over3960}
 >2+{1\over50}.
 \tag{8}
\]

The first term in (7) is at least 1-c eta/(4a), and the second is
297/289=1+8/289. The strict final comparison in (8) follows by multiplying
positive denominators. Equations (7)-(8) prove (3). If the right side is
not integral, the read count is of course rounded up to an integer.

## 6. What is and is not priced

The lower bound grants the static comparator more information and precision
than a charged implementation normally has. Charging that metadata or its
decoder cannot invalidate the lower bound for the smaller class. The
source-dependent state used to select B must still be a b-bit word of the
fixed interpreter; an uncharged source-dependent decoder would change the
quantifiers and defeat this construction.

The adaptive upper uses a fixed finite block catalog, a regular block
partition, and a declared source layout. It uses the original columns, so
the source payload can be identical for the two compared paths. Counting
these records and their exact finite encodings is necessary before naming
a numerical b. Finite existence does not supply that numerical catalog.

Under a declared dense contiguous-column layout with w-bit entries, the
abstract fresh scalar count is p times the column count. The corresponding
payload is pqw bits before headers. Alignment, page grouping, cache reuse,
and measured latency remain separate. In particular, the constructed
Hadamard source has additional structure: another execution class could
exploit it through nonlinear decoding of fetched data. Equation (3) is not
a bound on that broader class.

This note establishes a growing mathematical separation inside the declared
column-linear model, conditional only on the cited supporting proofs and
the stated finite encoding assumptions. It does not establish an optimal
description-distortion curve over every class allowed by MATHS.md, an
optimal adaptive scheme, a physical-device result, or a publication claim.
