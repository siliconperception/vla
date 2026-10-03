#!/bin/bash
# Response-surface batch 3 (v260-v262): can g go to 1 (plain linout init) with the decoder lr
# doing the work, and where does the decoder lr multiplier peak. 10K steps each, same seed and
# data as v226-v259. s = r / g.
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
Q=log/queue_b3.log
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
run v260_smolfwedu_sub100k_det_h4096_linin_ctx416_single_g1_r008_dec16_10K   --linout_gain 1          --dff_write_scale 0.08       --decoder_lr_mult 16
run v261_smolfwedu_sub100k_det_h4096_linin_ctx416_single_g1_r008_dec64_10K   --linout_gain 1          --dff_write_scale 0.08       --decoder_lr_mult 64
run v262_smolfwedu_sub100k_det_h4096_linin_ctx416_single_g283_r008_dec64_10K --linout_gain 2.82842712 --dff_write_scale 0.02828427 --decoder_lr_mult 64
echo "queue: ALL DONE $(date)" >> $Q
