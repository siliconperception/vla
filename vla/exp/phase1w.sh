#!/bin/bash
# Long-range track: same architecture sweep, trained on openwebtext (median 752 tokens/doc
# against TinyStories' 211) so a memory horizon past ~200 tokens can actually be measured.
cd /proj/devices/vla
S=10000
run () {
  M=$1; shift
  [ -f exp/done.$M ] && { echo "skip $M"; return; }
  echo "=== START $M $* $(date)"
  ./exp/run_web.sh $M $S "$@"
  conda run --no-capture-output -n dev python exp/memtest.py --load checkpoint.pt.$M \
      --corpus web --docs 250 --batch 250 --minlen 256 --maxlen 1024 --periods 0,16,64,256 \
      > log/exp.$M.mem 2>&1
  touch exp/done.$M
  echo "=== END $M $(date)"
}
T="--tap --init gaussian --ema 0.5 --accumulate"
run wbase  --n_layers 7  --depth 7  --clock fixed  $T
run wsync  --n_layers 7  --depth 7  --clock sync   $T
run wincr  --n_layers 7  --depth 7  --clock incr   $T
run wnoema --n_layers 7  --depth 7  --clock fixed --tap --init gaussian --accumulate
run w1x50  --n_layers 1  --depth 50 --clock sync   $T
run w10x5i --n_layers 10 --depth 5  --clock incr   $T
echo "PHASE1W COMPLETE $(date)"
