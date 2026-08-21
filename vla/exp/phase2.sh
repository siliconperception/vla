#!/bin/bash
# exp-focused study. --clock exp won the clock group outright on held-out loss
# (3.954 vs incr 4.396, fixed 4.530), is stable, and costs nothing at runtime
# (2.93 steps/s, marginally the fastest of the three).
#
# exp has no --clock_base ladder: layers 1 and N write every step and the middle layers each
# draw 2**k, k ~ Geometric(1/2), capped at --clock_max. The cap is a weak lever on the mean
# hold (log2(N)/2+1: 4 steps at 64, 6 at 1024, 8 at 16384) and a direct one on the tail, so
# it is the only knob exp has on reach -- which is where exp is currently weakest, saturating
# by c~16-32.
#
# xrep runs first: exp is stochastic by construction, so its run-to-run spread has to be
# known before any of the differences below can be read.
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

# noise floor for the randomized mode
run xrep    --n_layers 7  --depth 7  $A --seed 7
# shape: exp clocks layers 2..N-1, so n_layers sets how many middle layers are randomized
run x5x10   --n_layers 5  --depth 10 $A
run x10x5   --n_layers 10 --depth 5  $A
run x6x8    --n_layers 6  --depth 8  $A
# reach: the hold cap, exp's only timescale knob
run xcap64  --n_layers 7  --depth 7  $A --clock_max 64
run xcap16k --n_layers 7  --depth 7  $A --clock_max 16384
# ablations, now against the exp baseline rather than the abandoned fixed one
run xnotap  --n_layers 7  --depth 7  --clock exp        --init gaussian --ema 0.5 --accumulate
run xnoema  --n_layers 7  --depth 7  --clock exp --tap  --init gaussian --accumulate
run xnoacc  --n_layers 7  --depth 7  --clock exp --tap  --init gaussian --ema 0.5 --no-accumulate
run xqread  --n_layers 7  --depth 7  $A --qproj read
run xrelu   --n_layers 7  --depth 7  --clock exp --tap  --init relu     --ema 0.5 --accumulate
echo "PHASE2 COMPLETE $(date)"
