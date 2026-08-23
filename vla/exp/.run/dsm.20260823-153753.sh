#!/bin/bash
# --dff_norm softmax + --norm none (plain conv2d+relu CNN) + AdamW.
cd /proj/devices/vla
go () { M=$1; E=$2; shift 2
  [ -f exp/done.$M ] && { echo "skip $M"; return; }
  echo "=== START $M $* $(date '+%H:%M')"
  ./exp/watch.sh $M $E > /dev/null 2>&1 & WP=$!
  ./exp/run.sh $M 20000 --norm none --dff_norm softmax "$@"
  sleep 25; kill $WP 2>/dev/null
  cp -f checkpoint/$M.pt checkpoint/$M.final.pt 2>/dev/null
  conda run --no-capture-output -n dev python exp/score.py checkpoint/$M.final.pt \
      --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null \
      | grep -E "^$M" | tee -a PLAN.txt
  touch exp/done.$M; echo "=== END $M $(date '+%H:%M')"; }
go e51_dsm_adamw  E51 --opt adamw --lr_max 0.001 --beta1 0.9 --beta2 0.999
go e52_dsm_adamw3 E52 --opt adamw --lr_max 0.003 --beta1 0.9 --beta2 0.999
go e53_dsm_sgd    E53 --opt sgd   --lr_max 0.03
echo "DFF SOFTMAX COMPLETE $(date)"
