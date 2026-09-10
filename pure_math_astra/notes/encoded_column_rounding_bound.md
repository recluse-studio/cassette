# Error terms for stored encoded columns and a computed query transform

Status: supporting perturbation bound for the encoded-column model.
This is a mathematical bound, not evidence about a native runtime.

Let \(R\in\mathbb F^{m\times q}\) be the target residual, and let \(V\) be
an exact unitary or orthogonal transform from a declared library. Let \(b\)
be the common exact-size HT coefficient vector, with marginals
\(\theta_i>0\), and define
\[
 H=\max_i\theta_i^{-1},\qquad
 Z_0=RV D_bV^*.
\]
Suppose
\[
 \mathbb EZ_0=R,\qquad
 \sup_{\|x\|=1}\mathbb E\|(Z_0-R)x\|^2\le v_0.
 \tag{1}
\]
The library theorem can provide \(v_0=t+\varepsilon_0\) in its stated
source class.

Let \(U\) be the stored or decoded query transform and \(P\) the stored
encoded-column matrix. Declare actual operator-norm bounds
\[
 \|U-V\|\le\eta_U,\qquad
 \|P-RV\|\le\eta_P.
 \tag{2}
\]
The exact-arithmetic estimator using those stored objects is
\[
 Z=PD_bU^*,\qquad \mathbb EZ=M:=PU^*.
\]
Put
\[
 \eta_M=\eta_P(1+\eta_U)+\|R\|\eta_U,\qquad
 \eta_Z=H\eta_M.
 \tag{3}
\]
Then, for every query \(x\),
\[
 \|M-R\|\le\eta_M,
 \tag{4}
\]
\[
 \mathbb E\|(Z-M)x\|^2
 \le(\sqrt{v_0}+\eta_Z)^2\|x\|^2,
 \tag{5}
\]
and
\[
 \mathbb E\|(Z-R)x\|^2
 \le\bigl[(\sqrt{v_0}+\eta_Z)^2+\eta_M^2\bigr]\|x\|^2.
 \tag{6}
\]

To prove these claims, use \(\|U\|\le1+\eta_U\) and
\[
 M-R=(P-RV)U^*+RV(U^*-V^*).
\]
This gives (4). For every sample outcome,
\[
 Z-Z_0=(P-RV)D_bU^*+RV D_b(U^*-V^*),
\]
so \(\|Z-Z_0\|\le\eta_Z\), because \(\|D_b\|\le H\). Write
\(\Delta Z=Z-Z_0\). Centering can only reduce its mean square:
\[
 \mathbb E\|(\Delta Z-\mathbb E\Delta Z)x\|^2
 \le\mathbb E\|\Delta Zx\|^2
 \le\eta_Z^2\|x\|^2.
\]
The triangle inequality in the space of square-integrable random vectors,
together with (1), proves (5). The random vector \((Z-M)x\) has mean zero;
its cross term with \((M-R)x\) vanishes. This proves (6).

If the arithmetic implementation returns
\[
 Y_{\rm arith}(x)=Zx+e_b(x),\qquad
 \|e_b(x)\|\le\eta_{\rm arith}\|x\|
 \quad\text{for every legal sample outcome},
 \tag{7}
\]
then another square-integrable triangle inequality gives
\[
 \mathbb E\|Y_{\rm arith}(x)-Rx\|^2
 \le
 \left(
 \sqrt{(\sqrt{v_0}+\eta_Z)^2+\eta_M^2}
 +\eta_{\rm arith}
 \right)^2\|x\|^2.
 \tag{8}
\]
No centering or independence of the arithmetic error is assumed. A runtime
must establish (7) for its actual numerical operations before using (8).

A deterministic resident head can be included by adding its declared
operator error to \(\eta_{\rm arith}\) or by stating its bias separately.
Its approximation does not become part of the fresh-sampling variance.

## Probability and horizon fields

For a fixed nonzero query, if the coefficient on the right side of (8)
is \(v_{\rm total}\), Markov's inequality gives
\[
 \Pr\{\|Y_{\rm arith}(x)-Rx\|>\rho\|x\|\}
 \le v_{\rm total}/\rho^2.
\]
This is a sufficient probability bound. It is not an assertion that the
bound is sharp.

For a sequence of calls, the same conditional one-step inequality can be
used if the actual query and state are measurable before fresh sampling
and all stated bounds hold conditionally on that history. A union bound can
then allocate failure probabilities over a declared finite horizon.
Accumulated output error through later operators still needs the
sequential-composition hypotheses in MATHS.md. One-step bounds do not
establish those hypotheses.

## Storage and numerical interpretation

Equations (2) and (7) are obligations with numerical values, not labels.
Componentwise fixed-grid quantization can supply conservative values in
(2): if every real coordinate of an \(m\)-by-\(q\) matrix is rounded with
absolute error at most \(h/2\), its operator error is at most
\(\sqrt{\beta mq}\,h/2\), where \(\beta=1\) or \(2\) according to the field.
A sharper value may come from an actual operator-norm calculation.

The bound (8) keeps three effects separate: ideal sampling risk \(v_0\),
the bias introduced by stored columns and the query transform, and
arithmetic error. Exact unbiasedness toward \(R\) is retained only when
the mean operator \(M\) equals \(R\) and the numerical execution has the
required mean. A finite-word implementation can instead use the explicit
bias-inclusive bound above.

For a fixed precision, arithmetic and storage errors can impose a positive
floor on the achievable excess. The asymptotic transform-index exponent
therefore does not by itself prove a fixed-precision asymptotic statement.
The theorem must report its admissible error range, working storage,
encoded bytes per selected column, and arithmetic operation model.

This fills a conditional mathematical error account for the laboratory
model. It does not write or qualify a Cassette production certificate.
