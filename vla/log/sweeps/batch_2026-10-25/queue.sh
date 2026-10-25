#!/bin/bash
# Step 5 of PLAN_memory_2026-10-25: the batch-size ladder toward batch 1 (the deployed continual learner).
# Every run: from v462's stop checkpoint ($1), 1M training tokens, lr/B fixed at 4e-5 (linear scaling), every document
# recorded (--doc_log 1 --doc_keep 1), no evals in the loop; scored offline by score.sh (paired forgetting curve in tokens).
# Then v462 resumes (same config, same name) with its snapshot watcher.
cd /proj/devices/vla
S0=$1                        # e.g. checkpoint/v462_v461_wema_40M.step8722345.pt
O=log/sweeps/batch_2026-10-25
BASE=(--shards 14 --context 7 --mix fineweb:1.0 --eval_corpora fineweb --no-gen_vis --no-sample_vis --gen_interval 0
      --clock_hz 25 --ctx_tau 64,16,4,1 --vision_hz 2 --audio_hz 25 --streams 3 --fifo3 --no-inner_voice --voice_drop 0
      --caption_feed 0 --text_feed 0 --speech_delay 0.12 --speech_align --audio_encoder logmel --shard_offset 1
      --nul_weight 1 --loss_norm words --eval_interval 0 --checkpoint 1000000000 --doc_log 1 --doc_keep 1 --load $S0)
run () {   # name batch lr steps [extra...]
  local M=$1 B=$2 LR=$3 N=$4; shift 4
  echo "$(date '+%F %T') start $M batch $B lr $LR steps $N"
  bash exp/run.sh $M $N "${BASE[@]}" --batch $B --lr_max $LR --run_steps $N "$@"
  echo "$(date '+%F %T') done $M: $(grep -c '^STEP' log/exp.$M) STEP lines, $(wc -l < log/exp.$M.docs) records"
}
run v463_b250_1M     250 0.01    4000
run v464_b250bnf_1M  250 0.01    4000    --bn_frozen
run v465_b32bnf_1M    32 0.00128 31250   --bn_frozen
run v466_b4bnf_1M      4 0.00016 250000  --bn_frozen
run v467_b1bnf_1M      1 0.00004 1000000 --bn_frozen
echo "$(date '+%F %T') ladder done; resuming v462"
nohup bash exp/run.sh v462_v461_wema_40M 40000000 --shards 14 --context 7 --mix fineweb:1.0 --eval_corpora fineweb --no-gen_vis --no-sample_vis --gen_interval 2000 --clock_hz 25 --ctx_tau 64,16,4,1 --vision_hz 2 --audio_hz 25 --streams 3 --fifo3 --no-inner_voice --fluency_target 100 --voice_drop 0 --caption_feed 0 --text_feed 0 --speech_delay 0.12 --speech_align --eval_rare 10 --audio_encoder logmel --shard_offset 1 --nul_weight 1 --loss_norm words --eval_cloze 400 --eval_wp 0 --eval_hold 100 --doc_log 100 --eval_recent 20 --eval_pairs 1000 --eval_free 10000 --weight_ema 10000,100000 --eval_at_start --load checkpoint/v462_v461_wema_40M.pt > /dev/null 2>&1 &
sleep 120
nohup exp/snapwatch.sh v462_v461_wema_40M >> log/snapwatch.v462_v461_wema_40M.log 2>&1 &
