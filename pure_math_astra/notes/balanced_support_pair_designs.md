# Balanced-support pair designs: a matching obstruction fails

Status: a verified finite construction and a verified parity obstruction.  This
note isolates a combinatorial condition behind equality in a fixed-basis
sampling bound.  It does not establish novelty or a general Cassette
capability.

Let \(S_i\in\{-1,1\}\), and set \(I_i=(1+S_i)/2\).  A balanced sign law has
\(\sum_iS_i=0\) almost surely, so \(I\) selects exactly half the coordinates.
If \(\mathbb ES_i=0\), then \(\mathbb EI_i=1/2\).  For an edge \(ij\),
\[
\mathbb E(I_iI_j)=\frac14
\quad\Longleftrightarrow\quad
\mathbb E(S_iS_j)=0.
\tag{1}
\]
Thus a sign law with zero correlations on the nonzero Gram edges supplies the
equal-weight fixed-basis estimator \(b_i=2I_i\).

## A fourteen-coordinate construction without a perfect matching

Partition twelve vertices into four labelled triangles
\(T_1,\ldots,T_4\), and add two hubs.  Let the nonzero-edge graph of the Gram
matrix be the complete four-partite graph on the triangles; the hubs are
isolated.  Hence
\[
G=I+\eta A,\qquad 0<\eta<1/9,
\tag{2}
\]
where \(A\) is this adjacency matrix.  The stated range is safely positive
definite: in fact the least eigenvalue of \(A\) is \(-3\), so
\(0<\eta<1/3\) is sufficient.

The complement graph has the two hubs adjacent to one another and to every
triangle vertex, together with the four triangle cliques.  It has no perfect
matching.  After deletion of the two hubs, four odd components remain, which
violates Tutte's condition.

Nevertheless, the following finite sign law satisfies (1) on every nonzero
Gram edge.  Choose \(Y=(Y_1,\ldots,Y_4)\) uniformly from the eight sign
vectors with
\[
\prod_iY_i=-1.
\]
Then \(\sum_iY_i\in\{-2,2\}\).  Give both hubs the sign
\[
h=-\frac12\sum_iY_i.
\]
Conditional on \(Y\), choose independently in triangle \(T_i\), uniformly
among its three sign vectors having coordinate sum \(Y_i\).  This law has
\(8\cdot3^4\) equally likely outcomes.

Every outcome is balanced, because the triangle sums total \(\sum_iY_i\) and
the two hub signs total its negative.  Each triangle coordinate has
conditional mean \(Y_i/3\), while every \(Y_i\) has mean zero.  Each hub also
has mean zero.  For distinct triangles,
\[
\mathbb E(S_{ia}S_{jb})
=\frac19\mathbb E(Y_iY_j)=0,
\qquad i\ne j,
\tag{3}
\]
because every two coordinates of uniform odd-parity \(Y\) are independent.
These are exactly the nonzero off-diagonal Gram edges.  Therefore
\(\mathbb EI_i=1/2\) and the pair inclusion probability on every Gram edge is
\(1/4\).

With \(s=7\) and \(b_i=2I_i\),
\[
\mathbb E(D_bGD_b)-G=I.
\tag{4}
\]
The diagonal is \(4(1/2)-1=1\); every Gram-edge off-diagonal is multiplied by
\(4(1/4)-1=0\).  Since all diagonal energies equal one, the marginal lower
bound is \(u_7=1\).  Hence this construction proves
\[
\Phi_7(G)=1.
\tag{5}
\]
It shows that a perfect matching in the complement is not necessary for this
pair-design mechanism.  The construction is a parity stratification: the
hubs absorb the parity of four odd triangle sums.

## A six-coordinate parity obstruction

Now let the complement graph be two disjoint triangles, with vertex classes
\(A\) and \(B\) of size three.  The matrix
\[
C=\operatorname{blockdiag}\left(
 I_3-\tfrac12(J_3-I_3),\
 I_3-\tfrac12(J_3-I_3)
\right)
\tag{6}
\]
is positive semidefinite, has unit diagonal, is supported on this complement,
and satisfies \(C\mathbf1=0\).  It is therefore a natural pairwise
semidefinite witness for a balanced design with zero correlations across
\(A\) and \(B\).

No such balanced sign law exists.  Indeed, put
\[
X=\sum_{i\in A}S_i,\qquad Y=\sum_{j\in B}S_j.
\]
Balance forces \(Y=-X\), and \(X\) is an odd nonzero integer.  If all
cross-triangle pair correlations vanished, then
\[
0=\sum_{i\in A,j\in B}\mathbb E(S_iS_j)
=\mathbb E(XY)=-\mathbb E(X^2)<0,
\tag{7}
\]
a contradiction.  Thus positive semidefiniteness, unit diagonal, support,
and the row-sum balance condition do not imply realizability by a balanced
sign law.

For the equal-weight Horvitz--Thompson mechanism and the Gram whose
nonzero-edge graph is \(K_{3,3}\), this yields a quantitative obstruction.
If every cross Gram edge has coefficient \(\eta>0\), then the covariance is
\(I+\eta C_{\rm cross}\), where
\[
\sum_{i\in A,j\in B}(C_{\rm cross})_{ij}
=\mathbb E(XY)\leq-1.
\]
For
\(z=(\mathbf1_A,-\mathbf1_B)/\sqrt6\),
\[
z^*\!\left[I+\eta C_{\rm cross}\right]z
=1-\frac{\eta}{3}\mathbb E(XY)
\geq1+\frac{\eta}{3}.
\tag{8}
\]
This is a gap for balanced equal-weight laws.  It does not yet lower-bound
the full fixed-basis optimum, whose weights and support probabilities may
move away from their marginal-equality values.

## Remaining mathematical obstacle

The exact design question is membership in a balanced cut-moment polytope:
which prescribed edge correlations are moments of a balanced sign law with
specified coordinate marginals?  The first graph has no complement perfect
matching but is feasible; the second has a positive semidefinite row-sum-zero
witness but is infeasible.  A theorem that separates these two phenomena
would need a genuinely combinatorial moment condition beyond matching and
the elliptope.  Its novelty and its consequence for actual encoded-basis
libraries remain unestablished.
