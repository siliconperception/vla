#!/bin/bash
# queue2.sh: replaces queue.sh after v468 (user, 2026-10-25: "add v471 next"). Waits for v468's trainer ($2, a PID),
# scores v468, runs v471 (batch 1, lr 1e-5, frozen BatchNorm, 1M tokens: is lr 4e-5 too high at batch 1?) and scores
# it like the batch ladder, then the rest of 3c (v469, v470) and the v462 resume, as queue.sh would have.
cd /proj/devices/vla
S0=$1; WAIT=$2
O=log/sweeps/ladder_2026-10-25
while ps -p $WAIT > /dev/null; do sleep 30; done
echo "$(date '+%F %T') v468 trainer $WAIT gone; scoring v468"
bash $O/score.sh $S0 v468_tau64_250K 64,16,4,1 >> $O/score.log 2>&1 &
B=(--shards 14 --context 7 --mix fineweb:1.0 --eval_corpora fineweb --no-gen_vis --no-sample_vis --gen_interval 0
   --clock_hz 25 --ctx_tau 64,16,4,1 --vision_hz 2 --audio_hz 25 --streams 3 --fifo3 --no-inner_voice --voice_drop 0
   --caption_feed 0 --text_feed 0 --speech_delay 0.12 --speech_align --audio_encoder logmel --shard_offset 1
   --nul_weight 1 --loss_norm words --eval_interval 0 --checkpoint 1000000000 --doc_log 1 --doc_keep 1 --load $S0)
M=v471_b1bnf_lr1e5_1M
echo "$(date '+%F %T') start $M batch 1 lr 0.00001 steps 1000000"
bash exp/run.sh $M 1000000 "${B[@]}" --batch 1 --lr_max 0.00001 --run_steps 1000000 --bn_frozen
echo "$(date '+%F %T') done $M: $(grep -c '^STEP' log/exp.$M) STEP lines, $(wc -l < log/exp.$M.docs) records; scoring"
bash log/sweeps/batch_2026-10-25/score.sh $S0 $M 1 >> log/sweeps/batch_2026-10-25/score.log 2>&1 &
BASE=(--shards 14 --context 7 --mix fineweb:1.0 --eval_corpora fineweb --no-gen_vis --no-sample_vis --gen_interval 0
      --clock_hz 25 --vision_hz 2 --audio_hz 25 --streams 3 --fifo3 --no-inner_voice --voice_drop 0
      --caption_feed 0 --text_feed 0 --speech_delay 0.12 --speech_align --audio_encoder logmel --shard_offset 1
      --nul_weight 1 --loss_norm words --eval_interval 0 --checkpoint 1000000000 --doc_log 25 --doc_keep 1
      --batch 250 --lr_max 0.01 --load $S0)
N=250000
for x in v469_tau128_250K:128,32,8,2 v470_tau32_250K:32,8,2,0.5; do
  M=${x%%:*}; T=${x#*:}
  echo "$(date '+%F %T') start $M ctx_tau $T steps $N"
  bash exp/run.sh $M $N "${BASE[@]}" --ctx_tau $T --run_steps $N
  echo "$(date '+%F %T') done $M: $(grep -c '^STEP' log/exp.$M) STEP lines, $(wc -l < log/exp.$M.docs) records; scoring"
  bash $O/score.sh $S0 $M $T >> $O/score.log 2>&1 &
done
echo "$(date '+%F %T') 3c done; resuming v462"
nohup bash exp/run.sh v462_v461_wema_40M 40000000 --shards 14 --context 7 --mix fineweb:1.0 --eval_corpora fineweb --no-gen_vis --no-sample_vis --gen_interval 2000 --clock_hz 25 --ctx_tau 64,16,4,1 --vision_hz 2 --audio_hz 25 --streams 3 --fifo3 --no-inner_voice --fluency_target 100 --voice_drop 0 --caption_feed 0 --text_feed 0 --speech_delay 0.12 --speech_align --eval_rare 10 --audio_encoder logmel --shard_offset 1 --nul_weight 1 --loss_norm words --eval_cloze 400 --eval_wp 0 --eval_hold 100 --doc_log 100 --eval_recent 20 --eval_pairs 1000 --eval_free 10000 --weight_ema 10000,100000 --eval_at_start --load checkpoint/v462_v461_wema_40M.pt > /dev/null 2>&1 &
sleep 120
nohup exp/snapwatch.sh v462_v461_wema_40M >> log/snapwatch.v462_v461_wema_40M.log 2>&1 &
