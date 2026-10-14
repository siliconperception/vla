#!/bin/bash
# v385: D1 retry -- v380 deterministic reference (v382) with vanilla SGD at lr 0.001 (vla.py's
# default lr_max), momentum 0, no clip. v383 (SGD 0.03) went NaN at step 17 (grad 68 at step 0).
# Waits for queue_v381 (v384 is its last run) to finish, then runs.
set -u
cd /proj/devices/vla
Q=log/queue_v381.log
while pgrep -f 'exp/.run/queue_v381\.' > /dev/null; do sleep 60; done

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

M=v385_smolfwedu_fwsuite_det_v380_sgd0001_mom0_readnorm1run_toknorm_ctx256_2_1_100k
echo "queue: $M started $(date)" >> $Q
./exp/launch.sh exp/longrun.sh "$M" 100000 3 -- $V380 $DET --opt sgd --lr_min 0.001 --lr_max 0.001 >> "log/longrun.$M.nohup" 2>&1
echo "queue: $M ended at step $(grep -E '^STEP' "log/exp.$M" 2>/dev/null | tail -1 | awk '{print $2}'), trainers left: $(pgrep -fc "python vla.py.*$M") $(date)" >> $Q
echo "queue: v385 DONE $(date)" >> $Q
