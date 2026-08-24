#!/bin/bash
# Vanilla SGD with the read-path DFF constraint (user, 2026-08-23).
# E57 (adamw 1e-3) blew up: it sat near the unigram floor to step 1000 with
# dff_max decaying 8.2e4 -> 2.6e3, then at step 1500 went to loss 1.35e6 with
# grad 6.9e7 and dff_max 1.1e7.  Note the REGISTER is unbounded by design now --
# it holds raw ReLU output -- and the read is scale-free, so the recurrence is
# bounded but the WEIGHTS are not.  AdamW's per-parameter normalization gives
# every direction a full-size step regardless of gradient magnitude, which is the
# wrong medicine when the weights are what is diverging.
# Vanilla SGD scales the step by the actual gradient, so it should calm down.
cd /proj/devices/vla
go () { M=$1; E=$2; shift 2
  [ -f exp/done.$M ] && { echo "skip $M"; return; }
  echo "=== START $M $* $(date '+%H:%M')"
  ./exp/watch.sh $M $E > /dev/null 2>&1 & WP=$!
  ./exp/run.sh $M 20000 --norm none --init relu --dff_norm std --opt sgd "$@"
  sleep 25; kill $WP 2>/dev/null
  cp -f checkpoint/$M.pt checkpoint/$M.final.pt 2>/dev/null
  conda run --no-capture-output -n dev python exp/score.py checkpoint/$M.final.pt \
      --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null \
      | grep -E "^$M" | tee -a PLAN.txt
  touch exp/done.$M; echo "=== END $M $(date '+%H:%M')"; }
go e60_dstd_sgd03  E60 --lr_max 0.03
go e61_dstd_sgd01  E61 --lr_max 0.01
go e62_dstd_sgd003 E62 --lr_max 0.003
echo "DFF SGD COMPLETE $(date)"
