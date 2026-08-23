#!/bin/bash
# usage: run.sh <mnemonic> <steps> <args overriding the baseline...>
# Baseline is wnotap (see PLAN.txt section 1). Anything passed in "$@" overrides it,
# since argparse takes the last occurrence of a flag.
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
  --log log/exp.$M --save checkpoint/$M.pt \
  "$@" > log/exp.$M.out 2>&1
echo "RUN_DONE $M rc=$? $(date)" >> log/exp.$M.out
