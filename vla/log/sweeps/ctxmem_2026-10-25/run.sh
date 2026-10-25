#!/bin/bash
# 3b: is the weights' memory of a document keyed on the slow register context? Paired forgetting curve
# (pre = v460 step 7900000, now = v461 step 8646887; v461's recorded documents), with registers read as their mean state
cd /proj/devices/vla
O=log/sweeps/ctxmem_2026-10-25
for ab in none 1 1,2 3,4; do
  for c in pre:checkpoint/v460_v455_shards14_40M.step7900000.pt now:checkpoint/v461_v460_evalfree_40M.step8646887.pt; do
    n=${c%%:*}; f=${c#*:}
    conda run --no-capture-output -n dev python vla.py --load $f --doc_score $O/score_${n}_$ab.jsonl --doc_log_file $O/v461.docs \
      --doc_log_len 384 --eval_corpora fineweb --eval_docs 400 $( [ $ab != none ] && echo --doc_ablate $ab ) \
      --log /tmp/claude-1000/-proj-devices-vla/11ca6c7a-a8d6-465f-a7b5-e3fb965bb202/scratchpad/ctxmem/${n}_$ab.log 2>&1 | grep -E 'doc_score|doc_ablate|Traceback|Error'
  done
  echo "== ablate $ab"; conda run --no-capture-output -n dev python log/sweeps/forgetting_2026-10-25/pair.py $O/score_pre_$ab.jsonl $O/score_now_$ab.jsonl
done
