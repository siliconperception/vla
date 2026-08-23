#!/bin/bash
# GroupNorm optimizer variants (user, 2026-08-23).  lr is ruled out: E39 (lr 0.03)
# and E43 (lr 0.1) both sat at the unigram floor with grad 0.47-0.60 -- IDENTICAL
# gradient magnitude across a 3.3x lr change, which is expected since lr scales
# the update and not the gradient, and confirms the gradient itself is the
# problem.  E43 also pinned dff_max at exactly 4.33 for 4000 consecutive steps:
# the state reached a fixed point and stopped moving.  Not exploding, not dying,
# frozen -- a failure mode not seen anywhere else in this study.
# Plain SGD cannot escape a flat region; momentum accumulates across steps and
# AdamW rescales per parameter, so both attack a small-gradient regime directly.
cd /proj/devices/vla
go () { M=$1; E=$2; shift 2
  [ -f exp/done.$M ] && { echo "skip $M"; return; }
  echo "=== START $M $* $(date '+%H:%M')"
  ./exp/watch.sh $M $E > /dev/null 2>&1 & WP=$!
  ./exp/run.sh $M 20000 --norm group --norm_groups 32 "$@"
  sleep 25; kill $WP 2>/dev/null
  cp -f checkpoint/$M.pt checkpoint/$M.final.pt 2>/dev/null
  conda run --no-capture-output -n dev python exp/score.py checkpoint/$M.final.pt \
      --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null \
      | grep -E "^$M" | tee -a PLAN.txt
  touch exp/done.$M; echo "=== END $M $(date '+%H:%M')"; }

go e45_gn_mom  E45 --lr_max 0.1 --momentum 0.9 --nesterov
go e46_gn_adamw E46 --opt adamw --lr_max 0.001 --beta1 0.9 --beta2 0.999
go e47_gn_adamw3 E47 --opt adamw --lr_max 0.003 --beta1 0.9 --beta2 0.999
echo "GROUPNORM4 COMPLETE $(date)"
