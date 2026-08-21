#!/bin/bash
# Score wnotap at milestones. Runaway rate is the metric -- loss, grad and dff_std all looked
# healthy through both previous collapses, only the held-out runaway rate saw them.
cd /proj/devices/vla
for S in 20000 40000 60000 80000 100000; do
  until grep -qa "^TEXT step *$S" log/exp.wnotap 2>/dev/null \
        || [ $(pgrep -cf '^python vla.py') -eq 0 ]; do sleep 60; done
  grep -qa "^TEXT step *$S" log/exp.wnotap 2>/dev/null || { echo "trainer gone before $S"; break; }
  cp -f checkpoint.pt.wnotap checkpoint.pt.wnotap.$S 2>/dev/null
  echo "=== wnotap score @ $S  $(date +%H:%M)"
  conda run --no-capture-output -n dev python exp/score.py checkpoint.pt.wnotap.$S \
      --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null \
      | grep -E "^checkpoint|^wnotap|^----"
  conda run --no-capture-output -n dev python exp/gencheck.py checkpoint.pt.wnotap.$S 80 3 2>/dev/null
done
echo "W6SCORE DONE $(date)"
