# rounded_original_column_oracle_boundary_review.md — finite-word boundary review for the rounded original-column extension; depends on finite_family_transformed_column_oracle_boundary.md, finite_advice_spectral_trace_lower.md, encoded_column_rounding_bound.md, k4_dyadic_full_linear_page_accounting.md, and ../../MATHS.md.

Status: the proposed restriction is a legitimate declared execution format, and the rounding lift has a direct approximate-mean form. It is not a lower bound for arbitrary Cassette encodings or page layouts.

## Declared format

Fix a dyadic grid step \(h=2^{-r}\), a real Gram matrix \(G>0\), and
the full orbit \(\mathcal O_G\). Choose a fixed range \([-R,R]\) that
contains every entry of every \(A\in\mathcal O_G\); for example,
\(R=\max_j\sqrt{G_{jj}}\). Let

\[
 W=\operatorname{round}_h(A)
 \tag{1}
\]

be entrywise rounding with a declared tie rule. The resulting family is
finite. A legal fresh read is one complete original coordinate column
\(W_{:j}\), stored as an aligned dense page of \(p\) fixed-width signed
dyadic words. A word must contain the sign and enough integer and
fractional bits to represent every grid value in \([-R,R]\); its width is
therefore a declared function of \(R\) and \(r\), not one abstract real
word. The page size must include its header, alignment, and address rule.

This format is legitimate under MATHS.md because the description class,
fresh-access unit, and physical conversion are declared together. It is
the same kind of conditional original-column format used by the K4 page
account: a nonmonomial right transform is not one original-column page.
Signed permutations merely relabel pages and may be admitted explicitly.

The following choices change the format and must be charged or excluded:

1. materializing pages for \(WQ\) for a nonmonomial \(Q\);
2. fetching several original pages to synthesize a transformed column;
3. variable-length, cross-column, or entropy-coded payloads that alter the
   declared one-read byte unit;
4. source-dependent decoder parameters outside the finite state label; and
5. an unbounded-precision scalar word.

Applying a fixed matrix to the query *after* original pages are read does
not evade the model: it is already permitted inside an arbitrary Borel
branch map. Only changing which source vector is supplied by one read
would evade it.

## Why rounding preserves the information boundary

Suppose a finite-source decoder has states \(\ell(W)\), fixed support laws
within those states, and branch maps \(F_{\ell,S}(W_{:S},x)\). Compose it
with (1):

\[
 \widetilde F_{\ell,S}(A_{:S},x)
 =F_{\ell,S}(\operatorname{round}_h(A_{:S}),x).
 \tag{2}
\]

This is a Borel function of the observed continuous columns alone. A
shared decoder table of arbitrary finite or infinite size does not change
that fact. The Haar conditional-subspace argument can therefore be applied
to (2) before conditioning on the source-selected label. Taking the union
over every finite label, support, and test query remains valid.

This is precisely what blocks the finite-corpus identification trick in
`finite_family_transformed_column_oracle_boundary.md`. That trick reads a
transformed exact-real column whose scalar entries can pack all original
coordinates. Here one read reveals only one fixed-width rounded original
column. A shared table may map that column to any output, but it cannot add
unobserved source coordinates to the argument of (2). Conditional Haar
concentration is uniform over such Borel maps. Thus there is no simpler
table-based counterexample to the rounded-family lower within this format.

## Approximate-mean transfer

The rounded decoder is exactly unbiased for \(W\), not for \(A\). Put

\[
 E=A-W,
 \qquad
 \rho=\|E\|_{\mathrm{op}}
 \le {h\sqrt{pq}\over2}.
 \tag{3}
\]

Assume at every unit query that

\[
 \mathbb E F_S=Wx,
 \qquad
 \mathbb E\|F_S-Wx\|^2\le C.
 \tag{4}
\]

Let \(H=\sum_Sp_SP_{\operatorname{span}(A_{:S})}|_V\), and assume the
same branchwise leakage event as in the continuous theorem,

\[
 \|P_{V\cap V_S^\perp}F_S\|\le\epsilon\|F_S\|.
 \tag{5}
\]

The exact-mean proof changes only by the deterministic rounding bias. For
\(u\in V\), its Cauchy--Schwarz step becomes

\[
 |\langle u,Ax\rangle|
 \le \bigl(\sqrt{u^THu}+\epsilon\|u\|\bigr)
      \sqrt{\widetilde C+x^TGx}+\rho\|u\|,
 \tag{6}
\]

where

\[
 \widetilde C=C+2\rho\sqrt{\lambda_{\max}(G)}+\rho^2.
 \tag{7}
\]

Indeed, the variance identity gives
\(\mathbb E\|F_S\|^2\le C+\|Wx\|^2\), and
\(\|Wx\|\le\sqrt{x^TGx}+\rho\). This proves (6) without inverting an
individual support probability.

At the normalized finite-net query

\[
 x_z={(G+\widetilde C I)^{-1/2}z\over
           \|(G+\widetilde C I)^{-1/2}z\|},
 \tag{8}
\]

the same cancellation as in the continuous proof turns the last term in
(6) into at most

\[
 \alpha\|u\|,
 \qquad
 \alpha={\rho\over\sqrt{\lambda_{\min}(G)+\widetilde C}}.
 \tag{9}
\]

Thus, for a \(\delta\)-net and \(a=1-\delta^2/2\),

\[
 H\succeq
 a^2A(G+\widetilde C I)^{-1}A^T
 -2a(\epsilon+\alpha)I_V.
 \tag{10}
\]

Taking traces gives the finite-word analogue

\[
 \bar s\ge
 a^2\operatorname{tr}\bigl(G(G+\widetilde C I)^{-1}\bigr)
 -2aq(\epsilon+\alpha).
 \tag{11}
\]

Equations (3), (7), and (9) are the necessary rounding budget. For a
small-eigenvalue example, \(\rho\) must be small relative to the relevant
square-root spectral scale; a fixed word width may not suffice as the
target scale tends to zero.

## Exact accounting boundary

To use this as a Cassette certificate rather than a finite-dimensional
format lemma, the plan must record:

- the target matrix before rounding and the representation error
  \(\|A-W\|\), separately from stochastic execution error;
- grid step, tie rule, signed-word width, numerical range, page header,
  alignment, and original-column address map;
- the finite-state label bit count and where it resides;
- all shared interpreter, decoder-table, sampler, and transform bytes;
- the rule that a fresh selected coordinate fetches its complete declared
  original-column page; and
- arithmetic precision and its additional bias or variance.

The mathematical lower bound remains valid even if the shared Borel
decoder table is granted free, because it is a stronger comparator. An
actual Cassette byte account cannot grant that table, state label, or
arithmetic for free. MATHS.md also requires a separate sequential loss
propagation and observation contract before a one-call bound becomes a
capability claim.

## Conclusion

The rounded original-column construction closes the particular
finite-corpus loophole caused by free transformed exact-real columns. It
creates a credible restricted finite-word execution class. It does not
show that Cassette must use this class, that a frontier model has the
required Gram-orbit uncertainty, or that no other charged encoded-page
format can do better.
