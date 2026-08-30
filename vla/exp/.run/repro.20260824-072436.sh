#!/bin/bash
# 2026-08-24 07:30  B6 = B5 RERUN FROM SCRATCH, DIFFERENT SEED.
#
# B5 is now the baseline.  Before building anything else on top of it, measure
# how much of its 100K result is reproducible and how much is one roll of the
# dice.  Everything in this study is decided by comparing two runs, so the
# run-to-run sigma AT 100K is the scale that every future decision has to beat,
# and it has never been measured at that length -- only ~0.07 at short horizons.
#
# NOTE what this varies.  --seed controls weight init, but the data worker is
# NOT seeded (see PLAN.txt), so a rerun differs in initialization AND in the
# order/content of examples.  That is the right thing to measure: it is total
# run-to-run variance, the quantity that matters when ranking two configs.
#
# B5 reached 100K by resuming a 20K checkpoint (20K + 80K).  B6 runs 100K in
# one shot.  If the two land far apart, "resumed vs from-scratch" is a
# confound to check before blaming the seed.
#
# Reference numbers to beat/compare (b5_long.final, 100K):
#   held-out clean 5.7528 (night3 seed) / 5.7781 (rescored) -- 0.025 apart
#   training loss @20/40/60/80/100K: 6.1523 5.8963 5.7810 5.6966 5.6410
#   reach mean excess P=512 +0.0948, c511 -0.068
cd /proj/devices/vla

M=b6_seed2
echo "=== START $M (100000 steps, from scratch, --seed 2) $(date '+%H:%M')"
./exp/watch.sh $M B6 > /dev/null 2>&1 & WP=$!
./exp/run.sh $M 100000 --seed 2
sleep 25; kill $WP 2>/dev/null
cp -f checkpoint/$M.pt checkpoint/$M.final.pt 2>/dev/null

echo "=== SCORE $M vs b5 (one process, so the scorer seed cancels) $(date '+%H:%M')"
conda run --no-capture-output -n dev python exp/score.py \
    checkpoint/$M.final.pt checkpoint/b5_long.final.pt \
    --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null \
    | grep -E "^checkpoint|^b5|^b6|^----" | tee -a PLAN.txt
conda run --no-capture-output -n dev python exp/gencheck.py checkpoint/$M.final.pt 80 3 \
    2>/dev/null | tee -a PLAN.txt

echo "=== REACH $M $(date '+%H:%M')"
conda run --no-capture-output -n dev python exp/reach.py --load checkpoint/$M.final.pt \
    --corpus web --docs 800 --rows 500 --minlen 512 --maxlen 1024 --len 1024 \
    --periods 64,512 2>/dev/null | grep -E "full-history|^  P=" | tee -a PLAN.txt
echo "=== END $M $(date '+%H:%M')"
echo "REPRO COMPLETE $(date)"
