#!/bin/bash
# Chain: when E18's 30K run finishes, score it, then extend to 50K.
# Extended because E18 settles far later than any other run: its state swung
# dff_max 49 -> 388 -> 8.3 and dff_zeros only plateaued (~0.28) around 20K, where
# the other runs were structurally settled by 10K.  Its usable comparison window
# starts where theirs ended, so 30K is early for this configuration specifically.
cd /proj/devices/vla
until grep -q "RUN_DONE e18_noaccum" log/exp.e18_noaccum.out 2>/dev/null; do sleep 30; done
sleep 25
cp -f checkpoint/e18_noaccum.pt checkpoint/e18_noaccum.30000.pt
echo "=== held-out score e18 @30K  $(date +%H:%M)"
conda run --no-capture-output -n dev python exp/score.py checkpoint/e18_noaccum.30000.pt \
    --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null \
    | grep -E "^checkpoint|^e18|^----"
echo "=== baseline for comparison: e17_init0_ext @30K clean 6.3686 runaway 0.0%"
echo "=== extending E18 to 50K  $(date +%H:%M)"
./exp/run.sh e18_noaccum_ext 20000 --no-accumulate --load checkpoint/e18_noaccum.pt
