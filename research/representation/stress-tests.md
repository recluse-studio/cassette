# Mathematical attacks on representation and interpretation

These examples test claims shared by several candidate families. Each conclusion names the
assumption it defeats. None establishes that the affected family is unusable on a structured
weight matrix. The cases supplement each lane's own proof and source review.

## S1. A small rank does not follow from a large parameter count

Let \(A=I_n\). Every rank-\(k\) reconstruction with \(k<n\) has spectral error at least
one: its null space contains a unit vector \(x\), so \(\|(A-B)x\|=1\). Its best
Frobenius squared error is \(n-k\), attained by retaining \(k\) coordinate directions.
This attacks a source-independent claim that a very small low-rank description gives small
error on every query. Residual reads, a different encoding, or verified source structure must
account for the omitted action.

## S2. Average fidelity can hide a query direction

Let \(A=\operatorname{diag}(M,1)\), with \(M>1\), and use its best rank-one Frobenius
approximation \(B=\operatorname{diag}(M,0)\). The Frobenius-relative squared error tends
to zero as \(M\) grows, but \(x=e_2\) loses the whole answer. A small matrix-relative
distortion is therefore not a guarantee of small answer-relative error for every query.

The same issue survives a perfect fit to finite calibration queries. If those queries span
\(S\subsetneq\mathbb R^q\), choose unit \(v\perp S\) and unit output \(u\). The
matrices \(A\) and \(A+Luv^T\) agree on every calibration query for every \(L\), while
their answers at \(v\) differ by \(Lu\). A learned codebook or query predictor needs its
declared distribution or protected-query contract; calibration fit alone cannot prove more.

## S3. Weight relationships do not determine the output orientation

For every orthogonal \(U\), \((UA)^T(UA)=A^TA\). Thus the Gram matrix, all column norms,
and every pairwise column inner product are unchanged by an output rotation. Nevertheless,
\(UAx\) generally differs from \(Ax\). For the scalar pair \(A=[1]\) and \(A'=[-1]\),
both Gram representations are \([1]\), while the answer to \(x=1\) differs by two.

A decoder receiving only that representation and no external reads returns the same value for
both sources. Its worst absolute error is at least one. A relationship representation can guide
reads and bound error, but a general exact decoder must obtain the missing orientation somehow.

## S4. Finite encoded information must distinguish the requested answers

Consider every matrix in \(\{-1,1\}^{p\times q}\), and require exact answers to all coordinate
queries \(e_1,\ldots,e_q\) with zero external reads. A source-independent deterministic
interpreter with at most \(b\) resident bits can distinguish at most \(2^b\) sources. Exact
answers to those queries reveal all \(pq\) signs, so the encoder must be injective and
\(b\ge pq\). The same count applies when every answer has coordinatewise error strictly
below one, because each sign can still be recovered.

This is a finite, zero-read statement. It does not prohibit a small description with informative
external reads, or a compact encoding for a smaller verified source class. It does prohibit
using an arbitrary real number as an uncharged container for all the original bits.

## S5. A residual sampler can struggle on an exactly cancelling query

Take \(R=[1\ -1]\) and \(x=(1,1)^T\). The exact residual action is zero. Equal-probability
one-column sampling returns either 2 or -2, with mean zero and variance 4. Averaging \(s\)
independent samples has variance \(4/s\). Reading both columns once gives the exact result.
Unbiasedness alone therefore does not imply that a method is efficient, and a comparison that
omits stratified or correlated reads can prefer the wrong interpreter.

## S6. A page and a scalar are different read units

Suppose each requested \(w\)-byte scalar occupies a different \(P\)-byte page, where
\(P>w\). Reading \(t\) distinct requested scalars then transfers \(tP\) bytes under a
whole-page interface, not \(tw\). A compact mathematical sampler can still create scattered
physical reads. Conversely, several selected scalars on one already fetched page need not pay
for that page again. Both cases require the actual layout and request transcript.

## S7. An exact real-valued description needs a finite interpretation

Let a stored coefficient be \(b\), its finite decoded value be \(\widetilde b\), and a scalar
query be \(x\). Omitting the quantization error changes the answer by
\((b-\widetilde b)x\). If the residual corrects against \(A-b\) while the resident action
uses \(\widetilde b\), the same discrepancy becomes a systematic bias. Correcting against
the actual decoded \(A-\widetilde b\) restores the algebraic expectation, with sampling
variance calculated from that actual residual. Arithmetic roundoff remains a separate term.

## S8. A stored transform can cost more than it saves

A general dense change of basis on \(\mathbb R^q\) needs \(q^2\) scalar slots in its direct
encoding and quadratic work to apply. Calling the transformed source diagonal does not remove
those costs. A short product of fast transforms, a shared basis, or a structured transform may
reduce them, but each restricts the representable class or adds an approximation term that must
be proved. The comparison must also allow the established method to use the same transform.

## How the cases affect the campaign

S1, S2, and S8 attack low-rank, tensor, structured, and learned descriptions. S3 and S4 attack
claims of extremely small universal abstractions. S5 and S6 attack read-selection claims. S7
attacks the passage from exact mathematics to encoded weights. The source survey and candidate
notes add the family-specific cases. This list is an explicit coverage record, not an assertion
that every possible mathematical construction has been enumerated.
