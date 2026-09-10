# FALSIFICATION_RESULTS.md — fixed-seed counterexample-search record; depends on minimax_residual_sampling.py.

Run date: 5 September 2026.

Command:

```text
/usr/bin/time -p python3 pure_math_lab/minimax_residual_sampling.py
```

Result: exit status 0.

```text
estimator/covariance cases checked: 400
maximum direct-enumeration gap: 1.364e-12
two-column cases checked: 160
maximum closed-form evaluation gap: 8.527e-14
maximum closed-form minus dual-grid value: 5.684e-14
smallest grid value minus closed form: 0.000e+00
orthogonal three-column cases checked: 30
largest water-filling equalization gap: 2.842e-14
smallest orthogonal grid value minus closed form: 1.887e-02
rank-one three-column cases checked: 80 (41 balanced, 39 dominant)
maximum rank-one formula gap: 1.990e-13
smallest rank-one grid value minus closed form: 2.842e-14
orthogonal two-column family
ratio  frobenius-law variance  minimax variance  improvement
    1              1.00000000        1.00000000     1.000000  p=[0.5, 0.5]
    4              4.00000000        2.00000000     2.000000  p=[0.6666666666666666, 0.3333333333333333]
   16             16.00000000        4.00000000     4.000000  p=[0.8, 0.2]
   64             64.00000000        8.00000000     8.000000  p=[0.8888888888888888, 0.1111111111111111]
  256            256.00000000       16.00000000    16.000000  p=[0.9411764705882353, 0.058823529411764705]
 1024           1024.00000000       32.00000000    32.000000  p=[0.9696969696969697, 0.030303030303030304]
 4096           4096.00000000       64.00000000    64.000000  p=[0.9846153846153847, 0.015384615384615385]
real 36.11
user 34.34
sys 0.53
```

These are 670 fixed-seed cases plus finite embedded grids. The direct estimator/covariance check
uses two computational routes. The covariance, primal-grid, and closed-form evaluations share a
Gram helper and a floating Jacobi eigensolver; the dual-boundary and equalization checks are
separate scalar computations. Every grid is finite. The program can find counterexamples but
cannot prove global optimality. The written proofs carry the mathematical claim.
