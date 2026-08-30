#!/bin/bash
# 2026-08-24 14:25  C = 3x17 baseline + --bn_momentum 0 (cumulative average).
#
# Why this is still worth testing even though 3x17 already shows NO train/eval
# gap at 5K (-0.017, 0% runaway): momentum=0.1 is a ~10-step window, so the
# frozen eval statistics are an average over the last ~10 batches of a state
# distribution that is still moving.  It happens to be adequate at 5K.  The
# failure mode it invites is LATE, not early -- running stats drift with the
# weights, and every eval-mode blowup in this model's history has been
# intermittent and non-monotone.  Cumulative averaging (torch momentum=None)
# removes staleness by construction: the statistics are an average over every
# batch ever seen, so they cannot lag a slowly-moving distribution.
# Cost, if any, is the opposite failure: statistics that are TOO old, dominated
# by the early-training distribution the model has since left behind.
#
# 20K, because e25_3x17 gives a matched m=0.1 ladder at 5/10/15/20K and the
# question is whether the gap OPENS with training, which 5K cannot answer.
# PRIMARY READOUT: train/eval gap and runaway%, not loss (loss deltas at these
# horizons are inside the 0.02-0.035 noise floor measured this morning).
cd /proj/devices/vla

M=c_cummom
echo "=== START $M (20000 steps, 3x17 + --bn_momentum 0) $(date '+%H:%M')"
./exp/watch.sh $M C > /dev/null 2>&1 & WP=$!
./exp/run.sh $M 20000 --bn_momentum 0
sleep 25; kill $WP 2>/dev/null
cp -f checkpoint/$M.pt checkpoint/$M.final.pt 2>/dev/null

echo "=== SCORE: cumulative vs m=0.1, matched at 5/10/15/20K $(date '+%H:%M')"
conda run --no-capture-output -n dev python exp/score.py \
    checkpoint/$M.5000.pt checkpoint/$M.10000.pt checkpoint/$M.15000.pt checkpoint/$M.final.pt \
    checkpoint/e25_3x17.5000.pt checkpoint/e25_3x17.10000.pt \
    checkpoint/e25_3x17.15000.pt checkpoint/e25_3x17.final.pt \
    --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null \
    | grep -E "^checkpoint|^c_cum|^e25|^----" | tee -a PLAN.txt

echo "=== BATCH DEPENDENCE (must be ~0) $(date '+%H:%M')"
conda run --no-capture-output -n dev python exp/batchdep.py checkpoint/$M.final.pt 8 \
    2>/dev/null | tail -3 | tee -a PLAN.txt

echo "=== REACH $M $(date '+%H:%M')"
conda run --no-capture-output -n dev python exp/reach.py --load checkpoint/$M.final.pt \
    --corpus web --docs 800 --rows 500 --minlen 512 --maxlen 1024 --len 1024 \
    --periods 64,512 2>/dev/null | grep -E "full-history|^  P=" | tee -a PLAN.txt
echo "=== END $M $(date '+%H:%M')"
echo "CUM COMPLETE $(date)"
