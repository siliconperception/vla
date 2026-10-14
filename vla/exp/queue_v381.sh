#!/bin/bash
# v381-v384: first four optimizer / lr screens against the v380 baseline (2026-10-12).
#   v381  B4  lr decay on v378's 956K checkpoint: 1e-5 -> 1e-6 linearly over 200K steps, then
#             hold 1e-6 to 1,160,000 (one more eval). Is v378's ~4.85 plateau the constant lr?
#   v382  R0  v380 rerun DETERMINISTICALLY (--seed --no-shuffle --workers 1) to 100K: the
#             reference every screen below is compared against, step for step.
#   v383  D1  R0 with vanilla SGD at lr 0.03 (momentum 0, no weight decay).
#   v384  A1  R0 with --rms_alpha 0.999 (~1000-step squared-gradient window, was ~100).
# Each run is an ordinary longrun whose TOTAL is its stop step, so it ends on its own once the
# checkpoint at that step is written; the next one starts after it. Few restarts allowed: a
# screen that dies twice is a result, not something to keep relaunching.
set -u
cd /proj/devices/vla
Q=log/queue_v381.log

BASE="--dataset smolfwedu --shards 1 --no-preroll --init zero --no-bn_affine --bn_momentum 0.1
 --n_hidden 512 --c_context 384 --n_layers 1 --depth 8 --context 8 --batch 250 --monitor 100
 --opt rmsprop --schedule coswarm --lr_min 0.00001 --lr_period 2000 --lr_max 0.00001 --clip_dff 0
 --linout --linout_kernel 1 --linout_init rotate --ema 1 --ctx_ema 256,2,1 --ctx_mix none
 --ctx_first blend --ctx_cat_in --ctx_cat_narrow --no_text_proj --ctx_resid --dec_tree
 --dec_tree_linear --dec_tree_kernels 3,3,3 --dec_tree_pool --dec_width 256 --gen_score
 --checkpoint 4000 --gen_interval 4000 --eval_interval 20000 --eval_bands 1024,8192
 --tok_norm --ctx_read_norm 1"
V380="$BASE --ctx_read_norm_mode running"
DET="--seed 20261012 --no-shuffle --workers 1"

run () {   # run <total_steps> <mnemonic> <args...>
  local TOTAL=$1; shift
  local M=$1; shift
  echo "queue: $M started $(date)" >> $Q
  ./exp/launch.sh exp/longrun.sh "$M" "$TOTAL" 3 -- "$@" >> "log/longrun.$M.nohup" 2>&1
  echo "queue: $M ended at step $(grep -E '^STEP' "log/exp.$M" 2>/dev/null | tail -1 | awk '{print $2}'), trainers left: $(pgrep -fc "python vla.py.*$M") $(date)" >> $Q
}

# B4: resume a COPY of v378's last checkpoint (956,000) under a new name; longrun finds
# checkpoint/$M.pt and loads it, optimizer state included. triangle with lr_warmup = the
# resume step: lr 1e-5 at 956K, linear to 1e-6 at 1,156K (GLOBAL steps), then held.
M381=v381_smolfwedu_fwsuite_v378resume956k_lrdecay1e5to1e6over200k_ctxresid_readnorm1_toknorm_ctx256_2_1_rmsprop
if [ ! -f checkpoint/$M381.pt ]; then
  cp checkpoint/v378_smolfwedu_fwsuite_ctxresid_readnorm1_toknorm_fixwin_shards1_batch250_rmsprop_lr000001_h512_c384_d8_s8_notp_nolinin_ctx256_2_1_rot_catinnarrow_dectreelin333pool_reset0_blend_40M.pt checkpoint/$M381.pt
fi
run 1160000 $M381 $BASE --schedule triangle --lr_warmup 956000 --lr_period 200000 --lr_min 0.000001 --lr_max 0.00001

run 100000 v382_smolfwedu_fwsuite_det_v380ref_readnorm1run_toknorm_ctx256_2_1_rmsprop_lr000001_100k $V380 $DET
run 100000 v383_smolfwedu_fwsuite_det_v380_sgd003_mom0_readnorm1run_toknorm_ctx256_2_1_100k $V380 $DET --opt sgd --lr_min 0.03 --lr_max 0.03
run 100000 v384_smolfwedu_fwsuite_det_v380_rmsalpha0999_readnorm1run_toknorm_ctx256_2_1_lr000001_100k $V380 $DET --rms_alpha 0.999
echo "queue: ALL DONE $(date)" >> $Q
