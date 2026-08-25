#!/bin/bash
# usage: watch.sh <mnem> <expid> [report_every_steps]
# Calls report.sh once per NEW checkpoint, so PLAN.txt gets a row even if the
# interactive session is busy elsewhere. Idempotent: tracks the last step reported.
#
# report_every_steps (default 5000 = every checkpoint, the original behaviour) exists for
# LONG runs. A report is not free: it stashes a ~250MB copy of the weights, appends ~35
# lines to PLAN.txt, and runs gencheck plus three vla.py --generate subprocesses that each
# load the model and contend with the trainer for the GPU. At 4M steps a 5000-step cadence
# is 800 of those -- ~196GB of stashed checkpoints and ~28,000 lines appended to a PLAN.txt
# that is currently 5,200 lines long, which would destroy it as a readable document.
# The fine-grained curve does not come from here anyway: vla.py writes an EVAL line to the
# log every --eval_interval steps and a GEN sample every --gen_interval, both of which cost
# nothing extra. This controls only the heavyweight milestone reports.
M=$1; E=$2; EVERY=${3:-5000}
cd /proj/devices/vla
LAST=$(grep -a "^$E  $M  step" PLAN.txt 2>/dev/null | tail -1 | awk '{print $4}')
LAST=${LAST:-(-1)}
# ...but only if that row belongs to THIS run.  exp/run.sh truncates log/exp.$M at launch,
# so a PLAN row whose step is absent from the current log came from an EARLIER run with the
# same mnemonic -- and inheriting it makes this watcher skip that checkpoint silently.  That
# bit on 2026-08-24: p1_pile was rerun after a crash at 5000, the watcher started with
# LAST=5000 from the crashed run's row, skipped the rerun's 5000 checkpoint, and would have
# let checkpoint/p1_pile.pt be overwritten at 10000 with the 5000 weights never stashed.
# Keeping the PLAN-derived value when the step IS in the log preserves the original intent:
# a watcher restarted mid-run must not re-report what it already reported.
if [ "$LAST" != "(-1)" ] && ! grep -qa "^TEXT step  *$LAST " log/exp.$M 2>/dev/null; then
  echo "watch: PLAN row for step $LAST is not in this run's log -- previous run, ignoring"
  LAST=-1
fi
while true; do
  CUR=$(grep -a '^TEXT step' log/exp.$M 2>/dev/null | tail -1 | awk '{print $3}')
  # skip step 0: vla.py saves at i % checkpoint == 0, which fires on the untrained
  # model before any training has happened.  Reporting it wastes a gencheck run and
  # puts a meaningless row in PLAN.txt.
  if [ -n "$CUR" ] && [ "$CUR" != "$LAST" ] && [ "$CUR" != "0" ] \
     && [ $(( CUR % EVERY )) -eq 0 ]; then
    # stash a copy per 5K before reporting: checkpoint/<mnem>.pt is overwritten every
    # interval, so without this only the final weights survive and a collapse cannot be
    # traced back to the checkpoint before it.  sleep first -- torch.save is not atomic
    # and copying mid-write yields a corrupt file that loads without raising.
    sleep 20
    cp -f checkpoint/$M.pt checkpoint/$M.$CUR.pt 2>/dev/null
    ./exp/report.sh $M $E
    LAST=$CUR
  fi
  pgrep -f "python vla.py" >/dev/null || { sleep 30; pgrep -f "python vla.py" >/dev/null || break; }
  sleep 45
done
echo "WATCH DONE $M $(date)" >> log/exp.$M.out
