#!/bin/bash
# usage: run.sh <mnemonic> [steps] <args overriding the baseline...>
#        steps defaults to 4,000,000 = 1B tokens at batch 250
# BASELINE = e30 config (3x17, bn_track ON).  7x7 was adopted at 12:45 and
# REVERTED at 14:20: with tracking on it has a +1.66 nat TRAIN/EVAL GAP and
# runs away in eval, while 3x17 has none.  Measured at 5K, same lr:
#   3x17 m=0.1   train 6.7144  held-out 6.6974  gap -0.017  runaway  0.0%
#   7x7  m=0.1   train 6.7889  held-out 8.4471  gap +1.658  runaway  2.2%
#   7x7  (e24)   train 6.6230  held-out    nan             runaway 100.0%
# The reach result that motivated 7x7 was measured on --no-bn_track models,
# where eval uses live batch stats and this failure is invisible.
# Anything in "$@" overrides it,
# since argparse takes the last occurrence of a flag.
#
# MONITORING (2026-08-24, Phase 2): --gen_interval 500 --eval_interval 5000.  These are
# observation cadence, NOT model configuration -- neither touches a weight, an optimizer
# state or the data stream, so runs before and after this line are directly comparable.
# Generation moved to 500 because the text has overturned the scalar reading more than once
# and a sample is cheap; held-out eval runs at the checkpoint cadence so every EVAL line in
# the log describes weights that exist on disk and can be re-derived with exp/score.py.
#
# SEED (2026-08-24): --seed 1 REMOVED, so each run draws its own from os.urandom.  This is
# not a loosening of control -- a fixed seed never bought reproducibility here.  --seed pins
# weight init (vla.py:885), the HF shuffle (vla.py:1897) and generation sampling, but NOT
# the data the model sees: 12 builder threads (vla.py:1964) race for the iterator lock
# (vla.py:1903), so batch composition is thread-scheduling dependent.  Two runs of the same
# config at the same seed differ by 0.02-0.035 held-out (excursions to 0.067) -- that spread
# is in PLAN.txt and it was measured, not assumed.  What --seed 1 actually did was make every
# experiment in the study share ONE draw from the init distribution; a random seed per run
# makes each an independent sample and lets the run-to-run sigma be estimated honestly.
# vla.py prints the drawn seed and stores it in saved_args, so it is always recoverable.
#
# To PAIR an experiment against an older run, pass --seed <that run's seed> explicitly.
# p1_pile (Phase 2's first run) is deliberately seed 1, pairing it with e25_3x17 on web.
# 1B tokens = 4,000,000 steps at batch 250 is the standard budget; a missing or non-numeric
# step count falls back to it rather than erroring.
M=$1; shift
S=4000000
case "${1:-}" in ''|*[!0-9]*) ;; *) S=$1; shift ;; esac
[ "${1:-}" = "--" ] && shift
cd /proj/devices/vla
mkdir -p checkpoint
rm -f log/exp.$M

# The baseline, as an ARRAY rather than a here-and-now command, so the exact argv that is
# about to run can also be written to ./doit.  Expansion order is unchanged: "$@" still comes
# last, so argparse still takes the caller's override of any flag.
CMD=(python vla.py
  --dataset web --preroll --tokenizer pythia31m
  --context 16 --n_hidden 256 --kernel 3
  --batch 250 --monitor 20
  --opt sgd --momentum 0.0 --weight_decay 0.0
  --schedule const --lr_max 0.03 --device cuda
  --n_layers 3 --depth 17 --clock fixed --clock_base 13.15
  --init zero --ema 0.5
  --run_steps $((S+1)) --checkpoint 5000
  --gen_interval 500 --eval_interval 5000
  --log log/exp.$M --save checkpoint/$M.pt
  "$@")

# ── ./doit gets the RESOLVED command line, newest first (2026-08-28, standing rule) ────────
# doit is the experiment history.  It used to be maintained by hand, which means it recorded
# what was INTENDED at the time someone remembered to edit it -- not what actually ran.  The
# baseline lives here in run.sh and the overrides arrive in "$@", so no single file previously
# held the command that a given log/exp.$M came from; reconstructing one meant reading ps
# output or the frozen snapshot under exp/.run/.  Writing argv here closes that gap: every
# invocation prepends the exact, re-runnable line, so the top of doit is always the newest
# experiment.  Resumes are prepended too and marked (resume) -- longrun re-invokes this script
# with --load and a recomputed --run_steps, and that IS a different running command line.
_shq () {                              # join argv into a line that can be pasted back
  local out="" a
  for a in "$@"; do
    case "$a" in
      *[!A-Za-z0-9_./:=,+-]*) a="'${a//\'/\'\\\'\'}'" ;;   # quote anything shell-significant
    esac
    out+="$a "
  done
  printf '%s' "${out% }"
}
_tag=""
case " $* " in *" --load "*) _tag="  (resume)" ;; esac
{
  printf '# %s  %s%s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$M" "$_tag"
  printf '%s\n\n' "$(_shq "${CMD[@]}")"
  [ -f doit ] && cat doit
} > doit.$$ && mv doit.$$ doit

conda run --no-capture-output -n dev "${CMD[@]}" > log/exp.$M.out 2>&1
RC=$?                                  # capture BEFORE $(date) below, which clobbers $?
echo "RUN_DONE $M rc=$RC $(date)" >> log/exp.$M.out
