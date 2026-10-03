#!/bin/bash
# Response-surface batch 1 (v250-v255): (linout_gain g, register gain r = g * dff_write_scale)
# around/below v245 (g=2.83, r=0.5). 10K steps each -- the 5-10K training-loss bin ranks runs
# the same as 15-20K -- same seed and data as v226-v249. s = r / g.
set -u
cd /proj/devices/vla
STOP=10000
COMMON="--dataset smolfwedu --shards 1 --subsample 100000 --no-shuffle --seed 20261002 --workers 1
 --no-preroll --init gaussian --no-bn_affine --bn_momentum 0.1 --tokenizer pythia31m
 --n_hidden 4096 --c_context 256 --n_layers 1 --depth 16 --context 8 --batch 250 --monitor 100
 --opt sgd --schedule coswarm --lr_min 0.00001 --lr_period 2000 --lr_max 0.03 --clip_dff 0
 --linout --linout_kernel 1 --linin --ema 1 --ctx_ema 4,16 --gen_score --checkpoint 2000
 --gen_interval 2000 --eval_interval 20000 --eval_corpora smolfwedu,fineweb,tinytb --eval_docs 100
 --ctx_mix none"
Q=log/queue_b1.log
run () {
  local M=$1; shift
  setsid ./exp/launch.sh exp/longrun.sh "$M" 40000000 40 -- $COMMON "$@" >> "log/longrun.$M.nohup" 2>&1 &
  local PG=$!
  echo $PG > "log/longrun.$M.driverpid"
  echo "queue: $M started (pgid $PG) $(date)" >> $Q
  # stop on the STEP line (no EVAL at 10K), then wait for the step-STOP checkpoint
  until grep -qE "^STEP +$STOP " "log/exp.$M" 2>/dev/null; do
    sleep 30
    kill -0 $PG 2>/dev/null || { echo "queue: $M driver EXITED before step $STOP $(date)" >> $Q; break; }
  done
  for i in $(seq 30); do
    conda run --no-capture-output -n dev python - "$M" "$STOP" <<'PY' 2>/dev/null && break
import sys, torch
s = torch.load(f'checkpoint/{sys.argv[1]}.pt', map_location='cpu', weights_only=False).get('step', 0)
sys.exit(0 if s >= int(sys.argv[2]) else 1)
PY
    sleep 15
  done
  kill -- -$PG 2>/dev/null; sleep 10; kill -9 -- -$PG 2>/dev/null
  for i in $(seq 30); do pgrep -f "vla.py.*$M" >/dev/null || break; sleep 2; done
  echo "queue: $M stopped at step $(grep -E '^STEP' "log/exp.$M" | tail -1 | awk '{print $2}'), trainers left: $(pgrep -fc "vla.py.*$M") $(date)" >> $Q
}
run v250_smolfwedu_sub100k_det_h4096_linin_ctx416_single_g283_r0125_10K --linout_gain 2.82842712 --dff_write_scale 0.04419417
run v251_smolfwedu_sub100k_det_h4096_linin_ctx416_single_g283_r00625_10K --linout_gain 2.82842712 --dff_write_scale 0.02209709
run v252_smolfwedu_sub100k_det_h4096_linin_ctx416_single_g4_r025_10K     --linout_gain 4          --dff_write_scale 0.0625
run v253_smolfwedu_sub100k_det_h4096_linin_ctx416_single_g4_r0125_10K    --linout_gain 4          --dff_write_scale 0.03125
run v254_smolfwedu_sub100k_det_h4096_linin_ctx416_single_g566_r025_10K   --linout_gain 5.65685425 --dff_write_scale 0.04419417
run v255_smolfwedu_sub100k_det_h4096_linin_ctx416_single_g566_r0125_10K  --linout_gain 5.65685425 --dff_write_scale 0.02209709
echo "queue: ALL DONE $(date)" >> $Q
