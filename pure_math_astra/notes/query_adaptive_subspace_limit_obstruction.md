# Rank-two subspace limits and the uniform-witness obstruction; depends on query_adaptive_subspace_containment.md, query_adaptive_q4_sqrt_eta_block.md.

Status: an exact limiting reduction and a reason that a compactness-only
proof cannot yield a uniform square-root lower bound. It does not prove or
refute that lower bound.

Let \(P\) be a real rank-two orthogonal projector on \(\mathbb R^4\), let
\(N=I-P\), and set

\[
 T_r=P+rN,\qquad G_r=T_r^2=P+r^2N.
\tag{1}
\]

For a coordinate pair \(S\), write

\[
 L_S(r)=T_r E_S.
\tag{2}
\]

These are the six planes in the subspace-containment formulation.

## 1. Exact limiting planes

The limit of \(L_S(r)\) depends on the rank of \(P_{SS}\).

* If \(\operatorname{rank}P_{SS}=2\), then \(L_S(r)\to\operatorname{range}P\).
* If \(\operatorname{rank}P_{SS}=0\), then \(E_S\subset\ker P\), so
  \(L_S(r)=E_S\subset\ker P\) for every \(r>0\).
* If \(\operatorname{rank}P_{SS}=1\), let \(n_S\) be a unit vector in
  \(E_S\cap\ker P\), and let \(h_S\) be a unit vector spanning
  \(P E_S\). Then
  \[
   L_S(r)\longrightarrow\operatorname{span}\{h_S,n_S\}.
  \tag{3}
  \]

For the last assertion, choose a second vector in \(E_S\) complementary to
\(n_S\). Its image under \(T_r\) converges to a nonzero vector in the
high line \(P E_S\), while \(T_rn_S=rn_S\) spans the same low line for all
\(r>0\). The two limiting directions are orthogonal because one lies in
\(\operatorname{range}P\) and the other in \(\ker P\).

Thus for unit \(x\in\operatorname{range}P\), unit \(y\in\ker P\), and
\(z=x+y\), the limiting projection values are

\[
 \begin{cases}
  1,&\operatorname{rank}P_{SS}=2,\\
  |\langle x,h_S\rangle|^2+|\langle y,n_S\rangle|^2,
     &\operatorname{rank}P_{SS}=1,\\
  \|\operatorname{Proj}_{E_S}y\|^2,&\operatorname{rank}P_{SS}=0.
 \end{cases}
\tag{4}
\]

Equation (4) is a finite angular feasibility problem on two circles. It
retains the shared-dictionary relation: the high line \(h_S\) and low line
\(n_S\) come from the same coordinate pair, rather than from independently
chosen limiting planes.

## 2. Why a controlled mixed witness would prove the desired lower bound

Suppose one could choose unit \(x\in\operatorname{range}P\) and unit
\(y\in\ker P\), uniformly over \(P\), so that for all sufficiently small
\(r\)

\[
 \max_{|S|=2}\|\operatorname{Proj}_{L_S(r)}(x+y)\|^2\le1+Cr
\tag{5}
\]

with one absolute constant \(C\). In the containment criterion, take
\(v=cr\). Its right side at \(z=x+y\) is

\[
 {1\over1+cr}+{r^2\over r^2+cr}
 =1+r(c^{-1}-c)+O(r^2).
\tag{6}
\]

Choose a fixed \(c>0\) with \(c^{-1}-c>C\). Then (5)--(6) violate the
containment criterion for all small \(r\), proving
\(\Psi_2(P+r^2N)\ge cr\). This is the precise witness target.

## 3. Compactness at the limit is insufficient

At a fixed projector, (4) may admit a witness with every value at most
one. That fact alone does not imply (5), because there need not be a
strict gap below one.

The coordinate projector

\[
 P=\operatorname{Diag}(1,1,0,0)
\tag{7}
\]

already forces this issue. The pair \(\{1,2\}\) has rank two and the pair
\(\{3,4\}\) has rank zero. Therefore every unit mixed witness in (4) has
projection value exactly one on both of these planes. The four remaining
pairs give the constraints

\[
 |x_i|^2+|y_j|^2\le1\qquad(i\in\{1,2\},\ j\in\{3,4\}).
\tag{8}
\]

They are met, for example, by equal coordinate magnitudes, but the two
forced equalities remain. No argument that only takes a compact limit and
then invokes continuity can control their first-order perturbations.

This is not a counterexample to a uniform \(c\sqrt\eta\) lower bound. It
is a concrete obstruction to the proposed shortcut: any such proof must
analyze the order-\(r\) motion of the active limiting planes, or use a
different polar certificate. The unequal paired-block calculation is an
example of this necessity: its limiting witness is active, while its
finite-\(r\) correction decides the strict but lower-order real
improvement.

## 4. Consequence for a limit-family strategy

A contradiction sequence with \(P=P_r\) cannot be closed by extracting
only \(P_r\to P_0\). One must additionally record the ratios between
\(r\) and the small Plucker coordinates of \(P_r\). When a principal
minor tends to zero at order comparable to \(r\), its plane \(L_S(r)\)
has a nontrivial mixed limit not determined by the limiting rank alone.
That is the multi-scale information absent from a bare Grassmannian
compactness argument.
