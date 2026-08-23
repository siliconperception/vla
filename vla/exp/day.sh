#!/bin/bash
# Fallback driver for the 2026-08-22 day plan (PLAN.txt section 12).
# Fully specified so it runs without supervision; the interactive session may
# override or reorder, but if it stops, this still makes forward progress.
cd /proj/devices/vla
BEST_LR=${1:-0.02}   # 0.04 is unstable held-out; see E23

go () {   # go <mnem> <expid> <steps> <args...>
  M=$1; E=$2; S=$3; shift 3
  [ -f exp/done.$M ] && { echo "skip $M"; return; }
  echo "=== START $M ($S steps) $* $(date '+%H:%M')"
  ./exp/watch.sh $M $E > /dev/null 2>&1 &
  WP=$!
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
  echo "=== END $M $(date '+%H:%M')"
}

# lr 0.08 CANCELLED before running.  lr 0.04 (E23) had the best TRAINING loss of
# any run in the study (6.1329 @20K) and a held-out score of 9.8150 with 11.8%
# runaway -- worse than the 7.549 unigram floor.  The doubling ladder crossed the
# stability edge between 0.02 and 0.04, and the training curve concealed it
# completely.  lr 0.02 is the winner (held-out 6.3681, 0.0% runaway).
# Probe the interval instead of continuing to double.
go e24_lr03   E24 20000 --lr_max 0.03
go e25_3x17   E25 20000 --lr_max $BEST_LR --n_layers 3 --depth 17 --clock_base 13.15
go e26_ema25  E26 20000 --lr_max $BEST_LR --ema 0.25
go e27_exp    E27 20000 --lr_max $BEST_LR --clock exp
go e28_long   E28 40000 --lr_max $BEST_LR
echo "=== reach probe on the long run"
conda run --no-capture-output -n dev python exp/reach.py --load checkpoint/e28_long.final.pt \
    --corpus web --docs 800 --rows 500 --minlen 512 --maxlen 1024 --len 1024 \
    --periods 64,512 2>/dev/null | grep -E "full-history|^  P=" | tee -a PLAN.txt
echo "DAY COMPLETE $(date)"
