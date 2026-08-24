#!/bin/bash
# Incremental head-to-head: c_cummom (--bn_momentum 0) vs e25_3x17 (m=0.1),
# scored in ONE process per step so the scorer seed cancels.  Primary readout is
# runaway% then loss, per the user.  NOTE: e25 already has 0.0% runaway at 5K, so
# there is no headroom there -- any win must appear at 10/15/20K, where the
# staleness argument for cumulative averaging actually bites.
cd /proj/devices/vla
for S in 5000 10000 15000; do
  until [ -f checkpoint/c_cummom.$S.pt ]; do sleep 30; done
  sleep 25
  echo "=== STEP $S  cumulative vs m=0.1  $(date '+%H:%M')"
  conda run --no-capture-output -n dev python exp/score.py \
      checkpoint/c_cummom.$S.pt checkpoint/e25_3x17.$S.pt \
      --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null \
      | grep -E "^c_cummom|^e25"
done
echo "CUMCMP DONE $(date)"
