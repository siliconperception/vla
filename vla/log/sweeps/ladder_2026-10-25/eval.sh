#!/bin/bash
# eval.sh <checkpoint> <ctx_tau> <out log>: the selection evals for one 3c checkpoint, one shot (--eval, all rare evals on):
# held-out EVAL on 400 fineweb docs, EVALH (100 samples), EVALL (8 streams x 10K tokens), EVALM. min_p as saved.
cd /proj/devices/vla
conda run --no-capture-output -n dev python vla.py --load $1 --clock_hz 25 --ctx_tau $2 --eval --eval_corpora fineweb \
  --eval_docs 400 --eval_bands '' --eval_hold 100 --eval_free 10000 --eval_pairs 1000 --gen_score --log $3 > $3.out 2>&1
grep -E '^(EVAL|EVALH|EVALL|EVALM) ' $3 | tail -4 | cut -c1-200
