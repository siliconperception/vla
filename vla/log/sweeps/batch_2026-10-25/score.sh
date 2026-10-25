#!/bin/bash
# score.sh <pre checkpoint> <run> <batch>: paired forgetting curve in tokens for one ladder run
cd /proj/devices/vla
O=log/sweeps/batch_2026-10-25; P=$1; M=$2; B=$3
for c in pre:$P now:checkpoint/$M.pt; do
  conda run --no-capture-output -n dev python vla.py --load ${c#*:} --doc_score $O/${M}_${c%%:*}.jsonl \
    --doc_log_file log/exp.$M.docs --doc_log_len 384 --eval_corpora fineweb --eval_docs 400 \
    --log /tmp/claude-1000/-proj-devices-vla/11ca6c7a-a8d6-465f-a7b5-e3fb965bb202/scratchpad/batch_${M}_${c%%:*}.log 2>&1 | grep -E '^--doc_score|Traceback'
done
conda run --no-capture-output -n dev python $O/pair_tokens.py $O/${M}_pre.jsonl $O/${M}_now.jsonl $B | tee $O/$M.curve
