# k4_bounded_bit_full_linear_sampler.md — exact integer K4 maps with bounded fair-bit cost; depends on k4_dyadic_full_linear_page_accounting.md, fixed_projector_sparse_kernel_dichotomy.md, ../../MATHS.md.

# A bounded-bit K4 law

This note replaces rejection sampling in the earlier twenty-map construction.
It uses the same twenty integer prototypes, at most thirty-six scaled maps,
and at most \(\ell+4\) fair bits per six-coordinate block. All statements
concern the declared coefficient and original-column access model.

Let \(P\) be the \(K_4\) cut-space projector, \(N=I-P\), and
\(r=2^{-\ell}\), where \(\ell\ge1\). The preceding note defines sixteen
tree maps \(H_T\) and four raw-cycle maps \(C_f\), each with exactly three
nonzero rows and entries in \(\{0,\pm1\}\). For uniform tree and face indices,

\[
\mathbb E_T H_T=P,\qquad PH_T=P,\qquad H_TN=0,
\]
\[
\mathbb E_T\|NH_Tx\|^2\le3\|Px\|^2,\qquad
\mathbb E_f C_f=N,\qquad PC_f=0,\qquad
\mathbb E_f\|C_fx\|^2=3\|Nx\|^2.
\tag{1}
\]

Choose the following random map. Each row of this table gives its total
branch probability; choose the index uniformly within that branch.

| Map | Branch probability | Number of indices |
|---|---:|---:|
| \(H_T\) | \(1-2r\) | 16 |
| \(2H_T\) | \(r\) | 16 |
| \(r^{-1}C_f\) | \(r\) | 4 |

The first branch has probability zero when \(\ell=1\). Each realized map
has at most three nonzero rows, and every matrix entry is an integer of
absolute value at most \(2^\ell\). The mean is exactly

\[
\mathbb E L=(1-2r)P+2rP+N=I.
\tag{2}
\]

## Risk

Since the high branches have squared scaling average
\((1-2r)+4r=1+2r\), (1) gives

\[
\mathbb E\|PLx\|^2=(1+2r)\|Px\|^2,
\]
\[
\mathbb E\|NLx\|^2
\le3(1+2r)\|Px\|^2+\frac3r\|Nx\|^2.
\tag{3}
\]

Subtract the exact-mean squared norm in the metric \(G_r=P+r^2N\).
For every \(x\),

\[
\begin{aligned}
\mathbb E(Lx-x)^TG_r(Lx-x)
&\le (2r+3r^2+6r^3)\|Px\|^2
 +(3r-r^2)\|Nx\|^2\\
&\le5r\|x\|^2,\qquad 0<r\le\tfrac12.
\end{aligned}
\tag{4}
\]

The last step uses \(2+3r+6r^2\le5\) and \(3-r\le3\).
This is an upper bound; the number 5 is not claimed optimal.

## Exact fair-bit procedure and finite metadata

Draw \(\ell\) fair bits, interpreted as an integer
\(W\in\{0,\ldots,2^\ell-1\}\).

1. If \(W=0\), draw two further bits for a uniform face and return
   \(2^\ell C_f\).
2. If \(W=1\), draw four further bits for a uniform tree and return \(2H_T\).
3. Otherwise, draw four further bits for a uniform tree and return \(H_T\).

This produces the table's probabilities exactly. Its worst-case fair-bit
count is \(\ell+4\); its expectation is \(\ell+4-2r\). No rejection
step occurs. For \(\ell=1\), the third branch is unreachable, as required.

The twenty prototype matrices still admit the earlier 1440-bit literal
serialization. The branch rule is fixed. Store the two variable positive
integers \(\ell+1\) and \(m+1\) with Elias gamma codes when the family has
\(m\) blocks. Their combined length is

\[
2\lfloor\log_2(\ell+1)\rfloor+
2\lfloor\log_2(m+1)\rfloor+2.
\tag{5}
\]

The fixed format tag and interpreter are an additional constant description,
not zero-cost source-dependent state. Scale the prototypes by the three
integers \(1,2,2^\ell\); no joint table with \(36^m\) entries is stored.

This is a finite mathematical arithmetic specification. It is not a
native-machine execution or rounding proof for arbitrary real queries.

## Repeated blocks and the conditional traffic consequence

For the source factor
\(\mathcal R=I_m\otimes(P+rN)\), independent block choices give
\(\mathbb E L=I_{6m}\), at most \(3m\) nonzero output rows, risk at most
\(5r\) on unit queries, and at most \(m(\ell+4)\) fair bits.
Fetching all three selected original-column pages per block, including
any page whose coefficient later cancels, costs exactly \(3mB_{\rm page}\)
fresh bits under the earlier note's declared dense aligned page format.

For a fixed diagonal law with mean identity, let \(\bar s\) be its
expected support count. If its residual Gram is at least
\(a(I_m\otimes G_r)\), its worst-unit-query risk is at least

\[
\frac{a(1+r^2)}2\left(\frac{6m}{\bar s}-1\right).
\tag{6}
\]

Matching the upper bound \(5r\) therefore requires

\[
\bar s\ge\frac{6m}{1+10r/[a(1+r^2)]}.
\tag{7}
\]

For a query with no zero coordinates, the expected diagonal fresh traffic
under that same page format is at least \(\bar s B_{\rm page}\). Relative
to the full law, the lower ratio is

\[
\frac{2}{1+10r/[a(1+r^2)]}\longrightarrow2
\quad(r\downarrow0).
\tag{8}
\]

With the optional finite-interpreter near-isometry from the earlier note,
replace \(5r\) by \(5(1+\zeta)r\), and replace 10 in (7)--(8) by
\(10(1+\zeta)\). Its residual lower factor remains
\(a=1-\zeta-\delta^2\).

The page promise, charged resident state, and restricted diagonal comparator
remain essential assumptions. This note supplies bounded sampling cost for
that comparison; it does not establish a frontier over arbitrary encodings,
decoders, or Cassette plans. Correctness, originality, and sufficient
application significance remain separate questions.
