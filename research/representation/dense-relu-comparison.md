# Dense ReLU experiment results

The [reproducible experiment](dense-relu-relevance.md) passed all seven configurations on the same 129 texts and three dependent layers: 2,709 exact layer evaluations. Every configuration matched the reference output and active-index trace, and every fetched byte matched the original source. The matrices are generated dense signed-integer fixtures.

| Method | Step bits | Squared sums | Resident guide bytes, all layers | Original up bytes read | Original down bytes read | Up rows proved inactive |
|---|---:|---|---:|---:|---:|---:|
| streamed | 0 | False | 171 | 442,368 | 229,080 | 144 |
| represented | 4 | False | 2,679 | 229,824 | 229,080 | 9,000 |
| represented | 4 | True | 2,895 | 229,704 | 229,080 | 9,005 |
| represented | 8 | False | 1,911 | 238,920 | 229,080 | 8,621 |
| represented | 8 | True | 2,271 | 235,128 | 229,080 | 8,779 |
| represented | 12 | False | 1,311 | 385,536 | 229,080 | 2,512 |
| represented | 12 | True | 1,815 | 347,904 | 229,080 | 4,080 |

The streamed comparator reads original up rows, computes exact ReLU activations, and reads only original down columns with a positive activation. It recognizes an all-zero query without reading either matrix. Thus its omitted down columns are not credited to the new representation. Its 171 resident bytes are the three actual packed layout/identity headers.

The full source model has 6,912 weight bytes; embeddings add 6,144 bytes. Guide sizes above exclude input/output arrays, interpreter and arithmetic scratch, source read buffers, and the active-index verification trace. They are encoded guide sizes, not process peak RAM. The [JSON report](dense-relu-results.json) includes calculation counts and a separate 4,096-byte request-rounding model.

At step eight, the sum guide uses 1,911 resident bytes and reads 238,920 up bytes versus the streamed comparator's 442,368. Both read the same 229,080 down bytes. The difference is 203,448 logical weight bytes over the repeated queries. The guide also performs 222,912 coarse coefficient terms and 121,144 support-coordinate visits; a latency claim requires paying for that work and the actual page/request behavior.

The independently derived omission rule passed [bounded review](remainder-sum-review.md). It applies to exact integer ReLU and retains the source common offset needed for threshold comparisons. It is not a proof for an arbitrary floating-point kernel or another activation function.

## Existing work and originality

[LLM in a flash](https://aclanthology.org/2024.acl-long.678/) already studies external weight storage, selective loading, reuse, and contiguous access. [Deja Vu](https://proceedings.mlr.press/v202/liu23am/liu23am.pdf) already studies predicting contextual activation sparsity. [SparseInfer](https://arxiv.org/abs/2411.12692) predicts ReLU activation sparsity using sign bits. Those primary sources establish a substantial prior field around selective loading; this experiment does not claim to invent that aim.

The retained result is a sound integer certificate that proves inactivity before the source-row read and always resolves uncertainty with original weights. Its ingredients remain interval bounds, quotient coding, bounded sums, and Cauchy–Schwarz. The source review has not established a novel advantage over the fully improved existing methods.
