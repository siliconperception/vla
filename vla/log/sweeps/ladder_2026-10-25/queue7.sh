#!/bin/bash
# queue7.sh (user, 2026-10-25 21:35: "i like v469 better"): replaces queue6.sh's tail. v472 continues from v469
# (ctx_tau 128,32,8,2), overriding select.py's lowest-EVAL pick (v469 4.612 vs control 4.575; v469's EVALL
# fluency rises over 10K tokens, drift +7.1 vs -3.7). Waits for v470's trainer (started by queue6.sh), launches
# v472 at once, and scores/evaluates v470 alongside it; select.py still runs, for the record only.
cd /proj/devices/vla
S0=$1; P=$2   # P = v470's trainer PID
O=log/sweeps/ladder_2026-10-25
while kill -0 $P 2>/dev/null; do sleep 30; done
sleep 30      # let run.sh finish its bookkeeping
M=v470_tau32_250K
echo "$(date '+%F %T') done $M: $(grep -c '^STEP' log/exp.$M) STEP lines, $(wc -l < log/exp.$M.docs) records; scoring + evaluating"
( bash $O/score.sh $S0 $M 32,8,2,0.5 >> $O/score.log 2>&1
  bash $O/eval.sh checkpoint/$M.pt 32,8,2,0.5 $O/eval_$M.log >> $O/eval.log 2>&1
  echo "$(date '+%F %T') post-run done for $M"
  conda run --no-capture-output -n dev python $O/select.py v468_tau64_250K:64,16,4,1 v469_tau128_250K:128,32,8,2 v470_tau32_250K:32,8,2,0.5 > $O/SELECT.txt 2>&1
  echo "$(date '+%F %T') select.py (record only): $(grep '^DECISION ' $O/SELECT.txt)" ) &
W=v469_tau128_250K; T=128,32,8,2; M=v472_tau128_40M
echo "$(date '+%F %T') launching $M from checkpoint/$W.pt with ctx_tau $T (user's pick; no weight EMA)"
nohup bash exp/run.sh $M 40000000 --shards 14 --context 7 --mix fineweb:1.0 --eval_corpora fineweb --no-gen_vis --no-sample_vis --gen_interval 2000 --clock_hz 25 --vision_hz 2 --audio_hz 25 --streams 3 --fifo3 --no-inner_voice --fluency_target 100 --voice_drop 0 --caption_feed 0 --text_feed 0 --speech_delay 0.12 --speech_align --eval_rare 10 --audio_encoder logmel --shard_offset 1 --nul_weight 1 --loss_norm words --eval_cloze 400 --eval_wp 0 --eval_hold 100 --doc_log 100 --eval_recent 20 --eval_pairs 1000 --eval_free 10000 --eval_at_start --ctx_tau $T --load checkpoint/$W.pt > /dev/null 2>&1 &
sleep 120
nohup exp/snapwatch.sh $M >> log/snapwatch.$M.log 2>&1 &
wait
