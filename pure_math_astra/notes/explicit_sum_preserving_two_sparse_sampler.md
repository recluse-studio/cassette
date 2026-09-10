# An explicit real sum-preserving two-sparse sampler in four coordinates

Status: proved elementary construction.  This note gives a query-adaptive
real sampler; it does not assert optimality among two-sparse laws, a native
execution result, or a full Cassette resource result.

For \(x\in\mathbb R^4\), write

\[
 t=\mathbf1^Tx,\qquad n^2=\|x\|_2^2.
 \tag{1}
\]

The construction chooses one of two finite laws.  Every outcome \(Y\) has
at most two nonzero coordinates and satisfies \(\mathbf1^TY=t\).

## Finite pair formulation

This is also a finite active-set convex problem.  Orient the six edges of
the complete graph on four coordinates and let \(B\) be its incidence
matrix.  If edge \(e=ij\) has probability \(p_e\), write its conditional
outcome as

\[
 \frac t2(e_i+e_j)+a_e(e_i-e_j),\qquad f_e=p_ea_e.
 \tag{2}
\]

With \(\theta_i=\sum_{e\ni i}p_e\), exact mean is precisely

\[
 x=\frac t2\theta+Bf.
 \tag{3}
\]

Conditional Jensen shows that randomizing further after choosing an edge
cannot lower the second moment.  Thus the minimum second moment among all
sum-preserving two-sparse laws is the value of

\[
 \min_{p,f}\left\{\frac{t^2}{2}+2\sum_e\frac{f_e^2}{p_e}:
 p_e\ge0,\ \sum_ep_e=1,\ x=\frac t2\theta+Bf\right\},
 \tag{4}
\]

where \(f_e=0\) when \(p_e=0\) and \(0/0=0\).  Each perspective
\(f_e^2/p_e\) is convex.  The two laws below are explicit feasible points;
no claim that either solves (4) is needed.

## Uniform-pair law

Choose one of the six unordered pairs \(\{i,j\}\) uniformly.  For \(i<j\),
return

\[
 Y^{ij}=
 \left(\frac t2+\frac32(x_i-x_j)\right)e_i+
 \left(\frac t2-\frac32(x_i-x_j)\right)e_j.
 \tag{5}
\]

Each outcome has coordinate sum \(t\).  At coordinate \(i\), averaging the
three pairs containing it gives

\[
 \frac16\sum_{j\ne i}
 \left(\frac t2+\frac32(x_i-x_j)\right)
 =\frac t4+\frac14(4x_i-t)=x_i.
 \tag{6}
\]

Thus \(\mathbb EY^{U}=x\).  Put \(q=x-t\mathbf1/4\).  The squared norm of
(5) is \(t^2/2+(9/2)(x_i-x_j)^2\).  Since

\[
 \sum_{i<j}(x_i-x_j)^2=4\|q\|_2^2=4n^2-t^2,
 \tag{7}
\]

its exact variance is

\[
 V_U(x):=\mathbb E\|Y^{U}-x\|_2^2
 =2n^2-\frac{t^2}{4}.
 \tag{8}
\]

## Signed-mass transport law

Let

\[
 P=\sum_{x_i>0}x_i,\qquad N=\sum_{x_i<0}(-x_i).
 \tag{9}
\]

If \(P,N>0\), independently choose \(I\) and \(J\) with

\[
 \Pr\{I=i\}=\frac{x_i}{P}\quad(x_i>0),\qquad
 \Pr\{J=j\}=\frac{-x_j}{N}\quad(x_j<0),
 \tag{10}
\]

and return

\[
 Y^{F}=Pe_I-Ne_J.
 \tag{11}
\]

The signs make \(I\ne J\), so this is two-sparse.  Its coordinate sum is
\(P-N=t\), and its mean is the positive part of \(x\) plus its negative
part, hence \(\mathbb EY^F=x\).  It has at most four pair outcomes: with
both signs present, one sign set has at most two coordinates.

If \(N=0\), choose \(I=i\) with probability \(x_i/P\) and return \(Pe_I\).
If \(P=0\), use the analogous \(-Ne_J\).  If \(x=0\), return zero.  These
three boundary rules keep the same support, sum, and mean properties.

Every nonzero outcome in (11) has squared norm \(P^2+N^2\), including the
one-sign cases after setting the absent mass to zero.  Consequently

\[
 \begin{aligned}
 V_F(x)&=P^2+N^2-n^2\\
 &=\frac{\|x\|_1^2+t^2}{2}-n^2\\
 &\le n^2+\frac{t^2}{2},
 \end{aligned}
 \tag{12}
\]

where the final line is Cauchy--Schwarz in four coordinates.

## Fixed selector and uniform bound

Choose the uniform-pair law when

\[
 t^2\ge\frac43n^2,
 \tag{13}
\]

and otherwise choose the signed-mass transport law.  The selector uses only
addition, multiplication, comparison, and coordinate signs.  From (8), in
the first case,

\[
 V_U(x)\le\left(2-\frac13\right)n^2=\frac53n^2.
 \tag{14}
\]

From (12), in the second case,

\[
 V_F(x)\le\left(1+\frac23\right)n^2=\frac53n^2.
 \tag{15}
\]

Therefore the selected law obeys

\[
 \mathbb EY=x,\qquad \|Y\|_0\le2,\qquad
 \mathbf1^TY=\mathbf1^Tx\ \text{almost surely},\qquad
 \mathbb E\|Y-x\|_2^2\le\frac53\|x\|_2^2.
 \tag{16}
\]

For rational \(x\), every outcome value and probability in (5), (10), and
the one-sign rules is rational.  Uniform-pair sampling has six outcomes;
the transport law has at most four.  An exact rational sampler can therefore
be declared directly.  Here is one explicit finite-word account.  Suppose
the rational query is supplied as \(x_i=z_i/D\), with one positive common
denominator and signed \(b\)-bit numerators.  The uniform law uses rejection
from three fair bits and consumes four random bits in expectation.  For the
transport law, let \(A=\sum_{z_i>0}z_i\) and
\(B=\sum_{z_i<0}(-z_i)\).  To select a positive coordinate, draw
\(L_A=\lceil\log_2A\rceil\) fair bits until the resulting integer lies in
\(\{0,\ldots,A-1\}\), then use cumulative integer weights.  The negative
selection is identical with \(B\).  A zero mass requires no draw.  This
uses at most \(2L_A+2L_B\le4(b+1)\) random bits in expectation when both
masses are nonzero.  The selector compares
\(3(\sum_i z_i)^2\) with \(4\sum_i z_i^2\), and the output numerators have
at most \(b+3\) bits over denominator \(2D\).  These are constant-many
integer operations in dimension four, but an actual bit-operation or native
runtime cost still depends on the chosen integer implementation.

## Equicorrelation consequence and rounding

Let \(H_\eta=\mathbf1\mathbf1^T+\eta I_4\).  Every error \(e=Y-x\) in
(16) has \(\mathbf1^Te=0\) outcome by outcome.  Hence

\[
 e^TH_\eta e=\eta\|e\|_2^2,
 \qquad
 \mathbb E e^TH_\eta e\le\frac53\eta\|x\|_2^2.
 \tag{17}
\]

For \(G=H_\eta^{\oplus m}\), apply the selector separately in every block
and concatenate the results.  The construction preserves the query mean,
has hard support cap \(2m\), and has ideal risk at most

\[
 \frac53\eta\|x\|_2^2.
 \tag{18}
\]

If \(A^TA=G\), \(W=A+E\), and \(\|E\|_{\rm op}\le r_0\), blockwise
sum preservation gives \(\|A(Y-x)\|_2=\sqrt\eta\|Y-x\|_2\).  Thus

\[
 \mathbb E\|W(Y-x)\|_2^2
 \le\frac53(\sqrt\eta+r_0)^2\|x\|_2^2.
 \tag{19}
\]

The previous finite-word condition \(r_0\le\sqrt\eta/20000\) is more than
enough to make the coefficient in (19) smaller than \(1.9\eta\).  Unlike
the earlier finite-catalog bridge, this sampler needs no stored catalog or
query-selected catalog index.  It still needs a declared exact sampler,
query representation, physical-page layout, and native execution account.
