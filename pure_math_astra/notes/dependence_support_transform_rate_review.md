# Correctness review: dependence support and transform rate

Reviewed file: notes/dependence_support_transform_rate.md.

Verdict: the proposed theorem is correct conditional on the cited
quantitative fixed-basis rigidity inequality. The required attainment result
is proved in the Convex formulation and attainment section of
coded_basis_rigidity.md, equations (9)--(13). The optional
\(\eta\)-optimal-law revision removes that dependency from Section 5, but it
does not repair a gap.

## Verified steps

Sections 3 and 4 are correct. The skew-Hermitian chart has one
\(\mathbb F\)-coordinate for every unordered cross-eigenspace pair, hence
real dimension \(d=\beta N\). Diagonal changes and within-eigenspace
off-diagonals are quadratic, while cross-eigenspace entries are their
corresponding \(B\)-coordinates to first order. The cited rigidity bound
then gives \(\Phi_s(G(B))-t\geq c\lVert B\rVert^2\). For a fixed
exact-\(s\) law with ideal marginals, HT covariance equals \(tI\) at \(D\)
and has first-order cross part \(B\circ c\), which proves the local upper
comparison.

Section 5's reduction works for complex, subset-dependent weights. Let
\(Q=\mathbb E[D_b^*GD_b]-G\), \(I_i=\mathbf1_{\{b_i\ne0\}}\), and
\(\theta_i=\mathbb EI_i\). The diagonal bound
\(Q_{ii}\leq t+\delta\) and Cauchy give

\[
 \mathbb E|b_i|^2\geq1/\theta_i,\qquad
 \theta_i\geq d_i/(d_i+t+\delta).
\]

Schur--Horn plus concavity of \(x/(x+t)\) gives
\(\sum_i d_i/(d_i+t)\geq s\). Since supports have size at most \(s\),
this yields \(\theta_i=p_i+O(\delta+\lVert B\rVert^2)\) and expected
missing support size \(O(\delta)\). The Cauchy defect identity

\[
 \mathbb E\left|b_i-I_i/\theta_i\right|^2
 =\mathbb E|b_i|^2-1/\theta_i
\]

is then \(O(\delta)\). It is the needed bridge from arbitrary complex
weights to indicator pair moments.

Padding underfull outcomes changes the indicator law by \(O(\delta)\) in
total variation. If its new marginals are \(p+e\), the proposed correction

\[
 z=p-\rho e/\lVert e\rVert_\infty,\qquad
 \rho=\tfrac12\min_i\{p_i,1-p_i\},
\]

lies in the hypersimplex. Mixing its exact-\(s\) realization at weight
\(\lVert e\rVert_\infty/(\rho+\lVert e\rVert_\infty)\) gives exactly \(p\)
and changes total variation by \(O(\delta+\lVert B\rVert^2)\). This
calculation is correct. Together with the Cauchy defect, it proves the
pair-moment estimate in (12).

For the PSD slack \(M=(t+\delta)I-Q\), the same diagonal inequalities give
\(M_{ii}=O(\delta)\). Positivity yields
\(|Q_{ij}|=|M_{ij}|=O(\delta)\) off the diagonal. Combining this with the
first-order chart and pair-moment estimate gives (13); rigidity absorbs
\(\lVert B\rVert^2\). Thus the lower half of the local normal form follows.

Section 6 is valid for every compact coefficient set. The useful finite
argument is: for each coordinate set \(Z\) that is not a zero set of any
coefficient vector, compactness makes
\(\min_{c\in\mathcal C}\max_{i\in Z}|c_i|>0\). Taking the minimum across
the finitely many \(Z\)'s gives a uniform threshold. The stated comparison
with the finite set of support patterns follows.

Section 7 then has the claimed exponent. For a support of size \(j\), its
\(\beta j\) real coordinates have radius \(O(\varepsilon)\), and the
remaining \(d-\beta j\) coordinates have radius
\(O(\sqrt\varepsilon)\). The smallest support size \(k\) dominates the
finite union, giving \(\kappa=(d+\beta k)/2\). The diagonal points are
finite, and uniform rigidity excludes all other points from sufficiently
small sublevels.

Section 8 is valid with one common sampler. Choose one law attaining the
minimum support size \(k\), use its HT weights for every codeword, and
retain only its local acceptable set. Its measure is
\(\Omega(\varepsilon^\kappa)\). For this fixed law,

\[
 \left\|\mathbb E[D_b^*(G'-G)D_b]-(G'-G)\right\|_{\rm op}
 \leq(1+\mathbb E\|D_b\|_{\rm op}^2)\lVert G'-G\rVert_{\rm op}.
\]

The constant is finite because the HT weights are the fixed numbers
\(1/p_i\). An \(O(\varepsilon)\)-net and Haar-random transforms therefore
give the claimed \(O(\varepsilon^{-\kappa}\log(1/\varepsilon))\) library.
No source-dependent sampler must be encoded. The lower bound uses
\(\Phi_s\), so it remains valid even if a competing scheme chooses a
different law after selecting its transform.

Section 9's criterion is correct. Cross-block pairwise independence makes
the block counts pairwise uncorrelated. Their deterministic sum then
forces every block count to be constant, so every \(m_gp_g\) is integral.
Independent uniform fixed-count sampling within the blocks proves the
converse.

## Attainment provenance correction

My initial review incorrectly treated the SDP-attainment sentence in
Section 5 as unsupported. The referenced Convex formulation and attainment
section proves it for arbitrary complex, support-dependent weights:
conditional expectation reduces each realized support to one deterministic
weight vector in PSD order; the variables \(p_S,v_S=p_Sb_S\) give the
finite Hermitian block LMI in equation (11); and equation (13), together
with full column rank of \(R\), bounds every \(v_S\) on a finite sublevel.
The closed feasible set then contains a minimizer. The Section 5 use of an
optimal law is therefore justified.

Using an \(\eta\)-optimal law and taking \(\eta\downarrow0\) remains a
valid self-contained alternative.

## Direct file-format check

git diff --check does not inspect untracked files. Directly checking the
reviewed untracked theorem file with git diff --no-index --check reported:

    pure_math_astra/notes/dependence_support_transform_rate.md:377:
    new blank line at EOF.

This is a Markdown-format warning, not a mathematical finding. I did not
edit the reviewed file.
