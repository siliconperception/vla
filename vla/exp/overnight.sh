#!/bin/bash
# Unattended overnight queue, 2026-08-21 ~21:40 -> ~05:30.
# Baseline: wnotap + --init zero + --accumulate (exp/run.sh).  Reference numbers
# at 20K: train ~6.373, held-out 6.3686 @30K, gen cycle 0.08.
# Chosen for COVERAGE (section 6c): four dimensions with zero or weak data on web.
# Each run is ONE change from the baseline, gets a watcher (5K reports into
# PLAN.txt) and a held-out score on its final checkpoint.
cd /proj/devices/vla

go () {   # go <mnem> <expid> <steps> <args...>
  M=$1; E=$2; S=$3; shift 3
  [ -f exp/done.$M ] && { echo "skip $M"; return; }
  echo "=== START $M ($S steps) $* $(date '+%H:%M')"
  ./exp/watch.sh $M $E > /dev/null 2>&1 &
  WP=$!
  ./exp/run.sh $M $S "$@"
  sleep 25; kill $WP 2>/dev/null
  cp -f checkpoint/$M.pt checkpoint/$M.final.pt 2>/dev/null
  echo "=== SCORE $M $(date '+%H:%M')"
  conda run --no-capture-output -n dev python exp/score.py checkpoint/$M.final.pt \
      --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null \
      | grep -E "^checkpoint|^$M|^----" | tee -a PLAN.txt
  conda run --no-capture-output -n dev python exp/gencheck.py checkpoint/$M.final.pt 80 3 \
      2>/dev/null | tee -a PLAN.txt
  touch exp/done.$M
  echo "=== END $M $(date '+%H:%M')"
}

# E19  lr validation.  0.01 came from a 200-STEP grid; every comparison in this
#      study inherits it.  If 0.02 is clearly better the frame is wrong.
go e19_lr02   E19 20000 --lr_max 0.02

# E20  shape, low end.  3 layers x depth 17, clock_base 13.15 so p_max stays 173
#      (ladder 1,13,173).  Three timescales, 17 convs of compute between them.
go e20_3x17   E20 20000 --n_layers 3  --depth 17 --clock_base 13.15

# E21  shape, high end.  17 x 3, clock_base 1.38 (ladder 1,1,2,3,4,5,7,10,13,18,
#      25,35,48,66,91,125,173).  Sixteen distinct timescales, 3 convs each --
#      fewer than the 15 needed to mix a 16-wide grid within one layer, so each
#      layer is spatially local and mixing happens only through the stack.
go e21_17x3   E21 20000 --n_layers 17 --depth 3  --clock_base 1.38

# E22  batch.  TOKEN-MATCHED, not step-matched: 10K steps at batch 500 is the
#      same 5.0M tokens as 20K at batch 250.  Compare on the token axis.
go e22_batch500 E22 10000 --batch 500

echo "OVERNIGHT COMPLETE $(date)"
