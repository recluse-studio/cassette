# Uniform local geometry near a reciprocal covariance locus

Status: bounded scope analysis for the fixed-spectrum transform theorem. It
does not establish a finite-precision implementation or a novelty claim.

## 1. What remains uniform

Let \(D(h)\) be a smooth one-parameter family of diagonal spectra on a
compact parameter interval. Assume throughout that

\[
 0<a_-\leq a_i(h)\leq a_+,\qquad
 |a_i(h)-a_j(h)|\geq\gamma>0\quad(i\ne j),
\tag{1}
\]

and that the read cap \(s\) and multiplicities are fixed. Let \(t(h)\) and
\(p_i(h)=a_i(h)/(a_i(h)+t(h))\) be the spectral water level and its
marginals. Then, after shrinking the interval if needed,

\[
 0<\rho\leq p_i(h)\leq1-\rho.
\tag{2}
\]

Let \(\mathcal C_h\) be the exact-size subset-moment coefficient set and
retain the moment gauge

\[
 f_h(B)=\min_{c\in\mathcal C_h}\lVert B\circ c\rVert_F.
\tag{3}
\]

There are constants independent of \(h\) such that the local normal form is

\[
 c\bigl(\lVert B\rVert_F^2+f_h(B)\bigr)
 \leq\Phi_s(G_h(B))-t(h)
 \leq C\bigl(\lVert B\rVert_F^2+f_h(B)\bigr).
\tag{4}
\]

The proof is the same as the fixed-spectrum proof, but no conversion of
\(f_h\) to a discrete support norm is permitted. The constants are uniform:

- (1) makes the orbit chart and its Taylor bounds uniform;
- (2) uniformly bounds HT weights, the exact-marginal repair radius, and
  all second moments;
- the coefficient sets \(\mathcal C_h\) are uniformly bounded;
- the quantitative rigidity coefficient stays positive uniformly on this
  compact positive spectral family.

The arbitrary-weight lower reduction directly produces a
\(c_h\in\mathcal C_h\) with
\(\lVert B\circ c_h\rVert_F\lesssim\delta+\lVert B\rVert_F^2\), so it also
has uniform constants. The fixed-support comparison lemma does not: its
threshold is the minimum nonzero coefficient over finitely many support
patterns, and that threshold can tend to zero with \(h\).

## 2. The four-coordinate reciprocal crossover

For \(q=4\), \(s=2\), and simple spectrum, suppose

\[
 p_1(h)+p_2(h)=1+h,\qquad
 p_3(h)+p_4(h)=1-h,
\tag{5}
\]

with no other complementary pair near \(h=0\). At \(h=0\), the pair
\(\{1,2\}\) is reciprocal:

\[
 a_1(0)a_2(0)=t(0)^2.
\tag{6}
\]

The exact support classification gives \(k=2\) at \(h=0\) and \(k=5\) for
small nonzero generic \(h\). This jump alone does not give uniform
asymptotics. It says precisely why the support threshold in the fixed-\(h\)
proof collapses.

It is false in general that the full gauge is one fixed weighted support
sum. Away from the reciprocal locus, distinct exact subset laws can cancel
different matching edges. A single branch therefore misses competing
zero patterns. The relevant unresolved finite problem is a full
branch-by-branch volume comparison for the moment polytope.

The following crossover is a conjectural volume law, not a consequence of
the support classification alone:

\[
 \operatorname{vol}\{\Phi_2-t(h)\leq\varepsilon\}
\asymp
 \varepsilon^{2\beta}\varepsilon^{\beta/2}
 \min\{\sqrt\varepsilon,\varepsilon/|h|\}^{3\beta}.
\tag{8}
\]

The conjecture predicts

\[
 \operatorname{vol}\asymp
 \begin{cases}
 |h|^{-3\beta}\varepsilon^{11\beta/2},
   &0<\varepsilon\lesssim h^2,\\
 \varepsilon^{4\beta},
   &\varepsilon\gtrsim h^2,
 \end{cases}
\tag{9}
\]

and the corresponding deterministic library size is its reciprocal. At
\(h=0\), the \(4\beta\) exponent agrees with the reciprocal-locus value.
For fixed \(h\ne0\), the small-\(\varepsilon\) exponent is the generic
\(11\beta/2\) value.

## 3. Consequences for the procedural grid

For each fixed \(h\ne0\), the regular grid with \(k=5\) is valid as
\(\varepsilon\downarrow0\). At \(h=0\), the \(k=2\) grid is valid. Their
hidden constants are not uniform as \(h\to0\), because the support
comparison threshold collapses.

Any uniform grid must be derived from that full branch analysis. A
three-scale grid associated with one selected support is not presently
valid for the full gauge. The smooth atlas, inverse-function, and
Cayley-decoder constants themselves remain uniform under (1); the
unresolved issue is which branch or union of branches controls the
acceptable volume.

## 4. Rounding and resource boundary

The procedural Cayley grid has a per-atom transform index of
\(\kappa\log_2(1/\varepsilon)+O(1)\) only for fixed spectrum, dimension,
and read cap. A growing source family can change \(\kappa\), the atlas
constant, and the hidden additive term; the theorem gives no uniform
lower bound in that regime.

The procedural decoder note supplies a rational exact-size common law with
\(O_D(\log(1/\varepsilon))\) shared sampler bits, rational HT weights, and
exact unbiasedness toward the represented rational source. The encoded
column rounding bound then separately controls stored \(P\), a computed
query transform \(U\), and arithmetic error through declared norm bounds.
The procedural note also records dense transform workspace and operation
counts under its rational-arithmetic model.

Those accounts remain conditional resource formulas. They do not prove a
physical page conversion, fixed-word runtime, compiler index-selection
cost, or a total-description advantage over alternative descriptions.
