#!/bin/bash
# score.sh <start checkpoint> <run> <ctx_tau>: paired forgetting curve (age in steps) for one 3c run; both reads use the run's ladder
cd /proj/devices/vla
O=log/sweeps/ladder_2026-10-25; P=$1; M=$2; T=$3
for c in pre:$P now:checkpoint/$M.pt; do
  conda run --no-capture-output -n dev python vla.py --load ${c#*:} --clock_hz 25 --ctx_tau $T --doc_score $O/${M}_${c%%:*}.jsonl \
    --doc_log_file log/exp.$M.docs --doc_log_len 384 --eval_corpora fineweb --eval_docs 400 \
    --log /tmp/claude-1000/-proj-devices-vla/11ca6c7a-a8d6-465f-a7b5-e3fb965bb202/scratchpad/ladder_${M}_${c%%:*}.log 2>&1 | grep -E '^--doc_score|Traceback'
done
echo "== $M ctx_tau $T"
conda run --no-capture-output -n dev python log/sweeps/forgetting_2026-10-25/pair.py $O/${M}_pre.jsonl $O/${M}_now.jsonl | tee $O/$M.curve
