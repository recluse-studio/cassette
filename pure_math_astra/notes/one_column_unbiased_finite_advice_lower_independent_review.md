# Independent review: finite advice lower bound for one observed column

Verdict: the proposed theorem is correct in its declared model. For
\(p>q\ge2\), at most \(N\) source-selected states, and exactly one
observed column with a state-fixed probability vector, the proof yields

\[
 C\ge(q-1)
 \left(\frac{p-q}{p-1}\right)^{2/(p-q)}N^{-4/(p-q)}.
\]

I found no defect in the rectangular operator, the endpoint \(p=q+1\),
the zero-probability reduction, or the label-specific basis argument. This
is a correctness review only. It makes no originality or application
significance finding.

## 1. Rectangular conditional averaging

Let \(a\in S^{p-1}\) and let \(W\in\mathcal V_{p,q-1}\) be the other
columns of a uniform ordered \(q\)-frame. The operator

\[
 (Tf)(W)=\mathbb E[f(a)\mid W]
\]

maps \(L^2(S^{p-1})\) to \(L^2(\mathcal V_{p,q-1})\). For \(T^*T\),
condition first on \(a\), sample \(W\subset a^\perp\), and then sample
\(a'\in W^\perp\). Given \(W\), the ambient dimension of \(W^\perp\)
is \(p-q+1\), so the density of \(t=a^Ta'\) is proportional to

\[
 (1-t^2)^{(p-q-2)/2}.
\]

Dividing by the usual coordinate density
\((1-t^2)^{(p-3)/2}\) on \(S^{p-1}\) gives

\[
 (T^*Tf)(a)=\int_{S^{p-1}}
 \frac{\kappa_{p,q}}{(1-(a^Ta')^2)^{(q-1)/2}}
 f(a')\,d\sigma(a'),
\]

where the ratio of the two coordinate-density normalizers is exactly

\[
 \kappa_{p,q}=
 \frac{\Gamma((p-q+1)/2)\Gamma((p-1)/2)}
 {\Gamma((p-q)/2)\Gamma(p/2)}.
\]

This confirms the displayed kernel and constant. When \(p=q+1\), the
conditional exponent is \(-1/2\), hence integrable. More generally
\(p>q\) is exactly the condition needed for integrability. Truncating the
positive zonal kernel produces Hilbert--Schmidt kernels; the row and column
integrals of the tails vanish by monotone convergence. Schur's estimate
makes \(T^*T\) compact. If \(f_n\rightharpoonup0\), compactness gives
\(T^*Tf_n\to0\) in norm and

\[
 \|Tf_n\|^2=\langle f_n,T^*Tf_n\rangle\to0.
\]

Thus the rectangular \(T\) itself is compact. The atomic-matching proof
uses only compactness between the two probability spaces, so it applies
unchanged.

## 2. The small-cell constant

Put \(r=(p-1)/(q-1)>1\) and
\(\alpha=(p-q)/(p-1)\). A superlevel set of the kernel is two polar caps
with sine

\[
 \left(\frac{\kappa_{p,q}}{\lambda}\right)^{1/(q-1)}.
\]

The elementary two-cap bound gives

\[
 \sigma\{k(a^T\cdot)>\lambda\}
 \le\left(\frac{\kappa_{p,q}}{\lambda}\right)^r.
\]

Rearrangement or layer-cake integration therefore gives

\[
 \sup_a\int_B k(a^Ta')d\sigma(a')
 \le D_{p,q}\sigma(B)^\alpha,
 \qquad
 D_{p,q}=\frac{p-1}{p-q}\kappa_{p,q}.
\]

The kernel has row integral one and is pointwise at least
\(\kappa_{p,q}\), so \(\kappa_{p,q}\le1\). Hence
\(D_{p,q}\le(p-1)/(p-q)\). Applying the preceding estimate to
\(\langle1_A,T^*T1_A\rangle\), then Cauchy--Schwarz, proves the stated
countable disjoint-cell bound with factor
\(\sqrt{D_{p,q}}h^{\alpha/2}\). The exponents are consistent:

\[
 \frac{p-1}{2}\frac{p-q}{2(p-1)}=\frac{p-q}{4}.
\]

## 3. Exactness with one selected coordinate

After averaging the explicitly source-independent Borel output kernel over
its internal seed, Jensen preserves exactness and cannot increase squared
risk. A state with \(\pi_j=0\) is null: at query \(e_j\), its other
branch outputs would determine \(a_j\) from the other \(q-1\) columns.
Conditional on those columns, \(a_j\) is uniform on
\(S^{p-q}\), which is nonatomic because \(p>q\). A finite union of such
state cells remains null.

For a remaining state, choose \(j\) with
\(0<\theta=\pi_j\le1/q\). Let \(a=a_j\), let \(W\) be the other
columns, and average the non-\(j\) outputs into

\[
 H(W)=\frac1{1-\theta}\sum_{i\ne j}\pi_iF_i(a_i,e_j).
\]

Exactness at \(e_j\) gives
\(\theta F(a)+(1-\theta)H(W)=a\). Atomic matching applied to

\[
 f(a)=\theta F(a)-a,
 \qquad g(W)=-(1-\theta)H(W)
\]

provides countably many shared values. Jensen across the non-\(j\)
branches gives, for any shared value \(c\),

\[
 C\ge\frac{\|(1-\theta)a+c\|^2}{\theta(1-\theta)}.
\]

Thus the relevant sphere cell lies in a ball of radius

\[
 \sqrt{\frac{C\theta}{1-\theta}}
 \le\sqrt{\frac{C}{q-1}}.
\]

For \(C<q-1\), this is strictly below one and has spherical measure at
most

\[
 h=\tfrac12\left(\frac{C}{q-1}\right)^{(p-1)/2}.
\]

This single coordinate query is enough. It relies on the least-probable
coordinate, and it does not assume a query-adaptive law or a finite number
of shared values.

## 4. Final constants and basis states

The small-cell bound applied to each of the at most \(N\) state cells
gives

\[
 1\le N\sqrt{D_{p,q}}\,
 2^{-(p-q)/(2(p-1))}
 \left(\frac{C}{q-1}\right)^{(p-q)/4}.
\]

Using \(D_{p,q}\le(p-1)/(p-q)\) and discarding the displayed factor below
one yields the claimed result. When \(p\ge2q\),
\((p-1)/(p-q)\le2\), and \(N\le2^b\) yields

\[
 C\ge(q-1)2^{-(4b+2)/(p-q)}.
\]

For a fixed label basis \(Q_\ell\), transform the source to
\(AQ_\ell\) and use original query \(Q_\ell e_j\). The transformed
source is still uniform on the Stiefel manifold and its cell has the same
measure. Different labels may use different fixed \(Q_\ell\), because
the argument bounds the cells separately before summing. A basis varying
with the source inside one label remains outside the theorem.

The no-advice comparison is also exact: uniform one-column sampling with
output \(q a_jx_j\) has second moment \(q\|x\|^2\), mean \(Ax\), and
risk \((q-1)\|x\|^2\).

## Conclusion

The proof establishes the stated lower bound for static, exactly unbiased,
one-observed-column decoders with finitely many source-selected states.
It correctly excludes zero-probability coordinate states up to null
Stiefel measure and includes the endpoint \(p=q+1\). I found no
counterexample or unaddressed quantifier failure in the declared scope.

## Reviewed source

- [Proposed theorem](one_column_unbiased_finite_advice_lower.md).

## Addendum: stronger direct conditional-fiber proof

The proposed compact-operator proof is correct, but it is unnecessary for
this one-observed-column theorem. A direct argument gives a stronger
constant.

For the least-probable coordinate in a nondegenerate state, write
\(\theta=\pi_j\le1/q\), \(a=a_j\), and let \(W\) be the remaining
columns. Define \(H(W)\) as above. Exactness gives

\[
 \theta F(a)+(1-\theta)H(W)=a.
\]

Jensen on all non-\(j\) branches gives the actual coordinate-query risk
lower bound

\[
 \begin{aligned}
 R(A,e_j)
 &\ge \theta\|F(a)-a\|^2+(1-\theta)\|H(W)-a\|^2\\
 &=\frac{1-\theta}{\theta}\|H(W)-a\|^2.
 \end{aligned}
\]

Hence every frame in this label cell satisfies

\[
 \|a-H(W)\|\le
 \sqrt{\frac{C\theta}{1-\theta}}
 \le\sqrt{\frac{C}{q-1}}=\delta.
\]

Conditional on \(W\), the missing column is uniform on the unit sphere in
\(W^\perp\), which is \(S^{p-q}\). If \(C<q-1\), then \(\delta<1\),
and the spherical ball estimate bounds the conditional measure of the
state-cell section by

\[
 \frac12\delta^{p-q}
 =\frac12\left(\frac{C}{q-1}\right)^{(p-q)/2}.
\]

Fubini therefore bounds every nonnull state cell by that quantity. The
zero-probability states are null by the same fiber argument. Summing the
at most \(N\) cells gives

\[
 1\le\frac N2\left(\frac{C}{q-1}\right)^{(p-q)/2}.
\]

Together with the trivial case \(C\ge q-1\), this proves the stronger
bound

\[
 \boxed{\quad
 C\ge(q-1)\min\left\{1,\left(\frac2N\right)^{2/(p-q)}\right\}.
 \quad}
\]

It implies the weaker advertised consequence
\(C\ge(q-1)N^{-2/(p-q)}\). The argument retains the same static-state,
exact-mean, exactly-one-column scope. It needs neither atomic matching nor
the rectangular compactness calculation. Fixed label-specific right bases
are handled by the same per-label right rotation used above.
