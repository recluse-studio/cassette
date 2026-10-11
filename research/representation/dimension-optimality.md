# Exact dimension dependence of two-coordinate signed balance

This theorem extends the four-coordinate result. It uses the exact interpreter in
[four-coordinate-decoder.md](four-coordinate-decoder.md), whose three-case formula applies to
every real dimension. The optimized class allows arbitrary random signed coefficients, requires
an unbiased answer, preserves the ordinary coordinate sum on every outcome, and reads at most
two original coordinates. It does not optimize over all possible representations.

## Statement

For an integer \(n\ge2\), define

\[
M_n(x)=\inf\{\mathbb E\|Y\|_2^2:
\mathbb EY=x,\quad \|Y\|_0\le2,\quad
\mathbf1^TY=\mathbf1^Tx\ \text{almost surely}\}.
\]

Set

\[
f_n(l)=\frac{n-8l+\sqrt{n^2+48nl}}4,
\qquad
\Lambda_n=\max_{l\in\{0,1,\ldots,\lfloor n/2\rfloor\}}f_n(l).
\tag{D1}
\]

Then

\[
\sup_{x\ne0}\frac{M_n(x)}{\|x\|_2^2}=\Lambda_n,
\qquad
\sup_{x\ne0}\frac{M_n(x)-\|x\|_2^2}{\|x\|_2^2}=\Lambda_n-1.
\tag{D2}
\]

Only \(\lfloor n/6\rfloor\) and \(\lceil n/6\rceil\) need be evaluated in (D1).
If \(6\) divides \(n\), the exact worst-case variance ratio is \(2n/3-1\).
An extremal query then has five positive entries equal to one for each negative entry equal to
minus one. For \(n=4\), (D2) gives \(\sqrt{13}-2\).

## Proof of the upper bound

Reverse the sign of the query if necessary so that its positive mass \(P\) is at least its
negative mass \(N\). Write \(t=P-N\). Let \(k\) and \(l\) count the strictly positive and
strictly negative coordinates, and let \(m=k+l\le n\). If both signs occur,

\[
\|x\|_2^2\ge P^2/k+N^2/l.
\tag{D3}
\]

In the interpreter's first case, \(P\le3N\), the second moment is \(P^2+N^2\).
With \(u=P/N\in[1,3]\), its ratio is bounded by

\[
\frac{u^2+1}{u^2/k+1/l}.
\]

When \(k\le l\), this expression decreases with \(u\), and its maximum is
\(2kl/(k+l)\le m/2\). When \(k>l\), it increases with \(u\), and its maximum at
\(u=3\) is bounded by the second-case eigenvalue below; the two formulas agree at that
boundary.

In the second case, \(P>3N\) and no positive coordinate exceeds \(t/2+2N\),

\[
M_n(x)=t^2/2+4tN=P^2/2+3PN-7N^2/2.
\]

The largest ratio of this quadratic form to \(P^2/k+N^2/l\) is the largest eigenvalue of

\[
\begin{pmatrix}
k/2 & 3\sqrt{kl}/2\\
3\sqrt{kl}/2 & -7l/2
\end{pmatrix}.
\]

That eigenvalue is

\[
\frac{k-7l+\sqrt{k^2+50kl+49l^2}}4=f_m(l).
\tag{D4}
\]

For \(l\ge m/2\), (D4) is at most \(m/2\). For a fixed \(l\ge0\), \(f_m(l)\)
increases with \(m\), so zeros cannot evade the bound \(\Lambda_n\).

In the third case, let \(h\) be the largest positive coordinate and \(U=P-h\). Its
condition is \(h>U+3N\), and its exact second moment becomes

\[
M_n(x)=h^2+U^2+6UN+N^2.
\tag{D5}
\]

Keep every other coordinate fixed, with squared norm \(d\). Since
\(d\le U^2+N^2\), the ratio

\[
\frac{h^2+U^2+6UN+N^2}{h^2+d}
\]

does not increase as \(h\) increases. Reduce \(h\) to \(U+3N\); the resulting query
lies on the second-case boundary, already bounded above. If \(U=N=0\), the ratio is one.
Queries with only positive coordinates in the second case satisfy
\(M_n(x)=P^2/2\le(n/2)\|x\|_2^2\); their third case uses the same reduction.
This proves the upper bound in (D2).

## Equality and the finite maximization

The value \(f_n(0)=n/2\) is attained by a query whose \(n\) entries are all equal and
positive. For \(1\le l<n/2\), put \(k=n-l\), \(\lambda=f_n(l)\), and choose
equal negative entries and equal positive entries so that

\[
\frac PN=\frac{3k}{2\lambda-k}
=\frac{2\lambda+7l}{3l}.
\tag{D6}
\]

The denominator is positive. Because \(k>l\), this ratio exceeds three. The positive
coordinate count satisfies \(k\ge2\), so every positive coordinate is at most \(P/2\),
and therefore below \(t/2+2N=P/2+3N/2\). This query lies in the second case. It attains
equality in (D3) and the eigenvalue bound (D4). The endpoint \(l=n/2\), when present,
has value \(n/2\), already attained by the all-positive query.

As a real function on \([0,n/2]\),

\[
f_n'(l)=-2+\frac{6n}{\sqrt{n^2+48nl}},
\qquad f_n''(l)<0.
\]

Its unique maximum is at \(l=n/6\), where \(f_n(l)=2n/3\). The integer maximum lies
at the floor or ceiling of that point. For \(n=2\), both candidate values equal one, as
required because the query itself already has at most two coordinates. This completes the proof.

## Meaning for a representation

If a resident description identifies a direction whose contribution is preserved exactly,
the decoder pays no sampling error in that direction. The theorem gives the sharp remaining
Euclidean error factor when that direction is the ordinary sum after sign changes. Larger
blocks retain the two-coordinate read cap but increase their worst-case error factor. The
representation's residual geometry, encoded bytes, and actual page layout still determine
the useful block size.

The source-dependent construction in [signed-block-construction.md](signed-block-construction.md)
uses four-coordinate blocks. Generalizing its exhaustive sign search to \(n\) coordinates
costs \(2^{n-1}\) sign candidates; the dimension theorem does not remove that construction cost.
