#!/bin/bash
# --free_run 50000 x 8 streams, no reset: v459 (rat gate) vs v455 / v456 (no gate), GPU shared with the live trainer
cd /proj/devices/vla
one () { conda run --no-capture-output -n dev python vla.py --load $2 --free_run 50000 --free_rows 8 --free_window 5000 --eval_corpora fineweb --eval_gen_judge Qwen/Qwen2.5-1.5B --log /tmp/claude-1000/-proj-devices-vla/11ca6c7a-a8d6-465f-a7b5-e3fb965bb202/scratchpad/free/$1.log --free_save log/sweeps/freerun_2026-10-24/$1.txt > log/sweeps/freerun_2026-10-24/$1.out 2>&1; }
one v459_8120000 /tmp/claude-1000/-proj-devices-vla/11ca6c7a-a8d6-465f-a7b5-e3fb965bb202/scratchpad/free/v459.pt &
one v455_7807595 checkpoint/v455_v454_fw100_40M.step7807595.pt &
one v456_8020000 checkpoint/v456_v455_decay_200K.pt &
wait
