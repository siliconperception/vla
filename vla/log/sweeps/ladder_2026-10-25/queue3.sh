#!/bin/bash
# queue3.sh (rev 2: v469/v470 with GEN lines every 2000 steps, user 2026-10-25; min_p stays fixed, no --fluency_target): replaces queue2.sh (user, 2026-10-25: "go ahead with that rule, make it automatic"). After v468: v471, v469, v470
# as before; each 3c run is scored (forgetting curve) and evaluated (eval.sh: EVAL, EVALH, EVALL, EVALM) in the background;
# then select.py applies the rule, and the main run continues as v472 from the winner's checkpoint with its ladder,
# WITHOUT --weight_ema (v462 is not resumed), plus its snapshot watcher. If selection fails: the control (v468, 64,16,4,1).
cd /proj/devices/vla
S0=$1; WAIT=$2
O=log/sweeps/ladder_2026-10-25
while ps -p $WAIT > /dev/null; do sleep 30; done
post () {   # run tau: forgetting curve, then the selection evals
  bash $O/score.sh $S0 $1 $2 >> $O/score.log 2>&1
  bash $O/eval.sh checkpoint/$1.pt $2 $O/eval_$1.log >> $O/eval.log 2>&1
  echo "$(date '+%F %T') post-run done for $1"
}
echo "$(date '+%F %T') v468 trainer $WAIT gone; scoring + evaluating v468"
post v468_tau64_250K 64,16,4,1 &
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
  bash exp/run.sh $M $N "${BASE[@]}" --ctx_tau $T --run_steps $N --gen_interval 2000
  echo "$(date '+%F %T') done $M: $(grep -c '^STEP' log/exp.$M) STEP lines, $(wc -l < log/exp.$M.docs) records; scoring + evaluating"
  post $M $T &
done
wait    # every background score/eval
echo "$(date '+%F %T') 3c done; selecting"
conda run --no-capture-output -n dev python $O/select.py v468_tau64_250K:64,16,4,1 v469_tau128_250K:128,32,8,2 v470_tau32_250K:32,8,2,0.5 > $O/SELECT.txt 2>&1
cat $O/SELECT.txt
D=$(grep '^DECISION ' $O/SELECT.txt)
if [ -n "$D" ]; then W=$(echo $D | cut -d' ' -f2); T=$(echo $D | cut -d' ' -f3)
else W=v468_tau64_250K; T=64,16,4,1; echo "$(date '+%F %T') selection failed; continuing with the control"; fi
M=v472_${W#*_}; M=${M%_250K}_40M
echo "$(date '+%F %T') launching $M from checkpoint/$W.pt with ctx_tau $T (no weight EMA)"
nohup bash exp/run.sh $M 40000000 --shards 14 --context 7 --mix fineweb:1.0 --eval_corpora fineweb --no-gen_vis --no-sample_vis --gen_interval 2000 --clock_hz 25 --vision_hz 2 --audio_hz 25 --streams 3 --fifo3 --no-inner_voice --fluency_target 100 --voice_drop 0 --caption_feed 0 --text_feed 0 --speech_delay 0.12 --speech_align --eval_rare 10 --audio_encoder logmel --shard_offset 1 --nul_weight 1 --loss_norm words --eval_cloze 400 --eval_wp 0 --eval_hold 100 --doc_log 100 --eval_recent 20 --eval_pairs 1000 --eval_free 10000 --eval_at_start --ctx_tau $T --load checkpoint/$W.pt > /dev/null 2>&1 &
sleep 120
nohup exp/snapwatch.sh $M >> log/snapwatch.$M.log 2>&1 &
