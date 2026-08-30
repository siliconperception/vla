#!/bin/bash
# usage: run_exp.sh <mnemonic> <steps> <extra args...>
M=$1; shift
S=$1; shift
LOG=/proj/devices/vla/log/exp.$M
cd /proj/devices/vla
conda run --no-capture-output -n dev python vla.py \
  --dataset tiny --preroll --tokenizer pythia31m \
  --context 16 --n_hidden 256 --kernel 3 \
  --batch 250 --monitor 20 --checkpoint 5000 \
  --opt adamw --weight_decay 0.0 --momentum 0.9 \
  --schedule const --lr_max 0.001 --seed 1 \
  --run_steps $S --save checkpoint.pt.$M \
  "$@" > $LOG.out 2>&1
echo "DONE $M rc=$?" >> $LOG.out
