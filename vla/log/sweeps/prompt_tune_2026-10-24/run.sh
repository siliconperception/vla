#!/bin/bash
# --prompt_tune: EVALG's 50 prompts (128 tokens, 128-token continuations), none / cold / warm256 / state-tuned (200 Adam steps, caps 1,3,0), v460 checkpoint copy, GPU shared with v460
cd /proj/devices/vla
conda run --no-capture-output -n dev python vla.py --load /tmp/claude-1000/-proj-devices-vla/11ca6c7a-a8d6-465f-a7b5-e3fb965bb202/scratchpad/tune/v460.pt --prompt_tune 200 --prompt_tune_batch 8 --prompt_warm 256 --prompt_tune_cap 1,3,0 --eval_gen 50 --eval_corpora fineweb --eval_gen_prompt 128 --eval_gen_len 128 --eval_gen_judge Qwen/Qwen2.5-1.5B --log /tmp/claude-1000/-proj-devices-vla/11ca6c7a-a8d6-465f-a7b5-e3fb965bb202/scratchpad/tune/v460.log --prompt_tune_save log/sweeps/prompt_tune_2026-10-24/v460.txt > log/sweeps/prompt_tune_2026-10-24/v460.out 2>&1
