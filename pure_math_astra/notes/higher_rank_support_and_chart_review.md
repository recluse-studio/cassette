# Root checks of the first higher-rank reductions

The two K4 lower bounds and the conditional rank-k graph reduction were
reconstructed from their displayed arguments. This record supports those
statements; it does not resolve the uniform rank-k finite lemma.

In k4_cut_space_q6s3_order_r_lower.md, the edge order and normalized
cut vector are consistent with the K4 Laplacian 4I on zero-sum vertex
potentials. Every three-edge subset is a tree or a triangle. The tree
principal determinant is 1/16 and its eigenvalues are at most one, so
its least eigenvalue is at least 1/16. Each triangle principal block
has spectrum (3/4,3/4,0). Its restricted chosen cut vector has squared
norm 1/2 and pseudoinverse energy 2/3.

The chosen cycle vector has squared norm 1/3. Its null projection on
the original triangle has that full squared norm; on each other triangle
it has squared norm 1/27. The displayed triangle estimate has linear
coefficient -32/3+8/(3sqrt(6))<-9 and quadratic coefficient
128/3-64/(3sqrt(6))+4/9<44. The tree estimate and resolvent bounds also
hold on 0<r<=1/1024. The identity-metric lower bound covers the remaining
range. Thus Psi_3(P+r^2(I-P))>=r/1024 for this fixed K4 cut projector.

In k4_cut_space_support_split_lower.md, a deficient support must mean
that P restricted to its coordinate space is noninjective, equivalently
that P_SS is singular. It must not mean that the image has dimension
less than three: a two-edge forest can have an image containing the
chosen cut vector. With the injectivity definition, all supports in the
deficient event are triangles, and every complementary support is a
forest. The distance d=1/sqrt(3) then follows by pairing the chosen
potential with the four normalized potentials constant on a triangle.
The forest inverse estimate gives M=4.

The support-event bound p<=V/(a^2d^2), the complementary expected
cycle estimate, and eventwise Cauchy--Schwarz produce exactly
V^2+r^2b^2V>=r^2a^2d^2b^2/4 in the small-V branch. The stated
all-range positive constant follows by solving this quadratic and
using r<=1. It is weaker numerically than 1/1024 but supplies a general
fixed-projector proof mechanism.

In rank_k_graph_chart_reduction.md, Schur complementation leaves the
square submatrix K_{E,J}, with both index sets of size j. The correct
condition is

\[
 (n_J+K_{E,J}^Tu_E)^T
 (I_j+K_{E,J}^TK_{E,J})^{-1}
 (n_J+K_{E,J}^Tu_E)\le\|u_E\|^2.
\]

This matrix stays positive definite even when the submatrix is singular.
The maximum-volume row pivot bounds ||Z|| by k. The two metric
comparisons give G_r(P)>=H/[(1+k^2)(1+2k^2)]. With a hypothetical
uniform feasible ||n||>=rho_k, the proposed
c_k=rho_k/[4(k^2+2)] makes the resolvent excess positive and gives
the stated conditional coefficient
rho_k/[4(k^2+2)(1+k^2)(1+2k^2)].

The finite k-polar lemma is proved here only at k=2 through the earlier
scalar argument. For k>=3, the coupled square-submatrix constraints
remain open. The chart reduction makes that open statement exact; it
does not establish the premise by analogy.
