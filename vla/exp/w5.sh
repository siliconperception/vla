#!/bin/bash
# The structural candidates for the contractivity loss, both from 40K to 60K -- the window
# where two runs have now collapsed (40.5% and 100% runaway at 60K).
#
# ContextCNN is Conv->BatchNorm(affine=False)->ReLU throughout, so its 49 layers are
# normalized and its output is bounded. The feedback path is not: tap, deep_proj and
# decoder.proj are bare 1x1 convs with nothing after them, so the recurrence gain is the one
# quantity in this architecture that nothing constrains. --clip_dff bounded the state and
# failed, because the drift is in the map, not the state.
#
#   wnotap    no --tap at all. The register then receives ContextCNN's output directly --
#             post-BatchNorm, post-ReLU -- so it is bounded by construction and sparse
#             (~50% exact zeros). The simplest possible fix: delete the unbounded map.
#             NOTE this is not a resume of the same architecture -- dropping tap removes
#             parameters -- so it trains from scratch and 20K steps only gets it to where
#             wexp/wfix236 were at 20K. Judged on runaway rate, not on loss.
#   wtapgn    keep --tap but normalize its output with GroupNorm(32, affine=False):
#             identical in train and eval (no running statistics), so it bounds the feedback
#             gain without adding the train/eval mismatch that BatchNorm would. Adds no
#             parameters, so this one DOES resume from the 40K checkpoint.
cd /proj/devices/vla
COMMON="--dataset web --preroll --tokenizer pythia31m --context 16 --n_hidden 256 --kernel 3 \
--batch 250 --monitor 20 --opt sgd --momentum 0.0 --weight_decay 0.0 \
--schedule const --lr_max 0.01 --seed 1 --device cuda \
--n_layers 7 --depth 7 --clock fixed --clock_base 2.36 --init gaussian --ema 0.5 --accumulate"

echo "=== START wtapgn (resume from 40K, tap + GroupNorm) $(date +%H:%M)"
cp -f checkpoint.pt.wfix236.40k checkpoint.pt.wtapgn
conda run --no-capture-output -n dev python vla.py $COMMON --tap --tap_norm group \
  --load checkpoint.pt.wtapgn --save checkpoint.pt.wtapgn \
  --run_steps 20001 --checkpoint 5000 --log log/exp.wtapgn > log/exp.wtapgn.out 2>&1
echo "=== score wtapgn @ 60K"
conda run --no-capture-output -n dev python exp/score.py checkpoint.pt.wtapgn \
  --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null | grep -E "^checkpoint|^wtapgn|^----"

echo "=== START wnotap (from scratch, no tap) $(date +%H:%M)"
conda run --no-capture-output -n dev python vla.py $COMMON \
  --save checkpoint.pt.wnotap \
  --run_steps 20001 --checkpoint 5000 --log log/exp.wnotap > log/exp.wnotap.out 2>&1
echo "=== score wnotap @ 20K"
conda run --no-capture-output -n dev python exp/score.py checkpoint.pt.wnotap \
  --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null | grep -E "^checkpoint|^wnotap|^----"
echo "W5 COMPLETE $(date)"
