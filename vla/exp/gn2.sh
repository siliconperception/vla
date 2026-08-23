#!/bin/bash
# GroupNorm continued, reordered (user, 2026-08-23): lr FIRST, group count after.
# lr 0.03 was tuned for BatchNorm.  GroupNorm normalizes per-sample rather than
# across the 250-row batch, so its gradient noise differs and the lr need not
# transfer -- the same argument that required re-running 3x17 at the corrected lr.
# If GN wants a different lr then the group-count sweep at 0.03 is measured at the
# wrong point, so it goes after.
cd /proj/devices/vla
go () { M=$1; E=$2; shift 2
  [ -f exp/done.$M ] && { echo "skip $M"; return; }
  echo "=== START $M $* $(date '+%H:%M')"
  ./exp/watch.sh $M $E > /dev/null 2>&1 & WP=$!
  ./exp/run.sh $M 20000 --norm group "$@"
  sleep 25; kill $WP 2>/dev/null
  cp -f checkpoint/$M.pt checkpoint/$M.final.pt 2>/dev/null
  conda run --no-capture-output -n dev python exp/score.py checkpoint/$M.final.pt \
      --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null \
      | grep -E "^$M" | tee -a PLAN.txt
  conda run --no-capture-output -n dev python exp/gencheck.py checkpoint/$M.final.pt 80 3 \
      2>/dev/null | tee -a PLAN.txt
  touch exp/done.$M; echo "=== END $M $(date '+%H:%M')"; }

go e42_gn32_lr01 E42 --norm_groups 32 --lr_max 0.01
go e40_gn1       E40 --norm_groups 1
go e41_gn256     E41 --norm_groups 256
echo "GROUPNORM2 COMPLETE $(date)"
