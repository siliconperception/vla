#!/bin/bash
# OVERNIGHT 2026-08-23 21:30 -> ~09:00.  Fixed plan, no decisions required.
# Baseline: 3x17, lr 0.03, --init zero, --ema 0.5, --accumulate, --no-bn_track.
# B2 (--bn_affine) is already running against the PREVIOUS baseline (tracked BN)
# and finishes ~22:15; this chain starts after it.
#
# Priorities, in order:
#  1. Re-test --bn_affine ON the promoted baseline.  B2 measures it against the
#     old one, and the two plausibly interact -- affine parameters can partly
#     substitute for what running statistics were providing.  A promotion needs
#     the comparison against the current baseline.
#  2. Take the promoted config LONG.  Every promotion to date rests on a 20K
#     comparison; the best model in the study (5.6617 held-out) is 140K of the
#     PREVIOUS baseline.  The promoted config has never run past 20K, so the
#     deliverable weights and the recommended config are still different models.
#  3. Reach probe on the long run.  Reach has not been measured since baseline
#     change #2 (lr 0.03) and is a GATE, not an objective: mean excess must stay
#     above ~+0.04.  Reference: e30 +0.1286, wnotap +0.0756, wexp +0.0023.
#
# --bn_momentum 0.01 (the old B3) is DROPPED: it was the conservative fallback
# for stabilizing running statistics, and --no-bn_track removes them entirely.
cd /proj/devices/vla
until grep -q "=== END b2_affine" log/bn.log 2>/dev/null; do sleep 60; done
sleep 20

go () { M=$1; E=$2; S=$3; shift 3
  [ -f exp/done.$M ] && { echo "skip $M"; return; }
  echo "=== START $M ($S steps) $* $(date '+%H:%M')"
  ./exp/watch.sh $M $E > /dev/null 2>&1 & WP=$!
  ./exp/run.sh $M $S "$@"
  sleep 25; kill $WP 2>/dev/null
  cp -f checkpoint/$M.pt checkpoint/$M.final.pt 2>/dev/null
  echo "=== SCORE $M $(date '+%H:%M')"
  conda run --no-capture-output -n dev python exp/score.py checkpoint/$M.final.pt \
      --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null \
      | grep -E "^checkpoint|^$M|^----" | tee -a PLAN.txt
  conda run --no-capture-output -n dev python exp/gencheck.py checkpoint/$M.final.pt 80 3 \
      2>/dev/null | tee -a PLAN.txt
  touch exp/done.$M
  echo "=== END $M $(date '+%H:%M')"; }

# 1. --bn_affine on the PROMOTED baseline (2 h)
go b4_affine_nt B4 20000 --bn_affine

# 2. promoted baseline to 100K, resuming from B1's 20K weights (~7 h)
cp -f checkpoint/BASELINE_notrack_20k.pt checkpoint/b5_long.pt
go b5_long B5 80000 --load checkpoint/b5_long.pt

# 3. reach on the long run -- the GATE
echo "=== REACH b5_long $(date '+%H:%M')"
conda run --no-capture-output -n dev python exp/reach.py --load checkpoint/b5_long.final.pt \
    --corpus web --docs 800 --rows 500 --minlen 512 --maxlen 1024 --len 1024 \
    --periods 64,512 2>/dev/null | grep -E "full-history|^  P=" | tee -a PLAN.txt
echo "NIGHT3 COMPLETE $(date)"
