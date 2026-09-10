# Independent review: rounded native-column finite-advice lower and adaptive upper

Status: the two results match in their declared finite rounded-source,
original-column access model.  The lower is for static support laws selected
by finite source advice; the upper is query-adaptive.  This is a correctness
review only.  It makes no originality or Cassette-significance conclusion.

## Common model and quantifiers

The lower note fixes the protocol architecture first: at most \(N\) source
states, one source-independent support law in each state, and Borel branch
maps that see only the original stored columns \(W_S\).  The source is then
chosen from the finite family

\[
 \mathcal W_h=\{\operatorname{round}_h(A):A^TA=G\}.
\]

This family is finite because the orbit is bounded and the grid is discrete.
The lifted branch

\[
 \widetilde F_{\ell,S}(A_S,x)
 =F_{\ell,S}(\operatorname{round}_h(A_S),x)
\]

really depends only on the observed continuous columns.  Conditional
projection concentration may therefore be applied before the encoder picks
its label.  Zero-probability supports must be discarded first; for each
remaining support, replacing seed randomness by its conditional mean is
valid by Jensen.  The union bound then includes every positive-probability
support, every fixed label, and every net query.  Thus the label selected
from the rounded word cannot evade the good event.

The upper uses the same finite rounded source and reads only columns in the
same original four-coordinate layout.  It is deliberately outside the
static class: its finite catalog law is selected from the query.  This is
the intended static-versus-query-adaptive comparison.  Neither argument
permits a free source-dependent right transform or a coded column that
reveals unselected original columns.

## Sharpened rounding transfer

For a unit query, put

\[
 D_x=\sqrt{C+x^TGx},\qquad
 \zeta=\frac{r_0}{\sqrt{C+\lambda_{\min}(G)}}.
\]

If \(B=\sum_Sw_S\|\widetilde F_S\|^2\), exactness toward \(Wx\), the
risk bound, and \(\|W-A\|_{\rm op}\le r_0\) give

\[
 \sqrt B\le\sqrt{C+(\sqrt{x^TGx}+r_0)^2}
 \le D_x+r_0\le(1+\zeta)D_x.
\]

The last inequality uses \(D_x\ge\sqrt{C+\lambda_{\min}(G)}\), which is
why normalizing before taking a uniform bound retains the \(C\)-dependent
function \(f_G(C)\).  The projection/leakage Cauchy--Schwarz estimate is

\[
 |\langle u,Ax\rangle|
 \le(\sqrt{u^THu}+\epsilon\|u\|)\sqrt B+r_0\|u\|.
\]

For the normalized net queries
\(x_z=(G+CI)^{-1/2}z/\|(G+CI)^{-1/2}z\|\), the exact cancellation

\[
 \frac{Ax_z}{D_{x_z}}=A(G+CI)^{-1/2}z
\]

is unchanged by source rounding.  Net duality therefore yields

\[
 \alpha\sqrt{u^TK_Cu}\le\sqrt{u^THu}+\epsilon'\|u\|,
 \quad
 \alpha=\frac{a}{1+\zeta},\quad
 \epsilon'=\epsilon+\frac{\zeta}{1+\zeta},
\]

and the standard two-case square gives

\[
 H\succeq\alpha^2K_C-2\alpha\epsilon'I.
\]

Taking traces is legitimate because \(G\succ0\) makes every selected set
of columns linearly independent.  This proves

\[
 s_\ell\ge\alpha^2f_G(C)-2\alpha q\epsilon'.
\]

All displayed inequalities also cover \(C=0\), since the denominator in
\(\zeta\) remains positive.

## Equicorrelation arithmetic

Set \(q=4m\), \(C=19\eta/10\), and \(0<\eta\le1/100\).  Per block,

\[
 f_{H_\eta}(C)
 =\frac{4+\eta}{4+(29/10)\eta}+\frac{30}{29}
 \ge\frac{237160}{116841}.
\]

The first summand is decreasing in \(\eta\), so the right side is its
value at \(\eta=1/100\).  With

\[
 \epsilon=\frac1{1000},\quad \delta=\frac1{10000}^{1/2}=\frac1{100},
 \quad a=\frac{19999}{20000},\quad
 r_0\le\frac{\sqrt\eta}{20000},
\]

we have

\[
 \zeta\le\frac{1}{20000\sqrt{29/10}}<\frac1{20000},
 \quad \alpha\ge\alpha_0=\frac{19999}{20001},
 \quad \epsilon'\le\epsilon_0=\frac1{1000}+\frac1{20001}.
\]

Substituting \(\alpha_0\) into both terms needs one monotonicity check.
For fixed \(f\) and \(\epsilon_0\),

\[
 \frac{d}{d\alpha}(\alpha^2f-2\alpha q\epsilon_0)
 =2(\alpha f-q\epsilon_0)>0
\]

throughout \([\alpha_0,a]\): already
\(\alpha_0f>0.99\cdot2\), whereas
\(q\epsilon_0<4(1/1000+1/20000)\).  Hence the conservative lower value
is indeed attained at \(\alpha_0\), not merely by an invalid independent
substitution into a positive and a negative term.  Exact rational
calculation gives

\[
 \alpha_0^2\frac{237160}{116841}-8\alpha_0\epsilon_0
 =\frac{11807741126602841}{5842634219605125}
 =\frac{101}{50}
 +\frac{11240006000977}{11685268439210250}>2.02.
\]

The same tail calculation has the unchanged sufficient dimension condition

\[
 p-4m>4{,}000{,}000
 \bigl(\log N+6m\log2+4m\log201\bigr).
\]

## Adaptive rounded upper

The catalog bridge gives ideal-block risk
\(379\eta/200=1.895\eta\) and coefficient mean \(\mathbb EY=x\), with
support at most two per block.  Block concatenation retains exact mean and
the hard \(2m\)-column cap.  Since \(G\succeq\eta I\), the rounded source
satisfies

\[
 \|Wz\|\le\left(1+\frac{r_0}{\sqrt\eta}\right)\|Az\|.
\]

Thus the rounded risk is at most

\[
 \frac{379}{200}\left(\frac{20001}{20000}\right)^2\eta
 =\frac{151615160379}{80000000000}\eta<1.9\eta.
\]

The claim is compatible with the real lower model.  If a complex catalog
output is \(Y=x+u+iv\) for real \(x\), use \(Y_{\mathbb R}=\Re Y\).
It keeps exact coefficient mean and cannot add support.  For real
\(H_\eta\),

\[
 (Y-x)^*H_\eta(Y-x)=u^TH_\eta u+v^TH_\eta v,
\]

so real-part projection cannot increase risk.  This implication should be
stated explicitly in the upper note; it is sound, but presently implicit.

## Finite-word boundary

For dyadic \(h=2^{-L}\), every rounded entry is exactly \(hn\) with

\[
 |n|\le\left\lceil\frac{\sqrt{4+\eta}}h+\frac12\right\rceil,
\]

so \(\lceil\log_2(2N_h+1)\rceil\) signed bits per entry suffice.  The
stated \(2mpw_h\) payload-bit cap is therefore correct.  It excludes page
headers, alignment, addresses, cache state, catalog storage, catalog
selection, random-bit consumption, and native arithmetic.  The current
word claim also establishes literal exactness only for rational queries
under declared exact rational sampling and arithmetic.  The all-real
mathematical upper follows conditionally from the complex catalog theorem,
but a native all-real execution account is not established here.

The lower is robust to an arbitrarily large shared decoder table because it
permits arbitrary Borel branch maps.  That strength does not price the
upper's catalog.  The notes correctly leave this as an accounting boundary,
not a finite-page theorem.

## Review result

The sharpened lower transfer, exact parameter arithmetic, adaptive
rounding factor, finite source family, and original-column support claims
are correct within the declared model.  Add the real-part lemma explicitly
to make the lower/upper field match visible, and add the monotonicity line
above where the lower substitutes \(\alpha_0\).  These are exposition
repairs, not mathematical defects.
