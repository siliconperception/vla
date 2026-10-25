#!/bin/bash
# Step 3c of PLAN_memory_2026-10-25: does the DFF register ladder set what the weights keep?
# Warm start from v462's stop checkpoint ($1, the same start as the batch ladder): control (trained ladder 64,16,4,1 s),
# every window 2x slower (128,32,8,2) and 2x faster (32,8,2,0.5); batch 250, lr 0.01, 250K steps each, no evals in the
# loop, every 25th step's next document recorded (--doc_log 25 --doc_keep 1). Scored by score.sh (paired forgetting
# curve in steps, pre = the start checkpoint read with the run's own ladder). Waits for the batch ladder's last trainer
# ($2, a PID), then v462 resumes with its snapshot watcher.
cd /proj/devices/vla
S0=$1; WAIT=$2
O=log/sweeps/ladder_2026-10-25
while ps -p $WAIT > /dev/null; do sleep 30; done
echo "$(date '+%F %T') batch ladder trainer $WAIT gone; scoring v467 in the background"
bash log/sweeps/batch_2026-10-25/score.sh $S0 v467_b1bnf_1M 1 >> log/sweeps/batch_2026-10-25/score.log 2>&1 &
BASE=(--shards 14 --context 7 --mix fineweb:1.0 --eval_corpora fineweb --no-gen_vis --no-sample_vis --gen_interval 0
      --clock_hz 25 --vision_hz 2 --audio_hz 25 --streams 3 --fifo3 --no-inner_voice --voice_drop 0
      --caption_feed 0 --text_feed 0 --speech_delay 0.12 --speech_align --audio_encoder logmel --shard_offset 1
      --nul_weight 1 --loss_norm words --eval_interval 0 --checkpoint 1000000000 --doc_log 25 --doc_keep 1
      --batch 250 --lr_max 0.01 --load $S0)
N=250000
for x in v468_tau64_250K:64,16,4,1 v469_tau128_250K:128,32,8,2 v470_tau32_250K:32,8,2,0.5; do
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
