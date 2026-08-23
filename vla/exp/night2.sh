#!/bin/bash
# Overnight 2026-08-22 -> 08-23.  E29 (3x17 to 40K) is already running; when it
# finishes and scores, extend the best configuration far past anything tested so
# far.  Rationale: every promotion to date rests on a 20-40K comparison, and the
# eventual target is ~1B tokens.  The single most valuable unknown is whether the
# promoted config keeps descending, so spend the night on depth of horizon rather
# than breadth of options.
cd /proj/devices/vla
until [ -f exp/done.e29_3x17_40k ] || grep -q "^e29_3x17_40k" PLAN.txt; do sleep 60; done
sleep 30

# E30: continue 3x17 from 40K to 120K.  ~7.5 h at 3.06 steps/s.
./exp/watch.sh e30_3x17_120k E30 > /dev/null 2>&1 &
WP=$!
./exp/run.sh e30_3x17_120k 80000 --load checkpoint/e29_3x17_40k.pt
sleep 25; kill $WP 2>/dev/null
cp -f checkpoint/e30_3x17_120k.pt checkpoint/e30_3x17_120k.final.pt

echo "=== SCORE e30 @120K $(date '+%H:%M')"
conda run --no-capture-output -n dev python exp/score.py checkpoint/e30_3x17_120k.final.pt \
    --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null \
    | grep -E "^checkpoint|^e30|^----" | tee -a PLAN.txt
conda run --no-capture-output -n dev python exp/gencheck.py checkpoint/e30_3x17_120k.final.pt 80 3 \
    2>/dev/null | tee -a PLAN.txt
echo "=== REACH e30 @120K"
conda run --no-capture-output -n dev python exp/reach.py --load checkpoint/e30_3x17_120k.final.pt \
    --corpus web --docs 800 --rows 500 --minlen 512 --maxlen 1024 --len 1024 \
    --periods 64,512 2>/dev/null | grep -E "full-history|^  P=" | tee -a PLAN.txt
touch exp/done.e30_3x17_120k
echo "NIGHT2 COMPLETE $(date)"
