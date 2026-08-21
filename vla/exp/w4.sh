#!/bin/bash
# Weight decay against the contractivity loss.
#
# Why this lever and not the state clip: --clip_dff bounds the state's magnitude, and that
# turned out to be a symptom. dff_max never exceeded 116 in training and the clip never bound,
# yet the run still collapsed -- harder than the unclipped one (100% runaway at 60K vs 40.5%).
# The drift is in the weights' spectral properties, which no bound on the state can reach.
#
# Weight decay does act on the spectrum, and crucially it is NOT neutered by BatchNorm here.
# ContextCNN's convs are each followed by BatchNorm(affine=False), so decaying them only
# rescales a function BN renormalizes anyway -- the classic "weight decay under BN just changes
# the effective lr" result. But the convs on the FEEDBACK path have no BN after them: --tap
# (1x1 into the register), deep_proj (1x1 up the stack) and decoder.proj. Those are exactly
# the maps that set the recurrence's gain, and decaying them genuinely shrinks it.
#
# Both runs restart from the same 40K weights -- the last checkpoint good on every axis
# (clean 6.257, 1.0% runaway, reach +0.209 at c=64, generation cycle 0.08) -- and run 20K
# steps to 60K, the step where two independent runs have now collapsed (40.5% and 100%).
# Scored at 55K and 60K, since teacher-forced runaway is the only metric that sees this.
cd /proj/devices/vla
run_wd () {
  M=$1; WD=$2
  cp -f checkpoint.pt.wfix236.40k checkpoint.pt.$M
  echo "=== START $M  weight_decay $WD  $(date +%H:%M)"
  conda run --no-capture-output -n dev python vla.py \
    --dataset web --preroll --tokenizer pythia31m \
    --context 16 --n_hidden 256 --kernel 3 \
    --batch 250 --monitor 20 \
    --opt sgd --momentum 0.0 --weight_decay $WD \
    --schedule const --lr_max 0.01 \
    --seed 1 --device cuda \
    --n_layers 7 --depth 7 --clock fixed --clock_base 2.36 \
    --tap --init gaussian --ema 0.5 --accumulate \
    --load checkpoint.pt.$M --save checkpoint.pt.$M \
    --run_steps 20001 --checkpoint 5000 \
    --log log/exp.$M > log/exp.$M.out 2>&1
  for S in 55000 60000; do
    cp -f checkpoint.pt.$M checkpoint.pt.$M.$S 2>/dev/null
  done
  echo "=== score $M @ 60000"
  conda run --no-capture-output -n dev python exp/score.py checkpoint.pt.$M \
      --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null \
      | grep -E "^checkpoint|^$M|^----"
  echo "=== END $M $(date +%H:%M)"
}
run_wd wwd3 0.001
run_wd wwd2 0.01
echo "W4 COMPLETE $(date)"
