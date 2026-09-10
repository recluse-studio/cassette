# gaussian_static_nonlinear_oracle_minimax_gap_independent_review.md — independent correctness review of the Gaussian normalized minimax static-oracle separation; depends on gaussian_static_nonlinear_oracle_minimax_gap.md, gaussian_static_oracle_first_chaos_reduction.md, and ../../MATHS.md.

## Verdict

The minimax theorem is correct in its declared universal static-oracle
model. It removes the earlier selected-column-span restriction, but its
quantifiers remain different from the finite-word theorem: for each
source-independent static decoder, a source and a query can be chosen
against it. It neither selects one fixed hard source nor proves a physical
or finite-word result.

## Checked reductions

### Real catalog from the complex upper construction

For a real query \(x\), real \(G\), and complex coefficient output \(Y\),
write \(Y-x=u+iv\). If \(\mathbb E Y=x\), then
\(\mathbb E\operatorname{Re}Y=x\). Taking real parts cannot add nonzero
coordinates. Moreover,

\[
(\operatorname{Re}(Y-x))^TG\operatorname{Re}(Y-x)
=u^TGu
\le u^TGu+v^TGv
=(Y-x)^*G(Y-x).
\]

Thus the real-part law has the same exact mean, no larger support, and no
larger risk. The complex finite catalog therefore supplies the real
blockwise upper law used in the theorem.

### The normalization is analytic, not decoder input

\[
\Gamma_G(A)=\|AG^{-1/2}\|_{\rm op}^2
\]

is used only to state the uniform performance ratio. It need not be known
to the decoder. The Loewner comparison used by the upper construction is
valid:

\[
A^TA
=G^{1/2}(AG^{-1/2})^T(AG^{-1/2})G^{1/2}
\preceq\Gamma_G(A)G.
\]

Hence a coefficient law of \(G\)-risk at most \(19\eta/10\) has output
risk at most \((19\eta/10)\Gamma_G(A)\) for every source \(A\). This is
why the adaptive upper bound is uniform in the stated normalized metric.

### Gaussian comparison

For \(A=UG^{1/2}\), \(\Gamma_G(A)=\|U\|_{\rm op}^2\). The bound

\[
\mathbb E\Gamma_G(A)
\le\left(1+\sqrt{q/p}\right)^2+\frac4p
\]

is valid. The mean norm and concentration ingredients are treated here as
primary-source checked by the root from Vershynin, arXiv:1011.3027,
Theorem 5.32 and Proposition 5.34. The stated \(4/p\) variance allowance
is conservative; Gaussian Poincare gives a smaller constant.

Finite normalized risk implies the Gaussian \(L^2\) condition for the
first-chaos note: integrate the uniform error bound and use
\(\|F\|^2\le2\|F-Ax\|^2+2\|Ax\|^2\).

The signed-permutation first-chaos reduction then gives

\[
\mathcal R_G(F)\kappa_{p,q}
\ge\lambda_{\max}(M^{-1}-G)
\ge t_s(G).
\]

No source-dependent schedule, resident state, or query-dependent support
law enters this lower bound.

## Growing-family arithmetic and strict quantifiers

For \(p=65536q\), \(q=4m\), and \(m\ge1\),

\[
\kappa_{p,q}
\le\left(1+\frac1{256}\right)^2+\frac1{65536}
=1+\frac1{128}+\frac1{32768}
=\frac{33025}{32768}<\frac{101}{100}.
\]

If \(\mathcal R_G(F)\le19\eta/10\), then
\(\lambda_{\max}(M^{-1}-G)<(1919/1000)\eta\). For
\(G=H_\eta^{\oplus m}\), \(\eta\le1/100\), trace monotonicity gives

\[
\frac{s}{m}
\ge\frac{4+\eta}{4+(2919/1000)\eta}+\frac{3000}{2919}
\ge\frac{401000}{402919}+\frac{3000}{2919}
=\frac{793092000}{392040187}
>\frac{101}{50}.
\]

The first summand decreases in \(\eta\), so its minimum on the displayed
range is at \(1/100\). The fraction arithmetic is correct.

Consequently, for every static decoder with \(s\le(101/50)m\), the
uniform normalized-risk inequality

\[
\mathbb E_S\|F_S(A_{:S},x)-Ax\|^2
\le\frac{19}{10}\eta\,\Gamma_G(A)
\]

cannot hold for all nonzero \(A\) and all unit \(x\). Therefore there is a
real source \(A\ne0\) and a real unit query \(x\) for which the strict
reverse inequality holds. This last existence statement follows from the
strict uniform contradiction; it does not assert that either supremum in
\(\mathcal R_G(F)\) is attained.

## Scope

The hard source may depend on the decoder and its fixed schedule. The
argument does not yield a dyadic source, a near-isometric source, a single
source defeating every decoder, a source-trained static lower bound, or a
physical read/page result. Its source-dependent normalization is part of
the performance criterion, not side information supplied to the oracle.

Correctness is supported in this scope. No originality or Cassette-goal
acceptance conclusion follows from this review.
