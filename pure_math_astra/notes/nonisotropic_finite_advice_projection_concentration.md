# Conditional Haar-subspace concentration for finite nonisotropic advice

Status: proved concentration lemma and finite-union consequence. The lemma
supplies an approximate supported-coefficient certificate at finitely many
queries. It does not itself prove a spectral-water lower bound, a
finite-word theorem, or a Cassette resource certificate.

## Setting

Fix \(G\succ0\), \(p>q\), and a factor \(R\) with \(R^TR=G\). Draw
\(U\) uniformly from \(\mathcal V_{p,q}\) and put \(A=UR\). For a support
\(S\subseteq[q]\), let

\[
 r=|S|,\qquad L_S=\operatorname{ran}(RE_S)\subseteq\mathbb R^q.
\]

Positive definiteness of \(G\) makes \(RE_S\) injective, so
\(\dim L_S=r\). The observed columns are \(A_S=U(RE_S)\), and their
span is \(UL_S\). Define the unobserved part of the source span by

\[
 \mathcal E_S(A)=\operatorname{span}(A)\cap
                 \operatorname{span}(A_S)^\perp
               =U L_S^\perp.
 \tag{1}
\]

It has dimension \(d=q-r\) inside the ambient conditional space
\(\operatorname{span}(A_S)^\perp\), whose dimension is \(n=p-r\).

## Conditional projection tail

**Lemma 1.** Conditional on \(A_S\), \(\mathcal E_S(A)\) is a Haar
\(d\)-plane in \(\operatorname{span}(A_S)^\perp\). Consequently, for
any Borel function \(F(A_S,x)\), any fixed query \(x\), and every
\(\varepsilon>0\),

\[
 \Pr\left\{
 \|P_{\mathcal E_S(A)}P_{\operatorname{span}(A_S)^\perp}F(A_S,x)\|
 >\varepsilon\|P_{\operatorname{span}(A_S)^\perp}F(A_S,x)\|
 \ \middle|\ A_S\right\}
 \le 2^{d/2}e^{-n\varepsilon^2/4}.
 \tag{2}
\]

The right side is valid, though possibly larger than one. If the
perpendicular component of \(F\) vanishes, the event is empty.

**Proof.** Observing \(A_S=U(RE_S)\) determines the isometry \(U\) on
\(L_S\). Haar disintegration leaves its restriction to \(L_S^\perp\) as
a uniform isometry into \(\operatorname{span}(A_S)^\perp\). Its range is
therefore the stated Haar \(d\)-plane. This argument is unchanged if a
label reads columns of \(AQ\): replace \(R\) by \(RQ\).

After conditioning on \(A_S\), normalize the nonzero perpendicular
component of \(F\) to a fixed unit vector \(v\). If \(L\) is a Haar
\(d\)-plane in \(\mathbb R^n\), then

\[
 X=\|P_Lv\|^2\sim\operatorname{Beta}\left(\frac d2,
                                      \frac{n-d}{2}\right),
 \qquad
 \mathbb EX^k=\frac{(d/2)_k}{(n/2)_k}.
 \tag{3}
\]

For \(0<\lambda<1\), termwise comparison of the exponential series gives

\[
 \begin{aligned}
 \mathbb E e^{\lambda nX/2}
 &=\sum_{k\ge0}\frac{(\lambda n/2)^k}{k!}
     \frac{(d/2)_k}{(n/2)_k}\\
 &\le\sum_{k\ge0}\frac{\lambda^k(d/2)_k}{k!}
 =(1-\lambda)^{-d/2}.
 \end{aligned}
 \tag{4}
\]

Here \((n/2)^k\le(n/2)_k\). Markov's inequality at \(\lambda=1/2\)
gives (2). The cases \(d=0\) and \(d=n\) also satisfy the displayed
bound directly. \(\square\)

No norm bound on \(F\) is used. The normalized direction is measurable
where the perpendicular component is nonzero because

\[
 P_{\operatorname{span}(A_S)}
 =A_SG_{SS}^{-1}A_S^T
\tag{5}
\]

is Borel in \(A_S\). Thus unbounded Borel branch functions create no
conditional-projection pathology.

## Finite simultaneous union

Let there be at most \(N\) fixed decoder states, and let
\(\mathcal X\) be a finite set of fixed unit queries. Apply Lemma 1 to
every label, every support, and every query. No independence between
these events is needed. If all subsets are allowed, the union bound gives

\[
 \Pr\{\text{some listed projection bound fails}\}
 \le N\,2^{3q/2}|\mathcal X|
 \exp\left(-\frac{(p-q)\varepsilon^2}{4}\right).
 \tag{6}
\]

Indeed, there are at most \(2^q\) supports,
\(2^{(q-|S|)/2}\le2^{q/2}\), and \(p-|S|\ge p-q\). The sharper sum
before these worst-case replacements is

\[
 |\mathcal X|\sum_{\ell,S}
 2^{(q-|S|)/2}e^{-(p-|S|)\varepsilon^2/4}.
 \tag{7}
\]

For a \(\delta\)-net of the unit sphere in \(\mathbb R^q\), take
\(|\mathcal X|\le(1+2/\delta)^q\). In particular, a source satisfying
all listed inequalities exists whenever the right side of (6) is less
than one; a sufficient condition is

\[
 p-q>
 \frac4{\varepsilon^2}
 \left(\log N+\frac{3q}{2}\log2+
 q\log(1+2/\delta)\right).
 \tag{8}
\]

A source-selected label cannot evade this choice: the good event includes
every fixed label's branch maps, so it includes the label selected at the
chosen source.

## Finite-query supported-coefficient certificate

Suppose the selected label has fixed support probabilities \(w_S\), exact
mean recovery, and risk at most \(C\) at every query in a finite set. Take
\(\mathcal X=\{e_1,\ldots,e_q\}\), and choose a source satisfying Lemma 1
for all of these coordinate queries and every positive-probability support
of its selected label. Write

\[
 F_{S,j}=F_S(A_S,e_j),
 \qquad
 c_{S,j}=G_{SS}^{-1}A_S^TF_{S,j},
 \qquad C_S=[c_{S,1}\ \cdots\ c_{S,q}].
 \tag{9}
\]

Projecting the exact mean equations onto \(\operatorname{span}(A)\), and
using the orthogonal decomposition

\[
 P_{\operatorname{span}(A)}F_{S,j}
 =A_Sc_{S,j}+P_{\mathcal E_S(A)}
  P_{\operatorname{span}(A_S)^\perp}F_{S,j},
 \tag{10}
\]

gives

\[
 \left\|A-\sum_Sw_SA_SC_S\right\|_F
 \le\varepsilon\left(\sum_Sw_S\|[F_{S,1}\ \cdots\ F_{S,q}]\|_F^2
                  \right)^{1/2}.
 \tag{11}
\]

Exactness and the risk bound imply, separately for every coordinate,

\[
 \sum_Sw_S\|F_{S,j}\|^2
 =\|Ae_j\|^2+
   \sum_Sw_S\|F_{S,j}-Ae_j\|^2
 \le G_{jj}+C.
 \tag{12}
\]

Therefore (11) becomes the finite supported-coefficient certificate

\[
 \left\|G^{1/2}
 \left(I-\sum_Sw_SE_SC_S\right)\right\|_F
 \le\varepsilon\sqrt{\operatorname{tr}G+qC}.
 \tag{13}
\]

It holds for the state selected at the chosen source. The statement is
approximate and finite-query: it does not turn arbitrary Borel dependence
on \(x\) into a uniform-in-query assertion.

## Limitation of a query net

The union bound applies to any finite prescribed collection of queries.
For arbitrary Borel branch maps, values at nearby queries need not be
nearby. Thus a \(\delta\)-net alone does not control the decoder on the
entire unit sphere. A later trace or stability argument may use a finite
net only if it needs exactness and risk at those net points alone. Any
argument that extends the projection bound from the net to all queries
requires an additional regularity or structural premise.
