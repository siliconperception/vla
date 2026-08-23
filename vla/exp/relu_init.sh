#!/bin/bash
# E37/E38: --norm none with --init relu.  Written as a SEPARATE script rather than
# an edit to a running one -- bash reads a script incrementally by byte offset, so
# editing nobn.sh while it ran shifted the offsets and it resumed on the old
# E31/E32/E33 lines instead of the inserted E37/E38.  Never edit a running script.
cd /proj/devices/vla
go () { M=$1; E=$2; shift 2
  [ -f exp/done.$M ] && { echo "skip $M"; return; }
  echo "=== START $M $* $(date '+%H:%M')"
  ./exp/watch.sh $M $E > /dev/null 2>&1 & WP=$!
  ./exp/run.sh $M 10000 --norm none "$@"
  sleep 25; kill $WP 2>/dev/null
  cp -f checkpoint/$M.pt checkpoint/$M.final.pt 2>/dev/null
  conda run --no-capture-output -n dev python exp/score.py checkpoint/$M.final.pt \
      --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null \
      | grep -E "^$M" | tee -a PLAN.txt
  touch exp/done.$M; echo "=== END $M $(date '+%H:%M')"; }
go e37_nobn_relu    E37 --opt adamw --lr_max 0.001 --beta1 0.9 --beta2 0.999 --clip_dff 100 --init relu
go e38_nobn_relusgd E38 --opt sgd   --lr_max 0.03 --clip_dff 100 --init relu
echo "RELU INIT COMPLETE $(date)"
