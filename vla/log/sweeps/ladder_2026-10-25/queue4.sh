#!/bin/bash
# queue4.sh (user, 2026-10-25: "restart v468 with GEN lines"): v468 was stopped at 8839493 (SIGTERM save; copy
# .step8839493.pt) and resumes to its planned end, 8973091 (133598 steps), with GEN lines every 2000 steps -- observation
# only: min_p fixed, no --fluency_target. Then queue3.sh as before (v468 post-run, v471, v469, v470, selection, v472).
cd /proj/devices/vla
S0=$1
O=log/sweeps/ladder_2026-10-25
BASE=(--shards 14 --context 7 --mix fineweb:1.0 --eval_corpora fineweb --no-gen_vis --no-sample_vis --gen_interval 0
      --clock_hz 25 --vision_hz 2 --audio_hz 25 --streams 3 --fifo3 --no-inner_voice --voice_drop 0
      --caption_feed 0 --text_feed 0 --speech_delay 0.12 --speech_align --audio_encoder logmel --shard_offset 1
      --nul_weight 1 --loss_norm words --eval_interval 0 --checkpoint 1000000000 --doc_log 25 --doc_keep 1
      --batch 250 --lr_max 0.01 --load $S0)
echo "$(date '+%F %T') resume v468_tau64_250K at 8839493 for 133598 steps, GEN every 2000"
bash exp/run.sh v468_tau64_250K 133598 "${BASE[@]}" --ctx_tau 64,16,4,1 --run_steps 133598 --gen_interval 2000 --load checkpoint/v468_tau64_250K.pt
grep '^STEP' log/exp.v468_tau64_250K | tail -1 | cut -c1-40
exec bash $O/queue3.sh $S0 0
