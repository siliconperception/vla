#!/bin/bash
# GroupNorm at the promoted baseline (3x17, lr 0.03, --init zero, --ema 0.5,
# --accumulate).  Reference to beat, BatchNorm at the same config:
#   train@10K 6.372   train@20K 6.145   held-out 6.2203 @20K   0.0% runaway
# E39 is the direct swap.  E40/E41 vary the group count, which is GroupNorm's
# only free parameter: 1 = LayerNorm over channels, 256 = InstanceNorm.
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

go e39_gn32  E39 --norm_groups 32
go e40_gn1   E40 --norm_groups 1
go e41_gn256 E41 --norm_groups 256
echo "GROUPNORM COMPLETE $(date)"
