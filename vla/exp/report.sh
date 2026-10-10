#!/bin/bash
# usage: report.sh <mnemonic> <expid>   -- one 5K-checkpoint report, appended to PLAN.txt
M=$1; E=$2; L=log/exp.$M
cd /proj/devices/vla
S=$(grep -a '^TEXT step' $L | tail -1 | awk '{print $3}')
{
echo ""
echo "--------------------------------------------------------------------------------"
echo "$E  $M  step $S   $(date '+%Y-%m-%d %H:%M')"
echo "--------------------------------------------------------------------------------"
# The seed is no longer constant: exp/run.sh stopped passing --seed 1 on 2026-08-24, so
# each run draws its own and a report that omits it cannot be paired against another later.
# Read from the log's ARGS line, which vla.py writes AFTER resolving a None seed to a real one.
echo "  seed $(grep -ao 'seed=[0-9]*' $L | head -1 | cut -d= -f2)   dataset $(grep -ao "dataset='[a-z0-9_]*'" $L | head -1 | cut -d\' -f2)"
echo "loss/grad/state:"
grep '^STEP' $L | awk -v s=$S '$2%5000==0 {printf "  step %6d  loss %7.4f  grad %6.3f  dff_std %6.3f  dff_max %8.1f\n",$2,$7,$9,$15,$17}'
grep '^STEP' $L | tail -10 | awk '{t+=$7;n++} END {printf "  mean(last10) %.4f   tokens %.2f M   (unigram floor 7.549)\n",t/n,'"$S"'*250/1e6}'
# in-training held-out eval (--eval_interval), which vla.py now writes into the log at the
# checkpoint cadence. Printed here so a PLAN.txt row carries its own held-out number instead
# of waiting for someone to run exp/score.py against the stashed weights afterwards.
# NOTE the corpus: this is a held-out split of what the run TRAINED on (--dataset), so for a
# Phase 2 non-web run it measures FIT and is NOT comparable to the web numbers in PLAN.txt's
# reference table. Score with exp/score.py --corpus web for that comparison.
echo "held-out eval (split of --dataset; see note in report.sh before comparing):"
grep -a '^EVAL step' $L | tail -3 | sed 's/^/  /'
# The crossing thresholds and the "baseline" column are BOTH web numbers: the ladder is
# keyed to openwebtext's 7.549 unigram floor and compared against the wnotap web run. On a
# non-web dataset those rows are cross-corpus and mean nothing -- pile's unigram floor is
# 7.947, so "L<7.549" is a much harder crossing there than the label suggests, and beating
# the web baseline's step count is not evidence of anything.
_DS=$(grep -ao "dataset='[a-z0-9_]*'" $L | head -1 | cut -d\' -f2)
if [ "$_DS" != "web" ]; then
  echo "token efficiency (sustained crossings)  [!! thresholds and baseline are WEB numbers;"
  echo "     dataset is $_DS -- these rows are CROSS-CORPUS and are not a like-for-like read]:"
else
  echo "token efficiency (sustained crossings):"
fi
conda run --no-capture-output -n dev python - "$L" <<'PY' 2>/dev/null
import sys, numpy as np
S=[];L=[]
for ln in open(sys.argv[1]):
    f=ln.split()
    if f and f[0]=='STEP': S.append(int(f[1])); L.append(float(f[6]))
S=np.array(S); L=np.array(L)
if len(L)>=10:
    m=np.convolve(L,np.ones(10)/10,mode='valid'); ms=S[9:]
    base={7.549:3980,7.0:5940,6.5:15680,6.3:30120,6.1:49700,5.9:84980,5.8:99980}
    for t in (7.549,7.0,6.5,6.3,6.1,5.9,5.8):
        idx=[i for i in range(len(m)) if (m[i:]<t).all()]
        if idx:
            d=ms[idx[0]]-base[t]
            print(f'  L<{t:5.3f}  step {ms[idx[0]]:6d}  {ms[idx[0]]*250/1e6:6.2f} M tok   baseline {base[t]:6d}  ({d:+d})')
PY
echo "free-running generation (3 samples; cycle>0.6 degenerate, healthy 0.08-0.11):"
cp -f checkpoint/$M.pt checkpoint/.$M._gc 2>/dev/null
conda run --no-capture-output -n dev python exp/gencheck.py checkpoint/.$M._gc 80 3 2>/dev/null
# --- vla.py --generate, verbatim, for SUBJECTIVE analysis at every checkpoint ---
# gencheck.py returns only scalar health (cycle/uniq); those numbers cannot tell a
# fluent sentence from well-spaced noise.  The text itself has to be read, and it has
# to be preserved here so the reading can be redone later and compared across steps.
# Batch 1, which is what a deployed generator is -- valid now that bn_track is back on
# (with --no-bn_track this path silently measured a different function; see 12:40).
echo "  generated text (vla.py --generate, batch 1, seeds 11/12/13):"
for GS in 11 12 13; do
  echo "  --- seed $GS:"
  conda run --no-capture-output -n dev python vla.py --generate \
      --load checkpoint/.$M._gc --n 100 --seed $GS --device cuda 2>/dev/null \
      | grep -a "<STX>\|^ *[A-Za-z]" | tail -1 | fold -s -w 100 | sed 's/^/    /'
done
rm -f checkpoint/.$M._gc
} | LC_ALL=C tr -c '\11\12\15\40-\176' '?' >> PLAN.txt
# generated samples can contain any token in the vocabulary, including non-ASCII;
# PLAN.txt is specified as ASCII, so non-printables are mapped to '?' on the way in.
