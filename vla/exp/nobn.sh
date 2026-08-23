#!/bin/bash
# --norm none breakthrough grid (PLAN.txt section 14).  Short 10K runs scored on
# steps-to-breakthrough: if a no-BatchNorm 51-conv chain is going to fail, it
# fails before the unigram floor, which every run so far crosses by 1.2K-6K.
cd /proj/devices/vla
go () { M=$1; E=$2; shift 2
  [ -f exp/done.$M ] && { echo "skip $M"; return; }
  echo "=== START $M $* $(date '+%H:%M')"
  ./exp/watch.sh $M $E > /dev/null 2>&1 & WP=$!
  ./exp/run.sh $M 10000 --norm none "$@"
  sleep 25; kill $WP 2>/dev/null
  cp -f checkpoint/$M.pt checkpoint/$M.final.pt 2>/dev/null
  conda run --no-capture-output -n dev python exp/score.py checkpoint/$M.final.pt \
      --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null \
      | grep -E "^$M" | tee -a PLAN.txt
  touch exp/done.$M; echo "=== END $M $(date '+%H:%M')"; }

# ORDERED MOST-NOVEL-FIRST (user, 2026-08-23).  AdamW and momentum were both
# rejected early in this study on evidence collected WITH BatchNorm, and the
# mechanism that condemned AdamW -- BN scale-invariance making weight directions
# loss-neutral, which AdamW's per-parameter normalization then promotes to
# full-size steps -- has no cause once BN is gone.  Those runs can overturn a
# closed dimension; the SGD points mostly confirm what is already known, so they
# go last and are the ones to sacrifice if time runs short.
# --clip_dff added after measuring the mechanism in the first E35 attempt:
# --norm none removes the only thing bounding the DFF state.  The FIRST token
# always writes every layer, and without BatchNorm the He-initialized 17-conv
# chain outputs order 1e5, so layer 3 latched dff_max = 4.46e5 on step 0.  It
# then writes only every 173 steps (ladder 1,13,173) and --ema 0.5 halves it per
# write, so shedding it needs ~18 writes = ~3100 steps of pure decay -- most of
# the pre-breakthrough window.  Measured ratio was exactly 0.50 per 173 steps.
# --clip_dff 100 stops that first write latching a value it cannot shed.
go e35_nobn_adamw   E35 --opt adamw --lr_max 0.001  --beta1 0.9 --beta2 0.999 --clip_dff 100
go e36_nobn_adamw3  E36 --opt adamw --lr_max 0.0003 --beta1 0.9 --beta2 0.999 --clip_dff 100
go e34_nobn_mom     E34 --opt sgd   --lr_max 0.01 --momentum 0.9 --nesterov --clip_dff 100
# E37/E38 inserted ahead of the SGD tail (user, 2026-08-23).  --init is listed as
# a CLOSED dimension in this file, but that was concluded WITH BatchNorm present,
# so it does not transfer (section 7b(e)).  It also targets E35's actual failure:
# dying ReLUs, dff_zeros 0.54 -> 0.93, grad -> 0.03.  With --init zero there is NO
# mechanism to revive a dead unit -- once a channel's pre-activation is negative
# everywhere, ReLU zeroes it and nothing perturbs it back.  BatchNorm was doing
# that job by re-centring every layer every step.  --init relu seeds the state
# with relu(randn) at EVERY document boundary (~890 tokens on web), injecting
# fresh entropy into exactly the units that have died -- the state analogue of
# weight init, and the only stochasticity left once BN's batch-statistic noise
# is gone.  E37 uses E35's lr, the run that learned before it died.
go e37_nobn_relu    E37 --opt adamw --lr_max 0.001 --beta1 0.9 --beta2 0.999 --clip_dff 100 --init relu
go e38_nobn_relusgd E38 --opt sgd   --lr_max 0.03 --clip_dff 100 --init relu
go e31_nobn_sgd03   E31 --opt sgd   --lr_max 0.03 --clip_dff 100
# E32/E33 (sgd 0.01, sgd 0.1) DROPPED: the two AdamW runs already bracketed the
# bind -- too much lr kills the ReLUs, too little does not learn -- and that is a
# normalizer problem no optimizer setting fixes.  Two more SGD points would only
# re-demonstrate it.
echo "NOBN GRID COMPLETE $(date)"
