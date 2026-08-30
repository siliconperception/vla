#!/bin/bash
# 2026-08-24 07:something.  HORIZON VALIDATION.
#
# Finding that motivates this: four promotions (lr 0.03, 3x17, --init zero,
# --no-bn_track), each of which won a 20K head-to-head, net to ZERO at 100K.
# e30@100K scored 5.7567 held-out, b5@100K 5.7781 -- a tie, given that the same
# b5 weights scored 5.7528 and 5.7781 on two scorer seeds (0.025 spread).
# So the 20K ranking does not predict the 100K ranking, and roughly a dozen
# decisions in this study rest on the assumption that it does.
#
# B4 (--bn_affine) is the ideal probe, because it does double duty:
#   * it is IDENTICAL to b5 except for the one flag -- same 3x17, same lr 0.03,
#     same --no-bn_track, same --init zero -- and b5's curve is already measured
#     at 20/40/60/80/100K, so no control run is needed;
#   * it was REJECTED last night on a 20K held-out tie (6.1948 vs 6.2227, inside
#     sigma) despite leading on every single training checkpoint, its margin
#     GROWING to 0.069 by 20K.  If a 20K tie turns into an 80K win, the
#     rejection was wrong and so is the horizon that produced it.
#
# Resuming b4's own 20K checkpoint is sound: --bn_affine changes the state_dict
# (adds weight/bias per BatchNorm) so it cannot be toggled onto other weights,
# but b4's checkpoint already carries those tensors.
#
# Pre-registered reading, fixed BEFORE the run so the result cannot be
# rationalized afterwards.  Compare b4 vs b5 held-out at matched 60K and 80K:
#   * b4 ahead by >0.07 at 80K  -> --bn_affine is real, the 20K rejection was a
#     horizon artifact, and every 20K decision needs re-examination.
#   * tie (|d| <= 0.07)         -> rejection STANDS on the simplicity rule
#     (affine adds ~26K params), and 20K was an adequate horizon in this case.
#   * b4 behind                 -> rejection stands outright, 20K was fine.
# Either way the horizon question gets a measured answer instead of an
# assumption, which is the actual deliverable here.
cd /proj/devices/vla

M=h1_affine_long
cp -f checkpoint/b4_affine_nt.final.pt checkpoint/$M.pt
echo "=== START $M (60000 more steps, 20K->80K) $(date '+%H:%M')"
./exp/watch.sh $M H1 > /dev/null 2>&1 & WP=$!
./exp/run.sh $M 60000 --bn_affine --load checkpoint/$M.pt
sleep 25; kill $WP 2>/dev/null
cp -f checkpoint/$M.pt checkpoint/$M.final.pt 2>/dev/null

echo "=== SCORE $M $(date '+%H:%M')"
# score b4-long AND b5 together: same process, same scorer seed, so the
# comparison is not confounded by the 0.025 seed spread measured above.
conda run --no-capture-output -n dev python exp/score.py \
    checkpoint/$M.final.pt checkpoint/b5_long.final.pt \
    --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null \
    | grep -E "^checkpoint|^h1|^b5|^----" | tee -a PLAN.txt
conda run --no-capture-output -n dev python exp/gencheck.py checkpoint/$M.final.pt 80 3 \
    2>/dev/null | tee -a PLAN.txt

echo "=== REACH $M $(date '+%H:%M')"
conda run --no-capture-output -n dev python exp/reach.py --load checkpoint/$M.final.pt \
    --corpus web --docs 800 --rows 500 --minlen 512 --maxlen 1024 --len 1024 \
    --periods 64,512 2>/dev/null | grep -E "full-history|^  P=" | tee -a PLAN.txt
echo "=== END $M $(date '+%H:%M')"
echo "HORIZON COMPLETE $(date)"
