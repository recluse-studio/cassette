# Real versus complex query-adaptive sampling: exact reduction and obstruction

Status: exact reductions and a failed general comparison route.  No universal
constant comparison and no separating Gram family is proved here.

Let \(G\) be real symmetric positive definite.  Write
\(\phi_{\mathbb F}(x)\) for the inner minimum in

\[
 \Psi_{2,\mathbb F}(G)=\sup_{\|x\|_2=1}\phi_{\mathbb F}(x),
 \qquad \mathbb F\in\{\mathbb R,\mathbb C\},
\tag{1}
\]

with \(\mathbb EY=x\) and \(\|Y\|_0\leq2\) almost surely.  The support
condition is coordinate support over the indicated field.

## 1. What is exactly the same

For every real query \(x\),

\[
 \phi_{\mathbb C}(x)=\phi_{\mathbb R}(x).
\tag{2}
\]

The inequality \(\leq\) is immediate.  Conversely, write a legal complex
estimator as \(Y=U+iV\).  Its real part is real, two-sparse, and has
\(\mathbb EU=x\).  Because \(G\) is real,

\[
 \mathbb E(Y-x)^*G(Y-x)
 =\mathbb E(U-x)^TG(U-x)+\mathbb EV^TGV
 \geq\mathbb E(U-x)^TG(U-x).
\tag{3}
\]

Thus the field distinction enters only through genuinely non-real queries;
one cannot remove the mean condition or compare only their projected images.
In particular,

\[
 \Psi_{2,\mathbb C}(G)\geq\Psi_{2,\mathbb R}(G).
\tag{4}
\]

## 2. Exact polar rank formulation

For \(S\subset\{1,\ldots,4\}\), \(|S|=2\), put

\[
 K_S=E_SG_{SS}^{-1}E_S^T.
\tag{5}
\]

The real polar is

\[
 \mathcal P_{\mathbb R}=
 \{a\in\mathbb R^4:a^TK_Sa\leq1\ \text{for every }S\},
\tag{6}
\]

whereas a complex polar vector \(z=a+ib\) is equivalent to the real
positive semidefinite matrix

\[
 X=aa^T+bb^T,\qquad \operatorname{rank}X\leq2,
\tag{7}
\]

satisfying

\[
 \operatorname{tr}(K_SX)\leq1\quad\text{for every }S.
\tag{8}
\]

The objective can also be written without the atomic gauge:

\[
 \Psi_{2,\mathbb F}(G)
 =\max_{z\in\mathcal P_{\mathbb F}}
       \lambda_{\max}(zz^*-G).
\tag{9}
\]

For the real field, (9) optimizes over rank-one matrices \(aa^T\).  For
the complex field it optimizes over the rank-two matrices in (7), while
retaining the skew imaginary part of \(zz^*\).  This is the precise
rank-one versus rank-two obstruction.  It is distinct from the larger SDP
obtained by dropping the rank condition.

To verify (9), use

\[
 \gamma_{2,G}(x)^2=\max_{z\in\mathcal P_{\mathbb F}}|z^*x|^2
\tag{10}
\]

in the atomic identity
\(\Psi_2=\max_{\|x\|=1}(\gamma_{2,G}(x)^2-x^*Gx)\), then interchange the
two compact maxima.

## 3. Every complex polar vector gives a circle of real polar vectors

If \(z=a+ib\) is complex polar, then, for every \(\theta\),

\[
 a_\theta=a\cos\theta+b\sin\theta\in\mathcal P_{\mathbb R}.
\tag{11}
\]

Indeed, each pair form satisfies

\[
 a_\theta^TK_Sa_\theta
 \leq a^TK_Sa+b^TK_Sb
 =\operatorname{tr}(K_SX)\leq1.
\tag{12}
\]

This gives a useful, but insufficient, real rounding of a complex witness.
Its averaged second moment is

\[
 {1\over2\pi}\int_0^{2\pi}a_\theta a_\theta^T\,d\theta
 ={aa^T+bb^T\over2}={X\over2}.
\tag{13}
\]

The factor one half is unavoidable: if \(a,b\) are orthogonal with equal
norm, every single phase captures at most half of \(\operatorname{tr}X\).

## 4. Why the circle rounding does not give a multiplicative variance bound

Suppose \(t=\Psi_{2,\mathbb R}(G)\).  Real polar containment is exactly

\[
 aa^T\preceq G+tI\qquad(a\in\mathcal P_{\mathbb R}).
\tag{14}
\]

Applying (14) to the phase circle and averaging gives only

\[
 X\preceq2G+2tI.
\tag{15}
\]

The desired complex containment would have the qualitatively stronger form
\(zz^*\preceq G+CtI\).  Equation (15) leaves a full copy of \(G\), so it
cannot imply a bound \(\Psi_{2,\mathbb C}\leq C\Psi_{2,\mathbb R}\) when
\(t\ll\lambda_{\max}G\).

The same baseline loss appears in the primal circularization.  For a complex
query \(x\), let \(q_\theta=\operatorname{Re}(e^{-i\theta}x)\) and use an
optimal real estimator for \(q_\theta\).  Averaging phases and multiplying
the output by two restores the exact complex mean, but its second moment
contains twice \(x^*Gx\).  After subtracting the target energy, one copy of
\(x^*Gx\) remains.  This is not a proof defect: it is the same factor-two
rank loss as (13).

Thus splitting a complex witness into real and imaginary parts proves
neither an exact comparison nor a constant-factor comparison at small
variance.  A proof would need a simultaneous rounding that keeps the
baseline energy, or use the special six pair-principal constraints in a way
that generic circle rounding does not.

## 5. What this does and does not show

The paired-block calculation in
`query_adaptive_q4_unequal_paired_polar.md` gives a genuine field
distinction at the water level: for two real \(2\times2\) blocks with
eigenvalues \(1,r^2\), the complex field always has the displayed sharp
polar witness at \(r\), whereas the real field attains equality at \(r\)
only when the two normalized correlation magnitudes agree.  This rules out
a proof that simply replaces complex phases by real signs while preserving
the same witness.

It is not a separating family for a universal ratio. The note does not
show that the real value is \(o\) of the complex value. The general
spectral-water benchmark considered in
`query_adaptive_rank_two_spectrahedron.md` has since been disproved in
`query_adaptive_complex_water_counterexample.md`. That counterexample
does not settle the real-versus-complex ratio question posed here.

The unresolved discriminating statement is therefore narrow:

\[
 \text{Does a rank-two matrix (7)--(8) with large complex objective force
 a rank-one real polar vector with a fixed fraction of that objective?}
\tag{16}
\]

The phase-circle calculation alone does not settle the analogous rounding
question even for general convex bodies.  Whether the six coordinate-pair
inverse forms of a real \(4\times4\) Gram matrix supply the missing
structure remains open in this note.
