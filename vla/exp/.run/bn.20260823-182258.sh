#!/bin/bash
# BatchNorm option study at the promoted baseline (3x17, lr 0.03, --init zero,
# --ema 0.5, --accumulate, --norm batch).  Reference: train@20K 6.145,
# held-out 6.2203, 0.0% runaway, gen cycle 0.09.
cd /proj/devices/vla
go () { M=$1; E=$2; shift 2
  [ -f exp/done.$M ] && { echo "skip $M"; return; }
  echo "=== START $M $* $(date '+%H:%M')"
  ./exp/watch.sh $M $E > /dev/null 2>&1 & WP=$!
  ./exp/run.sh $M 20000 "$@"
  sleep 25; kill $WP 2>/dev/null
  cp -f checkpoint/$M.pt checkpoint/$M.final.pt 2>/dev/null
  conda run --no-capture-output -n dev python exp/score.py checkpoint/$M.final.pt \
      --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null \
      | grep -E "^$M" | tee -a PLAN.txt
  conda run --no-capture-output -n dev python exp/gencheck.py checkpoint/$M.final.pt 80 3 \
      2>/dev/null | tee -a PLAN.txt
  touch exp/done.$M; echo "=== END $M $(date '+%H:%M')"; }
go b1_notrack  B1 --no-bn_track
go b2_affine   B2 --bn_affine
go b3_mom001   B3 --bn_momentum 0.01
echo "BN STUDY COMPLETE $(date)"
