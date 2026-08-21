#!/bin/bash
# Group A -- establish a STABLE, low-variance exp baseline before ablating anything.
#
# Two runs of the identical exp config split: sexp held out at 3.954, xrep DIVERGED at
# inference (1.4e9) with no training-time warning (dff_max 46 vs 31, both normal). So
# inference stability is a coin flip for exp, and it is the gate -- a model that detonates
# at position 99 has no reach whatever its loss. Nothing below is worth measuring until a
# variant is found that is stable across replicates.
#
# exp's hold is base**k, k ~ Geometric(1/2). E[h] = 1/(2-base), which DIVERGES at base 2 --
# the historical hard-coded value -- so --clock_max was never a tail control, it was the only
# thing making the mean finite, and it does that by parking an atom of probability 1/cap
# exactly at the cap. Any base < 2 makes the mean finite with no atom, and is not even weaker:
# base 2 capped at 1024 gives E[h]=6, base 1.9 uncapped gives 10. So the cap is demoted to a
# rare-event backstop (at base 1.9 it binds 1/2048 of draws) and the base is the real knob.
# Mapping the base axis therefore tests the divergence mechanism directly, since hold weight
# and tail weight move together:
#   base 1.5  E[h]=2   P(hold > 1 document) = 1/8192   reach ~9
#   base 1.9  E[h]=10  P(hold > 1 document) = 1/298    reach ~43
#   base 2.0  E[h]=6   P(hold > 1 document) = 1/195    reach ~26   (= sexp/xrep, one diverged)
# Every setting runs at two seeds: neither a variance nor a divergence rate can be measured
# with one run. sincr2 replicates the best stable config so far, for comparison.
cd /proj/devices/vla
run () { M=$1; shift
  [ -f exp/done.$M ] && { echo "skip $M"; return; }
  S=$(cat exp/STEPS)
  echo "=== START $M ($S steps) $* $(date)"
  ./exp/run_exp.sh $M $S "$@"
  conda run --no-capture-output -n dev python exp/memtest.py --load checkpoint.pt.$M \
      --docs 500 --batch 250 --minlen 96 --maxlen 384 --periods 0,8,32,128 \
      > log/exp.$M.mem 2>&1
  conda run --no-capture-output -n dev python exp/reach.py --load checkpoint.pt.$M \
      --docs 400 --rows 1000 --periods 32,128 > log/exp.$M.reach 2>&1
  touch exp/done.$M
  echo "=== END $M $(date)"; }

A="--clock exp --tap --init gaussian --ema 0.5 --accumulate"
I="--clock incr --tap --init gaussian --ema 0.5 --accumulate"

run xb15a   --n_layers 7 --depth 7 $A --clock_base 1.5 --seed 11
run xb15b   --n_layers 7 --depth 7 $A --clock_base 1.5 --seed 12
run xb19a   --n_layers 7 --depth 7 $A --clock_base 1.9 --seed 11
run xb19b   --n_layers 7 --depth 7 $A --clock_base 1.9 --seed 12
run sincr2  --n_layers 7 --depth 7 $I --seed 7
echo "GROUPA COMPLETE $(date)"
