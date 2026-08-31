#!/bin/bash
# usage: longrun.sh <mnem> [total_steps] [max_restarts] [overrides for run.sh...]
#        total_steps defaults to 4,000,000 (1B tokens at batch 250), max_restarts to 20
#
# Supervises a run that is too long to babysit: relaunches it if the trainer dies, and
# stops when the GLOBAL step count reaches <total_steps>.
#
# Two things make this more than a `while true` loop:
#
# 1. --run_steps IS RELATIVE TO THE INVOCATION, not absolute.  vla.py breaks on
#    (i - _start_step) >= run_steps, so passing the same 4000000 to a resumed process would
#    run ANOTHER 4M steps from wherever it resumed.  Remaining steps are computed here.
# 2. PROGRESS IS THE CHECKPOINT'S step, NOT THE LOG'S.  A crash at step 7300 with the last
#    save at 5000 has really lost 2300 steps; trusting the log would skip them and the run
#    would finish 2300 steps short of the target while claiming otherwise.
#
# Resume is safe with respect to the log: exp/run.sh truncates log/exp.$M, but vla.py
# prepends the checkpoint's embedded log on --load, so the file is reconstructed whole and
# chart.py still sees one uninterrupted sequence.
#
# Resume DOES draw a fresh --seed (exp/run.sh no longer pins one), which means a fresh
# dataset shuffle and therefore fresh documents rather than a replay of what was already
# trained on.  For a corpus the size of the Pile that is the desired behaviour.
set -u
cd /proj/devices/vla
# 1B TOKENS = 4,000,000 steps at batch 250 is the STANDARD BUDGET for every experiment
# (2026-08-31).  Both numbers are still positional, but a missing or non-numeric argument now
# falls back to the standard rather than erroring, so `longrun.sh <mnem> -- <overrides>` and
# `longrun.sh <mnem> 4000000 20 <overrides>` mean the same thing.
M=$1; shift
TOTAL=4000000
case "${1:-}" in ''|*[!0-9]*) ;; *) TOTAL=$1; shift ;; esac
MAXR=20
case "${1:-}" in ''|*[!0-9]*) ;; *) MAXR=$1; shift ;; esac
[ "${1:-}" = "--" ] && shift

STATE=log/longrun.$M.state
echo "longrun: $M target $TOTAL steps, up to $MAXR restarts, $(date)" | tee -a $STATE

# Global step of a checkpoint, or 0.  Also serves as a load test: a checkpoint that cannot
# be read is one we must NOT resume from, and finding that out here (rather than after
# relaunching) is what lets us fall back to a milestone stash.
ckpt_step () {
  conda run --no-capture-output -n dev python - "$1" 2>/dev/null <<'PY'
import sys, torch
try:
    print(int(torch.load(sys.argv[1], map_location='cpu', weights_only=False).get('step', 0)))
except Exception:
    print(-1)
PY
}

for (( attempt=0; attempt<=MAXR; attempt++ )); do
  DONE=0
  if [ -f checkpoint/$M.pt ]; then
    DONE=$(ckpt_step checkpoint/$M.pt)
    if [ "$DONE" = "-1" ]; then
      # torch.save is not atomic; a crash mid-write leaves a file that loads as garbage or
      # not at all.  The milestone stashes exist precisely for this.
      NEWEST=$(ls -1t checkpoint/$M.[0-9]*.pt 2>/dev/null | head -1)
      echo "longrun: checkpoint/$M.pt is UNREADABLE -- falling back to ${NEWEST:-none}" | tee -a $STATE
      [ -n "$NEWEST" ] || { echo "longrun: no usable checkpoint, ABORTING" | tee -a $STATE; exit 1; }
      cp -f "$NEWEST" checkpoint/$M.pt
      DONE=$(ckpt_step checkpoint/$M.pt)
      [ "$DONE" = "-1" ] && { echo "longrun: stash unreadable too, ABORTING" | tee -a $STATE; exit 1; }
    fi
  fi

  REM=$(( TOTAL - DONE ))
  if [ $REM -le 0 ]; then
    echo "longrun: COMPLETE at step $DONE ($(date))" | tee -a $STATE
    exit 0
  fi

  EXTRA=""
  [ $DONE -gt 0 ] && EXTRA="--load checkpoint/$M.pt"
  echo "longrun: attempt $attempt -- at step $DONE, $REM to go $EXTRA ($(date))" | tee -a $STATE

  # via launch.sh, so each invocation executes a FROZEN SNAPSHOT of run.sh.  Over a run
  # measured in weeks the emitter will almost certainly be edited at some point, and bash
  # reads a script by byte offset -- editing the one it is mid-way through executing makes
  # it resume at a shifted position and run the wrong thing.  This is the same guard
  # launch.sh gives this script; run.sh needs it too since it is re-invoked on every resume.
  ./exp/launch.sh exp/run.sh $M $REM "$@" $EXTRA

  AFTER=$( [ -f checkpoint/$M.pt ] && ckpt_step checkpoint/$M.pt || echo 0 )
  echo "longrun: invocation ended at step $AFTER ($(date))" | tee -a $STATE
  if [ "$AFTER" != "-1" ] && [ "$AFTER" -ge "$TOTAL" ]; then
    echo "longrun: COMPLETE at step $AFTER ($(date))" | tee -a $STATE
    exit 0
  fi
  # A run that dies without advancing the checkpoint at all is failing on startup, not
  # mid-training; retrying it in a tight loop just burns the restart budget.
  if [ "$AFTER" = "$DONE" ]; then
    echo "longrun: no progress this attempt -- backing off 300s" | tee -a $STATE
    sleep 300
  fi
done
echo "longrun: EXHAUSTED $MAXR restarts, giving up ($(date))" | tee -a $STATE
exit 1
