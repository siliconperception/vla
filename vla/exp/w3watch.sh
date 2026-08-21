#!/bin/bash
# Score wclip at the steps where the unclipped run went bad (1.0% -> 40.5% runaway between
# 40K and 60K). Teacher-forced runaway rate is the only metric that detected that; loss,
# grad and dff_std all looked healthy throughout.
cd /proj/devices/vla
for S in 55000 60000; do
  until grep -qa "^TEXT step *$S" log/exp.wclip 2>/dev/null \
        || [ $(pgrep -cf '^python vla.py') -eq 0 ]; do sleep 60; done
  [ $(pgrep -cf '^python vla.py') -eq 0 ] && grep -qa "^TEXT step *$S" log/exp.wclip || true
  cp -f checkpoint.pt.wclip checkpoint.pt.wclip.${S} 2>/dev/null
  echo "=== score @ $S  $(date +%H:%M)"
  conda run --no-capture-output -n dev python exp/score.py checkpoint.pt.wclip.${S} \
      --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null \
      | grep -E "^checkpoint|^wclip|^----"
done
echo "W3WATCH DONE $(date)"
