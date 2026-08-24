#!/bin/bash
# 2026-08-24 13:00  D1 = the new baseline (7x7 + e30) taken to 50K.
#
# Purpose is NOT to beat a number.  It is to establish that the new baseline runs
# CLEAN over a long horizon and to get enough of a curve to extrapolate to 1B
# training tokens (= 4M steps at 250 tokens/step, 80x this run).  If it looks
# promising the model FREEZES here and the work moves to data (the pile, streamed).
#
# Every 5K checkpoint now also emits vla.py --generate samples at batch 1 into
# PLAN.txt (exp/report.sh), because scalar health numbers cannot tell fluent text
# from well-spaced noise -- a distinction that mattered enormously today: the
# --no-bn_track model looked bigram-level in generation while scoring 5.75 at
# batch 400.
cd /proj/devices/vla

M=d1_7x7_50k
echo "=== START $M (50000 steps, NEW BASELINE 7x7 + e30) $(date '+%H:%M')"
./exp/watch.sh $M D1 > /dev/null 2>&1 & WP=$!
./exp/run.sh $M 50000
sleep 25; kill $WP 2>/dev/null
cp -f checkpoint/$M.pt checkpoint/$M.final.pt 2>/dev/null

echo "=== SCORE $M vs e30@140K (one process, scorer seed cancels) $(date '+%H:%M')"
conda run --no-capture-output -n dev python exp/score.py \
    checkpoint/$M.final.pt checkpoint/e30_3x17_120k.final.pt \
    --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null \
    | grep -E "^checkpoint|^d1|^e30|^----" | tee -a PLAN.txt

echo "=== BATCH DEPENDENCE (must be ~0; bn_track is back on) $(date '+%H:%M')"
conda run --no-capture-output -n dev python exp/batchdep.py checkpoint/$M.final.pt 16 \
    2>/dev/null | tail -3 | tee -a PLAN.txt

echo "=== REACH $M $(date '+%H:%M')"
conda run --no-capture-output -n dev python exp/reach.py --load checkpoint/$M.final.pt \
    --corpus web --docs 800 --rows 500 --minlen 512 --maxlen 1024 --len 1024 \
    --periods 64,512 2>/dev/null | grep -E "full-history|^  P=" | tee -a PLAN.txt
echo "=== END $M $(date '+%H:%M')"
echo "D1 COMPLETE $(date)"
