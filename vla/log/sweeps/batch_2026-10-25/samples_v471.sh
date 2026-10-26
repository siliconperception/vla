#!/bin/bash
# waits for v471's trainer (615105), then appends two 300-token samples (seeds 1, 2) from its final checkpoint to samples.txt
cd /proj/devices/vla
O=log/sweeps/batch_2026-10-25; SP=/tmp/claude-1000/-proj-devices-vla/11ca6c7a-a8d6-465f-a7b5-e3fb965bb202/scratchpad
while ps -p 615105 > /dev/null; do sleep 20; done
for s in 1 2; do
  conda run --no-capture-output -n dev python vla.py --load checkpoint/v471_b1bnf_lr1e5_1M.pt --generate --n 300 --seed $s --device cuda --log $SP/gen471.log > $SP/gen471.out 2>&1
  { echo "=== B1-frozenBN-lr1e-5 (v471_b1bnf_lr1e5_1M) seed $s"; tail -1 $SP/gen471.out; echo; } >> $O/samples.txt
done
echo done
