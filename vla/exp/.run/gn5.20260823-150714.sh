#!/bin/bash
# GroupNorm + AdamW (user, 2026-08-23).  Ruled out so far, all stuck at the
# unigram floor with GroupNorm(32):
#   lr 0.03 plain sgd      grad 0.48-0.95
#   lr 0.1  plain sgd      grad 0.47-0.60, dff_max FROZEN at 4.33 for 4000 steps
#   lr 0.1  sgd + nesterov grad 0.15-0.22  -- momentum made it WORSE
# Momentum lowering the gradient means successive gradients DISAGREE and cancel,
# not that the step is too small.  AdamW rescales each parameter by its own
# gradient RMS, so a uniformly small and sign-inconsistent gradient still yields
# a full-size step -- the one mechanism left that addresses this directly.
# Note the reversal: AdamW's per-parameter normalization was a LIABILITY with
# BatchNorm (BN made weight directions loss-neutral and AdamW inflated exactly
# those, producing the day-one plateau).  Here the pathology is the opposite sign.
cd /proj/devices/vla
go () { M=$1; E=$2; shift 2
  [ -f exp/done.$M ] && { echo "skip $M"; return; }
  echo "=== START $M $* $(date '+%H:%M')"
  ./exp/watch.sh $M $E > /dev/null 2>&1 & WP=$!
  ./exp/run.sh $M 20000 --norm group --norm_groups 32 --opt adamw --beta1 0.9 --beta2 0.999 "$@"
  sleep 25; kill $WP 2>/dev/null
  cp -f checkpoint/$M.pt checkpoint/$M.final.pt 2>/dev/null
  conda run --no-capture-output -n dev python exp/score.py checkpoint/$M.final.pt \
      --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null \
      | grep -E "^$M" | tee -a PLAN.txt
  touch exp/done.$M; echo "=== END $M $(date '+%H:%M')"; }

go e46_gn_adamw   E46 --lr_max 0.001
go e47_gn_adamw3  E47 --lr_max 0.003
go e48_gn1_adamw  E48 --lr_max 0.001 --norm_groups 1
echo "GROUPNORM5 COMPLETE $(date)"
