#!/bin/bash
# usage: run.sh <mnemonic> <steps> <args overriding the baseline...>
# BASELINE = e30 config (3x17, bn_track ON).  7x7 was adopted at 12:45 and
# REVERTED at 14:20: with tracking on it has a +1.66 nat TRAIN/EVAL GAP and
# runs away in eval, while 3x17 has none.  Measured at 5K, same lr:
#   3x17 m=0.1   train 6.7144  held-out 6.6974  gap -0.017  runaway  0.0%
#   7x7  m=0.1   train 6.7889  held-out 8.4471  gap +1.658  runaway  2.2%
#   7x7  (e24)   train 6.6230  held-out    nan             runaway 100.0%
# The reach result that motivated 7x7 was measured on --no-bn_track models,
# where eval uses live batch stats and this failure is invisible.
# Anything in "$@" overrides it,
# since argparse takes the last occurrence of a flag.
#
# MONITORING (2026-08-24, Phase 2): --gen_interval 500 --eval_interval 5000.  These are
# observation cadence, NOT model configuration -- neither touches a weight, an optimizer
# state or the data stream, so runs before and after this line are directly comparable.
# Generation moved to 500 because the text has overturned the scalar reading more than once
# and a sample is cheap; held-out eval runs at the checkpoint cadence so every EVAL line in
# the log describes weights that exist on disk and can be re-derived with exp/score.py.
M=$1; shift
S=$1; shift
cd /proj/devices/vla
mkdir -p checkpoint
rm -f log/exp.$M
conda run --no-capture-output -n dev python vla.py \
  --dataset web --preroll --tokenizer pythia31m \
  --context 16 --n_hidden 256 --kernel 3 \
  --batch 250 --monitor 20 \
  --opt sgd --momentum 0.0 --weight_decay 0.0 \
  --schedule const --lr_max 0.03 --seed 1 --device cuda \
  --n_layers 3 --depth 17 --clock fixed --clock_base 13.15 \
  --init zero --ema 0.5 --accumulate \
  --run_steps $((S+1)) --checkpoint 5000 \
  --gen_interval 500 --eval_interval 5000 \
  --log log/exp.$M --save checkpoint/$M.pt \
  "$@" > log/exp.$M.out 2>&1
echo "RUN_DONE $M rc=$? $(date)" >> log/exp.$M.out
