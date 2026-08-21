#!/bin/bash
# usage: run_exp.sh <mnemonic> <steps> <swept args...>
# Fixed template; only the seven swept options vary in "$@".
M=$1; shift
S=$1; shift
cd /proj/devices/vla
LOG=log/exp.$M; OUT=log/exp.$M.out
rm -f $LOG
conda run --no-capture-output -n dev python vla.py \
  --dataset tiny --preroll --tokenizer pythia31m \
  --context 16 --n_hidden 256 --kernel 3 \
  --batch 250 --monitor 20 \
  --opt sgd --weight_decay 0.0 --momentum 0.0 \
  --schedule const --lr_max 0.01 \
  --seed 1 --device cuda \
  --run_steps $((S+1)) --checkpoint $S \
  --log $LOG --save checkpoint.pt.$M \
  "$@" > $OUT 2>&1
echo "EXP_DONE $M rc=$? args=$*" >> $OUT
