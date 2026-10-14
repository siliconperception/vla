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
# Baseline = v395 (2026-10-14), after the vla.py rewrite: every option spelled out, including
# the smolfwedu eval suite that the old vla.py applied implicitly.
CMD=(python vla.py
  --dataset smolfwedu --shards 1 --tokenizer pythia31m
  --context 8 --n_hidden 512 --c_context 384 --kernel 3 --depth 8 --init zero --bn_momentum 0.1
  --ctx_ema 256,64,16,4,1 --ctx_read_norm 1 --dec_tree_kernels 3,3,3 --dec_width 256
  --batch 250 --momentum 0.0 --weight_decay 0.0
  --schedule coswarm --lr_min 0.0001 --lr_max 0.01 --lr_period 20000 --device cuda
  --monitor 100 --run_steps $((S+1)) --checkpoint 4000
  --gen_interval 4000 --gen_score
  --eval_interval 20000 --eval_corpora smolfwedu --eval_docs 100 --eval_bands 1024,8192
  --eval_info 100 --eval_reach 100
  --eval_gen 50 --eval_gen_prompt 128 --eval_gen_len 128 --eval_gen_judge Qwen/Qwen2.5-1.5B
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
