#!/bin/bash
# Restart from the 40K checkpoint with --clip_dff, running to 100K total.
#
# Why: the unclipped run's recurrence progressively lost contractivity. Teacher-forced runaway
# on held-out documents went 1.8% (20K) -> 1.0% (40K) -> 40.5% (60K), the spliced probe went
# 0.2% -> 4.6% -> 82%, and the first failing position moved from 290 to 27. Median full-history
# loss at 60K was 7.506, at the 7.549 unigram floor -- more than half of scored tokens no
# better than a frequency table -- while the CLEAN mean kept improving to 6.183. The clean
# statistic excludes diverged documents by construction, so the model looked like it was
# getting better while becoming unusable. Training telemetry never showed it: grad rose
# steadily and dff_std stayed flat at ~0.60. Only dff_max drifted, 33 -> 63 -> 82 -> 101.
#
# --clip_dff 200 bounds the state after every write, rescaling per layer and per row so the
# encoded pattern is preserved and only the scale is capped. Healthy generation sits at
# dff_max 10-40 and healthy training at 30-100, so 200 leaves normal dynamics untouched and
# only catches the runaway. It demonstrably rescued free-running generation on the degenerate
# 50K checkpoint; this tests whether applying it during training keeps the recurrence
# contractive in the first place.
#
# 40K is the restart point because it is the last checkpoint that was good on every axis:
# clean 6.257, runaway 1.0%, reach +0.209 at c=64, generation cycle 0.08.
cd /proj/devices/vla
conda run --no-capture-output -n dev python vla.py \
  --dataset web --preroll --tokenizer pythia31m \
  --context 16 --n_hidden 256 --kernel 3 \
  --batch 250 --monitor 20 \
  --opt sgd --weight_decay 0.0 --momentum 0.0 \
  --schedule const --lr_max 0.01 \
  --seed 1 --device cuda \
  --n_layers 7 --depth 7 --clock fixed --clock_base 2.36 \
  --tap --init gaussian --ema 0.5 --accumulate \
  --clip_dff 200 \
  --load checkpoint.pt.wclip --save checkpoint.pt.wclip \
  --run_steps 60001 --checkpoint 5000 \
  --log log/exp.wclip > log/exp.wclip.out 2>&1
echo "W3 COMPLETE rc=$? $(date)"
