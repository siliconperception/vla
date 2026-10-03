# 100% fineweb-edu runs with >= 100K steps vs v224 (2026-10-02)
Metric: EVAL smolfwedu clean (100 held-out docs, hash holdout), runaway % in parens. batch 250 tokens/step.

| run  | n_hidden | DFF / topology                          | data                        | opt / lr       | 100K | 200K | 300K | 400K | 700K | best (step) |
|------|---------:|-----------------------------------------|-----------------------------|----------------|-----:|-----:|-----:|-----:|-----:|------------|
| v224 | 4096 | ctx_ema 4,16 (2 linout copies) + linin  | sub100k closed, 1 shard     | sgd 0.03       | 5.833 | 5.563 | 5.368 | 5.347 | 5.131 (3%) | 5.131 (700K, running) |
| v206/v207 | 2048 | 1 reg, ema_ladder 16, linout       | sub20k ep3 (v207: stream)   | rmsprop 1e-4   | 5.950 | 5.681 | 5.578 | 5.506 | 5.334 (0%) | 5.190 (1.2M) |
| v202 | 2048 | 1 reg, ema_ladder 16, linout            | sub20k ep3                  | sgd 0.03       | 5.993 | 5.756 | 5.631 | 5.520 | 5.364 (4%) | 4.933 (3.46M) |
| v199 | 2048 | 1 reg, ema16                            | sub2k ep30                  | sgd 0.1        | 6.094 | 5.823 | 5.772 | 5.695 | 5.701 (17%) | 5.468 (1.78M, 34% runaway) |
| v192 | 2048 | 1 reg, ema16, d32                       | sub2k ref0.5                | sgd 0.1        | 6.082 | 5.978 | 5.823 | 5.738 | -    | 5.602 (460K) |
| v208 | 2048 | 1 reg, ema16                            | stream                      | rmsprop 1e-5   | 6.101 | 5.845 | 5.769 | -    | -    | 5.689 (340K) |
| v203 | 2048 | 1 reg, ema16                            | sub20k ep3                  | sgd 0.01       | 6.190 | 5.916 | 5.785 | -    | -    | 5.713 (320K) |
| v178 | 512  | 1 reg, ema4, d32                        | sub10k ep20                 | sgd 0.1        | 6.192 | 6.120 | 6.111 | 5.905 | 5.851 | 5.494 (3.34M) |
| v182 | 512  | 1 reg, ema16, d32                       | sub10k ref0.5               | sgd 0.1        | 6.358 | 6.190 | 6.066 | 6.061 | 5.984 | 5.708 (1.82M) |
| v190 | 512  | 1 reg, ema16, d32                       | sub2k sched8                | sgd 0.1        | 6.336 | 6.120 | 6.041 | 6.109 | 6.011 | 5.708 (2.04M) |
| v185 | 512  | 1 reg, ema16, d32                       | sub1k ref1.0                | sgd 0.1        | 6.272 | 6.179 | 6.034 | 6.008 | 5.859 | 5.785 (1.08M) |
| v176 | 256  | 1 reg, ema4, d32                        | sub10k                      | sgd 0.1        | 6.223 | 6.073 | 5.908 | 5.882 | -    | 5.816 (440K) |
| r4   | 512  | d32                                     | sub10k ep20                 | sgd 0.1        | 6.283 | 5.999 | 6.049 | 5.810 | -    | 5.810 (400K) |
| v197 | 2048 | 1 reg, ema16                            | stream                      | sgd 0.1        | 5.871 | -    | -    | -    | -    | 5.871 (100K) |
| v201 | 2048 | 1 reg, ema16                            | sub20k ep3                  | sgd 0.1        | 5.897 | -    | -    | -    | -    | 5.897 (100K) |
Excluded from the step table: v11/v12c (eval on fwedu, 400 docs, older protocol), runs that stopped near 100K.
