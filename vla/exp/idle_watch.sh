#!/bin/bash
# GPU idle watchdog.  Emits one line per idle episode; a Monitor turns those into
# notifications.  Catches ANY cause of a stall -- a driver that exited early, a
# crashed trainer, a chain whose predecessor never signalled -- not just the
# edit-a-running-script bug that motivated it.
cd /proj/devices/vla
IDLE=0
while true; do
  # NOT anchored on "^python NAME": real cmdlines carry flags ("python -u exp/reach.py")
  # and conda wrappers, and an anchored pattern silently matched NOTHING -- which is
  # how a running probe was reported as an idle GPU twice on 2026-08-24.
  if pgrep -f "(vla|exp/score|exp/reach|exp/gencheck|exp/memtest|exp/genstate)\.py" > /dev/null; then
    IDLE=0
  else
    IDLE=$((IDLE+1))
    # 5 consecutive minutes with no trainer, then every 15 min while it persists
    if [ $IDLE -eq 5 ] || { [ $IDLE -gt 5 ] && [ $(( (IDLE-5) % 15 )) -eq 0 ]; }; then
      echo "GPU IDLE ${IDLE}min -- no trainer or eval-probe running. last driver lines:"
      for f in $(ls -t log/*.log 2>/dev/null | head -4); do
        [ -f "$f" ] && echo "  $(basename $f): $(tail -1 $f | cut -c1-90)"
      done
    fi
  fi
  sleep 60
done
