#!/bin/bash
# Reach on c1_7x7 at its 10K checkpoint, WITH the matched-step control.
# Comparing 7x7 at 10K against b5 at 100K would confound shape with training
# time, so b1_notrack.10000 (the 3x17 baseline lineage at the same step) is
# probed in the same conditions.  References at 100K+: b5 +0.0948, e30 +0.1286,
# wnotap +0.0756, wexp +0.0023 -- all far more trained, so expect lower numbers
# here from BOTH runs; what matters is 7x7 vs 3x17 at the same step.
cd /proj/devices/vla
until [ -f checkpoint/c1_7x7.10000.pt ]; do sleep 20; done
sleep 30                                  # let the stash finish writing
until [ -z "$(pgrep -f '^python exp/score.py' | head -1)" ]; do sleep 30; done
echo "=== REACH c1_7x7 @10K (7x7) $(date '+%H:%M')"
conda run --no-capture-output -n dev python -u exp/reach.py --load checkpoint/c1_7x7.10000.pt \
    --corpus web --docs 800 --rows 500 --minlen 512 --maxlen 1024 --len 1024 \
    --periods 64,512 2>/dev/null | grep -E "full-history|^  P=" | tee -a PLAN.txt
echo "=== REACH b1_notrack @10K (3x17 control) $(date '+%H:%M')"
conda run --no-capture-output -n dev python -u exp/reach.py --load checkpoint/b1_notrack.10000.pt \
    --corpus web --docs 800 --rows 500 --minlen 512 --maxlen 1024 --len 1024 \
    --periods 64,512 2>/dev/null | grep -E "full-history|^  P=" | tee -a PLAN.txt
echo "REACH_C1 COMPLETE $(date)"
