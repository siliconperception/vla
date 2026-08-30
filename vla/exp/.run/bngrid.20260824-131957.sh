#!/bin/bash
# 2026-08-24 13:05  BN GRID.  With tracking back ON, the remaining BatchNorm2d
# knobs are no longer cosmetic -- they control the TRAIN/EVAL GAP, which is the
# documented failure mode of this model ("the source of every train/held-out
# blowup", vla.py:327).
#
# Mechanism: in train, BN normalizes by the live batch; in eval it uses running
# stats.  momentum sets how fast those track:  running = (1-M)*running + M*batch.
# The 0.1 default is a ~10-STEP window over a state distribution that is still
# moving, so the frozen stats can be stale by construction.
#
# PRIMARY READOUT is NOT loss -- 5K loss deltas are inside the 0.02-0.035 noise
# floor measured this morning and would prove nothing.  It is the TRAIN/EVAL GAP
# (held-out minus training loss at the same checkpoint), which momentum controls
# mechanically and which has historically been LARGE (11x std mismatch).  A knob
# that shrinks the gap is real even if loss moves by noise.
# Secondary: batch-1 vs batch-16 (must stay ~0 now that bn_track is on), and the
# generated text, which today proved able to overturn a scalar-based conclusion.
cd /proj/devices/vla

# D1 was terminated at step 5280 by the user; checkpoint/d1_7x7_50k.5000.pt already
# exists and supplies the momentum=0.1 BASELINE ROW, so no wait and no baseline run.
go () { M=$1; E=$2; shift 2
  echo "=== START $M $* $(date '+%H:%M')"
  ./exp/watch.sh $M $E > /dev/null 2>&1 & WP=$!
  ./exp/run.sh $M 5000 "$@"
  sleep 20; kill $WP 2>/dev/null
  cp -f checkpoint/$M.pt checkpoint/$M.final.pt 2>/dev/null
  echo "=== END $M $(date '+%H:%M')"; }

go bn_m001  M1 --bn_momentum 0.01
go bn_m0001 M2 --bn_momentum 0.001
go bn_mcum  M3 --bn_momentum 0
go bn_eps3  M4 --bn_eps 0.001
go bn_aff   M5 --bn_affine

echo "=== SCORE ALL (one process: the scorer seed cancels across rows) $(date '+%H:%M')"
conda run --no-capture-output -n dev python exp/score.py \
    checkpoint/d1_7x7_50k.5000.pt checkpoint/bn_m001.final.pt \
    checkpoint/bn_m0001.final.pt checkpoint/bn_mcum.final.pt \
    checkpoint/bn_eps3.final.pt checkpoint/bn_aff.final.pt \
    --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null \
    | grep -E "^checkpoint|^d1|^bn_|^----" | tee -a PLAN.txt

echo "=== BATCH DEPENDENCE (all must be ~0) $(date '+%H:%M')"
for C in d1_7x7_50k.5000 bn_m001.final bn_m0001.final bn_mcum.final bn_eps3.final bn_aff.final; do
  echo -n "$C: "
  conda run --no-capture-output -n dev python exp/batchdep.py checkpoint/$C.pt 8 2>/dev/null \
      | tail -1
done | tee -a PLAN.txt
echo "BNGRID COMPLETE $(date)"
