#!/bin/bash
# GroupNorm lr ladder, upward (user, 2026-08-23).  E39 (GN32 at lr 0.03) stalled
# at the unigram floor for 16K steps: loss flat 7.58-7.71, and crucially
# grad 0.48-0.95, an order of magnitude BELOW the 4-6 every healthy run shows,
# with dff_max 5-12 and dff_zeros steady at 0.43-0.47.  Nothing exploding,
# nothing dying -- the model simply was not receiving a usable gradient.  That is
# the drowned-token signature (section 6b), which points to the effective step
# being too SMALL, not too large.
# Plausible mechanism: GroupNorm(32) normalizes over 256/32 = 8 channels x 16 x 16
# = 2048 elements per sample, where BatchNorm normalizes each channel over
# 250 x 16 x 16 = 64000 elements pooled across the batch.  Per-sample statistics
# are far noisier, and dividing by a noisy scale attenuates the gradient.
# So: go UP on lr, and try larger groups (fewer, bigger groups = more elements
# per statistic = less noise; --norm_groups 1 is LayerNorm over all 256 channels,
# 65536 elements per sample).
cd /proj/devices/vla
go () { M=$1; E=$2; shift 2
  [ -f exp/done.$M ] && { echo "skip $M"; return; }
  echo "=== START $M $* $(date '+%H:%M')"
  ./exp/watch.sh $M $E > /dev/null 2>&1 & WP=$!
  ./exp/run.sh $M 20000 --norm group "$@"
  sleep 25; kill $WP 2>/dev/null
  cp -f checkpoint/$M.pt checkpoint/$M.final.pt 2>/dev/null
  conda run --no-capture-output -n dev python exp/score.py checkpoint/$M.final.pt \
      --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null \
      | grep -E "^$M" | tee -a PLAN.txt
  conda run --no-capture-output -n dev python exp/gencheck.py checkpoint/$M.final.pt 80 3 \
      2>/dev/null | tee -a PLAN.txt
  touch exp/done.$M; echo "=== END $M $(date '+%H:%M')"; }

go e43_gn32_lr10 E43 --norm_groups 32 --lr_max 0.1
go e40_gn1       E40 --norm_groups 1   --lr_max 0.1
go e44_gn32_lr30 E44 --norm_groups 32 --lr_max 0.3
echo "GROUPNORM3 COMPLETE $(date)"
