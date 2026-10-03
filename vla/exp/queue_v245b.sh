#!/bin/bash
# v245-v249: next (g, r) corner beyond v241 (g=2.83, r=0.71): g in {2.83, 4} x r in {0.5, 0.35},
# plus the r=0 control (no feedback) at g=2.83. 20K each, training loss. s = r / g.
# v245b: v249 (r=0 control) first, then v246-v248. v245 already done via queue_v245.sh.
# Per-run stop step: run <stop> <mnemonic> <args...>.
# Same seed, same data (--no-shuffle --workers 1 makes the batch stream bit-identical across
# runs; verified 2026-10-02), same everything except --ctx_mix. Each run is the normal 40M-step
# longrun, stopped here once its step-40K EVAL is logged and the checkpoint has been written.
set -u
cd /proj/devices/vla
STOP=40000
COMMON="--dataset smolfwedu --shards 1 --subsample 100000 --no-shuffle --seed 20261002 --workers 1
 --no-preroll --init gaussian --no-bn_affine --bn_momentum 0.1 --tokenizer pythia31m
 --n_hidden 4096 --c_context 256 --n_layers 1 --depth 16 --context 8 --batch 250 --monitor 100
 --opt sgd --schedule coswarm --lr_min 0.00001 --lr_period 2000 --lr_max 0.03 --clip_dff 0
 --linout --linout_kernel 1 --linin --ema 1 --ctx_ema 4,16 --gen_score --checkpoint 2000
 --gen_interval 2000 --eval_interval 20000 --eval_corpora smolfwedu,fineweb,tinytb --eval_docs 100"
Q=log/queue_v245b.log
run () {
  local STOP=$1; shift
  local M=$1; shift
  # setsid: the driver leads its own process group, so one kill reaches driver, run.sh,
  # conda and the trainer -- no orphan longrun left to relaunch anything.
  setsid ./exp/launch.sh exp/longrun.sh "$M" 40000000 40 -- $COMMON "$@" >> "log/longrun.$M.nohup" 2>&1 &
  local PG=$!
  echo $PG > "log/longrun.$M.driverpid"
  echo "queue: $M started (pgid $PG) $(date)" >> $Q
  until [ "$(grep -cE "^EVAL step +$STOP " "log/exp.$M" 2>/dev/null)" -ge 3 ]; do
    sleep 60
    kill -0 $PG 2>/dev/null || { echo "queue: $M driver EXITED before step $STOP $(date)" >> $Q; break; }
  done
  # let the step-STOP checkpoint land (it is written at the same step as the eval)
  for i in $(seq 30); do
    conda run --no-capture-output -n dev python - "$M" "$STOP" <<'PY' 2>/dev/null && break
import sys, torch
s = torch.load(f'checkpoint/{sys.argv[1]}.pt', map_location='cpu', weights_only=False).get('step', 0)
sys.exit(0 if s >= int(sys.argv[2]) else 1)
PY
    sleep 20
  done
  kill -- -$PG 2>/dev/null; sleep 10; kill -9 -- -$PG 2>/dev/null
  for i in $(seq 30); do pgrep -f "vla.py.*$M" >/dev/null || break; sleep 2; done
  echo "queue: $M stopped at step $(grep -E '^STEP' "log/exp.$M" | tail -1 | awk '{print $2}'), trainers left: $(pgrep -fc "vla.py.*$M") $(date)" >> $Q
}

run 20000 v249_smolfwedu_sub100k_det_h4096_c256_d16_linin_ctx416_single_g283_r0_40M   --ctx_mix none --linout_gain 2.82842712 --dff_write_scale 0
run 20000 v246_smolfwedu_sub100k_det_h4096_c256_d16_linin_ctx416_single_g283_r035_40M --ctx_mix none --linout_gain 2.82842712 --dff_write_scale 0.125
run 20000 v247_smolfwedu_sub100k_det_h4096_c256_d16_linin_ctx416_single_g4_r050_40M   --ctx_mix none --linout_gain 4          --dff_write_scale 0.125
run 20000 v248_smolfwedu_sub100k_det_h4096_c256_d16_linin_ctx416_single_g4_r035_40M   --ctx_mix none --linout_gain 4          --dff_write_scale 0.08838835
echo "queue: ALL DONE $(date)" >> $Q
