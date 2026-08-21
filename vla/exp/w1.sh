#!/bin/bash
# W1 -- the decisive contrast on openwebtext (median 752 tokens/doc against TinyStories' 196).
#
# On tiny the winners reach ~16 tokens: a 196-token children's story has little dependency
# structure past a clause, so the model that spends everything on local statistics wins.
# That is a corpus property, and a 16-token recurrent context is not a serious proposition
# against a KV cache. This asks whether document-scale reach pays on documents that have it.
#
#   wexp     exp, ema 0.5          reach ~26    -- the tiny winner, short reach
#   wfix236  fixed, base 2.36      reach ~750   -- ladder 1,2,6,13,31,73,173, p_max=173
#
# 20K steps, not 10K: long-reach configs converge slower (sincr broke through at 1700 vs
# ssync at 860) and openwebtext is harder, so a short budget would re-derive the tiny
# artifact by simply not letting the ladder finish converging.
cd /proj/devices/vla
S=20000
run () { M=$1; shift
  [ -f exp/done.$M ] && { echo "skip $M"; return; }
  echo "=== START $M ($S steps) $* $(date)"
  ./exp/run_web.sh $M $S "$@"
  conda run --no-capture-output -n dev python exp/score.py checkpoint.pt.$M \
      --corpus web --docs 400 --minlen 512 --maxlen 1024 > log/exp.$M.score 2>&1
  conda run --no-capture-output -n dev python exp/reach.py --load checkpoint.pt.$M \
      --corpus web --docs 800 --rows 500 --minlen 512 --maxlen 1024 --len 1024 \
      --periods 64,512 > log/exp.$M.reach 2>&1
  touch exp/done.$M
  echo "=== END $M $(date)"; }

T="--tap --init gaussian --ema 0.5 --accumulate"
run wexp    --n_layers 7 --depth 7 --clock exp   $T
run wfix236 --n_layers 7 --depth 7 --clock fixed $T --clock_base 2.36
echo "W1 COMPLETE $(date)"
