#!/bin/bash
# Yardstick (2026-10-26): EVALM's minimal pairs (BLiMP 1005 + ComVE 999) scored by small reference LMs,
# each sentence from a bare BOS (exp/pairs_ref.py), GPU shared with v472. Compare with v472's EVALM lines.
cd /proj/devices/vla
O=log/sweeps/yardstick_2026-10-26
for m in EleutherAI/pythia-14m EleutherAI/pythia-31m EleutherAI/pythia-70m babylm/babyllama-10m-2024 babylm/babyllama-100m-2024 \
         timinar/baby-llama-58m roneneldan/TinyStories-33M SimpleStories/SimpleStories-V2-35M HuggingFaceTB/SmolLM2-135M; do
  conda run --no-capture-output -n dev python exp/pairs_ref.py $m 1000 2>&1 | grep -E '^REF|Error' | tail -2
done
# GPT-BERT (the 2025 BabyLM baselines) needs its repo code, which fails under transformers 5 ('all_tied_weights_keys'); skipped
