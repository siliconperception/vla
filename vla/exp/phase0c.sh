#!/bin/bash
# Phase 0c -- stabilization, REPLICATED and directed. 1200 steps x 15 runs ~= 1.7 h.
#
# What the transient is: ContextCNN is Conv -> BatchNorm(affine=False) -> ReLU, so its
# output is bounded O(1) in TRAIN mode. But the DFF carried to the next step is recomputed
# in EVAL mode (vla.py:2550), where BatchNorm uses running statistics instead of batch
# statistics. Early on those running stats lag the weights, and the mismatch compounds
# multiplicatively through n_layers*depth = 49 BatchNorms -> dff_max 1e2..1e5. A state that
# large drowns the token injection in `fb(dff) + deep_proj(o)`, which is why the loss parks
# at ~6.3 until the running stats catch up.
#
# Two runs at IDENTICAL config and IDENTICAL --seed 1 landed in different basins (loss 6.08
# vs 5.16 at step 2000), so the basin is decided by the nondeterministic data order, not the
# init draw. No single run can test a fix; every setting gets 3 replicates and is scored by
# how many of the 3 settle.  settle = first step after which dff_max stays below 100.
cd /proj/devices/vla
S=1200
A="--n_layers 7 --depth 7 --clock fixed --tap --init gaussian --ema 0.5 --accumulate"
# --tap is store_true and cannot be switched off, so arm D gets its own arch string.
AD="--n_layers 7 --depth 7 --clock fixed --init gaussian --ema 0.5 --accumulate"
run () { M=$1; shift
  [ -f exp/done.$M ] && { echo "skip $M"; return; }
  echo "=== START $M $* $(date)"; ./exp/run_exp.sh $M $S "$@"
  touch exp/done.$M; echo "=== END $M $(date)"; }

# A  baseline, adamw betas (0.9,0.9) lr 1e-3           -- base rate of the bad basin
# B  --beta2 0.999   H: a 10-step second-moment window lets one gradient spike rescale every
#                       step, so weights move faster than BatchNorm's running stats track
# C  warmup 300      H: same cause attacked directly -- hold the weights nearly still while
#                       the running statistics converge
# D  no --tap        H: tap is the one trainable map between the normalized ContextCNN
#                       output and the register, and it sits in a BN-scale-invariant
#                       direction the loss barely constrains, so it is free to drift large
# E  sgd + nesterov  H: no per-parameter normalization, so BN-invariant directions take
#                       steps proportional to their (tiny) true gradient, not the full lr.
#                       Three lrs rather than three seeds -- lr is uncalibrated for sgd here.
for R in 1 2 3; do
  run pA$R  $A  --seed $((100+R))
  run pB$R  $A  --seed $((100+R)) --beta2 0.999
  run pC$R  $A  --seed $((100+R)) --schedule warmup --lr_warmup 300 --lr_min 0.00001
  run pD$R  $AD --seed $((100+R))
done
run pE01 $A --seed 101 --opt sgd --nesterov --momentum 0.9 --lr_max 0.01
run pE03 $A --seed 102 --opt sgd --nesterov --momentum 0.9 --lr_max 0.03
run pE10 $A --seed 103 --opt sgd --nesterov --momentum 0.9 --lr_max 0.1
echo "PHASE0C COMPLETE $(date)"
