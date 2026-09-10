# A subspace-containment form of the remaining adaptive problem

Status: an exact reformulation of the atomic dual, not a novelty claim.
It gives a geometric form of the unresolved small-eigenvalue problem.

Let G>0 be real, let E_S embed the coordinates in S, and put

\[
 L_S=\operatorname{range}(G^{1/2}E_S),\qquad |S|=s.
 \tag{1}
\]

Let P_S be the orthogonal projector onto L_S. The image under G^{1/2}
of the atomic body for unbiased s-sparse sampling is

\[
 \mathcal B=\operatorname{conv}
    \bigcup_{|S|=s}\{y\in L_S:\|y\|\le1\}.
 \tag{2}
\]

Its support function is

\[
 h_{\mathcal B}(z)=\max_{|S|=s}\|P_S z\|.
 \tag{3}
\]

Indeed, a linear functional achieves its maximum over a convex hull on
the union being convexified, and its maximum over a subspace unit ball
is the norm of its orthogonal projection.

By the atomic-gauge identity, a bound Ψ_s(G)≤v is equivalent to
γ(x)²≤x^T(G+vI)x for all x. Therefore it is equivalent to containment
in (2) of the ellipsoid with shape matrix G(G+vI)^{-1}. Support
functions characterize containment of compact convex sets, so

\[
 \Psi_s(G)\le v
 \iff
 \max_{|S|=s}z^TP_Sz
       \ge z^TG(G+vI)^{-1}z
       \quad\text{for every }z .
 \tag{4}
\]

Equivalently,

\[
 \min_{|S|=s}\operatorname{dist}(z,L_S)^2
       \le v\,z^T(G+vI)^{-1}z
       \quad\text{for every }z .
 \tag{5}
\]

The subspaces in this formulation are constrained. They are the coordinate
subspaces of one invertible dictionary G^{1/2}; they are not an arbitrary
list of s-dimensional planes. Dropping that relation would change the
optimization problem.

For the difficult family G=P+η(I-P), with P a rank-two orthogonal
projector in four dimensions and s=2, the right side of (4) is

\[
 \frac{\|Pz\|^2}{1+v}
       +\frac{\eta\|(I-P)z\|^2}{\eta+v}.
 \tag{6}
\]

Thus a hypothetical v=o(√η) would require the six transformed coordinate
planes to cover this anisotropic quadratic requirement for every mixed
high- and low-eigenspace direction z.

The exact paired-block results settle some structured plane families.
The fixed-projector sparse-null filter settles other fixed planes.
Neither controls arbitrary P=P_η approaching a singular-minor stratum
at several rates. A proof or counterexample must retain both the complete
mixed-direction condition (6) and the common-dictionary relation (1).

The inverse-hull formulation in
query_adaptive_inverse_hull_design_audit.md gives a second exact route.
For a fixed query its inner optimization is finite multiresponse
c-optimal experimental design. That connection is established prior
mathematics; the present reformulation should not be presented as a new
duality theorem.
