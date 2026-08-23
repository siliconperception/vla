#!/bin/bash
# usage: watch.sh <mnem> <expid>
# Calls report.sh once per NEW 5K checkpoint, so PLAN.txt gets a row even if the
# interactive session is busy elsewhere. Idempotent: tracks the last step reported.
M=$1; E=$2
cd /proj/devices/vla
LAST=$(grep -a "^$E  $M  step" PLAN.txt 2>/dev/null | tail -1 | awk '{print $4}')
LAST=${LAST:-(-1)}
while true; do
  CUR=$(grep -a '^TEXT step' log/exp.$M 2>/dev/null | tail -1 | awk '{print $3}')
  # skip step 0: vla.py saves at i % checkpoint == 0, which fires on the untrained
  # model before any training has happened.  Reporting it wastes a gencheck run and
  # puts a meaningless row in PLAN.txt.
  if [ -n "$CUR" ] && [ "$CUR" != "$LAST" ] && [ "$CUR" != "0" ]; then
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
