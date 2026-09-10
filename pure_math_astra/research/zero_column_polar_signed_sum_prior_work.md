# Primary-source check: the signed-sum ingredient in the zero-column polar lemma

Status: source check complete.  The signed-sum separation step is a standard
real form of Bang's lemma.  The zero-column finite-polar application is a
direct use of that elementary lemma within this lab's finite-polar system;
this source check does not assess its originality.

## Sources read

1. Thøger Bang, [*A solution of the “plank problem”*](https://doi.org/10.1090/S0002-9939-1951-0046672-4),
   *Proceedings of the American Mathematical Society* **2** (1951), no. 6,
   990–993.  The [AMS scan](https://www.ams.org/journals/proc/1951-002-06/S0002-9939-1951-0046672-4/S0002-9939-1951-0046672-4.pdf)
   was read directly.  Bang's Lemma 2 chooses a sign vector by maximizing a
   finite expression containing a signed vector sum and its squared norm.
   The paper uses this maximization in the plank proof.  It does not isolate
   the exact unit-vector statement below under the modern name “Bang's
   lemma.”

2. Keith M. Ball, [*The complex plank problem*](https://discovery.ucl.ac.uk/id/eprint/12546/1/12546.pdf),
   *Bulletin of the London Mathematical Society* **33** (2001), no. 4,
   433–442, [DOI](https://doi.org/10.1112/S002460930100813X).
   Section 1, Lemma 5, explicitly calls the real statement Bang's lemma:
   for a real Gram matrix \(H=(h_{ij})\) and positive \(r_i\), signs
   \(\varepsilon_i\) exist such that

   \[
   \varepsilon_i r_i\sum_j h_{ij}r_j\varepsilon_j\ge r_i^2
   \qquad\text{for every }i. \tag{1}
   \]

   Ball states that the proof chooses signs maximizing the associated
   quadratic form.  This is the exact maximizing-sign mechanism used here.

## Exact comparison

Let \(w_1,\ldots,w_L\) be real unit vectors and let
\(H_{ij}=w_i^Tw_j\).  Ball's Lemma 5 with \(r_i=1\) gives signs
\(\sigma_i\) satisfying

\[
 \sigma_i w_i^T\sum_{j=1}^L\sigma_jw_j\ge1
 \qquad(1\le i\le L). \tag{2}
\]

Equivalently, if \(v=\sum_i\sigma_iw_i\) maximizes \(\|v\|_2^2\), then a
single sign flip gives

\[
 0\ge\|v-2\sigma_iw_i\|_2^2-\|v\|_2^2
 =4-4\sigma_iw_i^Tv. \tag{3}
\]

Since \(\|v\|_2\le L\), \(u=v/\|v\|_2\) obeys

\[
 |w_i^Tu|\ge L^{-1}. \tag{4}
\]

Thus the finite signed-sum lemma in the zero-column finite-polar note is
precisely a unit-weight specialization of the standard Bang lemma.  It
should be cited as such, not presented as a new separation theorem.

## The zero-column application

For a \(k\times k\) matrix with one exact zero column \(j_0\), the polar
proof takes one unit normal \(w_{EJ}\) for every square block
\(B=K_{E,J}\) with \(j_0\in J\).  The block has rank at most
\(|J|-1\), so this normal exists in
\(\operatorname{range}(B)^\perp\), supported on \(E\).  The number of
normals is

\[
 L=\sum_{r=1}^k\binom{k}{r}\binom{k-1}{r-1}
 =\binom{2k-1}{k}. \tag{5}
\]

Applying (4) simultaneously to this finite family gives a unit \(u\) at
distance at least \(1/L\) from every relevant column range.  With
\(n=L^{-1}e_{j_0}\), each such block satisfies \(Bn_J=0\).  The exact
finite-polar left side then splits into \(L^{-2}\) plus a quadratic form
bounded by the squared projection of \(u_E\) onto
\(\operatorname{range}(B)\).  The distance bound supplies the missing
\(L^{-2}\).  Blocks omitting \(j_0\) have \(n_J=0\) and follow from the
standard contraction

\[
 B(I+B^TB)^{-1}B^T\preceq I. \tag{6}
\]

This deduction is short once (4) is available, but it is not an immediate
statement of Bang's plank theorem: it relies on the lab-specific indexing
of all square submatrices, the exact zero-column cancellation, and the
finite-polar quadratic form.  The sources above establish the
signed-sum ingredient only.  They neither state nor imply a Cassette
resource theorem.

## Scope

The cited lemma is real and finite.  It supports the exact-zero-column
stratum only; it supplies no perturbation estimate for a small nonzero
column, no zero-row analogue, and no conclusion for an arbitrary
\(K\).  The exact-zero-column subcase was not found in the sources read,
but that absence does not support a substantive novelty claim: it is a
short direct application of a standard sign lemma and elementary linear
algebra.  No novelty conclusion follows from this primary-source match.
