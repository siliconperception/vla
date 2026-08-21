#!/bin/bash
# wnotap -- no --tap, bare ReLU feedback, trained long on openwebtext.
#
# ContextCNN is Conv->BatchNorm(affine=False)->ReLU throughout, so its output is bounded.
# The feedback path is the only unnormalized thing in the model: tap, deep_proj and
# decoder.proj are bare 1x1 convs, so the recurrence gain is unconstrained and drifts above 1
# by ~55-65K steps. Bounding the STATE (--clip_dff) failed -- collapsed harder, 100% runaway
# at 60K vs 40.5% unclipped -- because the drift is in the map, not the state.
#
# Dropping --tap deletes that map rather than constraining it: the register then receives
# ContextCNN's output directly, post-BatchNorm and post-ReLU, so it is bounded by construction
# and sparse (~50% exact zeros). Simplest available fix, and the strongest guarantee.
#
# Trains from scratch (no tap = different parameter set, cannot resume from the 40K weights),
# so its LOSS at any step lags the tapped runs. Judge it on runaway rate:
#   wexp     0.0% @20K      wfix236  1.8% @20K, 1.0% @40K, 40.5% @60K      wclip 100% @60K
#
# --init gaussian is kept deliberately, to change one thing at a time. Note the flag's own
# docs say gaussian suits a DENSE register, i.e. it is the setting chosen FOR --tap; with a
# sparse ReLU register --init relu is the matching seed and is worth a follow-up.
cd /proj/devices/vla
conda run --no-capture-output -n dev python vla.py \
  --dataset web --preroll --tokenizer pythia31m \
  --context 16 --n_hidden 256 --kernel 3 \
  --batch 250 --monitor 20 \
  --opt sgd --momentum 0.0 --weight_decay 0.0 \
  --schedule const --lr_max 0.01 \
  --seed 1 --device cuda \
  --n_layers 7 --depth 7 --clock fixed --clock_base 2.36 \
  --init gaussian --ema 0.5 --accumulate \
  --save checkpoint.pt.wnotap \
  --run_steps 100001 --checkpoint 5000 \
  --log log/exp.wnotap > log/exp.wnotap.out 2>&1
echo "W6 COMPLETE rc=$? $(date)"
