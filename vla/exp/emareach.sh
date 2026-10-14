#!/bin/bash
# 2026-09-22  EMA WINDOW vs TEMPORAL REACH.  Goal: the LONGEST single-register EMA window
# that still learns, to maximize the DFF state's temporal reach.
#
# WHY NOT HELD-OUT LOSS.  Five arms of the 2/4/8-token sweep (v171/172/173, v178/179) came
# back inside the 0.07-nat run-to-run sigma.  EVAL `clean` is a mean over whole documents and
# most next-token signal is local, so it averages away exactly the long-range behaviour this
# study is about.  PRIMARY READOUT IS exp/reach.py's excess(c): extra nats from having only c
# tokens of RELEVANT context, with warm-up held constant by splicing (not resetting), so a
# slow register cannot score as "long reach" merely by taking longer to leave its seed.
# Held-out EVAL is kept as a secondary check that the arm trained at all.
#
# BASELINE (v178, window 4, step 3.65M, same probe settings as below):
#   full-history clean 5.848
#   c0:+1.273 c1:+0.736 c4:+0.349 c8:+0.249 c16:+0.133 c32:+0.062 c64:+0.030 c128:+0.007
#   i.e. reach ~64-128 tokens: the tail is at the noise floor by c=128.
#
# SPACING is geometric (4,32,128,512 then 8): 2-vs-4-vs-8 is below the noise floor of the
# secondary metric and produced three nulls, so the arms are spread until degradation shows.
#
# MATCHED BUDGET.  Every arm self-terminates at $STEPS via longrun's total_steps, so the
# arms are comparable -- the earlier runs were each stopped by hand at a different step,
# which is what made their "long term trends" unusable.
# --seed is PINNED so every arm draws the SAME initial 10k-document subsample and the same
# weight init; batch composition is still thread-scheduling dependent (see exp/run.sh).
cd /proj/devices/vla
STEPS=${STEPS:-400000}
SEED=${SEED:-20260922}
OUT=log/sweeps/emareach.txt
mkdir -p log/sweeps
echo "=== ema-window reach sweep, $STEPS steps/arm, seed $SEED, $(date)" | tee -a $OUT

for W in 4 32 128 512 8; do
  M=r${W}_fwedu_sub10k_ep20_h512_d32_l1_lr01
  echo "=== ARM window $W ($M) START $(date '+%m-%d %H:%M')" | tee -a $OUT
  exp/longrun.sh $M $STEPS 20 -- \
    --dataset smolfwedu --subsample 10000 --epochs 20 --streaming --no-preroll \
    --init gaussian --no-bn_affine --bn_momentum 0.1 --tokenizer pythia31m \
    --n_hidden 512 --c_context 64 --n_layers 1 --depth 32 --context 16 \
    --batch 250 --monitor 100 --seed $SEED \
    --schedule coswarm --lr_min 0.00001 --lr_period 1000 --lr_max 0.1 \
    --clip_dff 0 --linout --linout_kernel 1 --ema_ladder $W, \
    --gen_score --checkpoint 2000 --gen_interval 2000 \
    --eval_interval 20000 --eval_corpora fwcrawl,smolfwedu,tinytb --eval_docs 100 \
    >> log/longrun.$M.nohup 2>&1

  # PRIMARY READOUT.  Identical probe settings for every arm, including the baseline above:
  # --len/--maxlen 1024 (the default 384 cannot reach past c=192) and a fixed --seed inside
  # reach.py, so the spliced plan is the same text for every model.
  echo "--- ARM window $W reach $(date '+%m-%d %H:%M')" | tee -a $OUT
  conda run --no-capture-output -n dev python exp/reach.py \
      --load checkpoint/$M.pt --corpus web --periods 8,32,128,256 \
      --len 1024 --maxlen 1024 --minlen 256 --docs 500 --rows 500 --device cuda \
      --out log/sweeps/reach.$M.json 2>&1 \
    | grep -vE "^torch|Namespace|^seed" | tee -a $OUT
  echo "--- ARM window $W held-out (last 3 evals)" | tee -a $OUT
  grep '^EVAL' log/exp.$M | awk '{k=$3; a[k]=a[k]" "$7} END{for(k in a)print k,a[k]}' \
    | sort -n | tail -3 | awk '{printf "  step %7d fw %.3f sm %.3f tb %.3f\n",$1,$2,$3,$4}' | tee -a $OUT
done
echo "=== sweep done $(date)" | tee -a $OUT
