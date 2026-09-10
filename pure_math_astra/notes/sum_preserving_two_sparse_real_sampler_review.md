# Real two-sparse sampler with an exact sum constraint

Status: proved explicit upper bound. It answers the posed strict-sub-\(2\)
question affirmatively. It does not identify the optimum over all
sum-preserving two-sparse laws, and it makes no novelty claim.

For \(x\in\mathbb R^4\), write

\[
 r^2=\|x\|_2^2,\qquad t=\sum_{i=1}^4x_i.
\]

Both samplers below have at most two nonzero coordinates in every outcome,
satisfy \(\sum_iY_i=t\) almost surely, and obey \(\mathbb EY=x\).

## Uniform-pair sampler

Choose an unordered pair \(\{i,j\}\) uniformly from the six pairs, and put

\[
 Y_i=\frac t2+\frac32(x_i-x_j),\qquad
 Y_j=\frac t2+\frac32(x_j-x_i),
\tag{1}
\]

with all other coordinates zero. The two displayed entries sum to \(t\).
For coordinate \(i\), averaging over its three incident pairs gives

\[
 \frac16\sum_{j\ne i}
 \left(\frac t2+\frac32(x_i-x_j)\right)=x_i.
\tag{2}
\]

For a selected pair, the squared norm is

\[
 \frac{t^2}{2}+\frac92(x_i-x_j)^2.
\]

Using \(\sum_{i<j}(x_i-x_j)^2=4r^2-t^2\), this gives

\[
 \mathbb E\|Y-x\|_2^2
 =2r^2-\frac{t^2}{4}.
\tag{3}
\]

## Positive-negative flow sampler

Let

\[
 P=\sum_i(x_i)_+,\qquad N=\sum_i(-x_i)_+.
\]

If \(P,N>0\), choose \(I\) and \(J\) independently with

\[
 \Pr(I=i)=\frac{(x_i)_+}{P},\qquad
 \Pr(J=j)=\frac{(-x_j)_+}{N},
\]

and return

\[
 Y=Pe_I-Ne_J.
\tag{4}
\]

The chosen coordinates are distinct, since one is positive and the other
negative. Thus the support cap holds; moreover

\[
 \mathbf1^TY=P-N=t,\qquad \mathbb EY=x,\qquad
 \mathbb E\|Y\|_2^2=P^2+N^2.
\tag{5}
\]

If \(x=0\), return zero. For a nonzero query, if \(N=0\), choose \(I\) with probability \(x_i/P\) and return \(Pe_I\).
If \(P=0\), use the analogous negative singleton. These endpoint rules
retain (5). Since

\[
 P^2+N^2=\frac{\|x\|_1^2+t^2}{2}
 \le2r^2+\frac{t^2}{2},
\]

the flow risk satisfies

\[
 \mathbb E\|Y-x\|_2^2\le r^2+\frac{t^2}{2}.
\tag{6}
\]

## A uniform strict bound

Select the flow sampler when \(t^2\le4r^2/3\), and otherwise select the
uniform-pair sampler. Equations (3) and (6) imply

\[
 \mathbb E\|Y-x\|_2^2\le\frac53r^2.
\tag{7}
\]

In particular,

\[
 \sup_{\|x\|_2=1}\inf
 \{\mathbb E\|Y-x\|_2^2:
   \|Y\|_0\le2,\ \mathbf1^TY=\mathbf1^Tx,\ \mathbb EY=x\}
 \le\frac53<2.
\tag{8}
\]

The selector uses only \(t\) and \(r^2\), so it is query adaptive but source
independent. For rational \(x\), all outcomes and probabilities in (1)
and (4) are rational. This does not bound the random-bit cost of sampling
arbitrary rational probabilities.

## A small sharpening for this two-sampler selector

The bound in (7) can be sharpened without claiming global optimality. Let

\[
 \gamma=\frac{19+3\sqrt2}{14}=1.660\ldots<\frac53.
\tag{9}
\]

Then the better of (3) and the exact flow risk in (5) is at most
\(\gamma r^2\).

To verify this, scale to \(r=1\) and replace \(x\) by \(-x\), if needed,
so \(P\ge N\). Let \(a\) and \(b\) be the numbers of positive and
negative coordinates, ignoring zeros. When \(a,b\le2\), direct
Cauchy--Schwarz within the two sign groups gives flow risk at most \(1\).
When \(a=1,b=3\), the constraints

\[
 P^2+\frac{N^2}{3}\le1,\qquad P\ge N
\]

give flow risk at most \(1/2\). With only one sign group, the flow and
uniform risks are \(P^2-1\) and \(2-P^2/4\), whose minimum is at most
\(7/5\). The only case that can exceed \(3/2\) is \(a=3,b=1\), where

\[
 \frac{P^2}{3}+N^2\le1.
\tag{10}
\]

Set

\[
 N_0^2=\frac{3}{12+4\sqrt2}.
\]

At \(N=N_0\), the boundary in (10) has
\(P=(1+2\sqrt2)N_0\), and the two risks agree at \(\gamma\). For a short
global check, write

\[
 d=2\sqrt{2-\gamma}=2\sqrt2N_0.
\]

If the uniform-pair risk exceeds \(\gamma\), then \(P-N<d\). If also
\(N\le N_0\), this yields \(P<N+d\), and the flow risk is at most
\((N+d)^2+N^2-1\le\gamma\). If \(N\ge N_0\), (10) directly gives flow
risk at most \(2-2N^2\le\gamma\). This also covers the endpoints by
continuity.

Equality occurs for the stated three-equal-positive, one-negative vector,
so \(\gamma\) is the worst value of this particular two-sampler selector.
A different admissible law may improve it; no lower bound for the original
infimum is asserted.

## Consequence for the equicorrelation metric

For \(H_\eta=\mathbf1\mathbf1^T+\eta I_4\), the exact sum constraint
annihilates the rank-one term in the error. Therefore this real sampler has

\[
 \mathbb E(Y-x)^TH_\eta(Y-x)
 \le\gamma\eta\|x\|_2^2.
\tag{11}
\]

It yields a real query-adaptive hard-two-coordinate law for every
\(\eta>0\), with no small-\(\eta\) or complex-catalog assumption. The
conclusion is mathematical. It does not by itself provide finite resident
catalog bytes, a bounded-bit sampler, or a native execution account.
