#!/bin/bash
# Frozen-BatchNorm held-out loss (v464 +0.072 vs v463 +0.007 from the same start): loss by position in the document.
# Per-token nats (--doc_score --doc_tokens) for the start checkpoint, v463 (batch 250) and v464 (batch 250, --bn_frozen),
# held-out documents up to 2048 tokens plus v464's recorded training documents (384), then pos.py bins by position.
cd /proj/devices/vla
O=log/sweeps/bnfrozen_2026-10-25
for c in start:checkpoint/v462_v461_wema_40M.step8723091.pt v463:checkpoint/v463_b250_1M.pt v464:checkpoint/v464_b250bnf_1M.pt; do
  conda run --no-capture-output -n dev python vla.py --load ${c#*:} --doc_score $O/${c%%:*}.jsonl --doc_tokens \
    --doc_log_file log/exp.v464_b250bnf_1M.docs --doc_log_len 2048 --eval_corpora fineweb --eval_docs 400 \
    --log /tmp/claude-1000/-proj-devices-vla/11ca6c7a-a8d6-465f-a7b5-e3fb965bb202/scratchpad/bnf_${c%%:*}.log 2>&1 | grep -E '^--doc_score|Traceback|Error'
done
conda run --no-capture-output -n dev python $O/pos.py $O/start.jsonl $O/v463.jsonl $O/v464.jsonl | tee $O/SUMMARY.txt
