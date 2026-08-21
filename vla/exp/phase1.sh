#!/bin/bash
# Architecture study. Optimizer fixed at sgd+nesterov m0.9 const lr 0.01; only the seven
# swept options vary, with --n_layers * --depth held at ~50 so every model is ~30M weights.
# Step count is read from exp/STEPS each run so the screen can be lengthened mid-sweep if
# the breakthrough turns out to come late -- the stack is 49 convs deep with no skip
# connections and a one-step gradient horizon, so it organizes slowly and a screen that
# ends before the breakthrough ranks nothing.
cd /proj/devices/vla
A="--clock fixed --tap --init gaussian --ema 0.5 --accumulate"   # template state dynamics
run () { M=$1; shift
  [ -f exp/done.$M ] && { echo "skip $M"; return; }
  S=$(cat exp/STEPS)
  echo "=== START $M ($S steps) $* $(date)"
  ./exp/run_exp.sh $M $S "$@"
  conda run --no-capture-output -n dev python exp/memtest.py --load checkpoint.pt.$M \
      --docs 500 --batch 250 --minlen 96 --maxlen 384 --periods 0,8,32,128 \
      > log/exp.$M.mem 2>&1
  touch exp/done.$M
  echo "=== END $M $(date)"; }

# clock, at the template shape
run sbase  --n_layers 7  --depth 7  $A                                       # template
run ssync  --n_layers 7  --depth 7  --clock sync --tap --init gaussian --ema 0.5 --accumulate
run sincr  --n_layers 7  --depth 7  --clock incr --tap --init gaussian --ema 0.5 --accumulate
run sexp   --n_layers 7  --depth 7  --clock exp  --tap --init gaussian --ema 0.5 --accumulate
# stack shape, n_layers * depth ~ 50
run s5x10  --n_layers 5  --depth 10 $A
run s10x5  --n_layers 10 --depth 5  $A
run s2x25  --n_layers 2  --depth 25 $A
run s1x50  --n_layers 1  --depth 50 $A
# state-dynamics options, one at a time off the template
run snotap --n_layers 7  --depth 7  --clock fixed        --init gaussian --ema 0.5 --accumulate
run snoema --n_layers 7  --depth 7  --clock fixed --tap  --init gaussian --accumulate
run snoacc --n_layers 7  --depth 7  --clock fixed --tap  --init gaussian --ema 0.5 --no-accumulate
run srelu  --n_layers 7  --depth 7  --clock fixed --tap  --init relu     --ema 0.5 --accumulate
run szero  --n_layers 7  --depth 7  --clock fixed --tap  --init zero     --ema 0.5 --accumulate
echo "PHASE1 COMPLETE $(date)"
