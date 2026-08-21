#!/bin/bash
# Re-score every stashed web checkpoint on the SAME held-out set, twice with different probe
# seeds. Runaway rate turned out to be non-monotone -- wnotap read 0.2% / 46.2% / 0.8% at
# 20K/40K/60K -- so single measurements do not establish a trend, and it is not yet known
# whether the probe itself is noisy (the --init seed and doc order vary) or the models really
# fluctuate in and out of marginal stability. Two seeds per checkpoint separates those.
cd /proj/devices/vla
for f in checkpoint.pt.wexp \
         checkpoint.pt.wfix236.20k checkpoint.pt.wfix236.40k checkpoint.pt.wfix236.50k \
         checkpoint.pt.wfix236.60k checkpoint.pt.wfix236.65k \
         checkpoint.pt.wclip.55000 checkpoint.pt.wclip.60000 \
         checkpoint.pt.wnotap.20000 checkpoint.pt.wnotap.40000 checkpoint.pt.wnotap.60000; do
  [ -f "$f" ] || continue
  for SEED in 1234 777; do
    conda run --no-capture-output -n dev python exp/score.py "$f" --corpus web --docs 400 \
        --minlen 512 --maxlen 1024 --seed $SEED 2>/dev/null \
        | grep -E "^[a-z]" | sed "s/^/seed$SEED  /"
  done
done
echo "RESCORE DONE $(date)"
