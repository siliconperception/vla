#!/bin/bash
# EVALM (--eval_pairs 1000: BLiMP 1005 + ComVE 999 pairs, each sentence from a zero state) across the lineage, GPU shared with v460
cd /proj/devices/vla
O=log/sweeps/pairs_2026-10-24
one () { conda run --no-capture-output -n dev python vla.py --load $2 --eval --eval_corpora fineweb --eval_docs 10 --eval_gen 0 --eval_cloze 0 --eval_hold 0 --eval_wp 0 --eval_info 0 --eval_reach 0 --eval_recent 0 --eval_pairs 1000 --log /tmp/claude-1000/-proj-devices-vla/11ca6c7a-a8d6-465f-a7b5-e3fb965bb202/scratchpad/pairs/$1.log > $O/$1.out 2>&1; }
one v442_5360000 checkpoint/v442_v441_nul_40M.step5360000.pt &
one v445_6300000 checkpoint/v445_v444_audio25_40M.step6300000.pt &
one v452_6810001 checkpoint/v452_v451_align_40M.step6810001.pt &
wait
one v454_6915254 checkpoint/v454_v453_cloze_40M.step6915254.pt &
one v456_8020000 checkpoint/v456_v455_decay_200K.pt &
one v459_8220000 checkpoint/v459_v455_rat4_shards14_40M.step8220000.pt &
wait
one v455_7807595 checkpoint/v455_v454_fw100_40M.step7807595.pt
grep -H ^EVALM $O/*.out
