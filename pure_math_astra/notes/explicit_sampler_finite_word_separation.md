# Finite-word separation corollary from the explicit four-coordinate sampler

Status: proved within the finite rounded-source, original-column model.  The
result is a mathematical read-count separation with an exact finite-word
source account.  It does not construct a physical Cassette page layout or a
native execution path.

## Parameters and adaptive upper

Set

\[
 \eta=\frac1{256},\qquad q=4m,\qquad
 G=H_\eta^{\oplus m},\qquad
 H_\eta=\mathbf1\mathbf1^T+\eta I_4,
 \tag{1}
\]

and set the target risk to

\[
 C=\frac{27}{16}\eta.
 \tag{2}
\]

Let \(A^TA=G\), round entrywise to a dyadic source
\(W=\operatorname{round}_h(A)\), and require

\[
 r_0:=\frac h2\sqrt{pq}\le\frac{\sqrt\eta}{1000}.
 \tag{3}
\]

Apply the explicit sum-preserving sampler in
`explicit_sum_preserving_two_sparse_sampler.md` independently to each
four-coordinate query block.  It is real, exactly coefficient-unbiased,
uses at most two original columns per block in every outcome, and keeps the
blockwise coordinate sum exact.  Its rounded-source risk is at most

\[
 \frac53(\sqrt\eta+r_0)^2\|x\|_2^2
 \le\frac53\left(\frac{1001}{1000}\right)^2\eta\|x\|_2^2
 =\frac{1002001}{600000}\eta\|x\|_2^2
 <\frac{27}{16}\eta\|x\|_2^2.
 \tag{4}
\]

The strict final gap is exact:

\[
 \frac{27}{16}-\frac{1002001}{600000}
 =\frac{10499}{600000}>0.
 \tag{5}
\]

Thus the rounded-source upper has risk below \(C\) and hard original-column
cap \(2m\), with no finite catalog table.  It uses the fixed two-law
selector and the exact rational samplers described in the cited note.

## Static finite-advice lower

Use the rounded original-column trace lower with

\[
 \epsilon=\frac1{250},\qquad
 \delta=\frac1{20},\qquad
 a=1-\frac{\delta^2}{2}=\frac{799}{800}.
 \tag{6}
\]

Because \(\lambda_{\min}(G)=\eta\), (2) and (3) give

\[
 \zeta=
 \frac{r_0}{\sqrt{C+\eta}}
 \le\frac{4}{1000\sqrt{43}}<\zeta_0:=\frac1{1000}.
 \tag{7}
\]

The conservative substitution before the trace square is

\[
 \alpha_0=\frac{a}{1+\zeta_0}=\frac{3995}{4004},
 \qquad
 \epsilon_0=\epsilon+\frac{\zeta_0}{1+\zeta_0}
 =\frac{1251}{250250}.
 \tag{8}
\]

The trace factor per four-coordinate block is

\[
 \begin{aligned}
 f_{H_\eta}(C)
 &=\frac{4+\eta}{4+(43/16)\eta}+\frac{3\eta}{(43/16)\eta}\\
 &=\frac{16400}{16427}+\frac{48}{43}
 =\frac{1493696}{706361}.
 \end{aligned}
 \tag{9}
\]

Therefore the static expected original-column count on the selected hard
rounded source is at least

\[
 \begin{aligned}
 s_{\ell(W)}
 &\ge m\left(\alpha_0^2f_{H_\eta}(C)-8\alpha_0\epsilon_0\right)\\
 &=m\frac{2811004608947}{1361104669925}\\
 &=m\left(\frac{103}{50}
   +\frac{14257977803}{2722209339850}\right)
 >2.06m.
 \end{aligned}
 \tag{10}
\]

The lower applies to every fixed static protocol with at most \(N\)
source-selected states provided

\[
 p-4m>250000\bigl(\ln N+6m\ln2+4m\ln41\bigr).
 \tag{11}
\]

It then supplies a rounded source \(W\), chosen after that static
architecture is fixed, where risk at most \(C\) requires more than \(2.06m\)
expected original-column reads.  This is a \(0.06m\) count margin over the
adaptive hard cap.  It remains a static-versus-query-adaptive statement.

## Exact finite-word source account

Condition (3) holds when the dyadic grid satisfies

\[
 h=2^{-L},\qquad 2^L\ge16000\sqrt{mp}.
 \tag{12}
\]

Every stored entry is then \(hn\), with

\[
 |n|\le N_h=
 \left\lceil2^{L-4}\sqrt{1025}+\frac12\right\rceil,
 \qquad
 w_h=\left\lceil\log_2(2N_h+1)\right\rceil
 \tag{13}
\]

signed payload bits per real scalar.  The stored source has \(4mp\)
scalars, hence exactly \(4mpw_h\) payload bits.  The adaptive hard cap fetches
at most \(2mpw_h\) payload bits per query before headers, alignment,
addressing, and cache effects.

For \(m=1\), the following conservative illustrations use
\(\ln2<0.694\) and \(\ln41<3.714\), rather than treating numerical log
output as an exact threshold proof.  These are strict elementary bounds:
the positive-term Taylor sums give \(e^{0.694}>2\) already through degree
four, and \(e^{3.714}>41\) through degree twelve.

| States \(N\) | Safe \(p\) from (11) | Dyadic \(h\) | \(w_h\) | Source payload | Adaptive fresh payload cap |
| --- | ---: | ---: | ---: | ---: | ---: |
| \(1\) | \(4{,}755{,}005\) | \(2^{-26}\) | \(29\) bits | \(551{,}580{,}580\) bits | \(275{,}790{,}290\) bits/query |
| \(2^{256}\) | \(49{,}171{,}005\) | \(2^{-27}\) | \(30\) bits | \(5{,}900{,}520{,}600\) bits | \(2{,}950{,}260{,}300\) bits/query |

For the first row,

\[
 250000(6\ln2+4\ln41)<4{,}755{,}000<p-4.
 \tag{14}
\]

For the second,

\[
 \begin{aligned}
 250000(256\ln2+6\ln2+4\ln41)
 &<250000(196.684)\\
 &=49{,}171{,}000<p-4.
 \end{aligned}
 \tag{15}
\]

The grid choices are checked without a square-root approximation by
squaring (12): \(2^{2L}\ge256000000p\).  The relevant comparisons are

\[
 \begin{array}{c|c|c}
 p&256000000p&2^{2L}\\ \hline
 4{,}755{,}005&1{,}217{,}281{,}280{,}000{,}000&2^{52}=4{,}503{,}599{,}627{,}370{,}496\\
 49{,}171{,}005&12{,}587{,}777{,}280{,}000{,}000&2^{54}=18{,}014{,}398{,}509{,}481{,}984.
 \end{array}
 \tag{16}
\]

For \(L=26\), (13) gives
\(N_h=134{,}283{,}249\) and \(w_h=29\); for \(L=27\), it gives
\(N_h=268{,}566{,}497\) and \(w_h=30\).  These source payloads are
mathematical packed-bit counts.  They are not device sizes, page counts, or
an asserted workload.

## Boundary

The explicit sampler removes the earlier existential finite catalog and its
catalog-index cost.  It still needs a declared rational query format, exact
integer sampler implementation, physical page conversion, resident state
account, output workspace account, and native Cassette execution before it
can support a full resource certificate.
