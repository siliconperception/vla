#!/bin/bash
# Phase 0 -- stabilization. Architecture is FIXED at the template (7x7, clock fixed, tap,
# gaussian, ema 0.5, accumulate) and --seed 1 throughout, so every run starts from bit-identical
# weights and the only difference is the optimizer/lr/warmup. Seed 1 is the draw that produced
# the bad startup basin under adamw 1e-3, so this is a paired stress test.
cd /proj/devices/vla
S=4000
A="--n_layers 7 --depth 7 --clock fixed --tap --init gaussian --ema 0.5 --accumulate"
run () { M=$1; shift
  [ -f exp/done.$M ] && { echo "skip $M"; return; }
  echo "=== START $M $* $(date)"; ./exp/run_exp.sh $M $S $A "$@"
  touch exp/done.$M; echo "=== END $M $(date)"; }

run oadam                                                          # baseline: adamw 1e-3, beta2 0.9
run oadamb99  --momentum 0.99                                      # adamw, beta2 0.99 (torch default-ish)
run oadamw1k  --schedule warmup --lr_warmup 1000 --lr_min 0.00001  # adamw 1e-3 with a 1k ramp
run oadam3e4  --lr_max 0.0003                                      # adamw, smaller lr
run osgd003   --opt sgd --nesterov --momentum 0.9 --lr_max 0.003
run osgd01    --opt sgd --nesterov --momentum 0.9 --lr_max 0.01
run osgd03    --opt sgd --nesterov --momentum 0.9 --lr_max 0.03
run osgd1     --opt sgd --nesterov --momentum 0.9 --lr_max 0.1
run osgd03w   --opt sgd --nesterov --momentum 0.9 --lr_max 0.03 --schedule warmup --lr_warmup 1000 --lr_min 0.0001
echo "PHASE0 COMPLETE $(date)"
