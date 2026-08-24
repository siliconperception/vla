#!/bin/bash
# --dff_norm std (read path), --norm none, --init relu.  lr ladder continues down.
# E60 lr 0.03 -> NaN at step 3.  E61 lr 0.01 -> alive but flat at the unigram
# floor for 5000 steps (7.65-7.73) with grad 1.2-1.7.  Same suppressed-gradient
# plateau every unnormalized variant has shown today.
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
go e63_dstd_sgd0001 E63 --lr_max 0.001
go e64_dstd_sgd0003 E64 --lr_max 0.0003
echo "DFF SGD LOW COMPLETE $(date)"
