#!/bin/bash
# Phase 0c continued, reordered. Arms A (baseline), B (--beta2 0.999) and C (warmup 300)
# all stalled on their first replicate, which rules out "slow the optimizer down" in all
# three of its forms. SGD is the arm that differs mechanically -- no per-parameter
# normalization, so directions the loss barely constrains (which is where the runaway
# channels live) get steps sized by their true tiny gradient instead of the full lr.
# It was queued last; it is now first, and widened, since it carries more weight than the
# remaining replicates of arms already known to fail.
cd /proj/devices/vla
S=1200
A="--n_layers 7 --depth 7 --clock fixed --tap --init gaussian --ema 0.5 --accumulate"
AD="--n_layers 7 --depth 7 --clock fixed --init gaussian --ema 0.5 --accumulate"
run () { M=$1; shift
  [ -f exp/done.$M ] && { echo "skip $M"; return; }
  echo "=== START $M $* $(date)"; ./exp/run_exp.sh $M $S "$@"
  touch exp/done.$M; echo "=== END $M $(date)"; }

# E: sgd lr ladder, nesterov momentum 0.9, plus one plain sgd (momentum 0) point
run pE003 $A --seed 101 --opt sgd --nesterov --momentum 0.9 --lr_max 0.003
run pE01  $A --seed 102 --opt sgd --nesterov --momentum 0.9 --lr_max 0.01
run pE03  $A --seed 103 --opt sgd --nesterov --momentum 0.9 --lr_max 0.03
run pE10  $A --seed 104 --opt sgd --nesterov --momentum 0.9 --lr_max 0.1
run pF03  $A --seed 105 --opt sgd --momentum 0.0 --lr_max 0.03      # plain sgd, no momentum
# D: the structural arm -- what sits between the layer output and the register
run pD1   $AD --seed 101
run pD2   $AD --seed 102
run pD3   $AD --seed 103
# remaining replicates of the arms already known to stall, for the base-rate denominator
run pA2 $A --seed 102
run pA3 $A --seed 103
run pB2 $A --seed 102 --beta2 0.999
run pC2 $A --seed 102 --schedule warmup --lr_warmup 300 --lr_min 0.00001
echo "PHASE0C2 COMPLETE $(date)"
