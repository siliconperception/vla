#!/bin/bash
# Phase 0b -- beta1 sweep for --opt adamw. Same paired design as phase 0: template
# architecture, --seed 1, so every run starts from bit-identical weights.
# beta1 is the gradient-EMA decay; window ~= 1/(1-beta1) steps.
# The first arm holds beta2 at the template's 0.9 so beta1 is varied one factor at a time
# off the baseline; the second arm checks beta1 at a long beta2 in case beta2 0.9 is itself
# the thing that breaks, which would otherwise sink the whole first arm.
cd /proj/devices/vla
S=4000
A="--n_layers 7 --depth 7 --clock fixed --tap --init gaussian --ema 0.5 --accumulate"
run () { M=$1; shift
  [ -f exp/done.$M ] && { echo "skip $M"; return; }
  echo "=== START $M $* $(date)"; ./exp/run_exp.sh $M $S $A "$@"
  touch exp/done.$M; echo "=== END $M $(date)"; }

#            beta1 arm at the template's beta2 = 0.9   (beta1 0.9 == oadam, already run)
run ob1_00   --beta1 0.0  --beta2 0.9      # no gradient averaging: plain sign-normalized step
run ob1_50   --beta1 0.5  --beta2 0.9      # ~2-step window
run ob1_95   --beta1 0.95 --beta2 0.9      # ~20-step window
run ob1_99   --beta1 0.99 --beta2 0.9      # ~100-step window
#            beta1 at a long second-moment window
run ob1_90d  --beta1 0.9  --beta2 0.999    # torch's own defaults
run ob1_95d  --beta1 0.95 --beta2 0.999
run ob1_99d  --beta1 0.99 --beta2 0.999
echo "PHASE0B COMPLETE $(date)"
