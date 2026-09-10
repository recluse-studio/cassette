# Independent proof of the critical-scale scalar \(n=u\) lemma

Status: proved.  This note verifies the sufficient scalar lemma in
`critical_scale_2x2_polar_algebra.md`; it does not claim that the scalar
choice characterizes every feasible pair.

Let

\[
 K=\begin{pmatrix}a&b\\c&d\end{pmatrix},\qquad a,d\leq0.
\tag{1}
\]

The coordinate sign symmetry permits conjugation by
\(\operatorname{Diag}(1,-1)\).  It preserves the diagonal entries and
replaces \((b,c,x)\) by \((-b,-c,-x)\).  It is therefore enough to treat

\[
 b+c=-e<0,\qquad
 a=-\alpha,\quad d=-\delta,\qquad
 \alpha,\delta\geq0,\quad e>0.
\tag{2}
\]

Write

\[
 b=w-{e\over2},\quad c=-w-{e\over2},\quad
 z=\delta-\alpha,\quad \sigma=\alpha+\delta,\quad
 D=\det K=\alpha\delta+w^2-{e^2\over4}.
\tag{3}
\]

For \(u=n=(1,x)^T\) with \(x>0\), put

\[
 h={1-x^2\over2x}.
\tag{4}
\]

The two off-diagonal coordinate inequalities are equivalent to

\[
 h\in J:=\left[w-{e\over2},\ w+{e\over2}\right].
\tag{5}
\]

Thus every \(h\in J\) determines a coordinate-feasible scalar candidate.

Let \(N_K(x)=A+2Bx+Cx^2\) be the numerator from equations (9)--(10) of
the critical-scale algebra note.  Since
\(\det(I+K^TK)(1+x^2)>0\), the ellipsoidal condition is exactly
\(N_K(x)\leq0\).  Direct substitution of (2)--(4) gives the identity

\[
 {N_K(x)\over1+x^2}
 =-\sigma(1+D)+
 {\bigl[z(1-D)-2ew\bigr]h-2wz-e(1-D)
  \over\sqrt{1+h^2}}.
\tag{6}
\]

The case \(4ad\ge(b+c)^2\) was already settled in the critical-scale
note: then \(K+K^T\preceq0\), so every coordinate-feasible scalar
candidate satisfies the ellipsoidal condition.  It remains to consider

\[
 k^2:={e^2\over4}-\alpha\delta>0,\qquad D=w^2-k^2.
\tag{7}
\]

## The case \(D\ge-1\)

Choose \(h=w\), which lies in \(J\).  Equation (6) becomes

\[
 {N_K(x)\over1+x^2}
 =-(1+D)\left(\sigma+{zw\over\sqrt{1+w^2}}\right)
  -{e(1+w^2+k^2)\over\sqrt{1+w^2}}<0.
\tag{8}
\]

Indeed, \(\sigma\ge|z|\), so the first parenthesis is nonnegative, while
the second term is strictly negative.  This includes \(D=-1\).

## The case \(D<-1\)

Put

\[
 L=-1-D>0,\qquad
 \gamma=4\alpha\delta=e^2-4k^2\ge0.
\tag{9}
\]

Since \(k^2=L+w^2+1\), the last identity in (9) implies
\(e>2|w|\).  In particular

\[
 v={e\over2}-w>0,\qquad J=[-v,\,w+e/2].
\tag{10}
\]

First suppose that \(h_0=-z/e\) belongs to \(J\).  At \(h=h_0\),
equation (6) simplifies to

\[
 {N_K(x)\over1+x^2}
 =L\sqrt{z^2+\gamma}-(L+2)\sqrt{z^2+e^2}<0.
\tag{11}
\]

The strict inequality follows from \(\gamma\le e^2\).

Suppose next that \(h_0<-v\).  Then \(z>ev>0\).  At the lower endpoint
\(h=-v\), multiply (6) by \(s_v=\sqrt{1+v^2}\) and define

\[
 f(z)=Ls_v\sqrt{z^2+\gamma}-(Lv+e)z
      +e(2wv-L-2).
\tag{12}
\]

For fixed \(L,w,e,\gamma\), its derivative on \(z\ge ev\) obeys

\[
 f'(z)
 \le L(s_v-v)-e<0.
\tag{13}
\]

For the strict final inequality, substitute \(w=e/2-v\) into (9):

\[
 \gamma=4(ev-v^2-L-1)\ge0,\qquad
 L\le ev-v^2-1.
\tag{14}
\]

Because \(s_v-v=1/(s_v+v)\), equation (14) gives

\[
 L(s_v-v)
 \le(ev-v^2-1)(s_v-v)<e;
\tag{15}
\]

the last comparison is equivalent to
\(ev-v^2-1<e(s_v+v)\), whose difference is \(es_v+v^2+1>0\).
At \(z=ev\), equation (11) applies at the endpoint \(h_0=-v\), so
\(f(ev)<0\).  Equations (13)--(15) then give \(f(z)<0\) for every
lower-clipped case.

Finally, if \(h_0>w+e/2\), exchange the two coordinates.  In the
parameters above this is

\[
 (z,w,h)\longmapsto(-z,-w,-h).
\tag{16}
\]

It preserves (6), maps the upper-clipped case to the lower-clipped case,
and preserves all sign hypotheses.  Thus it too has a feasible \(h\) with
\(N_K(x)<0\).

## Conclusion

For every real \(K\) with nonpositive diagonal, there is a real \(x\)
satisfying the two coordinate inequalities and \(F_K(x)\le1\).  Taking

\[
 u=n={ (1,x)^T\over\sqrt{1+x^2}}
\tag{17}
\]

therefore satisfies every condition of the finite polar lemma and has
\(\|n\|_2=\|u\|_2\).  The unresolved premise in the graph-chart bridge
holds with \(\rho=1\).
