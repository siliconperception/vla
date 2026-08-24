#!/bin/bash
# DFF state trajectory constrained on the READ path; prediction path is conv2d +
# ReLU only.  Register holds raw sparse ReLU output; --init relu matches that
# shape (relu(randn), non-negative, ~50% zeros) instead of seeding zeros.
cd /proj/devices/vla
go () { M=$1; E=$2; shift 2
  [ -f exp/done.$M ] && { echo "skip $M"; return; }
  echo "=== START $M $* $(date '+%H:%M')"
  ./exp/watch.sh $M $E > /dev/null 2>&1 & WP=$!
  ./exp/run.sh $M 20000 --norm none --init relu "$@"
  sleep 25; kill $WP 2>/dev/null
  cp -f checkpoint/$M.pt checkpoint/$M.final.pt 2>/dev/null
  conda run --no-capture-output -n dev python exp/score.py checkpoint/$M.final.pt \
      --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null \
      | grep -E "^$M" | tee -a PLAN.txt
  touch exp/done.$M; echo "=== END $M $(date '+%H:%M')"; }
go e57_dstd_r_adamw  E57 --dff_norm std     --opt adamw --lr_max 0.001 --beta1 0.9 --beta2 0.999
go e58_dstd_r_adamw3 E58 --dff_norm std     --opt adamw --lr_max 0.003 --beta1 0.9 --beta2 0.999
go e59_dsm_r_adamw   E59 --dff_norm softmax --opt adamw --lr_max 0.001 --beta1 0.9 --beta2 0.999
go e60_dstd_r_sgd    E60 --dff_norm std     --opt sgd   --lr_max 0.03
echo "DFF READ-PATH COMPLETE $(date)"
