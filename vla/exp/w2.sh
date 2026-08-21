#!/bin/bash
# Extend wfix236 from 20K to 100K on openwebtext.
#
# W1 result: wfix236 (fixed ladder 1,2,6,13,31,73,173) and wexp tie on loss (6.305 vs 6.293
# training tail) but differ 16x on reach -- wfix236 still pays +0.19/+0.14/+0.09 nats at
# c=32/64/96 where wexp is flat at 0.00 past c=32. The ladder genuinely uses document-scale
# context; exp is a ~10-token model.
#
# Open question this run answers: wfix236 is 0.10 nats behind held-out, but its gradient was
# still RISING at 20K (5.02 -> 5.57, vs wexp flat at ~4.6) and its slowest layer had written
# only ~115 times in the whole run against wexp's ~3300 per middle layer. If the gap is a
# training-budget artifact it should close and reverse; L7 reaches ~578 writes by 100K.
#
# --load resumes weights, optimizer-free (sgd, no state) and continues the step count.
# Checkpoint every 5000 so reach can be measured mid-run: if reach DEGRADES as loss improves,
# that is the reach/loss trade reasserting at scale and worth catching early.
cd /proj/devices/vla
conda run --no-capture-output -n dev python vla.py \
  --dataset web --preroll --tokenizer pythia31m \
  --context 16 --n_hidden 256 --kernel 3 \
  --batch 250 --monitor 20 \
  --opt sgd --weight_decay 0.0 --momentum 0.0 \
  --schedule const --lr_max 0.01 \
  --seed 1 --device cuda \
  --n_layers 7 --depth 7 --clock fixed --clock_base 2.36 \
  --tap --init gaussian --ema 0.5 --accumulate \
  --load checkpoint.pt.wfix236 --save checkpoint.pt.wfix236 \
  --run_steps 80001 --checkpoint 5000 \
  --log log/exp.wfix236 > log/exp.wfix236.out 2>&1
echo "W2 COMPLETE rc=$? $(date)"
