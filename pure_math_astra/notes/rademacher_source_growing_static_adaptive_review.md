# Root reconstruction of the independent-sign source extension

Reviewed rademacher_source_growing_static_adaptive_extension.md. The
probability, residual, and read-count argument is supported in its stated
column-linear class. The extension uses a standard subgaussian embedding
argument; its improved dimension estimate is not an originality claim.

For fixed real unit vectors v,w, the independent-sign bilinear sum has
squared coefficient sum 1/p. Its two-sided tail is therefore
2 exp(-p h^2/2). Two quarter-nets recover the operator norm with factor
two, yielding exponent p delta^2/8 in the codebook union bound. Complex
queries cause no extra factor: each decoded Bx lies in the complexification
of the real span of B's real and imaginary columns, and a real matrix has
the same operator norm on that complexification.

The near-isometry proof has the claimed linear dimension cost. Integrating
the scalar tail gives E|X|^{2j}<=2^{j+1} j!. With Y=X^2-1, EY=0 and
E|Y|^j<=2^{2j+1}j! for j>=2. This is bounded by
(j!/2)64 8^{j-2}; the comparison is equality in its powers of two at j=2
and weakens for larger j. Bernstein's denominator
2(64+8h) is at most 144 for 0<h<=1. Applying that bound at h=zeta/2
to one quadratic-form quarter-net gives exactly
2 exp(t log9-p zeta^2/576). No entrywise bound with a hidden factor t
is being substituted.

The union of the two failure events has probability below one under the
displayed condition. A common realization therefore exists with both
properties. Choosing p as a power of four keeps 1/sqrt(p) dyadic and
increases the least sufficient dimension by less than a factor of four.
For the fixed delta and zeta, p=O(m+b).

The upper risk transfer uses the Loewner comparison to the reference
block Gram. It does not falsely assume that the actual source Gram is
block diagonal. The residual completion of the square uses
|<UR0x,Bx>|<=delta||R0x||||Bx|| and ||UR0x||^2>=(1-zeta)||R0x||^2.
It therefore gives a=1-zeta-delta^2=127/128, while the upper coefficient
is c=(19/10)(1+zeta)=4883/2560. The resulting two scalar contributions
in the trace lower bound are 1-4883/1016000 and 1+197/7423.
Their excess over two is
163905491/7541768000>1/50, as stated.

The extension consequently preserves the growing support gap with
p=O_eta(m) and b=O_eta(log(m+2)), provided the finite shared catalog
and regular addressing records fit the common budget. The unspecified
catalog constant remains unspecified. The comparison remains source
specific, selected after the finite interpreter range, and restricted to
the declared resident-matrix and column-linear classes. Independent
factor signs remove the former global shared-row-sign structure; they
do not themselves prove a lower bound for arbitrary decoding of fetched
data. No physical page or numerical memory consequence is asserted.
