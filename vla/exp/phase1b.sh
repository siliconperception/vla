#!/bin/bash
# Shape sweep with reach held constant.
#
# Reach is set by the slowest layer's write period p_max, at roughly 4-5x that period, so a
# shape sweep at a fixed --clock_base confounds two things: how many timescales the stack
# has, and how far back the slowest one reaches. Solving b = T**(1/(L-1)) for T=43 pins
# p_max at 43 for every L -- ~4.6 writes per 196-token TinyStories example, and a predicted
# reach of ~190, i.e. document scale -- so --n_layers varies alone.
#
#   L=2  d=25  b=43.000  [1, 43]
#   L=5  d=10  b= 2.561  [1, 3, 7, 17, 43]
#   L=6  d= 8  b= 2.122  [1, 2, 5, 10, 20, 43]
#   L=7  d= 7  b= 1.872  [1, 2, 4, 7, 12, 23, 43]
#   L=10 d= 5  b= 1.519  [1, 2, 2, 4, 5, 8, 12, 19, 28, 43]
#
# L=1 has no ladder to rationalize -- one register, period 1 -- so its only timescale knob is
# --ema, whose window is ~1/DECAY writes. The template's 0.5 gives a ~2-token window, which
# is why it is not a document-reach control at all; 0.01 gives ~100 and is the honest L=1
# entry in this sweep.
cd /proj/devices/vla
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

A="--clock fixed --tap --init gaussian --ema 0.5 --accumulate"
run r7x7   --n_layers 7  --depth 7  $A --clock_base 1.872
run r6x8   --n_layers 6  --depth 8  $A --clock_base 2.122
run r5x10  --n_layers 5  --depth 10 $A --clock_base 2.561
run r10x5  --n_layers 10 --depth 5  $A --clock_base 1.519
run r2x25  --n_layers 2  --depth 25 $A --clock_base 43.0
run r1x50  --n_layers 1  --depth 50 --clock fixed --tap --init gaussian --ema 0.01 --accumulate
echo "PHASE1B COMPLETE $(date)"
