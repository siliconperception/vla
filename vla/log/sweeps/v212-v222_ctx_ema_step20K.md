# v212-v222 at step 20K (2026-10-01)
Common: mix tinytb:0.5,fineweb:0.5, pythia31m, c_context 256, depth 16, context 8, n_layers 1, sgd coswarm lr 0.03, --linout.
Eval: 100 docs/corpus, runaway = doc > 20 nats; "clean" = mean over non-runaway docs. Train = mean of STEP losses 18K-20K.

| run  | n_hidden | DFF                 | linout k | train | tinytb clean | tinytb run% | fineweb clean | fineweb run% | dff_std | dff_max | GENSCORE nats |
|------|---------:|---------------------|---------:|------:|-------------:|------------:|--------------:|-------------:|--------:|--------:|--------------:|
| v212 | 2048 | 1, ema_ladder 16    | 1 | 5.721 | 5.205 |  1% | 6.617 |  5% | 0.41 |  4.8 | 7.53 |
| v213 | 2048 | ctx_ema 4,16        | 1 | 5.597 | 5.130 |  0% | 6.388 |  1% | 0.29 |  3.3 | 8.31 |
| v214 |  256 | ctx_ema 4,16        | 3 | 5.833 | 5.405 |  2% | 6.701 |  2% | 1.03 | 33.4 | 8.73 |
| v215 |  512 | ctx_ema 4,16        | 3 | 5.756 | 5.516 |  5% | 6.860 | 17% | 0.74 | 15.5 | 6.81 |
| v216 | 1024 | ctx_ema 4,16        | 3 | 5.753 | 5.335 | 22% | 6.702 | 50% | 0.51 |  6.5 | 7.36 |
| v217 | 1024 | ctx_ema 4,16        | 1 | 5.671 | 5.167 |  0% | 6.505 |  1% | 0.41 |  5.4 | 7.16 |
| v219 | 4096 | ctx_ema 4,16 (K linout copies) + linin | 1 | 5.486 | 5.042 |  1% | 6.356 |  3% | 0.21 |  2.6 | 6.85 |
| v220 | 4096 | ctx_ema 4,16 (ONE shared linout) + linin | 1 | 5.792 | 5.397 |  0% | 6.560 |  3% | 0.30 |  3.5 | 7.25 |
| v222 | 4096 | ctx_ema 4,16 (shared linout) + linin over concat[input,DFF1,DFF2] | 1 | 5.661 | 5.346 |  2% | 6.546 |  0% | 0.31 |  3.9 | 7.42 |
