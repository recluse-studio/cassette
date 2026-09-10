# Finite rounded-orbit spectral trace lower bound with original-column reads

Status: proved rounding transfer in the declared finite-source,
original-column model. It does not prove that a separate adaptive upper law
survives source rounding, nor does it price a physical storage format beyond
entrywise finite words.

## Model and finite source family

Fix \(G\succ0\), \(p>q\ge2\), a grid spacing \(h>0\), and a deterministic
entrywise nearest-grid map \(\operatorname{round}_h\). At a midpoint, fix
one tie convention once and for all. For

\[
 \mathcal O_G=\{A\in\mathbb R^{p\times q}:A^TA=G\},
 \qquad W=\operatorname{round}_h(A),
\]

write

\[
 r_0=\frac h2\sqrt{pq}.
 \tag{1}
\]

Then

\[
 \|W-A\|_{\rm op}\le\|W-A\|_F\le r_0.
 \tag{2}
\]

The orbit is bounded, so the rounded family
\(\mathcal W_h=\{\operatorname{round}_h(A):A\in\mathcal O_G\}\) is
finite. Rounding is coordinatewise, including at ties, hence

\[
 \operatorname{round}_h(A)_S
 =\operatorname{round}_h(A_S)=W_S.
 \tag{3}
\]

A finite-state protocol receives a source \(W\in\mathcal W_h\), selects
one of at most \(N\) states from that \(W\), and in state \(\ell\) samples
an original-column support \(S\) from a fixed law \(w_{\ell,S}\). A branch
reads only \(W_S\), not a transformed or encoded replacement column. Its
Borel output is exactly unbiased for \(Wx\) and has squared risk at most
\(C\), for every \(W\in\mathcal W_h\) and every unit query \(x\).
Internal randomness is a source-independent Borel conditional law.

Zero-probability supports are discarded before taking conditional branch
means. For every remaining support, conditional expectation over the
internal seed gives a Borel deterministic branch map without increasing
risk. Its lift to the continuous orbit is

\[
 \widetilde F_{\ell,S}(A_S,x)
 =F_{\ell,S}(\operatorname{round}_h(A_S),x).
 \tag{4}
\]

This is Borel and depends only on \(A_S\). It needs no continuity. The
rounded source family is finite. If a branch was specified only on rounded
inputs arising in its own state cell, extend it by zero on the remaining
grid inputs before (4); this is a Borel extension and changes no legal
execution. The mean and risk identities for this lift hold at a source
\(A\) precisely in the state selected by \(W=\operatorname{round}_h(A)\):

\[
 \sum_Sw_S\widetilde F_S(A_S,x)=Wx,
 \qquad
 \sum_Sw_S\|\widetilde F_S(A_S,x)-Wx\|^2\le C.
 \tag{5}
\]

## Simultaneous conditional projection control

Let \(0<\epsilon<1\), \(0<\delta<1\), and let \(\mathcal Z\) be a
Euclidean \(\delta\)-net of the unit sphere in \(\mathbb R^q\), with
\(|\mathcal Z|\le(1+2/\delta)^q\). Use the unit queries

\[
 x_z=\frac{(G+CI)^{-1/2}z}
            {\|(G+CI)^{-1/2}z\|}.
 \tag{6}
\]

For fixed \((\ell,S,z)\), the lifted branch map in (4) is a Borel
function of its observed continuous columns. Conditional Haar-subspace
concentration therefore gives

\[
 \Pr\{\|P_{E_{\ell,S}}\widetilde F_{\ell,S}\|
       >\epsilon\|\widetilde F_{\ell,S}\|\}
 \le2^{(q-|S|)/2}e^{-(p-|S|)\epsilon^2/4},
 \tag{7}
\]

where
\(E_{\ell,S}=\operatorname{span}(A)\cap
\operatorname{span}(A_S)^\perp\). The event is formed over the full
continuous orbit, before the source label is selected. A union over all
fixed states, their positive-probability supports, and the finite query
set gives a good event \(\Omega\) with complement measure at most

\[
 \beta=N2^{3q/2}(1+2/\delta)^q
       e^{-(p-q)\epsilon^2/4}.
 \tag{8}
\]

The encoder may choose a state from the rounded source \(W\), but every
\(A\in\Omega\) is good for every fixed state, hence for its selected
state. The only source selected after this union is the finite word source
\(W=\operatorname{round}_h(A)\).

## Robust deterministic trace step

Fix \(A\in\Omega\), set \(W=\operatorname{round}_h(A)\), and work in its
selected state. Put \(V=\operatorname{span}(A)\),

\[
 H=\sum_Sw_SP_{\operatorname{span}(A_S)}\big|_V,
 \qquad
 K_C=A(G+CI)^{-1}A^T\big|_V.
 \tag{9}
\]

For a tested unit query, exactness in (5) gives the variance identity

\[
 B:=\sum_Sw_S\|\widetilde F_S\|^2
 =\sum_Sw_S\|\widetilde F_S-Wx\|^2+\|Wx\|^2
 \le C+\|Wx\|^2.
 \tag{10}
\]

Let

\[
 D_x=\sqrt{C+x^TGx},
 \qquad
 \zeta=\frac{r_0}{\sqrt{C+\lambda_{\min}(G)}}.
 \tag{11}
\]

By (2),

\[
 \sqrt B
 \le\sqrt{C+(\sqrt{x^TGx}+r_0)^2}
 \le D_x+r_0
 \le(1+\zeta)D_x.
 \tag{12}
\]

For \(u\in V\), exactness for \(Wx\), the leakage bound on \(\Omega\),
and Cauchy--Schwarz over the support law give

\[
 \begin{aligned}
 |\langle u,Ax\rangle|
 &\le |\langle u,Wx\rangle|+r_0\|u\|\\
 &\le\bigl(\sqrt{u^THu}+\epsilon\|u\|\bigr)\sqrt B+r_0\|u\|.
 \end{aligned}
 \tag{13}
\]

Dividing by \(D_x\) and using (12) yields

\[
 \frac{|\langle u,Ax\rangle|}{D_x}
 \le(1+\zeta)\sqrt{u^THu}
   +\bigl[\epsilon(1+\zeta)+\zeta\bigr]\|u\|.
 \tag{14}
\]

For the finite queries (6), the exact algebraic identity

\[
 \frac{Ax_z}{D_{x_z}}=A(G+CI)^{-1/2}z
 \tag{15}
\]

still concerns \(A\), not \(W\). A net point approximates the linear
dual direction exactly as in the unrounded trace argument; no decoder
value is compared at two nearby queries. With

\[
 a=1-\delta^2/2,
 \qquad
 \alpha=\frac{a}{1+\zeta},
 \qquad
 \epsilon'=\epsilon+\frac{\zeta}{1+\zeta},
 \tag{16}
\]

one obtains, for all \(u\in V\),

\[
 \alpha\sqrt{u^TK_Cu}
 \le\sqrt{u^THu}+\epsilon'\|u\|.
 \tag{17}
\]

Because \(0\preceq K_C\preceq I_V\), the same two-case squaring argument
as in the exact-source trace lemma gives

\[
 H\succeq\alpha^2K_C-2\alpha\epsilon'I_V.
 \tag{18}
\]

Since the columns of \(A\) are independent,
\(\operatorname{tr}H=\sum_Sw_S|S|\). Hence every \(A\in\Omega\) obeys

\[
s_{\ell(W)}
 \ge\alpha^2 f_G(C)-2\alpha q\epsilon'.
 \tag{19}
\]

Thus, writing the right side as \(L_h\),

\[
 \mu\{A:s_{\ell(\operatorname{round}_h(A))}<L_h\}
 \le\min\{1,\beta\}.
 \tag{20}
\]

If every selected state has expected read count at most \(s\) and
\(\beta<1\), some \(A\in\Omega\) exists, so

\[
 s\ge L_h.
 \tag{21}
\]

This picks a rounded source \(W\in\mathcal W_h\) after the finite
protocol architecture is fixed. It does not give a common hard \(W\) for
all architectures, and (20) is a measure statement about continuous
preimages of rounded words, not a counting statement about the finite
family.

## Endpoints and scope

The proof permits \(C=0\): \(G+CI\) and the denominator in \(\zeta\) stay
positive definite because \(G\succ0\). If \(L_h\le0\), the bound is
vacuous but remains correct. The rounding convention at signs and half-grid
ties affects neither (2) nor the commutation identity (3), provided it is
fixed independently of the source.

This is an original-column result. It excludes a free dense transform, a
coded page that reveals columns outside \(S\), or source-dependent branch
state beyond the finite selected label. Those changes alter the observed
information and can encode a finite corpus rather than merely round its
original entries.
