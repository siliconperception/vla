#!/bin/bash
# 200-step lr x momentum probe on openwebtext, --streaming for fast init (~10s vs 4.5 min
# for the memory-mapped non-streaming load). Both W1 architectures, so the optimizer choice
# is not tuned on one and applied blind to the other.
# Looking for: loss well down by step 200, dff_max NOT in the 1e5 range (lr 0.1 momentum 0
# put it at 6e5 and flat), and grad not collapsed to a constant.
cd /proj/devices/vla
S=200
SP=/tmp/claude-1000/-proj-devices-vla/f109efd3-cf20-4d0a-9144-4ca0dbbd6efd/scratchpad
one () {  # one <tag> <arch args...> -- optimizer args come from $OPT
  T=$1; shift
  [ -f log/w0/$T.done ] && { echo "skip $T"; return; }
  conda run --no-capture-output -n dev python vla.py \
    --dataset web --streaming --preroll --tokenizer pythia31m \
    --context 16 --n_hidden 256 --kernel 3 --batch 250 --monitor 20 \
    --opt sgd --weight_decay 0.0 $OPT \
    --schedule const --seed 1 --device cuda \
    --run_steps $((S+1)) --checkpoint 999999 \
    --log log/w0/$T --save $SP/w0.pt \
    "$@" > log/w0/$T.out 2>&1
  touch log/w0/$T.done
  echo "  done $T  $(grep '^STEP' log/w0/$T | tail -1 | awk '{printf "loss %.3f dff_max %.1f",$7,$17}')"
}

EXP="--n_layers 7 --depth 7 --clock exp   --tap --init gaussian --ema 0.5 --accumulate"
FIX="--n_layers 7 --depth 7 --clock fixed --tap --init gaussian --ema 0.5 --accumulate --clock_base 2.36"

for LR in 0.003 0.01 0.03 0.1; do
  for M in 0 9; do
    if [ $M = 0 ]; then OPT="--momentum 0.0 --lr_max $LR"; MT=m0
    else                OPT="--momentum 0.9 --nesterov --lr_max $LR"; MT=m9n; fi
    echo "=== lr $LR $MT $(date +%H:%M:%S)"
    one "exp.$LR.$MT" $EXP
    one "fix.$LR.$MT" $FIX
  done
done
echo "W0 COMPLETE $(date)"
